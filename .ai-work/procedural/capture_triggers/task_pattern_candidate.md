# task_pattern_candidate — Task pattern tái dùng
- **type:** playbook_candidate · **suggested_target:** guideline · **timing:** normal

## When
AI lặp lại hoặc khám phá ra một method hữu ích cho một loại task — ví dụ review design, create testcase, analyze impact, read legacy source, hoặc prepare AI coding input. Khi nhận ra cách làm này có thể tái dùng cho task cùng loại về sau.

## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `reusable_pattern` — tên trigger `task_pattern_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `reusable_pattern`. `improvement_scope` mặc định: `phải tự chọn`.

candidate_kind `task_pattern_candidate`.

## Suggested action
Sau HUMAN review: tạo/cập nhật playbook, AIP template guidance, hoặc một task pattern entry để method này được tái dùng nhất quán.

## Example
Khi review design lặp lại checklist "kiểm consistency giữa screen flow ↔ data flow ↔ API spec" → capture thành task_pattern_candidate cho loại task review design.

## Notes
—
