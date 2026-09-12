# Wiki Source Maintenance / Impact Detection Sprint Merge Summary

Version: v0.9.14  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.13  
Update scope: Wiki Source Maintenance / Impact Detection Sprint

---

## 1. Purpose

This document records how the Wiki Source Maintenance / Impact Detection Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:
- Source Maintenance Scope
- Changed Source Detection Flow
- Impact Evaluation Result Model
- Candidate Routing: Runtime Queue vs Capture Inbox
- Refresh Draft / Review / Apply Flow
- Update Log / Rollback Trace
- Source Representation Issue Handling
- Minimal Tool Patch Map
- Migration / Backward Compatibility
- Canonical Merge Map

---

## 3. Key decisions

1. Source change detection is signal.
2. Impact evaluation is recommendation.
3. Refresh is draft by default.
4. Apply is explicit and logged.
5. Promotion is controlled separately.
6. Current-task blocking maintenance routes to Runtime Queue.
7. Future-value non-blocking maintenance routes to Capture Inbox.
8. Applied Wiki maintenance updates must be traceable and reasonably reversible.
9. Source representation issues can block source verification and must be routed visibly.
10. WSM migration is additive and warning-compatible.

---

## 4. Implementation patches applied in v0.9.14

Applied:
- `detect_changed_wiki_sources.py` now emits WSM result records.
- `evaluate_wiki_source_impact.py` now emits WSM impact model fields.
- `refresh_wiki_source_meta.py` now writes maintenance log entries for draft/apply and rollback hint for apply.
- `build_wiki_source_index.py` now writes index rebuild maintenance log.
- `lint_wiki.py` now lints maintenance log and maintenance status hints.
- related skills updated with v0.9.14 WSM guidance.
- `Wiki_Maintenance_Log_Template.jsonl` added.

Not applied:
- full maintenance orchestrator command
- full metadata registry
- semantic impact scoring
- auto-update
- auto-promotion
- full source conversion framework

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/wiki_source_maintenance_impact_detection_sprint_2026-04-26/
```
