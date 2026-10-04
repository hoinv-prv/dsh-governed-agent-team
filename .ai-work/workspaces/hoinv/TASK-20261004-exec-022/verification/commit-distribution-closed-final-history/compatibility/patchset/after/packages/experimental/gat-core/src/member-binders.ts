/** Required binder registrations, authoritative reference pins and exactly-once prepared ownership. */
import { attachmentRecord, validateAttachmentRecords, validateAttachmentRequests } from './attachments.ts'
import { BindingDeadline, acquireBindingResource } from './binding-deadline.ts'
import { TeamError } from './error.ts'
import type { JsonValue, TeamMemberAttachmentRecord, TeamMemberAttachmentRequest, TeamMemberSpec } from './types.ts'


/**
 * Identify one Team member and its live binding generation.
 */
export interface BindingIdentity {
  readonly teamId: string
  readonly memberId: string
  readonly memberName: string
  readonly generation: string
}

/**
 * Describe one member-scoped prompt and tool contribution.
 */
export interface CapabilityContribution {
  readonly key: string
  readonly prompt: string
  readonly tools: readonly { readonly name: string; readonly schema: JsonValue; readonly capability?: 'read' | 'effect'; readonly invoke: (args: unknown) => Promise<unknown> }[]
}
/** Host-owned least-privileged port; it grants no Team mutation or execution authority. */
export interface MemberCapabilityScope {
  isCurrent(): boolean
  authorize(action: 'read' | 'effect' | 'request'): void
  install(contribution: CapabilityContribution): () => void
  beforeRequest(refresh: () => Promise<void>): () => void
  replacePrompt(key: string, prompt: string): void
}

/**
 * Provide normalized member data and bounded attachment input to prepare.
 */
export interface BinderPrepareInput extends BindingIdentity {
  readonly workspaceRealpath: string
  readonly spec: TeamMemberSpec
  readonly payload: JsonValue
}

/**
 * Provide the exact member capability scope to a binder.
 */
export interface BinderBindInput extends BindingIdentity {
  readonly workspaceRealpath: string
  readonly scope: MemberCapabilityScope
}

/**
 * Provide the persisted member scope used to reconstruct a binding.
 */
export type BinderRecoverInput = BinderBindInput

/**
 * Pair the canonical persisted attachment with its prepared process-local value.
 */
export interface PreparedAttachment<Prepared = unknown> {
  readonly attachment: JsonValue
  readonly value: Prepared
  abort(signal: AbortSignal): Promise<void>
}

/**
 * Expose admission cutoff, settlement, and release for one installed binding.
 */
export interface DisposableBinding {
  closeAdmission(): void
  settle(signal: AbortSignal): Promise<void>
  release(signal: AbortSignal): Promise<void>
}

/**
 * Define the prepare, bind, and recovery callbacks for one attachment protocol.
 */
export interface TeamMemberBinder<Prepared = unknown> {
  readonly id: string
  readonly protocolVersion: number
  prepare(input: BinderPrepareInput, signal: AbortSignal): Promise<PreparedAttachment<Prepared>>
  bind(input: BinderBindInput, attachment: JsonValue, prepared: Prepared, signal: AbortSignal): Promise<DisposableBinding>
  recover(input: BinderRecoverInput, attachment: JsonValue, signal: AbortSignal): Promise<DisposableBinding>
}

function unavailable(): never { throw new TeamError('required member binder is unavailable', 'TEAM_BINDER_UNAVAILABLE') }

/** Reference provider MUST enumerate authoritative durable records, including inactive members. */
export class TeamMemberBinderRegistry {
  private readonly registrations = new Map<string, TeamMemberBinder>()
  private readonly pins = new Map<string, number>()
  private readonly references: () => Iterable<readonly TeamMemberAttachmentRecord[]>
  constructor(references: () => Iterable<readonly TeamMemberAttachmentRecord[]>) { this.references = references }
  private key(id: string, version: number): string { return `${id}:${version}` }

