/** Exact reserved-child bridge and owner-scoped prompt/tool contributions. */
import type { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type {} from '@deepseek-ai/dsh-tools'
import type { ToolDefinition } from '@deepseek-ai/dsh-tools'
import type {} from '@deepseek-ai/dsh-system-prompt'
import { foldSubagentDescriptor } from '@deepseek-ai/dsh-subagent'
import type { ReservedContinuable } from '@deepseek-ai/dsh-subagent'
import { SessionId } from '@deepseek-ai/dsh-session'
import { TeamError } from './error.ts'
import { readPersistedSession } from './persisted.ts'
import type { MemberBindingHost, ReservedMemberChild } from './member-binding.ts'
import type { BinderPrepareInput, BindingIdentity, CapabilityContribution, MemberCapabilityScope } from './member-binders.ts'

/** Own reversible contributions for one exact live reserved child generation. */
export class HostMemberCapabilityScope implements MemberCapabilityScope {
  private open = true
  private readonly contributions = new Map<string, { prompt: string; remove: () => void }>()
  private readonly refreshers = new Set<() => void>()
  /**
   * Own the exact live child capability lifetime.
   * @param ctx Host services used to check live Agent identity.
   * @param agent Exact reserved child generation.
   * @param assertExecution Current private mission/task authorization check.
   * @param assertOpen Owning Team lifecycle admission check.
   */
  constructor(
    private readonly ctx: Context,
    readonly agent: Agent,
    private readonly assertExecution: (agent: Agent) => void,
    private readonly assertOpen: () => void,
  ) {}

  /**
   * Check generation/admission without granting an execution lease.
   * @returns Whether this exact capability scope remains installed and open.
   */
  isCurrent(): boolean {
    if (!this.open || this.ctx.agents.get(this.agent.id) !== this.agent) return false
    try { this.assertOpen(); return true } catch { return false }
  }

  /**
   * Revalidate exact authority for every read/effect/request boundary.
   * @param _action Protected capability boundary.
   */
  authorize(_action: 'read' | 'effect' | 'request'): void {
    this.requireCurrent()
    this.assertExecution(this.agent)
  }

  /**
   * Install one scoped owner section and real executable tools while quarantined.
   * @param contribution Required owner prompt and executable tool descriptors.
   * @returns Idempotent disposer that invalidates this required capability scope.
   */
  install(contribution: CapabilityContribution): () => void {
    this.requireCurrent()
    if (this.contributions.has(contribution.key)) throw new TeamError('member contribution already installed', 'TEAM_BINDING_CONFLICT')
    const scoped = this.agent.ctx
    const removers: Array<() => void> = []
    const entry = { prompt: contribution.prompt, remove: () => {} }
    const remove = () => {
      if (this.contributions.get(contribution.key) !== entry) return
      this.contributions.delete(contribution.key)
      const failures: unknown[] = []
      for (const dispose of removers.splice(0).reverse()) { try { dispose() } catch (error) { failures.push(error) } }
      try { this.close() } catch (error) { failures.push(error) }
      if (failures.length) throw new AggregateError(failures, 'member contribution cutoff failed')
    }
    entry.remove = remove
    this.contributions.set(contribution.key, entry)
    try {
      removers.push(scoped.systemPrompt.section({
        name: contribution.key,
        order: scoped.systemPrompt.getSectionOrder('TEAM_POLICY') + 1,
        text: () => { this.requireCurrent(); return entry.prompt },
      }))
      for (const tool of contribution.tools) {
        const capability = tool.capability === 'read' ? 'read' : 'effect'
        const parameters = tool.schema
        if (parameters === null || typeof parameters !== 'object' || Array.isArray(parameters)) {
          throw new TeamError('member tool schema must be an object', 'TEAM_BINDING_CONFLICT')
        }
        const definition: ToolDefinition = {
          name: tool.name,
          description: capability === 'read' ? 'Read one member memory item.' : 'Submit an unconfirmed member memory candidate.',
          parameters: { ...parameters },
          capabilities: capability === 'read' ? ['team-inspection'] : ['durable-memory-effect'],
          output: { schema: {}, render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }] },
          execute: async (args, execution) => {
            if (execution.agent !== this.agent || this.contributions.get(contribution.key) !== entry) {
              throw new TeamError('member contribution generation unavailable', 'TEAM_BINDING_UNAVAILABLE')
            }
            this.authorize(capability)
            const value = await tool.invoke(args)
            this.authorize(capability)
            if (this.contributions.get(contribution.key) !== entry) throw new TeamError('member contribution removed', 'TEAM_BINDING_UNAVAILABLE')
            return value
          },
        }
        removers.push(scoped.tools.register(definition))
      }
      this.requireCurrent()
      return remove
    } catch (error) {
      try { remove() } catch (cleanup) { throw new AggregateError([error, cleanup], 'member contribution installation failed') }
      throw error
    }
  }

  /**
   * Await exact owner refresh before each prompt rendering, including retries.
   * @param refresh Awaited owner refresh callback.
   * @returns Idempotent disposer for the exact Agent refresh listener.
   */
  beforeRequest(refresh: () => Promise<void>): () => void {
    this.requireCurrent()
    const dispose = this.agent.ctx.on('agent/prepare-prompt', async ({ agent, signal }) => {
      if (agent !== this.agent) throw new TeamError('member refresh generation mismatch', 'TEAM_BINDING_UNAVAILABLE')
      signal.throwIfAborted()
      this.authorize('request')
      await refresh()
      signal.throwIfAborted()
      this.authorize('request')
    })
    let installed = true
    const remove = () => {
      if (!installed) return
      installed = false
      this.refreshers.delete(remove)
      dispose()
    }
    this.refreshers.add(remove)
    return remove
  }

  /**
   * Replace existing text; a late refresh never recreates a removed section.
   * @param key Installed owner contribution key.
   * @param prompt Replacement material for the next prompt render.
   */
  replacePrompt(key: string, prompt: string): void {
    this.requireCurrent()
    const entry = this.contributions.get(key)
    if (!entry) throw new TeamError('member contribution unavailable', 'TEAM_BINDING_UNAVAILABLE')
    entry.prompt = prompt
  }

  /** Synchronously withdraw every owned executable/model contribution. */
  close(): void {
    if (!this.open) return
    this.open = false
    const failures: unknown[] = []
    for (const remove of [...this.refreshers].reverse()) { try { remove() } catch (error) { failures.push(error) } }
    for (const entry of [...this.contributions.values()].reverse()) { try { entry.remove() } catch (error) { failures.push(error) } }
    if (failures.length) throw new AggregateError(failures, 'member scope cutoff failed')
  }

  private requireCurrent(): void {
    if (!this.isCurrent()) throw new TeamError('member scope generation unavailable', 'TEAM_BINDING_UNAVAILABLE')
  }
}

