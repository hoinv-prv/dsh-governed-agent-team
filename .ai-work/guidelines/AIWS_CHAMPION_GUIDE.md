# AIWS Champion Guide — Hướng dẫn kỹ thuật triển khai AI Work System cho dự án

> **Đối tượng:** Champion / người phụ trách rollout AIWS cho một dự án cụ thể (BrSE, PM, Lead...).
> Không phải người phát triển methodology AIWS — xem `AIWS_DEV_GUIDE.md` cho vai trò đó.
>
> **Base package:** `AI_Work_System_MVP_v1.2.0_2026-08-20`
> **Quan hệ với tài liệu có sẵn:** Guide này là bản **toàn diện + kỹ thuật** dùng để tra cứu.
> Với người mới hoàn toàn, gửi `AIWS_Onboarding_Guide.md` trước — nó có luồng cài đặt A/B step-by-step.
> Guide này giả định bạn đã cài xong, và muốn hiểu **hết mọi skill, mọi tình huống**.

---

## Runtime baseline v1.2.0

For every non-trivial task, the Working AIP is the stable authority for intent and steps; the Task Workspace holds mutable findings, questions, drafts, `02_runtime_queue.jsonl`, and `08_capture_inbox.jsonl`. `00c_active_step_context.md` (ASC) is derived from the active AIP step—read it before work, but do not treat it as a replacement for the AIP.

Wiki lookup routes to likely evidence; it does not itself verify content. Open and verify the routed source before relying on it. In a `multi_system: true` project, the Human chooses the active system and lookups use `--system <id>` (or deliberate `--all-systems`); there is no silent default. Local and unregistered/raw search are exceptional and require explicit authorization.

Champions own rollout, adoption, project-local templates, and escalation. They may propose a candidate or CR, but may not self-promote Wiki/canonical content or self-apply a canonical change.

---

## Champion role in practice

### Champion là ai và chịu trách nhiệm điều gì?

Champion là người thành thạo AI và AIWS, chịu trách nhiệm giúp một dự án đưa AIWS vào công việc thật. Champion không chỉ hướng dẫn lệnh; họ chuẩn bị điều kiện để team làm việc lặp lại được, an toàn và có thể cải tiến.

Champion chịu trách nhiệm chuẩn bị project-local setup, nhận diện knowledge/template cần thiết, dẫn dắt pilot, hỗ trợ member ở task đầu tiên, và tổng hợp vấn đề để đề xuất cải tiến. Champion không tự phê duyệt hay áp dụng thay đổi canonical; không tự promote Wiki; không thay member sở hữu task hoặc người chịu trách nhiệm delivery.

### Vòng lặp vận hành của Champion

1. **Chuẩn bị:** xác định mục tiêu rollout, team/role, nguồn tài liệu, active system và một pilot thật nhỏ.
2. **Pilot:** cùng một member tạo/chạy AIP cho task thật; quan sát chỗ thiếu context, template hoặc hướng dẫn.
3. **Enable:** hướng dẫn member tiếp theo bằng onboarding + task thật; Champion kiểm tra hiểu task và boundary, không làm thay.
4. **Cải tiến:** xem lại findings/candidate; cải tiến project-local asset khi có evidence; chuẩn bị CR khi vấn đề thuộc canonical.

### Checklist Champion

#### Trước rollout/pilot

- [ ] Có mục tiêu rollout và role/member pilot.
- [ ] Chọn task thật, nhỏ, có kết quả kiểm chứng được.
- [ ] Xác định input/source of truth và active system nếu project đa hệ.
- [ ] Member đã biết onboarding guide; Champion đã xác định tài liệu kỹ thuật cần route.

#### Trước khi member start AIP đầu tiên

- [ ] AIP có scope, output, input và open point rõ ràng.
- [ ] Input được route qua Wiki trước khi đọc; lookup result được mở/verify trước khi tin.
- [ ] Member hiểu AIP là authority ổn định, Workspace là nơi ghi runtime, ASC chỉ là view theo step.
- [ ] Không có thao tác Wiki/canonical/agent nào vượt authority được hiểu là "đương nhiên".

#### Sau pilot hoặc mỗi tuần

- [ ] Ghi nhận blockage lặp lại, gap knowledge, và template candidate.
- [ ] Tách việc có thể cải tiến project-local khỏi việc cần CR/canonical approval.
- [ ] Chọn một cải tiến có evidence thay vì mở rộng scope đồng thời nhiều hướng.

### Tình huống thường gặp

