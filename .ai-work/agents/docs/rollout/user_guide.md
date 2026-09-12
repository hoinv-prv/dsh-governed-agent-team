# User Guide — AI Agents Pack (current agents)  (Phase J-1)

> **Status: CANONICAL (beta) — AI Agents Pack, version: see `PACK_VERSION.md` (pack root).** Promoted by CR-AIWS-2026-06-055 (2026-06-24); status formalized by CR-AIWS-2026-08-036. Built by AIP-EXEC-141 (Phase J-1) STEP-03.
>
> **SCOPE = current agents only.** This guide is for running the **3 priority agents** day to day:
> `aiws_detailed_design_review_agent`, `aiws_testcase_review_agent` (review/advisory), and `aiws_pm_agent`
> (planning/advisory). The remaining agent types (program phases **D**/**E**/**F**/**G**/**H**) are
> **deferred — see `known_limitations_and_backlog.md`**.
>
> File-first, HUMAN-controlled: nothing auto-runs, auto-chains, or auto-promotes. Run Python with `py`.
> Paths are relative to the **pack root** (`product/agents/` canonical · `.ai-work/agents/` when installed — byte-identical mirror). Command details: `command_usage_guide.md`.

## What you can do today

- **Review a detailed design document** → `aiws_detailed_design_review_agent` produces actionable findings.
- **Review a test-case set** → `aiws_testcase_review_agent` checks requirement coverage + quality.
- **Plan / track from review findings** → `aiws_pm_agent` proposes a task breakdown, risks, and explicit
  HUMAN decision points.
- **Give feedback on a run** and **review learning candidates** to (HUMAN-)teach a task desk over time.

> **Đề xuất thay đổi pack (CR-AIWS-2026-08-001):** raise IR upstream về AIWS repo; KHÔNG mint id
> `AP-CR-*`/`CR-AIWS-*` local (namespace của upstream — registry: `docs/ap_cr_ledger.md`); dùng
> namespace local riêng cho change-record nội bộ.

All three agents are **advisory**: they propose findings/plans, they never approve, edit, execute, or
auto-update anything. Review = **Wiki-first, NOT Wiki-only** (ground in the Wiki/index first, then
verify important findings against source and report conflicts).

## The Core runtime lifecycle: create → run → feedback → review-learning

```
/aiws-agent-create  ──►  /aiws-agent-run start  ──►  /aiws-agent-feedback  ──►  /aiws-agent-review-learning
   (make desk)           (run a task; AI acts)        (feedback → candidate)      (HUMAN confirms → memory)
```

> **Shortcut:** `/aiws-agent "<natural-language request>"` (AP-CR-22) is a front-door **router** — it
> resolves which desk + verb you mean (using `list`/the fuzzy token), **confirms** the
> (desk, verb, task) reading with you, then dispatches to one of the gated verbs. It is a thin
> convenience layer and **never mutates** on its own; the gated verbs stay the canonical gated path. A
> cross-desk `/aiws-agent-board` is deferred (Post-MVP).

> **Beyond the everyday loop — Desk lifecycle verbs** (maintain a task desk after creation):
> `/aiws-agent-upgrade` (reconcile a Blueprint upgrade, HUMAN-confirmed), `/aiws-agent-clone` (copy a good
> desk to a new one), `/aiws-agent-rename` (rename id/folder/names; the old id still resolves). See
> `command_usage_guide.md` for all three groups (Core runtime · Desk lifecycle · Convenience router).

### Step 1 — Have a task desk

A **task desk** (formerly *agent instance*) binds a blueprint to one project (context + memory + workspace). Create one with
`/aiws-agent-create blueprint=<id> project=<project>` (see `command_usage_guide.md`), or reuse a
provided `…__sample_project` desk (dev fixture). At creation you give it a friendly **`display_name`** first — a
person-name like **Henry — Detailed Design Review** — and the wizard **auto-suggests the `instance_id`**
from the blueprint (e.g. `aiws_detailed_design_review_agent`); `display_name` is the renamable label you'll
see day to day, while `instance_id` is the stable handle you type in commands (AP-CR-23). Creating a
desk does **not** run it. Wire its `context/wiki_references.yaml` at your project Knowledge Hub (see
`setup_guide.md` §5).

