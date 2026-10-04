# Durable Agent

Private Cordis package exposing Durable Agent API version 1. Host `apply(ctx, config)` validates the existing worker/triage/verify skill scaffold and publishes the `durableAgent` service. It returns the concrete service instance for provisioning and Consumer binding; the Cordis context also exposes the versioned service.

## Public roles

The root entry exports the service contract, `LocalDurableAgentProvider`, `DurableAgentConsumer`, `bindDurableAgentConsumer`, errors, and standalone legacy adapter APIs. The client entry preserves the existing host-binding config scaffold. `loadDurableAgentDeclarations()` is the only legacy `team_members.yaml` adapter: it validates that file strictly and defaults omitted legacy `storage_scope` to `workspace`. Core service declarations always require an explicit `scope`; global storage requires an explicit global declaration and trusted home input.

A Consumer binds one opaque service-issued reference. Its deterministic model contribution contains guidance, catalog metadata, path-free provenance, and fixed selective-read/candidate tool text. It never includes eager memory bodies, storage paths, keys, secrets, or another member's data. Candidate submission returns **unconfirmed, non-canonical** data; only an authorization-bearing commit can create confirmed memory.

The local provider persists profile, guidance, working artifacts, candidates, and immutable memory generations. It validates UTF-8/NUL and bounded inputs, rejects unsafe references and symlinks, migrates compatible legacy profile/memory state, and releases only process-local references while persistent data remains for reprovisioning. See [service details](docs/service.md).

## Shared task contracts

Hosts can provide a compact versioned contract to workers and reviewers with `createTaskPacket()` or `DurableAgentConsumer.taskContribution()`. Workers submit evidence-bound completion proposals; `reviewCompletion()` checks current contract/attempt/input bindings and requires an independent host verifier for every criterion. A `verified` assessment is not permission, task acceptance, or commit. Existing memory-only APIs remain unchanged. See [task contract API and host example](docs/task-contract.md).

## Fresh-context review

`runFreshReview()` builds a versioned evidence packet, independently checks host-authorized artifact/evidence digests and trusted test receipts, and dispatches only a fresh reviewer payload. Worker history and durable memory are excluded; rationale is fetched only through bounded, audited requests. Criterion verdicts are evidence-bound and advisory, with current-state/byte rechecks before return. The host supplies a genuinely new-session transport and owns acceptance/commit. See [API and integration guide](docs/reviewer-context.md) and [A/B evaluation results](docs/reviewer-ab-results.md).

## Boundaries

This package does not ship a GAT binder, create Agent Sessions, control Team lifecycle, discover global storage implicitly, or provide a path-level integration API. Those responsibilities are deferred to a separate binder/lifecycle mission.
