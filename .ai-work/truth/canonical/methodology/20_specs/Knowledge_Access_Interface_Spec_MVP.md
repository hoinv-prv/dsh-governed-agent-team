# Knowledge Access Interface Spec for AI Work System MVP
Version: 0.1 (2-layer reconciliation note added CR-AIWS-2026-05-020)
Status: Canonical merged spec  
Scope: Knowledge Hub / Specs / Guidelines

> **2-layer reconciliation (CR-AIWS-2026-05-020 / AIP-EXEC-038):** In this spec, "object/concept" denotes the
> **abstract resolved concept** whose knowledge unit is an **artifact-level meta** (Lớp 1) — retired KO record:
> xem `Knowledge_Object_Model_Spec_MVP` §8. `expand_from_object` / `expand_by_link_category` operate over the
> meta's **`## Related Sources`** (typed roles); `retrieve_object_profile` reads the artifact meta;
> `inspect_source_anchor` opens the source artifact a meta represents. Capability names are kept for adapter stability.
>
> **Two-kind node update (CR-AIWS-2026-05-023 / CR-AIWS-2026-05-029):** `resolve_object_or_concept` may resolve to an
> **object-node meta (`node_kind=object`)** when one exists (else to the describing artifact metas); `retrieve_object_profile`
> reads that object-node (or artifact) meta — still **no retired-record shape** (INV-1/INV-2 — xem `Knowledge_Object_Model_Spec_MVP` §8).
> `expand_from_object` / `expand_by_link_category` operate over the **three registers** (documentary / representation
> `represented_by` / domain `x:`) of `## Related Sources` + `wiki_relations.py --relations` (reverse/impact, one-hop —
> unchanged). For an object-node (`artifact_locator=__OBJECT__`, no file), `inspect_source_anchor` means following the
> `represented_by` edges to the describing artifacts.

---

# 1. Purpose of this spec

Tài liệu này mô tả phần **canonical spec ở mức access interface** cho `Knowledge Access Interface` trong Knowledge Hub của AI Work System current canonical baseline.

Mục tiêu của tài liệu là:
- chốt lớp **access contract logic** giữa AI và Knowledge Hub
- làm rõ:
  - AI cần những capability logic nào để làm việc với Knowledge Hub
  - các tool/search engine/graph engine/RAG/MCP adapters nên map vào những capability nào
  - đâu là interface logic ổn định, đâu là implementation detail có thể thay đổi
- giữ Knowledge Hub:
  - tool-agnostic
  - adapter-friendly
  - AI-friendly
  - đủ rõ để support wiki-first, routing, expansion, và deep research có scope

Lưu ý:
- đây là logic interface spec
- không phải API implementation cụ thể
- không phải MCP schema cụ thể
- không phụ thuộc một tool duy nhất
- các backend/adapters có thể khác nhau, nhưng nên map được về contract này

---

# 2. What Knowledge Access Interface is / is not

## 2.1. What it is
Trong AI Work System, `Knowledge Access Interface` là:

> **tập capability logic mà AI dùng để truy cập, resolve, retrieve, expand, và kiểm tra độ sâu bằng chứng trong Knowledge Hub**

Nó trả lời câu hỏi:
- AI nên có những thao tác logic nào để làm việc với Hub?
- Tool nào cũng phải hỗ trợ tối thiểu những thao tác nào?

## 2.2. What it is not
Knowledge Access Interface **không phải**:
- raw search engine API
- vector DB API
- graph DB API
- MCP server schema cụ thể
- filesystem grep command set
- UI specification

Đây là **lớp contract trung gian**:
- phía trên: AI reasoning / routing / Working AIP flow
- phía dưới: adapters / search engines / graph engines / raw source access

---

# 3. Core design principles

## 3.1. Tool-agnostic first
Knowledge Hub không nên bị khóa vào:
- graph tool cụ thể
- RAG engine cụ thể
- MCP implementation cụ thể
- wiki app cụ thể

AI nên gọi capability logic.
Adapters/tooling sẽ lo mapping xuống backend cụ thể.

