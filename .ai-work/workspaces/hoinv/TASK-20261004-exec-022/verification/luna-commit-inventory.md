# AIP-EXEC-022 commit inventory (read-only)

Inspected both Git worktrees on 2026-10-04. No staging, edits, commits or resets were performed for this inventory. Root currently reports 564 changed/untracked paths; the prerequisite worktree reports 304, so do not stage either tree wholesale.

## Root worktree: candidate task-owned paths

Candidate implementation and official design paths:

- `docs/gat-design/{ARCHITECTURE_DESIGN.md,BASIC_DESIGN.md,DETAIL_DESIGN.md,DURABLE_AGENT_INTEGRATION.md,SOURCE_CODE_MAP.md,design-verification.json,source-baseline.json,source-code-map.json}`
- `packages/core/**`, `packages/durable-agent/**`, `packages/durable-profile/**`, `packages/tools/**`
- `installer/index.mjs`, `installer/tests/binding-compatibility.test.mjs`, `installer/verify-binding*.mjs`, `scripts/generate-binding-compatibility.mjs`
- `README.md`, `packages/core/README*`, `packages/durable-agent/README*`, `packages/tools/README*`
- `verification/web/gat-agent-team-panel.e2e.ts` and `verification/web/task.expected.md`

Candidate controlled task evidence and governance paths:

- `.ai-work/aip/hoinv/exec/AIP-EXEC-022-implement-durable-agent-binding.md`, the two capture backlog files, and the changed control/output files under `.ai-work/workspaces/hoinv/TASK-20261004-exec-022/`.
- The verification directory has 227 changed/untracked evidence paths in the current status (228 including this inventory). Select the final, hash-bound receipts and necessary raw reports cited by the refreshed README/handoff; do not include every interim, failed, superseded, or duplicate run merely because it is present. The current close-final evidence set includes `binding-distribution-closed-final.json`, `binding-closed-final-artifact-proof.json`, `binding-built-packed-exports-closed-final.json`, `production-built-runtime-closed-final.json`, `production-browser-closed-final.log`, closed-final SDK corpus logs, final test/build/lint logs, and the final design/source-map verification. Retain failed runs as history only where the handoff refers to them.
- Root `compatibility/dsh-0.1.5-rc.2-binding-5c02ce9/` is the selected distribution artifact (233 changed/untracked paths). Its manifest SHA-256 is `2a0c9a5474d6a98ecb767522dce29dc3c259d48697bc61b2b0ec796a5cb07e30`, matching `binding-distribution-closed-final.json`; receipt binds prerequisite host `5c02ce9f3e44dfce3f87498f65cf684194ad4572`, provider `a8e215433ae050e36e0ba27205701be1a5f114a1`, 244 prerequisite files, 54 host files and 151 payload files. The complete selected named artifact is expected task content, including its manifest, before/after patchset and provider payload.

The final selected accepted distribution target is `/home/hoinv/work/dsh-binding-distribution-closed-final`. Current receipts show installer/hash checks PASS, built-runtime PASS, and browser replay 3/3 PASS (`production-browser-closed-final.log`). The final scoped task lint says zero findings. The old model mismatch and authenticated-Gateway failure logs are historical evidence, not the selected final result.

## Prerequisite worktree: candidate and exclusions

`/home/hoinv/work/dsh-binding-prerequisites` has 304 changed/untracked entries. The 198 files under `website/.vitepress/.temp/` (about 16.4 MB) are generated search/build output and must be excluded. Also exclude `.gat/installation.json` and the generated `native/system/packages/linux-x64/bin/` binary (17,360 bytes).

The remaining likely task-owned host-side paths cover: `apps/web/tests/**`; `docs/config-catalog*`, `docs/event-producer-consumer*`, `docs/subsystems/agent-team*`; `packages/api/gateway/**`, `packages/client/connection/src/rpc-host.ts`; `packages/experimental/gat-core/**`, `packages/experimental/gat-tools/**`, `packages/experimental/gat-durable-agent/**`, `packages/experimental/gat-durable-profile/**`; `packages/extensions/tool-cordis/src/api-catalog.ts`; `vendor/gat-durable-provider/**`; and `pnpm-lock.yaml`, `scripts/gen-cordis-catalog.ts`, `tsconfig.base.json`, `tsconfig.host.json`, `tsdown.config.ts`. Review the current host diff against the receipt before staging; the accepted distribution is an isolated generated artifact and does not itself prove every current host working-tree byte belongs in a commit. Keep the host changes in the prerequisite repository's commit, separate from the GAT root commit.

## Large files and exclusions

Large current root evidence includes `binding-closed-final-build-cache.json` (1,136,005 bytes), three near-1 MB whole-tree lint JSON reports (`production-whole-tree-lint*.json`), `binding-generated-pnpm-lock.yaml` (894,253 bytes), and the selected compatibility patchset lock snapshots (`patchset/before/pnpm-lock.yaml` 878,298 bytes; `patchset/after/pnpm-lock.yaml` 894,253 bytes). The patchset lock snapshots are part of the selected compatibility artifact. Build-cache and duplicate whole-tree lint dumps are bulky generated/interim evidence; include only if the refreshed handoff directly requires them. The root checked-out `pnpm-lock.yaml` change belongs to the source package integration.

Explicitly preserve outside commits in the root tree:

- `SOURCE_SNAPSHOT.json` (SHA-256 `e39e39c7846c6557a2fd7a28cdfb5e119e0f8d7072fe6abb8a144dc352c29deb`)
- `compatibility/dsh-0.1.5-rc.2/manifest.json` (SHA-256 `e0973ad5c8937caa3268d735014c29f00e9e457c29448fcdcdffa5b930794713`)
- `installer/verify.mjs` (SHA-256 `10b630428ec104fc13086802665d322f583478f451a35e20665f1497a7c72400`)
- all `__pycache__` / `.pyc` files and `08_capture_inbox.jsonl.bak`.

Explicitly preserve outside commits in the prerequisite worktree: `.gat/`, `native/system/packages/linux-x64/bin`, and the complete `website/.vitepress/.temp/` tree. These are local installation/build side effects.
