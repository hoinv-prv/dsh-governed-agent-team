import assert from 'node:assert/strict'
import { Context, symbols } from '@deepseek-ai/cordis'

const graph = process.argv[2]
assert(graph === 'direct' || graph === 'current')
const provider = await import('@vuhoi/gat-durable-agent/provider')
const wk = await import('@deepseek-ai/dsh-durable-agent')
const consumer = await import('@deepseek-ai/dsh-durable-agent/consumer')
assert.equal(provider.name, 'gat-durable-provider')
assert.equal(wk.DurableAgentConsumer, consumer.DurableAgentConsumer)

const ctx = new Context()
provider.apply(ctx)
const scoped = ctx.get('durableAgent')
const owner = Reflect.get(scoped, symbols.original) ?? scoped
assert(owner instanceof wk.LocalDurableAgentProvider)
assert(owner instanceof wk.DurableAgentService)
assert.equal(owner.constructor, wk.LocalDurableAgentProvider)
await ctx.fiber.dispose()

const result = { graph, provider: Object.keys(provider), service: owner.constructor.name, sameConsumer: true, sameServiceConstructor: true }
if (graph === 'direct') {
  const root = await import('@vuhoi/gat-durable-agent')
  const composition = await import('@vuhoi/gat-durable-agent/composition')
  assert.equal(typeof root.createDurableAgentBinder, 'function')
  assert.equal(composition.name, 'gat-durable-agent')
  result.root = Object.keys(root)
  result.composition = Object.keys(composition)
} else {
  const execution = await import('@vuhoi/gat-durable-agent/execution-composition')
  assert.equal(execution.name, 'gat-durable-execution')
  assert.equal(typeof execution.apply, 'function')
  assert(execution.Config !== undefined)
  assert.equal(Object.hasOwn(execution, 'default'), false)
  result.execution = Object.keys(execution)
  result.noDefaultExecutionExport = true
}
console.log(JSON.stringify(result))
