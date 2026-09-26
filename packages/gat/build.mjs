import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = path.dirname(fileURLToPath(import.meta.url));
const sourceRoot = path.join(packageRoot, 'src');
const outputRoot = path.join(packageRoot, 'lib');

async function copyTree(source, target) {
  await mkdir(target, { recursive: true });
  const entries = await readdir(source, { withFileTypes: true });
  entries.sort((left, right) => left.name.localeCompare(right.name, 'en'));
  for (const entry of entries) {
    const sourcePath = path.join(source, entry.name);
    const targetPath = path.join(target, entry.name);
    if (entry.isDirectory()) await copyTree(sourcePath, targetPath);
    else if (entry.isFile() && entry.name.endsWith('.mjs')) await cp(sourcePath, targetPath);
    else throw new Error(`Unsupported source entry: ${path.relative(packageRoot, sourcePath)}`);
  }
}

await rm(outputRoot, { recursive: true, force: true });
await copyTree(sourceRoot, outputRoot);
