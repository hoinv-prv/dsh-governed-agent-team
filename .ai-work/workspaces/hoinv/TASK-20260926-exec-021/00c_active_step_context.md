---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-021-STEP-04
task_id: TASK-20260926-exec-021
working_aip_ref: AIP-EXEC-021
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-021-gat-baseline-sync-contract-freeze.md
active_step_id: STEP-04
active_step_title: Verify compatibility and prepare handoff
source_aip: AIP-EXEC-021
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-021-gat-baseline-sync-contract-freeze.md
step_id: STEP-04
step_index: 5
step_total: 5
status: active
active_task_lens: design_authoring
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Verify compatibility and prepare handoff

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Establish the current DSH experimental GAT implementation as the behavioral baseline, synchronize that baseline into the standalone GAT authoring/distribution repository without overwriting unrelated work, freeze the cross-repository contracts required by later member-binding execution packages, and prove compatibility with focused tests plus installer verification.
- Final outcome (AIP Expected Outputs):
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/04_findings.md` — source-authority map, exact delta inventory, preservation decisions and evidence.
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/07_output_draft.md` — synchronization and contract-freeze draft.
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/11_output_final.md` — compatibility results and EXEC-B/EXEC-C readiness handoff.
  - `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` — versioned semantic contracts and unresolved HUMAN decisions.
  - Bounded standalone package/test/profile/compatibility updates required to match the selected DSH behavioral baseline.
- Scope:
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/` — runtime evidence, diffs, decisions, verification logs and final handoff.
  - `packages/core/**`, `packages/tools/**`, `packages/profile/**`, `packages/web/**`, `packages/web-profile/**` — synchronize only demonstrated DSH experimental GAT baseline deltas.
  - `compatibility/**`, `installer/**`, root package/version manifests and relevant verification fixtures — update only when the synchronized package surface requires it.
  - `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — correct current-source mapping if synchronization changes its caveat.
  - `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` — create the approved EXEC-B/EXEC-C boundary contract.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Persist confirmed task understanding  [upstream — done]
- STEP-01 — Pin baselines and build exact delta inventory  [upstream — done]
- STEP-02 — Synchronize approved baseline deltas  [upstream — done]
- STEP-03 — Freeze member-binding integration contracts  [upstream — done]
- STEP-04 — Verify compatibility and prepare handoff  ◀ ACTIVE (step 5 of 5)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/04_findings.md` — source-authority map, exact delta inventory, preservation decisions and evidence.
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/07_output_draft.md` — synchronization and contract-freeze draft.
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/11_output_final.md` — compatibility results and EXEC-B/EXEC-C readiness handoff.
  - `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` — versioned semantic contracts and unresolved HUMAN decisions.
  - Bounded standalone package/test/profile/compatibility updates required to match the selected DSH behavioral baseline.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - The standalone working tree already has overlapping modifications; direct copy/rsync is prohibited.
  - DSH and standalone package names/imports/profile wiring may intentionally differ.
  - Generated artifacts and source artifacts must not be confused; source-of-truth file direction must be documented.
  - Installer compatibility remains strict for host preimages, installed bytes and post-build verification even when development source drift is allowed.
  - Contract freeze must not silently implement EXEC-B/EXEC-C behavior.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/05_open_questions.md`
  - Whether every DSH-side delta belongs in standalone, or some are host-only integration differences; resolve by evidence in STEP-01.
  - Exact event migration strategy and attachment size limits remain decision placeholders for later HUMAN review unless existing DSH conventions determine them.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `.ai-work/workspaces/hoinv/TASK-20260926-plan-001/04_findings.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-plan-001/11_output_final.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-core/`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT design reference | SRC-GAT-DESIGN-REFERENCE | `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` | Maintained reference; executable source/tests override | — |

## Workspace Actions
- Finalize `11_output_final.md`, close open points, triage captures and run scoped lint.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
No unexplained regression remains; failures are fixed or explicitly block readiness; task lint is reported truthfully.

## Active Task Lens
- design_authoring
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Run focused package tests/build/type checks, persistence/profile integration tests, installer structural checks and final AIWS lint; report real results and residual risks.

## Recommended Mode
Verification

## Applicable Guidelines
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`

## Recommended Skills
- `aiws-lint`

## Inputs
- STEP-02 changes.
- STEP-03 contract freeze.

## Expected Outputs
- Verification matrix with exact commands/results.
- Final handoff determining readiness for EXEC-B and EXEC-C.
- Deferred capture disposition.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
No unexplained regression remains; failures are fixed or explicitly block readiness; task lint is reported truthfully.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Do not activate a live profile.
- Separate structural install verification from post-build runtime/profile verification.

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
- OUT-021-01-01 —  (draft)
- OUT-021-02-01 —  (draft)
- OUT-021-03-01 —  (draft)

## Capture Inbox References
- CAP-021-01 — Current DSH GAT behavioral baseline is an uncommitted working-tree state (captured)
- CAP-021-02 — DSH GAT Web mount and component contracts drift (captured)