> **Tip:** `py tooling/run_agent.py list` shows every desk (`id · display_name · blueprint ·
> status`), and command `<instance>` args accept a **fuzzy token** — a partial id, role word, or the
> display_name (e.g. `Henry`) — so you rarely type the full id. A unique match is required.

### Step 2 — Run a task (`/aiws-agent-run start`)

> **Activation — default là KHÔNG chỉ định (CR-AIWS-2026-08-044 C0):** giao việc cho agent/desk là
> OPTIONAL feature. Một AIP step không khai `Assigned Agent:` thì main session tự thực thi như AIWS
> thuần — không run, không desk nào tham gia. Khi giao việc, bạn chỉ định **AGENT** (handle == desk_id;
> desk là bộ đồ nghề + trí nhớ, không phải "bên nhận việc"), và có thể chọn thêm hai tham số plan-time:
> - `--executor main_session|claude_subagent` — đường thực thi cho ĐÚNG dispatch này (validate vs
>   `run_policy.executors_allowed` của desk; vắng = desk default).
> - `--tier <tier>` — mức năng lực (validate vs `capability.tiers_supported`; resolve → {model, effort}
>   qua registry `agents/execution_tiers.yaml`, MVP profile `claude`).

Start a run — the tool materializes the Active Run Context (ARC) and scaffolds the run-folder, then
**you (the AI), prompted by the HUMAN, act as the agent**:

```
py tooling/run_agent.py start detailed_design_review_agent__sample_project \
   --task "Review the order-cancel detailed design" --slug my-review \
   [--executor claude_subagent] [--tier standard]
```

> You can name the desk by a fuzzy token instead of the full id — e.g.
> `py tooling/run_agent.py start Henry --task "…"` resolves to the unique match.
>
> **AIP-driven task desks (AP-CR-25):** if a task desk declares `run_policy.aip_driven: true`, `start`
> **refuses** without a driving AIP and prints the `/aiws-aip create → /aiws-aip run` flow; pass
> `--aip <AIP-ID>` to proceed (e.g. `… start Henry --aip AIP-EXEC-123 --task "…"`). The gate fires
> before the run-folder is created (no orphan folder); the AIP id is recorded in `run_request.yaml`
> and shown in ARC `## 8. Run policy`. Task Desks without that policy start as normal.

This creates `…/workspace/active_runs/RUN-<ts>-my-review/` with:
- `00_active_run_context.md` (**ARC**) — the focused read surface: run identity · task request · agent
  definition from the blueprint (mission · responsibilities · **non_responsibilities** · skills ·
  process · output_templates) · context from the desk `context/` · confirmed memory · the output
  contract · guardrails.
- `run_state.yaml` (`status: active`) — status + a coarse `progress` checklist.
- `output/` + the Phase C run-record files (`run_request.yaml`, `input_manifest.md`,
  `used_references.md`, `used_tools.md`, `human_feedback.md`, `learning_candidates.jsonl`, …).

