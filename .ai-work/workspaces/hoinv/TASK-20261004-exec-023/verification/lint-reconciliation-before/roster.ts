/** Team membership, continuable-child provisioning, and roster-owned teardown. */

import { randomUUID } from 'node:crypto'
import type { Context } from '@deepseek-ai/cordis'
import { brandString } from '@deepseek-ai/dsh-brand'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type { SessionId } from '@deepseek-ai/dsh-session'
import { foldSubagentDescriptor } from '@deepseek-ai/dsh-subagent'
import type { ReservedContinuable } from '@deepseek-ai/dsh-subagent'
import { errorMessage, TeamError } from './error.ts'
import type { TeamJournal } from './journal.ts'
import type { TeamRuntimeLifecycle } from './lifecycle.ts'
import { readPersistedSession } from './persisted.ts'
import type { TeamState } from './projection.ts'
import { TeamId } from './types.ts'
import type {
  SpawnTeammateRequest,
  SpawnTeammateResult,
  TeamMemberSnapshot,
  TeamMemberView,
} from './types.ts'
import { requiredText } from './validation.ts'
import { validateAttachmentRequests } from './attachments.ts'

const MEMBER_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u

/** Caller identity inside one implicit Team. */
export interface TeamMembership {
  readonly root: Agent
  readonly id: TeamId
  readonly role: 'lead' | 'teammate'
  readonly name: string
}

/**
 * Resolve one active Team member by model-facing name, including the Lead pseudo-row.
 * @param root - exact live Team Lead.
 * @param state - current Team state.
 * @param rawName - candidate member name.
 * @returns resolved durable id and normalized name.
 */
export function resolveActiveMember(
  root: Agent,
  state: TeamState,
  rawName: string,
): { id: SessionId; name: string } {
  const name = rawName.trim()
  if (name === 'lead') return { id: root.id, name }
  const member = state.members.find(candidate => candidate.name === name)
  if (member?.attachments.length) throw new TeamError('required member bindings unavailable', 'TEAM_BINDING_UNAVAILABLE')
  if (member === undefined || member.phase !== 'active') {
    throw new TeamError(`active teammate "${name}" not found`, 'TEAM_MEMBER_NOT_FOUND')
  }
  return { id: member.id, name }
}

/** Owns Team identities and the lifecycle of rostered continuable children. */
export class TeamRoster {
  private readonly reservations = new Map<SessionId, ReservedContinuable>()
  private readonly releasedReservations = new WeakSet<ReservedContinuable>()
  private readonly inFlightCreations = new Set<Promise<unknown>>()
  private readonly inFlightCleanups = new Set<Promise<unknown>>()
  private readonly cleanupFailures: unknown[] = []

  /**
   * @param ctx - Team service context with Agent, Session, persistence, and subagent services.
   * @param journal - authoritative Lead-log transaction owner.
   * @param lifecycle - shared Team runtime admission cutoff.
   * @param maxMembers - maximum immutable roster entries per Team.
   */
  constructor(
    private readonly ctx: Context,
    private readonly journal: TeamJournal,
    private readonly lifecycle: TeamRuntimeLifecycle,
    private readonly maxMembers: number,
    private readonly assertExecution: (agent: Agent) => void,
    private readonly consumeMemberAdd: (caller: Agent, request: SpawnTeammateRequest) => void,
  ) {}

  /**
   * Resolve one exact live Agent's Team role.
   * @param agent - exact live Agent used as the authority credential.
   * @returns its root, Team identity, role, and model-facing name.
   */
  membership(agent: Agent): TeamMembership {
    const membership = this.tryMembership(agent)
    if (membership === undefined) {
      throw new TeamError(`agent "${agent.id}" is not a member of an active Agent Team`, 'TEAM_NOT_MEMBER')
    }
    return membership
  }

