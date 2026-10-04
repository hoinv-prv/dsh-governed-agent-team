import { randomUUID } from 'node:crypto'
import { homedir } from 'node:os'
import { mkdir, open, readFile, realpath, rename, lstat, unlink } from 'node:fs/promises'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import { LocalDurableAgentProvider } from './local-provider.js'
import type { DurableAgentDeclaration } from './service.js'
import { loadDurableMembersManifest, resolveLegacyDurableMember, type DurableMember, type DurableMembersManifest, type DurableMemberStorageScope, type MembersOptions } from './standalone-adapter.js'

const MANIFEST_VERSION = 1 as const
const MAX_PROFILE_BYTES = 256 * 1024
const MAX_MEMORY_INDEX_BYTES = 256 * 1024
const MAX_SOUL_BYTES = 256 * 1024
const MAX_MEMORY_ITEM_BYTES = 1024 * 1024
const DEFAULT_SOUL = `# SOUL.md

## Working principles

- Think before coding. State assumptions, surface ambiguity, and ask when requirements are unclear.
- Prefer the simplest solution that fully satisfies the task. Avoid speculative abstractions and features.
- Make surgical changes. Preserve existing style and do not refactor unrelated code.
- Work toward explicit, verifiable outcomes. Test the behavior you changed and report concrete evidence.
`
const MEMBER_NAME = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/u
const MEMORY_INDEX_KEYS = new Set(['version', 'items'])
const MEMORY_ITEM_KEYS = new Set(['id', 'title', 'when_to_use', 'file'])
const WRITE_MEMORY_ITEM_KEYS = new Set(['id', 'title', 'when_to_use', 'content'])
const MEMORY_INDEX_VERSION = 1 as const
const LEGACY_MEMORY_ID = 'legacy-memory'

export { loadDurableMembersManifest } from './standalone-adapter.js'
export type { DurableMember, DurableMembersManifest, DurableMemberStorageScope, MembersOptions } from './standalone-adapter.js'

export interface DurableMemberProfile extends DurableMember {
  readonly version: typeof MANIFEST_VERSION
  /** Present only for workspace-scoped members and bound to the canonical workspace directory. */
  readonly workspace_path?: string
}

export interface DurableMemoryIndexItem {
  readonly id: string
  readonly title: string
  /** Short retrieval hint loaded before a task so the agent can decide whether to open the item. */
  readonly when_to_use: string
  readonly file: string
}

export interface DurableMemoryIndex {
  readonly version: 1
  readonly items: readonly DurableMemoryIndexItem[]
}

export interface WriteDurableMemoryItemInput {
  readonly id: string
  readonly title: string
  readonly when_to_use: string
  readonly content: string
}

export interface DurableMemberTaskContext {
  readonly profile: DurableMemberProfile
  /** Persistent behavioral guidance. Inject immediately after host system commands. */
  readonly soul: string
  /** Bounded catalog loaded each task; open matching memory items separately. */
  readonly memoryIndex: DurableMemoryIndex
}

interface MemberPaths {
  readonly owner: string
  readonly storageIdentity: string
  readonly profile: string
  readonly soul: string
  readonly memoryDirectory: string
  readonly memoryIndex: string
  readonly legacyMemory: string
  readonly working: string
  readonly anchor: string
  readonly current: string
  readonly mutationLease: string
}
interface QueueRegistry { readonly tails: Map<string, Promise<void>> }

