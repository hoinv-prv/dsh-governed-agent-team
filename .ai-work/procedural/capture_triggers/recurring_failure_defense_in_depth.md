# recurring_failure_defense_in_depth — Recurring failure (N≥2) trong AIWS flow
- **type:** playbook_candidate · **suggested_target:** guideline · **timing:** normal
## When
Cùng một class lỗi xảy ra N≥2 lần trong AIWS pipeline (capture drop, retrieval miss, gate bypass...) **dù đã có rule/guidance**. Đây là tín hiệu single-point enforcement không đủ — không thể dựa vào AI memory hay 1 rule trong SKILL.md.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `review_rule` — tên trigger `recurring_failure_defense_in_depth` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `review_rule`. `improvement_scope` mặc định: `phải tự chọn`.

candidate_kind `task_pattern_candidate` (default). Branch theo ngữ cảnh:
- **task_pattern_candidate** → khi pattern cần ghi lại để xử lý sau (default).
- **aiws_system_improvement** → khi đã fix ngay.
PATTERN = Defense-in-depth enforcement: fix tại MỌI điểm trong pipeline, không chỉ nơi phát hiện — Discovery (tool output hint khi miss), Persistence (structured evidence trong artifact: AIP section, table column), Import (mandatory sweep khi tool/skill start), Close (mandatory sweep trước close/finalize).
## Suggested action
Khi phát hiện recurring failure pattern, apply defense-in-depth tại cả 4 điểm (Discovery / Persistence / Import / Close) thay vì chỉ fix tại discovery point.
## Example
AIP-EXEC-025: capture drop xảy ra 2 lần liên tiếp với TEMPLATE_DD; fixed bằng 4 enforcement points — lookup hint (IR-004), Pre-flight Pending Captures section (IR-002), aiws-aip run start sweep step 1b (IR-001), Final Capture Sweep step 6b / close sweep.
## Notes
—
