import { mkdir, readdir, symlink, lstat } from 'node:fs/promises'
import { join, resolve } from 'node:path'

const here = resolve(import.meta.dirname)
const consumerBase = process.env.GAT_ARTIFACT_CONSUMER_BASE
  ? resolve(process.env.GAT_ARTIFACT_CONSUMER_BASE) : join(here, 'consumer')
const graphs = {
  current: '/tmp/gat-exec024-host-c1157f7e',
  direct: '/tmp/gat-exec024-direct-5c02ce9f',
}

async function linkMissing(target, link) {
  try { await lstat(link); return } catch {}
  await symlink(target, link)
}

for (const [name, host] of Object.entries(graphs)) {
  const candidate = join(consumerBase, name, 'package')
  const packageDir = await lstat(candidate).then(() => candidate, () => join(consumerBase, name))
  const modules = join(packageDir, 'node_modules')
  await mkdir(join(modules, '@deepseek-ai'), { recursive: true })
  await mkdir(join(modules, '@vuhoi'), { recursive: true })
  await mkdir(join(modules, '@types'), { recursive: true })
  for (const scope of ['@deepseek-ai', '@vuhoi']) {
    for (const hostScope of [
      join(host, 'node_modules', scope),
      join(host, 'packages/experimental/gat-durable-agent/node_modules', scope),
    ]) {
      for (const entry of await readdir(hostScope).catch(() => [])) {
        await linkMissing(join(hostScope, entry), join(modules, scope, entry))
      }
    }
  }
  const wk = name === 'current'
    ? join(host, 'packages/experimental/gat-durable-agent/node_modules/@deepseek-ai/dsh-durable-agent')
    : join(host, 'node_modules/@deepseek-ai/dsh-durable-agent')
  await linkMissing(wk, join(modules, '@deepseek-ai/dsh-durable-agent'))
  await linkMissing(join(host, 'vendor/cosmokit'), join(modules, '@deepseek-ai/cosmokit'))
  await linkMissing(join(host, 'node_modules/@types/node'), join(modules, '@types/node'))
  await linkMissing(join(host, 'node_modules/yaml'), join(modules, 'yaml'))
  console.log(`${name}: package=${packageDir}; WK=${wk}`)
}
