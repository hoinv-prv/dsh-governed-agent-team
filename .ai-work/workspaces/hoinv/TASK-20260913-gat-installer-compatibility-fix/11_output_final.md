# Final Output

## Status
final

## Content

The live `dsh web` failure is fixed without using the forbidden verification worktree.

Root cause: `/home/hoinv/.dsh/profiles/web` linked GAT packages to the verification worktree, whose public `lib/index.js` outputs were missing. The main DSH checkout had no GAT installation. Source-hash authorization was a separate development blocker and could not repair those profile links by itself.

Repository changes:

- Added `GAT_VERSION.json` and explicit tested-commit compatibility evaluation.
- Made development payload hashes advisory while retaining strict patchset, host-preimage, and installed-byte checks.
- Added actual-byte installation records and dynamic compatibility-manifest selection.
- Added explicit `--allow-unverified-dsh` and overlap-safe `--allow-dirty-target` behavior.
- Added a live profile source/entrypoint verifier and regression tests.
- Reviewed and corrected the supplied refactor specification and activation documentation.

Live repair:

- Installed 82 GAT integration files into `/home/hoinv/deepseek-harness`; structural verification passed.
- Preserved all 123 pre-existing, non-overlapping dirty target paths.
- Completed DSH dependency install and full Host/Client/Web build.
- Repointed the Web profile to direct `link:` dependencies under the main DSH checkout.
- Verified all five GAT package origins and entrypoints, imported the three runtime packages, and started `dsh web` successfully on `127.0.0.1:3080`.

Verification: installer tests 11/11 passed; syntax checks and `git diff --check` passed; live installer status and profile verification passed. The target commit remains explicitly reported as `UNVERIFIED`, because it is newer than the tested commit, and installation required the user's explicit development overrides.
