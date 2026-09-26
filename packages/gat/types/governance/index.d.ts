export interface Decision { readonly disposition: string; readonly reason_code: string | null; readonly [key: string]: unknown }
export interface ExecutionIdentity { readonly tenantId: string; readonly principalId: string; readonly projectScopeId: string; readonly taskId: string; readonly aipId: string; readonly workspaceId: string; readonly bindingHash?: string }
export function createProjectScope(input: { tenantId: string; projectId: string; accountRegistryId: string; workspaceRoot: string }): Readonly<Record<string, string>>;
export function deriveAgentDeskId(input: { tenantId: string; principalId: string; projectScopeId: string; agentId: string }): string;
export function createExecutionIdentity(input: ExecutionIdentity): Readonly<Required<ExecutionIdentity>>;
export function checkExecutionIdentity(current: ExecutionIdentity, requested: ExecutionIdentity): Decision;
export function evaluateReadiness(input: { oracle: { source: 'package_readiness_oracle'; outcome: 'not_ready' | 'lite_ready' | 'execution_ready'; taskClass: 'trivial' | 'non_trivial'; evidenceHash: string; evidenceRevision: number; applicabilityHash: string } }): Decision;
export function authorizeTeamPlan(input: { plan: { revision: number; phase: string; planHash: string }; approval?: { approvedRevision: number; approvedPlanHash: string; snapshotHash: string } | null }): Decision;
export function authorizeMissionMapping(input: { mapping?: { revision: number; gatMissionId: string; nativeMissionId: string; nativeMissionRevision: number } | null; nativeMission?: { id: string; revision: number; title: string; objective: string; status: string; plan: unknown } | null; nativeApproval?: { approvedRevision: number } | null }): Decision;
