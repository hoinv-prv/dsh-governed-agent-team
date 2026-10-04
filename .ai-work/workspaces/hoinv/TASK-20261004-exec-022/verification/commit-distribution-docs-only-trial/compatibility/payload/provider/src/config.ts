export const ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256 = 'd19885139f8bbee3e9dcc792e903bde672cc575b6066db957214cbb2d40b541b' as const
export const DURABLE_ROLE_IDS = ['worker', 'triage', 'verify'] as const
export type DurableRoleId = typeof DURABLE_ROLE_IDS[number]

export interface SkillBinding {
  name: 'context-delegation'
  sha256: string
}

export interface DurableRoleBinding {
  role: DurableRoleId
  skill: SkillBinding
}

export interface DurableAgentConfig {
  schemaVersion: 1
  roles: Record<DurableRoleId, DurableRoleBinding>
}

export interface DurableAgentClientConfig {
  schemaVersion: 1
  hostBinding: '@deepseek-ai/dsh-durable-agent'
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

export function validateSkillBinding(value: unknown, role: DurableRoleId): DurableRoleBinding {
  if (!isRecord(value) || value.role !== role || !isRecord(value.skill)) {
    throw new TypeError(`DURABLE_AGENT_INVALID_ROLE_BINDING:${role}`)
  }
  if (value.skill.name !== 'context-delegation') {
    throw new TypeError(`DURABLE_AGENT_SKILL_NAME_MISMATCH:${role}`)
  }
  if (value.skill.sha256 !== ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256) {
    throw new TypeError(`DURABLE_AGENT_SKILL_HASH_MISMATCH:${role}`)
  }
  return Object.freeze({
    role,
    skill: Object.freeze({ name: 'context-delegation', sha256: ACCEPTED_CONTEXT_DELEGATION_SKILL_SHA256 }),
  })
}

export function validateDurableAgentConfig(value: unknown): Readonly<DurableAgentConfig> {
  if (!isRecord(value) || value.schemaVersion !== 1 || !isRecord(value.roles)) {
    throw new TypeError('DURABLE_AGENT_INVALID_CONFIG')
  }
  const roleInputs = value.roles
  const keys = Object.keys(roleInputs).sort()
  if (keys.join(',') !== [...DURABLE_ROLE_IDS].sort().join(',')) {
    throw new TypeError('DURABLE_AGENT_ROLE_SET_MISMATCH')
  }
  const roles = Object.fromEntries(DURABLE_ROLE_IDS.map(role => [role, validateSkillBinding(roleInputs[role], role)])) as Record<DurableRoleId, DurableRoleBinding>
  return Object.freeze({ schemaVersion: 1, roles: Object.freeze(roles) })
}

export function validateDurableAgentClientConfig(value: unknown): Readonly<DurableAgentClientConfig> {
  if (!isRecord(value) || value.schemaVersion !== 1 || value.hostBinding !== '@deepseek-ai/dsh-durable-agent' || Object.keys(value).sort().join(',') !== 'hostBinding,schemaVersion') {
    throw new TypeError('DURABLE_AGENT_CLIENT_HOST_BINDING_REQUIRED')
  }
  return Object.freeze({ schemaVersion: 1, hostBinding: '@deepseek-ai/dsh-durable-agent' })
}
