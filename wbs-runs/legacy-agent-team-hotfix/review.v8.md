# WBS revision 8 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v8.json`
- SHA-256: `bd90415f5a4c6d268b9326a86088bee26e24856349a3908ee5d0bbe6b9c9a288`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 8 is required

Final-review attempt 1 returned `insufficient_evidence` despite integration attempt 4 exiting 0:

1. Current `packages/web/src/client/locales.ts` renders `Import approved plan and approve`, while `verification/web/task.expected.md` still expects `Approve current plan`. Current source and accepted golden are not mutually consistent.
2. Raw verifier output was not persisted under the execution evidence directory.
3. Review verdicts were referenced only by runtime UUIDs/opaque strings; no durable review summaries existed.
4. STEP-01/02/03 output metadata and workspace final-output/brief artifacts remained draft/unverified/placeholders.
5. `mission.md` contained stale plan-only status; that control summary has now been reconciled for this candidate revision.

## Exact recovery

- Change only the dashboard golden approval label/text to `Import approved plan and approve`; retain the independently reviewed Missions lines.
- Persist canonical attempt-5 combined stdout/stderr under `evidence/integration-verification/attempt-integration-005/verifier.log` via the exact approved `bash -lc ... | tee ...` command.
- Persist bounded Markdown summaries for all acceptance-relevant independent reviews with reviewer IDs, verdicts, evidence, and limitations.
- Reconcile STEP-01/02/03 metadata plus `00_task_brief.md` and `11_output_final.md` to the actual accepted outputs without changing AIWS Truth/Wiki/tooling.
- Reset/clean/regenerate/install and rerun the complete canonical verifier.
- Produce a corrected final report, rerun scoped lint, obtain a new independent final verdict, then ask HUMAN to accept the exact reviewed report.

## Preserved history and budget

- All 15 prior attempts remain charged.
- Integration attempt 4 remains recorded as exit 0 but its acceptance is revoked by the final-review reconciliation; it is not treated as current-byte proof.
- Final-review attempt 1 remains failed with verdict `insufficient_evidence`.
- Integration maximum becomes 5; final-review maximum becomes 2.
- Total ceiling becomes 17 attempts / 1050 minutes, exactly covering integration attempt 5 and final-review attempt 2.
- Product behavior, parser/authorization semantics, mission isolation, external target, and HUMAN final acceptance remain unchanged.

Approval authorizes only this current-byte/evidence recovery and unchanged final closure flow.
