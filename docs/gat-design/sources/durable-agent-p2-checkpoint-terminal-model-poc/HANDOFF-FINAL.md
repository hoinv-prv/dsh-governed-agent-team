# Final handoff — Durable Agent P2 checkpoint terminal model

> This file supersedes `HANDOFF-COMPACT.md`. The mission is complete; this is a result and operating-lessons handoff, not authority to reopen accepted work.

## 1. Final mission status

- Mission: `durable-agent-p2-checkpoint-terminal-model-poc`
- Final WBS: `wbs.v36.json`
- WBS SHA-256: `8b9fba4125348be85d9bbaaa94e54f68f069dafc5c1757e44f17059586bb8fba`
- Execution state: `complete`
- Execution SHA-256: `a474131380a431265df9c57cc1faa08763c0e3d229e5c3eb49e059d19e6a3dc1`
- Decisions SHA-256: `531cee597af11b65e3f9c15a7374966618beedaeea17ef50aaff0a7a7df711fb`
- Attempts charged: `163/170`
- Attempt arrays: `162`; the historical charged-minus-array difference of `1` is intentional and preserved.
- Final HUMAN decision: `ACCEPT (Khuyến nghị)`
- Decision reference: `decisions.json#decision-final-p2-r36-009`
- Goal state: `complete`

The final acceptance grants **no** product, BS1, FS5, downstream execution, runtime-effect, self-acceptance, or learning-promotion authority.

## 2. Primary mission outputs

| Artifact | Purpose | SHA-256 |
|---|---|---|
| `final-report-r31.md` | Final evidence, limitations, and HUMAN decision report | `08e8c5a6e3b165ba34f7ad9f93257bfeaeafa31152a5672d7e02daf7f8b143e2` |
| `learning-candidates-r31.md` | Non-promoted learning candidates | `aaec1316e817e69f26023816122373bcd11f5c6218512d0e0bdba34c7c30ec12` |
| `integration-r31/integration-r31.md` | HUMAN-readable integrated P2 recommendation | `8d0156b00ab14c9e262974c2b33b80e9a4b8a8aafa21115e135eccafafae62c1` |
| `integration-r31/p2-decision-candidate-r31.json` | Machine-readable decision candidate | `df520179982f2fb9f9e9c7bfbdcc166d5ef14e2d9f8c0c417dda704e4523bd0a` |
| `integration-r31/source-hashes.json` | Compact exact-hash transitive receipt catalog | `b80e1fd10a8c0c91e97afe8e190d384ad6bddfaa72290cb1808a3145a9a2fad9` |
| `integration-r31/integration-selfcheck.test.mjs` | Coverage, provenance, and determinism validator | `d4b6b8fa5321b657ffbd02771d6ba527f0be52c083e48422f3f9898ace6cbb63` |
| `integration-r31/learning-check.md` | Integration scope and promotion limits | `eae6dc641e2ceb99812ec8bd47a7cfc30edd14fc55611817fa4751c7a688a909` |
| `progress.html` | Final HUMAN-readable WBS projection | `85c183c14d70e8c3cdaca0f0d1b571db56b794923f194942d430cb0586bd69cc` |
| `progress.json` | Final machine-readable WBS projection | `a9faa15077e9f5f0dc2eb75800faceb49d6c312586b18c1358f8e44002d1253f` |

Key accepted governance outputs:

- Integration evidence: `governance-r31/evidence/`
- Decision reconciliation: `governance-r31/reconciliation/`
- Contingency disposition: `governance-r31/contingency/`
- Accepted immutable deltas: `governance-r31/delta/`
- Runtime approval receipt: `governance-r31/runtime/runtime-approval-receipt.json`
- Attempt-local verification and review receipts: `evidence/<task-id>/<attempt-id>/`

Final native checks:

- Integration evidence: `69/69`
- Decision reconciliation a03-r36: `7/7`
- Contingency: `4/4`
- Integrated package: `8/8`
- Final manual verification and independent review: `meets_criteria`

## 3. How to inspect without broad reads

Start with this file, then use exact paths only:

1. Read `final-report-r31.md` for the conclusion and limitations.
2. Read `integration-r31/source-hashes.json` for transitive provenance.
3. Read `progress.json` for final task state.
4. Use `tools/bounded-json.mjs get|select` for exact `execution.json`, `decisions.json`, or WBS pointers.
5. Use `tools/wbs-task-context.mjs` for one task packet instead of reading the full WBS/execution ledger.
6. Read an attempt evidence directory only when investigating that exact attempt.

