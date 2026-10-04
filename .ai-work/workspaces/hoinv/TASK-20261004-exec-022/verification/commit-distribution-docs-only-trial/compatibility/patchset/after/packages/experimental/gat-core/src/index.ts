/** Agent Teams service façade over roster, mailbox, task, and runtime lifecycle owners. */

import { Context } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type {} from '@deepseek-ai/dsh-session-persistence'
import { Remote, TypertRemoteService } from '@deepseek-ai/dsh-typert-protocol'
import { approvedPlanTaskSubjects } from './approved-plan-import.ts'
import { consumeHumanControl } from '@deepseek-ai/dsh-client-connection'
import { TeamExecutionAuthority } from './authority.ts'
import type { BindTeamExecutionRequest } from './authority.ts'
import { TeamActivity } from './activity.ts'
import { errorMessage, TeamError } from './error.ts'
import { TeamJournal } from './journal.ts'
import { TeamRuntimeLifecycle } from './lifecycle.ts'
import { TeamMailbox } from './mailbox.ts'
import { TeamMissionBoard } from './mission-board.ts'
import { teamProjectionDefinition, validateInitialTask } from './projection.ts'
import type { TeamState } from './projection.ts'
import { TeamRoster } from './roster.ts'
import type { TeamMembership } from './roster.ts'
import { TeamTaskBoard } from './task-board.ts'
import { TeamWorkBoard } from './work-state.ts'
import { canonicalJson, payloadSha256 } from './attachments.ts'
import { TeamId, TeamMissionId, TeamTaskId } from './types.ts'
import { validateAttachmentRequests } from './attachments.ts'
import { requiredText } from './validation.ts'
import { abortPrepared } from './member-binders.ts'
import type { TeamMemberBinder } from './member-binders.ts'
import type {
  ApproveTeamMemberAddRequest,
  ApproveTeamMissionRequest,
  ApproveTeamPlanRequest,
  Config,
  CreateTeamMissionRequest,
  ImportApprovedTeamPlanResult,
  CreateTeamTaskRequest,
  ReportTeamWorkRequest,
  SendTeamMessageRequest,
  SendTeamMessageResult,
  SpawnTeammateRequest,
  SpawnTeammateResult,
  TeamEnableResult,
  TeamInitializer,
  TeamInitialization,
  TeamMemberView,
  TeamMemberSpec,
  TeamMissionMutationResult,
  TeamMissionView,
  TeamPlanApprovalResult,
  TeamPlanApprovalSnapshot,
  TeamTaskMutationResult,
  TeamTaskView,
  TeamView,
  TeamWaitResult,
  TeamWorkMutationResult,
  TeamWorkView,
  UpdateTeamTaskRequest,
} from './types.ts'

export type * from './types.ts'
export type { BindTeamExecutionRequest } from './authority.ts'
export type { TeamMembership } from './roster.ts'
export { TeamId, TeamMissionId, TeamMessageId, TeamTaskId } from './types.ts'
export { TeamError } from './error.ts'
export { scopesOverlap } from './task-board.ts'
export { ATTACHMENT_LIMITS, canonicalJson, payloadSha256, attachmentRecord, validateAttachmentRequests, validateAttachmentRecords } from './attachments.ts'
export { TeamMemberBinderRegistry, PreparedMemberAttachment, prepareMembers, abortPrepared } from './member-binders.ts'
export type * from './member-binders.ts'
export { BoundMemberRuntime, MemberBindingOwner, provisionPreparedMember, recoverBoundMember, BindingDeadline } from './member-binding.ts'
export type * from './member-binding.ts'

declare module '@deepseek-ai/cordis' {
  interface Context {
    agentTeams: TeamService
  }
}

const DEFAULT_MAX_MEMBERS = 8
const DEFAULT_MAX_TASKS = 256
const DEFAULT_MAX_PENDING_MESSAGES = 64
const DEFAULT_MAX_MESSAGE_BYTES = 65_536
const DEFAULT_DISPOSAL_TIMEOUT_MS = 5_000

/** Validate one positive safe-integer deployment limit. */
function positiveLimit(name: string, value: number): number {
  if (!Number.isSafeInteger(value) || value < 1) {
    throw new TeamError(`${name} must be a positive safe integer`, 'TEAM_INVALID_CONFIG')
  }
  return value
}

/** Agent Teams service backed by the exact live Lead Session log. */
export class TeamService extends TypertRemoteService {
  static inject = ['agents', 'sessions', 'sessionPersistence', 'sessionProjections', 'subagents', 'llm']

  static Config: z<Config> = z.object({
    maxMembers: z.number().step(1).min(1).default(DEFAULT_MAX_MEMBERS),
    maxTasks: z.number().step(1).min(1).default(DEFAULT_MAX_TASKS),
    maxPendingMessagesPerMember: z.number().step(1).min(1).default(DEFAULT_MAX_PENDING_MESSAGES),
    maxMessageBytes: z.number().step(1).min(1).default(DEFAULT_MAX_MESSAGE_BYTES),
    disposalTimeoutMs: z.number().step(1).min(1).default(DEFAULT_DISPOSAL_TIMEOUT_MS),
  })

  /** Validated deployment limits used by every Team operation. */
  private readonly config: Required<Config>

  private readonly activity: TeamActivity
  private readonly lifecycle: TeamRuntimeLifecycle
  private readonly journal: TeamJournal
  private readonly roster: TeamRoster
  private readonly mailbox: TeamMailbox
  private readonly authority: TeamExecutionAuthority
  private readonly missions: TeamMissionBoard
  private readonly tasks: TeamTaskBoard
  private readonly work: TeamWorkBoard
  private readonly approvalPreflights = new Set<(caller: Agent, view: TeamView) => readonly string[]>()
  private readonly memberAddGrants = new WeakMap<Agent, Set<string>>()
  private readonly initializers = new Set<TeamInitializer>()
  private readonly enabling = new WeakMap<Agent, Promise<TeamEnableResult>>()

