# aiws-wiki — operation: test-lookup

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose

Verify wiki lookup quality after building or updating index/meta. Answers the question:
"After I created these metas, will AI actually find the right sources?"

There are 3 modes depending on what the user wants to verify:

| Mode | Khi nào dùng | Cơ chế |
|---|---|---|
| A — self-test | Sau khi build/update index, kiểm tra nhanh toàn bộ | Script tự động: mỗi entry tự tìm được mình |
| B — structured cases | Có danh sách query cụ thể cần test | Script: chạy từng case JSONL, báo PASS/FAIL |
| C — natural language | Muốn thấy AI sẽ tìm ra gì khi làm một tác vụ cụ thể | AI: phân tích task → sinh queries → chạy lookup → tổng hợp |

---

## Mode A — Self-Test (automated)

Chạy khi user nói "self-test", "kiểm tra tất cả", "test toàn bộ index", hoặc không chỉ định mode cụ thể.

### Lệnh

```bash
# Basic self-test
python .ai-work/tooling/smoke_test_wiki_lookup.py --self-test

# Với chi tiết đầy đủ (hiện cả PASS)
python .ai-work/tooling/smoke_test_wiki_lookup.py --self-test --verbose

# Top-N kết quả phải có entry (default: 5)
python .ai-work/tooling/smoke_test_wiki_lookup.py --self-test --top-n 3

# Giới hạn số lookup_keys test per entry (default: 3)
python .ai-work/tooling/smoke_test_wiki_lookup.py --self-test --key-limit 5
```

### Cách hoạt động

Với mỗi entry trong `index.jsonl`:
1. **Test source_id** (id mode): entry phải xuất hiện ở rank 1
2. **Test lookup_keys** (semantic mode, tối đa `--key-limit` keys): entry phải có trong top-N

### Output mẫu

```
[PASS] SRC-DD-F01-001  (self:id)  — query='SRC-DD-F01-001'  mode=id  rank 1  score 100
[PASS] SRC-DD-F01-001  (self:key='F01 detail design')  — query='F01 detail design'  mode=semantic  rank 2  score 34
[FAIL] SRC-BD-MODULE-002  (self:key='module tổng quan')  — query='module tổng quan'  mode=semantic  not found in top-5
       hint: lookup_key 'module tổng quan' did not surface this entry in top-5. Top results: ['SRC-BD-MODULE-001', ...].
             Consider making lookup_key more specific or adding T1-tier tags.

Summary: 18/20 PASS  2 FAIL  [FAIL]
```

### Đọc kết quả

- **FAIL source_id**: source_id có thể bị duplicate hoặc không match index — check lại `build_wiki_source_index.py`
- **FAIL lookup_key**: key quá chung chung hoặc thiếu từ khóa đặc trưng → cải thiện lookup_keys trong meta, rebuild index
- **Score thấp (< 10) dù PASS**: entry được tìm thấy nhưng "mong manh" → cân nhắc cải thiện lookup_keys

---

## Mode B — Structured Cases

Chạy khi user cung cấp file test cases hoặc nói "test theo danh sách", "chạy test cases".

### Format file test cases

Tạo file JSONL (mỗi dòng 1 JSON object), đặt tại bất kỳ đường dẫn nào:

```jsonl
{"query": "màn hình đăng nhập", "mode": "semantic", "expected_source_id": "SRC-DD-F01-LOGIN", "top_n": 5, "label": "login screen basic query"}
{"query": "SRC-DD-F01-LOGIN", "mode": "id", "expected_source_id": "SRC-DD-F01-LOGIN", "top_n": 1, "label": "id lookup"}
{"query": "F01 detail design frontend", "mode": "semantic", "expected_source_id": "SRC-DD-F01-FE", "top_n": 3}
{"query": "order entry business logic", "mode": "lexical", "expected_source_id": "SRC-BD-ORDER", "top_n": 5}
```

**Fields:**
- `query` — chuỗi tìm kiếm (required)
- `expected_source_id` — source_id phải có trong top kết quả (required **trừ khi** có `forbid`)
- `mode` — `lexical` | `semantic` | `id` | `path` (default: `semantic`)
- `top_n` — kiểm tra trong bao nhiêu kết quả đầu (default: 5)
- `label` — nhãn mô tả, xuất hiện trong report (optional)
- `system` — (optional, CR-AIWS-2026-06-058 / multi-system CR-017) scope query về 1 system: chỉ giữ doc của system đó **+ common** (doc không có `system`). Dùng `lookup_wiki_source._in_system` (cùng filter với production, không re-implement). Absent → không scope.
- `forbid` — (optional, CR-058) list source_id **PHẢI VẮNG MẶT ở mọi rank** dưới scope (same-name / cross-system no-bleed assertion). Case chỉ có `forbid` (không `expected_source_id`) hợp lệ.

### Lệnh

```bash
python .ai-work/tooling/smoke_test_wiki_lookup.py --cases .ai-work/wiki_sources/lookup_test_cases.jsonl

# JSON output (cho programmatic use)
python .ai-work/tooling/smoke_test_wiki_lookup.py --cases lookup_test_cases.jsonl --format json
```

### Gợi ý đặt file

Convention: `.ai-work/wiki_sources/lookup_test_cases.jsonl`

---

## Mode C — Natural Language Task Description

**Quan trọng nhất:** User mô tả một tác vụ bằng ngôn ngữ tự nhiên, AI phân tích và chạy lookup
để cho thấy wiki sẽ tìm được gì khi AI thực sự làm tác vụ đó.

