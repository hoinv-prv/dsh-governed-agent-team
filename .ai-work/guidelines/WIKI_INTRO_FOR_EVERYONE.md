# Giới thiệu Wiki (Knowledge Hub) — Dành cho mọi member dự án

> **Audience:** Mọi người trong dự án — PM, BA, BrSE, dev, QA, designer, customer-side. **Không cần biết code** vẫn đọc được.
>
> **Mục đích:**
> - Hiểu Wiki là gì và tại sao team cần nó *trước khi* bắt đầu dùng.
> - Hiểu cách AI thực sự tìm kiếm trong Wiki khi làm task — để bạn biết Wiki tốt sẽ giúp AI thế nào, Wiki xấu sẽ làm AI ra kết quả sai ra sao.
> - Biết các **lệnh skill** member sẽ dùng (5 lệnh đủ để làm mọi việc).
> - Biết cách build Wiki sao cho phù hợp với dự án.
> - **Quan trọng:** Biết cách review Wiki (thường do AI build) để xác nhận đã đúng chưa.
>
> **Tài liệu kèm:** Khi cần đi sâu vào quy trình build chi tiết → đọc thêm [MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS](./MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS.md).

---

## 1. Wiki là gì? Hãy tưởng tượng như một thư viện

Hãy hình dung dự án của bạn có **hàng trăm tài liệu**: requirement, Q&A khách hàng, design doc, process, checklist, source code… Mỗi lần cần tìm "Q&A nào đã chốt cho màn đặt phòng?" — bạn phải mở Outlook, Slack, SharePoint, Confluence, đọc 5–10 file. Mất 20–30 phút chỉ để tìm.

Bây giờ tưởng tượng có **một thư viện**:

```
┌──────────────────────────────────────────────────┐
│                  THƯ VIỆN                         │
│                                                   │
│  📚 Kệ sách      = các tài liệu gốc của dự án     │
│      (PDF, Word, MD, code, design...)             │
│                                                   │
│  📝 Tờ giới thiệu = "meta" — mỗi cuốn có 1 trang  │
│      tóm tắt: nội dung gì, ai cần, từ khoá nào,   │
│      và mục "Xem thêm" trỏ sang tờ liên quan      │
│                                                   │
│  🔗 Mục "Xem thêm" = "Related Sources" — ngay     │
│      trong tờ giới thiệu, liệt kê các tờ liên     │
│      quan kèm vai trò (vd "test case của màn này")│
│                                                   │
│  🗃️ Thẻ mục lục   = "index" — danh sách dùng để   │
│      tra cứu nhanh, sinh tự động                  │
│                                                   │
│  👤 Thủ thư       = công cụ search (lookup tool)   │
│      Nhận câu hỏi → tìm trong thẻ mục lục →       │
│      đưa bạn tờ giới thiệu phù hợp                │
└──────────────────────────────────────────────────┘
```

Đó chính là **Wiki / Knowledge Hub trong AIWS**.

| Trong thư viện | Trong Wiki của ta |
|---|---|
| 📚 Cuốn sách thật | **Artifact** — file gốc (Req Def, DD, Q&A, code…) |
| 📝 Tờ giới thiệu | **Wiki Source Meta (Layer 1)** — 1 file Markdown ngắn mô tả 1 artifact. Đây là **đơn vị tri thức** của Wiki |
| 🔗 Mục "Xem thêm" | **`## Related Sources`** — section ngay trong meta, trỏ sang các source liên quan kèm **vai trò** (role) |
| 🗃️ Thẻ mục lục | **Index** — file `index.jsonl` được sinh tự động từ các meta (KHÔNG sửa tay) |
| 👤 Thủ thư | **Lookup tool** — `lookup_wiki_source.py`, AI gọi để tìm |
| 📋 Quy tắc xếp sách | **Source Interpretation Profile** (cho mỗi loại tài liệu) |
| 📐 Khuôn dùng lại | **Project Mapping Pattern (PMP)** — khuôn cho batch cùng format |

### Tại sao không chỉ "search Google trong SharePoint"?

Bởi vì:
- Tìm trong tài liệu gốc rất chậm (đọc cả file 50 trang).
- Tài liệu gốc thay đổi liên tục, tên file lộn xộn.
- AI nếu đọc thẳng tài liệu gốc dễ "đoán mò" nội dung không có trong source (hallucination).
- Không có cách nào biết "tài liệu này đã chốt chưa", "thay tài liệu này thì những tài liệu khác có ảnh hưởng không".

Wiki giải quyết bằng cách: **viết 1 tờ giới thiệu chuẩn cho mỗi cuốn sách**, và trong mỗi tờ có **mục "Xem thêm" trỏ sang các tờ liên quan**. Thủ thư (AI) tra mục lục → tờ giới thiệu → đi tiếp theo "Xem thêm" sang tờ liên quan → chỉ mở sách gốc khi thật sự cần.

---

## 2. Wiki được tổ chức như thế nào? — mô hình 2 lớp + index

Knowledge Hub gồm **2 lớp**: artifact-level meta (Layer 1) là đơn vị tri thức, và index là projection để tra cứu nhanh. Quan hệ giữa các artifact được ghi thẳng trong meta bằng section **`## Related Sources`**.

### 2.1. Hai lớp output