  constructor(ctx: Context, config: Config = {}) {
    super(ctx, 'agentTeams')
    this.config = {
      maxMembers: positiveLimit('maxMembers', config.maxMembers ?? DEFAULT_MAX_MEMBERS),
      maxTasks: positiveLimit('maxTasks', config.maxTasks ?? DEFAULT_MAX_TASKS),
      maxPendingMessagesPerMember: positiveLimit(
        'maxPendingMessagesPerMember',
        config.maxPendingMessagesPerMember ?? DEFAULT_MAX_PENDING_MESSAGES,
      ),
      maxMessageBytes: positiveLimit('maxMessageBytes', config.maxMessageBytes ?? DEFAULT_MAX_MESSAGE_BYTES),
      disposalTimeoutMs: positiveLimit(
        'disposalTimeoutMs',
        config.disposalTimeoutMs ?? DEFAULT_DISPOSAL_TIMEOUT_MS,
      ),
    }

    this.activity = new TeamActivity()
    this.lifecycle = new TeamRuntimeLifecycle(this.config.disposalTimeoutMs)
    this.journal = new TeamJournal(ctx, (root) => { this.activity.notify(TeamId(root.id)) }, () => { this.lifecycle.assertOpen() })
    this.authority = new TeamExecutionAuthority(this.journal)
    this.roster = new TeamRoster(ctx, this.journal, this.lifecycle, this.config.maxMembers,
      (agent) => { this.assertExecution(agent) }, (caller, request) => { this.consumeMemberAdd(caller, request) },
      (agent) => { this.authority.assert(agent, this.roster.membership(agent)) })
    this.mailbox = new TeamMailbox(
      ctx,
      this.journal,
      this.roster,
      this.lifecycle,
      this.config.maxPendingMessagesPerMember,
      this.config.maxMessageBytes,
      (agent) => { this.assertExecution(agent) },
    )
    this.missions = new TeamMissionBoard(this.journal)
    this.tasks = new TeamTaskBoard(this.journal, this.config.maxTasks,
      (caller, taskId) => { this.authority.assertTaskOperation(caller, this.roster.membership(caller), taskId) },
      (caller, _membership, taskId) => { this.authority.validateClaim(caller, this.roster.membership(caller), taskId) },
      (caller, _membership, taskId) => { this.authority.bindTask(caller, this.roster.membership(caller), taskId) })
    this.work = new TeamWorkBoard(this.journal, (caller, taskId) => { this.assertExecution(caller, taskId) })

    ctx.effect(() => {
      const disposeProjection = ctx.root.sessionProjections.register(teamProjectionDefinition)
      return async () => {
        try {
          await this.disposeRuntime()
        } finally {
          disposeProjection()
        }
      }
    }, 'agentTeams.runtimeLifecycle()')

    const guardedAgents = new WeakSet<Agent>()
    const installExecutionGuard = (agent: Agent): void => {
      if (guardedAgents.has(agent)) return
      guardedAgents.add(agent)
      const initialMembership = this.roster.tryMembership(agent)
      let executionRequired = initialMembership !== undefined && this.journal.state(initialMembership.root).members.length > 0
      ctx.effect(() => {
        const removeGuard = agent.ctx.agents.guardExecution(agent, () => {
          const membership = this.roster.tryMembership(agent)
          const parentId = agent.session.header.parentSession
          const parent = parentId === undefined ? undefined : this.ctx.agents.get(parentId)
          const rostered = parent !== undefined && this.journal.state(parent).members.some(member => member.id === agent.id)
          if (rostered || membership && this.journal.state(membership.root).members.length > 0) executionRequired = true
          if (executionRequired) this.assertExecution(agent)
          return undefined
        })
        return async () => {
          this.lifecycle.close()
          try { await this.disposeRuntime() } finally { removeGuard() }
        }
      }, 'agentTeams.exactExecutionAdmission()')
    }
    ctx.on('agent/created', ({ agent }) => { installExecutionGuard(agent) })
    for (const agent of ctx.agents.list()) installExecutionGuard(agent)
    ctx.on('agent/prepare-prompt', ({ agent }) => {
      const membership = this.roster.tryMembership(agent)
      if (membership && this.journal.state(membership.root).members.length > 0) this.assertExecution(agent)
      return Promise.resolve()
    })
    ctx.on('agent/model-admission', ({ agent }) => {
      const membership = this.roster.tryMembership(agent)
      if (membership && this.journal.state(membership.root).members.length > 0) this.assertExecution(agent)
      return Promise.resolve()
    })
    ctx.on('session/event', (session, event) => { this.mailbox.observeSessionEvent(session, event) })
    ctx.on('agent/session-start', ({ agent }) => { this.scheduleRecovery(agent) })
    ctx.on('agent/disposed', ({ agent }) => { this.roster.disposedAgent(agent) })
    ctx.on('agent/status', ({ agent }) => {
      const membership = this.roster.tryMembership(agent)
      if (membership !== undefined) this.activity.notify(membership.id)
    })

    for (const agent of ctx.agents.list()) this.scheduleRecovery(agent)
  }

  /**
   * Set the additional exact HUMAN current-plan requirement for non-simple mode.
   * @param requireCurrentPlan - whether admission additionally requires the exact current HUMAN-approved Team plan.
   */
  configureExecutionPolicy(requireCurrentPlan: boolean): void { this.authority.configure(requireCurrentPlan) }

