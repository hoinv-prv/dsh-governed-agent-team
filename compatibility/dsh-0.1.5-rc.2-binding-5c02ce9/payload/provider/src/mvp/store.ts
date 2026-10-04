import { randomUUID } from 'node:crypto'
import { basename, dirname, join } from 'node:path'
import { open, readFile, rename, unlink, writeFile } from 'node:fs/promises'
import { canonicalHash, canonicalJson } from '../domain/runtime.js'
import { taskAttemptIdentity, validateApprovedPlan } from './execution.js'
import type {
  ActionResult,
  ApprovedPlan,
  PlanApproval,
  TaskAttempt,
  TaskRecord,
  TaskState,
  ValidatedPlan,
} from './types.js'

/** The on-disk format is deliberately a small, local replacement snapshot. */
export const EXECUTION_SNAPSHOT_VERSION = 1 as const
export const UNKNOWN_OUTCOME = 'UNKNOWN_OUTCOME' as const

export interface ExecutionSnapshot {
  readonly schemaVersion: typeof EXECUTION_SNAPSHOT_VERSION
  readonly missionId: string
  readonly revision: number
  readonly planSha256: string
  readonly runId: string
  readonly generation: number
  readonly tasks: readonly TaskRecord[]
}

export interface SnapshotIdentity {
  readonly missionId: string
  readonly revision: number
  readonly planSha256: string
  readonly runId: string
}

export interface SnapshotExpectation extends Partial<SnapshotIdentity> {
  readonly generation?: number
}

export interface ReconcileOptions {
  /** Timestamp used for the synthetic terminal attempt created by recovery. */
  readonly now?: number
}

const HASH = /^[a-f0-9]{64}$/u
const STATES = new Set<TaskState>(['pending', 'ready', 'running', 'completed', 'blocked', 'failed'])
const TERMINAL = new Set<TaskState>(['completed', 'blocked', 'failed'])
const RESULT_KEYS = new Set(['ok', 'kind', 'taskId', 'attemptId', 'idempotencyKey', 'exitCode', 'signal', 'timedOut', 'stdout', 'stderr', 'value', 'error'])
const ATTEMPT_KEYS = new Set(['taskId', 'attempt', 'attemptId', 'idempotencyKey', 'startedAt', 'finishedAt', 'state', 'result'])
const RECORD_KEYS = new Set(['task', 'state', 'attempt', 'attempts', 'result'])
const SNAPSHOT_KEYS = new Set(['schemaVersion', 'missionId', 'revision', 'planSha256', 'runId', 'generation', 'tasks'])

type JsonObject = Record<string, unknown>

function fail(reason: string): never {
  throw new TypeError(`MVP_${reason}`)
}

function object(value: unknown, reason: string): JsonObject {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) fail(reason)
  return value as JsonObject
}

function exactKeys(value: JsonObject, allowed: ReadonlySet<string>, reason = 'SNAPSHOT_EXTRA_FIELD'): void {
  for (const key of Object.keys(value)) if (!allowed.has(key)) fail(reason)
}

function text(value: unknown, reason: string): asserts value is string {
  if (typeof value !== 'string' || value.length === 0 || value.trim() !== value || value.includes('\u0000')) fail(reason)
}

function integer(value: unknown, minimum: number, reason: string): asserts value is number {
  if (!Number.isSafeInteger(value) || (value as number) < minimum) fail(reason)
}

function planFor(value: ApprovedPlan | ValidatedPlan, approval?: PlanApproval): ValidatedPlan {
  return validateApprovedPlan(value, approval)
}

function assertActionResult(result: JsonObject): asserts result is JsonObject & ActionResult {
  if (typeof result.ok !== 'boolean' || (result.kind !== 'file' && result.kind !== 'command')) fail('INVALID_RESULT')
  for (const key of ['taskId', 'attemptId', 'idempotencyKey', 'stdout', 'stderr', 'value', 'error']) {
    if (result[key] !== undefined) text(result[key], 'INVALID_RESULT_TEXT')
  }
  if (result.exitCode !== undefined && result.exitCode !== null) integer(result.exitCode, 0, 'INVALID_RESULT_EXIT')
  if (result.signal !== undefined && result.signal !== null) text(result.signal, 'INVALID_RESULT_SIGNAL')
  if (result.timedOut !== undefined && typeof result.timedOut !== 'boolean') fail('INVALID_RESULT_TIMEOUT')
}

