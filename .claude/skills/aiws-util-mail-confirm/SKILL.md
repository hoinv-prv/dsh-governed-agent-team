---
name: aiws-util-mail-confirm
description: >
  BrSE/Comtor向けスキル: ベトナム語の顧客要求内容から日本語の確認メッセージ（メール・チャット）を自動生成する。
  Use this skill whenever the user (BrSE, Comtor, PM, or developer) wants to:
  - Write a Japanese confirmation message or email to a Japanese client
  - Confirm understanding of a customer request in Japanese
  - Draft a chat/email reply in Japanese from Vietnamese content
  - Generate a 確認メール, 返信メール, or confirm chat message in Japanese
  - Respond to Japanese clients about bugs, spec changes, deadlines, or clarifying questions
  Trigger on phrases like: "viết confirm tiếng Nhật", "gửi mail confirm cho khách Nhật", "soạn chat xác nhận",
  "reply tiếng Nhật", "confirm yêu cầu bằng tiếng Nhật", "tạo email Nhật", "clarification tiếng Nhật", etc.
---

# aiws-util-mail-confirm — Tạo tin nhắn xác nhận tiếng Nhật cho BrSE/Comtor

Skill này giúp BrSE/Comtor tự động soạn thảo tin nhắn confirm yêu cầu khách hàng Nhật từ nội dung tiếng Việt. Output là tiếng Nhật với keigo vừa phải (丁寧語), phù hợp môi trường IT offshore.

Skill tuân theo chuẩn **AIP (AI Process)** với flow 8 bước: Input Understandings → BrSE Confirmation → Draft → Review Viewpoint → Self Review → Finalize.

---

## Flow 8 bước (AIP-aligned)

```
[1] Read sources
[2] Output Input Understandings  ← AI phân tích đầy đủ trước khi viết
[3] BrSE confirms understandings ← Bắt buộc trước khi draft
[4] Draft email/chat
[5] Create Review Viewpoint       ← Kiểm tra chiều sâu, không chỉ keigo
[6] Self Review
[7] Finalize / present output
[8] Track reply & downstream note ← Gợi ý bước tiếp theo
```

---

## ⚠️ Kiểm tra tuân thủ bắt buộc trước khi nhập (VTI ISMS)

Trước khi nhập bất kỳ nội dung nào, BrSE **phải tự kiểm tra** theo ma trận phân loại thông tin (VJP-ISMS-AI-TR002 Phần 3). Skill sẽ nhắc lại ở Bước 1, nhưng trách nhiệm thuộc về người dùng.

```
🔴 TUYỆT ĐỐI KHÔNG nhập vào AI:
   · Tên thật / email / SĐT của người liên lạc phía khách hàng Nhật (PII)
   · Tên công ty đối tác nếu thuộc diện NDA
   · Nội dung hợp đồng, giá trị tài chính chưa công bố
   · Mật khẩu, API key, token xác thực bất kỳ

🟡 THAY VÀO ĐÓ → dùng mô tả chung khi nhập vào AI:
   · Tên người: 田中様 → "担当者様" / "お客様"
   · Tên công ty: 株式会社XYZ → "お客様" / "クライアント"
   · Email: hanako@client.co.jp → (bỏ qua)

✅ TÊN THẬT sẽ được BrSE TỰ ĐIỀN vào draft SAU KHI AI output xong
   (xem Bước 7 — Finalize)

❓ Không chắc thông tin có được nhập không → hỏi AI Promotion Lead bộ phận
```

> 💡 **Tại sao?** Dù hợp đồng Enterprise cam kết không dùng data để train AI, nhưng thông tin vẫn được truyền qua internet đến máy chủ Anthropic (TR002). Nếu hệ thống bị tấn công, tên khách hàng/công ty có thể bị lộ. Tên thật trong **mail gửi đi** là hoàn toàn bình thường — vấn đề chỉ là không để nó đi qua AI.

---

## Chọn kênh gửi: Chat hay Email?

Trước khi bắt đầu, xác định kênh phù hợp:

| Tình huống | Kênh |
|---|---|
| Cần unblock dev nhanh, hỏi 1–3 điểm cụ thể | ✅ **Chat** |
| Câu hỏi đơn giản, KH có thể reply ngay | ✅ **Chat** |
| Nội dung phức tạp, nhiều điểm cần giải thích | ✅ **Email** |
| Formal / contractual (cam kết, hợp đồng, deadline chính thức) | ✅ **Email** |
| Cần lưu vết rõ ràng, có thể forward / trích dẫn sau | ✅ **Email** |

> 💡 Nếu không chắc → dùng **Email** để an toàn hơn.

---

## Bước 1 — Kiểm tra ISMS & Thu thập thông tin đầu vào

### 🔴 Bắt buộc: Scan PII trước khi xử lý

Ngay khi nhận input, AI **phải scan toàn bộ nội dung** để phát hiện thông tin cá nhân (PII) hoặc thông tin mật. Nếu phát hiện → **AI tự động thay thế luôn**, sau đó thông báo cho BrSE biết đã thay gì. Không dừng lại chờ BrSE chỉnh tay.

| Dấu hiệu trong input | Thay thế bằng |
|---|---|
| Tên người Nhật (Yamamoto, Tanaka, 田中...) | `担当者様` / `お客様` |
| Tên công ty đối tác thuộc diện NDA | `お客様` / `クライアント` |
| Email / SĐT thật | `(省略)` |
| Mật khẩu / API key / token | `(省略)` |
| Nội dung hợp đồng / giá trị tài chính chưa công bố | mô tả chung ở mức loại thông tin |

**Mẫu thông báo sau khi thay:**
```
⚠️ ISMS Check — AI đã tự động ẩn danh hóa các thông tin sau:

   · "Yamamoto"      → "担当者様"
   · "株式会社XYZ"   → "お客様"
   (liệt kê tất cả những gì đã thay)

Nội dung sẽ được xử lý với thông tin đã ẩn danh hóa ở trên.
Nếu có thông tin nào bị thay sai → vui lòng thông báo để điều chỉnh.
```

> ✅ Nếu input không có PII → ghi "ISMS OK" và tiếp tục thu thập thông tin bên dưới.

---

### Thu thập thông tin đầu vào

Sau khi ISMS OK, kiểm tra input đã có đủ thông tin chưa. Nếu thiếu → hỏi inline ngay trong chat, không tự suy đoán:

| # | Thông tin cần có | Nếu thiếu → hỏi |
|---|---|---|
| 1 | Kênh gửi | "Bạn muốn gửi qua Email hay Chat?" |
| 2 | Loại yêu cầu | "Nội dung này là Bug / Spec / Question / Deadline?" |
| 3 | Deadline reply | "Có deadline cần KH reply không? Nếu có ghi rõ ngày." |
| 4 | Tên BrSE ký | "Tên BrSE/Comtor ký cuối mail là gì? (bỏ qua nếu không cần)" |

> 💡 **Quy tắc:**
> - Nếu input đã có thông tin rõ → ghi nhận, không hỏi lại
> - Hỏi tất cả những gì còn thiếu trong **1 tin nhắn duy nhất**, không hỏi lần lượt từng tin
> - Chờ BrSE trả lời đủ rồi mới tiếp tục Bước 2

> 💡 **Nhắc nhở:** AI sẽ tự dùng placeholder `[お客様名]` / `[会社名]` trong draft. BrSE chỉ cần điền tên thật vào **sau khi** đã review và copy ra ngoài.

---

## Bước 2 — Output Input Understandings (bắt buộc)

Đây là bước quan trọng nhất. Trước khi viết bất kỳ câu tiếng Nhật nào, AI **phải output đầy đủ 5 thành phần** sau bằng tiếng Việt để BrSE kiểm tra:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【INPUT UNDERSTANDINGS — Vui lòng xác nhận】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📤 Kênh gửi   : [Email / Chat (Google Chat / Chatwork / Slack)]
📂 Loại output: [Bug / Spec / Question / Deadline]

📋 1. Understanding Summary (Tóm tắt đã hiểu)
   [Tóm tắt ngắn gọn nội dung yêu cầu/tình huống — 2-3 câu]
   ⚠️  Lưu ý: Không hiển thị tên thật khách hàng / tên công ty đối tác NDA
              trong phần này — dùng "担当者様", "お客様", "クライアント" thay thế

