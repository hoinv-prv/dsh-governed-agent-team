# Output templates (references shared) — Detailed Design Review Agent

The review report and its companion templates are document-type-AGNOSTIC and are NOT duplicated here.
They live once under the shared review folder and are referenced (not copied) to avoid drift. See
`blueprint.yaml` -> `output_templates` for the bound paths.

| Output template | Shared location (relative to this blueprint folder) |
|---|---|
| Review report | `../../_shared/review/output_templates/review_report.md` |
| Findings table | `../../_shared/review/output_templates/findings_table.md` |
| Open questions | `../../_shared/review/output_templates/open_questions.md` |
| References used | `../../_shared/review/output_templates/references_used.md` |
| Review limitations | `../../_shared/review/output_templates/review_limitations.md` |

`output_contract` (in `blueprint.yaml`):
- required: `review_report.md`, `findings_table.md`, `open_questions.md`, `references_used.md`,
  `learning_candidates.jsonl`
- optional: `findings.jsonl`, `review_limitations.md`, `suggested_revision.md`

There is no detailed-design-specific output template — the shared report shape covers this document
type. Detailed-design specificity is carried through the findings (categories, severity examples) and
the document-specific checklist, not through a different report layout.
