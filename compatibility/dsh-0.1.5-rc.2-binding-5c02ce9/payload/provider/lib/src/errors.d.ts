export declare const DURABLE_AGENT_ERROR_CODES: readonly ["INCOMPATIBLE_API", "INVALID_DECLARATION", "UNAUTHORIZED_REFERENCE", "PROFILE_CONFLICT", "UNSUPPORTED_SCOPE", "INVALID_CONTEXT_DATA", "UNKNOWN_MEMORY_ITEM", "REJECTED_CANDIDATE", "CONCURRENT_MUTATION", "PROVIDER_UNAVAILABLE"];
export type DurableAgentErrorCode = typeof DURABLE_AGENT_ERROR_CODES[number];
export type DurableAgentReferenceState = 'missing' | 'foreign' | 'forged' | 'stale' | 'scope-mismatch' | 'released';
/** Deliberately path-free diagnostic values safe to return across the service boundary. */
export interface DurableAgentErrorDetails {
    readonly memberName?: string;
    readonly apiVersion?: number;
    readonly feature?: string;
    readonly scope?: 'workspace' | 'global';
    readonly referenceState?: DurableAgentReferenceState;
}
export declare class DurableAgentError extends Error {
    readonly name = "DurableAgentError";
    readonly code: DurableAgentErrorCode;
    readonly details: Readonly<DurableAgentErrorDetails>;
    constructor(code: DurableAgentErrorCode, details?: DurableAgentErrorDetails);
    toJSON(): Readonly<{
        name: 'DurableAgentError';
        code: DurableAgentErrorCode;
        message: string;
        details: Readonly<DurableAgentErrorDetails>;
    }>;
}
export declare function isDurableAgentError(value: unknown): value is DurableAgentError;
//# sourceMappingURL=errors.d.ts.map