import type { ChildProcess } from 'node:child_process';
/**
 * Product DTOs frozen by store-contract-baseline.v5.md §§2-3.
 * They are intentionally separate from both dsh-wbs/1 and the legacy MVP
 * runner compatibility types below.
 */
export declare const RUNTIME_PLAN_FORMAT: "durable-agent-runtime-plan/1";
export declare const RUNTIME_APPROVAL_FORMAT: "durable-agent-runtime-approval/1";
export type RuntimeFileOperationV1 = 'read' | 'write' | 'append' | 'delete';
export interface RuntimeFileReadActionV1 {
    readonly kind: 'file';
    readonly operation: 'read';
    readonly path: string;
}
export interface RuntimeFileWriteActionV1 {
    readonly kind: 'file';
    readonly operation: 'write';
    readonly path: string;
    readonly content: string;
}
export interface RuntimeFileAppendActionV1 {
    readonly kind: 'file';
    readonly operation: 'append';
    readonly path: string;
    readonly content: string;
}
export interface RuntimeFileDeleteActionV1 {
    readonly kind: 'file';
    readonly operation: 'delete';
    readonly path: string;
}
export type RuntimeFileActionV1 = RuntimeFileReadActionV1 | RuntimeFileWriteActionV1 | RuntimeFileAppendActionV1 | RuntimeFileDeleteActionV1;
export interface RuntimeCommandActionV1 {
    readonly kind: 'command';
    readonly argv: readonly string[];
    readonly cwd: string;
    readonly timeoutMs: number;
    readonly expectedExitCode: number;
}
export type RuntimeActionV1 = RuntimeFileActionV1 | RuntimeCommandActionV1;
export interface RuntimeTaskV1 {
    readonly id: string;
    readonly title: string;
    readonly dependencies: readonly string[];
    readonly action: RuntimeActionV1;
    readonly maxAttempts?: 1 | 2;
    readonly retryable?: boolean;
}
export interface RuntimePlanV1 {
    readonly format: typeof RUNTIME_PLAN_FORMAT;
    readonly missionId: string;
    readonly revision: number;
    readonly maxParallel: 1;
    readonly tasks: readonly RuntimeTaskV1[];
}
export interface NormalizedRuntimeTaskV1 extends Omit<RuntimeTaskV1, 'maxAttempts' | 'retryable'> {
    readonly maxAttempts: 1 | 2;
    readonly retryable: boolean;
}
export interface NormalizedRuntimePlanV1 extends Omit<RuntimePlanV1, 'tasks'> {
    readonly tasks: readonly NormalizedRuntimeTaskV1[];
}
export interface RuntimeApprovalV1 {
    readonly format: typeof RUNTIME_APPROVAL_FORMAT;
    readonly missionId: string;
    readonly revision: number;
    readonly planSha256: string;
    readonly decision: 'APPROVED';
    readonly approver: string;
    readonly approvedAt: number;
}
export interface RuntimeContractBindingV1 {
    readonly plan: NormalizedRuntimePlanV1;
    readonly planSha256: string;
    readonly approval: RuntimeApprovalV1;
    readonly approvalSha256: string;
}
/** Runner-only authority. This is not part of RuntimePlanV1 or its hash. */
export interface RuntimeExecutionPolicyV1 {
    readonly workspaceRoot: string;
    readonly allowedCommands: readonly RuntimeCommandActionV1[];
}
export interface ValidatedRuntimeExecutionV1 extends RuntimeContractBindingV1 {
    readonly policy: RuntimeExecutionPolicyV1;
}
export interface RuntimeAttemptIdentityV1 {
    readonly taskId: string;
    readonly attemptOrdinal: number;
    readonly attemptId: string;
    readonly idempotencyKey: string;
}
export interface RuntimeTaskAttemptV1 extends RuntimeAttemptIdentityV1 {
    readonly startedAt: number;
    readonly settledAt: number;
    readonly state: 'completed' | 'blocked' | 'failed';
    readonly result: ActionResult;
}
export interface RuntimeTaskRecordV1 {
    readonly task: NormalizedRuntimeTaskV1;
    readonly state: TaskState;
    readonly attemptCount: number;
    readonly attempts: readonly RuntimeTaskAttemptV1[];
    readonly result?: ActionResult;
}
export interface RuntimeRunnerOptionsV1 {
    readonly runId: string;
    /** Must durably consume the supplied identity before resolving; the store owns timestamps. */
    readonly persistAttempt: (attempt: Readonly<RuntimeAttemptIdentityV1>) => void | Promise<void>;
    readonly now?: () => number;
    readonly onTransition?: (record: RuntimeTaskRecordV1, from: TaskState, to: TaskState) => void | Promise<void>;
}
export interface RuntimeRunResultV1 {
    readonly ok: boolean;
    readonly state: 'completed' | 'failed' | 'blocked';
    readonly tasks: readonly RuntimeTaskRecordV1[];
    readonly blocker?: string;
}
export declare const TASK_STATES: readonly ["pending", "ready", "running", "completed", "blocked", "failed"];
export type TaskState = typeof TASK_STATES[number];
export type FileOperation = 'read' | 'write' | 'append' | 'delete';
export interface FileAction {
    readonly kind: 'file';
    readonly path: string;
    readonly operation?: FileOperation;
    readonly op?: FileOperation;
    readonly content?: string;
}
export interface ExactCommand {
    readonly argv: readonly string[];
    readonly cwd: string;
    readonly timeoutMs: number;
    readonly expectedExitCode: number;
}
export interface CommandAction {
    readonly kind: 'command';
    readonly argv?: readonly string[];
    readonly cwd?: string;
    readonly timeoutMs?: number;
    readonly expectedExitCode?: number;
    readonly command?: ExactCommand;
    /** Deliberately accepted only so validation can fail closed. */
    readonly shell?: boolean;
}
export type TaskAction = FileAction | CommandAction;
export interface ApprovedTask {
    readonly id: string;
    readonly dependencies: readonly string[];
    readonly action: TaskAction;
    readonly maxAttempts?: number;
    readonly retryable?: boolean;
}
export interface PlanApproval {
    readonly missionId: string;
    readonly revision: number;
    readonly planSha256: string;
    readonly decision: 'approve';
}
export interface ApprovedPlan {
    readonly missionId: string;
    readonly revision: number;
    readonly planSha256: string;
    readonly workspaceRoot: string;
    readonly tasks: readonly ApprovedTask[];
    readonly allowedCommands: readonly ExactCommand[];
    readonly approval?: PlanApproval;
    readonly maxParallel?: number;
    readonly max_parallel?: number;
}
export interface ValidatedPlan extends ApprovedPlan {
    readonly approval: PlanApproval;
    readonly maxParallel: 1;
    readonly tasks: readonly ApprovedTask[];
    readonly allowedCommands: readonly ExactCommand[];
}
export interface TaskAttempt {
    readonly taskId: string;
    readonly attempt: number;
    readonly attemptId: string;
    readonly idempotencyKey: string;
    readonly startedAt: number;
    readonly finishedAt?: number;
    readonly state: Exclude<TaskState, 'pending' | 'ready' | 'running'>;
    readonly result: ActionResult;
}
export interface TaskRecord {
    readonly task: ApprovedTask;
    readonly state: TaskState;
    readonly attempt: number;
    readonly attempts: readonly TaskAttempt[];
    readonly result?: ActionResult;
}
export interface ActionResult {
    readonly ok: boolean;
    readonly kind: TaskAction['kind'];
    readonly taskId?: string;
    readonly attemptId?: string;
    readonly idempotencyKey?: string;
    readonly exitCode?: number | null;
    readonly signal?: NodeJS.Signals | null;
    readonly timedOut?: boolean;
    readonly stdout?: string;
    readonly stderr?: string;
    readonly value?: string;
    readonly error?: string;
}
export interface RunnerOptions {
    readonly now?: () => number;
    readonly onTransition?: (record: TaskRecord, from: TaskState, to: TaskState) => void | Promise<void>;
}
export interface RunnerSnapshot {
    readonly missionId: string;
    readonly revision: number;
    readonly planSha256: string;
    readonly tasks: readonly TaskRecord[];
}
export interface RunResult {
    readonly ok: boolean;
    readonly state: 'completed' | 'blocked' | 'failed';
    readonly tasks: readonly TaskRecord[];
    readonly blocker?: string;
}
export type SpawnedProcess = ChildProcess;
export type Plan = ApprovedPlan;
export type Task = ApprovedTask;
export type CommandSpec = ExactCommand;
//# sourceMappingURL=types.d.ts.map