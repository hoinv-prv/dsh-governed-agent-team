import { reviewContribution, type ReviewPacket, type ReviewPacketOptions, type ReviewerVerdict } from './review-packet.js';
export interface ReviewBinding {
    readonly contractSha256: string;
    readonly proposalSha256: string;
    readonly attemptId: string;
    readonly workerId: string;
    readonly reviewerId: string;
}
export interface FreshReviewRequest {
    readonly context: 'fresh';
    readonly messages: readonly Readonly<{
        role: 'system' | 'user';
        content: string;
    }>[];
    readonly tools: ReturnType<typeof reviewContribution>['tools'];
}
export interface RationaleAuditEvent {
    readonly reviewPacketSha256: string;
    readonly rationaleId: string;
    readonly reason: string;
    readonly ref: string | null;
    readonly sha256: string | null;
    readonly status: 'requested' | 'served' | 'denied' | 'error';
    readonly bytes: number;
}
export interface ReviewTools {
    readonly readEvidence: (ref: string) => Promise<string>;
    readonly requestRationale: (request: Readonly<{
        id: string;
        reason: string;
    }>) => Promise<string>;
}
export interface FreshReviewOptions extends ReviewPacketOptions {
    /** Host must implement an actual new session; never append/fork worker or coordinator history. */
    readonly startFresh: (request: Readonly<FreshReviewRequest>, tools: Readonly<ReviewTools>) => Promise<unknown>;
    /** Persist append-only request/decision records before releasing rationale content. */
    readonly audit: (event: Readonly<RationaleAuditEvent>) => Promise<void>;
    /** Compare with authoritative current identity/state, before dispatch AND after review. */
    readonly assertCurrent: (binding: Readonly<ReviewBinding>) => Promise<boolean>;
    readonly rationaleBudget: Readonly<{
        maxRequests: number;
        maxBytes: number;
    }>;
}
export interface FreshReviewResult {
    readonly packet: Readonly<ReviewPacket>;
    readonly verdict: Readonly<ReviewerVerdict>;
    readonly rationaleAudit: readonly Readonly<RationaleAuditEvent>[];
}
/** Builds host-attested evidence, sends ONLY a fresh bounded payload, validates model output,
 * then rechecks exact bytes and authoritative state. No acceptance/commit is performed.
 * The transport is trusted to honor context:'fresh'; this adapter cannot inspect its hidden history. */
export declare function runFreshReview(contractInput: unknown, proposalInput: unknown, options: Readonly<FreshReviewOptions>): Promise<Readonly<FreshReviewResult>>;
//# sourceMappingURL=review-host.d.ts.map