Do not recursively read the mission root, historical WBS revisions, the full evidence tree, or accepted implementation files merely to obtain status.

## 4. WBS design lessons

### 4.1 Keep tasks bounded and cohesive

A task should represent one independently verifiable outcome, not a large phase and not one file.

- Bundle only files that jointly implement or verify the same outcome.
- Give every task exact inputs, outputs, forbidden reads, effects, verification, review, acceptance, stop conditions, and attempt limits.
- If a task requires many unrelated inputs, changes multiple authority domains, or cannot be explained in one compact task packet, split it.
- If the solution or verification command is unclear, create a bounded discovery/preflight task first. Its output must close the uncertainty before the implementation task becomes ready.
- Use a separate integration task to prove transitive coverage; do not force each implementation task to reproduce global evidence.

### 4.2 A task is not an output inventory

Do not create one task per output file. A task may:

- create several cohesive outputs;
- validate an already-created output;
- reconcile receipts without changing the underlying implementation;
- render a HUMAN-readable view from machine evidence;
- perform integration or final acceptance checks.

Outputs exist to support the task outcome and the next handoff. File count is not progress.

### 4.3 Plan rework before execution

Normal rework must not require a new WBS.

- Budget implementation failure, verification failure, review-requested correction, and one bounded recovery hypothesis in advance.
- Each retry is a new immutable attempt with a new hypothesis and evidence directory.
- A failed or review-rejected attempt remains in history and is never relabeled as successful.
- Reserve more attempts for tasks with provenance, reconciliation, rendering, or cross-artifact consistency risk.
- Use a discovery task when uncertainty would otherwise consume implementation attempts.

Create a new WBS revision only when the approved contract changes: requirements, task meaning, dependencies, grants, commands, acceptance, hard ceilings, or global limits. Do not regenerate a WBS simply because normal rework occurred.

### 4.4 Allow task-budget adjustment without repeated HUMAN approval

Use two budget levels:

1. **Hard approved envelope:** global attempt ceiling plus a safe per-task maximum or auto-extension ceiling.
2. **Soft runtime allocation:** the coordinator's current expected attempts for each task.

The initial WBS should pre-authorize the coordinator to move unused soft retry budget between tasks when all conditions hold:

- total charged attempts remain within the approved global ceiling;
- the task remains inside its approved hard/auto-extension ceiling;
- scope, outputs, effects, commands, verification, review, and acceptance do not change;
- every added attempt has a new evidence-backed hypothesis;
- accounting remains append-only.

With the current schema, `max_attempts` is a hard contract field. Therefore, set it to a realistic upper envelope during planning and keep the smaller working allocation as runtime bookkeeping. Increasing only the soft allocation requires no HUMAN approval; changing the approved hard `max_attempts` still requires a revision.

For a future schema, encode an approved shared retry pool such as:

- `limits.max_total_attempts` — immutable global ceiling;
- `limits.retry_reserve` — pre-approved shared reserve;
- task `initial_attempt_budget` — soft starting allocation;
- task `max_auto_attempts` — hard coordinator-usable ceiling.

This mission needed r36 solely because `p2_decision_reconciliation.max_attempts=2` was too small. A pre-approved retry reserve would have avoided that revision while preserving the global cap.

### 4.5 Never reopen accepted work

- Accepted tasks and their artifacts are immutable.
- Do not reset an accepted task to `running` or rewrite its accepted output.
- Corrections use a new delta/reconciliation task or a new attempt on a task that is not yet accepted.
- Downstream work consumes exact accepted hashes and receipts, not mutable “current copies.”
- If an accepted producer genuinely becomes invalid because the contract changed, record explicit invalidation under a reviewed revision; never silently reopen it.

## 5. How to reduce rework

1. Make attempt identity, revision, plan hash, input hashes, output hashes, and accounting snapshot part of the selfcheck.
2. Validate exact 64-character SHA-256 values; prefixes are insufficient for final provenance.
3. Test negative cases for stale attempt IDs, stale accounting, authority widening, changed source receipts, and forbidden dependencies.
4. Generate HUMAN-readable and machine-readable outputs from the same bounded facts and test their agreement.
5. Run implementation review against the full Definition of Done, not only the initially observed failure.
6. Before verification, ensure all attempt-bound metadata was regenerated. A local wording patch is insufficient if the envelope and accounting still identify an earlier attempt.
7. Treat independent review as a real gate. In this mission, native `7/7` verification still missed stale a01 provenance in the a02 reconciliation artifact.
8. Keep accepted dependency hashes in the task packet so workers do not guess identities.
9. Separate coordinator-owned ledger/evidence packaging from worker-owned implementation outputs.
10. A sandbox refusal before process start is not a native test failure. Record it honestly and let a capable coordinator execute the single approved verification; never fabricate or duplicate a run.