  /**
   * Host-only binding of an opaque lease to the exact live Agent generation.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - explicit mission identity/revision and optional claimed task selected by trusted host code.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  bindExecution(caller: Agent, request: BindTeamExecutionRequest): void {
    this.roster.assertBindings(caller)
    this.authority.bind(caller, this.roster.membership(caller), request)
  }

  /**
   * Revalidate exact canonical mission and task authorization before execution.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param taskId - optional exact claimed canonical task to revalidate.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  assertExecution(caller: Agent, taskId?: TeamTaskId): void {
    this.roster.assertBindings(caller)
    this.authority.assert(caller, this.roster.membership(caller), taskId)
  }

  /**
   * Release one prepared member initial item after its host-selected exact lease is bound.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param signal - cancellation checked before admission and during host preparation.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async activateMember(caller: Agent, signal: AbortSignal): Promise<void> {
    await this.lifecycle.admitMutation(async () => {
      const combined = AbortSignal.any([signal, this.lifecycle.signal])
      this.assertExecution(caller)
      const membership = this.roster.membership(caller)
      const requiresBindings = this.journal.state(membership.root).members.some(member =>
        member.id === caller.id && member.attachments.length > 0)
      if (requiresBindings && await this.roster.initialInputConsumed(caller, combined)) {
        const staged = await this.mailbox.stageRecoveryFor(caller, combined)
        // Keep a consumed, empty generation quarantined.
        if (staged === 0 && caller.inbox.nextTurn.length === 0 && caller.inbox.nextStep.length === 0) return
      }
      this.assertExecution(caller)
      await this.roster.activateMember(caller, combined)
      if (requiresBindings) await this.mailbox.recoverFor(caller, combined)
    })
  }

  /**
   * Cold-recover one explicitly selected member and bind its exact host-selected mission scope.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param targetName - explicit durable active member name selected by trusted host control.
   * @param request - explicit mission identity/revision and optional claimed task for the recovered generation.
   * @param signal - cancellation checked before admission and during host preparation.
   * @returns the newly recovered exact Agent after binding and gated activation.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async recoverMember(caller: Agent, targetName: string, request: BindTeamExecutionRequest, signal: AbortSignal): Promise<Agent> {
    return await this.lifecycle.admitMutation(async () => {
      const combined = AbortSignal.any([signal, this.lifecycle.signal])
      const membership = this.roster.membership(caller)
      if (membership.role !== 'lead') throw new TeamError('only Lead host control may recover a member', 'TEAM_LEAD_REQUIRED')
      this.assertExecution(caller)
      const member = this.journal.state(membership.root).members.find(value => value.name === targetName && value.phase === 'active')
      if (!member) throw new TeamError('exact active member is missing', 'TEAM_MEMBER_NOT_FOUND')
      const agent = await this.roster.recoverMember(membership.root, member.id, combined)
      this.bindExecution(agent, request)
      await this.activateMember(agent, combined)
      return agent
    })
  }

  /**
   * Report a safe authority diagnostic for tools without exposing lease fields.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @returns the denial reason, or undefined when the exact current scope is authorized.
   */
  executionDiagnostic(caller: Agent): string | undefined {
    try { this.assertExecution(caller); return undefined } catch (error) { return errorMessage(error) }
  }

  /**
   * Resolve one exact live Agent's Team role.
   * @param agent - exact live Agent used as the authority credential.
   * @returns its root, Team identity, role, and model-facing name.
   */
  membership(agent: Agent): TeamMembership {
    return this.roster.membership(agent)
  }

  /**
   * List the runtime-enriched roster visible to one Team member.
   * @param agent - exact live Team member.
   * @returns Lead and teammate rows in creation order.
   */
  listMembers(agent: Agent): TeamMemberView[] {
    return this.roster.list(this.roster.membership(agent))
  }

  private memberAddDigest(request: ApproveTeamMemberAddRequest): string {
    return payloadSha256(JSON.parse(canonicalJson({ name: request.name, description: request.description, prompt: request.prompt,
      context: request.context, provider: request.provider,
      ...(request.agentOptions === undefined ? {} : { agentOptions: request.agentOptions }), attachments: request.attachments ?? [] })))
  }

  private grantMemberAdd(caller: Agent, request: ApproveTeamMemberAddRequest): void {
    const grants = this.memberAddGrants.get(caller) ?? new Set<string>()
    grants.add(this.memberAddDigest(request)); this.memberAddGrants.set(caller, grants)
  }

  private consumeMemberAdd(caller: Agent, request: ApproveTeamMemberAddRequest): void {
    this.journal.assertCommitted(this.roster.membership(caller).root)
    const digest = this.memberAddDigest(request)
    if (!this.memberAddGrants.get(caller)?.delete(digest)) throw new TeamError('exact host-attested HUMAN member-add approval required', 'TEAM_MEMBER_ADD_APPROVAL_REQUIRED')
  }

  /**
   * Approve one exact immutable member specification; the one-use grant permits quarantine only.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - exact immutable member specification covered by the one-use authenticated control receipt.
   * @returns confirmation after durable approval; the grant permits quarantine only.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async approveMemberAdd(caller: Agent, request: ApproveTeamMemberAddRequest): Promise<{ readonly approved: true }> {
    const membership = this.roster.membership(caller)
    if (membership.role !== 'lead') throw new TeamError('only Lead control may add a member', 'TEAM_LEAD_REQUIRED')
    return this.lifecycle.admitMutation(() => this.journal.transact(membership.root.id, async () => {
      let receipt
      try { receipt = consumeHumanControl('agentTeams/approveMemberAdd', caller, request) } catch (cause) { throw new TeamError('exact HUMAN member-add control receipt required', 'TEAM_HUMAN_CONTROL_REQUIRED', { cause }) }
      await this.journal.appendAndFlush(membership.root, 'team/member-add-approved', { version: 1, teamId: membership.id, receiptId: receipt.id, digest: receipt.digest, specDigest: this.memberAddDigest(request), name: request.name })
      this.grantMemberAdd(caller, request)
      return { approved: true }
    }))
  }

  /**
   * Host-attested HUMAN member-add action; arbitrary model specs cannot mint grants.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param request - exact immutable member specification covered by the authenticated HTTP action.
   * @returns durable approval confirmation; child activation requires its separate exact lease.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('approveMemberAdd')
  remoteApproveMemberAdd(agent: Agent, request: ApproveTeamMemberAddRequest): Promise<{ readonly approved: true }> {
    return this.approveMemberAdd(agent, request)
  }

  /**
   * Create one named, continuable direct child of the Team Lead.
   * @param caller - exact live Lead Agent.
   * @param request - immutable name, description, prompt, context mode, provider, and cancellation.
   * @returns the active roster row.
   */
  async spawnTeammate(caller: Agent, request: SpawnTeammateRequest): Promise<SpawnTeammateResult> {
    if ((request.attachments?.length ?? 0) === 0) return await this.roster.spawn(caller, request)
    return await this.lifecycle.admitMutation(async () => {
      const signal = AbortSignal.any([request.signal, this.lifecycle.signal])
      const normalized = await this.validateInitialization(caller, { source: 'member-add', diagnostics: [], members: [{
        name: request.name, description: request.description, initialTask: request.prompt, context: request.context,
        continuationProvider: request.provider, attachments: request.attachments ?? [],
        ...request.agentOptions === undefined ? {} : { agentOptions: request.agentOptions },
      }] }, signal)
      const prepared = await this.roster.prepareRoster(this.roster.membership(caller).root, normalized.members, signal)
      try { return await this.roster.spawn(caller, { ...request, signal }, prepared[0]) }
      finally {
        const deadline = this.lifecycle.cleanupDeadline()
        try { await abortPrepared(prepared.flatMap(member => member.leases), deadline.signal, deadline) }
        finally { deadline.finish() }
      }
    })
  }

