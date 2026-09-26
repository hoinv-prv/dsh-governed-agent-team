import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../../../', import.meta.url);
const loadJson = async (path) => JSON.parse(await readFile(new URL(path, root), 'utf8'));

const actualApis = new Map([
  ['governance.authorizeTeamPlan', ['packages/gat/src/governance/index.mjs', 'export function authorizeTeamPlan']],
  ['governance.authorizeMissionMapping', ['packages/gat/src/governance/index.mjs', 'export function authorizeMissionMapping']],
  ['governance.evaluateReadiness', ['packages/gat/src/governance/index.mjs', 'export function evaluateReadiness']],
  ['governance.checkExecutionIdentity', ['packages/gat/src/governance/index.mjs', 'export function checkExecutionIdentity']],
  ['governance.deriveAgentDeskId', ['packages/gat/src/governance/index.mjs', 'export function deriveAgentDeskId']],
  ['policy.DenyFirstPolicy.authorize', ['packages/gat/src/policy/index.mjs', 'authorize(request)']],
  ['adapter.GatMemoryAdapter.invoke', ['packages/gat/src/adapter/index.mjs', 'invoke(tool,args,trusted)']],
  ['adapter.GatMemoryAdapter.visibleTools', ['packages/gat/src/adapter/index.mjs', 'visibleTools()']],
  ['memory.physicalPartitionKey', ['packages/gat/src/memory/index.mjs', 'export function physicalPartitionKey']],
  ['memory.PartitionStore.create', ['packages/gat/src/memory/index.mjs', 'create({ context, record']],
  ['memory.PartitionStore.revise', ['packages/gat/src/memory/index.mjs', 'revise({ context, recordId']],
  ['memory.PartitionStore.tombstone', ['packages/gat/src/memory/index.mjs', 'tombstone(args)']],
  ['memory.PartitionStore.get', ['packages/gat/src/memory/index.mjs', 'get({ context, recordId']],
  ['memory.PartitionStore.search', ['packages/gat/src/memory/index.mjs', 'search({ context, query']],
  ['memory.PartitionStore.auditRead', ['packages/gat/src/memory/index.mjs', 'auditRead({ context, authority']],
  ['memory.PartitionStore.recordDenied', ['packages/gat/src/memory/index.mjs', 'recordDenied({ context, operationId']],
  ['memory.PartitionStore.placeHold', ['packages/gat/src/memory/index.mjs', 'placeHold({ context, recordId']],
  ['memory.PartitionStore.releaseHold', ['packages/gat/src/memory/index.mjs', 'releaseHold({ context, recordId']],
  ['memory.PartitionStore.purge', ['packages/gat/src/memory/index.mjs', 'purge({ context, recordId']],
  ['memory.PartitionStore.verifyAudit', ['packages/gat/src/memory/index.mjs', 'verifyAudit()']],
  ['memory.PartitionStore.recover', ['packages/gat/src/memory/index.mjs', 'recover()']],
  ['memory.PartitionStore.backup', ['packages/gat/src/memory/index.mjs', 'backup()']],
  ['memory.PartitionStore.restore', ['packages/gat/src/memory/index.mjs', 'static restore(backup']]
]);

const plannedControl = new Set([
  'control.ControlState.bindWorkspace',
  'control.ControlState.replanExecution',
  'control.ControlState.supersedeTask',
  'control.ControlState.evaluateActivation',
  'control.ControlState.evaluatePromotion',
  'control.ControlState.evaluateOptionalMemory'
]);

const exactKeys = (value) => Object.keys(value).sort();
const sorted = (value) => [...value].sort();
const executionKeys = ['id', 'operation'];
const mappingKeys = ['absence_probe', 'api', 'api_status', 'evidence_producer', 'family', 'handler', 'id', 'operation', 'predicate', 'reducer'];
const forbiddenExecutionKeys = new Set(['expected', 'required_absence', 'required_evidence', 'disposition', 'reason_code', 'result', 'bindings', 'counters', 'evidence']);

function assertNamedComponent(name, prefix) {
  assert.equal(typeof name, 'string');
  assert.match(name, new RegExp(`^${prefix}[A-Za-z0-9]+$`, 'u'));
  assert.doesNotMatch(name, /[*?]|wildcard|generic/iu);
}

