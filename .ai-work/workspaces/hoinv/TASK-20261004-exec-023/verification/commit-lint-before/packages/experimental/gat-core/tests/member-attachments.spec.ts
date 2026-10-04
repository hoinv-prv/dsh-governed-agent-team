import { describe, expect, it, vi } from 'vitest'
import {
  ATTACHMENT_LIMITS,
  attachmentRecord,
  canonicalJson,
  payloadSha256,
  validateAttachmentRecords,
  validateAttachmentRequests,
} from '../src/attachments.ts'
import {
  abortPrepared,
  prepareMembers,
  TeamMemberBinderRegistry,
  type BinderPrepareInput,
  type PreparedAttachment,
  type TeamMemberBinder,
} from '../src/member-binders.ts'
import type { TeamMemberAttachmentRequest, TeamMemberSpec } from '../src/types.ts'

function request(payload: unknown = null, binderId = 'memory'): TeamMemberAttachmentRequest {
  return { binderId, protocolVersion: 1, required: true, payload } as TeamMemberAttachmentRequest
}

function deferred<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void
  const promise = new Promise<T>(done => { resolve = done })
  return { promise, resolve }
}

function spec(attachments: readonly TeamMemberAttachmentRequest[]): TeamMemberSpec {
  return {
    name: 'worker', description: 'worker', initialTask: [], context: 'fresh',
    continuationProvider: 'spawn', attachments,
  }
}

function sizedRequest(targetBytes: number, binderId: string): TeamMemberAttachmentRequest {
  const payload = { a: 'a'.repeat(16_384), b: 'b'.repeat(16_384), c: 'c'.repeat(16_384), d: '' }
  const item = request(payload, binderId)
  const base = Buffer.byteLength(canonicalJson(item), 'utf8')
  const fill = targetBytes - base
  if (fill < 0 || fill > ATTACHMENT_LIMITS.stringBytes) throw new Error(`cannot fit target request size ${targetBytes}`)
  payload.d = 'd'.repeat(fill)
  return request(payload, binderId)
}

function aggregateSizedRequest(targetBytes: number, binderId: string): TeamMemberAttachmentRequest {
  const payload = { a: 'a'.repeat(16_384), b: '' }
  const base = Buffer.byteLength(canonicalJson(request(payload, binderId)), 'utf8')
  const fill = targetBytes - base
  if (fill < 0 || fill > ATTACHMENT_LIMITS.stringBytes) throw new Error(`cannot fit target request size ${targetBytes}`)
  payload.b = 'b'.repeat(fill)
  return request(payload, binderId)
}

function binder(
  id: string,
  prepare: TeamMemberBinder['prepare'] = async input => ({ attachment: input.payload, value: id, abort: async () => {} }),
): TeamMemberBinder {
  return {
    id,
    protocolVersion: 1,
    prepare,
    bind: async () => ({ closeAdmission() {}, settle: async () => {}, release: async () => {} }),
    recover: async () => ({ closeAdmission() {}, settle: async () => {}, release: async () => {} }),
  }
}

function prepareInput(
  name: string,
  attachments: readonly TeamMemberAttachmentRequest[],
): Omit<BinderPrepareInput, 'payload'> {
  return {
    teamId: 'team-1', memberId: `member-${name}`, memberName: name, generation: 'generation-1',
    workspaceRealpath: '/workspace', spec: { ...spec(attachments), name },
  }
}

