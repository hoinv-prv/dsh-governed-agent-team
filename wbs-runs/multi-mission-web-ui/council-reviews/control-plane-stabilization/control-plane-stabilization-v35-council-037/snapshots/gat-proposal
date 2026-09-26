# Governed Agent Team + MCP Reference Memory Architecture Proposal

**Project:** Governed Agent Team (GAT) on DeepSeek Harness  
**Revision:** 3 — Conservative MVP (selective rereview corrections)  
**Date:** 2026-09-13  
**Status:** **Inactive proposal — implementation and activation are not approved**  
**Audience:** HUMAN decision owners, DSH/GAT implementers, security reviewers, and verification agents  
**Driving reviews:** `TASK-1_COUNCIL_REVIEW_REPORT.md` F1–F11; `review-advisory.md` R1–R8, selectively adjudicated  
**Working AIP:** `AIP-EXEC-007`

---

## 0. Decision Status and Normative Language

This revision adopts the HUMAN-selected **Conservative MVP** profile. It is a design proposal, not authority to implement, merge, deploy, or activate GAT.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

Precedence for this proposal is:

```text
Project Truth and package-owned governance
  > approved HUMAN decisions
  > this proposal
  > reference memory and working notes
```

GAT MAY invoke and report package-owned gates. It MUST NOT redefine, suppress, or bypass them. Only an attributable HUMAN decision owner may approve a deviation, accept a deliverable, approve this proposal, or activate an implementation. Those are separate decisions.

### 0.1 Conservative MVP decisions

The HUMAN selected the Conservative MVP policy profile. Revision 3's concrete backend, transaction, lifecycle, and adapter mechanisms are **proposed implementations of that profile**, not previously HUMAN-approved choices; they remain inactive until the Activation Manifest gates are satisfied.

| Area | Decision |
|---|---|
| Durable boundary | Use `ProjectScope`; do not redefine canonical Workspace |
| Runtime boundary | Exactly one canonical Task Workspace for each non-trivial Task execution |
| Execution guardrail | Exactly one Working AIP controls each non-trivial Task execution; no GAT-local bypass |
| AgentDesk identity | `(tenant_id, principal_id, project_scope_id, agent_id)` |
| Authorization | Deny by default; explicit deny wins; authorize every operation; revoke immediately |
| Promotion | No cross-scope promotion, sharing, copying, or scope mutation in MVP |
| Retrieval | Adapter-owned partitioned GAT MCP backend with deterministic substring matching; DSH provides the generic bridge; semantic/vector retrieval is future work |
| DSH compatibility | Adapt to current DSH; do not claim unverified per-member routing capabilities |
| Audit | Append-only, hash-chained, redacted, access-controlled events |
| Lifecycle | Tombstone first; configurable retention and purge; fail activation when policy is absent |
| Acceptance | Package-owned executable gates with persisted evidence; HUMAN accepts and activates |
| Delivery order | Security vertical slice before broad WebUI |

### 0.2 Activation rule

This proposal and every implementation built from it remain inactive until one content-addressed **Activation Manifest** exists and every referenced item verifies. The manifest MUST contain:

1. proposal hash and independent exact-hash review disposition;
2. implementation/package, DSH, MCP bridge, and `gat-partitioned-memory-mcp` hashes;
3. versioned conformance vector hash plus passing raw evidence for topology, raw-MCP-tool non-admission, physical isolation, readiness, native Team-plan approval, mutation/audit crash recovery, lifecycle, restart, and negative side effects;
4. accepted threat-model hash and residual-risk dispositions;
5. active tenant retention/privacy/legal-hold/purge policy hashes and audit/store protocol proof;
6. package-owned Working AIP readiness-gate name/revision and canonical Task Workspace integration evidence;
7. current native Team-plan mapping and, when used, native TeamMission mapping/approval evidence;
8. unresolved deviations/open risks, each with explicit HUMAN disposition;
9. explicit attributable HUMAN proposal approval/acceptance; and
10. a separate explicit HUMAN activation record binding the complete manifest hash.

Changing any referenced artifact or approval makes the manifest stale and blocks activation until rebuilt and re-approved.

---

## 1. Purpose and Bounded MVP

GAT provides reusable agent definitions and team coordination while preserving AI Work System governance and isolating reference memory.

The Conservative MVP is one end-to-end security vertical slice:

```text
Tenant + Principal
  → ProjectScope
  → AgentDefinition + current DSH Team membership
  → non-trivial Mission/Task
  → Working AIP + canonical Task Workspace
  → AgentRun
  → per-operation authorization
  → substring search/get/remember/revise/tombstone
  → append-only audit
  → independent verification
  → HUMAN acceptance and separate activation
```

Broad WebUI, semantic retrieval, cross-scope promotion, autonomous learning, independent-session routing, and per-member model/provider/preset routing are explicitly outside MVP.

---

## 2. Core Principles

### 2.1 Source of Truth is agent-independent

Authoritative requirements, policies, approved decisions, accepted deliverables, and designated repository state do not change with agent identity. Skills, Desks, and memory are reference-only and MUST NOT silently override authoritative sources.

When reference memory conflicts with SoT, SoT wins. The runtime SHOULD mark or report the memory as stale while preserving provenance.

### 2.2 Identity is persistent; execution is ephemeral

`AgentDefinition` is reusable. `AgentRun` is one bounded execution. Reusing an agent never implies reusing authorization, a Task Workspace, or a session.

### 2.3 Team membership is separate from agent identity

`TeamMembership` defines the role and bounded coordination authority for one team context. `member_id` is not `agent_id`. Membership does not grant memory access by itself; every memory operation is authorized independently.

### 2.4 ProjectScope and Task Workspace are different

`ProjectScope` is the durable tenant-bound project/repository boundary. The canonical `Task Workspace` is active runtime memory for one task/run at `.ai-work/workspaces/{account}/{task_id}/`.

A Task Workspace MUST NOT become a project registry, durable knowledge store, or second SoT. An AgentRun through a Working AIP MUST reuse the driving AIP's Task Workspace; it MUST NOT create a second task-runtime workspace.

### 2.5 AgentDesk is principal- and project-bound

```text
AgentDesk key = (tenant_id, principal_id, project_scope_id, agent_id)
```

A Desk is durable reference context for one principal using one agent within one ProjectScope. Changing tenant, principal, or ProjectScope selects a different Desk even when `agent_id` is unchanged. Aliases MUST NOT weaken this boundary.

### 2.6 Runtime scope is trusted; LLM assertions are not

GAT constructs immutable request context from authenticated runtime state. LLM tool arguments cannot broaden identity, scope, ownership, or permission.

### 2.7 Working AIP is mandatory

Every non-trivial Task execution MUST bind one Working AIP before dispatch or meaningful execution. Conservative MVP defines no GAT-local bypass. Any package-level reduction path remains owned by the controlling package and HUMAN gate, not by GAT configuration.

### 2.8 No cross-scope promotion in MVP

Memory can be created or revised only inside an already authorized target scope. Task→Desk, Desk→Agent, cross-project, and cross-tenant promotion/copy/share are disabled. Recording a candidate does not change its scope.

### 2.9 HUMAN retains important decision authority

Agents and councils may analyze, coordinate, recommend, and verify. HUMAN exclusively owns high-risk direction, deviations, deliverable acceptance, proposal approval, implementation activation, merge, and deployment decisions.

---

## 3. Domain Model and Invariants

### 3.1 Entities

```text
Tenant
Principal
ProjectScope
AgentDefinition
TeamRuntimeBinding
TeamMembership
Mission
Task
WorkingAIP
TaskWorkspace
AgentDesk
AgentRun
MemoryRecord
AuthorizationDecision
AuditEvent
ActivationRecord
```

`TeamDefinition` may be a future reusable GAT object. It MUST NOT be represented as a currently shipped DSH capability in MVP.

### 3.2 Required identifiers

All persisted identifiers MUST be unique within a tenant namespace. External IDs MUST be stored with type and issuer to prevent collisions.

