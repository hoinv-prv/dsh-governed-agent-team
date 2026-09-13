<!--
TEMPLATE — Open Points log (per-task)
Version: v1
Purpose: Satisfy SOP_MASTER Universal Gate U3. Track mọi điểm mơ hồ / câu hỏi / quyết định cần BrSE chốt cho 1 task cụ thể, kèm history thảo luận và conclusion để audit sau.
Usage:
  - Nếu AIP cụ thể đã quy định cách tracking open points khác → theo AIP, không dùng template này.
  - Mỗi open point có ID riêng: `OP-<TASK_ID>-<NN>` (NN đánh số thứ tự, 01, 02, …).
  - Khi đóng open point: fill Conclusion + đổi Status → `resolved` / `deferred` / `rejected`.
  - Không xóa open point đã resolve — giữ lại cho audit trail.
  - Phân biệt: file này = INTERNAL BrSE↔AI working notes. Không lẫn với Q&A formal (external communication với stakeholder).
-->

# Open Points — `<Task ID>` `<Task short title>`

> **Policy (CR-AIWS-2026-07-047 — log-and-continue):** ghi OP vào đây (id · severity · câu hỏi · **giả định đang dùng**) rồi **tiếp tục làm**. Chỉ DỪNG hỏi HUMAN khi OP là **blocker thật** (🔴 Blocker — thiếu nó thì output sai bản chất). Rule #6 (*ambiguous → clarify*) áp cho **ý định task**; rule này áp cho **chi tiết trong lúc làm**. Mọi OP phải đóng (resolved/deferred/rejected) trước khi close AIP (Gate U3).


## Metadata

| Field | Value |
|---|---|
| Task ID | `<TASK-YYYYMMDD-...>` |
| Workspace | `.ai-work/workspaces/TASK-.../` |
| AIP source | `<AIP-EXEC-XXX path>` |
| Maintainer | AI + BrSE (`<HUMAN-username>`) |
| Created | YYYY-MM-DD |
| Last updated | YYYY-MM-DD HH:mm |

## Index

| ID | Status | Severity | Raised at | Summary |
|---|---|---|---|---|
| OP-`<TASK_ID>`-01 | open / pending-brse / resolved / deferred / rejected | 🔴 / 🟠 / 🟡 / 🔵 | YYYY-MM-DD | `<one-line question>` |
|  |  |  |  |  |

Status legend:
- `open` — AI raised, chưa gửi BrSE
- `pending-brse` — đã gửi, chờ BrSE trả lời
- `resolved` — đã có conclusion, action clear
- `deferred` — không chốt bây giờ, hẹn sau (ghi ETA)
- `rejected` — quyết định không xử lý

Severity: 🔴 Blocker · 🟠 Critical · 🟡 Major · 🔵 Minor.

---

## OP-`<TASK_ID>`-01 — `<short title>`

- **Status:** `<open / pending-brse / resolved / deferred / rejected>`
- **Severity:** `<🔴/🟠/🟡/🔵>`
- **Raised at:** YYYY-MM-DD HH:mm
- **Context:** `<file / section / AIP step phát sinh>`

### Question / Issue
`<Mô tả rõ câu hỏi hoặc vấn đề. Cần đủ để người đọc sau hiểu không cần tra lại context.>`

### Options considered (nếu có)
1. `<option A — pros/cons>`
2. `<option B — pros/cons>`

### History

| Timestamp | Actor | Message |
|---|---|---|
| YYYY-MM-DD HH:mm | AI | `<câu hỏi / đề xuất ban đầu>` |
| YYYY-MM-DD HH:mm | BrSE | `<phản hồi>` |
| YYYY-MM-DD HH:mm | AI | `<clarify / option rework>` |

### Conclusion
`<Decision cuối + rationale. Nếu deferred → ghi rõ ETA và lý do defer. Nếu rejected → ghi lý do không xử lý.>`

**Follow-up actions:**
- [ ] `<action 1 — owner — due date>`
- [ ] `<action 2>`

---

<!-- Copy block trên cho mỗi open point mới. -->
