# GAT Installer Version & Compatibility Refactor Specification

**Project:** `dsh-governed-agent-team`
**Target:** Codex implementation
**Status:** Reviewed — approved with the corrections and safety constraints in §2.1
**Primary goal:** Replace source-file hash blocking during installation with explicit version/compatibility metadata and post-install verification.

---

## 1. Background

The current GAT installer performs payload/source hash validation before operations such as:

```bash
node installer/index.mjs status --target <DSH_WORKTREE>
node installer/index.mjs dry-run --target <DSH_WORKTREE>
node installer/index.mjs install --target <DSH_WORKTREE>
```

This causes installation to fail when legitimate development changes are made to GAT source files.

Example failure:

```text
gat-installer: payload hash mismatch for packages/core/src/mission-board.ts
```

This behavior is too strict for an actively developed plugin repository.

The current mechanism also mixes three different concerns:

1. **Source/release integrity**
2. **GAT-to-DSH compatibility**
3. **Runtime/install correctness**

These concerns should be separated.

---

# 2. Goals

Refactor the installer so that:

1. Source-file SHA/hash mismatch does **not block** normal `status`, `dry-run`, or `install`.
2. GAT version and supported DSH versions/commits are declared explicitly in a dedicated version descriptor.
3. Compatibility remains a hard gate where appropriate.
4. Post-install verification remains a hard gate.
5. Release artifact integrity may still use SHA256, but it is separate from runtime installation logic.
6. Existing `compatibility/<dsh-version>/manifest.json` remains usable for integration mapping, but source hashes are no longer required to authorize installation.
7. Development workflows can install from a dirty or modified GAT working tree without regenerating every source hash.

## 2.1 Review corrections and binding safety constraints

The proposal is accepted only with the following corrections, established against the current installer and the 2026-09-13 runtime failure:

1. The GAT version is `0.1.0`, matching the repository and package manifests. DSH `0.1.5-rc.2` is a compatibility target, not the GAT version.
2. Payload source hashes are advisory, but patchset integrity, target host-file preimages, and installed destination hashes remain strict hard gates.
3. Installation records store hashes of the bytes actually copied. They must not claim legacy manifest hashes when development bytes differ.
4. The compatibility manifest is selected by the target DSH version. `--allow-unverified-dsh` may override an unlisted commit only when a manifest for that DSH version/layout exists; it never bypasses host preimage checks.
5. A dirty target remains blocked by default. `--allow-dirty-target` may permit only unrelated dirty paths; any overlap with host files, payload destinations, cleanup roots, or the installation record remains blocked.
6. The installer copies source and patches but does not run package lifecycle scripts. Install-time structural verification and post-build runtime/profile verification are distinct gates; runtime entrypoints cannot be required before the DSH build creates them.
7. The installer does not activate a user profile and therefore does not create profile symlinks. Profile-origin checks apply to explicit activation/runtime verification. A verifier must not mutate or repoint the live profile as a side effect.
8. `status` reports source drift and unverified compatibility without failing, but it must report a broken installed state when recorded destination bytes are missing or changed.
9. Live-profile activation uses `link:` references to the build-complete packages in the selected DSH checkout. `file:` is invalid for this repository because it triggers standalone resolution of `workspace:^` dependencies. `gat-core`, `gat-tools`, and `gat-web` must be direct profile dependencies because the Cordis loader imports them from the profile root; the two profile packages alone are not sufficient with link semantics.

---

# 3. Non-goals

This change does **not**:

- remove compatibility checking;
- remove post-install verification;
- allow silently installing a known-incompatible GAT/DSH combination;
- remove release artifact checksums;
- redesign GAT package architecture;
- redesign DSH profile structure;
- automatically guarantee compatibility with all future DSH versions.

---

# 4. Design Principles

The installer must separate:

```text
GAT VERSION / COMPATIBILITY
        ↓
GAT_VERSION.json
        ↓
Can this GAT version install into this DSH version?
```

