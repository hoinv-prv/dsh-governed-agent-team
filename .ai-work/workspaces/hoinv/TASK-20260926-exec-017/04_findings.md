# Findings

## Findings List
- ...

## Confirmed Findings
- Gate U1: HUMAN requires session-scoped exclusivity whenever Agent Team is enabled: no ordinary fresh/fork sub-agent may be spawned outside the team.
- Capability-gap flow is HUMAN-controlled: request approval, add the approved member to the current team, then assign the task to that member.
- HUMAN confirmed this task does not require building an implementation team; the main session executes directly.

## Inferred Findings
- The narrow model-facing enforcement point is the per-Agent `scoped.tools.guard` in `packages/tools/src/index.ts`; it sees both Lead and teammate tool calls and runs before registered tool execution.
- `TeamView.enabled` is false until the durable roster has a teammate and true afterward, so the guard can preserve solo-session delegation and switch to Team-exclusive delegation without a global provider toggle.
- `spawn_teammate` is a distinct governed tool backed by `TeamService.spawnTeammate`/`TeamRoster.spawn`; it remains allowed through its existing approval/readiness/cap checks while external `subagent`, `subagent_fork`, `workflow`, and `ralph` paths are denied.
- The denial and Team policy provide the capability-gap sequence required by HUMAN: ask approval, create the approved member, then assign the task.
- Pre-start AIP lint had 0 errors and one advisory warning (`step_inputs_unresolvable` for STEP-02).
- A direct standalone Vitest invocation cannot resolve the copied-package tsconfig layout; canonical verification must run against an installed DSH worktree.

## To-Verify Findings
- ...

## Notes
- Implementation changed `packages/tools/src/index.ts`: added the external-delegation tool set, session-enabled guard, explicit HUMAN approval/member-add policy, and capability-gap guidance on `spawn_teammate`.
- Regression coverage changed `packages/tools/tests/tool-team.spec.ts` and `packages/profile/tests/profile.spec.ts`.
- No global provider was disabled; `spawn_teammate` continues through the governed Team roster path.
- Latest installed-worktree focused suite passed: 9 files / 143 tests, including 25 GAT tool tests and the profile integration covering real solo `subagent`/`subagent_fork` allowance plus enabled-Team denial.
- Canonical verifier initially exposed a pre-existing built Remote smoke mismatch (`remoteEnable` exported but missing from expected descriptors); `packages/core/tests/built-lib.e2e.ts` was aligned and full verification rerun.
- Final Capture Sweep reviewed implementation diffs, tests, and verifier evidence: 0 additional candidates; 2 total candidates were deferred with destinations (`BL-017-CAP-001`, `BL-017-CAP-002`); no pending relation candidates.
- Canonical verification evidence: installer lifecycle passed; 9 focused files / 143 tests passed; full Host/Client build passed; built-library smoke passed (1/1). The final Web dashboard smoke had 2/3 tests pass and one unrelated 30-second timeout waiting for the pre-existing `Mission detail` heading.
- Scoped AIWS finalize lint: 0 errors, 1 reviewed advisory warning (`step_inputs_unresolvable` in STEP-02); lint also noted fallback to repository dirt because AIP bullets do not begin with path tokens.