  /**
   * Resolve a caller without throwing for scoped installation and lifecycle observers.
   * @param agent - candidate exact live Agent.
   * @returns Team membership, or undefined for non-Team subagents and stale identities.
   */
  tryMembership(agent: Agent): TeamMembership | undefined {
    if (this.ctx.agents.get(agent.id) !== agent) return undefined
    try {
      const parentId = agent.session.header.parentSession
      if (parentId !== undefined) {
        const root = this.ctx.agents.get(parentId)
        if (root !== undefined) {
          const member = this.journal.state(root).members.find(candidate => candidate.id === agent.id)
          if (member?.attachments.length) return undefined
          if (member?.phase === 'active' || member?.phase === 'provisioning') {
            return { root, id: TeamId(root.id), role: 'teammate', name: member.name }
          }
          // A direct child outside the durable roster is not a teammate. Ordinary
          // host forks are independent roots; subagent descriptors distinguish
          // provider-owned workers that must not receive a nested Team identity.
          if (this.subagentDescriptor(agent)) return undefined
          return { root: agent, id: TeamId(agent.id), role: 'lead', name: 'lead' }
        }
      }
      // A continuation can briefly outlive its parent during child-first teardown.
      // Do not reinterpret that durable child as a new implicit root Team. A host-
      // resumed ordinary fork has no descriptor in its own suffix and remains a
      // valid new root whose inherited Team records stay outside its projected Team state.
      if (this.subagentDescriptor(agent)) return undefined
      return { root: agent, id: TeamId(agent.id), role: 'lead', name: 'lead' }
    } catch {
      // This method is used by lifecycle observers and teardown discovery. A
      // malformed durable stream is surfaced by authoritative Team operations;
      // the non-throwing probe must not veto unrelated Agent lifecycle edges.
      return undefined
    }
  }

  /**
   * List the runtime-enriched roster visible to one Team member.
   * @param membership - exact caller membership resolved by this roster.
   * @returns Lead and teammate rows in creation order.
   */
  list(membership: TeamMembership): TeamMemberView[] {
    const { root } = membership
    const state = this.journal.state(root)
    const result: TeamMemberView[] = [{
      id: root.id,
      name: 'lead',
      role: 'lead',
      status: root.status,
      ...root.options.model === undefined ? {} : { model: root.options.model },
      diagnostics: [],
    }]
    for (const member of state.members) {
      const live = this.ctx.agents.get(member.id)
      const model = live?.options.model ?? member.model
      result.push({
        id: member.id,
        name: member.name,
        role: 'teammate',
        status: member.phase === 'failed'
          ? 'failed'
          : member.phase === 'provisioning'
            ? 'provisioning'
            : member.attachments.length > 0 ? 'inactive' : live?.status ?? 'inactive',
        description: member.description,
        provider: member.provider,
        context: member.context,
        ...model === undefined ? {} : { model },
        diagnostics: member.error === undefined ? [] : [member.error],
        ...member.attachments.length === 0 ? {} : { bindings: member.attachments.map(record => ({ binderId: record.binderId, protocolVersion: record.protocolVersion, readiness: member.phase === 'failed' ? 'failed' as const : 'unavailable' as const })) },
      })
    }
    return result
  }

  /**
   * Create one named, continuable direct child of the Team Lead.
   * @param caller - exact live Lead Agent.
   * @param request - immutable name, description, prompt, context mode, provider, and cancellation.
   * @returns the active roster row.
   */
  async spawn(caller: Agent, request: SpawnTeammateRequest): Promise<SpawnTeammateResult> {
    if (this.lifecycle.disposed) throw new TeamError('Agent Teams service is disposing', 'TEAM_DISPOSED')
    const operation = this.spawnAdmitted(caller, request)
    this.inFlightCreations.add(operation)
    try {
      return await operation
    } finally {
      this.inFlightCreations.delete(operation)
    }
  }

  /**
   * Return admitted creation operations captured for ordered disposal.
   * @returns detached snapshot ordered only by Set insertion.
   */
  pendingCreations(): readonly Promise<unknown>[] {
    return [...this.inFlightCreations, ...this.inFlightCleanups]
  }

  /** Close every reserved child gate synchronously before runtime drain awaits. */
  cutoffRuntime(): void {
    const failures: unknown[] = []
    for (const reserved of this.reservations.values()) {
      let disposal: Promise<void>
      try { disposal = reserved.dispose() } catch (error) { disposal = Promise.reject(error) }
      this.inFlightCleanups.add(disposal)
      void disposal.then(() => this.inFlightCleanups.delete(disposal), error => {
        this.inFlightCleanups.delete(disposal)
        this.cleanupFailures.push(error)
        this.ctx.logger.warn(`reserved child disposal: ${errorMessage(error)}`)
      })
    }
    for (const [root, ids] of this.liveChildrenByRoot()) {
      for (const id of ids) {
        try { this.ctx.subagents.interrupt(id, { kind: 'ancestor', agent: root }) } catch (error) { failures.push(error) }
      }
    }
    if (failures.length) throw new AggregateError(failures, 'synchronous Team child cutoff failed')
  }

  /**
   * Retain physically settled cleanup failures even when their deadline returned first.
   * @returns Cleanup failures accumulated by prior roster operations.
   */

  takeCleanupFailures(): unknown[] { return this.cleanupFailures.splice(0) }

