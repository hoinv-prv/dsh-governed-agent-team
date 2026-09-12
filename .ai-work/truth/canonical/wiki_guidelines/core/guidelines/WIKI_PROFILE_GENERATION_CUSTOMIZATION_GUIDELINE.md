# WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1

## 1. Purpose
Guideline này hướng dẫn cách AI và BrSE:
- tạo `Wiki Knowledge Profile` từ artifacts hiện có của dự án
- map tài liệu thực tế sang các **canonical slots** theo common understanding
- reuse mapping cho các tài liệu cùng format về sau
- customize metadata/relation/index fields theo nhu cầu tìm kiếm của dự án

Guideline này không giả định rằng tài liệu phải dùng đúng template name hoặc heading chuẩn.

---

## 2. Core idea
AI không chỉ làm:
- artifact type recognition

mà còn phải làm:
- **semantic structure understanding**
- **canonical slot mapping**
- **project-specific mapping pattern**
- **project-customized meta enrichment**

Tức là AI đọc tài liệu thực tế, hiểu nội dung theo common understanding, rồi map sang bộ đầu mục chuẩn/canonical để hỗ trợ:
- Wiki Meta / Index
- object linkage
- artifact linkage
- later task execution

---

## 3. When to use
Dùng guideline này khi:
- cần tạo initial Wiki Knowledge Profile cho một loại artifact trong dự án
- cần hiểu một template/project format chưa có mapping pattern mạnh
- cần review và customize cách AI extract metadata từ artifact
- cần chuyển từ artifact understanding sang profile/meta generation

Không dùng guideline này khi:
- chỉ update nhỏ một field meta đơn lẻ
- đã có mapping/profile ổn định và không cần thay đổi

---

## 4. Foundational principles

### 4.1. Do not depend on exact heading match
AI không được phụ thuộc vào việc tài liệu phải dùng đúng heading/template chuẩn.

### 4.2. Use common understanding first
AI nên tận dụng common/pretrained understanding để nhận ra:
- phần nào của tài liệu đang mô tả loại nội dung gì
- nó tương ứng với canonical slot nào

### 4.3. Keep grounding visible
Canonical mapping phải luôn traceable về:
- source sections
- source tables
- source notes
- reviewed human corrections

### 4.4. Human-confirmed mapping is stronger than one-shot inference
Proposal ban đầu của AI là cần thiết,
nhưng mapping dùng lại mạnh về sau nên dựa trên:
- HUMAN confirmation
- project-specific customization

### 4.5. Reuse mapping when format is stable
Nếu cùng project dùng format tương tự lặp lại,
AI không nên suy luận lại từ đầu mỗi lần.

---

## 5. Main outputs this guideline should enable
Một flow tốt theo guideline này nên tạo được:

- `canonical_slot_mapping`
- `slot_to_source_mapping`
- `project_mapping_pattern`
- `proposed_meta_fields`
- `proposed_relation_fields`
- `project_customized_meta_rules`
- `important_missing_slots`
- `confidence_note`

---

## 6. Canonical slots and common understanding

### 6.1. What is a canonical slot
Canonical slot là đầu mục chuẩn mà AI Work System dùng để hiểu artifact theo một khung common,
ví dụ với Detail Design:
- UI/UX behavior
- FE state/event logic
- API contract/DTO
- BE processing logic
- DB/data access logic
- validation/message/exception
- function-to-function relation
- function-to-DB relation
- function-to-API relation

### 6.2. Why slots matter
Nếu AI chỉ đọc raw structure của từng tài liệu,
thì:
- khó normalize knowledge
- khó build meta thống nhất
- khó link object/artifact về sau

Canonical slots giúp AI normalize tài liệu dự án vào một layer hiểu chung hơn.

### 6.3. Rule
Canonical slot mapping nên dựa trên:
- semantic meaning
- structure clues
- table intent
- relation to other artifacts
không chỉ dựa trên exact heading text.

---

## 7. Recommended generation flow

### Step 1 — Identify artifact type and scope
AI xác định:
- artifact family/type
- likely scope
- whether artifact is whole-pack, partial-pack, or split-by-layer

