/** Optional trusted reviewer input for the additive execution composition; GAT Detail Design §§9–10. */
import { createHash } from 'node:crypto'
import { TextDecoder } from 'node:util'
import { symbols, type Context } from '@deepseek-ai/cordis'
import { brandString } from '@deepseek-ai/dsh-brand'
import {
  createReviewPacket, normalizeTaskContract, normalizeCompletionProposal,
  reviewPacketSha256, reviewEvidenceRefs, readReviewRef, taskContractSha256,
} from '@deepseek-ai/dsh-durable-agent'
import type {
  ReviewPacketOptions, ReviewTestReceipt, ReviewKnownRisk, ReviewRationaleRef,
  TaskContract, CompletionProposal,
} from '@deepseek-ai/dsh-durable-agent'
import type { ExecutionReviewInstaller, ExecutionBindingScope } from './execution-binding.ts'
import type { ToolRunContext } from '@deepseek-ai/dsh-tools'

export interface ReviewerAssignment {
  readonly rootSessionId: string
  readonly executionId: string
  readonly sessionId: string
  readonly memberId: string
  readonly generation: number
  readonly taskId: string
  readonly taskRevision: number
  readonly configurationSha256: string
}
export interface ReviewedCandidate extends ReviewerAssignment {
  readonly attemptId: string
  readonly candidateSha256: string
  readonly contractSha256: string
  readonly proposalSha256: string
}
export interface ReviewSelection { readonly reference: string; readonly revision: string }
export interface ReviewAuditEvent {
  readonly kind: 'packet' | 'evidence' | 'rationale'
  readonly status: 'requested' | 'prepared' | 'denied' | 'error'
  readonly reviewerExecutionId: string
  readonly candidateExecutionId: string
  readonly candidateSha256: string
  readonly packetSha256?: string
  readonly ref?: string
  readonly requestId?: string
  readonly rationaleId?: string
  readonly reasonSha256?: string
  readonly bytes?: number
}
export interface ReviewInput {
  readonly selection: ReviewSelection
  readonly reviewer: ReviewerAssignment
  readonly candidate: ReviewedCandidate
  readonly contract: TaskContract
  readonly proposal: CompletionProposal
  readonly policy: Readonly<{
    testReceipts: readonly ReviewTestReceipt[]
    requiredTestSuites: readonly string[]
    knownRisks: readonly ReviewKnownRisk[]
    rationaleRefs: readonly ReviewRationaleRef[]
  }>
  readonly limits: Readonly<{
    maxPacketValidationReads: number
    maxPacketValidationBytes: number
    maxEvidenceCalls: number
    maxEvidenceBytes: number
    maxEvidenceTotalBytes: number
    maxRationaleCalls: number
    maxRationaleAttempts: number
    maxRationaleTotalBytes: number
  }>
  /** Trusted host authenticates the exact current reviewer and stored candidate association. */
  assertCurrent(): void
  /** Notify synchronously before withdrawing this input's authority, candidate, or ACL. */
  subscribeRevocation(cutoff: () => void): () => void
  readRef(request: Readonly<{ ref: string; maxBytes: number; purpose: 'packet-validation' | 'evidence' | 'rationale' }>): Promise<Uint8Array>
  verifyReceipt(receipt: Readonly<ReviewTestReceipt>): Promise<boolean>
  audit(event: Readonly<ReviewAuditEvent>): Promise<void>
}
export interface ReviewInputPort {
  resolve(request: Readonly<{ selection: ReviewSelection; reviewer: ReviewerAssignment }>): Promise<ReviewInput | undefined>
}

declare module '@deepseek-ai/cordis' {
  interface Context {
    gatDurableReviewInput: ReviewInputPort
  }
}

