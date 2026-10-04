# GAT → Durable Agent binding: implementation proposal and agent handoff

Date: 2026-10-04 (Asia/Tokyo)

Status: Draft proposal for review; no implementation or production activation approval recorded here.

Scope: GAT required member attachments and a Durable Agent memory/context adapter.

Origin: Binding proposal and review in the HUMAN conversation; this revision incorporates all six review findings, source inspection, and the supplied closing-execution proposals.

## 1. Outcome, authority and reading order

Enable a GAT teammate to use a specifically declared Durable Agent identity, bounded context, selective memory reads and unconfirmed memory submissions. Binding must exist before the first model request and must be recovered before any later work is admitted. GAT owns Team lifecycle and coordination; Durable Agent owns its persistent domain data.

This document proposes the missing implementation. It does not change the frozen contract or mark target features as implemented. **Frozen requirements** below come from the existing contract. **Proposed decisions** are recommendations for an implementation baseline; approval of this document's preparation is not approval to execute or activate it. An implementing agent must identify the applicable implementation authorization and resolve the listed prerequisite gates before dependent work. Applicable CR gates remain in force for canonical changes.

Read project `AGENTS.md` and `.ai-work/AIWS.local.md` first. Follow wiki-first lookup before loading design inputs, then read:

1. [Architecture Design](ARCHITECTURE_DESIGN.md), §§4–7, especially AD-04, AD-08, AD-09 and AD-12.
2. [Basic Design](BASIC_DESIGN.md), BD-12–14 and §§5–8.
3. [Detail Design](DETAIL_DESIGN.md), DD-01–03, DD-07–11 and DD-15–17; use [Source Code Map](SOURCE_CODE_MAP.md) for actual symbols.
4. [Member-Binding Contract Freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md), §§3–14. This is the normative target, including bounds, callback ownership, authorization and activation ordering.
5. [Durable integration reference](DURABLE_AGENT_INTEGRATION.md), public integration contract and verification limits.
6. Original public [service](../../../dsh-durable-agent/durable-agent-plugin/src/service.ts), [Consumer](../../../dsh-durable-agent/durable-agent-plugin/src/consumer.ts), and [provider](../../../dsh-durable-agent/durable-agent-plugin/src/local-provider.ts). The sibling checkout is required for these links; pin and inspect the actual package intended for integration.
7. [GAT closing RCA/fix proposal](../../../../deepseek-harness/wbs-runs/gat-execution-closing-diagnosis/GAT_CLOSING_EXECUTION_RCA_AND_FIX_PROPOSAL.md) and [Durable closing compatibility proposal](../../../../deepseek-harness/wbs-runs/gat-execution-closing-diagnosis/DURABLE_AGENT_CLOSING_COMPATIBILITY_PROPOSAL.md). These are conditional owner handoffs, not accepted amendments or deployment evidence. Their applicability is scoped in §§2.1–2.2 and §7.5.

Useful navigation commands, from GAT root:

```sh
python3 .ai-work/tooling/lookup_wiki_source.py --query 'GAT member binding contract freeze'
python3 .ai-work/tooling/lookup_wiki_source.py --query 'GAT Detail Design'
python3 .ai-work/tooling/lookup_wiki_source.py --query 'Durable Agent consumer service'
```

Do not implement from this handoff alone. Compare it to the then-current source and design. Design/source conflicts require resolution before changing the affected behavior. Update the approved design delta before source; for WBS execution, follow the project rule for intermediate deltas and apply approved deltas to official design before finalization.

## 2. Inspected baseline and review disposition

Inspection used GAT HEAD `8121d8c13640afa234496af34fdeac727312c5b1` plus the current working tree, and Durable Agent HEAD `a8e215433ae050e36e0ba27205701be1a5f114a1`. GAT already had local changes in `core/src/{projection,roster,types}.ts`, `core/tests/{persistence,team}.spec.ts`, and `web/tests/team-action.client.spec.tsx` under `packages/`; preserve and recheck these changes. HEAD alone does not identify the inspected dirty bytes. No DSH checkout was qualified by this proposal.

| Review issue | Resolution in this proposal |
|---|---|
| Production lifecycle dependency unspecified | §10 gates production wiring on an evidenced DSH reserved-handle contract |
| Persistent identity/recovery payload missing | §§3–5 specify a candidate payload, trusted workspace check and ownership policy; never replay a process ref |
| Consumer descriptors mistaken for executable tools | §6 specifies handlers, schema checks, scope checks and disposal |
| Authorization treated as first-activation-only | §8 requires executor checks on effects, wake and resume, including nested delegation |
| Failure, retry and bounded cleanup underspecified | §7 distinguishes pre-active failure, live retry and reconstruction; covers late provider completion |
| Memory approval/context refresh ambiguous | §6 selects read/submit-only model tools and an explicit refresh policy |
| Additional finding: provider returns an existing active ref for the same identity | §5 adds exclusive ownership and prohibits unsupported sharing |
| Additional finding: current loader falls back to unbound defaults | §4 requires an explicit Durable declaration to fail closed |
| Closing-time presentation can throw before graceful execution cutoff | §§6,7.5 preserve static Team labels and add precise contribution abstention; live effects stay denied |
| Async closure can leave schemas/bodies or deadlock cleanup | §§6,7.5 cover pre-collected assembly surfaces, post-await checks and self-drain avoidance |
| Source, built artifact and loaded process can differ | §§10–11 require separate built-path and, when authorized, runtime qualification |
| Official DSH Consumer uses different APIs and execution identity | §2.2 requires explicit API/lifecycle selection rather than implicit WK-to-DSH translation |

Current source facts to preserve in the implementation record:

- `TeamService.registerInitializer()` already enforces one initializer, but its callback currently performs enable/provisioning and returns `TeamEnableResult`. The target callback returns normalized specs and core performs provisioning. This is an API and caller migration, not merely adding an extra registration.
- `TeamRoster` uses `startContinuable()`. `team/member` currently has version 2 and no attachments. The target member event is v3; other event families do not automatically become v3.
- `DurableAgentConsumer.modelContribution()` returns prompt text and tool descriptors. Executable DSH handlers still need implementation.
- `LocalDurableAgentProvider.provision()` deduplicates active identities using owner, scope and name. Same identity/declaration can return the same ref. Its `release()` has no `AbortSignal`, and repeat calls are not guaranteed idempotent. GAT must supply idempotent lifecycle wrappers.
- Existing installer/verifier mappings enumerate five GAT packages. A new adapter/profile package also requires distribution and verification changes.

