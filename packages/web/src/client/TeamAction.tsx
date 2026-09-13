import { useCallback, useEffect, useRef, useState, type ChangeEvent } from 'react'
import type { SessionId } from '@deepseek-ai/dsh-session/types'
import type {
  TeamMemberView as TeamRosterMember,
  TeamPlanApprovalResult,
  TeamTaskAction,
  TeamTaskId,
  TeamTaskMutationResult,
  TeamTaskView as TeamTask,
  TeamView,
} from '@vuhoi/gat-core/client'
import type { RemoteResult } from '@deepseek-ai/dsh-api-remotes/client'
import {
  IconCheckOutline14, IconCloseOutline16, IconEditOutline16, IconPlusOutline16,
  IconRefreshOutline14, IconTrashOutline16, IconUserOutline16, StateDot,
} from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale, PropsRuntime } from '@deepseek-ai/dsh-client-ui-slots'
import type {} from '@deepseek-ai/dsh-client-ui-conversation/client'
import { NS, type TeamKey } from './locales.ts'
import css from './TeamAction.module.css'

/** Generated Remote result consumed directly by the Team UI. */
export type TeamActionResult<T> = RemoteResult<T>

/** Generated Remote result whose business value preserves Team task rejections. */
export type TeamTaskActionResult = RemoteResult<TeamTaskMutationResult>

