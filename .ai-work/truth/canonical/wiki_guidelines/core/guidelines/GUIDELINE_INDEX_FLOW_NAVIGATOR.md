# GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1

## 1. Purpose
Tài liệu này là **start point** cho BrSE/AI khi làm việc với sprint Wiki.

Mục tiêu:
- cho biết nên bắt đầu từ guideline nào
- giảm confusion giữa nhiều guideline/spec
- điều hướng theo:
  - objective hiện tại
  - tình trạng project
  - loại artifact
  - build/update/maintenance/use flow

Tài liệu này không thay thế từng guideline chi tiết.
Nó là **entry guide / navigation layer**.

---

## 2. When to use
Dùng tài liệu này khi:
- mới bắt đầu setup Wiki cho một project
- chưa biết nên đọc guideline nào trước
- cần định hướng flow:
  - artifact understanding
  - canonical mapping
  - meta build/update
  - AIP customization
  - candidate / CR / governance
- cần onboarding member mới vào flow Wiki

---

## 3. Core navigation principle
Hãy bắt đầu từ **objective hiện tại**, không bắt đầu bằng cách đọc toàn bộ mọi guideline.

### Objective-first navigation
- muốn hiểu artifact → đi vào Artifact Understanding flow
- muốn map artifact sang canonical understanding → đi vào Profile Generation / Customization flow
- muốn build/update meta → đi vào Meta Build / Update flow
- muốn customize AIP template → đi vào AIP Template Customization flow
- muốn candidate / CR / canonical update → đi vào Wiki update governance flow

---

## 4. Quick entry map

