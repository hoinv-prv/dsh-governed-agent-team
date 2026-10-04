/** Frozen lifecycle orchestration over qualified ports; not wired to legacy DSH creation. */
import { validateAttachmentRecords } from './attachments.ts'
import { TeamError } from './error.ts'
import { BindingDeadline, acquireBindingResource } from './binding-deadline.ts'
export { BindingDeadline } from './binding-deadline.ts'
import { abortPrepared } from './member-binders.ts'
import type { BinderBindInput, BinderPrepareInput, BindingIdentity, DisposableBinding, MemberCapabilityScope, PreparedMember } from './member-binders.ts'
import type { TeamMemberAttachmentRecord } from './types.ts'


/**
 * Expose the reserved child lifecycle and its exact member scope.
 */
export interface ReservedMemberChild {
  readonly scope: MemberCapabilityScope
  isValid(): boolean
  persistInitialPrompt(task: BinderPrepareInput['spec']['initialTask'], key: string, signal: AbortSignal): Promise<string>
  activate(signal: AbortSignal): Promise<void>
  abort(signal: AbortSignal): Promise<void>
  dispose(signal: AbortSignal): Promise<void>
}

/**
 * Persist provisioning and active phases for member binding.
 */
export interface MemberBindingJournal {
  provisioning(input: BindingIdentity, records: readonly TeamMemberAttachmentRecord[]): Promise<void>
  active(input: BindingIdentity, records: readonly TeamMemberAttachmentRecord[]): Promise<void>
  failed(input: BindingIdentity, records: readonly TeamMemberAttachmentRecord[], diagnostic: string): Promise<void>
  committedPhase(input: BindingIdentity): Promise<'none' | 'provisioning' | 'active' | 'failed'>
}

/**
 * Materialize and recover reserved children through DSH host APIs.
 */
export interface MemberBindingHost {
  materialize(input: BinderPrepareInput, signal: AbortSignal): Promise<ReservedMemberChild>
  /** Cold reconstruction must preserve existing activation state with no inbox/model release. */
  recover(input: BindingIdentity, signal: AbortSignal): Promise<ReservedMemberChild>
  verifyPersistedChild(input: BindingIdentity, signal: AbortSignal): Promise<void>
}

/**
 * Authorize and publish readiness for one exact member generation.
 */
export interface MemberExecutionAuthority {
  authorize(input: BindingIdentity, operation: 'activate' | 'mailbox'): void
  publish(input: BindingIdentity, readiness: 'ready' | 'unavailable'): void
}


/**
 * Own a bound child, installed contributions, and readiness lifecycle.
 */
export class BoundMemberRuntime {
  /**
   * Normalized member identity and capability scope used by this runtime.
   */
  readonly input: BinderBindInput
  /**
   * Immutable attachment records owned by this member runtime.
   */
  readonly records: readonly TeamMemberAttachmentRecord[]
  private readonly child: ReservedMemberChild
  private readonly bindings: readonly DisposableBinding[]
  private readonly authority: MemberExecutionAuthority
  private closed = false
  private activation: Promise<void> | undefined
  private disposal?: Promise<void>
  private activated = false
  private readonly cancellation = new AbortController()
  /** Host-only failure evidence; callers must redact before any model/view exposure. */
  lastFailure: unknown
  constructor(input: BinderBindInput, records: readonly TeamMemberAttachmentRecord[], child: ReservedMemberChild, bindings: readonly DisposableBinding[], authority: MemberExecutionAuthority) {
    this.input = input; this.records = records; this.child = child; this.bindings = bindings; this.authority = authority
  }
  /**
   * Same-generation retry retains valid bindings and the existing quarantined initial item.
   * @param signal Cancellation signal for the operation.
   * @returns A promise that resolves after the reserved child is activated.
   */

