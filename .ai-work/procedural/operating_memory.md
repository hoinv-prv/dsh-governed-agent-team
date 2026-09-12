# Operating Memory — bài học vận hành, 2 tầng (CR-AIWS-2026-08-022)

Bài học rút ra khi làm việc có **hai loại đích**:

| | Loại | Đích | Ví dụ |
|---|---|---|---|
| 1 | Cần trở thành **quy tắc phải tuân thủ** | canonical doc — `tooling_authoring_conventions` Rule N · `capture_and_triage_rules` VD-N · CR Spec · Lint Spec | *"sort dùng cho anchor phải có key tường minh"* |
| 2 | Chỉ cần **nhớ để lần sau làm đúng/nhanh hơn** | **Operating Memory** (doc này) | *"so eol giữa hai bản working-tree là vô nghĩa — phải so với HEAD"* |

Loại 2 không phải thứ yếu. Nó không đáng sửa spec, không cần cưỡng chế, nhưng biết trước thì tiết
kiệm nửa buổi.

> **Đây KHÔNG phải nguồn thẩm quyền.** Không bao giờ trích Operating Memory như căn cứ để quyết định.
> Nếu một mục cần được *tuân thủ*, nó thuộc loại 1 — nâng lên canonical, đừng để ở đây.

---

## 1. Hai tầng

| Tầng | Ở đâu | Ai ghi | Chia sẻ |
|---|---|---|---|
| **L1 — cá nhân** | Personal Notebook (đã có, bản chất không đổi) | AI/HUMAN ghi tự do, rẻ, không gate | không — per-máy |
| **L2 — dự án** | `.ai-work/memory/` (committed, **không** ship xuống downstream) | qua **rà định kỳ**, HUMAN duyệt | cả đội + mọi phiên |

Cầu L1→L2 đã có sẵn: operation `mark_capture_candidate` của Personal Notebook skill. Trước CR-022 nó
đánh dấu được ứng viên nhưng **không có đích để tới**.

**Vì sao L2 không ship xuống dự án khách:** phần lớn nội dung là tên symbol nội bộ và đường đi của
chính repo này. Đổ sang dự án khách sẽ thành nhiễu, không thành tài sản.

## 2. Đường đọc — phần quan trọng nhất

**Hai runtime tự nạp digest**, và chúng cố ý thấy hai lát cắt khác nhau:

| Runtime | Lát cắt | Vì sao lát cắt đó |
|---|---|---|
| `aiws-aip run start\|resume\|step` (qua `build_active_step_context`) → Active Step Context | **cả bảy nhóm**, mới nhất trước | đang THI HÀNH một step: `tool_gotcha` · `verification_trap` · `recurring_shape` trả giá ngay lúc gõ |
| `aiws-aip create` (qua `py .ai-work/tooling/read_operating_memory.py`) | **bốn nhóm lập kế hoạch** — `cost_sizing` · `required_order` · `where_to_look` · `rejected_option` | đang quyết HÌNH DẠNG task: chia bao nhiêu step, thứ tự nào, đọc gì trước. Digest ngắn thì còn người đọc; `--all-groups` khi cần cả bảy |

**Một implementation, hai người đọc** — cả hai gọi `_common.operating_memory_digest`. Hai bản luật hiển
thị (sắp xếp, nhãn tuổi, ngưỡng budget, câu "không phải rule") **sẽ** trôi khỏi nhau; đó là lý do
CR-AIWS-2026-08-029 tách helper thay vì cho `create` tự đọc `entries.jsonl` lần nữa.

Mỗi mục hiển thị kèm **tuổi** — hint 6 tháng phải trông khác hint tuần trước — và hậu tố ` → ref` khi mục có `ref`
(đường đọc thêm; CR-AIWS-2026-08-127 C1). Lát cắt của `run` suy từ `Kind:` của step (bảng `KIND_TO_MEMORY_GROUPS`
trong `build_active_step_context.py`, mục ngoài lát cắt được bù và đánh dấu — CR-127 C2).

**Không có đường đọc thì kho này vô nghĩa.** Bằng chứng có sẵn: `notebook` là đích duy nhất không
phải canonical doc, tồn tại đủ store + skill + operation + giá trị trong enum — và được dùng
**0/417** capture, với **1 note trong 3 tuần**, vì không bước nào trong vòng đời AIP đọc nó. Một kho
không ai đọc thì không ai ghi.

Digest, **không phải toàn văn**: kho phình thì mỗi run không được gánh thêm context.

**Giới hạn hiện tại — chỉ `run` và `create`, không hơn.** Lint, agent task desk, `aiws-pkg`,
`aiws-wiki`, và mọi phiên không đi qua hai lệnh đó — sửa một tool, review một CR, trả lời một câu hỏi
lẻ, chạy một sweep — **không tự nạp gì cả**, và sẽ không thấy gì trừ khi đọc chủ động. Ghi ra đây thay
vì để người đọc suy rằng §2 phủ mọi runtime; điều kiện đọc chủ động ở **§2.1** ngay dưới
(CR-AIWS-2026-08-077 C3, thu hẹp bởi CR-AIWS-2026-08-029).

