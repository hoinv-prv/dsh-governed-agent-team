#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { chmodSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const REPOSITORY_ROOT = fileURLToPath(new URL('..', import.meta.url))
const DSH_ROOT = resolve(process.argv[2] ?? '/home/hoinv/deepseek-harness')
const BASE_COMMIT = 'c291e7961a515f6d7af9304e7fd1d257929aef26'
const GOLDEN_COMMIT = '12fef7a7e01f6c3ba7ecab0929355659b3370435'
const DSH_VERSION = '0.1.5-rc.2'
const GAT_VERSION = '0.1.0'
const GAT_SOURCE_COMMIT = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: REPOSITORY_ROOT, encoding: 'utf8' }).trim()
const COMPATIBILITY_ID = 'gat-0.1.0-dsh-0.1.5-rc.2-c291e796'
const COMPATIBILITY_ROOT = join(REPOSITORY_ROOT, 'compatibility', 'dsh-0.1.5-rc.2')

const PACKAGE_MAPPINGS = [
  ['core', 'packages/experimental/gat-core'],
  ['tools', 'packages/experimental/gat-tools'],
  ['web', 'packages/experimental/gat-web'],
  ['profile', 'packages/experimental/gat-profile'],
  ['web-profile', 'packages/experimental/gat-web-profile'],
]
const EXTRA_PAYLOAD = [
  ['verification/web/gat-agent-team-panel.e2e.ts', 'apps/web/tests/gat-agent-team-panel.e2e.ts'],
  ['verification/web/gat-agent-team-panel.overlay.yml', 'apps/web/tests/gat-agent-team-panel.overlay.yml'],
  ['verification/web/task.expected.md', 'apps/web/tests/snapshots/gat-agent-team-panel/task.expected.md'],
]

const sha256 = value => createHash('sha256').update(value).digest('hex')
const git = args => execFileSync('git', args, { cwd: DSH_ROOT })
const show = (commit, path) => git(['show', `${commit}:${path}`])

function replaceOnce(text, needle, replacement, label) {
  const first = text.indexOf(needle)
  if (first < 0 || text.indexOf(needle, first + needle.length) >= 0) {
    throw new Error(`${label}: expected exactly one replacement anchor`)
  }
  return text.slice(0, first) + replacement + text.slice(first + needle.length)
}

