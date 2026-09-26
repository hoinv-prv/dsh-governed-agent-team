/** Serialized Team transactions over the exact live Lead Session log. */

import type { Agent } from '@deepseek-ai/dsh-agent'
import type { Context } from '@deepseek-ai/cordis'
import type { SessionEventMap, SessionId } from '@deepseek-ai/dsh-session'
import type { TeamEventType, TeamState } from './projection.ts'

type AppendTeamEvent = <T extends TeamEventType>(type: T, data: SessionEventMap[T]) => void
type MutableTeamEventType =
  | 'team/member'
  | 'team/task'
  | 'team/mission'
  | 'team/plan-approved'
  | 'team/work'
  | 'team/message/queued'
  | 'team/message/delivered'

type PendingTeamEvent = {
  [T in MutableTeamEventType]: { readonly type: T; readonly data: SessionEventMap[T] }
}[MutableTeamEventType]

/** Owns per-Lead transaction order and committed Team event publication. */
export class TeamJournal {
  private readonly tails = new Map<SessionId, Promise<void>>()

  /**
   * @param ctx - Team service context with the injected Session service.
   * @param onCommit - synchronous notification after the Team event flush succeeds.
   */
  constructor(
    private readonly ctx: Context,
    private readonly onCommit: (root: Agent) => void,
  ) {}

  /**
   * Read authoritative Team state for one exact live Lead.
   * @param root - exact live Team Lead.
   * @returns current projected state selected by the Lead Team id.
   */
  state(root: Agent): TeamState {
    const projection = this.ctx.sessionProjections.stateOf(root.session, 'agentTeam')
    if (projection === undefined) throw new Error('Agent Teams projection is not registered')
    if (projection.failure !== undefined) throw new Error(projection.failure)
    return projection
  }

  /**
   * Serialize one Lead's asynchronous mutation operation.
   * @param rootId - Lead Session identity selecting the transaction queue.
   * @param operation - complete read-check-append operation.
   * @returns the operation result.
   */
  async transact<T>(rootId: SessionId, operation: () => Promise<T>): Promise<T> {
    const prior = this.tails.get(rootId) ?? Promise.resolve()
    const run = prior.then(operation, operation)
    const tail = run.then(() => undefined, () => undefined)
    this.tails.set(rootId, tail)
    try {
      return await run
    } finally {
      if (this.tails.get(rootId) === tail) this.tails.delete(rootId)
    }
  }

  /**
   * Append and checkpoint one root-owned Team event before publication.
   * @param root - exact live Lead whose Session owns the event.
   * @param type - Team event discriminant.
   * @param data - payload correlated with the event type.
   */
  async appendAndFlush<T extends MutableTeamEventType>(
    root: Agent,
    type: T,
    data: SessionEventMap[T],
  ): Promise<void> {
    await this.appendManyAndFlush(root, [{ type, data }] as unknown as PendingTeamEvent[])
  }

  /**
   * Append several already-validated Team events, then checkpoint them in one
   * flush and publish only after that flush succeeds. Callers must make all
   * validation decisions before this method so an invalid batch never appends
   * any prefix.
   */
  async appendManyAndFlush(root: Agent, events: readonly PendingTeamEvent[]): Promise<void> {
    // Team events never enter the conversation surface. This narrower local
    // capability removes Session.append's conditional surface argument while
    // preserving the event-key/payload correlation.
    const append = root.session.append.bind(root.session) as unknown as AppendTeamEvent
    for (const event of events) append(event.type, event.data)
    await this.ctx.sessions.flush(root.session)
    this.onCommit(root)
  }
}
