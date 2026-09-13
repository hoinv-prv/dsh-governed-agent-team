/** Scoped model-facing tools for the opt-in Agent Teams runtime. */

import type { Context } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type {} from '@deepseek-ai/dsh-subagent'
import { scopesOverlap, TeamTaskId } from '@vuhoi/gat-core'
import type { TeamMemberView, TeamView } from '@vuhoi/gat-core'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { InferValue, ValueSchemaSpec } from '@deepseek-ai/dsh-tools'

/** Cordis plugin name. */
export const name = 'tool-agent-team'
/** Services required by the Team tool plugin. */
export const inject = ['agents', 'agentTeams', 'subagents', 'tools', 'systemPrompt']

/** Tool routing configuration. */
export interface Config {
  /** Continuable-subagent provider used for fresh teammates. */
  readonly freshProvider?: string
  /** Continuable-subagent provider used for completed-prefix fork teammates. */
  readonly forkProvider?: string
  /** External read/HUMAN-interaction tools admitted while Team execution is restricted. */
  readonly externalRestrictedTools?: string[]
  /** Durable active teammates required before non-restricted execution. */
  readonly minExecutionMembers?: number
  /** Maximum durable active teammates the Team Lead may create. */
  readonly maxExecutionMembers?: number
}

/** Loader schema for the opt-in Team tool plugin. */
export const Config: z<Config> = z.object({
  freshProvider: z.string().default('spawn'),
  forkProvider: z.string().default('fork'),
  externalRestrictedTools: z.array(z.string().min(1)).default([]),
  minExecutionMembers: z.natural().min(1).max(Number.MAX_SAFE_INTEGER).default(2),
  maxExecutionMembers: z.natural().min(1).max(Number.MAX_SAFE_INTEGER).default(4),
})

/** Model-facing collaboration guidance shared by Lead and teammates. */
const POLICY = `Agent Teams is available in this session, but create teammates only when the user explicitly asks to use Agent Teams or teammates.

The Team Lead and all teammates share the same working directory and filesystem. Edits are immediately visible to every member. Split write work into disjoint scopes, record expected write scopes on shared tasks, and use task dependencies when work must be ordered. Write-scope overlap is advisory, not a lock.

Prefer read/edit/write for file changes. If a file operation returns FS_STALE_VERSION, read the current file, rebase your intended change onto the new content, and retry. Bash, formatters, code generators, and scripts are not fully protected by the filesystem version guard; coordinate them explicitly and have the Lead review the final diff and run tests.

send_message steers a running target at its nearest step boundary, starts an idle target, and cold-resumes an inactive teammate. A delivered peer item starts with its stable message id and sender name. A successful send is already durable even when its result says queued; do not resend it. Shared-task workflow is list, get, claim with the current revision, perform the work, then complete. Task readiness never starts an owner. Before wait_agent, use list_agents and make sure another required member is running or provisioning; use send_message first when the required member is inactive. wait_agent observes only changes after that call starts, never wakes a member, and returns noProgress immediately when no other member can produce a change. Re-list after wakeup or timeout. The Lead must wait for required teammates before giving the final answer.`

const ACTIVE_WAIT_STATUSES: ReadonlySet<TeamMemberView['status']> = new Set(['running', 'provisioning'])
const OWN_RESTRICTED_TOOLS = new Set([
  'list_agents',
  'wait_agent',
  'send_message',
  'team_task_create',
  'team_task_list',
  'team_task_get',
])
const RESTRICTED_REPORT_STATES = new Set(['blocked', 'review_required'])
const STRUCTURAL_TASK_ACTIONS = new Set(['edit', 'set_dependencies', 'delete'])
const NO_ACTIVE_PEER_MESSAGE = 'No other Team member is running or provisioning. wait_agent cannot make progress or wake inactive teammates. Re-list with list_agents and team_task_list, then use send_message to wake each required inactive teammate before waiting again.'

/** Count durable teammate rows without treating runtime idleness as removal. */
function durableActiveTeammates(view: TeamView): number {
  return view.members.filter(member => member.role === 'teammate'
    && member.status !== 'provisioning' && member.status !== 'failed').length
}