  /**
   * Reconcile provisioning state when one Team member Session starts.
   * @param agent - newly started exact live Agent.
   * @param signal - shared runtime cancellation.
   */
  async recoverFor(agent: Agent, signal: AbortSignal): Promise<void> {
    signal.throwIfAborted()
    const membership = this.tryMembership(agent)
    if (membership?.role === 'lead') await this.reconcileProvisioning(membership.root, signal)
  }

  /**
   * Reconstruct one exact roster child with its host gate closed and no model admission.
   * @param root Authoritative Team projection root.
   * @param childId Durable child Session id reserved for this Team member.
   * @param signal Cancellation signal for the operation.
   * @returns The recovered Agent for the exact durable child.
   */

  async recoverMember(root: Agent, childId: SessionId, signal: AbortSignal): Promise<Agent> {
    const member = this.journal.state(root).members.find(value => value.id === childId)
    if (!member || member.phase !== 'active' || member.attachments.length) throw new TeamError('exact active member is unavailable', 'TEAM_MEMBER_NOT_FOUND')
    const existing = this.reservations.get(childId)
    if (existing && this.ctx.agents.get(childId) === existing.agent) return existing.agent
    const reserved = await this.ctx.subagents.recoverContinuable({ childId, parent: root, provider: member.provider, signal })
    this.reservations.set(childId, reserved)
    return reserved.agent
  }

  /**
   * Activate an already-persisted initial item only after exact target authorization.
   * @param agent Live Agent generation whose authority is checked.
   * @param signal Cancellation signal for the operation.
   * @returns A promise that resolves after the selected member can be released.
   */

  async activateMember(agent: Agent, signal: AbortSignal): Promise<void> {
    this.assertExecution(agent)
    const reserved = this.reservations.get(agent.id)
    if (reserved) {
      if (reserved.agent !== agent) throw new TeamError('reserved child generation changed', 'TEAM_EXECUTION_DENIED')
      this.assertExecution(agent)
      if (!this.releasedReservations.has(reserved)) {
        await reserved.activate(signal)
        this.releasedReservations.add(reserved)
      }
    }
  }

  /**
   * Interrupt one live teammate turn without clearing its pending inbox.
   * @param caller - exact live Lead Agent.
   * @param targetName - durable teammate name.
   * @returns the target status sampled before cancellation.
   */
  interrupt(caller: Agent, targetName: string): { previousStatus: 'running' | 'idle' | 'inactive' } {
    const membership = this.membership(caller)
    if (membership.role !== 'lead') throw new TeamError('only the Team Lead can interrupt teammates', 'TEAM_LEAD_REQUIRED')
    const state = this.journal.state(membership.root)
    const target = resolveActiveMember(membership.root, state, targetName)
    if (target.id === membership.root.id) throw new TeamError('the Team Lead cannot interrupt itself', 'TEAM_INVALID_TARGET')
    const live = this.ctx.agents.get(target.id)
    if (live === undefined) return { previousStatus: 'inactive' }
    const previousStatus = live.status
    this.ctx.subagents.interrupt(target.id, { kind: 'ancestor', agent: caller })
    return { previousStatus }
  }

  /**
   * Group exact live roster children by their current Lead for runtime teardown.
   * @returns each live Lead and the roster child ids currently in the Agent registry.
   */
  liveChildrenByRoot(): Map<Agent, SessionId[]> {
    const teams = new Map<Agent, SessionId[]>()
    for (const agent of this.ctx.agents.list()) {
      const rootId = agent.session.header.parentSession
      if (rootId === undefined) continue
      const root = this.ctx.agents.get(rootId)
      if (root === undefined
        || !this.journal.state(root).members.some(member => member.id === agent.id)) continue
      const children = teams.get(root) ?? []
      children.push(agent.id)
      teams.set(root, children)
    }
    return teams
  }

  /**
   * Release exact teammate Activations through the continuation lifecycle owner.
   * @param root - exact live Team Lead authorizing release.
   * @param childIds - selected roster child ids.
   */
  async stopTeammates(root: Agent, childIds: readonly SessionId[]): Promise<void> {
    await this.lifecycle.withTimeout(this.ctx.subagents.drainContinuableChildren(root, childIds))
  }