  /**
   * Queue one durable peer message, then attempt immediate delivery.
   * @param caller - exact live sending Team member.
   * @param request - target name, content, and pre-queue cancellation.
   * @returns durable message identity and immediate-delivery observation.
   */
  async sendMessage(caller: Agent, request: SendTeamMessageRequest): Promise<SendTeamMessageResult> {
    return await this.mailbox.send(caller, request)
  }

  /**
   * Create one independently governed durable mission.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - mission title/objective and empty canonical task-reference plan.
   * @returns the new durable draft mission without executable approval.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async createMission(caller: Agent, request: CreateTeamMissionRequest): Promise<TeamMissionView> {
    return await this.lifecycle.admitMutation(async () => this.missions.create(this.roster.membership(caller), request))
  }

  /**
   * Return one mission including its mission-local task set.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param id - explicit mission identity in this Team.
   * @returns a detached mission view containing canonical task references.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  getMission(caller: Agent, id: TeamMissionId): TeamMissionView {
    return this.missions.get(this.roster.membership(caller), id)
  }

  /**
   * List the Team's independently governed missions.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @returns detached mission views for this exact Team.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  listMissions(caller: Agent): TeamMissionView[] {
    return this.missions.list(this.roster.membership(caller))
  }

  /**
   * Approve exactly the current revision of one mission.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
   * @returns the durably approved exact revision with authenticated provenance.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async approveMission(caller: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionView> {
    return await this.lifecycle.admitMutation(async () =>
      this.missions.approve(caller, this.roster.membership(caller), request))
  }

  /**
   * Close one exact mission revision using authenticated HUMAN control.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
   * @returns the durably closed mission with previous leases invalidated.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async closeMission(caller: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionView> {
    return this.lifecycle.admitMutation(() => this.missions.end(caller, this.roster.membership(caller), request, 'closeMission'))
  }

  /**
   * Revoke one exact mission revision using authenticated HUMAN control.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
   * @returns the durably revoked mission with previous leases invalidated.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async revokeMission(caller: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionView> {
    return this.lifecycle.admitMutation(() => this.missions.end(caller, this.roster.membership(caller), request, 'revokeMission'))
  }

  /**
   * Create one unowned pending task in the Team Lead log.
   * @param caller - exact live Team member creating the task.
   * @param request - explicit mission association, task text, blockers, and advisory write scopes.
   * @returns the revision-one task view.
   */
  async createTask(caller: Agent, request: CreateTeamTaskRequest): Promise<TeamTaskView> {
    return await this.lifecycle.admitMutation(() => this.tasks.create(this.roster.membership(caller), request))
  }

  /**
   * Return one task, including a deleted tombstone.
   * @param caller - exact live Team member reading the task.
   * @param id - Team-local task identity.
   * @returns the latest task value and derived readiness diagnostics.
   */
  getTask(caller: Agent, id: TeamTaskId): TeamTaskView {
    return this.tasks.get(this.roster.membership(caller), id)
  }

  /**
   * List current non-deleted tasks in numeric creation order.
   * @param caller - exact live Team member reading the board.
   * @returns detached current task views.
   */
  listTasks(caller: Agent): TeamTaskView[] {
    return this.tasks.list(this.roster.membership(caller))
  }

  /**
   * Compare-and-set one authorized task transition.
   * @param caller - exact live Team member authorizing the mutation.
   * @param request - task identity, expected revision, action, and action fields.
   * @returns the committed next task revision.
   */
  async updateTask(caller: Agent, request: UpdateTeamTaskRequest): Promise<TeamTaskView> {
    return await this.lifecycle.admitMutation(() => this.tasks.update(caller, this.roster.membership(caller), request))
  }

