# Lookup Key Strategy Spec — AI Work System MVP
Version: 0.2
Status: active  <!-- promoted draft→active by CR-AIWS-2026-07-001 Q3 (2026-07-04): the scoring subset in §7.4 is implemented -->
Updated: 2026-07-04
Updated: 2026-05-25
Source: CR-D2, AIWS-Wiki-CR-Proposal-2026-05-25.md §3

---

## 1. Purpose

Spec này định nghĩa **chiến lược phân tầng lookup keys** trong Wiki Source Meta, nhằm cải thiện routing precision và giảm candidate list phình không kiểm soát.

Vấn đề cần giải quyết:
- Routing system hiện không phân biệt keyword identifier (T1 — high discrimination) vs section heading generic (T3 — low discrimination)
- Candidate list phình → giảm precision → tốn token AI
- Không có rule kiểm tra "keyword này có thực sự discriminatory không?"

Spec này bổ sung cho `WIKI_META_INDEX_SPEC` (artifact meta structure) và `Knowledge_Routing_Spec_MVP` (routing logic).

---

## 2. Tier Definitions

Mỗi lookup key trong meta được gán một tier phản ánh mức độ discriminatory của nó:

### T1 — Unique Identifier (Mandatory ≥1 per meta)

**Định nghĩa:** Keyword nhận dạng artifact/object duy nhất trong project scope.

**Đặc điểm:**
- Nếu search đúng keyword này, result set rất nhỏ (≤ N artifacts, N mặc định = 10)
- Không thể nhầm với artifacts khác nếu dùng standalone
- Stable qua thời gian (không thay đổi khi format drift)

**Ví dụ:**
- Function ID: `CB01001`, `F04`, `BA05001`
- Artifact ID: `SRC-DD-CB01001-FE`
- Canonical name: `発注処理`, `Order Processing`, `xử lý đặt hàng`
- Screen/API endpoint có ID unique: `/api/v1/orders/CB01001`

**Rule: T1 phải có ≥1 per meta.** Lint rule: `warn` khi meta thiếu T1 (không hard-fail — xem §6 Exceptions).

### T2 — Domain-Specific Term (Optional)

**Định nghĩa:** Keyword domain-specific nhưng không guaranteed unique, cần kết hợp với T1 hoặc qualifier để đạt precision tốt.

**Đặc điểm:**
- Hit rate có thể cao hơn T1 nhưng result set vẫn trong domain scope nhất định
- Thường là endpoint path, table name, alias, subsystem keyword

**Ví dụ:**
- Database table name: `t_order_header`, `m_product`
- API endpoint path: `/api/v1/orders`
- Subsystem: `purchasing`, `inventory`
- Japanese alias: `発注`, `在庫管理`

### T3 — Category Label (Optional)

**Định nghĩa:** Keyword phân loại artifact theo category nhưng generic và không phân biệt được artifact cụ thể.

**Đặc điểm:**
- Dùng standalone → hit quá nhiều artifacts (> N)
- Hữu ích như additional filter, không phải primary search term
- Thường là artifact type label, document category

**Ví dụ:**
- `detail_design`, `basic_design`, `api_contract`
- `review-relevant`, `testcase-relevant`
- `function`, `screen`, `table`

---

## 3. Rule K-1 — Discriminatory Value Test

**Rule:** Một keyword được phân loại T1 chỉ khi nó pass test:

> "Nếu search đúng keyword này trong wiki index, result set có nhỏ và đúng không?"

**Formal condition:** `search(keyword) → |result_set| ≤ N` trong scope hiện tại.

**Default N = 10.** Configurable per project/profile.

**Failure action:** Nếu keyword fail test → không được gán T1; phải pair với qualifier để đạt T1-level precision, hoặc gán T2/T3.

**Ví dụ:**
- `CB01001` → unique → T1 ✓
- `design` → hits hàng trăm artifacts → T3, không phải T1
- `ordering` → hits ~50 artifacts → T2 at best, pair với `CB01001` thành `CB01001 ordering` → T1 ✓

---

## 4. Rule K-2 — Tier Combination Rule

Nếu T1 của artifact cần nhiều tokens (ví dụ cụm tên dài), và project cho phép compound keys:

**Rule:** Compound T1 key = `{T2_qualifier}_{T1_identifier}` hoặc space-separated. Ví dụ:
- `ordering_CB01001` thay vì chỉ `CB01001` (nếu IDs có thể trùng cross-subsystem)
- `発注_CB01001` (Japanese + ID)

Compound key giữ nguyên tier T1 vì tổng hợp vẫn unique.

---

## 5. Rule K-3 — Anti-Pattern: Standalone Generic Section Heading

**Anti-pattern:** Section heading generic dùng standalone làm lookup key.

**Examples of violating patterns:**
- `design` (quá generic)
- `API` (quá generic)
- `search` (quá generic)
- `process` (quá generic)
- `list` (quá generic)

**Compliant alternatives:**
- `F04_API` thay vì `API`
- `CB01001_search` thay vì `search`
- `detail_design_fe` (combined với type) thay vì `design`

**Rule:** Keywords matching generic heading patterns KHÔNG được dùng standalone làm T1 hoặc T2. Phải pair với qualifier (function ID, subsystem, artifact ID).

> **PLANNED / NOT BUILT (CR-AIWS-2026-08-057):** đoạn dưới mô tả tooling chưa tồn tại (`lint_wiki.py` không có `--check-tiers`) — design intent, không phải hành vi. Build → CR riêng gỡ banner.

Lint rule `lint_wiki.py --check-tiers` sẽ flag violation khi meta có keyword matching known generic patterns standalone.

---

## 6. Exceptions — T1 Mandatory Exemptions

Các trường hợp meta có thể không có T1 mà lint chỉ warn (không fail):

1. **Methodology spec artifact:** Spec có well-known canonical name (ví dụ `Knowledge_Routing_Spec_MVP`) — tên spec itself phục vụ như effective T1 ngay cả khi không phải function ID.
2. **External reference artifact:** Artifact từ nguồn bên ngoài không có project-level unique ID.
3. **Legacy artifact:** Artifact cũ chưa có ID convention.

Để claim exception, meta nên có field `t1_exception_reason: <reason>` để lint biết skip warning.

> **PLANNED / NOT BUILT (CR-AIWS-2026-08-057):** `t1_exception_reason` chưa được tool nào đọc (0 hit code) — design intent, không phải hành vi. Build → CR riêng gỡ banner.

---

## 7. Tooling Impact

### 7.1. Profile schema extension

Profile YAML nên thêm optional field `lookup_key_tier_hints`:

```yaml
lookup_key_tier_hints:
  T1:
    - pattern: "[A-Z]{2}[0-9]{5}"   # function ID pattern (regex)
    - pattern: "SRC-[A-Z]+-.*"       # source ID pattern
  T2:
    - pattern: "t_[a-z_]+"           # table name pattern
    - pattern: "/api/v[0-9]/"        # API path pattern
  T3:
    - values: [detail_design, basic_design, api_contract, test_case]  # fixed enum
```

Profile-level hints cho phép `build_wiki_source_meta.py` tự động tag tier khi emit lookup keys.

### 7.2. Meta field: lookup key tier tagging

Trong wiki source meta, lookup keys nên được tagged với tier:

```yaml
lookup_keys:
  - key: CB01001
    tier: T1
  - key: ordering
    tier: T2
  - key: detail_design_be
    tier: T3
```

### 7.3. Lint rule

> **PLANNED / NOT BUILT (CR-AIWS-2026-08-057):** đoạn dưới mô tả tooling chưa tồn tại (`lint_wiki.py` không có `--check-tiers` / không đọc `t1_exception_reason`) — design intent, không phải hành vi. Build → CR riêng gỡ banner.

`lint_wiki.py --check-tiers`:
- WARN khi meta thiếu T1 (unless `t1_exception_reason` present)
- WARN khi T1 candidate keyword matches known generic heading pattern

### 7.4. Lookup tool: discriminative scoring

