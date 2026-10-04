import { normalizeReviewerVerdict, createReviewPacket, readReviewRef, reviewContribution, reviewEvidenceRefs, reviewPacketSha256, REVIEWER_VERDICT_FORMAT } from './review-packet.js';
const RESPONSE_INSTRUCTION = `Return a JSON object with exactly: format='${REVIEWER_VERDICT_FORMAT}', reviewPacketSha256 (from the user envelope), reviewerId (from packet), status ('meets_criteria'|'changes_required'|'insufficient_evidence'), criteria (one per contract criterion, each exactly {criterionId,status:'met'|'not_met'|'insufficient_evidence',reason,evidenceIds:string[],artifactOutputIds:string[]}), risks:string[]. Every met criterion must cite claim-bound evidence and all its output IDs. Any not_met means changes_required; otherwise any insufficient_evidence means insufficient_evidence; otherwise meets_criteria. References alone do not establish correctness: independently read the actual evidence.`;
function fail(reason) { throw new TypeError(`REVIEW_${reason}`); }
function validText(value) { return typeof value === 'string' && value.length > 0 && value.length <= 4096 && value.trim() === value && !value.includes('\0'); }
function validLimit(value, max) { return Number.isSafeInteger(value) && value >= 0 && value <= max; }
/** Builds host-attested evidence, sends ONLY a fresh bounded payload, validates model output,
 * then rechecks exact bytes and authoritative state. No acceptance/commit is performed.
 * The transport is trusted to honor context:'fresh'; this adapter cannot inspect its hidden history. */
