import { describe, expect, it } from 'vitest'
import { SESSION_FORMAT_VERSION, SessionId, SessionSeq } from '@deepseek-ai/dsh-session'
import type { SessionEvent, SessionEventMap, SessionEventType } from '@deepseek-ai/dsh-session'
import { emptyTeamState, teamProjectionDefinition } from '../src/projection.ts'
import type { TeamProjectionState, TeamState } from '../src/projection.ts'
import { isStructuralTaskMutation } from '../src/task-board.ts'
import { TeamId, TeamMessageId, TeamTaskId } from '../src/types.ts'
import type { TeamMemberSnapshot, TeamMessageSnapshot, TeamTaskSnapshot } from '../src/types.ts'

const ROOT = SessionId('team-root')
const TEAM = TeamId(ROOT)
const CHILD = SessionId('child-a')

function event<T extends Extract<SessionEventType, `team/${string}`>>(type: T, data: SessionEventMap[T], seq: SessionSeq): SessionEvent<T> {
  return { type, data, seq, time: seq } as unknown as SessionEvent<T>
}

function project(rootId: SessionId, events: readonly SessionEvent[]): TeamProjectionState {
  let state = teamProjectionDefinition.init({
    version: SESSION_FORMAT_VERSION,
    id: rootId,
    createdAt: 0,
    isSeeded: false,
  })
  for (const event of events) state = teamProjectionDefinition.apply(state, event)
  return state
}

function teamState(projected: TeamProjectionState): TeamState {
  if (projected.failure !== undefined) throw new Error(projected.failure)
  return projected
}

function projectTeam(rootId: SessionId, events: readonly SessionEvent[]): TeamState {
  return teamState(project(rootId, events))
}

/** Queued-minus-delivered mail retained by the projection. */
function pending(state: TeamState): TeamMessageSnapshot[] {
  return state.messages.filter(message => !state.delivered.includes(message.id))
}

/** Whether one Team state contains no projected records. */
function isEmptyState(state: TeamState): boolean {
  return state.members.length === 0 && state.tasks.length === 0
    && state.messages.length === 0 && state.delivered.length === 0
}

function member(overrides: Partial<TeamMemberSnapshot> = {}): TeamMemberSnapshot {
  return {
    id: CHILD,
    name: 'worker-a',
    description: 'worker',
    provider: 'spawn',
    context: 'fresh',
    phase: 'provisioning',
    ...overrides,
  }
}

function task(overrides: Partial<TeamTaskSnapshot> = {}): TeamTaskSnapshot {
  return {
    id: TeamTaskId('task-1'),
    revision: 1,
    subject: 'subject',
    description: 'description',
    status: 'pending',
    blockedBy: [],
    writeScopes: [],
    ...overrides,
  }
}

function message(overrides: Partial<TeamMessageSnapshot> = {}): TeamMessageSnapshot {
  return {
    id: TeamMessageId('message-1'),
    senderId: ROOT,
    senderName: 'lead',
    targetId: CHILD,
    content: [{ type: 'text', text: 'hello' }],
    ...overrides,
  }
}

