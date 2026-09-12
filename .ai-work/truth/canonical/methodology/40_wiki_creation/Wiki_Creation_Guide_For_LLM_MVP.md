# Wiki Creation Guide for LLM — AI Work System MVP
Version: 0.2  
Status: Draft baseline  
Scope: MVP only

---

# 1. Purpose

This guide helps an LLM create:
- wiki candidate
- wiki update draft
- wiki-ready structured draft

according to **AI Work System MVP**.

This version is aligned with **Wiki v1.0 freeze**, including:
- `Wiki Source Artifact`
- `Wiki Source Meta`
- `Wiki Source Index`
- `Source Interpretation Profile`

---

# 2. Core rule

When asked to "create wiki", the LLM should normally create:

> **wiki candidate or wiki update draft first**, not silently assume official wiki update.

---

# 3. What the LLM should understand first

## 3.1. Wiki is not Truth
Wiki is a curated/guidance layer for understanding and navigation.
It does not replace Truth.

## 3.2. Source-side flow matters
The LLM should not read raw source blindly if source-side support exists.

Preferred flow:

**Wiki Source Index → Wiki Source Meta → Wiki Source Artifact → Source Interpretation Profile → Wiki Draft/Candidate/Update**

## 3.3. Be conservative
- if unsure between `curated` and `reference` → prefer `reference`
- if unsure between `curated` and `source_of_truth` → prefer `curated`

---

# 4. Reading order for wiki creation

## 4.1. Truth first
Always start from:
1. `.ai-work/truth/SOP_MASTER.md`
2. `.ai-work/truth/AI_WORK_CONTRACT.md`

If the wiki work belongs to a task with AIP:
3. relevant `.ai-work/aip/plans/...` or `.ai-work/aip/exec/...`

## 4.2. Procedural docs
Then read:
5. `.ai-work/procedural/wiki_authoring_guideline.md`
6. `.ai-work/procedural/capture_and_triage_rules.md`
7. `.ai-work/procedural/lint_policy.md`

## 4.3. Source-side lookup before raw source
If `Wiki Source Index` and `Wiki Source Meta` exist, then:
8. read relevant `Wiki Source Index` entries
9. confirm likely relevance
10. read matching `Wiki Source Meta`
11. read relevant `Source Interpretation Profile` if source type guidance is needed
12. only then open the actual `Wiki Source Artifact` when necessary

## 4.4. Existing wiki neighbors
Then read nearby wiki entries:
- domain/function/module/data/pattern/reference neighbors

## 4.5. Workspace findings if relevant
If this wiki work comes from an active task:
- findings
- open questions
- capture inbox
- triage candidates if available

## 4.6. History only if needed
Use History for trail/audit/candidate recall, not as primary truth.

---

# 5. Choosing the target entry type

Choose one:
- `domain`
- `function`
- `module`
- `data`
- `pattern`
- `reference`

Use the same interpretation as in v0.1.

---

# 6. Choosing knowledge class

Usually for LLM-generated wiki drafts in MVP, the target should be:
- `curated`
- or `reference`

Normally avoid directly generating:
- `source_of_truth`
- `history`

unless explicitly intended and governed by a stronger workflow.

Default use-rule mapping:
- `curated` → `verify_when_decision_matters`
- `reference` → `verify_before_use`

---

# 7. Metadata contract

Use YAML metadata at the top.

Recommended baseline:

```yaml
---
artifact_type: wiki_entry
entry_type: function
artifact_id: WIKI-FUNC-001
title: Manufacturing Order Update
knowledge_class: curated
use_rule: verify_when_decision_matters
status: active
canonical_references:
  - truth/canonical/shared_processing_design.md
last_verified_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
---
```

---

# 8. Required wiki sections

Every important wiki draft should include:
- `Purpose`
- `Scope`
- `Canonical References`
- `Recommended Next Reads`

Add type-specific sections as needed.

---

# 9. Source-side interpretation behavior

## 9.1. Index before artifact
If source-side support exists, the LLM should use index/meta before reading source artifacts directly.

## 9.2. Use meta to save context
`Wiki Source Meta` is the preferred small context card.
The LLM should use it to:
- confirm relevance
- understand relation hints
- understand likely knowledge targets
- understand profile mapping
- decide whether deep source reading is needed

## 9.3. Use Source Interpretation Profile when needed
If the source type is non-trivial, the LLM should consult the profile to understand:
- what signals matter
- what to ignore
- what lexical keys matter
- how to map source content into wiki structure
- how to reason about likely impact

## 9.4. Keep exact terms when useful
When drafting wiki, preserve exact identifiers/terms when they matter:
- Japanese business terms
- table names
- program ids
- screen ids
- source symbols

This improves lexical lookup and future grep/usefulness.

---

# 10. Rules when reading raw source / source artifacts

## 10.1. Truth-first, then summarize
Do not summarize from old wiki only and ignore truth/raw source.

## 10.2. Do not over-generalize
If the source only supports a partial understanding, do not write as if the whole system is fully understood.

## 10.3. Mark uncertainty clearly
If evidence is weak or conflicting:
- note it clearly
- use cautious wording
- do not flatten uncertainty

## 10.4. Keep navigation useful
Recommended Next Reads should help AI/humans know what to read next.

---

# 11. Creating new wiki candidate vs update draft

## 11.1. New wiki candidate
Use when:
- no suitable entry exists yet
- source-side material supports a new candidate entry

## 11.2. Wiki update draft
Use when:
- an entry exists
- new evidence/source/meta refresh suggests update

In update draft mode, include:
- what should change
- why
- source refs used
- updated section drafts

## 11.3. Do not apply automatically
LLM should generate:
- candidate
- draft
- proposal

not official apply.

---

# 12. Self-check before finalizing

LLM should verify:
- [ ] Read Truth / procedural docs needed?
- [ ] Chosen correct entry_type?
- [ ] Chosen correct knowledge_class?
- [ ] Used source index/meta first if available?
- [ ] Read source artifact only when needed?
- [ ] Purpose / Scope / Canonical References / Recommended Next Reads present?
- [ ] Not writing as source_of_truth without basis?
- [ ] Not flattening uncertainty?
- [ ] Canonical refs are useful and verifiable?
- [ ] Recommended Next Reads are useful?

---

# 13. Common mistakes to avoid

- using History as truth
- writing curated wiki from one weak note only
- skipping Canonical References
- skipping source-side lookup when available
- turning source meta into official wiki
- auto applying official update

---

# 14. Minimal file set to provide the LLM

## New wiki candidate
At minimum:
- Truth docs
- wiki authoring guideline
- relevant source index/meta if available
- canonical/raw/source files
- nearby wiki entries

## Wiki update draft
At minimum:
- all the above
- existing target wiki entry
- findings/candidates justifying update
- source-side materials that caused the update need

---

# 15. Conclusion

The LLM should create wiki using the following mindset:

**Truth → Procedural Rules → Wiki Source Index → Wiki Source Meta → Wiki Source Artifact → Source Interpretation Profile → Existing Wiki → Candidate/Update Draft**

This keeps wiki creation:
- evidence-based
- cautious
- memory-friendly
- source-aware
- extendable.
