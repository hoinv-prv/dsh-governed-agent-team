# GAT Conservative MVP — Conformance Contract Matrix

## Binding and status

- Mission: `multi-mission-web-ui`
- WBS: revision 31, SHA-256 `872248ffc2b352e869535a6a12d0145c4c69cea9b4cd35e5e5c0f92bbc58c78d`
- Vector baseline: `docs/conformance/gat-conservative-mvp-v1.json`, accepted hash recorded by the mission as `2250aa8bd50e08efd4e4e876e8d9ac4309d3aea8c1af424de04a817aa507b87c`
- Machine-readable contract: `conformance-contract-matrix.json`
- Status: static design contract only. The accepted baseline was read as data and was **not dispatched or executed**.

## Trust boundary

A later runner must split each vector before dispatch:

1. Setup code may receive setup fixtures only.
2. A closed handler receives exactly `{ id, operation }`.
3. The handler invokes the matrix-named current API or the exact planned control API and appends raw observations.
4. A named reducer and symbolic predicate derive actual disposition/reason/result from those observations.
5. A named absence probe and evidence producer resolve every token listed for the vector.
6. Only the terminal comparator may receive `expected`, `required_absence`, or `required_evidence`.

Fixtures and handler inputs must recursively reject truth/assertion/binding/evidence/counter fields. The matrix names components but does not implement or certify them.

## Coverage summary

The matrix contains exactly 51 unique vector mappings and preserves every vector's exact operation name, absence tokens, and evidence tokens. There are no wildcard/generic handlers, reducers, predicates, probes, producers, or APIs.

| API status | Vector coverage | Meaning |
|---|---:|---|
| Current package API | 44 | A concrete exported/current class method or function exists in accepted governance, policy, adapter, or memory source. |
| Planned control API | 7 | The accepted source lacks the required transition; downstream control-state work must implement the exact named API before handlers are eligible. |

### Explicit planned control gaps

| Vector(s) | Required API | Required state contract |
|---|---|---|
| `GAT-WS-001`, `GAT-EXEC-002` | `control.ControlState.bindWorkspace` | Write-once Workspace binding; conflict retains the original pointer. |
| `GAT-EXEC-001` | `control.ControlState.replanExecution` | Re-plan preserves Task/AIP/Workspace identity and records the transition. |
| `GAT-EXEC-003` | `control.ControlState.supersedeTask` | Supersession creates distinct Task/Workspace identity and retains provenance. |
| `GAT-ACT-001` | `control.ControlState.evaluateActivation` | Missing/stale/incomplete or non-HUMAN manifest leaves implementation inactive. |
| `GAT-PROMO-001` | `control.ControlState.evaluatePromotion` | Promotion/copy routes are explicitly denied with zero source/target mutation. |
| `GAT-DEGRADE-001` | `control.ControlState.evaluateOptionalMemory` | Optional reference-memory outage degrades explicitly; required security outage fails closed. |

`GAT-RETENTION-001` primarily targets current `memory.PartitionStore.create` validation and additionally declares `control.ControlState.evaluateActivation` as a prerequisite for its activation case.

## Current API families

- Governance: `authorizeTeamPlan`, `authorizeMissionMapping`, `evaluateReadiness`, `checkExecutionIdentity`, and `deriveAgentDeskId`.
- Authorization/admission: `DenyFirstPolicy.authorize`, `GatMemoryAdapter.invoke`, and `GatMemoryAdapter.visibleTools`.
- Partitioned memory: `physicalPartitionKey`; `PartitionStore` create/revise/tombstone/get/search/auditRead and denial/lifecycle/audit/transaction/backup/recovery operations.

Composite vectors name a primary observable API and may name an additional prerequisite. This is an execution contract, not permission to alter accepted dependencies.

## Downstream gate

Before control or runner source mutation, an independent reviewer must confirm:

- exact 51-ID equality with the accepted vector baseline;
- exact operation, absence-token, and evidence-token equality;
- every current API resolves to accepted source and every missing operation is an explicit planned control API;
- handler projection excludes all expected/absence/evidence declarations;
- the focused static test passes without baseline dispatch.

Passing the static test does not establish vector conformance, DSH integration, MCP integration, activation, or production readiness.
