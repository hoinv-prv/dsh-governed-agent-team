import { afterEach, describe, expect, it, vi } from 'vitest'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SessionQueryEngine from '@deepseek-ai/dsh-session-query'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as SubagentFork from '@deepseek-ai/dsh-subagent-fork-in-process'
import * as SubagentSpawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { MockAdapter } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../../gat-core/src/index.ts'
import type { TeamMemberView, TeamView } from '../../gat-core/src/types.ts'
import * as toolTeam from '../src/index.ts'
import { initializeAuthorizedFixture, humanAction } from '../../gat-core/tests/authorized-team-fixture.ts'

const roots: string[] = []
let callNumber = 0

class TestSessionQuery extends SessionQueryEngine {
  override searchSessions(): Promise<never> { return Promise.reject(new Error('not configured')) }
  override searchEvents(): Promise<never> { return Promise.reject(new Error('not configured')) }
}

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

async function setup() {
  const ctx = new Context()
  await initializeAuthorizedFixture(ctx)
  await mountAgentLoopTestDependencies(ctx)
  const storageRoot = mkdtempSync(join(tmpdir(), 'dsh-binding-view-'))
  roots.push(storageRoot)
  await ctx.plugin(JsonlSessionPersistence, { root: storageRoot })
  await ctx.plugin(TestSessionQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(SubagentService)
  await ctx.plugin(SubagentSpawn, { providerName: 'spawn' })
  await ctx.plugin(SubagentFork, { providerName: 'fork' })
  await ctx.plugin(TeamService)
  await ctx.plugin(toolTeam, { simpleMode: true, minExecutionMembers: 1, maxExecutionMembers: 1 })
  ctx.llm.registerAdapter(['mock'], new MockAdapter(['hang']))
  const lead = await ctx.agentLoop.create(
    SessionId('binding-view-lead'),
    { provider: 'mock', model: 'mock' },
    { cwd: storageRoot },
  )
  return { ctx, lead, storageRoot }
}

function execute(ctx: Context, agent: Agent, name: string) {
  return ctx.tools.execute({
    callId: ToolCallId(`binding-view-${++callNumber}`),
    name,
    arguments: {},
    signal: new AbortController().signal,
    agent,
  })
}

function resultText(result: Awaited<ReturnType<typeof execute>>): string {
  return result.content.flatMap(block => block.type === 'text' ? [block.text] : []).join('')
}

describe('member binding readiness views', () => {
  it('exposes only safe binding summaries and excludes unavailable or failed bindings from readiness', async () => {
    const { ctx, lead, storageRoot } = await setup()
    writeFileSync(join(storageRoot, 'team_members.yaml'), `version: 1
members:
  - name: baseline-worker
    description: Baseline member for safe binding summaries.
    prompt: Stay available.
`)
    await humanAction(ctx, lead, 'enable')
    const base = ctx.agentTeams.remoteView(lead)
    const leadView = base.members.find(member => member.role === 'lead')!
    let teammate: TeamMemberView = {
      id: SessionId('binding-view-member'),
      name: 'bound-worker',
      role: 'teammate',
      status: 'idle',
      diagnostics: [],
      bindings: [{ binderId: 'durable-memory', protocolVersion: 1, readiness: 'unavailable' }],
    }
    const currentView = (): TeamView => ({ ...base, enabled: true, members: [leadView, teammate] })
    vi.spyOn(ctx.agentTeams, 'remoteView').mockImplementation(() => currentView())
    vi.spyOn(ctx.agentTeams, 'listMembers').mockImplementation(() => [leadView, teammate])

    for (const readiness of ['unavailable', 'failed', 'ready'] as const) {
      teammate = {
        ...teammate,
        bindings: [{ binderId: 'durable-memory', protocolVersion: 1, readiness }],
      }

      const roster = await execute(ctx, lead, 'list_agents')
      expect(roster.isError).toBe(false)
      const rows = JSON.parse(resultText(roster)) as TeamMemberView[]
      expect(rows[1]?.bindings).toEqual([{ binderId: 'durable-memory', protocolVersion: 1, readiness }])
      expect(Object.keys(rows[1]!.bindings![0]!).sort()).toEqual(['binderId', 'protocolVersion', 'readiness'])

      const taskList = await execute(ctx, lead, 'team_task_list')
      expect(taskList.isError).toBe(false)
      const output = JSON.parse(resultText(taskList)) as { preflight: { durableActiveTeammates: number } }
      expect(output.preflight.durableActiveTeammates).toBe(readiness === 'ready' ? 1 : 0)
    }
  })
})
