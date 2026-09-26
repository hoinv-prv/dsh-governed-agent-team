# Partitioned memory — attempt-gat-memory-008 verification

Exact command:

```text
node --test packages/gat/tests/partition-store.test.mjs packages/gat/tests/transaction-audit.test.mjs packages/gat/tests/lifecycle-privacy.test.mjs
```

Result: PASS — 13 tests, 0 failures, exit 0.

Pinned v24 residual coverage:

1. All accepted records require `authority.mode=reference_only`, retain their content, and expose explicit `contentTrust=untrusted_reference` plus `<GAT_REFERENCE>` delimiters.
2. `direct_note` requires exactly zero source refs; derived origins require at least one complete ref.
3. GAT-CLASS-001/schema failures append denial audit evidence before returning the normalized rejection, while raw secret content is absent from audit history.
4. GENESIS is tenant/epoch neutral with no first-caller principal/project/owner scope; `audit.read` authority matches tenant, principal, project scope, scope kind, and owner key.
5. Audit-sink domain effects now preserve every operation's result. Old-backup suffix recovery replays get/search/audit/denial results and their idempotency without repeating backend work.

SHA-256 outputs:

- `packages/gat/src/memory/index.mjs`: `0cb28eea8cbec3d4fef81b6669561ead354e0261f0b2b177fb9f944d4b7c86c8`
- `packages/gat/types/memory/index.d.ts`: `6c45daf5171e62cca506ff76d46518209b9484a44a0303f34137100e7562f8a6`
- `packages/gat/tests/partition-store.test.mjs`: `2f5d19547ae01191165156d8393019dc3171739bc42f3887f899dadbd9af1953`
- `packages/gat/tests/transaction-audit.test.mjs`: `8672581f1aed42ccffc98d46d0bef522a22d15434f3722e5411786119a9feb04`
- `packages/gat/tests/lifecycle-privacy.test.mjs`: `513f0b3bf68bdc1ded40653c144627b804724d6df1070a884b2c6b1ca03852eb`

No package-manager, network, dependency, accepted conformance vector, DSH, activation, or live-Web command ran.
