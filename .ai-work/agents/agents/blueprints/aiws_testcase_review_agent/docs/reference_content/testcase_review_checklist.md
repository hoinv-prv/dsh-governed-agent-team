> **REFERENCE SEED (CR-AIWS-2026-08-008 T2)** — domain content, lớp project-local. KHÔNG auto-copy
> khi tạo desk; wizard offer như một nguồn `domain content` (manifest CR-AIWS-2026-08-009).
> Skeleton portable của ATDB không còn chứa file này (content contract: agent_runtime_design §10).

# Test Case Review Checklist (blueprint-local)

> Document-type-SPECIFIC checklist for the Test Case Review Agent.
> Mapped from: Document_Review_Agent_Blueprint/templates/REVIEW_AGENT_BLUEPRINT_TEMPLATE.md §8-§9
> + examples/TESTCASE_REVIEW_AGENT_EXAMPLE.md (template_version v0.1).
> Use TOGETHER WITH the shared common checklist
> (`../../_shared/review/checklists/common_document_review_checklist.md`): apply the common items on
> every run, then add the test-case-specific items below.
> Wiki-first NOT Wiki-only: coverage is judged against the requirement/design AND Wiki, not against
> the set of cases that already exist.

---

## 1. Checklist metadata

```yaml
checklist_id: testcase_review_checklist
checklist_name: Test Case Review Checklist
document_type: Test Case Document
version: 0.1
owner: HUMAN/team
status: draft
```

---

## 2. Coverage checks (the test-case lens)

| ID | Check Item | Coverage Axis | Finding Category | Why It Matters | Severity Hint |
|---|---|---|---|---|---|
| TC-001 | Are all in-scope requirements/features covered by at least one case? | requirement coverage | coverage_gap | A requirement with no test ships unverified. | Major/Critical |
| TC-002 | Are normal, abnormal, and error-path cases all present (not only happy paths)? | normal/abnormal balance | abnormal_case_gap | Abnormal paths are where most defects hide. | Major |
| TC-003 | Are boundary / limit / off-by-one values exercised on relevant inputs? | boundary | boundary_case_gap | Boundary defects are common and high-impact. | Major |
| TC-004 | Are role / permission / authorization variations covered where they change behavior? | role/permission | coverage_gap | Authorization gaps are security/correctness risks. | Major/Critical |
| TC-005 | Are data-state variations covered (empty, single, many, stale, conflicting)? | data state | coverage_gap | Behavior often differs by data state. | Major |
| TC-006 | Are status / state-transition paths covered (valid AND invalid transitions)? | status transition | coverage_gap | Invalid transitions are a frequent defect source. | Major |
| TC-007 | Are validation rules and error/exception messages covered and asserted? | error/validation | coverage_gap | Unasserted errors let silent failures pass. | Major |
| TC-008 | Are preconditions explicit, sufficient, and reproducible? | precondition | precondition_gap | Ambiguous setup makes a case non-runnable. | Minor/Major |
| TC-009 | Is test data specified clearly enough to reproduce the case? | test data | test_data_gap | Vague data yields non-deterministic results. | Minor/Major |
| TC-010 | Are expected results specific, verifiable, and tied to an observable outcome? | expected result | expected_result_ambiguity | "Works correctly" is not testable. | Major |
| TC-011 | Are regression-risk areas (changed/critical paths) protected by coverage? | regression | regression_risk | Unprotected hot paths break silently. | Major/Critical |
| TC-012 | Is each requirement traceable to its case(s), with no orphan/duplicate cases? | requirement trace | requirement_trace_gap | Untraced requirements hide coverage gaps. | Major |
| TC-013 | Are dependencies / mocks / stubs / environment assumptions stated? | environment | precondition_gap | Hidden dependencies cause flaky/false results. | Minor/Major |

---

## 3. Source / Wiki alignment checks (Wiki-first, NOT Wiki-only)

| ID | Check Item | Finding Category | Evidence / Reference | Severity Hint |
|---|---|---|---|---|
| TC-ALIGN-001 | Do the cases match the CURRENT requirement/design (not a stale version)? | requirement_trace_gap | requirement/design doc + Wiki | Major/Critical |
| TC-ALIGN-002 | Do expected results agree with the requirement and Wiki (no contradiction)? | conflict | requirement/Wiki/source | Major/Critical |
| TC-ALIGN-003 | Are known project cautions / past defects reflected in the cases? | regression_risk | Wiki cautions / lessons | Major |

> When the requirement, Wiki, and test cases disagree, REPORT the conflict (finding type
> `conflict`) per `../../_shared/review/process/source_trace_rule.md` — do not silently pick a side.

---

## 4. Output-readiness checks

| ID | Check Item | Why It Matters | Severity Hint |
|---|---|---|---|
| TC-READY-001 | Is each coverage gap stated with the specific requirement/axis it misses? | Generic gaps are not actionable. | Major |
| TC-READY-002 | Are review limitations stated (axes not assessed, references missing)? | Prevents over-trust in the review. | Minor/Major |
| TC-READY-003 | Are open questions for the test author/HUMAN clearly listed? | Prevents hidden blockers. | Major |

---

## 5. Severity examples (test-coverage lens)

These illustrate the shared severity tiers (`../../_shared/review/process/severity_definition.md`)
for this document type; they do NOT redefine the tiers.

```text
Critical:
  A major requirement has NO test coverage at all, or a security/authorization path is untested
  (e.g. an unauthorized-access case is entirely missing).

Major:
  Important abnormal / boundary / status-transition cases are missing, OR an expected result is so
  vague it cannot be verified (e.g. "system behaves correctly"), OR a regression-prone hot path is
  unprotected.

Minor:
  Test data or precondition wording is incomplete but the intent is inferable; case grouping makes
  coverage hard to read but the coverage exists.

Suggestion:
  Improve case naming, grouping, or requirement-to-case traceability format for maintainability.
```

---

## 6. How to use this checklist

- Apply the shared common checklist FIRST
  (`../../_shared/review/checklists/common_document_review_checklist.md`), then this test-case
  checklist.
- For each hit, record a finding using `../../_shared/review/process/finding_format.md`, set the
  finding `Category` to the matching category above, and assign severity using
  `../../_shared/review/process/severity_definition.md`.
- Judge coverage against the REQUIREMENT/design + Wiki, not against the cases that already exist.
- A recurring missed coverage axis is a `checklist_update_candidate` per
  `../../_shared/common/lesson_capture_rule.md` — candidate only, HUMAN-gated.