### Step 2 — Load or infer common expected slots
AI load common expected slots cho artifact type đó.
Ví dụ:
- Basic Design
- Detail Design
- Requirement Definition
- IT Testcase

### Step 3 — Perform semantic-to-canonical mapping
AI đọc tài liệu và map:
- source sections / tables / patterns
→ canonical slots

### Step 4 — Derive proposed meta and relations
Từ canonical mapping, AI propose:
- metadata fields
- relation fields
- object extraction targets
- searchable keys/index hints

### Step 5 — HUMAN review and confirmation
HUMAN có thể:
- confirm mapping
- sửa mapping
- thêm meta fields
- bỏ meta fields không cần
- hướng dẫn thêm project-specific requirements

### Step 6 — Save project mapping pattern
Sau khi confirm, AI lưu:
- mapping rules
- source-to-slot patterns
- project-specific enrichments
để lần sau reuse.

---

## 8. Low-confidence template handling rule

### 8.1. When to trigger
Nếu AI thấy template:
- khó map bằng common understanding
- structure lạ
- heading khó hiểu
- confidence thấp
thì AI được phép yêu cầu:
- một vài representative samples

### 8.2. Sample purpose
Sample dùng để:
- hiểu cấu trúc template
- tìm pattern lặp lại
- xác định heading/section/table nào thường map vào slot nào

### 8.3. Rule
AI không nên giả vờ hiểu chắc khi template fit thấp.
Nên nói rõ:
- confidence thấp
- cần sample để chuẩn hóa mapping

---

## 9. Proposal-and-confirm rule

### 9.1. What AI should propose
Sau khi đọc tài liệu, AI nên list:
- common/canonical slots đã nhận ra
- source → slot mapping
- metadata AI đề xuất đưa vào Wiki Meta
- relations AI đề xuất giữ
- missing/weak slots
- confidence note

### 9.2. What HUMAN can do
HUMAN có thể:
- confirm
- correct
- add project-specific guidance
- specify additional metadata to keep
- specify fields not worth storing
- ask AI to remap

### 9.3. Rule
Proposal là step trung gian quan trọng.
Không nên coi first-pass mapping là final mapping trong mọi trường hợp.

---

## 10. Project mapping pattern rule

### 10.1. Purpose
Sau lần đầu AI map tài liệu thành công,
cần lưu reusable mapping để:
- lần sau gặp tài liệu cùng format
- AI map nhanh hơn
- giảm need for re-inference

### 10.2. What should be remembered
Project mapping pattern nên lưu tối thiểu:
- artifact type
- format/style label
- source section patterns
- canonical slots used
- common section-to-slot mapping
- project-specific aliases
- project-specific enrichment rules
- confidence and exception notes

### 10.3. When to reuse
Reuse mạnh khi:
- format tương tự
- section pattern tương tự
- artifact class tương tự

### 10.4. When not to over-reuse
Nếu:
- format đổi đáng kể
- structure khác nhiều
- meaning của section bị thay đổi
thì AI nên degrade gracefully về semantic remapping,
không nên cưỡng ép reuse.

---

## 11. Project-customized meta enrichment rule

### 11.1. Why this is needed
Common canonical slots là cần thiết nhưng chưa đủ.
BrSE có thể cần thêm metadata để:
- dễ search
- dễ review
- dễ trace
- dễ connect object/artifact

### 11.2. What HUMAN may add
BrSE có thể yêu cầu thêm:
- extra meta fields
- extra relation fields
- extra index keys
- project tags
- hotspot fields for review/search
- business keywords
- dependency indicators
- screening or grouping labels

### 11.3. Rule
Final meta extraction should be:
- common canonical baseline
+ project-customized enrichment

### 11.4. Example additions
BrSE có thể thêm:
- subsystem keywords
- popup target screen IDs
- upstream/downstream function IDs
- related DB tables
- related APIs
- approval-sensitive flags
- search hotspot fields

---

## 12. Suggested output structure for BL-11 flow

### 12.1. Artifact understanding summary
- artifact type
- scope
- maturity
- confidence

