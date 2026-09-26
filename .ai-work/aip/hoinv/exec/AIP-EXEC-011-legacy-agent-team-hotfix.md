---
artifact_type: aip_exec
artifact_id: AIP-EXEC-011
title: "Legacy Agent Team readiness and Chat Plan import hotfix"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: wbs-runs/legacy-agent-team-hotfix/wbs.v9.json
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix
updated_at: 2026-09-13
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Legacy Agent Team readiness and Chat Plan import hotfix

## SOP Compliance
- Gate U1 Confirm-understanding-of-task is STEP-00.
- Gate U2 input understanding is recorded below and verified in the task workspace.
- Gate U3 open points live in the task workspace.

## Objective
Hotfix the legacy `packages/core`, `packages/tools`, and `packages/web` plugin so a Lead-only Team can execute after plan approval and one Approve Plan action imports missing tasks from the latest HUMAN-approved DSH Chat Plan `## Tasks` section before approving the exact resulting Team plan revision.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: bounded product hotfix with explicit HUMAN decisions and direct source/API evidence.
- Search/execution effect: prioritize current legacy plugin source, DSH plan-mode event contract, focused tests, and canonical installed-worktree verification.
- Resolved references: `AGENTS.md`; DSH plan-mode source inspected after wiki lookup miss; WBS candidate and direct HUMAN decisions.
- Deferred lookups: none.
- Expansion allowed: only inside approved WBS read scope when correctness requires it.

## Execution Scope
### In Scope
- Default minimum durable teammates becomes zero; Lead-only operation is allowed.
- Configurable maximum teammate cap and Team plan approval gate remain enforced.
- Latest successful HUMAN-approved `exit_plan_mode` call/result pairing is read deterministically from the Lead Session log.
- Only checklist/bullet/numbered items in a `## Tasks` section are imported.
- Existing Team tasks are preserved; only normalized missing tasks are added.
- Import and exact post-import approval are exposed as one Web action with localized fail-closed errors.
- Focused static review and canonical installed-worktree verification.

### Out of Scope
- `packages/gat` Conservative MVP work and the separately owned `multi-mission-web-ui` revision-32 mission.
- Arbitrary free-form chat parsing or AI-based task extraction.
- Removing the configurable maximum teammate cap.
- Live Web profile activation or server restart.
- AIWS Truth/Wiki/procedural/tooling modification.

## Expected Outputs
- Hotfixed legacy source and focused tests in `packages/tools`, `packages/core`, and `packages/web`.
- New mission evidence under `wbs-runs/legacy-agent-team-hotfix`.
- Canonical installed-worktree verification report.
- Independent task/final reviews and explicit HUMAN acceptance.

## Execution Input Package
### Plan Source
- `wbs-runs/legacy-agent-team-hotfix/wbs.v9.json`

### Required Truth Inputs
- `AGENTS.md`
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Legacy GAT plan integration | (none) | `packages/core`, `packages/tools`, `packages/web` | Project wiki lookup and semantic retry found no relevant DSH plan/task contract. | wiki:none |

### Reference lookup
- Wiki lookup query: `DSH conversation plan tasks approval`; semantic retry completed with no relevant project source.
- Raw source evidence: `/home/hoinv/deepseek-harness/packages/plan/plan-mode/src/index.ts` shows approved plan content is markdown carried by `exit_plan_mode`.

### Required Workspace Preconditions
- Workspace created as `TASK-20260913-legacy-agent-team-hotfix` after WBS approval.
- Active Step Context available before product mutation.
- Open-points and capture files initialized.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN hotfix decision | Lead-only Team is valid; Approve Plan imports and merges tasks first. | Maximum cap remains configurable. | None. | ✅ via `solo-team` / `plan-task-source` / `existing-tasks` / `plan-markdown-contract` answers |
| DSH plan-mode source | Approved plan is markdown in `exit_plan_mode` call arguments; projection has no task schema. | Successful paired result identifies HUMAN approval. | Exact pairing/parser must fail closed and be independently reviewed. | ✅ deterministic `## Tasks` contract selected |

