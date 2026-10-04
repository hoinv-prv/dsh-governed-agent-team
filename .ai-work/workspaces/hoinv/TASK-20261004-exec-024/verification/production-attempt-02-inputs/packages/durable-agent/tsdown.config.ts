import { defineConfig } from 'tsdown'

/** Emit additive entries together so their ownership coordinator is shared. */
export default defineConfig({
  entry: ['lib/types/index.js', 'lib/types/composition.js', 'lib/types/provider.js', 'lib/types/execution-composition.js'],
  outDir: 'lib',
  format: ['esm'],
  platform: 'node',
  target: 'es2024',
  fixedExtension: false,
  dts: false,
  clean: false,
})
