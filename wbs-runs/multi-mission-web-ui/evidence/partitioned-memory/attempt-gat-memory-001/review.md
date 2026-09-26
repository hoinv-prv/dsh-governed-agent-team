# Partitioned memory review — changes required

Independent review found material redesign requirements:

1. Verification command/path drift: WBS authorizes one exact Node command for `partition-store.test.mjs`, `transaction-audit.test.mjs`, and `lifecycle-privacy.test.mjs`; attempt ran three separate commands including two wrong filenames.
2. Physical key must be `(tenant, principal, project_scope, scope_kind, scope_owner_key)`; full record schema, expected-revision revise, tombstone, normalized ordered/capped/cited retrieval are missing.
3. Audit requires partition/epoch GENESIS, redacted allow/deny/read events, canonical domain-separated chaining/CAS, separately authorized audit read, emergency sink, and anchor high-water checks.
4. Mutations require prepared → local atomic commit → anchor → publish with recovery at every crash boundary; current external calls and local state can diverge.
5. Expiry must be derived eligibility without mutating persisted active status; hold/purge need audit/binding, tombstone first, exact HUMAN authorization, fencing, manifest/deadline/reconciliation.
6. Backup restore must reconcile tombstone/purge manifests and external anchor high-water to prevent resurrection.

The six passing tests and exact hashes are preserved but do not establish acceptance. Attempt 1 fails review; attempt 2 requires redesign and the exact single authorized command.
