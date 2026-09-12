# CHANGELOG_v0_5_0

## Summary
This release packages the full Wiki sprint into a rollout/installable doc set.

## Main additions compared with older package generations
- unified canonical Wiki spec/guideline/prompt set
- install guidance for new projects
- upgrade guidance from `v0.3` and `v0.4`
- rollout guidance for project adoption
- guideline index / flow navigator as entry point
- semantic-to-canonical mapping guidance
- project mapping pattern rule
- Wiki-first runtime guidance
- preset-to-project customization rule

## Important conceptual changes
- `Wiki Artifact Profile` + `Wiki Usage Profile` are superseded by `Wiki Knowledge Profile`
- runtime is clarified as **Wiki-first, not Wiki-only**
- candidate / CR / governance flow is explicitly formalized
- AIP-Wiki integration is clarified with deliverable/wiki-eligible/add-to-wiki handoff behavior
- canonical mapping and project-customized meta enrichment are now first-class parts of the process

## Upgrade-sensitive changes
- projects relying on older separated profile concepts should migrate to `WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1`
- projects with ad hoc Wiki update behavior should align to:
  - `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1`
  - `WIKI_CHANGE_REQUEST_SPEC_v0_1`
  - `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`
- projects using old AIP templates should review:
  - `AIP_WIKI_INTEGRATION_SPEC_v0_1`
  - `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1`
  - `PRESET_TO_PROJECT_CUSTOMIZATION_RULE_v0_1`
