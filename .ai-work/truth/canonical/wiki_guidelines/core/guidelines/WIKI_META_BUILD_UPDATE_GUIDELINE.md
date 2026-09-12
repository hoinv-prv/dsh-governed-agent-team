# WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1

## Related Specs (Other Layer)
*(Added CR-G3 — AIP-EXEC-015 STEP-01)*

- **Related Sources mechanism:** `## Related Sources` section in each artifact meta (CR-AIWS-2026-05-004 Change 8 / CR-AIWS-2026-05-017)
  — typed cross-artifact relationships (retired KO record — xem `Knowledge_Object_Model_Spec_MVP` §8)
- **Controlled Promotion:** `product/methodology/ai_work_system/20_specs/Controlled_Knowledge_Promotion_Spec_MVP.md`
  — §CR-D8 Promotion trigger list is referenced by Appendix A §7E checklist

---

## 1. Purpose
Guideline này hướng dẫn cách AI và BrSE:
- build Wiki Meta / Index lần đầu từ artifacts hiện có
- update Wiki Meta / Index khi có thông tin mới
- giữ traceability giữa source artifact, canonical slot mapping, object/relation/meta records
- build/update meta một cách đủ cấu trúc, nhưng không over-synthesize ngoài grounding đã có

Guideline này nối trực tiếp giữa:
- Artifact Understanding
- Wiki Knowledge Profile
- Canonical slot mapping
- Project mapping pattern
- Project-customized meta enrichment

## 2. What this guideline is for
Guideline này dùng khi cần:
- tạo meta/index từ artifact đã được hiểu
- convert canonical mapping thành object/meta/link records
- update meta khi có artifact mới, relation mới, reflection status mới
- revise meta sau khi HUMAN confirm / change request / new evidence

Guideline này không phải:
- governance rule
- CR rule
- runtime retrieval rule

## 3. Foundational principles

### 3.1. Build from grounded layers first
Wiki Meta / Index nên được build trước hết từ:
- source artifact understanding
- canonical slot mapping
- confirmed project mapping pattern
- HUMAN-confirmed enrichment

### 3.2. Meta is a structured layer, not the source of truth itself
Meta giúp:
- search
- routing
- traceability
- relation visibility
- review efficiency

Nhưng không thay thế source artifact.

### 3.3. Update should be incremental when possible
Nếu chỉ có thay đổi nhỏ:
- thêm link
- thêm alias
- update reflection status
- mark superseded
thì nên update incremental, không rebuild toàn bộ không cần thiết.

### 3.4. Keep unresolved visible
Nếu chưa chắc:
- object mapping
- relation mapping
- reflection status
- alias certainty
thì nên giữ unresolved marker thay vì over-claim.

### 3.5. Respect project-customized enrichment
Meta cuối cùng không chỉ theo common baseline,
mà còn theo project-specific meta/routing/search needs đã được BrSE confirm.

## 4. Main inputs for meta build/update
A good meta build/update flow should consume some or all of:
- artifact_understanding
- canonical_slot_mapping
- wiki_knowledge_profile
- project_mapping_pattern
- project_customized_meta_rules
- supplemental_status_reflection_info
- existing_meta_records
- change_request (when canonical update is requested)

### Rule
If these layers disagree, AI should:
- prefer grounded and human-confirmed layers
- mark uncertainty explicitly
- avoid silent collapsing of conflicting interpretations

## 5. Main output targets
Meta build/update should produce or update some of:
- artifact meta record
- object meta record
- link/traceability record
- alias record
- supplemental status/reflection record
- lightweight sufficiency/reference hints
- unresolved marker record

## 6. Initial meta build flow
### Step 1 — Confirm build scope
AI xác định:
- đang build cho artifact nào / artifact family nào
- build object-level hay artifact-level hay cả hai
- project scope là gì
- current confidence level ra sao

### Step 2 — Read canonical mapping
AI dùng:
- canonical slot mapping
- source-to-slot mapping
để biết tài liệu hiện tại đang cover những khối tri thức nào.

### Step 3 — Derive object candidates
AI extract object candidates như:
- function
- screen
- batch
- API
- table
- business rule
- requirement item
- supplemental knowledge item

### Step 4 — Derive meta fields
AI tạo meta fields theo:
- common meta baseline
- project-customized enrichment
- artifact-type-specific needs

### Step 5 — Derive relations and traceability
AI tạo:
- artifact ↔ object links
- object ↔ object links
- upstream/downstream trace chain
- reflection/superseded relations
- relation hints to related artifacts

