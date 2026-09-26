---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-012-STEP-03
task_id: TASK-20260926-exec-012
working_aip_ref: AIP-EXEC-012
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-012-simplify-agent-team-ui.md
active_step_id: STEP-03
active_step_title: Verify and review
source_aip: AIP-EXEC-012
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-012-simplify-agent-team-ui.md
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
  Simplify the Agent Team UI so it only shows the team's current mission and member list, removing mission/task creation controls and the task list from the interface.
- Final outcome (AIP Expected Outputs):
  - Updated Agent Team UI source files.
  - Updated focused UI tests where applicable.
  - Verification results recorded in the task workspace.
- Scope:
  - Identify the Agent Team UI components and their state/data dependencies.
  - Keep only current mission presentation and member-list presentation.
  - Remove or hide add-mission, add-task, and task-list UI affordances.
  - Update focused tests where present.
  **Out of Scope:**
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Inspect and map Agent Team UI  [upstream — done]
- STEP-02 — Implement mission-and-members-only UI  [upstream — done]
- STEP-03 — Verify and review  ◀ ACTIVE (step 4 of 4)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Updated Agent Team UI source files.
  - Updated focused UI tests where applicable.
  - Verification results recorded in the task workspace.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Removing visual controls must not accidentally break shared state or unrelated routes.
  - Preserve existing current-mission and member behavior.
  - Delegate bounded analysis, implementation, and review tasks according to teammate capability, with disjoint write scopes.
- **Known Open Points:**
  - No blocker identified; current-mission field selection follows the existing presentation unless the HUMAN specifies otherwise.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- Existing Agent Team UI implementation and focused tests, resolved during STEP-01.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Agent Team UI guidance | (none) | (none) | Focused lookup returned no relevant project UI specification | wiki:none |

## Workspace Actions
- Record verification evidence and final capture sweep summary.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Focused verification passes and AIWS task lint reports zero errors, or any remaining failure is reported with evidence.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Run focused tests/build checks and independently review that unwanted UI paths are absent without regressions to mission/member rendering.

## Recommended Mode
Reviewing

## Applicable Guidelines
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`

## Recommended Skills
- aiws-lint

## Inputs
- STEP-02 changes
- Relevant test/build commands

## Expected Outputs
- Test/lint results
- Review findings and any fixes

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Focused verification passes and AIWS task lint reports zero errors, or any remaining failure is reported with evidence.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Use a different teammate for review when practical.

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
- OUT-012-01-01 —  (draft)
- OUT-012-02-01 —  (draft)

## Capture Inbox References
- CAP-001 — Current mission selection policy (captured)
