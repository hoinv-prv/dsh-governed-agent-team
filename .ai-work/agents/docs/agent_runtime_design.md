# Agent Runtime Design — run/feedback (AI Agents Pack)

> **Status:** CANONICAL (beta) — version: see `PACK_VERSION.md` (pack root); promoted CR-AIWS-2026-06-055, formalized CR-AIWS-2026-08-036. **Source:** DDR-09/10/11 + AP-CR-19/20/21 (`docs/agent_pack_impl_package/docs/08_/09_`).
> **Built by:** AIP-EXEC-142 STEP-01 (Design deliverable, embedded). **Mental-model:** mirrors `/aiws-aip run` (thin orchestrator).
> **Reuses:** Phase C run schema (`<pack root>/agents/templates/run/`) — this design only **ADDS** `run_state.yaml` + `00_active_run_context.md`; it does **not** modify the existing run-record fields.

The Agent Runtime Command Set lets a HUMAN **assign a task to an agent task desk, track progress, resume/stop, and give feedback** — file-first, HUMAN-controlled, no auto-run, no auto-promotion. The runtime is a **thin orchestrator** (`run_agent.py`): it prepares state (Active Run Context + run-folder + status) for the AI to **act as the agent**; it never calls an LLM, never auto-runs a task, never chains agents.

## 0. Glossary — Agents Platform v2 vocabulary (AUTHORITY — CR-AIWS-2026-08-006)

- **agent** — the worker that executes one run: a Claude sub-agent (executor `claude_subagent`, definition generated at `.claude/agents/<desk_id>.md` — §8E) or the main session acting-as-agent (executor `main_session`). Stateless per run; state sống ở desk.
- **agent task desk (ATD)** — thực thể AIWS bền vững per role (trước: *agent instance*): identity (`desk.yaml` — P2 live 2026-08-05) + `memory/` + `process/` + `training/` + `workspace/` (runs). Agent ngồi vào desk để làm task; desk giữ mọi thứ học được.
- **agent task desk blueprint (ATDB)** — template tạo desk (trước: *agent blueprint*); từ CR-AIWS-2026-08-008 là thin archetype (chỉ phần portable — §10).
- Quy tắc viết: không dùng trần "agent" cho desk; tên cũ chỉ xuất hiện dạng "(formerly *agent instance*)" một lần mỗi doc khi cần bridge. P2 mechanical rename LIVE 2026-08-05 (AIP-EXEC-993): `agents/task_desks/` + `desk.yaml` + `.atdb_snapshot` là primary; tools dual-read tên cũ (`agents/instances/`, `instance.yaml`, `.blueprint_snapshot`) cho installs chưa migrate. YAML keys nội bộ (`instance_id`…) giữ nguyên — machine-key stability. Map: `docs/p2_rename_map.json`.
- **Dispatch-handle invariant (CR-AIWS-2026-08-044):** bề mặt giao việc chỉ định **agent** bằng handle **== `desk_id`** (shim `.claude/agents/<desk_id>.md` sinh 1:1 từ desk — §8E). Desk là toolkit + state anchor, **không phải bên nhận việc**; mọi gate/ledger key theo desk đứng trên bất biến 1:1 này — đổi nó là một CR migration riêng. **Activation model (C0): default = KHÔNG chỉ định** — step không khai `Assigned Agent:` → main session thực thi AIWS thuần (không run, không desk); toggle project-level `pack_config.yaml dispatch_enabled` (vắng = ON) tắt/bật cả cơ chế dispatch.
- 3-layer ownership (FR-AI-09) đọc theo tên mới: **ATDB** (AIWS-owned, upgradeable) / **Desk-override** (HUMAN-confirm per change) / **Desk-learned** (never auto-overwritten).

## 1. Run model

- **One run = one task assignment** to one desk. Happy path = **single-shot** (AI reads the Active Run Context, does the task in-session, writes the run-record).
- **Multi-step span (CR-AIWS-2026-08-046 C1):** một assignment có thể là **MỘT CHUỖI step LIÊN TIẾP cùng desk trong 1 driving AIP** — run 1-step là trường hợp con, hành vi cũ giữ nguyên 100%. Span chỉ hình thành giữa các step **ĐÃ chỉ định** cùng desk (activation C0 — CR-044); ranh giới cứng: KHÔNG vắt qua HARD GATE / Review Note / HUMAN-interaction step (gặp gate → run đóng, span mới sau gate); vẫn **1 active run/TW** (span là MỘT run). Mỗi step kế tiếp đi qua `extend` (gate per-step — §8E); hand-off contract vẫn **per-step**. `run_state` thêm additive `span_steps: [...]`.
- A run can be **interrupted** (long task / AI stopped mid-way). The HUMAN inspects progress via `status` and decides **resume** or **stop**.
- **Two-phase run (`plan_first` — CR-AIWS-2026-07-016):** desk policy `run_policy.plan_first: true`
  (or `--plan-first`) makes `start` stop at PHASE 1: the agent drafts `run_plan.md` (Working-AIP-Lite
  shape; task VERBATIM — the durable task record, since resume rewrites the ARC task line), status
  `awaiting_plan_confirm`; the HUMAN gates via `confirm-plan` (writes `plan_confirmed_by/at`), then
  execution proceeds with NO mid-run gate (OP log-and-continue). `resume` refuses an unconfirmed
  plan-phase run. An aip_driven run WITH `--aip` skips plan-first (the AIP already passed Gate U1);
  a plan that outgrows a run promotes to a full AIP via `/aiws-aip create` (escape hatch — not default).