/** Return the current approval failure, if any, with revision values actionable. */
function approvalFailure(view: TeamView): string | undefined {
  if (view.planApproval === undefined) {
    return `current Team plan revision ${view.planRevision} is not HUMAN-approved`
  }
  if (view.planPhase !== 'approved' || view.planApproval.approvedRevision !== view.planRevision) {
    return `approved revision ${view.planApproval.approvedRevision} is stale for current revision ${view.planRevision}`
  }
  return undefined
}

/** Read the canonical Team view and convert projection failures into one stable denial. */
function guardedTeamView(ctx: Context, agent: Agent): TeamView | string {
  try {
    return ctx.agentTeams.remoteView(agent)
  } catch {
    return 'canonical Team projection is unavailable; execution is fail-closed until it can be resolved'
  }
}

/** Admit only the exact built-in repair operation, including status arguments. */
function restrictedOwnToolAdmission(name: string, args: unknown): boolean | string {
  if (OWN_RESTRICTED_TOOLS.has(name)) return true
  if (name !== 'report_team_status') return false
  const state = typeof args === 'object' && args !== null && 'state' in args
    ? (args as { state?: unknown }).state
    : undefined
  if (typeof state === 'string' && RESTRICTED_REPORT_STATES.has(state)) return true
  const received = typeof state === 'string' ? JSON.stringify(state) : `<${typeof state}>`
  return `Team status reporting is restricted to blocked or review_required while Team execution is restricted; received state ${received}`
}

/** Canonical capability and complete-WBS predicate shared by approval, preflight, and dispatch. */
function completeEnvelopeDiagnostics(
  current: TeamView,
  agent: Agent,
  ctx: Context,
  config: Required<Config>,
): string[] {
  const envelopeDiagnostics: string[] = []
  for (const provider of [...new Set([config.freshProvider, config.forkProvider])].sort()) {
    if (ctx.subagents.getProvider(provider) === undefined) envelopeDiagnostics.push(`spawn provider "${provider}" is unavailable`)
  }
  const visibleTools = new Set(ctx.tools.schemas(agent).map(schema => schema.name))
  for (const toolName of [...new Set(config.externalRestrictedTools)].sort()) {
    if (!visibleTools.has(toolName)) envelopeDiagnostics.push(`configured restricted tool "${toolName}" is unavailable`)
  }
  const tasks = [...current.tasks].sort((left, right) => String(left.id).localeCompare(String(right.id)))
  for (const [index, task] of tasks.entries()) {
    for (const other of tasks.slice(index + 1)) {
      const overlap = [...task.writeScopes].sort().flatMap(left =>
        [...other.writeScopes].sort().flatMap(right => scopesOverlap(left, right) ? [[left, right] as const] : []),
      )[0]
      if (overlap !== undefined) {
        envelopeDiagnostics.push(
          `task write-scope overlap (${task.id}, ${other.id}): ${JSON.stringify(overlap[0])} overlaps ${JSON.stringify(overlap[1])}`,
        )
      }
    }
  }
  return envelopeDiagnostics
}

/** Canonical complete-envelope evaluation shared by preflight and dispatch enforcement. */
function readiness(current: TeamView, agent: Agent, ctx: Context, config: Required<Config>) {
  const approvalDiagnostic = approvalFailure(current)
  const durableCount = durableActiveTeammates(current)
  const memberDiagnostic = durableCount < config.minExecutionMembers
    ? `only ${durableCount} durable active teammate(s); ${config.minExecutionMembers} required`
    : undefined
  const envelopeDiagnostics = completeEnvelopeDiagnostics(current, agent, ctx, config)
  const mandatoryDiagnostics = [
    ...envelopeDiagnostics,
    ...(approvalDiagnostic === undefined ? [] : [approvalDiagnostic]),
  ]
  return {
    durableCount,
    mandatoryDiagnostics,
    diagnostics: [
      ...(approvalDiagnostic === undefined ? [] : [approvalDiagnostic]),
      ...(memberDiagnostic === undefined ? [] : [memberDiagnostic]),
      ...envelopeDiagnostics,
    ],
  }
}

