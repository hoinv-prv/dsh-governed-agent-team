# Independent remaining-source review — AIP-EXEC-022

Reviewer: `/root/remaining_review`. Date: 2026-10-04. Scope: source and existing source-test receipts only; no deployment, publication, merge, Truth or wiki promotion. This review artifact does not accept the complete AIP.

## Disposition

**PASS — source semantics and the reviewed source receipts.** Every identified source finding is resolved in the inspected frozen core/adapter bytes. Final built/runtime/browser/distribution qualification and overall AIP acceptance remain pending. This source PASS does not authorize deployment.

## Design inputs and review method

Wiki-first lookup resolved `SRC-GAT-DETAIL-DESIGN`. Reviewed official `docs/gat-design/DETAIL_DESIGN.md` §8 (including late failure observation, prepared construction ownership, contribution withdrawal and selected receipt hash corrections), related architecture/basic/integration deltas, `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§6–8/10–12, and proposal §§5–8/11. Source review covered connected binder registry, full roster preparation, immutable record publication, real reserved member scope, exact execution authorization, recovery/mailbox, WK exclusive ownership, executable closed tools, actual profile initialization and additive installer ownership.

Independently recomputed all 40 source and host mirror hashes recorded in `core-production-receipt.json`: all match. The source-ready receipt records the refreshed 11-file/166-test core plus real WK composition PASS, normal core type-aware lint, core/aggregate host typechecks and exported API JSDoc PASS. `core-production-ack-transaction-full-tests.log` reports 166 passed; its focused regression log reports 10 production-binding tests passed. The refreshed receipt records ordinary core type-aware lint and core/aggregate host declaration checks PASS. These were rerun by the owning agent after the acknowledgement correction; this reviewer independently checked their logs and all 40 receipt hashes. The full suite records a nonfatal FileHandle garbage-collection warning, disclosed in the source handoff. `adapter-production-tests.log` independently reports five files/48 tests passed. Empty successful compiler/lint stdout is treated together with the owner's receipt rather than inventing output. Passing source receipts do not establish built output acceptance.

## Resolved staged acknowledgement finding

**Resolved P1 — staged delivery receipt authorization in the journal queue.** In `packages/core/src/mailbox.ts`, `checkpointStaged()` checks exact target authority before awaiting `markDelivered()` and after it completes. `markDelivered()` first waits for `journal.transact(root.id, ...)`, then appends `team/message/delivered` without checking target authorization within that serialized callback. A queued canonical mission revocation/task revision committing ahead of the acknowledgement can make the pre-queue check stale; the final check rejects only after the delivered receipt is already published. Detail Design §8 requires exact current authority at asynchronous staging boundaries before receipt publication. Pass a staged-only exact assertion/signal into that callback, recheck after transaction admission immediately before append, and add a serialized revocation-before-acknowledgement regression. Preserve the already qualified empty-attachment delivery semantics.

Correction independently rechecked: only `checkpointStaged()` supplies an exact target/cancellation callback to `markDelivered()`. The callback executes inside `journal.transact`, immediately before `appendAndFlush`; no asynchronous gap separates this check from append admission. The actual serialized regression blocks the Lead queue, enqueues a real canonical task edit before acknowledgement, then independently reads the single staged target input. It proves no delivered receipt and no extra request after denial, followed by explicit reauthorization of the same Agent/input identity and exactly one receipt on retry. `core-production-ack-transaction-focused-tests.log` and `core-production-ack-transaction-full-tests.log` qualify the corrected bytes. Official Detail Design §8 “Staged acknowledgement transaction authorization” documents the commit-boundary rule before the source correction. The legacy empty-attachment acknowledgement passes no new callback.

## Corrected findings and source assessment

- Exact selected installer receipts now compare manifest and payload checksums and exact expected hash/size rows. Regenerating payload bytes at the same paths cannot accept an older installed payload. Legacy default receipt behavior remains separate.
- WK acquisition/recovery failures aggregate the original failure with contribution removal/provider release failures; failed release retains identity ownership. Core acquisition and deadline observers retain late physical cleanup rejection without holding the cancelled caller or reopening admission.
- Successful raw prepare results remain cleanup-owned through reading the opaque value and constructing a tracked lease; the safely captured abort survives a throwing value accessor. Pending/failed cleanup keeps the registration pin until physical settlement.
- Required contribution withdrawal closes the exact real host scope, removes remaining prompt/tools/hooks and makes core readiness unavailable. A still-live Agent or later lease cannot restore this generation. The blocked-read/revocation regression denies reauthorization and model admission.
- Registered real tools preserve explicit read/effect capability metadata and immutable nested dispatch enforcement. Tool schemas remain closed, runtime arguments/results bounded, candidate receipts unconfirmed, and provider refs/selector/workspace are not model inputs.
- Scope-current setup is independent of execution authorization, allowing quarantined installation without granting requests/effects. Exact host authorization and installed required bindings remain jointly required for final execution. Default GAT initializer behavior is retained; opt-in composition installs the sole strict Durable initializer/provider.
- Active reconstruction uses immutable persisted attachments and owned child admission evidence, never YAML reread or duplicate initial persistence. Consumed-initial staging is attached-only and verifies persisted target message identity after successful flush before its receipt; false and unpersisted-true flush regressions fail closed. The final acknowledgement transaction now rechecks exact authority inside the serialized append boundary, as detailed above.

## Built verifier coverage and remaining evidence

`installer/verify-binding-runtime.mjs` is an actual plain-Node exported Loader/profile verifier. It resolves and records built module/profile paths and hashes, uses private temporary provider/Session storage, authenticated HTTP mission control and explicit canonical tasks, checks quarantined enable before requests, coherent refresh across two requests, executable read schema/candidate effect, persistent provider recovery with changed YAML and one initial admission, consumed followup delivery, and revocation during a blocked selective read. Its assertions are substantive; it was not executed by this reviewer. Require its PASS receipt on the frozen installed target, fresh additive install/failure restore/status/idempotence/rollback receipts, frozen lock/export/packed checks, browser replay and final design/source mapping/lint before AIP acceptance. The selected direct-continuable target does not claim isolated closing/task execution semantics.

## Protected work

Independent SHA-256 comparison against `remaining-work-baseline.json`: {'SOURCE_SNAPSHOT.json': True, 'compatibility/dsh-0.1.5-rc.2/manifest.json': True, 'installer/verify.mjs': True}. These three protected dirty files remain byte-identical. No production or mission control was mutated during this review.

## Reviewed hash anchors

Hashes bind this source review to inspected bytes. A source correction requires refreshed owner receipts and re-review of affected paths.

| Path | SHA-256 |
| --- | --- |
| packages/core/src/member-host.ts | `7ad1914df53454ae42d2657991ebe423daa8177b4b8ba6a5dacc921f1e97c56d` |
| packages/core/src/member-binding.ts | `c0d191454c0608f19bbfd91c3b8b69376f2af234eb51ca6fd181088d65d12fb2` |
| packages/core/src/member-binders.ts | `e5b7967d0a9abb7be97efec68e0487c843bb8f7280c4f25cf83e61c9716113b1` |
| packages/core/src/binding-deadline.ts | `c3b0520c4f4558c92e49d3791878614f0c7f8fecaa1c20c16af205683f206fde` |
| packages/core/src/roster.ts | `f4518a259a325d9db4692516b58495cf209fad184364fcf930fe802dbd4231c5` |
| packages/core/src/mailbox.ts | `4be4d71ec88924c3ce38ac2a29e165f263c4572ebe3a62afda1b162b49a50a4e` |
| packages/core/src/index.ts | `5a173592fd7919a3361d5e0e7d3adbc30440fa40bde61c5cd8d504ec25f53420` |
| packages/durable-agent/src/binder.ts | `e96321ae263a2a8be4171ca744207e7e6c9190b17337d12ec1ec9efbef652e33` |
| packages/durable-agent/src/composition.ts | `7c2b1305f92d80021151a383936872a084f29a3cb4777beaaf9f0fbb22e594ec` |
| packages/durable-agent/src/provider.ts | `e1a3208196390f417f4ee61ad1f7327013a42b1aca7aa92c4ecb4a7b43162d18` |
| packages/durable-agent/src/initializer.ts | `2c2f7f4bde7e3157cef8dc6cd2bdad0df0733a2dfc854b09a5eeedc36a571b30` |
| packages/durable-agent/src/tools.ts | `5a986d23476809e3a5b8c70a00f33134339d4fef5fe4f0e116175da685fc1d61` |
| packages/durable-agent/src/ownership.ts | `2d0d7bf992c8211bf2309a9cb80c4b5a850e886790b15eb25bd03e508e9a6d20` |
| packages/durable-agent/tests/binder.spec.ts | `137333231d08eec33746873cf0aac1ee0e547b58a6da99d196071194cd059822` |
| packages/durable-agent/tests/composition.spec.ts | `b68d656bfb39d699db27b809499697e7f4a3fa6a9ed3c608038e5b9a848ff685` |
| installer/index.mjs | `0f6f64e66810c835616bcf014bab8a2e63fff140303eff508445f371a861c143` |
| installer/verify-binding-runtime.mjs | `d163076783550db2af06f5573f3eaa1c20c36ba6893510372dc1b6ba24f004b2` |
| installer/tests/binding-compatibility.test.mjs | `a40bcee39b51a2b8f085e563a0d46ac4d3761358d0a958b69c0600d465c9df1f` |
| packages/durable-profile/cordis.patch.yml | `af6d2c6b2417973bc85a79a81e09d30953490c4e5df589f3f552d25844a886b7` |
| docs/gat-design/DETAIL_DESIGN.md | `69c8ea37b35cffc5a786e69f6cb61b9c20e8ca2cfc1a91529ace960784c44bd8` |
| packages/core/tests/production-binding.spec.ts | `5c688b941130b5b20df67b530b5d461edd4d4c75e2111da079472fbe67c70d80` |

## Distribution/build-context follow-up — pre-seal source audit

Reviewed the updated official Detail Design §8 “Installed documentation layout ownership,” browser quarantine fixture alignment, built Remote descriptor alignment and “Shared authenticated control context in built gateway” before reviewing the associated distribution/verification delta. The gateway runtime peer correction externalizes the public client-connection module through the ordinary package contract and retains its development dependency. No receipt-free admission or alternate global authorization state was introduced. The observed duplicate AsyncLocalStorage defect affects built Gateway WebSocket dispatch; earlier signed HTTP Loader PASS does not qualify that path. Overall acceptance remains pending until actual WS/browser and the built external-import guard pass on the recaptured sealed artifact. Earlier qualified/accepted reports and browser diagnostics remain history.

Source audit of `scripts/generate-binding-compatibility.mjs`, selected manifest planning, `installer/index.mjs`, `installer/verify-binding.mjs` and the export/archive/runtime verifiers found no further installer ownership defect. Exact selected commit/prerequisite and payload drift checks precede mutation; host replacements retain before/after hashes, additions-only roots are eligible for recursive removal, and the fixed six installed core/tools documentation overrides do not override runtime source. Provider runtime/declaration reconstruction records 46 exact matches against the pinned provider revision; archived source/docs are checked against Git and excluded from aggregate/catalog source discovery. Fresh scratch creation rejects an existing target, installer failure/rollback requires pristine restoration, and workspace/native verification links retain target ownership. Eight packed private workspace package probes use their exact target peers and expressly exclude standalone registry publication.

The updated public export guard inspects gateway runtime peer metadata, requires public `withControlInvocation` and Core `consumeHumanControl` imports, rejects the known bundled admission store, compares scoped public module resolution and records gateway/admission module hashes. The root-owned runtime verifier now distinguishes receipt-free Enable, unauthenticated HTTP, authenticated stale business revision denial, later valid approval, coherent refresh, persistent queued recovery and late revoked read. These are source-coverage assessments; no new built PASS is inferred before the root/distribution owners seal and execute the final receipts. Final distribution handoff must identify the same sealed target/hash as final runtime/browser/SDK/native/packed evidence.

Follow-up reviewed helper hashes (pre-seal; refresh on final evidence):

| Path | SHA-256 |
| --- | --- |
| scripts/generate-binding-compatibility.mjs | `67af75e0dd86dbe590dbe148df8c26c52ebf7b5d766d3939d1332cd5028c2129` |
| installer/verify-binding.mjs | `65ae04b66fbeea063671e950922c02b8fde71c1cd189ab55198585e22730dda7` |
| installer/verify-binding-exports.mjs | `677883f6b7942befba86170c22e070429f41ca0854c48a3bbffedb6c3dc1a815` |
| installer/verify-binding-runtime.mjs | `c0ae3cec5cce63ee342facc158bae2b93dc170dd0098e87cee0276f34267485d` |
| verification/web/gat-agent-team-panel.e2e.ts | `6c1e2a631e970a39afc8c0bc7f6247f8f862a245bfee2349ef6d4fa28da05743` |

## Eight AIP Done Criteria audit — final evidence still pending

The approved WK/direct-continuable selection governs applicability; it does not weaken required direct-path denial, labels, scope or built/profile evidence. Proposal §11 explicitly makes isolated execution/closing portions of T16–T22 and isolated submission portions of T23 conditional. No new isolated runner, principal mapping, submission lifecycle or live deployment is required to close this selected implementation.

| AIP criterion | Independent assessment before final sealed replay |
| --- | --- |
| 1. U1/P01–08/API/lifecycle/owners and U2/U3 | Approved-decisions records explicit HUMAN choices and later isolated host/integration authority; final U2/U3 and open-point pointers must remain consistent with final receipts. |
| 2. Prior design coverage and current official design/maps | DD §8 prospectively covers connected source and review corrections, installer layout, fixtures, runtime peer and verifier refinement; final mappings/design verification and chronology references remain required. Separate prerequisite history is not rewritten. |
| 3. Binding/adapter/ownership/tools/refresh/replay/deadline conformity | Source review PASS after every identified correction; independent 40-row hash checks and real/port/barrier suites support the selected direct path. |
| 4. T01–T23/freeze §13 | No additional workflow identified beyond final built/WS/browser/default-core/SDK/packed/guard checks already scheduled. The actual 60-cell prerequisite authorization matrix (19 allowed/41 denied) covers the full declared tuple product; isolated conditional rows must remain explicit N/A with approval evidence. |
| 5. Pinned host/provider and real integration independent of fakes | Pins 5c02ce9/a8e2154 and final core receipt are qualified; final sealed built Loader/control-context checks must identify the same bytes. |
| 6. Default/Durable profiles, safe SDK/Web, distribution, replay/downgrade | Final same-target browser, runtime, SDK, packed, installer and native evidence remains pending. Package rollback restores preimages and retains data; it is never an event downgrade. Beforeimages at restored5c02 refuse attached-member membership/recovery/mailbox release. V2-only binary resume of v3 remains unsupported/refused, with no stripping/migration claim. |
| 7. Independent review, design/task verification and lint | Source defects are resolved. Current source logs independently show333 tests/24 files and767 host boundary tests/29 files PASS; counts overlap. Normal complete typed lint has no diagnostics with owner receipt, including the earlier172 owners. Final scoped lint, accurate whole-tree disclosure and final design/map/receipt consistency remain required. |
| 8. Capture dispositions and complete handoff | Explicit per-capture disposition/backlog destination and final design/source/check/deployment/publication status are required before governance close. No new user approval is inferred for publication/activation. |

The333-test suite discloses the same nonfatal FileHandle garbage-collection warning; this audit does not relabel it as an assertion failure or silently erase it. Earlier source/build/browser/SDK receipts remain historical where they predate the final gateway peer/artifact. No overall AIP acceptance is granted by this audit.
