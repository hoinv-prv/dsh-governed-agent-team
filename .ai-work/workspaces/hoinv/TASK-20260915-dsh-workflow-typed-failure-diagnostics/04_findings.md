# Findings

## STEP-00 confirmation

- HUMAN explicitly authorized a separate task to repair and verify the DSH council/workflow structured-output transport after run-035 returned three unexplained `null` lane results.
- Scope is limited to additive typed failure diagnostics, focused tests/docs and affected-package verification in `/home/hoinv/deepseek-harness`; no WBS or mission-control mutation and no council rerun before verification.

## Findings List

### F-010-01 — Ordinary child diagnostics were discarded before workflow completion

- `SubagentResult.diagnostic` already provides bounded provider-authored safe detail, but `workflow-worker-thread/src/host.ts` projected only output/structured/stopReason into `ChildResult`.
- `runtime.ts` deliberately mapped both a missing schema capture and any non-completed child to bare `null`, retaining only an observer outcome of `failed`; `WorkflowResult` and the model-facing tool result carried no per-child cause.
- This exactly explains run-035: the script correctly returned three null lane values, while the caller could not distinguish missing structured output from provider/model failure and therefore could not establish typed retry eligibility.

### Implemented additive contract

- Added `WorkflowAgentFailureInfo` with engine-owned codes `missing-structured-output` and `child-not-completed`, child identity, exact stop reason and optional bounded safe provider diagnostic.
- Worker runtime accumulates these failures in settlement order and returns them as optional `WorkflowResult.agentFailures`; successful structured results remain unchanged.
- Model-facing workflow tool always returns `agentFailures` (empty on a clean run) and renders diagnostics before the capped script value so a large result cannot hide failure causes.
- Updated runtime/host/tool tests and package README/JSDoc contracts.

## STEP-03 verification

- PASS: host TypeScript project check — `node --max-old-space-size=4096 ./node_modules/typescript/bin/tsc -b tsconfig.host.json`.
- PASS: targeted oxlint — 0 warnings, 0 errors across 8 modified TypeScript files.
- PASS: worker session suite — 27/27.
- PASS: full worker-thread suite — 55/55, including the real host/worker provider-diagnostic bridge.
- PASS: model-facing tool-workflow suite — 25/25 after the host rebuild.
- PASS: root `build:lib:host` after the minimal Typert-required `agent` parameter rename in `packages/experimental/wbs/src/index.ts:63`.
- PASS: Markdown wrap verifier — 1637 files, no hard-wrapped prose.
- UNRELATED docs baseline: link verifier reports broken links only in pre-existing `packages/experimental/gat-*` README files, not modified workflow docs.
- Verification total for affected workflow suites: 107/107 tests pass.
- Remaining blocker: the running `pnpm dsh web` process loaded the old plain packages before this build and no `pnpm run dev:web` watcher exists. Restarting it inside this live GUI session would terminate/disrupt the session. Another council call in this process would still use the old null-only transport and is prohibited.

## Confirmed Findings
- ...

## Inferred Findings
- ...

## To-Verify Findings
- ...

## Notes
- ...
