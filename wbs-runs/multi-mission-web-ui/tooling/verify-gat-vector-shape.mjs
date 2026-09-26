import fs from 'node:fs';

const path = 'docs/conformance/gat-conservative-mvp-v1.json';
const document = JSON.parse(fs.readFileSync(path, 'utf8'));
if (!Array.isArray(document.vectors)) throw new Error('vectors must be an array');

const expectedPinned = [
  'GAT-AUTH-001','GAT-AUTH-002','GAT-AUTH-003A','GAT-AUTH-003B','GAT-AUTH-004','GAT-AUTH-005',
  'GAT-PREFILTER-001','GAT-PREFILTER-002','GAT-PREFILTER-003','GAT-MCP-RAW-001','GAT-REV-001','GAT-PROMO-001',
  'GAT-PLAN-001','GAT-PLAN-002','GAT-MISSION-001','GAT-AIP-001','GAT-AIP-002','GAT-AIP-003','GAT-WS-001',
  'GAT-EXEC-001','GAT-EXEC-002','GAT-EXEC-003','GAT-EXEC-004','GAT-SEARCH-001','GAT-SEARCH-002','GAT-GET-001',
  'GAT-WRITE-001','GAT-REVISION-001','GAT-DELETE-001','GAT-DELETE-002','GAT-LIFECYCLE-001','GAT-LIFECYCLE-002',
  'GAT-AUDIT-001','GAT-AUDIT-002','GAT-AUDIT-003','GAT-AUDIT-004','GAT-AUDIT-005','GAT-TXN-001','GAT-TXN-002',
  'GAT-RESTART-001','GAT-TENANT-001','GAT-DESK-001','GAT-ACT-001',
];
const expectedExtensions = [
  'GAT-PATH-001','GAT-INJECTION-001','GAT-CLASS-001','GAT-RETENTION-001',
  'GAT-AUDIT-READ-001','GAT-DEGRADE-001','GAT-EXPIRY-001','GAT-BACKUP-001',
];
const requiredNullReasons = [
  'GAT-PREFILTER-001','GAT-PREFILTER-002','GAT-PREFILTER-003','GAT-EXEC-001','GAT-EXEC-003',
  'GAT-SEARCH-001','GAT-WRITE-001','GAT-DELETE-001','GAT-AUDIT-001','GAT-INJECTION-001',
];
const byId = new Map(document.vectors.map((vector) => [vector.id, vector]));
const ids = document.vectors.map((vector) => vector.id);
const pinned = document.vectors.filter((vector) => vector.source !== 'threat_model_extension').map((vector) => vector.id);
const extensions = document.vectors.filter((vector) => vector.source === 'threat_model_extension').map((vector) => vector.id);
const sorted = (items) => [...items].sort();
const equalSets = (left, right) => JSON.stringify(sorted(left)) === JSON.stringify(sorted(right));

const failures = [];
if (ids.length !== 51) failures.push(`total=${ids.length}`);
if (new Set(ids).size !== 51) failures.push(`unique=${new Set(ids).size}`);
if (!equalSets(pinned, expectedPinned)) failures.push('pinned_id_set_mismatch');
if (!equalSets(extensions, expectedExtensions)) failures.push('extension_id_set_or_source_mismatch');
const allowExplicit = document.vectors.filter((vector) => vector.expected && vector.expected.reason_code === 'ALLOW_EXPLICIT').map((vector) => vector.id);
if (allowExplicit.length) failures.push(`ALLOW_EXPLICIT=${allowExplicit.join(',')}`);
const nonNullRequired = requiredNullReasons.filter((id) => !byId.has(id) || byId.get(id).expected.reason_code !== null);
if (nonNullRequired.length) failures.push(`required_null_reason=${nonNullRequired.join(',')}`);

const result = {total: ids.length, unique: new Set(ids).size, pinned: pinned.length, extensions: extensions.length, allowExplicit, nonNullRequired, failures};
process.stdout.write(`${JSON.stringify(result)}\n`);
if (failures.length) process.exitCode = 1;
