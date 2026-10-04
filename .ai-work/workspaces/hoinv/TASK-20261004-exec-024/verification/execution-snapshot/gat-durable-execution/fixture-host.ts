/** Trusted fixture setup; recorded model calls own every task operation. */
import { symbols, type Context } from '@deepseek-ai/cordis'
import type {} from '@vuhoi/gat-core'
import { DurableAgentService } from '@deepseek-ai/dsh-durable-agent'

export const name = 'gat-durable-execution-fixture-host'
export const inject = ['agents', 'agentTeams', 'durableAgent']

/** Seed public memory and enable the existing Team initializer before the Lead's first request. */
export function apply(ctx: Context, config: { workspace: string }): void {
  let initialized = false
  ctx.on('agent/created', async ({ agent, signal }) => {
    if (agent.session.header.parentSession !== undefined) return
    if (initialized) throw new Error('fixture supports exactly one Lead')
    initialized = true
    const provider: unknown = Reflect.get(ctx.durableAgent, symbols.original) ?? ctx.durableAgent
    if (!(provider instanceof DurableAgentService)) throw new Error('fixture resolved a different WK module/constructor')
    const ref = await provider.provision(config.workspace, {
      name: 'worker', description: 'Explicit task memory worker',
      prompt: 'ROLE_ONLY: declare readiness without reading memory or executing a task.',
      context: 'fresh', scope: 'workspace', provider: 'deepseek-official', model: 'deepseek-v4-flash',
    })
    try {
      for (const [id, content] of [
        ['selected', 'TASK_SELECTED_MEMORY_BODY: cobalt tulip'],
        ['unselected', 'TASK_UNSELECTED_MEMORY_BODY: amber fern'],
      ] as const) {
        await provider.commitMemoryItem(ref, {
          item: { id, title: `MEMORY_CATALOG_${id}`, retrievalCondition: `MEMORY_INTENT_${id}`, content },
          authorization: { kind: 'authorized-host-workflow', authorizationRef: 'authored-gat-durable-execution-fixture' },
        })
      }
    } finally {
      await provider.release(ref)
    }
    if ((Reflect.get(ctx.durableAgent, symbols.original) ?? ctx.durableAgent) !== provider) {
      throw new Error('fixture WK provider identity changed')
    }
    const enabled = await ctx.agentTeams.enable(agent, signal ?? new AbortController().signal)
    if (!enabled.enabled || enabled.source !== 'workspace' || enabled.members.length !== 1 || enabled.members[0]?.name !== 'worker') {
      throw new Error('fixture did not enable its exact workspace roster')
    }
  })
}
