---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-working-aip-connection-spec-mvp-md-e993
title: methodology / 20_specs/Working_AIP_Connection_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Working_AIP_Connection_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-20T10:16:16.934894+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — methodology / 20_specs/Working_AIP_Connection_Spec_MVP.md

## Summary
This spec defines the minimal connection rules from discovery/reuse/runtime context into Working AIP. The purpose is to let AI move safely from: finding the right knowledge/context to: executing the task without bypassing Working AIP.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Working AIP Connection Spec MVP
- Working AIP Connection Spec MVP Purpose
- Working AIP Connection Spec MVP Core definition
- Working AIP Connection Spec MVP Core stance
- Working AIP Connection Spec MVP Mandatory Working AIP rule
- AIP
- Working
- execution
- context
- source
- Task
- task
- Lens
- Workspace
- aip
- Source
- output
- clear
- scope
- Notebook
- needed
- Wiki
- run
- feed
- trivial
- may
- markdown
- references
- Template
- Knowledge
- connection
- replace
- update
- HUMAN
- intent
- Candidate
- relation
- should
- working
- lookup

## Source-Specific Hints
- heading: Working AIP Connection Spec MVP
- heading: 1. Purpose
- heading: 2. Core definition
- heading: 3. Core stance
- heading: 4. Mandatory Working AIP rule
- heading: 5. Lightweight Working AIP option
- heading: Working AIP Lite
- heading: Task
- heading: Output
- heading: Context / Sources
- heading: Steps
- heading: Guardrails
- heading: Done Criteria
- heading: 6. Minimum Working AIP fields
- heading: Working AIP
- heading: 1. Task Intent
- heading: 2. Scope
- heading: 3. Expected Output
- heading: 4. Context / Source References
- heading: 5. Selected Task Lens / Mode
- heading: 6. Execution Steps
- heading: 7. Guardrails / Constraints
- heading: 8. Open Questions / Blockers
- heading: 9. Done Criteria
- heading: 7. Readiness levels
- heading: 8. Readiness checklist
- heading: Working AIP Readiness Checklist
- heading: 9. Handoff sources and roles
- heading: 10. Handoff representation
- heading: Context / Source References
- heading: 11. Anti-confusion boundary
- heading: 12. Runtime connection flow
- heading: 13. Task Lens relation
- heading: Selected Task Lens / Mode
- heading: 14. Wiki Meta / Index relation
- heading: 15. Workspace relation
- heading: 16. Notebook relation
- heading: 17. Source artifact relation
- heading: 18. aiws-aip run relation
- heading: 19. aiws-aip run pre-execution checklist
- heading: aiws-aip run Pre-Execution Checklist
- heading: 20. Controlled Knowledge Promotion / lookback relation
- heading: Post-Execution / Lookback
- heading: 21. Anti-patterns
- heading: 22. Deferred items
- heading: 23. Conclusion
- heading: v0.9.10 Workspace Boundary addendum
- heading: v0.9.11 Minimal Runtime Testing addendum

## Related Sources
- **SRC-METHOD-methodology-20-specs-minimal-runtime-testing-stance-spec-mvp-md-e577** — role: upstream_input — The v0.9.11 addendum in this spec adopts the runtime-sanity rule ("before non-trivial execution, check Working AIP readiness") from the Minimal Runtime Testing stance, which decides what MVP runtime testing does and does not cover (deterministic guardrail + boundary checks; explicitly no scoring/telemetry/semantic review). Coupling = the scope of what is verified; widening or narrowing that stance changes what this spec's addendum is expected to assert. [asserted]
- **SRC-METHOD-methodology-20-specs-runtime-sanity-checklists-mvp-md-8158** — role: downstream_target — The sanity checklists (sprint close / canonical merge / package close) contain the concrete check items that assert Working AIP boundary and readiness — they consume the readiness levels (§7), the readiness checklist (§8) and the aiws-aip run pre-execution checklist (§19) defined here. Coupling = the readiness field set; adding or dropping a readiness item here leaves the corresponding checkbox there out of date. [asserted]
