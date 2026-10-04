import { afterEach, describe, expect, it, vi } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import type { Agent, AgentOptions } from '@deepseek-ai/dsh-agent'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId, createToolResultMessage, createUserMessage } from '@deepseek-ai/dsh-llm'
import { SessionLogOffset, SessionId, type SessionEvent } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as SubagentFork from '@deepseek-ai/dsh-subagent-fork-in-process'
import * as SubagentSpawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService, { TeamError, TeamId, TeamMessageId, TeamTaskId } from '../src/index.ts'
import { TeamRuntimeLifecycle } from '../src/lifecycle.ts'
import { approvedPlanTaskSubjects, parseApprovedPlanTasks } from '../src/approved-plan-import.ts'
import { teamProjectionDefinition } from '../src/projection.ts'
import type { TeamMemberSnapshot, TeamMessageSnapshot, TeamTaskSnapshot } from '../src/index.ts'
import { initializeAuthorizedFixture, authorizeFixtureAgent, authorizedUpdate, recoverFixtureMember, authorizedTask, authorizedSpawn, humanAction, humanBusinessAction, fixtureMission } from './authorized-team-fixture.ts'
import { TestSessionQuery } from './test-session-query.ts'

const SIGNAL = new AbortController().signal
const roots: string[] = []

