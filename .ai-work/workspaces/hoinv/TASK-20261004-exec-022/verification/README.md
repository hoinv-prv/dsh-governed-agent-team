# Final verification ledger — AIP-EXEC-022

Final target: `/home/hoinv/work/dsh-binding-distribution-closed-final`. Exact selected manifest SHA-256: `2a0c9a5474d6a98ecb767522dce29dc3c259d48697bc61b2b0ec796a5cb07e30`. Host prerequisite is 5c02ce9 over c291; WK is unchanged a8e2154. `production-qualification-receipt.json` indexes source, exact artifact, actual loaded modules, independent review and governance results. Previous original/final/qualified/accepted/review-final runs remain history; no failed report was overwritten or represented as a final run.

| Check | Result | Final evidence |
|---|---|---|
| Full GAT source |333 PASS /24 files|production-all-gat-tests-final.log|
| Host admission/authority/prompt/tools boundaries |767 PASS /29 files|production-host-boundaries-final.log|
| Core and actual WK Loader source |166 PASS /11 files|core-production-receipt.json|
| Adapter/provider source |48 PASS /5 files|adapter-production-tests.log|
| Ordinary complete type-aware lint |Exit0; no diagnostics; all 11 previous owners included|production-type-aware-lint-complete-final.log|
| Installer |21 PASS|binding-installer-tests-closed-final.log|
| Owning documentation |34 PASS /0 failed /0 skipped|binding-closed-final-doc-sync.log|
| Source mapping |18 rows;138 files;184 anchors;80 test locators;0 errors|production-mapping-validation.json|
| Exact installation/lifecycle |205 rows /244 guards; fresh install, failure restore, repeat, status, rollback, reinstall PASS|binding-distribution-closed-final.json|
| Public and extracted archives |8 packages, shared public authenticated control context PASS|binding-built-packed-exports-closed-final.json|
| Actual built Loader/provider/recovery |5 cases /22 public modules PASS; native/profile hashes|production-built-runtime-closed-final.json|
| Actual supported browser WS |3 PASS, including independently asserted 5 Idle Agents|production-browser-closed-final.log|
| Built Core/Remote contribution |1 PASS|production-built-core-closed-final.log|
| Selected TypeScript SDK |7 PASS,12 unrelated scenarios filtered by name|production-sdk-ts-closed-final.log|
| Canonical corpus |3 PASS|production-sdk-corpus-closed-final.log|
| Python SDK |4 scenarios PASS|production-python-closed-final-sdk-*.log|
| All-step ASC reading surfaces |9 rebuilt/read/identity-checked snapshots|production-asc-all-steps.json|

Counts overlap. TypeScript/Python API facades launch the actual built CLI; installed registry SDK/wheel qualification is outside scope. Filtered SDK scenarios are unrelated coverage, not AIP criterion waivers. Conditional isolated-only exclusions are explicitly mapped in acceptance-matrix.md.

Compilers, both bundle faces and Web were built and qualified on review-final after the runtime-peer fix. Closed-final changes only 4 README status sentences and 2 matched translation sidecars. All 8,311 compiled/Web/native/compiler-cache files and 8 public entry hashes were carried byte-identically; this is recorded artifact reuse, not a new compiler/bundle run. Fresh installer, frozen lock, native flock, public/packed probes, owning documentation and all 9 parent replay commands pass on closed-final. `binding-closed-final-build-cache.json` and `binding-closed-final-artifact-proof.json` bind that distinction and post-replay hashes.

Reproduction uses the checked-in verifiers and private temporary storage. From repository root:

```sh
node installer/index.mjs status --target /home/hoinv/work/dsh-binding-distribution-closed-final --compatibility dsh-0.1.5-rc.2-binding-5c02ce9
node installer/verify-binding-exports.mjs --target /home/hoinv/work/dsh-binding-distribution-closed-final
node installer/verify-binding-runtime.mjs /home/hoinv/work/dsh-binding-distribution-closed-final
```

Browser and Core commands from the sealed target use `DSH_SNAPSHOT=replay node node_modules/vitest/vitest.mjs run --config vitest.web.config.ts apps/web/tests/gat-agent-team-panel.e2e.ts` and `--config vitest.e2e.config.ts packages/experimental/gat-core/tests/built-lib.e2e.ts`. TS SDK uses `DSH_EXAMPLE_MODE=lib DSH_SNAPSHOT=replay` with vitest.snapshot.config.ts and the exact 7-scenario name filter recorded in the parent receipt/command evidence; corpus is a separate unfiltered run. Python uses `PYTHONPATH=python/sdk/src /home/hoinv/anaconda3/bin/python scripts/smoke-python-runtime.py --scenario <sdk-request-refresh|sdk-snapshot|sdk-restart|sdk-minimal-in-history> --exe apps/cli/lib/bin.js`.

Final strict task lint and governed close results are in production-task-lint-final.log, production-governed-close.log and production-post-close-status.log. Whole-tree strict lint retains 0 errors/37 existing warnings/3005 info/1 accepted and exits 1; it is not represented as a clean strict whole-tree PASS. No suppression or unrelated Wiki/Truth repair is applied. All 14 captures receive explicit account-backlog disposition. No deployment, push, merge, publication or original dirty-work reset is performed.