```
   Câu hỏi của bạn / task của AI
              │
              ▼
   ┌─────────────────────────┐
   │   🗃️  Index (runtime)    │  ← thẻ mục lục, sinh tự động từ
   │   index.jsonl             │     các meta (KHÔNG sửa tay)
   └────────────┬─────────────┘
                │  thủ thư tra → ra source_id
                ▼
   ┌─────────────────────────┐
   │   📝  Layer 1:            │  ← Wiki Source Meta — tờ giới thiệu
   │   ARTIFACT META           │     1 file = 1 artifact.
   │   - Summary               │     ĐÂY LÀ ĐƠN VỊ TRI THỨC.
   │   - Lookup Keys (T1/T2/T3)│     - artifact_locator → file gốc
   │   - Hints / Cautions      │     - ## Related Sources → source
   │   - ## Related Sources    │       liên quan (có role)
   └────────────┬─────────────┘
                │  AI đọc trước; đi tiếp theo Related Sources
                ▼
   ┌─────────────────────────┐
   │   📚  Artifact gốc:       │  ← tài liệu gốc của dự án
   │   (Layer 0 — file thật)   │     Req Def, DD, code, Q&A
   └─────────────────────────┘

   ─── Quan hệ cross-artifact = ## Related Sources ─────
   Nằm TRONG mỗi meta (không phải lớp riêng):
   - mỗi entry trỏ tới 1 source_id liên quan + role có hướng
     (upstream_input, companion_design, downstream_target…)
   - KHÔNG project vào index.jsonl
   - related_artifact_refs (frontmatter) = traceability phẳng,
     KHÔNG dùng để điều hướng

   ─── Supplemental status (cho Q&A/findings) ──────────
   status, reflection_status, reflected_to, superseded_by
```

**Quan trọng:** AI **không đọc thẳng** kệ sách. Luôn đi qua thủ thư (index) → tờ giới thiệu (Layer 1 meta) → đi tiếp sang source liên quan theo `## Related Sources` → và chỉ khi không đủ mới mở sách thật (artifact gốc).

### 2.2. Một "tờ giới thiệu" (meta — Layer 1) có gì?

```markdown
---
source_id: SRC-DD-F04-BOOKING-SEARCH-FE
title: Detail Design — Màn Tìm kiếm Đặt phòng (F04) — FE layer
artifact_type: detailed_design_fe
source_type: design_doc
knowledge_class: source_of_truth
artifact_locator: docs/design/F04_BookingSearch_DD_v2_FE.md
profile_id: design_doc
status: active
updated_at: 2026-05-26
related_artifact_refs: [SRC-BD-F04-BOOKING-SEARCH, SRC-ITTC-F04]  # ← traceability phẳng
---

## Summary
Thiết kế chi tiết FE màn tìm kiếm đặt phòng F04: filter, sort, paging,
xử lý khi không có kết quả.

## Lookup Keys
- F04 [T1]                          ← Tier 1: ID duy nhất
- func_F04_BOOKING_SEARCH [T1]      ← Tier 1: canonical name
- booking search [T2]               ← Tier 2: domain term
- tìm kiếm đặt phòng [T2]            ← Tier 2: tiếng Việt
- BookingSearchService [T2]          ← Tier 2: technical name
- /api/v1/bookings/search [T2]
- detailed_design_fe [T3]            ← Tier 3: artifact type
- design [T3]

## Related Sources                  ← quan hệ cross-artifact (có role)
- **SRC-BD-F04-BOOKING-SEARCH** — role: upstream_input — BD định nghĩa business intent + acceptance criteria; coupling = business rules F04; đổi BD → review design.
- **SRC-DD-F04-BOOKING-SEARCH-API** — role: companion_design — cùng function, lớp API; coupling = request/response contract; đổi contract → đồng bộ FE.
- **SRC-ITTC-F04** — role: downstream_target — test case verify function; coupling = acceptance criteria; đổi DD → cập nhật test.

## Source-Specific Hints
- Section §3.2 là điểm khác biệt so với mock-up cũ (đã chốt theo Q&A-2026-04-12).

## Cautions
- Diagram sequence chỉ có ở file PDF gốc, file MD không capture được.
```

Mỗi meta có:
- `## Related Sources` — section liệt kê source liên quan kèm **role** có hướng. Đây là cơ chế điều hướng chính giữa các artifact.
- `related_artifact_refs` (frontmatter) — danh sách phẳng cho traceability; **KHÔNG** dùng để điều hướng.
- `artifact_type` được phân loại theo **Artifact Type Taxonomy** (14 loại chuẩn).
- `Lookup Keys` có gắn **Tier** T1/T2/T3 — quyết định điểm số khi search.

### 2.3. Quan hệ cross-artifact: `## Related Sources`

Khi 1 màn hình / function / table có **nhiều artifact** (vd Booking Search có BD + DD-FE + DD-API + DD-BE + Testcase), bạn muốn AI từ 1 meta đi tiếp được sang các meta liên quan. Mỗi meta tự mang section `## Related Sources`:

```markdown
## Related Sources
- **SRC-BD-F04-BOOKING-SEARCH** — role: upstream_input — BD gốc của function
- **SRC-DD-F04-BOOKING-SEARCH-API** — role: companion_design — cùng function, lớp API
- **SRC-DD-F04-BOOKING-SEARCH-BE** — role: companion_design — cùng function, lớp BE
- **SRC-ITTC-F04** — role: downstream_target — test case của function
- **SRC-TBL-BOOKING** — role: upstream_input — table được search
```

