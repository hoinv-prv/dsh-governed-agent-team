---
artifact_type: aip_exec
artifact_id: AIP-EXEC-010
title: "Repair DSH workflow structured-output failure diagnostics"
status: active
project: "dsh-governed-agent-team / DeepSeek Harness"
owner: "hoinv"
plan_source: "Direct HUMAN authorization in session"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260915-dsh-workflow-typed-failure-diagnostics
updated_at: 2026-09-15
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Repair DSH workflow structured-output failure diagnostics

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — Universal Gates áp dụng:
- **Gate U1** — STEP-00 records the HUMAN authorization already given in-session.
- **Gate U2** — input understanding is recorded below and expanded in workspace findings.
- **Gate U3** — runtime open points live in workspace `05_open_questions.md`.

## Objective
Diagnose and repair the DeepSeek Harness workflow structured-output path so a failed schema-bound child exposes deterministic typed diagnostics instead of collapsing to an unexplained `null`; add focused regression tests and documentation, then verify the exact package surface before any new council run.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: bounded cross-repository tooling defect with source and tests identified directly.
- Search/execution effect: inspect only the workflow runtime/host/tool packages and their existing tests/docs.
- Resolved references: DSH root `AGENTS.md`, `docs/architecture.md`, workflow runtime source and tests.
- Deferred lookups: none.
- Expansion allowed: yes, only when dependency tracing requires adjacent DSH package files.

## Execution Scope
### In Scope
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/` runtime/host contracts and tests.
- Adjacent workflow public types/tool documentation when required by the behavioral correction.
- Reproduction and regression tests for schema-bound child failures with typed diagnostics.
- Build/test verification of affected DSH packages.
- Minimal Typert-required unused parameter rename in `packages/experimental/wbs/src/index.ts:63` solely to unblock the affected host build.

### Out of Scope
- Product WBS build, selection, activation or execution.
- Manual repair of failed council reviewer envelopes.
- Provider-adapter changes unrelated to preserving child failure diagnostics.
- Changes to project Truth, Wiki canonical content, or mission controls.

## Expected Outputs
- Patched DSH workflow implementation that preserves typed child failure evidence for schema-bound agent calls.
- Regression tests covering completed-without-structured-output and failed-child cases.
- Updated affected DSH README/JSDoc contract.
- Workspace findings and verification evidence.

## Execution Input Package
### Plan Source
- HUMAN authorization: "Cho phép sửa council transport (Recommended)".

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| DSH workflow diagnostics knowledge | (none; lookup score below threshold) | `/home/hoinv/deepseek-harness/packages/workflow/` | Source-owned implementation evidence | wiki:none |

### Reference lookup
- Query `DSH workflow structured output diagnostics` returned no reliable project-specific route (top score 11); direct DSH source is the authoritative implementation evidence.

### Required Workspace Preconditions
- [ ] Workspace created.
- [ ] Active Step Context available.
- [ ] `05_open_questions.md` initialized.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| DSH workflow runtime | `agent()` deliberately maps ordinary child failures and missing structured output to bare `null`; caller loses reason needed for typed retry policy. | Fix should preserve existing null-compatible orchestration while adding an opt-in or companion diagnostic surface, unless tests prove a safe compatible enrichment. | Exact public shape must be derived from current workflow types/tests. | ✅ HUMAN authorized repair |
| Council run-035 evidence | Three schema-enforced agents returned null without typed reasons, preventing lawful retry classification. | Regression should reproduce the runtime branch, not council-specific policy. | Provider-side failure subtype may be present in child result and currently discarded. | ✅ |

## References to Read First
- `/home/hoinv/deepseek-harness/AGENTS.md`
- `/home/hoinv/deepseek-harness/docs/architecture.md`
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/src/runtime.ts`
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/src/types.ts`
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/tests/`

