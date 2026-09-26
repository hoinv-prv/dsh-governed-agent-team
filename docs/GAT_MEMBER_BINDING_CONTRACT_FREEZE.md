# GAT Member-Binding and DSH Lifecycle Contract Freeze

**Status:** Frozen design contract for EXEC-B and EXEC-C; not runtime activation authority
**Version:** 1.0-draft-freeze
**Date:** 2026-09-26
**Driving work:** AIP-EXEC-021
**Baseline:** standalone `6a8e4f62a30e05cf1e36950d74245b707f5394fe` plus the controlled EXEC-A merge; DSH `aeedf19995babaa28e35ca84624baff18a77a7d8` plus the pinned GAT working-tree files recorded by EXEC-A
**Normative post-sync package manifest:** `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/post-sync-package-sha256.txt` — SHA-256 `38274d6c1b80e16ea143b271ae31a05a7fce262fa98b5d242cb74c4ce79ad2ba`

## 1. Purpose and normative language

This document freezes the semantic boundary that lets two later work packages proceed independently:

- **EXEC-B** — GAT member specs, attachments, binder registry, persistence, and conformance tests.
- **EXEC-C** — DSH continuable-child materialization separated from initial inbox admission.

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` are normative. Exact API names may change, but the ownership, ordering, durability, failure, and authority rules below may not change without a reviewed contract revision.

This document does not implement member binding, the DSH two-phase lifecycle, Durable Agent integration, or the complete mission lifecycle.

## 2. Frozen decisions

| ID | Decision |
|---|---|
| CF-01 | GAT remains the sole authority for Team identity, roster phase, member Session ownership, mission, task, mailbox, work, and Team readiness. |
| CF-02 | DSH owns child materialization, Session/inbox logging, prompt assembly, model execution, and the primitive that admits the first inbox item. |
| CF-03 | Capability services such as Durable Agent own their persistent domain data; GAT stores only bounded opaque attachment records. |
| CF-04 | V1 attachments are **required-only**. A declared attachment must prepare, bind, and recover successfully; optional degraded binding is unsupported. |
| CF-05 | `team/member` moves from event payload v2 to v3. The adjacent v2 replay adapter supplies an empty attachment list; unknown versions fail closed. |
| CF-06 | One initializer returns normalized member specifications. GAT core validates/prepares the complete roster and owns provisioning; duplicate initializer registration fails deterministically. |
| CF-07 | DSH must expose materialize-without-admit and explicit exactly-once initial admission. Existing consumers retain a compatibility `startContinuable()` wrapper. |
| CF-08 | Team-enabled execution is Team-exclusive. External delegation is denied by executor-enforced capability metadata with a compatibility name deny-list fallback. |
| CF-09 | Target simple-mode authorization is one exact, current, host-attested HUMAN mission authorization. Lead/model identity alone is not HUMAN provenance. |
| CF-10 | Executable tasks have one authority: the canonical Team task board. Tasks carry `missionId`; missions retain task references/revision metadata rather than mutable duplicate task snapshots. |

## 3. Ownership and non-authority boundaries

| Concern | Authority |
|---|---|
| Team identity, enabled state, immutable member name, lifecycle phase, child ownership | GAT |
| Mission authorization, canonical tasks/DAG, assignment, mailbox, work reports | GAT |
| Reserved child materialization, initial inbox persistence, model admission | DSH subagent/Session runtime |
| Attachment payload semantics and member-scoped capability resources | Registered binder/capability service |
| Persistent Durable Agent profile, SOUL, memory, working artifacts | Durable Agent service |
| Raw workspace declaration parsing and cross-domain projection | Selected initializer adapter/integration package |

A binder MUST NOT create members; mutate roster, mission, task, mailbox, work, or approval state; grant filesystem/tool authority; or receive unrestricted Team mutators. GAT supplies only the exact member scope and the bounded values necessary for the callback.

A workspace declaration is input, not authority. Recovery MUST use the durable member snapshot and MUST NOT re-read a mutable declaration to redefine an enabled roster.

## 4. Normalized initialization contract

The semantic values are:

```ts
interface TeamMemberSpec {
  name: string
  description: string
  initialTask: ContentBlock[]
  context: 'fresh' | 'fork'
  continuationProvider: string
  agentOptions?: AgentOptions
  attachments?: TeamMemberAttachmentRequest[]
}

