import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { createHash } from 'node:crypto'

export const COMPATIBILITY_STATES = Object.freeze({
  SUPPORTED: 'SUPPORTED',
  UNVERIFIED: 'UNVERIFIED',
  UNSUPPORTED: 'UNSUPPORTED',
})

export function payloadSnapshotMatches(entry, bytes) {
  const actualSha256 = createHash('sha256').update(bytes).digest('hex')
  return { matches: bytes.length === entry.bytes && actualSha256 === entry.sha256, bytes: bytes.length, sha256: actualSha256 }
}

export function readVersionDescriptor(sourceRoot) {
  const path = join(sourceRoot, 'GAT_VERSION.json')
  const descriptor = JSON.parse(readFileSync(path, 'utf8'))
  if (descriptor.schema_version !== 1) throw new Error(`unsupported GAT version descriptor schema ${String(descriptor.schema_version)}`)
  if (descriptor.name !== 'dsh-governed-agent-team') throw new Error(`unexpected GAT version descriptor name ${String(descriptor.name)}`)
  if (typeof descriptor.version !== 'string' || descriptor.version.length === 0) throw new Error('GAT version descriptor has no version')
  if (descriptor.installer?.schema_version !== 1) throw new Error(`unsupported installer schema ${String(descriptor.installer?.schema_version)}`)
  const dsh = descriptor.compatibility?.dsh
  if (dsh?.policy !== 'tested-commits') throw new Error(`unsupported DSH compatibility policy ${String(dsh?.policy)}`)
  if (!Array.isArray(dsh.tested_versions) || !Array.isArray(dsh.tested_commits)) throw new Error('invalid tested DSH compatibility lists')
  if (dsh.unsupported_commits !== undefined && !Array.isArray(dsh.unsupported_commits)) throw new Error('invalid unsupported DSH commit list')
  return descriptor
}

export function inspectDshTarget(target) {
  if (!existsSync(target) || !statSync(target).isDirectory()) throw new Error(`target is not a directory: ${target}`)
  let top
  try {
    top = execFileSync('git', ['rev-parse', '--show-toplevel'], { cwd: target, encoding: 'utf8' }).trim()
  } catch {
    throw new Error(`target is not a Git worktree: ${target}`)
  }
  if (realpathSync(top) !== realpathSync(target)) throw new Error(`target must be the DSH worktree root: ${target}`)
  const packagePath = join(target, 'package.json')
  if (!existsSync(packagePath)) throw new Error(`target has no package.json: ${target}`)
  const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'))
  if (typeof packageJson.version !== 'string' || packageJson.version.length === 0) throw new Error('target package.json has no version')
  const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: target, encoding: 'utf8' }).trim()
  return { commit, version: packageJson.version }
}

export function evaluateDshCompatibility(descriptor, targetInfo) {
  const dsh = descriptor.compatibility.dsh
  if (dsh.unsupported_commits?.includes(targetInfo.commit)) {
    return { state: COMPATIBILITY_STATES.UNSUPPORTED, reason: `DSH commit ${targetInfo.commit} is explicitly unsupported` }
  }
  if (dsh.tested_versions.includes(targetInfo.version) && dsh.tested_commits.includes(targetInfo.commit)) {
    return { state: COMPATIBILITY_STATES.SUPPORTED, reason: `DSH ${targetInfo.version} at ${targetInfo.commit} is tested` }
  }
  return { state: COMPATIBILITY_STATES.UNVERIFIED, reason: `DSH ${targetInfo.version} at ${targetInfo.commit} is not in the tested compatibility set` }
}

export function inspectSource(sourceRoot, descriptor) {
  let commit = null
  let dirty = null
  try {
    commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: sourceRoot, encoding: 'utf8' }).trim()
    dirty = execFileSync('git', ['status', '--porcelain=v1', '--untracked-files=all'], { cwd: sourceRoot, encoding: 'utf8' }).trim().length > 0
  } catch {
    // A packaged release need not retain its Git metadata.
  }
  const expectedCommit = descriptor.source?.commit ?? null
  return { root: realpathSync(sourceRoot), commit, dirty, expectedCommit, commitDiffers: expectedCommit !== null && commit !== expectedCommit }
}
