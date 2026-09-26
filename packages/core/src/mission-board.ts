/** Independently governed durable Team mission commands. */

import type { Agent } from '@deepseek-ai/dsh-agent'
import { TeamError } from './error.ts'
import type { TeamJournal } from './journal.ts'
import type { TeamMembership } from './roster.ts'
import { TeamId, TeamMissionId } from './types.ts'
import type {
  ApproveTeamMissionRequest,
  CreateTeamMissionRequest,
  TeamMissionSnapshot,
  TeamMissionView,
} from './types.ts'
import { assertInitialMissionTaskPlan } from './mission-plan.ts'
import { requiredText } from './validation.ts'

/** Owns mission identity, authorization, revision, and approval boundaries. */
export class TeamMissionBoard {
  constructor(private readonly journal: TeamJournal) {}

  /** Create one mission with its initial revision already authorized by the current baseline flow. */
  async create(membership: TeamMembership, request: CreateTeamMissionRequest): Promise<TeamMissionView> {
    if (membership.role !== 'lead') throw new TeamError('only the Team Lead can create a mission', 'TEAM_LEAD_REQUIRED')
    const { root } = membership
    return this.journal.transact(root.id, async () => {
      const state = this.journal.state(root)
      const id = this.nextId(state.missions.map(mission => mission.id))
      const tasks = structuredClone(request.tasks ?? [])
      assertInitialMissionTaskPlan(tasks)
      const mission: TeamMissionSnapshot = {
        id,
        revision: 1,
        title: requiredText(request.title, 'title', 200),
        objective: requiredText(request.objective, 'objective', 16_384),
        status: 'approved',
        plan: { tasks },
        approval: { approvedRevision: 1 },
      }
      await this.journal.appendAndFlush(root, 'team/mission', {
        version: 2,
        teamId: TeamId(root.id),
        mission,
      })
      return structuredClone(mission)
    })
  }

  /** Get one detached mission record. */
  get(membership: TeamMembership, id: TeamMissionId): TeamMissionView {
    const mission = this.journal.state(membership.root).missions.find(candidate => candidate.id === id)
    if (mission === undefined) throw new TeamError(`team mission "${id}" not found`, 'TEAM_MISSION_NOT_FOUND')
    return structuredClone(mission)
  }

  /** List detached Team mission records in creation order. */
  list(membership: TeamMembership): TeamMissionView[] {
    return this.journal.state(membership.root).missions.map(mission => structuredClone(mission))
  }

  /** Approve exactly the current mission revision; only the Team Lead may approve. */
  async approve(_caller: Agent, membership: TeamMembership, request: ApproveTeamMissionRequest): Promise<TeamMissionView> {
    if (membership.role !== 'lead') throw new TeamError('only the Team Lead can approve a mission', 'TEAM_LEAD_REQUIRED')
    const { root } = membership
    return this.journal.transact(root.id, async () => {
      const state = this.journal.state(root)
      const current = state.missions.find(mission => mission.id === request.missionId)
      if (current === undefined) throw new TeamError(`team mission "${request.missionId}" not found`, 'TEAM_MISSION_NOT_FOUND')
      if (!Number.isSafeInteger(request.expectedRevision) || request.expectedRevision < 1) {
        throw new TeamError('expectedRevision must be a positive safe integer', 'TEAM_INVALID_ARGUMENT')
      }
      if (current.revision !== request.expectedRevision || current.status !== 'draft') {
        throw new TeamError(
          `stale Team mission "${current.id}" revision ${request.expectedRevision}; current revision is ${current.revision}`,
          'TEAM_MISSION_STALE_REVISION',
        )
      }
      const mission: TeamMissionSnapshot = {
        ...current,
        revision: current.revision + 1,
        status: 'approved',
        approval: { approvedRevision: current.revision + 1 },
      }
      await this.journal.appendAndFlush(root, 'team/mission', {
        version: 2,
        teamId: TeamId(root.id),
        mission,
      })
      return structuredClone(mission)
    })
  }

  private nextId(existing: readonly TeamMissionId[]): TeamMissionId {
    let number = 1
    const seen = new Set(existing.map(String))
    while (seen.has(`mission-${number}`)) number += 1
    return TeamMissionId(`mission-${number}`)
  }
}
