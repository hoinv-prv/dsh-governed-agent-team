# Autonomous Durable Mission Agent MVP — G0 design baseline v3

**Status:** candidate for independent review and explicit HUMAN product-architecture/security acceptance. This document does not self-accept or authorize product implementation.  
**Mission:** `durable-agent-plugin-mvp`  
**Approved planning basis:** WBS revision 8, SHA-256 `d76174a864b6f3c0c5004a78a3c37499eda84780ac302bf50cb67925870219e0`  
**Attempt:** existing charged attempt `t01-a02-r8`  
**Normative design:** `AI_Teammate_Durable_Agent_Architecture.md` v0.3, SHA-256 `5b5cf034dba47f365aa06efb1284d5fc99a86d8fa059b7ff8ab9ae3660394c5b`  
**Context policy:** `context-delegation.SKILL.md`, SHA-256 `d19885139f8bbee3e9dcc792e903bde672cc575b6066db957214cbb2d40b541b`

## 1. Decision and compatibility boundary

G0 selects a **single-node, single-writer SQLite/WAL control plane implemented as an opt-in Cordis plugin family**. DSH remains the execution runtime; the Mission store remains the business source of truth. DSH Session JSONL remains the source of truth for model-visible execution history. Cross-store references are immutable IDs plus hashes and are never inferred from process memory.

The implementation target is exactly:

| Item | Pinned identity |
|---|---|
| DSH checkout | commit `aeedf19995babaa28e35ca84624baff18a77a7d8`, root `@deepseek-ai/dsh-root@0.1.5-rc.2` |
| Package manager / Node | `pnpm@11.7.0`; Node `^22.19.0 || >=24.0.0` |
| DSH compatibility input | SHA-256 `bdb54b8a60cdd947914c62d95fe87eeb8e0cf312b3743bdcac69c83816f312ed` |
| Spike package | private `@dsh-spike/durable-agent-g0-compatibility@0.0.0-t00-a06-r8`, post-Web manifest bound to WBS r8 |
| Product package family | private MVP workspace package `@deepseek-ai/dsh-durable-agent@0.1.0` with Host entry, `/client` entry and generated Typert declaration; publication is forbidden at MVP G0 |
| Product artifact identity | SHA-256 of packed `.tgz` plus `sha512` integrity from `pnpm pack`; clean-profile tests and release report must name both |

Any different DSH commit/version, pinned API byte, context skill hash, package name/version, public-hook behavior, profile format, generated descriptor, or tarball is **not this baseline** and requires a reviewed WBS revision. No DSH core patch or private import is allowed.

Accepted compatibility evidence is `t00-a06-r8`: real SQLite recovery/fencing; real checkpoint and `exec.callId` Mission-ledger binding; real generated Gateway→Client Remote→published SlotCore Chromium path; real PINNED_ONLY/DIRECT/FRESH_SCOUT/FULL_FORK route matrix, package-enforced scout, rejected fork, runtime prefix/model/window evidence, rules-before-wiki, atomic admissions, replay/TOCTOU checks and persisted Session/request raw-exclusion inspection. Independent verdict: `meets_criteria` in `evidence/t00_g0_compatibility_spikes/t00-a06-r8/final-review.md`.

## 2. Exact public DSH seams

Only these public surfaces may be used:

| Concern | Public seam and mandatory use |
|---|---|
| Cordis lifecycle | named `apply(ctx)`/named exports; `ctx.plugin(...)`; effect-scoped registration and returned disposers; no default function-plugin export |
| Agent creation/resume | `ctx.agents.create({sessionId, agentOptions, setup})`, `ctx.agents.resume({resumeSessionId,...})`; retain and await `AgentHandle.dispose()` |
| Agent execution | standard `@deepseek-ai/dsh-agent-loop`; `Agent.followup`/inbox, `whenIdle`, `cancel`; `agent/request`, `agent/pre-step`, `agent/turn-stopping` policy points |
| Session truth | public append-only `SessionEvent`; `Session.append`; `session.surface.nodes`/`eventAt`; `snapshotEvents`; `request/header` and `request/context`; never synthesize private events |
| Session durability | `ctx.sessionPersistence.create/open`; `ctx.sessions.flush(session)`; JSONL backend; `@deepseek-ai/dsh-session-checkpoint-policy` before model requests/top-level tool bodies/next step |
| Tool effects | public `ToolDefinition`; `ctx.tools.register`; `ctx.tools.execute`; monotonic guard plus `tools/pre-execute`, `tools/execute`, `tools/post-execute`, `tools/result`; actual `ToolRunContext.callId` |
| Context injection | scoped `agentCtx.systemPrompt.context(...)` and `agent/request` admission gate; admitted semantic object/hash must be in the actual captured request |
| Fresh scout | `ctx.subagents.start('spawn', SubagentStartRequest)` using in-process spawn provider, `toolFilter.allow`, `maxDepth: 1`, parent Agent and cancellation signal |
| Full fork | `ctx.subagents.start('fork', ...)` using in-process fork provider only after six predicates; seed is completed-turn prefix only |
| Session discovery | `ctx.sessionQuery.searchSessions/searchEvents/readEvent/readSurface/readSession` and SQLite provider; same-workspace authority checked before every exact read |
| Child refs/lifecycle | returned child id/result plus durable `subagent/descriptor`; dispose returned run/handle; continuation APIs only for specialist grants, not scouts |
| Host API | generated Typert descriptors; `TypertRemoteService`/`@Remote`; strict `ctx.typertGateway`; business authorization reread inside each method |
| Client API | generated contribution mounted through `ctx.remote.$mount`; `RemoteResult`; Connection generation/reconnect; retained call fails after withdrawal |
| Dashboard UI | `ctx.slots.inject` + `ctx.slots.register`; published `SlotCore`/renderer; Cordis effect disposal recursively withdraws contributions |
| Profile/package | real Loader/profile, clean isolated HOME/profile, packed tarball resolution, generated catalogs/descriptors and real Chromium configuration |