## 3.2. Capability-based, not backend-based
AI không nên nghĩ theo kiểu:
- “gọi graph DB”
- “gọi vector search”
- “gọi grep tool”

AI nên nghĩ theo kiểu:
- resolve object
- search knowledge
- retrieve related knowledge
- expand object
- inspect source depth

## 3.3. Wiki-first by default
Access interface phải support mạnh cho:
- curated/wiki layer
- canonical objects
- aliases
- natural-language expressions
- expansion links
- source anchors

Raw/source access là capability riêng, không phải default path đầu tiên.

## 3.4. Deep access must remain scoped
Interface phải cho phép:
- inspect source artifacts
- deep research
- grep/search raw zones

nhưng không khuyến khích full raw scan mặc định.

---

# 4. Capability groups

Tôi đề xuất chia access interface thành 6 nhóm capability logic:

1. **Resolve**
2. **Search**
3. **Retrieve**
4. **Expand**
5. **Inspect source**
6. **Report evidence depth**

---

# 5. Resolve capabilities

## 5.1. `resolve_object_or_concept`
### Purpose
Map input từ HUMAN hoặc runtime task vào canonical object/concept.

### Typical inputs
- target_object_ref
- target_object_type
- domain_hint
- scope_precedence
- task_lens

### Typical outputs
- candidate objects/concepts
- resolved canonical object/concept if clear
- ambiguity flag if needed

### Example use cases
- `BD` → `concept_basic_design`
- `chức năng 0001` → `func_order_entry_0001`
- `màn hình nhập order` → candidate function/screen object

## 5.2. `confirm_canonical_target`
### Purpose
Support step confirm with BrSE when input was non-canonical and candidate resolution exists.

### Notes
Đây không nhất thiết là tool call riêng,
nhưng là capability logic mà flow phải support.

---

# 6. Search capabilities

## 6.1. `search_knowledge`
### Purpose
Search curated Knowledge Hub objects/artifacts theo:
- text
- alias
- natural-language expression
- keyword
- task lens
- domain
- scope

### Inputs
- query text
- task lens
- domain
- scope precedence
- target object type if known

### Outputs
- ranked candidate knowledge objects/artifacts
- enough metadata for next routing step

## 6.2. `search_by_family_or_type`
### Purpose
Search theo:
- artifact family
- knowledge type
- object subtype
- concern/platform tags

### Example use cases
- tìm mọi `design` artifacts liên quan function A
- tìm `test` artifacts trong project scope
- tìm `reference` objects cho `review_design`

---

# 7. Retrieve capabilities

## 7.1. `retrieve_object_profile`
### Purpose
Lấy profile đầy đủ của 1 object/concept từ Knowledge Hub.

### Returned information may include
- canonical names
- aliases
- natural-language expressions
- related keywords
- task tags
- source anchors
- expansion links
- scope/domain/type metadata

## 7.2. `retrieve_artifact_summary`
### Purpose
Lấy summary hoặc curated representation của artifact object.

### Example
- summary của Basic Design object
- summary của API design artifact
- summary của ticket/backlog item

## 7.3. `retrieve_multiple_objects`
### Purpose
Lấy nhiều object cùng lúc theo ID/reference list khi routing đã có danh sách target cần xem.

---

# 8. Expand capabilities

## 8.1. `expand_from_object`
### Purpose
Từ một object/concept đã resolve, lấy các edge `## Related Sources` (3 registers — documentary/representation/domain) phù hợp.
*(Two-kind node — CR-029: expansion đi qua các typed role trong `## Related Sources` — không field nào của retired record (xem `Knowledge_Object_Model_Spec_MVP` §8). Reverse/impact = `wiki_relations.py --relations`.)*

### Inputs
- object_id  *(abstract input identifier = `source_id` của object-node khi resolve thành object; tên param giữ cho adapter stability — KHÔNG phải một field trong meta (INV-2 — xem `Knowledge_Object_Model_Spec_MVP` §8))*
- task_lens
- optional link category filters

### Outputs
- expansion candidates by link category
- optionally prioritized for current lens

## 8.2. `expand_by_link_category`
### Purpose
Lấy expansion cụ thể theo category.

