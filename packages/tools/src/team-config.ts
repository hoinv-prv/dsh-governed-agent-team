/** Workspace Team roster loading and built-in fallback definitions. */

import { lstat, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { parse } from 'yaml'

const MEMBER_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u
const DOCUMENT_KEYS = new Set(['version', 'members'])
const MEMBER_KEYS = new Set([
  'name', 'description', 'prompt', 'context', 'provider', 'model', 'reasoning_effort',
])

/** One normalized member definition ready for route preflight and provisioning. */
export interface TeamMemberDefinition {
  readonly name: string
  readonly description: string
  readonly prompt: string
  readonly context: 'fresh' | 'fork'
  readonly provider: string
  readonly model: string
  readonly reasoningEffort?: string
}

/** One loaded roster and its user-visible provenance. */
export interface LoadedTeamMembers {
  readonly source: 'workspace' | 'built-in-default'
  readonly diagnostics: string[]
  readonly members: TeamMemberDefinition[]
}

function record(value: unknown, label: string, keys: ReadonlySet<string>): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error(`${label} must be a mapping`)
  }
  const result = value as Record<string, unknown>
  const unknown = Object.keys(result).find(key => !keys.has(key))
  if (unknown !== undefined) throw new Error(`${label} contains unknown field ${JSON.stringify(unknown)}`)
  return result
}

function text(value: unknown, label: string, max: number): string {
  if (typeof value !== 'string' || value.trim().length === 0 || value !== value.trim()) {
    throw new Error(`${label} must be a trimmed non-empty string`)
  }
  if (value.length > max) throw new Error(`${label} exceeds ${max} characters`)
  return value
}

function normalizeMember(value: unknown, index: number): TeamMemberDefinition {
  const label = `members[${index}]`
  const member = record(value, label, MEMBER_KEYS)
  const name = text(member.name, `${label}.name`, 64)
  if (!MEMBER_NAME.test(name)) throw new Error(`${label}.name must be lower-kebab-case`)
  const context = member.context ?? 'fresh'
  if (context !== 'fresh' && context !== 'fork') throw new Error(`${label}.context must be fresh or fork`)
  const reasoningEffort = member.reasoning_effort === undefined
    ? undefined
    : text(member.reasoning_effort, `${label}.reasoning_effort`, 80)
  return {
    name,
    description: text(member.description, `${label}.description`, 200),
    prompt: text(member.prompt, `${label}.prompt`, 16_384),
    context,
    provider: text(member.provider, `${label}.provider`, 200),
    model: text(member.model, `${label}.model`, 200),
    ...reasoningEffort === undefined ? {} : { reasoningEffort },
  }
}

function normalizeDocument(value: unknown, maxMembers: number): TeamMemberDefinition[] {
  const document = record(value, 'team_members.yaml', DOCUMENT_KEYS)
  if (document.version !== 1) throw new Error('team_members.yaml version must be 1')
  if (!Array.isArray(document.members) || document.members.length === 0) {
    throw new Error('team_members.yaml members must be a non-empty array')
  }
  if (document.members.length > maxMembers) {
    throw new Error(`team_members.yaml defines ${document.members.length} members; maximum is ${maxMembers}`)
  }
  const members = document.members.map(normalizeMember)
  if (new Set(members.map(member => member.name)).size !== members.length) {
    throw new Error('team_members.yaml member names must be unique')
  }
  return members
}

/** Build the four-member starter Team on the Lead's current LLM provider. */
export function builtInTeamMembers(provider: string): TeamMemberDefinition[] {
  return [
    {
      name: 'advisor',
      description: 'Advises the Lead when requested.',
      prompt: 'Act as the Team advisor. Give evidence-based options, risks, and a concise recommendation when the Lead asks. Do not edit files unless explicitly assigned.',
      context: 'fresh',
      provider,
      model: 'gpt-5.6-sol',
    },
    {
      name: 'senior-dev',
      description: 'Handles complex implementation and rigorous reviews.',
      prompt: 'Handle complex implementation and careful code or design review. Verify assumptions, coordinate write scopes, and report concrete evidence.',
      context: 'fresh',
      provider,
      model: 'gpt-5.6-sol',
    },
    {
      name: 'dev',
      description: 'Handles normal implementation tasks.',
      prompt: 'Implement assigned normal-complexity tasks, coordinate through the Team board, and report verification evidence.',
      context: 'fresh',
      provider,
      model: 'gpt-5.6-terra',
    },
    {
      name: 'junior-dev',
      description: 'Handles simple tasks with a clear design.',
      prompt: 'Implement only clearly specified simple tasks. Escalate ambiguity or missing design to the Lead before editing.',
      context: 'fresh',
      provider,
      model: 'gpt-5.6-luna',
    },
  ]
}

/** Load a bounded literal workspace file, falling back to the built-in starter Team on any config error. */
export async function loadTeamMembers(
  cwd: string | undefined,
  fallbackProvider: string,
  maxMembers: number,
  maxBytes: number,
): Promise<LoadedTeamMembers> {
  try {
    if (cwd === undefined) throw new Error('the Session has no workspace')
    const path = join(cwd, 'team_members.yaml')
    const entry = await lstat(path)
    if (!entry.isFile() || entry.isSymbolicLink()) throw new Error('team_members.yaml must be a regular file')
    if (entry.size > maxBytes) throw new Error(`team_members.yaml exceeds ${maxBytes} bytes`)
    const source = await readFile(path, 'utf8')
    if (Buffer.byteLength(source, 'utf8') > maxBytes) throw new Error(`team_members.yaml exceeds ${maxBytes} bytes`)
    return { source: 'workspace', diagnostics: [], members: normalizeDocument(parse(source), maxMembers) }
  } catch (error: unknown) {
    const detail = error instanceof Error ? error.message : String(error)
    const redacted = cwd === undefined ? detail : detail.replaceAll(cwd, '<workspace>')
    return {
      source: 'built-in-default',
      diagnostics: [`Workspace Team config unavailable or invalid; used built-in defaults: ${redacted}`],
      members: builtInTeamMembers(fallbackProvider).slice(0, maxMembers),
    }
  }
}
