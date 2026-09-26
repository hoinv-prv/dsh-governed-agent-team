---
artifact_type: aip_exec
artifact_id: AIP-EXEC-014
title: "Document current GAT design and features"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN request on 2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-014
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative. Runtime state belongs in workspace. -->

# AIP_EXEC — Document current GAT design and features

## SOP Compliance
- Gate U1 Confirm-understanding-of-task (HARD GATE): STEP-00; HUMAN confirmed in chat.
- Gate U2 Confirm-understanding-of-input (soft): workspace findings.
- Gate U3 Open Points tracking (soft): workspace `05_open_questions.md`.

## Objective
Create one durable reference document under `docs/` that consolidates the current Governed Agent Team design, implemented features, session lifecycle, component responsibilities, governance, and the exact `team_members.yaml` member-resolution contract, while clearly separating implemented behavior from proposals or deferred work.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: documentation synthesis grounded in current source and existing local reference documents.
- Search/execution effect: read the implementation and package documentation directly after wiki lookup returned no project GAT source route.
- Resolved references: existing GAT design, package READMEs, current source, tests, and the workspace `team_members.yaml`.
- Deferred lookups: none.
- Expansion allowed: yes, only to verify current implementation behavior.

## Execution Scope
### In Scope
- Current architecture and package/component map.
- Session-scoped Enable-only lifecycle and durable state behavior.
- Exact lookup, schema validation, limits, fallback, and reload semantics for `team_members.yaml`.
- Core roster, mailbox, tasks, missions, work state, tools, Web UI, profiles, installer, and governance behavior.
- Source-of-evidence map and implemented/proposed/deferred status labels.

### Out of Scope
- Changing GAT runtime behavior.
- Promoting the document into official Wiki/Truth.
- Rewriting existing design proposals.
- Claiming unverified features as implemented.

## Expected Outputs
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — consolidated maintained reference.
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-014/04_findings.md` — source verification notes.

## Execution Input Package
### Plan Source
- Direct HUMAN request and confirmed scope in this session.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Project GAT design/features | (none) | (none) | Wiki lookup returned no relevant registered project source | wiki:none |

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before execution.
- `05_open_questions.md` initialized.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Produce a future reference covering current GAT design and functions, especially member resolution from `team_members.yaml`. | One English Markdown reference with code examples and source paths is suitable for `docs/`. | None; implemented/proposed distinction is required. | ✅ |

## References to Read First
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `packages/core/README.md`
- `packages/tools/README.md`
- `packages/web/README.md`
- `packages/profile/README.md`
- `packages/web-profile/README.md`
- `team_members.yaml`
- Current GAT implementation under `packages/core/`, `packages/tools/`, and `packages/web/`.
- Installed/current DSH GAT sources under `/home/hoinv/deepseek-harness/packages/experimental/gat-*` when required to verify latest runtime behavior.

## Current Risks / Constraints
- Workspace source and installed DSH checkout currently differ; the document must identify which behavior is current and where its evidence lives.
- Existing proposal documents may describe future behavior; they cannot be presented as shipped behavior.
- `team_members.yaml` is read only when enabling a new session; existing durable rosters are not replaced.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-014/05_open_questions.md`
- No blocker identified.

## Workspace Execution Rule
Runtime findings, source comparisons, progress, and decisions belong in the task workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm documentation scope (HARD GATE)
Objective:
Record the HUMAN-confirmed scope, output location, and implemented-versus-proposed distinction.
Recommended Mode:
Clarifying
Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- wiki:none
Inputs:
- HUMAN request and explicit confirmation in this session.
Expected Outputs:
- Confirmation evidence in workspace findings.
Done Condition:
HUMAN confirmation is recorded.
Notes / Constraints:
Do not author the reference before recording confirmation.

### Step: STEP-01 — Verify current GAT behavior and source map
Objective:
Read the current implementation and documentation, reconcile workspace and installed-runtime differences, and record evidence for each documented behavior.
Recommended Mode:
Research
Applicable Guidelines:
- wiki:none
Inputs:
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `packages/core/README.md`
- `packages/tools/README.md`
- `packages/web/README.md`
- `team_members.yaml`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/src/team-config.ts`
Expected Outputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-014/04_findings.md` with verified feature and source map.
Done Condition:
Every planned section has implementation or document evidence and a status classification.
Notes / Constraints:
Treat proposal-only claims as proposed, not implemented.

### Step: STEP-02 — Author consolidated GAT reference
Objective:
Write the consolidated reference with architecture, feature catalog, lifecycles, `team_members.yaml` contract, governance, limitations, and source map.
Recommended Mode:
Authoring
Applicable Guidelines:
- wiki:none
Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-014/04_findings.md`
Expected Outputs:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
Done Condition:
The document is self-contained, traceable to current sources, and distinguishes implemented, proposed, and deferred behavior.
Notes / Constraints:
Do not silently turn this project reference into canonical Truth or Wiki authority.

### Step: STEP-03 — Review and finalize
Objective:
Review the reference against sources, check paths and terminology, run AIWS lint, and report any remaining uncertainty.
Recommended Mode:
Reviewing
Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`
- wiki:none
Inputs:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-014/04_findings.md`
Expected Outputs:
- Verification summary in workspace findings.
Done Condition:
Document review is complete and task lint has zero errors, or residual issues are reported with evidence.
Notes / Constraints:
Perform the mandatory final capture sweep before close.

## Done Criteria
- [ ] One consolidated GAT reference exists under `docs/`.
- [ ] Current features and architecture are summarized with source paths.
- [ ] `team_members.yaml` resolution, schema, validation, fallback, and reload behavior are explicit.
- [ ] Implemented, proposed, and deferred behavior are clearly separated.
- [ ] Gate U1 evidence is recorded.
- [ ] All open points are resolved, deferred, or rejected.
- [ ] AIWS task lint result is reported truthfully.

## Self-check / Review Points
- Verify no proposal-only behavior is labeled implemented.
- Verify the YAML example matches the actual schema and limits.
- Verify session-scoped one-way enable semantics and existing-roster behavior.
- Verify all referenced paths exist or are explicitly identified as external installed-runtime paths.

## Finalization Notes
- Run final capture sweep and task lint.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Any objective, scope, or expected-output change requires a dated Re-plan Log entry before modifying earlier sections.

## Re-plan Log
- (no re-plan yet)
