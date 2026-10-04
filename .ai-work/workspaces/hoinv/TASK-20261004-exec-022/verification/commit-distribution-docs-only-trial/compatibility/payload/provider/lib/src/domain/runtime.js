import { createHash } from 'node:crypto';
function encode(v, seen) { if (v === null)
    return 'null'; if (typeof v === 'string' || typeof v === 'boolean')
    return JSON.stringify(v); if (typeof v === 'number') {
    if (!Number.isFinite(v) || Object.is(v, -0))
        throw new TypeError('CANONICAL_UNSUPPORTED_NUMBER');
    return JSON.stringify(v);
} if (typeof v !== 'object')
    throw new TypeError('CANONICAL_UNSUPPORTED_VALUE'); if (seen.has(v))
    throw new TypeError('CANONICAL_CYCLE'); seen.add(v); try {
    if (Array.isArray(v)) {
        for (let i = 0; i < v.length; i++)
            if (!Object.hasOwn(v, i))
                throw new TypeError('CANONICAL_ARRAY_HOLE');
        if (Reflect.ownKeys(v).some(k => typeof k === 'symbol' || (k !== 'length' && !/^(0|[1-9]\d*)$/.test(k))))
            throw new TypeError('CANONICAL_ARRAY_EXTRA_PROPERTY');
        return `[${v.map(x => encode(x, seen)).join(',')}]`;
    }
    if (Object.getPrototypeOf(v) !== Object.prototype && Object.getPrototypeOf(v) !== null)
        throw new TypeError('CANONICAL_UNSUPPORTED_PROTOTYPE');
    if (Object.getOwnPropertySymbols(v).length)
        throw new TypeError('CANONICAL_SYMBOL_KEY');
    const o = v;
    return `{${Object.keys(o).sort().map(k => `${JSON.stringify(k)}:${encode(o[k], seen)}`).join(',')}}`;
}
finally {
    seen.delete(v);
} }
export function canonicalJson(v) { return encode(v, new WeakSet()); }
export function canonicalHash(v) { return createHash('sha256').update(canonicalJson(v)).digest('hex'); }
export function utf8Hash(v) { return createHash('sha256').update(v, 'utf8').digest('hex'); }
const hash = /^[a-f0-9]{64}$/;
const int = (n, min = 0) => Number.isSafeInteger(n) && n >= min;
function cloneFreeze(v) { if (v === null || typeof v !== 'object')
    return v; if (Array.isArray(v))
    return Object.freeze(v.map(cloneFreeze)); const out = Object.create(null); for (const [k, x] of Object.entries(v))
    Object.defineProperty(out, k, { value: cloneFreeze(x), enumerable: true, writable: false, configurable: false }); return Object.freeze(out); }
const runtimeKeys = { wake: ['generation', 'kind', 'missionId', 'projectId', 'triggerKey', 'wakeId'], run: ['generation', 'kind', 'missionId', 'projectId', 'runId', 'sessions', 'wakeId'], control: ['action', 'controlId', 'kind', 'missionId', 'projectId', 'revision', 'targetRunId', 'targetWakeId'], operation: ['effectKind', 'idempotencyKey', 'intent', 'intentHash', 'kind', 'missionId', 'operationId', 'ordinal', 'projectId', 'runId', 'wakeGeneration'], projection: ['aggregateRevision', 'kind', 'missionId', 'projectionId', 'projectId', 'runId', 'sourceRevision', 'wakeId'] };
export function runtimeRefs(scope, values) {
    if (!scope.projectId || values.some(x => x.missionId !== scope.missionId || x.projectId !== scope.projectId))
        throw new TypeError('FOREIGN_RUNTIME_REFERENCE');
    for (const x of values) {
        const allowed = runtimeKeys[x.kind], keys = Object.keys(x).sort();
        if (keys.some(k => !allowed.includes(k)) || allowed.filter(k => !['targetRunId', 'targetWakeId'].includes(k)).some(k => !keys.includes(k)))
            throw new TypeError('UNKNOWN_OR_MISSING_RUNTIME_FIELD');
        if (x.kind === 'run' && x.sessions.some(s => Object.keys(s).sort().join(',') !== 'model,ordinal,provider,sessionId'))
            throw new TypeError('UNKNOWN_SESSION_FIELD');
    }
    const ids = new Set(), wakes = new Map(), runs = new Map(), sessions = new Set();
    for (const x of values) {
        const id = x.kind === 'wake' ? x.wakeId : x.kind === 'run' ? x.runId : x.kind === 'control' ? x.controlId : x.kind === 'operation' ? x.operationId : x.projectionId;
        if (!id || ids.has(id))
            throw new TypeError('INVALID_OR_DUPLICATE_RUNTIME_ID');
        ids.add(id);
        if (x.kind === 'wake') {
            if (!int(x.generation, 1) || !x.triggerKey)
                throw new TypeError('INVALID_WAKE');
            wakes.set(x.wakeId, x);
        }
        if (x.kind === 'run') {
            const w = wakes.get(x.wakeId);
            if (!w || w.generation !== x.generation || !x.sessions.length || x.sessions.some((s, i) => !s.sessionId || sessions.has(s.sessionId) || !s.provider || !s.model || s.ordinal !== i))
                throw new TypeError('INVALID_RUN_WAKE_SESSION_LINK');
            x.sessions.forEach(s => sessions.add(s.sessionId));
            runs.set(x.runId, x);
        }
    }
    for (const x of values) {
        if (x.kind === 'control' && (!int(x.revision, 1) || Number(Boolean(x.targetWakeId)) + Number(Boolean(x.targetRunId)) !== 1 || (x.targetWakeId && !wakes.has(x.targetWakeId)) || (x.targetRunId && !runs.has(x.targetRunId))))
            throw new TypeError('INVALID_CONTROL_LINK');
        if (x.kind === 'operation') {
            const r = runs.get(x.runId), expected = idempotencyKey(x.missionId, x.runId, x.wakeGeneration, x.ordinal, x.effectKind, x.intent);
            if (!r || r.generation !== x.wakeGeneration || !int(x.ordinal) || x.intentHash !== canonicalHash(x.intent) || x.idempotencyKey !== expected || x.operationId !== expected || !hash.test(x.idempotencyKey))
                throw new TypeError('INVALID_OPERATION_LINK_OR_IDENTITY');
        }
        if (x.kind === 'projection' && (!int(x.aggregateRevision) || !int(x.sourceRevision) || x.sourceRevision > x.aggregateRevision || !x.wakeId || !x.runId || !wakes.has(x.wakeId) || !runs.has(x.runId) || runs.get(x.runId).wakeId !== x.wakeId))
            throw new TypeError('STALE_OR_FOREIGN_PROJECTION');
    }
    return Object.freeze(values.map(x => x.kind === 'run' ? Object.freeze({ ...x, sessions: Object.freeze(x.sessions.map(s => Object.freeze({ ...s }))) }) : x.kind === 'operation' ? Object.freeze({ ...x, intent: cloneFreeze(x.intent) }) : Object.freeze({ ...x })));
}
export function idempotencyKey(missionId, runId, wakeGeneration, ordinal, effectKind, intent) { if (!missionId || !runId || !int(wakeGeneration, 1) || !int(ordinal) || !effectKind)
    throw new TypeError('INVALID_IDEMPOTENCY_INPUT'); return canonicalHash({ missionId, runId, wakeGeneration, ordinal, effectKind, intent }); }
//# sourceMappingURL=runtime.js.map