  /**
   * Commit HUMAN approval of the exact current non-empty structural plan revision.
   * @param caller - exact live Lead Agent selected by the Web Remote authority.
   * @param request - revision displayed to the approving HUMAN.
   * @returns the committed approval snapshot.
   */
  async approvePlan(caller: Agent, request: ApproveTeamPlanRequest): Promise<TeamPlanApprovalSnapshot> {
    return await this.lifecycle.admitMutation(async () => {
      const membership = this.roster.membership(caller)
      if (membership.role !== 'lead') {
        throw new TeamError('only the Team Lead can approve a plan', 'TEAM_LEAD_REQUIRED')
      }
      return await this.journal.transact(membership.root.id, async () => {
        const state = this.journal.state(membership.root)
        if (!state.tasks.some(task => task.status !== 'deleted')) {
          throw new TeamError('an empty Team plan cannot be approved', 'TEAM_PLAN_EMPTY')
        }
        if (!Number.isSafeInteger(request.approvedRevision) || request.approvedRevision < 0) {
          throw new TeamError('approvedRevision must be a non-negative safe integer', 'TEAM_INVALID_ARGUMENT')
        }
        if (request.approvedRevision !== state.planRevision
          || state.planApproval !== undefined && request.approvedRevision <= state.planApproval.approvedRevision) {
          throw new TeamError(
            `stale Team plan revision ${request.approvedRevision}; current revision is ${state.planRevision}`,
            'TEAM_PLAN_STALE_REVISION',
          )
        }
        const diagnostics = [...this.approvalPreflights]
          .flatMap(preflight => [...preflight(caller, this.remoteView(caller))])
        if (diagnostics.length > 0) {
          throw new TeamError(
            `Team plan preflight failed: ${diagnostics.join('; ')}`,
            'TEAM_PLAN_PREFLIGHT_FAILED',
          )
        }
        let receipt
        try { receipt = consumeHumanControl('agentTeams/approvePlan', caller, request) } catch (cause) { throw new TeamError('exact HUMAN plan control receipt required', 'TEAM_HUMAN_CONTROL_REQUIRED', { cause }) }
        const approval = { approvedRevision: request.approvedRevision, eventId: receipt.id,
          digest: receipt.digest, humanSessionId: receipt.sessionId } satisfies TeamPlanApprovalSnapshot
        await this.journal.appendAndFlush(membership.root, 'team/plan-approved', {
          version: 3,
          teamId: TeamId(membership.root.id),
          approval,
        })
        return approval
      })
    })
  }

  /**
   * * Import the latest successful HUMAN-approved DSH plan and approve its exact
   * post-import revision in one serialized Lead-log batch.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param request - explicit target mission identity for canonical imported task association.
   * @returns the approval of the exact post-import canonical plan revision.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async importApprovedPlanAndApprove(caller: Agent, request: { readonly missionId: TeamMissionId }): Promise<TeamPlanApprovalSnapshot> {
    return this.lifecycle.admitMutation(async () => {
      const membership = this.roster.membership(caller)
      if (membership.role !== 'lead') throw new TeamError('only the Team Lead can approve a plan', 'TEAM_LEAD_REQUIRED')
      return this.journal.transact(membership.root.id, async () => {
        const state = this.journal.state(membership.root)
        const mission = state.missions.find(value => value.id === request.missionId)
        if (!mission || mission.status === 'closed' || mission.status === 'revoked') throw new TeamError('import requires an explicit live canonical mission', 'TEAM_TASK_MISSION_REQUIRED')
        // oxlint-disable-next-line typescript/no-deprecated -- Existing approved-plan history reader; migration deferred.
        const subjects = approvedPlanTaskSubjects(membership.root.session.snapshotEvents())
        const imported = this.tasks.prepareApprovedPlanImport(state, subjects, mission.id)
        const postRevision = state.planRevision + imported.length
        if (!Number.isSafeInteger(postRevision)) throw new TeamError('Team plan revision space exhausted', 'TEAM_PLAN_IMPORT_INVALID')
        const postState: TeamState = { ...state, planRevision: postRevision, planPhase: imported.length ? 'draft' : state.planPhase, tasks: [...state.tasks, ...imported] }
        if (!postState.tasks.some(task => task.status !== 'deleted')) throw new TeamError('an empty Team plan cannot be approved', 'TEAM_PLAN_EMPTY')
        if (state.planApproval && postRevision <= state.planApproval.approvedRevision) throw new TeamError('Team plan approval is stale', 'TEAM_PLAN_STALE_REVISION')
        const diagnostics = [...this.approvalPreflights].flatMap(preflight => [...preflight(caller, this.teamView(membership, postState))])
        if (diagnostics.length) throw new TeamError(`Team plan preflight failed: ${diagnostics.join('; ')}`, 'TEAM_PLAN_PREFLIGHT_FAILED')
        let receipt
        try { receipt = consumeHumanControl('agentTeams/importApprovedPlan', caller, request) } catch (cause) { throw new TeamError('exact HUMAN import control receipt required', 'TEAM_HUMAN_CONTROL_REQUIRED', { cause }) }
        const approval: TeamPlanApprovalSnapshot = { approvedRevision: postRevision, eventId: receipt.id,
          digest: receipt.digest, humanSessionId: receipt.sessionId }
        await this.journal.appendManyAndFlush(membership.root, [
          ...imported.map(task => ({ type: 'team/task' as const, data: { version: 3 as const, teamId: TeamId(membership.root.id), task } })),
          { type: 'team/plan-approved' as const, data: { version: 3 as const, teamId: TeamId(membership.root.id), approval } },
        ])
        return approval
      })
    })
  }

  /**
   * Register one live capability-envelope check at the HUMAN approval boundary.
   * @param preflight - synchronous check over the exact caller and current Team view.
   * @returns disposer that removes this approval check.
   */
  registerApprovalPreflight(preflight: (caller: Agent, view: TeamView) => readonly string[]): () => void {
    this.approvalPreflights.add(preflight)
    return () => { this.approvalPreflights.delete(preflight) }
  }

  /** Register one host-owned attachment protocol; removal verifies all durable references.
   * @param binder - required attachment protocol participant.
   * @returns asynchronous disposer that refuses referenced or pending registrations.
   */
  registerMemberBinder(binder: TeamMemberBinder): () => Promise<void> {
    this.lifecycle.assertOpen()
    return this.roster.registerMemberBinder(binder)
  }

  /**
   * Register the host initializer used by the session-scoped Enable action.
   * @param initializer - trusted default-roster producer evaluated before any member creation.
   * @returns an unregister function for this exact initializer.
   */
  registerInitializer(initializer: TeamInitializer): () => void {
    if (this.initializers.size > 0) throw new Error('an Agent Team initializer is already registered')
    this.initializers.add(initializer)
    return () => { this.initializers.delete(initializer) }
  }

