import { createHash, randomUUID } from 'node:crypto'
import { lstat, mkdir, open, readFile, readdir, realpath, rename, rm, unlink } from 'node:fs/promises'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import type { Context } from '@deepseek-ai/cordis'
import { DurableAgentError } from './errors.js'
import {
  DurableAgentService,
  type DurableAgentApprovedMemoryInput,
  type DurableAgentCommittedMemoryItem,
  type DurableAgentDeclaration,
  type DurableAgentMemoryCandidate,
  type DurableAgentMemoryCandidateInput,
  type DurableAgentMemoryCatalogItem,
  type DurableAgentMemoryItem,
  type DurableAgentRef,
  type DurableAgentStorageScope,
  type DurableAgentTaskContext,
  type DurableAgentWorkingLocation,
} from './service.js'

const PROFILE_VERSION = 1 as const
const STORE_VERSION = 1 as const
const MAX_PROFILE_BYTES = 256 * 1024
const MAX_GUIDANCE_BYTES = 256 * 1024
const MAX_MANIFEST_BYTES = 256 * 1024
const MAX_POINTER_BYTES = 8 * 1024
const MAX_MEMORY_ITEM_BYTES = 1024 * 1024
const MAX_CANDIDATE_BYTES = 2 * 1024 * 1024
const MAX_METADATA_BYTES = 16 * 1024
const MAX_PROVENANCE_BYTES = 64 * 1024
const MAX_AUTHORIZATION_BYTES = 16 * 1024
const MAX_LIMITATIONS = 64
const MAX_MEMORY_ITEMS = 1024
const MAX_GENERATION_CHAIN_LENGTH = 4096
const MAX_RELEASED_REFERENCE_TOMBSTONES = 64
const MEMBER_NAME = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/u
const REFERENCE_PART = /^[a-zA-Z0-9-]+$/u
const PROVIDER_NAME = /^[A-Za-z][A-Za-z0-9._-]*$/u
const DECLARATION_KEYS = new Set(['name', 'description', 'prompt', 'context', 'provider', 'model', 'reasoningEffort', 'scope'])
const LEGACY_INDEX_KEYS = new Set(['version', 'items'])
const LEGACY_ITEM_KEYS = new Set(['id', 'title', 'when_to_use', 'file'])
const CANDIDATE_KEYS = new Set(['title', 'retrievalCondition', 'content', 'provenance', 'confidence', 'limitations'])
const APPROVED_KEYS = new Set(['candidateId', 'item', 'authorization'])
const APPROVED_ITEM_KEYS = new Set(['id', 'title', 'retrievalCondition', 'content'])
const AUTHORIZATION_KEYS = new Set(['kind', 'authorizationRef'])
const DEFAULT_GUIDANCE = `# SOUL.md

## Working principles

- Think before coding. State assumptions, surface ambiguity, and ask when requirements are unclear.
- Prefer the simplest solution that fully satisfies the task. Avoid speculative abstractions and features.
- Make surgical changes. Preserve existing style and do not refactor unrelated code.
- Work toward explicit, verifiable outcomes. Test the behavior you changed and report concrete evidence.
`

interface LocalProfile {
  readonly version: typeof PROFILE_VERSION
  readonly name: string
  readonly description: string
  readonly prompt: string
  readonly context: 'fresh' | 'fork'
  readonly provider: string
  readonly model: string
  readonly reasoning_effort?: string
  readonly storage_scope: DurableAgentStorageScope
  readonly workspace_path?: string
}
interface PrivatePaths {
  readonly memberRoot: string
  readonly profile: string
  readonly guidance: string
  readonly memoryDirectory: string
  readonly memoryIndex: string
  readonly legacyMemory: string
  readonly working: string
  readonly anchor: string
  readonly current: string
  readonly mutationLease: string
  readonly objects: string
  readonly generations: string
  readonly staging: string
  readonly candidates: string
}
interface ManifestItem extends DurableAgentMemoryCatalogItem {
  readonly object: string
  readonly bytes: number
}
interface GenerationManifest {
  readonly version: typeof STORE_VERSION
  readonly generation: string
  readonly parent: string | null
  readonly parent_manifest: string | null
  readonly sequence: number
  readonly commit_key: string
  readonly items: readonly Readonly<ManifestItem>[]
}
interface BootstrapAnchor {
  readonly version: typeof STORE_VERSION
  readonly storage_identity: string
  readonly generation: string
  readonly manifest: string
}
interface CurrentPointer {
  readonly version: typeof STORE_VERSION
  readonly generation: string
  readonly sequence: number
  readonly manifest: string
}
interface StoredCandidate {
  readonly version: typeof STORE_VERSION
  readonly candidate_id: string
  readonly status: 'unconfirmed'
  readonly title: string
  readonly retrieval_condition: string
  readonly content: string
  readonly provenance: string
  readonly confidence: 'low' | 'medium' | 'high'
  readonly limitations: readonly string[]
}
interface AuthorityState {
  readonly anchor: BootstrapAnchor
  readonly pointer: CurrentPointer
  readonly manifest: GenerationManifest
}
interface ContentRevision { readonly digest: string; readonly revision: number }
interface ReleasedReferenceTombstone { readonly generation: string; readonly scope: DurableAgentStorageScope }
interface Entry {
  readonly token: string
  readonly ref: DurableAgentRef
  readonly generation: string
  readonly declaration: Readonly<DurableAgentDeclaration>
  readonly profile: LocalProfile
  readonly paths: PrivatePaths
  readonly identityKey: string
  readonly storageIdentity: string
  status: 'active' | 'closing'
  activeOperations: number
  drainWaiters: (() => void)[]
  nextRevision: number
  snapshotRevision?: ContentRevision
  readonly itemRevisions: Map<string, ContentRevision>
}
interface QueueRegistry { readonly tails: Map<string, Promise<void>> }

export interface LocalDurableAgentProviderOptions {
  readonly homeDirectory?: string
  readonly providerName?: string
}

