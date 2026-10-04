/** Assemble the separately qualified direct/execution graphs, then use existing tsdown. */
import { createHash } from 'node:crypto'
import { cp, mkdir, readFile, readdir, realpath, stat, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const options = new Map()
const accepted = ['--direct-host', '--execution-host', '--out', '--tsdown', '--tsc']
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i], value = process.argv[i + 1]
  if (!accepted.includes(key) || !value || options.has(key)) throw new Error('usage: --direct-host <path> --execution-host <path> --out <fresh-path> --tsdown <installed-executable> --tsc <installed-tsc-script>')
  options.set(key, resolve(value))
}
if (accepted.some(key => !options.has(key))) throw new Error('all five arguments are required')
const direct = await realpath(options.get('--direct-host'))
const execution = await realpath(options.get('--execution-host'))
if (direct === execution) throw new Error('qualification Hosts must be distinct')
const output = options.get('--out')
const tsdown = await realpath(options.get('--tsdown'))
const tsc = await realpath(options.get('--tsc'))
try { await stat(output); throw new Error('output already exists') } catch (error) { if (error.code !== 'ENOENT') throw error }
const pkg = 'packages/experimental/gat-durable-agent'
const source = join(root, 'packages/durable-agent')
const pins = new Map([[direct, '5c02ce9f3e44dfce3f87498f65cf684194ad4572'], [execution, 'c1157f7ed448b40c463c1a43fa595b12294fd50d']])
for (const [host, expected] of pins) {
  const result = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: host, encoding: 'utf8' })
  if (result.status !== 0 || result.stdout.trim() !== expected) throw new Error(`Host pin mismatch: ${host}`)
}
const hash = async path => createHash('sha256').update(await readFile(path)).digest('hex')
const inputs = {}
for (const name of await readdir(join(source, 'src'))) {
  if (!name.endsWith('.ts')) continue
  const host = name.startsWith('execution-') ? execution : direct
  const expected = await hash(join(source, 'src', name))
  if (await hash(join(host, pkg, 'src', name)) !== expected) throw new Error(`source mismatch: ${name}`)
  inputs[`src/${name}`] = expected
}
for (const [host, names] of [[direct, ['tsconfig.json']], [execution, ['tsconfig.execution.json', 'tsconfig.execution-conformance.json', 'tests/execution-host-types.ts']]]) {
  for (const name of names) {
    const digest = await hash(join(source, name))
    if (await hash(join(host, pkg, name)) !== digest) throw new Error(`compile input mismatch: ${name}`)
    inputs[name] = digest
  }
}
await mkdir(output, { recursive: true })
const compiles = []
for (const [host, project, label] of [[direct, 'tsconfig.json', 'direct'], [execution, 'tsconfig.execution-conformance.json', 'execution']]) {
  const args = [tsc, '-b', join(host, pkg, project), '--force', '--pretty', 'false']
  const result = spawnSync(process.execPath, args, { cwd: host, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 })
  const log = `assembly-compile-${label}.log`
  await writeFile(join(output, log), (result.stdout ?? '') + (result.stderr ?? ''))
  compiles.push({ command: [process.execPath, ...args], cwd: host, exit_code: result.status, log, log_sha256: await hash(join(output, log)) })
  await writeFile(join(output, 'assembly-compiles.json'), JSON.stringify(compiles, null, 2) + '\n')
  if (result.status !== 0) throw new Error(`${label} compile failed; receipt retained`)
}
for (const name of ['ownership.js', 'tools.js']) {
  const a = await hash(join(direct, pkg, 'lib/types', name))
  const b = await hash(join(execution, pkg, 'lib/types', name))
  if (a !== b) throw new Error(`shared emitted module mismatch: ${name}`)
  inputs[`shared/${name}`] = a
}
await mkdir(join(output, 'lib/types'), { recursive: true })
for (const host of [direct, execution]) {
  const directory = join(host, pkg, 'lib/types')
  for (const name of await readdir(directory)) {
    if (name.startsWith('execution-') !== (host === execution)) continue
    if (!/\.(?:js|d\.ts)(?:\.map)?$/u.test(name)) continue
    const path = join(directory, name)
    if (!(await stat(path)).isFile()) continue
    inputs[`${host === direct ? 'direct' : 'execution'}/${name}`] = await hash(path)
    await cp(path, join(output, 'lib/types', name))
  }
}
for (const name of ['package.json', 'README.md', 'tsdown.config.ts']) {
  inputs[name] = await hash(join(source, name))
  await cp(join(source, name), join(output, name))
}
for (const entry of ['index', 'composition', 'provider', 'execution-composition']) {
  for (const suffix of ['.js', '.d.ts']) await stat(join(output, 'lib/types', entry + suffix))
}
for (const name of await readdir(join(output, 'lib/types'))) {
  if (!name.endsWith('.d.ts')) continue
  const content = await readFile(join(output, 'lib/types', name), 'utf8')
  for (const match of content.matchAll(/(?:from|import)\s*['"](\.\.?\/[^'"]+)['"]/gu)) {
    const target = match[1].replace(/\.(?:js|ts)$/u, '.d.ts')
    await stat(resolve(output, 'lib/types', target))
  }
}
const command = [tsdown, '--config', 'tsdown.config.ts']
const built = spawnSync(command[0], command.slice(1), { cwd: output, stdio: 'inherit' })
const outputs = {}
async function inventory(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) await inventory(path)
    else if (entry.isFile()) outputs[path.slice(output.length + 1)] = await hash(path)
  }
}
await inventory(output)
for (const [name, digest] of Object.entries(inputs)) {
  if (!name.startsWith('src/')) continue
  if (await hash(join(source, name)) !== digest) throw new Error(`source changed during build: ${name}`)
  const host = name.startsWith('src/execution-') ? execution : direct
  if (await hash(join(host, pkg, name)) !== digest) throw new Error(`Host source changed during build: ${name}`)
}
await writeFile(join(output, 'assembly-receipt.json'), JSON.stringify({ direct, execution, host_pins: Object.fromEntries(pins), compiles, command, exit_code: built.status, inputs, outputs }, null, 2) + '\n')
if (built.status !== 0) throw new Error('tsdown failed; partial output and receipt retained for inspection')
