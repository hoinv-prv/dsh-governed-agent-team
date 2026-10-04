export const DURABLE_AGENT_ERROR_CODES = [
  'INCOMPATIBLE_API',
  'INVALID_DECLARATION',
  'UNAUTHORIZED_REFERENCE',
  'PROFILE_CONFLICT',
  'UNSUPPORTED_SCOPE',
  'INVALID_CONTEXT_DATA',
  'UNKNOWN_MEMORY_ITEM',
  'REJECTED_CANDIDATE',
  'CONCURRENT_MUTATION',
  'PROVIDER_UNAVAILABLE',
] as const

export type DurableAgentErrorCode = typeof DURABLE_AGENT_ERROR_CODES[number]

export type DurableAgentReferenceState =
  | 'missing'
  | 'foreign'
  | 'forged'
  | 'stale'
  | 'scope-mismatch'
  | 'released'

/** Deliberately path-free diagnostic values safe to return across the service boundary. */
export interface DurableAgentErrorDetails {
  readonly memberName?: string
  readonly apiVersion?: number
  readonly feature?: string
  readonly scope?: 'workspace' | 'global'
  readonly referenceState?: DurableAgentReferenceState
}

const ERROR_MESSAGES: Readonly<Record<DurableAgentErrorCode, string>> = Object.freeze({
  INCOMPATIBLE_API: 'The Durable Agent API version is incompatible.',
  INVALID_DECLARATION: 'The Durable Agent declaration is invalid.',
  UNAUTHORIZED_REFERENCE: 'The Durable Agent reference is not authorized.',
  PROFILE_CONFLICT: 'The Durable Agent profile conflicts with the declaration.',
  UNSUPPORTED_SCOPE: 'The requested Durable Agent scope is unsupported.',
  INVALID_CONTEXT_DATA: 'The Durable Agent context data is invalid.',
  UNKNOWN_MEMORY_ITEM: 'The requested Durable Agent memory item is unknown.',
  REJECTED_CANDIDATE: 'The Durable Agent memory candidate was rejected.',
  CONCURRENT_MUTATION: 'The Durable Agent mutation could not be serialized.',
  PROVIDER_UNAVAILABLE: 'The Durable Agent provider is unavailable.',
})

/**
 * Public service error with a stable semantic code and path-free diagnostics.
 * Provider causes, storage paths, content, and stack data are intentionally absent
 * from the serializable representation.
 */
function safeErrorDetails(details: DurableAgentErrorDetails): Readonly<DurableAgentErrorDetails> {
  const safe: {
    memberName?: string
    apiVersion?: number
    feature?: string
    scope?: 'workspace' | 'global'
    referenceState?: DurableAgentReferenceState
  } = {}
  if (details.memberName !== undefined && /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/u.test(details.memberName)) safe.memberName = details.memberName
  if (details.apiVersion !== undefined && Number.isSafeInteger(details.apiVersion) && details.apiVersion >= 0) safe.apiVersion = details.apiVersion
  if (details.feature !== undefined && /^[A-Za-z][A-Za-z0-9]*$/u.test(details.feature)) safe.feature = details.feature
  if (details.scope === 'workspace' || details.scope === 'global') safe.scope = details.scope
  if (details.referenceState !== undefined && ['missing', 'foreign', 'forged', 'stale', 'scope-mismatch', 'released'].includes(details.referenceState)) {
    safe.referenceState = details.referenceState
  }
  return Object.freeze(safe)
}

export class DurableAgentError extends Error {
  override readonly name = 'DurableAgentError'
  readonly code: DurableAgentErrorCode
  readonly details: Readonly<DurableAgentErrorDetails>

  constructor(code: DurableAgentErrorCode, details: DurableAgentErrorDetails = {}) {
    super(ERROR_MESSAGES[code])
    this.code = code
    this.details = safeErrorDetails(details)
  }

  toJSON(): Readonly<{
    name: 'DurableAgentError'
    code: DurableAgentErrorCode
    message: string
    details: Readonly<DurableAgentErrorDetails>
  }> {
    return Object.freeze({
      name: 'DurableAgentError',
      code: this.code,
      message: this.message,
      details: this.details,
    })
  }
}

export function isDurableAgentError(value: unknown): value is DurableAgentError {
  return value instanceof DurableAgentError
}
