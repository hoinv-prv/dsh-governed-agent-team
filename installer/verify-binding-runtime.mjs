#!/usr/bin/env node
/** Plain-Node actual Loader/profile lifecycle qualification in private temporary storage. */
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { createServer } from 'node:http'
import { mkdtemp, readFile, realpath, rm, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { pathToFileURL, fileURLToPath } from 'node:url'

const host = await realpath(resolve(process.argv[2] ?? ''))
const reportPath = process.argv[3] && resolve(process.argv[3])
const requireHost = createRequire(join(host, 'package.json'))
const modules = new Map()
const loaded = {}
function resolveImport(name) {
  const url = execFileSync(process.execPath, ['--input-type=module', '--eval',
    'process.stdout.write(import.meta.resolve(process.argv[1]))', name], { cwd: host, encoding: 'utf8' })
  return fileURLToPath(url)
}
async function load(name) {
  const path = await realpath(resolveImport(name))
  if (!path.startsWith(`${host}/`)) throw new Error(`built workspace module escaped selected target: ${name}`)
  loaded[name] = { path, sha256: createHash('sha256').update(await readFile(path)).digest('hex') }
  const module = await import(pathToFileURL(path).href)
  modules.set(name, module)
  return module
}
const { Context, symbols } = await load('@deepseek-ai/cordis')
const { default: Loader } = await load('@deepseek-ai/cordis-plugin-loader')
const { default: Include } = await load('@deepseek-ai/cordis-plugin-include')
const { default: AgentLoop } = await load('@deepseek-ai/dsh-agent-loop')
const { mountAgentLoopTestDependencies } = await load('@deepseek-ai/dsh-agent-loop-testkit')
const { LlmAdapter } = await load('@deepseek-ai/dsh-llm')
const { default: Persistence } = await load('@deepseek-ai/dsh-session-persistence-jsonl')
const { default: Query } = await load('@deepseek-ai/dsh-session-query')
const { SessionLogOffset } = await load('@deepseek-ai/dsh-session')
const { default: Subagents } = await load('@deepseek-ai/dsh-subagent')
const Spawn = await load('@deepseek-ai/dsh-subagent-spawn-in-process')
const Fork = await load('@deepseek-ai/dsh-subagent-fork-in-process')
const Connection = await load('@deepseek-ai/dsh-client-connection')
const { default: Gateway } = await load('@deepseek-ai/dsh-api-gateway')
const { default: TypertRegistry } = await load('@deepseek-ai/dsh-typert-registry')
const { loadOptionalPatches } = await load('@deepseek-ai/dsh-app-boot')
for (const name of ['@vuhoi/gat-core', '@vuhoi/gat-tools', '@vuhoi/gat-durable-agent/provider', '@vuhoi/gat-durable-agent/composition', '@deepseek-ai/dsh-durable-agent/service', '@deepseek-ai/dsh-durable-agent/consumer']) await load(name)
const profilePath = requireHost.resolve('@vuhoi/gat-durable-profile/cordis.patch.yml')
const signal = new AbortController().signal
const temporary = await mkdtemp(join(tmpdir(), 'gat-built-binding-'))
const workspace = await realpath(join(temporary))
const storage = await mkdtemp(join(tmpdir(), 'gat-built-sessions-'))
const owners = []
const cases = []
function cut(source, header, events) {
  const lease = () => ({ source, header, inheritedEventCount: SessionLogOffset(0), events,
    cursor: events.at(-1)?.seq ?? -1, retain: lease, [Symbol.dispose]() {} })
  return lease()
}
class TestQuery extends Query {
  static inject = ['sessions', 'sessionPersistence']
  async observeSession(id) {
    const live = this.ctx.sessions.get(id)
    if (live) return cut('live', live.header, live.snapshotEvents())
    const handle = await this.ctx.sessionPersistence.open(id, 'read')
    try { return cut('prepared', handle.header, (await handle.read()).events) } finally { await handle.close() }
  }
  async searchSessions() { throw new Error('unused qualification search') }
  async searchEvents() { throw new Error('unused qualification search') }
}
class Adapter extends LlmAdapter {
  requests = []
  async resolveModel(provider, model) { return { provider, id: model, name: model } }
  async *stream(options) {
    this.requests.push(options)
    const own = this.requests.filter(request => request.model === 'worker-mock')
    if (options.model === 'worker-mock' && this.firstRead && own.length === 1) {
      const args = JSON.stringify({ itemId: 'rule' })
      yield { type: 'block-start', index: 0, blockType: 'tool-call' }
      yield { type: 'tool-call-delta', index: 0, id: 'built-read', name: 'durable_agent_read_memory', argumentsDelta: args }
      yield { type: 'block-end', index: 0, block: { type: 'tool-call', id: 'built-read', name: 'durable_agent_read_memory', arguments: args } }
      yield { type: 'usage', usage: { inputTokens: 1, outputTokens: 1 } }
      yield { type: 'finish', reason: { kind: 'tool-calls' } }
      return
    }
    yield { type: 'block-start', index: 0, blockType: 'text' }
    yield { type: 'text-delta', index: 0, text: 'waiting' }
    await new Promise((_, reject) => {
      if (options.signal?.aborted) reject(new Error('aborted'))
      else options.signal?.addEventListener('abort', () => reject(new Error('aborted')), { once: true })
    })
  }
}
async function until(check) {
  const end = Date.now() + 5000
  while (true) {
    try { check(); return } catch (error) { if (Date.now() >= end) throw error }
    await new Promise(resolveWait => setTimeout(resolveWait, 10))
  }
}
async function boot(firstRead) {
  const ctx = new Context()
  const routes = []
  const credentials = new Map()
  ctx.provide('credentials', { async modifyRecord(key, mutate) {
    const current = credentials.get(key), next = await mutate(current)
    if (next !== undefined) credentials.set(key, next)
    return next ?? current
  } })
  ctx.provide('webServer', { register(route) { routes.push(route); return () => {} }, tapIndex: () => () => {}, port: 0 })
  await ctx.plugin({ inject: [...Connection.inject], apply: Connection.apply })
  await ctx.plugin(TypertRegistry)
  await ctx.plugin(Gateway)
  const server = createServer((req, res) => { void routes.find(route => route.path === '/api').handler(req, res) })
  await new Promise(resolveListen => server.listen(0, '127.0.0.1', resolveListen))
  const origin = `http://127.0.0.1:${server.address().port}`
  const url = new URL(ctx.connection.authenticatedUrl(origin))
  let cookie
  ctx.connection.authorizeIndex({ method: 'GET', url: url.pathname + url.search, headers: { host: url.host } }, {
    writeHead(_status, headers) { cookie = headers?.['set-cookie']?.split(';', 1)[0] ?? '' }, end() {},
  })
  let closed = false
  const close = async () => {
    if (closed) return
    closed = true
    try { await ctx.fiber.dispose() } finally {
      server.closeAllConnections()
      await new Promise((yes, no) => server.close(error => error ? no(error) : yes()))
    }
  }
  owners.push(close)
  const requestControl = async (method, leadId, request, authenticated = true) => {
    return await fetch(`${origin}/api/agentTeams/${method}`, { method: 'POST', headers: { 'content-type': 'application/json', ...(authenticated ? { cookie } : {}) },
      body: JSON.stringify({ type: 'client-request', rpcId: 'built-control', method: `agentTeams/${method}`, payload: { args: { agentId: leadId, ...(request === undefined ? {} : { request }) } } }) })
  }
  const call = async (method, leadId, request) => {
    const response = await requestControl(method, leadId, request)
    assert.equal(response.status, 200)
    const result = (await response.json()).result
    assert.equal(result.ok, true, JSON.stringify(result))
    if (result.value?.ok !== undefined) assert.equal(result.value.ok, true, JSON.stringify(result.value))
    return result.value
  }
  await mountAgentLoopTestDependencies(ctx)
  await ctx.plugin(Persistence, { root: storage })
  await ctx.plugin(TestQuery)
  await ctx.plugin(AgentLoop, { agents: [] })
  await ctx.plugin(Subagents)
  await ctx.plugin(Spawn, { providerName: 'spawn' })
  await ctx.plugin(Fork, { providerName: 'fork' })
  for (const name of ['ask_user_question', 'glob', 'grep', 'read', 'read_image']) ctx.tools.register({ name,
    description: 'Host inspection fixture', parameters: { type: 'object', properties: {} }, capabilities: ['team-inspection'],
    execute: async () => ({}), output: { schema: {}, render: () => [] } })
  await ctx.plugin(Loader)
  ctx.loader.builtins.include = Include
  const imports = []
  ctx.loader.internal = { version: 'v2', async import(name) { imports.push(name); return await load(name) } }
  const base = join(storage, 'cordis.yml')
  await writeFile(base, '- id: agent-team\n  name: "@vuhoi/gat-core"\n- id: tool-agent-team\n  name: "@vuhoi/gat-tools"\n')
  await ctx.loader.create({ name: 'cordis:include', config: { path: pathToFileURL(base).href,
    patches: loadOptionalPatches('built-durable', profilePath) } })
  await ctx.loader.await()
  assert.deepEqual(imports, ['@vuhoi/gat-core', '@vuhoi/gat-tools', '@vuhoi/gat-durable-agent/provider', '@vuhoi/gat-durable-agent/composition'])
  const adapter = new Adapter()
  adapter.firstRead = firstRead
  ctx.llm.registerAdapter(['mock'], adapter)
  const registered = ctx.get('durableAgent'), service = Reflect.get(registered, symbols.original) ?? registered
  const refs = []
  const provision = service.provision.bind(service)
  service.provision = async (...args) => { const ref = await provision(...args); refs.push(ref); return ref }
  return { ctx, call, requestControl, close, adapter, service, refs }
}
try {
  await writeFile(join(workspace, 'team_members.durable.yaml'), JSON.stringify({ version: 1, members: ['worker', 'reviewer'].map(name => ({
    name, description: 'Controlled member', prompt: 'Assigned initial work', context: 'fresh', provider: 'mock', model: 'worker-mock', durable: { scope: 'workspace' },
  })) }))
  const first = await boot(true)
  const lead = await first.ctx.agentLoop.create('built-lead', { provider: 'mock', model: 'lead-mock' }, { cwd: workspace })
  await assert.rejects(first.ctx.agentTeams.enable(lead, signal), error => error.code === 'TEAM_HUMAN_CONTROL_REQUIRED')
  const unauthenticated = await first.requestControl('enable', lead.id, undefined, false)
  assert.equal(unauthenticated.status, 401)
  assert.equal(first.refs.length, 0)
  assert.equal(first.adapter.requests.length, 0)
  await first.call('enable', lead.id)
  const row = first.ctx.agentTeams.remoteView(lead).members.find(member => member.name === 'worker')
  assert.deepEqual(row.bindings, [{ binderId: 'durable-agent', protocolVersion: 1, readiness: 'ready' }])
  const child = first.ctx.agents.get(row.id)
  await assert.rejects(first.ctx.agentTeams.activateMember(child, signal))
  assert.equal(first.adapter.requests.length, 0)
  cases.push('quarantined Loader/profile enable before first request')
  const mission = await first.ctx.agentTeams.createMission(lead, { title: 'Built mission', objective: 'Controlled qualification' })
  const task = await first.ctx.agentTeams.createTask(lead, { missionId: mission.id, subject: 'Work', description: 'Exact task' })
  const current = first.ctx.agentTeams.getMission(lead, mission.id)
  const staleResponse = await first.requestControl('approveMission', lead.id, { missionId: current.id, expectedRevision: current.revision + 1 })
  assert.equal(staleResponse.status, 200)
  const staleResult = (await staleResponse.json()).result
  assert.equal(staleResult.ok, true)
  assert.equal(staleResult.value.ok, false)
  assert.equal(staleResult.value.error.code, 'team-mission-conflict')
  await assert.rejects(first.ctx.agentTeams.activateMember(child, signal))
  assert.equal(first.adapter.requests.length, 0)
  cases.push('receipt-free and unauthenticated Enable denied; authenticated wrong-revision approval denies release')
  await first.call('approveMission', lead.id, { missionId: current.id, expectedRevision: current.revision })
  await first.ctx.agentTeams.updateTask(child, { taskId: task.id, expectedRevision: task.revision, action: 'claim' })
  first.ctx.agentTeams.bindExecution(lead, { missionId: current.id, expectedRevision: current.revision })
  first.ctx.agentTeams.bindExecution(child, { missionId: current.id, expectedRevision: current.revision, taskId: task.id })
  const commit = (service, ref, id, title) => service.commitMemoryItem(ref, { item: { id, title, retrievalCondition: 'During qualification', content: 'Independent stored evidence' }, authorization: { kind: 'human', authorizationRef: 'isolated-host-approval' } })
  await commit(first.service, first.refs[0], 'rule', 'First catalog')
  const readMemory = first.service.readMemoryItem.bind(first.service)
  let changed = false
  first.service.readMemoryItem = async (...args) => {
    const value = await readMemory(...args)
    if (!changed) { changed = true; await commit(first.service, first.refs[0], 'later', 'Second catalog') }
    return value
  }
  await first.ctx.agentTeams.activateMember(child, signal)
  await until(() => assert.equal(first.adapter.requests.filter(request => request.model === 'worker-mock').length, 2))
  const requests = first.adapter.requests.filter(request => request.model === 'worker-mock')
  assert.match(JSON.stringify(requests[0].messages), /First catalog/u)
  assert.match(JSON.stringify(requests[1].messages), /Second catalog/u)
  const readTool = requests[0].tools.find(tool => tool.name === 'durable_agent_read_memory')
  assert.equal(readTool.parameters.properties.itemId.type, 'string')
  const candidate = await child.ctx.tools.execute({ agent: child, name: 'durable_agent_submit_candidate', callId: 'built-candidate', signal,
    arguments: { title: 'Possible rule', retrievalCondition: 'During work', content: 'candidate only', provenance: 'isolated qualification', confidence: 'medium', limitations: [] } })
  assert.equal(candidate.isError, false, JSON.stringify(candidate))
  assert.match(JSON.stringify(candidate), /unconfirmed/u)
  const wireView = await first.call('view', lead.id)
  const serializedView = JSON.stringify(wireView)
  assert.ok(!serializedView.includes('serviceBindingKey'))
  assert.ok(!serializedView.includes('workspaceRealpath'))
  assert.ok(!serializedView.includes(first.refs[0]))
  assert.ok(wireView.members.some(member => member.bindings?.some(binding => binding.readiness === 'ready')))
  cases.push('actual pre-render refresh twice, executable schema and unconfirmed candidate')
  const childId = child.id
  await first.close()
  await writeFile(join(workspace, 'team_members.durable.yaml'), 'invalid: changed after enable\n')
  const second = await boot(false)
  const handle = await second.ctx.agents.resume({ resumeSessionId: lead.id, agentOptions: { provider: 'mock', model: 'lead-mock' } })
  const restoredLead = handle.agent
  second.ctx.agentTeams.bindExecution(restoredLead, { missionId: current.id, expectedRevision: current.revision })
  await second.ctx.agentTeams.sendMessage(restoredLead, { target: 'worker', content: [{ type: 'text', text: 'Recovered followup' }], signal })
  const recovered = await second.ctx.agentTeams.recoverMember(restoredLead, 'worker', { missionId: current.id, expectedRevision: current.revision, taskId: task.id }, signal)
  assert.equal(recovered.id, childId)
  await until(() => assert.equal(second.adapter.requests.filter(request => request.model === 'worker-mock').length, 1))
  assert.match(JSON.stringify(second.adapter.requests.find(request => request.model === 'worker-mock').messages), /Recovered followup/u)
  const kept = await recovered.ctx.tools.execute({ agent: recovered, name: 'durable_agent_read_memory', callId: 'built-kept', signal, arguments: { itemId: 'rule' } })
  assert.equal(kept.isError, false, JSON.stringify(kept))
  assert.match(JSON.stringify(kept), /Independent stored evidence/u)
  const stored = await second.ctx.sessionPersistence.open(childId, 'read')
  try { assert.equal((await stored.read()).events.filter(event => event.type === 'subagent/initial-admission' && event.data.kind === 'persisted').length, 1) } finally { await stored.close() }
  cases.push('public provider restart, persisted records, queued recovery, one initial admission without YAML reread')
  const originalRead = second.service.readMemoryItem.bind(second.service)
  let finishRead, enteredRead = false
  const readGate = new Promise(resolveGate => { finishRead = resolveGate })
  second.service.readMemoryItem = async (...args) => { enteredRead = true; await readGate; return await originalRead(...args) }
  const pendingRead = recovered.ctx.tools.execute({ agent: recovered, name: 'durable_agent_read_memory', callId: 'built-denied', signal, arguments: { itemId: 'rule' } })
  await until(() => assert.equal(enteredRead, true))
  await second.call('revokeMission', restoredLead.id, { missionId: current.id, expectedRevision: current.revision })
  finishRead()
  const denied = await pendingRead
  assert.equal(denied.isError, true)
  assert.equal(second.ctx.agentTeams.remoteView(restoredLead).members.find(member => member.id === childId).bindings[0].readiness, 'unavailable')
  cases.push('revoked exact authority withholds memory and withdraws required readiness')
  const nativeArtifacts = {}
  for (const path of [resolveImport('@deepseek-ai/node-addon-system/flock'), join(host, 'native/system/packages/linux-x64/bin/glibc/system.node')]) {
    const exact = await realpath(path)
    assert.ok(exact.startsWith(`${host}/`), 'native artifact must belong to selected target')
    nativeArtifacts[exact] = createHash('sha256').update(await readFile(exact)).digest('hex')
  }
  const report = { result: 'PASS', target: host, cases, loadedModules: loaded, profile: { path: profilePath, sha256: createHash('sha256').update(await readFile(profilePath)).digest('hex') },
    nativeArtifacts,
    topology: 'private temporary storage, dedicated provider, one host at a time; deployment separately authorized' }
  if (reportPath) await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n')
  process.stdout.write(JSON.stringify({ result: report.result, cases: cases.length, loadedModules: Object.keys(loaded).length }) + '\n')
} finally {
  for (const close of owners.reverse()) await close()
  await rm(temporary, { recursive: true, force: true })
  await rm(storage, { recursive: true, force: true })
}