const MAX_PACKET = 65536
const MAX_PACKET_CALLS = 16
const MAX_REF = 65536
const MAX_VALIDATION_READS = 96
const MAX_VALIDATION_BYTES = 262144
const MAX_EVIDENCE_CALLS = 32
const MAX_EVIDENCE_TOTAL = 262144
const MAX_RATIONALE_CALLS = 16
const MAX_RATIONALE_ATTEMPTS = 32
const MAX_RATIONALE_TOTAL = 65536
const HASH = /^[a-f0-9]{64}$/u
const utf8 = new TextDecoder('utf-8', { fatal: true })
function deny(): never { throw new Error('REVIEW_BINDING_UNAVAILABLE') }
function hash(bytes: Uint8Array | string): string { return createHash('sha256').update(bytes).digest('hex') }
function bytes(value: unknown): number { return Buffer.byteLength(JSON.stringify(value), 'utf8') }
function exact(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)
    || Reflect.ownKeys(value).length !== keys.length || keys.some(key => !Object.hasOwn(value, key))) deny()
  return value as Record<string, unknown>
}
function args(value: unknown, keys: readonly string[]): Record<string, string> {
  const result = exact(value, keys)
  if (keys.some(key => typeof result[key] !== 'string' || !(result[key] as string).length
    || Buffer.byteLength(result[key] as string, 'utf8') > 4096)) deny()
  return result as Record<string, string>
}
function selection(scope: ExecutionBindingScope): ReviewSelection {
  const matches = scope.execution.brief.inputs.filter(item => item.reference.startsWith('review-packet:'))
  if (matches.length !== 1) deny()
  const input = matches[0]!
  // The immutable GAT input supplies its version; never infer a current revision.
  const revision = input.revision
  if (typeof revision !== 'string' || !revision.length || revision.length > 128
    || revision.trim() !== revision || revision.includes('\0')
    || !/^review-packet:[a-z0-9][a-z0-9-]{0,127}$/u.test(input.reference)) deny()
  return Object.freeze({ reference: input.reference, revision })
}
function reviewer(scope: ExecutionBindingScope): ReviewerAssignment {
  const e = scope.execution
  return Object.freeze({ rootSessionId: scope.root.id, executionId: e.id, sessionId: scope.agent.id,
    memberId: String(e.memberId), generation: e.generation, taskId: e.taskId,
    taskRevision: e.taskRevision, configurationSha256: hash(JSON.stringify(scope.configuration)) })
}
function equal(a: unknown, b: unknown): boolean { return JSON.stringify(a) === JSON.stringify(b) }
function verifyLimits(l: ReviewInput['limits']): ReviewInput['limits'] {
  const caps = { maxPacketValidationReads: MAX_VALIDATION_READS, maxPacketValidationBytes: MAX_VALIDATION_BYTES,
    maxEvidenceCalls: MAX_EVIDENCE_CALLS, maxEvidenceBytes: MAX_REF, maxEvidenceTotalBytes: MAX_EVIDENCE_TOTAL,
    maxRationaleCalls: MAX_RATIONALE_CALLS, maxRationaleAttempts: MAX_RATIONALE_ATTEMPTS,
    maxRationaleTotalBytes: MAX_RATIONALE_TOTAL }
  exact(l, Object.keys(caps))
  for (const [key, cap] of Object.entries(caps)) {
    const value = l[key as keyof typeof l]
    if (!Number.isSafeInteger(value) || value < 1 || value > cap) deny()
  }
  return Object.freeze(structuredClone(l))
}
const objectSchema = (properties: Record<string, unknown>, required: string[]) =>
  ({ type: 'object' as const, properties, required, additionalProperties: false })
const textSchema = { type: 'string' as const, minLength: 1, maxLength: 4096 }
const unavailable = [{ type: 'text' as const, text: 'Review result unavailable.' }]

function registeredPort(ctx: Context): ReviewInputPort {
  const scoped: unknown = ctx.get('gatDurableReviewInput')
  if (!scoped || typeof scoped !== 'object') deny()
  const owner: unknown = Reflect.get(scoped, symbols.original) ?? scoped
  if (!owner || typeof owner !== 'object' || typeof Reflect.get(owner, 'resolve') !== 'function') deny()
  return owner as ReviewInputPort
}

