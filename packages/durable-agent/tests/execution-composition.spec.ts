/** Real GAT/WK task-memory experiments; prospective DETAIL_DESIGN §9. */
import { describe, expect, it, vi } from 'vitest'
import { cp, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import { boot, body, systemText } from './execution-harness.ts'

describe('task/intent memory without system prompt memory', () => {
  it('retrieves only on tool invocation, logs task result, leaves system prompt memory-free', async () => {
    const h = await boot(); expect(h.provisions).not.toHaveBeenCalled()
    const execution = await h.assign(); const worker = await h.live(execution.sessionId, 2)
    expect(h.contexts).not.toHaveBeenCalled(); expect(h.firstRequestReadCounts).toEqual([0]); expect(h.reads).toHaveBeenCalledTimes(1)
    const requests = h.requests(worker.id); expect(requests[0]!.tools?.map(tool => tool.name)).toContain('durable_agent_read_memory')
    expect(JSON.stringify(requests[0]!.messages)).not.toContain(body)
    expect(JSON.stringify(requests[1]!.messages)).toContain(body)
    expect(JSON.stringify(requests[0]!.messages)).not.toContain('role-bootstrap-history')
    for (const request of requests) {
      expect(systemText(request)).not.toMatch(/TASK_MEMORY_BODY_ONLY|catalog-selected|SOUL\.md|Working principles/)
      expect(request.tools?.map(tool => tool.name)).not.toContain('durable_agent_submit_candidate')
    }
    expect(systemText(requests[1]!)).toBe(systemText(requests[0]!))
    expect(JSON.stringify(worker.session.snapshotEvents().filter(event => event.type === 'tool/result'))).toContain(body)
    await h.ctx.agentTeams.cancelExecution(h.lead, execution.id)
    expect(h.releases).toHaveBeenCalledTimes(1)
  })

  it('denies unselected IDs at the actual executor without provider access', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const selected = await h.invoke(worker, 'selected'); expect(selected.isError).toBe(false)
    expect(JSON.stringify(selected.content)).toContain(body)
    const count = h.reads.mock.calls.length
    const denied = await h.invoke(worker, 'unselected'); expect(denied.isError).toBe(true)
    expect(h.reads).toHaveBeenCalledTimes(count); expect(JSON.stringify(denied)).not.toContain('UNSELECTED_BODY')
  })

  it.each([false, true])('no task selection or reviewer mode grants no memory tool, reviewer=%s', async reviewer => {
    const h = await boot({ mode: 'hang', reviewer })
    if (reviewer) {
      await expect(h.assign()).rejects.toBeDefined()
      expect(h.model.requests.every(request => request.sessionId === h.member.id || request.sessionId === h.lead.id)).toBe(true)
      expect(h.reads).not.toHaveBeenCalled(); expect(h.contexts).not.toHaveBeenCalled()
      return
    }
    const execution = await h.assign([])
    const worker = await h.live(execution.sessionId)
    expect(h.requests(worker.id)[0]!.tools?.map(tool => tool.name) ?? []).not.toContain('durable_agent_read_memory')
    expect((await h.invoke(worker, 'selected')).isError).toBe(true); expect(h.reads).not.toHaveBeenCalled(); expect(h.contexts).not.toHaveBeenCalled()
  })

  it.each(['body', 'result'])('bounds complete selected read %s without publishing body', async cap => {
    const h = await boot({ mode: 'hang', ...cap === 'body' ? { maxBodyBytes: 4 } : { maxResultBytes: 4 } })
    const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const result = await h.invoke(worker, 'selected'); expect(result.isError).toBe(true)
    expect(JSON.stringify(result)).not.toContain(body); expect(h.reads).toHaveBeenCalledTimes(1)
  })

  it('missing mapping rejects binding before any execution model request', async () => {
    const h = await boot({ mode: 'hang', missingMapping: true })
    await expect(h.assign()).rejects.toBeDefined()
    expect(h.provisions).not.toHaveBeenCalled(); expect(h.contexts).not.toHaveBeenCalled(); expect(h.reads).not.toHaveBeenCalled()
    expect(h.model.requests.every(request => request.sessionId === h.member.id || request.sessionId === h.lead.id)).toBe(true)
  })

  it('joins delayed reads on cancel, withholds late body and removes tools before release', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    // Capture the real method before replacing the spy; its original implementation remains provider-owned.
    h.reads.mockRestore(); const realRead = h.service.readMemoryItem.bind(h.service)
    vi.spyOn(h.service, 'readMemoryItem').mockImplementation(async (...args) => {
      const item = await realRead(...args); entered.resolve(); await gate.promise; return item
    })
    const reading = h.invoke(worker, 'selected')
    try {
      await entered.promise
      let settled = false
      const cancellation = h.ctx.agentTeams.cancelExecution(h.lead, execution.id).then(() => { settled = true })
      await vi.waitFor(() => expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).phase).toBe('closing'))
      await vi.waitFor(() => expect(worker.ctx.tools.schemas().map(tool => tool.name)).not.toContain('durable_agent_read_memory'))
      expect(settled).toBe(false); expect(h.releases).not.toHaveBeenCalled()
      gate.resolve(); expect((await reading).isError).toBe(true); await cancellation
      expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).phase).toBe('cancelled'); expect(h.releases).toHaveBeenCalledTimes(1)
    } finally { gate.resolve(); await reading }
  })

  it('checks binding authority on each retry and stops dispatch after plugin withdrawal', async () => {
    const h = await boot({ mode: 'retry' }); let stopped = false
    const observed = Promise.withResolvers<NonNullable<ReturnType<typeof h.ctx.agents.get>>>()
    h.ctx.on('agent/request-error', async ({ agent }, next) => {
      const execution = h.ctx.agentTeams.executionFor(agent); if (execution === undefined) return await next()
      await h.disposeBinding(); stopped = true; observed.resolve(agent)
      return { kind: 'retry' }
    })
    const execution = await h.assign(); await vi.waitFor(() => expect(stopped).toBe(true))
    await (await observed.promise).whenIdle()
    expect(h.requests(execution.sessionId)).toHaveLength(1); expect(h.contexts).not.toHaveBeenCalled()
    expect(h.releases).toHaveBeenCalledTimes(1)
  })

  it('reuses member storage on a second fresh assignment without prior conversation', async () => {
    const h = await boot({ mode: 'hang' }); const first = await h.assign(); const worker = await h.live(first.sessionId)
    expect((await h.invoke(worker, 'selected')).isError).toBe(false)
    await h.ctx.agentTeams.cancelExecution(h.lead, first.id)
    const second = await h.assign(); const next = await h.live(second.sessionId)
    expect(next.id).not.toBe(worker.id); expect((await h.invoke(next, 'selected')).isError).toBe(false)
    expect(JSON.stringify(h.requests(next.id)[0]!.messages)).not.toContain(body)
    expect(h.provisions).toHaveBeenCalledTimes(2); expect(h.contexts).not.toHaveBeenCalled()
  })

  it('denies a competing plugin owner before execution transport', async () => {
    const h = await boot({ mode: 'hang' }); await h.loadSecondBinding()
    await expect(h.assign()).rejects.toBeDefined()
    expect(h.provisions).toHaveBeenCalledTimes(1); expect(h.releases).toHaveBeenCalledTimes(1)
    expect(h.reads).not.toHaveBeenCalled(); expect(h.contexts).not.toHaveBeenCalled()
    expect(h.model.requests.every(request => request.sessionId === h.member.id || request.sessionId === h.lead.id)).toBe(true)
  })

  it('joins delayed physical release before terminal cancellation', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    h.releases.mockRestore(); const release = h.service.release.bind(h.service)
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    const releases = vi.spyOn(h.service, 'release').mockImplementation(async ref => {
      entered.resolve(); await gate.promise; await release(ref)
    })
    let settled = false
    const cancellation = h.ctx.agentTeams.cancelExecution(h.lead, execution.id).then(() => { settled = true })
    try {
      await entered.promise
      expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).phase).toBe('closing')
      expect(worker.ctx.tools.schemas().map(tool => tool.name)).not.toContain('durable_agent_read_memory')
      expect(settled).toBe(false); expect((await h.invoke(worker, 'selected')).isError).toBe(true)
      expect(h.reads).not.toHaveBeenCalled()
    } finally { gate.resolve(); await cancellation }
    expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).phase).toBe('cancelled')
    expect(releases).toHaveBeenCalledTimes(1)
  })

  it('reads newly committed content on explicit tool use without refreshing system prompt', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    expect((await h.invoke(worker, 'selected')).isError).toBe(false)
    const ref = await h.provisions.mock.results[0]!.value
    await h.service.commitMemoryItem(ref, { item: { id: 'selected', title: 'updated selected',
      retrievalCondition: 'task intent selected', content: 'TASK_MEMORY_NEW_BODY' },
      authorization: { kind: 'authorized-host-workflow', authorizationRef: 'disposable-qualification-update' } })
    const result = await h.invoke(worker, 'selected')
    expect(result.isError).toBe(false); expect(JSON.stringify(result)).toContain('TASK_MEMORY_NEW_BODY')
    expect(h.reads).toHaveBeenCalledTimes(2); expect(h.contexts).not.toHaveBeenCalled()
    expect(systemText(h.requests(worker.id)[0]!)).not.toContain(body)
    await h.ctx.agentTeams.cancelExecution(h.lead, execution.id)
    expect((await h.invoke(worker, 'selected')).isError).toBe(true); expect(h.reads).toHaveBeenCalledTimes(2)
  })

  it('denies a foreign Agent and terminal Session resume before WK access', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); await h.live(execution.sessionId)
    expect((await h.invoke(h.lead, 'selected')).isError).toBe(true); expect(h.reads).not.toHaveBeenCalled()
    await h.ctx.agentTeams.cancelExecution(h.lead, execution.id)
    await expect(h.ctx.agentLoop.resume(h.ctx, { resumeSessionId: execution.sessionId, parentAgent: h.lead,
      agentOptions: { provider: 'mock', model: 'mock' } })).rejects.toBeDefined()
    expect(h.ctx.agents.get(execution.sessionId)).toBeUndefined()
    expect(h.provisions).toHaveBeenCalledTimes(1); expect(h.reads).not.toHaveBeenCalled()
    expect(h.requests(execution.sessionId)).toHaveLength(1)
  })

  it('retains closing state and ownership quarantine after release failure', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const ref = await h.provisions.mock.results[0]!.value
    h.fixture.tolerateCleanupFailure = true
    h.releases.mockImplementation(async () => { throw new Error('controlled physical release failure') })
    try {
      await expect(h.ctx.agentTeams.cancelExecution(h.lead, execution.id)).rejects.toBeDefined()
      expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).phase).toBe('closing')
      expect((await h.invoke(worker, 'selected')).isError).toBe(true); expect(h.reads).not.toHaveBeenCalled()
      await expect(h.ctx.agentTeams.cancelExecution(h.lead, execution.id)).rejects.toBeDefined()
      expect(h.releases).toHaveBeenCalledTimes(1)
      await expect(h.assign()).rejects.toBeDefined()
    } finally {
      // Fixture-owned teardown only: never infer successful runtime settlement from this repair.
      h.releases.mockRestore(); await h.service.release(ref)
    }
  })

  it.each(['matching', 'missing-mapping', 'changed-profile'])('checks active checkpoint recovery before memory/model use: %s', async policy => {
    const first = await boot({ mode: 'hang' }); const execution = await first.assign(); const worker = await first.live(execution.sessionId)
    await first.ctx.sessions.flush(first.lead.session); await first.ctx.sessions.flush(worker.session)
    const checkpoint = join(first.fixture.root, 'live-checkpoint')
    await cp(join(first.fixture.root, 'sessions'), checkpoint, { recursive: true })
    await first.ctx.fiber.dispose()
    await rm(join(first.fixture.root, 'sessions'), { recursive: true, force: true })
    await cp(checkpoint, join(first.fixture.root, 'sessions'), { recursive: true })
    const second = await boot({ mode: 'hang',
      ...policy === 'missing-mapping' ? { missingMapping: true } : {},
      ...policy === 'changed-profile' ? { durableModel: 'changed-model' } : {},
      restart: { root: first.fixture.root, member: first.member, taskId: first.task.id } })
    expect(second.ctx.agentTeams.getExecution(second.lead, execution.id).phase).toBe('active')
    if (policy !== 'matching') {
      await expect(second.ctx.agentLoop.resume(second.ctx, { resumeSessionId: execution.sessionId, parentAgent: second.lead,
        agentOptions: { provider: 'mock', model: 'mock' } })).rejects.toBeDefined()
      expect(second.ctx.agents.get(execution.sessionId)).toBeUndefined()
      expect(second.requests(execution.sessionId)).toHaveLength(0)
      expect(second.reads).not.toHaveBeenCalled(); expect(second.contexts).not.toHaveBeenCalled()
      expect(second.provisions).toHaveBeenCalledTimes(policy === 'changed-profile' ? 1 : 0)
      return
    }
    const handle = await second.ctx.agentLoop.resume(second.ctx, { resumeSessionId: execution.sessionId, parentAgent: second.lead,
      agentOptions: { provider: 'mock', model: 'mock' } })
    expect(handle.agent).not.toBe(worker); expect(second.provisions).toHaveBeenCalledTimes(1)
    expect(await second.provisions.mock.results[0]!.value).not.toBe(await first.provisions.mock.results[0]!.value)
    expect(second.contexts).not.toHaveBeenCalled(); expect(second.reads).not.toHaveBeenCalled()
    handle.agent.followup(createUserMessage({ source: { kind: 'user' }, content: [{ type: 'text', text: 'Continue this exact active task.' }] }))
    await second.live(execution.sessionId)
    expect(systemText(second.requests(execution.sessionId)[0]!)).not.toContain(body)
    expect((await second.invoke(handle.agent, 'selected')).isError).toBe(false)
    expect(second.reads).toHaveBeenCalledTimes(1)
    await second.ctx.agentTeams.cancelExecution(second.lead, execution.id)
  })
})
