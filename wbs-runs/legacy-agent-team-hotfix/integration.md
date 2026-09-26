# Canonical integration verification — legacy-agent-team-hotfix

## Attempt 1 — failed and charged

Plan: revision 4, SHA-256 `6998784540c089965201296def7960802ad75691264a6920f60450184892f92e`  
Attempt: `attempt-integration-001`

Declared sequence:
1. Dedicated worktree reset to `c291e7961a515f6d7af9304e7fd1d257929aef26`: PASS.
2. Dedicated worktree `clean -fdx`: PASS.
3. Compatibility regeneration: PASS; 9 host files, 74 payload files; patchset `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`; payload `22df7d8dfbf52fb1c1be6e6e9e0f84fff3b1dea375921bfe109a12a712d7fbc7`.
4. Installer: PASS; manifest `gat-0.1.0-dsh-0.1.5-rc.2-c291e796`, 83 files, structural verification PASS.
5. Canonical verifier: FAIL at focused tests; verifier exited 1 and stopped before full build/smokes.

Observed focused result: 9 files; 8 passed, 1 failed. 164 tests; 162 passed, 2 failed.

Both failures are stale test substrings, not product behavior:
- configured minimum 1 expected `requires at least 1 durable active teammates; found 0`, while actual includes the strengthened approval-aware sentence `Team execution requires an exact current Team plan approved by HUMAN and at least 1 durable active teammates; found 0 durable active teammate(s)`;
- configured minimum 2 has the identical mismatch for count 2.

No rerun occurred. The task stopped on the first verifier failure as required. Full build, built-library smoke, and dashboard smoke remain unverified.

## Attempt 2 — failed and charged

Plan: revision 5, SHA-256 `45154051e1a231a175ce9a1eeee0e9af15ae582a232e31ab01a3207d3574b189`  
Attempt: `attempt-integration-002`

Declared sequence:
1. Dedicated worktree reset/clean: PASS.
2. Compatibility regeneration: PASS; 9 host files, 74 payload files; patchset `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`; payload `6603a5d51b33bc13eddfb17cfae380568661dd815425246da0ac658f61067e5f`.
3. Installer: PASS; manifest `gat-0.1.0-dsh-0.1.5-rc.2-c291e796`, 83 files, structural verification PASS.
4. Focused suite: PASS — 9 files, 164 tests.
5. Full DSH host/client build: PASS; Web shell assembled.
6. Built-library smoke: FAIL — 1 file, 1 test. The generated remote descriptor contains the pre-existing multi-mission methods plus the new import method, but `packages/core/tests/built-lib.e2e.ts` expects only the legacy task methods plus import. This is a stale expected descriptor list in the hotfix's test file; the built library itself exposes the required methods.
7. Assembled dashboard smoke: not reached.

No additional rerun occurred. The verifier exited 1 at the first failed post-build stage.

## Attempt 3 — failed and charged

Plan: revision 6, SHA-256 `07a175111b15d1e79874c4a6f874bab8fb9365e803584f9f3492328669e12bf9`  
Attempt: `attempt-integration-003`

Declared sequence:
1. Dedicated worktree reset/clean: PASS.
2. Compatibility regeneration: PASS; 9 host files, 74 payload files; patchset `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`; payload `76067048dcb846bcdb33717d0be9c1789c06bbd8eafec484758ca5dc2761ea54`.
3. Installer: PASS; 83 files, structural verification PASS.
4. Focused suite: PASS — 9 files, 164 tests.
5. Full DSH host/client build and Web shell assembly: PASS.
6. Built-library smoke: PASS.
7. Assembled dashboard smoke: FAIL — runtime panel contains the already-present Missions section, but `verification/web/task.expected.md` omits it. The only diff adds heading `Missions`, button `Add Mission`, and text `No missions yet`; one golden comparison failed.

No further rerun occurred. The verifier exited 1 at this final stage.

