# AI Work System MVP — Specs and Guidelines Index
Version: 0.4  
Status: Canonical merged index through current point  
Phase: Specs / Guidelines  
Scope: MVP current canonical baseline

---

# 1. Purpose

Tài liệu này là index của bộ **canonical Specs / Guidelines** hiện tại cho AI Work System MVP.

Mục tiêu là:
- chỉ ra bộ spec/guideline nào đang là baseline canonical tới thời điểm hiện tại
- giúp mapping từ design-level concepts sang operational contracts/guidelines
- giữ bộ canonical set rõ ràng sau khi merge các delta chính của nhánh Knowledge Hub
- phản ánh trạng thái hiện tại theo hướng:
  - Architecture
  - Basic Design
  - Specs
đã được align hơn và không còn coi Knowledge Hub chỉ là active branch riêng

---

# 2. Included canonical core specs

1. `Use_Case_Artifact_Spec_MVP_v0_1.md`
2. `AIP_Template_Spec_MVP_v0_1.md`
3. `Working_AIP_Spec_MVP_v0_1.md`
4. `Discovery_and_Selection_Output_Spec_MVP_v0_1.md`
5. `Controlled_Capture_Spec_MVP_v0_1.md`

---

# 3. Included canonical core guidelines

1. `Guided_Questioning_Guideline_MVP_v0_1.md`
2. `Reduction_Bypass_Guideline_MVP_v0_1.md`
3. `Human_Checkpoint_Guideline_MVP_v0_1.md`

---

# 4. Included canonical Knowledge Hub specs

1. `Knowledge_Object_Model_Spec_MVP_v0_1.md`
2. `Knowledge_Routing_Spec_MVP_v0_1.md`
3. `Knowledge_Expansion_Link_Spec_MVP_v0_1.md`
4. `Knowledge_Access_Interface_Spec_MVP_v0_1.md`

### Note
The Knowledge Hub specs above are now treated as part of the canonical current baseline through this merge point.
They should no longer be interpreted merely as an active delta branch for the current sprint.

> **Update (CR-AIWS-2026-05-020, 2026-05-30):** The **Knowledge Object** layer was removed (CR-AIWS-2026-05-005);
> the canonical model is now **2-layer** (artifact meta + index; relationships via `## Related Sources`).
> `Knowledge_Object_Model_Spec` and `Knowledge_Expansion_Link_Spec` were rewritten to the 2-layer model (filenames unchanged).

---

# 5. Current cross-cutting additions included in the canonical baseline

The current canonical baseline additionally reflects:

- actor model:
  - AI as primary execution actor
  - HUMAN as supervisory / decision actor
- artifact-centric AIP model
- Working AIP as minimum pre-execution guardrail
- minimal **Task Lens** concept:
  - preset lenses exist
  - BrSE can choose a lens
  - AI may define a lens at runtime but must confirm with BrSE
  - reusable runtime-defined lenses may later be proposed into Knowledge Hub
- Knowledge Hub canonical direction:
  - canonical object/concept model
  - wiki-first routing
  - common expansion-link model
  - capability-based access interface
  - explicit evidence depth signaling before deeper raw/source research

---

# 6. Relationship to design docs

These specs/guidelines should be read together with:

- `Architecture_Design_MVP_v0_5.md`
- `Basic_Design_MVP_v0_4.md`

---

# 7. Status

This index and the listed docs are considered:
- the canonical merged baseline through the current point
- suitable for current testing / demo / refinement work
- still open to future revision after further validation, but no longer waiting for the main Knowledge Hub delta merge

---

# Knowledge-runtime sprint additions in version 0.9.3

This version adds canonical coverage for the knowledge-runtime sprint:

- Runtime Knowledge Direction & Terminology Baseline
- Runtime Component Boundary
- Runtime Knowledge Access Flow
- Wiki Meta / Index Minimal Runtime Spec
- Task Lens Minimal Spec
- Working AIP Connection
- Minimal Runtime Metadata / Registry Support
- Minimal Runtime Testing Stance
- Canonical Merge Map

The following are preserved as delta/reference tracking, not as separate canonical components:

- Source-derived reusable understanding artifact pattern
- Notebook status memo
- MVP incomplete concepts/features memo
- BL-01 through BL-10 sprint drafts

The sprint confirms:
- Knowledge Hub is the reusable knowledge center and standard knowledge access layer.
- Wiki Meta / Index is the runtime-facing structured layer.
- Task Lens routes task → knowledge.
- Working AIP is mandatory before meaningful execution.
- Workspace holds active task state and does not replace Knowledge Hub or Working AIP.

---

# Personal Notebook additions in version 0.9.4

This version adds canonical MVP coverage for:

- `Personal_Notebook_Spec_MVP.md`
- `Personal_Notebook_Local_Setup_Guide_MVP.md`
- `Personal_Notebook_Write_Skill_Lite_Spec_MVP.md`
- `Personal_Notebook_Sprint_Merge_Summary.md`

