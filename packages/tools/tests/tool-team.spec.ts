import { afterEach, describe, expect, it, vi } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { scopeOf } from '@deepseek-ai/dsh-scope'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SessionQueryEngine from '@deepseek-ai/dsh-session-query'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as SubagentFork from '@deepseek-ai/dsh-subagent-fork-in-process'
import * as SubagentSpawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { renderPrompt } from '@deepseek-ai/dsh-system-prompt'
import * as ToolSubagentControl from '@deepseek-ai/dsh-tool-subagent-control'
import { defineContentToolFixture } from '@deepseek-ai/dsh-tools'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../../gat-core/src/index.ts'
import * as toolTeam from '../src/index.ts'

const SIGNAL = new AbortController().signal
const TOOL_NAMES = [
  'spawn_teammate',
  'send_message',
  'list_agents',
  'wait_agent',
  'interrupt_agent',
  'team_task_create',
  'team_task_list',
  'team_task_get',
  'team_task_update',
  'report_team_status',
].sort()

const roots: string[] = []
let callNumber = 0

/** Session query implementation whose search faces are outside these tests. */
class TestSessionQuery extends SessionQueryEngine {
  override searchSessions(): Promise<never> {
    return Promise.reject(new Error('session search is not configured in this test'))
  }

  override searchEvents(): Promise<never> {
    return Promise.reject(new Error('event search is not configured in this test'))
  }
}

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

async function setup(
  script: ConstructorParameters<typeof MockAdapter>[0],
  legacyControl = false,
  config: toolTeam.Config = {},
) {
  const ctx = new Context()
  await mountAgentLoopTestDependencies(ctx)
  const storageRoot = mkdtempSync(join(tmpdir(), 'dsh-tool-team-'))
  roots.push(storageRoot)
  await ctx.plugin(JsonlSessionPersistence, { root: storageRoot })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(SubagentService)
  if (legacyControl) await ctx.plugin(ToolSubagentControl)
  await ctx.plugin(SubagentSpawn, { providerName: 'spawn' })
  await ctx.plugin(SubagentFork, { providerName: 'fork' })
  await ctx.plugin(TeamService)
  const fiber = await ctx.plugin(toolTeam, config)
  const adapter = new MockAdapter(script)
  ctx.llm.registerAdapter(['mock'], adapter)
  const lead = await ctx.agentLoop.create(SessionId('tool-team-lead'), { provider: 'mock', model: 'mock' })
  return { ctx, lead, fiber }
}

async function approveCurrentPlan(ctx: Context, lead: Agent): Promise<void> {
  if (ctx.agentTeams.listTasks(lead).length === 0) {
    await ctx.agentTeams.createTask(lead, { subject: 'approved work', description: 'approved execution plan' })
  }
  const revision = ctx.agentTeams.remoteView(lead).planRevision
  await ctx.agentTeams.approvePlan(lead, { approvedRevision: revision })
}

function registerDanger(ctx: Context, calls: { count: number }): void {
  ctx.tools.register(defineContentToolFixture({
    name: 'danger_write',
    description: 'test-only non-allowlisted write capability',
    parameters: {},
    async execute() {
      calls.count += 1
      return [{ type: 'text', text: 'wrote' }]
    },
  }))
}

function spawnRequest(index: number) {
  return {
    name: `guard-worker-${index}`,
    description: `guard worker ${index}`,
    prompt: 'stay active',
  }
}

function execute(
  ctx: Context,
  agent: Agent | undefined,
  name: string,
  args: unknown,
  signal: AbortSignal = SIGNAL,
) {
  return ctx.tools.execute({
    callId: ToolCallId(`team-call-${++callNumber}`),
    name,
    arguments: args,
    signal,
    ...agent === undefined ? {} : { agent },
  })
}

function text(result: Awaited<ReturnType<typeof execute>>): string {
  return result.content.flatMap(block => block.type === 'text' ? [block.text] : []).join('')
}

function spawnedChildId(result: Awaited<ReturnType<typeof execute>>): SessionId {
  const parsed: unknown = JSON.parse(text(result))
  if (typeof parsed !== 'object' || parsed === null || !('member' in parsed)) {
    throw new Error('spawn_teammate result has no member')
  }
  const member = parsed.member
  if (typeof member !== 'object' || member === null || !('id' in member) || typeof member.id !== 'string') {
    throw new Error('spawn_teammate result has no member id')
  }
  return SessionId(member.id)
}

async function assembly(ctx: Context, agent: Agent) {
  const scope = scopeOf(agent.ctx)
  if (scope === undefined) throw new Error('expected Agent scope')
  return ctx.systemPrompt.assemble({ scope })
}

async function waitRunning(ctx: Context, id: SessionId): Promise<Agent> {
  return vi.waitFor(() => {
    const child = ctx.agents.get(id)
    expect(child?.status).toBe('running')
    return child!
  }, { timeout: 5_000 })
}

async function waitNoAgent(ctx: Context, id: SessionId): Promise<void> {
  await vi.waitFor(() => { expect(ctx.agents.get(id)).toBeUndefined() }, { timeout: 5_000 })
}

