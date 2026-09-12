> **REFERENCE SEED (CR-AIWS-2026-08-008 T2)** — domain content, lớp project-local. KHÔNG auto-copy
> khi tạo desk; wizard offer như một nguồn `domain content` (manifest CR-AIWS-2026-08-009).
> Skeleton portable của ATDB không còn chứa file này (content contract: agent_runtime_design §10).

# Detailed Design Review Checklist (blueprint-local)

> Document-type-SPECIFIC checklist for the Detailed Design Review Agent.
> Mapped from: REVIEW_CHECKLIST_TEMPLATE.md §3 (document-specific) + DETAILED_DESIGN_REVIEW_AGENT_EXAMPLE.md (v0.1).
> The COMMON checks (quality / alignment / readiness) are SHARED, not duplicated here — apply them
> from `../../_shared/review/checklists/common_document_review_checklist.md` first, then this list.
> Wiki-first NOT Wiki-only: alignment checks compare the design against Wiki AND source.

---

## 1. Checklist metadata

```yaml
checklist_id: detailed_design_review_checklist
checklist_name: Detailed Design Review Checklist
document_type: detailed_design_document
version: 0.1
owner: HUMAN/team
status: draft
extends: ../../_shared/review/checklists/common_document_review_checklist.md
```

---

## 2. How to use

1. Apply the SHARED common checklist first
   (`../../_shared/review/checklists/common_document_review_checklist.md`).
2. Then apply the detailed-design-specific checks below.
3. For each hit, record a finding using `../../_shared/review/process/finding_format.md`, assign
   severity using `../../_shared/review/process/severity_definition.md` (detailed-design severity
   examples live in `blueprint.yaml` -> `severity_examples`), and set the finding `Category` to one
   of the finding categories in `blueprint.yaml` -> `finding_categories`.
4. Alignment checks compare against BOTH Wiki and source; a Wiki/source conflict is reported as a
   `conflict` finding per `../../_shared/review/process/source_trace_rule.md` — never resolved
   silently.
5. A recurring missed check is a `checklist_update_candidate` per
   `../../_shared/common/lesson_capture_rule.md` — candidate only, HUMAN-gated.

---

## 3. Detailed-design-specific checks

| ID | Check Item | Category | Why It Matters | Evidence / Reference | Severity Hint |
|---|---|---|---|---|---|
| DD-001 | Are related requirements fully and correctly reflected in the design? | requirement_gap | Prevents missing or wrong implementation vs requirements. | Requirement definition / basic design / Wiki | Major/Critical |
| DD-002 | Are business rules complete, including exceptions and edge conditions? | business_rule_gap | Prevents wrong data updates and missed exception handling. | Business rules / requirement docs / Wiki | Major/Critical |
| DD-003 | Are screen, API, and DB responsibilities and fields mutually consistent? | consistency_issue | Prevents field/responsibility mismatch across layers. | Screen / API / DB specs | Major |
| DD-004 | Are status transitions fully defined (initial, valid, invalid, cancel, retry, rollback, terminal)? | status_transition_gap | Prevents undefined/illegal state behavior. | State diagram / status table | Major/Critical |
| DD-005 | Are input validation rules and validation messages defined? | error_handling_gap | Prevents inconsistent/insecure input handling. | Validation section / API spec | Major |
| DD-006 | Are exception, error-handling, and cancel/retry/rollback behaviors defined where needed? | error_handling_gap | Prevents undefined failure behavior and data corruption. | Error-handling section / sequence | Major/Critical |
| DD-007 | Are data create/update/delete timings and ownership clear? | data_model_issue | Prevents data-lifecycle and ownership ambiguity. | DB design / data lifecycle section | Major |
| DD-008 | Are role/permission rules clear and consistent with requirements? | business_rule_gap | Prevents permission/security defects. | Permission matrix / requirement docs | Major/Critical |
| DD-009 | Are external interfaces, batch timing, and dependencies clearly defined? | consistency_issue | Prevents integration and scheduling failures. | Interface spec / batch design | Major |
| DD-010 | Is the document sufficient for implementation and test-case creation (offshore-handoff ready)? | handoff_risk | Prevents handoff failure and rework. | Whole document vs downstream needs | Major |
| DD-011 | Are ambiguous or under-specified statements that block implementation flagged? | ambiguity | Prevents differing interpretations during implementation. | Any unclear section | Minor/Major |
| DD-012 | Are testability concerns (observable results, preconditions) addressed? | testability_issue | Prevents un-testable design reaching test-case creation. | Acceptance / expected behavior sections | Major |

---

## 4. Severity for this document type

Tier meanings are SHARED (`../../_shared/review/process/severity_definition.md`). Detailed-design
examples that illustrate each tier are in `blueprint.yaml` -> `severity_examples`. Severity reflects
implementation / project risk, not how easy the finding was to spot.
