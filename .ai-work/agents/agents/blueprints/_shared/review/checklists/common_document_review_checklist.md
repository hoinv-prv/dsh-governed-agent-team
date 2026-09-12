# Common Document Review Checklist (shared)

> Shared across all Document Review Agent blueprints.
> Mapped from: REVIEW_CHECKLIST_TEMPLATE.md §2 (common quality), §4 (alignment), §5 (readiness)
> (v0.1). Document-type-SPECIFIC checks (§3 of the template) are NOT here — they live in each
> blueprint's local `checklists/<doc_type>_review_checklist.md`.
> Wiki-first NOT Wiki-only: alignment checks compare the document against Wiki AND source.

---

## 1. Checklist metadata

```yaml
checklist_id: common_document_review_checklist
checklist_name: Common Document Review Checklist
version: 0.1
owner: HUMAN/team
status: draft
```

---

## 2. Common document quality checks

| ID | Check Item | Why It Matters | Evidence / Reference | Severity Hint |
|---|---|---|---|---|
| COMMON-001 | Is the document purpose clear? | Prevents wrong usage of the document. | Title, introduction, scope section | Minor/Major |
| COMMON-002 | Is the scope clear and bounded? | Prevents over/under implementation or review. | Scope/non-scope section | Major |
| COMMON-003 | Are assumptions and open questions explicit? | Prevents hidden risk. | Assumption/open question section | Major |
| COMMON-004 | Are terms/names consistent with Wiki/source? | Prevents misunderstanding. | Wiki terminology / source docs | Minor/Major |
| COMMON-005 | Are references to upstream/downstream documents clear? | Supports traceability. | Reference section / source trace | Minor/Major |
| COMMON-006 | Are claims supported by source or clearly marked as assumption? | Prevents false confidence. | Wiki/source/reference | Major |
| COMMON-007 | Are conflicts with Wiki/source reported (not silently resolved)? | Prevents silent inconsistency. | Wiki/source comparison | Major/Critical |

---

## 3. Alignment checks (document vs Wiki AND source)

| ID | Check Item | Why It Matters | Evidence / Reference | Severity Hint |
|---|---|---|---|---|
| ALIGN-001 | Is the document aligned with related requirements? | Prevents missing/wrong implementation. | Requirement docs / Wiki | Major/Critical |
| ALIGN-002 | Is the document aligned with related design decisions? | Prevents architecture/design drift. | Basic design / architecture Wiki | Major |
| ALIGN-003 | Is the document aligned with known project cautions? | Prevents repeated known mistakes. | Wiki cautions / lessons | Major |

---

## 4. Readiness checks (is it good enough for the next actor?)

| ID | Check Item | Why It Matters | Evidence / Reference | Severity Hint |
|---|---|---|---|---|
| READY-001 | Is the document sufficient for the next actor/task? | Prevents handoff failure. | Downstream task needs | Major |
| READY-002 | Are unresolved items clearly listed? | Prevents hidden blockers. | Open questions / TODO | Major |
| READY-003 | Are review limitations clearly stated? | Prevents over-trust in review. | Review report | Minor/Major |

---

## 5. How to use this checklist

- Apply these common items on EVERY document review run, then add the blueprint's
  document-specific checklist (`checklists/<doc_type>_review_checklist.md`).
- For each hit, record a finding using `../process/finding_format.md` and assign severity using
  `../process/severity_definition.md`.
- Alignment checks compare against BOTH Wiki and source (Wiki-first, not Wiki-only); a Wiki/source
  conflict is reported as a `conflict` finding per `../process/source_trace_rule.md`.
- A recurring missed check is a `checklist_update_candidate` per `../../common/lesson_capture_rule.md`
  — candidate only, HUMAN-gated.