### 2.1 Closing-proposal assessment and provenance

The supplied GAT RCA supports a closing-time presentation failure: a strict membership call can throw after execution admission intentionally closes, although a submitted result remains durable. It also records a preexisting static-label source patch and an older built artifact. This repository's current `packages/tools/src/index.ts` already captures role/name/Team ID during `install()` and renders static `team:policy` text. Preserve and qualify this behavior; do not add a duplicate patch or widen membership to closing to hide the error.

The Durable proposal identifies a conditional assembly risk in the official DSH Team/Durable Consumer. It does not establish a storage/provider cause, a mounted Consumer in the incident runtime, or approval to change the provider. Proposed handling is owner-local: exact known-closing executions contribute no Durable material while reads/effects remain denied. Unknown/stale identity and active provider errors remain failures.

Reference bytes inspected for this supplement on 2026-10-04:

| Input | SHA-256 |
|---|---|
| GAT closing RCA/fix proposal | `d6ab0707d163247f7b44f8c9fe49db42392e37259a6f073ab577508e58cbb834` |
| Durable closing compatibility proposal | `290e4b8f5f4916a389386fa5280e7108ae9977d8fe16585a5ff07b8639166773` |

The DSH checkout HEAD during inspection was `c1157f7ed448b40c463c1a43fa595b12294fd50d`; cited files include working-tree changes, so HEAD is not a tested artifact identity. The diagnosis [source observation](../../../../deepseek-harness/wbs-runs/gat-execution-closing-diagnosis/source-observation.json) is a timestamped source/artifact observation, explicitly not proof of the modules loaded by a live process. Reinspect current bytes during implementation. Do not copy incident task/execution IDs into regression fixtures as reusable authority or reactivate their old Sessions.

### 2.2 API and execution-model qualification

Two different Durable API families are involved. A shared Cordis service name or similar class name does not make them interchangeable.

| Family | Actual interface / lifecycle | Applicability to this handoff |
|---|---|---|
| Sibling WK-style package used by P-01 | Declaration-based `provision(workspace, declaration)`; generation-bound `DurableAgentRef`; `openTaskContext`, selective read, candidate/authorized commit; Consumer descriptors | §§4–6 describe this adapter. Snapshot/read consistency remains per public call; no request lease is implied |
| Official DSH Team/Durable Consumer | Profile/principal/limits-based provision; `DurableMemberRef` and request `openLease/read/releaseLease`; `durable_memory_read`; selected assignment memory; isolated execution or legacy principal | Closing-proposal implementation owner is this official Consumer. These signatures, tools, selection and cleanup APIs must not be pasted into the P-01 adapter |

Recheck the [Durable Detail Design DD-08/09](../../../dsh-durable-agent/docs/DURABLE_AGENT_DETAIL_DESIGN.md) and the original [official Consumer source](../../../../deepseek-harness/packages/experimental/agent-team-durable-agent/src/index.ts) for the chosen composition. The official Consumer currently mounts through `agent/created`; its existence is not qualification of the frozen pre-admission GAT binder lifecycle.

The closing diagnosis also uses a stable logical Team member plus fresh per-task execution Session. The originally inspected GAT baseline uses direct continuable teammate Sessions. S0 must record which lifecycle is the actual target. This supplement does not silently migrate the latter to isolated execution or change the frozen member/attachment identity. If an isolated target is selected, its owner must approve the member-to-execution mapping before wiring; retain stable logical member identity and persistent memory across fresh Sessions, close only the old execution's authority, and never reuse its transcript or revive it for a new task.

That mapping must distinguish the persisted member attachment/profile identity, the process-local provider ref and its exclusive cleanup owner, and the prompt/tools/authority installed for each exact execution Agent/Session/generation. Specify whether the ref is retained by a member owner or released and reprovisioned between executions, how execution cutoff joins that owner, and when the next execution may acquire authority. Provider deduplication is not proof that sharing or handover is safe. Any resulting change to frozen callback authority, ordering or failure semantics requires the applicable reviewed contract/protocol revision before dependent source changes.

For the official isolated path, retain its existing principal namespace and root-Team + stable-member segments. Do not substitute task Session ID, merge legacy namespaces, or change the WK provider's storage key to imitate it. Two fresh executions may reuse stable persistent content only under the existing ownership/lease rules; never overlap pending old-resource cleanup by weakening P-03. Legacy or direct-continuable paths lacking an equally strong execution-lifecycle proof retain strict denial on lost authority.

An assignment to implement the WK-style adapter can apply the general presentation/cleanup safeguards here without editing the official Consumer. An assignment to integrate the official DSH Consumer requires a separately reviewed API-mapping revision to §§3–6 and ownership agreement. This remains a concrete unresolved integration-selection gate, not a request to implement both families.

## 3. Proposed MVP decisions

The following are proposed defaults to approve together as a baseline, rather than options an implementing agent should silently select. They narrow the first adapter release without weakening the generic frozen binding protocol.

| ID | Recommended decision | Consequence / later extension |
|---|---|---|
| P-01 | Separate integration package `@vuhoi/gat-durable-agent` under proposed `packages/durable-agent/` | Core stays capability-agnostic; imports DA public `/service` and `/consumer` exports only |
| P-02 | Durable adapter V1 accepts explicit `scope: workspace` and `context: fresh` only | Reject global/fork declarations for this adapter; generic GAT keeps fresh/fork and members without attachments, subject to the applicable execution guards. Global sharing and inherited-context isolation need later design/tests |
| P-03 | One live GAT owner per canonical workspace + Durable name; dedicated provider instance used only by this binder; one host process per storage workspace | Concurrent second ownership is rejected, not silently shared. This is a deployment constraint, not a cross-process lock guarantee |
| P-04 | A separate strict `team_members.durable.yaml` declaration, selected by an explicit integration profile | Existing GAT-only configuration remains available through its default initializer. No automatic fallback from a requested Durable roster to unbound members |
| P-05 | Model sees read-memory and submit-candidate tools only | Confirmed commit remains an independently authorized host operation; no new memory approval UI in this MVP |
| P-06 | Refresh bounded Consumer context at bind/recover and before each authorized model request using a qualified host hook | Live scoped prompt section is replaced, not accumulated. Active refresh failure prevents that request; exact known-closing assembly abstains under §7.5 and admits no request; memory reads remain per-call reads |
| P-07 | Binding foundation and integration verification may finish before production enablement | Production still requires DSH lifecycle, exact mission leases and executor capability enforcement |
| P-08 | Graceful contribution abstention only for exact owner-proven closing/terminal isolated executions | Presentation returns no Durable material; executor admission remains closed. Unknown/stale identity and legacy paths without equivalent proof still reject; API/lifecycle selection is qualified in §2.2 |