function fail(reason: string): never { throw new TypeError(`DURABLE_MEMBERS_${reason}`) }
function queueRegistry(): QueueRegistry {
  const key = Symbol.for('@deepseek-ai/dsh-durable-agent.memory-lock.v1')
  const root = globalThis as typeof globalThis & { [key: symbol]: QueueRegistry | undefined }
  return root[key] ??= { tails: new Map() }
}
async function withStorageQueue<T>(identity: string, operation: () => Promise<T>): Promise<T> {
  const registry = queueRegistry()
  const prior = registry.tails.get(identity) ?? Promise.resolve()
  let release!: () => void
  const gate = new Promise<void>(resolveGate => { release = resolveGate })
  const tail = prior.then(() => gate)
  registry.tails.set(identity, tail)
  await prior
  try { return await operation() } finally {
    release()
    if (registry.tails.get(identity) === tail) registry.tails.delete(identity)
  }
}
function record(value: unknown, reason: string): Record<string, unknown> {
  if (value === null || typeof value !== 'object' || Array.isArray(value) || Object.getPrototypeOf(value) !== Object.prototype) fail(reason)
  return value as Record<string, unknown>
}
function text(value: unknown, reason: string): string {
  if (typeof value !== 'string' || value.length === 0 || value.trim() !== value || value.includes('\0')) fail(reason)
  return value
}
function memberName(value: unknown): string {
  const name = text(value, 'INVALID_NAME')
  if (!MEMBER_NAME.test(name)) fail('INVALID_NAME')
  return name
}
function closed(value: Record<string, unknown>, keys: ReadonlySet<string>, reason: string): void {
  if (Object.keys(value).some((key) => !keys.has(key))) fail(reason)
}
async function canonicalDirectory(value: string, reason: string, requireAbsolute = false): Promise<string> {
  if (typeof value !== 'string' || value.length === 0 || value.includes('\0') || (requireAbsolute && !isAbsolute(value))) fail(reason)
  let canonical: string
  try { canonical = await realpath(resolve(value)) } catch { fail(reason) }
  const stat = await lstat(canonical)
  if (!stat.isDirectory()) fail(reason)
  return canonical
}
async function rejectSymlink(path: string, required = false): Promise<boolean> {
  try {
    const stat = await lstat(path)
    if (stat.isSymbolicLink()) fail('SYMLINK_NOT_ALLOWED')
    return true
  } catch (error) {
    if (error instanceof TypeError && error.message.startsWith('DURABLE_MEMBERS_')) throw error
    if (required) fail('MISSING_MEMBER_FILE')
    return false
  }
}
async function directory(path: string): Promise<void> {
  if (await rejectSymlink(path)) {
    const stat = await lstat(path)
    if (!stat.isDirectory()) fail('INVALID_MEMBER_PATH')
    return
  }
  await mkdir(path, { recursive: false, mode: 0o700 })
}
async function syncDirectory(path: string): Promise<void> {
  const handle = await open(path, 'r')
  try { await handle.sync() } finally { await handle.close() }
}
async function atomicWrite(path: string, content: string): Promise<void> {
  const temporary = join(dirname(path), `.${randomUUID()}.tmp`)
  let handle: Awaited<ReturnType<typeof open>> | undefined
  try {
    handle = await open(temporary, 'wx', 0o600)
    await handle.writeFile(content, 'utf8')
    await handle.sync()
    await handle.close()
    handle = undefined
    await rename(temporary, path)
    await syncDirectory(dirname(path))
  } catch (error) {
    if (handle) await handle.close().catch(() => undefined)
    await unlink(temporary).catch(() => undefined)
    throw error
  }
}
function profileFor(member: DurableMember, workspace: string): DurableMemberProfile {
  return Object.freeze({
    version: MANIFEST_VERSION,
    ...member,
    ...(member.storage_scope === 'workspace' ? { workspace_path: workspace } : {}),
  })
}
function legacyProfileFor(member: DurableMember): Record<string, unknown> {
  const { storage_scope: _scope, ...legacyMember } = member
  return { version: MANIFEST_VERSION, ...legacyMember }
}
function profileJson(profile: DurableMemberProfile): string {
  const source = `${JSON.stringify(profile, null, 2)}\n`
  if (Buffer.byteLength(source, 'utf8') > MAX_PROFILE_BYTES || source.includes('\0')) fail('PROFILE_CONFLICT')
  return source
}
async function ensureProfile(path: string, member: DurableMember, workspace: string): Promise<DurableMemberProfile> {
  const expected = profileFor(member, workspace)
  const expectedSource = profileJson(expected)
  if (await rejectSymlink(path)) {
    const stat = await lstat(path)
    if (!stat.isFile() || stat.size > MAX_PROFILE_BYTES) fail('PROFILE_CONFLICT')
    const source = await readFile(path, 'utf8')
    if (Buffer.byteLength(source, 'utf8') > MAX_PROFILE_BYTES || source.includes('\0')) fail('PROFILE_CONFLICT')
    let actual: unknown
    try { actual = JSON.parse(source) } catch { fail('PROFILE_CONFLICT') }
    if (JSON.stringify(actual) === JSON.stringify(expected)) return expected
    if (member.storage_scope === 'workspace' && JSON.stringify(actual) === JSON.stringify(legacyProfileFor(member))) {
      await atomicWrite(path, expectedSource)
      return expected
    }
    fail('PROFILE_CONFLICT')
  }
  await atomicWrite(path, expectedSource)
  return expected
}
function memoryItemId(value: unknown): string {
  const id = text(value, 'INVALID_MEMORY_ID')
  if (!MEMBER_NAME.test(id)) fail('INVALID_MEMORY_ID')
  return id
}
function memoryItemFile(id: string): string { return `${id}.md` }
function memoryIndexJson(index: DurableMemoryIndex): string {
  const source = `${JSON.stringify(index, null, 2)}\n`
  if (Buffer.byteLength(source, 'utf8') > MAX_MEMORY_INDEX_BYTES) fail('INVALID_MEMORY_INDEX')
  return source
}
function parseMemoryIndex(source: string): DurableMemoryIndex {
  let parsed: unknown
  try { parsed = JSON.parse(source) } catch { fail('INVALID_MEMORY_INDEX') }
  const input = record(parsed, 'INVALID_MEMORY_INDEX')
  closed(input, MEMORY_INDEX_KEYS, 'MEMORY_INDEX_UNKNOWN_KEY')
  if (input.version !== MEMORY_INDEX_VERSION || !Array.isArray(input.items) || input.items.length > 1024) fail('INVALID_MEMORY_INDEX')
  const seen = new Set<string>()
  const items = input.items.map((value): DurableMemoryIndexItem => {
    const item = record(value, 'INVALID_MEMORY_ITEM')
    closed(item, MEMORY_ITEM_KEYS, 'MEMORY_ITEM_UNKNOWN_KEY')
    const id = memoryItemId(item.id)
    if (seen.has(id)) fail('DUPLICATE_MEMORY_ITEM')
    seen.add(id)
    if (item.file !== memoryItemFile(id)) fail('INVALID_MEMORY_FILE')
    return Object.freeze({
      id,
      title: text(item.title, 'INVALID_MEMORY_TITLE'),
      when_to_use: text(item.when_to_use, 'INVALID_MEMORY_RETRIEVAL_HINT'),
      file: item.file,
    })
  })
  return Object.freeze({ version: MEMORY_INDEX_VERSION, items: Object.freeze(items) })
}
async function readMemoryIndex(path: string): Promise<DurableMemoryIndex> {
  await rejectSymlink(path, true)
  const stat = await lstat(path)
  if (!stat.isFile()) fail('INVALID_MEMBER_FILE')
  if (stat.size > MAX_MEMORY_INDEX_BYTES) fail('INVALID_MEMORY_INDEX')
  const source = await readFile(path, 'utf8')
  if (Buffer.byteLength(source, 'utf8') > MAX_MEMORY_INDEX_BYTES || source.includes('\0')) fail('INVALID_MEMORY_INDEX')
  return parseMemoryIndex(source)
}
async function readSoul(path: string): Promise<string> {
  await rejectSymlink(path, true)
  const stat = await lstat(path)
  if (!stat.isFile() || stat.size > MAX_SOUL_BYTES) fail('INVALID_SOUL')
  const source = await readFile(path, 'utf8')
  if (source.trim().length === 0 || Buffer.byteLength(source, 'utf8') > MAX_SOUL_BYTES || source.includes('\0')) fail('INVALID_SOUL')
  return source
}
async function ensureSoul(path: string): Promise<void> {
  if (await rejectSymlink(path)) await readSoul(path)
  else await atomicWrite(path, DEFAULT_SOUL)
}
async function readMemoryBody(path: string): Promise<string> {
  await rejectSymlink(path, true)
  const stat = await lstat(path)
  if (!stat.isFile() || stat.size > MAX_MEMORY_ITEM_BYTES) fail('INVALID_MEMORY')
  const content = await readFile(path, 'utf8')
  if (Buffer.byteLength(content, 'utf8') > MAX_MEMORY_ITEM_BYTES || content.includes('\0')) fail('INVALID_MEMORY')
  return content
}
async function ensureMemoryStorage(paths: MemberPaths): Promise<void> {
  await directory(paths.memoryDirectory)
  if (await rejectSymlink(paths.memoryIndex)) {
    await readMemoryIndex(paths.memoryIndex)
  } else {
    await atomicWrite(paths.memoryIndex, memoryIndexJson({ version: MEMORY_INDEX_VERSION, items: [] }))
  }

  if (!(await rejectSymlink(paths.legacyMemory))) return
  const content = await readMemoryBody(paths.legacyMemory)
  if (content.length > 0) {
    const index = await readMemoryIndex(paths.memoryIndex)
    const existing = index.items.find(item => item.id === LEGACY_MEMORY_ID)
    const itemPath = join(paths.memoryDirectory, memoryItemFile(LEGACY_MEMORY_ID))
    if (existing === undefined) {
      await atomicWrite(itemPath, content)
      await atomicWrite(paths.memoryIndex, memoryIndexJson({
        version: MEMORY_INDEX_VERSION,
        items: [...index.items, {
          id: LEGACY_MEMORY_ID,
          title: 'Legacy MEMORY.md',
          when_to_use: 'Use when historical memory from the previous single-file store may be relevant.',
          file: memoryItemFile(LEGACY_MEMORY_ID),
        }],
      }))
    } else {
      if (await readMemoryBody(itemPath) !== content) fail('LEGACY_MEMORY_CONFLICT')
    }
  }
}
async function pathsFor(workspace: string, member: DurableMember, options: MembersOptions): Promise<MemberPaths> {
  const owner = member.storage_scope === 'workspace'
    ? workspace
    : await canonicalDirectory(options.homeDirectory ?? homedir(), 'INVALID_HOME_DIRECTORY', true)
  const dsh = join(owner, '.dsh')
  const root = join(dsh, 'durable-agents')
  const memberRoot = join(root, member.name)
  const memoryDirectory = join(memberRoot, 'memory')
  await directory(dsh)
  await directory(root)
  await directory(memberRoot)
  return {
    owner,
    storageIdentity: `${owner}\0${member.storage_scope}\0${member.name}`,
    profile: join(memberRoot, 'profile.json'),
    soul: join(memberRoot, 'SOUL.md'),
    memoryDirectory,
    memoryIndex: join(memoryDirectory, 'index.json'),
    legacyMemory: join(memberRoot, 'MEMORY.md'),
    working: join(memberRoot, 'working'),
    anchor: join(memoryDirectory, 'generation-mode.json'),
    current: join(memoryDirectory, 'current.json'),
    mutationLease: join(memoryDirectory, 'mutation.lock'),
  }
}
async function authorizeMember(workspaceRoot: string, name: string, options: MembersOptions): Promise<{ workspace: string, member: DurableMember }> {
  // Storage receives a normalized, explicitly scoped declaration from the adapter;
  // it never opens a manifest or derives authority from a filename.
  const resolved = await resolveLegacyDurableMember(workspaceRoot, name, options)
  return { workspace: resolved.workspace, member: resolved.member }
}
async function ensureAuthorizedMemberBase(workspaceRoot: string, name: string, options: MembersOptions): Promise<{ workspace: string, member: DurableMember, profile: DurableMemberProfile, paths: MemberPaths }> {
  const { workspace, member } = await authorizeMember(workspaceRoot, name, options)
  const paths = await pathsFor(workspace, member, options)
  const profile = await ensureProfile(paths.profile, member, workspace)
  await ensureSoul(paths.soul)
  await directory(paths.memoryDirectory)
  await directory(paths.working)
  return { workspace, member, profile, paths }
}
function serviceDeclaration(member: DurableMember): DurableAgentDeclaration {
  return Object.freeze({
    name: member.name,
    description: member.description,
    prompt: member.prompt,
    context: member.context,
    provider: member.provider,
    model: member.model,
    ...(member.reasoning_effort === undefined ? {} : { reasoningEffort: member.reasoning_effort }),
    scope: member.storage_scope,
  })
}
async function compatibilityProvider(workspace: string, member: DurableMember, options: MembersOptions): Promise<{ service: LocalDurableAgentProvider, ref: Awaited<ReturnType<LocalDurableAgentProvider['provision']>> }> {
  const service = new LocalDurableAgentProvider(new Context(), { homeDirectory: options.homeDirectory ?? homedir(), providerName: 'local-compatibility' })
  const ref = await service.provision(workspace, serviceDeclaration(member))
  return { service, ref }
}
async function legacyMutation<T>(paths: MemberPaths, operation: () => Promise<T>): Promise<T> {
  return await withStorageQueue(paths.storageIdentity, async () => {
    try {
      const lease = await open(paths.mutationLease, 'wx', 0o600)
      await lease.close()
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'EEXIST') fail('CONCURRENT_MUTATION')
      throw error
    }
    try {
      if (await rejectSymlink(paths.anchor) || await rejectSymlink(paths.current)) fail('APPROVAL_REQUIRED')
      await ensureMemoryStorage(paths)
      if (await rejectSymlink(paths.anchor) || await rejectSymlink(paths.current)) fail('APPROVAL_REQUIRED')
      return await operation()
    } finally {
      await unlink(paths.mutationLease).catch(() => undefined)
    }
  })
}

