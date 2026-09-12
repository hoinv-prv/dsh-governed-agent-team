# Active Step Context Sprint Merge Summary

Version: v0.9.16  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.15  
Update scope: Active Step Context Minimal Spec Sprint

---

## 1. Purpose

This document records how the Active Step Context Minimal Spec Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:
- Active Step Context scope
- content boundary
- build/refresh/staleness
- Step Output / Decision / Discussion Trace Persistence
- relation to Working AIP
- relation to Workspace Runtime Queue / Capture Inbox
- relation to Wiki lookup / source verification
- tool/skill patch map
- migration/compatibility
- canonical merge map

---

## 3. Key decisions

1. ASC is temporary step-local runtime view.
2. Working AIP remains task/step authority.
3. Workspace persists outputs/decisions/discussion traces.
4. ASC displays current-step slice.
5. Source pointers in ASC are not source verification.
6. Important step outputs must be persisted.
7. HUMAN–AI decisions/conclusions reused later must be persisted.
8. Key discussion process leading to reused decisions must be persisted.
9. Missing legacy trace is not approval or verification.
10. Tools expose ASC/traces but do not become full orchestration engine.

---

## 4. Implementation patches applied in v0.9.16

Applied:
- `build_active_step_context.py` adds current-step traceability/source verification sections.
- `run_aip.py status` shows ASC and traceability summary.
- `lint_workspace.py` lints Step Output Meta and Decision Discussion Trace.
- `lint_all.py` documents aggregated ASC/trace checks.
- templates added for ASC, Step Output Meta, Decision Trace, Step Output Index, and ASC Migration Report.
- related skills/specs updated with ASC and traceability guidance.

Not applied:
- full execution engine
- automatic context optimizer
- automatic step advancement
- UI/form
- automatic output review scoring
- full artifact registry

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/active_step_context_minimal_spec_sprint_2026-04-26/
```
