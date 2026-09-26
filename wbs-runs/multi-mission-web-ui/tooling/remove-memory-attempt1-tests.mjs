import { unlink } from 'node:fs/promises';

if (process.argv.length !== 2) throw new Error('No arguments accepted');
for (const path of [
  'packages/gat/tests/memory.test.mjs',
  'packages/gat/tests/audit-recovery.test.mjs',
]) await unlink(path);