function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value) && Object.getPrototypeOf(value) === Object.prototype
}
function closed(value: Record<string, unknown>, keys: ReadonlySet<string>): boolean { return Object.keys(value).every(key => keys.has(key)) }
function utf8Bytes(value: string): number { return Buffer.byteLength(value, 'utf8') }
function validText(value: unknown, maximum = Number.MAX_SAFE_INTEGER): value is string {
  return typeof value === 'string' && value.length > 0 && value.trim() === value && !value.includes('\0') && utf8Bytes(value) <= maximum
}
function publicFailure(error: unknown): never {
  if (error instanceof DurableAgentError) throw error
  throw new DurableAgentError('PROVIDER_UNAVAILABLE')
}
function invalidDeclaration(memberName?: string): never { throw new DurableAgentError('INVALID_DECLARATION', memberName ? { memberName } : {}) }
function invalidContext(memberName?: string): never { throw new DurableAgentError('INVALID_CONTEXT_DATA', memberName ? { memberName } : {}) }
function rejected(memberName?: string): never { throw new DurableAgentError('REJECTED_CANDIDATE', memberName ? { memberName } : {}) }
function hash(value: string | Uint8Array): string { return createHash('sha256').update(value).digest('hex') }
function jsonSource(value: unknown): string { return `${JSON.stringify(value, null, 2)}\n` }
function sameJson(left: unknown, right: unknown): boolean { return JSON.stringify(left) === JSON.stringify(right) }
function strictDecode(bytes: Uint8Array, memberName: string): string {
  let value: string
  try { value = new TextDecoder('utf-8', { fatal: true }).decode(bytes) } catch { invalidContext(memberName) }
  if (value.includes('\0')) invalidContext(memberName)
  return value
}

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

async function exists(path: string, memberName: string): Promise<boolean> {
  try {
    const stat = await lstat(path)
    if (stat.isSymbolicLink()) invalidContext(memberName)
    return true
  } catch (error) {
    if (error instanceof DurableAgentError) throw error
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return false
    throw error
  }
}
async function ensureDirectory(path: string, memberName: string): Promise<void> {
  if (await exists(path, memberName)) {
    if (!(await lstat(path)).isDirectory()) invalidContext(memberName)
    return
  }
  await mkdir(path, { recursive: false, mode: 0o700 })
}
async function syncDirectory(path: string): Promise<void> {
  const handle = await open(path, 'r')
  try { await handle.sync() } finally { await handle.close() }
}
async function writeSynced(path: string, content: string): Promise<void> {
  const handle = await open(path, 'wx', 0o600)
  try { await handle.writeFile(content, 'utf8'); await handle.sync() } finally { await handle.close() }
}
async function atomicWrite(path: string, content: string): Promise<void> {
  const temporary = join(dirname(path), `.${randomUUID()}.tmp`)
  try {
    await writeSynced(temporary, content)
    await rename(temporary, path)
    await syncDirectory(dirname(path))
  } catch (error) {
    await unlink(temporary).catch(() => undefined)
    throw error
  }
}
async function boundedText(path: string, maximum: number, memberName: string, required = true): Promise<string | undefined> {
  if (!(await exists(path, memberName))) {
    if (required) invalidContext(memberName)
    return undefined
  }
  const stat = await lstat(path)
  if (!stat.isFile() || stat.size > maximum) invalidContext(memberName)
  const bytes = await readFile(path)
  if (bytes.byteLength > maximum) invalidContext(memberName)
  return strictDecode(bytes, memberName)
}
async function withMutation<T>(paths: PrivatePaths, identity: string, memberName: string, operation: () => Promise<T>): Promise<T> {
  return await withStorageQueue(identity, async () => {
    try {
      const lease = await open(paths.mutationLease, 'wx', 0o600)
      await lease.close()
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'EEXIST') throw new DurableAgentError('CONCURRENT_MUTATION', { memberName })
      throw error
    }
    try { return await operation() } finally {
      await unlink(paths.mutationLease).catch(() => undefined)
    }
  })
}

