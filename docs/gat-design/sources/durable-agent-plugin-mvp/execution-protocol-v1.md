# Execution evidence protocol v1

**Mission:** `durable-agent-plugin-mvp`  
**Applies to:** every WBS revision-9 product task and attempt `t02`–`t19`  
**Authority:** approved WBS revision 9, SHA-256 `0f55a592ae78c79dceada8d1ba10275b40ea449d3189fe29ffc6d5058afd951f`  
**Effect:** evidence governance only. It adds no product acceptance, command, effect, write scope, authority, retry, or automatic acceptance.

## 1. Normative rule

A green command is necessary where declared, but never sufficient. A task is acceptance-ready only when every conjunctive acceptance claim has one complete evidence-matrix row bound to authoritative post-verification bytes, independent review is valid, and the designated acceptance owner records an explicit decision.

File existence, worker completion, passing aggregate tests, reviewer prose without byte binding, or coordinator inference cannot satisfy a row.

## 2. Authority order and snapshot classification

When records disagree, use this order:

1. exact HUMAN approval/acceptance decision bound to a WBS or artifact hash;
2. selected immutable WBS revision and its task contract;
3. append-only `execution.json` and `decisions.json` after reconciliation;
4. current durable Team ownership/task state and coordinator/goal state;
5. final-byte manifests, verification records and independent reviews for the exact attempt;
6. design baseline, this protocol and accepted task inputs;
7. advisory analyses, summaries and chat messages.

`progress-analysis.md` is an **advisory historical snapshot**, not current authority. Its snapshot claims—revision 8 selected, t01 pending, one accepted task, seven attempts charged, no G0 HUMAN decision, different current Session/unclear handoff, missing r8 reconciliation, and its then-current critical-path numbers—are **stale and must not be copied as current state**. Its retained lessons remain valid: RC2 command success did not close conjunctive claims; RC3 delayed broad evidence closure; RC5 ownership/handoff and audit gaps can stall ready work; P0/P1 recommendations for ownership proof, freshness, matrices, independent review and append-only reconciliation are adopted here. RC1/RC4 remain historical lessons, not present blockers.

Any status report must label a fact `current-authoritative`, `historical`, or `advisory`. Unknown timestamps remain unknown; do not invent elapsed time, latency or schedule delay.

## 3. Pre-dispatch gate

The coordinator must complete all checks before charging or dispatching:

1. **Ownership:** identify the recorded coordinator and current successor authority. If identities differ, require explicit handoff/resume evidence; never infer takeover from PID, idle status or filesystem access.
2. **Quiescence:** prove the predecessor and all prior writers are settled: no active Team task owner that may write the scope, no relevant running subagent/job, no unresolved command process, and `active_work` reconciled. Record the observations and timestamp.
3. **Fresh accepted inputs:** exact-hash every immutable task input named by the WBS or reference an already authoritative hash. Confirm dependencies are accepted and their evidence remains valid. Any drift is HOLD until reconciliation/revision.
4. **Scope/effects:** compare requested read/write paths, resources, effects and every verification argv/cwd/timeout with the WBS. No implicit shell, network, product, profile, HOME or control write.
5. **Attempt capacity:** preserve prior charges; allocate and record the attempt before dispatch. A worker/session/reopen does not reset it.
6. **Matrix skeleton:** copy `evidence-matrix-template.md`; split every acceptance sentence connected by `and`, `or`, lists, semicolons or route/state variants into atomic conjunctive claim rows. Record negative claims separately.
7. **Independence plan:** name prohibited contributor identities and the required reviewer class before implementation.

Failure of ownership, quiescence, freshness, attempt capacity or exact scope is a dispatch stop, not a reason to weaken the task.

## 4. Timestamped attempt lifecycle

Every attempt uses UTC ISO-8601 timestamps with millisecond precision and an append-only sequence. Each event records `event_id`, task/attempt/WBS hash, actor identity, evidence/ref, and previous event id.

| Required event | Minimum content |
|---|---|
| `allocated_at` | attempt charged, budget before/after, exact task/revision/hash |
| `dispatched_at` | worker identity, task-board revision, write scope, brief hash |
| `worker_settled_at` | worker status, changed files, claimed matrix rows; explicitly provisional |
| `verification_started_at` / `verification_finished_at` | coordinator identity, exact ordered commands/manual checks, exits, output refs |
| `bytes_frozen_at` | final manifest/hash, custody owner, last mutating verification |
| `review_started_at` / `review_finished_at` | independent reviewer, contributor-set check, manifest hash, verdict |
| `response_opened_at` / `response_settled_at` | if used, exact findings and same-attempt bound |
| `accepted_at` or `blocked_at` | authorized owner, complete matrix hash, review ref, reason |
| `attempt_settled_at` | final attempt outcome and remaining task/mission budgets |

Missing lifecycle timestamps prohibit duration/latency claims. They do not authorize rerunning accepted historical work.

## 5. In-attempt evidence discipline

