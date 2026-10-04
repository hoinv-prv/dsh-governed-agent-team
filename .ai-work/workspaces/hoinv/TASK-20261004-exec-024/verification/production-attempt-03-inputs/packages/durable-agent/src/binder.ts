import { realpath } from 'node:fs/promises'
import { DurableAgentConsumer } from '@deepseek-ai/dsh-durable-agent/consumer'
import type { DurableAgentDeclaration, DurableAgentRef, DurableAgentService } from '@deepseek-ai/dsh-durable-agent/service'
import { TeamError, validateAttachmentRequests } from '@vuhoi/gat-core'
import type { BinderBindInput, BinderPrepareInput, BindingIdentity, DisposableBinding, JsonValue, PreparedAttachment, TeamMemberBinder } from '@vuhoi/gat-core'
import { coordinatorFor } from './ownership.ts'
import { createDurableTools } from './tools.ts'

/** Persist the strict declaration and trusted selectors without runtime references. */
export interface DurableAttachmentV1 {
  readonly schemaVersion: 1
  readonly serviceBindingKey: string
  readonly workspaceRealpath: string
  readonly declaration: DurableAgentDeclaration & { readonly context: 'fresh'; readonly scope: 'workspace' }
}
/** Trusted composition assertions must be established by the host deployment owner. */
export interface DurableBinderComposition {
  readonly serviceBindingKey: string
  readonly service: DurableAgentService
  readonly dedicatedProvider: true
  readonly singleHostWorkspace: true
  resolveService(key: string): DurableAgentService | undefined
  resolveWorkspace(identity: BindingIdentity): Promise<string>
}

function isTrue(value: unknown): boolean { return value === true }
function isV1(value: unknown): boolean { return value === 1 }
function unavailable(): never { throw new TeamError('required Durable binding unavailable', 'TEAM_BINDING_UNAVAILABLE') }
function closed(value: unknown, keys: readonly string[], optional: readonly string[] = []): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) unavailable()
  const record = value as Record<string, unknown>
  if (keys.some(key => !(key in record)) || Object.keys(record).some(key => !keys.includes(key) && !optional.includes(key))) unavailable()
  return record
}
function text(value: unknown, max: number): value is string {
  return typeof value === 'string' && value.length > 0 && value === value.trim() && value.length <= max && !value.includes('\0')
}
function payload(value: JsonValue, input: BindingIdentity, composition: DurableBinderComposition): DurableAttachmentV1 {
  const validated = validateAttachmentRequests([{ binderId: 'durable-agent', protocolVersion: 1, required: true, payload: value }])[0]
  if (!validated) unavailable()
  const detached = validated.payload
  const root = closed(detached, ['schemaVersion', 'serviceBindingKey', 'workspaceRealpath', 'declaration'])
  const d = closed(root.declaration, ['name', 'description', 'prompt', 'context', 'provider', 'model', 'scope'], ['reasoningEffort'])
  if (root.schemaVersion !== 1 || root.serviceBindingKey !== composition.serviceBindingKey || !text(root.workspaceRealpath, 16_384)
    || d.name !== input.memberName || !text(d.name, 64) || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(d.name)
    || !text(d.description, 200) || !text(d.prompt, 16_384) || !text(d.provider, 200) || !text(d.model, 200)
    || d.context !== 'fresh' || d.scope !== 'workspace' || (d.reasoningEffort !== undefined && !text(d.reasoningEffort, 80))) unavailable()
  return detached as unknown as DurableAttachmentV1
}