### Example
- only `related_design`
- only `related_test`
- only `related_rule`

## 8.3. `suggest_next_expansion_steps`
### Purpose
Không chỉ trả về links, mà gợi ý:
- nên đi tiếp theo nhánh nào trước
- nhánh nào là optional
- nhánh nào là likely noise

### Design note
Capability này có thể do adapter hoặc AI reasoning layer đảm nhiệm,
nhưng logic interface nên support output shape phù hợp.

---

# 9. Source inspection capabilities

## 9.1. `inspect_source_anchor`
### Purpose
Từ một artifact meta (hoặc một source liệt kê trong `## Related Sources`), mở source artifact cụ thể tương ứng.
*(2-layer: meta trỏ tới source qua `artifact_locator` + `## Related Sources`; field KO `source_anchor` đã gỡ — CR-005/CR-020. Tên capability giữ nguyên để adapter ổn định.)*
*(Two-kind node — CR-029: với object-node (`node_kind=object`, `artifact_locator=__OBJECT__`, không có file), `inspect_source_anchor` = đi theo các edge `represented_by` tới các artifact mô tả object đó; với artifact node thì mở source như cũ.)*

### Example
- mở requirement doc gốc
- mở detail design file
- mở schema / interface spec
- mở source code file

## 9.2. `inspect_source_zone`
### Purpose
Đi sâu hơn vào raw/source layer trong một scope rõ ràng:
- folder
- group folder
- source zone

### Design rule
Không nên mặc định inspect toàn bộ codebase/docbase.
Capability này phải được dùng theo scoped deep-research rule.

## 9.3. `grep_or_search_within_source_zone`
### Purpose
Khi đã có source scope rõ, tìm tiếp trong zone đó.

### Example
- grep trong folder design
- grep trong folder backend
- grep trong folder api
- grep trong group folder liên quan function A

---

# 10. Evidence-depth capabilities

## 10.1. `get_evidence_depth_summary`
### Purpose
Cho AI biết kết quả hiện tại đang ở mức:
- `wiki_only`
- `source_checked`

### Output
- evidence level
- short explanation
- whether deeper source inspection is recommended

## 10.2. `list_unchecked_source_paths`
### Purpose
Cho AI biết:
- còn những source anchors/zones nào chưa kiểm tra
- nếu cần deep analysis thì nên đi đâu tiếp

---

# 11. Recommended minimal capability set for current phase

Tôi đề xuất current phase nên chốt tối thiểu các capability logic sau:

1. `resolve_object_or_concept`
2. `search_knowledge`
3. `search_by_family_or_type`
4. `retrieve_object_profile`
5. `retrieve_artifact_summary`
6. `expand_from_object`
7. `expand_by_link_category`
8. `inspect_source_anchor`
9. `inspect_source_zone`
10. `grep_or_search_within_source_zone`
11. `get_evidence_depth_summary`

Đây là bộ đủ mạnh để support:
- wiki-first
- routing
- expansion
- scoped deep research

---

# 12. Mapping guidance for adapters

## 12.1. Graph adapters
Graph/relationship tools nên map tốt vào:
- `resolve_object_or_concept`
- `retrieve_object_profile`
- `expand_from_object`
- `expand_by_link_category`

## 12.2. Search/RAG adapters
Search/RAG tools nên map tốt vào:
- `search_knowledge`
- `search_by_family_or_type`
- `retrieve_artifact_summary`

## 12.3. Raw source / grep adapters
Raw source tools nên map tốt vào:
- `inspect_source_anchor`
- `inspect_source_zone`
- `grep_or_search_within_source_zone`

## 12.4. MCP / orchestration adapters
MCP-style interfaces nên expose capability-oriented endpoints instead of backend-specific terms wherever possible.

---

# 13. Wiki-first and deep-research rules in interface usage

## 13.1. Default flow
Recommended default usage flow:

1. resolve object/concept
2. search knowledge
3. retrieve curated object/artifact summaries
4. expand through expansion links
5. check evidence depth
6. only then consider source inspection if needed

## 13.2. Required warning before deep jump
Nếu AI mới chỉ ở `wiki_only`,
AI phải warning điều đó trước khi đưa ra kết luận sâu.