```yaml
tenant_id: tenant-acme
principal_id: principal-hoi
project_scope_id: project-gat
agent_id: developer
team_runtime_id: dsh-root-session-id
member_id: implementer
aip_id: AIP-EXEC-006
task_workspace_id: TASK-20260913-update-gat-proposal
mission_id: mission-017
task_id: task-042
run_id: run-042-02
```

### 3.3 Cardinality and ownership

| Relationship | Conservative MVP invariant |
|---|---|
| Tenant → ProjectScope | One tenant has many ProjectScopes; each ProjectScope belongs to exactly one tenant |
| Principal × ProjectScope × Agent → Desk | At most one active Desk for the composite key; revisions are record-oriented |
| Mission → Task | A Mission has one or more Tasks; Task state is authoritative outside memory |
| Non-trivial Task execution → Working AIP | Exactly one controlling Working AIP |
| Non-trivial Task execution → Task Workspace | Exactly one canonical Task Workspace |
| Working AIP ↔ Task Workspace | One active pair for the execution; runtime pointer is stable provenance |
| Task execution identity | `(tenant_id, principal_id, task_id, working_aip_id, task_workspace_id)` is fixed for the Task lifetime; a re-plan updates the same Working AIP and never replaces the Task Workspace |
| Task execution replacement | GAT cannot replace the Task Workspace or alias another Workspace to the same Task. If package-owned flow requires a different Workspace or controlling AIP identity, it MUST create a new canonical `task_id` and preserve `supersedes_task_id` provenance |
| Task execution → AgentRun | One or more sequential/concurrent AgentRuns MAY participate, but all MUST bind the same fixed execution identity and current revisions; no AgentRun owns or duplicates the AIP/Workspace |
| AgentRun → Task execution | Exactly one Task execution identity, Working AIP, and Task Workspace |
| AgentRun → TeamMembership | Zero for approved solo execution; exactly one for team execution |

### 3.4 Lifecycle boundaries

- `ProjectScope` survives Tasks and AgentRuns.
- `TaskWorkspace` follows canonical lifecycle: `not_created → active → paused → closing → closed → archived`.
- `WorkingAIP` controls scope, steps, guardrails, re-plan, and done criteria.
- `AgentDesk` contains reference records only and never owns task state.
- `Mission` and `Task` state MUST NOT be inferred from memory.

---

## 4. Core Entity Contracts

### 4.1 ProjectScope

```yaml
project_scope_id: project-gat
tenant_id: tenant-acme
repository_refs:
  - repo:dsh-governed-agent-team
sot_refs:
  - docs/approved-requirements.md
policy_set_id: gat-project-policy
policy_revision: 12
status: active
```

`ProjectScope` identifies durable project/repository scope and its authoritative references. It is not canonical Workspace.

### 4.2 AgentDefinition

```yaml
agent_id: developer
tenant_id: tenant-acme
name: Developer
persona:
  role: Software implementation specialist
skills:
  - code-implementation
  - debugging
runtime_preferences:
  preset_ref: coding-default
policies:
  max_parallel_runs: 3
```

Runtime preferences are requests, not proof of DSH support. The adapter MUST discover and verify capability before use; unsupported preferences fail closed or use an explicitly approved current-runtime mapping, never a silent substitute.

### 4.3 TeamRuntimeBinding and TeamMembership

```yaml
team_runtime_id: dsh-root-session-id
runtime_kind: dsh-native-team
plan_revision: 9
plan_phase: approved
plan_approved_revision: 9
plan_approval_hash: sha256:...
native_mission_binding: none
member_id: implementer
agent_id: developer
role: implementation
responsibilities:
  - implement assigned task
authority_refs:
  - membership-policy-17
membership_revision: 4
requested_by: principal-hoi
decision_owner: principal-hoi
report_to: lead
escalation_route: human-requester
```

The DSH native Team is rooted in a top-level Session. GAT MUST keep its logical reusable identity separate from that current runtime identity.

### 4.4 Mission and Task

Mission carries goal, ProjectScope, requested-by/decision routing, acceptance criteria, and Tasks. Task carries authoritative task state, dependencies, owner, expected artifacts, Working AIP, and Task Workspace references.

```yaml
mission_id: mission-017
tenant_id: tenant-acme
project_scope_id: project-gat
requested_by: principal-hoi
decision_owner: principal-hoi
report_to: principal-hoi
escalation_route: principal-hoi
status: active
```

```yaml
task_id: task-042
mission_id: mission-017
working_aip_id: AIP-EXEC-042
working_aip_hash: sha256:...
working_aip_readiness_evidence_hash: sha256:...
task_workspace_id: TASK-20260913-task-042
status: in_progress
```

### 4.5 AgentRun

```yaml
run_id: run-042-02
tenant_id: tenant-acme
principal_id: principal-hoi
project_scope_id: project-gat
agent_id: developer
team_runtime_id: dsh-root-session-id
member_id: implementer
team_plan_revision: 9
team_plan_phase: approved
team_plan_approved_revision: 9
team_plan_approval_hash: sha256:...
native_mission_revision: 3              # only when explicitly mapped
native_mission_approved_revision: 3     # only when explicitly mapped
native_mission_approval_hash: sha256:... # only when explicitly mapped
mission_id: mission-017
task_id: task-042
working_aip_id: AIP-EXEC-042
working_aip_hash: sha256:...
working_aip_readiness: execution_ready
working_aip_readiness_gate_revision: aiws-readiness-v0.9.9
working_aip_readiness_evidence_hash: sha256:...
task_workspace_id: TASK-20260913-task-042
session_id: dsh-child-session-id
policy_revision: 12
membership_revision: 4
requested_by: principal-hoi
decision_owner: principal-hoi
report_to: lead
escalation_route: principal-hoi
```

Before start or resume, GAT MUST revalidate all references, the package-owned Working AIP readiness evidence, the fixed Task Workspace binding, current policy/membership revisions, and exact current native Team-plan approval. If a GAT Mission is explicitly mapped to native `TeamMissionSnapshot`, its exact approved revision is also bound; otherwise no native Mission approval is claimed. Resume is allowed only for the same tenant, principal, ProjectScope, agent, authority, Task/AIP/Workspace tuple, and approval snapshots. Otherwise create a new package-owned Task identity or AgentRun as applicable and repeat every gate.

Scope changes MUST follow Working AIP re-plan rules before execution continues.

---

## 5. Reference Context and AgentDesk

An AgentDesk is a logical view over authorized `project-desk`-scope MemoryRecords. It may contain observations, lessons, cautions, hypotheses, handoff references, and pointers to SoT.

Desk content MUST remain:

- `authority: reference_only`;
- attributable to tenant, principal, ProjectScope, agent, task, and run;
- individually revisioned;
- removable through governed lifecycle;
- invisible across composite Desk keys unless a future approved sharing design exists.

A single mutable `DESK.md` MUST NOT be the authoritative writable store. A generated read-only view MAY exist if it is derived from record-oriented storage.

---

## 6. Memory Scopes and No-Promotion Rule

Conservative MVP supports:

```text
agent
project-desk
task
```

All scopes remain tenant- and principal-aware.

- `agent`: explicitly authored agent reference records that are not derived from another scope. It is not a sink for promoted project data.
- `project-desk`: principal/agent reference context within one ProjectScope.
- `task`: reference notes for one Task; not task state.

`mission-shared` is deferred. Current DSH `TeamMembership` is team-wide, while no authoritative MissionMembership/revision contract is established for this proposal. A future revision must define membership source, exact revision, revocation, PDP/audit binding, and cross-mission isolation before adding the scope.

The adapter MUST reject:

- scope mutation;
- cross-scope copy or promotion;
- cross-ProjectScope or cross-tenant sharing;
- automatic Task→Desk→Agent flows;
- “agent-global” retrieval of records derived from a ProjectScope.