  /**
   * Enable this Lead Session's Team once, provisioning its configured members.
   * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
   * @param signal - cancellation checked before admission and during host preparation.
   * @returns the provisioned default roster; children remain gated until exact execution authorization.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  async enable(caller: Agent, signal: AbortSignal): Promise<TeamEnableResult> {
    this.lifecycle.assertOpen()
    const membership = this.roster.membership(caller)
    if (membership.role !== 'lead') throw new TeamError('only the Team Lead can enable Agent Team', 'TEAM_LEAD_REQUIRED')
    signal.throwIfAborted()
    const inFlight = this.enabling.get(membership.root)
    if (inFlight !== undefined) return await inFlight
    const existing = this.roster.list(membership).filter(member => member.role === 'teammate')
    if (existing.length > 0) return { enabled: true, alreadyEnabled: true, source: 'existing', diagnostics: [], members: existing }
    const [initializer] = this.initializers
    if (initializer === undefined) throw new TeamError('Agent Team initializer is unavailable', 'TEAM_INVALID_CONFIG')
    try { consumeHumanControl('agentTeams/enable', caller, undefined) } catch (cause) { throw new TeamError('authenticated HUMAN Enable control required', 'TEAM_HUMAN_CONTROL_REQUIRED', { cause }) }
    const operation = this.lifecycle.admitMutation(async () => {
      const combined = AbortSignal.any([signal, this.lifecycle.signal])
      const initialized = await initializer(membership.root, combined)
      const prepared = await this.validateInitialization(membership.root, initialized, combined)
      const bindings = await this.roster.prepareRoster(membership.root, prepared.members, combined)
      const members: TeamMemberView[] = []
      try {
        for (const binding of bindings) {
          const spec = binding.input.spec
          combined.throwIfAborted()
          const spawnRequest = {
            name: spec.name, description: spec.description, prompt: spec.initialTask,
            context: spec.context, provider: spec.continuationProvider,
            ...spec.agentOptions === undefined ? {} : { agentOptions: spec.agentOptions },
            attachments: spec.attachments ?? [], signal: combined,
          }
          this.grantMemberAdd(membership.root, spawnRequest)
          const spawned = await this.roster.spawn(membership.root, spawnRequest, binding)
          members.push(spawned.member)
        }
        return { enabled: true as const, alreadyEnabled: false, source: prepared.source, diagnostics: prepared.diagnostics, members }
      } finally {
        const deadline = this.lifecycle.cleanupDeadline()
        try { await abortPrepared(bindings.flatMap(binding => binding.leases), deadline.signal, deadline) }
        finally { deadline.finish() }
      }
    })
    this.enabling.set(membership.root, operation)
    void operation.then(() => { this.enabling.delete(membership.root) }, () => { this.enabling.delete(membership.root) })
    return await operation
  }

  /** Fully preflight normalized specs before any row/child, preserving default adapter behavior. */
  private async validateInitialization(lead: Agent, rawInput: unknown, signal: AbortSignal): Promise<TeamInitialization> {
    if (!rawInput || typeof rawInput !== 'object' || Array.isArray(rawInput)) throw new TeamError('invalid normalized Team roster', 'TEAM_INVALID_CONFIG')
    const input = rawInput as TeamInitialization
    const members = input.members
    const rawMembers: unknown = members
    if (!Array.isArray(rawMembers) || members.length < 1 || members.length > this.config.maxMembers) {
      throw new TeamError('invalid normalized Team roster', 'TEAM_INVALID_CONFIG')
    }
    const source = requiredText(input.source, 'initializer source', 200)
    if (!Array.isArray(input.diagnostics) || input.diagnostics.length > 64 || input.diagnostics.some(value => typeof value !== 'string' || value.length > 4096)) {
      throw new TeamError('invalid initializer diagnostics', 'TEAM_INVALID_CONFIG')
    }
    const diagnostics = [...input.diagnostics]
    const names = new Set<string>()
    const specs = members.map((rawSpec: unknown): TeamMemberSpec => {
      if (!rawSpec || typeof rawSpec !== 'object' || Array.isArray(rawSpec)) throw new TeamError('invalid normalized member', 'TEAM_INVALID_CONFIG')
      const spec = rawSpec as TeamMemberSpec
      if ( typeof spec.name !== 'string' || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(spec.name) || spec.name.length > 64 || spec.name === 'lead' || names.has(spec.name)) {
        throw new TeamError('invalid or duplicate normalized member name', 'TEAM_INVALID_MEMBER_NAME')
      }
      names.add(spec.name)
      const description = requiredText(spec.description, 'description', 200)
      const continuationProvider = requiredText(spec.continuationProvider, 'continuation provider', 200)
      const context: unknown = spec.context
      if (context !== 'fresh' && context !== 'fork' || !Array.isArray(spec.initialTask) || spec.initialTask.length === 0) {
        throw new TeamError('invalid normalized member context/task', 'TEAM_INVALID_CONFIG')
      }
      let initialTask: typeof spec.initialTask
      try { initialTask = validateInitialTask(structuredClone(spec.initialTask)) } catch {
        throw new TeamError('invalid normalized member initial task', 'TEAM_INVALID_CONFIG')
      }
      if (Buffer.byteLength(JSON.stringify(initialTask), 'utf8') > this.config.maxMessageBytes) {
        throw new TeamError('initial member task exceeds byte limit', 'TEAM_INVALID_CONFIG')
      }
      const attachments = validateAttachmentRequests(spec.attachments ?? [])
      if (this.ctx.subagents.getProvider(continuationProvider) === undefined) {
        throw new TeamError('normalized continuation provider unavailable', 'TEAM_INVALID_CONFIG')
      }
      return { ...spec, context, description, continuationProvider, initialTask, attachments,
        ...spec.agentOptions === undefined ? {} : { agentOptions: structuredClone(spec.agentOptions) } }
    })
    for (const spec of specs) {
      signal.throwIfAborted()
      const provider = spec.agentOptions?.provider ?? lead.options.provider
      const model = spec.agentOptions?.model ?? lead.options.model
      if (provider === undefined || model === undefined) throw new TeamError('normalized model route unavailable', 'TEAM_INVALID_CONFIG')
      await this.ctx.llm.resolveCallConfig({ provider, model,
        ...spec.agentOptions?.reasoningEffort === undefined ? {} : { reasoningEffort: spec.agentOptions.reasoningEffort } }, signal)
    }
    return { source, diagnostics, members: specs }
  }

