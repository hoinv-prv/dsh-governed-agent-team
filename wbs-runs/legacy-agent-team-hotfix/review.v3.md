# WBS revision 3 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v3.json`
- SHA-256: `62b39c67c0597e4851519ce91867d68a18395fcc460556299f000e00ce5b7b27`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 3 is required

Revision 2 authorized the third Lead-only attempt. That attempt correctly aligned both effective defaults:
- schema: `default(0)`;
- runtime apply: `config.minExecutionMembers ?? 0`.

Independent review then found a stale legacy test that omitted the minimum but expected two teammates. Coordinator inspection found a second implicit-old-default test. Since correcting tests after a failed review is a new attempt, revision 3 adds exactly one bounded recovery attempt.

## Recovery hypothesis

Preserve the tests' original intent by explicitly configuring `minExecutionMembers: 2` in both legacy cases:
1. nested non-allowlisted calls must remain denied until approval plus two configured teammates;
2. spawning remains allowed when the only diagnostic is a configured two-member shortage.

The dedicated Lead-only test continues to omit the minimum and prove the new default zero. No source behavior beyond the already-reviewed schema/runtime default alignment changes.

## Budget/history

- Governance attempt 1 accepted.
- Lead-only attempts 1–3 remain charged and failed with distinct review findings.
- Revision 3 raises Lead-only max attempts 3→4, total attempts 9→10, effort 630→660 minutes.
- Approved-plan-import and integration have not started.
- All other scope, effects, commands, requirements, dependencies, reviews, and mission isolation remain unchanged.

Approval authorizes attempt 4 and unchanged downstream work. It does not accept current bytes or pre-accept runtime verification.