**Role enum — 3 register** (typed relations, có hướng):
- **documentary** (Artifact→Artifact): `upstream_input · downstream_navigation · downstream_target · triggered_flow · system_foundation · companion_design · companion_requirement · output_template · related`.
- **representation** (Object↔Artifact): `represents · represented_by`.
- **domain** (Object→Object): `x:`-namespaced (vd `x:calls`, `x:part_of`, `x:reads`, `x:writes`).

> Mỗi entry kèm **basis note khách quan, intent-agnostic**: dependency edge nêu hướng + coupling (schema/field/contract) + ảnh hưởng khi đổi; skippable edge ghi rõ "no data coupling". Tránh "MUST READ" / "mở khi đổi X".

**Điểm cốt yếu:**
- `## Related Sources` nằm **TRONG meta của từng artifact** — không có record tổng hợp riêng.
- Section này được tool **scaffold tự động** khi build meta (gợi sẵn các role slot dạng TODO để người/AI điền target source_id).
- **KHÔNG project vào `index.jsonl`** — chỉ đọc khi đã mở meta.
- AI đi multi-hop bằng cách: mở 1 meta → đọc `## Related Sources` → mở meta của source liên quan → đọc tiếp `## Related Sources` của nó.

### 2.4. Còn các "khuôn" thì sao?

Có **hai loại khuôn**, đừng nhầm:

- **Source Interpretation Profile** (`profiles/<id>.yml`) — quy tắc cho **loại tài liệu** (vd `design_doc.yml` cho mọi DD). Đã có sẵn nhiều profile.
- **Project Mapping Pattern — PMP** (`profiles/mapping_patterns/PMP-<id>.yml`) — quy tắc cho **một format cụ thể** trong project (vd "DD của khách Fujitsu luôn có 5 section thế này → map vào canonical slot thế kia"). Tạo sau khi sample-first xác nhận format ổn định.

---

## 3. AI tìm kiếm trong Wiki như thế nào khi làm task?

### 3.1. Flow chuẩn 4 bước

Khi AI nhận một task (ví dụ "viết testcase cho màn Booking Search"), AI **không lao thẳng vào đọc 200 trang DD**. AI làm theo thứ tự:

```
   AI nhận task
        │
        ▼
   ┌──────────────────────────────────────────────┐
   │ Bước 1: Lookup trong Wiki                     │
   │   AI gọi /aiws-wiki lookup --query "..."    │
   │   Thủ thư tra index.jsonl → trả về danh sách  │
   │   meta (Layer 1) khớp nhất, kèm score.        │
   └──────────────────────┬───────────────────────┘
                          ▼
   ┌──────────────────────────────────────────────┐
   │ Bước 2: Đọc meta (Layer 1) trước              │
   │   AI mở tờ giới thiệu (meta).                 │
   │   Đọc: Summary, Lookup Keys, Hints, Cautions, │
   │         và ## Related Sources (đi tiếp sang   │
   │         meta liên quan nếu task cần).          │
   │   Câu hỏi: "Đã đủ trả lời chưa?"              │
   └──────────────────────┬───────────────────────┘
              ┌───── đủ ──┴── không đủ ─────┐
              ▼                              ▼
   ┌─────────────────┐         ┌──────────────────────────┐
   │ Trả lời / làm    │         │ Bước 3: Mở ARTIFACT gốc   │
   │ task             │         │   AI mới mở file DD,      │
   │                  │         │   đọc đúng section cần.   │
   └─────────────────┘         └────────────┬─────────────┘
                                            ▼
                            ┌──────────────────────────────┐
                            │ Bước 4: Nếu vẫn không rõ      │
                            │   → hỏi người (HUMAN)         │
                            │   AI KHÔNG được tự đoán.      │
                            └──────────────────────────────┘
```

### 3.2. Cách thủ thư khớp từ khoá — Tier T1/T2/T3

Thủ thư không khớp đều mọi từ khoá. Mỗi keyword trong meta được gắn **Tier**, và mỗi Tier có **hệ số nhân**:

| Tier | Hệ số | Ví dụ |
|---|---|---|
| **T1** — Unique identifier | **×3.0** | `F04`, `func_F04_BOOKING_SEARCH`, `SRC-DD-F04-...` |
| **T2** — Domain-specific term | **×1.5** | "tìm kiếm đặt phòng", "booking search", `/api/v1/bookings/search`, tên table |
| **T3** — Category label | **×1.0** | "design", "detailed_design_fe", "process" |

**Rule "T1 exact match → early return":** Nếu top-1 kết quả là T1 exact match → thủ thư dừng ngay, không trả thêm. Lý do: đã chắc chắn 100%, search thêm chỉ tốn token.

**Hệ quả thực tế:**

| Nếu bạn… | Thì AI sẽ… |
|---|---|
| Gắn **T1 đúng** cho ID/canonical name | Search bằng ID → hit ngay, không nhầm |
| Gắn T2 đúng cho business term + technical term | AI tìm bằng cả "đặt phòng" và "booking search" đều ra |
| Chỉ có T3 (label chung) → không có T1/T2 | Search ra cùng hạng với 50 file khác → noise |
| Quên gắn Tier (meta cũ) | Fallback về scoring không-tier (vẫn dùng được, nhưng yếu hơn) |

