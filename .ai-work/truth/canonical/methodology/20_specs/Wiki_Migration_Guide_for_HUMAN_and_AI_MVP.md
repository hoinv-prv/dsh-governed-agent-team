# Wiki Migration Guide for HUMAN and AI MVP

Status: Canonical migration guide  
Version: v0.9.13  
Date: 2026-04-26  
Source: WTA-11 Wiki Migration Guide for HUMAN and AI

---

# AIWS_WTA-11_WIKI_MIGRATION_GUIDE_FOR_HUMAN_AND_AI_v1

Status: Draft  
Sprint: Wiki Tooling Alignment Sprint  
Baseline: AI Work System MVP v0.9.12

---

## 1. Purpose

This guide explains how a HUMAN user, or an AI working under HUMAN instruction, can migrate / upgrade an existing AIWS Wiki / Knowledge Hub to align with the latest Wiki Tooling Alignment design.

The goal is to support practical version-up without requiring full automation.

This guide is for:

- HUMAN who wants to manually check and upgrade Wiki artifacts
- HUMAN who wants to ask AI to perform the migration
- AI that needs a safe step-by-step migration flow
- project maintainers who need compatibility with old v0.9.2-style Wiki tools/artifacts

---

## 2. Core migration stance

```text
Upgrade Wiki artifacts safely.
Preserve existing knowledge.
Do not auto-promote.
Do not treat migration as approval.
```

Important:

```text
Migration makes Wiki artifacts compatible with the latest design.
Migration does not automatically make old/candidate/draft knowledge approved.
```

---

## 3. What “Wiki migration” means

Wiki migration may include:

- checking existing Wiki Source Meta files
- checking Wiki Source Index files
- adding new optional metadata fields
- checking source artifact locators
- checking AIWS-readable source representation quality
- updating lookup/search triggers
- creating refresh drafts
- creating Wiki update candidates
- rebuilding source index
- recording migration notes/logs

Migration does **not** automatically mean:

- approving new knowledge
- promoting candidate content
- changing source of truth
- overwriting curated Wiki Meta without review
- claiming source verification if source artifact was not read
- silently fixing source representation quality issues

---

## 4. HUMAN migration options

HUMAN can choose one of three migration levels.

### Level 1 — Compatibility check only

Purpose:

```text
Check whether existing Wiki artifacts are still readable and safe to use.
```

Actions:
- run/read lint_wiki result
- check missing required fields
- check broken locators
- check index/meta consistency
- record warnings

No content update.

Recommended when:
- project is stable
- no immediate Wiki update needed
- HUMAN only wants to know risk level

---

### Level 2 — Metadata alignment

Purpose:

```text
Add or update latest recommended metadata fields without changing source meaning.
```

Actions:
- add missing optional fields with safe values such as `unknown`, `draft`, `needs_review`
- add source representation status/caution if known
- add authority/freshness/promotion status
- add Knowledge Value / intended AI use if clear
- update search triggers / aliases if safe
- rebuild index projection after review

Recommended when:
- old Wiki works but lacks latest routing/quality fields
- HUMAN wants AI to search/use Wiki more safely
- no major source content change happened

---

### Level 3 — Review + refresh + controlled update

Purpose:

```text
Refresh Wiki Source Meta based on changed source artifacts and apply updates after review.
```

Actions:
- detect changed sources
- evaluate impact
- create refresh draft
- compare old vs new meta
- review high-impact changes
- apply approved updates
- log change/rollback trace
- create Capture Inbox / promotion candidates when needed

Recommended when:
- source artifacts changed
- existing meta/index may be stale
- source representation quality changed
- Knowledge Hub content needs controlled update

---

## 5. Migration prerequisites

Before migration, HUMAN/AI should identify:

```markdown
- [ ] AIWS package/version currently used
- [ ] Wiki root directory
- [ ] Wiki Source Meta directory
- [ ] Wiki Source Index file
- [ ] source artifact directory
- [ ] whether source artifacts are AIWS-readable markdown or converted from raw non-text files
- [ ] whether existing Wiki content is source_of_truth, curated_reference, working_reference, or candidate
- [ ] whether migration should be check-only, metadata alignment, or controlled update
```

