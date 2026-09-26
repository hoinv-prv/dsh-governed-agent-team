# WBS revision 9 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v9.json`
- SHA-256: `79ea97523df2124db54b05eb82bdf6ef2de0244543fe71fb121d53dc87848b71`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 9 is required

Revision 8 changed only the dashboard golden to `Import approved plan and approve`, based on current project source. Canonical attempt 5 disproved that hypothesis:

- reset/clean/regenerate/install, focused tests, full build, and built-library smoke passed;
- the assembled dashboard still rendered `Approve current plan`, exactly as attempts 3–4 had observed;
- dashboard comparison failed only on that label; 2/3 dashboard tests passed;
- complete combined verifier output is durably stored at `evidence/integration-verification/attempt-integration-005/verifier.log`.

The stable runtime behavior matters more than the unused English dictionary literal for this assembled target. The product requirement is one-click import-then-approve behavior, not mandatory button wording.

## Exact recovery

1. Change only English `approvePlan` source copy back to `Approve current plan`; do not change the RPC/action implementation or typed rejection copy.
2. Revert only the dashboard golden button label/text to `Approve current plan`; retain the reviewed Missions section.
3. Independently review that source/golden copy alignment does not change behavior.
4. Regenerate compatibility, reset/clean/install, and rerun the full canonical verifier with raw output persisted under attempt 6.
5. Complete durable review/workspace evidence and perform the already-authorized second final review.

## Preserved history and budget

- All 16 prior attempts remain charged.
- Integration attempt 5 remains failed with raw evidence; no rerun is hidden.
- Approved-plan-import maximum becomes 4 (one copy-only recovery attempt); integration maximum becomes 6.
- Total ceiling becomes 19 attempts / 1170 minutes, exactly covering import attempt 4, integration attempt 6, and final-review attempt 2.
- Parser, merge/dedupe, approval atomicity, Lead-only behavior, authorization, limits, mission isolation, and final HUMAN acceptance are unchanged.

Approval authorizes only the English copy/golden alignment, one full persisted canonical rerun, and unchanged evidence-bound closure.
