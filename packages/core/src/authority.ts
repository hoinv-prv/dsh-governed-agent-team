/** Exact live Agent execution leases revalidated against the canonical Team projection. */
import type { Agent } from '@deepseek-ai/dsh-agent'
import { TeamError } from './error.ts'
import type { TeamJournal } from './journal.ts'
import type { TeamMembership } from './roster.ts'
import type { TeamMissionId, TeamTaskId } from './types.ts'

/** Host-selected authorization; model arguments never carry an execution lease. */
export interface BindTeamExecutionRequest {
  readonly missionId: TeamMissionId
  readonly expectedRevision: number
  readonly taskId?: TeamTaskId
}
interface ExecutionLease extends BindTeamExecutionRequest {
  readonly teamId: string
  readonly eventId: string
  readonly digest: string
  readonly issuanceGeneration: number
  readonly authorizationGeneration: number
  readonly revocationGeneration: number
  readonly planRevision?: number
  readonly planEventId?: string
}

/** Owns non-transferable Agent-generation leases and legacy plan policy. */
export class TeamExecutionAuthority {
  private readonly leases = new WeakMap<Agent, ExecutionLease>()
  private requirePlan = false
  private nextIssuanceGeneration = 1
  constructor(private readonly journal: TeamJournal) {}

  /**
   * Configure the additional exact HUMAN plan requirement for governed mode.
   * @param requirePlan Whether governed execution requires an exact current plan approval.
   */

  configure(requirePlan: boolean): void { this.requirePlan = requirePlan }

  /**
   * Bind exactly one host-selected or canonical task-derived authorized mission.
   * @param agent Live Agent generation whose authority is checked.
   * @param membership Current Team membership projection for the Agent.
   * @param request Host-selected mission approval or transition request.
   */

  bind(agent: Agent, membership: TeamMembership, request: BindTeamExecutionRequest): void {
    this.journal.assertCommitted(membership.root)
    this.assertActiveMember(agent, membership)
    const state = this.journal.state(membership.root)
    const mission = state.missions.find(value => value.id === request.missionId)
    const approval = mission?.approval
    if (!mission || mission.status !== 'approved' || mission.revision !== request.expectedRevision
      || approval?.approvedRevision !== mission.revision || !approval.eventId || !approval.digest || approval.humanSessionId !== state.id) {
      throw new TeamError('exact mission revision lacks current host-attested HUMAN authorization', 'TEAM_MISSION_UNAUTHORIZED')
    }
    if (request.taskId !== undefined) {
      const task = state.tasks.find(value => value.id === request.taskId)
      if (!task || task.status !== 'in_progress' || task.ownerId !== agent.id || task.missionId !== mission.id || !mission.plan.taskIds?.includes(task.id)) {
        throw new TeamError('canonical task mission association is missing or mismatched', 'TEAM_TASK_MISSION_REQUIRED')
      }
    }
    this.assertPlan(membership)
    this.leases.set(agent, Object.freeze({ ...request, teamId: state.id, eventId: approval.eventId, digest: approval.digest,
      issuanceGeneration: this.nextIssuanceGeneration++, authorizationGeneration: mission.authorizationGeneration ?? 0,
      revocationGeneration: mission.revocationGeneration ?? 0,
      ...this.requirePlan ? {
        planRevision: state.planRevision, planEventId: (state.planApproval as NonNullable<typeof state.planApproval>).eventId,
      } : {},
    }))
  }

  /**
   * Validate one explicit canonical claim without publishing any Agent execution lease.
   * @param agent Live Agent generation whose authority is checked.
   * @param membership Current Team membership projection for the Agent.
   * @param taskId Explicit canonical task identifier.
   */

  validateClaim(agent: Agent, membership: TeamMembership, taskId: TeamTaskId): void {
    this.journal.assertCommitted(membership.root)
    this.assertActiveMember(agent, membership)
    const state = this.journal.state(membership.root)
    const task = state.tasks.find(value => value.id === taskId)
    const mission = state.missions.find(value => value.id === task?.missionId)
    if (!task || !mission || !mission.plan.taskIds?.includes(task.id) || mission.status !== 'approved'
      || mission.approval?.approvedRevision !== mission.revision || !mission.approval.eventId || !mission.approval.digest
      || mission.approval.humanSessionId !== state.id) throw new TeamError('canonical claim mission lacks exact HUMAN approval', 'TEAM_MISSION_UNAUTHORIZED')
    this.assertPlan(membership)
  }

