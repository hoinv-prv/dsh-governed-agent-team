# Findings — AIP-EXEC-021

## STEP-00 — Confirmed task understanding

### Confirmed direction
- On 2026-09-26 the HUMAN explicitly confirmed: use the current DSH experimental GAT as the behavioral baseline and continue.
- Standalone `dsh-governed-agent-team` becomes the authoring/distribution source after controlled synchronization.
- This EXEC includes baseline synchronization, contract freeze, and compatibility verification only.

### Preservation constraints
- The standalone repository already contains extensive modified and untracked work. No reset, stash, cleanup, blanket directory copy, or unexplained overwrite is authorized.
- Every modified target file must be read in both repositories and classified before editing.
- DSH checkout is reference-only; no upstream DSH source change is in scope.

### Output boundary
- Adopt proven current-baseline package/test/profile behavior.
- Create `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` for later EXEC-B/EXEC-C.
- Do not implement binder registry, durable attachments, two-phase continuation lifecycle, Durable Agent integration, or mission lifecycle changes.

### Source authority
1. Current executable DSH/standalone source and tests for implemented behavior.
2. Approved installer compatibility specification for installation safety.
3. Maintained GAT design reference for navigation/status labels.
4. AIP-PLAN-001 recommendation for target sequencing.

## STEP-01 — Pinned baselines and classified delta inventory

### Exact baseline identifiers
- Standalone: commit `6a8e4f62a30e05cf1e36950d74245b707f5394fe`, branch `main`, with extensive pre-existing modified/untracked GAT work.
- DSH: commit `aeedf19995babaa28e35ca84624baff18a77a7d8`, branch `hoinv`, with the relevant GAT baseline itself modified/untracked.
- Consequence: the DSH commit alone is not the behavioral revision. Selected DSH file hashes are pinned in `dsh-baseline-sha256.txt`.

### File-level action matrix
| Area | Action | Preservation rule |
|---|---|---|
| `packages/core/src/types.ts`, `roster.ts` | merge DSH Agent route and `workspace` source | retain standalone approved-plan result/API |
| `packages/core/src/mission-board.ts`, `projection.ts`, `mission-plan.ts` | adopt DSH immediate-authorized mission + legacy replay + safety guard | retain mission approval API for legacy/future draft revisions |
| `packages/core/src/index.ts`, `journal.ts`, `task-board.ts`, `approved-plan-import.ts` | preserve standalone | retain atomic approved-plan import and 11-method Remote surface |
| core tests/docs | merge | add route/enable/authorized-mission coverage; retain approved-plan coverage |
| `packages/tools/src/team-config.ts` and tests | adopt DSH as new files | strict bounded regular-file parsing and fallback diagnostics |
| `packages/tools/src/index.ts` | merge | add simpleMode/routes/YAML/Session-key install; preserve Team-exclusive external-delegation guard and legacy non-simple approval |
| tools dependencies/TS refs | adopt DSH | add `yaml`, `dsh-llm`, LLM/subagent TS refs |
| `packages/profile/cordis.patch.yml` | adopt DSH config | default `simpleMode: true`, bounded manifest bytes |
| profile tests | merge DSH enable/YAML behavior | preserve Team-exclusive behavior and newer standalone assertions |
| `packages/web/src/client/mount.ts` | merge | add focused-build navigation cast; retain approved-plan/mission injections |
| `packages/web/src/client/locales.ts` | merge DSH copy/source labels | retain standalone approval error key used by current UI |
| Web tests | merge | retain standalone enable-flow and mission/import API coverage |
| READMEs | defer unless required by actual merged behavior | do not generate translation checksum manually |
| `lib/**`, `node_modules/**`, Vite results | ignore as generated/cache | rebuild, never copy from DSH |

### HUMAN resolutions during STEP-01
- Preserve Team-exclusive execution after enable: external `subagent`, `subagent_fork`, `workflow`, and `ralph` remain denied; missing capability uses HUMAN-approved member addition.
- Adopt DSH simpleMode mission-as-authorization for the default profile; retain legacy Team-plan approval behavior when `simpleMode: false`.

### Known baseline defects not to copy
- DSH gat-web mount removes injected mission/plan functions that its unchanged component interface still requires.
- DSH tests drop required `enabled`/`enable` fixtures in one component surface.
- DSH generated outputs are not authoritative and do not include standalone's newer Remote import method.

### Approved execution split
- `task-1` / `senior-dev`: `packages/core/**`.
- `task-2` / `dev`: `packages/tools/**`, `packages/profile/**`.
- `task-3` / `junior-dev`: `packages/web/**`.
- `task-4` / `advisor`: read-only member-binding contract review.

## STEP-02 — Controlled synchronization outcome