### 12.2. Canonical slot mapping
- recognized slots
- source-to-slot mapping
- unmapped but notable sections
- missing important slots

### 12.3. Proposed meta package
- metadata fields
- relation fields
- index/search fields
- object extraction targets

### 12.4. Review/customization notes
- HUMAN confirmed items
- HUMAN added items
- HUMAN rejected items
- unresolved items

### 12.5. Project mapping pattern update
- reusable mapping note
- exceptions
- format signature

---

## 13. Suggested mapping pattern schema (minimal)

```yaml
mapping_pattern_id: PMP-DD-001
artifact_type: detail_design
project_format_label: dd_split_fe_api_be_v1
format_signature:
  - separate FE document
  - separate API document
  - separate BE document
canonical_slots_used:
  - ui_ux_behavior
  - fe_event_logic
  - api_contract
  - be_processing_logic
  - db_data_access
common_source_to_slot_mapping:
  - source_pattern: "Detailed Design FE"
    canonical_slots:
      - ui_ux_behavior
      - fe_event_logic
      - function_to_function_relation
  - source_pattern: "Detailed Design API"
    canonical_slots:
      - api_contract
      - dto_definition
      - error_http_behavior
  - source_pattern: "Detailed Design BE"
    canonical_slots:
      - be_processing_logic
      - db_data_access
      - source_table_decision
project_customized_meta_fields:
  - related_tables
  - related_apis
  - popup_target_functions
  - approval_sensitive_behavior
reuse_confidence: high
exceptions:
  - if FE doc also contains API stubs, re-check mapping manually
```

---

## 14. Common artifact examples

### 14.1. Basic Design
AI nên cố map các nhóm như:
- function overview
- screen/event behavior
- screen item details
- screen item states
- layout
- model definition
- check specification
- DB update intention / CRUD perspective

### 14.2. Detail Design
AI nên cố map các nhóm như:
- purpose / assumptions / dependencies
- UI/UX behavior
- FE state/event logic
- API contract / DTO
- BE processing logic
- DB/data retrieval/update logic
- validation/message/exception
- function relations
- DB/API relations
- FE/API/BE split

### 14.3. Requirement Definition
AI nên cố map các nhóm như:
- scope
- business rules
- input/output expectations
- edge cases
- out of scope
- relation to Q&A / raw requirement if available

---

## 15. Common pitfalls
- đòi exact heading match mới chịu map
- reuse mapping quá mạnh dù format đã đổi
- để first-pass AI proposal thành final too early
- không cho HUMAN thêm project-specific meta needs
- bỏ qua relation fields quan trọng cho search/review
- overfit vào một sample không đại diện

---

## 16. If missing then do
Nếu AI chưa map tốt:
- lower confidence explicitly
- request representative samples
- propose partial mapping first
- keep missing slots visible
- ask HUMAN to confirm or guide enrichment

---

## 17. Relationship with other sprint artifacts
Guideline này được thiết kế để nối:
- `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1`
- `WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1`
- `WIKI_META_INDEX_SPEC_v0_2`
- `AIP_WIKI_INTEGRATION_SPEC_v0_1`
- future Wiki meta build/update guideline

---

## 18. Completion criteria for BL-11
BL-11 is considered done when:
- semantic-to-canonical mapping flow is clear
- low-confidence template handling rule is clear
- proposal-and-confirm rule is clear
- project mapping pattern rule is clear
- project-customized meta enrichment rule is clear

---

# CR-G2 Addendum — Slot Mapping for Split-by-Layer Design (2026-05-25)

Source: AIP-EXEC-015 STEP-01, CR-G2 from AIWS-Wiki-CR-Proposal-2026-05-25.md §5.

## 19a. Slot Mapping for Split-by-Layer Design

Khi artifact là một trong các layer của split design (FE / API / BE), canonical slot mapping phải follow bảng dưới đây. Đây là operationalization của §7.3 (slot cho từng layer) trong context Project Mapping Pattern.

