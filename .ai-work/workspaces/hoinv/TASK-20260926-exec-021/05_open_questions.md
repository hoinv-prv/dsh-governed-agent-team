# Open Points — TASK-20260926-exec-021 GAT baseline sync and contract freeze

## Metadata
| Field | Value |
|---|---|
| Task ID | `TASK-20260926-exec-021` |
| Workspace | `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/` |
| AIP source | `.ai-work/aip/hoinv/exec/AIP-EXEC-021-gat-baseline-sync-contract-freeze.md` |
| Maintainer | AI + HUMAN (`hoinv`) |
| Created | 2026-09-26 |
| Last updated | 2026-09-26 |

## Index
| ID | Status | Severity | Raised at | Summary |
|---|---|---|---|---|
| OP-TASK-20260926-exec-021-01 | resolved | 🟡 Major | 2026-09-26 | Select baseline authority and sync direction |
| OP-TASK-20260926-exec-021-02 | resolved | 🟡 Major | 2026-09-26 | Classify DSH-only versus portable GAT deltas |
| OP-TASK-20260926-exec-021-03 | resolved | 🔵 Minor | 2026-09-26 | Final attachment bounds and event migration choice |

## OP-TASK-20260926-exec-021-01 — Baseline authority
- **Status:** resolved
- **Severity:** 🟡 Major
- **Context:** Gate U1

### Conclusion
The HUMAN selected the current DSH experimental GAT as behavioral baseline. The standalone repository becomes authoring/distribution source after controlled synchronization.

## OP-TASK-20260926-exec-021-02 — Delta portability
- **Status:** resolved
- **Severity:** 🟡 Major
- **Context:** STEP-01 inventory

### Question / Issue
Which DSH experimental GAT differences are portable package baseline and which depend on host-only paths, package names, generated outputs, or private APIs?

### Assumption in use
Adopt only deltas backed by source/test behavior that can be represented in the standalone distribution; preserve/document host-only differences.

### Conclusion
Portable baseline: simpleMode, bounded YAML roster loading, route preflight/AgentOptions, Session-keyed installation, enable/profile behavior, immediate-authorized mission plus compatible replay, and navigation type cast. Merge rather than copy where standalone has newer approved-plan import, Team-exclusive delegation, mission APIs and tests. Exclude generated `lib/**`, caches, host-layout paths, and the internally inconsistent DSH Web contract removal.

## OP-TASK-20260926-exec-021-03 — Attachment bounds and event migration
- **Status:** resolved
- **Severity:** 🔵 Minor
- **Context:** Contract freeze

### Question / Issue
What exact member-attachment count/byte/depth limits and v2→v3 event migration form should EXEC-B implement?

### Conclusion
The HUMAN selected required-only V1 attachments; `team/member` event v3 with an explicit adjacent v2 adapter; and the conservative preset: 8 records/member, 65,536 UTF-8 bytes/record, 262,144 bytes/member, JSON depth 16, 4,096 nodes, 16,384 UTF-8 bytes/string, and binder ids capped at 64 ASCII lower-kebab characters. The HUMAN also selected canonical task-board authority with `missionId`, host-attested HUMAN mission admission bound to exactly one current mission revision, and capability-metadata external-delegation denial with a name fallback.
