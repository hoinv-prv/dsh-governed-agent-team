---
name: aiws-runtime-review-checklist
description: Materialize a per-run Runtime Review Checklist for one review task — select source-checklist items, exclude/N·A with rationale (gated), break each down into a concrete deterministic check via the breakdown-strategy method templates, bind evidence, and write 06_runtime_review_checklist.md into the task workspace. Common + framework-independent (no agent-pack dependency). NOT directly user-invocable — it is CALLED by the review-scaffold step of a review AIP (declared by `aiws-aip create`, executed by `aiws-aip run` — CR-AIWS-2026-08-094), or by a review agent, when a document review is being set up (design/test/API/DB/PM/security). The skill PRODUCES the checklist and STOPS; the caller executes it (fills verdicts).
user-invocable: false
---

# aiws-runtime-review-checklist

## Purpose
Turn generic common/project checklist knowledge into an **executable, per-run** checklist for one concrete review: which items apply (with rationale), how each is checked (a deterministic method + objective pass criteria), what evidence binds it, and a status per item. Output is a **runtime/workspace artifact** (`no_cr`), never auto-promoted to canonical knowledge. The skill **PRODUCES; the caller EXECUTES** (an AIP review Step, or any reviewer/agent fills the verdicts in place).

## Inputs (the skill's own contract — caller maps its fields in)
- `review_task` (id + free-text), `target_document` (path or wiki source-id) + `target_document_type` (basic_design | detailed_design | api_design | db_design | test_design | other)
- `review_mode(s)`, `review_scope` (+ optional `excluded_scope`, `review_depth`)
- "special cases" (db_access / api / external_system / state / permission …) are **DERIVED internally** as a selection signal — not a required input.

## Outputs
- **`06_runtime_review_checklist.md`** in the task workspace `.ai-work/workspaces/<task>/` (an allowed extra file; NOT added to `lint_workspace.py` REQUIRED_FILES). Re-invoke on an existing run no-ops unless `--force`.
- Everything else reuses the EXISTING workspace/review basenames (`04_findings.md`, `05_open_questions.md`, `07_output_draft.md`/`11_output_final.md`, `08_capture_inbox.jsonl`). No new report file — reference the existing review-report convention.