describe('Agent Teams projection events', () => {
  it('starts a new Team plan at revision zero in draft without approval', () => {
    const state = projectTeam(ROOT, [])

    expect(state.planRevision).toBe(0)
    expect(state.planPhase).toBe('draft')
    expect(state.planApproval).toBeUndefined()
  })

  it('rejects cached plan phases that contradict revision-bound approval', () => {
    const base = { ...emptyTeamState(ROOT), planRevision: 1 }
    const contradictory = [
      { ...base, planPhase: 'approved' },
      { ...base, planPhase: 'approved', planApproval: { approvedRevision: 0 } },
      { ...base, planPhase: 'draft', planApproval: { approvedRevision: 1 } },
      { ...base, planPhase: 'draft', planApproval: { approvedRevision: 2 } },
    ]

    for (const checkpoint of contradictory) {
      expect(() => teamProjectionDefinition.stateSchema.parse(checkpoint))
        .toThrow('planPhase must be approved exactly when approval matches planRevision')
    }
  })

  it('classifies structural task snapshots independently from execution state', () => {
    const current = task()
    for (const structural of [
      { ...current, revision: 2, subject: 'changed' },
      { ...current, revision: 2, description: 'changed' },
      { ...current, revision: 2, blockedBy: [TeamTaskId('task-2')] },
      { ...current, revision: 2, writeScopes: ['packages/experimental'] },
      { ...current, revision: 2, status: 'deleted' as const },
    ]) expect(isStructuralTaskMutation(current, structural)).toBe(true)

    expect(isStructuralTaskMutation(undefined, current)).toBe(true)
    for (const executionOnly of [
      { ...current, revision: 2, status: 'in_progress' as const, ownerId: CHILD },
      { ...current, revision: 2, ownerId: CHILD },
      { ...current, revision: 2, status: 'completed' as const },
    ]) expect(isStructuralTaskMutation(current, executionOnly)).toBe(false)
    expect(isStructuralTaskMutation(current, { ...current, revision: 2 })).toBe(false)
  })

  it('derives plan revision only from committed structural task events', () => {
    const created = task()
    const claimed = { ...created, revision: 2, status: 'in_progress' as const, ownerId: CHILD }
    const completed = { ...claimed, revision: 3, status: 'completed' as const }
    const edited = { ...completed, revision: 4, subject: 'changed' }
    const state = projectTeam(ROOT, [
      event('team/task', { version: 2, teamId: TEAM, task: created }, SessionSeq(0)),
      event('team/task', { version: 2, teamId: TEAM, task: claimed }, SessionSeq(1)),
      event('team/task', { version: 2, teamId: TEAM, task: completed }, SessionSeq(2)),
      event('team/task', { version: 2, teamId: TEAM, task: edited }, SessionSeq(3)),
    ])

    expect(state.planRevision).toBe(2)
  })

  it('projects exact-revision approval and derives staleness after a structural mutation', () => {
    const created = task()
    const approval = {
      type: 'team/plan-approved',
      data: { version: 2, teamId: TEAM, approval: { approvedRevision: 1 } },
      seq: SessionSeq(1),
      time: 10,
    } as unknown as SessionEvent
    const state = projectTeam(ROOT, [
      event('team/task', { version: 2, teamId: TEAM, task: created }, SessionSeq(0)),
      approval,
    ])

    expect(state.planApproval).toEqual({ approvedRevision: 1 })
    expect(state.planPhase).toBe('approved')

    const stale = teamProjectionDefinition.apply(state, event('team/task', {
      version: 2,
      teamId: TEAM,
      task: { ...created, revision: 2, subject: 'changed' },
    }, SessionSeq(2)))
    expect(stale.planApproval).toEqual({ approvedRevision: 1 })
    expect(stale.planRevision).toBe(2)
    expect(stale.planPhase).toBe('draft')
  })

  it('projects the latest member work state with event-envelope time', () => {
    const provisioning = event('team/member', { version: 2, teamId: TEAM, member: member() }, SessionSeq(0))
    const active = event('team/member', {
      version: 2,
      teamId: TEAM,
      member: member({ phase: 'active' }),
    }, SessionSeq(1))
    const ownedTask = event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ ownerId: CHILD, status: 'in_progress' }),
    }, SessionSeq(2))
    const working = {
      type: 'team/work',
      data: {
        version: 2,
        teamId: TEAM,
        work: { memberId: CHILD, state: 'working', summary: 'started', taskId: TeamTaskId('task-1'), files: [] },
      },
      seq: SessionSeq(3),
      time: 123,
    } as unknown as SessionEvent
    const done = {
      type: 'team/work',
      data: {
        version: 2,
        teamId: TEAM,
        work: { memberId: CHILD, state: 'done', summary: 'finished', taskId: TeamTaskId('task-1'), files: [] },
      },
      seq: SessionSeq(4),
      time: 456,
    } as unknown as SessionEvent

    const state = projectTeam(ROOT, [provisioning, active, ownedTask, working, done])
    expect(state.work).toEqual([{
      memberId: CHILD,
      state: 'done',
      summary: 'finished',
      taskId: TeamTaskId('task-1'),
      files: [],
      updatedAt: 456,
    }])
  })

  it('requires a task-bound persisted work report to reference an active task owned by the reporter', () => {
    const provisioning = event('team/member', { version: 2, teamId: TEAM, member: member() }, SessionSeq(0))
    const active = event('team/member', {
      version: 2,
      teamId: TEAM,
      member: member({ phase: 'active' }),
    }, SessionSeq(1))
    const owned = event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ ownerId: CHILD, status: 'in_progress' }),
    }, SessionSeq(2))
    const report = (taskId: ReturnType<typeof TeamTaskId>, seq: number) => ({
      type: 'team/work',
      data: {
        version: 2,
        teamId: TEAM,
        work: { memberId: CHILD, state: 'working', summary: 'started', taskId, files: [] },
      },
      seq: SessionSeq(seq),
      time: seq,
    }) as unknown as SessionEvent
    const deleted = event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ revision: 2, ownerId: CHILD, status: 'deleted' }),
    }, SessionSeq(4))

    expect(() => projectTeam(ROOT, [provisioning, active, report(TeamTaskId('missing'), 2)]))
      .toThrow('work task "missing" does not exist')
    expect(() => projectTeam(ROOT, [
      provisioning,
      active,
      event('team/task', {
        version: 2,
        teamId: TEAM,
        task: task({ ownerId: ROOT, status: 'in_progress' }),
      }, SessionSeq(2)),
      report(TeamTaskId('task-1'), 3),
    ])).toThrow('work task "task-1" is not owned by reporter')
    expect(() => projectTeam(ROOT, [provisioning, active, owned, deleted, report(TeamTaskId('task-1'), 5)]))
      .toThrow('work task "task-1" is deleted')

    const historical = projectTeam(ROOT, [
      provisioning,
      active,
      owned,
      report(TeamTaskId('task-1'), 3),
      deleted,
    ])
    expect(historical.work).toMatchObject([{ memberId: CHILD, taskId: TeamTaskId('task-1') }])
    expect(historical.tasks[0]?.status).toBe('deleted')
  })

  it('rejects non-normalized persisted work snapshots', () => {
    const malformed = {
      type: 'team/work',
      data: {
        version: 2,
        teamId: TEAM,
        work: {
          memberId: ROOT,
          state: 'review_required',
          summary: 'review',
          files: ['/absolute.ts'],
        },
      },
      seq: SessionSeq(0),
      time: 123,
    } as unknown as SessionEvent

    expect(() => projectTeam(ROOT, [malformed])).toThrow('persisted Agent Teams team/work payload is invalid')
  })

  it('projects current-team records independently from inherited records', () => {
    const records: SessionEvent[] = [
      event('team/member', { version: 2, teamId: TeamId('ancestor'), member: member() }, SessionSeq(0)),
      event('team/member', { version: 2, teamId: TEAM, member: member() }, SessionSeq(1)),
      event('team/member', {
        version: 2,
        teamId: TEAM,
        member: member({ phase: 'active' }),
      }, SessionSeq(2)),
      event('team/task', { version: 2, teamId: TEAM, task: task({ id: TeamTaskId('task-7') }) }, SessionSeq(3)),
      event('team/message/queued', { version: 2, teamId: TEAM, message: message() }, SessionSeq(4)),
    ]
    const projected = project(ROOT, records)
    const state = teamState(projected)

    expect(state).toMatchObject({ id: TEAM })
    expect(state.members).toHaveLength(1)
    expect(state.tasks).toHaveLength(1)
    expect(pending(state)).toHaveLength(1)
    expect(state.nextTaskNumber).toBe(8)
    expect(state.members.find(member => member.id === CHILD)?.name).toBe('worker-a')
    expect(teamProjectionDefinition.stateSchema.parse(JSON.parse(JSON.stringify(projected))))
      .toEqual(projected)
  })

  it('enforces teammate identity and lifecycle', () => {
    const base = event('team/member', { version: 2, teamId: TEAM, member: member() }, SessionSeq(0))
    expect(() => projectTeam(ROOT, [event('team/member', {
      version: 2,
      teamId: TEAM,
      member: member({ phase: 'active' }),
    }, SessionSeq(0))])).toThrow(/must begin provisioning/)
    expect(() => projectTeam(ROOT, [base, event('team/member', {
      version: 2,
      teamId: TEAM,
      member: member({ name: 'renamed', phase: 'active' }),
    }, SessionSeq(1))])).toThrow(/immutable identity/)
    expect(() => projectTeam(ROOT, [base, event('team/member', {
      version: 2,
      teamId: TEAM,
      member: member({ phase: 'active' }),
    }, SessionSeq(1)), event('team/member', {
      version: 2,
      teamId: TEAM,
      member: member({ phase: 'failed' }),
    }, SessionSeq(2))])).toThrow(/invalid active -> failed/)

    const duplicateName = member({ id: SessionId('child-b') })
    expect(() => projectTeam(ROOT, [base, event('team/member', {
      version: 2,
      teamId: TEAM,
      member: duplicateName,
    }, SessionSeq(1))])).toThrow(/name .* reused/)
  })

  it('enforces task revision continuity', () => {
    const first = event('team/task', { version: 2, teamId: TEAM, task: task() }, SessionSeq(0))
    expect(() => projectTeam(ROOT, [event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ revision: 2 }),
    }, SessionSeq(0))])).toThrow(/begin at revision 1/)
    expect(() => projectTeam(ROOT, [first, event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ revision: 3 }),
    }, SessionSeq(1))])).toThrow(/revision is not contiguous/)
  })

  it('rejects every invalid persisted task dependency relation', () => {
    const first = event('team/task', { version: 2, teamId: TEAM, task: task() }, SessionSeq(0))
    const second = event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({
        id: TeamTaskId('task-2'),
        blockedBy: [TeamTaskId('task-1')],
      }),
    }, SessionSeq(1))
    const invalid: Array<{ records: SessionEvent[]; message: RegExp }> = [
      {
        records: [event('team/task', {
          version: 2,
          teamId: TEAM,
          task: task({ blockedBy: [TeamTaskId('missing')] }),
        }, SessionSeq(0))],
        message: /blocker task "missing" .* is missing or deleted/,
      },
      {
        records: [event('team/task', {
          version: 2,
          teamId: TEAM,
          task: task({ blockedBy: [TeamTaskId('task-1')] }),
        }, SessionSeq(0))],
        message: /cannot block itself/,
      },
      {
        records: [first, event('team/task', {
          ...second.data,
          task: { ...second.data.task, blockedBy: [TeamTaskId('task-1'), TeamTaskId('task-1')] },
        }, SessionSeq(1))],
        message: /repeats blocker/,
      },
      {
        records: [first, second, event('team/task', {
          version: 2,
          teamId: TEAM,
          task: task({ revision: 2, blockedBy: [TeamTaskId('task-2')] }),
        }, SessionSeq(2))],
        message: /dependency cycle/,
      },
      {
        records: [first, second, event('team/task', {
          version: 2,
          teamId: TEAM,
          task: task({ revision: 2, status: 'deleted' }),
        }, SessionSeq(2))],
        message: /blocker task "task-1" .* is missing or deleted/,
      },
    ]

    for (const { records, message: expected } of invalid) {
      expect(() => projectTeam(ROOT, records)).toThrow(expected)
    }
  })

  it('leaves numeric allocation unchanged for a branded nonstandard task id', () => {
    const state = projectTeam(ROOT, [event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ id: TeamTaskId('external-task') }),
    }, SessionSeq(0))])
    expect(state.nextTaskNumber).toBe(1)
  })

  it('rejects a persisted numeric task id outside the safe integer range', () => {
    expect(() => projectTeam(ROOT, [event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task({ id: TeamTaskId('task-9007199254740992') }),
    }, SessionSeq(0))])).toThrow(/persisted Agent Teams team\/task payload is invalid/)
  })

  it('enforces mailbox queue and acknowledgement relations', () => {
    const queued = event('team/message/queued', { version: 2, teamId: TEAM, message: message() }, SessionSeq(0))
    const delivered = event('team/message/delivered', {
      version: 2,
      teamId: TEAM,
      messageId: TeamMessageId('message-1'),
      targetId: CHILD,
    }, SessionSeq(1))
    expect(pending(projectTeam(ROOT, [queued, delivered]))).toEqual([])
    expect(() => projectTeam(ROOT, [queued, queued])).toThrow(/queued twice/)
    expect(() => projectTeam(ROOT, [delivered])).toThrow(/delivered before queueing/)
    expect(() => projectTeam(ROOT, [queued, event('team/message/delivered', {
      ...delivered.data,
      targetId: SessionId('other'),
    }, SessionSeq(1))])).toThrow(/target changed/)
    expect(() => projectTeam(ROOT, [queued, delivered, { ...delivered, seq: SessionSeq(2) }])).toThrow(/delivered twice/)
  })

  it('validates every current-version persisted payload before projecting it', () => {
    const malformed = [
      {
        ...event('team/member', { version: 2, teamId: TEAM, member: member() }, SessionSeq(0)),
        data: { version: 2, teamId: TEAM, member: { ...member(), name: 42 } },
      },
      {
        ...event('team/task', { version: 2, teamId: TEAM, task: task() }, SessionSeq(0)),
        data: { version: 2, teamId: TEAM, task: { ...task(), blockedBy: [42] } },
      },
      {
        ...event('team/message/queued', { version: 2, teamId: TEAM, message: message() }, SessionSeq(0)),
        data: {
          version: 2,
          teamId: TEAM,
          message: { ...message(), content: [{ type: 'text', text: 42 }] },
        },
      },
      {
        ...event('team/message/delivered', {
          version: 2,
          teamId: TEAM,
          messageId: TeamMessageId('message-1'),
          targetId: CHILD,
        }, SessionSeq(0)),
        data: {
          version: 2,
          teamId: TEAM,
          messageId: TeamMessageId('message-1'),
          targetId: 42,
        },
      },
      {
        ...event('team/member', { version: 2, teamId: TEAM, member: member() }, SessionSeq(0)),
        data: { version: 2, teamId: TEAM, member: member(), unexpected: true },
      },
      {
        ...event('team/task', { version: 2, teamId: TEAM, task: task() }, SessionSeq(0)),
        data: { version: 2, teamId: 42, task: task() },
      },
    ] as unknown as SessionEvent[]

    for (const candidate of malformed) {
      expect(() => projectTeam(ROOT, [candidate]))
        .toThrow(/persisted Agent Teams .* payload is invalid/)
    }
  })

  it('retains merge-extensible content blocks while rejecting malformed core variants', () => {
    const extension = { type: 'plugin/custom', payload: { value: 1 } } as never
    const state = projectTeam(ROOT, [event('team/message/queued', {
      version: 2,
      teamId: TEAM,
      message: message({ content: [extension] }),
    }, SessionSeq(0))])
    expect(pending(state)[0]?.content).toEqual([extension])
  })

  it('records unsupported event versions without applying them', () => {
    const invalid = event('team/task', {
      version: 1 as 2,
      teamId: TEAM,
      task: task(),
    }, SessionSeq(0))
    const later = event('team/task', {
      version: 2,
      teamId: TEAM,
      task: task(),
    }, SessionSeq(1))
    const state = project(ROOT, [invalid, later])
    expect(state.failure).toMatch(/unsupported Agent Teams event version 1/)
    expect(isEmptyState(state)).toBe(true)
  })

  it('isolates unsupported inherited Team records from the current Team', () => {
    const inherited = event('team/task', {
      version: 1 as 2,
      teamId: TeamId('ancestor'),
      task: task(),
    }, SessionSeq(0))
    const projected = project(ROOT, [inherited])
    expect(projected.failure).toBeUndefined()
    expect(isEmptyState(teamState(projected))).toBe(true)
  })

  it('ignores malformed current-version records inherited from another Team', () => {
    const inherited = {
      ...event('team/task', {
        version: 2,
        teamId: TeamId('ancestor'),
        task: task(),
      }, SessionSeq(0)),
      data: {
        version: 2,
        teamId: TeamId('ancestor'),
        task: { ...task(), subject: 42 },
      },
    } as unknown as SessionEvent
    expect(isEmptyState(projectTeam(ROOT, [inherited]))).toBe(true)
  })
})
