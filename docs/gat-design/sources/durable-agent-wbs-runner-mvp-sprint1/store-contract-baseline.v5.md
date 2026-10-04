# Sprint-1 checkpoint Contract Baseline v5

## 1. Status, objective, scope, and binding

- **Contract version:** `5`.
- **On-disk `schemaVersion`:** the JSON number `2`.
- **Status:** normative planning-baseline successor and candidate for preimplementation review; not product implementation, mission execution authority, approval, or acceptance.
- **Evidence binding token:** `CURRENT_BASELINE_SHA256_RECORD`. A separate coordinator binding record MUST resolve this token to the real SHA-256 of this exact file. Author, test, verification, and review records MUST cite that one recorded value. This file contains no self-hash or substitute hash.
- **Objective:** define one uniquely implementable checkpoint-store contract for one approved, sequential, local runtime plan: consume an attempt before its effect, prevent replay of completed work, convert an interrupted current attempt into a consuming unknown outcome, permit only an explicitly eligible retry, and expose one deterministic store projection.

This baseline is complete in itself. Existing `dsh-wbs/1` artifacts, including `wbs-runs/durable-agent-wbs-runner-mvp-sprint1/wbs.v3.json`, are implementation-mission plans and MUST NOT be parsed, normalized, approved, hashed, or executed as a product `RuntimePlanV1`. Their present binding is not a readiness condition for this baseline.

### 1.1 Exact owner and threat model

Exactly one process and one live store owner instance own one checkpoint path and one `runId` from successful `initialize` or `open` until the single close barrier settles or that instance is abandoned. The caller MUST NOT create a second live owner for the path during that lifetime. Runtime `maxParallel` is exactly `1`. One instance serializes admitted calls in FIFO invocation order.

In scope: closed-schema validation; malformed, truncated, invalid-UTF-8, noncanonical, unsupported-version, cross-plan, cross-approval, cross-run, stale-generation, forged-identity, impossible-history, and extra-field snapshots; same-instance concurrent calls; pre-rename local write failures; and restart with one persisted current attempt.

Out of scope: a second process or live owner; hostile same-UID mutation; cross-process locks; multi-owner or multi-writer atomic CAS; distributed leases; append-only custody; generic migrations; filesystem or hardware dishonesty; and power-loss guarantees. Atomic local replacement is the only durability claim. These exclusions preserve CB-010 and CB-011.

### 1.2 Non-goals

No parallel execution, automatic retry, arbitrary history editing, database, network or external effect, production-readiness claim, old-snapshot import, or new WBS authority is defined. Workspace containment and effect execution remain runner obligations; the store validates the frozen action identity and settlement tuple but does not perform the action. Exact JSON/Markdown report rendering is not defined.

## 2. Scalar domains and closure rule

Every object named in this baseline is **closed**: listed required fields MUST exist, listed optional input fields MAY be absent, and no other field is legal. `null` is legal only where shown. Object member order is semantically irrelevant. Arrays preserve their specified order.

| Name | Exact domain |
|---|---|
| `Utf8Text` | JSON string with no unpaired UTF-16 surrogate; it may be empty. Its bytes are exact UTF-8 without normalization. |
| `NonEmptyText` | `Utf8Text`, length at least 1, equal to its own ECMAScript `trim()`, and containing no U+0000. |
| `ShortCode` | `NonEmptyText` of at most 128 UTF-16 code units. |
| `Digest` | lowercase ASCII matching `^[a-f0-9]{64}$`. |
| `SafeNat` | JSON number that is a safe integer in `[0, Number.MAX_SAFE_INTEGER]`; `-0` is forbidden. |
| `PositiveInt` | safe integer in `[1, Number.MAX_SAFE_INTEGER]`. |
| `ExitCode` | safe integer in `[0, 255]`. |
| `Timestamp` | `SafeNat`, interpreted as Unix epoch milliseconds. |
| `TaskIdText` | `NonEmptyText` of at most 128 UTF-16 code units. It is only a syntactic domain and does not imply membership in a plan. |
| `PlanTaskId` | a `TaskIdText` already proven to equal exactly one task ID in the normalized runtime plan. This is a semantic refinement, not a distinct JSON representation. |
| `WorkspacePath` | `NonEmptyText` using `/`, not starting with `/`, containing no `\\`, and having only nonempty segments other than `.` or `..`. |
| `CheckpointPath` | caller-supplied `NonEmptyText`; it is not persisted. |
| `FileOperation` | one of `"read"`, `"write"`, `"append"`, `"delete"`. |

Raw checkpoint and request schemas use `TaskIdText`, never `PlanTaskId`. Plan membership and checkpoint order are not scalar or structural facts. They are checked only in the plan-normalization, checkpoint-identity, or status-membership stages explicitly named in §§3.2, 6.4, and 8.5. Accepted checkpoint and output values may then be treated as containing `PlanTaskId` values.

SHA-256 always means SHA-256 over the exact byte sequence and a lowercase hexadecimal digest. `canonicalHash(v) = SHA256(UTF8(canonicalJson(v)))` using §10.

## 3. Product runtime plan and approval

### 3.1 Closed `RuntimePlanV1` input

```text
RuntimePlanV1 = {
  format: "durable-agent-runtime-plan/1",
  missionId: NonEmptyText,
  revision: PositiveInt,
  maxParallel: 1,
  tasks: RuntimeTaskV1[1..20]
}

RuntimeTaskV1 = {
  id: TaskIdText,
  title: NonEmptyText,
  dependencies: TaskIdText[0..19],
  action: FileActionV1 | CommandActionV1,
  maxAttempts?: 1 | 2,
  retryable?: boolean
}

FileActionV1 =
  { kind: "file", operation: "read", path: WorkspacePath } |
  { kind: "file", operation: "write", path: WorkspacePath, content: Utf8Text } |
  { kind: "file", operation: "append", path: WorkspacePath, content: Utf8Text } |
  { kind: "file", operation: "delete", path: WorkspacePath }

CommandActionV1 = {
  kind: "command",
  argv: NonEmptyText[1..64],
  cwd: WorkspacePath,
  timeoutMs: PositiveInt,
  expectedExitCode: ExitCode
}
```

Task IDs are unique. A dependency list contains unique existing task IDs, excludes its own task, and the whole graph is acyclic. Task array order is immutable and is the dispatch tie-break order.

### 3.2 One normalization and plan hash

`normalizeRuntimePlan(input)` performs these steps in order:

1. Reject any closure, scalar, cardinality, uniqueness, dependency-membership, self-reference, cycle, or `maxParallel` violation with `PLAN_INVALID`. Dependency membership belongs to this plan-normalization stage, not to raw request structural validation.
2. Preserve task array order, every string byte-for-byte, and every action field.
3. Reorder each task's dependency array into the referenced tasks' plan-array order.
4. Set effective `maxAttempts` to the supplied value, or exactly `1` when omitted.
5. Set effective `retryable` to the supplied value, or exactly `(effective maxAttempts === 2)` when omitted.
6. Emit the same closed shape with both `maxAttempts` and `retryable` required.

Thus every runtime task has effective `maxAttempts` exactly `1` or `2`. A task with `maxAttempts: 2, retryable: false` is legal but cannot be resumed after a failed or unknown first attempt. A supplied `maxAttempts: 1, retryable: true` is rejected as `PLAN_INVALID`, because it promises a retry with no retry budget.

```text
planSha256 = canonicalHash(normalizeRuntimePlan(input))
```

There is no other plan normalization, inferred dependency, default, Unicode normalization, task sort, or hash input.

### 3.3 Closed `RuntimeApprovalV1` and approval hash

```text
RuntimeApprovalV1 = {
  format: "durable-agent-runtime-approval/1",
  missionId: NonEmptyText,
  revision: PositiveInt,
  planSha256: Digest,
  decision: "APPROVED",
  approver: NonEmptyText,
  approvedAt: Timestamp
}
```

Approval normalization is closed-schema/scalar validation with no defaults and no transformed fields. `missionId`, `revision`, and `planSha256` MUST equal the normalized runtime plan. Otherwise validation returns `PLAN_APPROVAL_MISMATCH`.

```text
approvalSha256 = canonicalHash(validatedApproval)
```

The checkpoint binds both hashes. A different approval, even for the same plan, is a different approval identity.

## 4. Closed raw checkpoint schema v2

Version `2` is a new literal format. No earlier baseline artifact created an accepted product snapshot. Version `1`, an absent version, a future version, and every other version return `UNSUPPORTED_SNAPSHOT_VERSION` before identity, reconciliation, or write. There is no migration or compatibility reader.

```text
CheckpointV2 = {
  schemaVersion: 2,
  missionId: NonEmptyText,
  revision: PositiveInt,
  planSha256: Digest,
  approvalSha256: Digest,
  runId: NonEmptyText,
  generation: SafeNat,
  attemptCounts: AttemptCount[plan.tasks.length],
  settledAttempts: SettledAttempt[0..40],
  current: CurrentAttempt | null,
  blocker: Blocker | null
}

AttemptCount = {
  taskId: TaskIdText,
  count: SafeNat
}

CurrentAttempt = {
  taskId: TaskIdText,
  attemptOrdinal: PositiveInt,
  attemptId: Digest,
  idempotencyKey: Digest,
  startedAt: Timestamp
}
```

At the raw schema stage, `plan.tasks.length` supplies only the exact array cardinality; the entries' membership and order are deferred to checkpoint identity. After identity validation, every persisted task ID is a `PlanTaskId`, `attemptCounts` has one entry per plan task in plan order, `settledAttempts` is in dispatch order, and `current`, when present, is the last dispatched attempt. At most 40 attempts can be settled because there are at most 20 tasks and two attempts per task.