| Tình huống | Champion làm gì | Không làm gì |
|---|---|---|
| Member bị kẹt | Làm rõ mục tiêu/input, hỗ trợ tạo open point, route đúng guide | Tự làm toàn bộ task thay member |
| Thiếu knowledge | Xác minh nguồn và capture candidate | Tự promote Wiki |
| Task lặp lại | Thu evidence từ AIP đã hoàn tất, đề xuất template local | Tạo template từ giả định |
| Rule canonical có vẻ không phù hợp | Tách observation/proposal, lập CR draft | Sửa canonical trực tiếp |
| Cần dùng agent | Kiểm tra AIP/step assignment và trial status | Tự dispatch ngoài AIP/gate |

### Prompt mẫu đã kiểm chứng

Mỗi prompt dưới đây đã có acceptance record tại `06_prompt_acceptance_tests.md`; khi copy phải thay placeholder và giữ nguyên boundary.

1. **Chuẩn bị pilot:** "Tôi là Champion của dự án `<project>`. Hãy lập checklist sẵn sàng cho pilot AIWS: input cần có, setup project-local, cách chọn task pilot, và tiêu chí theo dõi. Không tự cài, không tự tạo Wiki/canonical change. Nêu open point."
2. **Onboard member:** "Là AI hỗ trợ Champion, hãy tạo kế hoạch onboarding 45 phút cho `<role>` đã cài AIWS. Bao gồm mục tiêu, tài liệu cần đọc, bài tập task thật nhỏ, và dấu hiệu cần Champion hỗ trợ. Không chạy AIP thay member."
3. **Task đầu tiên:** "Tôi là Champion của dự án `<project>`. Một member mới cần `<task>`. Hãy lập kế hoạch hỗ trợ 30 phút: mục tiêu, checklist Champion, prompt yêu cầu tạo AIP, và điểm kiểm tra trước khi start. Không sửa file hoặc tự chạy AIP/Wiki/canonical."
4. **Cải tiến template:** "Một loại task lặp lại đã có `<n>` AIP hoàn tất. Hãy đề xuất evidence cần thu thập, outline template, và rủi ro; không tự sửa template."
5. **Triage knowledge:** "Một tài liệu `<source>` có thể hữu ích cho nhiều task. Hãy phân loại dùng trực tiếp/notebook-candidate/đề xuất Wiki; nêu evidence và approver. Không tự đưa vào Wiki."
6. **Đề xuất CR:** "Champion thấy `<rule>` cần cải tiến. Hãy lập kế hoạch viết CR: evidence, observation vs proposal, approver, và điều không được làm trước khi duyệt. Không sửa canonical."

### Revision history

| Date | Rev | Change |
|---|---|---|
| 2026-08-20 | r1 | Added practical Champion enablement guidance, decision cards, and prompt library without altering the technical runtime sections. |
| 2026-08-25 | r2 | Expanded role definition, operating cycle, checklists, and decision cards with practical scenarios; replaced sample prompts with tested Vietnamese templates. Applied per CR-AIWS-2026-08-122 C1–C5. |

---

## 0. Bức tranh tổng thể

AIWS hoạt động trên 3 khối:

| Khối                                  | Là gì                                                                             | Sống ở đâu sau khi cài                                      |
| -------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **Skills**                       | Các "lệnh" AI biết làm — router pattern, mỗi domain 1 skill với nhiều verb  | `.claude/skills/<name>/SKILL.md` (stub) → trỏ tới bản full |
| **AIP (AI Implementation Plan)** | Kế hoạch làm 1 task cụ thể — PLAN hoặc EXEC                                  | `.ai-work/aip/<account_id>/<kind>/AIP-...md`                   |
| **Wiki (Knowledge Hub)**         | Tờ giới thiệu (meta) cho từng tài liệu, để AI tra nhanh thay vì đọc hết | `.ai-work/wiki_sources/`, `.ai-work/wiki/`                   |

Nguyên tắc vận hành: **AIP là kế hoạch cố định, Workspace là nơi làm thật, Wiki là bộ nhớ tra cứu dùng lại.**
Bạn hầu như không cần gõ đúng cú pháp lệnh — nói tự nhiên, AI (qua skill router) tự chọn đúng verb.

### 0.1 Flow triển khai tổng thể (7 bước)

Khi triển khai AIWS cho 1 dự án mới, hình dung theo 7 bước tuần tự sau — mỗi bước map với 1 nhóm skill đã có trong guide này:

| #  | Bước                                      | Nội dung                                                                                                                                                                                                                                                                            | Skill / verb tương ứng                                                                                                                                                              |
| -- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ① | **Tổng hợp tài liệu**             | Gom & phân loại tài liệu gốc của dự án (RD/BD/DD, checklist, process...) trước khi đưa vào hệ thống.                                                                                                                                                                  | Thủ công                                                                                                                                                                             |
| ② | **Convert & chuẩn hoá**             | Convert file gốc (PDF/Excel/Word/ảnh/drawio...) sang Markdown chuẩn cho AI đọc.                                                                                                                                                                                                 | `aiws-doc-convert-skill` (§4.3)                                                                                                                                                     |
| ③ | **Build Wiki**                        | Khởi tạo khung Wiki (`bootstrap`), sau đó đăng ký toàn bộ tài liệu đã convert vào Wiki (`register` / `register-batch`), kể cả meta cho source code.                                                                                                            | `aiws-wiki bootstrap` (§4.0) → `register`/`register-batch` (§4.4) → `build_python_wiki_metas.py`/`build_java_wiki_metas.py` (§4.5) → `test-lookup` để verify (§5) |
| ④ | **Tạo AIP template**                 | Từ các loại task lặp lại của dự án, soạn sẵn AIP template (PLAN/EXEC) để dùng lại — không phải soạn AIP từ đầu mỗi lần.                                                                                                                                       | `aiws-aip create` — ưu tiên base trên template có sẵn; chưa có → tạo pilot rồi nâng thành template (§3.1, §3.5)                                                       |
| ⑤ | **Chạy pilot & tinh chỉnh**         | Chạy thử 1 AIP thật trên dự án (`run`), lint kiểm tra (`aiws-lint`), rồi tinh chỉnh lại Wiki/AIP template dựa trên kết quả thực tế trước khi nhân rộng.                                                                                                      | `aiws-aip run` (§3.2) → `aiws-lint` (§3.3) → quay lại chỉnh Wiki (§4.6) / template (§3.5) nếu cần                                                                        |
| ⑥ | **Dùng AIP chạy task thật**        | Nhân rộng ra công việc hằng ngày: mọi task đáng kể đều tạo AIP (base trên template ở ④) rồi chạy trong workspace — không làm ad-hoc ngoài AIP. Tra Wiki trước mọi input (HARD GATE), capture candidate ngay trong lúc chạy, lint 0 lỗi mới đóng task. | `aiws-aip create` (§3.1) → `aiws-aip run start` / `resume` / `status` (§3.2) → `aiws-lint` (§3.3) → đóng task (§3.4)                                                |
| ⑦ | **Cập nhật Wiki & cải thiện AIP** | Định kỳ duyệt candidate từ capture inbox → đưa vào Wiki (`register` / `refresh`) và verify bằng `test-lookup`; đồng thời mang bài học ngược lại vào AIP template để lần chạy sau tốt hơn.                                                           | `aiws-wiki register` (§4.4) / `refresh` (§4.6) → `test-lookup` (§5) → nâng cấp template (§3.5)                                                                           |

> ①–⑤ là flow **rollout ban đầu**, làm 1 lần khi mở dự án. ⑥–⑦ là **vòng lặp vận hành hằng ngày** — chạy task bằng AIP, rồi nạp kết quả ngược lại vào Wiki/template. Chính vòng ⑥→⑦ giữ cho Knowledge Hub và bộ template luôn sống; không cần làm lại từ ①.

---

## 1. Danh sách toàn bộ Skill

| Skill                             | Người dùng gọi trực tiếp? | Mục đích 1 dòng                                                                                                                                |
| --------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `aiws-aip`                      | ✅ Có                          | Vòng đời AIP: tạo (create), chạy (run), quản lý workspace/step                                                                              |
| `aiws-wiki`                     | ✅ Có                          | Vòng đời Wiki: đăng ký, tìm, cập nhật, test, build trang tổng quan                                                                       |
| `aiws-doc-convert-skill`        | ✅ Có                          | Convert PDF/Excel/Word/ảnh/drawio/svg/... → Markdown cho AI đọc                                                                                |
| `aiws-lint`                     | ✅ Có                          | Kiểm tra lỗi cấu trúc AIP/workspace/wiki (deterministic, không phải review nội dung)                                                        |
| `aiws-pkg`                      | ✅ Có                          | Cài / nâng cấp / build package AIWS (install, upgrade, quick-install, build)                                                                    |
| `aiws-agent`                    | ✅ Có                          | Router cho**AI Agents Pack** riêng (tạo/chạy/clone agent chuyên biệt)<br />*(*) Hiện vẫn là bản beta, chưa release chính thức* |
| `aiws-util-mail-confirm`        | ✅ Có                          | Sinh mail/chat confirm tiếng Nhật từ nội dung tiếng Việt (BrSE/Comtor)                                                                       |
| `aiws-util-personal-notebook`   | ✅ Có                          | Ghi note cá nhân (chưa đủ chín để vào wiki)<br />(*) Hiện vẫn là bản beta, chưa release chính thức                                 |
| `aiws-review-plan`              | ❌ Nội bộ                     | AI tự gọi khi`aiws-aip create` scaffold task review cross-document — bạn không gọi trực tiếp                                             |
| `aiws-runtime-review-checklist` | ❌ Nội bộ                     | AI tự gọi để tạo checklist review runtime cho 1 lượt review — không gọi trực tiếp                                                      |

