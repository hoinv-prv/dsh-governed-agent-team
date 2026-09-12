---
artifact_type: sop_master
title: SOP Master — <PROJECT_NAME>
status: active
updated_at: <YYYY-MM-DD>
owner: <owner>
---

<!-- Top-level SOP. Authoritative zone (Wiki_Truth_History_Spec §3). No silent rewrite — candidate → review → apply. -->

# SOP Master — <PROJECT_NAME>

## Purpose
Top-level governance cho mọi công việc trong dự án. SOP Master nêu **nguyên tắc chung**, định nghĩa **Universal Gates** áp cho mọi task substantive, và **route** sang SOP chuyên biệt cho từng nhóm task.

## 1. Mục đích dự án

> _Mô tả ngắn gọn mục đích dự án — BrSE điền sau khi install._

## 2. Scope làm việc

### Covered
> _Liệt kê các loại công việc trong scope của dự án._

### Not Covered
- Task ngoài repo này.
- Lệch khỏi SOP → xử lý theo § Exceptions.

## Project Priorities

> _Thứ tự ưu tiên của dự án khi các mối quan tâm xung đột (1 = cao nhất) — BrSE điền sau khi install._

1. …
2. …

## 3. General Principles (áp dụng mọi task)
1. **Truth-first.** SOP → AI_WORK_CONTRACT → AIP_PLAN/EXEC → Guidelines → Wiki → Workspace. Ambiguous → spec wins trừ khi có Approved Deviation.
2. **Clarify-before-act.** Yêu cầu mơ hồ → hỏi BrSE, không tự suy đoán.
3. **No silent rewrite of Truth / official Wiki.** Mọi thay đổi Truth phải theo flow candidate → review → apply.
4. **Evidence trail.** Mọi quyết định/handoff phải để lại artifact kiểm chứng trong workspace.

## 4. Universal Gates
Áp dụng cho **mọi task substantive** (tạo deliverable, review deliverable, tạo AIP, research có output, sửa hệ thống, v.v. — không phải thao tác tầm thường như đọc 1 file, trả lời câu hỏi ngắn). Specialized SOP **không được nới lỏng** 3 gate này; chỉ có thể thêm gate chuyên biệt.

### Gate U1 — Confirm-understanding-of-task (HARD GATE)
Trước khi bắt đầu bất kỳ action nào, AI phải viết ra ý hiểu về task (scope, expected output/deliverable, định nghĩa "xong", assumptions) và **dừng chờ BrSE confirm**. Không confirm → không làm.
- **Exception:** BrSE explicit ủy quyền skip ("tin AI, cứ làm"). Ghi ủy quyền vào evidence trail.
- **Evidence:** Workspace findings / dedicated understanding note / chat confirmation.

### Gate U2 — Confirm-understanding-of-input (soft gate)
Nếu task có input artifact (tài liệu, data, code cần đọc để làm) — sau khi đọc, AI viết ra understandings về từng input: ý chính, assumptions, điểm mơ hồ, câu hỏi. Gửi BrSE; có thể tiếp tục song song, BrSE giữ quyền reject.
- Task không có input → gate không áp dụng.

### Gate U3 — Open Points tracking (soft gate)
Khi phát sinh điểm mơ hồ / quyết định cần BrSE chốt → **ghi vào Open Points** trong workspace: câu hỏi, history thảo luận (timestamp), conclusion.
- **Vị trí default:** workspace của task (`.ai-work/workspaces/TASK-*/05_open_questions.md`).
- **Override:** Nếu AIP cụ thể đã quy định cách tracking khác → theo AIP.

## 5. Routing — chọn SOP chuyên biệt

| Task type | Nhận biết bằng | SOP file |
|---|---|---|
| Tạo deliverable dự án (BD / DD / Screen Design / TestCase / v.v.) | Output là artifact kỹ thuật mới; có AI involvement | [SOP_DevelopmentTasks.md](SOP_DevelopmentTasks.md) |
| Review deliverable dự án (peer review, cross-phase review) | Input là deliverable có sẵn; output là đánh giá/feedback | [SOP_DevelopmentTasks.md](SOP_DevelopmentTasks.md) |

**Fallback rule:**
- Task không match rõ dòng nào → AI **hỏi BrSE** trước khi tiến hành. Vẫn áp Universal Gates U1–U3.
- Task hoàn toàn không có SOP chuyên biệt → chỉ follow General Principles + Universal Gates.

## 6. Kết thúc task
1. Chạy `/aiws-lint` để check toàn bộ
2. Archive workspace vào `history/` nếu cần
3. Promote knowledge hữu ích lên wiki

## 7. Quality Gates (cross-cutting)
- [ ] U1 pass — BrSE confirm task understanding (hoặc explicit ủy quyền skip).
- [ ] U2 pass — Input understandings ghi ra (hoặc không có input).
- [ ] U3 pass — Mọi open point có conclusion rõ ràng hoặc status pending+ETA.
- [ ] Đã xác định đúng SOP chuyên biệt (hoặc ghi rõ "chỉ theo Universal Gates").
- [ ] Mọi gate của SOP chuyên biệt đã pass.
- [ ] Evidence trail đầy đủ trong workspace.

## 8. Exceptions & Escalation
- Lệch SOP phải có **Approved Deviation** trong AI_WORK_CONTRACT.md (`.ai-work/truth/AI_WORK_CONTRACT.md`).
- Skip U1 hard gate phải có BrSE explicit ủy quyền, ghi rõ trong evidence trail.
- Không rõ có cần deviation hay không → hỏi BrSE.

## References
- Specialized SOP: [SOP_DevelopmentTasks.md](SOP_DevelopmentTasks.md)
- Task mapping: preset_knowledge/TASK_TO_AIP_MAPPING.md (`.ai-work/preset_knowledge/TASK_TO_AIP_MAPPING.md`)
- Contract: AI_WORK_CONTRACT.md (`.ai-work/truth/AI_WORK_CONTRACT.md`)

## Notes
- Initialized via AI Work System MVP install (`/aiws-pkg install`). Fill §1 Mục đích dự án, §2 Scope và §Project Priorities trước khi sử dụng.
