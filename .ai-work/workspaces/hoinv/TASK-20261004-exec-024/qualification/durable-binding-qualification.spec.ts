/** AIP-EXEC-024 qualification, prospective design DETAIL_DESIGN §9. */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context, symbols } from '@deepseek-ai/cordis'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import Include from '@deepseek-ai/cordis-plugin-include'
import { brandString } from '@deepseek-ai/dsh-brand'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as Spawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { LlmError } from '@deepseek-ai/dsh-llm'
import type { GenerateOptions } from '@deepseek-ai/dsh-llm'
import { DurableAgentConsumer, DurableAgentService, LocalDurableAgentProvider } from '@deepseek-ai/dsh-durable-agent'
import type { DurableAgentRef } from '@deepseek-ai/dsh-durable-agent'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../src/index.ts'
import { TestSessionQuery } from './test-session-query.ts'

const cleanups: (() => Promise<void>)[] = []
afterEach(async () => { for (const close of cleanups.splice(0).reverse()) await close() })
const signal = new AbortController().signal
const declaration = Object.freeze({ name: 'worker', description: 'qualification worker', prompt: 'role only',
  context: 'fresh' as const, provider: 'mock', model: 'mock', scope: 'workspace' as const })
const brief = {
  objective: 'qualify request freshness', deliverables: ['observed request'], acceptanceCriteria: ['fresh context'],
  allowedPaths: [], excludedWork: [], context: '', inputs: [{ reference: 'durable-memory:selected' }],
  checks: [], stopConditions: [], returnFormat: 'summary',
}
function requestText(request: GenerateOptions): string {
  return request.messages.flatMap(message => message.content)
    .filter(block => block.type === 'text').map(block => block.text).join('\n')
}
function publicProvider(ctx: Context): DurableAgentService {
  const registered = ctx.get('durableAgent')
  if (registered === undefined) throw new Error('Loader did not publish public WK service')
  const provider: unknown = Reflect.get(registered, symbols.original) ?? registered
  if (!(provider instanceof DurableAgentService)) throw new Error('registered service is not the WK public service')
  return provider
}
async function commit(service: DurableAgentService, ref: DurableAgentRef, title: string) {
  return await service.commitMemoryItem(ref, {
    item: { id: 'selected', title, retrievalCondition: 'explicit assignment selection', content: 'disposable test memory' },
    authorization: { kind: 'authorized-host-workflow', authorizationRef: 'exec024-disposable-fixture' },
  })
}

