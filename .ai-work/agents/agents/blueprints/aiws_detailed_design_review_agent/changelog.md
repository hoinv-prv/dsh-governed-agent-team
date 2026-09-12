# Changelog — Detailed Design Review Agent (blueprint)

## 0.2 — 2026-08-16
- **ATDB namespace rename** (CR-AIWS-2026-08-017): blueprint id `detailed_design_review_agent`
  → `aiws_detailed_design_review_agent`; `origin` + `previous_ids` added.
- **`required_core` + `companion_foldable`** added (CR-AIWS-2026-08-012).
- **`document_specific` checklist relocated** to `docs/reference_content/` and the
  blueprint-local `checklists/` directory removed (CR-AIWS-2026-08-008).
- Why this entry exists: v1.2.0 shipped all of the above while `blueprint_version` stayed
  `0.1`. `/aiws-agent-upgrade` compares that field to decide whether a desk is behind, and
  presents this changelog as the WHY a HUMAN reconciles against (spec §4A). With the version
  frozen, the comparison said "no change" while the snapshot said DRIFT, and the text put in
  front of the HUMAN described only the 0.1 birth. The gate stayed open with nothing to
  decide on (IR-2026-08-15 F10). Bumping without a changelog entry would have fixed the
  signal and left the explanation missing — so both move together, and CR-AIWS-2026-08-074
  C5 adds the guard that keeps them together.

## 0.1 — 2026-06-21
- Initial blueprint created (AIP-EXEC-139 / STEP-02). type: review.
- Review/advisory agent for Detailed Design documents: mission, responsibilities,
  non-responsibilities (forbid approve / edit / auto-update Wiki / auto-promote / silent conflict
  resolution), input_contract (required/recommended/optional tiers), output_contract
  (required/optional), 13 common + 10 detailed-design-specific skills, default_tools: [], richer
  review memory_policy (candidate_queue_required, report_conflict, 7 recommended memory files),
  workspace_policy, human_gate_policy.
- Additive blocks (template-unique, no pack-schema home): target_document, review_principles
  (incl. wiki_grounded_not_wiki_only = Wiki-first NOT Wiki-only), finding_categories,
  severity_examples (detailed-design), learning_candidate_types.
- FOLD: process_docs / common checklist / output_templates reference SHARED assets under
  `../_shared/review/` via relative paths (not copied); blueprint-local only:
  `checklists/detailed_design_review_checklist.md`.
- Default memory seed created EMPTY (no auto-promotion; no unapproved seed).
- Docs: CUSTOMIZE_GUIDELINES.md, INSTANCE_INITIALIZATION_GUIDE.md, MEMORY_AND_LEARNING_RULES.md.
- To register in `agents/blueprint_registry.yaml` (entry returned by STEP-02; registry edit owned by
  the registry-update step).

### Provenance
- source_template: docs/agent_pack_impl_package/agent_templates/Document_Review_Agent_Blueprint
- template_version: v0.1
- mapping_note: ../_shared/review/MAPPING_NOTE_template_to_pack_schema.md
- target_schema: docs/agent_pack_impl_package/docs/04_Detailed_Design.md (§1 folder, §3 blueprint)
- on_disk_precedent_mirrored: development/ai_agents/agents/blueprints/aiws_wiki_meta_strategy_coordinator/
- mapping_rules_applied: RENAME (blueprint_name->name, agent_type->type, version->blueprint_version,
  inputs->input_contract, outputs->output_contract); ADD (creation_mode: blueprint_based,
  blueprint_id); FOLD (process/checklist/output -> shared relative refs).

### Phase-I note (AP-CR-04)
- This blueprint is the Phase-I Detailed Design Review (DDR) merge base — built complete + mappable.
- The ai_assisstant feature is intentionally NOT merged here.

## 0.1.1 — 2026-06-21 — Phase I DDR-assistant absorb (AIP-EXEC-140 / STEP-03)

Absorbed the genuine strengths of the `ai_assisstant` Detail Design Review Assistant (DDR)
ADDITIVELY into this blueprint (agent = base/priority per AP-CR-04; additive-only, no override).
Gap/strength analysis: `../../../assistant_to_agent_mapping.md` (STEP-02). To-absorb list = 1 item.

- ADD `memory_load_policy` block (new keys only): `load_confirmed_only: true`,
  `load_order: newest_first`, `load_cap: 50`.
  - Rationale: the DDR config stated explicit confirmed-memory LOAD-at-run-start semantics that
    the agent's `memory_policy` (which governs CAPTURE/PROMOTION gating) did not express. This is
    the single genuine blueprint-layer directive the agent lacked.
  - Guarantee: ADDITIVE — no existing `memory_policy` key or value was modified.
  - absorbed_from: ai_assisstant DDR (`_aiws_assistants/assistants/detail_design_review/assistant_config.json` -> `memory_policy.load_confirmed_only` / `load_order` / `load_cap`; reinforced in `.claude/agents/detail-design-reviewer.md` step 5).

NOT absorbed (recorded in mapping STEP-02 + parity report STEP-04), with reason:
- Advisory session-lock (`session_policy`/`runtime_identity_policy`) — DROP: wrong layer (OQ-I1,
  runtime/instance concern), handled by instance `workspace/active_runs/` + Runtime Command Set (EXEC-142).
- ID conventions (`ID_CONVENTIONS.md`) — DROP: wrong layer (OQ-I1); agent model has its own id scheme (§4/§14/§15 + RUN-... ids).
- `.claude/` subagent + create/run/train skills — DROP: runtime command surface (EXEC-142 scope), not a blueprint field.
- `memory/examples/{good,bad}_outputs.md` — DROP: unapproved placeholder content; would violate no-unapproved-seed (instance memory stays EMPTY, HUMAN-seeded only). Findings-quality intent already covered by `review_principles.avoid_generic_findings`.
- All other DDR capabilities (mission, memory-policy gating, 5 review skills, knowledge/checklist,
  HUMAN-gate set, AIP/history policy, output contract) — already-covered: the agent is a strict
  superset; no graft (OQ-I2 — minimal graft acceptable).
