# Canonical Design Set Update Changelog v0.2
Version: 0.2  
Status: Changelog for canonical merge through current point

> **2026-05-30 update (CR-AIWS-2026-05-020 / AIP-EXEC-038):** The **Knowledge Object** layer recorded in this
> changelog (`Knowledge_Object_Model_Spec`, `Knowledge_Expansion_Link_Spec`, the object-model/expansion entries
> below) was **removed** by CR-AIWS-2026-05-005 ("not earning its complexity"). The canonical model is now
> **2-layer** (artifact-level meta + index; cross-artifact relationships via `## Related Sources`). The two specs
> were rewritten to the 2-layer model (CR-020). Entries below remain as the historical v0.2 record.

---

# 1. Summary

This update completes the main Knowledge Hub delta merge into the canonical current baseline.

---

# 2. New canonical docs added

- `Knowledge_Object_Model_Spec_MVP_v0_1.md`
- `Knowledge_Routing_Spec_MVP_v0_1.md`
- `Knowledge_Expansion_Link_Spec_MVP_v0_1.md`
- `Knowledge_Access_Interface_Spec_MVP_v0_1.md`

---

# 3. Canonical docs updated

- `Architecture_Design_MVP_v0_5.md`
- `Basic_Design_MVP_v0_4.md`
- `AI_Work_System_MVP_Specs_Guidelines_Index_v0_4.md`

---

# 4. Main changes reflected in canonical

- Knowledge Hub is now canonically described as supporting:
  - object model
  - routing
  - expansion
  - access interface
- Knowledge Hub is no longer presented only as an active branch in the specs index
- Expansion link model was simplified in the canonical spec to:
  - `parent`
  - `input`
  - `related`
  - `reference`
- Expansion-link lifecycle was explicitly reflected:
  - Working AIP
  - local wiki
  - project wiki
  - source meta / source artifact / wiki meta
- Architecture and Basic Design are now wording-aligned with the merged Knowledge Hub baseline

---

# 5. Important note

This changelog does not claim that all future refinement work is finished.
It only records that the current major delta branch has now been absorbed into the canonical baseline through the present point.

---

# v0.9.3 — Knowledge-runtime sprint canonical merge

Date: 2026-04-25

## Summary
Merged the knowledge-runtime sprint outputs into the canonical baseline.

## Main updates
- Confirmed runtime terminology baseline.
- Added component boundary guardrails for Knowledge Hub / Task Lens / Wiki Meta-Index / AIP Template / Working AIP / Workspace / Skills.
- Added runtime knowledge access flow.
- Added Wiki Meta / Index minimal runtime spec.
- Added Working AIP connection guardrail.
- Added minimal metadata / registry support.
- Added minimal runtime testing stance.
- Preserved delta tracking for all BL docs and reference memos.

## Deferred
- Notebook full spec
- full metadata/registry framework
- full testing/scoring/telemetry
- lens preset catalog/orchestration
- source-derived reusable understanding artifact canonicalization

---

# v0.9.4 — Personal Notebook Minimal Spec merge

Date: 2026-04-25

## Summary
Merged the Personal Notebook Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Added Personal Notebook MVP spec.
- Added Personal Notebook local setup guide.
- Added Personal Notebook Write Skill Lite spec.
- Updated Workspace / Capture boundary.
- Updated Knowledge Access relation.
- Updated Working AIP boundary.
- Updated Basic / Architecture / Methodology addenda.
- Added delta tracking for PN sprint docs.

## Deferred
- Task Notebook / Workspace Notebook.
- Notebook UI/database.
- Notebook search/index framework.
- Auto-promotion pipeline.
- Full governance/access control.

---

# v0.9.5 — Source Understanding Artifact Minimal Spec merge

Date: 2026-04-25

## Summary
Merged the Source Understanding Artifact Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Added Source Understanding Artifact MVP spec.
- Added Source Understanding Artifact examples.
- Added canonical merge summary.
- Updated Knowledge Access Interface Spec.
- Updated Knowledge Routing Spec.
- Updated Workspace / Queue / Capture Spec.
- Updated AIP Detail Spec.
- Updated Basic / Architecture / Methodology docs.
- Added delta tracking for SU sprint docs.

## Deferred
- full metadata/registry framework
- full source ingestion pipeline
- automated artifact generation
- quality scoring/telemetry
- source diff/update automation
- multi-source synthesis artifact spec

---

# v0.9.6 — Task Lens Minimal Spec merge

Date: 2026-04-25

## Summary
Merged the Task Lens Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Added Task Lens MVP spec.
- Added Task Lens examples appendix.
- Added Task Lens sprint merge summary.
- Updated Knowledge Routing Spec.
- Updated Knowledge Access Interface Spec.
- Updated AIP Detail Spec.
- Updated Workspace / Queue / Capture Spec.
- Updated Basic / Architecture / Methodology docs.
- Added delta tracking for TL sprint docs.

