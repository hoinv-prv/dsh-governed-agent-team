# WIKI_CHANGE_REQUEST_SPEC_v0_1

> **Relation (CR-AIWS-2026-06-030):** This spec is the **wiki-meta-specialized profile** of the general `AIWS_Change_Request_Spec_MVP` (`product/methodology/ai_work_system/20_specs/`). It governs **wiki-meta** CRs — its `change_type`/`target_layer` enums and the §15 propagation checklist are wiki-meta-specific; the general spec governs all other canonical AIWS CRs and promotes/links this §15 checklist. See the general spec §18. **Approver (CR-AIWS-2026-06-031):** this profile's **Wiki-Manager** (Wiki changes, common to every project using AIWS) is distinct from the **AIWS-Product-Owner** (AIWS canonical docs/tools, AIWS project only). This profile keeps `reviewer_or_wiki_manager`.

## 1. Purpose
`Wiki Change Request` là cấu trúc tối thiểu để yêu cầu cập nhật canonical Wiki một cách:
- rõ target
- rõ source basis
- đủ thông tin để AI thực hiện update
- tránh conflict khi nhiều người cùng tham gia tạo/project knowledge

Trong sprint này, Change Request được define ở mức minimal nhưng usable.

---

## 2. Why this is needed
Artifacts của dự án do nhiều người cùng tạo và nhiều người có thể phát hiện thứ nên bổ sung vào Wiki.

Nếu AI hoặc từng member cập nhật thẳng canonical Wiki, dễ gặp:
- duplicate updates
- inconsistent wording
- conflicting links/meta
- đưa knowledge chưa đủ chín vào canonical layer

Do đó sprint này chốt flow:
- candidate
- change request
- wiki manager request AI update
- AI updates canonical Wiki

---

## 3. Foundational principles

### 3.1. Canonical Wiki is not updated directly by any ad hoc finding
AI không tự cập nhật canonical Wiki chỉ vì vừa phát hiện candidate hữu ích.

### 3.2. Wiki manager controls canonical update request
Member quản lý Wiki là người request AI thực hiện update Wiki theo change request.

### 3.3. Output-driven by default
Mặc định, Change Request nên được tạo từ:
- output đã sinh ra trong task theo AIP
- hoặc output hiện có trong interaction hiện tại

AI không nên suy luận thêm để làm CR, trừ khi:
- thực sự cần thiết
- và BrSE/HUMAN yêu cầu rõ

### 3.4. AI-executable CR
CR phải đủ thông tin để AI:
- hiểu đổi cái gì
- đổi ở đâu
- dựa trên nguồn nào
- đổi theo hướng nào
- biết mức tự do của AI tới đâu

---

## 4. In-scope change types
Minimal change types in this sprint:

- `add_artifact_publication`
- `add_metadata`
- `update_metadata`
- `add_linkage`
- `update_linkage`
- `add_curated_knowledge`
- `update_curated_knowledge`
- `mark_reflected_or_superseded`
- `deprecate_or_hide`
- `merge_or_consolidate`

This sprint does not need a complex change taxonomy beyond this.

---

## 5. Minimal CR structure

### 5.1. Request identity
- `cr_id`
- `title`
- `request_type`
- `requester`
- `reviewer_or_wiki_manager`
- `status`

### 5.2. Target
- `target_wiki_object_or_section`
- `target_layer`
  - object
  - index
  - alias_map
  - linkage
  - curated_knowledge
  - status_reflection
  - other
- `target_project_scope`

### 5.3. Requested change
- `change_type`
- `change_summary`
- `change_reason`
- `expected_outcome`

### 5.4. Source basis
- `source_artifact_refs`
- `source_excerpt_or_evidence_summary`
- `related_session_outputs`
- `related_notebook_entries`
- `related_existing_wiki_refs`

### 5.5. Proposed update direction
- `proposed_new_metadata`
- `proposed_links`
- `proposed_aliases`
- `proposed_summary_or_curated_note`
- `provenance_note`

### 5.6. Guardrails
- `do_not_change`
- `must_preserve`
- `allowed_ai_freedom`
  - exact_apply
  - light_cleanup_only
  - synthesis_allowed
