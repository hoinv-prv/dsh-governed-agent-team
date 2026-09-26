# Standalone integration evidence — WBS v26 attempt 49

Status: verification passed; independent review pending.

## Exact verification

1. Combined source suite command from WBS: 32 tests passed, 0 failed, exit 0.
2. `node packages/gat/scripts/build.mjs`: exit 0.
3. `node --test packages/gat/tests/built-package.test.mjs`: 1 passed, 0 failed, exit 0; clean child process with empty environment imported root plus governance, memory, policy, adapter and conformance built modules.
4. A second build produced the same seven `lib/**/*.mjs` SHA-256 values, proving byte determinism.

No accepted vector baseline was executed. The conformance-runner tests used only three synthetic `SYN-*` fixtures and injected in-memory I/O/dispatcher surfaces.

## Security and architecture closure

- Policy: one transactional admission bundle commits allow audit plus selector together or neither. Slow/throwing preparation returns generic denial with terminal `SECURITY_SERVICE_UNAVAILABLE` emergency evidence and zero committed selector. Exact signed selector binds classification, resource/action, correlation/decision/time, Team/Mission/account/workspace/readiness/membership/capability evidence.
- Wrapper: visible schema contains only GAT wrapper names. Raw MCP prefix and Agent-supplied identity/selector/capability fields deny before PDP/MCP/backend. MCP capability is package-private. Allowed output is a provenance-labelled untrusted reference object, never interpolated as trusted instructions.
- Runner: exact `--vectors`/`--evidence` parsing, literal path reporting, unique every-vector dispatch, complete raw binding schema, raw stdout/stderr, nonzero fail-closed output, and synthetic-only tests. Accepted baseline remains unexecuted.
- Package: Node ESM and built-ins only, zero dependency/install/network requirement; DSH runtime and MCP bridge remain explicitly not integrated.

## Output hashes

- policy source `378586ef9a6cbebe2e09f7064f33500a95bee7d5352569c93f6cc63e6aa34750`
- adapter source `9b61327ba923beecbf425611c175dc0026a33cc165fc3735d28bcf7a1067d289`
- conformance source `40fb2aa437db5e0cef73c7bb67a27b02b1949078abf1a888c213fab218c3b2f5`
- conformance CLI `e2329159b4cbe4f1f11b6072becc1a56d3cabb6081083682e4163c1612d0d04b`
- policy test `13fde6360e48f62e3e5a2cc95255c97cbe9bb77e304308d745a8449855f5cc77`
- wrapper test `915b82c60bda281717fb2048e43b7e9e7f25fc29ed7d6976e3ffb334293ef264`
- runner test `090dbe55d652897d39f790cddac049b5b7b74d3a06af74754c80060da2dec946`
- built smoke `cd577d072d9206e338c2449cf81d4da514196f2bc5c66ddd77317e346175702c`

The built library hashes equal their source-module hashes for every copied module.

## Persistent exclusions

No npm/pnpm, network, external dependencies/store, DSH access/install/build/runtime, live Web, accepted-baseline conformance, activation, proposal approval or AIP close occurred in this attempt.