**Và có đường đọc KHÔNG bằng được đọc.** Ảnh chụp **2026-08-17**: trong **51** AIP kể từ khi đường thứ
nhất live (2026-08-12), **0** AIP nào mang một câu kiểu *"vì mục L2 X nên tách/đổi thứ tự step"*. Đường
thứ hai được thêm chính vì con số đó — nhưng nó cũng là lời cảnh báo, vì cả hai đường đều nằm trong một
tool/skill mà ai đó phải **thực sự chạy**. Lần rà sau: đo lại con số này trước khi kết luận cơ chế có
tác dụng, và đừng thêm đường thứ ba trước khi hai đường này chứng minh được điều gì.

**Ảnh chụp thứ hai, cùng ngày — thứ đang thiếu là NỘI DUNG, không phải đường đọc.** Lát cắt `create`
hôm nay chạm **6/25 mục**, và **3 trong 4 nhóm lập kế hoạch rỗng** (`required_order` 6 · `cost_sizing`
0 · `where_to_look` 0 · `rejected_option` 0). Kho đang nghiêng hẳn về `tool_gotcha` (9) +
`verification_trap` (9) — hai nhóm mà đường `run` đã phủ. Muốn đường thứ hai có ích thì phải **ghi vào
bốn nhóm kia**, không phải nới lát cắt.

## 2.1 Đọc khi nào — ngoài `run` và `create`

> **Đây là hints, không phải authority.** Một mục ở đây làm bạn *nhìn kỹ hơn*; nó không thay
> SOP/Contract/spec và không tự chứng minh điều gì. Mục cũ có thể đã sai — luôn kiểm lại tại nguồn.
> *(Giữ nguyên văn câu này khi sao chép hoặc trỏ tới §2.1 từ nơi khác — CR-AIWS-2026-08-077 C2.)*

Không phải "đọc mỗi lần". Đọc khi bạn **sắp** làm một trong các việc dưới đây — đó chính là những lúc
bảy nhóm ở §3 có thứ để nói. Bảng này **không** hẹp lại sau CR-029: `create` chỉ phủ bốn nhóm lập kế
hoạch, và chỉ khi ai đó chạy `create`; ba nhóm còn lại (1 · 2 · 4) vẫn hoàn toàn dựa vào đọc chủ động
ngoài `run`.

| Bạn sắp… | Vì §3 nhóm |
|---|---|
| **script hoá một phép kiểm** trên file có cấu trúc (YAML/JSONL/markdown) | 4 — hình dạng lỗi tái diễn |
| **kết luận từ kết quả một phép kiểm hoặc một lần tìm kiếm** ("0 hit ⇒ không có") | 1 — bẫy kiểm chứng |
| **đo hoặc so sánh hai trạng thái** (trước/sau, cây này/cây kia) | 1 + 3 — so sai chiều, sai thứ tự |
| **gọi một tool chưa quen**, hoặc chạy trên môi trường lạ | 2 — gotcha công cụ |
| **bắt đầu một chuỗi có thứ tự bắt buộc** (baseline · mirror dual-tree · grep test) | 3 — thứ tự bắt buộc |
| **chọn giữa hai cách làm có chi phí khác nhau**, hoặc đặt timeout | 5 — định cỡ chi phí |
| **đi tìm nơi một hành vi được sinh ra** | 6 — chỗ-cần-tìm |
| **đề xuất lại một phương án** có thể đã bị bác trước đó | 7 — phương án đã bị bác |

Danh sách này **suy ra từ §3**, không phải một danh sách mới phải bảo trì song song: mỗi dòng là "lúc
nào nhóm đó có ích". §3 đổi thì bảng này đổi theo, không tự sống.

Kho ở `.ai-work/memory/entries.jsonl` — một mục là một JSON object có `group` (đúng bảy nhóm ở §3),
`title`, `body`, `verified_at`. Lọc theo `group` khớp với việc bạn sắp làm; taxonomy và shape đầy đủ:
.ai-work/memory/README.md (`.ai-work/memory/README.md`).

## 3. Bảy nhóm nên ghi

1. **Bẫy kiểm chứng** — cách kiểm mà bản thân nó sai. *Nhóm giá trị nhất, vì sai ở đây luôn nghiêng
   về phía báo-xanh.*
   > So eol giữa `.ai-work/` và `product/` **với nhau** → cả hai đã bị đổi nên trông "nhất quán";
   > phải so **worktree vs HEAD**. · `accepted=N` là tổng, không phải bằng chứng rule của mình có
   > bắn — phải `--show-accepted`. · Output công cụ tìm kiếm hiển thị `\` **không phải** byte trong file.
2. **Gotcha công cụ/môi trường** — biết thì mất 0 phút, không biết thì mất 30.
   > `py` chứ không phải `python`. · here-string PowerShell `'@` phải ở **cột 0**. · `git mv` fail với
   > file chưa track. · `subprocess` trên Windows decode theo ANSI codepage → cần
   > `encoding='utf-8', errors='replace'`. · Đẩy >64KB vào stdin pipe gây deadlock.