function cloneResult(value: ActionResult): ActionResult {
  const result = object(value, 'INVALID_RESULT')
  exactKeys(result, RESULT_KEYS, 'RESULT_EXTRA_FIELD')
  assertActionResult(result)
  return Object.freeze({ ...result })
}

function expectedTask(plan: ValidatedPlan, id: string) {
  const task = plan.tasks.find((candidate) => candidate.id === id)
  if (!task) fail('UNKNOWN_TASK')
  return task
}

function validateAttempt(value: unknown, plan: ValidatedPlan, taskId: string, expectedNumber: number): TaskAttempt {
  const attempt = object(value, 'INVALID_ATTEMPT_RECORD')
  exactKeys(attempt, ATTEMPT_KEYS, 'ATTEMPT_EXTRA_FIELD')
  text(attempt.taskId, 'INVALID_ATTEMPT_TASK')
  if (attempt.taskId !== taskId) fail('ATTEMPT_TASK_MISMATCH')
  integer(attempt.attempt, 1, 'INVALID_ATTEMPT_NUMBER')
  if (attempt.attempt !== expectedNumber) fail('NON_MONOTONIC_ATTEMPTS')
  text(attempt.attemptId, 'INVALID_ATTEMPT_ID')
  text(attempt.idempotencyKey, 'INVALID_IDEMPOTENCY_KEY')
  const ids = taskAttemptIdentity(plan, taskId, expectedNumber)
  if (attempt.attemptId !== ids.attemptId || attempt.idempotencyKey !== ids.idempotencyKey) fail('ATTEMPT_IDENTITY_MISMATCH')
  integer(attempt.startedAt, 0, 'INVALID_ATTEMPT_TIME')
  if (attempt.finishedAt !== undefined) integer(attempt.finishedAt, attempt.startedAt, 'INVALID_ATTEMPT_FINISH')
  if (!TERMINAL.has(attempt.state as TaskState)) fail('INVALID_ATTEMPT_STATE')
  const result = cloneResult(attempt.result as ActionResult)
  const task = expectedTask(plan, taskId)
  if (result.kind !== task.action.kind || result.ok !== (attempt.state === 'completed')) fail('ATTEMPT_RESULT_STATE_MISMATCH')
  if (result.taskId !== undefined && result.taskId !== taskId) fail('RESULT_TASK_MISMATCH')
  if (result.attemptId !== undefined && result.attemptId !== attempt.attemptId) fail('RESULT_ATTEMPT_MISMATCH')
  if (result.idempotencyKey !== undefined && result.idempotencyKey !== attempt.idempotencyKey) fail('RESULT_IDEMPOTENCY_MISMATCH')
  return Object.freeze({ ...attempt, result }) as TaskAttempt
}