**IMPLEMENTED (CR-AIWS-2026-07-001 Q3, 2026-07-04) — proxy subset, no per-key tier tags yet.**
Scoring is now a SINGLE implementation in `_common.py` (`score_lexical` / `score_semantic`), consumed by
both `lookup_wiki_source.py` and `smoke_test_wiki_lookup.py` (the former inline copies drifted — CAP-902-004).
#### Cơ chế thật — và nó KHÔNG phải per-token (CR-AIWS-2026-08-104 C1)

`score_lexical` (mode mặc định của `lookup_wiki_source.py`) so **NGUYÊN CỤM query** với từng bề mặt của
record. Nó **không** cộng điểm theo từng token trùng, trừ đúng một dòng: token đường dẫn. Đây là điều quyết
định cách viết key, và trước đây mục này không nói ra.

**Bảng trọng số** (đọc từ `_common.score_lexical` + `_common._authority_boost`; con số ở đây được test khoá
lại — xem `test_cr104_*`):

| Điều kiện | Điểm |
|---|---|
| `source_id` **bằng** query (sau fold dấu) | +100 |
| query là **substring** của `source_id` | +20 |
| query là **substring** của `title` | +15 |
| một `lookup_key` **trùng khít** query | +12 |
| một `lookup_key` là substring của query, **hoặc query là substring của key** | **+4 mỗi key** |
| **mỗi token** của query trùng một token của `artifact_locator` | +3 |
| query là substring của `summary_short` | +2 |
| `authority_level` ∈ {authoritative, curated_reference, source_of_truth} | **+6** |
| `knowledge_class` ∈ {source_of_truth, curated} | **+4** |

Hai boost cũ vẫn còn, nay đọc được bằng số ở trên: **compound-key** = dòng +12 (một key nhiều từ trùng khít
query thắng một token generic), **exact-name** = dòng +15/+20 (query gọi đúng tên doc).

**Ngưỡng đọc kết quả:** `lookup_wiki_source.py` in cảnh báo *"top score < 15 (fragile match)"*. Dưới 15 nghĩa
là "tìm thấy nhưng mong manh" — đừng coi là đã định tuyến xong.

#### Hệ quả khi curate key: key phải NGẮN và nằm gọn trong câu hỏi (C2)

Vì matching là nguyên-cụm, một key **mô tả đầy đủ** thường ăn **0 điểm** cho câu hỏi thật — không bên nào là
substring của bên kia. Đây là lý do cơ học của luật "key phải phân biệt" ở §2–§3; không có nó, người curate
chỉ đoán.

*Ca đo được (AIP-EXEC-1080):* meta của skill council mang key `gate G1 G12 G4b council`. Với câu hỏi
`council engine gate` nó ăn **0** điểm từ key, chỉ còn điểm token đường dẫn, và **thua chính file router**
của mình (11 điểm). Thêm hai key ngắn — `gate` và `council engine` — đưa lên **18** và vượt.

Cách tự kiểm trước khi lưu: đọc key của bạn và hỏi *"cụm này có nằm gọn trong câu hỏi người ta sẽ gõ không,
hoặc câu hỏi đó có nằm gọn trong cụm này không?"*. Nếu không cả hai chiều ⇒ key đó không ăn điểm.

**Key stale / sai nội dung: mặc định là SỬA CHỖ SAI, KHÔNG xoá key (CR-AIWS-2026-08-111).** Một key **sai
nội dung vẫn đang khớp substring** — tức nó **vẫn gánh điểm**. Xoá nó là **degrade**, và degrade đó **im
lặng**.

*Ca đo được (AIP-1087):* meta `SRC-DOC-CR-IR-REVIEW-CHECKLIST` mang 5 key chứa chuỗi `(draft v0.1)` sau khi
tài liệu đã được promote thành canonical. Truy vấn **đúng tiêu đề tài liệu**:

| Phương án | Điểm | Á quân |
|---|---|---|
| giữ nguyên | 42 | 20 |
| **XOÁ 5 key** | **22** | 20 |
| **SỬA (gỡ chuỗi sai)** | **50** | 20 |

Xoá làm mất **20 điểm** (5 key × `+4` substring) — đủ để tài liệu tụt xuống **ngang á quân trên chính tiêu
đề của nó**. Sửa thì **+8**, vì key trở thành **trùng khít** ⇒ `+12` thay cho `+4`.