> Bạn chỉ cần nhớ **8 skill có thể gọi trực tiếp**. 2 skill nội bộ tự chạy ngầm khi cần, không phải lo.

---

## 2. Tình huống: CÀI ĐẶT

Dùng `aiws-pkg install` (hoặc nói tự nhiên "cài AIWS vào dự án này, package ở đường dẫn X").

Checklist:

1. Trỏ Claude vào **folder PROJECT** (không phải folder giải nén package).
2. Cung cấp đường dẫn package đã giải nén.
3. Claude hỏi tên project ngắn → xác nhận.
4. Verify: gõ `/aiws-aip create` → nếu AI hỏi loại task là **cài đúng**; nếu báo "unknown command" là đang mở sai folder.
5. Chạy thử 1 task nhỏ thật (xem §3) để xác nhận toàn luồng hoạt động, không chỉ cài xong là đủ.

**Verbs khác của `aiws-pkg`** (ít dùng với champion, biết để không bối rối khi thấy):

- `upgrade` — nâng cấp bản AIWS đang cài lên version mới hơn. Luôn temp-first (`.aiws-upgrade.tmp`), không tự áp dụng, phải người xác nhận, không đè Truth (`SOP_MASTER.md`, `AI_WORK_CONTRACT.md`), không tự xoá file trừ khi nằm trong rename-map + đã confirm.
- `quick-install` — chỉ dành cho người **dev AIWS** cài thử trực tiếp từ working tree (không phải bản release) để test nhanh; không dùng cho dự án thật.
- `build` — đóng gói bản release mới từ `product/` — việc của team dev AIWS, không phải champion.

---

## 3. Tình huống: LÀM 1 TASK BẰNG AIP (từ tạo pilot → run → test → đóng)

### 3.1 Tạo AIP (skill `aiws-aip`, verb `create`)

Nói tự nhiên: *"Tạo AIP để tôi review basic design chức năng F04"* hoặc gõ `/aiws-aip create`.

**Flow chuẩn khi tạo AIP — luôn ưu tiên template có sẵn:**

1. AI kiểm tra xem đã có **AIP template** phù hợp với loại task này chưa (trong `preset_knowledge/` hoặc `.ai-work/aip/templates/`).
2. Có template phù hợp → **base AIP mới trên template đó**, không soạn lại từ đầu.
3. Chưa có template phù hợp → tạo 1 **pilot AIP** (bình thường, theo checklist dưới) → chạy (§3.2) → test/đóng task (§3.3–3.4) → nếu thấy dạng task này sẽ lặp lại nhiều lần, biến pilot đã chạy tốt thành template dùng lại được (xem chi tiết §3.5).

AI sẽ:

- Hỏi rõ loại task (nếu chưa rõ PLAN hay EXEC — khi phân vân, AI chọn PLAN vì an toàn hơn).
- **Bắt buộc tra Wiki trước** khi mở bất kỳ tài liệu RD/BD/DD/spec nào làm input (HARD GATE) — không tự Glob/Grep hay đoán đường dẫn file liên quan.
- Cấp AIP ID qua tool cấp phát (không tự đặt số).
- Ghi AIP vào `.ai-work/aip/<account_id>/<kind>/AIP-<KIND>-NNN-<slug>.md`.
- Tự kiểm tra checklist trước khi báo xong (đúng section, field, `lint_aip` sạch).

Nếu chưa rõ AIP tạo ra có đúng ý không → mở file AIP vừa tạo, đọc lại, bảo AI chỉnh.

