# WIKI_V1_FREEZE_SUMMARY_MVP
Version: 1.0  
Status: Freeze summary  
Scope: MVP only, but extendable by design

---

# 1. Purpose

Tài liệu này chốt phần **Wiki v1.0** trong **AI Work System MVP**.

Mục tiêu của freeze này là:
- gói khái niệm Wiki trong phạm vi MVP
- nhưng freeze theo hướng **extendable**
- để sau này có thể mở rộng tool/search/SeedPath/automation mà **không cần đập lại model**

---

# 2. Core positioning of Wiki in MVP

## 2.1. Wiki is central, but not everything
Trong MVP, hệ knowledge được chia thành 3 vùng:

1. **Truth**
2. **Wiki**
3. **History**

### Truth
- authoritative
- canonical
- highest-priority reference

### Wiki
- curated + guidance-centric
- fast reading layer for AI
- optimized for understanding and navigation

### History
- evidence / trail / archive
- useful for audit, resume, and later curation
- not a primary truth layer

## 2.2. Wiki-first does not mean wiki-only
AI nên ưu tiên:
1. Truth liên quan
2. Curated Wiki
3. Reference / Guidance
4. History khi thật sự cần

---

# 3. Wiki entry model already frozen

## 3.1. Taxonomy
Wiki entry types in MVP:
- `domain`
- `function`
- `module`
- `data`
- `pattern`
- `reference`

## 3.2. Knowledge classes
- `source_of_truth`
- `curated`
- `reference`
- `history`

## 3.3. Use rules
- `source_of_truth` → `authoritative`
- `curated` → `verify_when_decision_matters`
- `reference` → `verify_before_use`
- `history` → `historical_only`

## 3.4. Core required sections for important wiki entries
- `Purpose`
- `Scope`
- `Canonical References`
- `Recommended Next Reads`

---

# 4. Wiki source-side model — frozen for v1.0

To make Wiki extendable, MVP introduces a source-side model with four first-class concepts:

1. **Wiki Source Artifact**
2. **Wiki Source Meta**
3. **Wiki Source Index**
4. **Source Interpretation Profile**

---

# 5. Wiki Source Artifact

## Definition
`Wiki Source Artifact` là source thật dùng để build/read wiki.

## Examples
- normalized markdown from a document
- code map
- call tree
- schema doc
- design doc
- raw source prepared for wiki work

## Rule
AI should not open source artifacts blindly by default.
Source artifacts are for deeper reading after relevance is confirmed.

---

# 6. Wiki Source Meta

## Definition
`Wiki Source Meta` là bản mô tả nhỏ đi kèm một `Wiki Source Artifact`.

## Purpose
Meta phải:
- đủ nhỏ để AI có thể preload / keep in memory
- đủ giàu để AI quyết định có nên mở source artifact thật hay không

## Typical contents
- short summary
- relation hints to other sources
- profile mapping
- knowledge target hints
- source-specific hints
- change impact hints
- lexical lookup surface richer than index

## Important rules
- Meta is **not** the source artifact
- Meta should **not** become a mini source
- Meta should remain memory-friendly
- Git metadata should **not** be part of meta

---

# 7. Wiki Source Index

## Definition
`Wiki Source Index` là lớp tra cứu trước khi đọc source thật.

## Purpose
AI uses the index to:
- scan candidate sources quickly
- confirm likely relevance
- find the matching meta
- perform reverse lookup from artifact to meta

## Core rule
AI should prefer:

**Wiki Source Index / Meta → confirm relevance → Wiki Source Artifact**

and not jump directly into source artifacts by default.

---

# 8. Relationship between Index and Meta

## Frozen rule
`Wiki Source Index` and `Wiki Source Meta` are tightly related but **not identical**.

### What is frozen
- Index should **not** embed full meta
- Each index entry should contain a **small projection** of the meta
- Meta remains the richer source-side context object

## Practical meaning
- `Wiki Source Index Entry` = projection for quick scan and grep
- `Wiki Source Meta` = richer context card
- `Wiki Source Artifact` = full source for deep reading

This is a deliberate design choice for memory efficiency and future scalability.

---

# 9. Source Interpretation Profile