function validateRecord(value: unknown, plan: ValidatedPlan): TaskRecord {
  const record = object(value, 'INVALID_TASK_RECORD')
  exactKeys(record, RECORD_KEYS, 'TASK_RECORD_EXTRA_FIELD')
  const taskValue = object(record.task, 'INVALID_TASK')
  const taskId = taskValue.id
  text(taskId, 'INVALID_TASK_ID')
  const task = expectedTask(plan, taskId)
  if (canonicalJson(taskValue) !== canonicalJson(task)) fail('TASK_DEFINITION_MISMATCH')
  if (!STATES.has(record.state as TaskState)) fail('INVALID_TASK_STATE')
  integer(record.attempt, 0, 'INVALID_TASK_ATTEMPT')
  if (!Array.isArray(record.attempts)) fail('INVALID_ATTEMPTS')
  const attempts = record.attempts.map((attempt, index) => validateAttempt(attempt, plan, taskId, index + 1))
  const maxAttempts = task.maxAttempts ?? 1
  const retryable = task.retryable ?? (maxAttempts === 2)
  if (attempts.length > maxAttempts) fail('TASK_ATTEMPT_LIMIT_EXCEEDED')
  if (!retryable && attempts.length > 1) fail('IMPOSSIBLE_TASK_HISTORY')
  const completedIndex = attempts.findIndex((attempt) => attempt.state === 'completed')
  if (completedIndex >= 0 && (record.state !== 'completed' || completedIndex !== attempts.length - 1)) fail('IMPOSSIBLE_TASK_HISTORY')
  if (record.attempt !== attempts.length && !(record.state === 'running' && record.attempt === attempts.length + 1)) fail('TASK_ATTEMPT_COUNT_MISMATCH')
  if (record.state === 'running') {
    if (record.result !== undefined) fail('RUNNING_RESULT_PRESENT')
    if (record.attempt !== attempts.length + 1) fail('RUNNING_ATTEMPT_MISMATCH')
    if (record.attempt > maxAttempts) fail('TASK_ATTEMPT_LIMIT_EXCEEDED')
    if (attempts.length > 0 && !retryable) fail('IMPOSSIBLE_TASK_HISTORY')
  } else if (record.state === 'pending' || record.state === 'ready') {
    if (record.result !== undefined || record.attempt !== attempts.length) fail('NONTERMINAL_RESULT_PRESENT')
    if (record.state === 'pending' && attempts.length > 0) fail('IMPOSSIBLE_TASK_HISTORY')
    if (record.state === 'ready' && attempts.length >= maxAttempts) fail('TASK_ATTEMPT_LIMIT_EXHAUSTED')
    if (record.state === 'ready' && attempts.length > 0 && !retryable) fail('IMPOSSIBLE_TASK_HISTORY')
  } else {
    if (record.result === undefined) fail('TERMINAL_RESULT_MISSING')
    const result = cloneResult(record.result as ActionResult)
    if (result.kind !== task.action.kind || result.ok !== (record.state === 'completed')) fail('TERMINAL_RESULT_STATE_MISMATCH')
    // Dependency-blocked tasks have a durable result but never acquired an attempt.
    if (!(record.state === 'blocked' && attempts.length === 0)) {
      const lastAttempt = attempts[attempts.length - 1]
      if (!lastAttempt || lastAttempt.state !== record.state || canonicalJson(result) !== canonicalJson(lastAttempt.result)) fail('TERMINAL_ATTEMPT_MISMATCH')
    }
    return Object.freeze({ task, state: record.state as TaskState, attempt: record.attempt as number, attempts: Object.freeze(attempts), result })
  }
  return Object.freeze({ task, state: record.state as TaskState, attempt: record.attempt as number, attempts: Object.freeze(attempts) })
}

function validateIdentity(snapshot: Pick<ExecutionSnapshot, 'missionId' | 'revision' | 'planSha256' | 'runId' | 'generation'>, expected?: SnapshotExpectation): void {
  if (expected?.missionId !== undefined && snapshot.missionId !== expected.missionId) fail('CROSS_PLAN_SNAPSHOT')
  if (expected?.revision !== undefined && snapshot.revision !== expected.revision) fail('CROSS_PLAN_SNAPSHOT')
  if (expected?.planSha256 !== undefined && snapshot.planSha256 !== expected.planSha256) fail('CROSS_PLAN_SNAPSHOT')
  if (expected?.runId !== undefined && snapshot.runId !== expected.runId) fail('CROSS_RUN_SNAPSHOT')
  if (expected?.generation !== undefined && snapshot.generation !== expected.generation) fail('STALE_SNAPSHOT')
}

/** Strictly validates a complete snapshot against the approved plan and identity. */
export function validateExecutionSnapshot(value: unknown, planInput: ApprovedPlan | ValidatedPlan, approval?: PlanApproval, expected?: SnapshotExpectation): ExecutionSnapshot {
  const plan = planFor(planInput, approval)
  const snapshot = object(value, 'INVALID_SNAPSHOT')
  exactKeys(snapshot, SNAPSHOT_KEYS)
  if (snapshot.schemaVersion !== EXECUTION_SNAPSHOT_VERSION) fail('UNSUPPORTED_SNAPSHOT_VERSION')
  text(snapshot.missionId, 'INVALID_SNAPSHOT_MISSION')
  integer(snapshot.revision, 1, 'INVALID_SNAPSHOT_REVISION')
  if (typeof snapshot.planSha256 !== 'string' || !HASH.test(snapshot.planSha256)) fail('INVALID_SNAPSHOT_PLAN_HASH')
  text(snapshot.runId, 'INVALID_SNAPSHOT_RUN')
  integer(snapshot.generation, 0, 'INVALID_SNAPSHOT_GENERATION')
  if (snapshot.missionId !== plan.missionId || snapshot.revision !== plan.revision || snapshot.planSha256 !== plan.planSha256) fail('CROSS_PLAN_SNAPSHOT')
  validateIdentity({
    missionId: snapshot.missionId,
    revision: snapshot.revision,
    planSha256: snapshot.planSha256,
    runId: snapshot.runId,
    generation: snapshot.generation,
  }, expected)
  if (!Array.isArray(snapshot.tasks) || snapshot.tasks.length !== plan.tasks.length) fail('INCOMPLETE_SNAPSHOT_TASKS')
  const records = snapshot.tasks.map((record) => validateRecord(record, plan))
  if (new Set(records.map((record) => record.task.id)).size !== records.length || records.some((record, index) => !plan.tasks.some((task) => task.id === record.task.id))) fail('INCOMPLETE_SNAPSHOT_TASKS')
  return Object.freeze({ schemaVersion: EXECUTION_SNAPSHOT_VERSION, missionId: snapshot.missionId, revision: snapshot.revision, planSha256: snapshot.planSha256, runId: snapshot.runId, generation: snapshot.generation, tasks: Object.freeze(records) })
}

