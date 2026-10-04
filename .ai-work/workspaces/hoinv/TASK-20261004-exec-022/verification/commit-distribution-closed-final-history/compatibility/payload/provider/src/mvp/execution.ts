import { createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import { appendFile, readFile, realpath, unlink, writeFile } from 'node:fs/promises'
import { basename, dirname, isAbsolute, relative, resolve, sep } from 'node:path'
import { canonicalHash, canonicalJson } from '../domain/runtime.js'
import type {
  ActionResult,
  ApprovedPlan,
  ApprovedTask,
  CommandAction,
  ExactCommand,
  FileAction,
  NormalizedRuntimePlanV1,
  NormalizedRuntimeTaskV1,
  PlanApproval,
  RunResult,
  RunnerOptions,
  RunnerSnapshot,
  RuntimeActionV1,
  RuntimeApprovalV1,
  RuntimeCommandActionV1,
  RuntimeContractBindingV1,
  RuntimeExecutionPolicyV1,
  RuntimePlanV1,
  RuntimeRunResultV1,
  RuntimeRunnerOptionsV1,
  RuntimeTaskAttemptV1,
  RuntimeTaskRecordV1,
  RuntimeAttemptIdentityV1,
  TaskAction,
  TaskAttempt,
  TaskRecord,
  TaskState,
  ValidatedPlan,
  ValidatedRuntimeExecutionV1,
} from './types.js'
import { RUNTIME_APPROVAL_FORMAT, RUNTIME_PLAN_FORMAT, TASK_STATES } from './types.js'

export type RuntimeContractErrorCode = 'PLAN_INVALID' | 'APPROVAL_INVALID' | 'PLAN_APPROVAL_MISMATCH' | 'EXECUTION_POLICY_INVALID'

export class RuntimeContractError extends TypeError {
  readonly code: RuntimeContractErrorCode

  constructor(code: RuntimeContractErrorCode, detail: string) {
    super(`${code}: ${detail}`)
    this.name = 'RuntimeContractError'
    this.code = code
  }
}

type ContractObject = Record<string, unknown>

const CONTRACT_HASH = /^[a-f0-9]{64}$/u
const SHELL_EXECUTABLES = new Set(['sh', 'bash', 'zsh', 'fish', 'dash', 'ksh', 'csh', 'cmd', 'cmd.exe', 'powershell', 'powershell.exe', 'pwsh', 'pwsh.exe'])

function contractFail(code: RuntimeContractErrorCode, detail: string): never {
  throw new RuntimeContractError(code, detail)
}

function contractObject(value: unknown, code: RuntimeContractErrorCode, detail: string): ContractObject {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) contractFail(code, detail)
  const prototype = Object.getPrototypeOf(value)
  if ((prototype !== Object.prototype && prototype !== null) || Object.getOwnPropertySymbols(value).length !== 0) contractFail(code, detail)
  return value as ContractObject
}

function contractKeys(value: ContractObject, required: readonly string[], optional: readonly string[], code: RuntimeContractErrorCode, detail: string): void {
  const allowed = new Set([...required, ...optional])
  if (required.some((key) => !Object.hasOwn(value, key)) || Object.getOwnPropertyNames(value).some((key) => !allowed.has(key))) contractFail(code, detail)
}

function contractArray(value: unknown, minimum: number, maximum: number, code: RuntimeContractErrorCode, detail: string): readonly unknown[] {
  if (!Array.isArray(value) || value.length < minimum || value.length > maximum) contractFail(code, detail)
  for (let index = 0; index < value.length; index += 1) if (!Object.hasOwn(value, index)) contractFail(code, detail)
  if (Reflect.ownKeys(value).some((key) => typeof key === 'symbol' || (key !== 'length' && !/^(0|[1-9]\d*)$/u.test(key)))) contractFail(code, detail)
  return value
}

function isUtf8Text(value: unknown): value is string {
  if (typeof value !== 'string') return false
  for (let index = 0; index < value.length; index += 1) {
    const unit = value.charCodeAt(index)
    if (unit >= 0xd800 && unit <= 0xdbff) {
      const next = value.charCodeAt(index + 1)
      if (!(next >= 0xdc00 && next <= 0xdfff)) return false
      index += 1
    } else if (unit >= 0xdc00 && unit <= 0xdfff) return false
  }
  return true
}

function contractUtf8(value: unknown, code: RuntimeContractErrorCode, detail: string): string {
  if (!isUtf8Text(value)) contractFail(code, detail)
  return value
}

function contractNonEmpty(value: unknown, code: RuntimeContractErrorCode, detail: string, maximum?: number): string {
  const text = contractUtf8(value, code, detail)
  if (text.length === 0 || text.trim() !== text || text.includes('\u0000') || (maximum !== undefined && text.length > maximum)) contractFail(code, detail)
  return text
}

function contractSafeInteger(value: unknown, minimum: number, maximum: number, code: RuntimeContractErrorCode, detail: string): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || Object.is(value, -0) || value < minimum || value > maximum) contractFail(code, detail)
  return value
}

function contractWorkspacePath(value: unknown, code: RuntimeContractErrorCode, detail: string): string {
  const path = contractNonEmpty(value, code, detail)
  if (path.startsWith('/') || path.includes('\\')) contractFail(code, detail)
  const segments = path.split('/')
  if (segments.some((segment) => segment.length === 0 || segment === '.' || segment === '..')) contractFail(code, detail)
  return path
}

