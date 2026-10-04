/** Loader-composed WK provider, bound children and persisted recovery. */
import { mkdtemp, readFile, realpath, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context, symbols } from '@deepseek-ai/cordis'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import Include from '@deepseek-ai/cordis-plugin-include'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { loadOptionalPatches } from '@deepseek-ai/dsh-app-boot'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import Subagents from '@deepseek-ai/dsh-subagent'
import * as Spawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import * as Fork from '@deepseek-ai/dsh-subagent-fork-in-process'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type { DurableAgentService, DurableAgentRef } from '@deepseek-ai/dsh-durable-agent/service'
import TeamService from '@vuhoi/gat-core'
import { MockAdapter, toolCallResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import { TestSessionQuery } from '../../gat-core/tests/test-session-query.ts'
import { mountHumanControl } from '../../gat-core/tests/human-control-fixture.ts'
import * as TeamTools from '../../gat-tools/src/index.ts'
import * as DurableComposition from '../src/composition.ts'
import * as DurableProvider from '../src/provider.ts'

const signal = new AbortController().signal
const cleanups: Array<() => Promise<void>> = []
afterEach(async () => {
  for (const cleanup of cleanups.splice(0).reverse()) await cleanup()
})

const declaration = { name: 'worker', description: 'Controlled worker', prompt: 'Use the assigned task',
  context: 'fresh' as const, provider: 'mock', model: 'mock', scope: 'workspace' as const }

async function boot(workspace: string, storage: string, script: ConstructorParameters<typeof MockAdapter>[0] = ['hang']) {
  const ctx = new Context()
  const control = await mountHumanControl(ctx)
  let closed = false
  const close = async () => {
    if (closed) return
    closed = true
    try { await ctx.fiber.dispose() } finally { await control.close() }
  }
  cleanups.push(close)
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(JsonlSessionPersistence, { root: storage })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(Subagents)
  await ctx.plugin(Spawn, { providerName: 'spawn' })
  await ctx.plugin(Fork, { providerName: 'fork' })
  for (const name of ['ask_user_question', 'glob', 'grep', 'read', 'read_image']) {
    ctx.tools.register({ name, description: 'Host baseline inspection fixture', capabilities: ['team-inspection'],
      parameters: { type: 'object', properties: {} },
      execute: async () => ({ fixture: name }), output: { schema: {}, render: () => [] } })
  }
  await ctx.plugin(Loader)
  ctx.loader.builtins.include = Include
  const modules = new Map<string, unknown>([
    ['@vuhoi/gat-core', TeamService],
    ['@vuhoi/gat-tools', TeamTools],
    ['@vuhoi/gat-durable-agent/provider', DurableProvider],
    ['@vuhoi/gat-durable-agent/composition', DurableComposition],
  ])
  ctx.loader.internal = {
    version: 'v2',
    import(specifier: string) {
      if (!modules.has(specifier)) return Promise.reject(new Error(`unexpected Loader import ${specifier}`))
      return Promise.resolve(modules.get(specifier))
    },
  } as unknown as NonNullable<typeof ctx.loader.internal>
  const configPath = join(storage, 'cordis.yml')
  const profile = await readFile(resolve(import.meta.dirname, '../../gat-durable-profile/cordis.patch.yml'), 'utf8')
  // The host base owns GAT core. The checked-in Durable patch owns selection and registration.
  await writeFile(configPath, '- id: agent-team\n  name: "@vuhoi/gat-core"\n- id: tool-agent-team\n  name: "@vuhoi/gat-tools"\n')
  const patchPath = join(storage, 'durable.patch.yml')
  await writeFile(patchPath, profile)
  await ctx.loader.create({ name: 'cordis:include', config: {
    path: pathToFileURL(configPath).href, patches: loadOptionalPatches('durable-composition', patchPath),
  } })
  await ctx.loader.await()
  const adapter = new MockAdapter(script)
  ctx.llm.registerAdapter(['mock'], adapter)
  const refs: DurableAgentRef[] = []
  const registered = ctx.get('durableAgent')
  const service = registered ? (Reflect.get(registered, symbols.original) ?? registered) as DurableAgentService : undefined
  if (!service) throw new Error('Durable profile provider is unavailable')
  const provision = service.provision.bind(service)
  vi.spyOn(service, 'provision').mockImplementation(async (...args) => {
    const ref = await provision(...args)
    refs.push(ref)
    return ref
  })
  return { ctx, control, adapter, refs, workspace, close, service }
}

async function fixture(script: ConstructorParameters<typeof MockAdapter>[0] = ['hang']) {
  const root = await mkdtemp(join(tmpdir(), 'gat-durable-composition-'))
  cleanups.push(async () => { await rm(root, { recursive: true, force: true }) })
  const workspace = await realpath(root)
  const storage = await mkdtemp(join(tmpdir(), 'gat-durable-sessions-'))
  cleanups.push(async () => { await rm(storage, { recursive: true, force: true }) })
  await writeFile(join(workspace, 'team_members.durable.yaml'), JSON.stringify({ version: 1,
    members: [declaration, { ...declaration, name: 'reviewer' }].map(({ scope, ...member }) => ({ ...member, durable: { scope } })),
  }))
  const h = await boot(workspace, storage, script)
  const lead = await h.ctx.agentLoop.create(SessionId('durable-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: workspace })
  return { ...h, lead, storage }
}

async function enable(h: Awaited<ReturnType<typeof fixture>>) {
  const result = await h.control.call('enable', h.lead.id)
  expect(result, JSON.stringify(result)).toMatchObject({ ok: true, value: { enabled: true } })
  const worker = h.ctx.agentTeams.remoteView(h.lead).members.find(member => member.name === 'worker')!
  const child = h.ctx.agents.get(worker.id)!
  expect(worker.bindings).toEqual([{ binderId: 'durable-agent', protocolVersion: 1, readiness: 'ready' }])
  expect(h.adapter.requests).toHaveLength(0)
  return child
}

async function authorize(h: Awaited<ReturnType<typeof fixture>>, child: Agent) {
  const mission = await h.ctx.agentTeams.createMission(h.lead, { title: 'selected mission', objective: 'controlled work' })
  const task = await h.ctx.agentTeams.createTask(h.lead, { missionId: mission.id, subject: 'work', description: 'exact canonical task' })
  const current = h.ctx.agentTeams.getMission(h.lead, mission.id)
  expect(await h.control.call('approveMission', h.lead.id, { missionId: current.id, expectedRevision: current.revision }))
    .toMatchObject({ ok: true, value: { ok: true } })
  await h.ctx.agentTeams.updateTask(child, { taskId: task.id, expectedRevision: task.revision, action: 'claim' })
  h.ctx.agentTeams.bindExecution(h.lead, { missionId: current.id, expectedRevision: current.revision })
  h.ctx.agentTeams.bindExecution(child, { missionId: current.id, expectedRevision: current.revision, taskId: task.id })
  return { mission: current, task }
}

function execute(h: Awaited<ReturnType<typeof boot>>, child: Agent, name: string, args: unknown) {
  return h.ctx.tools.execute({ agent: child, name, arguments: args, callId: ToolCallId(name), signal })
}

describe('registered Durable profile composition', () => {
  it('binds real storage before first admission, refreshes each request and keeps candidate submission unconfirmed', async () => {
    const h = await fixture([toolCallResponse('refresh-read', 'durable_agent_read_memory', { itemId: 'rule' }), 'hang'])
    const child = await enable(h)
    await expect(h.ctx.agentTeams.activateMember(child, signal)).rejects.toMatchObject({ code: 'TEAM_EXECUTION_DENIED' })
    await authorize(h, child)
    const ref = h.refs[0]!
    await h.service.commitMemoryItem(ref, { item: { id: 'rule', title: 'First rule', retrievalCondition: 'When working', content: 'preserve evidence' },
      authorization: { kind: 'human', authorizationRef: 'fixture-approved-commit' } })
    const readMemoryItem = h.service.readMemoryItem.bind(h.service)
    vi.spyOn(h.service, 'readMemoryItem').mockImplementationOnce(async (...args) => {
      const result = await readMemoryItem(...args)
      await h.service.commitMemoryItem(ref, { item: { id: 'later', title: 'Later rule', retrievalCondition: 'On followup', content: 'new evidence' },
        authorization: { kind: 'human', authorizationRef: 'fixture-later-commit' } })
      return result
    })
    await h.ctx.agentTeams.activateMember(child, signal)
    await vi.waitFor(() => { expect(h.adapter.requests).toHaveLength(2); expect(child.status).toBe('running') })
    expect(JSON.stringify(h.adapter.requests[0]!.messages)).toContain('First rule')
    const schemas = h.adapter.requests[0]!.tools ?? []
    expect(JSON.stringify(schemas)).toContain('durable_agent_read_memory')
    expect(JSON.stringify(schemas)).toContain('itemId')
    const read = await execute(h, child, 'durable_agent_read_memory', { itemId: 'rule' })
    expect(read.isError, JSON.stringify(read)).not.toBe(true)
    expect(JSON.stringify(read)).toContain('preserve evidence')
    const candidate = await execute(h, child, 'durable_agent_submit_candidate', {
      title: 'Possible rule', retrievalCondition: 'During review', content: 'candidate only', provenance: 'fixture', confidence: 'medium', limitations: [],
    })
    expect(candidate.isError, JSON.stringify(candidate)).not.toBe(true)
    expect(JSON.stringify(candidate)).toContain('unconfirmed')
    expect(JSON.stringify(h.adapter.requests[1]!.messages)).toContain('Later rule')
    const safe = JSON.stringify(h.ctx.agentTeams.remoteView(h.lead))
    expect(safe).not.toContain('serviceBindingKey')
    expect(safe).not.toContain(ref)
    expect(await h.control.call('revokeMission', h.lead.id, { missionId: h.ctx.agentTeams.listMissions(h.lead)[0]!.id,
      expectedRevision: h.ctx.agentTeams.listMissions(h.lead)[0]!.revision })).toMatchObject({ ok: true })
    expect((await execute(h, child, 'durable_agent_read_memory', { itemId: 'rule' })).isError).toBe(true)
  })

  it('recovers persisted attachments after restart without rereading changed YAML or readmitting initial work', async () => {
    const h = await fixture()
    const child = await enable(h)
    const { mission, task } = await authorize(h, child)
    await h.service.commitMemoryItem(h.refs[0]!, { item: { id: 'kept', title: 'Kept rule', retrievalCondition: 'After restart', content: 'persistent content' },
      authorization: { kind: 'human', authorizationRef: 'fixture-recovery-commit' } })
    await h.ctx.agentTeams.activateMember(child, signal)
    await vi.waitFor(() => { expect(h.adapter.requests).toHaveLength(1); expect(child.status).toBe('running') })
    const leadId = h.lead.id
    const childId = child.id
    await h.close()
    await writeFile(join(h.workspace, 'team_members.durable.yaml'), 'invalid: changed after enable\n')
    const second = await boot(h.workspace, h.storage)
    const handle = await second.ctx.agents.resume({ resumeSessionId: leadId, agentOptions: { provider: 'mock', model: 'lead-mock' } })
    const lead = handle.agent
    second.ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: mission.revision })
    await second.ctx.agentTeams.sendMessage(lead, { target: 'worker', content: [{ type: 'text', text: 'Recovery followup only' }], signal })
    const recovered = await second.ctx.agentTeams.recoverMember(lead, 'worker', {
      missionId: mission.id, expectedRevision: mission.revision, taskId: task.id,
    }, signal)
    expect(recovered.id).toBe(childId)
    await vi.waitFor(() => { expect(second.adapter.requests.filter(request => request.model === 'mock')).toHaveLength(1); expect(recovered.status).toBe('running') })
    expect(JSON.stringify(second.adapter.requests.find(request => request.model === 'mock')!.messages)).toContain('Recovery followup only')
    const read = await execute(second, recovered, 'durable_agent_read_memory', { itemId: 'kept' })
    expect(read.isError, JSON.stringify(read)).not.toBe(true)
    expect(JSON.stringify(read)).toContain('persistent content')
    const persisted = await second.ctx.sessionPersistence.open(childId, 'read')
    try {
      const { events } = await persisted.read()
      expect(events.filter(event => event.type === 'subagent/initial-admission' && event.data.kind === 'persisted')).toHaveLength(1)
    } finally { await persisted.close() }
  })
  it('withdraws required readiness after a revoked asynchronous read and denies same-generation admission', async () => {
    const h = await fixture()
    const child = await enable(h)
    const { mission } = await authorize(h, child)
    await h.service.commitMemoryItem(h.refs[0]!, { item: { id: 'rule', title: 'Rule', retrievalCondition: 'During work', content: 'private evidence' },
      authorization: { kind: 'human', authorizationRef: 'fixture-read-revocation' } })
    await h.ctx.agentTeams.activateMember(child, signal)
    await vi.waitFor(() => { expect(h.adapter.requests).toHaveLength(1); expect(child.status).toBe('running') })
    let finish!: () => void
    const blocked = new Promise<void>((resolve) => { finish = resolve })
    let entered = false
    const read = h.service.readMemoryItem.bind(h.service)
    vi.spyOn(h.service, 'readMemoryItem').mockImplementationOnce(async (...args) => {
      entered = true
      await blocked
      return await read(...args)
    })
    const pending = execute(h, child, 'durable_agent_read_memory', { itemId: 'rule' })
    await vi.waitFor(() => { expect(entered).toBe(true) })
    expect(await h.control.call('revokeMission', h.lead.id, { missionId: mission.id, expectedRevision: mission.revision }))
      .toMatchObject({ ok: true })
    finish()
    const result = await pending
    expect(result.isError).toBe(true)
    expect(JSON.stringify(result)).not.toContain('private evidence')
    expect(h.ctx.agentTeams.remoteView(h.lead).members.find(member => member.id === child.id)?.bindings?.[0]?.readiness).toBe('unavailable')
    const current = h.ctx.agentTeams.getMission(h.lead, mission.id)
    expect(await h.control.call('approveMission', h.lead.id, { missionId: current.id, expectedRevision: current.revision }))
      .toMatchObject({ ok: true })
    expect(() => { h.ctx.agentTeams.bindExecution(child, { missionId: current.id, expectedRevision: current.revision }) }).toThrow()
    await expect(h.ctx.agentTeams.activateMember(child, signal)).rejects.toThrow()
    expect(h.adapter.requests).toHaveLength(1)
  })

})
