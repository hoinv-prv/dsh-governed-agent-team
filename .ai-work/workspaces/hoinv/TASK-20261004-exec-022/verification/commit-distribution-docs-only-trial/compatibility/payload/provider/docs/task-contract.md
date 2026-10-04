# Shared task contract and completion assessment

The root package exports a compact, versioned task-contract boundary. It lets a host give the worker and an independent reviewer the same task meaning without changing the existing runtime/session DTOs or memory APIs.

## Contract packet

`normalizeTaskContract(input)` validates and freezes a contract. The required shape is:

- `format`: `durable-agent-task-contract/1`;
- `taskId`, positive integer `revision`, and `outcome`;
- `nonGoals`, `authorityLimits`, and `stopConditions` string arrays (authority limits and stop conditions must be non-empty);
- `inputs`: unique `{ id, version, sha256 }` records;
- `outputs`: unique `{ id, description }` records;
- `acceptance`: unique `{ id, requirement, evidenceRequired, outputIds }` records. Every output must be covered by at least one criterion, and criterion output IDs must refer to declared outputs.

Strings, arrays, hashes, object keys, and the total envelope are bounded and checked. `taskContractSha256()` returns the canonical SHA-256 of the normalized contract. The digest binds the normalized contract content, including its revision, not an informal task summary; object-key order does not affect it.

`createTaskPacket(contract, role)` returns the normalized contract, its digest, and role-specific instructions. `role` is `worker` or `reviewer`. The worker instruction requests exact input versions, artifact hashes, and evidence for each criterion. The reviewer instruction requires independent verification and says that requirements not present in the contract are contract ambiguity, not hidden rejection criteria.

A bound `DurableAgentConsumer.taskContribution(contract, role)` adds this packet alongside the consumer's existing durable-agent memory contribution. Calling `modelContribution()` directly remains unchanged.

## Completion proposals and review

A worker proposal has format `durable-agent-completion-proposal/1` and includes the `taskId`, contract digest, `attemptId`, `workerId`, exact input records, output artifact refs and hashes, evidence refs and hashes, criterion claims, and any blockers. `normalizeCompletionProposal()` validates this shape and rejects malformed or unbounded data.

The host calls `reviewCompletion(contract, proposal, { attemptId, workerId, reviewerId, verify })`. Before invoking the verifier it checks:

- the proposal is for the current task, contract digest, attempt, and worker;
- input IDs, versions, and digests match the current contract;
- every declared output and acceptance criterion is represented;
- evidence IDs and output references are known and each criterion has evidence covering its outputs;
- the worker has no blockers and the reviewer is not the worker.

The supplied `verify` function is independent and trusted host code. For each criterion it must resolve refs under the host's ACL, check artifact/evidence digests, and test the original requirement—not merely trust worker claims or a tool exit code. Exceptions fail closed. A valid-format artifact that lacks the requirement must therefore be rejected by the verifier.

The result is `verified`, `rejected`, or `blocked`, with per-criterion reasons. `blocked` is reserved for an otherwise structurally valid proposal with worker blockers; stale or invalid proposals are `rejected` even if they also list blockers. `verified` is only an evidence assessment: it is not authorization, task acceptance, permission to execute, or a commit. The host must re-check current contract/attempt state and its own authorization and commit rules before accepting or committing anything. The package intentionally performs no GAT wiring, session orchestration, team lifecycle control, or runner-DTO changes.

## Minimal host sketch

```ts
import {
  createTaskPacket,
  reviewCompletion,
  type CriterionVerifier,
} from '@deepseek-ai/dsh-durable-agent'

const contract = {
  format: 'durable-agent-task-contract/1', taskId: 'demo', revision: 1,
  outcome: 'Produce the report', nonGoals: ['No deployment'],
  inputs: [{ id: 'spec', version: '1', sha256: '<64 lowercase hex chars>' }],
  outputs: [{ id: 'report', description: 'The report file' }],
  acceptance: [{ id: 'complete', requirement: 'Report answers the spec',
    evidenceRequired: 'Report and verification evidence', outputIds: ['report'] }],
  authorityLimits: ['Read the declared input and write only the authorized report'],
  stopConditions: ['Stop if the input digest is stale'],
} as const

const packet = createTaskPacket(contract, 'worker')

const verify: CriterionVerifier = async ({ criterion, artifacts, evidence }) => {
  // Host code resolves refs, checks ACLs and sha256 values, and tests criterion.requirement.
  const passed = await hostChecks(criterion, artifacts, evidence)
  return { passed, reason: passed ? 'host checks passed' : 'requirement or evidence check failed' }
}
const assessment = await reviewCompletion(contract, proposal, {
  attemptId: currentAttemptId, workerId: worker.id, reviewerId: reviewer.id, verify,
})
// Re-check current state and authorization before any acceptance/commit.
```

`hostChecks`, `proposal`, `currentAttemptId`, `worker`, and `reviewer` above are host-owned values and are intentionally not provided by this package.

For a new-session semantic reviewer with machine preflight, evidence-only tools and audited rationale access, use the additive [fresh-context review API](reviewer-context.md). The older task contribution intentionally keeps its memory behavior and does not establish reviewer isolation.
