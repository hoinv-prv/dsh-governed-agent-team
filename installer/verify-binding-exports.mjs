#!/usr/bin/env node
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { tmpdir } from 'node:os'

const options = new Map()
for (let i = 2; i < process.argv.length; i += 2) {
  if (!['--target', '--report'].includes(process.argv[i]) || !process.argv[i + 1] || options.has(process.argv[i])) throw new Error('usage: verify-binding-exports.mjs --target <BUILT_INSTALLED_DSH> [--report <json>]')
  options.set(process.argv[i], resolve(process.argv[i + 1]))
}
if (!options.has('--target')) throw new Error('--target is required')
const target = realpathSync(options.get('--target'))
const packages = ['gat-core', 'gat-tools', 'gat-web', 'gat-profile', 'gat-web-profile', 'gat-durable-agent', 'gat-durable-profile'].map(name => `packages/experimental/${name}`).concat('vendor/gat-durable-provider')
const probe = `
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { relative, resolve } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import * as Core from '@vuhoi/gat-core'
import * as Durable from '@vuhoi/gat-durable-agent'
import * as Composition from '@vuhoi/gat-durable-agent/composition'
import * as Provider from '@vuhoi/gat-durable-agent/provider'
import * as Profile from '@vuhoi/gat-durable-profile'
import * as WK from '@deepseek-ai/dsh-durable-agent'
import * as Consumer from '@deepseek-ai/dsh-durable-agent/consumer'
import * as Service from '@deepseek-ai/dsh-durable-agent/service'
const { parse } = createRequire(import.meta.resolve('@vuhoi/gat-durable-agent'))('yaml')
const gatewayUrl = import.meta.resolve('@deepseek-ai/dsh-api-gateway')
const gatewayRequire = createRequire(gatewayUrl)
const coreRequire = createRequire(import.meta.resolve('@vuhoi/gat-core'))
const gatewayPackage = JSON.parse(await readFile(gatewayRequire.resolve('@deepseek-ai/dsh-api-gateway/package.json'), 'utf8'))
assert.equal(gatewayPackage.peerDependencies['@deepseek-ai/dsh-client-connection'], 'workspace:^')
const gatewayCode = await readFile(new URL(gatewayUrl), 'utf8')
const coreCode = await readFile(new URL(import.meta.resolve('@vuhoi/gat-core')), 'utf8')
assert.match(gatewayCode, /import\\s*\\{[^}]*\\bwithControlInvocation\\b[^}]*\\}\\s*from\\s*["']@deepseek-ai\\/dsh-client-connection["']/u)
assert.match(coreCode, /import\\s*\\{[^}]*\\bconsumeHumanControl\\b[^}]*\\}\\s*from\\s*["']@deepseek-ai\\/dsh-client-connection["']/u)
assert.doesNotMatch(gatewayCode, /\\b(?:const|let|var)\\s+admissions\\s*=\\s*new\\s+AsyncLocalStorage/u)
const admissionModule = gatewayRequire.resolve('@deepseek-ai/dsh-client-connection')
assert.equal(admissionModule, coreRequire.resolve('@deepseek-ai/dsh-client-connection'))
const sharedControlContext = { externalPublicGatewayImport: 'PASS', noDuplicateAdmissionStore: 'PASS', exactSharedModuleResolution: 'PASS', gatewayEntrySha256: createHash('sha256').update(gatewayCode).digest('hex'), admissionModuleSha256: createHash('sha256').update(await readFile(admissionModule)).digest('hex') }
const builtEntries = []
for (const specifier of ['@vuhoi/gat-core', '@vuhoi/gat-durable-agent', '@vuhoi/gat-durable-agent/composition', '@vuhoi/gat-durable-agent/provider', '@vuhoi/gat-durable-profile', '@deepseek-ai/dsh-durable-agent', '@deepseek-ai/dsh-durable-agent/consumer', '@deepseek-ai/dsh-durable-agent/service']) {
  const url = import.meta.resolve(specifier)
  const path = fileURLToPath(url)
  assert.ok(path.startsWith(resolve(process.cwd()) + '/'), 'public package entry escaped the selected target: ' + specifier)
  builtEntries.push({ specifier, path: relative(process.cwd(), path), sha256: createHash('sha256').update(await readFile(path)).digest('hex') })
}
assert.equal(typeof Core.default, 'function')
assert.equal(typeof Durable.createDurableAgentBinder, 'function')
assert.equal(typeof Durable.loadDurableTeamMembers, 'function')
assert.equal(typeof Composition.apply, 'function')
assert.equal(typeof Provider.apply, 'function')
assert.equal(WK.DurableAgentConsumer, Consumer.DurableAgentConsumer)
assert.equal(WK.DurableAgentService, Service.DurableAgentService)
const patchPath = import.meta.resolve('@vuhoi/gat-durable-profile/cordis.patch.yml')
const patch = parse(await readFile(new URL(patchPath), 'utf8'))
assert.equal(patch.find(row => row.id === 'tool-agent-team').config.initializer, 'external')
const registrations = patch.flatMap(row => row.insert ?? [])
assert.equal(registrations.filter(row => row.name === '@vuhoi/gat-durable-agent/provider').length, 1)
assert.equal(registrations.filter(row => row.name === '@vuhoi/gat-durable-agent/composition').length, 1)
const config = registrations.find(row => row.name === '@vuhoi/gat-durable-agent/composition').config
assert.equal(config.dedicatedProvider, true)
assert.equal(config.singleHostWorkspace, true)
assert.equal(config.serviceBindingKey, 'gat-wk-durable-v1')
const ctx = new Context()
await ctx.plugin(Provider)
const service = ctx.get('durableAgent')
assert.ok(service instanceof WK.LocalDurableAgentProvider)
assert.equal(service.apiVersion, 1)
assert.equal(service.features.selectiveMemoryRead, true)
assert.equal(service.features.memoryCandidateSubmission, true)
await ctx.fiber.dispose()
assert.equal(ctx.get('durableAgent'), undefined)
console.log(JSON.stringify({ imports: 8, builtEntries, sharedControlContext, publicProviderRegistrationAndDisposal: 'PASS', profilePatchResolution: 'PASS', trustedTopologyAssertions: 'PASS', runtime: 'plain-node', providerRegistrationOnly: true }))
`
const plain = JSON.parse(execFileSync(process.execPath, ['--input-type=module', '--eval', probe], { cwd: target, encoding: 'utf8' }).trim())
const scratch = mkdtempSync(join(tmpdir(), 'gat-binding-packed-'))
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
const packed = []
try {
  for (const directory of packages) {
    const packageRoot = join(target, directory)
    const pkg = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'))
    const result = JSON.parse(execFileSync('npm', ['pack', '--json', '--ignore-scripts', '--pack-destination', scratch], { cwd: packageRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }))[0]
    const archive = join(scratch, result.filename)
    const destination = join(scratch, directory)
    mkdirSync(destination, { recursive: true })
    execFileSync('tar', ['-xf', archive, '--strip-components=1', '-C', destination])
    packed.push({ name: pkg.name, destination, packageRoot, archiveSha256: hash(readFileSync(archive)), files: result.files.length })
  }
  const modules = join(scratch, 'node_modules')
  mkdirSync(modules)
  const link = (source, destination) => { mkdirSync(dirname(destination), { recursive: true }); symlinkSync(source, destination, 'junction') }
  for (const entry of readdirSync(join(target, 'node_modules'))) {
    if (entry.startsWith('.')) continue
    const source = join(target, 'node_modules', entry)
    if (entry.startsWith('@')) {
      for (const name of readdirSync(source)) {
        const dependency = join(source, name)
        if (existsSync(dependency)) link(realpathSync(dependency), join(modules, entry, name))
      }
    } else if (existsSync(source)) link(realpathSync(source), join(modules, entry))
  }
  for (const pkg of packed) {
    const destination = join(modules, pkg.name)
    if (existsSync(destination) || (() => { try { return lstatSync(destination).isSymbolicLink() } catch { return false } })()) rmSync(destination, { force: true })
    link(pkg.destination, destination)
  }
  const packedByName = new Map(packed.map(pkg => [pkg.name, pkg.destination]))
  for (const pkg of packed) {
    const metadata = JSON.parse(readFileSync(join(pkg.packageRoot, 'package.json'), 'utf8'))
    for (const name of Object.keys({ ...metadata.dependencies, ...metadata.peerDependencies })) {
      const source = packedByName.get(name) ?? realpathSync(join(pkg.packageRoot, 'node_modules', name))
      link(source, join(pkg.destination, 'node_modules', name))
    }
  }
  const yaml = join(modules, 'yaml')
  if (existsSync(yaml)) rmSync(yaml, { force: true })
  link(realpathSync(join(target, 'packages/experimental/gat-durable-agent/node_modules/yaml')), yaml)
  const packedProbe = JSON.parse(execFileSync(process.execPath, ['--input-type=module', '--eval', probe], { cwd: scratch, encoding: 'utf8' }).trim())
  const report = { format: 'gat-binding-built-and-packed-exports/1', target, plain, packed: packed.map(({ destination, packageRoot, ...pkg }) => pkg), packedProbe, scope: 'Built and packed public exports, dedicated-provider registration, and opt-in patch resolution with exact target dependency peers; full authorized lifecycle and standalone registry installation are separate.' }
  if (options.has('--report')) { mkdirSync(dirname(options.get('--report')), { recursive: true }); writeFileSync(options.get('--report'), `${JSON.stringify(report, null, 2)}\n`) }
  console.log(JSON.stringify(report, null, 2))
} finally { rmSync(scratch, { recursive: true, force: true }) }
