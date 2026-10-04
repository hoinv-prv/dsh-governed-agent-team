# BS1 — Current navigation

Use the categorized `current/` directory for browsing instead of scanning root-level compatibility files. `current/README.md` explains each category; this page remains the concise status index.

## Authoritative live state

| Purpose | File | Status |
|---|---|---|
| Mission summary | `mission.md` | Current narrative |
| Selected plan | `wbs.v58.json` | Approved; SHA `88259c82c30914a17e7d2dff05f6187c7313724e82d128a8748a4d50e5c8b52e` |
| Execution | `execution.json` | `waiting_for_human`; SHA `9cf2b60b674a9b3a9500f73439e8fd74886e2d929303eb2981bb2518733c78cb` |
| Decisions | `decisions.json` | Current decision ledger |
| Progress data | `progress.json` | Current stopped-v58 projection |
| Progress view | `progress.html` | Current stopped-v58 report |

## Current analysis and handoff

- `HANDOFF-PAUSED-R59-RECOVERY-DESIGN.md` — exact pause/resume instructions.
- `mission-rca-v58-stalled-critical-path.md` — mission-level RCA and recovery analysis.
- `mission-rca-v58-stalled-critical-path.review.json` — RCA review record.
- `CROSS-WORKSPACE-ISSUES-FINDINGS-LESSONS.md` — transferable issue/lesson package.
- `CROSS-WORKSPACE-ISSUES-FINDINGS-LESSONS.review.json` — independent review record.

## Reviewed candidate — awaiting exact HUMAN approval

The following revision-59 files are reviewed planning artifacts, not approved execution authority:

- `wbs.v59.json`
- `command-effects.v59.json`
- `execution-migration.v59.json`
- `execution-preview.v59.json`
- `wbs.v59.order.json`
- `task-v59-*.json`

The handoff describes the earlier paused snapshot. Its settlement and semantic-preflight blockers are now repaired. Exact candidate SHA is `49f7a941fc0f5f0220982feaef3e99863c2ae3cc780c3a046899e39cf32a40f1`; final independent review is `pass_with_notes`. HUMAN approval of these exact bytes and effects is still required before migration or execution.

## Historical backup and root cleanup

- `history/README.md` — backup/relocation policy and directory descriptions.
- `history/root-archive-manifest.json` — exact mapping and SHA-256 for 309 root-level files moved out of the active view.
- `history/root-archive/` — relocated non-current root files.
- `history/backup-manifest.json` — earlier copy-only snapshot of 173 WBS/lookback/RCA/progress artifacts.
- `history/wbs-revisions-v1-v57/` — old WBS revisions and companions.
- `history/lookback-lookup-rca/` — lookback/lookup/RCA copies.
- `history/progress-snapshot-v58-stopped/` — stopped progress snapshot.

Authoritative current files now live under categorized `current/` folders. Their original root names are compatibility symlinks required by approved WBS/runtime paths. Future HUMAN-review HTML must be written under `current/` as specified by `current/README.md`. Structured subdirectories were not changed. If a historical verifier requires an archived original path, restore the exact hash-matching file using `history/root-archive-manifest.json`; do not edit the archived copy.
