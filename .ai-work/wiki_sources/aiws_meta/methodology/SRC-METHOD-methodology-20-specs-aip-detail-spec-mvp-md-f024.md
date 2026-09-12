---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-aip-detail-spec-mvp-md-f024
title: methodology / 20_specs/AIP_Detail_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/AIP_Detail_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-25T01:39:18.883841+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — methodology / 20_specs/AIP_Detail_Spec_MVP.md

## Summary
Project-level control artifact.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- AIP Detail Spec for AI Work System MVP
- for AI Work System MVP AIP là gì
- for AI Work System MVP AIP không là gì
- for AI Work System MVP Nguyên tắc chính
- AIP_ROOT retired
- AIP
- execution
- Working
- aip
- runtime
- scope
- update
- task
- project
- present
- outputs
- should
- lint
- handoff
- does
- Workspace
- Task
- AIPs
- free
- slug
- PLAN
- EXEC
- artifact
- findings
- AIP_PLAN
- may
- Context
- depends_on
- Objective
- Constraints
- AIWS
- fields
- done
- wiki

## Source-Specific Hints
- heading: AIP Detail Spec for AI Work System MVP
- heading: 1. Mục đích
- heading: 2. Vai trò của AIP trong MVP
- heading: 2.1. AIP là gì
- heading: 2.2. AIP không là gì
- heading: 2.3. Nguyên tắc chính
- heading: 3. Các loại AIP trong MVP
- heading: 3.1. AIP_ROOT — RETIRED (CR-AIWS-2026-07-026)
- heading: 3.2. AIP_PLAN
- heading: 3.3. AIP_EXEC
- heading: 3.4. AIP_LOCAL
- heading: 3.5. Retrospective AIP authoring (ship-first emergencies)
- heading: 4. Naming convention
- heading: 4.1. File naming
- heading: 4.2. Slug guideline
- heading: 4.3. Slug prefix taxonomy (recommended)
- heading: 5. Metadata spec
- heading: 5.1. YAML frontmatter required
- heading: 5.2. AIP_ROOT metadata — RETIRED (CR-AIWS-2026-07-026)
- heading: 5.3. AIP_PLAN metadata
- heading: 5.4. AIP_EXEC metadata
- heading: 5.5. AIP_LOCAL metadata
- heading: 5.6. Enum rules
- heading: 5.7. Cross-AIP relationship fields (optional)
- heading: 6. Required sections
- heading: 6.1. AIP_ROOT required sections — RETIRED (CR-AIWS-2026-07-026)
- heading: 6.2. AIP_PLAN required sections
- heading: 6.3. AIP_EXEC required sections
- heading: 6.4. AIP_LOCAL required sections
- heading: 7. Step structure spec
- heading: 7.1. Required fields per step
- heading: 7.2. Optional fields per step
- heading: 7.3. Recommended step format
- heading: Step: STEP-02 — Identify mandatory review dependencies
- heading: 7.4. Step ID convention
- heading: 8. Granularity rules
- heading: 8.1. Default granularity
- heading: 8.2. Split triggers
- heading: 8.3. Avoid
- heading: 9. PLAN → EXEC handoff spec
- heading: 9.1. Handoff package minimum
- heading: 9.2. Consumption rule
- heading: 9.3. Drift rule
- heading: 10. Update rules
- heading: 10.1. AIP update allowed when
- heading: 10.2. AIP update not required for
- heading: 11. Relationship to other artifacts
- heading: 11.1. With Contract
- heading: 11.2. With Workspace
- heading: 11.3. With Active Step Context
- heading: 11.4. With Playbooks/Skills
- heading: 12. AIP lint targets
- heading: 12.1. Metadata lint
- heading: 12.2. Section lint
- heading: 12.3. Step lint
- heading: 12.4. Reference lint
- heading: 13. Minimal examples
- heading: 13.1. Good AIP_PLAN
- heading: 13.2. Bad AIP_PLAN
- heading: 14. Kết luận
- heading: Knowledge-runtime sprint addendum — Working AIP connection
- heading: Working AIP remains the execution guardrail
- heading: What may feed Working AIP
- heading: Execution rule
- heading: Personal Notebook and Working AIP addendum
- heading: Source Understanding Artifact and Working AIP addendum
- heading: Task Lens, AIP Template, and Working AIP canonical addendum
- heading: Controlled Knowledge Promotion AIP addendum
- heading: v0.9.8 Wiki Meta / Index AIP runtime addendum
- heading: v0.9.9 Working AIP Connection addendum
- heading: Task Intent
- heading: Scope
- heading: Expected Output
- heading: Context / Source References
- heading: Selected Task Lens / Mode
- heading: Execution Steps
- heading: Guardrails / Constraints
- heading: Open Questions / Blockers
- heading: Done Criteria

## Related Sources
- **SRC-METHOD-methodology-20-specs-working-aip-connection-spec-mvp-md-e993** — role: upstream_input — The Working AIP Connection addendum in this spec restates, in compressed form, a contract owned elsewhere: the mandatory-Working-AIP-before-non-trivial-execution rule, the minimum Working AIP section list, and the "support artifacts may feed but never replace" boundary. Coupling = that rule set + the minimum section list; if the readiness levels, minimum fields, or the anti-confusion table change in the connection spec, the addendum here goes stale. [asserted]
- **SRC-METHOD-methodology-20-specs-working-aip-connection-runtime-guidance-mvp-md-a41a** — role: downstream_navigation — Carries the runtime flow (intent → lens/context → wiki lookup → selected inputs → create/update Working AIP → readiness check → aiws-aip run) for the handoff that this spec only summarizes in its v0.9.9 addendum; it is where an executor goes to actually move from discovery into AIP-guarded execution. It applies, and does not redefine, the AIP artifact model — no coupling with the §5 metadata/section schema here. [asserted]