function freezeRuntimeCommand(value: ContractObject, code: RuntimeContractErrorCode): RuntimeCommandActionV1 {
  contractKeys(value, ['kind', 'argv', 'cwd', 'timeoutMs', 'expectedExitCode'], [], code, 'command action must be closed')
  if (value.kind !== 'command') contractFail(code, 'command kind is invalid')
  const argvInput = contractArray(value.argv, 1, 64, code, 'command argv cardinality is invalid')
  const argv = argvInput.map((argument) => contractNonEmpty(argument, code, 'command argv entry is invalid'))
  return Object.freeze({
    kind: 'command',
    argv: Object.freeze(argv),
    cwd: contractWorkspacePath(value.cwd, code, 'command cwd is invalid'),
    timeoutMs: contractSafeInteger(value.timeoutMs, 1, Number.MAX_SAFE_INTEGER, code, 'command timeout is invalid'),
    expectedExitCode: contractSafeInteger(value.expectedExitCode, 0, 255, code, 'command expected exit is invalid'),
  })
}

function freezeRuntimeAction(value: unknown, code: RuntimeContractErrorCode): RuntimeActionV1 {
  const action = contractObject(value, code, 'action must be an object')
  if (action.kind === 'command') return freezeRuntimeCommand(action, code)
  if (action.kind !== 'file') contractFail(code, 'action kind is invalid')
  if (action.operation === 'write' || action.operation === 'append') {
    contractKeys(action, ['kind', 'operation', 'path', 'content'], [], code, 'file action must be closed')
    return Object.freeze({ kind: 'file', operation: action.operation, path: contractWorkspacePath(action.path, code, 'file path is invalid'), content: contractUtf8(action.content, code, 'file content is invalid') })
  }
  if (action.operation === 'read' || action.operation === 'delete') {
    contractKeys(action, ['kind', 'operation', 'path'], [], code, 'file action must be closed')
    return Object.freeze({ kind: 'file', operation: action.operation, path: contractWorkspacePath(action.path, code, 'file path is invalid') })
  }
  contractFail(code, 'file operation is invalid')
}

/** Normalize exactly once according to baseline v5 §3.2. */
export function normalizeRuntimePlan(input: unknown): NormalizedRuntimePlanV1 {
  const plan = contractObject(input, 'PLAN_INVALID', 'plan must be an object')
  contractKeys(plan, ['format', 'missionId', 'revision', 'maxParallel', 'tasks'], [], 'PLAN_INVALID', 'plan must be closed')
  if (plan.format !== RUNTIME_PLAN_FORMAT) contractFail('PLAN_INVALID', 'unsupported runtime plan format')
  const missionId = contractNonEmpty(plan.missionId, 'PLAN_INVALID', 'missionId is invalid')
  const revision = contractSafeInteger(plan.revision, 1, Number.MAX_SAFE_INTEGER, 'PLAN_INVALID', 'revision is invalid')
  if (plan.maxParallel !== 1) contractFail('PLAN_INVALID', 'maxParallel must equal one')
  const tasksInput = contractArray(plan.tasks, 1, 20, 'PLAN_INVALID', 'task cardinality is invalid')
  const tasks = tasksInput.map((entry): NormalizedRuntimeTaskV1 => {
    const task = contractObject(entry, 'PLAN_INVALID', 'task must be an object')
    contractKeys(task, ['id', 'title', 'dependencies', 'action'], ['maxAttempts', 'retryable'], 'PLAN_INVALID', 'task must be closed')
    const id = contractNonEmpty(task.id, 'PLAN_INVALID', 'task id is invalid', 128)
    const title = contractNonEmpty(task.title, 'PLAN_INVALID', 'task title is invalid')
    const dependenciesInput = contractArray(task.dependencies, 0, 19, 'PLAN_INVALID', 'dependency cardinality is invalid')
    const dependencies = dependenciesInput.map((dependency) => contractNonEmpty(dependency, 'PLAN_INVALID', 'dependency id is invalid', 128))
    const hasMaxAttempts = Object.hasOwn(task, 'maxAttempts')
    const hasRetryable = Object.hasOwn(task, 'retryable')
    const maxAttempts = hasMaxAttempts ? contractSafeInteger(task.maxAttempts, 1, 2, 'PLAN_INVALID', 'maxAttempts is invalid') as 1 | 2 : 1
    if (hasRetryable && typeof task.retryable !== 'boolean') contractFail('PLAN_INVALID', 'retryable is invalid')
    const retryable = hasRetryable ? task.retryable as boolean : maxAttempts === 2
    if (maxAttempts === 1 && retryable) contractFail('PLAN_INVALID', 'retryable requires a second attempt')
    return Object.freeze({ id, title, dependencies: Object.freeze(dependencies), action: freezeRuntimeAction(task.action, 'PLAN_INVALID'), maxAttempts, retryable })
  })
  const ids = new Set(tasks.map((task) => task.id))
  if (ids.size !== tasks.length) contractFail('PLAN_INVALID', 'task ids must be unique')
  const planIndex = new Map(tasks.map((task, index) => [task.id, index]))
  const orderedTasks = tasks.map((task): NormalizedRuntimeTaskV1 => {
    if (new Set(task.dependencies).size !== task.dependencies.length || task.dependencies.includes(task.id) || task.dependencies.some((dependency) => !ids.has(dependency))) contractFail('PLAN_INVALID', 'dependencies must be unique existing non-self task ids')
    return Object.freeze({ ...task, dependencies: Object.freeze([...task.dependencies].sort((left, right) => planIndex.get(left)! - planIndex.get(right)!)) })
  })
  const visiting = new Set<string>()
  const visited = new Set<string>()
  const byId = new Map(orderedTasks.map((task) => [task.id, task]))
  const visit = (taskId: string): void => {
    if (visiting.has(taskId)) contractFail('PLAN_INVALID', 'dependency graph is cyclic')
    if (visited.has(taskId)) return
    visiting.add(taskId)
    for (const dependency of byId.get(taskId)!.dependencies) visit(dependency)
    visiting.delete(taskId)
    visited.add(taskId)
  }
  for (const task of orderedTasks) visit(task.id)
  return Object.freeze({ format: RUNTIME_PLAN_FORMAT, missionId, revision, maxParallel: 1, tasks: Object.freeze(orderedTasks) })
}