interface TeamInitialization {
  source: string
  diagnostics: string[]
  members: TeamMemberSpec[]
}

type TeamInitializer = (
  lead: Agent,
  signal: AbortSignal,
) => Promise<TeamInitialization>
```

The initializer adapter owns raw declaration parsing. GAT core MUST receive normalized values only. Before creating the first child, GAT MUST:

1. call exactly one initializer;
2. validate the complete roster and every generic attachment bound;
3. resolve every continuation/model route;
4. resolve every `(binderId, protocolVersion)` registration;
5. run all binder `prepare()` operations successfully;
6. detach/clone the exact returned `PreparedAttachment.attachment` values; revalidate plain JSON, JCS record/aggregate bytes, depth, nodes, strings, ids, versions, and uniqueness; compute `payloadSha256`; and construct the exact immutable records to persist;
7. abort every successful prepared lease in reverse order, with zero new member rows and zero child Sessions, if prepare or returned-output validation fails.

The persisted payload MUST be exactly the detached canonical value returned by `prepare()`. A binder cannot substitute process-local `Prepared` state, mutate the value after validation, or defer generic bounds until replay.

The existing GAT-only loader and built-in roster remain a default adapter. A DSH integration composition may replace that adapter, not run beside it.

## 5. Attachment record contract and fixed V1 bounds

```ts
interface TeamMemberAttachmentRequest {
  binderId: string
  protocolVersion: number
  required: true
  payload: JsonValue
}

interface TeamMemberAttachmentRecord {
  binderId: string
  protocolVersion: number
  required: true
  payload: JsonValue
  /** Lowercase SHA-256 hex of the RFC 8785 canonical payload bytes. */
  payloadSha256: string
}
```

V1 generic validation is fixed as follows:

| Limit | Value |
|---|---:|
| Attachment records per member | 8 |
| UTF-8 canonical JSON bytes per complete record | 65,536 |
| UTF-8 canonical JSON bytes for all member records | 262,144 |
| Maximum JSON depth | 16 |
| Maximum JSON nodes across all records | 4,096 |
| Maximum UTF-8 bytes in any string value | 16,384 |
| Binder id length | 64 ASCII characters |

Additional rules:

- `binderId` matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`, is at most 64 ASCII characters, and is unique within a member.
- `protocolVersion` is a positive safe integer.
- `required` MUST equal `true` in V1; `false` is rejected rather than silently degraded.
- Values are plain acyclic JSON only: null, booleans, finite numbers, strings, arrays, and plain string-keyed objects. `undefined`, bigint, functions, symbols, non-finite numbers, class instances, accessors, and cyclic graphs are rejected.
- Canonical bytes use RFC 8785 JSON Canonicalization Scheme (JCS), including its property ordering and ECMAScript number rendering (`-0` canonicalizes as `0`). A record's byte bound includes its entire envelope. The total byte bound is the UTF-8 length of the JCS array containing all records.
- Root depth is zero; each array element or object property value adds one edge. Every scalar, array, and object value counts as one node. Object keys do not add nodes, but the 16,384-byte string bound applies independently to every key and string value. Boundary values are accepted; one unit above is rejected.
- `payloadSha256` is computed from the JCS payload bytes and verified on replay. Persistence guarantees canonical value plus digest integrity, not preservation of the declaration's original lexical bytes or key order.
- Bounds apply before the provisioning event is appended.
- GAT never interprets or exposes payload semantics. Only the matching binder validates domain content.

## 6. Binder registry and callback contract

The semantic port is:

```ts
interface PreparedAttachment<Prepared = unknown> {
  attachment: JsonValue
  value: Prepared
  /** Idempotent cleanup until ownership transfers to a successful binding. */
  abort(signal: AbortSignal): Promise<void>
}

interface TeamMemberBinder<Prepared = unknown> {
  readonly id: string
  readonly protocolVersion: number
  prepare(input: BinderPrepareInput, signal: AbortSignal): Promise<PreparedAttachment<Prepared>>
  bind(
    input: BinderBindInput,
    attachment: JsonValue,
    prepared: Prepared,
    signal: AbortSignal,
  ): Promise<DisposableBinding>
  recover(
    input: BinderRecoverInput,
    attachment: JsonValue,
    signal: AbortSignal,
  ): Promise<DisposableBinding>
}

interface DisposableBinding {
  closeAdmission(): void
  settle(signal: AbortSignal): Promise<void>
  release(signal: AbortSignal): Promise<void>
}
```

Registry rules:

- One `(binderId, protocolVersion)` has at most one live registration.
- In-process registration replacement/removal is rejected while any projected durable member references it, including inactive members. On a later process start an absent registration is permitted only to report the member unavailable; it never permits execution.
- Prepare order is deterministic. Every successful prepared lease is either transferred exactly once into a successful binding or aborted exactly once in reverse order. Later prepare failure, cancellation, roster abort, bind failure, and failure before ownership transfer all abort unconsumed leases.
- Install order is deterministic; release order is the exact reverse.
- GAT owns cancellation, one total lifecycle deadline, callback serialization, live-generation identity, and safe error redaction.
- Binding installation is exactly once per member Agent generation.
- A protocol change to ordering, durability, active commit timing, callback authority, or failure semantics requires a new protocol version.
- Additive optional metadata/capability discovery may remain within a version only when old participants preserve identical safety behavior.

## 7. DSH two-phase continuable contract

DSH MUST provide an opaque reserved activation with semantics equivalent to:

```ts
const reserved = await subagents.materializeContinuable(specWithoutInitialPrompt)
// Child exists in `materialized`; no initial inbox and no request is runnable.
await bindAll(reserved.memberScope)
await installScopedContributions(reserved.memberScope)
const messageId = await reserved.persistInitialPrompt(initialTask, idempotencyKey, signal)
// State is `inbox-persisted`; the item is durable but quarantined and cannot wake the runner.
await gat.commitMemberActive()
await reserved.activate(signal) // sole transition that releases the item and may wake model work
```

Frozen handle states and errors:

```text
materialized -> inbox-persisted -> activated
      |               |
      +-----> aborted <+
activated -> disposed
aborted   -> disposed
```

- Invalid state transitions fail with stable `CONTINUABLE_STATE_CONFLICT`.
- Reusing an initial-prompt idempotency key with different content fails with `CONTINUABLE_ADMISSION_CONFLICT`; the same content returns the original message id.
- Calls after abort/dispose fail with `CONTINUABLE_CLOSED`.
- Provider/materialization failure is `CONTINUABLE_MATERIALIZE_FAILED`; durable inbox persistence failure is `CONTINUABLE_PERSIST_FAILED`; wake/activation failure is `CONTINUABLE_ACTIVATE_FAILED`.

Required invariants:

1. GAT durably reserves the child id in the provisioning member before materialization.
2. Materialization creates no initial user inbox item and causes zero model requests.
3. The reserved handle exposes only bounded operations and the exact child scope; it does not accept arbitrary GAT callbacks inside subagent internals.
4. `persistInitialPrompt` is explicit, idempotent, and persist-only. It creates at most one quarantined durable item and never wakes a runner.
5. `activate` is the sole release/wake point and is legal only after the durable GAT active commit. Repeated successful activation is idempotent; conflicting/concurrent state changes fail with no second request.
6. Abort after inbox persistence appends a durable cancellation/tombstone for the quarantined item before disposal; recovery never executes it.
7. If the active commit succeeds but runtime activation fails, the durable member remains active but runtime-unavailable. Recovery re-establishes bindings/contributions and idempotently activates the existing item; it does not create another inbox item.
8. Cold recovery can materialize a child and inspect persisted activation state without releasing inbox or mailbox work until all required `recover()` calls succeed.
9. The legacy `startContinuable()` wrapper performs materialize, persist, and activate in order and preserves existing behavior for unrelated consumers.

## 8. Provisioning, failure, recovery, and disposal

### 8.1 Success order