  /**
   * Register one binder protocol until no durable member references it.
   * @param binder Binder implementation to register for its id and protocol version.
   * @returns A disposer that unregisters this binder when no member references it.
   */
  register(binder: TeamMemberBinder): () => void {
    validateAttachmentRequests([{ binderId: binder.id, protocolVersion: binder.protocolVersion, required: true, payload: null }])
    const key = this.key(binder.id, binder.protocolVersion)
    if (this.registrations.has(key)) throw new TeamError('member binder already registered', 'TEAM_BINDER_CONFLICT')
    // Capture registration identity rather than trusting mutable participant properties later.
    const captured: TeamMemberBinder = Object.freeze({
      id: binder.id, protocolVersion: binder.protocolVersion,
      prepare: binder.prepare.bind(binder), bind: binder.bind.bind(binder), recover: binder.recover.bind(binder),
    })
    this.registrations.set(key, captured)
    return () => {
      if (this.registrations.get(key) !== captured) return
      if (this.pins.get(key)) throw new TeamError('member binder has a pending owner', 'TEAM_BINDER_REFERENCED')
      for (const records of this.references()) {
        if (records.some(record => this.key(record.binderId, record.protocolVersion) === key)) {
          throw new TeamError('durable member still references binder', 'TEAM_BINDER_REFERENCED')
        }
      }
      this.registrations.delete(key)
    }
  }

  /**
   * Resolve the registered binder for an attachment protocol version.
   * @param request Host-selected mission approval or transition request.
   * @returns The binder registered for the requested id and protocol version.
   */
  resolve(request: Pick<TeamMemberAttachmentRequest, 'binderId' | 'protocolVersion'>): TeamMemberBinder {
    return this.registrations.get(this.key(request.binderId, request.protocolVersion)) ?? unavailable()
  }

  /**
   * Hold a binder registration while an owner is being prepared.
   * @param request Host-selected mission approval or transition request.
   * @returns An idempotent release callback for the temporary binder pin.
   */
  pin(request: Pick<TeamMemberAttachmentRequest, 'binderId' | 'protocolVersion'>): () => void {
    this.resolve(request)
    const key = this.key(request.binderId, request.protocolVersion)
    this.pins.set(key, (this.pins.get(key) ?? 0) + 1)
    let released = false
    return () => { if (released) return; released = true; this.pins.set(key, (this.pins.get(key) as number) - 1) }
  }
}

/** A lease's original callback is never called twice or after successful transfer. */
export class PreparedMemberAttachment {
  /**
   * Binder registered for this attachment protocol.
   */
  readonly binder: TeamMemberBinder
  /**
   * Validated attachment record persisted for this member.
   */
  readonly record: TeamMemberAttachmentRecord
  /**
   * Process-local value returned by the binder prepare callback.
   */
  readonly value: unknown
  private state: 'prepared' | 'transferred' | 'aborted' = 'prepared'
  private abortPromise?: Promise<void>
  private readonly abortCallback: (signal: AbortSignal) => Promise<void>
  /**
   * Retain ownership of one safely captured prepared participant resource.
   * @param binder Registered participant protocol.
   * @param record Validated durable attachment identity.
   * @param prepared Raw participant resource whose opaque value is read under ownership.
   * @param unpin Release the registration only after transfer or physical abort settlement.
   * @param capturedAbort Abort callback captured once before lease construction.
   */
  constructor(
    binder: TeamMemberBinder,
    record: TeamMemberAttachmentRecord,
    prepared: PreparedAttachment,
    private readonly unpin: () => void = () => {},
    capturedAbort?: PreparedAttachment['abort'],
  ) {
    this.binder = binder; this.record = record; this.value = prepared.value
    this.abortCallback = capturedAbort ?? prepared.abort.bind(prepared)
  }

