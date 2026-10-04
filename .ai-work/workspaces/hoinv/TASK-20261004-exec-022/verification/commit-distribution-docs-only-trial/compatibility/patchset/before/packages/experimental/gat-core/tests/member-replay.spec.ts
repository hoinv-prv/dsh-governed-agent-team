import { describe, expect, it } from 'vitest'
import { SESSION_FORMAT_VERSION, SessionId, SessionSeq } from '@deepseek-ai/dsh-session'
import type { SessionEvent, SessionEventMap, SessionEventType } from '@deepseek-ai/dsh-session'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { teamProjectionDefinition, validateInitialTask } from '../src/projection.ts'
import type { TeamProjectionState } from '../src/projection.ts'
import { resolveActiveMember } from '../src/roster.ts'
import { payloadSha256 } from '../src/attachments.ts'
import { TeamId, TeamTaskId } from '../src/types.ts'
import type { LegacyTeamMemberSnapshot, TeamMemberAttachmentRecord, TeamMemberSnapshot, TeamTaskSnapshot } from '../src/types.ts'

const ROOT = SessionId('member-replay-root')
const TEAM = TeamId(ROOT)
const CHILD = SessionId('member-replay-child')

function event<T extends Extract<SessionEventType, `team/${string}`>>(
  type: T,
  data: SessionEventMap[T],
  seq: number,
): SessionEvent<T> {
  return { type, data, seq: SessionSeq(seq), time: seq } as unknown as SessionEvent<T>
}

function project(events: readonly SessionEvent[]): TeamProjectionState {
  let state = teamProjectionDefinition.init({
    version: SESSION_FORMAT_VERSION,
    id: ROOT,
    createdAt: 0,
    isSeeded: false,
  })
  for (const item of events) state = teamProjectionDefinition.apply(state, item)
  return state
}

function legacyMember(overrides: Partial<LegacyTeamMemberSnapshot> = {}): LegacyTeamMemberSnapshot {
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

function record(payload: unknown, binderId = 'memory'): TeamMemberAttachmentRecord {
  return {
    binderId,
    protocolVersion: 1,
    required: true,
    payload: payload as TeamMemberAttachmentRecord['payload'],
    payloadSha256: payloadSha256(payload),
  }
}

function member(attachments: readonly TeamMemberAttachmentRecord[], phase: TeamMemberSnapshot['phase'] = 'provisioning'): TeamMemberSnapshot {
  return { ...legacyMember({ phase }), attachments } as TeamMemberSnapshot
}

function task(): TeamTaskSnapshot {
  return {
    id: TeamTaskId('task-1'),
    revision: 1,
    subject: 'Replay task',
    description: 'Check unrelated family version handling',
    status: 'pending',
    blockedBy: [],
    writeScopes: [],
  }
}

describe('member event replay with required attachments', () => {
  it('strictly replays legacy v2 members with an empty attachment list', () => {
    const provisioning = event('team/member', { version: 2, teamId: TEAM, member: legacyMember() }, 0)
    const active = event('team/member', {
      version: 2, teamId: TEAM, member: legacyMember({ phase: 'active' }),
    }, 1)
    const state = project([provisioning, active])

    expect(state.failure).toBeUndefined()
    expect(state.members).toHaveLength(1)
    expect(state.members[0]!.phase).toBe('active')
    expect(state.members[0]!.attachments).toEqual([])

    const invalidLegacy = event('team/member', {
      version: 2,
      teamId: TEAM,
      member: { ...legacyMember(), attachments: [] },
    } as unknown as SessionEventMap['team/member'], 0)
    expect(project([invalidLegacy]).failure).toContain('persisted Agent Teams team/member payload is invalid')
  })

  it('replays v3 provisioning and active snapshots with immutable detached records', () => {
    const originalPayload = { profile: { name: 'worker', tags: ['read', 'draft'] } }
    const frozenRecord = record(originalPayload)
    const provisioningMember = member([frozenRecord])
    const activeMember = { ...member([frozenRecord], 'active') }
    const state = project([
      event('team/member', { version: 3, teamId: TEAM, member: provisioningMember }, 0),
      event('team/member', { version: 3, teamId: TEAM, member: activeMember }, 1),
    ])

    expect(state.failure).toBeUndefined()
    expect(state.members[0]!.phase).toBe('active')
    expect(state.members[0]!.attachments).toEqual([frozenRecord])
    expect(Object.isFrozen(state.members[0]!.attachments)).toBe(true)
    expect(Object.isFrozen(state.members[0]!.attachments[0]!.payload)).toBe(true)

    originalPayload.profile.tags[0] = 'mutated-after-projection'
    expect(state.members[0]!.attachments[0]!.payload).toEqual({ profile: { name: 'worker', tags: ['read', 'draft'] } })
    expect(state.members[0]!.attachments[0]!.payloadSha256).toBe(payloadSha256({ profile: { name: 'worker', tags: ['read', 'draft'] } }))
  })

  it('stores validation failures for invalid digest, unknown attachment envelope, and unknown member version', () => {
    const valid = record({ key: 'value' })
    const invalidDigestMember = member([{ ...valid, payloadSha256: '0'.repeat(64) }])
    expect(project([event('team/member', { version: 3, teamId: TEAM, member: invalidDigestMember }, 0)]).failure)
      .toContain('persisted Agent Teams team/member payload is invalid')

    const unknownEnvelopeMember = member([{ ...valid, payloadRef: 'host-only-ref' } as TeamMemberAttachmentRecord])
    expect(project([event('team/member', { version: 3, teamId: TEAM, member: unknownEnvelopeMember }, 0)]).failure)
      .toContain('persisted Agent Teams team/member payload is invalid')

    const unknownVersion = event('team/member', {
      version: 4, teamId: TEAM, member: member([]),
    } as unknown as SessionEventMap['team/member'], 0)
    expect(project([unknownVersion]).failure).toContain('unsupported Agent Teams event version 4')
  })

  it('rejects attachment changes between provisioning and terminal member snapshots', () => {
    const before = member([record({ version: 1 })])
    const after = member([record({ version: 2 })], 'active')
    const state = project([
      event('team/member', { version: 3, teamId: TEAM, member: before }, 0),
      event('team/member', { version: 3, teamId: TEAM, member: after }, 1),
    ])
    expect(state.failure).toContain('changed immutable identity fields')
  })

  it('rejects attached active members from legacy active-member resolution', () => {
    const state = project([
      event('team/member', { version: 3, teamId: TEAM, member: member([record({ scope: 'member' })]) }, 0),
      event('team/member', { version: 3, teamId: TEAM, member: member([record({ scope: 'member' })], 'active') }, 1),
    ])
    expect(state.failure).toBeUndefined()
    expect(() => resolveActiveMember({ id: ROOT } as Agent, state, 'worker-a'))
      .toThrow(expect.objectContaining({ code: 'TEAM_BINDING_UNAVAILABLE' }))
  })

  it('validates core initial-task blocks while retaining unknown plugin-tag compatibility', () => {
    expect(() => validateInitialTask([{ type: 'text', unexpected: true }])).toThrow()
    expect(validateInitialTask([{ type: 'custom-plugin-block', payload: { value: 1 } }]))
      .toEqual([{ type: 'custom-plugin-block', payload: { value: 1 } }])
  })

  it('rejects unsupported future task-family versions', () => {
    const invalidTask = event('team/task', {
      version: 4,
      teamId: TEAM,
      task: task(),
    } as unknown as SessionEventMap['team/task'], 0)
    expect(project([invalidTask]).failure).toContain('unsupported Agent Teams event version 4')
  })
})