from:

```text
RELEASE ARTIFACT INTEGRITY
        ↓
SHA256SUMS.txt / RELEASE_MANIFEST.json
        ↓
Was the downloaded release modified/corrupted?
```

from:

```text
POST-INSTALL VERIFICATION
        ↓
installer/verify.mjs
        ↓
Did installation actually produce a usable GAT integration?
```

Source-tree modifications during development should generate, at most, a warning.

---

# 5. New File: `GAT_VERSION.json`

Create at repository root:

```text
/GAT_VERSION.json
```

Recommended schema:

```json
{
  "schema_version": 1,
  "name": "dsh-governed-agent-team",
  "version": "0.1.0",
  "release_date": "2026-09-13",

  "source": {
    "repository": "hoinv-prv/dsh-governed-agent-team",
    "commit": null
  },

  "compatibility": {
    "dsh": {
      "policy": "tested-commits",
      "tested_versions": [
        "0.1.5-rc.2"
      ],
      "tested_commits": [
        "c291e7961a515f6d7af9304e7fd1d257929aef26"
      ]
    }
  },

  "installer": {
    "schema_version": 1
  }
}
```

---

# 6. `GAT_VERSION.json` Field Semantics

## 6.1 `schema_version`

Required integer.

Example:

```json
"schema_version": 1
```

Installer must reject unsupported future schema versions.

---

## 6.2 `name`

Required string.

Must currently be:

```text
dsh-governed-agent-team
```

Used to detect accidental use of another manifest.

---

## 6.3 `version`

Required semantic-ish version string.

Example:

```text
0.1.0
```

This is the logical GAT version, not a file-integrity identifier.

---

## 6.4 `release_date`

Optional informational field.

Must not control installation behavior.

---

## 6.5 `source.repository`

Informational repository identity.

---

## 6.6 `source.commit`

May be:

```json
null
```

during development.

For a frozen release it may contain the exact GAT commit:

```json
"commit": "abc123..."
```

If populated and the local checkout differs, installer should warn by default, not fail.

Recommended output:

```text
[WARN] Local GAT checkout differs from release source commit.
       expected: abc123
       actual:   def456
```

Optional future strict mode may convert this to an error.

---

# 7. Compatibility Policy

Initial implementation should support:

```json
"policy": "tested-commits"
```

The installer checks the target DSH worktree commit:

```bash
git -C <DSH_WORKTREE> rev-parse HEAD
```

If the commit is in:

```json
compatibility.dsh.tested_commits
```

then:

```text
SUPPORTED
```

Otherwise:

```text
UNVERIFIED
```

By default, `install` should still reject `UNVERIFIED` DSH targets unless the user explicitly opts in.

This preserves the safety property currently provided by the hardcoded expected commit.

---

# 8. Recommended Compatibility States

Internally normalize compatibility to one of:

```text
SUPPORTED
UNVERIFIED
UNSUPPORTED
INVALID_TARGET
```

Meaning:

### `SUPPORTED`

Target DSH version/commit has been explicitly tested.

Installation is allowed.

### `UNVERIFIED`

No explicit compatibility record exists.

Installation is blocked by default, but may be allowed using an explicit override.

### `UNSUPPORTED`

Known incompatible.

Installation must remain blocked unless a future dedicated force mode is intentionally implemented.

### `INVALID_TARGET`

Target is not a valid DSH worktree.

Always fail.

---

# 9. Add Explicit Override for Unverified DSH

Add installer option:

```bash
--allow-unverified-dsh
```

Example:

```bash
node installer/index.mjs install \
  --target /home/hoinv/deepseek-harness \
  --allow-unverified-dsh
```

Behavior:

```text
[WARN] DSH commit 017c7cb... is not present in tested_commits.
[WARN] Continuing because --allow-unverified-dsh was explicitly supplied.
```

The override must be explicit per command invocation.

Do not make this the default.

---

# 10. Remove Source Hashes from the Install Authorization Path