test('matrix covers the exact static 51-vector contract', async () => {
  const [baseline, matrix] = await Promise.all([
    loadJson('docs/conformance/gat-conservative-mvp-v1.json'),
    loadJson('wbs-runs/multi-mission-web-ui/conformance-contract-matrix.json')
  ]);

  assert.equal(matrix.format, 'gat-conformance-contract-matrix/1');
  assert.equal(matrix.revision, 31);
  assert.equal(matrix.plan_sha256, '872248ffc2b352e869535a6a12d0145c4c69cea9b4cd35e5e5c0f92bbc58c78d');
  assert.equal(matrix.vector_source.sha256, '2250aa8bd50e08efd4e4e876e8d9ac4309d3aea8c1af424de04a817aa507b87c');
  assert.equal(matrix.vector_source.mode, 'static_contract_only');
  assert.equal(matrix.vector_source.executed, false);
  assert.equal(baseline.vectors.length, 51);
  assert.equal(matrix.mappings.length, 51);

  const baselineById = new Map(baseline.vectors.map((vector) => [vector.id, vector]));
  const matrixById = new Map(matrix.mappings.map((mapping) => [mapping.id, mapping]));
  assert.equal(baselineById.size, 51, 'baseline IDs must be unique');
  assert.equal(matrixById.size, 51, 'matrix IDs must be unique');
  assert.deepEqual(sorted(matrixById.keys()), sorted(baselineById.keys()));

  const currentCatalog = new Set(matrix.api_catalog.current);
  const plannedCatalog = new Set(matrix.api_catalog.planned_control);
  assert.equal(currentCatalog.size, matrix.api_catalog.current.length);
  assert.equal(plannedCatalog.size, matrix.api_catalog.planned_control.length);
  assert.deepEqual(sorted(currentCatalog), sorted(actualApis.keys()));
  assert.deepEqual(sorted(plannedCatalog), sorted(plannedControl));

  for (const [api, [path, declaration]] of actualApis) {
    const source = await readFile(new URL(path, root), 'utf8');
    assert.ok(source.includes(declaration), `${api} must resolve to the named current package API`);
  }

  for (const mapping of matrix.mappings) {
    const vector = baselineById.get(mapping.id);
    assert.ok(vector);
    const permittedKeys = mapping.prerequisites ? [...mappingKeys, 'prerequisites'] : mappingKeys;
    assert.deepEqual(exactKeys(mapping), sorted(permittedKeys), `${mapping.id} has an undeclared matrix field`);
    assert.equal(mapping.operation, vector.operation.name);
    assert.match(mapping.family, /^[a-z][a-z0-9_]+$/u);
    assert.ok(mapping.api_status === 'current' || mapping.api_status === 'planned_control');
    assert.ok(mapping.api_status === 'current' ? currentCatalog.has(mapping.api) : plannedCatalog.has(mapping.api));
    assert.doesNotMatch(mapping.api, /[*?]|wildcard|generic/iu);
    assertNamedComponent(mapping.handler, 'handle');
    assertNamedComponent(mapping.reducer, 'reduce');
    assertNamedComponent(mapping.predicate, 'predicate');
    assertNamedComponent(mapping.absence_probe.name, 'probe');
    assertNamedComponent(mapping.evidence_producer.name, 'produce');
    assert.deepEqual(mapping.absence_probe.tokens, vector.required_absence);
    assert.deepEqual(mapping.evidence_producer.tokens, vector.required_evidence);
    assert.equal(new Set(mapping.absence_probe.tokens).size, mapping.absence_probe.tokens.length);
    assert.equal(new Set(mapping.evidence_producer.tokens).size, mapping.evidence_producer.tokens.length);
    for (const prerequisite of mapping.prerequisites ?? []) {
      assert.ok(currentCatalog.has(prerequisite) || plannedCatalog.has(prerequisite), `${mapping.id} prerequisite must be named`);
    }

    const handlerProjection = { id: vector.id, operation: vector.operation };
    assert.deepEqual(exactKeys(handlerProjection), executionKeys);
    for (const key of Object.keys(handlerProjection)) assert.ok(!forbiddenExecutionKeys.has(key));
    for (const key of matrix.trust_boundary.terminal_comparator_only) assert.ok(!Object.hasOwn(handlerProjection, key));
  }
});

test('planned control gaps are explicit and closed before handler implementation', async () => {
  const matrix = await loadJson('wbs-runs/multi-mission-web-ui/conformance-contract-matrix.json');
  const plannedMappings = matrix.mappings.filter((mapping) => mapping.api_status === 'planned_control');
  assert.deepEqual(sorted(plannedMappings.map((mapping) => mapping.id)), sorted([
    'GAT-ACT-001',
    'GAT-DEGRADE-001',
    'GAT-EXEC-001',
    'GAT-EXEC-002',
    'GAT-EXEC-003',
    'GAT-PROMO-001',
    'GAT-WS-001'
  ]));
  assert.deepEqual(matrix.trust_boundary.handler_projection, executionKeys);
  assert.deepEqual(matrix.trust_boundary.terminal_comparator_only, ['expected', 'required_absence', 'required_evidence']);
  assert.ok(matrix.trust_boundary.forbidden_handler_fields.every((key) => forbiddenExecutionKeys.has(key)));
});
