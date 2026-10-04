// @vitest-environment jsdom

import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { SessionId } from '@deepseek-ai/dsh-session/types'
import type { TeamMissionId, TeamMissionView as TeamMission } from '@vuhoi/gat-core/types'
import type { TeamView } from '@vuhoi/gat-core/client'
import { makeTranslate, RemoteError } from '@deepseek-ai/dsh-client-test-runtime'
import { zh as commonZh } from '@deepseek-ai/dsh-client-locale/src/locales/zh.ts'
import {
  TeamAction, type TeamActionInjected, type TeamActionProps, type TeamActionResult,
} from '../src/client/TeamAction.tsx'
import { zh } from '../src/client/locales.ts'

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

const SESSION = 'lead' as SessionId
const MISSION_1 = 'mission-1' as TeamMissionId
const MISSION_2 = 'mission-2' as TeamMissionId

const view: TeamView = {
  enabled: true,
  planRevision: 7,
  planPhase: 'draft',
  work: [],
  members: [
    { id: SESSION, name: 'lead', role: 'lead', status: 'idle', model: 'model-a', diagnostics: [] },
    { id: 'worker-id' as SessionId, name: 'worker', role: 'teammate', status: 'inactive', model: 'model-a', diagnostics: [] },
  ],
  tasks: [],
}

const mission: TeamMission = {
  id: MISSION_1,
  revision: 3,
  title: 'Secure release',
  objective: 'Prepare the independently governed release.',
  status: 'draft',
  plan: { tasks: [] },
}

function remoteFailure(message: string): TeamActionResult<never> {
  return { ok: false, error: new RemoteError('gateway/internal', message, {}) }
}

function props(actions: TeamActionInjected, sessionId: SessionId = SESSION): TeamActionProps {
  const unused = (): never => { throw new Error('unused framework prop') }
  return {
    sessionId,
    ...actions,
    useSession: unused,
    useProjection: unused,
    useConversation: unused,
    useChat: unused,
    useTrajectory: unused,
    useInput: unused,
    inputActions: {
      setDraft: unused,
      addAttachments: unused,
      removeAttachment: unused,
      pruneAttachments: unused,
      submit: unused,
    },
    useSessions: unused,
    useWorkspaces: unused,
    usePanelInfo: unused,
    useSessionPendingInteraction: unused,
    useResource: unused,
    t: makeTranslate(zh, commonZh),
  }
}

function actions(overrides: Partial<TeamActionInjected> = {}): TeamActionInjected {
  return {
    load: () => Promise.resolve({ ok: true, value: view }),
    enable: () => Promise.resolve({ ok: true, value: { enabled: true, alreadyEnabled: false, source: 'built-in-default' as const, diagnostics: [], members: view.members } }),
    listMissions: () => Promise.resolve({ ok: true, value: [mission] }),
    getMission: () => Promise.resolve({ ok: true, value: mission }),
    createMission: () => Promise.resolve({ ok: true, value: { ok: true, value: mission } }),
    approveMission: () => Promise.resolve({ ok: true, value: { ok: true, value: mission } }),
    importApprovedPlan: () => Promise.resolve({ ok: true, value: { ok: true, value: { approvedRevision: 7 } } }),
    createTask: () => Promise.resolve({ ok: true, value: { ok: false, error: { code: 'team-rejected', message: 'unused' } } }),
    updateTask: () => Promise.resolve({ ok: true, value: { ok: false, error: { code: 'team-rejected', message: 'unused' } } }),
    openTeammate: () => Promise.resolve(),
    openReviewFile: () => {},
    ...overrides,
  }
}

function openDashboard(injected = actions()): void {
  render(<TeamAction {...props(injected)} />)
  fireEvent.click(screen.getByRole('button', { name: /Agent Team/u }))
}

