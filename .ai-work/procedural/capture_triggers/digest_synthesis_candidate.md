# digest_synthesis_candidate — Tổng hợp ≥2 metas/sources có giá trị reuse
- **type:** summary_candidate · **suggested_target:** knowledge_hub_curated · **timing:** normal
## When
AI phải TỔNG HỢP thông tin từ ≥2 metas/sources để trả lời MỘT intent, và bản tổng hợp đó có giá trị dùng lại (task tương lai cùng shape sẽ cần đúng tổ hợp này). Hai dạng:
- **(b) digest đa-meta:** tổ hợp thông tin từ nhiều sources cho một chủ đề (vd: toàn bộ validation rules rải trong RD+BD+DD của một chức năng).
- **(c) purpose-specific digest:** phần thông tin của source B mà task-type T trên đối tượng A cần (vd: review chức năng A chỉ cần phần quan hệ A↔B trong design B — không cần toàn bộ B).
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `wiki_knowledge_gap` — tên trigger `digest_synthesis_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `wiki_knowledge_gap`. `improvement_scope` mặc định: `project`.

candidate_kind `digest_synthesis_candidate` — kèm fields: `purpose` (dùng cho task-type nào / đối tượng nào) + `source_refs[]` (source_ids/paths đã tổng hợp). Dạng (c) ghi purpose theo mẫu "quan hệ A↔B cho task-type T".
## Suggested action
Sau HUMAN triage → **materialize bằng E2**: `py .ai-work/tooling/build_reading_kit.py --materialize` với seed = `source_refs` (KHÔNG viết digest tay — derived-surface doctrine: citation path+id, staleness lint, refresh trigger) → đăng ký wiki source (`knowledge_targets: navigation`/curated).
## Example
Review DD chức năng F02 phải đọc 3 lần BD_F05 chỉ để lấy phần booking-conflict rules liên quan F02 → capture digest_synthesis_candidate purpose="quan hệ F02↔F05 (conflict rules) cho task review-DD", source_refs=[SRC-DEMO-BD-BOOKINGDETAILUPDATECANCEL, SRC-DEMO-DD-SEARCHROOM].
## Notes
- KHÁC #3 `summary_layer_candidate` (single-source summary/nav layer) — #20 là TỔNG HỢP cross-source theo intent.
- Đừng capture khi tổ hợp chỉ dùng 1 lần (task-local) — Knowledge Value filter vẫn áp.
