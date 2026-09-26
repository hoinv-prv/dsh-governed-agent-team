# WBS revision 7 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v7.json`
- SHA-256: `67dc8367df9a0b66770c3faa81b9c7a3795e9217c93edb98c50db355ef36000c`
- Validation: PASS.
- Status: candidate, not approved.

## Why revision 7 is required

Canonical integration attempt 3 passed every preceding stage:

- reset/clean/regenerate/install;
- all 164 focused tests;
- full DSH host/client build and Web shell assembly;
- built-library smoke.

The final assembled dashboard smoke failed one golden comparison. Runtime correctly shows the already-present empty Missions section, but `verification/web/task.expected.md` omits exactly:

- heading `Missions`;
- button `Add Mission`;
- text `No missions yet`.

## Exact recovery

Update only `verification/web/task.expected.md` with those three observed lines in their exact rendered position after Plan approval and before Members. Independently review the golden delta, regenerate compatibility, reset/clean/install, and run the canonical verifier once.

## Scope and budget delta

- All 13 prior attempts remain charged.
- Integration attempts 1–3 remain failed with their staged evidence preserved.
- Root and integration write scopes add only `verification/web/task.expected.md`.
- Integration maximum becomes 4 and effort 270 minutes.
- Total ceiling becomes 15 attempts / 930 minutes, leaving one integration attempt and the final review attempt.
- No product behavior, mission/UI architecture, live profile, server, other mission control, or acceptance rule changes.

Approval authorizes only the exact golden update and unchanged remaining verification/final work.
