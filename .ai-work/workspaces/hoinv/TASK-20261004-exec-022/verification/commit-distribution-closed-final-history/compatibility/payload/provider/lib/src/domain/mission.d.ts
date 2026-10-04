import type { AgentId, AgentRunId, MissionId, PlanId, SessionId } from '../identity.js';
export declare const MISSION_STATES: readonly ["ASSIGNED", "TRIAGING", "READY", "RUNNING", "WAITING_TIMER", "WAITING_DEPENDENCY", "WAITING_SPECIALIST", "WAITING_HUMAN", "RETRY_SCHEDULED", "VERIFYING", "REWORK", "HANDOFF_READY", "PAUSED", "BLOCKED", "COMPLETED", "FAILED", "CANCELLED", "EXPIRED"];
export type MissionState = typeof MISSION_STATES[number];
export declare const TERMINAL_STATES: readonly MissionState[];
export interface TransitionRule {
    readonly from: MissionState | null;
    readonly command: string;
    readonly to: MissionState;
}
export declare const TRANSITION_MATRIX: readonly TransitionRule[];
export interface SourceRevision {
    readonly ref: string;
    readonly revision: string;
    readonly sha256: string;
}
export interface MissionContract {
    readonly missionId: MissionId;
    readonly agentId: AgentId;
    readonly revision: number;
    readonly objective: string;
    readonly projectId: string;
    readonly systemSelectors: readonly string[];
    readonly sourceSet: readonly SourceRevision[];
}
export interface MissionSnapshot {
    readonly contract: MissionContract;
    readonly state: MissionState;
    readonly revision: number;
    readonly activePlanId?: PlanId;
    readonly nextAction: string;
}
export interface MissionEvent {
    readonly missionId: MissionId;
    readonly projectId: string;
    readonly seq: number;
    readonly type: string;
    readonly priorRevision: number;
    readonly aggregateRevision: number;
    readonly sourceSetHash: string;
    readonly occurredAt: number;
}
export interface TransitionAudit {
    readonly actor: AgentId;
    readonly reason: string;
    readonly sourceEventId: string;
    readonly correlationId: string;
    readonly dedupeKey: string;
    readonly runId?: AgentRunId;
    readonly sessionId?: SessionId;
    readonly evidenceHashes: readonly string[];
}
export interface TransitionPreconditions {
    readonly claimedGeneration: boolean;
    readonly purpose: 'triage' | 'execute' | 'verify' | 'control';
    readonly grantValid: boolean;
    readonly budgetValid: boolean;
    readonly artifactsDurable: boolean;
    readonly gatesPassed: boolean;
    readonly humanAuthorized: boolean;
    readonly ownerAuthorized: boolean;
    readonly runActive: boolean;
    readonly sessionSettled: boolean;
}
export declare function assertCommandPreconditions(command: string, to: MissionState, p: TransitionPreconditions): void;
export declare function sourceSet(v: readonly SourceRevision[]): readonly SourceRevision[];
export declare function missionContract(v: MissionContract, e?: {
    missionId: MissionId;
    projectId: string;
}): Readonly<MissionContract>;
export declare function missionEvent(v: MissionEvent, e: {
    missionId: MissionId;
    projectId: string;
    currentRevision: number;
}): Readonly<MissionEvent>;
export declare function assertTransition(from: MissionState | null, command: string, to: MissionState, expectedRevision: number, actualRevision: number, audit: TransitionAudit, human?: boolean): void;
//# sourceMappingURL=mission.d.ts.map