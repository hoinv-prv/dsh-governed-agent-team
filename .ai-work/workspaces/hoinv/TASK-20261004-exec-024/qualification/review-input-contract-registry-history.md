# Reviewer input contract — plugin-only proposal for STEP-03 review

Status: proposed, not accepted or implemented. OP-024-01 remains open. This is the smallest identified plugin integration seam, not a request to change DSH Core.

## Demonstrated source gap

Current public TeamExecutionBrief provides acceptanceCriteria strings, deliverable strings, inputs reference/revision and checks. TeamExecutionSnapshot binds assignment/Session/member/generation/task revision and provisional result. Neither contains a DA TaskContract, CompletionProposal, acceptance criterion/output IDs, immutable evidence digests or independently attested test receipts. A raw text result is not those authenticated structures. Searching current GAT source and execution interfaces found no createReviewPacket/verifyReceipt/ReviewPacket operation.

DA Detail DD-06/07 and public createReviewPacket require exact current contract/proposal bindings, independently supplied approved criteria/output IDs, ACL-authorized bytes and trusted receipt attestation. normalizeReviewPacket checks structure, not provenance. Consumer.reviewContribution also opens a memory snapshot, although it excludes memory from its output. Pure public packet functions can validate evidence without that memory context read. runFreshReview is a separate transport runner and cannot silently replace this AIP's existing GAT execution runner.

## Proposed plugin seam

A trusted companion plugin supplies review inputs to execution-composition through an effect-scoped registry/service. Model-visible tools cannot register or modify those inputs. Registration names one explicit review-packet reference that the immutable reviewer assignment must select in brief.inputs. Registration includes two separate bindings:

- Reviewer assignment: exact live Lead/root, reviewer execution ID/Session/member/generation/task ID/task revision and declaration/config identity.
- Reviewed candidate: exact original task/revision, worker execution/Session/member/generation, current provisional candidate digest and approved contract digest.

Keep those bindings separate: the review assignment may have a different task ID from the worker task under review. No matching by member display name or a generic reviewer label.

The trusted registration supplies the approved DA TaskContract and CompletionProposal, public ReviewPacketOptions policy, ACL readRef, verifyReceipt, bounded allocation policy and a current-authorization callback. They must be derived by the actual host workflow from current authorized inputs, not synthesized from anonymous brief strings. That host workflow is an explicit integration requirement; the adapter does not manufacture approval or provenance.

At awaited creation, resolve the exact selected registration; validate both identities before/after every await; call public createReviewPacket with trusted callbacks, freeze the resulting packet and bind its digest. Missing/stale/foreign/multiple registrations, changed target candidate or failed ACL/receipt verification reject before model release. No reviewer packet exists by default.

Deliver the packet through a bounded task-scoped tool result, never a memory/system prompt contribution. Register only packet/evidence/rationale reads with immutable allowlists, actual-byte digest verification, explicit count/per-call/aggregate UTF-8 limits and requested/terminal Session audit. All asynchronous calls join cutoff/cleanup. Rationale requires a declared ID and specific reason, and remains untrusted data. Results do not authorize final acceptance.

Enforce an explicit reviewer tool allowlist on the exact Agent, including denial of ambient memory, transcript, filesystem, shell, delegation and mutation access. Merely omitting durable_agent_read_memory does not meet this isolation contract. Retain denial after cutoff until the Agent context is disposed. A parent/root wrapper or second runner is unnecessary.

Before returning an advisory review result, revalidate current candidate, packet digest and authorized reads against the same binding. GAT's existing provisional submission/final acceptance process remains authoritative; no adapter auto-approval.

## Review and qualification requirements

STEP-03 must settle the public registration/config signature, companion-plugin ownership, audit/bounds and exact approved input workflow before production code. Existing task-memory prototype proves only memory denial for reviewer mode; it does not implement this registry or qualify packet delivery.

New executable evidence must include actual current host registration/assignment/candidate/receipt provenance, initial missing/foreign/stale packet rejection with zero execution transport, successful evidence-only result/logging, forged receipt/digest/ACL failures, ambient memory/tool denial, delayed authority loss, count/byte bounds and cutoff/recovery. No fake fixture PASS may be substituted for production receipt provenance.

This seam changes only GAT plugin code/config and uses existing assignment input references and public WK packet helpers. No DSH loop/Team persistence or WK provider API change is proposed. If the actual host cannot provide these approved inputs, reviewer activation must stay unavailable and the full AIP cannot claim completion.
