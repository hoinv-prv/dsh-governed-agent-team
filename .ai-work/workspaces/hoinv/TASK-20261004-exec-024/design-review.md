# Independent reviewer-contract design review — 2026-10-04

Reviewer: /root/review_contract_design, Astra. Read-only; no files changed or tests run. Actual returned verdict: optional host-supplied port is viable and bounded; direction approved subject to corrections, full STEP-03/production not cleared.

Inspected official GAT Detail §§5/7/8/9, member freeze, DA DD06/07/09 and public packet/host helpers, current execution and finalizer interfaces, original proposal/qualification candidate. Direct binding preserved.

## Required settled contract

- A single optional trusted plugin service resolve(selection, reviewer) suffices; no generic registry/second runner/runFreshReview/automatic acceptance. Resolve during awaited creation; require exact review reference and revision. Ordinary tasks do not require this service.
- Reviewer live tuple and completed worker durable tuple are distinct. Retain exact Agent/root objects and WK/port service identities. Worker need not be live or active. Self-review denial uses authenticated member/principal, not arbitrary names.
- Separate approved contract hash, DA proposal hash and exact GAT candidate/result hash, with host-attested association.
- Trusted synchronous assertCurrent checks protect finalization, alongside checks before/after each underlying asynchronous resolve/read/receipt/audit/provision operation.
- Evidence-only context is not a validated DA verdict. Keep existing GAT provisional submission as a narrow control exception. Do not add full verdict/actual-read/atomic-acceptance orchestration to this memory adapter.
- Before production code: settle and qualify the trust-boundary contract with real Loader/GAT/WK and authenticated fixture-owned records/actual test attestation. Actual live workflow/ACL/topology is an activation gate, not a reusable-adapter construction prerequisite.

## Proposed minimal port

resolve({ selection: { reference, revision }, reviewer: ReviewerAssignment }): Promise<ReviewInput | undefined>.

ReviewerAssignment: rootSessionId, executionId, sessionId, memberId, generation, taskId, taskRevision, configurationSha256.
ReviewedCandidate: rootSessionId, executionId, sessionId, memberId, generation, taskId, taskRevision, attemptId, candidateSha256, contractSha256, proposalSha256.

ReviewInput: reviewer/candidate tuples; approved DA contract/proposal; policy containing public ReviewPacketOptions data; limits; synchronous assertCurrent(); readRef({ref,maxBytes,purpose: packet-validation|evidence|rationale}); verifyReceipt(receipt); audit(event). Detach/normalize data; callbacks are trusted host dependencies, not authenticated by TS/freezing/hashes alone.

Call public createReviewPacket with wrapped callbacks, freeze packet/hash. Tools: review_get_packet({}), review_read_evidence({ref}) using reviewEvidenceRefs, review_request_rationale({id,reason}) using declared refs. Exact executor allowlist includes guarded team_execution_submit only as provisional control. Deny ambient memory/filesystem/transcripts/shell/delegation/mutation/wrapper bypasses; verify deployment does not inject personal memory through other prompt owners. Task Session is the sole runner; results never become memory/system contributions.

Explicit adapter and host allocation/count/byte limits: envelopes ≤64 KiB; evidence ≤32 calls, ≤64 KiB each, ≤256 KiB aggregate; rationale ≤16 requests/≤64 KiB aggregate and hard attempts counting denials. Separately bound eager packet-validation reads and bytes. Reserve capacity before awaits; concurrency-safe accounting; exact bytes/digest before strict UTF-8; complete serialized results bounded. Audit request/terminal before rationale delivery, binding exact tuples/hash/request/ref/status/bytes without bodies/private provider values. Prepublication audit must say prepared/authorized, not falsely served when finalizer later suppresses content; actual Session result is delivery evidence.

Cutoff removes tools/closes admissions synchronously, retains Agent denial, joins callbacks/WK release, preserves failed/timed-out ownership. Avoid self-drain. Recovery re-resolves exact current trusted inputs before model/tool use; old outputs/refs/callbacks are not recovery authority.

## Remaining clearance

Qualify absent/stale/foreign inputs, successful delivery, genuine/forged receipts/digests/ACL, ambient tools, concurrent bounds, post-await/finalizer authority loss, cutoff/recovery. Constant verifyReceipt:true is not provenance evidence. Live authority owner/workflow remains unresolved and belongs in deployment proposal. Parallel lifecycle corrections and reviewer fixtures are required before full STEP-03.