function transformedHostFile(path, before) {
  if (path === 'packages/core/session/src/known-event-types.ts' || path === 'packages/extensions/tool-cordis/src/api-catalog.ts') {
    return show(GOLDEN_COMMIT, path)
  }
  const text = before.toString('utf8')
  if (path === 'pnpm-lock.yaml') {
    const importerSource = show(GOLDEN_COMMIT, path).toString('utf8')
    const extractImporter = importer => {
      const start = importerSource.indexOf(`  ${importer}:\n`)
      if (start < 0) throw new Error(`${path}: missing importer ${importer}`)
      const remainder = importerSource.slice(start + 3)
      const nextImporterOffset = remainder.search(/\n  \S/u)
      if (nextImporterOffset < 0) throw new Error(`${path}: unterminated importer ${importer}`)
      return importerSource.slice(start, start + 3 + nextImporterOffset)
    }
    const sortDependencySections = block => {
      const lines = block.trimEnd().split('\n')
      for (let index = 0; index < lines.length; index += 1) {
        if (!/^    (?:devD|d)ependencies:$/u.test(lines[index])) continue
        let end = index + 1
        while (end < lines.length && !/^    \S/u.test(lines[end])) end += 1
        const chunks = []
        for (const line of lines.slice(index + 1, end)) {
          if (/^      \S/u.test(line)) chunks.push([line])
          else chunks.at(-1)?.push(line)
        }
        chunks.sort((left, right) => left[0] < right[0] ? -1 : left[0] > right[0] ? 1 : 0)
        lines.splice(index + 1, end - index - 1, ...chunks.flat())
      }
      return lines.join('\n')
    }
    const mappings = [
      ['packages/experimental/agent-team', 'packages/experimental/gat-core'],
      ['packages/experimental/agent-team-profile', 'packages/experimental/gat-profile'],
      ['packages/experimental/tool-agent-team', 'packages/experimental/gat-tools'],
      ['packages/experimental/client-ui-agent-team', 'packages/experimental/gat-web'],
      ['packages/experimental/agent-team-web-profile', 'packages/experimental/gat-web-profile'],
    ]
    const blocks = mappings.map(([source, destination]) => {
      let block = extractImporter(source).replace(`  ${source}:`, `  ${destination}:`)
      block = block
        .replaceAll('@deepseek-ai/dsh-experimental-agent-team', '@vuhoi/gat-core')
        .replaceAll('@deepseek-ai/dsh-experimental-tool-agent-team', '@vuhoi/gat-tools')
        .replaceAll('@deepseek-ai/dsh-experimental-client-ui-agent-team', '@vuhoi/gat-web')
        .replaceAll('link:../agent-team', 'link:../gat-core')
        .replaceAll('link:../tool-agent-team', 'link:../gat-tools')
        .replaceAll('link:../client-ui-agent-team', 'link:../gat-web')
      if (destination === 'packages/experimental/gat-web') {
        block = block
          .replace(
            "      '@deepseek-ai/dsh-client-ui-slots':\n        specifier: workspace:^\n        version: link:../../client/ui-slots\n",
            "      '@deepseek-ai/dsh-client-ui-slots':\n        specifier: workspace:^\n        version: link:../../client/ui-slots\n      '@deepseek-ai/dsh-client-ui-sidebar-right':\n        specifier: workspace:^\n        version: link:../../client/ui-sidebar-right\n",
          )
          .replace(
            "      '@deepseek-ai/dsh-typert-protocol':\n        specifier: workspace:^\n        version: link:../../typert/protocol\n",
            "      '@deepseek-ai/dsh-typert-protocol':\n        specifier: workspace:^\n        version: link:../../typert/protocol\n      '@deepseek-ai/dsh-util-workspace-path':\n        specifier: workspace:^\n        version: link:../../util/workspace-path\n",
          )
          .replace(
            "      '@deepseek-ai/cordis':\n        specifier: workspace:^\n        version: link:../../../vendor/cordis\n",
            "      '@deepseek-ai/cordis':\n        specifier: workspace:^\n        version: link:../../../vendor/cordis\n      '@deepseek-ai/schemastery':\n        specifier: link:../../../vendor/schemastery\n        version: link:../../../vendor/schemastery\n",
          )
      }
      if (destination === 'packages/experimental/gat-profile') {
        block = block
          .replace("      '@vuhoi/gat-core':\n        specifier: workspace:^", "      '@vuhoi/gat-core':\n        specifier: file:../gat-core")
          .replace("      '@vuhoi/gat-tools':\n        specifier: workspace:^", "      '@vuhoi/gat-tools':\n        specifier: file:../gat-tools")
      }
      if (destination === 'packages/experimental/gat-web-profile') {
        block = block.replace(
          '    dependencies:\n',
          "    dependencies:\n      '@vuhoi/gat-core':\n        specifier: file:../gat-core\n        version: link:../gat-core\n",
        ).replace("      '@vuhoi/gat-web':\n        specifier: workspace:^", "      '@vuhoi/gat-web':\n        specifier: file:../gat-web")
      }
      return sortDependencySections(block)
    })
    const anchor = '  packages/experimental/inspector:'
    return Buffer.from(replaceOnce(text, anchor, `${blocks.join('\n\n')}\n\n${anchor}`, path))
  }
  if (path === 'apps/web/tsconfig.json') {
    const anchor = '    "tests/agent-team-panel.e2e.ts",\n'
    return Buffer.from(replaceOnce(text, anchor, `${anchor}    "tests/gat-agent-team-panel.e2e.ts",\n`, path))
  }
  if (path === 'tsdown.config.ts') {
    const clientWorkspace = "      ? ['vendor/*', 'packages/*/*', 'apps/cli']"
    const hostWorkspace = "      : ['vendor/*', 'packages/*/*', 'apps/cli', 'apps/desktop', 'apps/desktop-host'],"
    const excludes = [
      "'!packages/experimental/agent-team'",
      "'!packages/experimental/agent-team-profile'",
      "'!packages/experimental/agent-team-web-profile'",
      "'!packages/experimental/client-ui-agent-team'",
      "'!packages/experimental/tool-agent-team'",
    ].join(', ')
    const withClient = replaceOnce(text, clientWorkspace, `      ? ['vendor/*', 'packages/*/*', ${excludes}, 'apps/cli']`, `${path} client workspace`)
    return Buffer.from(replaceOnce(withClient, hostWorkspace, `      : ['vendor/*', 'packages/*/*', ${excludes}, 'apps/cli', 'apps/desktop', 'apps/desktop-host'],`, `${path} host workspace`))
  }
  if (path === 'scripts/gen-tool-catalog.ts') {
    let after = text
    const replacements = [
      ['@deepseek-ai/dsh-experimental-agent-team', '@vuhoi/gat-core', 1],
      ['@deepseek-ai/dsh-experimental-tool-agent-team', '@vuhoi/gat-tools', 2],
      ["dir: 'tool-agent-team'", "dir: 'gat-tools'", 1],
      ["source: 'packages/experimental/tool-agent-team/src/index.ts'", "source: 'packages/experimental/gat-tools/src/index.ts'", 1],
    ]
    for (const [needle, replacement, expectedCount] of replacements) {
      const count = after.split(needle).length - 1
      if (count !== expectedCount) throw new Error(`${path}: expected ${expectedCount} occurrences of ${needle}; found ${count}`)
      after = after.replaceAll(needle, replacement)
    }
    return Buffer.from(after)
  }
  if (path === 'tsconfig.base.json') {
    const anchor = '      "@deepseek-ai/dsh-sdk-jsonrpc-server": ["./packages/sdk/server/src"],\n'
    const aliases = [
      '      "@vuhoi/gat-core": ["./packages/experimental/gat-core/src"],',
      '      "@vuhoi/gat-core/invariant": ["./packages/experimental/gat-core/src/invariant.ts"],',
      '      "@vuhoi/gat-tools": ["./packages/experimental/gat-tools/src"],',
      '      "@vuhoi/gat-web": ["./packages/experimental/gat-web/src"],',
      '      "@vuhoi/gat-profile": ["./packages/experimental/gat-profile/src"],',
      '      "@vuhoi/gat-web-profile": ["./packages/experimental/gat-web-profile/src"],',
    ].join('\n') + '\n'
    return Buffer.from(replaceOnce(text, anchor, anchor + aliases, path))
  }
  if (path === 'tsconfig.host.json') {
    const originalRefs = [
      '    { "path": "./packages/experimental/agent-team" },',
      '    { "path": "./packages/experimental/agent-team-profile" },',
      '    { "path": "./packages/experimental/tool-agent-team" },',
      '    { "path": "./packages/experimental/agent-team-web-profile" },',
    ].join('\n') + '\n'
    const gatRefs = [
      '    { "path": "./packages/experimental/gat-core" },',
      '    { "path": "./packages/experimental/gat-profile" },',
      '    { "path": "./packages/experimental/gat-tools" },',
      '    { "path": "./packages/experimental/gat-web-profile" },',
    ].join('\n') + '\n'
    const withRefs = replaceOnce(text, originalRefs, gatRefs, `${path} project references`)
    const testAnchor = '    "apps/web/tests/agent-team-panel.e2e.ts",\n'
    const withTest = replaceOnce(withRefs, testAnchor, `${testAnchor}    "apps/web/tests/gat-agent-team-panel.e2e.ts",\n`, `${path} Web test`)
    const excludeAnchor = '    "scripts/client-bundle-purity.spec.ts"\n'
    const originalExcludes = [
      '    "packages/experimental/agent-team/**",',
      '    "packages/experimental/agent-team-profile/**",',
      '    "packages/experimental/agent-team-web-profile/**",',
      '    "packages/experimental/tool-agent-team/**",',
    ].join('\n') + '\n'
    return Buffer.from(replaceOnce(withTest, excludeAnchor, originalExcludes + excludeAnchor, `${path} original package excludes`))
  }
  if (path === 'tsconfig.client.json') {
    const originalRef = '    { "path": "./packages/experimental/client-ui-agent-team" },\n'
    const gatRef = '    { "path": "./packages/experimental/gat-web" },\n'
    const withRef = replaceOnce(text, originalRef, gatRef, `${path} project reference`)
    const excludeAnchor = '    "packages/client/*/tests/**/*.host.spec.ts"\n'
    const originalExclude = '    "packages/experimental/client-ui-agent-team/**",\n'
    return Buffer.from(replaceOnce(withRef, excludeAnchor, originalExclude + excludeAnchor, `${path} original package exclude`))
  }
  throw new Error(`unsupported host file ${path}`)
}