### 3.2 Chạy AIP (skill `aiws-aip`, verb `run`)

`/aiws-aip run start` hoặc *"Chạy AIP AIP-EXEC-012"*.

- AI tạo **workspace** riêng cho task (nơi ghi mọi finding/draft/kết quả thật — **AIP không bị sửa trong lúc chạy**).
- Materialize "Active Step Context" (bối cảnh của bước hiện tại) để AI không lạc trọng tâm.
- Luôn đọc ASC trước khi thao tác workspace; ghi candidate có giá trị tái dùng vào Capture Inbox ngay khi phát hiện, rồi triage trước khi đóng task.
- Trong lúc làm: nếu phát hiện điều gì đáng lưu vào wiki sau này (candidate) → AI ghi ngay vào capture inbox, không chờ dồn cuối task.
- Di chuyển giữa các bước: `run step` (đi tiếp) — bình thường tự động theo `run start`/`run resume`, không cần bạn tự gọi.
- Tiếp tục task cũ: `run resume` hoặc *"tiếp tục AIP-EXEC-012"* — AI tự tìm lại đúng workspace.
- Xem tiến độ: `run status`.

### 3.3 Kiểm tra trước khi đóng task (skill `aiws-lint`)

Trước khi coi task xong: *"Chạy lint kiểm tra AIP và workspace"* hoặc `/aiws-lint` (scoped theo task, tự động khi `run` tới bước finalize).

- Phải **0 lỗi** thì mới đóng được.
- Nếu task có chạm vào phần lõi hệ thống hoặc áp dụng 1 CR → lint tự nâng cấp thành kiểm tra toàn bộ cây (whole-tree), không chỉ riêng task.

### 3.4 Đóng task

AI tự làm "Final Capture Sweep" (rà lại mọi thứ đáng lưu vào wiki, không được bỏ qua) → chuyển trạng thái AIP thành `done` → lint lại lần cuối.
Bạn chỉ cần xác nhận các candidate nào nên đưa vào wiki thật (xem §4).

### 3.5 Biến 1 "pilot AIP" thành AIP template dùng lại được

Không có nút bấm riêng cho việc này — đây tự nó là **1 task mới**, làm đúng quy trình AIP:

1. Sau khi pilot AIP chạy thành công và bạn thấy dạng task này sẽ lặp lại nhiều lần → tạo 1 **AIP EXEC mới**, mục tiêu: "thiết kế 1 template/preset AIWS có thể dùng lại".
2. Input cho AIP mới này: chính pilot AIP đã chạy tốt + 1 template có sẵn để tham khảo cấu trúc.
3. Output: file template mới.
   - Nếu chỉ dùng trong **project này** → lưu ở `.ai-work/aip/templates/<file>` — không cần CR, tự do.
   - Nếu muốn **đóng gói lại cho AIWS dùng chung mọi dự án** → phải theo đúng flow CR (xem `AIWS_DEV_GUIDE.md`), không tự thêm vào package.
4. Gợi ý cấu trúc: theo cặp **Sample (PLAN) + EXEC** giống các preset có sẵn trong `preset_knowledge/` — dễ tái sử dụng và dễ người khác đọc theo.

---

## 4. Tình huống: THÊM TÀI LIỆU VÀO WIKI

### 4.0 Bắt đầu dự án — build wiki lần đầu (skill `aiws-wiki`, verb `bootstrap`)

Đây là **skill dùng đầu tiên** khi bạn mới nhận 1 dự án và bắt đầu xây Knowledge Hub — chạy trước mọi verb khác trong §4.
Nói tự nhiên: *"Bắt đầu xây wiki cho dự án này"* hoặc gõ `/aiws-wiki bootstrap`.

- Mục đích: khởi tạo toàn bộ khung wiki cho project (cấu trúc `.ai-work/wiki_sources/`, `.ai-work/wiki/`, index rỗng...) trước khi đăng ký tài liệu đầu tiên — không phải build lại từ đầu mỗi lần thêm 1 file.
- Dùng đúng 1 lần khi project chưa có wiki; các lần sau (thêm/sửa tài liệu) dùng `register` / `register-batch` / `refresh` như §4.4–4.6.
- Sau khi bootstrap xong mới bắt đầu quy trình convert → register ở §4.3–4.4.

### 4.1 Vì sao cần Wiki

Mỗi tài liệu (RD, BD/DD, checklist, process, source code...) được viết 1 "tờ giới thiệu" ngắn (**Wiki Source Meta**): tóm tắt, từ khoá tra, mục liên quan. AI tra tờ giới thiệu trước — không đọc hết file gốc mỗi lần → nhanh hơn, đúng hơn, có traceability.