P-03 cannot be established by inspecting DA private directories. The public API has no exclusive-owner query or cross-host lease. The approved composition/deployment must establish exclusivity, and the binder must serialize all of its own owners. If shared providers or multiple hosts are required, stop that integration path and design a public lease/ref-count protocol with the DA owner; do not infer safety from a process-local map.

Out of scope: Durable task runner, WBS execution, reference-memory/MCP storage integration, global memory sharing, optional/degraded attachments, live identity edits, automatic memory promotion, new filesystem authority, and automatic package publication/profile activation. Existing services remain the owners of these independent concerns.

## 4. Declaration, normalization and persistent attachment

Proposed input example; **this format is not supported by current GAT**:

```yaml
version: 1
members:
  - name: implementer
    description: Implements the assigned canonical Team task
    prompt: Follow Team coordination and report evidence for assigned work.
    context: fresh
    provider: configured-llm-provider
    model: configured-model
    durable:
      scope: workspace
```

Use strict closed schemas for document, member and `durable` keys. Reuse existing safe file reading and member text bounds where suitable, but separate parsing from fallback behavior. Reject missing/malformed explicit Durable configuration, duplicate names, unsupported scope/context, incompatible API/features and unavailable routes before creating member rows. Defaults must never silently remove `durable` intent. The file is declaration input, not approval or execution authority.

Distinguish three provider concepts in types and diagnostics:

- `continuationProvider`: DSH materialization route, e.g. the configured spawn provider.
- `DurableAgentDeclaration.provider` and `.model`: LLM route from normalized member configuration; validate consistency with the actual child AgentOptions.
- Durable service registration/provider instance: trusted host configuration selecting the storage service. Do not let model tool arguments select it.

The integration initializer returns the frozen `TeamInitialization` / `TeamMemberSpec` shape. It resolves raw configuration into detached values and does not spawn children. GAT core owns prepare-all and provisioning. Migrate the current default initializer to the same normalized interface; the integration initializer replaces it in composition. Duplicate initializer registration remains an error.

Proposed attachment payload owned by binder `durable-agent`, protocol version `1`:

```ts
type DurableAttachmentV1 = {
  schemaVersion: 1
  serviceBindingKey: string  // trusted stable host registration selector
  workspaceRealpath: string // canonical public workspace, NOT provider storage path
  declaration: {
    name: string
    description: string
    prompt: string
    context: 'fresh'
    provider: string
    model: string
    reasoningEffort?: string
    scope: 'workspace'
  }
}
```

Persist this only inside the generic `TeamMemberAttachmentRecord` envelope: `binderId`, `protocolVersion`, `required: true`, `payload`, `payloadSha256`. Compute SHA-256 from RFC 8785 canonical payload bytes in core, after detaching and validating `prepare().attachment`. Do not persist the runtime DA ref, Consumer, live Agent, closure, secret, provider-private storage root or process-local prepared lease.

Apply **all** freeze §5 bounds to requests and prepared output: record/aggregate canonical bytes, depth, nodes, key/string bytes, ID/version/uniqueness and plain acyclic JSON. Validate before a provisioning event and again during replay; test exact limit and +1 cases. A domain-valid DA declaration may still exceed GAT's envelope limits and must then be rejected.

The persisted workspace is host-only recovery input, not a model-visible path. On recovery, independently resolve the owning root Session's workspace through the approved host resolver and require equality with `workspaceRealpath`. Resolve `serviceBindingKey` through trusted pinned host composition; a missing or changed registration is unavailable. Workspace relocation/provider migration requires explicit migration design, not a rewrite during recovery.

The declaration name must equal the immutable GAT member name in V1. Persist the approved initialization declaration exactly; later task messages never rewrite this profile declaration. A provider profile conflict fails closed. Recovery uses this persisted declaration, never the mutable YAML file.

## 5. Binder registry, API mapping and ownership

Implement the registry and `PreparedAttachment` / `TeamMemberBinder` / `DisposableBinding` contracts from freeze §6. One live registration per `(binderId, protocolVersion)`; no replacement/removal while any durable member, including inactive members, references it. Registry lookup on restart can report missing implementations, but cannot permit unbound execution.

Binder inputs carry exact Team/member/Agent-generation identity and only the scoped capability-installation facilities necessary for the callback. Do not pass unrestricted Team mutators or expose these inputs to model tools. The prepared state has an atomic ownership transition: prepared → transferred to binding, or prepared → aborted, exactly once.

| Callback | Proposed implementation using public DA APIs |
|---|---|
| `prepare(input, signal)` | Validate/normalize payload; verify pinned API version 1 and required feature flags; check trusted workspace and child-route agreement; call `validateDeclaration`; reserve exclusive identity in a host-wide coordinator; return detached attachment plus process-local lease and idempotent abort |
| `bind(input, attachment, prepared, signal)` | Verify exact lease/member generation; call `provision`; construct Consumer with returned opaque ref; validate initial snapshot; install bounded scoped prompt and executable handlers; transfer ownership only after complete success |
| `recover(input, attachment, signal)` | Revalidate persisted payload and host workspace/registration; reserve ownership for the new generation; provision the exact persisted declaration to get a current ref; construct Consumer and reinstall contributions. No YAML reload or reuse of a saved ref |
| `closeAdmission()` | Atomically deny new handler calls and refresh/model admission; invalidate scoped runtime authority and synchronously unregister owned tools/contribution listeners. Handle already-collected material under §7.5 |
| `settle(signal)` | Await operations admitted by this binding within the remaining shared lifecycle deadline; do not treat timeout as cancellation of a provider operation |
| `release(signal)` | Finish idempotent disposal after immediate contribution cutoff, call provider `release(ref)` through a single memoized promise, and relinquish identity ownership after actual settlement; repeated lifecycle calls reuse the result |

