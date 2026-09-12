# External Code Intake Guideline

**Status:** active · **Introduced by:** CR-AIWS-2026-08-027 · **Class:** process guideline (governance)
**Scope:** nhận một **package code** từ dự án ngoài vào canonical tooling của AIWS.

AIWS đã có kỷ luật cho việc nhận **tri thức** (IR → CR → apply) và cho việc nhận **CR** từ dự án downstream
(`AIWS_Change_Request_Spec §18`). Nó chưa có kỷ luật cho việc nhận **code**: một cây module có tác giả khác,
lịch sử khác, bộ test riêng, và vẫn đang được sửa trong lúc AIWS xét duyệt.

> **Mức độ chín: n = 1.** Toàn bộ tài liệu này rút từ **một** wave adopt (CR-AIWS-2026-08-026, ASP COBOL
> preset — 31 module, 2 bộ test, 11 vòng CR, nguồn thay đổi 4 lần giữa chừng). Vài luật có thể quá hẹp hoặc
> quá rộng. **Lần adopt thứ hai là phép thử thật** — rà lại tài liệu này sau đó, đừng coi nó đã đóng.

**Năm trong tám luật là lỗi của phía NHẬN**, không phải của dự án nguồn. Đó là lý do chúng sẽ lặp lại nếu
không viết ra.

---

## L1 — Cái đã CHỨNG MINH và cái sẽ SHIP có thể là hai bản khác nhau

Mọi số đo chất lượng dự án nguồn đưa ra thuộc về **bản họ đang chạy**. Thứ AIWS nhận là **package source**.
Trước khi trích bất kỳ con số nào như phẩm chất của thứ sắp nhận, phải xác định hai bản đó có **giống nhau
không**.

- **Đã trả giá:** nguồn tự khai 4 file lệch giữa `packages/…/src/` (thứ ship) và cây đã cài (thứ chạy); bản
  chạy có 2 fix mà bản ship thiếu. CR-026 r1–r4 viết *"code đã chạy trên 8857 meta thật"* như phẩm chất của
  thứ sắp nhận — sai attribution, phải đính chính ở r5. Bản dist cắt sau đó **vẫn** thiếu 2 fix.
- **Ranh giới:** không đòi hai bản phải giống nhau — đòi **biết** chúng có giống không, và nói đúng câu đó.

## L2 — Mô tả API trong CR là GIẢ THUYẾT; bộ test đi kèm package là SPEC

Khi CR mô tả hợp đồng của một hàm/API nhận từ ngoài, mô tả đó là **giả thuyết của người viết CR**. Nguồn sự
thật là **bộ test đi kèm package**. Test đỏ ⇒ mặc định **CR sai**, không phải test sai.

- **Đã trả giá:** CR-026 mô tả `write_meta_if_changed` = *"chỉ ghi khi nội dung khác"*. Cài đúng vậy: test
  riêng 11 check xanh, đã probe âm bản. Nhưng bộ test của package đỏ **1/125** — hợp đồng thật là **bỏ qua
  `updated_at` trong frontmatter và giữ stamp cũ trên đĩa**. Không đọc ra được từ mô tả; chỉ test bắt.
- **Ranh giới:** package không có test cho phần đó ⇒ hợp đồng vẫn là giả thuyết — **ghi rõ là giả thuyết**.
- Liên quan: `tooling_authoring_conventions` **Rule 13** (test phải phân biệt được).

## L3 — "Stdlib-only" và mọi thuộc tính kỹ thuật là LỜI KHAI cho tới khi enumerate

Thuộc tính do nguồn tuyên bố (chỉ dùng stdlib, không ghi ngoài out-root, không phụ thuộc X) phải được
**enumerate lại** trên chính cây sắp nhận trước khi đưa vào CR.

- **Đã trả giá:** `cobol_parser` khai stdlib-only và **đúng** — nhưng chỉ biết chắc sau khi liệt kê import của
  14 module. Ngược lại `handlers/cobol.py` **hard-import** `cobol_parser`, trong khi CR bản đầu ghi *"cobol_wiki
  không import cobol_parser, nên cobol_parser ngoài scope"* — sai, và nó đổi hẳn phạm vi CR.