### Applied package behavior
- Core now forwards optional `AgentOptions`, exposes `workspace` enable provenance, creates revision-1 approved missions for the selected baseline, accepts both legacy draft and new approved replay, and keeps approved-plan import/atomic journal/11 Remote methods.
- Tools/profile now support default `simpleMode`, bounded workspace YAML, full-route preflight before provisioning, per-member provider/model/reasoning effort, Session-keyed scoped installation and default profile limits.
- HUMAN-confirmed Team-exclusive denial remains in force after enable, and legacy `simpleMode: false` continues to enforce exact Team-plan approval.
- Web baseline deltas were already present in the standalone committed source. The merge deliberately retained mission/import injections rather than copy DSH's inconsistent removal.
- The built-lib smoke now resolves artifacts relative to its package so it no longer silently skips solely because the standalone path is not `packages/experimental/gat-core`.

### Distribution synchronization
- Compatibility payload was regenerated and now includes `team-config.ts` plus its test.
- The supported-target lockfile was normalized after discovering that structural installer verification alone allowed new `yaml`/`dsh-llm` package specifiers to be absent.
- Installer source drift remains advisory by approved design; destination preimages, installed bytes, and structural checks remain strict.

## STEP-03 — Contract freeze outcome

The HUMAN froze:
- required-only attachment V1;
- member event v3 with explicit adjacent v2 adapter;
- 8 attachments/member, 65,536 bytes/record, 262,144 bytes/member, depth 16, 4,096 nodes, 16,384 bytes/string, binder id ≤64 lower-kebab characters;
- canonical task-board authority with `missionId`;
- host-attested HUMAN admission bound to exactly one current Team/mission/revision;
- capability-metadata external-delegation denial with a compatibility name fallback.

Independent advisor review found and the contract resolved:
- persist-only quarantined inbox versus the sole activate/wake gate;
- cleanup ownership for prepared leases;
- one bounded cancellation/deadline contract for settle/release;
- exact reserved-handle states/errors and post-active live-retry versus new-generation recovery;
- RFC 8785 byte/depth/node conventions plus payload digest;
- distinct recovery of already-persisted child inbox and Team mailbox delivery;
- exact mission execution lease carrier, exhaustive exemptions, and wake-boundary revalidation;
- EXEC-B fake-only orchestration until EXEC-C production lifecycle lands.

Final advisor pass reported no blocking or major findings. The normative document is `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`; its post-sync package manifest is `post-sync-package-sha256.txt`.

## STEP-04 — Verification evidence

### Passing evidence
- Isolated DSH-shaped core run: 4 files / 96 tests; typecheck; emit; package build.
- Isolated DSH-shaped tools run: 2 files / 29 tests.
- Clean supported DSH clone installation: 85 files, `structuralVerification: PASS`.
- Clean supported clone frozen dependency install: lockfile accepted and 1,263 packages linked offline.
- Full installed package suite: 10 files / 150 tests passed, covering core, persistence, tools, YAML loader, profile, Web, and Web profile.
- Installer Node suite: 11/11 tests passed.
- Full supported-target verifier: PASS after native/unit verification, full host/client/Web build, built-lib E2E, opt-in Team browser E2E, final structural status, zero secret findings, and zero paths outside the allowlist.

### Expected/non-product failures investigated
- Direct standalone Vitest/build commands cannot resolve DSH root configs; verification moved to isolated DSH-shaped staging rather than adding fake standalone configs.
- The first clean-clone test attempt lacked the native `system.node` helper; after supplying the same host helper used by DSH, all 150 tests passed.
- The selected current DSH commit `aeedf...` is not the released installer compatibility target and its dirty live install record does not match this installer. Compatibility verification therefore used the manifest's supported clean commit `c291e796...`; the live DSH checkout remained unmodified.

### Verification defects found and repaired
- The compatibility generator now carries the new `yaml` and `dsh-llm` importer rows while preserving live workspace links needed by post-install profile-scaffold builds.
- The verifier now builds the DSH native system helper before running GAT unit tests.
- The installed Web overlay now matches the synchronized simple-mode profile, and the browser verification explicitly enables the opt-in Team before asserting mission/member content.

## Final Capture Sweep
- Reviewed the complete diff, package/installer failures, contract reviews, verification logs, findings, and outputs.
- Added three final reusable tooling candidates: lockfile live-link preservation (`CAP-021-05`), native-helper verifier ordering (`CAP-021-06`), and explicit opt-in browser verification (`CAP-021-07`).
- Total capture inbox entries before disposition: 7.
- Pending relation candidates (`candidate_kind: artifact_relation_update`): 0.
- No candidate was promoted. Close-time disposition is defer-to-account-backlog for later HUMAN curation.