- **Lifecycle `status`** (OQ-3):
  | status | meaning |
  |---|---|
  | `awaiting_plan_confirm` | phase-1 (plan_first): run_plan drafted/being drafted; waiting for HUMAN `confirm-plan` (CR-AIWS-2026-07-016) |
  | `active` | run open / in progress (just started, or being worked) |
  | `incomplete` | exited before done — **resume-able** (work remains) |
  | `completed` | task done; run closed |
  | `stopped` | HUMAN stopped/abandoned; run closed (evidence kept) |
- **Folder placement:** an open run lives under `agents/task_desks/<id>/workspace/active_runs/RUN-<id>/`; on `completed`/`stopped` it **moves** to `workspace/completed_runs/RUN-<id>/` (mirror Phase C).
- **Task Workspace reuse (agent-via-AIP) — CR-AIWS-2026-06-057 Phase 1:** when the desk is `aip_driven` and the run is started with a driving `--aip`, the run does **not** create a separate in-desk run-folder — it **reuses the driving AIP's Task Workspace** (`.ai-work/workspaces/{account}/{task_id}/`, resolved via the AIP's write-once `runtime_workspace` pointer). The run's ARC + `run_state.yaml` + `run_request.yaml` + `output/` materialize INTO that Task Workspace; the desk keeps a boundary-legal `run_index.jsonl` back-pointer (so `status`/`resume`/`stop` still resolve the run). Captures tier up to that Task Workspace's `08_capture_inbox.jsonl` (applied CR-042 C1). This removes the "two workspaces to track" problem for agent-via-AIP. A no-AIP / agent-only run keeps the in-desk folder above (Task-Workspace generalization for agent-only is CR-057 Phase 2). **Per-run namespacing (CR-AIWS-2026-07-018):** N runs may reuse ONE Task Workspace (multi-agent
  collaboration on one driving AIP) — each TW-backed run materializes into `<TW>/runs/<run_id>/`
  (run_state + ARC + run_request + output/ + reference surfaces); chain-shared surfaces stay at the
  TW root (`run_log.jsonl` = the CHAIN LEDGER — one line per run event; `08_capture_inbox.jsonl`).
  One ACTIVE run per TW at a time (sequential — MVP). Legacy pre-018 TW-root runs stay readable
  (fallback in `_find_run`). **Dispatch enforcement (stage-3, DP-913-D):** when the driving AIP
  declares `Assigned Agent:` steps, `start` refuses a task desk outside the assigned set and
  refuses any AIP not `status: active`; with those enforced, HUMAN-confirmed plans may
  batch-pre-authorize dispatch (router re-confirm per-run waived ONLY for enumerated runs);
  everything else still confirms per-run. `run_request.related_task_card` anchors the AIP STEP id —
  the ASC of the step IS the task card (no separate schema); `handoff_artifacts/` stays informal
  for standalone (non-AIP) chains.
- **Backward-compat (R-6):** a run-folder with **no** `run_state.yaml` (e.g. the EXEC-139 sample run) is treated as `completed`. Additive only — existing run-records stay valid.

## 2. `run_state.yaml` schema (NEW — additive, OQ-2)

One per run-folder. Plain/literal YAML only (no folded `>-`). Holds status + progress so the run is resume-able and inspectable.

```yaml
# run_state.yaml — runtime state of one agent run (additive to Phase C run-record)
run_id: RUN-20260621-0930-mock-design
agent_instance_id: detailed_design_review_agent__sample_project
status: active            # active | incomplete | completed | stopped
created_at: "2026-06-21"
updated_at: "2026-06-21"
stopped_reason: null      # filled only when status=stopped
progress:                 # ordered checklist the AI ticks as it works (resume reads this)
  - step: read ARC + task request
    done: true
  - step: produce review_report
    done: false
notes: <one-line current-state note for the HUMAN>
```

- `status` is the single source of truth for lifecycle. `progress` is a coarse checklist (NOT per-token) — enough for a HUMAN to judge resume vs stop.
- `run_agent.py` reads/writes ONLY this file for state; it does not parse `run_log.jsonl` for status.

## 3. Active Run Context (ARC) — `00_active_run_context.md` (NEW)

Materialized by `run_agent.py start` (and refreshed by `resume`) into the run-folder. It is the **focused reading surface** the AI reads to act as the agent — analogous to `00c_active_step_context.md` (ASC) for AIPs. Sections:

1. **Run identity** — run_id, instance_id, status, created_at.
2. **Task request** — the HUMAN's task prompt (free text the HUMAN supplies).
3. **Agent definition (from blueprint via `blueprint_ref`)** — mission · responsibilities · **non_responsibilities** · skills (skill_index) · process (refs) · output_templates (refs).
4. **Context (from desk `context/`)** — wiki_references · source_references · source_priority · **working_inventory** (non-wiki files) · ignored_paths.
5. **Confirmed memory** — desk `memory/confirmed_memory.jsonl` (load confirmed-only; newest-first) + lessons/local_guidelines.
6. **Output contract** — where to write outputs (`output/`) + which templates; learning candidates → `learning_candidates.jsonl`.
7. **Guardrails** — Wiki-first-not-Wiki-only · no auto-promotion · HUMAN-gated · the agent's non_responsibilities.

ARC is a **read surface for the AI**; `run_agent.py` assembles it by reading the desk + blueprint files (it does not invent content).

## 4. Subcommand semantics — `/aiws-agent-run <sub>` (AP-CR-19/20)

`run_agent.py` does state prep ONLY; the **AI** does the task by reading ARC. (OQ-5)

| subcommand | tooling (`run_agent.py`) does | AI then does |
|---|---|---|
| `start <instance> [--task "..."]` | create `active_runs/RUN-<ts>-<slug>/` from Phase C templates; write `run_request.yaml` + `run_state.yaml` (status=active); materialize `00_active_run_context.md` from blueprint+context+memory+task | read ARC → act as agent → write `output/` + `learning_candidates.jsonl`; tick `progress`; set status `completed` (or leave `incomplete`) |
| `resume <run>` | refresh ARC; show `run_state.yaml` (progress) | reload ARC + run-so-far → continue → update progress/status |
| `status [instance|run]` | read `run_state.yaml`; with no run-id → **list** runs of the desk + their status | (decide resume/stop) |
| `stop <run> [--reason]` | set status=`stopped` + `stopped_reason`; move to `completed_runs/` | — |
| `confirm-plan <instance> <run>` | CR-AIWS-2026-07-016: HUMAN confirms `run_plan.md` → status `active` (records `plan_confirmed_by/at`) | (two-phase run — §1) |
| `list` | AP-CR-22: list task desks (id · display_name · blueprint · status) | (directory) |
| `memory <instance> [--full]` | AP-CR-22: read-only confirmed memory (count + index; `--full` dumps) | (inspect) |
| `upgrade` / `clone` / `rename` | desk-lifecycle verbs (AP-CR-27/28/30) — semantics ở command specs riêng | (lifecycle — §8) |
| *(completed)* | when AI sets status=`completed`, tooling moves run → `completed_runs/` | — |

- **No `start` auto-runs the task.** Tooling stops after materializing ARC; the AI (prompted by HUMAN) does the work. No chaining/dispatch of other agents.

## 5. Feedback flow — `/aiws-agent-feedback <run>` (AP-CR-21)

```
HUMAN feedback on a run
  → append to run-folder human_feedback.md
  → emit learning candidate(s) status=candidate to BOTH (OQ-4):
       • run-folder  learning_candidates.jsonl   (run-local evidence)
       • desk        training/candidate_queue.jsonl   (review queue)
  → /aiws-agent-review-learning  (existing)  → HUMAN confirm → confirmed_memory.jsonl
```

- **NO direct memory write** (FR-MEM-04): feedback only produces candidates; confirmation is the existing 2-step HUMAN gate. `run_agent.py`/feedback never touch `confirmed_memory.jsonl`.
- **Capture routing (CR-AIWS-2026-08-010):** personal learning → Desk (candidate queue); capture chung dự án/task/wiki/aiws → Task Workspace `08_capture_inbox.jsonl` — bảng phân loại: `agents/blueprints/_shared/common/capture_routing_rule.md`.

## 6. `run_agent.py` scope / boundaries (OQ-5, R-1/R-4)

- **Thin wrapper, stdlib-only**, run with `py` (bare `python` broken on this machine); UTF-8 stdout (cp932-safe). Mirror `run_aip.py` structure (argparse subcommands + boundary guard).
- Does: scaffold run-folder, write/read `run_state.yaml`, materialize/refresh ARC, list/show runs, move active→completed.
- Does **NOT**: call an LLM, act as the agent, auto-run/loop/chain, write `confirmed_memory.jsonl`, write outside the pack root + allow-listed Task Workspace (below).
- **Boundary guard:** refuse any write whose resolved path is outside the **pack root** (anchor-agnostic — `product/agents/` canonical · `.ai-work/agents/` installed; `DEV_ROOT` = script parent.parent) **or** an explicitly allow-listed driving-AIP Task Workspace (`_EXTRA_ALLOWED_ROOTS`, CR-AIWS-2026-06-057) (mirror `run_aip.py` `_ensure_inside`).

## 7. Guardrails (carry pack philosophy)