export function canonicalRuntimePlanJson(input: unknown): string {
  return canonicalJson(normalizeRuntimePlan(input))
}

export function runtimePlanSha256(input: unknown): string {
  return canonicalHash(normalizeRuntimePlan(input))
}

function parseRuntimeApproval(input: unknown): RuntimeApprovalV1 {
  const approval = contractObject(input, 'APPROVAL_INVALID', 'approval must be an object')
  contractKeys(approval, ['format', 'missionId', 'revision', 'planSha256', 'decision', 'approver', 'approvedAt'], [], 'APPROVAL_INVALID', 'approval must be closed')
  if (approval.format !== RUNTIME_APPROVAL_FORMAT || approval.decision !== 'APPROVED') contractFail('APPROVAL_INVALID', 'approval literals are invalid')
  const planSha256 = contractNonEmpty(approval.planSha256, 'APPROVAL_INVALID', 'plan hash is invalid')
  if (!CONTRACT_HASH.test(planSha256)) contractFail('APPROVAL_INVALID', 'plan hash is invalid')
  return Object.freeze({
    format: RUNTIME_APPROVAL_FORMAT,
    missionId: contractNonEmpty(approval.missionId, 'APPROVAL_INVALID', 'approval missionId is invalid'),
    revision: contractSafeInteger(approval.revision, 1, Number.MAX_SAFE_INTEGER, 'APPROVAL_INVALID', 'approval revision is invalid'),
    planSha256,
    decision: 'APPROVED',
    approver: contractNonEmpty(approval.approver, 'APPROVAL_INVALID', 'approver is invalid'),
    approvedAt: contractSafeInteger(approval.approvedAt, 0, Number.MAX_SAFE_INTEGER, 'APPROVAL_INVALID', 'approvedAt is invalid'),
  })
}

export function validateRuntimeApproval(input: unknown, planInput: unknown): RuntimeApprovalV1 {
  const normalizedPlan = normalizeRuntimePlan(planInput)
  const expectedPlanSha256 = canonicalHash(normalizedPlan)
  const approval = parseRuntimeApproval(input)
  if (approval.missionId !== normalizedPlan.missionId || approval.revision !== normalizedPlan.revision || approval.planSha256 !== expectedPlanSha256) contractFail('PLAN_APPROVAL_MISMATCH', 'approval does not bind the normalized runtime plan')
  return approval
}

export function canonicalRuntimeApprovalJson(input: unknown): string {
  return canonicalJson(parseRuntimeApproval(input))
}

/** Hashes only an approval proven to bind the supplied normalized plan. */
export function runtimeApprovalSha256(input: unknown, planInput: unknown): string {
  return canonicalHash(validateRuntimeApproval(input, planInput))
}

export function bindRuntimePlanApproval(planInput: unknown, approvalInput: unknown): RuntimeContractBindingV1 {
  const plan = normalizeRuntimePlan(planInput)
  const planSha256 = canonicalHash(plan)
  const approval = validateRuntimeApproval(approvalInput, plan)
  return Object.freeze({ plan, planSha256, approval, approvalSha256: canonicalHash(approval) })
}

function isShellExecutable(executableInput: string): boolean {
  const executable = basename(executableInput.replaceAll('\\', '/')).toLowerCase()
  return SHELL_EXECUTABLES.has(executable)
}

function isShellCommand(command: RuntimeCommandActionV1): boolean {
  return isShellExecutable(command.argv[0]!)
}

function sameRuntimeCommand(left: RuntimeCommandActionV1, right: RuntimeCommandActionV1): boolean {
  return left.cwd === right.cwd && left.timeoutMs === right.timeoutMs && left.expectedExitCode === right.expectedExitCode && left.argv.length === right.argv.length && left.argv.every((argument, index) => argument === right.argv[index])
}

function validateRuntimeExecutionPolicy(input: unknown, plan: NormalizedRuntimePlanV1): RuntimeExecutionPolicyV1 {
  const policy = contractObject(input, 'EXECUTION_POLICY_INVALID', 'execution policy must be an object')
  contractKeys(policy, ['workspaceRoot', 'allowedCommands'], [], 'EXECUTION_POLICY_INVALID', 'execution policy must be closed')
  const workspaceRoot = contractNonEmpty(policy.workspaceRoot, 'EXECUTION_POLICY_INVALID', 'workspace root is invalid')
  const allowedInput = contractArray(policy.allowedCommands, 0, 20, 'EXECUTION_POLICY_INVALID', 'command allowlist is invalid')
  const allowedCommands = allowedInput.map((entry) => freezeRuntimeCommand(contractObject(entry, 'EXECUTION_POLICY_INVALID', 'allowlisted command must be an object'), 'EXECUTION_POLICY_INVALID'))
  if (allowedCommands.some(isShellCommand)) contractFail('EXECUTION_POLICY_INVALID', 'shell commands are forbidden')
  const keys = new Set(allowedCommands.map((command) => canonicalJson(command)))
  if (keys.size !== allowedCommands.length) contractFail('EXECUTION_POLICY_INVALID', 'allowlisted commands must be unique')
  containedPath(workspaceRoot, '.')
  for (const task of plan.tasks) {
    if (task.action.kind !== 'command') continue
    if (isShellCommand(task.action)) contractFail('EXECUTION_POLICY_INVALID', 'shell commands are forbidden')
    if (!allowedCommands.some((allowed) => sameRuntimeCommand(task.action as RuntimeCommandActionV1, allowed))) contractFail('EXECUTION_POLICY_INVALID', 'command is not exactly allowlisted')
  }
  return Object.freeze({ workspaceRoot, allowedCommands: Object.freeze(allowedCommands) })
}

