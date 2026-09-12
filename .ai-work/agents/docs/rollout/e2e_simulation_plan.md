# Scoped E2E Simulation Plan — AI Agents Pack (Phase J-1)

> **Status: HISTORICAL — point-in-time record, kept for provenance (formalized by CR-AIWS-2026-08-036).** Không phản ánh trạng thái hiện tại — xem `PACK_VERSION.md` + `docs/rollout/known_limitations_and_backlog.md`. Built by AIP-EXEC-141 (Phase J-1) STEP-01. Writes only under
> the pack root.
>
> **SCOPE = SCOPED E2E (review + PM ONLY).** This is **NOT** the full build/refresh/consume
> cross-pack E2E. Scenarios 1 (build) / 2 (refresh) and the wiki-meta parts of Scenario 3 (consume) —
> which need generated wiki-meta + the wiki-consumer agents — are **DEFERRED to round J-2** (see
> `known_limitations_and_backlog.md`). J-1 exercises only the **3 currently-built priority agents**
> (`aiws_detailed_design_review_agent`, `aiws_testcase_review_agent`, `aiws_pm_agent`) over the **existing Knowledge
> Hub** + **reused EXEC-139 MOCK fixtures**.
>
> **ALL FIXTURES + EVIDENCE = MOCK.** This proves the *mechanism* (chained review→review→PM flow over
> the runtime commands), not a review of any real document.

## 1. Objective

Design + run one chained, end-to-end scenario across the 3 priority agents, dogfooding the
**runtime command set** (`/aiws-agent-run`, `/aiws-agent-feedback`; created by EXEC-142) and the
existing `/aiws-agent-create` / `/aiws-agent-review-learning` commands:

```
DDR review  →(handoff: findings)→  testcase review  →(handoff: both reviews)→  PM track/plan
```

Each leg is a real run started by `py tooling/run_agent.py start <instance>`,
which materializes an **Active Run Context (ARC)**; the AI then **acts as that agent**, writes
`output/`, captures a learning **candidate** (`status=candidate`), sets `run_state.yaml`
`status=completed`, and the run reconciles into `completed_runs/`.

## 2. Guardrails honored (mark EVERYWHERE)

| Guardrail | How this plan honors it |
|---|---|
| **Scoped E2E = review + PM only** | Only the 3 priority agents run; no build/refresh/consume; no wiki-meta generation; no wiki-consumer agents. Marked in every artifact. |
| **All fixtures/evidence = MOCK** | Inputs reuse EXEC-139 `mock_fixtures/` (synthetic, defect-seeded). Every output header says MOCK. |
| **Coordinator no auto-run** | The coordinator agent is NOT invoked. No agent dispatches/triggers another. `run_agent.py` only prepares state; the AI does each leg HUMAN-prompted. |
| **Handoff = HUMAN-controlled artifact-passing** | Between legs, the upstream agent's `output/` is copied (by the operator, manually) into the downstream run as an input artifact. No agent reads another's workspace autonomously; no auto-chain. Recorded in the handoff note. |
| **Learning candidate `status=candidate`** | Each leg emits ≥1 candidate to `learning_candidates.jsonl`; none auto-confirmed. `/aiws-agent-review-learning` would surface them (not run here). |
| **No auto-promotion** | Outputs = evidence; nothing written to Official Wiki / memory / blueprint. |
| **No write to Official Wiki / memory / blueprint** | All writes land in the instance `workspace/` (run-folders) + `docs/rollout/`. `confirmed_memory.jsonl` untouched. |

## 3. Instances under test (existing, EXEC-139)

| Leg | Instance | Blueprint | Role (non_responsibilities reminder) |
|---|---|---|---|
| 1 | `detailed_design_review_agent__sample_project` | `aiws_detailed_design_review_agent` | Review/advisory only — finds gaps; does NOT approve/edit/auto-promote. |
| 2 | `testcase_review_agent__sample_project` | `aiws_testcase_review_agent` | Review/advisory only — coverage/trace findings; does NOT approve test cases. |
| 3 | `pm_agent__sample_project` | `aiws_pm_agent` | Planning/advisory only — proposes breakdown + HUMAN decision points; does NOT decide/execute/dispatch. |

## 4. MOCK fixtures reused (from EXEC-139 runs)

- **DDR leg inputs** (from `…/detailed_design_review_agent__sample_project/workspace/completed_runs/RUN-20260621-0001-mock-design/mock_fixtures/`):
  `mock_detailed_design_order_cancel.md` (target), `mock_requirements_order_cancel.md`,
  `mock_basic_design_order_cancel.md`.
