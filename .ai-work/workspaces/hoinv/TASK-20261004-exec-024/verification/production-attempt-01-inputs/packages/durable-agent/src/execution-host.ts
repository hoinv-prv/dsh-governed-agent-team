/** Current isolated execution ports; independent of the direct-member Host bridge. */
import { symbols, type Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type {
  TeamAssignmentTaskSnapshot, TeamExecutionId, TeamExecutionSnapshot,
} from '@deepseek-ai/dsh-experimental-agent-team/execution-types'
import { TeamError } from '@vuhoi/gat-core'

/** Public operations consumed by the execution adapter on its selected Host. */
export interface ExecutionTeamPort {
  executionFor(agent: Agent): TeamExecutionSnapshot | undefined
  tryMembership(agent: Agent): Readonly<{ id: string; root: Agent; role: 'lead' | 'teammate' }> | undefined
  getTask(caller: Agent, id: TeamExecutionSnapshot['taskId']): Pick<TeamAssignmentTaskSnapshot,
    'id' | 'revision' | 'status' | 'ownerMemberId'>
  getExecution(caller: Agent, id: TeamExecutionId): TeamExecutionSnapshot
}

function unavailable(): never { throw new TeamError('Execution binding unavailable.', 'TEAM_BINDING_UNAVAILABLE') }
function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}
function port(value: unknown): value is ExecutionTeamPort {
  return record(value) && ['executionFor', 'tryMembership', 'getTask', 'getExecution']
    .every(key => typeof value[key] === 'function')
}

/**
 * Resolve callable current-Host operations while preserving their original receiver.
 * @param ctx Plugin scope containing the registered Team service.
 * @returns The exact underlying owner, or a binding failure on an incompatible Host.
 */
export function resolveExecutionTeam(ctx: Context): ExecutionTeamPort {
  const scoped: unknown = ctx.get('agentTeams')
  if (!record(scoped)) unavailable()
  const owner: unknown = Reflect.get(scoped, symbols.original) ?? scoped
  if (!port(owner)) unavailable()
  return owner
}

/**
 * Check identity-bearing returned data before granting execution authority.
 * @param snapshot Current public execution snapshot returned by the selected service.
 */
export function assertExecutionSnapshot(snapshot: TeamExecutionSnapshot): void {
  if (!record(snapshot) || ['id', 'requestId', 'memberId', 'memberName', 'sessionId', 'taskId', 'provider']
    .some(key => typeof snapshot[key] !== 'string' || !(snapshot[key] as string).length)
    || !Number.isSafeInteger(snapshot.generation) || snapshot.generation < 1
    || !Number.isSafeInteger(snapshot.taskRevision) || snapshot.taskRevision < 1
    || !['provisioning', 'active', 'closing', 'completed', 'failed', 'cancelled'].includes(snapshot.phase)
    || !record(snapshot.brief) || !Array.isArray(snapshot.brief.inputs)
    || snapshot.brief.inputs.some(input => !record(input) || typeof input.reference !== 'string')
    || Buffer.byteLength(JSON.stringify(snapshot), 'utf8') > 65_536) unavailable()
}
