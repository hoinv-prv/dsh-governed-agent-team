import type { ActionResult, ApprovedPlan, NormalizedRuntimePlanV1, PlanApproval, RunResult, RunnerOptions, RunnerSnapshot, RuntimeActionV1, RuntimeApprovalV1, RuntimeContractBindingV1, RuntimeExecutionPolicyV1, RuntimePlanV1, RuntimeRunResultV1, RuntimeRunnerOptionsV1, RuntimeTaskRecordV1, RuntimeAttemptIdentityV1, TaskAction, TaskRecord, TaskState, ValidatedPlan, ValidatedRuntimeExecutionV1 } from './types.js';
export type RuntimeContractErrorCode = 'PLAN_INVALID' | 'APPROVAL_INVALID' | 'PLAN_APPROVAL_MISMATCH' | 'EXECUTION_POLICY_INVALID';
export declare class RuntimeContractError extends TypeError {
    readonly code: RuntimeContractErrorCode;
    constructor(code: RuntimeContractErrorCode, detail: string);
}
/** Normalize exactly once according to baseline v5 §3.2. */
export declare function normalizeRuntimePlan(input: unknown): NormalizedRuntimePlanV1;
export declare function canonicalRuntimePlanJson(input: unknown): string;
export declare function runtimePlanSha256(input: unknown): string;
export declare function validateRuntimeApproval(input: unknown, planInput: unknown): RuntimeApprovalV1;
export declare function canonicalRuntimeApprovalJson(input: unknown): string;
/** Hashes only an approval proven to bind the supplied normalized plan. */
export declare function runtimeApprovalSha256(input: unknown, planInput: unknown): string;
export declare function bindRuntimePlanApproval(planInput: unknown, approvalInput: unknown): RuntimeContractBindingV1;
export declare function validateRuntimeExecution(planInput: unknown, approvalInput: unknown, policyInput: unknown): ValidatedRuntimeExecutionV1;
export declare function runtimeTaskAttemptIdentity(plan: NormalizedRuntimePlanV1, planSha256: string, runIdInput: unknown, taskId: string, attemptOrdinalInput: unknown): RuntimeAttemptIdentityV1;
export declare function selectFirstReadyRuntimeTask(records: readonly RuntimeTaskRecordV1[]): RuntimeTaskRecordV1 | undefined;
export declare function executeRuntimeAction(actionInput: RuntimeActionV1 | unknown, executionInput: ValidatedRuntimeExecutionV1): Promise<ActionResult>;
export declare class RuntimeSequentialRunner {
    readonly execution: ValidatedRuntimeExecutionV1;
    private readonly options;
    private readonly records;
    private active;
    constructor(planInput: RuntimePlanV1 | unknown, approvalInput: RuntimeApprovalV1 | unknown, policyInput: RuntimeExecutionPolicyV1 | unknown, options: RuntimeRunnerOptionsV1);
    snapshot(): readonly RuntimeTaskRecordV1[];
    private timestamp;
    private transition;
    run(): Promise<RuntimeRunResultV1>;
}
export declare function createRuntimeRunner(plan: RuntimePlanV1 | unknown, approval: RuntimeApprovalV1 | unknown, policy: RuntimeExecutionPolicyV1 | unknown, options: RuntimeRunnerOptionsV1): RuntimeSequentialRunner;
export declare function runRuntimePlan(plan: RuntimePlanV1 | unknown, approval: RuntimeApprovalV1 | unknown, policy: RuntimeExecutionPolicyV1 | unknown, options: RuntimeRunnerOptionsV1): Promise<RuntimeRunResultV1>;
export declare function validateApprovedPlan(plan: ApprovedPlan, approval?: PlanApproval): ValidatedPlan;
export declare function selectDependencyReadyTask(snapshot: RunnerSnapshot | readonly TaskRecord[]): TaskRecord | undefined;
export declare function transitionTask(record: TaskRecord, next: TaskState): TaskRecord;
export declare function taskAttemptIdentity(plan: ValidatedPlan, taskId: string, attempt: number): {
    readonly attemptId: string;
    readonly idempotencyKey: string;
};
export declare function executeAction(action: TaskAction, plan: ValidatedPlan, taskId?: string, attempt?: number): Promise<ActionResult>;
export declare class SequentialRunner {
    readonly plan: ValidatedPlan;
    private readonly records;
    private readonly options;
    private active;
    constructor(plan: ApprovedPlan, approval?: PlanApproval, options?: RunnerOptions);
    snapshot(): RunnerSnapshot;
    private transition;
    private blockDependents;
    run(): Promise<RunResult>;
}
export declare function createRunner(plan: ApprovedPlan, approval?: PlanApproval, options?: RunnerOptions): SequentialRunner;
export declare function runApprovedPlan(plan: ApprovedPlan, approval?: PlanApproval, options?: RunnerOptions): Promise<RunResult>;
/** Short aliases keep the small MVP API convenient without adding another coordinator. */
export declare const validatePlan: typeof validateApprovedPlan;
export declare const selectReadyTask: typeof selectDependencyReadyTask;
export declare const executeTask: typeof executeAction;
//# sourceMappingURL=execution.d.ts.map