export function createExecutionSnapshot(planInput: ApprovedPlan | ValidatedPlan, runId: string, approval?: PlanApproval, generation = 0): ExecutionSnapshot {
  const plan = planFor(planInput, approval)
  text(runId, 'INVALID_SNAPSHOT_RUN')
  integer(generation, 0, 'INVALID_SNAPSHOT_GENERATION')
  return validateExecutionSnapshot({
    schemaVersion: EXECUTION_SNAPSHOT_VERSION,
    missionId: plan.missionId,
    revision: plan.revision,
    planSha256: plan.planSha256,
    runId,
    generation,
    tasks: plan.tasks.map((task) => ({ task, state: 'pending', attempt: 0, attempts: [] })),
  }, plan)
}

/** Alias kept intentionally small so callers can use the runner terminology. */
export const createSnapshot = createExecutionSnapshot
export const validateSnapshot = validateExecutionSnapshot

function withGeneration(snapshot: ExecutionSnapshot, generation: number, tasks: readonly TaskRecord[], plan: ValidatedPlan): ExecutionSnapshot {
  return validateExecutionSnapshot({ ...snapshot, generation, tasks }, plan)
}

/** Convert an interrupted running task into a durable unknown-outcome block. */
export function reconcileExecutionSnapshot(value: unknown, planInput: ApprovedPlan | ValidatedPlan, approval?: PlanApproval, options: ReconcileOptions = {}): ExecutionSnapshot {
  const plan = planFor(planInput, approval)
  const snapshot = validateExecutionSnapshot(value, plan)
  const now = options.now ?? Date.now()
  integer(now, 0, 'INVALID_RECOVERY_TIME')
  let changed = false
  const tasks = snapshot.tasks.map((record) => {
    if (record.state !== 'running') return record
    changed = true
    const attempt = record.attempt
    const ids = taskAttemptIdentity(plan, record.task.id, attempt)
    const result: ActionResult = { ok: false, kind: record.task.action.kind, taskId: record.task.id, attemptId: ids.attemptId, idempotencyKey: ids.idempotencyKey, error: UNKNOWN_OUTCOME }
    const attemptRecord: TaskAttempt = Object.freeze({ taskId: record.task.id, attempt, ...ids, startedAt: now, finishedAt: now, state: 'blocked', result })
    return Object.freeze({ ...record, state: 'blocked', attempt: record.attempts.length + 1, attempts: Object.freeze([...record.attempts, attemptRecord]), result })
  })
  return changed ? withGeneration(snapshot, snapshot.generation + 1, tasks, plan) : snapshot
}

export const reconcileSnapshot = reconcileExecutionSnapshot

/** Explicit caller acknowledgement permits only a remaining retry of unknown outcome. */
export function resumeExecutionSnapshot(value: unknown, planInput: ApprovedPlan | ValidatedPlan, approval?: PlanApproval): ExecutionSnapshot {
  const plan = planFor(planInput, approval)
  const snapshot = validateExecutionSnapshot(value, plan)
  let changed = false
  const tasks = snapshot.tasks.map((record) => {
    if (record.state !== 'blocked' || record.result?.error !== UNKNOWN_OUTCOME) return record
    const maxAttempts = record.task.maxAttempts ?? 1
    const retryable = record.task.retryable ?? (maxAttempts === 2)
    if (!retryable || record.attempts.length >= maxAttempts) return record
    changed = true
    const { result: _unknownOutcome, ...withoutResult } = record
    return Object.freeze({ ...withoutResult, state: 'ready', attempt: record.attempts.length })
  })
  return changed ? withGeneration(snapshot, snapshot.generation + 1, tasks, plan) : snapshot
}

export const resumeSnapshot = resumeExecutionSnapshot