function validateDeclarationShape(value: unknown): asserts value is DurableAgentDeclaration {
  if (!record(value) || !closed(value, DECLARATION_KEYS)) invalidDeclaration()
  if (!validText(value.name) || !MEMBER_NAME.test(value.name)) invalidDeclaration()
  if (!validText(value.description) || !validText(value.prompt) || !validText(value.provider) || !validText(value.model)) invalidDeclaration(value.name)
  if (value.context !== 'fresh' && value.context !== 'fork') invalidDeclaration(value.name)
  if (value.scope !== 'workspace' && value.scope !== 'global') throw new DurableAgentError('UNSUPPORTED_SCOPE', { memberName: value.name })
  if (value.reasoningEffort !== undefined && !validText(value.reasoningEffort)) invalidDeclaration(value.name)
}
async function canonicalDirectory(value: string, code: 'INVALID_DECLARATION' | 'PROVIDER_UNAVAILABLE', requireAbsolute = false): Promise<string> {
  if (!validText(value) || (requireAbsolute && !isAbsolute(value))) throw new DurableAgentError(code)
  try {
    const canonical = await realpath(resolve(value))
    if (!(await lstat(canonical)).isDirectory()) throw new DurableAgentError(code)
    return canonical
  } catch (error) {
    if (error instanceof DurableAgentError) throw error
    throw new DurableAgentError(code)
  }
}
function freezeDeclaration(value: DurableAgentDeclaration): Readonly<DurableAgentDeclaration> {
  return Object.freeze({ name: value.name, description: value.description, prompt: value.prompt, context: value.context, provider: value.provider, model: value.model, ...(value.reasoningEffort === undefined ? {} : { reasoningEffort: value.reasoningEffort }), scope: value.scope })
}
function profileFor(declaration: DurableAgentDeclaration, workspace: string): LocalProfile {
  return Object.freeze({ version: PROFILE_VERSION, name: declaration.name, description: declaration.description, prompt: declaration.prompt, context: declaration.context, provider: declaration.provider, model: declaration.model, ...(declaration.reasoningEffort === undefined ? {} : { reasoning_effort: declaration.reasoningEffort }), storage_scope: declaration.scope, ...(declaration.scope === 'workspace' ? { workspace_path: workspace } : {}) })
}
function profileSource(profile: LocalProfile): string {
  const source = jsonSource(profile)
  if (utf8Bytes(source) > MAX_PROFILE_BYTES || source.includes('\0')) invalidDeclaration(profile.name)
  return source
}
function legacyProfileFor(profile: LocalProfile): Record<string, unknown> { const { storage_scope: _scope, workspace_path: _workspace, ...legacy } = profile; return legacy }
async function ensureProfile(path: string, expected: LocalProfile): Promise<void> {
  const expectedSource = profileSource(expected)
  const existing = await boundedText(path, MAX_PROFILE_BYTES, expected.name, false)
  if (existing === undefined) { await atomicWrite(path, expectedSource); return }
  let actual: unknown
  try { actual = JSON.parse(existing) } catch { throw new DurableAgentError('PROFILE_CONFLICT', { memberName: expected.name }) }
  if (sameJson(actual, expected)) return
  if (expected.storage_scope === 'workspace' && sameJson(actual, legacyProfileFor(expected))) { await atomicWrite(path, expectedSource); return }
  throw new DurableAgentError('PROFILE_CONFLICT', { memberName: expected.name })
}
async function verifyProfile(path: string, expected: LocalProfile): Promise<void> {
  const source = await boundedText(path, MAX_PROFILE_BYTES, expected.name)
  let actual: unknown
  try { actual = JSON.parse(source!) } catch { throw new DurableAgentError('PROFILE_CONFLICT', { memberName: expected.name }) }
  if (record(actual) && actual.storage_scope !== undefined && actual.storage_scope !== expected.storage_scope) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { memberName: expected.name, referenceState: 'scope-mismatch' })
  if (!sameJson(actual, expected)) throw new DurableAgentError('PROFILE_CONFLICT', { memberName: expected.name })
}
function memoryId(value: unknown, memberName: string, unknown = false): string {
  if (!validText(value, MAX_METADATA_BYTES) || !MEMBER_NAME.test(value)) {
    if (unknown) throw new DurableAgentError('UNKNOWN_MEMORY_ITEM', { memberName })
    invalidContext(memberName)
  }
  return value
}

function pathsFor(owner: string, name: string): PrivatePaths {
  const memberRoot = join(owner, '.dsh', 'durable-agents', name)
  const memoryDirectory = join(memberRoot, 'memory')
  return {
    memberRoot,
    profile: join(memberRoot, 'profile.json'), guidance: join(memberRoot, 'SOUL.md'), memoryDirectory,
    memoryIndex: join(memoryDirectory, 'index.json'), legacyMemory: join(memberRoot, 'MEMORY.md'), working: join(memberRoot, 'working'),
    anchor: join(memoryDirectory, 'generation-mode.json'), current: join(memoryDirectory, 'current.json'), mutationLease: join(memoryDirectory, 'mutation.lock'),
    objects: join(memoryDirectory, 'objects'), generations: join(memoryDirectory, 'generations'), staging: join(memoryDirectory, 'staging'), candidates: join(memoryDirectory, 'candidates'),
  }
}
async function ensureBaseStorage(owner: string, profile: LocalProfile): Promise<PrivatePaths> {
  const dsh = join(owner, '.dsh'), root = join(dsh, 'durable-agents')
  const paths = pathsFor(owner, profile.name)
  for (const path of [dsh, root, paths.memberRoot, paths.memoryDirectory]) await ensureDirectory(path, profile.name)
  await ensureProfile(paths.profile, profile)
  const guidance = await boundedText(paths.guidance, MAX_GUIDANCE_BYTES, profile.name, false)
  if (guidance === undefined) await atomicWrite(paths.guidance, DEFAULT_GUIDANCE)
  else if (guidance.trim().length === 0) invalidContext(profile.name)
  await ensureDirectory(paths.working, profile.name)
  for (const path of [paths.objects, paths.generations, paths.staging, paths.candidates]) await ensureDirectory(path, profile.name)
  return paths
}

interface LegacyItem { readonly id: string; readonly title: string; readonly retrievalCondition: string; readonly content: string }
function parseLegacyIndex(source: string, memberName: string): readonly { id: string; title: string; retrievalCondition: string; file: string }[] {
  let value: unknown
  try { value = JSON.parse(source) } catch { invalidContext(memberName) }
  if (!record(value) || !closed(value, LEGACY_INDEX_KEYS) || value.version !== 1 || !Array.isArray(value.items) || value.items.length > MAX_MEMORY_ITEMS) invalidContext(memberName)
  const seen = new Set<string>()
  return value.items.map(raw => {
    if (!record(raw) || !closed(raw, LEGACY_ITEM_KEYS)) invalidContext(memberName)
    const id = memoryId(raw.id, memberName)
    if (seen.has(id) || !validText(raw.title, MAX_METADATA_BYTES) || !validText(raw.when_to_use, MAX_METADATA_BYTES) || raw.file !== `${id}.md`) invalidContext(memberName)
    seen.add(id)
    return { id, title: raw.title, retrievalCondition: raw.when_to_use, file: raw.file }
  })
}
async function legacyItems(paths: PrivatePaths, memberName: string): Promise<readonly LegacyItem[]> {
  let index = await boundedText(paths.memoryIndex, MAX_MANIFEST_BYTES, memberName, false)
  if (index === undefined) {
    index = jsonSource({ version: 1, items: [] })
    await atomicWrite(paths.memoryIndex, index)
  }
  const metadata = parseLegacyIndex(index, memberName)
  const items: LegacyItem[] = []
  for (const item of metadata) items.push({ ...item, content: (await boundedText(join(paths.memoryDirectory, item.file), MAX_MEMORY_ITEM_BYTES, memberName))! })
  const legacy = await boundedText(paths.legacyMemory, MAX_MEMORY_ITEM_BYTES, memberName, false)
  if (legacy !== undefined && legacy.length > 0) {
    const found = items.find(item => item.id === 'legacy-memory')
    if (found && found.content !== legacy) invalidContext(memberName)
    if (!found) items.push({ id: 'legacy-memory', title: 'Legacy MEMORY.md', retrievalCondition: 'Use when historical memory from the previous single-file store may be relevant.', content: legacy })
  }
  return items
}