## Key decisions
- Intent first, lens second.
- Explicit Task Lens is optional in MVP.
- No-Lens / AI-decides-search-scope is valid.
- HUMAN may adjust runtime lens.
- AI may expand/adjust lens.
- Task Lens is not a hard scope limiter.

---

# v0.9.7 — Controlled Knowledge Promotion Minimal Spec merge

Date: 2026-04-26

## Summary
Merged Controlled Knowledge Promotion Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Added Controlled Knowledge Promotion Spec MVP.
- Added templates/checklists appendix.
- Added skill/runtime guidance.
- Added sprint merge summary.
- Updated Knowledge Access, Routing, Workspace/Capture, Personal Notebook, Source Understanding Artifact, Task Lens, AIP Detail, Basic/Architecture/Methodology, Index, and Baseline Note.

## Key decisions
- Knowledge Hub is for AI runtime value.
- Notebook can store any.
- Candidate can be broad.
- Wiki requires Knowledge Value.
- Important add/update/promotion is controlled.
- Skill must use checklist before Wiki add/update.
- No auto-promotion or auto-apply-back.
- Important changes require log/rollback trace.

---

# v0.9.8 — Wiki Meta / Index Minimal Spec merge

Date: 2026-04-26

## Summary
Merged Wiki Meta / Index Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Updated `WIKI_META_INDEX_SPEC.md` with v0.9.8 runtime compatibility addendum.
- Added `WIKI_META_INDEX_RUNTIME_GUIDANCE.md`.
- Added `WIKI_META_INDEX_SAMPLE_RECORDS_APPENDIX.md`.
- Added merge summary.
- Updated Knowledge Access, Knowledge Routing, Source Understanding Artifact, Controlled Knowledge Promotion, Workspace/Capture, AIP Detail, and Wiki build/update guideline addenda.

## Key decisions
- Keep current Wiki Source Meta / Wiki Source Index mechanism.
- Preserve good existing field names.
- Use meta first, source artifact when needed.
- `artifact_locator` points to AIWS-readable source representation.
- Markdown representation must be sufficient for AI runtime understanding.
- Use existing sections before adding new fields.
- Lightweight maintenance vs Controlled Knowledge Promotion boundary.

---

# v0.9.9 — Working AIP Connection Minimal Spec merge

Date: 2026-04-26

## Summary
Merged Working AIP Connection Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Added `Working_AIP_Connection_Spec_MVP.md`.
- Added `Working_AIP_Connection_Runtime_Guidance_MVP.md`.
- Added `Working_AIP_Connection_Samples_Appendix_MVP.md`.
- Added merge summary.
- Updated AIP Detail, aiws-aip run skill, Knowledge Routing, Workspace, Notebook, Task Lens, Wiki Meta / Index, Source Understanding Artifact, Knowledge Access, and Controlled Knowledge Promotion.

## Key decisions
- Working AIP controls execution.
- Before non-trivial execution, AI must have or create a Working AIP.
- Support artifacts can feed Working AIP but cannot replace it.
- aiws-aip run executes against Working AIP.
- Candidate collection is not promotion or apply-back.

---

# v0.9.10 — Workspace Boundary Minimal Spec merge

Date: 2026-04-26

## Summary
Merged Workspace Boundary Minimal Spec Sprint outputs into canonical docs.

## Main updates
- Added `Workspace_Boundary_Spec_MVP.md`.
- Added `Workspace_Runtime_Guidance_MVP.md`.
- Added `Workspace_Boundary_Samples_Appendix_MVP.md`.
- Added `Workspace_Boundary_Minimal_Spec_Sprint_Merge_Summary.md`.
- Added Workspace templates for workspace file, Runtime Queue, and Capture Inbox.
- Updated Workspace / Queue / Capture spec with v0.9.10 boundary addendum.
- Updated Working AIP Connection, Controlled Knowledge Promotion, Personal Notebook, Knowledge Access, Wiki Meta / Index, Task Lens, Source Understanding, skills, and baseline docs.

## Key decisions
- Workspace is active task/session working context.
- Workspace can feed other layers but does not replace them.
- Runtime Queue captures current-task follow-up work.
- Capture Inbox captures future-value findings before triage.
- Task close must classify Workspace content.

---

# v0.9.11 — Minimal Runtime Testing Stance merge

Date: 2026-04-26

## Summary
Merged Minimal Runtime Testing Stance Sprint outputs into canonical docs.

## Main updates
- Added `Minimal_Runtime_Testing_Stance_Spec_MVP.md`.
- Added `Runtime_Sanity_Checklists_MVP.md`.
- Added `Minimal_Runtime_Test_Cases_Appendix_MVP.md`.
- Added `Runtime_Anti_Patterns_Appendix_MVP.md`.
- Added `Minimal_Runtime_Testing_Stance_Sprint_Merge_Summary.md`.
- Updated Working AIP Connection, Workspace Boundary, Workspace Runtime Guidance, Knowledge Routing, Wiki Meta / Index, Controlled Knowledge Promotion, Task Lens, Source Understanding, Knowledge Access, aiws-aip run, aiws-lint, and package/update skills where present.

