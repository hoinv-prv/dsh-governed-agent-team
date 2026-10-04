/** Replay observes actual requests/lifecycles; it never dispatches Team operations. */
import type { Context } from '@deepseek-ai/cordis'

export const name = 'gat-durable-execution-model-observer'

/** Require causally complete bootstrap/submission and tool memory in subsequent actual model input. */
export function apply(ctx: Context): void {
  let rootId: string | undefined
  let executionSessionId: string | undefined
  let bootstrapClosed = false
  let executionCompleted = false
  let leadToolFailed = false
  const requests = new Map<string, number>()
  const changes = new Set<() => void>()
  ctx.on('agent/created', ({ agent }) => {
    if (agent.session.header.parentSession === undefined) rootId = String(agent.id)
  })
  ctx.on('session/event', (session, event) => {
    if (String(session.id) === rootId && event.type === 'tool/result' && event.data.message.isError === true) leadToolFailed = true
    if (event.type === 'turn/end' && String(session.id) !== rootId && String(session.id) !== executionSessionId) bootstrapClosed = true
    if (event.type === 'team/assignment' || event.type === 'team/execution') {
      const value: unknown = event.data
      if (typeof value === 'object' && value !== null && 'execution' in value) {
        const execution = value.execution
        if (typeof execution === 'object' && execution !== null && 'sessionId' in execution && typeof execution.sessionId === 'string') {
          executionSessionId = execution.sessionId
          if ('phase' in execution && execution.phase === 'completed') executionCompleted = true
        }
      }
    }
    for (const changed of changes) changed()
  })
  ctx.on('llm/stream', (options, next) => (async function* () {
    const id = String(options.sessionId)
    const call = (requests.get(id) ?? 0) + 1
    requests.set(id, call)
    const ready = (): boolean => leadToolFailed || id !== rootId || (call === 1 ? bootstrapClosed : call === 3 ? executionCompleted : true)
    if (!ready()) await new Promise<void>((resolve, reject) => {
      const cleanup = (): void => {
        changes.delete(changed)
        options.signal?.removeEventListener('abort', aborted)
      }
      const changed = (): void => { if (ready()) { cleanup(); resolve() } }
      const aborted = (): void => { cleanup(); reject(options.signal?.reason) }
      changes.add(changed)
      options.signal?.addEventListener('abort', aborted, { once: true })
      if (options.signal?.aborted) aborted()
      else changed()
    })
    if (leadToolFailed) throw new Error('authored Lead tool operation failed before the scripted lifecycle gate')
    const system = JSON.stringify(options.messages.filter(message => message.role === 'system'))
    if (/TASK_(?:SELECTED|UNSELECTED)_MEMORY_BODY|MEMORY_CATALOG_|MEMORY_INTENT_/u.test(system)) {
      throw new Error('memory entered actual system request input')
    }
    if (id === executionSessionId) {
      const selectedTool = options.messages.some(message => message.role === 'tool'
        && JSON.stringify(message.content).includes('TASK_SELECTED_MEMORY_BODY: cobalt tulip'))
      if (call === 1 && /TASK_(?:SELECTED|UNSELECTED)_MEMORY_BODY|MEMORY_CATALOG_|MEMORY_INTENT_/u.test(JSON.stringify(options.messages))) {
        throw new Error('memory was eagerly loaded before the first task request')
      }
      if (call >= 2 && !selectedTool) throw new Error('explicit selected memory missing from subsequent actual model input')
      if (JSON.stringify(options.messages).includes('TASK_UNSELECTED_MEMORY_BODY: amber fern')) {
        throw new Error('unselected memory entered actual model input')
      }
    }
    yield* next(options)
  })())
}
