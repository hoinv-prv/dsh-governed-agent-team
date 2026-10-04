import { defineConfig } from 'tsdown'

/** Emit the library, composition and provider as independently importable entries. */
export default defineConfig({
  entry: ['lib/types/index.js', 'lib/types/composition.js', 'lib/types/provider.js'],
  outDir: 'lib',
  format: ['esm'],
  platform: 'node',
  target: 'es2024',
  fixedExtension: false,
  dts: false,
  clean: false,
})