Future promotion requires a separately approved design covering actor, decision owner, classification, sanitization, provenance, source/authority/target checks, revocation propagation, and audit. It is not exposed by MVP tools.

---

## 7. MemoryRecord Schema and Invariants

```json
{
  "id": "tenant-acme:mem-0081",
  "schema_version": 1,
  "revision": 1,
  "authority": "reference_only",
  "tenant_id": "tenant-acme",
  "principal_id": "principal-hoi",
  "project_scope_id": "project-gat",
  "scope": "project-desk",
  "owner": { "type": "agent", "id": "developer" },
  "agent_id": "developer",
  "desk_id": "tenant-acme:principal-hoi:project-gat:developer",
  "mission_id": "mission-017",
  "task_id": "task-042",
  "created_run_id": "run-042-02",
  "created_by": "principal-hoi",
  "updated_by": "principal-hoi",
  "content": "Check generated build output before changing plugin symlinks.",
  "kind": "lesson",
  "origin": {
    "type": "task_observation",
    "task_id": "task-042",
    "run_id": "run-042-02"
  },
  "source_refs": [
    { "type": "task_artifact", "id": "artifact-build-log-042", "revision": "sha256:..." }
  ],
  "classification": "internal",
  "status": "active",
  "retention_policy_id": "tenant-acme:memory-default-v1",
  "created_at": "2026-09-13T00:00:00Z",
  "updated_at": "2026-09-13T00:00:00Z",
  "expires_at": null,
  "tombstoned_at": null
}
```

### 7.1 Required fields

All records require `id`, `schema_version`, `revision`, `authority`, `tenant_id`, `principal_id`, `project_scope_id`, `scope`, `owner`, `agent_id`, `content`, `kind`, `origin`, `classification`, `status`, `retention_policy_id`, `created_by`, `updated_by`, `created_run_id`, `created_at`, and `updated_at`.

Every revise/tombstone/lifecycle transition MUST append an immutable prior-revision record containing prior content hash, actor, run, Task/Working-AIP/Task-Workspace binding hash, native Team-plan approval hash, policy/membership snapshot hashes, decision ID, timestamp, and previous revision. The current-record projection may change, but revision history is append-only and cannot be rewritten by `memory_revise`.

`source_refs` is required and non-empty when content is derived from an artifact, conversation, SoT source, tool result, or other record. Direct original notes use `source_refs: []` and `origin.type: direct_note`; they MUST NOT omit origin.

Scope-specific foreign keys are mandatory:

- `project-desk` → `desk_id`;
- `task` → `task_id`;
- `agent` → explicit `agent_id` and `origin.type: direct_note` in MVP.

Invalid or ambiguous records are rejected with no write.

### 7.2 Identity and access

Record owner and origin are provenance, not authorization grants. Knowing an ID, owning the agent name, or belonging to the Team does not imply read/write permission.

---

## 8. Authorization Decision Contract

### 8.1 Authoritative inputs

Every memory operation MUST call the policy decision point with trusted runtime data:

```json
{
  "subject": {
    "tenant_id": "tenant-acme",
    "principal_id": "principal-hoi",
    "agent_id": "developer",
    "team_runtime_id": "dsh-root-session-id",
    "member_id": "implementer",
    "mission_id": "mission-017",
    "task_id": "task-042",
    "working_aip_id": "AIP-EXEC-042",
    "working_aip_hash": "sha256:...",
    "task_workspace_id": "TASK-20260913-task-042",
    "run_id": "run-042-02",
    "team_plan_revision": 9,
    "team_plan_phase": "approved",
    "team_plan_approved_revision": 9,
    "native_mission_revision": 3,
    "native_mission_approved_revision": 3
  },
  "resource": {
    "type": "memory_namespace",
    "project_scope_id": "project-gat",
    "scope": "project-desk",
    "resource_id": "tenant-acme:mem-0081"
  },
  "action": "memory.get",
  "policy_revision": 12,
  "membership_revision": 4,
  "correlation_id": "corr-123"
}
```

`team_plan_*` fields are mandatory for native Team execution and come from the current DSH `TeamView`. `native_mission_*` fields are conditionally required only when the GAT Mission is explicitly bound to a native `TeamMissionSnapshot`; omission is otherwise explicit and MUST NOT be interpreted as native mission approval. The full Task/AIP/Workspace tuple is required for every non-trivial operation.

Required actions are:

```text
memory.search
memory.get
memory.remember
memory.revise
memory.tombstone
memory.legal_hold.apply
memory.legal_hold.release
memory.purge.authorize
memory.purge.execute
memory.purge.verify
audit.read
```

### 8.2 Decision output

```json
{
  "decision": "deny",
  "reason_code": "POLICY_EXPLICIT_DENY",
  "decision_id": "authz-991",
  "policy_revision": 12,
  "policy_snapshot_hash": "sha256:...",
  "membership_revision": 4,
  "membership_snapshot_hash": "sha256:...",
  "matched_rule_ids": ["rule-deny-17"],
  "task_execution_binding_hash": "sha256:...",
  "team_plan_approval_hash": "sha256:...",
  "allowed_namespace": null,
  "selector_hash": null,
  "decided_at": "2026-09-13T00:00:00Z"
}
```

### 8.3 Evaluation rules

1. Authenticate tenant and principal.
2. Validate the fixed AgentRun/Task/Working-AIP/Task-Workspace tuple.
3. Consume the package-owned Working AIP readiness result and evidence; for non-trivial execution anything other than the package's executable readiness outcome denies.
4. For native Team execution, read current `TeamView.planRevision/planPhase/planApproval`; missing, non-approved, or stale exact-revision approval denies before spawn/resume/tool operation.
5. If the GAT Mission is explicitly mapped to a native `TeamMissionSnapshot`, bind its current revision and exact HUMAN approval; do not claim this is a current DSH spawn gate.
6. Load current system, tenant, ProjectScope, agent-limit, membership, Task, and lifecycle policies.
7. An explicit deny at any authoritative layer wins.
8. Missing, stale, contradictory, or unverifiable input denies.
9. Absence of an allow denies.
10. Bind the result to content-addressed policy/membership/readiness/native-approval/execution evidence.
11. Authorize the exact operation and physical namespace before retrieval or mutation.
12. Append an audit event for allow and deny.

The storage namespace is physically partitioned by `(tenant_id, project_scope_id, scope_kind, scope_owner_key)`, where `scope_owner_key` is exactly: `agent:<principal_id>:<agent_id>` for agent scope; `desk:<principal_id>:<agent_id>` for project-desk; and `task:<task_id>` for task. Principal access remains part of every selector. The PDP produces a signed/typed selector containing the complete partition key, permitted principal/action/classification constraints, Task/AIP/Workspace binding hash, readiness evidence hash, native Team-plan approval hash, conditional native Mission approval hash, policy/membership snapshot hashes, and capability revision; the adapter MUST apply it before issuing any backend search/get. Denied requests perform **zero backend read/search/mutation calls**. Application-side post-filtering of a broader result set is forbidden.

Decision and result caching are disabled in Conservative MVP. Before every operation, the adapter MUST read the current authoritative execution binding, package readiness evidence, Team plan approval, policy, membership, and applicable native Mission approval in one consistent snapshot. The signed selector and decision bind hashes of that complete snapshot.

Minimum reason codes:

```text
ALLOW_EXPLICIT
AUTHENTICATION_FAILED
BINDING_INVALID
POLICY_EXPLICIT_DENY
NO_ALLOW_RULE
POLICY_REVISION_STALE
MEMBERSHIP_REVISION_STALE
RESOURCE_SCOPE_MISMATCH
ACTION_NOT_ALLOWED
WORKING_AIP_REQUIRED
WORKING_AIP_NOT_EXECUTION_READY
WORKING_AIP_LITE_INAPPLICABLE
TEAM_PLAN_APPROVAL_MISSING
TEAM_PLAN_APPROVAL_STALE
NATIVE_MISSION_APPROVAL_STALE
TASK_WORKSPACE_REQUIRED
TASK_WORKSPACE_CONFLICT
TASK_EXECUTION_BINDING_STALE
LIFECYCLE_ACTION_DENIED
LEGAL_HOLD_ACTIVE
PURGE_NOT_AUTHORIZED
PROMOTION_DISABLED
CAPABILITY_UNSUPPORTED
RAW_MCP_TOOL_NOT_ADMITTED
AUDIT_APPEND_FAILED
SECURITY_SERVICE_UNAVAILABLE
```