Required flags for this adapter are `selectiveMemoryRead` and `memoryCandidateSubmission`; core does not interpret these flags. Confirmed-commit and working-artifact features are not prerequisites for read/submit-only model tooling. Host commit workflows must check their own requirements.

The proposed prepare phase does not provision DA storage. A successful validate/prepare does not guarantee subsequent profile/storage success. A bind failure after storage creation retains persistent external data; it is not a transaction rollback of that storage.

Serialize ownership reservation and provider lifecycle per normalized identity across all Teams using this binder. Reject a second owner before invoking `provision`. Reserve all requested identities before creating the first child. Retain reservations while cleanup is physically pending so a late release cannot invalidate a replacement binding. Do not use a map local to one Team or Consumer.

If `bind`/`recover` acquires a ref and fails before returning a binding, that callback owns cleanup of its partially installed resources. Core still aborts any untransferred prepared lease. These operations must cooperate through one ownership record to avoid double release. Releasing a ref accidentally shared with an external consumer is not safe; enforce the P-03 composition precondition.

## 6. Scoped prompt, executable tools and memory policy

Register tools in the exact reserved child scope before initial prompt persistence. Use stable provenance-bearing prompt section keys that include binder identity; obey freeze §12 ordering. Duplicate section/tool keys fail binding. A Consumer descriptor is metadata, not executable registration.

Team role/name/ID display labels are captured once after installation-time authorization, as the current static `team:policy` section does. Rendering these labels never calls strict membership or acquires execution authority. Live checks remain in guards, handlers and host admission. Do not catch all rendering failures or reorder the global agent loop to fix one owner's callback.

| Model tool | Closed argument shape | Handler |
|---|---|---|
| `durable_agent_read_memory` | `{ itemId: string }` with pinned DA ID/byte constraints | Validate → check live scope/generation/binding and executor policy → `consumer.readMemory(itemId)` → bounded result |
| `durable_agent_submit_candidate` | `{ title, retrievalCondition, content, provenance, confidence, limitations }` using pinned DA candidate schema/bounds | Validate → check live scope/generation/binding and exact effect lease → `consumer.submitUnconfirmedCandidate(input)` → result explicitly marked `unconfirmed` |

Reject unknown keys, including ref, member/team ID, workspace, service/provider selector, scope, authorization and canonical status. Never accept an arbitrary ref from a tool caller. Bind handlers to the private Consumer instance. `provenance` in a candidate is untrusted descriptive text, not an authorization carrier.

Admission and in-flight accounting must be atomic with `closeAdmission()`. A closure retained after disposal, stale Agent object or same Session ID with another generation is denied. Check exact live authority before and after asynchronous snapshot/read calls; an operation admitted while active does not authorize its late result after closure. Withhold late model-visible memory/context rather than relying on provider validity alone. Non-Team agents, the Lead without an explicit attachment, and unavailable members receive no DA tools or DA prompt section. Do not put raw attachment JSON/ref/workspace into model-visible errors or view responses.

For P-06, refresh one bounded `modelContribution()` before each model request through a host hook that can prevent dispatch. Use its single coherent snapshot for prompt/catalog/revision metadata; do not combine separately fetched snapshots. Do not prefetch all memory bodies. If the hook does not exist or cannot gate requests, production is blocked pending that host capability or a reviewed refresh-policy revision. Do not silently revert to context cached forever at bind time. Active refresh/provider failures prevent the request and remain visible; only §7.5's exact known-closing case permits contribution abstention, with later model admission still denied.

An old catalog does not authorize a stale item: every read still validates against the current provider state. Public context and later selective reads have per-call consistency, not cross-call snapshot affinity. Refresh affects future request assembly; it does not rewrite historical Session messages or retract already consumed model context.

No confirmed-memory commit tool is registered. If an existing authorized host workflow calls `commitMemoryItem`, it must validate trusted approval outside the model, pass valid authorization evidence, and retain an audit reference. Candidate text claiming approval never suffices. A new approval UI/workflow is separately scoped work. `workingLocation` is also outside this adapter MVP; binding does not grant file access or change child cwd.

## 7. Lifecycle, failure and recovery algorithms

### 7.1 Prepare-all and first activation

Implement the exact freeze §§4,7–8 semantics. Semantic method names below are target interfaces, not a claim that installed DSH exports them.

```text
call one initializer and validate the entire normalized roster
resolve all continuation/model routes and binder registrations
prepare all attachments in deterministic order
detach/revalidate output; compute immutable records and digests
for each member under GAT-owned lifecycle admission:
  reserve child ID and append/flush v3 provisioning snapshot
  materialize reserved child without inbox or model admission
  bind all required attachments and scoped contributions
  persist exactly one initial inbox item in quarantine
  append/flush active snapshot with unchanged attachments
  publish binding readiness
  revalidate execution authorization and activate when permitted
```

Before completion of prepare-all, any failure produces zero member rows and zero child Sessions; abort successful prepared leases in reverse order. After provisioning begins, do not claim atomic roster rollback: earlier durable rows remain accountable, active members are not rewritten as failed, and unused prepared leases must still be aborted on failure/cancellation.

The initial-prompt idempotency key belongs to the member's durable activation identity and survives reconstruction; do not include a transient runtime generation in a way that creates another initial message. Same key/different content is a conflict. The reserved handle must preserve all legal/illegal/concurrent transition errors from freeze §7.

When no exact mission lease is available, bootstrap may create a bound member and a quarantined prompt under the separate bootstrap authorization. It must not activate the model. Keep binding readiness separate from execution authorization in readiness output; missing authorization is not itself a binding installation failure.

### 7.2 Failure matrix

