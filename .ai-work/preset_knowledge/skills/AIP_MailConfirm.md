# AIP_mail-confirm.md

**Version:** v1.1
**Date:** 2026-04-27
**AIP Type:** Standalone AIP
**Purpose:** Hướng dẫn AI soạn mail/chat confirm yêu cầu với KH Nhật — có Clarifying Mode và Plan Mode trước khi thực thi.

---

## Cách dùng file này

Paste nội dung yêu cầu (tiếng Việt) vào chat cùng với file này. AI sẽ chạy theo flow bên dưới — hỏi từng câu một để làm rõ input, hiển thị plan, chờ confirm rồi mới thực thi.

---

## PHASE 0 — ISMS Check (bắt buộc, chạy đầu tiên)

Ngay khi nhận input, AI **phải scan toàn bộ nội dung** trước khi làm bất cứ điều gì khác.

Nếu phát hiện PII → **AI tự động thay thế luôn**, sau đó thông báo cho BrSE biết đã thay gì. Không dừng lại chờ BrSE chỉnh tay.

| Dấu hiệu trong input                       | Thay thế bằng                    |
| ------------------------------------------ | -------------------------------- |
| Tên người Nhật (Yamamoto, Tanaka, 田中...) | `担当者様` / `お客様`            |
| Tên công ty đối tác thuộc diện NDA         | `お客様` / `クライアント`        |
| Email / SĐT thật                           | `(省略)`                         |
| Mật khẩu / API key / token                 | `(省略)`                         |
| Nội dung hợp đồng / tài chính chưa công bố | mô tả chung ở mức loại thông tin |

**Mẫu thông báo sau khi thay:**

```
⚠️ ISMS Check — AI đã tự động ẩn danh hóa các thông tin sau:

   · "Yamamoto"      → "担当者様"
   · "株式会社XYZ"   → "お客様"
   (liệt kê tất cả những gì đã thay)

Nội dung sẽ được xử lý với thông tin đã ẩn danh hóa ở trên.
Nếu có thông tin nào bị thay sai → vui lòng thông báo để điều chỉnh.
```

> ✅ Nếu input không có PII → ghi "ISMS OK" và chuyển sang Phase 1.

---

## PHASE 1 — Clarifying Mode (popup AskUserQuestion)

Sau khi ISMS OK, AI gọi tool **AskUserQuestion** với 4 câu hỏi cùng lúc — hiển thị popup để BrSE click chọn, không hỏi lần lượt.

**Mapping câu hỏi → AskUserQuestion:**

| #   | question                        | header         | options                                  |
| --- | ------------------------------- | -------------- | ---------------------------------------- |
| 1   | Bạn muốn gửi qua kênh nào?      | Kênh gửi       | Email / Chat                             |
| 2   | Nội dung thuộc loại nào?        | Loại yêu cầu   | Bug / Spec / Question / Deadline         |
| 3   | Có deadline cần KH reply không? | Deadline reply | Hôm nay / Ngày khác (ghi rõ) / Không gấp |
| 4   | Tên BrSE/Comtor ký cuối mail?   | Người ký       | Bỏ qua (Other = điền tên)                |

> 💡 **Quy tắc Clarifying Mode:**
>
> - Gọi AskUserQuestion **một lần duy nhất** với đủ 4 câu — không hỏi lần lượt
> - Nếu input đã có thông tin rõ ràng → vẫn hiển thị popup nhưng ghi chú "(gợi ý từ input)" trong description của option tương ứng
> - Nếu BrSE chọn "Ngày khác" cho deadline → hỏi thêm ngày cụ thể trước khi sang Phase 2
> - Sau khi có đủ 4 đáp án → chuyển sang Phase 2

---

## PHASE 2 — Plan Mode (hiển thị plan, chờ confirm)

Sau khi có đủ thông tin từ Clarifying Mode, AI hiển thị plan đầy đủ trước khi thực thi.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【PLAN — Vui lòng xác nhận trước khi chạy】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Thông tin đã thu thập:
   · Kênh gửi    : [Email / Chat]
   · Loại yêu cầu: [Bug / Spec / Question / Deadline]
   · Deadline    : [Có — hôm nay / Có — [ngày] / Không]
   · Người ký    : [Tên / Không có]

🗂️ Các bước sẽ thực hiện:
   [1] Output Input Understandings (5 thành phần) — tiếng Việt
   [2] Chờ BrSE xác nhận understandings
   [3] Draft [email/chat] — loại [Bug/Spec/Question/Deadline]
       · Ưu tiên điểm 🔴 BLOCK trước
       · Tối đa 3–5 câu hỏi nếu có open points
       · Có/không có deadline reply tùy thông tin đã thu thập
   [4] Review Viewpoint (9 tiêu chí)
   [5] Self review & chỉnh sửa nếu cần
   [6] Output draft cuối — có placeholder [お客様名] / [会社名]
   [7] Downstream note

- [ ] **OK** — bắt đầu thực thi
- [ ] **Chỉnh** — nêu điểm cần sửa trước khi chạy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> 🔴 **Không được bắt đầu thực thi khi chưa nhận được "OK" từ BrSE.**

---

## PHASE 3 — Execution (thực thi theo plan đã confirm)

Sau khi BrSE gõ "OK", thực thi tuần tự theo các bước đã nêu trong Plan.

### Bước 1 — Output Input Understandings

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【INPUT UNDERSTANDINGS — Vui lòng xác nhận】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 1. Understanding Summary
   [Tóm tắt ngắn gọn nội dung yêu cầu/tình huống — 2-3 câu]

