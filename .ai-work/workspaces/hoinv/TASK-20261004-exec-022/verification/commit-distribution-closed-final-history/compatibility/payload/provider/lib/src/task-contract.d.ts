export declare const TASK_CONTRACT_FORMAT: "durable-agent-task-contract/1";
export declare const COMPLETION_PROPOSAL_FORMAT: "durable-agent-completion-proposal/1";
export interface TaskInput {
    readonly id: string;
    readonly version: string;
    readonly sha256: string;
}
export interface TaskOutput {
    readonly id: string;
    readonly description: string;
}
export interface AcceptanceCriterion {
    readonly id: string;
    readonly requirement: string;
    readonly evidenceRequired: string;
    readonly outputIds: readonly string[];
}
/** Descriptive limits only: the host still enforces actual execution authority. */
export interface TaskContract {
    readonly format: typeof TASK_CONTRACT_FORMAT;
    readonly taskId: string;
    readonly revision: number;
    readonly outcome: string;
    readonly nonGoals: readonly string[];
    readonly inputs: readonly TaskInput[];
    readonly outputs: readonly TaskOutput[];
    readonly acceptance: readonly AcceptanceCriterion[];
    readonly authorityLimits: readonly string[];
    readonly stopConditions: readonly string[];
}
export interface CompletionArtifact {
    readonly outputId: string;
    readonly ref: string;
    readonly sha256: string;
}
export interface CompletionEvidence {
    readonly id: string;
    readonly ref: string;
    readonly sha256: string;
    readonly outputIds: readonly string[];
}
export interface CriterionClaim {
    readonly criterionId: string;
    readonly evidenceIds: readonly string[];
}
/** A worker proposal is never an acceptance decision, permission, or commit. */
export interface CompletionProposal {
    readonly format: typeof COMPLETION_PROPOSAL_FORMAT;
    readonly taskId: string;
    readonly contractSha256: string;
    readonly attemptId: string;
    readonly workerId: string;
    readonly inputs: readonly TaskInput[];
    readonly artifacts: readonly CompletionArtifact[];
    readonly evidence: readonly CompletionEvidence[];
    readonly claims: readonly CriterionClaim[];
    readonly blockers: readonly string[];
}
export interface TaskPacket {
    readonly role: 'worker' | 'reviewer';
    readonly contract: Readonly<TaskContract>;
    readonly contractSha256: string;
    readonly instruction: string;
}
export interface CompletionReview {
    readonly status: 'verified' | 'rejected' | 'blocked';
    readonly contractSha256: string;
    readonly proposalSha256: string;
    readonly attemptId: string;
    readonly reviewerId: string;
    readonly criteria: readonly Readonly<{
        criterionId: string;
        passed: boolean;
        reason: string;
    }>[];
    readonly reasons: readonly string[];
}
/** Trusted host verifier must resolve refs under its own ACL, check digests and
 * test the requirement, not merely trust claims or tool exit codes. No execution
 * permission is conveyed by this packet. Exceptions fail closed. */
export type CriterionVerifier = (packet: Readonly<{
    contract: Readonly<TaskContract>;
    criterion: Readonly<AcceptanceCriterion>;
    artifacts: readonly CompletionArtifact[];
    evidence: readonly CompletionEvidence[];
}>) => Promise<Readonly<{
    passed: boolean;
    reason: string;
}>>;
export declare function normalizeTaskContract(input: unknown): Readonly<TaskContract>;
export declare function taskContractSha256(input: unknown): string;
export declare function createTaskPacket(input: unknown, role: 'worker' | 'reviewer'): Readonly<TaskPacket>;
export declare function normalizeCompletionProposal(input: unknown): Readonly<CompletionProposal>;
/** Host supplies the CURRENT contract/attempt and an independent verifier.
 * Result is evidence assessment only; the host owns authorization and commit. */
export declare function reviewCompletion(input: unknown, proposalInput: unknown, options: Readonly<{
    attemptId: string;
    workerId: string;
    reviewerId: string;
    verify: CriterionVerifier;
}>): Promise<Readonly<CompletionReview>>;
//# sourceMappingURL=task-contract.d.ts.map