**Vẫn quan trọng:** thủ thư **không hiểu ngữ nghĩa**, không có AI thông minh khớp đồng nghĩa. Bạn viết "booking" mà người tìm gõ "đặt phòng" → KHÔNG khớp. Vẫn phải ghi cả hai trong Lookup Keys.

### 3.3. Vùng tìm kiếm: Project vs Local

```
   ┌──────────────────────────────────────────────┐
   │  AI ưu tiên tìm theo thứ tự:                  │
   │                                                │
   │  1. Project Wiki  (wiki của dự án hiện tại)    │
   │     → mặc định, AI luôn tìm ở đây trước        │
   │                                                │
   │  2. Local Wiki  (wiki của các dự án khác       │
   │     trên máy bạn, ví dụ Fujitsu manual)        │
   │     → KHÔNG mặc định. Cần HUMAN confirm trước. │
   │                                                │
   │  3. Hỏi HUMAN  (khi cả hai đều không có)       │
   │     → AI không tự suy đoán.                    │
   └──────────────────────────────────────────────┘
```

---

## 4. 5 lệnh skill member cần biết

AIWS có **router pattern**: bạn chỉ cần biết 5 lệnh entry — router tự delegate sang skill nội bộ phù hợp. **KHÔNG cần** nhớ tên các skill nội bộ.

| Lệnh | Khi nào dùng | Ví dụ câu nói với AI |
|---|---|---|
| `/aiws-wiki register` | Thêm tài liệu mới vào Wiki | "Add file này vào wiki", "đăng ký tài liệu này", "thêm cả thư mục vào wiki" |
| `/aiws-wiki refresh` | Cập nhật khi tài liệu gốc thay đổi | "Source đã thay đổi", "cập nhật wiki meta", "cập nhật related sources", "format đã đổi" |
| `/aiws-wiki lookup` | Tìm trong Wiki | "Lookup booking search", "tìm tài liệu về F04" |
| `/aiws-wiki add-local-knowledge` | Đăng ký bộ knowledge ngoài project | "Add Fujitsu manual vào local wiki" |
| `/aiws-wiki test-lookup` | Kiểm tra Wiki lookup có đúng không | "Test lookup cho wiki mới build", "verify wiki tìm ra source đúng không" |

### 4.1. Router là gì?

Tưởng tượng quầy lễ tân của khách sạn: bạn chỉ cần nói "tôi muốn đặt phòng" hoặc "tôi muốn đổi phòng" — lễ tân tự gọi đúng bộ phận (booking, housekeeping…). Không cần biết bên trong có bao nhiêu nhân viên.

Router skill cũng vậy. Bạn nói "add file này vào wiki" → `/aiws-wiki register` tự nhận diện:
- 1 file lẻ → chạy single-file flow
- Cả thư mục → delegate sang skill batch
- Format đã ổn định sau sample-first → suggest tạo PMP

### 4.2. Nhập tham số tự nhiên

Không cần học CLI argument. Chỉ cần nói chuyện bình thường:

```
Bạn: "Add file docs/design/F04_BookingSearch_DD_v2_FE.md vào wiki,
      đây là detail design của màn tìm kiếm đặt phòng F04."

AI: → /aiws-wiki register
    → STAGE 1: detect file type (.md, dùng as-is)
    → STAGE 2: classify artifact_type → "detailed_design_fe" (confidence 0.82)
              "Confirm artifact type là 'detailed_design_fe' nhé?"
    → Bạn: "Đúng"
    → STAGE 3: build meta + lint + verify
```

---

## 5. Ví dụ minh hoạ: một task thực tế của AI

### Scenario

> BrSE bảo AI: *"Generate testcase cho màn Booking Search (F04)"*

### Có Wiki tốt — AI làm gì?

```
1. AI lookup:  /aiws-wiki lookup --query "F04 booking search"

   Thủ thư tra index → hit meta SRC-DD-F04-BOOKING-SEARCH-FE
     (T1 exact match trên "F04") → early return.

2. AI mở meta đó (Layer 1). Đọc ngay:
     - Summary, Lookup Keys
     - ## Related Sources:
         • SRC-BD-F04-BOOKING-SEARCH      (upstream_input)
         • SRC-DD-F04-BOOKING-SEARCH-API  (companion_design)
         • SRC-DD-F04-BOOKING-SEARCH-BE   (companion_design)
         • SRC-ITTC-F04                   (downstream_target)
         • SRC-TBL-BOOKING                (upstream_input)
     - Cautions: "§3.2 đã chốt theo Q&A-2026-04-12"

3. AI đi tiếp theo ## Related Sources → mở các meta liên quan
   (BD, DD-API, DD-BE, test case). Mỗi meta lại có ## Related
   Sources riêng để đi sâu thêm khi cần.

4. AI lookup tiếp: /aiws-wiki lookup --query "Q&A-2026-04-12"
     → hit SRC-QA-2026-04-12-BOOKING-EMPTY-RESULT
     → AI đọc meta → đủ context.

5. AI quyết định mở file DD gốc để lấy chi tiết
   acceptance criteria → viết testcase.

6. Mỗi testcase trace đầy đủ:
     - Req: SRC-REQ-F04
     - DD: SRC-DD-F04-BOOKING-SEARCH-FE / API / BE
     - Q&A: SRC-QA-2026-04-12

→ Tổng thời gian: ~5 phút.
→ Có audit trail đầy đủ.
```