function insideSource(path) {
  const absolute = resolve(REPOSITORY_ROOT, path)
  const rel = relative(REPOSITORY_ROOT, absolute)
  if (rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) {
    throw new Error(`source path escapes repository: ${path}`)
  }
  return absolute
}

function filesUnder(root) {
  const results = []
  const visit = directory => {
    for (const name of readdirSync(directory).sort()) {
      if (name === 'lib' || name === 'node_modules' || name === 'coverage' || name === '__pycache__') continue
      const absolute = join(directory, name)
      const stats = statSync(absolute)
      if (stats.isDirectory()) visit(absolute)
      else if (stats.isFile()) results.push(absolute)
      else throw new Error(`unsupported payload entry ${absolute}`)
    }
  }
  visit(root)
  return results
}

function writeArtifact(path, content, mode) {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, content)
  chmodSync(path, mode)
}

const actualVersion = JSON.parse(show(BASE_COMMIT, 'package.json').toString('utf8')).version
if (actualVersion !== DSH_VERSION) throw new Error(`base version mismatch: ${actualVersion}`)
execFileSync('git', ['cat-file', '-e', `${GOLDEN_COMMIT}^{commit}`], { cwd: DSH_ROOT })

rmSync(COMPATIBILITY_ROOT, { recursive: true, force: true })

