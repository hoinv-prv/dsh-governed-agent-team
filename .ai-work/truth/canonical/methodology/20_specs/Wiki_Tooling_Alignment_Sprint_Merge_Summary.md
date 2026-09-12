# Wiki Tooling Alignment Sprint Merge Summary

Version: v0.9.13  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.12  
Update scope: Wiki Tooling Alignment Sprint

---

## 1. Purpose

This document records how the Wiki Tooling Alignment Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:
- Wiki Tooling Alignment scope
- Wiki Tool / Spec Compatibility Matrix
- Wiki Meta / Index Schema Alignment
- aiws-wiki lookup Runtime Alignment
- aiws-wiki refresh-meta Draft / Apply Alignment
- detect/evaluate Impact Candidate Flow
- Source Representation Quality Integration
- lint_wiki Alignment
- Migration / Compatibility Rules
- Minimal Patch Map / Canonical Merge Map
- Wiki Migration Guide for HUMAN and AI

---

## 3. Key decisions

1. Wiki tools support AI runtime routing and maintenance, but do not replace source verification, approval, or Controlled Knowledge Promotion.
2. aiws-wiki lookup is routing, not evidence verification.
3. Refresh creates draft/update candidate by default; apply is explicit.
4. Detect/evaluate tools produce signals and candidates, not approval.
5. Source representation quality must be visible.
6. lint_wiki is deterministic guardrail, not semantic reviewer.
7. New Wiki artifacts align; old Wiki artifacts remain warning-compatible.
8. Migration aligns structure/metadata, not approval.

---

## 4. Implementation patches applied in v0.9.13

Applied:
- `lookup_wiki_source.py` now outputs routing boundary and next action.
- `build_wiki_source_meta.py` supports authority/freshness/representation/value/promotion fields.
- `build_wiki_source_index.py` projects new lightweight alignment fields.
- `refresh_wiki_source_meta.py` preserves alignment fields and labels draft refresh as not approved.
- `detect_changed_wiki_sources.py` outputs signal boundary and recommended next action.
- `evaluate_wiki_source_impact.py` outputs impact level, candidate type, target, next action, and signal boundary.
- `lint_wiki.py` checks new optional fields, representation status, promotion trace, index projection bloat, and unsafe recommendations.
- Wiki skills updated with v0.9.13 alignment rules.

Not applied:
- full Knowledge Hub governance rewrite
- full metadata registry
- full code source profile framework
- Graphify/call graph integration
- full source conversion framework
- auto-promotion

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/wiki_tooling_alignment_sprint_2026-04-26/
```
