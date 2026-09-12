# WIKI_META_INDEX_SPEC_v0_2

## Related Specs (Other Layer)
*(Added CR-G3 — AIP-EXEC-015 STEP-01)*

- **Knowledge unit model (2-layer):** `product/methodology/ai_work_system/20_specs/Knowledge_Object_Model_Spec_MVP.md`
  — artifact-level meta as the knowledge unit; cross-artifact relationships via `## Related Sources` (retired KO record — xem `Knowledge_Object_Model_Spec_MVP` §8)
- **Lookup Key Strategy:** `product/wiki_guidelines/core/specs/Lookup_Key_Strategy_Spec_MVP.md`
  — T1/T2/T3 tier rules that govern lookup_keys in this spec's meta records
- **Artifact Type Taxonomy:** `product/wiki_guidelines/core/specs/Artifact_Type_Taxonomy_Spec_MVP.md`
  — canonical artifact_type enum referenced in this spec's artifact meta field

---

## 1. Purpose
Wiki Meta / Index là lớp biểu diễn tri thức ở mức:
- metadata
- index keys
- alias
- links
- traceability
- unresolved markers

để AI và BrSE có thể:
- tìm đúng artifact/object nhanh hơn
- hiểu quan hệ giữa các artifacts/knowledge items
- biết đâu là knowledge active, đâu là knowledge đã được reflected
- tránh phải đọc lại toàn bộ raw artifacts nhiều lần

Wiki Meta / Index là lớp runtime-facing chính của Knowledge Hub.

---

## 2. Key refinement in v0_2
Trong v0_2, spec này được làm rõ rằng Wiki Meta / Index được build dựa trên:
- Artifact Understanding outputs
- Supplemental Artifact Status / Reflection Model
- Wiki Knowledge Profile

### Input roles
- Artifact Understanding: provides structured understanding from source artifacts
- Supplemental Status / Reflection Model: provides operational state model for supplemental knowledge
- Wiki Knowledge Profile: provides build basis, meaning/scope, relation/sufficiency, and reflection handling guidance

---

## 3. Scope in this sprint
Trong sprint này, Wiki Meta / Index được define ở mức minimal nhưng usable:
- minimum metadata fields
- alias support
- required links
- traceability support
- unresolved markers
- supplemental artifact status/reflection support
- update-ready structure for later maintenance/change request flow

Không đi sâu trong sprint này vào:
- semantic/vector retrieval design
- ranking engine
- advanced search scoring
- graph UI
- automated large-scale consistency repair

---

## 4. Meta / Index object layers
Wiki Meta / Index trong sprint này nên support tối thiểu các lớp sau:

### 4.1. Artifact-level meta
Thông tin ở mức artifact cụ thể:
- artifact ref
- artifact type
- artifact family
- title/name
- revision/version
- source location
- project scope
- related artifact refs

### 4.2. Object-level meta
Thông tin ở mức object/concept xuất hiện trong artifacts:
- function
- screen
- batch
- api
- table
- field/group
- business rule
- other relevant project object

### 4.3. Link / traceability meta
Thông tin về quan hệ:
- requirement -> BD
- BD -> DD
- DD -> testcase
- raw requirement -> Q&A -> refined requirement
- supplemental knowledge -> reflected main artifact
- knowledge item -> related knowledge item

### 4.4. Supplemental control meta
Thông tin vận hành cho:
- Q&A
- findings
- open points
- clarification notes
- review comment summaries
- pending decisions

---

## 5. Foundational principle
A meta/index layer should make project knowledge:
- easier to find
- easier to route
- easier to consult correctly
- easier to maintain safely

It should capture enough structure to be useful, but not attempt to replace the source of truth itself.

---

## 6. Minimal goals
A usable Wiki Meta / Index layer should help answer:
- What artifact/knowledge is this?
- What object(s) does it describe or affect?
- How can it be found by name/alias/key?
- What is it linked to?
- Where is it in the requirement/design/test trace chain?
- Is this supplemental item still active?
- Has this supplemental item already been reflected into a main artifact?
- Is current meta usually enough, or is additional source/profile consultation likely needed?

---

## 7. In-scope knowledge families

### 7.1. Requirement-side knowledge
- Raw Requirement knowledge
- Q&A clarification knowledge
- Requirement Definition knowledge

### 7.2. Main project knowledge
- Basic Design knowledge
- Detail Design knowledge
- IT Testcase knowledge
- Meeting Minutes knowledge
- Weekly Report knowledge

### 7.3. Supplemental knowledge
- findings
- open points
- clarification notes
- review comments summary
- pending decisions
- similar supplemental knowledge

---

## 8. Minimal metadata model

