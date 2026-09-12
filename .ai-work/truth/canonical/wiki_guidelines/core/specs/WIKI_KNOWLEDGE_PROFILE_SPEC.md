# WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1

## 1. Purpose
Wiki Knowledge Profile là profile AI dùng chủ yếu cho:
- build Wiki
- update Wiki
- maintain Wiki

Nó giúp AI hiểu:
- knowledge này được build từ artifact nào
- nên có metadata/index/link gì
- knowledge này mô tả gì
- scope của knowledge này tới đâu
- knowledge này liên quan knowledge khác ra sao
- khi meta hiện tại thường là đủ
- khi nào vẫn cần refer source/profile thêm

Wiki Knowledge Profile không phải lớp nối task với knowledge.
Lớp đó vẫn là `Task Lens`.

---

## 2. Why this concept is used
Trong review trước, `Wiki Artifact Profile` và `Wiki Usage Profile` được thấy là khá gần nhau ở phía Knowledge.

Vì runtime thường sẽ chủ yếu dùng:
- Task Lens
- Wiki Meta / Index

nên giữ hai profile tách rời có thể làm tăng:
- số lượng khái niệm gần nhau
- risk chồng lấn scope
- maintenance overhead

Do đó, trong bản v0_1 này, hai profile đó được hợp nhất thành:
- `Wiki Knowledge Profile`

---

## 3. Scope in this sprint
Trong sprint này, Wiki Knowledge Profile được define ở mức minimal nhưng usable:
- source/build basis
- knowledge meaning/scope
- relation/sufficiency
- supplemental/reflection handling

Không đi sâu trong sprint này vào:
- profile engine
- inheritance system phức tạp
- automated profile conflict resolution
- advanced scoring/ranking

---

## 4. In-scope knowledge families

### 4.1. Requirement-side knowledge
- Raw Requirement knowledge
- Q&A clarification knowledge
- Requirement Definition knowledge

### 4.2. Main project knowledge
- Basic Design knowledge
- Detail Design knowledge
- IT Testcase knowledge
- Meeting Minutes knowledge
- Weekly Report knowledge

### 4.3. Supplemental knowledge
- findings
- open points
- clarification notes
- review comments summary
- pending decisions
- similar supplemental knowledge

---

## 5. Foundational principle
A Wiki Knowledge Profile should tell AI:
- how knowledge should be built from source artifacts
- what the resulting knowledge means
- what its scope is
- what related knowledge exists
- when current meta is usually enough
- when further source/profile consultation is needed

This profile is primarily a build/update/maintenance asset, not a first-line runtime consultation artifact.

---

## 6. Minimal profile structure

### 6.1. Identity
- `profile_id`
- `knowledge_type`
- `knowledge_family`
- `purpose`
- `when_to_use`

### 6.2. Source / Build Basis
- `source_artifact_types`
- `source_mapping_rule`
- `minimum_meta_fields`
- `object_extraction_targets`
- `recommended_index_keys`
- `required_links`
- `traceability_targets`

### 6.3. Knowledge Meaning / Scope
- `knowledge_summary`
- `knowledge_scope`
- `knowledge_in_scope`
- `knowledge_out_of_scope`

### 6.4. Relation / Sufficiency
- `related_knowledge_objects`
- `upstream_knowledge`
- `downstream_knowledge`
- `cross_reference_rule`
- `when_meta_is_usually_sufficient`
- `when_source_or_additional_knowledge_is_needed`

### 6.5. Supplemental / Reflection Handling
- `status_rule`
- `reflection_status_rule`
- `reflected_to_rule`
- `superseded_by_rule`

### 6.6. Missing / Unclear Cases
- `common_pitfalls`
- `if_missing_then_do`

---

## 7. Field explanations

### `source_artifact_types`
What source artifact classes this knowledge is primarily built from.

### `source_mapping_rule`
How source artifacts map into this knowledge type.

### `minimum_meta_fields`
What metadata is minimally needed so the knowledge is usable.

### `object_extraction_targets`
What domain entities/terms (function/screen/table names, IDs) should be extracted while building the knowledge — used to seed lookup keys and aliases. *(Entity extraction for findability — retired KO record: xem `Knowledge_Object_Model_Spec_MVP` §8.)*

### `recommended_index_keys`
What keys should make this knowledge findable later.

### `required_links`
What links should be made explicit.

### `knowledge_summary`
A concise explanation of what this knowledge describes.

### `knowledge_scope`
The intended coverage boundary of this knowledge.

### `knowledge_in_scope`
What kinds of content this knowledge should normally include.

### `knowledge_out_of_scope`
What should not be assumed to be covered by this knowledge.

### `related_knowledge_objects`
Other knowledge items / source artifacts that are meaningfully related. In the 2-layer model these relationships are recorded as the `## Related Sources` section (typed roles) inside the artifact meta (retired KO record — xem `Knowledge_Object_Model_Spec_MVP` §8).

### `upstream_knowledge`
Knowledge that often acts as a basis or prerequisite.

### `downstream_knowledge`
Knowledge commonly consulted next.

### `cross_reference_rule`
When AI should open related knowledge beyond the current one.

### `when_meta_is_usually_sufficient`
When the meta/index representation is usually enough without re-opening source/profile.

### `when_source_or_additional_knowledge_is_needed`
When AI should go beyond current meta.

---

## 8. Requirement-side rules

### 8.1. Raw Requirement knowledge
Should preserve:
- customer-origin input
- ambiguity or incompleteness
- item-level structure
- relation to later clarification and refinement