Pinned API hashes are the WBS r8 source set, including `agent-loop.md` `1e48…9787`, `session.md` `dfab…665f`, `tools.md` `87c1…866`, `session-checkpoint-policy.md` `c3fb…0e5a`, `subagent.md` `91b8…fa86`, `session-query.md` `8381…3819`, `api-gateway.md` `cc0c…dcc9`, `api-remotes.md` `dbb3…826`, `slots.md` `e254…448e`, `client-ui-slots.md` `f861…d7a8`, and `profile-plugin-reference.md` `1401…443b`. The release manifest must carry the full unshortened WBS source hashes; abbreviations here are descriptive only.

## 3. Source-of-truth and storage decision

### 3.1 Store, isolation and ownership

- SQLite 3 through Node `node:sqlite`, WAL mode, `foreign_keys=ON`, `synchronous=FULL`, `busy_timeout=5000`.
- Exactly one process is the Mission-store writer. A filesystem lock plus database `writer_epoch` lease fences stale processes. No network filesystem support in MVP.
- Every command opens `BEGIN IMMEDIATE`, checks aggregate `revision`, writer epoch, grant/budget/control revisions and source CAS predicates, appends domain events, updates projections, and inserts outbox rows in one transaction.
- Reads use SQLite snapshot isolation. Long reads must finish within 2 s and retry from a new snapshot at most twice.
- IDs are UUIDv7 except stable `AgentId` and deterministic operation/admission/idempotency keys. Timestamps are UTC epoch milliseconds. JSON is canonical UTF-8 with sorted keys for hashing.
- Database backup uses SQLite online backup after WAL checkpoint. Schema migrations are monotonic, transactional and retain the previous database until post-migration verification.

### 3.2 Normative tables/schemas

Every row has `created_at`, `updated_at` where applicable and a schema version.

```text
agent(agent_id PK, display_name, status, capability_profile_ref, revision)
mission(mission_id PK, agent_id FK, contract_revision, state, revision,
        planning_mode, active_plan_ref?, pause_revision, cancel_revision,
        budget_policy_ref, next_action, completion_revision?)
mission_contract(mission_id, revision, objective, scope_json, acceptance_json,
                 authority_json, budget_json, hashes_json, accepted_by, accepted_at,
                 PRIMARY KEY(mission_id,revision))
mission_event(mission_id, seq, event_id UNIQUE, type, payload_json, actor,
              occurred_at, causation_id, correlation_id, PRIMARY KEY(mission_id,seq))
outbox(outbox_id PK, mission_id, mission_seq, topic, payload_json, dedupe_key UNIQUE,
       state, attempts, next_attempt_at, lease_epoch, last_error?)
inbox(inbox_id PK, mission_id, source, source_event_id, generation,
      payload_hash, state, UNIQUE(source,source_event_id))
wake_intent(wake_id PK, mission_id, trigger_kind, trigger_key, generation,
            not_before, deadline?, state, lease_owner?, lease_epoch,
            lease_until?, attempts, UNIQUE(mission_id,trigger_key,generation))
agent_run(run_id PK, mission_id, purpose, wake_id?, wake_generation,
          state, lease_epoch, started_at, deadline, ended_at?, stop_reason?)
run_session(run_id, session_id, ordinal, provider, model, context_window?,
            opened_at, closed_at?, replacement_of?, PRIMARY KEY(run_id,session_id))
operation(operation_id PK, mission_id, run_id, wake_generation, ordinal,
          effect_kind, dsh_call_id UNIQUE, idempotency_key, idempotent,
          state, intent_hash, result_hash?, external_ref?, revision)
delegation_grant(grant_id PK, mission_id, revision, specialist_role,
                 capability_level, scope_json, tool_allowlist_json, budget_json,
                 expires_at, revoked_at?, contributor_set_hash)
budget_ledger(entry_id PK, mission_id, run_id?, category, reserved, consumed,
              unit, operation_id?, context_generation?, UNIQUE(operation_id,category))
context_decision(run_id, generation, purpose, route, policy_hash, skill_hash,
                 allowed_sources_json, excluded_sources_json, allowed_tools_json,
                 budgets_json, aiws_json, decision_hash,
                 PRIMARY KEY(run_id,generation))
search_package(package_hash PK, decision_hash, canonical_json, immutable=1)
direct_manifest(manifest_hash PK, decision_hash, canonical_json, immutable=1)
context_capsule(capsule_hash PK, package_hash, version, canonical_json,
                expires_at, redaction_profile, immutable=1)
fork_evidence(decision_hash PK, predicates_json, completed_prefix_hash,
              completed_through_turn, provider, model, context_window,
              input_tokens, reserved_output_tokens, headroom_tokens)
context_admission(admission_id PK, run_id, generation, request_ordinal,
                  decision_hash, evidence_hash, source_set_hash,
                  route_binding_hash?, admitted_semantics_hash,
                  committed_input_hash, state,
                  UNIQUE(run_id,generation,request_ordinal))
artifact(artifact_id PK, mission_id, uri, sha256, media_type, classification)
evidence(evidence_id PK, mission_id, gate_id, artifact_id?, claim, sha256)
gate_result(gate_id, revision, mission_id, reviewer_id, verdict, evidence_set_hash)
handoff(mission_id, completion_revision, artifact_set_hash, gate_set_hash,
        recipient, committed_at, PRIMARY KEY(mission_id,completion_revision))
projection_checkpoint(name PK, last_event_id, last_mission_seq, refreshed_at)
attention_incident(incident_key PK, mission_id, type, severity, first_seen,
                   last_seen, count, state, action, evidence_hash)
learning_proposal(proposal_id PK, agent_id, mission_id, statement, source_hashes,
                  scope, confidence, status, reviewer?)
```

Raw scout transcripts, raw direct excerpts, query pages, rejected candidates, reasoning and unredacted child topology **must not** be copied into business tables. Business records retain canonical package/manifest/capsule/admission data, hashes, accounting and classified references only.

## 4. Mission and effect state machines

### 4.1 Canonical architecture §16A Mission states

Planning mode is an accepted `PlanningDecision` attribute, never a Mission state. The exact business states are:

| State | Meaning | Terminal |
|---|---|---|
| `ASSIGNED` | accepted assignment exists but triage has not begun | no |
| `TRIAGING` | selecting execution mode and next action | no |
| `READY` | exactly one actionable generation/next wake is durably available | no |
| `RUNNING` | one active AgentRun lease exists | no |
| `WAITING_TIMER` | waiting for a specific durable time trigger | no |
| `WAITING_DEPENDENCY` | waiting for a dependency event | no |
| `WAITING_SPECIALIST` | waiting for a durable specialist response | no |
| `WAITING_HUMAN` | waiting for decision, permission or authority | no |
| `RETRY_SCHEDULED` | waiting for bounded retry/backoff | no |
| `VERIFYING` | automated, independent or HUMAN gate is running | no |
| `REWORK` | gate failed and rework budget remains | no |
| `HANDOFF_READY` | gates passed; awaiting atomic completion/handoff commit | no |
| `PAUSED` | admission disabled and wakes disarmed | no |
| `BLOCKED` | authority, budget, policy or resolvable condition is missing | no |
| `COMPLETED` | acceptance and handoff transaction committed | yes |
| `FAILED` | explicit failure policy proves no valid recovery | yes |
| `CANCELLED` | authorized owner cancellation | yes |
| `EXPIRED` | deadline/expiry policy terminal | yes |

`BUDGET_EXHAUSTED` and `AUTHORITY_BLOCKED` are `BLOCKED.reason` values, not terminal states. `READY` satisfies, in the same transaction, exactly one of: (a) a still-valid claimed WakeIntent generation is admitted into one AgentRun; or (b) a Mission event and outbox row create a new WakeIntent generation with dedupe key, `not_before`, next action and expected Mission revision. READY may never be stranded.

| Command/event | From | To | Preconditions and durable effect |
|---|---|---|---|
| `assign` | none | `ASSIGNED` | accept exact MissionContract revision; atomically append assignment event and outbox for a new triage WakeIntent generation/dedupe key |
| `begin_triage` | `ASSIGNED` | `TRIAGING` | triage wake generation is due/claimed and Agent lifecycle is active |
| `start_triage_run` | `TRIAGING` | `RUNNING` | CAS Mission revision; create exactly one restricted `purpose=triage` AgentRun for the claimed generation; never reuse a terminal run |
| `accept_planning_decision` | `RUNNING` | `READY` | active purpose is triage; persist mode/policy/reason; settle triage run/wake and atomically emit a new execution wake generation/dedupe key |
| `start_execution_run` | `READY` | `RUNNING` | CAS revision; claimed generation, contract, controls, grant and budget remain valid; acquire unique run lease |
| `checkpoint_wait` | `RUNNING` | `WAITING_TIMER` / `WAITING_DEPENDENCY` / `WAITING_SPECIALIST` / `WAITING_HUMAN` / `RETRY_SCHEDULED` | checkpoint current run; atomically persist exact trigger, new future WakeIntent/outbox and next action |
| `trigger_satisfied` | any `WAITING_*` or `RETRY_SCHEDULED` | `READY` | matching event/time/response/retry generation settles once; recheck pause/cancel/grant/budget and atomically provide actionable generation |
| `submit_for_verification` | `RUNNING` | `VERIFYING` | artifacts/evidence manifest durable; run checkpointed and settled; no unresolved effect |
| `gate_failed` | `VERIFYING` | `REWORK` / `BLOCKED` | durable findings; enter REWORK only with remaining rework budget, otherwise BLOCKED |
| `rework_ready` | `REWORK` | `READY` | corrective action accepted; atomically emit a new rework wake generation/dedupe key |
| `gate_passed` | `VERIFYING` | `HANDOFF_READY` | all automated, contribution-independent and HUMAN requirements satisfied |
| `complete` | `HANDOFF_READY` | `COMPLETED` | artifact, evidence, gate and recipient refs verified and committed with handoff/event/outbox atomically |
| `pause` | any nonterminal | `PAUSED` | increment control revision; checkpoint/interrupt active run; disarm wakes and retain prior state |
| `resume` | `PAUSED` | `READY` or retained `WAITING_*` | explicit authorized decision; re-evaluate contract/grant/budget; READY gets a new wake generation, waiting re-arms its prior trigger as a new generation; never blindly resume a Session |
| `block` | any nonterminal | `BLOCKED` | persist reason, evidence and required HUMAN action |
| `unblock` | `BLOCKED` | `TRIAGING` / `READY` | explicit HUMAN decision with expected revision; TRIAGING emits new triage wake, READY emits new execution wake |
| `fail` | any nonterminal | `FAILED` | explicit failure policy and evidence |
| `cancel` | any nonterminal | `CANCELLED` | authorized owner decision; reconcile dispatched effects |
| `expire` | any nonterminal | `EXPIRED` | accepted deadline/expiry policy and evidence |
| `reopen` | `FAILED` / `CANCELLED` / `EXPIRED` | `TRIAGING` | explicit HUMAN decision creates a new Mission revision, preserves immutable terminal history, and atomically emits a **new** triage WakeIntent generation with a **new** dedupe key; terminal AgentRun/Wake/Session identities are never reused |

Every transition records actor, reason, source event, expected aggregate revision, correlation/dedupe key, run/Session reference and evidence. The Agent retains responsibility in waiting, paused and blocked states; Session death never implies completion or unassignment.

### 4.2 Run, wake and effect states

- Run: `ALLOCATED → RUNNING → {WAITING,VERIFYING,SUCCEEDED,FAILED,CANCELLED}`; one active run lease per Mission.
- Wake: `ARMED → CLAIMED → SETTLED`; failures use `RETRY_WAIT`; exhausted attempts use `DEAD_LETTER`. Unique `(mission,trigger,generation)` prevents duplicate accepted runs.
- Operation: `PREPARED → DISPATCHED → ACCEPTED|REJECTED|OUTCOME_UNKNOWN`. `PREPARED` plus Mission intent and actual DSH `exec.callId` is durable before body. `DISPATCHED` non-idempotent operations never auto-retry. `OUTCOME_UNKNOWN` requires reconciliation or HUMAN decision. Provider-supported idempotency uses `operation_id`; plugin-owned effects dedupe it transactionally.

`operation_id = sha256(mission_id || run_id || wake_generation || effect_ordinal || effect_kind || canonical_intent_hash)`. A different `dsh_call_id`, intent hash or kind for an existing operation is `EFFECT_IDENTITY_CONFLICT`.

