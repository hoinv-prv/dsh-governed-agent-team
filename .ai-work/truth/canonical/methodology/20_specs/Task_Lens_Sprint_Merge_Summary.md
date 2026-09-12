# Task Lens Sprint Canonical Merge Summary

Version: v0.9.6  
Date: 2026-04-25  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.5  
Update scope: Task Lens Minimal Spec Sprint

---

## 1. Purpose

This document records how the Task Lens Minimal Spec Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint output integrated

The sprint adds canonical MVP coverage for:

- Task Lens concept and purpose
- Task Lens ownership and boundary
- minimal runtime flow
- starter lens examples
- selection / confirmation / HUMAN adjustment / expansion / No-Lens rules
- relation to Wiki Meta / Index and Knowledge Hub
- relation to AIP Template and Working AIP
- canonical merge map
- sprint close review

---

## 3. Canonical decisions

1. Task Lens is an optional runtime viewpoint for task → knowledge routing.
2. Task Lens selection requires intent-first handling.
3. Explicit Task Lens is not mandatory for every task.
4. No-Lens / AI-decides-search-scope is a valid MVP option.
5. HUMAN may adjust runtime lens after AI proposes it.
6. AI may expand/adjust lens when the current lens is too narrow.
7. Task Lens must not become a hard scope limiter.
8. Task Lens may influence/suggest AIP Template but does not replace it.
9. Task Lens may feed Working AIP context but does not replace it.
10. Wiki Meta / Index and Knowledge Hub are accessed through lens-guided or intent-guided routing.
11. Raw/source verification remains required when exactness/evidence/freshness matters.

---

## 4. Deferred

The following remain deferred:

- full lens catalog
- lens registry
- lens scoring/ranking
- lens orchestration
- automatic lens selection
- telemetry
- UI selector
- mandatory related_lenses metadata
- mandatory Working AIP Task Lens field
- lens testing/scoring framework

---

## 5. Delta tracking

Sprint delta materials are preserved under:

`payload/methodology/90_delta_tracking/task_lens_sprint_2026-04-25/`

They are tracking/audit artifacts and not a parallel canonical design set.
