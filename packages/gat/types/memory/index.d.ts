export interface PartitionContext { tenantId: string; principalId: string; projectScopeId: string; scopeKind: string; scopeOwnerKey: string }
export interface DecisionEvidence {
  decisionId: string; correlationId: string; decidedAt: number; outcome: 'allow' | 'deny'; matchedRules: string[];
  authoritative: { taskId: string; taskRevision: number; aipId: string; aipRevision: number; workspaceId: string; teamId: string; teamRevision: number; missionId: string; missionRevision: number };
  readinessHash: string; nativeApprovalHash: string; teamPlanHash: string; selectorHash: string; capabilityHash: string; policyHash: string; membershipHash: string;
}
export interface OperationEvidence { operationId: string; actorId: string; runId: string; bindingHash: string; decisionEvidence: DecisionEvidence; crashAt?: 'journaled' | 'sink_prepared_before_state' | 'sink_prepared' | 'local_effect_before_state' | 'local_committed' | 'anchor_cas_before_state' | 'anchored' | 'sink_commit_before_state' | 'sink_committed' | 'manifest_publish_before_state' | 'manifest_published' | 'published_set_before_state' | 'published' | 'idempotency_set_before_state' | 'idempotent' | null }
export function physicalPartitionKey(context: PartitionContext): string;
export class Crash extends Error { readonly boundary: string }
export class AnchorRegistry { head(auditPartition: string): string | null; highWater(auditPartition: string): Readonly<{ sequence: number; hash: string | null }>; compareAndSet(auditPartition: string, expectedHash: string | null, nextHash: string, nextSequence: number): void; snapshot(): readonly unknown[] }
export class TransactionalAuditSink { prepare(operationId: string, event: unknown): void; recordEffect(operationId: string, effect: unknown): void; commit(operationId: string): void; abort(operationId: string): void; committed(): readonly unknown[]; effect(operationId: string): Readonly<Record<string, unknown>> | null }
export class LifecycleRegistry { acquire(recordKey: string, token: string): () => void; publish(manifest: Record<string, unknown>): void; manifest(recordKey: string): Readonly<Record<string, unknown>> | null; inventory(): readonly unknown[] }
export class PartitionStore {
  constructor(options?: { clock?: () => number; auditSink?: TransactionalAuditSink; emergencySink?: { append(event: unknown): void }; operatorAlert?: { append(alert: unknown): void }; backendProbe?: (operation: string) => void; anchors?: AnchorRegistry; lifecycle?: LifecycleRegistry; epoch?: string; genesis?: { policyRevision: number; previousEpochHead: string | null; creationAuthority: Record<string, unknown>; signatureKeyId: string }; genesisSigningKey?: string });
  create(input: { context: PartitionContext; record: Record<string, unknown> } & OperationEvidence): Readonly<Record<string, unknown>>;
  revise(input: { context: PartitionContext; recordId: string; expectedRevision: number; patch: Record<string, unknown> } & OperationEvidence): Readonly<Record<string, unknown>>;
  tombstone(input: { context: PartitionContext; recordId: string; expectedRevision: number; tombstoneReason: string; patch?: Record<string, unknown> } & OperationEvidence): Readonly<Record<string, unknown>>;
  get(input: { context: PartitionContext; recordId: string; now?: number } & OperationEvidence): Readonly<Record<string, unknown>>;
  search(input: { context: PartitionContext; query: string; limit?: number; now?: number } & OperationEvidence): readonly Readonly<Record<string, unknown>>[];
  history(input: { context: PartitionContext; recordId: string }): readonly Readonly<Record<string, unknown>>[];
  auditRead(input: { context: PartitionContext; authority: Record<string, unknown> } & OperationEvidence): readonly Readonly<Record<string, unknown>>[];
  recordDenied(input: { context: PartitionContext; operation: string; reasonCode: string } & OperationEvidence): Readonly<Record<string, unknown>>;
  placeHold(input: { context: PartitionContext; recordId: string; holdId: string; decision: Record<string, unknown> } & OperationEvidence): Readonly<Record<string, unknown>>;
  releaseHold(input: { context: PartitionContext; recordId: string; holdId: string; decision: Record<string, unknown> } & OperationEvidence): Readonly<Record<string, unknown>>;
  purge(input: { context: PartitionContext; recordId: string; authorization: Record<string, unknown>; fenceToken: string } & OperationEvidence): Readonly<Record<string, unknown>>;
  recover(): void; verifyAudit(): boolean; backup(): Readonly<Record<string, unknown>>; restoreEvidence(): readonly Readonly<Record<string, unknown>>[];
  static restore(backup: unknown, options?: ConstructorParameters<typeof PartitionStore>[0]): PartitionStore;
}
export { PartitionStore as MemoryStore };