/** Idempotently provisions one member after authorization by the current workspace manifest. */
export async function ensureDurableMember(workspaceRoot: string, name: string, options: MembersOptions = {}): Promise<DurableMemberProfile> {
  const { profile, paths } = await ensureAuthorizedMemberBase(workspaceRoot, name, options)
  if (!(await rejectSymlink(paths.anchor)) && !(await rejectSymlink(paths.current))) {
    try { await legacyMutation(paths, async () => undefined) }
    catch (error) { if (!(error instanceof TypeError) || error.message !== 'DURABLE_MEMBERS_APPROVAL_REQUIRED') throw error }
  }
  return profile
}

/** Lists and provisions all members authorized by the current workspace manifest. */
export async function listDurableMembers(workspaceRoot: string, options: MembersOptions = {}): Promise<readonly DurableMemberProfile[]> {
  const manifest = await loadDurableMembersManifest(workspaceRoot, options)
  const profiles: DurableMemberProfile[] = []
  for (const member of manifest.members) profiles.push(await ensureDurableMember(workspaceRoot, member.name, options))
  return Object.freeze(profiles)
}

/** Reads persistent behavioral guidance for injection immediately after host system commands. */
export async function readDurableMemberSoul(workspaceRoot: string, name: string, options: MembersOptions = {}): Promise<string> {
  const { paths } = await ensureAuthorizedMemberBase(workspaceRoot, name, options)
  return await readSoul(paths.soul)
}