Trigger phrases:
- "hãy test wiki lookup cho tác vụ review detail design của chức năng F01"
- "test xem wiki tìm được gì khi làm [task]"
- "lookup sẽ ra gì nếu tôi yêu cầu AI [task]"
- "simulate lookup for [task description]"

### Flow AI phải thực hiện

**Bước 1 — Parse task description**

Từ input của user, extract:
- **Function/feature identifiers**: mã chức năng (F01, CB01001, ...), tên chức năng (đăng nhập, order entry, ...)
- **Document types**: loại tài liệu cần (detail design, basic design, DB design, API spec, screen spec, ...)
- **Task lens**: mục tiêu của tác vụ (review, implement, debug, estimate, ...)
- **Language variants**: tên có thể xuất hiện bằng VI/EN/JA

Ví dụ — "review detail design của chức năng F01":
- Identifiers: `F01`
- Doc types: `detail design`, `DD`, `thiết kế chi tiết`
- Task lens: `review`
- Cần tìm: tất cả tài liệu design liên quan đến F01

**Bước 2 — Lập query plan (3–5 queries)**

Sinh query plan đa góc độ để bao phủ các cách AI thực tế có thể tìm kiếm:

```
Query plan cho "review detail design của chức năng F01":
  Q1: "F01"                        mode=semantic  (identifier trực tiếp)
  Q2: "F01 detail design"          mode=semantic  (identifier + doc type)
  Q3: "F01 thiết kế chi tiết"      mode=semantic  (VN variant)
  Q4: "SRC-DD-F01"                 mode=lexical   (source_id prefix pattern nếu biết convention)
  Q5: "F01 screen spec"            mode=semantic  (alternative doc type)
```

**Bước 3 — Chạy từng query**

Với mỗi query trong plan, chạy:
```bash
python .ai-work/tooling/lookup_wiki_source.py --query "<query>" --mode <mode> --limit 20 --format json
```

Thu thập kết quả: source_id, title, score, artifact_locator của top results.

**Bước 4 — Tổng hợp và report**

Trình bày kết quả theo format:

```
=== Wiki Lookup Test: "review detail design của chức năng F01" ===

Queries chạy: 5  |  Queries có kết quả: 4  |  Unique sources found: 3

KẾT QUẢ:
  ✓ Q1 "F01" (semantic)         → SRC-DD-F01-FE (score 42), SRC-DD-F01-BE (score 38), SRC-BD-F01 (score 25)
  ✓ Q2 "F01 detail design"      → SRC-DD-F01-FE (score 51), SRC-DD-F01-BE (score 45)
  ✓ Q3 "F01 thiết kế chi tiết"  → SRC-DD-F01-FE (score 28)
  ✗ Q4 "SRC-DD-F01" (lexical)   → no match (source_id prefix không khớp convention)
  ✓ Q5 "F01 screen spec"        → SRC-DD-F01-FE (score 19)

SOURCES SẼ ĐƯỢC TÌM RA:
  [HIGH]  SRC-DD-F01-FE   — Detail Design Frontend F01      (3/5 queries, max score 51)
  [HIGH]  SRC-DD-F01-BE   — Detail Design Backend F01       (2/5 queries, max score 45)
  [MED]   SRC-BD-F01      — Basic Design F01                (1/5 queries, max score 25)

GAPS / CẦN CHÚ Ý:
  - SRC-DD-F01-DB (DB Design F01) không xuất hiện trong bất kỳ query nào
    → Có thể lookup_keys của source này thiếu "F01" hoặc "DB design" → kiểm tra meta
  - Score của Q5 thấp (19) → lookup_key "screen spec" chưa có trong meta của SRC-DD-F01-FE
    → Cân nhắc thêm lookup_key này nếu user thường dùng "screen spec"

KẾT LUẬN:
  Wiki lookup sẽ tìm ra 3/4 sources liên quan. 1 source (DB Design) cần cải thiện lookup_keys.
  Tác vụ review detail design F01 sẽ được phục vụ tốt với current index.
```

**Quy tắc bắt buộc cho Mode C:**
- PHẢI chạy tool thực tế (`lookup_wiki_source.py`) — không suy luận kết quả
- Mỗi query phải chạy riêng, thu thập JSON output
- Gap detection: source quan trọng không tìm thấy = signal cần cải thiện lookup_keys
- Score thấp (< 15 với semantic) = "found nhưng fragile" → ghi chú

---

## Object-node check (Mode A/C)

For a `node_kind=object` node, verify BOTH:
- **Discoverable** — found via lookup by its `source_id` (id mode, rank 1) AND ≥1 `## Lookup Keys` entry (semantic, top-N) — same checks as an artifact node.
- **Relation-resolvable** — its relations resolve via `python .ai-work/tooling/wiki_relations.py --relations <object-id>` as BOTH an out-edge source AND an IN-edge endpoint (the INV-5 named-consumer pattern). An object is only useful if findable AND navigable.

---

## Rules

- Sau khi test và phát hiện FAIL/GAP: đề xuất cụ thể cải thiện lookup_keys trong meta → user quyết định có update không
- Không tự sửa meta hay index sau khi test — chỉ report và suggest
- Mode A/B: kết quả chỉ phản ánh current index state — phải `build_wiki_source_index.py` sau khi sửa meta trước khi re-test
- Mode C NL: nếu không tìm thấy bất kỳ source nào → có thể index chưa có sources liên quan, báo rõ