## Definition
`Source Interpretation Profile` is common/procedural knowledge describing how to work with a source type.

## It defines
- how to read a type of source
- which signals matter
- which signals are noise
- how to extract useful knowledge
- how to map source information into wiki structures
- how to think about likely impact when the source changes
- what lexical lookup keys should be exposed for that source type

## Important distinction
- Profile = class-level knowledge
- Meta = instance-level knowledge

---

# 10. Reverse lookup is required

## Frozen rule
Relationship between Artifact and Meta must be navigable in both directions.

### Forward
Index / Meta → Artifact

### Reverse
Artifact → Index → Meta

## Important clarification
If a `Wiki Source Artifact` is raw / immutable / external and cannot contain reverse pointers:
- reverse lookup must be provided externally
- the standard place for that is `Wiki Source Index`

This is frozen as a principle.

---

# 11. Lexical + semantic lookup are both required

## Frozen rule
Wiki source discovery must support both:
- **semantic lookup**
- **lexical/exact lookup** (grep-friendly)

## Why
In software projects, many useful lookups are exact:
- table names
- field names
- program ids
- screen ids
- class names
- method names
- Japanese business terms
- legacy symbols
- abbreviations

## Consequence
Both `Wiki Source Index Entry` and `Wiki Source Meta` must expose enough `lookup_keys` surface for:
- grep
- exact match
- lexical search
- hybrid retrieval later

## Projection rule
- Index keeps **reduced** lookup keys surface
- Meta keeps **richer** lookup keys surface

---

# 12. Change handling around source artifacts

## Frozen rule
If a `Wiki Source Artifact` changes, the system should **not** rewrite source meta or official wiki immediately.

Instead:
1. detect source change
2. mark the relevant source meta as needing refresh
3. create a meta refresh candidate
4. rebuild meta draft using the source + interpretation profile
5. compare old vs new meta
6. only then create wiki update candidates or mark affected wiki entries if needed

## Important clarification
Git can be used as an **optional change detection mechanism** for sources in a software project repo.

But:
- Git is **not part of Wiki Source Meta**
- Git does **not** decide semantic impact
- semantic impact remains governed by:
  - Source Interpretation Profile
  - meta refresh logic
  - controlled wiki update workflow

---

# 13. Extendability contract

This Wiki v1.0 freeze is designed to be extendable.

## Frozen hard
These should remain stable:
- Truth / Wiki / History 3-zone model
- Wiki Source Artifact
- Wiki Source Meta
- Wiki Source Index
- Source Interpretation Profile
- index/meta-first reading principle
- reverse lookup principle
- index as projection, not full meta
- lexical + semantic lookup principle
- controlled wiki update flow
- Git only as optional change signal, not part of meta

## Frozen soft
These should remain flexible:
- exact file formats
- exact field sets beyond the minimal core
- exact relation taxonomy
- exact search backend
- exact tool names
- exact refresh implementation
- exact common/project storage split

---

# 14. Compatibility with surrounding systems

## Tools / Skills
The frozen model supports:
- source indexing
- meta build / refresh
- source lookup
- wiki candidate generation
- wiki maintenance

## LLM consumption
The model supports:
- lightweight preload via meta
- exact + semantic lookup
- artifact reading only when needed

## SeedPath later
The current model already provides graph-lite hooks:
- relations
- provenance
- source/meta/wiki identity
- profile-based interpretation

So SeedPath can later extend this model without redesigning it.

---

# 15. Freeze statement

The following is frozen for Wiki v1.0 in MVP:

> Wiki in MVP consists of a 3-zone knowledge model (Truth, Wiki, History) and a source-side model (Wiki Source Artifact, Wiki Source Meta, Wiki Source Index, Source Interpretation Profile).  
> AI should navigate source-side knowledge through index/meta first before opening source artifacts.  
> Index entries are projections of source meta, not full meta.  
> Both semantic and lexical lookup must be supported.  
> Source change handling must go through detection → meta refresh → impact evaluation → controlled wiki update, rather than direct rewrite.  
> This freeze is intentionally implementation-light so the surrounding layers—tools, LLM usage, and future SeedPath—can extend it without breaking the core model.