function manifestSource(value: GenerationManifest, memberName: string): string {
  const source = jsonSource(value)
  if (utf8Bytes(source) > MAX_MANIFEST_BYTES) invalidContext(memberName)
  return source
}
function pointerSource(value: BootstrapAnchor | CurrentPointer, memberName: string): string {
  const source = jsonSource(value)
  if (utf8Bytes(source) > MAX_POINTER_BYTES) invalidContext(memberName)
  return source
}
function parseAnchor(source: string, identityDigest: string, memberName: string): BootstrapAnchor {
  let raw: unknown
  try { raw = JSON.parse(source) } catch { invalidContext(memberName) }
  if (!record(raw) || Object.keys(raw).sort().join(',') !== 'generation,manifest,storage_identity,version' || raw.version !== 1 || raw.storage_identity !== identityDigest || !validText(raw.generation) || !REFERENCE_PART.test(raw.generation) || typeof raw.manifest !== 'string' || !/^[a-f0-9]{64}$/u.test(raw.manifest)) invalidContext(memberName)
  return raw as unknown as BootstrapAnchor
}
function parsePointer(source: string, memberName: string): CurrentPointer {
  let raw: unknown
  try { raw = JSON.parse(source) } catch { invalidContext(memberName) }
  if (!record(raw) || Object.keys(raw).sort().join(',') !== 'generation,manifest,sequence,version' || raw.version !== 1 || !validText(raw.generation) || !REFERENCE_PART.test(raw.generation) || !Number.isSafeInteger(raw.sequence) || (raw.sequence as number) < 0 || typeof raw.manifest !== 'string' || !/^[a-f0-9]{64}$/u.test(raw.manifest)) invalidContext(memberName)
  return raw as unknown as CurrentPointer
}
function parseManifest(source: string, memberName: string): GenerationManifest {
  let raw: unknown
  try { raw = JSON.parse(source) } catch { invalidContext(memberName) }
  if (!record(raw) || Object.keys(raw).sort().join(',') !== 'commit_key,generation,items,parent,parent_manifest,sequence,version' || raw.version !== 1 || !validText(raw.generation) || !REFERENCE_PART.test(raw.generation) || !(raw.parent === null || (validText(raw.parent) && REFERENCE_PART.test(raw.parent))) || !(raw.parent_manifest === null || (typeof raw.parent_manifest === 'string' && /^[a-f0-9]{64}$/u.test(raw.parent_manifest))) || (raw.parent === null) !== (raw.parent_manifest === null) || !Number.isSafeInteger(raw.sequence) || (raw.sequence as number) < 0 || typeof raw.commit_key !== 'string' || !/^[a-f0-9]{64}$/u.test(raw.commit_key) || !Array.isArray(raw.items) || raw.items.length > MAX_MEMORY_ITEMS) invalidContext(memberName)
  const seen = new Set<string>()
  const items = raw.items.map(value => {
    if (!record(value) || Object.keys(value).sort().join(',') !== 'bytes,id,object,retrievalCondition,title') invalidContext(memberName)
    const id = memoryId(value.id, memberName)
    if (seen.has(id) || !validText(value.title, MAX_METADATA_BYTES) || !validText(value.retrievalCondition, MAX_METADATA_BYTES) || typeof value.object !== 'string' || !/^[a-f0-9]{64}$/u.test(value.object) || !Number.isSafeInteger(value.bytes) || (value.bytes as number) < 0 || (value.bytes as number) > MAX_MEMORY_ITEM_BYTES) invalidContext(memberName)
    seen.add(id)
    return Object.freeze({ id, title: value.title, retrievalCondition: value.retrievalCondition, object: value.object, bytes: value.bytes as number })
  })
  return Object.freeze({ version: 1, generation: raw.generation, parent: raw.parent as string | null, parent_manifest: raw.parent_manifest as string | null, sequence: raw.sequence as number, commit_key: raw.commit_key, items: Object.freeze(items) })
}
async function readManifest(paths: PrivatePaths, generation: string, expectedDigest: string, memberName: string): Promise<GenerationManifest> {
  const source = (await boundedText(join(paths.generations, `${generation}.json`), MAX_MANIFEST_BYTES, memberName))!
  if (hash(source) !== expectedDigest) invalidContext(memberName)
  const manifest = parseManifest(source, memberName)
  if (manifest.generation !== generation) invalidContext(memberName)
  for (const item of manifest.items) {
    const path = join(paths.objects, `${item.object}.md`)
    if (!(await exists(path, memberName))) invalidContext(memberName)
    const stat = await lstat(path)
    if (!stat.isFile() || stat.size !== item.bytes) invalidContext(memberName)
  }
  return manifest
}
async function readObject(paths: PrivatePaths, item: ManifestItem, memberName: string): Promise<string> {
  const content = (await boundedText(join(paths.objects, `${item.object}.md`), MAX_MEMORY_ITEM_BYTES, memberName))!
  if (utf8Bytes(content) !== item.bytes || hash(content) !== item.object) invalidContext(memberName)
  return content
}
async function publishObject(paths: PrivatePaths, transaction: string, content: string, memberName: string): Promise<{ digest: string; bytes: number }> {
  const objectDigest = hash(content), bytes = utf8Bytes(content), target = join(paths.objects, `${objectDigest}.md`)
  if (await exists(target, memberName)) {
    const existing = (await boundedText(target, MAX_MEMORY_ITEM_BYTES, memberName))!
    if (hash(existing) !== objectDigest || utf8Bytes(existing) !== bytes) invalidContext(memberName)
    return { digest: objectDigest, bytes }
  }
  const temporary = join(transaction, `object-${objectDigest}.tmp`)
  await writeSynced(temporary, content)
  await rename(temporary, target)
  await syncDirectory(paths.objects)
  return { digest: objectDigest, bytes }
}
async function publishManifest(paths: PrivatePaths, transaction: string, manifest: GenerationManifest, memberName: string): Promise<string> {
  const source = manifestSource(manifest, memberName), digest = hash(source)
  const temporary = join(transaction, `manifest-${manifest.generation}.tmp`)
  await writeSynced(temporary, source)
  await rename(temporary, join(paths.generations, `${manifest.generation}.json`))
  await syncDirectory(paths.generations)
  return digest
}
async function publishPointer(paths: PrivatePaths, transaction: string, pointer: CurrentPointer, memberName: string): Promise<void> {
  const temporary = join(transaction, 'current.tmp')
  await writeSynced(temporary, pointerSource(pointer, memberName))
  await rename(temporary, paths.current)
  await syncDirectory(paths.memoryDirectory)
}
async function generationFiles(paths: PrivatePaths): Promise<string[]> { return (await readdir(paths.generations)).filter(name => /^[a-zA-Z0-9-]+\.json$/u.test(name)) }

