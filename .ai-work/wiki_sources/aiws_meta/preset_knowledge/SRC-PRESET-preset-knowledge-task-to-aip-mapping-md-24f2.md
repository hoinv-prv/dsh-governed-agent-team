---
artifact_type: wiki_source_meta
source_id: SRC-PRESET-preset-knowledge-task-to-aip-mapping-md-24f2
title: preset_knowledge / TASK_TO_AIP_MAPPING.md
source_type: methodology_spec
artifact_locator: .ai-work/preset_knowledge/TASK_TO_AIP_MAPPING.md
profile_id: methodology_spec
status: active
updated_at: 2026-04-25T01:17:48.925881+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — preset_knowledge / TASK_TO_AIP_MAPPING.md

## Summary
Mapping table from task type to AIP type + Task Lens + main output (e.g., design new spec->EXEC, review canonical artifact->EXEC, build/rebuild wiki source meta->EXEC build_wiki_meta lens, investigate spec gap->PLAN->EXEC, create AIP template->EXEC, version bump->EXEC, apply CR->EXEC), plus the BrSE preset tasks and their mandatory-AIP policy. AI use: decide which AIP type and lens a task needs.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Task to AIP Mapping AI Work System Design Project
- AI Work System Design Project Quick reference table
- AI Work System Design Project BrSE Preset Tasks (from preset_knowledge/)
- AI Work System Design Project Dependency Reminders
- EXEC
- task
- AIP
- PLAN
- canonical
- artifact
- aip_exec
- aip_samples
- Usually
- depends
- aip
- design_methodology_artifact
- meta
- mapping
- Task
- wiki
- Updated
- CLAUDE
- local
- preset_knowledge
- test
- recommended
- communication
- WKP
- scope
- workspace
- bump
- package
- folder
- requirement
- current
- AIWS
- yml
- Mapping
- System
- Project

## Source-Specific Hints
- heading: Task to AIP Mapping — AI Work System Design Project
- heading: Quick reference table
- heading: BrSE Preset Tasks (from preset_knowledge/)
- heading: Dependency Reminders

## Related Sources
- **SRC-METHOD-methodology-20-specs-aip-detail-spec-mvp-md-f024** — role: upstream_input — The 'Design new spec' dependency reminder names AIP_Detail_Spec_MVP as the structure-compliance input for the AIP produced by that task. Coupling = the AIP schema (frontmatter, required sections, step structure) every PLAN/EXEC this table routes must satisfy; a schema change there moves the compliance bar for the mapped tasks. [asserted]
- **SRC-PRESET-preset-knowledge-aip-exec-requirement-aip-exec-clarifyreq-meetingtord-md-105e** — role: downstream_navigation — The preset-task table routes the task 'Clarify requirements từ meeting transcript' straight to this EXEC preset file (standalone EXEC, output = RD / clarification document) — it is the only row naming a preset file rather than a folder. If that preset is renamed, moved or replaced, this row resolves to nothing. [asserted]
- **SRC-PRESET-preset-knowledge-preset-index-md-3cce** — role: downstream_navigation — This mapping table names preset FOLDERS (`aip_samples/design/`, `aip_exec/testcase/` …) and delegates the full file listing to PRESET_INDEX, which is the catalogue of preset_knowledge. Coupling = the preset library's file inventory: a reader must open the index to resolve a folder pointer here into an actual preset file, and newly added or renamed presets surface in the index first. [asserted]
- **SRC-PRESET-preset-knowledge-review-support-aip-review-checklist-v0-3-md-c84e** — role: upstream_input — The 'Review canonical artifact' dependency reminder names this checklist a required input for the review task this table routes; it supplies the conformance criteria and the pass/fail gate that produce that row's 'Review findings' output. Criteria changes there change what the mapped review task must cover. [asserted]
- **SRC-PRESET-preset-knowledge-review-support-aip-review-guideline-v0-3-md-e982** — role: upstream_input — The 'Review canonical artifact' dependency reminder names this guideline a required input alongside the checklist; it supplies the per-criterion rationale (Purpose / Anti-pattern / Spec ref) used to decide pass/fail during the review task this table routes. Its entries are keyed to the checklist's criterion IDs. [asserted]
