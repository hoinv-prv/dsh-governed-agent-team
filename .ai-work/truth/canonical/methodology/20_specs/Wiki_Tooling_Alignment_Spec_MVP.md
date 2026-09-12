# Wiki Tooling Alignment Spec MVP

Status: Canonical MVP spec  
Version: v0.9.13  
Date: 2026-04-26  
Source sprint: Wiki Tooling Alignment Sprint

---

## 1. Purpose

This spec defines Wiki Tooling Alignment for AI Work System MVP.

The goal is to align existing Wiki tools/scripts with the latest AIWS Knowledge Hub / Wiki Meta / Controlled Promotion / source representation specs, while preserving compatibility.

---

## 2. Central stance

```text
Wiki tools support AI runtime routing and maintenance,
but they do not replace source verification, approval, or Controlled Knowledge Promotion.
```

---

## 3. Core principles

### 3.1. AI-first Knowledge Hub purpose

```text
Knowledge Hub is primarily for AI to search, retrieve, route, reason, and verify more effectively.
```

### 3.2. Meta routes, source verifies

```text
Wiki Meta / Index routes.
Source artifact verifies.
```

### 3.3. lookup is routing, not evidence verification

```text
aiws-wiki lookup helps AI find candidate source/meta routes.
It does not prove source evidence.
```

### 3.4. refresh is not promotion

```text
Refresh creates draft/update candidate by default.
Apply is explicit, reviewed, logged, and rollback-aware.
Refresh is not promotion.
```

### 3.5. detect/evaluate impact is signal, not approval

```text
Detect/evaluate tools produce signals and candidates.
They do not approve or apply Knowledge Hub updates.
```

### 3.6. source representation quality must be visible

```text
Wiki tools should surface source representation quality/caution so AI can avoid overclaiming source verification.
```

### 3.7. lint_wiki is deterministic guardrail

```text
lint_wiki checks deterministic structure and boundary risks.
lint_wiki does not judge semantic correctness, source truth, or Knowledge Value quality.
```

### 3.8. migration aligns structure, not approval

```text
Migration makes Wiki artifacts compatible with the latest design.
Migration does not automatically make old/candidate/draft knowledge approved.
```

---

## 4. Wiki Meta / Index schema alignment

Recommended Wiki Source Meta fields include:

```yaml
source_id:
title:
source_type:
status:
artifact_locator:
source_scope:
profile_id:
authority_level:
freshness_status:
source_representation_status:
source_representation_caution:
source_representation_quality_issue:
knowledge_value:
intended_ai_use:
reuse_scenarios:
promotion_status:
maintenance_status:
review_required:
```

Recommended Wiki Source Index projection fields include:

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
promotion_status:
source_representation_status:
```

Rule:

```text
Index is projection.
Meta is orientation/routing.
Source artifact is evidence/detail.
```

---

## 5. Source representation rule

When original source files are non-text, AIWS runtime reads AIWS-readable markdown representation.

`artifact_locator` should point to the AIWS-readable source representation when used at runtime.

If representation is insufficient:

```text
source_representation_quality_issue
```

should be recorded or surfaced.

---

## 6. Controlled Promotion boundary

Candidates, refresh drafts, impact signals, and migration drafts are not approved Knowledge Hub updates.

Promotion or apply-back requires:
- value check
- source/authority check
- review/control check
- update log / rollback trace when applied

---

## 7. Compatibility rule

Old Wiki artifacts should remain readable and warning-compatible where reasonable.

New Wiki artifacts should align with latest schema.

Rule:

```text
New Wiki artifacts align.
Old Wiki artifacts remain readable/warning-compatible.
Migration/update/promotion must be explicit, review-aware, and logged.
```

---

## 8. Tool alignment summary

| Tool | Alignment rule |
|---|---|
| lookup_wiki_source.py | route/context only; not evidence verification |
| build_wiki_source_meta.py | support representation/value/authority/promotion hints |
| build_wiki_source_index.py | project lightweight new fields only |
| refresh_wiki_source_meta.py | draft first; apply explicit; not promotion |
| detect_changed_wiki_sources.py | change signal only |
| evaluate_wiki_source_impact.py | recommendation/candidate only; not approval |
| lint_wiki.py | deterministic structure/boundary checks |
| build_java_wiki_metas.py | future code source profile alignment |

---

## 9. Non-goals

This spec does not define:
- full Knowledge Hub governance rewrite
- full metadata registry framework
- semantic scoring
- auto-promotion
- auto-update Knowledge Hub without review
- Graphify/call graph integration
- full code profile framework
- full source conversion framework
- full CI/testing harness

---

## 10. Conclusion

Wiki Tooling Alignment ensures that Wiki tools help AI use Knowledge Hub safely and effectively without confusing routing, refresh, migration, or impact signals with evidence verification or approval.

---

# v0.9.14 Wiki Source Maintenance addendum

Wiki Tooling Alignment now includes a minimal maintenance flow:

```text
detect changed source
  → evaluate impact
  → route candidate / create refresh draft
  → review
  → apply/log if approved
