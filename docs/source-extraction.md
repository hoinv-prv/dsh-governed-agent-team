# GAT source extraction record

## Status

The accepted Governed Agent Team implementation was extracted from the DSH golden-reference worktree, migrated to the private `@vuhoi/gat-*` namespace, and packaged as a checksum-pinned local installer payload. The compatibility authority is `compatibility/dsh-0.1.5-rc.2/manifest.json`.

## Provenance

- Source root: `/home/hoinv/deepseek-harness/.worktrees/governed-agent-team-v1`
- Source branch: `feature/governed-agent-team-v1`
- Source commit: `12fef7a7e01f6c3ba7ecab0929355659b3370435`
- DSH compatibility target: `0.1.5-rc.2` at `c291e7961a515f6d7af9304e7fd1d257929aef26`
- GAT version: `0.1.0`

| Golden-reference package | Standalone source | Installed DSH destination |
|---|---|---|
| `packages/experimental/agent-team` | `packages/core` | `packages/experimental/gat-core` |
| `packages/experimental/tool-agent-team` | `packages/tools` | `packages/experimental/gat-tools` |
| `packages/experimental/client-ui-agent-team` | `packages/web` | `packages/experimental/gat-web` |
| `packages/experimental/agent-team-profile` | `packages/profile` | `packages/experimental/gat-profile` |
| `packages/experimental/agent-team-web-profile` | `packages/web-profile` | `packages/experimental/gat-web-profile` |

The package source contains 68 files. Three keyless assembled-Web verification files bring the install payload to 71 files. The manifest records every source path, destination path, byte count, mode, and SHA-256 value.

## Deliberate transformations

Package manifests, package imports, local links, tests, and documentation use the `@vuhoi/gat-*` identities. Runtime Cordis row ids such as `agent-team` and `tool-agent-team`, locale namespaces, tool names, and durable Session event names remain unchanged because they are behavioral identifiers rather than npm identities.

The installer adds nine host compatibility files. Two are the accepted golden-reference Session event and Cordis API catalog changes. Three select GAT in the Host and Client TypeScript aggregate programs and add explicit aliases for the non-DSH namespace. One switches the generated tool-catalog input from the original package names to GAT. One excludes the original packages from tsdown while GAT occupies the same runtime service keys. Original DSH experimental package source is not modified or removed.

## Regeneration

From this repository:

```sh
node scripts/generate-compatibility.mjs /home/hoinv/deepseek-harness
```

The command reads the pinned commits, regenerates before/after host files, inventories the current payload, and rewrites the compatibility manifest. Any payload edit requires regeneration before installation; otherwise source validation fails closed.

`SOURCE_SNAPSHOT.json` is the concise provenance record. The compatibility manifest is the per-file installation authority.

## Installation and rollback

See the repository `README.md` for canonical dry-run, installation, verification, activation, and rollback commands. Rollback covers only installer-owned files and refuses to overwrite post-install edits. It does not delete AIWS records or the original experimental DSH packages.

DSH without the host event-type patch cannot be assumed to replay Sessions containing required GAT events. Roll back only when those Sessions are no longer needed by that checkout.