async function readAuthority(paths: PrivatePaths, storageIdentity: string, memberName: string): Promise<AuthorityState> {
  const identityDigest = hash(storageIdentity)
  const anchorSource = await boundedText(paths.anchor, MAX_POINTER_BYTES, memberName, false)
  const currentSource = await boundedText(paths.current, MAX_POINTER_BYTES, memberName, false)
  if (anchorSource === undefined) invalidContext(memberName)
  const anchor = parseAnchor(anchorSource, identityDigest, memberName)
  if (currentSource === undefined) invalidContext(memberName)
  const pointer = parsePointer(currentSource, memberName)
  const manifest = await readManifest(paths, pointer.generation, pointer.manifest, memberName)
  if (pointer.sequence !== manifest.sequence) invalidContext(memberName)

  const visited = new Set<string>()
  let generation = manifest
  let generationDigest = pointer.manifest
  for (let depth = 0; depth < MAX_GENERATION_CHAIN_LENGTH; depth += 1) {
    if (visited.has(generation.generation)) invalidContext(memberName)
    visited.add(generation.generation)
    if (generation.sequence === 0) {
      if (generation.parent !== null || generation.parent_manifest !== null || generation.generation !== anchor.generation || generationDigest !== anchor.manifest) invalidContext(memberName)
      return { anchor, pointer, manifest }
    }
    if (generation.parent === null || generation.parent_manifest === null) invalidContext(memberName)
    const parentDigest = generation.parent_manifest
    const parent = await readManifest(paths, generation.parent, parentDigest, memberName)
    if (parent.sequence !== generation.sequence - 1) invalidContext(memberName)
    generation = parent
    generationDigest = parentDigest
  }
  invalidContext(memberName)
}
async function bootstrapOrRecover(paths: PrivatePaths, storageIdentity: string, memberName: string): Promise<void> {
  await withMutation(paths, storageIdentity, memberName, async () => {
    const identityDigest = hash(storageIdentity)
    const anchorSource = await boundedText(paths.anchor, MAX_POINTER_BYTES, memberName, false)
    const currentSource = await boundedText(paths.current, MAX_POINTER_BYTES, memberName, false)
    if (anchorSource === undefined && currentSource !== undefined) invalidContext(memberName)
    if (anchorSource !== undefined) {
      const anchor = parseAnchor(anchorSource, identityDigest, memberName)
      if (currentSource !== undefined) { await readAuthority(paths, storageIdentity, memberName); return }
      const files = await generationFiles(paths)
      if (files.length !== 1 || files[0] !== `${anchor.generation}.json`) invalidContext(memberName)
      const manifest = await readManifest(paths, anchor.generation, anchor.manifest, memberName)
      if (manifest.sequence !== 0 || manifest.parent !== null || manifest.parent_manifest !== null) invalidContext(memberName)
      const transaction = join(paths.staging, randomUUID())
      await mkdir(transaction, { mode: 0o700 })
      try { await publishPointer(paths, transaction, { version: 1, generation: anchor.generation, sequence: 0, manifest: anchor.manifest }, memberName) } finally { await rm(transaction, { recursive: true, force: true }).catch(() => undefined) }
      return
    }

    const legacy = await legacyItems(paths, memberName)
    const transaction = join(paths.staging, randomUUID())
    await mkdir(transaction, { mode: 0o700 })
    try {
      const items: ManifestItem[] = []
      for (const item of legacy) {
        const object = await publishObject(paths, transaction, item.content, memberName)
        items.push(Object.freeze({ id: item.id, title: item.title, retrievalCondition: item.retrievalCondition, object: object.digest, bytes: object.bytes }))
      }
      const generation = randomUUID()
      const manifest: GenerationManifest = Object.freeze({ version: 1, generation, parent: null, parent_manifest: null, sequence: 0, commit_key: hash(`bootstrap\0${identityDigest}\0${JSON.stringify(items)}`), items: Object.freeze(items) })
      const manifestDigest = await publishManifest(paths, transaction, manifest, memberName)
      const anchor: BootstrapAnchor = Object.freeze({ version: 1, storage_identity: identityDigest, generation, manifest: manifestDigest })
      const anchorTemp = join(transaction, 'generation-mode.tmp')
      await writeSynced(anchorTemp, pointerSource(anchor, memberName))
      await rename(anchorTemp, paths.anchor)
      await syncDirectory(paths.memoryDirectory)
      await publishPointer(paths, transaction, { version: 1, generation, sequence: 0, manifest: manifestDigest }, memberName)
    } finally { await rm(transaction, { recursive: true, force: true }).catch(() => undefined) }
  })
}