### 8.1. Common artifact meta fields
Each indexed artifact should minimally support:
- `artifact_ref`
- `artifact_type`
- `artifact_family`
- `artifact_title_or_name`
- `project_scope`
- `source_location`
- `version_or_revision`
- `related_artifact_refs` *(flat traceability; typed cross-artifact relationships go in the `## Related Sources` section of the meta MD)*
- `meta_confidence_note` *(optional but recommended)*
- `node_kind` *(optional; `artifact` (default) | `object`; **meta-only — NOT a slim-index field**, INV-7 of CR-AIWS-2026-05-023. See "Two-kind node — node_kind & object metas" below.)*
- `system` *(optional; CR-AIWS-2026-06-017 — multi-system scoping. A flat scope id; **absent/null = common** (visible under every system). Orthogonal to `source_type`/`profile_id` (same type can exist under many systems); NO subsystem level (encode finer scope inside the id, e.g. `sys-a-sub1`). Projected into the index with omit-blank. Active ONLY in a project with `multi_system: true` in `project_profile.yml`; otherwise ignored. When `multi_system: true`, a non-empty `system` must be one of the project's declared `systems:` (lint WARN otherwise). NOT a required field — existing metas without it remain valid = common.)*

### 8.2. Object-level common fields  *(retired — xem `Knowledge_Object_Model_Spec_MVP` §8)*

> Retired cùng KO record (CR-005/CR-020) — không thuộc 2-layer model; field list cũ nằm trong CR + git history.
> Cross-artifact relationships → **`## Related Sources`** (see "Knowledge Output Model (2-layer)" below).
>
> **Re-homed (CR-AIWS-2026-05-022):** the §8.3 relationship FIELD SET is NOT historical — it is the **LIVE**
> vocabulary for `## Related Sources` entries and the `relations.jsonl` projection. Its canonical home is now
> **Knowledge_Relationship (Related Sources) Spec v0.4 (§4 registry/confidence, §6A relations.jsonl contract)**.
> It is the field schema of the edge layer over artifact metas.

### 8.3. Relationship field set  *(LIVE — re-homed to Knowledge_Relationship Spec v0.4, CR-022)*
The relationship edge field set, used by `## Related Sources` entries and projected (both endpoints) into `relations.jsonl`:
- `relationship_type`  *(open registry: base roles ∪ `x:` extension; unknown bare type = WARNING only, never error)*
- `source_ref`
- `target_ref`
- `relationship_basis_note`
- `relationship_confidence_note`  *(optional; `asserted` / `inferred` / `candidate`, default `asserted`)*

Canonical home: **Knowledge_Relationship (Related Sources) Spec v0.4** — §4 (registry + confidence), §6A
(`relations.jsonl` projection contract). These are EDGE fields over artifact metas.

### 8.4. Sufficiency / consultation hints
Because meta is the main runtime-facing layer, it is useful to support lightweight hints such as:
- `meta_usually_sufficient` *(yes/no/maybe)*
- `additional_reference_may_be_needed_when`
This should stay lightweight in this sprint.

### 8.5. Multi-system tooling contract  *(CR-AIWS-2026-06-061)*
Multi-system scoping (CR-AIWS-2026-06-017) is **not** the responsibility of a single tool — it is a
**tooling-wide contract**. The `system` field (§8.1) is only honored end-to-end if *every* tool that writes a
meta, projects the index, queries it, regression-tests lookup, or reads the project config is system-aware.
Historically the gate lived in exactly one place (`lookup_wiki_source.py`'s `--system`/`--all-systems` gate)
and every other tool lagged it one at a time (e.g. a meta builder with no `--system`, a refresh that dropped
the tag, a regression tool that could not assert no-bleed). This contract closes that bug *class* rather than
patching one more instance.

**Obligation by tool class:**

| Tool class | Obligation |
|---|---|
| Meta **writer** (build / refresh / normalize / object-author) | set `system:` at create (`--system` / `--common`, validated against `systems:`, gated in a `multi_system: true` project) AND **preserve** it on refresh / normalize; absent = common |
| Index **projector** | project `system:` into the index with omit-blank; a per-scope build labels its own index |
| **Query** | in a `multi_system: true` project, hard-require `--system <id>` or `--all-systems` (no silent default); filter = the selected system ∪ common |
| **Test / regression** | be able to express AND assert system scoping and cross-system no-bleed (same-named artifacts under different systems must not leak) |
| **Config reader** | parse `systems:` correctly (including inline comments); never silently disarm the gate |

**Reuse, do not re-implement.** The canonical system primitives live in the shared tooling module
(`_common.py`): `read_project_config()`, `in_system()`, and `validate_system()`. Any tool in the classes above
MUST consume these primitives rather than re-deriving config parsing or the system-membership predicate —
divergent copies are the drift surface this contract removes.

**Fixture namespace — `synthetic_systems` (CR-AIWS-2026-07-028).** `project_profile.yml` MAY declare
`synthetic_systems: [..]` — the subset of `systems:` that are SYNTHETIC (fixture/test corpora, e.g. a demo
project or skill-test manuals). A fixture artifact (locator under a `fixtures/` dir) registered into the live
index **MUST** carry a synthetic system id; the namespace of a REAL system carries only real documents.
Enforced by lint rule `fixture_under_real_system` (**ERROR**), active only when `synthetic_systems` is
declared (absent → no-op, backward compatible). Rationale: fictional fixture docs under a real system poison
every wiki page grounded on that system (incident OP-931-03: three fictional RDs were system `aiws`'s only
`requirement_definition`s — its overview pages would have described a product that does not exist).
`read_project_config()` exposes the list; synthetic classification is **lint-only** — it never filters lookup
results (rule #12 scoping is untouched).

**Enforcement = a conformance test, not prose.** The obligation is enforced by a conformance matrix in the
wiki regression suite (`test_wiki_regression.py`), which asserts each class's obligation against the compliant
tools. **Checklist when adding or changing such a tool:** (1) make it system-aware per its class above; (2)
route its config / membership logic through the `_common` primitives; (3) add it to (or update) the conformance
matrix. A tool that is not yet compliant MUST be marked as a known-deferred entry referencing its tracking CR
— never silently omitted.

---

## 9. Alias support

### 9.1. Why alias matters
Projects often use:
- Japanese names
- English names
- abbreviations
- function IDs
- screen IDs
- local shorthand

Alias support is necessary so AI can:
- resolve user wording
- connect artifacts that use different names
- route to the right object faster

### 9.2. Minimal alias fields
- `canonical_name`
- `alias`
- `alias_type`
  - exact synonym
  - abbreviation
  - language variant
  - likely candidate
- `alias_confidence_note`

### 9.3. Rule
If alias mapping is unclear, AI should prefer:
- mark candidate alias
- or create unresolved alias note
rather than silently merging names incorrectly

---

## 10. Link and traceability support

### 10.1. Required link types
At minimal level, Wiki Meta / Index should support:
- `upstream_of`
- `downstream_of`
- `related_to`
- `reflected_to`
- `superseded_by`
- `implements`
- `tests`
- `clarifies`

### 10.2. Requirement chain support
The meta/index layer must support the chain:
- Raw Requirement
- Q&A Clarification
- Requirement Definition

This chain should not be flattened too early.

### 10.3. Main flow support
The meta/index layer should also support the flow:
- Requirement Definition -> Basic Design -> Detail Design -> IT Testcase

### 10.4. Knowledge relation support
Because runtime may rely on meta rather than profile most of the time,
important relations between knowledge items should be made explicit when they are practically useful.

### 10.5. Rule
When exact link certainty is unavailable, AI should:
- mark unresolved linkage
- keep conservative link note
- avoid pretending full certainty

---

## 11. Supplemental artifact support

### 11.1. Required fields for supplemental knowledge
For Q&A and similar supplemental knowledge, meta/index should additionally support:
- `status`
- `reflection_status`
- `reflected_to`
- `reflected_at`
- `superseded_by`

### 11.2. Why this is required
Without these fields, AI cannot know whether:
- the supplemental item is still operationally active
- it should still be consulted directly by default
- it has already been absorbed into a main artifact

### 11.3. Rule
Supplemental meta should preserve the difference between:
- resolved
- reflected
because these are not the same thing.

---

## 12. Unresolved markers

### 12.1. Purpose
Not all project meta can be completed safely from available artifacts.
Unresolved markers allow the system to stay honest without blocking all progress.

### 12.2. Minimal unresolved marker cases
- missing artifact linkage
- uncertain alias
- uncertain object mapping
- uncertain reflection status
- missing upstream/downstream target
- unclear knowledge scope or artifact role

### 12.3. Suggested unresolved fields
- `unresolved_type`
- `unresolved_note`
- `related_ref`
- `followup_needed`

---

## 13. Meta / Index output objects

### 13.1. Artifact meta record
Represents one artifact as an indexed object in the Wiki layer.

### 13.2. Object meta record
Represents one reusable project object/concept.

### 13.3. Link record
Represents one typed relationship between records.

### 13.4. Supplemental status record
Represents operational state and reflection state for a supplemental item, when relevant.

---

## 14. Minimal schema examples

### 14.1. Example — artifact meta record
```yaml
artifact_ref: DD_F04_v3
artifact_type: detail_design
artifact_family: main_project_artifact
artifact_title_or_name: Booking Search Detail Design
project_scope: project_alpha
source_location: /docs/dd/DD_F04_v3.docx
version_or_revision: v3
related_artifact_refs:
  - BD_F04_v1
  - REQ_DEF_F04_v2
meta_usually_sufficient: maybe
additional_reference_may_be_needed_when:
  - unresolved_q_and_a_still_active
```

### 14.2. Example — object meta record  *(LEGACY — object & link records removed under 2-layer, CR-020; see §8.2 note. Below §14.2 + §14.4 are historical only.)*
```yaml
object_ref: func_booking_search
object_type: function
canonical_name: Booking Search
aliases:
  - alias: F04
    alias_type: abbreviation
  - alias: 予約検索
    alias_type: language_variant
related_artifact_refs:
  - REQ_DEF_F04_v2
  - BD_F04_v1
  - DD_F04_v3
  - ITTC_F04_v1
```

### 14.3. Example — supplemental meta record
```yaml
artifact_ref: QA_REQ_F04_003
artifact_type: qa_list
artifact_family: requirement_side
status: answered_unapplied
reflection_status: not_reflected
reflected_to: []
reflected_at: null
superseded_by: []
meta_usually_sufficient: no
additional_reference_may_be_needed_when:
  - clarification_conflict_exists
```

### 14.4. Example — link record
```yaml
relationship_type: reflected_to
source_ref: QA_REQ_F04_003
target_ref: REQ_DEF_F04_v2
relationship_basis_note: This Q&A item was incorporated into the refined requirement definition.
```

---

## 15. Update-readiness requirement
The meta/index model should be structured so that later update flows can:
- add metadata
- revise alias mapping
- add new links
- revise reflection status
- mark superseded records

This sprint does not define the full update engine, but the model should not block later maintenance.

---

## 16. Relationship with other specs
This spec is intended to feed:
- Wiki Knowledge Profile Spec
- Wiki Change Request Spec
- AIP-Wiki Integration Spec
- maintenance/update guidelines

---

## 17. Out of scope for this sprint
- semantic retrieval scoring
- ranking optimization
- vector index design
- graph database design
- automated large-scale deduplication
- advanced conflict resolution engine

---

## 18. Completion criteria for BL-05
BL-05 is considered done when:
- minimal artifact meta model is clearly defined
- object-level meta support is clearly defined
- alias support is clearly defined
- link/traceability support is clearly defined
- supplemental artifact status/reflection support is clearly defined
- unresolved marker handling is clearly defined
- relationship with Wiki Knowledge Profile is explicitly captured

---

# v0.9.8 Runtime Compatibility Addendum — Wiki Source Meta / Index

## A1. Purpose of this addendum

This addendum clarifies how the minimal Wiki Meta / Index design is used in the current AIWS runtime while preserving compatibility with the existing v0.9.2 Wiki Source Meta / Wiki Source Index mechanism.

It does not replace the existing spec above.

It adds the following runtime-compatible decisions:
- preserve current good field names and tooling
- use Wiki Source Meta and Wiki Source Index as the current concrete implementation
- use `lookup_wiki_source.py` as current lookup interface
- use `meta_locator` first, then `artifact_locator` when source detail/evidence is needed
- treat `artifact_locator` as the AIWS-readable source representation
- keep optional enrichment optional
- distinguish lightweight meta maintenance from Controlled Knowledge Promotion

---

## A2. Current concrete mechanism

Current concrete mechanism:

```text
Wiki Source Meta
  ↓
Wiki Source Index
  ↓
lookup_wiki_source.py
  ↓
meta_locator
  ↓
artifact_locator when needed
```

Current project paths:

```text
.ai-work/wiki_sources/meta/*.md
.ai-work/wiki_sources/index.jsonl
.ai-work/wiki_sources/index.local.jsonl
.ai-work/tooling/build_wiki_source_index.py
.ai-work/tooling/lookup_wiki_source.py
```

Current package tooling:

```text
payload/tooling/build_wiki_source_meta.py
payload/tooling/build_wiki_source_index.py
payload/tooling/lookup_wiki_source.py
payload/skills/aiws-wiki/SKILL.md
payload/skills/aiws-wiki/SKILL.md
payload/skills/aiws-wiki/SKILL.md
```

---

## A3. Naming compatibility rule

```text
If an existing v0.9.2 field name is not wrong, keep it.
```

Preserve current frontmatter fields:

```yaml
artifact_type:
source_id:
title:
source_type:
knowledge_class:
artifact_locator:
profile_id:
status:
updated_at:
```

Preserve current body sections:

```markdown
## Summary
## Knowledge Targets
## Lookup Keys
## Artifact Reference
## Source-Specific Hints
## Change Impact Hints
## Cautions
```

Preserve current index JSONL fields:

```json
{
  "source_id": "",
  "title": "",
  "source_type": "",
  "artifact_locator": "",
  "meta_locator": "",
  "meta_id": "",
  "profile_id": "",
  "summary_short": "",
  "knowledge_targets": [],
  "lookup_keys": [],
  "status": "",
  "updated_at": ""
}
```

---

## A3.1 `updated_at` field semantics (CR-AIWS-2026-06-024)

`updated_at` is a **UTC ISO 8601 timestamp** (e.g. `2026-06-19T07:30:00+00:00`). Its value is content-aware:

| Meta kind | `updated_at` value |
|---|---|
| **Source-backed** — has a real backing artifact file (`artifact_locator` resolves to a file) | the **mtime of that source file** |
| **Sourceless** — object meta (`artifact_locator: __OBJECT__`) or a hand-authored entry meta with no backing file | the **moment the meta is updated** (write time) |

Rationale: a source-backed `updated_at` is deterministic by content basis — rebuilding/refreshing an unchanged source reproduces the same value; it advances only when the source changes. The tooling captures this automatically: `build_wiki_source_meta.py` and `build_java_wiki_metas.py` stamp `source_mtime_iso(source)`, and `refresh_wiki_source_meta.py` inherits the same value (it re-projects through the builder). Sourceless metas (refreshed by hand) record `now_utc_iso()`.

Entry-meta `last_verified_at` uses the same UTC ISO 8601 format (recorded at verification time).

**Backward-compat:** legacy date-only values (`YYYY-MM-DD`) remain valid — `lint_wiki` accepts BOTH a date and a timestamp permanently; there is no forced migration (a meta upgrades to a timestamp the next time it is built/refreshed).

**Caveat — git does not preserve mtime.** A fresh `clone`/`checkout` sets every source file's mtime to checkout time, so rebuilding metas on a fresh clone and re-committing would regress source-backed `updated_at` to checkout time. The captured value is frozen in the committed meta, so this is safe as long as build/refresh runs on the machine where the source was edited, before committing.

> Note: `updated_at` is a meta-frontmatter field only — it is **not** projected into the slim `index.jsonl` (removed 2026-05-27; see "Slim Index Entry Format" below).

---

## A4. Runtime lookup flow

AI should use this runtime flow:

```text
Current context / Workspace / current task state
  ↓
Clarify task intent if needed
  ↓
Use Task Lens to shape access when applicable
  ↓
Run lookup_wiki_source.py or inspect Wiki Source Index
  ↓
Review candidate source records
  ↓
Open meta_locator
  ↓
Read Wiki Source Meta
  ↓
Check Summary / Knowledge Targets / Lookup Keys / Hints / Cautions
  ↓
Open artifact_locator only when details/evidence are needed
  ↓
Use artifact/source in task
```

Core guardrail:

```text
Wiki-first, not Wiki-only.
Meta first, source artifact when needed.
```

---

## A5. Source artifact representation rule

AIWS runtime reads AIWS-readable markdown/source representation.

It does not directly read original non-text raw files.

For non-text files such as PDF, Word, Excel, PowerPoint, image, diagram, or binary file:

```text
Original non-text file
  ↓
converted as-is into markdown / AIWS-readable representation
  ↓
artifact_locator points to the converted representation
```

The markdown/source representation should be sufficient for AI to understand the original file content needed for runtime.

If not sufficient, classify as:

```text
source_representation_quality_issue
```

AI should then:
- state the limitation
- explain what cannot be verified
- request better conversion or HUMAN confirmation
- avoid unsupported inference
- not directly inspect the original non-text raw file as workaround

---

## A6. Artifact Reference pattern for converted files

Use the existing `Artifact Reference` section.

Recommended style:

```markdown
## Artifact Reference
- artifact_locator: <converted markdown / AIWS-readable artifact>
- original_artifact_locator: <optional original PDF/Excel/Word/image path>
- conversion_note: converted as-is from original format to markdown
- representation_quality: sufficient | partial | needs_review
```

This preserves the current `artifact_locator` field and does not require index schema changes.

---

## A7. Source ID / Knowledge Targets / Lookup Keys rules

`source_id` should be:
- unique in project
- stable over time
- uppercase
- hyphen-separated
- expressive enough to identify artifact family and scope

Recommended pattern:

```text
SRC-<ARTIFACT_FAMILY>-<OBJECT_OR_SCOPE>
```

`Knowledge Targets` should describe what knowledge areas the artifact covers.

`Lookup Keys` should include practical search keys:
- function ID
- screen ID
- aliases
- Japanese / English terms where useful
- common project shorthand
- artifact family terms

Rule:

```text
Keep current field names.
Make the content inside those fields better for AI retrieval.
```

---

## A8. Source-Specific Hints / Change Impact Hints / Cautions

Use existing body sections:

```text
Source-Specific Hints = how to use the artifact.
Change Impact Hints = when/how meta may need update.
Cautions = what AI must not over-assume.
```

These sections improve AI runtime behavior without schema/tooling changes.

---

## A9. Build / update / rebuild / verify rule

Current-compatible update flow:

```text
create/update Wiki Source Meta
  ↓
rebuild Wiki Source Index
  ↓
verify by lookup
  ↓
use meta/source in AI runtime
```

Core rule:

```text
Fix meta, not generated index.
Verify lookup after every meaningful meta change.
```

Do not edit `index.jsonl` or `index.local.jsonl` manually.

---

## A10. Optional enrichment boundary

Use current fields and body sections first.

Optional enrichment fields such as the following are not mandatory in this MVP merge:

```yaml
knowledge_value:
ai_use_cases:
authority:
freshness:
related_entries:
related_sources:
canonical_name:
aliases:
retrieval_keywords:
```

Default rule:

```text
Preserve current fields.
Use current body sections first.
Add new fields only when there is clear AI runtime value.
Do not change index schema/tooling in this sprint.
```

---

## A11. Relation to Controlled Knowledge Promotion

Small lookup/meta fixes may be lightweight maintenance.

Examples:
- add missing Lookup Key
- fix typo
- correct broken artifact_locator
- add clear caution
- improve Summary wording
- add representation quality note

Changes that affect authority, meaning, scope, source identity, or broad future AI behavior should go through Controlled Knowledge Promotion.

Examples:
- set `knowledge_class: source_of_truth`
- change `source_id`
- split/merge meta records
- mark important artifact deprecated
- change project-wide optional enrichment pattern
- update traceability between major artifacts

Important changes should be logged for review/revision/rollback.

---

## A12. Deferred items

Deferred:
- index schema change
- build/lookup script change
- mandatory new fields
- full metadata registry
- graph DB / ontology
- automatic migration

> **Amendment (CR-AIWS-2026-05-019):** "full metadata registry" ở trên là registry **enrichment cho
> source meta** — vẫn deferred. Nó KHÔNG bao gồm **Source Build Routing** (bảng dispatch
> `source_type → build/refresh tool`), một mối quan tâm tooling tách biệt được governed bởi
> `SOURCE_BUILD_ROUTING_SPEC.md`.
>
> **Update (CR-AIWS-2026-05-019 Stage 2, applied 2026-06-15 via AIP-EXEC-101):** the data-driven routing
> registry (`_build_routing.json` + `route_build_tool.py`) is now **IMPLEMENTED (MVP)** — the 2nd-source_type
> gate was waived by the wiki-manager. It remains a **JSON sidecar** and is **NOT projected into `index.jsonl`**
> (the registry-enrichment-of-source-meta concern above stays deferred; build routing is a separate tooling
> dispatch table, never an index field).
- automated validation/lint
- scoring/telemetry
- full SeedPath integration
- direct AI reading of original non-text raw files

---

# v0.9.9 Working AIP Connection addendum

Wiki Meta / Index supports Working AIP Connection by helping AI discover candidate sources.

A Wiki lookup result is not Working AIP.

Selected lookup results should be reflected into Working AIP as source references:

```markdown
## Context / Source References
| Ref | Type | Role in task | Status | Usage / Limitation |
|---|---|---|---|---|
| SRC-... | requirement_doc | source for ... | active | open meta first, artifact if exact wording needed |
```

If source representation is insufficient, record `source_representation_quality_issue` in Working AIP as blocker/limitation.

---

# v0.9.10 Workspace Boundary addendum

Workspace may store selected Wiki Source Meta / Index references for the current task.

A Workspace source note is not a Wiki Source Meta update.

If AI discovers missing lookup keys, missing cautions, source representation issues, or related Wiki Meta improvements:
- add current-task action to Runtime Queue if it must be handled in this task
- add possible future-value item to Capture Inbox if it should be triaged later
- use Controlled Knowledge Promotion / lightweight maintenance as appropriate

---

# v0.9.11 Minimal Runtime Testing addendum

Runtime testing stance for Wiki Meta / Index:

```text
Meta is routing, not final evidence.
Index is projection, not source.
```

Minimal checks:
- required locator/reference fields exist
- source_id/title/source_type/status are clear where required
- index does not embed full source/meta content
- source artifact is opened when exact evidence is needed
- source representation limitations are visible when relevant

Future alignment candidate:
- Wiki Tooling Alignment Sprint to align v0.9.2 Wiki tools with newer Knowledge Hub / Controlled Promotion / source representation specs.

---

# v0.9.12 Runtime Tooling Alignment addendum

Current Runtime Tooling Alignment includes only minimal Wiki tooling boundary alignment.

Preserve:
- index-first lookup
- meta is routing, not evidence
- lint_wiki is deterministic guardrail, not reviewer
- refresh is draft/review/apply
- change/impact tools are signal, not approval

Deep Wiki Tooling Alignment remains future sprint scope.

---

# v0.9.13 Wiki Tooling Alignment addendum

Wiki tooling boundary:

```text
Wiki tools support AI runtime routing and maintenance,
but they do not replace source verification, approval, or Controlled Knowledge Promotion.
```

Recommended Wiki Source Meta alignment fields:
- `authority_level`
- `freshness_status`
- `source_representation_status`
- `source_representation_caution`
- `source_representation_quality_issue`
- `knowledge_value`
- `intended_ai_use`
- `promotion_status`
- `maintenance_status`
- `review_required`

Recommended Wiki Source Index projection fields:
- `authority_level`
- `freshness_status`
- `promotion_status`
- `source_representation_status`
- `intended_ai_use` — lookup tool đọc field này để in `use-hint:` trong kết quả (routing hint trước khi mở meta/source; CR-AIWS-2026-08-056)

Runtime boundary:

```text
Index/Meta routes.
Source artifact verifies.
```

---

# v0.9.15 Source Representation addendum

Recommended Wiki Source Meta representation fields:
- `original_source_locator`
- `representation_locator`
- `representation_type`
- `conversion_method`
- `conversion_date`
- `converted_by`
- `conversion_limitations`
- `representation_scope`
- `source_representation_status`
- `source_representation_caution`
- `source_representation_quality_issue`

Runtime locator rule:

```text
artifact_locator should point to AIWS-readable source representation.
```

---

# CR-D1 Addendum — Output Model (2026-05-25; revised to 2-layer by CR-AIWS-2026-05-020, 2026-05-30)

Source: AIP-EXEC-014 STEP-03, CR-D1 from AIWS-Wiki-CR-Proposal-2026-05-25.md §3.
Revised by AIP-EXEC-038 / CR-AIWS-2026-05-020 (retired KO record — xem `Knowledge_Object_Model_Spec_MVP` §8).

## Knowledge Output Model (2-layer)

Wiki knowledge outputs trong AIWS được tổ chức thành **2 lớp** (artifact meta + index), cộng một nhóm supplemental:

| Lớp | Tên | Mô tả | Granularity | Nơi lưu | Tạo bởi |
|-----|-----|-------|-------------|---------|---------|
| 1 | Artifact-level meta | Routing/lookup metadata per source file, **kèm `## Related Sources`** cho quan hệ cross-artifact | Per file | `wiki_sources/meta/<id>.md` | `/aiws-wiki build-meta` |
| (proj) | Index | Projection của Lớp 1 metas — lookup surface | Per index | `wiki_sources/index.jsonl` | `build_wiki_source_index.py` |
| (proj) | Relations | Projection của `## Related Sources` edges — reverse/impact surface (both endpoints; one-hop; **KHÔNG** vào index.jsonl) | Per edge | `wiki_sources/relations.jsonl` | `build_relations.py` (query: `wiki_relations.py`) |
| (suppl) | Supplemental | Q&A records, findings, open points, reflection status | Per item | Workspace / AIP / curated per case | Manual / AIP |

### Quan hệ cross-artifact = `## Related Sources`

**Mỗi artifact meta mang một section `## Related Sources`** liệt kê các source liên quan kèm **role** (typed)
— vd `upstream_input`, `triggered_flow`, `companion_requirement`. (Retired KO record — xem
`Knowledge_Object_Model_Spec_MVP` §8.)

- `## Related Sources` nằm TRONG meta của Lớp 1; **KHÔNG project vào `index.jsonl`**.
- Role enum + scaffold tự động: xem CR-AIWS-2026-05-004 (Change 8) + CR-AIWS-2026-05-017.
- `related_artifact_refs` (Lớp 1) vẫn là flat traceability; quan hệ có-role dùng `## Related Sources`.
- **Reverse / impact (CR-AIWS-2026-05-022):** `## Related Sources` chỉ là out-edges. Để hỏi IN-edges ("ai trỏ AT X / ai gọi X")
  dùng projection `relations.jsonl` (build bằng `build_relations.py`; query opt-in bằng `wiki_relations.py --relations`) —
  một reverse index **ONE-HOP**, both-endpoints, **KHÔNG** nhập `index.jsonl`. Spec: Knowledge_Relationship Spec v0.4 §6A.

### Cross-references

- Knowledge unit model (2-layer): `product/methodology/ai_work_system/20_specs/Knowledge_Object_Model_Spec_MVP.md`
- Related Sources roles & scaffold: CR-AIWS-2026-05-004 (Change 8) / CR-AIWS-2026-05-017
- Status/reflection (supplemental): `product/methodology/ai_work_system/20_specs/Controlled_Knowledge_Promotion_Spec_MVP.md`
- Tier strategy cho Lớp 1 lookup_keys: `product/wiki_guidelines/core/specs/Lookup_Key_Strategy_Spec_MVP.md`

> **Revision (CR-AIWS-2026-05-020, 2026-05-30):** output model collapsed to 2-layer (artifact meta + index),
> relationships via `## Related Sources`; retired shapes — xem `Knowledge_Object_Model_Spec_MVP` §8.
> Pre-revision 4-layer table preserved in git history.

---

# CR-D7 Addendum — Evidence Level Behavioral Note (2026-05-25)

Source: AIP-EXEC-014 STEP-04, CR-D7 from AIWS-Wiki-CR-Proposal-2026-05-25.md §3.

## Behavioral note: `source_representation_status: partial` → evidence level

Khi artifact meta có `source_representation_status: partial`:

> AI MUST report evidence level as `wiki_only` per `Knowledge_Routing_Spec_MVP §evidence depth`.
> AI KHÔNG được claim `source_checked` mà không:
> 1. Mở source artifact raw (hoặc converted representation đầy đủ)
> 2. Confirm scope với user (đặc biệt khi representation conversion có limitations)

**Why:** `partial` status nghĩa là converted representation không cover đầy đủ source content. Claim `source_checked` dựa trên partial representation là false confidence.

**Alignment note:** Term `representation_quality: sufficient|partial|needs_review` từ guide local project B_N → align với canonical `source_representation_status` 6-value enum. Khi guide local và canonical conflict → spec wins (CLAUDE.local.md Rule 2).

---

## Slim Index Entry Format — 2026-05-27 Addendum

**Source:** Applied from wiki_improvement_request.md Nhóm 2+5 (validated in vti-ai-work-system-demo, 2026-05-26).

### Fields permanently removed from index projection

The following fields are no longer included in `index.jsonl` entries — they added token overhead without providing lookup or routing value:

| Field removed | Reason |
|---|---|
| `meta_id` | Duplicate of `source_id` — no independent value |
| `updated_at` | Not used by any tool at read time |
| `knowledge_value` | Not used by lookup tool; AI derives from meta |

> **`intended_ai_use` — KHÔNG còn trong removed-list** (CR-AIWS-2026-08-056): field được re-add vào index projection một cách chủ đích (commit `eb07d0c`, 2026-05-29 — thiếu CR, regularized bởi CR-AIWS-2026-08-056). Lookup tool **có dùng**: in `use-hint:` per result. Xem danh sách projection fields ở trên.

### Conditional locator fields

`original_source_locator` and `representation_locator` are included **only when their value differs from `artifact_locator`**. When identical, they are omitted to avoid duplication.

When `representation_locator` is omitted because it equals `artifact_locator`, the AIWS-readable `artifact_locator` itself **is** the representation locator; `lint_wiki` MUST NOT flag `meta_missing_representation_locator` in that case (CR-AIWS-2026-07-021 IR-C). It flags only when there is no AIWS-readable representation at all — e.g. `original_source_locator` is set and `artifact_locator` points at a raw binary (`.pdf`/`.xlsx`/…) with no `representation_locator`.

### Omit-blank rule

Index generator (`build_wiki_source_index.py`) must apply omit-blank logic: fields whose value is empty string `""`, `None`, or empty list `[]` are excluded from the written entry.

**Required fields** (`source_id`, `title`, `source_type`, `artifact_locator`, `profile_id`, `summary_short`, `knowledge_targets`, `status`) are always present — they never have blank values in a valid meta.

### Two-kind node — node_kind & object metas (CR-AIWS-2026-05-023, v0.3 design)

The knowledge unit is a meta with `node_kind: artifact (default) | object` (Knowledge_Object_Model_Spec v0.3). Object
nodes (logical entities: function/screen/table/…) sit in the **SAME `index.jsonl`**, found by the **SAME lookup** — there is
**no `--kind` flag, no new index field, no scorer change** (DP7). Specifics:

- **`node_kind` is META-ONLY — NOT projected into the slim index** (INV-7). It distinguishes kinds at meta level; the index/lookup treat both kinds identically.
- **Object identity = ordinary `source_id`** (recommended family prefixes `SRC-FUNC-`/`SRC-SCREEN-`/`SRC-TABLE-`…). Không shape nào của retired record (INV-1/INV-2 — xem `Knowledge_Object_Model_Spec_MVP` §8).
- **`__OBJECT__` sentinel:** an object meta sets `artifact_locator: __OBJECT__` (no backing file, INV-9). It is a non-blank value → the omit-blank rule preserves it. Lint (`INDEX_REQUIRED`/`META_REQUIRED`) accepts `__OBJECT__` **only when `node_kind=object`**; `_orphan_artifact_check` early-returns on `__OBJECT__`. *(Tooling enforcement is implemented in the follow-up apply per CR-023 Change-5; this spec documents the contract.)*
- **Pointer-only:** an object meta must NOT aggregate (retired shapes — xem `Knowledge_Object_Model_Spec_MVP` §8) — error-grade (DP5/INV-3). "Everything about X" = `wiki_relations.py --relations <source_id>` (out+in), not lookup.
- **Object-authoring gate:** object metas are authored only after the follow-up AIP lands the Change-5 guards + the INV-5 named-consumer test; default `node_kind=artifact` means zero migration for existing metas.

### Token impact

- Before (full schema): ~420 tokens/entry
- After (slim): ~90–130 tokens/entry
- Navigation outcome: unchanged — lookup precision unaffected

---

# H6 Chunked-Meta Addendum — section addressing for large sources (CR-AIWS-2026-07-002)

> Added 2026-07-04 (CR-AIWS-2026-07-002 H6; Wiki-Manager confirmed §18 two-role). Optional fields —
> **omit-blank in the index**, so normal (non-section) metas are unaffected (zero migration).

A **large** source file (default **> 1000 lines OR > 50 KB**; per-profile override via
`chunk_threshold_lines` / `chunk_threshold_kb`) is kept INTACT on disk but split at the META layer:
`build_wiki_source_meta.py` emits one **parent** meta + one **section** meta per `## ` section. A
section meta carries two optional frontmatter fields (projected into `index.jsonl` with omit-blank):

- **`section_heading`** — the `## ` heading the section covers.
- **`section_lines`** — the inclusive line range **`"start-end"`** (integers, start ≤ end) of that
  section in the shared `artifact_locator`. Runtime opens the source and **Reads only this range**
  instead of the whole file.

Parent ↔ section are linked via `## Related Sources` (`contains` on the parent, `part_of` on each
section) — queryable one-hop like any edge. The retired field name **`source_anchor` stays forbidden**
(INV-3); H6 uses `section_lines`. `lint_wiki` validates the `"start-end"` format (start ≤ end) and that
`section_heading` is accompanied by `section_lines`.

**Re-chunk on refresh (CR-AIWS-2026-07-006 A1 — supersedes the former "create-mode only" limit):**
`build_wiki_source_meta --mode refresh` on a chunked source REBUILDS the child set — heading/line
drift is detected, ranges re-computed, and orphan children (removed/merged sections) are deleted
(no dangling `-SEC-` metas). Child identity + carry-over rules:

- **Id-stability:** child ids are heading-slug-keyed (`<parent>-SEC-<slug>`), NOT positional;
  duplicate `## ` headings in one doc slug-dedup with `-2`, `-3`, … suffixes.
- **Content-hash carry-over:** each child records a `section_hash` of its section BODY (heading
  line excluded). On re-chunk, a hash match means unchanged content — the child KEEPS its
  completed `## Summary` and `## Lookup Keys` verbatim (LLM/curated work never silently reverts
  to boilerplate), even across a heading rename. Changed/new sections re-emit mechanically (and
  flag `needs_completion: [summary]` under `--emit-partial` — the H1 completion pass fills them).
- **First-3 keys guard (MP1):** a child's pinned keys are three discriminative compounds —
  `"<title> <heading>"`, `"<doc-stem> <heading>"`, `"<heading>"` — so the self-test first-3-keys
  gate holds on mechanical children (dogfood 2026-07-07: 45 children, 784/784 self-test PASS).
- **Ordered-`contains` contract (A3):** the parent's `## Related Sources` lists children in
  DOCUMENT ORDER — section sequence is derivable one-hop from the parent (no sibling next/prev
  edges). Lookup renders chunk children grouped under their parent when both hit.
- **Lint:** `chunk_range_vs_heading` (ERROR) — a child's `section_lines` must still start at its
  `## <section_heading>` line in the live artifact; a drifted range = re-chunk the source.
- **Enablement (A4 / DP-912-1):** per-profile `chunk_enabled: true|false` opt-in for bulk canonical
  builds (`build_canonical_package_metas` respects it; CLI `--chunk`/`--no-chunk` still override).
  The global default flip is gated on further dogfood (follow-up tracker A-1). Semantic GROUPING
  of sections ("nhóm thông tin", contiguous-only per DP-912-2) is evidence-gated P2 — NOT applied.

## Addendum — Retrieval recall additions (CR-AIWS-2026-07-007, applied 2026-07-07)

§3's deferred item "semantic/vector retrieval design" is re-opened INCREMENTALLY. P1 (applied, stdlib-only,
zero index-schema change — all attach at the `_common` single-point scorer / lookup CLI):

- **Two-way diacritic fold (B1):** scoring normalizes BOTH query and indexed fields via
  `_common.wiki_fold` (NFD-strip + casefold; Đ→D explicit). ASCII behavior unchanged; VN queries
  match có dấu/không dấu. Curated lookup_keys are NOT rebuilt (fold happens at score time).
- **Query alias expansion (B2):** `profiles/query_aliases.yml` — phrase-level `"<phrase> => <targets>"`
  entries, folded both sides, expanded into the query token set before scoring. PROJECT-customizable;
  seeded (never ships empty). Alias curation feeds from `retrieval_improvement` captures (MP2).
- **Query-time document frequency (B3):** tokens present in > `DF_CUTOFF` (0.4) of the LOADED record
  set contribute half weight in token-mode scoring (`_common.compute_token_df`, computed in-memory per
  invocation — deliberately NOT a projected index field; index.jsonl schema unchanged).
- **Mode naming (B4):** `--mode tokens` is the accurate name for per-token overlap matching;
  `semantic` remains a deprecated alias (one-line notice).
- **Catalog-scan concept recall (B6):** `--mode catalog` emits the full slim catalog (filtered by
  `--system`/`--source-type`, registered-only, no raw tier) for AI read-and-pick — the sanctioned
  zero-dependency concept-recall fallback; wired into the lookup skill escalation (before any raw step).
  A weak top score (<15) prints a catalog suggestion (B5); 2-stage retrieve→AI-rerank is the codified
  precision pass.

P2 (GATED — DP-912-3, NOT applied with P1): optional local-only embedding hybrid
(`build_wiki_embeddings.py` + `embeddings.jsonl` sidecar + `--mode hybrid` RRF merge) behind an
Approved Deviation (`AI_WORK_CONTRACT` §6) with mandatory stdlib fallback = the P1 path; benchmark
gate baseline = P1 + catalog-scan (concept-cases PASS + 0 regress). Lexical self-test 0-FAIL and
first-3-keys curation discipline remain mandatory regardless — hybrid may only ADD recall, never
substitute curation.
