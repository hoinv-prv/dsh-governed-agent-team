# Final P1 file/cwd containment decision report

## Binding and status

- Mission: `durable-agent-p1-file-cwd-containment-poc`
- WBS revision/hash: `1` / `9b7243ea15285e95e7922489113ae7b8069eb3f5893a2e8a81aa9d909921f3de`
- Task/attempt: `p1_final` / `p1_final-a01-r1`
- Independent integration review: `meets_criteria`, advisory `accept`
- Final artifact status: **candidate for independent final review and explicit HUMAN decision; not self-accepted**

## Advisory recommendation

**ACCEPT**, only for bounded P1 feasibility of the frozen component-aware, strict no-symlink file/cwd containment seam in the observed cooperative Linux/POSIX environment.

The supported claim is narrow: without hostile concurrent topology mutation, the frozen seam contains bounded `read`, `write`, and `append` operations and classifies a command cwd across the immutable topology matrix, while rejected cases show zero observed unintended changes in the monitored trees.

This recommendation does **not** authorize product edits, production deployment, production security/sandbox claims, hostile-TOCTOU safety, hard-link or mount-boundary safety, Windows or remote-filesystem behavior, BS1, FS3, FS4, another WBS, or any downstream execution.

The HUMAN alone must choose exactly one of **accept**, **defer**, or **reject** after independent final review. Until that explicit decision, P1 remains unaccepted.

## Six exact frozen input hashes

| Frozen input | SHA-256 |
|---|---|
| `oracle/topology-manifest.json` | `20de58bf0e3212dbbd9d1a3463698828d421b4b876ac188231a2c62e07c42bc3` |
| `oracle/p1-containment.test.mjs` | `a9e2406f9993bae5a1dde82900a47230d71faeedafb39a1e3980e3722569d7f9` |
| `prototype/containment.mjs` | `cb568613dd6d53fd890318b566de1e86ee90f0d12668f04d3ad06c9ec8b6054a` |
| `prototype/algorithm.md` | `a561d8ee77de6bbb4076e2b39f423c845a24e38790ab244bfddb16f9386aac46` |
| `prototype/environment.json` | `023ac9c768db6a5e8cdf5d68dcfe9c2e13db28469bab47e0a894291d8c8b3fec` |
| `prototype/ceiling-proposal.json` | `2d8558fa06fa63ef3d9bff2e9dac00b879511429927e711905893839fc1995bf` |

Coordinator-native exact integration verification on these bytes produced:

- immutable oracle: **66 passed / 66 total**, 0 failed, skipped, cancelled, or todo; exit 0;
- exact six-file `sha256sum`: all values matched the table in declared argument order; exit 0;
- matching deterministic environment and prototype receipts.

No hash is claimed here for `integration.md`, `p1-decision-candidate.json`, this report, or `learning-candidates.md`. The approved contract binds the six accepted inputs; final outputs remain subject to independent review.

## Topology and zero-outside-effect evidence

The 66 cases consist of 64 supported-action rows—four actions across sixteen explicit topologies—plus explicit `delete` and unknown-action rejection rows.

For each row, the immutable harness creates real mission-local `root`, `outside`, and `root-sibling` trees and records deterministic no-follow digests containing sorted relative path, lstat kind, mode, symlink text, regular-file size, and regular-file SHA-256.

- Every blocked case requires identical pre/post digests for all three trees.
- Accepted read changes nothing.
- Accepted write/append changes only the declared contained target.
- Accepted `command_cwd` changes only the harness-declared marker after successful cwd classification; the candidate never spawns.
- Outside and root-sibling digests remain unchanged for every accepted case.
- Fixtures are cleaned after execution.

This is real bounded topology evidence, not proof against unobserved or excluded filesystem adversaries.

## Observed environment

The exact authorized process observed and bound:

- Node `process.version`: `v22.23.1`;
- platform: `linux`;
- Node architecture: `x64`; normalized machine architecture recorded separately as `x86_64`;
- kernel release: `6.17.0-35-generic`;
- uid/gid: `1000` / `1000`;
- sorted groups: `[4, 24, 27, 30, 44, 46, 100, 114, 992, 1000]`;
- umask: decimal `2`, octal `0o002`;
- symlink capability positively observed through the generic `lstat` walk;
- 64 observed roots, all under `wbs-runs/durable-agent-p1-file-cwd-containment-poc/test-runtime`;
- fixture device: decimal `66306`, hex `0x10302`;
- raw `statfs.type`: decimal `61267`, hex `0xef53`; no filesystem name is fabricated;
- case sensitivity: measured `case-sensitive`;
- all observed roots shared the device/type/case facts.

The settled environment object must deep-canonically equal later receipts or the evidence process fails closed. This pins the feasibility claim to the observed cooperative environment; it does not establish portability.

## Nine proposed ceilings

| Ceiling | Proposed value | Engine ceiling | Exact unit |
|---|---:|---:|---|
| `path_input_bytes` | 4,096 | 16,384 | UTF-8 bytes |
| `relative_path_depth` | 64 | 256 | path segments |
| `file_read_bytes` | 1,048,576 | 4,194,304 | bytes returned per operation |
| `write_input_bytes` | 1,048,576 | 4,194,304 | input bytes per operation |
| `append_input_bytes` | 1,048,576 | 4,194,304 | input bytes per operation |
| `resulting_file_bytes` | 4,194,304 | 16,777,216 | bytes after write or append |
| `operation_count` | 256 | 1,024 | filesystem operations per seam call |
| `returned_metadata_bytes` | 65,536 | 262,144 | UTF-8 bytes per result |
| `cwd_input_bytes` | 4,096 | 16,384 | UTF-8 bytes per command cwd classification |