### 4.2 Quy tắc "nên đưa vào wiki khi nào"

✅ Nên: requirement/Q&A đã chốt, design (BD/DD), process, guideline, checklist — bất kỳ tài liệu sẽ bị tra lại ≥ 1 lần.
❌ Chưa nên: bản nháp đang đổi hằng ngày, note cá nhân, email rời rạc → để **Personal Notebook** (`aiws-util-personal-notebook`) trước, chín rồi mới đưa vào wiki.

### 4.3 Bước 1 — Convert tài liệu gốc sang Markdown (nếu chưa phải .md)

Skill: `aiws-doc-convert-skill`.

- Input: PDF, Excel (.xlsx/.xls), PowerPoint, Word, ảnh (png/jpg/tiff/...), drawio, svg, csv/txt/html/json/xml/yaml/eml.
- Nói: *"Convert file này sang Markdown cho AI đọc"*.
- Riêng Excel: nội bộ dùng `convert_excel_to_md.py` — mỗi sheet ra 1 file Markdown.
- Chiều ngược lại (Markdown → Excel, khi cần trả deliverable cho khách): `convert_md_to_excel.py` — **luôn làm xong & review trong Markdown trước, export Excel/Word ở bước cuối cùng**, đừng export sớm rồi sửa tay trong Excel/Word (mất context AI đọc lại).
- Skill này **chỉ trích xuất** (input → Markdown), không dựng ngược file Office từ Markdown có style gốc.

### 4.4 Bước 2 — Đăng ký vào Wiki

Skill: `aiws-wiki`, verb `register` (1 file) hoặc `register-batch` (cả folder).
Nói tự nhiên: *"Add file này vào wiki"* / *"Đăng ký cả folder design vào wiki"*.

Luồng bên trong (AI tự làm, bạn chỉ xác nhận ở các điểm chặn):

1. Convert binary → Markdown (nếu chưa làm ở §4.3).
2. Phân loại `artifact_type` — nếu AI không chắc (confidence thấp) → **hỏi bạn xác nhận, bắt buộc**.
3. Build meta (`build_wiki_source_meta.py`) → lint → smoke test.

Với `register-batch` (cả folder), có 3 điểm AI phải dừng hỏi bạn:

- Duyệt kế hoạch nhóm tài liệu trước khi build.
- Duyệt mẫu đầu tiên (sample) khi gặp format mới.
- Duyệt pattern (PMP) + quyết định route khi cần.

### 4.5 Tạo meta từ SOURCE CODE (Python / Java) — batch, không phải tay từng file

Đây là phần khác biệt nhất so với đăng ký tài liệu thường — dùng tool trực tiếp (chưa có verb riêng bao bọc, nhưng vẫn nằm trong hệ `aiws-wiki build-meta`):

| Ngôn ngữ | Tool                           | Cách chạy                                                                                    |
| ---------- | ------------------------------ | ---------------------------------------------------------------------------------------------- |
| Python     | `build_python_wiki_metas.py` | `--root <package> --source-prefix PY-<PROJECT> --meta-subdir python [--dry-run] [--limit N]` |
| Java       | `build_java_wiki_metas.py`   | `--root <src> --source-prefix JAVA-<PROJECT> --meta-subdir java [--dry-run] [--limit N]`     |

- Cả 2 build **1 meta / 1 file source**, tự phân tích code (Python: dùng `ast` chuẩn; Java: regex, có thể dùng `tree-sitter-java` nếu máy có cài, nếu không tự fallback về regex — không cần lo thiếu dependency).
- Tự nối quan hệ `## Related Sources` (import/gọi hàm) giữa các module trong project.
- Java còn tự trích **REST endpoint** (`@RequestMapping` + verb) vào mục `## Endpoints` — hữu ích để nối Frontend ↔ Backend.
- Luôn dùng `--dry-run` trước để xem trước sẽ tạo gì, rồi mới chạy thật.
- Đây chỉ tạo meta cho **file source** (artifact) — nếu muốn có node cho 1 hàm/màn hình/bảng cụ thể (`node_kind: object`) thì phải viết tay, tool không tự tạo loại này.

Bạn có thể nhờ AI chạy hộ: *"Dùng build_python_wiki_metas.py để tạo meta cho toàn bộ package backend này, dry-run trước cho tôi xem."*