export function validateRuntimeExecution(planInput: unknown, approvalInput: unknown, policyInput: unknown): ValidatedRuntimeExecutionV1 {
  const binding = bindRuntimePlanApproval(planInput, approvalInput)
  const policy = validateRuntimeExecutionPolicy(policyInput, binding.plan)
  return Object.freeze({ ...binding, policy })
}

export function runtimeTaskAttemptIdentity(plan: NormalizedRuntimePlanV1, planSha256: string, runIdInput: unknown, taskId: string, attemptOrdinalInput: unknown): RuntimeAttemptIdentityV1 {
  if (!CONTRACT_HASH.test(planSha256) || canonicalHash(plan) !== planSha256) contractFail('PLAN_INVALID', 'plan hash is not canonical')
  const runId = contractNonEmpty(runIdInput, 'EXECUTION_POLICY_INVALID', 'runId is invalid')
  const attemptOrdinal = contractSafeInteger(attemptOrdinalInput, 1, Number.MAX_SAFE_INTEGER, 'EXECUTION_POLICY_INVALID', 'attempt ordinal is invalid')
  const task = plan.tasks.find((candidate) => candidate.id === taskId)
  if (!task || attemptOrdinal > task.maxAttempts) contractFail('EXECUTION_POLICY_INVALID', 'attempt identity is outside the plan')
  const attemptId = canonicalHash({ attemptOrdinal, planSha256, runId, taskId })
  return Object.freeze({ taskId, attemptOrdinal, attemptId, idempotencyKey: canonicalHash({ attemptId, kind: 'mvp-task-attempt', missionId: plan.missionId, revision: plan.revision }) })
}

export function selectFirstReadyRuntimeTask(records: readonly RuntimeTaskRecordV1[]): RuntimeTaskRecordV1 | undefined {
  const byId = new Map(records.map((record) => [record.task.id, record]))
  return records.find((record) => (record.state === 'pending' || record.state === 'ready') && record.attemptCount < record.task.maxAttempts && record.task.dependencies.every((dependency) => byId.get(dependency)?.state === 'completed'))
}

export async function executeRuntimeAction(actionInput: RuntimeActionV1 | unknown, executionInput: ValidatedRuntimeExecutionV1): Promise<ActionResult> {
  // Revalidate the complete authority boundary so direct callers cannot bypass closure,
  // approval binding, plan membership, no-shell, or exact-command allowlisting.
  const execution = validateRuntimeExecution(executionInput.plan, executionInput.approval, executionInput.policy)
  const action = freezeRuntimeAction(actionInput, 'PLAN_INVALID')
  if (!execution.plan.tasks.some((task) => canonicalJson(task.action) === canonicalJson(action))) contractFail('EXECUTION_POLICY_INVALID', 'action is not a member of the approved plan')
  if (action.kind === 'file') {
    try {
      if (action.operation === 'read') {
        const target = await revalidateContained(execution.policy.workspaceRoot, action.path, true)
        return { kind: 'file', ok: true, value: await readFile(target, 'utf8') }
      }
      if (action.operation === 'delete') {
        const target = await revalidateContained(execution.policy.workspaceRoot, action.path, true)
        await unlink(target)
        return { kind: 'file', ok: true }
      }
      const target = await revalidateContained(execution.policy.workspaceRoot, action.path, false)
      if (action.operation === 'append') await appendFile(target, action.content, 'utf8')
      else await writeFile(target, action.content, 'utf8')
      return { kind: 'file', ok: true }
    } catch (error) {
      return { kind: 'file', ok: false, error: error instanceof Error ? error.message : String(error) }
    }
  }
  const result = await runCommand({ argv: action.argv, cwd: action.cwd, timeoutMs: action.timeoutMs, expectedExitCode: action.expectedExitCode }, execution.policy.workspaceRoot)
  return { kind: 'command', ...result }
}

const runtimeTransitions: Readonly<Record<TaskState, readonly TaskState[]>> = {
  pending: ['ready'],
  ready: ['running'],
  running: ['completed', 'blocked', 'failed'],
  completed: [],
  blocked: [],
  failed: [],
}

export class RuntimeSequentialRunner {
  readonly execution: ValidatedRuntimeExecutionV1
  private readonly options: RuntimeRunnerOptionsV1
  private readonly records: RuntimeTaskRecordV1[]
  private active = false

  constructor(planInput: RuntimePlanV1 | unknown, approvalInput: RuntimeApprovalV1 | unknown, policyInput: RuntimeExecutionPolicyV1 | unknown, options: RuntimeRunnerOptionsV1) {
    this.execution = validateRuntimeExecution(planInput, approvalInput, policyInput)
    if (!options || typeof options.persistAttempt !== 'function') contractFail('EXECUTION_POLICY_INVALID', 'persistAttempt is required')
    const runId = contractNonEmpty(options.runId, 'EXECUTION_POLICY_INVALID', 'runId is invalid')
    if (options.now !== undefined && typeof options.now !== 'function') contractFail('EXECUTION_POLICY_INVALID', 'clock is invalid')
    if (options.onTransition !== undefined && typeof options.onTransition !== 'function') contractFail('EXECUTION_POLICY_INVALID', 'transition callback is invalid')
    this.options = Object.freeze({ runId, persistAttempt: options.persistAttempt, ...(options.now === undefined ? {} : { now: options.now }), ...(options.onTransition === undefined ? {} : { onTransition: options.onTransition }) })
    this.records = this.execution.plan.tasks.map((task) => Object.freeze({ task, state: 'pending', attemptCount: 0, attempts: Object.freeze([]) }))
  }

