---
artifact_type: wiki_source_meta
source_id: SRC-PRESET-preset-knowledge-aip-exec-design-aip-exec-createdesigndoc-md-7f34
title: preset_knowledge / aip_exec/design/AIP_EXEC_CreateDesignDoc.md
source_type: methodology_spec
artifact_locator: .ai-work/preset_knowledge/aip_exec/design/AIP_EXEC_CreateDesignDoc.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-20T10:15:22.016695+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — preset_knowledge / aip_exec/design/AIP_EXEC_CreateDesignDoc.md

## Summary
Preset AIP_EXEC template for authoring a design document (Basic Design / Detail Design / Screen Design): objective, scope, inputs, and steps to produce the design. AI use: instantiate when the task is to create a BD/DD/screen design document.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- AIP_EXEC Create Design Document
- AIP_EXEC Create Design Document SOP Compliance
- AIP_EXEC Create Design Document Objective
- AIP_EXEC Create Design Document Selected Task Lens / Mode
- AIP_EXEC Create Design Document Execution Scope
- BrSE
- requirements
- scope
- points
- AIP
- Done
- Points
- inputs
- Inputs
- Requirements
- Workspace
- doc
- confirmed
- understanding
- Objective
- Self
- Expected
- Outputs
- Constraints
- sections
- dung
- draft
- Log
- Architecture
- context
- Recommended
- Guidelines
- Condition
- Actions
- aip
- exec
- createdesigndoc
- owner
- Gate
- log

## Source-Specific Hints
- heading: AIP_EXEC — Create Design Document
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

## Related Sources
- **SRC-PRESET-preset-knowledge-aip-exec-review-aip-exec-reviewdesign-md-a9be** — role: related — The two presets partition the design task space: this one only authors a BD/DD/Screen Design, and its Out of Scope routes any review-of-someone-else's-design to AIP_EXEC_ReviewDesign. They share no inputs or outputs (no data coupling) — the dependency is preset selection: whoever must decide author-vs-review needs both scope boundaries, and if one preset's boundary moves the other's Out of Scope list must move with it. [asserted]
- **SRC-PRESET-preset-knowledge-review-support-aip-review-checklist-v0-3-md-c84e** — role: output_template — STEP-04 of this preset (self-review of the design draft before the BrSE checkpoint) names AIP_REVIEW_CHECKLIST_v0_3 as its Applicable Guidelines — the checklist supplies the criteria set the draft design document is graded against at that quality gate. Coupling = that criteria set; if the checklist adds/removes criteria, the pass condition of this preset's self-review step changes with it. [asserted]