/** Build fresh additive readiness metadata from canonical and live registries. */
function preflight(agent: Agent, ctx: Context, config: Required<Config>) {
  const current = guardedTeamView(ctx, agent)
  if (typeof current === 'string') throw new Error(current)
  const evaluation = readiness(current, agent, ctx, config)
  const { durableCount, diagnostics } = evaluation
  return {
    planRevision: current.planRevision,
    planPhase: current.planPhase,
    ...(current.planApproval === undefined ? {} : { approvedRevision: current.planApproval.approvedRevision }),
    durableActiveTeammates: durableCount,
    requiredActiveTeammates: config.minExecutionMembers,
    executionReady: diagnostics.length === 0,
    diagnostics,
  }
}

/**
 * One roster row, matching `TeamMemberView`. The Lead pseudo-row omits the
 * teammate-only provisioning fields, so only identity, role, status, and
 * diagnostics are required.
 */
const MEMBER_VIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'string', required: true },
    name: { type: 'string', required: true },
    role: { type: 'string', required: true, enum: ['lead', 'teammate'] },
    status: { type: 'string', required: true, enum: ['running', 'idle', 'inactive', 'provisioning', 'failed'] },
    description: { type: 'string' },
    provider: { type: 'string' },
    context: { type: 'string', enum: ['fresh', 'fork'] },
    model: { type: 'string' },
    diagnostics: { type: 'array', required: true, items: { type: 'string' } },
  },
} as const

/** One shared task, matching the public `TeamTaskView`. */
const TASK_VIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'string', required: true },
    revision: { type: 'integer', required: true },
    subject: { type: 'string', required: true },
    description: { type: 'string', required: true },
    status: { type: 'string', required: true, enum: ['pending', 'in_progress', 'completed', 'deleted'] },
    ownerName: { type: 'string' },
    blockedBy: { type: 'array', required: true, items: { type: 'string' } },
    writeScopes: { type: 'array', required: true, items: { type: 'string' } },
    ready: { type: 'boolean', required: true },
    writeScopeWarnings: { type: 'array', required: true, items: { type: 'string' } },
  },
} as const

const SPAWN_VALUE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    member: { ...MEMBER_VIEW_SCHEMA, required: true },
  },
} as const

const MEMBER_LIST_VALUE_SCHEMA = { type: 'array', items: MEMBER_VIEW_SCHEMA } as const

/** One committed member-work row, matching the complete `TeamWorkView`. */
const WORK_VIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    memberId: { type: 'string', required: true },
    state: { type: 'string', required: true, enum: ['working', 'blocked', 'review_required', 'done'] },
    summary: { type: 'string', required: true },
    reason: { type: 'string' },
    taskId: { type: 'string' },
    files: { type: 'array', required: true, items: { type: 'string' } },
    updatedAt: { type: 'integer', required: true },
  },
} as const

const SEND_VALUE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    messageId: { type: 'string', required: true },
    status: { type: 'string', required: true, enum: ['accepted', 'queued'] },
  },
} as const

/** `noProgress` is present only on the model-only shortcut that skips the wait. */
const WAIT_VALUE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    timedOut: { type: 'boolean', required: true },
    noProgress: {
      type: 'object',
      additionalProperties: false,
      properties: {
        reason: { type: 'string', required: true, const: 'no-active-peer' },
        message: { type: 'string', required: true },
      },
    },
  },
} as const

const INTERRUPT_VALUE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    previousStatus: { type: 'string', required: true, enum: ['running', 'idle', 'inactive'] },
  },
} as const