## 5. Planning policy v1

Triage scores five axes 0–2: work items, dependency depth, affected domains, reversibility/risk, and uncertainty. It also records external effects, protected data, required reviews, estimated minutes and expected model calls.

- **NO_PLAN:** score ≤2; one work item; no hard dependency; no external/irreversible effect; no protected data; ≤30 min; ≤2 model requests.
- **CHECKLIST:** score 3–6; ≤8 items; dependency depth ≤1; reversible scoped effects; ≤240 min; ≤12 model requests.
- **WBS:** score ≥7, or any forced trigger: >8 items, dependency depth >1, cross-project/cross-domain change, irreversible/external effect, security/privacy/migration/package release, >240 min, >12 requests, >1 worker, or required independent/HUMAN gate.
- HUMAN review is mandatory before an irreversible/external effect, grant widening, full-prefix fork, raw AIWS access, migration, package release, budget increase >20%, or acceptance change.
- Ambiguous classification chooses the stricter mode. Any mode must persist `planning-policy-v1`, features, score, forced triggers and reason. READY liveness test requires each valid triage fixture to reach READY or a named waiting/blocked state—never remain TRIAGING.

Owner: Mission Controller. Fixtures: minimum 10 per mode plus boundary and forced-trigger cases; false-negative rate for forced WBS is 0.

## 6. Scheduler, wake and recovery policy v1

| Control | MVP value |
|---|---:|
| Execution quantum | 15 min wall clock or 12 model requests or 40 tool calls, whichever first |
| Scheduler scan precision | 5 s; batch 100 wakes |
| Run lease | 120 s; renew every 30 s; reclaim after expiry + 15 s skew allowance |
| Max active runs | 1 per Mission, 2 per Agent, 4 deployment-wide |
| Trigger dedupe | one accepted run per `(wake_id,generation)` |
| Retry attempts | 3 after initial failure |
| Backoff | 5 s, 30 s, 120 s; ±20% deterministic jitter from wake id |
| Dead letter | after fourth total dispatch or deadline; opens severity-2 incident |
| Quiet hours | 22:00–07:00 project timezone for discretionary work; deadlines, recovery, security and HUMAN explicit wakes bypass |
| Waiting recheck | event-driven; safety scan every 60 s, never model-powered busy polling |
| Shutdown | stop admission, checkpoint, drain owned calls ≤30 s, persist wake, release lease |

Crash windows: before claim (safe repeat), after claim/before run (lease reclaim), during model request (request checkpoint then resume), after tool call/before result (`TOOL_OUTCOME_UNKNOWN`), after result/before outbox (same Mission transaction/replay), after completion commit (idempotent handoff/outbox replay).

## 7. Authority, grants and specialist catalog

Autonomy levels: A0 advise only; A1 read/plan; A2 reversible workspace mutation; A3 declared external side effects with pre-approved operation classes; A4 is out of MVP. Child authority is the intersection of Mission contract, current grant, deployment policy, route package and live control revision.

Named specialist grants are exact templates; a Mission may attenuate but never widen them. `session_event_search/read` is permitted only for same-workspace Sessions authorized by the grant. `bash` below means only an exact Mission `allowed_commands` argv/cwd entry, never a shell string or arbitrary interpreter. All roles have `maxDepth=1`, cannot delegate, cannot ask the user, cannot mint/transfer grants, and cannot change objective, acceptance, authority or budget.

| Role/template | Level and purpose | Read/source scope | Write scope | Tool/effect allowlist | Budget ceiling | Provider/model and lifetime | Revocation and fallback |
|---|---|---|---|---|---|---|---|
| `pmo-v1` | A1; decompose, dependency/status/risk analysis | Mission contract, accepted baseline/WBS, task metadata, redacted evidence metadata, same-project Session refs | none; response is returned to parent, which alone may persist a proposal | tools `read,glob,grep,session_event_search,session_event_read`; effects `read` only | input 16k, output 4k tokens; 12 tool calls; 30 min; USD 1.00 | exact parent provider/model inherited, no override; resolved context ≤32k; expiry 30 min | revision/expiry/revoke checked before each request/tool; cooperative cancel; fallback: parent creates its own CHECKLIST/WBS or enters `WAITING_HUMAN` |
| `advisor-v1` | A1; bounded domain advice/options/risk | grant-listed authoritative rules/wiki/project refs and redacted Mission facts; no whole parent prefix by default | none; advisory response only | tools `read,glob,grep,session_event_search,session_event_read`; effects `read` only | input 12k, output 4k; 8 calls; 20 min; USD 0.75 | exact parent provider/model inherited; context ≤24k; expiry 20 min | revoke/cancel as above; fallback: record evidence gap, use supported facts only, or `WAITING_HUMAN` for protected decision |
| `senpai-v1` | A2; coached remediation of one named WorkItem | contract plus exact grant-listed project paths, current diff/artifacts and test evidence | only grant-listed WorkItem paths under Mission write scope; never mission controls, WBS, DSH core, HOME/profile or unrelated files | tools `read,glob,grep,edit,write,bash`; effects `read,write,execute`; no network/external; `bash` exact allowed commands only | input 32k, output 8k; 40 calls; 60 min; USD 3.00 | exact parent provider/model inherited; context ≤48k; expiry 60 min | revoke prevents new mutation/command and aborts cooperatively; dispatched effect reconciled; fallback: parent performs bounded rework or requests HUMAN capability/grant |
| `reviewer-v1` | A1; evidence-bound independent review | exact deliverable, inputs, manifests, tests and evidence named in review brief; redacted same-project Session refs | none; verdict returned to coordinator/parent, not written by reviewer | tools `read,glob,grep,session_event_search,session_event_read`; effects `read` only; no command execution | input 24k, output 6k; 20 calls; 45 min; USD 2.00 | deployment-approved reviewer provider/model fixed in grant; must differ in runtime identity from contributor; context ≤40k; expiry 45 min | stale/revoked or contributor-set match invalidates verdict; fallback: one alternate independent reviewer from approved catalog, else `WAITING_HUMAN`—never self-review |
| `context-scout-v1` | A1 retrieval only; not a specialist/business grant | immutable SearchDelegationPackage sources only | none | exact package allowlist; effects `read` only | §8 per-scout ceiling | parent-approved inherited route; expiry equals package deadline ≤30 min | discard or one same-scout capsule repair; then parent fallback/block |