  activate(signal: AbortSignal): Promise<void> {
    signal.throwIfAborted()
    if (this.closed || !this.child.isValid() || !this.input.scope.isCurrent()) throw new TeamError('binding reconstruction required', 'TEAM_BINDING_UNAVAILABLE')
    // Even repeated activation revalidates the current host lease before returning.
    this.authority.authorize(this.input, 'activate')
    if (this.activation) return this.activation
    this.authority.publish(this.input, 'ready')
    if (this.activated) return Promise.resolve()
    const combined = AbortSignal.any([signal, this.cancellation.signal])
    const operation = this.child.activate(combined).then(() => {
      combined.throwIfAborted()
      if (!this.child.isValid() || !this.input.scope.isCurrent()) throw new TeamError('binding reconstruction required', 'TEAM_BINDING_UNAVAILABLE')
      this.activated = true; this.lastFailure = undefined
    }).catch(error => {
      this.lastFailure = error
      try { this.authority.publish(this.input, 'unavailable') } catch { /* admission remains gated by host authority */ }
      throw error
    })
    this.activation = operation
    void operation.then(() => { this.activation = undefined }, () => { this.activation = undefined })
    return operation
  }
  /** Callback invoked only after current generation/lease and binding readiness are proven. */
  /**
   * Describe the release mailbox used by the Team API.
   * @param deliver Mailbox delivery operation to run after authority checks.
   * @returns A promise that resolves after the authorized mailbox delivery completes.
   */
  async releaseMailbox(deliver: () => Promise<void>): Promise<void> {
    if (this.closed || !this.child.isValid() || !this.input.scope.isCurrent()) throw new TeamError('member bindings unavailable', 'TEAM_BINDING_UNAVAILABLE')
    this.authority.authorize(this.input, 'mailbox')
    await deliver()
  }
  /**
   * Close all binding admission before cleanup begins.
   */
  closeAdmission(): void {
    if (this.closed) return
    this.closed = true
    this.cancellation.abort(new TeamError('member bindings closed', 'TEAM_BINDING_UNAVAILABLE'))
    const failures: unknown[] = []
    try { this.authority.publish(this.input, 'unavailable') } catch (error) { failures.push(error) }
    for (const binding of [...this.bindings].reverse()) {
      try { binding.closeAdmission() } catch (error) { failures.push(error) }
    }
    if (failures.length) throw new AggregateError(failures, 'binding admission cutoff failed')
  }

  /**
   * Settle and release member bindings and the reserved child.
   * @param timeoutMs Maximum time allowed for settlement and resource release.
   * @returns A promise that resolves after bindings and the reserved child are released.
   */
  dispose(timeoutMs: number): Promise<void> {
    if (this.disposal) return this.disposal
    const failures: unknown[] = []
    try { this.closeAdmission() } catch (error) { failures.push(error) }
    const deadline = new BindingDeadline(timeoutMs)
    this.disposal = (async () => {
      try {
        for (const binding of [...this.bindings].reverse()) {
          try { await deadline.run(signal => binding.settle(signal)) } catch (error) { failures.push(error) }
          try { await deadline.run(signal => binding.release(signal)) } catch (error) { failures.push(error) }
        }
        try { await deadline.run(signal => this.child.dispose(signal)) } catch (error) { failures.push(error) }
      } finally { deadline.finish() }
      if (failures.length) throw new AggregateError(failures, 'member binding disposal failed')
    })()
    void this.disposal.catch(() => undefined)
    return this.disposal
  }
}


/**
 * Collect journal, host, authority, and cleanup dependencies.
 */
export interface MemberBindingPorts { readonly journal: MemberBindingJournal; readonly host: MemberBindingHost; readonly authority: MemberExecutionAuthority; readonly cleanupTimeoutMs: number }

async function rollback(prepared: PreparedMember, child: ReservedMemberChild | undefined, bindings: readonly DisposableBinding[], ports: MemberBindingPorts, abortChild = true): Promise<void> {
  const failures: unknown[] = []
  // Cut off all bindings synchronously before awaiting a tombstone or provider operation.
  for (const binding of [...bindings].reverse()) { try { binding.closeAdmission() } catch (error) { failures.push(error) } }
  try { ports.authority.publish(prepared.input, 'unavailable') } catch (error) { failures.push(error) }
  const deadline = new BindingDeadline(ports.cleanupTimeoutMs)
  try {
    if (child && abortChild) { try { await deadline.run(signal => child.abort(signal)) } catch (error) { failures.push(error) } }
    try { await abortPrepared(prepared.leases, deadline.signal, deadline) } catch (error) { failures.push(error) }
    for (const binding of [...bindings].reverse()) {
      try { await deadline.run(signal => binding.settle(signal)) } catch (error) { failures.push(error) }
      try { await deadline.run(signal => binding.release(signal)) } catch (error) { failures.push(error) }
    }
    if (child) { try { await deadline.run(signal => child.dispose(signal)) } catch (error) { failures.push(error) } }
  } finally { deadline.finish() }
  if (failures.length) throw new AggregateError(failures, 'pre-active binding cleanup failed')
}