Current behavior conceptually resembles:

```text
for each source file:
    calculate SHA
    compare with compatibility manifest
    mismatch -> abort
```

Replace with:

```text
read GAT_VERSION.json
validate schema
detect GAT working-tree state
detect target DSH version/commit
evaluate compatibility
plan install
perform install
run verification
```

Source file SHA mismatch must no longer cause:

```text
status -> failure
dry-run -> failure
install -> failure
```

---

# 11. Development Working Tree Behavior

Detect whether GAT repository is dirty:

```bash
git status --porcelain
```

If dirty:

```text
[WARN] GAT source tree contains local modifications.
[INFO] Source-tree hashes are not used as an installation gate.
```

Installation should continue.

If untracked files are part of the installed payload, installer must still install the actual source currently present.

Example:

```text
?? packages/core/src/mission-board.ts
?? packages/core/src/mission-plan.ts
```

These files should be treated as valid development payload if referenced by the installation manifest.

## 11.1 Dirty DSH target behavior

The existing installer rejects every dirty target. That default remains correct, but the documented development workflow uses a dirty live DSH checkout and therefore needs a separate explicit override:

```bash
--allow-dirty-target
```

With the flag, the installer must enumerate dirty paths and reject the operation if any dirty path overlaps an installer-owned host file, payload destination/root, cleanup root, or installation record. Unrelated dirty files may remain untouched. This flag is independent from `--allow-unverified-dsh`; a caller may need both.

---

# 12. Role of Existing Compatibility Manifest

Keep:

```text
compatibility/dsh-0.1.5-rc.2/manifest.json
```

but redefine its responsibility.

It should describe:

- source-to-destination mappings;
- package mappings;
- profile integration;
- target paths;
- compatibility metadata;
- required patches;
- required DSH integration points.

It should **not require payload hashes to authorize installation**.

Example conceptual entry:

```json
{
  "source": "packages/core/src/mission-board.ts",
  "destination": "packages/experimental/gat-core/src/mission-board.ts"
}
```

This is sufficient for installation mapping.

If legacy fields such as:

```json
"sha256": "..."
```

still exist, installer may:

- ignore them;
- log informational mismatch;
- preserve them for old tooling.

But they must not block installation.

---

# 13. Backward Compatibility with Existing Manifests

The installer should remain able to read current manifests.

Pseudo-logic:

```js
if (entry.sha256) {
  const actual = calculateHash(source)

  if (actual !== entry.sha256) {
    warn(
      `payload hash differs for ${entry.source}; ` +
      `continuing because source hashes are advisory`
    )
  }
}
```

Recommended warning:

```text
[WARN] Payload differs from frozen manifest:
       packages/core/src/mission-board.ts
       continuing; source hash is advisory only
```

Do not throw.

---

# 14. Release Integrity

Create optional release integrity files:

```text
RELEASE_MANIFEST.json
SHA256SUMS.txt
```

These are intended for downloaded packaged releases, not working-tree install authorization.

Example:

```text
dist/
  dsh-governed-agent-team-0.1.0.tar.gz
SHA256SUMS.txt
```

Example checksum:

```text
13a...  dsh-governed-agent-team-0.1.0.tar.gz
```

Integrity validation should be a separate command or release process.

For example:

```bash
node installer/verify-release.mjs <artifact>
```

This is optional for the first implementation.

---

# 15. Installer Command Behavior

Existing interface:

```text
node installer/index.mjs <dry-run|install|status|rollback> --target <DSH_WORKTREE>
```

Keep this interface.

Add optional:

```text
--allow-unverified-dsh
--allow-dirty-target
```

Potential future options:

```text
--strict-source-version
--json
```

Do not implement future options unless useful.

---

# 16. `status` Behavior

Command:

```bash
node installer/index.mjs status \
  --target /home/hoinv/deepseek-harness
```

Expected output example:

```text
GAT Installer Status

GAT:
  version:       0.1.0
  source commit: 1234567
  source state:  MODIFIED

DSH:
  target:        /home/hoinv/deepseek-harness
  commit:        017c7cb8714a2d81f3d2317e0810fbc69f3f8d00
  compatibility: UNVERIFIED

Installation:
  state:         INSTALLED
  verification:  PASS
```

Important:

`status` should not fail just because compatibility is `UNVERIFIED`.

It should report state.

It should fail only if target is invalid or manifest/version data is malformed.

---

# 17. `dry-run` Behavior

Command:

```bash
node installer/index.mjs dry-run \
  --target /home/hoinv/deepseek-harness
```

For `SUPPORTED`:

```text
[OK] DSH compatibility: SUPPORTED
[PLAN] copy/link ...
[PLAN] update ...
[PLAN] register ...
```

For `UNVERIFIED` without override:

```text
[WARN] DSH compatibility: UNVERIFIED
[BLOCKED] install would require --allow-unverified-dsh
```

Dry-run should still print the full planned mutation set where possible.

Exit code may be non-zero if installation would be blocked.

---

# 18. `install` Behavior

Supported DSH:

```bash
node installer/index.mjs install \
  --target /home/hoinv/deepseek-harness
```

Expected:

```text
[INFO] GAT version 0.1.0
[INFO] DSH compatibility: SUPPORTED
[WARN] GAT working tree is modified
[INFO] Installing...
[INFO] Running post-install verification...
[OK] Installation verified
```

Unverified DSH without override:

```text
[ERROR] DSH commit 017c7cb... has not been verified with GAT 0.1.0
        Re-run with --allow-unverified-dsh only if intentional.
```

Unverified DSH with override:

```bash
node installer/index.mjs install \
  --target /home/hoinv/deepseek-harness \
  --allow-unverified-dsh
```

Expected:

```text
[WARN] Installing against an unverified DSH commit.
...
[INFO] Running post-install verification...
```

Post-install verification failure must still fail the install operation.

Rollback semantics must continue to work.

---

# 19. Post-install Verification

`installer/verify.mjs` should remain the main correctness gate.

The current installer is source-only and the current full verifier builds inside the target after installation. Therefore verification is split explicitly:

- **Install-time structural gate:** installed source/patch bytes match the installation record; mappings and record provenance are valid. This runs as part of `install`.
- **Post-build runtime gate:** after `pnpm install` and `pnpm run build` in the selected DSH target, package entrypoints resolve and load. Profile checks run only when an explicit profile root is supplied.

An absent `lib/index.js` before the build is not an installer failure. An absent or unloadable entrypoint after a successful build is a runtime verification failure.

Verification should check at least:

1. required installed package paths exist;
2. required DSH profile entries exist;
3. package entrypoints resolve;
4. `@vuhoi/gat-core` loads;
5. `@vuhoi/gat-tools` loads;
6. `@vuhoi/gat-web` loads;
7. expected GAT tools/plugins are registered;
8. target profile configuration is syntactically valid;
9. GAT web plugin can resolve required client-side dependencies;
10. no installer-created path points to an unintended temporary verification worktree.

Particularly important:

```text
~/.dsh/profiles/web/node_modules/@vuhoi/gat-web
```

must not accidentally point to paths such as:

```text
~/deepseek-harness/.worktrees/verify-gat-install-...
```

unless that path was explicitly selected as the installation source.

---

# 20. Source Location Tracking

The installer should record the actual GAT source root used during installation.

Recommended state:

```json
{
  "gat_version": "0.1.0",
  "gat_source_root": "/home/hoinv/work/dsh-governed-agent-team",
  "gat_source_commit": "abc123",
  "gat_source_dirty": true,
  "target_dsh_root": "/home/hoinv/deepseek-harness",
  "target_dsh_commit": "017c7cb...",
  "compatibility": "UNVERIFIED",
  "installed_at": "2026-09-13T..."
}
```

