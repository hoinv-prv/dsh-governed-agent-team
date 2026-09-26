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
| OP-TASK-20260926-exec-021-03 | deferred | 🔵 Minor | 2026-09-26 | Final attachment bounds and event migration choice |

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
- **Status:** deferred
- **Severity:** 🔵 Minor
- **Context:** Contract freeze

### Question / Issue
What exact member-attachment count/byte/depth limits and v2→v3 event migration form should EXEC-B implement?

### Conclusion
Defer final numeric/schema choice to HUMAN review after the contract document presents evidence-backed options. This does not block baseline synchronization.
