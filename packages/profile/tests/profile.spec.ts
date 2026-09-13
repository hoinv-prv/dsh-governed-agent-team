/** The experimental bundle must carry one parseable, explicit Team layer. */

import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import Include from '@deepseek-ai/cordis-plugin-include'
import * as yaml from 'js-yaml'
import { entryListSchema } from '@deepseek-ai/cordis-plugin-include'
import type { Agent } from '@deepseek-ai/dsh-agent'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { loadOptionalPatches } from '@deepseek-ai/dsh-app-boot'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SessionQueryEngine from '@deepseek-ai/dsh-session-query'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as SubagentFork from '@deepseek-ai/dsh-subagent-fork-in-process'
import * as SubagentSpawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { defineContentToolFixture } from '@deepseek-ai/dsh-tools'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import * as toolSubagent from '../../../subagent/tool-subagent/src/index.ts'
import TeamService from '../../gat-core/src/index.ts'
import * as toolTeam from '../../gat-tools/src/index.ts'

const roots: string[] = []
const contexts: Context[] = []
const consumedToolSubagentConfigs: toolSubagent.Config[] = []
const SIGNAL = new AbortController().signal
let callNumber = 0

class TestSessionQuery extends SessionQueryEngine {
  override searchSessions(): Promise<never> {
    return Promise.reject(new Error('session search is not configured in this test'))
  }

  override searchEvents(): Promise<never> {
    return Promise.reject(new Error('event search is not configured in this test'))
  }
}

afterEach(async () => {
  vi.useRealTimers()
  const failures: unknown[] = []
  try {
    for (const ctx of contexts.splice(0).reverse()) {
      try {
        await ctx.fiber.dispose()
      } catch (error: unknown) {
        failures.push(error)
      }
    }
  } finally {
    for (const root of roots.splice(0)) {
      try {
        rmSync(root, { recursive: true, force: true })
      } catch (error: unknown) {
        failures.push(error)
      }
    }
    consumedToolSubagentConfigs.length = 0
    callNumber = 0
  }
  if (failures.length > 0) throw new AggregateError(failures, 'profile smoke teardown failed')
})

function execute(ctx: Context, agent: Agent, name: string, args: unknown) {
  return ctx.tools.execute({
    callId: ToolCallId(`profile-smoke-${++callNumber}`),
    name,
    arguments: args,
    agent,
    signal: SIGNAL,
  })
}

function text(result: Awaited<ReturnType<typeof execute>>): string {
  return result.content.flatMap(block => block.type === 'text' ? [block.text] : []).join('')
}

function childId(result: Awaited<ReturnType<typeof execute>>): SessionId {
  const value = JSON.parse(text(result)) as { member: { id: string } }
  return SessionId(value.member.id)
}

async function waitRunning(ctx: Context, id: SessionId): Promise<Agent> {
  return vi.waitFor(() => {
    const agent = ctx.agents.get(id)
    expect(agent?.status).toBe('running')
    return agent!
  }, { timeout: 5_000 })
}

function planWork(view: ReturnType<TeamService['remoteView']>) {
  return {
    planRevision: view.planRevision,
    planPhase: view.planPhase,
    planApproval: view.planApproval,
    tasks: view.tasks,
    work: view.work,
  }
}

async function bootProfile(storageRoot: string, script: ConstructorParameters<typeof MockAdapter>[0]) {
  const ctx = new Context()
  contexts.push(ctx)
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(JsonlSessionPersistence, { root: storageRoot })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(SubagentService)
  await ctx.plugin(SubagentSpawn, { providerName: 'spawn' })
  await ctx.plugin(SubagentFork, { providerName: 'fork' })
  await ctx.plugin(Loader)
  ctx.loader.builtins.include = Include
  const noop = { apply() {} }
  const toolSubagentConsumer = {
    ...toolSubagent,
    apply(runtimeCtx: Context, config: toolSubagent.Config) {
      consumedToolSubagentConfigs.push(structuredClone(config))
      toolSubagent.apply(runtimeCtx, config)
    },
  }
  const modules = new Map<string, unknown>([
    ['@test/profile-base-row', noop],
    ['@deepseek-ai/dsh-tool-subagent', toolSubagentConsumer],
    ['@vuhoi/gat-core', TeamService],
    ['@vuhoi/gat-tools', toolTeam],
  ])
  ctx.loader.internal = {
    version: 'v2',
    async import(specifier: string) {
      if (!modules.has(specifier)) throw new Error(`unexpected Loader import: ${specifier}`)
      return modules.get(specifier)
    },
  } as unknown as NonNullable<typeof ctx.loader.internal>

  const root = fileURLToPath(new URL('..', import.meta.url))
  const fixture = resolve(root, 'tests/fixtures/keyless-base.yml')
  const patches = loadOptionalPatches('agent-team-profile-smoke', resolve(root, 'cordis.patch.yml'))
  if (patches === undefined) throw new Error('checked-in Agent Teams profile patch is missing')
  await ctx.loader.create({
    name: 'cordis:include',
    config: { path: pathToFileURL(fixture).href, patches },
  })
  await ctx.loader.await()
  for (const name of ['ask_user_question', 'glob', 'grep', 'read', 'read_image']) {
    ctx.tools.register(defineContentToolFixture({
      name,
      description: `test-only ${name} restricted-mode capability`,
      parameters: {},
      async execute() { return [{ type: 'text', text: name }] },
    }))
  }
  ctx.llm.registerAdapter(['mock'], new MockAdapter(script))
  return ctx
}