### Step 6 — Add unresolved markers if needed
Nếu object/alias/relation chưa chắc, tạo unresolved markers thay vì ép certainty.

### Step 7 — Emit build result
Output cần đủ để:
- review
- search
- later update
- canonical promotion if needed

## 7. Incremental meta update flow
### Step 1 — Identify update scope
AI xác định:
- record nào bị ảnh hưởng
- update loại gì
- cần touch object/meta/link/alias/status layer nào

### Step 2 — Check existing meta
AI kiểm tra:
- existing meta record
- existing links
- existing aliases
- current unresolved markers
- current supplemental status/reflection info

### Step 3 — Apply delta conservatively
AI chỉ update phần cần thiết:
- add link
- revise link
- add alias
- revise alias confidence
- update reflection status
- mark superseded
- add searchable field
- revise sufficiency hint

### Step 4 — Preserve provenance
Meta update cần giữ:
- source basis
- why updated
- what changed
- what remains unresolved

### Step 5 — Emit update summary
Nên có:
- changed records
- added records
- removed/deprecated records
- unresolved impacts

## 8. Canonical mapping → meta conversion rule
### 8.1. Mapping is not yet meta
Canonical slot mapping chỉ cho biết:
- tài liệu đang mô tả phần nào theo common understanding

AI vẫn cần chuyển tiếp từ mapping sang meta layer.

### 8.2. What should be converted
Từ canonical slots, AI nên derive:
- object candidates
- relation candidates
- searchable keys
- traceability targets
- likely dependency edges

### 8.3. Rule
Không phải canonical slot nào cũng phải trở thành một meta field riêng.
AI nên chọn:
- field có giá trị tìm kiếm
- field có giá trị route/review/link
- field được project customization yêu cầu

## 9. Project mapping pattern interaction rule
### 9.1. Reuse
Nếu project mapping pattern đủ mạnh,
AI nên reuse:
- section-to-slot expectations
- meta extraction patterns
- relation extraction patterns
- common aliases
- common searchable fields

### 9.2. Degrade gracefully
Nếu format khác đáng kể,
AI nên:
- reuse một phần
- re-evaluate phần còn lại
- keep lower confidence where needed

### 9.3. Update memory after build/update
Nếu build/update phát hiện pattern mới ổn định,
AI có thể propose update cho project mapping pattern.

## 10. Project-customized meta enrichment rule
### 10.1. Common baseline first
Meta build nên luôn có:
- common artifact/object/link baseline

### 10.2. Then merge project additions
Sau đó merge thêm:
- extra meta fields
- extra relation fields
- search/index-specific fields
- grouping tags
- dependency hints
- review hotspots

### 10.3. Rule
Nếu project-customized fields không có grounding đủ tốt,
AI nên:
- mark as proposed enrichment
- or keep unresolved
thay vì ghi cứng như fact đã chắc.

## 11. Supplemental artifact handling rule
### 11.1. Supplemental items need operational state
For Q&A, findings, open points, clarification notes, review comment summaries...
meta nên capture:
- status
- reflection_status
- reflected_to
- superseded_by
- whether direct future reading is still needed by default

### 11.2. Rule
Do not collapse:
- resolved
- reflected
- superseded
into a single generic state.

### 11.3. Update priority
Nếu có evidence mới liên quan supplemental state,
incremental update ở layer này thường nên được ưu tiên vì nó ảnh hưởng trực tiếp tới later consultation behavior.

## 12. Relation build rule
### 12.1. Main relation families
AI nên ưu tiên build các relation có giá trị dùng lại cao:
- upstream/downstream artifacts
- function ↔ API
- function ↔ DB table
- function ↔ popup/screen transition target
- requirement ↔ design ↔ testcase
- reflected_to / superseded_by

### 12.2. Rule
Nếu relation mới:
- grounded
- reusable
- reasonably placeable
thì nên explicit vào meta/link layer.

### 12.3. If uncertain
If relation is plausible but weak:
- unresolved marker
- weak candidate note
- or delayed update
is better than false certainty.

## 13. Suggested build/update outputs
### 13.1. Build output
- artifact_meta_records
- object_meta_records
- link_records
- alias_records
- supplemental_status_records
- unresolved_records
- build_summary

### 13.2. Update output
- updated_records
- new_records
- deprecated_records
- unresolved_changes
- update_summary

