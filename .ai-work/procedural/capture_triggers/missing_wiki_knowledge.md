# missing_wiki_knowledge — Thiếu kiến thức wiki, tìm thấy ở raw source
- **type:** wiki_update_candidate · **suggested_target:** wiki_meta · **timing:** normal
## When
AI cần một thông tin để làm task nhưng không tìm thấy trong Wiki (project/local/common), rồi phải tự đi tìm và bắt gặp nó trong một raw/source artifact (spec gốc, doc thiết kế, file nguồn). Dấu hiệu: lookup wiki trả về rỗng/không liên quan, nhưng raw source lại có đáp án.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `wiki_knowledge_gap` — tên trigger `missing_wiki_knowledge` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `wiki_knowledge_gap`. `improvement_scope` mặc định: `project`.

candidate_kind `missing_wiki_knowledge`.
## Suggested action
Sau khi HUMAN review: tạo/cập nhật Wiki entry hoặc source meta cho thông tin đó để các task tương lai không phải tái khám phá lại từ raw source.
## Example
Cần biết format mã giao dịch cho STEP-03 — lookup wiki rỗng, nhưng tìm thấy quy ước trong design spec gốc → đề xuất bổ sung source meta trỏ tới spec.
## Notes
—
