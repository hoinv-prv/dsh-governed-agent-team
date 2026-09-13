#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  chmodSync,
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  renameSync,
  rmdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'

const SOURCE_ROOT = fileURLToPath(new URL('..', import.meta.url))
const MANIFEST_PATH = join(SOURCE_ROOT, 'compatibility', 'dsh-0.1.5-rc.2', 'manifest.json')
const COMPATIBILITY_ROOT = dirname(MANIFEST_PATH)
const sha256 = value => createHash('sha256').update(value).digest('hex')

function usage(message) {
  if (message !== undefined) console.error(`gat-installer: ${message}`)
  console.error('usage: node installer/index.mjs <dry-run|install|status|rollback> --target <DSH_WORKTREE> [--simulate-failure-after <count>]')
  process.exit(2)
}

function parseArguments(argv) {
  const [operation, ...rest] = argv
  if (!['dry-run', 'install', 'status', 'rollback'].includes(operation)) usage('unknown or missing operation')
  let target
  let simulateFailureAfter
  for (let index = 0; index < rest.length; index += 1) {
    const argument = rest[index]
    if (argument === '--target') target = rest[++index]
    else if (argument === '--simulate-failure-after') simulateFailureAfter = Number(rest[++index])
    else usage(`unknown argument ${argument}`)
  }
  if (typeof target !== 'string' || target.length === 0) usage('--target is required')
  if (simulateFailureAfter !== undefined && (!Number.isSafeInteger(simulateFailureAfter) || simulateFailureAfter < 1)) {
    usage('--simulate-failure-after must be a positive safe integer')
  }
  if (simulateFailureAfter !== undefined && operation !== 'install') usage('--simulate-failure-after is valid only with install')
  return { operation, target: resolve(target), simulateFailureAfter }
}

function safeRelative(path, label) {
  if (typeof path !== 'string' || path.length === 0 || isAbsolute(path) || path.split('/').includes('..') || path.includes('\\')) {
    throw new Error(`${label} is not a safe repository-relative POSIX path: ${String(path)}`)
  }
  return path
}

function inside(root, path, label) {
  const candidate = resolve(root, safeRelative(path, label))
  const prefix = root.endsWith(sep) ? root : `${root}${sep}`
  if (candidate !== root && !candidate.startsWith(prefix)) throw new Error(`${label} escapes its repository root`)
  return candidate
}

function rejectSymlinkAncestors(root, destination) {
  const rel = relative(root, destination)
  let current = root
  for (const segment of rel.split(sep)) {
    current = join(current, segment)
    if (!existsSync(current)) continue
    if (lstatSync(current).isSymbolicLink()) throw new Error(`refusing symlink path ${current}`)
  }
}

function git(target, args) {
  return execFileSync('git', args, { cwd: target, encoding: 'utf8' }).trim()
}

function readManifest() {
  const bytes = readFileSync(MANIFEST_PATH)
  const manifest = JSON.parse(bytes.toString('utf8'))
  if (manifest.schemaVersion !== 1) throw new Error(`unsupported manifest schema ${String(manifest.schemaVersion)}`)
  return { manifest, manifestSha256: sha256(bytes) }
}

function patchFilePath(kind, path) {
  return inside(COMPATIBILITY_ROOT, `patchset/${kind}/${path}`, `patchset ${kind} path`)
}

function aggregateHostChecksum(hostFiles) {
  return sha256(Buffer.from(hostFiles.map(file => `${file.path}\0${file.beforeSha256}\0${file.afterSha256}\n`).join('')))
}

function aggregatePayloadChecksum(payloadFiles) {
  return sha256(Buffer.from(payloadFiles.map(file => `${file.destination}\0${file.mode}\0${file.bytes}\0${file.sha256}\n`).join('')))
}

