/** Real Loader/GAT/WK reviewer qualification with fixture-owned approved records. */
import { describe, expect, it, vi } from 'vitest'
import { createHash } from 'node:crypto'
import { spawnSync } from 'node:child_process'
import { writeFile, readFile, cp, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { brandString } from '@deepseek-ai/dsh-brand'
import { ToolCallId, LlmError, createUserMessage } from '@deepseek-ai/dsh-llm'
import { toolCallResponse } from '../../../core/agent-loop/tests/mock-adapter.ts'
import { taskContractSha256, createReviewPacket } from '@deepseek-ai/dsh-durable-agent'
import type { ReviewTestReceipt } from '@deepseek-ai/dsh-durable-agent'
import { boot, brief, declaration, signal, executionPlugin } from './execution-harness.ts'
import type { ReviewInput, ReviewInputPort } from '../src/execution-review.ts'
import * as ToolAgentTeam from '@deepseek-ai/dsh-experimental-tool-agent-team'

const sha = (value: Uint8Array | string) => createHash('sha256').update(value).digest('hex')
const settleTurn = () => new Promise<void>(resolve => setImmediate(resolve))
const canonical = (value: unknown): string => Array.isArray(value)
  ? `[${value.map(canonical).join(',')}]`
  : value !== null && typeof value === 'object'
    ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as Record<string, unknown>)[key])}`).join(',')}}`
    : JSON.stringify(value)
const limits = { maxPacketValidationReads: 8, maxPacketValidationBytes: 262144,
  maxEvidenceCalls: 4, maxEvidenceBytes: 65536, maxEvidenceTotalBytes: 262144,
  maxRationaleCalls: 2, maxRationaleAttempts: 4, maxRationaleTotalBytes: 65536 }