**Chỉ xoá khi key thật sự VÔ NGHĨA** — không ai truy vấn bằng chuỗi đó. "Sai nội dung" **không** đồng nghĩa
"vô nghĩa".

Hai ca hẹp cùng họ đã có ở tài liệu này, giữ nguyên vì mỗi ca mang **số đo riêng**: key **generic** (mục
"Đăng ký theo BATCH" — xoá chỉ đẩy key generic kế tiếp vào vùng self-test soi) và **nhãn phiên bản/trạng
thái** (mục "Phiên bản và trạng thái" — vị trí nhãn quyết định thiệt hại).

**Đo thế nào cho đúng.** Mọi thao tác key phải đo bằng **truy vấn đúng tên tài liệu**, và **ghi kèm điểm á
quân** — thứ quyết định là **BIÊN**, không phải hạng. Và biết trước điều này: **`--self-test` KHÔNG bắt được
lớp lỗi này.** Ở ca trên nó cho **1380/1380 PASS ở CẢ BA phương án**, kể cả phương án degrade — vì nó chỉ
hỏi *"entry có tự tìm được chính nó bằng key của nó không"*, mà cả ba đều đạt.

#### Phiên bản và trạng thái: đặt ở đâu — và VỊ TRÍ của nhãn quyết định thiệt hại (CR-AIWS-2026-08-107)

Vì matching là **nguyên cụm**, một token chèn vào **giữa** tên sẽ **cắt đứt** chuỗi. Ba bậc, đo được:

```
AIP v0.3 Conformance Checklist      ->  KHÔNG KHỚP    0    nhãn ở GIỮA -> đứt chuỗi
AIP Conformance Checklist (v0.3)    ->  substring    +4    nhãn ở CUỐI -> tụt một bậc
AIP Conformance Checklist           ->  trùng khít  +12
```

*Ca đo được (CR-107):* `AIP v0.3 Conformance Checklist` chấm **18** cho truy vấn
`AIP Conformance Checklist`, trong khi **á quân 17** — thắng bằng một điểm. Gỡ `v0.3` khỏi 5 key của nó:
**46**, biên **+15**. Ở chiều ngược lại, `(draft v0.1)` đặt ở **cuối** chỉ làm mất **8** điểm
(exact +12 → substring +4) — nhẹ hơn hẳn, và thường là cố ý.

**Nhãn phiên bản THÊM một key, không SỬA key tên.** Ba tình huống:

| Tình huống | Đặt ở đâu |
|---|---|
| **Chỉ một bản đang sống** (đa số) | Key = **tên sạch**, không nhãn. Phiên bản nằm ở **tên file** + nội dung tài liệu — đủ để truy nguồn |
| **Bản cũ vẫn còn trong wiki** | Bản cũ đặt **`status: superseded`**. Đừng ghi chữ "superseded" vào key |
| **Nhiều bản cùng `active`, người dùng phải chọn đúng bản** | Mỗi bản có **key tên sạch** (đều đạt +12 khi gõ tên) **CỘNG một key riêng mang phiên bản** — `AIP Conformance Checklist v0.3` |

**Hai sự thật cơ học cần biết trước khi chọn chỗ đặt:**

1. **`version` trong frontmatter meta là VÔ HÌNH với lookup.** Index chỉ chiếu một tập field cố định
   (`artifact_locator · authority_level · knowledge_targets · lookup_keys · meta_locator ·
   original_source_locator · profile_id · promotion_status · representation_type · section_heading ·
   section_lines · source_id · source_type · status · summary_short · system · title` …) — **không có
   `version`**. Ghi vào đó thì tra cứu không thấy: không chấm điểm, không lọc được.
2. **`status: superseded` thì NGƯỢC LẠI — nó có tác dụng thật, và mạnh.** `lookup_wiki_source` nhân điểm
   với `SUPERSEDED_PENALTY` (**0.2**, tức **phạt ×5**: một entry 45 điểm còn **9.0**), in kèm nhãn
   `[SUPERSEDED]`, và `--include-inactive` trả lại nguyên điểm khi bạn **cố ý** muốn tìm bản cũ. Đây là
   cơ chế đúng để nói "bản này đã cũ" — không phải chữ trong key.

