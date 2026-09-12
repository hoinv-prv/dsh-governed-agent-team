# summary_layer_candidate — Đọc lại cùng source nhiều lần
- **type:** summary_candidate · **suggested_target:** wiki_meta · **timing:** normal
## When
AI phải đọc lại cùng một source artifact nhiều lần trong khi thực ra mỗi lần chỉ cần summary, key rules, key sections, dependencies, hoặc search hints — không cần toàn bộ nội dung. Dấu hiệu: re-read lặp, scan tốn token để tìm lại cùng phần.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `wiki_knowledge_gap` — tên trigger `summary_layer_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `wiki_knowledge_gap`. `improvement_scope` mặc định: `project`.

candidate_kind: `wiki_knowledge_gap` — trigger này thuộc family `wiki_knowledge_gap` (CR-AIWS-2026-08-126 C1; tên trigger `summary_layer_candidate` giữ làm nhãn capture-time, không còn là giá trị ghi vào `candidate_kind`). Source bị đọc lại nhiều lần nhưng nhu cầu thực chỉ là lớp tóm tắt / điều hướng (summary, key rules, key sections, dependencies, search hints).
## Suggested action
Sau HUMAN review: bổ sung một summary layer cho artifact hoặc cải thiện source meta (lookup keys / summary / key sections) để lần sau AI orient được mà không cần đọc full.
## Example
AIP-EXEC phải mở lại SOP_MASTER 4 lần chỉ để tra key rule §4.1 → đề xuất thêm summary layer / cập nhật source meta.
## Notes
—
