# Implementation handoff — AIP-EXEC-024

Delivered an additive named plugin `@vuhoi/gat-durable-agent/execution-composition` for fresh isolated GAT task executions. It binds public WK before the first execution request; only exact task/intent-selected `durable-memory:<id>` native tools retrieve bodies into tool results/history. No ordinary memory context/catalog/guidance/body enters system prompt. Existing direct entry behavior is preserved on its separately compatible Host.

## Design and implementation

Read official GAT DETAIL_DESIGN DD-09/15/16 and §§5/7/8, BASIC_DESIGN external flow, DURABLE_AGENT_INTEGRATION, SOURCE_CODE_MAP and member-binding freeze §§2–4/8/12; external DA Architecture AD-02–05, Basic BD-02–05 and Detail DD-02–04/DD-06–09. Update design before dependent source: Detail §§9–10, Basic §13 and Integration additive execution section. Detail §11 and final source map record delivery; no Truth/canonical/wiki promotion. Full pre§9 Detail, freeze, selected WK source/design and selected main DSH inputs remain unchanged in final-consistency.json.

Source in `packages/durable-agent/src/`: execution-composition.ts named Config/apply; execution-host.ts validated structural public service port; execution-binding.ts detached closed config, exact authority, native selected reads and joined lifecycle; execution-review.ts optional trusted packet/receipt/ACL/rationale/audit input and synchronous revocation. Shared tools.ts changes old type dependencies only; unchanged ownership.ts emits once in the joint artifact. Additive exports/type graphs/build config and README distinguish both entries. scripts/assemble-durable-agent.mjs is bounded build tooling, not a runtime or snapshot runner.

Exact authority around awaits/publication, UTF-8/attempt/aggregate bounds, retained request denial, synchronous cutoff and joined physical cleanup/release are qualified. Failed cleanup retains quarantine. Optional reviewer mode has no memory/ambient tools; required trusted subscribeRevocation must notify before candidate/ACL/authorization withdrawal. Native team_execution_submit remains provisional; task acceptance is external. Live checkpoint rebind validates persisted identity/config and re-resolves current reviewer input, without new persistence fields or OS crash-lock claims.

## Exact pins and final artifact

GAT base `6f74ab239cbe795f0742d18831a433323f238460` plus selected working-tree bytes; current execution Host `c1157f7ed448b40c463c1a43fa595b12294fd50d`; compatible direct Host `5c02ce9f3e44dfce3f87498f65cf684194ad4572`; public WK `a8e215433ae050e36e0ba27205701be1a5f114a1`, package0.1.0 normal dependency. Final built checks retain Host Cordis4.0.4 and WK own4.0.2, same WK/provider/Consumer constructor, no exemption/override.

Artifact: [final tarball](verification/public-artifact/final-attempt-01/packed/vuhoi-gat-durable-agent-0.1.0.tgz), SHA256 `7f7848ce2eff8f07f01ea3bd778571083441d7db23783e3ddb54e2f80c695065`. Assembly receipt SHA256 `f7f54e6445e210be5fa50d0e93756d41a6498d9aaf090319c978c763f5fb15a7`; artifact receipt SHA256 `2948c0a7e96c13542f8d07a9059b0b0b7d835efe15ee16be63121090e3678ac9`. All52 packed files match frozen assembly; all four public JS/declaration entries present, one shared ownership chunk and no default execution export.

GAT-owned additive compatibility/execution-c1157f7e/manifest.json maps25 source/build inputs and17exact scenario files plus a bounded four-line headless verifier hook. Source scenario is verification/execution-snapshot/scenario/, target snapshots/session/gat-durable-execution. Old installer, SOURCE_SNAPSHOT and compatibility/dsh-0.1.5-rc.2 remain outside this task and existing dirty edits were preserved. No live profile mutation or main DSH source edits performed.

## Executed validation and independent review

- Final production:81 PASS/five files; current execution/assertion-free service type conformance PASS (production-attempt-03).
- Existing direct:48 PASS/five specs and compatible type graph PASS (direct attempt09/build02).
- Fresh forced direct/current graph compiles and one joint tsdown PASS (assembly-final-01).
- Plain Node old/current supported entries, same public WK identity, packed named Loader selected read/no eager/system-memory:PASS; Loader1case.
- Packed current strict/full-library declaration consumer PASS; direct strict consumer PASS with existing Host skipLibCheck:true.
- Existing shipped headless CLI source and final built replay each1owningcase PASS/139unrelatedskipped (snapshot13/14); unchanged replay inputs/sidecars and recorded source/dependency hashes.
- Actual Astra source/design/artifact review closes SR01/SR02/SR03. Sol owns independently qualified reviewer/package lanes, Luna audits direct evidence and additive machine maps; author does not invent approvals.

Detailed evidence: [test-matrix.md](test-matrix.md), [source-review.md](source-review.md), [source-design-consistency.md](source-design-consistency.md), verification/final-consistency.json and unique lane receipts. Final metadata/design/source/distribution consistency is independently accepted at STEP-06 in source-review.md; finalization records scoped lint/ASC and capture disposition separately.

## Limits and activation

Aggregate Host TypeScript is NG130 unrelated generated remote/client seams; focused plugin graphs and necessary runtime dependencies pass. Direct full library diagnostic finds existing duplicated Schemastery TS6200; source consumer passes under that Host's supported policy. Legacy ./src/* wildcard advertises unshipped sources; README identifies workspace-development use. Mocked transport/keyless replay do not certify live model quality, operator provenance, arbitrary prompt/tool topology or OS crash/lock recovery.

[deployment-proposal.md](deployment-proposal.md) contains exact final artifact, proposed task-only canonical workspace/provider/model/fresh roster/config, actual storage/log effects and rollback. Proposed YAML passes final public Config schema (verification/deployment-config-validation.json). Operator topology/storage and concrete reviewer authorized-input/receipt/ACL/audit workflow remain activation requirements. No activation, mission dispatch, reset, memory promotion, publication or commit/push performed.

Final STEP-06 source/artifact/design/source-map/distribution review accepted. STEP-07 ASC was regenerated/read fresh after transition. Final capture sweep covers all step findings, diffs and exact receipts:14 captures, zero relation candidates, no new uncaptured item. HUMAN explicitly instructed moving all14 captures to backlog for later review; governed close completed the transfer without promotion. AIP status is done. Backlog IDs BL-024-CAP-024-01 through BL-024-CAP-024-14 preserve content and source refs, with zero captures awaiting disposition in this workspace. Strict scoped lint and git diff whitespace checks pass; final governed-close/backlog/ASC status is retained in verification receipts.

The disposable /tmp qualification Hosts are unavailable on the resumed turn. Original executed and independently reviewed runtime/pin evidence is retained; no fresh runtime verification is claimed after their removal. The persistent final tarball was rechecked:all52 files equal frozen assembly, exact tar hash retained. Root source/scenario and three historical metadata objects also rechecked. Reproducing the build requires recreating the two pinned disposable checkouts with the recorded dependency graph.