- File-first · HUMAN invokes each run (no auto-run/chain) · single-shot happy path · resume is HUMAN-driven.
- No auto-promotion: output = evidence, learning = candidate (HUMAN-gated via review-learning); Official Wiki / memory / blueprint not auto-updated.
- **Stop-on-self-deviation (CR-AIWS-2026-08-002):** phát hiện mình đang lệch một rule/policy đã khai → DỪNG + báo, cấm tự phân xử — `agents/blueprints/_shared/common/stop_on_deviation_rule.md`.
- Canonical: `product/agents/` ↔ `.ai-work/agents/` byte-identical (promoted CR-AIWS-2026-06-055 — fulfills AP-CR-10); mọi thay đổi CR-gated (rule #8); dev tree `development/ai_agents/` đã retired + deleted (CR-AIWS-2026-08-039 — git history = provenance).

## 8. Relationship to existing surfaces

- **Reuses** Phase C run-record (run_request/run_context/run_log/output/used_*/human_feedback/learning_candidates) — adds `run_state.yaml` + `00_active_run_context.md`.
- **Complements** `/aiws-agent-create` (makes the desk) and `/aiws-agent-review-learning` (confirms candidates). The **Core runtime** group = create → run → feedback → review-learning; the **Desk lifecycle** group (upgrade / clone / rename) maintains a task desk after creation; `/aiws-agent` is the **Convenience router** over both.
- DD §8 addendum: `run_state.yaml` + ARC are the runtime additions to the §8 run/workspace model (additive; §8 fields unchanged).

## 8A. Agent capability declaration (NEW — CR-AIWS-2026-07-059, additive)

Blueprint / desk schema carries an OPTIONAL `capability:` block — the machine-readable declaration a main
agent uses to route an AIP step (`Difficulty` / `Kind`, AIP_Detail_Spec §7.2) to a capability-matched agent:

```yaml
capability:
  complexity_ceiling: low | medium | high   # ceiling order: low < medium < high
  task_kinds: [ ... ]                         # intersected with a step's Kind tags
```

Desk `capability` (if present) overrides the blueprint's. **Declaration only** — the routing/match mechanics
(`complexity_ceiling >= step.Difficulty` AND `task_kinds ∩ step.Kind`, tie-break, refuse-under-capable) live in
the agents-pack runtime (CR-AIWS-2026-07-061). Absent = today's behavior (static `Assigned Agent` / main session).

**`tiers_supported` (additive — CR-AIWS-2026-08-045 C2):** `capability.tiers_supported: {<tier>: <ceiling>}`
(inline map) — trần per-TIER của desk (trần phụ thuộc loại task nên đặt ở desk, không ở registry §8F). Vắng mặt
→ derive `{standard: <complexity_ceiling>}` (backward-compatible; desk không khai gì → tier routing inert).
Tier names phải thuộc registry `agents/execution_tiers.yaml`; lint_agents WARN `tiers_supported_invalid`.

## 8B. Mailbox — sub↔main messaging (NEW — CR-AIWS-2026-07-060, additive)

When a driving AIP runs multi-agent, sub-agents and the main agent exchange messages over an OPTIONAL
append-only JSONL mailbox — the same private/shared split as the chain ledger (CR-018): run-private
`<TW>/runs/<run_id>/messages_out.jsonl` (sub → main) + `messages_in.jsonl` (main → sub), merged into a
TW-root `messages.jsonl` by the main agent. **run-private staging + main merge — no live bus, no shared-file
race** (helpers `_merge_messages` / `_mailbox_answer` / `_read_inbox` in run_agent.py; all boundary-guarded,
never call an LLM). Line schema:

```
{msg_id, ts, from, to, step_id, run_id, kind, decision_class, content, status}
  kind ∈ {progress, info, question, blocked, answer, handoff_ready}
  decision_class ∈ {technical, coordination, business_rule, sot_conflict}
  status ∈ {open, answered, closed}
```

- **`blocked` → resume:** a non-blocking `question` is *log-and-continue*; a `blocked` message sets
  `run_state.status: incomplete` (run_state stays the SOLE lifecycle truth — the mailbox never carries status).
  The main agent records the answer via `_mailbox_answer`; **resume-from-inbox** (CR-AIWS-2026-07-061) rebuilds
  the ARC from `run_state` + `messages_in.jsonl` and finalizes.
- **`decision_class` — HUMAN-only for business/SoT (DP-F, safety rule):** a `blocked`/`question` with
  `decision_class ∈ {business_rule, sot_conflict}` is **HUMAN-only** — the main agent may only *relay* the
  HUMAN's decision, never decide it (state-don't-self-conclude at the orchestration layer; closes the
  gate-laundering hole the Hermes IR flagged as M-04). `decision_class ∈ {technical, coordination}` → the main
  agent may answer, grounded in the workspace.
- **`pending_human` handoff carry-field:** `input_manifest` may list items still awaiting a HUMAN decision so a
  downstream step does not assert them.
- Optional surface; `lint_workspace` recognizes it when present (JSONL hygiene + schema), never requires it.

## 8C. Capability routing + step-dispatch eligibility + resume-from-inbox (NEW — CR-AIWS-2026-07-061, additive)