describe('required member attachment validation', () => {
  it('uses canonical key order, normalizes negative zero, and hashes canonical payload bytes', () => {
    expect(canonicalJson({ z: -0, a: 1 })).toBe('{"a":1,"z":0}')
    expect(payloadSha256({ z: -0, a: 1 })).toBe('b55af27c4bd5f02ebeca8f901b84d2940b22e7bea7230e4d06f275d903bfdd72')
    expect(canonicalJson({ a: 1, z: 0 })).toBe(canonicalJson({ z: -0, a: 1 }))
    // JCS sorts object names by UTF-16 code units, so U+10000 precedes U+E000.
    expect(canonicalJson({ '\uE000': 1, '\u{10000}': 2 })).toBe('{"𐀀":2,"":1}')
  })

  it('rejects non-JSON values, getters without invoking them, and cyclic graphs', () => {
    const rejected: unknown[] = [undefined, 1n, Symbol('value'), () => {}, NaN, Infinity, new Date()]
    for (const value of rejected) {
      expect(() => validateAttachmentRequests([{ binderId: 'memory', protocolVersion: 1, required: true, payload: value }])).toThrow()
    }

    let getterCalls = 0
    const accessor = Object.defineProperty({}, 'secret', {
      enumerable: true,
      get() { getterCalls++; return 'must not run' },
    })
    expect(() => validateAttachmentRequests([request(accessor)])).toThrow()
    expect(getterCalls).toBe(0)

    const cycle: Record<string, unknown> = {}
    cycle.self = cycle
    expect(() => validateAttachmentRequests([request(cycle)])).toThrow()

    const sparse: unknown[] = []
    sparse.length = 1
    expect(() => validateAttachmentRequests([request(sparse)])).toThrow()
    const custom: unknown[] = []
    Object.defineProperty(custom, 'extra', { value: 'not JSON array data', enumerable: true })
    expect(() => validateAttachmentRequests([request(custom)])).toThrow()
    expect(() => validateAttachmentRequests([request({ [Symbol('key')]: 'not JSON' })])).toThrow()
    expect(() => validateAttachmentRequests([request('\uD800')])).toThrow()
  })

  it('rejects unknown request envelope fields and replay digest mismatches', () => {
    expect(() => validateAttachmentRequests([{
      binderId: 'memory', protocolVersion: 1, required: true, payload: null, extra: false,
    }])).toThrow()
    const record = attachmentRecord(request({ answer: 42 }), { answer: 42 })
    expect(validateAttachmentRecords([record])).toEqual([record])
    expect(() => validateAttachmentRecords([{ ...record, payloadSha256: '0'.repeat(64) }])).toThrow()
  })

  it('accepts exact record, record-count, depth, node, and aggregate-byte limits', () => {
    expect(validateAttachmentRequests([request('s'.repeat(ATTACHMENT_LIMITS.stringBytes))])).toHaveLength(1)
    expect(() => validateAttachmentRequests([request('s'.repeat(ATTACHMENT_LIMITS.stringBytes + 1))])).toThrow()

    const maxRecord = sizedRequest(ATTACHMENT_LIMITS.recordBytes, 'record-limit')
    expect(Buffer.byteLength(canonicalJson(maxRecord), 'utf8')).toBe(ATTACHMENT_LIMITS.recordBytes)
    expect(validateAttachmentRequests([maxRecord])).toHaveLength(1)
    expect(() => validateAttachmentRequests([sizedRequest(ATTACHMENT_LIMITS.recordBytes + 1, 'record-over')])).toThrow()

    expect(validateAttachmentRequests(Array.from({ length: ATTACHMENT_LIMITS.records }, (_, index) => request(null, `binder-${index}`))))
      .toHaveLength(ATTACHMENT_LIMITS.records)
    expect(() => validateAttachmentRequests(Array.from({ length: ATTACHMENT_LIMITS.records + 1 }, (_, index) => request(null, `binder-${index}`))))
      .toThrow()

    let depthBoundary: unknown = null
    for (let i = 0; i < ATTACHMENT_LIMITS.depth - 1; i++) depthBoundary = [depthBoundary]
    expect(() => validateAttachmentRequests([request(depthBoundary)])).not.toThrow()
    expect(() => validateAttachmentRequests([request([depthBoundary])])).toThrow()

    const maxNodes = Array.from({ length: ATTACHMENT_LIMITS.records }, (_, index) =>
      request(Array.from({ length: 507 }, () => null), `node-${index}`))
    expect(validateAttachmentRequests(maxNodes)).toHaveLength(ATTACHMENT_LIMITS.records)
    maxNodes[0] = request(Array.from({ length: 508 }, () => null), 'node-0')
    expect(() => validateAttachmentRequests(maxNodes)).toThrow()

    const aggregate = Array.from({ length: ATTACHMENT_LIMITS.records }, (_, index) =>
      aggregateSizedRequest(index < 7 ? 32_767 : 32_766, `aggregate-${index}`))
    expect(Buffer.byteLength(`[${aggregate.map(canonicalJson).join(',')}]`, 'utf8')).toBe(ATTACHMENT_LIMITS.aggregateBytes)
    expect(validateAttachmentRequests(aggregate)).toHaveLength(ATTACHMENT_LIMITS.records)
    aggregate[7] = aggregateSizedRequest(32_767, 'aggregate-7')
    expect(() => validateAttachmentRequests(aggregate)).toThrow()
  })
})

