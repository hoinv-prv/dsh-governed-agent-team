# GAT Detail Design

Document ID: GAT-DD-001  
Version: 1.0-draft  
Source inspection date: 2026-10-04  
Status: Formal source-aligned design draft. Parent: [Basic Design](BASIC_DESIGN.md).

## 1. Authority and implementation baseline

**Source code is the source of truth for implemented behavior.** This document describes the inspected working tree, not the behavior of every historical accepted mission. Where code and prior design differ, current behavior is documented here and the discrepancy is retained explicitly. Normative proposals are reference inputs, not implemented contracts.

[Source Code Map](SOURCE_CODE_MAP.md) maps every DD ID to file/symbol/test and implementation status. [Source baseline](source-baseline.json) records exact source hashes, repository HEADs and pre-existing dirty paths. The source map contains no claim that the cited suites were run for this task.

## 2. Shared current data contracts

| Value | Current shape / constraint |
|---|---|
| Team identity | Branded root SessionId; exact live Agent registry identity resolves Lead/teammate membership |
| Member snapshot | id, name, description, continuation provider, fresh/fork context, optional model, provisioning/active/failed phase, optional error |
| Task snapshot | id, positive revision, subject, description, pending/in_progress/completed/deleted, optional ownerId, blockedBy, writeScopes |
| Mission snapshot | id/revision/title/objective/status, embedded `plan.tasks`, optional approval; no current task `missionId` field |
| Work snapshot | memberId/state/summary, optional reason/taskId, files; view adds updatedAt |
| TeamView | enabled, planRevision/phase/optional approval, optional missions, work, members, tasks |
| Message snapshot | message id, sender id/name, target id, ContentBlock content |
| Team event payload | Current strict version 2 and matching teamId; unknown version fails projection |

Core defaults are maxMembers 8, maxTasks 256, maxPendingMessagesPerMember 64, maxMessageBytes 65536 and disposalTimeoutMs 5000. Tools defaults are minExecutionMembers 2, maxExecutionMembers 4, simpleMode true and teamMembersMaxBytes 65536. The shipped host YAML patch also declares 2/4/true. Historical minimum-zero hotfix claims do not replace these inspected values.

<a id="dd-01"></a>

## DD-01 — Workspace configuration and Session Enable