function validateCandidate(input: unknown, memberName: string): DurableAgentMemoryCandidateInput {
  if (!record(input) || !closed(input, CANDIDATE_KEYS) || !validText(input.title, MAX_METADATA_BYTES) || !validText(input.retrievalCondition, MAX_METADATA_BYTES) || typeof input.content !== 'string' || input.content.includes('\0') || utf8Bytes(input.content) > MAX_MEMORY_ITEM_BYTES || !validText(input.provenance, MAX_PROVENANCE_BYTES) || !['low', 'medium', 'high'].includes(input.confidence as string) || !Array.isArray(input.limitations) || input.limitations.length > MAX_LIMITATIONS || input.limitations.some(value => !validText(value, MAX_METADATA_BYTES))) rejected(memberName)
  if (utf8Bytes(JSON.stringify(input)) > MAX_CANDIDATE_BYTES) rejected(memberName)
  return input as unknown as DurableAgentMemoryCandidateInput
}
function validateApproved(input: unknown, memberName: string): DurableAgentApprovedMemoryInput {
  if (!record(input) || !closed(input, APPROVED_KEYS) || (input.candidateId !== undefined && (!validText(input.candidateId) || !REFERENCE_PART.test(input.candidateId))) || !record(input.item) || !closed(input.item, APPROVED_ITEM_KEYS) || !record(input.authorization) || !closed(input.authorization, AUTHORIZATION_KEYS)) rejected(memberName)
  const item = input.item, authorization = input.authorization
  if (!validText(item.id, MAX_METADATA_BYTES) || !MEMBER_NAME.test(item.id) || !validText(item.title, MAX_METADATA_BYTES) || !validText(item.retrievalCondition, MAX_METADATA_BYTES) || typeof item.content !== 'string' || item.content.includes('\0') || utf8Bytes(item.content) > MAX_MEMORY_ITEM_BYTES || !['human', 'authorized-host-workflow'].includes(authorization.kind as string) || !validText(authorization.authorizationRef, MAX_AUTHORIZATION_BYTES)) rejected(memberName)
  return input as unknown as DurableAgentApprovedMemoryInput
}
async function readCandidate(paths: PrivatePaths, candidateId: string, memberName: string): Promise<StoredCandidate> {
  const source = await boundedText(join(paths.candidates, `${candidateId}.json`), MAX_CANDIDATE_BYTES, memberName, false)
  if (source === undefined) rejected(memberName)
  let raw: unknown
  try { raw = JSON.parse(source) } catch { rejected(memberName) }
  if (!record(raw) || Object.keys(raw).sort().join(',') !== 'candidate_id,confidence,content,limitations,provenance,retrieval_condition,status,title,version' || raw.version !== 1 || raw.candidate_id !== candidateId || raw.status !== 'unconfirmed' || !validText(raw.title, MAX_METADATA_BYTES) || !validText(raw.retrieval_condition, MAX_METADATA_BYTES) || typeof raw.content !== 'string' || raw.content.includes('\0') || utf8Bytes(raw.content) > MAX_MEMORY_ITEM_BYTES || !validText(raw.provenance, MAX_PROVENANCE_BYTES) || !['low', 'medium', 'high'].includes(raw.confidence as string) || !Array.isArray(raw.limitations) || raw.limitations.length > MAX_LIMITATIONS || raw.limitations.some(value => !validText(value, MAX_METADATA_BYTES))) rejected(memberName)
  return raw as unknown as StoredCandidate
}

function contentDigest(value: unknown): string { return hash(JSON.stringify(value)) }

export class LocalDurableAgentProvider extends DurableAgentService {
  readonly providerName: string
  readonly #providerId = randomUUID()
  readonly #homeDirectory: string | undefined
  readonly #entries = new Map<string, Entry>()
  readonly #activeByIdentity = new Map<string, Entry>()
  readonly #releasedReferences = new Map<string, ReleasedReferenceTombstone>()

  constructor(ctx: Context, options: LocalDurableAgentProviderOptions = {}) {
    super(ctx, { selectiveMemoryRead: true, memoryCandidateSubmission: true, approvedMemoryCommit: true, workingArtifacts: true })
    this.providerName = validText(options.providerName) && PROVIDER_NAME.test(options.providerName) ? options.providerName : 'local-filesystem'
    this.#homeDirectory = options.homeDirectory
  }

