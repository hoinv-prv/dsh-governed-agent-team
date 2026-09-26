# Findings

## Findings List
- Gate U1 task understanding confirmed by HUMAN on 2026-09-26.

## Confirmed Findings
- Agent Team UI must show only the current mission and member list.
- Remove add-mission and add-task controls and remove the task list from the UI.
- Avoid backend/data-model changes unless required for build compatibility.
- HUMAN requested active delegation across team members according to task difficulty and capability.

## Inferred Findings
- Existing current-mission presentation defines the retained mission fields unless implementation evidence requires clarification.

## To-Verify Findings
- AIP pre-start lint passed with 0 errors and one non-blocking step-input locator warning.
- Component paths and focused verification commands remain to be resolved in STEP-01.

## STEP-01 affected-file map
- Primary UI: `packages/web/src/client/TeamAction.tsx`; retained mission selector/detail is around its mission render block, retained roster follows it, while Add Mission and Add Task/task-list blocks are separate.
- Supporting presentation: `packages/web/src/client/TeamAction.module.css` and `packages/web/src/client/locales.ts`.
- Focused unit coverage: `packages/web/tests/team-action.client.spec.tsx`; browser wiring coverage: `packages/web/tests/browser-plugin.client.spec.ts`.
- E2E/golden coverage: `verification/web/gat-agent-team-panel.e2e.ts` and `verification/web/snapshots/gat-agent-team-panel/task.expected.md`.
- No backend/core/mount change is expected because the request only removes UI affordances and preserves existing mission/member data.
- HUMAN decision: “current mission” means the most recently created mission, using the mission board’s existing creation order; captured as CAP-001.
- The UI must also remove plan approval, mission selector/list, mission approval/task summary, and shared-task sections so the visible surface is truly mission + members only.
- Baseline target files already contain uncommitted changes; implementation must preserve them and make a minimal additive diff.

## STEP-02 implementation
- `packages/web/src/client/TeamAction.tsx` now derives the current mission from `missionsResult.value.at(-1) ?? null` and renders only mission detail plus the existing roster/work surface.
- Rendered plan approval, mission selector/list/create/approve/task-summary, shared task list, task forms, and task mutation controls were removed; injected Remote/backend contracts remain intact.
- `packages/web/tests/team-action.client.spec.tsx` now covers zero/one/multiple missions, latest-created selection, removed-control absence, roster/work/review navigation, polling, and stale-session guards.
- `verification/web/gat-agent-team-panel.e2e.ts` and `verification/web/task.expected.md` now assert the simplified assembled browser surface.

## STEP-03 verification
- Standalone project test/build attempts failed because this distribution checkout intentionally references DSH-root configs that do not exist here; verification was rerun in `/home/hoinv/deepseek-harness` after syncing the affected plugin source/test artifacts.
- Initial focused run exposed three test-only assertion/timer issues; they were corrected and rerun.
- Independent final review identified ambiguous mission-list failure behavior. Fixed by gating the mission section on successful mission retrieval, clearing stale mission state on failure, preserving members plus the explicit error, and adding regression coverage.
- Final focused DSH web tests: 21/21 passed (`team-action.client.spec.tsx` + `browser-plugin.client.spec.ts`).
- Installed GAT web bundle: passed via `pnpm --dir packages/experimental/gat-web run bundle`.
- Focused assembled browser E2E: passed for “loads the current mission and members without task controls” after the review fix.
- Full assembled E2E file retains one unrelated pre-existing overlay mismatch (`simpleMode` / `teamMembersMaxBytes`), outside this task’s UI scope.
- Live URL `http://127.0.0.1:3080/` loaded in a fresh browser, but without an authenticated/connected conversation it exposed no `[data-team-action]`; assembled E2E provides the functional browser evidence. The existing server has no `pnpm run dev:web` watcher, so an open page requires refresh to load the rebuilt plugin bundle.

## Final Capture Sweep
- Reviewed the focused diffs, teammate findings, test failures/fixes, and verification artifacts.
- One reusable HUMAN-confirmed product decision was captured as CAP-001; no additional non-obvious reusable knowledge or AIWS system issue met the capture threshold.
- CAP-001 is deferred to the project capture backlog for later HUMAN curation; no relation candidates remain.

## Notes
- HUMAN selected “Xác nhận, triển khai” in the Gate U1 confirmation prompt.
- Teammates performed independent source-map, test-map, implementation, test, E2E, and final-review assignments.
