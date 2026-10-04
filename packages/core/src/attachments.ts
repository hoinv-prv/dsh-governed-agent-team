/** Frozen required-attachment validation, canonical value detachment and digest integrity. */
import { createHash } from 'node:crypto'
import { TeamError } from './error.ts'
import type { JsonValue, TeamMemberAttachmentRecord, TeamMemberAttachmentRequest } from './types.ts'

/** Set the fixed limits for required member attachments. */
export const ATTACHMENT_LIMITS = Object.freeze({
  records: 8, recordBytes: 65_536, aggregateBytes: 262_144,
  depth: 16, nodes: 4_096, stringBytes: 16_384, binderId: 64,
})

function invalid(): never {
  throw new TeamError('invalid or oversized required member attachment', 'TEAM_INVALID_ATTACHMENT')
}

function validString(value: string): string {
  if (Buffer.byteLength(value, 'utf8') > ATTACHMENT_LIMITS.stringBytes) invalid()
  // RFC 8785 requires rejection, not replacement, of lone Unicode surrogates.
  for (let i = 0; i < value.length; i++) {
    const c = value.charCodeAt(i)
    if (c >= 0xd800 && c <= 0xdbff) {
      const next = value.charCodeAt(++i)
      if (!(next >= 0xdc00 && next <= 0xdfff)) invalid()
    } else if (c >= 0xdc00 && c <= 0xdfff) invalid()
  }
  return value
}

/**
 * Read only own data descriptors; never invoke a caller's accessor or toJSON.
 * @param value Value to validate or normalize.
 * @param depth Current JSON nesting depth.
 * @param budget Shared node-count budget for the detached value.
 * @param ancestors Objects on the current traversal path.
 * @returns A detached, recursively frozen plain JSON value.
 */

export function detachJson(value: unknown, depth = 0, budget = { nodes: 0 }, ancestors = new Set<object>()): JsonValue {
  if (depth > ATTACHMENT_LIMITS.depth || ++budget.nodes > ATTACHMENT_LIMITS.nodes) invalid()
  if (value === null || typeof value === 'boolean') return value
  if (typeof value === 'string') return validString(value)
  if (typeof value === 'number') { if (!Number.isFinite(value)) invalid(); return Object.is(value, -0) ? 0 : value }
  if (typeof value !== 'object' || ancestors.has(value)) invalid()
  const prototype: unknown = Object.getPrototypeOf(value)
  if (Array.isArray(value) ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null) invalid()
  ancestors.add(value)
  try {
    const descriptors = Object.getOwnPropertyDescriptors(value)
    if (Object.getOwnPropertySymbols(value).length > 0) invalid()
    if (Array.isArray(value)) {
      const keys = Object.keys(descriptors)
      if (keys.length !== value.length + 1 || !keys.includes('length')) invalid()
      const result: JsonValue[] = []
      for (let i = 0; i < value.length; i++) {
        const entry = descriptors[String(i)]
        if (!entry || !('value' in entry) || !entry.enumerable) invalid()
        result.push(detachJson(entry.value, depth + 1, budget, ancestors))
      }
      return Object.freeze(result) as JsonValue[]
    }
    const result: Record<string, JsonValue> = {}
    for (const key of Object.keys(descriptors).sort()) {
      validString(key)
      const entry = descriptors[key] as PropertyDescriptor
      if (!('value' in entry) || !entry.enumerable) invalid()
      Object.defineProperty(result, key, { value: detachJson(entry.value, depth + 1, budget, ancestors), enumerable: true })
    }
    return Object.freeze(result)
  } finally { ancestors.delete(value) }
}

function encode(value: JsonValue): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value)
  if (Array.isArray(value)) return `[${value.map(encode).join(',')}]`
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${encode(value[key] as JsonValue)}`).join(',')}}`
}

/**
 * RFC 8785 UTF-16 key order and ECMAScript number/string rendering.
 * @param value Value to validate or normalize.
 * @returns The RFC 8785 canonical JSON string.
 */

export function canonicalJson(value: unknown): string { return encode(detachJson(value)) }