### Không có Wiki — AI làm gì?

```
1. AI không có gì để tra. Đọc thẳng folder docs/.
2. Mở 8 file design, 12 file Q&A, đọc lần lượt.
3. Tốn nhiều context, dễ bỏ sót Q&A-2026-04-12.
4. Viết testcase nhưng KHÔNG biết bị ảnh hưởng bởi Q&A mới.
5. Người review phải tự kiểm tra lại từ đầu.

→ Tổng thời gian: ~30 phút + có thể bị sai.
```

Đó là lý do Wiki **không phải là việc thừa cho team rảnh** — nó là khoản đầu tư giúp AI làm task nhanh hơn, đúng hơn, và người review không phải làm lại.

---

## 6. Build Wiki phù hợp với dự án — nguyên tắc dễ nhớ

### 6.1. 5 câu hỏi quyết định "có cần lên Wiki không?"

Trước khi đưa một tài liệu vào Wiki, hỏi 5 câu này:

| # | Câu hỏi | Nếu "Không" |
|---|---|---|
| 1 | Tài liệu đã **chốt** chưa (không còn nháp, TBD)? | Để notebook chờ chốt |
| 2 | Có ít nhất 1 **trường hợp cụ thể** sẽ cần tra lại sau 1 tháng? | Không cần build meta |
| 3 | Có **người khác trong team** sẽ cần đến? (Không chỉ note cá nhân) | Không phải project knowledge |
| 4 | Nội dung **có nguồn rõ ràng** (không phải suy đoán)? | Đợi có evidence mới làm |
| 5 | Bạn biết đặt nó vào **loại nào** trong 14 artifact type? | Hỏi Wiki Manager / AI confirm trước |

Cả 5 đều "Có" → đáng build meta. Một câu "Không" → chờ.

### 6.2. Bí quyết viết Meta tốt — 4 phần quan trọng nhất

#### a) Summary (1–2 câu)

**Tốt:**
> "Thiết kế chi tiết FE màn tìm kiếm đặt phòng F04: filter, sort, paging, xử lý khi không có kết quả."

**Xấu:**
> "Đây là tài liệu thiết kế." (quá chung chung)
> "Tài liệu này mô tả màn tìm kiếm đặt phòng. Màn tìm kiếm có ô search, filter theo ngày…[tiếp 30 dòng]" (vi phạm "không inline source")

#### b) Lookup Keys với Tier

**Quy tắc gắn Tier:**

- **T1** — Mỗi meta nên có **2–4 từ T1** là ID/canonical name. Không có T1 → search bằng ID không ra.
- **T2** — 5–15 từ. Mix tiếng Việt, tiếng Anh, tên technical, tên business.
- **T3** — 2–5 từ. Loại tài liệu, workflow stage, domain general.

**Sai lầm phổ biến:** chỉ gắn T3 vì "an toàn" → meta không bao giờ lên top khi search.

#### c) `## Related Sources`

Liệt kê các source liên quan kèm **role** có hướng. Đây là cách meta điều hướng AI sang tri thức tiếp theo. Ví dụ: BD gốc (`upstream_input`), các lớp cùng function FE/API/BE (`companion_design`), test case (`downstream_target`). Section này được tool scaffold tự động — bạn chỉ cần điền đúng target source_id và role.

#### d) Cautions (rất quan trọng)

Viết khi tài liệu có:
- Phần nào outdated chưa update.
- Khác biệt giữa MD và PDF gốc (diagram, table phức tạp).
- Mâu thuẫn với artifact khác.
- Đã bị thay thế một phần bởi Q&A/CR mới.

### 6.3. Sample-first — bí quyết tiết kiệm thời gian

Đừng build 80 meta cùng lúc rồi mới phát hiện profile sai. Quy tắc vàng:

```
   Chọn 2–3 tài liệu đại diện cùng format
            │
            ▼
   Build meta cho chúng (qua /aiws-wiki register)
            │
            ▼
   Tự verify bằng /aiws-wiki test-lookup
            │
            ▼
   Có ra đúng kết quả không?
       │            │
       Có           Không
       │            │
       ▼            ▼
   Format ổn   Fix profile/keys
   định?           │
       │            ▼
       ▼        Build lại sample
   Tạo PMP để
   reuse cho       │
   batch lớn       │
       │            │
       └─→ Mass build ←┘
           (qua /aiws-wiki register folder mode)
```

### 6.4. Project Wiki vs Local Wiki — đặt cái gì ở đâu?

| Tài liệu | Nơi đặt | Lệnh dùng |
|---|---|---|
| Tài liệu của **chính dự án này** | **Project Wiki** | `/aiws-wiki register` |
| Tài liệu **chung dùng được nhiều dự án** (Fujitsu manual…) | **Local Wiki** | `/aiws-wiki add-local-knowledge` |
| Tài liệu **bí mật cá nhân** | KHÔNG đưa lên Wiki nào | — |

---

## 7. Cách review Wiki — checklist cho người KHÔNG biết code

Đây là phần dành riêng cho bạn nếu vai trò là **người duyệt** Wiki (PM, BrSE senior, Wiki Manager) và Wiki thường được AI build sẵn — bạn cần xác nhận đúng/sai.