  /**
   * Admit Lead administration through its explicit host mission scope, or task work through its claimed scope.
   * @param agent Live Agent generation whose authority is checked.
   * @param membership Current Team membership projection for the Agent.
   * @param taskId Explicit canonical task identifier.
   */

  assertTaskOperation(agent: Agent, membership: TeamMembership, taskId: TeamTaskId): void {
    const lease = this.leases.get(agent)
    if (membership.role === 'lead' && lease?.taskId === undefined) {

      this.assert(agent, membership)
      const task = this.journal.state(membership.root).tasks.find(value => value.id === taskId)
      if (!task || task.missionId !== lease?.missionId) throw new TeamError('Lead task operation has a different canonical mission', 'TEAM_EXECUTION_DENIED')
      return
    }
    this.assert(agent, membership, taskId)
  }

  /**
   * Derive task admission only from one explicitly selected canonical task.
   * @param agent Live Agent generation whose authority is checked.
   * @param membership Current Team membership projection for the Agent.
   * @param taskId Explicit canonical task identifier.
   */

  bindTask(agent: Agent, membership: TeamMembership, taskId: TeamTaskId): void {
    this.journal.assertCommitted(membership.root)
    const state = this.journal.state(membership.root)
    const task = state.tasks.find(value => value.id === taskId)
    if (!task?.missionId) throw new TeamError('task has no canonical mission association', 'TEAM_TASK_MISSION_REQUIRED')
    const mission = state.missions.find(value => value.id === task.missionId)
    if (!mission) throw new TeamError('task mission is missing', 'TEAM_MISSION_UNAUTHORIZED')
    this.bind(agent, membership, { missionId: mission.id, expectedRevision: mission.revision, taskId })
  }

  /**
   * Revalidate the exact lease immediately before an effect or model request.
   * @param agent Live Agent generation whose authority is checked.
   * @param membership Current Team membership projection for the Agent.
   * @param taskId Explicit canonical task identifier.
   */
  assert(agent: Agent, membership: TeamMembership, taskId?: TeamTaskId): void {
    this.journal.assertCommitted(membership.root)
    this.assertActiveMember(agent, membership)
    const state = this.journal.state(membership.root)
    const lease = this.leases.get(agent)
    const mission = state.missions.find(value => value.id === lease?.missionId)
    if (!lease || lease.teamId !== state.id || !mission || mission.status !== 'approved'
      || lease.expectedRevision !== mission.revision || lease.eventId !== mission.approval?.eventId
      || lease.digest !== mission.approval.digest || lease.authorizationGeneration !== (mission.authorizationGeneration ?? 0)
      || lease.revocationGeneration !== (mission.revocationGeneration ?? 0)
      || mission.approval.approvedRevision !== mission.revision) {
      throw new TeamError('exact Agent mission lease is absent, stale, closed, or revoked', 'TEAM_EXECUTION_DENIED')
    }
    const selectedTask = taskId ?? lease.taskId
    if (taskId !== undefined && lease.taskId !== taskId) throw new TeamError('execution lease is bound to a different task', 'TEAM_EXECUTION_DENIED')
    if (selectedTask !== undefined) {
      const task = state.tasks.find(value => value.id === selectedTask)
      if (!task || task.status !== 'in_progress' || task.ownerId !== agent.id || task.missionId !== mission.id || !mission.plan.taskIds?.includes(task.id)) {
        throw new TeamError('execution lease canonical task association or owner changed', 'TEAM_EXECUTION_DENIED')
      }
    }
    this.assertPlan(membership)
    if (this.requirePlan && (lease.planRevision !== state.planRevision || lease.planEventId !== state.planApproval?.eventId)) {
      throw new TeamError('exact Agent current-plan lease is absent or stale', 'TEAM_PLAN_UNAUTHORIZED')
    }
  }

  private assertPlan(membership: TeamMembership): void {
    this.journal.assertCommitted(membership.root)
    const state = this.journal.state(membership.root)
    if (this.requirePlan && (state.planPhase !== 'approved' || state.planApproval?.approvedRevision !== state.planRevision
      || !state.planApproval.eventId || !state.planApproval.digest || state.planApproval.humanSessionId !== state.id)) {
      throw new TeamError('current Team plan lacks exact host-attested HUMAN approval', 'TEAM_PLAN_UNAUTHORIZED')
    }
  }

  private assertActiveMember(agent: Agent, membership: TeamMembership): void {
    if (membership.role !== 'teammate') return
    const member = this.journal.state(membership.root).members.find(value => value.id === agent.id)
    if (member?.phase !== 'active') throw new TeamError('canonical teammate is not active for execution', 'TEAM_EXECUTION_DENIED')
  }
}