async function fixture(options: { mutate?: (input: ReviewInput) => ReviewInput; omit?: boolean;
  onResolve?: () => void; resolveGate?: Promise<void> } = {}) {
  let input: ReviewInput | undefined
  let resolveInput: ReviewInputPort['resolve'] = async () => options.omit ? undefined : options.mutate?.(input!) ?? input
  const port: ReviewInputPort = { resolve(request) {
    if (this !== port) throw new Error('trusted port receiver lost')
    return resolveInput(request)
  } }
  const h = await boot({ mode: 'hang', reviewInputPort: port, bindingFactory: config => executionPlugin({ ...config, members: [
    { ...config.members[0]!, mode: 'task' },
    { declaration: { ...declaration, name: 'reviewer' }, mode: 'reviewer' },
  ] }) })
  const workerExecution = await h.assign(); const workerAgent = await h.live(workerExecution.sessionId)
  const workerResult = 'fixture-worker-provisional-result-v1'
  await h.ctx.agentTeams.submitExecution(workerAgent, workerExecution.id, 'completed', workerResult)
  await vi.waitFor(() => expect(h.ctx.agentTeams.getExecution(h.lead, workerExecution.id).phase).toBe('completed'))
  const worker = h.ctx.agentTeams.getExecution(h.lead, workerExecution.id)
  const reviewerMember = (await h.ctx.agentTeams.spawnTeammate(h.lead, {
    name: 'reviewer', description: 'independent reviewer', provider: 'spawn', context: 'fresh',
    prompt: [{ type: 'text', text: 'reviewer role only' }], signal,
  })).member
  await vi.waitFor(() => expect(h.ctx.agents.get(reviewerMember.id)).toBeUndefined())
  const reviewTask = await h.ctx.agentTeams.createTask(h.lead, { subject: 'independent review', description: 'review approved candidate' })
  const artifactText = 'approved fixture output\n'
  const evidenceText = 'fixture criterion observed: approved fixture output\n'
  const rationaleText = 'worker says output is complete; reviewer must verify independently\n'
  const bytes = new Map<string, Uint8Array>([
    ['fixture:artifact', Buffer.from(artifactText)], ['fixture:evidence', Buffer.from(evidenceText)],
    ['fixture:rationale', Buffer.from(rationaleText)],
  ])
  const artifactPath = join(h.fixture.root, 'review-artifact.txt')
  const checkPath = join(h.fixture.root, 'review-check.test.mjs')
  await writeFile(artifactPath, artifactText)
  await writeFile(checkPath, `import test from 'node:test'; import assert from 'node:assert/strict'; import { readFileSync } from 'node:fs'; test('approved fixture output bytes', () => { assert.equal(readFileSync(${JSON.stringify(artifactPath)}, 'utf8'), ${JSON.stringify(artifactText)}); });\n`)
  const checked = spawnSync(process.execPath, ['--test', checkPath], { encoding: 'utf8', timeout: 5000 })
  if (checked.error || checked.status !== 0) throw new Error(`fixture check failed: ${checked.stderr}`)
  const log = Buffer.from(checked.stdout + checked.stderr)
  bytes.set('fixture:test-log', log)
  const contract = { format: 'durable-agent-task-contract/1' as const,
    taskId: worker.taskId, revision: worker.taskRevision, outcome: 'Produce approved fixture output',
    nonGoals: ['No production changes'], inputs: [{ id: 'fixture-input', version: '1', sha256: sha('fixture input v1') }],
    outputs: [{ id: 'fixture-output', description: 'Approved fixture text' }],
    acceptance: [{ id: 'criterion-output', requirement: 'Output equals the approved fixture text',
      evidenceRequired: 'Exact artifact and independent executable check', outputIds: ['fixture-output'] }],
    authorityLimits: ['Fixture paths only'], stopConditions: ['Failed executable check'] }
  const contractSha256 = taskContractSha256(contract)
  const artifacts = [{ outputId: 'fixture-output', ref: 'fixture:artifact', sha256: sha(bytes.get('fixture:artifact')!) }]
  const proposal = { format: 'durable-agent-completion-proposal/1' as const,
    taskId: worker.taskId, contractSha256, attemptId: 'attempt-fixture-1', workerId: String(worker.memberId),
    inputs: contract.inputs, artifacts,
    evidence: [{ id: 'fixture-evidence', ref: 'fixture:evidence', sha256: sha(bytes.get('fixture:evidence')!), outputIds: ['fixture-output'] }],
    claims: [{ criterionId: 'criterion-output', evidenceIds: ['fixture-evidence'] }], blockers: [] }
  const receipt: ReviewTestReceipt = { id: 'receipt-fixture-1', suite: 'approved-output-check',
    attemptId: proposal.attemptId, contractSha256, inputs: contract.inputs, artifacts, result: 'passed',
    log: { ref: 'fixture:test-log', sha256: sha(log) } }
  const policy = { testReceipts: [receipt], requiredTestSuites: ['approved-output-check'], knownRisks: [],
    rationaleRefs: [{ id: 'rationale-1', ref: 'fixture:rationale', sha256: sha(bytes.get('fixture:rationale')!) }] }
  // Compute only the public DA proposal hash; its preflight checks the same fixture records.
  const packet = await createReviewPacket(contract, proposal, { ...policy, attemptId: proposal.attemptId,
    workerId: String(worker.memberId), reviewerId: String(reviewerMember.id),
    readRef: async ref => bytes.get(ref)!, verifyReceipt: async r => JSON.stringify(r) === JSON.stringify(receipt) })
  const auditEvents: unknown[] = []
  let revoked = false
  const listeners = new Set<() => void>()
  input = { selection: { reference: 'review-packet:fixture-1', revision: '1' },
    reviewer: undefined as never,
    candidate: { rootSessionId: h.lead.id, executionId: worker.id, sessionId: worker.sessionId,
      memberId: String(worker.memberId), generation: worker.generation, taskId: worker.taskId,
      taskRevision: worker.taskRevision, configurationSha256: '', attemptId: proposal.attemptId,
      candidateSha256: sha(workerResult), contractSha256, proposalSha256: packet.proposalSha256 },
    contract, proposal, policy, limits,
    assertCurrent: () => { if (revoked) throw new Error('fixture authority revoked') },
    subscribeRevocation(cutoff) {
      listeners.add(cutoff)
      if (revoked) cutoff()
      return () => { listeners.delete(cutoff) }
    },
    readRef: async ({ ref, maxBytes }) => {
      const value = bytes.get(ref)
      if (value === undefined || value.byteLength > maxBytes) throw new Error('ACL denied')
      return Uint8Array.from(value)
    },
    verifyReceipt: async r => checked.status === 0 && JSON.stringify(r) === JSON.stringify(receipt)
      && sha((await readFile(artifactPath))) === artifacts[0]!.sha256 && sha(bytes.get('fixture:test-log')!) === receipt.log.sha256,
    audit: async event => { auditEvents.push(event) },
  }
  // The port itself fills only the authenticated live reviewer tuple supplied by the real binding.
  resolveInput = async ({ selection, reviewer }) => {
    options.onResolve?.()
    if (options.resolveGate !== undefined) await options.resolveGate
    if (options.omit) return undefined
    const supplied = { ...input!, selection, reviewer, candidate: { ...input!.candidate,
      configurationSha256: reviewer.configurationSha256 } }
    return options.mutate?.(supplied) ?? supplied
  }
  let reviewRequest = 0
  const assignReview = (revision = '1') => {
    const current = h.ctx.agentTeams.getTask(h.lead, reviewTask.id)
    return h.ctx.agentTeams.assignTask(h.lead, { requestId: brandString(`review-request-${++reviewRequest}`),
      member: reviewerMember.name, taskId: reviewTask.id, expectedRevision: current.revision,
      brief: brief([{ reference: 'review-packet:fixture-1', revision }]), signal })
  }
  const invoke = (agent: NonNullable<ReturnType<typeof h.ctx.agents.get>>, name: string, arguments_: unknown) =>
    h.ctx.tools.execute({ name, arguments: arguments_, agent, callId: ToolCallId(`review-call-${Math.random()}`), signal })
  return { h, worker, reviewerMember, reviewTask, assignReview, invoke, auditEvents,
    revoke: () => { for (const notify of [...listeners]) notify(); revoked = true },
    replacePort: () => { h.setReviewInputPort({ ...port }) }, bytes, receipt, packet, port }
}