/**
 * One member of an already prepared roster. Roster owner must abort all unused sibling leases.
 * @param prepared Prepared member inputs and binder leases.
 * @param ports Host and persistence ports for member binding.
 * @param signal Cancellation signal for the operation.
 * @returns The active or runtime-unavailable member owner retained for explicit retry.
 */

export async function provisionPreparedMember(prepared: PreparedMember, ports: MemberBindingPorts, signal: AbortSignal): Promise<BoundMemberRuntime> {
  let child: ReservedMemberChild | undefined
  const bindings: DisposableBinding[] = []
  let runtime: BoundMemberRuntime | undefined
  try {
    signal.throwIfAborted()
    await ports.journal.provisioning(prepared.input, prepared.records)
    signal.throwIfAborted()
    child = await acquireBindingResource(() => ports.host.materialize(prepared.input, signal), signal, late => rollback(prepared, late, [], ports))
    signal.throwIfAborted()
    const input = { ...prepared.input, scope: child.scope }
    for (const lease of prepared.leases) {
      signal.throwIfAborted()
      const binding = await acquireBindingResource(() => lease.binder.bind(input, lease.record.payload, lease.value, signal), signal, async late => {
        const validated = await acceptBinding(late, ports.cleanupTimeoutMs)
        await rollback(prepared, undefined, [validated], ports, false)
      })
      await acceptBinding(binding, ports.cleanupTimeoutMs)
      bindings.push(binding); lease.transfer()
      signal.throwIfAborted()
    }
    await child.persistInitialPrompt(prepared.input.spec.initialTask, `gat-initial:${prepared.input.teamId}:${prepared.input.memberId}`, signal)
    signal.throwIfAborted()
    await ports.journal.active(prepared.input, prepared.records)
    runtime = new BoundMemberRuntime(input, prepared.records, child, Object.freeze(bindings), ports.authority)
  } catch (error) {
    let phase: Awaited<ReturnType<MemberBindingJournal['committedPhase']>>
    try { phase = await ports.journal.committedPhase(prepared.input) } catch (observation) {
      const failures = [error, observation]
      try { await rollback(prepared, child, bindings, ports, false) } catch (cleanup) { failures.push(cleanup) }
      throw new AggregateError(failures, 'member commit outcome unknown; execution unavailable')
    }
    if (phase === 'active' && child && child.isValid() && child.scope.isCurrent()) {
      // Uncertain active flush actually committed: preserve ownership for explicit live retry.
      runtime = new BoundMemberRuntime({ ...prepared.input, scope: child.scope }, prepared.records, child, Object.freeze(bindings), ports.authority)
      runtime.lastFailure = error
      try { ports.authority.publish(prepared.input, 'unavailable') } catch { /* activation has not occurred */ }
      return runtime
    }
    const failures: unknown[] = [error]
    try { await rollback(prepared, child, bindings, ports, phase !== 'active') } catch (cleanup) { failures.push(cleanup) }
    if (phase === 'provisioning') {
      try { await ports.journal.failed(prepared.input, prepared.records, 'required member binding failed') } catch (recording) { failures.push(recording) }
    }
    throw new AggregateError(failures, 'required member binding failed')
  }
  try { await runtime.activate(signal) } catch (error) {
    // Binding readiness does not grant an execution lease; preserve active resources for live retry.
    try { ports.authority.publish(prepared.input, 'unavailable') } catch { /* activation remains unavailable */ }
    runtime.lastFailure = error
  }
  return runtime
}

/**
 * Serialized generation reconstruction; caller must settle previous owner before invoking.
 * @param input Exact member identity and normalized input.
 * @param recordsValue Persisted attachment records to validate.
 * @param registry Registry that resolves required attachment binders.
 * @param ports Host and persistence ports for member binding.
 * @param signal Cancellation signal for the operation.
 * @returns The reconstructed runtime after required binders are recovered and activation is attempted.
 */

