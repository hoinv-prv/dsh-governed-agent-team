---
artifact_type: aip_exec
artifact_id: AIP-EXEC-013
title: "Restore session Agent Team enable/disable toggle"
status: active
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN correction of AIP-EXEC-012"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-013
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative. Runtime state belongs in workspace. -->

# AIP_EXEC — Restore session Agent Team enable/disable toggle

## SOP Compliance
- Gate U1 Confirm-understanding-of-task (HARD GATE): STEP-00; HUMAN confirmed in chat.
- Gate U2 Confirm-understanding-of-input (soft): workspace findings.
- Gate U3 Open Points tracking (soft): workspace `05_open_questions.md`.

## Governance Note
- This is a corrective implementation after HUMAN rejected the scope of AIP-EXEC-012.
- Product/UI code and focused tests are in scope; no canonical Truth or Wiki mutation is planned.

## Objective
Restore an explicit Enable/Disable Agent Team button in the conversation session UI. The toggle must apply to the current session only and must not mutate profile-level activation.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: focused corrective UI implementation with no relevant project UI specification found by wiki lookup.
- Search/execution effect: inspect current UI, mount, runtime/session APIs, and focused tests directly.
- Resolved references: direct HUMAN requirement; Truth SOP and Contract.
- Deferred lookups: none.
- Expansion allowed: yes, only to trace the session-scoped activation path.

## Execution Scope
### In Scope
- Identify the current Agent Team session UI and available session-scoped state/action APIs.
- Restore an accessible Enable/Disable control in the session header/panel.
- Ensure the toggle is scoped to the active session and reflected in UI state.
- Update focused tests and build verification.

### Out of Scope
- Profile-level package activation or deactivation.
- Backend/team data model changes unless required to persist session-scoped enablement.
- Restoring removed mission/task creation controls.
- Unrelated routes or UI changes.

## Expected Outputs
- Updated Agent Team UI and integration code for session-scoped enable/disable.
- Focused tests covering initial state, enable, disable, and session isolation.
- Verification and lint results in the task workspace.

## Execution Input Package
### Plan Source
- HUMAN correction: AIP-EXEC-012 incorrectly removed the Agent Team Enable/Disable button; it must remain available per session.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Agent Team session UI guidance | (none) | (none) | Lookup and semantic escalation found no relevant project UI guidance | wiki:none |

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before execution.
- `05_open_questions.md` initialized.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN correction | Keep a session-level Enable/Disable Agent Team control in the UI. | Profile activation remains separate; session state may use existing host API or need a minimal session-local adapter. | Exact existing host activation API must be traced during STEP-01. | ✅ |

## References to Read First
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- `packages/web/src/client/TeamAction.tsx`
- `packages/web/src/client/mount.ts`
- `packages/web/tests/team-action.client.spec.tsx`
- `packages/web/tests/browser-plugin.client.spec.ts`

## Current Risks / Constraints
- The current composition may expose Agent Team only when the profile layer is installed; the button must not be confused with profile activation.
- Session isolation must be tested explicitly when switching between conversations.
- Preserve the mission/member-only presentation from AIP-EXEC-012 except for the restored toggle.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-013/05_open_questions.md`
- Exact host-side session activation seam: resolve in STEP-01; if absent, stop and ask HUMAN before inventing a new backend contract.

## Workspace Execution Rule
Runtime findings, decisions, progress, test output, and open points belong in the workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm corrected task understanding (HARD GATE)
Objective:
Record that the HUMAN corrected AIP-EXEC-012 and explicitly requires a session-scoped Agent Team Enable/Disable button.
Recommended Mode:
Clarifying
Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- wiki:none — preflight found no relevant UI guidance.
Inputs:
- HUMAN correction and confirmation in the current session.
Expected Outputs:
- Confirmation evidence in workspace findings.
Done Condition:
HUMAN confirmation is recorded; this condition is satisfied by the current chat confirmation.
Notes / Constraints:
Do not implement before the corrected scope is recorded.

### Step: STEP-01 — Trace session activation seam
Objective:
Map the existing UI mount, session lifecycle, and any host/remote API capable of enabling or disabling Agent Team for one session.
Recommended Mode:
Executing
Applicable Guidelines:
- wiki:none
Inputs:
- Current Agent Team UI, mount, host session APIs, and focused tests.
Expected Outputs:
- Workspace findings with the affected-file map and selected session-scoped implementation seam.
Done Condition:
The implementation seam and session-isolation behavior are identified without inventing an unconfirmed backend contract.
Notes / Constraints:
If no viable existing seam exists and a backend contract is required, record a blocker and ask HUMAN before proceeding.

### Step: STEP-02 — Implement session Enable/Disable control
Objective:
Add the accessible Enable/Disable control and wire it to current-session state while preserving mission/member rendering.
Recommended Mode:
Executing
Applicable Guidelines:
- wiki:none
Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-013/04_findings.md#step-01-activation-seam-trace`
- `packages/web/src/client/TeamAction.tsx`
- `packages/web/src/client/mount.ts`
- `packages/core/src/index.ts`
Expected Outputs:
- Minimal source changes for UI, mount/remote wiring, and session-local state as needed.
Done Condition:
The active session can be enabled and disabled from the UI, and switching sessions does not leak the state.
Notes / Constraints:
Do not change profile-level activation or restore unrelated removed controls.

### Step: STEP-03 — Verify and review
Objective:
Run focused tests, build checks, and AIWS lint; review for session isolation and regression of current mission/member UI.
Recommended Mode:
Reviewing
Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`
- wiki:none
Inputs:
- STEP-02 changes and workspace evidence.
Expected Outputs:
- Focused test/build results, review findings, and final capture sweep summary.
Done Condition:
Focused verification passes and task lint reports zero errors, or remaining failures are reported with evidence.
Notes / Constraints:
Do not claim completion if the session-scoped seam remains unresolved.

## Done Criteria
- [ ] Enable/Disable Agent Team control is visible and accessible in the session UI.
- [ ] Enablement state applies only to the active session.
- [ ] Switching sessions preserves independent enablement states.
- [ ] Current mission and member rendering remain intact.
- [ ] Profile-level activation behavior is unchanged.
- [ ] Focused tests/build and AIWS lint are completed and reported truthfully.
- [ ] Gate U1 confirmation evidence is recorded.
- [ ] All open points are resolved, deferred, or rejected with a conclusion.

## Self-check / Review Points
- Confirm the control is not merely decorative and invokes the intended session-scoped action.
- Confirm keyboard accessibility and accessible enabled/disabled labeling.
- Confirm no profile/package composition mutation occurs.
- Confirm session switch cleanup prevents stale state or stale async updates.

## Finalization Notes
- Run the mandatory final capture sweep before close.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Any objective, scope, or expected-output change requires a dated Re-plan Log entry before modifying earlier sections.

## Re-plan Log
- 2026-09-26 — Correct AIP-EXEC-012 scope / Trigger: HUMAN reported the removed Enable/Disable button was required / Change: create corrective AIP-EXEC-013 restoring a session-scoped toggle while retaining the mission/member-only simplification / Evidence: current-session HUMAN confirmation / Approved by: HUMAN
