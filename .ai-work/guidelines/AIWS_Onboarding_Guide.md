# Hướng dẫn cài và dùng AI Work System (AIWS)

> Tài liệu này dùng để onboard thành viên mới vào AI Work System (AIWS).
> Người hướng dẫn: điền tên và liên hệ ở cuối file trước khi gửi.

AIWS được cài bằng cách **nhờ chính Claude làm hộ** — bạn không phải copy file thủ công.
Có **2 cách chạy Claude**, chọn 1 cách hợp với bạn rồi làm theo. Sau khi cài xong,
xem phần "Dùng hằng ngày" bên dưới.

**3 điều cần nắm trước khi bắt đầu:**
- 📁 **Folder PACKAGE (ZIP)** = kho chứa AIWS. Giải nén để đó, **không cài vào đây**.
- 📁 **Folder PROJECT** = dự án của bạn — nơi mở Claude và cài AIWS vào.
- → Hai folder này **KHÁC NHAU**. Nhớ kỹ đường dẫn của cả hai là được.

**2 cách cài — chọn 1:**

| | CASE A — Claude Code | CASE B — VS Code |
|---|---|---|
| Bạn dùng | Terminal hoặc app Claude Code | Editor VS Code (có sẵn extension) |
| Hợp với ai | Người quen dùng terminal / không dùng VS Code | Người đã code/đọc tài liệu trong VS Code |
| Cài Claude bằng | Tải app tại claude.ai/download | Cài extension "Claude Code" trong VS Code |

> Cả 2 case sau khi mở được Claude thì làm **chung** phần "Bước chung" — cách cài AIWS giống hệt nhau.

---

## PHẦN 1 — CÀI ĐẶT (làm 1 lần)

### Bước 0 — Tải & giải nén package AIWS (chung cho cả 2 case)

Tải package tại: _(người hướng dẫn điền link Drive hoặc đính kèm file zip)_