  async validateDeclaration(workspace: string, declaration: DurableAgentDeclaration): Promise<void> {
    try {
      validateDeclarationShape(declaration)
      const canonicalWorkspace = await canonicalDirectory(workspace, 'INVALID_DECLARATION')
      profileSource(profileFor(freezeDeclaration(declaration), canonicalWorkspace))
      if (declaration.scope === 'global') {
        if (this.#homeDirectory === undefined) throw new DurableAgentError('UNSUPPORTED_SCOPE', { memberName: declaration.name, scope: 'global' })
        await canonicalDirectory(this.#homeDirectory, 'PROVIDER_UNAVAILABLE', true)
      }
    } catch (error) { publicFailure(error) }
  }

  async provision(workspaceInput: string, declarationInput: DurableAgentDeclaration): Promise<DurableAgentRef> {
    try {
      validateDeclarationShape(declarationInput)
      const workspace = await canonicalDirectory(workspaceInput, 'INVALID_DECLARATION')
      const declaration = freezeDeclaration(declarationInput)
      let owner = workspace
      if (declaration.scope === 'global') {
        if (this.#homeDirectory === undefined) throw new DurableAgentError('UNSUPPORTED_SCOPE', { memberName: declaration.name, scope: 'global' })
        owner = await canonicalDirectory(this.#homeDirectory, 'PROVIDER_UNAVAILABLE', true)
      }
      const identityKey = `${owner}\0${declaration.scope}\0${declaration.name}`
      const existing = this.#activeByIdentity.get(identityKey)
      const profile = profileFor(declaration, workspace)
      profileSource(profile)
      if (existing?.status === 'active') {
        if (!sameJson(existing.declaration, declaration)) throw new DurableAgentError('PROFILE_CONFLICT', { memberName: declaration.name })
        await verifyProfile(existing.paths.profile, profile)
        return existing.ref
      }
      const paths = await ensureBaseStorage(owner, profile)
      await bootstrapOrRecover(paths, identityKey, declaration.name)
      const token = randomUUID(), generation = randomUUID()
      const ref = `dar1.${this.#providerId}.${declaration.scope}.${generation}.${token}` as DurableAgentRef
      const entry: Entry = { token, ref, generation, declaration, profile, paths, identityKey, storageIdentity: identityKey, status: 'active', activeOperations: 0, drainWaiters: [], nextRevision: 0, itemRevisions: new Map() }
      this.#entries.set(token, entry); this.#activeByIdentity.set(identityKey, entry)
      return ref
    } catch (error) { publicFailure(error) }
  }

  #resolve(memberRef: DurableAgentRef, allowClosing = false): Entry {
    if (typeof memberRef !== 'string' || memberRef.length === 0) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'missing' })
    const parts = memberRef.split('.')
    if (parts.length !== 5 || parts[0] !== 'dar1' || parts.some(part => !REFERENCE_PART.test(part))) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'forged' })
    const [, providerId, scope, generation, token] = parts
    if (providerId !== this.#providerId) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'foreign' })
    const entry = this.#entries.get(token!)
    if (!entry) {
      const released = this.#releasedReferences.get(token!)
      if (!released) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'forged' })
      if (scope !== released.scope) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'scope-mismatch' })
      if (generation !== released.generation) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'stale' })
      throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { referenceState: 'released' })
    }
    if (scope !== entry.declaration.scope) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { memberName: entry.declaration.name, referenceState: 'scope-mismatch' })
    if (generation !== entry.generation) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { memberName: entry.declaration.name, referenceState: 'stale' })
    if (entry.status === 'closing' && !allowClosing) throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { memberName: entry.declaration.name, referenceState: 'released' })
    return entry
  }
  #revise(entry: Entry, previous: ContentRevision | undefined, value: unknown): ContentRevision {
    const digest = contentDigest(value)
    if (previous?.digest === digest) return previous
    entry.nextRevision += 1
    return Object.freeze({ digest, revision: entry.nextRevision })
  }
  async #admit<T>(memberRef: DurableAgentRef, operation: (entry: Entry) => Promise<T>): Promise<T> {
    const entry = this.#resolve(memberRef)
    entry.activeOperations += 1
    try { await verifyProfile(entry.paths.profile, entry.profile); return await operation(entry) } catch (error) { return publicFailure(error) } finally {
      entry.activeOperations -= 1
      if (entry.activeOperations === 0) for (const waiter of entry.drainWaiters.splice(0)) waiter()
    }
  }

  async openTaskContext(memberRef: DurableAgentRef): Promise<Readonly<DurableAgentTaskContext>> {
    return await this.#admit(memberRef, async entry => {
      const authority = await readAuthority(entry.paths, entry.storageIdentity, entry.declaration.name)
      const guidance = (await boundedText(entry.paths.guidance, MAX_GUIDANCE_BYTES, entry.declaration.name))!
      if (guidance.trim().length === 0) invalidContext(entry.declaration.name)
      const memoryCatalog = Object.freeze(authority.manifest.items.map(item => Object.freeze({ id: item.id, title: item.title, retrievalCondition: item.retrievalCondition })))
      const member = Object.freeze({ ref: entry.ref, name: entry.declaration.name, description: entry.declaration.description })
      const provenance = Object.freeze({ scope: entry.declaration.scope, provider: this.providerName, generation: entry.generation })
      const capabilities = Object.freeze({ ...this.features })
      const visible = { member, guidance, memoryCatalog, provenance, capabilities }
      entry.snapshotRevision = this.#revise(entry, entry.snapshotRevision, visible)
      return Object.freeze({ ...visible, revision: entry.snapshotRevision.revision })
    })
  }
  async readMemoryItem(memberRef: DurableAgentRef, itemId: string): Promise<Readonly<DurableAgentMemoryItem>> {
    return await this.#admit(memberRef, async entry => {
      const id = memoryId(itemId, entry.declaration.name, true)
      const authority = await readAuthority(entry.paths, entry.storageIdentity, entry.declaration.name)
      const item = authority.manifest.items.find(value => value.id === id)
      if (!item) throw new DurableAgentError('UNKNOWN_MEMORY_ITEM', { memberName: entry.declaration.name })
      const content = await readObject(entry.paths, item, entry.declaration.name)
      const value = { id: item.id, title: item.title, retrievalCondition: item.retrievalCondition, content }
      const revision = this.#revise(entry, entry.itemRevisions.get(id), value)
      entry.itemRevisions.set(id, revision)
      return Object.freeze({ ...value, revision: revision.revision })
    })
  }
  async submitMemoryCandidate(memberRef: DurableAgentRef, candidateInput: DurableAgentMemoryCandidateInput): Promise<Readonly<DurableAgentMemoryCandidate>> {
    return await this.#admit(memberRef, async entry => {
      const candidate = validateCandidate(candidateInput, entry.declaration.name)
      return await withMutation(entry.paths, entry.storageIdentity, entry.declaration.name, async () => {
        await readAuthority(entry.paths, entry.storageIdentity, entry.declaration.name)
        const candidateId = randomUUID()
        const stored: StoredCandidate = Object.freeze({ version: 1, candidate_id: candidateId, status: 'unconfirmed', title: candidate.title, retrieval_condition: candidate.retrievalCondition, content: candidate.content, provenance: candidate.provenance, confidence: candidate.confidence, limitations: Object.freeze([...candidate.limitations]) })
        const source = jsonSource(stored)
        if (utf8Bytes(source) > MAX_CANDIDATE_BYTES) rejected(entry.declaration.name)
        await atomicWrite(join(entry.paths.candidates, `${candidateId}.json`), source)
        return Object.freeze({ candidateId, status: 'unconfirmed' as const, title: stored.title, retrievalCondition: stored.retrieval_condition, provenance: stored.provenance, confidence: stored.confidence, limitations: stored.limitations })
      })
    })
  }
  async commitMemoryItem(memberRef: DurableAgentRef, approvedInput: DurableAgentApprovedMemoryInput): Promise<Readonly<DurableAgentCommittedMemoryItem>> {
    return await this.#admit(memberRef, async entry => {
      const approved = validateApproved(approvedInput, entry.declaration.name)
      return await withMutation(entry.paths, entry.storageIdentity, entry.declaration.name, async () => {
        if (approved.candidateId) {
          const candidate = await readCandidate(entry.paths, approved.candidateId, entry.declaration.name)
          if (candidate.title !== approved.item.title || candidate.retrieval_condition !== approved.item.retrievalCondition || candidate.content !== approved.item.content) rejected(entry.declaration.name)
        }
        const authority = await readAuthority(entry.paths, entry.storageIdentity, entry.declaration.name)
        const bodyDigest = hash(approved.item.content), bodyBytes = utf8Bytes(approved.item.content)
        const existing = authority.manifest.items.find(item => item.id === approved.item.id)
        if (existing && existing.title === approved.item.title && existing.retrievalCondition === approved.item.retrievalCondition && existing.object === bodyDigest && existing.bytes === bodyBytes) {
          const content = await readObject(entry.paths, existing, entry.declaration.name)
          const revision = this.#revise(entry, entry.itemRevisions.get(existing.id), { id: existing.id, title: existing.title, retrievalCondition: existing.retrievalCondition, content })
          entry.itemRevisions.set(existing.id, revision)
          return Object.freeze({ id: existing.id, title: existing.title, retrievalCondition: existing.retrievalCondition, revision: revision.revision, status: 'confirmed' as const })
        }
        if (!existing && authority.manifest.items.length >= MAX_MEMORY_ITEMS) rejected(entry.declaration.name)
        const transaction = join(entry.paths.staging, randomUUID())
        await mkdir(transaction, { mode: 0o700 })
        try {
          const object = await publishObject(entry.paths, transaction, approved.item.content, entry.declaration.name)
          const nextItem: ManifestItem = Object.freeze({ id: approved.item.id, title: approved.item.title, retrievalCondition: approved.item.retrievalCondition, object: object.digest, bytes: object.bytes })
          const items = [...authority.manifest.items]
          const index = items.findIndex(item => item.id === nextItem.id)
          if (index < 0) items.push(nextItem); else items[index] = nextItem
          const generation = randomUUID()
          const commitKey = hash(JSON.stringify({ authorization: approved.authorization, candidateId: approved.candidateId ?? null, item: approved.item }))
          const manifest: GenerationManifest = Object.freeze({ version: 1, generation, parent: authority.pointer.generation, parent_manifest: authority.pointer.manifest, sequence: authority.pointer.sequence + 1, commit_key: commitKey, items: Object.freeze(items) })
          const manifestDigest = await publishManifest(entry.paths, transaction, manifest, entry.declaration.name)
          await publishPointer(entry.paths, transaction, { version: 1, generation, sequence: manifest.sequence, manifest: manifestDigest }, entry.declaration.name)
          const selected = await readAuthority(entry.paths, entry.storageIdentity, entry.declaration.name)
          const committed = selected.manifest.items.find(item => item.id === nextItem.id)
          if (!committed) invalidContext(entry.declaration.name)
          const content = await readObject(entry.paths, committed, entry.declaration.name)
          const revision = this.#revise(entry, entry.itemRevisions.get(committed.id), { id: committed.id, title: committed.title, retrievalCondition: committed.retrievalCondition, content })
          entry.itemRevisions.set(committed.id, revision)
          return Object.freeze({ id: committed.id, title: committed.title, retrievalCondition: committed.retrievalCondition, revision: revision.revision, status: 'confirmed' as const })
        } finally { await rm(transaction, { recursive: true, force: true }).catch(() => undefined) }
      })
    })
  }
  async workingLocation(memberRef: DurableAgentRef): Promise<DurableAgentWorkingLocation> {
    return await this.#admit(memberRef, async entry => { await ensureDirectory(entry.paths.working, entry.declaration.name); return entry.paths.working as DurableAgentWorkingLocation })
  }
  async release(memberRef: DurableAgentRef): Promise<void> {
    try {
      const entry = this.#resolve(memberRef, true)
      if (entry.status !== 'active') throw new DurableAgentError('UNAUTHORIZED_REFERENCE', { memberName: entry.declaration.name, referenceState: 'released' })
      entry.status = 'closing'
      if (entry.activeOperations > 0) await new Promise<void>(resolveDrain => entry.drainWaiters.push(resolveDrain))
      if (this.#activeByIdentity.get(entry.identityKey) === entry) this.#activeByIdentity.delete(entry.identityKey)
      this.#entries.delete(entry.token); entry.drainWaiters.length = 0; entry.itemRevisions.clear()
      this.#releasedReferences.set(entry.token, Object.freeze({ generation: entry.generation, scope: entry.declaration.scope }))
      while (this.#releasedReferences.size > MAX_RELEASED_REFERENCE_TOMBSTONES) {
        const oldest = this.#releasedReferences.keys().next().value as string | undefined
        if (!oldest) break
        this.#releasedReferences.delete(oldest)
      }
    } catch (error) { publicFailure(error) }
  }
}