  /**
   * Report the exact caller's latest durable work state.
   * @param caller - exact live Team member reporting current work.
   * @param request - durable state, summary, optional reason/task, and affected files.
   * @returns the committed authoritative work view.
   */
  async reportWork(caller: Agent, request: ReportTeamWorkRequest): Promise<TeamWorkView> {
    return await this.lifecycle.admitMutation(async () => {
      return await this.work.report(caller, this.roster.membership(caller), request)
    })
  }

  /**
   * Wait for the next Team-domain or member-status change.
   * @param caller - exact live Team member waiting for activity.
   * @param timeoutMs - bounded wait duration from ten seconds through one hour.
   * @param signal - caller cancellation for the wait only.
   * @returns one observed change or a timeout result.
   */
  async waitForChange(caller: Agent, timeoutMs: number, signal: AbortSignal): Promise<TeamWaitResult> {
    const membership = this.roster.membership(caller)
    return await this.activity.wait(membership.id, timeoutMs, signal)
  }

  /**
   * Interrupt one live teammate turn without clearing its pending inbox.
   * @param caller - exact live Lead Agent.
   * @param targetName - durable teammate name.
   * @returns the target status sampled before cancellation.
   */
  interrupt(caller: Agent, targetName: string): { previousStatus: 'running' | 'idle' | 'inactive' } {
    return this.roster.interrupt(caller, targetName)
  }

  /**
   * Resolve a caller without throwing, used by scoped-tool installation and observers.
   * @param agent - candidate exact live Agent.
   * @returns Team membership, or undefined for non-Team subagents and stale identities.
   */
  tryMembership(agent: Agent): TeamMembership | undefined {
    return this.roster.tryMembership(agent)
  }

  /** Build a Team view from either committed or fully prepared transactional state. */
  private teamView(membership: TeamMembership, state: TeamState): TeamView {
    return {
      enabled: state.members.length > 0,
      planRevision: state.planRevision,
      planPhase: state.planPhase,
      ...state.planApproval === undefined ? {} : { planApproval: structuredClone(state.planApproval) },
      ...state.missions.length === 0 ? {} : { missions: this.missions.list(membership) },
      work: state.work.map(item => ({ ...item, files: [...item.files] })),
      members: this.roster.list(membership),
      tasks: this.tasks.views(membership.root, state),
    }
  }

  /**
   * Read the current roster and non-deleted task board through the generated Remote API.
   * @param agent - exact live Team member used as the authority credential.
   * @returns detached current roster and task views.
   */
  @Remote('view')
  remoteView(agent: Agent): TeamView {
    const membership = this.roster.membership(agent)
    return this.teamView(membership, this.journal.state(membership.root))
  }

  /**
   * Enable and provision this Lead Session's Agent Team through the generated Web Remote API.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param signal - cancellation checked before admission and during host preparation.
   * @returns the default-roster provisioning result; child model admission remains separately gated.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('enable')
  remoteEnable(agent: Agent, signal: AbortSignal): Promise<TeamEnableResult> {
    return this.enable(agent, signal)
  }

  /**
   * Create one mission through the generated Web Remote API.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param request - mission title/objective and empty canonical task-reference plan.
   * @returns the draft mission or a typed business rejection.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('createMission')
  remoteCreateMission(agent: Agent, request: CreateTeamMissionRequest): Promise<TeamMissionMutationResult> {
    return this.missionMutationResult(this.createMission(agent, request))
  }

  /**
   * List independently governed missions through the generated Web Remote API.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @returns detached mission views for this Team.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('listMissions')
  remoteListMissions(agent: Agent): TeamMissionView[] {
    return this.listMissions(agent)
  }

  /**
   * Get one mission through the generated Web Remote API.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param id - explicit mission identity in this Team.
   * @returns the detached explicitly requested mission.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('getMission')
  remoteGetMission(agent: Agent, id: TeamMissionId): TeamMissionView {
    return this.getMission(agent, id)
  }

  /**
   * Approve one exact mission revision through the generated Web Remote API.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
   * @returns the committed approval or a typed business rejection.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('approveMission')
  remoteApproveMission(agent: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionMutationResult> {
    return this.missionMutationResult(this.approveMission(agent, request))
  }

  /**
   * Close one exact mission revision through authenticated Web control.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
   * @returns the committed closure or a typed business rejection.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('closeMission')
  remoteCloseMission(agent: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionMutationResult> {
    return this.missionMutationResult(this.closeMission(agent, request))
  }

  /**
   * Revoke one exact mission revision through authenticated Web control.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
   * @returns the committed revocation or a typed business rejection.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('revokeMission')
  remoteRevokeMission(agent: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionMutationResult> {
    return this.missionMutationResult(this.revokeMission(agent, request))
  }

  /**
   * Create one shared task through the generated Remote API.
   * @param agent - exact live Team member creating the task.
   * @param request - explicit mission association, task text, blockers, and advisory write scopes.
   * @returns the revision-one task or a typed Team rejection.
   */
  @Remote('createTask')
  remoteCreateTask(agent: Agent, request: CreateTeamTaskRequest): Promise<TeamTaskMutationResult> {
    return this.taskMutationResult(this.createTask(agent, request))
  }

