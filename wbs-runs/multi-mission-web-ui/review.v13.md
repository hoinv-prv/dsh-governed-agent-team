# Review candidate multi-mission-web-ui, revision 13

## Plan identity

- Plan: `wbs-runs/multi-mission-web-ui/wbs.v13.json`
- Exact-byte SHA-256: `96aabf505c4334f0554204adf40bdd8093a0743de00839cde5a22bbea0a8539f`
- Proposal: `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- Proposal SHA-256: `dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee`

## Objective and boundary

Build and verify the Conservative MVP as standalone `@deepseek-ai/dsh-gat` package artifacts before any DSH installation. No command or declared effect reaches a DSH checkout, compatibility generator, installer, full DSH build, live Web GUI/profile, or network.

Deferred without acceptance claim: actual DSH ports, native tool registration, compatibility generation, install/rollback, full build, dashboard smoke, live activation, broad UI, semantic retrieval, caching, `mission-shared`, cross-scope promotion, distributed 2PC, and MissionMembership.

## Requirement and gate coverage

| Gate / requirement | Task and observable evidence |
|---|---|
| Stale execution settlement | `governance-replan`: proves no writer remains, preserves 17 charges and attempt-core-007, selects exact revision/hash, re-plans AIP-EXEC-004 without changing its fixed Workspace |
| Threat model before code | `threat-model-gate`: independent Security review and HUMAN acceptance of exact threat/vector hashes; every coding task hard-depends on it |
| Execution/readiness/approval contracts | `governance-contracts`: focused tests and independent review |
| Record/provenance/partition/audit/lifecycle/privacy | `partitioned-memory`: three focused suites plus independent storage review |
| PDP/selector/account containment/non-disclosure | `policy-selector`: focused tests, zero-backend spies, independent authorization review |
| Wrapper-only raw MCP admission | `wrapper-admission`: schema hiding + forced-call denial + zero PDP/MCP/backend evidence |
| Buildable/exported package | `package-surface`: manifest/exports/workspace, typecheck, tsdown build, built-package Node smoke, independent package review |
| Every proposal vector/raw evidence field | `security-conformance`: exact proposal-pinned vector path and `pnpm --filter @deepseek-ai/dsh-gat test:conformance` interface; no missing/skipped/family-only vectors |
| Standalone integration | `standalone-integration`: source suite, typecheck, build, built smoke, conformance on identical hashes; no external effect |
| AIWS/final HUMAN gate | `standalone-report-review`: Workspace evidence, capture/open-point check, scoped lint, independent review, HUMAN standalone acceptance, then AIP close |

## Commands, scopes, and package independence

- Toolchain reads are declared: `package.json`, `pnpm-lock.yaml`, future `pnpm-workspace.yaml`, `node_modules`, and `packages/gat`; observed executable versions are preserved in `toolchain.v13.md`.
- New package writes include entrypoints, manifests, build config, source, tests, `lib`, conformance runner, and evidence.
- Exact commands are limited to AIWS lint/status/close, focused Vitest, TypeScript no-emit, tsdown build, Node built-package smoke, package-owned standalone tests, and the proposal-pinned conformance interface.
- No `external` or `network` effect is declared.
- Each task writes bounded runtime evidence under the existing fixed Task Workspace.

## Cumulative limits and history

- Existing charged attempts: 17.
- Revision-13 allocation: 19 attempts.
- Cumulative ceiling: 36 attempts.
- Cumulative effort ceiling: 4,535 minutes, preserving the prior 1,280-minute ceiling plus revision-13 estimates.
- Maximum parallelism: 2; only non-conflicting governance and memory slices may overlap after the accepted threat gate.

All revision 1–12 plans, decisions, attempts, acceptances, failures, and review evidence remain immutable provenance. Revision-12 approval is recorded, but its post-approval independent `REVISE` prevents dispatch; it grants no authority to revision 13.

## Delta closing revision-12 review

1. Threat model and complete vector baseline moved before implementation and require independent + HUMAN acceptance.
2. `governance-replan` is a hard first task that settles stale active work and preserves cumulative charges.
3. Attempts/effort are cumulative rather than reset.
4. Conformance uses the proposal-pinned package/path/interface and requires every unique §18.1 GAT-* vector plus all raw evidence bindings.
5. Missing record, provenance, classification, redaction, retention/expiry, account containment, timing, audit.read/sink failures, backup/restore, and restart obligations are explicit requirements and acceptance checks.
6. Every task has Task Workspace evidence scope; final scoped lint/capture/open-point/AIP-close obligations are explicit.
7. A real package manifest/export/typecheck/build/built-import smoke is required; package-manager metadata and executable-installation reads are declared.

## Validation

Canonical helper results:
- validate: PASS;
- order: `governance-replan`, `threat-model-gate`, `governance-contracts`, `partitioned-memory`, `policy-selector`, `wrapper-admission`, `package-surface`, `security-conformance`, `standalone-integration`, `standalone-report-review`;
- hash: `96aabf505c4334f0554204adf40bdd8093a0743de00839cde5a22bbea0a8539f`.

## Decision requested

Approve only these exact revision-13 bytes and bounded standalone effects, request changes, or keep plan-only. Approval authorizes execution through the pre-implementation threat-model gate; it does not pre-accept that threat model and does not authorize any DSH installation or activation.