❓ 2. Grouped Open Points (Điểm chưa rõ — phân nhóm, block-first)
   [Nhóm A — Về nghiệp vụ / spec]
     · 🔴 [BLOCK] [điểm đang chặn dev — cần hỏi ngay]
          - Lý do hỏi: [vì chỗ A và chỗ B đang mâu thuẫn / chỗ A liên quan B mà B chưa rõ...]
          - Ý đồ hỏi: [kết quả trả lời sẽ ảnh hưởng đến tài liệu / task nào]
          - Thời hạn: [nếu cần reply gấp — ghi rõ, nếu không thì bỏ qua]
     · 🟡 [điểm chưa rõ nhưng chưa block]
          - Lý do hỏi: [...]
          - Ý đồ hỏi: [...]
   [Nhóm B — Về kỹ thuật / môi trường]
     · 🔴 [BLOCK] [điểm đang chặn dev]
          - Lý do hỏi: [...]
          - Ý đồ hỏi: [...]
   (Nếu không có open points → ghi: Không có — thông tin đã đủ)

   **Block-first:** Đánh dấu 🔴 BLOCK cho điểm nào mà nếu chưa có câu trả lời thì dev không thể tiến hành. Những điểm này phải được hỏi trong lần gửi này. Điểm không block có thể defer sang lần sau.

   ⚠️  Nếu open points liên quan đến nội dung NDA / bí mật kinh doanh
       → chỉ mô tả ở mức "loại thông tin cần hỏi", không paste nguyên văn nội dung mật

🎯 3. Expected Answer Types (Loại câu trả lời cần nhận)
   · [Câu hỏi A] → Cần: [ví dụ: lựa chọn Yes/No / số cụ thể / mô tả chi tiết]
   · [Câu hỏi B] → Cần: [ví dụ: ngày tháng / file đính kèm / xác nhận bằng lời]

⚠️  4. Downstream Impact (Nếu chưa làm rõ thì ảnh hưởng gì)
   · Nếu [điểm X] chưa được xác nhận → [task Y] không thể tiến hành
   · Nếu [điểm Z] chưa rõ → có thể estimate sai / làm lại

💡 5. Assumptions Being Used (Giả định đang áp dụng)
   · [Giả định 1: ví dụ "Giả sử lỗi xảy ra trên tất cả môi trường, không chỉ staging"]
   · [Nếu không có giả định → ghi: Không có giả định đặc biệt]