function validateSource(manifest) {
  if (aggregateHostChecksum(manifest.hostFiles) !== manifest.patchsetChecksum) throw new Error('manifest patchset checksum mismatch')
  if (aggregatePayloadChecksum(manifest.payloadFiles) !== manifest.payloadChecksum) throw new Error('manifest payload checksum mismatch')
  for (const file of manifest.hostFiles) {
    safeRelative(file.path, 'host path')
    for (const kind of ['before', 'after']) {
      const source = patchFilePath(kind, file.path)
      rejectSymlinkAncestors(COMPATIBILITY_ROOT, source)
      if (!statSync(source).isFile()) throw new Error(`patchset entry is not a file: ${source}`)
      const expected = kind === 'before' ? file.beforeSha256 : file.afterSha256
      if (sha256(readFileSync(source)) !== expected) throw new Error(`patchset ${kind} hash mismatch for ${file.path}`)
    }
  }
  for (const file of manifest.payloadFiles) {
    const source = inside(SOURCE_ROOT, file.source, 'payload source')
    safeRelative(file.destination, 'payload destination')
    rejectSymlinkAncestors(SOURCE_ROOT, source)
    const stats = statSync(source)
    if (!stats.isFile()) throw new Error(`payload entry is not a file: ${file.source}`)
    const bytes = readFileSync(source)
    if (bytes.length !== file.bytes || sha256(bytes) !== file.sha256) throw new Error(`payload hash mismatch for ${file.source}`)
  }
}

function validateTargetIdentity(target, manifest) {
  if (!existsSync(target) || !statSync(target).isDirectory()) throw new Error(`target is not a directory: ${target}`)
  const top = realpathSync(git(target, ['rev-parse', '--show-toplevel']))
  if (top !== realpathSync(target)) throw new Error(`target must be the DSH worktree root: ${target}`)
  const head = git(target, ['rev-parse', 'HEAD'])
  if (head !== manifest.target.commit) throw new Error(`unsupported DSH commit ${head}; expected ${manifest.target.commit}`)
  const targetPackage = JSON.parse(readFileSync(join(target, 'package.json'), 'utf8'))
  if (targetPackage.version !== manifest.target.version) {
    throw new Error(`unsupported DSH version ${String(targetPackage.version)}; expected ${manifest.target.version}`)
  }
}

function recordPath(target, manifest) {
  return inside(target, manifest.installationRecord, 'installation record path')
}

function validatePristineTarget(target, manifest) {
  const status = git(target, ['status', '--porcelain=v1', '--untracked-files=all'])
  if (status.length > 0) throw new Error(`target worktree is not pristine:\n${status}`)
  for (const file of manifest.hostFiles) {
    const destination = inside(target, file.path, 'host destination')
    rejectSymlinkAncestors(target, destination)
    if (!existsSync(destination) || !statSync(destination).isFile()) throw new Error(`missing host file ${file.path}`)
    if (sha256(readFileSync(destination)) !== file.beforeSha256) throw new Error(`pristine hash mismatch for ${file.path}`)
  }
  for (const mapping of manifest.packageMappings) {
    const destination = inside(target, mapping.destination, 'package destination')
    rejectSymlinkAncestors(target, destination)
    if (existsSync(destination)) throw new Error(`package destination already exists without a valid installation record: ${mapping.destination}`)
  }
  for (const file of manifest.payloadFiles) {
    const destination = inside(target, file.destination, 'payload destination')
    rejectSymlinkAncestors(target, destination)
    if (existsSync(destination)) throw new Error(`payload destination already exists without a valid installation record: ${file.destination}`)
  }
  if (existsSync(recordPath(target, manifest))) throw new Error('installation record already exists but was not accepted')
}

function installedFileRows(manifest) {
  return [
    ...manifest.hostFiles.map(file => ({ path: file.path, sha256: file.afterSha256, kind: 'host' })),
    ...manifest.payloadFiles.map(file => ({ path: file.destination, sha256: file.sha256, kind: 'payload' })),
  ]
}

function readRecord(target, manifest) {
  const path = recordPath(target, manifest)
  if (!existsSync(path)) return undefined
  rejectSymlinkAncestors(target, path)
  return JSON.parse(readFileSync(path, 'utf8'))
}