describe('member binder registry and prepared ownership', () => {
  it('rejects duplicates and keeps registrations while any durable record references them', () => {
    let durableRecords = [attachmentRecord(request({ workspace: 'w' }), { workspace: 'w' })]
    const registry = new TeamMemberBinderRegistry(() => [durableRecords])
    const participant = binder('memory')
    const unregister = registry.register(participant)
    expect(() => registry.register(binder('memory'))).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_CONFLICT' }))
    expect(registry.resolve(request())).toBeDefined()
    expect(() => unregister()).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_REFERENCED' }))

    durableRecords = []
    unregister()
    expect(() => registry.resolve(request())).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_UNAVAILABLE' }))
  })

  it('prepares deterministically and aborts successful leases once in reverse order after failure', async () => {
    const calls: string[] = []
    const registry = new TeamMemberBinderRegistry(() => [])
    const aborts = new Map<string, ReturnType<typeof vi.fn>>()
    for (const id of ['alpha', 'beta', 'gamma']) {
      const abort = vi.fn(async () => { calls.push(`abort:${id}`) })
      aborts.set(id, abort)
      registry.register(binder(id, async input => {
        calls.push(`prepare:${id}`)
        if (id === 'gamma') throw new Error('injected prepare failure')
        return { attachment: input.payload, value: id, abort }
      }))
    }
    const inputs = [
      prepareInput('first', [request({ n: 1 }, 'alpha'), request({ n: 2 }, 'beta')]),
      prepareInput('second', [request({ n: 3 }, 'gamma')]),
    ]
    await expect(prepareMembers(registry, inputs, new AbortController().signal)).rejects.toThrow('injected prepare failure')
    expect(calls).toEqual(['prepare:alpha', 'prepare:beta', 'prepare:gamma', 'abort:beta', 'abort:alpha'])
    expect(aborts.get('alpha')).toHaveBeenCalledTimes(1)
    expect(aborts.get('beta')).toHaveBeenCalledTimes(1)
  })

  it('transfers a successful lease once and makes abort idempotent for untransferred leases', async () => {
    const registry = new TeamMemberBinderRegistry(() => [])
    const abort = vi.fn(async () => {})
    const unregister = registry.register(binder('memory', async input => ({ attachment: input.payload, value: 'prepared', abort })))
    const prepared = await prepareMembers(registry, [prepareInput('worker', [request({ value: 1 })])], new AbortController().signal)
    const lease = prepared[0]!.leases[0]!
    expect(() => unregister()).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_REFERENCED' }))
    lease.transfer()
    expect(() => lease.transfer()).toThrow(expect.objectContaining({ code: 'TEAM_BINDING_CONFLICT' }))
    await abortPrepared([lease], new AbortController().signal)
    expect(abort).not.toHaveBeenCalled()
    unregister()
    expect(() => registry.resolve(request())).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_UNAVAILABLE' }))

    const unregisterAgain = registry.register(binder('memory', async input => ({ attachment: input.payload, value: 'prepared', abort })))
    const another = await prepareMembers(registry, [prepareInput('worker-2', [request({ value: 2 })])], new AbortController().signal)
    const untransferred = another[0]!.leases[0]!
    expect(() => unregisterAgain()).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_REFERENCED' }))
    await untransferred.abort(new AbortController().signal)
    unregisterAgain()
    await untransferred.abort(new AbortController().signal)
    expect(abort).toHaveBeenCalledTimes(1)
  })

  it('pins unresolved prepares through cancellation until late abort settles', async () => {
    const registry = new TeamMemberBinderRegistry(() => [])
    const prepareGate = deferred<PreparedAttachment>()
    const cleanupGate = deferred<void>()
    const abortStarted = deferred<void>()
    let prepareStarted = false
    const unregister = registry.register(binder('memory', async () => {
      prepareStarted = true
      return prepareGate.promise
    }))
    const controller = new AbortController()
    const pending = prepareMembers(registry, [prepareInput('cancelled', [request({ value: 1 })])], controller.signal)
    await vi.waitFor(() => { expect(prepareStarted).toBe(true) })
    expect(() => unregister()).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_REFERENCED' }))

    controller.abort(new Error('cancel prepare'))
    await expect(pending).rejects.toThrow('cancel prepare')
    expect(() => unregister()).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_REFERENCED' }))

    prepareGate.resolve({
      attachment: { value: 1 },
      value: 'late',
      abort: async () => { abortStarted.resolve(); await cleanupGate.promise },
    })
    await abortStarted.promise
    expect(() => unregister()).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_REFERENCED' }))

    cleanupGate.resolve()
    await vi.waitFor(() => { unregister() })
    expect(() => registry.resolve(request())).toThrow(expect.objectContaining({ code: 'TEAM_BINDER_UNAVAILABLE' }))
  })
})
