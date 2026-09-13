# GAT source extraction record

## Status

**PARTIAL — source snapshot only. GAT is not installed.**

The standalone repository currently has no installer, no verified compatibility manifest, and no host patchset. Therefore this extraction must not be described as installed, independently buildable, compatible, safe, or release-ready.

## Scope

Tracked files were copied byte-for-byte from the accepted DeepSeek Harness golden-reference worktree:

- Source root: `/home/hoinv/deepseek-harness/.worktrees/governed-agent-team-v1`
- Branch: `feature/governed-agent-team-v1`
- HEAD: `12fef7a7e01f6c3ba7ecab0929355659b3370435`
- First compatibility target: DSH `0.1.5-rc.2` at `c291e7961a515f6d7af9304e7fd1d257929aef26`

Package mapping:

| Golden-reference package | Standalone snapshot path |
|---|---|
| `packages/experimental/agent-team` | `packages/core` |
| `packages/experimental/agent-team-profile` | `packages/profile` |
| `packages/experimental/agent-team-web-profile` | `packages/web-profile` |
| `packages/experimental/client-ui-agent-team` | `packages/web` |
| `packages/experimental/tool-agent-team` | `packages/tools` |


Copied package counts: `packages/core`: 29, `packages/tools`: 7, `packages/web`: 15, `packages/profile`: 9, `packages/web-profile`: 8. One accepted design document was also copied. Total copied files: **69**.

The canonical per-file SHA-256 and executable-mode inventory is `SOURCE_SNAPSHOT.json`.

## Locator interpretation

- `source.repository_root` is the immutable local golden-reference worktree used for this snapshot.
- Every `entries[].source` path is Git-tracked at the recorded golden-reference HEAD.
- Every `entries[].destination` path is relative to this standalone repository.
- `package_aggregates` hashes sorted records in the form `relative_path\0mode\0bytes\0sha256\n`.

## Representation status

- Five GAT package trees: **complete byte-for-byte tracked-file snapshots**.
- Standalone package identity/import migration: **not started**.
- Standalone workspace/build wiring: **not started**.
- DSH host compatibility patchset: **not extracted**.
- Transactional installer: **missing**.
- Installation/compatibility verification: **not run**.
- Overall migration status: **partial**.

## Deferred work requiring a separate approved task

1. Rename package identities and internal dependencies to `@vuhoi/gat-*`.
2. Add standalone workspace/build/test configuration and verify all copied tests.
3. Classify cross-cutting changes relative to DSH base commit and create the exact versioned patchset.
4. Create a fail-closed transactional installer and exact compatibility manifest.
5. Verify dry-run, install, rollback, idempotency, replay, approval guard, composition, and Web smoke in an isolated DSH worktree.

## Rollback / caution

The source-copy rollback boundary is the five mapped package directories, `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`, `docs/source-extraction.md`, and `SOURCE_SNAPSHOT.json`. Do not delete AIWS repository scaffolding or task evidence when rolling back this source snapshot.

Vanilla DSH cannot be assumed to replay sessions containing required non-ignorable GAT events after uninstall. This remains a compatibility-design limitation until the versioned host patchset and installer are implemented and verified.
