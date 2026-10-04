import { mkdtemp, realpath, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { type DurableRoutePreflight, loadDurableTeamMembers } from '../src/initializer.ts'

const fileName = 'team_members.durable.yaml'

function validMember(overrides: Record<string, unknown> = {}) {
  return {
    name: 'implementer',
    description: 'Implements assigned work.',
    prompt: 'Use the Team task board and report evidence.',
    context: 'fresh',
    provider: 'mock',
    model: 'model-a',
    durable: { scope: 'workspace' },
    ...overrides,
  }
}

describe('Durable Team initializer', () => {
  let root: string
  let workspaceRealpath: string
  let routePreflight: ReturnType<typeof vi.fn<DurableRoutePreflight>>

  beforeEach(async () => {
    root = await mkdtemp(join(tmpdir(), 'gat-durable-initializer-'))
    workspaceRealpath = await realpath(root)
    routePreflight = vi.fn(async () => ({ provider: 'mock', model: 'model-a' }))
  })

  afterEach(async () => {
    await rm(root, { recursive: true, force: true })
  })

  async function write(value: unknown): Promise<void> {
    await writeFile(join(workspaceRealpath, fileName), typeof value === 'string' ? value : JSON.stringify(value))
  }

  function load(maxBytes = 65_536) {
    return loadDurableTeamMembers({
      workspaceRealpath,
      serviceBindingKey: 'durable-main',
      continuationProvider: 'spawn',
      maxMembers: 4,
      maxBytes,
      routePreflight,
    })
  }

  it('returns detached normalized members with a required v1 attachment', async () => {
    await write({ version: 1, members: [validMember({ reasoning_effort: 'high' })] })

    const result = await load()

    expect(routePreflight).toHaveBeenCalledOnce()
    expect(routePreflight.mock.calls[0]?.[0]).toEqual({
      provider: 'mock', model: 'model-a', reasoningEffort: 'high',
    })
    expect(result).toMatchObject({ source: 'durable-workspace', diagnostics: [], members: [{
      name: 'implementer',
      description: 'Implements assigned work.',
      initialTask: [{ type: 'text', text: 'Use the Team task board and report evidence.' }],
      context: 'fresh',
      continuationProvider: 'spawn',
      agentOptions: { provider: 'mock', model: 'model-a' },
      attachments: [{
        binderId: 'durable-agent', protocolVersion: 1, required: true,
        payload: {
          schemaVersion: 1,
          serviceBindingKey: 'durable-main',
          workspaceRealpath,
          declaration: {
            name: 'implementer',
            description: 'Implements assigned work.',
            prompt: 'Use the Team task board and report evidence.',
            context: 'fresh', provider: 'mock', model: 'model-a', reasoningEffort: 'high', scope: 'workspace',
          },
        },
      }],
    }] })
  })

  it('fails closed when the explicit Durable config is missing', async () => {
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    expect(routePreflight).not.toHaveBeenCalled()
  })

  it('rejects malformed YAML without defaulting to an unbound roster', async () => {
    await write('version: [\nmembers: nope')
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    expect(routePreflight).not.toHaveBeenCalled()
  })

  it('rejects duplicate member names', async () => {
    await write({ version: 1, members: [validMember(), validMember()] })
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    expect(routePreflight).not.toHaveBeenCalled()
  })

  it('rejects unknown document, member, and durable fields', async () => {
    for (const config of [
      { version: 1, members: [validMember()], extra: true },
      { version: 1, members: [validMember({ extra: true })] },
      { version: 1, members: [validMember({ durable: { scope: 'workspace', extra: true } })] },
    ]) {
      await write(config)
      await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    }
    expect(routePreflight).not.toHaveBeenCalled()
  })

  it('rejects global scope and fork context for this adapter', async () => {
    await write({ version: 1, members: [validMember({ durable: { scope: 'global' } })] })
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    await write({ version: 1, members: [validMember({ context: 'fork' })] })
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    expect(routePreflight).not.toHaveBeenCalled()
  })

  it('rejects the reserved Lead identity and aliases', async () => {
    await write({ version: 1, members: [validMember({ name: 'lead' })] })
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    await write('version: 1\nmembers: &members []\ncopy: *members\n')
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
  })

  it('sanitizes route preflight failures', async () => {
    await write({ version: 1, members: [validMember()] })
    routePreflight.mockRejectedValueOnce(new Error(`route failure at ${workspaceRealpath}`))

    const error = await load().catch((value: unknown) => value)

    expect(error).toMatchObject({ code: 'TEAM_INVALID_CONFIG', message: 'Durable Team route preflight failed' })
    expect((error as Error).message).not.toContain(workspaceRealpath)
  })

  it('bounds reads and rejects symlinked config files', async () => {
    await write({ version: 1, members: [validMember()] })
    await expect(load(8)).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    await rm(join(workspaceRealpath, fileName))
    const outside = join(root, 'outside.yaml')
    await writeFile(outside, JSON.stringify({ version: 1, members: [validMember()] }))
    await symlink(outside, join(workspaceRealpath, fileName))
    await expect(load()).rejects.toMatchObject({ code: 'TEAM_INVALID_CONFIG' })
    expect(routePreflight).not.toHaveBeenCalled()
  })
})
