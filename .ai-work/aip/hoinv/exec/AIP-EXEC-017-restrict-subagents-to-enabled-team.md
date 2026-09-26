---
artifact_type: aip_exec
artifact_id: AIP-EXEC-017
title: "Restrict sub-agent spawning to enabled Agent Team"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN request 2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-017
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Restrict sub-agent spawning to enabled Agent Team

## SOP Compliance
- Gate U1 satisfied by HUMAN request and follow-up confirmation that implementation may proceed without building a team.
- Gate U2 is handled by reading the existing GAT profile/runtime and tests.
- Gate U3 is tracked in the task workspace.

## Objective
When Agent Team is enabled for a session, prevent that session from spawning or forking sub-agents outside the governed team, while preserving normal sub-agent behavior for sessions where Agent Team is disabled. If a needed skill or capability is absent, require HUMAN approval, add the approved member to the team, and only then assign the task to that member.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: bounded implementation and regression-test task in project source.
- Search/execution effect: inspect runtime integration points and tests directly after wiki lookup returned no relevant GAT source.
- Resolved references: project source and tests listed below.
- Deferred lookups: none.
- Expansion allowed: yes, only where required to identify the host admission hook.

## Execution Scope
### In Scope
- Identify the common admission point for ordinary sub-agent spawn/fork.
- Enforce session-scoped denial when Agent Team is enabled.
- Keep Agent Team teammate creation functional.
- Provide actionable denial guidance: request HUMAN approval, add the required member, then assign the task.
- Add regression tests for enabled and disabled sessions and the capability-gap guidance.

### Out of Scope
- Changing team membership limits or team lifecycle semantics.
- Reworking the Web UI.
- Modifying DSH canonical sources outside this workspace.

## Expected Outputs
- Source changes under `packages/` implementing session-scoped admission and HUMAN-approved member-add guidance.
- Automated tests covering denied external delegation, capability-gap guidance, and allowed team/solo behavior.
- Verified build/test/lint results.

## Execution Input Package
### Plan Source
- Direct HUMAN request: if Agent Team is enabled in a session, do not spawn sub-agents other than agents in that team.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT runtime guidance | (none) | `packages/` | Project implementation is not registered in the wiki; lookup and semantic retry returned no relevant source. | wiki:none |

### Reference lookup
- Query: `GAT Agent Team session sub-agent spawn`; default and semantic lookup returned no relevant GAT source.

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before runtime workspace updates.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Team-enabled session must be exclusive to governed team members. | Existing team spawn path can be distinguished from ordinary sub-agent tools. | Exact host admission extension point requires code inspection. | ✅ |

## References to Read First
- `packages/profile/src/index.ts`
- `packages/core/src/index.ts`
- `packages/core/src/roster.ts`
- `packages/tools/src/index.ts`
- Related package tests.

## Current Risks / Constraints
- Working tree contains substantial pre-existing HUMAN changes; do not overwrite or revert them.
- Guard must not block `spawn_teammate` itself.
- Enforcement should be runtime/session scoped, not a global static disable.

## Known Open Points
- None at creation; implementation details will be recorded in workspace findings if needed.

## Workspace Execution Rule
Runtime findings, progress, test evidence, and capture candidates belong in the task workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record the requested exclusive-team behavior and confirmation evidence.

Recommended Mode:
Clarifying

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- HUMAN request and follow-up discussion.

Expected Outputs:
- Confirmation evidence in workspace findings.

Done Condition:
The HUMAN request unambiguously specifies session-scoped team exclusivity.

Notes / Constraints:
- The HUMAN already confirmed that no implementation team is required; main session executes directly.

Workspace Actions:
- Record confirmation evidence.

### Step: STEP-01 — Inspect Admission Paths and Design Guard
Objective:
Trace ordinary sub-agent spawn/fork and governed teammate creation to select the narrowest common enforcement point.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- GAT core, tools, profile source, and existing tests.

Expected Outputs:
- Evidence-backed guard design in workspace findings.

Done Condition:
The design identifies how to deny external delegation without denying teammate provisioning.

Notes / Constraints:
- Preserve current unrelated working-tree changes.

Workspace Actions:
- Record inspected paths and selected guard point.

### Step: STEP-02 — Implement Session-Scoped Team Exclusivity
Objective:
Implement the selected guard and public typings/configuration required by the integration.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- STEP-01 findings and current source.

Expected Outputs:
- Minimal source changes enforcing the requested behavior.

Done Condition:
Ordinary spawn/fork is rejected only for team-enabled sessions, while governed teammate spawn remains operational.

Notes / Constraints:
- Do not globally disable sub-agent providers.

Workspace Actions:
- Record changed files and behavioral rationale.

### Step: STEP-03 — Add and Run Regression Tests
Objective:
Add focused tests and run affected package checks.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- Implemented guard and existing test harness.

Expected Outputs:
- Tests for enabled-team denial, solo-session allowance, and teammate allowance.
- Test/build/lint evidence.

Done Condition:
Affected tests and type/build checks pass, or any external blocker is reported precisely.

Notes / Constraints:
- Prefer targeted tests before broader package verification.

Workspace Actions:
- Record commands and outcomes.

## Done Criteria
- [ ] Team-enabled session cannot use ordinary sub-agent spawn/fork outside the team.
- [ ] Denial directs capability gaps through HUMAN approval → add team member → assign task.
- [ ] Governed teammate creation still works.
- [ ] Team-disabled session retains ordinary sub-agent behavior.
- [ ] Relevant automated tests pass.
- [ ] Gate U1 evidence and Gate U3 disposition exist in workspace.

## Self-check / Review Points
- Verify enforcement is session-scoped.
- Verify the guard cannot be bypassed through both fresh and fork delegation.
- Verify existing team tools continue to call the permitted internal path.
- Run scoped AIWS final lint and report actual results.

## Finalization Notes
- Final capture sweep is mandatory before close.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
If objective, scope, or expected outputs change, append a dated Re-plan Log entry before editing earlier sections.

## Re-plan Log
### 2026-09-26 — Add HUMAN-approved capability-gap flow
- Trigger: HUMAN clarified that missing skills/capabilities must not cause an external sub-agent spawn.
- Change: require HUMAN approval, add the needed member to the current team, then assign work to that member; denial guidance and tests are included in scope.
- Evidence ref: HUMAN message in this session.
- Approved by: HUMAN.