### 4.1 Settled attempts

```text
SuccessAttempt = {
  outcome: "SUCCESS",
  taskId: TaskIdText,
  attemptOrdinal: PositiveInt,
  attemptId: Digest,
  idempotencyKey: Digest,
  startedAt: Timestamp,
  settledAt: Timestamp,
  result: FileSuccess | CommandSuccess
}

FailureAttempt = {
  outcome: "FAILURE",
  taskId: TaskIdText,
  attemptOrdinal: PositiveInt,
  attemptId: Digest,
  idempotencyKey: Digest,
  startedAt: Timestamp,
  settledAt: Timestamp,
  retryEligible: boolean,
  result: FileFailure | CommandFailure
}

UnknownOutcomeAttempt = {
  outcome: "UNKNOWN_OUTCOME",
  taskId: TaskIdText,
  attemptOrdinal: PositiveInt,
  attemptId: Digest,
  idempotencyKey: Digest,
  startedAt: Timestamp,
  settledAt: Timestamp,
  retryEligible: boolean,
  reason: "INTERRUPTED_AFTER_DISPATCH",
  result: null
}

SettledAttempt = SuccessAttempt | FailureAttempt | UnknownOutcomeAttempt
```

### 4.2 Persisted result union

```text
FileSuccess = {
  kind: "file",
  operation: FileOperation,
  status: "ok",
  outputBytes: SafeNat | null,
  outputSha256: Digest | null
}

FileFailure = {
  kind: "file",
  operation: FileOperation,
  status: "error",
  errorCode: "READ_ERROR" | "WRITE_ERROR" | "APPEND_ERROR" |
             "DELETE_ERROR" | "CONTAINMENT_ERROR",
  errorBytes: SafeNat,
  errorSha256: Digest
}

CommandSuccess = {
  kind: "command",
  status: "ok",
  exitCode: ExitCode,
  signal: null,
  timedOut: false,
  stdoutBytes: SafeNat,
  stdoutSha256: Digest,
  stderrBytes: SafeNat,
  stderrSha256: Digest
}

CommandFailure = {
  kind: "command",
  status: "error",
  exitCode: ExitCode | null,
  signal: ShortCode | null,
  timedOut: boolean,
  errorCode: "SPAWN_ERROR" | "TIMEOUT" | "UNEXPECTED_EXIT" |
             "CONTAINMENT_ERROR",
  errorBytes: SafeNat,
  errorSha256: Digest,
  stdoutBytes: SafeNat,
  stdoutSha256: Digest,
  stderrBytes: SafeNat,
  stderrSha256: Digest
}
```

For a read success, both output fields are non-null. For write, append, and delete success, both are null. Result kind and file operation equal the current task's normalized action. §7 defines every legal tuple; no other tuple validates.

### 4.3 Blocker

```text
Blocker = {
  kind: "TASK_FAILURE" | "UNKNOWN_OUTCOME",
  taskId: TaskIdText,
  attemptOrdinal: PositiveInt,
  attemptId: Digest,
  reason: "FAILURE_RETRYABLE" | "FAILURE_POLICY_DENIED" |
          "FAILURE_BUDGET_EXHAUSTED" | "UNKNOWN_RETRYABLE" |
          "UNKNOWN_POLICY_DENIED" | "UNKNOWN_BUDGET_EXHAUSTED",
  retryEligible: boolean
}
```

For a just-settled failure or unknown attempt at replay count `c`:

```text
retryEligible = (task.retryable === true) && (c < task.maxAttempts)
```

Reason selection has this exact precedence:

1. if `c >= maxAttempts`, use `*_BUDGET_EXHAUSTED`;
2. else if `retryable === false`, use `*_POLICY_DENIED`;
3. else use `*_RETRYABLE`.

The prefix is `FAILURE` for `FAILURE` and `UNKNOWN` for `UNKNOWN_OUTCOME`; kind is `TASK_FAILURE` or `UNKNOWN_OUTCOME` respectively. Only the third branch has `retryEligible: true`.

## 5. Identity, clock, ownership, admission, and mutation boundaries

### 5.1 Attempt identity

For the newly consumed ordinal:

```text
attemptId = canonicalHash({
  attemptOrdinal,
  planSha256,
  runId,
  taskId
})

idempotencyKey = canonicalHash({
  attemptId,
  kind: "mvp-task-attempt",
  missionId,
  revision
})
```

`runId` is supplied once to initialize, validated as `NonEmptyText`, and immutable. Ordinals are one-based and contiguous per task. Dispatch increments count and persists current before returning and before an effect starts. That ordinal is never refunded or reused.

### 5.2 Infallible clock-adapter boundary

A store owner cannot be constructed with a raw callback. It accepts only an opaque `InfallibleTimestampClockV1` capability issued before store construction by the trusted clock-adapter factory. Its only callable method has this contract:

```text
InfallibleTimestampClockV1.now(): Timestamp   // synchronous, total, never throws
```

The factory takes the underlying time source, calls it once before any checkpoint ownership or store construction, catches every thrown value, and validates the result as `Timestamp`. A throw or invalid initial value returns the construction-only failure `CLOCK_ADAPTER_INVALID`; no store/owner exists, no checkpoint I/O occurs, and this code is not a `StoreErrorCode` or a public store-operation result.

After a valid initial sample, the opaque adapter contains every later source failure: on each call it catches a thrown value and treats a non-`Timestamp` value identically, returning its last valid `Timestamp`; on a valid result it records and returns that result. Therefore `now()` is infallible and Timestamp-only by construction. A syntactically valid result lower than the latest persisted replay timestamp is not repaired by the adapter: the store returns the existing `CLOCK_REGRESSION` no-write error. Test clocks use the same boundary; a finite scripted source repeats its last valid sample after exhaustion. No public store operation can observe an adapter exception or invalid clock value, and no runtime clock error is added.

### 5.3 Field authority

| Authority | Exact ownership |
|---|---|
| Normalized runtime plan | Mission/revision, task order/IDs/titles/dependencies/actions, `maxParallel`, effective retry policy and attempt maxima. |
| Runtime approval | Approval decision and binding to the normalized plan hash. |
| Caller | Checkpoint path, one `runId`, explicit resume request, and raw UTF-8 settlement DTO after the effect settles. |
| Trusted clock adapter | Infallible `Timestamp` values only; source faults and invalid source values never cross its construction boundary. |
| Store | Schema version, hashes, generation, counts, first-ready selection, identities, clock reads, current, all byte counts/digests, settled summaries, blocker, validation, owner/admission/work state, projection, and persisted bytes. |
| Startup recovery | Moves the existing current identity to unknown outcome; it never allocates an ordinal or starts an effect. |

Each store clock result MUST be not less than the latest persisted timestamp in replay order. A valid but regressing timestamp returns `CLOCK_REGRESSION` without mutation.

### 5.4 Orthogonal owner, admission, and work state

The model has three distinct axes. `CLOSING` is not a work state and is not a legal value anywhere.

```text
OwnerState = OPEN | CLOSED
AdmissionState = ACCEPTING | ADMISSION_CLOSED
WorkLifecycle = STARTUP_RECOVERY | IDLE | RUNNING
```

A successfully created owner begins in `OwnerState = OPEN`, `AdmissionState = ACCEPTING`, and exactly one `WorkLifecycle` value:

- `STARTUP_RECOVERY`: only a successful `open` of a validated checkpoint with non-null current enters this state. The persisted current is interrupted and cannot be settled as a live attempt.
- `IDLE`: the validated checkpoint has null current. It may have no blocker, an eligible blocker, a terminal blocker, or all tasks complete.
- `RUNNING`: exactly one current was created by this same live owner's successful `dispatch` and remains unsettled.

The work/checkpoint consistency rule is exact while `OwnerState = OPEN`: `STARTUP_RECOVERY` and `RUNNING` each require non-null current; `IDLE` requires null current. `AdmissionState` is orthogonal to this rule. The first close invocation changes only `AdmissionState` from `ACCEPTING` to `ADMISSION_CLOSED` and appends one close barrier; while that barrier waits, already admitted calls continue to evaluate and evolve the ordinary `WorkLifecycle` exactly as if close had not yet been invoked. No admitted operation transitions to or observes a closing work state.

When the one close barrier executes, it discards the cached checkpoint and expected-generation authority, clears the in-memory work-state authority, and changes `OwnerState` to `CLOSED`. It does not alter checkpoint bytes, persisted current, generation, or any plan/run identity. A closed owner has `AdmissionState = ADMISSION_CLOSED` and no defined/usable `WorkLifecycle`; no public operation can observe a work state after closure.

## 6. Deterministic history replay and state derivation

### 6.1 Replay validator

After structural and checkpoint-identity validation, the validator reconstructs the checkpoint from generation `0`; it never validates history from present-state counts alone.

Initial replay state is: every task count `0`, completed set empty, no current, no blocker, `replayGeneration = 0`, and no last timestamp.

Let the attempt stream be every `settledAttempts` member in stored array order, followed by `current` if non-null. For each settled member `A[i]`:

1. If a replay blocker exists, a later dispatch is legal only when that blocker is retry-eligible. Replay one explicit resume: clear it and add `1` to `replayGeneration`. Otherwise fail `HISTORY_AFTER_TERMINAL`.
2. Compute the ready set from §6.2. Its first plan-order task MUST equal `A[i].taskId`; otherwise fail `HISTORY_READINESS_INVALID`.
3. The ordinal MUST equal replay count plus one and be at most `maxAttempts`; identities MUST recompute exactly. Increment that task's replay count and add `1` to `replayGeneration` for dispatch.
4. `startedAt` MUST be at least the prior replay timestamp; set the timestamp cursor to it.
5. The settled member's repeated current fields MUST equal the dispatched identity. `settledAt` MUST be at least the cursor; set the cursor to it. Validate its exact result tuple.
6. Add `1` to `replayGeneration` for settlement or startup reconciliation. On success, add the task to completed and leave blocker null. On failure or unknown, recompute `retryEligible` and the exact blocker from §4.3 and set that replay blocker. A task already completed cannot appear.

After all settled members:

- If checkpoint `current` is non-null, first apply the same required resume rule, then require the first ready task, next ordinal, identities, and timestamp exactly as steps 2–4; increment its replay count and `replayGeneration` once. Current is therefore necessarily last and has no settlement.
- If checkpoint `current` is null and a replay blocker exists, checkpoint `blocker` either equals it exactly, or is null and the blocker is eligible, in which case replay exactly one final resume and add `1` generation. No other clear is legal.
- If no replay blocker exists, checkpoint `blocker` MUST be null.
- With current present, checkpoint `blocker` MUST be null.
- Replayed counts MUST equal `attemptCounts` exactly.
- Checkpoint `generation` MUST equal `replayGeneration` exactly.

Equivalent generation equation:

```text
D = settledAttempts.length + (current === null ? 0 : 1)
S = settledAttempts.length
E = number of retry-eligible FAILURE/UNKNOWN_OUTCOME members
U = 1 iff blocker is non-null and blocker.retryEligible is true, else 0
R = E - U
generation = D + S + R
```

`R` is the uniquely reconstructable number of explicit resumes. A non-eligible blocker is not counted in `E`. Any underflow, mismatch, alternate ordering, stale blocker, illegal clear, or extra resume fails validation.

Global timestamp order is therefore exactly:

```text
A[0].startedAt <= A[0].settledAt <= A[1].startedAt <= ...
<= lastSettled.settledAt <= current.startedAt
```

Equality is legal. There is no timestamp on resume or close.

### 6.2 Historical readiness and first-ready rule

At any replay point, a task is dependency-ready iff it is not completed, is not current, its replay count is below effective `maxAttempts`, and every normalized dependency is completed. Dispatch is legal only with no current and no blocker. The only dispatch selection is the first dependency-ready task in immutable plan order. Dispatch accepts no task ID.

A completed task is never ready again. For a valid acyclic plan, no-current/no-blocker/incomplete/no-ready is `HISTORY_READINESS_INVALID`.

### 6.3 Derived states

Per-task state is evaluated in this order:

1. `completed` when the task has a success;
2. `running` when it is current;
3. `blocked` when it owns a retry-eligible blocker;
4. `failed` when it owns a non-eligible blocker;
5. `ready` when dependency-ready and there is no current or blocker;
6. otherwise `pending`.

Overall state is:

1. `COMPLETED` iff every task is completed;
2. otherwise `BLOCKED` iff an eligible blocker exists;
3. otherwise `FAILED` iff a non-eligible blocker exists;
4. otherwise `ACTIVE`.

### 6.4 Typed, deterministic snapshot-validation failure

Snapshot validation returns one accepted value or the first error in this fixed stage order:

1. `INVALID_REQUEST` — enclosing operation request closure/scalar failure;
2. `PLAN_INVALID`;
3. `APPROVAL_INVALID`;
4. `PLAN_APPROVAL_MISMATCH`;
5. raw open/read errors in this order: `NOT_FOUND`, `IO_READ_ERROR`, `INVALID_UTF8`, `INVALID_JSON`, `NONCANONICAL_BYTES`;
6. `UNSUPPORTED_SNAPSHOT_VERSION`;
7. `SNAPSHOT_SCHEMA_INVALID` — closed structure, syntactic scalar, or cardinality failure; a syntactically valid `TaskIdText` never fails here for plan non-membership;
8. `IDENTITY_MISMATCH` — root mission/revision/plan hash/approval hash/run ID mismatch; then `attemptCounts` task IDs or order differ from the normalized plan; then, in stored array order and printed field order, any settled/current/blocker task ID is not a plan member. All persisted plan-membership and count-order failures occur here and nowhere else;
9. replay errors in this order at the earliest stream index: `HISTORY_AFTER_TERMINAL`, `HISTORY_READINESS_INVALID`, `HISTORY_ATTEMPT_INVALID`, `HISTORY_TIMESTAMP_INVALID`, `HISTORY_RESULT_INVALID`, `HISTORY_BLOCKER_INVALID`;
10. `HISTORY_LEDGER_INVALID` — final count or consumption mismatch;
11. `HISTORY_GENERATION_MISMATCH`.

Within one stage, array order then field order as printed in the relevant schema selects the first error. No validator may accept two interpretations of the same bytes. A snapshot with coherent replay at another generation passes all eleven stages; only the owner's later cache comparison can return `STALE_GENERATION`. A snapshot whose generation disagrees with its own history returns `HISTORY_GENERATION_MISMATCH` before any stale-cache comparison.

### 6.5 Static generation ceiling; no overflow branch

The closed mission bounds prove a generation ceiling without a runtime overflow error:

- at most `20 tasks × 2 attempts = 40` successful dispatch mutations;
- every dispatched attempt has at most one consuming terminal mutation, either success/failure settlement or startup reconciliation, so settlements plus reconciliations are at most `40`;
- a resume can occur only after a retry-eligible first attempt, at most once per task, so resumes are at most `20`;
- initialize starts at generation `0`, while open/read/status/projection/close/errors add zero.

Therefore every replay-valid checkpoint has `generation = D + S + R <= 40 + 40 + 20 = 100`. Every legal successor is at most `100`, far below `Number.MAX_SAFE_INTEGER`; generation addition cannot overflow. `GENERATION_OVERFLOW` is not a public or internal reachable branch and is absent from `StoreErrorCode`.

## 7. Caller settlement DTOs and exhaustive legal tuples

Raw texts exist only in the request. The store computes byte lengths and hashes and discards raw text after a successful replacement.

```text
SettleSuccessRequestV1 = {
  attemptId: Digest,
  result:
    { kind: "file", operation: "read", outputText: Utf8Text } |
    { kind: "file", operation: "write" } |
    { kind: "file", operation: "append" } |
    { kind: "file", operation: "delete" } |
    {
      kind: "command",
      exitCode: ExitCode,
      signal: null,
      timedOut: false,
      stdoutText: Utf8Text,
      stderrText: Utf8Text
    }
}

SettleFailureRequestV1 = {
  attemptId: Digest,
  result:
    {
      kind: "file",
      operation: FileOperation,
      errorCode: "READ_ERROR" | "WRITE_ERROR" | "APPEND_ERROR" |
                 "DELETE_ERROR" | "CONTAINMENT_ERROR",
      errorText: Utf8Text
    } |
    {
      kind: "command",
      exitCode: ExitCode | null,
      signal: ShortCode | null,
      timedOut: boolean,
      errorCode: "SPAWN_ERROR" | "TIMEOUT" | "UNEXPECTED_EXIT" |
                 "CONTAINMENT_ERROR",
      errorText: Utf8Text,
      stdoutText: Utf8Text,
      stderrText: Utf8Text
    }
}
```

### 7.1 File tuples

| Outcome | Approved operation | Only legal request tuple | Persisted tuple |
|---|---|---|---|
| success | `read` | `read` plus `outputText` | non-null output byte count/hash |
| success | `write`/`append`/`delete` | same operation, no text field | both output fields null |
| failure | `read` | `READ_ERROR` or `CONTAINMENT_ERROR` | same code plus error byte count/hash |
| failure | `write` | `WRITE_ERROR` or `CONTAINMENT_ERROR` | same code plus error byte count/hash |
| failure | `append` | `APPEND_ERROR` or `CONTAINMENT_ERROR` | same code plus error byte count/hash |
| failure | `delete` | `DELETE_ERROR` or `CONTAINMENT_ERROR` | same code plus error byte count/hash |

### 7.2 Command tuples

The command success tuple is legal only when `exitCode === approved expectedExitCode`, `signal === null`, and `timedOut === false`.

| `errorCode` | `exitCode` | `signal` | `timedOut` | Output constraint |
|---|---:|---|---|---|
| `SPAWN_ERROR` | null | null | false | stdout and stderr are exactly empty strings |
| `CONTAINMENT_ERROR` | null | null | false | stdout and stderr are exactly empty strings |
| `TIMEOUT` | null | null | true | either output text may be nonempty |
| `UNEXPECTED_EXIT` | non-null and not the approved expected code | null | false | either output text may be nonempty |
| `UNEXPECTED_EXIT` | null | non-null | false | either output text may be nonempty |

No other success or failure tuple is legal. In particular, exit code and signal cannot both be non-null; a timeout cannot carry either; and an expected exit cannot be settled as `UNEXPECTED_EXIT`.

For each raw text `x`, the store writes `bytes = UTF8(x).length` and `sha256 = SHA256(UTF8(x))`. This applies to read output, command stdout/stderr, and every `errorText`, including empty text. The caller cannot supply any byte count or digest.

## 8. Closed public operation DTOs, errors, owner/admission/work state, and precedence

All success and error envelopes are closed:

```text
Ok<T> = { ok: true, value: T }
Err = { ok: false, error: { code: StoreErrorCode } }
```