The mechanics that consume the §8A capability declaration + the §7.2 `Difficulty`/`Kind` step fields. **All are
state-prep/decision helpers in `run_agent.py` — the tool NEVER spawns an agent and NEVER calls an LLM; the
operator/main session decides which `start` to invoke.** (See §8D executor-boundary ruling.)

- **Capability routing** (`_route_step`, pure): match `complexity_ceiling >= step.Difficulty` AND
  `task_kinds ∩ step.Kind ≠ ∅`. Tie-break: an explicit `Assigned Agent` wins; else the lowest sufficient ceiling
  (cheapest capable agent). No capable agent, or ambiguous → STOP and ask HUMAN. `_instance_capability` reads a
  candidate's `capability:` (desk.yaml, else its blueprint). Routing is **static / plan-time** — HUMAN sees
  the chosen `Assigned Agent` set when approving the AIP; re-routing = editing the AIP (stage-3 unchanged).
- **Activation gate (CR-AIWS-2026-08-044 C0; CR-045 C3):** routing CHỈ chạy cho step **opt-in tường minh** —
  `Assigned Agent: <desk_id>` (gán cứng) hoặc `Assigned Agent: auto` (routing resolve desk). Step không khai →
  `_route_step` trả no-dispatch (default = main session thực thi AIWS thuần, không desk/run); `Difficulty`/`Kind`
  đứng một mình = metadata mô tả, KHÔNG phải dispatch intent.
- **Chiều tier (`_route_tier`, pure — CR-AIWS-2026-08-045 C3):** trong desk ĐÃ chọn, chọn tier **rẻ nhất** có
  `tiers_supported[tier] >= Difficulty` (thứ tự khai báo registry = rẻ→đắt — cheapest-capable nối dài CR-061);
  không tier đủ trần → refuse-under-capable / STOP hỏi HUMAN. `start --tier` validate ∈ tiers_supported.
