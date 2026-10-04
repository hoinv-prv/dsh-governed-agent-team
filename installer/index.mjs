#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { chmodSync, copyFileSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, renameSync, rmdirSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'
import { COMPATIBILITY_STATES, evaluateDshCompatibility, inspectDshTarget, inspectSource, payloadSnapshotMatches, readVersionDescriptor } from './compatibility.mjs'

const SOURCE_ROOT = fileURLToPath(new URL('..', import.meta.url))
const sha256 = value => createHash('sha256').update(value).digest('hex')

function usage(message) {
  if (message !== undefined) console.error(`gat-installer: ${message}`)
  console.error('usage: node installer/index.mjs <dry-run|install|status|rollback> --target <DSH_WORKTREE> [--compatibility <directory-id>] [--allow-unverified-dsh] [--allow-dirty-target] [--simulate-failure-after <count>]')
  process.exit(2)
}

function parseArguments(argv) {
  const [operation, ...rest] = argv
  if (!['dry-run', 'install', 'status', 'rollback'].includes(operation)) usage('unknown or missing operation')
  let target
  let compatibilityId
  let simulateFailureAfter
  let allowUnverifiedDsh = false
  let allowDirtyTarget = false
  for (let index = 0; index < rest.length; index += 1) {
    const argument = rest[index]
    if (argument === '--target') target = rest[++index]
    else if (argument === '--compatibility') compatibilityId = rest[++index]
    else if (argument === '--simulate-failure-after') simulateFailureAfter = Number(rest[++index])
    else if (argument === '--allow-unverified-dsh') allowUnverifiedDsh = true
    else if (argument === '--allow-dirty-target') allowDirtyTarget = true
    else usage(`unknown argument ${argument}`)
  }
  if (typeof target !== 'string' || target.length === 0) usage('--target is required')
  if (compatibilityId !== undefined && (typeof compatibilityId !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9.+-]*$/u.test(compatibilityId))) usage('--compatibility must be a safe directory id')
  if (simulateFailureAfter !== undefined && (!Number.isSafeInteger(simulateFailureAfter) || simulateFailureAfter < 1)) usage('--simulate-failure-after must be a positive safe integer')
  if (simulateFailureAfter !== undefined && operation !== 'install') usage('--simulate-failure-after is valid only with install')
  if ((allowUnverifiedDsh || allowDirtyTarget) && !['dry-run', 'install'].includes(operation)) usage('override flags are valid only with dry-run or install')
  return { operation, target: resolve(target), compatibilityId, simulateFailureAfter, allowUnverifiedDsh, allowDirtyTarget }
}

function safeRelative(path, label) {
  if (typeof path !== 'string' || path.length === 0 || isAbsolute(path) || path.split('/').includes('..') || path.includes('\\')) throw new Error(`${label} is not a safe repository-relative POSIX path: ${String(path)}`)
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
    if (existsSync(current) && lstatSync(current).isSymbolicLink()) throw new Error(`refusing symlink path ${current}`)
  }
}

const git = (target, args, encoding = 'utf8') => execFileSync('git', args, { cwd: target, encoding })

function readManifest(targetVersion, compatibilityId) {
  if (!/^[0-9A-Za-z.+-]+$/u.test(targetVersion)) throw new Error(`unsafe DSH version ${targetVersion}`)
  const path = join(SOURCE_ROOT, 'compatibility', compatibilityId ?? `dsh-${targetVersion}`, 'manifest.json')
  rejectSymlinkAncestors(SOURCE_ROOT, path)
  if (!existsSync(path)) throw new Error(`no compatibility mapping for DSH version ${targetVersion}`)
  const bytes = readFileSync(path)
  const manifest = JSON.parse(bytes.toString('utf8'))
  if (manifest.schemaVersion !== 1) throw new Error(`unsupported manifest schema ${String(manifest.schemaVersion)}`)
  if (manifest.target?.version !== targetVersion) throw new Error(`compatibility manifest targets ${String(manifest.target?.version)}, not ${targetVersion}`)
  if (compatibilityId !== undefined && (manifest.selectionPolicy !== 'exact-commit-and-hashes' || !/^[a-f0-9]{40}$/u.test(manifest.target?.commit ?? '') || !Array.isArray(manifest.prerequisiteFiles) || manifest.prerequisiteFiles.length === 0)) throw new Error('selected compatibility artifact requires exact commit and prerequisite hashes')
  if (compatibilityId !== undefined && manifest.lockfilePrepared !== true) throw new Error('selected compatibility artifact requires a generated dependency lockfile')
  return { manifest, manifestSha256: sha256(bytes), compatibilityRoot: dirname(path) }
}

