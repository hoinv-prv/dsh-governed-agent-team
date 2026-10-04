import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { readFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve, join } from 'node:path'
import { pathToFileURL } from 'node:url'
const root = '/home/hoinv/work/dsh-binding-prerequisites'
const imports = []
async function owner(path) {
  const manifest = resolve(root, path, 'package.json')
  const name = JSON.parse(readFileSync(manifest, 'utf8')).name
  const entry = createRequire(manifest).resolve(name)
  assert(entry.includes('/lib/'), entry)
  assert(!entry.includes('/src/'), entry)
  imports.push({ name, entry })
  return import(pathToFileURL(entry).href)
}
const { Context } = await owner('vendor/cordis')
const { mountAgentLoopTestDependencies } = await owner('packages/test-support/agent-loop-testkit')
const { default: AgentLoop } = await owner('packages/core/agent-loop')
const { default: Persistence } = await owner('packages/session/session-persistence-jsonl')
const { default: Subagents } = await owner('packages/subagent/subagent')
const Spawn = await owner('packages/subagent/subagent-spawn-in-process')
const { SessionId } = await owner('packages/core/session')
const { LlmAdapter, ToolCallId } = await owner('packages/llm/llm')
const { defineTool, EXTERNAL_DELEGATION } = await owner('packages/core/tools')
const { default: TeamService } = await owner('packages/experimental/gat-core')
const TeamTools = await owner('packages/experimental/gat-tools')
const dir = mkdtempSync(join(tmpdir(), 'gat-built-api-'))
const ctx = new Context()
let requests = 0
try {
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(Persistence, { root: dir })
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(Subagents)
  await ctx.plugin(Spawn, { providerName: 'spawn' })
  class Adapter extends LlmAdapter {
    resolveModel(provider, model) { return Promise.resolve({ provider, id: model, name: model }) }
    async *stream() { requests += 1; yield { type: 'block-start', index: 0, blockType: 'text' }; yield { type: 'text-delta', index: 0, text: 'done' }; yield { type: 'block-end', index: 0, block: { type: 'text', text: 'done' } }; yield { type: 'usage', usage: { inputTokens: 1, outputTokens: 1 } }; yield { type: 'finish', reason: { kind: 'stop' } } }
  }
  ctx.llm.registerAdapter(['mock'], new Adapter())
  const lead = await ctx.agentLoop.create(SessionId('public-built-parent'), { provider: 'mock', model: 'mock' }, { cwd: dir })
  const signal = new AbortController().signal
  const reserved = await ctx.subagents.materializeContinuable({ provider: 'spawn', label: 'built child', request: { parent: lead }, signal })
  assert.equal(requests, 0)
  assert.equal(reserved.agent.inbox.nextTurn.length, 0)
  const content = [{ type: 'text', text: 'one admitted initial item' }]
  const id = await reserved.persistInitialPrompt(content, 'built-key', signal)
  assert.equal(await reserved.persistInitialPrompt(content, 'built-key', signal), id)
  assert.equal(requests, 0)
  let refreshes = 0
  reserved.agent.ctx.on('agent/prepare-prompt', async () => { await Promise.resolve(); refreshes += 1; reserved.agent.ctx.systemPrompt.section({ name: 'built-fresh', text: 'built refreshed context', order: 200 }) })
  await reserved.activate(signal)
  await reserved.agent.whenIdle()
  assert.equal(requests, 1)
  assert.equal(refreshes, 1)
  await reserved.dispose()
  await ctx.plugin(TeamService)
  await ctx.plugin(TeamTools, { simpleMode: true, minExecutionMembers: 1 })
  const mission = await ctx.agentTeams.createMission(lead, { title: 'built draft', objective: 'must not self-authorize' })
  const task = await ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'built canonical task', description: 'exact association' })
  assert.equal(task.missionId, mission.id)
  assert.throws(() => ctx.agentTeams.bindExecution(lead, { missionId: mission.id, expectedRevision: mission.revision }))
  assert.throws(() => ctx.agentTeams.assertExecution(lead))
  let effects = 0
  ctx.tools.register(defineTool({ name: 'built-effect', description: 'built effect', parameters: {}, capabilities: [EXTERNAL_DELEGATION], output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] }, execute: async () => { effects += 1; return 'effect' } }))
  const remove = ctx.tools.guard(exec => exec.capabilities.includes(EXTERNAL_DELEGATION) ? 'built denial' : undefined)
  const result = await ctx.tools.execute({ name: 'built-effect', arguments: {}, agent: lead, signal, callId: ToolCallId('built-denied') })
  assert.equal(result.isError, true)
  assert.equal(effects, 0)
  remove()
  console.log(JSON.stringify({ status: 'PASS', imports, observations: { requests, refreshes, effects, canonicalTask: true, draftLeaseDenied: true } }, null, 2))
} finally {
  await ctx.fiber.dispose()
  rmSync(dir, { recursive: true, force: true })
}
