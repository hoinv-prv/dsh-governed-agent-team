import { mkdtemp, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import { builtInTeamMembers, loadTeamMembers } from '../src/team-config.ts'

const roots: string[] = []

async function workspace(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'gat-team-config-'))
  roots.push(root)
  return root
}

afterEach(async () => {
  await Promise.all(roots.splice(0).map(root => rm(root, { recursive: true, force: true })))
})

describe('workspace Team configuration', () => {
  it('loads and normalizes exact member routes', async () => {
    const root = await workspace()
    await writeFile(join(root, 'team_members.yaml'), `version: 1
members:
  - name: reviewer
    description: Reviews changes.
    prompt: Review the assigned change.
    provider: openai
    model: gpt-5.6-sol
    reasoning_effort: high
`)

    await expect(loadTeamMembers(root, 'fallback', 4, 65_536)).resolves.toEqual({
      source: 'workspace',
      diagnostics: [],
      members: [{
        name: 'reviewer',
        description: 'Reviews changes.',
        prompt: 'Review the assigned change.',
        context: 'fresh',
        provider: 'openai',
        model: 'gpt-5.6-sol',
        reasoningEffort: 'high',
      }],
    })
  })

  it('falls back for a missing or invalid workspace file', async () => {
    const root = await workspace()
    const missing = await loadTeamMembers(root, 'openai', 4, 65_536)
    expect(missing.source).toBe('built-in-default')
    expect(missing.members).toEqual(builtInTeamMembers('openai'))
    expect(missing.diagnostics[0]).toMatch(/used built-in defaults/)

    await writeFile(join(root, 'team_members.yaml'), 'version: 1\nmembers:\n  - name: Not Valid\n')
    const invalid = await loadTeamMembers(root, 'openai', 4, 65_536)
    expect(invalid.source).toBe('built-in-default')
  })

  it('rejects unknown fields and duplicate names through fallback', async () => {
    const root = await workspace()
    await writeFile(join(root, 'team_members.yaml'), `version: 1
members:
  - &member
    name: dev
    description: Develops.
    prompt: Implement.
    provider: openai
    model: gpt-5.6-terra
    unexpected: true
  - *member
`)
    const loaded = await loadTeamMembers(root, 'openai', 4, 65_536)
    expect(loaded.source).toBe('built-in-default')
    expect(loaded.diagnostics[0]).toMatch(/unknown field/)
  })

  it('bounds the workspace file before parsing and rejects symlinks', async () => {
    const root = await workspace()
    await writeFile(join(root, 'oversized.yaml'), 'x'.repeat(100))
    await symlink(join(root, 'oversized.yaml'), join(root, 'team_members.yaml'))
    const linked = await loadTeamMembers(root, 'openai', 4, 1_024)
    expect(linked.source).toBe('built-in-default')
    expect(linked.diagnostics[0]).toMatch(/regular file/)
    expect(linked.diagnostics[0]).not.toContain(root)

    await rm(join(root, 'team_members.yaml'))
    await writeFile(join(root, 'team_members.yaml'), 'x'.repeat(100))
    const oversized = await loadTeamMembers(root, 'openai', 4, 32)
    expect(oversized.source).toBe('built-in-default')
    expect(oversized.diagnostics[0]).toMatch(/exceeds 32 bytes/)
  })
})