/**
 * Loads the persistent context required for one task. The host must inject `soul`
 * immediately after its system commands, then use the memory index for selective retrieval.
 * Call this for every task so edits to SOUL.md and the memory index take effect.
 */
export async function loadDurableMemberTaskContext(workspaceRoot: string, name: string, options: MembersOptions = {}): Promise<DurableMemberTaskContext> {
  const { workspace, member, profile } = await ensureAuthorizedMemberBase(workspaceRoot, name, options)
  const provider = await compatibilityProvider(workspace, member, options)
  try {
    const snapshot = await provider.service.openTaskContext(provider.ref)
    return Object.freeze({
      profile,
      soul: snapshot.guidance,
      memoryIndex: Object.freeze({ version: 1 as const, items: Object.freeze(snapshot.memoryCatalog.map(item => Object.freeze({ id: item.id, title: item.title, when_to_use: item.retrievalCondition, file: memoryItemFile(item.id) }))) }),
    })
  } finally { await provider.service.release(provider.ref).catch(() => undefined) }
}

/** Loads the bounded memory catalog intended to be added to the agent context before each task. */
export async function readDurableMemberMemoryIndex(workspaceRoot: string, name: string, options: MembersOptions = {}): Promise<DurableMemoryIndex> {
  const { workspace, member } = await ensureAuthorizedMemberBase(workspaceRoot, name, options)
  const provider = await compatibilityProvider(workspace, member, options)
  try {
    const snapshot = await provider.service.openTaskContext(provider.ref)
    return Object.freeze({ version: 1, items: Object.freeze(snapshot.memoryCatalog.map(item => Object.freeze({ id: item.id, title: item.title, when_to_use: item.retrievalCondition, file: memoryItemFile(item.id) }))) })
  } finally { await provider.service.release(provider.ref).catch(() => undefined) }
}

