import type { AgentId, MissionId, PlanId, WorkItemId } from '../identity.js';
export declare const PLANNING_MODES: readonly ["NO_PLAN", "CHECKLIST", "WBS"];
export type PlanningMode = typeof PLANNING_MODES[number];
export interface PlanningFeatures {
    readonly workItems: number;
    readonly dependencyDepth: number;
    readonly affectedDomains: number;
    readonly risk: number;
    readonly uncertainty: number;
    readonly itemCount: number;
    readonly crossProject: boolean;
    readonly externalOrIrreversible: boolean;
    readonly protectedData: boolean;
    readonly securityPrivacyMigrationRelease: boolean;
    readonly estimatedMinutes: number;
    readonly modelCalls: number;
    readonly workerCount: number;
    readonly independentOrHumanGate: boolean;
}
export interface PlanningDecision {
    readonly missionId: MissionId;
    readonly revision: number;
    readonly priorRevision: number;
    readonly policyVersion: 'planning-policy-v1';
    readonly features: PlanningFeatures;
    readonly score: number;
    readonly thresholds: Readonly<{
        noPlanMax: 2;
        checklistMax: 6;
    }>;
    readonly forcedWbsReasons: readonly string[];
    readonly mode: PlanningMode;
    readonly reason: string;
    readonly nextAction: string;
    readonly decidedBy: AgentId;
    readonly decidedAt: number;
    readonly decisionHash: string;
    readonly claimedWakeId?: string;
    readonly emittedWakeId?: string;
}
export interface WorkItem {
    readonly id: WorkItemId;
    readonly missionId: MissionId;
    readonly planId: PlanId;
    readonly status: 'PENDING' | 'READY' | 'RUNNING' | 'DONE' | 'BLOCKED';
    readonly dependencies: readonly WorkItemId[];
    readonly attempt: number;
    readonly maxAttempts: number;
}
export declare function evaluatePlanning(f: PlanningFeatures): {
    score: number;
    forcedWbsReasons: string[];
    mode: PlanningMode;
};
export declare function planningDecision(v: PlanningDecision, e: {
    missionId: MissionId;
    currentRevision: number;
}): Readonly<PlanningDecision>;
export declare function workItems(v: readonly WorkItem[], e: {
    missionId: MissionId;
    planId: PlanId;
}): readonly Readonly<WorkItem>[];
//# sourceMappingURL=planning.d.ts.map