```text
validate complete roster and attachment requests
  -> prepare every route and binder
  -> detach/revalidate returned attachments and construct JCS digests/records
  -> append/flush member v3 provisioning snapshot with immutable attachments
  -> materialize reserved child with no inbox/model admission
  -> bind required attachments in deterministic order
  -> install required GAT/binder scoped contributions
  -> persist exactly one quarantined initial inbox item
  -> append/flush active member snapshot
  -> publish runtime readiness
  -> activate/release the persisted item and only then permit model work
```

`active` implies every required live binding and scoped contribution is installed for the current Agent generation. No model request may begin merely because the inbox item is durable.

### 8.2 Failure edges

Before the durable active commit:

```text
close binder admission
  -> tombstone any quarantined initial item
  -> abort unconsumed prepared leases in reverse order
  -> settle and release successful bindings in reverse order under the shared deadline
  -> dispose the reserved child
  -> append/flush the durable failed member edge with a safe diagnostic
  -> retain immutable name reservation and member-limit accounting
```

A prepare failure before the provisioning event creates no member row. Once a v3 provisioning row exists, every later failed snapshot retains the exact same attachment records and digests; attachments are never invented for a pre-provisioning failure.

After the durable active commit, publish/activation failure does not rewrite the member to failed and never causes `recover()` to double-install the same generation:

1. **Live-retry path:** if the reserved handle, bindings, and scoped contributions remain valid in the current generation, GAT closes its outer execution gate but does not call binding `closeAdmission`, release, reinstall, or `recover()`. It retries only the incomplete publish/`activate` transition; activation remains idempotent.
2. **Reconstruct path:** if the handle/binding is invalid, cleanup is required, the process restarted, or generation ownership is uncertain, GAT closes admission, settles/releases contributions and bindings, disposes the old handle, advances the Agent generation, then materializes and calls `recover()` exactly once for the new generation before idempotent activation of the existing quarantined item.

The generation and selected path are observable in runtime readiness. GAT MUST NOT silently retry as an unattached or non-durable member.

### 8.3 Recovery

Recovery MUST:

1. project the v2/v3 member record and persisted activation state;
2. validate every persisted required binder id/version, digest, and generic bound;
3. verify the persisted child descriptor, parent, and continuation provider;
4. materialize/cold-resume without releasing inbox, mailbox, or model work;
5. call every `recover()` in deterministic order and reinstall required scoped contributions;
6. publish binding readiness;
7. idempotently release an already-persisted, non-tombstoned initial child inbox item—never re-admit or duplicate it;
8. separately reconcile and deliver Team mailbox messages through the existing mailbox dedupe keys.

Missing/incompatible binders, corrupt/oversized attachments, or recovery failure leave the member unavailable. They do not rewrite the attachment, reload the workspace declaration, or fall back to unbound execution.

### 8.4 Disposal

One total deadline, derived from GAT's configured disposal timeout, covers admission cutoff, settlement, reverse release, child drain, and registry-effect cleanup. Every `settle`, prepared `abort`, and binding `release` receives the remaining-deadline `AbortSignal` and MUST be idempotent.

On deadline expiry, GAT aborts the shared signal, detaches the binding from all runtime authority, records a bounded safe leak/timeout diagnostic, and continues best-effort child drain and registry cleanup; it does not wait indefinitely. Persistent external capability data survives Team and Session disposal. A timed-out external resource may require operator cleanup, but it cannot retain tool, prompt, mission, or member execution authority.

## 9. Event migration and compatibility

`team/member` payload v3 adds immutable attachment records to every provisioning/active/failed member snapshot.

- New writes use v3 only after the format registration and projection ship together.
- The adjacent v2 adapter maps a valid v2 member to v3 semantics with `attachments: []`.
- The adapter is explicit and covered by replay fixtures; it does not reinterpret payload semantics.
- Unknown event or binder protocol versions fail before member execution.
- Attachments remain opaque and canonically value-preserved with a verified JCS SHA-256 digest across GAT migrations unless the owning binder supplies an explicit protocol adapter.
- Binder protocol version is independent of GAT package version and Team log version.