async function witness() {
  const root = await mkdtemp(join(tmpdir(), 'gat-exec024-provider-'))
  const workspace = join(root, 'workspace')
  await mkdir(workspace)
  const ctx = new Context()
  cleanups.push(async () => { try { await ctx.fiber.dispose() } finally { await rm(root, { recursive: true, force: true }) } })
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(JsonlSessionPersistence, { root: join(root, 'sessions') })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(SubagentService)
  await ctx.plugin(Spawn, { providerName: 'spawn' })
  await ctx.plugin(Loader)
  ctx.loader.builtins.include = Include
  ctx.loader.builtins['qualification-gat'] = TeamService
  ctx.loader.builtins['qualification-wk'] = LocalDurableAgentProvider
  const bindings = new Map<string, { ref: DurableAgentRef; consumer: DurableAgentConsumer }>()
  const assemblies: string[] = []
  let creationPhase: string | undefined
  const bindingPlugin = {
    name: 'qualification-execution-binding', inject: ['agentTeams', 'durableAgent'],
    apply(bindingContext: Context) {
      bindingContext.on('agent/created', async ({ agent }) => {
        const execution = bindingContext.agentTeams.executionFor(agent)
        if (execution === undefined) return
        creationPhase = execution.phase
        const service = publicProvider(bindingContext)
        const ref = await service.provision(workspace, declaration)
        const consumer = new DurableAgentConsumer(service, ref)
        bindings.set(agent.id, { ref, consumer })
        agent.ctx.on('system-prompt/assemble', async (_assembly, _context, next) => {
          const assembly = await next()
          const current = bindingContext.agentTeams.executionFor(agent)
          if (current?.id !== execution.id || current.generation !== execution.generation || current.phase !== 'active')
            throw new Error('execution is not active at context read')
          const contribution = await consumer.modelContribution()
          const after = bindingContext.agentTeams.executionFor(agent)
          if (after?.id !== current.id || after.generation !== current.generation || after.phase !== 'active')
            throw new Error('execution changed during context read')
          assemblies.push(contribution.prompt)
          return { ...assembly, sections: [...assembly.sections,
            { name: 'qualification-durable', text: `<<<WK>>>${contribution.prompt}<<<END>>>`, interpolate: false }] }
        })
      })
      bindingContext.on('subagent/closing-child', async agent => {
        const binding = bindings.get(agent.id)
        if (binding !== undefined) {
          await publicProvider(bindingContext).release(binding.ref)
          bindings.delete(agent.id)
        }
      })
    },
  }
  ctx.loader.builtins['qualification-binding'] = bindingPlugin
  const yaml = join(root, 'cordis.yml')
  await writeFile(yaml, '- id: gat\n  name: "cordis:qualification-gat"\n- id: wk\n  name: "cordis:qualification-wk"\n- id: binding\n  name: "cordis:qualification-binding"\n')
  await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(yaml).href } })
  await ctx.loader.await()
  const service = publicProvider(ctx)
  expect(service.apiVersion).toBe(1)
  const seed = await service.provision(workspace, declaration)
  await commit(service, seed, 'catalog-version-one')
  await service.release(seed)
  const attempts = new Map<string, number>()
  class QualificationModel extends MockAdapter {
    override async *stream(request: GenerateOptions) {
      const id = request.sessionId
      if (id !== undefined && bindings.has(id) && (attempts.get(id) ?? 0) >= 1) {
        this.requests.push(request)
        yield { type: 'block-start' as const, index: 0, blockType: 'text' as const }
        await new Promise<void>((_resolve, reject) => {
          if (request.signal?.aborted) { reject(new Error('aborted')); return }
          request.signal?.addEventListener('abort', () => reject(new Error('aborted')), { once: true })
        })
        return
      }
      yield* super.stream(request)
    }
  }
  const adapter = new QualificationModel(Array.from({ length: 12 }, () => (request: GenerateOptions) => {
    const id = request.sessionId
    if (id === undefined || !bindings.has(id)) return textResponse('bootstrap or lead done')
    const attempt = (attempts.get(id) ?? 0) + 1
    attempts.set(id, attempt)
    if (attempt === 1) throw new LlmError('busy', 'RATE_LIMIT')
    return textResponse('execution retry done')
  }))
  ctx.llm.registerAdapter(['mock'], adapter)
  ctx.on('agent/request-error', async ({ agent }, next) => {
    const binding = bindings.get(agent.id)
    if (binding === undefined) return await next()
    await commit(service, binding.ref, 'catalog-version-two')
    return { kind: 'retry' }
  })
  const lead = await ctx.agentLoop.create(SessionId('qualification-lead'), { provider: 'mock', model: 'mock' })
  const { member } = await ctx.agentTeams.spawnTeammate(lead, {
    name: 'worker', description: 'qualification worker', provider: 'spawn', context: 'fresh',
    prompt: [{ type: 'text', text: 'bootstrap' }], signal,
  })
  await vi.waitFor(() => expect(ctx.agents.get(member.id)).toBeUndefined())
  expect(bindings.size).toBe(0)
  const task = await ctx.agentTeams.createTask(lead, { subject: 'qualify', description: 'retry freshness' })
  const execution = await ctx.agentTeams.assignTask(lead, {
    requestId: brandString('qualification-request'), member: member.name, taskId: task.id,
    expectedRevision: task.revision, brief, signal,
  })
  await vi.waitFor(() => expect(adapter.requests.filter(request => request.sessionId === execution.sessionId)).toHaveLength(2))
  const worker = ctx.agents.get(execution.sessionId)
  if (worker === undefined) throw new Error('execution Agent unavailable')
  const binding = bindings.get(worker.id)
  if (binding === undefined) throw new Error('execution binding missing')
  const latest = await binding.consumer.modelContribution()
  const systemEvents = worker.session.snapshotEvents().filter(event => event.type === 'system/message')
  const requests = adapter.requests.filter(request => request.sessionId === execution.sessionId)
  const result = {
    creationPhase, assemblyCount: assemblies.length, executionRequestCount: requests.length,
    firstPrompt: requestText(requests[0]!), retryPrompt: requestText(requests[1]!),
    assembledContribution: assemblies[0], latestContribution: latest.prompt,
    loggedSystemEvents: JSON.stringify(systemEvents),
    phase: ctx.agentTeams.getExecution(lead, execution.id).phase,
  }
  await ctx.agentTeams.cancelExecution(lead, execution.id)
  expect(ctx.agentTeams.getExecution(lead, execution.id).phase).toBe('cancelled')
  await expect(binding.consumer.snapshot()).rejects.toMatchObject({ code: 'UNAUTHORIZED_REFERENCE' })
  const stored = await ctx.sessionPersistence.open(execution.sessionId, 'read')
  let persistedSystemEvents: string
  try {
    persistedSystemEvents = JSON.stringify((await stored.read(0)).events.filter(event => event.type === 'system/message'))
  } finally { await stored.close() }
  expect(persistedSystemEvents).toContain('catalog-version-one')
  expect(persistedSystemEvents).not.toContain('catalog-version-two')
  // Actual observed bytes and persisted Session events, not a file-exists receipt.
  await writeFile(join(import.meta.dirname, '../../../..', '.qualification-observation.json'),
    JSON.stringify({ ...result, persistedSystemEvents, terminalPhase: 'cancelled' }, null, 2) + '\n')
  return result
}

describe('AIP-EXEC-024 real GAT / WK retry qualification', () => {
  it('characterizes first-request binding, changed WK revision, logged prompt and current retry reuse', async () => {
    const seen = await witness()
    expect(seen.creationPhase).toBe('provisioning')
    expect(seen.phase).toBe('active')
    expect(seen.executionRequestCount).toBe(2)
    expect(seen.assemblyCount).toBe(1)
    expect(seen.firstPrompt).toContain('catalog-version-one')
    expect(seen.retryPrompt).toContain('catalog-version-one')
    expect(seen.retryPrompt).not.toContain('catalog-version-two')
    expect(seen.latestContribution).toContain('catalog-version-two')
    expect(seen.latestContribution).not.toBe(seen.assembledContribution)
    expect(seen.loggedSystemEvents).toContain('catalog-version-one')
    expect(seen.loggedSystemEvents).not.toContain('catalog-version-two')
    expect(seen.firstPrompt.split('<<<WK>>>')).toHaveLength(2)
    expect(seen.retryPrompt.split('<<<WK>>>')).toHaveLength(2)
  })
  it('requires the new public WK contribution in the actual retry (contract gate)', async () => {
    const seen = await witness()
    expect(seen.retryPrompt, 'OP-024-03: stale retry is an adapter feasibility failure').toContain('catalog-version-two')
  })
})
