# Wiki Tooling Alignment Patch Guide MVP

Status: Canonical implementation guide  
Version: v0.9.13  
Date: 2026-04-26  
Source: WTA-10 Minimal Patch Map / Canonical Merge Map

---

## Purpose

This guide records the minimal patch map for Wiki Tooling Alignment.

The package v0.9.13 applies P0 and part of P1:
- lookup output boundary
- lint_wiki boundary checks
- refresh no-auto-promotion wording
- build_wiki_source_meta optional field support
- build_wiki_source_index lightweight projection fields
- detect/evaluate candidate/signal output fields
- Wiki skills alignment

---

# AIWS_WTA-10_MINIMAL_PATCH_MAP_AND_CANONICAL_MERGE_MAP_v1

Status: Draft  
Sprint: Wiki Tooling Alignment Sprint  
Baseline: AI Work System MVP v0.9.12

---

## 1. Purpose

WTA-10 defines a minimal patch map and canonical merge map for Wiki Tooling Alignment Sprint.

This prepares future canonical merge / package update.

---

## 2. Implementation stance

```text
Patch minimally.
Preserve compatibility.
Avoid full Knowledge Hub rewrite.
No auto-promotion.
```

---

## 3. Patch priority

Recommended priorities:

```text
P0 — must align before next Wiki tooling package update if possible
P1 — should align soon
P2 — future sprint candidate
```

---

## 4. P0 patch candidates

### P0-01. lookup_wiki_source.py output boundary

Patch:
- label results as candidate route/context
- include recommended_next_action where possible
- avoid verified/confirmed wording
- surface meta_locator/artifact_locator
- surface source_representation_status/caution if present

Target:
```text
payload/tooling/lookup_wiki_source.py
payload/skills/aiws-wiki/SKILL.md
```

---

### P0-02. lint_wiki.py minimal boundary checks

Patch:
- recognize new optional fields
- warn for missing authority/source representation/promotion fields
- check artifact_locator exists
- check index/meta bloat
- warn candidate/promotion ambiguity
- keep old meta readable

Target:
```text
payload/tooling/lint_wiki.py
```

---

### P0-03. aiws-wiki refresh-meta no-auto-promotion wording

Patch:
- ensure default is draft/review
- apply is explicit
- high-impact update requires review/candidate/log
- output should not imply promotion

Target:
```text
payload/tooling/refresh_wiki_source_meta.py
payload/skills/aiws-wiki/SKILL.md
```

---

### P0-04. build_wiki_source_meta.py field support

Patch:
- allow/add optional fields:
  - authority_level
  - freshness_status
  - source_representation_status
  - source_representation_caution
  - knowledge_value
  - intended_ai_use
  - promotion_status
- use safe unknown/draft placeholders when not inferable
- do not hallucinate values

Target:
```text
payload/tooling/build_wiki_source_meta.py
payload/skills/aiws-wiki/SKILL.md
```

---

## 5. P1 patch candidates

### P1-01. build_wiki_source_index.py lightweight projection

Patch:
- project new lightweight fields if available
- keep index small
- avoid full meta/source body

Target:
```text
payload/tooling/build_wiki_source_index.py
```

---

### P1-02. detect/evaluate candidate flow output

Patch:
- use impact_level / recommendation / candidate_type / next_action
- avoid approval wording
- optionally emit Capture Inbox candidate snippet

Targets:
```text
payload/tooling/detect_changed_wiki_sources.py
payload/tooling/evaluate_wiki_source_impact.py
```

---

### P1-03. skills alignment

Patch:
- update `aiws-wiki lookup`
- update `aiws-wiki refresh-meta`
- update `aiws-wiki build-meta`
- add no-auto-promotion and source verification wording

---

## 6. P2 / future candidates

### P2-01. Full Wiki Tooling Alignment implementation

Could be done if current sprint only merges design.

### P2-02. Wiki Source Maintenance / Impact Detection Sprint

Dedicated flow:
- detect changed source
- evaluate impact
- create candidate
- refresh draft
- review/apply
- log/rollback

### P2-03. Source Representation / Conversion Integration Sprint

Dedicated source conversion/representation quality sprint.

### P2-04. Code Source Profile Sprint

For `build_java_wiki_metas.py`, Graphify/call graph, language-specific source profiles.

### P2-05. Local/Common Knowledge Integration Sprint

For `aiws-wiki add-local-knowledge`, local knowledge overview, common/project boundary.

---

## 7. Compatibility test checklist

After patching, test:

### Old meta/index