## 10. Mission authorization and canonical task authority

The synchronized EXEC-A baseline immediately approves a newly created mission and simple mode skips the legacy Team-plan approval gate. That baseline behavior is **not yet** the target authorization contract because the current Lead Agent credential does not prove a HUMAN authored the mission.

The target simple-mode contract is:

- DSH host supplies an authenticated HUMAN admission action/provenance that model arguments cannot forge.
- Model/Team tool creation may create a draft but cannot self-authorize it.
- Every non-repair execution dispatch binds exactly one `teamId + missionId + missionRevision` authorization.
- Missing, ambiguous, wrong-Team, stale, closed, revoked, or non-HUMAN-authorized missions deny before side effects.
- Legacy `simpleMode: false` retains the exact current-plan HUMAN approval gate; a mission cannot bypass it.
- Structural mission/task mutation invalidates the bound authorization until the required exact revision is authorized.

The authoritative carrier is a GAT-issued opaque execution lease stored in the exact Agent/Session scope, never a model-supplied tool argument and never “the first/current item” inferred from list order. The lease contains Team id, mission id, mission revision, authorization-event id/digest, issuance generation, and revocation generation. GAT revalidates it against the canonical projection immediately before every effectful dispatch.

Task-bound work derives its lease only from the claimed canonical task's immutable `missionId` plus the mission revision authorized for that task-plan revision. A Lead operation not bound to a task requires the same host-issued scope lease. Multiple eligible authorizations, missing task association, or any revision/generation mismatch is ambiguous and denied.

The exhaustive V1 mission-exempt capability classes are: read-only Team/workspace inspection; HUMAN questioning; Team view/list/get; Session Enable; Lead roster establishment with its separate host-attested member-add approval; structural task create/edit/dependency/delete; blocked or review-required reporting; list/wait/message queue coordination; and interrupt/cancel safety controls. These exemptions permit durable bootstrap/control mutation only—they never exempt a downstream model wake.

Enable/member-add may materialize members and persist quarantined initial prompts, but MUST NOT activate them without a current exact mission lease. `send_message` may durably queue a message without a lease, but waking, cold-resuming, or releasing any child inbox is a separate executor boundary that revalidates the exact mission lease; absent authorization, the message remains queued. Complete/reopen/claim/reassign, `working`/`done` reports, filesystem/network/process writes, model/provider delegation, child activation/wake/resume, and all other effectful capabilities require the exact mission lease. GAT owns this immutable classification; wrappers inherit the most restrictive nested classification and cannot widen an exemption.

Executable tasks live only on the canonical Team task board and carry `missionId`. The mission record stores objective, constraints, evidence contract, task ids, and revision metadata. Migration of current embedded mission task snapshots is deferred to the mission workstream but the authority direction is frozen.

## 11. Team-exclusive external delegation

When `TeamView.enabled === true`, execution of external delegation capabilities—including `subagent`, `subagent_fork`, `workflow`, `ralph`, aliases, and nested/composite dispatch—MUST fail before provider invocation, child creation, or event append.

DSH's tool registry owns immutable capability metadata; `external-delegation` is a reserved key that package code cannot remove through wrappers. Nested/composite execution propagates the union of its own and descendant capabilities, and the executor checks metadata again at each nested boundary. The GAT guard always applies both the capability denial and the compatibility name deny-list until every shipped delegation path is attested; missing metadata never disables the name fallback. Before Team enablement, configured one-shot tools may retain existing behavior. Prompt text is guidance, never enforcement.

## 12. Prompt, tools, and observability

Policy composition uses stable, provenance-bearing sections:

1. host/system safety;
2. GAT Team identity, authority, shared checkout, task, mailbox, wait, and completion duties;
3. bounded binder capability summary;
4. capability-specific guidance and bounded catalogs;
5. exact mission/task context.

Duplicate section keys fail loudly. Binder text cannot grant permission. Tools remain member-scoped and executor-guarded. Non-Team agents and unavailable/unbound members see no binder tools or context.

Views may expose binder id, protocol version, and safe readiness (`ready`, `unavailable`, `failed`) but never private payloads. Runtime status is distinct from binding readiness; a running member cannot lack a required live binding.

