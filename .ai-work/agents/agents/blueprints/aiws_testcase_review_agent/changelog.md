# Changelog — Test Case Review Agent (blueprint)

## 0.2 — 2026-08-16
- **ATDB namespace rename** (CR-AIWS-2026-08-017): `testcase_review_agent` →
  `aiws_testcase_review_agent`; `origin` + `previous_ids` added.
- **`required_core` + `companion_foldable`** added (CR-AIWS-2026-08-012).
- **`document_specific` checklist relocated** to `docs/reference_content/` (CR-AIWS-2026-08-008).
- Why this entry exists: see the note in the DD-review blueprint's 0.2 — content changed in
  v1.2.0 while `blueprint_version` stayed `0.1` (IR-2026-08-15 F10).

## 0.1 — 2026-06-21
- Initial blueprint created (AIP-EXEC-139 / STEP-03), type `review`.
- Mapped from READ-ONLY provenance template:
  - source_template: `docs/agent_pack_impl_package/agent_templates/Document_Review_Agent_Blueprint/`
  - template_version: v0.1
  - inputs used: `templates/REVIEW_AGENT_BLUEPRINT_TEMPLATE.md`, `examples/TESTCASE_REVIEW_AGENT_EXAMPLE.md`
- Mapping applied per `../_shared/review/MAPPING_NOTE_template_to_pack_schema.md`:
  - RENAME: blueprint_name->name, agent_type->type, version->blueprint_version, inputs->input_contract,
    outputs->output_contract (tiers preserved: input required/recommended/optional; output required/optional).
  - ADD: creation_mode: blueprint_based; kept blueprint_id.
  - FOLD: process_docs.* and checklists.common point at the SHARED `../_shared/review/` assets
    (referenced, not copied); only the document-specific checklist is blueprint-local.
  - ADDITIVE: target_document, review_principles, finding_categories, learning_candidate_types,
    review-specific human_gate_policy.required_for — placed after the pack-schema core keys.
- Pack-schema conformance: Detailed Design v0.2 §3 (blueprint schema), key order mirrors the
  precedent `aiws_wiki_meta_strategy_coordinator/blueprint.yaml`.
- HUMAN-confirmed defaults (R-6 / OQ-4): input_contract keeps the `recommended` tier; memory_policy
  carries the full review candidate-type set; human-gate covers final_review_acceptance,
  memory_confirmation, checklist_update, wiki_candidate_promotion, blueprint_improvement,
  conflict_resolution.
- Test-case coverage lens: 11 coverage-axis skills, blueprint-local
  `checklists/testcase_review_checklist.md` (coverage / alignment / readiness checks +
  test-coverage severity examples), finding categories coverage_gap … requirement_trace_gap.
- Conventions: relative cross-ref paths only; plain/literal YAML scalars (NO folded `>-`);
  Wiki-first NOT Wiki-only; no auto-promotion (memory seed empty; learning candidates status=candidate).
- status: active (parity with the sibling review blueprints + blueprint_registry.yaml).
- Registry: add entry to `agents/blueprint_registry.yaml` (see STEP return registry_entry).

## 0.1 — 2026-06-21 (parity pass, AIP-EXEC-139)
- Brought to structural parity with the reference `aiws_detailed_design_review_agent` blueprint:
  - ADD docs: `docs/CUSTOMIZE_GUIDELINES.md`, `docs/INSTANCE_INITIALIZATION_GUIDE.md`,
    `docs/MEMORY_AND_LEARNING_RULES.md` (test-case / coverage lens).
  - ADD `process/README.md` (pointer to the SHARED `../_shared/review/process/` assets; not copied).
  - `output_templates/README.md` already present (pointer to the SHARED review output templates).
  - Folder structure now matches aiws_detailed_design_review_agent.
- blueprint.yaml parity:
  - `status`: draft -> active.
  - `memory_policy`: enriched to the richer review shape — ADD `candidate_queue_required: true`,
    `conflict_with_wiki_policy: report_conflict`, the recommended memory file set (later formalized as the top-level `memory_profile` UNION-8, AP-CR-36); the
    candidate-type set is already carried in the top-level `learning_candidate_types` block.
  - ADD `severity_examples` (test-coverage lens), aligned with checklists §5.

