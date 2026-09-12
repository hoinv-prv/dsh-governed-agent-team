---
description: Chạy một task trên Agent Task Desk: tool dựng Active Run Context + run folder + status, AI đọc ARC rồi hành động với vai desk. Kèm resume / stop / status khi run bị gián đoạn.
argument-hint: <desk> --task "..." [--aip <AIP-ID>]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, TodoWrite
---

# Command Spec — `/aiws-agent-run`

> **Status:** prompt/spec (file-first), backed by thin tooling `tooling/run_agent.py` (stdlib, `py`). NOT a full CLI.
> **Built by:** AIP-EXEC-142 (Agent Runtime Command Set; AP-CR-19/20, DDR-09/10).
> **Source:** `development/ai_agents/docs/agent_runtime_design.md`; mirrors `/aiws-aip run` (thin orchestrator).
> **Scope:** assign a task to an existing Agent Task Desk, track progress, resume/stop. Does **not** create task desks (`/aiws-agent-create`), does **not** confirm memory (`/aiws-agent-review-learning`).

## Purpose
Run one task on an Agent Task Desk. The tool **prepares state** (Active Run Context + run-folder + status); the **AI then acts as the agent** by reading the ARC. Single-shot happy path; resume/stop when a run is interrupted.

## Guardrails (always)
- **Activation model — DEFAULT-OFF (CR-AIWS-2026-08-044 C0):** chỉ định agent/desk là OPTIONAL feature. AIP step không khai `Assigned Agent:` → main session thực thi **AIWS thuần** (không run, không desk); `Difficulty`/`Kind` đứng một mình = metadata, KHÔNG phải dispatch intent. Toggle project-level: `<pack-root>/pack_config.yaml` `dispatch_enabled: false` → `start`/`extend` refuse (vắng file = ON; lifecycle verbs + `list`/`memory` không bị gate). **Luật run-bắt-buộc:** main orchestrator thực thi task bằng đồ nghề desk = bắt buộc một RUN executor `main_session`; tra cứu read-only thì tự do.
- **Run ≠ auto-run.** `start` only materializes the ARC + scaffolds the run-folder. The tool NEVER calls an LLM, NEVER does the task, NEVER chains/dispatches other agents. The AI does the task, HUMAN-prompted.
- **No auto-promotion:** run output = evidence; learning = candidate (HUMAN-gated via `/aiws-agent-review-learning`). Official Wiki / memory / blueprint are NOT auto-updated.
- **Honor the agent's `non_responsibilities`** (in ARC §3): review/advisory/PM agents propose, never approve/edit/execute.
- **`aip_driven` gate (AP-CR-25 presence + AP-CR-41 conformance):** a task desk declaring `policies.run_policy.aip_driven: true` may NOT `start` without a driving `--aip <AIP-ID>` (**stage 1, presence**). **Stage 2 (AP-CR-41):** if it also declares `run_policy.aip_template`, the driving AIP's `template_source` (stamped by aiws-aip create — CR-AIWS-2026-06-050) MUST match it, compared **basename-normalized** so `aip_template` can be given as a full ID, a short alias, OR a full path. Mismatch → **refuse before scaffolding** (names expected vs actual + points at `/aiws-aip create --template <expected>`); a legacy AIP with **no `template_source` stamp** → **degrade-to-warn + proceed** (use `--strict-template` to refuse instead); unresolvable `--aip` → warn + proceed; `--aip` matching >1 file → ambiguous-refuse. All outcomes fire **before** scaffolding → **no orphan run-folder**. Task Desks without `run_policy` (or `aip_driven: false`, or no `aip_template`) behave exactly as before — **backward-compatible**.
- **Wiki-first NOT Wiki-only:** ground in Wiki/index first, verify important findings against source.
- **Stop-on-self-deviation (CR-AIWS-2026-08-002):** agent phát hiện mình đang lệch một rule/policy đã khai (run_policy, non_responsibilities, boundary, governance_invariant, điều khoản AIP đang drive) → DỪNG + báo (mailbox `blocked` / hand-off), cấm tự phân xử đi tiếp — `agents/blueprints/_shared/common/stop_on_deviation_rule.md`.
- Writes: **boundary-guarded to the pack root** (per-desk state dưới `agents/task_desks/<instance>/` — runs, `run_index.jsonl`, mailbox) **cộng** Task Workspace của AIP đang drive được allow-list cho run `aip_driven` (CR-AIWS-2026-06-057 — TW nằm dưới `<project>/.ai-work/workspaces/`, ngoài pack root). Không ghi chỗ nào khác.

