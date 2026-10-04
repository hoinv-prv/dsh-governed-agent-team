import { useCallback, useEffect, useRef, useState } from 'react'
import type { SessionId } from '@deepseek-ai/dsh-session/types'
import type {
  ImportApprovedTeamPlanResult,
  TeamEnableResult,
  TeamMemberView as TeamRosterMember,
  TeamTaskAction,
  TeamTaskId,
  TeamTaskMutationResult,
  TeamView,
} from '@vuhoi/gat-core/client'
import type {
  TeamMissionId,
  TeamMissionMutationResult,
  TeamMissionView as TeamMission,
} from '@vuhoi/gat-core/types'
import type { RemoteResult } from '@deepseek-ai/dsh-api-remotes/client'
import {
  IconCloseOutline16, IconRefreshOutline14, IconUserOutline16, StateDot,
} from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale, PropsRuntime } from '@deepseek-ai/dsh-client-ui-slots'
import type {} from '@deepseek-ai/dsh-client-ui-conversation/client'
import { NS, type TeamKey } from './locales.ts'
import css from './TeamAction.module.css'

/** Generated Remote result consumed directly by the Team UI. */
export type TeamActionResult<T> = RemoteResult<T>

/** Generated Remote result whose business value preserves Team task rejections. */
export type TeamTaskActionResult = RemoteResult<TeamTaskMutationResult>

/** Generated Remote result whose business value preserves mission rejections. */
export type TeamMissionActionResult = RemoteResult<TeamMissionMutationResult>

/** Business actions injected by the browser plugin. */
export interface TeamActionInjected {
  load: (sessionId: SessionId) => Promise<TeamActionResult<TeamView>>
  enable: (sessionId: SessionId) => Promise<TeamActionResult<TeamEnableResult>>
  listMissions: (sessionId: SessionId) => Promise<TeamActionResult<TeamMission[]>>
  getMission: (sessionId: SessionId, missionId: TeamMissionId) => Promise<TeamActionResult<TeamMission>>
  createMission: (sessionId: SessionId, input: {
    title: string
    objective: string
  }) => Promise<TeamMissionActionResult>
  approveMission: (sessionId: SessionId, input: {
    missionId: TeamMissionId
    expectedRevision: number
  }) => Promise<TeamMissionActionResult>
  importApprovedPlan: (sessionId: SessionId, input: { missionId: TeamMissionId }) => Promise<TeamActionResult<ImportApprovedTeamPlanResult>>
  createTask: (sessionId: SessionId, input: {
    missionId: TeamMissionId
    subject: string
    description: string
    blockedBy: TeamTaskId[]
    writeScopes: string[]
  }) => Promise<TeamTaskActionResult>
  updateTask: (sessionId: SessionId, input: {
    taskId: TeamTaskId
    expectedRevision: number
    action: TeamTaskAction
    subject?: string
    description?: string
    blockedBy?: TeamTaskId[]
    writeScopes?: string[]
    owner?: string
  }) => Promise<TeamTaskActionResult>
  openTeammate: (sessionId: SessionId, member: TeamRosterMember) => Promise<void>
  openReviewFile: (sessionId: SessionId, file: string) => void
}

/** Full props of the Team conversation-header action. */
export type TeamActionProps =
  PropsRuntime<'conversation.session.header.actions'> & TeamActionInjected & PropsLocale<typeof NS> & {
    stallWarningMs?: number
    refreshIntervalMs?: number
  }

/** One failure line for a generated Remote failure. */
function failureText(error: { readonly code: string; readonly message: string }): string {
  return `${error.message} (${error.code})`
}

function memberStatusKey(status: TeamRosterMember['status']): TeamKey {
  switch (status) {
    case 'running': return 'memberStatus.running'
    case 'idle': return 'memberStatus.idle'
    case 'inactive': return 'memberStatus.inactive'
    case 'provisioning': return 'memberStatus.provisioning'
    case 'failed': return 'memberStatus.failed'
  }
}

