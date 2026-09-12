# Tooling Authoring Conventions (AIWS)

> Canonical procedural doc — created by **CR-AIWS-2026-07-045** (trả nợ follow-up mà chính
> `CR-AIWS-2026-07-024` §11 khai là "still open"). Áp cho **mọi** tool trong `.ai-work/tooling/`
> (dual-tree `product/tooling/`). Mỗi rule dưới đây tồn tại vì **đã có ít nhất một lần trả giá**.

**Mức ràng buộc:** BINDING cho tool mới và cho mọi thay đổi chạm vùng liên quan của tool cũ.
Lệch rule → phải nêu lý do trong CR (§6) hoặc trong Apply Outcome.

---

## Rule 1 — Persist path CHỈ qua `portable_locator` / `resolve_locator`

Không bao giờ ghi **absolute path** vào artifact (AIP, workspace file, meta, index, registry).
Dùng helper sẵn có trong `_common.py`:

```python
from _common import portable_locator, resolve_locator
loc = portable_locator(path, project_root)     # ghi:  __PROJECT_ROOT__/.ai-work/...
p   = resolve_locator(loc, project_root)       # đọc:  Path tuyệt đối
```

- **Tại sao:** artifact có absolute path không portable giữa máy/OS/clone; project cài AIWS ở đường
  dẫn khác sẽ vỡ.
- **Đã trả giá:** `CR-AIWS-2026-07-022` — AIP-path fields ghi absolute path, phải sửa hồi tố toàn bộ;
  helper **đã tồn tại từ trước** mà tool không dùng.

## Rule 2 — KHÔNG re-implement index/scope resolution

Index selection, scope parsing, authorization gating (`--scope`, `--system`, `--authorized`) đã có
trong `_common.py` (`parse_scope`, `resolve_index_paths`, `scope_needs_authorization`,
`index_inventory`) và trong `lookup_wiki_source.py`. **Import chúng.** Nếu helper thiếu tính năng →
**mở rộng helper**, đừng copy logic.

- **Tại sao:** logic bị nhân bản sẽ drift; một CR sửa bản này, bản kia âm thầm sai (multi-index,
  authorization gate là chỗ sai nguy hiểm).
- **Đã trả giá:** `CR-AIWS-2026-07-024` — `build_wiki_page_base.load_index()` tự viết lại việc chọn
  index → mù với `index.aiws.jsonl`; phải sửa cả 3 subparser.

## Rule 3 — Tool resolve root từ `__file__` là KHÔNG cwd-sandboxable

Mọi tool phải nhận `--project-root` (default = `find_ai_work_root(Path.cwd())` hoặc walk-up từ
`__file__`). Test/fixture phải trỏ được tool vào sandbox.

```python
p.add_argument("--project-root", default="", help="project root (default: walk up)")
root = Path(ns.project_root).resolve() if ns.project_root else find_ai_work_root(Path.cwd())
```

- **Tại sao:** không có flag thì test phải hack `sys.path`/cwd, hoặc không test được; tool cũng không
  chạy được trên project khác.
- **Đã trả giá:** `route_build_tool.py` (fix ở CR-045 T2) — 6 tool anh em có flag, nó thì không.

## Rule 4 — Acceptance: multi-index

Tool **đọc wiki index** trong project multi-system phải có **≥1 test case mà corpus nằm ở index KHÁC
`index.jsonl`** (vd `index.aiws.jsonl`). Dogfood phải chạy trên **≥2 system có index shape khác nhau**.

- **Tại sao:** một corpus nằm trọn trong `index.jsonl` không thể lộ lỗi multi-index.
- **Đã trả giá:** `CR-AIWS-2026-07-023` — dogfood chạy trên system `demo` (38 sources đều trong
  `index.jsonl`) → lỗ multi-index **về mặt cấu trúc không thể xuất hiện**; test cũng chỉ đụng 2 lint
  rule, không gọi `load_index()`. Lỗi chỉ lộ ở CR-024.

## Rule 5 — Acceptance: dogfood-first cho builder/chunker

