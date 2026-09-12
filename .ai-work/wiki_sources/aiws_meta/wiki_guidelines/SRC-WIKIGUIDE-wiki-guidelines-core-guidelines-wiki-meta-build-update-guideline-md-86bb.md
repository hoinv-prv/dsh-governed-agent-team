---
artifact_type: wiki_source_meta
source_id: SRC-WIKIGUIDE-wiki-guidelines-core-guidelines-wiki-meta-build-update-guideline-md-86bb
title: wiki_guidelines / core/guidelines/WIKI_META_BUILD_UPDATE_GUIDELINE.md
source_type: wiki_guideline
artifact_locator: .ai-work/truth/canonical/wiki_guidelines/core/guidelines/WIKI_META_BUILD_UPDATE_GUIDELINE.md
profile_id: wiki_guideline
status: active
updated_at: 2026-08-13T14:33:12.477347+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
source_representation_quality_issue: False
maintenance_status: active
representation_scope: unknown
representation_type: markdown
system: aiws
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — wiki_guidelines / core/guidelines/WIKI_META_BUILD_UPDATE_GUIDELINE.md

## Summary
— typed cross-artifact relationships (retired KO record — xem `Knowledge_Object_Model_Spec_MVP` §8)

## Knowledge Targets
- reference
- pattern
- domain

## Lookup Keys
- WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1 Related Specs (Other Layer)
- WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1 Purpose
- WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1 What this guideline is for
- WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1 Foundational principles
- WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1
- meta
- build
- update
- artifact
- source
- mapping
- object
- project
- Meta
- Related
- Source
- Sources
- wiki
- AIWS
- layer
- Wiki
- canonical
- relation
- Project
- pattern
- unresolved
- fields
- API
- Mapping
- profile
- slot
- record
- Pattern
- PMP
- Build
- enrichment
- CB01001
- reflection
- should
- alias

## Source-Specific Hints
- heading: WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1
- heading: Related Specs (Other Layer)
- heading: 1. Purpose
- heading: 2. What this guideline is for
- heading: 3. Foundational principles
- heading: 4. Main inputs for meta build/update
- heading: 5. Main output targets
- heading: 6. Initial meta build flow
- heading: 7. Incremental meta update flow
- heading: 8. Canonical mapping → meta conversion rule
- heading: 9. Project mapping pattern interaction rule
- heading: 10. Project-customized meta enrichment rule
- heading: 11. Supplemental artifact handling rule
- heading: 12. Relation build rule
- heading: 13. Suggested build/update outputs
- heading: 14. Suggested minimal review checklist
- heading: 15. Common pitfalls
- heading: 16. If missing then do
- heading: 17. Completion criteria for BL-12
- heading: v0.9.8 Build/update compatibility addendum
- heading: CR-D4 Addendum — Split Design Pattern (2026-05-25)
- heading: 18. Split Design Pattern — Multi-artifact, Single-object
- heading: CR-G4 Addendum — Appendix A: Wiki Source Meta Build Checklist (2026-05-25)
- heading: Appendix A: Wiki Source Meta Build Checklist
- heading: CR-D3 Addendum — Sample-First Build Flow (2026-05-25)
- heading: 20. Sample-First Build Flow
- heading: CR-G1 Addendum — Operational Flow (Command-Level) (2026-05-25)
- heading: 21. Operational Flow (Command-Level)
- heading: Semantic Override Args + Step 0 + Slim Meta — 2026-05-27 Addendum

## Related Sources
- **SRC-METHOD-methodology-20-specs-controlled-knowledge-promotion-spec-mvp-md-0429** — role: upstream_input — The pre-apply gate of the meta update flow (Appendix A §7E) reads the Promotion trigger list (CR-D8) defined in Controlled_Knowledge_Promotion_Spec_MVP: if an update matches a trigger (set knowledge_class=source_of_truth, change a referenced source_id, split/merge metas, deprecate, change Related Sources between major artifacts) the lightweight update MUST stop and go through CR + wiki manager. Coupling = that trigger list; adding or removing a trigger there changes which meta edits may be applied directly. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-guidelines-wiki-profile-generation-customization-guideline-md-d049** — role: upstream_input — Meta extraction is driven by the profile plus the Project Mapping Pattern (`pmp_<profile_id>.yml`, which takes precedence for extraction logic while the profile still supplies `knowledge_targets`); the PMP schema, its canonical path next to the profile, and the Profile-vs-PMP precedence rule are defined in WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE. Coupling = profile/PMP schema + precedence + file path; a change there changes what `build_wiki_source_meta.py` extracts into every meta built or refreshed under this guideline. [asserted]
