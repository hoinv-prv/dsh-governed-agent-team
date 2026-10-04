import { type Context } from '@deepseek-ai/cordis';
import type { ReviewTestReceipt, ReviewKnownRisk, ReviewRationaleRef, TaskContract, CompletionProposal } from '@deepseek-ai/dsh-durable-agent';
import type { ExecutionReviewInstaller } from './execution-binding.ts';
export interface ReviewerAssignment {
    readonly rootSessionId: string;
    readonly executionId: string;
    readonly sessionId: string;
    readonly memberId: string;
    readonly generation: number;
    readonly taskId: string;
    readonly taskRevision: number;
    readonly configurationSha256: string;
}
export interface ReviewedCandidate extends ReviewerAssignment {
    readonly attemptId: string;
    readonly candidateSha256: string;
    readonly contractSha256: string;
    readonly proposalSha256: string;
}
export interface ReviewSelection {
    readonly reference: string;
    readonly revision: string;
}
export interface ReviewAuditEvent {
    readonly kind: 'packet' | 'evidence' | 'rationale';
    readonly status: 'requested' | 'prepared' | 'denied' | 'error';
    readonly reviewerExecutionId: string;
    readonly candidateExecutionId: string;
    readonly candidateSha256: string;
    readonly packetSha256?: string;
    readonly ref?: string;
    readonly requestId?: string;
    readonly rationaleId?: string;
    readonly reasonSha256?: string;
    readonly bytes?: number;
}
export interface ReviewInput {
    readonly selection: ReviewSelection;
    readonly reviewer: ReviewerAssignment;
    readonly candidate: ReviewedCandidate;
    readonly contract: TaskContract;
    readonly proposal: CompletionProposal;
    readonly policy: Readonly<{
        testReceipts: readonly ReviewTestReceipt[];
        requiredTestSuites: readonly string[];
        knownRisks: readonly ReviewKnownRisk[];
        rationaleRefs: readonly ReviewRationaleRef[];
    }>;
    readonly limits: Readonly<{
        maxPacketValidationReads: number;
        maxPacketValidationBytes: number;
        maxEvidenceCalls: number;
        maxEvidenceBytes: number;
        maxEvidenceTotalBytes: number;
        maxRationaleCalls: number;
        maxRationaleAttempts: number;
        maxRationaleTotalBytes: number;
    }>;
    /** Trusted host authenticates the exact current reviewer and stored candidate association. */
    assertCurrent(): void;
    readRef(request: Readonly<{
        ref: string;
        maxBytes: number;
        purpose: 'packet-validation' | 'evidence' | 'rationale';
    }>): Promise<Uint8Array>;
    verifyReceipt(receipt: Readonly<ReviewTestReceipt>): Promise<boolean>;
    audit(event: Readonly<ReviewAuditEvent>): Promise<void>;
}
export interface ReviewInputPort {
    resolve(request: Readonly<{
        selection: ReviewSelection;
        reviewer: ReviewerAssignment;
    }>): Promise<ReviewInput | undefined>;
}
declare module '@deepseek-ai/cordis' {
    interface Context {
        gatDurableReviewInput: ReviewInputPort;
    }
}
/** Resolve the optional service only when a reviewer execution is created. */
export declare function resolveReviewInstaller(ctx: Context): ExecutionReviewInstaller;
//# sourceMappingURL=execution-review.d.ts.map