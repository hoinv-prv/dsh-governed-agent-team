# best_practice_anti_pattern — Best practice / anti-pattern
- **type:** guideline_improvement_candidate · **suggested_target:** operating_memory · **timing:** normal
## When
AI phát hiện một cách làm tốt lặp lại được (good practice) hoặc một sai lầm cần tránh (mistake to avoid) trong quá trình thực thi. Dấu hiệu: nhận ra "lần sau nên làm thế này" hoặc "cái này gây lỗi, đừng lặp lại".
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `reusable_pattern` — tên trigger `best_practice_anti_pattern` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `reusable_pattern`. `improvement_scope` mặc định: `phải tự chọn`.

Chọn candidate_kind theo ngữ cảnh:
- **best_practice_candidate** → khi là good practice lặp lại được, nên khuyến khích.
- **anti_pattern_candidate** → khi là mistake to avoid, cần cảnh báo.
## Suggested action
Mặc định vào **Operating Memory** (bài học vận hành — xem `operating_memory.md`): thứ chỉ cần
nhớ để lần sau làm đúng/nhanh hơn. Nếu mục này cần được **tuân thủ** chứ không chỉ tham khảo, đổi
`suggested_target` sang `guideline` và đi đường canonical — Operating Memory KHÔNG phải nguồn thẩm quyền.
## Example
"Luôn chạy `/aiws-lint` trước khi finalize AIP" (best_practice) — đưa vào checklist guideline thay vì tự ý apply.
## Notes
Slug best_practice_anti_pattern bao trùm cả best_practice_candidate lẫn anti_pattern_candidate; chọn nhánh dựa trên tính chất quan sát được.