/** Dependencies retained by one Team's real reserved-host adapter. */
export interface ReservedMemberHostOptions {
  readonly ctx: Context
  readonly root: Agent
  readonly assertExecution: (agent: Agent) => void
  readonly assertOpen: () => void
  readonly onReserved: (identity: BindingIdentity, reserved: ReservedContinuable, scope: HostMemberCapabilityScope) => void
  readonly observeCleanup: (operation: Promise<void>) => void
}

/**
 * Bind generic member lifecycle operations to qualified exact DSH handles.
 * @param options Exact Team owner, authority checks and cleanup observers.
 * @returns Reserved host operations preserving quarantine and durable identity.
 */
export function createReservedMemberHost(options: ReservedMemberHostOptions): MemberBindingHost {
  const { ctx, root } = options
  const wrap = (input: BindingIdentity, reserved: ReservedContinuable): ReservedMemberChild => {
    const scope = new HostMemberCapabilityScope(ctx, reserved.agent, options.assertExecution, options.assertOpen)
    options.onReserved(input, reserved, scope)
    let physicalDisposal: Promise<void> | undefined
    return {
      scope,
      isValid: () => scope.isCurrent() && reserved.state !== 'aborted' && reserved.state !== 'disposed',
      persistInitialPrompt: async (task, key, signal) => await reserved.persistInitialPrompt(task, key, signal),
      activate: async (signal) => { options.assertOpen(); options.assertExecution(reserved.agent); await reserved.activate(signal) },
      abort: async (signal) => {
        const failures: unknown[] = []
        try { scope.close() } catch (error) { failures.push(error) }
        try { await reserved.abort(signal) } catch (error) { failures.push(error) }
        if (failures.length) throw new AggregateError(failures, 'reserved child abort failed')
      },
      dispose: async () => {
        const failures: unknown[] = []
        try { scope.close() } catch (error) { failures.push(error) }
        if (!physicalDisposal) {
          physicalDisposal = reserved.dispose()
          options.observeCleanup(physicalDisposal)
        }
        try { await physicalDisposal } catch (error) { failures.push(error) }
        if (failures.length) throw new AggregateError(failures, 'reserved child disposal failed')
      },
    }
  }
  return {
    materialize: async (input: BinderPrepareInput, signal) => {
      options.assertOpen()
      const reserved = await ctx.subagents.materializeContinuable({
        childId: SessionId(input.memberId), provider: input.spec.continuationProvider, label: input.spec.description,
        request: { parent: root, ...input.spec.agentOptions === undefined ? {} : { agentOptions: input.spec.agentOptions } }, signal,
      })
      return wrap(input, reserved)
    },
    recover: async (input, signal) => {
      options.assertOpen()
      const member = ctx.sessionProjections.stateOf(root.session, 'agentTeam')?.members.find(value => value.id === input.memberId)
      if (!member) throw new TeamError('persisted member unavailable', 'TEAM_BINDING_UNAVAILABLE')
      const reserved = await ctx.subagents.recoverContinuable({ childId: member.id, parent: root, provider: member.provider, signal })
      return wrap(input, reserved)
    },
    verifyPersistedChild: async (input, signal) => {
      options.assertOpen()
      const member = ctx.sessionProjections.stateOf(root.session, 'agentTeam')?.members.find(value => value.id === input.memberId)
      if (!member) throw new TeamError('persisted member unavailable', 'TEAM_BINDING_UNAVAILABLE')
      const loaded = await readPersistedSession(ctx.sessionPersistence, member.id, signal)
      const suffix = loaded.events.slice(loaded.inheritedEventCount)
      const descriptor = foldSubagentDescriptor(suffix)
      const initial = suffix.some(event => event.type === 'subagent/initial-admission' && event.data.kind === 'persisted')
      const aborted = suffix.some(event => event.type === 'subagent/initial-admission' && event.data.kind === 'aborted')
      if (loaded.header.parentSession !== root.id || descriptor?.mode !== 'continuable' || descriptor.provider !== member.provider
        || !initial || aborted) {
        throw new TeamError('persisted child descriptor or admission mismatch', 'TEAM_BINDING_UNAVAILABLE')
      }
    },
  }
}