## References to Read First
- `AGENTS.md`
- `wbs-runs/legacy-agent-team-hotfix/wbs.v9.json`
- `packages/tools/src/index.ts`
- `packages/core/src/index.ts`
- `packages/core/src/task-board.ts`
- `packages/web/src/client/TeamAction.tsx`
- `/home/hoinv/deepseek-harness/packages/plan/plan-mode/src/index.ts`

## Current Risks / Constraints
- Another coordinator owns the distinct revision-32 `multi-mission-web-ui` mission and `packages/gat`; this AIP must never mutate its controls or package scope.
- Session-event parsing must distinguish successful approval from rejection/incomplete calls.
- Merge/dedupe and approval revision must be atomic or fail closed with preserved existing tasks.
- Runtime/build proof is deferred to the canonical verifier.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/05_open_questions.md`
- No unresolved product decision; exact source design remains subject to independent review.

## Workspace Execution Rule
Runtime findings, decisions, metrics, drafts, capture candidates, and open points live in the task workspace, never in this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Hotfix Understanding (HARD GATE)
Objective:
Record the separate legacy-plugin mission boundary and HUMAN-confirmed semantics, then obtain/retain explicit WBS approval before product mutation.

Recommended Mode:
Clarifying

Applicable Guidelines:
- wiki:none
- `AGENTS.md`

Recommended Skills:
- dsh-wbs-build
- dsh-wbs-run

Inputs:
- Direct HUMAN hotfix decisions
- `wbs-runs/legacy-agent-team-hotfix/wbs.v9.json`

Expected Outputs:
- Workspace understanding note
- Exact WBS revision/hash approval evidence

Done Condition:
The HUMAN approves the exact WBS and confirms this mission remains separate from revision-32 `packages/gat` work.

Notes / Constraints:
- Do not touch the other mission's control files.

Workspace Actions:
- Record decisions and ownership boundary.

### Step: STEP-01 — Allow Lead-only Team Execution
Objective:
Update tools readiness/config/prompt/tests so zero durable teammates is valid while plan approval and max cap remain mandatory.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none
- `AGENTS.md`

Recommended Skills:
- (none)

Inputs:
- `packages/tools`
- Approved WBS

Expected Outputs:
- Tools hotfix and focused tests
- Independent static review evidence

Done Condition:
Fresh independent review finds no authorization or max-cap regression.

Notes / Constraints:
- No command-based verification outside the integration step.

Workspace Actions:
- Record hashes, attempt, findings, and review.

### Step: STEP-02 — Import Chat Plan Tasks and Approve
Objective:
Implement deterministic latest-approved-plan extraction, `## Tasks` parsing, merge-only-missing behavior, exact post-import approval, Web wiring/localization, and focused tests.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none
- `AGENTS.md`

Recommended Skills:
- (none)

Inputs:
- `packages/core`
- `packages/web`
- DSH plan-mode event contract

Expected Outputs:
- Core/Web hotfix and focused tests
- Independent static review evidence

Done Condition:
Fresh review validates successful call/result pairing, fail-closed parser, dedupe/merge, revision correctness, Web flow, and legacy preservation.

Notes / Constraints:
- Never parse arbitrary chat or content outside `## Tasks`.

Workspace Actions:
- Record hashes, attempt, findings, and review.

### Step: STEP-03 — Canonical Installed-worktree Verification
Objective:
Regenerate, install, and run the canonical verifier against the dedicated DSH worktree.

Recommended Mode:
Verifying

Applicable Guidelines:
- wiki:none
- `AGENTS.md`

Recommended Skills:
- (none)

Inputs:
- Accepted hotfix bytes and reviews
- Installer, compatibility generator, verifier, dedicated worktree

Expected Outputs:
- Updated compatibility artifacts
- `wbs-runs/legacy-agent-team-hotfix/integration.md`

Done Condition:
Declared reset/clean/regenerate/install/verify sequence exits 0 and required focused/build/smoke stages pass.

Notes / Constraints:
- Stop on first failure; no unapproved rerun.

Workspace Actions:
- Record command outputs, hashes, and limitations.

