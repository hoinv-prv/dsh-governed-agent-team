import type { AgentRunId, MissionId } from '../identity.js';
import { type BudgetAccount, type BudgetVector } from './authority.js';
import { type SourceRevision } from './mission.js';
import { type JsonValue } from './runtime.js';
export declare const CONTEXT_ROUTES: readonly ["PINNED_ONLY", "DIRECT", "FRESH_SCOUT", "FULL_FORK"];
export type ContextRoute = typeof CONTEXT_ROUTES[number];
export interface ContextDecision {
    readonly missionId: MissionId;
    readonly runId: AgentRunId;
    readonly generation: number;
    readonly projectId: string;
    readonly route: ContextRoute;
    readonly reason: string;
    readonly policyHash: string;
    readonly skillHash: string;
    readonly allowedSources: readonly string[];
    readonly excludedSources: readonly string[];
    readonly allowedTools: readonly string[];
    readonly aiwsHash: string;
    readonly decisionHash: string;
    readonly budget: BudgetAccount;
}
export interface SearchDelegationPackage {
    readonly hash: string;
    readonly decisionHash: string;
    readonly missionId: MissionId;
    readonly runId: AgentRunId;
    readonly projectId: string;
    readonly generation: number;
    readonly objective: string;
    readonly questions: readonly string[];
    readonly exclusions: readonly string[];
    readonly sourceOrder: readonly string[];
    readonly allowedSources: readonly string[];
    readonly excludedSources: readonly string[];
    readonly tools: readonly string[];
    readonly reservation: BudgetVector;
    readonly createdAt: number;
    readonly deadline: number;
    readonly authorityOrder: readonly ['rules', 'wiki', 'project', 'memory'];
    readonly maxDepth: 1;
    readonly allowRecursion: false;
    readonly allowMutation: false;
    readonly allowUser: false;
    readonly includeRaw: false;
    readonly aiwsHash: string;
}
export interface RetrievalCall {
    readonly tool: string;
    readonly query: string;
    readonly normalizedArgsHash: string;
}
export interface Citation {
    readonly sourceRef: string;
    readonly sourceRevision: string;
    readonly sourceSha256: string;
    readonly locator: string;
    readonly excerpt: string;
    readonly excerptHash: string;
}
export interface DirectRetrievalManifest {
    readonly hash: string;
    readonly decisionHash: string;
    readonly missionId: MissionId;
    readonly runId: AgentRunId;
    readonly projectId: string;
    readonly generation: number;
    readonly status: 'COMPLETE' | 'PARTIAL';
    readonly query: string;
    readonly calls: readonly RetrievalCall[];
    readonly sources: readonly SourceRevision[];
    readonly sourceSetHash: string;
    readonly citations: readonly Citation[];
    readonly conflicts: readonly string[];
    readonly accounting: BudgetAccount;
    readonly createdAt: number;
    readonly expiresAt: number;
}
export interface CapsuleClaim extends Citation {
    readonly statement: string;
    readonly status: 'SUPPORTED' | 'CONFLICT';
}
export interface ContextCapsule {
    readonly hash: string;
    readonly packageHash: string;
    readonly decisionHash: string;
    readonly missionId: MissionId;
    readonly runId: AgentRunId;
    readonly projectId: string;
    readonly generation: number;
    readonly version: number;
    readonly ttlClass: 'VOLATILE' | 'STANDARD' | 'PINNED_IMMUTABLE';
    readonly conflictPolicy: 'PRESERVE';
    readonly createdAt: number;
    readonly expiresAt: number;
    readonly redactionProfile: string;
    readonly sourceSet: readonly SourceRevision[];
    readonly sourceSetHash: string;
    readonly conflicts: readonly string[];
    readonly accounting: BudgetAccount;
    readonly claims: readonly CapsuleClaim[];
}
export interface ForkEvaluation {
    readonly missionId: MissionId;
    readonly runId: AgentRunId;
    readonly projectId: string;
    readonly predicates: Readonly<{
        shortCleanParent: boolean;
        mostlyRelevant: boolean;
        wholePrefixAuthorized: boolean;
        independentReviewNotRequired: boolean;
        inheritedRoute: boolean;
        enoughWindow: boolean;
    }>;
    readonly authorizationHash: string;
    readonly completedPrefix: readonly JsonValue[];
    readonly completedPrefixEvents: number;
    readonly inFlightEvents: 0;
    readonly openTurnIndex: number;
    readonly provider: string;
    readonly model: string;
    readonly contextWindow: number;
    readonly inputTokens: number;
    readonly outputReserve: number;
    readonly headroom: number;
    readonly prefixHash: string;
}
export interface ContextAdmission {
    readonly admissionId: string;
    readonly missionId: MissionId;
    readonly runId: AgentRunId;
    readonly generation: number;
    readonly ordinal: number;
    readonly projectId: string;
    readonly decisionHash: string;
    readonly admittedHash: string;
    readonly evidenceHashes: readonly string[];
    readonly sourceSet: readonly SourceRevision[];
    readonly sourceSetHash: string;
    readonly route: ContextRoute;
    readonly committedInputHash: string;
    readonly state: 'COMMITTED';
    readonly idempotencyKey: string;
}
export declare function contextDecision(v: ContextDecision, e: {
    missionId: MissionId;
    runId: AgentRunId;
    projectId: string;
    policyHash: string;
    skillHash: string;
    aiwsHash: string;
    sourceAllowlist: readonly string[];
    toolAllowlist: readonly string[];
    ceiling: BudgetVector;
}): Readonly<ContextDecision>;
export declare function searchPackage(v: SearchDelegationPackage, e: {
    decision: ContextDecision;
    now: number;
    ceiling: BudgetVector;
}): Readonly<SearchDelegationPackage>;
export declare function directManifest(v: DirectRetrievalManifest, e: {
    decision: ContextDecision;
    liveSources: readonly SourceRevision[];
    queries: readonly string[];
    tools: readonly string[];
    now: number;
    ceiling: BudgetVector;
}): Readonly<DirectRetrievalManifest>;
export declare function contextCapsule(v: ContextCapsule, e: {
    decision: ContextDecision;
    packageHash: string;
    liveSources: readonly SourceRevision[];
    redactionProfile: string;
    now: number;
    ceiling: BudgetVector;
}): Readonly<ContextCapsule>;
export declare function forkEvaluation(v: ForkEvaluation, e: {
    missionId: MissionId;
    runId: AgentRunId;
    projectId: string;
    authorizationHash: string;
    provider: string;
    model: string;
}): Readonly<ForkEvaluation>;
export declare function contextAdmission(v: ContextAdmission, e: {
    missionId: MissionId;
    runId: AgentRunId;
    projectId: string;
    decisionHash: string;
}, current: readonly SourceRevision[], seen: ReadonlyMap<string, ContextAdmission>): Readonly<ContextAdmission>;
//# sourceMappingURL=context.d.ts.map