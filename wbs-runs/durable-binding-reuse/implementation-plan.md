# Durable binding reuse — implementation plan

Date: 2026-10-04 (Asia/Tokyo). Status: planning candidate, pending qualification and independent review. Mission root: `wbs-runs/durable-binding-reuse` in the GAT repository.

Execution approach superseded on 2026-10-04 by the HUMAN-selected [AIP-EXEC-024](../../.ai-work/aip/hoinv/exec/AIP-EXEC-024-implement-durable-binding-reuse.md). This document remains technical planning input; its WBS-specific approval, accounting and compilation proposals do not govern AIP execution.

## Outcome and scope

Add an opt-in adapter that binds fresh current GAT execution Sessions to the public WK Durable Agent service. Reuse `assignTask`/`submitExecution`, stable roster identities, exact execution attribution, public Consumer rendering, and provider persistence/release. Existing direct-continuable composition remains supported.

Product changes are limited to GAT `packages/durable-agent/` and the necessary GAT-owned build/export/documentation/distribution metadata. Qualification uses the current DSH Host and real WK provider in disposable storage. No Durable provider/API/storage change, DSH core/loop/Team schema change, second dispatcher, binder-registry prerequisite, global/fork scope, confirmed-memory tool, live profile activation, prior evidence rewrite or Mission Board task10 assignment is included.

## Intended adapter design

1. **Explicit composition.** Export `./execution-composition` separately from `./composition`. Select one WK API-v1 provider and explicit member declarations, canonical workspace, topology assertions, byte limits and review-input policy. Require only capabilities actually used; a read-only adapter must not accidentally require candidate-write support through an old helper. Qualify current public imports and exact provider identity, including Cordis proxy unwrapping.
2. **Exact identity and authority.** Bind only a GAT-attributed isolated execution with exact live Agent/root, Team/member identity, execution ID, Session ID, generation and allowed phase. Freeze the selected declaration for the binding lifetime. Ignore ordinary non-Team Agents and legacy roster/bootstrap Sessions; reject a missing mapping for a selected execution. Provisioning is setup-only. Every model contribution or read requires current active authority and checks identity before and after each await.
3. **Persistent ownership.** Provider identity is canonical workspace/scope/name plus immutable declaration. GAT runtime identity is execution/session/generation. Reuse `coordinatorFor` on the underlying registered provider; reserve workspace/name before provision and release ownership only after physical provider release. A later assignment shares provider storage but starts an unseeded conversation. Overlap fails closed.
4. **Prompt integration.** Install one owner-scoped waterfall during awaited `agent/created`; await `next()` so GAT admission completes before retrieving active context. Add one stable bounded Durable section to the downstream assembly. Register a stable ordinary-work read tool before schema assembly, with an executor that denies unauthorized IDs; reviewer bindings register no memory tools. This avoids changing schemas during assembly and recursive reassembly. Qualify whether this hook covers every actual admitted request, including retries; failure stops this scope instead of silently weakening the requirement. Preserve logged model-visible context and other owners' sections.
5. **Ordinary work.** Use public Consumer context, but filter catalog metadata to exact nonempty `durable-memory:<id>` references in the immutable active assignment. No selection means guidance only and no readable memory. Selected-but-absent IDs fail through the public service. Guard the executable read before and after await and check both body and complete rendered-result byte caps. WK snapshot and body reads have per-call consistency. Candidate and confirmed-write tools are absent.
6. **Review work.** Host explicitly selects reviewer mode and supplies a validated frozen `ReviewPacket` for the exact assigned task/current candidate using the public packet builder. Do not fabricate hashes/receipts, reinterpret freeform brief strings as machine attestations, or silently fall back to ordinary context. Reuse `reviewContribution`, not generic `taskContribution(..., 'reviewer')`. Verify actual fresh transport, whole-prompt memory exclusion, read-only evidence ACLs and host digest/identity rechecks. Packet derivation/public export availability is a qualification question; adding a second runner or schema to solve it is outside scope.
7. **Cleanup.** Join the existing `subagent/closing-child` path and child/plugin effects to one memoized cleanup. Cut off listeners/tools synchronously before awaiting provider calls. Track provisioning/context/read operations; late results cannot install or disclose anything. Await non-cancellable WK work, then release the ref. Avoid an operation awaiting its own drain. Retain unavailable/quarantined ownership on release failure and prove terminal settlement cannot falsely attest successful cleanup. Deadline expiry can detach authority but cannot be described as cancellation of a WK call.
8. **Recovery.** A current live execution may reconstruct a fresh ref from unchanged approved configuration and provider-owned persistent profile. Revalidate exact identity before admission; fail on missing mapping, incompatible service or profile conflict. Verify cold recovery before inbox/model release through existing GAT APIs. Terminal executions stay denied. No bootstrap rebinding, transcript injection, roster redefinition, new persistence fields or retroactive binding receipts.