| Layer | Artifact type | Primary canonical slots | Secondary canonical slots |
|-------|--------------|------------------------|--------------------------|
| FE | `detailed_design_fe` | `ui_ux_behavior`, `fe_event_logic`, `screen_item_list` | `function_to_function_relation`, `validation_rule`, `popup_target` |
| API | `detailed_design_api` | `api_contract`, `dto_definition`, `error_http_behavior` | `request_response_schema`, `auth_rule` |
| BE | `detailed_design_be` | `be_processing_logic`, `db_data_access`, `source_table_decision` | `transaction_rule`, `error_handling` |
| Combined | `detailed_design_combined` | FE + API + BE primary slots | — |

**Phân biệt Primary vs Secondary:**
- Primary: luôn có trong meta nếu artifact có content
- Secondary: thêm khi BrSE confirm cần thiết cho search/review

**Cross-reference:** `WIKI_META_BUILD_UPDATE_GUIDELINE.md §18.2`, `Artifact_Type_Taxonomy_Spec_MVP.md §3`

---

# CR-D5 Addendum — Project Mapping Pattern: Schema + Lifecycle (2026-05-25)

Source: AIP-EXEC-014 STEP-03, CR-D5 from AIWS-Wiki-CR-Proposal-2026-05-25.md §3.

## 19. Project Mapping Pattern (PMP) — Schema và Lifecycle

Project Mapping Pattern là **active template** được apply tại build time, capture pattern đã observed + confirmed + reusable. Khác với "memory" (passive recall), PMP là structured schema được save và reuse có kiểm soát.

### 19.1. Storage path

```
.ai-work/wiki_sources/profiles/pmp_<profile_id>.yml
```

Ví dụ: `pmp_dd_split_fe_api_be.yml` (cho `profile_id: dd_split_fe_api_be`).

> **Canonical path (CR-AIWS-2026-06-021):** PMP sống **cạnh profile** ở `profiles/pmp_<profile_id>.yml` — đây là path tool đọc thật (`build_wiki_source_meta.py::_load_pmp`, L156) và khớp §22 + `GUIDELINE_INDEX_FLOW_NAVIGATOR` Step 1.5A. KHÔNG dùng thư mục con `mapping_patterns/` hay tên `PMP-<id>.yml` (path cũ tool không bao giờ đọc → PMP reuse fail âm thầm).

### 19.2. Schema (YAML)

```yaml
mapping_pattern_id: PMP-<PROJECT>-<FORMAT>-<VERSION>
artifact_type: <artifact_type enum>          # từ Artifact_Type_Taxonomy_Spec_MVP
project_format_label: <human-readable label> # e.g. dd_split_fe_api_be_v1
format_signature:
  - "<textual signature 1>"                  # pattern nhận ra format
  - "<textual signature 2>"
canonical_slots_used:
  - <slot_name>
common_source_to_slot_mapping:
  - source_pattern: "<section/heading pattern>"
    canonical_slots:
      - <slot_name>
project_customized_meta_fields:
  - field: <field_name>
    description: <description>
    example: <example_value>
reuse_confidence: high | medium | low
exceptions:
  - "<exception note>"
created_at: <YYYY-MM-DD>
confirmed_by: <human_id>
last_validated: <YYYY-MM-DD>
```

### 19.3. Lifecycle

> **Trigger point:** PMP lookup được thực hiện tự động tại Step 1.5A của registration flow (xem `GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1` Flow A). Không cần gọi PMP check thủ công nếu đang dùng flow chuẩn.

1. **Create:** Sau khi sample-first build confirm pattern mới stable → AI suggest tạo PMP → HUMAN confirm → save file
2. **Reuse:** Mass build đọc PMP matching format_signature → apply canonical slots + meta fields → skip re-inference
3. **Re-validate:** Khi format upstream thay đổi (phát hiện qua format drift hoặc explicit trigger) → `/aiws-wiki refresh-pattern`
4. **Deprecate:** Khi format không còn dùng → mark `reuse_confidence: low` + add deprecation note

### 19.4. When to trigger PMP creation

