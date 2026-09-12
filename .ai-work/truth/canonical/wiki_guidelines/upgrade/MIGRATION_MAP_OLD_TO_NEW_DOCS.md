# MIGRATION_MAP_OLD_TO_NEW_DOCS_v0_5_0.md

## Superseded / renamed concepts

### Old separated profile docs
- `WIKI_ARTIFACT_PROFILE_SPEC_v0_1`
- `WIKI_USAGE_PROFILE_SPEC_v0_1`

### New canonical concept
- `WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1`

### Meaning
The previous artifact-profile / usage-profile split is replaced by a unified knowledge-profile concept on the knowledge side, while `Task Lens` remains separate for task → knowledge routing.

## Old-to-new practical mapping

- old artifact understanding logic
  → `ARTIFACT_UNDERSTANDING_SPEC_v0_1`
  + `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1`

- older project-specific understanding tweaks
  → `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1`

- older ad hoc meta build/update notes
  → `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`

- older add-to-wiki or update behavior
  → `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1`
  + `WIKI_CHANGE_REQUEST_SPEC_v0_1`
  + `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`

- older wiki-related AIP tweaks
  → `AIP_WIKI_INTEGRATION_SPEC_v0_1`
  + `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1`

- older runtime practices
  → `WIKI_FIRST_RUNTIME_GUIDANCE_v0_1`

## Recommended migration note
Projects should preserve useful project-local decisions, but remap them into:
- preset/common
- project-specific
- task-instance
using `PRESET_TO_PROJECT_CUSTOMIZATION_RULE_v0_1`