### 8.4 Revocation

Policy, membership, readiness, native Team-plan approval, native Mission approval when bound, or Task-execution-binding revocation takes effect before the next operation. Active sessions and prior allow decisions confer no continuing right. Because Conservative MVP has no decision/result cache, every operation reads and binds the current authoritative snapshot directly. Stale request evidence is denied; revocation events are notification/operational signals, not the correctness mechanism.

### 8.5 Non-disclosure and side channels

Unauthorized and nonexistent IDs MUST use the same externally visible status class, response shape, and bounded timing policy. Search result counts, ranking metadata, timing, backend traces, logs, and errors MUST NOT reveal unauthorized namespace existence.

---

## 9. GatMemoryAdapter and Tool Contracts

```text
Agent / DSH tool call
  → GatMemoryAdapter
  → package readiness + native Team-plan gate + Authorization PDP
  → complete physical partition selector
  → gat-partitioned-memory-mcp
       ↔ transactional record/revision/idempotency/audit-outbox store
       → synchronous external audit-head anchor
  → normalized reference-only result or fail-closed disposition
```

The adapter receives trusted AgentRun context out of band. The LLM supplies only operation-specific data such as query, record ID, content, limit, idempotency key, or expected revision.

DSH's generic MCP client normally discovers and exposes server tools as raw `mcp__<server>__<tool>` names. Conservative MVP MUST NOT expose or admit raw `mcp__gat-partitioned-memory-mcp__*` tools to any Agent/LLM. The package registers only GAT wrapper tools below; tool-schema visibility and execution admission both deny the raw prefix before any MCP/backend call. The MCP connection is held in a trusted package-only capability surface unavailable to arbitrary tool dispatch. Configuration that makes raw tools visible or callable fails preflight and activation.

Each tool independently reauthorizes:

- `memory_search(query, limit)` — search only an authorized namespace;
- `memory_get(id)` — return an authorized active record or non-disclosing not-found;
- `memory_remember(record, idempotency_key)` — create only in the bound authorized scope;
- `memory_revise(id, patch, expected_revision, idempotency_key)` — same-scope update with optimistic concurrency;
- `memory_tombstone(id, expected_revision, reason, idempotency_key)` — immediate logical deletion and search-index/materialization removal;
- `memory_legal_hold_apply/release(...)` — HUMAN-authorized hold transition bound to exact record/policy revisions;
- `memory_purge_authorize/execute/verify(...)` — separate HUMAN authorization, fenced executor action, and reconciliation evidence.

`memory_share` and `memory_promote` do not exist in MVP.

Mutation responses MUST include `decision_id`, record ID, old/new revision where applicable, disposition, and audit event ID. Retry with the same idempotency key MUST return the original disposition without duplicate mutation.

Audit commit behavior for reads, denials, and mutations is normative in §12.2; no operation may expose content or mutate state without its required audit disposition.

---

## 10. Retrieval Capability Contract

### 10.1 Pinned MVP topology

MVP uses deterministic substring retrieval only. It MUST NOT require embeddings, vectors, semantic similarity, learned ranking, or third-party data transfer.

DSH itself supplies a generic, default-off MCP client bridge; it does **not** ship or govern a memory database. The upstream MCP Reference Memory example owns one JSONL graph and exposes no complete tenant/principal/Task namespace selector, so it is not the Conservative MVP backing store.

The MVP topology is one adapter-owned `gat-partitioned-memory-mcp` server whose transactional store is physically partitioned by the complete key defined in §8.3. The MCP tool request never supplies or overrides that key: `GatMemoryAdapter` selects exactly one partition from trusted runtime/PDP output, and the storage engine executes substring search within that partition only. No broad graph read or application-side security filter is permitted.

```json
{
  "dsh_bridge": {
    "kind": "generic-mcp-client",
    "default_enabled": false,
    "revision": "pinned-dsh-hash"
  },
  "backend": {
    "provider": "gat-partitioned-memory-mcp",
    "native_capabilities": ["physical-partition-select", "substring-search", "get", "transactional-write", "revise", "tombstone", "audit-outbox"],
    "revision": "implementation-hash"
  },
  "semantic_search": false
}
```

All memory capabilities remain unavailable until the topology PoC proves selector non-bypass, zero non-selected-partition reads, transactional mutation/audit semantics, restart recovery, and the package-owned conformance vectors on pinned revisions. If unavailable or unsupported, the adapter returns `CAPABILITY_UNSUPPORTED`; there is no silent provider substitution, upstream-reference-server fallback, semantic fallback, or third-party transfer.

### 10.2 Deterministic substring behavior

After authorization establishes the allowed namespace:

1. normalize query and searchable text using a pinned case-folding/Unicode rule;
2. apply literal substring matching to the documented searchable fields;
3. exclude tombstoned, expired, unauthorized, and disallowed-classification records before matching;
4. order results deterministically by exact-match class, then `updated_at` descending, then record ID ascending;
5. cap `limit` at a configured maximum;
6. return citations containing record ID, revision, source refs, status, and freshness metadata.

One empty result does not prove no memory exists. The LLM MAY reformulate a bounded number of searches, subject to rate and audit policy.

### 10.3 Task Lens

Task Lens is optional query/ranking context consistent with canonical AIWS architecture. It MUST NOT be an authorization grant or required hard filter. The MVP substring backend may ignore it after logging capability absence; the query still carries the information need.

### 10.4 Future provider gate

Semantic/vector retrieval requires a new reviewed proposal revision that pins provider, isolation, data handling, discovery, fallback, failure semantics, and executable acceptance evidence. It cannot be enabled by configuration alone.

---

## 11. Memory Lifecycle, Privacy, and Deletion

### 11.1 Classification and write validation

Every write MUST carry a permitted classification. Secret material, credentials, prohibited personal data, and content that fails tenant policy MUST be rejected or deterministically redacted before persistence. Retrieved memory is untrusted reference data and MUST be delimited from system/tool instructions to reduce prompt-injection risk.

### 11.2 Retention policy

Each tenant MUST configure a versioned retention policy before activation. No indefinite implicit default is allowed. At minimum it defines:

- TTL/retention by memory scope and classification;
- tombstone retention;
- physical purge schedule;
- backup purge SLA;
- restore policy;
- legal hold behavior;
- audit retention and redaction.

Absent or invalid policy blocks activation and memory writes.

### 11.3 Tombstone-first deletion

Authorized deletion immediately:

1. changes status to `tombstoned`;
2. sets `tombstoned_at` and reason code;
3. removes content from active search indexes and backend materializations;
4. prevents get/search return;
5. appends lifecycle and authorization audit events.

Physical purge follows the configured retention policy. Backups MUST be marked for purge within the configured SLA. Restore MUST NOT resurrect tombstoned content without explicit HUMAN authority and a new audited revision.

A valid legal hold overrides expiry and physical purge, but never makes tombstoned content searchable or readable through normal memory APIs. `memory.legal_hold.apply`, `memory.legal_hold.release`, and `memory.purge.authorize` require an attributable HUMAN decision owner named by tenant policy; ordinary Agent/Leader membership never grants them. `memory.purge.execute` and `memory.purge.verify` require a still-current purge authorization bound to exact record revisions, hold state, retention policy hash, executor, and expiry. Explicit deny wins; active hold returns `LEGAL_HOLD_ACTIVE`; absent/stale authorization returns `PURGE_NOT_AUTHORIZED`.

