# Governed Agent Team (GAT) — Design and Feature Reference

**Status:** Project reference, not canonical Truth or activation approval  
**Last verified:** 2026-09-26  
**Driving work:** AIP-EXEC-014, AIP-EXEC-015, AIP-EXEC-018, AIP-EXEC-021
**Scope:** GAT `0.1.0` on the pinned DeepSeek Harness compatibility target, including its target relationship with Durable Agent MiniMVP

## 1. Purpose and authority

Governed Agent Team (GAT) is a private, opt-in distribution that adds a durable multi-agent Team to DeepSeek Harness (DSH). One top-level Session is the Team root, its Agent is the Lead, and continuable child Sessions are teammates. All members share the same workspace checkout.

This page is a maintained navigation and behavior reference. It distinguishes:

- **Implemented** — behavior evidenced by current source or tests.
- **Proposed** — design work that is not authority to deploy or activate.
- **Deferred** — explicitly unsupported or postponed behavior.

When this page conflicts with executable source, tests, installation records, or approved project Truth, those stronger sources win.

### Current-source status

AIP-EXEC-021 synchronized the selected DSH session-enable, bounded `team_members.yaml`, route-preflight, optional Agent route, and immediate-mission-authorization baseline into this standalone workspace through a controlled merge. The standalone package tree is now the authoring/distribution source for those behaviors; the installed DSH checkout remains the pinned host compatibility target.

The DSH baseline was a working-tree state rooted at commit `aeedf19995babaa28e35ca84624baff18a77a7d8`, so its commit id alone is not a complete behavioral revision. Use the AIP-EXEC-021 file-hash evidence and the source map in §13 when auditing provenance.

## 2. System overview

```text
Web conversation header
  └─ @vuhoi/gat-web
       └─ generated Remote: agentTeams/view, agentTeams/enable, mission/task APIs
            └─ @vuhoi/gat-core
                 ├─ root Session event log (durable authority)
                 ├─ roster and teammate lifecycle
                 ├─ durable peer mailbox
                 ├─ task, mission, and work-state projections
                 └─ runtime lifecycle/recovery

Model request scope
  └─ @vuhoi/gat-tools
       ├─ Team policy
       ├─ teammate/message/wait/status/task tools
       ├─ execution-readiness checks
       └─ session initializer
            └─ <Session cwd>/team_members.yaml or built-in roster

Durable member context (target integration; not yet wired into GAT)
  └─ @deepseek-ai/dsh-durable-agent
       ├─ immutable member profile
       ├─ SOUL.md
       ├─ bounded memory index/items
       └─ member working files

Composition
  ├─ @vuhoi/gat-profile       (Host/domain/tools)
  └─ @vuhoi/gat-web-profile   (browser panel)
```

GAT does not create a second orchestration database. Durable Team state is recorded in the Lead Session log and projected into roster, task, mission, mailbox, and work views. Durable Agent is a complementary persistence/context subsystem: its files may hold a member's stable profile, behavioral guidance, memory, and working artifacts, but they must not become a second authority for Team lifecycle or coordination state.

## 3. Package responsibilities

| Package | Responsibility | Status |
|---|---|---|
| `@vuhoi/gat-core` | Team identity, durable journal/projection, roster, mailbox, task board, missions, work state, recovery, Remote API | Implemented |
| `@vuhoi/gat-tools` | Model-facing Team policy and tools, member-route preflight, session initializer, readiness/admission checks | Implemented |
| `@vuhoi/gat-web` | Conversation-header Team panel, Enable action, current mission/member display, refresh, navigation | Implemented behavior; current source has type/injection drift noted in §9 |
| `@vuhoi/gat-profile` | Ordered Host composition over `dsh-base`; activates core/tools and disables overlapping legacy controls | Implemented, opt-in |
| `@vuhoi/gat-web-profile` | Adds the browser Team panel after the stable Web and Host Team layers | Implemented, opt-in |
| Installer | Copies verified packages and compatibility patches into a pinned DSH checkout; status/verify/rollback | Implemented |
| `@deepseek-ai/dsh-durable-agent` | Durable member profile, SOUL, bounded file-backed memory, and member working storage | Implemented as a separate MiniMVP; GAT integration is proposed |
| MCP reference-memory package | Partitioned governed reference memory proposed for GAT | Proposed/inactive and distinct from Durable Agent memory |

