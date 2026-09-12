# Wiki Meta / Index Minimal Spec Sprint Merge Summary

Version: v0.9.8  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.7  
Update scope: Wiki Meta / Index Minimal Spec Sprint

---

## 1. Purpose

This document records how the Wiki Meta / Index Minimal Spec Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:

- current Wiki Source Meta / Wiki Source Index mechanism
- preservation of v0.9.2 field names and tooling
- runtime lookup flow
- source artifact representation rule
- source_representation_quality_issue
- source_id / Knowledge Targets / Lookup Keys rules
- build/update/rebuild/verify flow
- Source-Specific Hints / Change Impact Hints / Cautions semantics
- optional enrichment boundary
- relation to Controlled Knowledge Promotion
- current-compatible sample meta records
- canonical merge map

---

## 3. Key decisions

1. Keep current Wiki Source Meta / Wiki Source Index mechanism.
2. Preserve good existing field names.
3. Use meta first, then source artifact when needed.
4. `artifact_locator` points to AIWS-readable source representation.
5. Markdown/source representation must be sufficient for AI runtime understanding.
6. If representation is insufficient, mark `source_representation_quality_issue`.
7. Use existing sections before adding new fields.
8. Small meta fixes are lightweight maintenance.
9. Authority/meaning/broad changes use Controlled Knowledge Promotion.
10. Do not change index schema/tooling in this sprint.

---

## 4. Deferred

- index schema change
- build/lookup script change
- mandatory new fields
- full metadata registry
- graph DB / ontology
- automatic migration
- automated validation/lint
- scoring/telemetry
- full SeedPath integration
- direct AI reading of original non-text raw files

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/wiki_meta_index_minimal_spec_sprint_2026-04-26/
```