  /**
   * Transfer prepared-resource cleanup ownership to a successful binding.
   */
  transfer(): void {
    if (this.state !== 'prepared') throw new TeamError('prepared ownership conflict', 'TEAM_BINDING_CONFLICT')
    this.state = 'transferred'
    this.unpin()
  }
  /**
   * Abort this prepared resource once unless ownership was transferred.
   * @param signal Cancellation signal for the operation.
   * @returns A promise that resolves after the prepared resource cleanup settles.
   */
  abort(signal: AbortSignal): Promise<void> {
    if (this.state === 'transferred') return Promise.resolve()
    if (!this.abortPromise) {
      this.state = 'aborted'
      this.abortPromise = Promise.resolve().then(() => this.abortCallback(signal)).finally(this.unpin)
      void this.abortPromise.catch(() => undefined)
    }
    return this.abortPromise
  }
}


/**
 * Abort untransferred prepared leases in reverse order.
 * @param leases Prepared attachment leases to abort.
 * @param signal Cancellation signal for the operation.
 * @param deadline Shared cleanup deadline used by the lease abort callbacks.
 * @returns A promise that resolves after all untransferred leases are aborted.
 */
export async function abortPrepared(
  leases: readonly PreparedMemberAttachment[],
  signal: AbortSignal,
  deadline?: BindingDeadline,
): Promise<void> {
  const failures: unknown[] = []
  for (const lease of [...leases].reverse()) {
    try {
      await (deadline ? deadline.run(remaining => lease.abort(remaining)) : lease.abort(signal))
    } catch (error) { failures.push(error) }
  }
  if (failures.length) throw new AggregateError(failures, 'required attachment preparation cleanup failed')
}


/**
 * Hold a normalized member input, canonical records, and prepared leases.
 */
export interface PreparedMember {
  readonly input: BinderPrepareInput
  readonly leases: readonly PreparedMemberAttachment[]
  readonly records: readonly TeamMemberAttachmentRecord[]
}

/** Normalized spec detachment is independent of attachment envelope depth/node/string limits. */
function freezeSpec<T>(value: T, ancestors = new Set<object>()): T {
  if (value === null || value === undefined || typeof value === 'string' || typeof value === 'boolean') return value
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value !== 'object' || ancestors.has(value)) throw new TeamError('invalid normalized binding spec', 'TEAM_INVALID_CONFIG')
  const prototype: unknown = Object.getPrototypeOf(value)
  if (Array.isArray(value) ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null) throw new TeamError('invalid normalized binding spec', 'TEAM_INVALID_CONFIG')
  ancestors.add(value)
  try {
    const descriptors = Object.getOwnPropertyDescriptors(value)
    if (Object.getOwnPropertySymbols(value).length) throw new TeamError('invalid normalized binding spec', 'TEAM_INVALID_CONFIG')
    const result = Array.isArray(value) ? [] : {}
    for (const key of Object.keys(descriptors)) {
      if (Array.isArray(value) && key === 'length') continue
      const entry = descriptors[key] as PropertyDescriptor
      if (!('value' in entry) || !entry.enumerable) throw new TeamError('invalid normalized binding spec', 'TEAM_INVALID_CONFIG')
      Object.defineProperty(result, key, { value: freezeSpec(entry.value, ancestors), enumerable: true })
    }
    return Object.freeze(result) as T
  } finally { ancestors.delete(value) }
}

/**
 * Validate/resolve ALL requests first, then prepare in declaration order. No row/child is created.
 * @param registry Registry that resolves required attachment binders.
 * @param rawInputs Normalized member inputs to prepare.
 * @param signal Cancellation signal for the operation.
 * @param cleanupTimeoutMs Maximum duration allowed for cleanup.
 * @param observeLateFailure Owning Team sink retaining late participant cleanup failures.
 * @returns A frozen ordered list of prepared members with validated persisted records.
 */

