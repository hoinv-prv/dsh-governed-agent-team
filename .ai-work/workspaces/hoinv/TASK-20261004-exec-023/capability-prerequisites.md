# Capability prerequisite implementation

Scope: HUMAN-approved AIP-EXEC-023, isolated DSH worktree `/home/hoinv/work/dsh-binding-prerequisites` at baseline c291e7961a515f6d7af9304e7fd1d257929aef26. No original dirty DSH/GAT trees, AIP/ASC pointers, Truth or official Wiki were changed by this owner. Root owns the GAT integration and final build/review ceremony.

## Design consulted and updated before source

Read root AGENTS/local override, AIP/ASC, frozen binding contract §§10–11/13, formal GAT DETAIL_DESIGN §7, workspace design-delta and source-design-test-matrix; DSH AGENTS/package/docs rules, architecture and defensive patterns. Wiki lexical/semantic lookup for external DSH tools documents found no registered host specification; approved STEP-01 raw worktree fallback used owning tools subsystem/README and Agent Note guidelines.

Intended owning DSH docs were written before source: core/tools README pair, docs/subsystems/tools pair, immutable-tool-capabilities Agent Note (proposed before implementation; now implemented). Subsequent unclassified/transport and internal scheduler publication decisions were documented before dependent source. Registry-detachment compatibility requires search Consumer spill owners to capture the registered snapshot; fs-search README pair was updated before glob/grep migration. Delegation Consumer README pairs describe their required classification. Root/host own shared architecture ordering and final formal GAT reconciliation.

## Implemented API and behavior

`ToolDefinition` and `defineTool` accept host `capabilities?: readonly string[]` and `nestedTools?: readonly string[]`. Registry snapshots detached capability/reference arrays and body/name identity; registered-body provenance retains classification and references across changed-name aliases, including source mutation or an alias's omitted/empty fields. Ordinary unclassified registrations contribute `unclassified`. Only the registry-owned PTC transport may declare `nested-dispatch`; ordinary spoofing is rejected. `external-delegation` is captured by shipped subagent/fork/provider-name Consumers, workflow and Ralph independently of configured tool name.

Each `ToolExecution.capabilities` is a frozen own/required-descendant/exact-parent union. Required references resolve in the exact current Agent view; missing tools, cycles and missing classification fail before policy. Identity and arguments are runtime readonly; signal alone remains replaceable for around-dispatch cancellation. AsyncLocalStorage carries enclosing execution identity even when a nested caller omits nesting fields; forged, expired, wrong-root, conflicting and cross-Agent parent tokens deny. Settlement expires registry tokens.

Monotonic guards run before pre-execute, after async admission, before around-dispatch and immediately before the body. Each later check revalidates current registration, required references and live parent identity. Queued scheduler work is checked at actual dispatch. The internal scheduler publishes PTC start only after dispatch admission succeeds; unadmitted descendants produce no nested start/settle events. `run_code` checks actual invoked descendants and remains usable for harmless inspection. Root GAT guard combines capability checks with compatibility names and requires complete-union trusted exemptions; this owner supplies metadata, not GAT authority.

Registry detachment changes lookup identity. Exact-owner search spill processing now captures `ctx.tools.get(name, scopeOf(ctx))` immediately after registration; it preserves exact-registration equality rather than weakening to callback identity. Repository search found no other production tools.get definition equality consumers.

## Verification

`node node_modules/vitest/vitest.mjs run` with the exact 14 focused file arguments recorded below passed **703 tests / 14 files**. Source paths loaded through repository tsconfig source-plane resolver; no implicit pnpm install or full suite. Tests include mutable definitions and changed-name aliases, static descendant union, missing reference/classification/cycle, transport spoofing, dynamic async parent union, direct actual nested denial, wrapper identity stripping and policy change, stale/cross-Agent tokens, scheduler revalidation, actual PTC bindings with admitted inspection and rejected alias/no delegation events. Shipped Consumer fixtures exercise configured subagent/fork/custom names and aliases, workflow/Ralph aliases, zero provider/run/event counters and normal disabled-policy behavior.

Focused files: core/tools tests capabilities, tools, scoped, ptc, execution-mode, invariant, execution-signal-types; fs/tool-fs-search tools; spill/spill-policy spill-policy; workflow/tool-workflow tool-workflow; subagent/tool-subagent tool-subagent; workflow/tool-ralph tool-ralph; shell/shell-env shell-env; context/agent-instructions agent-instructions.

`node node_modules/typescript/bin/tsc -b packages/core/tools/tsconfig.json packages/fs/tool-fs-search/tsconfig.json --pretty false` passed. Focused `scripts/run-oxlint.ts` passed initially on changed source/new capability test (expanded affected-owner run recorded in capability-lint.log). Seven touched bilingual pairs passed named translation-pairing verification. `git diff --check` passed. Logs: verification/capability-focused.log, capability-typecheck.log, capability-lint.log, capability-doc-pairing.log; exact source hashes: capability-source-hashes.json.

The full export-JSDoc script was accidentally invoked by a `--help` attempt (it scans all packages): 188 violations, none in owned tools/fs capability implementation, in imported GAT baseline and in-progress host/control source. Root is informed; this is not reported as a clean full documentation gate. Generated API/Cordis catalogs, built runtime exports, broad documentation checks, immutable read/control GAT authority composition, independent review and AIWS final lint remain root qualification responsibilities.

## Intentional fixture changes

Replaced forged Symbol parent inputs in existing tools, workflow, fs-search and spill tests with actual live composite execution. Early monotonic denial no longer enters pre/around/post hooks; token observations include final result. A newly registered replacement guard is rechecked before dispatch. Unadmitted PTC policy failure returns its binding error without nested dispatch log events. These fixture changes preserve effect/result checks and exercise strengthened admission rather than bypassing it.