## Subcommands

### `start` — assign a task (AP-CR-20)
```
/aiws-agent-run start <instance> --task "<what to do>" [--slug <short>] [--aip <AIP-ID>] [--strict-template]
                      [--executor main_session|claude_subagent] [--tier <tier>]
```
Tool: `py tooling/run_agent.py start <instance> --task "..."`
- Creates `workspace/active_runs/RUN-<ts>-<slug>/` (Phase C run templates copied) + `run_state.yaml` (status=active) + `00_active_run_context.md` (ARC).
- **`--aip <AIP-ID>` (AP-CR-25):** required when the desk declares `policies.run_policy.aip_driven: true` — the gate runs **before** scaffolding (refused start → no orphan run-folder; prints `/aiws-aip create → /aiws-aip run` guidance). When supplied, the id is seeded into `run_request.yaml` → `related_aip`, and ARC gains a **`## 8. Run policy`** section naming the driving AIP, `aip_template`, and a **`template_conformance:`** line (OK / MISMATCH / unverified) so the run is read as one step of that AIP. Optional / ignored for non-`aip_driven` desks.
- **`--strict-template` (AP-CR-41):** escalate the legacy degrade-to-warn (driving AIP without a `template_source` stamp) into a refuse-before-scaffold. Default off = warn-and-proceed (backward-compatible). No effect when conformance is already verifiable or the desk is non-`aip_driven`.
- **Then the AI** reads the ARC and acts as the agent: writes `output/` (per blueprint `output_templates/`), ticks `run_state.yaml` `progress`, captures ≥1 learning candidate to `learning_candidates.jsonl` (status=candidate). On finish, set `run_state.yaml` `status: completed` (or leave `incomplete` if stopping mid-way).

- **`--executor` (CR-AIWS-2026-08-044):** executor cho ĐÚNG dispatch này — mang lựa chọn plan-time (AIP step field `Executor:` / HUMAN-stated; tool chỉ validate ∈ `run_policy.executors_allowed`, guard CR-013 kiểm theo requested executor). Vắng → desk default `run_policy.executor`.
- **`--tier` (CR-AIWS-2026-08-045):** execution tier cho dispatch này — validate ∈ `capability.tiers_supported` của desk, resolve → `{model, effort}` qua `agents/execution_tiers.yaml` (profile `default_provider`); refuse trước scaffold khi thiếu mapping. Run stamp tier + resolved values.

### `resume` — continue an interrupted run
```
/aiws-agent-run resume <instance> <run_id>
```
- Refreshes ARC + shows `run_state.yaml` (progress). AI reloads ARC + run-so-far (`output/`, `run_log.jsonl`, progress) and continues. Refuses if the run is `completed`/`stopped`.

### `extend` — multi-step span: next consecutive step (CR-AIWS-2026-08-046)
```
/aiws-agent-run extend <instance> <run_id> --step STEP-NN [--task "<note>"]
```
- Nới run ACTIVE (TW-backed, aip_driven) sang **step LIÊN TIẾP kế tiếp cùng desk, cùng driving AIP** — "span". STATE-PREP ONLY: chạy đủ gate per-step TRƯỚC khi nhận (toggle C0 + stage-3 re-read + consecutive check; refuse = không ghi gì), rồi append **step-brief** vào `messages_in.jsonl` + refresh ARC + stamp `span_steps` (additive).
- **Main session** sau đó CONTINUE **chính** desk subagent đang sống với step-brief mới (named continuation — **KHÔNG fork**; fork-for-desk bị cấm nguyên trạng per AGENT_USAGE_GUIDE §5.2). Hand-off contract **per-step** — main verify xong mới extend tiếp.
- Ranh giới span: không vắt qua HARD GATE / Review Note / HUMAN step (các step đó fail gate → đóng run, span mới sau gate); **1 span giữ 1 tier**; vẫn 1 active run/TW. Blocked giữa span → `incomplete` (mailbox + resume như CR-060/061; resume fallback spawn-mới là semantics bảo đảm — DP-046-1).