  /** Perform one creation admitted before the Team runtime disposal cutoff. */
  private async spawnAdmitted(
    caller: Agent,
    request: SpawnTeammateRequest,
  ): Promise<SpawnTeammateResult> {
    const membership = this.membership(caller)
    if (membership.role !== 'lead') {
      throw new TeamError('only the Team Lead can create teammates', 'TEAM_LEAD_REQUIRED')
    }
    const signal = AbortSignal.any([request.signal, this.lifecycle.signal])
    signal.throwIfAborted()
    if (validateAttachmentRequests(request.attachments ?? []).length > 0) {
      throw new TeamError('required attachments need a qualified reserved-child host', 'TEAM_BINDER_UNAVAILABLE')
    }
    const root = membership.root
    const name = this.memberName(request.name)
    const description = requiredText(request.description, 'description', 200)
    const childId = brandString<SessionId>(randomUUID())
    const member: TeamMemberSnapshot = {
      id: childId,
      name,
      description,
      provider: requiredText(request.provider, 'provider', 200),
      context: request.context,
      ...request.agentOptions?.model === undefined ? {} : { model: request.agentOptions.model },
      phase: 'provisioning',
      attachments: [],
    }

    await this.journal.transact(root.id, async () => {
      const state = this.journal.state(root)
      if (state.members.some(member => member.name === name)) {
        throw new TeamError(`teammate name "${name}" was already used in this Team`, 'TEAM_MEMBER_NAME_TAKEN')
      }
      if (state.members.length >= this.maxMembers) {
        throw new TeamError(`Team member limit ${this.maxMembers} reached`, 'TEAM_MEMBER_LIMIT')
      }
      this.consumeMemberAdd(caller, request)
      await this.journal.appendAndFlush(root, 'team/member', { version: 3, teamId: TeamId(root.id), member })
    })

    let reserved: ReservedContinuable | undefined
    try {
      reserved = await this.ctx.subagents.materializeContinuable({
        childId,
        provider: request.provider,
        label: description,
        request: {
          parent: root,
          ...request.agentOptions === undefined ? {} : { agentOptions: request.agentOptions },
        },
        signal,
      })
      this.reservations.set(childId, reserved)
      await reserved.persistInitialPrompt(request.prompt, `gat:${root.id}:${childId}:initial`, signal)
    } catch (error: unknown) {
      const cleanupFailures: unknown[] = []
      if (reserved) {
        const deadline = this.lifecycle.cleanupDeadline()
        // Both host methods close their gate synchronously, before any awaited lock/flush.
        const invoke = (operation: () => Promise<void>): Promise<void> => {
          try { return operation() } catch (failure) { return Promise.reject(failure) }
        }
        const aborting = invoke(() => reserved!.abort(deadline.signal))
        // Observe the unbounded host disposal promise separately from our total
        // deadline so late physical completion or failure retains an owner.
        const disposing = invoke(() => reserved!.dispose())
        const physical = Promise.allSettled([aborting, disposing]).then(outcomes => {
          const failures = outcomes.flatMap(outcome => outcome.status === 'rejected' ? [outcome.reason] : [])
          if (failures.length) throw new AggregateError(failures, 'failed child physical cleanup failed')
        })
        this.inFlightCleanups.add(physical)
        void physical.then(() => this.inFlightCleanups.delete(physical), failure => {
          this.inFlightCleanups.delete(physical)
          this.cleanupFailures.push(failure)
          this.ctx.logger.warn(`failed child cleanup: ${errorMessage(failure)}`)
        })
        try { await deadline.run(() => physical) } catch (failure) { cleanupFailures.push(failure) }
        finally { deadline.finish() }
        this.reservations.delete(childId)
      }
      const failed: TeamMemberSnapshot = {
        ...member,
        phase: 'failed',
        error: errorMessage(error),
      }
      try {
        const phase = await this.settleProvisioning(root, failed)
        if (!reserved) await this.stopTeammates(root, [childId])
        if (phase === 'active') {
          throw new TeamError(
            `teammate "${name}" became active while its creator reported failure`,
            'TEAM_PROVISIONING_CONFLICT',
            { cause: error },
          )
        }
      } catch (recordError: unknown) {
        throw new AggregateError([error, ...cleanupFailures, recordError], 'teammate creation and durable failure recording both failed')
      }
      if (cleanupFailures.length) throw new AggregateError([error, ...cleanupFailures], `teammate creation failed: ${errorMessage(error)}; cleanup failed`)
      throw error
    }
    const active = {
      ...member,
      phase: 'active' as const,
    } satisfies TeamMemberSnapshot
    // The initial item is durably quarantined. If
    // this checkpoint fails, keep the in-memory active edge instead of inventing
    // an impossible active -> failed transition; restart reconciliation covers
    // the provisioning-only durable prefix.
    const settledPhase = await this.settleProvisioning(root, active)
    if (settledPhase === 'failed') {
      const conflict = new TeamError(
        `teammate "${name}" was reconciled as failed while creation was in progress`,
        'TEAM_PROVISIONING_CONFLICT',
      )
      try {
        await this.stopTeammates(root, [childId])
      } catch (cleanupError: unknown) {
        /* v8 ignore next -- requires the independently tested HMR settlement conflict and cleanup failure together. */
        throw new AggregateError([conflict, cleanupError], 'provisioning conflict cleanup failed')
      }
      throw conflict
    }
    return { member: this.memberView(active) }
  }