/**
 * Compute the SHA-256 digest of a canonical JSON payload.
 * @param value Value to validate or normalize.
 * @returns The lowercase SHA-256 hex digest of the canonical JSON payload.
 */
export function payloadSha256(value: unknown): string { return createHash('sha256').update(canonicalJson(value), 'utf8').digest('hex') }

function envelope(value: unknown, replay: boolean, budget: { nodes: number }): TeamMemberAttachmentRecord | TeamMemberAttachmentRequest {
  const detached = detachJson(value, 0, budget)
  if (detached === null || typeof detached !== 'object' || Array.isArray(detached)) invalid()
  const expected = replay ? ['binderId', 'payload', 'payloadSha256', 'protocolVersion', 'required'] : ['binderId', 'payload', 'protocolVersion', 'required']
  if (Object.keys(detached).join('|') !== expected.join('|')) invalid()
  const { binderId, protocolVersion, required, payload } = detached
  if (typeof binderId !== 'string' || binderId.length > ATTACHMENT_LIMITS.binderId || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(binderId)) invalid()
  if (typeof protocolVersion !== 'number' || !Number.isSafeInteger(protocolVersion) || protocolVersion < 1 || required !== true) invalid()
  if (Buffer.byteLength(encode(detached), 'utf8') > ATTACHMENT_LIMITS.recordBytes) invalid()
  if (replay && (typeof detached.payloadSha256 !== 'string' || !/^[a-f0-9]{64}$/u.test(detached.payloadSha256) || detached.payloadSha256 !== payloadSha256(payload))) invalid()
  return detached as unknown as TeamMemberAttachmentRecord | TeamMemberAttachmentRequest
}

function validateList(values: unknown, replay: boolean): readonly (TeamMemberAttachmentRecord | TeamMemberAttachmentRequest)[] {
  if (!Array.isArray(values) || Object.getPrototypeOf(values) !== Array.prototype || values.length > ATTACHMENT_LIMITS.records) invalid()
  // Check list descriptors without traversing payloads twice or invoking accessors.
  const descriptors = Object.getOwnPropertyDescriptors(values)
  if (Reflect.ownKeys(descriptors).length !== values.length + 1) invalid()
  const budget = { nodes: 0 }
  const names = new Set<string>()
  const result = Array.from({ length: values.length }, (_, index) => {
    const descriptor = descriptors[String(index)]
    if (!descriptor || !('value' in descriptor) || !descriptor.enumerable) invalid()
    const record = envelope(descriptor.value, replay, budget)
    if (names.has(record.binderId)) invalid()
    names.add(record.binderId)
    return record
  })
  if (Buffer.byteLength(`[${result.map(value => encode(value as unknown as JsonValue)).join(',')}]`, 'utf8') > ATTACHMENT_LIMITS.aggregateBytes) invalid()
  return Object.freeze(result)
}


/**
 * Validate and detach required attachment requests.
 * @param value Value to validate or normalize.
 * @returns A frozen list of validated required attachment requests.
 */
export function validateAttachmentRequests(value: unknown): readonly TeamMemberAttachmentRequest[] {
  return validateList(value, false)
}

/**
 * Validate persisted attachment records and their payload digests.
 * @param value Value to validate or normalize.
 * @returns A frozen list of persisted records with verified payload digests.
 */
export function validateAttachmentRecords(value: unknown): readonly TeamMemberAttachmentRecord[] {
  return validateList(value, true) as readonly TeamMemberAttachmentRecord[]
}

/**
 * Build a persisted attachment record from the binder-prepared payload.
 * @param request Host-selected mission approval or transition request.
 * @param preparedPayload Payload returned by the binder prepare callback for durable persistence.
 * @returns The detached attachment record with its computed payload digest.
 */
export function attachmentRecord(request: TeamMemberAttachmentRequest, preparedPayload: unknown): TeamMemberAttachmentRecord {
  const payload = detachJson(preparedPayload)
  const record = {
    binderId: request.binderId, protocolVersion: request.protocolVersion,
    required: true, payload, payloadSha256: payloadSha256(payload),
  }
  return validateAttachmentRecords([record])[0] as TeamMemberAttachmentRecord
}