Use existing installer state location if one already exists.

Do not invent a second state mechanism unnecessarily.

---

# 21. Symlink Safety

If installer uses symlinks, links must resolve against the actual GAT repository from which installer is executed.

Bad:

```text
~/.dsh/profiles/web/node_modules/@vuhoi/gat-web
→ ~/deepseek-harness/.worktrees/verify-gat-install.../packages/experimental/gat-web
```

when installation was intended from:

```text
/home/hoinv/work/dsh-governed-agent-team
```

Good:

```text
~/.dsh/profiles/web/node_modules/@vuhoi/gat-web
→ /home/hoinv/work/dsh-governed-agent-team/packages/web
```

The profile activation/runtime verification path must verify each resolved link after creation. The source-copy installer itself creates no profile links.

For the current DSH profile model, activation must link all five packages from the selected, built DSH checkout. Only `gat-profile` and `gat-web-profile` belong in `dsh.profile.bundles`; `gat-core`, `gat-tools`, and `gat-web` are direct package dependencies used by loader entries. Verification must reject missing direct dependencies, missing `main` entrypoints, and any resolved package outside the selected target root.

---

# 22. `GAT_VERSION.json` Compatibility Evolution

Initial policy:

```json
"policy": "tested-commits"
```

Future supported policies may include:

```text
tested-commits
version-range
compatibility-matrix
```

Do not implement all policies now.

Design parsing code so another policy can be added later.

Recommended abstraction:

```js
evaluateDshCompatibility({
  versionDescriptor,
  dshVersion,
  dshCommit
})
```

Return:

```js
{
  state: "SUPPORTED" | "UNVERIFIED" | "UNSUPPORTED",
  reason: "...",
  matchedRule: ...
}
```

---

# 23. Version Range — Future Option

Future example:

```json
{
  "compatibility": {
    "dsh": {
      "policy": "version-range",
      "range": ">=0.1.5-rc.2 <0.1.6"
    }
  }
}
```

Do not use version ranges as a replacement for actual testing until DSH APIs are stable enough.

For now, tested commits are safer.

---

# 24. Installer Error Categories

Use distinct errors.

Examples:

```text
ERR_GAT_VERSION_DESCRIPTOR_INVALID
ERR_DSH_TARGET_INVALID
ERR_DSH_UNVERIFIED
ERR_DSH_UNSUPPORTED
ERR_INSTALL_MUTATION_FAILED
ERR_POST_INSTALL_VERIFY_FAILED
ERR_ROLLBACK_FAILED
```

Do not report source hash drift as an error.

Use warning:

```text
WARN_SOURCE_DIFFERS_FROM_FROZEN_MANIFEST
```

---

# 25. Exit Code Expectations

Suggested:

```text
0  success / healthy status
1  generic installer failure
2  invalid arguments
3  invalid target
4  compatibility blocked
5  install mutation failure
6  verification failure
7  rollback failure
```

Exact numbers may be adapted to existing conventions.

Avoid changing existing public exit-code semantics unless necessary.

---

# 26. Logging Requirements

Always show:

```text
GAT version
GAT source root
GAT source commit if available
GAT dirty state
DSH target
DSH commit
compatibility result
installer operation
verification result
```

Do not print hundreds of advisory source hash warnings by default.

If many legacy hashes mismatch, summarize:

```text
[WARN] 17 payload files differ from the frozen compatibility snapshot.
       Source hashes are advisory and installation will continue.
```

Add verbose detail only if an existing verbose/debug mechanism exists.

---

# 27. Required Tests

## Test 1 — Clean supported installation

Given:

- clean GAT source;
- target DSH commit in `tested_commits`.

Expect:

- `status` succeeds;
- `dry-run` succeeds;
- `install` succeeds;
- verification succeeds.

---

## Test 2 — Dirty GAT source

Modify:

```text
packages/core/src/mission-board.ts
```

Expect:

- warning only;
- no payload-hash install block;
- installation allowed if DSH is supported.