  /** Settle provisioning-only members from their independently durable child Sessions. */
  private async reconcileProvisioning(root: Agent, signal: AbortSignal): Promise<void> {
    const provisioning = this.journal.state(root).members.filter(member => member.phase === 'provisioning')
    for (const member of provisioning) {
      signal.throwIfAborted()
      if (member.attachments.length > 0) continue
      // A live child means creation is still completing in this process. Its
      // creator owns the terminal member edge.
      if (this.ctx.agents.get(member.id) !== undefined) continue
      let phase: 'active' | 'failed' = 'failed'
      let failure = 'provisioning did not leave a resumable child Session'
      try {
        const loaded = await readPersistedSession(this.ctx.sessionPersistence, member.id, signal)
        const suffix = loaded.events.slice(loaded.inheritedEventCount)
        const descriptor = foldSubagentDescriptor(suffix)
        const recovered = await this.ctx.subagents.recoverContinuable({ childId: member.id, parent: root, provider: member.provider, signal })
        this.reservations.set(member.id, recovered)
        const acceptedInitialPrompt = recovered.initialMessageId !== undefined && recovered.state !== 'aborted' && recovered.state !== 'disposed'
        if (loaded.header.parentSession === root.id
          && descriptor?.mode === 'continuable'
          && descriptor.provider === member.provider
          && acceptedInitialPrompt) {
          phase = 'active'
        } else {
          failure = 'persisted child Session does not match the provisioned continuation'
        }
      } catch (error: unknown) {
        failure = `child Session recovery failed: ${errorMessage(error)}`
      }
      signal.throwIfAborted()
      await this.journal.transact(root.id, async () => {
        signal.throwIfAborted()
        const current = this.journal.state(root).members.find(candidate => candidate.id === member.id)
        if (current?.phase !== 'provisioning') return
        const settled: TeamMemberSnapshot = {
          ...current,
          phase,
          ...phase === 'failed' ? { error: failure } : {},
        }
        await this.journal.appendAndFlush(root, 'team/member', {
          version: 3,
          teamId: TeamId(root.id),
          member: settled,
        })
      })
    }
  }

  /** Build one runtime member row after successful creation. */
  private memberView(member: TeamMemberSnapshot & { readonly phase: 'active' }): TeamMemberView {
    const live = this.ctx.agents.get(member.id)
    const model = live?.options.model ?? member.model
    return {
      id: member.id,
      name: member.name,
      role: 'teammate',
      status: live?.status ?? 'inactive',
      description: member.description,
      provider: member.provider,
      context: member.context,
      ...model === undefined ? {} : { model },
      diagnostics: [],
    }
  }

  /** Validate a never-reused model-facing teammate name. */
  private memberName(value: string): string {
    if (!MEMBER_NAME.test(value) || value.length > 64 || value === 'lead') {
      throw new TeamError(
        'teammate name must be lower-kebab-case, at most 64 characters, and not "lead"',
        'TEAM_INVALID_MEMBER_NAME',
      )
    }
    return value
  }

  /** Append one terminal provisioning edge unless recovery already settled it. */
  private async settleProvisioning(
    root: Agent,
    terminal: TeamMemberSnapshot,
  ): Promise<'active' | 'failed'> {
    return this.journal.transact(root.id, async () => {
      const current = this.journal.state(root).members.find(member => member.id === terminal.id)
      /* v8 ignore next 3 -- the append-only provisioning event is committed by this operation before settlement. */
      if (current === undefined) {
        throw new TeamError(`provisioned teammate "${terminal.id}" disappeared`, 'TEAM_PROVISIONING_CONFLICT')
      }
      if (current.phase !== 'provisioning') return current.phase
      await this.journal.appendAndFlush(root, 'team/member', {
        version: 3,
        teamId: TeamId(root.id),
        member: terminal,
      })
      return terminal.phase === 'active' ? 'active' : 'failed'
    })
  }

  /** Whether a Session's own suffix identifies a provider-owned subagent child. */
  private subagentDescriptor(agent: Agent): boolean {
    // oxlint-disable-next-line typescript/no-deprecated -- Existing Session history read; migration deferred.
    return foldSubagentDescriptor(agent.session.snapshotEvents(agent.session.inheritedEventCount)) !== undefined
  }
}
