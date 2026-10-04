/** Additional DD §9 lifecycle edges. Faults use public service boundaries, never private state. */
import { describe, expect, it, vi } from 'vitest'
import { Context, symbols } from '@deepseek-ai/cordis'
import { brandString } from '@deepseek-ai/dsh-brand'
import { LocalDurableAgentProvider } from '@deepseek-ai/dsh-durable-agent'
import TeamService from '@vuhoi/gat-core'
import { boot, body, brief, declaration, signal } from './execution-harness.ts'
import { executionPlugin as prototype } from './execution-harness.ts'

function teamOwner(h: Awaited<ReturnType<typeof boot>>): TeamService {
  const scoped = h.ctx.agentTeams
  const original: unknown = Reflect.get(scoped, symbols.original) ?? scoped
  if (!(original instanceof TeamService)) throw new Error('unexpected real GAT owner')
  return original
}

describe('task memory additional lifecycle edges', () => {
  it('joins a late successful provision after withdrawal and releases its real reference', async () => {
    const h = await boot({ mode: 'hang' })
    h.provisions.mockRestore(); const provision = h.service.provision.bind(h.service)
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    const provisions = vi.spyOn(h.service, 'provision').mockImplementation(async (...args) => {
      const ref = await provision(...args); entered.resolve(); await gate.promise; return ref
    })
    const assignment = h.assign().then(value => ({ value }), error => ({ error }))
    let withdrawn = false
    let withdrawing: Promise<void> | undefined
    try {
      await entered.promise
      withdrawing = h.disposeBinding().then(() => { withdrawn = true })
      await Promise.resolve()
      expect(withdrawn).toBe(false); expect(h.releases).not.toHaveBeenCalled()
      gate.resolve(); await withdrawing
      expect(await assignment).toHaveProperty('error')
      expect(provisions).toHaveBeenCalledTimes(1); expect(h.releases).toHaveBeenCalledTimes(1)
      expect(h.reads).not.toHaveBeenCalled(); expect(h.contexts).not.toHaveBeenCalled()
      expect(h.model.requests.every(request => request.sessionId === h.member.id || request.sessionId === h.lead.id)).toBe(true)
    } finally { gate.resolve(); await assignment; await withdrawing }
  })

  it.each(['before', 'after'])('denies underlying provider replacement %s an awaited read', async timing => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const replacementCtx = new Context(); const replacement = new LocalDurableAgentProvider(replacementCtx)
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    let reading: ReturnType<typeof h.invoke> | undefined
    try {
      if (timing === 'after') {
        h.reads.mockRestore(); const read = h.service.readMemoryItem.bind(h.service)
        vi.spyOn(h.service, 'readMemoryItem').mockImplementation(async (...args) => {
          const item = await read(...args); entered.resolve(); await gate.promise; return item
        })
        reading = h.invoke(worker, 'selected'); await entered.promise
      }
      // Context.set is the public service-owner replacement seam; no Cordis private registry edits.
      h.service.ctx.set('durableAgent', replacement)
      gate.resolve()
      const result = await (reading ?? h.invoke(worker, 'selected'))
      expect(result.isError).toBe(true); expect(JSON.stringify(result.content)).not.toContain(body)
      if (timing === 'before') expect(h.reads).not.toHaveBeenCalled()
    } finally {
      gate.resolve(); if (reading !== undefined) await reading
      h.service.ctx.set('durableAgent', h.service); await replacementCtx.fiber.dispose()
    }
  })

  it('rejects a same-ID foreign Agent returned by the public registry seam', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const get = h.ctx.agents.get.bind(h.ctx.agents)
    const foreign = new Proxy(worker, {})
    const lookup = vi.spyOn(h.ctx.agents, 'get').mockImplementation(id => id === worker.id ? foreign : get(id))
    try {
      expect(foreign.id).toBe(worker.id); expect(foreign).not.toBe(worker)
      const result = await h.invoke(worker, 'selected')
      expect(result.isError).toBe(true); expect(h.reads).not.toHaveBeenCalled()
      expect(JSON.stringify(result.content)).not.toContain(body)
    } finally { lookup.mockRestore() }
  })

  it('denies replacement of the underlying registered Team service before memory access', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    const other = await boot({ mode: 'hang' }); const original = teamOwner(h); const replacement = teamOwner(other)
    expect(replacement).not.toBe(original)
    try {
      original.ctx.set('agentTeams', replacement)
      const result = await h.invoke(worker, 'selected')
      expect(result.isError).toBe(true); expect(h.reads).not.toHaveBeenCalled()
      expect(JSON.stringify(result.content)).not.toContain(body)
    } finally { original.ctx.set('agentTeams', original) }
  })

  it.each(['generation', 'task-revision'])('withholds an admitted body after public %s authority loss', async edge => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    h.reads.mockRestore(); const read = h.service.readMemoryItem.bind(h.service)
    const entered = Promise.withResolvers<void>(); const gate = Promise.withResolvers<void>()
    vi.spyOn(h.service, 'readMemoryItem').mockImplementation(async (...args) => {
      const item = await read(...args); entered.resolve(); await gate.promise; return item
    })
    const reading = h.invoke(worker, 'selected'); const team = teamOwner(h)
    let restore: (() => void) | undefined
    try {
      await entered.promise
      if (edge === 'generation') {
        const current = team.executionFor.bind(team)
        const lookup = vi.spyOn(team, 'executionFor').mockImplementation(agent => {
          const value = current(agent)
          return agent === worker && value !== undefined ? { ...value, generation: value.generation + 1 } : value
        })
        restore = () => lookup.mockRestore()
      } else {
        const current = team.getTask.bind(team)
        const lookup = vi.spyOn(team, 'getTask').mockImplementation((caller, id) => {
          const value = current(caller, id)
          return id === execution.taskId ? { ...value, revision: value.revision + 1 } : value
        })
        restore = () => lookup.mockRestore()
      }
      gate.resolve(); const result = await reading
      expect(result.isError).toBe(true); expect(JSON.stringify(result.content)).not.toContain(body)
    } finally { gate.resolve(); await reading; restore?.() }
  })

  it('binds two different members to distinct real persistent memory identities', async () => {
    const otherDeclaration = { ...declaration, name: 'other-worker' }
    const h = await boot({ mode: 'hang', bindingFactory: cfg => prototype({ ...cfg,
      members: [...cfg.members, { declaration: otherDeclaration, mode: 'task' }] }) })
    const seed = await h.service.provision(h.workspace, otherDeclaration)
    await h.service.commitMemoryItem(seed, { item: { id: 'selected', title: 'other catalog',
      retrievalCondition: 'other task intent', content: 'OTHER_MEMBER_MEMORY' },
      authorization: { kind: 'authorized-host-workflow', authorizationRef: 'disposable-distinct-member-seed' } })
    await h.service.release(seed)
    const other = (await h.ctx.agentTeams.spawnTeammate(h.lead, { name: otherDeclaration.name,
      description: otherDeclaration.description, provider: 'spawn', context: 'fresh',
      prompt: [{ type: 'text', text: 'other bootstrap role' }], signal })).member
    await vi.waitFor(() => expect(h.ctx.agents.get(other.id)).toBeUndefined())
    const task = await h.ctx.agentTeams.createTask(h.lead, { subject: 'other task', description: 'other memory intent' })
    const first = await h.assign(); const firstWorker = await h.live(first.sessionId)
    const second = await h.ctx.agentTeams.assignTask(h.lead, { requestId: brandString('other-request'),
      member: other.name, taskId: task.id, expectedRevision: task.revision,
      brief: brief([{ reference: 'durable-memory:selected' }]), signal })
    const secondWorker = await h.live(second.sessionId)
    const one = await h.invoke(firstWorker, 'selected'); const two = await h.invoke(secondWorker, 'selected')
    expect(one.isError).toBe(false); expect(two.isError).toBe(false)
    expect(JSON.stringify(one.content)).toContain(body); expect(JSON.stringify(one.content)).not.toContain('OTHER_MEMBER_MEMORY')
    expect(JSON.stringify(two.content)).toContain('OTHER_MEMBER_MEMORY'); expect(JSON.stringify(two.content)).not.toContain(body)
    expect(first.memberId).not.toBe(second.memberId)
    await h.ctx.agentTeams.cancelExecution(h.lead, first.id); await h.ctx.agentTeams.cancelExecution(h.lead, second.id)
  })

  it('real ordinary submission settles after binding release without accepting the task', async () => {
    const h = await boot({ mode: 'hang' }); const execution = await h.assign(); const worker = await h.live(execution.sessionId)
    await h.ctx.agentTeams.submitExecution(worker, execution.id, 'completed', 'Self-contained provisional output')
    await vi.waitFor(() => expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).phase).toBe('completed'))
    expect(h.releases).toHaveBeenCalledTimes(1); expect(h.ctx.agents.get(worker.id)).toBeUndefined()
    expect((await h.invoke(worker, 'selected')).isError).toBe(true)
    expect(h.ctx.agentTeams.getTask(h.lead, execution.taskId).status).toBe('in_progress')
    expect(h.ctx.agentTeams.getExecution(h.lead, execution.id).result).toBe('Self-contained provisional output')
  })
})
