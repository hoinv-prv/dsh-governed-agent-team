# GAT Detail Design

Document ID: GAT-DD-001  
Version: 1.0-draft  
Source inspection date: 2026-10-04  
Status: Formal source-aligned design draft. Parent: [Basic Design](BASIC_DESIGN.md).

## 1. Authority and implementation baseline

**Source code is the source of truth for implemented behavior.** This document describes the inspected working tree, not the behavior of every historical accepted mission. Where code and prior design differ, current behavior is documented here and the discrepancy is retained explicitly. Normative proposals are reference inputs, not implemented contracts.

[Source Code Map](SOURCE_CODE_MAP.md) maps every DD ID to file/symbol/test and implementation status. [Source baseline](source-baseline.json) records exact source hashes, repository HEADs and pre-existing dirty paths. Mapped paths alone do not prove a test ran. Current qualification receipts in the AIP-EXEC-022 workspace identify executed suites and exact bytes; earlier receipts remain historical.

## 2. Shared current data contracts

| Value | Current shape / constraint |
|---|---|
| Team identity | Branded root SessionId; exact live Agent registry identity resolves Lead/teammate membership |
| Member snapshot | id, name, description, continuation provider, fresh/fork context, optional model, provisioning/active/failed phase, optional error and immutable required attachments |
| Task snapshot | id, positive revision, immutable missionId for executable tasks, subject, description, pending/in_progress/completed/deleted, optional ownerId, blockedBy, writeScopes; adjacent v2 history may omit missionId |
| Mission snapshot | id/revision/title/objective/status, canonical `plan.taskIds`, authorization/revocation generations, optional exact host-attested approval; embedded `plan.tasks` is historical and never executable authority |
| Work snapshot | memberId/state/summary, optional reason/taskId, files; view adds updatedAt |
| TeamView | enabled, planRevision/phase/optional approval, optional missions, work, members, tasks |
| Message snapshot | message id, sender id/name, target id, ContentBlock content |
| Team event payload | Member writes v3; mission/task/plan/control authority uses its strict v3 contracts. Strict adjacent v2 replay remains family-specific; v2 members supply empty attachments and historical approvals do not grant execution authority. Matching teamId and known family version required |

Core defaults are maxMembers 8, maxTasks 256, maxPendingMessagesPerMember 64, maxMessageBytes 65536 and disposalTimeoutMs 5000. Tools defaults are minExecutionMembers 2, maxExecutionMembers 4, simpleMode true and teamMembersMaxBytes 65536. The shipped host YAML patch also declares 2/4/true. Historical minimum-zero hotfix claims do not replace these inspected values.

<a id="dd-01"></a>

## DD-01 — Workspace configuration and Session Enable

