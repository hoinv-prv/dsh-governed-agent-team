#!/usr/bin/env node
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { chmodSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('..', import.meta.url))
const options = new Map()
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i]
  if (!['--host', '--provider', '--prepared-lockfile'].includes(key) || !process.argv[i + 1] || options.has(key)) throw new Error('usage: generate-binding-compatibility.mjs --host <DSH> --provider <WK_REPO> [--prepared-lockfile <path>]')
  options.set(key, resolve(process.argv[i + 1]))
}
if (!options.has('--host') || !options.has('--provider')) throw new Error('--host and --provider are required')
const host = options.get('--host')
const providerRepo = options.get('--provider')
const hostCommit = '5c02ce9f3e44dfce3f87498f65cf684194ad4572'
const providerCommit = 'a8e215433ae050e36e0ba27205701be1a5f114a1'
const id = 'dsh-0.1.5-rc.2-binding-5c02ce9'
const output = join(root, 'compatibility', id)
const git = (cwd, args) => execFileSync('git', args, { cwd })
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
if (git(host, ['rev-parse', 'HEAD']).toString().trim() !== hostCommit) throw new Error('host must be at the qualified prerequisite commit')
if (git(providerRepo, ['rev-parse', 'HEAD']).toString().trim() !== providerCommit) throw new Error('provider must be at the selected WK revision')
const providerRoot = join(providerRepo, 'durable-agent-plugin')
const providerPackage = JSON.parse(readFileSync(join(providerRoot, 'package.json'), 'utf8'))
if (providerPackage.name !== '@deepseek-ai/dsh-durable-agent' || providerPackage.version !== '0.1.0') throw new Error('unexpected WK package')
const receipt = JSON.parse(readFileSync(join(root, '.ai-work/workspaces/hoinv/TASK-20261004-exec-023/commit-receipt.json'), 'utf8'))
if (receipt.host_commit !== hostCommit || Object.keys(receipt.committed_files_sha256).length !== 244) throw new Error('invalid prerequisite receipt')
const prerequisiteFiles = Object.entries(receipt.committed_files_sha256).map(([path, sha256]) => {
  if (hash(git(host, ['show', `${hostCommit}:${path}`])) !== sha256) throw new Error(`prerequisite receipt mismatch: ${path}`)
  return { path, sha256 }
})
const mappings = ['core', 'tools', 'web', 'profile', 'web-profile', 'durable-agent', 'durable-profile'].map(name => [`packages/${name}`, `packages/experimental/gat-${name}`])
for (const [source] of mappings) if (!existsSync(join(root, source, 'package.json'))) throw new Error(`missing composition package: ${source}`)
if (!existsSync(join(providerRoot, 'lib/src/index.js'))) throw new Error('WK provider must be built before packaging')
function walk(directory) {
  const files = []
  for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (['node_modules', 'lib', 'coverage', '__pycache__', '.vite'].includes(entry.name)) continue
    const path = join(directory, entry.name)
    if (entry.isDirectory()) files.push(...walk(path))
    else if (entry.isFile()) files.push(path)
    else throw new Error(`unsupported source entry ${path}`)
  }
  return files
}
function write(path, bytes, mode = 0o644) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, bytes)
  chmodSync(path, mode)
}
function replace(text, needle, value) {
  if (!text.includes(needle)) throw new Error(`missing metadata anchor: ${needle}`)
  return text.replace(needle, value)
}
const beforePaths = new Set(git(host, ['ls-tree', '-r', '--name-only', hostCommit]).toString().trim().split('\n'))
const planned = []
for (const [source, destination] of mappings) {
  for (const path of walk(join(root, source))) planned.push({ source: relative(root, path), destination: `${destination}/${relative(join(root, source), path)}`, bytes: readFileSync(path), mode: statSync(path).mode & 0o777 })
}
const extras = [
  ['verification/web/gat-agent-team-panel.e2e.ts', 'apps/web/tests/gat-agent-team-panel.e2e.ts'],
  ['verification/web/gat-agent-team-panel.overlay.yml', 'apps/web/tests/gat-agent-team-panel.overlay.yml'],
  ['verification/web/task.expected.md', 'apps/web/tests/snapshots/gat-agent-team-panel/task.expected.md'],
]
for (const [source, destination] of extras) planned.push({ source, destination, bytes: readFileSync(join(root, source)), mode: 0o644 })
const metadata = {}
const capturedHostDeltaPaths = git(host, ['diff', '--name-only', '-z', hostCommit]).toString().split('\0').filter(Boolean).sort()
// The authorized prerequisite worktree had no tracked dirty files at task start.
// Root package sources and generated build metadata below remain authoritative.
const explicitDestinations = new Set(planned.map(file => file.destination))
for (const path of capturedHostDeltaPaths) {
  if (explicitDestinations.has(path)) continue
  const absolute = join(host, path)
  if (!existsSync(absolute) || !statSync(absolute).isFile()) throw new Error(`unsupported removed host delta: ${path}`)
  planned.push({ destination: path, bytes: readFileSync(absolute), mode: statSync(absolute).mode & 0o777 })
}
// DD §8: reviewed host documentation owns links for the installed package layout.
// This exact allowlist cannot override package metadata or runtime source.
const installedDocumentationOverrides = ['core', 'tools'].flatMap(name =>
  ['README.md', 'README.zh.md', 'README.i18n.yaml'].map(file => `packages/experimental/gat-${name}/${file}`))