## Tool / Data
- Method templates (per `item_type`): the **co-located `runtime_review_breakdown_strategies.md`** (in this skill's folder — the breakdown-strategy method library; dispatch each item to its template; do not invent a per-item method).
- Source resolution: `py .ai-work/tooling/lookup_wiki_source.py` (Wiki Source Index) + the canonical review preset-knowledge (`preset_knowledge/{aip_samples,aip_exec}/review/`, `review_support/`).

## Per-item schema (REQUIRED — each item is a self-contained deterministic check)
**Assert** (objective claim) · **Method** (numbered steps, each citing an EXACT target-doc locus) · **PASS / FAIL / N·A-iff** (objective, measurable — banned: "enough / appropriate / obvious / needs-a-guess") · **Evidence** · **Verdict** (caller fills: `PASS`/`FAIL`/`RISK`/`QUESTION`/`N/A`/`NOT_CHECKED` + a one-line finding for non-PASS) · plus an `inferred? / assumption-basis` note where applicability/exclusion is inferred. Bar: two independent reviewers reach the SAME verdict from `Assert+Method+iff` alone.

## Flow
1. **Understand the task** — target doc + type, review mode(s), scope; derive special cases.
2. **Resolve sources** — pick the source checklist + guidelines + baselines via the Wiki Source Index / review preset-knowledge. Select the right SECTION for the document type before item-level selection (e.g. a DD checklist's DD section; do not pull BD/IT sections for a DD).
3. **Select items** — the chosen section's items are the closed universe.
4. **Exclude / N·A — GATED** (anti-weakening guard): high-severity/security/DB/state/permission/governance items may NOT be auto-excluded; `N/A` only on an explicit `n_a_condition` match (cite it) or HUMAN confirm; otherwise carry forward as visible `NOT_CHECKED`. Whole-section scope cuts (wrong artifact type) are allowed with reason.
5. **Break down** — dispatch each selected item to its `item_type` METHOD TEMPLATE in the data asset; instantiate `Assert/Method/iff/Evidence` with this doc's loci. Follow the template's determinism rules (closed universe, locus-validity ⇒ GAP/QUESTION, template-conformance, objective sufficiency).
6. **Bind evidence** — name the exact section/source each check reads.
7. **Write** `06_runtime_review_checklist.md` (sections: Target · Sources used · Selected items · Excluded/N·A · Breakdown · Execution result · Open questions · Reference gaps · Learning-candidate hints), verdicts initialized `NOT_CHECKED`. STOP — the caller executes. **Finding-trace:** every non-PASS verdict links a finding carrying `Related Runtime Item: <id>` + `Source Checklist Item: <id>` (so two runs are diff-able).

## Rules
- **Framework-independent** — depend on NO AI-Agents-Pack path or surface: no per-agent instance workspace tree, no per-run agent context surface, no agent-definition files, no agent-local learning queue. The agent pack REUSES this skill, not the reverse.
- **Verdict assignment is by the LEG-CLASSIFIED rubric, not by feel** — set each item's token (`PASS/FAIL/RISK/QUESTION/N/A`) via the data asset `## Verdict rubric — LEG-CLASSIFIED` (HARD leg absent ⇒ FAIL; SOFT leg absent/advisory ⇒ RISK; QUESTION/N·A as stated). This is the cross-run reproducibility lever (proven: 41.7%→91.7% single-run agreement, RISK↔FAIL drift→0).
- **Completeness honesty + headline** — the headline is machine-derived from the per-item verdicts by precedence `FAIL → RISK/CONDITIONAL → INCOMPLETE (QUESTION/NOT_CHECKED) → PASS`; no global `PASS` while any selected non-`N/A` item is `FAIL`/`RISK`/`QUESTION`/`NOT_CHECKED` (a recorded production RISK never hides under PASS). Counts are DERIVED from the per-item verdicts (each item one bucket; sum to the selected total); flag INCOMPLETE if any selected item is `NOT_CHECKED`. (See the data asset `## Completeness honesty + headline derivation`.)
- **Findings invariant** — every non-PASS verdict (`FAIL/RISK/QUESTION/NOT_CHECKED`) emits EXACTLY ONE Findings row (`Related Runtime Item` + `Source Checklist Item` + reason); `#findings == #non-PASS` — no flagged item stays only in per-item reasoning.
- **Cross-document items** — verify against the named baseline if available; if a needed baseline is absent, mark `QUESTION` + emit an Open Question (never silent PASS). For **cross-document review**, also build the **entity-column read/write map** — enumerate every column the target reads/writes/displays and cross-check vs the OVERALL data-model (orphan/undefined column ⇒ defect), in addition to producer→consumer edge diffs (data asset `### consistency (cross_document)`).
- **Capture routing (rule #7)** — under an AIP, learning + `wiki_candidate` captures tier UP to the AIP workspace `08_capture_inbox.jsonl` (keep a local pointer); standalone runs keep them in the task workspace inbox. Learning candidates use existing capture-inbox kinds + a `suggested_target`; never auto-promote to checklist/memory/Wiki.
- **Ensemble (high-stakes) — the reproducibility multiplier** — run the checklist **k≥3 (default 5) independent times**; resolve each item by **majority vote** of the verdict token; **union** the findings for recall; flag any item with no clean majority as **`contested → escalate to HUMAN`**. (Leg-classified rubric → ~100% clean majority under 3-of-5; ensemble complements the rubric, not a substitute.)
- **Output hygiene** — every item id is one of the source section's ids; reject fabricated ids.
- **Machine-checkable `iff`** — each item's `PASS/FAIL/N·A-iff` is a mechanical predicate (closed-enum / presence / equality on a cited locus), verbatim-verifiable from the `iff` alone; banned perception verbs are a **lint** target (checklist-lint follow-on), not a model self-audit. (Data asset Determinism rule 6.)
- **Doc-type applicability** — on a **dense single doc** (e.g. a detailed design) the per-item breakdown is a reproducibility lever, NOT a recall lever (it can REDUCE recall vs free reading) → prefer a **hybrid free-read + checklist pass** (or a project-specialised dense-doc checklist). The full cross-doc method (this skill + a review plan) is the validated **mechanical-recall lever for cross-document designs**. (Data asset `## Doc-type applicability + method positioning`.)
- **Positioning (no over-claim)** — this skill delivers **reproducibility + traceability + mechanical/structural coverage**, NOT a recall/correctness guarantee; **deep-logic / business-rule recall is reasoning-bound** (model/project depth), out-of-method.
- **Status semantics + LEG-CLASSIFIED verdict rubric + anti-weakening guard + the method templates (incl. `state_workflow`, `testability`)**: see the data asset.
