import { Service, type Context } from '@deepseek-ai/cordis';
export declare const DURABLE_AGENT_SERVICE_NAME: "durableAgent";
export declare const DURABLE_AGENT_API_VERSION: 1;
export type DurableAgentStorageScope = 'workspace' | 'global';
export type DurableAgentContextMode = 'fresh' | 'fork';
/**
 * A host-resolved declaration. Scope is mandatory: only a separate adapter may
 * supply defaults or translate an external manifest into this shape.
 */
export interface DurableAgentDeclaration {
    readonly name: string;
    readonly description: string;
    readonly prompt: string;
    readonly context: DurableAgentContextMode;
    readonly provider: string;
    readonly model: string;
    readonly reasoningEffort?: string;
    readonly scope: DurableAgentStorageScope;
}
export interface DurableAgentFeatureFlags {
    readonly selectiveMemoryRead: boolean;
    readonly memoryCandidateSubmission: boolean;
    readonly approvedMemoryCommit: boolean;
    readonly workingArtifacts: boolean;
}
export declare const DURABLE_AGENT_FEATURE_NAMES: readonly ["selectiveMemoryRead", "memoryCandidateSubmission", "approvedMemoryCommit", "workingArtifacts"];
declare const durableAgentRefBrand: unique symbol;
/** Issued only by a provider after provisioning an explicit declaration. */
export type DurableAgentRef = string & {
    readonly [durableAgentRefBrand]: 'DurableAgentRef';
};
declare const workingLocationBrand: unique symbol;
/**
 * Trusted-host-only working-artifact target. Consumers must treat the value as
 * opaque and must not derive a profile, memory, or provider storage root from it.
 */
export type DurableAgentWorkingLocation = string & {
    readonly [workingLocationBrand]: 'DurableAgentWorkingLocation';
};
export interface DurableAgentPublicMember {
    readonly ref: DurableAgentRef;
    readonly name: string;
    readonly description: string;
}
export interface DurableAgentMemoryCatalogItem {
    readonly id: string;
    readonly title: string;
    readonly retrievalCondition: string;
}
export interface DurableAgentTaskContextCapabilities extends DurableAgentFeatureFlags {
}
export interface DurableAgentTaskContextProvenance {
    readonly scope: DurableAgentStorageScope;
    readonly provider: string;
    /** Opaque provider generation; never a path or storage-format identifier. */
    readonly generation: string;
}
/**
 * A deeply immutable, path-free snapshot produced afresh for one admitted call.
 * `memoryCatalog` contains retrieval metadata only and never eager item bodies.
 */
export interface DurableAgentTaskContext {
    readonly member: Readonly<DurableAgentPublicMember>;
    readonly guidance: string;
    readonly memoryCatalog: readonly Readonly<DurableAgentMemoryCatalogItem>[];
    readonly revision: number;
    readonly provenance: Readonly<DurableAgentTaskContextProvenance>;
    readonly capabilities: Readonly<DurableAgentTaskContextCapabilities>;
}
export interface DurableAgentMemoryItem {
    readonly id: string;
    readonly title: string;
    readonly retrievalCondition: string;
    readonly content: string;
    /** Content revision from which this value was read. */
    readonly revision: number;
}
export type DurableAgentMemoryConfidence = 'low' | 'medium' | 'high';
/** Candidate input has no approval or canonical-status field by design. */
export interface DurableAgentMemoryCandidateInput {
    readonly title: string;
    readonly retrievalCondition: string;
    readonly content: string;
    readonly provenance: string;
    readonly confidence: DurableAgentMemoryConfidence;
    readonly limitations: readonly string[];
}
export interface DurableAgentMemoryCandidate {
    readonly candidateId: string;
    readonly status: 'unconfirmed';
    readonly title: string;
    readonly retrievalCondition: string;
    readonly provenance: string;
    readonly confidence: DurableAgentMemoryConfidence;
    readonly limitations: readonly string[];
}
export interface DurableAgentCommitAuthorization {
    readonly kind: 'human' | 'authorized-host-workflow';
    /** Host-owned audit reference; it is not inferred from candidate content. */
    readonly authorizationRef: string;
}
export interface DurableAgentApprovedMemoryInput {
    readonly candidateId?: string;
    readonly item: Readonly<{
        id: string;
        title: string;
        retrievalCondition: string;
        content: string;
    }>;
    readonly authorization: Readonly<DurableAgentCommitAuthorization>;
}
export interface DurableAgentCommittedMemoryItem {
    readonly id: string;
    readonly title: string;
    readonly retrievalCondition: string;
    readonly revision: number;
    readonly status: 'confirmed';
}
/**
 * Provider-neutral Cordis port. Every operation after declaration validation
 * requires a service-issued reference. A reference grants only these Durable
 * Agent operations; it grants no filesystem, Team, Session, budget, approval,
 * tool, or delegation authority.
 */
export declare abstract class DurableAgentService extends Service {
    readonly apiVersion: 1;
    readonly features: Readonly<DurableAgentFeatureFlags>;
    protected constructor(ctx: Context, features: DurableAgentFeatureFlags);
    /** Validates a normalized explicit-scope declaration without creating storage. */
    abstract validateDeclaration(workspace: string, declaration: DurableAgentDeclaration): Promise<void>;
    /** Creates or verifies persistent identity and returns a generation-bound reference. */
    abstract provision(workspace: string, declaration: DurableAgentDeclaration): Promise<DurableAgentRef>;
    /** Freshly validates and returns a bounded immutable snapshot with no eager memory bodies. */
    abstract openTaskContext(memberRef: DurableAgentRef): Promise<Readonly<DurableAgentTaskContext>>;
    /** Selectively reads one item that still belongs to the referenced member. */
    abstract readMemoryItem(memberRef: DurableAgentRef, itemId: string): Promise<Readonly<DurableAgentMemoryItem>>;
    /** Records a reviewable value that is always explicitly unconfirmed. */
    abstract submitMemoryCandidate(memberRef: DurableAgentRef, candidate: DurableAgentMemoryCandidateInput): Promise<Readonly<DurableAgentMemoryCandidate>>;
    /** Commits confirmed memory only with explicit HUMAN or authorized-host evidence. */
    abstract commitMemoryItem(memberRef: DurableAgentRef, approvedInput: DurableAgentApprovedMemoryInput): Promise<Readonly<DurableAgentCommittedMemoryItem>>;
    /** Returns only the trusted-host working-artifact capability, never the storage root. */
    abstract workingLocation(memberRef: DurableAgentRef): Promise<DurableAgentWorkingLocation>;
    /**
     * Closes new admission, waits for admitted mutations, and releases process-local
     * resources. Persistent profile, memory, and working artifacts are not deleted.
     * A released reference is unauthorized for every subsequent operation.
     */
    abstract release(memberRef: DurableAgentRef): Promise<void>;
}
declare module '@deepseek-ai/cordis' {
    interface Context {
        durableAgent: DurableAgentService;
    }
}
export {};
//# sourceMappingURL=service.d.ts.map