function validateInstalled(target, manifest, manifestSha256, record) {
  if (record.schemaVersion !== 1 || record.manifestId !== manifest.id || record.manifestSha256 !== manifestSha256) {
    throw new Error('installation record does not match this installer manifest')
  }
  if (record.patchsetChecksum !== manifest.patchsetChecksum || record.payloadChecksum !== manifest.payloadChecksum) {
    throw new Error('installation record checksums do not match this installer')
  }
  if (manifest.gat.sourceCommit !== undefined && (record.gatSourceCommit !== manifest.gat.sourceCommit || JSON.stringify(record.installer) !== JSON.stringify(manifest.installer))) {
    throw new Error('installation record source or installer identity mismatch')
  }
  if (manifest.installedPackages !== undefined && (record.completionState !== 'installed' || JSON.stringify(record.installedPackages) !== JSON.stringify(manifest.installedPackages))) {
    throw new Error('installation record completion or package inventory mismatch')
  }
  const expected = installedFileRows(manifest)
  if (!Array.isArray(record.files) || JSON.stringify(record.files) !== JSON.stringify(expected)) {
    throw new Error('installation record file inventory mismatch')
  }
  if (manifest.installedPackages !== undefined && JSON.stringify(record.changedPaths) !== JSON.stringify(expected.map(file => file.path))) {
    throw new Error('installation record changed-path inventory mismatch')
  }
  for (const file of expected) {
    const destination = inside(target, file.path, 'installed path')
    rejectSymlinkAncestors(target, destination)
    if (!existsSync(destination) || !statSync(destination).isFile()) throw new Error(`installed file missing: ${file.path}`)
    if (sha256(readFileSync(destination)) !== file.sha256) throw new Error(`installed file changed: ${file.path}`)
  }
}

function atomicWrite(destination, bytes, mode) {
  mkdirSync(dirname(destination), { recursive: true })
  const temporary = `${destination}.gat-tmp-${process.pid}`
  writeFileSync(temporary, bytes, { mode })
  chmodSync(temporary, mode)
  renameSync(temporary, destination)
}

function removeInstalledRoots(target, manifest) {
  for (const file of [...manifest.payloadFiles].reverse()) {
    rmSync(inside(target, file.destination, 'payload destination'), { force: true })
  }
  const cleanupDirectories = manifest.cleanupDirectories ?? manifest.packageMappings.map(mapping => mapping.destination)
  for (const directory of [...cleanupDirectories].reverse()) {
    rmSync(inside(target, directory, 'cleanup directory'), { recursive: true, force: true })
  }
  const record = recordPath(target, manifest)
  rmSync(record, { force: true })
  const recordDirectory = dirname(record)
  try {
    rmdirSync(recordDirectory)
  } catch (error) {
    if (error?.code !== 'ENOTEMPTY' && error?.code !== 'ENOENT') throw error
  }
}