async function atomicReplace(path: string, content: string): Promise<void> {
  const directory = dirname(path)
  const temporary = join(directory, `.${basename(path) || 'snapshot'}.${process.pid}.${randomUUID()}.tmp`)
  let handle: Awaited<ReturnType<typeof open>> | undefined
  try {
    handle = await open(temporary, 'wx', 0o600)
    await handle.writeFile(content, 'utf8')
    await handle.sync()
    await handle.close()
    handle = undefined
    await rename(temporary, path)
    try {
      const directoryHandle = await open(directory, 'r')
      try { await directoryHandle.sync() } finally { await directoryHandle.close() }
    } catch { /* directory fsync is not portable; rename remains the settlement boundary */ }
  } catch (error) {
    if (handle) await handle.close().catch(() => undefined)
    await unlink(temporary).catch(() => undefined)
    throw error
  }
}

/** Persist exactly one canonical complete snapshot using same-directory replacement. */
export async function writeExecutionSnapshot(path: string, snapshot: ExecutionSnapshot): Promise<void> {
  const content = canonicalJson(snapshot)
  await atomicReplace(path, content)
}

export const writeSnapshot = writeExecutionSnapshot
export const settleSnapshot = writeExecutionSnapshot

export interface DurableExecutionStoreOptions {
  readonly approval?: PlanApproval
  readonly now?: () => number
}

/** Local snapshot store; it is not a database, lease, append-only log, or power-loss guarantee. */
export class DurableExecutionStore {
  readonly path: string
  readonly plan: ValidatedPlan
  readonly runId: string
  private readonly now: () => number

  constructor(path: string, planInput: ApprovedPlan | ValidatedPlan, runId: string, options: DurableExecutionStoreOptions = {}) {
    this.path = path
    this.plan = planFor(planInput, options.approval)
    text(runId, 'INVALID_SNAPSHOT_RUN')
    this.runId = runId
    this.now = options.now ?? (() => Date.now())
  }

  async initialize(): Promise<ExecutionSnapshot> {
    try { return await this.load() } catch (error) {
      if (!(error instanceof Error) || !error.message.includes('ENOENT')) throw error
    }
    const initial = createExecutionSnapshot(this.plan, this.runId, undefined, 0)
    await writeExecutionSnapshot(this.path, initial)
    return initial
  }

  async load(expected?: SnapshotExpectation): Promise<ExecutionSnapshot> {
    const textValue = await readFile(this.path, 'utf8')
    let parsed: unknown
    try { parsed = JSON.parse(textValue) } catch { fail('CORRUPT_SNAPSHOT') }
    const snapshot = validateExecutionSnapshot(parsed, this.plan, undefined, { ...expected, runId: this.runId })
    if (canonicalJson(snapshot) !== textValue) fail('NON_CANONICAL_SNAPSHOT')
    return snapshot
  }

  async read(expected?: SnapshotExpectation): Promise<ExecutionSnapshot> { return await this.load(expected) }

  async commit(snapshot: ExecutionSnapshot): Promise<ExecutionSnapshot> {
    const checked = validateExecutionSnapshot(snapshot, this.plan, undefined, { runId: this.runId })
    let current: ExecutionSnapshot
    try { current = await this.load() } catch (error) {
      if (!(error instanceof Error) || !error.message.includes('ENOENT')) throw error
      if (checked.generation !== 0) fail('STALE_SNAPSHOT')
      await writeExecutionSnapshot(this.path, checked)
      return checked
    }
    if (checked.generation !== current.generation + 1) fail('STALE_SNAPSHOT')
    await writeExecutionSnapshot(this.path, checked)
    return checked
  }

  async save(snapshot: ExecutionSnapshot): Promise<ExecutionSnapshot> { return await this.commit(snapshot) }

  async recover(options: ReconcileOptions = {}): Promise<ExecutionSnapshot> {
    const current = await this.load()
    const recovered = reconcileExecutionSnapshot(current, this.plan, undefined, { now: options.now ?? this.now() })
    if (recovered.generation === current.generation) return current
    if (recovered.generation !== current.generation + 1) fail('STALE_SNAPSHOT')
    return await this.commit(recovered)
  }

  async resume(): Promise<ExecutionSnapshot> {
    const current = await this.load()
    const resumed = resumeExecutionSnapshot(current, this.plan)
    if (resumed.generation === current.generation) return current
    if (resumed.generation !== current.generation + 1) fail('STALE_SNAPSHOT')
    return await this.commit(resumed)
  }

