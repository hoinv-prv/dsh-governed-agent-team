# Smoke Test Checklist — AI Agents Pack (current agents)  (Phase J-1)

> **Status: CANONICAL (beta) — AI Agents Pack, version: see `PACK_VERSION.md` (pack root).** Promoted by CR-AIWS-2026-06-055 (2026-06-24); status formalized by CR-AIWS-2026-08-036. Built by AIP-EXEC-141 (Phase J-1) STEP-05.
>
> **SCOPE = current agents only (review + PM).** This checklist dogfoods the **3 priority agents**
> (`aiws_detailed_design_review_agent`, `aiws_testcase_review_agent`, `aiws_pm_agent`) + the A/B/C foundation
> (registry / `/aiws-agent-create` / run + learning loop). It does **NOT** smoke-test build / refresh /
> consume pipelines, wiki-meta generation, the coordinator, or wiki-consumer agents — those are
> **DEFERRED to round J-2** (`known_limitations_and_backlog.md`). All inputs/evidence are **MOCK**.
>
> Run from the project root. Python via `py` (bare `python` is broken on this machine). All paths
> relative to the **pack root** (`product/agents/` canonical · `.ai-work/agents/` when installed — byte-identical mirror). Tooling: `tooling/run_agent.py`.

## How to use
Walk the steps top to bottom. Each step has a **command/action**, an **expected result**, and a
**pass check**. A green run = every pass check holds AND the guardrail checks in §G hold. The reference
evidence for a full pass is the J-1 scoped E2E (`docs/rollout/e2e_simulation_result.md`) + the
`sample_project_package/` expected outputs.

## A. Registry resolves the 3 blueprints
- [ ] **Action:** open `agents/blueprint_registry.yaml`.
- **Expected:** entries for `aiws_detailed_design_review_agent`, `aiws_testcase_review_agent`, `aiws_pm_agent` (all
  `status: active`), each with a `path:` under `agents/blueprints/…/`.
- **Pass check:** each `path:` directory exists and contains a `blueprint.yaml`. (The registry also lists
  `aiws_wiki_meta_strategy_coordinator` — present but OUT of J-1 smoke scope.)

## B. Create a task desk from a blueprint  (`/aiws-agent-create`)
- [ ] **Action:** `/aiws-agent-create blueprint=aiws_detailed_design_review_agent project=smoke` (Mode A).
- **Expected:** wizard creates `agents/task_desks/detailed_design_review_agent__smoke/` with
  `desk.yaml`, `blueprint_ref.yaml`, `context/*.yaml`, **empty-skeleton** `memory/*`,
  empty `workspace/{active_runs,completed_runs,handoff_artifacts,step_outputs}/`, empty
  `training/*`, `tools/`, `changelog.md`, `instance_readme.md`.
- **Pass checks:**
  - [ ] `memory/confirmed_memory.jsonl` is **empty** (no fabricated seed) — empty-skeleton rule.
  - [ ] **Create ≠ run:** no run-folder was created under `workspace/active_runs/`.
  - [ ] Desk is `active` only after HUMAN confirms the setup summary.
- *(For the rest of this checklist you may reuse the existing `…__sample_project` task desks instead of
  the `__smoke` one — they are already created.)*

## C. Run a review on MOCK input  (`/aiws-agent-run start` + AI acts)
- [ ] **Action:** `py tooling/run_agent.py start detailed_design_review_agent__sample_project --task "MOCK smoke: review the mock order-cancel detailed design" --slug smoke`
- **Expected:** prints `run started: RUN-<ts>-smoke`, creates `workspace/active_runs/RUN-<ts>-smoke/`
  with `00_active_run_context.md` (ARC), `run_state.yaml` (status=active), `output/`, and the Phase C
  run-record files.
- **Pass checks:**
  - [ ] ARC §2 shows the task; §3 names the blueprint + **non_responsibilities** reminder; §5 confirmed
    memory shows "(empty — no confirmed memory yet)".
  - [ ] **Tool did NOT do the task** — `output/` is empty until the AI writes it.
  - [ ] **AI then acts as the agent:** writes `output/review_report.md` (per
    `_shared/review/output_templates/review_report.md`), captures ≥1 candidate to
    `learning_candidates.jsonl` (**overwrite the template placeholder row** — see
    `issue_warning_list.md` W-01), sets `run_state.yaml status: completed`.
  - [ ] Review is **Wiki-first NOT Wiki-only** (report records the grounding gap + source verification).
