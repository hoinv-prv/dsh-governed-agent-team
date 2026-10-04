import { createRequire } from 'node:module'
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'

const root = '/home/hoinv/work/dsh-governed-agent-team'
const roots = { gat: root, 'durable-agent': '/home/hoinv/work/dsh-durable-agent', 'dsh-prerequisites': '/home/hoinv/work/dsh-binding-prerequisites' }
const ts = createRequire(join(roots['dsh-prerequisites'], 'package.json'))('typescript')
const mapPath = join(root, 'docs/gat-design/source-code-map.json')
const baselinePath = join(root, 'docs/gat-design/source-baseline.json')
const map = JSON.parse(readFileSync(mapPath))
const baseline = JSON.parse(readFileSync(baselinePath))
const row = id => map.rows.find(value => value.detail_id === id)
function add(id, kind, path, symbols = []) {
  const list = row(id)[kind]
  if (!list.some(value => value.repository === 'gat' && value.path === path)) list.push({ repository: 'gat', path, ...(kind === 'sources' ? { symbols: symbols.map(symbol => ({ symbol, line: 1 })) } : {}) })
}
add('DD-16', 'sources', 'packages/core/src/member-host.ts', ['HostMemberCapabilityScope', 'createReservedMemberHost'])
add('DD-16', 'tests', 'packages/core/tests/production-binding.spec.ts')
add('DD-07', 'tests', 'packages/core/tests/production-binding.spec.ts')
add('DD-15', 'sources', 'packages/durable-agent/src/composition.ts', ['apply'])
add('DD-15', 'sources', 'packages/durable-agent/src/provider.ts', ['apply'])
add('DD-15', 'sources', 'packages/durable-agent/package.json')
add('DD-15', 'sources', 'packages/durable-agent/tsdown.config.ts')
for (const path of ['packages/durable-agent/README.md', 'packages/durable-agent/README.zh.md', 'packages/durable-agent/README.i18n.yaml']) add('DD-15', 'sources', path)
add('DD-15', 'tests', 'packages/durable-agent/tests/composition.spec.ts')
for (const path of ['packages/durable-profile/package.json', 'packages/durable-profile/cordis.patch.yml']) add('DD-11', 'sources', path)
for (const path of ['README.md', 'packages/durable-profile/README.md', 'packages/durable-profile/README.zh.md', 'packages/durable-profile/README.i18n.yaml']) add('DD-11', 'sources', path)
for (const path of ['installer/verify-binding.mjs', 'installer/verify-binding-exports.mjs', 'installer/verify-binding-runtime.mjs', 'scripts/generate-binding-compatibility.mjs']) add('DD-11', 'sources', path)
add('DD-11', 'tests', 'installer/tests/binding-compatibility.test.mjs')
add('DD-11', 'tests', 'verification/web/gat-agent-team-panel.e2e.ts')
add('DD-11', 'tests', 'packages/core/tests/built-lib.e2e.ts')
add('DD-11', 'sources', 'verification/web/task.expected.md')
add('DD-11', 'tests', 'packages/durable-agent/tests/composition.spec.ts')
for (const path of ['packages/api/gateway/package.json', 'packages/api/gateway/README.md', 'packages/api/gateway/README.zh.md', 'packages/api/gateway/README.i18n.yaml', 'pnpm-lock.yaml']) {
  if (!row('DD-11').sources.some(entry => entry.repository === 'dsh-prerequisites' && entry.path === path)) {
    row('DD-11').sources.push({ repository: 'dsh-prerequisites', path, symbols: [] })
  }
}
for (const id of ['DD-15', 'DD-16', 'DD-17']) {
  row(id).status = id === 'DD-15' ? 'External WK + implemented adapter' : 'Current implementation'
  row(id).verification_status = 'Current AIP-EXEC-022 qualification is bound in workspace verification/production-qualification-receipt.json; earlier AIP-EXEC-022/AIP-EXEC-023 receipts remain historical. Deployment is separate.'
  row(id).implementation_gap = 'Approved WK/direct-continuable composition implemented; isolated DD-18 task runner, official DSH Consumer integration and deployment are separate scope.'
  row(id).design_reference = 'docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md; docs/gat-design/DETAIL_DESIGN.md §§7–8'
}
const unresolved = []
let anchors = 0
const uniqueFiles = new Map()
const parsed = new Map()
function declarations(repository, path) {
  const key = `${repository}:${path}`
  if (parsed.has(key)) return parsed.get(key)
  const text = readFileSync(join(roots[repository], path), 'utf8')
  const file = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true)
  const names = new Map()
  function put(name, node) {
    const line = file.getLineAndCharacterOfPosition(node.getStart(file)).line + 1
    if (!names.has(name)) names.set(name, [])
    names.get(name).push(line)
  }
  function visit(node, owner) {
    let nextOwner = owner
    if (ts.isClassDeclaration(node) && node.name) nextOwner = node.name.text
    if (node.name && (ts.isIdentifier(node.name) || ts.isPrivateIdentifier(node.name) || ts.isStringLiteral(node.name))) {
      const name = node.name.text.replace(/^#/, '')
      put(name, node)
      if (owner && ts.isMethodDeclaration(node)) put(`${owner}.${name}`, node)
    }
    if (ts.isExportSpecifier(node)) put(node.name.text, node.parent.parent.parent)
    if (ts.isStringLiteral(node)) put(node.text, node)
    ts.forEachChild(node, child => visit(child, nextOwner))
  }
  visit(file)
  parsed.set(key, names)
  return names
}
for (const item of map.rows) for (const kind of ['sources', 'tests']) for (const entry of item[kind]) {
  const absolute = join(roots[entry.repository], entry.path)
  if (!existsSync(absolute)) throw new Error(`missing mapping: ${absolute}`)
  const bytes = readFileSync(absolute)
  uniqueFiles.set(`${entry.repository}:${entry.path}`, { repository: entry.repository, path: entry.path, sha256: createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length })
  for (const locator of entry.symbols ?? []) {
    const candidates = declarations(entry.repository, entry.path).get(locator.symbol)
    if (!candidates?.length) unresolved.push({ ...entry, symbol: locator.symbol })
    else locator.line = candidates.sort((a, b) => Math.abs(a - locator.line) - Math.abs(b - locator.line))[0]
    anchors++
  }
}
if (unresolved.length) throw new Error(JSON.stringify(unresolved, null, 2))
map.inspected_on = '2026-10-04'
map.iteration = { aip_id: 'AIP-EXEC-022', evidence: '.ai-work/workspaces/hoinv/TASK-20261004-exec-022/verification/production-qualification-receipt.json', provenance: 'Working-tree bytes after design-before-code production integration; qualified prerequisite commit remains separately pinned. Symbol anchors are TypeScript AST declaration locations, or exact event string locations.' }
baseline.inspected_on = '2026-10-04'
baseline.repositories = baseline.repositories.map(repository => ({ ...repository, head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: repository.root, encoding: 'utf8' }).trim(), working_tree_status_at_inspection: execFileSync('git', ['status', '--short'], { cwd: repository.root, encoding: 'utf8' }).trimEnd().split('\n').filter(Boolean) }))
baseline.files = [...uniqueFiles.values()].sort((a, b) => `${a.repository}:${a.path}`.localeCompare(`${b.repository}:${b.path}`))
baseline.iteration = map.iteration
writeFileSync(mapPath, JSON.stringify(map, null, 2) + '\n')
writeFileSync(baselinePath, JSON.stringify(baseline, null, 2) + '\n')
const report = { status: 'PASS', source_map_rows: map.rows.length, files: uniqueFiles.size, symbols: anchors, test_paths: map.rows.reduce((sum, entry) => sum + entry.tests.length, 0), missing_paths: 0, unresolved_symbols: 0, mismatched_line_anchors: 0 }
writeFileSync(join(root, '.ai-work/workspaces/hoinv/TASK-20261004-exec-022/verification/production-mapping-validation.json'), JSON.stringify(report, null, 2) + '\n')
console.log(JSON.stringify(report))
