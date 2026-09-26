# WBS revision 4 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v4.json`
- SHA-256: `6998784540c089965201296def7960802ad75691264a6920f60450184892f92e`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 4 is required

Revision 3 authorized attempt 4 to make two stale old-default tests explicitly configure `minExecutionMembers: 2`. A whole-file independent review then found one final implicit old-default assumption: the complete-envelope diagnostics test creates two teammates and asserts `requiredActiveTeammates: 2`, but its setup does not configure a minimum.

## Exact recovery

Add `minExecutionMembers: 2` to that complete-envelope test setup. This preserves its intended configured-readiness envelope without changing product behavior. The default-zero test remains the only omitted-minimum behavior assertion and continues to prove Lead-only readiness.

The reviewer searched the full focused test file and reported no other implicit `required 2` matches.

## Budget/history

- Governance attempt 1 accepted.
- Lead-only attempts 1–4 remain charged and failed with distinct findings.
- Revision 4 raises Lead-only max attempts 4→5, total attempts 10→11, effort 660→690 minutes.
- Approved-plan-import and integration have not started.
- All other scope, effects, commands, requirements, dependencies, reviews, and ownership isolation remain unchanged.

Approval authorizes attempt 5 and unchanged downstream work; it does not accept current bytes or pre-accept verification.
