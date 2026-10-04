/** Canonical mission revisions and host-attested HUMAN authorization commands. */
import type { Agent } from '@deepseek-ai/dsh-agent'
import { consumeHumanControl } from '@deepseek-ai/dsh-client-connection'
import { TeamError } from './error.ts'
import type { TeamJournal } from './journal.ts'
import type { TeamMembership } from './roster.ts'
import { TeamId, TeamMissionId } from './types.ts'
import type { ApproveTeamMissionRequest, CreateTeamMissionRequest, TeamMissionSnapshot, TeamMissionView } from './types.ts'
import { requiredText } from './validation.ts'

/** Owns exact mission authorization; Lead credentials alone never prove HUMAN intent. */
export class TeamMissionBoard {
  constructor(private readonly journal: TeamJournal) {}

  /**
   * Create a draft only; executable tasks are separately created on the canonical board.
   * @param membership Current Team membership projection for the Agent.
   * @param request Host-selected mission approval or transition request.
   * @returns The created mission view after the creation event is committed.
   */

  async create(membership: TeamMembership, request: CreateTeamMissionRequest): Promise<TeamMissionView> {
    if (membership.role !== 'lead') throw new TeamError('only the Team Lead can create a mission', 'TEAM_LEAD_REQUIRED')
    if (request.tasks !== undefined && !Array.isArray(request.tasks)) throw new TeamError('tasks must be an array', 'TEAM_INVALID_ARGUMENT')
    if (request.tasks?.length) throw new TeamError('create canonical tasks with explicit missionId; embedded mission task snapshots are historical only', 'TEAM_TASK_MISSION_REQUIRED')
    const { root } = membership
    return this.journal.transact(root.id, async () => {
      const state = this.journal.state(root)
      let number = 1
      while (state.missions.some(mission => mission.id === `mission-${number}`)) number += 1
      const mission: TeamMissionSnapshot = { id: TeamMissionId(`mission-${number}`), revision: 1,
        title: requiredText(request.title, 'title', 200), objective: requiredText(request.objective, 'objective', 16_384),
        status: 'draft', plan: { tasks: [], taskIds: [] }, authorizationGeneration: 0, revocationGeneration: 0 }
      await this.journal.appendAndFlush(root, 'team/mission', { version: 3, teamId: TeamId(root.id), mission })
      return structuredClone(mission)
    })
  }

  /**
   * Get one detached mission record.
   * @param membership Current Team membership projection for the Agent.
   * @param id Mission identifier to read.
   * @returns The matching mission view, or `undefined` when no mission has that id.
   */

  get(membership: TeamMembership, id: TeamMissionId): TeamMissionView {
    const mission = this.journal.state(membership.root).missions.find(value => value.id === id)
    if (!mission) throw new TeamError(`team mission "${id}" not found`, 'TEAM_MISSION_NOT_FOUND')
    return structuredClone(mission)
  }

  /**
   * List detached mission records; list order carries no execution authority.
   * @param membership Current Team membership projection for the Agent.
   * @returns The current mission views for this Team.
   */

  list(membership: TeamMembership): TeamMissionView[] {
    return this.journal.state(membership.root).missions.map(value => structuredClone(value))
  }

  /**
   * Consume the exact host-attested approval action inside the canonical transaction.
   * @param caller Host-attested caller identity.
   * @param membership Current Team membership projection for the Agent.
   * @param request Host-selected mission approval or transition request.
   * @returns The mission view after host-attested approval is committed.
   */

  async approve(caller: Agent, membership: TeamMembership, request: ApproveTeamMissionRequest): Promise<TeamMissionView> {
    return this.control(caller, membership, request, 'approveMission')
  }

  /**
   * Close or revoke the exact current mission revision.
   * @param caller Host-attested caller identity.
   * @param membership Current Team membership projection for the Agent.
   * @param request Host-selected mission approval or transition request.
   * @param action Terminal mission action to apply.
   * @returns The mission view after the requested terminal transition is committed.
   */

  async end(caller: Agent, membership: TeamMembership, request: ApproveTeamMissionRequest, action: 'closeMission' | 'revokeMission'): Promise<TeamMissionView> {
    return this.control(caller, membership, request, action)
  }

  private async control(caller: Agent, membership: TeamMembership, request: ApproveTeamMissionRequest, action: 'approveMission' | 'closeMission' | 'revokeMission'): Promise<TeamMissionView> {
    if (membership.role !== 'lead') throw new TeamError('only the Team Lead can control missions', 'TEAM_LEAD_REQUIRED')
    const { root } = membership
    return this.journal.transact(root.id, async () => {
      const current = this.get(membership, request.missionId)
      if (current.revision !== request.expectedRevision || !Number.isSafeInteger(request.expectedRevision) || request.expectedRevision < 1
        || (action === 'approveMission' ? current.status !== 'draft' : current.status === 'closed' || current.status === 'revoked')) {
        throw new TeamError('mission revision or lifecycle is stale', 'TEAM_MISSION_STALE_REVISION')
      }
      let receipt
      try { receipt = consumeHumanControl(`agentTeams/${action}`, caller, request) } catch (cause) {
        throw new TeamError('exact host-attested HUMAN control receipt required', 'TEAM_HUMAN_CONTROL_REQUIRED', { cause })
      }
      const { approval: _oldApproval, ...withoutApproval } = current
      const generation = (current.authorizationGeneration ?? 0) + 1
      const mission: TeamMissionSnapshot = action === 'approveMission'
        ? { ...current, status: 'approved', authorizationGeneration: generation,
          approval: {
            approvedRevision: current.revision, eventId: receipt.id, digest: receipt.digest,
            humanSessionId: receipt.sessionId, generation,
          } }
        : { ...withoutApproval, revision: current.revision + 1, status: action === 'closeMission' ? 'closed' : 'revoked',
          revocationGeneration: (current.revocationGeneration ?? 0) + 1 }
      await this.journal.appendAndFlush(root, 'team/mission', { version: 3, teamId: TeamId(root.id), mission })
      return structuredClone(mission)
    })
  }
}
