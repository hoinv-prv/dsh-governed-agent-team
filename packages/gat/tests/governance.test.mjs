import assert from 'node:assert/strict';
import test from 'node:test';
import { authorizeMissionMapping, authorizeTeamPlan, checkExecutionIdentity, createExecutionIdentity, createProjectScope, deriveAgentDeskId, evaluateReadiness } from '../src/governance/index.mjs';

const h = (digit) => digit.repeat(64);

test('ProjectScope and four-part AgentDesk key are immutable and project-bound', () => {
  const input = { tenantId: 't1', projectId: 'p1', accountRegistryId: 'r1', workspaceRoot: '/safe/root' };
  const scope = createProjectScope(input);
  input.projectId = 'mutated';
  assert.equal(scope.projectId, 'p1');
  assert(Object.isFrozen(scope));
  assert.match(scope.bindingHash, /^[a-f0-9]{64}$/);
  const base = { tenantId: 't1', principalId: 'alice', agentId: 'agent' };
  assert.notEqual(deriveAgentDeskId({ ...base, projectScopeId: 'scope-a' }), deriveAgentDeskId({ ...base, projectScopeId: 'scope-b' }));
  assert.notEqual(deriveAgentDeskId({ ...base, projectScopeId: 'scope-a' }), deriveAgentDeskId({ ...base, principalId: 'bob', projectScopeId: 'scope-a' }));
});

test('execution identity owns and hashes tenant principal task AIP Workspace plus ProjectScope', () => {
  const input = { tenantId: 't', principalId: 'alice', projectScopeId: 'p', taskId: 'task', aipId: 'aip', workspaceId: 'ws' };
  const current = createExecutionIdentity(input);
  input.principalId = 'mallory';
  assert.equal(current.principalId, 'alice');
  assert(Object.isFrozen(current));
  assert.equal(checkExecutionIdentity(current, current).disposition, 'allow');
  for (const key of ['tenantId', 'principalId', 'projectScopeId', 'taskId', 'aipId', 'workspaceId']) {
    assert.equal(checkExecutionIdentity(current, { ...current, [key]: `${current[key]}-stale` }).reason_code, 'TASK_EXECUTION_BINDING_STALE');
  }
  assert.equal(checkExecutionIdentity(current, { ...current, principalId: undefined }).reason_code, 'BINDING_INVALID');
});

test('readiness consumes immutable package oracle evidence without reclassification', () => {
  const oracle = { source: 'package_readiness_oracle', outcome: 'execution_ready', taskClass: 'non_trivial', evidenceHash: h('a'), evidenceRevision: 3, applicabilityHash: h('b') };
  const decision = evaluateReadiness({ oracle });
  oracle.outcome = 'not_ready';
  assert.equal(decision.disposition, 'allow');
  assert.equal(decision.oracle.outcome, 'execution_ready');
  assert(Object.isFrozen(decision.oracle));
  assert.equal(evaluateReadiness({ oracle: { ...oracle, outcome: 'not_ready' } }).reason_code, 'WORKING_AIP_NOT_EXECUTION_READY');
  assert.equal(evaluateReadiness({ oracle: { ...oracle, outcome: 'lite_ready', taskClass: 'non_trivial' } }).reason_code, 'WORKING_AIP_LITE_INAPPLICABLE');
  assert.equal(evaluateReadiness({ oracle: { ...oracle, outcome: 'lite_ready', taskClass: 'trivial' } }).disposition, 'allow');
  assert.equal(evaluateReadiness({ oracle: { ...oracle, outcome: 'execution_ready', evidenceHash: 'stale' } }).reason_code, 'BINDING_INVALID');
});

test('Team plan requires approved phase, numeric exact revision, and hashed snapshot', () => {
  const plan = { revision: 2, phase: 'approved', planHash: h('c') };
  const approval = { approvedRevision: 2, approvedPlanHash: h('c'), snapshotHash: h('d') };
  assert.equal(authorizeTeamPlan({ plan: { ...plan, phase: 'draft' }, approval }).reason_code, 'TEAM_PLAN_APPROVAL_MISSING');
  assert.equal(authorizeTeamPlan({ plan, approval: null }).reason_code, 'TEAM_PLAN_APPROVAL_MISSING');
  assert.equal(authorizeTeamPlan({ plan: { ...plan, revision: '2' }, approval }).reason_code, 'BINDING_INVALID');
  assert.equal(authorizeTeamPlan({ plan, approval: { ...approval, approvedRevision: 1 } }).reason_code, 'TEAM_PLAN_APPROVAL_STALE');
  assert.equal(authorizeTeamPlan({ plan, approval: { ...approval, snapshotHash: 'bad' } }).reason_code, 'BINDING_INVALID');
  const allowed = authorizeTeamPlan({ plan, approval });
  plan.planHash = h('e');
  assert.equal(allowed.disposition, 'allow');
  assert(Object.isFrozen(allowed.plan));
  assert.match(allowed.approvalBindingHash, /^[a-f0-9]{64}$/);
});

test('Mission mapping normalizes native snapshot and exact revision approval without admission overclaim', () => {
  const unmapped = authorizeMissionMapping({ mapping: null });
  assert.equal(unmapped.nativeMissionGateClaimed, false);
  assert.equal(unmapped.disposition, 'not_applicable');
  const mapping = { revision: 1, gatMissionId: 'gat-m', nativeMissionId: 'native-m', nativeMissionRevision: 4 };
  const nativeMission = { id: 'native-m', revision: 4, title: 'Mission', objective: 'Objective', status: 'active', plan: { tasks: ['one'] } };
  const approval = { approvedRevision: 4 };
  for (const invalid of [
    { nativeMission, nativeApproval: null },
    { nativeMission: { ...nativeMission, id: 'other' }, nativeApproval: approval },
    { nativeMission: { ...nativeMission, revision: 5 }, nativeApproval: approval },
    { nativeMission: { ...nativeMission, status: 'completed' }, nativeApproval: approval },
    { nativeMission, nativeApproval: { approvedRevision: 3 } },
  ]) assert.equal(authorizeMissionMapping({ mapping, ...invalid }).reason_code, 'NATIVE_MISSION_APPROVAL_STALE');
  const allowed = authorizeMissionMapping({ mapping, nativeMission, nativeApproval: approval });
  mapping.nativeMissionId = 'mutated';
  nativeMission.plan.tasks.push('mutated');
  approval.approvedRevision = 99;
  assert.equal(allowed.disposition, 'allow');
  assert.equal(allowed.mapping.nativeMissionId, 'native-m');
  assert.deepEqual(allowed.nativeMission.plan, { tasks: ['one'] });
  assert.equal(allowed.nativeApproval.approvedRevision, 4);
  assert(Object.isFrozen(allowed.mapping));
  assert(Object.isFrozen(allowed.nativeMission.plan));
  assert.match(allowed.mappingBindingHash, /^[a-f0-9]{64}$/);
  assert.match(allowed.nativeMissionSnapshotHash, /^[a-f0-9]{64}$/);
  assert.match(allowed.nativeApprovalSnapshotHash, /^[a-f0-9]{64}$/);
  assert.equal(allowed.dshAdmissionEnforcementClaimed, false);
});