| Point / condition | Required result |
|---|---|
| Prepare or returned-output validation fails | Zero new rows/children; abort every successful lease once in reverse order |
| Provisioning/materialize/bind/contribution/prompt step fails before durable active | Close admission; tombstone quarantined prompt if present; abort unused leases; settle/release installed bindings in reverse order; dispose child; append failed snapshot preserving exact attachments and name reservation |
| Active append/flush outcome uncertain | Inspect durable committed evidence before deciding the edge. Do not assume an exception means no active event exists or blindly append failed |
| Active commit succeeded, publish/activate fails; live resources remain valid | Durable phase stays active, runtime unavailable. Close only outer execution gate; retry incomplete publish/activate; do not close/release/recover the still-valid binding |
| Active commit succeeded, resources invalid or generation uncertain | Close/settle/release old resources, dispose old handle, advance generation, reconstruct and recover exactly once before activating the existing message |
| Missing binder/version, corrupt digest, identity/profile mismatch | Unavailable with bounded diagnostics; no attachment rewrite, fallback or model/inbox/mailbox release |
| Authorization absent/stale/revoked | Deny the effect/wake; preserve queued/quarantined work for valid later authorization; no bypass via readiness or simpleMode |
| Owner-proven isolated execution closing/terminal | Revoke its Consumer admission, return no Consumer material during assembly, preserve later graceful host cutoff and retained submission; drain owned resources. This never reactivates the execution or grants reads/effects |

An `active` durable snapshot after restart does not prove live readiness. Recovery must establish bindings and host admission state before advertising the member as runnable.

### 7.3 Cold recovery

1. Project valid member events and inspect durable activation state; verify child descriptor, parent, provider and owned Session suffix.
2. Validate all attachment envelopes, versions, canonical digest and bounds before invoking binders.
3. Materialize/cold-resume with inbox, mailbox and model release disabled.
4. Recover required binders in deterministic order using the persisted payload, obtaining fresh runtime refs where necessary.
5. Install/refresh contributions, publish binding readiness, then revalidate the current exact mission lease at activation.
6. Activate only the existing non-tombstoned initial item; never create a replacement prompt to make recovery pass.
7. Reconcile normal Team mailbox messages using their existing dedupe keys, with separate executor checks at delivery/wake boundaries.

Concurrent enable/spawn/recovery must serialize ownership by durable member and generation. Duplicate recovery for the same live generation returns/awaits its in-flight result rather than reinstalling. An unavailable member remains inspectable/repairable without executing unbound.

### 7.4 Deadline, non-cancellable provider work and disposal

One total GAT lifecycle deadline covers cutoff, settlement, reverse release, child drain and registry-effect cleanup. Every binder callback receives the remaining-deadline signal. Provider APIs currently do not accept that signal: racing a promise against a timer does not cancel storage work.

Track all outstanding provider operations. If cancellation occurs during `provision`, retain its ownership reservation and observe late completion; a late ref must be released, not installed into an obsolete generation. If release times out, detach all prompt/tool/execution authority immediately, record a safe pending-cleanup diagnostic, retain identity quarantine, and continue best-effort child cleanup. Keep observing late results/rejections so they cannot become unhandled or reopen admission.

Memoize cleanup per acquired ref; do not turn provider `UNAUTHORIZED_REFERENCE` into blanket success since it may reveal wrong ownership. Treat repeat calls as idempotent at the wrapper level using proven local lifecycle state. Persistent memory/profile/work data survives release. Never delete provider storage as compensation for a failed Team bootstrap.

### 7.5 Expected closing: contribution abstention without regained authority

This is proposed conditional compatibility handling from the supplied owner handoffs. It supplements closure/assembly behavior; it does not redefine `active`, alter durable member phases, authorize a terminated execution or require a provider/storage API change. Qualify it only for the explicitly selected composition in §2.2.

Use an internal classifier derived from the existing authoritative execution owner, not a writable tool/config flag, cached role label or second lifecycle store:

| Classification | Required proof | Assembly response / operation response |
|---|---|---|
| Authorized active | Exact live root and Agent objects, captured execution ID, stable member ID/name, Session and generation still match; provisioning/active phase and current assignment selection apply | Preserve bounded context and provider/selection validation. Operations and model admission still apply their current guards |
| Known closing | The same exact live objects and authoritative captured execution still match, but phase is closing or terminal; active membership may intentionally be absent | Synchronously revoke Consumer admission; omit its schema/context/guidance/catalog/provider details without a new expected-closing assembly error. Deny reads/effects/model wake and withhold late bodies |
| Unauthorized/unknown | Missing/replaced root/Agent/execution, changed generation/identity, ambiguous binding, or unsupported legacy-to-isolated transition | Reject with bounded sanitized errors. Missing membership alone is not proof of graceful closing |

Terminal abstention is eligible only while exact identity remains observable. After removal/replacement it is unknown/unauthorized, not authority to reconstruct. For the current direct-continuable or legacy path, do not infer this classification from a failed membership lookup; retain strict denial unless that lifecycle owner supplies equivalent authoritative proof. Intentional absent/stale mission authorization on an otherwise active execution is also not known closing.

Owner-local assembly/cleanup sequence:

1. Probe the classifier before downstream assembly or provider open/snapshot. On known closing, atomically revoke new admission and dispose future scoped Consumer listeners/tools; invoke the existing one-shot cleanup owner rather than creating a second release manager.
2. Finish the current assembly with **zero material owned by this Consumer**. Tool schema/SDK surfaces may already have been collected before the waterfall, so unregistering alone is insufficient. Filter structured owner-tagged output or perform a bounded owner-local reassembly through a qualified host API. Preserve unrelated sections/tools and the host execution's later admission denial. Do not redact by broad substring replacement or hide missing/duplicate Team policy defects.
3. Recheck after downstream assembly and after every async open/snapshot/read. If closing now matches exactly, never publish a late lease/ref as active or return a late body; remove any material collected earlier in the same assembly. In the WK-style adapter cover both read and candidate descriptors; in the official Consumer cover `durable_memory_read`, `durable-agent:guidance`, `durable-agent:task-context` and its catalog/provider material. The actual registered owner names remain the source of truth.
4. Separate synchronous revocation from awaited cleanup. An open/read/refresh callback must not await a `close()` that drains a set containing that callback; return/settle first and let the lifecycle owner await the one-shot cleanup. A late acquired provider resource remains tracked and is released exactly once. Demonstrate bounded reassembly and absence of recursion/self-await deadlocks with barriers.
5. Keep failures observable: wrong/stale identity, active provider errors, invalid snapshots/revisions/bounds, missing/duplicate Team policy and cleanup errors are real failures. Direct memory calls during closing still deny; graceful assembly abstention is not a successful memory read. Already admitted storage mutations may settle; closing does not prove they were cancelled, undone or safe to replay.

