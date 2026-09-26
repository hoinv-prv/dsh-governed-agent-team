import { createHash, createHmac } from 'node:crypto';

const MAX_LIMIT = 50;
const text = (name, value) => { if (typeof value !== 'string' || value.length === 0) throw new TypeError(`${name} required`); return value; };
const integer = (name, value) => { if (!Number.isSafeInteger(value) || value < 0) throw new TypeError(`${name} invalid`); return value; };
const clone = (value) => structuredClone(value);
const deepFreeze = (value) => { if (value && typeof value === 'object') { for (const item of Object.values(value)) deepFreeze(item); Object.freeze(value); } return value; };
const owned = (value) => deepFreeze(clone(value));
function canonical(value) {
  if (value === null || ['string', 'boolean'].includes(typeof value)) return JSON.stringify(value);
  if (typeof value === 'number' && Number.isFinite(value)) return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && Object.getPrototypeOf(value) === Object.prototype) return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  throw new TypeError('JSON value required');
}
const digest = (domain, value) => `sha256:${createHash('sha256').update(`${domain}\0${canonical(value)}`).digest('hex')}`;
const SHA = /^sha256:[a-f0-9]{64}$/u;
const auditDigest = (priorDigest, eventBytes) => {
  const state = createHash('sha256').update('GAT-AUDIT-V1\0');
  state.update(priorDigest === null ? Buffer.alloc(32) : Buffer.from(priorDigest.slice(7), 'hex'));
  return `sha256:${state.update('\0').update(canonical(eventBytes)).digest('hex')}`;
};
const nonemptyObject = (name, value) => { if (!value || Object.getPrototypeOf(value) !== Object.prototype || Object.keys(value).length === 0) throw new Error('BINDING_INVALID'); return value; };
const sha = (name, value) => { if (!SHA.test(value)) throw new Error('BINDING_INVALID'); return value; };
const normalize = (value) => value.normalize('NFKC').toLocaleLowerCase('und');
const REFERENCE_START = '<GAT_REFERENCE trust="untrusted">';
const REFERENCE_END = '</GAT_REFERENCE>';
const PROHIBITED = /\b(password|api[_-]?key|secret|token)\s*[:=]\s*\S+|\b\d{3}-\d{2}-\d{4}\b|\b(?:\d[ -]*?){13,16}\b/iu;
const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/giu;
function sanitizeRecordStrings(value, state) {
  if (typeof value === 'string') { if (PROHIBITED.test(value)) { const error = new Error('ACTION_NOT_ALLOWED'); error.reasonCode = 'ACTION_NOT_ALLOWED'; throw error; } const redacted = value.replace(EMAIL, '[REDACTED:EMAIL]'); if (redacted !== value) state.redacted = true; return redacted; }
  if (Array.isArray(value)) return value.map((item) => sanitizeRecordStrings(item, state));
  if (value && Object.getPrototypeOf(value) === Object.prototype) return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, sanitizeRecordStrings(item, state)]));
  return value;
}

export function physicalPartitionKey({ tenantId, principalId, projectScopeId, scopeKind, scopeOwnerKey }) {
  return [tenantId, principalId, projectScopeId, scopeKind, scopeOwnerKey].map((part, i) => encodeURIComponent(text(`partition[${i}]`, part))).join('/');
}

export class Crash extends Error { constructor(boundary) { super(`CRASH:${boundary}`); this.boundary = boundary; } }

