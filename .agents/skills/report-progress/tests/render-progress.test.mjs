import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { loadMission, writeReport } from '../scripts/render-progress.mjs';
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
const json = (value) => `${JSON.stringify(value, null, 2)}\n`;
async function fixture(base, name = 'mission', active = true) {
  const root = path.join(base, 'wbs-runs', name); await mkdir(root, { recursive: true });
  const task1 = { id: 'gate', title: 'Gate <script>alert(1)</script>', depends_on: [], deliverable: 'accepted', max_attempts: 2, effort_minutes: 45 };
  const task2 = { id: 'build', title: 'Build', depends_on: ['gate'], deliverable: 'next', max_attempts: 3, effort_minutes: 90 };
  const v1 = { format: 'dsh-wbs/1', mission_id: name, revision: 1, limits: { max_total_attempts: 8 }, tasks: [task1, task2] };
  const v2 = { ...v1, revision: 2, limits: { max_total_attempts: 10 }, tasks: [{ ...task1, title: 'Gate revised' }, task2] };
  const v1Bytes = json(v1); const v2Bytes = json(v2); await writeFile(path.join(root, 'wbs.v1.json'), v1Bytes); await writeFile(path.join(root, 'wbs.v2.json'), v2Bytes);
  const execution = { format: 'dsh-wbs-execution/1', mission_id: name, revision: 1, plan_sha256: hash(v1Bytes), run_state: active ? 'active' : 'done', attempts_charged: 3, tasks: { gate: { state: 'accepted', attempts: [{ id: 'a1' }] }, build: { state: 'failed', attempts: [{ id: 'a2' }, { id: 'a3' }] }, legacy: { state: 'accepted', attempts: Array.from({ length: 20 }, (_, index) => ({ id: `legacy-${index}` })) } } };
  const decisions = { format: 'dsh-wbs-decisions/1', mission_id: name, decisions: [{ id: 'approve-2', kind: 'revision', revision: 2, plan_sha256: hash(v2Bytes), decision: 'approve' }] };
  await writeFile(path.join(root, 'execution.json'), json(execution)); await writeFile(path.join(root, 'decisions.json'), json(decisions)); return root;
}
test('explicit mission renders selected versus approved, approved denominator, escaped HTML and preserves controls', async () => { const base = await mkdtemp(path.join(os.tmpdir(), 'report-progress-')); try { const root = await fixture(base); const controls = ['execution.json', 'decisions.json', 'wbs.v1.json', 'wbs.v2.json']; const before = Object.fromEntries(await Promise.all(controls.map(async (file) => [file, hash(await readFile(path.join(root, file)))]))); const result = await writeReport({ cwd: base, missionRoot: root, generatedAt: '2026-09-14' }); assert.deepEqual({ selected: result.selectedRevision, approved: result.approvedRevision, accepted: result.accepted, total: result.total, charged: result.attemptsCharged, cap: result.attemptCap }, { selected: 1, approved: 2, accepted: 1, total: 2, charged: 3, cap: 10 }); const html = await readFile(result.outputPath, 'utf8'); assert.match(html, /Selected revision <b>1<\/b>/); assert.match(html, /latest HUMAN-approved revision <b>2<\/b>/); assert.doesNotMatch(html, /<script>alert/); assert.match(html, /WBS dependency view/); assert.match(html, /Logical Gantt/); assert.match(html, /HUMAN cần làm gì/); for (const file of controls) assert.equal(hash(await readFile(path.join(root, file))), before[file]); } finally { await rm(base, { recursive: true, force: true }); } });
test('implicit mission resolution refuses ambiguity', async () => { const base = await mkdtemp(path.join(os.tmpdir(), 'report-progress-')); try { await fixture(base, 'one'); await fixture(base, 'two'); await assert.rejects(() => loadMission({ cwd: base }), /MISSION_ROOT_AMBIGUOUS:2/); } finally { await rm(base, { recursive: true, force: true }); } });
test('output is restricted to HTML inside mission root', async () => { const base = await mkdtemp(path.join(os.tmpdir(), 'report-progress-')); try { const root = await fixture(base); await assert.rejects(() => writeReport({ cwd: base, missionRoot: root, output: path.join(base, 'outside.html') }), /OUTPUT_PATH_NOT_ALLOWED/); await assert.rejects(() => writeReport({ cwd: base, missionRoot: root, output: path.join(root, 'execution.json') }), /OUTPUT_PATH_NOT_ALLOWED/); } finally { await rm(base, { recursive: true, force: true }); } });