The `tombstoned → purged` transition requires a purge manifest containing record/revision IDs, content hashes, primary/index/materialization disposition, backup purge deadline, policy revision, decision owner, and audit-chain event. The verifier MUST reconcile that manifest against primary storage, indexes, materializations, and backup inventory.

### 11.4 Status

```text
active
superseded
stale
archived
tombstoned
purged
```

`active` means retained as usable reference, never authoritative.

---

## 12. Audit Contract

Every allowed or denied operation emits an append-only event:

```json
{
  "event_id": "audit-1001",
  "audit_epoch": "2026-09",
  "sequence": 1001,
  "correlation_id": "corr-123",
  "decision_id": "authz-991",
  "tenant_id": "tenant-acme",
  "principal_id": "principal-hoi",
  "agent_id": "developer",
  "team_runtime_id": "dsh-root-session-id",
  "member_id": "implementer",
  "mission_id": "mission-017",
  "task_id": "task-042",
  "working_aip_id": "AIP-EXEC-042",
  "working_aip_hash": "sha256:...",
  "working_aip_readiness": "execution_ready",
  "working_aip_readiness_evidence_hash": "sha256:...",
  "task_workspace_id": "TASK-20260913-task-042",
  "task_execution_binding_hash": "sha256:...",
  "run_id": "run-042-02",
  "team_plan_revision": 9,
  "team_plan_approved_revision": 9,
  "team_plan_approval_hash": "sha256:...",
  "native_mission_approval_hash": null,
  "project_scope_id": "project-gat",
  "operation": "memory.get",
  "resource_type": "memory_record",
  "resource_id": "tenant-acme:mem-0081",
  "policy_revision": 12,
  "policy_snapshot_hash": "sha256:...",
  "membership_revision": 4,
  "membership_snapshot_hash": "sha256:...",
  "matched_rule_ids": ["rule-deny-17"],
  "selector_hash": "sha256:...",
  "capability_revision": "sha256:...",
  "decision": "deny",
  "reason_code": "POLICY_EXPLICIT_DENY",
  "outcome": "no_side_effect",
  "timestamp": "2026-09-13T00:00:00Z",
  "previous_event_hash": "sha256:...",
  "event_hash": "sha256:..."
}
```

Audit requirements:

- allow and deny attempts are recorded;
- raw memory content and secrets are excluded or redacted;
- `audit.read` is separately authorized;
- retention is versioned tenant policy;
- deletion of memory does not silently delete required security audit evidence.

### 12.1 Integrity protocol

- Partition key: `(tenant_id, audit_epoch)`; each partition begins with a signed `GENESIS` event naming the schema, policy revision, previous epoch head, and creation authority.
- Canonical bytes: RFC 8785 JSON Canonicalization Scheme over the event with `event_hash` omitted and UTF-8 encoding.
- Hash input is exactly ASCII domain prefix `GAT-AUDIT-V1`, one `0x00` separator, the **raw 32-byte SHA-256 digest** of the prior event, one `0x00` separator, then canonical event bytes. The event stores the result as lowercase 64-character hex with `sha256:` prefix. For a partition GENESIS, the prior digest is 32 zero bytes; `previous_epoch_head` remains a separately signed field in the canonical GENESIS event.
- Event hash: `SHA-256(ASCII("GAT-AUDIT-V1") || 0x00 || prior_digest_32_bytes || 0x00 || canonical_event_bytes)`.
- Append ordering: a per-partition monotonic `sequence` is allocated by one transactional compare-and-append operation; concurrent writers retry against the new head and cannot fork the accepted chain.
- Head anchoring: **every accepted event head** is synchronously committed, before the operation reports success, to a separately access-controlled append-only anchor/high-water store containing partition, epoch, sequence, and head hash. The event append and anchor compare-and-set form one recoverable commit protocol; incomplete commits fail closed and are reconciled before later operations. Startup and verification compare the local head/sequence with the anchored high-water record, so missing suffixes, rollback, fork, or truncation are detectable.
- Epoch rotation synchronously anchors both old and new heads. Retention or archival cannot remove the last anchor needed to prove the retained chain.

### 12.2 Audit-sink failure semantics

The operation and its audit append form one disposition boundary:

- `remember`, `revise`, `tombstone`, and lifecycle mutations fail closed with `AUDIT_APPEND_FAILED` and zero committed/visible domain mutation under §12.3 when the event cannot be committed.
- Allowed `search` and `get` fail closed before returning content when their allow-event cannot be committed.
- A denied operation still returns the non-disclosing denial if the primary audit sink is unavailable, but MUST synchronously append a minimal redacted denial to a separately provisioned emergency append-only sink. If neither sink accepts it, the adapter returns generic `SECURITY_SERVICE_UNAVAILABLE`, emits no content, performs no backend lookup/mutation, and raises an operator alert.
- `audit.read` and integrity verification fail closed when chain/head verification is unavailable or invalid.

### 12.3 Transactional mutation/audit protocol

Conservative MVP uses one adapter-owned transactional store for the MemoryRecord current projection, immutable revision history, idempotency disposition, audit intent/local chain event, and commit marker. It does not attempt distributed two-phase commit with an unrelated third-party memory database.

Mutation state machine:

```text
absent
  → prepared          # domain revision + audit intent written atomically, not visible
  → locally_committed # local audit event/chain head committed atomically
  → anchored          # every-head external anchor acknowledged
  → published         # domain revision becomes visible; response may succeed
```

Rules:

1. One transaction writes the prepared domain revision, idempotency result, audit intent, and expected prior heads; prepared data is fenced from reads/searches.
2. A compare-and-append transaction commits the local audit event/head or aborts the prepared mutation.
3. The exact head is synchronously anchored under §12.1.
4. Only after anchor acknowledgement may a transaction mark the domain revision `published` and return success.
5. Crash recovery scans prepared/locally-committed entries using idempotency key and fencing token: it completes a valid anchored publish or appends an abort outcome and leaves the prior domain revision visible.
6. “Zero mutation on audit failure” means zero **committed/visible domain mutation**; forensic prepared/abort records may remain and MUST be auditable.
7. Search/get never expose prepared/aborted revisions. Repeated requests return the durable idempotency disposition.

The conformance suite MUST inject crashes before/after prepare, local audit append, anchor acknowledgement, publish, and response delivery.

---

## 13. Package-Owned Gates and HUMAN Authority

### 13.1 Authority matrix

| Action | Agent/Leader | Council/Reviewer | HUMAN decision owner | Package/runtime |
|---|---|---|---|---|
| Analyze/recommend | Performs | Reviews/recommends | Informed | Provides tools |
| Dispatch within approved scope | Coordinates | No | Sets/limits authority | Enforces Team/tool policy |
| Task state proposal | Proposes | Reviews | Accepts when required | Persists authoritative state |
| Working AIP creation/use | Executes | Reviews evidence | Confirms hard gates/deviations | Owns AIP gate semantics |
| Re-plan/deviation | Proposes | Assesses | **Approves** | Records/enforces gate |
| Ordinary memory operation | Requests | May inspect | Sets policy | PDP decides per operation |
| Legal hold/purge authorization | Cannot authorize | May recommend/verify | **Authorizes exact transition** | PDP + fenced executor enforce/verify |
| Promotion/share | Cannot in MVP | Cannot approve | Future design owner | Tool absent/denies |
| Deliverable acceptance | Cannot self-accept | Recommends | **Accepts** | Records decision |
| Proposal approval | Cannot | Recommends | **Approves** | Records decision |
| Implementation activation | Cannot | Recommends | **Activates separately** | Enforces activation record |
| Merge/deploy | Cannot infer | Advises | **Authorizes** | Existing controls apply |

### 13.2 Decision routing fields

Mission, Task, AgentRun, review record, deviation record, acceptance record, and activation record MUST propagate:

```text
requested_by
decision_owner
report_to
escalation_route
```

### 13.3 Gate preservation

GAT MUST preserve wiki-first lookup, Working AIP, Task Workspace wiring, Truth/canonical change control, lint/finalization, and required independent review gates. Configuration cannot disable them. A denied package gate is final for that operation unless the owning package exposes an explicit HUMAN-authorized path.

