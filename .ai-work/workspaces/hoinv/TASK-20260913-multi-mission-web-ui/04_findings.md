# Findings

## Confirmed Findings
- HUMAN approved WBS revision 6, SHA-256 `a484fdda4d896f3430c7501b5bbc2c8cbf4b9166d0f2ead3d2133ea0ebe59add`, through `ask_user_question:approve-wbs-v6`.
- Scope is explicit: complete multi-mission Web UI, independent reviews, canonical installed-worktree verification, final human acceptance, and AIP close.
- Core implementation has accepted static review evidence; runtime behavior remains unverified until integration.
- Web attempt 1 failed after leaving partial changes; attempt 2 is the final Web attempt.
- AIWS operating memory was read before step planning and was empty.
- Wiki preflight returned no applicable project multi-mission guidance; one weak unrelated generic review sample was ignored.
- `lint_aip.py` returned exit 0 with zero errors and two warnings about vague STEP-04 evidence inputs. The exact integration/final report paths are nevertheless specified elsewhere in STEP-04 and will be checked during finalization.
- `run_aip.py start` created this workspace, set STEP-00 active, and reported no pending captures.

## Inferred Findings
- Earlier HUMAN design decisions and repeated execution/revision approvals satisfy Gate U1 without a duplicate confirmation request.

## To-Verify Findings
- Partial Web output completeness and correctness.
- Canonical core/Web runtime, build, library smoke, and assembled dashboard smoke.

## Pre-applied Work Inspection
- Accepted core output includes mission types/board/plan validator, durable `team/mission` replay, Remote APIs, isolated approval/conflict tests, and legacy empty-view compatibility. Accepted review: `evidence/core-mission-model/attempt-core-004-review.md`.
- Failed Web attempt 1 changed only `TeamAction.tsx`, `mount.ts`, `locales.ts`, `TeamAction.module.css`, and `team-action.client.spec.tsx`; `browser-plugin.client.spec.ts` remained at its original hash.
- Partial Web bytes contain mission API props/state, concurrent view/list refresh, selected detail loading, creation and exact-revision approval handlers, mission list/detail UI, Remote wiring, localization, CSS, and initial test mocks. Full scenario tests and browser wiring coverage remain incomplete/unverified.
- No implementation child remains active; it is safe to allocate the final Web attempt.

## Integration Attempt 1
- Web attempt 2 completed and a fresh Luna read-only reviewer returned `meets_criteria`; executable proof remained deferred.
- The first integration command failed with exit 1: rollback rejected the stale compatibility source payload at `packages/core/src/index.ts` before touching the target.
- No later integration command ran. `integration.md` records the exact output.
- Source inspection confirms rollback invokes current-source payload validation before target cleanup. A revision is required to reset/clean only the dedicated verification worktree before regeneration.

## Revision-16 Standalone Phase
- Exact WBS revision 16 is HUMAN-approved and independently reviewed PASS.
- Governance repair attempt 2 passed AIP lint/status; cumulative charges are 19 before the threat-model attempt.
- Threat-model/vector attempt 1 is active. Candidate artifacts exist and await independent Security review plus separate HUMAN hash acceptance before code.
- No package code has started.

## Later DSH Test Authorization Input
- HUMAN supplied `/home/hoinv/dev/deepseek-harness` as a test DSH checkout and stated it may be modified as convenient for testing.
- This is a future scope/effect input, not silent authority to violate revision 16, whose approved boundary still forbids DSH access/modification and ends at the standalone implementation freeze.
- After the frozen implementation hash and exact-path conformance phase, a new reviewed WBS may declare this checkout's precise read/write/install/test/rollback effects and request exact-plan approval. No inspection or mutation of that path has occurred.

## Notes
- No AIWS Truth, Wiki, procedural, or tooling file has been modified.
- No live Web profile activation is authorized.
