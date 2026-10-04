# Independent prerequisite security review — AIP-EXEC-023

Date: 2026-10-04, Asia/Tokyo. Reviewer: `/root/prerequisite_review`. Current verdict: **PROVISIONAL — no unresolved R1–R8 implementation blocker; final qualification pending**. This report is a runtime artifact, not approval of deployment or AIP-EXEC-022 production eligibility. Historical findings and intermediate verdicts below retain their original evidence; the latest disposition is at the end.

## Scope and authority

Read root AGENTS.md/local override and active STEP-02 ASC before workspace writes; reviewed AIP-resolved frozen contract `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§7–13 and formal `docs/gat-design/DETAIL_DESIGN.md` §7, source/design/test matrix, host-prerequisites.md and capability-prerequisites.md. Reviewed approved isolated DSH host `/home/hoinv/work/dsh-binding-prerequisites` at base `c291e7961a515f6d7af9304e7fd1d257929aef26`, its AGENTS/packages/docs instructions and current host source. Original dirty DSH is excluded. No source/design patches were authored by this reviewer; implementation owners received findings promptly. Source was changing during review; observations below bind to the stated reproduction and later recheck, not immutable final bytes.

## Blocking findings

### R1 — P1: model request survives a committed revocation in a later async admission listener

Locations at reproduction: approved DSH `packages/core/agent-loop/src/agent.ts:392` awaits serial `agent/model-admission`; `:401` starts model-visible commits and `:422` invokes stream. Root GAT `packages/core/src/index.ts:157` registers its assertion as a normal async listener. A later listener can change canonical authority after GAT checked it; only the request AbortSignal is checked after listeners finish.

Actual composition reproduction used Connection/Gateway signed-cookie HTTP, TeamService, JSONL persistence, AgentLoop, Subagents and Spawn from the approved host. A granted, quarantined child was given an exact approved mission scope. Its scoped later `agent/model-admission` listener awaited real `control.call('revokeMission', lead.id, exactRevision)`. Response committed `status: revoked`, revision 2. The mock provider still received **one request**. Thus this is a demonstrated security failure, not inferred from fixture counts. No input/provider request may be admitted after that committed revocation (freeze §10, DD §7 prompt/model admission).

Required fix/recheck: after all asynchronous admission listeners, synchronously validate live owner guards before input commit and again immediately before provider invocation; no await between final assertion and protected operation. Retain actual HTTP negative regression with zero provider calls and zero new input commits.

### R2 — P1: child release/wake survives revocation during activation flush

Locations at reproduction: root `packages/core/src/roster.ts:215` checks authority before awaiting `reserved.activate`; DSH `packages/subagent/subagent/src/reserved.ts:237` awaits flush, then releases execution without GAT revalidation.

Actual signed-HTTP composition blocked the child `session/flush` during activation, committed exact `revokeMission`, then released flush. `activateMember` resolved successfully and child `agent/status: running` was observed **once**. Provider calls stayed **zero** because a later prompt guard denied. The zero provider count does not satisfy freeze §10's separate wake/release boundary: authority was revoked before actual wake.

Required fix/recheck: synchronous owner guard after durable activation flush immediately before release, with actual blocked-flush/revoke race asserting no child wake, no provider request and stable denial. Recovery must preserve the original initial message and remain gated.

### R3 — P1: unsuccessful claim publishes task authority and release leaves it executable

Original locations: root `packages/core/src/task-board.ts:203` bound task lease before expected-revision/readiness checks; `packages/core/src/authority.ts:101` accepted an undefined owner and every task status except deleted. A stale/blocked claim could retain the minted lease; released/pending/completed task work could still execute. This was reported before owner edits; it was a direct source finding, not an executed full HTTP reproduction in this review.

Owner source re-read now shows validation-only claim inside canonical transaction, lease publication after successful task flush, and `in_progress` plus exact `ownerId === agent.id` in task-bound bind/assert. Lead administration is explicitly mission-matched. **Fix inspected; actual staged-host negative regression still pending independent recheck.** Required cases: stale/blocked/failed-flush claim yields no newly usable lease; release/complete/reassign invalidates task work; task association is immutable.

### R4 — P2: repeated disposal hides a failed physical cleanup

Location at reproduction: DSH `packages/subagent/subagent/src/reserved.ts:280` set `disposed = true` before awaiting registry disposal; subsequent calls returned success.

Inline actual-module reproduction constructed a bounded owner capability with a rejecting physical disposal primitive: first `r.dispose()` rejected `physical cleanup failed`; second resolved; primitive count was **1**. Physical cleanup idempotency alone does not preserve the required shared failed settlement. Required fix: memoize the physical cleanup Promise/outcome, retaining late failure observation; repeated/concurrent calls share rejection. Host owner acknowledged and is implementing.

### R5 — P2: malformed durable admission lacks stable conflict denial

Location at reproduction: DSH `packages/subagent/subagent/src/reserved.ts:90` dereferences durable `event.data.version` before checking object validity. Inline actual `foldInitialAdmission` calls with null/undefined durable admission payloads threw raw `TypeError`, no stable code. They did deny execution, but violated the frozen stable state/error contract. Required parser regressions: null, primitive, array and malformed required fields fail `CONTINUABLE_STATE_CONFLICT` before recovery/materialization. Also inspect reserved descriptor payload handling for the same durable-field dereference class. Host owner acknowledged.

### R6 — P1: explicit v2 replay preserves receipt-like self-approval authority

Locations at reproduction: root `packages/core/src/projection.ts:388` adapts v2 missions by spreading `rawMission`, retaining `approval.eventId/digest/humanSessionId`; its shared mission and plan approval schemas accept those fields for versions 2 and 3. The v2 plan approval branch also directly stores the supplied receipt fields. Resetting generation values to zero does not remove authority because newly bound leases capture the same zero generations.

Inline actual approved-host staged-module reproduction applied a version-2 `team/mission` snapshot with `status: approved`, revision 1, empty legacy tasks, `approvedRevision: 1` and model-authored receipt-like strings plus matching root id. Projection failure was undefined; actual `TeamExecutionAuthority.bind` and `assert` **accepted** the v2 mission as executable. This violates DD §7's explicit legacy-authority removal and freeze §10 HUMAN provenance. The scenario matters even if ordinary historical snapshots did not carry receipt-like fields; the adjacent adapter must never reinterpret v2 fields as current trusted authority.

Required fix/recheck: v2 mission and plan adapters retain their historical safe display approval only, strip every executable provenance/generation field, and prevent stored projection checkpoints from resurrecting pre-fix legacy authority. Add explicit receipt-like v2 negative fixtures for simple/governed mode. Authority owner has been informed; recheck pending.

### R7 — P2: empty-attachment creation failure can await cleanup without the configured deadline

Exact review locator: root `packages/core/src/roster.ts:333` and `:334`.

Current root source `packages/core/src/roster.ts`, spawnAdmitted failure block, awaits `reserved.abort(signal)` and `reserved.dispose()` before bounded `stopTeammates`. A failed persistence call need not cancel the request signal; a never-settling child flush or physical disposal therefore leaves creation waiting without the configured GAT disposal timeout. DD §7 reserved lifecycle says shared bounded teardown; freeze §8.4 requires one total cleanup deadline. This is a source-level concern, not a newly executed failure reproduction. Root was asked to clarify applicability or implement intended bounded cleanup before source, with an existing-style failure regression. Do not apply the binder-only deadline guarantee to this bootstrap path without evidence.

### R8 — P1: Team lifecycle cutoff is absent from execution/lease admission

Current root `packages/core/src/index.ts:215` bindExecution and `:225` assertExecution invoke canonical authority without checking `lifecycle.disposed`. The final exact-Agent synchronous guard calls assertExecution. `disposeRuntime` closes lifecycle before awaiting admitted mutations/child drains, during which projected canonical approval and Agents remain live. A valid lease can therefore still pass activation/model admission while Team execution is closing; new recoverMember/activateMember also lack lifecycle cutoff/fused cancellation. Constructor task callbacks invoke authority directly and must not bypass the same cutoff. This is a demonstrated source-path inconsistency, not a custom execution reproduction in the resumed review. DD §7 closed scopes and freeze §8.4 admission cutoff require fail-closed effect admission during that interval. Root was asked for design-first correction and existing conformance regression holding teardown settlement while attempting activation/model/task execution.

## Recheck in progress

R8 also includes policy withdrawal order. GAT guards belong to outer GAT effects at `packages/core/src/index.ts:173`; Cordis `vendor/cordis/src/fiber.ts:676` unloads effect cleanups concurrently. Guard/listener removal can precede the child drain while disposeRuntime awaits mutation settlement. A lifecycle predicate alone is insufficient after its guard disappears: child admission must close synchronously before policy withdrawal, or retain a closed exact-generation guard through physical detachment. Root was notified to qualify actual plugin unload while a model route/settlement is held, not only direct lifecycle assertion.

R1/R2 current source now exposes owner-scoped synchronous exact-Agent guards, checked after all async model-admission listeners, again immediately before stream, and through the factory-owned releaseExecution after activation flush. Actual signed HTTP regressions are present in prerequisite-composition.spec.ts. R3 current source validates claim without publishing authority and binds only after successful task flush; task bind/assert requires in_progress plus exact owner, and an explicit reassignment regression is present. R4 caches the shared disposal Promise; R5 validates admission and reservation records before field reads, including generic cold resume and owner recovery negatives. R6 strips executable v2 mission/plan receipt fields and v2 task association, with projection stateVersion 9 against released baseline 8. These fixes match formal DD §7 by inspection. Independent final regression and final source hashes are pending stable-source notification; prior red observations remain in this report as history.

The latest formal DD §7 adds mailbox false-flush publication, model-visible queue/recovery wording, direct admitted live delivery and per-handle recovered release semantics before the corresponding ongoing corrections. Current direct target Agent steer revalidates exact authority immediately before wake; false target flush leaves root delivery unacknowledged; every recovered reservation has a separate releasedReservations identity. Final qualification must exercise warm follow-up, consumed-initial cold recovery and no-lease quarantine rather than infer gate state from durable activated history.

## Design-before-code chronology

`04_findings.md`, Corrective-edit chronology, explicitly records two earlier production corrections (projection registration ordering; avoiding reopening an already released warm reserved handle) made without a new intended-design paragraph first. Current source follows existing formal invariants and does not introduce a conflicting contract decision, but this does **not** retroactively satisfy the workspace's every-change design-before-code rule. This reviewer preserves the process gap and will not state universal compliance. Later mailbox/recovered-release deltas are now stated in formal DD §7 before subsequent implementation.

## Positive observations and executed checks

Registry registration snapshots capability/reference arrays and callback/name identity; callback provenance survives changed-name aliases. Required-descendant resolution fails closed on absent/unclassified/cyclic references. Execution identity/arguments and capability union are protected; ALS derives active-parent Agent/root identity and settlement expires tokens. Monotonic guards recheck before policy, after async policy, before wrapper dispatch and before body. Internal PTC publication follows admission, and rejected descendants generate no start/settle effects. These are source observations backed by focused fixtures, not arbitrary trusted-plugin sandboxing claims.

Authenticated HUMAN receipt minting is private to verified Connection HTTP dispatch; exact endpoint, wire digest, resolved object identity, request digest, active lifetime, signal and one-use consumption are enforced. Gateway tests exercise wrong Agent/request/action, nested use, direct unverified calls, invalid/missing cookie, hostile Origin, replay and retained sync/async scope. Direct generic Gateway calls cannot mint HUMAN authority. Root canonical journal's pending/failed publication guard rejects authority during pending and false-result flush; grants publish after success. Full authority durability matrix remains root qualification responsibility.

Reserved source keeps a durable quarantined initial item, idempotent key/content identity, child mutex, cold-recovery gate, tombstone before abort teardown, and claimed-but-uncommitted initial restoration. Direct waking methods remain gated and legacy generic recovery rejects explicit reservations. Per-request refresh runs before first assembly and every retry; model-visible refreshed context is logged/reconstructable. Findings R1/R2 limit admission qualification despite these observations.

Reviewer executed approved-host focused suites: `packages/api/gateway/tests/gateway.host.spec.ts`, `packages/core/tools/tests/capabilities.spec.ts`, `packages/subagent/subagent/tests/reserved.spec.ts`, `packages/core/agent-loop/tests/prepare-prompt.spec.ts`: **4 files, 73 tests passed**, exit 0 (11:20 JST/host process start shown as 11:20:16). A duplicate direct-binary run also passed 73/73; it adds no coverage. `pnpm exec vitest` unexpectedly performed auto-install of three cached workspace dependencies and hook setup before tests; root was informed to audit lockfile footprint. No authored source/design edit was made.

## Initial evidence gaps — latest disposition below

- R1/R2 corrected final synchronous guard with actual authentication/race regressions and reviewed generation/disposal behavior.
- R3 staged actual-host task claim and release/completion/reassignment regressions; R4/R5 fixed-module repro and focused negative fixtures.
- Exhaustive freeze §13 mode/enablement/mission/plan matrix, aborted ingress lifetime, exact plan-receipt replacement, failed approval and failed claim flush cases.
- Keyless transcript snapshots, both SDK expected-output changes, actual Loader/process composition and built public imports.
- Final source/design/map/hash consistency, generated persistence/catalog freshness, final documentation gates and AIWS scoped/whole-tree lint as applicable.
- Parent AIP-EXEC-022 binder generation/attachment recovery integration. This review does not qualify its production binding path or deployment.

Tests supplied by other owners (host230/capability703/root composition) were read as reports and are not represented as independently rerun here. No PASS verdict will follow solely from their counts.

## Resumed source review — R7/R8 and driver boundary

R7 fix inspected in current ROOT `packages/core/src/roster.ts:360`: creation failure uses one fresh configured `BindingDeadline`; abort and dispose start synchronously before awaits. Abort uses the deadline signal; dispose retains its actual unbounded physical Promise, while only the GAT await races the shared deadline. Actual reserved host methods synchronously close execution and memoize disposal. Roster retains the physical disposal settlement observer after its bounded await returns, including late failure aggregation/logging. The existing bounded-failure authority regression blocks actual child flush, expects bounded aggregated failure and a failed roster row, observes zero provider calls, then releases flush and observes child removal. Independent final execution is pending staged-source readiness.

R8 fix inspected in current ROOT `packages/core/src/index.ts:174`/`:183`/`:963`/`:973`, `packages/core/src/roster.ts:196`, and `packages/core/src/journal.ts:54`: each guard disposer synchronously closes lifecycle, shares idempotent runtime drainage and removes the final guard only afterward. Runtime cutoff closes every reserved gate and interrupts live children before awaiting mutations. Journal authority admission checks lifecycle first; task mutations, member-add approval, explicit recovery and activation are admitted/tracked. This fixes the original source paths by inspection. Existing authority fixtures block claim publication during actual Team unload and verify no post-cutoff lease/task admission, and now hold a real child activation flush, unload the actual Team fiber, directly observe denied final host model and activation guards, then observe denied activation after release and zero provider calls. Independent execution is still pending.

The trusted independent driver boundary in approved DSH `packages/core/tools/src/index.ts:826` uses the current `ctx.get('agents')` service, exact Agent object identity and AsyncLocalStorage.exit only around fresh host driver startup (`packages/core/agent-loop/src/agent.ts:224`). Ordinary nested execution parent inference/capability checks remain intact. No model Tool or Remote exposes this scheduling operation. Source matches formal DD §7, Prerequisite independent Agent driver context; actual built SDK child-to-parent relay evidence remains pending.

Independently executed existing `scripts/catalog-source-files.spec.ts` with direct Node Vitest: **1 file, 10 tests passed**, exit 0, process start 11:41:24, duration 653ms. Explicit replacement exclusions are tied to matching build references and root exclusion rules; ambiguous simultaneous selection fails and unrelated/default discovery remains conservative. This result is separate from root-reported catalog counts. Compiled declaration presence was inspected for host guards, capability/reference metadata, reserved methods and GAT binding/recovery methods; declaration presence is not a runtime public-import receipt.

Latest inspected source is consistent with formal DD §7 intended R7/R8 and driver paragraphs. Historical design-before-code gaps above remain recorded. Verdict remains **CHANGES REQUIRED; final staged regressions and qualification evidence pending**; no new concrete source blocker was demonstrated in this resumed read-only review.

## Stable staged-source independent recheck

Root declared production source stable in the approved isolated worktree. Reviewer reran existing suites read-only with the direct Node binary, without new reproducer scripts, source edits, package installation or snapshot-update options. CWD for both commands: `/home/hoinv/work/dsh-binding-prerequisites`; HEAD remains approved baseline `c291e7961a515f6d7af9304e7fd1d257929aef26` with the reviewed prerequisite changes in the worktree.

```text
node node_modules/vitest/vitest.mjs run packages/api/gateway/tests/gateway.host.spec.ts packages/core/tools/tests/capabilities.spec.ts packages/subagent/subagent/tests/reserved.spec.ts packages/core/agent-loop/tests/prepare-prompt.spec.ts packages/experimental/gat-core/tests/authority.spec.ts packages/experimental/gat-core/tests/projection-events.spec.ts packages/experimental/gat-tools/tests/prerequisite-composition.spec.ts --reporter=default
```

Result: **7 files / 133 tests passed**, exit 0, process start `12:30:29`, duration `10.24s`. Counts by file: gateway 45, capability 14, reserved 21, prepare-prompt 9, authority 16, projection 23, actual signed HTTP composition 5.

```text
node node_modules/vitest/vitest.mjs run packages/core/tools/tests/ptc.spec.ts packages/core/tools/tests/scoped.spec.ts packages/core/tools/tests/tools.spec.ts packages/subagent/subagent/tests/control.spec.ts packages/experimental/gat-profile/tests/profile.spec.ts packages/experimental/gat-tools/tests/tool-team.spec.ts --reporter=default
```

Result: **6 files / 305 tests passed**, exit 0, process start `12:30:53`, duration `12.75s`. Counts by file: PTC 91, scoped tools 27, tools 136, subagent control 23, actual Loader profile 2, scoped Team tools 26. This independently exercises immutable capability registration/aliases/union, parent token lifetime, monotonic denial, PTC publication boundaries, complete-envelope fast paths, simple/governed routing, configured readiness, scoped HMR and actual Loader replay.

| Finding | Current disposition and evidence |
| --- | --- |
| R1 | Fixed. Actual signed HTTP later-async-listener revocation test denies provider dispatch; host prompt tests verify the synchronous guard after async listeners and immediately before stream. |
| R2 | Fixed. Actual signed HTTP held-activation-flush revocation preserves child gate with zero wake/provider; reserved release calls the final synchronous owner guard. |
| R3 | Fixed. Actual authority cases deny stale/blocked/false-flush claims before lease publication and invalidate released/completed/reassigned task ownership. Task scope requires canonical association, active exact owner and executable status. |
| R4 | Fixed. Reserved concurrent/repeated disposal shares physical settlement and preserves cleanup rejection. |
| R5 | Fixed. Malformed durable admission/reservation negatives return stable conflict denial and cannot recover/wake the child. |
| R6 | Fixed. Receipt-looking v2 mission and governed-plan fixtures cannot mint execution authority; adapter strips provenance and legacy task associations, and projection stateVersion 9 invalidates released baseline-8 checkpoints. |
| R7 | Fixed. Actual blocked-child cleanup test returns bounded aggregate failure, retains gate closure and later observes physical child removal; source retains the actual disposal Promise outside its deadline await. |
| R8 | Fixed. Actual Team unload with held child activation flush directly rejects final host model and activation guards; held claim publication cannot bind a post-cutoff task lease. Guards survive until runtime gate closure/drain. |

Formal consistency reviewed against DD §7's durable authority, synchronous owner guard, live delivery/recovered release, failed-spawn deadline, withdrawal cutoff, independent driver, authority publication families and active member authority paragraphs. The final host driver fixture additionally rejects stale/disposed generations, preserves the detached root across an await, restores ordinary nested parent/union and retains cross-Agent nesting denial. No unresolved implementation blocker was found among R1–R8 at these bytes. This conclusion does not erase the recorded chronology gaps.

Source SHA-256 checked before and after the first run, unchanged:

```text
d8d46efb267c9b983266b2424d24d4658b1217f093ab268b6ec1e60e29376c97  packages/core/agent-loop/src/agent.ts
d3e65703e2b0e0c5c41eb2597ac3cabe4baec1c9ac0a033f48823a09f49914e7  packages/core/agent-loop/src/index.ts
a0081433b8be817fbdd9c1280973f9950ff189375a1e8b75b905b6e9a74a6fcf  packages/core/agent/src/index.ts
de773858f9674e21acf881f28267358013032738fcb62018fd3a9dec3dc48b5c  packages/core/tools/src/index.ts
e23d9488888c9df5b8cbf3705663782687989862538bb9d1e69996bc7075e595  packages/subagent/subagent/src/reserved.ts
516a26552a23c07becf9954a4c86bee2d94ceb5608c709b32f5e5de4ec5d4a0f  packages/experimental/gat-core/src/index.ts
3e3ad042cddcc7cbe1953cd8ce68ee97ba53591560973843176d093f0a2a3311  packages/experimental/gat-core/src/authority.ts
2a25191be482cab6b5c8bf2d93e8434eefa2339b0eaf17bc921e6941dad821d2  packages/experimental/gat-core/src/journal.ts
763a3afe65dd3fc762b1a6b9aad0909b30751c7b3908c453c92f0d708674f8ac  packages/experimental/gat-core/src/lifecycle.ts
968c40b23a9308afd4b7b60e7677c101d40358c334b0e7445aac23273d4bd2a2  packages/experimental/gat-core/src/roster.ts
8669e8a46605e2d10c8f5177da60a0e114e199fa37842ff269e497d59729dc62  packages/experimental/gat-core/src/projection.ts
b134eec6087435fd732287b62792d05a1e088053a4215b84eea77e841f028a66  packages/experimental/gat-tools/src/index.ts
```

Current verdict: **PROVISIONAL — no unresolved R1–R8 implementation blocker; final qualification pending**. Remaining parent qualification includes the recovery `team.spec` fixture investigation, final full builds/documentation/generated-artifact checks, built SDK relay/expected projections, final runtime public imports and AIWS lint. This reviewer has not independently rerun or accepted those final receipts yet. AIP-EXEC-022 bound-member production integration and deployment remain outside this prerequisite acceptance.

### Subsequent parent receipts reviewed

Read `verification/public-built-final.log`: plain Node public package imports PASS, including host AgentLoop/Subagents/Tools and GAT core/tools; observed two requests, one refresh, zero denied effect bodies, canonical task association and draft lease denial. This is a reviewed parent-produced runtime receipt, not a second independent smoke execution.

Read SDK qualification, accepted final TypeScript replay (`sdk-ts-final-replay.log`: 2 files, 10 passed / 12 intentionally filtered skipped) and four successful Python final replay receipts, fixture-diff review and predecessor audit. The lifecycle diff retains complete initial content/parent steering and existing prompt/tool/wire sidecar hashes; each affected child adds one reservation fact and persisted/activated admission facts. Earlier failing relay evidence remains visible in the historical lifecycle-refresh log and is superseded by accepted refresh/replay evidence. The updated SDK driver asserts real child tool delivery and parent history, not solely model prose. Independently ran `sha256sum` for the seven CLI/host/SDK built runtime entries; every current value matches both sides of `sdk-final-hash-comparison.json` (changed list empty). SDK evidence therefore applies to those same current artifacts without a redundant rerun.

Documentation remains incomplete: the latest reviewed `doc-sync-final-02.log` records 32 passing gates and two failed gates (doc graphs and export JSDoc); root is correcting them. Recovery Team fixture and final AIWS lint receipts also remain pending. Overall verdict stays provisional despite all R1–R8 implementation findings being resolved.

## Closure review follow-up — final reconciliation pending

Read-only reviewer `/root/closure_review` reread actual root AGENTS/local override, AIP-EXEC-023, STEP-06 ASC, wiki-resolved frozen contract §§7–13 and formal DD §7, current authority/matrix/recovery sources, and the parent qualification receipts. The corrected recovered-dispatch fixture queues while inactive, explicitly recovers the exact named child, holds the actual team-message receipt once, and independently observes tracked dispatch cancellation, retained unacknowledged input, awaited disposal and physical child removal. Root/staged `team.spec.ts`, `authorization-matrix.spec.ts` and `task-board.ts` were byte-identical at this inspection. Parent's final GAT receipt records 16 files / 210 tests passed; this reviewer did not rerun that receipt.

The actual 60-cell matrix fixture and its machine receipts were inspected. Authenticated HTTP controls establish the real mission/plan states; the actual dispatcher body counter records 19 allowed effects and 41 denials, with zero provider requests throughout. Absent selected scope includes an unrelated approved mission without implicit selection. Disabled/current and disabled/stale tuples are genuinely reachable under mounted Spawn/Fork providers and the default empty restricted-tool configuration. This is source-and-receipt review; a final independent rerun is still withheld until source stabilization.

OP-01/OP-02 are now explicitly resolved; OP-03 is deferred to parent release/compatibility qualification and separate deployment approval. The protected-original audit reports unchanged HEAD and 365 unchanged protected files, with the original DSH `AGENTS.md` differing outside this workstream; `04_findings.md` records its 12:29 JST modification and the absence of a task-issued edit. Do not claim all 366 original file hashes remain unchanged. Whole-tree AIWS evidence has 0 errors, 37 warnings, 3005 information findings and 1 accepted finding; the warnings remain visible and are not a universal clean-tree claim.

During public JSDoc completion, the annotator split `task-board.list`'s return expression across a newline and separately lost the `export` on `ATTACHMENT_LIMITS`. Root reports both restored and retains both accidents as process history. These are additional annotation incidents, separate from the two earlier design-before-code chronology exceptions. A comments-stripped self-comparison cannot independently prove equality to the pre-annotation source; final supported compilation, built JavaScript comparison and runtime regression receipts are required.

The new applicable `source-lint-jsdoc.log` is red, including style/type lint findings. Root assigned a capable reconciliation owner and wrote formal DD §7's intended source-lint reconciliation before that fix phase. Source is explicitly **not stable** at this point. This reviewer made no production or design edits, authored no reproducer, and ran no package-installing commands in this follow-up. Final existing-suite recheck and final receipt/vote are deferred until root supplies stable source, supported compiler, the new 270-test qualification, applicable scoped source lint, built runtime comparison, final documentation and governance lint evidence.

Current verdict remains **PROVISIONAL — R1–R8 resolved by prior independent evidence; final source reconciliation and qualification pending**. Parent AIP-EXEC-022 production binder integration, release compatibility and deployment are outside this prerequisite review.

## Final stable source independent behavior recheck

Root declared source stable after source-lint reconciliation. Reviewer read formal DD §7 “Prerequisite source lint reconciliation” and `lint-reconciliation-plan.md`, then inspected the correction delta against `verification/lint-reconciliation-before/`. Unknown views preserve malformed task/prepared/binding validation instead of deleting runtime checks. Erased `as Error` assertions preserve the actual non-Error cancellation/rejection values. `failedChild` captures the same non-undefined reserved handle before synchronous abort/dispose startup and retains physical settlement ownership. Attachment descriptor/size/digest validation remains intact; `export const ATTACHMENT_LIMITS` and same-line `task-board.list` return are present. Projection changes are formatting; exact authority guard order and short-circuit denial remain intact. No new concrete source blocker was found.

Reviewer independently executed existing suites with direct Node, without source edits, custom repro scripts, package installation or snapshot updates. CWD `/home/hoinv/work/dsh-binding-prerequisites`, approved HEAD `c291e7961a515f6d7af9304e7fd1d257929aef26`:

```text
node node_modules/vitest/vitest.mjs run packages/experimental/gat-core/tests packages/experimental/gat-tools/tests packages/experimental/gat-web/tests packages/experimental/gat-profile/tests --maxWorkers=3 --reporter=default
```

Result: **17 files / 270 tests passed**, exit 0, start `12:52:02`, duration `12.29s`. Coverage includes the 60 actual authorization cells, canonical authority (16), projection (23), signed HTTP composition (5), actual Team lifecycle/recovery (66), attachment bounds, binder preparation/reconstruction, persisted replay, scoped tools, browser consumers and Loader profile. This is a newly executed independent receipt; it does not relabel parent evidence as independent. Test-run output is retained in reviewer tool receipts (session 35590).

Reviewed parent `gat-source-lint-final.log` is empty successful output; root reports exact required Oxlint exit 0. Earlier red `source-lint-jsdoc.log` remains historical. Final overall vote still waits for root's supported compiler, built-JavaScript comparison, public artifact/hash qualification, documentation/generated-reference receipts and final governance lint. Historical chronology/annotation incidents and original AGENTS.md difference above remain recorded.

### Final built artifact receipts and equivalence review

Root reports exit 0 for final supported host/compiler bundle and client/compiler bundle (`host-qualified-{types,bundle}.log`, `client-qualified-{types,bundle}.log`). Reviewed `public-built-qualified.log`: plain Node imports eleven public runtime packages and observes two requests, one refresh, zero denied effect bodies, canonical task association and draft-lease denial. This is a reviewed parent runtime receipt, not an independently rerun smoke.

`built-js-comparison.json` uses TypeScript JavaScript parsing/printing with comments removed: GAT tools normalized output matches exactly; **GAT core does not match exactly**. Reviewer read the full `built-core-semantic-review.diff` against the actual source reconciliation. Core differences are equivalent single-read aliases, the object-held acquisition flag with the same closure lifetime, callback statement form, rejection aliases preserving the same values, malformed-input aliases retaining identical predicates, and `failedChild` capturing the same handle before immediate cleanup startup. Removing the second optional chain on `mission.approval.digest` remains fail-closed because the preceding exact nonempty lease event-id comparison already rejects absent approval. The pre-comment/final built diff contains no remaining lost attachment export or split-return behavior. This is substantive equivalence review backed by the independent 270-test run, not a claim of exact core AST equality.

Independently hashed the seven current built CLI/host/SDK entries with `sha256sum`; all match both columns of `sdk-qualified-hash-comparison.json` (no changed entries). Prior qualified TypeScript/Python SDK replay receipts therefore still bind those same current runtime artifacts. Final documentation/generated-reference and governance receipts remain pending before the overall vote.

## Final independent vote — PASS for AIP-EXEC-023 prerequisites

The final prerequisite implementation is **PASS** within the approved source-and-artifact scope. R1–R8 have no unresolved implementation blocker. Final lint correction inspection, the independently executed 17-file/270-test integration run, prior independent host/capability suites, authenticated ingress/composition negatives and complete actual authorization matrix support the reserved lifecycle, awaited prompt refresh, exact durable authority and immutable nested capability requirements. No conflicting decision against the frozen contract or formal DD §7 was found. This vote supersedes the provisional verdicts above while preserving their historical observations.

Final receipts reviewed: supported host/client compiler and bundles exit 0; required source Oxlint exit 0; public built smoke passes with eleven runtime imports and actual request/denial counters; SDK artifacts retain the replay-qualified hashes; `doc-sync-accepted.log` records **34 passed / 0 failed / 0 skipped**, including the required documentation, catalog, pairing, generated-reference and site gates. The previous 33/34 failure and all prior failures remain historical. Reviewer independently verified all **57** current root/staged source/test hash pairs against `tested-source-final-hashes.json`, with zero changes since that receipt. Current map/source anchors were spotchecked; root retains responsibility for completing final mapping report packaging and handoff metadata, without changing qualified production source.

Reviewer independently ran final scoped strict governance lint:

```text
python3 .ai-work/tooling/lint_all.py --scope task --workspace .ai-work/workspaces/hoinv/TASK-20261004-exec-023 --aip .ai-work/aip/hoinv/exec/AIP-EXEC-023-implement-binding-prerequisites.md --strict --format text
```

Result: exit 0, **0 errors / 0 warnings / 0 information findings**. Reviewed final whole-tree strict receipt `governance-whole-tree-accepted.log` retains exit 1 for **37 historical warnings**, with 0 errors, 3005 information findings and 1 accepted finding. This vote does not claim the entire tree is warning-free.

Process limitations remain explicit: two prior design-before-code corrective-edit gaps, both corrected API annotation accidents, and the outside-workstream original DSH `AGENTS.md` hash difference. Current source/design consistency and behavior were independently checked; that evidence does not retroactively erase those incidents. GAT core normalized JavaScript differs and was substantively reviewed as equivalent; only GAT tools has exact normalized equality. SDK checks use source facades with the built CLI/host runtime and do not qualify an installed release package.

This is a substantive reviewer vote only. It performs no AIP/mission/output acceptance mutation, release, merge, deployment, profile activation or canonical promotion. Parent AIP-EXEC-022 production binder integration and changed-host compatibility/package qualification remain outstanding outside this prerequisite scope.
