---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-017-STEP-03
task_id: TASK-20260926-exec-017
working_aip_ref: AIP-EXEC-017
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-017-restrict-subagents-to-enabled-team.md
active_step_id: STEP-03
active_step_title: Add and Run Regression Tests
source_aip: AIP-EXEC-017
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-017-restrict-subagents-to-enabled-team.md
step_id: STEP-03
step_index: 4
step_total: 4
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Add and Run Regression Tests

## AIP Goal & Outcome
- Goal (AIP-level objective):
  When Agent Team is enabled for a session, prevent that session from spawning or forking sub-agents outside the governed team, while preserving normal sub-agent behavior for sessions where Agent Team is disabled. If a needed skill or capability is absent, require HUMAN approval, add the approved member to the team, and only then assign the task to that member.
- Final outcome (AIP Expected Outputs):
  - Source changes under `packages/` implementing session-scoped admission and HUMAN-approved member-add guidance.
  - Automated tests covering denied external delegation, capability-gap guidance, and allowed team/solo behavior.
  - Verified build/test/lint results.
- Scope:
  - Identify the common admission point for ordinary sub-agent spawn/fork.
  - Enforce session-scoped denial when Agent Team is enabled.
  - Keep Agent Team teammate creation functional.
  - Provide actionable denial guidance: request HUMAN approval, add the required member, then assign the task.
  - Add regression tests for enabled and disabled sessions and the capability-gap guidance.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Inspect Admission Paths and Design Guard  [upstream — done]
- STEP-02 — Implement Session-Scoped Team Exclusivity  [upstream — done]
- STEP-03 — Add and Run Regression Tests  ◀ ACTIVE (step 4 of 4)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Source changes under `packages/` implementing session-scoped admission and HUMAN-approved member-add guidance.
  - Automated tests covering denied external delegation, capability-gap guidance, and allowed team/solo behavior.
  - Verified build/test/lint results.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Working tree contains substantial pre-existing HUMAN changes; do not overwrite or revert them.
  - Guard must not block `spawn_teammate` itself.
  - Enforcement should be runtime/session scoped, not a global static disable.
- **Known Open Points:**
  - None at creation; implementation details will be recorded in workspace findings if needed.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `packages/profile/src/index.ts`
- `packages/core/src/index.ts`
- `packages/core/src/roster.ts`
- `packages/tools/src/index.ts`
- Related package tests.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT runtime guidance | (none) | `packages/` | Project implementation is not registered in the wiki; lookup and semantic retry returned no relevant source. | wiki:none |

## Workspace Actions
- Record commands and outcomes.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Affected tests and type/build checks pass, or any external blocker is reported precisely.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Add focused tests and run affected package checks.

## Recommended Mode
Executing

## Applicable Guidelines
- wiki:none

## Recommended Skills
- (none)

## Inputs
- Implemented guard and existing test harness.

## Expected Outputs
- Tests for enabled-team denial, solo-session allowance, and teammate allowance.
- Test/build/lint evidence.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Affected tests and type/build checks pass, or any external blocker is reported precisely.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Prefer targeted tests before broader package verification.

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
- OUT-017-01-01 —  (draft)
- OUT-017-02-01 —  (draft)

## Capture Inbox References
- CAP-001 — Document Agent Team exclusive delegation boundary (captured)
