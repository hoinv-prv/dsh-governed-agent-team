---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-wiki-tooling-alignment-patch-guide-mvp-md-44ff
title: methodology / 20_specs/Wiki_Tooling_Alignment_Patch_Guide_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Wiki_Tooling_Alignment_Patch_Guide_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-20T10:16:16.897050+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — methodology / 20_specs/Wiki_Tooling_Alignment_Patch_Guide_MVP.md

## Summary
This guide records the minimal patch map for Wiki Tooling Alignment. The package v0.9.13 applies P0 and part of P1: lookup output boundary lint_wiki boundary checks refresh no-auto-promotion wording build_wiki_source_meta optional field support build_wiki_source_index lightweight projection fields detect/evaluate candidate/signal output fields Wiki skills alignment

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Wiki Tooling Alignment Patch Guide MVP
- Wiki Tooling Alignment Patch Guide MVP Purpose
- Wiki Tooling Alignment Patch Guide MVP Implementation stance
- Wiki Tooling Alignment Patch Guide MVP Patch priority
- Wiki Tooling Alignment Patch Guide MVP P0 patch candidates
- source
- WTA
- Wiki
- wiki
- tooling
- meta
- Patch
- candidate
- accepted
- promotion
- markdown
- patch
- Alignment
- boundary
- refresh
- fields
- payload
- alignment
- lookup
- merge
- Tooling
- Sprint
- update
- guide
- wording
- Knowledge
- Source
- output
- skills
- canonical
- representation
- draft
- mvp
- map
- lint_wiki

## Source-Specific Hints
- heading: Wiki Tooling Alignment Patch Guide MVP
- heading: Purpose
- heading: AIWS_WTA-10_MINIMAL_PATCH_MAP_AND_CANONICAL_MERGE_MAP_v1
- heading: 1. Purpose
- heading: 2. Implementation stance
- heading: 3. Patch priority
- heading: 4. P0 patch candidates
- heading: 5. P1 patch candidates
- heading: 6. P2 / future candidates
- heading: 7. Compatibility test checklist
- heading: 8. Canonical merge targets
- heading: 9. WTA item to canonical destination map
- heading: 10. Core snippets to merge
- heading: 11. Deferred items
- heading: 12. Sprint close readiness check
- heading: 13. Conclusion

## Related Sources
- **SRC-METHOD-methodology-20-specs-wiki-tooling-alignment-spec-mvp-md-1e6e** — role: implements — This guide is the patch/merge map for that spec's decisions: WTA-01..WTA-09 items are mapped here to concrete tool patches (P0/P1/P2) and to canonical merge destinations (§9 table); coupling = the WTA item set and its boundary statements (lookup = routing not verification; refresh = draft not promotion); if the spec's items or boundaries change, this patch map, its targets and its §7 compatibility checklist go stale. [asserted]
- **SRC-METHOD-methodology-20-specs-wiki-tooling-alignment-sprint-merge-summary-md-cf41** — role: companion_design — Same-sprint companion: this guide states the intended patches, the merge summary records which of them actually landed in canonical (§8 lists both as canonical additions); coupling = the P0/P1 patch list and its merge status; the two carry complementary halves — planned patch vs merged outcome — of the same sprint record. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-wiki-meta-index-spec-md-15a8** — role: upstream_input — The optional meta fields the P0-04 patch adds to build_wiki_source_meta.py and the P1-01 patch projects into the index (authority_level, freshness_status, source_representation_status/caution, knowledge_value, intended_ai_use, promotion_status) are meta/index schema fields owned there; coupling = those field names and allowed values; a schema change invalidates the patch targets and the old-meta/new-meta compatibility checklist in §7. [asserted]
- **SRC-METHOD-methodology-20-specs-controlled-knowledge-promotion-spec-mvp-md-0429** — role: system_foundation — The no-auto-promotion boundary these patches encode in tooling (refresh emits draft/candidate by default, apply is explicit + reviewed + logged, detect/evaluate emit signals not approvals — P0-03, P1-02, §10) is the draft/review/apply promotion state machine owned there; coupling = the promotion states and who may transition them; if the promotion model changes, the patched tool output wording and the lint boundary checks must change with it. [asserted]