export async function prepareMembers(
  registry: TeamMemberBinderRegistry,
  rawInputs: readonly Omit<BinderPrepareInput, 'payload'>[],
  signal: AbortSignal,
  cleanupTimeoutMs = 5_000,
  observeLateFailure?: (error: unknown) => void,
): Promise<readonly PreparedMember[]> {
  const inputs = rawInputs.map(input => Object.freeze({ ...input, spec: freezeSpec(input.spec) }))
  const requested = inputs.map(input => validateAttachmentRequests(input.spec.attachments ?? []).map(request => ({
    request, binder: registry.resolve(request),
  })))
  const leases: PreparedMemberAttachment[] = []
  const members: PreparedMember[] = []
  let cleanupDeadline: BindingDeadline | undefined
  const cleanup = () => cleanupDeadline ??= new BindingDeadline(cleanupTimeoutMs, observeLateFailure)
  try {
    for (let index = 0; index < inputs.length; index++) {
      const input = inputs[index] as (typeof inputs)[number]
      const memberLeases: PreparedMemberAttachment[] = []
      for (const { request, binder } of requested[index] as (typeof requested)[number]) {
        signal.throwIfAborted()
        const unpin = registry.pin(request)
        const acquisition = { acquired: false }
        let capturedAbort: PreparedAttachment['abort'] | undefined
        const captureAbort = (prepared: PreparedAttachment): PreparedAttachment['abort'] => {
          if (capturedAbort) return capturedAbort
          const callback: unknown = Reflect.get(prepared, 'abort')
          if (typeof callback !== 'function') throw new TeamError('invalid prepared binding resource', 'TEAM_BINDING_CONFLICT')
          capturedAbort = remaining => Reflect.apply(callback, prepared, [remaining]) as Promise<void>
          return capturedAbort
        }
        const lateAbort = async (prepared: PreparedAttachment, shared?: BindingDeadline) => {
          const deadline = shared ?? new BindingDeadline(cleanupTimeoutMs, observeLateFailure)
          try { await deadline.run((remaining) => {
            const abort = captureAbort(prepared)
            const pending = Promise.resolve().then(() => abort(remaining)).finally(unpin)
            return pending
          }) } finally { if (!shared) deadline.finish() }
        }
        let prepared: PreparedAttachment
        try {
          prepared = await acquireBindingResource(
            () => Promise.resolve().then(() => binder.prepare({ ...input, payload: request.payload }, signal)).then(
              (value) => { acquisition.acquired = true; return value }, (error: unknown) => { unpin(); throw error },
            ), signal, value => lateAbort(value),
            observeLateFailure,
          )
        } catch (error) {
          // A cancelled unresolved participant retains its registration until it really settles.
          if (!signal.aborted && !acquisition.acquired) unpin()
          throw error
        }
        // Track raw successful lease BEFORE validating its returned payload.
        let lease: PreparedMemberAttachment
        try {
          const candidate = prepared as unknown as Partial<PreparedAttachment> | null | undefined
          if (!candidate) {
            throw new TeamError('invalid prepared binding resource', 'TEAM_BINDING_CONFLICT')
          }
          captureAbort(prepared)
          const record = attachmentRecord(request, prepared.attachment)
          lease = new PreparedMemberAttachment(binder, record, prepared, unpin, capturedAbort)
        } catch (error) {
          try { await lateAbort(prepared, cleanup()) } catch (failure) { throw new AggregateError([error, failure], 'prepared output rejected and abort failed') }
          throw error
        }
        leases.push(lease); memberLeases.push(lease)
        signal.throwIfAborted()
      }
      const records = validateAttachmentRecords(memberLeases.map(lease => lease.record))
      members.push(Object.freeze({ input: { ...input, payload: null }, leases: Object.freeze(memberLeases), records }))
    }
    return Object.freeze(members)
  } catch (error) {
    const deadline = cleanup()
    try { await abortPrepared(leases, deadline.signal, deadline) } catch (cleanup) { throw new AggregateError([error, cleanup], 'required attachment prepare-all failed') }
    finally { deadline.finish() }
    throw error
  }
}
