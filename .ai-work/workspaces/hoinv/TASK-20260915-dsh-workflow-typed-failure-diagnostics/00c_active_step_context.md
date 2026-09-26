---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260915-dsh-workflow-typed-failure-diagnostics-STEP-03
task_id: TASK-20260915-dsh-workflow-typed-failure-diagnostics
working_aip_ref: AIP-EXEC-010
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-010-dsh-workflow-typed-failure-diagnostics.md
active_step_id: STEP-03
active_step_title: Verify affected packages and council usability
source_aip: AIP-EXEC-010
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-010-dsh-workflow-typed-failure-diagnostics.md
step_id: STEP-03
step_index: 4
step_total: 5
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-16
---

# Active Step Context — Verify affected packages and council usability

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Diagnose and repair the DeepSeek Harness workflow structured-output path so a failed schema-bound child exposes deterministic typed diagnostics instead of collapsing to an unexplained `null`; add focused regression tests and documentation, then verify the exact package surface before any new council run.
- Final outcome (AIP Expected Outputs):
  - Patched DSH workflow implementation that preserves typed child failure evidence for schema-bound agent calls.
  - Regression tests covering completed-without-structured-output and failed-child cases.
  - Updated affected DSH README/JSDoc contract.
  - Workspace findings and verification evidence.
- Scope:
  - `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/` runtime/host contracts and tests.
  - Adjacent workflow public types/tool documentation when required by the behavioral correction.
  - Reproduction and regression tests for schema-bound child failures with typed diagnostics.
  - Build/test verification of affected DSH packages.
  **Out of Scope:**
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Reproduce and trace diagnostic loss  [upstream — done]
- STEP-02 — Implement typed workflow child diagnostics  [upstream — done]
- STEP-03 — Verify affected packages and council usability  ◀ ACTIVE (step 4 of 5)
- STEP-04 — Final capture and task lint  [downstream]

## Downstream / Output Contract
- Next step (STEP-04 — Final capture and task lint) needs as Inputs:
  - All task diffs and workspace evidence.
- Shape this step's output to satisfy the above + the AIP final outcome (see AIP Goal & Outcome).

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Preserve workflow API compatibility unless an explicit tested additive contract is required.
  - Follow DSH package instructions, documentation-with-code rule, and exact affected-package checks.
  - No speculative council rerun until transport diagnostics are tested.
  - Existing product goal remains paused; `execution.json` and WBS state are immutable in this task.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/TASK-20260915-dsh-workflow-typed-failure-diagnostics/05_open_questions.md`
  - Exact additive diagnostic representation will be chosen from DSH current public types and tests; record any non-blocking assumption in the workspace.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `/home/hoinv/deepseek-harness/AGENTS.md`
- `/home/hoinv/deepseek-harness/docs/architecture.md`
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/src/runtime.ts`
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/src/types.ts`
- `/home/hoinv/deepseek-harness/packages/workflow/workflow-worker-thread/tests/`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| DSH workflow diagnostics knowledge | (none; lookup score below threshold) | `/home/hoinv/deepseek-harness/packages/workflow/` | Source-owned implementation evidence | wiki:none |

## Workspace Actions
- Record exact commands and exit codes.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Run affected tests/typecheck/build, inspect the diff, and verify the new diagnostic is sufficient to classify retry eligibility without starting a council run.

## Recommended Mode
Verifying

## Applicable Guidelines
- `/home/hoinv/deepseek-harness/AGENTS.md`

## Recommended Skills
- (none)

## Inputs
- Patched DSH checkout.

## Expected Outputs
- Test/typecheck/build evidence and a council-consumption note.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Affected gates pass and the diagnostic surface provides a stable machine-readable failure reason.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Do not start or replace the existing Web GUI server.

## Operating Memory (L2 — bài học vận hành)
- Lát cắt: mọi nhóm (step không khai Kind)
- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical (`.ai-work/procedural/operating_memory.md`).
- (Operating Memory trống — chưa có mục nào)

## Coverage
**Coverage Gaps:**
- Step Output / Decision Persistence Requirements (trimmed → spec §7.2)
- Source Verification Requirements (trimmed → spec §5)
- No expected outputs declared (inherited from AIP)

## Previous Step Results / Handoff Inputs
- OUT-010-01-01 —  (draft)
- OUT-010-02-01 —  (draft)

## Capture Inbox References
- ? — DSH tool-workflow tests can fail before test logic because scripts/test-invariants.ts observes FiberState as undefined in the current dirty checkout; distinguish this environment/baseline fault from feature regression and retain the exact stack. (captured)
- ? — Fan-out combinators may intentionally map ordinary child failures to null, but the enclosing result must retain typed per-child diagnostics or governance callers cannot establish retry eligibility without inventing evidence. (captured)
