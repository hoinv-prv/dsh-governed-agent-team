/** Exact isolated execution memory lifetime; GAT Detail Design §§9–10. */
import { type Context } from '@deepseek-ai/cordis';
import type { Agent } from '@deepseek-ai/dsh-agent';
import type { DurableAgentDeclaration } from '@deepseek-ai/dsh-durable-agent';
import type { TeamExecutionSnapshot } from '@deepseek-ai/dsh-experimental-agent-team/execution-types';
import { type ExecutionTeamPort } from './execution-host.ts';
/** Explicit topology, durable members and task-result limits. */
export interface ExecutionCompositionConfig {
    readonly dedicatedProvider: true;
    readonly singleHostWorkspace: true;
    readonly workspace: string;
    readonly members: readonly Readonly<{
        declaration: DurableAgentDeclaration;
        mode: 'task' | 'reviewer';
    }>[];
    readonly limits: Readonly<{
        maxBodyBytes: number;
        maxResultBytes: number;
        maxSelectedItems: number;
        maxReadCalls: number;
        maxReadResultBytes: number;
    }>;
}
/** Binding-owned authority and callback drain available to the optional reviewer. */
export interface ExecutionBindingScope {
    readonly team: ExecutionTeamPort;
    readonly ctx: Context;
    readonly agent: Agent;
    readonly root: Agent;
    readonly execution: TeamExecutionSnapshot;
    readonly configuration: ExecutionCompositionConfig;
    assertCurrent(): void;
    assertActive(): void;
    revoke(): void;
    track<T>(run: () => Promise<T>): Promise<T>;
    own(dispose: () => void): void;
}
/** Install reviewer tools while the exact execution is still provisioning. */
export type ExecutionReviewInstaller = (scope: ExecutionBindingScope) => Promise<void>;
/**
 * Install exact task bindings and Agent-owned guards through the plugin scope.
 * @param ctx Selected current Host context.
 * @param config Explicit normalized topology/member policy.
 * @param reviewInstaller Optional trusted reviewer installer; never used by ordinary tasks.
 */
export declare function installExecutionBindings(ctx: Context, input: ExecutionCompositionConfig, reviewInstaller?: ExecutionReviewInstaller): Promise<void>;
//# sourceMappingURL=execution-binding.d.ts.map