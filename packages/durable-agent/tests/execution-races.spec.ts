/** Paired reproduction against sealed attempt-09 and prospective reviewed corrections. */
import { describe, expect, it, vi } from 'vitest'
import { boot, body, limits } from './execution-harness.ts'
import { executionPlugin as corrected } from './execution-harness.ts'

const variants = [
  { name: 'corrected candidate', factory: corrected, leaks: false },
]

describe.each(variants)('$name publication/preparation boundaries', ({ factory, leaks }) => {
  it('checks the final boundary after an awaited post-execute policy', async () => {
    const h = await boot({ mode: 'hang', bindingFactory: factory })
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    h.ctx.on('tools/post-execute', async (exec, _result, next) => {
      if (exec.name !== 'durable_agent_read_memory') return await next()
      entered.resolve(); await gate.promise; return { kind: 'accept' }
    })
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const reading = h.invoke(worker, 'selected')
    try {
      await entered.promise; await h.disposeBinding(); gate.resolve()
      const result = await reading
      // Native model/Session publication uses content; canonical values remain registry-owned.
      expect(JSON.stringify(result.content).includes(body)).toBe(leaks)
    } finally { gate.resolve(); await reading }
  })

  it('bounds replacement content after post-execute', async () => {
    const h = await boot({ mode: 'hang', bindingFactory: factory })
    h.ctx.on('tools/post-execute', async (exec, _result, next) => exec.name !== 'durable_agent_read_memory'
      ? await next() : { kind: 'accept', content: [{ type: 'text', text: 'OVERSIZED_REPLACEMENT' + 'x'.repeat(limits.maxResultBytes) }] })
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const result = await h.invoke(worker, 'selected')
    expect(JSON.stringify(result.content).includes('OVERSIZED_REPLACEMENT')).toBe(leaks)
    if (!leaks) expect(Buffer.byteLength(JSON.stringify(result.content), 'utf8')).toBeLessThanOrEqual(limits.maxResultBytes)
  })

  it('withholds a provider result with an unselected returned identity', async () => {
    const h = await boot({ mode: 'hang', bindingFactory: factory })
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    h.reads.mockRestore(); const realRead = h.service.readMemoryItem.bind(h.service)
    vi.spyOn(h.service, 'readMemoryItem').mockImplementation(async (ref, _requested) => await realRead(ref, 'unselected'))
    const result = await h.invoke(worker, 'selected')
    expect(JSON.stringify(result).includes('UNSELECTED_BODY')).toBe(leaks)
    if (!leaks) expect(result.isError).toBe(true)
  })

  it('cuts off withdrawal while real LLM preparation is pending', async () => {
    const h = await boot({ mode: 'hang', bindingFactory: factory })
    const realPrepare = h.ctx.llm.prepareCall.bind(h.ctx.llm)
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    vi.spyOn(h.ctx.llm, 'prepareCall').mockImplementation(async (...args) => {
      const prepared = await realPrepare(...args); entered.resolve(); await gate.promise; return prepared
    })
    const execution = await h.assign(); await entered.promise
    const worker = h.ctx.agents.get(execution.sessionId); if (worker === undefined) throw new Error('missing exact Agent')
    try {
      await h.disposeBinding(); gate.resolve()
      if (leaks) await vi.waitFor(() => expect(h.requests(execution.sessionId)).toHaveLength(1))
      else { await worker.whenIdle(); expect(h.requests(execution.sessionId)).toHaveLength(0) }
    } finally { gate.resolve(); await h.ctx.agentTeams.cancelExecution(h.lead, execution.id) }
  })
})
