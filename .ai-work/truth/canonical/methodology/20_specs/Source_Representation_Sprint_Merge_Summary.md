# Source Representation / Conversion Integration Sprint Merge Summary

Version: v0.9.15  
Date: 2026-04-26  
Status: Canonical merge summary  
Baseline: AI Work System MVP v0.9.14  
Update scope: Source Representation / Conversion Integration Minimal Sprint

---

## 1. Purpose

This document records how the Source Representation / Conversion Integration Minimal Sprint is reflected into the canonical AI Work System package.

---

## 2. Sprint outputs integrated

The sprint adds MVP coverage for:
- Source Representation Scope
- AIWS-readable Source Artifact Rule
- Representation Artifact Model
- Representation Quality Status Model
- Limitation Handling / HUMAN Check / Re-conversion Flow
- Source Verification Boundary
- Runtime Routing: Queue vs Capture Inbox
- Tool / Skill Patch Map
- Migration / Backward Compatibility
- Canonical Merge Map

---

## 3. Key decisions

1. AIWS runtime reads AIWS-readable representation.
2. AI does not automatically read raw non-text original.
3. Representation status controls verification strength.
4. Representation limitation must be handled explicitly.
5. AI can only verify what is present in the AIWS-readable representation, unless HUMAN verifies the original.
6. Blocking representation issues route to Runtime Queue.
7. Non-blocking reusable improvement candidates route to Capture Inbox.
8. Tools expose representation boundary; they do not implement full conversion automation.
9. Migration does not imply verification.

---

## 4. Implementation patches applied in v0.9.15

Applied:
- `build_wiki_source_meta.py` supports representation/original/conversion metadata fields.
- `lint_wiki.py` checks raw/non-text locator risks and representation locator hints.
- `lookup_wiki_source.py` surfaces representation/original/conversion fields and clearer next actions.
- `refresh_wiki_source_meta.py` preserves representation/conversion fields.
- `build_wiki_source_index.py` projects lightweight representation fields.
- `evaluate_wiki_source_impact.py` adds verification level/boundary fields.
- `detect_changed_wiki_sources.py` surfaces original/representation locator hints.
- related skills updated with v0.9.15 SRI guidance.
- HUMAN check, re-conversion request, and migration report templates added.

Not applied:
- full source conversion framework
- OCR/table/diagram extraction
- automated conversion pipeline
- raw binary runtime reading
- full conversion certification workflow

---

## 5. Delta tracking

Sprint delta materials are preserved under:

```text
payload/methodology/90_delta_tracking/source_representation_conversion_integration_sprint_2026-04-26/
```