## 13.3. Scoped deep research only
Nếu cần vượt wiki layer:
- AI không nên gọi raw/source zone search trên toàn repo mặc định
- AI nên đề xuất folder/group-folder/source-zone cho BrSE chọn trước

---

# 14. Sample interface usage patterns

## 14.1. Review detail design for Function A
1. `resolve_object_or_concept("chức năng A", type=function, lens=review_detail_design_function)`
2. `search_knowledge(query="detail design", domain=cobol_migration, scope=project-first)`
3. `retrieve_object_profile(func_order_entry_0001)`
4. `expand_from_object(func_order_entry_0001, lens=review_detail_design_function)`
5. `get_evidence_depth_summary()`
6. if still wiki-only and deep review needed:
   - propose source zones:
     - `/design/detail/`
     - `/api/`
     - `/db/`
   - then `inspect_source_zone(...)` after BrSE choice

## 14.2. Clarify what “BD” means
1. `resolve_object_or_concept("BD", type=concept)`
2. candidate found: `concept_basic_design`
3. confirm canonical target with BrSE
4. `retrieve_object_profile(concept_basic_design)`
5. `expand_from_object(concept_basic_design, lens=clarify_requirement_or_design_context)`

## 14.3. Investigate deep issue beyond wiki
1. retrieve relevant wiki objects
2. `get_evidence_depth_summary()` → `wiki_only`
3. AI warns current depth
4. AI proposes source zones:
   - backend folder
   - api folder
   - testcase folder
5. BrSE chooses
6. `inspect_source_zone(chosen_zone)`
7. `grep_or_search_within_source_zone(...)`

---

# 15. Quality rules

## Rule 1
AI should think in capabilities, not backend/tool names.

## Rule 2
Curated/wiki access should be the default first step.

## Rule 3
Resolution and retrieval should happen before broad raw source inspection.

## Rule 4
Expansion should use explicit object-level links when available.

## Rule 5
Evidence depth should always be inspectable and expressible.

## Rule 6
Raw/source access should be scoped before deep research proceeds.

## Rule 7
The interface should remain stable even if underlying tools change.

---

# 16. Proposed merged content summary

The Knowledge Hub design should be updated to reflect the following for Knowledge Access Interface:

1. Define a capability-based access interface between AI and Knowledge Hub.
2. Keep the interface tool-agnostic and backend-independent.
3. Organize capabilities into:
   - resolve
   - search
   - retrieve
   - expand
   - inspect source
   - report evidence depth
4. Use wiki-first as the default access path.
5. Preserve explicit source inspection capabilities for deeper analysis when needed.
6. Require scoped deep research rather than default full raw grep.
7. Allow adapters such as graph engines, search/RAG engines, MCP tools, and raw-source tools to map into the same logical capability set.

---

# 17. Delta status

This canonical spec is considered:
- mature enough for access-interface-spec-level review
- suitable as the baseline Knowledge Access Interface contract for Knowledge Hub upgrade work
- still open to later extension in areas such as:
  - richer output schemas per capability
  - standardized adapter mapping patterns
  - future MCP-specific profiles

---

# Knowledge-runtime sprint addendum — Wiki Meta / Index and minimal support registries

## Wiki Meta / Index role

For the current MVP direction, **Wiki Meta / Index** is the runtime-facing structured layer of Knowledge Hub.

It should support:

- identity / disambiguation
- short runtime summary
- routing hints
- linkage to curated knowledge objects
- source/provenance pointer
- lightweight readiness/status hints when useful

It is not:
- the whole Knowledge Hub
- source of truth
- a full metadata framework
- an execution artifact
- a decision engine

## Minimal support registries

The current sprint only requires two independent minimal registry supports:

1. **Alias registry**
   - maps alternate wording / shorthand / alias to canonical entry or object
   - supports lightweight disambiguation

2. **Source manifest**
   - maps source identity to raw/source location or reference
   - supports traceability and verification

Object inventory remains part of the Wiki Meta / Index direction and is not split into a separate registry in this sprint.

## Local representation note

