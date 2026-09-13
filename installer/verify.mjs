#!/usr/bin/env node

import { execFileSync, spawnSync } from 'node:child_process'
import { existsSync, lstatSync, mkdirSync, readFileSync, readlinkSync, readdirSync, realpathSync, rmdirSync, rmSync, symlinkSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'

const SOURCE_ROOT = fileURLToPath(new URL('..', import.meta.url))
const INSTALLER = join(SOURCE_ROOT, 'installer', 'index.mjs')
const MANIFEST_PATH = join(SOURCE_ROOT, 'compatibility', 'dsh-0.1.5-rc.2', 'manifest.json')
const manifest = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8'))
const PACKAGE_ORIGINS = {
  'gat-core': 'agent-team',
  'gat-tools': 'tool-agent-team',
  'gat-web': 'client-ui-agent-team',
  'gat-profile': 'agent-team-profile',
  'gat-web-profile': 'agent-team-web-profile',
}

function parseTarget(argv) {
  if (argv.length !== 2 || argv[0] !== '--target') {
    console.error('usage: node installer/verify.mjs --target <INSTALLED_DSH_WORKTREE>')
    process.exit(2)
  }
  return resolve(argv[1])
}

function run(command, args, cwd, expected = 0) {
  console.log(`\n$ ${command} ${args.join(' ')}`)
  const result = spawnSync(command, args, { cwd, stdio: 'inherit', env: { ...process.env, DSH_SNAPSHOT: 'replay' } })
  if (result.error !== undefined) throw result.error
  if (result.status !== expected) throw new Error(`${command} exited ${String(result.status)}; expected ${expected}`)
}

function git(target, args, encoding = 'utf8') {
  return execFileSync('git', args, { cwd: target, encoding })
}

function statusPaths(target) {
  const bytes = git(target, ['status', '--porcelain=v1', '-z', '--untracked-files=all'], 'buffer')
  if (bytes.length === 0) return []
  return bytes.toString('utf8').split('\0').filter(Boolean).map(record => {
    const status = record.slice(0, 2)
    if (status.includes('R') || status.includes('C')) throw new Error(`unexpected rename/copy status ${status}`)
    return record.slice(3)
  })
}

function isAllowed(path) {
  return manifest.allowedPaths.some(allowed => allowed.endsWith('/') ? path.startsWith(allowed) : path === allowed)
}

function pathExists(path) {
  try {
    lstatSync(path)
    return true
  } catch (error) {
    if (error?.code === 'ENOENT') return false
    throw error
  }
}

function linkVerificationDependencies(target, sourceCheckout) {
  const createdLinks = []
  const createdDirectories = []
  const ensureDirectory = path => {
    if (pathExists(path)) return
    mkdirSync(path)
    createdDirectories.push(path)
  }
  const cloneLinkTree = (source, destination, linkDirectory = false) => {
    if (!existsSync(source)) return
    const stats = lstatSync(source)
    if (stats.isSymbolicLink()) {
      if (!pathExists(destination)) {
        ensureDirectory(dirname(destination))
        symlinkSync(readlinkSync(source), destination)
        createdLinks.push(destination)
      }
      return
    }
    if (!stats.isDirectory() || linkDirectory) {
      if (!pathExists(destination)) {
        ensureDirectory(dirname(destination))
        symlinkSync(source, destination, stats.isDirectory() ? 'junction' : 'file')
        createdLinks.push(destination)
      }
      return
    }
    ensureDirectory(destination)
    for (const entry of readdirSync(source)) {
      cloneLinkTree(join(source, entry), join(destination, entry), entry === '.pnpm')
    }
  }
  const sourceModules = join(sourceCheckout, 'node_modules')
  if (!existsSync(sourceModules)) throw new Error(`dependency checkout has no node_modules: ${sourceCheckout}`)
  const targetModules = join(target, 'node_modules')
  cloneLinkTree(sourceModules, targetModules)
  ensureDirectory(join(targetModules, '@vuhoi'))
  for (const [targetName, sourceName] of Object.entries(PACKAGE_ORIGINS)) {
    cloneLinkTree(join(target, 'packages', 'experimental', targetName), join(targetModules, '@vuhoi', targetName), true)
    cloneLinkTree(
      join(sourceCheckout, 'packages', 'experimental', sourceName, 'node_modules'),
      join(target, 'packages', 'experimental', targetName, 'node_modules'),
    )
  }
  cloneLinkTree(
    join(sourceCheckout, 'native/system/packages/linux-x64/bin'),
    join(target, 'native/system/packages/linux-x64/bin'),
    true,
  )
  cloneLinkTree(join(sourceCheckout, 'website/node_modules'), join(target, 'website/node_modules'))
  cloneLinkTree(
    realpathSync(join(sourceCheckout, 'apps/web/node_modules/playwright')),
    join(target, 'benchmarks/long-session-browser/node_modules/playwright'),
    true,
  )
  for (const top of ['packages', 'apps', 'vendor', 'native']) {
    const sourceBase = join(sourceCheckout, top)
    const targetBase = join(target, top)
    if (!existsSync(sourceBase) || !existsSync(targetBase)) continue
    const visit = (source, destination, depth) => {
      if (depth === 0) return
      for (const entry of readdirSync(source, { withFileTypes: true })) {
        if (!entry.isDirectory()) continue
        const sourceChild = join(source, entry.name)
        const targetChild = join(destination, entry.name)
        if (!existsSync(targetChild)) continue
        cloneLinkTree(join(sourceChild, 'node_modules'), join(targetChild, 'node_modules'))
        visit(sourceChild, targetChild, depth - 1)
      }
    }
    visit(sourceBase, targetBase, 3)
  }
  return () => {
    for (const path of createdLinks.reverse()) rmSync(path, { force: true })
    for (const path of createdDirectories.reverse()) {
      try {
        rmdirSync(path)
      } catch (error) {
        if (error?.code !== 'ENOTEMPTY' && error?.code !== 'ENOENT') throw error
      }
    }
  }
}

function verifyLifecycle(target) {
  const scratch = join(tmpdir(), `gat-lifecycle-${process.pid}`)
  rmSync(scratch, { recursive: true, force: true })
  try {
    run('git', ['worktree', 'add', '--detach', scratch, manifest.target.commit], target)
    run(process.execPath, [INSTALLER, 'dry-run', '--target', scratch], SOURCE_ROOT)
    run(process.execPath, [INSTALLER, 'install', '--target', scratch, '--simulate-failure-after', '10'], SOURCE_ROOT, 1)
    if (statusPaths(scratch).length !== 0) throw new Error('simulated failure left worktree changes')
    run(process.execPath, [INSTALLER, 'install', '--target', scratch], SOURCE_ROOT)
    run(process.execPath, [INSTALLER, 'install', '--target', scratch], SOURCE_ROOT)
    run(process.execPath, [INSTALLER, 'rollback', '--target', scratch], SOURCE_ROOT)
    if (statusPaths(scratch).length !== 0) throw new Error('rollback left worktree changes')
  } finally {
    try {
      run('git', ['worktree', 'remove', '--force', scratch], target)
    } catch (error) {
      if (existsSync(scratch)) throw error
    }
  }
}

function removeBuildOutputs(target) {
  const visit = directory => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === '.git' || entry.name === 'node_modules') continue
      const path = join(directory, entry.name)
      if (entry.isDirectory() && ['lib', 'dist', '.vite'].includes(entry.name)) {
        rmSync(path, { recursive: true, force: true })
      } else if (entry.isDirectory()) {
        visit(path)
      }
    }
  }
  visit(target)
}