describe('TeamAction', () => {
  it('shows Enable Agent Team for a session that is off', async () => {
    const enable = vi.fn(() => Promise.resolve({
      ok: true as const,
      value: { enabled: true as const, alreadyEnabled: false, source: 'built-in-default' as const, diagnostics: [], members: view.members },
    }))
    openDashboard(actions({
      load: () => Promise.resolve({ ok: true, value: { ...view, enabled: false } }),
      enable,
    }))

    expect(await screen.findByText(zh.teamOff)).toBeTruthy()
    const button = screen.getByRole('button', { name: zh.enableTeam })
    fireEvent.click(button)
    await waitFor(() => { expect(enable).toHaveBeenCalledWith(SESSION) })
  })

  it('shows the zero-mission empty state and no retired plan, task, or mission controls', async () => {
    openDashboard(actions({ listMissions: () => Promise.resolve({ ok: true, value: [] }) }))

    expect(await screen.findByText(zh.emptyMissions)).toBeTruthy()
    for (const label of [zh.plan, zh.tasks, zh.addMission, zh.create, zh.approvePlan, zh.approveMission]) {
      expect(screen.queryByRole('button', { name: label })).toBeNull()
      expect(screen.queryByText(label)).toBeNull()
    }
    expect(screen.queryByPlaceholderText(zh.missionTitle)).toBeNull()
    expect(screen.queryByPlaceholderText(zh.subject)).toBeNull()
  })

  it('keeps members visible without showing a false mission empty state when mission loading fails', async () => {
    openDashboard(actions({ listMissions: () => Promise.resolve(remoteFailure('missions unavailable')) }))

    expect((await screen.findByRole('alert')).textContent).toContain('missions unavailable')
    expect(screen.getByText('lead')).toBeTruthy()
    expect(screen.queryByText(zh.emptyMissions)).toBeNull()
    expect(screen.queryByRole('heading', { name: zh.missionDetail })).toBeNull()
  })

  it('shows the only mission as the current mission without exposing its task plan', async () => {
    openDashboard()

    expect(await screen.findByText('Secure release')).toBeTruthy()
    expect(screen.getByText(mission.objective)).toBeTruthy()
    expect(screen.getByText(`${zh.missionRevision}: 3`)).toBeTruthy()
    expect(screen.getByText(`${zh.missionApproval}: ${zh.missionApprovalPending}`)).toBeTruthy()
    expect(screen.queryByText(zh.missionTasks)).toBeNull()
    expect(screen.queryByText('Review package')).toBeNull()
  })

  it('uses the last mission returned by the dedicated API as current mission', async () => {
    const latest: TeamMission = {
      ...mission,
      id: MISSION_2,
      revision: 4,
      title: 'Migration rollout',
      objective: 'Migrate clients independently.',
      status: 'active',
    }
    const listMissions = vi.fn(() => Promise.resolve({ ok: true as const, value: [mission, latest] }))
    openDashboard(actions({ listMissions }))

    expect(await screen.findByText('Migration rollout')).toBeTruthy()
    expect(screen.getByText(latest.objective)).toBeTruthy()
    expect(screen.queryByText('Secure release')).toBeNull()
    expect(screen.getByText(`${zh.missionRevision}: 4`)).toBeTruthy()
    expect(listMissions).toHaveBeenCalledWith(SESSION)
  })

  it('renders each member model without substituting the lead model', async () => {
    const dashboard: TeamView = {
      ...view,
      members: [
        { ...view.members[0]!, model: 'gpt-5.6-terra' },
        { ...view.members[1]!, model: 'gpt-5.6-luna' },
        { id: 'unknown-model' as SessionId, name: 'unknown', role: 'teammate', status: 'inactive', diagnostics: [] },
      ],
    }
    openDashboard(actions({ load: () => Promise.resolve({ ok: true, value: dashboard }) }))

    expect(await screen.findByText(new RegExp(`${zh.model}: gpt-5\\.6-terra`, 'u'))).toBeTruthy()
    expect(screen.getByText(new RegExp(`${zh.model}: gpt-5\\.6-luna`, 'u'))).toBeTruthy()
    const unknown = screen.getByRole('button', { name: /^unknown\b/u })
    expect(unknown.textContent).not.toContain(`${zh.model}:`)
  })

  it('renders roster status, diagnostics, durable work, and suspected stalls separately', async () => {
    vi.setSystemTime(new Date('2026-09-12T12:00:00.000Z'))
    const now = Date.now()
    const dashboard: TeamView = {
      ...view,
      members: [
        { ...view.members[0]!, id: 'member-boundary' as SessionId, status: 'running' },
        { ...view.members[0]!, id: 'member-stalled' as SessionId, name: 'Researcher', status: 'running', diagnostics: ['provider warning'] },
        { ...view.members[0]!, id: 'member-idle' as SessionId, name: 'Reviewer', status: 'idle' },
      ],
      work: [
        { memberId: 'member-boundary' as SessionId, state: 'working', summary: 'Boundary work', reason: 'Waiting on input', files: ['src/boundary.ts'], updatedAt: now - 180_000 },
        { memberId: 'member-stalled' as SessionId, state: 'working', summary: 'Stalled work', files: [], updatedAt: now - 180_001 },
        { memberId: 'member-idle' as SessionId, state: 'working', summary: 'Not runtime-running', files: [], updatedAt: now - 999_999 },
      ],
    }
    openDashboard(actions({ load: () => Promise.resolve({ ok: true, value: dashboard }) }))

    expect(await screen.findByText('Boundary work')).toBeTruthy()
    expect(screen.getByText('provider warning')).toBeTruthy()
    expect(screen.getByText('src/boundary.ts')).toBeTruthy()
    expect(screen.getByText(new RegExp(`${zh.blockerReason}: Waiting on input`, 'u'))).toBeTruthy()
    expect(screen.getAllByText(zh.suspectedStall)).toHaveLength(1)
  })

  it('opens healthy teammates while disabling the lead, failed, and provisioning roster entries', async () => {
    const openTeammate = vi.fn(() => Promise.resolve())
    const dashboard: TeamView = {
      ...view,
      members: [
        view.members[0]!,
        { ...view.members[1]!, status: 'running' },
        { id: 'failed-id' as SessionId, name: 'failed-worker', role: 'teammate', status: 'failed', diagnostics: ['provider failed'] },
        { id: 'provisioning-id' as SessionId, name: 'provisioning-worker', role: 'teammate', status: 'provisioning', diagnostics: [] },
      ],
    }
    openDashboard(actions({ load: () => Promise.resolve({ ok: true, value: dashboard }), openTeammate }))

    const worker = await screen.findByRole('button', { name: /^worker\b/u })
    expect(screen.getByRole<HTMLButtonElement>('button', { name: /lead/u }).disabled).toBe(true)
    expect(screen.getByRole<HTMLButtonElement>('button', { name: /failed-worker/u }).disabled).toBe(true)
    expect(screen.getByRole<HTMLButtonElement>('button', { name: /provisioning-worker/u }).disabled).toBe(true)
    fireEvent.click(worker)
    await waitFor(() => { expect(openTeammate).toHaveBeenCalledWith(SESSION, dashboard.members[1]) })
  })

  it('offers review-file navigation only for review-required durable work', async () => {
    const reviewView: TeamView = {
      ...view,
      work: [
        { memberId: SESSION, state: 'review_required', summary: 'Review this', files: ['src/review.ts'], updatedAt: 1 },
        { memberId: view.members[1]!.id, state: 'blocked', summary: 'Not reviewable', files: ['src/blocked.ts'], updatedAt: 2 },
      ],
    }
    const openReviewFile = vi.fn()
    openDashboard(actions({ load: () => Promise.resolve({ ok: true, value: reviewView }), openReviewFile }))

    const review = await screen.findByRole('button', { name: `${zh.openReviewFile}: src/review.ts` })
    fireEvent.click(review)
    expect(openReviewFile).toHaveBeenCalledWith(SESSION, 'src/review.ts')
    expect(screen.queryByRole('button', { name: /src\/blocked\.ts/u })).toBeNull()
  })

  it('polls only while open, retains the last view on failure, and clears polling on close', async () => {
    vi.useFakeTimers()
    const load = vi.fn()
      .mockResolvedValueOnce({ ok: true, value: view })
      .mockResolvedValueOnce(remoteFailure('poll failed'))
      .mockResolvedValue({ ok: true, value: { ...view, planRevision: 8 } })
    const rendered = render(<TeamAction {...props(actions({ load }))} refreshIntervalMs={1_000} />)

    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(load).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: /Agent Team/u }))
    await act(async () => { await Promise.resolve(); await Promise.resolve() })
    expect(screen.getByText('Secure release')).toBeTruthy()
    await act(async () => { await vi.advanceTimersByTimeAsync(1_000) })
    expect(screen.getByRole('alert').textContent).toContain('poll failed')
    await act(async () => { await vi.advanceTimersByTimeAsync(1_000) })
    expect(load).toHaveBeenCalledTimes(3)

    fireEvent.click(screen.getByRole('button', { name: zh.close }))
    await act(async () => { await vi.advanceTimersByTimeAsync(5_000) })
    expect(load).toHaveBeenCalledTimes(3)
    expect(vi.getTimerCount()).toBe(0)
    rendered.unmount()
  })

  it('ignores a stale Team load after the conversation session changes', async () => {
    const nextSession = 'next-lead' as SessionId
    const firstLoad = Promise.withResolvers<TeamActionResult<TeamView>>()
    const nextView: TeamView = {
      ...view,
      members: [{ id: nextSession, name: 'next lead', role: 'lead', status: 'idle', diagnostics: [] }],
    }
    const load = vi.fn((sessionId: SessionId) => sessionId === SESSION
      ? firstLoad.promise
      : Promise.resolve({ ok: true as const, value: nextView }))
    const injected = actions({ load })
    const rendered = render(<TeamAction {...props(injected)} />)
    fireEvent.click(screen.getByRole('button', { name: /Agent Team/u }))
    await waitFor(() => { expect(load).toHaveBeenCalledWith(SESSION) })

    rendered.rerender(<TeamAction {...props(injected, nextSession)} />)
    fireEvent.click(screen.getByRole('button', { name: /Agent Team/u }))
    expect(await screen.findByText('next lead')).toBeTruthy()
    firstLoad.resolve({ ok: true, value: view })
    await Promise.resolve()

    await waitFor(() => { expect(screen.queryByText('worker')).toBeNull() })
  })
})
