# Process (references shared) — Test Case Review Agent

The review process for this blueprint is document-type-AGNOSTIC and is NOT duplicated here. It lives
once under the shared review folder and is referenced (not copied) to avoid drift. See
`blueprint.yaml` -> `process_docs` for the bound paths.

| Process asset | Shared location (relative to this blueprint folder) |
|---|---|
| Review process | `../../_shared/review/process/document_review_process.md` |
| Severity definition | `../../_shared/review/process/severity_definition.md` |
| Finding format | `../../_shared/review/process/finding_format.md` |
| Source-trace rule (Wiki-first NOT Wiki-only) | `../../_shared/review/process/source_trace_rule.md` |
| Lesson-capture rule (no auto-promotion) | `../../_shared/common/lesson_capture_rule.md` |

Test-case-SPECIFIC additions to the process live in this blueprint:
- `../docs/reference_content/testcase_review_checklist.md` (reference seed) (coverage / alignment / readiness checks)
- `blueprint.yaml` -> `severity_examples`, `finding_categories`, `skills` (coverage-axis skills).
