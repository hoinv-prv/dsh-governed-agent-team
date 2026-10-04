/** Test-only feasibility candidate: GAT DETAIL_DESIGN §9, task/intent policy. */
import { Context, symbols } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { DurableAgentConsumer, DurableAgentService } from '@deepseek-ai/dsh-durable-agent'
import type { DurableAgentDeclaration, DurableAgentRef } from '@deepseek-ai/dsh-durable-agent'
import { TeamError } from '@vuhoi/gat-core'
import type { TeamExecutionSnapshot } from '@vuhoi/gat-core'
import { realpath } from 'node:fs/promises'
import { coordinatorFor } from './qualification-shared/ownership.ts'
import { createDurableTools } from './qualification-shared/tools.ts'

export interface PrototypeConfig {
  readonly workspace: string
  readonly members: readonly Readonly<{ declaration: DurableAgentDeclaration; mode: 'task' | 'reviewer' }>[]
  readonly limits: Readonly<{ maxBodyBytes: number; maxResultBytes: number; maxSelectedItems: number }>
}
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
  private readonly teamId: string
  private readonly selected: ReadonlySet<string>
  private readonly releaseOwner: () => void

  constructor(private readonly ctx: Context, private readonly agent: Agent,
    private readonly execution: TeamExecutionSnapshot, private readonly service: DurableAgentService,
    private readonly workspace: string, private readonly member: PrototypeConfig['members'][number],
    private readonly limits: PrototypeConfig['limits']) {
    const parentId = agent.session.header.parentSession
    const root = parentId === undefined ? undefined : ctx.agents.get(parentId)
    const membership = ctx.agentTeams.tryMembership(agent)
    if (root === undefined || membership === undefined || membership.role !== 'teammate') denied()
    this.root = root
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
    const current = this.ctx.agentTeams.executionFor(this.agent)
    const membership = this.ctx.agentTeams.tryMembership(this.agent)
    if (current?.id !== this.execution.id || current.sessionId !== this.agent.id
      || current.memberId !== this.execution.memberId || current.memberName !== this.execution.memberName
      || current.generation !== this.execution.generation || current.taskId !== this.execution.taskId
      || current.taskRevision !== this.execution.taskRevision || membership?.role !== 'teammate'
      || String(membership.id) !== this.teamId
      || (current.phase !== 'active' && !(provisioning && current.phase === 'provisioning'))
      || JSON.stringify(current.brief) !== JSON.stringify(this.execution.brief)) denied()
    const task = this.ctx.agentTeams.getTask(this.root, current.taskId)
    if (task.status !== 'in_progress' || task.ownerMemberId !== current.memberId
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
      if (this.member.mode === 'task' && this.selected.size > 0) {
        this.disposers.push(this.agent.ctx.tools.register({
          name: read.name, description: 'Read a memory item explicitly selected in this task assignment.',
          parameters: read.schema,
          execute: async args => {
            const id = selectedId(args)
            this.authority()
            if (!this.selected.has(id)) denied()
            return await this.operation(async () => {
              const item = await read.invoke(args)
              this.authority()
              if (!record(item) || typeof item.content !== 'string'
                || Buffer.byteLength(item.content, 'utf8') > this.limits.maxBodyBytes
                || Buffer.byteLength(JSON.stringify(item), 'utf8') > this.limits.maxResultBytes) denied()
              return item
            })
          },
          output: { schema: {}, render: (_args, item) => [{ type: 'text', text: JSON.stringify(item) }] },
        }))
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
    } catch {
      await this.close()
      denied()
    }
  }

  close(): Promise<void> {
    if (this.cleanup !== undefined) return this.cleanup
    this.phase = 'closing'
    for (const dispose of this.disposers.splice(0).reverse()) dispose()
    this.cleanup = (async () => {
      // No tracked operation invokes/awaits close, so it cannot wait on itself.
      await Promise.allSettled([...this.pending])
      if (this.ref !== undefined) await this.service.release(this.ref)
      this.releaseOwner()
      this.phase = 'closed'
    })().catch(() => { this.phase = 'failed'; denied() })
    // Observe errors even if a Fiber disposal reports them separately.
    void this.cleanup.catch(() => undefined)
    return this.cleanup
  }
}

export function prototype(config: PrototypeConfig) {
  return {
    name: 'gat-task-memory-qualification', inject: ['agentTeams', 'agents', 'tools', 'durableAgent'],
    async apply(ctx: Context) {
      for (const value of Object.values(config.limits)) {
        if (!Number.isSafeInteger(value) || value < 1) denied()
      }
      const workspace = await realpath(config.workspace)
      const limits = Object.freeze(structuredClone(config.limits))
      const members = structuredClone(config.members)
      const names = members.map(member => member.declaration.name)
      if (new Set(names).size !== names.length || members.some(member => member.declaration.context !== 'fresh'
        || member.declaration.scope !== 'workspace' || !['task', 'reviewer'].includes(member.mode))) denied()
      const bindings = new Map<Agent, Binding>()
      ctx.on('agent/created', async ({ agent }) => {
        const execution = ctx.agentTeams.executionFor(agent)
        if (execution === undefined) return
        const member = members.find(member => member.declaration.name === execution.memberName)
        if (member === undefined) denied()
        const binding = new Binding(ctx, agent, execution, registered(ctx), workspace, member, limits)
        bindings.set(agent, binding)
        await binding.install()
      })
      ctx.on('subagent/closing-child', async agent => { await bindings.get(agent)?.close() })
      ctx.effect(() => async () => {
        const results = await Promise.allSettled([...bindings.values()].map(binding => binding.close()))
        if (results.some(result => result.status === 'rejected')) denied()
      }, 'taskMemory.closeAll()')
    },
  }
}
