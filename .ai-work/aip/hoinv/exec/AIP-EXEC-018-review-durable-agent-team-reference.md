---
artifact_type: aip_exec
artifact_id: AIP-EXEC-018
title: "Review Durable Agent Team reference for GAT design deltas"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN request on 2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-018
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative. Runtime state belongs in workspace. -->

# AIP_EXEC — Review Durable Agent Team reference for GAT design deltas

## SOP Compliance
- Gate U1 Confirm-understanding-of-task (HARD GATE): STEP-00; HUMAN confirmed in chat.
- Gate U2 Confirm-understanding-of-input (soft): workspace findings.
- Gate U3 Open Points tracking (soft): workspace `05_open_questions.md`.

## Objective
Review the external Durable Agent Team workspace-adoption reference against the current GAT design and incorporate only material, evidence-backed design deltas, while preserving clear implemented/proposed status.

## Selected Task Lens / Mode
- Lens: design_review
- Reason: cross-document design comparison and selective reconciliation.
- Search/execution effect: compare claims and operational contracts, then update only non-duplicative material gaps.
- Resolved references: HUMAN-supplied Durable Agent Team reference and current GAT design reference.
- Deferred lookups: none.
- Expansion allowed: yes, only to verify source claims.

## Execution Scope
### In Scope
- Compare activation, manifest authorization, catalog/discovery, delegation, context assembly, memory promotion, failure/security, and workspace-adoption guidance.
- Add material missing design contracts to the GAT reference.
- Update evidence and maintenance mapping.

### Out of Scope
- Copying the entire external reference into GAT docs.
- Runtime implementation changes.
- Treating target contracts as installed behavior.
- Wiki/Truth promotion.

## Expected Outputs
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — selectively updated if material gaps exist.
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-018/04_findings.md` — delta analysis and verification.

## Execution Input Package
### Plan Source
- Direct HUMAN request and scope confirmation in this session.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Durable Agent Team reference | (none) | `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENT_TEAM_REFERENCE.md` | Wiki lookup and semantic escalation found no project source | [retrieval_gap] |

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before execution.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Review the additional Durable Agent Team reference and enrich GAT design only where needed. | Material deltas should be summarized rather than duplicated. | None. | ✅ |

## References to Read First
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENT_TEAM_REFERENCE.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md`

## Current Risks / Constraints
- The external document is a target integration/adoption reference, not proof of installed behavior.
- It may repeat content already incorporated by AIP-EXEC-015.
- Operational guidance must not silently become canonical project policy.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-018/05_open_questions.md`
- No blocker identified.

## Workspace Execution Rule
Delta findings, source classification, and decisions belong in the workspace.

## Execution Steps

### Step: STEP-00 — Confirm selective review scope (HARD GATE)
Objective:
Record the HUMAN-confirmed instruction to apply only material deltas and preserve implementation-status labels.
Recommended Mode:
Clarifying
Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- wiki:none
Inputs:
- HUMAN request and explicit confirmation.
Expected Outputs:
- Confirmation evidence in workspace findings.
Done Condition:
Selective-review scope is recorded.
Notes / Constraints:
Do not edit merely to duplicate existing prose.

### Step: STEP-01 — Analyze material design deltas
Objective:
Compare the external adoption reference with the current GAT design and classify each candidate delta as duplicate, material, unsupported, or operational-only.
Recommended Mode:
Reviewing
Applicable Guidelines:
- wiki:none
Inputs:
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENT_TEAM_REFERENCE.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
Expected Outputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-018/04_findings.md`
Done Condition:
Every material update has source evidence and an implementation-status label.
Notes / Constraints:
Reject unsupported or contradictory target claims.

### Step: STEP-02 — Apply material GAT design updates
Objective:
Add concise missing contracts without duplicating the external reference.
Recommended Mode:
Authoring
Applicable Guidelines:
- wiki:none
Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-018/04_findings.md`
Expected Outputs:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
Done Condition:
All accepted deltas are integrated and attributed to AIP-EXEC-018.
Notes / Constraints:
If no material delta exists, record a no-change conclusion instead.

### Step: STEP-03 — Review and finalize
Objective:
Verify the updated design against both references, run lint, and report residual uncertainty.
Recommended Mode:
Reviewing
Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`
- wiki:none
Inputs:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-018/04_findings.md`
Expected Outputs:
- Verification evidence and final summary.
Done Condition:
Review is complete and task lint has zero errors, or residual issues are reported with evidence.
Notes / Constraints:
Perform final capture sweep before close.

## Done Criteria
- [ ] External reference is compared against current GAT design.
- [ ] Only material, supported deltas are added.
- [ ] Target behavior remains distinguished from installed behavior.
- [ ] External source and AIP attribution are present if the design changes.
- [ ] Gate U1 and review evidence are recorded.
- [ ] AIWS task lint is reported truthfully.

## Self-check / Review Points
- Confirm no whole-section duplication without added design value.
- Confirm directories on disk are never treated as authorization.
- Confirm catalog and memory do not grant authority.
- Confirm adoption guidance is not mislabeled runtime behavior.

## Finalization Notes
- Defer Wiki registration to separate HUMAN curation.

## Pre-flight Pending Captures
- Durable Agent Team reference retrieval gap: external source is not registered in the project Wiki.

## Re-plan Rule
Any objective, scope, or expected-output change requires a dated Re-plan Log entry before modifying earlier sections.

## Re-plan Log
- (no re-plan yet)
