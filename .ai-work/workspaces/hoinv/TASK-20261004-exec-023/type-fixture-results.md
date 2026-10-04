# AIP-EXEC-023 affected-consumer type fixtures

Worktree: `/home/hoinv/work/dsh-binding-prerequisites`.

Read the project instructions and current ASC, then completed the AIP-resolved wiki lookup. Reviewed `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§10–11 and `docs/gat-design/DETAIL_DESIGN.md` §7, plus the workspace host/capability prerequisite notes. In the DSH worktree, reviewed `AGENTS.md`, `packages/AGENTS.md`, `docs/AGENTS.md`, and `docs/architecture.md` before touching tests. These are fixture-only changes; no design or implementation change was needed.

Changes are limited to the three assigned test files:

- `packages/core/scope/tests/invariant.spec.ts`: added typed rows for `agent/prepare-prompt` and `agent/model-admission` to the exhaustive event map, using their actual serial-event payload shape.
- `packages/fs/tool-fs-search/tests/tools.spec.ts`: conditionally forwards `exec.agent` in the nested call, preserving the live execution token and signal while omitting an absent optional `agent` field.
- `packages/spill/spill-policy/tests/spill-policy.spec.ts`: conditionally forwards `outer.agent`, preserving the actual parent token and signal while omitting an absent optional `agent` field.

Verification:

- Focused Vitest run: 140 passed, 1 failed across 3 files. Both consumer suites passed (140 tests). The scope invariant suite fails because the generated `scoped-events.generated.ts` resolver currently has no resolver for `agent/prepare-prompt`; it therefore does not reject a mismatched carrier in the newly added event row. This is outside this fixture-only ownership. Kept the check intact and did not weaken or spoof it. Full output: `verification/type-fixture-focused.log`.
- `node node_modules/typescript/bin/tsc -b packages/core/scope packages/fs/tool-fs-search packages/spill/spill-policy --pretty false`: passed. Output: `verification/type-fixture-typecheck.log`.

No source implementation, package manifest, lockfile, or design file was edited.
