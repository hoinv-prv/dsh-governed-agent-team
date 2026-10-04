import type { ActionResult, ApprovedPlan, PlanApproval, TaskRecord, ValidatedPlan } from './types.js';
/** The on-disk format is deliberately a small, local replacement snapshot. */
export declare const EXECUTION_SNAPSHOT_VERSION: 1;
export declare const UNKNOWN_OUTCOME: "UNKNOWN_OUTCOME";
export interface ExecutionSnapshot {
    readonly schemaVersion: typeof EXECUTION_SNAPSHOT_VERSION;
    readonly missionId: string;
    readonly revision: number;
    readonly planSha256: string;
    readonly runId: string;
    readonly generation: number;
    readonly tasks: readonly TaskRecord[];
}
export interface SnapshotIdentity {
    readonly missionId: string;
    readonly revision: number;
    readonly planSha256: string;
    readonly runId: string;
}
export interface SnapshotExpectation extends Partial<SnapshotIdentity> {
    readonly generation?: number;
}
export interface ReconcileOptions {
    /** Timestamp used for the synthetic terminal attempt created by recovery. */
    readonly now?: number;
}
/** Strictly validates a complete snapshot against the approved plan and identity. */
export declare function validateExecutionSnapshot(value: unknown, planInput: ApprovedPlan | ValidatedPlan, approval?: PlanApproval, expected?: SnapshotExpectation): ExecutionSnapshot;
export declare function createExecutionSnapshot(planInput: ApprovedPlan | ValidatedPlan, runId: string, approval?: PlanApproval, generation?: number): ExecutionSnapshot;
/** Alias kept intentionally small so callers can use the runner terminology. */
export declare const createSnapshot: typeof createExecutionSnapshot;
export declare const validateSnapshot: typeof validateExecutionSnapshot;
/** Convert an interrupted running task into a durable unknown-outcome block. */
export declare function reconcileExecutionSnapshot(value: unknown, planInput: ApprovedPlan | ValidatedPlan, approval?: PlanApproval, options?: ReconcileOptions): ExecutionSnapshot;
export declare const reconcileSnapshot: typeof reconcileExecutionSnapshot;
/** Explicit caller acknowledgement permits only a remaining retry of unknown outcome. */
export declare function resumeExecutionSnapshot(value: unknown, planInput: ApprovedPlan | ValidatedPlan, approval?: PlanApproval): ExecutionSnapshot;
export declare const resumeSnapshot: typeof resumeExecutionSnapshot;
/** Persist exactly one canonical complete snapshot using same-directory replacement. */
export declare function writeExecutionSnapshot(path: string, snapshot: ExecutionSnapshot): Promise<void>;
export declare const writeSnapshot: typeof writeExecutionSnapshot;
export declare const settleSnapshot: typeof writeExecutionSnapshot;
export interface DurableExecutionStoreOptions {
    readonly approval?: PlanApproval;
    readonly now?: () => number;
}
/** Local snapshot store; it is not a database, lease, append-only log, or power-loss guarantee. */
export declare class DurableExecutionStore {
    readonly path: string;
    readonly plan: ValidatedPlan;
    readonly runId: string;
    private readonly now;
    constructor(path: string, planInput: ApprovedPlan | ValidatedPlan, runId: string, options?: DurableExecutionStoreOptions);
    initialize(): Promise<ExecutionSnapshot>;
    load(expected?: SnapshotExpectation): Promise<ExecutionSnapshot>;
    read(expected?: SnapshotExpectation): Promise<ExecutionSnapshot>;
    commit(snapshot: ExecutionSnapshot): Promise<ExecutionSnapshot>;
    save(snapshot: ExecutionSnapshot): Promise<ExecutionSnapshot>;
    recover(options?: ReconcileOptions): Promise<ExecutionSnapshot>;
    resume(): Promise<ExecutionSnapshot>;
    acknowledgeUnknownOutcome(): Promise<ExecutionSnapshot>;
    startTask(taskId: string, startedAt?: number): Promise<ExecutionSnapshot>;
    settleTask(taskId: string, result: ActionResult, finishedAt?: number): Promise<ExecutionSnapshot>;
    settle(taskId: string, result: ActionResult, finishedAt?: number): Promise<ExecutionSnapshot>;
}
export declare const ExecutionStore: typeof DurableExecutionStore;
export declare const DurableStore: typeof DurableExecutionStore;
export declare const DurableSnapshotStore: typeof DurableExecutionStore;
export declare function openDurableStore(path: string, plan: ApprovedPlan | ValidatedPlan, runId: string, options?: DurableExecutionStoreOptions): Promise<DurableExecutionStore>;
export declare const openStore: typeof openDurableStore;
export declare function readExecutionSnapshot(path: string, plan: ApprovedPlan | ValidatedPlan, runId: string, options?: DurableExecutionStoreOptions): Promise<ExecutionSnapshot>;
export declare const readSnapshot: typeof readExecutionSnapshot;
/** Useful when callers need the canonical bytes/hash without changing the store. */
export declare function snapshotCanonicalJson(snapshot: ExecutionSnapshot): string;
export declare function snapshotCanonicalHash(snapshot: ExecutionSnapshot): string;
//# sourceMappingURL=store.d.ts.map