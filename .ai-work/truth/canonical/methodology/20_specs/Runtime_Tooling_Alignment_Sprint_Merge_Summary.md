# Runtime Tooling Alignment Sprint Merge Summary

Version: v0.9.12  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.11  
Update scope: Runtime Tooling Alignment Sprint

---

## 1. Purpose

This document records how the Runtime Tooling Alignment Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:

- runtime tooling alignment scope
- tool/spec compatibility matrix
- Runtime Queue / Capture Inbox tooling alignment
- aiws-aip run Runtime Status Alignment
- aiws-lint / lint-workspace / lint-wiki Alignment
- Workspace Template Alignment
- Migration / Backward Compatibility Rules
- general version-up rename rule
- Wiki Tooling Boundary / Future Split Decision
- Minimal Implementation Plan / Patch Map
- Canonical Merge Map

---

## 3. Key decisions

1. Runtime Tooling Alignment makes existing tools/templates align with latest canonical specs.
2. Preserve baseline compatibility.
3. Avoid unnecessary redesign.
4. `02_investigation_queue.jsonl` is renamed to `02_runtime_queue.jsonl` on version-up.
5. Old queue file remains readable as legacy alias / migration source.
6. aiws-aip run prepares/points runtime context and exposes status/readiness; it is not semantic executor.
7. lint/check is deterministic guardrail, not reviewer.
8. Deep Wiki Tooling Alignment is future sprint scope.

---

## 4. Implementation patches applied in v0.9.12

Applied:
- workspace template now uses `02_runtime_queue.jsonl`
- `02_investigation_queue.jsonl` removed from new template
- `00_task_brief.md` documents runtime artifacts
- `init_workspace.py` ensures new workspace uses `02_runtime_queue.jsonl`
- `lint_workspace.py` supports new + legacy queue files
- `lint_workspace.py` supports legacy + new queue schemas
- `lint_workspace.py` extends Capture Inbox types/status/targets
- `lint_all.py` delegates workspace lint to aligned `lint_workspace_dir`
- `run_aip.py status` shows Runtime Queue and Capture Inbox visibility

Not applied:
- deep Wiki tooling implementation
- full Active Step Context redesign
- full CI/testing harness
- semantic lint

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/runtime_tooling_alignment_sprint_2026-04-26/
```