describe('dsh-tool-team', () => {
  it('reports the exact durable Team work view and preserves domain rejections', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'])
    const schema = (await assembly(ctx, lead)).tools.find(tool => tool.name === 'report_team_status')
    expect(schema?.parameters).toEqual({
      type: 'object',
      properties: {
        state: { type: 'string', enum: ['working', 'blocked', 'review_required', 'done'] },
        summary: { type: 'string' },
        reason: { type: 'string' },
        task_id: { type: 'string' },
        files: { type: 'array', items: { type: 'string' } },
      },
      required: ['state', 'summary'],
    })
    expect(ctx.tools.get('report_team_status', lead)?.output.schema).toMatchObject({
      type: 'object',
      additionalProperties: false,
      properties: {
        memberId: { type: 'string' },
        state: { type: 'string' },
        summary: { type: 'string' },
        reason: { type: 'string' },
        taskId: { type: 'string' },
        files: { type: 'array' },
        updatedAt: { type: 'integer' },
      },
      required: ['memberId', 'state', 'summary', 'files', 'updatedAt'],
    })

    await approveCurrentPlan(ctx, lead)
    const childIds: SessionId[] = []
    for (const index of [0, 1]) {
      const spawned = await execute(ctx, lead, 'spawn_teammate', spawnRequest(index))
      const childId = spawnedChildId(spawned)
      childIds.push(childId)
      await waitRunning(ctx, childId)
    }

    const reported = await execute(ctx, lead, 'report_team_status', {
      state: 'working',
      summary: 'Implementing the guarded tool surface',
      files: ['packages/experimental/gat-tools/src/index.ts'],
    })
    expect(reported.isError).toBe(false)
    const value = JSON.parse(text(reported)) as Record<string, unknown>
    expect(Object.keys(value).sort()).toEqual([
      'files', 'memberId', 'state', 'summary', 'updatedAt',
    ])
    expect(value).toMatchObject({
      memberId: lead.id,
      state: 'working',
      summary: 'Implementing the guarded tool surface',
      files: ['packages/experimental/gat-tools/src/index.ts'],
    })
    expect(typeof value.updatedAt).toBe('number')

    const rejected = await execute(ctx, lead, 'report_team_status', {
      state: 'blocked', summary: 'Cannot continue',
    })
    expect(rejected.isError).toBe(true)
    expect(text(rejected)).toContain('blocked work requires a non-empty reason')
    for (const [index, childId] of childIds.entries()) {
      await execute(ctx, lead, 'interrupt_agent', { target: `guard-worker-${index}` })
      await waitNoAgent(ctx, childId)
    }
  })

  it('allows only blocked and review-required status reports while restricted', async () => {
    const { ctx, lead } = await setup([])
    const initialEventCount = lead.session.snapshotEvents().filter(event => event.type === 'team/work').length

    const blocked = await execute(ctx, lead, 'report_team_status', {
      state: 'blocked', summary: 'Waiting for approval', reason: 'The Team plan is not approved',
    })
    expect(blocked.isError).toBe(false)
    expect(JSON.parse(text(blocked))).toMatchObject({ state: 'blocked', reason: 'The Team plan is not approved' })
    const reviewRequired = await execute(ctx, lead, 'report_team_status', {
      state: 'review_required', summary: 'Review the proposed change', files: ['src/review.ts'],
    })
    expect(reviewRequired.isError).toBe(false)
    expect(JSON.parse(text(reviewRequired))).toMatchObject({ state: 'review_required', files: ['src/review.ts'] })

    const beforeDenied = ctx.agentTeams.remoteView(lead).work
    const eventCountBeforeDenied = lead.session.snapshotEvents().filter(event => event.type === 'team/work').length
    expect(eventCountBeforeDenied).toBe(initialEventCount + 2)
    for (const args of [
      { state: 'working', summary: 'Must not commit working' },
      { state: 'done', summary: 'Must not commit done' },
      { summary: 'Missing state' },
      { state: 42, summary: 'Non-string state' },
      { state: 'unknown', summary: 'Unknown state' },
    ]) {
      const denied = await execute(ctx, lead, 'report_team_status', args)
      expect(denied.isError).toBe(true)
      expect(text(denied)).toContain('Team status reporting is restricted to blocked or review_required')
      expect(ctx.agentTeams.remoteView(lead).work).toEqual(beforeDenied)
      expect(lead.session.snapshotEvents().filter(event => event.type === 'team/work')).toHaveLength(eventCountBeforeDenied)
    }
  })

  it('denies interrupt while restricted and restores ordinary status and interrupt when ready', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'])
    await approveCurrentPlan(ctx, lead)
    const childIds: SessionId[] = []
    for (const index of [0, 1]) {
      const spawned = await execute(ctx, lead, 'spawn_teammate', spawnRequest(index))
      const childId = spawnedChildId(spawned)
      childIds.push(childId)
      await waitRunning(ctx, childId)
    }
    await execute(ctx, lead, 'team_task_create', {
      subject: 'Invalidate approval', description: 'Exercise restricted dispatch after a structural edit',
    })

    const denied = await execute(ctx, lead, 'interrupt_agent', { target: 'guard-worker-0' })
    expect(denied.isError).toBe(true)
    expect(text(denied)).toContain('Team execution denied for tool "interrupt_agent"')
    expect(ctx.agents.get(childIds[0]!)).toBeDefined()

    await approveCurrentPlan(ctx, lead)
    for (const state of ['working', 'done'] as const) {
      const reported = await execute(ctx, lead, 'report_team_status', {
        state, summary: `${state} after full readiness`,
      })
      expect(reported.isError).toBe(false)
      expect(JSON.parse(text(reported))).toMatchObject({ state })
    }
    const interrupted = await execute(ctx, lead, 'interrupt_agent', { target: 'guard-worker-0' })
    expect(interrupted.isError).toBe(false)
    await waitNoAgent(ctx, childIds[0]!)
    await execute(ctx, lead, 'interrupt_agent', { target: 'guard-worker-1' })
    await waitNoAgent(ctx, childIds[1]!)
  })

  it('denies spawn before approval, allows it below four, and denies it at four', async () => {
    const { ctx, lead } = await setup(['hang', 'hang', 'hang', 'hang'])
    const request = (index: number) => ({
      name: `guard-worker-${index}`,
      description: `guard worker ${index}`,
      prompt: 'stay active',
    })
    const beforeApproval = await execute(ctx, lead, 'spawn_teammate', request(0))
    expect(beforeApproval.isError).toBe(true)
    expect(text(beforeApproval)).toMatch(/current Team plan revision \d+ is not HUMAN-approved/u)

    await approveCurrentPlan(ctx, lead)
    for (let index = 0; index < 4; index += 1) {
      const spawned = await execute(ctx, lead, 'spawn_teammate', request(index))
      expect(spawned.isError).toBe(false)
      await waitRunning(ctx, spawnedChildId(spawned))
    }
    const capped = await execute(ctx, lead, 'spawn_teammate', request(4))
    expect(capped.isError).toBe(true)
    expect(text(capped)).toContain('durable teammate cap of 4')
  })

  it('uses configured minimum readiness and durable teammate cap', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'], false, {
      minExecutionMembers: 1,
      maxExecutionMembers: 2,
    })
    registerDanger(ctx, { count: 0 })
    await approveCurrentPlan(ctx, lead)

    const restricted = await execute(ctx, lead, 'danger_write', {})
    expect(restricted.isError).toBe(true)
    expect(text(restricted)).toContain('requires at least 1 durable active teammates; found 0')
    const first = await execute(ctx, lead, 'spawn_teammate', spawnRequest(0))
    expect(first.isError).toBe(false)
    await waitRunning(ctx, spawnedChildId(first))
    expect((await execute(ctx, lead, 'danger_write', {})).isError).toBe(false)

    const ready = JSON.parse(text(await execute(ctx, lead, 'team_task_list', {}))) as {
      preflight: { requiredActiveTeammates: number; executionReady: boolean }
    }
    expect(ready.preflight).toMatchObject({ requiredActiveTeammates: 1, executionReady: true })
    const second = await execute(ctx, lead, 'spawn_teammate', spawnRequest(1))
    expect(second.isError).toBe(false)
    await waitRunning(ctx, spawnedChildId(second))
    const capped = await execute(ctx, lead, 'spawn_teammate', spawnRequest(2))
    expect(capped.isError).toBe(true)
    expect(text(capped)).toContain('durable teammate cap of 2')
  })

  it('denies direct and nested non-allowlisted calls until approval and two durable teammates', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'], false, {
      externalRestrictedTools: ['composite_dispatch'],
    })
    const calls = { count: 0 }
    registerDanger(ctx, calls)
    ctx.tools.register(defineContentToolFixture({
      name: 'composite_dispatch',
      description: 'test-only nested dispatcher',
      parameters: {},
      async execute(_args, exec) {
        const nested = await ctx.tools.execute({
          callId: ToolCallId(`nested-${++callNumber}`),
          rootCallId: exec.callId,
          parent: exec.token,
          name: 'danger_write',
          arguments: {},
          ...(exec.agent === undefined ? {} : { agent: exec.agent }),
          signal: exec.signal,
        })
        return nested.content
      },
    }))

    const directDraft = await execute(ctx, lead, 'danger_write', {})
    expect(directDraft.isError).toBe(true)
    expect(text(directDraft)).toMatch(/current Team plan revision \d+ is not HUMAN-approved/u)
    const nestedDraft = await execute(ctx, lead, 'composite_dispatch', {})
    expect(nestedDraft.isError).toBe(false)
    expect(text(nestedDraft)).toContain('Team execution denied for tool "danger_write"')
    expect(calls.count).toBe(0)

    await approveCurrentPlan(ctx, lead)
    const stillShort = await execute(ctx, lead, 'danger_write', {})
    expect(stillShort.isError).toBe(true)
    expect(text(stillShort)).toContain('requires at least 2 durable active teammates; found 0')

    const readyIds: SessionId[] = []
    for (const index of [1, 2]) {
      const spawned = await execute(ctx, lead, 'spawn_teammate', {
        name: `ready-worker-${index}`, description: 'readiness worker', prompt: 'stay active',
      })
      const childId = spawnedChildId(spawned)
      readyIds.push(childId)
      await waitRunning(ctx, childId)
    }
    expect((await execute(ctx, lead, 'danger_write', {})).isError).toBe(false)
    expect((await execute(ctx, lead, 'composite_dispatch', {})).isError).toBe(false)
    await execute(ctx, lead, 'interrupt_agent', { target: 'ready-worker-1' })
    await waitNoAgent(ctx, readyIds[0]!)
    expect((await execute(ctx, lead, 'danger_write', {})).isError).toBe(false)
    expect(calls.count).toBe(3)
  })

  it('preserves ordinary downstream permission denial after Team execution opens', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'])
    const calls = { count: 0 }
    registerDanger(ctx, calls)
    let ordinaryGuardCalls = 0
    lead.ctx.tools.guard((exec) => {
      if (exec.name !== 'danger_write') return undefined
      ordinaryGuardCalls += 1
      return 'ordinary permission denied'
    })

    await approveCurrentPlan(ctx, lead)
    for (const index of [1, 2]) {
      const spawned = await execute(ctx, lead, 'spawn_teammate', {
        name: `permission-worker-${index}`,
        description: 'permission-chain worker',
        prompt: 'stay active',
      })
      await waitRunning(ctx, spawnedChildId(spawned))
    }

    const denied = await execute(ctx, lead, 'danger_write', {})
    expect(denied.isError).toBe(true)
    expect(text(denied)).toContain('ordinary permission denied')
    expect(ordinaryGuardCalls).toBe(1)
    expect(calls.count).toBe(0)
  })

  it('allows only structural task updates while restricted and re-closes after mutation', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'])
    const calls = { count: 0 }
    registerDanger(ctx, calls)
    const created = await execute(ctx, lead, 'team_task_create', {
      subject: 'guarded task', description: 'exercise update discrimination',
    })
    const task = JSON.parse(text(created)) as { id: string; revision: number }
    for (const action of ['claim', 'release', 'complete', 'reopen', 'reassign']) {
      const denied = await execute(ctx, lead, 'team_task_update', {
        task_id: task.id, expected_revision: task.revision, action,
      })
      expect(denied.isError).toBe(true)
      expect(text(denied)).toContain(`task action "${action}" is unavailable while Team execution is restricted`)
    }
    const editResult = await execute(ctx, lead, 'team_task_update', {
      task_id: task.id, expected_revision: task.revision, action: 'edit', subject: 'edited task',
    })
    expect(editResult.isError).toBe(false)
    const edit = JSON.parse(text(editResult)) as { revision: number }
    const dependencies = await execute(ctx, lead, 'team_task_update', {
      task_id: task.id, expected_revision: edit.revision, action: 'set_dependencies', blocked_by: [],
    })
    expect(dependencies.isError).toBe(false)
    const dependency = JSON.parse(text(dependencies)) as { revision: number }
    const deleted = await execute(ctx, lead, 'team_task_update', {
      task_id: task.id, expected_revision: dependency.revision, action: 'delete',
    })
    expect(deleted.isError).toBe(false)
    await execute(ctx, lead, 'team_task_create', {
      subject: 'approved replacement work', description: 'keep the governed plan non-empty',
    })

    await approveCurrentPlan(ctx, lead)
    for (const index of [1, 2]) {
      const spawned = await execute(ctx, lead, 'spawn_teammate', {
        name: `stale-worker-${index}`, description: 'stale approval worker', prompt: 'stay active',
      })
      await waitRunning(ctx, spawnedChildId(spawned))
    }
    expect((await execute(ctx, lead, 'danger_write', {})).isError).toBe(false)
    const structural = await execute(ctx, lead, 'team_task_create', {
      subject: 'new structural work', description: 'invalidate approval',
    })
    expect(structural.isError).toBe(false)
    const stale = await execute(ctx, lead, 'danger_write', {})
    expect(stale.isError).toBe(true)
    expect(text(stale)).toContain('approved revision')
    expect(text(stale)).toContain('is stale for current revision')
    expect(calls.count).toBe(1)
  })

  it('rejects approval until the complete provider, tool, and pending-WBS envelope is valid', async () => {
    const { ctx, lead } = await setup([], false, {
      forkProvider: 'approval-fork',
      externalRestrictedTools: ['approval_read'],
    })
    const first = await ctx.agentTeams.createTask(lead, {
      subject: 'first pending task', description: 'first pending task', writeScopes: ['src/shared'],
    })
    const second = await ctx.agentTeams.createTask(lead, {
      subject: 'second pending task', description: 'second pending task', writeScopes: ['src/shared/file.ts'],
    })
    const revision = ctx.agentTeams.remoteView(lead).planRevision

    await expect(ctx.agentTeams.remoteApprovePlan(lead, { approvedRevision: revision })).resolves.toEqual({
      ok: false,
      error: {
        code: 'team-preflight-rejected',
        message: 'Team plan preflight failed: spawn provider "approval-fork" is unavailable; configured restricted tool "approval_read" is unavailable; task write-scope overlap (task-1, task-2): "src/shared" overlaps "src/shared/file.ts"',
      },
    })
    expect(ctx.agentTeams.remoteView(lead).planApproval).toBeUndefined()

    await ctx.plugin(SubagentFork, { providerName: 'approval-fork' })
    ctx.tools.register(defineContentToolFixture({
      name: 'approval_read',
      description: 'test-only approval capability',
      parameters: {},
      async execute() { return [{ type: 'text', text: 'available' }] },
    }))
    const overlapApproval = await ctx.agentTeams.remoteApprovePlan(lead, { approvedRevision: revision })
    expect(overlapApproval.ok).toBe(false)
    if (overlapApproval.ok) throw new Error('overlapping Team plan unexpectedly approved')
    expect(overlapApproval.error.code).toBe('team-preflight-rejected')
    expect(overlapApproval.error.message).toContain('task write-scope overlap (task-1, task-2)')

    const separated = await ctx.agentTeams.updateTask(lead, {
      taskId: second.id,
      expectedRevision: second.revision,
      action: 'edit',
      writeScopes: ['tests/second.ts'],
    })
    const nonOverlapRevision = ctx.agentTeams.remoteView(lead).planRevision
    await expect(ctx.agentTeams.remoteApprovePlan(lead, { approvedRevision: nonOverlapRevision })).resolves.toEqual({
      ok: true,
      value: { approvedRevision: nonOverlapRevision },
    })

    await ctx.agentTeams.updateTask(lead, {
      taskId: second.id,
      expectedRevision: separated.revision,
      action: 'edit',
      writeScopes: ['src/shared/file.ts'],
    })
    const overlappingRevision = ctx.agentTeams.remoteView(lead).planRevision
    await expect(ctx.agentTeams.remoteApprovePlan(lead, { approvedRevision: overlappingRevision })).resolves.toMatchObject({
      ok: false,
      error: { code: 'team-preflight-rejected' },
    })

    const overlapping = ctx.agentTeams.getTask(lead, second.id)
    await ctx.agentTeams.updateTask(lead, {
      taskId: second.id,
      expectedRevision: overlapping.revision,
      action: 'delete',
    })
    const deletedExcludedRevision = ctx.agentTeams.remoteView(lead).planRevision
    await expect(ctx.agentTeams.remoteApprovePlan(lead, { approvedRevision: deletedExcludedRevision })).resolves.toEqual({
      ok: true,
      value: { approvedRevision: deletedExcludedRevision },
    })
    expect(first.id).not.toBe(second.id)
  })

  it('fails closed for complete-envelope diagnostics and opens only after re-approval', async () => {
    const externalRestrictedTools = ['composite_dispatch', 'repo_read', 'missing_tool', 'missing_tool']
    const { ctx, lead } = await setup(['hang', 'hang', 'hang', 'hang'], false, {
      forkProvider: 'missing-fork',
      externalRestrictedTools,
    })
    externalRestrictedTools.push('mutated-after-apply')
    const calls = { count: 0 }
    registerDanger(ctx, calls)
    ctx.tools.register(defineContentToolFixture({
      name: 'repo_read',
      description: 'test-only repository reader',
      parameters: {},
      async execute() { return [{ type: 'text', text: 'read' }] },
    }))
    ctx.tools.register(defineContentToolFixture({
      name: 'composite_dispatch',
      description: 'test-only nested dispatcher',
      parameters: {},
      async execute(_args, exec) {
        const nested = await ctx.tools.execute({
          callId: ToolCallId(`nested-${++callNumber}`),
          rootCallId: exec.callId,
          parent: exec.token,
          name: 'danger_write',
          arguments: {},
          ...(exec.agent === undefined ? {} : { agent: exec.agent }),
          signal: exec.signal,
        })
        return nested.content
      },
    }))
    const first = await ctx.agentTeams.createTask(lead, {
      subject: 'first', description: 'first', writeScopes: ['src/shared.ts'],
    })
    const second = await ctx.agentTeams.createTask(lead, {
      subject: 'second', description: 'second', writeScopes: ['src/second.ts'],
    })
    for (const index of [0, 1]) {
      const spawned = await ctx.agentTeams.spawnTeammate(lead, {
        ...spawnRequest(index),
        prompt: [{ type: 'text', text: 'stay active' }],
        context: 'fresh',
        provider: 'spawn',
        signal: SIGNAL,
      })
      await waitRunning(ctx, spawned.member.id)
    }
    await ctx.agentTeams.updateTask(lead, {
      taskId: first.id,
      expectedRevision: first.revision,
      action: 'claim',
    })
    const initial = JSON.parse(text(await execute(ctx, lead, 'team_task_list', {}))) as {
      preflight: {
        planRevision: number
        planPhase: string
        approvedRevision?: number
        durableActiveTeammates: number
        requiredActiveTeammates: number
        executionReady: boolean
        diagnostics: string[]
      }
    }
    expect(initial.preflight).toMatchObject({
      planPhase: 'draft',
      durableActiveTeammates: 2,
      requiredActiveTeammates: 2,
      executionReady: false,
    })
    expect(initial.preflight.diagnostics).toEqual(expect.arrayContaining([
      'spawn provider "missing-fork" is unavailable',
      'configured restricted tool "missing_tool" is unavailable',
    ]))
    expect(initial.preflight.diagnostics.filter(value => value.includes('missing_tool'))).toHaveLength(1)
    expect(initial.preflight.diagnostics.some(value => value.includes('mutated-after-apply'))).toBe(false)
    expect(initial.preflight.diagnostics.some(value => value.includes('write-scope overlap'))).toBe(false)

    const assertDispatchDenied = async (diagnostic: string): Promise<void> => {
      const direct = await execute(ctx, lead, 'danger_write', {})
      expect(direct.isError).toBe(true)
      expect(text(direct)).toContain(diagnostic)
      const nested = await execute(ctx, lead, 'composite_dispatch', {})
      expect(nested.isError).toBe(false)
      expect(text(nested)).toContain('Team execution denied for tool "danger_write"')
      expect(text(nested)).toContain(diagnostic)
      expect(calls.count).toBe(0)
    }

    const missingProvider = await ctx.plugin(SubagentFork, { providerName: 'missing-fork' })
    await assertDispatchDenied('configured restricted tool "missing_tool" is unavailable')
    const spawnWithMissingTool = await execute(ctx, lead, 'spawn_teammate', spawnRequest(2))
    expect(spawnWithMissingTool.isError).toBe(true)
    expect(text(spawnWithMissingTool)).toContain('configured restricted tool "missing_tool" is unavailable')

    await missingProvider.dispose()
    ctx.tools.register(defineContentToolFixture({
      name: 'missing_tool',
      description: 'test-only late tool',
      parameters: {},
      async execute() { return [{ type: 'text', text: 'available' }] },
    }))
    await assertDispatchDenied('spawn provider "missing-fork" is unavailable')
    const spawnWithMissingProvider = await execute(ctx, lead, 'spawn_teammate', spawnRequest(2))
    expect(spawnWithMissingProvider.isError).toBe(true)
    expect(text(spawnWithMissingProvider)).toContain('spawn provider "missing-fork" is unavailable')

    await ctx.plugin(SubagentFork, { providerName: 'missing-fork' })
    const overlap = await ctx.agentTeams.updateTask(lead, {
      taskId: second.id,
      expectedRevision: second.revision,
      action: 'edit',
      writeScopes: ['src/shared.ts'],
    })
    await expect(ctx.agentTeams.remoteApprovePlan(lead, {
      approvedRevision: ctx.agentTeams.remoteView(lead).planRevision,
    })).resolves.toMatchObject({ ok: false, error: { code: 'team-preflight-rejected' } })
    await assertDispatchDenied('task write-scope overlap')
    const spawnWithOverlap = await execute(ctx, lead, 'spawn_teammate', spawnRequest(2))
    expect(spawnWithOverlap.isError).toBe(true)
    expect(text(spawnWithOverlap)).toContain('task write-scope overlap')

    await ctx.agentTeams.updateTask(lead, {
      taskId: second.id,
      expectedRevision: overlap.revision,
      action: 'edit',
      writeScopes: ['src/second.ts'],
    })
    const stale = JSON.parse(text(await execute(ctx, lead, 'team_task_list', {}))) as {
      preflight: { executionReady: boolean; diagnostics: string[] }
    }
    expect(stale.preflight.executionReady).toBe(false)
    expect(stale.preflight.diagnostics.some(value => value.includes('is not HUMAN-approved'))).toBe(true)
    await assertDispatchDenied('is not HUMAN-approved')
    await approveCurrentPlan(ctx, lead)

    const resolved = JSON.parse(text(await execute(ctx, lead, 'team_task_list', {}))) as {
      preflight: { executionReady: boolean; diagnostics: string[] }
    }
    expect(resolved.preflight).toEqual(expect.objectContaining({ executionReady: true, diagnostics: [] }))
    expect((await execute(ctx, lead, 'danger_write', {})).isError).toBe(false)
    expect((await execute(ctx, lead, 'composite_dispatch', {})).isError).toBe(false)
    expect(calls.count).toBe(2)
    expect(first.id).not.toBe(second.id)
  })

  it('allows spawn for the minimum-member diagnostic alone', async () => {
    const { ctx, lead } = await setup(['hang'])
    await approveCurrentPlan(ctx, lead)
    const before = JSON.parse(text(await execute(ctx, lead, 'team_task_list', {}))) as {
      preflight: { executionReady: boolean; diagnostics: string[] }
    }
    expect(before.preflight).toEqual(expect.objectContaining({
      executionReady: false,
      diagnostics: ['only 0 durable active teammate(s); 2 required'],
    }))
    const spawned = await execute(ctx, lead, 'spawn_teammate', spawnRequest(0))
    expect(spawned.isError).toBe(false)
  })

  it('fails closed with a deterministic projection diagnostic', async () => {
    const { ctx, lead } = await setup([])
    registerDanger(ctx, { count: 0 })
    vi.spyOn(ctx.agentTeams, 'remoteView').mockImplementationOnce(() => {
      throw new Error('projection unavailable')
    })

    const result = await execute(ctx, lead, 'danger_write', {})
    expect(result.isError).toBe(true)
    expect(text(result)).toContain('canonical Team projection is unavailable')
    expect(text(result)).not.toContain('projection unavailable')
  })

  it('installs the complete scoped schema and shared-checkout policy for roots and teammates', async () => {
    const { ctx, lead } = await setup(['hang'])
    await approveCurrentPlan(ctx, lead)
    const leadAssembly = await assembly(ctx, lead)
    expect(leadAssembly.tools.map(schema => schema.name).filter(name => TOOL_NAMES.includes(name)).sort())
      .toEqual(TOOL_NAMES)
    const leadPrompt = renderPrompt(leadAssembly)
    expect(leadPrompt).toContain('create teammates only when the user explicitly asks')
    expect(leadPrompt).toContain('FS_STALE_VERSION')
    expect(leadPrompt).toContain('Bash, formatters, code generators, and scripts are not fully protected')
    expect(leadPrompt).toContain('Task readiness never starts an owner')
    expect(leadPrompt).toContain('returns noProgress immediately')
    expect(leadPrompt).toContain('Your Team role is lead')

    const spawned = await execute(ctx, lead, 'spawn_teammate', {
      name: 'tool-worker',
      description: 'exercise scoped tools',
      prompt: 'stay available',
    })
    expect(spawned.isError).toBe(false)
    const childId = spawnedChildId(spawned)
    const child = await waitRunning(ctx, childId)
    const childAssembly = await assembly(ctx, child)
    expect(childAssembly.tools.map(schema => schema.name).filter(name => TOOL_NAMES.includes(name)).sort())
      .toEqual(TOOL_NAMES)
    expect(renderPrompt(childAssembly)).toContain('Your Team role is teammate; your Team name is tool-worker')
    const initialPrompt = child.session.snapshotEvents().find(event => event.type === 'user/message'
      && event.data.source.kind === 'user')
    expect(initialPrompt?.type === 'user/message'
      ? initialPrompt.data.content.flatMap(block => block.type === 'text' ? [block.text] : [])
      : []).toEqual(['stay available'])

    const denied = await execute(ctx, child, 'spawn_teammate', {
      name: 'nested', description: 'not allowed', prompt: 'no',
    })
    expect(denied.isError).toBe(true)
    expect(text(denied)).toContain('only the Team Lead')
    ctx.agentTeams.interrupt(lead, 'tool-worker')
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })
  })

  it('returns actionable no-progress output and renders structured wait cancellation', async () => {
    const inactiveSetup = await setup([textResponse('worker done')])
    await approveCurrentPlan(inactiveSetup.ctx, inactiveSetup.lead)
    const inactiveSpawn = await execute(inactiveSetup.ctx, inactiveSetup.lead, 'spawn_teammate', {
      name: 'inactive-worker', description: 'finish immediately', prompt: 'finish',
    })
    const inactiveId = spawnedChildId(inactiveSpawn)
    await waitNoAgent(inactiveSetup.ctx, inactiveId)
    const noProgress = await execute(inactiveSetup.ctx, inactiveSetup.lead, 'wait_agent', { timeout_ms: 3_600_000 })
    expect(noProgress.isError).toBe(false)
    expect(JSON.parse(text(noProgress))).toEqual({
      timedOut: false,
      noProgress: {
        reason: 'no-active-peer',
        message: 'No other Team member is running or provisioning. wait_agent cannot make progress or wake inactive teammates. Re-list with list_agents and team_task_list, then use send_message to wake each required inactive teammate before waiting again.',
      },
    })
    for (const timeout_ms of [9_999, 3_600_001, Number.MAX_SAFE_INTEGER + 1]) {
      const invalid = await execute(inactiveSetup.ctx, inactiveSetup.lead, 'wait_agent', { timeout_ms })
      expect(invalid.isError).toBe(true)
      expect(text(invalid)).toContain('timeoutMs must be an integer from 10000 through 3600000')
    }

    const activeSetup = await setup(['hang'])
    await approveCurrentPlan(activeSetup.ctx, activeSetup.lead)
    const activeSpawn = await execute(activeSetup.ctx, activeSetup.lead, 'spawn_teammate', {
      name: 'active-worker', description: 'stay active', prompt: 'wait',
    })
    const activeId = spawnedChildId(activeSpawn)
    await waitRunning(activeSetup.ctx, activeId)
    const controller = new AbortController()
    const waiting = execute(activeSetup.ctx, activeSetup.lead, 'wait_agent', { timeout_ms: 10_000 }, controller.signal)
    await new Promise(resolve => setTimeout(resolve, 0))
    controller.abort({ kind: 'user' })
    const aborted = await waiting
    expect(aborted.isError).toBe(true)
    expect(text(aborted)).toBe("Error: wait_agent aborted: { kind: 'user' }")
    activeSetup.ctx.agentTeams.interrupt(activeSetup.lead, 'active-worker')
    await waitNoAgent(activeSetup.ctx, activeId)
  })

  it('adapts roster, mailbox, wait, and task CAS operations to canonical JSON', async () => {
    const { ctx, lead } = await setup(['hang', 'hang', textResponse('lead received wakeup')])
    const created = await execute(ctx, lead, 'team_task_create', {
      subject: 'tool task',
      description: 'created through tool',
      blocked_by: [],
      write_scopes: ['src/team'],
    })
    const task = JSON.parse(text(created)) as { id: string; revision: number }
    await approveCurrentPlan(ctx, lead)
    const spawned = await execute(ctx, lead, 'spawn_teammate', {
      name: 'json-worker', description: 'json worker', prompt: 'wait', context: 'fresh',
    })
    const childId = spawnedChildId(spawned)
    const child = await waitRunning(ctx, childId)
    const readinessSpawn = await execute(ctx, lead, 'spawn_teammate', {
      name: 'readiness-worker', description: 'second durable worker', prompt: 'wait', context: 'fresh',
    })
    const readinessId = spawnedChildId(readinessSpawn)
    await waitRunning(ctx, readinessId)

    const roster = await execute(ctx, child, 'list_agents', {})
    expect(JSON.parse(text(roster))).toMatchObject([
      { name: 'lead', role: 'lead' },
      { name: 'json-worker', role: 'teammate' },
      { name: 'readiness-worker', role: 'teammate' },
    ])
    // Every Team result reaches the model as compact JSON: indentation would
    // spend tokens on every roster, task, and receipt without adding meaning.
    expect(text(roster)).toBe(JSON.stringify(JSON.parse(text(roster))))
    const peer = await execute(ctx, child, 'send_message', { target: 'lead', message: 'progress report' })
    expect(peer.isError).toBe(false)
    expect(JSON.parse(text(peer))).toMatchObject({ status: 'accepted' })
    const followup = await execute(ctx, child, 'send_message', { target: 'lead', message: 'review the report' })
    expect(followup.isError).toBe(false)
    expect(JSON.parse(text(followup))).toMatchObject({ status: 'accepted' })
    await lead.whenIdle()

    const listed = await execute(ctx, child, 'team_task_list', { ready: true, limit: 1 })
    expect(JSON.parse(text(listed))).toMatchObject({ tasks: [{ id: task.id, ready: true }] })
    const read = await execute(ctx, child, 'team_task_get', { task_id: task.id })
    expect(JSON.parse(text(read))).toMatchObject({ id: task.id, revision: 1 })
    const claimed = await execute(ctx, child, 'team_task_update', {
      task_id: task.id,
      expected_revision: task.revision,
      action: 'claim',
    })
    expect(JSON.parse(text(claimed))).toMatchObject({ status: 'in_progress', ownerName: 'json-worker' })
    const stale = await execute(ctx, lead, 'team_task_update', {
      task_id: task.id,
      expected_revision: task.revision,
      action: 'delete',
    })
    expect(stale.isError).toBe(true)
    expect(text(stale)).toContain('stale team task')

    const wait = execute(ctx, lead, 'wait_agent', { timeout_ms: 10_000 })
    const completedCall = new Promise<Awaited<ReturnType<typeof execute>>>((resolve, reject) => {
      setTimeout(() => {
        void execute(ctx, child, 'team_task_update', {
          task_id: task.id,
          expected_revision: 2,
          action: 'complete',
        }).then(resolve, reject)
      }, 0)
    })
    await expect(wait).resolves.toMatchObject({ isError: false })
    expect((await completedCall).isError).toBe(false)

    const childInterrupt = await execute(ctx, child, 'interrupt_agent', { target: 'json-worker' })
    expect(childInterrupt.isError).toBe(true)
    await execute(ctx, lead, 'interrupt_agent', { target: 'json-worker' })
    await execute(ctx, lead, 'interrupt_agent', { target: 'readiness-worker' })
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })
  })

  it('adapts optional task filters, mutations, pagination, and default waiting', async () => {
    const { ctx, lead } = await setup(['hang', 'hang'])
    const firstResult = await execute(ctx, lead, 'team_task_create', {
      subject: 'first', description: 'first task',
    })
    const secondResult = await execute(ctx, lead, 'team_task_create', {
      subject: 'second', description: 'second task',
    })
    const first = JSON.parse(text(firstResult)) as { id: string; revision: number }
    const second = JSON.parse(text(secondResult)) as { id: string; revision: number }
    await approveCurrentPlan(ctx, lead)
    const spawned = await execute(ctx, lead, 'spawn_teammate', {
      name: 'fork-worker', description: 'fork worker', prompt: 'stay active', context: 'fork',
    })
    const childId = spawnedChildId(spawned)
    await waitRunning(ctx, childId)
    const readinessSpawn = await execute(ctx, lead, 'spawn_teammate', {
      name: 'filter-readiness-worker', description: 'second durable worker', prompt: 'stay active', context: 'fresh',
    })
    const readinessId = spawnedChildId(readinessSpawn)
    await waitRunning(ctx, readinessId)
    const claimed = await execute(ctx, lead, 'team_task_update', {
      task_id: first.id, expected_revision: first.revision, action: 'claim',
    })
    const claim = JSON.parse(text(claimed)) as { revision: number }

    expect(JSON.parse(text(await execute(ctx, lead, 'team_task_list', {
      status: 'in_progress', owner: 'lead', cursor: 0, limit: 1,
    })))).toMatchObject({ tasks: [{ id: first.id }] })
    expect(JSON.parse(text(await execute(ctx, lead, 'team_task_list', {
      owner: 'unowned', limit: 1,
    })))).toMatchObject({ tasks: [{ id: second.id }] })
    expect(JSON.parse(text(await execute(ctx, lead, 'team_task_list', {
      cursor: 0, limit: 1,
    })))).toMatchObject({ nextCursor: 1 })
    expect(JSON.parse(text(await execute(ctx, lead, 'team_task_list', {
      cursor: 1,
    })))).not.toHaveProperty('nextCursor')
    expect((await execute(ctx, lead, 'team_task_list', { cursor: -1 })).isError).toBe(true)
    expect((await execute(ctx, lead, 'team_task_list', { limit: 101 })).isError).toBe(true)

    const edited = await execute(ctx, lead, 'team_task_update', {
      task_id: first.id,
      expected_revision: claim.revision,
      action: 'edit',
      subject: 'edited',
      description: 'edited description',
      write_scopes: ['src/team'],
    })
    const edit = JSON.parse(text(edited)) as { revision: number }
    const dependencies = await execute(ctx, lead, 'team_task_update', {
      task_id: first.id,
      expected_revision: edit.revision,
      action: 'set_dependencies',
      blocked_by: [second.id],
    })
    expect(dependencies.isError).toBe(false)
    const dependency = JSON.parse(text(dependencies)) as { revision: number }
    expect((await execute(ctx, lead, 'team_task_update', {
      task_id: first.id,
      expected_revision: dependency.revision,
      action: 'reassign',
      owner: 'fork-worker',
    })).isError).toBe(true)

    const wait = execute(ctx, lead, 'wait_agent', {})
    const wake = new Promise<Awaited<ReturnType<typeof execute>>>((resolve, reject) => {
      setTimeout(() => {
        void execute(ctx, lead, 'team_task_create', {
          subject: 'wake', description: 'wake default wait',
        }).then(resolve, reject)
      }, 0)
    })
    expect((await wait).isError).toBe(false)
    expect((await wake).isError).toBe(false)

    ctx.agentTeams.interrupt(lead, 'fork-worker')
    ctx.agentTeams.interrupt(lead, 'filter-readiness-worker')
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })
  })

  it('removes and reinstalls every scoped registration across plugin HMR without stopping the child', async () => {
    const { ctx, lead, fiber } = await setup(['hang'])
    await approveCurrentPlan(ctx, lead)
    const spawned = await execute(ctx, lead, 'spawn_teammate', {
      name: 'hmr-worker', description: 'hmr worker', prompt: 'wait',
    })
    const childId = spawnedChildId(spawned)
    const child = await waitRunning(ctx, childId)

    await fiber.dispose()
    expect((await assembly(ctx, lead)).tools.map(schema => schema.name).some(name => TOOL_NAMES.includes(name))).toBe(false)
    expect((await assembly(ctx, child)).tools.map(schema => schema.name).some(name => TOOL_NAMES.includes(name))).toBe(false)
    expect(ctx.agents.get(childId)).toBe(child)

    const replacement = await ctx.plugin(toolTeam)
    expect((await assembly(ctx, lead)).tools.map(schema => schema.name).filter(name => TOOL_NAMES.includes(name)).sort())
      .toEqual(TOOL_NAMES)
    expect((await assembly(ctx, child)).tools.map(schema => schema.name).filter(name => TOOL_NAMES.includes(name)).sort())
      .toEqual(TOOL_NAMES)
    ctx.agentTeams.interrupt(lead, 'hmr-worker')
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })
    await replacement.dispose()
  })

  it('shadows legacy global control names only inside Team member scopes', async () => {
    const { ctx, lead, fiber } = await setup([], true)
    const teamSchema = (await assembly(ctx, lead)).tools.find(schema => schema.name === 'send_message')
    expect(JSON.stringify(teamSchema)).toContain('target')
    expect(JSON.stringify(teamSchema)).not.toContain('subagent_id')

    await fiber.dispose()
    const legacySchema = (await assembly(ctx, lead)).tools.find(schema => schema.name === 'send_message')
    expect(JSON.stringify(legacySchema)).toContain('agent_id')
  })

  it('rolls back partial scoped installation after a same-scope collision', async () => {
    const { ctx, lead, fiber } = await setup([])
    await fiber.dispose()
    lead.ctx.tools.register(defineContentToolFixture({
      name: 'spawn_teammate',
      description: 'intentional collision',
      parameters: {},
      async execute() { return [{ type: 'text', text: 'collision' }] },
    }))

    await expect(ctx.plugin(toolTeam)).rejects.toThrow(/already registered/u)
    const assembled = await assembly(ctx, lead)
    expect(assembled.tools.filter(schema => TOOL_NAMES.includes(schema.name)).map(schema => schema.name))
      .toEqual(['spawn_teammate'])
    expect(renderPrompt(assembled)).not.toContain('Your Team role is lead')
  })

  it('resolves direct-apply defaults without Loader schema normalization', async () => {
    const { ctx, lead, fiber } = await setup([textResponse('ordinary child')])
    await fiber.dispose()
    expect(() => { toolTeam.apply(ctx, { externalRestrictedTools: [''] }) })
      .toThrow('externalRestrictedTools[0] must be a non-empty string')
    for (const config of [
      { minExecutionMembers: 0 },
      { minExecutionMembers: 1.5 },
      { maxExecutionMembers: Number.MAX_SAFE_INTEGER + 1 },
    ]) {
      expect(() => { toolTeam.apply(ctx, config) })
        .toThrow(/ExecutionMembers must be a positive safe integer/u)
    }
    expect(() => { toolTeam.apply(ctx, { minExecutionMembers: 3, maxExecutionMembers: 2 }) })
      .toThrow('maxExecutionMembers must be greater than or equal to minExecutionMembers')
    toolTeam.apply(ctx, {})
    expect((await assembly(ctx, lead)).tools.map(schema => schema.name).filter(name => TOOL_NAMES.includes(name)).sort())
      .toEqual(TOOL_NAMES)
    const ordinary = await ctx.subagents.startContinuable({
      provider: 'spawn',
      label: 'ordinary child',
      request: { prompt: [{ type: 'text', text: 'finish' }], parent: lead },
      signal: SIGNAL,
    })
    await vi.waitFor(() => { expect(ctx.agents.get(ordinary.childId)).toBeUndefined() }, { timeout: 5_000 })
  })

  it('reinstalls Team scope before a cold-resumed teammate request', async () => {
    const { ctx, lead } = await setup([textResponse('first'), 'hang'])
    await approveCurrentPlan(ctx, lead)
    const spawned = await execute(ctx, lead, 'spawn_teammate', {
      name: 'cold-worker', description: 'cold worker', prompt: 'finish once',
    })
    const childId = spawnedChildId(spawned)
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })

    await ctx.agentTeams.sendMessage(lead, {
      target: 'cold-worker',
      content: [{ type: 'text', text: 'resume with Team scope' }],
      signal: SIGNAL,
    })
    const resumed = await waitRunning(ctx, childId)
    expect((await assembly(ctx, resumed)).tools.map(schema => schema.name)
      .filter(name => TOOL_NAMES.includes(name)).sort()).toEqual(TOOL_NAMES)
    expect(renderPrompt(await assembly(ctx, resumed))).toContain('Your Team role is teammate; your Team name is cold-worker')
    ctx.agentTeams.interrupt(lead, 'cold-worker')
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })
  })

  it('fails safely without a calling Agent and has the function-plugin export shape', async () => {
    const { ctx } = await setup([])
    const result = await execute(ctx, undefined, 'list_agents', {})
    expect(result.isError).toBe(true)
    expect(text(result)).toContain('unknown tool "list_agents"')
    expect('default' in toolTeam).toBe(false)
    expect(toolTeam.name).toBe('tool-agent-team')
    expect(toolTeam.inject).toEqual(['agents', 'agentTeams', 'subagents', 'tools', 'systemPrompt'])
  })

  it('uses configured fresh and fork provider names', async () => {
    const { ctx, lead, fiber } = await setup([textResponse('custom')])
    await fiber.dispose()
    await ctx.plugin(SubagentSpawn, { providerName: 'team-fresh' })
    await ctx.plugin(toolTeam, { freshProvider: 'team-fresh', forkProvider: 'fork' })
    await approveCurrentPlan(ctx, lead)
    const result = await execute(ctx, lead, 'spawn_teammate', {
      name: 'custom-provider', description: 'custom provider', prompt: 'go',
    })
    expect(result.isError).toBe(false)
    const childId = spawnedChildId(result)
    await vi.waitFor(() => { expect(ctx.agents.get(childId)).toBeUndefined() }, { timeout: 5_000 })
    expect(ctx.agentTeams.listMembers(lead)[1]).toMatchObject({ provider: 'team-fresh' })
  })
})