| Situation | Action |
|-----------|--------|
| Format mới chưa có PMP, sample-first passed, ≥2 artifacts | ✅ Suggest create PMP (`reuse_confidence: medium/high`) |
| Format mới chưa có PMP, chỉ 1 artifact | ⚠️ Hai nhánh — AI chọn theo context (xem §19.4a bên dưới) |
| Format đã có PMP matching | ❌ Skip — reuse existing |
| Format drift detected | ⚠️ Trigger re-validate PMP |

### 19.4a. Single-sample PMP decision

Khi chỉ có 1 artifact và chưa có PMP, AI đề xuất một trong hai hướng:

**Hướng 1 — Draft PMP ngay từ 1 mẫu** *(khuyến nghị khi format rõ ràng)*

1. AI phân tích heading/section structure của file
2. AI draft PMP với `reuse_confidence: low` và note `"single-sample draft"`
3. Trình HUMAN confirm — HUMAN có thể: (a) confirm, (b) cung cấp thêm mẫu, (c) bỏ qua
4. Nếu HUMAN confirm → save PMP, áp dụng cho các file tiếp theo
5. Khi thêm được ≥1 artifact cùng format → upgrade `reuse_confidence` lên `medium/high` via `/aiws-wiki refresh-pattern`

**Hướng 2 — Defer và yêu cầu thêm mẫu** *(khi format chưa rõ)*

1. AI báo: *"Format mới, chỉ 1 mẫu, cấu trúc không ổn định — khuyến nghị bổ sung thêm mẫu"*
2. BrSE cung cấp thêm file cùng loại → AI phân tích cả nhóm
3. Nếu pattern nhất quán → draft PMP với `reuse_confidence: medium`

**Criteria để AI chọn hướng:**

| Điều kiện | Hướng |
|-----------|-------|
| Heading rõ, ≥3 distinct sections, pattern generic | Hướng 1 |
| Heading mơ hồ, structure flat, nội dung highly artifact-specific | Hướng 2 |

### 19.5. Cross-references

- Skills: `/aiws-wiki build-pattern` (create), `/aiws-wiki refresh-pattern` (update) — Wave 2
- Taxonomy: `product/wiki_guidelines/core/specs/Artifact_Type_Taxonomy_Spec_MVP.md`
- Split Design: §18 (CR-D4) trong file này

---

## Profile vs PMP Architecture Clarification — 2026-05-27 Addendum

**Source:** Applied from wiki_improvement_request.md Nhóm 14 (validated in vti-ai-work-system-demo, 2026-05-26). Supersedes Phase 1 profile extension (Nhóm 11a, reverted).

### Architecture rule

| Artifact | Scope | Contains | Used by |
|---|---|---|---|
| **Profile** (`.ai-work/wiki_sources/profiles/<type>.yml`) | AIWS canonical — shared across all projects | `profile_id`, `description`, `knowledge_targets` | `build_wiki_source_meta.py` (knowledge_targets) |
| **PMP** (`.ai-work/wiki_sources/profiles/pmp_<type>.yml`) | Project-specific | `format_signature`, `summary_extraction`, `t1_key_extraction`, `hints_extraction`, `canonical_slot_mapping` | `build_wiki_source_meta.py` (extraction) |

### Why profiles must remain generic

Profile files ship with AIWS and are shared across all projects. Embedding project-specific extraction rules (heading names, ID patterns, naming conventions) into profiles would break reusability — Project B with a different BD template would need to fork the profile.

PMPs are the correct layer for project-specific extraction specs. They live alongside profiles and are automatically picked up by `build_wiki_source_meta.py` via `pmp_<profile_id>.yml` naming convention.

### Tool behavior (simplified)

```python
profile = _load_profile(profile_path)              # knowledge_targets
pmp = _load_pmp(profile_path)                      # format_signature, summary_extraction, ...
extraction_spec = pmp if pmp else profile          # PMP takes precedence for extraction
```

### Migration note for existing PMPs

Prior PMP files (CR-D5 schema: `format_signature`, `canonical_slot_mapping`) remain valid. Extended fields (`summary_extraction`, `hints_extraction`, `t1_key_extraction`) are additive — existing PMPs without them fall back gracefully. *(Cross-meta grouping đi qua `## Related Sources`; retired machinery — xem `Knowledge_Object_Model_Spec_MVP` §8.)*