- **Ranh giới:** enumerate **một lần cho mỗi vòng duyệt**, không phải mỗi lần đọc (xem L5).

## L4 — Danh sách target phải SINH TỪ MÁY; và pattern khớp KHÔNG đồng nghĩa defect

**Vế 1 — enumerate bằng lệnh.** Khi §2 Target trỏ tới một **cây** (thư mục, package) chứ không phải vài path
rời, danh sách và con số phải **sinh bằng lệnh** rồi dán vào CR. Không kê tay.

- **Đã trả giá:** CR-026 §2 ghi `cobol_wiki` "12 module" (liệt kê 16 tên — sai số học — và **bỏ sót**
  `handlers/cobol_regex.py`, chính là fallback mà một DP của CR dựa vào) và `cobol_parser` "13 module" (bỏ sót
  `__init__.py`, API surface). Thực tế **17** và **14**. Lỗi sống qua **6 vòng CR** và qua **cả vòng PO
  approve**, vì con số trông hợp lý; chỉ bị bắt ở bước re-verify trước khi copy.

**Vế 2 — pattern khớp không đồng nghĩa defect.** Khi CR nêu **N** file mà grep ra **M ≫ N**, đừng cho rằng CR
đếm thiếu. Hỏi **vì sao lệch** trước: cùng một chuỗi có thể mang nghĩa khác nhau tuỳ **vị trí** file. Cách kiểm
rẻ nhất là chạy **chính cái check đang báo lỗi** lên một mẫu thuộc nhóm dôi ra — nó im thì nhóm đó không phải
defect.

- **Đã trả giá:** một script grep pattern link SOP hai-bậc ra **104** file và sửa hết, trong khi CR nêu **5**.
  Link đó chỉ **hỏng** ở layout ba bậc; ở layout phẳng nó resolve đúng. `lint_aip` báo **1** hit trên file ba
  bậc và **0** trên file phẳng — một lệnh là xong. Phải khôi phục 99 file. Sửa 99 file không hỏng không chỉ
  lãng phí: nó nhấn chìm 5 sửa thật vào một diff không ai review nổi.
- **Ranh giới:** path rời (1–3 file) kê tay vẫn được — ngưỡng là "cây", không phải số lượng. Vế 2 áp khi danh
  sách target được **suy ra bằng pattern**, bất kể cây hay rời.

## L5 — CR đang mở phải RE-VERIFY claim vs upstream trước MỖI vòng duyệt

Một CR nhận code từ ngoài có **nền di động**. Mọi claim grounded vào nguồn phải được kiểm lại trước mỗi vòng
trình PO, và trạng thái nguồn phải được **ghim** ở thời điểm apply.

- **Đã trả giá:** nguồn đổi **4 lần trong 4 ngày** giữa lúc CR mở — chuyển từ regex sang parser (đổi hẳn scope,
  +11.5k dòng) → cập nhật docs → port 2 fix + bundle thư viện → build lại dist. Mỗi lần đều làm chết ít nhất
  một khẳng định trong CR. Lúc apply, nguồn ở trạng thái **HEAD + 7 file chưa commit** ⇒ sha commit một mình
  **không** tái lập được; phải ghim **sha256 của cả 32 file thực sự copy**.
- **Ranh giới:** không đòi theo dõi liên tục — đòi kiểm lại **tại các mốc**: mỗi vòng duyệt, và ngay trước copy.

## L6 — Muốn nói "X xung đột với Y", phải đọc chỗ SINH RA X

Trước khi kết luận code nhận vào **xung đột** với một invariant của AIWS, phải đọc nơi **sinh ra** hành vi đó —
không chỉ nơi cấu hình nó, và không chỉ triệu chứng ở đầu ra.

