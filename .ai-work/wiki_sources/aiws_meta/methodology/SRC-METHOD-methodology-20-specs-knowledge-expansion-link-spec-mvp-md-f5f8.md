---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-knowledge-expansion-link-spec-mvp-md-f5f8
title: methodology / 20_specs/Knowledge_Expansion_Link_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Knowledge_Expansion_Link_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-08-13T14:26:03.355170+00:00
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
# Wiki Source Meta — methodology / 20_specs/Knowledge_Expansion_Link_Spec_MVP.md

## Summary
Spec này định nghĩa **quan hệ tri thức có hướng** giữa các artifact trong Knowledge Hub (mô hình 2-layer),

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Knowledge Relationship (Related Sources) Spec for AI Work System MVP
- for AI Work System MVP Là gì
- for AI Work System MVP Không là gì
- for AI Work System MVP Related Sources
- for AI Work System MVP Three relation registers two kind node)
- Related
- Sources
- jsonl
- node
- quan
- relations
- artifact
- Object
- meta
- intent
- AIWS
- edge
- coupling
- Knowledge
- object
- reverse
- F03
- expansion
- F04
- knowledge
- typed
- layer
- confidence
- hop
- task
- upstream_input
- edges
- expansion_links
- contract
- projection
- related
- model
- asserted
- graph
- Artifact

## Source-Specific Hints
- heading: Knowledge Relationship (Related Sources) Spec for AI Work System MVP
- heading: 1. Purpose of this spec
- heading: 2. Một relationship (`## Related Sources` entry) là gì / không là gì
- heading: 2.1. Là gì
- heading: 2.2. Không là gì
- heading: 3. Cấu trúc một `## Related Sources` entry
- heading: 4. Relation type registry (typed relations)
- heading: 4.0. Three relation registers (v0.5 — two-kind node)
- heading: 4.1. Open registry + extension (CR-022 OP-4)
- heading: 4.2. Confidence note (optional; net-new ở v0.4)
- heading: 4.3. Entry line format (v0.4)
- heading: 4.4. Basis note: objective stakes, intent-agnostic (CR-AIWS-2026-06-002)
- heading: 5. Lens-aware expansion (intent giữ nguyên)
- heading: 6. Three-Way Separation (2-layer) — ba cơ chế cross-artifact
- heading: 6A. `relations.jsonl` — queryable projection (reverse index) [v0.4, CR-022]
- heading: 7. Cross-references

## Related Sources
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-wiki-meta-index-spec-md-15a8** — role: system_foundation — The edges this spec defines are stored as bullets inside the `## Related Sources` block of an artifact meta, and that meta/index record model (2-layer: meta file + slim index.jsonl) is owned there; coupling = the section heading name, the bullet fields (SRC-id / role / basis / confidence) and the frontmatter keys the endpoints resolve against (source_id, node_kind, artifact_locator); a change to the meta schema or that block changes what build_relations.py can parse and what relations.jsonl can project. [asserted]
- **SRC-METHOD-methodology-20-specs-knowledge-object-model-spec-mvp-md-24ff** — role: companion_design — Defines the NODES the edges here connect (node_kind object vs artifact, source_id identity, __OBJECT__ locator, DP5/INV-3 no-rollup); coupling = endpoint node_kind, which selects the permitted relation register and type (documentary / representation `represented_by` / domain `x:`) per §4 and §6A here against §3bis.6 there; a change to the node kinds or to the no-rollup invariant changes which relation types are legal on an edge. [asserted]