## Work and dependencies

| Task | Deliverable / DoD | Depends on | Difficulty | Estimate |
| --- | --- | --- | --- | --- |
| Q1 | Prospective qualification delta, actual Host/WK artifact manifest and a complete evidence matrix for reviewer packet/public exports, first request/refresh/logging, cleanup and restart. Exact failures and scope disposition recorded. | — | High | 2–3 h |
| Q2 | Independent assessment of Q1 and the complete implementation/integration/acceptance chain against both design sets. Verdict records unresolved gaps. | Q1 | High | 1 h |
| D1 | Reviewed GAT design amendment describing this additive entry, identity/config, selection/review, refresh, cleanup/recovery and source mapping. Approved design is in place before adapter edits. | Q2 accepted qualification | High | 1–2 h |
| I1 | Adapter, explicit Config, executable selected-read wrapper, package export/build entry and documentation. Reuse helpers only where both paths consume them; no provider/Host changes. | D1 accepted design | High | 3–5 h |
| R1 | Independent source/design review of identity, async revocation, reviewer isolation and lifecycle. Current candidate cleared or precise corrections recorded. | I1 | High | 1–2 h |
| T1 | Focused UT/IT plus keyless Session snapshot and public built-import qualification; complete PASS/NG matrix bound to exact candidate bytes. | R1 accepted source | High | 2–3 h |
| F1 | Final handoff with design/source consistency, exact artifacts/check receipts, limitations and proposed deployment diff/storage/rollback. Technical acceptance is explicit. | T1 accepted evidence | Medium | 1 h |

Base effort: approximately 11–17 hours, plus 3–5 hours reserved for evidence-driven correction/recheck. This is an estimate, not a money cap. Use one writer for the adapter/official design; independent review occurs after each candidate is frozen. Runtime output attempts, review/test disposition and correction tasks remain execution-owned; diagnostic checkpoint 2, ordinary rework ceiling 5 unless the HUMAN approves different limits. No execution budget is charged by this plan.

Q1 must write its intended experimental design before any test-only adapter code. Q1 acceptance is evidence about the real integration path, not a mocked Team fixture or file-exists check. Q2 is independent of Q1's author. Implementation remains blocked if Q1/Q2 discovers missing public operations, impossible reviewer input binding, unqualified request ordering or cleanup/recovery ownership gaps.

## Design application and ownership

Before I1, add an explicitly attributed delta to GAT `DETAIL_DESIGN.md` covering DD-09/DD-15/DD-16 and §5/§8 compatibility, update `BASIC_DESIGN.md` external capability flow, `DURABLE_AGENT_INTEGRATION.md` with the new entry boundary, and `SOURCE_CODE_MAP.md` with prospective mapping. Preserve the frozen member-binding design; any semantic conflict requires a reviewed decision rather than rewriting it. WBS intermediate design may live here, but finalization requires the approved delta consolidated under `docs/gat-design/`.

DA public behavior is unchanged. Its Architecture AD-02–05, Basic BD-02–05, Detail DD-02–04/DD-06–09 and conflicts C-01/02/03/05/06/07/10/11/17 are ordinary external implementation/review/test inputs. If a qualification failure demands a DA change, stop that branch and obtain separate authority; any such change must first amend the owning DA `docs/` design/index/source map/conflict disposition. This plan does not silently close DA conflicts or require rewriting its historical source baseline.

