import { createHash } from 'node:crypto';
export const TASK_CONTRACT_FORMAT = 'durable-agent-task-contract/1';
export const COMPLETION_PROPOSAL_FORMAT = 'durable-agent-completion-proposal/1';
const HASH = /^[a-f0-9]{64}$/u;
function fail(reason) { throw new TypeError(`TASK_CONTRACT_${reason}`); }
function object(value, keys) {
    if (!value || typeof value !== 'object' || Array.isArray(value) || Object.getPrototypeOf(value) !== Object.prototype)
        fail('OBJECT_INVALID');
    const record = value;
    if (Object.keys(record).length !== keys.length || keys.some(key => !Object.hasOwn(record, key)))
        fail('KEYS_INVALID');
    return record;
}
function text(value) {
    if (typeof value !== 'string' || !value.length || value.length > 4096 || value.trim() !== value || value.includes('\0'))
        fail('TEXT_INVALID');
    return value;
}
function digest(value) { const result = text(value); if (!HASH.test(result))
    fail('HASH_INVALID'); return result; }
function list(value, parse, min = 0) {
    if (!Array.isArray(value) || value.length < min || value.length > 32)
        fail('LIST_INVALID');
    return Object.freeze(value.map(parse));
}
function strings(value, min = 0) { const result = list(value, text, min); unique(result); return result; }
function unique(values) { if (new Set(values).size !== values.length)
    fail('DUPLICATE_ID'); }
function inputs(value) {
    const result = list(value, item => { const v = object(item, ['id', 'version', 'sha256']); return Object.freeze({ id: text(v.id), version: text(v.version), sha256: digest(v.sha256) }); });
    unique(result.map(item => item.id));
    return result;
}
function bounded(value) {
    let encoded;
    try {
        encoded = JSON.stringify(value);
    }
    catch {
        fail('ENVELOPE_INVALID');
    }
    if (!encoded || Buffer.byteLength(encoded, 'utf8') > 64 * 1024)
        fail('ENVELOPE_TOO_LARGE');
}
function canonical(value) {
    if (Array.isArray(value))
        return `[${value.map(canonical).join(',')}]`;
    if (value !== null && typeof value === 'object')
        return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
    return JSON.stringify(value);
}
function hash(value) { return createHash('sha256').update(canonical(value)).digest('hex'); }
export function normalizeTaskContract(input) {
    bounded(input);
    const v = object(input, ['format', 'taskId', 'revision', 'outcome', 'nonGoals', 'inputs', 'outputs', 'acceptance', 'authorityLimits', 'stopConditions']);
    if (v.format !== TASK_CONTRACT_FORMAT || !Number.isSafeInteger(v.revision) || v.revision < 1)
        fail('IDENTITY_INVALID');
    const outputs = list(v.outputs, item => { const o = object(item, ['id', 'description']); return Object.freeze({ id: text(o.id), description: text(o.description) }); }, 1);
    unique(outputs.map(item => item.id));
    const acceptance = list(v.acceptance, item => {
        const c = object(item, ['id', 'requirement', 'evidenceRequired', 'outputIds']);
        const outputIds = strings(c.outputIds, 1);
        if (outputIds.some(id => !outputs.some(output => output.id === id)))
            fail('UNKNOWN_OUTPUT');
        return Object.freeze({ id: text(c.id), requirement: text(c.requirement), evidenceRequired: text(c.evidenceRequired), outputIds });
    }, 1);
    unique(acceptance.map(item => item.id));
    if (outputs.some(output => !acceptance.some(criterion => criterion.outputIds.includes(output.id))))
        fail('OUTPUT_WITHOUT_CRITERION');
    return Object.freeze({ format: TASK_CONTRACT_FORMAT, taskId: text(v.taskId), revision: v.revision, outcome: text(v.outcome), nonGoals: strings(v.nonGoals), inputs: inputs(v.inputs), outputs, acceptance, authorityLimits: strings(v.authorityLimits, 1), stopConditions: strings(v.stopConditions, 1) });
}
export function taskContractSha256(input) { return hash(normalizeTaskContract(input)); }
export function createTaskPacket(input, role) {
    if (role !== 'worker' && role !== 'reviewer')
        fail('ROLE_INVALID');
    const contract = normalizeTaskContract(input);
    return Object.freeze({ role, contract, contractSha256: hash(contract), instruction: role === 'worker'
            ? 'Follow this contract and its limits. Stop on stop conditions. Return a completion proposal with exact input versions, artifact hashes and evidence for every criterion. Tool success is not task completion.'
            : 'Independently verify every criterion against current artifacts and evidence using this same contract. Do not infer acceptance from worker assertions or tool success. Report extra requirements as contract ambiguity, not hidden rejection criteria.' });
}
export function normalizeCompletionProposal(input) {
    bounded(input);
    const v = object(input, ['format', 'taskId', 'contractSha256', 'attemptId', 'workerId', 'inputs', 'artifacts', 'evidence', 'claims', 'blockers']);
    if (v.format !== COMPLETION_PROPOSAL_FORMAT)
        fail('PROPOSAL_FORMAT_INVALID');
    const artifacts = list(v.artifacts, item => { const a = object(item, ['outputId', 'ref', 'sha256']); return Object.freeze({ outputId: text(a.outputId), ref: text(a.ref), sha256: digest(a.sha256) }); });
    const evidence = list(v.evidence, item => { const e = object(item, ['id', 'ref', 'sha256', 'outputIds']); return Object.freeze({ id: text(e.id), ref: text(e.ref), sha256: digest(e.sha256), outputIds: strings(e.outputIds, 1) }); });
    const claims = list(v.claims, item => { const c = object(item, ['criterionId', 'evidenceIds']); return Object.freeze({ criterionId: text(c.criterionId), evidenceIds: strings(c.evidenceIds, 1) }); });
    unique(artifacts.map(item => item.outputId));
    unique(evidence.map(item => item.id));
    unique(claims.map(item => item.criterionId));
    return Object.freeze({ format: COMPLETION_PROPOSAL_FORMAT, taskId: text(v.taskId), contractSha256: digest(v.contractSha256), attemptId: text(v.attemptId), workerId: text(v.workerId), inputs: inputs(v.inputs), artifacts, evidence, claims, blockers: strings(v.blockers) });
}
/** Host supplies the CURRENT contract/attempt and an independent verifier.
 * Result is evidence assessment only; the host owns authorization and commit. */