export async function recoverBoundMember(input: Omit<BinderBindInput, 'scope'>, recordsValue: unknown, registry: import('./member-binders.ts').TeamMemberBinderRegistry, ports: MemberBindingPorts, signal: AbortSignal): Promise<BoundMemberRuntime> {
  const records = validateAttachmentRecords(recordsValue)
  const binders = records.map(record => registry.resolve(record))
  signal.throwIfAborted()
  await ports.host.verifyPersistedChild(input, signal)
  const cleanupChild = async (child: ReservedMemberChild, bindings: readonly DisposableBinding[] = []) => {
    const runtime = new BoundMemberRuntime({ ...input, scope: child.scope }, records, child, bindings, ports.authority)
    await runtime.dispose(ports.cleanupTimeoutMs)
  }
  const child = await acquireBindingResource(() => ports.host.recover(input, signal), signal, cleanupChild)
  const bindings: DisposableBinding[] = []
  try {
    for (let i = 0; i < records.length; i++) {
      signal.throwIfAborted()
      const binding = await acquireBindingResource(() => binders[i]!.recover({ ...input, scope: child.scope }, records[i]!.payload, signal), signal, async late => {
        // The cancellation catch already drains this child; the late callback owns only its resource.
        const binding = await acceptBinding(late, ports.cleanupTimeoutMs)
        const deadline = new BindingDeadline(ports.cleanupTimeoutMs)
        const failures: unknown[] = []
        try {
          try { binding.closeAdmission() } catch (error) { failures.push(error) }
          try { await deadline.run(remaining => binding.settle(remaining)) } catch (error) { failures.push(error) }
          try { await deadline.run(remaining => binding.release(remaining)) } catch (error) { failures.push(error) }
        } finally { deadline.finish() }
        if (failures.length) throw new AggregateError(failures, 'late recovered binding cleanup failed')
      })
      bindings.push(await acceptBinding(binding, ports.cleanupTimeoutMs))
      signal.throwIfAborted()
    }
    const runtime = new BoundMemberRuntime({ ...input, scope: child.scope }, records, child, Object.freeze(bindings), ports.authority)
    try { await runtime.activate(signal) } catch (error) { runtime.lastFailure = error; try { ports.authority.publish(input, 'unavailable') } catch { /* host admission stays denied */ } }
    return runtime
  } catch (error) {
    const runtime = new BoundMemberRuntime({ ...input, scope: child.scope }, records, child, bindings, ports.authority)
    try { await runtime.dispose(ports.cleanupTimeoutMs) } catch (cleanup) { throw new AggregateError([error, cleanup], 'member recovery and cleanup failed') }
    throw error
  }
}

async function acceptBinding(value: DisposableBinding, timeoutMs: number): Promise<DisposableBinding> {
  if (!value || typeof value.closeAdmission !== 'function' || typeof value.settle !== 'function' || typeof value.release !== 'function') {
    const failures: unknown[] = [new TeamError('invalid disposable binding resource', 'TEAM_BINDING_CONFLICT')]
    const deadline = new BindingDeadline(timeoutMs)
    try {
      if (typeof value?.closeAdmission === 'function') { try { value.closeAdmission() } catch (error) { failures.push(error) } }
      if (typeof value?.settle === 'function') { try { await deadline.run(signal => value.settle(signal)) } catch (error) { failures.push(error) } }
      if (typeof value?.release === 'function') { try { await deadline.run(signal => value.release(signal)) } catch (error) { failures.push(error) } }
    } finally { deadline.finish() }
    throw new AggregateError(failures, 'invalid disposable binding resource')
  }
  return value
}

/** GAT-owned serialization: live retry does not reinstall; reconstruction settles the prior owner. */
export class MemberBindingOwner {
  private readonly entries = new Map<string, { generation: string; operation: Promise<BoundMemberRuntime> }>()
  private readonly queues = new Map<string, Promise<unknown>>()
  constructor(private readonly ports: MemberBindingPorts) {}

  /**
   * Run one cleanup operation under the remaining deadline.
   * @param input Exact member identity and normalized input.
   * @param create Factory that creates a runtime after the previous generation has settled.
   * @param signal Cancellation signal for the operation.
   * @returns The callback result, or a rejection when the shared deadline expires.
   */
  run(input: BindingIdentity, create: () => Promise<BoundMemberRuntime>, signal: AbortSignal): Promise<BoundMemberRuntime> {
    const key = JSON.stringify([input.teamId, input.memberId])
    const operation = (this.queues.get(key) ?? Promise.resolve()).catch(() => undefined).then(async () => {
      signal.throwIfAborted()
      const existing = this.entries.get(key)
      if (existing?.generation === input.generation) {
        const runtime = await existing.operation
        await runtime.activate(signal)
        return runtime
      }
      if (existing) await (await existing.operation).dispose(this.ports.cleanupTimeoutMs)
      const next = create()
      this.entries.set(key, { generation: input.generation, operation: next })
      try { return await next } catch (error) { this.entries.delete(key); throw error }
    })
    this.queues.set(key, operation)
    void operation.catch(() => undefined)
    return operation
  }
}
