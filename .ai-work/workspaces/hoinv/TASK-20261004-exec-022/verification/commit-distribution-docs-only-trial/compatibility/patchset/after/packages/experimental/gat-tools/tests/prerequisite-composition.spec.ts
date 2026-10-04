/** Actual HTTP authority, reserved-child, prompt and registry composition. */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { Session, SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import Subagents from '@deepseek-ai/dsh-subagent'
import * as Spawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import * as Fork from '@deepseek-ai/dsh-subagent-fork-in-process'
import { defineTool, EXTERNAL_DELEGATION } from '@deepseek-ai/dsh-tools'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../../gat-core/src/index.ts'
import { TestSessionQuery } from '../../gat-core/tests/test-session-query.ts'
import { mountHumanControl } from '../../gat-core/tests/human-control-fixture.ts'
import * as TeamTools from '../src/index.ts'

const signal = new AbortController().signal
const cleanups: Array<() => Promise<void>> = []
afterEach(async () => { for (const cleanup of cleanups.splice(0)) await cleanup() })

async function harness(simpleMode = true) {
  const ctx = new Context()
  const root = mkdtempSync(join(tmpdir(), 'gat-prerequisite-composition-'))
  const control = await mountHumanControl(ctx)
  cleanups.push(async () => {
    try { await ctx.fiber.dispose() } finally { await control.close(); rmSync(root, { recursive: true, force: true }) }
  })
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(JsonlSessionPersistence, { root })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(Subagents)
  await ctx.plugin(Spawn, { providerName: 'spawn' })
  await ctx.plugin(Fork, { providerName: 'fork' })
  await ctx.plugin(TeamService)
  await ctx.plugin(TeamTools, { simpleMode, minExecutionMembers: 1, maxExecutionMembers: 2 })
  const adapter = new MockAdapter(Array.from({ length: 8 }, () => textResponse('done')))
  ctx.llm.registerAdapter(['mock'], adapter)
  const lead = await ctx.agentLoop.create(SessionId('composition-lead'), { provider: 'mock', model: 'mock' }, { cwd: root })
  const spec = { name: 'worker', description: 'controlled worker', prompt: [{ type: 'text' as const, text: 'initial work' }], context: 'fresh' as const, provider: 'spawn' }
  const approved = await control.call('approveMemberAdd', lead.id, spec)
  expect(approved).toMatchObject({ ok: true, value: { approved: true } })
  const { member } = await ctx.agentTeams.spawnTeammate(lead, { ...spec, signal })
  const child = ctx.agents.get(member.id)!
  return { ctx, lead, child, control, adapter }
}

async function authorize(h: Awaited<ReturnType<typeof harness>>) {
  const mission = await h.ctx.agentTeams.createMission(h.lead, { title: 'selected mission', objective: 'exact task execution' })
  const task = await h.ctx.agentTeams.createTask(h.lead, { missionId: mission.id, subject: 'selected canonical task', description: 'controlled work' })
  const current = h.ctx.agentTeams.getMission(h.lead, mission.id)
  expect(await h.control.call('approveMission', h.lead.id, { missionId: current.id, expectedRevision: current.revision }))
    .toMatchObject({ ok: true, value: { ok: true } })
  return { mission: current, task }
}

function effect(ctx: Context, counter: { calls: number }) {
  ctx.tools.register(defineTool({
    name: 'effect', description: 'observable effect', parameters: {}, capabilities: ['workspace-effect'],
    output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
    async execute() { counter.calls += 1; return 'effect happened' },
  }))
}

describe('qualified prerequisite composition', () => {
  it('keeps actual roster bootstrap quarantined, then refreshes the exact leased child before its only request', async () => {
    const h = await harness()
    expect(h.adapter.requests).toEqual([])
    expect(h.child.inbox.nextTurn).toEqual([])
    await expect(h.ctx.agentTeams.activateMember(h.child, signal)).rejects.toMatchObject({ code: 'TEAM_EXECUTION_DENIED' })
    const queued = await h.ctx.agentTeams.sendMessage(h.lead, { target: 'worker', content: [{ type: 'text', text: 'queued peer input' }], signal })
    expect(queued.status).toBe('queued')
    expect(h.adapter.requests).toEqual([])
    const { mission, task } = await authorize(h)
    await h.ctx.agentTeams.updateTask(h.child, { taskId: task.id, expectedRevision: task.revision, action: 'claim' })
    h.ctx.agentTeams.bindExecution(h.child, { missionId: mission.id, expectedRevision: mission.revision, taskId: task.id })
    let refreshed = false
    h.child.ctx.on('agent/prepare-prompt', async () => {
      await Promise.resolve()
      h.child.ctx.systemPrompt.section({ name: 'binding-owner', order: 310, text: 'current binding context' })
      refreshed = true
    })
    h.ctx.on('llm/stream', (request, next) => {
      expect(refreshed).toBe(true)
      expect(request.messages).toEqual(Session.create(h.child.id, h.child.session.snapshotEvents()).deriveMessages())
      return next()
    })
    await h.ctx.agentTeams.activateMember(h.child, signal)
    await h.child.whenIdle()
    expect(h.adapter.requests).toHaveLength(1)
    expect(JSON.stringify(h.adapter.requests[0]!.messages)).toContain('current binding context')
    const handle = await h.ctx.sessionPersistence.open(h.child.id, 'read')
    try {
      const events = (await handle.read()).events
      expect(events.filter(event => event.type === 'subagent/initial-admission' && event.data.kind === 'persisted')).toHaveLength(1)
      expect(events.filter(event => event.type === 'subagent/initial-admission' && event.data.kind === 'activated')).toHaveLength(1)
    } finally { await handle.close() }
  })

  it('rechecks the actual lease after an awaited policy and keeps nested delegation denied with a valid lease', async () => {
    const h = await harness()
    const counter = { calls: 0 }
    effect(h.ctx, counter)
    const run = (name: string) => h.ctx.tools.execute({ name, arguments: {}, callId: ToolCallId(name), agent: h.lead, signal })
    expect((await run('effect')).isError).toBe(true)
    const { mission } = await authorize(h)
    h.ctx.agentTeams.bindExecution(h.lead, { missionId: mission.id, expectedRevision: mission.revision })
    let wrapperEffects = 0
    h.ctx.tools.register(defineTool({ name: 'delegate_alias', description: 'delegator alias', parameters: {}, capabilities: [EXTERNAL_DELEGATION],
      output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
      async execute() { counter.calls += 1; return 'delegated' },
    }))
    h.ctx.tools.register(defineTool({ name: 'inspection_wrapper', description: 'restricted descendant wrapper', parameters: {},
      capabilities: ['team-inspection'], nestedTools: ['delegate_alias'],
      output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
      async execute() { wrapperEffects += 1; return 'wrapper effect' },
    }))
    expect((await run('inspection_wrapper')).isError).toBe(true)
    const entered = Promise.withResolvers<ReturnType<() => void>>()
    const release = Promise.withResolvers<ReturnType<() => void>>()
    h.ctx.on('tools/pre-execute', async (exec, next) => {
      if (exec.name === 'effect') { entered.resolve(); await release.promise }
      return next()
    })
    const pending = run('effect')
    await entered.promise
    expect(await h.control.call('revokeMission', h.lead.id, { missionId: mission.id, expectedRevision: mission.revision }))
      .toMatchObject({ ok: true, value: { ok: true } })
    release.resolve()
    expect((await pending).isError).toBe(true)
    expect({ effects: counter.calls, wrapperEffects }).toEqual({ effects: 0, wrapperEffects: 0 })
  })

  it('denies the actual provider after a later awaited model listener revokes its mission', async () => {
    const h = await harness()
    const { mission } = await authorize(h)
    h.ctx.agentTeams.bindExecution(h.child, { missionId: mission.id, expectedRevision: mission.revision })
    let revoked = false
    h.child.ctx.on('agent/model-admission', async () => {
      expect(await h.control.call('revokeMission', h.lead.id, { missionId: mission.id, expectedRevision: mission.revision }))
        .toMatchObject({ ok: true, value: { ok: true } })
      revoked = true
    })
    await h.ctx.agentTeams.activateMember(h.child, signal)
    await h.child.whenIdle()
    expect(revoked).toBe(true)
    expect(h.adapter.requests).toHaveLength(0)
    expect(() => { h.ctx.agentTeams.assertExecution(h.child) }).toThrow()
  })

  it('retains the actual child gate when authority is revoked during activation publication', async () => {
    const h = await harness()
    const { mission } = await authorize(h)
    h.ctx.agentTeams.bindExecution(h.child, { missionId: mission.id, expectedRevision: mission.revision })
    const entered = Promise.withResolvers<ReturnType<() => void>>()
    const release = Promise.withResolvers<ReturnType<() => void>>()
    const original = h.child.ctx.sessions.flush.bind(h.child.ctx.sessions)
    const spy = vi.spyOn(h.child.ctx.sessions, 'flush').mockImplementation(async (session) => {
      if (session.id === h.child.id && session.snapshotEvents().some(event => event.type === 'subagent/initial-admission' && event.data.kind === 'activated')) {
        entered.resolve()
        await release.promise
      }
      return original(session)
    })
    const activation = h.ctx.agentTeams.activateMember(h.child, signal)
    const rejected = expect(activation).rejects.toMatchObject({ code: 'CONTINUABLE_ACTIVATE_FAILED', cause: { code: 'TEAM_EXECUTION_DENIED' } })
    await entered.promise
    expect(await h.control.call('revokeMission', h.lead.id, { missionId: mission.id, expectedRevision: mission.revision }))
      .toMatchObject({ ok: true, value: { ok: true } })
    release.resolve()
    await rejected
    spy.mockRestore()
    expect(h.child.status).toBe('idle')
    expect(h.adapter.requests).toHaveLength(0)
  })

  it('requires both exact mission and current HUMAN plan in governed mode', async () => {
    const h = await harness(false)
    const { mission } = await authorize(h)
    expect(() => { h.ctx.agentTeams.bindExecution(h.lead, { missionId: mission.id, expectedRevision: mission.revision }) })
      .toThrow('current Team plan')
    const revision = h.ctx.agentTeams.remoteView(h.lead).planRevision
    expect(await h.control.call('approvePlan', h.lead.id, { approvedRevision: revision }))
      .toMatchObject({ ok: true, value: { ok: true } })
    h.ctx.agentTeams.bindExecution(h.lead, { missionId: mission.id, expectedRevision: mission.revision })
    const counter = { calls: 0 }
    effect(h.ctx, counter)
    const result = await h.ctx.tools.execute({ name: 'effect', arguments: {}, callId: ToolCallId('allowed'), agent: h.lead, signal })
    expect(result.isError).toBe(false)
    expect(counter.calls).toBe(1)
  })
})
