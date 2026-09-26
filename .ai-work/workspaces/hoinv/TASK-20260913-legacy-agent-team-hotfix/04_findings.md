# Findings — TASK-20260913-legacy-agent-team-hotfix

## Confirmed Findings
- HUMAN approved WBS revision 1 hash `95abfac1e7d78df05daee7bd5cb825d679579fd160416cbdea23fe607c3a2f93` via `ask_user_question:approve-legacy-hotfix-v1`.
- Mission is isolated from coordinator `session-ad97e23b-b7c9-4713-ac6f-15f610e9dbac`, approved `multi-mission-web-ui` revision 32, and `packages/gat`.
- Legacy Team readiness counts durable teammates excluding Lead; the historical effective default `minExecutionMembers=2` explained Lead + 2 = 3 people.
- HUMAN requires Lead-only validity, interpreted as zero durable teammates; maximum cap remains configurable.
- HUMAN approved bounded recovery WBS revisions 2–9 after distinct review/verifier findings; current exact plan is revision 9 SHA `79ea97523df2124db54b05eb82bdf6ef2de0244543fe71fb121d53dc87848b71`.
- Lead-only attempt 5 is accepted after whole-file review: schema default and runtime fallback are zero, omitted-config test proves zero, positive-minimum tests explicitly configure their minima, exact approval and max cap remain.
- DSH plan-mode stores approved plan markdown in `exit_plan_mode` call arguments; it has no structured task schema.
- HUMAN selected section-bounded `## Tasks` parsing, one-action merge/import/approve, and merge-only-missing behavior.
- AIP-EXEC-011 lint passed with 0 errors and 0 warnings; dedicated workspace started at STEP-00.
- Approved-plan import attempt 2 is accepted after latest-call fail-closed recovery and independent trust-boundary adjudication; attempt 3 updated only the built-library expected Remote surface and passed independent review.
- One action now imports normalized missing list items only from explicit `## Tasks`, preserves existing tasks, preflights post-import state, appends imported tasks plus exact-revision approval in one serialized flush, and maps invalid sources to localized `team-plan-import-rejected`.
- Canonical integration attempt 6 completed exit 0 with persisted raw evidence; focused 9 files/164 tests, full host/client build, built-library smoke, and assembled dashboard smoke all passed.
- Installed verification reported SUPPORTED, 84 changed paths, zero paths outside the allowlist, and zero secret findings.

## To Verify
- Independent final-report review and explicit HUMAN acceptance.

## Notes
- Governance, Lead-only, and approved-plan-import implementation tasks are accepted; all earlier failed attempts remain charged with distinct evidence.
- Live GUI activation and server restart remain excluded and were not performed.
- Final Capture Sweep: 0 new candidates; 2 total candidates; both HUMAN-triaged `retained_local`; 0 pending relation candidates and no Wiki/Truth promotion.
