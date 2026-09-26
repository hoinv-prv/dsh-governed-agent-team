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
