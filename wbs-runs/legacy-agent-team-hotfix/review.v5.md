# WBS revision 5 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v5.json`
- SHA-256: `45154051e1a231a175ce9a1eeee0e9af15ae582a232e31ab01a3207d3574b189`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 5 is required

Canonical integration attempt 1 passed reset, clean, compatibility regeneration, install, installer lifecycle checks, and reached the focused suite. It then stopped with 162/164 tests passing. The two failures are exact stale string assertions in the configured-minimum tools tests:

- count 1 test expects the old shorter `requires at least 1 ...; found 0` fragment;
- count 2 test expects the old shorter `requires at least 2 ...; found 0` fragment.

The observed runtime messages correctly retain both mandatory concepts: exact current HUMAN-approved plan plus the configured positive teammate threshold. Product behavior is not changed.

## Exact recovery

Update only those two assertions to the approval-aware deterministic text (or a precise fragment that includes the configured threshold and observed count). Independently review the test-only delta, regenerate compatibility, reset/clean/install, and use the already-authorized second integration attempt for one canonical verifier rerun.

## Preserved history and budget

- Governance accepted.
- Lead-only attempts 1–5 remain charged; attempt 5 was statically accepted before runtime exposed only stale assertions.
- Plan-import attempts 1–2 remain charged; attempt 2 is accepted after fail-closed recovery and trust-boundary adjudication.
- Integration attempt 1 remains charged and failed; no later verifier stages are claimed.
- Revision 5 adds one Lead-only recovery attempt: task maximum 5→6, total attempts 11→12, effort 690→720 minutes.
- Integration maximum remains 2; final maximum remains 1.
- All scope, product semantics, external effects, commands, requirements, and mission isolation remain unchanged.

Approval authorizes only this test recovery and the unchanged remaining integration/final work.
