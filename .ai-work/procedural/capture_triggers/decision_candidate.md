# decision_candidate — Decision chưa được lưu
- **type:** insight · **suggested_target:** knowledge_hub_curated · **timing:** normal
## When
Trong lúc execute AIP, HUMAN đưa ra hoặc xác nhận một quyết định quan trọng, nhưng quyết định đó **chưa được ghi lại** trong Wiki / decision trace / canonical docs.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `decision_or_convention` — tên trigger `decision_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `decision_or_convention`. `improvement_scope` mặc định: `project`.

candidate_kind: `decision_or_convention` — trigger này thuộc family `decision_or_convention` (CR-AIWS-2026-08-126 C1; tên trigger `decision_candidate` giữ làm nhãn capture-time, không còn là giá trị ghi vào `candidate_kind`).
## Suggested action
Sau khi HUMAN review, preserve quyết định kèm đủ context: scope, impact, và source of confirmation (ai/đâu xác nhận).
## Example
HUMAN chốt "dùng JSONL thay vì SQLite cho capture inbox" giữa AIP-EXEC — capture lại scope + lý do + nguồn xác nhận.
## Notes
—
