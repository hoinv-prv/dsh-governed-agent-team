import { TeamError } from '@vuhoi/gat-core'
import type { JsonValue, MemberCapabilityScope } from '@vuhoi/gat-core'
import type { DurableAgentConsumer } from '@deepseek-ai/dsh-durable-agent/consumer'
import type {
  DurableAgentMemoryCandidate,
  DurableAgentMemoryCandidateInput,
  DurableAgentMemoryItem,
} from '@deepseek-ai/dsh-durable-agent/service'

const MAX_METADATA_BYTES = 16 * 1024
const MAX_MEMORY_ITEM_BYTES = 1024 * 1024
const MAX_PROVENANCE_BYTES = 64 * 1024
const MAX_CANDIDATE_BYTES = 2 * 1024 * 1024
const MAX_READ_RESULT_BYTES = 2 * 1024 * 1024
const MAX_CANDIDATE_RESULT_BYTES = 128 * 1024
const MAX_LIMITATIONS = 64
const MEMORY_ID = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u
const CANDIDATE_KEYS = ['title', 'retrievalCondition', 'content', 'provenance', 'confidence', 'limitations'] as const

/** Closed executable model tool with immutable dispatch classification. */
export interface DurableToolDescriptor {
  readonly name: string
  /** Captured host dispatch classification, independent of the tool name. */
  readonly capability: 'read' | 'effect'
  readonly schema: JsonValue
  readonly invoke: (args: unknown) => Promise<unknown>
}

function rejected(): never {
  throw new TeamError('invalid Durable Agent tool arguments', 'TEAM_INVALID_ARGUMENT')
}

function unavailable(): never {
  throw new TeamError('Durable Agent operation failed', 'TEAM_BINDING_UNAVAILABLE')
}

function utf8Bytes(value: string): number {
  return Buffer.byteLength(value, 'utf8')
}

function text(value: unknown, maximum: number): value is string {
  return typeof value === 'string'
    && value.length > 0
    && value.trim() === value
    && !value.includes('\0')
    && utf8Bytes(value) <= maximum
}

function contentText(value: unknown, maximum: number): value is string {
  return typeof value === 'string' && !value.includes('\0') && utf8Bytes(value) <= maximum
}

function closedDataArray(value: unknown): unknown[] {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) rejected()
  const keys = Reflect.ownKeys(value)
  if (keys.some(key => typeof key !== 'string' || (key !== 'length' && !/^(?:0|[1-9][0-9]*)$/u.test(key)))) rejected()
  if (keys.length !== value.length + 1) rejected()
  const copy: unknown[] = []
  for (let index = 0; index < value.length; index += 1) {
    const descriptor = Object.getOwnPropertyDescriptor(value, String(index))
    if (descriptor === undefined || !('value' in descriptor) || descriptor.get !== undefined || descriptor.set !== undefined) rejected()
    copy.push(descriptor.value)
  }
  return copy
}

function closedDataRecord(value: unknown, expectedKeys: readonly string[]): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) rejected()
  const prototype: unknown = Object.getPrototypeOf(value)
  if (prototype !== Object.prototype && prototype !== null) rejected()
  const keys = Reflect.ownKeys(value)
  if (keys.some(key => typeof key !== 'string') || keys.length !== expectedKeys.length
    || expectedKeys.some(key => !keys.includes(key))) rejected()
  const result: Record<string, unknown> = Object.create(null) as Record<string, unknown>
  for (const key of expectedKeys) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key)
    if (descriptor === undefined || !('value' in descriptor) || descriptor.get !== undefined || descriptor.set !== undefined) rejected()
    result[key] = descriptor.value
  }
  return result
}

function candidateInput(args: unknown): DurableAgentMemoryCandidateInput {
  const input = closedDataRecord(args, CANDIDATE_KEYS)
  const limitations = closedDataArray(input.limitations)
  if (!text(input.title, MAX_METADATA_BYTES)
    || !text(input.retrievalCondition, MAX_METADATA_BYTES)
    || !contentText(input.content, MAX_MEMORY_ITEM_BYTES)
    || !text(input.provenance, MAX_PROVENANCE_BYTES)
    || !['low', 'medium', 'high'].includes(input.confidence as string)
    || limitations.length > MAX_LIMITATIONS
    || limitations.some(item => !text(item, MAX_METADATA_BYTES))) rejected()
  const normalized: DurableAgentMemoryCandidateInput = {
    title: input.title,
    retrievalCondition: input.retrievalCondition,
    content: input.content,
    provenance: input.provenance,
    confidence: input.confidence as DurableAgentMemoryCandidateInput['confidence'],
    limitations: limitations as string[],
  }
  if (utf8Bytes(JSON.stringify(normalized)) > MAX_CANDIDATE_BYTES) rejected()
  return normalized
}

