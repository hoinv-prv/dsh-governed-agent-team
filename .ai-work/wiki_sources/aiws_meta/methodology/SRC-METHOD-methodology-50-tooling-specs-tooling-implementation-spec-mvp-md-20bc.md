---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-50-tooling-specs-tooling-implementation-spec-mvp-md-20bc
title: methodology / 50_tooling/specs/Tooling_Implementation_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/50_tooling/specs/Tooling_Implementation_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-20T10:16:17.072095+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — methodology / 50_tooling/specs/Tooling_Implementation_Spec_MVP.md

## Summary
This spec details the **tooling layer** of AI Work System MVP. This version updates tooling expectations to align with **Wiki v1.0 freeze**, especially the source-side model: `Wiki Source Artifact` `Wiki Source Meta` `Wiki Source Index` `Source Interpretation Profile` Tooling exists to support deterministic-first operations around: AIP + Workspace Wiki source discovery source meta refresh wiki ...

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Tooling Implementation Spec for AI Work System MVP
- for AI Work System MVP Deterministic first
- for AI Work System MVP No silent truth rewrite
- for AI Work System MVP Support the workflow, do not redefine it
- for AI Work System MVP Index/meta first support
- source
- meta
- Wiki
- Source
- wiki
- tooling
- Purpose
- artifact
- profile
- refresh
- lookup
- Tooling
- side
- Profile
- support
- lint
- official
- Responsibilities
- implementation
- MVP
- projection
- workspace
- output
- metas
- entries
- semantic
- PMP
- spec
- mvp
- AIP
- update
- build_wiki_source_meta
- friendly
- tools
- should

## Source-Specific Hints
- heading: Tooling Implementation Spec for AI Work System MVP
- heading: 1. Purpose
- heading: 2. Tooling principles
- heading: 2.1. Deterministic first
- heading: 2.2. No silent truth rewrite
- heading: 2.3. Support the workflow, do not redefine it
- heading: 2.4. Index/meta-first support
- heading: 3. Minimal tooling sets in MVP
- heading: 3.1. Runtime / AIP tooling
- heading: 3.2. Wiki / source-side tooling
- heading: 3.3. Optional future-friendly tools
- heading: 4. Existing runtime tools
- heading: 4.1. build_active_step_context.py
- heading: 4.2. set_current_step.py
- heading: 4.3. init_workspace.py
- heading: 4.4. lint_aip.py
- heading: 4.5. lint_workspace.py
- heading: 5. New wiki/source-side tool expectations
- heading: 5.1. build_wiki_source_meta.py
- heading: Purpose
- heading: Input
- heading: Output
- heading: Responsibilities
- heading: Must not do
- heading: 5.2. build_wiki_source_index.py
- heading: Purpose
- heading: Input
- heading: Output
- heading: Responsibilities
- heading: Must not do
- heading: 5.3. lookup_wiki_source.py
- heading: Purpose
- heading: Lookup modes
- heading: Input
- heading: Output
- heading: Responsibilities
- heading: 5.4. refresh_wiki_source_meta.py
- heading: Purpose
- heading: Input
- heading: Output
- heading: Responsibilities
- heading: Must not do
- heading: 5.5. lint_wiki.py
- heading: Purpose
- heading: Now includes checks for:
- heading: 6. Optional change-detection tools
- heading: detect_changed_wiki_sources.py
- heading: evaluate_wiki_source_impact.py
- heading: 7. Updated lint scope expectations
- heading: 8. Tool input/output philosophy
- heading: 8.1. Read-only by default
- heading: 8.2. Controlled writes
- heading: 8.3. Projection rule
- heading: 9. CLI behavior recommendations
- heading: 10. Priority order for implementation
- heading: Priority 1
- heading: Priority 2
- heading: Priority 3
- heading: Priority 4
- heading: 11. Acceptance criteria
- heading: Runtime side
- heading: Wiki side
- heading: 12. Non-goals
- heading: 13. Conclusion
- heading: 7. Wiki Tooling Improvements — 2026-05-27 Addendum
- heading: 7.1 build_wiki_source_meta.py — Extended Responsibilities (supplements §5.1)
- heading: 7.2 build_wiki_source_index.py — Extended Responsibilities (supplements §5.2)
- heading: 7.3 lookup_wiki_source.py — Extended Responsibilities (supplements §5.3)
- heading: 7.4 Profile vs PMP Architecture (supplements §2.4)