```

Boundary:
- detection is signal, not approval
- impact evaluation is recommendation, not approval
- refresh is draft by default
- apply is explicit and logged
- promotion is controlled separately

---

# v0.9.15 Source Representation addendum

Wiki tools must expose source representation boundary.

Rules:
- `artifact_locator` should point to AIWS-readable representation for runtime verification
- `original_source_locator` tracks raw/original source
- `representation_locator` tracks converted/prepared representation
- lookup routes; source representation verifies
- tools do not implement full conversion automation

---

# v0.9.16 Active Step Context addendum

ASC may include Wiki/source route pointers, but lookup/Meta pointers are not source verification.

```text
ASC can carry source routes and verification requirements,
but verified evidence still requires reading AIWS-readable source representation.
```

---

# v0.9.17 Wiki Tooling Improvements Addendum — 2026-05-27

**Source:** Applied from wiki_improvement_request.md (validated in vti-ai-work-system-demo, 2026-05-26).

## Slim index schema alignment (supplements §4)

Index projection is now leaner. Fields permanently removed from `index.jsonl` entries:
`meta_id`, `updated_at`, `knowledge_value`, `intended_ai_use`.

`original_source_locator` and `representation_locator` included only when different from `artifact_locator`.

Index generator applies omit-blank: fields with value `""`, `None`, or `[]` are omitted.

Required fields (`source_id`, `title`, `source_type`, `artifact_locator`, `profile_id`,
`summary_short`, `knowledge_targets`, `status`) always present — lint still enforces them.

## Profile vs PMP architecture boundary (supplements §3)

Profile = AIWS canonical, generic-only (`knowledge_targets` + `description`).
PMP = project-specific extraction spec (`format_signature`, `summary_extraction`,
`t1_key_extraction`, `hints_extraction`, `canonical_slot_mapping`).

Tool alignment: `build_wiki_source_meta.py` reads both; PMP takes precedence for extraction.
This preserves profile reusability across projects while PMP carries project-specific knowledge.

## No-match escalation as standard lookup behavior (supplements §3.3)

When `lookup_wiki_source.py` returns 0 results:
- Tool prints a structured fallback hint (retry semantic, raw search, ask HUMAN)
- JSON mode returns `{"matches": [], "raw_fallback_hint": "..."}` instead of empty array
- Skill `aiws-wiki lookup/SKILL.md` enforces a 5-step No-match escalation protocol
- AI must not conclude "not found" without completing the protocol

Boundary: fallback hint is a process signal, not evidence. Source artifact verifies.

## PRE-FLIGHT GATE as standard skill behavior (supplements §3.2)

Skills that consume canonical artifacts (RD/BD/DD/spec) as input enforce a **PRE-FLIGHT GATE**:
wiki lookup must run before any direct file open. Baked into `aiws-aip/operations/create.md` and
`aiws-aip/operations/run.md` as a HARD GATE section.

Forbidden patterns:
- Glob/Grep for artifact files without wiki lookup first
- Inferring peer artifact paths from a user-provided path ("anchor-path" pattern)
- Skipping lookup with rationale "I already know where it is"

Alignment: PRE-FLIGHT GATE is a runtime routing enforcement, consistent with §3.2
(lookup is routing, not evidence verification) and §3.4 (source artifact verifies).