---

## 6. Recommended migration flow

### Step 1 — Inventory existing Wiki artifacts

Check:

```markdown
- [ ] Wiki Source Meta files
- [ ] Wiki Source Index files
- [ ] source artifacts
- [ ] refresh drafts if any
- [ ] change snapshots if any
- [ ] local knowledge overview if any
```

Output:

```text
Wiki Migration Inventory
```

---

### Step 2 — Classify artifact status

For each Wiki artifact, classify:

```text
source_of_truth
curated_reference
working_reference
history_reference
candidate
draft
unknown
```

If unclear, use:

```text
unknown
```

Do not guess approval status.

---

### Step 3 — Check locators

Check:

```markdown
- [ ] meta_locator exists in index
- [ ] artifact_locator exists in meta/index
- [ ] artifact_locator points to AIWS-readable source artifact
- [ ] raw non-text file is not used as runtime source artifact locator
- [ ] source scope is clear
```

If locator is missing/broken:

```text
create wiki_meta_update_candidate or migration issue
```

---

### Step 4 — Check source representation quality

For each source artifact, check whether it is:

```text
AIWS-readable text/markdown
converted from PDF/Word/Excel/image/binary
unknown
```

Add or update fields:

```yaml
source_representation_status:
source_representation_caution:
source_representation_quality_issue:
```

Safe default if unknown:

```yaml
source_representation_status: unknown
source_representation_caution: "Representation quality has not been reviewed."
source_representation_quality_issue: false
```

If known incomplete:

```yaml
source_representation_status: partial
source_representation_quality_issue: true
```

---

### Step 5 — Add authority/freshness/promotion hints

Recommended fields:

```yaml
authority_level:
freshness_status:
last_reviewed_at:
source_updated_at:
promotion_status:
maintenance_status:
review_required:
```

Safe defaults:

```yaml
authority_level: unknown
freshness_status: unknown
promotion_status: draft
maintenance_status: needs_review
review_required: true
```

For existing approved/curated content, HUMAN should confirm before marking:

```yaml
promotion_status: approved
authority_level: source_of_truth
```

---

### Step 6 — Add Knowledge Value / intended AI use

Recommended fields:

```yaml
knowledge_value:
intended_ai_use:
reuse_scenarios:
```

Examples:

```yaml
knowledge_value: "Helps AI route to the correct source when reviewing requirement/design consistency."
intended_ai_use: "source routing, source verification, review viewpoint selection"
reuse_scenarios:
  - "review design against requirement"
  - "find source evidence for requirement branch"
```

If not clear:

```yaml
knowledge_value: "unknown"
intended_ai_use: "unknown"
```

Do not hallucinate value.

---

### Step 7 — Check search triggers / aliases

Check:

```markdown
- [ ] search_triggers exist
- [ ] aliases exist if HUMAN/project uses alternate names
- [ ] related_keywords exist where useful
- [ ] related_sources exist where useful
```

If AI had difficulty finding a source, add candidate:

```text
wiki_meta_update_candidate: missing alias/search trigger
```

Do not update canonical meta without review.

---

### Step 8 — Rebuild / refresh index as projection

After metadata alignment, rebuild Wiki Source Index if needed.

Rule:

```text
Index is projection.
Index should not embed full meta or full source body.
```

Index should include lightweight fields such as:

```yaml
source_id:
title:
source_type:
status:
meta_locator:
artifact_locator:
summary_short:
search_triggers:
tags:
authority_level:
freshness_status:
source_representation_status:
```

---

### Step 9 — Detect changed sources and evaluate impact

If source snapshots exist, run/check:

```text
detect_changed_wiki_sources.py
evaluate_wiki_source_impact.py
```

Interpretation:

```text
change detection = signal
impact evaluation = recommendation
neither = approval
```