describe('Agent Teams profile bundle', () => {
  it('declares a private parseable layer with Team-owned controls', () => {
    const root = fileURLToPath(new URL('..', import.meta.url))
    const manifest = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8')) as {
      private?: boolean
      publishConfig?: { access?: string }
      dependencies?: Record<string, string>
      dsh?: { bundle?: { patch?: string } }
    }
    expect(manifest.private).toBe(true)
    expect(manifest.publishConfig).toBeUndefined()
    expect(manifest.dsh?.bundle?.patch).toBe('./cordis.patch.yml')
    expect(manifest.dependencies).toMatchObject({
      '@vuhoi/gat-core': 'file:../gat-core',
      '@vuhoi/gat-tools': 'file:../gat-tools',
    })

    const parsed = yaml.load(
      readFileSync(resolve(root, manifest.dsh!.bundle!.patch!), 'utf8'),
      { schema: entryListSchema },
    )
    expect(Array.isArray(parsed)).toBe(true)
    const patches = parsed as {
      id?: string
      disabled?: boolean
      config?: Record<string, unknown>
      insert?: { id?: string; name?: string; config?: Record<string, unknown> }[]
    }[]
    expect(patches.find(patch => patch.id === 'tool-subagent-control')).toMatchObject({ disabled: true })
    expect(patches.find(patch => patch.id === 'tool-subagent-list-agents')).toMatchObject({ disabled: true })
    expect(patches.find(patch => patch.id === 'tool-subagent')?.config).toMatchObject({ backgroundMode: 'one-shot' })
    expect(patches.find(patch => patch.id === 'tool-subagent-fork')?.config).toMatchObject({ backgroundMode: 'one-shot' })
    const inserted = patches.flatMap(patch => patch.insert ?? [])
    expect(inserted.find(entry => entry.id === 'agent-team')).toMatchObject({
      name: '@vuhoi/gat-core',
      config: { maxMembers: 8 },
    })
    expect(inserted.find(entry => entry.id === 'tool-agent-team')).toMatchObject({
      name: '@vuhoi/gat-tools',
      config: {
        freshProvider: 'spawn',
        forkProvider: 'fork',
        minExecutionMembers: 2,
        maxExecutionMembers: 4,
        externalRestrictedTools: ['ask_user_question', 'glob', 'grep', 'read', 'read_image'],
      },
    })
  })

  it('composes the governed lifecycle and replays its persisted plan and work projection', async () => {
    const storageRoot = mkdtempSync(join(tmpdir(), 'dsh-agent-team-profile-smoke-'))
    roots.push(storageRoot)
    const sessionId = SessionId('governed-profile-smoke')
    const first = await bootProfile(storageRoot, [
      'hang',
      'hang',
      textResponse('spawn one-shot result'),
      textResponse('fork one-shot result'),
    ])
    const leadHandle = await first.agents.create({
      sessionId,
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    const lead = leadHandle.agent
    const dangerCalls = { count: 0 }
    first.tools.register(defineContentToolFixture({
      name: 'danger_write',
      description: 'test-only non-allowlisted write capability',
      parameters: {},
      async execute() {
        dangerCalls.count += 1
        return [{ type: 'text', text: 'wrote' }]
      },
    }))

    const entries = new Map([...first.loader.entries()].map(entry => [entry.options.id, entry.options]))
    expect(entries.get('tool-subagent')?.config).toMatchObject({
      provider: 'spawn', toolName: 'subagent', backgroundMode: 'one-shot',
    })
    expect(entries.get('tool-subagent-fork')?.config).toMatchObject({
      provider: 'fork', toolName: 'subagent_fork', backgroundMode: 'one-shot',
    })
    expect(consumedToolSubagentConfigs).toEqual([
      expect.objectContaining({ provider: 'spawn', toolName: 'subagent', backgroundMode: 'one-shot' }),
      expect.objectContaining({ provider: 'fork', toolName: 'subagent_fork', backgroundMode: 'one-shot' }),
    ])
    expect(first.tools.get('subagent', lead)).toBeDefined()
    expect(first.tools.get('subagent_fork', lead)).toBeDefined()
    expect(entries.get('agent-team')?.config).toMatchObject({ maxMembers: 8 })
    expect(entries.get('tool-agent-team')?.config).toEqual({
      freshProvider: 'spawn',
      forkProvider: 'fork',
      minExecutionMembers: 2,
      maxExecutionMembers: 4,
      externalRestrictedTools: ['ask_user_question', 'glob', 'grep', 'read', 'read_image'],
    })

    const createdResult = await execute(first, lead, 'team_task_create', {
      subject: 'Implement governed smoke',
      description: 'Exercise composition and replay',
      write_scopes: ['src/governed-smoke.ts'],
    })
    expect(createdResult.isError).toBe(false)
    const task = JSON.parse(text(createdResult)) as { id: string; revision: number }
    const expectedTask = {
      id: 'task-1',
      revision: 1,
      subject: 'Implement governed smoke',
      description: 'Exercise composition and replay',
      status: 'pending',
      blockedBy: [],
      writeScopes: ['src/governed-smoke.ts'],
      ready: true,
      writeScopeWarnings: [],
    }
    expect(task).toEqual(expectedTask)
    const draftView = first.agentTeams.remoteView(lead)
    expect(draftView.planApproval).toBeUndefined()
    expect(draftView).toEqual({
      planRevision: 1,
      planPhase: 'draft',
      work: [],
      members: [expect.objectContaining({ name: 'lead', role: 'lead' })],
      tasks: [expectedTask],
    })
    const denied = await execute(first, lead, 'danger_write', {})
    expect(denied.isError).toBe(true)
    expect(text(denied)).toContain('is not HUMAN-approved')
    expect(dangerCalls.count).toBe(0)

    const currentRevision = 1
    await expect(first.agentTeams.remoteApprovePlan(lead, { approvedRevision: currentRevision - 1 }))
      .resolves.toMatchObject({ ok: false, error: { code: 'team-plan-conflict' } })
    await expect(first.agentTeams.remoteApprovePlan(lead, { approvedRevision: currentRevision }))
      .resolves.toEqual({ ok: true, value: { approvedRevision: currentRevision } })

    const blockedSpawn = await execute(first, lead, 'spawn_teammate', {
      name: 'blocked-worker', description: 'report a durable blocker', prompt: 'stay active',
    })
    const blockedWorker = await waitRunning(first, childId(blockedSpawn))
    const reviewSpawn = await execute(first, lead, 'spawn_teammate', {
      name: 'review-worker', description: 'report a review file', prompt: 'stay active', context: 'fork',
    })
    const reviewWorker = await waitRunning(first, childId(reviewSpawn))
    expect(lead.session.snapshotEvents().filter(event => event.type === 'team/member'
      && event.data.member.phase === 'active')).toHaveLength(2)

    const starts = vi.spyOn(first.subagents, 'start')
    const freshDelegation = await execute(first, lead, 'subagent', {
      description: 'fresh one shot', prompt: 'return the scripted fresh result',
    })
    if (freshDelegation.isError) throw new Error(text(freshDelegation))
    expect(text(freshDelegation)).toBe('spawn one-shot result')
    const forkDelegation = await execute(first, lead, 'subagent_fork', {
      description: 'fork one shot', prompt: 'return the scripted fork result',
    })
    if (forkDelegation.isError) throw new Error(text(forkDelegation))
    expect(text(forkDelegation)).toBe('fork one-shot result')
    expect(starts.mock.calls.map(([provider]) => provider)).toEqual(['spawn', 'fork'])

    expect((await execute(first, lead, 'danger_write', {})).isError).toBe(false)
    expect(dangerCalls.count).toBe(1)

    const blocked = await execute(first, blockedWorker, 'report_team_status', {
      state: 'blocked', summary: 'Cannot continue', reason: 'Waiting for a local prerequisite',
    })
    expect(blocked.isError).toBe(false)
    const review = await execute(first, reviewWorker, 'report_team_status', {
      state: 'review_required', summary: 'Ready for review', files: ['./src\\governed-smoke.ts'],
    })
    expect(review.isError).toBe(false)
    expect(JSON.parse(text(review))).toMatchObject({ files: ['src/governed-smoke.ts'] })

    const claimed = await execute(first, lead, 'team_task_update', {
      task_id: task.id, expected_revision: task.revision, action: 'claim',
    })
    const claim = JSON.parse(text(claimed)) as { revision: number }
    const completed = await execute(first, lead, 'team_task_update', {
      task_id: task.id, expected_revision: claim.revision, action: 'complete',
    })
    expect(completed.isError).toBe(false)
    const beforeRestart = planWork(first.agentTeams.remoteView(lead))
    expect(beforeRestart).toMatchObject({
      planRevision: currentRevision,
      planPhase: 'approved',
      planApproval: { approvedRevision: currentRevision },
      tasks: [{ status: 'completed' }],
      work: [
        { state: 'blocked', reason: 'Waiting for a local prerequisite' },
        { state: 'review_required', files: ['src/governed-smoke.ts'] },
      ],
    })

    await first.fiber.dispose()
    contexts.splice(contexts.indexOf(first), 1)
    const restarted = await bootProfile(storageRoot, [])
    const resumed = await restarted.agents.resume({
      resumeSessionId: sessionId,
      agentOptions: { provider: 'mock', model: 'mock' },
    })
    expect(planWork(restarted.agentTeams.remoteView(resumed.agent))).toEqual(beforeRestart)
  })
})
