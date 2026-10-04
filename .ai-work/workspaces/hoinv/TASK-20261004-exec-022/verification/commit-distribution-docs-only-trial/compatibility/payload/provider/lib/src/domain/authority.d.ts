import type { AgentId, AgentRunId, MissionId } from '../identity.js';
export interface BudgetVector {
    readonly searches: number;
    readonly sources: number;
    readonly toolCalls: number;
    readonly inputTokens: number;
    readonly outputTokens: number;
    readonly costUsd: number;
}
export interface BudgetAccount {
    readonly reserved: BudgetVector;
    readonly consumed: BudgetVector;
}
export interface BudgetLedgerEntry {
    readonly entryId: string;
    readonly missionId: MissionId;
    readonly runId?: AgentRunId;
    readonly generation?: number;
    readonly category: keyof BudgetVector;
    readonly eventId: string;
    readonly sequence: number;
    readonly reservedDelta: number;
    readonly consumedDelta: number;
    readonly returnedDelta: number;
}
export interface BudgetLedgerSummary {
    readonly reserved: BudgetVector;
    readonly consumed: BudgetVector;
    readonly returned: BudgetVector;
    readonly activeReserved: BudgetVector;
}
export interface DelegationGrant {
    readonly grantId: string;
    readonly missionId: MissionId;
    readonly contractRevision: number;
    readonly controlRevision: number;
    readonly revision: number;
    readonly revocationRevision: number;
    readonly issuer: AgentId;
    readonly subject: AgentId;
    readonly projectId: string;
    readonly role: string;
    readonly templateVersion: string;
    readonly capability: string;
    readonly purpose: string;
    readonly templateHash: string;
    readonly contributionSetHash: string;
    readonly readScopes: readonly string[];
    readonly writeScopes: readonly string[];
    readonly effects: readonly string[];
    readonly commands: readonly string[];
    readonly provider: string;
    readonly model: string;
    readonly inputTokenCeiling: number;
    readonly outputTokenCeiling: number;
    readonly contextCeiling: number;
    readonly toolCallCeiling: number;
    readonly timeCeilingMs: number;
    readonly costCeilingUsd: number;
    readonly mayContribute: boolean;
    readonly budget: BudgetVector;
    readonly issuedAt: number;
    readonly expiresAt: number;
    readonly revokedAt?: number;
}
export interface GrantCeiling {
    readonly missionId: MissionId;
    readonly contractRevision: number;
    readonly controlRevision: number;
    readonly issuer: AgentId;
    readonly projectId: string;
    readonly templateHash: string;
    readonly readScopes: readonly string[];
    readonly writeScopes: readonly string[];
    readonly effects: readonly string[];
    readonly commands: readonly string[];
    readonly providers: readonly string[];
    readonly models: readonly string[];
    readonly inputTokenCeiling: number;
    readonly outputTokenCeiling: number;
    readonly contextCeiling: number;
    readonly toolCallCeiling: number;
    readonly timeCeilingMs: number;
    readonly costCeilingUsd: number;
    readonly budget: BudgetVector;
    readonly priorRevocationRevision: number;
}
export interface AiwsAuthorization {
    readonly missionId: MissionId;
    readonly projectId: string;
    readonly order: readonly ['rules', 'wiki', 'project', 'memory'];
    readonly systemSelector: string;
    readonly authorityRef?: string;
    readonly localAllowed: boolean;
    readonly rawAllowed: boolean;
    readonly allowedPatterns: readonly string[];
    readonly issuedAt: number;
    readonly expiresAt: number;
}
export declare const BUDGET_DIMENSIONS: readonly (keyof BudgetVector)[];
export declare function budget(v: BudgetVector, limit?: BudgetVector): Readonly<BudgetVector>;
export declare function budgetAccount(v: BudgetAccount, limit: BudgetVector, prior?: BudgetAccount): Readonly<BudgetAccount>;
export declare function budgetLedger(entries: readonly BudgetLedgerEntry[], e: {
    missionId: MissionId;
    ceiling: BudgetVector;
}): Readonly<BudgetLedgerSummary>;
export declare function delegationGrant(v: DelegationGrant, c: GrantCeiling, now: number): Readonly<DelegationGrant>;
export declare function aiwsAuthorization(v: AiwsAuthorization, e: {
    missionId: MissionId;
    projectId: string;
    systemSelectors: readonly string[];
    scopePatterns: readonly string[];
    now: number;
}): Readonly<AiwsAuthorization>;
//# sourceMappingURL=authority.d.ts.map