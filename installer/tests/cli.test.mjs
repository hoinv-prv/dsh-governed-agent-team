import { execFileSync, spawnSync } from 'node:child_process'
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { afterEach, describe, it } from 'node:test'
import assert from 'node:assert/strict'

const ROOT = fileURLToPath(new URL('../..', import.meta.url))
const INSTALLER = join(ROOT, 'installer', 'index.mjs')
const MANIFEST = JSON.parse(readFileSync(join(ROOT, 'compatibility', 'dsh-0.1.5-rc.2', 'manifest.json'), 'utf8'))
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

function compatibleTemporaryRepository() {
  const root = temporaryRepository()
  for (const file of MANIFEST.hostFiles) {
    const destination = join(root, file.path)
    mkdirSync(resolve(destination, '..'), { recursive: true })
    copyFileSync(join(ROOT, 'compatibility', 'dsh-0.1.5-rc.2', 'patchset', 'before', file.path), destination)
  }
  execFileSync('git', ['add', '.'], { cwd: root })
  execFileSync('git', ['commit', '--quiet', '-m', 'compatible fixture'], { cwd: root })
  return root
}

describe('GAT installer CLI', () => {
  it('rejects an unknown operation without touching a target', () => {
    const result = spawnSync(process.execPath, [INSTALLER, 'unknown'], { encoding: 'utf8' })
    assert.equal(result.status, 2)
    assert.match(result.stderr, /unknown or missing operation/u)
  })

  it('reports an unverified DSH commit without failing status', () => {
    const target = temporaryRepository()
    const result = spawnSync(process.execPath, [INSTALLER, 'status', '--target', target], { encoding: 'utf8' })
    assert.equal(result.status, 0, result.stderr)
    assert.equal(JSON.parse(result.stdout).dsh.compatibility, 'UNVERIFIED')
  })

  it('blocks an unverified DSH dry-run unless explicitly overridden', () => {
    const target = temporaryRepository()
    const result = spawnSync(process.execPath, [INSTALLER, 'dry-run', '--target', target], { encoding: 'utf8' })
    assert.equal(result.status, 4)
    assert.equal(JSON.parse(result.stdout).status, 'blocked')
    assert.match(result.stdout, /allow-unverified-dsh/u)
  })

  it('allows unrelated dirty target paths only with the explicit override', () => {
    const target = compatibleTemporaryRepository()
    writeFileSync(join(target, 'unrelated.txt'), 'preserve me\n')
    const blocked = spawnSync(process.execPath, [INSTALLER, 'dry-run', '--target', target, '--allow-unverified-dsh'], { encoding: 'utf8' })
    assert.equal(blocked.status, 1)
    assert.match(blocked.stderr, /target worktree is not pristine/u)
    const allowed = spawnSync(process.execPath, [INSTALLER, 'dry-run', '--target', target, '--allow-unverified-dsh', '--allow-dirty-target'], { encoding: 'utf8' })
    assert.equal(allowed.status, 0, allowed.stderr)
    assert.equal(JSON.parse(allowed.stdout).status, 'ready')
    assert.equal(readFileSync(join(target, 'unrelated.txt'), 'utf8'), 'preserve me\n')
  })

  it('never allows a dirty host preimage even with the dirty-target override', () => {
    const target = compatibleTemporaryRepository()
    writeFileSync(join(target, MANIFEST.hostFiles[0].path), 'changed\n')
    const result = spawnSync(process.execPath, [INSTALLER, 'dry-run', '--target', target, '--allow-unverified-dsh', '--allow-dirty-target'], { encoding: 'utf8' })
    assert.equal(result.status, 1)
    assert.match(result.stderr, /dirty target paths overlap installer-owned paths/u)
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