  snapshot(): readonly RuntimeTaskRecordV1[] {
    return Object.freeze(this.records.map((record) => Object.freeze({ ...record, attempts: Object.freeze([...record.attempts]) })))
  }

  private timestamp(): number {
    return contractSafeInteger(this.options.now?.() ?? Date.now(), 0, Number.MAX_SAFE_INTEGER, 'EXECUTION_POLICY_INVALID', 'clock returned an invalid timestamp')
  }

  private async transition(index: number, next: TaskState, result?: ActionResult): Promise<void> {
    const current = this.records[index]!
    if (!runtimeTransitions[current.state].includes(next)) contractFail('EXECUTION_POLICY_INVALID', 'illegal runtime transition')
    const changed: RuntimeTaskRecordV1 = Object.freeze({ ...current, state: next, ...(result === undefined ? {} : { result }) })
    this.records[index] = changed
    await this.options.onTransition?.(changed, current.state, next)
  }

  async run(): Promise<RuntimeRunResultV1> {
    if (this.active) contractFail('EXECUTION_POLICY_INVALID', 'parallel runtime invocation is forbidden')
    this.active = true
    try {
      for (;;) {
        const ready = selectFirstReadyRuntimeTask(this.records)
        if (!ready) {
          const tasks = this.snapshot()
          if (tasks.every((record) => record.state === 'completed')) return Object.freeze({ ok: true, state: 'completed', tasks })
          return Object.freeze({ ok: false, state: tasks.some((record) => record.state === 'failed') ? 'failed' : 'blocked', tasks, blocker: tasks.some((record) => record.state === 'failed') ? 'TASK_FAILURE' : 'NO_READY_TASK' })
        }
        const index = this.records.indexOf(ready)
        if (ready.state === 'pending') await this.transition(index, 'ready')
        const selected = this.records[index]!
        const attemptOrdinal = selected.attemptCount + 1
        const identity = runtimeTaskAttemptIdentity(this.execution.plan, this.execution.planSha256, this.options.runId, selected.task.id, attemptOrdinal)
        // Neither the running notification nor the action effect is reachable until the
        // caller's store-owned durable consumption barrier settles.
        await this.options.persistAttempt(identity)
        const startedAt = this.timestamp()
        await this.transition(index, 'running')
        const running = this.records[index]!
        let result: ActionResult
        try {
          result = await executeRuntimeAction(running.task.action, this.execution)
        } catch (error) {
          result = { kind: running.task.action.kind, ok: false, error: error instanceof Error ? error.message : String(error) }
        }
        const settledAt = this.timestamp()
        if (settledAt < startedAt) contractFail('EXECUTION_POLICY_INVALID', 'clock regressed')
        const retryEligible = !result.ok && running.task.retryable && attemptOrdinal < running.task.maxAttempts
        const state: RuntimeTaskAttemptV1['state'] = result.ok ? 'completed' : retryEligible ? 'blocked' : 'failed'
        const attempt: RuntimeTaskAttemptV1 = Object.freeze({ ...identity, startedAt, settledAt, state, result })
        this.records[index] = Object.freeze({ ...running, attemptCount: attemptOrdinal, attempts: Object.freeze([...running.attempts, attempt]), result })
        await this.transition(index, state, result)
        if (!result.ok) return Object.freeze({ ok: false, state: retryEligible ? 'blocked' : 'failed', tasks: this.snapshot(), blocker: `task:${running.task.id}` })
      }
    } finally {
      this.active = false
    }
  }
}

export function createRuntimeRunner(plan: RuntimePlanV1 | unknown, approval: RuntimeApprovalV1 | unknown, policy: RuntimeExecutionPolicyV1 | unknown, options: RuntimeRunnerOptionsV1): RuntimeSequentialRunner {
  return new RuntimeSequentialRunner(plan, approval, policy, options)
}

export async function runRuntimePlan(plan: RuntimePlanV1 | unknown, approval: RuntimeApprovalV1 | unknown, policy: RuntimeExecutionPolicyV1 | unknown, options: RuntimeRunnerOptionsV1): Promise<RuntimeRunResultV1> {
  return await createRuntimeRunner(plan, approval, policy, options).run()
}

const HASH = /^[a-f0-9]{64}$/
const transitions: Readonly<Record<TaskState, readonly TaskState[]>> = {
  pending: ['ready', 'blocked'],
  ready: ['running', 'blocked'],
  running: ['completed', 'failed', 'blocked'],
  completed: [],
  blocked: [],
  failed: ['ready'],
}

type InternalActionResult = ActionResult & { readonly taskId: string; readonly attemptId: string; readonly idempotencyKey: string }

function invalid(reason: string): never {
  throw new TypeError(`MVP_${reason}`)
}

function assertString(value: unknown, reason: string): asserts value is string {
  if (typeof value !== 'string' || value.length === 0 || value.trim() !== value || value.includes('\u0000')) invalid(reason)
}

function assertPathText(value: unknown, reason: string): asserts value is string {
  assertString(value, reason)
  if (isAbsolute(value) || value.split(/[\\/]/u).includes('..')) invalid('PATH_OUTSIDE_WORKSPACE')
}

function commandEquals(a: ExactCommand, b: ExactCommand): boolean {
  return a.cwd === b.cwd && a.timeoutMs === b.timeoutMs && a.expectedExitCode === b.expectedExitCode &&
    a.argv.length === b.argv.length && a.argv.every((arg, index) => arg === b.argv[index])
}

