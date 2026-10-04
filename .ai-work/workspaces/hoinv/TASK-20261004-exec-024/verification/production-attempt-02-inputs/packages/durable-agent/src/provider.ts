/** Register a dedicated WK local provider through the provider's public API. */
import type { Context } from '@deepseek-ai/cordis'
import { LocalDurableAgentProvider } from '@deepseek-ai/dsh-durable-agent'

/** Cordis provider plugin name. */
export const name = 'gat-durable-provider'
/** The dedicated provider creates its own service. */
export const inject: string[] = []

/**
 * Register the provider without sharing an existing capability service.
 * @param ctx The selected provider's host scope.
 */
export function apply(ctx: Context): void {
  if (ctx.get('durableAgent') !== undefined) throw new Error('a Durable provider is already registered')
  new LocalDurableAgentProvider(ctx)
}
