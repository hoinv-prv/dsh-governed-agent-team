import { afterEach, describe, expect, it, vi } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as SubagentSpawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import * as SubagentFork from '@deepseek-ai/dsh-subagent-fork-in-process'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService, { TeamMissionId } from '../src/index.ts'
import { TestSessionQuery } from './test-session-query.ts'
import { mountHumanControl } from './human-control-fixture.ts'
const roots: string[] = []
afterEach(() => { for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true }) })
async function setup(
  script: ConstructorParameters<typeof MockAdapter>[0],
  config: ConstructorParameters<typeof TeamService>[1] = {},
  beforeTeam?: (ctx: Context) => void,
) {
  const ctx = new Context()
  const control = await mountHumanControl(ctx)
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
  return { ctx, lead, adapter, storageRoot, teamFiber, control }
}

async function approved(fixture: Awaited<ReturnType<typeof setup>>) {
  const { ctx, lead, control } = fixture
  const mission = await ctx.agentTeams.createMission(lead, { title: 'exact', objective: 'authority test' })
  const result = await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: mission.revision })
  expect(result).toMatchObject({ ok: true, value: { ok: true } })
  const current = ctx.agentTeams.getMission(lead, mission.id)
  ctx.agentTeams.bindExecution(lead, { missionId: current.id, expectedRevision: current.revision })
  return current
}