---

## 14. Current DSH Mapping and Capability Boundary

The MVP is an adapter over current verified DSH capabilities, not a replacement Team runtime. This proposal inspected DSH revision `aeedf19995babaa28e35ca84624baff18a77a7d8`; implementation evidence MUST pin and re-run against its actual DSH revision rather than assuming compatibility.

| GAT concept/need | Current DSH type/tool evidence | Exact adapter mapping | Status |
|---|---|---|---|
| Native Team identity | `packages/experimental/gat-core/src/types.ts`: `TeamId(id: SessionId|string)` brands the root Session | `team_runtime_id = TeamId(root_session_id)`; logical GAT configuration ID stays separate | Native/current |
| Durable teammate identity | `TeamMemberSnapshot.id: SessionId`; `TeamMemberView.role/status` | Store `(agent_id, member_id, session_id)` in AgentRun; validate current roster before each dispatch/resume | Adapter binding |
| Task identity/state | `TeamTaskId`, `TeamTaskSnapshot.revision/status/ownerId/blockedBy/writeScopes` | Store `task_id` plus expected task revision; current Team task remains authoritative | Native + adapter revision check |
| Native Team-plan approval | `TeamView.planRevision/planPhase/planApproval`; `gat-tools.approvalFailure/readiness` rejects absent or stale exact-revision approval | Treat current native plan snapshot as authoritative for Team execution; bind revision/phase/approvedRevision/hash to AgentRun, PDP, selector, audit, preflight, spawn, resume, and tool admission | Native mandatory gate |
| Native TeamMission | `TeamMissionSnapshot` and exact-revision `TeamMissionApprovalSnapshot` exist, but inspected `gat-tools` does not prove they gate spawn/tool execution | Bind only when GAT Mission explicitly maps to a native Mission; native record/approval then wins. Otherwise record `native_mission_binding: none` and claim no enforcement | Conditional mapping, not current admission claim |
| Native Team spawn | `packages/experimental/gat-tools/src/index.ts` tool `spawn_teammate` accepts `name`, `description`, `prompt`, `context` | Pass only supported arguments; persist returned Session/member ID and observed runtime route | Native/current |
| Per-member provider/model/preset selection | Not exposed by current `spawn_teammate` tool contract | Reject requested override as `CAPABILITY_UNSUPPORTED`; no silent inheritance claim | Rejected in MVP |
| Reusable TeamDefinition independent of root Session | Not current native Team identity model | Configuration may describe desired slots, but materialization always records the actual root Session Team and memberships | Adapter-emulated config, not native identity |
| Canonical Task Workspace | AIWS `.ai-work/workspaces/{account}/{task_id}/` | `principal_id` maps through a HUMAN-ratified account registry to one canonical `account_id`; normalized path is joined below the fixed workspace root | Required integration |
| Working AIP readiness | AIWS package owns `not_ready` / `lite_ready` / `execution_ready` classification and applicability | Persist AIP path/hash plus package gate name/revision/readiness/evidence hash; non-trivial execution requires package-approved `execution_ready`; GAT never reimplements the classifier | Required native-package oracle |
| Generic MCP bridge | DSH guide: default-off client discovers and exposes raw `mcp__<server>__<tool>` tools; DSH does not own backend security | Hold the connection behind a package-only capability; raw `mcp__gat-partitioned-memory-mcp__*` schemas and execution are denied, and only GAT wrappers may call it | Native bridge + mandatory package guard |
| MCP Reference Memory example | One upstream JSONL graph with substring search and no complete namespace selector | Interoperability reference only; MUST NOT back Conservative MVP secure storage | Rejected as MVP backend |
| GAT substring/get/write/revise/tombstone | Not native DSH memory semantics | `gat-partitioned-memory-mcp` implements native physical partition and transactional contracts; unavailable until PoC/conformance PASS | Proposed package capability |
| Semantic retrieval | Not part of pinned topology | Reject `CAPABILITY_UNSUPPORTED`; no silent adapter/provider | Future |

`tenant_id` and `principal_id` MUST NOT be interpolated directly into filesystem paths. A HUMAN-ratified account registry maps `(tenant_id, principal_id)` to one canonical AIWS `account_id`. The adapter validates `account_id` and `task_id` against package grammars, rejects separators/dot segments/symlink escapes, resolves the canonical path under `.ai-work/workspaces/`, and verifies containment before access. Mapping collisions fail activation.

No DSH fork is required for Conservative MVP. Any future independent-session strategy or per-member routing requires a separate DSH capability proposal, compatibility plan, migration plan, and conformance evidence.

---

## 15. Runtime Flow

```text
HUMAN supplies Mission/Task and authority routing
  → resolve Tenant, Principal, ProjectScope, current DSH Team/member
  → package-owned wiki/source preflight
  → obtain package-owned Working AIP readiness result (`execution_ready` required)
  → create/reuse exactly one canonical Task Workspace for the fixed Task identity
  → read exact current native Team-plan approval; bind native Mission approval only when mapped
  → HUMAN resolves required hard gates
  → create AgentRun bound to Task/AIP/Workspace + readiness + native approvals + policy revisions
  → execute within AIP scope
      → each memory/lifecycle operation reads a fresh authoritative snapshot and calls PDP
      → explicit deny/default deny applied; no decision/result cache
      → select exactly one physical `gat-partitioned-memory-mcp` partition
      → authorized substring retrieval or transactional same-scope mutation
      → commit/anchor/publish audit disposition under §12.3
  → write runtime findings/evidence to Task Workspace
  → independent review
  → package-owned lint/finalization
  → HUMAN accepts output if satisfied
  → separate HUMAN activation decision before rollout
```

Memory outage may degrade optional reference assistance. It MUST NOT corrupt SoT/task state, bypass Working AIP, widen authorization, or fabricate remembered information. Audit unavailability follows §12.2: no content exposure or mutation may proceed without its required audit disposition.

---

## 16. Threat Model Gate

Before implementation, the GAT Security Owner MUST produce `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md`, bound to the proposal hash and reviewed by an independent Security Reviewer. The HUMAN decision owner accepts or rejects the threat-model gate.

The artifact MUST cover assets, trust boundaries, actors, tenant/principal confusion, retrieved-memory prompt injection, authorization/revocation races, physical namespace escape, backend-materialization/count/timing/ranking leakage, audit rollback/truncation, backup/restore, malicious tool arguments, and DSH native-Team versus adapter drift. Each threat maps to a control, conformance vector, residual risk, owner, and activation disposition. Missing or unaccepted threat-model evidence blocks activation.

---

## 17. WebUI Boundary

Broad WebUI is post-MVP. The security vertical slice MAY expose a minimal operator/evidence view showing:

- AgentRun binding;
- Working AIP and Task Workspace references;
- policy/membership revisions;
- authorization decision and reason code;
- redacted audit-chain verification;
- memory status and tombstone state.

The UI MUST apply the same authorization as APIs. Leader status does not grant access to private Desk content or metadata. Counts, filters, timing, backend-state indicators, and ranking metadata MUST not disclose unauthorized records.

Future Agent/Team/Mission/Desk browsing requires a separate UI threat model and acceptance vectors.

---

## 18. Executable Conformance Contract

The implementation package MUST own a versioned vector file and verifier. Proposed required interface:

```text
pnpm --filter @deepseek-ai/dsh-gat test:conformance -- \
  --vectors docs/conformance/gat-conservative-mvp-v1.json \
  --evidence .artifacts/gat-conformance/<implementation-hash>/
```

The exact package/path may change only in a reviewed proposal revision. Evidence MUST bind:

- proposal hash;
- implementation commit/hash;
- vector file hash;
- policy and membership revisions plus immutable snapshot hashes/rule IDs;
- Task/Working-AIP/Task-Workspace binding and package readiness evidence hashes;
- native Team-plan approval and conditional native TeamMission approval hashes;
- DSH version/hash;
- MCP bridge, partitioned backend topology, selector, and capability revisions;
- backend/test environment;
- command, exit code, timestamps, and raw verifier output.

