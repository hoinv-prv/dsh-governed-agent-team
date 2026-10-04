#!/usr/bin/env node
import { execFileSync, spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { cpSync, lstatSync, mkdirSync, readFileSync, readlinkSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('..', import.meta.url))
const compatibility = 'dsh-0.1.5-rc.2-binding-5c02ce9'
const manifestBytes = readFileSync(join(root, 'compatibility', compatibility, 'manifest.json'))
const manifest = JSON.parse(manifestBytes.toString('utf8'))
const isCli = process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url)
const options = new Map()
for (let i = 2; isCli && i < process.argv.length; i += 2) {
  if (!['--host', '--target', '--provider', '--report'].includes(process.argv[i]) || !process.argv[i + 1] || options.has(process.argv[i])) throw new Error('usage: verify-binding.mjs --host <DSH> --target <NEW_SCRATCH_WORKTREE> --provider <WK_REPO> [--report <json>]')
  options.set(process.argv[i], resolve(process.argv[i + 1]))
}
for (const key of isCli ? ['--host', '--target', '--provider'] : []) if (!options.has(key)) throw new Error(`${key} required`)
const host = options.get('--host'), target = options.get('--target'), provider = options.get('--provider')
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
const git = args => execFileSync('git', args, { cwd: target, encoding: 'utf8' })
function run(args, expected = 0) {
  const result = spawnSync(process.execPath, [join(root, 'installer/index.mjs'), ...args, '--target', target, '--compatibility', compatibility], { cwd: root, encoding: 'utf8' })
  if (result.status !== expected) throw new Error(`installer ${args.join(' ')} exited ${result.status}: ${result.stderr}`)
  return expected === 0 ? JSON.parse(result.stdout) : result.stderr
}
function exists(path) { try { lstatSync(path); return true } catch (error) { if (error.code === 'ENOENT') return false; throw error } }
function link(source, destination, exactWorkspace = false) {
  if (exists(destination)) {
    if (!exactWorkspace) return
    let current
    try { current = realpathSync(destination) } catch (error) { if (error.code !== 'ENOENT') throw error }
    if (current === realpathSync(resolve(dirname(destination), source))) return
    if (!lstatSync(destination).isSymbolicLink()) throw new Error(`verification workspace link is a real directory: ${destination}`)
    rmSync(destination)
  }
  mkdirSync(dirname(destination), { recursive: true })
  symlinkSync(source, destination, 'junction')
}
function cloneModules(source, destination) {
  if (!exists(source)) return
  const stats = lstatSync(source)
  if (stats.isSymbolicLink()) {
    if (!exists(destination)) { mkdirSync(dirname(destination), { recursive: true }); symlinkSync(readlinkSync(source), destination) }
  } else if (!stats.isDirectory() || source.endsWith('/.pnpm')) link(source, destination)
  else { mkdirSync(destination, { recursive: true }); for (const entry of readdirSync(source)) cloneModules(join(source, entry), join(destination, entry)) }
}
export function linkBindingVerificationDependencies(hostRoot, targetRoot, providerRoot) {
  cloneModules(join(hostRoot, 'node_modules'), join(targetRoot, 'node_modules'))
  const packageByName = new Map()
  const packageDirectories = []
  const scan = (sourceDirectory, destinationDirectory, depth) => {
    if (!exists(destinationDirectory)) return
    // Some referenced compiler fixtures have local dependency links but no package.json.
    cloneModules(join(sourceDirectory, 'node_modules'), join(destinationDirectory, 'node_modules'))
    if (exists(join(destinationDirectory, 'package.json'))) {
      const pkg = JSON.parse(readFileSync(join(destinationDirectory, 'package.json'), 'utf8'))
      packageByName.set(pkg.name, destinationDirectory)
      packageDirectories.push(destinationDirectory)
      return
    }
    if (depth === 0) return
    for (const entry of readdirSync(destinationDirectory, { withFileTypes: true })) if (entry.isDirectory() && !['node_modules', 'lib', 'dist', '.git'].includes(entry.name)) scan(join(sourceDirectory, entry.name), join(destinationDirectory, entry.name), depth - 1)
  }
  for (const top of ['vendor', 'packages', 'apps', 'native', 'native/system/packages', 'website', 'benchmarks']) scan(join(hostRoot, top), join(targetRoot, top), 4)
  const yaml = realpathSync(join(providerRoot, 'durable-agent-plugin/node_modules/yaml'))
  for (const directory of packageDirectories) {
    const pkg = JSON.parse(readFileSync(join(directory, 'package.json'), 'utf8'))
    const dependencies = { ...pkg.dependencies, ...pkg.optionalDependencies, ...pkg.peerDependencies, ...pkg.devDependencies }
    for (const name of Object.keys(dependencies)) {
      const workspace = packageByName.get(name)
      if (workspace) link(relative(join(directory, 'node_modules', dirname(name)), workspace), join(directory, 'node_modules', name), true)
      else if (name === 'yaml' && dependencies[name] === '2.9.1') link(yaml, join(directory, 'node_modules/yaml'))
      else {
        const dependency = join(hostRoot, 'node_modules', name)
        if (exists(dependency)) link(realpathSync(dependency), join(directory, 'node_modules', name))
      }
    }
  }
  for (const [name, directory] of packageByName) link(relative(join(targetRoot, 'node_modules', dirname(name)), directory), join(targetRoot, 'node_modules', name), true)
  const nativeSource = join(hostRoot, 'native/system/packages/linux-x64/bin')
  const nativeTarget = join(targetRoot, 'native/system/packages/linux-x64/bin')
  if (exists(nativeTarget) && lstatSync(nativeTarget).isSymbolicLink()) {
    if (realpathSync(nativeTarget) !== realpathSync(nativeSource)) throw new Error('unexpected native verification binary link')
    rmSync(nativeTarget)
  }
  // Verification may rebuild this target's host addon without modifying shared binaries.
  if (!exists(nativeTarget)) cpSync(realpathSync(nativeSource), nativeTarget, { recursive: true })
  for (const [name, directory] of packageByName) {
    if (realpathSync(join(targetRoot, 'node_modules', name)) !== realpathSync(directory)) throw new Error(`workspace resolution escaped selected target: ${name}`)
  }
  return { workspacePackages: packageByName.size, exactTargetWorkspaceLinks: 'PASS' }
}
// Creating a target is explicit; no supplied worktree or old compatibility mapping is overwritten.
if (isCli) {
if (exists(target)) throw new Error('verification target must not already exist')
execFileSync('git', ['worktree', 'add', '--detach', target, manifest.target.commit], { cwd: host, stdio: 'inherit' })
try {
  const dryRun = run(['dry-run'])
  run(['install', '--simulate-failure-after', '2'], 1)
  if (git(['status', '--porcelain']).trim() !== '') throw new Error('failed installation left changes')
  const first = run(['install']), second = run(['install']), status = run(['status'])
  const installed = Object.fromEntries([...manifest.hostFiles.map(f => [f.path, f.afterSha256]), ...manifest.payloadFiles.map(f => [f.destination, f.sha256])])
  for (const [path, expected] of Object.entries(installed)) if (hash(readFileSync(join(target, path))) !== expected) throw new Error(`installed hash mismatch: ${path}`)
  run(['rollback'])
  if (git(['status', '--porcelain']).trim() !== '') throw new Error('rollback left changes')
  const final = run(['install'])
  const linkProof = linkBindingVerificationDependencies(host, target, provider)
  const report = { format: 'gat-binding-distribution-verification/1', hostCommit: manifest.target.commit, providerCommit: manifest.externalProvider.repositoryCommit, compatibility, manifestSha256: hash(manifestBytes), prerequisiteFiles: manifest.prerequisiteFiles.length, hostFiles: manifest.hostFiles.length, payloadFiles: manifest.payloadFiles.length, lockfilePrepared: manifest.lockfilePrepared, dryRun: dryRun.status, install: first.status, repeatedInstall: second.status, status: status.status, simulatedFailureRestore: 'PASS', rollbackRestore: 'PASS', finalInstall: final.status, exactInstalledHashes: 'PASS', installedFilesSha256: installed, verificationDependencyLinks: linkProof, target, targetRetainedForBuildAndRuntimeChecks: true }
  if (options.has('--report')) { mkdirSync(dirname(options.get('--report')), { recursive: true }); writeFileSync(options.get('--report'), `${JSON.stringify(report, null, 2)}\n`) }
  console.log(JSON.stringify(report, null, 2))
} catch (error) {
  // Leave a failed target for inspection; never delete user or runtime data on failure.
  console.error(`verification failed; target preserved: ${target}`)
  throw error
}
}
