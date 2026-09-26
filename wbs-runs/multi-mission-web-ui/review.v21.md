# Review candidate multi-mission-web-ui, revision 21

- SHA-256: `113c041b61324d124cf36429d25852cbf6e78ee923548a87faf1609d0e857a03`
- Base: HUMAN-approved revision 20 `239f40e8c4fa8cbba7bf919e8af10e249eb4dbe627bbc06ec207a6f12e15289c`
- Trigger: direct HUMAN instruction, “Tôi nâng budget lên 50 attempts. Hãy tiếp tục.”
- Validate/order/hash: PASS; canonical order unchanged.

## Exact budget delta

Current charge remains 31. Revision 21 raises the cumulative ceiling 43→50 and allocates the seven added attempts to remaining technical risk:

- `partitioned-memory`: max 3→5 (+2 × 240 minutes)
- `policy-selector`: 2→3 (+1 × 180)
- `wrapper-admission`: 2→3 (+1 × 180)
- `conformance-runner`: 2→3 (+1 × 180)
- `standalone-integration`: 2→3 (+1 × 120)
- `implementation-freeze`: 1→2 (+1 × 90)

`governance-replan` remains max 6 and supplies the still-unspent selection/reconciliation attempt. Threat/scaffold/governance accepted task caps remain unchanged.

Arithmetic: current 31 + remaining 19 = 50. Potential effort ceiling 4,940 + 1,230 = 6,170 minutes. Attempt ceilings are not targets; retries still require a demonstrated failure and revised hypothesis.

The first candidate accidentally migrated the memory evidence Workspace path; after independent review it was restored to exact v20. No task scope, cleanup, command, dependency, review/HUMAN gate, DSH/network/dependency/accepted-conformance boundary, or Workspace path changes from v20. Exact HUMAN approval of this immutable allocation/hash is required before selection.
