# cross_project_knowledge_candidate — Knowledge tái dùng liên dự án
- **type:** future_backlog_candidate · **suggested_target:** future_backlog · **timing:** normal
## When
AI phát hiện một principle/pattern có thể tái dùng ngoài phạm vi project hiện tại — ví dụ cấu trúc Overview → Detail, thiết kế HUMAN gate, Wiki-first retrieval, hoặc source verification practice. 1-3 câu nhận biết: pattern không gắn riêng project này mà mang tính phương pháp luận chung.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `reusable_pattern` — tên trigger `cross_project_knowledge_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `reusable_pattern`. `improvement_scope` mặc định: `phải tự chọn`.

candidate_kind: `reusable_pattern` — trigger này thuộc family `reusable_pattern` (CR-AIWS-2026-08-126 C1; tên trigger `cross_project_knowledge_candidate` giữ làm nhãn capture-time, không còn là giá trị ghi vào `candidate_kind`).
- `future_backlog_candidate` → khi pattern đáng cân nhắc promote lên common preset/package knowledge nhưng cần HUMAN review (mặc định cho trigger này).
## Suggested action
Consider promotion to common preset/package knowledge sau khi HUMAN review — đánh giá tính tổng quát và reuse trước khi đưa vào package chung.
## Example
Phát hiện "HUMAN gate trước mọi canonical update" áp dụng được cho nhiều dự án → capture làm cross_project_knowledge_candidate cho common package.
## Notes
—