### 8.2. Q&A clarification knowledge
Should preserve:
- clarification intent
- answer state
- reflection status
- relation to raw requirement and requirement definition

### 8.3. Requirement Definition knowledge
Should preserve:
- refined/stabilized requirement layer
- relation to earlier raw inputs and Q&A clarification

### 8.4. Rule
The requirement chain:
- raw requirement
- Q&A clarification
- requirement definition

must not be flattened too early.

---

## 9. Supplemental knowledge rules

### 9.1. Why supplemental handling matters
For Q&A, findings, open points, and similar knowledge,
their usefulness depends not only on content, but on:
- status
- reflection status
- whether they remain operationally active

### 9.2. Required support
Knowledge profiles for these families should make explicit:
- how status is interpreted
- how reflection is tracked
- how reflected knowledge becomes less necessary for direct consultation by default

### 9.3. Rule
Do not assume:
- resolved = reflected
- historical = irrelevant

---

## 10. Relationship with Task Lens
Task Lens remains separate.

### Task Lens does:
- knowledge targeting
- routing
- search direction
- expansion direction

### Wiki Knowledge Profile does:
- build basis
- meaning/scope
- relation/sufficiency
- reflection handling

### Anti-confusion note
Task Lens tells AI **what knowledge to find**.
Wiki Knowledge Profile tells AI **how that knowledge is built and what it means**.

---

## 11. Relationship with Wiki Meta / Index
Wiki Meta / Index is the runtime-facing structured layer.
Wiki Knowledge Profile is one of the main inputs used to build that layer.

### Primary build role
Wiki Knowledge Profile should tell AI:
- what fields to build
- what links to build
- what relation/scope/reflection structure should be explicit

### Runtime role
Runtime should usually rely first on Wiki Meta / Index.
Profile reference should happen mainly when:
- meta is insufficient
- build/update is needed
- maintenance/debugging is needed

---

## 12. Minimal examples

### 12.1. Example — Detail Design knowledge profile
```yaml
profile_id: WKP-DD-001
knowledge_type: detail_design_knowledge
knowledge_family: main_project_knowledge
purpose: Build and maintain usable Wiki knowledge for detail design artifacts.
when_to_use:
  - build wiki from DD artifacts
  - update DD-related knowledge
source_artifact_types:
  - detail_design
source_mapping_rule:
  - map one DD artifact into artifact meta + `## Related Sources` relationships
minimum_meta_fields:
  - function_id
  - function_name
  - artifact_ref
  - revision
  - related_bd_ref
object_extraction_targets:
  - function
  - screen
  - api
  - table
recommended_index_keys:
  - function_id
  - function_name
  - screen_name
required_links:
  - related_basic_design
  - related_requirement_definition
traceability_targets:
  - upstream_requirement_definition
  - downstream_it_testcase
knowledge_summary: Detailed design knowledge for one function/screen/batch behavior.
knowledge_scope: Detailed implementation-facing design details within project design flow.
knowledge_in_scope:
  - structure
  - design rules
  - DB/API references
knowledge_out_of_scope:
  - fully authoritative business requirement interpretation without upstream confirmation
related_knowledge_objects:
  - basic_design_knowledge
  - requirement_definition_knowledge
  - it_testcase_knowledge
when_meta_is_usually_sufficient:
  - when link chain is complete and no unresolved issue remains
when_source_or_additional_knowledge_is_needed:
  - when unresolved Q&A/open points are still active
```

### 12.2. Example — Q&A clarification knowledge profile
```yaml
profile_id: WKP-QA-001
knowledge_type: qa_clarification_knowledge
knowledge_family: requirement_side_knowledge
purpose: Build and maintain requirement clarification knowledge with reflection awareness.
when_to_use:
  - build wiki from Q&A artifacts
  - maintain requirement clarification knowledge
source_artifact_types:
  - qa_list
source_mapping_rule:
  - map Q&A items into clarification knowledge items with status/reflection fields
minimum_meta_fields:
  - qa_item_id
  - related_requirement_ref
  - answer_state
  - reflection_status
object_extraction_targets:
  - requirement_item
  - clarification_topic
  - resolved_rule
recommended_index_keys:
  - qa_item_id
  - requirement_key
  - topic
required_links:
  - raw_requirement_item
  - requirement_definition
traceability_targets:
  - raw_requirement_to_refined_requirement_chain
knowledge_summary: Clarification knowledge bridging raw customer input and refined requirement definition.
knowledge_scope: Requirement refinement and clarification history relevant to project work.
knowledge_out_of_scope:
  - direct final replacement of requirement definition in all cases
status_rule:
  - must preserve active vs answered vs resolved states
reflection_status_rule:
  - must preserve not_reflected / partially_reflected / reflected distinction
when_meta_is_usually_sufficient:
  - when reflected status is clear and refined target is linked
when_source_or_additional_knowledge_is_needed:
  - when status/reflection is unclear or conflict exists
```

---

## 13. Out of scope for this sprint
- profile inheritance engine
- dynamic adaptation engine
- automated project-wide profile merger
- profile scoring system
- runtime dependency engine

---

## 14. Completion criteria for BL-03
BL-03 is considered done when:
- a minimal unified Wiki Knowledge Profile structure is clearly defined
- requirement-side special rules are explicitly captured
- supplemental/reflection-aware rules are explicitly captured
- the boundary with Task Lens is explicitly captured
- the relationship with Wiki Meta / Index is explicitly captured
