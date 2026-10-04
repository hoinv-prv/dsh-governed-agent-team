import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import AgentLoop from '@deepseek-ai/dsh-agent-loop'
import { mountAgentLoopTestDependencies } from '@deepseek-ai/dsh-agent-loop-testkit'
import { SessionId } from '@deepseek-ai/dsh-session'
import JsonlSessionPersistence from '@deepseek-ai/dsh-session-persistence-jsonl'
import SubagentService from '@deepseek-ai/dsh-subagent'
import * as SubagentSpawn from '@deepseek-ai/dsh-subagent-spawn-in-process'
import { MockAdapter } from '../../../core/agent-loop/tests/mock-adapter.ts'
import TeamService from '../src/index.ts'
import type { TeamMemberSpec } from '../src/index.ts'
import { TestSessionQuery } from './test-session-query.ts'

describe('normalized initializer full-roster preflight', () => {
  it('creates no member rows or child Agents when any later spec fails', async () => {
    const root = await mkdtemp(join(tmpdir(), 'gat-initializer-preflight-'))
    const ctx = new Context()
    try {
      await mountAgentLoopTestDependencies(ctx)
      await ctx.plugin(JsonlSessionPersistence, { root })
      await ctx.plugin(TestSessionQuery)
      await ctx.plugin(AgentLoop, { agents: [] })
      await ctx.plugin(SubagentService)
      await ctx.plugin(SubagentSpawn, { providerName: 'spawn' })
      await ctx.plugin(TeamService)
      const adapter = new MockAdapter(['hang'])
      ctx.llm.registerAdapter(['mock'], adapter)
      const lead = await ctx.agentLoop.create(SessionId('preflight-lead'), { provider: 'mock', model: 'mock' })
      const good: TeamMemberSpec = {
        name: 'first', description: 'First', initialTask: [{ type: 'text', text: 'Wait' }],
        context: 'fresh', continuationProvider: 'spawn', agentOptions: { provider: 'mock', model: 'mock' }, attachments: [],
      }
      const badSpecs: unknown[] = [
        { ...good, name: 'second', initialTask: [{ type: 'text', text: 7 }] },
        { ...good, name: 'first' },
        { ...good, name: { toString: () => 'second' } },
        { ...good, name: 'second', continuationProvider: 'absent' },
        { ...good, name: 'second', agentOptions: { provider: 'absent', model: 'mock' } },
        { ...good, name: 'second', attachments: [{ binderId: 'required', protocolVersion: 1, required: true, payload: null }] },
      ]
      for (const second of badSpecs) {
        const unregister = ctx.agentTeams.registerInitializer(async () => ({ source: 'fixture', diagnostics: [], members: [good, second as TeamMemberSpec] }))
        await expect(ctx.agentTeams.enable(lead, new AbortController().signal)).rejects.toThrow()
        expect(ctx.agentTeams.remoteView(lead).members).toHaveLength(1)
        expect(lead.session.snapshotEvents().filter(event => event.type === 'team/member')).toHaveLength(0)
        expect(ctx.agents.list()).toEqual([lead])
        unregister()
      }
      expect(adapter.requests).toHaveLength(0)
    } finally {
      await ctx.fiber.dispose()
      await rm(root, { recursive: true, force: true })
    }
  })
})
