/** Complete authorization states through signed HTTP controls and actual tool effects. */
import { afterEach, describe, expect, it } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import Subagents from '@deepseek-ai/dsh-subagent'
import * as Spawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import * as Fork from '@deepseek-ai/dsh-subagent-fork-in-process'
import { defineTool } from '@deepseek-ai/dsh-tools'
import { MockAdapter, textResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../../gat-core/src/index.ts'
import { TestSessionQuery } from '../../gat-core/tests/test-session-query.ts'
import { mountHumanControl } from '../../gat-core/tests/human-control-fixture.ts'
import * as TeamTools from '../src/index.ts'

const signal = new AbortController().signal
const cleanups: Array<() => Promise<void>> = []
afterEach(async () => { for (const cleanup of cleanups.splice(0)) await cleanup() })

const missionStates = ['absent', 'draft', 'authorized', 'stale', 'closed'] as const
const planStates = ['unapproved', 'current', 'stale'] as const
const cells = [true, false].flatMap(simpleMode => [false, true].flatMap(enabled =>
  missionStates.flatMap(mission => planStates.map(plan => ({ simpleMode, enabled, mission, plan })))))

async function harness(simpleMode: boolean, enabled: boolean) {
  const ctx = new Context()
  const root = mkdtempSync(join(tmpdir(), 'gat-authorization-matrix-'))
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
  const adapter = new MockAdapter([textResponse('unexpected execution')])
  ctx.llm.registerAdapter(['mock'], adapter)
  const lead = await ctx.agentLoop.create(SessionId('matrix-lead'), { provider: 'mock', model: 'mock' }, { cwd: root })
  if (enabled) {
    const spec = { name: 'worker', description: 'quarantined roster member', prompt: [{ type: 'text' as const, text: 'initial' }], context: 'fresh' as const, provider: 'spawn' }
    expect(await control.call('approveMemberAdd', lead.id, spec)).toMatchObject({ ok: true, value: { approved: true } })
    await ctx.agentTeams.spawnTeammate(lead, { ...spec, signal })
  }
  return { ctx, lead, control, adapter }
}

describe('complete actual authorization matrix', () => {
  it.each(cells)('simple=$simpleMode enabled=$enabled mission=$mission plan=$plan', async (cell) => {
    const h = await harness(cell.simpleMode, cell.enabled)
    const { ctx, lead, control } = h
    const controls: Array<{ action: string; result: unknown }> = []
    const call = async (action: string, request: unknown) => {
      const result = await control.call(action, lead.id, request)
      controls.push({ action, result })
      expect(result.ok).toBe(true)
      return result.value as { ok: boolean; error?: { code: string; message: string } }
    }
    const planning = await ctx.agentTeams.createMission(lead, { title: 'unrelated planning mission', objective: 'non-empty canonical plan, never selected implicitly' })
    await ctx.agentTeams.createTask(lead, { missionId: planning.id, subject: 'planning task', description: 'canonical non-empty Team plan' })
    const selected = cell.mission === 'absent' ? undefined : await ctx.agentTeams.createMission(lead, { title: 'exact selected mission', objective: 'host selects only this scope' })
    if (selected && cell.mission !== 'draft') {
      expect(await call('approveMission', { missionId: selected.id, expectedRevision: selected.revision })).toMatchObject({ ok: true })
    }
    if (!selected) {
      const unrelated = ctx.agentTeams.getMission(lead, planning.id)
      expect(await call('approveMission', { missionId: unrelated.id, expectedRevision: unrelated.revision })).toMatchObject({ ok: true })
      expect(ctx.agentTeams.listMissions(lead).some(mission => mission.status === 'approved')).toBe(true)
    }
    const approvePlan = async () => call('approvePlan', { approvedRevision: ctx.agentTeams.remoteView(lead).planRevision })
    let planRejection: { code: string; message: string } | undefined
    if (cell.plan !== 'unapproved') {
      const result = await approvePlan()
      if (!result.ok) planRejection = result.error
    }
    let bindingFailure: string | undefined
    if (selected) {
      try { ctx.agentTeams.bindExecution(lead, { missionId: selected.id, expectedRevision: selected.revision }) }
      catch (error) { bindingFailure = error instanceof Error ? error.message : String(error) }
    }
    if (selected && cell.mission === 'stale') {
      await ctx.agentTeams.createTask(lead, { missionId: selected.id, subject: 'mission revision changed', description: 'invalidates the prior exact mission receipt and lease' })
      const current = ctx.agentTeams.getMission(lead, selected.id)
      expect(current.revision).toBeGreaterThan(selected.revision)
      expect(current.status).toBe('draft')
      expect(current.approval).toBeUndefined()
      if (cell.plan === 'current' && !planRejection) expect(await approvePlan()).toMatchObject({ ok: true })
    }
    if (selected && cell.mission === 'closed') {
      expect(await call('closeMission', { missionId: selected.id, expectedRevision: selected.revision })).toMatchObject({ ok: true })
      expect(ctx.agentTeams.getMission(lead, selected.id).status).toBe('closed')
    }
    if (cell.plan === 'stale' && cell.mission !== 'stale' && !planRejection) {
      await ctx.agentTeams.createTask(lead, { missionId: planning.id, subject: 'planning revision changed', description: 'changes only unrelated planning mission and Team plan' })
    }
    const view = ctx.agentTeams.remoteView(lead)
    expect(view.enabled).toBe(cell.enabled)
    expect(view.members.filter(member => member.role === 'teammate')).toHaveLength(cell.enabled ? 1 : 0)
    const hasTeamTools = ctx.tools.schemas(lead).some(schema => schema.name === 'list_agents')
    expect(hasTeamTools).toBe(!cell.simpleMode || cell.enabled)
    if (cell.plan === 'unapproved' || planRejection) expect(view.planApproval).toBeUndefined()
    else if (cell.plan === 'current') expect(view.planApproval?.approvedRevision).toBe(view.planRevision)
    else expect(view.planApproval!.approvedRevision).toBeLessThan(view.planRevision)
    if (selected && cell.mission === 'authorized') expect(ctx.agentTeams.getMission(lead, selected.id).status).toBe('approved')
    const authorityDiagnostic = ctx.agentTeams.executionDiagnostic(lead)
    let effects = 0
    ctx.tools.register(defineTool({ name: 'matrix_effect', description: 'observable workspace effect', parameters: {}, capabilities: ['workspace-effect'],
      output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
      async execute() { effects += 1; return 'effect body ran' },
    }))
    const result = await ctx.tools.execute({ name: 'matrix_effect', arguments: {}, callId: ToolCallId('matrix-effect'), agent: lead, signal })
    const reachable = planRejection === undefined
    const allowed = !cell.enabled ? cell.simpleMode : cell.mission === 'authorized' && (cell.simpleMode || cell.plan === 'current') && reachable
    expect(result.isError).toBe(!allowed)
    expect(effects).toBe(allowed ? 1 : 0)
    expect(h.adapter.requests).toHaveLength(0)
    const reason = result.content.flatMap(block => block.type === 'text' ? [block.text] : []).join('\n')
    if (!allowed) expect(reason).toContain('Team execution denied')
    const events = lead.session.snapshotEvents()
    const approvals = events.filter(event => event.type === 'team/mission' && event.data.mission.status === 'approved')
    for (const event of approvals) {
      if (event.type !== 'team/mission') throw new Error('unexpected approval event')
      expect(event.data.version).toBe(3)
      expect(event.data.mission.approval?.eventId).toBeTruthy()
      expect(event.data.mission.approval?.humanSessionId).toBe(lead.id)
    }
    console.log('AUTHORIZATION_MATRIX_CELL ' + JSON.stringify({ ...cell, reachable, effects, providerRequests: h.adapter.requests.length,
      outcome: result.isError ? 'deny' : 'allow', reason, authorityDiagnostic, bindingFailure, planRejection, planRevision: view.planRevision,
      approvedPlanRevision: view.planApproval?.approvedRevision, hasTeamTools, controls }))
  })
})
