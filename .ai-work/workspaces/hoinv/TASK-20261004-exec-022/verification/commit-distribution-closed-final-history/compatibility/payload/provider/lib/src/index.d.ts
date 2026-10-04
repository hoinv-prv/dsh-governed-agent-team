import type { Context } from '@deepseek-ai/cordis';
import { type DurableAgentConfig } from './config.js';
import type { DurableAgentService } from './service.js';
export declare const name = "@deepseek-ai/dsh-durable-agent";
export declare const inject: readonly string[];
export interface DurableAgentHostRegistration {
    readonly kind: 'durable-agent-host';
    readonly config: Readonly<DurableAgentConfig>;
    readonly service: DurableAgentService;
}
/** Publishes the versioned Cordis service before any Consumer can bind a reference. */
export declare function apply(ctx: Context, config: DurableAgentConfig): DurableAgentHostRegistration;
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
//# sourceMappingURL=index.d.ts.map