### 4.0. Tôi muốn build Wiki cho dự án lần đầu (first build, từ đầu)
Đọc trước:
1. `PROJECT_WIKI_BUILDUP_GUIDELINE_v0_1` (11-step gated method + Appendix G = build the project's maintenance/sync command)

Chạy `/aiws-wiki bootstrap` (one-time bootstrap: explore shape + Q&A → instantiate a fixed 12-step AIP skeleton → delegate to `/aiws-aip create`). Maintenance về sau (whole-repo refresh) build per project theo Appendix G.

### 4.1. Tôi muốn hiểu tài liệu hiện có của dự án
Đọc trước:
1. `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1`
2. `PROMPT_ARTIFACT_UNDERSTANDING_v0_1`
3. `PROMPT_REVISE_ARTIFACT_UNDERSTANDING_v0_1`

Nếu artifact là supplemental hoặc có Q&A/findings/open points:
- đọc thêm `SUPPLEMENTAL_ARTIFACT_STATUS_REFLECTION_MODEL_v0_1`

### 4.2. Tôi muốn map tài liệu sang đầu mục chuẩn để dùng lại về sau
Đọc trước:
1. `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1`
2. `PROMPT_GENERATE_CANONICAL_SLOT_MAPPING_v0_1`
3. `PROMPT_REVIEW_CONFIRM_MAPPING_AND_META_v0_1`

### 4.3. Tôi muốn build meta/index từ tài liệu đã hiểu
Đọc trước:
1. `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`
2. `PROMPT_BUILD_WIKI_META_FROM_MAPPING_v0_1`

### 4.4. Tôi muốn update meta/index khi có thay đổi mới
Đọc trước:
1. `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`
2. `PROMPT_UPDATE_WIKI_META_INCREMENTALLY_v0_1`

### 4.5. Tôi muốn biết khi nào nên suggest đưa thông tin vào Wiki
Đọc trước:
1. `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1`
2. `AIP_WIKI_INTEGRATION_SPEC_v0_1`
3. `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`

### 4.6. Tôi muốn update canonical Wiki đúng flow
Đọc trước:
1. `WIKI_CHANGE_REQUEST_SPEC_v0_1`
2. `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`
3. `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`

### 4.7. Tôi muốn customize AIP template cho project
Đọc trước:
1. `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1`
2. `PROMPT_CUSTOMIZE_AIP_TEMPLATE_FROM_PRESET_v0_1`
3. `PROMPT_REVISE_AIP_TEMPLATE_CUSTOMIZATION_v0_1`
4. `AIP_WIKI_INTEGRATION_SPEC_v0_1`

### 4.8. Tôi có nhiều wiki sources có khái niệm/thuật ngữ trùng nhau
Đọc trước:
1. `WIKI_SOURCE_DISAMBIGUATION_GUIDELINE_v0_1`

Áp dụng khi: đăng ký ≥ 2 sources từ cùng vendor/domain; AI có nguy cơ chọn sai nguồn do volume bias.

### 4.9. Tôi muốn biết impact/reverse — "ai trỏ AT / ai gọi nguồn X" (CR-022)
Đọc trước:
1. `Knowledge_Expansion_Link_Spec_MVP` v0.4 §6A (`relations.jsonl` projection)
2. Tool: `python .ai-work/tooling/wiki_relations.py --relations <source_id>` (out + IN edges) · build bằng `build_relations.py`

Áp dụng khi: cần impact analysis / reverse dependency (`## Related Sources` chỉ có out-edges). Opt-in, one-hop;
`lookup_wiki_source.py` (discovery) không đổi.

---

## 5. Main flow navigator

## Flow A — Project already has artifacts, and we want to initialize Wiki
Bước khuyến nghị:
1. Artifact Understanding
2. Profile & PMP existence check *(bắt buộc — xem Step 1.5A bên dưới)*
3. Canonical slot mapping
4. HUMAN review / confirm
5. Project mapping pattern
6. Meta build
7. Candidate / CR / canonical update if needed

### Use these docs
- `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1`
- `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1` — §19 (PMP lifecycle, §19.4a single-sample)
- `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`
- `WIKI_CHANGE_REQUEST_SPEC_v0_1`
- `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`

### Step 1.5A — Profile & PMP existence check

Trước khi build meta cho bất kỳ tài liệu nào, AI thực hiện:

1. Xác định `artifact_type` của tài liệu (từ kết quả Artifact Understanding)
2. Kiểm tra profile file: `.ai-work/wiki_sources/profiles/<artifact_type>.yml`
   - Có → ghi nhận `profile_id`, tiếp tục
   - Không có → báo HUMAN: *"Profile cho artifact type `<type>` chưa tồn tại. Đây là profile canonical do AIWS team quản lý — cần tạo mới hoặc mapping sang type gần nhất."* → đợi HUMAN quyết định
3. Kiểm tra PMP file: `.ai-work/wiki_sources/profiles/pmp_<artifact_type>.yml`
   - Có → load PMP, áp dụng cho meta build → skip PMP creation flow
   - Không có → trigger `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1 §19.4` flow
4. Sau khi cả profile và PMP đã resolve → tiến hành meta build với đầy đủ context

**Điều kiện bỏ qua bước này:**
- BrSE chỉ định rõ "bỏ qua PMP check" (khi đã biết không có PMP và cố ý làm relaxed meta)
- Artifact type là `unknown` / `misc` (không có profile canonical → ghi chú và tiếp tục)

---

## Flow B — New deliverable artifact created under AIP
Bước khuyến nghị:
1. Check deliverable vs working
2. Check wiki-eligible vs not
3. Suggest candidate if relevant
4. If BrSE agrees, prepare handoff
5. Go through CR / governance if canonical update is wanted

### Use these docs
- `AIP_WIKI_INTEGRATION_SPEC_v0_1`
- `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1`
- `WIKI_CHANGE_REQUEST_SPEC_v0_1`
- `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`

---

## Flow C — Existing Wiki meta is weak and needs improvement
Bước khuyến nghị:
1. Re-open artifact understanding if needed
2. Re-check canonical mapping
3. Update meta incrementally
4. Preserve unresolved markers
5. Update mapping pattern if a stable pattern is discovered

### Use these docs
- `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1`
- `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1`
- `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`

---

## Flow D — Template/project format is unfamiliar
Bước khuyến nghị:
1. Do first-pass semantic mapping
2. If confidence low, ask for representative samples
3. Generate proposal
4. HUMAN confirm / correct
5. Save project mapping pattern
6. Then build meta or customize AIP as needed

### Use these docs
- `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1`
- `PROMPT_GENERATE_CANONICAL_SLOT_MAPPING_v0_1`
- `PROMPT_REVIEW_CONFIRM_MAPPING_AND_META_v0_1`

---

## Flow E — Need project-customized AIP template
Bước khuyến nghị:
1. Select nearest preset
2. Confirm task understanding
3. Apply project profile constraints
4. Add minimal Wiki-first behavior where relevant
5. HUMAN review
6. Save project-customized template rule

### Use these docs
- `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1`
- `PROMPT_CUSTOMIZE_AIP_TEMPLATE_FROM_PRESET_v0_1`
- `PROMPT_REVISE_AIP_TEMPLATE_CUSTOMIZATION_v0_1`

---

## 6. Objective-to-document matrix

| Objective | Primary guideline(s) | Supporting docs |
|---|---|---|
| Understand artifact | `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1` | artifact understanding prompts, supplemental model |
| Normalize artifact into canonical understanding | `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1` | canonical mapping prompts |
| Build meta/index | `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1` | meta build prompt |
| Update meta/index | `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1` | incremental update prompt |
| Suggest Wiki candidate | `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1` | AIP integration, governance |
| Create CR for canonical update | `WIKI_CHANGE_REQUEST_SPEC_v0_1` | governance rule |
| Control canonical update | `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1` | CR spec |
| Customize AIP template | `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1` | AIP customization prompts, AIP-Wiki integration |
| Handle overlapping terms across multiple sources | `WIKI_SOURCE_DISAMBIGUATION_GUIDELINE_v0_1` | (self-contained) |
| Find reverse / impact (who points AT / calls X) | `Knowledge_Expansion_Link_Spec_MVP` v0.4 (§6A) | `wiki_relations.py --relations` · `build_relations.py` |
| Nhận một **package code** từ dự án ngoài vào canonical tooling | `EXTERNAL_CODE_INTAKE_GUIDELINE` | `AIWS_Change_Request_Spec_MVP` §11/§18 · `tooling_authoring_conventions` Rule 11/13 |

---

## 7. Suggested reading order for a new project
Nếu project chưa có setup Wiki rõ, thứ tự khuyến nghị là:

1. `GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1`
2. `ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1`
3. `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1`
4. `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`
5. `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1`
6. `WIKI_CHANGE_REQUEST_SPEC_v0_1`
7. `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`
8. `AIP_WIKI_INTEGRATION_SPEC_v0_1`
9. `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1`

---

## 8. Anti-confusion notes

### 8.1. Artifact Understanding vs Canonical Mapping
- Artifact Understanding = hiểu artifact hiện có
- Canonical Mapping = map artifact đó sang common slots để normalize

### 8.2. Canonical Mapping vs Meta Build
- Canonical Mapping = hiểu nội dung theo đầu mục chuẩn
- Meta Build = convert phần hữu ích sang records/links/aliases/search fields

### 8.3. Candidate vs Canonical Update
- Candidate = đáng cân nhắc cho Wiki
- Canonical Update = đã đi qua CR + governance

### 8.4. AIP-Wiki Integration vs Governance
- AIP-Wiki Integration = AIP nên dùng Wiki và handoff vào Wiki thế nào
- Governance = ai được update canonical Wiki và qua flow nào

### 8.5. Task Lens vs AIP Template
- Task Lens = route task → knowledge
- AIP Template = guide execution flow of the task

---

## 9. Minimal “what should I do now?” navigator

### If you say:
- “Tôi muốn hiểu bộ tài liệu hiện có”
  - Start at Artifact Understanding

- “Tôi muốn chuẩn hóa cách AI hiểu loại tài liệu này”
  - Start at Wiki Profile Generation / Customization

- “Tôi muốn tạo meta để AI tìm lại nhanh hơn”
  - Start at Wiki Meta Build / Update

- “Tôi muốn biết có nên add thứ này vào Wiki không”
  - Start at Wiki Candidate Suggestion Rule

- “Tôi muốn update canonical Wiki”
  - Start at Wiki Change Request + Governance

- “Tôi muốn AIP của project dùng Wiki đúng hơn”
  - Start at AIP Template Customization + AIP-Wiki Integration

---

## 10. Completion criteria for BL-14
BL-14 is considered done when:
- objective-first navigation is clear
- main flows are clear
- objective-to-document mapping is clear
- reading order for a new project is clear
- anti-confusion notes are clear

---

# v0.9.8 Wiki Meta / Index runtime guidance

When working with Wiki Meta / Index, refer to:

- `core/specs/WIKI_META_INDEX_SPEC.md`
- `core/guidelines/WIKI_META_INDEX_RUNTIME_GUIDANCE.md`
- `appendix/examples/WIKI_META_INDEX_SAMPLE_RECORDS_APPENDIX.md`

Key flow:

```text
lookup_wiki_source.py → meta_locator → artifact_locator when needed
```