function safeReadResult(value: DurableAgentMemoryItem): DurableAgentMemoryItem {
  try {
    const item = closedDataRecord(value, ['id', 'title', 'retrievalCondition', 'content', 'revision'])
    const result = {
      id: item.id as string,
      title: item.title as string,
      retrievalCondition: item.retrievalCondition as string,
      content: item.content as string,
      revision: item.revision as number,
    }
    if (!text(result.id, MAX_METADATA_BYTES) || !MEMORY_ID.test(result.id)
      || !text(result.title, MAX_METADATA_BYTES)
      || !text(result.retrievalCondition, MAX_METADATA_BYTES)
      || !contentText(result.content, MAX_MEMORY_ITEM_BYTES)
      || !Number.isSafeInteger(result.revision) || result.revision < 0
      || utf8Bytes(JSON.stringify(result)) > MAX_READ_RESULT_BYTES) unavailable()
    return result
  } catch {
    unavailable()
  }
}

function safeCandidateResult(value: DurableAgentMemoryCandidate): DurableAgentMemoryCandidate {
  try {
    const candidate = closedDataRecord(value, [
      'candidateId', 'status', 'title', 'retrievalCondition', 'provenance', 'confidence', 'limitations',
    ])
    const limitations = closedDataArray(candidate.limitations)
    const result = {
      candidateId: candidate.candidateId as string,
      status: candidate.status as 'unconfirmed',
      title: candidate.title as string,
      retrievalCondition: candidate.retrievalCondition as string,
      provenance: candidate.provenance as string,
      confidence: candidate.confidence as DurableAgentMemoryCandidate['confidence'],
      limitations: limitations as string[],
    }
    if (candidate.status !== 'unconfirmed'
      || !text(result.candidateId, MAX_METADATA_BYTES)
      || !text(result.title, MAX_METADATA_BYTES)
      || !text(result.retrievalCondition, MAX_METADATA_BYTES)
      || !text(result.provenance, MAX_PROVENANCE_BYTES)
      || !['low', 'medium', 'high'].includes(result.confidence)
      || result.limitations.length > MAX_LIMITATIONS
      || result.limitations.some(item => !text(item, MAX_METADATA_BYTES))
      || utf8Bytes(JSON.stringify(result)) > MAX_CANDIDATE_RESULT_BYTES) unavailable()
    return result
  } catch {
    unavailable()
  }
}

const readSchema: JsonValue = {
  type: 'object',
  properties: { itemId: { type: 'string', pattern: '^[a-z0-9]+(?:-[a-z0-9]+)*$', maxLength: MAX_METADATA_BYTES } },
  required: ['itemId'],
  additionalProperties: false,
}

const candidateSchema: JsonValue = {
  type: 'object',
  properties: {
    title: { type: 'string', maxLength: MAX_METADATA_BYTES },
    retrievalCondition: { type: 'string', maxLength: MAX_METADATA_BYTES },
    content: { type: 'string', maxLength: MAX_MEMORY_ITEM_BYTES },
    provenance: { type: 'string', maxLength: MAX_PROVENANCE_BYTES },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
    limitations: { type: 'array', items: { type: 'string', maxLength: MAX_METADATA_BYTES }, maxItems: MAX_LIMITATIONS },
  },
  required: [...CANDIDATE_KEYS],
  additionalProperties: false,
}

/**
 * Build the selective-read and unconfirmed-candidate model tools.
 * @param consumer Public WK Consumer bound to the exact opaque provider reference.
 * @param authorize Current authority check performed before and after each operation.
 * @returns Two closed tool descriptors without confirmed-memory authority.
 */
export function createDurableTools(
  consumer: DurableAgentConsumer,
  authorize: MemberCapabilityScope['authorize'],
): readonly DurableToolDescriptor[] {
  const read: DurableToolDescriptor = {
    name: 'durable_agent_read_memory',
    capability: 'read',
    schema: readSchema,
    invoke: async (args: unknown): Promise<unknown> => {
      const input = closedDataRecord(args, ['itemId'])
      const itemId = input.itemId
      if (!text(itemId, MAX_METADATA_BYTES) || !MEMORY_ID.test(itemId)) rejected()
      authorize('read')
      let item: DurableAgentMemoryItem
      try {
        item = await consumer.readMemory(itemId)
      } catch {
        unavailable()
      }
      authorize('read')
      return safeReadResult(item)
    },
  }
  const submit: DurableToolDescriptor = {
    name: 'durable_agent_submit_candidate',
    capability: 'effect',
    schema: candidateSchema,
    invoke: async (args: unknown): Promise<unknown> => {
      const input = candidateInput(args)
      authorize('effect')
      let result: DurableAgentMemoryCandidate
      try {
        result = await consumer.submitUnconfirmedCandidate(input)
      } catch {
        unavailable()
      }
      authorize('effect')
      return safeCandidateResult(result)
    },
  }
  return Object.freeze([Object.freeze(read), Object.freeze(submit)])
}
