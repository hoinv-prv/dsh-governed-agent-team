#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { lstat, mkdir, readFile, readdir, realpath, rename, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const esc = (value) => String(value ?? '').replace(/[&<>"']/gu, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const pct = (value) => `${Math.max(0, Math.min(100, value)).toFixed(2)}%`;
const readJson = async (file) => JSON.parse(await readFile(file, 'utf8'));
const hashFile = async (file) => sha256(await readFile(file));

function parseArgs(argv) {
  const result = { missionRoot: null, output: null, date: null };
  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index];
    if (arg === '--mission-root') result.missionRoot = argv[++index];
    else if (arg === '--output') result.output = argv[++index];
    else if (arg === '--date') result.date = argv[++index];
    else throw new Error(`UNKNOWN_ARGUMENT:${arg}`);
  }
  return result;
}

async function discoverMissionRoot(cwd) {
  const base = path.join(cwd, 'wbs-runs');
  const entries = await readdir(base, { withFileTypes: true });
  const active = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const root = path.join(base, entry.name);
    try { if ((await readJson(path.join(root, 'execution.json'))).run_state === 'active') active.push(root); } catch { /* not a mission */ }
  }
  if (active.length !== 1) throw new Error(`MISSION_ROOT_AMBIGUOUS:${active.length}`);
  return active[0];
}

function collectAttempts(execution) {
  const byTask = new Map(); const seen = new Set();
  const add = (attempt, fallbackTask) => {
    if (!attempt || typeof attempt !== 'object' || !attempt.id || seen.has(attempt.id)) return;
    seen.add(attempt.id); const taskId = attempt.task_id ?? fallbackTask; if (!taskId) return;
    if (!byTask.has(taskId)) byTask.set(taskId, []); byTask.get(taskId).push(attempt);
  };
  for (const [taskId, task] of Object.entries(execution.tasks ?? {})) for (const attempt of task?.attempts ?? []) add(attempt, taskId);
  for (const [key, value] of Object.entries(execution)) if (key.endsWith('_attempts') || key.startsWith('task_attempts_')) for (const attempt of Array.isArray(value) ? value : []) add(attempt, null);
  return byTask;
}

function latestApproval(decisions) {
  return (decisions.decisions ?? []).filter((item) => item.kind === 'revision' && item.decision === 'approve' && Number.isSafeInteger(item.revision)).sort((a, b) => b.revision - a.revision)[0] ?? null;
}

function statusFor(taskId, execution, approvedPending) {
  const raw = execution.tasks?.[taskId]?.state ?? 'pending';
  if (taskId === 'governance-replan' && approvedPending) return 'active';
  if (raw === 'accepted') return 'accepted';
  if (['failed', 'review_required', 'verifying', 'running'].includes(raw)) return raw === 'running' ? 'active' : 'recovery';
  return 'pending';
}

function statusLabel(status) {
  return ({ accepted: 'ACCEPTED', active: 'ACTIVE', recovery: 'CHANGES REQUIRED', pending: 'PENDING' })[status] ?? status.toUpperCase();
}

function logicalSchedule(tasks) {
  const times = new Map();
  for (const task of tasks) {
    const duration = Math.max(1, Math.ceil((task.effort_minutes ?? 60) / 90));
    const start = Math.max(0, ...(task.depends_on ?? []).map((id) => times.get(id)?.end ?? 0));
    times.set(task.id, { start, end: start + duration, duration });
  }
  return { times, total: Math.max(1, ...[...times.values()].map((item) => item.end)) };
}

function humanActions(approvedPending, firstOpen) {
  const now = approvedPending ? 'Không cần làm gì; approval đã được ghi nhận và coordinator sẽ reconcile revision.' : 'Không cần làm gì trong lúc implementation tiếp tục.';
  return [now, `Khi ${firstOpen ? firstOpen.title : 'standalone freeze'} cần HUMAN gate, review exact evidence/hash rồi accept hoặc reject.`, 'Conformance execution và DSH installation/activation luôn là các quyết định riêng sau này.'];
}