/** Resolve the optional service only when a reviewer execution is created. */
export function resolveReviewInstaller(ctx: Context): ExecutionReviewInstaller {
  return async scope => {
    const port = registeredPort(ctx)
    const currentPort = () => registeredPort(ctx)
    const resolver = port.resolve
    let cut = false
    const cutoff = () => { if (!cut) { cut = true; scope.revoke() } }
    const ownerOf = (value: unknown): unknown => value && typeof value === 'object'
      ? Reflect.get(value, symbols.original) ?? value : value
    const observePort = scope.ctx.on('internal/service', (name, value) => {
      if (name === 'gatDurableReviewInput' && ownerOf(value) !== port) cutoff()
    })
    scope.own(() => { observePort() })
    const current = () => {
      try {
        scope.assertCurrent()
        if (cut || currentPort() !== port || port.resolve !== resolver) deny()
      } catch { cutoff(); deny() }
    }
    current()
    const selected = selection(scope), assignment = reviewer(scope)
    const resolved = await scope.track(() => resolver.call(port, { selection: selected, reviewer: assignment }))
    current()
    if (resolved === undefined || !equal(resolved.selection, selected) || !equal(resolved.reviewer, assignment)) deny()
    if (resolved.candidate.memberId === assignment.memberId || resolved.candidate.sessionId === assignment.sessionId
      || resolved.candidate.rootSessionId !== assignment.rootSessionId
      || resolved.candidate.configurationSha256 !== assignment.configurationSha256
      || !HASH.test(resolved.candidate.candidateSha256)) deny()
    const candidate = Object.freeze(structuredClone(resolved.candidate))
    if (typeof resolved.assertCurrent !== 'function' || typeof resolved.subscribeRevocation !== 'function'
      || typeof resolved.readRef !== 'function'
      || typeof resolved.verifyReceipt !== 'function' || typeof resolved.audit !== 'function') deny()
    const callbacks = { assertCurrent: resolved.assertCurrent, subscribeRevocation: resolved.subscribeRevocation,
      readRef: resolved.readRef,
      verifyReceipt: resolved.verifyReceipt, audit: resolved.audit }
    const authority = (active = false) => {
      try {
      current()
      if (active) scope.assertActive()
      if (!equal(resolved.selection, selected) || !equal(resolved.reviewer, assignment)
        || !equal(resolved.candidate, candidate)
        || resolved.assertCurrent !== callbacks.assertCurrent
        || resolved.subscribeRevocation !== callbacks.subscribeRevocation || resolved.readRef !== callbacks.readRef
        || resolved.verifyReceipt !== callbacks.verifyReceipt || resolved.audit !== callbacks.audit) deny()
      const assertion: unknown = callbacks.assertCurrent.call(resolved)
      if (assertion !== undefined) {
        if (assertion && typeof assertion === 'object' && 'then' in assertion)
          void Promise.resolve(assertion).catch(() => undefined)
        deny()
      }
      const stored = scope.team.getExecution.call(scope.team, scope.root,
        brandString<ExecutionBindingScope['execution']['id']>(candidate.executionId))
      if (stored.sessionId !== candidate.sessionId || String(stored.memberId) !== candidate.memberId
        || stored.generation !== candidate.generation || stored.taskId !== candidate.taskId
        || stored.taskRevision !== candidate.taskRevision || stored.result === undefined
        || hash(stored.result) !== candidate.candidateSha256) deny()
      current()
      if (active) scope.assertActive()
      } catch { cutoff(); deny() }
    }
    authority()
    let disposeSubscription: unknown
    try { disposeSubscription = callbacks.subscribeRevocation.call(resolved, cutoff) }
    catch { cutoff(); deny() }
    if (typeof disposeSubscription !== 'function') {
      if (disposeSubscription && typeof disposeSubscription === 'object' && 'then' in disposeSubscription) {
        const lateCleanup = scope.track(async () => {
          const late: unknown = await Promise.resolve(disposeSubscription)
          if (typeof late === 'function') {
            const result: unknown = late.call(resolved)
            if (result !== undefined) await Promise.resolve(result)
          }
        })
        void lateCleanup.catch(() => undefined)
      }
      // A malformed subscription cannot leave exclusive ownership reusable.
      scope.own(() => { deny() })
      cutoff(); deny()
    }
    // Preserve the runtime return value: Binding.close joins thenables and quarantines malformed disposal.
    scope.own(() => (disposeSubscription as () => void).call(resolved))
    authority()
    scope.agent.ctx.on('agent/request', async ({ signal }, next) => {
      signal.throwIfAborted()
      authority(true)
      const route = await next()
      signal.throwIfAborted()
      authority(true)
      return route
    })
    const limits = verifyLimits(resolved.limits)
    const contract = normalizeTaskContract(structuredClone(resolved.contract))
    const proposal = normalizeCompletionProposal(structuredClone(resolved.proposal))
    const policy = structuredClone(resolved.policy)
    exact(policy, ['testReceipts', 'requiredTestSuites', 'knownRisks', 'rationaleRefs'])
    if (bytes({ contract, proposal, policy, candidate }) > MAX_PACKET
      || contract.taskId !== candidate.taskId || contract.revision !== candidate.taskRevision
      || taskContractSha256(contract) !== candidate.contractSha256
      || proposal.contractSha256 !== candidate.contractSha256
      || proposal.workerId !== candidate.memberId
      || proposal.attemptId !== candidate.attemptId
      || proposal.taskId !== candidate.taskId) deny()
    // Proposal hash is normalized by the public packet constructor below.
    let validationReads = 0, validationBytes = 0
    const read = async (ref: string, maxBytes: number, purpose: 'packet-validation' | 'evidence' | 'rationale') => {
      authority(purpose !== 'packet-validation')
      const raw = await scope.track(() => callbacks.readRef.call(resolved, { ref, maxBytes, purpose }))
      authority(purpose !== 'packet-validation')
      if (!(raw instanceof Uint8Array) || raw.byteLength > maxBytes) deny()
      return Uint8Array.from(raw)
    }
    const options: ReviewPacketOptions = {
      attemptId: candidate.attemptId, workerId: candidate.memberId,
      reviewerId: assignment.memberId, testReceipts: policy.testReceipts,
      requiredTestSuites: policy.requiredTestSuites, knownRisks: policy.knownRisks,
      rationaleRefs: policy.rationaleRefs,
      readRef: async ref => {
        if (++validationReads > limits.maxPacketValidationReads) deny()
        const allocation = Math.min(MAX_REF, limits.maxPacketValidationBytes - validationBytes)
        if (allocation < 1) deny()
        const raw = await read(ref, allocation, 'packet-validation')
        validationBytes += raw.byteLength
        if (validationBytes > limits.maxPacketValidationBytes) deny()
        return raw
      },
      verifyReceipt: async receipt => {
        authority()
        const verified = await scope.track(() => callbacks.verifyReceipt.call(resolved, receipt))
        authority()
        return verified === true
      },
    }
    const packet = await scope.track(() => createReviewPacket(contract, proposal, options))
    authority()
    const packetSha256 = reviewPacketSha256(packet)
    if (packet.proposalSha256 !== candidate.proposalSha256
      || packet.contractSha256 !== candidate.contractSha256) deny()
    const envelope = Object.freeze({ selection: selected, reviewer: assignment,
      candidate, packetSha256, packet })
    if (bytes(envelope) > MAX_PACKET) deny()
    const evidence = new Map(reviewEvidenceRefs(packet).map(entry => [entry.ref, entry.sha256]))
    const rationale = new Map(packet.rationaleRefs.map(entry => [entry.id, entry]))
    let packetCalls = 0, evidenceCalls = 0, evidenceBytes = 0, evidenceReserved = 0,
      rationaleCalls = 0, rationaleAttempts = 0, rationaleBytes = 0, rationaleReserved = 0
    const prepared = new WeakMap<object, string>()
    const audit = async (kind: ReviewAuditEvent['kind'], status: ReviewAuditEvent['status'],
      ref?: string, requestId?: string, count?: number, rationaleId?: string, reasonSha256?: string) => {
      authority(true)
      await scope.track(() => callbacks.audit.call(resolved, { kind, status, reviewerExecutionId: assignment.executionId,
        candidateExecutionId: candidate.executionId, candidateSha256: candidate.candidateSha256,
        packetSha256, ...ref === undefined ? {} : { ref }, ...requestId === undefined ? {} : { requestId },
        ...count === undefined ? {} : { bytes: count },
        ...rationaleId === undefined ? {} : { rationaleId },
        ...reasonSha256 === undefined ? {} : { reasonSha256 } }))
      authority(true)
    }
    const safe = (exec: object, result: { isError: boolean; value?: unknown; content: unknown; additionalContexts?: readonly unknown[] }) => {
      try {
        authority(true)
        if (result.isError) return unavailable
        if (result.additionalContexts?.length || bytes(result.content) > MAX_PACKET) return unavailable
        const expected = prepared.get(exec)
        if (expected === undefined || JSON.stringify(result.value) !== expected
          || !equal(result.content, [{ type: 'text', text: expected }])) return unavailable
        return undefined
      } catch { return unavailable }
    }
    const make = (name: string, description: string, parameters: ReturnType<typeof objectSchema>,
      run: (a: Record<string, string>, exec: ToolRunContext) => Promise<unknown>, keys: string[]) => {
      scope.own(scope.agent.ctx.tools.register({ name, description, parameters,
        execute: async (raw, exec) => {
          if (exec.agent !== scope.agent || exec.parent !== undefined) deny()
          const a = args(raw, keys)
          authority(true)
          return await scope.track(async () => {
            try {
              const value = await run(a, exec)
              authority(true)
              if (bytes(value) > MAX_PACKET) deny()
              prepared.set(exec, JSON.stringify(value))
              return value
            } catch (error) {
              if (error instanceof TypeError && name !== 'review_get_packet') {
                try { await audit(name === 'review_read_evidence' ? 'evidence' : 'rationale', 'error', a.ref,
                  String(exec.rootCallId), undefined, a.id, a.reason === undefined ? undefined : hash(a.reason))
                } catch { /* Current authority may already be gone. */ }
              }
              deny()
            }
          })
        },
        output: { schema: {}, render: (_a, value) => [{ type: 'text', text: JSON.stringify(value) }] },
        finalizeContent: (exec, result) => safe(exec, result),
      }))
      scope.agent.ctx.on('tools/post-execute', async (exec, result, next) => {
        const decision = await next()
        if (exec.name !== name || exec.agent !== scope.agent) return decision
        try {
          authority(true)
          if (result.additionalContexts?.length || decision.additionalContexts?.length
            || (decision.kind === 'accept' && (Object.hasOwn(decision, 'value')
              || (decision.content !== undefined && bytes(decision.content) > MAX_PACKET)))) deny()
          return decision
        } catch { return { kind: 'block', feedback: unavailable } }
      })
    }
    // Agent lifetime owns this guard; it remains after task-tool cutoff.
    const counted = new WeakSet<object>()
    scope.agent.ctx.tools.guard(exec => {
      if (exec.agent !== scope.agent) return undefined
      if (exec.parent !== undefined || !['review_get_packet', 'review_read_evidence',
        'review_request_rationale', 'team_execution_submit'].includes(exec.name)) return 'Review tool unavailable.'
      if (exec.name === 'review_get_packet' && !counted.has(exec)) {
        counted.add(exec)
        if (++packetCalls > MAX_PACKET_CALLS) return 'Packet attempt budget exhausted.'
      }
      if (exec.name === 'review_read_evidence' && !counted.has(exec)) {
        counted.add(exec)
        if (++evidenceCalls > limits.maxEvidenceCalls) return 'Evidence attempt budget exhausted.'
      }
      if (exec.name === 'review_request_rationale' && !counted.has(exec)) {
        counted.add(exec)
        if (++rationaleAttempts > limits.maxRationaleAttempts) return 'Rationale attempt budget exhausted.'
      }
      try { authority(true); return undefined } catch { return 'Review binding unavailable.' }
    })
    make('review_get_packet', 'Get the frozen public review packet for this exact assignment.',
      objectSchema({}, []), async (_a, exec) => {
        await audit('packet', 'requested', undefined, String(exec.rootCallId))
        await audit('packet', 'prepared', undefined, String(exec.rootCallId), bytes(envelope))
        return envelope
      }, [])
    make('review_read_evidence', 'Read one allowlisted review evidence ref.',
      objectSchema({ ref: textSchema }, ['ref']), async (a, exec) => {
        const ref = a.ref
        if (ref === undefined) deny()
        const digest = evidence.get(ref)
        if (digest === undefined) { await audit('evidence', 'denied', ref, String(exec.rootCallId)); deny() }
        await audit('evidence', 'requested', ref, String(exec.rootCallId))
        const allocation = Math.min(limits.maxEvidenceBytes,
          limits.maxEvidenceTotalBytes - evidenceBytes - evidenceReserved)
        if (allocation < 1) { await audit('evidence', 'denied', ref, String(exec.rootCallId)); deny() }
        evidenceReserved += allocation
        let raw: Uint8Array
        try { raw = await readReviewRef({ ref, sha256: digest }, ref => read(ref, allocation, 'evidence')) }
        finally { evidenceReserved -= allocation }
        evidenceBytes += raw.byteLength
        if (evidenceBytes > limits.maxEvidenceTotalBytes) { await audit('evidence', 'denied', ref, String(exec.rootCallId)); deny() }
        const value = Object.freeze({ ref, sha256: digest, content: utf8.decode(raw) })
        await audit('evidence', 'prepared', ref, String(exec.rootCallId), raw.byteLength)
        return value
      }, ['ref'])
    make('review_request_rationale', 'Request declared rationale with a specific reason; rationale is not evidence.',
      objectSchema({ id: textSchema, reason: textSchema }, ['id', 'reason']), async (a, exec) => {
        const id = a.id, reason = a.reason
        if (id === undefined || reason === undefined) deny()
        if (reason.trim() !== reason || reason.includes('\0')) {
          await audit('rationale', 'denied', undefined, String(exec.rootCallId), undefined, id, hash(reason)); deny()
        }
        const entry = rationale.get(id)
        if (entry === undefined || rationaleCalls >= limits.maxRationaleCalls) {
          await audit('rationale', 'denied', entry?.ref, String(exec.rootCallId), undefined, id, hash(reason)); deny()
        }
        rationaleCalls++
        await audit('rationale', 'requested', entry.ref, String(exec.rootCallId), undefined, id, hash(reason))
        const allocation = Math.min(MAX_REF, limits.maxRationaleTotalBytes - rationaleBytes - rationaleReserved)
        if (allocation < 1) {
          await audit('rationale', 'denied', entry.ref, String(exec.rootCallId), undefined, id, hash(reason)); deny()
        }
        rationaleReserved += allocation
        let raw: Uint8Array
        try { raw = await readReviewRef(entry, ref => read(ref, allocation, 'rationale')) }
        finally { rationaleReserved -= allocation }
        rationaleBytes += raw.byteLength
        if (rationaleBytes > limits.maxRationaleTotalBytes) {
          await audit('rationale', 'denied', entry.ref, String(exec.rootCallId), undefined, id, hash(reason)); deny()
        }
        const value = Object.freeze({ id, ref: entry.ref, sha256: entry.sha256, content: utf8.decode(raw) })
        await audit('rationale', 'prepared', entry.ref, String(exec.rootCallId), raw.byteLength, id, hash(reason))
        return value
      }, ['id', 'reason'])
  }
}
