# P0 contract-plan prototype design notes

## Binding

- Mission revision: `durable-agent-p0-task-contract-plan-poc` revision 6
- Plan SHA-256: `1fce7d02edf2916b52463516e87e2c10a91fc9ad44eacd7f3e014315db49a6c2`
- Task/attempt: `p0_prototype_rebind` / `p0_prototype_rebind-a01-r6`
- Public seam: `validateAndNormalize(taskContract, planProposal)`

## Design

The module is a deterministic data-only validator and normalizer. Its sole static dependency is exact `node:crypto` for SHA-256. It performs no file, network, model, WBS, shell, clock, random, or product operation.

Validation proceeds fail-closed through execution identity, required TaskContract fields, opaque-origin restrictions, finite retry-policy normalization, proposal shape and identity binding, step count/type/ID/order/terminal-handoff rules, replan snapshot binding, and per-step authority/retry checks. Missing execution identity blocks at assignment with no handoff; later failures are planning blocks carrying the already-bound contract handoff metadata.

File steps remain bound to an allowed path/operation and command steps to an exact command declaration. Verify steps instead bind the exact verification ID, require a read effect, and require that effect path to equal the verification declaration's target. They do not require a second `authority.allowed_paths` read grant for the already-declared verification target. Handoff remains limited to `handoff_commit`.

Accepted plans copy only the closed oracle field set. Initial plans use revision 1 and no parent. Replans bind the exact supplied parent snapshot and increment the revision once. Before plan construction, every snapshot completed entry must be an object with exactly `id`, `order`, `result_hash`, and `step_body`; its ID/order must equal the bound step body's ID/order, parent completed history must deep-equal the snapshot, and exactly one proposal step with that ID must deep-equal the bound body. Any mismatch returns `COMPLETED_HISTORY_MUTATION`. Contract authority, verification, ceilings, handoff metadata, complete normalized retry policy, and the host-supplied deterministic proposal remain data; no step is executed.

Canonical bytes recursively sort object keys and preserve array order. The plan hash is lowercase SHA-256 over the UTF-8 canonical bytes.

## Boundaries and residual risk

This PoC is designed only for the immutable P0 fixture corpus. It is not a production schema validator, JavaScript sandbox, runtime attempt ledger, effect executor, persistence proof, or authorization layer. Runtime debit durability, crash recovery, concurrency, and terminal transitions remain deferred. Independent source review remains required even when the authorized syntax and oracle commands pass.
