# AIWS Knowledge-Runtime Sprint Canonical Merge Summary

Version: v0.9.3  
Date: 2026-04-25  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.2  
Update scope: Knowledge-runtime sprint integration

> **Historical record — superseded in part (CR-AIWS-2026-05-020, 2026-05-30):** This v0.9.3 summary predates the
> removal of the Knowledge Object layer (CR-AIWS-2026-05-005). Where it mentions "curated knowledge objects" /
> object model, the current canonical model is **2-layer** (artifact meta + index; relationships via
> `## Related Sources`). Body kept as historical record.

---

## 1. Purpose

This document records how the knowledge-runtime sprint outputs are reflected into the canonical AI Work System documents for version v0.9.3.

The sprint focused on:
- runtime knowledge direction
- component boundaries
- Task Lens
- Wiki Meta / Index
- Working AIP connection
- minimal metadata / registry support
- minimal testing stance
- canonical merge tracking

This document does not replace the canonical design/spec documents. It is a merge trace and closeout reference.

---

## 2. Canonical direction confirmed

The following direction is confirmed in this version:

1. **Knowledge Hub** is the reusable knowledge center and standard knowledge access layer.
2. **Wiki Meta / Index** is treated as the runtime-facing structured access layer of Knowledge Hub for the current MVP direction.
3. **Task Lens** is the minimal runtime concept for task → knowledge routing.
4. Runtime access follows **Wiki-first, not Wiki-only**:
   - current context / notebook / active workspace state first
   - Wiki Meta / Index next
   - curated knowledge objects when needed
   - raw/source when verification, detail, conflict, or exact evidence requires it
5. **Working AIP** remains the minimum execution guardrail and is mandatory before meaningful execution.
6. **Workspace** holds active task/session state; it is not the reusable knowledge store.
7. **Skills** are reusable capabilities; they are not decision authority or orchestrator.
8. Runtime improvement must preserve task correctness and working value.

---

## 3. Sprint outputs merged or tracked

### Canonical body / spec updates
The sprint outputs are reflected into the following canonical areas:

- Architecture Design
- Basic Design
- Methodology Design
- Knowledge Routing Spec
- Knowledge Access Interface Spec
- AIP Detail Spec
- Workspace / Queue / Capture Spec
- Specs / Guidelines Index
- Canonical changelog and baseline note

### Delta tracking retained
The sprint BL documents, reference findings, notebook status memo, and incomplete concept memo are preserved under:

`payload/methodology/90_delta_tracking/knowledge_runtime_sprint_2026-04-25/`

This is kept for auditability and future continuation. It is not a parallel canonical design set.

---

## 4. Intentionally deferred items

The following items are intentionally deferred to later sprint/version work:

- Notebook full spec
- Notebook lifecycle / promotion model
- Source-derived reusable understanding artifact canonicalization
- Full metadata / registry framework
- Full testing / scoring / telemetry
- Lens preset catalog / orchestration

These are not blockers for closing this sprint.

---

## 5. Closeout status

The sprint is considered content-close-ready because:

- all backlog-level open points were closed
- BL-01 through BL-10 were drafted
- core principles alignment was checked
- in-scope concepts have minimal MVP coverage
- out-of-scope concepts were explicitly deferred
- canonical merge destinations were identified

---
