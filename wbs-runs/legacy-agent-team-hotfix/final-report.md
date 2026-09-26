# Final report — legacy-agent-team-hotfix

## Decision requested

Accept WBS revision 9 (`79ea97523df2124db54b05eb82bdf6ef2de0244543fe71fb121d53dc87848b71`) as complete for the isolated legacy Agent Team hotfix. This report does not close the AIP until explicit HUMAN acceptance is recorded.

## Delivered behavior

### Lead-only Team execution

- `packages/tools/src/index.ts` defaults `minExecutionMembers` to `0` in schema and runtime fallback.
- An exact current HUMAN-approved Team plan remains mandatory.
- Configured positive minimums and the maximum durable teammate cap remain enforced.
- Lead-only prompt/readiness output explicitly permits zero durable teammates without nonsensical “at least 0” copy.
- Focused tests cover omitted default, configured minima, approval gate, and cap.

### One-action approved Chat Plan import

- `packages/core/src/approved-plan-import.ts` selects the latest `exit_plan_mode` call and requires its one later matching successful canonical result; it never falls back to an older approval.
- Only checklist, bullet, or numbered items inside explicit `## Tasks` are accepted. Unknown lines, nested headings, empty/overlong subjects, and malformed checklist-like lines fail with `TEAM_PLAN_IMPORT_INVALID`.
- Subjects are NFKC/whitespace/case normalized for dedupe. Existing active tasks are preserved; only missing tasks are prepared.
- `packages/core/src/index.ts` performs all parsing, task-limit/revision checks, exact post-import preflights, and authorization before one serialized flush containing imported task events plus `team/plan-approved` at the exact resulting revision.
- Remote errors map to `team-plan-import-rejected`; Web localization presents the typed rejection.
- `packages/web/src/client/TeamAction.tsx` uses one Approve action to call import-and-approve and refresh on success.

## Requirement-to-evidence map

| Requirement | Result | Evidence |
|---|---|---|
| AIWS governance and mission isolation | PASS | `AIP-EXEC-011`; dedicated workspace; `wbs.v9.json`; no modifications to `packages/gat` or `wbs-runs/multi-mission-web-ui` |
| Lead-only execution | PASS | accepted Lead-only attempt 6; independent review `282332ec-7e20-4b32-9583-b6fa4862ebcc`; canonical focused suite |
| Approved-plan import/merge/approve | PASS | accepted import attempts 2–4; adjudication `c47fc92c-1daa-47c2-81b1-c9f85018b737`; descriptor review `ac957fb4-cd28-4681-bf40-a2e7bae71e95`; canonical focused/built-lib tests |
| Canonical installed verification | PASS | `integration.md` attempt 6; persisted verifier log; independent integration review `7ee05df0-4636-4bd8-a212-c7a8d85d5189` |

## Canonical verification

Dedicated target: `/home/hoinv/deepseek-harness/.worktrees/verify-gat-install-0.1.5-rc.2` at DSH commit `c291e7961a515f6d7af9304e7fd1d257929aef26`.

Accepted attempt 6 executed the declared reset, clean, compatibility generation, installation, and canonical verifier sequence. All commands exited 0.

- Compatibility: 9 host files, 74 payload files.
- Patchset SHA-256: `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`.
- Payload SHA-256: `2dca38007ed5e0533f04f9f26c0eb140dda29ed593301b29f67b62e7184dd5e5`.
- Install manifest: `gat-0.1.0-dsh-0.1.5-rc.2-c291e796`; 83 files; structural verification PASS.
- Focused suite: 9 files / 164 tests PASS.
- Full DSH host/client build and Web shell assembly: PASS.
- Built-library smoke: PASS.
- Assembled dashboard smoke and fixture inventory: 3 tests PASS.
- Final verifier result: `status: pass`; installed/SUPPORTED; 84 changed paths; 0 outside allowlist; 0 secret findings.

## Attempt history

Nineteen attempts are charged under revision 9's ceiling:

- governance: 1 accepted;
- Lead-only: attempts 1–4 failed with distinct default/test diagnoses; attempts 5–6 accepted/recovered;
- approved-plan import: attempt 1 failed review; attempts 2–4 accepted/recovered;
- integration: attempts 1–3 failed progressively at stale expectations; attempt 4 passed but lacked current-byte evidence; attempt 5 disproved a golden hypothesis; attempt 6 passed all stages with a persisted log;
- final review: attempt 1 failed for insufficient evidence; attempt 2 is active pending independent verdict and HUMAN acceptance.

No failed attempt was erased or reset.

## Reviews and limitations

Independent integration verdict: `meets_criteria`. The source tree is dirty, so installer-reported source hashes are advisory; exact approved WBS hashes, compatibility hashes, and staged integration results are recorded. Attempt-6 raw combined verifier output is persisted under `evidence/integration-verification/attempt-integration-006/verifier.log`, with `integration.md` as the durable summary. No live GUI/profile activation or server restart was performed.

## Capture and open-point sweep

- `05_open_questions.md`: no unresolved open points.
- Both capture candidates were explicitly triaged by HUMAN as `keep_captured_no_promotion`; no Wiki, Truth, tooling, or canonical promotion is part of this hotfix.

## Final state

Implementation and canonical verification are complete. Scoped AIWS lint passed with 0 errors, 0 warnings, and 0 info findings. Remaining gates are independent review of this final report, explicit HUMAN acceptance of the exact reviewed report, and AIP closure.