export class AnchorRegistry {
  #heads = new Map();
  head(auditPartition) { return this.#heads.get(auditPartition)?.hash ?? null; }
  highWater(auditPartition) { return owned(this.#heads.get(auditPartition) ?? { sequence: -1, hash: null }); }
  compareAndSet(auditPartition, expectedHash, nextHash, nextSequence) { const current = this.highWater(auditPartition); if (current.hash !== expectedHash || nextSequence !== current.sequence + 1) throw new Error('ANCHOR_CAS_CONFLICT'); this.#heads.set(auditPartition, { sequence: nextSequence, hash: nextHash }); }
  snapshot() { return owned([...this.#heads]); }
}

export class TransactionalAuditSink {
  #prepared = new Map(); #committed = new Map(); #effects = new Map();
  prepare(operationId, event) { const existing = this.#prepared.get(operationId) ?? this.#committed.get(operationId); if (existing && existing.eventHash !== event.eventHash) throw new Error('AUDIT_PREPARE_CONFLICT'); if (!existing) this.#prepared.set(operationId, owned(event)); }
  recordEffect(operationId, effect) { const prior = this.#effects.get(operationId); const next = owned(effect); if (prior && digest('GAT-DOMAIN-EFFECT-V1', prior) !== digest('GAT-DOMAIN-EFFECT-V1', next)) throw new Error('DOMAIN_EFFECT_CONFLICT'); this.#effects.set(operationId, next); }
  commit(operationId) { if (this.#committed.has(operationId)) return; const event = this.#prepared.get(operationId); if (!event) throw new Error('AUDIT_PREPARE_MISSING'); this.#committed.set(operationId, event); this.#prepared.delete(operationId); }
  abort(operationId) { if (!this.#committed.has(operationId)) { this.#prepared.delete(operationId); this.#effects.delete(operationId); } }
  committed() { return owned([...this.#committed.values()]); }
  effect(operationId) { return owned(this.#effects.get(operationId) ?? null); }
}

export class LifecycleRegistry {
  #purges = new Map(); #fences = new Set();
  acquire(recordKey, token) { text('fenceToken', token); if (this.#fences.has(recordKey)) throw new Error('PURGE_FENCE_CONFLICT'); this.#fences.add(recordKey); return () => this.#fences.delete(recordKey); }
  publish(manifest) { const prior = this.#purges.get(manifest.recordKey); if (prior && prior.manifestHash !== manifest.manifestHash) throw new Error('PURGE_MANIFEST_CONFLICT'); this.#purges.set(manifest.recordKey, owned(manifest)); }
  manifest(recordKey) { return this.#purges.get(recordKey) ?? null; }
  inventory() { return owned([...this.#purges]); }
}

export class PartitionStore {
  #records = new Map(); #audit = new Map(); #journal = new Map(); #published = new Set(); #idempotency = new Map(); #holds = new Map();
  #clock; #sink; #emergency; #operatorAlert; #backendProbe; #anchors; #lifecycle; #epoch; #genesis; #genesisSigningKey; #restoreEvidence = [];
  constructor({ clock = () => Date.now(), auditSink = new TransactionalAuditSink(), emergencySink = { append() {} }, operatorAlert = { append() {} }, backendProbe = () => {}, anchors = new AnchorRegistry(), lifecycle = new LifecycleRegistry(), epoch = 'epoch-1', genesis = { policyRevision: 1, previousEpochHead: null, creationAuthority: { principalId: 'system' }, signatureKeyId: 'local-test-key' }, genesisSigningKey = 'local-test-secret' } = {}) {
    nonemptyObject('genesis.creationAuthority', genesis.creationAuthority); integer('genesis.policyRevision', genesis.policyRevision); text('genesis.signatureKeyId', genesis.signatureKeyId); if (genesis.previousEpochHead !== null) sha('genesis.previousEpochHead', genesis.previousEpochHead);
    this.#clock = clock; this.#sink = auditSink; this.#emergency = emergencySink; this.#operatorAlert = operatorAlert; this.#backendProbe = backendProbe; this.#anchors = anchors; this.#lifecycle = lifecycle; this.#epoch = text('epoch', epoch); this.#genesis = owned(genesis); this.#genesisSigningKey = text('genesisSigningKey', genesisSigningKey);
  }
  #recordKey(context, recordId) { return `${physicalPartitionKey(context)}::${encodeURIComponent(text('recordId', recordId))}`; }
  #partitionEpoch(context) { return `${encodeURIComponent(context.tenantId)}#${encodeURIComponent(this.#epoch)}`; }
  #ensureChain(context) {
    const pe = this.#partitionEpoch(context);
    if (!this.#audit.has(pe)) {
      const unsigned = { schema: 'gat.audit.v1', tenantId: context.tenantId, epoch: this.#epoch, sequence: 0, operation: 'GENESIS', decision: 'system', reasonCode: null, resourceId: null, actorId: 'system', runId: 'system', bindingHash: digest('GAT-GENESIS-BINDING-V1', { tenantId: context.tenantId, epoch: this.#epoch }), metadataHash: digest('GAT-METADATA-V1', {}), policyRevision: this.#genesis.policyRevision, previousEpochHead: this.#genesis.previousEpochHead, creationAuthority: this.#genesis.creationAuthority, signatureKeyId: this.#genesis.signatureKeyId };
      const signature = `sha256:${createHmac('sha256', this.#genesisSigningKey).update(canonical(unsigned)).digest('hex')}`; const core = { ...unsigned, signature };
      const genesis = owned({ ...core, priorDigest: null, eventHash: auditDigest(null, core), operationId: 'GENESIS' });
      this.#anchors.compareAndSet(pe, null, genesis.eventHash, 0);
      this.#audit.set(pe, [genesis]);
    }
    return pe;
  }
  #event(context, request) {
    const pe = this.#ensureChain(context); const chain = this.#audit.get(pe); const previous = chain.at(-1);
    const evidence = request.decisionEvidence; nonemptyObject('decisionEvidence', evidence); for (const key of ['readinessHash', 'nativeApprovalHash', 'teamPlanHash', 'selectorHash', 'capabilityHash', 'policyHash', 'membershipHash']) sha(`decisionEvidence.${key}`, evidence[key]); text('decisionId', evidence.decisionId); text('correlationId', evidence.correlationId); integer('decidedAt', evidence.decidedAt); if (evidence.outcome !== request.decision) throw new Error('BINDING_INVALID'); const authoritative = nonemptyObject('authoritative', evidence.authoritative); for (const key of ['taskId', 'aipId', 'workspaceId', 'teamId', 'missionId']) text(`authoritative.${key}`, authoritative[key]); for (const key of ['taskRevision', 'aipRevision', 'teamRevision', 'missionRevision']) integer(`authoritative.${key}`, authoritative[key]); if (!Array.isArray(evidence.matchedRules) || evidence.matchedRules.length === 0) throw new Error('BINDING_INVALID'); for (const rule of evidence.matchedRules) text('matchedRule', rule);
    const core = { schema: 'gat.audit.v1', tenantId: context.tenantId, principalId: context.principalId, projectScopeId: context.projectScopeId, scopeKind: context.scopeKind, scopeOwnerKey: context.scopeOwnerKey, epoch: this.#epoch, sequence: previous.sequence + 1, operation: request.operation, decision: request.decision, reasonCode: request.reasonCode ?? null, resourceId: request.resourceId ?? null, actorId: text('actorId', request.actorId), runId: text('runId', request.runId), bindingHash: sha('bindingHash', request.bindingHash), decisionEvidence: owned(evidence), metadataHash: digest('GAT-METADATA-V1', request.redactedMetadata ?? {}) };
    return owned({ ...core, priorDigest: previous.eventHash, eventHash: auditDigest(previous.eventHash, core), operationId: request.operationId });
  }
  #snapshotLocal() { return { records: clone([...this.#records]), audit: clone([...this.#audit]), holds: clone([...this.#holds]) }; }
  #restoreLocal(snapshot) { this.#records = new Map(snapshot.records); this.#audit = new Map(snapshot.audit); this.#holds = new Map(snapshot.holds); }
  #alert(code, operationId) { try { this.#operatorAlert.append(owned({ code, operationId, occurredAt: this.#clock() })); } catch { /* alert failure is represented by the primary error */ } }
  #assertNoPending() { if ([...this.#journal.values()].some((entry) => !['idempotent', 'aborted'].includes(entry.state))) throw new Error('RECOVERY_REQUIRED'); }
  #transact({ context, operationId, operation, decision = 'allow', reasonCode = null, resourceId = null, actorId, runId, bindingHash, decisionEvidence, redactedMetadata = {}, request, apply = () => undefined, crashAt = null }) {
    this.#assertNoPending(); text('operationId', operationId);
    const requestHash = digest('GAT-REQUEST-V1', request); const replay = this.#idempotency.get(operationId);
    if (replay) { if (replay.requestHash !== requestHash) throw new Error('IDEMPOTENCY_CONFLICT'); return replay.result; }
    const event = this.#event(context, { operationId, operation, decision, reasonCode, resourceId, actorId, runId, bindingHash, decisionEvidence, redactedMetadata }); const before = this.#snapshotLocal();
    const entry = { operationId, state: 'journaled', requestHash, event, before, result: null, partitionEpoch: this.#partitionEpoch(context) }; this.#journal.set(operationId, entry);
    if (crashAt === 'journaled') throw new Crash('journaled');
    try { this.#sink.prepare(operationId, event); } catch { entry.state = 'aborted'; this.#alert('PRIMARY_AUDIT_UNAVAILABLE', operationId); throw new Error(operation === 'get' || operation === 'search' || operation === 'audit.read' ? 'SECURITY_SERVICE_UNAVAILABLE' : 'AUDIT_APPEND_FAILED'); }
    if (crashAt === 'sink_prepared_before_state') throw new Crash('sink_prepared_before_state'); entry.state = 'sink_prepared';
    if (crashAt === 'sink_prepared') throw new Crash('sink_prepared');
    try { entry.state = 'applying'; entry.result = owned(apply(event)); this.#sink.recordEffect?.(operationId, { operation, context, resourceId, requestHash, result: entry.result }); this.#audit.get(entry.partitionEpoch).push(event); if (crashAt === 'local_effect_before_state') throw new Crash('local_effect_before_state'); entry.state = 'local_committed'; } catch (error) { if (error instanceof Crash) throw error; this.#restoreLocal(before); this.#sink.abort(operationId); entry.state = 'aborted'; throw error; }
    if (crashAt === 'local_committed') throw new Crash('local_committed');
    this.#anchors.compareAndSet(entry.partitionEpoch, event.priorDigest, event.eventHash, event.sequence); if (crashAt === 'anchor_cas_before_state') throw new Crash('anchor_cas_before_state'); entry.state = 'anchored';
    if (crashAt === 'anchored') throw new Crash('anchored');
    this.#sink.commit(operationId); if (crashAt === 'sink_commit_before_state') throw new Crash('sink_commit_before_state'); entry.state = 'sink_committed';
    if (crashAt === 'sink_committed') throw new Crash('sink_committed');
    if (operation === 'record.purge') this.#lifecycle.publish(entry.result); if (crashAt === 'manifest_publish_before_state') throw new Crash('manifest_publish_before_state'); entry.state = 'manifest_published';
    if (crashAt === 'manifest_published') throw new Crash('manifest_published');
    this.#published.add(operationId); if (crashAt === 'published_set_before_state') throw new Crash('published_set_before_state'); entry.state = 'published';
    if (crashAt === 'published') throw new Crash('published');
    this.#idempotency.set(operationId, { requestHash, result: entry.result }); if (crashAt === 'idempotency_set_before_state') throw new Crash('idempotency_set_before_state'); entry.state = 'idempotent';
    if (crashAt === 'idempotent') throw new Crash('idempotent');
    return entry.result;
  }
  recover() {
    for (const entry of this.#journal.values()) {
      if (['journaled', 'sink_prepared', 'applying'].includes(entry.state)) { this.#restoreLocal(entry.before); this.#sink.abort(entry.operationId); entry.state = 'aborted'; continue; }
      if (entry.state === 'local_committed') { const high = this.#anchors.highWater(entry.partitionEpoch); if (high.hash === entry.event.eventHash && high.sequence === entry.event.sequence) entry.state = 'anchored'; else { this.#restoreLocal(entry.before); this.#sink.abort(entry.operationId); entry.state = 'aborted'; continue; } }
      if (entry.state === 'anchored') { this.#sink.commit(entry.operationId); entry.state = 'sink_committed'; }
      if (entry.state === 'sink_committed') { if (entry.event.operation === 'record.purge') this.#lifecycle.publish(entry.result); entry.state = 'manifest_published'; }
      if (entry.state === 'manifest_published') { this.#published.add(entry.operationId); entry.state = 'published'; }
      if (entry.state === 'published') { this.#idempotency.set(entry.operationId, { requestHash: entry.requestHash, result: entry.result }); entry.state = 'idempotent'; }
    }
  }
  #validateRecord(context, input, revision, createdAt, prior = null) {
    const sanitization = { redacted: false }; input = sanitizeRecordStrings(clone(input), sanitization);
    const authority = nonemptyObject('authority', input.authority); const owner = nonemptyObject('owner', input.owner); const agent = nonemptyObject('agent', input.agent); const origin = nonemptyObject('origin', input.origin); const classification = nonemptyObject('classification', input.classification); const actor = nonemptyObject('actor', input.actor); const run = nonemptyObject('run', input.run); const binding = nonemptyObject('binding', input.binding); const retention = nonemptyObject('retention', input.retention);
    for (const [object, key] of [[authority, 'id'], [owner, 'id'], [agent, 'id'], [origin, 'type'], [actor, 'id'], [run, 'id']]) text(key, object[key]); if (authority.mode !== 'reference_only') throw new Error('BINDING_INVALID'); sha('binding.hash', binding.hash); text('record.kind', input.kind);
    if (!['public', 'internal', 'restricted'].includes(classification.label)) throw new Error('BINDING_INVALID'); sha('classification.policyHash', classification.policyHash); integer('classification.redactionRevision', classification.redactionRevision);
    integer('origin.capturedAt', origin.capturedAt); if (origin.type !== 'direct_note') { text('origin.systemId', origin.systemId); text('origin.eventId', origin.eventId); }
    text('retention.policyId', retention.policyId); integer('retention.policyRevision', retention.policyRevision); text('retention.mode', retention.mode); integer('retention.retainUntil', retention.retainUntil); integer('retention.expiresAt', retention.expiresAt); if (retention.expiresAt < retention.retainUntil) throw new Error('BINDING_INVALID'); sha('retention.policyHash', retention.policyHash);
    if (!Array.isArray(input.sourceRefs) || (origin.type === 'direct_note' ? input.sourceRefs.length !== 0 : input.sourceRefs.length === 0)) throw new Error('BINDING_INVALID'); for (const ref of input.sourceRefs) { nonemptyObject('sourceRef', ref); text('sourceRef.id', ref.id); integer('sourceRef.revision', ref.revision); sha('sourceRef.evidenceHash', ref.evidenceHash); }
    const now = this.#clock(); const status = input.status ?? 'active'; if (!['active', 'tombstoned'].includes(status)) throw new Error('BINDING_INVALID'); if (status === 'tombstoned') { text('tombstoneReason', input.tombstoneReason); integer('tombstonedAt', input.tombstonedAt); }
    let rawContent = String(input.content ?? ''); if (rawContent.startsWith(`${REFERENCE_START}\n`) && rawContent.endsWith(`\n${REFERENCE_END}`)) rawContent = rawContent.slice(REFERENCE_START.length + 1, -(REFERENCE_END.length + 1)); const content = status === 'tombstoned' ? '' : `${REFERENCE_START}\n${rawContent}\n${REFERENCE_END}`; const appliedClassification = { ...classification, redactionApplied: sanitization.redacted || prior?.classification?.redactionApplied === true };
    const core = { recordId: text('recordId', input.recordId), revision, authority: clone(authority), owner: clone(owner), scope: { kind: context.scopeKind, ownerKey: context.scopeOwnerKey, tenantId: context.tenantId, principalId: context.principalId, projectScopeId: context.projectScopeId }, agent: clone(agent), kind: input.kind, origin: clone(origin), sourceRefs: clone(input.sourceRefs), classification: owned(appliedClassification), status, retention: clone(retention), actor: clone(actor), run: clone(run), binding: clone(binding), title: input.title ?? '', content, contentTrust: 'untrusted_reference', contentDelimiter: { start: REFERENCE_START, end: REFERENCE_END }, tags: clone(input.tags ?? []), createdAt, updatedAt: now, tombstonedAt: input.tombstonedAt ?? null, tombstoneReason: input.tombstoneReason ?? null, priorRevisionHash: prior?.evidenceHash ?? null, contentHash: digest('GAT-RECORD-CONTENT-V1', { title: input.title ?? '', content, tags: input.tags ?? [] }), transactionId: null };
    return owned({ ...core, evidenceHash: digest('GAT-RECORD-EVIDENCE-V1', core) });
  }
  create({ context, record, operationId, actorId, runId, bindingHash, decisionEvidence, crashAt }) {
    const request = { context, record }; const prior = this.#idempotency.get(operationId);
    if (prior) { if (prior.requestHash !== digest('GAT-REQUEST-V1', request)) throw new Error('IDEMPOTENCY_CONFLICT'); return prior.result; }
    let next; try { next = this.#validateRecord(context, record, 1, this.#clock()); } catch (error) { const reasonCode = error?.message === 'ACTION_NOT_ALLOWED' ? 'ACTION_NOT_ALLOWED' : 'BINDING_INVALID'; this.recordDenied({ context, operationId, operation: 'record.create', reasonCode, actorId, runId, bindingHash, decisionEvidence }); throw new Error(reasonCode); }
    const key = this.#recordKey(context, next.recordId); if (this.#records.has(key)) throw new Error('RECORD_EXISTS');
    return this.#transact({ context, operationId, operation: 'record.create', resourceId: record.recordId, actorId, runId, bindingHash, decisionEvidence, request, crashAt, apply: (event) => { const saved = owned({ ...next, transactionId: operationId, auditHash: event.eventHash }); this.#records.set(key, [saved]); return saved; } });
  }
  revise({ context, recordId, expectedRevision, patch, operationId, actorId, runId, bindingHash, decisionEvidence, crashAt, _request = null }) {
    const request = _request ?? { context, recordId, expectedRevision, patch }; const prior = this.#idempotency.get(operationId); if (prior) { if (prior.requestHash !== digest('GAT-REQUEST-V1', request)) throw new Error('IDEMPOTENCY_CONFLICT'); return prior.result; } const key = this.#recordKey(context, recordId); const current = this.#records.get(key)?.at(-1); if (!current || current.revision !== expectedRevision) throw new Error('REVISION_CONFLICT');
    const merged = { ...current, ...clone(patch), recordId }; let next; try { next = this.#validateRecord(context, merged, expectedRevision + 1, current.createdAt, current); } catch (error) { const reasonCode = error?.message === 'ACTION_NOT_ALLOWED' ? 'ACTION_NOT_ALLOWED' : 'BINDING_INVALID'; this.recordDenied({ context, operationId, operation: 'record.revise', reasonCode, actorId, runId, bindingHash, decisionEvidence }); throw new Error(reasonCode); }
    return this.#transact({ context, operationId, operation: 'record.revise', resourceId: recordId, actorId, runId, bindingHash, decisionEvidence, request, crashAt, apply: (event) => { const saved = owned({ ...next, transactionId: operationId, auditHash: event.eventHash }); this.#records.set(key, [...this.#records.get(key), saved]); return saved; } });
  }
  tombstone(args) { const reason = text('tombstoneReason', args.tombstoneReason); const stableRequest = { context: args.context, recordId: args.recordId, expectedRevision: args.expectedRevision, patch: args.patch ?? {}, tombstoneReason: reason }; return this.revise({ ...args, _request: stableRequest, patch: { ...(args.patch ?? {}), status: 'tombstoned', tombstonedAt: this.#clock(), tombstoneReason: reason, content: '', title: '', tags: [] } }); }
  #eligible(record, now) { return record.status === 'active' && now < record.retention.expiresAt; }
  get({ context, recordId, operationId, actorId, runId, bindingHash, decisionEvidence, now = this.#clock() }) {
    return this.#transact({ context, operationId, operation: 'get', resourceId: recordId, actorId, runId, bindingHash, decisionEvidence, request: { context, recordId, now }, apply: () => { this.#backendProbe('get'); const current = this.#records.get(this.#recordKey(context, recordId))?.at(-1); return current && this.#eligible(current, now) ? owned({ record: current, eligibility: { state: 'returnable', evaluatedAt: now }, citations: current.sourceRefs }) : owned({ record: null, eligibility: { state: current?.status === 'active' ? 'expired' : 'not_returnable', evaluatedAt: now }, citations: [] }); } });
  }
  search({ context, query, operationId, actorId, runId, bindingHash, decisionEvidence, limit = 20, now = this.#clock() }) {
    text('query', query); if (!Number.isSafeInteger(limit) || limit < 1 || limit > MAX_LIMIT) throw new Error('LIMIT_INVALID');
    const select = () => { this.#backendProbe('search'); const needle = normalize(query); const prefix = `${physicalPartitionKey(context)}::`; return owned([...this.#records.entries()].filter(([key]) => key.startsWith(prefix)).map(([, versions]) => versions.at(-1)).filter((record) => this.#eligible(record, now)).map((record) => { const fields = [record.title, record.content, ...record.tags]; const exact = fields.some((field) => normalize(String(field)) === needle); const substring = fields.some((field) => normalize(String(field)).includes(needle)); return { record, exact, substring }; }).filter((hit) => hit.substring).sort((a, b) => Number(b.exact) - Number(a.exact) || b.record.updatedAt - a.record.updatedAt || a.record.recordId.localeCompare(b.record.recordId)).slice(0, limit).map(({ record, exact }) => ({ record, match: exact ? 'exact' : 'substring', citations: record.sourceRefs }))); };
    return this.#transact({ context, operationId, operation: 'search', actorId, runId, bindingHash, decisionEvidence, request: { context, query, limit, now }, apply: select });
  }
  history({ context, recordId }) { const pending = [...this.#journal.values()].find((entry) => !['idempotent', 'aborted'].includes(entry.state)); const records = pending ? new Map(pending.before.records) : this.#records; return owned((records.get(this.#recordKey(context, recordId)) ?? []).filter((record) => this.#published.has(record.transactionId))); }
  auditRead({ context, authority, operationId, actorId, runId, bindingHash, decisionEvidence }) {
    if (!authority || authority.tenantId !== context.tenantId || authority.principalId !== context.principalId || authority.projectScopeId !== context.projectScopeId || authority.scopeKind !== context.scopeKind || authority.scopeOwnerKey !== context.scopeOwnerKey || authority.capability !== 'audit.read') { this.recordDenied({ context, operationId, operation: 'audit.read', reasonCode: 'RESOURCE_SCOPE_MISMATCH', actorId, runId, bindingHash, decisionEvidence }); throw new Error('RESOURCE_SCOPE_MISMATCH'); }
    const pe = this.#ensureChain(context); const result = () => owned(this.#audit.get(pe).filter((event) => event.operationId === 'GENESIS' || (this.#published.has(event.operationId) && event.principalId === context.principalId && event.projectScopeId === context.projectScopeId && event.scopeKind === context.scopeKind && event.scopeOwnerKey === context.scopeOwnerKey)));
    return this.#transact({ context, operationId, operation: 'audit.read', actorId, runId, bindingHash, decisionEvidence, request: { context, authority }, apply: result });
  }
  recordDenied({ context, operationId, operation, reasonCode, actorId, runId, bindingHash, decisionEvidence }) {
    try { return this.#transact({ context, operationId, operation, decision: 'deny', reasonCode, actorId, runId, bindingHash, decisionEvidence: { ...decisionEvidence, outcome: 'deny' }, request: { context, operation, reasonCode }, apply: () => ({ denied: true, reasonCode }) }); }
    catch (error) { this.#alert('PRIMARY_AUDIT_UNAVAILABLE', operationId); try { this.#emergency.append(owned({ operation, reasonCode, redacted: true, occurredAt: this.#clock() })); return owned({ denied: true, reasonCode }); } catch { this.#alert('EMERGENCY_AUDIT_UNAVAILABLE', operationId); throw new Error('SECURITY_SERVICE_UNAVAILABLE'); } }
  }
  #validateLifecycleDecision(decision, current, bindingHash, actorId, holdStateHash) { if (!decision || decision.human !== true || text('decisionOwner', decision.decisionOwner).length === 0 || decision.executorId !== actorId || decision.bindingHash !== bindingHash || decision.recordEvidenceHash !== current.evidenceHash || decision.policyRevision !== current.retention.policyRevision || decision.policyHash !== current.retention.policyHash || decision.holdStateHash !== holdStateHash || decision.expiresAt <= this.#clock()) throw new Error('LIFECYCLE_AUTHORIZATION_INVALID'); }
  placeHold({ context, recordId, holdId, decision, operationId, actorId, runId, bindingHash, decisionEvidence }) { const key = this.#recordKey(context, recordId); const current = this.#records.get(key)?.at(-1); if (!current) throw new Error('RECORD_NOT_FOUND'); const emptyHoldHash = digest('GAT-HOLD-STATE-V1', null); this.#validateLifecycleDecision(decision, current, bindingHash, actorId, emptyHoldHash); return this.#transact({ context, operationId, operation: 'hold.place', resourceId: recordId, actorId, runId, bindingHash, decisionEvidence, request: { context, recordId, holdId, decision }, apply: () => { const hold = { holdId: text('holdId', holdId), bindingHash, decisionOwner: decision.decisionOwner, policyRevision: decision.policyRevision, active: true }; this.#holds.set(key, owned({ ...hold, holdStateHash: digest('GAT-HOLD-STATE-V1', hold) })); return this.#holds.get(key); } }); }
  releaseHold({ context, recordId, holdId, decision, operationId, actorId, runId, bindingHash, decisionEvidence }) { const key = this.#recordKey(context, recordId); const current = this.#records.get(key)?.at(-1); const hold = this.#holds.get(key); if (!current || hold?.holdId !== holdId) throw new Error('HOLD_MISMATCH'); this.#validateLifecycleDecision(decision, current, bindingHash, actorId, hold.holdStateHash); return this.#transact({ context, operationId, operation: 'hold.release', resourceId: recordId, actorId, runId, bindingHash, decisionEvidence, request: { context, recordId, holdId, decision }, apply: () => { this.#holds.delete(key); return { released: true, priorHoldStateHash: hold.holdStateHash }; } }); }
  purge({ context, recordId, authorization, fenceToken, operationId, actorId, runId, bindingHash, decisionEvidence }) {
    const key = this.#recordKey(context, recordId); const current = this.#records.get(key)?.at(-1); if (!current || current.status !== 'tombstoned' || this.#holds.has(key)) throw new Error('PURGE_INELIGIBLE'); const now = this.#clock();
    const emptyHoldHash = digest('GAT-HOLD-STATE-V1', null); if (!authorization || authorization.human !== true || authorization.recordId !== recordId || authorization.expectedRevision !== current.revision || authorization.expiresAt <= now || authorization.bindingHash !== bindingHash || authorization.executorId !== actorId || typeof authorization.decisionOwner !== 'string' || authorization.decisionOwner.length === 0 || authorization.policyRevision !== current.retention.policyRevision || authorization.policyHash !== current.retention.policyHash || authorization.recordEvidenceHash !== current.evidenceHash || authorization.holdStateHash !== emptyHoldHash || !Number.isFinite(authorization.backupPurgeDeadline) || authorization.backupPurgeDeadline < now || !SHA.test(authorization.inventoryHash)) throw new Error('PURGE_AUTHORIZATION_INVALID');
    const release = this.#lifecycle.acquire(key, fenceToken); try { const result = this.#transact({ context, operationId, operation: 'record.purge', resourceId: recordId, actorId, runId, bindingHash, decisionEvidence, request: { context, recordId, authorization, fenceToken }, apply: (event) => { const core = { recordKey: key, recordId, purgedRevision: current.revision, recordEvidenceHash: current.evidenceHash, recordContentHashes: this.#records.get(key).map((version) => version.contentHash), authorizationHash: digest('GAT-PURGE-AUTH-V1', authorization), auditHash: event.eventHash, policyRevision: authorization.policyRevision, policyHash: authorization.policyHash, holdStateHash: authorization.holdStateHash, decisionOwner: authorization.decisionOwner, executorId: authorization.executorId, inventoryHash: authorization.inventoryHash, dispositions: { primary: 'deleted', index: 'deleted', materialization: 'deleted' }, purgedAt: now, backupPurgeDeadline: authorization.backupPurgeDeadline }; const manifest = owned({ ...core, manifestHash: digest('GAT-PURGE-MANIFEST-V1', core) }); this.#records.delete(key); return manifest; } }); return result; } finally { release(); }
  }
  verifyAudit() { for (const [pe, chain] of this.#audit) { let prior = null; for (let index = 0; index < chain.length; index++) { const { eventHash, operationId: _operationId, priorDigest, ...core } = chain[index]; if (core.sequence !== index || priorDigest !== prior || auditDigest(prior, core) !== eventHash) return false; if (index === 0) { const { signature, ...unsigned } = core; const expected = `sha256:${createHmac('sha256', this.#genesisSigningKey).update(canonical(unsigned)).digest('hex')}`; if (signature !== expected || core.signatureKeyId !== this.#genesis.signatureKeyId) return false; } prior = eventHash; } const high = this.#anchors.highWater(pe); if (high.hash !== prior || high.sequence !== chain.at(-1)?.sequence) return false; } return true; }
  #replayEffect(operationId, operation) { const effect = this.#sink.effect?.(operationId); if (!effect) throw new Error('DOMAIN_EFFECT_MISSING'); const key = effect.resourceId ? this.#recordKey(effect.context, effect.resourceId) : null; if (effect.operation === 'record.create') { if (!this.#records.has(key)) this.#records.set(key, [owned(effect.result)]); } else if (effect.operation === 'record.revise') { const versions = this.#records.get(key) ?? []; if ((versions.at(-1)?.revision ?? 0) < effect.result.revision) this.#records.set(key, [...versions, owned(effect.result)]); } else if (effect.operation === 'record.purge') this.#records.delete(key); else if (effect.operation === 'hold.place') this.#holds.set(key, owned(effect.result)); else if (effect.operation === 'hold.release') this.#holds.delete(key); this.#published.add(operationId); this.#idempotency.set(operationId, { requestHash: effect.requestHash, result: owned(effect.result) }); }
  backup() { return owned({ schema: 'gat.backup.v1', epoch: this.#epoch, genesis: this.#genesis, records: [...this.#records], audit: [...this.#audit], journal: [...this.#journal], published: [...this.#published], idempotency: [...this.#idempotency], holds: [...this.#holds], anchorInventory: this.#anchors.snapshot(), purgeInventory: this.#lifecycle.inventory() }); }
  restoreEvidence() { return owned(this.#restoreEvidence); }
  static restore(backup, options = {}) {
    if (!backup || backup.schema !== 'gat.backup.v1' || !Array.isArray(backup.anchorInventory) || !Array.isArray(backup.purgeInventory)) throw new Error('BACKUP_INVALID'); const store = new PartitionStore({ ...options, epoch: backup.epoch, genesis: backup.genesis }); store.#records = new Map(clone(backup.records)); store.#audit = new Map(clone(backup.audit)); store.#journal = new Map(clone(backup.journal)); store.#published = new Set(clone(backup.published)); store.#idempotency = new Map(clone(backup.idempotency)); store.#holds = new Map(clone(backup.holds));
    const externalEvents = typeof store.#sink.committed === 'function' ? store.#sink.committed() : [];
    for (const [pe, chain] of store.#audit) { const target = store.#anchors.head(pe); if (target !== chain.at(-1)?.eventHash) { const suffix = externalEvents.filter((event) => `${encodeURIComponent(event.tenantId)}#${encodeURIComponent(event.epoch)}` === pe && event.sequence > chain.at(-1).sequence).sort((a, b) => a.sequence - b.sequence); let prior = chain.at(-1).eventHash; for (const event of suffix) { if (event.priorDigest !== prior) throw new Error('ANCHOR_HIGH_WATER_MISMATCH'); chain.push(clone(event)); store.#replayEffect(event.operationId, event.operation); prior = event.eventHash; if (prior === target) break; } if (prior !== target) throw new Error('ANCHOR_HIGH_WATER_MISMATCH'); store.#restoreEvidence.push({ partitionEpoch: pe, action: 'anchored_suffix_reconciled', head: target }); } }
    for (const manifest of store.#lifecycle.inventory()) { store.#records.delete(manifest.recordKey); store.#restoreEvidence.push({ recordKey: manifest.recordKey, action: 'purge_manifest_won', manifestHash: manifest.manifestHash, inventoryHash: manifest.inventoryHash }); }
    if (!store.verifyAudit()) throw new Error('AUDIT_CHAIN_INVALID'); store.recover(); return store;
  }
}

export const MemoryStore = PartitionStore;