## 6. Token-efficiency operating policy

The dominant token cost was repeated model turns with large context replay, not only raw file size.

### 6.1 Bounded retrieval

- Prefer `bounded-json get/select`, `grep`, exact `read` ranges, and task-context packets over full-file reads.
- Never place full WBS, execution ledger, progress history, evidence tree, minified bundles, or recursive directory listings in model context.
- Retrieve accepted details only when the current task needs them; otherwise use hashes and receipt references.
- Batch independent hash, validation, and report operations in one tool call when safe.

### 6.2 Limit task inputs

- Declare the smallest exact input set needed for the task outcome.
- Prefer accepted receipts or compact catalogs over raw producer artifacts.
- Forbid historical revisions, unrelated failures, recursive scans, and mutable current copies.
- Target a compact worker packet that includes identifiers, DoD, exact paths, hashes, one verification command, and stop conditions.

### 6.3 Limit task outputs

Outputs should be only what is needed to:

- verify the current task;
- hand off exact facts to the next task; or
- produce the final HUMAN/machine decision package.

Avoid duplicate narratives, repeated source copies, speculative reports, and task-local dashboards. One compact machine receipt plus one HUMAN-readable explanation is usually sufficient.

### 6.4 Reduce model turns

- Let one fresh-context worker complete a whole bounded implementation attempt.
- Do not use speculative scouts when exact source paths are already known.
- Keep worker and reviewer reports under about 900 characters: outcome, checks, hashes, evidence refs, risks, blocker.
- The lead should allocate and reconcile once, delegate once, verify once, review once, then accept or allocate one evidence-backed retry.
- Do not make workers repeatedly rediscover WBS state; pass the exact task packet.
- Diagnose a failure before retrying. Never repeat an identical attempt only to consume budget.

### 6.5 Assign work by role and complexity

Recommended routing:

- **Primary implementer:** cohesive multi-file implementation and integration tasks.
- **Simple-task implementer:** small, deterministic, low-risk artifacts with exact I/O.
- **Senior implementer:** difficult provenance/reconciliation work only when its actual runtime mandate permits writes.
- **Independent reviewer:** read-only review after implementation and verification; never self-review implementation.
- **Coordinator:** allocation, ledger CAS updates, exact verification execution, evidence packaging, acceptance, and HUMAN gates.

The agent's actual mandate overrides its informal role label. In this mission, `delta-auditor` remained read-only and correctly refused implementation despite an earlier handoff describing it as a possible senior implementer. Future missions should align the durable agent mandate and intended role before execution; otherwise reassign immediately rather than spending turns negotiating incompatible authority.

Use `max_parallel=1` when tasks share the same filesystem authority and are sequentially dependent. Parallelism helps only when scopes and effects are truly independent; otherwise it increases context, conflict, and reconciliation cost.

## 7. Specific lessons from this mission

- Accepted artifacts must remain immutable; deltas and new attempt IDs are the safe correction mechanism.
- A verification pass is necessary but not sufficient when provenance and HUMAN meaning require independent judgment.
- Exact attempt identity and accounting snapshots are functional requirements for reconciliation artifacts.
- Hash prefixes are useful for conversation summaries but must not appear as final provenance bindings.
- Reviewer-requested corrections must regenerate every attempt-bound field, not only the visible defect.
- WBS retry budgets should reflect provenance risk, not just coding effort.
- Progress reports are deterministic projections; `execution.json` remains authoritative.
- Token optimization should minimize parent turns and context replay first, then minimize bytes.
- Short task packets and short worker reports preserved quality while materially reducing unnecessary context.
- HUMAN approval remains mandatory only for explicitly protected decisions: plan contract changes outside a pre-approved budget policy and final HUMAN acceptance.

## 8. Handoff rule

This mission requires no continuation. Do not reopen completed tasks or rerun their verification for status reporting. If future work is requested, start from the accepted hashes above and create a new scoped mission, delta task, or reviewed contract as appropriate.