`StoreErrorCode` is exactly:

```text
INVALID_REQUEST | PLAN_INVALID | APPROVAL_INVALID | PLAN_APPROVAL_MISMATCH |
ALREADY_EXISTS | NOT_FOUND | IO_READ_ERROR | INVALID_UTF8 | INVALID_JSON |
NONCANONICAL_BYTES | UNSUPPORTED_SNAPSHOT_VERSION | SNAPSHOT_SCHEMA_INVALID |
IDENTITY_MISMATCH | HISTORY_AFTER_TERMINAL | HISTORY_READINESS_INVALID |
HISTORY_ATTEMPT_INVALID | HISTORY_TIMESTAMP_INVALID | HISTORY_RESULT_INVALID |
HISTORY_BLOCKER_INVALID | HISTORY_LEDGER_INVALID |
HISTORY_GENERATION_MISMATCH | STALE_GENERATION | RECONCILIATION_REQUIRED |
RECONCILIATION_NOT_REQUIRED | CURRENT_ATTEMPT_EXISTS | CLOCK_REGRESSION |
PERSISTENCE_ERROR | NO_WORK | RUN_BLOCKED | RUN_FAILED | NO_CURRENT |
ATTEMPT_MISMATCH | RESULT_INVALID | RESUME_NOT_ELIGIBLE | UNKNOWN_TASK |
STORE_CLOSED
```

Every ordinary operation error performs no target replacement and leaves authoritative target bytes, persisted generation, owner `expectedGeneration`, any cached validated checkpoint, and `WorkLifecycle` unchanged. A pre-rename persistence failure is `PERSISTENCE_ERROR`. Queue bookkeeping used to deliver an error is not authoritative checkpoint/cache/work state. Invocation-time `STORE_CLOSED` likewise performs no admission, I/O, clock access, request validation, cache/generation/work-state mutation, or barrier insertion. The close barrier's owner/cache effects are specified separately in §8.4 and are not an error branch.

The following names are exact closed code sets used by the operation table:

```text
INPUT_ERRORS = INVALID_REQUEST | PLAN_INVALID | APPROVAL_INVALID |
               PLAN_APPROVAL_MISMATCH

SNAPSHOT_ERRORS = NOT_FOUND | IO_READ_ERROR | INVALID_UTF8 | INVALID_JSON |
                  NONCANONICAL_BYTES | UNSUPPORTED_SNAPSHOT_VERSION |
                  SNAPSHOT_SCHEMA_INVALID | IDENTITY_MISMATCH |
                  HISTORY_AFTER_TERMINAL | HISTORY_READINESS_INVALID |
                  HISTORY_ATTEMPT_INVALID | HISTORY_TIMESTAMP_INVALID |
                  HISTORY_RESULT_INVALID | HISTORY_BLOCKER_INVALID |
                  HISTORY_LEDGER_INVALID | HISTORY_GENERATION_MISMATCH

OWNER_READ_ERRORS = SNAPSHOT_ERRORS | STALE_GENERATION
MUTATION_STORAGE_ERRORS = OWNER_READ_ERRORS | PERSISTENCE_ERROR
CLOCKED_MUTATION_ERRORS = MUTATION_STORAGE_ERRORS | CLOCK_REGRESSION
```

A set name expands only to the listed codes; it is not an open category.

### 8.1 Request and success schemas

```text
InitializeRequestV1 = {
  checkpointPath: CheckpointPath,
  plan: RuntimePlanV1,
  approval: RuntimeApprovalV1,
  runId: NonEmptyText
}
InitializeValueV1 = { checkpoint: CheckpointV2 }

OpenRequestV1 = {
  checkpointPath: CheckpointPath,
  plan: RuntimePlanV1,
  approval: RuntimeApprovalV1,
  runId: NonEmptyText
}
OpenValueV1 = {
  checkpoint: CheckpointV2,
  reconciliationRequired: boolean
}

ReadRequestV1 = {}
ReadValueV1 = { checkpoint: CheckpointV2 }

DispatchRequestV1 = {}
DispatchValueV1 = { current: CurrentAttempt, generation: SafeNat }

SettleSuccessValueV1 = { attempt: SuccessAttempt, generation: SafeNat }
SettleFailureValueV1 = { attempt: FailureAttempt, blocker: Blocker, generation: SafeNat }

RestartReconciliationRequestV1 = {}
RestartReconciliationValueV1 = {
  reconciled: true,
  attempt: UnknownOutcomeAttempt,
  blocker: Blocker,
  generation: SafeNat
}

ResumeRequestV1 = { blockerAttemptId: Digest }
ResumeValueV1 = { generation: SafeNat }

StatusRequestV1 = { taskId: TaskIdText | null }
StatusValueV1 = {
  generation: SafeNat,
  overallState: "ACTIVE" | "BLOCKED" | "FAILED" | "COMPLETED",
  task: {
    taskId: PlanTaskId,
    state: "pending" | "ready" | "running" | "completed" | "blocked" | "failed",
    attemptCount: SafeNat,
    maxAttempts: 1 | 2,
    exhausted: boolean
  } | null
}

ProjectionRequestV1 = {}
ProjectionValueV1 = { projection: StoreProjectionV1 }

CloseRequestV1 = {}
CloseValueV1 = { closed: true }
```

There is no successful no-op reconciliation response. Reconciliation is a startup-recovery mutation or the exact no-write error `RECONCILIATION_NOT_REQUIRED`.

### 8.2 Total ordinary work-lifecycle transition table

`initialize` and `open` are factory operations: no owner exists before success, so no live-current or admission branch applies to them. They cannot be invoked on an existing owner. On success they create `OwnerState = OPEN`, `AdmissionState = ACCEPTING`, and the stated ordinary work state.

The table below applies only to a non-close call atomically admitted while the owner is `OPEN/ACCEPTING`. Once admitted, a call executes its row against the `WorkLifecycle` produced by all earlier admitted calls. It does so even if close later changes admission to `ADMISSION_CLOSED` while this call is queued. Every owner operation has an explicit branch for both kinds of live current: interrupted startup current (`STARTUP_RECOVERY`) and same-owner live current (`RUNNING`). Admission and owner state never replace a `WorkLifecycle` cell.

| Operation | `STARTUP_RECOVERY` (interrupted current) | `IDLE` (no current) | `RUNNING` (same-owner current) | Success transition |
|---|---|---|---|---|
| `read` | `RECONCILIATION_REQUIRED` | success | success, including current | no work-state change |
| `dispatch` | `RECONCILIATION_REQUIRED` | dispatch or state error | `CURRENT_ATTEMPT_EXISTS` | `IDLE -> RUNNING` |
| `settleSuccess` | `RECONCILIATION_REQUIRED` | `NO_CURRENT` | settle matching current | `RUNNING -> IDLE` |
| `settleFailure` | `RECONCILIATION_REQUIRED` | `NO_CURRENT` | settle matching current | `RUNNING -> IDLE` |
| `restartReconciliation` | reconcile interrupted current | `RECONCILIATION_NOT_REQUIRED` | `RECONCILIATION_NOT_REQUIRED` | `STARTUP_RECOVERY -> IDLE` |
| `resume` | `RECONCILIATION_REQUIRED` | resume or blocker error | `CURRENT_ATTEMPT_EXISTS` | `IDLE -> IDLE` |
| `status` | `RECONCILIATION_REQUIRED` | success or `UNKNOWN_TASK` | success or `UNKNOWN_TASK`, including running state | no work-state change |
| `projection` | `RECONCILIATION_REQUIRED` | success | success, including current | no work-state change |

A dispatch admitted behind an earlier successful dispatch executes in `RUNNING` and returns exactly `CURRENT_ATTEMPT_EXISTS`. It does not fall through to readiness, blocker, `NO_WORK`, or clock stages. Resume in `RUNNING` likewise returns exactly `CURRENT_ATTEMPT_EXISTS`. Reconciliation is legal only in `STARTUP_RECOVERY`; in both `IDLE` and `RUNNING` it returns exactly `RECONCILIATION_NOT_REQUIRED`. Each is an executable no-write branch with unchanged bytes/cache/generation/work state. These rules remain exact when admission has closed after the calls were admitted.

### 8.3 Total operation table

For every owner operation other than close, the listed branches are reachable only after invocation-time admission succeeds. A call invoked after `AdmissionState` becomes `ADMISSION_CLOSED`, or after `OwnerState` becomes `CLOSED`, instead returns only `STORE_CLOSED` under §§8.4–8.5 and never reaches this table. A previously admitted call still reaches this table.