A concrete `DelegationGrant` pins the selected template/version, Mission/contract/control revisions, purpose, source/write scopes, exact tool/effect and command allowlists, provider/model, input/output/context ceilings, tool/time/cost budgets, expiry, contribution flag and revocation revision. Default expiry is the per-role value above and may never exceed 24 h. Revocation is durable, increments grant/control revision, blocks new model/tool admission immediately and cooperatively cancels active work; already-dispatched external effects enter reconciliation. Expired or failed specialist work never silently switches provider/model, widens paths or receives a fresh budget: only the stated fallback is allowed, and any retry consumes the same Mission/specialist budget.

## 8. Context policy v1

### 8.1 Route selection

Every `triage|execute|verify|recover` run evaluates route before each model request and after an evidence gap.

- **PINNED_ONLY:** all required inputs are already immutable, cited and ≤8,000 admitted tokens; no unresolved freshness/conflict.
- **DIRECT:** 1–3 known exact sources; ≤3 retrieval calls; no exploration; parent can produce a complete manifest.
- **FRESH_SCOUT:** unknown location, >3 candidate sources, conflict/freshness check, or exploration needed; package fits budgets and no whole-prefix need.
- **FULL_FORK:** exceptional; only when all six predicates pass and the completed parent prefix is materially necessary. Otherwise FRESH_SCOUT or BLOCKED.

### 8.2 Numeric context and cumulative Mission budgets

| Budget | Per direct request | Per scout | Per fork | Per run cumulative | Mission cumulative |
|---|---:|---:|---:|---:|---:|
| unique sources considered | 3 | 6 | 8 | 12 | 64 |
| exact sources read | 3 | 4 | 6 | 8 | 40 |
| search rounds | 1 | 2 | 0 | 4 | 16 |
| retrieval/tool calls | 3 | 8 | 4 | 16 | 128 |
| raw bytes processed | 16 KiB | 64 KiB | 128 KiB | 192 KiB | 2 MiB |
| admitted input tokens | 8,000 | 12,000 | completed prefix max 32,000 | 40,000 | 160,000 |
| retrieval+scout output tokens | 0 | 4,000 | 2,000 | 8,000 | 48,000 |
| normalized cost ceiling | USD 0.25 | USD 0.75 | USD 1.50 | USD 3.00 | USD 15.00 |
| wall time | 5 s | 30 s | 15 s | 60 s | 10 min |

Provider billing uses actual metered cost when available; otherwise `normalized_cost = input_tokens×configured_input_rate + output_tokens×configured_output_rate`, with rates pinned in the Mission contract. Missing rates prohibit paid routes. Budget checks reserve before dispatch and settle actual use in `budget_ledger`; unused reservation returns. All routes share the same Mission counters—new Sessions/generations do not reset them. Crossing 80% opens a warning; 100% blocks additional retrieval/model work pending HUMAN budget revision.

Minimum model headroom is `max(2,048 tokens, 25% of contextWindow)` after inherited/admitted input and reserved output. Unknown context window rejects FULL_FORK.

### 8.3 Immutable schemas

**DirectRetrievalManifest v1**

```json
{"kind":"direct","version":1,"decisionHash":"…","status":"complete|partial|no-evidence","calls":[{"tool":"glob|grep|read|session-query","normalizedArgsHash":"…","source":{"ref":"…","revision":"…","hash":"…","authority":1}}],"selectedExactReads":[{"citation":"…","excerptHash":"…","source":"…"}],"conflicts":[],"unresolved":[],"accounting":{"sources":0,"calls":0,"bytes":0,"tokens":0,"costUsd":0},"createdAt":0,"expiresAt":0,"hash":"…"}
```

**SearchDelegationPackage v1**

```json
{"kind":"search-package","version":1,"id":"…","decisionHash":"…","objective":"…","questions":[],"allowedSources":[],"excludedSources":[],"authorityOrder":["rules","wiki","project","memory"],"allowedTools":[],"budgets":{"sources":6,"rounds":2,"toolCalls":8,"bytes":65536,"tokens":4000,"costUsd":0.75,"deadline":0},"restrictions":{"readOnly":true,"noMutation":true,"noUser":true,"noRecursiveDelegation":true,"noScopeExpansion":true},"aiwsProfileRef":"…","hash":"…"}
```

**ContextCapsule v1**

```json
{"kind":"capsule","version":1,"id":"…","packageHash":"…","status":"complete|partial|no-evidence","summary":"…","claims":[{"statement":"…","confidence":"high|medium|low","evidenceRef":"…","authorityVersion":"…"}],"conflicts":[],"unresolved":[],"recommendedExactReads":[],"sourceRevisionSet":[{"ref":"…","revision":"…","hash":"…","authority":1}],"searchAccounting":{"sourcesConsidered":0,"sourcesRead":0,"roundsUsed":0,"toolCalls":0,"bytes":0,"tokens":0,"costUsd":0,"budgetExhausted":false},"createdAt":0,"expiresAt":0,"redactionProfile":"context-v1","hash":"…"}
```

Hash excludes only its own `hash` field. A capsule with an uncited claim, source outside package, expired source, exceeded budget, mutable package, wrong hash or unresolved high-impact conflict is rejected.

### 8.4 AIWS profile, authority order and bounded fallback

The one canonical order everywhere—package, retrieval, conflict resolution, capsule validation and replay—is **`rules → wiki → project → memory`**:

1. exact applicable rules are mandatory and highest authority;
2. the authorized wiki is read second as maintained supplemental interpretation;
3. exact project sources are read third for current project facts and may not override rules;
4. prior memory is last, advisory only, and any action-affecting claim requires corroboration by a current rules/wiki/project source.

System selection is explicit (`systemSelector`) and must match Mission membership. Local/raw source access requires a specific HUMAN authorization ref, source pattern and maximum 60-minute expiry; inherited generic filesystem authority is insufficient. Default `aiws-standard-v1` denies local/raw access and ambiguous system selection.