export async function loadMission({ cwd = process.cwd(), missionRoot = null } = {}) {
  const requested = missionRoot ? path.resolve(cwd, missionRoot) : await discoverMissionRoot(cwd);
  const root = await realpath(requested); const executionPath = path.join(root, 'execution.json'); const decisionsPath = path.join(root, 'decisions.json');
  const execution = await readJson(executionPath); const decisions = await readJson(decisionsPath); const approval = latestApproval(decisions);
  const selectedPath = path.join(root, `wbs.v${execution.revision}.json`); const selected = await readJson(selectedPath); const selectedHash = await hashFile(selectedPath);
  if (selectedHash !== execution.plan_sha256) throw new Error('SELECTED_PLAN_HASH_MISMATCH');
  let approved = selected; let approvedPath = selectedPath; let approvedHash = selectedHash;
  if (approval) { approvedPath = path.join(root, `wbs.v${approval.revision}.json`); approved = await readJson(approvedPath); approvedHash = await hashFile(approvedPath); if (approvedHash !== approval.plan_sha256) throw new Error('APPROVED_PLAN_HASH_MISMATCH'); }
  const controlPaths = [executionPath, decisionsPath, selectedPath, ...(approvedPath === selectedPath ? [] : [approvedPath])];
  const controlHashes = Object.fromEntries(await Promise.all(controlPaths.map(async (file) => [file, await hashFile(file)])));
  return { root, execution, decisions, selected, selectedHash, approved, approvedHash, approval, controlPaths, controlHashes };
}