### 7.1. Review 1 meta trong 5 phút — quy trình 3 bước

```
   ┌─────────────────────────────────────────┐
   │  Bước A: Mở meta file (.md), đọc 6 phần: │
   │   - Summary                              │
   │   - Lookup Keys (kiểm Tier T1/T2/T3)     │
   │   - ## Related Sources (target + role)   │
   │   - Source-Specific Hints                │
   │   - Cautions                             │
   │   - artifact_locator (đường dẫn)         │
   └──────────────────┬──────────────────────┘
                      ▼
   ┌─────────────────────────────────────────┐
   │  Bước B: Mở artifact gốc (file thật)     │
   │   Check: meta có miêu tả đúng không?     │
   │   Lookup Keys có đủ không?               │
   └──────────────────┬──────────────────────┘
                      ▼
   ┌─────────────────────────────────────────┐
   │  Bước C: Chạy /aiws-wiki test-lookup           │
   │   Để xem AI có tìm ra meta này không.    │
   │   (Cách dễ nhất: bảo AI chạy giúp.)      │
   └─────────────────────────────────────────┘
```

### 7.2. Checklist 14 câu cho người review

Dành cho người **không biết code**. Mở meta ra và check từng dòng:

**Phần A — Identity**

- [ ] `source_id` có **UPPERCASE, có gạch ngang**, và có ý nghĩa? (Ví dụ `SRC-DD-F04-BOOKING-SEARCH-FE` thì OK; `src-1234-test` thì xấu.)
- [ ] `title` đọc lên hiểu ngay tài liệu nói gì?
- [ ] `artifact_type` thuộc **14 loại trong taxonomy** (không phải tự đặt)?
- [ ] `profile_id` khớp với `artifact_type`?
- [ ] `knowledge_class` hợp lý? (Req Def đã chốt → `source_of_truth`; nháp → `curated`; code thường → `reference`.)
- [ ] `artifact_locator` trỏ đến file **có tồn tại** trên máy?

**Phần B — Nội dung & Tier**

- [ ] **Summary** ≤ 2 câu, đọc xong hiểu tài liệu là gì? (Nếu > 5 dòng → trả về sửa.)
- [ ] **Lookup Keys** có **ít nhất 2 từ T1** (ID/canonical name)?
- [ ] T2 có cả **tiếng Việt và tiếng Anh** (nếu dự án bilingual)?
- [ ] Lookup Keys có **business term** (không chỉ technical name)?
- [ ] **Cautions** có nếu tài liệu có phần outdated / khác PDF gốc?

**Phần C — Related Sources (quan hệ cross-artifact)**

- [ ] Có `## Related Sources` nếu tài liệu thuộc 1 entity lớn / có artifact liên quan (BD↔DD↔Testcase, FE/API/BE…)?
- [ ] Mỗi entry có **target source_id tồn tại** + **role hợp lệ** (trong role enum)?
- [ ] Không còn TODO scaffold chưa điền (vd `<target_source_id>`)?

**Phần D — Test thực tế**

- [ ] Bạn (hoặc AI) đã chạy **`/aiws-wiki test-lookup`** → meta này được tìm thấy với các từ khoá điển hình?

### 7.3. Quyết định sau khi review

| Tình huống | Hành động |
|---|---|
| ≤ 1 câu "Không" trong checklist, lỗi nhỏ format | **Approve**, sửa nhẹ |
| 2–4 câu "Không", liên quan keys/summary/cautions | **Request edit** — ghi rõ phần nào cần sửa |
| Meta tả sai nội dung source, hoặc source không tồn tại | **Reject** — không merge, yêu cầu build lại |
| Meta có inline cả source (≥ 50 dòng nội dung) | **Reject** — vi phạm "no inline source" |
| Có trigger Promotion Gate (đổi knowledge_class lên source_of_truth, split/merge…) | **Escalate** — cần CR + Wiki Manager duyệt riêng |

### 7.4. 5 dấu hiệu "đỏ" — meta xấu thấy ngay không cần đọc kỹ

1. **Summary dài hơn 10 dòng** → chắc chắn inline source, vi phạm rule.
2. **Không có Tier T1 nào** trong Lookup Keys → meta không thể được tìm bằng ID.
3. **Không có Cautions** dù tài liệu được biết là có phần outdated.
4. **`knowledge_class: source_of_truth`** cho một file nháp / draft / nội bộ team → over-claim.
5. **`artifact_locator` không tồn tại** hoặc trỏ về file đã rename → liên kết gãy.

### 7.5. Nếu bạn KHÔNG biết code, làm sao chạy test lookup?

Cách đơn giản nhất: nhờ AI làm.

> "Hãy chạy `/aiws-wiki test-lookup` mode C cho task: 'tìm tài liệu về màn Booking Search F04'. Cho tôi xem kết quả lookup score và meta nào được tìm thấy."

AI sẽ:
1. Phân tích task → sinh 3–5 query phù hợp.
2. Chạy lookup tool cho từng query.
3. Tổng hợp: meta nào hit, score bao nhiêu, có gap nào không.
4. Báo "PASS / FAIL" cho từng query.

→ Bạn nhận report dễ đọc, không cần biết CLI.

---

## 8. Promotion Gate — khi nào cần Wiki Manager duyệt thêm