### `status` — check progress / list runs
```
/aiws-agent-run status <instance> [run_id]
```
- With `run_id`: prints that run's status + `run_state.yaml`. Without: **lists** all runs (active + completed) and their status. Reconciles any `completed`/`stopped` run still in `active_runs/` → `completed_runs/`.
- This is where the HUMAN decides **resume vs stop** for an `incomplete` run.

### `stop` — abandon a run
```
/aiws-agent-run stop <instance> <run_id> [--reason "<why>"]
```
- Sets `status: stopped` (+ reason), moves the run to `completed_runs/` (evidence kept). Not deleted; rollback-friendly.

## Status lifecycle
`active` (open) → `incomplete` (exited, resume-able) → `completed` (done) / `stopped` (HUMAN abandoned). A run-folder with no `run_state.yaml` (pre-runtime runs) = `completed` (backward-compat).

## Outputs (per run)
`00_active_run_context.md` (ARC) · `run_state.yaml` (status+progress) · `output/` (agent deliverables) · `learning_candidates.jsonl` · `human_feedback.md` (via `/aiws-agent-feedback`) · plus the Phase C run-record files. On close the run sits in `completed_runs/`.

## Related
`/aiws-agent-create` (make the desk) · `/aiws-agent-feedback` (feedback on a run) · `/aiws-agent-review-learning` (confirm candidates → memory).
Lifecycle (AP-CR-27/28): `/aiws-agent-upgrade` (reconcile vs a newer blueprint) · `/aiws-agent-clone` (new task desk from an existing one).

## Two-phase run (plan_first) — CR-AIWS-2026-07-016
`start` on a `plan_first` desk (or `--plan-first`) stops at PHASE 1: agent drafts `run_plan.md`
(Working-AIP-Lite; Task VERBATIM), status `awaiting_plan_confirm`. HUMAN gates: `confirm-plan
<instance> <run>` (records `plan_confirmed_by/at`) → `active`; execution then has NO mid-run gate
(OP log-and-continue). `resume` refuses unconfirmed plan-phase runs. aip_driven + `--aip` skips
plan-first (AIP = the confirmed plan). Plan outgrows the run → promote via `/aiws-aip create` (escape
hatch). Canonical-touching tasks still REQUIRE a full AIP — plan_first never replaces `aiws-aip create`.

## Multi-agent collaboration via one driving AIP — CR-AIWS-2026-07-018
1 task nhiều agent = 1 driving AIP: mỗi step gán `Assigned Agent: <instance_id>` (AIP_Detail_Spec
§7.2); các run dispatch với `--aip <AIP>` REUSE chung Task Workspace, mỗi run ở `runs/<run_id>/`
(không ghi đè nhau); output run trước = input run sau qua `input_manifest` trỏ TW paths — hết
manual copy. Chain ledger = TW `run_log.jsonl`. Stage-3 enforcement: desk ∉ assigned set →
refused; AIP không `status: active` → refused; revoke = sửa AIP. DP-913-D: khi plan đã HUMAN-confirm
với run list enumerated, main session dispatch không re-confirm router per-run (bounded); run ngoài
list vẫn confirm. Tool KHÔNG bao giờ tự chain agents; tuần tự 1 active run/TW (MVP).

## Executor `claude_subagent` — CR-AIWS-2026-08-007