## 14. Suggested minimal review checklist
Before finalizing build/update result, AI/BrSE should quickly check:
1. Are key objects extracted?
2. Are key relations explicit enough?
3. Are useful search/index fields present?
4. Are unresolved parts preserved visibly?
5. Are project-specific enrichment needs reflected?
6. Has provenance/change basis stayed visible?

## 15. Common pitfalls
- turning every slot into too many low-value meta fields
- losing traceability between meta and source basis
- rebuilding too much for small changes
- over-reusing old mapping pattern after format drift
- hiding uncertainty too early
- flattening supplemental states too aggressively

## 16. If missing then do
If meta build/update is weak because inputs are insufficient:
- keep scope narrow
- add unresolved markers
- ask for missing artifact/sample if needed
- emit partial meta rather than false-complete meta
- suggest change request or later follow-up when appropriate

## 17. Completion criteria for BL-12
BL-12 is considered done when:
- initial meta build flow is clear
- incremental meta update flow is clear
- canonical mapping → meta conversion rule is clear
- project mapping pattern interaction is clear
- project-customized enrichment merge rule is clear
- supplemental handling rule is clear

---

# v0.9.8 Build/update compatibility addendum

Preserve current v0.9.2 field names and sections.

After meaningful Wiki Source Meta change:

```text
update meta → rebuild index → verify lookup
```

Do not edit generated index files manually.

`artifact_locator` should point to AIWS-readable source artifact. For original non-text files, use converted markdown/source representation and optionally record:

```markdown
- original_artifact_locator:
- conversion_note:
- representation_quality:
```

If markdown representation is insufficient, mark `source_representation_quality_issue`.

---

# CR-D4 Addendum — Split Design Pattern (2026-05-25)

Source: AIP-EXEC-014 STEP-03, CR-D4 from AIWS-Wiki-CR-Proposal-2026-05-25.md §3.

## 18. Split Design Pattern — Multi-artifact, Single-object

Áp dụng khi 1 business function/object được design thành nhiều files độc lập theo layer (phổ biến trong project MES/ERP: FE design, API design, BE design riêng nhau).

### 18.1. Core rule

**Rule:** Mỗi file vẫn có 1:1 meta riêng. Các meta cùng function được liên kết với nhau qua section
**`## Related Sources`** (role `companion_design` cho các layer cùng function) — không dùng field nào của
retired KO record (xem `Knowledge_Object_Model_Spec_MVP` §8; `build_wiki_source_meta.py` không emit field nào loại đó).

```markdown
# trong SRC-DD-CB01001-FE meta
## Related Sources
- **SRC-DD-CB01001-API** — role: companion_design — API design của cùng function cb01001
- **SRC-DD-CB01001-BE** — role: companion_design — BE design của cùng function cb01001
```

### 18.2. Canonical slot mapping per layer

| Layer | Artifact type | Primary canonical slots |
|-------|--------------|------------------------|
| FE | `detailed_design_fe` | `ui_ux_behavior`, `fe_event_logic`, `function_to_function_relation`, `screen_item_list` |
| API | `detailed_design_api` | `api_contract`, `dto_definition`, `error_http_behavior`, `request_response_schema` |
| BE | `detailed_design_be` | `be_processing_logic`, `db_data_access`, `source_table_decision`, `transaction_rule` |

AI nên derive `canonical_slots_used` cho mỗi meta từ `artifact_type` (ref: `Artifact_Type_Taxonomy_Spec_MVP`).

### 18.3. Cross-artifact relationships (via `## Related Sources`)

*(Revised CR-AIWS-2026-05-020.)*

Quan hệ giữa các metas của cùng function (và quan hệ upstream/downstream như BD → DD → test case) được
biểu diễn trực tiếp trong section `## Related Sources` của từng artifact meta, dùng role enum (vd
`companion_design` cho các layer cùng function, `upstream_input` cho BD → DD, `triggered_flow` cho DD → test case).
Không cơ chế aggregate nào của retired KO record (xem `Knowledge_Object_Model_Spec_MVP` §8).