function validateCommand(command: ExactCommand, root: string): ExactCommand {
  if (!Array.isArray(command.argv) || command.argv.length === 0 || command.argv.some((x) => typeof x !== 'string' || x.length === 0 || x.includes('\u0000'))) invalid('INVALID_COMMAND')
  assertPathText(command.cwd, 'INVALID_COMMAND_CWD')
  if (!Number.isSafeInteger(command.timeoutMs) || command.timeoutMs <= 0 || command.timeoutMs > 300_000) invalid('INVALID_COMMAND_TIMEOUT')
  if (!Number.isSafeInteger(command.expectedExitCode) || command.expectedExitCode < 0 || command.expectedExitCode > 255) invalid('INVALID_EXPECTED_EXIT')
  const program = command.argv[0]
  if (program === undefined || isShellExecutable(program)) invalid('SHELL_NOT_ALLOWED')
  // This is a lexical check during plan validation; the realpath check is repeated just before spawn.
  containedPath(root, command.cwd)
  return Object.freeze({ argv: Object.freeze([...command.argv]), cwd: command.cwd, timeoutMs: command.timeoutMs, expectedExitCode: command.expectedExitCode })
}

function normalizeCommand(action: CommandAction): ExactCommand {
  if (action.shell === true) invalid('SHELL_NOT_ALLOWED')
  const direct = action.argv !== undefined || action.cwd !== undefined || action.timeoutMs !== undefined || action.expectedExitCode !== undefined
  if (action.command !== undefined) {
    if (direct) invalid('AMBIGUOUS_COMMAND')
    return action.command
  }
  if (!direct || action.argv === undefined || action.cwd === undefined || action.timeoutMs === undefined || action.expectedExitCode === undefined) invalid('INVALID_COMMAND')
  return { argv: action.argv, cwd: action.cwd, timeoutMs: action.timeoutMs, expectedExitCode: action.expectedExitCode }
}

function normalizeFile(action: FileAction): Required<Pick<FileAction, 'path'>> & { readonly operation: 'read' | 'write' | 'append' | 'delete'; readonly content?: string } {
  assertPathText(action.path, 'INVALID_FILE_PATH')
  const operation = action.operation ?? action.op ?? 'write'
  if (action.operation !== undefined && action.op !== undefined && action.operation !== action.op) invalid('INVALID_FILE_OPERATION')
  if (!['read', 'write', 'append', 'delete'].includes(operation)) invalid('INVALID_FILE_OPERATION')
  if ((operation === 'write' || operation === 'append') && typeof action.content !== 'string') invalid('INVALID_FILE_CONTENT')
  if (operation === 'read' || operation === 'delete') return { path: action.path, operation }
  return action.content === undefined ? { path: action.path, operation } : { path: action.path, operation, content: action.content }
}

function containedPath(root: string, child: string): string {
  const base = resolve(root)
  const candidate = resolve(base, child)
  const escaped = candidate !== base && !candidate.startsWith(`${base}${sep}`)
  if (escaped || relative(base, candidate).startsWith(`..${sep}`) || relative(base, candidate) === '..') invalid('PATH_OUTSIDE_WORKSPACE')
  return candidate
}

async function revalidateContained(root: string, child: string, existing: boolean): Promise<string> {
  // Resolve the lexical path again immediately before an effect, then resolve an existing
  // target (or its parent for a new write) to prevent a symlink from escaping the workspace.
  const candidate = containedPath(root, child)
  const base = await realpath(root)
  let target: string
  if (existing) target = await realpath(candidate)
  else {
    try { target = await realpath(candidate) } catch { target = await realpath(dirname(candidate)) }
  }
  const rel = relative(base, target)
  if (rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) invalid('PATH_OUTSIDE_WORKSPACE')
  return candidate
}

function actionKind(action: TaskAction): 'file' | 'command' {
  if (!action || (action.kind !== 'file' && action.kind !== 'command')) invalid('UNKNOWN_ACTION')
  return action.kind
}

function validateAction(action: TaskAction, plan: ApprovedPlan): TaskAction {
  actionKind(action)
  if (action.kind === 'file') {
    const file = normalizeFile(action)
    containedPath(plan.workspaceRoot, file.path)
    return { kind: 'file', ...file }
  }
  const command = validateCommand(normalizeCommand(action), plan.workspaceRoot)
  if (!plan.allowedCommands.some((allowed) => commandEquals(command, allowed))) invalid('COMMAND_NOT_ALLOWLISTED')
  return { kind: 'command', command }
}

function validateApproval(plan: ApprovedPlan, approval: PlanApproval | undefined): PlanApproval {
  const bound = approval ?? plan.approval
  if (!bound || bound.decision !== 'approve' || bound.missionId !== plan.missionId || bound.revision !== plan.revision || bound.planSha256 !== plan.planSha256) invalid('APPROVAL_MISMATCH')
  return Object.freeze({ ...bound })
}