`run_policy.executor: main_session | claude_subagent` (default `main_session` — legacy, không đổi hành vi).
**CR-AIWS-2026-08-044:** executor nay là lựa chọn **per-assignment plan-time** (`start --executor` mang AIP `Executor:` field / HUMAN-stated; `run_policy.executor` = default; additive `executors_allowed` giới hạn tập — review-family khóa `[claude_subagent]`); guard CR-013 kiểm theo **requested** executor; toggle C0 + luật run-bắt-buộc xem Guardrails. Tier per-dispatch: CR-AIWS-2026-08-045 (`--tier`, registry `execution_tiers.yaml` §8F). Span/extend: CR-AIWS-2026-08-046. Authority chi tiết: `agent_runtime_design.md` §8E–§8F.
Với `claude_subagent`: `start` chạy đủ gate như cũ (AP-CR-25/41 + stage-3, TRƯỚC scaffold) → rc=0 → **main
session** spawn Claude sub-agent `<desk_id>` (shim sinh sẵn tại `.claude/agents/<desk_id>.md` bởi
`tooling/build_agent_shims.py` — regenerate ở create/clone/rename/upgrade) với dispatch brief 3-block; agent
đọc Desk (scoped-load digest+hints) + ARC/TW, làm task, **return = hand-off contract** (summary +
self-assessment + suggested-next + POINTERS — không lặp nội dung workspace); main verify rồi đóng run.
`blocked` → mailbox answer → resume = spawn mới (ARC surface answer — CR-060/061). Shim tools whitelist
LOẠI `Agent` (no chaining). Tool vẫn KHÔNG spawn/gọi LLM (§8D invariant). Chi tiết: `agent_runtime_design.md` §8E.
**Output-contract profile (CR-AIWS-2026-08-012):** dưới `claude_subagent`, bắt buộc ghi thành FILE chỉ là
`output_contract.required_core` (review family: `review_report.md` + `learning_candidates.jsonl`); các
`companion_foldable` (`findings_table` / `open_questions` / `references_used`…) được phép **fold thành mục
có tên tương ứng bên trong report** — môi trường sub-agent từ chối companion `.md` (đo ở Phase B).
`main_session` giữ nguyên `required` cũ (không hồi tố); fold không được làm mất nội dung.
**Họ PM (CR-AIWS-2026-08-013):** profile là `required_core_policy: task_scoped` — run khai **đúng MỘT**
deliverable (`task_breakdown` / `progress_report` / `risk_issue_decision_log`) ở dispatch, cộng
`learning_candidates.jsonl`; `replan_options`/`prioritization_output` foldable. **Guard:** `start` **từ
chối trước scaffold** nếu desk khai `executor: claude_subagent` mà blueprint thiếu profile
(`lint_agents` cũng WARN `blueprint_missing_executor_profile`) — cách sửa là khai profile cho blueprint,
không phải tắt guard.

## Capability routing + eligibility + resume-from-inbox — CR-AIWS-2026-07-061
Step mang optional `Difficulty:` (low|medium|high) + `Kind:` (task-kind tags); agent mang `capability:`
(`complexity_ceiling` + `task_kinds`). Main session dùng helper `_route_step` (thuần) để chọn desk:
`ceiling >= Difficulty` AND `task_kinds ∩ Kind`; tie-break = `Assigned Agent` thắng, else ceiling-đủ-thấp-nhất;
không có agent phù hợp / mơ hồ → STOP hỏi HUMAN. `start --step STEP-NN` ghi `related_task_card`. Trước khi
scaffold, `_dispatch_eligible` (§5) kiểm: AIP active · non-APPLY_CR · Expected Outputs ⊆ TW (không product//truth//wiki)
· không Review Note/HARD GATE · không multi_system (v1) · inputs resolve được. **resume-from-inbox:** run `blocked`
→ `incomplete`; main ghi answer qua mailbox (CR-060); `resume` rebuild ARC + surface answer từ `messages_in.jsonl`
để finalize. Tool vẫn thin — KHÔNG gọi LLM, KHÔNG spawn agent (operator session quyết định). Tuần tự Phase-1
(parallel-limited = Phase-2).