If submission has already durably recorded a result and `closing`, cleanup must not replay submission or erase its receipt to repair prompt assembly. Preserve separately: submission/result state, Agent turn outcome, resource cleanup, canonical task settlement and product acceptance. `closing` means submitted/cleanup-pending; terminal publication follows the execution owner's required cleanup, and a cleanup failure remains visible. A completed execution does not automatically complete the canonical task or accept its deliverable. Natural post-tool turn termination may be a blocked admission result; do not redefine it as a completed turn merely to make a test pass.

The primary GAT static-label fix must be qualified both without and with the intended Consumer. This distinguishes presentation regression from conditional Consumer compatibility. It does not justify changes to Durable storage, principal/security semantics, WK working capabilities or LEG/BS1 task execution.

The closing supplement introduces no additional persistence migration beyond the binding work already specified here. Its classifier consumes existing authoritative execution state. Any change needed to support a different execution model is a separate approved mapping/design dependency, not an incident fix inferred from these reports.

## 8. Authorization and delegation dependencies

Production requires freeze §§10–11, not only binding readiness:

- Trusted host admission supplies exact HUMAN `teamId + missionId + missionRevision` provenance. A Lead/model-created approved-looking mission is insufficient.
- GAT scope leases include the authorization identity and issuance/revocation generations; executor checks current authority immediately before effects, activation, wake and resume.
- Task execution derives its association from the canonical Team task and immutable `missionId`; do not choose the latest/first mission or rely on a duplicated mission task list.
- Apply the exhaustive exempt-capability classification from the freeze. Queuing/inspection exemptions never imply permission to wake a child. Candidate submission is a storage effect and requires the corresponding execution authorization; read tools still require scope checks and the frozen executor policy.
- Enforce Team-exclusive external delegation through immutable capability metadata and the compatibility deny-list, including aliases and nested dispatch. Binder/Consumer guidance cannot provide this enforcement.

The agent owning binding may consume these as separate approved host/GAT workstreams. Do not silently expand a binding-only assignment to rewrite mission authority. Record their concrete revisions/evidence as production prerequisites. Without them, complete foundation/integration fixtures only and report production enablement blocked. Any proposed relaxation requires an explicit reviewed contract revision.

## 9. Source work map and design-before-code obligations

Paths marked **new** are proposed destinations; symbols and exact names may be refined without changing the frozen semantics.

| Work | Existing / proposed source | Required design coverage before source change |
|---|---|---|
| Normalize initializer ownership | `packages/core/src/index.ts`; `packages/tools/src/index.ts`, `team-config.ts` | DD-01 and DD-16: callback migration, default/integration selection, strict declaration behavior |
| Attachment types/validation/registry | `packages/core/src/types.ts`; **new** `attachments.ts`, `member-binders.ts` | DD-16: public contracts, JCS bounds, registry lifetime, ownership transfer |
| Member event v3 and replay | `packages/core/src/types.ts`, `projection.ts`, `journal.ts`, `roster.ts` | DD-03/DD-16: event-family version dispatch, adapter and immutable records |
| Provision/recover/teardown | `packages/core/src/roster.ts`, `lifecycle.ts`, `mailbox.ts`, `index.ts` | DD-02/DD-07/DD-08/DD-16: ordering, uncertainty, deadlines and wake gates |
| DA adapter and strict initializer | **new** `packages/durable-agent/src/{index,initializer,binder,ownership,tools}.ts` | DD-15/DD-16 and this approved adapter delta: schema, public API mapping, scoped contributions |
| Closing-time presentation and scoped shutdown | Existing `packages/tools/src/index.ts`; chosen adapter prompt/handler code; official Consumer only under its owner's approved scope | DD-09/DD-15/DD-16: static labels, exact classifier, material removal, post-await withholding and one cleanup owner; isolated execution mapping separately approved |
| Executor/mission dependencies | DSH host and approved GAT authorization workstream; exact files discovered there | DD-09/DD-17; frozen mission/delegation contract |
| Safe views/SDK | `packages/core/src/types.ts`, `index.ts`; relevant `packages/web/` consumers | DD-10/DD-16: binder ID, protocol version, safe readiness; exclude payload/ref/workspace |
| Opt-in integration composition | **new** integration profile package/patch; existing profile tests | DD-11: exactly one initializer, dedicated provider, required features/hooks |
| Distribution | `scripts/generate-compatibility.mjs`, `installer/{index,compatibility,verify}.mjs`, compatibility artifacts and package manifests | DD-11/AD-12: new package mappings, build/export/pin and installation checks |

Do not place this implementation in standalone `packages/gat/src/memory` or use that reference-memory backend as Durable Agent storage.

For member v3, update format registration/types and projection together. Replay valid v2 members as `attachments: []`. Preserve strict rejection for unknown versions and all original child/name/lifecycle evidence. Use per-event-family version handling; avoid changing a shared version guard in a way that accepts unknown task/mission/message versions. New failed/active snapshots retain the exact provisioning attachment payload/digest.

Audit `TeamMemberView` and Remote serialization explicitly: extending a snapshot type or spreading its fields can accidentally publish host-only attachments. Views should construct a safe allow-listed binding summary. Regenerate SDK/build artifacts using repository tooling; do not hand-edit generated files.

A binary that only reads v2 cannot safely resume a log containing v3 members. Package rollback is not an event downgrade. Document downgrade refusal or an independently approved migration; never strip required attachments to permit an older binary to execute.

## 10. Delivery order and prerequisite gates

