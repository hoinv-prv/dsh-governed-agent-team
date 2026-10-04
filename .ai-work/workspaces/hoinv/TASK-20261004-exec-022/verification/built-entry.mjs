import { strict as assert } from 'node:assert'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'
const root = process.argv[2]
const core = await import(pathToFileURL(resolve(root, 'packages/experimental/gat-core/lib/index.js')).href)
const adapter = await import(pathToFileURL(resolve(root, 'packages/experimental/gat-durable-agent/lib/index.js')).href)
for (const name of ['TeamMemberBinderRegistry', 'prepareMembers', 'provisionPreparedMember', 'recoverBoundMember', 'MemberBindingOwner', 'canonicalJson']) assert.equal(typeof core[name], 'function', name)
for (const name of ['createDurableAgentBinder', 'loadDurableTeamMembers', 'createDurableTools', 'DurableOwnershipCoordinator']) assert.equal(typeof adapter[name], 'function', name)
assert.equal(core.canonicalJson({ z: -0, a: 1 }), '{"a":1,"z":0}')
const tools = adapter.createDurableTools({ readMemory: async () => { throw new Error('invalid arguments must never reach provider') } }, () => {})
assert.deepEqual(tools.map(tool => tool.name), ['durable_agent_read_memory', 'durable_agent_submit_candidate'])
await assert.rejects(tools[0].invoke({ itemId: 'owned', ref: 'forbidden' }), { code: 'TEAM_INVALID_ARGUMENT' })
console.log(JSON.stringify({ status: 'pass', face: 'plain-node-built-exports', coreExports: 6, adapterExports: 4, closedArgumentCheck: true }))