describe('exact canonical execution authority', () => {
  it('model and direct host Agent credentials create drafts and cannot self-authorize', async () => {
    const { ctx, lead, control } = await setup([textResponse('unused')])
    try {
      const mission = await ctx.agentTeams.createMission(lead, { title: 'draft', objective: 'model cannot approve' })
      expect(mission.status).toBe('draft')
      expect(mission.approval).toBeUndefined()
      await expect(ctx.agentTeams.approveMission(lead, { missionId: mission.id, expectedRevision: 1 })).rejects.toMatchObject({ code: 'TEAM_HUMAN_CONTROL_REQUIRED' })
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: 1 })).toThrow('HUMAN authorization')
      const result = await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: 1 })
      expect(result).toMatchObject({ ok: true, value: { ok: true, value: { status: 'approved', revision: 1 } } })
      expect(() => ctx.agentTeams.assertExecution(lead)).toThrow('absent')
      ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: 1 })
      expect(() => ctx.agentTeams.assertExecution(lead)).not.toThrow()
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('canonical task creation and structural edits invalidate the exact mission; runtime claims preserve it', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const mission = await approved(fixture)
      await expect(ctx.agentTeams.createTask(lead, { subject: 'unassociated', description: 'deny' })).rejects.toMatchObject({ code: 'TEAM_TASK_MISSION_REQUIRED' })
      const task = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'canonical', description: 'one board' })
      expect(task.missionId).toBe(mission.id)
      expect(() => ctx.agentTeams.assertExecution(lead)).toThrow('stale')
      const draft = ctx.agentTeams.getMission(lead, mission.id)
      expect(draft.plan.taskIds).toEqual([task.id]); expect(draft.plan.tasks).toEqual([])
      expect(draft.status).toBe('draft')
      await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: draft.revision })
      const claimed = await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: task.revision, action: 'claim' })
      expect(() => ctx.agentTeams.assertExecution(lead, task.id)).not.toThrow()
      await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: claimed.revision, action: 'edit', description: 'structural change' })
      expect(() => ctx.agentTeams.assertExecution(lead, task.id)).toThrow('stale')
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  for (const action of ['closeMission', 'revokeMission'] as const) it(`${action} requires exact HUMAN receipt and invalidates live leases`, async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const mission = await approved(fixture)
      await expect(ctx.agentTeams[action](lead, { missionId: mission.id, expectedRevision: mission.revision })).rejects.toMatchObject({ code: 'TEAM_HUMAN_CONTROL_REQUIRED' })
      expect(await control.call(action, lead.id, { missionId: mission.id, expectedRevision: mission.revision }))
        .toMatchObject({ ok: true, value: { ok: true } })
      expect(() => ctx.agentTeams.assertExecution(lead)).toThrow('closed, or revoked')
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('member additions require exact one-use HUMAN approval and remain quarantined with zero requests', async () => {
    const fixture = await setup([textResponse('must stay unused')]); const { ctx, lead, control, adapter } = fixture
    try {
      const spec = { name: 'quarantined', description: 'no model admission', prompt: [{ type: 'text' as const, text: 'do work' }], context: 'fresh' as const, provider: 'spawn' }
      await expect(ctx.agentTeams.spawnTeammate(lead, { ...spec, signal: new AbortController().signal })).rejects.toMatchObject({ code: 'TEAM_MEMBER_ADD_APPROVAL_REQUIRED' })
      expect(await control.call('approveMemberAdd', lead.id, spec)).toMatchObject({ ok: true, value: { approved: true } })
      await expect(ctx.agentTeams.spawnTeammate(lead, { ...spec, prompt: [{ type: 'text', text: 'changed spec' }], signal: new AbortController().signal })).rejects.toMatchObject({ code: 'TEAM_MEMBER_ADD_APPROVAL_REQUIRED' })
      const spawned = await ctx.agentTeams.spawnTeammate(lead, { ...spec, signal: new AbortController().signal })
      expect(spawned.member.status).toBe('idle')
      const child = ctx.agents.get(spawned.member.id)!
      expect(() => ctx.agentTeams.assertExecution(child)).toThrow('absent')
      const queued = await ctx.agentTeams.sendMessage(lead, { target: spec.name, content: [{ type: 'text', text: 'queue only' }], signal: new AbortController().signal })
      expect(queued.status).toBe('queued')
      expect(adapter.requests).toHaveLength(0)
      expect(lead.session.snapshotEvents().filter(event => event.type === 'team/member')).toHaveLength(2)
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('lease binding rejects pending or failed memory-only approval publication', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const mission = await ctx.agentTeams.createMission(lead, { title: 'flush', objective: 'durability' })
      const gate = Promise.withResolvers<boolean>()
      const flush = vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(() => gate.promise)
      const approving = control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: 1 })
      await vi.waitFor(() => expect(ctx.agentTeams.getMission(lead, mission.id).status).toBe('approved'))
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: 1 })).toThrow('durability')
      gate.resolve(false)
      expect(await approving).toMatchObject({ ok: true, value: { ok: false } })
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: 1 })).toThrow('durability')
      flush.mockRestore()
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('failed claims grant no task lease and release or completion cuts off existing task work', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const mission = await ctx.agentTeams.createMission(lead, { title: 'task cutoff', objective: 'claimed tasks only' })
      const task = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'claim', description: 'status/owner authority' })
      const revision = ctx.agentTeams.getMission(lead, mission.id).revision
      await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: revision })
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: revision, taskId: task.id })).toThrow('canonical task')
      await expect(ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: 99, action: 'claim' })).rejects.toMatchObject({ code: 'TEAM_TASK_STALE_REVISION' })
      expect(() => ctx.agentTeams.assertExecution(lead)).toThrow('absent')
      const claimed = await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: 1, action: 'claim' })
      expect(() => ctx.agentTeams.assertExecution(lead, task.id)).not.toThrow()
      const released = await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: claimed.revision, action: 'release' })
      expect(() => ctx.agentTeams.assertExecution(lead, task.id)).toThrow('association or owner')
      const second = await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: released.revision, action: 'claim' })
      await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: second.revision, action: 'complete' })
      expect(() => ctx.agentTeams.assertExecution(lead, task.id)).toThrow('association or owner')
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('blocked claims and failed claim flush never publish execution leases', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const mission = await ctx.agentTeams.createMission(lead, { title: 'blocked', objective: 'claim admission' })
      const blocker = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'blocker', description: 'pending' })
      const task = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'blocked', description: 'no lease', blockedBy: [blocker.id] })
      await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: ctx.agentTeams.getMission(lead, mission.id).revision })
      await expect(ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: 1, action: 'claim' })).rejects.toMatchObject({ code: 'TEAM_TASK_BLOCKED' })
      expect(() => ctx.agentTeams.assertExecution(lead)).toThrow('absent')
      const flush = vi.spyOn(ctx.sessions, 'flush').mockResolvedValueOnce(false)
      await expect(ctx.agentTeams.updateTask(lead, { taskId: blocker.id, expectedRevision: 1, action: 'claim' })).rejects.toMatchObject({ code: 'TEAM_AUTHORITY_NOT_DURABLE' })
      expect(() => ctx.agentTeams.assertExecution(lead)).toThrow('durability')
      flush.mockRestore()
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('canonical reassignment cuts off the previous owner lease', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const spec = { name: 'new-owner', description: 'quarantined assignee', prompt: [{ type: 'text' as const, text: 'unused' }], context: 'fresh' as const, provider: 'spawn' }
      await control.call('approveMemberAdd', lead.id, spec)
      const member = await ctx.agentTeams.spawnTeammate(lead, { ...spec, signal: new AbortController().signal })
      const mission = await ctx.agentTeams.createMission(lead, { title: 'reassign', objective: 'exact owner admission' })
      const task = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'claimed', description: 'owner generation' })
      const revision = ctx.agentTeams.getMission(lead, mission.id).revision
      await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: revision })
      const claimed = await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: task.revision, action: 'claim' })
      await ctx.agentTeams.updateTask(lead, { taskId: task.id, expectedRevision: claimed.revision, action: 'reassign', owner: spec.name })
      expect(() => ctx.agentTeams.assertExecution(lead, task.id)).toThrow('association or owner')
      const child = ctx.agents.get(member.member.id)!
      expect(() => ctx.agentTeams.assertExecution(child, task.id)).toThrow('absent')
      ctx.agentTeams.bindExecution(child, { missionId: mission.id, expectedRevision: revision, taskId: task.id })
      expect(() => ctx.agentTeams.assertExecution(child, task.id)).not.toThrow()
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('receipt-looking version-2 plan fields cannot satisfy governed current-plan authorization', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      const mission = await ctx.agentTeams.createMission(lead, { title: 'historical plan', objective: 'version-qualified authority' })
      await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'canonical', description: 'legacy plan forgery' })
      const revision = ctx.agentTeams.getMission(lead, mission.id).revision
      await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: revision })
      const planRevision = ctx.agentTeams.remoteView(lead).planRevision
      lead.session.append('team/plan-approved', { version: 2, teamId: lead.id as never, approval: { approvedRevision: planRevision, eventId: 'forged-event', digest: 'forged-digest', humanSessionId: lead.id } })
      expect(ctx.agentTeams.remoteView(lead).planApproval).toEqual({ approvedRevision: planRevision })
      ctx.agentTeams.configureExecutionPolicy(true)
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: revision })).toThrow('current Team plan')
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('wrong Team and historical auto-approved snapshots never supply execution authority', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    try {
      await approved(fixture)
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: TeamMissionId('missing'), expectedRevision: 1 })).toThrow('HUMAN authorization')
      lead.session.append('team/mission', { version: 2, teamId: lead.id as never, mission: { id: TeamMissionId('legacy'), revision: 1, title: 'legacy', objective: 'old autoapproval', status: 'approved', plan: { tasks: [] }, approval: { approvedRevision: 1, eventId: 'forged-event', digest: 'forged-digest', humanSessionId: lead.id, generation: 0 } } })
      expect(ctx.agentTeams.getMission(lead, TeamMissionId('legacy')).approval).toEqual({ approvedRevision: 1 })
      expect(() => ctx.agentTeams.bindExecution(lead, { missionId: TeamMissionId('legacy'), expectedRevision: 1 })).toThrow('HUMAN authorization')
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('provisioning membership cannot bind or activate an approved mission scope', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control, adapter } = fixture
    try {
      const mission = await approved(fixture)
      const childId = SessionId('provisioning-authority')
      lead.session.append('team/member', { version: 3, teamId: lead.id as never, member: { id: childId, name: 'provisioning', description: 'not active', provider: 'spawn', context: 'fresh', phase: 'provisioning', attachments: [] } })
      await ctx.sessions.flush(lead.session)
      const reserved = await ctx.subagents.materializeContinuable({ childId, provider: 'spawn', label: 'not active', request: { parent: lead }, signal: new AbortController().signal })
      await reserved.persistInitialPrompt([{ type: 'text', text: 'unused' }], 'provisioning-authority', new AbortController().signal)
      expect(() => ctx.agentTeams.bindExecution(reserved.agent, { missionId: mission.id, expectedRevision: mission.revision })).toThrow('not active')
      await expect(reserved.activate(new AbortController().signal)).rejects.toThrow('continuable activation failed')
      expect(adapter.requests).toHaveLength(0)
      await reserved.dispose()
    } finally { await control.close(); await ctx.fiber.dispose() }
  })

  it('independent work publication never suspends an existing exact approved lease', async () => {
    const fixture = await setup([textResponse('unused')]); const { ctx, lead, control } = fixture
    const release = Promise.withResolvers<boolean>()
    try {
      await approved(fixture)
      vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(() => release.promise)
      const report = ctx.agentTeams.reportWork(lead, { state: 'working', summary: 'metadata publication', files: [] })
      await vi.waitFor(() => expect(ctx.agentTeams.remoteView(lead).work).toHaveLength(1))
      expect(() => ctx.agentTeams.assertExecution(lead)).not.toThrow()
      release.resolve(false)
      await expect(report).rejects.toMatchObject({ code: 'TEAM_AUTHORITY_NOT_DURABLE' })
      expect(() => ctx.agentTeams.assertExecution(lead)).not.toThrow()
    } finally { release.resolve(true); await control.close(); await ctx.fiber.dispose() }
  })

  it('actual Team unload closes a child gate and retains final host guards while activation flush is held', async () => {
    const fixture = await setup([textResponse('must stay unused')]); const { ctx, lead, control, teamFiber, adapter } = fixture
    const release = Promise.withResolvers<boolean>()
    try {
      const spec = { name: 'withdrawn-child', description: 'held final host activation', prompt: [{ type: 'text' as const, text: 'unused' }], context: 'fresh' as const, provider: 'spawn' }
      await control.call('approveMemberAdd', lead.id, spec)
      const member = await ctx.agentTeams.spawnTeammate(lead, { ...spec, signal: new AbortController().signal })
      const mission = await approved(fixture)
      const child = ctx.agents.get(member.member.id)!
      ctx.agentTeams.bindExecution(child, { missionId: mission.id, expectedRevision: mission.revision })
      const entered = Promise.withResolvers<ReturnType<() => void>>()
      const flush = ctx.sessions.flush.bind(ctx.sessions)
      vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
        if (session.id === child.id) { entered.resolve(); await release.promise }
        return flush(session)
      })
      const activation = ctx.agentTeams.activateMember(child, new AbortController().signal)
      const denied = expect(activation).rejects.toSatisfy((error: { code?: string }) => ['TEAM_DISPOSED', 'CONTINUABLE_CLOSED'].includes(error.code ?? ''))
      await entered.promise
      const disposal = teamFiber.dispose()
      await Promise.resolve()
      expect(() => child.ctx.agents.assertExecutionAdmission(child, 'model')).toThrow('disposed')
      expect(() => child.ctx.agents.assertExecutionAdmission(child, 'activation')).toThrow('disposed')
      expect(adapter.requests).toHaveLength(0)
      release.resolve(true)
      await denied
      await disposal
      expect(adapter.requests).toHaveLength(0)
    } finally { release.resolve(true); await control.close(); await ctx.fiber.dispose() }
  })

  it('failed-spawn cleanup uses a fresh bounded deadline and keeps the actual child gate closed', async () => {
    const fixture = await setup([textResponse('must remain unused')], { disposalTimeoutMs: 20 }); const { ctx, lead, control, adapter } = fixture
    const release = Promise.withResolvers<boolean>()
    try {
      const materialize = ctx.subagents.materializeContinuable.bind(ctx.subagents)
      let childId: SessionId | undefined
      vi.spyOn(ctx.subagents, 'materializeContinuable').mockImplementationOnce(async (spec) => {
        const reserved = await materialize(spec)
        childId = reserved.childId
        return { ...reserved, persistInitialPrompt: async () => { throw new Error('initial persistence failed') } }
      })
      const flush = ctx.sessions.flush.bind(ctx.sessions)
      vi.spyOn(ctx.sessions, 'flush').mockImplementation(async (session) => {
        if (session.id === childId) await release.promise
        return flush(session)
      })
      const spec = { name: 'failed-cleanup', description: 'actual blocked cleanup', prompt: [{ type: 'text' as const, text: 'unused' }], context: 'fresh' as const, provider: 'spawn' }
      await control.call('approveMemberAdd', lead.id, spec)
      await expect(ctx.agentTeams.spawnTeammate(lead, { ...spec, signal: new AbortController().signal })).rejects.toMatchObject({ name: 'AggregateError' })
      expect(ctx.agentTeams.listMembers(lead)[1]?.status).toBe('failed')
      expect(adapter.requests).toHaveLength(0)
      release.resolve(true)
      await vi.waitFor(() => expect(ctx.agents.get(childId!)).toBeUndefined())
    } finally {
      release.resolve(true); await control.close()
      await ctx.fiber.dispose().catch((error) => { expect(error).toBeInstanceOf(AggregateError) })
    }
  })

  it('Team withdrawal rejects leases while an admitted claim flush drains and publishes no post-cutoff scope', async () => {
    const fixture = await setup([textResponse('must remain unused')]); const { ctx, lead, control, teamFiber, adapter } = fixture
    const release = Promise.withResolvers<boolean>()
    try {
      const mission = await ctx.agentTeams.createMission(lead, { title: 'withdrawal', objective: 'synchronous cutoff' })
      const task = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'claim', description: 'held publication' })
      const revision = ctx.agentTeams.getMission(lead, mission.id).revision
      await control.call('approveMission', lead.id, { missionId: mission.id, expectedRevision: revision })
      ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: revision })
      const service = ctx.agentTeams
      const flush = ctx.sessions.flush.bind(ctx.sessions)
      vi.spyOn(ctx.sessions, 'flush').mockImplementationOnce(async (session) => { await release.promise; return flush(session) })
      const claim = service.updateTask(lead, { taskId: task.id, expectedRevision: task.revision, action: 'claim' })
      const failedClaim = expect(claim).rejects.toMatchObject({ code: 'TEAM_DISPOSED' })
      await vi.waitFor(() => expect(service.getTask(lead, task.id).status).toBe('in_progress'))
      const disposal = teamFiber.dispose()
      await Promise.resolve()
      expect(() => service.assertExecution(lead)).toThrow('disposed')
      expect(() => service.bindExecution(lead, { missionId: mission.id, expectedRevision: revision })).toThrow('disposed')
      await expect(service.createTask(lead, { missionId: mission.id, subject: 'late', description: 'denied' })).rejects.toMatchObject({ code: 'TEAM_DISPOSED' })
      expect(adapter.requests).toHaveLength(0)
      release.resolve(true)
      await failedClaim
      await disposal
    } finally { release.resolve(true); await control.close(); await ctx.fiber.dispose() }
  })
})