## 4. Team identity and durable model

### 4.1 Identity

- A top-level Session is the implicit Team root.
- `TeamId` equals the root `SessionId` with a Team brand.
- The root Agent is always the Lead.
- Each teammate is a continuable child Session with a durable, immutable Team name.
- Failed or previously used teammate names are not silently reused.

### 4.2 Member lifecycle

Durable teammate phase:

```text
provisioning -> active
             -> failed
```

Runtime view status is separate:

```text
running | idle | inactive | provisioning | failed
```

Creation first records a durable `provisioning` member, starts the continuable child, then records the terminal active/failed edge. Restart reconciliation checks persisted child evidence rather than inventing success.

### 4.3 Canonical state

The root Session event log is the durable authority. UI and tools read projected state rather than maintaining independent Team stores. Important projected data includes:

- `enabled`
- roster members
- queued/delivered Team messages
- shared tasks and plan revision
- missions and mission approval
- latest durable member work status

## 5. Session Enable lifecycle

### 5.1 Default state

With the GAT profile in `simpleMode: true`, a new Session starts solo:

- `TeamView.enabled === false`
- Team policy and Team-scoped tools are not installed for that Session
- opening the Web panel reads `agentTeams/view`
- the panel displays **Enable Agent Team for this session**

Profile installation and session Enable are different controls:

- **Profile activation** makes GAT capabilities available to DSH.
- **Session Enable** provisions the Team for one root Session.

### 5.2 Enable operation

The Web client calls `agentTeams/enable` for the Lead Session. The core service:

1. verifies the caller is the Team Lead;
2. returns the existing roster when the Session is already enabled;
3. invokes the single registered tools initializer otherwise;
4. serializes the mutation through the Team runtime lifecycle.

The tools initializer:

1. deduplicates concurrent Enable requests for the same Session;
2. derives the Lead's provider and Session workspace (`session.header.cwd`);
3. loads `team_members.yaml` or the built-in fallback roster;
4. preflights every configured member LLM route;
5. provisions members sequentially;
6. installs Team policy/tools after the first durable member event;
7. returns the source, diagnostics, and created member views.

### 5.3 Disable semantics

Current V1 activation is **one-way per Session**. There is no destructive Disable operation:

- the UI does not delete teammates;
- durable roster/history is not replaced;
- revisiting Enable on an existing Team returns `source: existing`;
- changes to `team_members.yaml` require a new Session to be loaded.

A real teardown/Disable contract is deferred because it must define active-turn cancellation, durable history, task ownership, mailbox, and restart semantics.

## 6. `team_members.yaml` member resolution

### 6.1 Exact lookup rule

The initializer resolves:

```ts
join(lead.session.header.cwd, 'team_members.yaml')
```

Therefore the operative file is the file in the **current Lead Session workspace**, not a globally hard-coded path.

For a Session whose workspace is this repository, that resolves to:

```text
/home/hoinv/work/dsh-governed-agent-team/team_members.yaml
```

If the Session uses another cwd, GAT reads the file from that other cwd.

### 6.2 Example

```yaml
version: 1
members:
  - name: advisor
    description: Advises the Lead when requested.
    prompt: >-
      Give evidence-based options, risks, and a concise recommendation.
    context: fresh
    provider: openai-codex
    model: gpt-5.6-sol

  - name: dev
    description: Handles normal implementation tasks.
    prompt: >-
      Implement assigned work and report verification evidence.
    context: fresh
    provider: openai-codex
    model: gpt-5.6-terra
    reasoning_effort: medium
```

### 6.3 Document schema

Top-level keys are strict:

| Field | Required | Contract |
|---|---:|---|
| `version` | yes | Must be integer `1` |
| `members` | yes | Non-empty array; length must not exceed `maxExecutionMembers` |

Unknown top-level keys reject the workspace configuration.

### 6.4 Member schema