Mọi thay đổi **builder / chunker** phải **dogfood trên doc THẬT** có ít nhất: **code fence** và
**heading trùng hoặc bị đổi tên**, trước khi coi là done. Paper review không đủ.

- **Đã trả giá:** `CR-AIWS-2026-07-006` — paper review PASS, dogfood trên doc thật bắt 2 defect:
  (a) section hash gồm cả heading → đổi heading là mất carry-over summary; (b) scan `## ` không
  fence-aware → `WIKI_META_INDEX_SPEC` bị chẻ thành 9 child rác.

## Rule 6 — Namespace: KHÔNG tự chọn meta root / index path

Tool **đọc metas** → `_common.meta_roots(ai_work)`. Tool **resolve id/endpoint** → `_common.all_index_paths(wiki_sources)`.
**Search/lookup có scope** → vẫn đi qua `parse_scope` + `resolve_index_paths` (giữ authorization gate rule #11/#13 — `all_index_paths` cố ý **loại** `index.local.jsonl`).

```python
from _common import meta_roots, all_index_paths
for root in meta_roots(ai_work):        # project meta/ + shipped aiws_meta/
    for f in root.rglob("*.md"): ...
known = {r["source_id"] for idx in all_index_paths(ws) for r in read_jsonl(idx)}
```

- **Tại sao:** viết tay `ai_work / "wiki_sources" / "meta"` là cách **CÙNG MỘT defect ship 7 LẦN**, mỗi lần âm thầm bỏ qua toàn bộ meta AIWS:

  | # | Tool | Triệu chứng |
  |---|---|---|
  | 1 | `lint_wiki` meta-scan | 188 meta chưa từng được lint (32 summary rỗng + 27 section_lines drift vô hình) |
  | 2 | `build_relations` | 75 edge vừa author **không bao giờ** vào `relations.jsonl` |
  | 3 | `_lint_relations` | 117 `relations_broken_ref` **giả** |
  | 4 | `wiki_relations._load_index` | `[BROKEN REF]` cho mọi endpoint AIWS |
  | 5 | `detect_changed_wiki_sources` | sửa **150 meta** → detector báo **0** thay đổi |
| 6 | `evaluate_wiki_source_impact` | mù 187 source AIWS (`ERROR not in index`) — **và** đọc `index.local.jsonl` không gate (rò authorization) |
| 7 | `wiki_meta --view` | `not found in index` cho mọi id AIWS |

  *(CR-041 · CR-048 · CR-049 · CR-051 — lần 6/7: `evaluate_wiki_source_impact` + `wiki_meta --view`, phát hiện bởi chính self-check của CR-049)*

- **ENFORCED:** `.ai-work/tests/test_meta_namespace_conformance.py` (CR-051 T4). Thêm tool đọc meta/index mà không qua helper ⇒ **battery đỏ**. Allowlist chỉ chấp nhận **writer** (chọn thư mục ĐÍCH) và owner của authorization gate — mỗi entry **bắt buộc có lý do**.

## Rule 7 — Sửa file tại chỗ: đọc TOÀN BỘ → tính nội dung mới → assert khác rỗng → RỒI MỚI mở để ghi

```python
# ❌ SAI — Python đánh giá io.open(f,"w") TRƯỚC (truncate!), read_text đọc phải file đã rỗng
io.open(f, "w").write(transform(read_text(f)))

# ✅ ĐÚNG
new = transform(read_text(f))
assert new.strip(), f"refusing to write empty {f}"
io.open(f, "w", encoding="utf-8", newline="\n").write(new)
```

- **Đã trả giá:** apply CR-048 — **5 meta bị xoá trắng**; may mà lint (`meta_missing`) bắt được và `git checkout` khôi phục được.

## Rule 8 — Lint rule mới (hoặc scan mở rộng làm rule cũ hiện thêm) PHẢI có một dòng release-note

CR nào thêm một `report.error/warn(<code>, …)` **mới**, hoặc mở rộng phạm vi quét khiến một rule cũ bắn
thêm đáng kể, **bắt buộc** thêm vào `product/UPGRADE_IMPACT_NOTE_next_release.md`: **tên code · WARN/ERROR ·
một câu operator hiểu tại sao · cách xử lý**. Nếu là scan-widening: nêu **ước lượng +N** warning.

- **Tại sao:** một tool sắc hơn mà không kèm giải thích thì operator đọc thành "dự án tôi tệ đi".
- **Đã trả giá:** `curated_citation_stale` (round-3 R3-06) ship không doc → vá một lần, không thành rule →
  **tái phát R4-02** (`meta_summary_degenerate` ×10 + bạn bè, hiện ra do scan-widening CR-041). Rule 8 là
  fix bền cho lớp đó thay vì vá lần thứ ba.

## Rule 9 — Path đến từ DATA: normalize → classify → build → `is_file()`

Giá trị dùng làm path mà đến từ **dữ liệu** (frontmatter meta, record `index*.jsonl`,
`_build_routing.json`, `.current_step.json`, snapshot/config JSON) **KHÔNG BAO GIỜ** được đưa thẳng vào
`Path()` / `resolve_locator()`, và **`.exists()` KHÔNG phải guard hợp lệ trước khi ĐỌC**.

```python
from _common import locator_str, resolve_data_file
loc = locator_str(rec.get("meta_locator"))     # []/None/blank -> "" (= absent)
if not loc: ...                                 # classify: skip / diagnostic / missing[]
p = resolve_data_file(loc, project_root)        # None nếu không resolve ra FILE đọc được
if p is None: ...                               # per-item degrade — KHÔNG để crash giết cả run
```

- **Tại sao:** `Path("")` == `Path(".")` — thư mục đang tồn tại → `.exists()` luôn True; bare YAML key
  parse ra `[]`, `null` ra `None` → `Path()` ném TypeError; `resolve_locator` gọi `s.startswith` không
  type-check. Helper là **một nguồn chân lý** cho cả 3 cái bẫy đó.
- **Đã trả giá:** `CR-AIWS-2026-07-063` — detector chết cả run vì meta 0-byte ở project downstream
  (**2 leg trong CÙNG một tool**: leg thứ hai chính bản báo cáo gốc bỏ sót). Audit sau đó
  (`CR-AIWS-2026-07-064`) tìm thêm **17 site** cùng class, trong đó: **5 site trong `lint_wiki`** (một
  meta hỏng giết chính CR gate), `check_aiws_upgrade --verify` (chết và **vứt sạch CRITICAL đã thu
  thập**), `build_wiki_source_index` (một entry `meta_dirs` rỗng → **quét cả working tree vào
  `index.local.jsonl`**, âm thầm, không diagnostic).
- **Hệ quả bắt buộc:** một item dữ liệu hỏng chỉ được làm hỏng **item đó** (diagnostic per-item),
  không bao giờ được abort cả run. `lint_wiki` là mẫu ĐÚNG (report rồi chạy tiếp); detector trước
  CR-063 là mẫu SAI.
- **Ranh giới:** helper KHÔNG thay `resolve_locator`/`portable_locator` (vẫn là primitive, semantics
  resolve giữ nguyên) và KHÔNG đụng scope/authorization (Rule 2/6). Path trỏ **thư mục** có chủ đích
  (vd `meta_dirs`) → dùng `locator_str()` + `is_dir()`, không dùng `resolve_data_file`.

## Rule 10 — Byte-compare / hash cross-source: normalize eol TRƯỚC khi so (CR-AIWS-2026-08-005)

Mọi phép so sánh mức byte giữa nội dung đến từ **hai nguồn khác nhau** (hai repo, package ↔ working
tree, bản gốc ↔ bản sao, release notes giữa hai bản) phải **normalize line endings (`\r\n` → `\n`)
trước khi so/hash** — TRỪ khi mục đích của phép kiểm là chính eol. Phép kiểm hash phải **hash chính
vật đang kiểm** và in **cả hai giá trị cạnh nhau**; cấm chép giá trị nguồn sang ô của bản sao.

- **Tại sao:** repo không pin eol (trước CR-2026-08-005 không có `.gitattributes`) — mỗi máy/tool tự
  quyết; một byte `\r` làm hash lệch và diff "nhìn giống hệt nhau". Cổng so sánh báo động giả hàng
  loạt là cổng bị tắt.
- **Đã trả giá (reported + in-repo):** demo deployment 2026-08 — bản phòng hộ gold set "tự vô hiệu"
  vì hash lệch CRLF, và 8/10 phép đối chiếu status báo LỆCH giả (IR-2026-08-05 G8/CAP-083-02); in-repo:
  fold UPGRADE_NOTES giữa release từng phải diff tay (build v1.1.4).
- **Ranh giới:** dual-tree `diff -q` trong CÙNG working tree (2 cây do cùng tool ghi) không bắt buộc
  normalize — nhưng nếu lệch chỉ vì eol thì đó là bug của writer, sửa writer chứ không nới gate.

## Rule 11 — Writer không được đổi eol của file (CR-AIWS-2026-08-016)

Python ghi file text trong repo: `write_text(..., newline='\n')` / `open(..., 'w', newline='\n')`
khi file (hoặc HEAD của nó) là LF — `newline=None` mặc định trên Windows CRLF-hoá **TOÀN file** dù
chỉ sửa một dòng, và dưới `* -text` (CR-AIWS-2026-08-005) churn đó commit nguyên vẹn. File vốn CRLF
(vd `change_requests/**`) → giữ CRLF.

- **Tại sao:** Rule 10 sửa phép ĐO (normalize trước khi so); Rule 11 sửa phép GHI — không có nó thì
  mọi editor/writer Windows âm thầm biến diff nội-dung-vài-dòng thành full-file diff, chôn nội dung
  thật của thay đổi.
- **Đã trả giá (in-repo):** wave 2026-08 — **108/236** file text tracked-modified bị flip LF→CRLF
  toàn file (đo 2026-08-07); diff toàn wave phình 18.968+/21.700− dòng, sau repair per-file về HEAD
  eol còn 1.221+/3.953− (CR-AIWS-2026-08-016).
- **Sau MỌI edit canonical** (kể cả qua editor tool): check `git diff --stat` — số dòng phình bất
  thường so với chủ đích ⇒ nghi eol flip, khôi phục eol theo HEAD **trước khi** mirror/cp.

## Rule 12 — Thứ tự của `sorted()` trên `Path` phụ thuộc OS (CR-AIWS-2026-08-024)

Khi kết quả sort được dùng để **chọn một phần tử đại diện** — anchor của finding, phần tử `[0]` sau
sort, khoá để matching — **không** được dựa vào thứ tự mặc định của `sorted(list[Path])`. Sort bằng
**key tường minh**: `key=lambda p: p.relative_to(root).as_posix()`.

- **Tại sao:** `pathlib` so sánh qua `_str_normcase` — Windows hạ toàn chuỗi về viết thường, POSIX
  phân biệt hoa/thường. Với member nằm **khác thư mục**, hai OS cho **thứ tự khác nhau**. Rule nào
  chọn `paths[0]` làm anchor thì anchor lật theo OS, và `lint_accept` match theo **path chính xác**
  nên một accept đặt đúng trên máy dev (Windows) sẽ **trượt** trên CI Linux — không sinh cảnh báo nào.
- **Đã trả giá (in-repo):** lớp lỗi này xuất hiện **hai lần ở hai hàm khác nhau trong cùng một ngày**
  (2026-08-07): `_check_duplicate_cr_ids` (CR-AIWS-2026-07-071) và `_check_duplicate_artifact_ids`
  (CR-AIWS-2026-08-021 T3). Fixture chứng minh — `acct/exec/archived/AIP-EXEC-001-alpha.md` vs
  `acct/exec/Zed-AIP-EXEC-001.md`: viết thường chọn `archived/…` (`a` < `z`), phân biệt hoa/thường
  chọn `Zed-…` (`Z`=90 < `a`=97). Exposure lúc đó = 0 nhưng **reachable**.
- **Ranh giới:** `sorted()` an toàn khi (a) mọi member **cùng một thư mục**, hoặc (b) thứ tự chỉ để
  **hiển thị**. Đây không phải lệnh cấm `sorted()` — là yêu cầu **key tường minh khi thứ tự có hệ
  quả**. Và vì dev chỉ chạy Windows, invariant này phải được **test ghim** — xem Rule 13.

## Rule 13 — Test phải phân biệt được; invariant tinh tế phải có probe âm bản (CR-AIWS-2026-08-024)

Mọi assert phải trả lời được: ***"nếu implement SAI thì dòng này có ĐỎ không?"***. Với test bảo vệ một
invariant tinh tế — **anchor · thứ tự · encoding · eol · hành vi phụ thuộc platform** — **bắt buộc**
kèm **probe âm bản**: tạm phá implement → test phải **đỏ** → khôi phục → **xanh**. Ghi kết quả probe
vào nơi kiểm được (Apply Outcome / findings).

- **Tại sao:** một test **luôn xanh tệ hơn không có test** — nó vừa tạo cảm giác an toàn giả, vừa
  được đếm vào "N/N PASS", nên làm **báo cáo gate nói dối**. Bảy hình dạng đã gặp thật:
  - **assert tautology** — `check(<điều kiện> or True, …)`.
  - **fixture không phân biệt được** — xanh bất kể implement đúng hay sai.
  - **thông điệp sai sự thật kèm exit 0** — in "every tracked file matches its blob" trong khi còn
    file khác nội dung.
  - **tập duyệt RỖNG** — lặp qua một tập rồi assert "không vi phạm"; tập rỗng ⇒ 0 vi phạm ⇒ PASS.
    Test vẫn *chạy*, vẫn *xanh*, và cái nó canh thì nó không nhìn thấy. ⇒ **mọi test duyệt một tập
    file/module phải assert tập đó KHÔNG rỗng** — rẻ một dòng.
  - **fixture quá sạch để defect kích hoạt** — fixture *hợp lệ* nhưng thiếu điều kiện tiên quyết làm
    lỗi nổ; gate chỉ chứng minh "chạy được", không chứng minh "bắt được".
  - **vắng mặt không vi phạm schema** — với **lint**, không phải test: field optional biến mất không
    sinh lỗi nào ⇒ "lint sạch" **không** là bằng chứng "không mất dữ liệu"; phải đo bằng **tín hiệu
    dương** (một dòng đếm những gì đã giữ lại).
  - **điều kiện pre-release viết bằng văn xuôi** — một câu "phải làm X trước khi release" trong tài
    liệu không chặn được gì; chỉ một check trong build/release script mới chặn.
  - **probe không THẬT SỰ phá** (CR-AIWS-2026-08-109) — mutation *landing* nhưng chỉ đổi **văn bản**:
    chèn comment, đổi tên biến không dùng, thêm dòng chết. Test xanh là **đúng**, nhưng người chạy đọc
    thành *"bất biến này không được test bảo vệ"* rồi đi sửa thứ không hỏng. Đã trả giá 2026-08-19
    (AIP-1086): probe "đảo thứ tự hai vòng lặp" chỉ chèn một comment ⇒ kết luận sai; viết lại cho đảo
    thật ⇒ ĐỎ ngay.
  - **harness ĐỌC kết quả sai** (CR-AIWS-2026-08-109) — không phải test sai, không phải mutation sai,
    mà **công cụ phân loại kết quả** sai. Tầng này dễ bỏ qua nhất **vì nó là thứ đang được dùng để nghi
    ngờ mọi thứ khác**. Đã trả giá 2026-08-19 (AIP-1087): bộ lọc `"(f" in line` khớp nhầm
    `"(format verdict)"` ⇒ một probe **không** làm ca nào đỏ vẫn được đếm là "có hiệu lực", suýt vào
    Apply Outcome thành *"3/3 probe có hiệu lực"*. **Dấu hiệu:** bộ lọc dùng **substring trên văn bản
    người-đọc** (nhãn ca, tiêu đề, prose) thì sẽ khớp nhầm — dùng regex **có neo**, hoặc để test in mã
    ca ở dạng máy đọc được. **Luật rẻ: harness phải IN RA thứ nó đếm, không chỉ in số đếm.**
- **Đã trả giá (in-repo):** 2026-08-07 — assert `or True` lọt vào bản nháp, chỉ bắt được nhờ đọc lại;
  ngược lại probe âm bản chạy **2 lần** (case D8 của `test_duplicate_cr_id`, case P3a của
  `test_cr021_wave`) và **cả hai** chứng minh test thật sự phân biệt được. 2026-08-12 (apply
  CR-AIWS-2026-08-026) — `test_standalone.py` PASS trên **0/14** module vì neo đường dẫn trỏ vào thư
  mục không tồn tại, trong một bộ **421 test toàn xanh**; xoá-rồi-rebuild mất **6857 field + 49
  section** với **0 lint error**; một điều kiện pre-release viết bằng văn xuôi bị bỏ qua và release
  mang đúng defect mà câu đó gọi tên.
### Đọc kết quả probe (CR-AIWS-2026-08-109)

Có probe là một chuyện; **đọc đúng kết quả của nó** là chuyện khác. Ba lần trong hai ngày một probe
**XANH** bị đọc sai theo **ba nguyên nhân khác nhau**, và cả ba kết luận sai đều **mang hình dạng của sự
cẩn thận** — chúng trông như sản phẩm của việc kiểm tra kỹ.

**Probe trả XANH ⇒ hỏi đủ BA câu, theo thứ tự, trước khi kết luận "test yếu":**

1. **Mutation có LANDING không?** Đọc lại file sau khi phá (`diff`/`grep`), đừng tin `str.replace` đã
   đổi đúng thứ mình nghĩ. Anchor khớp nhưng thay bằng thứ khác là ca hay gặp nhất; `str.replace` không
   khớp thì **im lặng không làm gì**.
2. **Mutation có đổi HÀNH VI không, hay chỉ đổi VĂN BẢN?** Chèn comment, đổi tên biến không dùng, thêm
   dòng chết — đều không đổi hành vi, nên test xanh là **đúng**.
3. **Ca đang gác thứ này đã ĐỦ DỮ KIỆN để có nghĩa chưa?** Một ca **tích hợp** có thể chỉ có nghĩa sau
   khi một thay đổi khác đã land. Với thay đổi nhiều khối phụ thuộc thứ tự, probe phải chạy lại ở
   **trạng thái cuối**; chạy giữa chừng thì kết quả là **tạm**, phải ghi rõ như vậy.

Chỉ khi cả ba đều đạt mà test vẫn xanh thì mới kết luận test yếu.

**Và một lớp bảo vệ có thể cần N SỬA ĐỒNG THỜI mới phá được.** Ca đo được (CR-AIWS-2026-08-107): một ca
được giữ bởi **ba thứ độc lập** — neo `^`, neo `$`, và `.match`; gỡ **một hoặc hai** đều không đổi hành
vi, gỡ **cả ba** mới hỏng. Probe một-sửa trả XANH ở đó là **bằng chứng về độ chắc của thiết kế**, không
phải dấu hiệu test yếu. Cách chốt: dựng bản sao hàm với **toàn bộ** lớp bảo vệ bị gỡ và chứng minh nó
hỏng — kết luận **đo được**, thay cho suy đoán.

- **Ranh giới:** probe âm bản **bắt buộc** cho invariant tinh tế; với logic thẳng (parse, format,
  tính toán rõ ràng) thì **khuyến nghị** — bắt buộc toàn bộ sẽ bị bỏ qua như mọi rule quá rộng.

---

## Rule 14 — Dời literal cấu hình: COMMENT MANG RATIONALE phải đi cùng DỮ LIỆU (CR-AIWS-2026-08-109)

Khi refactor **dời một literal cấu hình** sang chỗ khác (gom về `_common`, tách module, đổi nguồn sự
thật), **comment mang RATIONALE phải đi cùng dữ liệu** — và CR phải khai comment đó **là một phần của
target**, không phải *"chỉ là comment"*.

- **Rationale ở đây nghĩa hẹp:** comment nêu **điều kiện để thay đổi giá trị**, **lý do nó được chọn**,
  hoặc **quyết định quản trị** gắn với nó. Không phải mọi comment — chú thích kiểu/định dạng/ví dụ thì
  không thuộc rule này.
- **Tại sao:** thao tác dời là **cơ học**, và cái cơ học chỉ mang theo **giá trị**. Cái *vì sao* nằm ở
  văn xuôi cạnh đó, không có gì buộc nó đi theo — nên nó rơi lại phía sau **mà không lệnh nào đỏ**.
- **Đã trả giá (in-repo):** các `frozenset({...})` exclusion trong `PAYLOAD_SECTIONS` mang comment nêu
  **điều kiện gỡ exclusion** (noise floor → control set → mẫu số tường minh → pre-registration; và
  *"gỡ là một CR RIÊNG, không phải một lần sửa lặng lẽ"*). CR-AIWS-2026-08-102 C2 dời dữ liệu sang
  `_common`; nếu chỉ chép giá trị thì repo mất luôn điều kiện đó, và lần sau ai gỡ exclusion sẽ không
  biết phải làm gì trước. Lần ấy comment được mang sang **bằng tay** — không luật nào bắt.

---

## Checklist khi viết/sửa tool

- [ ] Path persist qua `portable_locator` (Rule 1)?
- [ ] Không copy logic index/scope — import từ `_common` (Rule 2)?
- [ ] Có `--project-root` (Rule 3)?
- [ ] Nếu đọc index: có test ở index ≠ `index.jsonl` + dogfood ≥2 system (Rule 4)?
- [ ] Nếu là builder/chunker: đã dogfood doc thật có code fence + heading trùng (Rule 5)?
- [ ] Dual-tree: `.ai-work/tooling/x.py` ↔ `product/tooling/x.py` byte-identical (`diff -q`)?
- [ ] Stdlib-only (ngoại lệ phải có Approved Deviation trong `AI_WORK_CONTRACT` §6)?
- [ ] Đọc metas/index → dùng `meta_roots()` / `all_index_paths()`, KHÔNG tự chọn root (Rule 6)?
- [ ] Thêm/đổi lint rule hoặc mở rộng scan → có dòng trong impact note kèm ước lượng +N (Rule 8)?
- [ ] Sửa file tại chỗ → đọc-tính-assert-rồi-ghi (Rule 7)?
- [ ] Path đến từ DATA → `locator_str()` + `resolve_data_file()`, KHÔNG `exists()`-rồi-đọc (Rule 9)?
- [ ] Byte-compare/hash cross-source → normalize eol trước; hash chính vật đang kiểm (Rule 10)?
- [ ] Ghi file text → `newline='\n'` (file LF) / giữ nguyên eol gốc; sau edit check `git diff --stat` không phình (Rule 11)?
- [ ] Đổi **output format** của tool → grep canonical docs/SKILL pin format đó (CR Spec §2
      output-contract exception) và liệt vào §2 Target?
- [ ] Sort dùng cho anchor/matching → key `relative_to(root).as_posix()`, không `sorted()` trần (Rule 12)?
- [ ] Test có **phân biệt được** không (nếu implement sai thì có đỏ)? Test duyệt một tập → đã assert tập
      KHÔNG rỗng? Invariant tinh tế → đã chạy probe âm bản và ghi kết quả (Rule 13)?
      Probe báo **XANH** → đã chạy đủ **ba câu hỏi** (mutation landing · đổi hành vi · ca gác đủ dữ
      kiện chưa) trước khi kết luận "test yếu"? (Rule 13 §Đọc kết quả probe)
