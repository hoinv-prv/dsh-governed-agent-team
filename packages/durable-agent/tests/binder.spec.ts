import { mkdtemp, realpath, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import { LocalDurableAgentProvider } from '@deepseek-ai/dsh-durable-agent'
import type { DurableAgentMemoryCandidateInput, DurableAgentMemoryItem, DurableAgentRef, DurableAgentService, DurableAgentTaskContext } from '@deepseek-ai/dsh-durable-agent/service'
import type { BinderBindInput, BinderPrepareInput, CapabilityContribution, JsonValue, MemberCapabilityScope } from '@vuhoi/gat-core'
import { createDurableAgentBinder } from '../src/binder.ts'
import type { DurableBinderComposition } from '../src/binder.ts'

function barrier<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>(yes => { resolve = yes })
  return { promise, resolve }
}

const workspaces: string[] = []
afterEach(async () => {
  await Promise.all(workspaces.splice(0).map(workspace => rm(workspace, { recursive: true, force: true })))
})

async function fixture() {
  const workspace = await realpath(await mkdtemp(join(tmpdir(), 'gat-durable-binding-')))
  workspaces.push(workspace)
  const ref = 'private-service-ref' as DurableAgentRef
  let revision = 1
  let current = true
  let authorized = true
  const actions: string[] = []
  const contributions = new Map<string, CapabilityContribution>()
  const hooks = new Set<() => Promise<void>>()
  let installed: CapabilityContribution | undefined
  const scope: MemberCapabilityScope = {
    isCurrent: () => current,
    authorize: vi.fn(action => { actions.push(action); if (!authorized) throw new Error('host lease revoked') }),
    install: vi.fn(contribution => { installed = contribution; contributions.set(contribution.key, contribution); return vi.fn(() => { contributions.delete(contribution.key) }) }),
    beforeRequest: vi.fn(refresh => { hooks.add(refresh); return vi.fn(() => { hooks.delete(refresh) }) }),
    replacePrompt: vi.fn((key, prompt) => { const old = contributions.get(key); if (!old) throw new Error('missing contribution'); contributions.set(key, { ...old, prompt }) }),
  }
  const declaration = { name: 'worker-one', description: 'Review approved source', prompt: 'Review the approved source.', context: 'fresh' as const, provider: 'provider-one', model: 'model-one', scope: 'workspace' as const }
  const context = (): DurableAgentTaskContext => ({
    member: { ref, name: declaration.name, description: declaration.description },
    guidance: `Guidance revision ${revision}`, memoryCatalog: [{ id: 'memory-one', title: 'A known fact', retrievalCondition: 'When reviewing' }],
    revision, provenance: { scope: 'workspace', provider: 'fake-provider', generation: `provider-generation-${revision}` },
    capabilities: { selectiveMemoryRead: true, memoryCandidateSubmission: true, approvedMemoryCommit: true, workingArtifacts: true },
  })
  const item: DurableAgentMemoryItem = { id: 'memory-one', title: 'A known fact', retrievalCondition: 'When reviewing', content: 'Selected private body', revision: 1 }
  const service = {
    apiVersion: 1,
    features: { selectiveMemoryRead: true, memoryCandidateSubmission: true, approvedMemoryCommit: true, workingArtifacts: true },
    validateDeclaration: vi.fn(async () => {}),
    provision: vi.fn(async () => ref),
    openTaskContext: vi.fn(async () => context()),
    readMemoryItem: vi.fn(async () => item),
    submitMemoryCandidate: vi.fn(async (_ref: DurableAgentRef, candidate: DurableAgentMemoryCandidateInput) => ({ candidateId: 'candidate-one', status: 'unconfirmed' as const, title: candidate.title, retrievalCondition: candidate.retrievalCondition, provenance: candidate.provenance, confidence: candidate.confidence, limitations: candidate.limitations })),
    commitMemoryItem: vi.fn(async () => { throw new Error('host-only commit must not be called') }),
    workingLocation: vi.fn(async () => { throw new Error('host-only location must not be called') }),
    release: vi.fn(async () => {}),
  }
  let selected: DurableAgentService | undefined = service as unknown as DurableAgentService
  const composition: DurableBinderComposition = {
    serviceBindingKey: 'dedicated-wk-service', service: service as unknown as DurableAgentService,
    dedicatedProvider: true, singleHostWorkspace: true,
    resolveService: () => selected,
    resolveWorkspace: vi.fn(async () => workspace),
  }
  const input: BinderPrepareInput = {
    teamId: 'team-one', memberId: 'child-one', memberName: 'worker-one', generation: 'generation-one', workspaceRealpath: workspace,
    spec: { name: declaration.name, description: declaration.description, initialTask: [{ type: 'text', text: declaration.prompt }], context: 'fresh', continuationProvider: 'spawn', agentOptions: { provider: declaration.provider, model: declaration.model } },
    payload: { schemaVersion: 1, serviceBindingKey: composition.serviceBindingKey, workspaceRealpath: workspace, declaration },
  }
  const bindInput: BinderBindInput = { teamId: input.teamId, memberId: input.memberId, memberName: input.memberName, generation: input.generation, workspaceRealpath: workspace, scope }
  const binder = createDurableAgentBinder(composition)
  const bound = async () => {
    const prepared = await binder.prepare(input, new AbortController().signal)
    const binding = await binder.bind(bindInput, prepared.attachment, prepared.value, new AbortController().signal)
    return { prepared, binding, contribution: installed! }
  }
  return {
    workspace, ref, service, composition, binder, input, bindInput, scope, actions, contributions, hooks, context, item, bound,
    setRevision: (value: number) => { revision = value }, setCurrent: (value: boolean) => { current = value }, setAuthorized: (value: boolean) => { authorized = value },
    replaceService: () => { selected = undefined },
    refresh: async () => { for (const hook of hooks) await hook() },
  }
}