| Operation | Exact success branch | Generation/write | Exact operation-specific errors |
|---|---|---|---|
| `initialize` | Validate/normalize plan and approval; require absent target; create exact zero-count, empty-history, null-current/null-blocker checkpoint and `OPEN/ACCEPTING/IDLE` owner. | Generation `0`; one atomic create settlement. | `INPUT_ERRORS | ALREADY_EXISTS | PERSISTENCE_ERROR`. No owner on error. |
| `open` | Strictly open and replay-validate exact identity; acquire `OPEN/ACCEPTING` owner. Return `reconciliationRequired:true` and `STARTUP_RECOVERY` iff current exists; otherwise false and `IDLE`. | `+0`; never writes. | `INPUT_ERRORS | SNAPSHOT_ERRORS`. No owner on error. |
| `read` | Admitted in `IDLE` or `RUNNING`, re-read and return immutable validated checkpoint. | `+0`; no write. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | OWNER_READ_ERRORS`. |
| `dispatch` | Admitted in `IDLE`/ACTIVE, auto-select first ready task; increment count; derive identity; persist current; return after replacement. Request has no `taskId`. | Exactly `+1`. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | CURRENT_ATTEMPT_EXISTS | RUN_BLOCKED | RUN_FAILED | NO_WORK | CLOCKED_MUTATION_ERRORS`. |
| `settleSuccess` | Admitted in `RUNNING`, require matching current attempt ID and legal raw success; compute summaries; append success and clear current. | Exactly `+1`. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | NO_CURRENT | ATTEMPT_MISMATCH | RESULT_INVALID | CLOCKED_MUTATION_ERRORS`. |
| `settleFailure` | Admitted in `RUNNING`, require matching current attempt ID and legal raw failure; compute summaries; append failure, clear current, and persist exact blocker. | Exactly `+1`. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | NO_CURRENT | ATTEMPT_MISMATCH | RESULT_INVALID | CLOCKED_MUTATION_ERRORS`. |
| `restartReconciliation` | Admitted only in `STARTUP_RECOVERY`, move current identity to unknown with store time, persist blocker, clear current, and enter `IDLE`. | Exactly `+1`. | `INVALID_REQUEST | RECONCILIATION_NOT_REQUIRED | CLOCKED_MUTATION_ERRORS`. On error work state remains unchanged. |
| `resume` | Admitted in `IDLE`, require matching eligible blocker and clear only blocker. It allocates no identity and starts no effect. | Exactly `+1`. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | CURRENT_ATTEMPT_EXISTS | RESUME_NOT_ELIGIBLE | ATTEMPT_MISMATCH | MUTATION_STORAGE_ERRORS`. |
| `status` | Admitted in `IDLE` or `RUNNING`, return overall state and, for a non-null member task ID, exact task state and `exhausted = (attemptCount === maxAttempts)`; null returns null task. | `+0`; no write. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | UNKNOWN_TASK | OWNER_READ_ERRORS`. |
| `projection` | Admitted in `IDLE` or `RUNNING`, return exactly §9. | `+0`; no write. | `INVALID_REQUEST | RECONCILIATION_REQUIRED | OWNER_READ_ERRORS`. No partial projection. |
| `close` | First invocation atomically closes admission and appends the one barrier; all close invocations share that barrier's eventual `{closed:true}`. | `+0`; barrier performs no checkpoint I/O/write and does not change generation. | None. Repeated/concurrent close has no second barrier or other work. |

### 8.4 FIFO admission, close barrier, failures, and executable trace

#### 8.4.1 Atomic invocation rules

While `OwnerState = OPEN` and `AdmissionState = ACCEPTING`, every non-close invocation atomically receives the next monotonically increasing in-memory queue sequence and is admitted before its first asynchronous step. Its result is thereafter governed by the ordinary pipeline and evolving `WorkLifecycle`, not by a later admission-state change.

The first `close` invocation atomically performs one indivisible admission action relative to all invocations: it changes `AdmissionState` from `ACCEPTING` to `ADMISSION_CLOSED`, creates the one shared close completion, and appends exactly one close barrier at the next FIFO queue position. Therefore the barrier is after every call already admitted and before no ordinary call. The first close invocation does not change `WorkLifecycle`, `OwnerState`, cache, expected generation, checkpoint bytes, or generation.

A non-close call whose invocation linearizes after admission closes returns `STORE_CLOSED` immediately. It receives no queue sequence, performs no request validation, clock call, filesystem I/O, cache/generation/work-state mutation, or checkpoint work. The same rule applies after `OwnerState = CLOSED`.

A concurrent or later `close` invocation never enters the queue and never creates another barrier. It returns the same shared completion/result as the first invocation. Before the barrier settles, it observes the same pending completion; after settlement, it observes the same settled `{closed:true}` result. This identity/idempotence rule has no additional I/O, validation, mutation, or generation effect.

#### 8.4.2 FIFO execution and failure semantics

The queue executes alone in sequence order. Every pre-close admitted ordinary call executes before the barrier against the ordinary `WorkLifecycle`, checkpoint/cache, and expected generation produced by all earlier calls. A successful call may evolve normal work state. An errored call returns the first ordinary error selected by §8.5 and, under the unchanged-on-error rule, leaves ordinary authoritative state unchanged. In either case the FIFO immediately continues to the next admitted item; an error never cancels, poisons, or skips later admitted calls.

Consequently, if a pre-close operation fails, a later pre-close admitted operation still executes. It is judged at its turn by its own request, owner read, current `WorkLifecycle`, and ordinary guards; it may succeed or return its own guard/semantic/storage error. The earlier failure does not replace the later result. The close barrier executes after every such admitted call has settled, regardless of how many returned errors.

When the barrier reaches the head, it performs no checkpoint validation, clock call, checkpoint read, checkpoint replacement, checkpoint write, or generation change. It discards the cached validated checkpoint and expected-generation authority, clears in-memory work-state authority, atomically sets `OwnerState = CLOSED`, and settles the one shared close completion as `{closed:true}`. A persisted live current is intentionally left for a later owner's startup recovery. No failure of an earlier operation can cause the barrier to fail.

#### 8.4.3 Executable acceptance trace

Use an `OPEN/ACCEPTING/IDLE` owner at generation `0` with one ready task and a deferred filesystem/queue spy.

| Step | Invocation/admission assertion | Deferred execution/result assertion |
|---:|---|---|
| 1 | Invoke mutation A = `dispatch({})`; atomically admit it as queue sequence `q`. Pause before its first I/O. | None yet; owner remains `OPEN/ACCEPTING/IDLE`, generation `0`. |
| 2 | Invoke call B = `read({})`; atomically admit it as `q+1`. | None yet. |
| 3 | Invoke first `close({})`; atomically set `ADMISSION_CLOSED`, create the shared close completion, and append exactly one barrier as `q+2`. `OwnerState` remains `OPEN`; work state remains `IDLE`. | Close completion remains pending. |
| 4 | Invoke later call C = `status({taskId:null})`; return exactly `STORE_CLOSED` without queue admission, request validation, clock/I/O, or any cache/generation/work-state change. | Queue is still exactly A, B, one barrier. |
| 5 | Release A. It executes under ordinary `IDLE`, persists the first current, advances generation to `1`, returns dispatch success, and changes work state `IDLE -> RUNNING`. | Admission remains closed; owner remains open. |
| 6 | B executes next under the evolved ordinary `RUNNING` state, re-reads generation `1`, and returns the checkpoint including current at `+0`; no `STORE_CLOSED` recheck occurs. | Work state remains `RUNNING`. |
| 7 | The barrier executes, performs zero checkpoint I/O/write and no generation change, discards cache/expected-generation/work-state authority, sets owner `CLOSED`, and settles the shared result `{closed:true}`. | Persisted generation is still `1`, with current intact for later startup recovery. |
| 8 | Invoke `close({})` again. | Receive the identical already-settled shared completion/result; queue/barrier count stays one and all I/O/mutation spies stay zero. |

A required companion variant makes A return an injected `PERSISTENCE_ERROR`: B still executes next against unchanged `IDLE` and returns its ordinary read result unless its own guard/I/O rejects; the barrier still executes and closes. This variant proves exact failure continuation rather than merely the success interleaving.

### 8.5 Deterministic public-operation error precedence

Factory operations use the validation stage order in §6.4; `initialize` then tests target absence/persistence, while `open` completes strict snapshot validation before creating an owner.

For an owner invocation, admission selection is atomic and precedes every ordinary error:

1. A repeated/concurrent `close` returns the existing shared close completion/result. It is not an ordinary admission attempt.
2. A first `close` on `OPEN/ACCEPTING` atomically closes admission and appends the one barrier as §8.4. It has no request-validation or ordinary-operation error branch.
3. A non-close invocation on `OPEN/ACCEPTING` is admitted and assigned its FIFO sequence. That admission decision is final: it will not be rechecked when the call later executes.
4. A non-close invocation after admission has closed, including after owner closure, returns `STORE_CLOSED` before all request, lifecycle, clock, and I/O branches. `STORE_CLOSED` therefore cannot replace any result of a call already admitted.

For every admitted non-close owner operation, exactly this execution-time order selects one result:

1. **Request syntax:** validate the operation's closed raw request. Failure is `INVALID_REQUEST`. A syntactically valid status `TaskIdText` is not checked for plan membership here.
2. **Owner read:** re-read canonical bytes and apply §6.4 through `HISTORY_GENERATION_MISMATCH`.
3. **Cache generation:** compare validated disk generation to `expectedGeneration`; inequality is `STALE_GENERATION`. This stage is unreachable when disk generation is incoherent with its own replay, because that already returned `HISTORY_GENERATION_MISMATCH`.
4. **Work lifecycle/current:** apply the exact row in §8.2 using the state left by earlier admitted calls. In particular, startup restrictions precede operation semantics; `RUNNING` dispatch/resume return `CURRENT_ATTEMPT_EXISTS`; reconciliation outside startup returns `RECONCILIATION_NOT_REQUIRED`; and `IDLE` settlement returns `NO_CURRENT`.
5. **Operation semantics:**
   - dispatch: `RUN_BLOCKED`, then `RUN_FAILED`, then `NO_WORK`, else selected work;
   - settlement in `RUNNING`: `ATTEMPT_MISMATCH` before `RESULT_INVALID`;
   - resume in `IDLE`: `RESUME_NOT_ELIGIBLE` when blocker is absent or non-eligible, otherwise `ATTEMPT_MISMATCH` for the wrong blocker ID;
   - status: a non-null syntactically valid `TaskIdText` not equal to a normalized plan task ID returns `UNKNOWN_TASK`. This is the only request-membership error and cannot overlap `INVALID_REQUEST` or persisted `IDENTITY_MISMATCH`.
