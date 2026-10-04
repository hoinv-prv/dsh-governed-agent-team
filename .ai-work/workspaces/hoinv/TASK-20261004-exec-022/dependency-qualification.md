# DSH dependency qualification (source inspection)

Inspection date: 2026-10-04. This records source declarations and control flow only; it makes no claim about which bytes are loaded in any running process.

## Compared source identities

| Tree | Revision | Relation to compatibility manifest |
|---|---|---|
| `/tmp/gat-exec022-verify` | `c291e7961a515f6d7af9304e7fd1d257929aef26` | Exact `target.commit` recorded by the manifest; this report does not select or approve that compatibility revision. |
| `/home/hoinv/deepseek-harness` | `c1157f7ed448b40c463c1a43fa595b12294fd50d` | Separately observed working tree; not the manifest target. |

## Public continuable-child lifecycle

In the manifest-target tree, `packages/subagent/subagent/src/index.ts:219-230` exposes `startContinuable(spec): Promise<ContinuableStart>` and documents that it establishes the child and delivers its initial prompt. `types.ts:31-50` defines the spec (provider, label, optional caller-reserved child id, request, signal); there is no context-policy field. `continuation.ts:102-185` performs the operation as one call: it materializes at `:159-173`, then immediately calls private `submitMaterialized` at `:175-183`. The helper is private (`:456+`).

`index.ts:233-238` documents `sendMessage` as cold-resuming an absent direct child. The implementation routes absent activations to private `coldResume` (`continuation.ts:290-300`); `coldResume` reconstructs/materializes and submits the waiting message (`:400-453`). No public source API was found for reserving/materializing without initial prompt, persisting the initial prompt without activation, separately activating, or requiring recover-before-release on cold resume. The current single-call and cold-resume paths therefore do not satisfy the frozen reserved-state/activation/recovery contract by themselves.

In the separately observed tree, `index.ts:260-271` retains the same public `startContinuable` contract, while `types.ts:31-52` adds `contextPolicy?: 'require-fresh'` at `:43-44`. `continuation.ts:102-194` still materializes and submits the initial prompt in one operation; its `:147-149` check applies to seeded parent history and does not add a reserved admission stage. Absent-child cold resume remains private and submits the message (`continuation.ts:429-478`). This one source-level delta does not establish a reserved lifecycle API or make the two trees equivalent.

## Per-request hook and prompt refresh

Both trees declare the `agent/request` waterfall in `packages/core/agent/src/runtime-types.ts:330-339`; it returns `LlmCallConfig`, and the contract explicitly says it cannot mutate messages. In target `packages/core/agent-loop/src/agent.ts:381-408`, the step renders `decision.assembly` at `:387-388` before `prepareRequest`; the hook is awaited within `prepareRequest` at `:529-533`, before request construction. The observed tree has the same order at `agent-loop/src/agent.ts:381-408` and hook dispatch at `:559-563`.

Thus a host listener can participate in request-route preparation and its rejected promise prevents reaching request construction, but the hook receives no prompt assembly/message replacement capability. The prompt for that step has already been rendered. The inspected hook is not a source-supported mechanism for reloading and replacing live prompt context at each actual model request; that remains an integration prerequisite for the frozen per-request refresh requirement.

## Tool registry and nested capability enforcement

Target `packages/core/tools/src/index.ts:222-236` defines `ToolDefinition` as schema plus execution/output behavior, without declarative capability ownership. Its `ToolExecutionInput` at `:326-351` carries call/name/arguments/agent/parent-token/signal; no capability set or immutable owner classification appears there. `ToolRestriction` at `:696-705` is name-based allow/deny, and `ToolGuard` at `:723-731` can deny but cannot grant. The observed tree has the corresponding `ToolDefinition` at `packages/core/tools/src/index.ts:223-236`, execution input at `:326-351`, and name filter/guard at `:724+` / `:731+`; `packages/llm/llm/src/types.ts:473-484` adds `deferLoading` to `ToolSchema`, not capability metadata. Target `packages/llm/llm/src/types.ts:411-416` has only name, description, and parameters.

The registry therefore offers useful name filtering and a monotonic deny hook, but the inspected declarations do not provide immutable per-tool capability ownership, nested/composite descendant-capability union, or an enforced capability check at every nested dispatch boundary. This does not qualify the frozen nested-capability-union requirement. No conclusion about any uninspected toolkit-specific capability API is made here.

## Frozen host prerequisites still outstanding

The freeze's §7 reserved-child state machine requires materialization, initial-prompt persistence, activation, and recovery gating as separate controlled transitions. §10 requires a host-attested lease bound to the exact team, mission id and revision, and canonical task identity, with revocation/generation checks on effects; the inspected DSH continuable APIs above expose no such GAT admission lease. §11 requires capability union across nested dispatch. The present source findings qualify only the APIs shown above: they do not claim runtime availability, do not satisfy those frozen prerequisites, and do not authorize choosing a DSH revision, bypassing compatibility, or activating/installing anything.

Design prerequisites consulted: `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§7, 10–11 and `docs/gat-design/DETAIL_DESIGN.md` §5 (DD-01/DD-09/DD-15/DD-16/DD-17).

## Qualified prerequisite follow-up

The source-only baseline inspection above is retained as history. AIP-EXEC-023 implements and qualifies the four missing prerequisite families in an isolated, approved changed-host patch. Exact source/artifact and independent review receipts are ../TASK-20261004-exec-023/qualification-receipt.json and prerequisite-handoff.md. This does not select a supported release, approve deployment or qualify the parent production binder/profile. The unchanged compatibility commit must be paired with the qualified patch SHA-256; it cannot stand in for changed bytes.