const hostPaths = [
  'apps/web/tsconfig.json',
  'packages/core/session/src/known-event-types.ts',
  'packages/extensions/tool-cordis/src/api-catalog.ts',
  'pnpm-lock.yaml',
  'scripts/gen-tool-catalog.ts',
  'tsdown.config.ts',
  'tsconfig.base.json',
  'tsconfig.host.json',
  'tsconfig.client.json',
]
const hostFiles = hostPaths.map(path => {
  const before = show(BASE_COMMIT, path)
  const after = transformedHostFile(path, before)
  const mode = Number.parseInt(git(['ls-tree', BASE_COMMIT, path]).toString('utf8').slice(0, 6), 8) & 0o777
  writeArtifact(join(COMPATIBILITY_ROOT, 'patchset', 'before', path), before, mode)
  writeArtifact(join(COMPATIBILITY_ROOT, 'patchset', 'after', path), after, mode)
  return {
    path,
    mode: mode.toString(8).padStart(4, '0'),
    beforeSha256: sha256(before),
    afterSha256: sha256(after),
  }
})

const payloadFiles = []
for (const [sourcePackage, destinationRoot] of PACKAGE_MAPPINGS) {
  const sourceRoot = join(REPOSITORY_ROOT, 'packages', sourcePackage)
  for (const absolute of filesUnder(sourceRoot)) {
    const source = relative(REPOSITORY_ROOT, absolute).split(sep).join('/')
    const suffix = relative(sourceRoot, absolute).split(sep).join('/')
    const bytes = readFileSync(absolute)
    const mode = statSync(absolute).mode & 0o777
    payloadFiles.push({
      source,
      destination: `${destinationRoot}/${suffix}`,
      mode: mode.toString(8).padStart(4, '0'),
      sha256: sha256(bytes),
      bytes: bytes.length,
    })
  }
}
for (const [source, destination] of EXTRA_PAYLOAD) {
  const absolute = insideSource(source)
  const bytes = readFileSync(absolute)
  const mode = statSync(absolute).mode & 0o777
  payloadFiles.push({
    source,
    destination,
    mode: mode.toString(8).padStart(4, '0'),
    sha256: sha256(bytes),
    bytes: bytes.length,
  })
}
payloadFiles.sort((left, right) => left.destination.localeCompare(right.destination))

