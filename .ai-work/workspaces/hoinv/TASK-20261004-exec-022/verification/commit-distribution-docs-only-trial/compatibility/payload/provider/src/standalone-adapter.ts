import { lstat, readFile, realpath } from 'node:fs/promises'
import { isAbsolute, relative, resolve } from 'node:path'
import { parseDocument } from 'yaml'
import type { DurableAgentContextMode, DurableAgentDeclaration, DurableAgentStorageScope } from './service.js'

const MANIFEST_VERSION = 1 as const
const MAX_MEMBERS = 32
const MAX_MANIFEST_BYTES = 256 * 1024
const MEMBER_NAME = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/u
const MANIFEST_FILE_NAME = /^[A-Za-z0-9][A-Za-z0-9._-]*$/u
const MEMBER_KEYS = new Set(['name', 'description', 'prompt', 'context', 'provider', 'model', 'reasoning_effort', 'storage_scope'])
const MANIFEST_KEYS = new Set(['version', 'members'])

export type { DurableAgentStorageScope as DurableMemberStorageScope }

/** Legacy team_members.yaml declaration retained only at this boundary. */
export interface DurableMember {
  readonly name: string
  readonly description: string
  readonly prompt: string
  readonly context: DurableAgentContextMode
  readonly provider: string
  readonly model: string
  readonly reasoning_effort?: string
  readonly storage_scope: DurableAgentStorageScope
}

export interface DurableMembersManifest {
  readonly version: typeof MANIFEST_VERSION
  readonly members: readonly DurableMember[]
}

export interface MembersOptions {
  /** A workspace-root manifest file name; nested paths are rejected. Defaults to team_members.yaml. */
  readonly manifestPath?: string
  /** Trusted host/test seam for global members; consumed by storage, not this adapter. */
  readonly homeDirectory?: string
}

function fail(reason: string): never { throw new TypeError(`DURABLE_MEMBERS_${reason}`) }
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
async function canonicalWorkspace(value: string): Promise<string> {
  if (typeof value !== 'string' || value.length === 0 || value.includes('\0')) fail('INVALID_WORKSPACE')
  let canonical: string
  try { canonical = await realpath(resolve(value)) } catch { fail('INVALID_WORKSPACE') }
  const stat = await lstat(canonical)
  if (!stat.isDirectory()) fail('INVALID_WORKSPACE')
  return canonical
}
function manifestFile(root: string, options: MembersOptions): string {
  const candidate = options.manifestPath ?? 'team_members.yaml'
  if (typeof candidate !== 'string' || !MANIFEST_FILE_NAME.test(candidate) || candidate === '.' || candidate === '..' || isAbsolute(candidate)) fail('INVALID_MANIFEST_PATH')
  const path = resolve(root, candidate)
  const relation = relative(root, path)
  if (relation === '' || relation.startsWith('..') || isAbsolute(relation)) fail('INVALID_MANIFEST_PATH')
  return path
}
function declaration(member: DurableMember): DurableAgentDeclaration {
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

/** The sole parser/default resolver for legacy team_members.yaml. */
export async function loadDurableMembersManifest(workspaceRoot: string, options: MembersOptions = {}): Promise<DurableMembersManifest> {
  const workspace = await canonicalWorkspace(workspaceRoot)
  const path = manifestFile(workspace, options)
  let stat
  try { stat = await lstat(path) } catch { fail('MANIFEST_UNREADABLE') }
  if (stat.isSymbolicLink() || !stat.isFile() || stat.size > MAX_MANIFEST_BYTES) fail('INVALID_MANIFEST_FILE')
  const source = await readFile(path, 'utf8')
  if (Buffer.byteLength(source, 'utf8') > MAX_MANIFEST_BYTES || source.includes('\0')) fail('INVALID_MANIFEST_CONTENT')
  let parsed: unknown
  try {
    const document = parseDocument(source, { uniqueKeys: true })
    if (document.errors.length > 0 || document.warnings.length > 0) fail('MALFORMED_MANIFEST')
    parsed = document.toJS()
  } catch (error) {
    if (error instanceof TypeError && error.message.startsWith('DURABLE_MEMBERS_')) throw error
    fail('MALFORMED_MANIFEST')
  }
  const input = record(parsed, 'INVALID_MANIFEST')
  closed(input, MANIFEST_KEYS, 'MANIFEST_UNKNOWN_KEY')
  if (input.version !== MANIFEST_VERSION || !Array.isArray(input.members) || input.members.length > MAX_MEMBERS) fail('INVALID_MANIFEST')
  const seen = new Set<string>()
  const members = input.members.map((value): DurableMember => {
    const entry = record(value, 'INVALID_MEMBER')
    closed(entry, MEMBER_KEYS, 'MEMBER_UNKNOWN_KEY')
    const name = memberName(entry.name)
    if (seen.has(name)) fail('DUPLICATE_MEMBER')
    seen.add(name)
    const context = entry.context
    if (context !== 'fresh' && context !== 'fork') fail('INVALID_CONTEXT')
    const scope = entry.storage_scope ?? 'workspace'
    if (scope !== 'workspace' && scope !== 'global') fail('INVALID_STORAGE_SCOPE')
    const reasoning = entry.reasoning_effort === undefined ? undefined : text(entry.reasoning_effort, 'INVALID_REASONING_EFFORT')
    return Object.freeze({ name, description: text(entry.description, 'INVALID_DESCRIPTION'), prompt: text(entry.prompt, 'INVALID_PROMPT'), context, provider: text(entry.provider, 'INVALID_PROVIDER'), model: text(entry.model, 'INVALID_MODEL'), ...(reasoning === undefined ? {} : { reasoning_effort: reasoning }), storage_scope: scope })
  })
  return Object.freeze({ version: MANIFEST_VERSION, members: Object.freeze(members) })
}

/** Converts legacy declarations to the explicit service contract. */
export async function loadDurableAgentDeclarations(workspaceRoot: string, options: MembersOptions = {}): Promise<readonly DurableAgentDeclaration[]> {
  const manifest = await loadDurableMembersManifest(workspaceRoot, options)
  return Object.freeze(manifest.members.map(declaration))
}

/** Compatibility resolver; authorization happens only in the manifest adapter. */
export async function resolveLegacyDurableMember(workspaceRoot: string, name: string, options: MembersOptions = {}): Promise<{ readonly workspace: string, readonly member: DurableMember, readonly declaration: DurableAgentDeclaration }> {
  const workspace = await canonicalWorkspace(workspaceRoot)
  const manifest = await loadDurableMembersManifest(workspace, options)
  const normalizedName = memberName(name)
  const member = manifest.members.find(candidate => candidate.name === normalizedName)
  if (member === undefined) fail('UNKNOWN_MEMBER')
  return Object.freeze({ workspace, member, declaration: declaration(member) })
}
