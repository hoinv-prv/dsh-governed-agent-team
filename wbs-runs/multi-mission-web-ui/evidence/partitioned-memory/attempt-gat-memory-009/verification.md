# Partitioned memory — attempt-gat-memory-009 verification

Exact command:

```text
node --test packages/gat/tests/partition-store.test.mjs packages/gat/tests/transaction-audit.test.mjs packages/gat/tests/lifecycle-privacy.test.mjs
```

Result: PASS — 14 tests, 0 failures, exit 0.

Attempt-8 reviewer residual corrections:

1. GENESIS `bindingHash` is now derived only from tenant id and audit epoch. A cross-store test proves byte-identical GENESIS for different first-caller principal/project/owner scopes in the same tenant/epoch.
2. Stored active content is physically wrapped exactly once in `<GAT_REFERENCE trust="untrusted"> ... </GAT_REFERENCE>`; create/get/search therefore never return undelimited raw content. Revision recognizes and unwraps the prior envelope before re-wrapping, preventing nested envelopes. Tombstones store empty content.
3. Recursive pre-validation scans every string in the proposed MemoryRecord. Credential/prohibited-personal patterns deny before persistence; email is redacted across content, title, tags, origin and source refs before validation/persistence/hash. Tests cover non-content secret/PII denial and cross-field email redaction.

All attempt-8 closed mechanics remain tested: reference-only authority; exact provenance cardinality; audited four-class denials with zero raw payload; five-field audit.read; every-operation suffix result/idempotency; crash/purge/restore.

SHA-256 outputs:

- source: `6531e5fc8644372ac0f8ab43124076cc39cd50dd1e49a2c5142b00ff2c337bf0`
- declarations: `6c45daf5171e62cca506ff76d46518209b9484a44a0303f34137100e7562f8a6`
- partition tests: `dd9d5a377e92b40ff29be9f9fe7ae1197a1f90b066a0d5d4fd58d75a92a55ca9`
- transaction/audit tests: `7682f23500b77dc89b70d2065812e5acc9113ed30f5378f420431c75c3e1582d`
- lifecycle/privacy tests: `513f0b3bf68bdc1ded40653c144627b804724d6df1070a884b2c6b1ca03852eb`

No package-manager, network, dependency, accepted conformance vector, DSH, activation, or live-Web command ran.
