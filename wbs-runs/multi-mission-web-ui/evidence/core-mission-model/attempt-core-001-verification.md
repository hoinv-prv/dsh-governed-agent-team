# Verification evidence — attempt-core-001

- Mission: `multi-mission-web-ui`
- Revision: `1`
- Plan SHA-256: `582c4aab13d2813e368a2e0ed233a2a05dc34d4071a98603d7d6a2cf20d0b68e`
- Task: `core-mission-model`
- Attempt: `attempt-core-001`

Executed exactly:
- argv: `pnpm exec vitest run packages/core/tests/team.spec.ts packages/core/tests/projection-events.spec.ts`
- cwd: `.`
- timeout: `120000 ms`
- expected exit: `0`
- observed exit: `1`

Observed failure:
- Vitest stopped before test discovery with `TSCONFIG_ERROR`.
- `packages/core/tsconfig.json` extends `../../../tsconfig.base.json`, which is absent from the current workspace.
- The only matching files are compatibility snapshots under `compatibility/dsh-0.1.5-rc.2/patchset/{before,after}/tsconfig.base.json`; using either would widen scope and change the verification environment.

Disposition: failed verification; no acceptance. Core implementation changes are retained for diagnosis, but downstream tasks remain blocked until a reviewed plan revision or an authorized repository-supported test environment resolves the missing base config.
