---
name: aiws-review-plan
description: Produce a per-review-task REVIEW PLAN for a CROSS-DOCUMENT review — related-doc set + load-order + cross-doc interface-contract edge field-diffs + entity-column read/write map + region/order — then dispatch to aiws-runtime-review-checklist (M1); the caller executes (M3 leg-rubric + ensemble). Common + framework-independent. DOC-TYPE-GATED: for a dense single document, emit a minimal plan and recommend a hybrid free-read + checklist pass instead (the cross-doc plan does not lift recall there). NOT directly user-invocable — CALLED by the review-scaffold step of a review AIP (declared by `aiws-aip create`, executed by `aiws-aip run` — CR-AIWS-2026-08-094), or by a review agent. The skill PRODUCES the plan and STOPS; M1 breaks down items; the caller executes verdicts.
user-invocable: false
---

# aiws-review-plan

## Purpose
Turn a review task into an executable **review plan** the runtime checklist + execution run against: which related docs to load, in what order, which cross-document interfaces to reconcile (forced field-diffs), which entity-columns to cross-check vs the data model, and how to group/sequence items. This is the **M2** layer: **aiws-review-plan (M2) → aiws-runtime-review-checklist (M1) → review execution (M3: leg-rubric + ensemble)**. Output is a **workspace artifact** (`no_cr`), never canonical.

**Validated scope (AIP-EXEC-175):** the cross-doc plan (forced interface-contract field-diff + entity-column read/write map) is the **mechanical-recall lever for cross-document designs** (e.g. a basic design reconciled vs RD/OVERALL/sibling functions). It is **doc-type-gated** — see Rules.

## Inputs (caller maps its fields in)
- `review_task` (id + free-text), `target_document` (path or wiki source-id) + `target_document_type` (basic_design | detailed_design | api_design | db_design | test_design | other)
- `review_mode(s)`, `review_scope`; baselines (RD / OVERALL) + the target's §Related Documents (resolved, not guessed)

## Outputs
- **`review_plan.md`** in the task workspace `.ai-work/workspaces/<task>/` (an allowed extra file): `related_set` · `load_order` · `cross_doc_edges` (each + a "build interface-contract field-diff table" obligation) · `entity_column_map` · `regions/order`. Plus the `06_runtime_review_checklist.md` produced by M1.

## Flow
1. **Determine review shape** — target doc + type + mode + scope. **DOC-TYPE GATE (decide first):** if this is a **dense single document reviewed largely standalone** (no external reconciliation surface — e.g. a DD on its own), DO NOT build the cross-doc machinery; emit a minimal plan and **recommend the hybrid free-read + checklist pass** (per `aiws-runtime-review-checklist` data asset `## Doc-type applicability + method positioning`). For **cross-document** review (target reconciled vs RD/OVERALL/siblings), continue.
2. **Related-doc set** — resolve MECHANICALLY from the target's §Related Documents + its RD/baseline + OVERALL (a closed list; never guess members).
3. **Load order** — target → vertical baselines (RD, OVERALL) → related-function docs.
4. **Cross-doc edges** — enumerate every producer→consumer interface (shared field / status / nav / payload); attach a mandatory **build interface-contract field-diff table** obligation per edge. HARD guard: an edge may NOT PASS while any row is RENAMED / DROPPED / source-unknown.
5. **Entity-column read/write map** — enumerate every entity-column the target reads/writes/displays; cross-check each vs the OVERALL data-model (defined? written-by? orphan/undefined?) — orphan/undefined ⇒ defect. (= the `consistency (cross_document)` obligation in the M1 data asset.)
6. **Region/order** — group related checklist items into review regions + a sequence (review related items together).
7. **Dispatch to M1** — call `aiws-runtime-review-checklist` to break each selected item into Assert/Method/iff/Evidence; hand the plan + `06_` to the caller. STOP — the caller executes (M3: leg-rubric + ensemble + the Findings invariant).

## Rules
- **Framework-independent** — depend on NO AI-Agents-Pack path/surface. (The agent pack may REUSE this skill, not the reverse.)
- **Generic derivation only** — the related-set / edges / column-map / regions are derived by the SAME rules for every target; NEVER pin object-specific defects into the plan (that is object-tuning, not planning).
- **Doc-type gate** — the cross-doc plan is for **cross-document** review. For a **dense single doc** it does not lift recall (can reduce it vs free reading) → emit a minimal plan + recommend the hybrid free-read + checklist pass. (AIP-EXEC-175: cross-doc BD = plan dominates; dense DD = ad-hoc free reading ≥ plan.)
- **Layering** — M2 (this) produces the plan; **M1** (`aiws-runtime-review-checklist`) breaks down items; **M3** (the caller / review agent) executes via the leg-classified rubric + ensemble. `aiws-aip create` DECLARES the review-scaffold step that calls this skill; `aiws-aip run` executes it once the task workspace exists (CR-AIWS-2026-08-094).
- **Positioning (no over-claim)** — the plan delivers **reproducibility + traceability + cross-doc mechanical rigor**; recall depth depends on doc-type + model, and **deep-logic / business-rule recall is reasoning-bound (out-of-method)**.
- **Output is a workspace artifact** (`no_cr`); never auto-promoted to canonical. Capture routing per rule #7 (tier learning candidates to the AIP inbox; never auto-promote).