export async function reviewCompletion(input, proposalInput, options) {
    const contract = normalizeTaskContract(input), proposal = normalizeCompletionProposal(proposalInput);
    const contractSha256 = hash(contract), reasons = [];
    const attemptId = text(options.attemptId), workerId = text(options.workerId), reviewerId = text(options.reviewerId);
    if (typeof options.verify !== 'function')
        fail('VERIFIER_REQUIRED');
    if (reviewerId === workerId || reviewerId === proposal.workerId)
        reasons.push('SELF_REVIEW');
    if (proposal.taskId !== contract.taskId || proposal.contractSha256 !== contractSha256 || proposal.attemptId !== attemptId || proposal.workerId !== workerId)
        reasons.push('STALE_OR_FOREIGN_PROPOSAL');
    const sortedInputs = (value) => [...value].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
    if (canonical(sortedInputs(contract.inputs)) !== canonical(sortedInputs(proposal.inputs)))
        reasons.push('INPUT_VERSION_MISMATCH');
    if (contract.outputs.length !== proposal.artifacts.length || contract.outputs.some(output => !proposal.artifacts.some(artifact => artifact.outputId === output.id)))
        reasons.push('OUTPUT_SET_MISMATCH');
    if (contract.acceptance.length !== proposal.claims.length || contract.acceptance.some(criterion => !proposal.claims.some(claim => claim.criterionId === criterion.id)))
        reasons.push('CRITERION_SET_MISMATCH');
    if (proposal.evidence.some(e => e.outputIds.some(id => !contract.outputs.some(output => output.id === id))))
        reasons.push('UNKNOWN_EVIDENCE_OUTPUT');
    for (const criterion of contract.acceptance) {
        const claim = proposal.claims.find(c => c.criterionId === criterion.id);
        const evidence = proposal.evidence.filter(e => claim?.evidenceIds.includes(e.id));
        if (!claim || evidence.length !== claim.evidenceIds.length || criterion.outputIds.some(id => !evidence.some(e => e.outputIds.includes(id))))
            reasons.push(`MISSING_EVIDENCE:${criterion.id}`);
    }
    if (proposal.blockers.length)
        reasons.push('WORKER_BLOCKERS');
    const criteria = [];
    // No verifier invocation for a stale, incomplete, blocked or self-reviewed proposal.
    if (!reasons.length)
        for (const criterion of contract.acceptance) {
            const claim = proposal.claims.find(c => c.criterionId === criterion.id);
            let passed = false, reason = 'VERIFIER_ERROR';
            try {
                const checked = await options.verify(Object.freeze({ contract, criterion, artifacts: Object.freeze(proposal.artifacts.filter(a => criterion.outputIds.includes(a.outputId))), evidence: Object.freeze(proposal.evidence.filter(e => claim.evidenceIds.includes(e.id))) }));
                reason = text(checked.reason);
                passed = checked.passed === true;
            }
            catch { /* fail closed, do not expose verifier exceptions/secrets */ }
            criteria.push(Object.freeze({ criterionId: criterion.id, passed, reason }));
            if (!passed)
                reasons.push(`CRITERION_FAILED:${criterion.id}`);
        }
    return Object.freeze({ status: reasons.length ? (reasons.length === 1 && reasons[0] === 'WORKER_BLOCKERS' ? 'blocked' : 'rejected') : 'verified', contractSha256, proposalSha256: hash(proposal), attemptId, reviewerId, criteria: Object.freeze(criteria), reasons: Object.freeze(reasons) });
}
//# sourceMappingURL=task-contract.js.map