The retry/fallback contract is concrete and shares the original ContextDecision/Mission budget:

| Attempt | Route | Action | Failure disposition |
|---|---|---|---|
| 1 | `DIRECT` | exact-read rules, then wiki, then project using at most the DIRECT ceiling | transient provider/read failure may retry once after 1 s with identical system/workspace/source set/normalized args; revision drift instead creates a new generation |
| 2 | same `DIRECT` | the single identical retry; no new source or query widening | if mandatory rules still unavailable: `WAITING_HUMAN` or `BLOCKED`; never substitute wiki/project/memory for rules |
| fallback | `FRESH_SCOUT` | permitted only when location/ambiguity, not authority bypass, caused the gap; immutable `aiws-standard-v1` package retains `rules,wiki,project,memory`, exact system and original source ceiling | one capsule validation repair by the same scout; then partial/no-evidence with explicit gap, `WAITING_SPECIALIST`, `WAITING_HUMAN` or `BLOCKED` |
| exceptional | `FULL_FORK` | never an automatic retry; requires all six fresh predicates and exact-prefix authorization | any failed predicate returns to bounded FRESH_SCOUT or blocks before child publication |

No attempt may change provider/model except a new HUMAN-approved decision, switch AIWS system, add local/raw scope, reorder authority, reset counters or treat missing lower-authority evidence as authoritative absence. Owner: project security owner; override owner: HUMAN product/security owner.

### 8.5 FULL_FORK authorization

All six durable predicates must be true:

1. `shortCleanParent`: completed prefix ≤32,000 tokens, balanced turns, no unknown effect/reasoning secret;
2. `mostlyRelevant`: ≥80% of completed surface tokens are relevant to child objective;
3. `wholePrefixAuthorized`: HUMAN or contract explicitly authorizes this exact completed-prefix hash and classifications;
4. `independentReviewNotRequired`: child is not serving as independent reviewer of contributor-owned content;
5. `inheritedRoute`: provider/model are permitted and exactly inherited/resolved;
6. `enoughWindow`: required headroom rule passes.

The prefix ends at the last completed `turn/end`; open/in-flight turn events are excluded. Persist exact prefix hash, through-turn, event count, provider/model, context window, measured input, reserved output and headroom. A failed predicate rejects **before** provider publication and creates no child.

### 8.6 Atomic admission, CAS and replay

- One `ContextDecision` per `(run,generation)` is durable before retrieval.
- Exact reads capture `(ref,revision,hash)`. In the same `BEGIN IMMEDIATE` transaction, admission rereads current source authority and rejects any mismatch (`CONTEXT_SOURCE_CAS_FAILED`).
- One admission per `(run,generation,requestOrdinal)`; duplicates return the same committed record only when every hash matches, otherwise conflict.
- `agent/request` refuses dispatch unless admission is accepted, unexpired and matches purpose, route, skill, policy, package/manifest/capsule, source set, binding and live budgets/control revision.
- The actual request contains route, admitted semantic object or canonical selected semantics, evidence hash, admission hash and citations. Parent and admitted Session surfaces exclude raw child/query/tool envelopes, rejected candidates, retrieval traces and uncited content.
- Replay uses `committed_input_hash` and immutable rows. It never reruns retrieval silently. A replacement Session reconstructs byte-equivalent committed input; source/policy/authority drift invalidates and requires a new generation.

### 8.7 TTL, retention and redaction

- Direct manifest TTL: 15 min or any source revision change.
- Search package TTL: 30 min before start; immutable forever once referenced.
- Capsule TTL: 30 min default, 5 min for local/raw or volatile sources, maximum 24 h for pinned immutable sources.
- Raw scout child Session: encrypted runtime store, 7 days then deletion; security hold maximum 30 days with HUMAN approval.
- Raw direct query/page/excerpt: memory only, deleted at run end; never business-persisted.
- Packages/manifests/capsules/admissions/accounting: Mission lifetime +365 days; hashes/audit skeleton 2 years.
- Model-visible Session retention: project policy, default 30 days after Mission close; legal/security hold overrides are explicit.
- Redaction profile `context-v1`: remove secrets/tokens, personal data not required for objective, absolute HOME paths, raw child IDs from dashboard, and excerpt text after hashing. Redaction itself is versioned and hash-bound.

## 9. Dashboard privacy and controls

Authorization is project membership + role (`viewer`, `operator`, `owner`) checked on every Host request and stream generation. Cross-project access returns indistinguishable not-found. Controls require operator/owner, expected Mission revision, CSRF/trusted Connection and audit reason.

Dashboard may show Agent/Mission IDs, state/revision, responsibility, next action/wake, lease health, blocker category, aggregate budget, gate status, route/status, source counts, conflicts, staleness, redacted child class and evidence hashes. It must not show prompts, raw retrieval, excerpts, capsule claims/content, scout transcript, reasoning, secrets, absolute paths, unredacted child topology or rejected candidates.

Projection freshness: target ≤2 s, warning >5 s, stale badge and disabled mutation >15 s. Client reconnect obtains a fresh baseline before deltas. UI cache clears on logout/disposal and is capped at 24 h. Access audit is retained 365 days; security incident access is 2 years. Browser tests cover unauthorized/cross-project access, stale revision, redaction, reconnect, contribution withdrawal, retained-call failure and duplicate-free remount.

## 10. Watchdog policy v1

Deterministic scans every 30 s:

| Condition | Threshold | Action |
|---|---:|---|
| expired active lease | lease expiry +15 s | fence owner, re-arm same wake generation, severity 2 |
| missed due wake | 30 s | enqueue idempotent scheduler nudge; 2 min severity 2 |
| RUNNING no durable event | 5 min | request checkpoint/cancel; 10 min severity 2 |
| WAITING without trigger/next action | immediate | severity 1, block Mission |
| retry/dead-letter | retry 4 total attempts | severity 2, block |
| rework exhaustion | zero remaining | severity 2, block/HUMAN |
| budget pressure | 80% warning / 100% block | notify / deny new work |
| stale projection | 5 s warn / 15 s disable controls | rebuild projection; severity 2 at 60 s |
| unknown external outcome | immediate | severity 1; no retry |

