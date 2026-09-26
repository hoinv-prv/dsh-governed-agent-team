# WBS revision 25 review

Status: independently reviewed PASS for presentation; execution stopped pending HUMAN decision.

Plan: `wbs.v25.json`  
SHA-256: `01f4d1af08d25092743b5c29cc489ef9781fef3969cbf0e2f4fa6fdd49f443ac`

Independent review: `revision-reviewer`, message `team-message-48023800-8e7e-437f-90a5-b979f386c252`.

## Why revision 25 is necessary

Policy attempt 2 exhausted revision 24's two policy attempts after focused tests passed but independent review found four exact semantic gaps: selector classification breadth; logical path containment; deficient/full-response timing enforcement; and exact resource/correlation/decision/issued-at selector binding.

At charge 45, revision 24 has only five total attempts left but its remaining per-task allocation cannot fund both a new policy attempt and every downstream/freeze gate. Revision 25 preserves scope by reallocating the unused tenth memory attempt to policy and combining wrapper admission plus the already-synthetic conformance runner into one serialized task/attempt. Their distinct exact commands, scopes, STEP-09→STEP-10 transition, independent review lanes, and no-baseline-execution rule remain intact.

## Exact remaining budget

Current: 45 / 50 charged. Remaining exactly five:

1. revision-25 reconciliation/selection;
2. policy attempt 3;
3. combined wrapper admission + synthetic runner;
4. integration/build/smoke;
5. freeze/handoff/lint/final HUMAN acceptance.

Effort ceiling: 6,260 minutes. Maximum parallelism remains 2, although the remaining dependency path is serialized.

## Incident requiring HUMAN disposition

During v25 planning, the coordinator invoked the global helper path `/home/hoinv/.agents/skills/dsh-wbs-build/scripts/wbs.mjs`. It returned no output and made no write/build/install/runtime effect. A later `readlink -f` showed that the global path resolves into `/home/hoinv/deepseek-harness/.agents/skills/dsh-wbs-build/scripts/wbs.mjs`.

This was read-only but still crossed the mission's explicit no-DSH-checkout-access boundary. It is recorded in `incident-dsh-read-boundary-001.md`; it is not minimized or silently waived. Revision 25 requires an explicit HUMAN ACCEPT/HOLD/REJECT disposition. Missing, HOLD, or REJECT forbids plan selection and further product work.

No DSH install/build/patch/runtime integration occurred. No accepted conformance baseline ran.

## Independent conclusion

Manual review confirms the corrected v25 structure matches the prior validated plan shape; DAG is acyclic; command/grant containment holds; v24/current controls/incident are hash-pinned; 45 charges and all evidence are preserved; arithmetic closes exactly at 50; wrapper/runner obligations remain complete. The independent reviewer did not access DSH or run commands.

Execution may resume only if the HUMAN explicitly ACCEPTS the disclosed incident and approves exact revision 25/hash in the same or separate response.
