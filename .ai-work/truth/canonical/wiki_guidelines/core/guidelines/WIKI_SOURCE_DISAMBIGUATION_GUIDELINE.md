# WIKI_SOURCE_DISAMBIGUATION_GUIDELINE_v0_1

## 1. Purpose

Guideline này định nghĩa best practice để xử lý khi một project đăng ký nhiều wiki sources (project wiki hoặc local knowledge) có **khái niệm, tên lệnh, hoặc thuật ngữ trùng nhau** giữa các nguồn.

Mục tiêu:
- Ngăn AI tự động chọn nguồn có volume lớn hơn khi search (volume bias)
- Đảm bảo AI report kết quả từ **tất cả các nguồn liên quan** trước khi trả lời
- Cung cấp cơ chế để Human xác nhận nguồn mong muốn
- Chuẩn hóa cách thiết lập disambiguation policy khi đăng ký overlapping sources

---

## 2. Scope

### Guideline này áp dụng khi
- Project có ≥ 2 wiki sources (project wiki hoặc local knowledge) từ cùng vendor, domain, hoặc technology family
- Các sources đó có overlap đáng kể về thuật ngữ, lệnh, hoặc khái niệm
- AI có nguy cơ "chọn sai nguồn" vì một nguồn có volume lớn hơn (lexical search bias)

### Guideline này KHÔNG phải
- Governance rule (ai được update canonical Wiki → xem `WIKI_MINIMAL_GOVERNANCE_RULE`)
- Meta build guideline (cách tạo wiki meta → xem `WIKI_META_BUILD_UPDATE_GUIDELINE`)
- Quy định về cách đăng ký sources (→ xem skill `/aiws-wiki add-local-knowledge`)

---

## 3. Khi nào cần tạo disambiguation policy

### Trigger conditions

Tạo disambiguation policy khi hội đủ **hai điều kiện sau**:

**Điều kiện A — Overlap tồn tại:**
Ít nhất một trong các dấu hiệu sau:
- Cùng vendor (ví dụ: cùng Fujitsu, cùng IBM, cùng Oracle)
- Cùng technology family (ví dụ: cùng ngôn ngữ COBOL, cùng framework)
- Nhiều shared terms quan trọng (lệnh, khái niệm kỹ thuật, tên section)

**Điều kiện B — Volume không cân bằng đáng kể:**
Một nguồn có volume lớn hơn ≥ 5× so với nguồn kia — khoảng cách này đủ để gây volume bias trong lexical search.

> **Lưu ý:** Nếu volume cân bằng (~1×–3×) nhưng overlap rất cao (>50% terms chính đều xuất hiện ở cả hai bên), vẫn nên tạo disambiguation policy.

### Ví dụ thực tế
- Fujitsu ASP Manuals (~45× volume) vs Fujitsu NetCOBOL Manuals: cùng vendor, cùng COBOL, nhiều terms dùng chung
- Hai phiên bản manual khác nhau của cùng sản phẩm (V10 và V12): nhiều section cùng tên nhưng nội dung khác
- API spec cho 2 môi trường (staging vs production) dùng cùng endpoint names

---

## 4. Artifacts cần tạo

Disambiguation policy gồm 3 artifacts. Artifact 1 là bắt buộc; 2 và 3 tùy mức độ overlap.

### 4.1. Disambiguation policy section trong LOCAL_KNOWLEDGE_OVERVIEW.md (bắt buộc)

Thêm một section riêng trong `LOCAL_KNOWLEDGE_OVERVIEW.md` với tiêu đề rõ ràng (ví dụ: "Fujitsu COBOL Source Disambiguation Policy"). Section này phải chứa:

**a) Bảng nguồn:**

| Nguồn | Platform / Context | Signals nhận diện |
|-------|-------------------|-------------------|
| Tên nguồn A | mô tả platform | keyword1, keyword2, keyword3 |
| Tên nguồn B | mô tả platform | keyword4, keyword5, keyword6 |

**b) Hard rule 4 bước** — áp dụng khi Human **chưa chỉ định rõ** nguồn:

```
1. Search CẢ HAI (hoặc tất cả) nguồn — dùng --mode semantic để tránh volume bias
2. Report ngắn kết quả mỗi nguồn: tìm thấy hay không, section nào liên quan
3. Hỏi Human muốn xem nguồn nào:
   "Tìm thấy trong [A] ([section]) và [B] ([section]). Bạn muốn xem A, B, hay cả hai?"
4. Nếu chỉ một nguồn có → vẫn báo và hỏi confirm:
   "Chỉ tìm thấy trong [A], không có ở [B]. Bạn muốn xem không?"
```

**c) Định nghĩa "đã chỉ định nguồn":**

Liệt kê rõ signals nào = đã chỉ định rõ nguồn (AI search thẳng nguồn đó) vs signals nào = vẫn ambiguous (phải search cả hai).

**d) Pointer đến disambiguation reference file** (nếu có artifact 4.2):
`Chi tiết overlap terms: `wiki_disambiguation.md`.`

**Template section mẫu:**

```markdown
## [Tên nhóm nguồn] Source Disambiguation Policy

> **Áp dụng:** Mọi wiki search liên quan đến [domain/vendor].

Local wiki có **[N] nguồn [vendor/domain] độc lập**, nhiều khái niệm trùng nhau:

| Nguồn | Platform | Đặc trưng nhận diện |
|-------|----------|---------------------|
| **[Nguồn A]** | [platform A] | [signal1, signal2, signal3] |
| **[Nguồn B]** | [platform B] | [signal4, signal5, signal6] |

**Rule (HARD — không được bỏ qua):** Nếu Human **chưa chỉ định rõ** nguồn:

1. **Search cả [N] nguồn** (`--mode semantic` để tránh volume bias)
2. **Report ngắn** kết quả mỗi nguồn (tìm thấy hay không, section nào)
3. **Hỏi Human** muốn xem bên nào:
   > "Tìm thấy trong **[A]** ([section]) và **[B]** ([section]). Bạn muốn xem [A], [B], hay cả hai?"
4. Nếu chỉ một bên có → báo và hỏi confirm trước khi trình bày.

**Coi là đã chỉ định** khi Human nhắc đến signal đặc trưng của một bên → search thẳng bên đó.

**Không coi là đã chỉ định:** [liệt kê shared terms mà cả hai bên đều có]

Chi tiết overlap terms: `wiki_disambiguation.md`.
```

---

### 4.2. wiki_disambiguation.md — Reference file (khuyến nghị khi overlap cao)

File này lưu phân tích chi tiết các terms trùng nhau — không cần đọc tự động, chỉ tra khi cần xác minh term cụ thể.

**Khi nào cần tạo:** Khi có ≥ 10 shared terms hoặc khi cần phân loại mức độ ambiguity.

**Cấu trúc:**

```markdown
# [Group Name] — Wiki Source Disambiguation

> Tài liệu tham khảo. Không đọc tự động — chỉ tra khi cần xác minh term cụ thể có overlap không.

## Các nguồn cần phân biệt

| Nguồn | source_type | Platform | Meta dir |
|-------|------------|----------|----------|
| [Nguồn A] | `type_a` | [platform] | `path/to/meta/` |
| [Nguồn B] | `type_b` | [platform] | `path/to/meta/` |

## Platform signals (nhận diện nhanh)

| Signal | → Nguồn |
|--------|---------|
| keyword1, keyword2 | Nguồn A |
| keyword3, keyword4 | Nguồn B |

## Terms có trong CẢ HAI nguồn

### Nhóm 1 — Cùng tên, khác sản phẩm (dễ nhầm nhất)

| Term | Entries A | Entries B | Ghi chú |
|------|-----------|-----------|---------|
| `TermX` | N | M | A: [context A] · B: [context B] |

### Nhóm 2 — [category khác]

...

## Hướng dẫn search khi đã biết nguồn

[search commands với filter theo source_type]
```

---

### 4.3. Hard rule trong CLAUDE.local.md (hoặc project rules file)

Ghi thành HARD RULE trong `CLAUDE.local.md` của project để đảm bảo AI không bypass. Pattern:

```markdown
## Rule [ID] — [Group name] source disambiguation (HARD RULE)

[Project wiki / Local wiki] có **[N] nguồn [domain] độc lập** với nhiều khái niệm trùng nhau.

**Flow BẮT BUỘC khi Human chưa chỉ định nguồn:**

1. **Search cả [N] nguồn** — dùng `--mode semantic` để tránh volume bias
2. **Report kết quả mỗi bên** ngắn gọn: có hay không, section nào liên quan
3. **Hỏi Human** muốn xem bên nào:
   > "[Greeting]. Tìm thấy trong **[A]** ([section]) và **[B]** ([section]). Bạn muốn xem [A], [B], hay cả hai?"
4. Nếu **chỉ một bên có** → vẫn báo và hỏi confirm

Nếu Human đã dùng signal rõ của **một bên** → search thẳng bên đó, không cần check bên kia.

| [A] signals | [B] signals |
|-------------|-------------|
| signal1, signal2 | signal3, signal4 |

**TUYỆT ĐỐI KHÔNG** tự chọn và trả luôn kết quả từ một nguồn mà không report bên kia.

Chi tiết overlap terms: [link to wiki_disambiguation.md].
```

---

## 5. AI behavior rule (runtime)

Đây là rule AI phải follow trong mọi context (kể cả ngoài AIP execution).

### 5.1. Default behavior khi nguồn chưa được chỉ định

**HARD RULE — không được bỏ qua:**

Khi query có thể match ≥ 2 nguồn có disambiguation policy:
1. Search tất cả nguồn liên quan (dùng `--mode semantic`)
2. Nhóm kết quả theo nguồn
3. Report ngắn cho mỗi nguồn: có/không, sections nào liên quan
4. Hỏi Human chọn nguồn — KHÔNG tự trả lời từ một nguồn mà không hỏi

**TUYỆT ĐỐI KHÔNG:**
- Tự pick nguồn có nhiều kết quả hơn (volume bias)
- Tự pick nguồn rank cao hơn trong lexical search
- Trả lời từ một nguồn mà không mention sự tồn tại của nguồn kia

### 5.2. Volume bias — lý do cần semantic mode

Trong lexical search, sources có volume lớn hơn sẽ **luôn thắng** vì chứa nhiều indexed terms hơn — không phải vì phù hợp hơn về ngữ nghĩa.

**Ví dụ:** ASP Manuals (volume ~45×) vs NetCOBOL: query `CALL` trả 36 ASP hits vs 30 NetCOBOL hits. AI sẽ chọn ASP — sai nếu user đang hỏi về NetCOBOL runtime.

**Giải pháp:** Luôn dùng `--mode semantic` khi search sources có disambiguation policy.

### 5.3. Xác định "đã chỉ định nguồn" (disambiguation resolution)

AI có thể tự resolve sang một nguồn **khi và chỉ khi** Human đã dùng signal đặc trưng của nguồn đó trong query (theo signal table trong policy).

**Pattern xác định:**

| Loại signal | Có resolve không? |
|-------------|-------------------|
| Signal đặc trưng rõ ràng của 1 nguồn | ✅ Resolve về nguồn đó |
| Term chung trong nhiều nguồn | ❌ Phải search cả hai |
| Tên lệnh/feature dùng chung | ❌ Phải search cả hai |
| Term kỹ thuật chung của domain | ❌ Phải search cả hai |

### 5.4. Trường hợp chỉ một nguồn có kết quả

Kể cả khi chỉ tìm thấy ở một nguồn, AI vẫn phải báo và hỏi confirm:

> "Chỉ tìm thấy trong **[nguồn A]** (section: [X]), không có ở **[nguồn B]**. Bạn muốn xem không?"

Không tự động trả lời mà không report kết quả tìm kiếm.

---

## 6. Thiết kế signal table

### Mục đích signal table

Signal table xác định các keywords đặc trưng (platform-specific) để phân biệt nguồn nào đang được hỏi. Giúp AI biết khi nào có thể resolve về một nguồn mà không cần search cả hai.

### Nguyên tắc chọn signal

**Signals tốt (nên đưa vào table):**
- Tên sản phẩm chính thức của nguồn đó (ví dụ: "ASP COBOL G", "NetCOBOL V11")
- Feature/tool chỉ có ở nguồn đó (ví dụ: "cobpconv", "FORML", "MeFtWeb")
- Tên hệ thống/môi trường đặc trưng (ví dụ: "本社", "福島", "Windows COBOL runtime")
- Version numbers cụ thể của sản phẩm đó