  async acknowledgeUnknownOutcome(): Promise<ExecutionSnapshot> { return await this.resume() }

  async startTask(taskId: string, startedAt = this.now()): Promise<ExecutionSnapshot> {
    let current = await this.load()
    let index = current.tasks.findIndex((record) => record.task.id === taskId)
    if (index < 0) fail('UNKNOWN_TASK')
    let record = current.tasks[index]!
    if (record.state !== 'ready' && record.state !== 'pending') fail('TASK_NOT_READY')
    if (!record.task.dependencies.every((dependency) => current.tasks.find((candidate) => candidate.task.id === dependency)?.state === 'completed')) fail('TASK_NOT_READY')
    if (record.attempts.length >= (record.task.maxAttempts ?? 1)) fail('TASK_ATTEMPT_LIMIT_EXHAUSTED')
    integer(startedAt, 0, 'INVALID_ATTEMPT_TIME')
    if (record.state === 'pending') {
      const readyTasks = [...current.tasks]
      readyTasks[index] = Object.freeze({ ...record, state: 'ready' })
      current = await this.commit(withGeneration(current, current.generation + 1, readyTasks, this.plan))
      index = current.tasks.findIndex((candidate) => candidate.task.id === taskId)
      record = current.tasks[index!]!
    }
    const attempt = record.attempts.length + 1
    const tasks = [...current.tasks]
    tasks[index!] = Object.freeze({ ...record, state: 'running', attempt, attempts: Object.freeze([...record.attempts]) })
    return await this.commit(withGeneration(current, current.generation + 1, tasks, this.plan))
  }

  async settleTask(taskId: string, result: ActionResult, finishedAt = this.now()): Promise<ExecutionSnapshot> {
    const current = await this.load()
    const index = current.tasks.findIndex((record) => record.task.id === taskId)
    if (index < 0) fail('UNKNOWN_TASK')
    const record = current.tasks[index]!
    if (record.state !== 'running') fail('TASK_NOT_RUNNING')
    const checkedResult = cloneResult(result)
    if (checkedResult.kind !== record.task.action.kind || checkedResult.ok !== true && checkedResult.ok !== false) fail('INVALID_RESULT')
    integer(finishedAt, 0, 'INVALID_ATTEMPT_FINISH')
    const ids = taskAttemptIdentity(this.plan, taskId, record.attempt)
    const attemptRecord: TaskAttempt = Object.freeze({ taskId, attempt: record.attempt, ...ids, startedAt: finishedAt, finishedAt, state: checkedResult.ok ? 'completed' : 'failed', result: { ...checkedResult, taskId, attemptId: ids.attemptId, idempotencyKey: ids.idempotencyKey } })
    const terminal: TaskState = checkedResult.ok ? 'completed' : 'failed'
    const tasks = [...current.tasks]
    tasks[index] = Object.freeze({ ...record, state: terminal, attempts: Object.freeze([...record.attempts, attemptRecord]), result: attemptRecord.result })
    return await this.commit(withGeneration(current, current.generation + 1, tasks, this.plan))
  }

  async settle(taskId: string, result: ActionResult, finishedAt = this.now()): Promise<ExecutionSnapshot> {
    return await this.settleTask(taskId, result, finishedAt)
  }
}

export const ExecutionStore = DurableExecutionStore
export const DurableStore = DurableExecutionStore
export const DurableSnapshotStore = DurableExecutionStore

export async function openDurableStore(path: string, plan: ApprovedPlan | ValidatedPlan, runId: string, options?: DurableExecutionStoreOptions): Promise<DurableExecutionStore> {
  const store = new DurableExecutionStore(path, plan, runId, options)
  await store.initialize()
  // Opening an existing run is the restart boundary: running work is reconciled
  // before the caller can select the next ready task.
  await store.recover(options?.now ? { now: options.now() } : {})
  return store
}

export const openStore = openDurableStore

export async function readExecutionSnapshot(path: string, plan: ApprovedPlan | ValidatedPlan, runId: string, options?: DurableExecutionStoreOptions): Promise<ExecutionSnapshot> {
  return await (new DurableExecutionStore(path, plan, runId, options)).load()
}

export const readSnapshot = readExecutionSnapshot

/** Useful when callers need the canonical bytes/hash without changing the store. */
export function snapshotCanonicalJson(snapshot: ExecutionSnapshot): string { return canonicalJson(snapshot) }
export function snapshotCanonicalHash(snapshot: ExecutionSnapshot): string { return canonicalHash(snapshot) }
