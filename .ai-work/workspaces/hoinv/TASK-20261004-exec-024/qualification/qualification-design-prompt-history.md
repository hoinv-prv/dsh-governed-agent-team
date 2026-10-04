# Qualification design — STEP-01

Date: 2026-10-04. Design-before-code: official `docs/gat-design/DETAIL_DESIGN.md` §9 was written before experimental test files. §§5/7/8 remain the accepted direct-continuable implementation; §7 promises per-request refresh in a different prerequisite Host, not automatically in the selected current Host.

Consulted GAT DD-09/DD-15/DD-16, §7 model admission, Integration and the freeze; external WK Architecture AD-02–05, Basic BD-02–05, Detail DD-02–04/DD-06–09 and conflict boundaries. WK ref grants provider operations only; current GAT execution is task authority. WK snapshots are per-call, not pinned to the initial model assembly. Provider storage and API remain unchanged.

## Exact experimental path

Create isolated DSH worktree `/tmp/gat-exec024-host-c1157f7e` at `c1157f7ed448b40c463c1a43fa595b12294fd50d`. Reuse existing installed dependency links without installation/builds; copy exact prebuilt WK public package to `vendor/gat-qualification-wk/` and resolve its Cordis peer to the same Host source owner in test configuration. Hash selected source/package/lib files, and record dependency-link targets. Retain runnable experimental source copies under this workspace `qualification/`.

Use the supported Vitest launcher, existing Host decorators, source aliases and fork arguments. Test-only Loader YAML resolves GAT and public WK plugin module namespaces; real AgentLoop/session persistence/subagent services supply assignment/admission. Scoped experimental binding observes `executionFor`, provisions explicit fresh workspace declaration in awaited agent creation, then joins downstream prompt admission before public Consumer contribution. Nonexecution bootstrap Sessions remain unbound.

First experiment isolates OP-024-03: mock model bootstrap, then failed execution request, then successful retry. In public request-error middleware commit a new confirmed memory item through WK with a test-only authorized-host-workflow audit ref. Assert the real Consumer sees the new revision/catalog, count actual assemblies versus requests, and compare logged prompt with actual model requests. Characterization assertions prove the selected Host behavior; a separate contract assertion must detect stale retry rather than normalize its expectation.

Public `agent/request` middleware is route-only; calling an extra assembly there cannot replace the rendered prompt already captured by the current loop. Transport rewriting would make model input diverge from logged projection and is excluded. No fake Team service, private provider storage edit, second execution runner, core patch or live credential/model is used.

## Matrix and gates

Prioritize retry freshness because a reproduced missing public operation prevents the requested adapter from meeting its contract at all. Continue independent public export/first-request/logging checks while gathering the negative witness. Do not claim completed reviewer/selection/cleanup/recovery qualification from that witness; retain those rows as unqualified. If retry is feasible, expand the real matrix before production design/review. If infeasible, produce the smallest Host prerequisite proposal with exact evidence and await HUMAN scope decision; STEP-04 remains gated.

Reviewer input method remains explicit host-supplied validated public ReviewPacket built from actual evidence bytes, approved contract and candidate. No implementation default, fabricated receipt or generic reviewer role is chosen here. Missing authenticated packet input is an additional downstream dependency, not hidden acceptance.

## Effects

Writes: official prospective design amendment; AIP runtime files/captures; new isolated git worktree plus git worktree registration; new test-only files/config and copied WK artifacts inside that tree; Vitest caches in that tree; unique temporary Session/provider directories cleaned by fixture teardown. Existing dependency targets are read only. No dependency installation, native rebuild, production code, deployed profile, accepted mission artifact or external message mutation.
