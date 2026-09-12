# Scoped E2E Simulation Result — AI Agents Pack (Phase J-1)

> **Status: HISTORICAL — point-in-time record, kept for provenance (formalized by CR-AIWS-2026-08-036).** Không phản ánh trạng thái hiện tại — xem `PACK_VERSION.md` + `docs/rollout/known_limitations_and_backlog.md`. Built by AIP-EXEC-141 (Phase J-1) STEP-01.
>
> **SCOPE = SCOPED E2E (review + PM ONLY).** This is **NOT** the full build/refresh/consume cross-pack
> E2E (that is **DEFERRED to round J-2** — see `known_limitations_and_backlog.md`). All fixtures + run
> evidence are **MOCK**. Plan: `e2e_simulation_plan.md`.

## 1. What ran

One chained scenario across the 3 currently-built priority agents, each leg a real run started by the
runtime tooling (`run_agent.py` / `/aiws-agent-run start`), dogfooded end to end:

```
DDR review  →(handoff)→  testcase review  →(handoff: both reviews)→  PM track/plan
```

| Leg | Instance | Run id | Started via | Output (in run-folder `output/`) | Learning candidates | run_state |
|---|---|---|---|---|---|---|
| 1 | `detailed_design_review_agent__sample_project` | `RUN-20260621-1655-j1-e2e` | `run_agent.py start … --slug j1-e2e` | `review_report.md` (11 findings, 4 Critical) | LC-001, LC-002 (`status=candidate`) | completed → `completed_runs/` |
| 2 | `testcase_review_agent__sample_project` | `RUN-20260621-1657-j1-e2e` | `run_agent.py start … --slug j1-e2e` | `review_report.md` (8 findings, 1 Critical, 1 conflict) | LC-001, LC-002 (`status=candidate`) | completed → `completed_runs/` |
| 3 | `pm_agent__sample_project` | `RUN-20260621-1658-j1-e2e` | `run_agent.py start … --slug j1-e2e` | `task_breakdown.md` (7-task remediation backlog + 5 HUMAN decisions + `decision_request`) | LC-001, LC-002 + LC-FB-001 (via feedback) (`status=candidate`) | completed → `completed_runs/` |

Each leg: `run_agent.py start` materialized the **ARC** (`00_active_run_context.md`) from
blueprint + instance context + (empty) confirmed memory + task; the AI read the ARC, **acted as the
agent**, wrote `output/` per the blueprint output templates, captured ≥1 learning candidate, set
`run_state.yaml status=completed`, and `run_agent.py status` reconciled the run into `completed_runs/`.

## 2. Commands exercised (all 4)

| Command | Exercised? | Where / evidence |
|---|---|---|
| `/aiws-agent-run start` | YES (×3) | 3 legs above — each created `active_runs/RUN-…-j1-e2e/` + ARC + `run_state.yaml` |
| `/aiws-agent-run status` | YES (×3) | reconciled each leg `active_runs/ → completed_runs/`; final list shows all `completed` |
| `/aiws-agent-feedback` | YES (×1) | on PM `RUN-20260621-1658-j1-e2e`: appended `human_feedback.md` + emitted LC-FB-001 (`status=candidate`) to BOTH the run-local `learning_candidates.jsonl` AND `training/candidate_queue.jsonl`; `confirmed_memory.jsonl` untouched |
| `/aiws-agent-review-learning` | exercised in `smoke_test_checklist.md` (surfaces candidates, no auto-confirm) | the feedback candidate sits in `pm_agent__sample_project/training/candidate_queue.jsonl` ready for it |
| `/aiws-agent-create` | exercised in `smoke_test_checklist.md` (registry → new instance) | — |

> `/aiws-agent-run resume` and `stop` were already dogfooded by EXEC-142 (see
> `…/detailed_design_review_agent__sample_project/workspace/completed_runs/RUN-20260621-1554-stop-demo`).
> This E2E used the single-shot happy path (no interruption), so resume was not needed here.

## 3. Handoff chain (HUMAN-controlled, artifact-passing)

Full record: `…/pm_agent__sample_project/workspace/handoff_artifacts/handoff_note_RUN-20260621-1658-j1-e2e.md`.

```
[DDR  RUN-…-1655]  review_report.md (findings) ─┐  HUMAN/operator copies artifact (no auto-chain)
[TC   RUN-…-1657]  review_report.md (findings) ─┤
                                                 └─► [PM RUN-…-1658]  input/HANDOFF_*.md → task_breakdown.md
```

- H-1: DDR findings → PM run `input/HANDOFF_ddr_review_report.md` (manual copy by operator).
- H-2: testcase findings → PM run `input/HANDOFF_testcase_review_report.md` (manual copy by operator).
- The PM leg planned only from the handed-in artifacts; it did NOT read the review workspaces and did
  NOT re-invoke the review agents (T7 re-review is owned by "review agents (HUMAN-invoked)").

## 4. Guardrails honored (verified)

| Guardrail | Verified by |
|---|---|
| Scoped E2E = review + PM only (NOT full build/refresh/consume) | only the 3 priority agents ran; coordinator + wiki-meta + consumer agents untouched; marked in every artifact |
| All fixtures/evidence MOCK | inputs reused EXEC-139 `mock_fixtures/`; every output header says MOCK |
| Coordinator no auto-run | `wiki_meta_strategy_coordinator__sample_project` had no new run; no agent dispatched another |
| Handoff = HUMAN-controlled artifact-passing | recorded in handoff note; PM `input/` holds copies, not workspace links |
| Learning candidate `status=candidate`, no auto-confirm | all `learning_candidates.jsonl` + `candidate_queue.jsonl` entries are `status=candidate` |
| No write to Official Wiki / memory / blueprint | all 3 `confirmed_memory.jsonl` = 0 bytes post-run (verified); blueprints unchanged; no `product/`/`.ai-work/` write |
| Run evidence in Instance Workspace | all runs sit in each instance's `completed_runs/` |
| Review = Wiki-first NOT Wiki-only + source verification | both review reports record the Wiki grounding gap and verify against MOCK source |
| PM = HUMAN decision points + no auto-execution | `task_breakdown.md` §10 + `decision_request: status=awaiting_human_decision`; `agent_will_not` lists dispatch |

## 5. Defects / issues observed

See `issue_warning_list.md`. Summary: no blocking runtime defect; the chain ran clean. A few small
staging observations (ergonomics + doc-consistency) were noted; none require re-scoping any agent.

## 6. Scoped, not full — reader caution

This result proves the **review → review → PM mechanism** end to end on MOCK inputs over the existing
Knowledge Hub. It does **NOT** prove the full pack: build / refresh / consume pipelines, wiki-meta
generation, coordinator orchestration, and the wiki-consumer agents are **DEFERRED to round J-2**. The
pack is **not** complete. See `known_limitations_and_backlog.md`.
