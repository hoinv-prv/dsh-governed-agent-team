/** Initial task-plan invariants shared by mission creation and durable replay. */

import { TeamError } from './error.ts'
import { assertTaskGraphCandidate, TeamTaskGraphError } from './task-graph.ts'
import type { TeamTaskId, TeamTaskSnapshot } from './types.ts'
import { requiredText, writeScope } from './validation.ts'

const numericTaskIdPattern = /^task-(\d+)$/u
const taskFields = new Set([
  'id',
  'revision',
  'subject',
  'description',
  'status',
  'ownerId',
  'blockedBy',
  'writeScopes',
])

function invalid(message: string): never {
  throw new TeamError(`invalid initial mission task plan: ${message}`, 'TEAM_INVALID_ARGUMENT')
}

function assertTaskId(value: unknown, field: string): asserts value is TeamTaskId {
  if (typeof value !== 'string' || value.length === 0) invalid(`${field} must be a non-empty task id`)
  const match = numericTaskIdPattern.exec(value)
  if (match !== null && !Number.isSafeInteger(Number(match[1]))) {
    invalid(`${field} numeric suffix must be a safe integer`)
  }
}

/**
 * Validate a mission's immutable, creation-time task plan.
 *
 * Mission tasks are snapshots rather than mutable global Team tasks. They must
 * therefore all be new, pending, unowned revision-one tasks whose complete
 * dependency graph is valid before the mission event is committed or replayed.
 */
export function assertInitialMissionTaskPlan(tasks: readonly TeamTaskSnapshot[]): void {
  if (!Array.isArray(tasks)) invalid('tasks must be an array')

  const ids = new Set<TeamTaskId>()
  for (const [index, task] of tasks.entries()) {
    const path = `tasks[${index}]`
    if (task === null || typeof task !== 'object' || Array.isArray(task)) invalid(`${path} must be an object`)
    const record = task as unknown as Record<string, unknown>
    if (Object.keys(record).some(field => !taskFields.has(field))) invalid(`${path} contains an unknown field`)
    assertTaskId(record.id, `${path}.id`)
    if (ids.has(record.id)) invalid(`duplicate task id "${record.id}"`)
    ids.add(record.id)
    if (record.revision !== 1) invalid(`${path} must begin at revision 1`)
    if (record.status !== 'pending') invalid(`${path} must begin pending`)
    if (record.ownerId !== undefined) invalid(`${path} must begin unowned`)
    if (typeof record.subject !== 'string' || requiredText(record.subject, `${path}.subject`, 200) !== record.subject) {
      invalid(`${path}.subject must be normalized non-empty text`)
    }
    if (typeof record.description !== 'string'
      || requiredText(record.description, `${path}.description`, 16_384) !== record.description) {
      invalid(`${path}.description must be normalized non-empty text`)
    }
    if (!Array.isArray(record.blockedBy)) invalid(`${path}.blockedBy must be an array`)
    record.blockedBy.forEach((blocker, blockerIndex) => assertTaskId(blocker, `${path}.blockedBy[${blockerIndex}]`))
    if (!Array.isArray(record.writeScopes)) invalid(`${path}.writeScopes must be an array`)
    const scopes = new Set<string>()
    record.writeScopes.forEach((scope, scopeIndex) => {
      if (typeof scope !== 'string' || writeScope(scope) !== scope) invalid(`${path}.writeScopes[${scopeIndex}] must be normalized`)
      if (scopes.has(scope)) invalid(`${path} repeats write scope "${scope}"`)
      scopes.add(scope)
    })
  }

  if (tasks.length === 0) return
  try {
    assertTaskGraphCandidate(tasks, tasks[0]!)
  } catch (error: unknown) {
    if (error instanceof TeamTaskGraphError) invalid(error.message)
    throw error
  }
}
