export const PLANNING_MODES = ['NO_PLAN', 'CHECKLIST', 'WBS'];
const hash = /^[a-f0-9]{64}$/;
const statuses = ['PENDING', 'READY', 'RUNNING', 'DONE', 'BLOCKED'];
export function evaluatePlanning(f) { const axes = [f.workItems, f.dependencyDepth, f.affectedDomains, f.risk, f.uncertainty]; if (axes.some(x => !Number.isInteger(x) || x < 0 || x > 2) || ![f.itemCount, f.estimatedMinutes, f.modelCalls, f.workerCount].every(x => Number.isSafeInteger(x) && x >= 0))
    throw new TypeError('INVALID_PLANNING_FEATURES'); const score = axes.reduce((a, b) => a + b, 0), forced = [f.itemCount > 8 && 'items>8', f.dependencyDepth > 1 && 'dependency-depth>1', f.crossProject && 'cross-project', f.affectedDomains > 1 && 'cross-domain', f.externalOrIrreversible && 'external-or-irreversible', f.protectedData && 'protected-data', f.securityPrivacyMigrationRelease && 'security-privacy-migration-release', f.estimatedMinutes > 240 && 'minutes>240', f.modelCalls > 12 && 'model-calls>12', f.workerCount > 1 && 'workers>1', f.independentOrHumanGate && 'required-gate'].filter((x) => Boolean(x)); let mode = 'CHECKLIST'; if (forced.length || score >= 7)
    mode = 'WBS';
else if (score <= 2 && f.itemCount === 1 && f.dependencyDepth === 0 && !f.externalOrIrreversible && !f.protectedData && f.estimatedMinutes <= 30 && f.modelCalls <= 2)
    mode = 'NO_PLAN'; return { score, forcedWbsReasons: forced, mode }; }
export function planningDecision(v, e) { const wakes = Number(Boolean(v.claimedWakeId)) + Number(Boolean(v.emittedWakeId)), model = evaluatePlanning(v.features); if (v.missionId !== e.missionId || v.policyVersion !== 'planning-policy-v1' || v.thresholds.noPlanMax !== 2 || v.thresholds.checklistMax !== 6 || v.score !== model.score || v.mode !== model.mode || JSON.stringify(v.forcedWbsReasons) !== JSON.stringify(model.forcedWbsReasons) || v.priorRevision !== e.currentRevision || v.revision !== v.priorRevision + 1 || !v.reason.trim() || !v.nextAction.trim() || !v.decidedBy || !Number.isSafeInteger(v.decidedAt) || v.decidedAt < 0 || !hash.test(v.decisionHash) || wakes !== 1)
    throw new TypeError('INVALID_PLANNING_POLICY_AUDIT_OR_READY_LIVENESS'); return Object.freeze({ ...v, features: Object.freeze({ ...v.features }), thresholds: Object.freeze({ ...v.thresholds }), forcedWbsReasons: Object.freeze([...v.forcedWbsReasons]) }); }
export function workItems(v, e) { const ids = new Set(v.map(x => x.id)); if (!v.length || ids.size !== v.length)
    throw new TypeError('DUPLICATE_OR_EMPTY_WORK_ITEMS'); for (const x of v)
    if (!x.id || x.missionId !== e.missionId || x.planId !== e.planId || !statuses.includes(x.status) || !Number.isSafeInteger(x.attempt) || !Number.isSafeInteger(x.maxAttempts) || x.attempt < 0 || x.maxAttempts < 1 || x.attempt > x.maxAttempts || new Set(x.dependencies).size !== x.dependencies.length || x.dependencies.includes(x.id) || x.dependencies.some(d => !ids.has(d)))
        throw new TypeError('INVALID_WORK_ITEM_PROVENANCE'); const visiting = new Set(), visited = new Set(), byId = new Map(v.map(x => [x.id, x])); const visit = (id) => { if (visiting.has(id))
    throw new TypeError('WORK_ITEM_CYCLE'); if (visited.has(id))
    return; visiting.add(id); for (const d of byId.get(id).dependencies)
    visit(d); visiting.delete(id); visited.add(id); }; for (const id of ids)
    visit(id); return Object.freeze(v.map(x => Object.freeze({ ...x, dependencies: Object.freeze([...x.dependencies]) }))); }
//# sourceMappingURL=planning.js.map