function install(target, manifest, manifestSha256, simulateFailureAfter) {
  const existing = readRecord(target, manifest)
  if (existing !== undefined) {
    validateInstalled(target, manifest, manifestSha256, existing)
    console.log(JSON.stringify({ status: 'already-installed', manifestId: manifest.id, target }, null, 2))
    return
  }
  validatePristineTarget(target, manifest)
  if (simulateFailureAfter !== undefined && simulateFailureAfter > manifest.hostFiles.length + manifest.payloadFiles.length) {
    throw new Error(`simulated failure point ${simulateFailureAfter} exceeds the ${manifest.hostFiles.length + manifest.payloadFiles.length} file mutations`)
  }
  const backupRoot = mkdtempSync(join(tmpdir(), 'gat-installer-backup-'))
  let mutationCount = 0
  try {
    for (const file of manifest.hostFiles) {
      const destination = inside(target, file.path, 'host destination')
      const backup = inside(backupRoot, file.path, 'backup path')
      mkdirSync(dirname(backup), { recursive: true })
      copyFileSync(destination, backup)
      chmodSync(backup, Number.parseInt(file.mode, 8))
      atomicWrite(destination, readFileSync(patchFilePath('after', file.path)), Number.parseInt(file.mode, 8))
      mutationCount += 1
      if (mutationCount === simulateFailureAfter) throw new Error(`simulated failure after ${mutationCount} mutations`)
    }
    for (const file of manifest.payloadFiles) {
      const destination = inside(target, file.destination, 'payload destination')
      rejectSymlinkAncestors(target, destination)
      atomicWrite(destination, readFileSync(inside(SOURCE_ROOT, file.source, 'payload source')), Number.parseInt(file.mode, 8))
      mutationCount += 1
      if (mutationCount === simulateFailureAfter) throw new Error(`simulated failure after ${mutationCount} mutations`)
    }
    const record = {
      schemaVersion: 1,
      manifestId: manifest.id,
      manifestSha256,
      gatVersion: manifest.gat.version,
      gatSourceCommit: manifest.gat.sourceCommit,
      installer: manifest.installer,
      installedPackages: manifest.installedPackages,
      completionState: 'installed',
      targetCommit: manifest.target.commit,
      targetVersion: manifest.target.version,
      patchsetChecksum: manifest.patchsetChecksum,
      payloadChecksum: manifest.payloadChecksum,
      changedPaths: installedFileRows(manifest).map(file => file.path),
      files: installedFileRows(manifest),
    }
    atomicWrite(recordPath(target, manifest), Buffer.from(`${JSON.stringify(record, null, 2)}\n`), 0o644)
    console.log(JSON.stringify({ status: 'installed', manifestId: manifest.id, target, files: record.files.length }, null, 2))
  } catch (error) {
    for (const file of [...manifest.hostFiles].reverse()) {
      const backup = inside(backupRoot, file.path, 'backup path')
      if (existsSync(backup)) atomicWrite(inside(target, file.path, 'host destination'), readFileSync(backup), Number.parseInt(file.mode, 8))
    }
    removeInstalledRoots(target, manifest)
    throw error
  } finally {
    rmSync(backupRoot, { recursive: true, force: true })
  }
}

function rollback(target, manifest, manifestSha256) {
  const record = readRecord(target, manifest)
  if (record === undefined) throw new Error('GAT is not installed in this target')
  validateInstalled(target, manifest, manifestSha256, record)
  for (const file of manifest.hostFiles) {
    atomicWrite(
      inside(target, file.path, 'host destination'),
      readFileSync(patchFilePath('before', file.path)),
      Number.parseInt(file.mode, 8),
    )
  }
  removeInstalledRoots(target, manifest)
  console.log(JSON.stringify({ status: 'rolled-back', manifestId: manifest.id, target }, null, 2))
}

function main() {
  const { operation, target, simulateFailureAfter } = parseArguments(process.argv.slice(2))
  const { manifest, manifestSha256 } = readManifest()
  validateSource(manifest)
  validateTargetIdentity(target, manifest)
  if (operation === 'dry-run') {
    const existing = readRecord(target, manifest)
    if (existing !== undefined) validateInstalled(target, manifest, manifestSha256, existing)
    else validatePristineTarget(target, manifest)
    console.log(JSON.stringify({
      status: existing === undefined ? 'ready' : 'already-installed',
      manifestId: manifest.id,
      target,
      hostFiles: manifest.hostFiles.length,
      payloadFiles: manifest.payloadFiles.length,
      allowedPaths: manifest.allowedPaths,
    }, null, 2))
  } else if (operation === 'install') {
    install(target, manifest, manifestSha256, simulateFailureAfter)
  } else if (operation === 'status') {
    const record = readRecord(target, manifest)
    if (record === undefined) console.log(JSON.stringify({ status: 'not-installed', manifestId: manifest.id, target }, null, 2))
    else {
      validateInstalled(target, manifest, manifestSha256, record)
      console.log(JSON.stringify({ status: 'installed', manifestId: manifest.id, target, files: record.files.length }, null, 2))
    }
  } else {
    rollback(target, manifest, manifestSha256)
  }
}

try {
  main()
} catch (error) {
  console.error(`gat-installer: ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
}
