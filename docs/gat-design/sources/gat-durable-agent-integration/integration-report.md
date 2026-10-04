# Durable Agent capability — integration verification

## Verification identity

- Mission: `gat-durable-agent-integration`
- Approved WBS: revision 2, SHA-256 `ddabe11b55fe9a012f25bdffb3109952d1a8b057da158a14ebea9631a6467457`
- Integrated attempt: `integration_verify-a03`
- Current attempt inputs are recorded in `evidence/integration_verify/integration_verify-a03/input-hashes.json`.
- Historical `integration_verify-a01` is retained as failed evidence: the full suite exposed three stale retained-compatibility expectations. Attempt a02 changed only `tests/members.spec.ts` to assert the already accepted immutable-generation authority, write-before-bootstrap rule, and non-destructive legacy retention, but its first verification still found one passing-control write ordered after bootstrap; a02 is also retained failed. Attempt a03 verified the final settled fixture. No product implementation changed in these retries.

## Exact integrated verification

All commands ran successfully against the same settled source/test/package bytes:

| Command | Result |
|---|---|
| `pnpm exec vitest run` | PASS — 10 files, 127/127 tests |
| `pnpm run build` | PASS |
| `pnpm run check:named-exports` | PASS |
| `pnpm run smoke:packed-profile-v3` | PASS |

The suite includes service contracts, standalone compatibility, local provider behavior, raw memory lifecycle/recovery oracles, Consumer/model composition, legacy members compatibility, domain contracts, and the pre-existing MVP execution/store tests. Exact machine-readable results and hashes are in `evidence/integration_verify/integration_verify-a03/verification.json`.

## Requirement-to-accepted-evidence map

| Requirement | Current capability and terminal accepted evidence |
|---|---|
| `service_port` | Versioned Cordis `DurableAgentService`, feature declaration, bounded DTOs, typed errors, opaque refs: `service_contract-a02` verification/review. |
| `identity_authority` | Workspace/global declaration validation, opaque generation-bound references, scope isolation, profile conflict/release rejection: `service_contract-a02`, `local_provider-a04`, and current full suite. |
| `task_context` | Frozen path-free task snapshots, selective memory catalog/read, deterministic revision behavior: `service_contract-a02`, `local_provider-a04`, `scoped_consumer-a02`. |
| `provider_persistence` | Local filesystem provider, immutable content objects/manifests, atomic current pointer, bootstrap/recovery and restart behavior: `local_provider-a04`, `memory_protocol_qualification-a02`, `memory_lifecycle-a02`. |
| `memory_governance` | Unconfirmed/non-canonical candidates separated from authorization-bearing confirmed commits; bounded fail-closed recovery and independent raw oracle: `memory_protocol_qualification-a02`, `memory_lifecycle-a02`. |
| `lifecycle` | Mutation serialization, release admission close/drain/ref invalidation, reprovision persistence, stale/foreign/scope-mismatch denial: `local_provider-a04`, `memory_lifecycle-a02`. |
| `member_consumer` | One explicitly bound opaque ref, deterministic metadata-only model contribution, exact tool/result contract, two-member isolation, real `apply → service → provision → bind → snapshot` composition: `scoped_consumer-a02`. |
| `compatibility_docs` | Explicit legacy adapter with workspace default only at the adapter boundary; package exports/declarations and docs for the actual API, persistence, migration, release and Consumer; private layout is not public contract: `standalone_adapter-a01`, `package_docs-a02`. |
| `mission_evidence` | Append-preserved attempts/charges, terminal acceptance objects, independent reviews, exact hashes, failed-attempt triage, and this integrated full-suite/build/export/smoke result. |

Terminal acceptance references are authoritative in `execution.json`. The accepted attempts are:

- `service_contract-a02`
- `standalone_adapter-a01`
- `local_provider-a04`
- `memory_protocol_qualification-a02`
- `memory_lifecycle-a02`
- `scoped_consumer-a02`
- `package_docs-a02`

Each attempt's verification and review files live under `evidence/<task>/<attempt>/` and are referenced by its terminal acceptance object.

## Current exact file hashes

These are current integrated bytes, not stale predecessor snapshots:

| File | SHA-256 |
|---|---|
| `durable-agent-plugin/src/service.ts` | `f54e4954ad7a4b085fdb8c6dcc600c28832ce16cb5174c1985ab35085c9ed833` |
| `durable-agent-plugin/src/errors.ts` | `10f1dbe70be6c762894ecb8947debdfa0246207effe01366e4e998fc9601c43f` |
| `durable-agent-plugin/src/standalone-adapter.ts` | `6181154388782419e258a491d6d256ff1850cd973733728351c5d3dc73de2788` |
| `durable-agent-plugin/src/local-provider.ts` | `75e63d7d634d5afe7b162dd4e3758103a733ac7eff1f9481b1115fd72c6ca58a` |
| `durable-agent-plugin/src/members.ts` | `6d5f39891f1436d53b9e34dd3a57757d20798bcde0143317a1b453f142383f5d` |
| `durable-agent-plugin/src/consumer.ts` | `1ca3189ba0f50896f2fd17685c9c26876a5e4bfae2ac7fd59c50e3e7b2712af4` |
| `durable-agent-plugin/src/index.ts` | `acba47f39e746bb055908d13410b7d731f90b6ef058ca03372b9e507964d57da` |
| `durable-agent-plugin/src/client.ts` | `2318befba503e5d817475ec96abe575394bc4f0cc371ff78521a40ec00584e9f` |
| `durable-agent-plugin/src/mvp/execution.ts` | `7761d4f8da8777c632215fc0fac66141b9273114ff022c4c562cf0250a66f41e` |
| `durable-agent-plugin/src/mvp/store.ts` | `e2459fe00a178fd427d9954cbbab2295cb92241359f33d44ea6562cfdc4464e9` |
| `durable-agent-plugin/tests/members.spec.ts` | `7af123d9ee9751d0f1da859dff61f9c010d01ea0bf1bb61d0c23b99838a9f251` |
| `durable-agent-plugin/package.json` | `098539552a89b3f4018db71e5b3138489daa9a3e8550c3b9ec9f9e10b7069a6b` |
| `durable-agent-plugin/README.md` | `bb6efbb9d1ca50cf9bfb0267eddc72eeb59dcb05694ca74e6bb197f0d4688126` |
| `durable-agent-plugin/docs/service.md` | `c9fae74bd0d75e97f8fc37fa1e4b226b7b015798277f68c3ede6a3fb247c2949` |
| `wbs-runs/gat-durable-agent-integration/memory-protocol-qualification.md` | `6c56960561e1b74c7c9bb007d1cad5f3267073899df536cc11b697d1c905868a` |

### Downstream lineage reconciliation

Accepted predecessor hashes are historical evidence, not a claim that later tasks cannot update the same output. `memory_lifecycle-a02` established the accepted protocol and behavior. `package_docs-a02` later applied reviewed, behavior-preserving strict TypeScript narrowing to `local-provider.ts` and `members.ts` so the declared package build could generate declarations; it also corrected baseline MVP narrowing. `integration_verify-a02` reconciled the stale compatibility test expectations and `integration_verify-a03` verified the final settled fixture. The current hashes above are bound to the integrated command result, while every earlier hash and attempt remains preserved.

## Persistence, migration, recovery, composition

- Bootstrap uses an immutable mode anchor plus immutable content objects and generation manifests, with atomic current-pointer publication.
- Pointer loss/corruption and parent-chain corruption fail closed under bounded validation; the independent raw oracle covers bootstrap and mutation fault boundaries, recovery, release, concurrency, and FIFO end-state behavior.
- Legacy profile and `MEMORY.md` input migrate compatibly and non-destructively. Once bootstrap commits the discriminator, retained flat writers cannot mutate canonical memory and return approval-required; direct changes to legacy flat files are non-authoritative.
- Candidates remain unconfirmed and non-canonical until an authorized confirmed commit publishes a canonical generation.
- Consumer composition was exercised through the real plugin registration/service instance and emits only governed, deterministic, path-free model context.

## Dependency and ownership scan

A source-import scan found no TypeScript import/dynamic-import path containing `gat`, and `package.json` contains no GAT dependency. The package depends only on Cordis and YAML at runtime. No GAT type, binder, Team controller, Session controller, implicit global discovery, or path-level integration API was added.

## Explicitly deferred scope and residual risks

The Durable Agent capability and its standalone compatibility adapter are complete for this workspace mission. The separate GAT-owned binder that maps GAT Agent Session/Team lifecycle into `provision → bind → inject → release` remains deliberately outside scope and unimplemented here.

Residual risks/limits:

1. The filesystem generation layout is provider-private implementation detail; hosts must integrate through the service/adapter APIs.
2. `workingLocation` is a trusted opaque capability; hosts must not infer adjacent provider layout.
3. Serialization guarantees cover participating provider/compatibility processes using the mutation lease; arbitrary external writers are outside the protocol.
4. Human or authorized-host policy remains responsible for approving a candidate before confirmed commit.
5. Package publication and the GAT binder adoption step are not part of this mission.
