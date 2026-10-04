import { execFileSync, spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'
import { afterEach, test } from 'node:test'
import assert from 'node:assert/strict'

const ROOT = fileURLToPath(new URL('../..', import.meta.url))
const roots = []
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
afterEach(() => { for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true }) })
function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'gat-binding-installer-'))
  roots.push(root)
  const source = join(root, 'source'), target = join(root, 'target')
  const write = (path, text) => { mkdirSync(dirname(path), { recursive: true }); writeFileSync(path, text) }
  mkdirSync(target)
  mkdirSync(join(source, 'installer'), { recursive: true })
  for (const name of ['index.mjs', 'compatibility.mjs']) copyFileSync(join(ROOT, 'installer', name), join(source, 'installer', name))
  copyFileSync(join(ROOT, 'GAT_VERSION.json'), join(source, 'GAT_VERSION.json'))
  write(join(target, 'package.json'), '{"version":"0.1.5-rc.2"}\n')
  const existing = 'packages/experimental/gat-core/src/owner.ts'
  const guard = 'packages/core/agent/src/admission.ts'
  write(join(target, existing), 'qualified before\n')
  write(join(target, guard), 'closed admission\n')
  write(join(target, 'persistent-data/member-v3.json'), '{"attachments":["keep"]}\n')
  execFileSync('git', ['init', '--quiet'], { cwd: target })
  execFileSync('git', ['add', '.'], { cwd: target })
  execFileSync('git', ['-c', 'user.name=GAT Test', '-c', 'user.email=gat@example.invalid', 'commit', '--quiet', '-m', 'qualified host fixture'], { cwd: target })
  const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: target, encoding: 'utf8' }).trim()
  const compatibility = 'dsh-fixture-binding'
  const base = join(source, 'compatibility', compatibility)
  const before = Buffer.from('qualified before\n'), after = Buffer.from('connected after\n')
  write(join(base, 'patchset/before', existing), before)
  write(join(base, 'patchset/after', existing), after)
  write(join(source, 'payload/entry.ts'), 'new binding\n')
  write(join(source, 'payload/addition.ts'), 'new existing-package file\n')
  const hostFiles = [{ path: existing, mode: '0644', beforeSha256: hash(before), afterSha256: hash(after) }]
  const payloadFiles = [
    { source: 'payload/entry.ts', destination: 'packages/experimental/gat-durable-agent/src/index.ts', mode: '0644', sha256: hash(Buffer.from('new binding\n')), bytes: 12 },
    { source: 'payload/addition.ts', destination: 'packages/experimental/gat-core/src/addition.ts', mode: '0644', sha256: hash(Buffer.from('new existing-package file\n')), bytes: 26 },
  ]
  const manifest = {
    schemaVersion: 1, id: 'binding-fixture', selectionPolicy: 'exact-commit-and-hashes', lockfilePrepared: true,
    target: { version: '0.1.5-rc.2', commit }, installer: { name: '@vuhoi/governed-agent-team', version: '0.1.0' },
    installationRecord: '.gat/durable-binding-installation.json', installedPackages: ['@vuhoi/gat-durable-agent'],
    packageMappings: [{ source: 'payload', destination: 'packages/experimental/gat-durable-agent' }],
    cleanupDirectories: ['packages/experimental/gat-durable-agent'],
    prerequisiteFiles: [{ path: existing, sha256: hash(before) }, { path: guard, sha256: hash(Buffer.from('closed admission\n')) }],
    hostFiles, payloadFiles,
    patchsetChecksum: hash(Buffer.from(hostFiles.map(f => `${f.path}\0${f.beforeSha256}\0${f.afterSha256}\n`).join(''))),
    payloadChecksum: hash(Buffer.from(payloadFiles.map(f => `${f.destination}\0${f.mode}\0${f.bytes}\0${f.sha256}\n`).join(''))),
  }
  const manifestPath = join(base, 'manifest.json')
  write(manifestPath, JSON.stringify(manifest))
  return { source, target, existing, guard, manifest, manifestPath, write, run(operation, ...args) { return spawnSync(process.execPath, [join(source, 'installer/index.mjs'), operation, '--target', target, '--compatibility', compatibility, ...args], { encoding: 'utf8' }) } }
}
function success(result) { assert.equal(result.status, 0, result.stderr); return JSON.parse(result.stdout) }

