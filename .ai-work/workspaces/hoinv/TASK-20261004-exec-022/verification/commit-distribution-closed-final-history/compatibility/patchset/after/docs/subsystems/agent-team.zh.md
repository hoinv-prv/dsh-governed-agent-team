# Agent Teams

[English](agent-team.md) | 中文

实验性隐式 Root Team 领域、模型工具与宿主适配器共享的类型。[Agent Teams Agent Note](../../.agents/notes/implemented/feature/2026-08-05-agent-teams.zh.md)负责身份、mailbox、task 与共享 checkout 决策；本页记录 [`packages/experimental/agent-team/src/types.ts`](../../packages/experimental/agent-team/src/types.ts) 中的字面持久形式。

在明确选择 GAT 替代包的工作区中，当前授权及绑定契约由 [`gat-core`](../../packages/experimental/gat-core/README.zh.md) 拥有；参见[经认证的控制决策](../../.agents/notes/implemented/architecture/2026-10-04-authenticated-control-admission.zh.md)。下方手写示例描述保留的原型。生成的 API 区域通过[明确的替代所有权](../../.agents/notes/implemented/process/2026-10-04-active-catalog-replacements.zh.md) 跟随选中的包声明。

对于必需 GAT 绑定，Host 在 Team enable 之前注册 binder，并在 reserved-child 释放之前提供精确 mission/task 授权。[Durable 层](../../packages/experimental/gat-durable-profile/README.zh.md)选择专用 WK provider 和严格 workspace 声明。必需 contribution 在每次 prompt 渲染前刷新；移除它们会使精确 generation 失效。恢复读取持久 attachment 并保留初始消息身份；对于初始消息已消费的恢复，会在释放前将已授权 pending mailbox work 持久暂存。

## 身份与 roster

