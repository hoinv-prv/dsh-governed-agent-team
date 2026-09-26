---
artifact_type: aip_exec
artifact_id: AIP-EXEC-016
title: "Recheck GAT reference §§6.6, 6.9, and 7"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN request dated 2026-09-26"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-016
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Recheck GAT reference §§6.6, 6.9, and 7

## SOP Compliance
- Gate U1: the direct HUMAN request fixes the sections, comparison sources, named concerns, and output rule; this is accepted as explicit task confirmation.
- Gate U2: input understanding will be recorded in the workspace.
- Gate U3: open points will be tracked in the workspace.

## Objective
Recheck only §§6.6, 6.9, and 7 of the GAT design/feature reference against the durable-agents MiniMVP and current GAT team-config/tool sources, and report only remaining material discrepancies concerning the nine named prior concerns.

## Selected Task Lens / Mode
- Lens: design_review
- Reason: bounded cross-document conformance review.
- Search/execution effect: prioritize normative specification and implementation evidence.
- Resolved references: direct HUMAN-provided artifact paths plus runtime-review methodology.
- Deferred lookups: none.
- Expansion allowed: yes, but only current team-config/tool sources needed to verify the named concerns.

## Execution Scope
### In Scope
- Target document §§6.6, 6.9, and 7 only.
- Durable-agent MiniMVP clauses relevant to fallback scope, byte limit, route authority, SOUL ordering, per-task loading, manifest snapshots, restart admission, conditional sharing, and filesystem ownership.
- Current GAT team-config and tool sources that implement or constrain those points.

### Out of Scope
- Other target-document sections except cross-references necessary to interpret the scoped text.
- Editing product/design/source artifacts.
- Style or immaterial wording differences.

## Expected Outputs
- Advisory review evidence in the task workspace.
- Final response listing remaining material discrepancies only, or `None.`

## Execution Input Package
### Plan Source
- Direct HUMAN request dated 2026-09-26.

### Required Truth Inputs
- .ai-work/truth/SOP_MASTER.md
- .ai-work/truth/AI_WORK_CONTRACT.md
- .ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT design/feature reference | (none) | docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md | Direct HUMAN path; wiki lookup and semantic retry did not resolve it | [retrieval_gap] |
| Durable agents MiniMVP | (none) | /home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md | Direct HUMAN path; wiki lookup and semantic retry did not resolve it | [retrieval_gap] |
| Runtime review methodology | SRC-METHOD-methodology-20-specs-runtime-review-methodology-mvp-md-cb16 | .ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md | Review reproducibility method | — |

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context available.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Bounded recheck with nine named concerns and discrepancies-only output | “Current sources” means repository state at review time | None | ✅ direct request |

## References to Read First
- docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md
- /home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md
- Current GAT team-config and tool sources discovered from explicit references in the scoped sections and bounded source search.

## Current Risks / Constraints
- Only material semantic/behavioral mismatches are reportable.
- Do not broaden the target-document review beyond §§6.6, 6.9, and 7.

## Known Open Points
- None at creation.

## Workspace Execution Rule
Runtime findings and evidence belong in the workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record the exact bounded review scope and output contract from the direct HUMAN request.

Recommended Mode:
Clarifying

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- Direct HUMAN request

Expected Outputs:
- Task-understanding note and confirmation evidence in workspace

Done Condition:
The workspace records the supplied request as explicit scope confirmation.

Notes / Constraints:
- Do not ask redundant questions because the request is fully specified.

Workspace Actions:
- Record task understanding in findings.

### Step: STEP-01 — Materialize Cross-document Review Scaffold
Objective:
Create a bounded review plan and deterministic runtime review checklist for the scoped comparison.

Recommended Mode:
Reviewing

Applicable Guidelines:
- .ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md

Recommended Skills:
- aiws-review-plan
- aiws-runtime-review-checklist

Inputs:
- The three scoped target sections
- Durable-agent MiniMVP
- Current GAT team-config/tool sources

Expected Outputs:
- review_plan.md
- 06_runtime_review_checklist.md

Done Condition:
Both scaffold artifacts exist in the task workspace and bind checks to the nine named concerns.

Notes / Constraints:
- M2 before M1.

Workspace Actions:
- Write scaffold artifacts to workspace.

### Step: STEP-02 — Verify Corrections Against Specification and Sources
Objective:
Compare each named concern against normative durable-agent requirements and current GAT implementation/configuration evidence.

Recommended Mode:
Reviewing

Applicable Guidelines:
- .ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md

Recommended Skills:
- (none)

Inputs:
- docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md §§6.6, 6.9, and 7
- /home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md
- Current GAT team-config/tool sources

Expected Outputs:
- Evidence matrix and material-discrepancy findings in workspace

Done Condition:
All nine concerns have evidence-bound determinations and every remaining discrepancy cites loci in both target and authority/source.

Notes / Constraints:
- Ignore immaterial wording and out-of-scope issues.

Workspace Actions:
- Record findings and draft final answer.

### Step: STEP-03 — Finalize Review
Objective:
Run capture sweep and scoped lint, then produce the discrepancies-only answer.

Recommended Mode:
Reviewing

Applicable Guidelines:
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- aiws-lint

Inputs:
- Review workspace artifacts

Expected Outputs:
- Clean scoped lint result
- Final concise response

Done Condition:
Scoped lint has zero errors and final output contains only remaining material discrepancies or `None.`

Notes / Constraints:
- Do not include a concern-by-concern success recap when no discrepancies remain.

Workspace Actions:
- Complete final capture sweep and final output.

## Done Criteria
- [ ] Only §§6.6, 6.9, and 7 were reviewed as target text.
- [ ] All nine named concerns were checked against normative and current-source evidence.
- [ ] Remaining material discrepancies only are reported, or `None.`
- [ ] Gates U1–U3 and scoped final lint are satisfied.

## Self-check / Review Points
- Evidence cites exact target/spec/source loci.
- No issue is reported solely because wording differs.
- No success summary leaks into discrepancies-only output.

## Finalization Notes
- Run `python3 .ai-work/tooling/lint_all.py --scope task --workspace <workspace> --aip <this-aip>`.

## Pre-flight Pending Captures
- [IMPORTED 2026-09-26] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="GAT_DESIGN_AND_FEATURE_REFERENCE.md" lookup_query="GAT design feature reference" reason="Reusable project design reference used for cross-document review is not resolved by the wiki index."
- [IMPORTED 2026-09-26] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="DURABLE_AGENTS_MINIMVP.md" lookup_query="durable agents minimum MVP" reason="Reusable shared specification used as review authority is not resolved by the wiki index."

## Re-plan Rule
Macro scope/output changes require a dated Re-plan Log entry before editing earlier sections.

## Re-plan Log
- (no re-plan yet)
