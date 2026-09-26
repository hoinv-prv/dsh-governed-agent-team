# Final Output

## Status
final

## Content
Implemented session-scoped Agent Team exclusivity in `packages/tools/src/index.ts`:
- Solo sessions may continue using ordinary delegation tools.
- Once Agent Team is enabled, `subagent`, `subagent_fork`, `workflow`, and `ralph` are denied before execution.
- Denial guidance requires HUMAN approval, then `spawn_teammate`, then task assignment when a capability is missing.
- Governed teammate spawning remains available through the existing Team approval/readiness/cap path.

Regression coverage was added in `packages/tools/tests/tool-team.spec.ts` and `packages/profile/tests/profile.spec.ts`. Verification evidence is recorded in `04_findings.md`.