| Field | Required | Contract |
|---|---:|---|
| `name` | yes | Unique lower-kebab-case; maximum 64 characters |
| `description` | yes | Trimmed non-empty string; maximum 200 characters |
| `prompt` | yes | Trimmed non-empty string; maximum 16,384 characters |
| `context` | no | `fresh` or `fork`; defaults to `fresh` |
| `provider` | yes | LLM provider id; trimmed; maximum 200 characters |
| `model` | yes | LLM model id; trimmed; maximum 200 characters |
| `reasoning_effort` | no | Provider/model reasoning effort; trimmed; maximum 80 characters |

Unknown member keys reject the workspace configuration. Duplicate names reject it.

### 6.5 File-safety and size rules

- The file must be a regular file.
- Symbolic links are rejected.
- The on-disk entry size and actual UTF-8 byte count are both bounded.
- Default `teamMembersMaxBytes` is `65,536`.
- `teamMembersMaxBytes`, `minExecutionMembers`, and `maxExecutionMembers` must be positive safe integers.
- `maxExecutionMembers` must be greater than or equal to `minExecutionMembers`.

### 6.6 Fallback behavior

Any roster file read, YAML parse, or roster-schema validation failure selects a built-in starter Team and returns a diagnostic. Examples include:

- Session has no workspace;
- file is missing;
- YAML is invalid;
- schema or names are invalid;
- file is a symlink or not a regular file;
- file exceeds the byte limit;
- member count exceeds the configured maximum.

Built-in members:

| Name | Model | Context | Intended role |
|---|---|---|---|
| `advisor` | `gpt-5.6-sol` | fresh | options, risks, recommendations |
| `senior-dev` | `gpt-5.6-sol` | fresh | complex implementation and rigorous review |
| `dev` | `gpt-5.6-terra` | fresh | normal implementation |
| `junior-dev` | `gpt-5.6-luna` | fresh | clearly specified simple work |

The built-in roster uses the Lead's current LLM provider and is truncated to `maxExecutionMembers`. Fallback selection is not guaranteed activation: provider/model route preflight occurs afterward, and a route-resolution failure aborts Enable rather than selecting another fallback.

### 6.7 Provider versus continuation provider

Two provider concepts are intentionally separate:

- YAML `provider` + `model` + optional `reasoning_effort` choose the child Agent's LLM route.
- Profile `freshProvider`/`forkProvider` choose the DSH continuable-subagent mechanism used to create the child Session.

A YAML member with `context: fork` uses `forkProvider`; `fresh` uses `freshProvider`.

### 6.8 Preflight and partial bootstrap

All configured LLM routes are resolved before the first teammate is provisioned. This prevents obvious route errors from producing a partial roster. Provisioning itself is sequential and not transactionally rolled back; a later process/provider failure may leave already-created durable members for inspection and recovery.

### 6.9 Durable Agent schema compatibility

Durable Agent uses the same manifest name and common member fields, but the schemas are **not unified today**:

| Rule | GAT current loader | Durable Agent MiniMVP | Consequence |
|---|---|---|---|
| `storage_scope` | Unknown field; rejects workspace roster validation and selects GAT's built-in roster before route preflight | Optional `workspace|global`; defaults to `workspace` | A Durable Agent manifest that explicitly declares scope is currently invalid for GAT |
| `context` | Optional; defaults to `fresh` | Required | A GAT-valid manifest omitting context is not Durable-Agent-valid |
| member count | Non-empty and bounded by `maxExecutionMembers` | No count limit stated in the MiniMVP document | Durable Agent validity does not guarantee GAT validity |
| text normalization/limits | Strict trimming and field-size limits | Exact limits are not stated in the MiniMVP document | Durable Agent validity does not guarantee GAT validity |

The current portable subset requires every member to include `context`, omit `storage_scope`, satisfy GAT's stricter text/count rules, remain below GAT's configurable `teamMembersMaxBytes` UTF-8 limit, and accept workspace-local Durable Agent storage by default. Sharing a filename does not establish a shared parser or shared authority.

## 7. Relationship to Durable Agent

### 7.1 Why the relationship is close

GAT and Durable Agent describe two halves of a durable multi-agent system:

- **GAT is the Team control plane and runtime orchestrator.** It owns the root Session, child Session creation, roster lifecycle, peer messages, shared tasks, missions, work status, readiness, recovery, tools, and Web projection.
- **Durable Agent is the member identity/context persistence plane.** It owns an immutable member profile, persistent behavioral guidance (`SOUL.md`), a bounded memory catalog with Markdown items, and member-owned working files.

Durable Agent deliberately does not automatically spawn agents, choose fallback routes, schedule concurrent tasks, supervise retries, or manage runtime lifecycle. Those responsibilities remain with GAT/DSH. Conversely, GAT currently does not provide persistent per-member SOUL/memory/working storage; that is the Durable Agent role.

### 7.2 Authority and responsibility boundary

| Concern | Authority |
|---|---|
| Team identity, membership, runtime status, child Session address | GAT root Session event log and DSH runtime |
| Messages, task board, missions, durable work status | GAT root Session event log |
| Member definition and storage-scope authorization | Current `team_members.yaml` manifest |
| Persisted immutable profile binding/conflict detection | Durable Agent `profile.json` checked against the authorized manifest |
| Effective child runtime route | GAT/DSH route resolution and child instantiation from the authorized member definition |
| Persistent behavioral guidance | Durable Agent `SOUL.md` |
| Per-member operational memory | Durable Agent `memory/index.json` and selected Markdown items |
| Member-owned working documents | Durable Agent `working/` |
| Repository files edited by agents | Shared workspace filesystem; neither subsystem provides isolation or locking |

Durable storage is not proof that a GAT teammate became active. A profile may exist for a failed or not-yet-started member. Likewise, a GAT active member does not imply that Durable Agent storage has been provisioned until an integration explicitly performs that step.

### 7.3 Identity and storage scopes

Both systems use `name`, but its authority differs:

- In GAT, the name is immutable within one root Team and maps to one child Session.
- In Durable Agent, the name is the durable directory identity under a storage scope.

Default workspace-local storage is:

```text
<workspace>/.dsh/durable-agents/<name>/
├── profile.json
├── SOUL.md
├── memory/
│   ├── index.json
│   └── <memory-id>.md
└── working/
```

Explicit global storage is:

```text
$HOME/.dsh/durable-agents/<name>/
```

A global member is allowed only when each workspace manifest explicitly authorizes the same name as global with the same immutable profile configuration. Global Durable Agent storage does **not** create global GAT membership, a shared child Session, a shared mailbox, or shared task ownership.

A subtle consequence is that two independently integrated GAT root Sessions using the same workspace and member name can resolve to the same workspace-local Durable Agent files when both are authorized by a compatible current manifest/profile. They still have different Team logs and child Sessions. Fallback members are not automatically authorized, and a profile conflict can prevent storage access. Any integration must address concurrent access and cross-Session memory sharing explicitly.

“Member-owned” is a logical ownership rule, not filesystem isolation. Because GAT members share the workspace, ordinary file tools may still modify another member's local SOUL, profile, memory, or working files unless the host adds enforcement. The integration must define who may mutate persistent behavioral guidance and protect immutable profile data through its API and filesystem policy.

### 7.4 Durable task context

Durable Agent storage contains:

- `profile.json` — schema version, identity, description, prompt, context, provider/model, effective scope, optional reasoning effort, and workspace binding for local members;
- `SOUL.md` — persistent behavioral guidance loaded for every task;
- `memory/index.json` — bounded catalog of `id`, `title`, `when_to_use`, and exact item filename;
- `memory/<memory-id>.md` — selectively loaded human-readable memory;
- `working/` — task-specific member-owned documents.

Provisioning is idempotent and preserves valid existing content. Profile conflicts fail closed instead of silently changing identity, route, owner, or scope. Local/global memory is never copied implicitly.

SOUL and memory are not replacements for GAT policy or Team state. Their **authority precedence** must be:

1. host safety/governance and HUMAN boundaries;
2. GAT Team role and coordination policy;
3. Durable Agent SOUL;
4. configured member prompt;
5. task-specific context and selectively retrieved memory.