- **Testcase leg inputs** (from `…/testcase_review_agent__sample_project/workspace/completed_runs/RUN-20260621-0001-mock-testcase/input/`):
  `MOCK_testcases_login.md` (target), `MOCK_requirements_login.md`, `MOCK_basic_design_login.md`.
- **Existing Knowledge Hub**: consulted Wiki-first (no seed entry exists for these mock features →
  documented grounding gap, review continues against source — Wiki-first NOT Wiki-only).

> Note on the two feature areas: the EXEC-139 fixtures cover two different mock features (order-cancel
> for DDR; login for testcase). For a single coherent E2E narrative the J-1 chain treats them as **one
> mock sample-project release** ("Sample Project release candidate") whose design + test artifacts are
> both under review; the PM leg then plans the combined remediation backlog from both review outputs.
> This keeps the handoff realistic without inventing new fixtures.

## 5. Chained scenario (single E2E run = 3 legs)

### Leg 1 — Detailed Design Review (DDR)
- `run_agent.py start detailed_design_review_agent__sample_project --task "MOCK J-1 E2E: review the mock order-cancel detailed design vs requirements/basic-design; emit findings for PM handoff" --slug j1-e2e`
- AI reads ARC → acts as DDR agent → writes `output/review_report.md` (+ summary) → captures candidate.
- **Handoff out**: `review_report.md` findings table → becomes an input artifact for the PM leg.

### Leg 2 — Test Case Review
- `run_agent.py start testcase_review_agent__sample_project --task "MOCK J-1 E2E: review the mock login test cases for coverage/trace vs requirements/basic-design; emit findings for PM handoff" --slug j1-e2e`
- AI reads ARC → acts as testcase agent → writes `output/review_report.md` (+ summary) → captures candidate.
- **Handoff in**: none required from Leg 1 (independent review lens); **Handoff out**: findings → PM leg.

> The two review legs are independent review lenses on the same release; neither agent reads the
> other's workspace. The HUMAN/operator passes both review outputs forward to the PM leg as artifacts.

### Leg 3 — PM track/plan
- `run_agent.py start pm_agent__sample_project --task "MOCK J-1 E2E: from the DDR + testcase review findings, produce a remediation task breakdown + risk/decision points for the Sample Project release" --slug j1-e2e`
- **Handoff in**: copies of both review reports placed in the PM run-folder (e.g. `input/` or referenced
  by relative path) — HUMAN-controlled artifact-passing.
- AI reads ARC → acts as PM agent → writes `output/task_breakdown.md` (proposed remediation backlog +
  HUMAN decision points + `decision_request`) → captures candidate.

## 6. Handoff chain (HUMAN-controlled, artifact-passing)

```
[Leg 1 DDR]  output/review_report.md (12 findings)
                         │  (operator copies findings forward — no auto-chain)
[Leg 2 TC ]  output/review_report.md (8 findings)
                         │  (operator copies BOTH review reports into PM run input)
[Leg 3 PM ]  output/task_breakdown.md (remediation backlog; proposals + decision_request)
```

A `handoff_note.md` records each pass: source run-id, artifact, destination run-id, who passed it
(HUMAN/operator), and confirmation that no agent auto-read another agent's workspace.

## 7. Commands exercised (dogfood target)

| Command | Where exercised |
|---|---|
| `/aiws-agent-run start` | 3× (one per leg) — this plan |
| `/aiws-agent-run status` | after each leg (reconcile active→completed) |
| `/aiws-agent-feedback` | on the chain (emits a candidate without auto-confirm) — see result doc |
| `/aiws-agent-review-learning` | exercised in `smoke_test_checklist.md` (surfaces candidates, no auto-confirm) |
| `/aiws-agent-create` | exercised in `smoke_test_checklist.md` (registry → new instance) |

## 8. Expected outputs of STEP-01

- 3 chained runs (review → review → PM) in the instances' `completed_runs/`, each with ARC,
  `run_state.yaml` (completed), `output/`, and a `learning_candidates.jsonl` candidate.
- `e2e_simulation_result.md` (what ran, run-ids, outputs, handoff chain, guardrails honored).
- `issue_warning_list.md` (any defect observed; small staging fixes only — no agent re-scope).
- `handoff_note.md` recording the HUMAN-controlled artifact passes.

## 9. Done = scoped, not full

This plan proves the **review→review→PM mechanism** end to end on MOCK inputs over the existing Hub.
It does **not** prove the full pack (build/refresh/consume pipelines, wiki-meta generation, coordinator
orchestration, wiki-consumer agents) — those are **J-2**. Reader must not conclude the pack is complete.
