---
artifact_type: aip_exec
artifact_id: AIP-EXEC-019
title: "Make AIP usage optional by default"
status: draft
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "direct-user-request-2026-09-26"
template_source: AIP_EXEC_TEMPLATE
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Make AIP usage optional by default

## Governance Note

- STEP-01 through STEP-02 produce and review a change request; they do not alter Truth.
- STEP-03 changes `.ai-work/truth/SOP_MASTER.md`, so it is a canonical-edit HARD GATE and requires an approved change request.
- STEP-03 also changes the local, package-owned core-rule source `.ai-work/AIWS.md` and refreshes the generated AIWS block in `AGENTS.md`.

## Objective

Adopt the Human-directed policy that AIPs are optional by default in this repository. An AIP is created only when the Human requests one or when an explicitly approved project process requires one.

## Selected Task Lens / Mode

- Lens: No-Lens
- Reason: A narrow policy and governance update with no product-domain inputs.
- Search/execution effect: Resolve Truth and the indexed AIP/change-control methodology only.
- Resolved references: AIP Detail Spec and AIWS Change Request Spec.
- Deferred lookups: none.
- Expansion allowed: yes, when needed to validate change-control requirements.

## Execution Scope

### In Scope

- Draft a change request for the policy override.
- After Human approval, update the SOP and `.ai-work/AIWS.md`.
- Refresh the generated AIWS block in `AGENTS.md` so it reflects the revised core rules.

### Out of Scope

- Changing the upstream AIWS package or canonical methodology files.
- Changing project Truth other than `SOP_MASTER.md`.
- Requiring AIPs retroactively for existing work.

## Expected Outputs

- A reviewed, Human-approved change request.
- Updated `.ai-work/truth/SOP_MASTER.md` and `.ai-work/AIWS.md`.
- Refreshed AIWS block in `AGENTS.md` and verification evidence in the task workspace.

## Execution Input Package

### Plan Source

- Direct Human request dated 2026-09-26.

### Required Truth Inputs

- `.ai-work/truth/SOP_MASTER.md` (currently empty)
- `.ai-work/truth/AI_WORK_CONTRACT.md` (currently empty)

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| AIP Detail Spec | SRC-METHOD-methodology-20-specs-aip-detail-spec-mvp-md-f024 | `.ai-work/truth/canonical/methodology/20_specs/AIP_Detail_Spec_MVP.md` | Current AIP default policy | — |
| AIWS Change Request Spec | SRC-METHOD-methodology-20-specs-aiws-change-request-spec-mvp-md-1b40 | `.ai-work/truth/canonical/methodology/20_specs/AIWS_Change_Request_Spec_MVP.md` | Canonical-change approval process | — |

## References to Read First

- `.ai-work/truth/canonical/methodology/20_specs/AIP_Detail_Spec_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/AIWS_Change_Request_Spec_MVP.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`

## Current Risks / Constraints

- The project SOP and contract are empty, so the CR must supply a concise, explicit policy without inventing unrelated governance.
- The core rule source is normally package-owned and may be overwritten by a future AIWS upgrade; the project-specific SOP remains the authoritative local override.
- No Truth file may change until the Human approves the CR.

## Known Open Points

- The intended wording is interpreted as: do not create an AIP by default; create one only on explicit Human request or an explicitly approved project process.

## Execution Steps

### Step: STEP-01 — Draft policy change request
Objective:
Create a narrowly scoped CR that records the new default and its interaction with existing AIWS methodology.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/20_specs/AIWS_Change_Request_Spec_MVP.md`

Inputs:
- Direct Human request
- Declared Truth and wiki inputs

Expected Outputs:
- Draft CR with target files, proposed wording, risk assessment, and verification plan

Done Condition:
- CR is ready for Human review and approval.

Notes / Constraints:
- Do not edit Truth or generated rule blocks in this step.

### Step: STEP-02 — Obtain Human approval
Objective:
Present the exact CR for approval.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/20_specs/AIWS_Change_Request_Spec_MVP.md`

Inputs:
- Draft CR

Expected Outputs:
- Explicit Human approval or revision request

Done Condition:
- Approval is recorded for the final CR content.

Notes / Constraints:
- Approval is required before STEP-03.

### Step: STEP-03 — Apply approved policy override
Objective:
Apply the approved SOP and core-rule policy, then render and verify the generated agent rule block.

Recommended Mode:
Canonical-edit

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-pkg/operations/upgrade.md`

Inputs:
- Approved CR

Expected Outputs:
- Updated SOP, core rules, and generated agent rule block

Done Condition:
- `compose_aiws_rules.py --check` and the applicable lint command pass.

Notes / Constraints:
- Preserve project-owned text outside the AIWS block.

## Done Criteria

- AIP and CR pass their applicable lint checks.
- Human approval precedes every Truth edit.
- The final SOP makes AIP use optional by default without weakening the separate CR approval requirement for Truth changes.
- Generated rule files agree with `.ai-work/AIWS.md`.

## Self-check / Review Points

- Verify that the SOP is the explicit project-level override for the local methodology.
- Verify that no wording accidentally makes CR approval optional for Truth changes.
- Verify the AGENTS block changes only inside its AIWS markers.

## Re-plan Rule

Record a dated Re-plan Log entry before changing scope, target files, or the policy meaning.

## Re-plan Log

- 2026-09-26: Initial scope created from the Human request to make AIP usage optional by default.
