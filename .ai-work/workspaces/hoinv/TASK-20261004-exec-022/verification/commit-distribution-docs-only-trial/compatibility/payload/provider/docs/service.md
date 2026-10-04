# Durable Agent service

`DURABLE_AGENT_API_VERSION` is `1`. `DurableAgentService` exposes declaration validation, provisioning, fresh task context, selective item reads, candidate submission, approved commit, trusted working location, and release. Feature flags describe which optional operations a provider supports.

Declarations contain name, description, prompt, context, provider, model, and explicit `workspace` or `global` scope. The local provider uses canonical workspace resolution; global scope also requires a trusted absolute home directory. It returns opaque generation-bound references. Invalid declarations, unauthorized references, profile conflicts, unsupported scope, invalid context data, unknown items, rejected candidates, concurrent mutation, unavailable features, and incompatible APIs use the exported path-free `DurableAgentError` categories.

Task snapshots are immutable and freshly read. They contain member display data, guidance, catalog metadata, revision, path-free provenance, and capabilities; catalog entries never include bodies. Item bodies require a selective read through the same owned reference. Provider input limits include 256 KiB profiles/guidance/manifests, 1 MiB memory bodies, 2 MiB candidate envelopes, bounded metadata, and NUL rejection.

Candidates are always `unconfirmed` and non-canonical. A confirmed memory commit requires explicit human or authorized-host authorization. The local provider stores recoverable immutable generations and migrates compatible legacy profile and `MEMORY.md` state without promising its private on-disk layout. `release()` closes new admission, drains admitted work, invalidates the reference, retains only a bounded revocation window, and preserves persistent data for reprovisioning.

`DurableAgentConsumer` binds exactly one service-issued reference. Its model contribution deterministically serializes only guidance, sorted catalog metadata, and path-free provenance; its fixed tool/result text identifies selective reads and states that candidate results remain unconfirmed/non-canonical until independent approval. An unbound context has no contribution.

The standalone adapter is the only parser for legacy `team_members.yaml`; it strictly validates the legacy shape and resolves omitted scope to workspace before producing normalized declarations. It is not an implicit discovery mechanism.

No GAT binder, Agent Session controller, Team lifecycle controller, implicit global discovery, or storage-path integration API is included here. Those belong to a separate future integration mission.

## Shared task contracts

The root entry also exports the additive shared task-contract API. `normalizeTaskContract()` validates and freezes a versioned contract; `createTaskPacket()` supplies the same normalized contract and digest to a worker or reviewer; and `DurableAgentConsumer.taskContribution()` adds that packet to the existing memory contribution. Workers can return a versioned, hash-bound completion proposal, which `reviewCompletion()` checks against the current task, contract, attempt, worker, inputs, outputs, criteria, evidence, and reviewer identity.

The host supplies an independent trusted criterion verifier. It must resolve artifact and evidence refs under its ACL, check their digests, and test the original requirement rather than trusting claims or tool success. The resulting `verified` value is only an evidence assessment—not authorization, task acceptance, or commit permission. Hosts must re-check current state and authorization before committing. This API does not add GAT/session/team lifecycle wiring or change runner DTOs; existing memory-only service and Consumer methods remain unchanged. See [task contract details](task-contract.md).

## Fresh-context review

The additive root exports `createReviewPacket()`, `normalizeReviewPacket()`, `reviewPacketSha256()`, `reviewContribution()`, `normalizeReviewerVerdict()` and `runFreshReview()`. The host-owned adapter checks current proposal/contract bindings, exact digests and trusted test receipts, dispatches a fresh evidence-only request, guards read-only evidence/rationale tools, then rechecks current state and bytes before returning an advisory criterion verdict. `DurableAgentConsumer.reviewContribution()` checks a live reference but deliberately excludes ALL consumer memory/catalog/guidance. The older `taskContribution(..., 'reviewer')` remains compatible and does not provide fresh isolation.

A `context: 'fresh'` request cannot attest a transport's hidden history; the host must actually start a new model session. Required test policy, ACLs, receipt authenticity, durable rationale audit, authenticated identities and final atomic acceptance/commit remain host responsibilities. Nothing is automatically wired into the GUI/GAT/Team lifecycle. See [fresh review guide](reviewer-context.md).