- `needs_human_confirmation_after_draft`

### 5.7. Maturity / grounding
- `is_confirmed_from_project_source`
- `contains_inference`
- `needs_additional_verification`
- `confidence_level`

---

## 6. Field explanations

### `cr_id`
Unique identifier for the change request.

### `title`
Short human-readable summary.

### `request_type`
High-level type of request, usually `wiki_update`.

### `requester`
The person or role issuing the CR request.

### `reviewer_or_wiki_manager`
The person/role responsible for deciding whether AI should execute the change.

### `status`
Minimal statuses:
- `draft`
- `proposed`
- `approved_for_ai_update`
- `applied`
- `rejected`
- `superseded`

### `target_wiki_object_or_section`
Where the change should be applied.

### `target_layer`
What kind of wiki layer is being updated.

### `change_type`
What kind of operation is intended.

### `source_artifact_refs`
The main grounding references.

### `source_excerpt_or_evidence_summary`
Short evidence summary so AI does not need to rediscover the same basis from zero.

### `allowed_ai_freedom`
The degree of allowed synthesis/cleanup.

### `contains_inference`
Whether the requested change includes AI-added interpretation beyond direct project-grounded content.

---

## 7. Minimal mandatory fields
At the absolute minimum, an AI-executable CR should contain:
- `cr_id`
- `title`
- `target_wiki_object_or_section`
- `change_type`
- `change_summary`
- `change_reason`
- `source_artifact_refs`
- `source_excerpt_or_evidence_summary`
- `proposed_update_direction` *(can be a combined field in lightweight CR form)*
- `reviewer_or_wiki_manager`
- `status`

If these are missing, AI should prefer:
- draft only
- or request more information
rather than updating canonical Wiki directly

---

## 8. Lightweight CR form
For practical use, a lightweight CR form is allowed in this sprint as long as it still contains enough information.

Example compact fields:
- `cr_id`
- `title`
- `target`
- `change_type`
- `reason`
- `source_basis`
- `proposed_direction`
- `wiki_manager_status`

This sprint does not require every project to use the full verbose form if a compact form remains AI-executable.

---

## 9. Source-basis rule

### 9.1. Default source basis
CR should primarily be created from:
- AIP task outputs
- artifact understanding outputs
- review outputs
- brainstorming/research outputs already produced
- existing structured session outputs
- metadata/linkage candidates already surfaced

### 9.2. No-extra-reasoning by default
AI should not add extra reasoning just to make a CR look richer.

### 9.3. Exception
Additional reasoning is allowed only when:
- the current outputs are insufficient to make the CR executable
- and BrSE/HUMAN requests or permits it

### 9.4. Rule
If additional synthesis is added, it should be clearly separated from directly grounded source content.

---

## 10. CR and wiki manager flow

### 10.1. Minimal flow
1. candidate is identified
2. draft CR is created
3. wiki manager reviews / approves
4. wiki manager requests AI update
5. AI applies update
6. change summary can be recorded

### 10.2. Why wiki manager matters
This reduces:
- duplicate updates
- wording inconsistency
- direct conflict on canonical Wiki
- uncontrolled promotion of immature knowledge

---

## 11. Relation to AIP-driven and non-AIP interactions

### 11.1. AIP-driven flows
These are the main in-scope flows for clearly specified CR handling in this sprint.

### 11.2. Non-AIP interactions
Outside AIP, AI may still suggest useful wiki candidates,
but this sprint does not formalize the process in equal detail.
Canonical update still goes through CR and wiki manager control.

---

## 12. Examples

