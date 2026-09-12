---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-knowledge-routing-spec-mvp-md-e9f4
title: methodology / 20_specs/Knowledge_Routing_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Knowledge_Routing_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-20T10:16:16.734940+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — methodology / 20_specs/Knowledge_Routing_Spec_MVP.md

## Summary
The Knowledge Hub design should be updated to reflect the following for Knowledge Routing: 1. Define routing as a task-lens-aware mechanism for finding, filtering, expanding, and stopping in Knowledge Hub. 2. Route through five logical layers: Task Lens Domain Scope precedence Object/concept resolution Expansion 3. Support multiple scope precedence modes: project-first common-first local-first ...

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Knowledge Routing Spec for AI Work System MVP
- for AI Work System MVP Related Specs (Other Layer)
- for AI Work System MVP What Knowledge Routing is
- for AI Work System MVP What Knowledge Routing is not
- for AI Work System MVP Wiki first by default
- source
- Knowledge
- routing
- wiki
- task
- lens
- Routing
- raw
- Wiki
- Lens
- object
- expansion
- folder
- knowledge
- scope
- Task
- Hub
- artifact
- concept
- should
- grep
- search
- evidence
- related
- current
- runtime
- Meta
- Expansion
- research
- decision
- AIP
- meta
- objects
- context
- local

## Source-Specific Hints
- heading: Knowledge Routing Spec for AI Work System MVP
- heading: Related Specs (Other Layer)
- heading: 1. Purpose of this spec
- heading: 2. What Knowledge Routing is / is not
- heading: 2.1. What Knowledge Routing is
- heading: 2.2. What Knowledge Routing is not
- heading: 3. Core routing principles
- heading: 3.1. Wiki-first by default
- heading: 3.2. Resolve before deep expansion
- heading: 3.3. Search should be task-lens-aware
- heading: 3.4. Expansion should be controlled
- heading: 3.5. Evidence depth must be explicit
- heading: 3.6. Deep research beyond wiki must be scoped
- heading: 4. Routing goals
- heading: 4.1. Fast initial orientation
- heading: 4.2. Relevant-first retrieval
- heading: 4.3. Controlled expansion
- heading: 4.4. Efficient stop decision
- heading: 4.5. Honest evidence signaling
- heading: 5. Routing inputs
- heading: 5.1. `task_family`
- heading: 5.2. `task_lens`
- heading: 5.3. `target_object_ref`
- heading: 5.4. `target_object_type`
- heading: 5.5. `domain_hint`
- heading: 5.6. `current_goal_or_stage`
- heading: 6. Routing layers
- heading: 6.1. Task Lens
- heading: 6.2. Domain
- heading: 6.3. Scope precedence
- heading: 6.4. Object / concept resolution
- heading: 6.5. Expansion
- heading: 7. Scope precedence modes
- heading: 7.1. Project-first mode
- heading: 7.2. Common-first mode
- heading: 7.3. Local-first mode
- heading: 7.4. Design rule
- heading: 8. Object and concept resolution rules
- heading: 8.1. Resolution should happen early
- heading: 8.2. Resolution sources
- heading: 8.3. Canonical confirmation rule
- heading: 8.4. Example
- heading: 9. Expansion rules
- heading: 9.1. Expansion must be lens-aware
- heading: 9.2. Expansion should follow meaningful links first
- heading: 9.3. Expansion should stop when enough
- heading: 10. Stop conditions
- heading: 10.1. Sufficient-for-next-decision
- heading: 10.2. No-significant-information-gain
- heading: 10.3. HUMAN-gate-before-broader-search
- heading: 11. Evidence depth rules
- heading: 11.1. Evidence levels
- heading: 11.2. `wiki_only`
- heading: 11.3. `source_checked`
- heading: 11.4. Required warning at wiki-only level
- heading: 11.5. Deep-analysis-sensitive tasks
- heading: 12. Deep research rules beyond wiki
- heading: 12.1. Wiki-first remains the default
- heading: 12.2. No full raw grep by default
- heading: 12.3. Folder-scoped deep research
- heading: 12.4. AI should propose scoped candidates
- heading: 12.5. Example wording
- heading: 13. HUMAN checkpoints in routing
- heading: 13.1. Object resolution ambiguity
- heading: 13.2. Scope ambiguity
- heading: 13.3. Lens ambiguity
- heading: 13.4. Expansion ambiguity
- heading: 13.5. Deep research boundary
- heading: 14. Routing output contract
- heading: 14.1. `resolved_task_lens`
- heading: 14.2. `resolved_domain`
- heading: 14.3. `resolved_scope_precedence`
- heading: 14.4. `resolved_target_objects`
- heading: 14.5. `retrieval_focus_summary`
- heading: 14.6. `expansion_plan_summary`
- heading: 14.7. `routing_readiness`
- heading: 14.8. `evidence_level`
- heading: 14.9. `evidence_depth_summary`
- heading: 15. Quality rules
- heading: Rule 1
- heading: Rule 2
- heading: Rule 3
- heading: Rule 4
- heading: Rule 5
- heading: Rule 6
- heading: Rule 7
- heading: Rule 8
- heading: 16. Proposed merged content summary
- heading: 17. Delta status
- heading: Knowledge-runtime sprint addendum — runtime access flow
- heading: Default runtime access order
- heading: Raw/source fallback triggers
- heading: Stop rule
- heading: Tool support rule
- heading: Source Understanding Artifact routing addendum
- heading: Task Lens canonical addendum
- heading: Definition
- heading: Core rules
- heading: Minimal routing flow
- heading: Controlled Knowledge Promotion routing addendum
- heading: v0.9.8 Wiki Meta / Index routing addendum
- heading: v0.9.9 Working AIP Connection routing addendum
- heading: v0.9.11 Minimal Runtime Testing addendum
- heading: v0.9.13 Wiki Tooling Alignment addendum
- heading: CR-G5 Addendum — Wiki-First Evidence Policy (2026-05-25)
- heading: Explicit evidence level policy

## Related Sources
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-wiki-meta-index-spec-md-15a8** — role: upstream_input — Routing consumes the artifact-level meta (Lớp 1) whose structure is owned there — that meta plus the slim index.jsonl projection is the record routing matches, filters, scopes and stops on; coupling = the fields routing reads (lookup_keys, knowledge_targets, authority/freshness, meta_locator/artifact_locator); a change to those fields or to the index projection changes routing inputs and precedence outcomes. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-lookup-key-strategy-spec-mvp-md-1b67** — role: upstream_input — The T1/T2/T3 key tiers owned there are the match inputs a query is scored against during routing; coupling = the tier definitions and the lookup_keys field carried in artifact meta; a change to tiering or key-quality rules changes which sources route first and whether a query resolves at all. [asserted]
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-artifact-understanding-spec-md-139a** — role: related — Cited once, at the end, for the confirmed-vs-inferred provenance separation that routing output preserves when reporting evidence; vocabulary alignment only — routing reads no field this spec owns and no schema or data flows between them. [asserted]
