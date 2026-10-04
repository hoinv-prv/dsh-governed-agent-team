/** Exact isolated execution memory lifetime; GAT Detail Design §§9–10. */
import { type Context, symbols } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { DurableAgentConsumer, DurableAgentService } from '@deepseek-ai/dsh-durable-agent'
import type { DurableAgentDeclaration, DurableAgentRef } from '@deepseek-ai/dsh-durable-agent'
import { TeamError } from '@vuhoi/gat-core'
import type { TeamExecutionSnapshot } from '@deepseek-ai/dsh-experimental-agent-team/execution-types'
import type {} from '@deepseek-ai/dsh-subagent'
import { resolveExecutionTeam, assertExecutionSnapshot, type ExecutionTeamPort } from './execution-host.ts'
import { realpath } from 'node:fs/promises'
import { coordinatorFor } from './ownership.ts'
import { createDurableTools } from './tools.ts'

/** Explicit topology, durable members and task-result limits. */
export interface ExecutionCompositionConfig {
  readonly dedicatedProvider: true
  readonly singleHostWorkspace: true
  readonly workspace: string
  readonly members: readonly Readonly<{ declaration: DurableAgentDeclaration; mode: 'task' | 'reviewer' }>[]
  readonly limits: Readonly<{ maxBodyBytes: number; maxResultBytes: number; maxSelectedItems: number; maxReadCalls: number; maxReadResultBytes: number }>
}
/** Binding-owned authority and callback drain available to the optional reviewer. */
export interface ExecutionBindingScope {
  readonly team: ExecutionTeamPort
  readonly ctx: Context
  readonly agent: Agent
  readonly root: Agent
  readonly execution: TeamExecutionSnapshot
  readonly configuration: ExecutionCompositionConfig
  assertCurrent(): void
  assertActive(): void
  track<T>(run: () => Promise<T>): Promise<T>
  own(dispose: () => void): void
}
/** Install reviewer tools while the exact execution is still provisioning. */
export type ExecutionReviewInstaller = (scope: ExecutionBindingScope) => Promise<void>
function denied(): never { throw new TeamError('task memory binding is unavailable', 'TEAM_BINDING_UNAVAILABLE') }
function registered(ctx: Context): DurableAgentService {
  const service = ctx.get('durableAgent')
  if (service === undefined) denied()
  const underlying: unknown = Reflect.get(service, symbols.original) ?? service
  if (!(underlying instanceof DurableAgentService) || underlying.apiVersion !== 1
    || underlying.features.selectiveMemoryRead !== true) denied()
  return underlying
}
function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}
function freeze<T>(value: T): T {
  if (value !== null && typeof value === 'object') {
    for (const child of Object.values(value)) freeze(child)
    Object.freeze(value)
  }
  return value
}
function selectedId(args: unknown): string {
  if (!record(args) || Reflect.ownKeys(args).length !== 1) denied()
  const property = Object.getOwnPropertyDescriptor(args, 'itemId')
  if (property === undefined || !('value' in property) || typeof property.value !== 'string'
    || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(property.value)) denied()
  return property.value
}

class Binding {
  private readonly pending = new Set<Promise<unknown>>()
  private readonly disposers: (() => void)[] = []
  private phase: 'open' | 'closing' | 'closed' | 'failed' = 'open'
  private ref?: DurableAgentRef
  private cleanup?: Promise<void>
  private readonly root: Agent
  private readonly teamOwner: ExecutionTeamPort
  private readonly teamId: string
  private readonly selected: ReadonlySet<string>
  private readonly releaseOwner: () => void
  private readCalls = 0
  private readResultBytes = 0
  private readonly rendered = new WeakMap<object, string>()

