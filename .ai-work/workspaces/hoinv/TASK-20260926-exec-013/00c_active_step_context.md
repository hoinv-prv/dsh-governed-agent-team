---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-013-STEP-03
task_id: TASK-20260926-exec-013
working_aip_ref: AIP-EXEC-013
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-013-restore-session-agent-team-toggle.md
active_step_id: STEP-03
active_step_title: Verify and review
source_aip: AIP-EXEC-013
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-013-restore-session-agent-team-toggle.md
step_id: STEP-03
step_index: 4
step_total: 4
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Verify and review

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Restore an explicit Enable/Disable Agent Team button in the conversation session UI. The toggle must apply to the current session only and must not mutate profile-level activation.
- Final outcome (AIP Expected Outputs):
  - Updated Agent Team UI and integration code for session-scoped enable/disable.
  - Focused tests covering initial state, enable, disable, and session isolation.
  - Verification and lint results in the task workspace.
- Scope:
  - Identify the current Agent Team session UI and available session-scoped state/action APIs.
  - Restore an accessible Enable/Disable control in the session header/panel.
  - Ensure the toggle is scoped to the active session and reflected in UI state.
  - Update focused tests and build verification.
  **Out of Scope:**
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm corrected task understanding (HARD GATE)  [upstream — done]
- STEP-01 — Trace session activation seam  [upstream — done]
- STEP-02 — Implement session Enable/Disable control  [upstream — done]
- STEP-03 — Verify and review  ◀ ACTIVE (step 4 of 4)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Updated Agent Team UI and integration code for session-scoped enable/disable.
  - Focused tests covering initial state, enable, disable, and session isolation.
  - Verification and lint results in the task workspace.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - The current composition may expose Agent Team only when the profile layer is installed; the button must not be confused with profile activation.
  - Session isolation must be tested explicitly when switching between conversations.
  - Preserve the mission/member-only presentation from AIP-EXEC-012 except for the restored toggle.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-013/05_open_questions.md`
  - Exact host-side session activation seam: resolve in STEP-01; if absent, stop and ask HUMAN before inventing a new backend contract.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- `packages/web/src/client/TeamAction.tsx`
- `packages/web/src/client/mount.ts`
- `packages/web/tests/team-action.client.spec.tsx`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Agent Team session UI guidance | (none) | (none) | Lookup and semantic escalation found no relevant project UI guidance | wiki:none |

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Focused verification passes and task lint reports zero errors, or remaining failures are reported with evidence.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Run focused tests, build checks, and AIWS lint; review for session isolation and regression of current mission/member UI.

## Recommended Mode
Reviewing

## Applicable Guidelines
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`
- wiki:none

## Recommended Skills
- ...

## Inputs
- STEP-02 changes and workspace evidence.

## Expected Outputs
- Focused test/build results, review findings, and final capture sweep summary.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Focused verification passes and task lint reports zero errors, or remaining failures are reported with evidence.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
Do not claim completion if the session-scoped seam remains unresolved.

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
- OUT-013-02-01 —  (draft)
