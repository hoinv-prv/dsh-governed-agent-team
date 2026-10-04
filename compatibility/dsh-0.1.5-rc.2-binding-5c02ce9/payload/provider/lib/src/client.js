import { validateDurableAgentClientConfig } from './config.js';
export const name = '@deepseek-ai/dsh-durable-agent/client';
export const inject = Object.freeze(['@deepseek-ai/dsh-durable-agent']);
export function apply(_ctx, config) {
    return Object.freeze({ kind: 'durable-agent-client', config: validateDurableAgentClientConfig(config) });
}
export { validateDurableAgentClientConfig };
//# sourceMappingURL=client.js.map