Incident key `(mission,type,trigger-generation)` makes actions idempotent. Watchdog cannot change objective, acceptance, authority or budget. HUMAN page SLO: severity 1 ≤1 min, severity 2 ≤5 min. Fixture false-positive budget is <1% across 1,000 healthy deterministic cases and zero authority-widening actions.

## 11. MVP SLOs and release thresholds

Single-node reference environment, measured over ≥100 deterministic operations plus fault fixtures:

| SLO | Gate |
|---|---|
| due wake dispatch | p95 ≤5 s, p99 ≤15 s |
| crash detection/lease reclaim | p95 ≤150 s |
| recovery to safe state | p95 ≤180 s; unknown effects never replayed |
| state/outbox atomicity | 100% across all injected crash points |
| duplicate accepted effects/admissions/wakes | 0 |
| context PINNED_ONLY admission | p95 ≤100 ms |
| DIRECT route | p95 ≤2 s and ≤3 calls |
| FRESH_SCOUT | p95 ≤30 s and declared budget |
| FULL_FORK authorization/start | p95 ≤15 s; 100% incomplete predicates rejected pre-provider |
| context replay | 100% byte-equivalent or fail closed |
| raw/cross-project leakage | 0 across negative suite |
| dashboard projection | p95 ≤2 s; controls disabled >15 s stale |
| pause/revoke enforcement | deny new run/scout/effect p95 ≤1 s after durable commit |
| intervention rate | ≤10% ordinary reference Missions; 100% protected decisions escalated |
| Mission cost | 100% within contract; default context ceiling USD 15 |
| package lifecycle | 100% clean install/boot/dispose; no residual credential/runtime files |

An unmet SLO is HOLD, not a reason to relax tests. Production/24×7 SLA and multi-node HA are explicitly out of scope.

## 12. Quality, handoff, learning and metrics

A worker or specialist can produce evidence but cannot accept its own output. Required gate owner is independent or HUMAN as declared. Completion atomically binds artifact hashes, evidence claims, gate verdicts and recipient handoff.

Only accepted terminal outcomes or HUMAN-approved major checkpoints may create a `learning_proposal`. Proposals retain statement, source hashes, scope, confidence and reviewer status—never raw transcript/retrieval. Capsules never auto-promote to memory or skills.

Metrics are derived reproducibly from durable events: completion/gate/rework rate, autonomy/intervention, planning mode and override, wake latency/recovery, duplicate suppression, context route/latency/budget/capsule validity/staleness/replay drift/leak denial, delegation outcomes/independence, projection freshness and normalized cost. Metrics retain 13 months aggregated; per-Mission links follow Mission +365-day policy.

## 13. Security, threat ownership and rollback

| Threat | Preventive control | Owner |
|---|---|---|
| prompt injection/retrieved instruction | treat retrieval as data; authority order; cited capsule validation | context-policy owner |
| source TOCTOU/stale replay | transaction source CAS; committed-input replay | persistence owner |
| scope laundering/child escalation | immutable package/grant intersection, allowlist, depth 1 | security owner |
| prefix overexposure | six predicates + exact hash + in-flight exclusion | Mission Controller/HUMAN |
| duplicate/unknown effect | operation ledger, actual callId, checkpoint, no blind retry | effect/tool owner |
| cross-project/dashboard leak | membership per call, redaction, negative browser tests | API/UI security owner |
| stale control/grant/budget | revision CAS before run/scout/effect | Mission Controller |
| package/supply-chain drift | lock/tarball/generated descriptor hashes, clean profile | release owner |

Rollback triggers: any raw/cross-project leak, duplicate accepted external effect, lost Mission responsibility, corrupted migration, unsupported DSH seam, package hash drift, SLO gate failure, or severity-1 unresolved finding.

Rollback procedure: stop new admission; durably pause affected Missions; revoke grants; cancel cooperative runs; reconcile dispatched effects; drain/dispose Cordis fibers; restore previous package/profile and pre-migration database; replay and validate event/projection hashes; resume only after HUMAN incident decision. Never delete Session logs, attempt history or unknown-effect evidence. Schema downgrade is forbidden unless an explicit reverse migration was previously tested; otherwise restore backup read-only and forward-fix under a revised plan.

## 14. Requirement-to-design/test/owner matrix

| Req | Concrete decision | Required verification | Accountable owner |
|---|---|---|---|
| r1 | stable AgentId; separate Mission/Run/Session/Workspace/model identities | identity survives Session/model/workspace changes | domain owner |
| r2 | immutable contracts, CAS Mission revision, event/outbox/completion transaction | transition/model property tests; crash replay | Mission Controller + persistence owner |
| r3 | planning-policy-v1 thresholds and forced WBS | NO_PLAN/CHECKLIST/WBS boundary fixtures; READY liveness | planning-policy owner |
| r4 | SQLite/WAL single writer, Session JSONL boundary, atomic outbox | process-kill atomicity, migration and projection replay | persistence owner |
| r5 | wake-policy-v1, leases, generations, checkpoint and dead letter | fake clock/load plus real crash/unknown recovery | scheduler owner |
| r6 | live revision/grant/budget checks; cumulative ledgers | pause/revoke/budget TOCTOU and child attenuation tests | authority owner |
| r7 | named catalog and versioned grants, reviewer independence | grant expiry/revoke/scope/recursive/independence negatives | delegation owner + HUMAN |
| r8 | context-policy-v1 routes, schemas, admission, CAS and replay | all four real routes, AIWS, raw exclusion, drift/replacement | context owner |
| r9 | evidence/gates/handoff atomic completion; no self-accept | concurrent completion and missing-gate negatives | quality owner |
| r10 | strict generated Remote + privacy projection + Slot UI | real Chromium auth/redaction/stale/reconnect/unmount | API/UI owner |
| r11 | watchdog-policy-v1 | deterministic incident/idempotency/false-positive suite | reliability owner |
| r12 | proposals only; reproducible event metrics | terminal/checkpoint eligibility and no-raw tests | learning/telemetry owner |
| r13 | deny-first security and fault matrix | malicious retrieval, fork, CAS, race, crash, privacy tests | security/reliability owner |
| r14 | exact private package/tarball, clean profile real paths | pack/install/Loader/recorded Session/Chromium scenarios | release owner |