## 13. Required conformance fixtures

| Fixture | Required assertion |
|---|---|
| Prepare-all | Any route/binder prepare or returned-output validation failure produces zero member rows and zero child Sessions; every earlier prepared lease aborts exactly once in reverse order. Oversized/mutable/non-JSON returned values never reach the journal. |
| Success trace | `prepare-all -> provisioning flush -> materialize -> bind/contributions -> persist quarantined inbox -> active -> activate`; request count stays zero until `activate`. |
| Failure injection | Failure at each edge, including after inbox persistence and after active commit, follows the frozen tombstone/unavailable rule, releases ownership safely, and retains name reservation. Same-process publish/activate retry never reinstalls; restart/fatal reconstruction releases the old generation then recovers exactly once. |
| Reserved-handle states | Every legal/illegal/concurrent transition produces the frozen state and stable error; prompt idempotency creates one durable item. |
| Exactly-once activation | Concurrent/repeated persistence and activation create one durable inbox item and at most one first request. |
| JSON boundaries | RFC 8785 record/array bytes, root-depth/node/key/string conventions, digest, exact-limit acceptance, and +1 rejection are shared fixtures. |
| Restart matrix | Active/provisioning, missing binder, adjacent/unknown protocol, corrupt/oversized attachment; no inbox release or mailbox delivery before recovery success. |
| Disposal | Admission cutoff, bounded settlement, reverse release, child drain, persistent external data retained. |
| Delegation denial | Every named tool, alias, and nested dispatcher denies when enabled; provider/child/event counters remain zero. |
| Authorization matrix | `{simpleMode on/off} × {disabled/enabled} × {mission absent/draft/authorized/stale/closed} × {plan unapproved/current/stale}` has explicit allow/deny reasons. |
| HUMAN provenance | Model-created mission cannot authorize; host-attested HUMAN exact revision can; wrong Team, ambiguity, revision drift, close, and revoke deny. Enable/member-add/message queue with no lease causes zero provider/model calls until a separately guarded wake validates a lease. |
| Scope isolation | Only the exact bound member sees contributions; non-Team and unavailable members do not. |
| Compatibility | GAT-only Loader, JSONL replay, generated SDK, browser safe diagnostics, keyless snapshots, and legacy `startContinuable()` remain covered. |

## 14. EXEC-B / EXEC-C dependency matrix

| Contract surface | EXEC-B (GAT) | EXEC-C (DSH) |
|---|---|---|
| Normalized specs and initializer | implement/own | consume Agent route semantics only |
| Attachment bounds/event v3/adapter | implement/own | opaque |
| Binder registry and orchestration | implement against the frozen reserved-handle interface and fakes; no production wiring | expose exact member scope |
| Reserved child handle/state/errors | compile against interface/fake | implement/own |
| Persist-only inbox and exactly-once activation | order and verify against fake | implement/own |
| Recovery before work admission | orchestrate binders | materialize without resume/admit |
| Rollback/disposal | order bindings and durable phase | child cleanup primitive |
| Legacy wrapper compatibility | test integration | preserve existing consumers |

EXEC-B may implement types, validation, persistence, registry, prepared-lease ownership, and orchestration only against the frozen reserved-handle interface plus deterministic fakes. It MUST NOT add production child wiring before EXEC-C lands. EXEC-C implements the handle state machine, stable errors, persist-only inbox, activation gate, recovery inspection, and compatibility wrapper without importing GAT. Production integration orchestration waits for both.

## 15. Explicitly deferred

- Optional/degraded attachments.
- Durable Agent storage, SOUL, memory, and task-context implementation.
- Production binder implementation and integration profile.
- Host-attested mission admission implementation and mission close/revoke commands.
- Capability-metadata implementation in the DSH tool registry.
- Mission event/task normalization migration details beyond the frozen one-authority direction.
- Web/SDK release UI beyond safe diagnostic contracts.

Any implementation that treats the current simple-mode approval shortcut as authenticated mission authorization, binds after `agent/created`, re-reads the workspace manifest during recovery, or allows an active member without all required live bindings violates this contract.