const patchFilePath = (root, kind, path) => inside(root, `patchset/${kind}/${path}`, `patchset ${kind} path`)
const aggregateHostChecksum = files => sha256(Buffer.from(files.map(file => `${file.path}\0${file.beforeSha256}\0${file.afterSha256}\n`).join('')))
const aggregatePayloadChecksum = files => sha256(Buffer.from(files.map(file => `${file.destination}\0${file.mode}\0${file.bytes}\0${file.sha256}\n`).join('')))
const mappingChecksum = manifest => sha256(Buffer.from([
  ...manifest.hostFiles.map(file => `host\0${file.path}\0${file.mode}\n`),
  ...manifest.payloadFiles.map(file => `payload\0${file.source}\0${file.destination}\0${file.mode}\n`),
].join('')))

function validateSource(manifest, compatibilityRoot) {
  if (aggregateHostChecksum(manifest.hostFiles) !== manifest.patchsetChecksum) throw new Error('manifest patchset checksum mismatch')
  if (aggregatePayloadChecksum(manifest.payloadFiles) !== manifest.payloadChecksum) throw new Error('manifest payload checksum mismatch')
  for (const file of manifest.hostFiles) {
    safeRelative(file.path, 'host path')
    for (const kind of ['before', 'after']) {
      const source = patchFilePath(compatibilityRoot, kind, file.path)
      rejectSymlinkAncestors(compatibilityRoot, source)
      if (!statSync(source).isFile()) throw new Error(`patchset entry is not a file: ${source}`)
      const expected = kind === 'before' ? file.beforeSha256 : file.afterSha256
      if (sha256(readFileSync(source)) !== expected) throw new Error(`patchset ${kind} hash mismatch for ${file.path}`)
    }
  }
  const actualPayload = []
  const drifted = []
  for (const file of manifest.payloadFiles) {
    const source = inside(SOURCE_ROOT, file.source, 'payload source')
    safeRelative(file.destination, 'payload destination')
    rejectSymlinkAncestors(SOURCE_ROOT, source)
    if (!existsSync(source) || !statSync(source).isFile()) throw new Error(`payload source is missing or not a file: ${file.source}`)
    const bytes = readFileSync(source)
    const comparison = payloadSnapshotMatches(file, bytes)
    const actual = { ...file, sha256: comparison.sha256, bytes: comparison.bytes }
    actualPayload.push(actual)
    if (!comparison.matches) drifted.push(file.source)
  }
  return { actualPayload, drifted }
}

function warnSourceState(sourceInfo, drifted, exactSelectedArtifact = false) {
  if (sourceInfo.dirty) console.error(exactSelectedArtifact
    ? '[WARN] GAT source tree contains local modifications; selected artifact file hashes were verified.'
    : '[WARN] GAT source tree contains local modifications; source hashes are advisory.')
  if (sourceInfo.commitDiffers) console.error(`[WARN] GAT source commit differs from descriptor: expected ${sourceInfo.expectedCommit}, actual ${sourceInfo.commit ?? 'unknown'}.`)
  if (drifted.length > 0) console.error(`[WARN] ${drifted.length} payload file(s) differ from the frozen compatibility snapshot; current bytes will be installed.`)
}

const recordPath = (target, manifest) => inside(target, manifest.installationRecord, 'installation record path')

function dirtyPaths(target) {
  const paths = new Set()
  for (const args of [['diff', '--name-only', '-z'], ['diff', '--cached', '--name-only', '-z'], ['ls-files', '--others', '--exclude-standard', '-z']]) {
    for (const path of git(target, args, 'buffer').toString('utf8').split('\0')) if (path) paths.add(path)
  }
  return [...paths].sort()
}

function controlledPaths(manifest) {
  return [
    ...manifest.hostFiles.map(file => file.path),
    ...manifest.payloadFiles.map(file => file.destination),
    ...(manifest.cleanupDirectories ?? manifest.packageMappings.map(mapping => mapping.destination)).map(path => path.replace(/\/$/u, '')),
    manifest.installationRecord,
  ]
}

const pathsOverlap = (left, right) => left === right || left.startsWith(`${right}/`) || right.startsWith(`${left}/`)

