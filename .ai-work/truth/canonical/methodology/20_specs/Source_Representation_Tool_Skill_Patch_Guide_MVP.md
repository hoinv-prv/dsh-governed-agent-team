# Source Representation Tool / Skill Patch Guide MVP

Status: Canonical implementation guide  
Version: v0.9.15  
Date: 2026-04-26  
Source: SRI-08 Tool / Skill Patch Map

---

## Purpose

This guide records the minimal patch map for Source Representation / Conversion Integration.

The package v0.9.15 applies P0 and part of P1:
- build_wiki_source_meta.py representation fields
- lint_wiki.py representation locator checks
- lookup_wiki_source.py representation boundary
- refresh_wiki_source_meta.py representation field preservation
- evaluate_wiki_source_impact.py representation verification fields
- detect_changed_wiki_sources.py representation/original locator hints
- build_wiki_source_index.py lightweight representation projection fields
- skill guidance updates

---

# AIWS_SRI-08_TOOL_SKILL_PATCH_MAP_v1

Status: Draft  
Sprint: Source Representation / Conversion Integration Minimal Sprint  
Baseline: AI Work System MVP v0.9.14

---

## 1. Purpose

SRI-08 defines the minimal tool/skill patch map for Source Representation / Conversion Integration.

This is a planning document for canonical merge / optional implementation package update.

---

## 2. Implementation stance

```text
Patch minimally.
Do not build full conversion framework.
Do not make AI read raw binary/non-text directly.
```

---

## 3. Target tools

Primary target tools:

```text
build_wiki_source_meta.py
refresh_wiki_source_meta.py
lint_wiki.py
lookup_wiki_source.py
evaluate_wiki_source_impact.py
detect_changed_wiki_sources.py
```

Related tools:

```text
build_wiki_source_index.py
run_aip.py status
lint_workspace.py
```

Target skills:

```text
aiws-wiki build-meta
aiws-wiki refresh-meta
aiws-wiki lookup
aiws-lint
aiws-aip run
```

---

## 4. P0 patch candidates

### P0-01. build_wiki_source_meta.py representation fields

Patch:
- support original_source_locator
- support representation_locator
- support representation_type
- support conversion_method
- support conversion_date
- support conversion_limitations
- support source_scope / representation_scope
- preserve artifact_locator as AIWS-readable representation locator

---

### P0-02. lint_wiki.py representation locator checks

Patch:
- warn if artifact_locator appears to point to non-AI-readable raw file
- warn if original_source_locator exists but representation_locator/artifact_locator missing
- warn if source_representation_status missing for converted/non-text source
- warn if partial/failed/needs_review lacks caution
- warn if quality_issue true but review_required/candidate missing

---

### P0-03. lookup_wiki_source.py representation boundary

Patch:
- show representation status/caution
- show recommended next action:
  - open_source_for_evidence
  - check_representation_quality
  - request_human_check
  - request_reconversion
- avoid full verification wording when representation status is incomplete

---

### P0-04. refresh_wiki_source_meta.py preservation

Patch:
- preserve original/representation locators
- preserve conversion metadata
- preserve limitations
- do not overwrite caution unless explicitly updated
- if representation status worsens, review_required true

---

## 5. P1 patch candidates

### P1-01. evaluate_wiki_source_impact.py representation impact mapping

Patch:
- partial/needs_review/failed/unknown + high-impact source => high/unknown impact
- output source_representation_issue candidate
- blocking_current_task if current task requires evidence

### P1-02. detect_changed_wiki_sources.py representation staleness

Patch:
- detect representation file missing
- detect original changed but representation not updated if timestamps/hash available
- output requires_impact_evaluation true

### P1-03. run_aip.py status visibility

Patch:
- optionally show blocking source_representation_check queue items
- no full representation workflow

### P1-04. skill guidance updates

Patch skills with:
- AIWS-readable representation rule
- no raw binary runtime reading assumption
- source verification boundary
- HUMAN check/re-conversion request flow

---

## 6. P2 / future

Defer:
- conversion CLI tool
- OCR integration
- table/diagram extraction
- conversion quality scoring
- representation certification
- source repository integration
- UI/form for re-conversion requests

---

## 7. Compatibility test checklist

After implementation, test:

```markdown
- [ ] old meta without representation fields remains warning-compatible
- [ ] new meta can include original_source_locator / representation_locator
- [ ] artifact_locator points to AIWS-readable representation
- [ ] partial/unknown status shows caution in lookup
- [ ] lint warns for raw binary artifact_locator
- [ ] refresh preserves representation fields
- [ ] impact evaluation treats representation issue as review/blocker when needed
```

---

## 8. Conclusion

SRI-08 defines minimal tool/skill patch map.

Central decision:

```text
Tools should make representation boundary visible,
not implement full conversion automation.
```

Next: SRI-09 Migration / Backward Compatibility.
