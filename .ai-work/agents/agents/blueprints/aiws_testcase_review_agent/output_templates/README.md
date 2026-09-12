# Output templates — Test Case Review Agent

This review blueprint does NOT keep its own copies of the review output templates. To avoid drift,
the output templates are document-type-AGNOSTIC and shared across all review blueprints. They live
once under the shared review assets and are referenced by relative path from `blueprint.yaml`
(`output_templates:` block).

Shared output templates (relative to this folder):

- `../../_shared/review/output_templates/review_report.md`
- `../../_shared/review/output_templates/findings_table.md`
- `../../_shared/review/output_templates/open_questions.md`
- `../../_shared/review/output_templates/references_used.md`
- `../../_shared/review/output_templates/review_limitations.md`

The findings table is filled using `../../_shared/review/process/finding_format.md`; the test-case
finding categories (coverage_gap, abnormal_case_gap, boundary_case_gap, expected_result_ambiguity,
precondition_gap, test_data_gap, regression_risk, requirement_trace_gap) are defined in this
blueprint's `blueprint.yaml` (`finding_categories:`) and `docs/reference_content/testcase_review_checklist.md` (reference seed).