  constructor(private readonly ctx: Context, private readonly agent: Agent,
    private readonly execution: TeamExecutionSnapshot, team: ExecutionTeamPort, private readonly service: DurableAgentService,
    private readonly workspace: string, private readonly member: ExecutionCompositionConfig['members'][number],
    private readonly limits: ExecutionCompositionConfig['limits'], private readonly configuration: ExecutionCompositionConfig,
    private readonly reviewInstaller?: ExecutionReviewInstaller,
    private readonly onClosed?: (binding: Binding) => void) {
    const parentId = agent.session.header.parentSession
    const root = parentId === undefined ? undefined : ctx.agents.get(parentId)
    const membership = team.tryMembership(agent)
    if (root === undefined || membership === undefined || membership.role !== 'teammate' || membership.root !== root
      || String(membership.id) !== root.id) denied()
    this.root = root
    this.teamOwner = team
    this.teamId = String(membership.id)
    const ids = execution.brief.inputs.filter(input => input.reference.startsWith('durable-memory:'))
      .map(input => input.reference.slice('durable-memory:'.length))
    if (ids.length > limits.maxSelectedItems || ids.some(id => !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(id))) denied()
    this.selected = new Set(ids)
    this.releaseOwner = coordinatorFor(service).reserve(workspace, member.declaration.name)
  }

  private authority(provisioning = false): void {
    if (this.phase !== 'open' || this.ctx.agents.get(this.agent.id) !== this.agent
      || this.ctx.agents.get(this.root.id) !== this.root || registered(this.ctx) !== this.service) denied()
    if (resolveExecutionTeam(this.ctx) !== this.teamOwner) denied()
    const current = this.teamOwner.executionFor(this.agent)
    const membership = this.teamOwner.tryMembership(this.agent)
    if (current !== undefined) assertExecutionSnapshot(current)
    if (current?.id !== this.execution.id || current.sessionId !== this.agent.id
      || current.memberId !== this.execution.memberId || current.memberName !== this.execution.memberName
      || current.generation !== this.execution.generation || current.taskId !== this.execution.taskId
      || current.taskRevision !== this.execution.taskRevision || membership?.role !== 'teammate'
      || String(membership.id) !== this.teamId || membership.root !== this.root
      || (current.phase !== 'active' && !(provisioning && current.phase === 'provisioning'))
      || JSON.stringify(current.brief) !== JSON.stringify(this.execution.brief)) denied()
    const task = this.teamOwner.getTask(this.root, current.taskId)
    if (task.id !== current.taskId || task.status !== 'in_progress' || task.ownerMemberId !== current.memberId
      || task.revision !== current.taskRevision) denied()
  }

  private async operation<T>(run: () => Promise<T>): Promise<T> {
    const pending = Promise.resolve().then(run)
    this.pending.add(pending)
    try { return await pending } finally { this.pending.delete(pending) }
  }