| Stage | Work and output | Exit evidence |
|---|---|---|
| S0 — Baseline and approved design | Record current GAT/DA/DSH revisions, dirty paths and relevant hashes; select API family and execution model (§2.2); accept/revise P-01–08; put approved intended deltas in `docs/gat-design/` before coding | Design-to-source map and dependency record; unresolved decisions explicitly marked |
| S1 — Binding foundation | Types, initializer migration, bounds/digests, member v3, registry and lifecycle against reserved-handle fakes | T01–T05/T08/T09 below, plus applicable GAT-only regressions |
| S2 — DSH contract qualification | Implement or verify freeze §7 reserved handle, persist-only inbox, activation, cold-recovery gate, legacy wrapper, request-refresh hook and owner-local assembly shutdown surfaces | Exact DSH revision, exports and tests; precise closing proof or explicit unsupported-path denial; no assumption based on a method name |
| S3 — DA adapter integration | Implement payload validation, ownership coordinator, Consumer handlers, refresh and lifecycle cleanup; qualify real public provider in temporary storage and applicable §7.5 behavior | T06–T08/T10–T12/T16–T21 with selected public service/composition; pinned package/build evidence |
| S4 — Production prerequisites | Integrate approved mission/lease/capability work; finish profile, packaging and compatibility verification | T13–T15/T22–T23 as applicable, and every dependency below satisfied |
| S5 — Final review and handoff | Reconcile official design, source maps and actual tested bytes; document deployment constraints and rollback | Complete evidence bundle; activation/publication only within applicable authorization |

S1 can use deterministic fakes without S2. Production child wiring in S3 waits for S1 + qualified S2, as freeze §14 requires. Pure adapter units can use fake member scopes while S2 is pending. Production dispatch is disabled until S4 is complete.

Production gate checklist (each needs an evidence locator, not just a Boolean):

- DSH materialize/persist/activate/recover contract and context-refresh hook qualified on the exact selected revision.
- API family/execution model explicitly selected, with approved identity mapping for isolated execution if used; no implicit WK/official Consumer translation or old-Session reuse.
- Closing assembly qualified with and without the Consumer, including pre-collected schemas, late responses, unknown-authority negatives and one-shot non-deadlocking cleanup.
- Public DA package version/API/features and named exports verified; storage identity ownership assumptions established.
- Exact mission authorization, task authority mapping, revocation and nested delegation enforcement qualified at executor boundaries.
- End-to-end composition uses the new binder and executable tools; tests are not exclusively mocks or standalone Consumer tests.
- GAT-only compatibility, v2/v3 replay, SDK, installer/profile/build smoke all pass on final bytes.
- Source-plane and published-entry regressions resolve the intended modules/artifacts; live-runtime acceptance, if requested and authorized, separately identifies loaded packages and the existing process. Neither source nor on-disk artifact hashes alone prove what a cached process runs.
- All accepted design deltas are reflected in official `docs/gat-design/` documentation; no target is called implemented based only on a historical mission report.

## 11. Acceptance tests and evidence

Use keyless deterministic model/host fixtures and isolated provider storage. Instrument model calls, child creation, inbox writes/releases, provider calls, binding installs and cleanup. Assert event order and durable state as well as counters; independent raw-log assertions help avoid testing only the new projection against itself.

| ID | Test / required assertions | Suggested suite |
|---|---|---|
| T01 | Every prepare/route/schema failure: zero new member rows and children; earlier leases abort once in reverse order; post-return payload mutation cannot alter persisted bytes | New core `attachments.spec.ts`, `member-binding.spec.ts` |
| T02 | JCS vectors and digest; exact bounds/+1; getters, cycles, non-JSON, duplicate binders, unsafe versions; registration mutation rejected for inactive references too | New core attachment/registry tests |
| T03 | Full success trace: zero model calls until active commit + authorization + activation; bindings/tools/context present in exact child scope | New core binding + DSH conformance |
| T04 | Inject failure at each lifecycle edge, including uncertain flush and after active commit; correct tombstone/failed/unavailable state; no duplicate install on live retry | Core binding + persistence tests |
| T05 | Concurrent prompt persistence/activation/enable/recovery: one durable initial item and at most one first request; stable errors for conflicts | DSH reserved-handle + core integration |
| T06 | Member A cannot select B's ref/scope; non-Team/Lead/stale generation cannot invoke retained closures; model arguments cannot inject authorization; no private data in prompt/errors/views | New adapter `tools.spec.ts`, composition tests |
| T07 | Missing/corrupt/unknown binder on restart denies work; changed YAML has no effect; valid recovery uses persisted declaration and a current ref; queued mailbox delivery waits for recovery/authorization | Core persistence + adapter recovery |
| T08 | Shared total deadline; slow provision, in-flight submit and slow release; late completion observed; identity remains quarantined; no late runtime authority, duplicate release or data deletion | Adapter lifecycle + core disposal |
| T09 | Valid v2 → empty attachments; v3 canonical round trip; unknown versions fail; unrelated event families keep their contracts; old binary compatibility not falsely claimed | `projection-events.spec.ts`, `persistence.spec.ts` |
| T10 | Concurrent same identity rejected before second provision; other identities independent; failed/released owner cleanup; second Team cannot invalidate first Team's ref | New adapter `ownership.spec.ts` |
| T11 | Refresh precedes every model request, replaces one section, fails closed on error; catalog only; selective reads are current per call; context remains bounded | Adapter contribution + host-hook tests |
| T12 | Candidate tool returns unconfirmed; approval-looking text cannot commit; no model commit tool; externally authorized commit visible according to refresh policy | Adapter + public DA memory lifecycle |
| T13 | Full freeze §13 authorization matrix including wrong Team/revision, ambiguity, close/revoke, simpleMode on/off; queue/bootstrap without lease causes zero model wakes | Approved executor/mission integration |
| T14 | Enabled Team blocks named/aliased/nested external delegation before provider/child/event effects; disabled behavior and default GAT initializer remain compatible | Tools/host regression suites |
| T15 | Real plugin registration → service → binder → child prompt/tool call → restart → release; packed imports/profile contain new packages; safe SDK/Web summaries; GAT-only install still works | Profile, built-library and installer verification |
| T16 | Hold physical cleanup after durable submission, without Consumer: exact closing worker remains live, membership absent, static Team labels render without strict membership calls; no extra model request; Team mutation and actual filesystem/shell write attempt denied | Tools held-closing regression + executor fixture |
| T17 | Exact known-closing isolated execution with Consumer: no new provider open/snapshot, no Consumer schema/guidance/catalog/context/body; unrelated assembly preserved; later host admission remains denied | Selected Consumer closing integration |
| T18 | Close during barrier-paused downstream assembly: remove pre-collected schemas and SDK/context contributions in returned assembly; no additional model work, recursive assembly or blanket prompt-error suppression | Consumer/host assembly fixture |
| T19 | Close during open/snapshot/read: late resource released once and never published active; late memory body withheld; old-operation drain settles without self-await deadlock; timeout and cleanup failures remain visible | Consumer async lifecycle + disposal fixture |
| T20 | Missing/replaced root/Agent/execution/generation, ambiguous or legacy-to-isolated identity still reject; active provider/bounds/revision and missing/duplicate policy errors remain loud/sanitized | Consumer negative controls |
| T21 | For approved isolated composition only: same stable member across two fresh task Sessions retains principal/content, gets distinct execution histories and current selection/leases; no old transcript, unselected memory, revived Session or overlapping cleanup authority | Isolated identity/selection compatibility fixture |
| T22 | Durable submitted result survives; closing shows cleanup-pending; terminal publication follows owned cleanup; turn errors and cleanup failures preserved; Lead task settlement and deliverable acceptance remain separate | Execution/subagent outcome regression |
| T23 | Source-plane and actual exported built-path smoke plus keyless recorded supported-profile workflow, with/without Consumer: same intended labels/closing behavior, detect stale artifact; authorized live check records actual module paths/artifact identities and existing runtime reload separately | Build/profile/session fixture; runtime owner qualification if authorized |

