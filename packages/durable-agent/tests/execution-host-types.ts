/** Compile against the actual current GAT service, without assertion casts. */
import type TeamService from '@vuhoi/gat-core'
import type { ExecutionTeamPort } from '@vuhoi/gat-durable-agent/src/execution-host.ts'

export function currentExecutionPort(service: TeamService): ExecutionTeamPort {
  return service
}