6. **Clock:** only a selected dispatch, valid settlement, or legal startup reconciliation calls the infallible adapter; a valid regressing timestamp returns `CLOCK_REGRESSION`. Resume has no clock.
7. **Successor/persistence:** construct the unique `+1` replay-valid successor, validate it in memory, perform atomic replacement, then update cache and work state. A required pre-rename failure is `PERSISTENCE_ERROR`.

No later error may replace an earlier error. An error settles only its own queue item; FIFO then evaluates the next admitted item under this same ordering. The barrier uses §8.4 only and completes after all earlier admitted items regardless of their outcomes.

### 8.6 Internal expected generation

A successful initialize/open caches `expectedGeneration`. At execution time, every admitted ordinary owner operation re-reads and fully validates the target before comparing disk generation to that cache, even if admission has since closed. A mutator constructs the unique replay-valid successor at exactly `expectedGeneration + 1`, atomically replaces, and updates `expectedGeneration`, any cached checkpoint, and `WorkLifecycle` only after rename succeeds. Pure/error branches do not update them. The close barrier runs only after all admitted ordinary operations; it then discards the cache and expected-generation authority without reading or writing the checkpoint. The static proof in §6.5 eliminates any overflow branch. This is same-owner stale-state detection, not cross-process CAS.

## 9. One store-owned projection DTO

```text
StoreProjectionV1 = {
  format: "durable-agent-store-projection/1",
  plan: {
    missionId: NonEmptyText,
    revision: PositiveInt,
    planSha256: Digest,
    approvalSha256: Digest,
    maxParallel: 1
  },
  run: {
    runId: NonEmptyText,
    generation: SafeNat,
    state: "ACTIVE" | "BLOCKED" | "FAILED" | "COMPLETED"
  },
  tasks: ProjectionTaskV1[plan.tasks.length],
  blocker: Blocker | null
}

ProjectionTaskV1 = {
  taskId: PlanTaskId,
  title: NonEmptyText,
  dependencies: PlanTaskId[],
  action: FileActionV1 | CommandActionV1,
  maxAttempts: 1 | 2,
  retryable: boolean,
  attemptCount: SafeNat,
  exhausted: boolean,
  state: "pending" | "ready" | "running" | "completed" | "blocked" | "failed",
  settledAttempts: SettledAttempt[0..2],
  current: CurrentAttempt | null
}
```

The projection is a pure value derived only from the normalized plan and validated checkpoint. Task rows are in plan order. Dependencies are normalized plan order. A row's settled attempts are filtered from global dispatch order and therefore have increasing task ordinal; current appears only in its owning row. `exhausted` is exact count equality. Repeated projection of equal normalized plan and checkpoint values returns deeply equal DTO values and performs no mutation, reconciliation, resume, effect inspection, or acceptance inference.

This is the store baseline's only report boundary. Exact JSON serialization, a JSON report schema, Markdown structure/escaping/newlines, byte-exact rendering, and JSON/Markdown agreement are explicitly outside this baseline. A separately frozen integration/report contract is required before `integrate-mvp`. This baseline makes no byte-exact Markdown claim.

## 10. Canonical bytes, strict open, and replacement

Serialization is pinned to the existing `src/domain/runtime.ts` `canonicalJson` behavior:

- `null`, booleans, strings, and finite JSON numbers use JSON encoding; `-0` and non-finite numbers fail;
- arrays preserve index order and reject holes, symbol keys, and extra properties;
- plain or null-prototype objects only; own string keys sort lexicographically at every level; symbol keys fail;
- unsupported values/prototypes and cycles fail;
- output contains no insignificant whitespace.

Checkpoint bytes are exactly `UTF8(canonicalJson(checkpoint))`: no BOM and no trailing newline. Open and every re-read reject invalid UTF-8, duplicate/noncanonical spellings, parse failure, whitespace, BOM, trailing newline, or any bytes unequal to exact re-encoding.

Replacement uses a unique same-directory temporary file opened with exclusive create and mode `0600`, writes all canonical bytes, syncs the file, closes it, and renames it over the target. Best-effort temporary cleanup follows pre-rename failure. Successful rename is the settlement boundary and last fallible required step. Directory sync is not a required step and carries no success or failure claim. Any required failure before rename returns `PERSISTENCE_ERROR`; the prior target remains authoritative. Orphan temporary files are never checkpoints. Power-loss behavior is not claimed.

## 11. Normative invariants

- **I-01 Runtime input/approval:** only normalized `RuntimePlanV1` and matching `RuntimeApprovalV1` bind a run; neither is `dsh-wbs/1`.
- **I-02 Closed checkpoint/version and syntactic IDs:** every loaded/pre-write value is exactly raw `CheckpointV2`; only literal version `2` is accepted; raw task IDs are syntactic `TaskIdText` until the identity stage.
- **I-03 Immutable identity/order:** plan, approval, run, plan membership, task IDs, count order, and plan order are exact and immutable; persisted membership/order failures are only `IDENTITY_MISMATCH`, while status request non-membership is only `UNKNOWN_TASK`.
- **I-04 Replay/generation:** history reconstructs uniquely from generation `0`, and the mutation equation equals persisted generation.
- **I-05 Ledger/current-last:** consumed attempts are exactly settled plus optional last current; ordinals/identities/counts are contiguous and exact.
- **I-06 Global timestamps and clock boundary:** all persisted times follow one nondecreasing replay sequence and come only from a preconstructed infallible Timestamp-only adapter; valid regression is a handled no-write error.
- **I-07 Result tuples:** every result is exactly one action-matching legal tuple with all byte fields present and valid.
- **I-08 Retry/blocker:** eligibility formula, reason precedence, blocker presence, and blocker clearing are exact; retry is never automatic.
- **I-09 Historical readiness/non-replay:** each historical and new dispatch is the first dependency-ready task; success is never replayed.
- **I-10 Derived states:** task/run state and exhaustion are derived only by §§6.2–6.3 and status equality.
- **I-11 Settlement authority:** callers supply raw UTF-8 text; the store alone computes byte counts and digests.
- **I-12 Total mutation/no-write and bounded generation:** each successful mutator advances exactly once; initialize is zero; pure/error/close advances zero and preserves checkpoint bytes/generation; legal generation is statically bounded by `100` and has no overflow error. Ordinary errors preserve cache/work state; the close barrier alone discards cache/work authority without checkpoint I/O.
- **I-13 Orthogonal owner/admission/work state and FIFO close:** ordinary work state is exactly `STARTUP_RECOVERY | IDLE | RUNNING`, never `CLOSING`; owner and admission are separate. First close atomically disables admission and appends one barrier after all admitted calls. Those calls continue in FIFO against evolving normal work state despite admission closure; their errors do not stop later items. Post-close invocations return `STORE_CLOSED` before admission/I/O/mutation. The barrier always closes the owner, discards cache/authority, writes no checkpoint, changes no generation, and is shared by every close invocation.
- **I-14 Internal generation check:** every admitted ordinary owner operation first validates disk history, then compares its replay-valid generation to internal expected generation; the barrier runs only afterward and discards that authority.
- **I-15 Canonical replacement:** exact canonical bytes and synced-temp same-directory rename define persistence settlement.
- **I-16 Startup recovery:** only reconciliation in `STARTUP_RECOVERY` converts current to one consuming unknown outcome; reconciliation elsewhere is one no-write error and never runs an effect.
- **I-17 Projection boundary:** one closed, plan-order, deterministic, pure DTO is owned; renderer bytes are not.
- **I-18 Scope/migration:** no migration, cross-process lock/CAS, distributed lease, generic execution store, or power-loss guarantee is introduced.

## 12. Acceptance-to-evidence matrix

Every case record MUST cite this artifact and the coordinator-resolved `CURRENT_BASELINE_SHA256_RECORD`. “Ordinary unchanged” means exact target bytes, persisted generation, owner expected-generation/cache, and `WorkLifecycle` are unchanged. “Invocation rejection unchanged” additionally means no queue sequence/admission and no owner/admission mutation. Fixtures use a matching normalized runtime plan/approval unless the row says otherwise.

For every owner-operation row below, its ordinary positive/negative branches are invoked and admitted while `OwnerState = OPEN` and `AdmissionState = ACCEPTING`; once admitted they execute against the evolving normal `WorkLifecycle` even if close has since set `ADMISSION_CLOSED`. Every owner-operation suite also applies the shared post-admission-close assertion: an invocation after the close linearization returns only `STORE_CLOSED`, receives no sequence, and performs no validation, clock, I/O, cache/generation/work-state mutation. Factory rows have no owner/admission precondition. Rows unaffected by F-V4-001 retain their v3/v4 case IDs and assertions; the coupled owner/admission/close rows are regenerated as `V5-*`.