3. **Thứ tự bắt buộc** — "làm X trước Y, nếu không phải trả giá".
   > Đo baseline **trước** khi sửa code. · Định nghĩa contract **trước** khi bật rule cưỡng chế nó. ·
   > Grep test **trước** khi sửa tool. · Mirror dual-tree **trước** mọi bulk sweep.
4. **Hình dạng lỗi tái diễn** — để nhận ra ở chỗ mới.
   > `sorted(Path)` lật thứ tự theo OS ⇒ mọi rule chọn `paths[0]` làm anchor đều dính. · Guard im
   > lặng: accept đặt nhầm chỗ không sinh cảnh báo nào. · Test duyệt tập rỗng thì luôn xanh.
5. **Định cỡ chi phí** — để lần sau lên kế hoạch đúng.
   > Battery đầy đủ ~14 phút · whole-tree lint ~3 phút · `git show` cho ~2900 file = timeout 10 phút,
   > `git cat-file --batch` = vài giây.
6. **Chỗ-cần-tìm** — tiết kiệm vòng dò.
   > `_CR_SUBDIRS` (trong `lint_aip`) ghim tập thư mục CR. · `ARCHIVE_NAMES` gate **cả** AIP lẫn
   > workspace iteration. · `allocate_aip_id._disk_max` đếm cả `archived/` theo **prefix id**.
7. **Phương án đã bị bác + lý do** — để không ai đề xuất lại rồi điều tra lại từ đầu.
   > Thêm `cancelled` vào `ARCHIVE_NAMES`: repo không có thư mục nào tên đó. · `core.autocrlf=false`
   > là **no-op** khi `.gitattributes` có `* -text`.

## 4. KHÔNG nên vào — và đích thay thế

| Loại | Đích đúng | Vì sao |
|---|---|---|
| Một **quy tắc phải tuân thủ** | canonical doc (loại 1) | cần *tuân thủ* thì phải ở nơi có thẩm quyền |
| Kiến thức **về dự án/spec** | wiki / knowledge hub | khác trục: "cái gì đúng" vs "làm thế nào cho nhanh" |
| Việc cần làm | `future_backlog` | |
| Số liệu tức thời (số warning, số capture) | không ghi, hoặc ghi **kèm ngày** và coi là ảnh chụp | mục ruỗng nhanh nhất |
| **Số dòng** cụ thể | ghi **tên symbol** | số dòng chết ngay lần refactor sau |

## 5. Entry shape — tối thiểu, vì ghi đắt thì không ai ghi

Bắt buộc: `title` = **quy tắc hành động** (đọc title là làm được) · `group` (1 trong 7) · `body` = 1–3 câu
*triệu chứng → cách đúng*, đích ≤ ~300 B — lint WARN `operating_memory_body_long` từ 400 B / >3 câu / có ` · `
(CR-AIWS-2026-08-127) · `verified_at`.
Optional: `evidence` = **MỘT** lệnh/output/locator ≤ 150 B (không kể chuyện) · `source_ref` = provenance (CAP/AIP/CR id)
· `ref` = **MỘT** locator ổn định để đọc thêm — ưu tiên `<path>#<mục>` canonical → `module.symbol` tool → `CR-…`/`AIP-…`
id; **không** workspace path, số dòng, CAP id, file temp (lint WARN `operating_memory_ref_unstable`).

Phép thử tách bạch body/ref: **body đủ để hành động khi không mở `ref`** — cần mở `ref` mới làm đúng ⇒ body chưa đạt.
Gộp (fold) một capture vào mục cũ = **viết lại** body thành quy tắc tổng quát hơn; khác quy tắc thì **tách mục** — không
nối phụ lục (` · CÙNG HỌ …`): kho đã phình từ 68 B lên 1.319 B/mục đúng bằng cách đó (AIP-EXEC-1120 rà 31 → 30 mục).

Không bắt buộc phân loại nặng, **không** review-gate để ghi vào **L1**. Nếu ghi một bài học tốn hơn
khoảng một phút thì thiết kế sai — và con số 0.7% (3/417 capture dùng trigger best-practice) sẽ lặp lại.

## 6. Giữ kho sống — soft budget, không cắt cụt

Khi số **mục** trong L2 vượt ngưỡng, bước đọc phát **WARN gợi ý rà lại** — không tự xoá, không
truncate (khuôn CR-AIWS-2026-07-037).

Rà thì **buộc chọn** cho từng mục quá hạn:
- **nâng lên canonical** — nó đã chứng minh là quy tắc, thuộc loại 1;
- **giữ** — còn đúng, cập nhật `verified_at`;
- **xoá** — hết đúng hoặc hết cần.

Chính sức ép đó giữ kho sống. Một kho chỉ-thêm sẽ ngừng được đọc.

## 7. Xem thêm

- `capture_and_triage_rules.md` §Promote L1→L2 — tiêu chí ≥2/3 và nhịp rà.
- `tooling_authoring_conventions.md` Rule 12/13 — ví dụ của **loại 1** (cùng bài học, khác đích).
- Personal Notebook README — bản chất L1, không đổi bởi CR này.
