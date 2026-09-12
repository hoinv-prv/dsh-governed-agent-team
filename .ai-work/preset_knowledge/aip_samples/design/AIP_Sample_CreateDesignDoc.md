# AIP_Sample_CreateDesignDoc.md

**Version:** v1.0
**Date:** 2026-04-24
**Target Task:** Tạo tài liệu design (BD / DD / Screen Design)
**Recommended AIP Type:** PLAN → EXEC (hoặc EXEC trực tiếp nếu scope đã rõ)
**Linked EXEC Preset:** `aip_exec/design/AIP_EXEC_CreateDesignDoc.md`

---

## 1. Vì sao task này phải có AIP

Task **"tạo tài liệu design"** là artifact quan trọng trong development process — nó là input trực tiếp cho dev, QA, và offshore team. Nếu làm sai hoặc thiếu, toàn bộ downstream bị ảnh hưởng.

Đây không chỉ là việc "AI viết một document":
- Phải phân tích đúng requirements trước khi thiết kế
- Phải đưa ra design decisions và ghi lại rationale
- Phải nhận ra ambiguities trong requirements trước khi chúng trở thành bugs
- Phải đảm bảo design nhất quán với system architecture
- Phải usable cho downstream: dev có thể implement, QA có thể test, offshore có thể follow

**Rủi ro không dùng AIP:**
- AI "bịa" expected behavior khi requirements không rõ — error ẩn vào document
- BrSE không có checkpoint sớm → phát hiện vấn đề khi đã viết xong hết
- Thiếu traceability: không biết design section nào cover requirement nào
- Open points không được track → trôi vào implementation mà không giải quyết

AIP cho task này giúp:
- Chốt scope và loại document trước khi bắt đầu (STEP-00 gate)
- Structure quá trình phân tích → thiết kế → review
- Track open points và design decisions rõ ràng
- Tạo checkpoint BrSE trước khi finalize

---

## 2. AIP type đề xuất

### 2.1. PLAN → EXEC (khi scope chưa hoàn toàn rõ)

Dùng PLAN khi:
- Module mới, chưa có design precedent
- Cần research architecture/existing code trước khi thiết kế
- Chưa chắc nên làm BD hay DD trước
- Cần đánh giá tradeoffs trước khi commit vào một approach

### 2.2. EXEC trực tiếp (khi scope đã rõ)

Dùng trực tiếp EXEC (`AIP_EXEC_CreateDesignDoc.md`) khi:
- Design type đã xác nhận (BD / DD / Screen)
- Module scope đã chốt
- Requirements đã confirm
- Flow: copy preset → fill context → execute

### 2.3. Rule bắt buộc

> **Tạo tài liệu design (BD/DD/Screen Design) với AI involvement BẮT BUỘC có AIP trước khi thực hiện.**
>
> Không được để AI draft design document mà không có AIP — không có scope confirmation, không có open points tracking, không có BrSE checkpoint.

---

## 3. Bộ Q&A để clarify task (STEP-00)

Trước khi bắt đầu, confirm các điểm sau với BrSE:

| # | Câu hỏi | Mục đích |
|---|---|---|
| Q1 | Loại document: BD, DD, hay Screen Design? | Xác định structure, depth, scope |
| Q2 | Module / feature / screen nào? Scope cụ thể đến đâu? | Tránh scope creep |
| Q3 | Inputs có sẵn: requirements doc (RD), user story, existing design? | Xác định baseline để thiết kế |
| Q4 | Architecture context có sẵn không (tech stack, module boundaries)? | Cần thiết cho BD/DD |
| Q5 | Dự án có design template riêng không? | Conform to project standards |
| Q6 | Output ngôn ngữ: Tiếng Nhật (cho KH) hay Tiếng Việt (nội bộ)? | Tránh làm lại |
| Q7 | Downstream consumer: dev, QA, offshore? Yêu cầu gì đặc thù? | Đảm bảo usability |

---

## 4. Mapping requirements → design

Với mỗi task tạo design doc, AI cần tạo traceability:

```
Requirement R-001 → BD Section 3.2 (Order Flow)
Requirement R-002 → DD Function processOrder() + Screen S-01
Acceptance Criteria AC-001 → Screen S-01 Field Validation
```

Nếu không có requirement IDs → AI tạo implicit mapping (mô tả, không có ID cụ thể), vẫn phải đủ để BrSE verify.

---

## 5. Khi nào KHÔNG cần AIP

- BrSE tự viết toàn bộ, không có AI involvement
- Sửa nhỏ: thêm 1 field vào màn hình có sẵn, thêm 1 note
- Refactor format (không thay đổi nội dung)

---

## 6. Linked EXEC Preset

Copy và fill [AIP_EXEC_CreateDesignDoc.md](../../aip_exec/design/AIP_EXEC_CreateDesignDoc.md):
1. Điền `project`, `owner`, `plan_source`
2. Điền loại document vào Objective section
3. Điền paths vào References to Read First
4. Execute STEP-00 → STEP-05
