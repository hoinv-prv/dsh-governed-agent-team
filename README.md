# Governed Agent Team

Governed Agent Team (GAT) is a private, opt-in Agent Teams distribution for DeepSeek Harness. Version `0.1.0` supports only DSH `0.1.5-rc.2` at commit `c291e7961a515f6d7af9304e7fd1d257929aef26`.

## Install

Use a pristine, isolated DSH worktree at the supported commit. The installer validates the DSH identity, every payload checksum, every host preimage, and the complete changed-path allowlist before writing.

```sh
GAT=/home/hoinv/work/dsh-governed-agent-team
DSH=/path/to/pristine/dsh-worktree

node "$GAT/installer/index.mjs" dry-run --target "$DSH"
node "$GAT/installer/index.mjs" install --target "$DSH"
node "$GAT/installer/index.mjs" status --target "$DSH"
```

Installation copies checksum-pinned source into these new directories:

- `packages/experimental/gat-core`
- `packages/experimental/gat-tools`
- `packages/experimental/gat-web`
- `packages/experimental/gat-profile`
- `packages/experimental/gat-web-profile`

The original DSH experimental Agent Teams source directories remain unchanged. The installed TypeScript aggregates select GAT instead of compiling both implementations under the same Cordis service keys. The installer does not run package lifecycle scripts, contact a registry, activate a profile, start a server, or call an AI provider.

The installation record is `$DSH/.gat/installation.json`. A repeated install succeeds without writes only when that record and every installed checksum match. Any mismatch fails closed.

## Verify

The canonical verifier is keyless. It runs installer lifecycle checks in a disposable worktree, a frozen offline lockfile-only install check, focused Host and Web tests, a complete DSH build, the built-library smoke, and the assembled Web dashboard smoke. It reuses the main checkout's existing dependency tree through temporary links; the install check does not write `node_modules` or package content to the shared pnpm store.

```sh
node "$GAT/installer/verify.mjs" --target "$DSH"
```

No production service or real provider is used. Chromium must already be available through the DSH Playwright installation.

## Activate explicitly

After verification, add the local profile layers to the intended DSH profile. GAT is never enabled by default.

```sh
cd "$DSH"
pnpm dsh plugin --profile headless add "file:$DSH/packages/experimental/gat-profile"
pnpm dsh plugin --profile web add \
  "file:$DSH/packages/experimental/gat-profile" \
  "file:$DSH/packages/experimental/gat-web-profile"
```

These commands modify the selected user profile. They are not part of installation or keyless verification.

## Roll back

Rollback refuses to overwrite an installed file that changed after installation.

```sh
node "$GAT/installer/index.mjs" rollback --target "$DSH"
```

A successful rollback restores all nine host preimages, removes every copied GAT or verification file, removes the installation record, and leaves the supported worktree pristine.

## Compatibility artifacts

`compatibility/dsh-0.1.5-rc.2/manifest.json` is the machine-readable authority. It records the exact target identity, source and destination inventory, modes, per-file SHA-256 values, aggregate payload checksum, aggregate patchset checksum, cleanup directories, allowed changed paths, and canonical commands. `scripts/generate-compatibility.mjs` deterministically regenerates that manifest and the before/after host patchset from the pinned DSH and accepted golden commits.
