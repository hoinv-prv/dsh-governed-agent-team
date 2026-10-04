# Fresh-context, evidence-bound review

Improvement ② is an additive **explicit host API**, exported from the package root. It does not install a GAT binder, change the Web GUI, create Team members, or rewrite runtime runner DTOs. Existing `modelContribution()`, `taskContribution()` and `reviewCompletion()` remain compatible.

## Flow and trust boundaries

```text
approved current contract + worker completion proposal
  -> host schema / current binding / byte hashes / trusted test receipts
  -> immutable versioned review packet
  -> NEW reviewer session: fixed system message + packet, evidence-only tools
  -> criterion verdict with references to independently read content
  -> recheck bytes, receipts and authoritative current identity
  -> advisory result (host owns acceptance and commit)
```

`runFreshReview()` is the recommended entry point. The host supplies `startFresh`, `readRef`, `verifyReceipt`, `audit` and `assertCurrent`; none defaults to an arbitrary filesystem, worker tool output or global model session. The adapter constructs a request with exactly `context: 'fresh'`, two messages, and fixed review tool descriptors. It never passes worker messages, worker memory/catalog/guidance, coordinator history, or worker rationale bodies. **The host transport must actually create a new session and not append hidden history.** The package can test the request payload, not prove a remote transport's hidden context.

Host identities are authenticated by the host; unequal strings alone cannot establish independent people/processes. Review tools are read-only. Artifact/evidence contents, risks and rationale are untrusted data and can contain hostile instructions; no prompt can guarantee an LLM will resist all of them. Host ACLs and read-only effects enforce the actual boundary.

## Public APIs

- `createReviewPacket(contract, proposal, options)`: async host preflight; throws on stale/broken binding, blockers, failed/missing required tests, digest mismatch or untrusted receipt.
- `normalizeReviewPacket(input)`: structure, bounds, canonical identity and consistency **only**, not authenticity or real machine execution.
- `reviewPacketSha256(input)`: canonical SHA-256 of normalized packet. Object key order does not matter; array order does.
- `reviewContribution(packet)`: compact `{ reviewPacketSha256, packet }` JSON envelope and two fixed tool descriptions, no durable memory contribution. The digest is supplied explicitly so a model need not calculate it.
- `DurableAgentConsumer.reviewContribution(packet)`: checks the bound reference is live, then returns the same memory-free contribution. Its guidance/catalog is deliberately not included. A contribution alone is not session isolation or trusted dispatch.
- `normalizeReviewerVerdict(input, packet)`: validates the exact packet/reviewer/criterion/evidence bindings and consistent top-level status, but cannot tell whether a model really inspected content.
- `runFreshReview(contract, proposal, options)`: host preflight, fresh transport, guarded evidence/rationale tools, verdict validation and post-review revalidation. Additionally rejects verdict references not read through its tools in this invocation.

Do not concatenate a memory-only or worker contribution into the reviewer request. Do not call `taskContribution(contract, 'reviewer')` expecting fresh-review isolation: that older method intentionally retains its compatible memory behavior. A caller-provided packet saying `machineChecks: 'passed'` is not a trusted receipt; `runFreshReview` always builds and checks its own packet.

## Packet and receipt schemas

`ReviewPacket` has format `durable-agent-review-packet/1` and exactly:

- `contract`, `contractSha256`: the full approved contract, shared with worker.
- `proposal`, `proposalSha256`: compact normalized completion claim (input identities, artifact/evidence refs and hashes, criterion mapping); no worker conversation or rationale.
- `reviewerId`: host-selected independent identity.
- `testReceipts`, `requiredTestSuites`: current trusted test results and the approved minimum suite policy.
- `knownRisks`: `{ id, description, sourceRef }` records, including known blockers/risks relevant to the contract. These are sourced assertions, not acceptance decisions.
- `rationaleRefs`: `{ id, ref, sha256 }` records; bodies are never read by packet construction. They cannot alias automatically readable evidence refs.
- `machineChecks`: exactly `{ schema: 'passed', bindings: 'passed', digests: 'passed', testReceipts: 'passed' }`.
- `instruction`: the fixed exported `REVIEW_INSTRUCTION` string.

Every test receipt is exactly `{ id, suite, attemptId, contractSha256, inputs, artifacts, result, log: { ref, sha256 } }`. ID and suite are unique. It must describe the exact current normalized inputs and the full current artifact ID/ref/hash set. `result` must be `passed`; a host callback cannot override a recorded failure. Every supplied receipt, including optional extra suites, must pass independent `verifyReceipt`. The callback should resolve the host's execution records, authenticated receipt store or rerun approved tests; checking the worker-supplied `result` alone is insufficient. Log hashes prove bytes, not that a test ran.

Required suites are **host policy derived from the approved contract**, not hidden reviewer criteria. An empty required set/receipt list is permitted for contracts without automated tests; `testReceipts: 'passed'` then means the required set is empty, not that semantic correctness was tested. Optional extra suites are allowed if valid, current and trusted. Input records are version/hash checked against the contract; the host still owns establishing that the contract's input bytes are authoritative.

Objects are closed and deeply frozen, envelopes <=64 KiB, lists <=32 items, strings <=4096 characters and hashes lowercase 64-character SHA-256. Failed preflight never calls the model. Artifact/evidence/test-log refs with conflicting digests are rejected. `readRef` must authorize exact refs, prevent traversal/symlinks where applicable, and snapshot bytes; there is no implicit path resolver.