## Key decisions
- Minimal runtime testing is deterministic guardrails + runtime boundary checks.
- lint/check is guardrail, not reviewer.
- aiws-aip run prepares runtime, not semantic execution.
- v0.9.2 is baseline/reference, not design direction.
- Future scoring/telemetry/testing harness are deferred.

---

# v0.9.12 — Runtime Tooling Alignment merge

Date: 2026-04-26

## Summary
Merged Runtime Tooling Alignment Sprint outputs into canonical docs and applied minimal P0/P1 implementation patches.

## Main updates
- Added `Runtime_Tooling_Alignment_Spec_MVP.md`.
- Added `Runtime_Tooling_Alignment_Patch_Guide_MVP.md`.
- Added `Runtime_Tooling_Alignment_Sprint_Merge_Summary.md`.
- Renamed Workspace template queue file to `02_runtime_queue.jsonl`.
- Updated `init_workspace.py`.
- Updated `lint_workspace.py`.
- Updated `lint_all.py`.
- Updated `run_aip.py status` for queue/capture visibility.

## Key decisions
- `02_investigation_queue.jsonl` → `02_runtime_queue.jsonl` on version-up.
- Old queue file remains readable as legacy alias.
- aiws-aip run prepares runtime/status, not semantic execution.
- lint/check is deterministic guardrail, not reviewer.

---

# v0.9.13 — Wiki Tooling Alignment merge

Date: 2026-04-26

## Summary
Merged Wiki Tooling Alignment Sprint outputs into canonical docs and applied minimal P0/P1 Wiki tool patches.

## Main updates
- Added `Wiki_Tooling_Alignment_Spec_MVP.md`.
- Added `Wiki_Tooling_Alignment_Patch_Guide_MVP.md`.
- Added `Wiki_Migration_Guide_for_HUMAN_and_AI_MVP.md`.
- Added `Wiki_Tooling_Alignment_Sprint_Merge_Summary.md`.
- Updated Wiki tools and Wiki skills with routing / no-auto-promotion / source representation guardrails.

## Key decisions
- aiws-wiki lookup is routing, not evidence verification.
- Refresh draft is not Knowledge Hub update.
- Detect/evaluate impact is signal, not approval.
- Source representation quality must be visible.
- lint_wiki is deterministic guardrail, not semantic reviewer.
- Migration aligns structure, not approval.

---

# v0.9.14 — Wiki Source Maintenance / Impact Detection merge

Date: 2026-04-26

## Summary
Merged Wiki Source Maintenance / Impact Detection Sprint outputs into canonical docs and applied minimal P0/P1 Wiki maintenance tool patches.

## Main updates
- Added `Wiki_Source_Maintenance_Impact_Detection_Spec_MVP.md`.
- Added `Wiki_Source_Maintenance_Tool_Patch_Guide_MVP.md`.
- Added `Wiki_Maintenance_Log_Template.jsonl`.
- Added `Wiki_Source_Maintenance_Sprint_Merge_Summary.md`.
- Updated related specs/skills with WSM guidance.

## Key decisions
- Source change detection is signal.
- Impact evaluation is recommendation.
- Refresh is draft by default.
- Apply is explicit and logged.
- Promotion is controlled separately.
- Runtime Queue for current-task blocking maintenance.
- Capture Inbox for future-value maintenance candidates.
- Applied maintenance updates must be traceable and reasonably reversible.

---

# v0.9.15 — Source Representation / Conversion Integration merge

Date: 2026-04-26

## Summary
Merged Source Representation / Conversion Integration Minimal Sprint outputs into canonical docs and applied minimal P0/P1 tool/skill patches.

## Main updates
- Added `Source_Representation_Conversion_Integration_Spec_MVP.md`.
- Added `Source_Representation_Tool_Skill_Patch_Guide_MVP.md`.
- Added HUMAN check / re-conversion / migration report templates.
- Added `Source_Representation_Sprint_Merge_Summary.md`.
- Updated related specs/skills with source representation boundary.

## Key decisions
- AIWS runtime reads AIWS-readable representation.
- AI does not automatically read raw non-text original.
- AI can only verify what is present in representation unless HUMAN verifies original.
- Limitations must be handled visibly.
- Tools expose representation boundary; they do not implement full conversion automation.

---

# v0.9.16 — Active Step Context Minimal Spec merge

Date: 2026-04-26

## Summary
Merged Active Step Context Minimal Spec Sprint outputs into canonical docs and applied minimal tool/skill patches.

## Main updates
- Added `Active_Step_Context_Spec_MVP.md`.
- Added `Step_Output_Decision_Traceability_Spec_MVP.md`.
- Added `Active_Step_Context_Tool_Skill_Patch_Guide_MVP.md`.
- Added ASC / Step Output / Decision Discussion Trace templates.
- Updated tools/skills with ASC and traceability support.

## Key decisions
- ASC is temporary step-local runtime view.
- Working AIP remains task authority.
- Workspace persists outputs/decisions/discussion traces.
- ASC source pointers are not source verification.
- Important HUMAN–AI decision process must be persisted when reused.
