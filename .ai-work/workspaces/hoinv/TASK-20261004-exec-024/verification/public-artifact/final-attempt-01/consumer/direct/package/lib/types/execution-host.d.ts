/** Current isolated execution ports; independent of the direct-member Host bridge. */
import { type Context } from '@deepseek-ai/cordis';
import type { Agent } from '@deepseek-ai/dsh-agent';
import type { TeamAssignmentTaskSnapshot, TeamExecutionId, TeamExecutionSnapshot } from '@deepseek-ai/dsh-experimental-agent-team/execution-types';
/** Public operations consumed by the execution adapter on its selected Host. */
export interface ExecutionTeamPort {
    executionFor(agent: Agent): TeamExecutionSnapshot | undefined;
    tryMembership(agent: Agent): Readonly<{
        id: string;
        root: Agent;
        role: 'lead' | 'teammate';
    }> | undefined;
    getTask(caller: Agent, id: TeamExecutionSnapshot['taskId']): Pick<TeamAssignmentTaskSnapshot, 'id' | 'revision' | 'status' | 'ownerMemberId'>;
    getExecution(caller: Agent, id: TeamExecutionId): TeamExecutionSnapshot;
}
/**
 * Resolve callable current-Host operations while preserving their original receiver.
 * @param ctx Plugin scope containing the registered Team service.
 * @returns The exact underlying owner, or a binding failure on an incompatible Host.
 */
export declare function resolveExecutionTeam(ctx: Context): ExecutionTeamPort;
/**
 * Check identity-bearing returned data before granting execution authority.
 * @param snapshot Current public execution snapshot returned by the selected service.
 */
export declare function assertExecutionSnapshot(snapshot: TeamExecutionSnapshot): void;
//# sourceMappingURL=execution-host.d.ts.map