test('selected artifact installs, repeats, reports and rolls back exact host replacements and additions', () => {
  const f = fixture()
  assert.equal(success(f.run('dry-run')).status, 'ready')
  assert.equal(success(f.run('install')).status, 'installed')
  assert.equal(readFileSync(join(f.target, f.existing), 'utf8'), 'connected after\n')
  assert.equal(success(f.run('install')).status, 'already-installed')
  assert.equal(success(f.run('status')).status, 'installed')
  assert.equal(success(f.run('rollback')).status, 'rolled-back')
  assert.equal(readFileSync(join(f.target, f.existing), 'utf8'), 'qualified before\n')
  assert.equal(readFileSync(join(f.target, 'persistent-data/member-v3.json'), 'utf8'), '{"attachments":["keep"]}\n')
  assert.ok(!existsSync(join(f.target, 'packages/experimental/gat-durable-agent')))
  assert.ok(!existsSync(join(f.target, 'packages/experimental/gat-core/src/addition.ts')))
  assert.equal(execFileSync('git', ['status', '--porcelain'], { cwd: f.target, encoding: 'utf8' }), '')
})
test('failed selected installation restores preimages and leaves no payload or record', () => {
  const f = fixture(), result = f.run('install', '--simulate-failure-after', '2')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /simulated failure/)
  assert.equal(execFileSync('git', ['status', '--porcelain'], { cwd: f.target, encoding: 'utf8' }), '')
})
test('selected artifact never permits another commit through old unverified override', () => {
  const f = fixture()
  f.manifest.target.commit = '0'.repeat(40)
  f.write(f.manifestPath, JSON.stringify(f.manifest))
  const result = f.run('install', '--allow-unverified-dsh')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /selected artifact requires DSH commit/)
  assert.equal(execFileSync('git', ['status', '--porcelain'], { cwd: f.target, encoding: 'utf8' }), '')
})
test('selected artifact rejects source payload drift instead of installing current bytes', () => {
  const f = fixture()
  f.write(join(f.source, 'payload/entry.ts'), 'changed\n')
  const result = f.run('install')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /selected frozen payload drift/)
})
test('selected artifact refuses an incomplete dependency mapping', () => {
  const f = fixture()
  f.manifest.lockfilePrepared = false
  f.write(f.manifestPath, JSON.stringify(f.manifest))
  const result = f.run('dry-run')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /requires a generated dependency lockfile/)
})
test('regenerated selected payload cannot silently accept an older installation', () => {
  const f = fixture()
  success(f.run('install'))
  const priorRecord = readFileSync(join(f.target, f.manifest.installationRecord))
  const bytes = Buffer.from('changed binding\n')
  f.write(join(f.source, 'payload/entry.ts'), bytes)
  f.manifest.payloadFiles[0].sha256 = hash(bytes)
  f.manifest.payloadFiles[0].bytes = bytes.length
  f.manifest.payloadChecksum = hash(Buffer.from(f.manifest.payloadFiles.map(row => `${row.destination}\0${row.mode}\0${row.bytes}\0${row.sha256}\n`).join('')))
  f.write(f.manifestPath, JSON.stringify(f.manifest))
  for (const operation of ['install', 'status', 'rollback']) {
    const result = f.run(operation)
    assert.equal(result.status, 1)
    assert.match(result.stderr, /selected installation record payload does not match/)
  }
  assert.equal(readFileSync(join(f.target, f.manifest.payloadFiles[0].destination), 'utf8'), 'new binding\n')
  assert.deepEqual(readFileSync(join(f.target, f.manifest.installationRecord)), priorRecord)
})
test('selected receipt must match exact manifest rows even if its aggregate checksum is retained', () => {
  const f = fixture()
  success(f.run('install'))
  const path = join(f.target, f.manifest.installationRecord)
  const record = JSON.parse(readFileSync(path, 'utf8'))
  record.files.find(row => row.kind === 'payload').sha256 = '0'.repeat(64)
  f.write(path, JSON.stringify(record))
  const result = f.run('status')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /file hashes do not match the exact manifest rows/)
})
test('unmapped prerequisite drift denies even with dirty-target override', () => {
  const f = fixture()
  f.write(join(f.target, f.guard), 'open admission\n')
  const result = f.run('dry-run', '--allow-dirty-target')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /prerequisite hash mismatch/)
})
test('installed prerequisite drift blocks rollback without discarding data', () => {
  const f = fixture()
  success(f.run('install'))
  f.write(join(f.target, f.guard), 'new user work\n')
  const result = f.run('rollback')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /prerequisite hash mismatch/)
  assert.equal(readFileSync(join(f.target, f.guard), 'utf8'), 'new user work\n')
  assert.equal(readFileSync(join(f.target, f.existing), 'utf8'), 'connected after\n')
})
test('selection rejects traversal and a symlinked compatibility directory', () => {
  const f = fixture()
  const traversal = spawnSync(process.execPath, [join(f.source, 'installer/index.mjs'), 'dry-run', '--target', f.target, '--compatibility', '../escape'], { encoding: 'utf8' })
  assert.equal(traversal.status, 2)
  assert.match(traversal.stderr, /safe directory id/)
  const real = join(f.source, 'compatibility/dsh-fixture-binding')
  const moved = join(f.source, 'saved-artifact')
  execFileSync('mv', [real, moved])
  symlinkSync(moved, real, 'dir')
  const result = f.run('dry-run')
  assert.equal(result.status, 1)
  assert.match(result.stderr, /refusing symlink/)
})