  /**
   * Apply one task mutation and preserve Team rejections as business results.
   * @param agent - exact live Team member authorizing the mutation.
   * @param request - task identity, expected revision, action, and action fields.
   * @returns the committed task or a typed Team rejection.
   */
  @Remote('updateTask')
  remoteUpdateTask(agent: Agent, request: UpdateTeamTaskRequest): Promise<TeamTaskMutationResult> {
    return this.taskMutationResult(this.updateTask(agent, request))
  }

  /**
   * Approve one exact displayed plan revision through the generated Web Remote API.
   * @param agent - exact live Lead Agent used as the authority credential.
   * @param request - revision displayed to the approving HUMAN.
   * @returns the committed approval or a typed plan conflict/rejection.
   */
  @Remote('approvePlan')
  async remoteApprovePlan(agent: Agent, request: ApproveTeamPlanRequest): Promise<TeamPlanApprovalResult> {
    try {
      return { ok: true, value: await this.approvePlan(agent, request) }
    } catch (error) {
      if (!(error instanceof TeamError)) throw error
      return {
        ok: false,
        error: {
          code: error.code === 'TEAM_PLAN_STALE_REVISION'
            ? 'team-plan-conflict'
            : error.code === 'TEAM_PLAN_PREFLIGHT_FAILED'
              ? 'team-preflight-rejected'
              : 'team-rejected',
          message: error.message,
        },
      }
    }
  }

  /**
   * Import the latest approved DSH plan and approve it through one Web Remote action.
   * @param agent - exact live Agent resolved by the host or Gateway.
   * @param request - explicit target mission identity reviewed by HUMAN control.
   * @returns the committed plan approval or a typed import/preflight rejection.
   * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
   */
  @Remote('importApprovedPlan')
  async remoteImportApprovedPlan(agent: Agent, request: { readonly missionId: TeamMissionId }): Promise<ImportApprovedTeamPlanResult> {
    try {
      return { ok: true, value: await this.importApprovedPlanAndApprove(agent, request) }
    } catch (error) {
      if (!(error instanceof TeamError)) throw error
      return {
        ok: false,
        error: {
          code: error.code === 'TEAM_PLAN_STALE_REVISION'
            ? 'team-plan-conflict'
            : error.code === 'TEAM_PLAN_IMPORT_INVALID'
              ? 'team-plan-import-rejected'
              : error.code === 'TEAM_PLAN_PREFLIGHT_FAILED'
                ? 'team-preflight-rejected'
                : 'team-rejected',
          message: error.message,
        },
      }
    }
  }

  /**
   * Report caller-bound member work through the generated Web Remote API.
   * @param agent - exact live Team member reporting current work.
   * @param request - durable state, summary, optional reason/task, and affected files.
   * @returns the committed report or a typed Team rejection.
   */
  @Remote('reportWork')
  async remoteReportWork(agent: Agent, request: ReportTeamWorkRequest): Promise<TeamWorkMutationResult> {
    try {
      return { ok: true, value: await this.reportWork(agent, request) }
    } catch (error) {
      if (!(error instanceof TeamError)) throw error
      return { ok: false, error: { code: 'team-rejected', message: error.message } }
    }
  }

  /** Preserve mission stale revisions while allowing unexpected failures to reject the Remote call. */
  private async missionMutationResult(operation: Promise<TeamMissionView>): Promise<TeamMissionMutationResult> {
    try {
      return { ok: true, value: await operation }
    } catch (error) {
      if (!(error instanceof TeamError)) throw error
      return {
        ok: false,
        error: {
          code: error.code === 'TEAM_MISSION_STALE_REVISION' ? 'team-mission-conflict' : 'team-rejected',
          message: error.message,
        },
      }
    }
  }

  /** Preserve Team task rejections while allowing unexpected failures to reject the Remote call. */
  private async taskMutationResult(operation: Promise<TeamTaskView>): Promise<TeamTaskMutationResult> {
    try {
      return { ok: true, value: await operation }
    } catch (error) {
      if (!(error instanceof TeamError)) throw error
      return {
        ok: false,
        error: {
          code: error.code === 'TEAM_TASK_STALE_REVISION' ? 'team-task-conflict' : 'team-rejected',
          message: error.message,
        },
      }
    }
  }

  /** Queue one contained recovery pass after publication has unwound. */
  private scheduleRecovery(agent: Agent): void {
    queueMicrotask(() => {
      if (this.lifecycle.disposed) return
      void this.recoverFor(agent).catch((error: unknown) => {
        if (this.lifecycle.disposed) return
        this.ctx.logger.warn(`Agent Teams recovery for "${agent.id}" failed: ${errorMessage(error)}`)
      })
    })
  }

  /** Reconcile roster provisioning before retrying that member's pending mailbox. */
  private async recoverFor(agent: Agent): Promise<void> {
    await this.roster.recoverFor(agent, this.lifecycle.signal)
    await this.mailbox.recoverFor(agent, this.lifecycle.signal)
  }

  /** Stop Team-owned live branches and release every waiter before service disposal completes. */
  private runtimeDisposal?: Promise<void>

  /** Retain guard lifetime through one shared physical runtime drain. */
  private disposeRuntime(): Promise<void> {
    return this.runtimeDisposal ??= this.disposeRuntimeOnce()
  }

  /** Close admission before awaiting all Team-owned operations. */
  private async disposeRuntimeOnce(): Promise<void> {
    this.lifecycle.close()
    this.activity.close()

    const failures: unknown[] = []
    try { this.roster.cutoffRuntime() } catch (error) { failures.push(error) }
    await this.lifecycle.settleMutations(failures)
    await this.lifecycle.settle(this.roster.pendingCreations(), failures)
    await this.lifecycle.settle(this.mailbox.pendingDispatches(), failures)
    for (const [root, childIds] of this.roster.liveChildrenByRoot()) {
      try {
        await this.roster.stopTeammates(root, childIds)
      } catch (error: unknown) {
        failures.push(error)
      }
    }
    failures.push(...this.roster.takeCleanupFailures())
    if (failures.length > 0) throw new AggregateError(failures, 'Agent Teams runtime disposal failed')
  }
}

export default TeamService
