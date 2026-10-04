# Prerequisite source inventory findings

Observed 2026-10-04 from the approved GAT checkout and isolated host prerequisite worktree. This is a provisional source map: files may still change, and path/symbol presence does not establish qualification PASS, deployment readiness, or canonical promotion. Hashes are in `prerequisite-source-inventory.json` and must be regenerated for final qualification.

## Design and scope alignment

Read `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§7, 10–13 and `docs/gat-design/DETAIL_DESIGN.md` §7. The ownership split there maps cleanly to the inspected implementation areas:

- DD-02 / DD-03 / DD-16: reserved lifecycle is owned by host `packages/subagent/subagent`; GAT orchestration remains in roster/member-binding/mailbox and commits readiness around the host handle.
- DD-09 / DD-15 / DD-16: request refresh/admission belongs to host `packages/core/agent-loop`; GAT binder and tool integrations remain adapters.
- DD-04 / DD-06 / DD-17: trusted receipts originate in host Connection HTTP control admission; GAT owns canonical mission/task leases and durable event projection.
- DD-09 / DD-17: immutable nested capability capture and rechecks belong to host `packages/core/tools`; GAT supplies policy and compatibility fallback.

No design conflict was found in these inspected owner boundaries. This work is inventory only and changes no source, design, or official source map.

## Current anchors and affected tests

Reserved admission and recovery: host `packages/subagent/subagent/src/index.ts` exposes `materializeContinuable`, `recoverContinuable`, and the compatibility `startContinuable`; `continuation.ts` implements those paths; `reserved.ts` defines the opaque handle, state machine, and persist-only prompt transition. Focused tests are `reserved.spec.ts` and `continuation.spec.ts`. GAT call sites are `roster.ts`, `member-binding.ts`, `index.ts`, and `mailbox.ts`, with member-binding, enable, replay, attachment, and team regression suites.

Prompt/model boundary: host `core/agent-loop/src/agent.ts` has `agent/prepare-prompt` before pre-step/each request attempt and `agent/model-admission` immediately before provider work; `runtime-context.ts` owns projected prompt state and `core/system-prompt/src/index.ts` renders it. Focused tests include `prepare-prompt.spec.ts`, `system-prompt-admission.spec.ts`, request reconstruction, and loop tests. GAT adapter paths are the durable-agent binder/tools and Team tools policy.

Authenticated control/authority: host `client/connection/src/rpc-host.ts` contains `authenticatedControl`, `withControlInvocation`, and `consumeHumanControl`; `control-admission.ts` holds the opaque invocation-scoped receipt machinery. GAT `authority.ts` binds/asserts exact agent and task leases; `mission-board.ts` consumes authenticated approvals; `journal.ts` blocks use until authority append flush succeeds; task and projection modules enforce canonical task and versioned event rules. Tests include the real signed-cookie HTTP fixture, authority, projection, and team tests.

Nested capability checks: host `core/tools/src/index.ts` defines capability keys and `ToolRuntime`, snapshots metadata at registration, resolves descendants, and checks captured metadata at nested dispatch. `schema.ts` carries declarations. Tests are `capabilities.spec.ts`, `ptc.spec.ts`, and core tool pipeline tests. GAT enforcement is in `packages/tools/src/index.ts`, composed with durable-agent tools; prerequisite composition/team tests cover integration.

## Existing source-map drift

`docs/gat-design/source-code-map.json` row DD-17 is currently empty for both source and tests, despite §7 now specifying concrete host/GAT owner paths and fixtures. DD-16 still describes the pre-prerequisite qualification gap and lists the generic attachment/binding foundation; that remains useful context but does not map the new host lifecycle, exact authority, or nested capability implementation. Existing DD-02/03/04/06/09/15/16 line numbers are historical anchors: this checkout contains modified and newly added files, so consumers must resolve declarations at current locations. In particular, refresh DD-02 roster anchors, DD-09 tools guard anchors, and DD-15 host lifecycle paths (the current owner is `packages/subagent/subagent/src`, not only the external durable-agent adapter). Do not update the official source map from this inventory alone; qualification evidence and source hashes must be reconciled first.

## Verification boundary

No tests were run for this inventory. The source and test SHA-256 values in the JSON are the exact observed bytes at capture time, not a claim those suites pass. If implementation changes after this snapshot, regenerate affected hashes and line anchors before using this mapping as qualification evidence.