### 12.1. Example — add linkage
```yaml
cr_id: WCR-001
title: Add BD-DD-Testcase linkage for Booking Search
request_type: wiki_update
requester: wiki_manager
reviewer_or_wiki_manager: wiki_manager
status: approved_for_ai_update

target_wiki_object_or_section:
  - func_booking_search
  - artifact_links
target_layer: linkage
target_project_scope: project_alpha

change_type: add_linkage
change_summary: Add upstream/downstream links between BD, DD, and IT testcase for Booking Search.
change_reason: Repeated review tasks required manual tracing; reusable linkage should be added to Wiki.
expected_outcome: Function object can directly point to related BD/DD/testcase artifacts.

source_artifact_refs:
  - BD_BookingSearch_v1
  - DD_BookingSearch_v2
  - ITTC_BookingSearch_v1
source_excerpt_or_evidence_summary: >
  These three artifacts refer to the same Booking Search function and are already used together in review tasks.

proposed_links:
  - func_booking_search -> BD_BookingSearch_v1
  - func_booking_search -> DD_BookingSearch_v2
  - func_booking_search -> ITTC_BookingSearch_v1

provenance_note: project_grounded
allowed_ai_freedom: light_cleanup_only
needs_human_confirmation_after_draft: true
is_confirmed_from_project_source: true
contains_inference: false
needs_additional_verification: false
confidence_level: high
```

### 12.2. Example — mark reflected
```yaml
cr_id: WCR-002
title: Mark Q&A item QA_REQ_F04_003 as reflected into REQ_DEF_F04_v2
request_type: wiki_update
requester: wiki_manager
reviewer_or_wiki_manager: wiki_manager
status: approved_for_ai_update
target_wiki_object_or_section:
  - QA_REQ_F04_003
target_layer: status_reflection
target_project_scope: project_alpha
change_type: mark_reflected_or_superseded
change_summary: Mark this Q&A item as reflected into the refined requirement definition.
change_reason: Requirement clarification no longer needs default direct consultation once reflected.
source_artifact_refs:
  - QA_LIST_F04
  - REQ_DEF_F04_v2
source_excerpt_or_evidence_summary: >
  The refined requirement definition already contains the clarified rule from this Q&A item.
proposed_summary_or_curated_note: >
  reflection_status = reflected; reflected_to = REQ_DEF_F04_v2
provenance_note: project_grounded
allowed_ai_freedom: exact_apply
needs_human_confirmation_after_draft: false
is_confirmed_from_project_source: true
contains_inference: false
needs_additional_verification: false
confidence_level: medium
```

---

## 13. Out of scope for this sprint
- approval workflow engine
- automatic CR deduplication engine
- multi-stage CR routing
- conflict resolution engine
- UI design for CR management

---

## 14. Completion criteria for BL-06
BL-06 is considered done when:
- minimal CR structure is clearly defined
- AI-executable minimum fields are clearly defined
- output-driven/no-extra-reasoning-by-default rule is clearly captured
- wiki manager flow is clearly captured
- AIP-driven vs non-AIP treatment is clearly captured

---

## 15. Node-model / vocab-change propagation checklist
> Added by **CR-AIWS-2026-06-004** (object-node lint/skill propagation). Rationale: the two-kind-node / object layer
> (CR-023, refined CR-035) reached some enforcement points but not others — index-check, the `source_type` vocab, and
> the build-meta skill's object frontmatter example — which surfaced as broken lint for spec-correct object metas. When
> a CR changes the **node model** or a **validated vocabulary**, the change must propagate to every touchpoint
> together. Enumerate each below as **propagated** or **N/A (reason)** before apply:

- [ ] **`META_REQUIRED`** (per-meta required fields) — field added / removed / exempted?
- [ ] **`INDEX_REQUIRED`** (projected index required fields) — kept in sync with `META_REQUIRED`?
- [ ] **Vocabulary** — `SOURCE_TYPE_VOCAB` and/or the relevant **profile** (`wiki_sources/profiles/*.yml`, e.g. `knowledge_object`) updated? Prefer profile DATA over a hardcoded vocab when the open-union allows extend-without-CR.
- [ ] **Index-builder projection** (`build_wiki_source_index.py`, incl. `_omit_blank`) — does the new/removed field project correctly, or stay deliberately unprojected (e.g. `node_kind` per INV-7)?
- [ ] **Skill authoring example** (e.g. `aiws-wiki build-meta` object frontmatter) — shows every required field, no stale "omit X"?
- [ ] **Spec** (`Knowledge_Object_Model_Spec` / the relevant canonical doc) — the change is synced TO the spec, or the spec IS the change?
- [ ] **Golden fixture / CI guard** — a fixture exercises the change so a future propagation gap fails CI?

A CR touching the node model or a vocabulary MUST resolve every line above (propagated or N/A) before its apply AIP runs.