---

## Test 3 — New untracked payload source file

Add:

```text
packages/core/src/mission-plan.ts
```

and reference it in installation manifest.

Expect:

- installer handles it;
- no hash freeze required;
- target receives correct payload.

---

## Test 4 — Legacy manifest hash mismatch

Manifest contains old:

```json
"sha256": "OLD_HASH"
```

Source differs.

Expect:

```text
WARN
```

not error.

---

## Test 5 — Supported DSH commit

Target commit is listed.

Expect:

```text
compatibility = SUPPORTED
```

---

## Test 6 — Unverified DSH commit

Target commit not listed.

Without flag:

```text
install -> blocked
```

With:

```bash
--allow-unverified-dsh
```

expect installation to continue.

---

## Test 7 — Invalid DSH target

Target directory is not a valid DSH checkout.

Expect hard failure.

---

## Test 8 — Broken package entrypoint

After installation:

```text
@vuhoi/gat-web/lib/index.js
```

is missing.

Expect post-install verification failure.

---

## Test 9 — Wrong symlink source

Installed symlink points to a temporary worktree instead of current GAT repository.

Expect verification failure or explicit warning treated as failure.

---

## Test 10 — Rollback after install failure

Simulate failure using existing option:

```text
--simulate-failure-after <count>
```

Expect:

- rollback restores target;
- version/compatibility metadata does not break rollback.

---

# 28. Existing Installer Tests

Preserve:

```bash
pnpm test:installer
```

Existing tests must continue passing unless intentionally updated for new semantics.

Add tests specifically for:

- advisory legacy hashes;
- `GAT_VERSION.json`;
- `--allow-unverified-dsh`;
- dirty working tree;
- symlink source root correctness.

---

# 29. Recommended New Test Files

Possible structure:

```text
installer/tests/version-descriptor.test.mjs
installer/tests/compatibility-policy.test.mjs
installer/tests/source-integrity-advisory.test.mjs
installer/tests/install-source-root.test.mjs
```

Use the repo's current test conventions.

---

# 30. `generate:compatibility`

Current command:

```bash
pnpm run generate:compatibility
```

After this refactor, the generator may still generate:

```text
compatibility/<dsh-version>/manifest.json
```

but should not be required merely because a source file changed.

If it currently generates payload hashes, either:

### Preferred

Stop generating file hashes for install authorization.

or:

### Transitional

Continue generating hashes as informational metadata, while installer treats them as advisory.

Prefer transitional compatibility if removing fields would cause unnecessary churn.

---

# 31. Migration Plan

Implement in phases.

## Phase A — Add version descriptor

Add:

```text
GAT_VERSION.json
```

Add parser + schema validation.

No behavior change yet.

---

## Phase B — Add compatibility evaluator

Move current DSH commit check into version-driven logic.

Replace hardcoded expected DSH commit with `tested_commits`.

---

## Phase C — Downgrade source hash mismatch

Change:

```js
throw new Error(...)
```

to advisory warning/summary.

---

## Phase D — Add `--allow-unverified-dsh`

Preserve strict-by-default compatibility safety.

---

## Phase E — Strengthen verification

Verify:

- entrypoints;
- symlinks;
- source root;
- profile integration.

---

## Phase F — Tests and documentation

Update installer README/help and tests.

---

# 32. CLI Help

Update usage from:

```text
usage: node installer/index.mjs <dry-run|install|status|rollback> --target <DSH_WORKTREE> [--simulate-failure-after <count>]
```

to:

```text
usage:
  node installer/index.mjs <dry-run|install|status|rollback>
    --target <DSH_WORKTREE>
    [--allow-unverified-dsh]
    [--allow-dirty-target]
    [--simulate-failure-after <count>]
```

Document:

```text
--allow-unverified-dsh

Allow installation into a DSH commit that is not listed as tested in
GAT_VERSION.json. This does not bypass post-install verification.

--allow-dirty-target

Allow installation into a dirty DSH checkout only when every dirty path is outside installer-owned paths. This does not bypass host preimage or installed-file checks.
```