export function renderReport(model, { generatedAt = new Date().toISOString().slice(0, 10) } = {}) {
  const { execution, selected, approved, approvedHash, approval } = model; const tasks = approved.tasks ?? []; const attempts = collectAttempts(execution);
  const approvedPending = approved.revision !== selected.revision; const rows = tasks.map((task) => ({ ...task, state: statusFor(task.id, execution, approvedPending), used: attempts.get(task.id)?.length ?? 0 }));
  const accepted = rows.filter((task) => execution.tasks?.[task.id]?.state === 'accepted').length; const touched = rows.filter((task) => task.state !== 'pending' || task.used > 0).length; const total = rows.length; const charged = execution.attempts_charged ?? 0; const cap = approved.limits?.max_total_attempts ?? charged; const remaining = Math.max(0, cap - charged); const firstOpen = rows.find((task) => task.state !== 'accepted' && !(approvedPending && task.id === 'governance-replan'));
  const schedule = logicalSchedule(rows); const color = { accepted: '#18864b', active: '#d28b00', recovery: '#bd5600', pending: '#7a8799' };
  const flow = rows.map((task, index) => `<div class="node ${esc(task.state)}"><b>${index + 1}. ${esc(task.title)}</b><small>${esc(task.id)}</small><span>${statusLabel(task.state)}</span><em>depends: ${esc((task.depends_on ?? []).join(', ') || 'none')}</em></div>`).join('<i>→</i>');
  const gantt = rows.map((task) => { const time = schedule.times.get(task.id); return `<div class="g-row"><span>${esc(task.title)}</span><div class="track"><div class="bar" style="left:${pct(time.start / schedule.total * 100)};width:${pct(time.duration / schedule.total * 100)};background:${color[task.state]}">${statusLabel(task.state)}</div></div></div>`; }).join('');
  const taskRows = rows.map((task, index) => `<tr><td>${index + 1}</td><td><code>${esc(task.id)}</code><br>${esc(task.title)}</td><td><span class="pill ${esc(task.state)}">${statusLabel(task.state)}</span></td><td>${task.used} / ${task.max_attempts ?? '?'}</td><td>${esc(task.deliverable ?? '')}</td></tr>`).join('');
  const next = approvedPending ? [`Reconcile và select WBS revision ${approved.revision}; verify AIP lint/status.`, `Tiếp tục task ${firstOpen?.id ?? 'next-ready-task'} theo exact approved scope.`, 'Chạy declared verification và independent review trước khi accept.', 'Tiếp tục dependency order đến deterministic freeze/handoff.'] : [`Tiếp tục task ${firstOpen?.id ?? 'next-ready-task'} theo exact selected WBS.`, 'Chạy declared verification và independent review trước khi accept.', 'Tiếp tục dependency order đến deterministic freeze/handoff.'];
  const humans = humanActions(approvedPending, firstOpen);
  return `<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(approved.mission_id)} — WBS Progress</title><style>
:root{--bg:#f5f7fb;--card:#fff;--ink:#172033;--muted:#647087;--line:#d8deea;--green:#18864b;--amber:#a96d00;--orange:#bd5600;--gray:#667085}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}.wrap{max-width:1240px;margin:auto;padding:28px}.hero,.card{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:0 4px 18px #26334d0d;padding:20px;margin:0 0 18px}.hero h1,h2{margin:0 0 12px}.muted{color:var(--muted)}.hash{font:12px ui-monospace,monospace;word-break:break-all}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.metric b{display:block;font-size:27px}.flow{display:flex;gap:10px;align-items:center;overflow:auto;padding-bottom:8px}.flow>i{font-size:20px;color:#929bad}.node{min-width:155px;min-height:130px;border:2px solid;border-radius:11px;padding:10px;display:flex;flex-direction:column;justify-content:center;text-align:center}.node small,.node em{font-size:10px;color:var(--muted);font-style:normal}.node span,.pill{font-weight:700;font-size:11px}.node.accepted{background:#ddf6e7;border-color:var(--green)}.node.active{background:#fff0bd;border-color:var(--amber)}.node.recovery{background:#ffe3cb;border-color:var(--orange)}.node.pending{background:#edf0f4;border-color:#8993a4}.scroll{overflow:auto}.gantt{min-width:850px}.g-row{display:grid;grid-template-columns:260px 1fr;gap:12px;margin:7px 0}.track{height:27px;position:relative;background:repeating-linear-gradient(90deg,#f0f2f7 0,#f0f2f7 calc(10% - 1px),#dce1ea calc(10% - 1px),#dce1ea 10%);border-radius:5px}.bar{position:absolute;top:4px;height:19px;color:white;border-radius:4px;padding:1px 6px;font-size:10px;white-space:nowrap;overflow:hidden}table{border-collapse:collapse;width:100%;min-width:900px}th,td{padding:9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:#f7f9fc}.pill{display:inline-block;border-radius:999px;padding:3px 8px}.pill.accepted{background:#ddf6e7;color:var(--green)}.pill.active{background:#fff0bd;color:var(--amber)}.pill.recovery{background:#ffe3cb;color:var(--orange)}.pill.pending{background:#edf0f4;color:var(--gray)}.budget{display:flex;height:30px;border-radius:7px;overflow:hidden}.used{background:#6741a5;color:#fff;text-align:center}.remain{background:#c9d4e7;text-align:center}.callout{background:#e4efff;border-left:4px solid #2463b6;border-radius:6px;padding:12px 14px}code{background:#f0f2f6;border-radius:4px;padding:2px 5px}@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}.wrap{padding:12px}}@media print{body{background:#fff}.hero,.card{box-shadow:none}}
</style></head><body><main class="wrap"><section class="hero"><h1>${esc(approved.mission_id)} — WBS Progress</h1><div>Generated: ${esc(generatedAt)}</div><p>Selected revision <b>${esc(selected.revision)}</b> · latest HUMAN-approved revision <b>${esc(approved.revision)}</b>${approvedPending ? ' · <span class="pill active">SELECTION PENDING</span>' : ''}</p><div class="hash">Approved SHA-256: ${esc(approvedHash)}</div></section>
<section class="grid"><div class="card metric"><b>${Math.round(accepted / Math.max(1,total) * 100)}%</b><span>${accepted} / ${total} accepted</span></div><div class="card metric"><b>${Math.round(touched / Math.max(1,total) * 100)}%</b><span>${touched} / ${total} touched</span></div><div class="card metric"><b>${charged} / ${cap}</b><span>attempts charged</span></div><div class="card metric"><b>${remaining}</b><span>attempts remaining</span></div></section>
<section class="card"><h2>WBS dependency view</h2><div class="flow">${flow}</div></section><section class="card"><h2>Logical Gantt</h2><div class="scroll gantt">${gantt}</div><p class="muted">Logical effort units only; not calendar commitments.</p></section>
<section class="card"><h2>Task status</h2><div class="scroll"><table><thead><tr><th>#</th><th>Task</th><th>State</th><th>Attempts</th><th>Deliverable</th></tr></thead><tbody>${taskRows}</tbody></table></div></section>
<section class="card"><h2>Attempt budget</h2><div class="budget"><div class="used" style="width:${pct(charged/cap*100)}">${charged} charged</div><div class="remain" style="width:${pct(remaining/cap*100)}">${remaining} remain</div></div></section>
<section class="card"><h2>Tiếp theo sẽ làm gì?</h2><ol>${next.map((item) => `<li>${esc(item)}</li>`).join('')}</ol></section><section class="card"><h2>HUMAN cần làm gì?</h2><div class="callout"><b>${esc(humans[0])}</b></div><ul>${humans.slice(1).map((item) => `<li>${esc(item)}</li>`).join('')}</ul></section>
<section class="card muted">Report này chỉ đọc mission controls và chỉ ghi file HTML output. Nó không chạy, resume, verify hoặc accept WBS task.</section></main></body></html>`;
}

