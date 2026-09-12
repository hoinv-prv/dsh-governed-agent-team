# aiws_system_improvement — Fix lỗi skill/template/tooling khi run
- **type:** aip_template_improvement_candidate · **suggested_target:** aip_template · **timing:** ⚡immediate
## When
Trong lúc chạy `aiws-aip create` hoặc thực thi một AIP step, AI gặp sự cố trong chính hệ thống AIWS (lint fail, schema mismatch, template thiếu/sai section, sai field name trong playbook example, skill cho guidance mâu thuẫn, tooling bug) **và tự fix ngay trong session**. Bản fix là bằng chứng thực tế rằng hệ thống đang sai/thiếu.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** không có family. `aiws_system_improvement` được **superseded bởi `improvement_scope: aiws`** — record cũ giữ nguyên và không bị cảnh báo; record MỚI chọn family theo bản chất vấn đề (ví dụ `tooling_opportunity`, `process_doc_gap`, `spec_impl_drift`) và đặt `improvement_scope: aiws`.

candidate_kind `aiws_system_improvement`. Chọn type theo nguồn gốc lỗi:
- `aip_template_improvement_candidate` → template thiếu/sai section/field (suggested_target `aip_template`)
- `run_aip_improvement_candidate` → flow/guidance/self-check của aiws-aip run mơ hồ hoặc sai (suggested_target `run_aip`)
- `guideline_improvement_candidate` → playbook/skill/guideline sai hoặc lỗi thời (suggested_target `guideline`)
- `tooling_opportunity_candidate` → script/linter bug hoặc thiếu validation (suggested_target `tooling`)
## Suggested action
Cập nhật template/skill/guideline/tooling tương ứng để vấn đề không tái diễn.
## Example
Lint báo lỗi field name trong example của AIP_EXEC_TEMPLATE → sửa template ngay → capture `aip_template_improvement_candidate`.
## Notes
TIMING RULE: capture **⚡immediate ngay sau khi fix** trong khi context còn tươi — KHÔNG defer tới end-of-step hay AIP close, nếu không fix sẽ bị cô lập và lỗi tái diễn.