The sprint confirms:

- Personal Notebook is file/folder-based in MVP.
- Personal Notebook effective scope follows configured path.
- Personal Notebook is not Workspace findings.
- Personal Notebook is not Working AIP.
- Personal Notebook is not Knowledge Hub.
- Personal Notebook is not source of truth by default.
- Personal Notebook does not auto-promote.
- Personal Notebook may produce capture candidates.
- Personal Notebook Write Skill Lite is allowed as a lightweight support skill.

---

# Source Understanding Artifact additions in version 0.9.5

This version adds canonical MVP coverage for:

- `Source_Understanding_Artifact_Spec_MVP.md`
- `Source_Understanding_Artifact_Examples_MVP.md`
- `Source_Understanding_Artifact_Sprint_Merge_Summary.md`

The sprint confirms:

- Practical term: Source Understanding Artifact.
- Full descriptive term: Source-derived Reusable Understanding Artifact.
- One artifact should correspond to one clear source unit.
- Minimum provenance: source pointer, source scope, understanding date.
- Status/authority/freshness hints are required.
- Raw/source remains source of truth.
- Wiki Meta / Index may route to Source Understanding Artifacts.
- Controlled capture is required before curated Knowledge Hub status.

---

# Task Lens additions in version 0.9.6

This version adds canonical MVP coverage for:

- `Task_Lens_Spec_MVP.md`
- `Task_Lens_Examples_MVP.md`
- `Task_Lens_Sprint_Merge_Summary.md`

The sprint confirms:

- Task Lens is optional runtime routing support.
- Intent first, lens second.
- No-Lens / AI-decides-search-scope is allowed.
- HUMAN may adjust runtime lens.
- AI may expand/adjust lens when too narrow.
- Task Lens must not become a hard scope limiter.
- Task Lens does not replace AIP Template, Working AIP, Wiki Meta / Index, Knowledge Hub, or raw/source verification.

---

# Controlled Knowledge Promotion additions in version 0.9.7

Added canonical specs:
- `Controlled_Knowledge_Promotion_Spec_MVP.md`
- `Controlled_Knowledge_Promotion_Templates_Checklists_MVP.md`
- `Controlled_Knowledge_Promotion_Skill_Runtime_Guidance_MVP.md`
- `Controlled_Knowledge_Promotion_Sprint_Merge_Summary.md`

Key decisions:
- Knowledge Hub is AI-first runtime knowledge layer.
- Knowledge Value means helping AI work more efficiently and/or produce higher-quality outputs.
- Notebook can store any.
- Candidate can be broad and intermediate.
- Wiki / Knowledge Hub requires Knowledge Value.
- Knowledge Hub add/update requires checklist gate.
- No Auto-Promotion.
- Post-feedback lookback captures improvement candidates.
- Important promotion/improvement requires log/rollback trace.

---

# v0.9.8 Wiki Meta / Index Minimal Spec additions

Updated/added canonical docs:
- `payload/wiki_guidelines/core/specs/WIKI_META_INDEX_SPEC.md`
- `payload/wiki_guidelines/core/guidelines/WIKI_META_INDEX_RUNTIME_GUIDANCE.md`
- `payload/wiki_guidelines/appendix/examples/WIKI_META_INDEX_SAMPLE_RECORDS_APPENDIX.md`
- `payload/methodology/20_specs/Wiki_Meta_Index_Minimal_Spec_Sprint_Merge_Summary.md`

Key decisions:
- Preserve current Wiki Source Meta / Wiki Source Index mechanism.
- Preserve good existing field names.
- Use lookup → meta_locator → artifact_locator when needed.
- `artifact_locator` points to AIWS-readable source representation.
- Markdown/source representation must be sufficient for AI runtime understanding.
- Use existing sections before adding new fields.
- Small meta fixes are lightweight maintenance.
- Authority/meaning/broad changes use Controlled Knowledge Promotion.

---

# v0.9.9 Working AIP Connection additions

Added/updated canonical docs:
- `Working_AIP_Connection_Spec_MVP.md`
- `Working_AIP_Connection_Runtime_Guidance_MVP.md`
- `Working_AIP_Connection_Samples_Appendix_MVP.md`
- `Working_AIP_Connection_Minimal_Spec_Sprint_Merge_Summary.md`

Key decisions:
- Discovery/reuse/context can inform execution.
- Working AIP controls execution.
- Before non-trivial execution, AI must have or create a Working AIP.
- Support artifacts can feed Working AIP but cannot replace it.
- aiws-aip run executes against Working AIP.
- Candidate collection is not promotion or apply-back.

---

# v0.9.10 Workspace Boundary additions

