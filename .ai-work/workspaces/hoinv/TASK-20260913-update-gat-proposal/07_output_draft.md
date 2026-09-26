# Output Draft — GAT Proposal Revision 2

## Draft Outcome
- Replaced the broad initial proposal with a Conservative MVP implementation specification.
- Proposal remains explicitly inactive pending exact-hash re-review, conformance evidence, HUMAN approval, and separate HUMAN activation.

## Applied Architecture Decisions
- Durable `ProjectScope` is distinct from canonical per-task `Task Workspace`.
- `AgentDesk=(tenant_id, principal_id, project_scope_id, agent_id)`.
- Every non-trivial Task execution binds exactly one Working AIP and one canonical Task Workspace; GAT has no MVP bypass.
- Authorization is deny-by-default with explicit-deny precedence, per-operation checks, policy/membership revision binding, immediate revocation, and non-disclosing failures.
- Cross-scope promotion/share/copy is disabled in MVP.
- Shipped substring retrieval is the only MVP search capability; semantic/vector/provider substitution is deferred.
- Memory identity/provenance, retention/tombstone/privacy, append-only hash-chained audit, and HUMAN authority contracts are normative.
- Current DSH root-Session Team identity and spawn limits are mapped; per-member route/preset support is future-only.
- Package-owned conformance vectors and a security vertical slice precede WebUI.

## Pending Verification
- Search for stale conflicting claims.
- Compute new proposal SHA-256.
- Run task-scoped lint.
- Obtain fresh independent F1–F11 review.