## Host transport and rationale

`startFresh(request, tools)` returns a parsed verdict object or JSON string. Its request contains fixed tool descriptions plus two messages: fixed system instructions/response schema and a user envelope `{ reviewPacketSha256, packet }`. The bridge must map `review_read_evidence` to `tools.readEvidence(ref)` and `review_request_rationale` to `tools.requestRationale({ id, reason })`, start a new session, and await tool calls before returning. Tools are closed after transport completion; unfinished calls fail the review. Host/transport callback exceptions are not disclosed to the model/user through the returned error.

`readEvidence` exposes only packet-declared artifact/evidence/test-log refs, verifies exact bytes on each read and returns strict UTF-8. It is capped at 32 reads, 64 KiB per response and 256 KiB total. Binary/larger evidence needs a separate host-approved bounded representation, declared with its own digest and sufficient contract evidence; never silently truncate and pretend it is the original. The trusted `readRef` implementation should enforce storage/read limits before allocating large content; the adapter cannot constrain its internal allocation.

Rationale requests require a declared ID and a nonempty bounded reason. `rationaleBudget` has exactly `{ maxRequests, maxBytes }`, allowing 0..16 requests and 0..65536 cumulative content bytes. Zero requests disables access. Denied/invalid/over-budget requests are audited. Valid requests persist `requested` before fetching, then `served`, `denied` or `error`; served content is digest-checked and bounded. `served` records the audited grant, not a proof of remote delivery: if a detached transport closes during persistence, an append-only compensating `error` records that the grant was not delivered. The review fails and content is withheld. A rationale can clarify a decision, never replace artifact inspection. Failed audit persistence fails the whole review even if transport catches the tool error. There is an additional hard cap of 32 total rationale calls to bound denied-request abuse. The returned `rationaleAudit` is a frozen convenience copy; the host persists the authoritative append-only audit.

`assertCurrent(binding)` compares the exact contract/proposal hashes, attempt, worker and reviewer against host state before model dispatch and after review. Digests and receipt authenticity are rechecked after model completion. This is not an atomic commit: the host must perform a final current-state/authorization check atomically with any later acceptance/commit. Newly requested rationale bodies are checked at access time; they do not become artifact acceptance evidence.

## Verdict

Format `durable-agent-reviewer-verdict/1` has exactly `format`, `reviewPacketSha256`, `reviewerId`, `status`, `criteria`, `risks`.

Each criterion is `{ criterionId, status, reason, evidenceIds, artifactOutputIds }`, once for every approved criterion. A `met` criterion must cite claim-bound evidence covering every criterion output, and all its output IDs. `not_met` must cite at least an artifact or evidence reference supporting the defect. `insufficient_evidence` can have no refs when evidence is unavailable. All cited refs must actually have been read through guarded tools during `runFreshReview`.

Top-level status is derived: any `not_met` -> `changes_required`; otherwise any `insufficient_evidence` -> `insufficient_evidence`; otherwise `meets_criteria`. Unknown/missing criteria, unbound refs, inconsistent statuses, extra approval/commit fields and malformed model JSON fail closed. A syntactically valid verdict is still a model's advisory semantic assessment, not a deterministic truth proof.

## Integration sketch

The host functions in this sketch are intentionally application-specific. No example callback that always returns `true` is a production verifier.

```ts
import { runFreshReview, type FreshReviewOptions } from '@deepseek-ai/dsh-durable-agent'

// These values come from your approved contract, worker proposal and trusted host records.
const options: FreshReviewOptions = {
  attemptId: currentAttempt.id,
  workerId: currentAttempt.workerId,
  reviewerId: selectedReviewer.id,
  testReceipts: hostReceipts,
  requiredTestSuites: approvedTestPolicy.suites,
  knownRisks: sourcedKnownRisks,
  rationaleRefs: approvedRationaleRefs,
  rationaleBudget: { maxRequests: 2, maxBytes: 8192 },
  readRef: ref => evidenceStore.readAuthorizedSnapshot(ref, selectedReviewer),
  verifyReceipt: receipt => executionLedger.verifyReceipt(receipt),
  audit: event => auditStore.append(event),
  assertCurrent: binding => taskStore.matchesCurrent(binding),
  startFresh: (request, tools) => modelBridge.reviewInNewSession(request, tools),
}
const result = await runFreshReview(currentContract, workerProposal, options)
if (result.verdict.status !== 'meets_criteria') {
  // Keep task open. Record criterion findings for correction or more evidence.
} else {
  // Advisory only: apply your authorized acceptance/commit gate with atomic state recheck.
}
```

The model bridge must supply the response schema from the system message and execute the exposed callbacks; merely handing a prompt to a reused chat is not this feature. Machine `passed` flags, a worker claim, or two agreeing agents never independently close a task.

## Verification and A/B evaluation

Run `pnpm build`, `pnpm run test:reviewer-context`, then `pnpm run benchmark:reviewer-ab` for the explicitly **deterministic smoke**. The bounded harness has paired full-chat/evidence-only lanes with identical evidence/model/tool/budget configuration and repeated reversed order. A separately supplied trusted host bridge or hash-bound externally collected model responses is required for live efficacy measurements. Mock metrics do not establish collusion reduction. See [A/B results and limitations](reviewer-ab-results.md).

The design follows the local research-pack recommendations and provenance/independent-review lessons. It does not claim to reproduce the paper or generalize its reported collusion rate to this system.
