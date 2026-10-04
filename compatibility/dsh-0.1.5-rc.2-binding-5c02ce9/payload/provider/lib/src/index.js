import { validateDurableAgentConfig } from './config.js';
import { LocalDurableAgentProvider } from './local-provider.js';
export const name = '@deepseek-ai/dsh-durable-agent';
export const inject = Object.freeze([]);
/** Publishes the versioned Cordis service before any Consumer can bind a reference. */
export function apply(ctx, config) {
    const service = new LocalDurableAgentProvider(ctx);
    return Object.freeze({ kind: 'durable-agent-host', config: validateDurableAgentConfig(config), service });
}
export * from './config.js';
export * from './consumer.js';
export * from './errors.js';
export * from './identity.js';
export { loadDurableAgentDeclarations, resolveLegacyDurableMember } from './standalone-adapter.js';
export * from './local-provider.js';
export * from './members.js';
export * from './service.js';
export * from './task-contract.js';
export * from './review-packet.js';
export * from './review-host.js';
//# sourceMappingURL=index.js.map