❓ 2. Grouped Open Points (block-first)
   [Nhóm A — Về nghiệp vụ / spec]
     · 🔴 [BLOCK] [điểm đang chặn dev]
          - Lý do hỏi : [...]
          - Ý đồ hỏi  : [...]
          - Thời hạn  : [nếu cần gấp]
     · 🟡 [điểm chưa rõ nhưng chưa block]
   (Nếu không có → ghi: Không có — thông tin đã đủ)

🎯 3. Expected Answer Types
   · [Câu hỏi A] → Cần: [Yes/No / số cụ thể / mô tả / tên cụ thể]

⚠️ 4. Downstream Impact
   · Nếu [điểm X] chưa rõ → [task Y] không thể tiến hành

💡 5. Assumptions Being Used
   · [Giả định đang áp dụng / Không có giả định đặc biệt]

📊 Input Understanding Status: [ PENDING BrSE CONFIRMATION ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] **OK** — understandings đúng, tiếp tục
- [ ] **Chỉnh** — nêu điểm cần sửa
```

---

### Bước 2 — Draft email/chat

Soạn theo kênh và loại yêu cầu đã xác nhận ở Plan Mode.

**Quy tắc chọn điểm hỏi:**

- Ưu tiên 🔴 BLOCK trước — bắt buộc có trong lần gửi này
- Tối đa 3–5 điểm mỗi lần — defer phần còn lại, ghi vào Downstream note
- Nếu có deadline → nêu rõ ngày và lý do

**Template Email — 確認事項:**

```
▼ 確認事項

実装を進めるにあたり、以下の点をご確認いただけますでしょうか。

①[Câu hỏi 1]
　※[Lý do hỏi nếu cần]
　→[Ý đồ / downstream nếu hữu ích]

②[Câu hỏi 2 nếu có]
　※[Lý do hỏi nếu cần]

[Nếu có deadline:]
お手数ですが、[〇月〇日まで / なるべくお早めに] にご回答いただけますと幸いです。
（[lý do deadline]）

ご回答いただき次第、[bước tiếp theo].
```

**Template Chat — 確認事項:**

```
【確認事項】
以下の点をご確認いただけますでしょうか。

・[Câu hỏi 1]（※[Lý do ngắn gọn nếu cần]）
・[Câu hỏi 2 nếu có]

[Nếu có deadline:]
お手数ですが、[〇日まで / なるべくお早めに] にご回答いただけますと助かります。

ご回答後、[bước tiếp theo].
```

---

### Bước 3 — Review Viewpoint (9 tiêu chí)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【REVIEW VIEWPOINT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅/❌  Clarification objective rõ chưa?
✅/❌  Câu hỏi đã grouped hợp lý chưa?
✅/❌  Lý do hỏi có được nêu không (nếu cần)?
✅/❌  Ý đồ hỏi / downstream impact có rõ không (nếu cần)?
✅/❌  Thời hạn reply có được nêu không (nếu cần gấp)?
✅/❌  Expected answer type có rõ không?
✅/❌  Open points: hỏi đủ chưa, có hỏi thừa không?
✅/❌  Audience/tone phù hợp chưa?
✅/❌  Follow-up handling rõ chưa?

📊 Review Viewpoint Status: [ PASS / NEEDS REVISION ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Nếu có `❌` → tự chỉnh draft trước khi output, giải thích ngắn điểm đã sửa.

---

### Bước 4 — Output draft cuối

Output bản draft tiếng Nhật hoàn chỉnh. Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật.

> 🔴 **Trước khi gửi, BrSE thực hiện 3 việc ngoài AI:**
>
> 1. Review toàn bộ nội dung — keigo, ngày tháng, hướng xử lý, không có hallucination
> 2. Điền placeholder bằng tên thật trong email client / chat tool
> 3. Gửi sau khi đã review đầy đủ

---

### Bước 5 — Downstream note

```
📌 Downstream note:
   Sau khi nhận reply từ KH → [hành động cụ thể]
   Nếu không reply trong [X ngày] → cân nhắc follow-up hoặc chuyển sang email/chat

📋 Ghi nhận sử dụng AI (VJP-ISMS-AI-FO001 Điều 3.3):
   Mail/chat này được soạn với hỗ trợ AI.
   Nếu forward hoặc trích dẫn trong tài liệu chính thức → ghi chú theo quy định VTI.
```

---

## Tóm tắt flow

```
[INPUT]
   ↓
[PHASE 0] ISMS Check — scan PII → tự động ẩn danh hóa + thông báo BrSE → tiếp tục
   ↓
[PHASE 1] Clarifying Mode — hiển thị 4 mục một lần → BrSE chọn + confirm 1 lần
   ↓
[PHASE 2] Plan Mode — hiển thị plan đầy đủ → chờ BrSE gõ "OK"
   ↓
[PHASE 3] Execution
   ├─ Bước 1: Input Understandings → chờ BrSE confirm
   ├─ Bước 2: Draft email/chat
   ├─ Bước 3: Review Viewpoint (9 tiêu chí)
   ├─ Bước 4: Output draft cuối (có placeholder)
   └─ Bước 5: Downstream note
```

---

## Lưu ý vận hành

- Clarifying Mode: hỏi **từng câu một**, không hỏi gộp, không tự suy đoán
- Plan Mode: **không thực thi khi chưa có "OK"** từ BrSE
- Block-first: luôn ưu tiên điểm 🔴 BLOCK trong draft
- Giới hạn **3–5 điểm** mỗi lần gửi — defer phần còn lại
- Nội dung formal/contractual → Email, không dùng Chat
- Placeholder `[お客様名]` / `[会社名]` → BrSE tự điền **ngoài AI**
- AI không thay thế trách nhiệm review của BrSE
