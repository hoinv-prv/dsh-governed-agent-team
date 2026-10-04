import type { AgentRunId, MissionId, SessionId } from '../identity.js';
export type JsonValue = null | boolean | string | number | readonly JsonValue[] | {
    readonly [k: string]: JsonValue;
};
export declare function canonicalJson(v: unknown): string;
export declare function canonicalHash(v: unknown): string;
export declare function utf8Hash(v: string): string;
export interface RuntimeScope {
    readonly missionId: MissionId;
    readonly projectId: string;
}
export interface WakeRef extends RuntimeScope {
    readonly kind: 'wake';
    readonly wakeId: string;
    readonly generation: number;
    readonly triggerKey: string;
}
export interface RunSession {
    readonly sessionId: SessionId;
    readonly provider: string;
    readonly model: string;
    readonly ordinal: number;
}
export interface RunRef extends RuntimeScope {
    readonly kind: 'run';
    readonly runId: AgentRunId;
    readonly wakeId: string;
    readonly generation: number;
    readonly sessions: readonly RunSession[];
}
export interface ControlRef extends RuntimeScope {
    readonly kind: 'control';
    readonly controlId: string;
    readonly revision: number;
    readonly action: 'PAUSE' | 'RESUME' | 'CANCEL';
    readonly targetWakeId?: string;
    readonly targetRunId?: AgentRunId;
}
export interface OperationRef extends RuntimeScope {
    readonly kind: 'operation';
    readonly operationId: string;
    readonly runId: AgentRunId;
    readonly wakeGeneration: number;
    readonly ordinal: number;
    readonly effectKind: string;
    readonly intent: JsonValue;
    readonly intentHash: string;
    readonly idempotencyKey: string;
}
export interface ProjectionRef extends RuntimeScope {
    readonly kind: 'projection';
    readonly projectionId: string;
    readonly aggregateRevision: number;
    readonly sourceRevision: number;
    readonly wakeId?: string;
    readonly runId?: AgentRunId;
}
export type RuntimeRef = WakeRef | RunRef | ControlRef | OperationRef | ProjectionRef;
export declare function runtimeRefs(scope: RuntimeScope, values: readonly RuntimeRef[]): readonly Readonly<RuntimeRef>[];
export declare function idempotencyKey(missionId: MissionId, runId: AgentRunId, wakeGeneration: number, ordinal: number, effectKind: string, intent: JsonValue): string;
//# sourceMappingURL=runtime.d.ts.map