- **Đã trả giá:** dogfood báo 5 lỗi `meta_object_no_outedge`. Kiểm hai knob cấu hình thấy đều thuận lợi ⇒ kết
  luận *"xung đột thật với INV-4"* và trình PO như một blocker cần đổi lint rule. **Sai.** Hàm emit có sẵn một
  out-edge thiết kế cho đúng INV-4, lấy từ **cột 5 của catalog CSV**; comment ngay trong code nói thẳng điều
  đó. Fixture dùng dạng inline không mang được cột ấy. Đổi sang CSV ⇒ **0 error**. Chi phí của kết luận sai:
  một vòng trình PO và một đề xuất đổi lint rule không cần thiết.
- **Ranh giới:** áp cho claim **xung đột kiến trúc**. Bug thường thì đọc triệu chứng là đủ.

## L7 — CR đổi identifier phải khai CHI PHÍ ở phía đang dùng tên cũ

Mọi DP đổi tên một identifier (`source_type`, tên module, tên file) phải trả lời: **ai đang dùng tên cũ, và họ
trả giá gì**. Và phải kiểm identifier đó có được dùng để **dẫn xuất path** không — đổi một field và đổi một
thư mục là hai mức rủi ro khác hẳn nhau.

- **Đã trả giá:** DP đổi `cobol_source` → `asp_cobol_source` được trình bày như quyết định đặt tên thuần tuý.
  Thực tế: (a) corpus đang sống của dự án nguồn mang tên cũ trên ~8857 meta; (b) **thư mục meta lấy tên từ
  chính `source_type`** khi thiếu một cờ ⇒ đổi tên sẽ **di dời cả cây meta** và mọi locator trong index. Cả hai
  phải bổ sung ở vòng sau. Đổi tên package còn là **import path** trong config của mọi dự án.
- **Ranh giới:** không cấm đổi tên — đòi **khai giá trước khi PO quyết**.

## L8 — Bundling lúc phân phối ≠ vendoring nguồn

Khi một package mang theo thư viện khác, phân biệt bằng **ba** tiêu chí: (1) source of truth của thư viện nằm
ở đâu; (2) sau khi cài, nó là package **top-level** hay **lồng** trong consumer; (3) hợp đồng standalone của nó
còn **kiểm được** không.

- **Đã trả giá (theo hướng tốt):** yêu cầu "đóng gói `cobol_parser`" được giải bằng khai báo `BUNDLED` trong
  build script — payload mang thư viện **song song** engine, source vẫn ở package riêng, `test_standalone.py`
  vẫn đúng sau khi cài. Ba tiêu chí đều đạt ⇒ **không** mâu thuẫn ruling "first-class, không vendored". Không
  có ba tiêu chí này thì rất dễ **bác nhầm một giải pháp đúng**.
- **Ranh giới:** tiêu chí (3) chỉ áp khi thư viện **có** hợp đồng standalone kiểm được.

---

## Phụ lục — cạm bẫy id namespace

`AIWS_Change_Request_Spec §18` cấm dự án downstream mint id trong namespace upstream, nhưng luật phát biểu ở
mức **tên file**. Code nhận vào có thể mang id upstream trong **docstring/comment**, nơi lint `duplicate_cr_id`
không nhìn tới.

Wave này gặp thật: 3 docstring trích một `CR-AIWS-*` id mà ở AIWS id đó thuộc về một CR **hoàn toàn khác** (đã
applied) ⇒ người đọc tra ra sai. **Intake phải grep `CR-AIWS-` trong payload và re-anchor trước khi merge.**

## Xem thêm

- `AIWS_Change_Request_Spec_MVP` §18 (id namespace downstream) · §11.5–11.9 (kỷ luật §2 Target).
- `tooling_authoring_conventions` Rule 11 (writer không đổi eol) · Rule 13 (test phải phân biệt được).
- `capture_and_triage_rules` §Verification discipline VD-5 (đọc nguồn, không đọc bản render).
- `CR-AIWS-2026-08-026` — wave sinh ra toàn bộ evidence ở đây; Revision History r1–r11 + Apply Outcome.