const TASK_LIST_VALUE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    tasks: { type: 'array', required: true, items: TASK_VIEW_SCHEMA },
    nextCursor: { type: 'integer' },
    preflight: {
      type: 'object',
      required: true,
      additionalProperties: false,
      properties: {
        planRevision: { type: 'integer', required: true },
        planPhase: { type: 'string', required: true, enum: ['draft', 'approved'] },
        approvedRevision: { type: 'integer' },
        durableActiveTeammates: { type: 'integer', required: true },
        requiredActiveTeammates: { type: 'integer', required: true },
        executionReady: { type: 'boolean', required: true },
        diagnostics: { type: 'array', required: true, items: { type: 'string' } },
      },
    },
  },
} as const

/**
 * Declare one canonical output schema with compact model-facing JSON. Every
 * Team result is a fixed record, so the declared schema is what makes the
 * compiler check `execute` against the value the model is promised.
 * @param schema - canonical value schema for one tool.
 * @returns the `output` declaration accepted by {@link defineTool}.
 */
function jsonOutput<const S extends ValueSchemaSpec>(schema: S): {
  schema: S
  render: (args: unknown, value: InferValue<S>) => [{ type: 'text'; text: string }]
} {
  return {
    schema,
    render: (_args: unknown, value: InferValue<S>) => [{ type: 'text', text: JSON.stringify(value) }],
  }
}

/** Recover the exact caller guaranteed by Agent-scoped tool discovery. */
function callingAgent(agent: Agent | undefined, toolName: string): Agent {
  /* v8 ignore next 2 -- Team tools are registered only in an exact Agent scope, so discovery supplies this carrier. */
  if (agent === undefined) throw new Error(`${toolName} requires a calling Agent`)
  return agent
}

