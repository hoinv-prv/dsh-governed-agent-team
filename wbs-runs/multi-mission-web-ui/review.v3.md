# Review candidate multi-mission-web-ui, revision 3

- Plan: `wbs.v3.json`
- Exact SHA-256: `347823ac39155a82709b08650041bbfdc2d5398bd7d7e63406409ace1801f589`
- Objective, scope, commands, external effects, dependencies, and acceptance gates are unchanged from approved revision 2.
- Delta: independent core review `attempt-core-002` found one high-severity validation gap: arbitrary mission task snapshots could be durably appended without duplicate-ID, dependency-graph, initial-revision/status, or ownership validation.
- Revision 3 raises `core-mission-model.max_attempts` from 2 to 3, total attempts from 7 to 8, and effort ceiling from 440 to 530 minutes. The new attempt is limited to adding mission-plan creation/replay validation and focused malformed/duplicate/cyclic/non-v1 task tests, followed by a fresh independent review.
- Cumulative attempts remain preserved: 3 attempts are already charged; no counter is reset.
- Validation: WBS helper API and workspace inspection passed. Order remains discover → core → Web → integration → final.
- Risk: if the third core attempt or its review fails, core and all downstream tasks remain blocked; there is no fourth attempt in this revision.

Approve only this exact revision/hash and bounded additional attempt. Approval does not activate the live Web profile or override DSH policy.
