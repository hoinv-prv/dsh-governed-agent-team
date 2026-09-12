# Controlled Knowledge Promotion Sprint Merge Summary

Version: v0.9.7  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.6  
Update scope: Controlled Knowledge Promotion Minimal Spec Sprint

---

## 1. Purpose

This document records how the Controlled Knowledge Promotion Minimal Spec Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:

- Controlled Knowledge Promotion concept and purpose
- Knowledge Value definition
- AI-first Knowledge Hub purpose
- Notebook / Candidate / Wiki boundary
- Knowledge Promotion Candidate definition/lifecycle/status
- promotion targets and boundaries
- review / source / authority / freshness checks
- No Auto-Promotion rule
- Knowledge Hub Add/Update Checklist
- checklist-of-checklist governance
- Knowledge Hub Add/Update skill concept
- Knowledge Promotion request template
- relation to AIWS components
- HUMAN-triggered lookback command
- Improvement Candidate Collection Pattern
- default lookback step for relevant AIP Templates
- aiws-aip run lookback support
- Knowledge Promotion / Improvement Log & Rollback Trace
- Canonical Merge Map

---

## 3. Key decisions

1. Knowledge Hub is primarily for AI runtime value.
2. HUMAN guides/reviews/controls; AI is primary runtime consumer.
3. Knowledge Value means helping AI work more efficiently and/or produce higher-quality outputs.
4. Notebook can store any.
5. Candidate can be broad and intermediate.
6. Wiki / Knowledge Hub requires Knowledge Value.
7. Important promotion/add/update is controlled.
8. `knowledge-hub-add-update` must use the Knowledge Hub Add/Update Checklist.
9. AI can collect/prepare candidates but must not auto-promote.
10. Post-feedback lookback captures improvement value.
11. `aiws-aip run` should remind/check lookback for relevant AIPs.
12. Important promotion/improvement must be logged for review/revision/rollback.

---

## 4. Deferred items

Deferred to future sprint/phase:

- apply-back workflow
- full metadata/registry framework
- full approval workflow / role matrix
- exact skill implementation
- candidate registry / ID convention
- automated promotion pipeline
- scoring/telemetry
- UI/database
- version-control/rollback automation
- Knowledge Hub lint/health automation

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/controlled_knowledge_promotion_sprint_2026-04-26/
```

These are tracking/audit artifacts and not a parallel canonical design set.