All values and engine ceilings are positive safe integers with documented rationale and candidate enforcement. They are bounded P1 proposals, not production limits. Command timeout, stdout/stderr, signals, argv, and process count remain deferred because this seam classifies cwd and never executes a process.

## All nine requirement dispositions

| Requirement | Final evidence-bound disposition |
|---|---|
| `p1-authority-scope` | Satisfied on frozen bytes: exactly read/write/append/cwd classification are supported; delete and unknown actions reject before effect; v10/baseline authority remains bound. |
| `p1-topology-matrix` | Satisfied: 64 supported-action topology rows plus delete/unknown pass, including existing, absent, missing ancestor, all symlink forms, traversal/outside/prefix collision, empty/NUL/non-string, and wrong-kind cases. |
| `p1-zero-outside-effect` | Satisfied under monitored-tree semantics: every block has identical three-tree digests; accepted cases change only the declared target/marker. |
| `p1-chosen-algorithm` | Satisfied for the PoC: component-aware lexical containment, complete `lstat` walk, categorical symlink rejection, absent-final distinction, kind checks, immediate revalidation, typed fail-closed results, and one bounded effect. |
| `p1-command-cwd` | Satisfied: only an existing contained non-symlink directory returns `ACCEPT_CWD`; no process is spawned; rejected cwd rows produce no marker. |
| `p1-threat-environment` | Satisfied only for the exact observed cooperative Linux/POSIX environment and raw receipt facts above; hostile concurrency and cross-platform claims remain excluded. |
| `p1-ceilings-units` | Satisfied as nine finite P1 proposals with exact units, engine ceilings, rationale, and enforcement; unrelated process ceilings remain deferred. |
| `p1-decision-governance` | Satisfied through final-artifact production: exact bytes/commands, both failed HIGH-review cycles, residual risks, independent reviews, and complete accounting are preserved. Independent final review and HUMAN choice remain pending. |
| `p1-learning-governance` | Satisfied: learning observations are provenance-bound, mission-local, non-canonical, and not automatically promoted. |

## Complete charged-attempt and review lineage

1. **`p1_boundary_oracle-a01-r1` — failed, 40 minutes.** Selfcheck passed 5/5, but independent review found two HIGH gaps: malformed input covered only empty string, and the five declared oracle output hashes were absent.
2. **`p1_boundary_oracle-a02-r1` — accepted, 40 minutes.** Selfcheck passed 6/6; empty/NUL/non-string cases for every action and all five oracle output hashes were bound. Independent review returned `meets_criteria`.
3. **`p1_containment_prototype-a01-r1` — failed, 45 minutes.** Syntax and immutable oracle passed 66/66, but independent review found two HIGH gaps: environment facts remained provisional and all five prototype output hashes were absent.
4. **`p1_containment_prototype-a02-r1` — accepted, 45 minutes.** Final syntax and immutable oracle passed 66/66; deterministic generic receipts settled the observed environment and five prototype hashes without oracle changes or row-ID branching. Independent review returned `meets_criteria`.
5. **`p1_integration-a01-r1` — accepted, 25 minutes.** Coordinator-native 66/66 and exact six hashes passed. Independent integration review returned `meets_criteria` and advisory `accept`, while limiting evidence instrumentation to PoC use.
6. **`p1_final-a01-r1` — current charged attempt, 20 minutes.** Produces this conclusion package; independent final review and HUMAN choice are still required.

No failed attempt, HIGH finding, or charge was hidden, reset, or reused.

- Charged attempts: **6 / 6**
- Charged effort allowance: **215 / 215 minutes**
- Remaining capacity: **0 attempts / 0 minutes**

No correction or retry remains under this plan.

## Evidence instrumentation limitation

The prototype's generic instrumentation observes only roots received through the public seam, emits deduplicated deterministic environment facts, validates settled environment equality, and hashes the five prototype outputs. It does not inspect manifest row IDs or test names, change seam results, spawn, use the network, or write receipt files.

This instrumentation is **PoC-only evidence instrumentation**. It is not a generalized production telemetry, audit, operation-counting, containment, or security contract and must not be treated as one.

## Explicit exclusions

Regardless of the HUMAN decision, this report grants no authority for:

- product modification, production implementation, readiness, certification, or sandbox claims;
- hostile TOCTOU, concurrent rename, or symlink-swap resistance;
- hard-link aliases;
- bind mounts, mount mutation, or other mount-boundary attacks;
- Windows junctions, reparse points, or case-folding behavior;
- remote filesystems;
- ACL, quota, durability, crash atomicity, or global filesystem monitoring;
- real command/process execution, delete, rename, chmod, network, model, WBS, queue, or delegation effects;
- BS1, FS3, FS4, another WBS, or any downstream execution.

## Required HUMAN choice

Choose exactly one:

- **accept** — approve only the bounded P1 cooperative Linux/POSIX strict no-symlink feasibility conclusion for the six exact frozen inputs;
- **defer** — withhold the conclusion without asserting that the frozen evidence is false;
- **reject** — reject when an exact hash, command, review, accounting, or mandatory semantic claim is contradicted.

**HUMAN decision required: `accept` | `defer` | `reject`.**

A missing, ambiguous, held, or rejected decision leaves P1 unaccepted. No choice authorizes any excluded or downstream work.
