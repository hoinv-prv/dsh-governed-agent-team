import { normalizeReviewerVerdict, createReviewPacket, readReviewRef, reviewContribution, reviewEvidenceRefs, reviewPacketSha256, REVIEWER_VERDICT_FORMAT, type ReviewPacket, type ReviewPacketOptions, type ReviewerVerdict } from './review-packet.js'

export interface ReviewBinding {
  readonly contractSha256: string
  readonly proposalSha256: string
  readonly attemptId: string
  readonly workerId: string
  readonly reviewerId: string
}
export interface FreshReviewRequest {
  readonly context: 'fresh'
  readonly messages: readonly Readonly<{ role: 'system' | 'user'; content: string }>[]
  readonly tools: ReturnType<typeof reviewContribution>['tools']
}
export interface RationaleAuditEvent {
  readonly reviewPacketSha256: string
  readonly rationaleId: string
  readonly reason: string
  readonly ref: string | null
  readonly sha256: string | null
  readonly status: 'requested' | 'served' | 'denied' | 'error'
  readonly bytes: number
}
export interface ReviewTools {
  readonly readEvidence: (ref: string) => Promise<string>
  readonly requestRationale: (request: Readonly<{ id: string; reason: string }>) => Promise<string>
}
export interface FreshReviewOptions extends ReviewPacketOptions {
  /** Host must implement an actual new session; never append/fork worker or coordinator history. */
  readonly startFresh: (request: Readonly<FreshReviewRequest>, tools: Readonly<ReviewTools>) => Promise<unknown>
  /** Persist append-only request/decision records before releasing rationale content. */
  readonly audit: (event: Readonly<RationaleAuditEvent>) => Promise<void>
  /** Compare with authoritative current identity/state, before dispatch AND after review. */
  readonly assertCurrent: (binding: Readonly<ReviewBinding>) => Promise<boolean>
  readonly rationaleBudget: Readonly<{ maxRequests: number; maxBytes: number }>
}
export interface FreshReviewResult {
  readonly packet: Readonly<ReviewPacket>
  readonly verdict: Readonly<ReviewerVerdict>
  readonly rationaleAudit: readonly Readonly<RationaleAuditEvent>[]
}

const RESPONSE_INSTRUCTION = `Return a JSON object with exactly: format='${REVIEWER_VERDICT_FORMAT}', reviewPacketSha256 (from the user envelope), reviewerId (from packet), status ('meets_criteria'|'changes_required'|'insufficient_evidence'), criteria (one per contract criterion, each exactly {criterionId,status:'met'|'not_met'|'insufficient_evidence',reason,evidenceIds:string[],artifactOutputIds:string[]}), risks:string[]. Every met criterion must cite claim-bound evidence and all its output IDs. Any not_met means changes_required; otherwise any insufficient_evidence means insufficient_evidence; otherwise meets_criteria. References alone do not establish correctness: independently read the actual evidence.`
function fail(reason: string): never { throw new TypeError(`REVIEW_${reason}`) }
function validText(value: unknown): value is string { return typeof value === 'string' && value.length > 0 && value.length <= 4096 && value.trim() === value && !value.includes('\0') }
function validLimit(value: unknown, max: number): value is number { return Number.isSafeInteger(value) && (value as number) >= 0 && (value as number) <= max }

/** Builds host-attested evidence, sends ONLY a fresh bounded payload, validates model output,
 * then rechecks exact bytes and authoritative state. No acceptance/commit is performed.
 * The transport is trusted to honor context:'fresh'; this adapter cannot inspect its hidden history. */
