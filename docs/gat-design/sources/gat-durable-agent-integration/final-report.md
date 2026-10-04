# Final mission report — Durable Agent capability

## Decision requested

This is the reviewed-candidate conclusion for HUMAN acceptance of WBS revision 2 for mission `gat-durable-agent-integration`.

The repository-level Durable Agent capability is implemented, packaged, documented, and integration-verified for the approved workspace mission. This conclusion **does not** claim that the separate GAT-owned binder, Agent Session lifecycle, or Team lifecycle has been implemented. Final mission acceptance remains open until the HUMAN accepts this exact report after independent review.

## Bound authority and evidence

- Approved WBS r2 SHA-256: `ddabe11b55fe9a012f25bdffb3109952d1a8b057da158a14ebea9631a6467457`
- Accepted integration report SHA-256: `a81b254b34503dc24f54dd897b4102bdb4f114e325f5edc98d964f3348f4cfc9`
- Integrated verification: `integration_verify-a03`
  - verification SHA-256: `927cf23c3d09bd728bac9bcfff1180fd3cd62c5fa434d17ec3ea53bbdfb05712`
  - independent review SHA-256: `525d9d608b9c975e5da1ac0cb516c3f87d92c57fae4bd086f0a0862cdb80650b`
  - result: 10/10 test files and 127/127 tests passed; build, named-export check, and packed-profile smoke passed on the same settled bytes.
- Charged attempts before this final-report attempt: 18. This final-report attempt is charge 19 of the approved ceiling of 28. Failed, blocked, interrupted, and accepted attempts remain append-preserved in `execution.json`; none was rewritten as success.

The complete current-file hash table, downstream lineage reconciliation, and evidence locators are in `integration-report.md`. Historical predecessor hashes are retained as attempt evidence; current claims bind to the accepted downstream lineage and `integration_verify-a03`.

## Requirement conclusion

| Requirement | Completion conclusion | Accepted evidence |
|---|---|---|
| `service_port` | Complete: versioned Cordis service, feature flags, bounded DTOs, typed semantic errors, opaque refs. | `service_contract-a02`; `integration_verify-a03` |
| `identity_authority` | Complete: explicit workspace/global scope, profile authority, generation-bound reference checks, isolation and conflict handling. | `service_contract-a02`; `local_provider-a04`; `integration_verify-a03` |
| `task_context` | Complete: frozen path-free snapshots, metadata-only catalog, selective reads and deterministic revisions. | `service_contract-a02`; `local_provider-a04`; `scoped_consumer-a02` |
| `provider_persistence` | Complete: immutable content/generation storage, atomic current publication, restart recovery and bounded fail-closed validation. | `local_provider-a04`; `memory_protocol_qualification-a02`; `memory_lifecycle-a02` |
| `memory_governance` | Complete: candidates are unconfirmed/non-canonical; confirmed commits require explicit authorization and become canonical only through the governed mutation path. | `memory_protocol_qualification-a02`; `memory_lifecycle-a02` |
| `lifecycle` | Complete: same-isolate mutations serialize through the storage-identity FIFO; overlapping participating cross-process writers fail closed through the exclusive mutation lease; release closes admission, drains admitted work, invalidates the ref, and preserves persistent reprovisioning. | `local_provider-a04`; `memory_lifecycle-a02` |
| `member_consumer` | Complete: one explicit opaque-ref binding, deterministic model contribution and tool contract, isolation, and real plugin composition. | `scoped_consumer-a02`; `integration_verify-a03` |
| `compatibility_docs` | Complete: standalone compatibility adapter, package exports/declarations, operational documentation, explicit public/private boundary. | `standalone_adapter-a01`; `package_docs-a02`; `integration_verify-a03` |
| `mission_evidence` | Complete for review: exact hashes, command evidence, independent reviews, failed-attempt triage, terminal acceptances, and integrated provenance are retained. | `execution.json`; task evidence directories; `integration_verify-a03` |

## What is delivered

1. A real versioned `DurableAgentService` published through the plugin registration while retaining a standalone adapter.
2. A local provider with explicit scope, opaque refs, bounded inputs, immutable generations, authorization-bearing confirmed commits, recoverable publication, concurrency handling, and release semantics.
3. A Consumer projection that adds deterministic, governed, path-free member context and exact memory tooling without implicit global discovery.
4. Compatibility behavior for the existing member profile/legacy memory path, including non-destructive migration and a final discriminator recheck that prevents retained writers from mutating canonical generations after bootstrap.
5. Public package exports, generated declarations, README and service documentation that describe only the shipped capability.
6. Full integrated verification plus independent review with no unresolved critical/high contract, security, durability, isolation, or provenance finding.

## Explicitly deferred GAT-owned work

The following are **not** delivered or claimed by this mission:

- a GAT binder that owns `provision → bind → inject → release` across Agent Session or Team lifecycle;
- Team creation/destruction, Session ownership, or cross-session controller behavior;
- implicit global member discovery;
- a path-level API or a stable public contract for provider-private generation layout;
- package publication or deployment into a GAT release train.

These boundaries are deliberate. The Durable Agent package supplies the service and adapter surfaces that a future GAT-owned integration can call without making this package depend on GAT types or runtime ownership.

## Residual risks and limitations

1. The generation history has a bounded fail-closed validation ceiling; very long-lived installations may eventually need a separately designed and authorized compaction/migration procedure.
2. Same-isolate mutations serialize through the storage-identity FIFO. Overlapping participating cross-process writers fail closed through the exclusive mutation lease rather than waiting; stale leases may require operator intervention, and arbitrary non-participating filesystem writers are outside the protocol.
3. Filesystem durability depends on supported rename/fsync semantics of the deployment filesystem.
4. `workingLocation` is a trusted opaque capability; trusted hosts must not inspect or infer neighboring private layout.
5. Candidate approval policy remains the responsibility of the HUMAN or an explicitly authorized host authority.
6. Package publication and real GAT adoption have not been exercised in this workspace mission.

None of these limitations contradicts the approved Durable Agent capability objective, but each must remain visible during adoption.

## Recommended adoption steps

1. Publish/version the package only after the release owner repeats the recorded package build/export/smoke checks in the release environment.
2. Have the GAT owner design a separate binder against the public `DurableAgentService`/Consumer interfaces, with explicit Session/Team ownership and release ordering; do not couple to provider paths.
3. Add GAT-owned composition tests for Session creation, member binding, prompt/tool injection, authorization UI or policy, release drain, and teardown.
4. Define operator handling for stale mutation leases, storage backup/restore, and any future generation compaction before production rollout.
5. Keep confirmed-memory authorization auditable and never promote unconfirmed candidates merely because they exist on disk.

## Conclusion

All nine approved WBS requirements have current accepted technical evidence, and the independent integration review reports no remaining finding after the exact provenance repair. The Durable Agent capability portion of this mission is ready for HUMAN acceptance. The mission itself is not terminal until the HUMAN accepts this exact reviewed report.