### Step: STEP-04 — Final Review, Acceptance, and Close
Objective:
Produce the final evidence report, run scoped AIWS lint, obtain independent review and explicit HUMAN acceptance, disposition capture candidates, and close the AIP.

Recommended Mode:
Reviewing

Applicable Guidelines:
- wiki:none
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

Recommended Skills:
- aiws-lint

Inputs:
- `wbs-runs/legacy-agent-team-hotfix/integration.md`
- `wbs-runs/legacy-agent-team-hotfix/execution.json`
- `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/04_findings.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/05_open_questions.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/08_capture_inbox.jsonl`
- `wbs-runs/legacy-agent-team-hotfix/evidence`

Expected Outputs:
- `wbs-runs/legacy-agent-team-hotfix/final-report.md`
- Independent final verdict
- HUMAN acceptance and closed AIP

Done Condition:
All requirements map to evidence, scoped lint is clean, HUMAN accepts exact final report, captures are explicitly triaged, and AIP is done.

Notes / Constraints:
- Waiting for HUMAN is not completion.

Workspace Actions:
- Final capture/open-point sweep and closure evidence.

## Done Criteria
- [ ] Exact WBS is HUMAN-approved and other mission ownership is not disturbed.
- [ ] Lead-only Team execution works without weakening plan approval or maximum cap.
- [ ] One Approve Plan action deterministically merges latest approved `## Tasks` items and approves exact resulting revision.
- [ ] Canonical verifier passes focused tests, full build, built-library smoke, and dashboard smoke.
- [ ] Independent reviews, scoped lint, HUMAN acceptance, capture triage, and AIP close are complete.

## Self-check / Review Points
- Verify latest successful call/result pairing and reject stale/rejected/incomplete plan calls.
- Verify parser is section-bounded and deterministic.
- Verify merge preserves existing tasks and exact revision accounting.
- Verify Team execution still requires current plan approval.
- Verify no file under `packages/gat` or `wbs-runs/multi-mission-web-ui` is mutated.

## Finalization Notes
- Live profile activation is explicitly excluded.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Any change to scope, parser contract, authorization semantics, external effects, or acceptance requires a dated Re-plan Log entry and reviewed WBS revision before work.

## Re-plan Log
### 2026-09-13 — Lead-only default recovery allowance
- Trigger: attempts 1–2 exposed two distinct default-path defects: schema default remained 2, then runtime `apply` fallback remained 2.
- Change: candidate WBS revision 2 preserves scope and acceptance while raising the Lead-only task ceiling from 2 to 3 attempts and cumulative mission ceiling from 8 to 9 attempts / 630 minutes.
- Evidence ref: independent recovery review `390d690a-d097-4f93-bd13-fe6fb0b37874`; `wbs-runs/legacy-agent-team-hotfix/review.v2.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v2`, exact SHA-256 `733c8ae628f1076b49499b4bb10017fd9b8cde0013071bf89067636d0683f5d5`.

### 2026-09-13 — Legacy expectation recovery allowance
- Trigger: attempt 3 corrected schema and runtime defaults, but independent review found an existing test still implicitly depended on the old default of 2; coordinator inspection found a second such test.
- Change: candidate WBS revision 3 preserves scope and acceptance while raising the Lead-only task ceiling from 3 to 4 attempts and cumulative ceiling from 9 to 10 attempts / 660 minutes.
- Evidence ref: independent review `74872b4f-96f0-40fc-ad82-33cdd1a04ca1`; `wbs-runs/legacy-agent-team-hotfix/review.v3.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v3`, exact SHA-256 `62b39c67c0597e4851519ce91867d68a18395fcc460556299f000e00ce5b7b27`.

### 2026-09-13 — Complete implicit-default test recovery
- Trigger: attempt 4 corrected two old-default-dependent tests, but whole-file review found one remaining complete-envelope test with an implicit required count of 2.
- Change: candidate WBS revision 4 preserves scope and acceptance while raising the Lead-only task ceiling from 4 to 5 attempts and cumulative ceiling from 10 to 11 attempts / 690 minutes.
- Evidence ref: independent whole-file review `b44a1c87-219a-4785-8061-73a69f052339`; `wbs-runs/legacy-agent-team-hotfix/review.v4.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v4`, exact SHA-256 `6998784540c089965201296def7960802ad75691264a6920f60450184892f92e`.

