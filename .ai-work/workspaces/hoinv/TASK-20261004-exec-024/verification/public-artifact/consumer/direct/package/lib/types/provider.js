import { LocalDurableAgentProvider } from '@deepseek-ai/dsh-durable-agent';
/** Cordis provider plugin name. */
export const name = 'gat-durable-provider';
/** The dedicated provider creates its own service. */
export const inject = [];
/**
 * Register the provider without sharing an existing capability service.
 * @param ctx The selected provider's host scope.
 */
export function apply(ctx) {
    if (ctx.get('durableAgent') !== undefined)
        throw new Error('a Durable provider is already registered');
    new LocalDurableAgentProvider(ctx);
}
//# sourceMappingURL=provider.js.map