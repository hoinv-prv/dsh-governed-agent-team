import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { mkdirSync, mkdtempSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const ROOT = fileURLToPath(new URL('../..', import.meta.url))
const VERIFIER = join(ROOT, 'installer', 'verify-profile.mjs')
const PACKAGE_NAMES = ['gat-core', 'gat-tools', 'gat-web', 'gat-profile', 'gat-web-profile']

function fixture(originOutsideTarget = false) {
  const root = mkdtempSync(join(tmpdir(), 'gat-profile-test-'))
  const target = join(root, 'dsh')
  const profile = join(root, 'profile')
  const packageBase = originOutsideTarget ? join(root, 'wrong-source') : join(target, 'packages', 'experimental')
  mkdirSync(target, { recursive: true })
  mkdirSync(join(profile, 'node_modules', '@vuhoi'), { recursive: true })
  for (const name of PACKAGE_NAMES) {
    const source = join(packageBase, name)
    mkdirSync(join(source, 'lib'), { recursive: true })
    writeFileSync(join(source, 'package.json'), `${JSON.stringify({ name: `@vuhoi/${name}`, main: 'lib/index.js' })}\n`)
    writeFileSync(join(source, 'lib', 'index.js'), 'export default {}\n')
    symlinkSync(source, join(profile, 'node_modules', '@vuhoi', name), 'dir')
  }
  return { root, target, profile }
}

describe('live profile verifier', () => {
  it('accepts built packages from the selected DSH target', () => {
    const value = fixture()
    try {
      const result = spawnSync(process.execPath, [VERIFIER, '--target', value.target, '--profile-root', value.profile], { encoding: 'utf8' })
      assert.equal(result.status, 0, result.stderr)
      assert.equal(JSON.parse(result.stdout).status, 'pass')
    } finally { rmSync(value.root, { recursive: true, force: true }) }
  })

  it('rejects links to any other checkout', () => {
    const value = fixture(true)
    try {
      const result = spawnSync(process.execPath, [VERIFIER, '--target', value.target, '--profile-root', value.profile], { encoding: 'utf8' })
      assert.equal(result.status, 1)
      assert.match(result.stderr, /outside selected DSH target/u)
    } finally { rmSync(value.root, { recursive: true, force: true }) }
  })
})