**Why (Documented + inference):** [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §§5.1–5.3 separates opt-in profile availability from per-Session activation and defers destructive Disable until cancellation/history/ownership/restart semantics are defined. §6.8 explicitly preflights routes to avoid obvious partial-roster failures. Built-in fallback is documented in §6.6; treating it as a usability trade-off is an inference, not an approved security guarantee.

Basic feature: BD-01. Status: Current. Architecture decisions: AD-05, AD-06.

Input: exact Lead Agent, AbortSignal and Session cwd. Read `join(cwd, 'team_members.yaml')` using lstat/regular-file/no-symlink and pre/post byte bounds. Closed document keys are version/members; version is 1. Closed member keys are name/description/prompt/context/provider/model/reasoning_effort. Names are unique lower-kebab-case, max 64 chars; description max 200, prompt max 16384, provider/model max 200, reasoning effort max 80; context defaults fresh. Members must be nonempty and within configured maximum.

Loader errors return bounded-source built-in fallback diagnostics with cwd redacted. Defaults use the Lead LLM provider and are sliced to maxExecutionMembers. Provider/model resolution then preflights every member with `childAgentOptions`; failure stops before any member spawn.

`TeamService.enable` requires Lead role, returns existing retained teammates when any exist, otherwise calls the one registered initializer under lifecycle admission. The initializer deduplicates by Lead Session and provisions sequentially after preflight. Output is enabled/alreadyEnabled/source/diagnostics/members. It does not support live reload or transactional rollback of the entire roster.

Failure examples: TEAM_LEAD_REQUIRED, TEAM_INVALID_CONFIG (missing initializer), route resolution/aborted signal; invalid YAML itself selects defaults.

<a id="dd-02"></a>

## DD-02 — Roster provisioning and child ownership

**Why (Documented + inference):** [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §4.2 requires persisted child evidence rather than invented restart success; [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Evidence and lessons applied, calls for preserving useful work and avoiding one-new-agent-per-defect recovery. Reserving used names and checkpointing acceptance make incomplete creation observable; this causal explanation is inferred from those goals and current ordering.

Basic feature: BD-02. Status: Current. Architecture decisions: AD-01, AD-04.

`TeamRoster.spawn` admits lifecycle work; `spawnAdmitted` resolves exact Lead membership, validates name/description/provider and allocates child UUID. Under the per-root journal transaction, reject previously used names or durable member cap, then append/flush version-2 provisioning snapshot.

Call DSH `startContinuable` using reserved childId, continuation provider, prompt, root parent and AgentOptions. `checkpointInitialPrompt` flushes the child and verifies its accepted message in the child-owned suffix outside inherited fork events. Commit active only after that evidence. Errors settle failed state and stop child; conflicting terminal reconciliation raises TEAM_PROVISIONING_CONFLICT and may aggregate cleanup errors.

Names remain reserved across failed creation. Once child acceptance occurred, a failed active checkpoint must not invent an active-to-failed transition. Restart reconciliation evaluates durable child descriptor/parent/prompt evidence. It does not implement the target binder/materialize-without-admit state machine.

<a id="dd-03"></a>

## DD-03 — Journal, projection and persisted-session reads

**Why (Documented):** [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Evidence and lessons applied / Canonical plan state / Data flow, requires one durable projection and derives structural plan phase from the same committed task events to prevent second-write divergence. Successful flush-before-notify means views/waiters observe durable progress; queue/handle mechanics implement that goal.

Basic features: BD-02, BD-03. Status: Current. Architecture decisions: AD-02, AD-03.

`TeamJournal.transact(rootId, operation)` chains a per-root Promise tail. Rejected prior work does not poison later queue entries; settled tail is removed only if still current. Mutation code reads/checks candidate state within that queue.

`appendManyAndFlush` appends all prevalidated Team events, calls `ctx.sessions.flush(root.session)`, then notifies activity. This provides ordered append/flush publication, not transactional rollback of Session appends if a later flush fails.

`teamProjectionDefinition` initializes root-specific state and reduces only owned Team events. Selector teamId mismatch is ignored; owned unsupported version, strict-shape failure or illegal transition records terminal projection failure. `TeamJournal.state` rejects failed/unregistered projection. Event families: member, task, mission, plan-approved, work, message/queued and message/delivered.

`readPersistedSession` opens a read handle, reads header/full committed events with inheritedEventCount and closes in finally. Roster/mailbox examine owned suffixes rather than accepting inherited fork evidence.

<a id="dd-04"></a>

## DD-04 — Task DAG, CAS and transitions

**Why (Documented):** [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Objective / Team lifecycle / Failure handling, calls for dependency-aware work, exact revision checks and disjoint write scopes. The task-board DAG and CAS support that coordination; [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §7.2 states that the shared checkout is not isolated/locked. Write-scope diagnostics must not be promoted into a sandbox claim.

Basic feature: BD-04. Status: Current.

Create uses next numeric `task-N`, revision 1, pending/unowned status, normalized text/dependencies/write scopes and shared graph validation. Updates reject missing/deleted task and stale expectedRevision before authorizing action. Every accepted update increments task revision and flushes a complete snapshot.

| Action | Preconditions and next state |
|---|---|
| claim | pending and blockers completed; no foreign owner → in_progress, caller owner |
| release | owner or Lead; in_progress → pending without owner |
| edit | owner or Lead; at least subject/description/writeScopes supplied; preserve lifecycle |
| set_dependencies | owner or Lead; supplied blockers valid, unique, nonself and acyclic |
| complete | owner or Lead; in_progress → completed |
| reopen | owner or Lead; completed → pending without owner |
| reassign | Lead only; pending/in_progress, ready for nonempty owner → active member owner/in_progress; empty owner → pending/unowned |
| delete | owner or Lead; no nondeleted dependent → deleted tombstone |

`isStructuralTaskMutation` detects create, subject/description, deletion, dependency and write-scope changes; projection advances planRevision and invalidates structural approval. Completion/claim/owner changes are distinct from structural planning changes. `scopesOverlap` uses equality or slash-component prefix; warnings do not block filesystem writes.

Errors include TEAM_TASK_STALE_REVISION, TEAM_TASK_UNAUTHORIZED, TEAM_TASK_BLOCKED, TEAM_TASK_DEPENDENCY_CYCLE and TEAM_TASK_HAS_DEPENDENTS. No task-level mission association is implemented in the inspected type.

<a id="dd-05"></a>

## DD-05 — Plan approval and approved-chat import

**Why (Documented + inference):** [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Canonical plan state, binds approval to the reviewed revision so structural edits cannot retain stale approval. One-action import is documented in the collected [hotfix report](sources/gat-missions/legacy-agent-team-hotfix/final-report.md). Atomic prevalidation/deduplication avoids partial or duplicated imported plans; that implementation trade-off is an inference from code and the reported behavior.

Basic feature: BD-05. Status: Current.

`approvePlan` requires exact Lead, nonempty live task plan, exact structural revision and registered envelope preflights. `approvedPlanTaskSubjects` selects latest exit_plan_mode call and its one matching later successful result; rejects missing/multiple/malformed result rather than choosing older approval. Only bounded items in explicit Tasks section parse. `normalizedTaskSubject` NFKC/whitespace/case normalization deduplicates subjects.

`prepareApprovedPlanImport` preserves current nondeleted tasks, allocates only missing subjects, checks active cap/id space and creates revision-one pending tasks with empty dependencies/scopes. `importApprovedPlanAndApprove` calculates resulting structural revision, validates nonempty/staleness, runs preflights against the prepared postState, then appends task snapshots and exact approval in one flush. No invalid candidate prefix is intentionally appended.

Remote import maps business rejection to a typed plan-import result. Presence of these core APIs does not prove every current Web component exposes the import action. Current simple-mode dispatch also skips legacy plan-approval diagnostics (DD-09).

<a id="dd-06"></a>

## DD-06 — Mission snapshots and current approval shortcut

**Why (No documented justification for shortcut):** [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §10 records the synchronized immediate-approval baseline but explicitly says Lead credentials do not prove HUMAN authorship. Existing docs explain why authenticated authorization is needed; they do not establish a sufficient rationale for current self-approved creation. Preserve this gap rather than invent a safety justification.

Basic feature: BD-06. Status: Current baseline; target authorization is absent.

`TeamMissionBoard.create` requires Lead, validates title/objective and initial mission plan, allocates a mission id and flushes revision 1 with status approved and approval `{approvedRevision: 1}`. `get/list` return detached snapshots. `approve` accepts only draft at positive exact expectedRevision, advances revision and binds approval to that resulting revision.

Projection enforces approved status exactly when approval equals mission revision. Mission plan contains embedded task snapshots. Current methods do not implement host-attested HUMAN authorization, lease/revoke/close, or task-board normalization. Do not infer HUMAN provenance from caller Lead identity or mission status.

<a id="dd-07"></a>

## DD-07 — Durable peer mailbox

**Why (Documented + inference):** [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §8.2 describes durable queueing, receipt deduplication and inactive-target recovery; §10 warns against repeated sends because queued work is already durable. Stable message identity and accepted-receipt checks prevent recovery from becoming a fresh logical send; this mechanism-level reason is an inference from that goal.

Basic feature: BD-07. Status: Current.

Validate exact sender/target, ContentBlocks/serialized byte limit and pending-per-member cap, then append/flush queue event with stable message identity. Delivery is serialized/tracked and attempts Lead steer or DSH child steer/cold resume. Target acceptance checks matching team-message source in owned Session suffix; persisted target reads support inactive recovery. A live accepted target receipt is flushed before root delivered marking.

`markDelivered` checks already delivered/queued target identity under root serialization. Recover queued items after lifecycle/member recovery; delivery exceptions retain queued state and diagnostics. Cancellation before queue differs from cancellation after durable queue. Returned accepted/queued describes immediate observation, not exactly-once distributed processing.

<a id="dd-08"></a>

## DD-08 — Work, waits, interrupt and disposal

**Why (Documented):** [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Evidence and lessons applied / Member work state / Runtime and stall display, separates member facts from inferred stalls, preserves report-defective work for review and bounds autonomous recovery. Durable work state provides reviewable evidence while wait/interrupt support coordination. Current physical mutation drain beyond a timeout is observed code behavior, not a documented total-deadline guarantee.

Basic features: BD-07, BD-08. Status: Current.

`TeamWorkBoard.report` persists caller's own state. Summary/reason max 4096; blocked requires reason; working/done forbid reason; review_required requires at least one normalized workspace file; duplicate files reject. Optional task must be nondeleted and owned by caller. Work updatedAt is derived in projection. Reporting done does not itself complete a task or accept a result.

`TeamActivity.wait` accepts 10000..3600000ms, releases at most once on notification/abort/timeout and removes timer/listeners. `TeamRoster.interrupt` is Lead-only and cancels current teammate turn while preserving inbox.

`TeamRuntimeLifecycle` aborts admission, tracks mutations and aggregates unexpected settlement failures. `TeamService.disposeRuntime` coordinates runtime cleanup before projection withdrawal. `settleMutations` reports timeout but still awaits physical settlement; therefore the configured timeout is not a total hard shutdown bound.

<a id="dd-09"></a>

## DD-09 — Scoped model tools and execution guards

**Why (Documented; partial implementation of target):** [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Evidence and lessons applied / Write barrier, moves complete-envelope checks before effectful dispatch because capability mismatch and stale readiness were discovered too late in prior work. Its explicit defaults are 2–4 teammates, but no measurement justifies an exact minimum of 2. [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §11 motivates executor metadata against aliases/nesting; current code only demonstrates the inspected name guard and scoped readiness logic.

Basic feature: BD-09. Status: Current.

`apply` resolves positive safe config limits and registers approval preflight/Enable initializer. `install` registers scoped policy, tools and guard in exact Agent context; disposers reverse cleanup. Simple-mode solo Agents are not installed until enabled. Current tool names include spawn_teammate, report_team_status, send_message, list_agents, wait_agent, interrupt_agent and team_task_create/list/get/update.

Scoped policy identity is presentation metadata: `install` validates membership once and captures only role, member name and Team id as static section text. Prompt rendering must not query live membership after authority is revoked or the exact Agent leaves the live registry. The snapshot grants no authority: tool guards, readiness and domain operations continue to resolve live state and reject stale callers. Reinstallation validates membership again. Regression coverage renders an already installed scope with membership unavailable and verifies a task mutation remains denied without adding a task. This prevents the membership exception reported by downstream isolated execution submission; this checkout has no `team_execution_submit` lifecycle and does not claim downstream closing-to-completed coverage.

`readiness` combines live envelope diagnostics, configured active-durable-member minimum and (only when simpleMode false) current plan approval diagnostic. `preflight` reports current plan revision/phase, approved revision, active count, required count, readiness and diagnostics.

Guard first denies known external delegation names when Team enabled. Spawn checks mandatory envelope diagnostics and maximum member cap. Restricted task update permits structural repair actions; bounded coordination/inspection/HUMAN tools follow explicit admission classification. Remaining work requires current readiness. Name denial is not reserved nested capability metadata enforcement. Defaults 2/4 and simpleMode true override historical zero-minimum descriptions.

<a id="dd-10"></a>

## DD-10 — Browser Remote mount and projection rendering

**Why (Documented):** [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Runtime and stall display, makes suspected_stall presentation-only to avoid changing work facts or retrying from a timing inference. [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §9 explicitly documents the simplified current panel without task/mission creation controls and stale-response protection. Its reduced scope should not be inferred from leftover injected interfaces.

Basic feature: BD-10. Status: Current.

`mountAgentTeamUi` owns generated agentTeams Remote mount, locale/slot registration and disposers; browser `apply` delegates to it. `TeamAction` receives injected business functions; actual rendered component uses load/enable/listMissions/navigation, shows roster and most recently created mission. Declared injection interfaces include task/mission/plan mutations, but their declaration alone is not proof of rendered controls.

Refresh loads view/missions concurrently and rejects stale Session/generation responses. Session change resets state; open panel polls at default 5000ms, skips overlapping polls and clears timers on close/unmount. Default stallWarningMs is 180000. Transport errors and business rejections remain distinct. Last-created mission selection is not an effect-authorization decision.

<a id="dd-11"></a>

## DD-11 — Profiles, compatibility and installer

**Why (Documented):** [Installer refactor spec](../GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md) §§1–2.1 describes legitimate development edits blocked by source-file hashes and separates source integrity, DSH compatibility and installed correctness. Advisory source drift enables development installs while host preimages, patchset integrity and actual installed bytes retain strict checks. This is not permission to activate a profile.

Basic feature: BD-10. Status: Current.

Host `cordis.patch.yml` disables overlapping legacy continuation-control rows, configures one-shot subagent providers, then inserts core/tools with explicit limits. Web patch inserts browser package/timers. Profile TypeScript exports are empty; YAML bundle patches carry composition.

`evaluateDshCompatibility` classifies target against version descriptor; `inspectSource` records advisory source state. CLI parses dry-run/install/status/rollback and explicit override flags. Validate mapping, safe relative paths, symlink ancestors, controlled target state and installed file records. Install stages controlled payload/host changes and writes installation record; rollback checks installer-owned state. `installer/verify.mjs` and `verify-profile.mjs` assess installed payload/profile. No command in this design task installs or runs target verification.

<a id="dd-12"></a>

## DD-12 — Standalone governance and reference-memory storage

**Why (Documented; standalone scope):** [MCP memory proposal](../GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md) §§1–3,6,11–12 and [Threat model](../security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md) §5 T04/T06/T08/T11/T12/T14/T15 motivate scoped identity, physical isolation, no cross-scope promotion, lifecycle authority, idempotency and recoverable audit. Current in-memory standalone structures demonstrate those boundaries; they do not prove persistent production deployment.

Basic feature: BD-11. Status: Standalone; no DSH/MCP integration.

Governance functions validate project scope, derive stable Agent desk and execution identity hashes, compare requested/current identity, evaluate supplied readiness oracle, authorize exact Team plan and map native mission approval. Closed identity fields/revisions/digests prevent inference from labels alone.

`physicalPartitionKey` includes tenant/principal/project/scope-kind/owner dimensions. `PartitionStore` uses in-memory maps plus injected audit sink, anchor and lifecycle registry; operations bind decision evidence, idempotency and audit hash chain. Transaction snapshots/journal recover domain/audit publication and lifecycle/legal-hold/purge state. It is not a filesystem durable database and default in-memory/test keys are not production deployment configuration.

<a id="dd-13"></a>

## DD-13 — Standalone deny-first policy and memory wrapper

**Why (Documented; standalone scope):** [Threat model](../security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md) §5 T01–T03/T06/T07/T13 and [MCP memory proposal](../GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md) §§8–10 motivate explicit deny precedence, fresh authorization evidence, package-private MCP capability and untrusted reference output. This prevents model-supplied identity/partition claims and reference text from acquiring authority.

Basic feature: BD-11. Status: Standalone.

`DenyFirstPolicy.authorize` validates trusted request/snapshots/classification/rules; admission coordinates audit and selector, preserving deny/error evidence. `verifySelector` validates canonical hash/HMAC. A selector binds resource/action, identity, revisions, decision/correlation/time and classification/capability evidence.

`GatMemoryAdapter.invoke` accepts only explicit GAT wrapper names and closed action arguments. Raw MCP prefix, unknown tools, malformed args, absent trusted host capability or mismatched selector deny before MCP execution. Private MCP capability belongs to adapter instance; returned data is a provenance-labelled untrusted reference. This is standalone API enforcement, not a live GAT/DSH wrapper installation claim.

<a id="dd-14"></a>

## DD-14 — Standalone conformance tooling

**Why (Documented; evidence gap retained):** [MCP memory proposal](../GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md) §§0,18 and [Threat model](../security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md) §5 T16/T17 require exact implementation/vector/evidence bindings and separate activation, so passing synthetic tests cannot authorize incomplete or different deployment bytes. The collected runner-gap report explains why expected-value simulation is not implementation conformance.

Basic feature: BD-11. Status: Standalone; full baseline conformance unverified.

`parseArguments` requires exact --vectors/--evidence pairs. `createVectorDispatcher` resolves registered handlers; missing handlers fail. Scenario/runtime/CLI helpers collect operation results and required evidence bindings, raw command streams and run/reviewer/source identities. Tests and collected integration used synthetic fixtures; `PACKAGE_STATUS.conformanceStatus` remains not-executed. A runner report must not copy expected outcomes as evidence of a real transition. The [runner gap](sources/gat-missions/multi-mission-web-ui/runner-architecture-gap.md) remains the design-recovery reference.

<a id="dd-15"></a>

## DD-15 — External Durable Agent service and provider

**Why (Documented + inference):** [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §§7.1–7.2 separates Team control/Session orchestration from persistent member identity/context. The collected [integration report](sources/gat-durable-agent-integration/integration-report.md) preserves public/private API and approval/recovery boundaries. Opaque refs/selective context limit accidental storage coupling and broad memory exposure; this trade-off is inferred from those explicit contracts.

Basic feature: BD-12. Status: External; no inspected GAT production binder.

Public service has immutable API version/features and methods validateDeclaration, provision, openTaskContext, readMemoryItem, submitMemoryCandidate, commitMemoryItem, workingLocation and release. Declarations have explicit scope; refs are opaque/generation-bound. Consumer binds one explicit ref and contributes bounded deterministic path-free context and exact memory tools.

Local provider validates identity/profile/bounds. Bootstrap commits immutable object/manifest generation zero and mode anchor before current pointer. Confirmed commits require authorization, serialize by storage identity and atomically publish complete generation pointer; corrupt authority fails closed. Candidates are unconfirmed. Release blocks new admission, drains admitted work, invalidates ref and retains persistent storage. Context/read consistency is per public call; later reads need not use an earlier snapshot revision.

Private storage layout is not host API. Sibling current-source hashes are separate from mission hashes, and no external package suite was rerun here. See [integration reference](DURABLE_AGENT_INTEGRATION.md) for accepted mission evidence and deployment limits.

## 3. Target design appendix — no current GAT production implementation

The following IDs retain traceability to requested designs, but are not part of the implemented GAT baseline. Source code wins any conflict. Do not treat their reference algorithms as callable current APIs.

<a id="dd-16"></a>

### DD-16 — Required attachment binding and two-phase child admission

**Why (Documented target rationale):** [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §§1–3,7–9,14 freezes ownership so GAT and DSH work packages can proceed independently. Required binding before model admission prevents an active member executing without declared capabilities; durable snapshots prevent a mutable manifest from redefining recovery. Current roster does not yet implement this target.

Basic feature: BD-13. Status: Target. Source design: [Member binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md).

Target prepare-all validates normalized specs/routes/binder protocol/JSON value/digest bounds, then provisions/materializes without model admission, binds contributions, persists quarantined prompt, commits active and guarded activation. Required-only recovery rebinds persisted records before work; reverse cleanup preserves external data. Current source instead has no attachment field/binder registry, writes event v2 and uses startContinuable. No production file/symbol is mapped for this target.

<a id="dd-17"></a>

### DD-17 — Authenticated mission leases and nested delegation metadata

**Why (Documented target rationale):** [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §§10–11 explains that model/Lead identity cannot authenticate HUMAN authorization and aliases/nested tools can bypass prompt-only delegation rules. Exact mission leases and canonical task authority prevent stale or ambiguous approval and duplicate task state. Current mission shortcut/name guard remains a recorded gap.

Basic feature: BD-14. Status: Target. Source design: member freeze CF-08..CF-10.

Target exact host-attested HUMAN team/mission/revision lease binds task claim and every effect/wake. Structural repair/queueing exemptions never exempt downstream model admission. Canonical tasks carry missionId; registry capability union denies named/aliased/nested external delegation. Current code has immediate approved mission creation, embedded mission tasks, simple-mode plan shortcut and name-based guard. None implements the complete target contract.

<a id="dd-18"></a>

### DD-18 — Source-agnostic contracted member runner

**Why (Documented target/PoC rationale):** The collected [Agile goal baseline](sources/durable-agent-wbs-runner-mvp-agile/goal-scope-baseline-v2.md) and [member compatibility memo](sources/durable-agent-wbs-runner-mvp-agile/memo-durable-agent-team-member-compatibility-v3.md) narrow the member to one task so WBS orchestration/acceptance stays with PM/Team. Immutable identity, unknown-outcome handling and provisional handoff prevent replay or self-acceptance; accepted bounded PoCs do not prove GAT production integration.

Basic feature: BD-15. Status: Target with accepted bounded PoC references.

One normalized task binds immutable task/contract/run identity; host-supplied PlanProposal cannot widen budget/effects. Busy through execution/handoff-pending; no queue/delegation. Unsettled effects become UNKNOWN_OUTCOME, completed effects never replay. Atomic deterministic provisional handoff returns idle without PM ack; conflicting handoff bytes reject.

P0/P1/P2 are bounded external PoCs; BS1 is unfinished design. Earlier runtime-plan/checkpoint code is a separate narrowed historical implementation and cannot be mapped as complete delivery of this goal. No GAT production runner symbol is claimed.

## 4. Source/design discrepancies to preserve

| Gap | Current source truth | Historical/target input |
|---|---|---|
| Active teammate minimum | 2; positive config required | Accepted hotfix had minimum/default 0 |
| Plan admission | simpleMode true skips legacy plan gate | Hotfix described mandatory exact Team-plan approval |
| Member event/lifecycle | v2/startContinuable/no attachments | Freeze specifies v3, required binders and reserved-handle activation |
| Mission authority | Lead-created approved revision 1; embedded tasks | Freeze requires authenticated HUMAN lease and normalized task authority |
| Web control surface | Current renderer consumes Enable/view/missions/navigation | Injected types and older reports include more mutation controls |
| Runtime timeout | Mutation timeout diagnostic retains physical drain | Target total deadline cleanup is not current behavior |
| Reference memory | Standalone maps/injected registries; inactive/not integrated | Proposed production MCP/reference-memory architecture |

No source correction is authorized by documenting these gaps. Update implementation through the applicable task/approval process, then regenerate mappings and reconcile design.