## Attempt 4 — accepted candidate

Plan: revision 7, SHA-256 `67dc8367df9a0b66770c3faa81b9c7a3795e9217c93edb98c50db355ef36000c`  
Attempt: `attempt-integration-004`

Declared sequence:
1. Dedicated worktree reset to `c291e7961a515f6d7af9304e7fd1d257929aef26`: PASS.
2. Dedicated worktree `clean -fdx`: PASS.
3. Compatibility regeneration: PASS; 9 host files, 74 payload files; patchset `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`; payload `49a66127373a581b9ad7ee9940582a76affb5f49ab63e421e6629e2cc05499e7`.
4. Installer: PASS; manifest `gat-0.1.0-dsh-0.1.5-rc.2-c291e796`, 83 files, structural verification PASS.
5. Canonical verifier: PASS (exit 0).
   - installer CLI/lifecycle checks: PASS;
   - focused core/tools/Web/profile suite: 9 files, 164 tests PASS;
   - full DSH host/client build and Web shell assembly: PASS;
   - built-library smoke: PASS;
   - assembled dashboard smoke and fixture inventory: 3 tests PASS;
   - final installation status: installed/SUPPORTED;
   - changed paths: 84; paths outside allowlist: 0; secret findings: 0.

Limitations: the verifier warns that the GAT source tree is dirty, so source hashes are advisory; exact approved WBS hashes and staged integration artifacts remain recorded. No live GUI/profile activation or server restart was performed.

## Post-pass final-review reconciliation

Final review found current `packages/web/src/client/locales.ts` renders `Import approved plan and approve`, while the accepted dashboard golden still says `Approve current plan`. Although attempt 4 exited 0, that unresolved current-source/golden contradiction and the absence of a persisted raw verifier log make its acceptance insufficient for mission closure. A reviewed revision must update the exact golden label, persist the next verifier output, and rerun canonically.

## Attempt 5 — failed and charged

Plan: revision 8, SHA-256 `bd90415f5a4c6d268b9326a86088bee26e24856349a3908ee5d0bbe6b9c9a288`  
Attempt: `attempt-integration-005`

- Reset/clean/regenerate/install: PASS.
- Compatibility payload SHA-256: `486d0fdb396d37ee1992f100ec1464a1a8176f87ee22e5240224cf7042b6c8f0`.
- Focused suite, full build, and built-library smoke: PASS.
- Dashboard smoke: FAIL — observed runtime still renders `Approve current plan`, while revision 8 golden expected `Import approved plan and approve`; 2/3 dashboard tests passed.
- Raw combined verifier output is durably persisted at `evidence/integration-verification/attempt-integration-005/verifier.log`.

This evidence disproves revision 8's golden-only hypothesis. The runtime label is stable across attempts 3–5. A new reviewed revision must align the English source copy and golden with the observed runtime without changing import behavior, then rerun canonically.

## Attempt 6 — accepted candidate

Plan: revision 9, SHA-256 `79ea97523df2124db54b05eb82bdf6ef2de0244543fe71fb121d53dc87848b71`  
Attempt: `attempt-integration-006`

- Reset/clean/regenerate/install: PASS.
- Compatibility: 9 host files, 74 payload files; patchset `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`; payload `2dca38007ed5e0533f04f9f26c0eb140dda29ed593301b29f67b62e7184dd5e5`.
- Focused suite: PASS — 9 files / 164 tests.
- Full host/client build and Web shell: PASS.
- Built-library smoke: PASS — 1 test.
- Dashboard smoke/fixture inventory: PASS — 3 tests.
- Final status: installed/SUPPORTED; 84 changed paths; 0 outside allowlist; 0 secret findings.
- Canonical verifier exit: 0.
- Raw combined output: `evidence/integration-verification/attempt-integration-006/verifier.log`.

No live GUI activation or server restart occurred. Source remains dirty, so installer source hashes are advisory.
