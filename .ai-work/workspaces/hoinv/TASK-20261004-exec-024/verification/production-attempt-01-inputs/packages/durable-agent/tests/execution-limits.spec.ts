/** Closed configuration, executor bypass and publication/budget boundaries from DD §9. */
import { describe, expect, it, vi } from 'vitest'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { boot, body, signal } from './execution-harness.ts'
import { executionPlugin as prototype } from './execution-harness.ts'

describe('task memory closed bounds', () => {
  it('bounds denied content even with the smallest accepted result envelope', async () => {
    const h = await boot({ mode: 'hang', maxResultBytes: 2 }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const result = await h.invoke(worker, 'selected')
    expect(result.isError).toBe(true)
    expect(Buffer.byteLength(JSON.stringify(result.content), 'utf8')).toBeLessThanOrEqual(2)
  })
  it('withholds bounded replacement content as well as oversized replacements', async () => {
    const h = await boot({ mode: 'hang' })
    h.ctx.on('tools/post-execute', async (exec, _result, next) => exec.name === 'durable_agent_read_memory'
      ? { kind: 'accept', content: [{ type: 'text', text: 'INJECTED_BODY' }] } : await next())
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const result = await h.invoke(worker, 'selected')
    expect(JSON.stringify(result.content)).not.toContain('INJECTED_BODY')
  })

  it('denies nested memory calls before provider access', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const result = await h.ctx.tools.execute({ name: 'durable_agent_read_memory', arguments: { itemId: 'selected' },
      agent: worker, callId: ToolCallId('nested-memory'), signal,
      parent: { name: 'wrapper', agent: worker, callId: ToolCallId('wrapper'), signal, arguments: {} } })
    expect(result.isError).toBe(true); expect(h.reads).not.toHaveBeenCalled()
    expect(JSON.stringify(result)).not.toContain(body)
  })

  it('reserves concurrent attempt budgets before awaiting provider reads', async () => {
    const h = await boot({ mode: 'hang', bindingFactory: cfg => prototype({ ...cfg, limits: { ...cfg.limits, maxReadCalls: 1 } }) })
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const results = await Promise.all([h.invoke(worker, 'selected'), h.invoke(worker, 'selected')])
    expect(results.filter(result => result.isError)).toHaveLength(1); expect(h.reads).toHaveBeenCalledTimes(1)
  })

  it('bounds aggregate bytes before concurrent disclosure', async () => {
    const h = await boot({ mode: 'hang', bindingFactory: cfg => prototype({ ...cfg, limits: { ...cfg.limits, maxReadResultBytes: 1 } }) })
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const results = await Promise.all([h.invoke(worker, 'selected'), h.invoke(worker, 'selected')])
    expect(results.every(result => result.isError)).toBe(true)
    expect(JSON.stringify(results)).not.toContain(body)
  })

  it.each(['unknown-key', 'missing-limit', 'excess-limit', 'duplicate-name', 'unsupported-mode'])(
    'rejects malformed configuration (%s) at apply before WK provisioning', async kind => {
      let rejected = false
      const h = await boot({ mode: 'hang', bindingFactory: cfg => {
        const malformed = kind === 'unknown-key' ? { ...cfg, extra: true }
          : kind === 'missing-limit' ? { ...cfg, limits: Object.fromEntries(Object.entries(cfg.limits).filter(([key]) => key !== 'maxReadCalls')) }
          : kind === 'excess-limit' ? { ...cfg, limits: { ...cfg.limits, maxReadCalls: 33 } }
          : kind === 'duplicate-name' ? { ...cfg, members: [...cfg.members, ...cfg.members] }
          : { ...cfg, members: [{ ...cfg.members[0]!, mode: 'invalid' }] }
        const p = prototype(malformed as typeof cfg)
        // Loader records failed plugins instead of rejecting its await barrier. Observe apply itself.
        return { ...p, async apply(ctx) { try { await p.apply(ctx) } catch { rejected = true } } }
      } })
      expect(rejected).toBe(true); expect(h.provisions).not.toHaveBeenCalled()
      expect(h.reads).not.toHaveBeenCalled(); expect(h.contexts).not.toHaveBeenCalled()
    })
})
