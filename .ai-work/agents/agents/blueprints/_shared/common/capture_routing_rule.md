# Capture routing rule — Desk vs Task Workspace (CR-AIWS-2026-08-010)

**Câu hỏi phân loại:** *"Người KHÁC làm task này (hoặc dự án/AIWS) có cần biết điều này không?"*

| Loại | Đích | Cơ chế |
|---|---|---|
| Kinh nghiệm CHỈ cải thiện cách desk này làm việc (retrieval hint, tool note, output preference, lesson riêng, process improvement của desk) | **Desk** — per-run `learning_candidates.jsonl` → `training/candidate_queue.jsonl` → HUMAN confirm (`/aiws-agent review-learning`) → `memory/` | đã có (AP-CR-39/31; FR-MEM-04 không auto-promote) |
| Capture chung: dự án / task hiện tại / wiki knowledge / lỗi-cải tiến AIWS (spec drift, tooling bug, guideline gap, relation, retrieval gap) | **Task Workspace** `08_capture_inbox.jsonl` (per capture playbook) | đã có (AP-CR-13 tier-up; run aip_driven dùng TW của driving AIP) |
| **Cả hai giá trị** (bài học riêng NHƯNG dự án cũng cần) | Ghi CẢ HAI — desk entry (góc "cách tôi làm") + TW entry (góc "điều dự án cần biết"); TW entry KHÔNG trỏ ngược vào desk memory (desk = private surface) | rule này |
| Không chắc | → TW (thiên về chia sẻ; triage sẽ lọc) | rule này |

> **Hai mặt routing (CR-AIWS-2026-08-126 C6).** File NAY quan tri **desk -> Task Workspace tier-up**, khoa tren `type`.
> **Consumer map** trong `procedural/capture_and_triage_rules.md` quan tri chinh cai inbox cua Task Workspace,
> khoa tren `candidate_kind` — ai triage tung family va no tro thanh artifact gi. Hai mat, mot inbox: file nay
> la authoritative cho cay cau, file kia cho triage.
>
> **Mot va cham ten goi can phan biet:** `process_improvement_candidate` o day la mot **`type`** duoc danh dau
> desk-only/never-tier-up; `process_doc_gap` ben kia la mot **`candidate_kind`** con song voi 43 record in-repo.
> Hai truong khac nhau — cai nay khong ham y cai kia.

**Cấm:** promote thẳng vào wiki/memory (mọi kênh đều HUMAN-gated); dùng desk memory làm chỗ né triage.

## Vocabulary bridge (BẮT BUỘC khi tier-up — CR-AIWS-2026-08-011)

Desk và Task Workspace dùng **hai vocabulary khác nhau**, cả hai đều hợp lệ trong phạm vi của mình:
desk-side = candidate types của `lesson_capture_rule.md` §3; TW-side = enum đóng của `lint_workspace`
(`CAPTURE_TYPE_ENUM` / `CAPTURE_TARGET_ENUM`). Khi tier-up lên TW, **phải dịch** — nếu không, capture
đúng-rule vẫn sinh hàng loạt WARNING (đo được: 6 capture agent → 10 warning, trong khi 3 capture ghi
bằng enum TW → 0 warning; Phase B dogfood AIP-EXEC-994).

| Desk-side candidate type | → TW `type` | → `suggested_target` |
|---|---|---|
| `checklist_update_candidate` | `guideline_improvement_candidate` | `guideline` |
| `review_rule_candidate` | `guideline_improvement_candidate` | `guideline` |
| `retrieval_hint_candidate` | `wiki_meta_update_candidate` | `wiki_meta` |
| `wiki_candidate` | `wiki_update_candidate` | `knowledge_hub_curated` |
| `tool_improvement_candidate` | `tooling_opportunity_candidate` | `tooling` |
| `blueprint_improvement_candidate` | `guideline_improvement_candidate` | `guideline` |
| `project_issue_pattern_candidate` | `finding_candidate` | `future_backlog` |
| `false_positive_note_candidate` | *(desk-only — KHÔNG tier-up)* | — |
| `output_preference_candidate` | *(desk-only — KHÔNG tier-up)* | — |
| `process_improvement_candidate` | *(desk-only — KHÔNG tier-up; ghi vào `process/` của chính desk qua review-learning, AP-CR-31)* | — |

**Quy tắc khi ghi vào TW inbox:**
1. `type` + `suggested_target` **theo enum TW** (cột 2/3).
2. Giữ nhãn gốc ở field phụ **`desk_type`** — không mất thông tin, triage vẫn truy được nguồn desk.
3. Type không có trong bảng (kể cả type bạn tự nghĩ ra cho tình huống mới) → dùng
   `guideline_improvement_candidate` + ghi `desk_type` nguyên bản. **KHÔNG tự mint type mới trong `type`.**
4. Hàng *desk-only* ở lại desk; nếu nội dung có giá trị cho dự án → viết một capture RIÊNG theo góc
   "điều dự án cần biết" (bảng phân loại phía trên), không tier-up bản desk.