The acceptance matrix augments the complete freeze §13 fixture set; it does not remove requirements. Record skipped/blocked checks as such, with dependency and owner. Do not claim DA historical test counts as results of the new GAT integration.

T17–T21 are conditional on the approved isolated Consumer composition; a legacy-only target must document unsupported graceful classification and prove its strict-denial controls instead. Tests must never fabricate known-closing proof to bypass that applicability gate. T16/T22 and the isolated submission portions of T23 also require that execution model even when the Consumer is absent; the direct-continuable target still qualifies static labels, strict denial and its actual source/build/profile lifecycle. Do not add isolated execution merely to satisfy a fixture. Existing RCA source regressions are preexisting dirty work and need owner review; do not duplicate their patch or claim them executed from their presence.

Existing verification entrypoints:

```sh
# From the GAT repository root, after the implementation is available:
node --test installer/tests/*.test.mjs
python3 .ai-work/tooling/lint_all.py --strict --format text

# Set GAT_BINDING_DSH_TARGET to the reviewed installed DSH verification checkout.
# Existing verifier uses a disposable worktree; extend its suite/package list first.
: "${GAT_BINDING_DSH_TARGET:?Set the reviewed DSH verification checkout first}"
node installer/verify.mjs --target "$GAT_BINDING_DSH_TARGET"
```

GAT core/tools TypeScript suites are currently executed in the DSH workspace by the verifier; do not assume root `npm test` exists. Extend the verifier to include new suites/packages, then run focused suites during development and the full supported build/smoke at integration completion. Select the DSH revision and required dependencies explicitly; the old advertised compatible commit is not evidence for the new reserved-handle APIs.

For DA, use its pinned package scripts (`build`, `check:named-exports`) and relevant service/provider/Consumer/composition suites in the isolated test environment. Record exact commands, revisions, source hashes, exit codes and counts. Never install new packages or bypass target compatibility checks merely to make a missing test harness appear green without documenting the supported environment change.

## 12. Instructions to the implementing agent

1. Confirm the assigned execution scope from the HUMAN instruction or approved process. This proposal-writing task alone authorizes no implementation, external repository edits, merge or activation. An AIP is optional under the local override unless explicitly required by the assigned process.
2. Follow §1 reading order; re-run wiki lookup and inspect current source/tests. Record all three repository baselines and dirty files. Protect unrelated edits; do not reset the existing working tree.
3. Compare P-01–08 with approved decisions, explicitly select the API/lifecycle per §2.2 and apply §7.5 only where exact proof exists. Resolve conflicts and blocked dependencies through the owning HUMAN/workstream. Complete independent authorized foundation work where possible; never bypass a dependency with `startContinuable()` or a post-created binding hook.
4. Before each source change, update its intended design coverage from §9. Keep current implementation and target design status explicit. Do not rewrite frozen requirements to match a shortcut implementation.
5. Deliver stages in §10 with §11 evidence. Keep core generic and binders least-privileged. If delegating under the assigned process, pass the same design-first rules, exact design paths and dependency gates; source work must wait for its design delta.
6. At review, trace every requirement/test to changed symbols and the tested source bytes. Include the failure matrix, event migration, view redaction and package composition, not just the happy path.
7. Final handoff must list design files/sections updated, source files affected, acceptance results and remaining production gates. For WBS, include run-delta → official-design mapping. Refresh wiki/source-map registration through the applicable reviewed workflow; do not treat a local proposal as promoted canonical knowledge.

Required implementation evidence bundle: baseline/dirty-file record; approved decision references; selected API/lifecycle and identity mapping; design-to-source/test matrix; DSH and DA dependency qualifications; executed test/build/lint reports; lifecycle/recovery/closing traces; separate result/turn/cleanup/task/acceptance outcomes; built-entry and, where authorized, loaded-runtime qualification; supported deployment/rollback constraints; and an explicit statement of whether production activation has been authorized and performed.

## 13. Status of this document revision

This revision incorporates the binding review and the two closing proposals into a concrete candidate handoff, with proposed MVP defaults, API/lifecycle qualification, conditional closing compatibility and implementation/test instructions. It changes no runtime source, frozen contract, installed profile or canonical/wiki registration. Implementation tests, build/runtime reload and DSH dependency qualification have not been run as part of preparing this proposal.

Document verification including the closing supplement on 2026-10-04: all 14 linked local inputs resolve; code fences/whitespace and the 23 unique test IDs / 8 proposed-decision IDs check cleanly; supplied proposal hashes match the inspected bytes. Repository AIWS lint (`--strict --format text`) reported 0 errors, 37 warnings, 3005 informational findings and 1 accepted finding; exit 1 because of warnings in existing repository artifacts, unchanged from the initial document check. AIWS lint checks AIWS structures, not behavioral correctness of this design. No warning was suppressed or unrelated file repaired for this proposal.