If impact is medium/high/unknown:

```text
create review/update candidate
```

---

### Step 10 — Create refresh draft, not direct update

When refreshing meta:

```text
refresh draft first
apply explicitly only after review
```

Recommended flow:

```text
old meta
  ↓
refresh draft
  ↓
compare
  ↓
review
  ↓
apply if approved
  ↓
log change / rollback trace
```

---

### Step 11 — Apply only after review

Before applying Wiki update, check:

```markdown
- [ ] HUMAN or approved process reviewed the change
- [ ] source locator is valid
- [ ] source representation quality is acceptable or limitation is stated
- [ ] Knowledge Value is clear enough
- [ ] promotion/authority status is correct
- [ ] change summary exists
- [ ] rollback hint exists
```

If not, keep as draft/candidate.

---

### Step 12 — Log migration / rollback trace

Record:

```yaml
migration_id:
date:
performed_by:
target_artifact:
old_state:
new_state:
change_summary:
reason:
review_status:
rollback_hint:
```

For MVP, this can be:
- migration report
- package report
- maintenance log
- delta tracking file

---

## 7. How HUMAN can ask AI to perform migration

HUMAN can use prompts like:

### Check-only migration prompt

```text
Hãy kiểm tra Wiki hiện tại theo AIWS Wiki Tooling Alignment mới nhất.
Chỉ list vấn đề và migration candidates, không sửa file.
Ưu tiên kiểm tra Wiki Meta, Wiki Index, artifact_locator, source_representation_status,
promotion_status, knowledge_value, và lookup boundary.
```

### Metadata alignment prompt

```text
Hãy tạo draft migration để bổ sung metadata còn thiếu cho Wiki Meta theo design mới nhất.
Không apply trực tiếp.
Không promote candidate.
Output gồm: file cần sửa, field đề xuất thêm, lý do, risk, và patch draft.
```

### Controlled update prompt

```text
Hãy refresh Wiki Source Meta cho các source đã thay đổi.
Tạo refresh draft trước, so sánh old/new, đánh dấu impact level,
và tạo candidate/update log. Không apply nếu chưa có confirm.
```

### Apply after review prompt

```text
Tôi đã review các refresh draft sau và approve.
Hãy apply các thay đổi đã approve, cập nhật index nếu cần,
ghi migration log/change summary/rollback hint.
Không thay đổi các draft chưa được approve.
```

---

## 8. AI migration guardrails

When AI performs migration, AI must follow:

```text
Do not auto-promote.
Do not auto-update approved Wiki content without explicit instruction.
Do not claim source verification unless source artifact was read.
Do not hide source representation quality issue.
Do not infer missing source content.
Do not overwrite without backup/change log.
```

AI should:
- create migration plan first
- show affected files
- create draft changes
- ask for HUMAN review when high-impact
- keep old artifacts readable
- log migration actions

---

## 9. Migration output template

Recommended output:

```markdown
# Wiki Migration Report

## 1. Migration scope
...

## 2. Current Wiki inventory
...

## 3. Compatibility findings
...

## 4. Proposed metadata additions
...

## 5. Source representation issues
...

## 6. Lookup/index issues
...

## 7. Refresh/update candidates
...

## 8. High-impact items requiring HUMAN review
...

## 9. Applied changes
...

## 10. Deferred items
...

## 11. Rollback hints
...
```

---

## 10. Migration checklist

