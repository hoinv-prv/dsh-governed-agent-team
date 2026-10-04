import { afterEach, describe, expect, it, vi } from 'vitest'
import { attachmentRecord } from '../src/attachments.ts'
import { BoundMemberRuntime, MemberBindingOwner, provisionPreparedMember, recoverBoundMember } from '../src/member-binding.ts'
import type { MemberBindingPorts, ReservedMemberChild } from '../src/member-binding.ts'
import { abortPrepared, prepareMembers, TeamMemberBinderRegistry } from '../src/member-binders.ts'
import type { BinderPrepareInput, DisposableBinding, MemberCapabilityScope, PreparedAttachment, TeamMemberBinder } from '../src/member-binders.ts'
import type { JsonValue, TeamMemberAttachmentRecord } from '../src/types.ts'
import { acquireBindingResource } from '../src/binding-deadline.ts'

function barrier<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason: unknown) => void
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}

function fixture(ids = ['memory-a', 'memory-b']) {
  const trace: string[] = []
  let phase: 'none' | 'provisioning' | 'active' | 'failed' = 'none'
  let valid = true
  let authorized = true
  let publishThrows = false
  const references: (readonly TeamMemberAttachmentRecord[])[] = []
  const registry = new TeamMemberBinderRegistry(() => references)
  const scope: MemberCapabilityScope = {
    isCurrent: () => valid,
    authorize: () => { if (!authorized) throw new Error('host authority revoked') },
    install: () => () => {}, beforeRequest: () => () => {}, replacePrompt: () => {},
  }
  const bindings = new Map<string, DisposableBinding>()
  const binders = new Map<string, TeamMemberBinder>()
  const unregister = new Map<string, () => void>()
  for (const id of ids) {
    const binding = {
      closeAdmission: vi.fn(() => { trace.push(`close:${id}`) }),
      settle: vi.fn(async (_signal: AbortSignal) => { trace.push(`settle:${id}`) }),
      release: vi.fn(async (_signal: AbortSignal) => { trace.push(`release:${id}`) }),
    }
    bindings.set(id, binding)
    const binder: TeamMemberBinder = {
      id, protocolVersion: 1,
      prepare: vi.fn(async (): Promise<PreparedAttachment> => {
        trace.push(`prepare:${id}`)
        return { attachment: { persisted: id }, value: { id }, abort: vi.fn(async () => { trace.push(`abort:${id}`) }) }
      }),
      bind: vi.fn(async () => { trace.push(`bind:${id}`); return binding }),
      recover: vi.fn(async (_input, payload) => { trace.push(`recover:${id}`); expect(payload).toEqual({ persisted: id }); return binding }),
    }
    binders.set(id, binder)
    unregister.set(id, registry.register(binder))
  }
  const input: Omit<BinderPrepareInput, 'payload'> = {
    teamId: 'team-one', memberId: 'child-one', memberName: 'worker-one', generation: 'generation-one',
    workspaceRealpath: '/canonical/workspace',
    spec: {
      name: 'worker-one', description: 'Review a document', initialTask: [{ type: 'text', text: 'Review the approved document.' }],
      context: 'fresh', continuationProvider: 'spawn',
      attachments: ids.map(binderId => ({ binderId, protocolVersion: 1, required: true, payload: { declaration: binderId } })),
    },
  }
  const child: ReservedMemberChild = {
    scope, isValid: () => valid,
    persistInitialPrompt: vi.fn(async (_task, key) => { trace.push(`persist:${key}`); return 'initial-one' }),
    activate: vi.fn(async () => { expect(phase).toBe('active'); trace.push('activate') }),
    abort: vi.fn(async () => { trace.push('child:abort'); valid = false }),
    dispose: vi.fn(async () => { trace.push('child:dispose'); valid = false }),
  }
  const ports: MemberBindingPorts = {
    cleanupTimeoutMs: 25,
    journal: {
      provisioning: vi.fn(async (_identity, records) => { trace.push('flush:provisioning'); references.push(records); phase = 'provisioning' }),
      active: vi.fn(async () => { trace.push('flush:active'); phase = 'active' }),
      failed: vi.fn(async (_identity, records, diagnostic) => {
        expect(records).toEqual(references[0]); expect(diagnostic).toBe('required member binding failed')
        trace.push('flush:failed'); phase = 'failed'
      }),
      committedPhase: vi.fn(async () => { trace.push(`observe:${phase}`); return phase }),
    },
    host: {
      materialize: vi.fn(async () => { trace.push('materialize'); return child }),
      recover: vi.fn(async () => { trace.push('cold:recover'); return child }),
      verifyPersistedChild: vi.fn(async () => { trace.push('verify:child') }),
    },
    authority: {
      authorize: vi.fn((_identity, operation) => { trace.push(`authorize:${operation}`); if (!authorized) throw new Error('host authority revoked') }),
      publish: vi.fn((_identity, state) => { trace.push(`publish:${state}`); if (publishThrows) throw new Error('readiness publisher failed') }),
    },
  }
  return {
    trace, registry, bindings, binders, unregister, input, child, ports,
    setPhase: (next: typeof phase) => { phase = next },
    setValid: (next: boolean) => { valid = next },
    setAuthorized: (next: boolean) => { authorized = next },
    setPublishThrows: (next: boolean) => { publishThrows = next },
    prepared: async (signal = new AbortController().signal) => (await prepareMembers(registry, [input], signal, ports.cleanupTimeoutMs))[0]!,
    records: () => ids.map(binderId => attachmentRecord({ binderId, protocolVersion: 1, required: true, payload: null }, { persisted: binderId })),
  }
}

