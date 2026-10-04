# Governed Agent Team

Governed Agent Team (GAT) is a private, opt-in Agent Teams distribution for DeepSeek Harness. The default compatibility artifact targets DSH `0.1.5-rc.2` at commit `c291e7961a515f6d7af9304e7fd1d257929aef26`. A separate additive Durable binding artifact targets the qualified prerequisite revision `5c02ce9f3e44dfce3f87498f65cf684194ad4572` and WK Durable Agent revision `a8e215433ae050e36e0ba27205701be1a5f114a1`. It must be selected explicitly; it does not change the default installer or enable a profile. Integrated binding/profile qualification is recorded under AIP-EXEC-022, and deployment remains a separate decision. Other commits are unverified and require an explicit installer override.

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

## Additive Durable binding compatibility

The Durable binding artifact is separate from the default compatibility above. It selects the exact DSH prerequisite commit and checks captured prerequisite hashes before making changes. Use it only with a clean checkout at the artifact's exact target commit:

```sh
BINDING_COMPATIBILITY=dsh-0.1.5-rc.2-binding-5c02ce9

node "$GAT/installer/index.mjs" dry-run --target "$DSH" --compatibility "$BINDING_COMPATIBILITY"
node "$GAT/installer/index.mjs" install --target "$DSH" --compatibility "$BINDING_COMPATIBILITY"
node "$GAT/installer/index.mjs" status --target "$DSH" --compatibility "$BINDING_COMPATIBILITY"
node "$GAT/installer/index.mjs" rollback --target "$DSH" --compatibility "$BINDING_COMPATIBILITY"
```

This selection adds `gat-durable-agent`, `gat-durable-profile`, and the prebuilt `gat-durable-provider` beside the existing packages. It writes a separate `$DSH/.gat/durable-binding-installation.json` receipt. Rollback must use the same compatibility selection; it restores captured host preimages and removes only the added package roots and binding receipt. It preserves v3 attachment records, Sessions, and provider data.

The lifecycle verifier creates a fresh disposable worktree at the pinned host commit and leaves it for inspection:

```sh
node "$GAT/installer/verify-binding.mjs" \
  --host "$DSH_HOST" \
  --target /tmp/gat-binding-verify \
  --provider "$WK_REPO"
```

`DSH_HOST` must be at `5c02ce9f3e44dfce3f87498f65cf684194ad4572`; `WK_REPO` must be at `a8e215433ae050e36e0ba27205701be1a5f114a1`. The target path must not already exist. The integrated production qualification is recorded in the AIP-EXEC-022 evidence workspace; artifact availability and lifecycle verification do not by themselves qualify deployment.

## Verify

The canonical verifier is keyless. It runs installer lifecycle checks in a disposable worktree, a frozen offline lockfile-only install check, focused Host and Web tests, a complete DSH build, the built-library smoke, and the assembled Web dashboard smoke. It reuses the main checkout's existing dependency tree through temporary links; the install check does not write `node_modules` or package content to the shared pnpm store.

```sh
node "$GAT/installer/verify.mjs" --target "$DSH"
```

No production service or real provider is used. Chromium must already be available through the DSH Playwright installation.

## Activate explicitly

After the applicable verification and deployment approval, add the local profile layers to the intended DSH profile. GAT is never enabled by default. The existing headless and Web commands below install the default GAT layers only.

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

The Durable layer is an additional opt-in profile after `gat-profile`. Once the exact compatibility artifact and integration qualification are approved, add both profile layers and their runtime packages explicitly:

```sh
pnpm dsh plugin --profile headless add "link:$DSH/packages/experimental/gat-profile"
pnpm dsh plugin --profile headless add "link:$DSH/packages/experimental/gat-durable-profile"
pnpm --dir "$HOME/.dsh/profiles/headless" add --save-prod \
  "link:$DSH/packages/experimental/gat-core" \
  "link:$DSH/packages/experimental/gat-tools" \
  "link:$DSH/packages/experimental/gat-durable-agent" \
  "link:$DSH/packages/experimental/gat-durable-profile" \
  "link:$DSH/packages/experimental/gat-durable-provider"
```

The Durable composition exports `@vuhoi/gat-durable-agent/composition` and `/provider`. The profile selects its strict `team_members.durable.yaml` initializer and requires an explicitly dedicated provider and single-host workspace. These topology assertions are configuration inputs, not distributed-lock proof. Do not activate the layer until integration qualification and the deployment owner's topology review are complete.

Build the selected DSH checkout before activation, and do not activate profile packages from a disposable verification worktree. The package entrypoints under `lib/` are build outputs. Use `link:` for the local built packages: `file:` asks the standalone profile package manager to resolve GAT's `workspace:^` dependencies and fails outside the DSH workspace. For the default GAT profile, the three runtime packages are direct profile dependencies because Cordis imports them from the profile root.

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

A successful rollback restores the selected artifact's recorded host preimages, removes its copied GAT or verification files and installation receipt, and leaves the supported worktree pristine. The default artifact uses `$DSH/.gat/installation.json`; the additive Durable artifact uses `$DSH/.gat/durable-binding-installation.json` and must be rolled back with the same `--compatibility` id used to install it.

## Compatibility artifacts

`compatibility/dsh-0.1.5-rc.2/manifest.json` remains the machine-readable authority for the default install. The additive binding artifact at `compatibility/dsh-0.1.5-rc.2-binding-5c02ce9/manifest.json` independently records the exact DSH and WK revisions, prerequisite hashes, source/destination inventory, payload hashes, host preimages, cleanup roots, and its separate installation receipt. `scripts/generate-compatibility.mjs` regenerates the default artifact; `scripts/generate-binding-compatibility.mjs` regenerates the exact-revision Durable artifact from the qualified host/provider inputs. The existing default snapshot and compatibility artifact remain intact.