Authority precedence does not by itself define literal prompt ordering. Durable Agent requires SOUL immediately after host system commands and before member/task context, while current GAT contributes its policy through the host system-prompt service and has no SOUL slot. A concrete integration must define one prompt-assembly contract that places non-overridable host/GAT governance before editable SOUL while preserving Durable Agent's placement requirement. This ordering is unresolved today.

### 7.5 Target integration sequence — proposed, not implemented

A safe integration should:

1. load and validate one canonical manifest snapshot rather than run two drifting parsers;
2. extend Durable Agent APIs to accept or atomically verify the Session-bound manifest digest/snapshot, because current APIs reload the live manifest on every operation;
3. resolve storage scope and validate every immutable profile/route binding;
4. preflight all member LLM routes before the first runtime side effect;
5. ensure durable member storage before the member's first task;
6. let GAT record `provisioning`, start the continuable child, and record `active` or `failed`;
7. load SOUL plus the bounded memory index before every task and open only relevant memory items; per-turn reload would require a separate invalidation contract;
8. keep Team events exclusively in the GAT root Session log and member persona/memory/working artifacts exclusively in Durable Agent storage;
9. on restart, reconcile child evidence and revalidate the durable profile before admitting the first resumed task or durable-context access; failure must surface a failed/degraded state instead of silently continuing;
10. require an explicit governed migration or a new durable identity for name, provider, model, reasoning-effort, or storage-scope changes.

### 7.6 Failure and drift rules — target contract

Authorization, identity-binding, controlled-file, and authority-conflict failures must fail closed. Lifecycle failures may preserve inspectable state but must surface an explicit failed/degraded status rather than continue silently:

- **Manifest drift:** GAT currently reads the roster at Enable, while Durable Agent reloads the manifest for every ensure/list/read/write call. A Session-bound digest alone is insufficient unless Durable Agent atomically verifies it or accepts snapshot-aware operations; otherwise later calls may authorize different bytes.
- **Schema drift:** current GAT rejects `storage_scope`; until a shared parser exists, adding it causes GAT to use the built-in fallback roster.
- **Fallback authorization:** GAT fallback members are synthesized from code and are not automatically authorized Durable Agent profiles. Durable storage must remain disabled for fallback members unless a separate policy explicitly authorizes it.
- **Route/profile conflict:** Durable Agent treats route and scope as immutable. Conflicts require migration or a new identity, not silent rewrite.
- **Partial provisioning:** file storage may exist without an active child; earlier members may remain active after a later failure. Preserved storage is inspectable evidence, not activation proof, and the incomplete activation must be reported as failed/degraded.
- **Concurrent writes:** workspace/global identities may be shared across Sessions, but the MiniMVP defines no locking or compare-and-set contract for memory updates. Until one exists, the integration must serialize writes or reject detected conflicts. Shared-filesystem tools also lack member-level isolation for direct SOUL/profile/working-file edits.
- **Policy conflict:** SOUL or memory that attempts to override HUMAN boundaries, Lead authority, tool restrictions, or no-silent-retry rules must not be admitted as effective authority.
- **Controlled-file validation:** apply each Durable Agent file type's own bounded contract. Profile binding conflicts fail closed; provisioning may create missing defaults where the MiniMVP explicitly allows it; task admission rejects invalid required SOUL or memory files, including applicable empty, oversized, NUL-containing, non-regular, or symlinked cases. Use the package's bounded APIs instead of trusting arbitrary paths.
- **Secret handling:** credentials and secrets must not be stored in profiles, SOUL, memory, discovery catalogs, Team messages, or task artifacts. Prompt policy is not a security boundary; enforcement belongs in trusted host/tool layers.

### 7.7 Durable Agent memory versus proposed GAT reference memory

These are separate layers:

- Durable Agent memory is private operational memory for one durable member, retrieved through a small `when_to_use` index.
- The proposed GAT MCP/reference-memory architecture is a governed shared/reference knowledge system with different partition, provenance, and retention goals.

The Durable Agent MiniMVP does not claim semantic/vector retrieval. Combining these layers requires an explicit provenance, retention, authorization, and conflict-resolution design.

### 7.8 Current implementation status

As of the verification date:

- Durable Agent MiniMVP behavior is documented and implemented in the separate `dsh-durable-agent` project.
- GAT and Durable Agent both consume `team_members.yaml`, but GAT is not wired to Durable Agent storage/context APIs.
- No GAT runtime code currently provisions `profile.json`, injects `SOUL.md`, loads member memory, or writes member `working/` files.
- The relationship and integration sequence in this section are target architecture, not current GAT runtime behavior.

### 7.9 Authorization and bounded discovery catalog — target contract

The enabled Session's validated manifest snapshot should authorize which durable identities may participate. A durable directory on disk is never sufficient authorization.

When the Team is disabled:

- no Durable Agent catalog or member context should be injected;
- existing profiles, SOUL, memory, and working files remain inert on disk;
- neither workspace-local nor global directories become dispatchable merely because they exist.

After Enable, the integration may expose a bounded catalog derived only from authorized members. It should contain routing metadata—not identity payloads:

- member name and description;
- effective workspace/global scope after schema harmonization;
- declared capabilities if a future harmonized schema supports them;
- current runtime availability/status supplied by GAT.

The catalog must not embed every member's full prompt, SOUL, or memory. Discovery also grants no authority to create or interrupt a teammate, assign work, write files, read another member's private memory, or bypass mission, task, review, or HUMAN gates. Fallback members require a separate Durable authorization rule and must not enter the catalog automatically.

### 7.10 Delegation and target-context contract — target contract

Before dispatch, the caller should verify:

1. Agent Team is enabled and the target is in the live authorized roster;
2. the member role fits the work and its runtime status permits dispatch;
3. the task contract states objective, scope, expected output, constraints, and verification;
4. required planning, review, approval, and dependency gates have passed;
5. shared-checkout write scopes are coordinated;
6. implementation and independent review remain separated when independence is required.

For each delegated task, the integration should verify the selected profile binding, reload that target's current SOUL and bounded memory index, and inject only task-relevant memory items. No other member's SOUL, prompt, or private memory should be included. Task authority comes from the explicit task/governance contract, not from role labels, catalog presence, SOUL, or remembered instructions.

For high-governance work, workspace policy may require `source: workspace` roster provenance and reject built-in fallback execution. All operators should inspect Enable diagnostics and roster source rather than assuming a malformed manifest produced the requested Team.

### 7.11 Learning and promotion boundary — target contract

Task findings do not automatically become durable truth. Reusable findings should first become bounded candidates with retrieval conditions, evidence/provenance, confidence, and limitations. Before promotion, compare against existing memory and project knowledge for duplication or conflict.

The promotion destination must remain explicit:

- private member memory;
- shared project knowledge candidate;
- guideline/process candidate;
- discard or task-local working artifact.

A member must not self-declare a finding “canonical” or “confirmed.” HUMAN or otherwise authorized review controls promotion. This complements, rather than replaces, the project's AIWS capture/review process.

### 7.12 Workspace adoption acceptance — target guidance

An adopting workspace may prepare a concise `AGENTS.md` pointer to a versioned Durable Agent Team reference instead of copying its complete contents into every prompt. Current-runtime preparation can verify:

- installed GAT Host/Web profiles and explicit per-Session Enable;
- a valid manifest using only fields supported by the installed GAT schema;
- intended roster source and absence of accidental fallback;
- independently valid Durable Agent profiles, role-specific SOUL files, bounded memory indexes, private working directories, regular-file/symlink safeguards, and completed legacy-memory migration where applicable.

The workspace is only **prepared for the bridge** after the current-runtime checks above. It becomes **integration-ready/adoption-accepted** only after installed runtime evidence also verifies:

- bounded authorized catalog injection occurs only after Enable;
- target-only context assembly and profile authorization are enforced per task;
- delegation contracts, governance gates, write-scope coordination, and status reporting are wired to GAT;
- learning candidates follow reviewed promotion rather than automatic memory or guideline mutation.

This checklist is target adoption guidance, not evidence that the bridge exists in the installed runtime. Until integration is implemented, workspace instructions must label these integration-only gates explicitly.

## 8. Implemented Team capabilities

### 8.1 Roster and delegation