for (const path of installedDocumentationOverrides) {
  if (!beforePaths.has(path)) throw new Error(`installed documentation must be a tracked prerequisite file: ${path}`)
  const index = planned.findIndex(file => file.destination === path)
  if (index < 0) throw new Error(`missing root documentation mapping: ${path}`)
  const absolute = join(host, path)
  if (!statSync(absolute).isFile()) throw new Error(`invalid installed documentation: ${path}`)
  planned[index] = { destination: path, bytes: readFileSync(absolute), mode: statSync(absolute).mode & 0o777 }
}
const baseConfig = git(host, ['show', `${hostCommit}:tsconfig.base.json`]).toString()
const aliases = [
  '      "@vuhoi/gat-durable-agent": ["./packages/experimental/gat-durable-agent/src"],',
  '      "@vuhoi/gat-durable-agent/composition": ["./packages/experimental/gat-durable-agent/src/composition.ts"],',
  '      "@vuhoi/gat-durable-agent/provider": ["./packages/experimental/gat-durable-agent/src/provider.ts"],',
  '      "@vuhoi/gat-durable-profile": ["./packages/experimental/gat-durable-profile/src"],',
].join('\n')
metadata['tsconfig.base.json'] = replace(baseConfig, '      "@vuhoi/gat-web-profile": ["./packages/experimental/gat-web-profile/src"],', `      "@vuhoi/gat-web-profile": ["./packages/experimental/gat-web-profile/src"],\n${aliases}`)
const hostConfig = git(host, ['show', `${hostCommit}:tsconfig.host.json`]).toString()
metadata['tsconfig.host.json'] = replace(hostConfig, '    { "path": "./packages/experimental/gat-web-profile" },', '    { "path": "./packages/experimental/gat-web-profile" },\n    { "path": "./packages/experimental/gat-durable-agent" },\n    { "path": "./packages/experimental/gat-durable-profile" },')
const tsdown = git(host, ['show', `${hostCommit}:tsdown.config.ts`]).toString()
const excluded = "'!vendor/gat-durable-provider'"
metadata['tsdown.config.ts'] = tsdown.replaceAll("'!packages/experimental/tool-agent-team'", `'!packages/experimental/tool-agent-team', ${excluded}`)
if (options.has('--prepared-lockfile')) metadata['pnpm-lock.yaml'] = readFileSync(options.get('--prepared-lockfile'), 'utf8')
// The old compatibility tree and source snapshot are intentionally not generator outputs.
rmSync(output, { recursive: true, force: true })
const hostFiles = []
const payloadFiles = []
for (const [path, text] of Object.entries(metadata)) {
  const prior = planned.findIndex(file => file.destination === path)
  if (prior >= 0) planned.splice(prior, 1)
  planned.push({ destination: path, bytes: Buffer.from(text), mode: 0o644 })
}
for (const file of planned.sort((a, b) => a.destination.localeCompare(b.destination))) {
  if (beforePaths.has(file.destination)) {
    const before = git(host, ['show', `${hostCommit}:${file.destination}`])
    if (before.equals(file.bytes)) continue
    write(join(output, 'patchset/before', file.destination), before, file.mode)
    write(join(output, 'patchset/after', file.destination), file.bytes, file.mode)
    hostFiles.push({ path: file.destination, mode: file.mode.toString(8).padStart(4, '0'), beforeSha256: hash(before), afterSha256: hash(file.bytes) })
  } else {
    payloadFiles.push({ source: file.source, destination: file.destination, mode: file.mode.toString(8).padStart(4, '0'), sha256: hash(file.bytes), bytes: file.bytes.length })
  }
}
// External runtime bytes are copied into this artifact, never read through a deployed checkout.
const providerFiles = []
function visitProvider(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) visitProvider(path)
    else if (entry.isFile()) providerFiles.push(path)
    else throw new Error(`unsupported provider entry ${path}`)
  }
}
visitProvider(join(providerRoot, 'lib/src'))
visitProvider(join(providerRoot, 'src'))
visitProvider(join(providerRoot, 'docs'))
providerFiles.push(join(providerRoot, 'package.json'), join(providerRoot, 'README.md'))
for (const path of providerFiles) {
  const suffix = relative(providerRoot, path)
  const bytes = readFileSync(path)
  if (!suffix.startsWith('lib/')) {
    const pinned = git(providerRepo, ['show', `${providerCommit}:durable-agent-plugin/${suffix}`])
    if (!pinned.equals(bytes)) throw new Error(`pinned provider source drift: ${suffix}`)
  }
  const source = `compatibility/${id}/payload/provider/${suffix}`
  write(join(root, source), bytes)
  payloadFiles.push({ source, destination: `vendor/gat-durable-provider/${suffix}`, mode: '0644', sha256: hash(bytes), bytes: bytes.length })
}
payloadFiles.sort((a, b) => a.destination.localeCompare(b.destination))
const newMappings = mappings.filter(([, destination]) => !beforePaths.has(`${destination}/package.json`))
newMappings.push([`compatibility/${id}/payload/provider`, 'vendor/gat-durable-provider'])
const manifest = {
  schemaVersion: 1, id: `gat-binding-${hostCommit.slice(0, 8)}`, selectionPolicy: 'exact-commit-and-hashes',
  lockfilePrepared: options.has('--prepared-lockfile'),
  gat: { version: '0.1.0', sourceCommit: git(root, ['rev-parse', 'HEAD']).toString().trim() },
  installer: { name: '@vuhoi/governed-agent-team', version: '0.1.0' },
  target: { repository: 'deepseek-harness', version: '0.1.5-rc.2', commit: hostCommit },
  externalProvider: { repositoryCommit: providerCommit, package: providerPackage.name, version: providerPackage.version, builtLayout: 'lib/src' },
  installationRecord: '.gat/durable-binding-installation.json',
  installedPackages: mappings.map(([source]) => JSON.parse(readFileSync(join(root, source, 'package.json'), 'utf8')).name).concat(providerPackage.name),
  packageMappings: newMappings.map(([source, destination]) => ({ source, destination })),
  cleanupDirectories: newMappings.map(([, destination]) => destination),
  prerequisiteFiles, capturedHostDeltaPaths, installedDocumentationOverrides, hostFiles, payloadFiles,
  patchsetChecksum: hash(Buffer.from(hostFiles.map(file => `${file.path}\0${file.beforeSha256}\0${file.afterSha256}\n`).join(''))),
  payloadChecksum: hash(Buffer.from(payloadFiles.map(file => `${file.destination}\0${file.mode}\0${file.bytes}\0${file.sha256}\n`).join(''))),
  allowedPaths: [...hostFiles.map(file => file.path), ...payloadFiles.map(file => file.destination), '.gat/durable-binding-installation.json'],
}
write(join(output, 'manifest.json'), Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`))
console.log(JSON.stringify({ compatibility: id, hostFiles: hostFiles.length, payloadFiles: payloadFiles.length, prerequisiteFiles: prerequisiteFiles.length, lockfilePrepared: manifest.lockfilePrepared }, null, 2))