### 2026-09-13 — Canonical verifier expectation recovery
- Trigger: integration attempt 1 passed reset/clean/regeneration/install, then focused tests reported two stale expected substrings after the intentionally approval-aware readiness wording change.
- Change: candidate WBS revision 5 preserves product behavior and all downstream checks while adding one Lead-only test-recovery attempt; cumulative ceiling becomes 12 attempts / 720 minutes. Integration attempt 1 remains charged and failed; attempt 2 remains the sole canonical rerun.
- Evidence ref: `wbs-runs/legacy-agent-team-hotfix/integration.md`; `wbs-runs/legacy-agent-team-hotfix/review.v5.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v5`, exact SHA-256 `45154051e1a231a175ce9a1eeee0e9af15ae582a232e31ab01a3207d3574b189`.

### 2026-09-13 — Built-library descriptor recovery
- Trigger: integration attempt 2 passed all 164 focused tests and the full host/client build, then the built-library smoke found its expected method list omitted already-present mission Remote methods.
- Change: candidate WBS revision 6 adds one plan-import test-recovery attempt and one integration attempt; cumulative ceiling becomes 14 attempts / 840 minutes. Both prior integration attempts remain charged and failed.
- Evidence ref: `wbs-runs/legacy-agent-team-hotfix/integration.md`; `wbs-runs/legacy-agent-team-hotfix/review.v6.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v6`, exact SHA-256 `07a175111b15d1e79874c4a6f874bab8fb9365e803584f9f3492328669e12bf9`.

### 2026-09-13 — Assembled dashboard golden recovery
- Trigger: integration attempt 3 passed focused tests, full build, and built-library smoke, then the final dashboard smoke found `verification/web/task.expected.md` omitted the already-present empty Missions section.
- Change: candidate WBS revision 7 expands integration write scope only to that golden file and adds one integration attempt; cumulative ceiling becomes 15 attempts / 930 minutes. All three prior integration attempts remain charged and failed.
- Evidence ref: `wbs-runs/legacy-agent-team-hotfix/integration.md`; `wbs-runs/legacy-agent-team-hotfix/review.v7.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v7`, exact SHA-256 `67dc8367df9a0b66770c3faa81b9c7a3795e9217c93edb98c50db355ef36000c`.

### 2026-09-13 — Current-byte golden and durable-evidence recovery
- Trigger: final-review attempt 1 found current English approval copy contradicts the dashboard golden and that raw verifier/review evidence plus workspace output metadata were not durably resolvable.
- Change: candidate WBS revision 8 corrects the exact approval-label golden, persists the next verifier output, records durable review summaries/reconciled workspace outputs, and adds one integration plus one final-review attempt; cumulative ceiling becomes 17 attempts / 1050 minutes.
- Evidence ref: final review `92b95a8c-48ba-47b9-96bf-574707863174`; `wbs-runs/legacy-agent-team-hotfix/review.v8.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v8-retry`, exact SHA-256 `bd90415f5a4c6d268b9326a86088bee26e24856349a3908ee5d0bbe6b9c9a288`.

### 2026-09-13 — Runtime-observed approval copy alignment
- Trigger: integration attempt 5 durably proved the assembled runtime still renders `Approve current plan`; the revision-8 golden-only hypothesis was false although all earlier stages passed.
- Change: candidate WBS revision 9 aligns the English source copy and golden to the repeatedly observed runtime without changing one-action import behavior, then adds one import recovery and one integration attempt; cumulative ceiling becomes 19 attempts / 1170 minutes.
- Evidence ref: `wbs-runs/legacy-agent-team-hotfix/evidence/integration-verification/attempt-integration-005/verifier.log`; `wbs-runs/legacy-agent-team-hotfix/review.v9.md`.
- Approved by: HUMAN via `ask_user_question:approve-legacy-hotfix-v9`, exact SHA-256 `79ea97523df2124db54b05eb82bdf6ef2de0244543fe71fb121d53dc87848b71`.