export async function writeReport({ cwd = process.cwd(), missionRoot = null, output = null, generatedAt = null } = {}) {
  const model = await loadMission({ cwd, missionRoot }); const rootPrefix = `${model.root}${path.sep}`; const outputPath = path.resolve(cwd, output ?? path.join(model.root, 'WBS_PROGRESS.html'));
  if (!outputPath.startsWith(rootPrefix) || ['execution.json', 'decisions.json'].includes(path.basename(outputPath)) || !outputPath.endsWith('.html')) throw new Error('OUTPUT_PATH_NOT_ALLOWED');
  try { if ((await lstat(outputPath)).isSymbolicLink()) throw new Error('OUTPUT_SYMLINK_NOT_ALLOWED'); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  const html = renderReport(model, { generatedAt: generatedAt ?? new Date().toISOString().slice(0, 10) }); await mkdir(path.dirname(outputPath), { recursive: true }); const temp = `${outputPath}.${process.pid}.tmp`;
  try { await writeFile(temp, html, { encoding: 'utf8', flag: 'wx' }); await rename(temp, outputPath); } finally { await rm(temp, { force: true }); }
  for (const [file, before] of Object.entries(model.controlHashes)) if (await hashFile(file) !== before) throw new Error('MISSION_CONTROL_CHANGED');
  return { outputPath, missionId: model.approved.mission_id, selectedRevision: model.selected.revision, approvedRevision: model.approved.revision, accepted: (model.approved.tasks ?? []).filter((task) => model.execution.tasks?.[task.id]?.state === 'accepted').length, total: model.approved.tasks?.length ?? 0, attemptsCharged: model.execution.attempts_charged, attemptCap: model.approved.limits?.max_total_attempts };
}

async function main() { const args = parseArgs(process.argv.slice(2)); const result = await writeReport({ missionRoot: args.missionRoot, output: args.output, generatedAt: args.date }); process.stdout.write(`${JSON.stringify(result)}\n`); }
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main().catch((error) => { process.stderr.write(`${error.message}\n`); process.exitCode = 1; });