**Ngoại lệ cần phân biệt:** nếu từ `superseded`/`deprecated` xuất hiện trong key với tư cách **văn xuôi mô
tả nội dung tài liệu** (ví dụ một mục nói "Stage 1 (SUPERSEDED by Stage 2 retained as history)") thì đó
**không** phải nhãn trạng thái của tài liệu — gỡ nó đi sẽ bẻ gãy nghĩa. Ca như vậy dùng `lint_accept` kèm
lý do, đừng sửa key.

Enforced by lint WARN **`meta_lookup_key_marker_midname`** (chỉ bắt nhãn đứng **riêng** và có chữ ở **cả
hai phía**; nhãn ở cuối và nhãn nằm bên trong một token như `CHANGELOG_v0_5_0` **không** bị bắt).

#### Đăng ký theo BATCH: phải đo lại meta CŨ, không chỉ meta mới (C3)

Thêm một loạt meta cùng họ từ khoá làm **meta có sẵn tụt hạng**, và điều đó **im lặng**: lint xanh, index
xanh. Acceptance chỉ hỏi *"meta mới có top-1 không"* sẽ không thấy gì.

**Bắt buộc:** chạy `py .ai-work/tooling/smoke_test_wiki_lookup.py --self-test` **trước và sau** mỗi batch
đăng ký; số PASS **không được giảm**. Chạy kèm `--cases .ai-work/wiki_sources/lookup_test_cases.jsonl`.

*Ca đo được (AIP-EXEC-1080 → AIP-EXEC-1085):* self-test **1380/1380** trước batch → **1379/1380** sau khi
thêm 7 meta họ "review" (một entry có sẵn rớt khỏi top-5 cho chính key của nó) → **1380/1380** sau khi curate
lại key của entry đó.

> **Xoá key generic KHÔNG phải là sửa — thay bằng key phân biệt mới là.** Self-test chỉ soi **các key đầu**
> của mỗi entry, nên xoá một key generic chỉ **đẩy key generic kế tiếp vào vùng bị soi**. PoC trên bản sao
> index: thay `checklist` → `wiki rollout checklist` cho **1380/1380 PASS**; còn **bỏ hẳn** `checklist` vẫn
> **1379/1380 FAIL**, ca đỏ chỉ chuyển sang key `done`.

#### `authority_level` là nút chỉnh XẾP HẠNG, không phải nhãn phân loại (C4)

`authority_level` cộng **+6** và `knowledge_class` cộng **+4** — trên dải điểm thật của truy vấn thường
(13–20) thì đủ **lật thứ hạng**. Điền hai field này là một quyết định về xếp hạng, không phải gắn nhãn cho
đẹp hồ sơ. *Đo được:* đặt `authority_level: curated_reference` cho 7 meta làm điểm nghiệm thu nhảy đồng loạt
(`source trace rule` 56 → 62; `finding format Fact Inference invariant` 18 → 24).

**FUTURE (not in this CR):** full per-key `tier:` tags in `lookup_keys` with the T1×3.0 / T2×1.5 / T3×1.0
multipliers + a T1-exact stop condition (original §7.2 design) — this changes the index projection schema, so it
is deferred; the compound-proxy above delivers most of the value without a schema change.

---

## 8. Relationship to Other Specs

- **[WIKI_META_INDEX_SPEC]** — `lookup_keys` field là nơi tier tags được embed
- **[Knowledge_Routing_Spec_MVP]** — Routing logic dùng tier scoring trong §4 (Discovery inputs)
- **[Artifact_Type_Taxonomy_Spec_MVP]** — `classification_signals.path_tokens` trong taxonomy đóng vai trò T2 hint candidates

---

## 9. Open Questions

- **OP-Q1:** N threshold = 10 có phù hợp với project lớn (1000+ artifacts) không? Cần calibrate per-project.
- **OP-Q2:** Khi meta đã built không có tier tags — có nên retroactively tag khi build index không? Tentative: yes (via rebuild index with --retag-tiers flag).

---

*Created: 2026-05-25 under AIP-EXEC-014 STEP-02. Source: CR-D2, AIWS-Wiki-CR-Proposal-2026-05-25.md §3.*
