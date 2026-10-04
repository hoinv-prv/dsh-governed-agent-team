# Bộ tài liệu HUMAN cần đọc

## Candidate hiện tại sau review

Review advisory tại `council-reviews/durable-agent-mvp-goal-scope/review-summary.md` đã được phản biện và áp dụng bằng một planning revision. Bắt đầu bằng [`phan-bien-review-goal-scope-v1.md`](phan-bien-review-goal-scope-v1.md), rồi đọc candidate hiện tại dưới đây.

`handoff-review-goal-scope-sprint-v1.md` là handoff của revision cũ và chỉ còn giá trị lịch sử. Cần tạo/freeze handoff mới trước fresh independent re-review.

## Thứ tự đề nghị

1. [`goal-scope-baseline-v2.md`](goal-scope-baseline-v2.md)
   - authoritative candidate hiện tại cho PBG1–PBG4, DF1–DF6, TaskContract, terminal lifecycle, effects, durability và TaskHandoff.
2. [`memo-agent-team-pm-goals-v1.md`](memo-agent-team-pm-goals-v1.md)
   - goal bắt buộc dành cho coordinator/Agent Team/PM khi planning và execution.
3. [`memo-durable-agent-team-member-compatibility-v3.md`](memo-durable-agent-team-member-compatibility-v3.md)
   - source-agnostic task, one-active-task, host seam, terminal handoff và immutable artifact settlement.
4. [`ke-hoach-sprint-agile-v10.md`](ke-hoach-sprint-agile-v10.md)
   - P0 oracle/seam, PoC dependencies, một basic-design sprint, sáu feature sprints, integration và qualification.
5. [`phan-bien-review-goal-scope-v1.md`](phan-bien-review-goal-scope-v1.md)
   - disposition F-01..F-07 và phần review bị giới hạn hoặc over-spec.
6. [`quy-trinh-capture-kinh-nghiem-v1.md`](quy-trinh-capture-kinh-nghiem-v1.md)
   - process supporting DG4, không phải Durable Agent function.
7. Khi cần kiểm tra nguyên nhân reset, đọc [`../durable-agent-wbs-runner-mvp-sprint1/pm-systemic-rework-rca.md`](../durable-agent-wbs-runner-mvp-sprint1/pm-systemic-rework-rca.md).

## Trạng thái

- Đây là tài liệu planning, chưa phải WBS execution authority.
- Chưa có WBS mới được phê duyệt hoặc được phép chạy.
- Các `sprint-plan.*`, `mvp-function-risk-sprint-map.v1.md`, `kiem-tra-lai-*`, `muc-tieu-kinh-doanh-*`, `goal-scope-baseline-v1.md`, compatibility memo v1/v2 và sprint plan trước v10 là lịch sử draft/review; baseline v2, compatibility memo v3 và sprint plan v10 supersede chúng cho candidate hiện tại.
- Candidate revision mới chưa có fresh independent verdict. Chỉ sau verdict `ready_for_p0_wbs` mới draft một WBS nhỏ cho P0 để review riêng; không tạo WBS lớn cho toàn bộ roadmap.

## Quy ước ngôn ngữ

Tài liệu HUMAN-facing dùng tiếng Việt. Chỉ giữ tiếng Anh cho từ kỹ thuật hoặc identifier cần đối chiếu chính xác, ví dụ: WBS, Agent, task, sprint, PoC, dependency, approval, checkpoint, restart, replay, effect, blocker, oracle, runtime, DTO, API, JSON, Markdown và tên trạng thái/mã lỗi.