const candidate = { title: 'A learned fact', retrievalCondition: 'When revisiting', content: 'Reviewable detail', provenance: 'Task review evidence', confidence: 'medium' as const, limitations: ['Needs independent review'] }

describe('WK Durable binder and identity ownership over public service ports', () => {
  it.each([
    ['unknown payload field', (input: BinderPrepareInput) => ({ ...input, payload: { ...(input.payload as object), ref: 'forged-ref' } as JsonValue })],
    ['wrong schema', (input: BinderPrepareInput) => ({ ...input, payload: { ...(input.payload as object), schemaVersion: 2 } as JsonValue })],
    ['different service key', (input: BinderPrepareInput) => ({ ...input, payload: { ...(input.payload as object), serviceBindingKey: 'another-service' } as JsonValue })],
    ['different workspace', (input: BinderPrepareInput) => ({ ...input, workspaceRealpath: '/unapproved/workspace' })],
    ['different member', (input: BinderPrepareInput) => ({ ...input, memberName: 'another-member' })],
    ['different route', (input: BinderPrepareInput) => ({ ...input, spec: { ...input.spec, agentOptions: { provider: 'another-provider', model: 'model-one' } } })],
    ['fork context', (input: BinderPrepareInput) => ({ ...input, spec: { ...input.spec, context: 'fork' as const } })],
    ['global storage', (input: BinderPrepareInput) => ({ ...input, payload: { ...(input.payload as object), declaration: { ...((input.payload as { declaration: object }).declaration), scope: 'global' } } as JsonValue })],
    ['different initial task', (input: BinderPrepareInput) => ({ ...input, spec: { ...input.spec, initialTask: [{ type: 'text' as const, text: 'An unapproved task' }] } })],
  ])('fails closed during prepare for %s before provisioning', async (_label, mutate) => {
    const f = await fixture()
    await expect(f.binder.prepare(mutate(f.input), new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    expect(f.service.provision).not.toHaveBeenCalled()
    expect(f.scope.install).not.toHaveBeenCalled()
  })

  it.each(['version', 'read', 'candidate'] as const)('requires supported service API and feature %s before preparing', async feature => {
    const f = await fixture()
    if (feature === 'version') f.service.apiVersion = 2
    else if (feature === 'read') f.service.features.selectiveMemoryRead = false
    else f.service.features.memoryCandidateSubmission = false
    await expect(f.binder.prepare(f.input, new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    expect(f.service.validateDeclaration).not.toHaveBeenCalled()
    expect(f.service.provision).not.toHaveBeenCalled()
  })

  it('shares workspace/name ownership across Teams and releases a prepared reservation on abort', async () => {
    const f = await fixture()
    const prepared = await f.binder.prepare(f.input, new AbortController().signal)
    const otherBinder = createDurableAgentBinder(f.composition)
    const otherInput = { ...f.input, teamId: 'team-two', memberId: 'child-two' }
    await expect(otherBinder.prepare(otherInput, new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_CONFLICT' })
    await prepared.abort(new AbortController().signal)
    await prepared.abort(new AbortController().signal)
    const replacement = await otherBinder.prepare(otherInput, new AbortController().signal)
    await replacement.abort(new AbortController().signal)
    expect(f.service.provision).not.toHaveBeenCalled()
    expect(f.service.release).not.toHaveBeenCalled()
  })

  it('installs two executable closed tools and one coherent prompt without exposing a ref or eagerly reading bodies', async () => {
    const f = await fixture()
    const { binding, contribution, prepared } = await f.bound()
    expect(contribution.tools.map(tool => tool.name)).toEqual(['durable_agent_read_memory', 'durable_agent_submit_candidate'])
    expect(f.contributions.size).toBe(1)
    expect(f.hooks.size).toBe(1)
    expect(contribution.prompt).not.toContain(f.ref)
    expect(contribution.prompt).not.toContain(f.workspace)
    expect(contribution.prompt).not.toContain(f.item.content)
    expect(JSON.stringify(prepared.attachment)).not.toContain(f.ref)
    expect(f.service.readMemoryItem).not.toHaveBeenCalled()
    const read = contribution.tools[0]!
    expect(read.schema).toMatchObject({ additionalProperties: false, required: ['itemId'] })
    await expect(read.invoke({ itemId: 'memory-one', ref: 'forged' })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    expect(f.service.readMemoryItem).not.toHaveBeenCalled()
    await expect(read.invoke({ itemId: 'memory-one' })).resolves.toEqual(f.item)
    expect(f.service.readMemoryItem).toHaveBeenCalledExactlyOnceWith(f.ref, 'memory-one')
    await expect(contribution.tools[1]!.invoke({ ...candidate, approval: 'human' })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(contribution.tools[1]!.invoke(candidate)).resolves.toMatchObject({ status: 'unconfirmed' })
    expect(f.service.submitMemoryCandidate).toHaveBeenCalledExactlyOnceWith(f.ref, candidate)
    expect(f.service.commitMemoryItem).not.toHaveBeenCalled()
    expect(f.service.workingLocation).not.toHaveBeenCalled()
    await binding.release(new AbortController().signal)
  })

  it('refreshes the owner prompt for every authorized request and fails the request on refresh error', async () => {
    const f = await fixture()
    const { binding, contribution } = await f.bound()
    expect(JSON.parse(contribution.prompt).revision).toBe(1)
    f.setRevision(2)
    await f.refresh()
    expect(f.contributions.size).toBe(1)
    expect(JSON.parse(f.contributions.get(contribution.key)!.prompt)).toMatchObject({ revision: 2, guidance: 'Guidance revision 2' })
    expect(f.scope.install).toHaveBeenCalledTimes(1)
    expect(f.scope.replacePrompt).toHaveBeenCalledTimes(1)
    expect(f.actions.filter(action => action === 'request')).toHaveLength(2)
    f.service.openTaskContext.mockRejectedValueOnce(new Error('snapshot unavailable'))
    await expect(f.refresh()).rejects.toThrow('snapshot unavailable')
    expect(f.scope.replacePrompt).toHaveBeenCalledTimes(1)
    await binding.release(new AbortController().signal)
  })

  it.each(['generation', 'service', 'authorization'] as const)('revokes stale tool admission immediately when %s is lost', async reason => {
    const f = await fixture()
    const { binding, contribution } = await f.bound()
    if (reason === 'generation') f.setCurrent(false)
    else if (reason === 'service') f.replaceService()
    else f.setAuthorized(false)
    await expect(contribution.tools[0]!.invoke({ itemId: 'memory-one' })).rejects.toBeTruthy()
    expect(f.service.readMemoryItem).not.toHaveBeenCalled()
    expect(f.contributions.size).toBe(0)
    expect(f.hooks.size).toBe(0)
    await binding.release(new AbortController().signal)
    expect(f.service.release).toHaveBeenCalledTimes(1)
  })

  it('withholds a paused read result after scope revocation without self-drain deadlock', async () => {
    const f = await fixture()
    const { binding, contribution } = await f.bound()
    const entered = barrier<void>()
    const readResult = barrier<DurableAgentMemoryItem>()
    f.service.readMemoryItem.mockImplementation(async () => { entered.resolve(); return await readResult.promise })
    const read = contribution.tools[0]!.invoke({ itemId: 'memory-one' })
    void read.catch(() => undefined)
    await entered.promise
    f.setCurrent(false)
    // A new admission detects revocation while an already admitted read is paused.
    await expect(contribution.tools[1]!.invoke(candidate)).rejects.toBeTruthy()
    expect(f.contributions.size).toBe(0)
    expect(f.hooks.size).toBe(0)
    expect(f.service.release).not.toHaveBeenCalled()
    readResult.resolve(f.item)
    await expect(read).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    await binding.release(new AbortController().signal)
    expect(f.service.release).toHaveBeenCalledTimes(1)
    expect(f.service.submitMemoryCandidate).not.toHaveBeenCalled()
  })

  it('recovers the exact persisted declaration without reading workspace YAML or preparing again', async () => {
    const f = await fixture()
    const prepared = await f.binder.prepare(f.input, new AbortController().signal)
    const persisted = structuredClone(prepared.attachment)
    await prepared.abort(new AbortController().signal)
    // The temporary workspace contains no declaration file at all.
    const recover = await f.binder.recover({ ...f.bindInput, generation: 'generation-two' }, persisted, new AbortController().signal)
    expect(f.service.provision).toHaveBeenCalledExactlyOnceWith(f.workspace, (persisted as { declaration: unknown }).declaration)
    expect(f.contributions.size).toBe(1)
    expect(f.service.validateDeclaration).toHaveBeenCalledTimes(2)
    await recover.release(new AbortController().signal)
  })

  it('retains cross-Team ownership until physical release settles and memoizes all cleanup callers', async () => {
    const f = await fixture()
    const { binding } = await f.bound()
    const released = barrier<void>()
    const entered = barrier<void>()
    f.service.release.mockImplementation(async () => { entered.resolve(); await released.promise })
    binding.closeAdmission()
    expect(f.contributions.size).toBe(0)
    expect(f.hooks.size).toBe(0)
    const first = binding.release(new AbortController().signal)
    const second = binding.release(new AbortController().signal)
    expect(first).toBe(second)
    await entered.promise
    const nextInput = { ...f.input, teamId: 'team-two', memberId: 'child-two' }
    await expect(f.binder.prepare(nextInput, new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_CONFLICT' })
    released.resolve()
    await first
    const next = await f.binder.prepare(nextInput, new AbortController().signal)
    await next.abort(new AbortController().signal)
    expect(f.service.release).toHaveBeenCalledTimes(1)
  })

  it('quarantines identity ownership after provider release fails and never reuses the failed cleanup ref', async () => {
    const f = await fixture()
    const { binding } = await f.bound()
    f.service.release.mockRejectedValue(new Error('provider cleanup failed'))
    const first = binding.release(new AbortController().signal)
    await expect(first).rejects.toThrow('provider cleanup failed')
    expect(binding.release(new AbortController().signal)).toBe(first)
    await expect(f.binder.prepare({ ...f.input, teamId: 'team-two', memberId: 'child-two' }, new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_CONFLICT' })
    expect(f.contributions.size).toBe(0)
    expect(f.hooks.size).toBe(0)
    expect(f.service.release).toHaveBeenCalledTimes(1)
  })

  it('removes installed authority immediately on bind-signal cancellation and waits for physical provider cleanup', async () => {
    const f = await fixture()
    const prepared = await f.binder.prepare(f.input, new AbortController().signal)
    const cancellation = new AbortController()
    const binding = await f.binder.bind(f.bindInput, prepared.attachment, prepared.value, cancellation.signal)
    cancellation.abort(new Error('member shutdown'))
    expect(f.contributions.size).toBe(0)
    expect(f.hooks.size).toBe(0)
    await binding.release(new AbortController().signal)
    expect(f.service.release).toHaveBeenCalledTimes(1)
  })

  it('rejects a mismatched bind workspace before provisioning or installing a child contribution', async () => {
    const f = await fixture()
    const prepared = await f.binder.prepare(f.input, new AbortController().signal)
    try {
      await expect(f.binder.bind({ ...f.bindInput, workspaceRealpath: '/different/child/workspace' }, prepared.attachment, prepared.value, new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
      expect(f.service.provision).not.toHaveBeenCalled()
      expect(f.scope.install).not.toHaveBeenCalled()
    } finally { await prepared.abort(new AbortController().signal) }
  })

  it.each(['aborted', 'stale'] as const)('rejects %s bind admission before persistent provisioning starts', async state => {
    const f = await fixture()
    const prepared = await f.binder.prepare(f.input, new AbortController().signal)
    const cancellation = new AbortController()
    if (state === 'aborted') cancellation.abort(new Error('bind already cancelled'))
    else f.setCurrent(false)
    try {
      await expect(f.binder.bind(f.bindInput, prepared.attachment, prepared.value, cancellation.signal)).rejects.toBeTruthy()
      expect(f.service.provision).not.toHaveBeenCalled()
      expect(f.scope.install).not.toHaveBeenCalled()
    } finally { await prepared.abort(new AbortController().signal) }
  })

  it('uses the real public provider for host-approved memory, request refresh, unconfirmed candidates and persisted recovery', async () => {
    const f = await fixture()
    const service = new LocalDurableAgentProvider(new Context())
    const composition: DurableBinderComposition = { ...f.composition, service, resolveService: () => service }
    const binder = createDurableAgentBinder(composition)
    const provision = vi.spyOn(service, 'provision')
    const prepared = await binder.prepare(f.input, new AbortController().signal)
    const persisted = structuredClone(prepared.attachment)
    const binding = await binder.bind(f.bindInput, persisted, prepared.value, new AbortController().signal)
    // The host observes the public provision result; the ref never comes from model arguments.
    const ref = await provision.mock.results[0]!.value as DurableAgentRef
    const committed = await service.commitMemoryItem(ref, {
      item: { id: 'memory-one', title: 'An approved fact', retrievalCondition: 'When reviewing', content: 'Host-approved body' },
      authorization: { kind: 'human', authorizationRef: 'aip-exec-022-provider-test' },
    })
    await f.refresh()
    const contribution = [...f.contributions.values()][0]!
    expect(JSON.parse(contribution.prompt).catalog).toEqual([{ id: 'memory-one', title: 'An approved fact', retrievalCondition: 'When reviewing' }])
    expect(contribution.prompt).not.toContain('Host-approved body')
    expect(contribution.prompt).not.toContain(ref)
    await expect(contribution.tools[0]!.invoke({ itemId: 'memory-one' })).resolves.toMatchObject({ content: 'Host-approved body', revision: committed.revision })
    await expect(contribution.tools[1]!.invoke(candidate)).resolves.toMatchObject({ status: 'unconfirmed' })
    await binding.release(new AbortController().signal)
    await expect(service.openTaskContext(ref)).rejects.toBeTruthy()
    const restarted = new LocalDurableAgentProvider(new Context())
    const recoveredBinder = createDurableAgentBinder({ ...composition, service: restarted, resolveService: () => restarted })
    const recovered = await recoveredBinder.recover({ ...f.bindInput, generation: 'generation-two' }, persisted, new AbortController().signal)
    const recoveredContribution = [...f.contributions.values()][0]!
    await expect(recoveredContribution.tools[0]!.invoke({ itemId: 'memory-one' })).resolves.toMatchObject({ content: 'Host-approved body', revision: committed.revision })
    expect(JSON.stringify(persisted)).not.toContain(ref)
    await recovered.release(new AbortController().signal)
  })

  it('releases a recovered ownership reservation when cancellation arrives between validation and bind admission', async () => {
    const f = await fixture()
    const cancellation = new AbortController()
    let checks = 0
    const interrupted = createDurableAgentBinder({
      ...f.composition,
      resolveService: () => {
        if (++checks === 2) queueMicrotask(() => cancellation.abort(new Error('recovery cancelled at handoff')))
        return f.composition.service
      },
    })
    await expect(interrupted.recover(f.bindInput, f.input.payload, cancellation.signal)).rejects.toThrow('recovery cancelled at handoff')
    const next = await f.binder.prepare({ ...f.input, teamId: 'team-two', memberId: 'child-two' }, new AbortController().signal)
    await next.abort(new AbortController().signal)
    expect(f.service.provision).not.toHaveBeenCalled()
    expect(f.scope.install).not.toHaveBeenCalled()
  })
})