Markdown frontmatter, JSON, or JSONL may be used as local working representations when useful.

This is not a final canonical storage decision.

---

# Personal Notebook access addendum

## Runtime relation

Personal Notebook may be consulted when HUMAN asks or when a task explicitly needs personal/cross-task notes.

It should not be consulted for every task automatically.

## Authority

Personal Notebook is not source of truth by default.

AI must read Personal Notebook notes according to their status/authority/source hints.

## Knowledge Hub relation

Personal Notebook is not Knowledge Hub.

If a Personal Notebook note appears reusable, AI may suggest controlled capture. AI must not auto-promote it.

---

# Source Understanding Artifact access addendum

## Runtime relation

Wiki Meta / Index may route to Source Understanding Artifacts when the task needs reusable source-derived understanding.

A typical access path is:

```text
Task/current step
  ↓
Task Lens
  ↓
Wiki Meta / Index
  ↓
Source Understanding Artifact
  ↓
raw/source when verification is required
```

## Usage rule

AI should check:
- status
- authority
- freshness
- source scope
- limitations
- verification triggers

before relying on a Source Understanding Artifact.

## Verification fallback

AI must return to raw/source when exact wording, final decision, implementation detail, conflict resolution, evidence, or source freshness check is required.

---

# Task Lens and Knowledge Access canonical addendum

Task Lens guides how AI uses Wiki Meta / Index and Knowledge Hub.

Task Lens is not metadata and does not store source pointers.

Wiki Meta / Index may include lens-related hints such as `related_lenses`, but these are optional hints and not hard filters.

No-Lens mode may still use Wiki Meta / Index and Knowledge Hub based on confirmed task intent.

Raw/source verification remains required when exactness, source evidence, conflict resolution, implementation detail, or freshness check matters.

---

# Controlled Knowledge Promotion addendum

Knowledge Hub / Wiki in AIWS is primarily for AI runtime retrieval, routing, reasoning, and verification.

Knowledge Hub add/update must be controlled.

Core rules:
- Notebook can store any.
- Candidate can be broad and intermediate.
- Wiki / Knowledge Hub requires clear Knowledge Value.
- Knowledge Value means helping AI work more efficiently and/or produce higher-quality outputs in AIWS.
- Every meaningful Knowledge Hub add/update should use the Knowledge Hub Add/Update Checklist.
- `knowledge-hub-add-update` skill must run the checklist before recommending `ready_to_add_update`.
- HUMAN guides/reviews/controls important add/update; AI is the primary runtime consumer.

Knowledge Hub is not a dumping ground and does not replace raw/source verification.

---

# v0.9.8 Wiki Meta / Index access addendum

Wiki Meta / Index remains the runtime access layer for Knowledge Hub/source artifacts.

Current concrete mechanism is preserved:

```text
Wiki Source Meta → Wiki Source Index → lookup_wiki_source.py → meta_locator → artifact_locator when needed
```

Rules:
- preserve current v0.9.2 field names and tooling
- use meta first, source artifact when needed
- `artifact_locator` points to AIWS-readable source artifact
- for non-text raw files, use converted markdown/source representation
- markdown/source representation must be sufficient for AI runtime understanding
- if not sufficient, mark `source_representation_quality_issue`
- use existing sections before adding new fields

---

# v0.9.9 Working AIP Connection access addendum

Knowledge access layers help AI find and select context.

Before non-trivial execution, selected context must be connected into Working AIP.

Knowledge access results should not be used as direct execution instructions without Working AIP readiness check.

---

# v0.9.10 Workspace Boundary addendum

Workspace may store selected source/context references.

Workspace notes are not source of truth.

If exact evidence is needed, use Knowledge Hub / Wiki Meta / source artifact.

Reusable Workspace findings should go through Capture Inbox and Controlled Knowledge Promotion, not directly into Knowledge Hub.

---

# v0.9.11 Minimal Runtime Testing addendum

Runtime testing checks for knowledge access:

- knowledge access results are candidate context, not automatic truth
- source verification is performed when needed
- local/common/baseline knowledge does not override project source of truth without review
- v0.9.2 baseline is compatibility reference, not design direction
