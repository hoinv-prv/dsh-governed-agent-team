/** Real reserved DSH integration over exact Team binding ownership and persistence. */
import { mkdtemp, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { SessionId } from '@deepseek-ai/dsh-session'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type { TeamJournal } from '../src/journal.ts'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as Spawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { MockAdapter, textResponse, toolCallResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../src/index.ts'
import type { BinderBindInput, DisposableBinding, TeamMemberBinder, TeamMemberSpec, TeamMessageId } from '../src/index.ts'
import { TestSessionQuery } from './test-session-query.ts'
import { authorizeFixtureAgent, authorizedTask, fixtureMission, humanAction, initializeAuthorizedFixture, recoverFixtureMember } from './authorized-team-fixture.ts'

const signal = new AbortController().signal
const cleanups: Array<() => Promise<void>> = []
afterEach(async () => { for (const cleanup of cleanups.splice(0).reverse()) await cleanup() })

async function stack(storage?: string, script: ConstructorParameters<typeof MockAdapter>[0] = [textResponse('first'), textResponse('second'), textResponse('third')]) {
  const root = storage ?? await mkdtemp(join(tmpdir(), 'gat-production-binding-'))
  if (!storage) cleanups.push(async () => { await rm(root, { recursive: true, force: true }) })
  const ctx = new Context()
  cleanups.push(async () => { await ctx.fiber.dispose() })
  await initializeAuthorizedFixture(ctx)
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(JsonlSessionPersistence, { root })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(SubagentService)
  await ctx.plugin(Spawn, { providerName: 'spawn' })
  await ctx.plugin(TeamService)
  const adapter = new MockAdapter(script)
  ctx.llm.registerAdapter(['mock'], adapter)
  return { ctx, root, adapter }
}

function member(name = 'worker'): TeamMemberSpec {
  return {
    name, description: name, initialTask: [{ type: 'text', text: 'Wait for assigned work.' }],
    context: 'fresh', continuationProvider: 'spawn', agentOptions: { provider: 'mock', model: 'mock' },
    attachments: [{ binderId: 'fixture-memory', protocolVersion: 1, required: true, payload: { marker: name } }],
  }
}

function binder(trace: string[], readPrompt: () => string, effect: () => void = () => {}): TeamMemberBinder {
  const install = async (input: BinderBindInput): Promise<DisposableBinding> => {
    const key = `fixture:${input.memberId}:${input.generation}`
    const remove = input.scope.install({ key, prompt: readPrompt(), tools: [{
      name: 'fixture_memory_read', capability: 'read',
      schema: { type: 'object', properties: { itemId: { type: 'string' } }, required: ['itemId'], additionalProperties: false },
      invoke: async (args: unknown) => {
        if (!args || typeof args !== 'object' || !('itemId' in args) || typeof args.itemId !== 'string') throw new Error('invalid item')
        input.scope.authorize('read'); effect(); return { itemId: args.itemId }
      },
    }] })
    const stopRefresh = input.scope.beforeRequest(async () => {
      trace.push(`refresh:${input.memberName}`)
      input.scope.replacePrompt(key, readPrompt())
    })
    return {
      closeAdmission() { trace.push(`close:${input.memberName}`); stopRefresh(); remove() },
      settle: async () => {}, release: async () => { trace.push(`release:${input.memberName}`) },
    }
  }
  return {
    id: 'fixture-memory', protocolVersion: 1,
    prepare: async input => ({ attachment: input.payload, value: null, abort: async () => { trace.push(`abort:${input.memberName}`) } }),
    bind: async (input) => { trace.push(`bind:${input.memberName}`); return await install(input) },
    recover: async (input) => { trace.push(`recover:${input.memberName}`); return await install(input) },
  }
}

function requestText(adapter: MockAdapter, index: number): string {
  return JSON.stringify(adapter.requests.filter(request => request.model === 'mock')[index]?.messages)
}

describe('production reserved member binding', () => {
  it('installs real tools and refreshes each request after quarantined complete-roster enable', async () => {
    const { ctx, root, adapter } = await stack(undefined, [toolCallResponse('auto-read', 'fixture_memory_read', { itemId: 'first' }), 'hang'])
    const lead = await ctx.agentLoop.create(SessionId('bound-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: root })
    let memory = 'memory-before-first-request'
    let reads = 0
    const trace: string[] = []
    const removeBinder = ctx.agentTeams.registerMemberBinder(binder(trace, () => memory, () => { reads += 1; memory = 'memory-refreshed-before-second-request' }))
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(ctx, lead, 'enable')
    const row = ctx.agentTeams.listMembers(lead).find(value => value.name === 'worker')
    expect(row?.bindings).toEqual([{ binderId: 'fixture-memory', protocolVersion: 1, readiness: 'ready' }])
    expect(adapter.requests).toHaveLength(0)
    const child = ctx.agents.get(row!.id)!
    await expect(ctx.agentTeams.activateMember(child, signal)).rejects.toThrow()
    expect(adapter.requests).toHaveLength(0)
    await authorizeFixtureAgent(ctx, child)
    await ctx.agentTeams.activateMember(child, signal)
    await vi.waitFor(() => { expect(adapter.requests.filter(request => request.model === 'mock')).toHaveLength(2); expect(child.status).toBe('running') })
    expect(requestText(adapter, 0)).toContain('memory-before-first-request')
    expect(requestText(adapter, 1)).toContain('memory-refreshed-before-second-request')
    expect(adapter.requests[0]?.tools?.find(tool => tool.name === 'fixture_memory_read')?.parameters).toEqual({
      type: 'object', properties: { itemId: { type: 'string' } }, required: ['itemId'], additionalProperties: false,
    })
    const result = await child.ctx.tools.execute({ agent: child, callId: ToolCallId('read'), name: 'fixture_memory_read', arguments: { itemId: 'first' }, signal })
    expect(result, JSON.stringify(result)).toMatchObject({ isError: false })
    expect(reads).toBe(2)
    expect(trace.filter(value => value === 'refresh:worker')).toHaveLength(2)
    expect(trace.filter(value => value === 'bind:worker')).toHaveLength(1)
    await expect(removeBinder()).rejects.toMatchObject({ code: 'TEAM_BINDER_REFERENCED' })
  })

  it('prepares all required binders before rows and aborts a successful prefix after later prepare failure', async () => {
    const { ctx, root, adapter } = await stack()
    const lead = await ctx.agentLoop.create(SessionId('prepare-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: root })
    const trace: string[] = []
    const base = binder(trace, () => 'context')
    ctx.agentTeams.registerMemberBinder({ ...base, prepare: async (input) => {
      expect(ctx.agentTeams.listMembers(lead)).toHaveLength(1)
      trace.push(`prepare:${input.memberName}`)
      if (input.memberName === 'second') throw new Error('second prepare failed')
      return await base.prepare(input, signal)
    } })
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member('first'), member('second')] }))
    await expect(humanAction(ctx, lead, 'enable')).rejects.toThrow()
    expect(ctx.agentTeams.listMembers(lead)).toHaveLength(1)
    expect(ctx.agents.list()).toEqual([lead])
    expect(trace).toEqual(['prepare:first', 'prepare:second', 'abort:first'])
    expect(adapter.requests).toHaveLength(0)
  })

  it('recovers once per fresh generation and preserves durable initial identity', async () => {
    const { ctx, root, adapter } = await stack(undefined, ['hang'])
    const lead = await ctx.agentLoop.create(SessionId('recover-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: root })
    const trace: string[] = []
    ctx.agentTeams.registerMemberBinder(binder(trace, () => 'recovered-context'))
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(ctx, lead, 'enable')
    const id = ctx.agentTeams.listMembers(lead).find(value => value.name === 'worker')!.id
    await ctx.subagents.drainContinuableChildren(lead, [id])
    const recovered = await recoverFixtureMember(ctx, lead, 'worker')
    await vi.waitFor(() => { expect(adapter.requests.filter(request => request.model === 'mock')).toHaveLength(1); expect(recovered.status).toBe('running') })
    expect(trace.filter(value => value === 'recover:worker')).toHaveLength(1)
    expect(ctx.agentTeams.listMembers(lead).find(value => value.id === id)?.bindings?.[0]?.readiness).toBe('ready')
    const stored = await ctx.sessionPersistence.open(id, 'read')
    try {
      const events = (await stored.read()).events
      expect(events.filter(event => event.type === 'subagent/initial-admission' && event.data.kind === 'persisted')).toHaveLength(1)
    } finally { await stored.close() }
    const same = await recoverFixtureMember(ctx, lead, 'worker')
    expect(same).toBe(recovered)
    expect(trace.filter(value => value === 'recover:worker')).toHaveLength(1)
  })

  for (const flushMode of ['false', 'unpersisted-true'] as const) it(`denies consumed-initial release after ${flushMode} target flush and retries exactly once`, async () => {
    const { ctx, root, adapter } = await stack(undefined, [textResponse('Initial work complete'), 'hang'])
    ctx.llm.registerAdapter(['lead-notices'], new MockAdapter(Array.from({ length: 8 }, () => textResponse('notice received'))))
    const lead = await ctx.agentLoop.create(SessionId(`consumed-${flushMode}`), { provider: 'lead-notices', model: 'lead-mock' }, { cwd: root })
    const trace: string[] = []
    ctx.agentTeams.registerMemberBinder(binder(trace, () => 'exact recovered memory'))
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(ctx, lead, 'enable')
    const id = ctx.agentTeams.listMembers(lead).find(value => value.name === 'worker')!.id
    const initialChild = ctx.agents.get(id)!
    await authorizeFixtureAgent(ctx, initialChild)
    await ctx.agentTeams.activateMember(initialChild, signal)
    await vi.waitFor(() => { expect(adapter.requests).toHaveLength(1); expect(ctx.agents.get(id)).toBeUndefined() })
    await authorizeFixtureAgent(ctx, lead)
    const queued = await ctx.agentTeams.sendMessage(lead, { target: 'worker', content: [{ type: 'text', text: 'Recovered followup only' }], signal })
    expect(queued.status).toBe('queued')
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const replacement = vi.spyOn(ctx.sessions, 'flush').mockImplementation(async session => session.id === id ? flushMode !== 'false' : await flush(session))
    await expect(recoverFixtureMember(ctx, lead, 'worker')).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    const recovered = ctx.agents.get(id)!
    expect(recovered).toBeDefined()
    expect(adapter.requests).toHaveLength(1)
    expect(lead.session.snapshotEvents().filter(event => event.type === 'team/message/delivered' && event.data.messageId === queued.messageId)).toHaveLength(0)
    replacement.mockRestore()
    await ctx.agentTeams.activateMember(recovered, signal)
    await vi.waitFor(() => { expect(adapter.requests).toHaveLength(2); expect(recovered.status).toBe('running') })
    expect(requestText(adapter, 1)).toContain('Recovered followup only')
    expect(trace.filter(value => value === 'recover:worker')).toHaveLength(1)
    expect(lead.session.snapshotEvents().filter(event => event.type === 'team/message/delivered' && event.data.messageId === queued.messageId)).toHaveLength(1)
    const stored = await ctx.sessionPersistence.open(id, 'read')
    try {
      const events = (await stored.read()).events
      expect(events.filter(event => event.type === 'subagent/initial-admission' && event.data.kind === 'persisted')).toHaveLength(1)
      expect(events.filter(event => event.type === 'user/message' && event.data.source.kind === 'team-message' && event.data.source.messageId === queued.messageId)).toHaveLength(1)
    } finally { await stored.close() }
  })

  it('revalidates staged acknowledgement after a preceding serialized canonical task edit', async () => {
    const { ctx, root, adapter } = await stack(undefined, [textResponse('Initial complete'), 'hang'])
    ctx.llm.registerAdapter(['lead-notices'], new MockAdapter(Array.from({ length: 8 }, () => textResponse('notice received'))))
    const lead = await ctx.agentLoop.create(SessionId('ack-boundary-lead'), { provider: 'lead-notices', model: 'lead-mock' }, { cwd: root })
    ctx.agentTeams.registerMemberBinder(binder([], () => 'required recovery material'))
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(ctx, lead, 'enable')
    const id = ctx.agentTeams.listMembers(lead).find(value => value.name === 'worker')!.id
    const initial = ctx.agents.get(id)!
    await authorizeFixtureAgent(ctx, initial)
    await ctx.agentTeams.activateMember(initial, signal)
    await vi.waitFor(() => { expect(adapter.requests).toHaveLength(1); expect(ctx.agents.get(id)).toBeUndefined() })
    await authorizeFixtureAgent(ctx, lead)
    const mission = await fixtureMission(ctx, lead)
    const queued = await ctx.agentTeams.sendMessage(lead, { target: 'worker', content: [{ type: 'text', text: 'Staged until exact ack authorization' }], signal })
    // Observe the actual private journal queue without replacing its serialization or authority checks.
    const internal = ctx.agentTeams as unknown as {
      journal: TeamJournal
      mailbox: {
        markDelivered(root: Agent, messageId: TeamMessageId, targetId: SessionId, assertTarget?: () => void): Promise<void>
      }
    }
    const ackEntered = Promise.withResolvers<ReturnType<() => void>>()
    const allowAckQueue = Promise.withResolvers<ReturnType<() => void>>()
    const queueEntered = Promise.withResolvers<ReturnType<() => void>>()
    const releaseQueue = Promise.withResolvers<ReturnType<() => void>>()
    const ack = internal.mailbox.markDelivered.bind(internal.mailbox)
    vi.spyOn(internal.mailbox, 'markDelivered').mockImplementation(async (...args) => {
      if (args[1] === queued.messageId) { ackEntered.resolve(); await allowAckQueue.promise }
      await ack(...args)
    })
    const recovery = recoverFixtureMember(ctx, lead, 'worker')
    void recovery.catch(() => undefined)
    await ackEntered.promise
    const blocker = internal.journal.transact(lead.id, async () => { queueEntered.resolve(); await releaseQueue.promise })
    await queueEntered.promise
    const queueCalls = vi.spyOn(internal.journal, 'transact')
    const edit = ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'Invalidate queued target lease', description: 'Commit before the delivered edge.' })
    await vi.waitFor(() => { expect(queueCalls).toHaveBeenCalledTimes(1) })
    allowAckQueue.resolve()
    await vi.waitFor(() => { expect(queueCalls).toHaveBeenCalledTimes(2) })
    expect(lead.session.snapshotEvents().filter(event => event.type === 'team/message/delivered' && event.data.messageId === queued.messageId)).toHaveLength(0)
    releaseQueue.resolve()
    await blocker
    await edit
    await expect(recovery).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    expect(adapter.requests).toHaveLength(1)
    const recovered = ctx.agents.get(id)!
    expect(recovered).toBeDefined()
    expect(() => { ctx.agentTeams.assertExecution(recovered) }).toThrow()
    expect(lead.session.snapshotEvents().filter(event => event.type === 'team/message/delivered' && event.data.messageId === queued.messageId)).toHaveLength(0)
    const stored = await ctx.sessionPersistence.open(id, 'read')
    try {
      const events = (await stored.read()).events
      expect(events.filter(event => event.type === 'agent/inbox/spliced').flatMap(event => event.data.inserted)
        .filter(message => message.source.kind === 'team-message' && message.source.messageId === queued.messageId)).toHaveLength(1)
    } finally { await stored.close() }
    await authorizeFixtureAgent(ctx, recovered)
    await ctx.agentTeams.activateMember(recovered, signal)
    await vi.waitFor(() => { expect(adapter.requests).toHaveLength(2) })
    expect(lead.session.snapshotEvents().filter(event => event.type === 'team/message/delivered' && event.data.messageId === queued.messageId)).toHaveLength(1)
  })

  it('invalidates required scope after a blocked read loses authority and denies same-Agent reauthorization', async () => {
    const { ctx, root, adapter } = await stack(undefined, ['hang'])
    const lead = await ctx.agentLoop.create(SessionId('withdrawal-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: root })
    let unblock!: () => void
    let enter!: () => void
    const blocked = new Promise<ReturnType<() => void>>((resolve) => { unblock = resolve })
    const entered = new Promise<ReturnType<() => void>>((resolve) => { enter = resolve })
    const base = binder([], () => 'required material')
    ctx.agentTeams.registerMemberBinder({ ...base, bind: async (input) => {
      const remove = input.scope.install({ key: 'blocked-owner', prompt: 'required material', tools: [{ name: 'blocked_read', capability: 'read', schema: {}, invoke: async () => {
        input.scope.authorize('read'); enter(); await blocked
        try { input.scope.authorize('read') } catch (error) { remove(); throw error }
        return 'must remain withheld'
      } }] })
      const refresh = input.scope.beforeRequest(async () => { input.scope.replacePrompt('blocked-owner', 'fresh required material') })
      return { closeAdmission() { refresh(); remove() }, settle: async () => {}, release: async () => {} }
    } })
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(ctx, lead, 'enable')
    const child = ctx.agents.get(ctx.agentTeams.listMembers(lead).find(value => value.name === 'worker')!.id)!
    await authorizeFixtureAgent(ctx, child)
    const read = child.ctx.tools.execute({ agent: child, callId: ToolCallId('blocked'), name: 'blocked_read', arguments: {}, signal })
    await entered
    await authorizedTask(ctx, lead, { subject: 'Change exact mission structure', description: 'Invalidate the earlier child lease.' })
    unblock()
    expect(await read).toMatchObject({ isError: true })
    expect(ctx.agents.get(child.id)).toBe(child)
    expect(ctx.agentTeams.listMembers(lead).find(value => value.id === child.id)?.bindings?.[0]?.readiness).toBe('unavailable')
    await expect(authorizeFixtureAgent(ctx, child)).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    await expect(ctx.agentTeams.activateMember(child, signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    expect(adapter.requests).toHaveLength(0)
  })

  it('retains inactive persisted references and denies recovery with an absent required binder', async () => {
    const first = await stack()
    const lead = await first.ctx.agentLoop.create(SessionId('restart-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: first.root })
    first.ctx.agentTeams.registerMemberBinder(binder([], () => 'first-context'))
    first.ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(first.ctx, lead, 'enable')
    await first.ctx.fiber.dispose()
    const second = await stack(first.root)
    const resumed = await second.ctx.agents.resume({ resumeSessionId: lead.id, agentOptions: { provider: 'mock', model: 'mock' } })
    await authorizeFixtureAgent(second.ctx, resumed.agent)
    await expect(recoverFixtureMember(second.ctx, resumed.agent, 'worker')).rejects.toMatchObject({ code: 'TEAM_BINDER_UNAVAILABLE' })
    expect(second.adapter.requests).toHaveLength(0)
    expect(second.ctx.agents.list()).toEqual([resumed.agent])
    const remove = second.ctx.agentTeams.registerMemberBinder(binder([], () => 'later-context'))
    await expect(remove()).rejects.toMatchObject({ code: 'TEAM_BINDER_REFERENCED' })
  })

  it('blocks provider admission when an installed request refresh fails', async () => {
    const { ctx, root, adapter } = await stack(undefined, ['hang'])
    const lead = await ctx.agentLoop.create(SessionId('refresh-failure-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: root })
    const base = binder([], () => 'initial-context')
    let refreshed = false
    ctx.agentTeams.registerMemberBinder({ ...base, bind: async (input) => {
      const installed = await base.bind(input, null, null, signal)
      const remove = input.scope.beforeRequest(async () => { refreshed = true; throw new Error('refresh unavailable') })
      return { ...installed, closeAdmission() { remove(); installed.closeAdmission() } }
    } })
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await humanAction(ctx, lead, 'enable')
    const child = ctx.agents.get(ctx.agentTeams.listMembers(lead).find(value => value.name === 'worker')!.id)!
    await authorizeFixtureAgent(ctx, child)
    await ctx.agentTeams.activateMember(child, signal)
    await vi.waitFor(() => { expect(refreshed).toBe(true) })
    expect(adapter.requests).toHaveLength(0)
  })

  it('persists a safe failed edge with unchanged attachments after required bind failure', async () => {
    const { ctx, root, adapter } = await stack()
    const lead = await ctx.agentLoop.create(SessionId('bind-failure-lead'), { provider: 'mock', model: 'lead-mock' }, { cwd: root })
    const trace: string[] = []
    const base = binder(trace, () => 'context')
    ctx.agentTeams.registerMemberBinder({ ...base, bind: async () => { throw new Error('private provider detail') } })
    ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [member()] }))
    await expect(humanAction(ctx, lead, 'enable')).rejects.toThrow()
    expect(ctx.agentTeams.listMembers(lead)[1]).toMatchObject({ status: 'failed', diagnostics: ['required member binding failed'] })
    expect(adapter.requests).toHaveLength(0)
    expect(trace).toEqual(['abort:worker'])
    const persisted = await ctx.sessionPersistence.open(lead.id, 'read')
    try {
      const events = (await persisted.read()).events.filter(event => event.type === 'team/member')
      expect(events.map(event => event.data.member.phase)).toEqual(['provisioning', 'failed'])
      const records = events.map((event) => {
        if (event.data.version !== 3) throw new Error('required attachments must retain v3 member events')
        return event.data.member.attachments
      })
      expect(records[0]).toEqual(records[1])
    } finally { await persisted.close() }
  })

})
