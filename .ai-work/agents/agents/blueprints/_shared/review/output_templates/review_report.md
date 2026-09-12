# Review Report

> Shared output template for all Document Review Agent blueprints.
> Mapped from: REVIEW_OUTPUT_TEMPLATE.md (v0.1). Fill per run.
> Companion files in this folder: findings_table.md, open_questions.md, references_used.md,
> review_limitations.md. Use the companions for the detailed tables; this report links/summarizes.

## 1. Review Metadata

- Review ID:
- Agent Task Desk:          <!-- instance_id -->
- Source Blueprint:        <!-- blueprint_id @ blueprint_version -->
- Target Document:
- Document Type:
- Review Scope:
- Review Depth:            <!-- quick / standard / deep -->
- Review Date:

## 2. Review Summary

<!-- 2-4 sentences: what was reviewed, the headline result, the most important finding. -->

## 3. References Used

<!-- Summary; full detail in references_used.md. Wiki-first, NOT Wiki-only. -->

| Reference | Type | Used For | Notes |
|---|---|---|---|

## 4. Review Limitations

<!-- Summary; full detail in review_limitations.md. What was NOT checked, missing references,
     assumptions, confidence limits. -->

## 5. Overall Assessment

<!-- CR-AIWS-2026-07-012: headline is MACHINE-DERIVED from per-item verdicts (precedence
     FAIL → RISK → INCOMPLETE → PASS — see ../process/severity_definition.md §Headline).
     Never set by judgment. Include the counts line. -->

```text
Headline: <FAIL / RISK (CONDITIONAL-PASS) / INCOMPLETE / PASS>
Counts:   PASS=<n> FAIL=<n> RISK=<n> QUESTION=<n> N/A=<n> NOT_CHECKED=<n>
Legacy:   <Ready / Needs Fix / Needs HUMAN Decision / Not Enough Information>
```

## 6. Findings (IDed — single source of detail)

<!-- Summary or full table; detailed table in findings_table.md.
     Severity: see ../process/severity_definition.md. Format: see ../process/finding_format.md.
     CR-AIWS-2026-07-012: IDs FND-nn / RSK-nn / QST-nn; findings invariant #findings == #non-PASS
     when a runtime checklist was used; every finding carries [fact]/[inference] + Trace. -->

| ID | Severity | Type | Category | Location | Finding | Fact/Inference | Evidence / Reference | Trace | Impact | Suggested Action | HUMAN Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|

## 6A. VIEW A — by check item (CR-AIWS-2026-07-012)

<!-- One row per runtime checklist item (grouped by region/check). Reason is MANDATORY even for
     PASS. Finding IDs reference §6 — do not repeat detail here. -->

| Item id | Target | Verdict | Reason (even for PASS) | Finding IDs |
|---|---|---|---|---|

## 6B. VIEW B — by target (CR-AIWS-2026-07-012)

<!-- One row per review target. When the subject is a LIST (each row/entry/command reviewed
     separately) → EACH ELEMENT = ONE TARGET. Aggregate verdict = worst of the target's items
     (precedence in severity_definition.md). Multi-viewpoint → one verdict column per viewpoint
     + an overall column. -->

| Target | Verdict (aggregate) | Reason (summary) | Finding IDs |
|---|---|---|---|

## 7. Open Questions

<!-- Summary; full table in open_questions.md. -->

| ID | Question | Related Location | Why It Matters | Suggested Owner |
|---|---|---|---|---|

## 8. Risks

| ID | Risk | Impact | Mitigation / Next Action |
|---|---|---|---|

## 9. Suggested Next Actions

<!-- Concrete next steps for the HUMAN / author. -->

## 10. Learning Candidates

<!-- Link to workspace/completed_runs/<run_id>/learning_candidates.jsonl or summarize proposed
     candidates. All status: candidate — HUMAN-gated. See ../../common/lesson_capture_rule.md. -->
