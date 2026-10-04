declare const identityBrand: unique symbol

type Identity<Kind extends string> = string & { readonly [identityBrand]: Kind }

export type AgentId = Identity<'AgentId'>
export type MissionId = Identity<'MissionId'>
export type PlanId = Identity<'PlanId'>
export type WorkItemId = Identity<'WorkItemId'>
export type AgentRunId = Identity<'AgentRunId'>
export type SessionId = Identity<'SessionId'>
export type WorkspaceId = Identity<'WorkspaceId'>

function identity<Kind extends string>(kind: Kind, value: string): Identity<Kind> {
  if (value.length === 0 || value.trim() !== value) throw new TypeError(`DURABLE_AGENT_INVALID_ID:${kind}`)
  return value as Identity<Kind>
}

export const agentId = (value: string): AgentId => identity('AgentId', value)
export const missionId = (value: string): MissionId => identity('MissionId', value)
export const planId = (value: string): PlanId => identity('PlanId', value)
export const workItemId = (value: string): WorkItemId => identity('WorkItemId', value)
export const agentRunId = (value: string): AgentRunId => identity('AgentRunId', value)
export const sessionId = (value: string): SessionId => identity('SessionId', value)
export const workspaceId = (value: string): WorkspaceId => identity('WorkspaceId', value)

// `tsc` must consume every @ts-expect-error below, proving both directions of
// each forbidden identity assignment remain rejected by the public types.
function assertIdentitySeparation(
  agent: AgentId,
  mission: MissionId,
  plan: PlanId,
  workItem: WorkItemId,
  run: AgentRunId,
  session: SessionId,
  workspace: WorkspaceId,
): void {
  // @ts-expect-error AgentId must not accept MissionId.
  const agentFromMission: AgentId = mission
  // @ts-expect-error MissionId must not accept AgentId.
  const missionFromAgent: MissionId = agent
  // @ts-expect-error PlanId must not accept WorkItemId.
  const planFromWorkItem: PlanId = workItem
  // @ts-expect-error WorkItemId must not accept PlanId.
  const workItemFromPlan: WorkItemId = plan
  // @ts-expect-error AgentRunId must not accept SessionId.
  const runFromSession: AgentRunId = session
  // @ts-expect-error SessionId must not accept AgentRunId.
  const sessionFromRun: SessionId = run
  // @ts-expect-error WorkspaceId must not accept AgentId.
  const workspaceFromAgent: WorkspaceId = agent
  // @ts-expect-error AgentId must not accept WorkspaceId.
  const agentFromWorkspace: AgentId = workspace
  // @ts-expect-error WorkspaceId must not accept MissionId.
  const workspaceFromMission: WorkspaceId = mission
  // @ts-expect-error MissionId must not accept WorkspaceId.
  const missionFromWorkspace: MissionId = workspace
  // @ts-expect-error WorkspaceId must not accept PlanId.
  const workspaceFromPlan: WorkspaceId = plan
  // @ts-expect-error PlanId must not accept WorkspaceId.
  const planFromWorkspace: PlanId = workspace
  // @ts-expect-error WorkspaceId must not accept WorkItemId.
  const workspaceFromWorkItem: WorkspaceId = workItem
  // @ts-expect-error WorkItemId must not accept WorkspaceId.
  const workItemFromWorkspace: WorkItemId = workspace
  // @ts-expect-error WorkspaceId must not accept AgentRunId.
  const workspaceFromRun: WorkspaceId = run
  // @ts-expect-error AgentRunId must not accept WorkspaceId.
  const runFromWorkspace: AgentRunId = workspace
  // @ts-expect-error WorkspaceId must not accept SessionId.
  const workspaceFromSession: WorkspaceId = session
  // @ts-expect-error SessionId must not accept WorkspaceId.
  const sessionFromWorkspace: SessionId = workspace
  void [agentFromMission, missionFromAgent, planFromWorkItem, workItemFromPlan, runFromSession, sessionFromRun, workspaceFromAgent, agentFromWorkspace, workspaceFromMission, missionFromWorkspace, workspaceFromPlan, planFromWorkspace, workspaceFromWorkItem, workItemFromWorkspace, workspaceFromRun, runFromWorkspace, workspaceFromSession, sessionFromWorkspace]
}

void assertIdentitySeparation