- Lead-only teammate creation.
- Fresh or fork context.
- Optional exact provider/model/reasoning route.
- Durable provisioning, active, and failed records.
- Runtime-enriched status and diagnostics.
- Lead-only interruption of a current teammate turn.

### 8.2 Durable peer messaging

- Any Team member can message another member or the Lead.
- Running targets receive the message at a step boundary.
- Idle targets start a turn.
- Inactive teammates cold-resume.
- Delivery result is `accepted` or durably `queued`.
- A queued message must not be resent.
- Target Session evidence prevents duplicate delivery across recovery.

### 8.3 Shared task board

Tasks support:

- creation with subject, description, dependencies, and advisory write scopes;
- claim, release, reassign, complete, reopen, edit, dependency update, and delete;
- compare-and-set revision checks;
- dependency readiness;
- owner checks;
- advisory write-scope overlap warnings;
- durable history for deleted tasks.

Write-scope warnings coordinate agents but are not filesystem locks.

### 8.4 Durable work reporting

Each member can publish a latest work state:

```text
working | blocked | review_required | done
```

Work state is distinct from runtime state. `blocked` includes a reason; `review_required` includes review files. Event time becomes `updatedAt` in the view.

### 8.5 Missions

GAT supports independently governed mission records with:

- title and objective;
- mission-local immutable plan snapshot;
- revision and status;
- exact-revision HUMAN approval representation.

In current simple mode, readiness skips the legacy Team-plan approval check and the simplified panel exposes no Team-plan approval action. Package prose describes a HUMAN-authored mission as authorization, but current code does not verify mission authorship or require a mission for readiness. Treat that statement as intended policy, not an enforced invariant.

### 8.6 Model-facing tools

| Tool | Capability |
|---|---|
| `spawn_teammate` | Lead creates one durable teammate |
| `list_agents` | Read roster and runtime status |
| `send_message` | Durable peer steer/message |
| `interrupt_agent` | Lead interrupts one teammate turn |
| `wait_agent` | Wait for subsequent Team/member/task activity |
| `report_team_status` | Publish durable work status |
| `team_task_create` | Create an unowned task |
| `team_task_list` | List/filter task board |
| `team_task_get` | Read one current task revision |
| `team_task_update` | Compare-and-set task mutation |

The tools are registered in Team member scopes, not globally for arbitrary subagents.

## 9. Web UI behavior

Implemented Web behavior includes:

- conversation-header Agent Team action;
- off-state explanation and session Enable action;
- loading and Remote error presentation;
- current mission display;
- member roster with runtime status, model, diagnostics, and durable work;
- presentation-only suspected-stall warning;
- teammate conversation navigation through the stable addressed-child route;
- review-file navigation;
- refresh on panel open, explicit refresh, and bounded polling while open;
- stale async response protection when the active Session changes.

The simplified current panel intentionally does not expose mission/task creation controls or the task list. The backend and model tools may still retain those capabilities.

### Installed DSH baseline Web drift

The selected DSH working-tree baseline contains a type/injection mismatch that EXEC-A intentionally did not copy:

- its core/client surface removes `ImportApprovedTeamPlanResult` while `TeamAction.tsx` still imports it;
- its `mount.ts` removes `approveMission` and `importApprovedPlan` while the unchanged `TeamActionInjected` interface still requires them.

The synchronized standalone source retains the newer approved-plan type and both action injections, so its interface remains internally consistent. The simplified render path still does not expose those controls. The installed DSH checkout remains unchanged until a later verified installer application.

## 10. Governance and execution controls

GAT's governing principles are:

- **Opt-in:** package/profile activation is explicit; session Team activation is explicit.
- **Single durable authority:** root Session events drive UI and tools.
- **Explicit Lead authority:** only the Lead can create or interrupt teammates.
- **HUMAN boundary:** the model cannot invent HUMAN approval or acceptance.
- **Scoped tools:** Team tools/policy appear only after Team activation in simple mode.
- **Fail-closed revisions:** stale task or approval mutations are rejected.
- **Shared-checkout coordination:** tasks and write scopes coordinate work but do not isolate files.
- **No silent retries:** queued messages are already durable; repeated sends risk duplication.
- **Readiness/admission checks:** configured membership and capability requirements are checked before governed execution.