Giải nén ra thư mục bất kỳ, ví dụ: `C:\tools\aiws\`. Bên trong sẽ có 1 folder tên kiểu
`AI_Work_System_MVP_v1.0_2026-06-03`.

➡️ **Ghi nhớ đường dẫn đầy đủ tới folder đó** (ví dụ `C:\tools\aiws\AI_Work_System_MVP_v1.0_2026-06-03`).
Không cần mở gì bên trong — lát nữa bạn chỉ đưa đường dẫn này cho Claude.

---

## CASE A — Cài qua Claude Code (terminal / app)

### A1 — Cài Claude Code (bỏ qua nếu đã có)

Tải và cài tại: https://claude.ai/download

Kiểm tra: mở terminal, gõ `claude --version` → thấy số version là OK ✅

### A2 — Mở Claude tại PROJECT của bạn

Mở terminal, trỏ vào folder project rồi gõ:

```
cd C:\đường-dẫn\đến\project-của-bạn
claude
```

Hoặc: mở app Claude Code → **Open Folder** → chọn folder project.

➡️ Tiếp tục xuống **"Bước chung (cho cả 2 case)"** bên dưới.

---

## CASE B — Cài qua VS Code (extension)

### B1 — Cài extension Claude Code

1. Mở VS Code
2. Nhấn `Ctrl+Shift+X` → mở tab **Extensions**
3. Gõ **`Claude Code`** vào ô tìm kiếm → nhấn **Install**

Tham khảo: https://docs.anthropic.com/claude-code/vscode

### B2 — Mở project & đăng nhập

1. Sau khi cài, sidebar trái xuất hiện **icon Claude Code** → nhấn vào → **Sign in**
2. **File → Open Folder** → chọn đúng folder PROJECT của bạn
3. Khung chat Claude hiện ở bên cạnh editor — bạn sẽ nhắn Claude ở đây

➡️ Tiếp tục xuống **"Bước chung (cho cả 2 case)"** bên dưới.

---

## Bước chung (cho cả 2 case) — nhắn Claude cài → kiểm tra → chạy thử

> Đến đây bạn đã mở được Claude **đang trỏ vào folder PROJECT**. Phần này giống nhau cho cả CASE A và CASE B.

### Bước 1 — Nhắn Claude cài AIWS vào project

Paste đoạn sau vào chat. Thay dòng 2 bằng **đường dẫn folder bạn đã giải nén ở Bước 0**:

```
Hãy cài AI Work System MVP vào dự án này.
Package nằm tại: C:\tools\aiws\AI_Work_System_MVP_v1.0_2026-06-03
Đọc install_guide.md trong folder đó và làm theo từng bước.
```

Claude tự copy files vào project. Nó sẽ hỏi **tên project** — điền tên ngắn,
còn lại nhấn Enter giữ mặc định. Đợi Claude báo ✅ là xong.

### Bước 2 — Kiểm tra cài đúng chưa

Gõ `/aiws-aip create` vào chat:
- ✅ Claude hỏi loại task → cài đúng, dùng được rồi
- ❌ Báo "unknown command" → đang mở sai folder (chưa trỏ vào PROJECT), xem lại A2 / B2

### Bước 3 — Chạy thử 1 task thật để xác nhận hoạt động

Đây là bước quan trọng — đừng bỏ qua. Cài xong mà không chạy thử = không biết có lỗi không.

Paste đoạn sau vào chat Claude (đang mở project của mình):

```
Hãy tạo AIP để tôi tóm tắt và ghi lại các điểm chính
từ cuộc họp hôm nay (hoặc task nhỏ nhất tôi đang làm).
```

Kết quả đúng khi:
- ✅ Claude hỏi thêm về task rồi tạo file AIP trong `.ai-work/aip/`
- ✅ Claude tạo workspace và bắt đầu làm từng bước
- ❌ Báo "không biết làm thế nào" hoặc không tạo file → liên hệ người hướng dẫn

---

## PHẦN 2 — DÙNG HẰNG NGÀY

Mỗi task làm việc với AI theo 3 bước chính (+ 1 bước lưu wiki khi cần):

### 1. Tạo AIP (kế hoạch làm việc)
```
/aiws-aip create
```
Hoặc nói tự nhiên: _"Hãy tạo AIP để tôi review basic design chức năng F04"_

Claude tự tìm template phù hợp và tạo file AIP.

Nếu chưa rõ AIP dùng đúng không → xem file AIP Claude vừa tạo rồi bảo Claude chỉnh lại.

### 2. Bắt đầu chạy task
```
/aiws-aip run start
```
Hoặc nói tự nhiên: _"Hãy chạy AIP [AIP-ID]"_

Claude tạo workspace và làm việc từng bước.
> Mọi findings, draft, output ghi vào workspace — không ghi vào AIP
> ASC chỉ là bối cảnh của step hiện tại; Working AIP vẫn là authority. Runtime Queue (`02_runtime_queue.jsonl`) xử lý việc chặn step, còn Capture Inbox ghi candidate để triage sau — không tự promote Wiki/canonical.

> **Task Desk (for Agent) là Beta:** hãy trial trong project trước khi dùng production.

### 3. Kiểm tra trước khi finalize

Bảo Claude chạy giúp: _"Chạy lint kiểm tra AIP và workspace cho mình"_
Hoặc gõ lệnh: `/aiws-lint`

Claude báo lỗi nếu có → sửa → xong.

### 4. Lưu tài liệu vào wiki (khi cần)

Sau khi task xong, nếu output đáng lưu lại để tái sử dụng (design doc, RD, checklist, SOP...):

Bảo Claude: _"Dùng AIWS, thêm tài liệu này vào wiki giúp mình"_

→ Tìm lại sau: _"Tìm trong wiki AIWS tài liệu liên quan đến [chức năng/keyword]"_

> Chi tiết về wiki xem **PHẦN 3** bên dưới.

**Lưu ý:**
- AIP = bản kế hoạch cố định, không thay đổi trong lúc làm
- Workspace = nơi làm việc thực tế, ghi mọi thứ vào đây
- Gõ lệnh chuẩn hơn, nói tự nhiên cũng được

---

## PHẦN 3 — WIKI (KNOWLEDGE HUB) LÀ GÌ & 5 LỆNH CẦN BIẾT

### Hình dung Wiki như một thư viện

Dự án có hàng trăm tài liệu (requirement, Q&A, design, checklist, code…). Tìm thủ công
trong Outlook/Slack/SharePoint rất mất thời gian. **Wiki (Knowledge Hub)** giải quyết bằng
cách viết cho mỗi tài liệu **một "tờ giới thiệu" ngắn** (gọi là *meta*): nó tóm tắt nội dung,
từ khoá để tìm, và mục "Xem thêm" trỏ sang tài liệu liên quan.

Nhờ vậy AI **không phải đọc cả file 50 trang** — nó tra tờ giới thiệu trước, chỉ mở tài liệu
gốc khi thật sự cần. Kết quả: **nhanh hơn, đúng hơn, có dấu vết truy nguyên (traceability)**.

### 5 lệnh skill — chỉ cần nhớ 5 lệnh này

AIWS dùng **router pattern**: bạn chỉ nói chuyện tự nhiên, AI tự chọn đúng việc cần làm.

| Lệnh | Khi nào dùng | Ví dụ câu nói |
|---|---|---|
| `/aiws-wiki register` | Thêm tài liệu mới vào wiki (1 file / cả folder) | _"Add file này vào wiki", "đăng ký cả folder design vào wiki"_ |
| `/aiws-wiki refresh` | Tài liệu gốc thay đổi → cập nhật wiki | _"Source đã đổi, cập nhật wiki meta"_ |
| `/aiws-wiki lookup` | Tìm trong wiki | _"Tìm tài liệu về màn đặt phòng F04"_ |
| `/aiws-wiki test-lookup` | Kiểm tra wiki có tìm ra tài liệu không | _"Test lookup cho các source vừa thêm"_ |

### Khi nào nên đưa tài liệu vào wiki?

Quy tắc đơn giản: **tài liệu nào bạn (hoặc AI) cần tra lại ≥ 1 lần khi làm task → nên đưa vào wiki.**

✅ Nên đưa: requirement/Q&A đã chốt, design (BD/DD), process, guideline, checklist.
❌ Chưa/không nên: bản nháp đang đổi hằng ngày, note cá nhân, email rời rạc, code sinh tự động.

> Nguyên tắc vàng: **chưa chốt thì để notebook, đừng vội đưa vào wiki.** Khi nghi ngờ thì hỏi Claude.

> 📚 **Đào sâu về Wiki** (đọc khi bạn bắt đầu xây Knowledge Hub cho dự án):
> - [WIKI_INTRO_FOR_EVERYONE](./WIKI_INTRO_FOR_EVERYONE.md) — giới thiệu Wiki cho **mọi vai trò** (PM/BA/BrSE/dev/QA), gồm cách AI tìm trong wiki và cách **review** wiki.
> - [MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS](./MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS.md) — quy trình **build wiki chi tiết** theo từng loại tài liệu (requirement, design, process, checklist…).

---

## PHẦN 4 — THÓI QUEN DÙNG AI HIỆU QUẢ

Hai quy tắc này dùng được với mọi AI tool, không chỉ AIWS:

### Convert tài liệu sang Markdown trước khi cho AI đọc

Trước khi đưa tài liệu cho AI xử lý (Word, Excel, PDF...):
- Bảo Claude: _"Hãy chuyển nội dung dưới đây sang Markdown"_ → paste nội dung vào
- Hoặc dùng tool convert online → copy kết quả Markdown vào chat

AI đọc Markdown chính xác hơn nhiều so với bảng Excel hay format Word gốc.

### Review và finalize trong Claude — rồi mới export sang Excel/Word

Khi output cần là file Excel hoặc Word:
1. Làm và review hoàn toàn trong Claude trước (ở dạng Markdown/text)
2. Sau khi OK → bảo Claude: _"Tạo bảng Excel từ nội dung này"_ hoặc tự copy ra

Đừng export sớm rồi chỉnh trong Excel/Word — mất context, khó cho AI đọc lại để chỉnh tiếp.

---

## PHẦN 5 — TỰ TÌM HIỂU (hỏi Claude)

Không hiểu gì thì cứ hỏi Claude, nó trả lời được hết.

> **Tip:** Luôn thêm từ khoá **AIWS / AIP / SOP / Wiki** vào câu hỏi để Claude
> biết bạn đang hỏi về AI Work System (không nhầm với skill khác).

**Hỏi về hệ thống:**
- _"AIWS là gì?"_
- _"AIP trong AIWS là gì? Dùng khi nào?"_
- _"Các skill của AIWS đang có là gì?"_

**Hỏi về task của mình:**
- _"Tôi muốn dùng AIWS để tạo test case, tôi phải làm thế nào?"_
- _"Tôi muốn dùng AIWS để review basic design, bắt đầu thế nào?"_
- _"AIWS có AIP template nào phù hợp với task clarify requirement không?"_

**Hỏi về wiki:**
- _"Dùng AIWS, làm thế nào để thêm tài liệu vào wiki?"_
- _"Tìm trong wiki AIWS tài liệu liên quan đến chức năng đặt phòng"_

---

_Gặp vấn đề gì liên hệ: [tên người hướng dẫn] — AI推進委員会_