describe('explicit reviewer input port through real Loader/GAT/WK', () => {
  it('requires the optional registered port only for an explicit reviewer assignment', async () => {
    const h = await boot({ mode: 'hang', reviewer: true })
    const before = h.model.requests.length
    await expect(h.assign([{ reference: 'review-packet:fixture-1', revision: '1' }])).rejects.toBeDefined()
    expect(h.model.requests).toHaveLength(before)
    expect(h.reads).not.toHaveBeenCalled()
  })

  it('delivers a bounded packet and ACL evidence while making zero reviewer memory reads', async () => {
    const f = await fixture()
    const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const packet = await f.invoke(reviewer, 'review_get_packet', {})
    expect(packet.isError).toBe(false)
    expect(JSON.stringify(packet)).toContain('durable-agent-review-packet/1')
    const evidence = await f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })
    expect(evidence.isError).toBe(false); expect(JSON.stringify(evidence)).toContain('approved fixture output')
    const rationale = await f.invoke(reviewer, 'review_request_rationale', { id: 'rationale-1', reason: 'Clarify output' })
    expect(rationale.isError).toBe(false)
    expect(f.h.reads).not.toHaveBeenCalled(); expect(f.h.contexts).not.toHaveBeenCalled()
    expect(f.auditEvents.some(event => (event as { status: string }).status === 'prepared')).toBe(true)
    expect(f.auditEvents.filter(event => ['packet', 'evidence'].includes((event as { kind: string }).kind))
      .every(event => !!(event as { requestId?: string }).requestId)).toBe(true)
    expect((await f.invoke(reviewer, 'durable_agent_read_memory', { itemId: 'selected' })).isError).toBe(true)
    expect((await f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:rationale' })).isError).toBe(true)
    await f.h.ctx.agentTeams.cancelExecution(f.h.lead, execution.id)
    expect((await f.invoke(reviewer, 'review_get_packet', {})).isError).toBe(true)
  })

  it('preserves the original receiver for trusted port and input callbacks', async () => {
    const f = await fixture({ mutate: input => {
      const owned: ReviewInput = { ...input,
        assertCurrent() { if (this !== owned) throw new Error('assert receiver lost'); input.assertCurrent() },
        subscribeRevocation(cutoff) { if (this !== owned) throw new Error('subscribe receiver lost'); return input.subscribeRevocation(cutoff) },
        readRef(request) { if (this !== owned) throw new Error('reader receiver lost'); return input.readRef(request) },
        verifyReceipt(receipt) { if (this !== owned) throw new Error('receipt receiver lost'); return input.verifyReceipt(receipt) },
        audit(event) { if (this !== owned) throw new Error('audit receiver lost'); return input.audit(event) },
      }
      return owned
    } })
    const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    expect((await f.invoke(reviewer, 'review_get_packet', {})).isError).toBe(false)
    expect((await f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })).isError).toBe(false)
  })

  it.each([
    ['missing port result', { omit: true }],
    ['foreign reviewer tuple', { mutate: (i: ReviewInput) => ({ ...i, reviewer: { ...i.reviewer, memberId: 'foreign' } }) }],
    ['same member self review', { mutate: (i: ReviewInput) => ({ ...i, candidate: { ...i.candidate, memberId: i.reviewer.memberId } }) }],
    ['forged candidate hash', { mutate: (i: ReviewInput) => ({ ...i, candidate: { ...i.candidate, candidateSha256: sha('forged') } }) }],
    ['forged receipt', { mutate: (i: ReviewInput) => ({ ...i, policy: { ...i.policy, testReceipts: [{ ...i.policy.testReceipts[0]!, id: 'forged' }] } }) }],
    ['bad evidence digest', { mutate: (i: ReviewInput) => ({ ...i, readRef: async r => r.ref === 'fixture:artifact'
      ? Buffer.from('tampered output') : i.readRef(r) }) }],
    ['ACL denial', { mutate: (i: ReviewInput) => ({ ...i, readRef: async r => {
      if (r.ref === 'fixture:artifact') throw new Error('ACL denied')
      return i.readRef(r)
    } }) }],
    ['async current assertion', { mutate: (i: ReviewInput) => ({ ...i,
      assertCurrent: (async () => undefined) as unknown as () => void }) }],
    ['policy identity injection', { mutate: (i: ReviewInput) => ({ ...i,
      policy: { ...i.policy, workerId: 'foreign' } as ReviewInput['policy'] }) }],
    ['stale contract revision with matching hashes', { mutate: (i: ReviewInput) => {
      const contract = { ...i.contract, revision: i.contract.revision + 1 }
      const contractSha256 = taskContractSha256(contract)
      const proposal = { ...i.proposal, contractSha256 }
      const receipt = { ...i.policy.testReceipts[0]!, contractSha256 }
      return { ...i, contract, proposal, policy: { ...i.policy, testReceipts: [receipt] },
        candidate: { ...i.candidate, contractSha256, proposalSha256: sha(canonical(proposal)) } }
    } }],
  ])('denies %s before reviewer model dispatch', async (_name, options) => {
    const f = await fixture(options)
    const before = f.h.model.requests.length
    await expect(f.assignReview()).rejects.toBeDefined()
    expect(f.h.model.requests).toHaveLength(before)
    expect(f.h.reads).not.toHaveBeenCalled(); expect(f.h.contexts).not.toHaveBeenCalled()
  })

  it('cuts off evidence after trusted host revocation', async () => {
    const f = await fixture(); const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const before = f.h.requests(reviewer.id).length
    f.revoke()
    expect((await f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })).isError).toBe(true)
    expect(f.h.reads).not.toHaveBeenCalled()
    await vi.waitFor(() => expect(reviewer.ctx.tools.schemas().map(tool => tool.name)).not.toContain('review_get_packet'))
    expect(f.h.requests(reviewer.id)).toHaveLength(before)
  })

  it('cuts off a reviewer when the registered port changes during awaited resolution', async () => {
    const entered = Promise.withResolvers<void>(), release = Promise.withResolvers<void>()
    const f = await fixture({ onResolve: () => entered.resolve(), resolveGate: release.promise })
    const before = f.h.model.requests.length
    const pending = f.assignReview()
    await entered.promise
    f.replacePort()
    release.resolve()
    await expect(pending).rejects.toBeDefined()
    expect(f.h.model.requests).toHaveLength(before)
    expect(f.h.reads).not.toHaveBeenCalled()
  })

  it('rejects inline subscription revocation without resuming reviewer admission', async () => {
    const f = await fixture({ mutate: i => ({ ...i,
      subscribeRevocation(cutoff) { cutoff(); return () => undefined },
    }) })
    const before = f.h.model.requests.length
    await expect(f.assignReview()).rejects.toBeDefined()
    expect(f.h.model.requests).toHaveLength(before)
    expect(f.h.reads).not.toHaveBeenCalled()
  })

  it('rejects malformed asynchronous subscription and observes a late disposer', async () => {
    let disposed = false
    const f = await fixture({ mutate: i => ({ ...i,
      subscribeRevocation: (() => Promise.resolve(() => { disposed = true })) as unknown as ReviewInput['subscribeRevocation'],
    }) })
    const before = f.h.model.requests.length
    await expect(f.assignReview()).rejects.toBeDefined()
    await vi.waitFor(() => expect(disposed).toBe(true))
    expect(f.h.model.requests).toHaveLength(before)
  })

  it('joins a deferred malformed subscription cleanup before physical release', async () => {
    const entered = Promise.withResolvers<void>(), subscription = Promise.withResolvers<() => void>()
    let disposed = false
    const f = await fixture({ mutate: i => ({ ...i,
      subscribeRevocation: (() => {
        entered.resolve()
        return subscription.promise
      }) as unknown as ReviewInput['subscribeRevocation'],
    }) })
    const released = f.h.releases.mock.calls.length
    const pending = f.assignReview()
    await entered.promise
    await settleTurn()
    expect(f.h.releases).toHaveBeenCalledTimes(released)
    subscription.resolve(() => { disposed = true })
    await expect(pending).rejects.toBeDefined()
    expect(disposed).toBe(true)
    expect(f.h.releases).toHaveBeenCalledTimes(released + 1)
  })

  it('joins a deferred disposer after inline revocation without model release', async () => {
    const disposing = Promise.withResolvers<void>(), release = Promise.withResolvers<void>()
    const f = await fixture({ mutate: i => ({ ...i,
      subscribeRevocation(cutoff) {
        cutoff()
        return (() => { disposing.resolve(); return release.promise }) as () => void
      },
    }) })
    const before = f.h.model.requests.length
    const released = f.h.releases.mock.calls.length
    const pending = f.assignReview()
    try {
      await disposing.promise
      await settleTurn()
      expect(f.h.releases).toHaveBeenCalledTimes(released)
    } finally { release.resolve() }
    await expect(pending).rejects.toBeDefined()
    expect(f.h.releases).toHaveBeenCalledTimes(released + 1)
    expect(f.h.model.requests).toHaveLength(before)
  })

  it('checks current input authority across a pending reviewer request waterfall', async () => {
    const entered = Promise.withResolvers<void>(), release = Promise.withResolvers<void>()
    const f = await fixture()
    f.h.ctx.on('agent/request', async ({ agent }, next) => {
      if (f.h.ctx.agentTeams.executionFor(agent)?.memberName !== 'reviewer') return await next()
      entered.resolve()
      await release.promise
      return await next()
    })
    const execution = await f.assignReview()
    await entered.promise
    const before = f.h.requests(execution.sessionId).length
    f.revoke()
    release.resolve()
    await vi.waitFor(() => expect(f.h.releases).toHaveBeenCalledTimes(2))
    expect(f.h.requests(execution.sessionId)).toHaveLength(before)
  })

  it('cuts off a notified reviewer while real model preparation is pending', async () => {
    const f = await fixture()
    const realPrepare = f.h.ctx.llm.prepareCall.bind(f.h.ctx.llm)
    const entered = Promise.withResolvers<void>(), release = Promise.withResolvers<void>()
    vi.spyOn(f.h.ctx.llm, 'prepareCall').mockImplementation(async (...args) => {
      const prepared = await realPrepare(...args)
      entered.resolve()
      await release.promise
      return prepared
    })
    const execution = await f.assignReview()
    await entered.promise
    const reviewer = f.h.ctx.agents.get(execution.sessionId)
    if (reviewer === undefined) throw new Error('missing exact reviewer Agent')
    try {
      f.revoke()
      release.resolve()
      await reviewer.whenIdle()
      expect(f.h.requests(execution.sessionId)).toHaveLength(0)
      expect(f.h.reads).not.toHaveBeenCalled()
    } finally { release.resolve() }
  })

  it('stops retry dispatch after synchronous input revocation', async () => {
    const f = await fixture()
    const original = f.h.model.stream.bind(f.h.model)
    let reviewerCalls = 0
    vi.spyOn(f.h.model, 'stream').mockImplementation(async function* (request) {
      const agent = request.sessionId === undefined ? undefined : f.h.ctx.agents.get(request.sessionId)
      const execution = agent === undefined ? undefined : f.h.ctx.agentTeams.executionFor(agent)
      if (execution?.memberName === 'reviewer' && reviewerCalls++ === 0) {
        f.h.model.requests.push(request)
        throw new LlmError('temporary failure', 'RATE_LIMIT')
      }
      yield* original(request)
    })
    const entered = Promise.withResolvers<void>(), release = Promise.withResolvers<void>()
    f.h.ctx.on('agent/request-error', async ({ agent }, next) => {
      if (f.h.ctx.agentTeams.executionFor(agent)?.memberName !== 'reviewer') return await next()
      entered.resolve()
      await release.promise
      return { kind: 'retry' }
    })
    const execution = await f.assignReview()
    await entered.promise
    const reviewer = f.h.ctx.agents.get(execution.sessionId)
    if (reviewer === undefined) throw new Error('missing exact reviewer Agent')
    try {
      f.revoke()
      release.resolve()
      await reviewer.whenIdle()
      expect(f.h.requests(execution.sessionId)).toHaveLength(1)
      expect(reviewerCalls).toBe(1)
      expect(f.h.reads).not.toHaveBeenCalled()
    } finally { release.resolve() }
  })

  it.each(['current', 'missing', 'stale'] as const)('revalidates %s reviewer input on active checkpoint recovery', async policy => {
    const first = await fixture()
    const execution = await first.assignReview()
    const reviewer = await first.h.live(execution.sessionId)
    await first.h.ctx.sessions.flush(first.h.lead.session)
    await first.h.ctx.sessions.flush(reviewer.session)
    const checkpoint = join(first.h.fixture.root, 'reviewer-checkpoint')
    await cp(join(first.h.fixture.root, 'sessions'), checkpoint, { recursive: true })
    await first.h.ctx.fiber.dispose()
    await rm(join(first.h.fixture.root, 'sessions'), { recursive: true, force: true })
    await cp(checkpoint, join(first.h.fixture.root, 'sessions'), { recursive: true })
    const stalePort: ReviewInputPort = { async resolve(request) {
      const input = await first.port.resolve(request)
      return input === undefined ? undefined : { ...input,
        assertCurrent() { throw new Error('stale fixture authorization') } }
    } }
    const second = await boot({ mode: 'hang',
      ...policy === 'missing' ? {} : { reviewInputPort: policy === 'current' ? first.port : stalePort },
      bindingFactory: config => executionPlugin({ ...config, members: [
        { ...config.members[0]!, mode: 'task' },
        { declaration: { ...declaration, name: 'reviewer' }, mode: 'reviewer' },
      ] }),
      restart: { root: first.h.fixture.root, member: first.reviewerMember, taskId: first.reviewTask.id },
    })
    expect(second.ctx.agentTeams.getExecution(second.lead, execution.id).phase).toBe('active')
    expect(second.service).not.toBe(first.h.service)
    const resume = () => second.ctx.agentLoop.resume(second.ctx, { resumeSessionId: execution.sessionId,
      parentAgent: second.lead, agentOptions: { provider: 'mock', model: 'mock' } })
    if (policy !== 'current') {
      await expect(resume()).rejects.toBeDefined()
      expect(second.ctx.agents.get(execution.sessionId)).toBeUndefined()
      expect(second.requests(execution.sessionId)).toHaveLength(0)
      expect(second.reads).not.toHaveBeenCalled()
      return
    }
    const handle = await resume()
    expect(handle.agent).not.toBe(reviewer)
    expect(second.provisions).toHaveBeenCalledTimes(1)
    const oldRef = await first.h.provisions.mock.results.at(-1)!.value
    const newRef = await second.provisions.mock.results[0]!.value
    expect(newRef).not.toBe(oldRef)
    handle.agent.followup(createUserMessage({ source: { kind: 'user' },
      content: [{ type: 'text', text: 'Continue this exact review assignment.' }] }))
    const active = await second.live(execution.sessionId)
    expect(JSON.stringify(second.requests(execution.sessionId)[0]!.messages)).not.toContain('approved fixture output')
    const packet = await second.ctx.tools.execute({ name: 'review_get_packet', arguments: {}, agent: active,
      callId: ToolCallId('recovered-review-packet'), signal })
    expect(packet.isError).toBe(false)
    const evidence = await second.ctx.tools.execute({ name: 'review_read_evidence',
      arguments: { ref: 'fixture:artifact' }, agent: active, callId: ToolCallId('recovered-review-evidence'), signal })
    expect(evidence.isError).toBe(false)
    expect(JSON.stringify(evidence)).toContain('approved fixture output')
    expect(second.reads).not.toHaveBeenCalled()
    expect(second.contexts).not.toHaveBeenCalled()
    first.revoke()
    await vi.waitFor(() => expect(active.ctx.tools.schemas().map(tool => tool.name)).not.toContain('review_get_packet'))
  })

  it('reserves evidence call slots before concurrent callbacks', async () => {
    const f = await fixture(); const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const results = await Promise.all(Array.from({ length: 6 }, () =>
      f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })))
    expect(results.filter(result => !result.isError)).toHaveLength(4)
    expect(results.filter(result => result.isError)).toHaveLength(2)
    expect(f.auditEvents.filter(event => (event as { kind: string }).kind === 'evidence')).toHaveLength(8)
    expect(f.h.reads).not.toHaveBeenCalled()
  })

  it('accepts explicit nonnumeric revision and denies replacement of the exact trusted port', async () => {
    const f = await fixture(); const execution = await f.assignReview('approved-v1'); const reviewer = await f.h.live(execution.sessionId)
    expect((await f.invoke(reviewer, 'review_get_packet', {})).isError).toBe(false)
    f.replacePort()
    expect((await f.invoke(reviewer, 'review_get_packet', {})).isError).toBe(true)
  })

  it('sanitizes private host audit failure before tool publication', async () => {
    const f = await fixture({ mutate: i => ({ ...i, audit: async () => { throw new Error('PRIVATE_AUDIT_SENTINEL') } }) })
    const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const result = await f.invoke(reviewer, 'review_get_packet', {})
    expect(result.isError).toBe(true)
    expect(JSON.stringify(result)).not.toContain('PRIVATE_AUDIT_SENTINEL')
    expect(JSON.stringify(result.content)).toContain('Review result unavailable')
  })

  it('stops packet-construction reads at the hard allocation count', async () => {
    let calls = 0
    const f = await fixture({ mutate: i => ({ ...i,
      limits: { ...i.limits, maxPacketValidationReads: 1 },
      readRef: async request => { calls++; return i.readRef(request) },
    }) })
    await expect(f.assignReview()).rejects.toBeDefined()
    expect(calls).toBe(1)
    expect(f.h.reads).not.toHaveBeenCalled()
  })

  it('stops interactive packet calls before further host audit callbacks', async () => {
    const f = await fixture(); const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const results = await Promise.all(Array.from({ length: 18 }, () => f.invoke(reviewer, 'review_get_packet', {})))
    expect(results.filter(result => !result.isError)).toHaveLength(16)
    expect(results.filter(result => result.isError)).toHaveLength(2)
    expect(f.auditEvents.filter(event => (event as { kind: string }).kind === 'packet')).toHaveLength(32)
  })

  it('records terminal error when host allocation bound rejects evidence bytes', async () => {
    const f = await fixture({ mutate: i => ({ ...i,
      limits: { ...i.limits, maxEvidenceTotalBytes: 1 },
    }) })
    const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const result = await f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })
    expect(result.isError).toBe(true)
    expect(JSON.stringify(result.content)).toContain('Review result unavailable')
    expect(f.auditEvents.filter(event => (event as { kind: string }).kind === 'evidence')
      .map(event => (event as { status: string }).status)).toEqual(['requested', 'error'])
  })

  it('caps rationale attempts including denials and audits a hashed reason with call identity', async () => {
    const f = await fixture(); const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const first = await f.invoke(reviewer, 'review_request_rationale', { id: 'rationale-1', reason: 'Clarify output' })
    expect(first.isError).toBe(false)
    const events = f.auditEvents.filter(event => (event as { kind: string }).kind === 'rationale') as {
      requestId: string; reasonSha256: string; rationaleId: string; status: string }[]
    expect(events.map(event => event.status)).toEqual(['requested', 'prepared'])
    expect(events[0]!.requestId).toBeTruthy()
    expect(events[0]!.reasonSha256).toBe(sha('Clarify output'))
    expect(JSON.stringify(events)).not.toContain('Clarify output')
    for (let n = 0; n < 3; n++)
      expect((await f.invoke(reviewer, 'review_request_rationale', { id: 'missing', reason: ' Explain ' })).isError).toBe(true)
    const before = f.auditEvents.length
    expect((await f.invoke(reviewer, 'review_request_rationale', { id: 'rationale-1', reason: 'Over budget' })).isError).toBe(true)
    expect(f.auditEvents).toHaveLength(before)
  })

  it('withholds a delayed evidence read after current authority is revoked', async () => {
    const entered = Promise.withResolvers<void>(), release = Promise.withResolvers<void>()
    const f = await fixture({ mutate: i => ({ ...i, readRef: async request => {
      const bytes = await i.readRef(request)
      if (request.purpose === 'evidence') { entered.resolve(); await release.promise }
      return bytes
    } }) })
    const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const pending = f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })
    await entered.promise
    const released = f.h.releases.mock.calls.length
    try {
      f.revoke()
      await vi.waitFor(() => expect(reviewer.ctx.tools.schemas().map(tool => tool.name)).not.toContain('review_read_evidence'))
      await settleTurn()
      expect(f.h.releases).toHaveBeenCalledTimes(released)
    } finally { release.resolve() }
    expect((await pending).isError).toBe(true)
    expect(f.h.reads).not.toHaveBeenCalled()
    await vi.waitFor(() => expect(f.h.releases).toHaveBeenCalledTimes(released + 1))
  })

  it.each(['throwing', 'asynchronous'] as const)('releases physical storage and quarantines a %s subscription disposer', async kind => {
    const f = await fixture({ mutate: i => ({ ...i,
      subscribeRevocation(cutoff) {
        const dispose = i.subscribeRevocation(cutoff)
        return (() => {
          dispose()
          if (kind === 'throwing') throw new Error('PRIVATE_DISPOSER_SENTINEL')
          return Promise.resolve()
        }) as () => void
      },
    }) })
    f.h.fixture.tolerateCleanupFailure = true
    const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    const released = f.h.releases.mock.calls.length
    f.revoke()
    await vi.waitFor(() => expect(f.h.releases).toHaveBeenCalledTimes(released + 1))
    expect((await f.invoke(reviewer, 'review_get_packet', {})).isError).toBe(true)
    expect(f.h.reads).not.toHaveBeenCalled()
    await expect(f.h.ctx.agentTeams.cancelExecution(f.h.lead, execution.id))
      .rejects.toMatchObject({ code: 'ACTIVATION_TEARDOWN_FAILED' })
  })

  it('withholds post-execute content replacement at the final publication boundary', async () => {
    const f = await fixture(); const execution = await f.assignReview(); const reviewer = await f.h.live(execution.sessionId)
    f.h.ctx.on('tools/post-execute', async (exec, _result, next) => {
      const decision = await next()
      if (exec.agent === reviewer && exec.name === 'review_read_evidence')
        return { kind: 'accept', content: [{ type: 'text', text: 'INJECTED_REVIEW_CONTENT' }] }
      return decision
    })
    const result = await f.invoke(reviewer, 'review_read_evidence', { ref: 'fixture:artifact' })
    expect(JSON.stringify(result)).not.toContain('INJECTED_REVIEW_CONTENT')
    expect(JSON.stringify(result)).toContain('Review result unavailable')
  })

  it('allows only the real provisional GAT submission control and joins cleanup', async () => {
    const f = await fixture()
    await f.h.ctx.plugin(ToolAgentTeam, { freshProvider: 'spawn' })
    const original = f.h.model.stream.bind(f.h.model)
    let reviewCalls = 0
    vi.spyOn(f.h.model, 'stream').mockImplementation(async function* (request) {
      const agent = request.sessionId === undefined ? undefined : f.h.ctx.agents.get(request.sessionId)
      const execution = agent === undefined ? undefined : f.h.ctx.agentTeams.executionFor(agent)
      if (execution?.memberName === 'reviewer' && reviewCalls++ === 0) {
        f.h.model.requests.push(request)
        yield* toolCallResponse('review-submit', 'team_execution_submit', {
          execution_id: execution.id, outcome: 'completed', result: 'Provisional independent review observations only',
        })
        return
      }
      yield* original(request)
    })
    const execution = await f.assignReview()
    await vi.waitFor(() => expect(f.h.ctx.agentTeams.getExecution(f.h.lead, execution.id).phase).toBe('completed'), { timeout: 5000 })
    expect(reviewCalls).toBeGreaterThan(0)
    expect(f.h.ctx.agentTeams.getExecution(f.h.lead, execution.id).result).toBe('Provisional independent review observations only')
    expect(f.h.ctx.agentTeams.getTask(f.h.lead, execution.taskId).status).toBe('in_progress')
    expect(f.h.reads).not.toHaveBeenCalled()
  })
})