  async install(): Promise<void> {
    this.agent.ctx.effect(() => () => this.close(), 'taskMemory.close()')
    try {
      await this.operation(async () => {
        this.authority(true)
        await this.service.validateDeclaration(this.workspace, this.member.declaration)
        this.authority(true)
        this.ref = await this.service.provision(this.workspace, this.member.declaration)
        this.authority(true)
      })
      const consumer = new DurableAgentConsumer(this.service, this.ref!)
      const read = createDurableTools(consumer, () => this.authority())[0]!
      if (!record(read.schema)) denied()
      if (this.member.mode === 'task' && this.selected.size > 0) {
        this.disposers.push(this.agent.ctx.tools.register({
          name: read.name, description: 'Read a memory item explicitly selected in this task assignment.',
          parameters: read.schema,
          execute: async (args, exec) => {
            if (++this.readCalls > this.limits.maxReadCalls) denied()
            const id = selectedId(args)
            this.authority()
            if (!this.selected.has(id)) denied()
            return await this.operation(async () => {
              const item = await read.invoke(args)
              this.authority()
              if (!record(item) || item.id !== id || typeof item.content !== 'string'
                || Buffer.byteLength(item.content, 'utf8') > this.limits.maxBodyBytes
                || Buffer.byteLength(JSON.stringify(item), 'utf8') > this.limits.maxResultBytes) denied()
              const encoded = JSON.stringify(item)
              this.readResultBytes += Buffer.byteLength(encoded, 'utf8')
              if (this.readResultBytes > this.limits.maxReadResultBytes) denied()
              this.rendered.set(exec, encoded)
              return item
            })
          },
          output: { schema: {}, render: (_args, item) => [{ type: 'text', text: JSON.stringify(item) }] },
          finalizeContent: (exec, result) => {
            const denial = [{ type: 'text' as const, text: 'Task memory result unavailable.' }]
            const withheld = Buffer.byteLength(JSON.stringify(denial), 'utf8') <= this.limits.maxResultBytes ? denial : []
            try {
              this.authority()
              const expected = this.rendered.get(exec)
              if (exec.agent !== this.agent || result.additionalContexts?.length
                || Buffer.byteLength(JSON.stringify(result.content), 'utf8') > this.limits.maxResultBytes) return withheld
              if (!result.isError && (expected === undefined || JSON.stringify(result.value) !== expected)) return withheld
              if (!result.isError && JSON.stringify(result.content) !== JSON.stringify([{ type: 'text', text: expected }])) return withheld
              return undefined
            } catch { return withheld }
          },
        }))
        this.agent.ctx.on('tools/post-execute', async (exec, result, next) => {
          const decision = await next()
          if (exec.name !== read.name) return decision
          try {
            this.authority()
            if (decision.additionalContexts?.length || result.additionalContexts?.length) denied()
            if (decision.kind === 'accept' && (Object.hasOwn(decision, 'value')
              || (decision.content !== undefined && Buffer.byteLength(JSON.stringify(decision.content), 'utf8') > this.limits.maxResultBytes))) denied()
            return decision
          } catch { return { kind: 'block', feedback: [{ type: 'text', text: 'Task memory result unavailable.' }] } }
        })
      }
      this.agent.ctx.on('agent/request', async ({ signal }, next) => {
        signal.throwIfAborted()
        this.authority()
        const route = await next()
        signal.throwIfAborted()
        this.authority()
        return route
      })
      // Retained tools cannot grant a reviewer access to another owner's memory tool.
      this.agent.ctx.tools.guard(exec => this.member.mode === 'reviewer'
        && ['durable_agent_read_memory', 'durable_memory_read', 'durable_agent_submit_candidate'].includes(exec.name)
        ? 'This review assignment has no memory permission.' : undefined)
      this.agent.ctx.tools.guard(exec => exec.name === 'durable_agent_read_memory' && exec.parent !== undefined
        ? 'Task memory is available only through a top-level native call.' : undefined)
      if (this.member.mode === 'reviewer') {
        if (this.reviewInstaller === undefined) denied()
        await this.operation(async () => this.reviewInstaller!({
          ctx: this.ctx, team: this.teamOwner, agent: this.agent, root: this.root, execution: this.execution,
          configuration: this.configuration, assertCurrent: () => this.authority(true), assertActive: () => this.authority(),
          track: run => this.operation(run), own: dispose => {
            if (this.phase !== 'open') { dispose(); denied() }
            this.disposers.push(dispose)
          },
        }))
        this.authority(true)
      }
    } catch {
      await this.close()
      denied()
    }
  }

  close(): Promise<void> {
    if (this.cleanup !== undefined) return this.cleanup
    this.phase = 'closing'
    this.agent.cancel({ kind: 'hook', reason: 'task memory binding closed' })
    for (const dispose of this.disposers.splice(0).reverse()) dispose()
    this.cleanup = (async () => {
      // No tracked operation invokes/awaits close, so it cannot wait on itself.
      await Promise.allSettled([...this.pending])
      if (this.ref !== undefined) await this.service.release(this.ref)
      this.releaseOwner()
      this.phase = 'closed'
      this.onClosed?.(this)
    })().catch(() => { this.phase = 'failed'; denied() })
    // Observe errors even if a Fiber disposal reports them separately.
    void this.cleanup.catch(() => undefined)
    return this.cleanup
  }
}