- Update the matrix during implementation, not after aggregate tests.
- One row covers one observable claim for one route/state/failure variant. A shared artifact may be referenced by many rows but cannot merge claims.
- Each row must bind: normative source; implementation symbol/path; focused positive test; focused negative/fault test where meaningful; produced artifact; authoritative final hash; reviewer; disposition.
- “Not applicable” requires a source-bound rationale and reviewer concurrence. Blank means open.
- A negative claim such as “no raw output,” “no duplicate effect,” or “no unauthorized access” needs an adversarial marker/fault/cross-scope test; code inspection alone is insufficient.
- The worker may state `ready_for_verification`, never `accepted`.
- Raw search output, child transcript, reviewer chain-of-thought or unrelated worker chat must not enter worker context or the Mission store. The coordinator forwards only bounded findings, citations and required changes.

## 6. Verification and final-byte custody

1. Settle all writers before coordinator verification.
2. Execute every declared verification entry exactly as ordered and record it once. A command failure is evidence, never silently replaced.
3. Treat installs, builds, generators, snapshots and Web tests as mutating when they can change bytes.
4. After the **last mutating verification**, generate/read the authoritative manifest required by the task. It must include current source, tests, configuration, lock/package/tarball/generated descriptors, artifacts, screenshots, reports and the matrix as applicable.
5. Record `bytes_frozen_at`, manifest SHA-256, complete file/hash set, coordinator identity and verification record hash.
6. From freeze through review/acceptance, no in-scope byte may change. A change invalidates verification and review; rerun the full affected declared sequence, freeze a new manifest, and record the supersession append-only.
7. Execution hashes, verification, reports, matrix and review must agree with the frozen manifest. A stale hash is HOLD.
8. Review is explicitly “of manifest `<sha256>`”; a verdict on earlier bytes cannot accept later bytes.

The coordinator is custodian of final bytes. Workers and reviewers cannot update the frozen set while reviewing it.

## 7. Contributor-set independence

The contributor set is the union of identities that authored code/design, changed tests/fixtures/reports, selected claims, generated nonmechanical expected data, or directed the remediation being judged. Tool/runtime identity and parent/child lineage are recorded.

An independent reviewer must:

- not be in the contributor set for the reviewed claims;
- receive the task contract, matrix, final manifest and evidence, not worker intermediate chat;
- inspect exact current bytes and negative evidence;
- return `meets_criteria`, `changes_required`, or `insufficient_evidence` with row IDs;
- never edit reviewed files or self-accept.

Automated generation alone does not add a contributor; the person/agent choosing its inputs does. Coordinator verification does not make the coordinator independent for claims they implemented.

## 8. Bounded same-attempt review response

A review response may reuse the already charged attempt only when all conditions hold:

- the attempt is not accepted and its immutable charge already exists;
- the hypothesis, WBS task, accepted inputs, commands/effects/write paths and acceptance remain unchanged;
- findings are corrections to the same deliverable/evidence, not new scope or a failed stop condition;
- the coordinator explicitly reopens the same Team task/attempt and forwards only cited findings;
- at most **one** response round, bounded to the lesser of **20% of task effort** or **60 minutes**;
- all affected verification is repeated, a new authoritative manifest is frozen, and a fresh independent review occurs.

If the bound is exceeded, a source changes, a new command/effect is needed, the hypothesis changes, or the second review still blocks, settle the attempt `changes_required`/`blocked` and use the WBS attempt/revision process. Reopening a Team task is not a free retry.

## 9. Acceptance and settlement

Before acceptance, the coordinator proves:

- all matrix rows are `PASS` with final hashes and evidence, or explicitly HUMAN-waived by exact row id without contradicting WBS stops;
- all declared commands/manual checks passed on frozen bytes;
- reviewer independence and verdict are valid;
- stop conditions are false;
- no worker/reviewer self-accepted;
- budgets/attempts and output hashes are reconciled.

Only the task’s WBS acceptance owner may accept. The acceptance record binds task id, attempt id, WBS hash, matrix hash, final manifest hash, verification and review refs, timestamp and actor. Green commands alone leave the task unaccepted.

## 10. Append-only reconciliation

Never rewrite an immutable WBS, decision, attempt, review, acceptance or historical output to “fix” chronology. Append a reconciliation containing:

- new reconciliation id and UTC timestamp;
- affected record ids and observed inconsistency;
- authoritative source/evidence refs;
- corrected current interpretation;
- superseded claim (not deleted);
- actor and predecessor reconciliation id.

Reconciliation may repair metadata/history only; it cannot fabricate consent, uncharge an attempt, change product acceptance, or convert stale bytes into current evidence. If facts cannot be proven, record `unknown` and block the dependent claim.

## 11. Nonblocking ready-batch selection

After each settlement or gate change, derive readiness from accepted hard dependencies only. A waiting review/HUMAN decision blocks its dependents, not unrelated tasks.

A task may join the next batch only if:

- every hard dependency is accepted with valid fresh evidence;
- its read/write paths, verification side effects and exclusive resource keys do not conflict with active work;
- ownership/quiescence and attempt capacity pass;
- batch size respects WBS `max_parallel`.

Soft ordering ranks ready tasks but never creates a blocker. Do not hold a ready independent task merely because another task is waiting. Conversely, apparent parallelism never overrides shared mutable paths/resources or an unaccepted dependency. Record each selection and exclusion reason with timestamp.

## 12. Required use at t18/t19

`t18` must audit every t02–t17 matrix row and frozen byte chain against r1–r15. `t19` must bind the final report to the authoritative package/tarball/manifests, all independent reviews, reconciliations, residual risks and explicit HUMAN gate. Neither task may backfill missing evidence with prose or rerun accepted t00/t01 merely because this protocol was introduced later.
