import { defineConfig } from 'vitest/config'
import tsconfigPaths from 'vite-tsconfig-paths'
import { resolve } from 'node:path'
import { standardDecoratorPlugin, vitestExecArgv } from './vitest.shared.ts'

export default defineConfig({
  plugins: [tsconfigPaths({ projects: ['./tsconfig.base.json'] }), standardDecoratorPlugin()],
  cacheDir: './.qualification-cache',
  resolve: {
    extensions: ['.ts', '.tsx', '.mts', '.js', '.json'],
    alias: [
      { find: /^@vuhoi\/gat-core$/, replacement: resolve('packages/experimental/gat-core/src/index.ts') },
      { find: /^@deepseek-ai\/cordis$/, replacement: resolve('vendor/cordis/src/index.ts') },
      { find: /^@deepseek-ai\/dsh-durable-agent$/, replacement: resolve('vendor/gat-qualification-wk/lib/src/index.js') },
    ],
  },
  test: {
    pool: 'forks', execArgv: vitestExecArgv,
    include: [
      'packages/experimental/gat-core/tests/durable-binding-qualification.spec.ts',
      'packages/core/agent-loop/tests/system-prompt-admission.spec.ts',
      'packages/experimental/gat-core/tests/task-memory-qualification.spec.ts',
      'packages/experimental/gat-core/tests/task-memory-publication-races.spec.ts',
      'packages/experimental/gat-core/tests/task-memory-limits.spec.ts',
      'packages/experimental/gat-core/tests/task-review-qualification.spec.ts',
    ],
    testTimeout: 15000, hookTimeout: 15000,
  },
})