function scanSecrets(target) {
  const patterns = [
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/u,
    /\bsk-[A-Za-z0-9_-]{16,}\b/u,
    /\bghp_[A-Za-z0-9]{20,}\b/u,
    /\bAKIA[0-9A-Z]{16}\b/u,
    /(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?):\/\/[^\s:@/]+:[^\s@/]+@/iu,
  ]
  const findings = []
  for (const file of [...manifest.hostFiles.map(item => item.path), ...manifest.payloadFiles.map(item => item.destination)]) {
    const text = readFileSync(join(target, file), 'utf8')
    if (patterns.some(pattern => pattern.test(text))) findings.push(file)
  }
  if (findings.length > 0) throw new Error(`possible secrets in installed files: ${findings.join(', ')}`)
  return findings.length
}

const target = parseTarget(process.argv.slice(2))
const commonGitDir = realpathSync(resolve(target, git(target, ['rev-parse', '--git-common-dir']).trim()))
const dependencyCheckout = dirname(commonGitDir)
const initialPaths = statusPaths(target)
const outsideAllowlist = initialPaths.filter(path => !isAllowed(path))
if (outsideAllowlist.length > 0) throw new Error(`paths outside manifest allowlist: ${outsideAllowlist.join(', ')}`)

run(process.execPath, [INSTALLER, 'status', '--target', target], SOURCE_ROOT)
run('git', ['diff', '--check'], target)
run(process.execPath, ['--test', 'installer/tests/cli.test.mjs'], SOURCE_ROOT)
verifyLifecycle(target)
const secretFindings = scanSecrets(target)
run('pnpm', ['install', '--frozen-lockfile', '--ignore-scripts', '--lockfile-only', '--offline'], target)

removeBuildOutputs(target)
const unlinkDependencies = linkVerificationDependencies(target, dependencyCheckout)
try {
  run('pnpm', [
    'exec', 'vitest', 'run',
    'packages/experimental/gat-core/tests/invariant.spec.ts',
    'packages/experimental/gat-core/tests/persistence.spec.ts',
    'packages/experimental/gat-core/tests/projection-events.spec.ts',
    'packages/experimental/gat-core/tests/team.spec.ts',
    'packages/experimental/gat-tools/tests/tool-team.spec.ts',
    'packages/experimental/gat-profile/tests/profile.spec.ts',
    'packages/experimental/gat-web-profile/tests/profile.spec.ts',
    'packages/experimental/gat-web/tests/browser-plugin.client.spec.ts',
    'packages/experimental/gat-web/tests/team-action.client.spec.tsx',
  ], target)
  run('pnpm', ['run', 'build'], target)
  run('pnpm', ['exec', 'vitest', 'run', '--config', 'vitest.e2e.config.ts', 'packages/experimental/gat-core/tests/built-lib.e2e.ts'], target)
  run('pnpm', ['exec', 'vitest', 'run', '--config', 'vitest.web.config.ts', 'apps/web/tests/gat-agent-team-panel.e2e.ts'], target)
} finally {
  unlinkDependencies()
}

const finalPaths = statusPaths(target)
const finalOutsideAllowlist = finalPaths.filter(path => !isAllowed(path))
if (finalOutsideAllowlist.length > 0) throw new Error(`verification changed paths outside manifest allowlist: ${finalOutsideAllowlist.join(', ')}`)
run(process.execPath, [INSTALLER, 'status', '--target', target], SOURCE_ROOT)
console.log(JSON.stringify({
  status: 'pass',
  manifestId: manifest.id,
  changedPaths: finalPaths.length,
  pathsOutsideAllowlist: finalOutsideAllowlist,
  secretFindings,
}, null, 2))