UT uses the accepted detailed delta and DA DD-02–04/DD-06–07. IT uses GAT Basic/Integration and DA BD-02–05. Scenario/snapshot acceptance uses the proposal's qualification cases plus the approved requirement refinements in this plan. Author, reviewer and tester read those same sources.

## Qualification and verification

The real consumer path is existing `team_task_assign` → GAT execution manager → fresh DSH child → awaited binding → logged model request → selected read or evidence-only review → submission/cancellation → joined provider cleanup. Mock only model transport or nondeterministic input. Existing official-adapter fixtures provide patterns, not proof for WK/GAT.

Required scenarios:

- Fresh assignment binds once before request 1. Missing/invalid declarations, provider failure and binding-install failure produce zero model requests and safe failed admission.
- Two members use separate persistent identities. Same-member assignment 2 retains provider data without transcript inheritance. Concurrent same-member owners are denied; a failed cleanup keeps the identity unavailable.
- Worker catalog/tool obey exact assignment selection; unselected, foreign, released, stale-generation and terminal calls deny. Revoke/replace Agent, root or provider during each await and verify no late disclosure.
- Reviewer packet matches contract, candidate, inputs and required receipts. Invalid/missing/stale packet denies admission. Whole logged request has no personal guidance/catalog/body or memory tools; authorized evidence remains readable; no prior conversation is inherited.
- Initial and subsequent actual requests refresh once each without duplicate sections/tools or recursive assembly. Clarify retry semantics with the real model transport path. Model-visible bytes reconstruct from persisted Session events.
- Submit/cancel/Team teardown/adapter disposal cut off authority before drain. Delayed context/read/provision results are discarded or released; failure does not publish false terminal cleanup success; no extra closing request or self-await deadlock.
- Cold recovery rebuilds only authorized live executions; unchanged profile succeeds, profile/config conflict or absent mapping denies; terminal Sessions never reopen.
- Built public entry resolves the selected WK service and Consumer; test Loader retains GAT task tools/initializer and one selected provider. Existing composition regression suite remains passing.

Known command forms, to be scoped to the selected qualification Host after Q1's environment/artifact preflight:

```text
# cwd: /home/hoinv/deepseek-harness
pnpm exec vitest run packages/experimental/gat-core/tests/execution-authority.spec.ts packages/experimental/gat-core/tests/execution-projection.spec.ts packages/experimental/agent-team-durable-agent/tests/binding.spec.ts
pnpm exec vitest run packages/experimental/gat-durable-agent/tests/execution-composition.spec.ts packages/experimental/gat-durable-agent/tests/execution-lifecycle.spec.ts
pnpm exec tsc -b packages/experimental/gat-durable-agent/tsconfig.json
pnpm exec tsdown --config packages/experimental/gat-durable-agent/tsdown.config.ts
pnpm run test:snapshot -- -t gat-durable-execution
```

New test/snapshot names are proposed deliverables, not existing passing checks. Q1 must verify the package target/mapping, tsconfig references, snapshot composition and exact supported launcher before authorizing dependent executable tasks. Build/typecheck may emit dependency `lib/`/`.tsbuildinfo`; snapshot refresh writes expected files. Include those actual effects in the finalized command grants. No broad shell/interpreter grant, online provider call or full repository suite is planned. Public artifact smoke must use a supported test-only Loader/profile and real public imports, not a package bin as an application launcher.

## Execution and deployment gates

This is a technical planning candidate, not an execution-ready WBS. Known qualification questions and precise cross-repository test/build grants remain open; local WBS formats cannot authorize sibling checkout effects by embedding absolute input paths. Finalize those grants against the chosen isolated Host before an executable WBS is approved. Do not broaden the workspace root or fabricate TaskPlans/OutputSpecs merely to make validation pass. No worker was dispatched or independent approval invented.

After Q1/Q2 and design acceptance, seek one implementation decision on the concrete candidate scope/effects. Following T1/F1, present exact selected Web profile/config bytes, verified topology, package resolution, storage creation/bootstrap effects, coordinated activation and rollback. Live GUI verification occurs only after that deployment decision. Leave Mission Board task10 and its existing WBS/evidence/charges untouched until binding/lifecycle qualification and coordinated activation are accepted.