---

# 33. Example Desired Workflow

Development:

```bash
cd /home/hoinv/work/dsh-governed-agent-team

node installer/index.mjs status \
  --target /home/hoinv/deepseek-harness
```

Output:

```text
GAT 0.1.0
source: modified

DSH:
  commit: 017c7cb...
  compatibility: UNVERIFIED
```

Then:

```bash
node installer/index.mjs dry-run \
  --target /home/hoinv/deepseek-harness \
  --allow-unverified-dsh \
  --allow-dirty-target
```

Then:

```bash
node installer/index.mjs install \
  --target /home/hoinv/deepseek-harness \
  --allow-unverified-dsh \
  --allow-dirty-target
```

Then:

```text
post-install verification: PASS
```

No source hash regeneration is required merely because:

```text
mission-board.ts
mission-plan.ts
TeamAction.tsx
```

were changed.

---

# 34. Recommended Acceptance Criteria

Implementation is complete when all of the following are true.

1. Running installer against a dirty GAT working tree no longer fails because a source hash changed.
2. `GAT_VERSION.json` is the authoritative source for GAT version and DSH compatibility.
3. Current hardcoded expected DSH commit is removed from installer logic.
4. A tested DSH commit installs normally.
5. An unverified DSH commit is blocked by default.
6. `--allow-unverified-dsh` explicitly permits an unverified DSH target.
7. Install-time structural verification remains mandatory, and post-build runtime verification remains mandatory before activation.
8. Missing GAT package entrypoints still fail verification.
9. Installer records or reports the actual GAT source root.
10. Installer does not unintentionally retain symlinks to old verification worktrees.
11. Legacy manifest hashes, if retained, are advisory only.
12. Existing rollback behavior remains functional.
13. `pnpm test:installer` passes.
14. New compatibility/version tests pass.
15. Dirty targets are blocked by default; the explicit dirty-target override permits only non-overlapping changes.
16. Installation records hash the actual copied development payload.

---

# 35. Codex Implementation Instructions

When implementing this spec:

1. Inspect existing installer architecture before editing.
2. Reuse existing manifest/parser/state/rollback infrastructure.
3. Do not rewrite the installer unnecessarily.
4. Keep changes narrow and backward-compatible.
5. Preserve current rollback semantics.
6. Add tests before or alongside behavior changes.
7. Do not delete existing compatibility manifests.
8. Do not delete legacy hash fields unless necessary.
9. Treat legacy source hashes as advisory.
10. Keep compatibility strict by default.
11. Add explicit override only for `UNVERIFIED`, not known `UNSUPPORTED`, unless existing architecture strongly requires another distinction.
12. Run all installer tests after changes.
13. Produce a short implementation report describing:
    - files changed;
    - old behavior;
    - new behavior;
    - migration implications;
    - test results;
    - remaining risks.

---

# 36. Preferred Final Architecture

```text
dsh-governed-agent-team
│
├── GAT_VERSION.json
│      │
│      └── version + DSH compatibility
│
├── compatibility/
│      └── dsh-*/
│            └── manifest.json
│                 mapping / integration contract
│
├── installer/
│      ├── index.mjs
│      └── verify.mjs
│
├── packages/
│      ├── core
│      ├── tools
│      ├── web
│      ├── profile
│      └── web-profile
│
└── optional release integrity
       ├── RELEASE_MANIFEST.json
       └── SHA256SUMS.txt
```

Responsibility split:

```text
GAT_VERSION.json
    = What version is this?
    = Which DSH versions/commits are tested?

compatibility manifest
    = How is GAT integrated into a particular DSH layout?

SHA256SUMS / release manifest
    = Is the downloaded release artifact intact?

installer verify
    = Does the installed system actually work?
```

This separation is the intended outcome of this refactor.
