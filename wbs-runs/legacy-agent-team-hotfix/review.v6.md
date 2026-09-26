# WBS revision 6 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v6.json`
- SHA-256: `07a175111b15d1e79874c4a6f874bab8fb9365e803584f9f3492328669e12bf9`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 6 is required

Canonical integration attempt 2 passed:

- dedicated reset/clean/regenerate/install;
- all focused tests: 9 files, 164 tests;
- full DSH host/client build and Web shell assembly.

It stopped at the built-library smoke: the generated `agentTeams` Remote descriptor correctly contains both the already-present multi-mission methods and the newly added `importApprovedPlan`, but `packages/core/tests/built-lib.e2e.ts` expects only the older task method list plus import. One test failed; dashboard smoke was not reached.

## Exact recovery

Update only the built-library smoke expected method list to match the current generated Remote surface, preserving the new import method and existing mission methods. Independently review the test-only delta. Then regenerate compatibility, reset/clean/install, and use one additional canonical integration attempt.

## Preserved history and budget

- All 11 prior attempts remain charged.
- Integration attempts 1 and 2 remain failed; no downstream stage is claimed beyond the recorded evidence.
- Revision 6 adds one plan-import recovery attempt (maximum 2→3, effort 120→150 minutes) and one integration attempt (maximum 2→3, effort 90→180 minutes).
- Total ceiling becomes 14 attempts / 840 minutes so the recovery, third integration attempt, and final review can each be charged.
- Product scope, semantics, acceptance, effects, commands, mission isolation, and final HUMAN gate remain unchanged.

Approval authorizes only the expected-descriptor correction and unchanged remaining verification/final work.