**Signals không nên (không đủ đặc trưng):**
- Tên vendor chung cho cả hai nguồn (ví dụ: "Fujitsu")
- Domain keywords chung (ví dụ: "COBOL", "migration")
- Lệnh/function cùng tên trong nhiều nguồn (ví dụ: "CALL", "DISPLAY", "MOVE")
- Japanese terms chung trong domain

### Pattern signal table

```markdown
| [Nguồn A] signals | [Nguồn B] signals |
|-------------------|-------------------|
| ProductName-A, ToolA1, ToolA2 | ProductName-B, ToolB1, ToolB2 |
| EnvContext-A, SystemA | EnvContext-B, SystemB |
```

---

## 7. Phân tích terms overlap (cho wiki_disambiguation.md)

### Các nhóm overlap cần phân loại

**Nhóm 1 — Cùng tên, khác sản phẩm (nguy hiểm nhất)**
Terms giống hệt nhau nhưng refer đến different products trong mỗi nguồn.
Ví dụ: "MeFt" trong ASP là ASP MeFt_Web (middleware); trong NetCOBOL là MeFt V12.2 (I/O library).

**Nhóm 2 — Lệnh/cú pháp chung (cùng ngôn ngữ, khác runtime)**
Cùng ngôn ngữ nên dùng chung syntax, nhưng runtime context khác nhau.
Ví dụ: COBOL statements (CALL, DISPLAY, MOVE) có trong cả ASP COBOL G lẫn NetCOBOL.

**Nhóm 3 — Encoding/standards (ít ambiguous)**
Standards chung nhưng implementation có thể khác.
Ví dụ: EBCDIC, JIS, EUC.

**Nhóm 4 — Database/connectivity**
Database terms có mức độ ambiguity thấp hơn vì context thường rõ hơn.

### Format entry trong disambiguation table

```markdown
| Term | Entries A | Entries B | Ghi chú |
|------|-----------|-----------|---------|
| `TermX` | N | M | A: [brief context in A] · B: [brief context in B] |
```

Nên ghi `Entries A` và `Entries B` = số indexed entries/chapters chứa term → giúp ước lượng volume bias.

---

## 8. Anti-confusion notes

### 8.1. Disambiguation policy ≠ search filter
Policy không cấm search một nguồn — nó yêu cầu **search tất cả** rồi report, không phải loại trừ nguồn nào.

### 8.2. "Semantic mode" không phải option tùy chọn
Khi có disambiguation policy, `--mode semantic` là bắt buộc (không phải preferred). Lexical mode sẽ luôn trả volume-biased results.

### 8.3. Hard rule overrides wiki-first
Wiki-first principle ưu tiên curated knowledge trước source artifacts — điều này không thay đổi. Disambiguation rule là rule **về cách search** (search which sources), không phải rule về layer (wiki vs source).

### 8.4. Disambiguation áp dụng cho cả project wiki lẫn local knowledge
Rule này không giới hạn ở local knowledge. Nếu project wiki sources cũng có overlap, áp dụng tương tự.

### 8.5. Per-source reporting ≠ đọc toàn bộ artifact
"Report kết quả mỗi nguồn" nghĩa là báo search hits (có/không, section nào) — không phải đọc và summarize toàn bộ nội dung từ cả hai nguồn trước khi hỏi.

---

## 9. Relationship with other guidelines

- **WIKI_FIRST_RUNTIME_GUIDANCE_v0_1** — Runtime layer order (Layer 1-4). Disambiguation rule hoạt động tại Layer 3/4 khi AI search source artifacts.
- **WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1** — Cách build wiki meta. Meta build không thay thế disambiguation — search vẫn cần check multiple sources khi overlap.
- **WIKI_MINIMAL_GOVERNANCE_RULE_v0_1** — Ai được update canonical Wiki. Không liên quan trực tiếp.
- **Skill `/aiws-wiki add-local-knowledge`** — Khi đăng ký nguồn mới: nếu nguồn mới overlap với nguồn hiện có, trigger tạo disambiguation policy.

---

## 10. Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-05-21 | v0.1 | Initial draft. Extracted and generalized from real-world implementation in VTI-AI-Program Test project (Fujitsu COBOL ASP/NetCOBOL disambiguation). Source: AIP-EXEC-013. |
