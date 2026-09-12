# PACKAGE_MANIFEST_v0_5_0

## Package version
- `v0.5.0`

## Canonical doc set

### Core specs
- ARTIFACT_UNDERSTANDING_SPEC_v0_1.md
- ARTIFACT_UNDERSTANDING_OUTPUT_SCHEMA_v0_1.md
- SUPPLEMENTAL_ARTIFACT_STATUS_REFLECTION_MODEL_v0_1.md
- WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1.md
- WIKI_META_INDEX_SPEC_v0_2.md
- WIKI_CHANGE_REQUEST_SPEC_v0_1.md
- WIKI_MINIMAL_GOVERNANCE_RULE_v0_1.md
- AIP_WIKI_INTEGRATION_SPEC_v0_1.md
- WIKI_CANDIDATE_SUGGESTION_RULE_v0_1.md

### Core guidelines
- ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1.md
- WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1.md
- WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1.md
- PROJECT_WIKI_BUILDUP_GUIDELINE_v0_1.md
- AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1.md
- GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1.md
- WIKI_FIRST_RUNTIME_GUIDANCE_v0_1.md
- PRESET_TO_PROJECT_CUSTOMIZATION_RULE_v0_1.md
- WIKI_SOURCE_DISAMBIGUATION_GUIDELINE_v0_1.md

### Core prompts
- PROMPT_ARTIFACT_UNDERSTANDING_v0_1.md
- PROMPT_REVISE_ARTIFACT_UNDERSTANDING_v0_1.md
- PROMPT_GENERATE_CANONICAL_SLOT_MAPPING_v0_1.md
- PROMPT_REVIEW_CONFIRM_MAPPING_AND_META_v0_1.md
- PROMPT_BUILD_WIKI_META_FROM_MAPPING_v0_1.md
- PROMPT_UPDATE_WIKI_META_INCREMENTALLY_v0_1.md
- PROMPT_CUSTOMIZE_AIP_TEMPLATE_FROM_PRESET_v0_1.md
- PROMPT_REVISE_AIP_TEMPLATE_CUSTOMIZATION_v0_1.md

## Install / rollout docs
- install/NEW_INSTALLATION_GUIDE_v0_5_0.md
- install/INSTALL_CHECKLIST_v0_5_0.md
- install/RECOMMENDED_PROJECT_STRUCTURE_v0_5_0.md
- upgrade/UPGRADE_GENERAL_GUIDE_v0_5_0.md
- upgrade/UPGRADE_FROM_v0_3_TO_v0_5_0.md
- upgrade/UPGRADE_FROM_v0_4_TO_v0_5_0.md
- upgrade/MIGRATION_MAP_OLD_TO_NEW_DOCS_v0_5_0.md
- rollout/PROJECT_ROLLOUT_GUIDELINE_v0_5_0.md
- rollout/PROJECT_ONBOARDING_FLOW_v0_5_0.md
- rollout/ROLLOUT_CHECKLIST_v0_5_0.md

## Shipped runtime wiki (aiws namespace)
- The AIWS install also ships a **pre-built, searchable AIWS wiki** in a dedicated **`aiws` namespace** (`.ai-work/wiki_sources/index.aiws.jsonl` + `relations.aiws.jsonl`, pre-built in `payload/aiws_wiki_index/`; rebuild via `build_preset_wiki.py --target .`), queryable via `lookup_wiki_source.py --scope aiws` and traversable via `wiki_relations.py --relations <id>` — separate from the project's own domain wiki (`index.jsonl` / `relations.jsonl`). (CR-AIWS-2026-06-040 / -041; noted per CR-AIWS-2026-06-059; relations preset per CR-AIWS-2026-08-064.)

## Appendix
- execution notes
- sprint backlogs
- deprecated/superseded transition notes

## Missing source files while packaging
- none
