import type { Context } from '@deepseek-ai/cordis'
import { apply, Config, name, type ReviewInputPort } from '@vuhoi/gat-durable-agent/execution-composition'
import { apply as applyProvider, name as providerName } from '@vuhoi/gat-durable-agent/provider'

const config: Config = {
  workspace: '/tmp/qualified-workspace',
  dedicatedProvider: true,
  singleHostWorkspace: true,
  members: [{ mode: 'task', declaration: {
    name: 'worker', description: 'qualified worker', prompt: 'role only', context: 'fresh',
    scope: 'workspace', provider: 'mock', model: 'mock',
  } }],
  limits: { maxBodyBytes: 4096, maxResultBytes: 8192, maxSelectedItems: 8,
    maxReadCalls: 32, maxReadResultBytes: 262144 },
}
const reviewInput: ReviewInputPort = { resolve: async () => undefined }
export function compilePublicCurrent(ctx: Context): void {
  ctx.provide('gatDurableReviewInput', reviewInput)
  applyProvider(ctx)
  void apply(ctx, config)
  if (name !== 'gat-durable-execution' || providerName !== 'gat-durable-provider') throw new Error('wrong entry')
}
export const publicSchema = Config