Một số thay đổi quan trọng hơn cập nhật bình thường. Khi gặp **5 trigger** sau, AI/người **dừng lại**, không tự apply, phải tạo CR + Wiki Manager duyệt:

1. **Set `knowledge_class: source_of_truth`** — nâng tài liệu lên truth.
2. **Đổi `source_id`** của meta đã được tham chiếu.
3. **Split hoặc merge** meta records.
4. **Đánh dấu artifact quan trọng là `deprecated`**.
5. **Đổi traceability chain (`related_artifact_refs` / `## Related Sources`)** giữa các artifact lớn.

Đây gọi là **Promotion Gate** — hàng rào ngăn AI tự ý promote nội dung lên canonical mà không có người kiểm soát.

---

## 9. Khi nào KHÔNG nên dùng Wiki?

| Tình huống | Lý do | Thay thế |
|---|---|---|
| Nháp, brainstorm, ý tưởng cá nhân | Wiki = nội dung đã chốt | Notebook cá nhân |
| Thông tin thay đổi hàng giờ (status board) | Meta sẽ outdated ngay | Jira / dashboard |
| Email/Slack rời rạc | Không có cấu trúc | Tổng hợp thành Q&A artifact trước |
| Code generated tự động | Không reuse được, noise | Skip, không build meta |
| Tài liệu duplicate (3 bản cùng nội dung) | Gây confuse | Chọn 1 canonical, archive còn lại |

---

## 10. FAQ — câu hỏi hay gặp

### Q1: Tôi không biết code, tôi có cần build meta không?

**Không bắt buộc.** Vai trò của bạn nhiều khả năng là:
- Quyết định tài liệu nào *đáng* lên Wiki (5 câu hỏi mục 6.1).
- **Review** meta do AI build có đúng không (checklist mục 7.2).
- Cung cấp domain knowledge để Lookup Keys có business term.

Người build meta thường là AI hoặc BrSE/dev (qua `/aiws-wiki register`). Bạn là **người duyệt**.

### Q2: AI có thể tự build meta cho cả dự án mà không cần người không?

**Không nên.** AI build thì nhanh, nhưng:
- AI không biết tài liệu nào đã chốt vs nháp.
- AI dễ dùng `knowledge_class: source_of_truth` quá rộng (over-claim).
- AI có thể bỏ sót business term tiếng Việt mà chỉ ghi technical name.
- AI có thể classify sai artifact_type → profile sai → mapping sai.

**Cách đúng:** AI build → người confirm artifact_type → người review final → AI fix → người approve.

### Q3: Wiki update thường xuyên không? Ai update?

Wiki **không** update mỗi ngày như Jira. Wiki update khi:
- Tài liệu mới chốt → `/aiws-wiki register`.
- Tài liệu cũ thay đổi nội dung (kể cả `## Related Sources`) → `/aiws-wiki refresh`.
- Format đã đổi (PMP drift) → `/aiws-wiki refresh`.

Quy trình: **candidate → CR → Wiki Manager duyệt → AI apply**.

### Q4: Nếu meta sai mà tôi không có quyền sửa, làm gì?

Ghi vào notebook hoặc tạo CR (Change Request) → gửi Wiki Manager. Tuyệt đối **không tự sửa canonical wiki** dù lỗi nhỏ.

### Q5: Wiki có thể search tiếng Việt được không?

**Có, nếu meta có Lookup Keys tiếng Việt với Tier T2.** Thủ thư chỉ khớp từ — viết "đặt phòng" thì search "đặt phòng" mới ra. Nên Lookup Keys phải mix cả tiếng Việt (T2) và technical name (T2/T1).

### Q6: AI có "hiểu" được tài liệu mà không cần Wiki không?

Có thể, nhưng **chậm, dễ sai, không trace được**. AI sẽ đọc 50 trang DD → tốn context → dễ bỏ sót Q&A liên quan → output không có link traceability. Wiki là cách để AI làm task **nhanh + đúng + có audit trail**.

### Q7: Local Wiki dùng để làm gì? Có cần build không?

Local Wiki dùng cho **knowledge dùng được nhiều dự án** (ví dụ manual của framework công ty, design pattern chung, glossary domain). Nếu dự án bạn không cần re-use kiến thức từ dự án khác → không cần local wiki. Nếu cần → `/aiws-wiki add-local-knowledge`.

### Q8: Wiki có thay thế Confluence/SharePoint không?

**Không hoàn toàn.** Wiki của AIWS là **lớp meta + index** (cộng `## Related Sources` trong từng meta) giúp AI tra cứu nhanh. Bạn vẫn có thể giữ Confluence/SharePoint làm nơi lưu file gốc. Wiki của AIWS có thể trỏ `artifact_locator` về URL Confluence (nếu setup phù hợp).

### Q9: Làm sao liên kết các artifact của cùng 1 entity (vd 1 function có BD + DD + Testcase)?

Ghi quan hệ trong section **`## Related Sources`** của từng meta, kèm role có hướng (`upstream_input`, `companion_design`, `downstream_target`…). Section này được tool scaffold tự động khi build meta — bạn chỉ điền target source_id + role. Nếu 1 file lẻ không có artifact liên quan → để `## Related Sources` trống cũng được.

### Q10: PMP (Project Mapping Pattern) khác Source Interpretation Profile thế nào?