AI Work System governance remains separate and authoritative where adopted: non-trivial work requires its Working AIP/Workspace flow, wiki-first lookup, capture, and lint. GAT does not bypass those gates.

## 11. Installation and activation

The installer targets a pinned DSH version/commit and copies packages into:

```text
packages/experimental/gat-core
packages/experimental/gat-tools
packages/experimental/gat-web
packages/experimental/gat-profile
packages/experimental/gat-web-profile
```

It also applies compatibility patches and records installed checksums. Installation does **not** activate a profile, start Web, or call an AI provider.

After verification and build, Host and Web profile layers must be added explicitly. The Web profile order is:

```text
dsh-base -> dsh-web-app -> gat-profile -> gat-web-profile
```

The live browser at `http://127.0.0.1:3080` uses built package entrypoints. Editing source alone is insufficient: rebuild `@vuhoi/gat-web` and refresh/restart the existing DSH Web process as appropriate.

## 12. Limitations and deferred behavior

Current limitations:

- one DSH process and one shared checkout;
- no worktree isolation or filesystem locking;
- one-way session activation; no destructive Disable;
- no automatic roster replacement after YAML changes;
- no atomic rollback of a partially provisioned Team;
- no cross-process Team consensus;
- no autonomous retry/watchdog/root-cause engine;
- no mailbox timeline in the Web panel;
- no production stability guarantee for private experimental packages;
- prompt policy coordinates behavior but is not a security sandbox;
- no current GAT–Durable Agent runtime integration, shared manifest parser, SOUL injection, memory loading, or concurrent durable-memory write protocol.

Proposed but not current runtime behavior includes the GAT–Durable Agent integration in §7 and the partitioned MCP reference-memory architecture, semantic/vector retrieval, advanced retention/audit topology, and activation-manifest controls described in `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`.

## 13. Source and evidence map

### Project/distribution sources

- `README.md` — install, verify, activate, rollback, compatibility.
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md` — accepted V1 design foundation; some approval behavior predates simple mode.
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` — frozen EXEC-B/EXEC-C ownership, attachment, binder, lifecycle, authorization, and conformance boundary; not implementation authority.
- `packages/core/README.md` — core domain behavior.
- `packages/tools/README.md` — tool surface; may lag the installed runtime during synchronization.
- `packages/web/README.md` — Web package behavior; may lag the installed runtime during synchronization.
- `packages/profile/README.md` — Host composition.
- `packages/web-profile/README.md` — Web composition.
- `team_members.yaml` — this workspace's configured roster.
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md` — external Durable Agent MiniMVP manifest, storage, SOUL, memory, and non-goal contract; not currently registered in this project's Wiki.
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENT_TEAM_REFERENCE.md` — external target integration and workspace-adoption reference used for authorization, catalog, delegation, learning, and acceptance deltas; not proof of installed GAT behavior and not currently registered in this project's Wiki.

### Latest installed-runtime evidence at verification time

- `/home/hoinv/deepseek-harness/packages/experimental/gat-core/src/types.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-core/src/index.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/src/team-config.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/src/index.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/tests/team-config.spec.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-web/src/client/TeamAction.tsx`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-web/src/client/mount.ts`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-web/README.md`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-profile/README.md`

## 14. Maintenance checklist

Update this reference when any of the following changes:

1. `team_members.yaml` schema, limits, path, or fallback roster;
2. session Enable/Disable lifecycle;
3. Team Remote or tool surface;
4. Web panel functions;
5. profile composition or defaults;
6. readiness/approval semantics;
7. installer compatibility target;
8. Durable Agent manifest, profile, SOUL, memory, storage-scope, or task-context contract;
9. Durable Agent catalog, authorization, delegation, learning-promotion, or workspace-adoption contract;
10. the GAT–Durable Agent integration moves from proposed to implemented;
11. an item moves from proposed/deferred to implemented.

Before updating behavioral claims, verify the implementation and focused tests, then record the source path and verification date. Registering this page in the project Wiki Source Index remains a separate HUMAN-reviewed curation action.
