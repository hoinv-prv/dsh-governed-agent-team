# Findings

## Findings List
- STEP-00 task contract is confirmed by the HUMAN.

## Confirmed Findings
- Package identities: `@vuhoi/gat-core`, `@vuhoi/gat-tools`, `@vuhoi/gat-web`, `@vuhoi/gat-profile`, and `@vuhoi/gat-web-profile`.
- Installation mode: checksum-verified copy into the isolated target; no symlink or dependency on the source repository after installation.
- GAT release identity for this installer: `0.1.0`.
- Target package directories: `packages/experimental/gat-core`, `gat-tools`, `gat-web`, `gat-profile`, and `gat-web-profile`; the original DSH experimental Agent Teams directories remain intact.
- Acceptance scope: every requirement in `/home/hoinv/work/dsh-governed-agent-team-install-prompt.md` remains mandatory.
- Supported host: DSH `0.1.5-rc.2` at exact commit `c291e7961a515f6d7af9304e7fd1d257929aef26` only.
- Protected locations: main DSH checkout and golden-reference worktree remain read-only; installer execution must not mutate the GAT source repository.

## Inferred Findings
- The five copied packages require identity/import migration and standalone workspace wiring before they can serve as installer payloads.
- The host patch must be extracted from the exact base-to-golden diff and exclude package payload paths copied from this repository.

## To-Verify Findings
- None.

## Implemented Findings
- Compatibility manifest: `compatibility/dsh-0.1.5-rc.2/manifest.json`; 71 copied payload files and nine checksum-pinned host replacements.
- Host replacements cover Session event/API catalog changes, explicit `@vuhoi` TypeScript aliases, Host/Client aggregate selection, original-package aggregate exclusion, tool-catalog generation input, the Web E2E compiler boundary, and frozen pnpm importers.
- Installer commands implement dry-run, install, status, rollback, exact target identity checks, source/preimage checksums, symlink refusal, idempotence, post-install drift refusal, complete installation records, and simulated-failure rollback.
- Canonical lifecycle verification passed dry-run no-write, injected failure with clean rollback, install, repeated install, and rollback in a disposable exact-commit worktree.
- Frozen offline lockfile verification passed and left `pnpm-lock.yaml` byte-identical.
- Focused installed-package verification passed 147 tests across nine files, including downstream ordinary-permission denial after Team execution opens.
- `pnpm run build` passed and recorded 234 client artifacts; the plain-Node built-library smoke passed 1 test.
- The assembled Web dashboard smoke passed all 3 tests with keyless replay fixtures.
- Canonical verifier result: `status: pass`, 81 changed paths, zero paths outside the allowlist, and zero secret findings.
- Target identity remained DSH `0.1.5-rc.2` at commit `c291e7961a515f6d7af9304e7fd1d257929aef26`; original Agent Teams tracked paths, main-checkout GAT paths, and golden-reference tracked content remained unchanged.
- Verification removed temporary dependency links and lifecycle worktrees and left no verifier, Vite, Playwright, or lifecycle process.

## Notes
- Initial `python` lookup command failed because only `python3` is available; all subsequent AIWS tooling uses `python3`.
- Final capture sweep reviewed installer failures, lockfile normalization, build wiring, and final integrity evidence. The existing design-retrieval candidate remains useful; no additional reusable AIWS candidate met the capture threshold.