function validateInstallTarget(target, manifest, allowDirtyTarget) {
  const dirty = dirtyPaths(target)
  if (dirty.length > 0 && !allowDirtyTarget) throw new Error(`target worktree is not pristine:\n${dirty.join('\n')}`)
  if (dirty.length > 0) {
    const controlled = controlledPaths(manifest)
    const overlaps = dirty.filter(path => controlled.some(owned => pathsOverlap(path, owned)))
    if (overlaps.length > 0) throw new Error(`dirty target paths overlap installer-owned paths:\n${overlaps.join('\n')}`)
    console.error(`[WARN] Continuing with ${dirty.length} unrelated dirty target path(s) because --allow-dirty-target was supplied.`)
  }
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
  return dirty
}

function validatePrerequisites(target, manifest, installed) {
  if (manifest.selectionPolicy !== 'exact-commit-and-hashes') return
  const replacements = new Map(manifest.hostFiles.map(file => [file.path, file.afterSha256]))
  const seen = new Set()
  for (const file of manifest.prerequisiteFiles) {
    if (seen.has(file.path) || !/^[a-f0-9]{64}$/u.test(file.sha256 ?? '')) throw new Error('invalid prerequisite hash inventory')
    seen.add(file.path)
    const destination = inside(target, file.path, 'prerequisite path')
    rejectSymlinkAncestors(target, destination)
    const expected = installed ? (replacements.get(file.path) ?? file.sha256) : file.sha256
    if (!existsSync(destination) || !statSync(destination).isFile() || sha256(readFileSync(destination)) !== expected) throw new Error(`prerequisite hash mismatch for ${file.path}`)
  }
}

function installedFileRows(manifest, payload = manifest.payloadFiles) {
  return [
    ...manifest.hostFiles.map(file => ({ path: file.path, sha256: file.afterSha256, kind: 'host' })),
    ...payload.map(file => ({ path: file.destination, sha256: file.sha256, bytes: file.bytes, kind: 'payload' })),
  ]
}

function readRecord(target, manifest) {
  const path = recordPath(target, manifest)
  if (!existsSync(path)) return undefined
  rejectSymlinkAncestors(target, path)
  return JSON.parse(readFileSync(path, 'utf8'))
}

