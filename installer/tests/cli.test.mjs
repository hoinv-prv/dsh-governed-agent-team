import { execFileSync, spawnSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { afterEach, describe, it } from 'node:test'
import assert from 'node:assert/strict'

const ROOT = fileURLToPath(new URL('../..', import.meta.url))
const INSTALLER = join(ROOT, 'installer', 'index.mjs')
const roots = []

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})

function temporaryRepository(version = '0.1.5-rc.2') {
  const root = mkdtempSync(join(tmpdir(), 'gat-installer-test-'))
  roots.push(root)
  execFileSync('git', ['init', '--quiet'], { cwd: root })
  execFileSync('git', ['config', 'user.name', 'GAT Test'], { cwd: root })
  execFileSync('git', ['config', 'user.email', 'gat-test@example.invalid'], { cwd: root })
  writeFileSync(join(root, 'package.json'), `${JSON.stringify({ version })}\n`)
  execFileSync('git', ['add', 'package.json'], { cwd: root })
  execFileSync('git', ['commit', '--quiet', '-m', 'fixture'], { cwd: root })
  return root
}

describe('GAT installer CLI', () => {
  it('rejects an unknown operation without touching a target', () => {
    const result = spawnSync(process.execPath, [INSTALLER, 'unknown'], { encoding: 'utf8' })
    assert.equal(result.status, 2)
    assert.match(result.stderr, /unknown or missing operation/u)
  })

  it('rejects every unpinned DSH commit before installation writes', () => {
    const target = temporaryRepository()
    const before = execFileSync('git', ['status', '--porcelain=v1', '--untracked-files=all'], { cwd: target, encoding: 'utf8' })
    const result = spawnSync(process.execPath, [INSTALLER, 'dry-run', '--target', target], { encoding: 'utf8' })
    const after = execFileSync('git', ['status', '--porcelain=v1', '--untracked-files=all'], { cwd: target, encoding: 'utf8' })
    assert.equal(result.status, 1)
    assert.match(result.stderr, /unsupported DSH commit/u)
    assert.equal(after, before)
  })

  it('rejects a target path that is not the worktree root', () => {
    const target = temporaryRepository()
    const nested = resolve(target, 'nested')
    mkdirSync(nested)
    const result = spawnSync(process.execPath, [INSTALLER, 'dry-run', '--target', nested], { encoding: 'utf8' })
    assert.equal(result.status, 1)
    assert.match(result.stderr, /target must be the DSH worktree root/u)
  })
})
