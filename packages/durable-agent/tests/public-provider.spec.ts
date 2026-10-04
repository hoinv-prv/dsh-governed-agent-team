import { mkdtemp, realpath, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import { LocalDurableAgentProvider } from '@deepseek-ai/dsh-durable-agent'
import type { DurableAgentRef } from '@deepseek-ai/dsh-durable-agent/service'
import type { BinderPrepareInput, CapabilityContribution, MemberCapabilityScope } from '@vuhoi/gat-core'
import { createDurableAgentBinder } from '../src/binder.ts'

describe('WK public provider in temporary storage', () => {
  it('retains independently committed memory across release/recovery and submits only unconfirmed candidates', async () => {
    const root = await mkdtemp(join(tmpdir(), 'gat-wk-public-'))
    const workspaceRealpath = await realpath(root)
    const ctx = new Context()
    const service = new LocalDurableAgentProvider(ctx)
    let contribution: CapabilityContribution | undefined
    let refresh: (() => Promise<void>) | undefined
    let current = true
    const scope: MemberCapabilityScope = {
      isCurrent: () => current, authorize: () => { if (!current) throw new Error('host lease unavailable') },
      install: (value) => { contribution = value; return () => { contribution = undefined } },
      beforeRequest: (value) => { refresh = value; return () => { refresh = undefined } },
      replacePrompt: (_key, prompt) => { contribution = { ...contribution!, prompt } },
    }
    const declaration = { name: 'implementer', description: 'Implement approved work', prompt: 'Use assigned tasks', context: 'fresh' as const, provider: 'mock', model: 'mock', scope: 'workspace' as const }
    const input: BinderPrepareInput = {
      teamId: 'team', memberId: 'member', memberName: 'implementer', generation: 'first', workspaceRealpath,
      spec: { name: declaration.name, description: declaration.description, initialTask: [{ type: 'text', text: declaration.prompt }], context: 'fresh', continuationProvider: 'spawn', agentOptions: { provider: 'mock', model: 'mock' } },
      payload: { schemaVersion: 1, serviceBindingKey: 'fixture', workspaceRealpath, declaration },
    }
    const binder = createDurableAgentBinder({ service, serviceBindingKey: 'fixture', dedicatedProvider: true, singleHostWorkspace: true, resolveService: () => service, resolveWorkspace: async () => workspaceRealpath })
    const signal = new AbortController().signal
    let ref: DurableAgentRef | undefined
    try {
      // Public host setup supplies independent authorization; it is never a model-facing tool.
      ref = await service.provision(workspaceRealpath, declaration)
      await service.commitMemoryItem(ref, { item: { id: 'rule-one', title: 'One rule', retrievalCondition: 'When implementing', content: 'Preserve evidence' }, authorization: { kind: 'human', authorizationRef: 'temporary-test-approval' } })
      await service.release(ref); ref = undefined
      const prepared = await binder.prepare(input, signal)
      const binding = await binder.bind({ ...input, scope }, prepared.attachment, prepared.value, signal)
      expect(contribution!.tools.map(tool => tool.name)).toEqual(['durable_agent_read_memory', 'durable_agent_submit_candidate'])
      expect((JSON.parse(contribution!.prompt) as { catalog: unknown[] }).catalog).toEqual([expect.objectContaining({ id: 'rule-one' })])
      const read = contribution!.tools[0]!
      expect(await read.invoke({ itemId: 'rule-one' })).toMatchObject({ content: 'Preserve evidence' })
      expect(await contribution!.tools[1]!.invoke({ title: 'Possible rule', retrievalCondition: 'During review', content: 'Candidate only', provenance: 'temporary fixture', confidence: 'medium', limitations: [] })).toMatchObject({ status: 'unconfirmed' })
      await refresh!()
      const before = (JSON.parse(contribution!.prompt) as { revision: number }).revision
      binding.closeAdmission()
      await binding.settle(signal); await binding.release(signal)
      expect(contribution).toBeUndefined()
      await expect(read.invoke({ itemId: 'rule-one' })).rejects.toThrow()
      const recovered = await binder.recover({ ...input, generation: 'second', scope }, prepared.attachment, signal)
      expect((JSON.parse(contribution!.prompt) as { revision: number }).revision).toBe(before)
      expect(await contribution!.tools[0]!.invoke({ itemId: 'rule-one' })).toMatchObject({ content: 'Preserve evidence' })
      current = false
      await expect(refresh!()).rejects.toThrow()
      recovered.closeAdmission(); await recovered.settle(signal); await recovered.release(signal)
    } finally {
      if (ref) await service.release(ref)
      await ctx.fiber.dispose()
      await rm(root, { recursive: true, force: true })
    }
  })
})