**Typed registry + reverse query (CR-AIWS-2026-05-022, v0.4):** role là một **open registry** — base roles ∪
project `x:` extension; type lạ = WARNING only (không bao giờ block lint). Mỗi entry CÓ THỂ kèm confidence tùy chọn
`[asserted|inferred|candidate]` (default `asserted`). `## Related Sources` chỉ là **out-edges**; để hỏi
**reverse/impact** ("ai trỏ AT / ai gọi X") dùng projection `relations.jsonl` (build `build_relations.py`; query
opt-in `wiki_relations.py --relations`). Sau khi sửa `## Related Sources` → rebuild `relations.jsonl` (projection,
never hand-edit). Đây là **guidance kèm ví dụ**, KHÔNG phải hard lint (register membership chỉ warn). Spec:
Knowledge_Relationship Spec v0.4 §4 + §6A.

### 18.4. Project Mapping Pattern trigger

Lần đầu gặp split format → confirm pattern → lưu Project Mapping Pattern (xem §19). Khi có Project Mapping Pattern, lần tiếp theo build mass sẽ reuse thay vì re-inference.

### 18.5. Naming convention for split meta source IDs

```
SRC-<artifact_type_prefix>-<function_id>[-<layer>]

Examples:
SRC-BD-CB01001          (basic design)
SRC-DD-CB01001-FE       (detailed design FE)
SRC-DD-CB01001-API      (detailed design API)
SRC-DD-CB01001-BE       (detailed design BE)
SRC-UT-CB01001-FE       (unit test FE)
```

---

# CR-G4 Addendum — Appendix A: Wiki Source Meta Build Checklist (2026-05-25)

Source: AIP-EXEC-014 STEP-04, CR-G4 from AIWS-Wiki-CR-Proposal-2026-05-25.md §5.

## Appendix A: Wiki Source Meta Build Checklist

Checklist này được dùng khi build hoặc review Wiki Source Meta. Chia thành 5 categories (7A–7E) theo phase.

---

### 7A — Pre-build

Trước khi chạy `/aiws-wiki build-meta` hoặc `/aiws-wiki register`:

- [ ] **7A-1** Profile đã được chọn đúng cho artifact type này?
- [ ] **7A-2** Artifact type xác định được (hoặc đã qua classification gate nếu ambiguous)?
- [ ] **7A-3** Source file accessible và là AIWS-readable format (markdown hoặc đã convert)?
- [ ] **7A-4** Nếu binary source (Excel, PDF, Word) → đã convert và `representation_status` sẽ được set đúng (`partial` nếu conversion incomplete)?
- [ ] **7A-5** `source_id` convention nhất quán với naming pattern của project?
- [ ] **7A-6** Nếu split design format → đã xác định các metas cùng function để liên kết qua `## Related Sources` (role `companion_design`)?

---

### 7B — Post-build per-meta

Sau khi meta được tạo, trước khi rebuild index:

- [ ] **7B-1** `lookup_keys` có ít nhất 1 T1 key (unique identifier)?
  - Exception: methodology spec / external source → check `t1_exception_reason` present
- [ ] **7B-2** `task_relevant_tags` có ít nhất 1 tag (không empty)?
- [ ] **7B-3** `summary` đúng scope và không quá ngắn (đủ để AI hiểu artifact này là gì)?
- [ ] **7B-4** `## Related Sources` đã resolve (điền source_id thật / xóa role không dùng / xóa section nếu không có quan hệ) nếu artifact có quan hệ cross-artifact?
- [ ] **7B-5** `source_representation_status` đúng giá trị (`complete` / `partial` / `needs_review` / …)?
- [ ] **7B-6** `artifact_locator` trỏ đúng đến AIWS-readable file (không phải raw PDF/Excel)?
- [ ] **7B-7** T3 generic keywords không dùng standalone (pass Rule K-3)?

---

### 7C — Post-index verify

Sau khi rebuild index (`build_wiki_source_index.py`):

- [ ] **7C-1** Smoke test: lookup 3 loại keyword → đều hit đúng artifact này?
  - T1 keyword (unique ID) → exact match?
  - T2 keyword (domain term) → trong top-3 results?
  - T3 keyword (category) → trong top-10 results?
- [ ] **7C-2** Lint pass: `lint_wiki.py --sources-only` → 0 errors?
- [ ] **7C-3** Nếu sample-first mode: tất cả samples pass 7B + 7C trước khi mass build?

---

### 7D — Split design specific

Áp dụng khi 1 function được split thành nhiều files (FE/API/BE):

- [ ] **7D-1** Tất cả metas của cùng function liên kết với nhau qua `## Related Sources` (role `companion_design`)?
- [ ] **7D-2** Slot mapping đúng per layer (FE → ui_ux_behavior, API → api_contract, BE → be_processing_logic)?
- [ ] **7D-3** Source IDs follow naming convention `SRC-DD-<id>-FE/API/BE`?
- [ ] **7D-4** Có Project Mapping Pattern (PMP) cho format này chưa?
  - Nếu chưa → đây là candidate PMP (trigger `/aiws-wiki build-pattern`)