/** Opens one memory item selected from the task-time index. */
export async function readDurableMemberMemoryItem(workspaceRoot: string, name: string, id: string, options: MembersOptions = {}): Promise<string> {
  const normalizedId = memoryItemId(id)
  const { workspace, member } = await ensureAuthorizedMemberBase(workspaceRoot, name, options)
  const provider = await compatibilityProvider(workspace, member, options)
  try { return (await provider.service.readMemoryItem(provider.ref, normalizedId)).content }
  catch (error) {
    if (error instanceof Error && 'code' in error && error.code === 'UNKNOWN_MEMORY_ITEM') fail('UNKNOWN_MEMORY_ITEM')
    throw error
  } finally { await provider.service.release(provider.ref).catch(() => undefined) }
}

/** Creates or replaces one memory item and atomically publishes its retrieval metadata in the index. */
export async function writeDurableMemberMemoryItem(workspaceRoot: string, name: string, input: WriteDurableMemoryItemInput, options: MembersOptions = {}): Promise<void> {
  const candidate = record(input, 'INVALID_MEMORY_ITEM')
  closed(candidate, WRITE_MEMORY_ITEM_KEYS, 'MEMORY_ITEM_UNKNOWN_KEY')
  const id = memoryItemId(candidate.id)
  const title = text(candidate.title, 'INVALID_MEMORY_TITLE')
  const whenToUse = text(candidate.when_to_use, 'INVALID_MEMORY_RETRIEVAL_HINT')
  if (typeof candidate.content !== 'string' || candidate.content.includes('\0') || Buffer.byteLength(candidate.content, 'utf8') > MAX_MEMORY_ITEM_BYTES) fail('INVALID_MEMORY')
  const content = candidate.content
  const { paths } = await ensureAuthorizedMemberBase(workspaceRoot, name, options)
  await legacyMutation(paths, async () => {
    const index = await readMemoryIndex(paths.memoryIndex)
    const file = memoryItemFile(id)
    const path = join(paths.memoryDirectory, file)
    if (await rejectSymlink(path)) {
      const stat = await lstat(path)
      if (!stat.isFile()) fail('INVALID_MEMORY_FILE')
    }
    await atomicWrite(path, content)
    const nextItem: DurableMemoryIndexItem = { id, title, when_to_use: whenToUse, file }
    const itemIndex = index.items.findIndex(item => item.id === id)
    const items = [...index.items]
    if (itemIndex === -1) items.push(nextItem)
    else items[itemIndex] = nextItem
    await atomicWrite(paths.memoryIndex, memoryIndexJson({ version: MEMORY_INDEX_VERSION, items }))
  })
}

/** @deprecated Compatibility adapter for the former single MEMORY.md API. */
export async function readDurableMemberMemory(workspaceRoot: string, name: string, options: MembersOptions = {}): Promise<string> {
  const index = await readDurableMemberMemoryIndex(workspaceRoot, name, options)
  if (!index.items.some(item => item.id === LEGACY_MEMORY_ID)) return ''
  return await readDurableMemberMemoryItem(workspaceRoot, name, LEGACY_MEMORY_ID, options)
}

/** @deprecated Writes the compatibility legacy-memory item; new callers should write named items. */
export async function writeDurableMemberMemory(workspaceRoot: string, name: string, content: string, options: MembersOptions = {}): Promise<void> {
  await writeDurableMemberMemoryItem(workspaceRoot, name, {
    id: LEGACY_MEMORY_ID,
    title: 'Legacy memory',
    when_to_use: 'Use when general memory written through the legacy compatibility API may be relevant.',
    content,
  }, options)
}
