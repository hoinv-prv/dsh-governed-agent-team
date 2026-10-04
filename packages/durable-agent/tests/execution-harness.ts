/** Real GAT/WK task-memory experiments; prospective DETAIL_DESIGN §9. */
import { afterEach, expect, vi } from 'vitest'
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
import { LlmError, ToolCallId } from '@deepseek-ai/dsh-llm'
import { LocalDurableAgentProvider, DurableAgentService } from '@deepseek-ai/dsh-durable-agent'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { MockAdapter, textResponse, toolCallResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import type { GenerateOptions } from '@deepseek-ai/dsh-llm'
import type { TeamExecutionBrief } from '@vuhoi/gat-core'
import TeamService from '@vuhoi/gat-core'
import { TestSessionQuery } from '../../gat-core/tests/test-session-query.ts'
import * as Composition from '../src/execution-composition.ts'
import type { ReviewInputPort } from '../src/execution-composition.ts'
/** Test composition invokes the named public entry through the real Loader. */
export function executionPlugin(config: Composition.Config) {
  return { name: Composition.name, inject: Composition.inject, apply: async (ctx: Context) => await Composition.apply(ctx, config) }
}

const fixtures: { ctx: Context; root: string; tolerateCleanupFailure: boolean }[] = []
afterEach(async () => {
  for (const fixture of fixtures.splice(0).reverse()) {
    try { await fixture.ctx.fiber.dispose() } catch (error) { if (!fixture.tolerateCleanupFailure) throw error }
    finally { await rm(fixture.root, { recursive: true, force: true }) }
  }
  vi.restoreAllMocks()
})
export const signal = new AbortController().signal
export const declaration = { name: 'worker', description: 'memory worker', prompt: 'role only',
  context: 'fresh' as const, scope: 'workspace' as const, provider: 'mock', model: 'mock' }
export const body = 'TASK_MEMORY_BODY_ONLY'
export const limits = { maxBodyBytes: 4096, maxResultBytes: 8192, maxSelectedItems: 8, maxReadCalls: 32, maxReadResultBytes: 262144 }
export const brief = (inputs: TeamExecutionBrief['inputs']): TeamExecutionBrief => ({
  objective: 'Use explicitly selected memory for this task intent', deliverables: ['task answer'],
  acceptanceCriteria: ['only selected memory'], allowedPaths: [], excludedWork: [], context: '', inputs,
  checks: [], stopConditions: [], returnFormat: 'summary',
})
export function systemText(request: GenerateOptions): string {
  return request.messages.filter(message => message.role === 'system')
    .flatMap(message => message.content).filter(block => block.type === 'text').map(block => block.text).join('\n')
}
export async function boot(options: { mode?: 'read' | 'hang' | 'retry'; reviewer?: boolean;
  bindingFactory?: (config: Parameters<typeof executionPlugin>[0]) => ReturnType<typeof executionPlugin>; missingMapping?: boolean; maxBodyBytes?: number; maxResultBytes?: number; durableModel?: string; reviewInputPort?: ReviewInputPort;
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
  const taskBinding = (options.bindingFactory ?? executionPlugin)({ workspace, dedicatedProvider: true, singleHostWorkspace: true,
    members: options.missingMapping ? [] : [{ declaration: { ...declaration,
      ...options.durableModel === undefined ? {} : { model: options.durableModel } }, mode: options.reviewer ? 'reviewer' : 'task' }],
    limits: { ...limits, ...options.maxBodyBytes === undefined ? {} : { maxBodyBytes: options.maxBodyBytes },
      ...options.maxResultBytes === undefined ? {} : { maxResultBytes: options.maxResultBytes } },
  })
  let bindingContext: Context | undefined
  ctx.loader.builtins['task-binding'] = { ...taskBinding, async apply(owner: Context) {
    bindingContext = owner
    if (options.reviewInputPort !== undefined) owner.provide('gatDurableReviewInput', options.reviewInputPort)
    await taskBinding.apply(owner)
  } }
  const binding = join(root, 'binding.yml'); await writeFile(binding, '- id: binding\n  name: "cordis:task-binding"\n')
  await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(binding).href } }); await ctx.loader.await()
  for (const entry of ctx.loader.entries()) await entry.fiber?.await()
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
    setReviewInputPort: (port: ReviewInputPort) => { if (bindingContext === undefined) throw new Error('binding not loaded'); bindingContext.set('gatDurableReviewInput', port) },
    disposeBinding: async () => { if (bindingContext === undefined) throw new Error('binding not loaded'); await bindingContext.fiber.dispose() },
    loadSecondBinding: async () => {
      ctx.loader.builtins['task-binding-second'] = executionPlugin({ workspace, dedicatedProvider: true, singleHostWorkspace: true, members: [{ declaration, mode: 'task' }], limits })
      const path = join(root, 'second.yml'); await writeFile(path, '- id: second\n  name: "cordis:task-binding-second"\n')
      await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(path).href } }); await ctx.loader.await()
    } }
}