/** Business actions injected by the browser plugin. */
export interface TeamActionInjected {
  load: (sessionId: SessionId) => Promise<TeamActionResult<TeamView>>
  approvePlan: (sessionId: SessionId, input: {
    approvedRevision: number
  }) => Promise<TeamActionResult<TeamPlanApprovalResult>>
  createTask: (sessionId: SessionId, input: {
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

interface Draft {
  subject: string
  description: string
  blockers: string
  scopes: string
}

const EMPTY_DRAFT: Draft = { subject: '', description: '', blockers: '', scopes: '' }

function items(value: string): string[] {
  return [...new Set(value.split(',').map(item => item.trim()).filter(Boolean))]
}

function taskIds(value: string): TeamTaskId[] {
  return items(value) as TeamTaskId[]
}

/**
 * One failure line for either carrier: a Remote failure, or a Team business
 * rejection whose codes stay local to this seam and never ride the wire.
 */
function failureText(error: { readonly code: string; readonly message: string }): string {
  return `${error.message} (${error.code})`
}

function statusKey(status: TeamTask['status']): TeamKey {
  switch (status) {
    case 'pending': return 'status.pending'
    case 'in_progress': return 'status.in_progress'
    case 'completed': return 'status.completed'
    /* v8 ignore next -- Team views omit deleted task tombstones. */
    case 'deleted': return 'status.completed'
  }
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

/** Render the live Team roster and compare-and-set task board. */
export function TeamAction({
  sessionId, load, approvePlan, createTask, updateTask, openTeammate, openReviewFile, t,
  stallWarningMs = 180_000, refreshIntervalMs = 5_000,
}: TeamActionProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState<TeamView | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [approving, setApproving] = useState(false)
  const [creating, setCreating] = useState(false)
  const [createDraft, setCreateDraft] = useState<Draft>(EMPTY_DRAFT)
  const [editing, setEditing] = useState<string | null>(null)
  const [editDraft, setEditDraft] = useState<Draft>(EMPTY_DRAFT)
  const [pendingTasks, setPendingTasks] = useState<ReadonlySet<string>>(() => new Set())
  const sessionRef = useRef(sessionId)
  const refreshGeneration = useRef(0)
  const pollOwner = useRef<object | null>(null)
  sessionRef.current = sessionId

  useEffect(() => {
    refreshGeneration.current += 1
    setOpen(false)
    setLoading(false)
    setView(null)
    setError(null)
    setApproving(false)
    setCreating(false)
    setCreateDraft(EMPTY_DRAFT)
    setEditing(null)
    setEditDraft(EMPTY_DRAFT)
    setPendingTasks(new Set())
  }, [sessionId])

  const refresh = useCallback(async (): Promise<boolean> => {
    const requestedSession = sessionId
    const generation = ++refreshGeneration.current
    setLoading(true)
    const result = await load(requestedSession)
    if (sessionRef.current !== requestedSession || refreshGeneration.current !== generation) return false
    setLoading(false)
    if (result.ok) {
      setView(result.value)
      setError(null)
      return true
    } else {
      setError(failureText(result.error))
      return false
    }
  }, [load, sessionId])

  const invalidateRefresh = useCallback((): void => {
    refreshGeneration.current += 1
    setLoading(false)
  }, [])

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

  const submitApproval = async (displayedRevision: number): Promise<void> => {
    const requestedSession = sessionId
    invalidateRefresh()
    setApproving(true)
    try {
      const result = await approvePlan(requestedSession, { approvedRevision: displayedRevision })
      if (sessionRef.current !== requestedSession) return
      if (!result.ok) {
        setError(failureText(result.error))
        return
      }
      if (!result.value.ok) {
        if (result.value.error.code === 'team-plan-conflict') {
          const reloaded = await refresh()
          if (sessionRef.current !== requestedSession) return
          if (reloaded) setError(t('approvalConflict'))
        } else {
          setError(failureText(result.value.error))
        }
        return
      }
      setError(null)
      await refresh()
    } finally {
      if (sessionRef.current === requestedSession) setApproving(false)
    }
  }

  const settleTask = useCallback(async (
    taskId: string,
    operation: () => Promise<TeamTaskActionResult>,
  ): Promise<TeamTask | undefined> => {
    const requestedSession = sessionId
    invalidateRefresh()
    setPendingTasks(current => new Set(current).add(taskId))
    try {
      const result = await operation()
      if (sessionRef.current !== requestedSession) return undefined
      if (!result.ok) {
        setError(failureText(result.error))
        return undefined
      }
      if (!result.value.ok) {
        if (result.value.error.code === 'team-task-conflict') {
          const reloaded = await refresh()
          if (sessionRef.current !== requestedSession) return undefined
          if (reloaded) setError(t('conflict'))
        } else {
          setError(failureText(result.value.error))
        }
        return undefined
      }
      const task = result.value.value
      setError(null)
      await refresh()
      if (sessionRef.current !== requestedSession) return undefined
      return task
    } finally {
      if (sessionRef.current === requestedSession) {
        setPendingTasks((current) => {
          const next = new Set(current)
          next.delete(taskId)
          return next
        })
      }
    }
  }, [invalidateRefresh, refresh, sessionId, t])

  const submitCreate = async (): Promise<void> => {
    const subject = createDraft.subject.trim()
    const description = createDraft.description.trim()
    /* v8 ignore next -- TaskForm disables Save while either normalized field is empty. */
    if (subject === '' || description === '') return
    const created = await settleTask('create', () => createTask(sessionId, {
      subject,
      description,
      blockedBy: taskIds(createDraft.blockers),
      writeScopes: items(createDraft.scopes),
    }))
    if (created === undefined) return
    setCreateDraft(EMPTY_DRAFT)
    setCreating(false)
  }

  const startEdit = (task: TeamTask): void => {
    setEditing(task.id)
    setEditDraft({
      subject: task.subject,
      description: task.description,
      blockers: task.blockedBy.join(', '),
      scopes: task.writeScopes.join(', '),
    })
  }

  const submitEdit = async (task: TeamTask): Promise<void> => {
    const requestedSession = sessionId
    const edited = await settleTask(task.id, () => updateTask(requestedSession, {
      taskId: task.id,
      expectedRevision: task.revision,
      action: 'edit',
      subject: editDraft.subject.trim(),
      description: editDraft.description.trim(),
      writeScopes: items(editDraft.scopes),
    }))
    if (edited === undefined) return
    const blockedBy = taskIds(editDraft.blockers)
    if (blockedBy.length === edited.blockedBy.length
      && blockedBy.every((blocker, index) => blocker === edited.blockedBy[index])) {
      setEditing(null)
      return
    }
    const dependencyTask = await settleTask(task.id, () => updateTask(requestedSession, {
      taskId: task.id,
      expectedRevision: edited.revision,
      action: 'set_dependencies',
      blockedBy,
    }))
    if (dependencyTask === undefined) return
    setEditing(null)
  }

  const teammates = view?.members.filter(member => member.role === 'teammate') ?? []
  const assignable = view?.members.filter(member => member.status !== 'failed' && member.status !== 'provisioning') ?? []

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
          {view !== null && (
            <>
              <section className={css.plan}>
                <h3>{t('plan')}</h3>
                <div className={css.meta}>
                  <span>{t('planPhase')}: {t(`planPhase.${view.planPhase}`)}</span>
                  <span>{t('planRevision')}: {view.planRevision}</span>
                  {view.planApproval !== undefined && (
                    <span>{t('approvedRevision')}: {view.planApproval.approvedRevision}</span>
                  )}
                </div>
                {view.planPhase === 'draft' && (
                  <button
                    type="button"
                    className={css.smallButton}
                    disabled={approving}
                    onClick={() => { void submitApproval(view.planRevision) }}
                  >
                    <IconCheckOutline14 /> {t('approvePlan')}
                  </button>
                )}
              </section>
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
              <section>
                <div className={css.sectionTitle}>
                  <h3>{t('tasks')}</h3>
                  <button type="button" className={css.smallButton} onClick={() => { setCreating(true) }}>
                    <IconPlusOutline16 size={13} /> {t('create')}
                  </button>
                </div>
                {creating && (
                  <TaskForm
                    draft={createDraft}
                    setDraft={setCreateDraft}
                    pending={pendingTasks.has('create')}
                    onSave={() => { void submitCreate() }}
                    onCancel={() => { setCreating(false) }}
                    t={t}
                  />
                )}
                {view.tasks.length === 0 && !creating && <div className={css.notice}>{t('empty')}</div>}
                <div className={css.tasks}>
                  {view.tasks.map(task => editing === task.id
                    ? (
                      <TaskForm
                        key={task.id}
                        draft={editDraft}
                        setDraft={setEditDraft}
                        pending={pendingTasks.has(task.id)}
                        onSave={() => { void submitEdit(task) }}
                        onCancel={() => { setEditing(null) }}
                        t={t}
                      />
                    )
                    : (
                      <article key={task.id} className={css.task}>
                        <div className={css.taskTitle}>
                          <strong>{task.subject}</strong>
                          <span>{t(statusKey(task.status))}</span>
                        </div>
                        <p>{task.description}</p>
                        <div className={css.meta}>
                          <span>{task.id}</span>
                          {task.status === 'pending' && <span>{task.ready ? t('ready') : t('blocked')}</span>}
                          {task.blockedBy.length > 0 && <span>{t('blockedBy')}: {task.blockedBy.join(', ')}</span>}
                          {task.writeScopes.length > 0 && <span>{t('writeScopes')}: {task.writeScopes.join(', ')}</span>}
                          {task.writeScopeWarnings.map(warning => <span key={warning} className={css.warning}>{warning}</span>)}
                        </div>
                        <div className={css.taskActions}>
                          <label>
                            {t('owner')}
                            <select
                              value={task.ownerName ?? ''}
                              disabled={pendingTasks.has(task.id) || task.status === 'completed'}
                              onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                                const owner = event.target.value
                                void settleTask(task.id, () => updateTask(sessionId, {
                                  taskId: task.id,
                                  expectedRevision: task.revision,
                                  action: 'reassign',
                                  ...owner === '' ? {} : { owner },
                                }))
                              }}
                            >
                              <option value="">{t('unowned')}</option>
                              {assignable.map(member => <option key={member.id} value={member.name}>{member.name}</option>)}
                            </select>
                          </label>
                          <button type="button" onClick={() => { startEdit(task) }} disabled={pendingTasks.has(task.id)}>
                            <IconEditOutline16 size={13} /> {t('edit')}
                          </button>
                          {task.status === 'in_progress' && (
                            <button type="button" disabled={pendingTasks.has(task.id)} onClick={() => {
                              void settleTask(task.id, () => updateTask(sessionId, {
                                taskId: task.id, expectedRevision: task.revision, action: 'complete',
                              }))
                            }}><IconCheckOutline14 /> {t('complete')}</button>
                          )}
                          {task.status === 'completed' && (
                            <button type="button" disabled={pendingTasks.has(task.id)} onClick={() => {
                              void settleTask(task.id, () => updateTask(sessionId, {
                                taskId: task.id, expectedRevision: task.revision, action: 'reopen',
                              }))
                            }}>{t('reopen')}</button>
                          )}
                          <button type="button" disabled={pendingTasks.has(task.id)} onClick={() => {
                            void settleTask(task.id, () => updateTask(sessionId, {
                              taskId: task.id, expectedRevision: task.revision, action: 'delete',
                            }))
                          }}><IconTrashOutline16 size={13} /> {t('delete')}</button>
                        </div>
                      </article>
                    ))}
                </div>
              </section>
            </>
          )}
        </div>
      )}
    </div>
  )
}

