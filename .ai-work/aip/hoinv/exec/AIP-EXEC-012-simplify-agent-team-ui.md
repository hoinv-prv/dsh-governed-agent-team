---
artifact_type: aip_exec
artifact_id: AIP-EXEC-012
title: "Simplify Agent Team UI to current mission and members"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN request on 2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-012
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Simplify Agent Team UI to current mission and members

## SOP Compliance
- Gate U1 Confirm-understanding-of-task (HARD GATE): STEP-00
- Gate U2 Confirm-understanding-of-input (soft): workspace findings
- Gate U3 Open Points tracking (soft): workspace `05_open_questions.md`

## Objective
Simplify the Agent Team UI so it only shows the team's current mission and member list, removing mission/task creation controls and the task list from the interface.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: focused implementation against the existing local UI code; no reusable project UI specification was found by wiki lookup.
- Search/execution effect: inspect the implementation and tests directly after Gate U1 confirmation.
- Resolved references: direct HUMAN request; `.ai-work/truth/SOP_MASTER.md`.
- Deferred lookups: none.
- Expansion allowed: yes, only when required to trace affected components and tests.

## Execution Scope
### In Scope
- Identify the Agent Team UI components and their state/data dependencies.
- Keep only current mission presentation and member-list presentation.
- Remove or hide add-mission, add-task, and task-list UI affordances.
- Update focused tests where present.

### Out of Scope
- Changing backend mission/task APIs or persisted data models unless compilation requires a minimal compatibility adjustment.
- Redesigning unrelated pages.
- Adding new mission or task functionality.

## Expected Outputs
- Updated Agent Team UI source files.
- Updated focused UI tests where applicable.
- Verification results recorded in the task workspace.

## Execution Input Package
### Plan Source
- Direct HUMAN request in this session.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Agent Team UI guidance | (none) | (none) | Focused lookup returned no relevant project UI specification | wiki:none |

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before execution.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | UI should show only current mission and members; no add mission, add task, or task list | Existing data may remain in backend/state but must not be exposed in this UI | Whether mission details beyond title/description should remain will follow existing current-mission card | pending |

## References to Read First
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- Existing Agent Team UI implementation and focused tests, resolved during STEP-01.

## Current Risks / Constraints
- Removing visual controls must not accidentally break shared state or unrelated routes.
- Preserve existing current-mission and member behavior.
- Delegate bounded analysis, implementation, and review tasks according to teammate capability, with disjoint write scopes.

## Known Open Points
- No blocker identified; current-mission field selection follows the existing presentation unless the HUMAN specifies otherwise.

## Workspace Execution Rule
Runtime findings, progress, verification, and decisions belong in the task workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Restate scope, deliverables, and exclusions, then obtain explicit HUMAN confirmation before implementation.

Recommended Mode:
Clarifying

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- Direct HUMAN request
- This AIP

Expected Outputs:
- Confirmation evidence in workspace findings after start

Done Condition:
HUMAN explicitly confirms the stated understanding or authorizes proceeding.

Notes / Constraints:
- Do not inspect or modify implementation files before confirmation.

Workspace Actions:
- Record task understanding and HUMAN confirmation.

### Step: STEP-01 — Inspect and map Agent Team UI
Objective:
Locate the UI implementation, relevant data flow, and focused tests; produce a minimal change map.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- context-delegation

Inputs:
- Existing repository source and test files
- Confirmed task scope

Expected Outputs:
- Affected-file map and implementation approach in workspace findings

Done Condition:
The current-mission, members, mission/task controls, and task-list render paths are identified.

Notes / Constraints:
- Delegate independent inspection/review work to appropriately capable team members.

Workspace Actions:
- Record findings and affected paths.

### Step: STEP-02 — Implement mission-and-members-only UI
Objective:
Remove the unwanted controls and task list while preserving the current mission and members display.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-012/04_findings.md#step-01-affected-file-map`
- Existing UI source and tests

Expected Outputs:
- Minimal UI source changes
- Focused test updates where applicable

Done Condition:
The Agent Team UI renders the current mission and members only, with no add-mission, add-task, or task-list UI.

Notes / Constraints:
- Avoid backend/schema changes unless required for compilation.
- Assign implementation to a teammate with a disjoint write scope; retain review/verification separately.

Workspace Actions:
- Record implementation summary and changed paths.

### Step: STEP-03 — Verify and review
Objective:
Run focused tests/build checks and independently review that unwanted UI paths are absent without regressions to mission/member rendering.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`

Recommended Skills:
- aiws-lint

Inputs:
- STEP-02 changes
- Relevant test/build commands

Expected Outputs:
- Test/lint results
- Review findings and any fixes

Done Condition:
Focused verification passes and AIWS task lint reports zero errors, or any remaining failure is reported with evidence.

Notes / Constraints:
- Use a different teammate for review when practical.

Workspace Actions:
- Record verification evidence and final capture sweep summary.

## Done Criteria
- [ ] Agent Team UI shows the current mission.
- [ ] Agent Team UI shows the member list.
- [ ] Add-mission functionality is absent from the UI.
- [ ] Add-task functionality is absent from the UI.
- [ ] Task list is absent from the UI.
- [ ] Focused verification and AIWS task lint are completed and reported truthfully.
- [ ] Gate U1 confirmation evidence is recorded.
- [ ] All open points are resolved, deferred, or rejected with a conclusion.

## Self-check / Review Points
- Confirm no unrelated route or backend API was changed.
- Confirm removed controls are not merely visually hidden while still keyboard-accessible in the page.
- Confirm current mission and member rendering still handles empty/loading states appropriately.
- Run `python3 .ai-work/tooling/lint_all.py --scope task --workspace <workspace> --aip .ai-work/aip/hoinv/exec/AIP-EXEC-012-simplify-agent-team-ui.md`.

## Finalization Notes
- Perform the mandatory final capture sweep before close.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Any objective, scope, or output change requires a dated Re-plan Log entry before modifying earlier sections.

## Re-plan Log
- (no re-plan yet)
