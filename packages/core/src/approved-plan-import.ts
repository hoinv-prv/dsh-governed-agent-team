/** Select and parse the latest HUMAN-approved DSH plan from Lead Session history. */

import type { SessionEvent } from '@deepseek-ai/dsh-session'
import { TeamError } from './error.ts'
import { requiredText } from './validation.ts'

const MAX_PLAN_MARKDOWN_CHARACTERS = 1_000_000
const TASKS_HEADING = /^##[ \t]+Tasks[ \t]*$/u
const SECTION_ENDING_HEADING = /^#{1,2}(?:[ \t]+|$)/u
const CHECKLIST_PREFIX = /^[ \t]{0,3}[-+*][ \t]+\[/u
const VALID_CHECKLIST = /^[ \t]{0,3}[-+*][ \t]+\[[ xX]\][ \t]+.+?[ \t]*$/u
const TASK_LINE = /^[ \t]{0,3}(?:[-+*][ \t]+\[[ xX]\][ \t]+|[-+*][ \t]+|\d+[.)][ \t]+)(.+?)[ \t]*$/u

/**
 * Normalize a subject deterministically for plan-import de-duplication only.
 * @param value Value to validate or normalize.
 * @returns The NFKC-normalized, whitespace-collapsed task subject.
 */

export function normalizedTaskSubject(value: string): string {
  return value.normalize('NFKC').trim().replace(/\s+/gu, ' ').toLocaleLowerCase('en-US')
}

function invalid(message: string): never {
  throw new TeamError(`approved plan import rejected: ${message}`, 'TEAM_PLAN_IMPORT_INVALID')
}

/** Check that a result event is the one exact, successful result for a call. */
function isSuccessfulResultForCall(event: SessionEvent, callId: string): boolean {
  if (event.type !== 'tool/result') return false
  const message = event.data.message as unknown as {
    source: { kind: unknown; callId?: unknown }
    content: { type: unknown; toolCallId?: unknown; isError?: unknown }[]
  }
  const block = message.content[0]
  return message.source.kind === 'tool'
    && String(message.source.callId) === callId
    && block?.type === 'tool-result'
    && String(block.toolCallId) === callId
    && block.isError === false
}

/** Identify result events which claim to belong to a given call, including malformed ones. */
function isResultForCall(event: SessionEvent, callId: string): boolean {
  if (event.type !== 'tool/result') return false
  const message = event.data.message as unknown as {
    source: { kind: unknown; callId?: unknown }
    content: { type: unknown; toolCallId?: unknown }[]
  }
  return (message.source.kind === 'tool' && String(message.source.callId) === callId)
    || message.content.some(block => block.type === 'tool-result' && String(block.toolCallId) === callId)
}

/**
 * Parse subjects from only the explicit `## Tasks` section of an approved plan.
 * Any unrecognized non-blank line inside that section makes the import fail closed.
 * @param plan Approved plan content to parse.
 * @returns Task subject strings from the validated approved plan.
 */

export function parseApprovedPlanTasks(plan: string): string[] {
  if (plan.length > MAX_PLAN_MARKDOWN_CHARACTERS) invalid('plan exceeds import length limit')
  const lines = plan.replace(/\r\n?/gu, '\n').split('\n')
  const start = lines.findIndex(line => TASKS_HEADING.test(line))
  if (start < 0) invalid('missing explicit ## Tasks section')

  const subjects: string[] = []
  for (let index = start + 1; index < lines.length; index += 1) {
    const line = lines[index] as string
    if (SECTION_ENDING_HEADING.test(line)) break
    if (/^[ \t]*$/u.test(line)) continue
    if (CHECKLIST_PREFIX.test(line) && !VALID_CHECKLIST.test(line)) {
      invalid(`malformed checklist task line ${index + 1}`)
    }
    const matched = TASK_LINE.exec(line)
    if (matched === null) invalid(`malformed task line ${index + 1}`)
    let subject: string
    try {
      subject = requiredText((matched[1] as string).normalize('NFKC').replace(/\s+/gu, ' '), 'task subject', 200)
    } catch {
      invalid(`invalid task subject on line ${index + 1}`)
    }
    if (normalizedTaskSubject(subject) === '') invalid(`empty task line ${index + 1}`)
    subjects.push(subject)
  }
  if (subjects.length === 0) invalid('## Tasks section is empty')
  return subjects
}

/**
 * Select the latest `exit_plan_mode` call from exactly one Lead log and require
 * its one matching successful result. Failed, incomplete, and older calls are
 * never used as an import source.
 * @param events Events to append before the journal flush.
 * @returns Unique task subjects found in approved plan journal events.
 */

export function approvedPlanTaskSubjects(events: readonly SessionEvent[]): string[] {
  const callIndex = events.findLastIndex((event): event is Extract<SessionEvent, { type: 'tool/call' }> => (
    event.type === 'tool/call' && event.data.name === 'exit_plan_mode'
  ))
  if (callIndex < 0) invalid('no exit_plan_mode call exists in the Lead Session')

  const call = events[callIndex] as Extract<SessionEvent, { type: 'tool/call' }>
  const callId = String(call.data.callId)
  const results = events.slice(callIndex + 1).filter(event => isResultForCall(event, callId))
  if (results.length !== 1 || !isSuccessfulResultForCall(results[0] as SessionEvent, callId)) {
    invalid('latest exit_plan_mode call lacks one matching successful result')
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(call.data.arguments)
  } catch {
    invalid('latest exit_plan_mode call has malformed arguments')
  }
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)
    || typeof (parsed as Record<string, unknown>).plan !== 'string') {
    invalid('latest exit_plan_mode call has no markdown plan argument')
  }
  return parseApprovedPlanTasks((parsed as { plan: string }).plan)
}
