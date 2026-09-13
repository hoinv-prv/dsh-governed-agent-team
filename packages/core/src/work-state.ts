/** Canonical durable member-work reporting over the Team event journal. */

import type { Agent } from '@deepseek-ai/dsh-agent'
import { TeamError } from './error.ts'
import { TeamJournal } from './journal.ts'
import type { TeamMembership } from './roster.ts'
import { TeamId } from './types.ts'
import type { ReportTeamWorkRequest, TeamWorkSnapshot, TeamWorkView } from './types.ts'
import { requiredText, writeScope } from './validation.ts'

const MAX_WORK_SUMMARY_LENGTH = 4_096
const MAX_WORK_REASON_LENGTH = 4_096

function isWorkState(state: string): state is ReportTeamWorkRequest['state'] {
  return state === 'working' || state === 'blocked' || state === 'review_required' || state === 'done'
}

/** Owns validation and durable replacement of each Team member's current work state. */
export class TeamWorkBoard {
  constructor(private readonly journal: TeamJournal) {}

  /**
   * Validate, append, flush, then return the complete committed work view.
   * @param caller - member reporting its own current work state.
   * @param membership - caller's authoritative Team membership.
   * @param request - candidate durable work snapshot.
   * @returns complete committed Team work projection after the append flushes.
   */
  async report(
    caller: Agent,
    membership: TeamMembership,
    request: ReportTeamWorkRequest,
  ): Promise<TeamWorkView> {
    return this.journal.transact(membership.root.id, async () => {
      const state = this.journal.state(membership.root)
      if (membership.role === 'teammate'
        && !state.members.some(member => member.id === caller.id && member.phase === 'active')) {
        throw new TeamError(`work reporter "${membership.name}" is not active`, 'TEAM_NOT_MEMBER')
      }
      const summary = requiredText(request.summary, 'summary', MAX_WORK_SUMMARY_LENGTH)
      if (!isWorkState(request.state)) {
        throw new TeamError(`unsupported work state ${String(request.state)}`, 'TEAM_INVALID_ARGUMENT')
      }
      const reason = request.reason === undefined
        ? undefined
        : requiredText(request.reason, 'reason', MAX_WORK_REASON_LENGTH)
      if (request.state === 'blocked' && reason === undefined)
        throw new TeamError('blocked work requires a non-empty reason', 'TEAM_INVALID_ARGUMENT')
      if ((request.state === 'working' || request.state === 'done') && reason !== undefined) {
        throw new TeamError(`${request.state} work must not include a blocker reason`, 'TEAM_INVALID_ARGUMENT')
      }
      const files = request.files.map(file => writeScope(file))
      if (request.state === 'review_required' && files.length === 0) {
        throw new TeamError('review_required work requires at least one workspace-relative file', 'TEAM_INVALID_ARGUMENT')
      }
      if (new Set(files).size !== files.length)
        throw new TeamError('work files must not contain duplicates', 'TEAM_INVALID_ARGUMENT')
      if (request.taskId !== undefined) {
        const task = state.tasks.find(candidate => candidate.id === request.taskId && candidate.status !== 'deleted')
        if (task?.ownerId !== caller.id) {
          throw new TeamError(`task "${request.taskId}" is not owned by the reporting member`, 'TEAM_INVALID_ARGUMENT')
        }
      }
      const work: TeamWorkSnapshot = {
        memberId: caller.id,
        state: request.state,
        summary,
        ...reason === undefined ? {} : { reason },
        ...request.taskId === undefined ? {} : { taskId: request.taskId },
        files,
      }
      await this.journal.appendAndFlush(membership.root, 'team/work', {
        version: 2,
        teamId: TeamId(membership.root.id),
        work,
      })
      const committed = this.journal.state(membership.root).work.find(item => item.memberId === caller.id)
      if (committed === undefined) throw new Error('committed Team work state is missing from projection')
      return { ...committed, files: [...committed.files] }
    })
  }
}