📊 Input Understanding Status: [ PENDING BrSE CONFIRMATION ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Nếu đúng, gõ "OK" hoặc "xác nhận". Nếu cần chỉnh, nêu điểm cần sửa.
```

**Quy tắc quan trọng:** Không được chuyển sang Bước 3 (draft) khi chưa có xác nhận từ BrSE. Nếu input quá rõ ràng và BrSE đã nêu tất cả thông tin, có thể gộp bước này với lời xác nhận trong cùng một output — nhưng vẫn phải hiển thị đủ 5 thành phần.

---

## Bước 3 — BrSE confirms understandings

Nhận xác nhận từ BrSE (gõ "OK", "xác nhận", hoặc nêu chỉnh sửa). Sau khi confirmed → cập nhật status thành `[ CONFIRMED ]` và tiến hành draft.

---

## Bước 4 — Draft email/chat tiếng Nhật

Soạn theo template phù hợp với kênh và loại yêu cầu. Xem phần **Templates** và **Điều chỉnh theo loại yêu cầu** bên dưới.

**Quy tắc chọn điểm hỏi khi soạn:**
- Ưu tiên **điểm 🔴 BLOCK trước** — những điểm này bắt buộc có trong lần gửi này
- Giới hạn **tối đa 3–5 điểm** mỗi lần gửi — nếu nhiều hơn thì defer phần không block sang lần sau hoặc mail riêng
- Điểm defer → ghi vào Downstream note để không bị quên

---

## Bước 5 — Create Review Viewpoint

Sau khi có draft, thực hiện Review Viewpoint với **9 tiêu chí**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【REVIEW VIEWPOINT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅/❌  Clarification objective rõ chưa?
       → [Nhận xét ngắn]

✅/❌  Câu hỏi đã grouped hợp lý chưa?
       → [Nhận xét: có bị trộn lẫn topic không, số lượng hợp lý chưa]

✅/❌  Lý do hỏi có được nêu không (nếu cần)?
       → [Với câu hỏi phức tạp hoặc có thể gây bất ngờ cho KH — có giải thích tại sao hỏi không]

✅/❌  Ý đồ hỏi / downstream impact có rõ không (nếu cần)?
       → [KH có biết câu trả lời của họ sẽ ảnh hưởng đến tài liệu / task nào không]

✅/❌  Thời hạn reply có được nêu không (nếu cần gấp)?
       → [Nếu có deadline → có ghi rõ ngày và lý do chưa]

✅/❌  Expected answer type có rõ không?
       → [Mỗi câu hỏi có dẫn đến câu trả lời cụ thể và có thể dùng được không]

✅/❌  Open points: hỏi đủ chưa, có hỏi thừa không?
       → [Nhận xét: câu nào thừa, điểm nào còn bỏ sót]

✅/❌  Audience/tone phù hợp chưa?
       → [Keigo đúng mức, câu văn tự nhiên, email vs chat đúng độ dài]

✅/❌  Follow-up handling rõ chưa?
       → [Sau khi khách reply, BrSE sẽ làm gì tiếp theo — có nêu trong mail không]

📊 Review Viewpoint Status: [ PASS / NEEDS REVISION ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Bước 6 — Self Review & chỉnh sửa

Nếu Review Viewpoint có tiêu chí `❌`, tự động chỉnh sửa draft trước khi output. Giải thích ngắn gọn điểm đã sửa.

---

## Bước 7 — Finalize output

Output bản draft cuối cùng bằng tiếng Nhật. Draft sẽ chứa placeholder `[お客様名]`, `[会社名]` ở những chỗ cần tên thật.

> 🔴 **[Bắt buộc theo VJP-ISMS-AI-FO001 Điều 3 & TR002 Step ⑤]**
> Trước khi gửi cho khách, BrSE thực hiện **3 việc theo thứ tự**:
>
> **① Review nội dung** — đọc lại toàn bộ draft:
>    - Keigo đúng mức, ngày tháng, hướng xử lý chính xác chưa
>    - AI có thêm thông tin không có trong input không (hallucination)
>
> **② Điền placeholder** — thay thế bằng tên thật **ngoài AI** (copy ra email client / chat tool rồi điền):
>    - `[お客様名]` → tên thật người nhận (ví dụ: 田中様)
>    - `[会社名]` → tên công ty thật (ví dụ: 株式会社XYZ)
>    - Các placeholder khác nếu có
>
> **③ Gửi** — sau khi đã review và điền đầy đủ.
>
> **AI không thay thế trách nhiệm review của BrSE. Con người chịu trách nhiệm cuối cùng về nội dung gửi đi.**

---

## Bước 8 — Track reply & downstream note

Sau khi output draft, ghi một dòng gợi ý về bước tiếp theo:

```
📌 Downstream note:
   Sau khi nhận reply từ khách → [hành động cụ thể: ví dụ "cập nhật ticket Backlog",
   "xác nhận spec với dev team", "tạo estimate nếu khách approve hướng xử lý"]
   Nếu khách không reply trong [X ngày] → cân nhắc follow-up lần 2.

📋 Ghi nhận sử dụng AI (VJP-ISMS-AI-FO001 Điều 3.3 & TR002 Step ⑥):
   Mail/chat này được soạn với hỗ trợ AI. Theo quy định VTI:
   · Lưu kết quả vào hệ thống nội bộ nếu là tài liệu chính thức
   · Nếu mail này được forward hoặc trích dẫn trong tài liệu chính thức
     gửi ra ngoài → ghi chú "có sử dụng hỗ trợ AI" theo quy định
   · Trường hợp giao tiếp thông thường (confirm/clarify hàng ngày):
     tham khảo AI Promotion Lead về mức độ cần ghi nhận
```

---

## Các loại yêu cầu

### `spec` — Yêu cầu thay đổi spec / tính năng
Mục tiêu: Confirm đã hiểu đúng yêu cầu thay đổi, hỏi rõ các điểm chưa đủ để implement.

### `bug` — Báo cáo lỗi / bug
Mục tiêu: Confirm đã nhận được báo cáo lỗi, thông báo đang điều tra / hướng xử lý.

### `deadline` — Cập nhật tiến độ / deadline
Mục tiêu: Báo cáo tiến độ rõ ràng, xác nhận mốc thời gian cam kết.

### `question` — Hỏi thêm thông tin / đặt câu hỏi ngược
Mục tiêu: Confirm đã nhận yêu cầu, đặt câu hỏi cụ thể và grouped để làm rõ trước khi thực hiện.

---

## Template EMAIL

> 📝 AI sẽ dùng `[お客様名]` và `[会社名]` làm placeholder. BrSE tự điền tên thật khi copy draft ra ngoài để gửi.

```
件名: 【ご確認】[tên hệ thống] [chủ đề ngắn gọn]

[会社名] [お客様名]様

お世話になっております。
[Tên BrSE/Comtor] でございます。

ご連絡いただきありがとうございます。
[tình huống dẫn nhập — 1 câu]

---
▼ ご依頼内容の確認

[Tóm tắt nội dung đã hiểu — bullet nếu có nhiều điểm]

---
▼ 弊社の対応について

[Hướng xử lý / giải pháp — cụ thể, rõ ràng]

---
[Nếu có open points:]
▼ 確認事項

実装を進めるにあたり、以下の点をご確認いただけますでしょうか。

①[Câu hỏi 1]
　※[Lý do hỏi nếu cần — ví dụ: 「仕様書AとBで記載が異なるため」/ 「A機能に影響するため」]
　→[Ý đồ hỏi nếu hữu ích — ví dụ: 「ご回答いただき次第、設計書を更新いたします」]

②[Câu hỏi 2]
　※[Lý do hỏi nếu cần]

[Nếu có deadline reply:]
お手数ですが、[〇月〇日（〇）まで / なるべくお早めに] にご回答いただけますと幸いです。
[Lý do deadline nếu cần — ví dụ: 「〇〇のリリース日程に影響するため」]

ご回答いただき次第、[bước tiếp theo sẽ làm gì].

---
ご不明な点がございましたら、お気軽にご連絡ください。
引き続きどうぞよろしくお願いいたします。

[Tên BrSE/Comtor]
```

## Template CHAT

> 📝 Chat thường không cần xưng tên người nhận. Nếu có, dùng `[お客様名]様` làm placeholder.

```
お世話になっております。[tên hệ thống/context]についてご連絡いたします。

【ご依頼内容の確認】
[Tóm tắt ngắn gọn — 1-2 câu hoặc bullet]

【対応について】
[Hướng xử lý ngắn gọn]

[Nếu có open points:]
【確認事項】
以下の点をご確認いただけますでしょうか。

・[Câu hỏi 1]（※[Lý do ngắn gọn nếu cần — ví dụ: 「AとBで仕様が異なるため」]）
・[Câu hỏi 2 nếu có]

[Nếu có deadline reply:]
お手数ですが、[〇日まで / なるべくお早めに] にご回答いただけますと助かります。（[lý do nếu cần]）

ご回答後、[bước tiếp theo].
よろしくお願いいたします。
```

---

## Điều chỉnh theo loại yêu cầu

### Với `bug`:
- Mở đầu: 「不具合のご報告、承りました。」
- Thêm: 「現在、原因を調査しております。」
- Nếu biết hướng fix: 「～の方向で修正対応いたします。」
- Nếu chưa biết: 「詳細が判明次第、改めてご連絡いたします。」
- Downstream note: Cập nhật ticket sau khi có kết quả điều tra.

### Với `spec`:
- Mở đầu: 「ご要望の内容について確認いたします。」
- Xác nhận từng điểm thay đổi rõ ràng, phân nhóm nếu nhiều điểm.
- Nếu cần thêm thông tin: 「実装前にいくつか確認させてください。」
- Downstream note: Sau khi khách confirm → lên estimate và cập nhật backlog.

### Với `deadline`:
- Mở đầu: 「進捗についてご報告いたします。」
- Nêu rõ % hoàn thành, phần đã xong, phần còn lại.
- Dùng: 「〇月〇日を目途に」hoặc「〇月〇日までに対応予定です。」
- Downstream note: Set reminder nội bộ để follow up trước ngày cam kết.

### Với `question`:
- Mở đầu: 「ご依頼内容を確認いたしました。」
- Câu hỏi đánh số ①②③, nhóm theo topic rõ ràng.
- Ưu tiên 🔴 BLOCK questions trước — tối đa 3–5 câu hỏi mỗi lần gửi, defer phần còn lại.
- Downstream note: Sau khi nhận reply → tổng hợp và sync với team trước khi bắt đầu làm.

---

## Keigo Reference — Mức độ lịch sự vừa phải

| Tình huống | Nên dùng | Tránh |
|-----------|----------|-------|
| Cảm ơn | ありがとうございます | ありがとう |
| Xin lỗi vì trễ | ご返信が遅くなり、申し訳ございません | すみません |
| Nhờ xác nhận | ご確認いただけますでしょうか | 確認してください |
| Thông báo sẽ làm | 対応いたします | やります |
| Hỏi ý kiến | いかがでしょうか | どうですか |
| Kết thúc mail | よろしくお願いいたします | よろしく |
| Sẽ liên hệ lại | 改めてご連絡いたします | また連絡します |
| Nhận yêu cầu | 承りました | わかりました |
| Thông báo điều tra | 調査を進めております | 調べます |

---

## Ví dụ thực tế (AIP-aligned)

### Ví dụ 1 — Email, loại `bug`

**Input:** Khách báo lỗi: khi user click nút "Export CSV" trên màn hình báo cáo thì bị lỗi trắng màn hình. Lỗi xảy ra trên Chrome, chưa rõ nguyên nhân, team đang điều tra. Dự kiến trả lời sau 1 ngày.

**Bước 2 — Input Understandings:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【INPUT UNDERSTANDINGS — Vui lòng xác nhận】

📋 1. Understanding Summary
   Khách báo lỗi màn hình trắng khi click "Export CSV" trên màn hình báo cáo,
   môi trường Chrome. Team đang điều tra và sẽ phản hồi trong 1 ngày.

❓ 2. Grouped Open Points
   Không có — thông tin đã đủ để viết confirm.

🎯 3. Expected Answer Types
   Không áp dụng (đây là mail thông báo, không cần câu trả lời từ khách).

⚠️  4. Downstream Impact
   Nếu điều tra quá 1 ngày → cần gửi mail update tiến độ lần 2.

💡 5. Assumptions Being Used
   Giả sử lỗi xảy ra trên tất cả user, không chỉ 1 account cụ thể.

📊 Input Understanding Status: [ PENDING BrSE CONFIRMATION ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Bước 4 — Draft (AI output — có placeholder, chưa có tên thật):**
```
件名: 【ご報告】レポート画面 CSVエクスポートエラーについて

[会社名] [お客様名]様

お世話になっております。〇〇でございます。
このたびは不具合のご報告をいただき、ありがとうございます。

▼ 不具合内容の確認
・対象画面：レポート画面
・発生操作：「CSVエクスポート」ボタンクリック時
・現象：画面が白くなる（ブラウザ：Chrome）

▼ 弊社の対応について
現在、原因の調査を進めております。
1営業日以内を目途に調査結果をご報告いたします。

ご不便をおかけし、大変申し訳ございません。
引き続きどうぞよろしくお願いいたします。

〇〇
```

**Bước 7 — BrSE điền tay trước khi gửi (ngoài AI):**
```
// Copy draft ra Gmail / Google Chat, sau đó thay thế:
[会社名]   → 株式会社XYZ  (tên thật công ty khách)
[お客様名] → 田中          (tên thật người nhận)
```

**Bước 5 — Review Viewpoint:**
```
✅ Clarification objective rõ → thông báo đã nhận + đang xử lý
✅ Không có open points cần grouped
✅ Không cần expected answer type (mail thông báo)
✅ Không hỏi thừa/thiếu
✅ Keigo vừa phải, email đủ thành phần
✅ Follow-up: hẹn phản hồi trong 1 ngày → rõ ràng

📊 Review Viewpoint Status: [ PASS ]
```

**Bước 8 — Downstream note:**
```
📌 Sau khi nhận reply từ khách → cập nhật ticket bug trên Backlog.
   Nếu chưa có kết quả điều tra sau 1 ngày → gửi mail update tiến độ lần 2.
```

---

### Ví dụ 2 — Chat, loại `question`

**Input:** Khách yêu cầu thêm chức năng filter theo ngày trên màn hình lịch sử đơn hàng. Chưa rõ: filter theo ngày tạo hay ngày cập nhật? Range tối đa là bao nhiêu ngày?

**Bước 2 — Input Understandings (tóm tắt):**
```
📋 Understanding Summary: Thêm date filter vào màn hình lịch sử đơn hàng.
❓ Grouped Open Points:
   [Nhóm A — Nghiệp vụ] · Loại ngày filter (tạo / cập nhật) · Range tối đa
🎯 Expected Answer Types:
   · Loại ngày → chọn 1 trong 2 (hoặc cả hai)
   · Range → số ngày cụ thể hoặc "không giới hạn"
⚠️  Downstream: Chưa rõ 2 điểm này → không thể viết spec / estimate
💡 Assumptions: Chưa có giả định — cần xác nhận từ khách trước
📊 Input Understanding Status: [ PENDING BrSE CONFIRMATION ]
```

**Bước 4 — Draft chat (AI output — chat thường không cần tên người nhận):**
```
お世話になっております。注文履歴画面の日付フィルター機能についてご連絡いたします。

【ご依頼内容の確認】
注文履歴画面に日付フィルター機能を追加するご要望として承りました。

【確認事項】
実装前に以下の点をご確認いただけますでしょうか。

①フィルターの対象日付は「作成日」「更新日」のどちらでしょうか（両方も可能です）。
②選択可能な日付の最大範囲はございますでしょうか（例：30日・90日・制限なし）。

ご回答いただき次第、実装の検討を進めてまいります。
よろしくお願いいたします。
```

> ✅ Chat thường không cần tên người nhận → không có placeholder cần điền. Copy và gửi thẳng sau khi review.

**Bước 8 — Downstream note:**
```
📌 Sau khi nhận reply → tổng hợp answer, cập nhật spec doc, sync với dev để estimate.
```

---

## Lưu ý vận hành

- Không bỏ qua Bước 2 dù input có vẻ rõ — luôn hiển thị 5 thành phần để BrSE xác nhận
- Luôn hiển thị **Kênh gửi** và **Loại output** ở đầu Input Understandings để BrSE xác nhận
- Nếu input thiếu thông tin → hỏi tất cả trong **1 tin nhắn**, không hỏi lần lượt từng tin
- Luôn đánh dấu 🔴 BLOCK cho điểm nào đang chặn dev — hỏi những điểm này trước
- Giới hạn **3–5 điểm** mỗi lần gửi — điểm không block thì defer, ghi vào Downstream note
- Nội dung formal/contractual → dùng Email, không dùng Chat
- Thuật ngữ kỹ thuật (API, DB, UI, spec, backlog…) giữ nguyên tiếng Anh — thông lệ môi trường IT Nhật
- Nếu BrSE chỉnh sửa ở Bước 3 → cập nhật lại Input Understandings trước khi draft
- Review Viewpoint Status `NEEDS REVISION` → bắt buộc chỉnh draft trước khi output bản cuối

## Tuân thủ VTI ISMS (tóm tắt)

| Quy định | Nội dung | Bước áp dụng |
|----------|----------|-------------|
| FO001 Đ.2.1 | Không nhập PII, NDA, API key, thông tin tài chính | ⚠️ Trước Bước 1 |
| FO001 Đ.2.2 | Ẩn danh hóa thông tin cá nhân trước khi nhập | ⚠️ Trước Bước 1 |
| FO001 Đ.3.1 | Human review bắt buộc trước khi dùng output AI | Bước 7 |
| FO001 Đ.3.2 | Con người chịu trách nhiệm cuối cùng, không phải AI | Bước 7 |
| FO001 Đ.3.3 | Ghi nhận sử dụng AI khi chia sẻ ra ngoài chính thức | Bước 8 |
| TR002 Step⑥ | Lưu thành quả vào hệ thống nội bộ khi cần | Bước 8 |
| G001 Ch.5.2 | Không đưa thông tin mật vào System Prompt / Projects | Luôn luôn |

> Mọi sự cố (vô tình nhập thông tin mật, phát hiện bất thường) → báo cáo ngay AI Promotion Lead hoặc vjp.isms@vti.com.vn
