# Approved implementation decisions

Date: 2026-10-04 (Asia/Tokyo)

## HUMAN evidence

- Request: `please run this AIP`.
- P-01–P-08 question answer: `Approve P-01–P-08 as proposed (Recommended)`.
- Integration question answer: `WK-style adapter with current direct-continuable members (Recommended)`.

## Baseline

P-01: proposed separate `@vuhoi/gat-durable-agent`, `packages/durable-agent/`.
P-02: explicit workspace/fresh adapter; generic core may keep fresh/fork/no attachments.
P-03: one owner per canonical workspace/name, dedicated provider, single host per storage workspace; reject concurrent owners and quarantine unsettled cleanup.
P-04: strict explicit `team_members.durable.yaml`, selected by opt-in integration profile, one initializer.
P-05: read-memory and submit-unconfirmed-candidate model tools; host-only independently authorized commit.
P-06: bounded coherent refresh at bind/recover and before every authorized request; active refresh failure blocks the request.
P-07: independent foundation/integration verification can proceed before production enablement.
P-08: graceful contribution abstention only with exact authoritative isolated-execution closing proof. This selected direct-continuable target retains strict denial on authority loss; it does not fabricate isolated proof. General post-await withholding and cleanup safeguards still apply.

## Dependency ownership

- GAT implementation/design: this AIP in this repository.
- WK DA provider/API: existing sibling package, read-only qualification; changes need owner-approved scope.
- DSH reserved-handle/request hook/executor metadata: host dependency, read-only qualification; missing capabilities become owner handoffs.
- Mission/task leases: approved GAT/host authorization workstream evidence must be located; binding scope cannot silently rewrite that authority.
- Canonical/Truth/contract/wiki changes: applicable approved review/CR gates. Project draft design deltas here preserve their existing authority status.

## Authorized prerequisite and final integration follow-up

The later HUMAN instruction explicitly authorized isolated DSH prerequisite changes in the separate worktree based on c291, with design-before-code and deployment approval separate. AIP-EXEC-023 delivered committed prerequisite revision 5c02ce9. The current request authorizes completing remaining AIP-EXEC-022 integration, package and evidence tasks against those pins. Disposable verification targets and private provider/session storage are test fixtures. The original dirty checkout, protected compatibility controls and untracked native outputs are preserved. No push, merge, publication or existing-process activation is included.
