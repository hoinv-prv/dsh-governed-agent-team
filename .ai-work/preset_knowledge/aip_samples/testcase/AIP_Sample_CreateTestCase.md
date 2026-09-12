# AIP_Sample_CreateTestCase.md

**Version:** v1.0
**Date:** 2026-04-24
**Target Task:** Tạo tài liệu test case (Markdown format)
**Recommended AIP Type:** PLAN → EXEC (hoặc EXEC trực tiếp nếu scope đã rõ)
**Linked EXEC Preset:** `aip_exec/testcase/AIP_EXEC_CreateTestCase.md`

---

## 1. Vì sao task này phải có AIP

Task **"tạo test case"** không chỉ là "liệt kê các bước test". Nếu làm không đúng, QA waste time test sai chỗ, bugs vẫn bị miss.

Thực tế, tạo test case tốt bao gồm:
- Phân tích design document / requirements để xác định testable items
- Thiết kế test scenarios đủ coverage (không chỉ happy path)
- Xác định boundary conditions và error cases không hiển nhiên
- Viết expected results cụ thể, verifiable (không phải "system works")
- Đảm bảo traceability: mỗi requirement có ít nhất 1 TC

**Rủi ro không dùng AIP:**
- AI viết TC theo "cảm giác" — thiếu boundary cases, thiếu error handling
- Expected results mơ hồ → QA không biết pass/fail như thế nào
- Không có traceability → requirements bị bỏ sót mà không ai biết
- Không có BrSE checkpoint → AI assume business rules sai → TCs sai toàn bộ

AIP cho task này giúp:
- Confirm scope và coverage level trước khi bắt đầu (STEP-00 gate)
- Structure quá trình: phân tích → design scenarios → viết → coverage review
- Track business rules chưa rõ thay vì assume
- Tạo coverage matrix để verify không bỏ sót requirements

---

## 2. AIP type đề xuất

### 2.1. PLAN → EXEC (khi scope phức tạp)

Dùng PLAN khi:
- Feature lớn, nhiều scenarios phức tạp, cần plan test approach trước
- Cần quyết định coverage strategy (test theo risk? theo priority?)
- Cần phân tích gap giữa design và requirements trước khi viết TC

### 2.2. EXEC trực tiếp (khi scope đã rõ)

Dùng trực tiếp EXEC (`AIP_EXEC_CreateTestCase.md`) khi:
- Feature scope rõ, có design doc làm input
- Coverage level đã thống nhất
- Flow: copy preset → fill context → execute STEP-00 → STEP-05

### 2.3. Rule bắt buộc

> **Tạo tài liệu test case với AI involvement BẮT BUỘC có AIP trước khi thực hiện.**
>
> Không được để AI tạo test cases mà không có AIP — không có scope confirmation, không có coverage standard, không có BrSE checkpoint trên expected results.

---

## 3. Bộ Q&A để clarify task (STEP-00)

| # | Câu hỏi | Mục đích |
|---|---|---|
| Q1 | Feature / module / screen nào cần test? | Xác định scope |
| Q2 | Input artifact: design doc (BD/DD/Screen), requirements, hay cả hai? | Xác định baseline |
| Q3 | Coverage level: basic / standard / comprehensive? | Quyết định depth |
| Q4 | Có acceptance criteria chính thức không? | Làm anchor cho coverage |
| Q5 | Dự án có TC template riêng không (fields, format)? | Conform to standards |
| Q6 | Test case này cho QA manual hay có automation plan? | Ảnh hưởng detail level |
| Q7 | Upstream input có confirmed chưa? Design doc đã sign off chưa? | Tránh làm TC trên design còn thay đổi |

---

## 4. Coverage levels

| Level | Scenarios | Khi nào dùng |
|---|---|---|
| **Basic** | Normal cases (happy path) only | Prototype, quick verification, low-risk features |
| **Standard** | Normal + Abnormal (invalid input, error condition) | Typical feature development |
| **Comprehensive** | Normal + Abnormal + Boundary + Error handling | Critical features, security-sensitive, payment, data integrity |

> Default cho development features: **Standard**.

---

## 5. Ví dụ TC format (generic)

```markdown
## TC-001: Đăng nhập thành công với email và password hợp lệ
**Category:** Normal
**Priority:** High
**Preconditions:** User đã có account, đang ở màn hình Login
**Test Steps:**
1. Nhập email hợp lệ vào field Email
2. Nhập password đúng vào field Password
3. Click button "Đăng nhập"
**Expected Result:** Hệ thống redirect đến trang Home. Hiển thị tên user ở header.
**Test Data:** email: test@example.com, password: ValidPass123

## TC-002: Đăng nhập thất bại với password sai
**Category:** Abnormal
**Priority:** High
**Preconditions:** User đã có account, đang ở màn hình Login
**Test Steps:**
1. Nhập email hợp lệ
2. Nhập password sai
3. Click "Đăng nhập"
**Expected Result:** Hiển thị error message "Email hoặc mật khẩu không đúng". Không redirect.
**Test Data:** email: test@example.com, password: WrongPass

## TC-003: Validate field Password — boundary max length
**Category:** Boundary
**Priority:** Medium
**Preconditions:** Đang ở màn hình Login
**Test Steps:**
1. Nhập password = 128 ký tự (max allowed)
2. Click "Đăng nhập"
**Expected Result:** Hệ thống accept input, xử lý bình thường (không bị truncate).
**Test Data:** password: [128-char string]
```

---

## 6. Khi nào KHÔNG cần AIP

- BrSE tự viết TC toàn bộ, không có AI involvement
- Thêm 1-2 TC vào document có sẵn cho change nhỏ
- Review TC của người khác → dùng `AIP_EXEC_ReviewTestCase.md`

---

## 7. Linked EXEC Preset

Copy và fill [AIP_EXEC_CreateTestCase.md](../../aip_exec/testcase/AIP_EXEC_CreateTestCase.md):
1. Điền `project`, `owner`, `plan_source`
2. Điền coverage level vào Workspace Preconditions
3. Điền paths vào References to Read First
4. Execute STEP-00 → STEP-05
