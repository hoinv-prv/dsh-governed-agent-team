---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-knowledge-object-model-spec-mvp-md-24ff
title: methodology / 20_specs/Knowledge_Object_Model_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Knowledge_Object_Model_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-08-13T14:26:03.076055+00:00
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
# Wiki Source Meta — methodology / 20_specs/Knowledge_Object_Model_Spec_MVP.md

## Summary
Tài liệu này định nghĩa **đơn vị tri thức (knowledge unit)** của Knowledge Hub trong baseline canonical hiện tại

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Knowledge Unit Model Spec for AI Work System MVP
- for AI Work System MVP Đơn vị tri thức = meta (node_kind artifact object)
- for AI Work System MVP Object node = POINTER, KHÔNG phải container (hard invariant SHAPE 2 forbidden)
- for AI Work System MVP bis.1. Object Kind Catalog (canonical but extensible)
- for AI Work System MVP bis.2. Identity (identity = source_id)
- object
- meta
- node
- artifact
- Object
- INV
- Knowledge
- Sources
- Related
- source_id
- knowledge
- bis
- identity
- model
- node_kind
- layer
- jsonl
- Layer
- aliases
- AIWS
- unit
- core
- object_id
- objects
- metas
- file
- lookup_keys
- F03
- product
- record
- AIP
- concept
- source
- HUMAN
- domain

## Source-Specific Hints
- heading: Knowledge Unit Model Spec for AI Work System MVP
- heading: 1. Purpose of this spec
- heading: 2. Mô hình 2-layer + two-kind node
- heading: 2.1. Đơn vị tri thức = meta (node_kind: artifact | object)
- heading: 2.2. Object node = POINTER, KHÔNG phải container (hard invariant — SHAPE 2 forbidden)
- heading: 3. Identity, naming, và natural-language resolution
- heading: 3bis. Knowledge Object discovery & identity extraction
- heading: 3bis.1. Object Kind Catalog (canonical-but-extensible)
- heading: 3bis.2. Identity (identity = source_id)
- heading: 3bis.3. source_id lifecycle (synthesized core)
- heading: 3bis.4. Discovery hints (heuristic)
- heading: 3bis.5. Inference contract + necessity test (MVP, inference-first)
- heading: 3bis.6. Relations của object node (3 registers — DP4)
- heading: 4. Quan hệ & expansion = `## Related Sources`
- heading: 5. Design goals (intent giữ nguyên, đặt trên substrate 2-layer two-kind node)
- heading: 6. Quan hệ với Working AIP / Use Case
- heading: 7. Cross-references
- heading: 8. Retired shapes — FORBIDDEN (anti-KO stop-line INV-1..INV-9)

## Related Sources
- **SRC-METHOD-methodology-20-specs-knowledge-expansion-link-spec-mvp-md-f5f8** — role: companion_design — This spec is the node half of one model and defers the edge half to it: full semantics of the 3 registers and of the relationship roles live there; coupling = the relation-type registry and register-membership rules that an object node's `## Related Sources` out-edges must use (INV-4 requires at least one out-edge); a change to the register set or type registry changes which edges an object node may legally carry. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-wiki-meta-index-spec-md-15a8** — role: system_foundation — An object node is not a separate record: it is written as an ordinary source meta in the schema owned there and lands in the same slim index.jsonl; coupling = the frontmatter keys node_kind, source_id, artifact_locator (the __OBJECT__ sentinel, INV-9), lookup_keys/aliases, plus the index projection; a change to the meta frontmatter or index fields changes how object nodes are stored, linted and found. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-lookup-key-strategy-spec-mvp-md-1b67** — role: upstream_input — Object identity and findability are expressed with the key tiers owned there: official ID/name to T1, multilingual names to aliases, natural phrasing matched via T2/T3 (§3, §3bis.2 here); coupling = the tier definitions and the lookup_keys/aliases fields an object meta must populate; a change to tiering or key rules changes whether an object node (e.g. bare `F03` for SRC-FUNC-F03) is resolvable by ordinary lookup. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-artifact-type-taxonomy-spec-mvp-md-2ff4** — role: upstream_input — The §3bis.4 discovery hints consume `classification_signals` from the artifact-type taxonomy as the heuristic input for locating object candidates in real documents; coupling = that field's name and content per artifact_type; if the signals are renamed or re-scoped, the object-discovery hints stop resolving. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-wiki-knowledge-profile-spec-md-5ec8** — role: upstream_input — The §3bis.4 discovery hints consume `object_extraction_targets` from the knowledge profile — the per-artifact-type declaration of which objects to extract; coupling = that field as carried in profiles/*.yml; dropping or renaming it removes the input that drives object candidate proposals. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-artifact-understanding-output-schema-md-244e** — role: upstream_input — Object candidates are read out of the artifact-understanding output field `key_objects_and_terms`, which that schema owns; coupling = that output field; if the understanding output schema drops or renames it, the object-discovery pass loses its input record. [asserted]
- **SRC-METHOD-methodology-20-specs-knowledge-routing-spec-mvp-md-e9f4** — role: downstream_target — Routing resolves an object/concept to an object-node meta (node_kind=object) when one exists, else to the describing artifact metas, then expands over its `## Related Sources`; coupling = node_kind, source_id identity and the out-edge registers defined here; a change to object identity, kinds or the __OBJECT__ locator changes what routing can resolve and expand. [asserted]
- **SRC-METHOD-methodology-20-specs-knowledge-access-interface-spec-mvp-md-0086** — role: downstream_target — The access capabilities resolve_object_or_concept / retrieve_object_profile / expand_from_object read the object-node meta defined here, and for an object node (artifact_locator=__OBJECT__, no file) inspect_source_anchor is redefined as following `represented_by` edges; coupling = node_kind, the __OBJECT__ sentinel and the three registers; a change to either breaks the capability contract that tool/RAG/MCP adapters map onto. [asserted]
