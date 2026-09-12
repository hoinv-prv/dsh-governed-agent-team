# Source Representation / Conversion Integration Spec MVP

Status: Canonical MVP spec  
Version: v0.9.15  
Date: 2026-04-26  
Source sprint: Source Representation / Conversion Integration Minimal Sprint

---

## 1. Purpose

This spec defines minimal source representation / conversion integration for AIWS MVP.

The goal is to ensure AI can use source artifacts safely when original files are non-text or difficult to read directly.

---

## 2. Central stance

```text
AIWS uses explicit AI-readable source representations for runtime verification,
and representation limitations are handled visibly instead of hidden.
```

---

## 3. Core rules

### 3.1. Runtime reads AIWS-readable representation

```text
AIWS runtime reads AIWS-readable representation.
AI does not automatically read raw non-text original.
```

### 3.2. Verification is limited to what AI reads

```text
AI can only verify what is present in the AIWS-readable representation,
unless HUMAN verifies the original.
```

### 3.3. Quality/status controls verification strength

```text
Representation status tells AI how safely it can use the AIWS-readable source artifact for verification.
```

### 3.4. Limitation must be handled explicitly

```text
Representation limitation must lead to caveat, HUMAN check, re-conversion request,
or blocking route depending task impact.
```

### 3.5. Runtime routing

```text
Representation issues that block current source verification go to Runtime Queue;
non-blocking reusable improvement candidates go to Capture Inbox.
```

---

## 4. AIWS-readable source artifact rule

For runtime use:

```text
artifact_locator should point to AIWS-readable source artifact.
```

Recommended locator semantics:

```yaml
artifact_locator: <AIWS-readable runtime source artifact>
original_source_locator: <raw/original file reference>
representation_locator: <converted/prepared AI-readable representation>
```

In many cases:

```text
artifact_locator == representation_locator
```

MVP default representation format:

```text
Markdown (.md)
```

Other acceptable text/structured formats:
- `.txt`
- `.json`
- `.jsonl`
- `.csv`
- `.yml`
- `.yaml`

---

## 5. Representation artifact model

Recommended fields:

```yaml
source_id:
title:
source_type:
artifact_locator:
original_source_locator:
representation_locator:
representation_type:
conversion_method:
conversion_date:
converted_by:
source_scope:
representation_scope:
source_representation_status:
source_representation_caution:
source_representation_quality_issue:
conversion_limitations:
last_representation_reviewed_at:
review_required:
```

Minimum recommended set:

```yaml
artifact_locator:
source_representation_status:
source_representation_caution:
source_representation_quality_issue:
```

---

## 6. Representation quality/status model

Recommended values:

```text
complete
partial
needs_review
failed
unknown
not_applicable
```

Quick meaning:
- `complete`: enough content for intended scope
- `partial`: representation covers only part or may omit important details
- `needs_review`: representation exists but requires HUMAN/conversion check
- `failed`: not usable for source verification
- `unknown`: quality not assessed
- `not_applicable`: original source is already AIWS-readable

---

## 7. Verification levels

Recommended verification levels:

```text
not_verified
route_identified
meta_reviewed
representation_reviewed
source_verified_with_caveat
source_verified
human_verified_original
```

Boundary:
- Wiki Source Index = route only
- Wiki Source Meta = orientation/routing
- AIWS-readable representation = evidence if sufficient
- original raw source = HUMAN/raw check required if not AI-readable

---

## 8. Limitation handling flow

```text
Representation limitation detected
  ↓
Does current task need the missing/uncertain content?
  ├─ no  → continue with caveat / capture future candidate if useful
  └─ yes
       ↓
Is HUMAN/original check available?
       ├─ yes → request HUMAN check
       └─ no
            ↓
Can re-conversion solve it?
            ├─ yes → request re-conversion
            └─ no  → block or proceed only with explicit limitation acceptance
```

---

## 9. Runtime routing

Runtime Queue is used when representation issue blocks current source verification.

Capture Inbox is used when the issue is reusable/future-value but not currently blocking.

---

## 10. Migration compatibility

Old artifacts remain readable.

Safe defaults for old artifacts:

```yaml
source_representation_status: unknown
source_representation_caution: "Representation quality has not been reviewed."
source_representation_quality_issue: unknown
review_required: true
```

Migration does not imply verification.

---

## 11. Tool alignment summary

| Tool | SRI alignment |
|---|---|
| build_wiki_source_meta.py | supports representation/original/conversion fields |
| lint_wiki.py | warns about raw/non-text runtime locators and missing representation fields |
| lookup_wiki_source.py | surfaces representation status/caution and recommended next action |
| refresh_wiki_source_meta.py | preserves representation/conversion fields |
| evaluate_wiki_source_impact.py | maps representation issues to review/blocking decisions |
| detect_changed_wiki_sources.py | surfaces representation/original locator hints |
| run_aip.py status | future optional visibility for source_representation_check queue items |

---

## 12. Non-goals

This spec does not define:
- full source conversion framework
- OCR/table/diagram extraction algorithm
- automated conversion pipeline
- raw binary runtime reading by AI
- full conversion certification workflow
- full CI/testing harness
- semantic completeness scoring

---

## 13. Conclusion

Source Representation / Conversion Integration ensures AIWS can use raw/non-text sources through explicit AI-readable representations while preserving verification safety.

---

# v0.9.16 Active Step Context addendum

When a step output uses source evidence, Step Output Meta should record:

```yaml
source_refs:
  - source_id:
    locator:
    verification_level:
    limitation:
```

ASC can expose these requirements, but persisted Step Output Meta stores the trace.
