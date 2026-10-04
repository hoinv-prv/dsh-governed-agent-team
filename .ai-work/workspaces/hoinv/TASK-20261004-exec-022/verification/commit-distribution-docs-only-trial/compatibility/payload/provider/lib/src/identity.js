function identity(kind, value) {
    if (value.length === 0 || value.trim() !== value)
        throw new TypeError(`DURABLE_AGENT_INVALID_ID:${kind}`);
    return value;
}
export const agentId = (value) => identity('AgentId', value);
export const missionId = (value) => identity('MissionId', value);
export const planId = (value) => identity('PlanId', value);
export const workItemId = (value) => identity('WorkItemId', value);
export const agentRunId = (value) => identity('AgentRunId', value);
export const sessionId = (value) => identity('SessionId', value);
export const workspaceId = (value) => identity('WorkspaceId', value);
// `tsc` must consume every @ts-expect-error below, proving both directions of
// each forbidden identity assignment remain rejected by the public types.
function assertIdentitySeparation(agent, mission, plan, workItem, run, session, workspace) {
    // @ts-expect-error AgentId must not accept MissionId.
    const agentFromMission = mission;
    // @ts-expect-error MissionId must not accept AgentId.
    const missionFromAgent = agent;
    // @ts-expect-error PlanId must not accept WorkItemId.
    const planFromWorkItem = workItem;
    // @ts-expect-error WorkItemId must not accept PlanId.
    const workItemFromPlan = plan;
    // @ts-expect-error AgentRunId must not accept SessionId.
    const runFromSession = session;
    // @ts-expect-error SessionId must not accept AgentRunId.
    const sessionFromRun = run;
    // @ts-expect-error WorkspaceId must not accept AgentId.
    const workspaceFromAgent = agent;
    // @ts-expect-error AgentId must not accept WorkspaceId.
    const agentFromWorkspace = workspace;
    // @ts-expect-error WorkspaceId must not accept MissionId.
    const workspaceFromMission = mission;
    // @ts-expect-error MissionId must not accept WorkspaceId.
    const missionFromWorkspace = workspace;
    // @ts-expect-error WorkspaceId must not accept PlanId.
    const workspaceFromPlan = plan;
    // @ts-expect-error PlanId must not accept WorkspaceId.
    const planFromWorkspace = workspace;
    // @ts-expect-error WorkspaceId must not accept WorkItemId.
    const workspaceFromWorkItem = workItem;
    // @ts-expect-error WorkItemId must not accept WorkspaceId.
    const workItemFromWorkspace = workspace;
    // @ts-expect-error WorkspaceId must not accept AgentRunId.
    const workspaceFromRun = run;
    // @ts-expect-error AgentRunId must not accept WorkspaceId.
    const runFromWorkspace = workspace;
    // @ts-expect-error WorkspaceId must not accept SessionId.
    const workspaceFromSession = session;
    // @ts-expect-error SessionId must not accept WorkspaceId.
    const sessionFromWorkspace = workspace;
    void [agentFromMission, missionFromAgent, planFromWorkItem, workItemFromPlan, runFromSession, sessionFromRun, workspaceFromAgent, agentFromWorkspace, workspaceFromMission, missionFromWorkspace, workspaceFromPlan, planFromWorkspace, workspaceFromWorkItem, workItemFromWorkspace, workspaceFromRun, runFromWorkspace, workspaceFromSession, sessionFromWorkspace];
}
void assertIdentitySeparation;
//# sourceMappingURL=identity.js.map