**Why (Documented + inference):** [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §§5.1–5.3 separates opt-in profile availability from per-Session activation and defers destructive Disable until cancellation/history/ownership/restart semantics are defined. §6.8 explicitly preflights routes to avoid obvious partial-roster failures. Built-in fallback is documented in §6.6; treating it as a usability trade-off is an inference, not an approved security guarantee.

Basic feature: BD-01. Status: Current. Architecture decisions: AD-05, AD-06.

Input: exact Lead Agent, AbortSignal and Session cwd. Read `join(cwd, 'team_members.yaml')` using lstat/regular-file/no-symlink and pre/post byte bounds. Closed document keys are version/members; version is 1. Closed member keys are name/description/prompt/context/provider/model/reasoning_effort. Names are unique lower-kebab-case, max 64 chars; description max 200, prompt max 16384, provider/model max 200, reasoning effort max 80; context defaults fresh. Members must be nonempty and within configured maximum.

Loader errors return bounded-source built-in fallback diagnostics with cwd redacted. Defaults use the Lead LLM provider and are sliced to maxExecutionMembers. Provider/model resolution then preflights every member with `childAgentOptions`; failure stops before any member spawn.

`TeamService.enable` requires Lead role, returns existing retained teammates when any exist, otherwise calls the one registered initializer under lifecycle admission. Core deduplicates by exact Lead object. The initializer returns normalized specs; core validates the entire roster before sequential legacy provisioning with empty attachments. Required attachments fail before any row until a qualified reserved-child host is connected. Output is enabled/alreadyEnabled/source/diagnostics/members. It does not support live reload or transactional rollback of the entire roster.

Failure examples: TEAM_LEAD_REQUIRED, TEAM_INVALID_CONFIG (missing initializer), route resolution/aborted signal; invalid YAML itself selects defaults.

<a id="dd-02"></a>

## DD-02 — Roster provisioning and child ownership

**Why (Documented + inference):** [Feature reference](../GAT_DESIGN_AND_FEATURE_REFERENCE.md) §4.2 requires persisted child evidence rather than invented restart success; [Golden V1 design](../golden-reference/2026-09-12-governed-agent-team-v1-design.md), Evidence and lessons applied, calls for preserving useful work and avoiding one-new-agent-per-defect recovery. Reserving used names and checkpointing acceptance make incomplete creation observable; this causal explanation is inferred from those goals and current ordering.

Basic feature: BD-02. Status: Current. Architecture decisions: AD-01, AD-04.

`TeamRoster.spawn` admits lifecycle work; `spawnAdmitted` resolves exact Lead membership, validates name/description/provider and allocates child UUID. Under the per-root journal transaction, reject previously used names or durable member cap, then append/flush version-3 provisioning snapshot with empty attachments on the legacy path.

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

## DD-06 — Canonical missions and host-attested approval

**Why:** [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §10 distinguishes Lead credentials from HUMAN authorship. The approved prerequisite design (§7, DD-17) replaces the historical immediate-approval shortcut with authenticated exact control receipts.

Basic feature: BD-06. Status: Current; authority details in DD-17 and §7.

`TeamMissionBoard.create` requires the Lead, validates title/objective, rejects nonempty embedded task snapshots and commits a revision-one draft with empty canonical task IDs and zero authorization/revocation generations. Canonical tasks carry immutable `missionId`; historical embedded tasks remain replay evidence. `get/list` return detached snapshots, and list order selects no execution scope.

Approve, revoke and close consume an exact host-attested control receipt inside the serialized root transaction. Approval requires the current draft revision and captures receipt identity/digest/session and authorization generation. Revoke/close advance the mission revision/revocation generation and remove approval. Exact committed mission/task/executor leases are checked at wake, refresh, model dispatch and effect boundaries; failed authority publication denies execution. Historical v2 approval never supplies a new lease.

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

Private storage layout is not host API. Sibling current-source hashes remain separate from original mission hashes. AIP-EXEC-022 records an independent rebuild of pinned WK exports and real public-provider integration checks; it does not repeat or inherit every historical external mission suite. See [integration reference](DURABLE_AGENT_INTEGRATION.md) for accepted mission evidence and deployment limits.

## 3. Binding and authority contracts; remaining task-runner target

DD-16 and DD-17 are implemented under the approved deltas in §§5/7/8. DD-18 remains future scope. Source maps and exact qualification receipts identify delivered behavior; historical target algorithms alone do not establish callable APIs.

<a id="dd-16"></a>

### DD-16 — Required attachment binding and two-phase child admission

**Why (Documented target rationale):** [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §§1–3,7–9,14 freezes ownership so GAT and DSH work packages can proceed independently. Required binding before model admission prevents an active member executing without declared capabilities; durable snapshots prevent a mutable manifest from redefining recovery. The production roster now implements required binding through the reserved host bridge specified in §8.

Basic feature: BD-13. Status: Current required-binding implementation. Source design: [Member binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md).

Prepare-all validates the complete normalized roster/routes/binder protocol and bounded canonical attachment records before provisioning. Core materializes a reserved child, binds exact-generation owner contributions, persists initial input while quarantined, commits active and permits only explicitly authorized activation. The real host scope owns prompt/tools/refresh and closes synchronously on required withdrawal. Same-generation retry retains live resources; reconstruction recovers immutable persisted records before staged mailbox acknowledgement and release. Reverse bounded cleanup retains physical ownership and late-failure diagnostics without deleting provider data. Empty attachments retain their qualified legacy path. See §§5/8 and current composition/provider/core receipts for failure ordering and actual public imports.

<a id="dd-17"></a>

### DD-17 — Authenticated mission leases and nested delegation metadata

**Why (Documented target rationale):** [Member-binding freeze](../GAT_MEMBER_BINDING_CONTRACT_FREEZE.md) §§10–11 explains that model/Lead identity cannot authenticate HUMAN authorization and aliases/nested tools can bypass prompt-only delegation rules. Exact mission leases and canonical task authority prevent stale or ambiguous approval and duplicate task state. The approved prerequisite implementation replaces that historical shortcut and name-only guard with exact authority and immutable nested capabilities.

Basic feature: BD-14. Status: Current prerequisite and integrated authority. Source design: member freeze CF-08..CF-10.

Exact host-attested HUMAN Team/mission/revision control binds canonical task claims and current executor leases. Revalidate generation, committed mission/task/approval state and cancellation at every wake, request/refresh, effect and staged acknowledgement commit boundary. Structural repair and queueing exemptions never authorize downstream dispatch. Canonical task `missionId` is immutable; registry captures capability unions and denies named, aliased and nested external delegation. Historical approved v2 records and embedded tasks retain no executable authority. See §7 for host ownership/matrix and §8 for the production bridge.

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
| Member lifecycle | v3/strict v2 replay; required binding through real reserved host scope and guarded recovery, with empty legacy behavior preserved | Initial foundation had no production bridge; §8 supersedes that snapshot |
| Mission authority | Draft creation, canonical task mission association, exact authenticated controls/current executor leases | Historical immediate approval/embedded tasks do not supply authority |
| Web control surface | Current renderer consumes Enable/view/missions/navigation | Injected types and older reports include more mutation controls |
| Runtime timeout | Required binding uses one bounded lifecycle deadline, synchronous cutoff and observed late cleanup; legacy mutation drain retains its own semantics | No timeout permits freeing unsettled provider identity or reopening runtime authority |
| Reference memory | Standalone maps/injected registries; inactive/not integrated | Proposed production MCP/reference-memory architecture |

No source correction is authorized by documenting these gaps. Update implementation through the applicable task/approval process, then regenerate mappings and reconcile design.

## 5. Approved implementation delta — AIP-EXEC-022

Approved on 2026-10-04: proposal P-01–P-08; WK-style adapter with current direct-continuable members. This section specifies intended changes **before source implementation**. It is project draft design, not Truth promotion, a contract revision or production activation evidence. The member-binding freeze §§3–14 remains normative. Isolated execution and the official DSH Consumer are outside this selected implementation.

### DD-01 / DD-16 — normalized roster ownership

The single initializer returns `TeamInitialization` containing `source`, bounded diagnostics and normalized `TeamMemberSpec[]` (`name`, `description`, `initialTask`, `context`, `continuationProvider`, optional AgentOptions and required attachments). Core deduplicates Enable by exact Lead object and owns complete-roster validation/preparation followed by provisioning. The default adapter still owns existing YAML fallback and route preflight; it no longer spawns members. Explicit Durable declarations use their separate strict adapter and never select unbound defaults.

Before any durable member row, validate all names, prompts, contexts, limits, routes and attachment registrations/output. A requested attachment without a qualified reserved-host integration fails closed before rows/children. Generic prepare/lifecycle modules can be exercised against deterministic ports; neither installing those modules nor returning a Consumer descriptor qualifies production integration. GAT-only members continue through the existing compatibility path with empty attachments until the host reserved contract is qualified.

Initial-task preflight uses the same content-block validation as replay: core block variants must match their fields, while documented plugin tags retain replay compatibility. Readiness counts exclude any required binding that is unavailable or failed; closed tool result schemas admit only the safe binding summaries.

### DD-03 / DD-16 — bounded records and replay

`attachments.ts` validates detached plain acyclic JSON without invoking accessors; reject sparse/custom arrays, symbols, non-finite numbers, unsupported values and invalid Unicode surrogate strings. Implement RFC 8785 ordering and ECMAScript numeric rendering, including negative zero normalization. Requests and prepared records enforce freeze §5 bounds; complete records include digest/envelope bytes. Each record is validated with root depth zero; nodes are summed across records. The wrapper array participates in the aggregate canonical byte limit. Digests cover canonical payload bytes only. Clone and deeply freeze returned records before persistence; validate again on replay.

`team/member` writes v3; a strict v2 parser supplies empty attachments. Unknown member versions and unrelated family versions reject independently. Projection enforces unchanged attachment canonical value/digest across provisioning→active/failed, and its cached state version increases. Types retain an explicit legacy v2 snapshot for old event fixtures. Durable snapshot attachment storage is host-only; `TeamMemberView` allows only binder id/version/readiness summaries, constructed explicitly.

### DD-02 / DD-07 / DD-08 / DD-16 — generic binding port

`member-binders.ts` owns one registration per binder/version and requires an injected authoritative durable-reference enumeration (including inactive records); mutation cannot replace a referenced registration. Deterministic prepare-all detaches/revalidates every returned value and builds digests before provisioning. Every successful prepared resource transfers to a binding once or aborts once; cancellation/validation failure aborts in reverse order. Registry participant errors are bounded host diagnostics, never payload/ref exposure.

`member-binding.ts` uses an explicit reserved-child port, durable journal port and trusted execution-authorization port. The caller supplies exact Team/member/generation identity and least-privileged capability scope. Success is prepare-all→provisioning flush→materialize without admission→bind/contributions→quarantined initial persist→active flush→readiness→authorized activate. A stable member initial-message key excludes transient generation. Journal uncertainty is resolved through committed evidence before a failed edge is written. After active commit, a valid live retry preserves its binding and only retries publication/activation; reconstruction cleans the old generation before recovery. Recovery validates stored records and child evidence, never rereads YAML, and releases existing initial/mailbox work only after bindings and authorization succeed. No production caller is connected before qualified S2 and authorization dependencies.

All cleanup consumes one remaining-deadline signal; cutoff is synchronous, release reverse-ordered, promises observed even after timeout, and late callbacks never install authority into a lost generation. Non-cancellable provider cleanup retains ownership quarantine until actual settlement. Generic foundation shutdown is separate from the legacy runtime mutation drain; do not claim the latter becomes bounded merely because a new standalone port is present.

Preparations pin registrations until abort settles or ownership transfers to a durably recorded binding. Required-binding rows are excluded from every legacy wake path, including already queued mailbox recovery and live target resolution. Unavailable publishers cannot interrupt admission cutoff or resource cleanup. A cancelled acquisition remains observed: late prepared resources abort, late children tombstone/drain, and late bindings close/settle/release without activating. Bounded cleanup invokes all reverse callbacks even if an earlier callback ignores cancellation.

### DD-09 / DD-15 / DD-16 — WK adapter

Proposed `packages/durable-agent/src/{initializer,binder,ownership,tools}.ts` uses only WK public service/Consumer interfaces. Persist schema v1 payload (trusted `serviceBindingKey`, independently verified `workspaceRealpath`, immutable declaration); never persist a ref, capability scope or prepared lease. Name equals GAT member name. Require API v1 plus selective-read/candidate flags; reject global/fork for this adapter. Dedicated provider and single-host workspace are composition preconditions, not a claimed distributed lock.

An identity coordinator shared across this binder's Teams reserves canonical workspace/name before provision; release once through a memoized promise; retain identity if physical cleanup is pending. Executable closed-schema read and candidate handlers close over the Consumer; validate current exact scope/generation and execution policy before and after asynchronous responses. Candidate remains unconfirmed; host approval cannot come from model arguments. One coherent bounded `modelContribution` refresh replaces its owner section before every authorized request; errors prevent requests. Existing static Team policy labels remain presentation-only. On this direct-continuable target authority loss strictly rejects; no isolated known-closing classifier is fabricated. Cutoff removes listeners/tools immediately and withholds late context/bodies without awaiting cleanup from an operation that cleanup itself must drain.

### DD-10 / DD-11 / DD-17 — deferred host integration

Safe summaries, supported opt-in profile composition and package build/export/installer coverage ship only with evidence for the exact selected host. The new adapter may be tested in fake scopes and real temporary provider storage first. Reserved inbox/model admission, refresh gating, authenticated exact mission/task leases and immutable nested capability classification remain production prerequisites owned by their respective workstreams. A v2-only package refuses v3 logs; installer rollback never strips attachments. Source/test mapping must identify independent foundation evidence separately from integrated production evidence.

## 6. Historical foundation qualification — AIP-EXEC-022

**Historical snapshot before AIP-EXEC-023 and production §8:** the gated statements below describe that inspection only. Current implementation follows §§7–8 and the current source map.

The intended §5 delta preceded source changes. Initial foundation sources and test locators are mapped in SOURCE_CODE_MAP.md. The WK adapter is a separately buildable, explicit integration library; its YAML loader, exclusive owner coordinator, executable read/candidate tools and request refresh run over trusted ports. It imports the selected WK public service/Consumer exports only. Snapshot prompt is bounded to 1 MiB; read output to 2 MiB; candidate output to 128 KiB. Provider cleanup keeps identity quarantined until actual settlement and never deletes persistent data.

At that inspection, production status remained gated. Inspected DSH APIs combine materialization and initial dispatch; cold resume also releases messages directly. The inspected request hook runs after prompt rendering and cannot replace message content. Exact authenticated mission/task leases and immutable nested capability union are not qualified. Core therefore refuses nonempty attachments before rows, skips attached provisioning reconciliation and denies attached target resolution/mailbox recovery; tools exclude unavailable bindings from readiness. No automatic Durable profile, supported installer activation or known-closing isolated classifier is claimed.

Verification, remaining prerequisite ownership and applicability decisions live in the AIP workspace acceptance-matrix.md, dependency-qualification.md and implementation-handoff.md. Historical collection and wiki registration results remain historical evidence; source mapping changes do not promote wiki/canonical content.

## 7. Approved prerequisite implementation delta — AIP-EXEC-023

HUMAN authorized the separate DSH host worktree at c291e7961a515f6d7af9304e7fd1d257929aef26 and the authority/capability prerequisites on 2026-10-04. This intended design precedes all prerequisite source edits. The direct-continuable WK target and frozen semantics remain unchanged. Deployment remains separate; qualification status changes only with executable evidence.

### DD-02 / DD-03 / DD-16 — reserved host lifecycle

DSH owns opaque materializeContinuable/recoverContinuable handles with exact child Agent/scope and persisted activation inspection. New calls separate materialized, inbox-persisted, activated, aborted and disposed; use freeze §7 stable errors. Materialization never admits a user inbox item or model work. Initial prompt, exact idempotency key/digest and cancellation/release facts are durable child-owned events. Persist-only flush completes before return; same key/content returns original message id, differing content fails. Child mutex serializes persistence/activation/disposal and surviving durable state reconstructs idempotently. Activation releases the existing non-tombstoned item exactly once; recovery starts with the gate closed even if the persisted state was activated. Legacy startContinuable performs staged operations and retains behavior only for children not requiring explicit recovery. Ordinary send/cold resume cannot bypass a reserved owner's gate. All release/activation/provider requests retain exact generation ownership, cancellation, shared bounded teardown and observed late resources. DSH APIs do not import GAT or accept arbitrary binder callbacks.

### DD-09 / DD-15 / DD-16 — prompt refresh and model admission

DSH supplies an awaited owner-scoped extension before rendering every actual model request, including retries. Binder refresh replaces its existing contribution and does not append duplicate sections. Assembly is refreshed before rendered system text is reconciled into logged model history; model-visible context remains reconstructable from durable system/message events. Existing request-route hook remains route-only. Refresh failure, cancellation or owner disposal prevents provider dispatch and late contribution publication; other owners' sections remain intact. GAT revalidates exact execution lease at every model admission as well as tool/effect/wake boundaries. Registration/disposal uses reversible Cordis effects.

### DD-04 / DD-06 / DD-17 — HUMAN approvals and exact scoped authority

Mission creation from model/Lead operations creates draft state; historical auto-approved mission records do not acquire HUMAN authority on replay. Trusted authenticated host control ingress produces a process-local opaque approval receipt with exact action, Team/Agent identity, mission/plan revision, unique approval event id and canonical action digest. Receipt minting occurs only in verified host ingress, not a public model argument, ordinary Service call or unverified programmatic Gateway invoke; receipts cannot be JSON-cloned, forged, cross-used or consumed after their invocation scope closes. Human-facing Remote/command handlers consume the receipt once and append durable provenance. Exact trusted ingress must be qualified against its actual authentication implementation before accepting approval.

Authority publication follows durable commit: pending, failed or false-result journal flush cannot make a newly appended mission/plan approval or member-add grant executable through the live in-memory projection. Admission checks require committed provenance; a concurrent binding/effect during an uncommitted authority append fails closed. This is the intended implementation of the durable approval boundary, before dependent journal changes.

GAT owns opaque per-exact-Agent execution leases in a private runtime store. Each lease records Team id, mission id/revision, authorization event id/digest, issuance/revocation generation and canonical task association. Task-bound issuance derives from the canonical task's immutable missionId and the mission revision authorized for the exact structural task-plan revision; task identity is not inferred from first/current list order. Mission taskIds refer to the canonical Team board; embedded historical snapshots remain explicit legacy views and never become a second executable board. Structural task/mission mutation invalidates authority; close/revoke invalidates all dependent live leases. Public task effect operations, working/done reports, model requests, child activation/resume and queued mailbox release check the current projected authority immediately before effects. New authority/task data has explicit event-family versions and adjacent read adapters; no released log bytes are rewritten.

Freeze §10 control/read/bootstrap exemptions remain exhaustive; wrappers inherit most restrictive descendant classification. Bootstrap can establish quarantined resources and queue messages without a mission execution lease, with separately host-attested member-add approval where required; it cannot release model work. Simple mode requires exact HUMAN mission approval; non-simple mode additionally requires exact current HUMAN plan approval. Existing static Team labels remain fixed while live guards remain strict. Unknown, missing, ambiguous, wrong-Team, stale, replaced-Agent, closed or revoked scopes deny with safe stable reasons. Model-visible approval wording grants no authority.

### DD-09 / DD-17 — registry-owned nested capabilities

DSH ToolDefinition permits explicit capability keys and declared nested tool references; registry registration captures immutable normalized metadata detached from mutable definitions. Reserved external-delegation is attached to every shipped subagent/fork/workflow/Ralph entrypoint regardless of alias. Alias/wrapper/composite registrations retain source/descendant capability union; cycles/missing required descendant metadata deny rather than widen an exemption. The executor attaches captured capabilities to immutable execution identity and checks current policy before pre-execute/provider/tool/child/event side effects at each nested dispatch. Async nested calls inherit their parent union and cannot replace it through arguments or around-dispatch identity mutation. PTC run_code checks each actual descendant boundary without globally prohibiting harmless Team inspection. GAT combines capability denial with compatibility name fallback when enabled; disabled Team semantics remain unchanged. Explicit read/control exemptions cannot cover unknown or effectful descendants.

### File ownership and qualification

Reserved host lifecycle/request refresh owner: DSH packages/subagent/subagent, packages/core/agent and packages/core/agent-loop plus their owning docs/tests. Capability owner: DSH packages/core/tools and shipped delegation Consumers/wrapper/PTC routes. Authority owner: GAT packages/core/src/{types,projection,mission-board,task-board,index,roster,mailbox,work-state} and packages/tools policy; DSH authenticated control ingress/gateway as required. Source edit ownership is disjoint; shared files require coordination. Review exercises actual host registry/provider/inbox/auth ingress and independent durable observations, complete freeze §13 matrix, public built imports and affected docs/SDK gates. Formal source maps reconcile after evidence; parent AIP022 consumes exact receipts and does not infer production eligibility from source presence.

### DD-04 / DD-17 — authority qualification details

Authenticated admission minting remains private inside the verified Connection HTTP dispatcher; public imports expose receipt consumption and invocation binding only. Exact current-plan revision and receipt identity are captured in each governed-mode lease, so changing policy from simple to governed requires a new binding. Task execution and working/done reports revalidate inside the canonical journal transaction after queue admission, before any append. A claim derives its lease from the explicitly requested canonical task inside that same transaction; no prior current-mission selection supplies authority.

Enable consumes an exact authenticated Session Enable receipt before initializing its configured roster. The protected Remote approveMemberAdd action appends a durable exact specification receipt and grants one non-replayable creation permission in the exact live Lead scope. Additional creation consumes that grant inside the member-row transaction; a model tool cannot mint one from approval wording or transfer it across Lead generations. Enable authorizes its initializer-selected specifications with the authenticated invocation receipt. Member-add approval evidence is retained in a distinct durable event; replay never recreates a grant. Bootstrap remains quarantined and requires a separate current mission lease at activation and model admission.

Canonical authority publication also waits for a successful durability flush. Live Session projection can observe appended snapshots before asynchronous persistence finishes; TeamJournal records pending/failed authority publication and every lease bind/effect/model admission rejects that interval. A false or rejected flush leaves the exact root unavailable for execution in that process until explicit recovery; a memory-only approval never grants authority. Member-add receipts use the same tracked append/flush path, and grants publish only after success.

Task-derived lease publication follows successful durable claim inside the canonical transaction. A claim preflight validates the explicit task/mission association without granting execution; a failed stale, blocked or owned-task claim leaves no new lease. Task-scoped bind and every subsequent effect/model check require the exact current owner Agent and `in_progress` status, so release/completion/reassignment revoke that scope. Lead administrative task operations may instead use an explicitly host-bound mission scope for that same canonical mission; they do not derive a work lease from an unclaimed task.

#### Prerequisite generated-reference ownership

The isolated qualification tree retains original DSH prototype files while the installed GAT packages replace their build references. Generated persistence, scoped Cordis and client references must use the explicitly selected replacement declarations, without deleting retained source or hand-editing generated artifacts. Catalog discovery excludes a retained prototype only when the repository build entry explicitly excludes it and references its replacement; incomplete or contradictory replacement configuration fails closed. Every other source remains in the discovery corpus. This intended tooling delta precedes generator changes and does not qualify a deployable installer revision.

DSH exact Agent execution guards are synchronous and owner scoped. GAT registers a generation-bound canonical lease check through `agent.ctx.agents.guardExecution`. DSH checks all guards after every asynchronous model-admission listener, again immediately before provider streaming, and after reserved activation flush immediately before inbox release. No asynchronous listener or await separates the final check from the protected release. GAT withdrawal releases its scoped guards; a replacement Agent generation never inherits them.

### Prerequisite mailbox delivery publication

An admitted mailbox delivery may publish its durable delivered receipt only after the exact target Session flush reports success. A false result or rejection leaves delivery unacknowledged and fails closed; a retry preserves message identity. This applies to warm delivery and explicit recovery delivery after exact execution authorization. It does not release a quarantined child or create authority from queued input. The implementation and regression must observe a false child flush separately from a thrown flush before claiming a durable receipt.

### Prerequisite model-visible mailbox contract

The `send_message` tool must describe exact delivery behavior: a message for an inactive or quarantined member is queued without model wake; subsequent delivery requires explicit host recovery and a current exact mission/task execution binding. Ordinary model input cannot request generic cold resume or grant that binding. Update the affected tool description and its owning model-visible schema/description expectation using the established snapshot workflow; retain the existing runtime delivery and denial assertions.

### Prerequisite live delivery and recovered release

Reserved children intentionally reject the generic subagent continuation delivery route. The GAT mailbox owns the exact live target and must, after exact lease revalidation, steer a typed `team-message` user item directly to that admitted Agent, then checkpoint its durable receipt. An absent target remains queued; only host recovery reconstructs it. The generic route remains denied for explicitly reserved children.

Durable `activated` history does not imply the recovered generation's execution gate is open. The roster tracks successful release per reserved-handle identity, separately from durable state; every newly recovered handle requires `activate` after exact binding. A successfully released warm handle is not reopened on later mailbox deliveries. Regression evidence must cover warm follow-up, explicit cold recovery with consumed initial input, and continued quarantine without a lease.

### Prerequisite legacy continuation prompt compatibility

The automatic legacy continuation wrapper must preserve its parent-return prompt suffix and actual child-to-parent `send_message` behavior. Capability metadata snapshots may detach the ToolDefinition object; adjacent sender recognition must use exact registry-owned provenance rather than original definition object equality. The reserved explicit GAT path retains its own admitted initial item and does not receive accidental generic delivery authority. SDK acceptance observes the child's tool effect and actual parent mailbox/history, independently from model prose; a recording that loses the relay is a regression.

### Prerequisite failed-spawn cleanup deadline

A reserved spawn that fails during materialization or initial publication uses one fresh cleanup deadline based on the configured Team disposal bound, independently of the already cancelled request. Close execution synchronously, start abort/tombstone and dispose cleanup with that deadline, and retain their physical settlement observers. A stuck flush or disposal cannot hold the spawn failure response indefinitely. Report the original creation failure together with cleanup timeout/failures; publish the failed member edge only when its own durable journal operation succeeds. A late cleanup cannot reopen or duplicate the child. Add a blocked-child-cleanup regression using the actual reserved handle.

### Prerequisite Team withdrawal cutoff

Closing the Team runtime synchronously revokes all further lease binding, execution assertions, activation and recovery admission, even while durable mutation drainage temporarily retains its projection. `bindExecution` and `assertExecution` reject the closed lifecycle before reading authorization. Recovery and activation join the runtime cancellation signal, are tracked as admitted operations, and revalidate at each actual release/request boundary. Disposal removes the final guard only after closing the relevant execution gates; a retained valid mission receipt cannot reopen a withdrawing Team. Regression evidence blocks physical disposal settlement and independently observes denied activation/model admission with zero wake/provider effects.

### Prerequisite independent Agent driver context

An independently scheduled Agent turn is a new root tool execution context. The host Agent-loop wraps each fresh driver with a trusted registry operation `withAgentDriver(agent, callback)`, which validates the exact live Agent generation and exits the enclosing tool AsyncLocalStorage while starting that driver. The caller's context is restored immediately after scheduling; asynchronous work inside the new driver retains its detached root. Ordinary nested `tools.execute` keeps ambient-parent inference and rejects wrong-Agent, stale or forged parent tokens. This operation is host-only scheduling infrastructure, never a model-facing tool or a permission to dispatch a descendant without capability checks. SDK regression evidence must observe successful child-to-parent relay while the direct cross-Agent nesting negatives remain denied.

### Prerequisite authority publication families

The committed-publication barrier protects events that establish or change execution authority: mission, canonical task, current-plan approval, member/member-add approval, and Team enable/control state. Pending or failed publication of those facts denies binding and final execution assertion. Mailbox queue/delivery and work-status facts do not establish or revise authority, so their independent pending flush does not suspend an otherwise valid exact lease. Every family still requires a successful flush before publishing its own durable acknowledgement/notification; no false or failed delivery receipt becomes durable authority. Test a warm admitted child's request concurrently with delayed mailbox acknowledgement, separately from blocked mission/task publication.

### Prerequisite active member authority

Teammate execution binding and every execution assertion require the exact canonical member row to be `active`. A live provisioning, failed or missing member remains eligible only for its established inspection/queue/control operations. Persisted initial admission does not itself make that member active or authorize execution. Recovery settles the durable roster transition before trusted host binding and release; an early bind/activate attempt observes zero model requests and wake effects.

### Prerequisite public API documentation completion

Before final qualification, complete exported GAT API JSDoc summaries and parameter/return descriptions against the contracts above. This documentation-only source delta changes no signatures, persistence payloads, scheduling or authority behavior. Rebuild generated references from the documented declarations and refresh mapping anchors after comment insertion; do not replace executable conformance with documentation completeness.

### Prerequisite authorization matrix qualification

The prerequisite conformance report must enumerate the complete simple/governed × disabled/enabled × selected mission absent/draft/authorized/stale/closed × plan unapproved/current/stale matrix. Exercise reachable states through actual host control and effect dispatch. Distinguish absent selected scope from an unrelated approved mission; no list-order inference supplies authority. Disabled simple-mode Agents retain ordinary tool behavior before Team tool installation; disabled governed-mode Agents retain the existing roster/current-plan readiness restriction. Where authenticated plan preflight makes a disabled/current or disabled/stale tuple unreachable, report that constraint and its actual rejection rather than manufacture approved state. Enabled simple mode ignores plan approval only after exact mission authorization; enabled governed mode requires both, and every denied effect body stays uncalled.

### Prerequisite source lint reconciliation

Before final acceptance, reconcile the imported GAT prerequisite source with the host's required style and type-aware lint. Formatting, explicit unknown error boundaries, local narrowing and removal of redundant assertions must preserve the existing runtime validation, malformed-input rejection, guard order and cleanup ownership contracts. Restore any accidental annotation-edit statement/export loss against the prior qualified behavior. Do not suppress a safety check solely because its input has a static type; expose and validate the actual untrusted boundary instead. Re-run affected behavior and compare pre-comment and final built JavaScript, explaining equivalent lint-only differences separately.

### Prerequisite commit-check reconciliation

Before committing the qualified work, satisfy the host's staged-file lint for all included source and test fixtures. This delta permits parentheses, indentation and line wrapping without changing executable expressions, exports, guards, validation or cleanup ordering. Fixture completion types may express the existing void return through `ReturnType<() => void>` where the staged rule rejects method-level void type arguments; preserve resolver calls and emitted JavaScript. Retain required type-aware suppression comments even when staged lint omits type analysis. Compare normalized emitted source before and after, refresh affected declaration pointers and source hashes, and rerun affected fixtures and required documentation checks. Keep the earlier qualification receipt as history; bind the commit to the final corrected bytes separately.

## 8. Production composition implementation delta — AIP-EXEC-022

The HUMAN requested completion of the remaining AIP-EXEC-022 work on 2026-10-04. This intended delta precedes its source changes and consumes the exact AIP-EXEC-023 host commit `5c02ce9f3e44dfce3f87498f65cf684194ad4572`. The selected WK provider remains `a8e215433ae050e36e0ba27205701be1a5f114a1`, API v1, workspace/fresh and direct continuable members. Qualification and activation remain separate; no deployed host or canonical knowledge is changed by these decisions.

### DD-01 / DD-02 / DD-16 — connected binder ownership

TeamService exposes host-only member-binder registration and owns a registry connected to the roster. Registering a binder supplies no Team mutation or execution permission. Registration removal asynchronously enumerates persisted Sessions, strictly reads/project-checks durable member records, merges live projected records and retains inactive references before attempting the registry disposer. A failed or incomplete scan refuses removal. Pending preparations retain their existing registry pins. Observed records remain authoritative until a complete newer durable scan proves otherwise; losing a live Agent does not erase references. During whole-Team-service shutdown, keep any referenced registration inert in its closed owner instead of attempting dynamic removal; runtime admission and contributions are already closed, and the entire registry expires with its service. This does not permit replacement or unregistering a referenced binder in a live service.

Enable validates normalized specifications and continuation/model routes for the complete roster, allocates exact child/generation identities and prepares every required attachment before the first member row. Each prepared member flows through the existing generic provisioning orchestration. A single explicitly approved add uses the same preparation and resource ownership. The empty-attachment path retains its existing reserved-host behavior. Nonempty attachments require the registered real host bridge, never the legacy rejection being deleted in isolation. Reverse abort cleans unused preparations if a later member or admission fails.

The roster owns the exact reserved handle and BoundMemberRuntime for each attached live child. Generic journal callbacks append/flush unchanged canonical attachment records at provisioning, active and failed edges. Committed-phase inspection reads persisted Lead events rather than treating an appended, memory-only projection as durable evidence. The host bridge materializes/reconstructs exact children without admission, validates parent/provider/descriptor and initial-admission facts, and maps persist, activate, tombstone and dispose to the qualified DSH operations. Admission without an execution lease leaves an installed active member quarantined; trusted host task/mission binding and later activation reuse the valid generation without rebinding. Binding readiness is installation state, distinct from exact current execution authority; final request/mailbox/effect guards require both.

Active attached recovery uses persisted records and child evidence, creates a fresh generation scope and calls each binder recover once without YAML reread or duplicate initial persistence. Provisioning-only attached records never become active from legacy child inference: close/tombstone/drain and preserve the original records in a safe failed transition when durable evidence permits it, otherwise remain unavailable. Mailbox queue/control may identify attached members while quarantined; delivery and readiness-dependent execution require installed current bindings plus exact current authority. Team withdrawal synchronously closes all binding admission before owned bounded reverse cleanup and child drain. Physical cleanup may outlive its deadline but cannot retain model/tool/prompt authority or prematurely release provider identity.

The Cordis composition compares registered provider identity after unwrapping the framework's public `symbols.original` traceable-service proxy. Repeated scoped lookups may allocate distinct wrappers and must not falsely revoke the same provider. The binder and identity coordinator retain the exact underlying provider; every lookup still checks the currently registered provider, so replacement or withdrawal denies admission.

### Consumed-initial recovery mailbox ordering

For the required-attachment path only, a recovered reserved child with its initial message already consumed has no initial inbox item to keep that generation alive after release. Before activation, TeamService inspects the exact persisted child initial identity and consumed-message history. For this consumed-initial case only, stage pending Team mailbox items to the exact authorized child with persist-only `send(message, next-turn, false)`, then flush and independently verify the durable target message identity before publishing its delivery receipt and releasing the same reserved handle. This staging requires installed current bindings and exact current host-selected mission/task authority at each asynchronous boundary; it never grants authority or wakes a quarantined generation. A failed or false target flush denies release and leaves the message retryable without a new delivered receipt. Retain target-local serialization and stable message identity deduplication across retries. For an unconsumed initial message, retain initial-first activation and the subsequent mailbox sweep, never stage peer input ahead of that initial message. Apply this ordering to explicit attached recovery and same-generation attached host activation; retain the already qualified empty-attachment mailbox path and its existing ordering. Ordinary model mailbox input cannot activate or recover a member.

### DD-09 / DD-16 — real member contribution scope

A host-owned MemberCapabilityScope closes over the exact live Agent, Team/member/generation, canonical workspace and owner lifetime. isCurrent checks identity/admission independently of execution leases so quarantined bind setup can install its first contribution. authorize(read/effect/request) checks current canonical mission/task authority and exact generation immediately around asynchronous operations. Public Team execution assertions additionally require installed required bindings; internal activation authority validates the private lease without a circular readiness requirement.

Each contribution installs one owner-scoped system-prompt section and actual executable ToolDefinitions. Add optional read/effect classification to contribution tool metadata; unspecified tools remain effectful. The WK adapter explicitly classifies its selective read and candidate effect, and registry capture preserves immutable nested capability enforcement; no tool-name inference grants exemptions. beforeRequest registers an awaited agent/prepare-prompt listener for this exact Agent. replacePrompt replaces the existing section. Each disposer removes only its own listeners, prompt section and tools synchronously; retained handlers reject after cutoff and late provider bodies are withheld. Required refresh failure prevents rendering/provider admission.

### DD-15 / DD-17 — explicit WK composition and initializer selection

The adapter exports a Cordis composition entry in addition to its library APIs. It consumes an explicitly registered WK service, configured trusted serviceBindingKey, explicit dedicated-provider and single-host-workspace assertions, canonical host workspace resolution and model-route preflight. Its one initializer loads strict team_members.durable.yaml and supplies the existing bounded v1 payload; missing/malformed input never falls back. Team tools gain an explicit default/external initializer selection whose default retains existing behavior. The opt-in Durable profile selects external initialization and supplies the sole Durable initializer, binder and dedicated provider; neither two simultaneous initializers nor disabled Team tools are acceptable substitutions. Provider/model selections remain explicit in declarations.

The pinned WK provider is packaged under `vendor/gat-durable-provider` using the existing upstream-vendor documentation/source ownership classification, as its own prebuilt external dependency using its lib/src public export layout, without editing provider source or substituting the official DSH Consumer. Include the unchanged source and linked documentation archives from that exact WK revision beside its prebuilt outputs so original source maps resolve; these archived sources remain excluded from aggregate build discovery and are never rewritten by host compilation. Host GAT adapter/profile projects use ordinary host build references. The provider is explicitly excluded from ordinary tsdown source-project scanning and first-party API/configuration catalog discovery; dependency resolution, package manifests, profile Loader and plain-Node exported artifacts must independently prove the exact service/Consumer path. yaml remains pinned at 2.9.1 with generated lock/importer support. Dedicated/single-host assertions describe the supported topology; test evidence establishes that topology in isolated storage, while real deployment requires separate owner authorization and topology evidence.

### DD-10 / DD-11 / DD-17 — changed-host distribution and fixture alignment

Add a separate compatibility artifact for the exact prerequisite host revision and explicit installer compatibility selection. Preserve default installer behavior and the existing dirty SOURCE_SNAPSHOT.json, compatibility/dsh-0.1.5-rc.2/manifest.json and installer/verify.mjs. The selected artifact captures all prerequisite hashes, transactional before/after images for replaced existing files and payloads for additions; drift rejects before mutation. Only newly introduced package roots are eligible for directory cleanup. A separate installation record supports status/idempotence/failure restoration/rollback; rollback restores prerequisite files and never strips v3 attachments or deletes capability/Session data. Verify in fresh disposable targets, never reinstall the old patch over the prerequisite worktree. New package/profile/API fields regenerate their applicable mappings, documentation and safe SDK/Web expectations through owning tooling.

The supplied GAT browser golden has obsolete teammate model labels. Align only its four labels with the existing builtInTeamMembers defaults and preserve all other assertions and the original failure log. This is fixture reconciliation, not a product default change or blanket recording refresh.

### Type-aware lint and acceptance

Resolve applicable source/fixture diagnostics under the normal host type-aware configuration without disabling safety guards or broad lint rules. Prefer explicit unknown boundaries, invocation-safe callbacks, named completion types and clear async/void bodies. Retain independently meaningful malformed-input and revocation assertions; justified local exceptions must name the actual untrusted/protocol boundary. Follow fixes with focused behavior checks and final exact source hashes. The earlier staged lint and 172-diagnostic report remain historical evidence, never a full type-aware PASS.

Qualification executes real provider/storage, registered composition, reserved persistence/admission, exact host control, tool and model dispatch, refresh/restart/cleanup failures, safe views, actual Loader/profile and built imports. Required T01–T23 cases need new or applicable pinned evidence with explicit isolated-only exclusions. Independent review checks freeze consistency, unchanged static policy labels, source/design synchronization and separate turn/result/cleanup/task/acceptance facts. Runtime output metadata and captures are updated per step; macro controls remain stable unless an explicit re-plan is required. Deployment, merge, publication and canonical promotion remain separately governed.

Selected-artifact installation validation compares the current manifest payload checksum and exact payload row hashes with its schema-v2 receipt, in addition to mapping and host patch checksums. An older receipt for different payload bytes cannot count as already installed merely because destination paths and host patches stayed the same. Preserve legacy default receipt semantics separately.

Binding or recovery acquisition failures report synchronous contribution-removal and physical provider-release failures alongside the original error through an aggregate host failure. Recovery has no caller-owned prepared lease, so it must not suppress release rejection while retaining its quarantined identity. Cleanup remains memoized; persistent data survives, and failed release never frees ownership. Model-facing paths retain generic redaction.

Late binding resources acquired after cancellation retain a host-owned settlement observer. If late disposal, binder abort or provider release rejects, record that cleanup failure through the owning Team diagnostic sink; never discard it in a terminal promise catch. This observer does not delay the cancelled request or reopen admission, and remains owned while physical settlement is pending.

A successful prepare result remains raw-resource owned through lease construction, including reads of its opaque value and abort handler. A throwing or malformed participant accessor cannot fall between validation and tracked ownership: invoke the safely captured abort exactly once, observe physical settlement, and retain the registration pin until cleanup settles. Include malformed participant-output coverage rather than assuming static protocol types eliminate that boundary.

Withdrawal of any required member contribution invalidates the exact host capability scope synchronously, including its remaining prompt/tool/refresh contributions. Core readiness must become unavailable when a binder removes its owner section after failed asynchronous authority revalidation; a still-live Agent or later mission reauthorization cannot revive that withdrawn binding generation. Explicit reconstruction establishes a fresh scope. This uses the existing scope-current contract without revising frozen binder signatures. Regression covers revocation during a blocked read, withdrawal, later same-Agent reauthorization and denied model admission without refreshed required material.

### Staged acknowledgement transaction authorization

AIP-EXEC-022 independent review refinement: after persisted staging is independently verified, the exact target generation, current mission/task authority and cancellation signal must be checked inside the Lead journal transaction immediately before appending its delivered receipt. A pre-queue check and a post-await check cannot substitute for this commit-boundary check: a serialized mission revocation or task edit may commit while acknowledgement is waiting. Denial leaves the input staged and the Lead message queued; no acknowledgement or model release is admitted. This refinement applies to the required-attachment recovery path and preserves the existing empty-attachment delivery path.

### Installed documentation layout ownership

The GAT repository uses unprefixed sibling package paths; the installed DSH composition uses `packages/experimental/gat-*`. The fifteen tracked host documents `{gat-core,gat-tools,gat-web,gat-profile,gat-web-profile}/{README.md,README.zh.md,README.i18n.yaml}` therefore remain explicit installed-layout overrides in the selected compatibility generator. Capture their reviewed host bytes after package source planning, including relative package links, current generated catalog anchors and bilingual hash sidecars. Other root package source payloads retain their existing precedence. Root documentation keeps its valid sibling package links; this documentation override grants no source, package or runtime authority.

AIP-EXEC-022 commit preflight identified that the three previously omitted package pairs had been copied from valid root documentation into an incompatible installed layout. Preserve the sealed artifact and its successful runtime evidence, record this documentation qualification gap, and capture a fresh documentation-only artifact using the host's existing qualified installed-layout bytes. Preserve the vendor ownership README's administrative upstream pin entry as a separate documentation delta, without changing the pinned provider archive. Validate links and bilingual pairing on the actual installed target's worktree bytes, and run the owning documentation aggregate there; a source-host documentation pass does not qualify different installer after-images. Retain exact executable, package metadata, provider and native hashes, and reuse prior completed builds only with an explicit byte-equality proof.

Commit staging does not change payload ownership: the pinned provider planner exclusively owns `vendor/gat-durable-provider/`. If those archive files appear among staged host deltas, verify their bytes against the pinned upstream package and omit the duplicate host capture. Reject mismatched archive bytes. Each installed destination has one payload row; the administrative `vendor/README.md` remains a separate host-owned document.

### Pinned private-provider notices attribution

The owning third-party-notices generator must account for every vendor directory while retaining the existing MIT license checks for the Cordis foundation. The exact `vendor/gat-durable-provider` package is a private upstream dependency whose original metadata declares `private: true`, name `@deepseek-ai/dsh-durable-agent`, version `0.1.0`, and no license field. Admit only that path and identity with the exact upstream URL and revision `a8e215433ae050e36e0ba27205701be1a5f114a1` recorded in the vendor table. Reject unexpected path, identity, privacy, version, upstream, revision or license metadata; ordinary unlicensed vendor packages remain rejected. Generate a separate private-provider provenance section that states the missing license declaration without assigning MIT or claiming permission to redistribute. Preserve the provider package and archive bytes. Add focused positive and negative attribution tests, regenerate notices using the owning generator, verify freshness, and recapture the selected artifact with the generator/test/notice tooling delta. This does not alter product runtime or grant deployment or publication approval.

### Browser replay reflects quarantined default Enable

The supported default-profile browser fixture manually finishes the Lead turn, then enables four members without selecting an authenticated mission/task execution lease. Its Lead and the reserved, initial-persisted members must therefore remain live Idle, with no model admission from Enable. Retain existing model defaults and task-control absence. Update only the stale Running/Inactive expected status labels to Idle, and add an independent exact live status assertion before comparing the panel golden. This is expected fixture alignment with qualified authority gating, without changing runtime behavior or using record-mode refresh. Preserve the original mismatch logs and recapture the selected artifact after the fixture change.

### Built Remote descriptor fixture alignment

The plain-Node built GAT service smoke must assert the complete generated public Remote contribution, including the prerequisite host-control methods `approveMemberAdd`, `closeMission` and `revokeMission` alongside existing methods. Their source contracts were approved and implemented in §7. Add only these three exact sorted descriptor IDs to the stale expected API list, retain the exported Host class and generated contribution probe, and requalify selected distribution bytes. This updates verification expectations; it does not alter or weaken public authorization, generate a new endpoint or change product code.

### Shared authenticated control context in built gateway

The gateway's runtime import of `withControlInvocation` and the Team's import of `consumeHumanControl` must resolve the same public client-connection module instance. Its AsyncLocalStorage owns exact authenticated action/session/revision receipts. The host build must externalize this runtime peer through the ordinary package dependency contract; a dev-only declaration must not allow the gateway bundle to inline a second admission store. Declare client-connection as an explicit gateway runtime peer, retain its development dependency for compilation, and regenerate the lock with owning tooling. Do not replace context validation with global state or grant receipt-free admission. Add a built-artifact guard that verifies external public module resolution and run the actual browser WebSocket Enable path, alongside existing signed HTTP and forged/stale control negatives. Recapture and seal the selected artifact after this metadata change, preserving earlier browser failures as evidence.

### Final package documentation status

Package development notes refer to qualification evidence recorded under AIP-EXEC-022 and separate deployment approval, without a mutable “qualification is running” status that becomes stale at closure. Update only that sentence in matched English/Chinese adapter and Durable profile READMEs and regenerate their translation sidecars. Capture the documentation-only source delta separately from the preceding sealed qualification. Preserve executable, manifest API and native build identity, explicitly compare reused built artifacts, and replay final installed public/runtime/browser/SDK checks on the resulting exact artifact. No functionality, expected result, authentication or deployment permission changes.