`TeamId` 是具有独立[品牌](core.zh.md#branded-ids)的 Root `SessionId`。`TeamTaskId` 在 Team 内按 `task-<n>` 单调分配；`TeamMessageId` 是全局随机值。teammate 的 Session id 始终是持久身份，而 `name` 是不可变的模型／UI 标签。

```ts type-equiv
/** Whole durable value written on every teammate lifecycle change. */
interface TeamMemberSnapshot {
  readonly id: SessionId
  readonly name: string
  readonly description: string
  readonly provider: string
  readonly context: 'fresh' | 'fork'
  readonly phase: TeamMemberPhase
  readonly error?: string
}
```

每个 member 都从 `provisioning` 开始，并且只到达一个终态 roster phase：`active` 或 `failed`。运行时 `running`／`idle`／`inactive` 状态单独派生，绝不会重写该记录。

## 持久 mailbox

Lead Session 首先存储完整 queued message。只有 target 的 pending inbox 条目或已记录用户消息完成持久化，才会写入独立 acknowledgement event，queued-minus-delivered 因而构成恢复 mailbox。

```ts type-equiv
/** One peer message retained until its target Session records it. */
interface TeamMessageSnapshot {
  readonly id: TeamMessageId
  readonly senderId: SessionId
  readonly senderName: string
  readonly targetId: SessionId
  readonly content: ContentBlock[]
}
```

每条消息都会尝试 Steer 投递。running target 在最近的步骤边界收到消息，idle target 启动一个轮次，inactive teammate 则冷恢复。调用方不能选择其他模式，因此持久记录不存储调度方式。

target Session 会在 pending inbox 条目和最终用户消息上保留消息身份与发送者归因。跨 inbox 与历史折叠该 source 构成 target 侧去重键；模型可见的 framing 会重复 id 和发送者。

```ts type-equiv
/** Source retained by the target Session for durable mailbox de-duplication. */
interface TeamMessageSource {
  readonly kind: 'team-message'
  readonly teamId: TeamId
  readonly messageId: TeamMessageId
  readonly senderId: SessionId
  readonly senderName: string
}
```

## 共享任务 DAG

每条 task event 都存储完整快照。`revision` 是 compare-and-set 值，每次变更递增 1。`blockedBy` edge 必须指向未删除任务，并维持无环图。`writeScopes` 是规范化的提示性路径前缀，不是锁。

```ts type-equiv
/** Whole durable task snapshot; every mutation increments {@link revision}. */
interface TeamTaskSnapshot {
  readonly id: TeamTaskId
  readonly revision: number
  readonly subject: string
  readonly description: string
  readonly status: TeamTaskStatus
  readonly ownerId?: SessionId
  readonly blockedBy: TeamTaskId[]
  readonly writeScopes: string[]
}
```

`pending` 表示尚未开始或已经释放，`in_progress` 携带 owner，`completed` 满足 blocker，`deleted` 是保留的 tombstone。view 会添加 owner name、readiness 和 write-scope 重叠警告，但不会改变持久快照。

## 回放

`foldTeam()` 把一个 Root Session 回放成每个 Team 操作所读取的 roster、任务板与 queued-minus-delivered mailbox。它按 `TeamId` 选取记录，因此普通 fork 继承的 event 保留 ancestor id，绝不会进入新 Root 的状态。Session event 的 `seq` 与 `time` 继续负责顺序和时间记录，Team snapshot 不再重复保存它们。roster 与 task 读取以 view 形式到达调用方，而 pending 邮件仅供投递与恢复内部使用。包 [README](../../packages/experimental/agent-team/README.zh.md)负责 operation、authorization、recovery 和限制行为。

<!-- BEGIN GENERATED cordis-surface (gen-cordis-catalog.ts) — do not edit between markers -->

<a id="cordis-surface"></a>

## Cordis API

Generated from source by `scripts/gen-cordis-catalog.ts` (verified fresh by `pnpm run verify-cordis-catalog` in doc-sync; regenerate with `pnpm run gen-cordis-catalog`) — the language sides differ only in locale-specific paired document paths. Signature blocks use a `ts cordis-catalog` fence and keep the original source JSDoc; dispatch modes are defined in the [primer](../cordis-primer.zh.md#dispatch-modes), and the framework-inherited `ctx` API lives in [cordis-api/inherited.md](../cordis-api/inherited.md).

<a id="ctxagentteams--teamservice"></a>

### `ctx.agentTeams` — `TeamService`

Agent Teams service backed by the exact live Lead Session log.

```ts cordis-catalog
/**
 * Set the additional exact HUMAN current-plan requirement for non-simple mode.
 * @param requireCurrentPlan - whether admission additionally requires the exact current HUMAN-approved Team plan.
 */
configureExecutionPolicy(requireCurrentPlan: boolean): void

/**
 * Host-only binding of an opaque lease to the exact live Agent generation.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - explicit mission identity/revision and optional claimed task selected by trusted host code.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
bindExecution(caller: Agent, request: BindTeamExecutionRequest): void

/**
 * Revalidate exact canonical mission and task authorization before execution.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param taskId - optional exact claimed canonical task to revalidate.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
assertExecution(caller: Agent, taskId?: TeamTaskId): void

/**
 * Release one prepared member initial item after its host-selected exact lease is bound.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param signal - cancellation checked before admission and during host preparation.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async activateMember(caller: Agent, signal: AbortSignal): Promise<void>

/**
 * Cold-recover one explicitly selected member and bind its exact host-selected mission scope.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param targetName - explicit durable active member name selected by trusted host control.
 * @param request - explicit mission identity/revision and optional claimed task for the recovered generation.
 * @param signal - cancellation checked before admission and during host preparation.
 * @returns the newly recovered exact Agent after binding and gated activation.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async recoverMember(caller: Agent, targetName: string, request: BindTeamExecutionRequest, signal: AbortSignal): Promise<Agent>

/**
 * Report a safe authority diagnostic for tools without exposing lease fields.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @returns the denial reason, or undefined when the exact current scope is authorized.
 */
executionDiagnostic(caller: Agent): string | undefined

/**
 * Resolve one exact live Agent's Team role.
 * @param agent - exact live Agent used as the authority credential.
 * @returns its root, Team identity, role, and model-facing name.
 */
membership(agent: Agent): TeamMembership

/**
 * List the runtime-enriched roster visible to one Team member.
 * @param agent - exact live Team member.
 * @returns Lead and teammate rows in creation order.
 */
listMembers(agent: Agent): TeamMemberView[]

/**
 * Approve one exact immutable member specification; the one-use grant permits quarantine only.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - exact immutable member specification covered by the one-use authenticated control receipt.
 * @returns confirmation after durable approval; the grant permits quarantine only.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async approveMemberAdd(caller: Agent, request: ApproveTeamMemberAddRequest): Promise<{ readonly approved: true }>

/**
 * Host-attested HUMAN member-add action; arbitrary model specs cannot mint grants.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param request - exact immutable member specification covered by the authenticated HTTP action.
 * @returns durable approval confirmation; child activation requires its separate exact lease.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('approveMemberAdd') remoteApproveMemberAdd(agent: Agent, request: ApproveTeamMemberAddRequest): Promise<{ readonly approved: true }>

/**
 * Create one named, continuable direct child of the Team Lead.
 * @param caller - exact live Lead Agent.
 * @param request - immutable name, description, prompt, context mode, provider, and cancellation.
 * @returns the active roster row.
 */
async spawnTeammate(caller: Agent, request: SpawnTeammateRequest): Promise<SpawnTeammateResult>

/**
 * Queue one durable peer message, then attempt immediate delivery.
 * @param caller - exact live sending Team member.
 * @param request - target name, content, and pre-queue cancellation.
 * @returns durable message identity and immediate-delivery observation.
 */
async sendMessage(caller: Agent, request: SendTeamMessageRequest): Promise<SendTeamMessageResult>

/**
 * Create one independently governed durable mission.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - mission title/objective and empty canonical task-reference plan.
 * @returns the new durable draft mission without executable approval.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async createMission(caller: Agent, request: CreateTeamMissionRequest): Promise<TeamMissionView>

/**
 * Return one mission including its mission-local task set.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param id - explicit mission identity in this Team.
 * @returns a detached mission view containing canonical task references.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
getMission(caller: Agent, id: TeamMissionId): TeamMissionView

/**
 * List the Team's independently governed missions.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @returns detached mission views for this exact Team.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
listMissions(caller: Agent): TeamMissionView[]

/**
 * Approve exactly the current revision of one mission.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
 * @returns the durably approved exact revision with authenticated provenance.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async approveMission(caller: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionView>

/**
 * Close one exact mission revision using authenticated HUMAN control.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
 * @returns the durably closed mission with previous leases invalidated.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async closeMission(caller: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionView>

/**
 * Revoke one exact mission revision using authenticated HUMAN control.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
 * @returns the durably revoked mission with previous leases invalidated.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async revokeMission(caller: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionView>

/**
 * Create one unowned pending task in the Team Lead log.
 * @param caller - exact live Team member creating the task.
 * @param request - explicit mission association, task text, blockers, and advisory write scopes.
 * @returns the revision-one task view.
 */
async createTask(caller: Agent, request: CreateTeamTaskRequest): Promise<TeamTaskView>

/**
 * Return one task, including a deleted tombstone.
 * @param caller - exact live Team member reading the task.
 * @param id - Team-local task identity.
 * @returns the latest task value and derived readiness diagnostics.
 */
getTask(caller: Agent, id: TeamTaskId): TeamTaskView

/**
 * List current non-deleted tasks in numeric creation order.
 * @param caller - exact live Team member reading the board.
 * @returns detached current task views.
 */
listTasks(caller: Agent): TeamTaskView[]

/**
 * Compare-and-set one authorized task transition.
 * @param caller - exact live Team member authorizing the mutation.
 * @param request - task identity, expected revision, action, and action fields.
 * @returns the committed next task revision.
 */
async updateTask(caller: Agent, request: UpdateTeamTaskRequest): Promise<TeamTaskView>

/**
 * Commit HUMAN approval of the exact current non-empty structural plan revision.
 * @param caller - exact live Lead Agent selected by the Web Remote authority.
 * @param request - revision displayed to the approving HUMAN.
 * @returns the committed approval snapshot.
 */
async approvePlan(caller: Agent, request: ApproveTeamPlanRequest): Promise<TeamPlanApprovalSnapshot>

/**
 * * Import the latest successful HUMAN-approved DSH plan and approve its exact
 * post-import revision in one serialized Lead-log batch.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param request - explicit target mission identity for canonical imported task association.
 * @returns the approval of the exact post-import canonical plan revision.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async importApprovedPlanAndApprove(caller: Agent, request: { readonly missionId: TeamMissionId }): Promise<TeamPlanApprovalSnapshot>

/**
 * Register one live capability-envelope check at the HUMAN approval boundary.
 * @param preflight - synchronous check over the exact caller and current Team view.
 * @returns disposer that removes this approval check.
 */
registerApprovalPreflight(preflight: (caller: Agent, view: TeamView) => readonly string[]): () => void

/** Register one host-owned attachment protocol; removal verifies all durable references.
 * @param binder - required attachment protocol participant.
 * @returns asynchronous disposer that refuses referenced or pending registrations.
 */
registerMemberBinder(binder: TeamMemberBinder): () => Promise<void>

/**
 * Register the host initializer used by the session-scoped Enable action.
 * @param initializer - trusted default-roster producer evaluated before any member creation.
 * @returns an unregister function for this exact initializer.
 */
registerInitializer(initializer: TeamInitializer): () => void

/**
 * Enable this Lead Session's Team once, provisioning its configured members.
 * @param caller - exact live Team Agent; Lead identity alone supplies no HUMAN approval.
 * @param signal - cancellation checked before admission and during host preparation.
 * @returns the provisioned default roster; children remain gated until exact execution authorization.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
async enable(caller: Agent, signal: AbortSignal): Promise<TeamEnableResult>

/**
 * Report the exact caller's latest durable work state.
 * @param caller - exact live Team member reporting current work.
 * @param request - durable state, summary, optional reason/task, and affected files.
 * @returns the committed authoritative work view.
 */
async reportWork(caller: Agent, request: ReportTeamWorkRequest): Promise<TeamWorkView>

/**
 * Wait for the next Team-domain or member-status change.
 * @param caller - exact live Team member waiting for activity.
 * @param timeoutMs - bounded wait duration from ten seconds through one hour.
 * @param signal - caller cancellation for the wait only.
 * @returns one observed change or a timeout result.
 */
async waitForChange(caller: Agent, timeoutMs: number, signal: AbortSignal): Promise<TeamWaitResult>

/**
 * Interrupt one live teammate turn without clearing its pending inbox.
 * @param caller - exact live Lead Agent.
 * @param targetName - durable teammate name.
 * @returns the target status sampled before cancellation.
 */
interrupt(caller: Agent, targetName: string): { previousStatus: 'running' | 'idle' | 'inactive' }

/**
 * Resolve a caller without throwing, used by scoped-tool installation and observers.
 * @param agent - candidate exact live Agent.
 * @returns Team membership, or undefined for non-Team subagents and stale identities.
 */
tryMembership(agent: Agent): TeamMembership | undefined

/**
 * Read the current roster and non-deleted task board through the generated Remote API.
 * @param agent - exact live Team member used as the authority credential.
 * @returns detached current roster and task views.
 */
@Remote('view') remoteView(agent: Agent): TeamView

/**
 * Enable and provision this Lead Session's Agent Team through the generated Web Remote API.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param signal - cancellation checked before admission and during host preparation.
 * @returns the default-roster provisioning result; child model admission remains separately gated.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('enable') remoteEnable(agent: Agent, signal: AbortSignal): Promise<TeamEnableResult>

/**
 * Create one mission through the generated Web Remote API.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param request - mission title/objective and empty canonical task-reference plan.
 * @returns the draft mission or a typed business rejection.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('createMission') remoteCreateMission(agent: Agent, request: CreateTeamMissionRequest): Promise<TeamMissionMutationResult>

/**
 * List independently governed missions through the generated Web Remote API.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @returns detached mission views for this Team.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('listMissions') remoteListMissions(agent: Agent): TeamMissionView[]

/**
 * Get one mission through the generated Web Remote API.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param id - explicit mission identity in this Team.
 * @returns the detached explicitly requested mission.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('getMission') remoteGetMission(agent: Agent, id: TeamMissionId): TeamMissionView

/**
 * Approve one exact mission revision through the generated Web Remote API.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
 * @returns the committed approval or a typed business rejection.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('approveMission') remoteApproveMission(agent: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionMutationResult>

/**
 * Close one exact mission revision through authenticated Web control.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
 * @returns the committed closure or a typed business rejection.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('closeMission') remoteCloseMission(agent: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionMutationResult>

/**
 * Revoke one exact mission revision through authenticated Web control.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param request - explicit mission identity and displayed current revision protected by authenticated HUMAN control.
 * @returns the committed revocation or a typed business rejection.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('revokeMission') remoteRevokeMission(agent: Agent, request: ApproveTeamMissionRequest): Promise<TeamMissionMutationResult>

/**
 * Create one shared task through the generated Remote API.
 * @param agent - exact live Team member creating the task.
 * @param request - explicit mission association, task text, blockers, and advisory write scopes.
 * @returns the revision-one task or a typed Team rejection.
 */
@Remote('createTask') remoteCreateTask(agent: Agent, request: CreateTeamTaskRequest): Promise<TeamTaskMutationResult>

/**
 * Apply one task mutation and preserve Team rejections as business results.
 * @param agent - exact live Team member authorizing the mutation.
 * @param request - task identity, expected revision, action, and action fields.
 * @returns the committed task or a typed Team rejection.
 */
@Remote('updateTask') remoteUpdateTask(agent: Agent, request: UpdateTeamTaskRequest): Promise<TeamTaskMutationResult>

/**
 * Approve one exact displayed plan revision through the generated Web Remote API.
 * @param agent - exact live Lead Agent used as the authority credential.
 * @param request - revision displayed to the approving HUMAN.
 * @returns the committed approval or a typed plan conflict/rejection.
 */
@Remote('approvePlan') async remoteApprovePlan(agent: Agent, request: ApproveTeamPlanRequest): Promise<TeamPlanApprovalResult>

/**
 * Import the latest approved DSH plan and approve it through one Web Remote action.
 * @param agent - exact live Agent resolved by the host or Gateway.
 * @param request - explicit target mission identity reviewed by HUMAN control.
 * @returns the committed plan approval or a typed import/preflight rejection.
 * @throws TeamError when identity, canonical revision, durable authority, or lifecycle admission is invalid.
 */
@Remote('importApprovedPlan') async remoteImportApprovedPlan(agent: Agent, request: { readonly missionId: TeamMissionId }): Promise<ImportApprovedTeamPlanResult>

/**
 * Report caller-bound member work through the generated Web Remote API.
 * @param agent - exact live Team member reporting current work.
 * @param request - durable state, summary, optional reason/task, and affected files.
 * @returns the committed report or a typed Team rejection.
 */
@Remote('reportWork') async remoteReportWork(agent: Agent, request: ReportTeamWorkRequest): Promise<TeamWorkMutationResult>
```

Types: [Agent](core.zh.md)

Source: [`packages/experimental/gat-core/src/index.ts`](../../packages/experimental/gat-core/src/index.ts)
<!-- END GENERATED cordis-surface -->
