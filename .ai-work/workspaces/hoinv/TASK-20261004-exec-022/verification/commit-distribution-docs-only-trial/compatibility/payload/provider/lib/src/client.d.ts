import type { Context } from '@deepseek-ai/cordis';
import { validateDurableAgentClientConfig, type DurableAgentClientConfig } from './config.js';
export declare const name = "@deepseek-ai/dsh-durable-agent/client";
export declare const inject: readonly string[];
export interface DurableAgentClientRegistration {
    readonly kind: 'durable-agent-client';
    readonly config: Readonly<DurableAgentClientConfig>;
}
export declare function apply(_ctx: Context, config: DurableAgentClientConfig): DurableAgentClientRegistration;
export { validateDurableAgentClientConfig };
export type { DurableAgentClientConfig };
//# sourceMappingURL=client.d.ts.map