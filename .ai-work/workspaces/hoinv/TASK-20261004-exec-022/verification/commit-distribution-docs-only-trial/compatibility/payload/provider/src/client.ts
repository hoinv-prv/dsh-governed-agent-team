import type { Context } from '@deepseek-ai/cordis'
import { validateDurableAgentClientConfig, type DurableAgentClientConfig } from './config.js'

export const name = '@deepseek-ai/dsh-durable-agent/client'
export const inject = Object.freeze(['@deepseek-ai/dsh-durable-agent'])

export interface DurableAgentClientRegistration {
  readonly kind: 'durable-agent-client'
  readonly config: Readonly<DurableAgentClientConfig>
}

export function apply(_ctx: Context, config: DurableAgentClientConfig): DurableAgentClientRegistration {
  return Object.freeze({ kind: 'durable-agent-client', config: validateDurableAgentClientConfig(config) })
}

export { validateDurableAgentClientConfig }
export type { DurableAgentClientConfig }