const patchsetChecksum = sha256(Buffer.from(hostFiles.map(file => `${file.path}\0${file.beforeSha256}\0${file.afterSha256}\n`).join('')))
const payloadChecksum = sha256(Buffer.from(payloadFiles.map(file => `${file.destination}\0${file.mode}\0${file.bytes}\0${file.sha256}\n`).join('')))
const manifest = {
  schemaVersion: 1,
  id: COMPATIBILITY_ID,
  gat: {
    version: GAT_VERSION,
    sourceRepository: '/home/hoinv/work/dsh-governed-agent-team',
    sourceCommit: GAT_SOURCE_COMMIT,
    acceptedGoldenCommit: GOLDEN_COMMIT,
  },
  installer: {
    name: '@vuhoi/governed-agent-team',
    version: GAT_VERSION,
  },
  target: {
    repository: 'deepseek-harness',
    version: DSH_VERSION,
    commit: BASE_COMMIT,
  },
  installationRecord: '.gat/installation.json',
  installedPackages: [
    '@vuhoi/gat-core',
    '@vuhoi/gat-tools',
    '@vuhoi/gat-web',
    '@vuhoi/gat-profile',
    '@vuhoi/gat-web-profile',
  ],
  packageMappings: PACKAGE_MAPPINGS.map(([source, destination]) => ({ source: `packages/${source}`, destination })),
  cleanupDirectories: [
    ...PACKAGE_MAPPINGS.map(([, destination]) => destination),
    'apps/web/tests/snapshots/gat-agent-team-panel',
  ],
  hostFiles,
  payloadFiles,
  patchsetChecksum,
  payloadChecksum,
  allowedPaths: [
    ...PACKAGE_MAPPINGS.map(([, destination]) => `${destination}/`),
    ...EXTRA_PAYLOAD.map(([, destination]) => destination),
    ...hostPaths,
    '.gat/installation.json',
  ],
  commands: {
    dryRun: 'node installer/index.mjs dry-run --target <DSH_WORKTREE>',
    install: 'node installer/index.mjs install --target <DSH_WORKTREE>',
    status: 'node installer/index.mjs status --target <DSH_WORKTREE>',
    rollback: 'node installer/index.mjs rollback --target <DSH_WORKTREE>',
    verify: 'node installer/verify.mjs --target <DSH_WORKTREE>',
  },
}
writeArtifact(join(COMPATIBILITY_ROOT, 'manifest.json'), Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`), 0o644)
const snapshotPath = join(REPOSITORY_ROOT, 'SOURCE_SNAPSHOT.json')
if (existsSync(snapshotPath)) {
  const snapshot = JSON.parse(readFileSync(snapshotPath, 'utf8'))
  snapshot.distribution = {
    ...snapshot.distribution,
    version: GAT_VERSION,
    compatibilityManifest: 'compatibility/dsh-0.1.5-rc.2/manifest.json',
    payloadFiles: payloadFiles.length,
    payloadSha256: payloadChecksum,
    hostFiles: hostFiles.length,
    patchsetSha256: patchsetChecksum,
  }
  writeArtifact(snapshotPath, Buffer.from(`${JSON.stringify(snapshot, null, 2)}\n`), 0o644)
}
console.log(`generated ${relative(REPOSITORY_ROOT, COMPATIBILITY_ROOT)}`)
console.log(`host_files=${hostFiles.length}`)
console.log(`payload_files=${payloadFiles.length}`)
console.log(`patchset_sha256=${patchsetChecksum}`)
console.log(`payload_sha256=${payloadChecksum}`)
