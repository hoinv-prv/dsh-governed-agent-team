export const BUDGET_DIMENSIONS = ['searches', 'sources', 'toolCalls', 'inputTokens', 'outputTokens', 'costUsd'];
const hash = /^[a-f0-9]{64}$/, empty = () => ({ searches: 0, sources: 0, toolCalls: 0, inputTokens: 0, outputTokens: 0, costUsd: 0 });
export function budget(v, limit) { for (const k of BUDGET_DIMENSIONS) {
    const n = v[k];
    if (!Number.isFinite(n) || n < 0 || (k !== 'costUsd' && !Number.isSafeInteger(n)) || (limit && n > limit[k]))
        throw new TypeError(`BUDGET_${k}_OUT_OF_RANGE`);
} return Object.freeze({ ...v }); }
export function budgetAccount(v, limit, prior) { const reserved = budget(v.reserved, limit), consumed = budget(v.consumed, reserved); if (prior && BUDGET_DIMENSIONS.some(k => reserved[k] < prior.reserved[k] || consumed[k] < prior.consumed[k]))
    throw new TypeError('BUDGET_NOT_MONOTONIC'); return Object.freeze({ reserved, consumed }); }
export function budgetLedger(entries, e) { const ids = new Set(), events = new Set(), reserved = empty(), consumed = empty(), returned = empty(); let seq = 0; for (const x of entries) {
    if (!x.entryId || ids.has(x.entryId) || !x.eventId || events.has(x.eventId) || x.missionId !== e.missionId || x.sequence !== ++seq || (x.runId === undefined) !== (x.generation === undefined) || (x.generation !== undefined && (!Number.isSafeInteger(x.generation) || x.generation < 1)) || !BUDGET_DIMENSIONS.includes(x.category) || [x.reservedDelta, x.consumedDelta, x.returnedDelta].some(n => !Number.isFinite(n) || n < 0) || (x.category !== 'costUsd' && [x.reservedDelta, x.consumedDelta, x.returnedDelta].some(n => !Number.isSafeInteger(n))))
        throw new TypeError('INVALID_BUDGET_LEDGER_HISTORY');
    ids.add(x.entryId);
    events.add(x.eventId);
    reserved[x.category] += x.reservedDelta;
    consumed[x.category] += x.consumedDelta;
    returned[x.category] += x.returnedDelta;
    if (consumed[x.category] + returned[x.category] > reserved[x.category] || reserved[x.category] > e.ceiling[x.category])
        throw new TypeError('BUDGET_LEDGER_OVERDRAW_OR_RESET');
} const active = empty(); for (const k of BUDGET_DIMENSIONS)
    active[k] = reserved[k] - consumed[k] - returned[k]; return Object.freeze({ reserved: budget(reserved), consumed: budget(consumed), returned: budget(returned), activeReserved: budget(active) }); }
const subset = (a, b, allowEmpty = false) => ((allowEmpty && a.length === 0) || a.length > 0) && new Set(a).size === a.length && a.every(x => x && b.includes(x));
export function delegationGrant(v, c, now) { const positive = [v.contractRevision, v.controlRevision, v.revision, v.inputTokenCeiling, v.outputTokenCeiling, v.contextCeiling, v.toolCallCeiling, v.timeCeilingMs, v.costCeilingUsd].every(x => Number.isFinite(x) && x > 0); if (!v.grantId || !positive || v.contractRevision !== c.contractRevision || v.controlRevision !== c.controlRevision || v.issuer !== c.issuer || v.issuer === v.subject || v.missionId !== c.missionId || v.projectId !== c.projectId || v.templateHash !== c.templateHash || !hash.test(v.templateHash) || !hash.test(v.contributionSetHash) || ![v.role, v.templateVersion, v.capability, v.purpose, v.provider, v.model].every(x => x.trim()) || !c.providers.includes(v.provider) || !c.models.includes(v.model) || v.inputTokenCeiling > c.inputTokenCeiling || v.outputTokenCeiling > c.outputTokenCeiling || v.contextCeiling > c.contextCeiling || v.toolCallCeiling > c.toolCallCeiling || v.timeCeilingMs > c.timeCeilingMs || v.costCeilingUsd > c.costCeilingUsd || v.revocationRevision < c.priorRevocationRevision || v.issuedAt > now || v.expiresAt <= now || v.expiresAt - v.issuedAt > 86_400_000 || (v.revokedAt !== undefined && v.revocationRevision <= c.priorRevocationRevision) || !subset(v.readScopes, c.readScopes) || !subset(v.writeScopes, c.writeScopes, true) || !subset(v.effects, c.effects) || !subset(v.commands, c.commands, true))
    throw new TypeError('GRANT_SCOPE_ELEVATION_OR_INVALID'); return Object.freeze({ ...v, readScopes: Object.freeze([...v.readScopes]), writeScopes: Object.freeze([...v.writeScopes]), effects: Object.freeze([...v.effects]), commands: Object.freeze([...v.commands]), budget: budget(v.budget, c.budget) }); }
export function aiwsAuthorization(v, e) { const patterns = v.allowedPatterns.length > 0 && v.allowedPatterns.every(p => e.scopePatterns.includes(p)); if (v.missionId !== e.missionId || v.projectId !== e.projectId || v.order.join(',') !== 'rules,wiki,project,memory' || !e.systemSelectors.includes(v.systemSelector) || ((v.rawAllowed || v.localAllowed) && (!v.authorityRef || !patterns)) || (!v.rawAllowed && !v.localAllowed && v.allowedPatterns.length) || v.issuedAt > e.now || v.expiresAt <= e.now || v.expiresAt - v.issuedAt > 3_600_000)
    throw new TypeError('AIWS_AUTHORIZATION_DENIED'); return Object.freeze({ ...v, order: Object.freeze([...v.order]), allowedPatterns: Object.freeze([...v.allowedPatterns]) }); }
//# sourceMappingURL=authority.js.map