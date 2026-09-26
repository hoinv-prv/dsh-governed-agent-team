# Review candidate multi-mission-web-ui, revision 12

## Plan identity

- Plan: `wbs-runs/multi-mission-web-ui/wbs.v12.json`
- Exact-byte SHA-256: `5be249f76b2b73266c8b0bb17d648a86b93cc7af65aeaffeb797cde45d8b365d`
- Design source: `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- Design SHA-256: `dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee`

## Objective, scope, and non-goals

Revision 12 implements and independently tests the proposal's Conservative MVP in this repository before any DSH installation. It keeps the existing mission ID/root solely to preserve revision and attempt history.

Write scope is limited to:
- `packages/core/src/gat` and two focused core test files;
- new standalone `packages/memory`;
- `packages/tools/src/gat` and its focused test;
- `docs/security` and `verification` conformance artifacts;
- the existing AIP/workspace during the first gated execution task;
- standalone integration/final evidence under the mission root.

Explicitly excluded: DSH checkout/worktree changes, compatibility generation, installer/verify commands, full DSH build, Web shell/profile changes, server restart, activation, broad UI, semantic retrieval, cache, `mission-shared`, cross-scope promotion, distributed 2PC, and MissionMembership.

## Requirement coverage

| Requirement | Main deliverable | Verification |
|---|---|---|
| `aiws-control` | `governance-replan` | AIP lint/status plus coordinator inspection of fixed Workspace and re-plan provenance |
| `execution-governance` | `governance-contracts` | focused Vitest + independent governance review |
| `authorization-isolation` | `policy-selector`, `wrapper-admission` | focused PDP/adapter tests with zero-backend-call spies + independent review |
| `memory-protocol` | `partitioned-memory` | partition, transaction/audit, lifecycle Vitest files + storage review |
| `lifecycle-audit` | `partitioned-memory`, `security-conformance` | crash-boundary/restart/hold/purge tests and threat-model review |
| `wrapper-admission` | `wrapper-admission` | schema absence, forced raw-call denial, and zero backend access |
| `conformance-evidence` | `security-conformance`, `standalone-integration` | versioned vector runner, combined run, independent reviews, hashes |
| `standalone-boundary` | all implementation tasks and reports | no `@deepseek-ai/*` production imports; no external/install commands or effects |

Integration task: `standalone-integration`. Final conclusion: `final-review`.

## Commands and effects

Only Python AIWS lint/status and exact `pnpm exec vitest run <explicit files>` commands are admitted. The plan declares no `network` or `external` effect and contains no Git, compatibility, installer, DSH build, browser, or server command.

The canonical helper produced:
- validate: PASS;
- order: `governance-replan`, `governance-contracts`, `policy-selector`, `partitioned-memory`, `wrapper-admission`, `security-conformance`, `standalone-integration`, `final-review`;
- exact hash: `5be249f76b2b73266c8b0bb17d648a86b93cc7af65aeaffeb797cde45d8b365d`.

A separate planning-review subagent was attempted but the runtime returned `subagent run failed` without a verdict. Therefore no independent planning verdict is claimed; this document is the coordinator review presented for HUMAN decision. Independent reviews remain mandatory inside the approved execution plan.

## Gates and limits

- Exact revision/hash approval is required before any execution.
- Existing revision-11 active work is not erased or silently continued; the run coordinator must reconcile it after approval.
- Product coding is blocked on the `governance-replan` acceptance.
- Each product/conformance slice requires focused tests and independent review.
- Final acceptance belongs to the HUMAN and covers only standalone readiness.
- Limits: maximum parallelism 2, 15 total attempts, 2,430 effort minutes.

## Delta from approved revision 11

1. **Objective replaced:** from finishing multi-mission Web/install verification to implementing proposal Revision 3 standalone.
2. **Old readiness invalidated:** revision-11 core/Web static acceptance and installed-worktree results remain historical but cannot satisfy new requirements.
3. **External effects removed:** all DSH worktree reset/clean, compatibility generation, install, canonical verifier, full build, and live Web concerns move to a later revision.
4. **New slices:** governance contracts, policy/selector, partitioned memory/audit/lifecycle, wrapper-only MCP admission, threat model, executable conformance, standalone integration.
5. **No architecture inflation:** cache, `mission-shared`, semantic retrieval, promotion, distributed 2PC, and broad UI remain deferred.
6. **History preserved:** revision 1–11 plans, approvals, 17 charged attempts, and evidence are not reset; the active revision-11 item requires run-side reconciliation after approval.

## Decision requested

Choose plan-only/request changes, or approve exact revision 12 and authorize bounded execution in this repository. Approval does **not** authorize DSH installation, DSH checkout modification, proposal activation, or live Web changes.
