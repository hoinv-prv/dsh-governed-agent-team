# Host lifecycle and prompt refresh prerequisite evidence

Working tree: `/home/hoinv/work/dsh-binding-prerequisites`, approved baseline `c291e7961a515f6d7af9304e7fd1d257929aef26`. No deployment. Original dirty DSH is preserved by root baseline audit.

## Design read and applied order

Read project AGENTS and AIWS.local, DSH AGENTS/packages/docs rules, frozen contract §§7–9/13–14, formal DETAIL_DESIGN §7, active STEP-01 context, design-delta and source-design-test-matrix. AIP-resolved paths used; registered retrieval misses/raw fallback are in the root design/ASC evidence. Intended DSH architecture/subsystem/README/Agent Note prose preceded source changes. Final English/Chinese pairs and sidecars reflect the verified implementation.

Owning design: DSH `docs/architecture.md` Turn flow / Reserved execution and prompt preparation; `docs/subsystems/core.md` Prompt preparation and reserved execution; `docs/subsystems/subagent.md` Reserved continuable children; owning `packages/{core/agent,core/agent-loop,subagent/subagent}/README.md` Reserved admission and request preparation; `.agents/notes/implemented/architecture/2026-10-04-reserved-continuable-admission.md` Problem/Decision/Alternatives considered/Consequences. Architecture details were relocated to owning references to keep all budgeted docs within ceiling. Source/design consistency was checked against durable facts, actual request histories, and negative dispatch observations.

## Exported owner operations

`ctx.subagents.materializeContinuable(ContinuableMaterializeSpec)` accepts provider/label/childId and request without prompt. `recoverContinuable({childId,parent,provider?,signal})` validates exact live parent and child-owned descriptor, and reconstructs behind the closed execution gate even for activated history. Both return `ReservedContinuable`: childId, exact agent, memberScope, state, initialMessageId, persistInitialPrompt(content,key,signal), activate(signal), abort(signal), dispose(signal?). No GAT dependency or arbitrary binder callback enters DSH internals.

The initial item is a version-1 `subagent/initial-admission` fact, quarantined outside the runnable inbox. Persistence and activation facts flush before release. Same key/content yields the original id; conflicts are stable. `agent/execution-reserved` v1 distinguishes explicit owner recovery from automatic legacy recovery. Child serializer linearizes transitions. Abortion writes/flushed tombstone before teardown; owner cutoff closes execution synchronously. Cleanup deadline returns promptly with late cleanup observed. Activated recovery restores the same initial message if the first driver claimed it without committing `user/message`; a consumed message is not reinserted. Explicit reservations reject ordinary continuation delivery and generic resume. Legacy start uses all stages and retains automatic continuation delivery/recovery, original error priority and teardown observations.

Core factory advertises `supportsDeferredExecution`; incapable factories deny before construction effects. Deferred creation/resume gates all direct Agent wakes. Owner-only handle release/close capabilities preserve pending explicit-owner work for recovery. Scoped `agent/prepare-prompt` {agent,turn,step,attempt,signal} runs before assembly on first attempt and every retry. Retries refresh sections, context and tools without repeating pre-step/user admission. Scoped `agent/model-admission` revalidates authority after async route preparation and before input commit/provider dispatch. Existing agent/request remains route-only. Refreshed model-visible input derives from logged system/message and runtime-context user/message facts.

## Source files

DSH subagent: `src/{continuation,continuation-activation,reserved,index,types}.ts`; core/agent: `src/{index,runtime-types,types}.ts`; core/agent-loop: `src/{agent,index}.ts`. Root owns generated event catalogs and required-event declarations; host source supplies payload/JSDoc annotations for regeneration. Tests: `subagent/tests/reserved.spec.ts`, `core/agent-loop/tests/prepare-prompt.spec.ts`; legacy continuation final-flush fixtures now observe actual turn completion, and prompt retry assertions use refreshed assembly semantics.

## Verification

