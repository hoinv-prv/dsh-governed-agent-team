# QA Memory Spec (MVP) — v0.1

> **Status:** canonical methodology spec (MVP). **Authority:** định nghĩa QA Memory — store các cặp question/answer TỐT được HUMAN confirm để reuse ở tác vụ sau. **Nguồn:** CR-AIWS-2026-07-009 (Track D, IR-2026-07-07) — HUMAN yêu cầu 2026-07-07: "lưu kết quả cuối, không lưu conversation".
> **Placement:** `product/methodology/ai_work_system/20_specs/QA_Memory_Spec_MVP.md`.

## 1. Purpose & vị trí trong kiến trúc

QA Memory lưu **kết quả cuối** của những lần hỏi–đáp có giá trị reuse (không lưu hội thoại). Store là **TRUTH** của QA memory; trang `QA_MEMORY_OVERVIEW` (generator CR-2026-07-010, page #9) là **PROJECTION** để lookup tìm thấy — đúng mô hình meta/index.

- **Store:** `.ai-work/wiki/qa_memory/confirmed_qa.jsonl` (project-local, HUMAN-curated — sibling của `task_lens_presets/`).
- **Precedence:** QA record là curated-lớp-thấp — **không bao giờ** outrank Truth/canonical; mọi surface hiển thị QA phải mang nhãn "curated QA — verify vs Truth/canonical khi decision matters".
- **Phân định:** KHÁC agents-pack `confirmed_memory.jsonl` (instance-scoped); KHÁC memory của harness/session.

## 2. Taxonomy 3 nguồn Q&A (HUMAN 2026-07-07)

| `qa_kind` | Nguồn | Answer shape | Convergence |
|---|---|---|---|
| `overview_answer` | (i) HUMAN hỏi tổng quan (hệ thống / function list / luồng nghiệp vụ) | summary ngắn + **POINTER tới overview page** khi có (không duplicate — page regenerate thì QA không stale) | trang generated CR-010 |
| `task_info_pack` | (ii) Q&A tìm info cho 1 task cụ thể (vd "toàn bộ info cho review DD chức năng A") | question + trỏ **materialized reading kit** qua `source_refs` | E2 `build_reading_kit.py` |
| `investigation_finding` | (iii) AI tự capture khi điều tra | fact ngắn + evidence refs | BẮT BUỘC HUMAN confirm khi promote (rule #7) |

## 3. Record schema (JSONL — 1 record/dòng)

```json
{"id": "QA-001", "question": "...", "answer": "...",
 "qa_kind": "overview_answer|task_info_pack|investigation_finding",
 "asked_by": "human|ai", "applies_when": "<1 dòng điều kiện relevance>",
 "scope_tags": ["..."], "system": "<id|absent=common>",
 "source_refs": ["<source_id hoặc path evidence/kit>"], "asked_in": "TASK-...",
 "confirmed_by": "HUMAN", "confirmed_at": "YYYY-MM-DD",
 "status": "confirmed", "supersedes": "QA-000?"}
```

- **Mandatory:** `id` (QA-NNN, duy nhất), `question`, `answer`, `qa_kind`, `asked_by`, `status`; `confirmed_by: HUMAN` + `confirmed_at` bắt buộc khi `status: confirmed`.
- **Status enum (3):** `confirmed` → `needs_review` (nguồn refs đổi / meta refresh flag) → `confirmed` lại hoặc `deprecated` (+`supersedes` khi bị record mới thay).
- **Answer = KẾT QUẢ CUỐI:** ngắn gọn đủ dùng lại (khuyến nghị ≤ ~10 dòng); evidence/chi tiết qua `source_refs` — CẤM dump transcript/conversation.

## 4. Feed — từ capture đến store

1. Capture: type `qa_candidate` với fields tách bạch `question`/`answer`/`qa_kind`/`asked_by` (CR-2026-07-008; lint_workspace validate enum). Trigger #5 (HUMAN-answered) + nhánh AI-self-derived (`asked_by: ai`).
2. **Triage precedence — meta-first (chống second-truth-surface):** ưu tiên promote nội dung vào **meta lookup_keys/summary hoặc relation edge** TRƯỚC; QA store CHỈ nhận answer KHÔNG quy về meta/relation/kit edit. (Chi tiết: `capture_and_triage_rules.md` §Triage qa_candidate.)
3. Promote (HUMAN): append record vào store (`status: confirmed`, `confirmed_by: HUMAN`); capture gốc → `status: promoted` + `source_refs` trỏ QA-id.

## 5. Retrieval & reuse

- **Found-again:** trang `QA_MEMORY_OVERVIEW` (page #9, generator CR-010 — owner duy nhất) đăng ký làm wiki source → lookup thấy qua đường chuẩn; store lớn → H6 chunk theo topic. KHÔNG per-record index (giữ index schema).
- **Reuse trigger (P3 — GATED DP-912-5b, chưa apply):** `build_active_step_context.py` match QA vs AIP/step intent (adapter: `question`→title · `scope_tags`+`applies_when`+question-tokens→lookup_keys · answer dòng đầu→summary_short · `QA-NNN`→source_id, qua `_common.score_semantic`); ASC section "## Known Answers" 3-5 hits, CHỈ `status: confirmed`, mỗi hit mang nhãn verify-vs-Truth + QA-id + confirmed_at; rỗng → omit (lean-surface). Opt-in → default sau ≥10-20 QA thật.

## 6. Lifecycle & lint

- Refresh meta nguồn có trong `source_refs` → flip record `needs_review` (maintenance pass).
- Lint store (`lint_wiki` — `qa_store_*`): mandatory fields; id duy nhất; status enum; `confirmed_by: HUMAN` khi confirmed; `source_refs` dạng source_id phải resolve trong index (WARN nếu không).
- Store ships RỖNG — mọi record qua HUMAN confirm; AI không bao giờ tự append store (rule #7).

## 7. Out of scope (MVP)

ASC hook (P3 gated); agents-pack instance đọc project store (follow-up B-10); QA analytics; multi-store federation.

## 8. Relationships

`WIKI_CANDIDATE_SUGGESTION_RULE` (eligibility) · `wiki_candidate_capture_playbook` trigger #5 + qa fields (CR-008) · `build_wiki_overview` page #9 (CR-010) · agents-pack `confirmed_memory_schema` (pattern nguồn, instance-scoped) · `Controlled_Knowledge_Promotion_Spec_MVP` (promotion nguyên tắc).
