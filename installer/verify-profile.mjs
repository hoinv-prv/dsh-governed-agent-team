#!/usr/bin/env node

import { existsSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { isAbsolute, join, resolve, sep } from 'node:path'

const PACKAGE_NAMES = ['gat-core', 'gat-tools', 'gat-web', 'gat-profile', 'gat-web-profile']

function usage() {
  console.error('usage: node installer/verify-profile.mjs --target <DSH_WORKTREE> --profile-root <DSH_PROFILE_ROOT>')
  process.exit(2)
}

function parseArguments(argv) {
  let target
  let profileRoot
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === '--target') target = argv[++index]
    else if (argv[index] === '--profile-root') profileRoot = argv[++index]
    else usage()
  }
  if (!target || !profileRoot) usage()
  return { target: realpathSync(resolve(target)), profileRoot: realpathSync(resolve(profileRoot)) }
}

function assertInside(root, candidate, label) {
  const prefix = root.endsWith(sep) ? root : `${root}${sep}`
  if (candidate !== root && !candidate.startsWith(prefix)) throw new Error(`${label} resolves outside selected DSH target: ${candidate}`)
}

function verifyPackage(target, profileRoot, shortName) {
  const packageName = `@vuhoi/${shortName}`
  const linkedPath = join(profileRoot, 'node_modules', '@vuhoi', shortName)
  if (!existsSync(linkedPath)) throw new Error(`${packageName} is missing from profile ${profileRoot}`)
  const resolvedPackage = realpathSync(linkedPath)
  assertInside(join(target, 'packages', 'experimental'), resolvedPackage, packageName)
  const packageJsonPath = join(resolvedPackage, 'package.json')
  if (!existsSync(packageJsonPath)) throw new Error(`${packageName} has no package.json at ${resolvedPackage}`)
  const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'))
  if (packageJson.name !== packageName) throw new Error(`${linkedPath} resolves to unexpected package ${String(packageJson.name)}`)
  if (typeof packageJson.main !== 'string' || packageJson.main.length === 0 || isAbsolute(packageJson.main)) throw new Error(`${packageName} has an invalid main entrypoint`)
  const entrypoint = resolve(resolvedPackage, packageJson.main)
  assertInside(resolvedPackage, entrypoint, `${packageName} main`)
  if (!existsSync(entrypoint) || !statSync(entrypoint).isFile()) throw new Error(`${packageName} entrypoint is missing: ${entrypoint}`)
  return { package: packageName, source: resolvedPackage, entrypoint }
}

try {
  const { target, profileRoot } = parseArguments(process.argv.slice(2))
  const packages = PACKAGE_NAMES.map(name => verifyPackage(target, profileRoot, name))
  console.log(JSON.stringify({ status: 'pass', target, profileRoot, packages }, null, 2))
} catch (error) {
  console.error(`gat-profile-verifier: ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
}
