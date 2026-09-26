# WBS revision 2 review — legacy-agent-team-hotfix

- Exact plan: `wbs.v2.json`
- SHA-256: `733c8ae628f1076b49499b4bb10017fd9b8cde0013071bf89067636d0683f5d5`
- Validation/order: PASS.
- Status: candidate, not approved.

## Why revision 2 is required

Revision 1 authorized two Lead-only implementation attempts. Both are charged:

1. Attempt 1 changed validation/readiness/prompt behavior but left the schema default at `2`. Coordinator inspection rejected the otherwise positive review.
2. Attempt 2 changed the schema default to `0` and made the focused test exercise omitted config. Independent recovery review found the runtime `apply` fallback still uses `config.minExecutionMembers ?? 2`.

A further mutation would be a new attempt. Revision 2 therefore adds exactly one Lead-only recovery attempt, raises the cumulative mission ceiling from 8 to 9 attempts and 600 to 630 minutes, and preserves every other scope, effect, requirement, dependency, command, review gate, and non-goal.

## Recovery hypothesis

Change the runtime fallback to zero and independently inspect all three default layers together:
- schema `default(0)`;
- `apply` fallback `?? 0`;
- focused test omits `minExecutionMembers` and observes required count zero.

The exact plan-approval gate, configured positive minima, validation, and maximum teammate cap remain unchanged. Runtime execution remains deferred to canonical integration verification.

## Preserved history

- Governance attempt 1 remains accepted.
- Lead-only attempts 1 and 2 remain charged and failed for distinct findings.
- No approved-plan-import or integration attempt has started.
- No mutation under `packages/gat` or `wbs-runs/multi-mission-web-ui` is authorized.

Approval of revision 2 authorizes attempt 3 and the unchanged downstream plan; it does not accept current product bytes or pre-accept verification.
