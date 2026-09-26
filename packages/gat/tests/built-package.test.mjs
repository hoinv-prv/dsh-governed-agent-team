import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const builtEntry = new URL('../lib/index.mjs', import.meta.url).href;

test('built package imports in a clean Node process', () => {
  const base = new URL('../lib/', import.meta.url); const urls = ['governance/index.mjs','memory/index.mjs','policy/index.mjs','adapter/index.mjs','conformance/index.mjs'].map((part) => new URL(part, base).href); const program = `import { PACKAGE_STATUS } from ${JSON.stringify(builtEntry)}; const modules = await Promise.all(${JSON.stringify(urls)}.map((url) => import(url))); process.stdout.write(JSON.stringify({status:PACKAGE_STATUS,exports:modules.map((module) => Object.keys(module).sort())}));`;
  const child = spawnSync(process.execPath, ['--input-type=module', '--eval', program], {
    cwd: new URL('..', import.meta.url),
    encoding: 'utf8',
    env: {},
  });
  assert.equal(child.status, 0, child.stderr);
  assert.equal(child.stderr, '');
  const parsed = JSON.parse(child.stdout); assert.deepEqual(parsed.status, {
    proposalRevision: 3,
    proposalStatus: 'inactive',
    implementationStatus: 'standalone-under-development',
    conformanceStatus: 'not-executed',
    dshRuntimeStatus: 'not-integrated',
    mcpBridgeStatus: 'not-integrated',
  }); assert(parsed.exports.every((names) => names.length > 0)); assert(parsed.exports[2].includes('DenyFirstPolicy')); assert(parsed.exports[3].includes('GatMemoryAdapter')); assert(parsed.exports[4].includes('runConformance'));
});
