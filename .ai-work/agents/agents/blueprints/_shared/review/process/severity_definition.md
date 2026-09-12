# Severity Definition (shared)

> Shared across all Document Review Agent blueprints.
> Mapped from: REVIEW_AGENT_BLUEPRINT_TEMPLATE.md §11 (v0.1).
> Document-type-agnostic baseline. A document-type blueprint MAY add type-specific examples for
> each tier in its own profile/checklist, but MUST NOT change the meaning of the tiers below.

---

## Severity tiers

### Critical
Causes serious requirement/design failure, data loss, security risk, release blocker, or major
implementation misdirection. Must be resolved or explicitly accepted by HUMAN before the document
is used downstream.

### Major
Likely to cause a bug, rework, missing requirement, test failure, or handoff misunderstanding.
Should be fixed before the document is relied on.

### Minor
Reduces clarity or completeness but does not block implementation or review. Fix when convenient.

### Suggestion
Improvement idea for readability, maintainability, or future quality. Optional.

---

## How to assign severity

- Severity reflects implementation / project RISK, not how easy the finding was to spot.
- A finding with no evidence is not automatically Minor — assess the risk if the suspicion is
  correct, then mark it as `possible_issue` or `open_question` (see `finding_format.md`).
- A conflict between the document and Wiki/source is at least Major; raise to Critical when it
  would cause a release blocker or data/security problem if shipped.
- When unsure between two tiers, pick the higher tier and state the uncertainty in the finding.

---

## Per-type examples (blueprint-local)

Each document-type blueprint supplies concrete examples for its type, e.g.:
- Critical example: <type-specific>
- Major example: <type-specific>
- Minor example: <type-specific>
- Suggestion example: <type-specific>

These examples illustrate the tiers for that document type; they do not redefine the tiers.

---

## Verdict tokens (per checklist item) — CR-AIWS-2026-07-012

Two DISTINCT layers: **verdict** = per-check token (reproducibility layer, below); **severity** =
finding impact (tiers above, used when rolling findings up). Do not mix them.

Each runtime checklist item gets exactly one token, assigned by the **leg-classified rubric**
(mechanical ladder — no "does this block implementation?" gut call; see
`Runtime_Review_Methodology_MVP` §4, instantiated by the `aiws-runtime-review-checklist` skill):

| Token | When |
|---|---|
| `N/A` | an explicit n_a_condition / cited scope-out applies (guarded categories: only on explicit match or HUMAN confirm) |
| `QUESTION` | a needed leg requires an out-of-scope / un-openable source, or a business/environment fact only HUMAN can confirm |
| `FAIL` | any **HARD** leg is absent / contradicted |
| `RISK` | any **SOFT** leg is absent, or present only as advisory/modal wording |
| `PASS` | all legs satisfied |
| `NOT_CHECKED` | initial state — not yet run |

## Headline (machine-derived) — CR-AIWS-2026-07-012

> ⚖ **governance_invariant** `machine_headline` — the review headline is DERIVED from the per-item verdicts by the precedence below, never set by judgment; a clean PASS headline is forbidden while any selected non-N/A item is FAIL / RISK / QUESTION / NOT_CHECKED.

```text
headline = FAIL        if any selected non-N/A item is FAIL
         else RISK      if any selected non-N/A item is RISK      ("RISK / CONDITIONAL-PASS")
         else INCOMPLETE if any selected non-N/A item is QUESTION or NOT_CHECKED
         else PASS
```

Report the headline together with counts (PASS / FAIL / RISK / QUESTION / N/A / NOT_CHECKED).
