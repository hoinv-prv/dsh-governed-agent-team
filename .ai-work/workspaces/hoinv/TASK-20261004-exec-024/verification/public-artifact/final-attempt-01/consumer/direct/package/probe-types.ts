import type { Context } from '@deepseek-ai/cordis'
import { createDurableAgentBinder, DurableOwnershipCoordinator } from '@vuhoi/gat-durable-agent'
import { apply, Config, name } from '@vuhoi/gat-durable-agent/composition'
import { apply as applyProvider } from '@vuhoi/gat-durable-agent/provider'

export const publicBinder: typeof createDurableAgentBinder = createDurableAgentBinder
export const publicCoordinator: typeof DurableOwnershipCoordinator = DurableOwnershipCoordinator
export const publicSchema = Config
const config: Config = { serviceBindingKey: 'durable-agent', dedicatedProvider: true, singleHostWorkspace: true }
export function compilePublicDirect(ctx: Context): void {
  applyProvider(ctx)
  apply(ctx, config)
  if (name !== 'gat-durable-agent') throw new Error('wrong entry')
}