---

### 7E — Controlled Promotion trigger

Trước khi apply bất kỳ update nào, check nếu operation là Promotion trigger:

- [ ] **7E-1** Operation có trong Promotion trigger list không? (ref: `Controlled_Knowledge_Promotion_Spec_MVP` CR-D8 Addendum)
  - Set `knowledge_class: source_of_truth`?
  - Change `source_id` của meta đang referenced?
  - Split hoặc merge meta records?
  - Mark important artifact `deprecated`?
  - Change `related_artifact_refs` / `## Related Sources` relationships giữa major artifacts?
- [ ] **7E-2** Nếu YES → **STOP, không proceed với lightweight update**. Trigger Controlled Promotion flow (CR + wiki manager).
- [ ] **7E-3** Nếu NO → proceed với lightweight draft/review/apply như bình thường.

---

# CR-D3 Addendum — Sample-First Build Flow (2026-05-25)

Source: AIP-EXEC-015 STEP-01, CR-D3 from AIWS-Wiki-CR-Proposal-2026-05-25.md §3.

## 20. Sample-First Build Flow

Sample-First là best practice khi build Wiki Source Meta cho một **format mới hoặc chưa quen**. Tránh mass build trên format chưa validate quality.

### 20.1. Khi nào dùng Sample-First

| Tình huống | Sample-First? |
|---|---|
| Format mới chưa có Project Mapping Pattern (PMP) | ✅ Required |
| Format có PMP nhưng confidence = low | ✅ Required |
| Format đã có PMP (confidence = high/medium) | ❌ Skip — mass build OK |
| Format quen nhưng là lần đầu apply cho project mới | ⚠️ Optional (build 1 probe sample) |

### 20.2. Flow 6 bước

1. **Chọn 2–3 representative samples** — không chọn outlier, không chọn quá đơn giản. Đại diện cho phần lớn artifacts trong batch.
2. **Build meta cho samples** — chạy `/aiws-wiki build-meta` (hoặc `/aiws-wiki register`) với `--mode sample-first`.
3. **Check quality** — dùng checklist 7A–7D (§Appendix A). Tất cả samples phải pass trước khi tiếp.
4. **Test search** — chạy lookup với ≥3 loại keyword: (a) unique ID (T1), (b) domain term (T2), (c) category label (T3). Tất cả phải hit đúng.
5. **Review + fix profile/PMP** — nếu có issue trong bước 3–4, fix profile hoặc tạo Project Mapping Pattern trước khi mass build.
6. **Mass build** — chỉ tiến hành khi bước 3–4–5 đều OK.

### 20.3. Acceptance criteria để "OK mass build"

- Tất cả samples pass checklist 7B + 7C (§Appendix A)
- Lookup test với 3 loại keyword đều hit đúng
- BrSE/AI confirm Summary đúng scope ≥1 sample
- Project Mapping Pattern đã lưu nếu phát hiện stable pattern mới (xem §19)

### 20.4. State file

Khi dùng `--mode sample-first`, skill emit state file:
```
.ai-work/wiki_sources/_sample_review/<batch-id>.json
{
  "batch_id": "<id>",
  "samples_reviewed": ["SRC-...", "SRC-..."],
  "quality_pass": true|false,
  "lookup_pass": true|false,
  "pmp_created": true|false,
  "ready_for_mass": true|false,
  "reviewer_confirmed": false
}
```
Mass build chỉ được chạy khi `ready_for_mass: true` và `reviewer_confirmed: true`.

---

# CR-G1 Addendum — Operational Flow (Command-Level) (2026-05-25)

Source: AIP-EXEC-015 STEP-01, CR-G1 from AIWS-Wiki-CR-Proposal-2026-05-25.md §5.

## 21. Operational Flow (Command-Level)

Quick reference cho build meta từ đầu:

```bash
# 1. Check available profiles
ls .ai-work/wiki_sources/profiles/

# 2. Build meta (single file)
python .ai-work/tooling/build_wiki_source_meta.py \
  --artifact <path/to/artifact.md> \
  --source-id SRC-<TYPE>-<ID>[-<LAYER>] \
  --source-type <source_type> \
  --profile <path/to/profile.yml> \
  --title "<descriptive title>"
  # Or: --artifact-type <enum> to auto-derive profile+slots+tags (CR-D9)

# 3. Review meta manually (or via checklist 7B)
cat .ai-work/wiki_sources/meta/<source-id>.md

# 4. Rebuild index
python .ai-work/tooling/build_wiki_source_index.py

# 5. Verify lookup
python .ai-work/tooling/lookup_wiki_source.py --query "<keyword>"
python .ai-work/tooling/lookup_wiki_source.py --query "<function_id>"

# 6. Lint
python .ai-work/tooling/lint_wiki.py --sources-only
```

**Shortcut (ad-hoc single file):**
```bash
/aiws-wiki register   # skill với 3-stage flow: classify → confirm → build
```

**Shortcut (batch folder):**
```bash
/aiws-wiki register-batch  # skill với 4-stage flow (Wave 3)
```

---

## Semantic Override Args + Step 0 + Slim Meta — 2026-05-27 Addendum

**Source:** Applied from wiki_improvement_request.md Nhóm 3+6+9 (validated in vti-ai-work-system-demo, 2026-05-26).

### Step 0 — Semantic derivation (pre-tool mandatory)

Before running `build_wiki_source_meta.py`, derive the following from the artifact content:

| Arg | How to derive |
|---|---|
| `--summary` | Content from PMP `summary_extraction.target_sections`; enrich with doc metadata (version, function name/ID). |
| `--knowledge-targets` | Pick from profile list; add artifact-specific targets not in profile. |
| `--lookup-keys` | T1: unique IDs from text. T2: domain terms. Comma-separated. |

Skip Step 0 only when: artifact exactly matches profile's `format_signature` AND auto-extracted summary is acceptable.

### Updated CLI command (supersedes CR-G1 Operational Flow)

```bash
py .ai-work/tooling/build_wiki_source_meta.py \
  --artifact <path> \
  --source-id <SRC-ID> \
  --source-type <type> \
  --profile .ai-work/wiki_sources/profiles/<type>.yml \
  --title "..." \
  --summary "v1.0. <Purpose section content with function ID/name>." \
  --knowledge-targets "screen_spec,validation_rule,data_crud_spec" \
  --lookup-keys "F02,BD-F02,VAL-F02-01" \
  --hints-depth 2
```

Note: `py` is the Windows Python launcher. Use `python3` on Linux/macOS.

### Slim meta body format

Starting from this addendum, generated meta files omit the following body sections:

| Section removed | Reason |
|---|---|
| `## Runtime Use` | Duplicated frontmatter fields |
| `## Source Representation` | Duplicated frontmatter fields |
| `## Change Impact Hints` | Boilerplate by default (a MEANINGFUL one may be hand-authored — the reader shows it) |
| `## Cautions` | Generic boilerplate by default (a MEANINGFUL one may be hand-authored — e.g. an unreviewed-source caution — the reader shows it) |
| `## Profile Mapping` | Mirrors frontmatter `profile_id` — **enforced removed by CR-AIWS-2026-05-024** (builder no longer emits it; lint no longer requires it) |
| `## Artifact Reference` | Redundant with frontmatter `artifact_locator` |

**Sections retained (builder-generated):** Summary, Knowledge Targets, Lookup Keys, Source-Specific Hints, `## Related Sources` (CR-017 scaffold). A meta MAY additionally carry a hand-authored MEANINGFUL `## Cautions` / custom section.

Blank optional frontmatter fields omitted. Token cost: ~685 → ~300 tokens/meta.

> **Meta = AI orientation surface (CR-024 tenet):** a meta exists for AI to understand the source artifact + decide the
> next action, NOT as human prose. At meta-first, read it via `wiki_meta.py --view <id>` (the value-add reader): it
> prints Summary / Source-Specific Hints / Cautions / a **Related Sources signal** (out-edge count + types + a
> `wiki_relations.py --relations` pointer; NOT the full out-edges — out-only, CR-AIWS-2026-06-054) and SKIPS what the
> index already carries (Lookup Keys / Knowledge Targets / Profile Mapping). Keep every retained section terse + signal-dense.

### Profile vs PMP: which drives extraction

`build_wiki_source_meta.py` now loads the **Project Mapping Pattern** (`pmp_<profile_id>.yml`) when it exists alongside the profile. The PMP takes precedence for extraction logic. The profile continues to provide `knowledge_targets`. See Profile vs PMP Architecture addendum in `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE.md`.