export function validateApprovedPlan(plan: ApprovedPlan, approval?: PlanApproval): ValidatedPlan {
  if (!plan || typeof plan !== 'object') invalid('INVALID_PLAN')
  assertString(plan.missionId, 'INVALID_PLAN_ID')
  if (!Number.isSafeInteger(plan.revision) || plan.revision < 1 || !HASH.test(plan.planSha256)) invalid('INVALID_PLAN_IDENTITY')
  assertString(plan.workspaceRoot, 'INVALID_WORKSPACE')
  const maxParallel = plan.maxParallel ?? plan.max_parallel
  if (plan.maxParallel !== undefined && plan.max_parallel !== undefined && plan.maxParallel !== plan.max_parallel) invalid('MAX_PARALLEL_MISMATCH')
  if (maxParallel !== 1) invalid('MAX_PARALLEL_NOT_ONE')
  if (!Array.isArray(plan.tasks) || plan.tasks.length === 0 || plan.tasks.length > 20) invalid('TASK_LIMIT')
  if (!Array.isArray(plan.allowedCommands)) invalid('INVALID_ALLOWLIST')
  const approvalBound = validateApproval(plan, approval)
  const commands = plan.allowedCommands.map((command) => validateCommand(command, plan.workspaceRoot))
  const commandKeys = new Set(commands.map((command) => JSON.stringify(command)))
  if (commandKeys.size !== commands.length) invalid('DUPLICATE_ALLOWLIST_COMMAND')
  const ids = new Set<string>()
  for (const task of plan.tasks) {
    assertString(task.id, 'INVALID_TASK_ID')
    if (ids.has(task.id)) invalid('DUPLICATE_TASK_ID')
    ids.add(task.id)
    if (!Array.isArray(task.dependencies) || new Set(task.dependencies).size !== task.dependencies.length || task.dependencies.includes(task.id)) invalid('INVALID_DEPENDENCIES')
    const attempts = task.maxAttempts ?? 1
    if (!Number.isSafeInteger(attempts) || attempts < 1 || attempts > 2) invalid('RETRY_BOUND')
    validateAction(task.action, plan)
  }
  for (const task of plan.tasks) for (const dependency of task.dependencies) if (!ids.has(dependency)) invalid('UNKNOWN_DEPENDENCY')
  const visiting = new Set<string>()
  const visited = new Set<string>()
  const byId = new Map(plan.tasks.map((task) => [task.id, task]))
  const visit = (id: string): void => {
    if (visiting.has(id)) invalid('DEPENDENCY_CYCLE')
    if (visited.has(id)) return
    visiting.add(id)
    const task = byId.get(id)
    if (!task) invalid('UNKNOWN_DEPENDENCY')
    for (const dependency of task.dependencies) visit(dependency)
    visiting.delete(id)
    visited.add(id)
  }
  for (const task of plan.tasks) visit(task.id)
  return Object.freeze({
    ...plan,
    approval: approvalBound,
    maxParallel: 1,
    tasks: Object.freeze(plan.tasks.map((task) => Object.freeze({ ...task, dependencies: Object.freeze([...task.dependencies]), maxAttempts: task.maxAttempts ?? 1 }))),
    allowedCommands: Object.freeze(commands),
  })
}

function isTaskRecordArray(snapshot: RunnerSnapshot | readonly TaskRecord[]): snapshot is readonly TaskRecord[] {
  return Array.isArray(snapshot)
}

export function selectDependencyReadyTask(snapshot: RunnerSnapshot | readonly TaskRecord[]): TaskRecord | undefined {
  const records = isTaskRecordArray(snapshot) ? snapshot : snapshot.tasks
  const byId = new Map(records.map((record) => [record.task.id, record]))
  return records.find((record) => (record.state === 'pending' || record.state === 'ready') && record.task.dependencies.every((id) => byId.get(id)?.state === 'completed'))
}

export function transitionTask(record: TaskRecord, next: TaskState): TaskRecord {
  if (!TASK_STATES.includes(record.state) || !TASK_STATES.includes(next) || !transitions[record.state].includes(next)) invalid('ILLEGAL_TASK_TRANSITION')
  return Object.freeze({ ...record, state: next })
}

function identity(plan: ValidatedPlan, taskId: string, attempt: number): { readonly attemptId: string; readonly idempotencyKey: string } {
  const attemptId = `${plan.missionId}:${plan.revision}:${taskId}:a${attempt}`
  const idempotencyKey = createHash('sha256').update(JSON.stringify({ missionId: plan.missionId, revision: plan.revision, taskId, attempt })).digest('hex')
  return { attemptId, idempotencyKey }
}

export function taskAttemptIdentity(plan: ValidatedPlan, taskId: string, attempt: number): { readonly attemptId: string; readonly idempotencyKey: string } {
  if (!Number.isSafeInteger(attempt) || attempt < 1) invalid('INVALID_ATTEMPT')
  if (!plan.tasks.some((task) => task.id === taskId)) invalid('UNKNOWN_TASK')
  return identity(plan, taskId, attempt)
}

async function runCommand(command: ExactCommand, root: string): Promise<Omit<ActionResult, 'kind'>> {
  const cwd = await revalidateContained(root, command.cwd, true)
  return await new Promise((resolveResult) => {
    let stdout = ''
    let stderr = ''
    let timedOut = false
    let settled = false
    const child = spawn(command.argv[0]!, command.argv.slice(1), { cwd, shell: false, stdio: ['ignore', 'pipe', 'pipe'] })
    child.stdout?.setEncoding('utf8').on('data', (chunk: string) => { stdout += chunk })
    child.stderr?.setEncoding('utf8').on('data', (chunk: string) => { stderr += chunk })
    const timer = setTimeout(() => { timedOut = true; child.kill('SIGTERM') }, command.timeoutMs)
    const settle = (value: Omit<ActionResult, 'kind'>): void => { if (settled) return; settled = true; clearTimeout(timer); resolveResult(value) }
    child.once('error', (error) => settle({ ok: false, stdout, stderr, error: error.message }))
    child.once('close', (exitCode, signal) => settle({ ok: !timedOut && exitCode === command.expectedExitCode, exitCode, signal, timedOut, stdout, stderr, ...(timedOut ? { error: 'TIMEOUT' } : exitCode !== command.expectedExitCode ? { error: 'UNEXPECTED_EXIT' } : {}) }))
  })
}

