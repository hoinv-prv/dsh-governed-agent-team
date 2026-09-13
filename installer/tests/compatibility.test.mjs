import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { evaluateDshCompatibility, payloadSnapshotMatches, readVersionDescriptor } from '../compatibility.mjs'

const ROOT = fileURLToPath(new URL('../..', import.meta.url))

describe('GAT version and compatibility policy', () => {
  it('loads the repository version descriptor', () => {
    const descriptor = readVersionDescriptor(ROOT)
    assert.equal(descriptor.version, '0.1.0')
    assert.equal(descriptor.compatibility.dsh.policy, 'tested-commits')
  })

  it('distinguishes supported, unverified, and unsupported commits', () => {
    const descriptor = readVersionDescriptor(ROOT)
    const tested = descriptor.compatibility.dsh.tested_commits[0]
    assert.equal(evaluateDshCompatibility(descriptor, { version: '0.1.5-rc.2', commit: tested }).state, 'SUPPORTED')
    assert.equal(evaluateDshCompatibility(descriptor, { version: '0.1.5-rc.2', commit: 'unverified' }).state, 'UNVERIFIED')
    const withUnsupported = structuredClone(descriptor)
    withUnsupported.compatibility.dsh.unsupported_commits = ['bad']
    assert.equal(evaluateDshCompatibility(withUnsupported, { version: '0.1.5-rc.2', commit: 'bad' }).state, 'UNSUPPORTED')
  })

  it('treats a legacy payload hash mismatch as source drift data', () => {
    const comparison = payloadSnapshotMatches({ bytes: 1, sha256: 'legacy' }, Buffer.from('development bytes'))
    assert.equal(comparison.matches, false)
    assert.equal(comparison.bytes, Buffer.byteLength('development bytes'))
    assert.match(comparison.sha256, /^[a-f0-9]{64}$/u)
  })
})
