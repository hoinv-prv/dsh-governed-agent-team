/** Historical command regression fixtures use real HUMAN control before admitted execution. */
import type { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { TeamMissionId } from '../src/index.ts'
import type { CreateTeamTaskRequest, ReportTeamWorkRequest, SpawnTeammateRequest, TeamMissionView, UpdateTeamTaskRequest } from '../src/index.ts'
import { mountHumanControl } from './human-control-fixture.ts'

const controls = new WeakMap<Context, Awaited<ReturnType<typeof mountHumanControl>>>()
const missions = new WeakMap<Context, TeamMissionView>()

/** Mount signed-cookie ingress for a command regression fixture. */
export async function initializeAuthorizedFixture(ctx: Context): Promise<void> {
  const control = await mountHumanControl(ctx)
  controls.set(ctx.root, control)
  ctx.effect(() => () => control.close(), 'authorized-test-carrier')
}

/** Invoke one actual authenticated HUMAN control action and preserve business rejection. */
export async function humanAction(ctx: Context, caller: Agent, method: string, request?: unknown): Promise<unknown> {
  const control = controls.get(ctx.root)
  if (!control) throw new Error('HUMAN fixture not mounted')
  const transport = await control.call(method, caller.id, request)
  if (!transport.ok) throw new Error(`HUMAN transport rejected: ${JSON.stringify(transport.error)}`)
  const result = transport.value as { ok?: boolean; value?: unknown; error?: unknown }
  if (result?.ok === false) throw new Error(`HUMAN control rejected: ${JSON.stringify(result.error)}`)
  return result?.ok === true ? result.value : result
}

/** Select the named fixture mission explicitly; no production list/current inference is exercised. */
export async function fixtureMission(ctx: Context, caller: Agent): Promise<TeamMissionView> {
  const lead = ctx.root.agentTeams.membership(caller).root
  let mission = missions.get(ctx.root)
  if (!mission) {
    mission = await ctx.root.agentTeams.createMission(lead, { title: 'Regression fixture mission', objective: 'Explicit HUMAN-authorized historical command coverage' })
    missions.set(ctx.root, mission)
  }
  return ctx.root.agentTeams.getMission(lead, TeamMissionId(mission.id))
}

/** Approve only the fixture mission's displayed exact revision and bind the requested Agent. */
export async function authorizeFixtureAgent(ctx: Context, agent: Agent): Promise<TeamMissionView> {
  const lead = ctx.root.agentTeams.membership(agent).root
  let mission = await fixtureMission(ctx, lead)
  if (mission.status === 'draft') {
    await humanAction(ctx, lead, 'approveMission', { missionId: mission.id, expectedRevision: mission.revision })
    mission = ctx.root.agentTeams.getMission(lead, mission.id)
  }
  ctx.root.agentTeams.bindExecution(agent, { missionId: mission.id, expectedRevision: mission.revision })
  return mission
}

/** Create an explicitly associated task, then HUMAN-authorize the resulting exact structural revision. */
export async function authorizedTask(ctx: Context, caller: Agent, request: CreateTeamTaskRequest) {
  const mission = await fixtureMission(ctx, caller)
  const task = await ctx.root.agentTeams.createTask(caller, { ...request, missionId: request.missionId ?? mission.id })
  await authorizeFixtureAgent(ctx, caller)
  return task
}

/** Authorize the exact member spec, commit its quarantined child, then bind and activate that child explicitly. */
export async function authorizedSpawn(ctx: Context, caller: Agent, request: SpawnTeammateRequest, activate = true) {
  const { signal: _signal, ...spec } = request
  if (ctx.root.agentTeams.membership(caller).role !== 'lead') return ctx.root.agentTeams.spawnTeammate(caller, request)
  await humanAction(ctx, caller, 'approveMemberAdd', spec)
  const result = await ctx.root.agentTeams.spawnTeammate(caller, request)
  await authorizeFixtureAgent(ctx, caller)
  const child = ctx.agents.get(result.member.id)
  if (child) {
    await authorizeFixtureAgent(ctx, child)
    if (activate) await ctx.root.agentTeams.activateMember(child, request.signal)
  }
  return result
}

/** Supply an explicit host lease before exercising a legacy work semantic validation. */
export async function authorizedReport(ctx: Context, caller: Agent, request: ReportTeamWorkRequest) {
  await authorizeFixtureAgent(ctx, caller)
  if (request.taskId !== undefined) {
    const task = ctx.root.agentTeams.getTask(caller, request.taskId)
    if (task.missionId) ctx.root.agentTeams.bindExecution(caller, { missionId: task.missionId, expectedRevision: ctx.root.agentTeams.getMission(caller, task.missionId).revision, taskId: task.id })
  }
  return ctx.root.agentTeams.reportWork(caller, request)
}

/** Return the protected Remote's business result through actual authenticated ingress. */
export async function humanBusinessAction(ctx: Context, caller: Agent, method: string, request: unknown): Promise<unknown> {
  const control = controls.get(ctx.root)
  if (!control) throw new Error('HUMAN fixture not mounted')
  const transport = await control.call(method, caller.id, request)
  if (!transport.ok) throw new Error(`HUMAN transport rejected: ${JSON.stringify(transport.error)}`)
  return transport.value
}

/** Rebind explicit fixture scope after deliberate structure/owner changes in command regressions. */
export async function authorizedUpdate(ctx: Context, caller: Agent, request: UpdateTeamTaskRequest) {
  await authorizeFixtureAgent(ctx, caller)
  const task = ctx.root.agentTeams.listTasks(caller).find(value => value.id === request.taskId)
  if (task?.missionId && task.status === 'in_progress' && task.ownerName === ctx.root.agentTeams.membership(caller).name) {
    ctx.root.agentTeams.bindExecution(caller, { missionId: task.missionId, expectedRevision: ctx.root.agentTeams.getMission(caller, task.missionId).revision, taskId: task.id })
  }
  return ctx.root.agentTeams.updateTask(caller, request)
}

/** Explicit trusted host recovery of the named fixture member; mailbox queues never choose its mission. */
export async function recoverFixtureMember(ctx: Context, lead: Agent, name: string) {
  const mission = await authorizeFixtureAgent(ctx, lead)
  return ctx.root.agentTeams.recoverMember(lead, name, { missionId: mission.id, expectedRevision: mission.revision }, new AbortController().signal)
}
