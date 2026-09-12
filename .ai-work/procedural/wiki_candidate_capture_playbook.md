# Wiki / Knowledge Hub Candidate Capture Playbook

Operational quick-reference: **bắt gì · capture lúc nào · ghi thế nào**.
Chi tiết + ví dụ từng trigger: file riêng trong [`capture_triggers/`](capture_triggers/) — mỗi dòng bảng dưới map sẵn **case → file**.
Eligibility theory: `product/wiki_guidelines/core/specs/WIKI_CANDIDATE_SUGGESTION_RULE.md`.

## Cách tổ chức (đọc 1 lần)
- File này là **index hành động**: bảng 20 trigger + record format + closing check. Đủ để AI quyết định capture mà không cần mở gì thêm.
- Cần chi tiết/ví dụ của 1 trigger → cột `# · fragment` đã chỉ sẵn file → Read **đúng** `capture_triggers/<slug>.md`, không mò, không load cả khối.
- **Thêm use-case mới:** (1) tạo `capture_triggers/<new_slug>.md` theo template; (2) thêm 1 dòng vào bảng dưới. KHÔNG đụng fragment cũ.

## Scope
- Active trong **mọi AIP execution** (bất cứ task nào cần workspace), không chỉ khi `/aiws-aip run`.
- AI **chỉ suggest candidate** — KHÔNG tự promote/refresh canonical Wiki (HUMAN-controlled).
- Lưu vào: `.ai-work/workspaces/<TASK-ID>/08_capture_inbox.jsonl` (append 1 JSON/dòng).
- `aiws-aip run status <AIP-ID>` báo capture counts + số cần triage (status=captured) cho workspace của AIP (CR-AIWS-2026-06-015 F4); `build_aip_index.py --list-untriaged` liệt kê mọi AIP còn capture mở (repo-wide).
- **AI Agent Instance (CR-AIWS-2026-06-042 C1):** instance chạy **dưới một AIP** (run sở hữu workspace) → append capture vào project inbox `08_capture_inbox.jsonl` theo đúng trigger + record format dưới đây, y như mọi in-workspace work (tái dùng cơ chế AIWS, CLAUDE.md #7). Instance chạy **không có AIP** → giữ capture trong **instance queue** (`candidate_queue.jsonl`, package-/instance-level) — KHÔNG chảy vào project inbox cho tới khi instance đó chạy dưới một AIP hoặc HUMAN promote. Promotion → confirmed memory / official wiki vẫn **HUMAN-gated** ở cả hai nhánh.

## Capture khi nào
**Capture** nếu giúp ≥1: task tương lai nhanh/chính xác/nhất quán hơn · giảm đọc lại raw source ·
cải thiện search/meta/discovery · lưu rule/decision HUMAN-confirmed · lộ quan hệ source chưa có trong meta ·
tránh lặp lỗi · thành pattern/playbook tái dùng · cơ hội tooling.
**Không capture** nếu: chỉ task-local tạm · không có giá trị tái dùng · suy đoán không bằng chứng ·
trùng candidate đã có · quá nhỏ.

## 20 Triggers — capture as
Cột **`# · fragment`** = map case → file chi tiết (đọc đúng file, khỏi mò). ⚡ = capture ngay (không dồn cuối step).

| # · fragment | Khi... | `candidate_kind` | `type` điển hình | `suggested_target` |
|---|---|---|---|---|
| [1 · missing_wiki_knowledge](capture_triggers/missing_wiki_knowledge.md) | Cần info, wiki không có nhưng raw source có | `missing_wiki_knowledge` | `wiki_update_candidate` | `wiki_meta` |
| [2 · artifact_relation_update](capture_triggers/artifact_relation_update.md) ⚡ | Phát hiện quan hệ giữa sources chưa có trong meta/index → capture NGAY kèm block `relation:{from,to,role,basis_note_draft,confidence}` (default `knowledge_value: high`; promote qua Relations Enrichment CR batch) | `artifact_relation_update` | `relation_candidate` | `wiki_meta` |
| [3 · summary_layer_candidate](capture_triggers/summary_layer_candidate.md) | Đọc lại cùng source nhiều lần (chỉ cần summary/meta) | `summary_layer_candidate` | `summary_candidate` | `wiki_meta` |
| [4 · new_reference_candidate](capture_triggers/new_reference_candidate.md) | Tìm thấy reference/source-of-truth hữu ích mới | `new_reference_candidate` | `wiki_update_candidate` | `knowledge_hub_reference` |
| [5 · human_confirmed_knowledge](capture_triggers/human_confirmed_knowledge.md) | HUMAN trả lời 1 clarification tái dùng được | `human_confirmed_knowledge` | `qa_candidate` | `knowledge_hub_curated` |
| [6 · retrieval_improvement](capture_triggers/retrieval_improvement.md) | Wiki có nhưng khó tìm (alias/index/title yếu) | `retrieval_improvement` | `wiki_meta_update_candidate` | `wiki_meta` |
| [7 · task_pattern_candidate](capture_triggers/task_pattern_candidate.md) | Phát hiện task pattern tái dùng | `task_pattern_candidate` | `playbook_candidate` | `guideline` |
| [8 · best_practice_anti_pattern](capture_triggers/best_practice_anti_pattern.md) | Best practice / anti-pattern | `best_practice_candidate` / `anti_pattern_candidate` | `guideline_improvement_candidate` | `guideline` |
| [9 · knowledge_quality_issue](capture_triggers/knowledge_quality_issue.md) | Knowledge quality issue (outdated/conflict/low-conf) | `knowledge_quality_issue` | `finding_candidate` | `wiki_meta` |
| [10 · decision_candidate](capture_triggers/decision_candidate.md) | Decision chưa được lưu | `decision_candidate` | `insight` | `knowledge_hub_curated` |
| [11 · glossary_candidate](capture_triggers/glossary_candidate.md) | Glossary/terminology cần chuẩn hoá | `glossary_candidate` | `wiki_update_candidate` | `knowledge_hub_curated` |
| [12 · onboarding_candidate](capture_triggers/onboarding_candidate.md) | Onboarding knowledge (đọc gì trước, entry point) | `onboarding_candidate` | `guideline_improvement_candidate` | `guideline` |
| [13 · tooling_opportunity_candidate](capture_triggers/tooling_opportunity_candidate.md) | Cơ hội tooling/automation cho việc cơ học lặp lại | `tooling_opportunity_candidate` | `tooling_opportunity_candidate` | `future_backlog` |
| [14 · cross_project_knowledge_candidate](capture_triggers/cross_project_knowledge_candidate.md) | Knowledge tái dùng được liên dự án | `cross_project_knowledge_candidate` | `future_backlog_candidate` | `future_backlog` |
| [15 · aiws_system_improvement](capture_triggers/aiws_system_improvement.md) ⚡ | Fix lỗi skill/template/tooling/playbook ngay khi run | `aiws_system_improvement` | `aip_template_improvement_candidate` · `run_aip_improvement_candidate` · `guideline_improvement_candidate` · `tooling_opportunity_candidate` | `aip_template`/`run_aip`/`guideline`/`tooling` |
| [16 · ai_output_improvement_feedback](capture_triggers/ai_output_improvement_feedback.md) ⚡ | HUMAN feedback về chất lượng output AI | `ai_output_improvement_feedback` | `guideline_improvement_candidate` · `run_aip_improvement_candidate` · `aip_template_improvement_candidate` · `notebook_note_candidate` | `guideline`/`notebook` |
| [17 · recurring_failure_defense_in_depth](capture_triggers/recurring_failure_defense_in_depth.md) | Recurring failure (N≥2) trong AIWS flow | `task_pattern_candidate` | `playbook_candidate` | `guideline` |
| [18 · wiki_source_refresh_needed](capture_triggers/wiki_source_refresh_needed.md) ⚡ | Sửa/phát hiện-đổi tài liệu wiki đã đăng ký/canonical | `wiki_source_refresh_needed` | `wiki_meta_update_candidate` (dùng `wiki_update_candidate` nếu canonical doc) | `wiki_meta` (hoặc `knowledge_hub_curated`) |
| [19 · object_relation_capture](capture_triggers/object_relation_capture.md) ⚡ | Lúc build/refresh meta cho artifact → nhận biết OBJECT nó mô tả + quan hệ object↔artifact (representation) + quan hệ object↔object (domain x:, kể cả suy luận) | `object_relation_capture` | `wiki_update_candidate` | `wiki_meta` |
| [20 · digest_synthesis_candidate](capture_triggers/digest_synthesis_candidate.md) | Tổng hợp ≥2 metas/sources cho 1 intent, synthesis có giá trị reuse — gồm purpose-digest "quan hệ A↔B cho task-type T"; kèm `purpose` + `source_refs[]`; materialize khi promote = E2 `--materialize`, không viết tay | `digest_synthesis_candidate` | `summary_candidate` | `knowledge_hub_curated` |

Chọn `candidate_kind` gần nhất, đừng đẻ kind trùng lặp. Không có → kind mới rõ ràng + giải thích trong `content`.
Cột `# · fragment` link thẳng tới detail (Suggested action / Example / Notes) của trigger đó.

## Record format

> **Ghi capture bằng tool, đừng viết tay JSON (CR-AIWS-2026-07-045 T4).**
> `py .ai-work/tooling/append_capture.py --workspace <ws> --id CAP-00N --type <type> --title "..." --content "..."`
> Tool build record trong Python, `json.dumps` rồi **re-parse để chứng minh hợp lệ** trước khi append.
> Viết tay bằng heredoc/echo là cách JSONL hỏng lọt vào inbox: Windows path trong `content` sinh escape
> không hợp lệ, và lỗi chỉ lộ ở finalize lint (`capture_parse`) — đã xảy ra **2 lần trong 1 task** (AIP-913).
> Buộc phải viết tay → dùng **forward slash** trong `content` và validate:
> `py -c "import json,sys;json.loads(sys.stdin.read())" < line.json`

Append 1 JSON object/dòng vào `08_capture_inbox.jsonl`. Compact nhưng có bằng chứng.

> **LINTER CONTRACT** (`lint_workspace.py`) — hai phần, đọc cả hai.
>
> **(a) Field bắt buộc — vô điều kiện.** 6 field: `id`, `type`, `title`, `content`, `status`,
> `suggested_target` (`suggested_target` thiếu = warning; 4 field còn lại + `type` thiếu = error).
>
> **(b) Contract theo STATUS** — điều kiện chỉ áp khi capture ở một `status` nhất định:
> - `status: promoted` → **phải** có `source_refs` (rule `capture_refs`, WARNING). Một capture đã
>   promote mà không nói nó trở thành cái gì thì không truy vết được. Chỉ `promoted` mới bị đòi:
>   một capture `triaged` có disposition kết thúc thì hợp lệ khi không có `source_refs`
>   (CR-AIWS-2026-06-029).
> - *(chưa có điều kiện theo-status nào khác — thêm rule mới thì thêm dòng vào ĐÂY)*
>
> Phần (b) tồn tại vì mục này từng được viết như một danh sách field vô điều kiện, nên rule
> `capture_refs` không có ô nào để nằm và sống trong code suốt mà không vào tài liệu
> (CAP-1003-02 → CR-AIWS-2026-08-131).

```json
{"id":"CAP-001","type":"wiki_meta_update_candidate","title":"...","content":"... (kèm evidence inline)",
 "status":"captured","suggested_target":"wiki_meta","candidate_kind":"wiki_source_refresh_needed",
 "knowledge_value":"high","discovered_at":"YYYY-MM-DD","step":"STEP-NN","reusable":true}
```

<!-- AIWS:BEGIN generated-capture-enums -->
<!-- GENERATED from lint_workspace.py by `py .ai-work/tooling/append_capture.py --sync-playbook-enums --apply`. Do not hand-edit: this block drifted from the code once already (CR-AIWS-2026-08-126 C7). -->
**Enum hợp lệ (generated — doc == code):**

- `candidate_kind` (15): `authoring_lesson` · `decision_or_convention` · `deliverable_defect` · `output_quality_feedback` · `process_doc_gap` · `qa_candidate` · `relation_or_object` · `retrieval_improvement` · `reusable_pattern` · `review_rule` · `spec_impl_drift` · `tool_gotcha` · `tooling_opportunity` · `wiki_knowledge_gap` · `wiki_quality_issue`
  - Một dự án có thể khai thêm kind riêng trong `.ai-work/project_profile.yml` (`capture_kinds:`); tập hiệu lực = preset ∪ `<namespace>:<id>`. Thêm **kind** thì được, thêm `type` / `suggested_target` thì không.
- `improvement_scope` (**bắt buộc với record mới**): `aiws` · `project`
- `target_artifact` (tùy chọn): repo-relative path hoặc stable id. Chỉ validate **shape**, không bao giờ kiểm tra tồn tại — một capture có quyền trỏ tới thứ chưa có.
- `type` (16): `aip_template_improvement_candidate` · `checklist_update_candidate` · `deferred_note` · `finding_candidate` · `future_backlog_candidate` · `gotcha_candidate` · `guideline_improvement_candidate` · `insight` · `playbook_candidate` · `qa_candidate` · `review_rule_candidate` · `run_aip_improvement_candidate` · `summary_candidate` · `tooling_opportunity_candidate` · `wiki_meta_update_candidate` · `wiki_update_candidate`
  - từ chối cho record mới (deprecated): `notebook_note_candidate` · `relation_candidate` · `source_representation_issue`
- `suggested_target` (17): `aip_template` · `discard` · `future_backlog` · `guideline` · `history_only` · `knowledge_hub_curated` · `knowledge_hub_reference` · `notebook` · `operating_memory` · `playbook` · `run_aip` · `skill` · `tooling` · `truth` · `wiki_curated` · `wiki_meta` · `wiki_reference`
- `status` (7): `archived` · `captured` · `deferred` · `discarded` · `promoted` · `retained_local` · `triaged`
- `correction_class` (tùy chọn, cho `output_quality_feedback`): `factual_error` · `missing_section` · `scope` · `wrong_approach` · `wrong_format`
<!-- AIWS:END generated-capture-enums -->

Còn untriaged → xử lý trước khi đóng task, theo **đúng hai đường**: triage ngay, hoặc `defer` **kèm lý do** vào Capture Backlog. `aiws-aip run close` từ chối flip AIP sang `done` khi còn row `captured` (CR-AIWS-2026-08-125).

**Fields bổ sung theo kind (CR-AIWS-2026-07-008):**
- `artifact_relation_update` → block `relation: {from_id, to_id, role, basis_note_draft, confidence: "candidate"}` (lint validate khi có).
- `digest_synthesis_candidate` → `purpose` + `source_refs[]`.
- `qa_candidate` → `question` / `answer` / `qa_kind` (`overview_answer`|`task_info_pack`|`investigation_finding`) / `asked_by` (`human`|`ai`) — tách bạch, không squash vào content (feed cho QA memory store, CR-2026-07-009).
- **Capture bắt buộc theo trip-wire (E4):** search vượt ~2× input count hoặc escalate tokens/catalog/raw → PHẢI capture `retrieval_improvement` (vocabulary: `lookup_miss_patterns.md` MP1–MP7). **Van "assessed-no-reuse":** record bắt buộc được phép kết luận "không có reuse value vì X" → discard-triage ngay — noise filter vẫn nguyên.

## Step Closing Check
Trước khi đóng mỗi step, tự hỏi — yes bất kỳ → append candidate:
1. Không tìm thấy trong wiki nhưng tìm ở nơi khác? (§1)
2. Hỏi HUMAN 1 điều nên tái dùng? (§5) · Đọc lại cùng source nhiều lần? (§3)
3. Phát hiện quan hệ source / reference / source-of-truth chưa được ghi? (§2,§4)
4. Wiki khó retrieve / cần alias-index-overview? (§6)
5. Task pattern · best practice · anti-pattern · decision đáng lưu? (§7,§8,§10)
6. Conflict / outdated / low-confidence knowledge? (§9)
7. Fix lỗi skill/playbook/template/tooling? (§15) · HUMAN feedback về output? (§16)
8. Sửa/thấy đổi tài liệu wiki đã đăng ký/canonical → cần refresh meta/index/object? (§18 — scope: artifact meta/index)
9. Build/refresh meta cho artifact → đã nhận biết object nó mô tả + quan hệ object↔artifact (representation) và object↔object (domain x:, kể cả suy luận) → đề xuất HUMAN author object node + edges chưa? (§19)
10. Search có intent nào vượt budget/trip-wire (≥2× calls) chưa capture `retrieval_improvement`? (§6 + MP1–MP7) · Có tổng hợp ≥2 metas đáng làm digest? (§20) · Relations mới phát hiện đã capture ⚡ với relation block chưa? (§2)

## See Also
- Map case → file: bảng **20 Triggers** phía trên (cột `# · fragment`). Chi tiết từng trigger: [`capture_triggers/`](capture_triggers/) (20 fragment, mỗi use-case 1 file).
- Relations Enrichment CR batch: [`relations_enrichment_cr_template.md`](relations_enrichment_cr_template.md) · Miss patterns: [`lookup_miss_patterns.md`](lookup_miss_patterns.md)
- `WIKI_CANDIDATE_SUGGESTION_RULE.md` — eligibility theory · `capture_and_triage_rules.md` — nguyên tắc capture
- `queue_rules.md` — queue conventions