export async function runFreshReview(contractInput, proposalInput, options) {
    const { startFresh, audit, assertCurrent, readRef, verifyReceipt } = options;
    if ([startFresh, audit, assertCurrent, readRef, verifyReceipt].some(fn => typeof fn !== 'function'))
        fail('HOST_ADAPTER_REQUIRED');
    const budget = options.rationaleBudget;
    if (!budget || Object.getPrototypeOf(budget) !== Object.prototype || Object.keys(budget).length !== 2 || !validLimit(budget.maxRequests, 16) || !validLimit(budget.maxBytes, 64 * 1024))
        fail('RATIONALE_BUDGET_INVALID');
    const maxRequests = budget.maxRequests, maxBytes = budget.maxBytes;
    const packet = await createReviewPacket(contractInput, proposalInput, options);
    const packetHash = reviewPacketSha256(packet);
    const binding = Object.freeze({ contractSha256: packet.contractSha256, proposalSha256: packet.proposalSha256, attemptId: packet.proposal.attemptId, workerId: packet.proposal.workerId, reviewerId: packet.reviewerId });
    const checkCurrent = async () => {
        let current = false;
        try {
            current = await assertCurrent(binding) === true;
        }
        catch { /* Never expose host exceptions. */ }
        if (!current)
            fail('CURRENT_STATE_MISMATCH');
    };
    await checkCurrent();
    const auditEvents = [];
    let rationaleRequests = 0, rationaleBytes = 0, evidenceReads = 0, evidenceBytes = 0;
    let active = true, fatal;
    const observedArtifacts = new Set(), observedEvidence = new Set();
    const pending = new Set();
    const track = (operation) => {
        const promise = operation();
        pending.add(promise);
        void promise.then(() => pending.delete(promise), () => pending.delete(promise));
        return promise;
    };
    const appendAudit = async (event) => {
        const entry = Object.freeze({ reviewPacketSha256: packetHash, ...event });
        try {
            await audit(entry);
        }
        catch {
            fatal = 'AUDIT_UNAVAILABLE';
            fail(fatal);
        }
        auditEvents.push(entry);
    };
    const ensureActive = () => { if (!active)
        fail('REVIEW_TOOLS_CLOSED'); if (fatal)
        fail(fatal); };
    const evidenceRefs = reviewEvidenceRefs(packet);
    const tools = Object.freeze({
        readEvidence: (ref) => track(async () => {
            ensureActive();
            if (!validText(ref))
                fail('EVIDENCE_REQUEST_INVALID');
            const entry = evidenceRefs.find(e => e.ref === ref);
            if (!entry)
                fail('EVIDENCE_REF_DENIED');
            evidenceReads += 1;
            if (evidenceReads > 32) {
                fatal = 'EVIDENCE_BUDGET_EXCEEDED';
                fail(fatal);
            }
            let bytes;
            try {
                bytes = await readReviewRef(entry, readRef);
            }
            catch {
                fatal = 'EVIDENCE_READ_FAILED';
                fail(fatal);
            }
            evidenceBytes += bytes.byteLength;
            if (bytes.byteLength > 64 * 1024 || evidenceBytes > 256 * 1024) {
                fatal = 'EVIDENCE_BUDGET_EXCEEDED';
                fail(fatal);
            }
            let content;
            try {
                content = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
            }
            catch {
                fail('EVIDENCE_ENCODING_INVALID');
            }
            for (const a of packet.proposal.artifacts)
                if (a.ref === ref)
                    observedArtifacts.add(a.outputId);
            for (const e of packet.proposal.evidence)
                if (e.ref === ref)
                    observedEvidence.add(e.id);
            ensureActive();
            return content;
        }),
        requestRationale: (request) => track(async () => {
            ensureActive();
            rationaleRequests += 1;
            if (rationaleRequests > 32) {
                fatal = 'RATIONALE_CALL_LIMIT';
                fail(fatal);
            }
            const valid = request && Object.getPrototypeOf(request) === Object.prototype && Object.keys(request).length === 2 && validText(request.id) && validText(request.reason);
            const id = valid ? request.id : 'invalid-request', reason = valid ? request.reason : 'Invalid rationale request';
            const entry = valid ? packet.rationaleRefs.find(r => r.id === id) : undefined;
            const event = { rationaleId: id, reason, ref: entry?.ref ?? null, sha256: entry?.sha256 ?? null, bytes: 0 };
            if (!valid || !entry || rationaleRequests > maxRequests) {
                await appendAudit({ ...event, status: 'denied' });
                fail('RATIONALE_DENIED');
            }
            await appendAudit({ ...event, status: 'requested' });
            let terminal = false;
            try {
                ensureActive();
                let bytes;
                try {
                    bytes = await readReviewRef(entry, readRef);
                }
                catch {
                    fail('RATIONALE_UNAVAILABLE');
                }
                if (bytes.byteLength + rationaleBytes > maxBytes) {
                    await appendAudit({ ...event, status: 'denied', bytes: bytes.byteLength });
                    terminal = true;
                    fail('RATIONALE_BUDGET_EXCEEDED');
                }
                let content;
                try {
                    content = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
                }
                catch {
                    fail('RATIONALE_ENCODING_INVALID');
                }
                ensureActive();
                rationaleBytes += bytes.byteLength;
                await appendAudit({ ...event, status: 'served', bytes: bytes.byteLength });
                terminal = true;
                // A detached transport can close while the durable audit is being persisted.
                // Append a compensating terminal error: the audited grant was NOT delivered.
                if (!active) {
                    await appendAudit({ ...event, status: 'error' });
                    fail('REVIEW_TOOLS_CLOSED');
                }
                ensureActive();
                return content;
            }
            catch (error) {
                if (!terminal && fatal !== 'AUDIT_UNAVAILABLE')
                    await appendAudit({ ...event, status: 'error' });
                throw error;
            }
        }),
    });
    const contribution = reviewContribution(packet);
    const request = Object.freeze({ context: 'fresh', messages: Object.freeze([
            Object.freeze({ role: 'system', content: `${packet.instruction}\n${RESPONSE_INSTRUCTION}` }),
            Object.freeze({ role: 'user', content: contribution.prompt }),
        ]), tools: contribution.tools });
    let result, transportFailed = false;
    try {
        result = await startFresh(request, tools);
    }
    catch {
        transportFailed = true;
    }
    finally {
        active = false;
    }
    const unfinishedTools = pending.size > 0;
    await Promise.allSettled([...pending]);
    if (fatal)
        fail(fatal);
    if (transportFailed)
        fail('TRANSPORT_FAILED');
    if (unfinishedTools)
        fail('INCOMPLETE_TOOL_CALL');
    if (typeof result === 'string') {
        if (!result.length || Buffer.byteLength(result, 'utf8') > 64 * 1024)
            fail('VERDICT_ENVELOPE_TOO_LARGE');
        try {
            result = JSON.parse(result);
        }
        catch {
            fail('VERDICT_JSON_INVALID');
        }
    }
    const verdict = normalizeReviewerVerdict(result, packet);
    // A model must actually inspect the cited content, not just echo IDs from worker claims.
    for (const criterion of verdict.criteria) {
        if (criterion.artifactOutputIds.some(id => !observedArtifacts.has(id)) || criterion.evidenceIds.some(id => !observedEvidence.has(id)))
            fail('VERDICT_UNREAD_EVIDENCE');
    }
    // Rebuild from frozen inputs and the same host trust functions, never from model output.
    const rechecked = await createReviewPacket(packet.contract, packet.proposal, { attemptId: binding.attemptId, workerId: binding.workerId, reviewerId: binding.reviewerId, testReceipts: packet.testReceipts, requiredTestSuites: packet.requiredTestSuites, knownRisks: packet.knownRisks, rationaleRefs: packet.rationaleRefs, readRef, verifyReceipt });
    if (reviewPacketSha256(rechecked) !== packetHash)
        fail('PACKET_CHANGED');
    await checkCurrent();
    return Object.freeze({ packet, verdict, rationaleAudit: Object.freeze([...auditEvents]) });
}
//# sourceMappingURL=review-host.js.map