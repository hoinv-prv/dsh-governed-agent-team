# Process (references shared) — Detailed Design Review Agent

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

Detailed-design-SPECIFIC additions to the process live in this blueprint:
- `../docs/reference_content/detailed_design_review_checklist.md` (reference seed) (document-specific checks)
- `blueprint.yaml` -> `severity_examples`, `finding_categories`, `document_specific` skills.