> **Best practice:** Với meta cho **source code**, nên nhờ Claude Code chạy đúng tool "wiki build router" (`build_python_wiki_metas.py` / `build_java_wiki_metas.py`) để tạo meta — **không nên dùng LLM tự đọc code rồi viết meta tay**. Tool deterministic, đọc code bằng `ast`/regex (Java có thể dùng `tree-sitter-java` nếu có, fallback regex) nên chính xác và ổn định hơn LLM tự suy diễn. Hiện AIWS có sẵn tool cho **Python** và **Java**; các ngôn ngữ khác sẽ được bổ sung dần.

### 4.6 Cập nhật khi tài liệu gốc đổi

Verb `refresh` / `refresh-meta`. Nói: *"Source đã đổi, cập nhật wiki meta"*.
⚠️ Có 5 tình huống bị **chặn cứng, không tự làm**, phải qua duyệt (Promotion Gate): đổi 1 meta thành `source_of_truth`, đổi `source_id` của tài liệu đang được trỏ tới, tách/gộp meta, đánh dấu tài liệu quan trọng là `deprecated`, đổi chuỗi traceability giữa các tài liệu lớn. Gặp 1 trong 5 → AI sẽ hỏi bạn, không tự áp dụng.

### 4.7 Gỡ tài liệu khỏi wiki

Verb `deregister` — mặc định archive (không xoá thẳng), luôn có điểm dừng hỏi xác nhận trước khi thực hiện.

### 4.8 Thêm knowledge KHÔNG thuộc project (manual chung, tài liệu vendor...)

Verb `add-local-knowledge`. Nói: *"Add Fujitsu manual vào local wiki"*. Đây là index riêng (`local`), không lẫn với wiki của project.

---

## 5. Tình huống: TEST / KIỂM TRA WIKI

Verb `test-lookup` (skill `aiws-wiki`). Nói: *"Test lookup cho các source vừa thêm"*.

2 cách:

- **Self-test** — kiểm tra mọi entry trong index có tự tìm ra chính nó không (bằng id + lookup keys). Dùng ngay sau khi đăng ký hàng loạt.
- **Cases** — đưa 1 bộ câu hỏi mẫu, kiểm tra có ra đúng kết quả mong đợi không.

Kết quả chỉ là **báo cáo + gợi ý** — AI không tự sửa meta/index dựa trên kết quả test, bạn quyết định sửa gì.

**Tìm tài liệu (dùng hằng ngày, không phải test):** verb `lookup`. Nói: *"Tìm trong wiki tài liệu liên quan đến màn đặt phòng F04"*. Nếu tìm không ra, AI sẽ tự nới rộng cách tìm (đổi mode, thử semantic, cuối cùng mới hỏi bạn) — không bao giờ tự kết luận "không có" ngay từ lần tìm đầu.

---

## 6. Skill khác đáng biết

| Skill                           | Dùng khi                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `aiws-agent`                  | Bạn muốn tạo/chạy/nhân bản 1**AI Agent chuyên biệt** (khác AIP — agent là "nhân sự AI" cố định cho 1 vai trò lặp lại, có thể học/nhớ qua nhiều lần chạy). Ví dụ: *"cho agent Reviewer review giúp thiết kế này"*, *"tạo agent mới"*. ⚠️ **Còn beta, chưa test kỹ — chưa nên dùng trong dự án thật nếu chưa tự test và thấy dùng được.** |
| `aiws-util-mail-confirm`      | BrSE/Comtor cần soạn mail/chat xác nhận tiếng Nhật từ nội dung tiếng Việt — có kiểm tra phân loại ISMS trước khi xử lý input.                                                                                                                                                                                                                                                               |
| `aiws-util-personal-notebook` | Ghi lại điều học được / lưu ý cá nhân**chưa đủ chín** để vào wiki chính thức — bước đệm trước khi trở thành wiki candidate thật. ⚠️ **Còn beta, chưa test kỹ — chưa nên dùng trong dự án thật nếu chưa tự test và thấy dùng được.**                                                                                                             |

---

## 7. Bảng lệnh nhanh (cheat-sheet)