function validateInstalled(target, manifest, manifestSha256, record) {
  if (![1, 2].includes(record.schemaVersion) || record.manifestId !== manifest.id) throw new Error('installation record does not match this installer manifest')
  if (record.schemaVersion === 1) {
    if (record.manifestSha256 !== manifestSha256 || record.patchsetChecksum !== manifest.patchsetChecksum || record.payloadChecksum !== manifest.payloadChecksum) throw new Error('legacy installation record checksums do not match this installer')
  } else if (record.mappingChecksum !== mappingChecksum(manifest) || record.patchsetChecksum !== manifest.patchsetChecksum) {
    throw new Error('installation record mapping or patchset does not match this installer')
  }
  if (manifest.selectionPolicy === 'exact-commit-and-hashes') {
    if (record.manifestSha256 !== manifestSha256 || record.payloadChecksum !== manifest.payloadChecksum) throw new Error('selected installation record payload does not match this exact compatibility artifact')
    const rows = installedFileRows(manifest)
    if (!Array.isArray(record.files) || record.files.length !== rows.length || !record.files.every((file, index) => {
      const expected = rows[index]
      return file.path === expected.path && file.kind === expected.kind && file.sha256 === expected.sha256 && file.bytes === expected.bytes
    })) throw new Error('selected installation record file hashes do not match the exact manifest rows')
  }
  const expected = installedFileRows(manifest).map(file => ({ path: file.path, kind: file.kind }))
  const recorded = Array.isArray(record.files) ? record.files.map(file => ({ path: file.path, kind: file.kind })) : []
  if (JSON.stringify(recorded) !== JSON.stringify(expected)) throw new Error('installation record file inventory mismatch')
  if (!Array.isArray(record.changedPaths) || JSON.stringify(record.changedPaths) !== JSON.stringify(record.files.map(file => file.path))) throw new Error('installation record changed-path inventory mismatch')
  for (const file of record.files) {
    const destination = inside(target, file.path, 'installed path')
    rejectSymlinkAncestors(target, destination)
    if (!existsSync(destination) || !statSync(destination).isFile()) throw new Error(`installed file missing: ${file.path}`)
    const bytes = readFileSync(destination)
    if (file.bytes !== undefined && bytes.length !== file.bytes) throw new Error(`installed file size changed: ${file.path}`)
    if (sha256(bytes) !== file.sha256) throw new Error(`installed file changed: ${file.path}`)
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
  for (const file of [...manifest.payloadFiles].reverse()) rmSync(inside(target, file.destination, 'payload destination'), { force: true })
  const directories = manifest.cleanupDirectories ?? manifest.packageMappings.map(mapping => mapping.destination)
  for (const directory of [...directories].reverse()) rmSync(inside(target, directory, 'cleanup directory'), { recursive: true, force: true })
  const record = recordPath(target, manifest)
  rmSync(record, { force: true })
  try { rmdirSync(dirname(record)) } catch (error) { if (error?.code !== 'ENOTEMPTY' && error?.code !== 'ENOENT') throw error }
}

function install(target, targetInfo, compatibility, manifestData, descriptor, sourceInfo, sourceValidation, options) {
  const { manifest, manifestSha256, compatibilityRoot } = manifestData
  const existing = readRecord(target, manifest)
  if (existing !== undefined) {
    validateInstalled(target, manifest, manifestSha256, existing)
    console.log(JSON.stringify({ status: 'already-installed', manifestId: manifest.id, target, compatibility: compatibility.state }, null, 2))
    return
  }
  const dirty = validateInstallTarget(target, manifest, options.allowDirtyTarget)
  const mutationTotal = manifest.hostFiles.length + sourceValidation.actualPayload.length
  if (options.simulateFailureAfter !== undefined && options.simulateFailureAfter > mutationTotal) throw new Error(`simulated failure point ${options.simulateFailureAfter} exceeds the ${mutationTotal} file mutations`)
  const backupRoot = mkdtempSync(join(tmpdir(), 'gat-installer-backup-'))
  let mutationCount = 0
  try {
    for (const file of manifest.hostFiles) {
      const destination = inside(target, file.path, 'host destination')
      const backup = inside(backupRoot, file.path, 'backup path')
      mkdirSync(dirname(backup), { recursive: true })
      copyFileSync(destination, backup)
      chmodSync(backup, Number.parseInt(file.mode, 8))
      atomicWrite(destination, readFileSync(patchFilePath(compatibilityRoot, 'after', file.path)), Number.parseInt(file.mode, 8))
      if (++mutationCount === options.simulateFailureAfter) throw new Error(`simulated failure after ${mutationCount} mutations`)
    }
    for (const file of sourceValidation.actualPayload) {
      const destination = inside(target, file.destination, 'payload destination')
      rejectSymlinkAncestors(target, destination)
      atomicWrite(destination, readFileSync(inside(SOURCE_ROOT, file.source, 'payload source')), Number.parseInt(file.mode, 8))
      if (++mutationCount === options.simulateFailureAfter) throw new Error(`simulated failure after ${mutationCount} mutations`)
    }
    const files = installedFileRows(manifest, sourceValidation.actualPayload)
    const record = {
      schemaVersion: 2,
      manifestId: manifest.id,
      manifestSha256,
      mappingChecksum: mappingChecksum(manifest),
      gatVersion: descriptor.version,
      gatSourceRoot: sourceInfo.root,
      gatSourceCommit: sourceInfo.commit,
      gatSourceDirty: sourceInfo.dirty,
      installer: { name: manifest.installer.name, version: descriptor.version, schemaVersion: descriptor.installer.schema_version },
      installedPackages: manifest.installedPackages,
      completionState: 'installed',
      targetRoot: realpathSync(target),
      targetCommit: targetInfo.commit,
      targetVersion: targetInfo.version,
      compatibility: compatibility.state,
      installedAt: new Date().toISOString(),
      dirtyTargetPathsPreserved: dirty,
      patchsetChecksum: manifest.patchsetChecksum,
      ...(manifest.selectionPolicy === 'exact-commit-and-hashes' ? { payloadChecksum: manifest.payloadChecksum } : {}),
      changedPaths: files.map(file => file.path),
      files,
    }
    atomicWrite(recordPath(target, manifest), Buffer.from(`${JSON.stringify(record, null, 2)}\n`), 0o644)
    validateInstalled(target, manifest, manifestSha256, record)
    console.log(JSON.stringify({ status: 'installed', manifestId: manifest.id, target, compatibility: compatibility.state, files: files.length, structuralVerification: 'PASS' }, null, 2))
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

function rollback(target, manifestData) {
  const { manifest, manifestSha256, compatibilityRoot } = manifestData
  const record = readRecord(target, manifest)
  if (record === undefined) throw new Error('GAT is not installed in this target')
  validateInstalled(target, manifest, manifestSha256, record)
  for (const file of manifest.hostFiles) atomicWrite(inside(target, file.path, 'host destination'), readFileSync(patchFilePath(compatibilityRoot, 'before', file.path)), Number.parseInt(file.mode, 8))
  removeInstalledRoots(target, manifest)
  console.log(JSON.stringify({ status: 'rolled-back', manifestId: manifest.id, target }, null, 2))
}

function compatibilityAllowed(compatibility, override) {
  if (compatibility.state === COMPATIBILITY_STATES.UNSUPPORTED) throw new Error(compatibility.reason)
  if (compatibility.state === COMPATIBILITY_STATES.UNVERIFIED && !override) return false
  if (compatibility.state === COMPATIBILITY_STATES.UNVERIFIED) console.error('[WARN] Continuing because --allow-unverified-dsh was explicitly supplied.')
  return true
}

function main() {
  const options = parseArguments(process.argv.slice(2))
  const descriptor = readVersionDescriptor(SOURCE_ROOT)
  const sourceInfo = inspectSource(SOURCE_ROOT, descriptor)
  const targetInfo = inspectDshTarget(options.target)
  const manifestData = readManifest(targetInfo.version, options.compatibilityId)
  const compatibility = options.compatibilityId === undefined ? evaluateDshCompatibility(descriptor, targetInfo) : {
    state: targetInfo.commit === manifestData.manifest.target.commit ? COMPATIBILITY_STATES.SUPPORTED : COMPATIBILITY_STATES.UNSUPPORTED,
    reason: targetInfo.commit === manifestData.manifest.target.commit ? 'selected exact host compatibility artifact' : `selected artifact requires DSH commit ${manifestData.manifest.target.commit}; actual ${targetInfo.commit}`,
  }
  const sourceValidation = validateSource(manifestData.manifest, manifestData.compatibilityRoot)
  const { manifest, manifestSha256 } = manifestData
  if (options.compatibilityId !== undefined) {
    if (compatibility.state !== COMPATIBILITY_STATES.SUPPORTED) throw new Error(compatibility.reason)
    if (sourceValidation.drifted.length > 0) throw new Error(`selected frozen payload drift: ${sourceValidation.drifted.join(', ')}`)
    validatePrerequisites(options.target, manifest, readRecord(options.target, manifest) !== undefined)
  }
  warnSourceState(sourceInfo, sourceValidation.drifted, options.compatibilityId !== undefined)

  if (options.operation === 'status') {
    const record = readRecord(options.target, manifest)
    if (record !== undefined) validateInstalled(options.target, manifest, manifestSha256, record)
    console.log(JSON.stringify({ status: record === undefined ? 'not-installed' : 'installed', gat: { version: descriptor.version, source: sourceInfo }, dsh: { target: options.target, ...targetInfo, compatibility: compatibility.state, reason: compatibility.reason }, installation: record === undefined ? undefined : { files: record.files.length, structuralVerification: 'PASS', sourceRoot: record.gatSourceRoot } }, null, 2))
    return
  }
  if (options.operation === 'rollback') return rollback(options.target, manifestData)

  const allowed = compatibilityAllowed(compatibility, options.allowUnverifiedDsh)
  if (options.operation === 'dry-run') {
    const record = readRecord(options.target, manifest)
    let dirty = []
    if (record !== undefined) validateInstalled(options.target, manifest, manifestSha256, record)
    else if (allowed) dirty = validateInstallTarget(options.target, manifest, options.allowDirtyTarget)
    console.log(JSON.stringify({ status: allowed ? (record === undefined ? 'ready' : 'already-installed') : 'blocked', reason: allowed ? undefined : `${compatibility.reason}; use --allow-unverified-dsh only if intentional`, gatVersion: descriptor.version, manifestId: manifest.id, target: options.target, targetCommit: targetInfo.commit, compatibility: compatibility.state, sourceDriftFiles: sourceValidation.drifted.length, dirtyTargetPathsPreserved: dirty, hostFiles: manifest.hostFiles.length, payloadFiles: sourceValidation.actualPayload.length, allowedPaths: manifest.allowedPaths }, null, 2))
    if (!allowed) process.exitCode = 4
    return
  }
  if (!allowed) {
    const error = new Error(`${compatibility.reason}; re-run with --allow-unverified-dsh only if intentional`)
    error.exitCode = 4
    throw error
  }
  install(options.target, targetInfo, compatibility, manifestData, descriptor, sourceInfo, sourceValidation, options)
}

try { main() } catch (error) {
  console.error(`gat-installer: ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = error?.exitCode ?? 1
}
