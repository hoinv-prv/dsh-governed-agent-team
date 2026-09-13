# Findings

## Findings List
- ...

## Confirmed Findings
- 2026-09-13 Gate U1: HUMAN replied "OK, run", confirming diagnosis of the `dsh web` failure, review/correction of the supplied refactor spec, implementation of the repository fix, and verification of a safe recovery path.
- 2026-09-13 HUMAN constraint: do not use `/home/hoinv/deepseek-harness/.worktrees/verify-gat-install-0.1.5-rc.2`. The only allowed live DSH target is `/home/hoinv/deepseek-harness`; the GAT source is `/home/hoinv/work/dsh-governed-agent-team`.

## Root-cause evidence

- The live Web profile declares `@vuhoi/gat-profile` and `@vuhoi/gat-web-profile` as absolute links into the forbidden verification worktree in `/home/hoinv/.dsh/profiles/web/package.json` and its lockfile.
- Transitive links for `@vuhoi/gat-core`, `@vuhoi/gat-tools`, and `@vuhoi/gat-web` resolve to the same verification worktree.
- Those linked packages expose `lib/index.js` as their `main`/default export, but the linked build only contains TypeScript compiler output under `lib/types/` (and `gat-web` has no `lib/`), so loader resolution fails exactly as shown in the user log.
- The main DSH checkout at `/home/hoinv/deepseek-harness` is commit `017c7cb8714a2d81f3d2317e0810fbc69f3f8d00`, has no `.gat/installation.json`, and has no `packages/experimental/gat-*` installation. The active profile therefore points at a separate, stale verification installation rather than the requested live target.
- `installer/index.mjs` does not activate user profiles. The stale profile links were created by a separate `dsh plugin --profile web add file:...` activation. Installer source-hash validation can prevent a new development install, but changing that gate alone cannot repair the current profile links or missing build entrypoints.
- Main-target install completed with 82 recorded files and install-time structural verification PASS. The installation record identifies the actual GAT source root and preserves the 123 pre-existing, non-overlapping dirty target paths.
- `CI=true pnpm install --frozen-lockfile` and `CI=true pnpm run build` completed in `/home/hoinv/deepseek-harness`; GAT Host and Client bundles were generated.
- Live profile activation with `file:` failed because standalone profile resolution cannot satisfy GAT `workspace:^` dependencies. Activation with `link:` succeeded, but Cordis runtime package names still required direct profile-root links. Adding direct links for `gat-core`, `gat-tools`, and `gat-web` resolved all imports.
- `installer/verify-profile.mjs` passes for all five packages and confirms every source path is under `/home/hoinv/deepseek-harness/packages/experimental` and every `main` entrypoint exists.
- `pnpm dsh web` started successfully at `127.0.0.1:3080`; an unauthenticated HTTP request returned 401, demonstrating the server is alive and enforcing its token rather than crashing during plugin loading.

## Inferred Findings
- Specification verdict: approved with revisions, not correct as originally written.
- Correct direction: explicit version/compatibility metadata, advisory development-source hashes, strict compatibility by default, and explicit unverified override.
- Required corrections applied to the spec: GAT is version `0.1.0`; DSH `0.1.5-rc.2` is the target version; patch/preimage/installed hashes remain strict; install records hash actual copied bytes; manifest selection follows target version; dirty-target override is explicit and overlap-safe; source installation and post-build runtime verification are separate; profile-link checks belong to explicit activation/runtime verification because the installer creates no profile links.
- The live target's nine host preimages all match the `dsh-0.1.5-rc.2` compatibility patchset despite commit drift, and its existing dirty paths do not overlap current installer-controlled paths. This supports an explicit, non-overlapping dirty-target override without weakening per-file mutation safety.

## To-Verify Findings
- ...

## Notes
- Implementation added `GAT_VERSION.json`, version/compatibility helpers, advisory payload drift handling, actual-byte installation records, dynamic DSH-version manifest selection, explicit unverified and non-overlapping dirty-target overrides, a live-profile origin/entrypoint verifier, tests, and corrected documentation/specification.
- Installer tests: 11 passed, 0 failed.
- Final Capture Sweep: reviewed task diffs, runtime findings, activation failures, and verification results. Added 1 reusable-pattern capture (`CAP-005-02`); inbox total is 2 captured entries, with 0 relation candidates. Promotion remains HUMAN-controlled; both entries will be deferred to the project capture backlog on AIP close.