A PASS requires every vector to pass and all declared no-side-effect assertions to be proven. Missing evidence is not PASS.

### 18.1 Pinned minimum vectors

| ID | Initial state and operation | Exact expected disposition | Required absence/evidence |
|---|---|---|---|
| GAT-AUTH-001 | No allow rule; `memory_search("alpha")` | deny `NO_ALLOW_RULE` | zero backend search/read; one denied audit event |
| GAT-AUTH-002 | Allow and explicit deny both match `memory_get(M1)` | deny `POLICY_EXPLICIT_DENY` | no record content; decision binds current revisions |
| GAT-AUTH-003A | Trusted run is principal A; LLM argument claims principal B | deny `BINDING_INVALID` | no namespace lookup; non-disclosing response |
| GAT-AUTH-003B | Trusted principal is valid but resource names another ProjectScope | deny `RESOURCE_SCOPE_MISMATCH` | no namespace lookup; non-disclosing response |
| GAT-AUTH-004 | No allow rule exists; attempt `memory_remember` into each scope | deny `NO_ALLOW_RULE` | zero new records/revisions/index entries; denied audit event |
| GAT-AUTH-005 | Explicit deny targets `memory_revise` and `memory_tombstone` on an existing record | deny `POLICY_EXPLICIT_DENY` | record, history, index, and tombstone state byte-identical |
| GAT-PREFILTER-001 | Allowed tenant A search while tenant B has a matching secret fixture | allow with tenant-A selector | backend trace proves physical tenant-A partition only; zero tenant-B reads |
| GAT-PREFILTER-002 | Same tenant/project has another principal Desk with matching secret | allow current principal Desk only | selector equals exact `project-desk` partition key; zero other-principal backend reads |
| GAT-PREFILTER-003 | Same tenant/project has peer Task partitions with matching secrets | allow only explicitly authorized Task partition | backend trace proves zero reads from every non-selected Task partition |
| GAT-MCP-RAW-001 | Agent attempts direct `mcp__gat-partitioned-memory-mcp__search/get/write` call | deny `RAW_MCP_TOOL_NOT_ADMITTED` at schema/admission guard | raw tool absent from Agent-visible schema; forced execution yields zero MCP/backend/PDP side effects except denial audit |
| GAT-REV-001 | Allow at revision 4; revoke to 5; reuse the same session | deny `POLICY_REVISION_STALE`, then current-policy denial | fresh authoritative snapshot read; no prior decision reuse; revocation evidence |
| GAT-PROMO-001 | Attempt Task→Desk, Desk→Agent, or cross-project copy | deny `PROMOTION_DISABLED` | source unchanged; no target record; audit denial |
| GAT-PLAN-001 | Native Team execution has no `planApproval` for current plan revision | deny `TEAM_PLAN_APPROVAL_MISSING` | no spawn/resume/memory/backend effect; denial binds current `planRevision` |
| GAT-PLAN-002 | Native Team `approvedRevision` differs from current `planRevision` | deny `TEAM_PLAN_APPROVAL_STALE` | no execution/backend effect; exact revisions audited |
| GAT-MISSION-001 | GAT Mission explicitly maps to native TeamMission but its approval is stale | deny `NATIVE_MISSION_APPROVAL_STALE` | no claim that unmapped Mission is natively gated; mapped execution stops |
| GAT-AIP-001 | Start non-trivial AgentRun without Working AIP | deny `WORKING_AIP_REQUIRED` | no AgentRun execution side effect |
| GAT-AIP-002 | Package readiness oracle returns `not_ready` | deny `WORKING_AIP_NOT_EXECUTION_READY` | no execution/backend effect; readiness evidence hash audited |
| GAT-AIP-003 | High-impact/non-trivial task presents `lite_ready` | deny `WORKING_AIP_LITE_INAPPLICABLE` | no execution/backend effect; package applicability result is oracle |
| GAT-WS-001 | AgentRun bound to an execution that already has a Task Workspace tries to create a second | deny `TASK_WORKSPACE_CONFLICT` | exactly one Task Workspace remains |
| GAT-EXEC-001 | Re-plan changes steps/scope through the same Working AIP and fixed Task Workspace | allow same execution identity | AIP Re-plan Log records change; no new Task Workspace or task identity |
| GAT-EXEC-002 | Request attempts to bind a different Task Workspace to the same `task_id` | deny `TASK_WORKSPACE_CONFLICT` | original write-once pointer remains; no second workspace |
| GAT-EXEC-003 | New package-owned Task supersedes old Task and receives a new Workspace | allow only with new `task_id` and `supersedes_task_id` | old Task/Workspace retained for provenance; identities never alias |
| GAT-EXEC-004 | AgentRun uses stale AIP/Workspace/task tuple | deny `TASK_EXECUTION_BINDING_STALE` | zero execution/memory side effects; denial audited |
| GAT-SEARCH-001 | Authorized fixture with pinned normalization/order | exact ordered record IDs from literal substring match | no unauthorized/tombstoned IDs; stable rerun output |
| GAT-SEARCH-002 | Request semantic search against substring-only provider | error `CAPABILITY_UNSUPPORTED` | no provider substitution or third-party call |
| GAT-GET-001 | Guess unauthorized existing ID and nonexistent ID | same external status class/shape | no content/count leak; separate redacted audit reasons allowed |
| GAT-WRITE-001 | Retry remember with same idempotency key | same successful disposition | exactly one record and one logical mutation |
| GAT-REVISION-001 | Two revisions use same expected revision | one success; one conflict | final revision increments once |
| GAT-DELETE-001 | Authorized tombstone then search/get | success then non-return | search index/materialization invalidated; tombstone + audit preserved |
| GAT-DELETE-002 | Expired/tombstoned record under legal hold, then release and purge | deny `LEGAL_HOLD_ACTIVE` before release; exact authorized purge after release/deadline | purge manifest reconciles primary/index/materialization/backup inventory |
| GAT-LIFECYCLE-001 | Agent/Leader without HUMAN lifecycle authority attempts hold apply/release | deny `LIFECYCLE_ACTION_DENIED` | hold state unchanged; denial/audit binds policy and actor |
| GAT-LIFECYCLE-002 | Purge execute uses absent, stale, wrong-revision, or expired authorization | deny `PURGE_NOT_AUTHORIZED` | record/tombstone/backups unchanged; no purge side effect |
| GAT-AUDIT-001 | Reconstruct one allowed and one denied operation | chain verifies and decisions are reproducible | execution/readiness/native-approval/selector/capability and immutable policy evidence present; raw secret absent |
| GAT-AUDIT-002 | Modify/delete an interior audit event | verifier fails non-zero | identifies broken chain segment |
| GAT-AUDIT-003 | Remove chain suffix after a checkpoint | verifier fails non-zero | anchored head/sequence detects tail truncation |
| GAT-AUDIT-004 | Primary audit sink fails during allowed get/search/write | `SECURITY_SERVICE_UNAVAILABLE` for read or `AUDIT_APPEND_FAILED` for mutation | zero content/mutation/backend work beyond defined boundary; operator alert |
| GAT-AUDIT-005 | Primary sink fails during denial; emergency sink available/unavailable | original non-disclosing denial with emergency event, else generic unavailable | zero content/backend read/mutation; emergency evidence or alert |
| GAT-TXN-001 | Crash before/after prepare, local audit append, anchor, publish, and response | recovery returns one durable idempotency disposition | no prepared/aborted revision visible; exactly one published revision or prior revision only |
| GAT-TXN-002 | Anchor fails after local commit | deny `AUDIT_APPEND_FAILED` | zero committed/visible domain mutation; fenced recovery/abort evidence retained |
| GAT-RESTART-001 | Restart adapter after write, revoke, and tombstone | restored current revisions and denial/tombstone behavior | no stale authorization state or tombstoned content resurrection |
| GAT-TENANT-001 | Same record suffix/agent ID in two tenants | isolation maintained | no cross-tenant result, count, backend-state, or audit access |
| GAT-DESK-001 | Same agent/project under two principals | distinct Desk IDs and exact principal-bound selectors | backend trace proves zero reads from the other principal partition; no cross-principal exposure |
| GAT-ACT-001 | Tests pass but Activation Manifest is missing/stale/incomplete or lacks separate HUMAN activation | implementation remains inactive | activation attempt denied and audited against exact missing/stale manifest item |