export async function executeAction(action: TaskAction, plan: ValidatedPlan, taskId = 'action', attempt = 1): Promise<ActionResult> {
  const checked = validateAction(action, plan)
  const ids = identity(plan, taskId, attempt)
  if (checked.kind === 'file') {
    const file = normalizeFile(checked)
    if (file.operation === 'read') {
      const target = await revalidateContained(plan.workspaceRoot, file.path, true)
      try { return { ...ids, kind: 'file', ok: true, value: await readFile(target, 'utf8') } } catch (error) { return { ...ids, kind: 'file', ok: false, error: error instanceof Error ? error.message : String(error) } }
    }
    if (file.operation === 'delete') {
      try { const target = await revalidateContained(plan.workspaceRoot, file.path, true); await unlink(target); return { ...ids, kind: 'file', ok: true } } catch (error) { return { ...ids, kind: 'file', ok: false, error: error instanceof Error ? error.message : String(error) } }
    }
    try {
      const target = await revalidateContained(plan.workspaceRoot, file.path, false)
      if (file.operation === 'append') await appendFile(target, file.content!, 'utf8')
      else await writeFile(target, file.content!, 'utf8')
      return { ...ids, kind: 'file', ok: true }
    } catch (error) { return { ...ids, kind: 'file', ok: false, error: error instanceof Error ? error.message : String(error) }
    }
  }
  const command = normalizeCommand(checked)
  const result = await runCommand(command, plan.workspaceRoot)
  return { ...ids, kind: 'command', ...result }
}

export class SequentialRunner {
  readonly plan: ValidatedPlan
  private readonly records: TaskRecord[]
  private readonly options: RunnerOptions
  private active = false

  constructor(plan: ApprovedPlan, approval?: PlanApproval, options: RunnerOptions = {}) {
    this.plan = validateApprovedPlan(plan, approval)
    this.options = options
    this.records = this.plan.tasks.map((task) => ({ task, state: 'pending', attempt: 0, attempts: [] }))
  }

  snapshot(): RunnerSnapshot {
    return Object.freeze({ missionId: this.plan.missionId, revision: this.plan.revision, planSha256: this.plan.planSha256, tasks: Object.freeze(this.records.map((record) => Object.freeze({ ...record, attempts: Object.freeze([...record.attempts]) }))) })
  }

  private async transition(index: number, next: TaskState, result?: ActionResult): Promise<void> {
    const current = this.records[index]!
    const changed = transitionTask(current, next)
    this.records[index] = Object.freeze({ ...changed, ...(result ? { result } : {}) })
    await this.options.onTransition?.(this.records[index]!, current.state, next)
  }

  private blockDependents(): Promise<void> {
    const byId = new Map(this.records.map((record) => [record.task.id, record]))
    return this.records.reduce(async (chain, record, index) => {
      await chain
      if (record.state === 'pending' && record.task.dependencies.some((id) => ['blocked', 'failed'].includes(byId.get(id)?.state ?? ''))) {
        await this.transition(index, 'blocked', { ok: false, kind: record.task.action.kind, error: 'DEPENDENCY_NOT_COMPLETED' })
      }
    }, Promise.resolve())
  }

  async run(): Promise<RunResult> {
    if (this.active) invalid('PARALLEL_RUN')
    this.active = true
    try {
      for (;;) {
        await this.blockDependents()
        const ready = selectDependencyReadyTask(this.records)
        if (!ready) {
          const states = this.records.map((record) => record.state)
          if (states.every((state) => state === 'completed')) return { ok: true, state: 'completed', tasks: this.snapshot().tasks }
          const failed = this.records.find((record) => record.state === 'failed')
          return { ok: false, state: failed ? 'failed' : 'blocked', tasks: this.snapshot().tasks, blocker: failed ? `task:${failed.task.id}` : 'NO_READY_TASK' }
        }
        const index = this.records.indexOf(ready)
        if (this.records[index]!.state === 'pending') await this.transition(index, 'ready')
        await this.transition(index, 'running')
        const task = this.records[index]!.task
        const attempt = this.records[index]!.attempts.length + 1
        const ids = identity(this.plan, task.id, attempt)
        let result: ActionResult
        try { result = await executeAction(task.action, this.plan, task.id, attempt) } catch (error) { result = { ...ids, kind: task.action.kind, ok: false, error: error instanceof Error ? error.message : String(error) } }
        const terminal: Exclude<TaskState, 'pending' | 'ready' | 'running'> = result.ok ? 'completed' : (attempt < (task.maxAttempts ?? 1) && (task.retryable ?? (task.maxAttempts === 2)) ? 'failed' : 'failed')
        const attemptRecord: TaskAttempt = Object.freeze({ taskId: task.id, attempt, ...ids, startedAt: this.options.now?.() ?? Date.now(), finishedAt: this.options.now?.() ?? Date.now(), state: terminal, result })
        this.records[index] = Object.freeze({ ...this.records[index]!, attempt, attempts: Object.freeze([...this.records[index]!.attempts, attemptRecord]), result })
        await this.transition(index, terminal, result)
        if (!result.ok && attempt < (task.maxAttempts ?? 1) && (task.retryable ?? (task.maxAttempts === 2))) await this.transition(index, 'ready')
      }
    } finally { this.active = false }
  }
}

export function createRunner(plan: ApprovedPlan, approval?: PlanApproval, options?: RunnerOptions): SequentialRunner {
  return new SequentialRunner(plan, approval, options)
}

export async function runApprovedPlan(plan: ApprovedPlan, approval?: PlanApproval, options?: RunnerOptions): Promise<RunResult> {
  return await new SequentialRunner(plan, approval, options).run()
}

/** Short aliases keep the small MVP API convenient without adding another coordinator. */
export const validatePlan = validateApprovedPlan
export const selectReadyTask = selectDependencyReadyTask
export const executeTask = executeAction