- **Step-dispatch eligibility** (`_dispatch_eligible`, §5, machine-checkable, runs before scaffolding): AIP
  `status: active` · non-APPLY_CR template · Expected Outputs ⊆ the Task Workspace (no `product/`,
  `.ai-work/truth/`, wiki-canonical) · no Review Note / HARD GATE / HUMAN-interaction step · `multi_system`
  refused in v1 (rule #12 never waived) · inputs resolvable (Deferred lookups resolved pre-dispatch). An
  in-session sub-agent MAY use `lookup_wiki_source.py` at registered scope; raw stays CR-052-gated.
- **`--step STEP-NN`** on `start` records `run_request.related_task_card` (the step's ASC IS the task card).
- **resume-from-inbox** (extends `cmd_resume`, CR-016): a `blocked`→`incomplete` run resumes by rebuilding the
  ARC from `run_state` + `messages_in.jsonl` (CR-060); the relayed answer is surfaced in the ARC, so the run
  finalizes with the decision in view. No live channel.
- **Sequential in Phase-1** — routing/eligibility/resume do NOT re-open "one active run per TW" (parallel-limited
  = Phase-2). Dispatch-brief (ARC): a run-scoped finding-ID prefix + "surface out-of-slice observations as a
  mailbox `info`, do NOT verdict them" keep fan-out boundaries clean.

## 8D. Executor boundary — in-session sub-agent ≠ L-2 engine (RULING — CR-AIWS-2026-07-062)

**Ruling (DP-H, PO-approved 2026-07-16):** an **in-session sub-agent** — spawned by the operator/main session's
own harness, invoked per an `active` driving AIP (DP-913-D pre-authorization), not outliving the main process,
using the same governance surfaces — is **NOT** the "real CLI / autonomous engine" that L-2 scope-locks, and is
NOT the external executor CR-AIWS-2026-07-019 (Hermes) gates. The invariant that makes this hold: **`run_agent.py`
never calls an LLM and never spawns/chains agents** — it prepares and gates state (routing/eligibility/mailbox/
resume helpers are all state-prep); the operator session does the dispatch. External executors (a separate
process/CLI running unattended) remain **L-2 Post-MVP + CR-019 default-REJECT** — no scope is lifted here.

**Method disciplines (proven in the PoCs, apply to any fan-out / replication):**
- **Frozen foundation (A/L):** a fan-out / replication step MUST run against a foundation the main agent froze
  first (understanding + plan + pinned checklist). PoC #3: this keeps multi-agent output stable (gate 3/3); a
  free foundation reintroduces variance.
- **Verify, don't re-judge (F):** the orchestrator accepts a sub-agent's verdicts as primary and verifies
  evidence + cross-run coherence; it does not re-derive verdicts (PoC #1: a shallow re-judgment was worse than
  the sub-agent's ensemble).

## 8E. Executor model — `run_policy.executor` (NEW — CR-AIWS-2026-08-007, additive)

`run_policy.executor: main_session | claude_subagent` — **default `main_session`** (absent = legacy behavior, backward-compatible 100%).

**Dispatch surface (CR-AIWS-2026-08-044):** executor là lựa chọn **per-assignment, plan-time** — AIP step field
`Executor:` (AIP_Detail_Spec §7.2) hoặc HUMAN-stated trong hội thoại → truyền xuống `start --executor` (tool chỉ
**validate**, không bao giờ tự chọn; model không có quyền tùy nghi — concept-map invariant #2 mở rộng).
`run_policy.executor` giữ vai trò **default** khi assignment không nói gì; additive
`run_policy.executors_allowed: [...]` giới hạn tập cho phép (vắng = `[executor]`; desk không khai executor →
`[main_session]`). **Guard CR-013 re-key theo REQUESTED executor** (desk-declared là trường hợp con). **Toggle
C0:** `<pack-root>/pack_config.yaml` `dispatch_enabled: false` → `start`/`extend` refuse; vắng file/key = ON
(cài pack = opt-in — DP-044-3); lifecycle verbs + read-only `list`/`memory` không bị gate. **Luật run-bắt-buộc
(C5ii):** main orchestrator THỰC THI task bằng đồ nghề desk (process/skill/memory) = bắt buộc một RUN executor
`main_session` — tra cứu read-only thì tự do; không tồn tại "mượn đồ nghề ngoài run". Review-family desks khóa
`executors_allowed: [claude_subagent]` (blindness — DP-044-2, PO 2026-08-14; lint `shim_desk_binding_drift`
canh bất biến shim 1:1).

**Tier áp vào spawn (CR-AIWS-2026-08-045 C4):** dispatch resolve tier → profile của `default_provider` (§8F) →
`{model, effort}` làm spawn params + block "tier policy" (autonomy LỚP 1) trong dispatch brief;
`run_state`/`run_request` stamp **tier + resolved {provider, model, effort}** (C5 — mapping đổi theo thời gian,
số đo phải ghi giá trị thực chạy). Đường `main_session`: stamp để ledger nhất quán; model/effort phiên chính
không đổi giữa task (cache — AGENT_USAGE_GUIDE §5.3.6). **1 span giữ 1 tier.**

**Span / continue (CR-AIWS-2026-08-046 C3):** step đầu của span = spawn **named** desk subagent như flow dưới
(KHÔNG fork — fork-for-desk bị cấm nguyên trạng, AGENT_USAGE_GUIDE §5.2); step kế: main **verify hand-off** step
trước (§8D) → `extend <desk> <run> --step STEP-NN` (STATE-PREP ONLY: toggle C0 + stage-3 re-read + consecutive
check TRƯỚC khi nhận; append step-brief vào `messages_in.jsonl` + refresh ARC + stamp `span_steps`) → main
**CONTINUE chính subagent đó** với step-brief mới. Blocked giữa span → `incomplete` như CR-060/061; resume
fallback **spawn-mới là semantics bảo đảm** (DP-046-1; continue là tối ưu khi harness còn giữ agent).

Per-desk enablement: khuyến nghị mở cho review-family trước (DP-991-A).

**Dispatch flow (`claude_subagent`):**
1. `run_agent.py start <desk> --aip …` chạy MỌI gate hiện có (AP-CR-25 presence → AP-CR-41 template conformance → CR-018 stage-3) **TRƯỚC scaffold — không gate nào đổi**. Tool vẫn thin: KHÔNG spawn, KHÔNG gọi LLM (bất biến §8D giữ nguyên).
2. rc=0 → **main session** spawn agent (Claude sub-agent `<desk_id>`) với dispatch brief 3-block (digest bối cảnh + step info + hand-off contract — chuẩn 2026-07-17).
3. Agent đọc Desk theo **scoped-load policy hiện có** (digest + hints, AP-CR-26/CR-017 — KHÔNG đọc hết bàn) + ARC/Task Workspace.
4. Return = **hand-off contract**: summary + self-assessment + suggested-next + POINTERS (04/05/mailbox/08/output) — không lặp nội dung workspace.
5. Main verify (per §8D "Verify, don't re-judge") + đóng run.

**Blocked/resume:** agent không hỏi được giữa run → return `blocked` + câu hỏi trong hand-off; answer qua mailbox `messages_in.jsonl` (§8B); resume = spawn mới, ARC surface answer (CR-060/061 — cơ chế giữ nguyên, đổi vehicle). **No chaining:** shim tools whitelist LOẠI `Agent` tool — agent không spawn agent (luật Phase-1 giữ).

**Output-contract profile theo executor (CR-AIWS-2026-08-012, DP-012-A = Option A).** Blueprint
`output_contract` được viết cho `main_session` (agent ghi thẳng nhiều file). Môi trường sub-agent có
chính sách riêng về việc ghi file báo cáo — đo được ở Phase B (AIP-EXEC-994): `review_report.md` ghi
OK, companion `.md` kế tiếp bị TỪ CHỐI ("subagents should return findings as text"), `.jsonl` được
chấp nhận. Vì vậy hợp đồng output **khai theo executor**, không để mỗi run tự chế workaround
(pre-registration — Runtime_Review_Methodology §10 rule 4):

| executor | Họ agent | Bắt buộc ghi thành FILE | Companion |
|---|---|---|---|
| `main_session` | mọi họ | `output_contract.required` (nguyên như cũ — **không hồi tố**) | như cũ |
| `claude_subagent` | **review** (dd/testcase) | `output_contract.required_core` (`review_report.md` + `learning_candidates.jsonl`) | `companion_foldable` — file HOẶC **mục có tên tương ứng bên trong `review_report.md`** |
| `claude_subagent` | **PM** (CR-AIWS-2026-08-013) | `required_core_policy: task_scoped` — **đúng MỘT** deliverable trong `required_core_candidates`, khai ở dispatch (AIP step Expected Outputs / task text) + `required_core_always` (`learning_candidates.jsonl`) | `companion_foldable` — file HOẶC mục trong deliverable chính |
| `claude_subagent` | **coordinator** | `required_core` (1 core doc + learning candidates) | `companion_foldable` |

**Vì sao PM khác:** ba `required` của PM là deliverable ĐỘC LẬP, khác người đọc (team / quản lý / PM+HUMAN)
— fold chung sẽ tạo artifact không ai đọc; còn đòi đủ ba mỗi run thì vốn đã không đúng ngay cả dưới
`main_session`. Task-scoped core biến hợp đồng thành thứ **kiểm được per-run** mà không phải đoán trước
ngữ nghĩa PM (pre-registration — Runtime_Review_Methodology §10 rule 4).

**Bất biến (CR-AIWS-2026-08-013):** *mọi shipped blueprint đều khai executor profile* (`required_core`
hoặc `required_core_policy`). Cưỡng chế hai lớp: `run_agent.py start` **từ chối trước scaffold** khi một
desk khai `executor: claude_subagent` mà blueprint của nó thiếu profile; `lint_agents` bắn WARN
`blueprint_missing_executor_profile` để bất biến hiển thị cả khi không chạy run. Lý do có guard: trước
CR-013, **không cơ chế nào** ngăn việc bật executor trên desk thiếu profile — chỉ có người tình cờ để ý.

Quy tắc: khi fold, report phải có mục mang đúng vai của companion (findings table / open questions /
references used) — fold **không** được làm mất nội dung. Hand-off contract KHÔNG đổi (vẫn
summary + POINTERS-only) và dispatch flow/gates cũng không. **DP-991-D (reviewer read-only) resolve
theo dữ liệu Phase B:** sub-agent GIỮ quyền Write trong run folder (đủ để ghi required_core) — chọn
"read-only tuyệt đối" sẽ buộc mọi output đi qua return, phá chính hand-off POINTERS-only; boundary
vẫn được hậu kiểm (Phase B: `git status` fixtures + desk sạch).

**Shim = generated artifact:** `.claude/agents/<desk_id>.md` sinh bởi `tooling/build_agent_shims.py` từ desk identity + ATDB (frontmatter: `name`=desk_id, `description`=when-to-use routing, `tools`=whitelist; BODY: identity + Desk pointer + load policy + boundary + non_responsibilities + stop-on-self-deviation + capture routing + "đọc dispatch brief/ARC trước"). Regenerate ở create/clone/rename/upgrade; sửa tay sẽ bị generator ghi đè. **Native harness** — cùng permission envelope/session tree ⇒ KHÔNG thuộc phạm vi CR-019 (external executor, §8D ruling áp nguyên).

> **Shim registration lag (CR-AIWS-2026-08-015):** sinh shim ≠ agent type dispatch được ngay trong
> phiên hiện tại — harness đăng ký theo lịch riêng (đo được: ranh giới session; xem
> known_limitations L-10). Enablement flow phải thiết kế chịu được lag: bật `executor:
> claude_subagent` chỉ sau khi dogfood PASS ở phiên có agent type; dispatch fail vì "agent type not
> found" trên shim hợp lệ = BLOCKED môi trường, không phải lỗi desk/blueprint — đừng "sửa" desk để
> chữa nó.

## 8F. Execution tier registry — `agents/execution_tiers.yaml` (NEW — CR-AIWS-2026-08-045)

Registry **2 LỚP, phi trạng thái** (tier không memory, không shim riêng, không là "ai" — level là THAM SỐ
dispatch, không phải thực thể):

- **LỚP 1 `tiers:`** — năng lực trừu tượng, provider-agnostic: `display_name` + autonomy policy
  (`stop_threshold` — ngưỡng dừng-hỏi; `scoped_load_depth` — hints-only vs mở full khi cần). Khởi điểm 2 tier
  `standard`/`deep` (DP-045-1); nhãn nhân sự (junior/senior) nếu muốn chỉ là `display_name` (DP-045-2).
- **LỚP 2 `provider_profiles:`** — map tier → `{model, effort}` **THEO PROVIDER**, kèm `effort_vocab` per
  provider. `default_provider` chọn profile active (pack-level; per-dispatch provider override NGOÀI scope MVP).
  **MVP ship duy nhất profile `claude`** (DP-045-4: `standard → {claude-sonnet-5, medium}` ·
  `deep → {claude-opus-5, high}`).

Nguyên tắc: desk/spec/AIP chỉ biết **tier name** — model ids (đổi nhanh theo thời gian) chỉ sống ở registry
(**single point of update**: đổi mapping = sửa 1 file, không cần CR trừ khi đổi schema). Thêm provider (vd
`codex`) = thêm block, KHÔNG đổi schema — và **profile là DATA, không phải sanction executor**: external
executor vẫn L-2 Post-MVP + CR-AIWS-2026-07-019 default-REJECT (§8D nguyên trạng). Tier KHÔNG được đổi output
contract / gates / `non_responsibilities` / memory ownership (desk-owned, HUMAN-gated). **Escalation ladder
(C6):** run tier thấp `blocked`/REWORK vì đuối năng lực → re-dispatch cùng desk tier cao hơn — quyết định
plan-time/HUMAN, ghi ledger; model KHÔNG tự leo thang. "Thăng chức" xảy ra ở bảng routing/mapping: HUMAN chỉnh
`tiers_supported`/profiles định kỳ theo run stamps (C5) — agent không tự tiến hóa. Lint:
`provider_profile_invalid` + `tiers_supported_invalid` (lint_agents).

## 9. Reference resolution — `lookup_intents` + ARC §4A (canonical per CR-AIWS-2026-07-014)

Formalizes the AIP-EXEC-154 prototype (draft CR-AIWS-AGENT-FRAMEWORK-002; all 7 defaults
HUMAN-confirmed 2026-06-23, ratified by CR-AIWS-2026-07-014):

- **`context/wiki_references.yaml` has two sides** — static `recommended_entries` (pre-listed wiki
  entries; convention: include the per-system `SRC-OVERVIEW-*` first-read pages) and dynamic
  **`lookup_intents[]`**: a process-named intent → structured index query. Required keys `intent` +
  `search_targets` (real index source_type/reference_type) + `fallback` ∈ {report_reference_gap,
  ask_human_if_required, continue_with_limitation}; optional `description` / `required_task_metadata`
  / `system_scoped` (multi-system: pass `--system <id>`; ambiguous → STOP and ask HUMAN).
- **Resolver** = `.ai-work/tooling/lookup_wiki_source.py` — returns POINTERS, never auto-loads
  content. Default scope `project,aiws`; **agents hold NO standing raw-search grant** (CR-052
  authorization frame; DP-913-B): raw/local search stays HUMAN/AIP/agent-rule-gated.
- **ARC §4A "Reference resolution & run rationale"** — Process Interpretation / Selected+Excluded
  References / Reference Gaps / Assumptions / Limitations — is a SECTION of the ARC (no separate
  artifact), filled by the agent as it selects context.
- `lookup_intents` are DESK-owned and blueprint-upgrade-immune (like working_inventory);
  populated at create-time (AI-suggested, HUMAN-gated), refined via learning candidates.
- Ratified defaults (full wording: draft CR-002 §14): no-blueprint = first-class-not-default ·
  source_type reuse over new types · project assets registered `status: draft` · intent min-metadata ·
  Process-Interpretation-in-ARC · create-time suggestion degrades gracefully · samples as-is in MVP.

## 10. ATDB content contract — thin archetype (CR-AIWS-2026-08-008)

Một ATDB chỉ giữ phần **portable thật** giữa mọi dự án; domain content thuộc project, bơm vào desk lúc create (interview — CR-AIWS-2026-08-009). Ba cơ chế sống nhờ ATDB **không đổi**: upgrade/reconcile (AP-CR-27 — diff nhỏ đi vì skeleton nhỏ), governance-invariant floor (AP-CR-31 — so desk process vs skeleton invariants), learning uplink (`blueprint_improvement_candidate` — P2 rename `atdb_improvement_candidate`).

| Ở LẠI skeleton (portable — AIWS-owned) | CHUYỂN project-local (bơm lúc create) |
|---|---|
| `governance_invariant` steps + boundary/non_responsibilities defaults | Checklist domain (DD/BD/testcase nội dung nghiệp vụ) |
| Learning/capture wiring (candidate types, lifecycle, routing pointers) | Process nghiệp vụ chi tiết per khách hàng/dự án |
| Desk schema (memory/process/training/workspace layout) | Ngôn ngữ output, spec refs, ví dụ domain |
| Output contract SHAPE (report skeleton, finding format refs) | Severity tuning per dự án (base definitions ở `_shared` giữ) |
| tools-whitelist defaults + `run_policy` defaults (executor, aip_driven, aip_template) | — |

Domain content hiện có trong 4 ATDB **không xoá** khi migrate — chuyển thành `docs/reference_content/` trong chính ATDB (seed tham khảo, không auto-copy; wizard offer như một nguồn domain content). `_shared/review/process/*` (severity/finding-format/source-trace/leg-rubric) **GIỮ NGUYÊN** — proven bằng đo lường (CR-053/056), portable đúng nghĩa. *(Migration per-file = apply-AIP riêng, bảng phân loại present PO trước khi ghi — CR-008 T2.)*