class DurableLease implements DisposableBinding {
  private ref?: DurableAgentRef
  private provision?: Promise<void>
  private cleanup?: Promise<void>
  private readonly operations = new Set<Promise<unknown>>()
  private readonly removers: (() => void)[] = []
  private closed = false
  private transferred = false
  private installed = false
  constructor(readonly attachment: DurableAttachmentV1, readonly identity: BindingIdentity,
    private readonly composition: DurableBinderComposition, private readonly releaseOwner: () => void,
  ) {}
  private check(scope: BinderBindInput['scope'], action?: 'read' | 'effect' | 'request'): void {
    try {
      if (this.closed || !scope.isCurrent()
        || this.composition.resolveService(this.attachment.serviceBindingKey) !== this.composition.service) unavailable()
      if (action) scope.authorize(action)
    } catch (error) {
      try { this.closeAdmission() } catch { /* all removers attempted before cleanup */ }
      // Never await self-drain from inside an admitted tool/refresh operation.
      queueMicrotask(() => { void this.release(new AbortController().signal).catch(() => undefined) })
      throw error
    }
  }
  private async track<T>(operation: () => Promise<T>): Promise<T> {
    const pending = Promise.resolve().then(operation)
    this.operations.add(pending)
    try { return await pending } finally { this.operations.delete(pending) }
  }
  async bind(input: BinderBindInput, signal: AbortSignal): Promise<DisposableBinding> {
    signal.throwIfAborted()
    if (input.workspaceRealpath !== this.attachment.workspaceRealpath) unavailable()
    this.check(input.scope)
    if (this.transferred || this.closed || JSON.stringify(this.identity) !== JSON.stringify({
      teamId: input.teamId, memberId: input.memberId, memberName: input.memberName, generation: input.generation,
    })) unavailable()
    this.transferred = true
    const onAbort = () => {
      try { this.closeAdmission() } catch { /* each remover was attempted */ }
      queueMicrotask(() => { void this.release(new AbortController().signal).catch(() => undefined) })
    }
    signal.addEventListener('abort', onAbort, { once: true })
    this.removers.push(() =>{  signal.removeEventListener('abort', onAbort) })
    const service = this.composition.service
    this.provision = (async () => { this.ref = await service.provision(this.attachment.workspaceRealpath, this.attachment.declaration) })()
    try {
      await this.provision
      signal.throwIfAborted(); this.check(input.scope)
      const ref = this.ref
      if (!ref) unavailable()
      const consumer = new DurableAgentConsumer(service, ref)
      const key = `gat:durable-agent:${input.teamId}:${input.memberId}:${input.generation}`
      const refresh = async (authorize: boolean) =>{  await this.track(async () => {
        this.check(input.scope, authorize ? 'request' : undefined)
        const contribution = await consumer.modelContribution()
        signal.throwIfAborted(); this.check(input.scope, authorize ? 'request' : undefined)
        if (typeof contribution.prompt !== 'string' || Buffer.byteLength(contribution.prompt, 'utf8') > 1_048_576) unavailable()
        if (!this.installed) {
          const tools = createDurableTools(consumer, (action) => { this.check(input.scope, action) }).map(tool => ({
            ...tool, invoke: (args: unknown) => this.track(() => tool.invoke(args)),
          }))
          this.removers.push(input.scope.install({ key, prompt: contribution.prompt, tools }))
          this.installed = true
        } else input.scope.replacePrompt(key, contribution.prompt)
      }) }
      await refresh(false)
      this.removers.push(input.scope.beforeRequest(() => refresh(true)))
      signal.throwIfAborted(); this.check(input.scope)
      return this
    } catch (error) {
      const failures: unknown[] = [error]
      try { this.closeAdmission() } catch (cleanup) { failures.push(cleanup) }
      try { await this.release(new AbortController().signal) } catch (cleanup) { failures.push(cleanup) }
      if (failures.length > 1) throw new AggregateError(failures, 'Durable binding acquisition and cleanup failed')
      throw error
    }
  }
  closeAdmission(): void {
    if (this.closed) return
    this.closed = true
    const failures: unknown[] = []
    for (const remove of this.removers.splice(0).reverse()) { try { remove() } catch (error) { failures.push(error) } }
    if (failures.length) throw new AggregateError(failures, 'Durable contribution removal failed')
  }
  async settle(_signal: AbortSignal): Promise<void> {
    await Promise.allSettled([...this.operations])
  }
  release(_signal: AbortSignal): Promise<void> {
    if (this.cleanup) return this.cleanup
    try { this.closeAdmission() } catch { /* all removers already attempted */ }
    this.cleanup = (async () => {
      await this.provision?.catch(() => undefined)
      await this.settle(_signal)
      if (this.ref) await this.composition.service.release(this.ref)
      this.releaseOwner()
    })()
    void this.cleanup.catch(() => undefined)
    return this.cleanup
  }
  abort(signal: AbortSignal): Promise<void> { return this.release(signal) }
}