Added/updated canonical docs:
- `Workspace_Boundary_Spec_MVP.md`
- `Workspace_Runtime_Guidance_MVP.md`
- `Workspace_Boundary_Samples_Appendix_MVP.md`
- `Workspace_Boundary_Minimal_Spec_Sprint_Merge_Summary.md`
- `Workspace_Template_MVP.md`
- `Workspace_Runtime_Queue_Template.jsonl`
- `Workspace_Capture_Inbox_Template.jsonl`

Key decisions:
- Workspace is active task/session working context.
- Workspace supports continuity and current-state management.
- Workspace can feed Working AIP, Knowledge Promotion, Notebook, and canonical outputs.
- Workspace does not replace Working AIP, Knowledge Hub, Notebook, source artifacts, or canonical docs.
- Workspace Runtime Queue stores current-task follow-up work so AI can stay focused and process emergent subtasks sequentially.
- Capture Inbox stores possible future-value findings before triage.
- At task close, Workspace content should be classified.

---

# v0.9.11 Minimal Runtime Testing Stance additions

Added/updated canonical docs:
- `Minimal_Runtime_Testing_Stance_Spec_MVP.md`
- `Runtime_Sanity_Checklists_MVP.md`
- `Minimal_Runtime_Test_Cases_Appendix_MVP.md`
- `Runtime_Anti_Patterns_Appendix_MVP.md`
- `Minimal_Runtime_Testing_Stance_Sprint_Merge_Summary.md`

Key decisions:
- Minimal runtime testing checks whether AIWS follows runtime guardrails and component boundaries.
- Deterministic checks and manual checkpoints are guardrails, not semantic review.
- Correctness before optimization.
- lint/check is guardrail, not reviewer.
- aiws-aip run prepares runtime, not semantic execution.
- v0.9.2 is baseline/reference, not design direction.
- Future scoring/telemetry/testing harness are deferred.


# 2026-06-19 — AIWS Change Request Spec (CR-AIWS-2026-06-030)

- `20_specs/AIWS_Change_Request_Spec_MVP.md` — general AIWS-wide CR authority: how Change Requests are written, governed, approved, and applied for ALL canonical AIWS docs (Truth, methodology/specs, guidelines, wiki_guidelines, AIP templates, procedural, doc-bearing skills). `WIKI_CHANGE_REQUEST_SPEC` retained as its wiki-meta profile. Codifies month-scoped + cross-branch CR-id discipline and 3 CR-authoring conventions. Added via AIP-EXEC-086.


# 2026-06-24 — Runtime Review Methodology (CR-AIWS-2026-06-060)

- `20_specs/Runtime_Review_Methodology_MVP.md` — framework-independent methodology for **review reproducibility** (same review inputs → same verdicts run-to-run). Defines the 3 reproducibility layers, the leg-classified HARD⇒FAIL / SOFT⇒RISK verdict rubric, the ensemble protocol (k≥3, default 5, 3-of-5 majority, contested→HUMAN), RISK-in-headline derivation, and the finding-trace convention. `aiws-runtime-review-checklist` (CR-053/056) is its operational instance; empirically validated via the CR-056 2×2 re-test. Added via AIP-EXEC-174.

# 2026-06-24 — Review-method PoC supplements: aiws-runtime-review-checklist data asset + new aiws-review-plan skill (CR-AIWS-2026-06-062, CR-AIWS-2026-06-063)

- `procedural/skills/aiws-runtime-review-checklist/runtime_review_breakdown_strategies.md` + `SKILL.md` — **CR-062** additive supplements (grounded in the AIP-EXEC-175 generic-method-validation PoC; dev/test split + best-model benchmark): **S-A** Findings invariant (every non-PASS ⇒ exactly one Findings row); **S-B** entity-column read/write-map obligation in `consistency (cross_document)` (the cross-doc mechanical-recall lever — orphan/undefined column ⇒ FAIL); **S-C** machine-checkable `iff` (Determinism rule 6; banned perception verbs enforced by a checklist-lint follow-on, not self-audit); **S-D + S-E** `## Doc-type applicability + method positioning` (dense single-doc = reproducibility lever NOT recall lever → hybrid free-read + checklist; deep-logic recall = out-of-method). Anchored on CR-053/056; additive. Applied via AIP-EXEC-178.
- `procedural/skills/aiws-review-plan/SKILL.md` — **CR-063** NEW common skill (**M2**): per-review-task plan = related-set + load-order + cross-doc interface-contract edge field-diffs + entity-column read/write map + region/order; dispatches to `aiws-runtime-review-checklist` (M1); executed by the caller (M3 leg-rubric + ensemble). **Doc-type-gated** (cross-doc designs = validated mechanical-recall lever; dense single-doc → hybrid free-read pass). `user-invocable: false` (called by aiws-aip create / a review agent — matches sibling M1). Framework-independent. Applied via AIP-EXEC-178.
