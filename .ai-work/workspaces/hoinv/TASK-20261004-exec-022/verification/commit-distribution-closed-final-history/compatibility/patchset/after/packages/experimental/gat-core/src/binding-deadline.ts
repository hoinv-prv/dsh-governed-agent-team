import { TeamError } from './error.ts'

/** A single total cleanup budget. Every callback is invoked, even after expiry. */
export class BindingDeadline {
  /**
   * Describe the signal used by the Team API.
   */
  readonly signal: AbortSignal
  private readonly controller = new AbortController()
  private readonly expired: Promise<never>
  private timer!: ReturnType<typeof setTimeout>
  private readonly expiresAt: number
  /**
   * Retain one bounded cleanup budget and its physical-settlement observer.
   * @param timeoutMs Total cleanup admission budget in milliseconds.
   * @param observeLateFailure Owning Team sink for rejection after the deadline expires.
   */
  constructor(timeoutMs: number, private readonly observeLateFailure?: (error: unknown) => void) {
    if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1) throw new TeamError('invalid lifecycle deadline', 'TEAM_INVALID_CONFIG')
    this.expiresAt = Date.now() + timeoutMs
    this.signal = this.controller.signal
    this.expired = new Promise((_, reject) => {
      this.timer = setTimeout(() => {
        const error = new TeamError('member binding cleanup deadline exceeded', 'TEAM_DISPOSAL_TIMEOUT')
        this.controller.abort(error); reject(error)
      }, timeoutMs)
    })
    void this.expired.catch(() => undefined)
  }

  /**
   * Read remaining total cleanup budget; exhausted callbacks receive an aborted signal.
   * @returns Positive remaining milliseconds for nested bounded cleanup.
   */
  remainingMs(): number { return Math.max(1, this.expiresAt - Date.now()) }

  /**
   * Run one cleanup operation under the remaining deadline.
   * @param operation Asynchronous resource-acquisition operation.
   * @returns The callback result, or a rejection when the shared deadline expires.
   */
  async run<T>(operation: (signal: AbortSignal) => Promise<T>): Promise<T> {
    const pending = Promise.resolve().then(() => operation(this.signal))
    void pending.catch((error: unknown) => {
      if (this.signal.aborted && error !== this.signal.reason) {
        try { this.observeLateFailure?.(error) } catch { /* failure observation cannot reopen cleanup admission */ }
      }
    })
    return await Promise.race([pending, this.expired])
  }

  /**
   * Close the deadline and release its timer resources.
   */
  finish(): void { clearTimeout(this.timer) }
}

/**
 * Cancellation closes admission promptly; late successful acquisitions still have an owner.
 * @param operation Asynchronous resource-acquisition operation.
 * @param signal Cancellation signal for the operation.
 * @param late Cleanup callback for a resource that settles after cancellation.
 * @param observeLateFailure Owning Team sink for late participant or cleanup rejection.
 * @returns The acquired resource after cancellation checks; late resources are passed to cleanup.
 */

export function acquireBindingResource<T>(
  operation: () => Promise<T>, signal: AbortSignal, late: (resource: T) => Promise<void>,
  observeLateFailure?: (error: unknown) => void,
): Promise<T> {
  signal.throwIfAborted()
  return new Promise<T>((resolve, reject) => {
    let settled = false
    const onAbort = () => {
      if (settled) return
      settled = true
      signal.removeEventListener('abort', onAbort)
      const reason: unknown = signal.reason
      const rejection = reason as Error
      reject(rejection)
    }
    signal.addEventListener('abort', onAbort, { once: true })
    const observed = Promise.resolve().then(operation).then((resource) => {
      if (signal.aborted && !settled) onAbort()
      if (settled) return Promise.resolve().then(() => late(resource))
      // Ownership handoff and promise resolution occur in the same synchronous edge.
      settled = true
      signal.removeEventListener('abort', onAbort)
      resolve(resource)
    }, (error: unknown) => {
      if (!settled) {
        settled = true
        signal.removeEventListener('abort', onAbort)
        const rejection = error as Error
        reject(rejection)
      } else if (error !== signal.reason) {
        try { observeLateFailure?.(error) } catch { /* failure observation cannot reopen cancelled admission */ }
      }
    })
    void observed.catch((error: unknown) => {
      try { observeLateFailure?.(error) } catch { /* the owner sink cannot reopen this cancelled acquisition */ }
    })
  })
}
