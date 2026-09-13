# Governed Agent Team

Governed Agent Team (GAT) is a private, opt-in Agent Teams distribution for DeepSeek Harness. Version `0.1.0` is tested with DSH `0.1.5-rc.2` at commit `c291e7961a515f6d7af9304e7fd1d257929aef26`. Other commits are unverified and require an explicit installer override.

## Install

Use a pristine DSH checkout at the supported commit by default. Development source hashes are advisory; patchset integrity, host preimages, installed destination bytes, and path boundaries remain strict. An unverified commit or an otherwise dirty checkout requires a separate explicit override.

```sh
GAT=/home/hoinv/work/dsh-governed-agent-team
DSH=/path/to/pristine/dsh-worktree

node "$GAT/installer/index.mjs" dry-run --target "$DSH"
node "$GAT/installer/index.mjs" install --target "$DSH"
node "$GAT/installer/index.mjs" status --target "$DSH"
```

For an intentional development install on an unverified commit with unrelated local changes:

```sh
node "$GAT/installer/index.mjs" dry-run --target "$DSH" \
  --allow-unverified-dsh --allow-dirty-target
node "$GAT/installer/index.mjs" install --target "$DSH" \
  --allow-unverified-dsh --allow-dirty-target
```

`--allow-dirty-target` never permits overlap with installer-owned files or directories.

Installation copies the current mapped source into these new directories and records hashes of the bytes actually written:

- `packages/experimental/gat-core`
- `packages/experimental/gat-tools`
- `packages/experimental/gat-web`
- `packages/experimental/gat-profile`
- `packages/experimental/gat-web-profile`

The original DSH experimental Agent Teams source directories remain unchanged. The installed TypeScript aggregates select GAT instead of compiling both implementations under the same Cordis service keys. The installer does not run package lifecycle scripts, contact a registry, activate a profile, start a server, or call an AI provider.

The installation record is `$DSH/.gat/installation.json`. A repeated install succeeds without writes only when that record, mapping, patchset, and every installed checksum match. Any installed-state mismatch fails closed.

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
pnpm dsh plugin --profile headless add "link:$DSH/packages/experimental/gat-profile"
pnpm --dir "$HOME/.dsh/profiles/headless" add --save-prod \
  "link:$DSH/packages/experimental/gat-core" \
  "link:$DSH/packages/experimental/gat-tools"
pnpm dsh plugin --profile web add \
  "link:$DSH/packages/experimental/gat-profile" \
  "link:$DSH/packages/experimental/gat-web-profile"
pnpm --dir "$HOME/.dsh/profiles/web" add --save-prod \
  "link:$DSH/packages/experimental/gat-core" \
  "link:$DSH/packages/experimental/gat-tools" \
  "link:$DSH/packages/experimental/gat-web"
```

These commands modify the selected user profile. They are not part of installation or keyless verification.

Build the selected DSH checkout before activation, and do not activate profile packages from a disposable verification worktree. The package entrypoints under `lib/` are build outputs. Use `link:` for the local built packages: `file:` asks the standalone profile package manager to resolve GAT's `workspace:^` dependencies and fails outside the DSH workspace. The three runtime packages are direct profile dependencies because Cordis imports them from the profile root.

After activation, verify that every live profile link comes from the selected DSH checkout and that every package entrypoint exists:

```sh
node "$GAT/installer/verify-profile.mjs" \
  --target "$DSH" \
  --profile-root "$HOME/.dsh/profiles/web"
```

## Roll back

Rollback refuses to overwrite an installed file that changed after installation.

```sh
node "$GAT/installer/index.mjs" rollback --target "$DSH"
```

A successful rollback restores all nine host preimages, removes every copied GAT or verification file, removes the installation record, and leaves the supported worktree pristine.

## Compatibility artifacts

`compatibility/dsh-0.1.5-rc.2/manifest.json` is the machine-readable authority. It records the exact target identity, source and destination inventory, modes, per-file SHA-256 values, aggregate payload checksum, aggregate patchset checksum, cleanup directories, allowed changed paths, and canonical commands. `scripts/generate-compatibility.mjs` deterministically regenerates that manifest and the before/after host patchset from the pinned DSH and accepted golden commits.