function missionStatusKey(status: TeamMission['status']): TeamKey {
  switch (status) {
    case 'draft': return 'missionStatus.draft'
    case 'approved': return 'missionStatus.approved'
    case 'active': return 'missionStatus.active'
    case 'completed': return 'missionStatus.completed'
    case 'closed': return 'missionStatus.closed'
    case 'revoked': return 'missionStatus.revoked'
  }
}

/** Render the most recently created Team mission and the live member roster. */
export function TeamAction({
  sessionId, load, enable, listMissions, openTeammate, openReviewFile, t,
  stallWarningMs = 180_000, refreshIntervalMs = 5_000,
}: TeamActionProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [enabling, setEnabling] = useState(false)
  const [view, setView] = useState<TeamView | null>(null)
  const [currentMission, setCurrentMission] = useState<TeamMission | null>(null)
  const [missionsLoaded, setMissionsLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sessionRef = useRef(sessionId)
  const refreshGeneration = useRef(0)
  const pollOwner = useRef<object | null>(null)
  sessionRef.current = sessionId

  useEffect(() => {
    refreshGeneration.current += 1
    setOpen(false)
    setLoading(false)
    setEnabling(false)
    setView(null)
    setCurrentMission(null)
    setMissionsLoaded(false)
    setError(null)
  }, [sessionId])

  const refresh = useCallback(async (): Promise<boolean> => {
    const requestedSession = sessionId
    const generation = ++refreshGeneration.current
    setLoading(true)
    const [viewResult, missionsResult] = await Promise.all([load(requestedSession), listMissions(requestedSession)])
    if (sessionRef.current !== requestedSession || refreshGeneration.current !== generation) return false
    setLoading(false)
    if (!viewResult.ok) {
      setError(failureText(viewResult.error))
      return false
    }
    setView(viewResult.value)
    if (!missionsResult.ok) {
      setCurrentMission(null)
      setMissionsLoaded(false)
      setError(failureText(missionsResult.error))
      return false
    }
    setCurrentMission(missionsResult.value.at(-1) ?? null)
    setMissionsLoaded(true)
    setError(null)
    return true
  }, [listMissions, load, sessionId])

  useEffect(() => {
    if (!open) return
    const owner = {}
    const timer = window.setInterval(() => {
      if (pollOwner.current === owner) return
      pollOwner.current = owner
      void refresh().finally(() => {
        if (pollOwner.current === owner) pollOwner.current = null
      })
    }, refreshIntervalMs)
    return () => {
      window.clearInterval(timer)
      refreshGeneration.current += 1
      if (pollOwner.current === owner) pollOwner.current = null
    }
  }, [open, refresh, refreshIntervalMs])

  const teammates = view?.members.filter(member => member.role === 'teammate') ?? []

  return (
    <div className={css.root} data-team-action>
      <button
        type="button"
        className={css.trigger}
        aria-expanded={open}
        onClick={() => {
          const next = !open
          setOpen(next)
          if (next) void refresh()
        }}
      >
        <IconUserOutline16 size={14} />
        <span>{t('trigger')}</span>
        {teammates.length > 0 && <span className={css.count}>{teammates.length}</span>}
      </button>
      {open && (
        <div className={css.panel} role="dialog" aria-label={t('trigger')}>
          <div className={css.toolbar}>
            <strong>{t('trigger')}</strong>
            <span className={css.spacer} />
            <button type="button" className={css.iconButton} aria-label={t('refresh')} onClick={() => { void refresh() }}>
              <IconRefreshOutline14 />
            </button>
            <button type="button" className={css.iconButton} aria-label={t('close')} onClick={() => { setOpen(false) }}>
              <IconCloseOutline16 size={14} />
            </button>
          </div>
          {error !== null && <div className={css.error} role="alert">{error}</div>}
          {loading && view === null && <div className={css.notice}>{t('loading')}</div>}
          {view !== null && !view.enabled && (
            <section className={css.notice}>
              <strong>{t('teamOff')}</strong>
              <p>{t('teamOffDescription')}</p>
              <button
                type="button"
                disabled={enabling}
                onClick={() => {
                  setEnabling(true)
                  void enable(sessionId).then((result) => {
                    if (!result.ok) {
                      setError(failureText(result.error))
                      return
                    }
                    void refresh()
                  }).catch((reason: unknown) => { setError(String(reason)) }).finally(() => { setEnabling(false) })
                }}
              >
                {enabling ? t('enabling') : t('enableTeam')}
              </button>
            </section>
          )}
          {view !== null && view.enabled && (
            <>
              {missionsLoaded && (
                <section>
                  <h3>{t('missionDetail')}</h3>
                  {currentMission === null
                    ? <div className={css.notice}>{t('emptyMissions')}</div>
                    : (
                      <article className={css.missionDetail} aria-label={t('missionDetail')}>
                        <div className={css.taskTitle}>
                          <strong>{currentMission.title}</strong>
                          <span>{t(missionStatusKey(currentMission.status))}</span>
                        </div>
                        <p>{currentMission.objective}</p>
                        <div className={css.meta}>
                          <span>{t('missionRevision')}: {currentMission.revision}</span>
                          <span>{t('missionApproval')}: {currentMission.approval === undefined ? t('missionApprovalPending') : `${t('missionApprovalApproved')} (${currentMission.approval.approvedRevision})`}</span>
                        </div>
                      </article>
                    )}
                </section>
              )}
              <section>
                <h3>{t('roster')}</h3>
                <div className={css.roster}>
                  {view.members.map((member) => {
                    const durableWork = view.work.find(work => work.memberId === member.id)
                    const suspectedStall = member.status === 'running'
                      && durableWork?.state === 'working'
                      && Date.now() - durableWork.updatedAt > stallWarningMs
                    return (
                      <div key={member.id} className={css.memberRow}>
                        <button
                          type="button"
                          className={css.member}
                          disabled={member.role === 'lead' || member.status === 'failed' || member.status === 'provisioning'}
                          title={member.role === 'teammate' ? t('open') : undefined}
                          onClick={() => {
                            void openTeammate(sessionId, member).catch((reason: unknown) => { setError(String(reason)) })
                          }}
                        >
                          <StateDot state={member.status === 'running' ? 'ongoing' : member.status === 'failed' ? 'error' : 'done'} />
                          <span className={css.memberText}>
                            <span>{member.name}</span>
                            <small>{t('runtimeStatus')}: {t(memberStatusKey(member.status))}{member.model === undefined ? '' : ` · ${t('model')}: ${member.model}`}</small>
                            {member.diagnostics.map(diagnostic => <small key={diagnostic} className={css.diagnostic}>{diagnostic}</small>)}
                          </span>
                        </button>
                        <div className={css.work}>
                          {durableWork === undefined
                            ? <small>{t('noDurableWork')}</small>
                            : (
                              <>
                                <small>{t('durableWorkState')}: {t(`workState.${durableWork.state}`)}</small>
                                <small>{durableWork.summary}</small>
                                {durableWork.reason === undefined ? null : <small>{t('blockerReason')}: {durableWork.reason}</small>}
                                {durableWork.taskId === undefined ? null : <small>{t('taskId')}: {durableWork.taskId}</small>}
                                {durableWork.files.map(file => durableWork.state === 'review_required'
                                  ? (
                                    <button
                                      key={file}
                                      type="button"
                                      className={css.fileButton}
                                      onClick={() => { openReviewFile(sessionId, file) }}
                                    >
                                      {t('openReviewFile')}: {file}
                                    </button>
                                  )
                                  : <small key={file}>{file}</small>)}
                                <small>{t('updatedAt')}: {new Date(durableWork.updatedAt).toLocaleString()}</small>
                                {suspectedStall ? <small className={css.warning}>{t('suspectedStall')}</small> : null}
                              </>
                            )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </section>
            </>
          )}
        </div>
      )}
    </div>
  )
}
