---
artifact_type: wiki_source_meta
source_id: SRC-PRESET-preset-knowledge-aip-exec-review-aip-exec-reviewdesign-md-a9be
title: preset_knowledge / aip_exec/review/AIP_EXEC_ReviewDesign.md
source_type: methodology_spec
artifact_locator: .ai-work/preset_knowledge/aip_exec/review/AIP_EXEC_ReviewDesign.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-25T01:38:50.842519+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — preset_knowledge / aip_exec/review/AIP_EXEC_ReviewDesign.md

## Summary
Preset AIP_EXEC template for reviewing a design document (Basic Design / Detail Design / Screen Design): review scope, criteria, steps, and outputs. AI use: instantiate when the task is to review a design document.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- AIP_EXEC Review Design Document
- AIP_EXEC Review Design Document SOP Compliance
- AIP_EXEC Review Design Document Objective
- AIP_EXEC Review Design Document Selected Task Lens / Mode
- AIP_EXEC Review Design Document Execution Scope
- BrSE
- findings
- requirement
- Checklist
- Understanding
- Comment
- scope
- ghi
- severity
- checklist
- downstream
- Outputs
- specific
- project
- Done
- understandings
- Workspace
- confirmed
- Objective
- dimensions
- Requirement
- handoff
- Expected
- Inputs
- Constraints
- Critical
- finding
- Recommended
- Guidelines
- Condition
- Actions
- AIP
- baseline
- owner
- Write

## Source-Specific Hints
- heading: AIP_EXEC — Review Design Document
- heading: SOP Compliance
- heading: Objective
- heading: Selected Task Lens / Mode
- heading: Execution Scope
- heading: Expected Outputs
- heading: Execution Input Package
- heading: Input Understanding
- heading: References to Read First
- heading: Current Risks / Constraints
- heading: Known Open Points
- heading: Workspace Execution Rule
- heading: Execution Steps
- heading: Done Criteria
- heading: Self-check / Review Points
- heading: Finalization Notes
- heading: Re-plan Rule
- heading: Re-plan Log
- heading: Guidance Notes
- heading: Changelog

## Related Sources
- **SRC-PRESET-preset-knowledge-aip-exec-design-aip-exec-createdesigndoc-md-7f34** — role: related — Complementary half of the design task space: this preset only reviews an existing design and explicitly forbids creating one (and forbids editing the document under review — it outputs findings only), routing any authoring work to AIP_EXEC_CreateDesignDoc. No shared inputs or outputs; needed to pick the correct preset, and the two Out-of-Scope boundaries must stay mutually consistent. [asserted]
- **SRC-PRESET-preset-knowledge-aip-samples-review-aip-sample-reviewdesign-shared-md-de6d** — role: upstream_input — AIP_Sample_ReviewDesign_Shared is the mapped PLAN-phase sample for this review EXEC: the EXEC's entry conditions require a PLAN (or equivalent) to have fixed the review scope/objective and BrSE-confirmed input understandings, and those are exactly what that PLAN sample produces and hands off. Coupling = the PLAN handoff set (review scope, confirmed understandings, downstream consumer of findings); if it changes, this EXEC's Workspace Preconditions and Mode A/B/C baseline assumptions no longer hold. [asserted]
