---
artifact_type: aip_exec
artifact_id: AIP-EXEC-015
title: "Integrate Durable Agent design into GAT reference"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN request on 2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-015
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative. Runtime state belongs in workspace. -->

# AIP_EXEC — Integrate Durable Agent design into GAT reference

## SOP Compliance
- Gate U1 Confirm-understanding-of-task (HARD GATE): STEP-00; HUMAN confirmed in chat.
- Gate U2 Confirm-understanding-of-input (soft): workspace findings.
- Gate U3 Open Points tracking (soft): workspace `05_open_questions.md`.

## Objective
Use the Durable Agents MiniMVP design as an external reference to extend the GAT design reference with the architectural relationship, shared manifest, responsibility boundary, persistence/context mapping, integration assumptions, gaps, and roadmap—without mislabeling Durable Agent behavior as already implemented in GAT.

## Selected Task Lens / Mode
- Lens: design_authoring
- Reason: cross-document architecture synthesis between GAT and Durable Agent.
- Search/execution effect: compare concepts, lifecycle boundaries, storage ownership, and integration seams before authoring.
- Resolved references: HUMAN-supplied Durable Agent MiniMVP, current GAT design reference, and current GAT implementation sources.
- Deferred lookups: none.
- Expansion allowed: yes, only to verify claims and source boundaries.

## Execution Scope
### In Scope
- Define how GAT orchestration relates to Durable Agent identity, SOUL, memory, and working storage.
- Map the shared `team_members.yaml` fields and the additional `storage_scope` field.
- Define separation of lifecycle/orchestration from durable definition/storage.
- Document integration sequence, fail-closed rules, mismatches, and future work.
- Update source/evidence and maintenance sections.

### Out of Scope
- Implementing the Durable Agent package or integrating runtime code.
- Changing `team_members.yaml` schema in GAT.
- Registering external Durable Agent documentation into the project Wiki.
- Claiming automatic spawning, scheduling, or lifecycle management in Durable Agent.

## Expected Outputs
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — updated with Durable Agent relationship and design mapping.
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md` — comparison and verification evidence.

## Execution Input Package
### Plan Source
- Direct HUMAN request and scope confirmation in this session.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Durable Agent MiniMVP | (none) | `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md` | Wiki lookup and semantic escalation found no project source | [retrieval_gap] |

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before execution.
- Open points log initialized.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Durable Agent is closely related to GAT and its design must inform the GAT reference. | Durable Agent remains a complementary subsystem unless implementation evidence proves integration. | No blocker; document shared contract and boundaries explicitly. | ✅ |

## References to Read First
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `team_members.yaml`
- Latest GAT core/tools sources identified by AIP-EXEC-014.

## Current Risks / Constraints
- Both systems use `team_members.yaml`, but their accepted schema currently differs because Durable Agent adds `storage_scope` while the latest GAT loader rejects unknown keys.
- Durable Agent explicitly does not spawn agents or manage runtime lifecycle; GAT must remain the orchestration owner.
- A future integration must avoid two independent manifest parsers drifting silently.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/05_open_questions.md`
- No blocker identified.

## Workspace Execution Rule
Runtime analysis, comparisons, and decisions belong in the task workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Durable Agent integration scope (HARD GATE)
Objective:
Record the HUMAN-confirmed intent and the rule that Durable Agent features must not be represented as already implemented in GAT.
Recommended Mode:
Clarifying
Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- wiki:none — no registered Durable Agent project source found.
Inputs:
- HUMAN request and explicit confirmation.
Expected Outputs:
- Confirmation evidence in workspace findings.
Done Condition:
Scope and implementation-status boundary are recorded.
Notes / Constraints:
Do not author integration claims before confirmation.

### Step: STEP-01 — Compare Durable Agent and GAT contracts
Objective:
Map identity, manifest, storage, task-context, lifecycle, recovery, and governance responsibilities; identify conflicts and integration seams.
Recommended Mode:
Research
Applicable Guidelines:
- wiki:none
Inputs:
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `team_members.yaml`
Expected Outputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md`
Done Condition:
Shared concepts, ownership boundaries, incompatibilities, and proposed integration sequence are evidence-bound.
Notes / Constraints:
Do not infer runtime integration from shared filenames alone.

### Step: STEP-02 — Update GAT design reference
Objective:
Add the Durable Agent relationship, boundary, contract mapping, integration model, gaps, and roadmap to the maintained reference.
Recommended Mode:
Authoring
Applicable Guidelines:
- wiki:none
Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md`
Expected Outputs:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
Done Condition:
The relationship is self-contained and clearly labels current versus target behavior.
Notes / Constraints:
Add AIP-EXEC-015 attribution and the external reference path.

### Step: STEP-03 — Review and finalize
Objective:
Review the update against both documents, verify the schema incompatibility and boundary claims, and run AIWS lint.
Recommended Mode:
Reviewing
Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`
- wiki:none
Inputs:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md`
Expected Outputs:
- Verification evidence and final output summary.
Done Condition:
Review is complete and task lint has zero errors, or residual issues are reported with evidence.
Notes / Constraints:
Perform final capture sweep before close.

## Done Criteria
- [ ] GAT reference explains the Durable Agent relationship.
- [ ] Shared manifest and `storage_scope` incompatibility are explicit.
- [ ] Runtime orchestration and durable storage responsibilities are separated.
- [ ] Current and target behavior are clearly distinguished.
- [ ] Integration assumptions, fail-closed behavior, and roadmap are documented.
- [ ] Gate U1 and source evidence are recorded.
- [ ] AIWS task lint is reported truthfully.

## Self-check / Review Points
- Confirm Durable Agent is not described as an automatic spawner or scheduler.
- Confirm GAT remains owner of Team runtime/session lifecycle.
- Confirm Durable Agent remains owner of SOUL/memory/working storage.
- Confirm GAT's current strict parser would reject `storage_scope`.
- Confirm no Truth or Wiki was silently modified.

## Finalization Notes
- Defer any Wiki-registration candidate to HUMAN curation.

## Pre-flight Pending Captures
- Durable Agent source retrieval gap: `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md` is not registered in this project's Wiki.

## Re-plan Rule
Any objective, scope, or expected-output change requires a dated Re-plan Log entry before modifying earlier sections.

## Re-plan Log
- (no re-plan yet)
