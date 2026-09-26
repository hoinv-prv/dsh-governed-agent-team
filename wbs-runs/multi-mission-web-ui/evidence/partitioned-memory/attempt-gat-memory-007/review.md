# Partitioned memory review — changes required

Independent review confirms raw-zero/HMAC GENESIS, sequence high-water, durable-effect crash recovery, purge and tombstone replay mechanics are substantially closed, but finds five material contract inversions:

1. Every MemoryRecord must be `authority: reference_only` while retaining explicitly untrusted/delimited content; implementation/tests currently require `authoritative` and reject reference content.
2. `direct_note` requires exactly empty source_refs; derived origins require nonempty references.
3. Classification/schema denials happen before the audited transaction and therefore lack required primary/emergency denial evidence.
4. Tenant/epoch GENESIS leaks first-caller scope metadata and `auditRead` authority omits scopeKind/scopeOwnerKey binding.
5. Suffix replay restores idempotency only for mutations, not get/search/audit/denial results.

Attempt 7 fails independent review. The v23 task allowance is exhausted; further work requires a reviewed immutable WBS revision.
