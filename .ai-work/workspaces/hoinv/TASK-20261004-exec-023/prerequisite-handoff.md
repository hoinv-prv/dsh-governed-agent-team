# AIP-EXEC-023 prerequisite handoff

Status: prerequisite source/artifact qualification PASS; independent review PASS. AIP closed through the governed tool; verification/aip-close.log records the status transition. Parent production composition and deployment remain separate.

The authorized DSH worktree is `/home/hoinv/work/dsh-binding-prerequisites`, branch `gat-binding-prerequisites`, based on `c291e7961a515f6d7af9304e7fd1d257929aef26`. Source changes remain uncommitted. The reviewable source patch and SHA-256 receipt are `verification/DSH-prerequisites.patch` and `verification/source-patch-receipt.json`. The patch includes the installed GAT foundation needed for actual composition plus these prerequisites. Operational installer receipts, native build binaries, Python caches and VitePress build temporaries are excluded; it is not a deployment package. The 244-path patch SHA-256 is `d532cc1e8d110c9db891219c89f20b4fd94d0836aa1e8c7d6d3494dddfb8cbf0`. An alternate Git index verifies application to the approved baseline; the real index remains unchanged.

DSH exports controlled `materializeContinuable` / `recoverContinuable`, persist-only quarantined initial admission, durable activation/abort and exact generation recovery. The Agent loop awaits `agent/prepare-prompt` before every render, then checks final synchronous authority before provider dispatch. The registry captures immutable capabilities and descendant references, validates live nested parent identity and rechecks actual dispatch. Independently scheduled Agent drivers receive their own root context through host-only `withAgentDriver`.

GAT consumes one-use authenticated HTTP control receipts, persists exact HUMAN mission/member/plan approval and stores private Agent-generation mission/task leases. Canonical task association, owner/status and revision are checked at effects, model admission, activation and queued release. Authority publication failures deny; unrelated mailbox/work publication does not suspend a valid lease. Team withdrawal closes gates synchronously and retains guards through physical drainage.

| Evidence | Scope |
|---|---|
| `host-prerequisites.md` | Reserved lifecycle, malformed/recovered records, prompt/retry and final guard regressions |
| `capability-prerequisites.md` | 703 focused registry/executor/Consumer checks |
| `authority-prerequisites.md` | Exact receipts, claims, publication/cutoff and real host races |
| `authorization-matrix.md` | 60 actual HTTP/dispatcher cells; 19 allowed effect bodies, 41 denied, zero provider requests |
| `sdk-qualification.md` | Built CLI TypeScript replay and four Python scenarios; retained historical predecessor audit |
| `conformance.md` | Final contract-to-evidence matrix and acceptance limits |
| `independent-review.md` | Substantive R1–R8 disposition, independently executed suites and closure verdict |

Design ownership is formal GAT `DETAIL_DESIGN.md` §7, with architecture §11, basic §12 and the Durable integration prerequisite section. Owning DSH architecture/core/subagent/tools references, README pairs and implemented Agent Notes record the contracts. Source maps point to exact current GAT declarations and the isolated DSH revision. Two prior corrective edits lacked a separately written intended paragraph; this chronology gap remains recorded and was independently reviewed for consistency. API comment insertion split expressions and removed the ATTACHMENT_LIMITS export. The supported compiler caught these defects, and they were restored before final acceptance. Final supported host/client builds pass; the full 270-test suite passes independently. Normalized tools JavaScript matches the pre-comment artifact exactly; core differs through independently reviewed equivalent aliases, cleanup capture and validation syntax. See source-design-consistency.md and verification/built-js-comparison.json.

The original DSH HEAD is unchanged. Its 365 other protected dirty-file hashes match the baseline. Original `AGENTS.md` changed during the interruption at 12:29 JST; this workstream issued no edit there, and its current contents were preserved. `verification/protected-original-audit-final.json` records the observed difference instead of claiming every original byte is unchanged. Original source files were not restored, reset or replaced.

To inspect the result:

```bash
cd /home/hoinv/work/dsh-binding-prerequisites
git status --short
git diff --stat
git diff -- packages/core/agent-loop/src/agent.ts packages/core/tools/src/index.ts
```

The source patch also includes new files that plain `git diff` omits. Review `verification/source-patch-receipt.json` and the binary-safe patch from the task workspace. It is produced through a temporary Git index; the worktree's real index remains unchanged.

To repeat the principal GAT integration checks after a later source change:

```bash
cd /home/hoinv/work/dsh-binding-prerequisites
node node_modules/vitest/vitest.mjs run packages/experimental/gat-core/tests packages/experimental/gat-tools/tests packages/experimental/gat-web/tests packages/experimental/gat-profile/tests --maxWorkers=3
node --max-old-space-size=4096 node_modules/typescript/bin/tsc -b tsconfig.host.json --pretty false
node node_modules/tsdown/dist/run.mjs --env.DSH_BUILD_FACE host
node node_modules/typescript/bin/tsc -b tsconfig.client.json --pretty false
node node_modules/tsdown/dist/run.mjs --env.DSH_BUILD_FACE client
pnpm run doc-sync
```

These commands assume the already prepared worktree dependencies and Linux native addon. They are validation commands, not installation into the original checkout.

Qualification receipts: verification/gat-behavior-final.log (17 files / 270 tests), gat-source-lint-final.log (exit 0), host-qualified-types.log / host-qualified-bundle.log and client-qualified-types.log / client-qualified-bundle.log (exit 0), public-built-qualified.log (11 public imports), doc-sync-accepted.log (34/34), tested-source-final-hashes.json (57 matches), sdk-qualified-hash-comparison.json (seven unchanged runtime artifacts), source-patch-final-validation.json (244 paths; applicable to baseline; unchanged real index). Independent review records PASS. Task strict governance lint has zero errors/warnings; whole-tree retains 37 warnings and zero errors. Counts overlap.

AIP-EXEC-022 may consume these exact qualified source/artifact receipts after closure of this prerequisite. Its next work is production binder composition against these exported APIs, generation/attachment recovery, profile/packaging/browser qualification and an exact compatibility receipt for the changed host. The old compatibility baseline alone cannot approve modified bytes. Current-v3 SDK expectation refresh was reviewed separately from released-format migration; historical v2 and existing Python predecessor bytes remain unchanged.

Deployment, publication, merge, live profile activation and Truth/Wiki promotion remain separate. Captured knowledge is deferred to the account backlog for HUMAN review; no canonical promotion occurred. Parent AIP-EXEC-022 remains open.

## Local commit handoff — 2026-10-04

The isolated DSH prerequisite work is committed locally as `5c02ce9f3e44dfce3f87498f65cf684194ad4572`, with parent `c291e7961a515f6d7af9304e7fd1d257929aef26`. `commit-receipt.json` binds all 244 committed paths to the checked bytes and preserves the earlier patch receipt as history. Eleven commit-check corrections match the preceding normalized emitted JavaScript exactly; 18 GAT files / 271 tests and 22 Connection/Gateway files / 451 tests pass. Documentation checks pass 34/34; client types and public built imports pass; seven SDK runtime hashes remain unchanged; 57 root/host source pairs match. Source maps and current hashes were refreshed.

Required staged lint passes with 21 warnings and enabled commit hooks. Supplemental type-aware lint remains RED with 172 diagnostics traced to pre-correction lines. This is not a full lint qualification; parent RQ-022-05 requires disposition. Parent production composition, changed-host release/profile/package qualification and browser mismatch remain open. No deployment or external publication was performed. Earlier uncommitted-patch instructions and results above describe their historical inspection.
