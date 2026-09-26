# Review candidate multi-mission-web-ui, revision 16

- Exact plan SHA-256: `a9a8a95d9ccc22662b33d331edf7da37175cd49f18a9eeda2fe96675f7ba1247`
- Canonical validate/order/hash: PASS.
- Base: approved revision 15, exact hash `a6eb5baedafabb7098016fc45a7656421847cc5fea462a076a3568de66ed290b`.

## Trigger

Revision-15 `governance-replan` attempt 1 correctly reconciled ownership/history and updated the AIP, but its declared lint verification exited 2 because newly appended STEP-05 through STEP-11 used compact prose instead of the mandatory seven-field AIP step schema. Runtime status exited 0. No product work was dispatched.

Evidence: `evidence/governance-replan/attempt-gat-govreplan-001/verification.md`.

## Exact delta

- Preserve cumulative charge 18, including failed `attempt-gat-govreplan-001`; do not retry it under revision 15.
- Increase only `governance-replan.max_attempts` from 1 to 2.
- The retry repairs STEP-05 through STEP-11 to include `Objective`, `Recommended Mode`, `Applicable Guidelines`, `Inputs`, `Expected Outputs`, `Done Condition`, and `Notes / Constraints`, then runs the same exact lint/status verification.
- No product task, scope, command, dependency, effect, acceptance, threat gate, package design, or conformance boundary changes.
- Cumulative cap increases from 36 to 37 attempts and 4,355 to 4,400 effort minutes: prior 18/1,325 plus at most 19/3,075 remaining.

All revision-15 PASS findings continue to apply. Revision 16 requires a new exact HUMAN approval because it authorizes one additional charged governance repair attempt. Coding remains blocked behind successful reconciliation and later HUMAN threat/vector acceptance.
