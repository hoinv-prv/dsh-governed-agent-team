import { describe, expect, it, vi } from 'vitest'
import { TeamError } from '@vuhoi/gat-core'
import type { DurableAgentConsumer } from '@deepseek-ai/dsh-durable-agent/consumer'
import type { DurableAgentMemoryCandidateInput } from '@deepseek-ai/dsh-durable-agent/service'
import { createDurableTools } from '../src/tools.ts'

function consumerMock(overrides: Record<string, unknown> = {}): DurableAgentConsumer {
  return {
    readMemory: vi.fn(async () => ({
      id: 'architecture', title: 'Architecture', retrievalCondition: 'When design is needed',
      content: 'Bounded memory body.', revision: 3,
    })),
    submitUnconfirmedCandidate: vi.fn(async (input: DurableAgentMemoryCandidateInput) => ({
      candidateId: 'candidate-1', status: 'unconfirmed', title: input.title,
      retrievalCondition: input.retrievalCondition, provenance: input.provenance,
      confidence: input.confidence, limitations: [...input.limitations],
    })),
    ...overrides,
  } as unknown as DurableAgentConsumer
}

function candidate(overrides: Record<string, unknown> = {}) {
  return {
    title: 'Useful note',
    retrievalCondition: 'When this topic appears',
    content: 'A candidate body.',
    provenance: 'Observed during a task',
    confidence: 'medium',
    limitations: ['Needs review'],
    ...overrides,
  }
}

describe('Durable Agent model tools', () => {
  it('exposes only the read and unconfirmed-candidate tools', () => {
    const tools = createDurableTools(consumerMock(), vi.fn())
    expect(tools.map(tool => tool.name)).toEqual([
      'durable_agent_read_memory', 'durable_agent_submit_candidate',
    ])
    expect(tools.map(tool => tool.schema)).toEqual(expect.arrayContaining([
      expect.objectContaining({ additionalProperties: false }),
    ]))
  })

  it('rejects malformed read and candidate arguments without calling the Consumer', async () => {
    const consumer = consumerMock()
    const authorize = vi.fn()
    const [read, submit] = createDurableTools(consumer, authorize)
    if (read === undefined || submit === undefined) throw new Error('expected the two Durable tools')

    await expect(read.invoke({ itemId: 'bad_id' })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(read.invoke({ itemId: 'architecture', ref: 'injected' })).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    const getter = Object.defineProperty({}, 'itemId', { enumerable: true, get: () => { throw new Error('getter ran') } })
    await expect(read.invoke(getter)).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(submit.invoke(candidate({ authorized: true }))).rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    await expect(submit.invoke(candidate({ content: 'x'.repeat(1024 * 1024 + 1) })))
      .rejects.toMatchObject({ code: 'TEAM_INVALID_ARGUMENT' })
    expect(consumer.readMemory).not.toHaveBeenCalled()
    expect(consumer.submitUnconfirmedCandidate).not.toHaveBeenCalled()
    expect(authorize).not.toHaveBeenCalled()
  })

  it('checks live authority before and after an asynchronous read', async () => {
    const consumer = consumerMock()
    const authorizationError = new TeamError('stale scope', 'TEAM_BINDING_UNAVAILABLE')
    const authorize = vi.fn()
      .mockImplementationOnce(() => undefined)
      .mockImplementationOnce(() => { throw authorizationError })
    const [read] = createDurableTools(consumer, authorize)
    if (read === undefined) throw new Error('expected the read tool')

    await expect(read.invoke({ itemId: 'architecture' })).rejects.toBe(authorizationError)
    expect(consumer.readMemory).toHaveBeenCalledOnce()
    expect(authorize.mock.calls).toEqual([['read'], ['read']])
  })

  it('authorizes before effects and returns only an explicitly unconfirmed candidate', async () => {
    const consumer = consumerMock()
    const authorize = vi.fn()
    const [, submit] = createDurableTools(consumer, authorize)
    if (submit === undefined) throw new Error('expected the submit tool')

    await expect(submit.invoke(candidate())).resolves.toMatchObject({
      candidateId: 'candidate-1', status: 'unconfirmed', title: 'Useful note',
    })
    expect(consumer.submitUnconfirmedCandidate).toHaveBeenCalledWith(candidate())
    expect(authorize.mock.calls).toEqual([['effect'], ['effect']])
  })

  it('does not call the Consumer when pre-authorization is stale', async () => {
    const consumer = consumerMock()
    const authorizationError = new TeamError('revoked', 'TEAM_BINDING_UNAVAILABLE')
    const authorize = vi.fn(() => { throw authorizationError })
    const [, submit] = createDurableTools(consumer, authorize)

    await expect(submit?.invoke(candidate())).rejects.toBe(authorizationError)
    expect(consumer.submitUnconfirmedCandidate).not.toHaveBeenCalled()
    expect(authorize).toHaveBeenCalledOnce()
  })

  it('withholds a read result that exceeds the public response bound', async () => {
    const consumer = consumerMock({
      readMemory: vi.fn(async () => ({
        id: 'architecture', title: 'Architecture', retrievalCondition: 'When design is needed',
        content: 'x'.repeat(1024 * 1024 + 1), revision: 3,
      })),
    })
    const [read] = createDurableTools(consumer, vi.fn())

    await expect(read?.invoke({ itemId: 'architecture' })).rejects.toMatchObject({
      code: 'TEAM_BINDING_UNAVAILABLE', message: 'Durable Agent operation failed',
    })
  })
})