## 15. Resolution of every architecture §33A OPEN row

| OPEN row | G0 resolution | Release evidence / HOLD |
|---|---|---|
| store/isolation/lease | §3 SQLite/WAL single writer, immediate transactions, epoch fence | atomicity/process-kill/migration tests; HOLD on multiwriter ambiguity |
| effect operation ID/dedupe | §4 actual DSH callId + deterministic Mission operation ledger | crash/identity-conflict/unknown tests; no exactly-once claim |
| planning thresholds | §5 planning-policy-v1 | three-mode fixtures, zero missed forced WBS |
| wake/scheduler values | §6 numeric quantum/precision/lease/retry/dead-letter/quiet hours/concurrency | fake-clock, load, crash and liveness suite |
| specialists/grants | §7 catalog and grant template | HUMAN least-privilege approval and negative tests |
| dashboard privacy | §9 role/membership/redaction/retention/freshness | cross-project/redaction/stale real Chromium tests |
| watchdog | §10 thresholds/actions/SLO/false-positive budget | deterministic 1,000-case evaluation |
| quantified SLOs | §11 numeric gates | integration measurements; any miss is HOLD |
| DSH version/public seams | §§1–2 exact 0.1.5-rc.2 public map | accepted t00 plus clean packed-profile qualification |
| context decisions | §8 routes/budgets/schemas/TTL/redaction/fork/AIWS/admission/replay/SLO | accepted t00 plus product route/security/replay suite |
| subagent/fork/query seams | §2 and §8 public `ctx.subagents`/providers/`ctx.sessionQuery` | real spawn/fork/query child refs and lifecycle tests |

No OPEN G0 decision remains implicit.

## 16. Effort and scope adequacy

WBS r8 local ceiling is **54 attempts / 34,380 attempt-minutes**; six preserved charges / 5,580 minutes yield the conservative cumulative ceiling **60 / 39,960**. This t01 attempt remains within its already charged 600-minute allocation. No additional attempt is allocated by this document.

The remaining tasks t02–t19 are re-estimated against the decisions in this baseline as follows. “Need” includes focused implementation, fixtures, evidence packaging and review response; it excludes a new technology discovery. The reviewed WBS allocation is sufficient in every row, and its additional attempts are contingency rather than permission to repeat an unchanged hypothesis.

| Task | Re-estimated need (min) | WBS minutes/attempt × max attempts | Adequacy condition |
|---|---:|---:|---|
| t02 scaffold/package | 300 | 360 × 2 | exact private package and existing pnpm/Loader pattern |
| t03 domain/codecs | 420 | 480 × 2 | schemas in §§3, 7, 8 are final |
| t04 persistence | 1,400 | 660 × 3 | SQLite single writer; no HA/database substitution |
| t05 Mission/planning | 1,150 | 600 × 3 | state machine and planning-v1 unchanged |
| t06 authority/budget | 850 | 540 × 2 | A0–A3, grant and numeric budget policy unchanged |
| t07 runtime adapter | 1,300 | 660 × 3 | only accepted public DSH seams |
| t08 scheduler/recovery | 1,550 | 720 × 3 | single-node scheduler and stated crash windows |
| t09 delegation | 1,150 | 540 × 3 | four specialist roles; depth one |
| t10 context authority | 1,650 | 720 × 3 | four routes and policy-v1; no new retrieval backend |
| t11 quality/handoff | 1,050 | 480 × 3 | declared gates and atomic completion only |
| t12 watchdog | 700 | 420 × 2 | deterministic rules; no ML anomaly detector |
| t13 projections/API | 1,200 | 540 × 3 | redacted operational projection, not raw explorer |
| t14 dashboard | 1,500 | 660 × 3 | minimal fleet/detail/attention/control views |
| t15 learning/metrics | 700 | 420 × 2 | proposals/derived metrics; no training pipeline |
| t16 security/chaos | 1,650 | 720 × 3 | declared threat/crash matrix |
| t17 reference scenarios | 1,950 | 840 × 3 | exact finite scenario set in WBS |
| t18 integration/package | 850 | 480 × 2 | existing commands and one private tarball candidate |
| t19 final report | 200 | 240 × 1 | evidence assembly only; no remediation hidden here |

These estimates total 19,570 implementation minutes versus 27,060 available task-attempt minutes for t02–t19; the 7,490-minute difference is bounded retry/review contingency, not planned work. Together with t00/t01, the WBS local ceiling remains 34,380 attempt-minutes. They are adequate **only** for this selected single-node SQLite, public DSH seams, private package, four context routes and real Host/Client profile; no task must invent a storage engine, IAM platform, billing system, multi-node scheduler, workflow designer or DSH patch. Implementation must stop and request WBS revision if:

- any exact public seam or pinned byte differs;
- package qualification needs a new command/effect/write path;
- a task exceeds 80% of its per-attempt minutes with an acceptance-critical unknown;
- migration, security, Web integration or context SLO needs more than its declared attempts;
- HUMAN changes any numeric threshold, authority, privacy, acceptance or package identity.

The coordinator must preserve cumulative charges; a new worker/session/revision never resets them.

## 17. HUMAN acceptance checklist

The HUMAN product architecture and security owner must explicitly accept the exact bytes of this baseline and confirm:

1. SQLite single-node/single-writer scope, state/event/outbox/wake/effect/completion transactions;
2. exact DSH 0.1.5-rc.2 seams and no-core-patch boundary;
3. planning, wake, watchdog and SLO numeric values;
4. specialist catalog, autonomy limits and grants;
5. context route thresholds, cumulative budgets, schemas, fork predicates, AIWS profiles, CAS/replay and raw exclusion;
6. retention/redaction/dashboard privacy and threat owners;
7. package identity, clean-profile qualification and rollback;
8. effort adequacy and all residual limitations.

Silence, this document's existence, accepted t00 spikes, green tests, reviewer recommendation or coordinator opinion is not acceptance. Until explicit HUMAN acceptance is recorded, t01 remains unaccepted and t02 stays blocked.
