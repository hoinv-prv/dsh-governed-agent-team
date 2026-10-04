/** Independent assertions over actual persisted Sessions, before normalization/refresh. */
import { expect } from 'vitest'

type Row = Record<string, unknown>
const SELECTED_BODY = 'TASK_SELECTED_MEMORY_BODY: cobalt tulip'
const UNSELECTED_BODY = 'TASK_UNSELECTED_MEMORY_BODY: amber fern'
function rows(log: string): Row[] { return log.trim().split('\n').map(line => JSON.parse(line) as Row) }
function events(log: string, type: string): Row[] {
  return rows(log).filter(row => row.type === type).map(row => row.data as Row)
}
function text(content: unknown): string {
  if (!Array.isArray(content)) throw new Error('missing actual tool content')
  return content.map(block => String((block as Row).text ?? '')).join('\n')
}

/** Check actual attribution, native tool delivery, prompt isolation and separate Lead acceptance. */
export function verifyDurableExecution(logs: readonly string[]): void {
  expect(logs, 'Lead, fresh bootstrap, fresh execution').toHaveLength(3)
  const [lead, bootstrap, task] = logs as readonly [string, string, string]
  const headers = logs.map(log => rows(log)[0]!)
  expect(new Set(headers.map(header => header.id)).size).toBe(3)
  for (const header of headers.slice(1)) {
    expect(header.parentSession).toBe(headers[0]!.id)
    expect(header.isSeeded).toBe(false)
    expect(header.seedLength).toBeUndefined()
  }
  const assignments = events(lead, 'team/assignment').map(event => event.execution as Row)
  expect(assignments).toHaveLength(1)
  const own = assignments[0]!
  expect(own).toMatchObject({ requestId: 'memory-request', taskId: 'task-1', memberName: 'worker',
    memberId: headers[1]!.id, sessionId: headers[2]!.id, generation: 1 })
  expect(headers.map(header => header.id)).not.toContain(own.id)
  expect((own.brief as Row).inputs).toEqual([{ reference: 'durable-memory:selected', revision: 'fixture-1' }])
  for (const log of logs) {
    const systems = events(log, 'system/message').map(event => JSON.stringify((event.message as Row).content))
    expect(systems.length, 'actual system messages are inspected').toBeGreaterThan(0)
    expect(systems.join('\n')).not.toMatch(/TASK_(?:SELECTED|UNSELECTED)_MEMORY_BODY|MEMORY_CATALOG_|MEMORY_INTENT_/u)
    const schemas = events(log, 'request/header').map(event => JSON.stringify((event.header as Row).tools))
    expect(schemas.join('\n')).not.toMatch(/durable_agent_submit_candidate|durable_memory_write|commit_memory/u)
    expect(log).not.toContain(UNSELECTED_BODY)
  }
  expect(bootstrap).not.toContain(SELECTED_BODY)
  expect(events(bootstrap, 'tool/call')).toEqual([])
  for (const log of [lead, bootstrap]) {
    const schemas = events(log, 'request/header').map(event => JSON.stringify((event.header as Row).tools))
    expect(schemas.join('\n')).not.toContain('durable_agent_read_memory')
  }
  const calls = events(task, 'tool/call')
  expect(calls.map(call => call.name)).toEqual(['durable_agent_read_memory', 'durable_agent_read_memory', 'team_execution_submit'])
  expect(JSON.parse(String(calls[0]!.arguments))).toEqual({ itemId: 'selected' })
  expect(JSON.parse(String(calls[1]!.arguments))).toEqual({ itemId: 'unselected' })
  const results = events(task, 'tool/result').map(event => event.message as Row)
  const selected = results.find(result => result.toolCallId === calls[0]!.callId)!
  expect(selected).toMatchObject({ isError: false })
  expect(JSON.parse(text(selected.content))).toMatchObject({ id: 'selected', content: SELECTED_BODY })
  const denied = results.find(result => result.toolCallId === calls[1]!.callId)!
  expect(denied).toMatchObject({ isError: true })
  expect(Buffer.byteLength(JSON.stringify(denied.content), 'utf8')).toBeLessThanOrEqual(8192)
  const taskRows = rows(task)
  const firstRead = taskRows.findIndex(row => row.type === 'tool/call')
  expect(taskRows.slice(0, firstRead).map(row => JSON.stringify(row)).join('\n'))
    .not.toMatch(/TASK_(?:SELECTED|UNSELECTED)_MEMORY_BODY|MEMORY_CATALOG_|MEMORY_INTENT_/u)
  const selectedResult = taskRows.findIndex(row => row.type === 'tool/result'
    && ((row.data as Row).message as Row).toolCallId === calls[0]!.callId)
  expect(taskRows.slice(selectedResult + 1).some(row => row.type === 'step/start')).toBe(true)
  expect(JSON.parse(String(calls[2]!.arguments))).toMatchObject({ execution_id: own.id, outcome: 'completed' })
  expect(results.find(result => result.toolCallId === calls[2]!.callId)).toMatchObject({ isError: false })
  const lifecycle = events(lead, 'team/execution').map(event => event.execution as Row).filter(execution => execution.id === own.id)
  expect(lifecycle.map(execution => execution.phase)).toEqual(['active', 'closing', 'completed'])
  expect(lifecycle.at(-1)).toMatchObject({ finalOutcome: 'completed', result: 'MEMORY_TASK_RESULT: cobalt tulip; unselected read denied.' })
  const leadCalls = events(lead, 'tool/call')
  expect(leadCalls.map(call => call.name)).toEqual(['team_task_create', 'team_task_assign', 'team_execution_get', 'team_task_get', 'team_task_update'])
  const leadResults = events(lead, 'tool/result').map(event => event.message as Row)
  expect(leadResults.every(result => result.isError === false), JSON.stringify(leadResults)).toBe(true)
  const beforeAcceptance = leadResults.find(result => result.toolCallId === leadCalls[3]!.callId)!
  expect(JSON.parse(text(beforeAcceptance.content))).toMatchObject({ id: 'task-1', status: 'in_progress', revision: 2 })
  expect(JSON.parse(String(leadCalls[4]!.arguments))).toEqual({ task_id: 'task-1', expected_revision: 2, action: 'complete' })
  expect(events(lead, 'team/task').map(event => event.task as Row).at(-1)).toMatchObject({ id: 'task-1', status: 'completed', revision: 3 })
}