export async function runFreshReview(contractInput: unknown, proposalInput: unknown, options: Readonly<FreshReviewOptions>): Promise<Readonly<FreshReviewResult>> {
  const { startFresh, audit, assertCurrent, readRef, verifyReceipt } = options
  if ([startFresh, audit, assertCurrent, readRef, verifyReceipt].some(fn => typeof fn !== 'function')) fail('HOST_ADAPTER_REQUIRED')
  const budget = options.rationaleBudget
  if (!budget || Object.getPrototypeOf(budget) !== Object.prototype || Object.keys(budget).length !== 2 || !validLimit(budget.maxRequests, 16) || !validLimit(budget.maxBytes, 64 * 1024)) fail('RATIONALE_BUDGET_INVALID')
  const maxRequests = budget.maxRequests, maxBytes = budget.maxBytes
  const packet = await createReviewPacket(contractInput, proposalInput, options)
  const packetHash = reviewPacketSha256(packet)
  const binding = Object.freeze({ contractSha256: packet.contractSha256, proposalSha256: packet.proposalSha256, attemptId: packet.proposal.attemptId, workerId: packet.proposal.workerId, reviewerId: packet.reviewerId })
  const checkCurrent = async () => {
    let current = false
    try { current = await assertCurrent(binding) === true } catch { /* Never expose host exceptions. */ }
    if (!current) fail('CURRENT_STATE_MISMATCH')
  }
  await checkCurrent()
  const auditEvents: Readonly<RationaleAuditEvent>[] = []
  let rationaleRequests = 0, rationaleBytes = 0, evidenceReads = 0, evidenceBytes = 0
  let active = true, fatal: string | undefined
  const observedArtifacts = new Set<string>(), observedEvidence = new Set<string>()
  const pending = new Set<Promise<unknown>>()
  const track = <T>(operation: () => Promise<T>): Promise<T> => {
    const promise = operation()
    pending.add(promise)
    void promise.then(() => pending.delete(promise), () => pending.delete(promise))
    return promise
  }
  const appendAudit = async (event: Omit<RationaleAuditEvent, 'reviewPacketSha256'>) => {
    const entry = Object.freeze({ reviewPacketSha256: packetHash, ...event })
    try { await audit(entry) } catch { fatal = 'AUDIT_UNAVAILABLE'; fail(fatal) }
    auditEvents.push(entry)
  }
  const ensureActive = () => { if (!active) fail('REVIEW_TOOLS_CLOSED'); if (fatal) fail(fatal) }
  const evidenceRefs = reviewEvidenceRefs(packet)
  const tools: Readonly<ReviewTools> = Object.freeze({
    readEvidence: (ref: string) => track(async () => {
      ensureActive()
      if (!validText(ref)) fail('EVIDENCE_REQUEST_INVALID')
      const entry = evidenceRefs.find(e => e.ref === ref)
      if (!entry) fail('EVIDENCE_REF_DENIED')
      evidenceReads += 1
      if (evidenceReads > 32) { fatal = 'EVIDENCE_BUDGET_EXCEEDED'; fail(fatal) }
      let bytes: Uint8Array
      try { bytes = await readReviewRef(entry, readRef) } catch { fatal = 'EVIDENCE_READ_FAILED'; fail(fatal) }
      evidenceBytes += bytes.byteLength
      if (bytes.byteLength > 64 * 1024 || evidenceBytes > 256 * 1024) { fatal = 'EVIDENCE_BUDGET_EXCEEDED'; fail(fatal) }
      let content: string
      try { content = new TextDecoder('utf-8', { fatal: true }).decode(bytes) } catch { fail('EVIDENCE_ENCODING_INVALID') }
      for (const a of packet.proposal.artifacts) if (a.ref === ref) observedArtifacts.add(a.outputId)
      for (const e of packet.proposal.evidence) if (e.ref === ref) observedEvidence.add(e.id)
      ensureActive()
      return content
    }),
    requestRationale: (request: Readonly<{ id: string; reason: string }>) => track(async () => {
      ensureActive()
      rationaleRequests += 1
      if (rationaleRequests > 32) { fatal = 'RATIONALE_CALL_LIMIT'; fail(fatal) }
      const valid = request && Object.getPrototypeOf(request) === Object.prototype && Object.keys(request).length === 2 && validText(request.id) && validText(request.reason)
      const id = valid ? request.id : 'invalid-request', reason = valid ? request.reason : 'Invalid rationale request'
      const entry = valid ? packet.rationaleRefs.find(r => r.id === id) : undefined
      const event = { rationaleId: id, reason, ref: entry?.ref ?? null, sha256: entry?.sha256 ?? null, bytes: 0 }
      if (!valid || !entry || rationaleRequests > maxRequests) {
        await appendAudit({ ...event, status: 'denied' })
        fail('RATIONALE_DENIED')
      }
      await appendAudit({ ...event, status: 'requested' })
      let terminal = false
      try {
        ensureActive()
        let bytes: Uint8Array
        try { bytes = await readReviewRef(entry, readRef) } catch { fail('RATIONALE_UNAVAILABLE') }
        if (bytes.byteLength + rationaleBytes > maxBytes) {
          await appendAudit({ ...event, status: 'denied', bytes: bytes.byteLength })
          terminal = true
          fail('RATIONALE_BUDGET_EXCEEDED')
        }
        let content: string
        try { content = new TextDecoder('utf-8', { fatal: true }).decode(bytes) } catch { fail('RATIONALE_ENCODING_INVALID') }
        ensureActive()
        rationaleBytes += bytes.byteLength
        await appendAudit({ ...event, status: 'served', bytes: bytes.byteLength })
        terminal = true
        // A detached transport can close while the durable audit is being persisted.
        // Append a compensating terminal error: the audited grant was NOT delivered.
        if (!active) { await appendAudit({ ...event, status: 'error' }); fail('REVIEW_TOOLS_CLOSED') }
        ensureActive()
        return content
      } catch (error) {
        if (!terminal && fatal !== 'AUDIT_UNAVAILABLE') await appendAudit({ ...event, status: 'error' })
        throw error
      }
    }),
  })
  const contribution = reviewContribution(packet)
  const request: Readonly<FreshReviewRequest> = Object.freeze({ context: 'fresh', messages: Object.freeze([
    Object.freeze({ role: 'system' as const, content: `${packet.instruction}\n${RESPONSE_INSTRUCTION}` }),
    Object.freeze({ role: 'user' as const, content: contribution.prompt }),
  ]), tools: contribution.tools })
  let result: unknown, transportFailed = false
  try { result = await startFresh(request, tools) } catch { transportFailed = true } finally { active = false }
  const unfinishedTools = pending.size > 0
  await Promise.allSettled([...pending])
  if (fatal) fail(fatal)
  if (transportFailed) fail('TRANSPORT_FAILED')
  if (unfinishedTools) fail('INCOMPLETE_TOOL_CALL')
  if (typeof result === 'string') {
    if (!result.length || Buffer.byteLength(result, 'utf8') > 64 * 1024) fail('VERDICT_ENVELOPE_TOO_LARGE')
    try { result = JSON.parse(result) as unknown } catch { fail('VERDICT_JSON_INVALID') }
  }
  const verdict = normalizeReviewerVerdict(result, packet)
  // A model must actually inspect the cited content, not just echo IDs from worker claims.
  for (const criterion of verdict.criteria) {
    if (criterion.artifactOutputIds.some(id => !observedArtifacts.has(id)) || criterion.evidenceIds.some(id => !observedEvidence.has(id))) fail('VERDICT_UNREAD_EVIDENCE')
  }
  // Rebuild from frozen inputs and the same host trust functions, never from model output.
  const rechecked = await createReviewPacket(packet.contract, packet.proposal, { attemptId: binding.attemptId, workerId: binding.workerId, reviewerId: binding.reviewerId, testReceipts: packet.testReceipts, requiredTestSuites: packet.requiredTestSuites, knownRisks: packet.knownRisks, rationaleRefs: packet.rationaleRefs, readRef, verifyReceipt })
  if (reviewPacketSha256(rechecked) !== packetHash) fail('PACKET_CHANGED')
  await checkCurrent()
  return Object.freeze({ packet, verdict, rationaleAudit: Object.freeze([...auditEvents]) })
}
