---
artifact_type: sop_specialized
title: SOP — Development Tasks (tạo / review deliverables)
status: active
parent: SOP_MASTER.md
updated_at: <YYYY-MM-DD>
owner: <owner>
---

<!-- Specialized SOP. Routed từ SOP_MASTER. Authoritative zone. No silent rewrite — candidate → review → apply. -->

# SOP — Development Tasks

## Purpose
Quy định phần **specialized** cho task **tạo deliverable** hoặc **review deliverable** trong dự án (thiết kế, test case, v.v.), bổ sung lên Universal Gates của SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`).

## Relationship with SOP_MASTER
> **Áp dụng Universal Gates U1–U3 của SOP_MASTER trước.** SOP này chỉ thêm các rule chuyên biệt (D0, D1, D2) cho task deliverable. Không được nới lỏng Universal Gates.

| Gate | Source | Type | Áp dụng cho |
|---|---|---|---|
| U1 — Confirm-understanding-of-task | SOP_MASTER | **HARD** | Mọi task substantive |
| U2 — Confirm-understanding-of-input | SOP_MASTER | soft | Task có input artifact |
| U3 — Open Points tracking | SOP_MASTER | soft | Mọi task khi phát sinh open point |
| D0 — AIP-first | Đây | **HARD** | Task CREATE hoặc REVIEW deliverable |
| D1 — Review Checklist file | Đây | soft | Task REVIEW deliverable |
| D2 — Self-Review Checklist file | Đây | soft | Task CREATE deliverable |

## Scope
### Covered
- Task **tạo deliverable**: BD (Basic Design), DD (Detail Design), Screen Design, TestCase, IT (Integration Test), UT (Unit Test), TestReport, Review Report, và các artifact kỹ thuật khác của dự án.
- Task **review deliverable**: peer review, cross-phase review, self-review.

### Not Covered
- Task thuần tooling / script / config không sinh deliverable dự án.
- Task research / brainstorming không có deliverable dự án cố định (chỉ áp Universal Gates).

## Specialized Gates

### Gate D0 — AIP-first (HARD GATE)
Trước khi bắt đầu bất kỳ task tạo hoặc review deliverable nào, AI **bắt buộc** phải:
1. Xác định loại task trong TASK_TO_AIP_MAPPING.md (`.ai-work/preset_knowledge/TASK_TO_AIP_MAPPING.md`) — mục **BrSE Preset Tasks / Mandatory AIP Policy**.
2. Tạo AIP bằng `/aiws-aip create` (nếu chưa có AIP cho task này).
3. Khởi động execution bằng `/aiws-aip run` trước khi bắt tay vào tạo/review deliverable.

**Không được tạo hoặc review deliverable trực tiếp mà không có AIP kiểm soát.**

- **Exception:** BrSE explicit ủy quyền skip ("tin AI, cứ làm"). Ghi ủy quyền vào evidence trail.
- **Evidence:** Workspace đã được init; AIP đã tồn tại và ở trạng thái active.
- **Lý do:** Đảm bảo scope confirmation, open points tracking, và BrSE checkpoint trước khi output đến downstream (per TASK_TO_AIP_MAPPING §Mandatory AIP Policy).

### Gate D1 — Review Checklist file (soft gate, áp dụng task REVIEW)
AI list các **viewpoints/criteria** sẽ dùng để review thành **file riêng, tách khỏi AIP**, có cột **OK/NG/Note** để điền khi review.
- File lưu trong workspace của task, là deliverable phụ.
- **Mục đích:** Có trail rõ ràng về những gì đã được kiểm tra.

### Gate D2 — Self-Review Checklist file (soft gate, áp dụng task CREATE)
Sau khi tạo deliverable, AI list các **self-review points** thành **file riêng, tách khỏi AIP**, có cột **OK/NG/Note**, và tự điền trước khi handoff.
- File lưu trong workspace của task.
- **Mục đích:** Deliverable được self-check trước khi BrSE review.

## Phương châm (design intent)
- D0 là **hard gate** không thể skip trừ khi có explicit BrSE ủy quyền — tương đương U1.
- D1/D2 là soft gate: AI tự tạo mà không cần nhắc; BrSE có quyền reject trong soft window.
- Artifact phụ (checklist) **tách khỏi AIP** để có thể điền trạng thái độc lập.

## Roles & Responsibilities
- **BrSE:** Có quyền ủy quyền skip D0 (phải explicit). Có quyền reject D1/D2 trong soft window. Chốt nội dung checklist cụ thể theo dự án.
- **AI:** Không bắt đầu deliverable task nếu chưa có AIP (D0). Tự sinh checklist file mà không cần được nhắc (D1/D2). Áp đầy đủ Universal Gates (U1 hard, U2/U3 soft) theo SOP_MASTER.

## Quality Gates
- [ ] Universal Gates U1–U3 đã pass (xem SOP_MASTER § Universal Gates (`.ai-work/truth/SOP_MASTER.md`)).
- [ ] D0 pass — AIP đã được tạo (`/aiws-aip create`) và execution đã khởi động (`/aiws-aip run`), hoặc BrSE explicit ủy quyền skip.
- [ ] D1 (review task) — Review Checklist file tồn tại trong workspace, có cột OK/NG/Note, đã điền đủ trước đóng task.
- [ ] D2 (create task) — Self-Review Checklist file tồn tại trong workspace, có cột OK/NG/Note, đã điền đủ trước handoff.

## Exceptions & Escalation
- Bỏ qua D0 phải có BrSE explicit ủy quyền, ghi rõ trong evidence trail.
- Bỏ qua D1/D2 phải có Approved Deviation trong AI_WORK_CONTRACT.md (`.ai-work/truth/AI_WORK_CONTRACT.md`).
- Universal Gates không thể bỏ qua ở đây (phải escalate qua SOP_MASTER).

## References
- Parent: SOP_MASTER.md (`.ai-work/truth/SOP_MASTER.md`)
- Contract: AI_WORK_CONTRACT.md (`.ai-work/truth/AI_WORK_CONTRACT.md`)
- Task mapping: preset_knowledge/TASK_TO_AIP_MAPPING.md (`.ai-work/preset_knowledge/TASK_TO_AIP_MAPPING.md`)
- Preset EXEC: preset_knowledge/aip_exec/design/AIP_EXEC_CreateDesignDoc.md (`.ai-work/preset_knowledge/aip_exec/design/AIP_EXEC_CreateDesignDoc.md`)
- Preset EXEC: preset_knowledge/aip_exec/testcase/AIP_EXEC_CreateTestCase.md (`.ai-work/preset_knowledge/aip_exec/testcase/AIP_EXEC_CreateTestCase.md`)
- Preset EXEC: preset_knowledge/aip_exec/review/AIP_EXEC_ReviewDesign.md (`.ai-work/preset_knowledge/aip_exec/review/AIP_EXEC_ReviewDesign.md`)
- Preset EXEC: preset_knowledge/aip_exec/review/AIP_EXEC_ReviewTestCase.md (`.ai-work/preset_knowledge/aip_exec/review/AIP_EXEC_ReviewTestCase.md`)