interface TaskFormProps {
  draft: Draft
  setDraft: (draft: Draft) => void
  pending: boolean
  onSave: () => void
  onCancel: () => void
  t: TeamActionProps['t']
}

function TaskForm({ draft, setDraft, pending, onSave, onCancel, t }: TaskFormProps) {
  const field = (key: keyof Draft, value: string): void => { setDraft({ ...draft, [key]: value }) }
  return (
    <div className={css.form}>
      <input value={draft.subject} placeholder={t('subject')} onChange={(event: ChangeEvent<HTMLInputElement>) => { field('subject', event.target.value) }} />
      <textarea value={draft.description} placeholder={t('description')} onChange={(event: ChangeEvent<HTMLTextAreaElement>) => { field('description', event.target.value) }} />
      <input value={draft.blockers} placeholder={t('blockers')} onChange={(event: ChangeEvent<HTMLInputElement>) => { field('blockers', event.target.value) }} />
      <input value={draft.scopes} placeholder={t('scopes')} onChange={(event: ChangeEvent<HTMLInputElement>) => { field('scopes', event.target.value) }} />
      <div className={css.formActions}>
        <button type="button" disabled={pending || draft.subject.trim() === '' || draft.description.trim() === ''} onClick={onSave}>{t('save')}</button>
        <button type="button" disabled={pending} onClick={onCancel}>{t('cancel')}</button>
      </div>
    </div>
  )
}