afterEach(() => {
  vi.useRealTimers()
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

/** Detached durable Team read through the same projection definition as the service. */
function durable(agent: Agent): {
  members: TeamMemberSnapshot[]
  tasks: TeamTaskSnapshot[]
  pendingMessages: TeamMessageSnapshot[]
} {
  let projected = teamProjectionDefinition.init(agent.session.header)
  for (const event of agent.session.snapshotEvents()) projected = teamProjectionDefinition.apply(projected, event)
  if (projected.failure !== undefined) throw new Error(projected.failure)
  const state = projected
  return {
    members: state.members,
    tasks: state.tasks,
    pendingMessages: state.messages.filter(message => !state.delivered.includes(message.id)),
  }
}

/** Read one stored session's full event log through a short-lived read handle. */
async function storedEvents(ctx: Context, id: SessionId): Promise<readonly SessionEvent[]> {
  const handle = await ctx.sessionPersistence.open(id, 'read')
  try {
    return (await handle.read()).events
  } finally {
    await handle.close()
  }
}

async function setup(
  script: ConstructorParameters<typeof MockAdapter>[0],
  config: ConstructorParameters<typeof TeamService>[1] = {},
  beforeTeam?: (ctx: Context) => void,
) {
  const ctx = new Context()
  await initializeAuthorizedFixture(ctx)
  await mountAgentLoopTestDependencies(ctx)
  const storageRoot = mkdtempSync(join(tmpdir(), 'dsh-team-'))
  roots.push(storageRoot)
  await ctx.plugin(JsonlSessionPersistence, { root: storageRoot })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(SubagentService)
  await ctx.plugin(SubagentSpawn, { providerName: 'spawn' })
  await ctx.plugin(SubagentFork, { providerName: 'fork' })
  beforeTeam?.(ctx)
  const teamFiber = await ctx.plugin(TeamService, config)
  const adapter = new MockAdapter(script)
  ctx.llm.registerAdapter(['mock'], adapter)
  const lead = await ctx.agentLoop.create(SessionId('lead'), { provider: 'mock', model: 'mock' })
  return { ctx, lead, adapter, storageRoot, teamFiber }
}

function content(text: string) {
  return [{ type: 'text' as const, text }]
}

function approvedPlanEvents(callId: string, plan: string, isError = false): SessionEvent[] {
  const id = ToolCallId(callId)
  return [
    {
      type: 'tool/call',
      data: { turn: 1, step: 1, callId: id, name: 'exit_plan_mode', arguments: JSON.stringify({ plan }) },
    },
    {
      type: 'tool/result',
      data: {
        turn: 1,
        step: 1,
        message: createToolResultMessage({ callId: id, content: content('approved'), isError }),
      },
    },
  ] as unknown as SessionEvent[]
}

async function appendApprovedPlan(lead: Agent, plan: string, isError = false): Promise<void> {
  await fixtureMission(lead.ctx, lead)
  lead.session.append('turn/start', { turn: 1 })
  lead.session.append('step/start', { turn: 1, step: 1 })
  const callId = ToolCallId('approved-plan')
  const call = lead.session.append('tool/call', {
    turn: 1, step: 1, callId, name: 'exit_plan_mode', arguments: JSON.stringify({ plan }),
  })
  lead.session.append('tool/result', {
    turn: 1,
    step: 1,
    message: createToolResultMessage({ callId, content: content('approved'), isError }),
  }, { surfaceOp: 'append', sourceEventSeqs: [call.seq] })
  lead.session.append('step/end', { turn: 1, step: 1 })
  lead.session.append('turn/end', { turn: 1, reason: { kind: 'completed' } })
}

interface TeamServiceInternals {
  readonly roster: {
    readonly inFlightCreations: Set<Promise<unknown>>
    reconcileProvisioning(root: Agent, signal: AbortSignal): Promise<void>
    liveChildrenByRoot(): Map<Agent, SessionId[]>
  }
  readonly mailbox: {
    tryDispatch(root: Agent, message: TeamMessageSnapshot, signal: AbortSignal): Promise<boolean>
    serializeDispatch(message: TeamMessageSnapshot, operation: () => Promise<boolean>): Promise<boolean>
    markDelivered(root: Agent, messageId: ReturnType<typeof TeamMessageId>, targetId: SessionId): Promise<void>
  }
  readonly journal: {
    state(root: Agent): unknown
  }
  disposeRuntime(): Promise<void>
  recoverFor(agent: Agent): Promise<void>
  scheduleRecovery(agent: Agent): void
}

/** White-box access follows the runtime owners so coverage does not widen the service API. */
function teamInternals(ctx: Context): TeamServiceInternals {
  return ctx.agentTeams as unknown as TeamServiceInternals
}

function spawn(
  ctx: Context,
  lead: Agent,
  name: string,
  options: { context?: 'fresh' | 'fork'; provider?: string; agentOptions?: AgentOptions; activate?: boolean } = {},
) {
  const context = options.context ?? 'fresh'
  return authorizedSpawn(ctx, lead, {
    name,
    description: `${name} responsibility`,
    prompt: content(`${name} initial`),
    context,
    provider: options.provider ?? (context === 'fork' ? 'fork' : 'spawn'),
    ...(options.agentOptions === undefined ? {} : { agentOptions: options.agentOptions }),
    signal: SIGNAL,
  }, options.activate ?? true)
}

async function waitNoAgent(ctx: Context, id: SessionId): Promise<void> {
  await vi.waitFor(() => { expect(ctx.agents.get(id)).toBeUndefined() }, { timeout: 5_000 })
}

async function waitRunning(ctx: Context, id: SessionId): Promise<Agent> {
  return vi.waitFor(() => {
    const agent = ctx.agents.get(id)
    expect(agent?.status).toBe('running')
    return agent!
  }, { timeout: 5_000 })
}

describe('Team identity and provisioning', () => {
  it('rejects missing and failed authoritative Team projections', async () => {
    const first = await setup([])
    const journal = teamInternals(first.ctx).journal
    const stateOf = first.ctx.sessionProjections.stateOf.bind(first.ctx.sessionProjections)
    const stateOfSpy = vi.spyOn(first.ctx.sessionProjections, 'stateOf').mockImplementation((session, key) => (
      key === 'agentTeam' ? undefined : stateOf(session, key)
    ))
    expect(() => journal.state(first.lead)).toThrow('Agent Teams projection is not registered')
    stateOfSpy.mockImplementation((session, key) => key === 'agentTeam'
      ? { ...teamProjectionDefinition.init(session.header), failure: 'failed Team projection' }
      : stateOf(session, key))
    expect(() => journal.state(first.lead)).toThrow('failed Team projection')
    stateOfSpy.mockRestore()
  })

  it('rejects deployment limits that are not positive safe integers', async () => {
    const fields = [
      'maxMembers',
      'maxTasks',
      'maxPendingMessagesPerMember',
      'maxMessageBytes',
      'disposalTimeoutMs',
    ] as const
    for (const field of fields) {
      for (const value of [0, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
        await expect(setup([], { [field]: value })).rejects.toThrow()
      }
    }
  })

  it('supports direct-constructor defaults and recovers roots that already exist', async () => {
    const ctx = new Context()
    await mountAgentLoopTestDependencies(ctx)
    const storageRoot = mkdtempSync(join(tmpdir(), 'dsh-team-direct-'))
    roots.push(storageRoot)
    await ctx.plugin(JsonlSessionPersistence, { root: storageRoot })
    await ctx.plugin(AgentLoop, { agents: [] })
    await ctx.plugin(SubagentService)
    const lead = await ctx.agentLoop.create(SessionId('preexisting-lead'), {})
    const service = new TeamService(ctx)

    expect(service.listMembers(lead)).toEqual([expect.objectContaining({
      name: 'lead',
      status: 'idle',
      diagnostics: [],
    })])
    const provisioning = {
      id: SessionId('preexisting-child'),
      name: 'preexisting-worker',
      description: 'preexisting responsibility',
      provider: 'spawn',
      context: 'fresh' as const,
      phase: 'provisioning' as const,
    }
    lead.session.append('team/member', {
      version: 2,
      teamId: TeamId(lead.id),
      member: provisioning,
    })
    expect(service.listMembers(lead)[1]).toEqual(expect.objectContaining({
      name: 'preexisting-worker',
      status: 'provisioning',
      diagnostics: [],
    }))
    expect(service.listMembers(lead)[1]).not.toHaveProperty('model')
    await Promise.resolve()
  })

  it('creates fresh and fork teammates with immutable names and bounded roster size', async () => {
    const { ctx, lead } = await setup([
      textResponse('lead answer'),
      textResponse('fork answer'),
      textResponse('fresh answer'),
    ], { maxMembers: 2 })
    lead.followup(createUserMessage({ content: content('lead turn'), source: { kind: 'user' } }))
    await lead.whenIdle()

    const forked = await spawn(ctx, lead, 'fork-worker', { context: 'fork' })
    await waitNoAgent(ctx, forked.member.id)
    const fresh = await spawn(ctx, lead, 'fresh-worker')
    await waitNoAgent(ctx, fresh.member.id)

    expect((await ctx.sessionPersistence.stat(forked.member.id))?.header.isSeeded).toBe(true)
    expect((await ctx.sessionPersistence.stat(fresh.member.id))?.header.isSeeded).toBe(false)
    expect(ctx.agentTeams.listMembers(lead).map(row => [row.name, row.context, row.status])).toEqual([
      ['lead', undefined, 'idle'],
      ['fork-worker', 'fork', 'inactive'],
      ['fresh-worker', 'fresh', 'inactive'],
    ])
    await expect(spawn(ctx, lead, 'third-worker')).rejects.toMatchObject({ code: 'TEAM_MEMBER_LIMIT' })
    await expect(spawn(ctx, lead, 'fresh-worker')).rejects.toMatchObject({ code: 'TEAM_MEMBER_NAME_TAKEN' })
  })

  it('flushes the accepted child prompt before committing the active roster edge', async () => {
    const { ctx, lead } = await setup([textResponse('checkpointed child answer')])
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const order: string[] = []
    vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
      if (session.id === lead.id && durable(lead).members[0]?.phase === 'active') {
        order.push('lead-active')
      } else if (session.id !== lead.id) {
        order.push('child')
      }
      return flush(session)
    })

    const started = await spawn(ctx, lead, 'checkpoint-worker')
    expect(order.indexOf('child')).toBeGreaterThanOrEqual(0)
    expect(order.indexOf('child')).toBeLessThan(order.indexOf('lead-active'))
    await waitNoAgent(ctx, started.member.id)
  })

  it('persists an initial prompt idempotently while the actual host gate remains closed', async () => {
    const { ctx, lead, adapter } = await setup([textResponse('unused')])
    const reserved = await ctx.subagents.materializeContinuable({ childId: SessionId('reserved-checkpoint'), provider: 'spawn', label: 'checkpoint', request: { parent: lead }, signal: SIGNAL })
    const first = await reserved.persistInitialPrompt(content('checkpoint me'), 'exact-checkpoint', SIGNAL)
    const second = await reserved.persistInitialPrompt(content('checkpoint me'), 'exact-checkpoint', SIGNAL)
    expect(second).toBe(first)
    expect(reserved.initialMessageId).toBe(first)
    expect(reserved.state).toBe('inbox-persisted')
    expect(adapter.requests).toHaveLength(0)
    const aborted = new AbortController()
    aborted.abort(new Error('checkpoint stopped'))
    await expect(reserved.persistInitialPrompt(content('other'), 'other', aborted.signal)).rejects.toThrow('checkpoint stopped')
    await reserved.dispose()
  })

  it('drains a materialized child when its initial durable prompt fails', async () => {
    const { ctx, lead } = await setup(['hang'])
    const materialize = ctx.subagents.materializeContinuable.bind(ctx.subagents)
    vi.spyOn(ctx.subagents, 'materializeContinuable').mockImplementationOnce(async (spec) => {
      const reserved = await materialize(spec)
      return { ...reserved, persistInitialPrompt: async () => { throw new Error('checkpoint failed') } }
    })
    await expect(spawn(ctx, lead, 'checkpoint-failure')).rejects.toThrow('checkpoint failed')
    const member = durable(lead).members[0]
    expect(member).toMatchObject({ phase: 'failed', error: 'checkpoint failed' })
    if (member !== undefined) await waitNoAgent(ctx, member.id)
  })

  it('records failed provisioning durably, reserves its name, and counts it against the limit', async () => {
    const { ctx, lead } = await setup([], { maxMembers: 1 })
    await expect(spawn(ctx, lead, 'failed-worker', { provider: 'missing' })).rejects.toThrow()

    expect(ctx.agentTeams.listMembers(lead)[1]).toMatchObject({
      name: 'failed-worker',
      status: 'failed',
      provider: 'missing',
    })
    await expect(spawn(ctx, lead, 'failed-worker')).rejects.toMatchObject({ code: 'TEAM_MEMBER_NAME_TAKEN' })
    await expect(spawn(ctx, lead, 'other-worker')).rejects.toMatchObject({ code: 'TEAM_MEMBER_LIMIT' })
  })

  it('records non-Error provider failures and contains a reversed provisioning settlement race', async () => {
    const first = await setup([])
    vi.spyOn(first.ctx.subagents, 'materializeContinuable').mockRejectedValueOnce('string provider failure')
    await expect(spawn(first.ctx, first.lead, 'string-failure')).rejects.toBe('string provider failure')
    expect(first.ctx.agentTeams.listMembers(first.lead)[1]).toMatchObject({
      status: 'failed',
      diagnostics: ['string provider failure'],
    })
    await expect(first.ctx.agentTeams.sendMessage(first.lead, {
      target: 'string-failure', content: content('cannot deliver'), signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_MEMBER_NOT_FOUND' })

    const second = await setup([])
    vi.spyOn(second.ctx.subagents, 'materializeContinuable').mockImplementationOnce(async () => {
      const provisioning = durable(second.lead).members[0]
      if (provisioning === undefined) throw new Error('missing provisioning edge')
      second.lead.session.append('team/member', {
        version: 3,
        teamId: TeamId(second.lead.id),
        member: { ...provisioning, phase: 'active' },
      })
      await second.ctx.sessions.flush(second.lead.session)
      throw new Error('creator failed after recovery settled active')
    })
    await expect(spawn(second.ctx, second.lead, 'reverse-race')).rejects.toBeInstanceOf(AggregateError)
    expect(durable(second.lead).members[0]?.phase).toBe('active')
  })

  it('cleans up a child when recovery settles its provisioning record first', async () => {
    const { ctx, lead } = await setup(['hang'])
    const start = ctx.subagents.materializeContinuable.bind(ctx.subagents)
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    let childId: SessionId | undefined
    vi.spyOn(ctx.subagents, 'materializeContinuable').mockImplementation(async (spec) => {
      childId = spec.childId
      entered.resolve(undefined)
      await release.promise
      return start(spec)
    })

    const spawning = spawn(ctx, lead, 'racing-worker')
    const rejected = expect(spawning).rejects.toMatchObject({ code: 'TEAM_PROVISIONING_CONFLICT' })
    await entered.promise
    await teamInternals(ctx).roster.reconcileProvisioning(lead, SIGNAL)
    expect(durable(lead).members[0]?.phase).toBe('failed')

    release.resolve(undefined)
    await rejected
    if (childId === undefined) throw new Error('reserved child id was not observed')
    await waitNoAgent(ctx, childId)
  })

  it('keeps a durably persisted child gated until explicit authorization and preserves its route', async () => {
    const { ctx, lead, adapter } = await setup([textResponse('unused')])
    const spec = { name: 'gated-worker', description: 'explicit child route', prompt: content('accepted'), context: 'fresh' as const, provider: 'spawn', agentOptions: { provider: 'mock', model: 'child-model' } }
    await humanAction(ctx, lead, 'approveMemberAdd', spec)
    const result = await ctx.agentTeams.spawnTeammate(lead, { ...spec, signal: SIGNAL })
    expect(result.member).toMatchObject({ status: 'idle', model: 'child-model' })
    expect(durable(lead).members[0]).toMatchObject({ model: 'child-model', phase: 'active' })
    expect(adapter.requests).toHaveLength(0)
    expect(() => { ctx.agentTeams.assertExecution(ctx.agents.get(result.member.id)!) }).toThrow('absent')
  })

  it('validates names and permits only the Lead to create or interrupt teammates', async () => {
    const { ctx, lead } = await setup(['hang'])
    for (const name of ['Lead', 'lead', '-bad', 'bad-', 'bad_name', 'x'.repeat(65)]) {
      await expect(spawn(ctx, lead, name)).rejects.toMatchObject({ code: 'TEAM_INVALID_MEMBER_NAME' })
    }
    const started = await spawn(ctx, lead, 'worker')
    const worker = await waitRunning(ctx, started.member.id)
    await expect(spawn(ctx, worker, 'nested')).rejects.toMatchObject({ code: 'TEAM_LEAD_REQUIRED' })
    expect(() => ctx.agentTeams.interrupt(worker, 'worker')).toThrow(expect.objectContaining({ code: 'TEAM_LEAD_REQUIRED' }))
    expect(ctx.agentTeams.interrupt(lead, 'worker')).toEqual({ previousStatus: 'running' })
    await waitNoAgent(ctx, worker.id)
    expect(ctx.agentTeams.interrupt(lead, 'worker')).toEqual({ previousStatus: 'inactive' })
    expect(() => ctx.agentTeams.interrupt(lead, 'lead')).toThrow(expect.objectContaining({ code: 'TEAM_INVALID_TARGET' }))
  })

  it('forwards an exact teammate Agent route to continuable provisioning', async () => {
    const { ctx, lead } = await setup(['hang'])
    const start = ctx.subagents.materializeContinuable.bind(ctx.subagents)
    let observed: AgentOptions | undefined
    vi.spyOn(ctx.subagents, 'materializeContinuable').mockImplementation(async (spec) => {
      observed = spec.request.agentOptions
      return start(spec)
    })

    const result = await spawn(ctx, lead, 'routed-worker', {
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    expect(observed).toEqual({ provider: 'mock', model: 'mock' })
    ctx.agentTeams.interrupt(lead, 'routed-worker')
    await waitNoAgent(ctx, result.member.id)
  })

  it('validates teammate text fields and pre-provisioning cancellation', async () => {
    const { ctx, lead } = await setup([])
    await expect(ctx.agentTeams.spawnTeammate(lead, {
      name: 'empty-description',
      description: ' ',
      prompt: content('unused'),
      context: 'fresh',
      provider: 'spawn',
      signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(ctx.agentTeams.spawnTeammate(lead, {
      name: 'empty-provider',
      description: 'valid description',
      prompt: content('unused'),
      context: 'fresh',
      provider: ' ',
      signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    const controller = new AbortController()
    controller.abort(new TeamError('cancelled before provisioning', 'TEST_CANCELLED'))
    await expect(ctx.agentTeams.spawnTeammate(lead, {
      name: 'cancelled-worker',
      description: 'never provisioned',
      prompt: content('unused'),
      context: 'fresh',
      provider: 'spawn',
      signal: controller.signal,
    })).rejects.toMatchObject({ code: 'TEST_CANCELLED' })
    expect(durable(lead).members).toEqual([])
  })

  it('treats an ordinary fork as a new Root Team and filters inherited Team state', async () => {
    const { ctx, lead } = await setup([])
    await authorizedTask(ctx, lead, { subject: 'parent task', description: 'belongs to parent' })
    const handle = await ctx.agents.create({
      sessionId: SessionId('ordinary-fork'),
      seed: lead.session.snapshotEvents(),
      meta: { parentSession: lead.id, isSeeded: true },
      inheritedEventCount: SessionLogOffset(lead.session.seq),
      agentOptions: { provider: 'mock', model: 'mock' },
    })

    expect(ctx.agentTeams.membership(handle.agent)).toMatchObject({
      id: TeamId(handle.agent.id),
      role: 'lead',
      name: 'lead',
    })
    expect(durable(handle.agent)).toMatchObject({ members: [], tasks: [], pendingMessages: [] })
    await handle.dispose()
  })

  it('rejects stale Agent identities and non-Team subagent children', async () => {
    const { ctx, lead } = await setup([textResponse('done')])
    const started = await ctx.subagents.startContinuable({
      provider: 'spawn',
      label: 'ordinary worker',
      request: { prompt: content('ordinary'), parent: lead },
      signal: SIGNAL,
    })
    const live = ctx.agents.get(started.childId)
    if (live !== undefined) expect(ctx.agentTeams.tryMembership(live)).toBeUndefined()
    await waitNoAgent(ctx, started.childId)
    expect(() => ctx.agentTeams.membership(lead)).not.toThrow()

    const impostor = { ...lead } as Agent
    expect(ctx.agentTeams.tryMembership(impostor)).toBeUndefined()
    expect(() => ctx.agentTeams.membership(impostor)).toThrow(expect.objectContaining({ code: 'TEAM_NOT_MEMBER' }))

    const orphanRoot = await ctx.agents.create({
      sessionId: SessionId('orphan-ordinary-root'),
      meta: { parentSession: SessionId('absent-parent') },
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    expect(ctx.agentTeams.membership(orphanRoot.agent)).toMatchObject({ role: 'lead', name: 'lead' })
    await orphanRoot.dispose()
  })

  it('does not reinterpret an orphaned provider child or malformed parent stream as a Team root', async () => {
    const first = await setup([textResponse('ordinary child done')])
    const parent = await first.ctx.agents.create({
      sessionId: SessionId('temporary-parent'),
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    const started = await first.ctx.subagents.startContinuable({
      provider: 'spawn',
      label: 'ordinary child',
      request: { prompt: content('finish'), parent: parent.agent },
      signal: SIGNAL,
    })
    await waitNoAgent(first.ctx, started.childId)
    await parent.dispose()
    const orphan = await first.ctx.agents.resume({
      resumeSessionId: started.childId,
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    expect(first.ctx.agentTeams.tryMembership(orphan.agent)).toBeUndefined()
    expect(teamInternals(first.ctx).roster.liveChildrenByRoot()).toEqual(new Map())
    await orphan.dispose()

    const second = await setup([])
    const child = await second.ctx.agents.create({
      sessionId: SessionId('malformed-parent-child'),
      meta: { parentSession: second.lead.id },
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    const journal = teamInternals(second.ctx).journal
    const state = journal.state.bind(journal)
    journal.state = () => { throw new Error('malformed Team stream') }
    expect(second.ctx.agentTeams.tryMembership(child.agent)).toBeUndefined()
    journal.state = state
    await child.dispose()
  })
})

describe('Team shared task DAG', () => {
  it('fails loudly when the durable numeric task id space is exhausted', async () => {
    const { ctx, lead } = await setup([])
    const id = TeamTaskId(`task-${Number.MAX_SAFE_INTEGER}`)
    lead.session.append('team/task', {
      version: 2,
      teamId: TeamId(lead.id),
      task: {
        id,
        revision: 1,
        subject: 'last numeric task',
        description: 'occupies the final safe numeric task id',
        status: 'pending',
        blockedBy: [],
        writeScopes: [],
      },
    })
    await ctx.sessions.flush(lead.session)

    await expect(authorizedTask(ctx, lead, {
      subject: 'cannot allocate',
      description: 'no safe numeric task id remains',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_LIMIT' })
  })

  it('bounds non-deleted tasks while retaining deleted task ids as tombstones', async () => {
    const { ctx, lead } = await setup([], { maxTasks: 1 })
    const first = await authorizedTask(ctx, lead, { subject: 'first', description: 'first task' })
    await expect(authorizedTask(ctx, lead, { subject: 'overflow', description: 'overflow task' }))
      .rejects.toMatchObject({ code: 'TEAM_TASK_LIMIT' })

    const deleted = await authorizedUpdate(ctx, lead, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'delete',
    })
    const second = await authorizedTask(ctx, lead, { subject: 'second', description: 'second task' })
    expect(deleted.status).toBe('deleted')
    expect(second.id).toBe(TeamTaskId('task-2'))
    expect(ctx.agentTeams.getTask(lead, first.id).status).toBe('deleted')
    expect(ctx.agentTeams.listTasks(lead).map(task => task.id)).toEqual([second.id])
  })

  it('enforces CAS, ownership, dependencies, transitions, and write-scope warnings', async () => {
    const { ctx, lead } = await setup(['hang', 'hang', textResponse('beta integrated update')])
    const firstMember = await spawn(ctx, lead, 'alpha', { activate: false })
    const alpha = ctx.agents.get(firstMember.member.id)!
    const secondMember = await spawn(ctx, lead, 'beta', { activate: false })
    const beta = ctx.agents.get(secondMember.member.id)!

    const first = await authorizedTask(ctx, alpha, {
      subject: 'first',
      description: 'first task',
      writeScopes: ['src', './src/', 'src'],
    })
    const second = await authorizedTask(ctx, beta, {
      subject: 'second',
      description: 'second task',
      blockedBy: [first.id],
      writeScopes: ['src/feature'],
    })
    expect(first.writeScopes).toEqual(['src'])
    await expect(authorizedUpdate(ctx, beta, {
      taskId: second.id,
      expectedRevision: second.revision,
      action: 'claim',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_BLOCKED' })

    const claimed = await authorizedUpdate(ctx, alpha, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'claim',
    })
    await expect(authorizedUpdate(ctx, beta, {
      taskId: first.id,
      expectedRevision: claimed.revision,
      action: 'claim',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_ALREADY_CLAIMED' })
    expect(ctx.agentTeams.getTask(beta, second.id)).toMatchObject({
      ready: false,
      writeScopeWarnings: [`write scopes overlap with ${first.id}`],
    })
    await expect(authorizedUpdate(ctx, beta, {
      taskId: first.id,
      expectedRevision: claimed.revision,
      action: 'edit',
      subject: 'stolen',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_UNAUTHORIZED' })
    await expect(authorizedUpdate(ctx, alpha, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'complete',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_STALE_REVISION' })

    const completed = await authorizedUpdate(ctx, alpha, {
      taskId: first.id,
      expectedRevision: claimed.revision,
      action: 'complete',
    })
    expect(completed.status).toBe('completed')
    expect(ctx.agentTeams.getTask(beta, second.id).ready).toBe(true)
    const secondClaim = await authorizedUpdate(ctx, beta, {
      taskId: second.id,
      expectedRevision: second.revision,
      action: 'claim',
    })
    const released = await authorizedUpdate(ctx, beta, {
      taskId: second.id,
      expectedRevision: secondClaim.revision,
      action: 'release',
    })
    expect(released).toMatchObject({ status: 'pending', ready: true })
    expect('ownerId' in released).toBe(false)

    await ctx.subagents.drainContinuableChildren(lead, [alpha.id, beta.id])
    await Promise.all([waitNoAgent(ctx, alpha.id), waitNoAgent(ctx, beta.id)])
  })

  it('rejects malformed scopes and every invalid dependency relation', async () => {
    const { ctx, lead } = await setup([])
    const first = await authorizedTask(ctx, lead, { subject: 'one', description: 'one' })
    const second = await authorizedTask(ctx, lead, {
      subject: 'two', description: 'two', blockedBy: [first.id],
    })
    await expect(authorizedTask(ctx, lead, {
      subject: 'bad', description: 'bad', blockedBy: [TeamTaskId('missing')],
    })).rejects.toMatchObject({ code: 'TEAM_TASK_NOT_FOUND' })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'set_dependencies',
      blockedBy: [second.id],
    })).rejects.toMatchObject({ code: 'TEAM_TASK_DEPENDENCY_CYCLE' })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'set_dependencies',
      blockedBy: [first.id],
    })).rejects.toMatchObject({ code: 'TEAM_TASK_DEPENDENCY_CYCLE' })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'set_dependencies',
      blockedBy: [second.id, second.id],
    })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    for (const scope of ['', '.', '..', '/root', 'C:\\root', 'C:root', 'a//b', 'a/../b']) {
      await expect(authorizedTask(ctx, lead, {
        subject: 'scope', description: 'scope', writeScopes: [scope],
      })).rejects.toMatchObject({ code: 'TEAM_INVALID_WRITE_SCOPE' })
    }
  })

  it('rejects incomplete mutations, invalid transitions, and deletion of a live blocker', async () => {
    const { ctx, lead } = await setup([])
    await expect(authorizedTask(ctx, lead, { subject: ' ', description: 'invalid' }))
      .rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(authorizedTask(ctx, lead, { subject: 'invalid', description: '' }))
      .rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(authorizedTask(ctx, lead, { subject: 'x'.repeat(201), description: 'too long' }))
      .rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    const blocker = await authorizedTask(ctx, lead, { subject: 'blocker', description: 'blocker' })
    await authorizedTask(ctx, lead, {
      subject: 'dependent', description: 'dependent', blockedBy: [blocker.id],
    })
    expect(() => ctx.agentTeams.getTask(lead, TeamTaskId('missing')))
      .toThrow(expect.objectContaining({ code: 'TEAM_TASK_NOT_FOUND' }))
    for (const action of ['release', 'complete', 'reopen'] as const) {
      await expect(authorizedUpdate(ctx, lead, {
        taskId: blocker.id,
        expectedRevision: blocker.revision,
        action,
      })).rejects.toMatchObject({ code: 'TEAM_TASK_INVALID_TRANSITION' })
    }
    await expect(authorizedUpdate(ctx, lead, {
      taskId: blocker.id,
      expectedRevision: blocker.revision,
      action: 'edit',
    })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: blocker.id,
      expectedRevision: blocker.revision,
      action: 'set_dependencies',
    })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: blocker.id,
      expectedRevision: blocker.revision,
      action: 'delete',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_HAS_DEPENDENTS' })
  })

  it('supports Lead reassignment, completion, reopen, and deletion permissions', async () => {
    const { ctx, lead } = await setup(['hang'])
    const started = await spawn(ctx, lead, 'owner', { activate: false })
    const owner = ctx.agents.get(started.member.id)!
    const task = await authorizedTask(ctx, owner, { subject: 'lifecycle', description: 'lifecycle' })
    await authorizeFixtureAgent(ctx, lead)
    const assigned = await authorizedUpdate(ctx, lead, {
      taskId: task.id,
      expectedRevision: task.revision,
      action: 'reassign',
      owner: 'owner',
    })
    const associated = ctx.agentTeams.getMission(lead, task.missionId!)
    ctx.agentTeams.bindExecution(owner, { missionId: associated.id, expectedRevision: associated.revision, taskId: task.id })
    await expect(authorizedUpdate(ctx, owner, {
      taskId: task.id,
      expectedRevision: assigned.revision,
      action: 'reassign',
      owner: 'lead',
    })).rejects.toMatchObject({ code: 'TEAM_LEAD_REQUIRED' })
    const complete = await authorizedUpdate(ctx, owner, {
      taskId: task.id,
      expectedRevision: assigned.revision,
      action: 'complete',
    })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: task.id,
      expectedRevision: complete.revision,
      action: 'reassign',
      owner: 'lead',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_INVALID_TRANSITION' })
    await authorizeFixtureAgent(ctx, lead)
    const reopened = await authorizedUpdate(ctx, lead, {
      taskId: task.id,
      expectedRevision: complete.revision,
      action: 'reopen',
    })
    const claimed = await authorizedUpdate(ctx, owner, {
      taskId: task.id,
      expectedRevision: reopened.revision,
      action: 'claim',
    })
    const deleted = await authorizedUpdate(ctx, owner, {
      taskId: task.id,
      expectedRevision: claimed.revision,
      action: 'delete',
    })
    expect(deleted.status).toBe('deleted')
    expect(ctx.agentTeams.listTasks(lead)).toEqual([])
    await expect(authorizedUpdate(ctx, owner, {
      taskId: task.id,
      expectedRevision: deleted.revision,
      action: 'edit',
      subject: 'late',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_DELETED' })
    await ctx.subagents.drainContinuableChildren(lead, [owner.id])
    await waitNoAgent(ctx, owner.id)
  })

  it('covers partial edits, Lead ownership, unassignment, and blocked reassignment', async () => {
    const { ctx, lead } = await setup(['hang'])
    const started = await spawn(ctx, lead, 'editor', { activate: false })
    const editor = ctx.agents.get(started.member.id)!
    const blocker = await authorizedTask(ctx, lead, { subject: 'blocker', description: 'blocker' })
    const task = await authorizedTask(ctx, lead, {
      subject: 'draft',
      description: 'draft description',
      blockedBy: [blocker.id],
    })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: TeamTaskId('missing-update'), expectedRevision: 1, action: 'delete',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_NOT_FOUND' })
    await expect(authorizedUpdate(ctx, lead, {
      taskId: task.id, expectedRevision: task.revision, action: 'reassign', owner: 'editor',
    })).rejects.toMatchObject({ code: 'TEAM_TASK_BLOCKED' })

    const leadClaim = await authorizedUpdate(ctx, lead, {
      taskId: blocker.id, expectedRevision: blocker.revision, action: 'claim',
    })
    expect(leadClaim.ownerName).toBe('lead')
    const completedBlocker = await authorizedUpdate(ctx, lead, {
      taskId: blocker.id, expectedRevision: leadClaim.revision, action: 'complete',
    })
    expect(completedBlocker.status).toBe('completed')
    await authorizeFixtureAgent(ctx, lead)
    const assigned = await authorizedUpdate(ctx, lead, {
      taskId: task.id, expectedRevision: task.revision, action: 'reassign', owner: 'editor',
    })
    const subject = await authorizedUpdate(ctx, editor, {
      taskId: task.id, expectedRevision: assigned.revision, action: 'edit', subject: 'edited subject',
    })
    const description = await authorizedUpdate(ctx, editor, {
      taskId: task.id,
      expectedRevision: subject.revision,
      action: 'edit',
      description: 'edited description',
    })
    const scopes = await authorizedUpdate(ctx, editor, {
      taskId: task.id,
      expectedRevision: description.revision,
      action: 'edit',
      writeScopes: ['src/nested'],
    })
    expect(scopes).toMatchObject({
      subject: 'edited subject',
      description: 'edited description',
      writeScopes: ['src/nested'],
    })
    await authorizeFixtureAgent(ctx, lead)
    const unassigned = await authorizedUpdate(ctx, lead, {
      taskId: task.id, expectedRevision: scopes.revision, action: 'reassign', owner: ' ',
    })
    expect(unassigned).toMatchObject({ status: 'pending' })
    expect('ownerId' in unassigned).toBe(false)

    const broad = await authorizedTask(ctx, lead, {
      subject: 'broad scope', description: 'broad scope', writeScopes: ['src'],
    })
    const narrow = await authorizedTask(ctx, lead, {
      subject: 'narrow scope', description: 'narrow scope', writeScopes: ['src/nested'],
    })
    const disjoint = await authorizedTask(ctx, lead, {
      subject: 'disjoint scope', description: 'disjoint scope', writeScopes: ['docs'],
    })
    await authorizedUpdate(ctx, lead, {
      taskId: broad.id, expectedRevision: broad.revision, action: 'claim',
    })
    await authorizedUpdate(ctx, lead, {
      taskId: narrow.id, expectedRevision: narrow.revision, action: 'claim',
    })
    await authorizedUpdate(ctx, lead, {
      taskId: disjoint.id, expectedRevision: disjoint.revision, action: 'claim',
    })
    expect(ctx.agentTeams.getTask(lead, broad.id).writeScopeWarnings)
      .toEqual([`write scopes overlap with ${narrow.id}`])

    await ctx.subagents.drainContinuableChildren(lead, [editor.id])
    await waitNoAgent(ctx, editor.id)
  })
})

describe('Team Remote API', () => {
  it('enables through the registered initializer and then returns the durable roster idempotently', async () => {
    const { ctx, lead } = await setup(['hang'])
    await expect(ctx.agentTeams.remoteEnable(lead, SIGNAL))
      .rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    const initialize = vi.fn(async (_root: Agent, _signal: AbortSignal) => {
      const member = {
        name: 'enabled-worker',
        description: 'Enabled from the test initializer.',
        initialTask: content('stay active'),
        context: 'fresh' as const,
        continuationProvider: 'spawn',
        agentOptions: { provider: 'mock', model: 'mock' },
        attachments: [],
      }
      return {
        source: 'workspace' as const,
        diagnostics: [],
        members: [member],
      }
    })
    const dispose = ctx.agentTeams.registerInitializer(initialize)

    await expect(humanAction(ctx, lead, 'enable')).resolves.toMatchObject({
      enabled: true,
      alreadyEnabled: false,
      source: 'workspace',
      members: [expect.objectContaining({ name: 'enabled-worker', model: 'mock' })],
    })
    await expect(humanAction(ctx, lead, 'enable')).resolves.toMatchObject({
      enabled: true,
      alreadyEnabled: true,
      source: 'existing',
    })
    expect(initialize).toHaveBeenCalledTimes(1)
    expect(ctx.agentTeams.remoteView(lead).enabled).toBe(true)
    dispose()
    ctx.agentTeams.interrupt(lead, 'enabled-worker')
  })

  it('creates independent draft missions and stores executable task references on the canonical Teamboard', async () => {
    const { ctx, lead } = await setup([])
    const alpha = await ctx.agentTeams.createMission(lead, { title: 'Alpha', objective: 'Alpha independently' })
    const beta = await ctx.agentTeams.createMission(lead, { title: 'Beta', objective: 'Beta independently' })
    const first = await ctx.agentTeams.createTask(lead, { missionId: alpha.id, subject: 'Alpha task', description: 'canonical' })
    const second = await ctx.agentTeams.createTask(lead, { missionId: beta.id, subject: 'Beta task', description: 'canonical' })
    expect(ctx.agentTeams.listMissions(lead).map(mission => mission.id)).toEqual([alpha.id, beta.id])
    expect(ctx.agentTeams.getMission(lead, alpha.id)).toMatchObject({ status: 'draft', plan: { tasks: [], taskIds: [first.id] } })
    expect(ctx.agentTeams.getMission(lead, beta.id)).toMatchObject({ status: 'draft', plan: { tasks: [], taskIds: [second.id] } })
    expect(ctx.agentTeams.listTasks(lead).map(task => task.missionId)).toEqual([alpha.id, beta.id])
    await expect(ctx.agentTeams.remoteApproveMission(lead, { missionId: alpha.id, expectedRevision: 2 })).resolves.toMatchObject({ ok: false, error: { code: 'team-rejected' } })
  })

  it('rejects malformed initial mission task plans before appending', async () => {
    const { ctx, lead } = await setup([])
    const missionTask = (overrides: Partial<TeamTaskSnapshot> = {}): TeamTaskSnapshot => ({
      id: TeamTaskId('mission-task-1'),
      revision: 1,
      subject: 'Mission task',
      description: 'Initial mission task',
      status: 'pending',
      blockedBy: [],
      writeScopes: [],
      ...overrides,
    })
    const first = missionTask()
    const second = missionTask({
      id: TeamTaskId('mission-task-2'),
      blockedBy: [TeamTaskId('mission-task-1')],
    })
    const invalidPlans: readonly [string, unknown][] = [
      ['malformed', {}],
      ['duplicate ids', [first, missionTask()]],
      ['cyclic dependencies', [
        missionTask({ blockedBy: [TeamTaskId('mission-task-2')] }),
        second,
      ]],
      ['missing dependency', [missionTask({ blockedBy: [TeamTaskId('missing-task')] })]],
      ['invalid owner', [missionTask({ ownerId: SessionId('unknown-member') })]],
      ['non-v1 revision', [missionTask({ revision: 2 })]],
      ['non-pending initial status', [missionTask({ status: 'completed' })]],
    ]

    const before = lead.session.snapshotEvents().length
    for (const [kind, tasks] of invalidPlans) {
      await expect(ctx.agentTeams.createMission(lead, {
        title: 'Invalid mission',
        objective: 'This must not be committed to the durable mission log.',
        tasks: tasks as readonly TeamTaskSnapshot[],
      })).rejects.toMatchObject({ code: kind === 'malformed' ? 'TEAM_INVALID_ARGUMENT' : 'TEAM_TASK_MISSION_REQUIRED' })
    }
    expect(lead.session.snapshotEvents()).toHaveLength(before)
    expect(ctx.agentTeams.listMissions(lead)).toEqual([])
  })

  it('reports caller-bound durable work with exact semantic and file contracts', async () => {
    const { ctx, lead } = await setup([])
    const created = await authorizedTask(ctx, lead, { subject: 'Owned', description: 'work' })
    await ctx.agentTeams.updateTask(lead, {
      taskId: created.id,
      expectedRevision: created.revision,
      action: 'claim',
    })
    const eventCount = lead.session.snapshotEvents().length
    const rejected = [
      { state: 'blocked' as const, summary: 'blocked', files: [] },
      { state: 'working' as const, summary: 'work', reason: 'not allowed', files: [] },
      { state: 'done' as const, summary: 'done', reason: 'not allowed', files: [] },
      { state: 'review_required' as const, summary: 'review', files: [] },
      { state: 'working' as const, summary: '   ', files: [] },
      { state: 'review_required' as const, summary: 'review', files: ['/absolute.ts'] },
      { state: 'review_required' as const, summary: 'review', files: ['src/../relative.ts'] },
      { state: 'working' as const, summary: 'work', taskId: TeamTaskId('missing'), files: [] },
    ]
    for (const request of rejected) {
      const result = await ctx.agentTeams.remoteReportWork(lead, request)
      expect(result.ok).toBe(false)
      if (result.ok) throw new Error('invalid work report unexpectedly succeeded')
      expect(result.error.code).toBe('team-rejected')
    }
    expect(lead.session.snapshotEvents()).toHaveLength(eventCount)

    const files = ['./src\\owned.ts']
    const result = await ctx.agentTeams.remoteReportWork(lead, {
      state: 'review_required',
      summary: '  ready for review  ',
      taskId: created.id,
      files,
    })
    files[0] = 'mutated.ts'
    if (!result.ok) throw new Error('work report unexpectedly failed')
    const { updatedAt, ...durableWork } = result.value
    expect(durableWork).toEqual({
      memberId: lead.id,
      state: 'review_required',
      summary: 'ready for review',
      taskId: created.id,
      files: ['src/owned.ts'],
    })
    expect(typeof updatedAt).toBe('number')
    expect(Object.keys(result.value).sort()).toEqual([
      'files', 'memberId', 'state', 'summary', 'taskId', 'updatedAt',
    ])
    const workEvent = lead.session.snapshotEvents().at(-1)
    expect(workEvent).toMatchObject({
      type: 'team/work',
      data: {
        version: 2,
        teamId: TeamId(lead.id),
        work: {
          memberId: lead.id,
          state: 'review_required',
          summary: 'ready for review',
          taskId: created.id,
          files: ['src/owned.ts'],
        },
      },
    })
    expect((workEvent?.data as { work?: { updatedAt?: unknown } }).work).not.toHaveProperty('updatedAt')
    expect(result.value.updatedAt).toBe(workEvent?.time)
    expect(ctx.agentTeams.remoteView(lead).work).toEqual([result.value])
  })

  it('rejects an unknown work state before append without poisoning the projection', async () => {
    const { ctx, lead } = await setup([])
    const before = lead.session.snapshotEvents().length

    await expect(ctx.agentTeams.remoteReportWork(lead, {
      state: 'unknown' as never,
      summary: 'invalid state',
      files: [],
    })).resolves.toEqual({
      ok: false,
      error: { code: 'team-rejected', message: 'unsupported work state unknown' },
    })

    expect(lead.session.snapshotEvents()).toHaveLength(before)
    expect(ctx.agentTeams.remoteView(lead).work).toEqual([])
  })

  it('rejects provisioning teammate reports before append while the Lead remains eligible', async () => {
    const { ctx, lead } = await setup([])
    const childId = SessionId('provisioning-reporter')
    lead.session.append('team/member', {
      version: 2,
      teamId: TeamId(lead.id),
      member: {
        id: childId,
        name: 'provisioning-reporter',
        description: 'not active yet',
        provider: 'spawn',
        context: 'fresh',
        phase: 'provisioning',
      },
    })
    await ctx.sessions.flush(lead.session)
    const child = await ctx.agents.create({
      sessionId: childId,
      meta: { parentSession: lead.id, isSeeded: false },
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    const before = lead.session.snapshotEvents().length

    await expect(ctx.agentTeams.remoteReportWork(child.agent, {
      state: 'working',
      summary: 'too early',
      files: [],
    })).resolves.toEqual({
      ok: false,
      error: { code: 'team-rejected', message: 'canonical teammate is not active for execution' },
    })
    expect(lead.session.snapshotEvents()).toHaveLength(before)
    expect(ctx.agentTeams.remoteView(lead).work).toEqual([])

    await authorizeFixtureAgent(ctx, lead)
    await expect(ctx.agentTeams.remoteReportWork(lead, {
      state: 'working',
      summary: 'lead work',
      files: [],
    })).resolves.toMatchObject({ ok: true, value: { memberId: lead.id } })
    await child.dispose()
  })

  it('requires the latest exit-plan call to have exactly one successful matching result', () => {
    const older = approvedPlanEvents('older', '## Tasks\n- Old task')
    const rejected = approvedPlanEvents('rejected', '## Tasks\n- Rejected task', true)
    const latest = approvedPlanEvents('latest', '## Tasks\n- [ ] Keep task\n1. Numbered task\n* Bullet task\n## Notes\nnot parsed')
    expect(approvedPlanTaskSubjects([...older, ...rejected, ...latest]))
      .toEqual(['Keep task', 'Numbered task', 'Bullet task'])
    expect(() => approvedPlanTaskSubjects([...older, ...rejected] as SessionEvent[]))
      .toThrow(expect.objectContaining({ code: 'TEAM_PLAN_IMPORT_INVALID' }))
    expect(() => approvedPlanTaskSubjects([...latest, latest[1]!] as SessionEvent[]))
      .toThrow(expect.objectContaining({ code: 'TEAM_PLAN_IMPORT_INVALID' }))
    expect(() => approvedPlanTaskSubjects([
      ...older,
      { type: 'tool/call', data: { turn: 2, step: 1, callId: ToolCallId('incomplete'), name: 'exit_plan_mode', arguments: '{}' } },
    ] as SessionEvent[])).toThrow(expect.objectContaining({ code: 'TEAM_PLAN_IMPORT_INVALID' }))
  })

  it('normalizes every plan parsing validation failure to plan-import-invalid', () => {
    expect(parseApprovedPlanTasks('## Tasks\n- [x] One\n\n## Other\n- ignored')).toEqual(['One'])
    for (const invalid of [
      '# Tasks\n- One',
      '## Tasks\nparagraph',
      '## Tasks\n- [ ]',
      '## Tasks\n- [',
      '## Tasks\n- [q] invalid marker',
      '## Tasks\n-    ',
      `## Tasks\n- ${'x'.repeat(201)}`,
      '## Tasks\n### Nested\n- One',
    ]) {
      expect(() => parseApprovedPlanTasks(invalid)).toThrow(expect.objectContaining({
        code: 'TEAM_PLAN_IMPORT_INVALID',
      }))
    }
  })

  it('imports, de-duplicates, and approves the exact post-import plan revision in one flush', async () => {
    const { ctx, lead } = await setup([])
    await appendApprovedPlan(lead, '## Tasks\n- Build API\n- build   api\n1. Build UI\n## Notes\n- ignored')
    const before = lead.session.snapshotEvents().length

    await expect(humanBusinessAction(ctx, lead, 'importApprovedPlan', { missionId: (await fixtureMission(ctx, lead)).id })).resolves.toMatchObject({
      ok: true,
      value: { approvedRevision: 2 },
    })
    expect(ctx.agentTeams.remoteView(lead)).toMatchObject({
      planRevision: 2,
      planPhase: 'approved',
      planApproval: { approvedRevision: 2 },
      tasks: [
        { subject: 'Build API', status: 'pending' },
        { subject: 'Build UI', status: 'pending' },
      ],
    })
    expect(lead.session.snapshotEvents().slice(before).map(event => event.type))
      .toEqual(['team/task', 'team/task', 'team/plan-approved'])
  })

  it('approves a no-op import at the current unapproved revision and leaves failures unmutated', async () => {
    const { ctx, lead } = await setup([], { maxTasks: 1 })
    await authorizedTask(ctx, lead, { subject: 'Existing task', description: 'already present' })
    await appendApprovedPlan(lead, '## Tasks\n- existing   TASK')
    await expect(humanAction(ctx, lead, 'importApprovedPlan', { missionId: (await fixtureMission(ctx, lead)).id }))
      .resolves.toMatchObject({ approvedRevision: 1 })

    const afterApproval = lead.session.snapshotEvents().length
    await expect(ctx.agentTeams.importApprovedPlanAndApprove(lead, { missionId: (await fixtureMission(ctx, lead)).id }))
      .rejects.toMatchObject({
        code: 'TEAM_PLAN_STALE_REVISION',
      })
    expect(lead.session.snapshotEvents()).toHaveLength(afterApproval)

    const { ctx: limitedCtx, lead: limitedLead } = await setup([], { maxTasks: 1 })
    await authorizedTask(limitedCtx, limitedLead, { subject: 'Existing task', description: 'already present' })
    await appendApprovedPlan(limitedLead, '## Tasks\n- New task')
    const beforeLimit = limitedLead.session.snapshotEvents().length
    await expect(humanBusinessAction(limitedCtx, limitedLead, 'importApprovedPlan', { missionId: (await fixtureMission(limitedCtx, limitedLead)).id })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-rejected' },
    })
    expect(limitedLead.session.snapshotEvents()).toHaveLength(beforeLimit)
  })

  it('fails closed for malformed source input, preflights, and non-Leads without a partial import', async () => {
    const { ctx, lead } = await setup(['hang'])
    const malformed = approvedPlanEvents('bad', '## Tasks\n- One')
    const call = malformed[0]!
    if (call.type !== 'tool/call') throw new Error('test fixture call missing')
    lead.session.append('turn/start', { turn: 1 })
    lead.session.append('step/start', { turn: 1, step: 1 })
    lead.session.append('tool/call', { ...call.data, arguments: '{' })
    await fixtureMission(ctx, lead)
    const beforeMalformed = lead.session.snapshotEvents().length
    await expect(humanBusinessAction(ctx, lead, 'importApprovedPlan', { missionId: (await fixtureMission(ctx, lead)).id })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-plan-import-rejected' },
    })
    expect(lead.session.snapshotEvents()).toHaveLength(beforeMalformed)

    const { ctx: checkedCtx, lead: checkedLead } = await setup([])
    await appendApprovedPlan(checkedLead, '## Tasks\n- Checked task')
    checkedCtx.agentTeams.registerApprovalPreflight(() => ['hold'])
    await fixtureMission(checkedCtx, checkedLead)
    const beforePreflight = checkedLead.session.snapshotEvents().length
    await expect(humanBusinessAction(checkedCtx, checkedLead, 'importApprovedPlan', { missionId: (await fixtureMission(checkedCtx, checkedLead)).id })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-preflight-rejected' },
    })
    expect(checkedLead.session.snapshotEvents()).toHaveLength(beforePreflight)

    const { ctx: teamCtx, lead: teamLead } = await setup(['hang'])
    const started = await spawn(teamCtx, teamLead, 'import-worker')
    const worker = await waitRunning(teamCtx, started.member.id)
    const beforeNonLead = teamLead.session.snapshotEvents().length
    await expect(humanBusinessAction(teamCtx, worker, 'importApprovedPlan', { missionId: (await fixtureMission(teamCtx, worker)).id })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-rejected' },
    })
    expect(teamLead.session.snapshotEvents()).toHaveLength(beforeNonLead)
    teamCtx.agentTeams.interrupt(teamLead, 'import-worker')
    await waitNoAgent(teamCtx, worker.id)
  })

  it('rejects a later incomplete or rejected plan call without importing the older plan', async () => {
    const { ctx, lead } = await setup([])
    await appendApprovedPlan(lead, '## Tasks\n- Older task')
    lead.session.append('tool/call', {
      turn: 2, step: 1, callId: ToolCallId('later-incomplete'), name: 'exit_plan_mode', arguments: '{}',
    })
    const beforeIncomplete = lead.session.snapshotEvents().length
    await expect(humanBusinessAction(ctx, lead, 'importApprovedPlan', { missionId: (await fixtureMission(ctx, lead)).id })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-plan-import-rejected' },
    })
    expect(lead.session.snapshotEvents()).toHaveLength(beforeIncomplete)
    expect(ctx.agentTeams.remoteView(lead).tasks).toEqual([])

    const { ctx: rejectedCtx, lead: rejectedLead } = await setup([])
    await appendApprovedPlan(rejectedLead, '## Tasks\n- Older task')
    await appendApprovedPlan(rejectedLead, '## Tasks\n- Rejected task', true)
    const beforeRejected = rejectedLead.session.snapshotEvents().length
    await expect(humanBusinessAction(rejectedCtx, rejectedLead, 'importApprovedPlan', { missionId: (await fixtureMission(rejectedCtx, rejectedLead)).id })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-plan-import-rejected' },
    })
    expect(rejectedLead.session.snapshotEvents()).toHaveLength(beforeRejected)
    expect(rejectedCtx.agentTeams.remoteView(rejectedLead).tasks).toEqual([])
  })

  it('maps empty and overlong imported task subjects to typed import rejections without mutation', async () => {
    for (const plan of ['## Tasks\n- [ ]', `## Tasks\n- ${'x'.repeat(201)}`]) {
      const { ctx, lead } = await setup([])
      await appendApprovedPlan(lead, plan)
      const before = lead.session.snapshotEvents().length
      await expect(humanBusinessAction(ctx, lead, 'importApprovedPlan', { missionId: (await fixtureMission(ctx, lead)).id })).resolves.toMatchObject({
        ok: false,
        error: { code: 'team-plan-import-rejected' },
      })
      expect(lead.session.snapshotEvents()).toHaveLength(before)
      expect(ctx.agentTeams.remoteView(lead).tasks).toEqual([])
    }
  })

  it('approves only a Lead exact non-empty current plan revision and appends no invalid event', async () => {
    const { ctx, lead } = await setup(['hang'])
    const beforeEmpty = lead.session.snapshotEvents().length
    await expect(ctx.agentTeams.approvePlan(lead, { approvedRevision: 0 }))
      .rejects.toMatchObject({ code: 'TEAM_PLAN_EMPTY' })
    expect(lead.session.snapshotEvents()).toHaveLength(beforeEmpty)

    const task = await authorizedTask(ctx, lead, { subject: 'approved', description: 'exact revision' })
    const revision = ctx.agentTeams.remoteView(lead).planRevision
    const started = await spawn(ctx, lead, 'approval-worker')
    const worker = await waitRunning(ctx, started.member.id)
    const beforeInvalid = lead.session.snapshotEvents().length
    await expect(ctx.agentTeams.approvePlan(worker, { approvedRevision: revision }))
      .rejects.toMatchObject({ code: 'TEAM_LEAD_REQUIRED' })
    await expect(ctx.agentTeams.approvePlan(lead, { approvedRevision: revision - 1 }))
      .rejects.toMatchObject({ code: 'TEAM_PLAN_STALE_REVISION' })
    expect(lead.session.snapshotEvents()).toHaveLength(beforeInvalid)

    await expect(humanBusinessAction(ctx, lead, 'approvePlan', { approvedRevision: revision })).resolves.toMatchObject({
      ok: true,
      value: { approvedRevision: revision },
    })
    expect(ctx.agentTeams.remoteView(lead)).toMatchObject({
      planRevision: revision,
      planPhase: 'approved',
      planApproval: { approvedRevision: revision },
    })
    const afterApproval = lead.session.snapshotEvents().length
    await expect(ctx.agentTeams.remoteApprovePlan(lead, { approvedRevision: revision })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-plan-conflict' },
    })
    expect(lead.session.snapshotEvents()).toHaveLength(afterApproval)

    await ctx.agentTeams.updateTask(lead, {
      taskId: task.id,
      expectedRevision: task.revision,
      action: 'edit',
      subject: 'stale approval',
    })
    expect(ctx.agentTeams.remoteView(lead)).toMatchObject({
      planRevision: revision + 1,
      planPhase: 'draft',
      planApproval: { approvedRevision: revision },
    })
    ctx.agentTeams.interrupt(lead, 'approval-worker')
    await waitNoAgent(ctx, worker.id)
  })

  it('exports Team views and task mutations from the owning service', async () => {
    const { ctx, lead } = await setup([])
    expect(ctx.agentTeams.typertRemote).toMatchObject({ serviceKey: 'agentTeams', namespace: 'agentTeams' })
    const emptyView = ctx.agentTeams.remoteView(lead)
    expect(emptyView).toEqual({
      enabled: false,
      planRevision: 0,
      planPhase: 'draft',
      work: [],
      members: [expect.objectContaining({ name: 'lead', role: 'lead', status: 'idle' })],
      tasks: [],
    })
    expect(emptyView).not.toHaveProperty('missions')

    const createdResult = await ctx.agentTeams.remoteCreateTask(lead, {
      missionId: (await fixtureMission(ctx, lead)).id,
      subject: 'Remote task',
      description: 'Created through the generated API',
      blockedBy: [],
      writeScopes: ['packages/experimental/gat-core'],
    })
    expect(createdResult).toMatchObject({ ok: true, value: { revision: 1 } })
    if (!createdResult.ok) throw new Error('Remote task creation did not succeed')
    const created = createdResult.value
    await authorizeFixtureAgent(ctx, lead)
    await expect(ctx.agentTeams.remoteUpdateTask(lead, {
      taskId: created.id,
      expectedRevision: created.revision,
      action: 'claim',
    })).resolves.toMatchObject({
      ok: true,
      value: { id: created.id, revision: 2, ownerName: 'lead' },
    })
    expect(ctx.agentTeams.remoteView(lead).tasks).toHaveLength(1)
  })

  it('preserves Team task rejections and propagates unexpected failures', async () => {
    const { ctx, lead } = await setup([])
    const createRequest = {
      subject: 'Remote task', description: 'Rejected task', blockedBy: [], writeScopes: [],
    }
    const request = { taskId: TeamTaskId('task-1'), expectedRevision: 1, action: 'delete' as const }
    vi.spyOn(ctx.agentTeams, 'createTask')
      .mockRejectedValueOnce(new TeamError('invalid task', 'TEAM_TASK_INVALID'))
      .mockRejectedValueOnce(new Error('unexpected creation failure'))
    vi.spyOn(ctx.agentTeams, 'updateTask')
      .mockRejectedValueOnce(new TeamError('stale', 'TEAM_TASK_STALE_REVISION'))
      .mockRejectedValueOnce(new TeamError('denied', 'TEAM_TASK_FORBIDDEN'))
      .mockRejectedValueOnce(new Error('unexpected mutation failure'))

    await expect(ctx.agentTeams.remoteCreateTask(lead, createRequest)).resolves.toEqual({
      ok: false,
      error: { code: 'team-rejected', message: 'invalid task' },
    })
    await expect(ctx.agentTeams.remoteCreateTask(lead, createRequest))
      .rejects.toThrow('unexpected creation failure')
    await expect(ctx.agentTeams.remoteUpdateTask(lead, request)).resolves.toEqual({
      ok: false,
      error: { code: 'team-task-conflict', message: 'stale' },
    })
    await expect(ctx.agentTeams.remoteUpdateTask(lead, request)).resolves.toEqual({
      ok: false,
      error: { code: 'team-rejected', message: 'denied' },
    })
    await expect(ctx.agentTeams.remoteUpdateTask(lead, request)).rejects.toThrow('unexpected mutation failure')
  })
})

describe('Team mailbox and waiting', () => {
  it('steers a message addressed to the Lead and checkpoints its receipt', async () => {
    const { ctx, lead } = await setup(['hang'])
    await authorizeFixtureAgent(ctx, lead)
    const message: TeamMessageSnapshot = {
      id: TeamMessageId('steer-lead-message'),
      senderId: SessionId('team-worker'),
      senderName: 'worker',
      targetId: lead.id,
      content: content('progress report'),
    }
    lead.session.append('team/message/queued', {
      version: 2,
      teamId: TeamId(lead.id),
      message,
    })

    await expect(teamInternals(ctx).mailbox.tryDispatch(lead, message, SIGNAL)).resolves.toBe(true)
    expect(lead.session.snapshotEvents().some(event => event.type === 'agent/inbox/spliced'
      && event.data.inserted.some(input => input.source.kind === 'team-message'
        && input.source.messageId === message.id))).toBe(true)
    expect(durable(lead).pendingMessages).toEqual([])
    lead.cancel({ kind: 'parent' })
    await lead.whenIdle()
  })

  it('acknowledges steered messages persisted by a busy Lead before model claim', async () => {
    const { ctx, lead, teamFiber } = await setup(['hang', 'hang'], { maxPendingMessagesPerMember: 1 })
    const started = await spawn(ctx, lead, 'lead-reporter')
    const reporter = await waitRunning(ctx, started.member.id)
    lead.followup(createUserMessage({ content: content('keep the Lead busy'), source: { kind: 'user' } }))
    await waitRunning(ctx, lead.id)

    const first = await ctx.agentTeams.sendMessage(reporter, {
      target: 'lead', content: content('first progress report'), signal: SIGNAL,
    })
    const second = await ctx.agentTeams.sendMessage(reporter, {
      target: 'lead', content: content('second progress report'), signal: SIGNAL,
    })
    expect([first.status, second.status]).toEqual(['accepted', 'accepted'])
    expect(lead.status).toBe('running')
    expect(durable(lead).pendingMessages).toEqual([])

    const messageIds = new Set([first.messageId, second.messageId])
    const persisted = await storedEvents(ctx, lead.id)
    const receiptOrder = persisted.flatMap((event) => {
      if (event.type === 'agent/inbox/spliced' && event.data.inserted.some(message =>
        message.source.kind === 'team-message' && messageIds.has(message.source.messageId))) {
        return ['agent/inbox/spliced']
      }
      if (event.type === 'team/message/delivered' && messageIds.has(event.data.messageId)) {
        return ['team/message/delivered']
      }
      return []
    })
    expect(receiptOrder).toEqual([
      'agent/inbox/spliced',
      'team/message/delivered',
      'agent/inbox/spliced',
      'team/message/delivered',
    ])

    const receiptCount = lead.session.snapshotEvents().filter(event => event.type === 'agent/inbox/spliced'
      && event.data.inserted.some(message => message.source.kind === 'team-message'
        && messageIds.has(message.source.messageId))).length
    await teamFiber.dispose()
    await ctx.plugin(TeamService, { maxPendingMessagesPerMember: 1 })
    await vi.waitFor(() => { expect(durable(lead).pendingMessages).toEqual([]) })
    expect(lead.session.snapshotEvents().filter(event => event.type === 'agent/inbox/spliced'
      && event.data.inserted.some(message => message.source.kind === 'team-message'
        && messageIds.has(message.source.messageId)))).toHaveLength(receiptCount)

    lead.cancel({ kind: 'parent' })
    await lead.whenIdle()
  })

  it('flushes a live pending receipt before acknowledgement without inserting a duplicate', async () => {
    const { ctx, lead } = await setup(['hang'])
    const started = await spawn(ctx, lead, 'pending-target')
    const target = await waitRunning(ctx, started.member.id)
    const deliveryWarnings: string[] = []
    ctx.logger.warn = ((value: unknown) => { deliveryWarnings.push(String(value)) }) as typeof ctx.logger.warn
    const immediate = await ctx.agentTeams.sendMessage(lead, {
      target: 'pending-target',
      content: content('live steer receipt'),
      signal: SIGNAL,
    })
    expect(immediate.status, deliveryWarnings.join('\n')).toBe('accepted')
    expect(durable(lead).pendingMessages).toEqual([])
    expect(target.inbox.nextStep.some(item => item.source.kind === 'team-message'
      && item.source.messageId === immediate.messageId)).toBe(true)

    const message: TeamMessageSnapshot = {
      id: TeamMessageId('live-pending-message'),
      senderId: lead.id,
      senderName: 'lead',
      targetId: target.id,
      content: content('durable pending receipt'),
    }
    lead.session.append('team/message/queued', {
      version: 2,
      teamId: TeamId(lead.id),
      message,
    })
    await ctx.sessions.flush(lead.session)
    target.inject(createUserMessage({
      content: content('durable pending receipt'),
      source: {
        kind: 'team-message',
        teamId: TeamId(lead.id),
        messageId: message.id,
        senderId: lead.id,
        senderName: 'lead',
      },
    }))

    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const flushed: SessionId[] = []
    const flushSpy = vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
      flushed.push(session.id)
      return flush(session)
    })
    const delivered = await teamInternals(ctx).mailbox.tryDispatch(lead, message, SIGNAL)

    expect(delivered).toBe(true)
    expect(flushed.slice(0, 2)).toEqual([target.id, lead.id])
    expect(target.inbox.nextStep.filter(item => item.source.kind === 'team-message'
      && item.source.messageId === message.id)).toHaveLength(1)
    expect(durable(lead).pendingMessages).toEqual([])

    // A false target flush is no receipt publication. The same durable identity
    // retries through the live inbox without duplication once persistence works.
    const unflushed = { ...message, id: TeamMessageId('false-target-flush') }
    lead.session.append('team/message/queued', { version: 2, teamId: TeamId(lead.id), message: unflushed })
    await flush(lead.session)
    target.inject(createUserMessage({ content: unflushed.content, source: { kind: 'team-message', teamId: TeamId(lead.id), messageId: unflushed.id, senderId: lead.id, senderName: 'lead' } }))
    flushSpy.mockResolvedValueOnce(false)
    await expect(teamInternals(ctx).mailbox.tryDispatch(lead, unflushed, SIGNAL)).resolves.toBe(false)
    expect(durable(lead).pendingMessages.map(item => item.id)).toEqual([unflushed.id])
    await expect(teamInternals(ctx).mailbox.tryDispatch(lead, unflushed, SIGNAL)).resolves.toBe(true)
    expect(target.inbox.nextStep.filter(item => item.source.kind === 'team-message' && item.source.messageId === unflushed.id)).toHaveLength(1)
    expect(durable(lead).pendingMessages).toEqual([])


    const disappearing: TeamMessageSnapshot = {
      ...message,
      id: TeamMessageId('disappearing-pending-message'),
      content: content('canceled before checkpoint'),
    }
    lead.session.append('team/message/queued', {
      version: 2,
      teamId: TeamId(lead.id),
      message: disappearing,
    })
    await flush(lead.session)
    const disappearingInput = createUserMessage({
      content: content('canceled before checkpoint'),
      source: {
        kind: 'team-message',
        teamId: TeamId(lead.id),
        messageId: disappearing.id,
        senderId: lead.id,
        senderName: 'lead',
      },
    })
    target.inject(disappearingInput)
    flushSpy.mockImplementationOnce(async (session) => {
      target.inbox.remove(disappearingInput.id)
      return flush(session)
    })
    await expect(teamInternals(ctx).mailbox.tryDispatch(lead, disappearing, SIGNAL)).resolves.toBe(false)
    expect(durable(lead).pendingMessages.map(pending => pending.id)).toEqual([disappearing.id])

    ctx.agentTeams.interrupt(lead, 'pending-target')
    target.cancel({ kind: 'parent' })
    await waitNoAgent(ctx, target.id)
  })

  it('acknowledges steered messages accepted by a busy target inbox', async () => {
    const { ctx, lead } = await setup(['hang'], { maxPendingMessagesPerMember: 1 })
    const started = await spawn(ctx, lead, 'busy-target')
    const target = await waitRunning(ctx, started.member.id)
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const flushed: SessionId[] = []
    vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
      flushed.push(session.id)
      return flush(session)
    })

    const first = await ctx.agentTeams.sendMessage(lead, {
      target: 'busy-target', content: content('first steered message'), signal: SIGNAL,
    })

    expect(first.status).toBe('accepted')
    expect(flushed[0]).toBe(lead.id)
    expect(flushed.at(-1)).toBe(lead.id)
    expect(flushed.slice(1, -1)).toContain(target.id)
    expect(durable(lead).pendingMessages).toEqual([])
    expect(target.inbox.nextStep.some(message => message.source.kind === 'team-message'
      && message.source.messageId === first.messageId)).toBe(true)

    flushed.length = 0
    const second = await ctx.agentTeams.sendMessage(lead, {
      target: 'busy-target', content: content('second steered message'), signal: SIGNAL,
    })

    expect(second.status).toBe('accepted')
    expect(flushed[0]).toBe(lead.id)
    expect(flushed.at(-1)).toBe(lead.id)
    expect(flushed.slice(1, -1)).toContain(target.id)
    expect(durable(lead).pendingMessages).toEqual([])
    expect(target.inbox.nextStep.filter(message => message.source.kind === 'team-message'
      && (message.source.messageId === first.messageId || message.source.messageId === second.messageId)))
      .toHaveLength(2)

    ctx.agentTeams.interrupt(lead, 'busy-target')
    target.cancel({ kind: 'parent' })
    await waitNoAgent(ctx, target.id)
  })

  it('serializes concurrent Steer delivery admission for one target', async () => {
    const { ctx, lead } = await setup(['hang'])
    const started = await spawn(ctx, lead, 'ordered-target')
    const target = await waitRunning(ctx, started.member.id)
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    const admitted: string[] = []
    const steer = target.steer.bind(target)
    vi.spyOn(target, 'steer').mockImplementation((input) => {
      const last = input.content.at(-1)
      const text = last?.type === 'text' ? last.text : ''
      admitted.push(text)
      steer(input)
    })
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    let held = false
    vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
      if (session.id === target.id && !held) {
        held = true
        entered.resolve(undefined)
        await release.promise
      }
      return flush(session)
    })

    const first = ctx.agentTeams.sendMessage(lead, {
      target: 'ordered-target', content: content('first steer'), signal: SIGNAL,
    })
    await entered.promise
    let secondSettled = false
    const second = ctx.agentTeams.sendMessage(lead, {
      target: 'ordered-target', content: content('second steer'), signal: SIGNAL,
    }).finally(() => { secondSettled = true })
    await vi.waitFor(() => { expect(durable(lead).pendingMessages).toHaveLength(2) })
    expect(admitted).toEqual(['first steer'])
    expect(secondSettled).toBe(false)

    release.resolve(undefined)
    await expect(Promise.all([first, second])).resolves.toMatchObject([
      { status: 'accepted' },
      { status: 'accepted' },
    ])
    expect(admitted).toEqual(['first steer', 'second steer'])

    ctx.agentTeams.interrupt(lead, 'ordered-target')
    target.cancel({ kind: 'parent' })
    await waitNoAgent(ctx, target.id)
  })

  it('delivers persisted mail before the later message that cold-resumes its target', async () => {
    const { ctx, lead } = await setup([textResponse('target initial'), 'hang', 'hang'])
    const started = await spawn(ctx, lead, 'reordered-target')
    await waitNoAgent(ctx, started.member.id)
    const earlier: TeamMessageSnapshot = {
      id: TeamMessageId('earlier-message'),
      senderId: lead.id,
      senderName: 'lead',
      targetId: started.member.id,
      content: content('earlier steer'),
    }
    lead.session.append('team/message/queued', {
      version: 2,
      teamId: TeamId(lead.id),
      message: earlier,
    })
    await ctx.sessions.flush(lead.session)

    const later = await ctx.agentTeams.sendMessage(lead, {
      target: 'reordered-target', content: content('later steer'), signal: SIGNAL,
    })
    expect(later.status).toBe('queued')
    await recoverFixtureMember(ctx, lead, 'reordered-target')
    const pending = durable(lead).pendingMessages.find(item => item.id === later.messageId)!
    await expect(teamInternals(ctx).mailbox.tryDispatch(lead, pending, SIGNAL)).resolves.toBe(true)
    const target = await waitRunning(ctx, started.member.id)
    await vi.waitFor(() => {
      const accepted = target.session.snapshotEvents().flatMap(event => event.type === 'agent/inbox/spliced'
        ? event.data.inserted.flatMap(message => message.source.kind === 'team-message'
          ? [message.source.messageId]
          : [])
        : [])
      expect(accepted).toEqual([earlier.id, later.messageId])
    })

    ctx.agentTeams.interrupt(lead, 'reordered-target')
    target.cancel({ kind: 'parent' })
    await waitNoAgent(ctx, target.id)
  })

  it('deduplicates live target history and contains inspection and delivery failures', async () => {
    const { ctx, lead } = await setup(['hang', textResponse('inactive target initial')])
    const liveStarted = await spawn(ctx, lead, 'live-target')
    const live = await waitRunning(ctx, liveStarted.member.id)
    const internal = teamInternals(ctx).mailbox
    const message: TeamMessageSnapshot = {
      id: TeamMessageId('live-recorded-message'),
      senderId: lead.id,
      senderName: 'lead',
      targetId: live.id,
      content: content('already in live history'),
    }
    lead.session.append('team/message/queued', {
      version: 2, teamId: TeamId(lead.id), message,
    })
    await ctx.sessions.flush(lead.session)
    live.session.append('user/message', createUserMessage({
      content: content('different Team message first'),
      source: {
        kind: 'team-message',
        teamId: TeamId(lead.id),
        messageId: TeamMessageId('other-message'),
        senderId: lead.id,
        senderName: 'lead',
      },
    }), { surfaceOp: 'append' })
    live.session.append('user/message', createUserMessage({
      content: content('already in live history'),
      source: {
        kind: 'team-message',
        teamId: TeamId(lead.id),
        messageId: message.id,
        senderId: lead.id,
        senderName: 'lead',
      },
    }), { surfaceOp: 'append' })
    await expect(internal.tryDispatch(lead, message, SIGNAL)).resolves.toBe(true)
    await internal.markDelivered(lead, message.id, live.id)
    await expect(internal.tryDispatch(lead, message, SIGNAL)).resolves.toBe(true)

    const wrongTarget: TeamMessageSnapshot = {
      ...message,
      id: TeamMessageId('wrong-target-message'),
    }
    lead.session.append('team/message/queued', {
      version: 2, teamId: TeamId(lead.id), message: wrongTarget,
    })
    await ctx.sessions.flush(lead.session)
    await internal.markDelivered(lead, wrongTarget.id, SessionId('wrong-target'))
    await expect(internal.serializeDispatch(wrongTarget, async () => true)).resolves.toBe(true)
    const serialEntered = Promise.withResolvers<undefined>()
    const releaseSerial = Promise.withResolvers<undefined>()
    const serialFirst = internal.serializeDispatch(wrongTarget, async () => {
      serialEntered.resolve(undefined)
      await releaseSerial.promise
      return true
    })
    await serialEntered.promise
    const serialSecond = internal.serializeDispatch({
      ...wrongTarget, id: TeamMessageId('second-serialized-message'),
    }, async () => true)
    releaseSerial.resolve(undefined)
    await expect(Promise.all([serialFirst, serialSecond])).resolves.toEqual([true, true])

    const warnings: string[] = []
    ctx.logger.warn = ((value: unknown) => { warnings.push(String(value)) }) as typeof ctx.logger.warn
    const failedAck = vi.spyOn(ctx.sessions, 'flush').mockRejectedValueOnce(new Error('acknowledgement flush failed'))
    live.session.append('user/message', createUserMessage({
      content: content('acknowledgement failure'),
      source: {
        kind: 'team-message',
        teamId: TeamId(lead.id),
        messageId: wrongTarget.id,
        senderId: lead.id,
        senderName: 'lead',
      },
    }), { surfaceOp: 'append' })
    await vi.waitFor(() => {
      expect(warnings.some(warning => warning.includes('acknowledgement flush failed'))).toBe(true)
    })
    failedAck.mockRestore()

    const inactiveStarted = await spawn(ctx, lead, 'inactive-target')
    await waitNoAgent(ctx, inactiveStarted.member.id)
    const openRead = vi.spyOn(ctx.sessionPersistence, 'open').mockRejectedValueOnce(new Error('read unavailable'))
    const uncertain = await ctx.agentTeams.sendMessage(lead, {
      target: 'inactive-target', content: content('inspection failure'), signal: SIGNAL,
    })
    expect(uncertain.status).toBe('queued')
    openRead.mockRestore()

    const inaccessibleSteer = vi.spyOn(live, 'steer').mockImplementationOnce(() => { throw new Error('delivery unavailable') })
    const failed = await ctx.agentTeams.sendMessage(lead, {
      target: 'inactive-target', content: content('delivery failure'), signal: SIGNAL,
    })
    expect(failed.status).toBe('queued')
    expect(warnings.some(warning => warning.includes('read unavailable'))).toBe(false)
    expect(warnings.some(warning => warning.includes('delivery unavailable'))).toBe(false)
    expect(inaccessibleSteer).not.toHaveBeenCalled()

    ctx.agentTeams.interrupt(lead, 'live-target')
    await waitNoAgent(ctx, live.id)
  })

  it('queues an inactive sibling until explicit host recovery, preserving sender attribution', async () => {
    const { ctx, lead } = await setup(['hang', 'hang', textResponse('beta resumed')])
    const alphaStarted = await spawn(ctx, lead, 'alpha')
    const alpha = await waitRunning(ctx, alphaStarted.member.id)
    const betaStarted = await spawn(ctx, lead, 'beta')
    const beta = await waitRunning(ctx, betaStarted.member.id)
    ctx.agentTeams.interrupt(lead, 'beta')
    await waitNoAgent(ctx, beta.id)

    const first = await ctx.agentTeams.sendMessage(alpha, {
      target: 'beta', content: content('first update'), signal: SIGNAL,
    })
    expect(first.status).toBe('queued')
    await recoverFixtureMember(ctx, lead, 'beta')
    const pending = durable(lead).pendingMessages.find(item => item.id === first.messageId)!
    await expect(teamInternals(ctx).mailbox.tryDispatch(lead, pending, SIGNAL)).resolves.toBe(true)
    await waitNoAgent(ctx, betaStarted.member.id)
    await vi.waitFor(() => { expect(durable(lead).pendingMessages).toEqual([]) })

    const stored = await storedEvents(ctx, betaStarted.member.id)
    const peerMessages = stored.filter(event => event.type === 'user/message'
      && event.data.source.kind === 'team-message')
    expect(peerMessages.map((event) => {
      if (event.type !== 'user/message') return undefined
      const block = event.data.content.at(-1)
      return block?.type === 'text' ? block.text : undefined
    })).toEqual(['first update'])
    expect(peerMessages.map(event => event.type === 'user/message'
      ? event.data.content[0]?.type === 'text' && event.data.content[0].text
      : undefined)).toEqual([
      expect.stringMatching(/^Team message .* from alpha:$/u),
    ])
    expect(peerMessages.map(event => event.type === 'user/message' && event.data.source.kind === 'team-message'
      ? [event.data.source.messageId, event.data.source.senderName]
      : undefined)).toEqual([
      [first.messageId, 'alpha'],
    ])

    ctx.agentTeams.interrupt(lead, 'alpha')
    await waitNoAgent(ctx, alpha.id)
  })

  it('enforces message byte and pending-count limits without encouraging retry after enqueue', async () => {
    const { ctx, lead } = await setup([textResponse('idle')], {
      maxMessageBytes: 256,
      maxPendingMessagesPerMember: 1,
    })
    const target = await spawn(ctx, lead, 'target')
    await waitNoAgent(ctx, target.member.id)
    await expect(ctx.agentTeams.sendMessage(lead, {
      target: 'target', content: content('x'.repeat(300)), signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_MESSAGE_TOO_LARGE' })
    vi.spyOn(ctx.sessionPersistence, 'open').mockRejectedValueOnce(new Error('temporary read failure'))
    const queued = await ctx.agentTeams.sendMessage(lead, {
      target: 'target', content: content('one'), signal: SIGNAL,
    })
    expect(queued.status).toBe('queued')
    await expect(ctx.agentTeams.sendMessage(lead, {
      target: 'target', content: content('two'), signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_MAILBOX_FULL' })
    await expect(ctx.agentTeams.sendMessage(lead, {
      target: 'lead', content: content('self'), signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_SELF_MESSAGE' })
    await expect(ctx.agentTeams.sendMessage(lead, {
      target: 'missing', content: content('unknown target'), signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_MEMBER_NOT_FOUND' })
    const controller = new AbortController()
    controller.abort(new TeamError('cancelled before queue', 'TEST_CANCELLED'))
    await expect(ctx.agentTeams.sendMessage(lead, {
      target: 'target', content: content('cancelled'), signal: controller.signal,
    })).rejects.toMatchObject({ code: 'TEST_CANCELLED' })
  })

  it('interrupts only the current turn and retains an already accepted follow-up', async () => {
    const { ctx, lead } = await setup(['hang', textResponse('after interrupt')])
    const started = await spawn(ctx, lead, 'worker')
    const worker = await waitRunning(ctx, started.member.id)
    const followup = await ctx.agentTeams.sendMessage(lead, {
      target: 'worker', content: content('retained follow-up'), signal: SIGNAL,
    })
    expect(followup.status).toBe('accepted')
    expect(ctx.agentTeams.interrupt(lead, 'worker')).toEqual({ previousStatus: 'running' })
    await vi.waitFor(() => { expect(worker.status).toBe('idle') })
    expect([...worker.inbox.nextStep, ...worker.inbox.nextTurn].some(message => message.source.kind === 'team-message'
      && message.source.messageId === followup.messageId)).toBe(true)
    worker.cancel({ kind: 'parent' })
    await waitNoAgent(ctx, worker.id)
  })

  it('waits for one change, supports cancellation, times out, and releases waiters on HMR disposal', async () => {
    const ctx = new Context()
    await initializeAuthorizedFixture(ctx)
    await mountAgentLoopTestDependencies(ctx)
    const storageRoot = mkdtempSync(join(tmpdir(), 'dsh-team-wait-'))
    roots.push(storageRoot)
    await ctx.plugin(JsonlSessionPersistence, { root: storageRoot })
    await ctx.plugin(AgentLoop, { agents: [] })
    await ctx.plugin(SubagentService)
    const fiber = await ctx.plugin(TeamService)
    const service = ctx.agentTeams
    const lead = await ctx.agentLoop.create(SessionId('wait-lead'), {})
    await fixtureMission(ctx, lead)

    await expect(service.waitForChange(lead, 9_999, SIGNAL))
      .rejects.toMatchObject({ code: 'TEAM_INVALID_TIMEOUT' })
    const alreadyAborted = new AbortController()
    alreadyAborted.abort(new TeamError('cancelled before wait', 'TEST_CANCELLED'))
    await expect(service.waitForChange(lead, 10_000, alreadyAborted.signal))
      .rejects.toMatchObject({ code: 'TEST_CANCELLED' })

    const changed = service.waitForChange(lead, 10_000, SIGNAL)
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const flushEntered = Promise.withResolvers<undefined>()
    const releaseFlush = Promise.withResolvers<undefined>()
    vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(async (session) => {
      flushEntered.resolve(undefined)
      await releaseFlush.promise
      return await flush(session)
    })
    let waitSettled = false
    void changed.finally(() => { waitSettled = true })
    const creating = service.createTask(lead, { missionId: (await fixtureMission(ctx, lead)).id, subject: 'wake', description: 'wake waiter' })
    await flushEntered.promise
    expect(waitSettled).toBe(false)
    releaseFlush.resolve(undefined)
    await creating
    await expect(changed).resolves.toEqual({ timedOut: false })

    const controller = new AbortController()
    const cancelled = service.waitForChange(lead, 10_000, controller.signal)
    controller.abort(new TeamError('cancelled', 'TEST_CANCELLED'))
    await expect(cancelled).rejects.toMatchObject({ code: 'TEST_CANCELLED' })

    const stringAbort = new AbortController()
    const firstWaiter = service.waitForChange(lead, 10_000, stringAbort.signal)
    const secondWaiter = service.waitForChange(lead, 10_000, SIGNAL)
    stringAbort.abort('string cancellation')
    await expect(firstWaiter).rejects.toMatchObject({
      code: 'TEAM_WAIT_ABORTED',
      message: 'wait_agent aborted: string cancellation',
    })
    await service.createTask(lead, { missionId: (await fixtureMission(ctx, lead)).id, subject: 'second waiter', description: 'second waiter remains registered' })
    await expect(secondWaiter).resolves.toEqual({ timedOut: false })

    const objectAbort = new AbortController()
    const objectCancelled = service.waitForChange(lead, 10_000, objectAbort.signal)
    objectAbort.abort({ kind: 'user' })
    await expect(objectCancelled).rejects.toMatchObject({
      code: 'TEAM_WAIT_ABORTED',
      message: "wait_agent aborted: { kind: 'user' }",
    })

    await service.createTask(lead, { missionId: (await fixtureMission(ctx, lead)).id, subject: 'already changed', description: 'edge-triggered wait' })
    vi.useFakeTimers()
    const timeout = service.waitForChange(lead, 10_000, SIGNAL)
    await vi.advanceTimersByTimeAsync(10_000)
    await expect(timeout).resolves.toEqual({ timedOut: true })
    vi.useRealTimers()

    const disposed = service.waitForChange(lead, 10_000, SIGNAL)
    await fiber.dispose()
    await expect(disposed).resolves.toEqual({ timedOut: false })
    expect(ctx.get('agentTeams')).toBeUndefined()
  })

  it('disposes live teammate Activations and their waits when the Team service unloads', async () => {
    const { ctx, lead, teamFiber } = await setup(['hang'])
    const started = await spawn(ctx, lead, 'dispose-worker')
    await waitRunning(ctx, started.member.id)
    const waiting = ctx.agentTeams.waitForChange(lead, 10_000, SIGNAL)

    await teamFiber.dispose()

    await expect(waiting).resolves.toEqual({ timedOut: false })
    expect(ctx.agents.get(started.member.id)).toBeUndefined()
    expect(ctx.get('agentTeams')).toBeUndefined()
  })

  it('closes creation admission and drains an in-flight spawn before unload completes', async () => {
    const { ctx, lead, teamFiber } = await setup(['hang'])
    const service = ctx.agentTeams
    const start = ctx.subagents.materializeContinuable.bind(ctx.subagents)
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    let childId: SessionId | undefined
    vi.spyOn(ctx.subagents, 'materializeContinuable').mockImplementation(async (spec) => {
      childId = spec.childId
      entered.resolve(undefined)
      await release.promise
      return start(spec)
    })
    const spawning = spawn(ctx, lead, 'disposing-worker')
    const rejected = expect(spawning).rejects.toSatisfy((error: unknown) => error instanceof TeamError && error.code === 'TEAM_DISPOSED' || error instanceof AggregateError && error.errors.every((cause: unknown) => cause instanceof TeamError && cause.code === 'TEAM_DISPOSED'))
    await entered.promise

    const disposal = teamFiber.dispose()
    await Promise.resolve()
    await expect(service.waitForChange(lead, 3_600_000, SIGNAL)).resolves.toEqual({ timedOut: false })
    await expect(service.spawnTeammate(lead, {
      name: 'late-worker',
      description: 'must not enter after disposal',
      prompt: content('late task'),
      context: 'fresh',
      provider: 'spawn',
      signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_DISPOSED' })
    release.resolve(undefined)

    await rejected
    await disposal
    if (childId !== undefined) expect(ctx.agents.get(childId)).toBeUndefined()
    expect(ctx.get('agentTeams')).toBeUndefined()
  })

  it('drains an admitted plan approval before projection teardown and rejects late approval', async () => {
    const { ctx, lead, teamFiber } = await setup([])
    const service = ctx.agentTeams
    const task = await service.createTask(lead, {
      missionId: (await fixtureMission(ctx, lead)).id,
      subject: 'approval race',
      description: 'approval must commit before teardown',
    })
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(async (session) => {
      entered.resolve(undefined)
      await release.promise
      return await flush(session)
    })

    const admitted = humanBusinessAction(ctx, lead, 'approvePlan', { approvedRevision: task.revision })
    await entered.promise
    const lifecycle = (service as unknown as { lifecycle: TeamRuntimeLifecycle }).lifecycle
    const closed = lifecycle.disposed
      ? Promise.resolve()
      : new Promise<void>((resolve) => { lifecycle.signal.addEventListener('abort', () => { resolve() }, { once: true }) })
    let disposed = false
    const disposal = teamFiber.dispose().then(() => { disposed = true })
    await closed
    const late = humanBusinessAction(ctx, lead, 'approvePlan', { approvedRevision: task.revision })
    await Promise.resolve()
    const disposedBeforeRelease = disposed
    release.resolve(undefined)

    const [admittedOutcome, lateOutcome] = await Promise.allSettled([admitted, late])
    await disposal
    expect(disposedBeforeRelease).toBe(false)
    expect(admittedOutcome).toMatchObject({
      status: 'fulfilled',
      value: { ok: true, value: { approvedRevision: task.revision } },
    })
    expect(lateOutcome.status).toBe('rejected')
    if (lateOutcome.status !== 'rejected') throw new Error('late approval unexpectedly admitted')
    expect(lateOutcome.reason).toMatchObject({ message: 'control HTTP 404' })
    expect(lead.session.snapshotEvents().map((event: { type: string }) => event.type)
      .filter((type: string) => type === 'team/plan-approved')).toHaveLength(1)
  })

  it('drains an admitted work report before projection teardown and rejects late work', async () => {
    const { ctx, lead, teamFiber } = await setup([])
    const service = ctx.agentTeams
    await authorizeFixtureAgent(ctx, lead)
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(async (session) => {
      entered.resolve(undefined)
      await release.promise
      return await flush(session)
    })

    const admitted = service.remoteReportWork(lead, { state: 'working', summary: 'admitted', files: [] })
    await entered.promise
    const lifecycle = (service as unknown as { lifecycle: TeamRuntimeLifecycle }).lifecycle
    const closed = lifecycle.disposed
      ? Promise.resolve()
      : new Promise<void>((resolve) => { lifecycle.signal.addEventListener('abort', () => { resolve() }, { once: true }) })
    let disposed = false
    const disposal = teamFiber.dispose().then(() => { disposed = true })
    await closed
    const late = service.remoteReportWork(lead, { state: 'working', summary: 'late', files: [] })
    await Promise.resolve()
    const disposedBeforeRelease = disposed
    release.resolve(undefined)

    const [admittedOutcome, lateOutcome] = await Promise.allSettled([admitted, late])
    await disposal
    expect(disposedBeforeRelease).toBe(false)
    expect(admittedOutcome.status).toBe('fulfilled')
    if (admittedOutcome.status !== 'fulfilled' || !admittedOutcome.value.ok)
      throw new Error('admitted work report unexpectedly failed')
    expect(admittedOutcome.value.value).toMatchObject({ memberId: lead.id, summary: 'admitted' })
    expect(lateOutcome).toEqual({
      status: 'fulfilled',
      value: { ok: false, error: { code: 'team-rejected', message: 'Agent Teams service disposed' } },
    })
    expect(lead.session.snapshotEvents().map((event: { type: string }) => event.type)
      .filter((type: string) => type === 'team/work')).toHaveLength(1)
  })

  it('keeps the projection registered after mutation disposal times out until the mutation settles', async () => {
    let projectionDisposals = 0
    const { ctx, lead, teamFiber } = await setup([], { disposalTimeoutMs: 10 }, (setupCtx) => {
      const register = setupCtx.sessionProjections.register.bind(setupCtx.sessionProjections) as (
        definition: typeof teamProjectionDefinition,
      ) => () => void
      vi.spyOn(setupCtx.sessionProjections, 'register').mockImplementation(((definition: typeof teamProjectionDefinition) => {
        const dispose = register(definition)
        return () => {
          projectionDisposals += 1
          dispose()
        }
      }) as typeof setupCtx.sessionProjections.register)
    })
    const service = ctx.agentTeams
    await authorizeFixtureAgent(ctx, lead)
    const disposalErrors: unknown[] = []
    ctx.logger.error = ((error: unknown) => { disposalErrors.push(error) }) as typeof ctx.logger.error
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(async (session) => {
      entered.resolve(undefined)
      await release.promise
      return await flush(session)
    })

    const admitted = service.remoteReportWork(lead, { state: 'working', summary: 'held past timeout', files: [] })
    await entered.promise
    const lifecycle = (service as unknown as { lifecycle: TeamRuntimeLifecycle }).lifecycle
    const closed = new Promise<void>((resolve) => {
      lifecycle.signal.addEventListener('abort', () => { resolve() }, { once: true })
    })
    vi.useFakeTimers()
    let disposed = false
    const disposal = teamFiber.dispose().then(() => { disposed = true })
    await closed
    const late = service.remoteReportWork(lead, { state: 'working', summary: 'late', files: [] })

    await vi.advanceTimersByTimeAsync(10)
    await Promise.resolve()
    const disposedWhileHeld = disposed
    const projectionWhileHeld = ctx.sessionProjections.stateOf(lead.session, 'agentTeam')
    release.resolve(undefined)

    const [admittedOutcome, lateOutcome] = await Promise.allSettled([admitted, late])
    await disposal
    expect(disposedWhileHeld).toBe(false)
    expect(projectionWhileHeld).toBeDefined()
    expect(admittedOutcome.status).toBe('fulfilled')
    if (admittedOutcome.status !== 'fulfilled' || !admittedOutcome.value.ok)
      throw new Error('admitted work report unexpectedly failed')
    expect(admittedOutcome.value.value).toMatchObject({ memberId: lead.id, summary: 'held past timeout' })
    expect(lateOutcome).toEqual({
      status: 'fulfilled',
      value: { ok: false, error: { code: 'team-rejected', message: 'Agent Teams service disposed' } },
    })
    expect(disposalErrors.some(error => error instanceof AggregateError
      && error.errors.some(reason => reason instanceof TeamError && reason.code === 'TEAM_DISPOSAL_TIMEOUT'))).toBe(true)
    expect(projectionDisposals).toBe(1)
    expect(ctx.sessionProjections.stateOf(lead.session, 'agentTeam')).toBeUndefined()
  })

  it('retains an in-flight creation cleanup failure during disposal', async () => {
    const { ctx } = await setup([])
    const internal = teamInternals(ctx)
    const cleanupFailure = new Error('creation cleanup failed')
    const rejected = Promise.reject(cleanupFailure)
    void rejected.catch(() => undefined)
    internal.roster.inFlightCreations.add(rejected)

    await expect(internal.disposeRuntime()).rejects.toMatchObject({ errors: [cleanupFailure] })
  })

  it('recognizes wrapped and coded runtime cancellation during disposal settlement', async () => {
    const open = new TeamRuntimeLifecycle(100)
    const ordinaryFailure = new Error('ordinary failure before disposal')
    const openFailures: unknown[] = []
    await open.settle([Promise.reject(ordinaryFailure)], openFailures)
    expect(openFailures).toEqual([ordinaryFailure])

    const lifecycle = new TeamRuntimeLifecycle(100)
    lifecycle.close()
    const failures: unknown[] = []
    await lifecycle.settle([
      Promise.reject(new Error('wrapped cancellation', { cause: lifecycle.reason })),
      Promise.reject(new TeamError('translated cancellation', 'TEAM_DISPOSED')),
    ], failures)
    expect(failures).toEqual([])

    const cyclic = new Error('unrelated cyclic failure')
    cyclic.cause = cyclic
    await lifecycle.settle([Promise.reject(cyclic)], failures)
    expect(failures).toEqual([cyclic])
  })

  it('disposes a quarantined child after its provisioning edge becomes failed', async () => {
    const { ctx, lead } = await setup(['hang'])
    const childId = SessionId('failed-live-child')
    const member = {
      id: childId,
      name: 'failed-live-worker',
      description: 'failed-live-worker responsibility',
      provider: 'spawn',
      context: 'fresh' as const,
      phase: 'provisioning' as const,
    }
    lead.session.append('team/member', {
      version: 2,
      teamId: TeamId(lead.id),
      member,
    })
    const reserved = await ctx.subagents.materializeContinuable({
      childId, provider: 'spawn', label: member.description, request: { parent: lead }, signal: SIGNAL,
    })
    await reserved.persistInitialPrompt(content('failed child task'), 'failed-live', SIGNAL)
    expect(() => { ctx.agentTeams.bindExecution(reserved.agent, {
      missionId: 'unapproved' as import('../src/index.ts').TeamMissionId, expectedRevision: 1,
    }) }).toThrow('canonical teammate is not active')
    expect(reserved.agent.status).toBe('idle')
    lead.session.append('team/member', {
      version: 2,
      teamId: TeamId(lead.id),
      member: {
        ...member,
        phase: 'failed',
        error: 'creation cleanup is pending',
      },
    })
    await ctx.sessions.flush(lead.session)
    expect(ctx.agentTeams.listMembers(lead)[1]?.status).toBe('failed')

    const internal = ctx.agentTeams as unknown as { disposeRuntime(): Promise<void> }
    await internal.disposeRuntime()
    expect(ctx.agents.get(childId)).toBeUndefined()
  })

  it('aborts and awaits an admitted explicitly recovered mailbox dispatch during disposal', async () => {
    const checkpoint = async <T>(label: string, operation: Promise<T>): Promise<T> => {
      let timer: ReturnType<typeof setTimeout> | undefined
      try {
        return await Promise.race([operation, new Promise<never>((_resolve, reject) => {
          timer = setTimeout(() => { reject(new Error(`Recovery disposal checkpoint timed out: ${label}`)) }, 1_000)
        })])
      } finally {
        clearTimeout(timer)
      }
    }
    const { ctx, lead } = await setup([textResponse('worker done'), 'hang', 'hang'])
    const started = await spawn(ctx, lead, 'mailbox-worker')
    await checkpoint('initial child settlement', waitNoAgent(ctx, started.member.id))
    const sending = await ctx.agentTeams.sendMessage(lead, {
      target: 'mailbox-worker',
      content: content('resume during disposal'),
      signal: SIGNAL,
    })
    expect(sending.status).toBe('queued')
    const entered = Promise.withResolvers<undefined>()
    const aborted = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    const lifecycle = (ctx.agentTeams as unknown as { lifecycle: TeamRuntimeLifecycle }).lifecycle
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    let blockDelivery = true
    vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
      const receipt = session.id === started.member.id && session.snapshotEvents().some(event =>
        event.type === 'agent/inbox/spliced' && event.data.inserted.some(message =>
          message.source.kind === 'team-message' && message.source.messageId === sending.messageId))
      if (!receipt || !blockDelivery) return flush(session)
      blockDelivery = false
      entered.resolve(undefined)
      return await new Promise<never>((_resolve, reject) => {
        lifecycle.signal.addEventListener('abort', () => {
          aborted.resolve(undefined)
          void release.promise.then(() => { reject(new Error('target receipt cancelled during disposal')) })
        }, { once: true })
      })
    })

    const recovered = await checkpoint('explicit child recovery', recoverFixtureMember(ctx, lead, 'mailbox-worker'))
    expect(ctx.agents.get(started.member.id)).toBe(recovered)
    const pending = durable(lead).pendingMessages.find(message => message.id === sending.messageId)!
    const dispatch = teamInternals(ctx).mailbox.tryDispatch(lead, pending, SIGNAL)
    await checkpoint('target receipt flush entry', entered.promise)
    expect(lifecycle.disposed).toBe(false)
    const mailbox = (ctx.agentTeams as unknown as { mailbox: { pendingDispatches(): readonly Promise<unknown>[] } }).mailbox
    expect(mailbox.pendingDispatches().length).toBeGreaterThan(0)
    const internal = ctx.agentTeams as unknown as { disposeRuntime(): Promise<void> }
    let disposed = false
    const disposal = internal.disposeRuntime().then(() => { disposed = true })
    await checkpoint('dispatch abort listener', aborted.promise)
    await Promise.resolve()
    expect(disposed).toBe(false)
    release.resolve(undefined)

    await expect(checkpoint('dispatch settlement', dispatch)).resolves.toBe(false)
    await checkpoint('disposal settlement', disposal)
    expect(disposed).toBe(true)
    expect(durable(lead).pendingMessages.map(message => message.id)).toContain(sending.messageId)
    expect(ctx.agents.get(started.member.id)).toBeUndefined()
  })

  it('awaits an admitted target receipt flush without publishing acknowledgement after withdrawal', async () => {
    const { ctx, lead } = await setup([])
    const message: TeamMessageSnapshot = {
      id: TeamMessageId('dispose-ack-message'),
      senderId: SessionId('sender'),
      senderName: 'sender',
      targetId: lead.id,
      content: content('acknowledge before disposal'),
    }
    lead.session.append('team/message/queued', {
      version: 2,
      teamId: TeamId(lead.id),
      message,
    })
    await ctx.sessions.flush(lead.session)

    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    const flush = ctx.sessions.flush.bind(ctx.sessions)
    let blockReceipt = true
    const flushSpy = vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
      if (blockReceipt && session === lead.session) {
        blockReceipt = false
        entered.resolve(undefined)
        await release.promise
      }
      return flush(session)
    })
    lead.session.append('user/message', createUserMessage({
      content: content('acknowledge before disposal'),
      source: {
        kind: 'team-message',
        teamId: TeamId(lead.id),
        messageId: message.id,
        senderId: message.senderId,
        senderName: message.senderName,
      },
    }), { surfaceOp: 'append' })

    const internal = ctx.agentTeams as unknown as { disposeRuntime(): Promise<void> }
    let disposed = false
    const disposal = internal.disposeRuntime().then(() => { disposed = true })
    await entered.promise
    await Promise.resolve()
    const disposedBeforeRelease = disposed
    release.resolve(undefined)
    await disposal

    expect(disposedBeforeRelease).toBe(false)
    expect(disposed).toBe(true)
    expect(durable(lead).pendingMessages.map(item => item.id)).toEqual([message.id])
    flushSpy.mockRestore()
  })

  it('bounds Team runtime disposal when a reserved physical cleanup never settles', { timeout: 30_000 }, async () => {
    const { ctx, lead, teamFiber } = await setup(['hang'], { disposalTimeoutMs: 25 })
    const materialize = ctx.subagents.materializeContinuable.bind(ctx.subagents)
    const dispose = vi.fn<() => Promise<void>>()
    let physicalDisposal: Promise<void> | undefined
    vi.spyOn(ctx.subagents, 'materializeContinuable').mockImplementationOnce(async (spec) => {
      const reserved = await materialize(spec)
      dispose.mockImplementation(() => {
        physicalDisposal = reserved.dispose()
        return new Promise(() => {})
      })
      return { ...reserved, dispose }
    })
    const started = await spawn(ctx, lead, 'stuck-worker')
    await waitRunning(ctx, started.member.id)
    const outcome = await Promise.race([
      teamFiber.dispose().then(() => 'disposed'),
      new Promise<'hung'>((resolve) => { setTimeout(() => { resolve('hung') }, 1_000) }),
    ])
    expect(outcome).toBe('disposed')
    expect(dispose).toHaveBeenCalled()
    await physicalDisposal
    expect(ctx.agents.get(started.member.id)).toBeUndefined()
    expect(ctx.get('agentTeams')).toBeUndefined()
  })

  it('bounds disposal while an admitted creation ignores cancellation', async () => {
    const { ctx, lead } = await setup([], { disposalTimeoutMs: 25 })
    const internal = teamInternals(ctx)
    internal.roster.inFlightCreations.add(new Promise(() => {}))

    await expect(internal.disposeRuntime()).rejects.toBeInstanceOf(AggregateError)
    await expect(ctx.agentTeams.spawnTeammate(lead, {
      name: 'after-timeout',
      description: 'admission remains closed',
      prompt: content('must reject'),
      context: 'fresh',
      provider: 'spawn',
      signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_DISPOSED' })
    await expect(ctx.agentTeams.sendMessage(lead, {
      target: 'nobody', content: content('must reject'), signal: SIGNAL,
    })).rejects.toMatchObject({ code: 'TEAM_DISPOSED' })
    await expect(internal.mailbox.tryDispatch(lead, {
      id: TeamMessageId('post-disposal-message'),
      senderId: lead.id,
      senderName: 'lead',
      targetId: lead.id,
      content: content('must not dispatch'),
    }, SIGNAL)).resolves.toBe(false)
  })

  it('contains recovery callback failures and ignores work scheduled after disposal', async () => {
    const { ctx, lead, teamFiber } = await setup([])
    const warnings: string[] = []
    ctx.logger.warn = ((value: unknown) => { warnings.push(String(value)) }) as typeof ctx.logger.warn
    const internal = teamInternals(ctx)
    internal.recoverFor = async () => { throw new Error('forced recovery failure') }
    internal.scheduleRecovery(lead)
    await Promise.resolve()
    await Promise.resolve()
    expect(warnings.some(warning => warning.includes('forced recovery failure'))).toBe(true)

    lead.session.append('user/message', createUserMessage({
      content: content('orphan Team source'),
      source: {
        kind: 'team-message',
        teamId: TeamId('absent-team'),
        messageId: TeamMessageId('absent-team-message'),
        senderId: SessionId('absent-sender'),
        senderName: 'absent',
      },
    }), { surfaceOp: 'append' })
    await Promise.resolve()

    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    internal.recoverFor = async () => {
      entered.resolve(undefined)
      await release.promise
      throw new Error('failure after disposal')
    }
    internal.scheduleRecovery(lead)
    await entered.promise
    await teamFiber.dispose()
    release.resolve(undefined)
    await Promise.resolve()
    await Promise.resolve()
    internal.scheduleRecovery(lead)
    await Promise.resolve()
  })

  it('reports contained teardown failures without retaining the Team service', async () => {
    const { ctx, lead, teamFiber } = await setup(['hang'])
    const started = await spawn(ctx, lead, 'failing-drain')
    await waitRunning(ctx, started.member.id)
    vi.spyOn(ctx.subagents, 'drainContinuableDescendants').mockRejectedValueOnce(new Error('drain failure'))

    await teamFiber.dispose()
    expect(ctx.get('agentTeams')).toBeUndefined()
  })

  it('reconciles mismatched persisted children and ignores a concurrently settled member', async () => {
    const first = await setup([])
    const liveId = SessionId('live-provisioning-child')
    const live = await first.ctx.agents.create({
      sessionId: liveId,
      meta: { parentSession: first.lead.id },
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    const provisioning = {
      id: liveId,
      name: 'mismatched-child',
      description: 'mismatched persisted child',
      provider: 'spawn',
      context: 'fresh' as const,
      phase: 'provisioning' as const,
    }
    first.lead.session.append('team/member', {
      version: 2, teamId: TeamId(first.lead.id), member: provisioning,
    })
    const reconcileFirst = teamInternals(first.ctx).roster
    await reconcileFirst.reconcileProvisioning(first.lead, SIGNAL)
    expect(durable(first.lead).members[0]?.phase).toBe('provisioning')
    live.agent.session.append('user/message', createUserMessage({
      content: content('persist mismatched child'), source: { kind: 'user' },
    }), { surfaceOp: 'append' })
    await first.ctx.sessions.flush(live.agent.session)
    await live.dispose()
    await reconcileFirst.reconcileProvisioning(first.lead, SIGNAL)
    expect(durable(first.lead).members[0]?.phase).toBe('failed')
    expect(durable(first.lead).members[0]?.error).toContain('child Session recovery failed:')

    const second = await setup([])
    const childId = SessionId('concurrently-settled-child')
    const member = { ...provisioning, id: childId, name: 'concurrent-child' }
    second.lead.session.append('team/member', {
      version: 2, teamId: TeamId(second.lead.id), member,
    })
    const entered = Promise.withResolvers<undefined>()
    const release = Promise.withResolvers<undefined>()
    vi.spyOn(second.ctx.sessionPersistence, 'open').mockImplementationOnce(async () => {
      entered.resolve(undefined)
      await release.promise
      throw new Error('late inspection failure')
    })
    const reconcileSecond = teamInternals(second.ctx).roster
    const reconciling = reconcileSecond.reconcileProvisioning(second.lead, SIGNAL)
    await entered.promise
    second.lead.session.append('team/member', {
      version: 2,
      teamId: TeamId(second.lead.id),
      member: { ...member, phase: 'failed', error: 'settled elsewhere' },
    })
    release.resolve(undefined)
    await reconciling
    expect(durable(second.lead).members[0]).toMatchObject({
      phase: 'failed', error: 'settled elsewhere',
    })
  })
})
