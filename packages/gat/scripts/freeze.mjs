import { createHash } from 'node:crypto';
import { lstat, readdir, readFile, realpath, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repositoryRoot = path.resolve(packageRoot, '..', '..');
const allowedOutputRoot = path.join(repositoryRoot, 'wbs-runs/multi-mission-web-ui');
const expectedOutput = 'wbs-runs/multi-mission-web-ui/implementation-freeze.json';
const expectedHandoff = 'wbs-runs/multi-mission-web-ui/conformance-handoff.md';
const fixedInputs = [
  'docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md',
  'docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md',
  'docs/conformance/gat-conservative-mvp-v1.json',
];

function parseArgs(argv) {
  const values = new Map();
  for (let index = 0; index < argv.length; index += 2) {
    const option = argv[index];
    const value = argv[index + 1];
    if (!['--output', '--handoff'].includes(option) || !value || values.has(option)) {
      throw new Error('Usage: freeze.mjs --output <path> --handoff <path>');
    }
    values.set(option, value);
  }
  if (values.size !== 2) throw new Error('Both --output and --handoff are required');
  return { output: values.get('--output'), handoff: values.get('--handoff') };
}

let outputRootIdentity;
let realOutputRoot;

async function assertOutputRootIdentity() {
  const current = await lstat(allowedOutputRoot);
  if (!current.isDirectory() || current.isSymbolicLink()) throw new Error('Allowed output root must be a real directory');
  if (current.dev !== outputRootIdentity.dev || current.ino !== outputRootIdentity.ino) {
    throw new Error('Allowed output root identity changed');
  }
  if (await realpath(allowedOutputRoot) !== realOutputRoot) throw new Error('Allowed output root real path changed');
}

async function containedOutput(raw) {
  if (path.isAbsolute(raw)) throw new Error(`Absolute output path denied: ${raw}`);
  const resolved = path.resolve(repositoryRoot, raw);
  const relative = path.relative(allowedOutputRoot, resolved);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error(`Output must be a file below wbs-runs/multi-mission-web-ui: ${raw}`);
  }
  const parent = path.dirname(resolved);
  if (parent !== allowedOutputRoot) {
    throw new Error(`Output must be a direct child of wbs-runs/multi-mission-web-ui: ${raw}`);
  }
  await assertOutputRootIdentity();
  try {
    const existing = await lstat(resolved);
    if (!existing.isFile() || existing.isSymbolicLink() || existing.nlink !== 1) {
      throw new Error(`Existing output target is not a single regular file: ${raw}`);
    }
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  return resolved;
}

async function collectFiles(root, relative = '') {
  const entries = await readdir(path.join(root, relative), { withFileTypes: true });
  entries.sort((left, right) => left.name.localeCompare(right.name, 'en'));
  const files = [];
  for (const entry of entries) {
    if (entry.name === 'node_modules') continue;
    const child = path.join(relative, entry.name);
    if (entry.isDirectory()) files.push(...await collectFiles(root, child));
    else if (entry.isFile()) files.push(child.split(path.sep).join('/'));
    else throw new Error(`Unsupported package entry: ${child}`);
  }
  return files;
}

const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');
const args = parseArgs(process.argv.slice(2));
if (args.output !== expectedOutput || args.handoff !== expectedHandoff) {
  throw new Error(`Exact paths required: --output ${expectedOutput} --handoff ${expectedHandoff}`);
}
outputRootIdentity = await lstat(allowedOutputRoot);
if (!outputRootIdentity.isDirectory() || outputRootIdentity.isSymbolicLink()) {
  throw new Error('Allowed output root must be a real directory');
}
realOutputRoot = await realpath(allowedOutputRoot);
if (realOutputRoot !== allowedOutputRoot) throw new Error('Allowed output root must not be aliased');
const outputPath = await containedOutput(args.output);
const handoffPath = await containedOutput(args.handoff);
if (outputPath === handoffPath) throw new Error('--output and --handoff must differ');

const packageFiles = (await collectFiles(packageRoot)).filter((relative) => !relative.startsWith('lib/') || relative.endsWith('.mjs'));
const paths = [...fixedInputs, ...packageFiles.map((relative) => `packages/gat/${relative}`)].sort();
const files = [];
for (const relative of paths) files.push({ path: relative, sha256: digest(await readFile(path.join(repositoryRoot, relative))) });
const implementationHash = digest(Buffer.from(files.map((entry) => `${entry.path}\0${entry.sha256}\n`).join(''), 'utf8'));
const manifest = {
  format: 'dsh-gat-implementation-freeze/1',
  proposal_status: 'inactive',
  conformance_status: 'not_executed',
  dsh_runtime_status: 'not_integrated',
  mcp_bridge_status: 'not_integrated',
  implementation_sha256: implementationHash,
  files,
};
const evidencePath = `.artifacts/gat-conformance/${implementationHash}/`;
const command = `pnpm --filter @deepseek-ai/dsh-gat test:conformance -- --vectors docs/conformance/gat-conservative-mvp-v1.json --evidence ${evidencePath}`;
const handoff = `# GAT conformance handoff\n\nImplementation SHA-256: \`${implementationHash}\`\n\nRequired evidence path: \`${evidencePath}\`\n\nFuture reviewed command:\n\n\`\`\`sh\n${command}\n\`\`\`\n\nStatus: not executed; DSH runtime not integrated; MCP bridge not integrated; proposal inactive.\n`;
const outputTemp = path.join(allowedOutputRoot, `.gat-freeze-manifest-${process.pid}.tmp`);
const handoffTemp = path.join(allowedOutputRoot, `.gat-freeze-handoff-${process.pid}.tmp`);
if (new Set([outputPath, handoffPath, outputTemp, handoffTemp]).size !== 4) {
  throw new Error('Final and temporary paths must be distinct');
}
await assertOutputRootIdentity();
await writeFile(outputTemp, `${JSON.stringify(manifest, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
await assertOutputRootIdentity();
await writeFile(handoffTemp, handoff, { encoding: 'utf8', flag: 'wx' });
await assertOutputRootIdentity();
await rename(outputTemp, outputPath);
await assertOutputRootIdentity();
await rename(handoffTemp, handoffPath);
process.stdout.write(`${implementationHash}\n`);
