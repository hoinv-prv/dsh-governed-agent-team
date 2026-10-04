declare const identityBrand: unique symbol;
type Identity<Kind extends string> = string & {
    readonly [identityBrand]: Kind;
};
export type AgentId = Identity<'AgentId'>;
export type MissionId = Identity<'MissionId'>;
export type PlanId = Identity<'PlanId'>;
export type WorkItemId = Identity<'WorkItemId'>;
export type AgentRunId = Identity<'AgentRunId'>;
export type SessionId = Identity<'SessionId'>;
export type WorkspaceId = Identity<'WorkspaceId'>;
export declare const agentId: (value: string) => AgentId;
export declare const missionId: (value: string) => MissionId;
export declare const planId: (value: string) => PlanId;
export declare const workItemId: (value: string) => WorkItemId;
export declare const agentRunId: (value: string) => AgentRunId;
export declare const sessionId: (value: string) => SessionId;
export declare const workspaceId: (value: string) => WorkspaceId;
export {};
//# sourceMappingURL=identity.d.ts.map