# tooling_opportunity_candidate — Cơ hội tooling / automation
- **type:** tooling_opportunity_candidate · **suggested_target:** future_backlog · **timing:** normal

## When
AI nhận ra công việc cơ học lặp đi lặp lại — validation, conversion, scan, search, hoặc formatting — mà lẽ ra có thể giao cho một script deterministic hoặc một lightweight agent xử lý.

## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `tooling_opportunity` — tên trigger `tooling_opportunity_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `tooling_opportunity`. `improvement_scope` mặc định: `aiws`.

candidate_kind `tooling_opportunity_candidate` (single branch, không phân nhánh theo ngữ cảnh).

## Suggested action
Sau HUMAN review: thêm vào tooling backlog, hoặc tạo một tool improvement candidate để theo dõi và triển khai sau.

## Example
Lặp lại việc tay convert nhiều file Excel sang MD và validate cùng một định dạng → đề xuất script deterministic thay cho thao tác thủ công.

## Notes
—
