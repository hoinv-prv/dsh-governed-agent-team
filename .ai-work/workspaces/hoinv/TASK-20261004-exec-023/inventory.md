# AIP-EXEC-023 prerequisite inventory

Read-only inventory captured 2026-10-04. No source/design/wiki/Truth changes or tests were run for this inventory. The only write is this workspace report.

## Governance and scope

- Root `AGENTS.md`, `.ai-work/AIWS.local.md`, and the active STEP-02 ASC were read first. The approved execution target is `/home/hoinv/work/dsh-binding-prerequisites` at `c291e7961a515f6d7af9304e7fd1d257929aef26`; preserve its dirty baseline. Deployment/activation is separately gated.
- Wiki-first lookup for “GAT member binding contract freeze” returned `SRC-GAT-MEMBER-BINDING-FREEZE` at `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`.
- Formal design checked: `docs/gat-design/DETAIL_DESIGN.md` §7. Frozen requirements checked: `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§7–14.
- DD §7 assigns DSH reserved lifecycle/request refresh to subagent, core/agent and agent-loop; capabilities to core/tools and delegation consumers; authority to GAT plus authenticated DSH ingress. It requires intended owner docs before source edits, actual registry/provider/inbox/auth qualification, the complete freeze §13 matrix, built public imports, affected docs/SDK gates and reconciled source maps.
- Freeze §§7–9 require persist-only quarantined initial inbox, activation as sole release, exact idempotency/stable errors, tombstone-before-dispose, recovery-before-release, generation-safe recovery and legacy wrapper compatibility. §§10–12 require exact host-attested HUMAN provenance, current scoped leases checked before effects, canonical task authority, immutable nested capability unions and safe prompt/view behavior. §13 defines lifecycle, restart, disposal, delegation, authorization, scope-isolation and compatibility fixtures. §14 makes DSH own reserved handles and SDK/runtime primitives, while GAT owns orchestration and authority.

## AIP and workspace coverage

- `lint_aip.py --path .ai-work/aip/hoinv/exec/AIP-EXEC-023-implement-binding-prerequisites.md --format json`: exit 0; 0 errors, 0 warnings, 0 info, no findings.
- The active pointer and current ASC are STEP-02. Snapshot coverage exists for STEP-00, STEP-01 and STEP-02 only; STEP-00/01 snapshots still say `status: active`, while STEP-02 is active. No STEP-03 through STEP-07 ASC snapshots are present.
- Output metadata has one real row: `OUT-023-01-01`, STEP-01 `design-delta.md`, `review_status: draft`, `verification_level: unverified`, empty `source_refs`. `STEP-NN.meta.yml.template` is scaffolding, not evidence. STEP-02+ have no output metadata rows.
- `step-status.md` says STEP-02 is in progress, STEP-03/04/05 are also in progress, and STEP-06/07 pending. This is not backed by per-step ASC snapshots or output metadata past STEP-01. Reconcile the status and generated ASC/output records as execution advances; do not treat the status prose as qualification evidence.
- The active ASC’s “Previous Step Results” points at the unverified STEP-01 draft. Its own coverage section flags trimmed Step Output/Decision requirements, trimmed Source Verification requirements, and no expected outputs declared. Its capture inbox references include retrieval gaps for the proposal, DSH architecture doc and AIP template.

## Existing verification evidence

These are observations of saved logs only. None stores a command exit code or a machine-readable command record, so exit status is **not evidenced** for any log; do not infer an exit code solely from a success-looking tail. No checks were rerun.

| Log | Saved result / findings | Exit evidence |
|---|---|---|
| `verification/baseline-tools-scope.log` | Vitest scoped tests: 25 passed, 2 failed (27 total). Failures: guard replacement deferred behavior expected `ran:t`, got `Error: replacement denial`; token count expected 2, got 1. | Not recorded |
| `verification/capability-focused.log` | Latest saved file reports 14 test files and 703 tests passed. (An earlier read during this inventory saw a smaller version; shared files were changing. This reports the current on-disk contents.) | Not recorded |
| `verification/capability-typecheck.log` | Empty, 0 bytes; no result can be established. | Not recorded |
| `verification/prerequisite-types-01.log` | Type build diagnostics include exact-optional `deferExecution` forwarding incompatibilities, composite/rootDir project-reference errors and a GAT callback returning `void` where `Promise<void>` is required. `04_findings.md` says this early failed build also emitted 60 untracked TS siblings; those were removed after checking they were generated and absent from git. | Not recorded; failure output present |
| `verification/native-build.log` | Contains install/build output and `build: built linux-x64/bin/glibc/system.node`; includes platform/cycle and missing CLI-bin warnings. | Not recorded |

`04_findings.md` separately records a 94-file structural baseline PASS before host changes and protected hashes retained, but this inventory did not independently validate that receipt. It explicitly says preparation failures are not qualification PASS evidence.

## Applicable DSH gates from repository instructions

- Product-visible behavior needs real composition coverage through Loader/app/process; hand-built `ctx.plugin()` tests alone are insufficient. Lifecycle/capability paths also need focused invalid-case denials before side effects.
- Since `agent-loop` and `SessionEventMap` are changed, update and qualify **both** SDK projections: TypeScript under `snapshots/sdk/` and the Python runtime expected output at `scripts/snapshots/python-sdk-single-exe/`. Relevant model/protocol/human-visible behavior also requires a keyless recorded-session scenario; review transcript and workspace expected diffs.
- Update owning package README and JSDoc with behavior, update `docs/architecture.md` for loop changes and the owning subsystem page for reshaped public types. Non-trivial work needs an Agent Note; keep bilingual documentation pairs together where applicable.
- Run relevant focused behavior checks and affected type/build checks, then DSH documentation gates (`pnpm run doc-sync`, which includes documentation validation/synchronization); add the built public-import smoke for exported package paths. The full suite is not the default local gate; CI owns exhaustive coverage/platform matrix.
- The worktree root `AGENTS.md` also requires documenting only commands actually run. It lists `pnpm run test`, `typecheck`, `build`, `hygiene`, `test:snapshot`, and `doc-sync`; scope the checks to changed surfaces and current AIP qualification rather than claiming these all ran.

## Worktree baseline

The DSH worktree HEAD remains the approved `c291e7961a515f6d7af9304e7fd1d257929aef26`; it has many modified and untracked files spanning docs, agent-loop, subagent, tools, connection, experimental GAT packages and native output. The root GAT repository also has broad pre-existing dirty design/source/workspace changes. Preserve both footprints and compare against the recorded protected baseline before any future destructive cleanup or handoff. This inventory makes no production eligibility or deployment claim.