- **Source Interpretation Profile** (`profiles/<id>.yml`) = quy tắc cho **loại tài liệu** chung (vd `design_doc.yml` cho mọi DD). Dùng được nhiều project.
- **PMP** (`profiles/mapping_patterns/PMP-<id>.yml`) = quy tắc cho **format cụ thể trong 1 project** (vd "DD của khách Fujitsu có 5 section thế này → map sang canonical slot thế kia"). Chỉ dùng trong project đó.

Tạo PMP sau khi `sample-first` build cho 2–3 sample xác nhận format ổn định.

---

## 11. Glossary — từ điển nhanh

| Từ | Ý nghĩa đời thường |
|---|---|
| **Artifact** | Tài liệu gốc (Req, DD, Q&A, code…) — "cuốn sách" |
| **Layer 1 / Wiki Source Meta** | "Tờ giới thiệu" 1 trang cho 1 artifact — **đơn vị tri thức** của Wiki |
| **`## Related Sources`** | "Mục Xem thêm" trong meta — trỏ sang source liên quan kèm role có hướng |
| **Index** | "Thẻ mục lục" của toàn bộ wiki, sinh tự động (`index.jsonl`) |
| **Lookup tool** | "Thủ thư" — công cụ search wiki (`/aiws-wiki lookup`) |
| **Source Interpretation Profile** | "Quy tắc xếp sách" cho từng loại tài liệu (`profiles/<id>.yml`) |
| **Project Mapping Pattern (PMP)** | "Khuôn dùng lại" cho format cụ thể trong project (`mapping_patterns/PMP-<id>.yml`) |
| **Source ID** | Mã định danh duy nhất cho 1 meta — tựa như mã sách thư viện |
| **Role (Related Sources)** | Vai trò có hướng của quan hệ: `upstream_input`, `companion_design`, `downstream_target`, `triggered_flow`, `related`… |
| **related_artifact_refs** | Danh sách phẳng (frontmatter) cho traceability — KHÔNG dùng để điều hướng |
| **Lookup Keys** | Từ khoá để tra meta — càng đầy đủ, AI càng dễ tìm |
| **Tier T1/T2/T3** | Mức độ "độc nhất" của từ khoá: T1×3 (ID), T2×1.5 (domain), T3×1 (label) |
| **Knowledge Class** | Mức độ tin cậy: `source_of_truth` > `curated` > `reference` > `history` |
| **Artifact Type Taxonomy** | 14 loại artifact chuẩn của AIWS |
| **Skill Router** | Skill đóng vai trò "lễ tân", delegate sang skill nội bộ phù hợp |
| **Promotion Gate** | 5 trigger khi cần Wiki Manager duyệt CR riêng |
| **Candidate** | Phát hiện "có thể đáng lên wiki" — chưa được approve |
| **CR (Change Request)** | Đề xuất chính thức để thêm/sửa/xoá nội dung canonical wiki |
| **Wiki Manager** | Người duyệt mọi thay đổi canonical wiki |
| **Project Wiki** | Wiki riêng của dự án hiện tại |
| **Local Wiki** | Wiki chứa knowledge dùng chung nhiều dự án trên máy bạn |
| **Canonical** | "Bản chính thức", đã qua duyệt — đối lập với "candidate" / "draft" |
| **Confirmed / Inferred / Unresolved** | 3 trạng thái nội dung: chắc chắn / suy luận / chưa rõ — phải tách rõ |
| **Resolved / Reflected / Superseded** | 3 trạng thái Q&A: đã trả lời / đã phản ánh vào Req Def / đã bị thay thế |

---

## 12. Đóng lại — 6 điều quan trọng nhất

Nếu bạn chỉ nhớ 6 thứ sau khi đọc tài liệu này:

1. **Wiki = thư viện 2 lớp + index.** Artifact gốc → Tờ giới thiệu (Layer 1 meta, có `## Related Sources`) → Index. AI luôn đi qua thủ thư.
2. **AI khớp từ với Tier.** T1 (ID) × 3, T2 (domain) × 1.5, T3 (label) × 1. Meta phải có ít nhất 2 T1.
3. **5 lệnh skill là đủ.** `/aiws-wiki register`, `/aiws-wiki refresh`, `/aiws-wiki lookup`, `/aiws-wiki add-local-knowledge`, `/aiws-wiki test-lookup`. Không cần nhớ skill nội bộ.
4. **Meta routes, source verifies.** AI dùng meta để định hướng, mở source khi cần evidence. Không bao giờ inline source vào meta.
5. **Sample-first khi build.** 2–3 sample → `/aiws-wiki test-lookup` → fix → mass build → tạo PMP để reuse.
6. **Không tự sửa canonical wiki.** Mọi thay đổi qua candidate → CR → Wiki Manager. Promotion Gate dừng AI lại khi cần.

> **Lúc nghi ngờ: HỎI, không SUY ĐOÁN.**
> **Khi chưa chốt: ĐỂ NOTEBOOK, không BUILD META VỘI.**

---

## Phụ lục: tài liệu liên quan

| Cần đào sâu vào | Đọc tài liệu |
|---|---|
| Quy trình build chi tiết theo 7 loại tài liệu | [MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS](./MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS.md) |

> Spec canonical chi tiết do AI Work System quản lý nội bộ — khi cần, hỏi AI: _"AIWS có spec nào về [chủ đề]?"_
