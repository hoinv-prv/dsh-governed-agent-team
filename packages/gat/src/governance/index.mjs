import { createHash } from 'node:crypto';

const ID = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/u;
const HASH = /^[a-f0-9]{64}$/u;
const requiredId = (name, value) => {
  if (typeof value !== 'string' || !ID.test(value)) throw new TypeError(`${name} is invalid`);
  return value;
};
const requiredHash = (name, value) => {
  if (typeof value !== 'string' || !HASH.test(value)) throw new TypeError(`${name} is invalid`);
  return value;
};
const requiredRevision = (name, value) => {
  if (!Number.isSafeInteger(value) || value < 0) throw new TypeError(`${name} is invalid`);
  return value;
};
function normalize(value) {
  if (value === null || ['string', 'boolean'].includes(typeof value)) return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (Array.isArray(value)) return value.map(normalize);
  if (value && Object.getPrototypeOf(value) === Object.prototype) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, normalize(value[key])]));
  }
  throw new TypeError('Only JSON values are accepted');
}
function deepFreeze(value) {
  if (value && typeof value === 'object') {
    for (const child of Object.values(value)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}
const owned = (value) => deepFreeze(normalize(value));
const canonical = (value) => JSON.stringify(normalize(value));
const bindingHash = (kind, value) => createHash('sha256').update(`${kind}\0${canonical(value)}`).digest('hex');
const deny = (reason_code, evidence = {}) => owned({ disposition: 'deny', reason_code, ...evidence });
const allow = (evidence = {}) => owned({ disposition: 'allow', reason_code: null, ...evidence });

export function createProjectScope({ tenantId, projectId, accountRegistryId, workspaceRoot }) {
  if (typeof workspaceRoot !== 'string' || !workspaceRoot.startsWith('/')) throw new TypeError('workspaceRoot must be absolute');
  const core = { tenantId: requiredId('tenantId', tenantId), projectId: requiredId('projectId', projectId), accountRegistryId: requiredId('accountRegistryId', accountRegistryId), workspaceRoot };
  return owned({ ...core, projectScopeId: `project-scope:${bindingHash('ProjectScope', core)}`, bindingHash: bindingHash('ProjectScope', core) });
}

export function deriveAgentDeskId({ tenantId, principalId, projectScopeId, agentId }) {
  const key = { tenantId: requiredId('tenantId', tenantId), principalId: requiredId('principalId', principalId), projectScopeId: requiredId('projectScopeId', projectScopeId), agentId: requiredId('agentId', agentId) };
  return `desk:${bindingHash('AgentDesk', key)}`;
}

export function createExecutionIdentity({ tenantId, principalId, projectScopeId, taskId, aipId, workspaceId }) {
  const core = { tenantId: requiredId('tenantId', tenantId), principalId: requiredId('principalId', principalId), projectScopeId: requiredId('projectScopeId', projectScopeId), taskId: requiredId('taskId', taskId), aipId: requiredId('aipId', aipId), workspaceId: requiredId('workspaceId', workspaceId) };
  return owned({ ...core, bindingHash: bindingHash('ExecutionIdentity', core) });
}

export function checkExecutionIdentity(currentInput, requestedInput) {
  let current;
  let requested;
  try {
    current = createExecutionIdentity(currentInput);
    requested = createExecutionIdentity(requestedInput);
  } catch {
    return deny('BINDING_INVALID');
  }
  for (const key of ['tenantId', 'principalId', 'projectScopeId', 'taskId', 'aipId', 'workspaceId']) {
    if (current[key] !== requested[key]) return deny('TASK_EXECUTION_BINDING_STALE', { currentBindingHash: current.bindingHash, requestedBindingHash: requested.bindingHash });
  }
  return allow({ identity: current, bindingHash: current.bindingHash });
}

export function evaluateReadiness({ oracle }) {
  if (!oracle || oracle.source !== 'package_readiness_oracle') return deny('BINDING_INVALID');
  let snapshot;
  try {
    snapshot = owned({ source: oracle.source, outcome: oracle.outcome, taskClass: oracle.taskClass, evidenceHash: requiredHash('evidenceHash', oracle.evidenceHash), evidenceRevision: requiredRevision('evidenceRevision', oracle.evidenceRevision), applicabilityHash: requiredHash('applicabilityHash', oracle.applicabilityHash) });
  } catch {
    return deny('BINDING_INVALID');
  }
  if (!['not_ready', 'lite_ready', 'execution_ready'].includes(snapshot.outcome) || !['trivial', 'non_trivial'].includes(snapshot.taskClass)) return deny('BINDING_INVALID');
  const oracleBindingHash = bindingHash('ReadinessOracle', snapshot);
  if (snapshot.outcome === 'not_ready') return deny('WORKING_AIP_NOT_EXECUTION_READY', { oracleBindingHash });
  if (snapshot.taskClass === 'non_trivial' && snapshot.outcome !== 'execution_ready') return deny('WORKING_AIP_LITE_INAPPLICABLE', { oracleBindingHash });
  return allow({ oracle: snapshot, oracleBindingHash });
}

export function authorizeTeamPlan({ plan, approval }) {
  if (!plan || plan.phase !== 'approved') return deny('TEAM_PLAN_APPROVAL_MISSING');
  let current;
  try {
    current = owned({ revision: requiredRevision('plan.revision', plan.revision), phase: plan.phase, planHash: requiredHash('plan.planHash', plan.planHash) });
  } catch {
    return deny('BINDING_INVALID');
  }
  if (!approval) return deny('TEAM_PLAN_APPROVAL_MISSING', { planBindingHash: bindingHash('TeamPlan', current) });
  let accepted;
  try {
    accepted = owned({ approvedRevision: requiredRevision('approval.approvedRevision', approval.approvedRevision), approvedPlanHash: requiredHash('approval.approvedPlanHash', approval.approvedPlanHash), snapshotHash: requiredHash('approval.snapshotHash', approval.snapshotHash) });
  } catch {
    return deny('BINDING_INVALID');
  }
  const planBindingHash = bindingHash('TeamPlan', current);
  const approvalBindingHash = bindingHash('TeamPlanApproval', accepted);
  if (accepted.approvedRevision !== current.revision || accepted.approvedPlanHash !== current.planHash) return deny('TEAM_PLAN_APPROVAL_STALE', { planBindingHash, approvalBindingHash });
  return allow({ plan: current, approval: accepted, planBindingHash, approvalBindingHash });
}

export function authorizeMissionMapping({ mapping, nativeMission, nativeApproval }) {
  if (!mapping) return owned({ disposition: 'not_applicable', reason_code: null, nativeMissionGateClaimed: false });
  let boundMapping;
  try {
    boundMapping = owned({ revision: requiredRevision('mapping.revision', mapping.revision), gatMissionId: requiredId('mapping.gatMissionId', mapping.gatMissionId), nativeMissionId: requiredId('mapping.nativeMissionId', mapping.nativeMissionId), nativeMissionRevision: requiredRevision('mapping.nativeMissionRevision', mapping.nativeMissionRevision) });
  } catch {
    return deny('BINDING_INVALID');
  }
  const mappingBindingHash = bindingHash('MissionMapping', boundMapping);
  let mission;
  let approval;
  try {
    if (!nativeMission || !nativeApproval) return deny('NATIVE_MISSION_APPROVAL_STALE', { mappingBindingHash });
    mission = owned({ id: requiredId('nativeMission.id', nativeMission.id), revision: requiredRevision('nativeMission.revision', nativeMission.revision), title: nativeMission.title, objective: nativeMission.objective, status: nativeMission.status, plan: nativeMission.plan });
    approval = owned({ approvedRevision: requiredRevision('nativeApproval.approvedRevision', nativeApproval.approvedRevision) });
  } catch {
    return deny('NATIVE_MISSION_APPROVAL_STALE', { mappingBindingHash });
  }
  const nativeMissionSnapshotHash = bindingHash('NativeMissionSnapshot', mission);
  const nativeApprovalSnapshotHash = bindingHash('NativeMissionApprovalSnapshot', approval);
  if (mission.id !== boundMapping.nativeMissionId || mission.revision !== boundMapping.nativeMissionRevision || mission.status !== 'active' || approval.approvedRevision !== mission.revision) {
    return deny('NATIVE_MISSION_APPROVAL_STALE', { mappingBindingHash, nativeMissionSnapshotHash, nativeApprovalSnapshotHash });
  }
  return allow({ mapping: boundMapping, mappingBindingHash, nativeMission: mission, nativeMissionSnapshotHash, nativeApproval: approval, nativeApprovalSnapshotHash, nativeMissionGateClaimed: true, dshAdmissionEnforcementClaimed: false });
}
