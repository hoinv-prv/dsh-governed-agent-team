# Document Review Process (shared)

> Shared across all Document Review Agent blueprints in the pack.
> Mapped from: Document_Review_Agent_Blueprint/templates/REVIEW_PROCESS_TEMPLATE.md (v0.1).
> Document-type-agnostic. A document-type blueprint adds its own checklist and skills on top of
> this process; it does not replace the steps below.

---

> **Governance-invariant floor (AP-CR-31).** Lines tagged `⚖ governance_invariant` `<id>` mark non-overridable governance steps. An Agent Task Desk owns a copy of this process (FR-AI-13, §6D) and may add / reorder / annotate / mark-satisfied-elsewhere, but must NOT silently drop or weaken a `governance_invariant` step; the staging lint `tooling/lint_agents.py` warns if a copied instance process is missing one.

## 1. Purpose

Define the standard, repeatable process a Review Agent Task Desk follows to review a document.

---

## 2. Process

### Step 1 — Understand the review request

Confirm:
- target document and its path
- document type
- review scope (and any excluded scope)
- review depth: quick / standard / deep
- expected output
- deadline / priority if any

If any of these is unclear, ask the HUMAN before reviewing. Do not assume scope.

### Step 2 — Select review mode / checklist

Select and combine:
- the common document review checklist (`../checklists/common_document_review_checklist.md`)
- the document-specific checklist (blueprint-local: `docs/reference_content/<doc_type>_review_checklist.md`)
- any optional focus lens requested by the HUMAN

### Step 3 — Load references (Wiki-first, NOT Wiki-only)

Read in this order:
1. relevant Wiki entries first — for project context, terminology, design decisions, cautions,
   and source-navigation hints.
2. related source / reference documents (verify Wiki against source where it matters).
3. related AIP / task plan if any.
4. agent memory: retrieval hints, false-positive notes, confirmed memory.

Wiki is the starting point for grounding, not the only authority. When Wiki is stale, unverified,
or contradicts the source, verify against the source and follow `source_trace_rule.md`.

**Lookup discipline (CR-AIWS-2026-07-015):** resolve wiki entries via the standard tool —
`py .ai-work/tooling/lookup_wiki_source.py --query <kw> --system <id> --limit 5` (multi-system:
`--system` is mandatory). Escalation chain: lexical → `--mode tokens` → `--mode catalog`
(read-and-choose over the registered catalog) → raw (STILL authorization-gated per CR-052 —
halt-and-ask; agents hold no standing raw grant). 2-stage retrieve→AI-rerank per the
`aiws-wiki lookup`. Trip-wire ⇒ mandatory `retrieval_improvement` capture (MP1–MP7) — see
ARC §4A.

### Step 4 — Create review plan (M2), then materialize the runtime checklist (M1) — CR-AIWS-2026-07-012

**4a (M2 — review plan).** Produce a short review plan (`review_plan.md`) capturing:
- review scope (regions / targets — when the subject is a list, each element = one target)
- references to use, classified by SoT layer (`source_trace_rule.md` §6)
- checklist / lens selected
- expected output
- known limitations going in

*(M2 is delegated to the AIWS skill `aiws-review-plan` — reference by name, per its spec.)*

*(Two-phase runs — CR-AIWS-2026-07-016: when the run is `plan_first`, `run_plan.md` IS this
review plan — extend review_plan content with the run_plan sections (Task verbatim / confirm
points / autonomy note). ONE plan artifact per run; never maintain both.)*

**4b (M1 — runtime checklist).** Materialize the runtime review checklist by DELEGATING to the
AIWS skill **`aiws-runtime-review-checklist`** (do not hand-build the item structure). Every
item carries: Assert / Method (cite the exact locus) / iff machine-checkable condition / Evidence
binding / Verdict init `NOT_CHECKED` / leg classification **HARD·SOFT**. The source-checklist
universe = the checklists selected in Step 2.

### Step 5 — Review the document (M3 — execute by leg-rubric) — CR-AIWS-2026-07-012

Run each runtime checklist item and set its **verdict token by the leg-rubric** (see
`severity_definition.md` §Verdict tokens — mechanical, no gut call): HARD leg absent ⇒ `FAIL`;
SOFT leg absent ⇒ `RISK`; needs HUMAN ⇒ `QUESTION`; explicit n_a_condition ⇒ `N/A`; else `PASS`.

**Ensemble (high-stakes items).** Run k≥3 (default 5) independent passes and majority-vote the
token, union the findings, `contested → escalate to HUMAN` — for items matching the CHECKABLE
criteria: HARD legs under direction-alignment / correctness-of-decisions viewpoints, items whose
locus the artifact itself marks TBD/未確定/要確認, and items with a prior 🔴-severity finding.

Record findings as they arise. Distinguish clearly:
- confirmed_issue
- possible_issue
- open_question
- conflict
- suggestion

Follow `finding_format.md` for structure (incl. `[fact]/[inference]` tag + Trace columns +
findings invariant) and `severity_definition.md` for severity. Every important finding needs
evidence per `source_trace_rule.md`, or must be marked as an assumption / open question.

### Step 6 — Produce the review report

Produce, using the shared output templates in `../output_templates/`:
- review_report.md — headline MACHINE-DERIVED + counts; dual view §6A by-item + §6B by-target;
  findings IDed FND/RSK/QST; reason stated even for PASS (CR-AIWS-2026-07-012)
- findings_table.md (or findings.jsonl)
- open_questions.md
- references_used.md
- review_limitations.md

### Step 7 — Capture learning candidates

Emit `learning_candidates.jsonl` per `../../common/lesson_capture_rule.md`. All entries `status: candidate`.
Candidate types: review_rule_candidate, checklist_update_candidate, retrieval_hint_candidate,
false_positive_note_candidate, project_issue_pattern_candidate, output_preference_candidate,
wiki_candidate, blueprint_improvement_candidate.

### Step 8 — Wait for HUMAN feedback

> ⚖ **governance_invariant** `human_gate` — do NOT update confirmed memory / checklist / Wiki / blueprint without HUMAN confirmation; promotion is HUMAN-gated.

Do NOT update confirmed memory, checklist, Wiki, or blueprint automatically. Promotion is
HUMAN-gated.

### Step 9 — Update after HUMAN confirmation

Only after the HUMAN confirms candidates:
- update memory files
- update the checklist if approved
- create a Wiki candidate if approved
- create a blueprint improvement candidate if approved
- update the relevant changelog

---

## 3. Run evidence

For formal review runs, save evidence under the instance workspace:
`workspace/completed_runs/<run_id>/` (run record + outputs + learning_candidates.jsonl).
When the run serves an AIP task, the PRIMARY deliverable lives in the AIP workspace
(`.ai-work/workspaces/<task-id>/`); the instance workspace keeps a run record + pointer, not a
duplicate (Detailed Design v0.2 §8 / AP-CR-14).