/**
 * Install exact task bindings and Agent-owned guards through the plugin scope.
 * @param ctx Selected current Host context.
 * @param config Explicit normalized topology/member policy.
 * @param reviewInstaller Optional trusted reviewer installer; never used by ordinary tasks.
 */
export async function installExecutionBindings(ctx: Context, config: ExecutionCompositionConfig,
  reviewInstaller?: ExecutionReviewInstaller): Promise<void> {
  const keys = Object.keys(config).sort().join(',')
  if (keys !== 'dedicatedProvider,limits,members,singleHostWorkspace,workspace'
    || config.dedicatedProvider !== true || config.singleHostWorkspace !== true || typeof config.workspace !== 'string'
    || !Array.isArray(config.members) || Buffer.byteLength(JSON.stringify(config), 'utf8') > 65536
    || Object.keys(config.limits).sort().join(',') !== 'maxBodyBytes,maxReadCalls,maxReadResultBytes,maxResultBytes,maxSelectedItems') denied()
  for (const value of Object.values(config.limits)) {
    if (!Number.isSafeInteger(value) || value < 1) denied()
  }
  if (config.limits.maxBodyBytes > 65536 || config.limits.maxResultBytes > 65536
    || config.limits.maxResultBytes < 2
    || config.limits.maxReadCalls > 32 || config.limits.maxReadResultBytes > 262144
    || config.limits.maxSelectedItems > 32) denied()
  const team = resolveExecutionTeam(ctx)
  const workspace = await realpath(config.workspace)
  if (resolveExecutionTeam(ctx) !== team) denied()
  const limits = Object.freeze(structuredClone(config.limits))
  const members = freeze(structuredClone(config.members))
  const declarationKeys = ['name', 'description', 'prompt', 'context', 'provider', 'model', 'scope']
  if (members.length > 32 || members.some(member => !record(member.declaration)
    || Reflect.ownKeys(member.declaration).some(key => typeof key !== 'string' || ![...declarationKeys, 'reasoningEffort'].includes(key))
    || declarationKeys.some(key => !Object.hasOwn(member.declaration, key)))) denied()
  const names = members.map(member => member.declaration.name)
  if (new Set(names).size !== names.length || members.some(member => member.declaration.context !== 'fresh'
    || Object.keys(member).sort().join(',') !== 'declaration,mode'
    || member.declaration.scope !== 'workspace' || !['task', 'reviewer'].includes(member.mode))) denied()
  const configuration: ExecutionCompositionConfig = freeze({ dedicatedProvider: true, singleHostWorkspace: true, workspace, members: structuredClone(members), limits })
  const bindings = new Map<Agent, Binding>()
  ctx.on('agent/created', async ({ agent }) => {
    if (resolveExecutionTeam(ctx) !== team) denied()
    const execution = team.executionFor(agent)
    if (execution === undefined) return
    assertExecutionSnapshot(execution)
    const member = members.find(member => member.declaration.name === execution.memberName)
    if (member === undefined) denied()
    const binding = new Binding(ctx, agent, execution, team, registered(ctx), workspace, member, limits, configuration, reviewInstaller,
      closed => { if (bindings.get(agent) === closed) bindings.delete(agent) })
    bindings.set(agent, binding)
    await binding.install()
  })
  ctx.on('subagent/closing-child', async agent => { await bindings.get(agent)?.close() })
  ctx.effect(() => async () => {
    const results = await Promise.allSettled([...bindings.values()].map(binding => binding.close()))
    if (results.some(result => result.status === 'rejected')) denied()
  }, 'taskMemory.closeAll()')
}