/** Register the complete Team tool set in one exact Agent scope. */
function install(agent: Agent, ctx: Context, config: Required<Config>): () => void {
  const scoped = agent.ctx
  const disposers: Array<() => unknown> = []
  const register = (disposer: () => unknown): void => { disposers.push(disposer) }
  const externalRestrictedTools = new Set(config.externalRestrictedTools)
  try {
    register(scoped.tools.guard((exec) => {
      const current = guardedTeamView(ctx, agent)
      if (typeof current === 'string') return `Team execution denied: ${current}`
      const evaluation = readiness(current, agent, ctx, config)
      const active = evaluation.durableCount

      if (exec.name === 'spawn_teammate') {
        const failure = evaluation.mandatoryDiagnostics[0]
        if (failure !== undefined) return `Team spawn denied: ${failure}`
        if (active >= config.maxExecutionMembers) {
          return `Team spawn denied: durable teammate cap of ${config.maxExecutionMembers} reached; found ${active}`
        }
        return undefined
      }

      if (evaluation.diagnostics.length === 0) return undefined
      if (exec.name === 'team_task_update') {
        const args = exec.arguments
        const action = typeof args === 'object' && args !== null && 'action' in args
          ? (args as { action?: unknown }).action
          : undefined
        if (typeof action === 'string' && STRUCTURAL_TASK_ACTIONS.has(action)) return undefined
        return `Team task action ${JSON.stringify(action)} is unavailable while Team execution is restricted; use edit, set_dependencies, or delete`
      }
      const ownAdmission = restrictedOwnToolAdmission(exec.name, exec.arguments)
      if (ownAdmission === true || externalRestrictedTools.has(exec.name)) return undefined
      if (typeof ownAdmission === 'string') return ownAdmission
      const condition = evaluation.mandatoryDiagnostics[0]
        ?? `Team execution requires at least ${config.minExecutionMembers} durable active teammates; found ${active}`
      return `Team execution denied for tool "${exec.name}": ${condition}`
    }))

    register(scoped.systemPrompt.section({
      name: 'team:policy',
      order: scoped.systemPrompt.getSectionOrder('TEAM_POLICY'),
      text: () => {
        const membership = ctx.agentTeams.membership(agent)
        return `${POLICY}\n\nExecution requires at least ${config.minExecutionMembers} durable active teammates, and the durable teammate cap is ${config.maxExecutionMembers}.\n\nYour Team role is ${membership.role}; your Team name is ${membership.name}; Team id is ${membership.id}.`
      },
    }))

    register(scoped.tools.register(defineTool({
      name: 'spawn_teammate',
      description: 'Create one named, durable teammate. Only the Team Lead may call this tool.',
      parameters: {
        name: { type: 'string', required: true, description: 'Unique lower-kebab-case teammate name.' },
        description: { type: 'string', required: true, description: 'Short description of the delegated responsibility.' },
        prompt: { type: 'string', required: true, description: 'Complete initial task for the teammate.' },
        context: {
          type: 'string',
          enum: ['fresh', 'fork'],
          description: 'fresh starts without Lead history; fork inherits completed Lead turns. Defaults to fresh.',
        },
      },
      output: jsonOutput(SPAWN_VALUE_SCHEMA),
      async execute(args, exec) {
        const agent = callingAgent(exec.agent, 'spawn_teammate')
        const context = args.context ?? 'fresh'
        return await ctx.agentTeams.spawnTeammate(agent, {
          name: args.name,
          description: args.description,
          prompt: [{ type: 'text', text: args.prompt }],
          context,
          provider: context === 'fork' ? config.forkProvider : config.freshProvider,
          signal: exec.signal,
        })
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'report_team_status',
      description: 'Commit your current durable Team work state and return the complete authoritative work view.',
      parameters: {
        state: { type: 'string', required: true, enum: ['working', 'blocked', 'review_required', 'done'] },
        summary: { type: 'string', required: true },
        reason: { type: 'string' },
        task_id: { type: 'string' },
        files: { type: 'array', items: { type: 'string' } },
      },
      output: jsonOutput(WORK_VIEW_SCHEMA),
      async execute(args, exec) {
        const work = await ctx.agentTeams.reportWork(callingAgent(exec.agent, 'report_team_status'), {
          state: args.state,
          summary: args.summary,
          ...args.reason === undefined ? {} : { reason: args.reason },
          ...args.task_id === undefined ? {} : { taskId: TeamTaskId(args.task_id) },
          files: args.files ?? [],
        })
        return { ...work, files: [...work.files] }
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'send_message',
      description: 'Send one durable message to another Team member. A running target receives it at the nearest step boundary; an idle target starts a turn; an inactive teammate cold-resumes.',
      parameters: {
        target: { type: 'string', required: true, description: 'Team member name, or lead.' },
        message: { type: 'string', required: true, description: 'Self-contained message for the target.' },
      },
      output: jsonOutput(SEND_VALUE_SCHEMA),
      execute(args, exec) {
        return ctx.agentTeams.sendMessage(callingAgent(exec.agent, 'send_message'), {
          target: args.target,
          content: [{ type: 'text', text: args.message }],
          signal: exec.signal,
        })
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'list_agents',
      description: 'List the Lead and every durable teammate with current runtime status.',
      parameters: {},
      output: jsonOutput(MEMBER_LIST_VALUE_SCHEMA),
      async execute(_args, exec) {
        return Promise.resolve(ctx.agentTeams.listMembers(callingAgent(exec.agent, 'list_agents')))
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'wait_agent',
      description: 'Wait for the next teammate status, mailbox, or shared-task change after this call starts. This never wakes inactive members and returns noProgress immediately when no other member is running or provisioning. Re-list after wakeup or timeout instead of polling.',
      parameters: {
        timeout_ms: {
          type: 'integer',
          description: 'Wait duration in milliseconds, from 10000 through 3600000. Defaults to 30000.',
        },
      },
      output: jsonOutput(WAIT_VALUE_SCHEMA),
      async execute(args, exec) {
        const caller = callingAgent(exec.agent, 'wait_agent')
        const timeoutMs = args.timeout_ms ?? 30_000
        // Preserve TeamService's authoritative timeout validation before the
        // model-only no-progress shortcut.
        if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 10_000 || timeoutMs > 3_600_000) {
          return await ctx.agentTeams.waitForChange(caller, timeoutMs, exec.signal)
        }
        // The active-peer read and waiter registration must remain one synchronous
        // span; awaiting between them can lose the only peer-status edge.
        const hasActivePeer = ctx.agentTeams.listMembers(caller).some(member =>
          member.id !== caller.id && ACTIVE_WAIT_STATUSES.has(member.status))
        if (!hasActivePeer) {
          return {
            timedOut: false,
            noProgress: {
              reason: 'no-active-peer' as const,
              message: NO_ACTIVE_PEER_MESSAGE,
            },
          }
        }
        return await ctx.agentTeams.waitForChange(caller, timeoutMs, exec.signal)
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'interrupt_agent',
      description: 'Interrupt one teammate\'s current turn while preserving its pending inbox. Team Lead only.',
      parameters: {
        target: { type: 'string', required: true, description: 'Teammate name.' },
      },
      output: jsonOutput(INTERRUPT_VALUE_SCHEMA),
      async execute(args, exec) {
        return Promise.resolve(ctx.agentTeams.interrupt(
          callingAgent(exec.agent, 'interrupt_agent'),
          args.target,
        ))
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'team_task_create',
      description: 'Create one unowned pending task on the shared Team task board.',
      parameters: {
        subject: { type: 'string', required: true, description: 'Concise task title.' },
        description: { type: 'string', required: true, description: 'Complete task details and acceptance criteria.' },
        blocked_by: { type: 'array', items: { type: 'string' }, description: 'Task ids that must complete first.' },
        write_scopes: {
          type: 'array',
          items: { type: 'string' },
          description: 'Advisory workspace-relative file or directory prefixes this task expects to modify.',
        },
      },
      output: jsonOutput(TASK_VIEW_SCHEMA),
      async execute(args, exec) {
        return await ctx.agentTeams.createTask(callingAgent(exec.agent, 'team_task_create'), {
          subject: args.subject,
          description: args.description,
          ...args.blocked_by === undefined ? {} : { blockedBy: args.blocked_by.map(TeamTaskId) },
          ...args.write_scopes === undefined ? {} : { writeScopes: args.write_scopes },
        })
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'team_task_list',
      description: 'List shared tasks, including readiness, owner, revision, blockers, and write-scope warnings.',
      parameters: {
        status: {
          type: 'string',
          enum: ['pending', 'in_progress', 'completed'],
          description: 'Optional exact status filter.',
        },
        owner: { type: 'string', description: 'Optional member-name filter; use unowned for tasks without an owner.' },
        ready: { type: 'boolean', description: 'Optional readiness filter.' },
        cursor: { type: 'integer', description: 'Zero-based result offset. Defaults to 0.' },
        limit: { type: 'integer', description: 'Number of rows, 1 through 100. Defaults to 50.' },
      },
      output: jsonOutput(TASK_LIST_VALUE_SCHEMA),
      execute(args, exec) {
        const status = args.status
        const filtered = ctx.agentTeams.listTasks(callingAgent(exec.agent, 'team_task_list')).filter(task =>
          (status === undefined || task.status === status)
          && (args.owner === undefined || (args.owner === 'unowned' ? task.ownerName === undefined : task.ownerName === args.owner))
          && (args.ready === undefined || task.ready === args.ready))
        const cursor = args.cursor ?? 0
        const limit = args.limit ?? 50
        if (!Number.isSafeInteger(cursor) || cursor < 0) throw new Error('cursor must be a non-negative safe integer')
        if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('limit must be an integer from 1 through 100')
        return Promise.resolve({
          tasks: filtered.slice(cursor, cursor + limit),
          ...(cursor + limit < filtered.length ? { nextCursor: cursor + limit } : {}),
          preflight: preflight(callingAgent(exec.agent, 'team_task_list'), ctx, config),
        })
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'team_task_get',
      description: 'Read the complete latest value of one shared task before changing or executing it.',
      parameters: {
        task_id: { type: 'string', required: true, description: 'Shared task id.' },
      },
      output: jsonOutput(TASK_VIEW_SCHEMA),
      async execute(args, exec) {
        return Promise.resolve(ctx.agentTeams.getTask(
          callingAgent(exec.agent, 'team_task_get'),
          TeamTaskId(args.task_id),
        ))
      },
    })))

    register(scoped.tools.register(defineTool({
      name: 'team_task_update',
      description: 'Compare-and-set a shared task action using the latest revision from team_task_get or team_task_list.',
      parameters: {
        task_id: { type: 'string', required: true, description: 'Shared task id.' },
        expected_revision: { type: 'integer', required: true, description: 'Current task revision used as the CAS precondition.' },
        action: {
          type: 'string',
          required: true,
          enum: ['claim', 'release', 'edit', 'set_dependencies', 'complete', 'reopen', 'reassign', 'delete'],
          description: 'Task transition to apply.',
        },
        subject: { type: 'string', description: 'Replacement title for edit.' },
        description: { type: 'string', description: 'Replacement details for edit.' },
        blocked_by: { type: 'array', items: { type: 'string' }, description: 'Complete blocker list for set_dependencies.' },
        write_scopes: { type: 'array', items: { type: 'string' }, description: 'Replacement advisory write scopes for edit.' },
        owner: { type: 'string', description: 'Member name for Lead-only reassign; omit to unassign.' },
      },
      output: jsonOutput(TASK_VIEW_SCHEMA),
      async execute(args, exec) {
        return await ctx.agentTeams.updateTask(callingAgent(exec.agent, 'team_task_update'), {
          taskId: TeamTaskId(args.task_id),
          expectedRevision: args.expected_revision,
          action: args.action,
          ...args.subject === undefined ? {} : { subject: args.subject },
          ...args.description === undefined ? {} : { description: args.description },
          ...args.blocked_by === undefined ? {} : { blockedBy: args.blocked_by.map(TeamTaskId) },
          ...args.write_scopes === undefined ? {} : { writeScopes: args.write_scopes },
          ...args.owner === undefined ? {} : { owner: args.owner },
        })
      },
    })))
  } catch (error: unknown) {
    for (const dispose of disposers.reverse()) void dispose()
    throw error
  }
  return () => {
    for (const dispose of disposers.reverse()) void dispose()
  }
}

/** Install Team tools in every live or subsequently published Team member scope. */
export function apply(ctx: Context, config: Config = {}): void {
  const resolved: Required<Config> = {
    freshProvider: config.freshProvider ?? 'spawn',
    forkProvider: config.forkProvider ?? 'fork',
    minExecutionMembers: config.minExecutionMembers ?? 2,
    maxExecutionMembers: config.maxExecutionMembers ?? 4,
    externalRestrictedTools: [...new Set((config.externalRestrictedTools ?? []).map((tool, index) => {
      if (typeof tool !== 'string' || tool.length === 0) {
        throw new Error(`externalRestrictedTools[${index}] must be a non-empty string`)
      }
      return tool
    }))].sort(),
  }
  for (const key of ['minExecutionMembers', 'maxExecutionMembers'] as const) {
    if (!Number.isSafeInteger(resolved[key]) || resolved[key] < 1) {
      throw new TypeError(`${key} must be a positive safe integer`)
    }
  }
  if (resolved.maxExecutionMembers < resolved.minExecutionMembers) {
    throw new RangeError('maxExecutionMembers must be greater than or equal to minExecutionMembers')
  }
  ctx.effect(() => ctx.agentTeams.registerApprovalPreflight((agent, view) => (
    completeEnvelopeDiagnostics(view, agent, ctx, resolved)
  )), 'tool-team.approvalPreflight()')
  const installed = new Map<Agent, () => void>()
  const maybeInstall = (agent: Agent): void => {
    if (installed.has(agent) || ctx.agentTeams.tryMembership(agent) === undefined) return
    installed.set(agent, install(agent, ctx, resolved))
  }
  for (const agent of ctx.agents.list()) maybeInstall(agent)
  ctx.on('agent/created', ({ agent }) => { maybeInstall(agent) })
  ctx.on('agent/disposed', ({ agent }) => {
    installed.get(agent)?.()
    installed.delete(agent)
  })
  ctx.effect(() => () => {
    for (const dispose of installed.values()) dispose()
    installed.clear()
  }, 'tool-team.scopedTools()')
}
