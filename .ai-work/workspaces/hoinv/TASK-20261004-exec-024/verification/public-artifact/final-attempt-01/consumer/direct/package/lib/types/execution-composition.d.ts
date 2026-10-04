/** Opt-in task/intent memory and explicit reviewer input for fresh GAT executions. */
import type { Context } from '@deepseek-ai/cordis';
import z from '@deepseek-ai/schemastery';
import { type ExecutionCompositionConfig } from './execution-binding.ts';
/** Cordis plugin name, separate from the direct-continuable composition. */
export declare const name = "gat-durable-execution";
/** Required selected Host services; the review input service is optional. */
export declare const inject: string[];
/** Closed host-owned configuration for this entry. */
export type Config = ExecutionCompositionConfig;
/** Loader validation; no topology assertions or limits are defaulted. */
export declare const Config: z<Schemastery.ObjectS<NoInfer<{
    workspace: z<string, string, "defined">;
    dedicatedProvider: z<true, true, "defined">;
    singleHostWorkspace: z<true, true, "defined">;
    members: z<({
        mode?: "task" | "reviewer" | null;
        declaration?: ({
            name?: string | null;
            description?: string | null;
            prompt?: string | null;
            context?: "fresh" | null;
            scope?: "workspace" | null;
            provider?: string | null;
            model?: string | null;
            reasoningEffort?: string | null;
        } & import("@deepseek-ai/cosmokit").Dict) | null;
    } & import("@deepseek-ai/cosmokit").Dict)[], Schemastery.ObjectT<NoInfer<{
        mode: z<"task" | "reviewer", "task" | "reviewer", "defined">;
        declaration: z<Schemastery.ObjectS<NoInfer<{
            name: z<string, string, "defined">;
            description: z<string, string, "defined">;
            prompt: z<string, string, "defined">;
            context: z<"fresh", "fresh", "defined">;
            scope: z<"workspace", "workspace", "defined">;
            provider: z<string, string, "defined">;
            model: z<string, string, "defined">;
            reasoningEffort: z<string, string, "plain">;
        }>>, Schemastery.ObjectT<NoInfer<{
            name: z<string, string, "defined">;
            description: z<string, string, "defined">;
            prompt: z<string, string, "defined">;
            context: z<"fresh", "fresh", "defined">;
            scope: z<"workspace", "workspace", "defined">;
            provider: z<string, string, "defined">;
            model: z<string, string, "defined">;
            reasoningEffort: z<string, string, "plain">;
        }>>, "defined">;
    }>>[], "defined">;
    limits: z<Schemastery.ObjectS<NoInfer<{
        maxBodyBytes: z<number, number, "defined">;
        maxResultBytes: z<number, number, "defined">;
        maxSelectedItems: z<number, number, "defined">;
        maxReadCalls: z<number, number, "defined">;
        maxReadResultBytes: z<number, number, "defined">;
    }>>, Schemastery.ObjectT<NoInfer<{
        maxBodyBytes: z<number, number, "defined">;
        maxResultBytes: z<number, number, "defined">;
        maxSelectedItems: z<number, number, "defined">;
        maxReadCalls: z<number, number, "defined">;
        maxReadResultBytes: z<number, number, "defined">;
    }>>, "defined">;
}>>, Schemastery.ObjectT<NoInfer<{
    workspace: z<string, string, "defined">;
    dedicatedProvider: z<true, true, "defined">;
    singleHostWorkspace: z<true, true, "defined">;
    members: z<({
        mode?: "task" | "reviewer" | null;
        declaration?: ({
            name?: string | null;
            description?: string | null;
            prompt?: string | null;
            context?: "fresh" | null;
            scope?: "workspace" | null;
            provider?: string | null;
            model?: string | null;
            reasoningEffort?: string | null;
        } & import("@deepseek-ai/cosmokit").Dict) | null;
    } & import("@deepseek-ai/cosmokit").Dict)[], Schemastery.ObjectT<NoInfer<{
        mode: z<"task" | "reviewer", "task" | "reviewer", "defined">;
        declaration: z<Schemastery.ObjectS<NoInfer<{
            name: z<string, string, "defined">;
            description: z<string, string, "defined">;
            prompt: z<string, string, "defined">;
            context: z<"fresh", "fresh", "defined">;
            scope: z<"workspace", "workspace", "defined">;
            provider: z<string, string, "defined">;
            model: z<string, string, "defined">;
            reasoningEffort: z<string, string, "plain">;
        }>>, Schemastery.ObjectT<NoInfer<{
            name: z<string, string, "defined">;
            description: z<string, string, "defined">;
            prompt: z<string, string, "defined">;
            context: z<"fresh", "fresh", "defined">;
            scope: z<"workspace", "workspace", "defined">;
            provider: z<string, string, "defined">;
            model: z<string, string, "defined">;
            reasoningEffort: z<string, string, "plain">;
        }>>, "defined">;
    }>>[], "defined">;
    limits: z<Schemastery.ObjectS<NoInfer<{
        maxBodyBytes: z<number, number, "defined">;
        maxResultBytes: z<number, number, "defined">;
        maxSelectedItems: z<number, number, "defined">;
        maxReadCalls: z<number, number, "defined">;
        maxReadResultBytes: z<number, number, "defined">;
    }>>, Schemastery.ObjectT<NoInfer<{
        maxBodyBytes: z<number, number, "defined">;
        maxResultBytes: z<number, number, "defined">;
        maxSelectedItems: z<number, number, "defined">;
        maxReadCalls: z<number, number, "defined">;
        maxReadResultBytes: z<number, number, "defined">;
    }>>, "defined">;
}>>, "plain">;
export type { ReviewInputPort, ReviewInput, ReviewSelection, ReviewerAssignment, ReviewedCandidate, ReviewAuditEvent } from './execution-review.ts';
/**
 * Bind current task executions before first request without adding system memory.
 * @param ctx Scope owning binding listeners and physical cleanup.
 * @param config Explicit dedicated single-Host policy and member mappings.
 */
export declare function apply(ctx: Context, config: Config): Promise<void>;
//# sourceMappingURL=execution-composition.d.ts.map