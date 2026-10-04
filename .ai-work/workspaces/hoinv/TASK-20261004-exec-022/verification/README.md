# Verification ledger — AIP-EXEC-022

Current authoritative step is STEP-07. Source tests qualify foundation/adapter, not registered production child dispatch. Test source bytes are compared in tested-source-hashes.json. artifact-hashes.json records built entry/manifest/baseline identities. asc-refresh.json records each rebuild/read and the STEP-08 preview. Logs are fresh runs, not historical mapping claims.

Disposable DSH build/test checkout: /tmp/gat-exec022-verify at compatible c291e7961a515f6d7af9304e7fd1d257929aef26 (0.1.5-rc.2). Current GAT source and candidate adapter copied into experimental packages. Candidate adapter added only to scratch host TS references. WK public provider is a built copy at /tmp/gat-exec022-da-provider from sibling clean a8e215433ae050e36e0ba27205701be1a5f114a1. yaml 2.9.1 and existing dependencies linked; native-system build completed. No external source checkout or live runtime was changed. Initial pnpm bootstrap, missing native binary/link and fixture failures were resolved during setup; final exits below describe the final runs. Native GC warnings remain visible in source logs.

| Final check | Exit / result | Raw log |
|---|---|---|
| Source suite | 0; 19 files / 235 tests PASS | source-tests.log |
| Installer CLI suites | 0; 11 PASS | installer-tests.log |
| Host aggregate TS | 0 | host-types.log |
| Host bundle / generated remote API | 0 | host-bundle.log |
| Client aggregate TS | 0 | client-types.log |
| Client bundle | 0 | client-bundle.log |
| Web Vite build | 0; chunk size warnings | web-build.log |
| Built core smoke | 0; 1 PASS | built-core-smoke.log |
| Plain Node adapter/core exports | 0; closed argument rejection PASS | built-adapter-smoke.log |
| Default install dry-run/install/status/rollback | each 0; 94 installed files structural PASS | install-dry.log, install.log, install-status.log, rollback.log |
| Keyless installed-profile browser | 1; 2 PASS / 1 FAIL | browser.log |
| Strict task lint | 0; errors=0 warnings=0 info=0 | task-strict-lint.log |
| Strict whole-tree lint | 1; errors=0 warnings=37 info=3005 accepted=1 (existing baseline warnings) | whole-tree-strict-lint.log |

Final source command (cwd /tmp/gat-exec022-verify):
`DSH_SNAPSHOT=replay node node_modules/vitest/vitest.mjs run packages/experimental/gat-core/tests packages/experimental/gat-tools/tests packages/experimental/gat-durable-agent/tests packages/experimental/gat-profile/tests packages/experimental/gat-web-profile/tests packages/experimental/gat-web/tests`

Other commands in that checkout: `node node_modules/typescript/bin/tsc -b tsconfig.host.json`; `node node_modules/tsdown/dist/run.mjs --env.DSH_BUILD_FACE host`; `node node_modules/typescript/bin/tsc -b tsconfig.client.json`; `node node_modules/tsdown/dist/run.mjs --env.DSH_BUILD_FACE client`; from apps/web, `node node_modules/vite/bin/vite.js build`; `DSH_SNAPSHOT=replay node node_modules/vitest/vitest.mjs run --config vitest.e2e.config.ts packages/experimental/gat-core/tests/built-lib.e2e.ts`; `node <workspace>/verification/built-entry.mjs /tmp/gat-exec022-verify`; browser: `DSH_SNAPSHOT=replay node node_modules/vitest/vitest.mjs run --config vitest.web.config.ts apps/web/tests/gat-agent-team-panel.e2e.ts`.

Root installer tests: `node --test installer/tests/*.test.mjs`. Separate fresh disposable /tmp/gat-exec022-install used `node installer/index.mjs install --target /tmp/gat-exec022-install --dry-run`, then install, status and rollback. Default installer excludes the candidate adapter pending host/authority qualifications. Full installer/verify.mjs pipeline is not claimed PASS: individual checks were run directly to avoid pnpm's implicit reinstallation for the scratch-only peer package, and the browser golden failed.

Browser failure is a model-label mismatch against supplied golden; actual defaults are unchanged in HEAD packages/tools/src/team-config.ts. No record-mode overwrite. Real reserved-child, request-refresh, exact authority and nested capability prerequisites remain unqualified; no deployment/profile activation, packed production adapter proof or live loaded-module evidence is claimed.

Strict lint commands (project root): `python3 .ai-work/tooling/lint_all.py --scope task --workspace .ai-work/workspaces/hoinv/TASK-20261004-exec-022 --aip .ai-work/aip/hoinv/exec/AIP-EXEC-022-implement-durable-agent-binding.md --strict`; `python3 .ai-work/tooling/lint_all.py --strict`. `git diff --check` passed. Six captured candidates await HUMAN review; no direct Wiki/Truth changes.
