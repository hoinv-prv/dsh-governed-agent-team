# GUIDE_ADD_WORKING_AND_LEGACY_SOURCES_TO_PROJECT_WIKI_MVP
Version: 0.1  
Status: Practical guide  
Scope: MVP only

---

# 1. Purpose

Tài liệu này hướng dẫn cách đưa:
- `source working`
- `source legacy`

vào wiki của một dự án phần mềm trong AI Work System MVP.

Mục tiêu:
- giữ cùng một model cho cả hai loại source
- cho AI dùng đúng ưu tiên
- tạo được lookup / compare / maintenance flow hợp lý
- không cần redesign project wiki

---

# 2. Core principle

Do **not** turn source working or source legacy directly into curated wiki.

Instead, put both into the source-side layer:
- `Wiki Source Artifact`
- `Wiki Source Meta`
- `Wiki Source Index`
- `Source Interpretation Profile`

The difference is:
- `source_role`
- `source_use_rule`
- relation semantics
- reading priority

---

# 3. Step-by-step onboarding

# Step 1 — Identify your two source sets

## Working source
Examples:
- current implementation repo
- active design docs
- current schema docs
- current generated normalized notes

## Legacy source
Examples:
- old repo snapshot
- previous generation design docs
- old batch programs
- migrated-but-kept source
- archived schema/docs still useful for comparison

---

# Step 2 — Register them as Wiki Source Artifacts

For each source or source bundle, register it as source-side input.

## For working source artifacts
Recommended:
- `source_role: working`
- `source_use_rule: primary_for_current_work`

## For legacy source artifacts
Recommended:
- `source_role: legacy`
- `source_use_rule: reference_only`
or
- `source_use_rule: compare_when_needed`

---

# Step 3 — Build Wiki Source Meta

For each important artifact or source bundle, create source meta that is:
- small
- memory-friendly
- useful for relevance confirmation

## Working source meta should emphasize
- current implementation area
- current identifiers
- current module/function anchors
- current code/doc scope

## Legacy source meta should emphasize
- what older generation it belongs to
- what it helps compare
- what current source it is related to
- what caution applies if used for current behavior inference

---

# Step 4 — Build Wiki Source Index

Create index entries as projections of metas.

Each index entry should expose enough to:
- grep by exact identifiers
- confirm whether the source is relevant
- know whether it is working or legacy
- jump to the source meta
- jump to the source artifact

Recommended at minimum:
- `source_id`
- `title`
- `source_type`
- `artifact_locator`
- `meta_locator`
- `profile_id`
- `source_role`
- `source_use_rule`
- `summary_short`
- `knowledge_targets`
- `status`

---

# Step 5 — Add working/legacy relations

Where useful, link working and legacy source objects.

Recommended relation types:
- `legacy_of`
- `working_successor_of`
- `compare_with`
- `same_function_different_generation`
- `migration_related`

These relations help AI:
- prefer working first
- open legacy only when comparison is useful
- understand lineage

---

# Step 6 — Use the correct reading order in practice

## For current implementation work
AI should prefer:
1. Truth
2. Working source-side objects
3. Curated wiki
4. Legacy source-side objects when needed
5. History

## For migration / comparison / reverse-engineering tasks
AI may read:
1. Truth
2. Working source-side objects
3. Legacy source-side objects
4. Curated wiki
5. History

The task context determines how much legacy should move upward.

---

# 4. How to treat source working in wiki

## Source working should be included
Yes, strongly recommended.

## But not as direct curated wiki
Working source should feed:
- source meta
- source index
- wiki candidate/update drafts

It should remain source-side, not become official wiki automatically.

## Why
Because source working is usually the best source for:
- current behavior
- impact analysis
- exact identifiers
- maintenance work

---

# 5. How to treat source legacy in wiki

## Source legacy should also be included
Yes, but mainly as:
- compare source
- historical reference
- migration support
- terminology/rationale support

## Legacy should not be default current truth
Use it cautiously.
Prefer working source for current implementation unless the task explicitly requires legacy-centered analysis.

---

# 6. Practical examples

## Example A — Current bug fix in working system
Use:
- working source first
- working source meta/index first
- legacy only if current source behavior is unclear or if regression history matters

## Example B — Migration analysis
Use:
- working + legacy side by side
- relation mapping between generations
- compare-oriented notes and candidates

## Example C — Build function wiki
Use:
- working source as main evidence
- legacy source as optional compare/reference
- mention compare findings only when useful

---

# 7. Recommended project organization

A project may physically organize source artifacts like:
- `sources/working/...`
- `sources/legacy/...`

This is optional but useful.

Regardless of physical layout, keep the same source-side model and let role/use-rule do the conceptual work.

---

# 8. Common mistakes to avoid

- treating legacy source as default current truth
- copying working source directly into curated wiki
- mixing working and legacy without role markers
- forgetting relation semantics between generations
- skipping source meta and index for large source sets

---

# 9. Minimal rollout checklist

- [ ] register working source artifacts
- [ ] register legacy source artifacts
- [ ] assign `source_role`
- [ ] assign `source_use_rule`
- [ ] build source metas
- [ ] build source index
- [ ] add working/legacy relations where useful
- [ ] teach LLM/guide to prefer working source for current work
- [ ] teach compare workflows when legacy is needed

---

# 10. Conclusion

For MVP project wiki:
- include both working and legacy source
- keep them in the same source-side framework
- distinguish them by role and use-rule
- prefer working source for current work
- use legacy as reference/comparison source
- keep curated wiki downstream from source-side processing, not a direct dump of source sets