| Việc cần làm                             | Gõ lệnh                          | Hoặc nói tự nhiên                                                                                                                                                     |
| ------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cài AIWS                                   | `/aiws-pkg install`              | "Cài AIWS vào dự án này, package ở [path]"                                                                                                                          |
| Nâng cấp AIWS                             | `/aiws-pkg upgrade`              | "Nâng cấp AIWS lên bản mới"                                                                                                                                          |
| Tạo AIP cho task                           | `/aiws-aip create`               | "Tạo AIP để tôi làm [task]"                                                                                                                                          |
| Chạy task                                  | `/aiws-aip run start`            | "Chạy AIP AIP-EXEC-xxx"                                                                                                                                                  |
| Tiếp tục task cũ                         | `/aiws-aip run resume`           | "Tiếp tục AIP-EXEC-xxx"                                                                                                                                                 |
| Xem tiến độ                              | `/aiws-aip run status`           | "Task này đang tới đâu rồi?"                                                                                                                                        |
| Kiểm tra trước khi đóng task           | `/aiws-lint`                     | "Lint AIP và workspace cho mình"                                                                                                                                        |
| Convert file sang Markdown                  | `/aiws-doc-convert-skill`        | "Convert file này sang Markdown"                                                                                                                                         |
| **Build wiki lần đầu (từ đầu)** | **`/aiws-wiki bootstrap`** | **"Bắt đầu xây wiki cho dự án này"**                                                                                                                         |
| Thêm 1 file vào wiki                      | `/aiws-wiki register`            | "Add file này vào wiki"                                                                                                                                                 |
| Thêm cả folder vào wiki                  | `/aiws-wiki register-batch`      | "Đăng ký cả folder này vào wiki"                                                                                                                                    |
| Tạo meta từ source code                   | —                                 | "Chạy build_python_wiki_metas.py cho package này, dry-run trước"                                                                                                      |
| Cập nhật wiki khi source đổi            | `/aiws-wiki refresh`             | "Source đã đổi, cập nhật wiki"                                                                                                                                      |
| Gỡ tài liệu khỏi wiki                   | `/aiws-wiki deregister`          | "Gỡ tài liệu này khỏi wiki"                                                                                                                                          |
| Tìm trong wiki                             | `/aiws-wiki lookup`              | "Tìm tài liệu về [từ khoá]"                                                                                                                                         |
| Test chất lượng wiki                     | `/aiws-wiki test-lookup`         | "Test lookup cho các source vừa thêm"                                                                                                                                  |
| Thêm knowledge ngoài project              | `/aiws-wiki add-local-knowledge` | "Add manual này vào local wiki"                                                                                                                                         |
| Build trang tổng quan wiki                 | `/aiws-wiki build-overview`      | "Tạo trang tổng quan wiki"                                                                                                                                              |
| Build trang onboarding dự án              | `/aiws-wiki build-pages`         | "Tạo trang giới thiệu hệ thống cho dự án"                                                                                                                          |
| Soạn mail confirm tiếng Nhật             | `/aiws-util-mail-confirm`        | "Soạn mail confirm tiếng Nhật cho nội dung này"                                                                                                                      |
| Ghi note cá nhân                          | `/aiws-util-personal-notebook`   | "Ghi note này vào personal notebook"<br />⚠️ **Còn beta, chưa test kỹ — chưa nên dùng trong dự án thật nếu chưa tự test và thấy dùng được.** |

---

## 8. Nguyên tắc vàng (nhớ 3 điều này là đủ)

1. **AIP cố định, workspace là nơi làm thật.** Đừng sửa tay vào AIP giữa lúc chạy task.
2. **Chưa chốt thì để notebook, đừng vội đưa vào wiki.** Khi nghi ngờ, hỏi Claude.
3. **Làm & review trong Markdown trước, export Excel/Word ở bước cuối.** Đừng export sớm rồi sửa tay — AI mất context khi đọc lại.

---

## 9. Đào sâu thêm (đọc khi cần)

- `AIWS_Onboarding_Guide.md` — luồng cài đặt A/B chi tiết cho người hoàn toàn mới.
- `WIKI_INTRO_FOR_EVERYONE.md` — giải thích Wiki cho mọi vai trò (PM/BA/BrSE/dev/QA) + checklist review meta 14 điểm.
- `MEMBER_GUIDE_BUILD_KNOWLEDGE_HUB_FROM_EXISTING_DOCS.md` — quy trình build wiki chi tiết theo từng loại tài liệu (requirement, design, process, checklist...).
- Không hiểu gì → hỏi Claude trực tiếp, luôn kèm từ khoá **AIWS / AIP / Wiki** để AI không nhầm skill khác.

---

_Tài liệu kỹ thuật triển khai — cập nhật theo `AI_Work_System_MVP_v1.2.0_2026-08-20`. Liên hệ team AI推進委員会 khi cần hỗ trợ._
