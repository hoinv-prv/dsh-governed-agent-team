/** Real GAT/WK task-memory experiments; prospective DETAIL_DESIGN §9. */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context, symbols } from '@deepseek-ai/cordis'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import Include from '@deepseek-ai/cordis-plugin-include'
import { brandString } from '@deepseek-ai/dsh-brand'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import Subagents from '@deepseek-ai/dsh-subagent'
import * as Spawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { LlmError, ToolCallId, createUserMessage } from '@deepseek-ai/dsh-llm'
import { LocalDurableAgentProvider, DurableAgentService } from '@deepseek-ai/dsh-durable-agent'
import { mkdtemp, mkdir, writeFile, rm, cp } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { MockAdapter, textResponse, toolCallResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import type { GenerateOptions } from '@deepseek-ai/dsh-llm'
import type { TeamExecutionBrief } from '@vuhoi/gat-core'
import TeamService from '../src/index.ts'
import { TestSessionQuery } from './test-session-query.ts'
import { prototype } from './task-memory-prototype.ts'

const fixtures: { ctx: Context; root: string; tolerateCleanupFailure: boolean }[] = []
afterEach(async () => {
  for (const fixture of fixtures.splice(0).reverse()) {
    try { await fixture.ctx.fiber.dispose() } catch (error) { if (!fixture.tolerateCleanupFailure) throw error }
    finally { await rm(fixture.root, { recursive: true, force: true }) }
  }
  vi.restoreAllMocks()
})
const signal = new AbortController().signal
const declaration = { name: 'worker', description: 'memory worker', prompt: 'role only',
  context: 'fresh' as const, scope: 'workspace' as const, provider: 'mock', model: 'mock' }
const body = 'TASK_MEMORY_BODY_ONLY'
const limits = { maxBodyBytes: 4096, maxResultBytes: 8192, maxSelectedItems: 8 }
const brief = (inputs: TeamExecutionBrief['inputs']): TeamExecutionBrief => ({
  objective: 'Use explicitly selected memory for this task intent', deliverables: ['task answer'],
  acceptanceCriteria: ['only selected memory'], allowedPaths: [], excludedWork: [], context: '', inputs,
  checks: [], stopConditions: [], returnFormat: 'summary',
})
function systemText(request: GenerateOptions): string {
  return request.messages.filter(message => message.role === 'system')
    .flatMap(message => message.content).filter(block => block.type === 'text').map(block => block.text).join('\n')
}
async function boot(options: { mode?: 'read' | 'hang' | 'retry'; reviewer?: boolean;
  missingMapping?: boolean; maxBodyBytes?: number; maxResultBytes?: number; durableModel?: string;
  restart?: { root: string; member: Awaited<ReturnType<Context['agentTeams']['spawnTeammate']>>['member'];
    taskId: Parameters<Context['agentTeams']['getTask']>[1] } } = {}) {
  const root = options.restart?.root ?? await mkdtemp(join(tmpdir(), 'gat-task-memory-'))
  const workspace = join(root, 'workspace'); await mkdir(workspace, { recursive: true })
  const ctx = new Context(); const fixture = { ctx, root, tolerateCleanupFailure: false }; fixtures.push(fixture)
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(JsonlSessionPersistence, { root: join(root, 'sessions') })
  await ctx.plugin(TestSessionQuery); await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(Subagents); await ctx.plugin(Spawn, { providerName: 'spawn' })
  await ctx.plugin(Loader); ctx.loader.builtins.include = Include
  ctx.loader.builtins['task-gat'] = TeamService; ctx.loader.builtins['task-wk'] = LocalDurableAgentProvider
  const base = join(root, 'base.yml')
  await writeFile(base, '- id: gat\n  name: "cordis:task-gat"\n- id: wk\n  name: "cordis:task-wk"\n')
  await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(base).href } }); await ctx.loader.await()
  const scoped = ctx.get('durableAgent'); if (scoped === undefined) throw new Error('WK unavailable')
  const provider: unknown = Reflect.get(scoped, symbols.original) ?? scoped
  if (!(provider instanceof DurableAgentService)) throw new Error('wrong public WK owner')
  const service = provider
  if (options.restart === undefined) {
    const seed = await service.provision(workspace, declaration)
    for (const id of ['selected', 'unselected']) await service.commitMemoryItem(seed, {
      item: { id, title: `catalog-${id}`, retrievalCondition: `task intent ${id}`, content: id === 'selected' ? body : 'UNSELECTED_BODY' },
      authorization: { kind: 'authorized-host-workflow', authorizationRef: 'disposable-qualification-seed' },
    })
    await service.release(seed)
  }
  const reads = vi.spyOn(service, 'readMemoryItem'); const contexts = vi.spyOn(service, 'openTaskContext')
  const provisions = vi.spyOn(service, 'provision'); const releases = vi.spyOn(service, 'release')
  const taskBinding = prototype({ workspace,
    members: options.missingMapping ? [] : [{ declaration: { ...declaration,
      ...options.durableModel === undefined ? {} : { model: options.durableModel } }, mode: options.reviewer ? 'reviewer' : 'task' }],
    limits: { ...limits, ...options.maxBodyBytes === undefined ? {} : { maxBodyBytes: options.maxBodyBytes },
      ...options.maxResultBytes === undefined ? {} : { maxResultBytes: options.maxResultBytes } },
  })
  let bindingContext: Context | undefined
  ctx.loader.builtins['task-binding'] = { ...taskBinding, async apply(owner: Context) {
    bindingContext = owner
    await taskBinding.apply(owner)
  } }
  const binding = join(root, 'binding.yml'); await writeFile(binding, '- id: binding\n  name: "cordis:task-binding"\n')
  await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(binding).href } }); await ctx.loader.await()
  const attempts = new Map<string, number>(); const firstRequestReadCounts: number[] = []
  const executionOf = (request: GenerateOptions) => {
    const agent = request.sessionId === undefined ? undefined : ctx.agents.get(request.sessionId)
    return agent === undefined ? undefined : ctx.agentTeams.executionFor(agent)
  }
  class Model extends MockAdapter {
    override async *stream(request: GenerateOptions) {
      const execution = executionOf(request)
      if (execution !== undefined && (options.mode === 'hang' || (attempts.get(execution.id) ?? 0) >= 1)) {
        this.requests.push(request)
        yield { type: 'block-start' as const, index: 0, blockType: 'text' as const }
        await new Promise<void>((_resolve, reject) => {
          if (request.signal?.aborted) { reject(new Error('aborted')); return }
          request.signal?.addEventListener('abort', () => reject(new Error('aborted')), { once: true })
        }); return
      }
      yield* super.stream(request)
    }
  }
  const model = new Model(Array.from({ length: 64 }, () => (request: GenerateOptions) => {
    const execution = executionOf(request)
    if (execution === undefined) return textResponse('role-bootstrap-history')
    attempts.set(execution.id, (attempts.get(execution.id) ?? 0) + 1)
    firstRequestReadCounts.push(reads.mock.calls.length)
    if (options.mode === 'retry') throw new LlmError('busy', 'RATE_LIMIT')
    return toolCallResponse('memory-call', 'durable_agent_read_memory', { itemId: 'selected' })
  }))
  ctx.llm.registerAdapter(['mock'], model)
  const lead = options.restart === undefined
    ? await ctx.agentLoop.create(SessionId('task-memory-lead'), { provider: 'mock', model: 'mock' })
    : (await ctx.agentLoop.resume(ctx, { resumeSessionId: SessionId('task-memory-lead'),
      agentOptions: { provider: 'mock', model: 'mock' } })).agent
  const member = options.restart?.member ?? (await ctx.agentTeams.spawnTeammate(lead, {
    name: 'worker', description: 'memory worker', provider: 'spawn', context: 'fresh',
    prompt: [{ type: 'text', text: 'role-bootstrap-history' }], signal,
  })).member
  await vi.waitFor(() => expect(ctx.agents.get(member.id)).toBeUndefined())
  const task = options.restart === undefined
    ? await ctx.agentTeams.createTask(lead, { subject: 'task memory', description: 'explicit intent' })
    : ctx.agentTeams.getTask(lead, options.restart.taskId)
  let count = 0
  const assign = (inputs: TeamExecutionBrief['inputs'] = [{ reference: 'durable-memory:selected' }]) => {
    const current = ctx.agentTeams.getTask(lead, task.id)
    return ctx.agentTeams.assignTask(lead, { requestId: brandString(`request-${++count}`), member: member.name,
      taskId: task.id, expectedRevision: current.revision, brief: brief(inputs), signal })
  }
  const requests = (sessionId: string) => model.requests.filter(request => request.sessionId === sessionId)
  const live = async (sessionId: SessionId, minimum = 1) => {
    await vi.waitFor(() => expect(requests(sessionId).length).toBeGreaterThanOrEqual(minimum))
    const agent = ctx.agents.get(sessionId); if (agent === undefined) throw new Error('execution not live'); return agent
  }
  const invoke = (agent: NonNullable<ReturnType<typeof ctx.agents.get>>, id: string) => ctx.tools.execute({
    name: 'durable_agent_read_memory', arguments: { itemId: id }, agent, callId: ToolCallId(`manual-${id}`), signal,
  })
  return { ctx, service, reads, contexts, provisions, releases, lead, member, task, assign, requests, live, invoke,
    model, workspace, fixture, firstRequestReadCounts,
    disposeBinding: async () => { if (bindingContext === undefined) throw new Error('binding not loaded'); await bindingContext.fiber.dispose() },
    loadSecondBinding: async () => {
      ctx.loader.builtins['task-binding-second'] = prototype({ workspace, members: [{ declaration, mode: 'task' }], limits })
      const path = join(root, 'second.yml'); await writeFile(path, '- id: second\n  name: "cordis:task-binding-second"\n')
      await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(path).href } }); await ctx.loader.await()
    } }
}

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
    const h = await boot({ mode: 'hang', reviewer }); const execution = await h.assign(reviewer ? undefined : [])
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