### 18.2 Security acceptance thresholds

- Unauthorized content exposure: **zero records/bytes**.
- Unauthorized mutation: **zero persisted target changes**.
- Revocation: effective before the next operation; stale-revision request MUST be denied.
- Audit reconstruction: every tested allow/deny maps to one decision and one valid chain event.
- Test repeatability: pinned fixtures produce identical dispositions and substring result ordering.

Performance targets require measured deployment-specific values and HUMAN approval; they MUST NOT be invented by this proposal.

---

## 19. MVP Implementation Order

1. Freeze identifiers, invariants, threat model, and policy schemas.
2. Integrate package-owned Working AIP readiness and fixed canonical Task Workspace identity.
3. Bind current DSH Team-plan approval and conditional native TeamMission mapping without a DSH fork.
4. Prove the adapter-owned partitioned MCP topology and physical selector non-bypass.
5. Implement deny-by-default authorization with fresh execution/readiness/approval/policy snapshots and no decision/result cache.
6. Implement the single-store transactional record/revision/idempotency/audit protocol, substring retrieval, tombstone, legal hold, and purge.
7. Implement synchronous audit-head anchoring, recovery, and integrity verification.
8. Run the complete security vertical-slice suite, including crash injection and restart.
9. Obtain independent review bound to exact hashes and build the complete Activation Manifest.
10. Obtain HUMAN proposal acceptance and a separate manifest-bound activation decision.
11. Only then consider minimal evidence UI; broad WebUI remains future work.

---

## 20. Explicitly Deferred Work

The following are not MVP and MUST NOT appear in MVP flows or acceptance claims as available behavior:

- semantic/vector/embedding retrieval;
- transparent alternate or third-party provider selection;
- cross-scope memory promotion, sharing, or copying;
- autonomous long-term learning;
- Team-global or `mission-shared` memory until authoritative Mission membership/revision semantics exist;
- decision/result caching until the complete execution/readiness/native-approval identity is safely keyed and tested;
- upstream MCP Reference Memory as a secure multi-tenant backing store unless a future native-selector topology is proven;
- reusable native TeamDefinition independent of root Session;
- independent-session orchestration;
- per-member provider/model/preset/skills/tools/credential overrides not exposed by current DSH contracts;
- sophisticated ranking or task-type taxonomy;
- broad Agent/Team/Desk WebUI.

Each requires its own reviewed proposal revision, threat model, compatibility/migration plan, acceptance vectors, and HUMAN approval.

---

## 21. Traceability to Council Findings

| Finding | Closure in this revision | Conformance evidence |
|---|---|---|
| F1 Workspace conflict | §§2.4–2.5, 3, 4.1, 5 | GAT-WS-001, GAT-DESK-001 |
| F2 Working AIP omitted | §§2.7, 3.3, 4.5, 13–15 | GAT-AIP-001–003, GAT-WS-001 |
| F3 Authorization under-specified | §8 | GAT-AUTH-001–005, GAT-PREFILTER-001–003, GAT-REV-001 |
| F4 Unsafe promotion | §§2.8, 6, 9 | GAT-PROMO-001 |
| F5 Semantic mismatch | §10 | GAT-SEARCH-001/002 |
| F6 Memory identity/provenance | §7 | schema/history validation plus GAT-TENANT-001/GAT-DESK-001 |
| F7 Audit reconstruction | §12 | GAT-AUDIT-001–005 |
| F8 Lifecycle/privacy/revocation | §§8.4, 11–12 | GAT-REV-001, GAT-DELETE-001/002, GAT-LIFECYCLE-001/002, GAT-TXN-001/002, GAT-RESTART-001 |
| F9 DSH mapping | §14 | GAT-PLAN-001/002, GAT-MISSION-001, topology PoC evidence bound by §18 |
| F10 Executable acceptance | §18 | package-owned vector suite and persisted output |
| F11 HUMAN boundary | §§0, 13, 15 | GAT-ACT-001 plus decision records |

### 21.1 Rereview v3 dispositions applied selectively

| Rereview item | Disposition | Result |
|---|---|---|
| R1 native approval mapping | Accept with correction | §14 binds proven native Team-plan gate; native TeamMission mapping is conditional and not misrepresented as current spawn enforcement; GAT-PLAN/MISSION vectors |
| R2 Workspace replacement | Accept | §§3.3/4.5 keep one fixed Workspace per Task; new Workspace requires new canonical Task; GAT-EXEC-001–004 |
| R3 physical selector feasibility | Accept with correction | §§8.3/10.1 pin adapter-owned partitioned GAT MCP topology; upstream reference server rejected as MVP backing store |
| R4 atomic audit/mutation | Accept with correction | §12.3 defines zero committed/visible mutation protocol and crash recovery; GAT-TXN vectors |
| R5 AIP readiness | Accept with correction | §§8/14 bind package-owned readiness oracle rather than duplicating it; GAT-AIP-002/003 |
| R6 execution identity/cache | Accept | Full tuple binds PDP/audit/history; decision/result cache removed from MVP |
| R7 mission-shared authority | Accept by narrowing | `mission-shared` removed from MVP and deferred instead of inventing MissionMembership |
| R8 lifecycle/audit/activation | Accept selectively | Explicit lifecycle actions, content-addressed reconstruction evidence, and single hashed Activation Manifest; no redundant full decision snapshot |

The council protocol `insufficient_evidence` outcome is retained as provenance, not treated as architecture authority. Its `BlockingIOError` lint attempt is inconclusive and is not used as proposal evidence.

External advisories are addressed as follows: retrieved-memory injection (§11.1), UI privacy (§17), runtime authorization drift (§8 and one adapter path), side channels (§8.5), and security-vertical-slice sequencing (§1 and §19).

---

## 22. Final Mental Model

```text
Tenant + authenticated Principal
              │
              ▼
        ProjectScope ───────────────► SoT references / policy
              │                              │
              ├── principal-bound AgentDesk │ authoritative basis
              │                              ▼
              └── Mission → Task → Working AIP
                                  → one canonical Task Workspace
                                             │
AgentDefinition + current DSH TeamMembership │
                    └──────────────► AgentRun
                                             │
                                             ▼
                                    GatMemoryAdapter
                        readiness + native-plan gate + authorization
                                             │
                                             ▼
                            gat-partitioned-memory-mcp + audit anchor
                                  agent / project-desk / task
                                             │
                                      reference assistance
                                             ▼
                                    governed task execution
                                             │
                                  review → HUMAN acceptance
                                             │
                              separate HUMAN activation decision
```

SoT tells the agent what is authoritative. The Working AIP controls non-trivial execution. The Task Workspace holds runtime state. Skills provide capabilities. Memory and Desk provide scoped reference assistance. Current DSH supplies the concrete Team/session runtime. HUMAN retains important decision authority.

---

## 23. Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| 1 | Before 2026-09-13 | Council `BLOCKED` | Initial broad proposal |
| 2 | 2026-09-13 | Superseded | Applied HUMAN-selected Conservative MVP and addressed F1–F11 |
| 3 | 2026-09-13 | Inactive; exact-hash re-review required | Critiqued rereview R1–R8; selectively added proven Team-plan/readiness bindings, fixed Workspace identity, pinned adapter-owned partitioned MCP topology, transactional audit/mutation recovery, removed cache and mission-shared from MVP, expanded lifecycle/audit evidence, and consolidated the Activation Manifest |