- `host-qualification-05.log`: eight focused files, 230/230 pass: continuation, inheritance, reserved lifecycle, prepare-prompt, system-prompt admission, interception, request reconstruction, inbox.
- After bounded abort, captured-generation flags and admission tracking changes: `host-lifecycle-final.log`: reserved 9/9 and prompt refresh 4/4 pass. `host-factory-final.log`: prompt/unsupported-factory suite 5/5 pass; incapable factories create zero resources.
- `host-types-final.log`: focused `tsc -b packages/subagent/subagent packages/core/agent-loop` clean.
- `host-lint-final.log`: focused source/test oxlint clean. New arbitrary synchronous Session event scans were removed; durable observations initialize state and scoped session events update admission state.
- `host-pairs-final.log`: seven named documentation pairs consistent. `host-doc-budgets-final.log`: all eight budgeted docs within ceiling.
- Whole corpus export-JSDoc and Agent Note-format checks also ran. Host files have no remaining export-JSDoc findings; global findings belong to GAT/other prerequisites, with complete raw logs retained for root final checks. Earlier failing logs retain regression investigation evidence; final results above supersede them.

Root still owns generated persistence/Cordis catalog regeneration, final broad docs/type checks, built public import proof, actual Team authority integration and independent review. No claim of deployed or supported package qualification is made here.

## Independent review corrections (2026-10-04)

Owning architecture/core/subagent references, three READMEs and Agent Note received the intended final synchronous policy, durable-ingress validation and shared-disposal contract before these changes. English/Chinese edits preserve the existing parallel prose. Architecture remains at the 5% headroom target (2280/2400 words). Source JSDoc declares scope-filtered dispatch for both serial hooks, and the factory support property has its explicit public type.

`agents.guardExecution(agent, guard)` attaches a generic synchronous exact-generation assertion through the calling Cordis scope effect; the callback returns undefined or throws. `kind` is model or activation. The loop asserts after the complete awaited model-admission listener chain, before committing input, and again immediately before provider stream dispatch. `AgentHandle.releaseExecution` asserts activation after all reserved lock/flush awaits and before wake/release. The host has no GAT imports and accepts no binder callback through the reserved handle. Registration cleanup removes exactly that scoped callback; required-policy owners close execution before relinquishing guards.

Malformed initial-admission data (null, absent, scalar or array) fails with CONTINUABLE_STATE_CONFLICT. Corrupted execution-reserved markers reject at generic cold resume, explicit owner recovery and legacy send ingress before effects. Reserved dispose closes execution synchronously and shares one physical cleanup promise: concurrent and later calls retain the first rejection. The cleanup deadline bounds only each caller's wait and keeps late cleanup observed.

- `host-review-qualification.log`: eight suites, 247/247 pass. Includes late async listener revocation with zero committed users/provider calls; synchronous request-header observer revocation with zero provider calls; scope-policy cleanup; activation revocation during blocked flush with zero running publication/wake; permitted same-handle activation retry; repeated/concurrent dispose rejection identity and one physical cleanup; malformed durable input.
- `host-review-coldresume.log`: following adjacent legacy ingress validation, reserved + continuation suites 157/157 pass. Persisted malformed execution markers exercise generic resume, owner recovery and ordinary sendMessage, with zero provider requests/live generations.
- `host-review-types-final.log`: focused TypeScript build clean. `host-review-lint-final.log`: owning source/tests oxlint clean. `host-review-diff-check.log`: diff check clean. `host-review-doc-budgets-final.log`: all budgeted documentation within ceilings.
- `host-review-pairs-final.log`: five package/subagent/note pairs written and consistent. Root will re-record/check the retained architecture/core translations after its generated core catalog refresh. The owning agent-loop README pair references TypeScript request-refresh and Python sdk-request-refresh assembled-history scenarios per the SDK intended design. All three README pairs keep Dev Note last with aligned section links. SDK replay results remain with its verification owner.

Actual signed HTTP Team races and generated catalog qualification remain with authority/root; these host tests assert the actual host lifecycle and dispatch effects directly.
