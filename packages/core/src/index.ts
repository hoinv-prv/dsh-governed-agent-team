/** Agent Teams service façade over roster, mailbox, task, and runtime lifecycle owners. */

import { Context } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type {} from '@deepseek-ai/dsh-session-persistence'
import { Remote, TypertRemoteService } from '@deepseek-ai/dsh-typert-protocol'
import { TeamActivity } from './activity.ts'
import { errorMessage, TeamError } from './error.ts'
import { TeamJournal } from './journal.ts'
import { TeamRuntimeLifecycle } from './lifecycle.ts'
import { TeamMailbox } from './mailbox.ts'
import { teamProjectionDefinition } from './projection.ts'
import { TeamRoster } from './roster.ts'
import type { TeamMembership } from './roster.ts'
import { TeamTaskBoard } from './task-board.ts'
import { TeamWorkBoard } from './work-state.ts'
import { TeamId, TeamTaskId } from './types.ts'
import type {
  ApproveTeamPlanRequest,
  Config,
  CreateTeamTaskRequest,
  ReportTeamWorkRequest,
  SendTeamMessageRequest,
  SendTeamMessageResult,
  SpawnTeammateRequest,
  SpawnTeammateResult,
  TeamMemberView,
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
export type { TeamMembership } from './roster.ts'
export { TeamId, TeamMessageId, TeamTaskId } from './types.ts'
export { TeamError } from './error.ts'
export { scopesOverlap } from './task-board.ts'

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
  static inject = ['agents', 'sessions', 'sessionPersistence', 'sessionProjections', 'subagents']

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
  private readonly tasks: TeamTaskBoard
  private readonly work: TeamWorkBoard
  private readonly approvalPreflights = new Set<(caller: Agent, view: TeamView) => readonly string[]>()

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
    this.journal = new TeamJournal(ctx, (root) => { this.activity.notify(TeamId(root.id)) })
    this.roster = new TeamRoster(ctx, this.journal, this.lifecycle, this.config.maxMembers)
    this.mailbox = new TeamMailbox(
      ctx,
      this.journal,
      this.roster,
      this.lifecycle,
      this.config.maxPendingMessagesPerMember,
      this.config.maxMessageBytes,
    )
    this.tasks = new TeamTaskBoard(this.journal, this.config.maxTasks)
    this.work = new TeamWorkBoard(this.journal)

    ctx.on('session/event', (session, event) => { this.mailbox.observeSessionEvent(session, event) })
    ctx.on('agent/session-start', ({ agent }) => { this.scheduleRecovery(agent) })
    ctx.on('agent/status', ({ agent }) => {
      const membership = this.roster.tryMembership(agent)
      if (membership !== undefined) this.activity.notify(membership.id)
    })
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
    for (const agent of ctx.agents.list()) this.scheduleRecovery(agent)
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

  /**
   * Create one named, continuable direct child of the Team Lead.
   * @param caller - exact live Lead Agent.
   * @param request - immutable name, description, prompt, context mode, provider, and cancellation.
   * @returns the active roster row.
   */
  async spawnTeammate(caller: Agent, request: SpawnTeammateRequest): Promise<SpawnTeammateResult> {
    return await this.roster.spawn(caller, request)
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
   * Create one unowned pending task in the Team Lead log.
   * @param caller - exact live Team member creating the task.
   * @param request - task text, blockers, and advisory write scopes.
   * @returns the revision-one task view.
   */
  async createTask(caller: Agent, request: CreateTeamTaskRequest): Promise<TeamTaskView> {
    return await this.tasks.create(this.roster.membership(caller), request)
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
    return await this.tasks.update(caller, this.roster.membership(caller), request)
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
        const approval = { approvedRevision: request.approvedRevision } satisfies TeamPlanApprovalSnapshot
        await this.journal.appendAndFlush(membership.root, 'team/plan-approved', {
          version: 2,
          teamId: TeamId(membership.root.id),
          approval,
        })
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

  /**
   * Read the current roster and non-deleted task board through the generated Remote API.
   * @param agent - exact live Team member used as the authority credential.
   * @returns detached current roster and task views.
   */
  @Remote('view')
  remoteView(agent: Agent): TeamView {
    const membership = this.roster.membership(agent)
    const state = this.journal.state(membership.root)
    return {
      planRevision: state.planRevision,
      planPhase: state.planPhase,
      ...state.planApproval === undefined ? {} : { planApproval: structuredClone(state.planApproval) },
      work: state.work.map(item => ({ ...item, files: [...item.files] })),
      members: this.roster.list(membership),
      tasks: this.tasks.list(membership),
    }
  }

  /**
   * Create one shared task through the generated Remote API.
   * @param agent - exact live Team member creating the task.
   * @param request - task text, blockers, and advisory write scopes.
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
  private async disposeRuntime(): Promise<void> {
    this.lifecycle.close()
    this.activity.close()

    const failures: unknown[] = []
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
    if (failures.length > 0) throw new AggregateError(failures, 'Agent Teams runtime disposal failed')
  }
}

export default TeamService
