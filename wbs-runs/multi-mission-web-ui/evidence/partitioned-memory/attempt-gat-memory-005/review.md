# Partitioned memory review — changes required

Independent review confirms purge/manifest recovery and old-backup purge reconciliation pass, but finds final material residuals:

1. GENESIS hashing omits the mandatory 32 zero prior bytes; signature is unauthenticated; audit partition/high-water lacks normative tenant+epoch sequence tuple.
2. Crash after anchor CAS but before journal state update rolls back against an advanced anchor; recovery must inspect external high-water. Other before-state durable-side-effect boundaries need the same treatment.
3. Decision events need authoritative IDs/revisions, decision/correlation, Task/AIP/Workspace/Team/Mission, matched rules, outcome, and timestamp—not only opaque hashes.
4. Canonical `direct_note` with empty source_refs must be allowed; deterministic credential/prohibited-content reject or redact-allow with redaction revision and stronger authority/provenance validation are missing.
5. Restore must replay anchored non-purge domain/idempotency changes, especially tombstones/revisions, rather than append only audit events and leave stale active state.

Attempt 5 fails review. The task allowance is exhausted; a reviewed WBS revision and revised hypothesis are required.
