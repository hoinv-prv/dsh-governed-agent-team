# GAT WK Durable Agent adapter

This explicit adapter library uses the WK Durable Agent public API v1 (`/service` and `/consumer`). It provides strict `team_members.durable.yaml` normalization, the `durable-agent` v1 binder, exclusive identity ownership, and executable read-memory / submit-candidate tools. Confirmed memory remains a separately authorized host operation.

The current GAT compatibility runtime rejects required attachments before creating member rows. Production composition still needs the frozen reserved-child lifecycle, a request hook that refreshes prompt context before dispatch, exact mission/task authorization, and nested capability enforcement. The package is therefore excluded from the current default installer/profile. Deterministic ports and temporary public-provider tests qualify the adapter library only.

Trusted host composition supplies `serviceBindingKey`, a pinned service instance, an independent workspace resolver and explicit `dedicatedProvider: true` / `singleHostWorkspace: true` assertions to `createDurableAgentBinder`. A coordinator shared by all binders on that service prevents overlapping owners for canonical workspace/name. These assertions require deployment evidence; they do not create a distributed storage lock. Pending or failed provider cleanup keeps identity quarantined.

`loadDurableTeamMembers` takes canonical workspace, continuation route and model-route preflight from the host. It reads a regular bounded file without symlink following, requires explicit fresh/workspace declarations and never falls back. The normalized payload stores the declaration and trusted selectors, with no runtime reference. Recovery uses that persisted payload and independently verifies its workspace/service identity.

The qualified host capability scope installs one prompt section and two tools, replaces the section on each request refresh, authorizes every read/effect/request, and removes all installed authority synchronously at cutoff. Provider calls that finish after cutoff cannot return model-visible bodies. Cleanup is memoized and persistent provider data survives release.

Design: [proposal](../../docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md) §§4–7 and [Detail Design](../../docs/gat-design/DETAIL_DESIGN.md) §§5–6. Exact source, test, build and dependency evidence: `.ai-work/workspaces/hoinv/TASK-20261004-exec-022/`.
