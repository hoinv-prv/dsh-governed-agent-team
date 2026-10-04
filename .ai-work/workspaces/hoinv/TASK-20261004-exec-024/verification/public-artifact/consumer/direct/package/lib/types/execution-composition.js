import z from '@deepseek-ai/schemastery';
import { installExecutionBindings } from "./execution-binding.js";
import { resolveReviewInstaller } from "./execution-review.js";
/** Cordis plugin name, separate from the direct-continuable composition. */
export const name = 'gat-durable-execution';
/** Required selected Host services; the review input service is optional. */
export const inject = ['agentTeams', 'agents', 'tools', 'durableAgent'];
/** Loader validation; no topology assertions or limits are defaulted. */
export const Config = z.object({
    workspace: z.string().min(1).required(), dedicatedProvider: z.const(true).required(), singleHostWorkspace: z.const(true).required(),
    members: z.array(z.object({
        mode: z.union(['task', 'reviewer']).required(),
        declaration: z.object({ name: z.string().min(1).required(), description: z.string().required(), prompt: z.string().required(),
            context: z.const('fresh').required(), scope: z.const('workspace').required(), provider: z.string().min(1).required(), model: z.string().min(1).required(),
            reasoningEffort: z.string().min(1) }).required(),
    }).required()).max(32).required(),
    limits: z.object({ maxBodyBytes: z.number().step(1).min(1).max(65_536).required(),
        maxResultBytes: z.number().step(1).min(2).max(65_536).required(), maxSelectedItems: z.number().step(1).min(1).max(32).required(),
        maxReadCalls: z.number().step(1).min(1).max(32).required(), maxReadResultBytes: z.number().step(1).min(1).max(262_144).required() }).required(),
});
/**
 * Bind current task executions before first request without adding system memory.
 * @param ctx Scope owning binding listeners and physical cleanup.
 * @param config Explicit dedicated single-Host policy and member mappings.
 */
export async function apply(ctx, config) {
    z.resolve(config, Config, {});
    await installExecutionBindings(ctx, config, resolveReviewInstaller(ctx));
}
//# sourceMappingURL=execution-composition.js.map