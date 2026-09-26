---
artifact_type: aip_exec
artifact_id: AIP-EXEC-020
title: "Bootstrap the GAT design-document wiki"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "direct-user-request-2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-020
updated_at: 2026-09-26
---

# AIP_EXEC — Bootstrap the GAT design-document wiki

## SOP Compliance

- Gate U1: the Human confirmed scope, purpose, docs-only shape, and no object nodes on 2026-09-26.
- Gate U2/U3: execution records understanding and open points in the workspace.

## Objective

Build the first project wiki for the approved GAT design-document corpus, supporting Q&A plus design, implementation, and review tasks.

## Selected Task Lens / Mode

- Lens: No-Lens
- Reason: first-build wiki bootstrap has its own fixed method and scope.
- Search/execution effect: use the fixed 12-step `PROJECT_WIKI_BUILDUP_GUIDELINE` flow.
- Resolved references: the indexed project wiki buildup guideline.
- Deferred lookups: source documents are unregistered and will be handled by the bootstrap registration flow.
- Expansion allowed: no; source-code, test, historical snapshot, and evidence files remain out of scope.

## Execution Scope

### In Scope

- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md`
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v39.md` (the final current version only)
- Project wiki source metadata, document-to-document relations, and generated overview pages.

### Out of Scope

- `packages/` source and tests.
- Earlier `control-plane-stabilization-design.v*.md` versions, council snapshots, evidence, reports, and implementation records in `wbs-runs`.
- Identity/object nodes and any invented feature enumeration.

## Expected Outputs

- Registered metadata and index entries for the six scoped design documents.
- Document-to-document relations only, with no object nodes.
- Build log, lesson log, lookup tests, and project wiki overview pages.
- A project wiki build-up guideline derived from the completed build.

## Execution Input Package

### Plan Source

- Direct Human request and scope decisions dated 2026-09-26.

### Required Truth Inputs

- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Project wiki buildup guideline | SRC-WIKIGUIDE-wiki-guidelines-core-guidelines-project-wiki-buildup-guideline-md-1d04 | `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` | Fixed bootstrap method | — |

## References to Read First

- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md`
- `.ai-work/procedural/skills/aiws-wiki/operations/bootstrap.md`

## Current Risks / Constraints

- This is a first-build operation; no project wiki metadata or index entries currently exist.
- The selected WBS document must remain v39 only; historical revisions and evidence are excluded.
- Candidate metadata and relations require Human review gates before application.

## Known Open Points

- Open Points log: workspace `05_open_questions.md`.
- No object-node enumeration source exists; identity nodes are intentionally skipped.

## Workspace Execution Rule

Maintain the Active Step Context, build log, lesson log, findings, open questions, draft output, and capture inbox in the workspace.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record the Human-confirmed corpus, purpose, docs-only shape, and no-object-node decision.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline

Inputs:
- Human scope decisions

Expected Outputs:
- Confirmed task-understanding note in the workspace

Done Condition:
- The confirmed scope and exclusions are recorded.

Notes / Constraints:
- Do not register sources before confirmation evidence is recorded.

### Step: STEP-01 — Define the GOAL of the wiki
Objective:
Set the GAT wiki goal for Q&A, design, implementation, and review; initialize BUILD LOG and LESSON LOG.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 1

Recommended Skills:
- aiws-wiki lookup

Inputs:
- Confirmed docs-only corpus and task kinds

Expected Outputs:
- Wiki goal, docs-only shape decision, `build-log.md`, and lesson-log reference

Done Condition:
- Goal, task simulations, and shape are explicit.

Notes / Constraints:
- Docs-only annotation: no source-code layer is in scope.

### Step: STEP-02 — Decide WHAT goes in (inventory)
Objective:
Create the authoritative six-document inventory and source-type grouping.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 2

Recommended Skills:
- aiws-wiki lookup

Inputs:
- Scoped paths from this AIP

Expected Outputs:
- In/out inventory and source-type plan

Done Condition:
- Every scoped source and exclusion is classified.

Notes / Constraints:
- Docs-only annotation: group documents by role, not code language or layer.

### Step: STEP-03 — Confirm authority / value / use
Objective:
Confirm authority, intended use, and source-of-truth boundaries for each document.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 3

Inputs:
- Approved inventory

Expected Outputs:
- Authority/value/use matrix

Done Condition:
- Document roles and any non-SoT status are explicit.

Notes / Constraints:
- Docs-only annotation: mark proposals or snapshots as non-SoT when appropriate.

### Step: STEP-04 — Predict the relationships
Objective:
Plan document-to-document relation types and directions.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 4

Recommended Skills:
- wiki-relations

Inputs:
- Authority/value/use matrix

Expected Outputs:
- Relation map

Done Condition:
- Relation candidates are reviewable and object nodes are excluded.

Notes / Constraints:
- Docs-only annotation: create document↔document relations only.

### Step: STEP-05 — Plan the meta build
Objective:
Choose metadata profiles and registration methods for each document group.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 5

Recommended Skills:
- aiws-wiki register-batch
- aiws-wiki build-pattern

Inputs:
- Inventory and relation map

Expected Outputs:
- Per-group metadata build plan

Done Condition:
- Registration plan is approved for trial samples.

Notes / Constraints:
- Docs-only annotation: skip the source-code layer.

### Step: STEP-06 — Identify the tools to build
Objective:
Determine whether existing batch registration tools cover the document corpus.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 6

Recommended Skills:
- aiws-wiki register-batch

Inputs:
- Metadata build plan

Expected Outputs:
- Tooling directive for each new bulk builder, if any

Done Condition:
- Existing-tool or new-tool decision is recorded.

Notes / Constraints:
- Docs-only annotation: normally no bulk builder or cross-layer matcher is required.

### Step: STEP-07 — Trial-run build-meta on samples
Objective:
Build and validate sample metadata profiles before the mass run.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 7

Recommended Skills:
- aiws-wiki build-meta
- aiws-wiki test-lookup
- aiws-lint

Inputs:
- Approved metadata plan

Expected Outputs:
- Sample metas and three-keyword lookup smoke evidence

Done Condition:
- Human approves the sample format and smoke result.

Notes / Constraints:
- Docs-only annotation: trial the profile, not a code-analysis tool.

### Step: STEP-08 — Build/confirm the refresh tool
Objective:
Confirm the refresh path preserves curated metadata content.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 8

Recommended Skills:
- aiws-wiki refresh

Inputs:
- Sample metadata

Expected Outputs:
- Confirmed refresh procedure

Done Condition:
- Refresh behavior is safe for curated content.

Notes / Constraints:
- Docs-only annotation: use single-artifact refresh; no matcher caveat applies.

### Step: STEP-09 — Mass-run + spot-checks + wire relations
Objective:
Register the scoped corpus, spot-check results, and apply approved document relations.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 9

Recommended Skills:
- aiws-wiki register-batch
- aiws-lint
- wiki-relations

Inputs:
- Approved sample format and relation map

Expected Outputs:
- Indexed metas, relations, and spot-check evidence

Done Condition:
- Fix-and-rerun loop is complete and all approved documents are registered.

Notes / Constraints:
- Docs-only annotation: wire document↔document edges only; skip object nodes and matchers.

### Step: STEP-10 — Test the wiki; tune the profile
Objective:
Run acceptance simulations for Q&A, design, implementation, and review tasks and tune the profile as approved.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 10

Recommended Skills:
- aiws-wiki test-lookup
- aiws-lint

Inputs:
- Registered wiki and task simulation cases

Expected Outputs:
- Lookup-test results and curation-gap decisions

Done Condition:
- Acceptance cases pass or approved gaps are recorded.

Notes / Constraints:
- Docs-only annotation: test bidirectional document↔document retrieval.

### Step: STEP-11 — Produce the project's wiki build-up guideline
Objective:
Produce and accept the project wiki buildup guideline, incorporating BUILD LOG and triaged lessons; generate overview pages.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 11

Inputs:
- `build-log.md`
- Lesson log and accepted build results

Expected Outputs:
- Project wiki buildup guideline and generated contents/search/health overview pages

Done Condition:
- Human accepts the guideline and lesson triage; overview build completes.

Notes / Constraints:
- Run `python3 .ai-work/tooling/build_wiki_overview.py --all-systems` at wrap-up.

## Done Criteria

- The fixed STEP-00 through STEP-11 skeleton remains sequential and complete.
- All six approved documents are registered; excluded historical and evidence artifacts are absent.
- No identity/object nodes are created.
- Human reviews this AIP before execution begins.
- Applicable wiki and task lint checks pass.

## Self-check / Review Points

- Each step pins the core guideline section plus its assigned step section.
- BUILD LOG is an explicit STEP-11 input.
- Document-to-document relations are approved before application.

## Finalization Notes

- Offer `aiws-wiki build-pages survey` as an optional post-bootstrap handoff; do not add another bootstrap step.

## Pre-flight Pending Captures

- (none)

## Re-plan Rule

Record a dated Re-plan Log entry before changing corpus scope, purpose, or the fixed skeleton.

## Re-plan Log

- 2026-09-26: Initial bootstrap plan from Human-confirmed scope and gates.