| Row | Case IDs and exact inputs/assertions | Required evidence |
|---|---|---|
| I-01 | `V3-I01-P`: input with omitted attempt fields normalizes to `1,false`; input with `maxAttempts:2` and omitted retryable normalizes to `2,true`; approval hashes/binds the normalized plan. `V3-I01-N`: a `format:"dsh-wbs/1"`, mismatched hash, or `1,true` task returns the specified plan/approval error before file I/O. | Normalization/hash vectors and closed-schema tests. |
| I-02 | `V4-I02-P`: minimal canonical v2 checkpoint with syntactic member `TaskIdText` validates. `V4-I02-N`: independently add, omit, mistype, illegally null, use a syntactically invalid ID, or set version `1`/`3`; assert structural/version error. A syntactically valid non-member ID passes schema then returns `IDENTITY_MISMATCH`, never `SNAPSHOT_SCHEMA_INVALID`. | Table-driven schema/version/stage fixtures. |
| I-03 | `V4-I03-P`: first and last count entries match plan order; all settled/current/blocker IDs are members; both hashes/run ID open. `V4-I03-N`: alter each root identity, reorder counts, or substitute a syntactically valid non-member ID in every persisted ID position; assert only `IDENTITY_MISMATCH`. Status with the same non-member text asserts only `UNKNOWN_TASK` after a valid owner read. | Identity mutation and status-membership fixtures. |
| I-04 | `V3-I04-P`: histories with zero attempts, one success, eligible failure+resume+retry, and current satisfy `D+S+R`. `V3-I04-N`: set generation one below/above or omit the implied resume; assert `HISTORY_GENERATION_MISMATCH`. | Replay oracle plus generation vectors. |
| I-05 | `V3-I05-P`: two attempts of one task are ordinals 1/2 with recomputed IDs; current follows every settled member. `V3-I05-N`: skip/repeat ordinal, forge ID, mismatch count, duplicate current as settled, or place an attempt after success; assert exact replay code. | Ledger/identity mutation tests. |
| I-06 | `V4-I06-P`: trusted factory accepts a valid initial Timestamp; equal and increasing values persist; a scripted source repeats its final value after exhaustion. `V4-I06-N`: initial throw/invalid value yields construction-only `CLOCK_ADAPTER_INVALID` before owner/I/O; later throw/invalid value is contained and returns last valid Timestamp; a valid regression returns `CLOCK_REGRESSION` with unchanged state. Assert no public operation throws or returns an unlisted clock code. | Factory, adapter containment, deterministic timestamp, and operation no-throw tests. |
| I-07 | `V3-I07-P`: instantiate every file row and five command-failure rows from §7 plus command success. `V3-I07-N`: vary one tuple coordinate, action kind/operation, expected exit, null, or extra field; assert `RESULT_INVALID` on settlement and `HISTORY_RESULT_INVALID` on open. | Exhaustive cross-product table test. |
| I-08 | `V3-I08-P`: counts below max with policy true yield `*_RETRYABLE`; false policy below max yields `*_POLICY_DENIED`; count at max yields `*_BUDGET_EXHAUSTED` even when policy is false. `V3-I08-N`: stale/missing blocker, cleared non-eligible blocker, or later attempt after non-eligible blocker fails exact history code. | Retry/blocker precedence table and replay tests. |
| I-09 | `V3-I09-P`: in a DAG with two ready tasks, every historical/new dispatch uses the first plan-order ready task. `V3-I09-N`: forge a later ready task, unmet dependency, exhausted task, or completed task in history; assert `HISTORY_READINESS_INVALID`. | DAG replay/dispatch tests; no caller-choice case. |
| I-10 | `V3-I10-P`: representative zero/current/eligible-blocker/noneligible-blocker/all-success snapshots derive exact task/run states and exhaustion equality. `V3-I10-N`: incomplete no-current/no-blocker acyclic snapshot with no ready task fails readiness validation. | Pure state/status vectors. |
| I-11 | `V3-I11-P`: non-ASCII and empty raw text produce exact UTF-8 counts and known SHA-256 fields. `V3-I11-N`: a request containing caller-supplied bytes/digest is `INVALID_REQUEST`. | UTF-8 golden vectors and DTO closure tests. |
| I-12 | `V5-I12-P`: dispatch, each settlement, startup reconciliation, and resume each add one; initialize is zero; construct the legal maximum of 40 dispatches, 40 consuming settlements/reconciliations, and 20 resumes and assert generation exactly `100`. `V5-I12-B`: every pure/error branch and the close barrier add zero and preserve exact checkpoint bytes/generation; ordinary errors preserve cache/work state, while the barrier alone discards cache/authority. Static inspection asserts `GENERATION_OVERFLOW` and `CLOSING` absent from code/type/error maps. | Transition assertions, max-bound replay vector, pre-rename fault injection, barrier authority spy, and static symbol inspection. |
| I-13 | `V5-I13-P`: execute every §8.2 cell under `OPEN/ACCEPTING`; then execute the exact §8.4.3 A/B/close/C trace, proving A and B evolve `IDLE -> RUNNING`, C is unadmitted `STORE_CLOSED`, and the one barrier closes/discards after B. `V5-I13-F`: inject A `PERSISTENCE_ERROR`; prove B still executes under unchanged `IDLE`, later admitted guard errors remain their own, and barrier still settles. `V5-I13-B`: concurrent/repeated close returns the same pending/settled completion with one barrier. | Work-lifecycle table suite, linearized admission harness, deferred-I/O FIFO spy, failure-continuation trace, and shared-completion identity assertion. |
| I-14 | `V5-I14-P`: each admitted ordinary owner operation succeeds when disk and cache generations match, including execution after admission closes. `V5-I14-N1`: starting from owner cache generation `0`, externally replace bytes with a canonical replay-valid generation-`1` successor containing the correctly derived first current attempt; next admitted owner operation passes replay and returns `STALE_GENERATION`, ordinary state unchanged. `V5-I14-N2`: alter only generation on otherwise unchanged history; assert `HISTORY_GENERATION_MISMATCH`, not stale. Barrier then discards cache/expected-generation without I/O. | Canonical successor stale fixture, separate incoherent-history fixture, and post-queue barrier authority spy. |
| I-15 | `V3-I15-P`: persisted bytes equal exact runtime canonical JSON and trace exclusive temp/create-write-sync-close-rename. `V3-I15-N`: BOM, whitespace, newline, noncanonical spelling, or injected required pre-rename failure is rejected and old target remains exact. | Golden-byte and filesystem fault tests; implementation inspection. |
| I-16 | `V5-I16-P`: open current into `OPEN/ACCEPTING/STARTUP_RECOVERY`, reconcile once, and assert same identity becomes one unknown, current clears, exact blocker appears, generation +1, work state `IDLE`, and effect spy zero. `V5-I16-N`: reconcile in both `IDLE` and `RUNNING` returns only `RECONCILIATION_NOT_REQUIRED`; startup clock/persistence failure preserves startup work state/current/bytes/cache. An admitted reconciliation retains these semantics after admission closes. | Startup recovery, no-write branch, queued-close, and fault tests. |
| I-17 | `V3-I17-P`: exact projection contains identity, state, plan-order rows, normalized actions/dependencies, per-task ordinal attempts/current, exhaustion, and blocker. `V3-I17-N`: invalid/stale/recovery-required input returns no partial DTO and no write. | Deep-equality projection fixtures and purity spy; no renderer golden. |
| I-18 | `V3-I18-P`: fresh literal v2 initializes without predecessor import. `V3-I18-N`: absent/v1/future version fails without write; review finds no lock, multi-owner CAS, lease, migration, or power-loss claim. | Version tests and scope inspection. |
| OP-INITIALIZE | `V5-OP-INIT-P`: with preconstructed valid clock, absent target + one-task plan + matching approval + run ID yields generation-0 exact empty checkpoint and `OPEN/ACCEPTING/IDLE` owner. `V5-OP-INIT-N`: existing target yields `ALREADY_EXISTS`; invalid plan/approval yields its typed error; no owner/write. Factory clock failure occurs before this operation exists. | Factory/operation test. |
| OP-OPEN | `V5-OP-OPEN-P`: valid no-current bytes return `OPEN/ACCEPTING/IDLE`/false; valid current returns `OPEN/ACCEPTING/STARTUP_RECOVERY`/true at unchanged generation. `V5-OP-OPEN-N`: missing, invalid bytes, cross-identity, or impossible history returns exact typed error and no owner/write. | Raw-open, identity-stage, and replay tests. |
| OP-READ | `V5-OP-READ-P`: admitted in `IDLE` and `RUNNING`, including before close but executed after admission closes, returns immutable validated checkpoints at unchanged generation. `V5-OP-READ-N`: startup recovery, canonical replay-valid stale successor, or malformed disk returns exact precedence error, ordinary state unchanged; post-close invocation is unadmitted `STORE_CLOSED`. | Lifecycle/read/purity and queued-close test. |
| OP-DISPATCH | `V5-OP-DISPATCH-P`: admitted empty `{}` in `IDLE` auto-selects first ready, consumes next ordinal, enters `RUNNING`, and rename finishes before effect spy may start, including when close queues behind it. `V5-OP-DISPATCH-N`: startup/blocked/failed/completed branches return exact error; a dispatch admitted behind a successful dispatch returns only `CURRENT_ATTEMPT_EXISTS`; a post-close invocation returns `STORE_CLOSED` before validation/I/O. | Ordering spy, queue race, close interleaving, and every lifecycle/state branch. |
| OP-SETTLE-SUCCESS | `V5-OP-SS-P`: admitted in `RUNNING`, matching attempt and every legal success input persist exact computed summary, clear current, enter `IDLE`, generation +1, including if admission closes before execution. `V5-OP-SS-N`: startup/idle/wrong-attempt/illegal-tuple returns respectively `RECONCILIATION_REQUIRED`/`NO_CURRENT`/`ATTEMPT_MISMATCH`/`RESULT_INVALID`, ordinary state unchanged; post-close invocation is unadmitted `STORE_CLOSED`. | Settlement table, lifecycle, and queued-close tests. |
| OP-SETTLE-FAILURE | `V5-OP-SF-P`: admitted in `RUNNING`, matching attempt and every legal failure input persist computed byte fields and exact blocker, clear current, enter `IDLE`, generation +1, including if admission closes before execution. `V5-OP-SF-N`: startup/idle/wrong-attempt/illegal tuple or action returns exact precedence error, ordinary state unchanged; post-close invocation is unadmitted `STORE_CLOSED`. | Failure tuple/precedence/lifecycle and queued-close tests. |
| OP-RECONCILE | `V5-OP-REC-P`: only admitted `STARTUP_RECOVERY` current becomes exact unknown and `IDLE` before success returns, including after admission closes. `V5-OP-REC-N`: both `IDLE` and `RUNNING` return exactly `RECONCILIATION_NOT_REQUIRED`; startup clock or persistence failure leaves work state/current/bytes/cache unchanged; post-close invocation is unadmitted. | Every lifecycle branch, queued-close, restart fault, and effect-spy test. |
| OP-RESUME | `V5-OP-RES-P`: admitted in `IDLE`, matching eligible blocker ID clears only blocker at +1; next already-admitted dispatch gets next ordinal even if admission then closes. `V5-OP-RES-N`: startup returns `RECONCILIATION_REQUIRED`; running returns `CURRENT_ATTEMPT_EXISTS`; idle no/noneligible blocker returns `RESUME_NOT_ELIGIBLE`; wrong eligible ID returns `ATTEMPT_MISMATCH`; post-close invocation is `STORE_CLOSED`; all error branches are unchanged. | Lifecycle, blocker-precedence, FIFO, and close-admission tests. |
| OP-STATUS | `V5-OP-STAT-P`: admitted in `IDLE` and `RUNNING`, including execution after admission closes, null returns exact run state/null task; known ID returns equality-based exhaustion and state at +0. `V5-OP-STAT-N`: syntactically invalid ID is `INVALID_REQUEST`; syntactically valid non-member is only `UNKNOWN_TASK`; startup/stale/invalid snapshot wins before membership for an admitted call; post-close invocation wins as `STORE_CLOSED` before syntax. | Status membership, lifecycle, exhaustion, admission, and precedence tests. |
| OP-PROJECTION | `V5-OP-PROJ-P`: admitted in `IDLE` and `RUNNING`, including execution after admission closes, minimal and 40-settled legal histories return exactly `StoreProjectionV1`, deeply equal on repeat. `V5-OP-PROJ-N`: startup/invalid/stale admitted input returns exact error, no partial value, and no write; post-close invocation is unadmitted `STORE_CLOSED`. | Projection lifecycle, admission, boundary, and max-cardinality tests. |
| OP-CLOSE | `V5-OP-CLOSE-P`: from each ordinary work state, first close atomically sets `ADMISSION_CLOSED`, queues one barrier after all admitted calls, leaves owner `OPEN` and work state evolving until those calls settle, then discards cache/authority and sets `CLOSED` with zero checkpoint I/O/write and +0 generation. `V5-OP-CLOSE-F`: any earlier operation error and any later admitted ordinary guard error settle independently; FIFO continues and barrier succeeds. `V5-OP-CLOSE-B`: simultaneous/repeated close shares the identical pending/settled completion and creates no second barrier. `V5-OP-CLOSE-N`: every later non-close invocation returns `STORE_CLOSED` before admission/validation/I/O. | Exact §8.4.3 trace, all-work-state FIFO barrier suite, injected predecessor-failure suite, shared-completion identity, and zero-I/O spy. |

