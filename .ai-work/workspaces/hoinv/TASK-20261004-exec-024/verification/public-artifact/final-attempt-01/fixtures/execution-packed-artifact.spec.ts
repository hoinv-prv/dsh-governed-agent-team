import { describe, expect, it } from 'vitest'
import { pathToFileURL } from 'node:url'
import { boot, body, systemText } from './execution-harness.ts'

const packedEntry = '/home/hoinv/work/dsh-governed-agent-team/.ai-work/workspaces/hoinv/TASK-20261004-exec-024/verification/public-artifact/final-attempt-01/consumer/current/package/lib/execution-composition.js'

describe('exact packed execution entry via real Loader', () => {
  it('reads only the selected item after first transport without system memory', async () => {
    const packed = await import(/* @vite-ignore */ pathToFileURL(packedEntry).href)
    expect(packed.name).toBe('gat-durable-execution')
    expect(Object.hasOwn(packed, 'default')).toBe(false)
    const h = await boot({ bindingFactory: config => ({
      name: packed.name,
      inject: packed.inject,
      apply: async ctx => await packed.apply(ctx, config),
    }) })
    expect(h.provisions).not.toHaveBeenCalled()
    const execution = await h.assign()
    const worker = await h.live(execution.sessionId, 2)
    const requests = h.requests(worker.id)
    expect(h.firstRequestReadCounts).toEqual([0])
    expect(h.contexts).not.toHaveBeenCalled()
    expect(h.reads).toHaveBeenCalledTimes(1)
    expect(JSON.stringify(requests[0]!.messages)).not.toContain(body)
    expect(JSON.stringify(requests[1]!.messages)).toContain(body)
    for (const request of requests) {
      expect(systemText(request)).not.toContain(body)
      expect(systemText(request)).not.toContain('catalog-selected')
    }
    expect(JSON.stringify(worker.session.snapshotEvents().filter(event => event.type === 'tool/result'))).toContain(body)
    await h.ctx.agentTeams.cancelExecution(h.lead, execution.id)
    expect(h.releases).toHaveBeenCalledTimes(1)
  })
})
