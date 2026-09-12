# Artifact Type Taxonomy Spec — AI Work System MVP
Version: 0.2
Status: draft
Updated: 2026-05-31
Source: CR-D9, AIWS-Wiki-CR-Proposal-2026-05-25.md §11.4
Last update: v0.2 (CR-AIWS-2026-05-034) — added §2bis: the `source_type` spine + the many-to-one `artifact_type` → `source_type` map (artifact_type may be finer than source_type); documented profile-extension (CR-008) + local-scope exemption + `_unknown` as a classifier-only sentinel. Non-destructive: the fine §3 schemas are unchanged.

---

## 1. Purpose

Spec này định nghĩa **canonical taxonomy cho artifact types** được dùng trong AIWS Wiki Source Meta và các skills wiki.

Vấn đề cần giải quyết:
- Các skills hiện assume user đã biết `source_type` / `profile` khi gọi — không có canonical taxonomy để classifier tham chiếu
- Khi user gửi prompt tự do (`"đây là layout design của F04"`), AI không có spec để classify và disambiguate
- Thiếu mapping từ `artifact_type` → `default_profile`, `default_canonical_slots`, `default_task_relevant_tags`

Spec này là foundational input cho:
- `/aiws-wiki register` (CR-S11) — STAGE 2 classifier
- `/aiws-wiki register-batch` (CR-S10) — STAGE A format detection
- `build_wiki_source_meta.py` — `--artifact-type` flag *(planned — chưa build; xem banner §5, CR-AIWS-2026-08-057)*

---

## 2. Canonical Artifact Type Enum

Đây là initial set. Vocabulary có thể extend theo project. Tất cả values lowercase_underscore.

| artifact_type | Mô tả | Typical artifact family |
|---|---|---|
| `requirement_definition` | Requirement spec / feature definition / user story | requirement |
| `basic_design` | Basic design / check spec / high-level design | design |
| `detailed_design_fe` | Detailed design — Frontend layer | design |
| `detailed_design_api` | Detailed design — API/interface layer | design |
| `detailed_design_be` | Detailed design — Backend/processing layer | design |
| `detailed_design_combined` | Detailed design — Combined (không split by layer) | design |
| `test_case` | Integration test / E2E test case spec | test |
| `unit_test_spec` | Unit test spec / test design doc | test |
| `screen_mockup` | Screen wireframe / layout mockup / UI prototype | ui_ux |
| `db_schema` | Database schema / table design / ER diagram | data_model |
| `api_manual` | API reference manual / API specification doc | interface_api |
| `methodology_spec` | AIWS methodology spec / guideline doc | reference |
| `meeting_note` | Meeting minutes / Q&A record / decision record | project_control |
| `legacy_design` | Legacy/old-system design doc (umbrella) | reference |
| `_unknown` | Classifier không xác định được type | — |

**Note:** `_unknown` là fallback type khi classifier confidence thấp và user không thể disambiguate. Meta được build với `source_representation_status: needs_review`.

---

## 2bis. `source_type` spine và quan hệ `artifact_type` → `source_type` (CR-AIWS-2026-05-034)

Có **hai** vocabulary cho khái niệm "artifact này thuộc loại gì", phục vụ hai mục đích khác nhau — chúng **không trùng tập hợp**, mà liên hệ qua một **map nhiều-về-một**:

- **`artifact_type`** (spec này, §2) — nhãn **classifier** sinh ra; có thể **mịn** (vd `detailed_design_fe/_api/_be`) để drive `default_canonical_slots` + `classification_signals`.
- **`source_type`** (field trong Wiki Source Meta; validate bởi `lint_wiki.py SOURCE_TYPE_VOCAB`) — **xương sống thô** + **lint authority** duy nhất. Là **profile-extensible** (CR-AIWS-2026-05-008/IR-04): `allowed = base SOURCE_TYPE_VOCAB ∪ source_type khai báo trong `wiki_sources/profiles/*.yml``. Unknown source_type = **warning**, không phải error.

**Mô hình:** `source_type` là spine; mỗi `artifact_type` **MAP onto** đúng một `source_type` (many-to-one). Một `artifact_type` được phép mịn hơn `source_type` của nó. `source_type` KHÔNG cần là tập con literal của `artifact_type` và ngược lại.

**Map (`artifact_type` → `source_type`):**

| artifact_type | → source_type (spine) |
|---|---|
| `detailed_design_fe` / `detailed_design_api` / `detailed_design_be` / `detailed_design_combined` | `detail_design` |
| `test_case` | `test_spec` |
| `unit_test_spec` | `unit_test_spec` |
| `requirement_definition` / `basic_design` / `screen_mockup` / `db_schema` / `api_manual` / `methodology_spec` / `meeting_note` / `legacy_design` | (1:1, same value) |
| (reference standards — `naming_convention`, checklist, guideline) | `process_guideline` |
| (templates) | `process_template` |
| `_unknown` | — (classifier-only **sentinel**; NEVER a valid meta `source_type`) |

Ghi chú:
- **Non-destructive:** các fine artifact_type `detailed_design_*` / `test_case` ở §3 giữ nguyên schema (canonical_slots + classification_signals) — chỉ thêm quan hệ map, không gộp/xóa.
- **Local-scope source_types** (vd `asp_vendor_manual`, `magento_*`, `fujitsu_*`) là **namespace riêng**, khai báo qua local profiles — **EXEMPT** khỏi base vocab; KHÔNG migrate.
- Lookup theo source_type: `lookup_wiki_source.py --source-type <spine>` (xem `Task_Lens_Spec_MVP` §B bridge cho reference standards).

---

## 3. Per-Type Schema

Mỗi `artifact_type` có schema định nghĩa defaults và classification signals:

```yaml
artifact_type: <enum_value>

# Defaults cho meta build
default_profile: <profile_id>
default_canonical_slots:
  - <slot_name>
default_task_relevant_tags:
  - <tag>

# Classification signals (generic — không hardcode project-specific strings)
classification_signals:
  # Path/filename patterns (regex, case-insensitive)
  path_tokens:
    - <pattern>
  # Common heading patterns in document (regex)
  heading_patterns:
    - <pattern>
  # Content markers often found in this artifact type
  content_markers:
    - <marker>
  # Types easily confused with this one (disambiguation needed)
  ambiguous_with:
    - <other_artifact_type>
```

### 3.1. requirement_definition

```yaml
default_profile: requirement_spec
default_canonical_slots: [requirement_item, acceptance_criteria, business_rule, constraint]
default_task_relevant_tags: [requirement-relevant, review-relevant]
classification_signals:
  path_tokens: ["requirement", "要件", "spec.*requirement", "RD_", "req_"]
  heading_patterns: ["要件定義", "機能要件", "非機能要件", "acceptance criteria"]
  content_markers: ["shall", "must", "user story", "AS A.*I WANT", "受入条件"]
  ambiguous_with: [basic_design]
```

### 3.2. basic_design

```yaml
default_profile: design_doc
default_canonical_slots: [function_overview, flow_diagram, data_flow, interface_overview, constraint]
default_task_relevant_tags: [design-relevant, review-relevant]
classification_signals:
  path_tokens: ["basic.design", "check.spec", "BD_", "基本設計", "概要設計"]
  heading_patterns: ["基本設計", "処理概要", "機能概要", "flow", "overview"]
  content_markers: ["概要", "フロー", "シーケンス", "interface list", "機能一覧"]
  ambiguous_with: [requirement_definition, detailed_design_combined]
```

### 3.3. detailed_design_fe

```yaml
default_profile: design_doc
default_canonical_slots: [ui_ux_behavior, fe_event_logic, function_to_function_relation, screen_item_list, validation_rule]
default_task_relevant_tags: [detail-design-relevant, review-relevant, testcase-relevant]
classification_signals:
  path_tokens: ["detailed.*design.*fe", "dd.*fe", "詳細設計.*FE", "画面設計", "frontend"]
  heading_patterns: ["イベント一覧", "画面項目", "FE処理", "screen item", "event handler"]
  content_markers: ["popup_target", "field validation", "event handler", "画面遷移", "FE"]
  ambiguous_with: [screen_mockup, detailed_design_combined]
```

### 3.4. detailed_design_api

```yaml
default_profile: design_doc
default_canonical_slots: [api_contract, dto_definition, error_http_behavior, request_response_schema]
default_task_relevant_tags: [detail-design-relevant, review-relevant, testcase-relevant]
classification_signals:
  path_tokens: ["detailed.*design.*api", "dd.*api", "詳細設計.*API", "api.*design"]
  heading_patterns: ["API仕様", "リクエスト", "レスポンス", "HTTPステータス", "DTO"]
  content_markers: ["endpoint", "request body", "response", "HTTP status", "REST", "APIパス"]
  ambiguous_with: [api_manual, detailed_design_combined]
```

### 3.5. detailed_design_be

```yaml
default_profile: design_doc
default_canonical_slots: [be_processing_logic, db_data_access, source_table_decision, transaction_rule, error_handling]
default_task_relevant_tags: [detail-design-relevant, review-relevant, testcase-relevant]
classification_signals:
  path_tokens: ["detailed.*design.*be", "dd.*be", "詳細設計.*BE", "backend"]
  heading_patterns: ["処理フロー", "DB更新", "テーブル仕様", "BE処理", "業務ロジック"]
  content_markers: ["SQL", "テーブル名", "SELECT", "INSERT", "transaction", "エラー処理"]
  ambiguous_with: [basic_design, detailed_design_combined]
```

### 3.6. detailed_design_combined

```yaml
default_profile: design_doc
default_canonical_slots: [ui_ux_behavior, api_contract, be_processing_logic, db_data_access]
default_task_relevant_tags: [detail-design-relevant, review-relevant]
classification_signals:
  path_tokens: ["detailed.*design(?!.*(fe|api|be))", "詳細設計(?!.*(FE|API|BE))"]
  heading_patterns: ["詳細設計", "detail design"]
  content_markers: ["FE", "API", "BE", "DB"]
  ambiguous_with: [detailed_design_fe, detailed_design_api, detailed_design_be]
```

### 3.7. test_case

```yaml
default_profile: test_case
default_canonical_slots: [test_case_id, test_condition, expected_result, test_target_function]
default_task_relevant_tags: [testcase-relevant, review-relevant]
classification_signals:
  path_tokens: ["test.*case", "テストケース", "IT_", "E2E_", "integration.*test"]
  heading_patterns: ["テストケース", "テスト条件", "期待結果", "test case", "テスト一覧"]
  content_markers: ["テストID", "期待値", "前提条件", "pass/fail", "テスト手順"]
  ambiguous_with: [unit_test_spec]
```

### 3.8. unit_test_spec

```yaml
default_profile: test_case
default_canonical_slots: [unit_test_target, test_method, mock_setup, assertion]
default_task_relevant_tags: [testcase-relevant]
classification_signals:
  path_tokens: ["unit.*test", "UT_", "単体テスト"]
  heading_patterns: ["単体テスト", "unit test", "テスト対象メソッド"]
  content_markers: ["mock", "assert", "stub", "テスト対象", "カバレッジ"]
  ambiguous_with: [test_case]
```

### 3.9. screen_mockup

```yaml
default_profile: design_doc
default_canonical_slots: [screen_layout, ui_component_list, navigation_flow]
default_task_relevant_tags: [design-relevant, review-relevant]
classification_signals:
  path_tokens: ["mockup", "wireframe", "画面設計書", "layout", "prototype"]
  heading_patterns: ["画面レイアウト", "画面構成", "ナビゲーション"]
  content_markers: ["画面", "ボタン", "フォーム", "layout", "component"]
  ambiguous_with: [detailed_design_fe]
```

### 3.10. db_schema

```yaml
default_profile: data_model
default_canonical_slots: [table_definition, column_spec, index_spec, relation_diagram]
default_task_relevant_tags: [data-model-relevant, review-relevant]
classification_signals:
  path_tokens: ["db.*schema", "table.*design", "ER.*diagram", "データベース設計", "DB設計"]
  heading_patterns: ["テーブル定義", "カラム定義", "ER図", "table definition"]
  content_markers: ["PRIMARY KEY", "FOREIGN KEY", "NOT NULL", "型", "テーブル名", "CREATE TABLE"]
  ambiguous_with: [detailed_design_be]
```

### 3.11. api_manual

```yaml
default_profile: api_reference
default_canonical_slots: [api_endpoint_catalog, parameter_spec, auth_method, error_code_list]
default_task_relevant_tags: [api-relevant, reference-relevant]
classification_signals:
  path_tokens: ["api.*manual", "api.*reference", "API仕様書", "swagger", "openapi"]
  heading_patterns: ["API一覧", "エンドポイント", "認証", "エラーコード"]
  content_markers: ["GET", "POST", "PUT", "DELETE", "Authorization", "OpenAPI"]
  ambiguous_with: [detailed_design_api]
```

### 3.12. methodology_spec

```yaml
default_profile: methodology_spec
default_canonical_slots: [spec_objective, rule_list, definition, applicability]
default_task_relevant_tags: [methodology-relevant, reference-relevant]
classification_signals:
  path_tokens: [".*Spec.*MVP", ".*GUIDELINE.*", ".*RULE.*", "methodology"]
  heading_patterns: ["Purpose", "Objective", "Rules", "Spec", "Guideline"]
  content_markers: ["MUST", "SHOULD", "AI Work System", "spec version"]
  ambiguous_with: []
```

### 3.13. meeting_note

```yaml
default_profile: supplemental
default_canonical_slots: [agenda, decision, action_item, qa_record]
default_task_relevant_tags: [supplemental-relevant]
classification_signals:
  path_tokens: ["meeting", "qa_record", "議事録", "Q&A", "minutes"]
  heading_patterns: ["議事録", "決定事項", "アクションアイテム", "Q&A", "minutes"]
  content_markers: ["決定", "TODO", "確認事項", "アクション", "Q:", "A:"]
  ambiguous_with: []
```

### 3.14. legacy_design

```yaml
default_profile: legacy_reference
default_canonical_slots: [legacy_function_overview, legacy_data_model, migration_note]
default_task_relevant_tags: [legacy-relevant, reference-relevant]
classification_signals:
  path_tokens: ["legacy", "old.*system", "旧.*システム", "現行", "AS-IS"]
  heading_patterns: ["旧システム", "現行システム", "legacy", "AS-IS"]
  content_markers: ["現行", "旧", "COBOL", "移行", "AS-IS"]
  ambiguous_with: [basic_design]
```

---

## 4. Classification Rules

### 4.1. Heuristic Scoring

Classifier sử dụng scoring deterministic (không cần AI) dựa trên:

1. **path_tokens score:** Mỗi regex match trong file path/name → +3 điểm per match
2. **heading_patterns score:** Match trong top-5 headings → +2 điểm per match
3. **content_markers score:** Match trong first 500 chars → +1 điểm per match

Compute score cho mỗi artifact_type. Return top-3 candidates sorted by score descending.

### 4.2. Confidence Threshold — HUMAN Disambiguation Gate

**Condition kích hoạt HUMAN gate:**

```
confidence = top1_score / total_score  # normalized
gap = top1_score - top2_score

IF confidence < 0.75 OR gap < 0.15 × total_score:
    → AMBIGUOUS → trigger HUMAN disambiguation gate
```

**HUMAN gate behavior:**
- AI present top-3 candidates với scores và reasoning
- AI suggest most likely candidate với explanation
- User confirm hoặc chọn khác
- User có thể specify custom type (extend enum)

**AI có thể đề xuất** top candidate dựa trên content reasoning — nhưng KHÔNG tự apply mà không có user confirmation.

### 4.3. AI Content Reasoning (Optional Enhancement)

Nếu deterministic scoring không đủ, AI có thể supplement bằng semantic reasoning:
- Đọc một đoạn ngắn của artifact (first 500 chars + section headings)
- Reasoning về artifact intent và expected canonical slots
- Đề xuất type với confidence note

AI reasoning này là **advisory** — không replace HUMAN gate khi threshold không đạt.

---

## 5. Tooling Impact

> **PLANNED / NOT BUILT (CR-AIWS-2026-08-057):** toàn bộ §5 (5.1 `--artifact-type` flag · 5.2 lint enum check · 5.3 taxonomy export yml) mô tả tooling chưa tồn tại — 0 hit code, không có file export. Design intent, không phải hành vi. Build → CR riêng gỡ banner.

### 5.1. build_wiki_source_meta.py

Accept `--artifact-type <enum>` để auto-derive:
- `--profile` (default_profile)
- Canonical slots suggestion
- `task_relevant_tags`

```bash
python .ai-work/tooling/build_wiki_source_meta.py \
  --artifact docs/design/CB01001-detailed-design-fe.md \
  --source-id SRC-DD-CB01001-FE \
  --artifact-type detailed_design_fe \
  --title "Detailed Design FE — CB01001"
  # profile, canonical_slots, tags auto-derived from taxonomy
```

### 5.2. Lint rule

`lint_wiki.py` check `artifact_type ∈ enum` khi meta build:
- FAIL nếu `artifact_type` có giá trị không trong enum (typo, unsupported type)
- WARN nếu `artifact_type` là `_unknown` (cần follow-up)

### 5.3. Classification config

Taxonomy data export thành machine-readable `artifact_type_taxonomy.json` (or YAML) tại:
`.ai-work/wiki_sources/profiles/artifact_type_taxonomy.yml`

Dùng bởi `/aiws-wiki register` STAGE 2 classifier.

---

## 6. Extension Mechanism

Taxonomy là **controlled-but-extensible**:
- Core enum (§2) là canonical
- Project có thể thêm project-specific types dưới prefix `prj_`: ví dụ `prj_cobol_source`, `prj_screen_excel`
- Extension types không cần CR để thêm (project-scope only)
- Extension types nên document `default_profile` + `classification_signals` riêng trong project profile folder

---

## 7. Relationship to Other Specs

- **[WIKI_KNOWLEDGE_PROFILE_SPEC]** — `artifact_type` là input cho profile selection
- **[Lookup_Key_Strategy_Spec_MVP]** — `classification_signals.path_tokens` provides T2 hint candidates
- **[WIKI_META_INDEX_SPEC]** — Meta field `artifact_type` references this enum
- **[WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE]** — `Project Mapping Pattern` maps artifact_type → canonical slots

---

## 8. Open Questions

- **OP-Q1:** `detailed_design_combined` có cần split sub-types khi project có non-standard layer decomposition không? Tentative: no — use `_combined` + per-project canonical slot customization.
- **OP-Q2:** Confidence threshold 0.75 — calibrate after first 20 real test cases. Adjust per project domain nếu cần.

---

*Created: 2026-05-25 under AIP-EXEC-014 STEP-02. Source: CR-D9, AIWS-Wiki-CR-Proposal-2026-05-25.md §11.4.*
