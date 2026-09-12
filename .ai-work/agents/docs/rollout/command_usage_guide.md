# Command Usage Guide — AI Agents Pack (current agents)  (Phase J-1)

> **Status: CANONICAL (beta) — AI Agents Pack, version: see `PACK_VERSION.md` (pack root).** Promoted by CR-AIWS-2026-06-055 (2026-06-24); status formalized by CR-AIWS-2026-08-036. Built by AIP-EXEC-141 (Phase J-1) STEP-03.
>
> The agent commands fall into three groups: **Core runtime** (create → run → feedback → review-learning —
> the everyday loop), **Desk lifecycle** (upgrade / clone / rename — post-create maintenance), and the
> **Convenience router** (`/aiws-agent`). All are **file-first prompt/specs** — there is no
> executable `aiws` CLI. Only `/aiws-agent-run` is backed by tooling (`tooling/run_agent.py`, stdlib,
> run with `py`); the other three are procedures the AI follows. Each command's authoritative spec
> lives under `../../commands/`; this guide summarizes purpose / mode / inputs / outputs / guardrails
> to match those specs. Paths are relative to the **pack root** (`product/agents/` canonical · `.ai-work/agents/` when installed — byte-identical mirror).

## At a glance

| Command | Spec file | Backed by tooling? | One-line purpose |
|---|---|---|---|
| `/aiws-agent` | `commands/aiws-agent.md` | partial (read-only `list`/`memory`) | NL front-door **router**: parse request → resolve desk → confirm → dispatch to a verb below. **Never mutates** (AP-CR-22). |
| `/aiws-agent-create` | `commands/aiws-agent-create.md` | no (AI follows wizard) | Create a named task desk from a blueprint (A), AI-recommended blueprint (B), or custom (C). **Create ≠ run.** |
| `/aiws-agent-run` | `commands/aiws-agent-run.md` | yes (`tooling/run_agent.py`) | Assign a task to a task desk; track/resume/stop. `start`/`resume`/**`extend`** (multi-step span — CR-08-046)/`status`/`stop` (+ `list`/`memory`). Start nhận `--executor`/`--tier` (CR-08-044/045). **Run ≠ auto-run.** |
| `/aiws-agent-feedback` | `commands/aiws-agent-feedback.md` | no (AI follows) | Record HUMAN feedback on a run → learning **candidates**. **No direct memory write.** |
| `/aiws-agent-review-learning` | `commands/aiws-agent-review-learning.md` | no (AI follows) | Review candidates; HUMAN confirm/defer/reject → confirmed memory. **No auto-confirm.** |
| `/aiws-agent-upgrade` | `commands/aiws-agent-upgrade.md` | yes (`run_agent.py upgrade`) | **Desk lifecycle.** Reconcile a Blueprint upgrade into a task desk (3-way, HUMAN-confirmed; never clobbers desk-learned). (AP-CR-27) |
| `/aiws-agent-clone` | `commands/aiws-agent-clone.md` | yes (`run_agent.py clone`) | **Desk lifecycle.** Create a new task desk from an existing one (full-copy minus run-history; carried memory flagged `clone_review`). (AP-CR-28) |
| `/aiws-agent-rename` | `commands/aiws-agent-rename.md` | yes (`run_agent.py rename`) | **Desk lifecycle.** Rename a task desk's id/folder/names; old id stays resolvable via `previous_ids` alias. (AP-CR-30) |

> Groups: **Core runtime** = create/run/feedback/review-learning · **Desk lifecycle** = upgrade/clone/rename · **Convenience router** = `/aiws-agent`. `/aiws-agent` is a thin convenience layer (AP-CR-22) over the gated verbs above — they remain the canonical audit/gate verbs. `/aiws-agent-board` (a cross-desk status board) is **deferred — Post-MVP**.

---

## 1. `/aiws-agent-create` — make a task desk

- **Spec:** `commands/aiws-agent-create.md` (Phase B, AIP-EXEC-108).
- **Purpose:** create a named, trackable **Agent Task Desk** under
  `agents/task_desks/<instance_id>/`. It initializes identity, context references, tool bindings, and
  policies; generates the desk folder skeleton; and produces a setup summary for HUMAN review.
  **It does not run the agent.**

**Modes**

- **Mode A — explicit blueprint:** `/aiws-agent-create blueprint=<blueprint_id> [project=<project_id>]`.
  Looks `<blueprint_id>` up in `agents/blueprint_registry.yaml`; if absent, offers Mode B or C.
  Generates `blueprint_ref.yaml` (id / version / **relative** path / customization summary).
- **Mode B — AI-assisted selection:** `/aiws-agent-create` (no blueprint). Asks the purpose question,
  **recommends** registry blueprints with a reason; on accept behaves like Mode A.
- **Mode C — custom, no blueprint:** `/aiws-agent-create mode=custom` (or `no_blueprint=true`).
  Fills `agent_design_snapshot.yaml` (`creation_mode: custom_no_blueprint`, `blueprint_id: null`) from
  `agents/templates/agent_design_snapshot_template.yaml`, then runs
  `agents/templates/custom_instance_validation_checklist.md` before the setup summary.

**Inputs:** purpose, identity (AP-CR-23 — ask the friendly `display_name` like `Henry` **first**, then
**auto-suggest** `instance_id` = `<blueprint_short>` / `<blueprint_short>_<NN>`; the mandatory
`__<project>` suffix is **dropped for single-project**, kept optional only for multi-project/shared-pool;
`instance_id` is the stable machine key, `display_name` the renamable label — plus project/context name,
owner/reviewer), context references (wiki index/entries, source doc + code folders, ignored paths,
priority modules), tool bindings, policies (memory / workspace / HUMAN-gate). The wizard is the 8 steps +
11 init-question categories in the spec (see `agents/templates/instance_creation_wizard.md`).

**Outputs** (under `agents/task_desks/<instance_id>/`): `desk.yaml`, `instance_readme.md`,
`context/{wiki_references,source_references,ignored_paths,source_priority}.yaml`, **empty-skeleton**
`memory/*`, empty `workspace/{active_runs,completed_runs,handoff_artifacts,step_outputs}/`, empty
`training/*`, `tools/{local_tools/,tool_bindings.yaml}`, `changelog.md`, plus Mode A/B
`blueprint_ref.yaml` or Mode C `agent_design_snapshot.yaml`. A setup summary
(`agents/templates/instance_setup_summary.md`) is shown for HUMAN confirm.

**Guardrails:** create ≠ run (no auto-run, FR-CMD-08) · no Shared Task Workspace (Post-MVP) · no
auto-promotion — a custom desk does **not** auto-become a Blueprint (FR-AI-08) · memory ships
**empty** (no fabricated seed) · desk is `active` only after HUMAN confirms the setup summary ·
writes only under `agents/task_desks/<instance_id>/`.

---

## 2. `/aiws-agent-run` — run / track / resume / stop

- **Spec:** `commands/aiws-agent-run.md` (Phase Runtime, AIP-EXEC-142). **Backed by**
  `tooling/run_agent.py` (thin orchestrator; mirrors `/aiws-aip run` / `.ai-work/tooling/run_aip.py`).
- **Purpose:** run one task on an existing task desk. The **tool prepares state** (Active Run Context +
  run-folder + status); the **AI then acts as the agent** by reading the ARC. Single-shot happy path;
  resume/stop when interrupted. It does not create task desks (use `/aiws-agent-create`) and does not
  confirm memory (use `/aiws-agent-review-learning`).

**Subcommands** (tool = `py tooling/run_agent.py <sub> ...`)

- **`start <instance> --task "<what to do>" [--slug <short>] [--aip <AIP-ID>] [--executor E] [--tier T]`** — creates
  `workspace/active_runs/RUN-<ts>-<slug>/` (Phase C run templates copied) + `run_state.yaml`
  (`status: active`) + `00_active_run_context.md` (the ARC). **Then the AI** reads the ARC, acts as the
  agent, writes `output/` per the blueprint `output_templates/`, ticks `run_state.yaml` `progress`,
  captures ≥1 learning candidate to `learning_candidates.jsonl` (`status: candidate`), and on finish
  sets `run_state.yaml status: completed` (or leaves `incomplete` if stopping mid-way).
  `--aip` is **required** when the desk declares `run_policy.aip_driven: true` (AP-CR-25): the gate
  runs before scaffolding (no orphan run-folder), the id seeds `run_request.yaml → related_aip`, and the
  ARC gains a `## 8. Run policy` section.
  **`--executor main_session|claude_subagent` (CR-AIWS-2026-08-044):** đường thực thi cho ĐÚNG dispatch
  này — mang lựa chọn plan-time (AIP step field `Executor:` / HUMAN-stated); tool validate vs
  `run_policy.executors_allowed` của desk (vắng flag = desk default; guard output-contract profile kiểm
  theo executor được yêu cầu). **`--tier <tier>` (CR-AIWS-2026-08-045):** mức năng lực — validate vs
  `capability.tiers_supported`, resolve → `{model, effort}` qua registry `agents/execution_tiers.yaml`
  (profile `default_provider`, MVP: claude); refuse trước scaffold khi thiếu mapping; run stamp tier +
  resolved values vào `run_state.yaml`/`run_request.yaml`.
- **`resume <instance> <run_id>`** — refreshes the ARC + shows `run_state.yaml` progress. The AI
  reloads ARC + run-so-far (`output/`, `run_log.jsonl`, progress) and continues. Refuses if the run is
  `completed`/`stopped`.
- **`extend <instance> <run_id> --step STEP-NN [--task "<note>"]` (CR-AIWS-2026-08-046)** — multi-step
  **span**: nới run ACTIVE (TW-backed, aip_driven) sang step LIÊN TIẾP kế tiếp cùng desk, cùng driving
  AIP. State-prep only: chạy đủ gate per-step TRƯỚC khi nhận (toggle + stage-3 re-read + consecutive
  check; refuse = không ghi gì), append **step-brief** vào `messages_in.jsonl`, refresh ARC, stamp
  `span_steps` (additive). **Main session** sau đó CONTINUE chính desk subagent đang sống (named
  continuation — KHÔNG fork). Hand-off per-step; span không vắt qua HARD GATE / Review Note / HUMAN
  step; 1 span giữ 1 tier.
- **`status <instance> [run_id]`** — with a `run_id`: prints that run's status + `run_state.yaml`;
  without: **lists** all runs (active + completed). Reconciles any `completed`/`stopped` run still in
  `active_runs/` → `completed_runs/`. This is where the HUMAN decides resume vs stop for an
  `incomplete` run.
- **`stop <instance> <run_id> [--reason "<why>"]`** — sets `status: stopped` (+ reason), moves the run
  to `completed_runs/` (evidence kept, not deleted).
- **`list`** (AP-CR-22) — lists task desks (`id · display_name · blueprint · status`; flags
  `[aip_driven]`). No desk arg. The directory the fuzzy resolver matches against.
- **`memory <instance> [--full]`** (AP-CR-22) — read-only view of a task desk's confirmed memory
  (entry count + an `id · type · scope_tags` index, plus candidate/lessons counts); `--full` dumps every
  entry. Never writes.

**Fuzzy desk token (AP-CR-22/23):** every `<instance>` arg accepts a partial id, role word, or
`display_name` (e.g. `Henry`); a **unique** match is required (ambiguous/none → error pointing at
`list`), so the HUMAN need not type the full compound id.

**Status lifecycle:** `active` → `incomplete` (resume-able) → `completed` / `stopped`. A run-folder
with **no** `run_state.yaml` (pre-runtime runs) is treated as `completed` (backward-compat).

**Outputs (per run):** `00_active_run_context.md` (ARC) · `run_state.yaml` (status + progress) ·
`output/` (deliverables) · `learning_candidates.jsonl` · `human_feedback.md` (via feedback) · plus the
Phase C run-record files. On close the run sits in `completed_runs/`.

**Guardrails:** run ≠ auto-run — `start` only materializes the ARC + scaffolds the folder; the tool
**never** calls an LLM, does the task, or chains/dispatches other agents (the AI does the task,
HUMAN-prompted) · **`aip_driven` gate (AP-CR-25):** a task desk with `run_policy.aip_driven: true`
refuses `start` unless `--aip <AIP-ID>` is given (gate fires before scaffolding → no orphan run-folder;
satisfiable, not refuse-only; backward-compatible for non-`aip_driven` task desks) · no auto-promotion
(output = evidence, learning = candidate, HUMAN-gated via review-learning) · honor the agent's
`non_responsibilities` (review/advisory/PM agents propose, never approve/edit/execute) · Wiki-first NOT
Wiki-only · boundary guard: writes refused outside the pack root · **project toggle (CR-AIWS-2026-08-044
C0):** `pack_config.yaml` `dispatch_enabled: false` → `start`/`extend` refuse (vắng file = ON; lifecycle
verbs + `list`/`memory` không bị gate) · **activation default-off:** AIP step không khai
`Assigned Agent:` → không dispatch (main session AIWS thuần); `Difficulty`/`Kind` một mình = metadata.

---

## 3. `/aiws-agent-feedback` — feedback → candidates

- **Spec:** `commands/aiws-agent-feedback.md` (Phase Runtime, AIP-EXEC-142).
- **Purpose:** capture a HUMAN's feedback on a run so the desk can improve — **without writing
  memory directly**. Feedback becomes `human_feedback.md` evidence + learning **candidates** that a
  later HUMAN gate confirms.

**Inputs / flow:** `/aiws-agent-feedback <instance> <run_id>` →
1. Append the feedback to the run-folder `human_feedback.md` (dated; verbatim + any AI interpretation).
2. Emit learning candidate(s) (`status: candidate`) to **BOTH** the run-local
   `learning_candidates.jsonl` **and** the desk `training/candidate_queue.jsonl` (the queue
   `/aiws-agent-review-learning` scans). Candidate kinds per
   `agents/templates/learning_candidate_schema.md`.
3. Point the HUMAN to `/aiws-agent-review-learning` to confirm/defer/reject. Nothing is promoted here.

**Outputs:** updated run-folder `human_feedback.md`; new `candidate` entries in the run-local
`learning_candidates.jsonl` and the desk `training/candidate_queue.jsonl`.

**Guardrails:** no direct memory write — feedback **never** touches `memory/confirmed_memory.jsonl`
(FR-MEM-04) · no auto-learning / no auto-promotion — candidates stay candidates until HUMAN confirms ·
does not run the agent, confirm candidates, edit the blueprint, or write Official Wiki · writes only
under the run-folder + the desk `training/`.

---

## 4. `/aiws-agent-review-learning` — confirm candidates → memory

- **Spec:** `commands/aiws-agent-review-learning.md` (Phase C, AIP-EXEC-109). Reuses the AIWS capture →
  triage → HUMAN-gate mechanics at desk scope.
- **Purpose:** review a task desk's learning candidates (from runs + feedback) and let the HUMAN
  **confirm / defer / reject** each. Confirmed candidates become **confirmed memory**;
  reusable-beyond-desk items become a **blueprint improvement candidate** (separate route).

**Inputs / flow:** `/aiws-agent-review-learning instance=<instance_id> [run=<RUN-id>]` →
1. **Collect** candidates (status `candidate`/`deferred`) from `training/candidate_queue.jsonl` (and
   the named run's `learning_candidates.jsonl`).
2. **Present** each (id, type, content, source_run) to HUMAN.
3. **Decide per candidate:** **confirm** → append `confirmed_memory.jsonl` (`status: confirmed`,
   `source_candidate`, `confirmed_by: HUMAN`, `confirmed_at`); set candidate `status: confirmed`; for
   lesson/guideline/hint types also append to `memory/lessons_learned.md` /
   `local_guidelines.md` / `retrieval_hints.jsonl`. **defer** → `status: deferred`. **reject** →
   `status: rejected`.
4. **Blueprint improvement** (if reusable beyond this desk) → create/append
   `training/blueprint_creation_candidate.md` (separate from desk memory; HUMAN review later).
5. **Record review** → append a `training/periodic_review_log.md` entry.

**Outputs:** updated `memory/confirmed_memory.jsonl` (+ lessons/guidelines/hints as applicable),
updated `training/candidate_queue.jsonl` (status transitions), `training/periodic_review_log.md` entry,
optional `training/blueprint_creation_candidate.md`. Candidate status enum:
`candidate` → `confirmed` / `deferred` / `rejected` / `deprecated`.

**Guardrails:** no auto-confirm / no auto-learning (FR-MEM-04) — every promotion is an explicit HUMAN
decision · confirmed entries trace to a `source_candidate` + `confirmed_by: HUMAN` · blueprint
improvement is **separate** from desk memory (FR-AI-05); never auto-updates a Blueprint · never
promotes anything into Official Wiki or a Blueprint automatically (canonical promotion is CR-gated) ·
writes only under `agents/task_desks/<instance_id>/`.

---

## Deferred commands / capabilities

Beyond the Core-runtime + Desk-lifecycle verbs above, `/aiws-agent` (AP-CR-22) is a thin NL front-door **router** that only resolves +
confirms + dispatches to them (it never mutates). `/aiws-agent-board` (a cross-desk status board) is
**deferred — Post-MVP**. Anything tied to the deferred agent types (coordinators auto-orchestrating,
metadata/tooling/wiki-lifecycle/wiki-consumer flows) is **deferred — see
`known_limitations_and_backlog.md`** (program phases D/E/F/G/H + full cross-pack E2E → round J-2). A real
executable `aiws` CLI is Post-MVP.

> **CR-AIWS-2026-07-016/018:** thêm `start --plan-first` + `confirm-plan <instance> <run>` (two-phase); TW-backed run nay ở `runs/<run_id>/`; `start --aip` chịu stage-3 (assigned set + AIP active).