The AI reads the ARC, does the review/plan, writes `output/` (per the blueprint's output templates),
ticks `progress`, captures ≥1 learning candidate (`status: candidate`), and sets
`run_state.yaml status: completed`. The tool **never** does the task itself.

### Step 3 — Read the output

- **Review agents** write `review_report.md` (Summary · References Used (Wiki-first) · Limitations ·
  Overall Assessment · **Findings** table with severity/type/category/location/evidence · Open
  Questions · Risks · Suggested Next Actions · Learning Candidates) plus `findings_table.md`,
  `open_questions.md`, `references_used.md` (templates: `_shared/review/output_templates/`).
- **PM agent** writes `task_breakdown.md` (Facts · Assumptions · Work Breakdown · Dependency Map ·
  Critical Path · Recommended Order · Risks · **HUMAN Decisions Needed** · Next Actions +
  a `decision_request` block) and optionally `progress_report.md`, `risk_issue_decision_log.md`,
  `replan_options.md`, `prioritization_output.md` (templates:
  `agents/blueprints/aiws_pm_agent/output_templates/`). Every priority/owner/order is a **proposal** — the
  PM agent marks decision points and blocks on them; it never decides, executes, or dispatches.

### Step 4 — Track / resume / stop

```
py tooling/run_agent.py list                                                           # all task desks: id · display_name · blueprint · status
py tooling/run_agent.py status detailed_design_review_agent__sample_project           # list runs + status
py tooling/run_agent.py status detailed_design_review_agent__sample_project RUN-...    # one run's run_state
py tooling/run_agent.py memory  Henry [--full]                                          # read-only: confirmed memory (count + index; --full dumps)
py tooling/run_agent.py resume <instance> RUN-...                                       # continue an incomplete run
py tooling/run_agent.py stop   <instance> RUN-... --reason "superseded"                 # abandon (evidence kept)
```

`list` (AP-CR-22) is the desk directory; `memory <instance> [--full]` (AP-CR-22) is a **read-only**
look at what a task desk has learned (it never writes). `status` reconciles any finished run still in
`active_runs/` into `completed_runs/`. A run with no `run_state.yaml` (older runs) counts as `completed`.

**Multi-step span (CR-AIWS-2026-08-046):** một run có thể phục vụ MỘT CHUỖI step liên tiếp cùng desk
trong 1 driving AIP. Sau khi verify hand-off của step hiện tại:

```
py tooling/run_agent.py extend <desk> RUN-... --step STEP-NN   # gate per-step + step-brief vào messages_in.jsonl
```

rồi main session **CONTINUE chính desk subagent đang sống** với step-brief mới (named continuation —
KHÔNG fork; context desk digest + ARC đã nạp được giữ nguyên, đỡ sàn ~16k + nạp lại desk mỗi step).
Hand-off vẫn **per-step** — verify xong mới extend tiếp. Span không vắt qua HARD GATE / Review Note /
HUMAN step; step không liên tiếp → đóng run, mở run mới. Blocked giữa span → `incomplete` như cũ
(mailbox + resume; resume bằng spawn-mới luôn là đường bảo đảm).

### Step 5 — Give feedback (`/aiws-agent-feedback`)

```
/aiws-agent-feedback <instance> <run_id>
```

Appends your feedback to the run-folder `human_feedback.md` and emits learning **candidate(s)**
(`status: candidate`) to **both** the run-local `learning_candidates.jsonl` and the desk
`training/candidate_queue.jsonl`. **It never writes confirmed memory** — it only produces candidates.

### Step 6 — Review learning candidates (`/aiws-agent-review-learning`)

```
/aiws-agent-review-learning instance=<instance_id> [run=<RUN-id>]
```

Surfaces each candidate (id, type, content, source_run) for the HUMAN to **confirm / defer / reject**.
Only on an explicit **confirm** does an entry land in `memory/confirmed_memory.jsonl` (carrying
`source_candidate` + `confirmed_by: HUMAN`). On confirm the AI also **proposes** an optional
`applies_when` + `scope_tags` for the entry and you **approve** them (AP-CR-26): tag `always` for
cross-cutting methodology/process memory, or function/topic tags (`function:f02`, `topic:search`) for
specifics — these drive the relevance-scoped loading you see in the ARC's `§5.1 Loaded` / `§5.2 Index`
(an untagged entry stays always-load). **Nothing is auto-confirmed.** Reusable-beyond-desk items
route to a separate blueprint-improvement candidate, never auto-updating a Blueprint.

## Worked example — the J-1 scoped E2E

A recorded, real worked example of the whole chain lives at `e2e_simulation_result.md` (plan:
`e2e_simulation_plan.md`). It is **MOCK** and **scoped to review + PM only** (not the full
build/refresh/consume pack — that is J-2). It chains the 3 priority agents, HUMAN-controlled:

```
DDR review  →(handoff)→  testcase review  →(handoff: both reviews)→  PM track/plan
```

> Convention: the first mention names the agent by its friendly **display_name**; the
> **`instance_id`** in `code` is the handle you type in commands (AP-CR-23).

| Leg | Desk (display_name · `instance_id`) | Run id | Output |
|---|---|---|---|
| 1 | Henry — Detailed Design Review · `detailed_design_review_agent__sample_project` | `RUN-20260621-1655-j1-e2e` | `review_report.md` — 11 findings (4 Critical), e.g. DDR-F-001 missing PAID-order cancellation, DDR-F-004 cross-customer permission; LC-001/LC-002 candidates |
| 2 | Tess — Test-Case Review · `testcase_review_agent__sample_project` | `RUN-20260621-1657-j1-e2e` | `review_report.md` — 8 findings (1 Critical, 1 conflict) |
| 3 | Paula — PM / Planning · `pm_agent__sample_project` | `RUN-20260621-1658-j1-e2e` | `task_breakdown.md` — 7-task remediation backlog + 5 HUMAN decisions (D-1..D-5) + `decision_request` (`status: awaiting_human_decision`) |

How it ran, and the guardrails it demonstrates:
- Each leg was a real `run_agent.py start` (`--slug j1-e2e`): tool materialized the ARC, the AI acted
  as the agent, wrote `output/`, captured candidates, set `status: completed`; `status` reconciled the
  run to `completed_runs/`.
- **Handoff was HUMAN-controlled artifact-passing** — the operator manually copied the two review
  reports into the PM run's `input/HANDOFF_*.md`. No agent auto-read another agent's workspace; no
  agent chained another; the coordinator was never invoked. Record:
  `…/pm_agent__sample_project/workspace/handoff_artifacts/handoff_note_RUN-20260621-1658-j1-e2e.md`.
- **Feedback** ran once on the PM run (`/aiws-agent-feedback`): appended `human_feedback.md`, emitted
  LC-FB-001 (`status: candidate`) to both files; `confirmed_memory.jsonl` stayed empty (0 bytes).
- **`/aiws-agent-review-learning`** and **`/aiws-agent-create`** are exercised in
  `smoke_test_checklist.md`; the feedback candidate sits in the PM desk's
  `training/candidate_queue.jsonl` ready to be reviewed (no auto-confirm).
- The expected reference outputs for the agents lived in the old dev tree's `sample_project_package/expected_outputs/` (dev fixture — deleted together with `development/ai_agents/` by CR-AIWS-2026-08-039; never shipped with the pack).

> **Reader caution.** This proves the review → review → PM **mechanism** on MOCK inputs over the
> existing Knowledge Hub. It does **not** prove build/refresh/consume, wiki-meta generation, coordinator
> orchestration, or the wiki-consumer agents — those are **deferred to J-2**. The pack is not complete.

## Guardrails you will see everywhere

- **No auto-run** — a HUMAN starts every run; the tool only prepares state; no agent chains another.
- **No auto-promotion** — run output is evidence; learning stays `candidate` until HUMAN confirms;
  Official Wiki / memory / blueprint are never auto-updated.
- **Learning candidates are HUMAN-gated** — feedback only proposes; `/aiws-agent-review-learning` is
  the only path to confirmed memory, and only on an explicit HUMAN decision.
- **Honor `non_responsibilities`** — review agents review/advise only; the PM agent proposes options
  and decision points only. None approve, edit, execute, or dispatch.
- **Project toggle (CR-AIWS-2026-08-044 C0)** — dự án tắt/bật cả cơ chế dispatch bằng
  `<pack-root>/pack_config.yaml` `dispatch_enabled: false` (vắng file = ON; cài pack đã là opt-in).
  Toggle off → `start`/`extend` refuse; desk lifecycle verbs + read-only `list`/`memory` vẫn dùng được.
- **KHÔNG fork cho desk** — fork chạy bằng identity/tool-set của MAIN session (mất desk identity,
  whitelist, output contract, tier, blindness). Đường "chạy một mạch nhiều step" là **span** (named
  continuation, mục Step 4) — không phải fork. (AGENT_USAGE_GUIDE §5.2.)

## Related guides

`command_usage_guide.md` (command groups: Core runtime · Desk lifecycle · Convenience router) · `setup_guide.md` (install/wire) ·
`agent_authoring_guide.md` (author a new agent) · `smoke_test_checklist.md` (verify) ·
`known_limitations_and_backlog.md` (deferred scope) · `promotion_readiness_note.md`.

> **Multi-agent update (CR-AIWS-2026-07-018):** collaboration chạy qua MỘT driving AIP (step field `Assigned Agent`), chung Task Workspace với per-run `runs/<run_id>/`, chain ledger tại TW `run_log.jsonl`; stage-3 enforcement thay thế manual-copy handoff cho AIP-driven chains (manual handoff vẫn dùng cho standalone). Two-phase run: xem `plan_first` (CR-016).