```markdown
# Wiki Migration Checklist

## Preparation
- [ ] Current package/version identified
- [ ] Wiki root identified
- [ ] Source meta/index/source artifact locations identified
- [ ] Migration level selected: check-only / metadata alignment / controlled update

## Compatibility
- [ ] Old meta files readable
- [ ] Old index readable
- [ ] Required locators checked
- [ ] Missing new fields reported as warning/info, not immediate failure

## Source representation
- [ ] AIWS-readable artifact locator checked
- [ ] Non-text converted sources identified
- [ ] source_representation_status added/checked
- [ ] source_representation_quality_issue captured where needed

## Authority / promotion
- [ ] authority_level checked
- [ ] promotion_status checked
- [ ] candidate/draft not treated as approved
- [ ] review_required marked where needed

## Knowledge Value
- [ ] knowledge_value checked
- [ ] intended_ai_use checked
- [ ] reuse_scenarios checked or left unknown safely

## Lookup / index
- [ ] search_triggers checked
- [ ] aliases checked
- [ ] index rebuilt if approved
- [ ] index remains lightweight

## Refresh / update
- [ ] changed sources detected
- [ ] impact evaluated
- [ ] refresh draft created
- [ ] high-impact changes reviewed
- [ ] approved changes applied explicitly

## Logging
- [ ] change summary recorded
- [ ] rollback hint recorded
- [ ] migration report created
```

---

## 11. Recommended migration sequence by risk

### Low-risk migration

```text
check only
  → add missing optional fields as unknown/draft
  → rebuild index projection
```

### Medium-risk migration

```text
metadata alignment
  → refresh draft
  → HUMAN review
  → apply selected changes
```

### High-risk migration

```text
source changed / authority changes / source representation issue
  → impact evaluation
  → candidate flow
  → HUMAN review
  → controlled apply/log
```

---

## 12. Relationship to tools

This guide can be supported by tools:

| Tool | Migration role |
|---|---|
| `lookup_wiki_source.py` | find candidate source/meta routes |
| `lint_wiki.py` | detect structure/boundary issues |
| `build_wiki_source_meta.py` | generate new/aligned meta draft |
| `build_wiki_source_index.py` | rebuild lightweight index projection |
| `refresh_wiki_source_meta.py` | create refresh draft / apply explicitly |
| `detect_changed_wiki_sources.py` | identify changed source artifacts |
| `evaluate_wiki_source_impact.py` | recommend review/update candidate |
| Capture Inbox | store future-value migration candidates |
| Runtime Queue | store current-task migration actions |

---

## 13. Common migration mistakes

### Mistake 1 — Treating migration as approval

Bad:

```text
Migrated meta = approved Knowledge Hub entry
```

Correct:

```text
Migration compatibility does not equal promotion approval.
```

### Mistake 2 — Auto-overwriting curated meta

Bad:

```text
refresh source meta → overwrite existing curated meta
```

Correct:

```text
refresh source meta → create draft → review → apply explicitly
```

### Mistake 3 — Hiding representation limitation

Bad:

```text
converted Excel/PDF incomplete but no caution
```

Correct:

```text
record source_representation_quality_issue or caution
```

### Mistake 4 — Index becomes source body

Bad:

```text
index stores full source or full meta body
```

Correct:

```text
index remains lightweight projection
```

### Mistake 5 — AI guesses missing values

Bad:

```text
AI invents authority_level / knowledge_value / representation completeness
```

Correct:

```text
use unknown / needs_review / draft if not supported
```

---

## 14. Conclusion

Wiki migration should help existing Wiki artifacts become compatible with the latest AIWS design.

Central rule:

```text
Migration aligns structure and metadata.
Promotion/approval still requires controlled review.
Source verification still requires reading source artifact.
```

This guide allows HUMAN to self-migrate or instruct AI to migrate safely without breaking the Knowledge Hub governance boundary.

---

# v0.9.14 Wiki Source Maintenance addendum

During Wiki migration, source maintenance model can be introduced additively.

Rules:
- old artifacts remain readable/warning-compatible
- migration does not equal approval
- refresh drafts are not applied automatically
- applied Wiki maintenance updates should be logged with rollback hint
- source representation issues should be captured or routed

---

# v0.9.15 Source Representation migration addendum

When migrating old Wiki artifacts:
- keep old artifacts readable
- do not assume representation completeness
- add safe defaults such as `source_representation_status: unknown`
- split raw file locator into `original_source_locator` and AI-readable `representation_locator` when possible
- migration does not imply source verification