## Current Risks / Constraints
- Preserve workflow API compatibility unless an explicit tested additive contract is required.
- Follow DSH package instructions, documentation-with-code rule, and exact affected-package checks.
- No speculative council rerun until transport diagnostics are tested.
- Existing product goal remains paused; `execution.json` and WBS state are immutable in this task.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260915-dsh-workflow-typed-failure-diagnostics/05_open_questions.md`
- Exact additive diagnostic representation will be chosen from DSH current public types and tests; record any non-blocking assumption in the workspace.

## Workspace Execution Rule
All runtime evidence belongs in the task workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record the task scope, done definition and the HUMAN's explicit authorization.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- wiki:none — project wiki has no reliable DSH workflow transport entry.

Recommended Skills:
- (none)

Inputs:
- HUMAN authorization message
- This AIP

Expected Outputs:
- Workspace confirmation note with session evidence.

Done Condition:
HUMAN authorization and bounded task understanding are recorded.

Notes / Constraints:
- Authorization already exists in the current session; do not ask redundantly.

Workspace Actions:
- Record confirmation in `04_findings.md`.

### Step: STEP-01 — Reproduce and trace diagnostic loss
Objective:
Trace worker/runtime/host result types and create a focused failing regression test proving where typed evidence becomes null.

Recommended Mode:
Executing

Applicable Guidelines:
- `/home/hoinv/deepseek-harness/AGENTS.md`
- `/home/hoinv/deepseek-harness/docs/architecture.md`

Recommended Skills:
- (none)

Inputs:
- Workflow source, public types and tests.

Expected Outputs:
- Root-cause evidence and a failing focused test.

Done Condition:
A deterministic test reproduces loss of child stop reason/error or missing structured-output reason.

Notes / Constraints:
- Prefer the narrowest behaviorally complete contract change.

Workspace Actions:
- Record trace and failing test command/output.

### Step: STEP-02 — Implement typed workflow child diagnostics
Objective:
Implement the compatible diagnostic contract, update documentation/JSDoc, and make focused tests pass.

Recommended Mode:
Executing

Applicable Guidelines:
- `/home/hoinv/deepseek-harness/AGENTS.md`
- `/home/hoinv/deepseek-harness/docs/architecture.md`

Recommended Skills:
- (none)

Inputs:
- STEP-01 root cause and regression.

Expected Outputs:
- DSH source/test/documentation changes.

Done Condition:
Focused tests prove failed schema-bound child calls expose deterministic typed diagnostics without breaking successful structured results.

Notes / Constraints:
- Do not weaken schema validation or synthesize reviewer content.

Workspace Actions:
- Record changed files and contract decisions.

### Step: STEP-03 — Verify affected packages and council usability
Objective:
Run affected tests/typecheck/build, inspect the diff, and verify the new diagnostic is sufficient to classify retry eligibility without starting a council run.

Recommended Mode:
Verifying

Applicable Guidelines:
- `/home/hoinv/deepseek-harness/AGENTS.md`

Recommended Skills:
- (none)

Inputs:
- Patched DSH checkout.

Expected Outputs:
- Test/typecheck/build evidence and a council-consumption note.

Done Condition:
Affected gates pass and the diagnostic surface provides a stable machine-readable failure reason.

Notes / Constraints:
- Do not start or replace the existing Web GUI server.

Workspace Actions:
- Record exact commands and exit codes.

### Step: STEP-04 — Final capture and task lint
Objective:
Complete capture sweep, scoped AIWS lint and final handoff.

Recommended Mode:
Finalizing

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `.ai-work/procedural/wiki_candidate_capture_playbook.md`

Recommended Skills:
- `aiws-lint`

Inputs:
- All task diffs and workspace evidence.

Expected Outputs:
- Final output, capture disposition and lint evidence.

Done Condition:
Final capture sweep is recorded, scoped lint has zero errors, and outputs are presented.

Notes / Constraints:
- Historical warnings must be reported honestly.

Workspace Actions:
- Update `11_output_final.md`, findings and capture inbox.

## Done Criteria
- [ ] Gate U1 evidence recorded.
- [ ] Gate U2 input understanding verified against DSH source.
- [ ] Gate U3 open points resolved/deferred/rejected.
- [ ] Typed child-failure diagnostics are implemented and tested.
- [ ] Affected DSH docs and package gates pass.
- [ ] No mission/WBS runtime state changed.
- [ ] Final capture sweep and scoped lint completed.

## Self-check / Review Points
- Successful schema-bound agents still return their structured object unchanged.
- Child failure never becomes an unexplained null on the diagnostic-aware path.
- Failure evidence contains no untrusted synthesized classification.
- Tests cover both missing structured output and explicit child failure.
- Documentation matches actual public contract.

## Finalization Notes
- Do not resume council until the patch is verified in the active harness runtime or rebuilt artifacts as required.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Macro-scope/output changes require a dated Re-plan Log entry before editing earlier sections; runtime findings remain in the workspace.

## Re-plan Log

### 2026-09-16 — unblock affected Harness build verification
- Trigger: automatic continuation of the active HUMAN-approved WBS objective; the workflow transport patch cannot be activated or verified while the root host build stops at an unrelated one-token Typert naming violation in the experimental WBS service.
- Change: add the minimal parameter rename at `/home/hoinv/deepseek-harness/packages/experimental/wbs/src/index.ts:63` and rerun affected build/tests; no other experimental WBS behavior enters scope.
- Evidence ref: workspace `04_findings.md` STEP-03 build failure and `05_open_questions.md` OP-01.
- Approved by: active goal continuation authority; bounded prerequisite only.