## 13. Closure map, retained lineage, risks, and blocker

### 13.1 F-V4-001 closure and retained v3 closure

| Finding | v5 disposition |
|---|---|
| F-V4-001 | **Closed:** §§5.4 and 8.2–8.6 remove `CLOSING` and define separate `OwnerState`, `AdmissionState`, and ordinary `WorkLifecycle`. First close atomically closes admission and queues exactly one FIFO barrier after admitted calls. Those calls execute against evolving normal work state; their errors do not stop later admitted items or the barrier. Later non-close invocations return `STORE_CLOSED` with no admission/I/O/mutation. Barrier execution discards cache/authority, sets final `CLOSED`, performs no checkpoint write, and changes no generation. Every close shares one completion/result. §8.4.3 and `V5-I13`/`V5-OP-CLOSE` make the coupled success and predecessor-failure interleavings executable. |
| V3-001 | **Closed and corrected without reopening:** `WorkLifecycle` retains the three ordinary live-current states and every exact operation branch; owner closure and admission are now orthogonal instead of a five-state conflation. §§8.2–8.5 preserve queued-dispatch/current errors, startup-only reconciliation, resume/current errors, total precedence, and ordinary unchanged-on-error semantics. |
| V3-002 | **Closed:** raw checkpoint/request schemas use syntactic `TaskIdText`; persisted membership/order is only checkpoint-identity `IDENTITY_MISMATCH`, while status request membership is only `UNKNOWN_TASK`; structural errors cannot overlap either. |
| V3-003 | **Closed:** §5.2 admits only an opaque, preconstructed, infallible Timestamp-only adapter, rejects an invalid initial source before owner/I/O, and contains every later throw/invalid value. Public operations have no unhandled clock exception/value and no invented runtime clock error. |
| V3-004 | **Closed:** `V5-I14-N1` uses a canonical replay-valid successor at a different generation to reach `STALE_GENERATION`; `V5-I14-N2` separately proves incoherent generation returns `HISTORY_GENERATION_MISMATCH`. |
| V3-005 | **Closed:** `GENERATION_OVERFLOW` is removed from reachable/public errors; §6.5 proves the absolute ceiling `40 dispatch + 40 settlement/reconcile + 20 resume = 100`. |
| V3-006 | **Mandatory post-acceptance handoff constraint only, not baseline readiness:** after this baseline is independently accepted, the successor implementation WBS must cite this exact artifact path and coordinator-recorded SHA-256, and exact HUMAN approval must precede dispatch. The current `wbs.v3` binding is neither asserted nor required for baseline acceptance. |

### 13.2 Retained CB and v2 lineage

| Finding | v5 disposition |
|---|---|
| V2-001 | Closed and retained: separate closed product `RuntimePlanV1`/`RuntimeApprovalV1`, exact normalization, two hashes, and explicit non-equivalence to `dsh-wbs/1`. |
| V2-002 | Closed and retained: generation-0 replay, event order, mutation equation, timestamps, first-ready history, blocker clears, and deterministic typed validation. |
| V2-003 | Closed and retained: raw caller DTOs, store-owned byte fields, exhaustive legal tuples, exact error bytes, formula, and blocker precedence. |
| V2-004 | Closed and corrected: every public request/value/error branch, generation/no-write behavior, orthogonal owner/admission/work state, FIFO close barrier, shared idempotence, and `STORE_CLOSED` are total. |
| V2-005 | Closed and retained: exactly one closed projection DTO; renderer formats and byte claims are explicitly deferred to a separate frozen contract. |
| V2-006 | Closed and retained/affected rows regenerated: matrix covers replay, generation, current-last, timestamps, retry/blocker, tuples, projection, work lifecycle, admission, live-current, recovery, precedence, failure-continuing FIFO, and close barrier without wrong-choice dispatch or directory-sync-failure cases. |
| CB-001 | Closed by exact closed runtime, approval, checkpoint, result, blocker, projection, request, response, error, owner/admission/work-state, and adapter schemas/contracts. |
| CB-002 | Closed by run-bound identities, store clock, persist-before-effect consumption, raw settlement boundary, and nonrefundable attempts. |
| CB-003 | Closed by replay-time and live first-ready DAG selection and total derived state rules. |
| CB-004 | Closed by total operations, exact generation effects, persistence boundaries, ordinary unchanged-on-error rules, and explicit barrier-only cache/authority discard. |
| CB-005 | Closed within scope by one-owner lifetime, orthogonal owner/admission/work state, failure-continuing FIFO, startup recovery, one close barrier, and internal expected generation. |
| CB-006 | Closed by preserved runtime canonical JSON, strict open/re-read bytes, and same-directory synced-temp rename. |
| CB-007 | Closed by bounded settled history and one deterministic projection DTO; rendering is not claimed. |
| CB-008 | Closed by literal checkpoint version `2`, fail-closed predecessor/future handling, and no migration. |
| CB-009 | Closed by one executable evidence row per normative invariant and public operation, bound through the coordinator hash record. |
| CB-010 | Refuted/preserved out of scope: no cross-process lock or multi-owner atomic CAS is added. |
| CB-011 | Preserved future risk/non-goal: multi-process writers and power-loss durability are not claimed. |

Retained risks are contract-violating second owners, same-UID tampering, orphan temporary files, and loss around rename under power failure. The trusted adapter boundary must be implemented and inspected as specified; it does not make the underlying time source truthful. The linearizable invocation/admission boundary and shared close-completion identity require careful same-instance implementation and concurrency testing, but the contract now fixes their result. These are not Sprint-1 acceptance claims.

**Planning blocker:** no product implementation or mission dispatch is authorized by this artifact. The coordinator must first obtain independent preimplementation review with no open HIGH baseline gap and create the separate `CURRENT_BASELINE_SHA256_RECORD` binding for these exact bytes. Only after baseline acceptance may a successor implementation WBS be authored; that WBS must cite this exact path and recorded SHA-256 and receive exact HUMAN approval before dispatch. Before `integrate-mvp`, a separately frozen integration/report contract must define exact JSON and Markdown rendering. No current WBS binding is a condition of baseline readiness.