```markdown
- [ ] old meta loads
- [ ] old index loads
- [ ] missing new optional fields produce warning/info, not hard error
```

### New meta/index

```markdown
- [ ] new optional fields accepted
- [ ] source representation fields accepted
- [ ] promotion status fields accepted
- [ ] index stays lightweight
```

### Lookup

```markdown
- [ ] lookup output says candidate route/context
- [ ] exact evidence still points to source artifact
- [ ] representation caution displayed if present
```

### Refresh/apply

```markdown
- [ ] default creates draft
- [ ] apply is explicit
- [ ] high-impact changes require review/log
- [ ] no auto-promotion wording
```

### Impact

```markdown
- [ ] impact result is signal/recommendation
- [ ] candidate flow is suggested, not applied
- [ ] no approval wording
```

---

## 8. Canonical merge targets

Recommended canonical additions:

```text
Wiki_Tooling_Alignment_Spec_MVP.md
Wiki_Tooling_Alignment_Patch_Guide_MVP.md
Wiki_Tooling_Alignment_Sprint_Merge_Summary.md
```

Recommended canonical updates:
- `WIKI_META_INDEX_SPEC.md`
- `Knowledge_Routing_Spec_MVP.md`
- `Controlled_Knowledge_Promotion_Spec_MVP.md`
- `Source_Understanding_Artifact_Spec_MVP.md`
- `Minimal_Runtime_Testing_Stance_Spec_MVP.md`
- `Runtime_Tooling_Alignment_Spec_MVP.md`
- Wiki skills:
  - aiws-wiki lookup
  - aiws-wiki build-meta
  - aiws-wiki refresh-meta
  - aiws-wiki add-local-knowledge if relevant
- changelog / manifest / baseline note

---

## 9. WTA item to canonical destination map

| WTA | Main merge destination | Merge type |
|---|---|---|
| WTA-01 Scope | Wiki Tooling Alignment Spec | body |
| WTA-02 Compatibility Matrix | Wiki Tooling Alignment Spec | body |
| WTA-03 Meta/Index Schema | WIKI_META_INDEX_SPEC / WTA Spec | body |
| WTA-04 lookup Runtime Alignment | Knowledge Routing / lookup skill | body |
| WTA-05 refresh Draft/Apply | Controlled Promotion / refresh skill | body |
| WTA-06 Impact Candidate Flow | Controlled Promotion / WTA Spec | body |
| WTA-07 Source Representation | Source Understanding / Wiki Meta spec | body |
| WTA-08 lint_wiki Alignment | WTA Patch Guide / MRT | body |
| WTA-09 Migration Rules | WTA Spec | body |
| WTA-10 Patch/Merge Map | delta tracking | delta |

---

## 10. Core snippets to merge

### Wiki tooling central stance

```markdown
Wiki tools help AI route, refresh, detect changes, and check structure.
They do not approve knowledge, replace source verification, or auto-promote candidates.
```

### Lookup boundary

```markdown
aiws-wiki lookup is a routing tool.
It helps AI find candidate source/meta routes.
It does not replace source artifact verification.
```

### Refresh boundary

```markdown
Refresh creates draft/update candidate by default.
Apply is explicit, reviewed, logged, and rollback-aware.
Refresh is not promotion.
```

### Impact boundary

```markdown
Detect/evaluate tools produce signals and candidates.
They do not approve or apply Knowledge Hub updates.
```

### Representation quality

```markdown
Wiki tools should surface source representation quality/caution so AI can avoid overclaiming source verification.
```

---

## 11. Deferred items

Do not merge as current commitment:
- full Knowledge Hub governance rewrite
- full metadata registry framework
- semantic scoring
- auto-promotion
- auto-update Knowledge Hub
- Graphify/call graph integration
- full code profile framework
- full CI/testing harness
- full source conversion framework

---

## 12. Sprint close readiness check

Before close, confirm:

```markdown
- [ ] WTA scope accepted
- [ ] compatibility matrix accepted
- [ ] Meta/Index schema alignment accepted
- [ ] lookup boundary accepted
- [ ] refresh draft/apply boundary accepted
- [ ] detect/evaluate candidate flow accepted
- [ ] source representation quality integration accepted
- [ ] lint_wiki alignment accepted
- [ ] migration/compatibility rules accepted
- [ ] patch/merge map accepted
```

---

## 13. Conclusion

WTA-10 prepares canonical merge and future patching for Wiki Tooling Alignment.

Central merge message:

```text
Wiki tools support AI runtime routing and maintenance,
but they do not replace source verification, approval, or Controlled Knowledge Promotion.
```
