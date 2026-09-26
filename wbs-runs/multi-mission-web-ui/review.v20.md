# Review candidate multi-mission-web-ui, revision 20

- SHA-256: `239f40e8c4fa8cbba7bf919e8af10e249eb4dbe627bbc06ec207a6f12e15289c`
- Base: approved revision 19 `95d9cfac0c4b08539490769af7c8d7653d3e2855f38a40d7069feda9824aac0b`
- Validate/order/hash: PASS; canonical order unchanged.

## Trigger and bounded delta

Partitioned-memory attempt 1 ran six green tests but failed review because the implementation contradicted accepted memory/audit/lifecycle vectors and two test filenames plus command shape were outside the exact grant. Revision 20:

- preserves all 31 charged attempts and all prior accepted outputs;
- adds one governance reconciliation charge only, raising caps 42→43 attempts and 4,895→4,940 minutes;
- keeps partitioned-memory max attempts at 3, leaving attempts 2 and 3 available;
- expands that task's write scope only to delete the two hashed unauthorized attempt-1 test files;
- pins the redesign to complete record/physical selector/retrieval, partitioned canonical audit and authorized read/emergency sink/high-water, prepared→commit→anchor→publish crash recovery, derived expiry, audited hold/tombstone-first authorized purge/manifests, and anti-resurrection restore;
- preserves the one exact three-file Node test command and all later tasks, gates, dependencies, no-DSH/network/dependency/accepted-conformance restrictions.

Independent review first found an accidental unaffected wrapper Workspace migration; the candidate restores the exact v19 wrapper path. HUMAN approval is required before reconciliation, cleanup, or redesign.
