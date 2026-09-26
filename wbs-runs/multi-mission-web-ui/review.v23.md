# Review candidate multi-mission-web-ui, revision 23

- SHA-256: `c919b6efd5c4792eb32ef9ee8b06d98da00c042d03e9d0c89c52af388e3f70bb`
- Base: approved/selected revision 22 `f6d7e37d882c96982feea06e766b26c5a4b0d29aca05bf119ebfa007f8be7c8a`
- Validate/order/hash: PASS; order and all commands/paths unchanged.

## Trigger and bounded reallocation

Partitioned-memory attempt 5 passed 10/10 tests and closed purge recovery but failed independent review on five protocol/privacy/restart residuals; its task cap is exhausted. Revision 23 preserves all 37 charges and adds two final memory attempts plus one selection reconciliation while keeping the HUMAN-set total at 50:

- governance-replan 7→8 (+45 min)
- partitioned-memory 5→7 (+480)
- wrapper-admission 3→2 (−180)
- conformance-runner 3→2 (−180)
- standalone-integration 3→2 (−120)

Current 37 + remaining 13 = 50. Effort ceiling changes 6,125→6,170 minutes. Policy remains 3; freeze remains 1.

The memory delta is limited to: exact GENESIS zero-prior/authenticated signature and `(tenant,audit_epoch)` sequence high-water; full authoritative decision-reproduction fields; external-state inspection at before-state durable crash boundaries; canonical direct-note/source-ref behavior and exact GAT-CLASS-001 outcomes—credentials and prohibited personal data each deny/ACTION_NOT_ALLOWED with zero raw persistence, while only deterministically redactable data allow/null with redacted-only persistence bound to classification-policy hash and redaction revision; anchored non-purge domain/idempotency suffix replay. Existing successful purge/restore behavior must regress cleanly.

No scope/path/command/dependency/review gate or DSH/network/dependency/accepted-conformance boundary changes. Exact HUMAN approval is required before selection.