afterEach(() => { vi.useRealTimers() })

describe('required member binding lifecycle over qualified deterministic ports', () => {
  it('retains exactly one resource owner when cancellation races promise handoff at successive microtask boundaries', async () => {
    for (let offset = 0; offset < 9; offset++) {
      const cancellation = new AbortController()
      const acquired = barrier<{ id: number }>()
      const late = vi.fn(async (_resource: { id: number }) => {})
      const operation = acquireBindingResource(() => acquired.promise, cancellation.signal, late)
      void operation.catch(() => undefined)
      acquired.resolve({ id: offset })
      for (let index = 0; index < offset; index++) await Promise.resolve()
      cancellation.abort(new Error('handoff cancellation'))
      let handedOff = 0
      await operation.then(resource => { expect(resource.id).toBe(offset); handedOff++ }, () => undefined)
      for (let index = 0; index < 12; index++) await Promise.resolve()
      // Either the caller owns the resource, or the late cleanup owns it. Never neither/both.
      expect({ offset, owners: handedOff + late.mock.calls.length }).toEqual({ offset, owners: 1 })
    }
  })

  it('keeps the initial item quarantined until the active flush barrier has completed', async () => {
    const f = fixture()
    const prepared = await f.prepared()
    const entered = barrier<void>()
    const flush = barrier<void>()
    vi.mocked(f.ports.journal.active).mockImplementation(async () => {
      f.trace.push('active:entered'); entered.resolve(); await flush.promise
      f.setPhase('active'); f.trace.push('flush:active')
    })
    const operation = provisionPreparedMember(prepared, f.ports, new AbortController().signal)
    await entered.promise
    expect(f.child.persistInitialPrompt).toHaveBeenCalledExactlyOnceWith(prepared.input.spec.initialTask, 'gat-initial:team-one:child-one', expect.any(AbortSignal))
    expect(f.child.activate).not.toHaveBeenCalled()
    expect(f.ports.authority.publish).not.toHaveBeenCalled()
    flush.resolve()
    await operation
    expect(f.trace).toEqual([
      'prepare:memory-a', 'prepare:memory-b', 'flush:provisioning', 'materialize',
      'bind:memory-a', 'bind:memory-b', 'persist:gat-initial:team-one:child-one',
      'active:entered', 'flush:active', 'authorize:activate', 'publish:ready', 'activate',
    ])
  })

  it('tombstones pre-active failure and releases bindings in reverse order without changing attachments', async () => {
    const f = fixture()
    const prepared = await f.prepared()
    vi.mocked(f.child.persistInitialPrompt).mockRejectedValue(new Error('persistence failed'))
    await expect(provisionPreparedMember(prepared, f.ports, new AbortController().signal)).rejects.toBeInstanceOf(AggregateError)
    expect(f.trace.slice(6)).toEqual([
      'observe:provisioning', 'close:memory-b', 'close:memory-a', 'publish:unavailable', 'child:abort',
      'settle:memory-b', 'release:memory-b', 'settle:memory-a', 'release:memory-a', 'child:dispose', 'flush:failed',
    ])
    expect(f.child.activate).not.toHaveBeenCalled()
    expect(f.ports.journal.active).not.toHaveBeenCalled()
    expect(f.trace.filter(value => value.startsWith('abort:'))).toEqual([])
  })

  it('preserves a committed active generation after an uncertain flush and retries without reinstall or duplicate initial item', async () => {
    const f = fixture()
    vi.mocked(f.ports.journal.active).mockImplementation(async () => { f.setPhase('active'); throw new Error('flush acknowledgement lost') })
    const runtime = await provisionPreparedMember(await f.prepared(), f.ports, new AbortController().signal)
    expect(runtime.lastFailure).toBeInstanceOf(Error)
    expect(f.child.activate).not.toHaveBeenCalled()
    await runtime.activate(new AbortController().signal)
    await runtime.activate(new AbortController().signal)
    expect(f.child.activate).toHaveBeenCalledTimes(1)
    expect(f.child.persistInitialPrompt).toHaveBeenCalledTimes(1)
    for (const binder of f.binders.values()) { expect(binder.bind).toHaveBeenCalledTimes(1); expect(binder.recover).not.toHaveBeenCalled() }
    for (const binding of f.bindings.values()) expect(binding.closeAdmission).not.toHaveBeenCalled()
    expect(f.child.abort).not.toHaveBeenCalled()
    expect(f.ports.journal.failed).not.toHaveBeenCalled()
  })

  it('disposes an invalid committed active generation while preserving its existing initial item', async () => {
    const f = fixture()
    vi.mocked(f.ports.journal.active).mockImplementation(async () => { f.setPhase('active'); f.setValid(false); throw new Error('generation invalidated') })
    await expect(provisionPreparedMember(await f.prepared(), f.ports, new AbortController().signal)).rejects.toBeInstanceOf(AggregateError)
    expect(f.child.dispose).toHaveBeenCalledTimes(1)
    expect(f.child.abort).not.toHaveBeenCalled()
    expect(f.child.persistInitialPrompt).toHaveBeenCalledTimes(1)
    expect(f.ports.journal.failed).not.toHaveBeenCalled()
    expect(f.child.activate).not.toHaveBeenCalled()
  })

  it('keeps bindings installed when authority is absent and reauthorizes a live retry', async () => {
    const f = fixture()
    f.setAuthorized(false)
    const runtime = await provisionPreparedMember(await f.prepared(), f.ports, new AbortController().signal)
    expect(f.child.activate).not.toHaveBeenCalled()
    expect(f.trace.at(-1)).toBe('publish:unavailable')
    f.setAuthorized(true)
    await runtime.activate(new AbortController().signal)
    expect(f.ports.authority.authorize).toHaveBeenCalledTimes(2)
    expect(f.child.activate).toHaveBeenCalledTimes(1)
    expect(f.child.persistInitialPrompt).toHaveBeenCalledTimes(1)
    for (const binding of f.bindings.values()) expect(binding.closeAdmission).not.toHaveBeenCalled()
  })

  it('rechecks authorization for a concurrent activation retry and marks activation failures unavailable', async () => {
    const f = fixture()
    const admission = barrier<void>()
    const entered = barrier<void>()
    vi.mocked(f.child.activate).mockImplementation(async () => { entered.resolve(); await admission.promise; throw new Error('wake failed') })
    f.setPhase('active')
    const runtime = new BoundMemberRuntime({ ...f.input, scope: f.child.scope }, f.records(), f.child, [...f.bindings.values()], f.ports.authority)
    const first = runtime.activate(new AbortController().signal)
    void first.catch(() => undefined)
    await entered.promise
    f.setAuthorized(false)
    expect(() => runtime.activate(new AbortController().signal)).toThrow('host authority revoked')
    admission.resolve()
    await expect(first).rejects.toThrow('wake failed')
    expect(f.trace.at(-1)).toBe('publish:unavailable')
    expect(f.child.activate).toHaveBeenCalledTimes(1)
  })

  it('validates persisted digest and child evidence before recover and never persists another initial item', async () => {
    const f = fixture()
    const records = f.records()
    const corrupt = records.map((record, index) => index === 0 ? { ...record, payloadSha256: '0'.repeat(64) } : record)
    await expect(recoverBoundMember(f.input, corrupt, f.registry, f.ports, new AbortController().signal)).rejects.toMatchObject({ code: 'TEAM_INVALID_ATTACHMENT' })
    expect(f.ports.host.verifyPersistedChild).not.toHaveBeenCalled()
    f.setPhase('active')
    await recoverBoundMember(f.input, records, f.registry, f.ports, new AbortController().signal)
    expect(f.trace).toEqual(['verify:child', 'cold:recover', 'recover:memory-a', 'recover:memory-b', 'authorize:activate', 'publish:ready', 'activate'])
    expect(f.child.persistInitialPrompt).not.toHaveBeenCalled()
    expect(f.ports.journal.provisioning).not.toHaveBeenCalled()
    expect(f.ports.journal.failed).not.toHaveBeenCalled()
  })

  it('serializes simultaneous same-generation recovery and disposes the previous owner before a new generation', async () => {
    const f = fixture()
    const owner = new MemberBindingOwner(f.ports)
    const entered = barrier<void>()
    const creation = barrier<void>()
    f.setPhase('active')
    const create = vi.fn(async () => { entered.resolve(); await creation.promise; return await recoverBoundMember(f.input, f.records(), f.registry, f.ports, new AbortController().signal) })
    const first = owner.run(f.input, create, new AbortController().signal)
    await entered.promise
    const second = owner.run(f.input, create, new AbortController().signal)
    creation.resolve()
    expect(await first).toBe(await second)
    expect(create).toHaveBeenCalledTimes(1)
    for (const binder of f.binders.values()) expect(binder.recover).toHaveBeenCalledTimes(1)
    const replacement = fixture()
    replacement.setPhase('active')
    await owner.run({ ...f.input, generation: 'generation-two' }, async () => {
      expect(f.trace.at(-1)).toBe('child:dispose')
      return await recoverBoundMember({ ...replacement.input, generation: 'generation-two' }, replacement.records(), replacement.registry, replacement.ports, new AbortController().signal)
    }, new AbortController().signal)
    expect(f.child.abort).not.toHaveBeenCalled()
  })

  it('cuts off every binding and completes reverse release even when readiness publication throws', async () => {
    const f = fixture()
    const runtime = await provisionPreparedMember(await f.prepared(), f.ports, new AbortController().signal)
    f.trace.length = 0
    f.setPublishThrows(true)
    await expect(runtime.dispose(25)).rejects.toBeInstanceOf(AggregateError)
    expect(f.trace).toEqual(['publish:unavailable', 'close:memory-b', 'close:memory-a', 'settle:memory-b', 'release:memory-b', 'settle:memory-a', 'release:memory-a', 'child:dispose'])
    await expect(runtime.releaseMailbox(async () => { throw new Error('must never execute') })).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
  })

  it('uses one total cleanup signal and invokes remaining reverse callbacks after the deadline', async () => {
    const f = fixture()
    const runtime = await provisionPreparedMember(await f.prepared(), f.ports, new AbortController().signal)
    const never = barrier<void>()
    const signals: AbortSignal[] = []
    vi.mocked(f.bindings.get('memory-b')!.settle).mockImplementation(async signal => { signals.push(signal); await never.promise })
    for (const [id, binding] of f.bindings) {
      vi.mocked(binding.release).mockImplementation(async signal => { signals.push(signal); f.trace.push(`release:${id}`) })
    }
    vi.mocked(f.bindings.get('memory-a')!.settle).mockImplementation(async signal => { signals.push(signal) })
    vi.mocked(f.child.dispose).mockImplementation(async signal => { signals.push(signal); f.trace.push('child:dispose') })
    vi.useFakeTimers()
    const disposal = runtime.dispose(10)
    await vi.advanceTimersByTimeAsync(10)
    await expect(disposal).rejects.toBeInstanceOf(AggregateError)
    expect(signals).toHaveLength(5)
    expect(signals.every(signal => signal === signals[0] && signal.aborted)).toBe(true)
    expect(f.trace.slice(-3)).toEqual(['release:memory-b', 'release:memory-a', 'child:dispose'])
    never.resolve()
  })

  it('rejects malformed binding output before initial persistence and aborts its untransferred prepared lease', async () => {
    const f = fixture(['memory-a'])
    vi.mocked(f.binders.get('memory-a')!.bind).mockResolvedValue(undefined as unknown as DisposableBinding)
    await expect(provisionPreparedMember(await f.prepared(), f.ports, new AbortController().signal)).rejects.toBeInstanceOf(AggregateError)
    expect(f.trace).toContain('abort:memory-a')
    expect(f.child.persistInitialPrompt).not.toHaveBeenCalled()
    expect(f.child.activate).not.toHaveBeenCalled()
    expect(f.ports.journal.failed).toHaveBeenCalledTimes(1)
  })

  it('rejects cancellation promptly, retains the pending registration, and aborts a late prepared resource once', async () => {
    const f = fixture(['memory-a'])
    const acquired = barrier<PreparedAttachment>()
    const entered = barrier<void>()
    const abortDone = barrier<void>()
    const late: PreparedAttachment = { attachment: { persisted: 'memory-a' }, value: null, abort: vi.fn(async () => { await abortDone.promise }) }
    vi.mocked(f.binders.get('memory-a')!.prepare).mockImplementation(async () => { entered.resolve(); return await acquired.promise })
    const cancellation = new AbortController()
    const operation = prepareMembers(f.registry, [f.input], cancellation.signal, 25)
    void operation.catch(() => undefined)
    await entered.promise
    cancellation.abort(new Error('cancelled'))
    await expect(operation).rejects.toThrow('cancelled')
    expect(f.unregister.get('memory-a')).toThrow()
    acquired.resolve(late)
    await vi.waitFor(() => expect(late.abort).toHaveBeenCalledTimes(1))
    expect(f.unregister.get('memory-a')).toThrow()
    abortDone.resolve()
    await vi.waitFor(() => expect(f.unregister.get('memory-a')).not.toThrow())
    expect(late.abort).toHaveBeenCalledTimes(1)
  })

  it('tombstones and drains a child that materializes after provisioning cancellation', async () => {
    const f = fixture(['memory-a'])
    const childReady = barrier<ReservedMemberChild>()
    const entered = barrier<void>()
    vi.mocked(f.ports.host.materialize).mockImplementation(async () => { entered.resolve(); return await childReady.promise })
    const cancellation = new AbortController()
    const operation = provisionPreparedMember(await f.prepared(), f.ports, cancellation.signal)
    void operation.catch(() => undefined)
    await entered.promise
    cancellation.abort(new Error('cancelled'))
    await expect(operation).rejects.toBeInstanceOf(AggregateError)
    expect(f.trace.filter(value => value === 'abort:memory-a')).toHaveLength(1)
    childReady.resolve(f.child)
    await vi.waitFor(() => expect(f.child.dispose).toHaveBeenCalledTimes(1))
    expect(f.child.abort).toHaveBeenCalledTimes(1)
    expect(f.child.persistInitialPrompt).not.toHaveBeenCalled()
    expect(f.child.activate).not.toHaveBeenCalled()
  })

  it('cuts off and releases a binding that arrives after the member acquisition was cancelled', async () => {
    const f = fixture(['memory-a'])
    const bindingReady = barrier<DisposableBinding>()
    const entered = barrier<void>()
    vi.mocked(f.binders.get('memory-a')!.bind).mockImplementation(async () => { entered.resolve(); return await bindingReady.promise })
    const cancellation = new AbortController()
    const operation = provisionPreparedMember(await f.prepared(), f.ports, cancellation.signal)
    void operation.catch(() => undefined)
    await entered.promise
    cancellation.abort(new Error('cancelled'))
    await expect(operation).rejects.toBeInstanceOf(AggregateError)
    bindingReady.resolve(f.bindings.get('memory-a')!)
    await vi.waitFor(() => expect(f.bindings.get('memory-a')!.release).toHaveBeenCalledTimes(1))
    expect(f.bindings.get('memory-a')!.closeAdmission).toHaveBeenCalledTimes(1)
    expect(f.bindings.get('memory-a')!.settle).toHaveBeenCalledTimes(1)
    expect(f.trace.filter(value => value === 'abort:memory-a')).toHaveLength(1)
    expect(f.child.activate).not.toHaveBeenCalled()
  })

  it('bounds reverse prepared cleanup and invokes earlier aborts even when the last ignores cancellation', async () => {
    const f = fixture()
    const prepared = await f.prepared()
    const blocked = barrier<void>()
    const order: string[] = []
    const signals: AbortSignal[] = []
    const last = prepared.leases[1]!
    vi.spyOn(last, 'abort').mockImplementation(async signal => { order.push('last'); signals.push(signal); await blocked.promise })
    vi.spyOn(prepared.leases[0]!, 'abort').mockImplementation(async signal => { order.push('first'); signals.push(signal) })
    const { BindingDeadline } = await import('../src/member-binding.ts')
    vi.useFakeTimers()
    const deadline = new BindingDeadline(10)
    const operation = abortPrepared(prepared.leases, deadline.signal, deadline)
    void operation.catch(() => undefined)
    await vi.advanceTimersByTimeAsync(10)
    await expect(operation).rejects.toBeInstanceOf(AggregateError)
    expect(order).toEqual(['last', 'first'])
    expect(signals[0]).toBe(signals[1])
    expect(signals[0]!.aborted).toBe(true)
    blocked.resolve(); deadline.finish()
  })

  it('shares the cleanup deadline for rejected prepared output and all previously prepared resources', async () => {
    const f = fixture()
    const signals: AbortSignal[] = []
    vi.mocked(f.binders.get('memory-a')!.prepare).mockResolvedValue({ attachment: null, value: null, abort: async signal => { signals.push(signal) } })
    vi.mocked(f.binders.get('memory-b')!.prepare).mockResolvedValue({ attachment: undefined as unknown as JsonValue, value: null, abort: async signal => { signals.push(signal) } })
    await expect(f.prepared()).rejects.toMatchObject({ code: 'TEAM_INVALID_ATTACHMENT' })
    expect(signals).toHaveLength(2)
    expect(signals[0]).toBe(signals[1])
  })

  it('cancels pending cold recovery promptly and drains a late child without tombstoning its active initial item', async () => {
    const f = fixture(['memory-a'])
    f.setPhase('active')
    const entered = barrier<void>()
    const childReady = barrier<ReservedMemberChild>()
    vi.mocked(f.ports.host.recover).mockImplementation(async () => { entered.resolve(); return await childReady.promise })
    const cancellation = new AbortController()
    const operation = recoverBoundMember(f.input, f.records(), f.registry, f.ports, cancellation.signal)
    let settled = false
    void operation.then(() => { settled = true }, () => { settled = true })
    await entered.promise
    cancellation.abort(new Error('cancelled cold recovery'))
    try {
      await vi.waitFor(() => expect(settled).toBe(true), { timeout: 100, interval: 5 })
    } finally {
      childReady.resolve(f.child)
      await operation.catch(() => undefined)
    }
    await vi.waitFor(() => expect(f.child.dispose).toHaveBeenCalledTimes(1))
    expect(f.child.abort).not.toHaveBeenCalled()
    expect(f.child.activate).not.toHaveBeenCalled()
    expect(f.child.persistInitialPrompt).not.toHaveBeenCalled()
  })

  it('cancels pending binder recovery promptly and releases its late binding without reopening member execution', async () => {
    const f = fixture(['memory-a'])
    f.setPhase('active')
    const entered = barrier<void>()
    const bindingReady = barrier<DisposableBinding>()
    vi.mocked(f.binders.get('memory-a')!.recover).mockImplementation(async () => { entered.resolve(); return await bindingReady.promise })
    const cancellation = new AbortController()
    const operation = recoverBoundMember(f.input, f.records(), f.registry, f.ports, cancellation.signal)
    let settled = false
    void operation.then(() => { settled = true }, () => { settled = true })
    await entered.promise
    cancellation.abort(new Error('cancelled binder recovery'))
    try {
      await vi.waitFor(() => expect(settled).toBe(true), { timeout: 100, interval: 5 })
    } finally {
      bindingReady.resolve(f.bindings.get('memory-a')!)
      await operation.catch(() => undefined)
    }
    await vi.waitFor(() => expect(f.bindings.get('memory-a')!.release).toHaveBeenCalledTimes(1))
    expect(f.bindings.get('memory-a')!.closeAdmission).toHaveBeenCalledTimes(1)
    expect(f.child.dispose).toHaveBeenCalledTimes(1)
    expect(f.child.abort).not.toHaveBeenCalled()
    expect(f.child.activate).not.toHaveBeenCalled()
    expect(f.child.persistInitialPrompt).not.toHaveBeenCalled()
  })

  it('aborts an in-flight activation at synchronous admission cutoff and withholds late success', async () => {
    const f = fixture()
    f.setPhase('active')
    const entered = barrier<void>()
    const wake = barrier<void>()
    let activationSignal: AbortSignal | undefined
    vi.mocked(f.child.activate).mockImplementation(async signal => { activationSignal = signal; entered.resolve(); await wake.promise })
    const runtime = new BoundMemberRuntime({ ...f.input, scope: f.child.scope }, f.records(), f.child, [...f.bindings.values()], f.ports.authority)
    const activation = runtime.activate(new AbortController().signal)
    void activation.catch(() => undefined)
    await entered.promise
    const disposal = runtime.dispose(25)
    expect(activationSignal?.aborted).toBe(true)
    wake.resolve()
    await expect(activation).rejects.toMatchObject({ code: 'TEAM_BINDING_UNAVAILABLE' })
    await disposal
    expect(f.trace.at(-1)).not.toBe('publish:ready')
    expect(() => runtime.activate(new AbortController().signal)).toThrow()
  })
})
