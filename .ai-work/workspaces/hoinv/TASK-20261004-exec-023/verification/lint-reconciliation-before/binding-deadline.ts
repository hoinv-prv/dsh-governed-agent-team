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
  constructor(timeoutMs: number) {
    if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1) throw new TeamError('invalid lifecycle deadline', 'TEAM_INVALID_CONFIG')
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
   * Run one cleanup operation under the remaining deadline.
   * @param operation Asynchronous resource-acquisition operation.
   * @returns The callback result, or a rejection when the shared deadline expires.
   */
  async run<T>(operation: (signal: AbortSignal) => Promise<T>): Promise<T> {
    const pending = Promise.resolve().then(() => operation(this.signal))
    void pending.catch(() => undefined)
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
 * @returns The acquired resource after cancellation checks; late resources are passed to cleanup.
 */

export function acquireBindingResource<T>(operation: () => Promise<T>, signal: AbortSignal, late: (resource: T) => Promise<void>): Promise<T> {
  signal.throwIfAborted()
  return new Promise<T>((resolve, reject) => {
    let settled = false
    const onAbort = () => {
      if (settled) return
      settled = true
      signal.removeEventListener('abort', onAbort)
      reject(signal.reason)
    }
    signal.addEventListener('abort', onAbort, { once: true })
    const observed = Promise.resolve().then(operation).then(resource => {
      if (signal.aborted && !settled) onAbort()
      if (settled) return Promise.resolve().then(() => late(resource))
      // Ownership handoff and promise resolution occur in the same synchronous edge.
      settled = true
      signal.removeEventListener('abort', onAbort)
      resolve(resource)
    }, error => {
      if (!settled) {
        settled = true
        signal.removeEventListener('abort', onAbort)
        reject(error)
      }
    })
    void observed.catch(() => undefined)
  })
}
