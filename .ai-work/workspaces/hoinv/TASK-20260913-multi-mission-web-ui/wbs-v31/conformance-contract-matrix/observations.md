# Attempt observations — conformance contract matrix

- Task: `conformance-contract-matrix`
- Attempt: `attempt-gat-contract-matrix-001`
- Plan: WBS revision 31, SHA-256 `872248ffc2b352e869535a6a12d0145c4c69cea9b4cd35e5e5c0f92bbc58c78d`
- Input hashes: preserved in `execution.json#task_attempts_v31`; worker did not modify mission controls.
- Baseline handling: parsed/read only as static contract data; no vector was dispatched or executed.

## Design observations

1. The baseline contains 51 unique IDs.
2. Forty-four vectors have a named primary current governance, policy, adapter, or memory API.
3. Seven vectors require an explicit planned control API: Workspace write-once binding, execution re-plan, Task supersession, activation denial, promotion denial, and optional-memory degradation.
4. `GAT-RETENTION-001` targets current record validation and also requires the planned activation gate for its activation case.
5. Each mapping names a closed handler, reducer, symbolic predicate, absence probe, and evidence producer. Exact required absence/evidence tokens remain static comparator contracts and are not included in the handler projection.

## Outputs

- `wbs-runs/multi-mission-web-ui/conformance-contract-matrix.json`
- `wbs-runs/multi-mission-web-ui/conformance-contract-matrix.md`
- `packages/gat/tests/conformance-contract-matrix.test.mjs`

## Verification

Pending the single authorized command: `node --test packages/gat/tests/conformance-contract-matrix.test.mjs` from repository root with timeout 120000 ms.

## Risks / downstream obligations

- Planned control APIs are contracts, not implemented operations; downstream control-state work must implement and independently review them before handler work.
- Named handlers/reducers/probes/producers are likewise contracts for the next task, not current executable conformance.
- No claim of accepted-baseline conformance, DSH/MCP integration, or activation is made.