- [ ] **Action:** `py tooling/run_agent.py status detailed_design_review_agent__sample_project`
- **Pass check:** the run reconciles `active_runs → completed_runs` and lists as `completed`.

## D. Run a PM task on MOCK input  (`/aiws-agent-run start` + AI acts)
- [ ] **Action:** `py tooling/run_agent.py start pm_agent__sample_project --task "MOCK smoke: plan a small remediation backlog" --slug smoke`
- **Expected:** run-folder + ARC + `run_state.yaml` as in C.
- **Pass checks:**
  - [ ] AI writes `output/task_breakdown.md` (per `agents/blueprints/aiws_pm_agent/output_templates/task_breakdown.md`).
  - [ ] Output carries **HUMAN decision points** (§10) + a `decision_request` with
    `status: awaiting_human_decision` and an `agent_will_not` block (no decide / no execute / no dispatch).
  - [ ] **No auto-execution / no dispatch** of any other agent.
  - [ ] `status` reconciles the run to `completed`.

## E. Feedback emits a candidate, not auto-confirm  (`/aiws-agent-feedback`)
- [ ] **Action:** `/aiws-agent-feedback pm_agent__sample_project <RUN-id>`
- **Expected:** appends the HUMAN feedback to the run-folder `human_feedback.md`; emits a learning
  candidate (`status: candidate`) to **BOTH** the run-local `learning_candidates.jsonl` AND
  `training/candidate_queue.jsonl`.
- **Pass checks:**
  - [ ] New candidate has `status: candidate` in both files.
  - [ ] `memory/confirmed_memory.jsonl` is **still empty** — feedback never writes confirmed memory.

## F. Review-learning surfaces the candidate, no auto-confirm  (`/aiws-agent-review-learning`)
- [ ] **Action:** `/aiws-agent-review-learning instance=pm_agent__sample_project`
- **Expected:** collects candidates from `training/candidate_queue.jsonl` (status `candidate`/`deferred`)
  and presents each (id, type, content, source_run) to HUMAN for **confirm / defer / reject**.
- **Pass checks:**
  - [ ] The feedback candidate from step E is **surfaced**.
  - [ ] **Nothing is auto-confirmed** — `confirmed_memory.jsonl` changes ONLY after an explicit HUMAN
    confirm decision (and then the entry carries `source_candidate` + `confirmed_by: HUMAN`).
  - [ ] If HUMAN does not confirm, `confirmed_memory.jsonl` stays empty.

## G. Guardrail checks (must all hold)
- [ ] **No write outside the desk workspace:** every write from a run lands under
  `agents/task_desks/<instance>/workspace/` (or `training/` for feedback). `run_agent.py` refuses any
  path outside the pack root (boundary guard).
- [ ] **Coordinator no auto-run / no auto-chain:** running a review or PM task never triggers another
  agent; the coordinator is never invoked automatically.
- [ ] **Handoff is HUMAN-controlled:** any cross-agent handoff is a manual artifact copy (operator), not
  an agent reading another agent's workspace.
- [ ] **No auto-promotion:** Official Wiki / memory / blueprint are never auto-updated; learning stays
  `candidate` until HUMAN confirms.
- [ ] **MOCK clarity:** every produced artifact is marked MOCK; the smoke run reviews fixtures, not real docs.
- [ ] **Scoped:** no build/refresh/consume, no wiki-meta generation, no consumer agents (J-2).

## Reference: a known-good full pass
The J-1 scoped E2E is a recorded full pass of C+D+E:
- DDR review run `RUN-20260621-1655-j1-e2e`, testcase review run `RUN-20260621-1657-j1-e2e`,
  PM run `RUN-20260621-1658-j1-e2e` (+ `/aiws-agent-feedback` on the PM run).
- See `docs/rollout/e2e_simulation_result.md` and `sample_project_package/expected_outputs/`.