/**
 * Create a WK v1 binder for the selected trusted host topology.
 * @param composition Exact provider identity, topology assertions and independent resolvers.
 * @returns Required member binder with exclusive ownership and bounded scoped contributions.
 */
export function createDurableAgentBinder(composition: DurableBinderComposition): TeamMemberBinder<DurableLease> {
  if (!isTrue(composition.dedicatedProvider) || !isTrue(composition.singleHostWorkspace)
    || !text(composition.serviceBindingKey, 200)) unavailable()
  const service = composition.service
  const coordinator = coordinatorFor(service)
  const validate = async (input: BindingIdentity & { workspaceRealpath: string }, value: JsonValue, signal: AbortSignal) => {
    signal.throwIfAborted()
    if (composition.resolveService(composition.serviceBindingKey) !== service || !isV1(service.apiVersion)
      || !isTrue(service.features.selectiveMemoryRead) || !isTrue(service.features.memoryCandidateSubmission)) unavailable()
    const attachment = payload(value, input, composition)
    const workspace = await composition.resolveWorkspace(input)
    if (workspace !== attachment.workspaceRealpath || workspace !== input.workspaceRealpath
      || await realpath(workspace) !== workspace) unavailable()
    await service.validateDeclaration(workspace, attachment.declaration)
    signal.throwIfAborted()
    if (composition.resolveService(composition.serviceBindingKey) !== service) unavailable()
    return attachment
  }
  return {
    id: 'durable-agent', protocolVersion: 1,
    async prepare(input: BinderPrepareInput, signal): Promise<PreparedAttachment<DurableLease>> {
      const attachment = await validate(input, input.payload, signal)
      const d = attachment.declaration
      const route = input.spec.agentOptions
      if (route === undefined || input.spec.name !== d.name || input.spec.context !== 'fresh' || input.spec.description !== d.description
        || route.provider !== d.provider || route.model !== d.model || route.reasoningEffort !== d.reasoningEffort
        || input.spec.initialTask.length !== 1 || input.spec.initialTask[0]?.type !== 'text'
        || (input.spec.initialTask[0] as { text?: string }).text !== d.prompt) unavailable()
      const releaseOwner = coordinator.reserve(attachment.workspaceRealpath, d.name)
      const value = new DurableLease(attachment, {
        teamId: input.teamId, memberId: input.memberId, memberName: input.memberName, generation: input.generation,
      }, composition, releaseOwner)
      return { attachment: attachment as unknown as JsonValue, value, abort: signal => value.abort(signal) }
    },
    async bind(input, value, prepared, signal) {
      if (!(prepared instanceof DurableLease) || JSON.stringify(prepared.attachment)
        !== JSON.stringify(payload(value, input, composition))) unavailable()
      await validate(input, value, signal)
      return await prepared.bind(input, signal)
    },
    async recover(input, value, signal) {
      const attachment = await validate(input, value, signal)
      const releaseOwner = coordinator.reserve(attachment.workspaceRealpath, attachment.declaration.name)
      const lease = new DurableLease(attachment, {
        teamId: input.teamId, memberId: input.memberId, memberName: input.memberName, generation: input.generation,
      }, composition, releaseOwner)
      try { return await lease.bind(input, signal) } catch (error) {
        try { await lease.abort(new AbortController().signal) } catch (cleanup) {
          throw new AggregateError([error, cleanup], 'Durable recovery and cleanup failed')
        }
        throw error
      }
    },
  }
}
