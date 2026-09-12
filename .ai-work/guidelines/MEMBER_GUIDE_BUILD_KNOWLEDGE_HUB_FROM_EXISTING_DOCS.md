  # Hướng dẫn cho Member — Xây Wiki (Knowledge Hub) từ các tài liệu sẵn có của dự án

  > **Audience:** BrSE, dev, QA, PM, member dự án bất kỳ đang triển khai AIWS Knowledge Hub
  >
  > **Tài liệu liên quan:**
  > - Giới thiệu tổng quan cho mọi member: [WIKI_INTRO_FOR_EVERYONE](./WIKI_INTRO_FOR_EVERYONE.md)
  >
  > Spec canonical chi tiết do AI Work System quản lý nội bộ — khi cần, hỏi AI: _"AIWS có spec nào về [chủ đề]?"_

  ---

  ## 1. Tài liệu này dùng khi nào?

  Dùng khi bạn là member dự án và muốn:

  - Đưa các tài liệu dự án sẵn có (giới thiệu, process, guidelines, rules/checklists, requirements/Q&A, design, source code) vào Knowledge Hub.
  - Hiểu *quy trình chuẩn* của AIWS chứ không tự nghĩ ra cách tổ chức wiki riêng.
  - Biết **5 skill entry-point** đủ để thao tác với wiki, không phải nhớ tool CLI.
  - Biết khi nào nội dung *đáng* đưa vào wiki và khi nào *nên để ở notebook/backlog*.
  - Biết template, mandatory field, Tier annotation, để output của mình lint được, search được, reuse được.

  **Tài liệu này KHÔNG thay thế** các spec/guideline canonical của AIWS. Đây là **lớp hướng dẫn vận hành** giúp member rút ngắn thời gian onboarding.

  **Nên đọc trước:** [WIKI_INTRO_FOR_EVERYONE](./WIKI_INTRO_FOR_EVERYONE.md) — tài liệu giới thiệu Wiki cho mọi audience, đặc biệt phần 4 (5 lệnh skill) và phần 2 (mô hình 2 lớp + `## Related Sources`).

  ---

  ## 2. Khái niệm cốt lõi cần nắm trước khi bắt đầu

  | Khái niệm | Ý nghĩa nhanh |
  |---|---|
  | **Knowledge Hub** | Tên gọi của Wiki trong AIWS — gồm artifact, meta/index, profile, governance, không phải chỉ là một trang web. |
  | **Artifact** | Tài liệu nguồn (Raw Req, Q&A, Req Def, BD, DD, IT Testcase, Meeting Minutes, guideline, checklist, code file…). Không phải mọi artifact đều cần lên Wiki. |
  | **`node_kind`** | Mỗi meta là 1 node thuộc 1 trong 2 kind: `artifact` (mặc định, có file nền) hoặc `object` (entity logic, KHÔNG file nền). Cùng 1 index, cùng `## Related Sources`. |
  | **Object node** | Node `node_kind=object` = entity tái dùng (function/screen/api/batch/table/module/concept), `artifact_locator=__OBJECT__`. **Hand-authored** (AI chỉ suggest). KHÔNG có store/field riêng của retired record (xem `Knowledge_Object_Model_Spec_MVP` §8) — là pointer, không phải container. Xem §7.8. |
  | **Artifact Type Taxonomy** | 14 `artifact_type` chuẩn (nhãn **classifier**): `requirement_definition`, `basic_design`, `detailed_design_fe/api/be/combined`, `test_case`, `unit_test_spec`, `screen_mockup`, `db_schema`, `api_manual`, `methodology_spec`, `meeting_note`, `legacy_design` (+ `_unknown` sentinel). Enum **có thể extend theo project**. Không tự đặt bừa. |
  | **`source_type` (spine)** | Xương sống thô + **lint authority** (validate bởi `lint_wiki`). `artifact_type` **→** `source_type` là **many-to-one** (vd `detailed_design_*` → `detail_design`; `test_case` → `test_spec`). Profile-extensible. Là field meta bắt buộc, **khác** `artifact_type`. |
  | **Wiki Source Meta (Layer 1)** | 1 file Markdown nhẹ mô tả 1 artifact: summary, lookup keys (có Tier), hints, cautions, `## Related Sources`… Đây là **đơn vị tri thức** của Wiki (mô hình 2-layer). |
  | **`## Related Sources`** | Section trong từng meta liệt kê các source liên quan kèm **role** có hướng. Cơ chế điều hướng cross-artifact; không project vào index. |
  | **Index** | Projection (sinh tự động) của các Layer-1 meta → `index.jsonl`. Lookup surface; KHÔNG sửa tay. |
  | **Source Interpretation Profile** | Khuôn dùng để build meta cho 1 loại artifact (vd `design_doc.yml`, `methodology_spec.yml`). |
  | **Project Mapping Pattern (PMP)** | Khuôn dùng lại cho **một format cụ thể trong project**. Lưu ở `profiles/mapping_patterns/PMP-<id>.yml`. |
  | **Canonical Slot** | Đầu mục chuẩn của AIWS để chuẩn hoá nội dung tài liệu (vd với DD: `ui_ux_behavior`, `api_contract`, `be_processing_logic`…). |
  | **Lookup Key Tier (T1/T2/T3)** | Tier của từ khoá — T1 ×3 (ID), T2 ×1.5 (domain term), T3 ×1.0 (label). |
  | **Candidate** | Phát hiện *có thể* đưa lên Wiki. AI/người chỉ được *suggest candidate*, không tự promote. |
  | **CR (Change Request)** | Cấu trúc chính thức để chuyển candidate → canonical update. |
  | **Promotion Gate** | 5 trigger HARD STOP — cần CR + Wiki Manager (xem mục 11). |
  | **Governance** | Flow tối thiểu: `candidate → CR → Wiki Manager duyệt → AI/người apply`. |
  | **Knowledge Class** | Phân loại: `source_of_truth` > `curated` > `reference` > `history`. |
  | **Confirmed / Inferred / Unresolved** | 3 trạng thái bắt buộc tách khi hiểu artifact. |
  | **Skill Router** | Skill đóng vai trò lễ tân, delegate sang skill nội bộ phù hợp. |

  ---

  ## 3. 5 skill entry-point — member chỉ cần biết những lệnh này

  AIWS có **router pattern**: member **chỉ tương tác với 5 skill entry-point**. Các skill còn lại là internal — router tự gọi khi cần.

  ### 3.1. Bảng skill cheatsheet

  | Skill | Khi nào dùng | Câu nói tự nhiên với AI |
  |---|---|---|
  | **`/aiws-wiki register`** | Thêm tài liệu mới vào Wiki (1 file / cả folder / tạo PMP) | "Add file này vào wiki", "đăng ký toàn bộ folder design", "tạo PMP cho format DD Fujitsu" |
  | **`/aiws-wiki refresh`** | Cập nhật khi tài liệu/format thay đổi (kể cả `## Related Sources`) | "Source đã đổi, cập nhật wiki", "cập nhật related sources cho SRC-DD-F04", "PMP đã drift, refresh" |
  | **`/aiws-wiki lookup`** | Tìm trong Wiki | "Lookup booking search", "tìm tài liệu về F04" |
  | **`/aiws-wiki test-lookup`** | Verify wiki lookup chất lượng | "Test wiki lookup cho 5 source mới build", "lookup có tìm ra func_F04 không" |

  ### 3.2. Skill router routing — cách AI tự nhận biết case

  **`/aiws-wiki register` (router ADD) — 3 CASE:**

  ### Khi nào dùng `/aiws-wiki bootstrap`

  Dùng **một lần** khi project chưa có Knowledge Hub. Không dùng để maintenance wiki đã tồn tại; khi đó dùng refresh/sync flow.

  Trước bootstrap, HUMAN phải chốt scope, purpose/task kinds, project shape và object-node gate; project multi-system phải chọn rõ `--system`. Bootstrap tạo **fixed 12-step AIP (STEP-00..STEP-11)**, không tự thêm/bớt step và không tự author/free-form AIP. Flow tốt: inventory → sample-first meta/profile → test-lookup → PMP/mass build → spot-check relations; duy trì BUILD LOG và LESSON LOG. AIP phải lint sạch và được HUMAN review trước `run start`.

  Lookup chỉ route nguồn, không thay source verification. Candidate vẫn đi candidate → CR → reviewer approval → apply; bootstrap không tự promote Wiki/canonical content.

  ```
  User nói / cung cấp                                         → CASE
  ──────────────────────────────────────────────────────────────────────────────
  File path (1 file lẻ)                                        → CASE 1: single-file flow
  Folder path / nhiều file                                     → CASE 2: delegate batch
  "tạo PMP" / "save pattern" (reactive sau sample-first)       → CASE 3: build PMP
  "tạo profile/PMP trước", "setup mapping" (proactive)         → CASE 3: build PMP (proactive mode)
  ```

  **CASE 1 — Single-file flow**
  - **Khi nào:** 1 file lẻ bất kỳ — Markdown, Excel, PDF, Word.
  - **Flow key:** STAGE 1: convert binary → MD (nếu cần) · STAGE 2: classify `artifact_type` — **HUMAN confirm bắt buộc** · STAGE 3: build meta với Lookup Keys + Tier + **scaffold `## Related Sources`** (tool tự sinh các role slot dạng TODO để bạn điền target source liên quan).
  - **Lưu ý:** File binary được router tự convert, không cần chuẩn bị trước. Đây là flow cơ bản nhất — mọi case khác đều gọi lại flow này bên trong.

  **CASE 2 — Batch (delegate sang `/aiws-wiki register-batch`)**
  - **Khi nào:** Folder hoặc danh sách nhiều file cùng lúc.
  - **Flow key:** Scan folder → nhóm theo `artifact_type` → áp dụng PMP nếu đã có → gọi CASE 1 cho từng file theo wave. Mỗi meta được scaffold `## Related Sources`.
  - **Lưu ý:** **Không nên batch ngay khi chưa có PMP.** Làm sample-first (CASE 1 với 2–3 file) + tạo PMP (CASE 3) trước — nếu không, phát hiện profile sai sau khi build 80 meta sẽ phải làm lại từ đầu.
  - **Flow:** Batch build Layer-1 meta + index. Có **3 HUMAN Gate**: plan review, sample review, PMP creation.

  **CASE 3 — Build PMP (Project Mapping Pattern)**

  Delegate sang `/aiws-wiki build-pattern`. Có **2 chế độ trigger**:

  - **Reactive (AI suggest, sau sample-first):** Sau khi ≥ 2–3 meta cùng format đã confirm, AI nhận thấy format ổn định và *tự đề xuất* tạo PMP. AI propose format signature + canonical slot mapping → HUMAN confirm → tạo `PMP-<id>.yml` (`reuse_confidence: high` sau khi `/aiws-wiki test-lookup` pass).
  - **Proactive (user chủ động, trước khi add):** User yêu cầu setup profile/PMP trước. Xem chi tiết §3.2.1.

  **`/aiws-wiki refresh` (router UPDATE) — 2 CASE:**

  ```
  User nói / cung cấp                            → CASE
  ──────────────────────────────────────────────────────────────────────
  File path + "changed/updated/stale"            → CASE 1: meta refresh
  "cập nhật related sources"                      → CASE 1 (sửa ## Related Sources trong meta)
  "format đã đổi" / "PMP stale" / "drift"        → CASE 2: PMP refresh
  ```

  > Để cập nhật quan hệ cross-artifact: sửa `## Related Sources` của meta liên quan qua CASE 1 (meta refresh).

  ### 3.2.1. CASE 3 (proactive) — User chủ động tạo Profile / PMP trước khi add tài liệu

  > **Đây là chế độ trigger proactive của CASE 3**, khác với chế độ reactive (AI suggest sau sample-first).

  **Khi nào dùng chế độ proactive:**

  | Tình huống | Ví dụ |
  |---|---|
  | User đã biết format từ dự án cũ hoặc template quen thuộc | "Format DD Fujitsu này tôi đã làm nhiều, tôi muốn define PMP trước" |
  | User muốn review canonical slot mapping *trước* khi AI tự suy | "Tôi muốn confirm mapping trước khi batch 50 file" |
  | Team quy định "setup profile trước, batch sau" | BrSE owner thiết lập PMP cho toàn team dùng chung |
  | User có sample đại diện và muốn build PMP ngay không qua sample-first | "Đây là 3 file sample, build PMP từ đây trước đi" |

  **Flow khi vào chế độ proactive:**

  ```
  User: "Tạo profile/PMP trước cho loại tài liệu X"
            │
            ▼
  AI hỏi: "Bạn có sample artifact đại diện không?"
            │
      ┌─────┴──────┐
      │ Có sample  │ Không có sample
      ▼            ▼
  AI analyze   AI dùng common understanding
  sample →     + user mô tả format →
  đề xuất      draft profile/PMP
  mapping      (reuse_confidence: medium)
      │            │
      └─────┬──────┘
            ▼
    HUMAN review & confirm mapping
            │
            ▼
    AI tạo file:
    - profiles/<type>.yml          ← Source Interpretation Profile
    - profiles/mapping_patterns/
      PMP-<id>.yml                  ← Project Mapping Pattern
            │
            ▼
    Profile/PMP sẵn sàng →
    /aiws-wiki register sau đó load và áp dụng ngay
  ```

  **Khác biệt reactive vs proactive (đều là CASE 3):**

  | | Reactive | Proactive |
  |---|---|---|
  | **Ai khởi động** | AI suggest sau khi format đã ổn định | User chủ động yêu cầu |
  | **Thời điểm** | Sau sample-first, khi meta đã build xong | Trước khi add tài liệu |
  | **Sample bắt buộc** | Có (≥ 2–3 sample đã build meta) | Không bắt buộc — có thể từ mô tả |
  | **`reuse_confidence`** | `high` (đã verify) | `medium` nếu không có sample, `high` sau khi test pass |

  **Lưu ý quan trọng:**

  - Nếu không có sample: ghi `reuse_confidence: medium` trong PMP → sau khi test với file thực tế và `/aiws-wiki test-lookup` pass → nâng lên `high`.
  - Profile (`<type>.yml`) là khuôn canonical AIWS — nếu type mới hoàn toàn (chưa có trong taxonomy), **hỏi Wiki Manager** trước khi tạo.
  - PMP (`PMP-<id>.yml`) là project-specific — BrSE có thể tạo tự do hơn, nhưng vẫn cần confirm qua CASE 3 (chế độ proactive) flow.
  - Sau khi profile/PMP được tạo proactively, Step 4 trong Flow tổng quát (§6) sẽ được bỏ qua hoặc fast-track khi mass build.

  ---

  ### 3.3. 5 skill internal — bạn KHÔNG gọi trực tiếp

  Để biết (không cần nhớ): `aiws-wiki build-meta`, `aiws-wiki register-batch` (batch), `aiws-wiki build-pattern`, `aiws-wiki refresh-meta`, `aiws-wiki refresh-pattern`. Router gọi tự động.

  ### 3.4. Lưu ý quan trọng

  - Member **không cần nhớ argument CLI**. Nói chuyện tự nhiên bằng tiếng Việt/Anh, router parse intent.
  - Vẫn có thể dùng tool CLI trực tiếp (`python .ai-work/tooling/lookup_wiki_source.py …`) khi cần — nhưng skill ưu tiên hơn.
  - Khi AI vào CASE 1 của `/aiws-wiki register`, có **HUMAN gate** ở STAGE 2 (classify artifact_type) — bạn cần confirm/correct trước khi AI build meta.

  ---

  ### 3.5. Sample prompts — câu lệnh mẫu

  > **Lưu ý:** Không cần gõ đúng từng chữ — AI hiểu intent. Dưới đây là các mẫu tham khảo.

  #### Thêm vào wiki (`/aiws-wiki register`)

  **1 file lẻ — artifact đã là Markdown:**
  ```
  "Add file docs/design/F04_DD_FE.md vào wiki"
  "Đăng ký tài liệu docs/requirements/Req_Def_v2.md vào Knowledge Hub"
  "Thêm coding-guideline.md vào wiki — đây là coding guideline của dự án"
  ```

  **1 file binary (Excel, PDF, Word) — router tự convert:**
  ```
  "Add file này vào wiki, đây là screen design Excel của F04: docs/F04_screen_layout.xlsx"
  "Đăng ký tài liệu PDF này vào wiki: docs/project_overview_kickoff.pdf"
  "Thêm vào wiki: docs/checklists/release_checklist.xlsx — đây là release checklist"
  ```

  **Cả folder (batch):**
  ```
  "Thêm toàn bộ tài liệu design trong folder docs/design/cb-ordering/ vào wiki"
  "Đăng ký hết tài liệu requirement trong folder requirements/phase1/ vào wiki"
  "Add tất cả file trong docs/guidelines/ vào wiki"
  ```

  **Liên kết các artifact cùng entity (qua `## Related Sources`):**
  ```
  "Trong meta SRC-DD-CB01001-FE, thêm related sources tới BD, DD-API, DD-BE cùng function CB01001"
  "Điền ## Related Sources cho func_F04: BD (upstream_input), test case (downstream_target)"
  ```
  > Section `## Related Sources` đã được scaffold sẵn khi build meta — bạn chỉ cần điền target source_id + role, hoặc nhờ AI điền rồi review.

  **Tạo Project Mapping Pattern (reactive — sau sample-first):**
  ```
  "Tạo PMP cho format DD Fujitsu dựa trên 3 samples vừa confirm"
  "Save format pattern cho template Detail Design JP này thành PMP"
  ```

  **Tạo Profile / PMP proactively TRƯỚC khi add tài liệu (CASE 3 proactive):**
  ```
  "Tạo profile cho loại tài liệu Detail Design JP Fujitsu trước khi add"
  "Setup PMP cho format BD của dự án này — tôi sẽ mô tả cấu trúc heading cho bạn"
  "Build PMP từ sample này trước: docs/design/F04_DD_FE.md — tôi muốn review mapping trước khi batch"
  "Tôi muốn define canonical slot mapping cho format DD này trước, sau đó mới đăng ký hàng loạt"
  "Tạo PMP từ 3 sample sau đây, chưa cần add vào wiki: [file1, file2, file3]"
  "Chưa cần add tài liệu — chỉ cần tạo profile + PMP cho format requirement này trước"
  ```

  ---

  #### Cập nhật wiki (`/aiws-wiki refresh`)

  **Source file đã thay đổi — cập nhật meta Layer 1:**
  ```
  "File F04_DD_FE.md đã được update lên v3, cập nhật wiki meta"
  "Source SRC-DD-CB01001-FE đã thay đổi — refresh meta"
  "Tài liệu Req_Def_v2.md vừa chốt thêm 2 acceptance criteria, sync wiki"
  ```

  **Cập nhật quan hệ cross-artifact (`## Related Sources` trong meta):**
  ```
  "Trong SRC-DD-F04-FE, thêm related source tới testcase SRC-ITTC-F04 (role downstream_target)"
  "Cập nhật ## Related Sources cho SRC-DD-CB01001-FE — có function liên quan mới CB02001 (role related)"
  ```

  **Format / PMP đã drift:**
  ```
  "Format DD Fujitsu vừa thay đổi cấu trúc heading, refresh PMP-DD-FUJITSU-V1"
  "PMP của template detail design bị outdated sau khi format đổi, cập nhật lại"
  ```

  ---

  #### Xóa / Archive / Deprecate khỏi wiki

  > ⚠️ **Quan trọng:** Xóa hoặc deprecate KHÔNG phải thao tác nhẹ. Nếu gặp Promotion Gate trigger (artifact đang được tham chiếu, hoặc `knowledge_class: source_of_truth`) → **phải tạo CR + Wiki Manager duyệt** trước. Xem §11.

  **Archive tài liệu cũ (superseded):**
  ```
  "Tài liệu SRC-BD-F03-V1 đã bị thay thế bởi SRC-BD-F03-V2, cần mark superseded"
  "Q&A-2026-03-15 đã được phản ánh vào Req Def, set status reflected"
  ```

  **Deprecate tài liệu không còn dùng:**
  ```
  "Guideline GUIDE-JAVA-V1 đã bị thay thế hoàn toàn bởi GUIDE-JAVA-V2 — deprecate đi"
  "Process doc cũ về deploy đã outdated, cần mark deprecated và trỏ sang version mới"
  ```

  **Lưu ý:**
  - AI sẽ check Promotion Gate trước khi thực hiện.
  - Nếu có trigger → AI DỪNG, thông báo cần CR + Wiki Manager.
  - Không có lệnh "xóa cứng" (hard delete) meta — chỉ `deprecated` + `superseded_by` để giữ audit trail.

  ---

  ## 4. Nguyên tắc nền tảng — phải đọc trước khi đụng vào wiki

  ### 4.1. Wiki-first, không phải Wiki-only

  Khi cần thông tin: tra Knowledge Hub trước. Nhưng nếu meta không đủ thì *mở source artifact* để verify. Meta route, source verify.

  ### 4.2. Meta-first, không inline source

  Không copy toàn bộ nội dung tài liệu vào meta. Meta chỉ chứa: summary 1–2 dòng, knowledge targets, lookup keys (có Tier), hints, cautions, locator trỏ về source.

  ### 4.3. Sample-first trước khi mass build

  Chọn 2–3 artifact đại diện cùng format → build meta → `/aiws-wiki test-lookup` verify → fix profile → mới mass build. Sau khi format ổn định → tạo PMP để reuse cho batch lớn.

  ### 4.4. 1 file = 1 artifact-level meta (Rule M-1)

  Một file source ↔ một meta file (áp dụng cho `node_kind=artifact` — mặc định). Đừng gom 5 file vào 1 meta hoặc tách 1 file ra 3 meta (trừ khi đã consensus chia object FE/API/BE — xem mục 7.6).

  > **Ngoại lệ object-kind:** meta `node_kind=object` (function/screen/table…) là **1 meta / entity logic, KHÔNG có file nền** (`artifact_locator=__OBJECT__`) → không áp M-1 "1 file". Xem §7.8.

  ### 4.5. Tách rõ Confirmed / Inferred / Unresolved

  Khi đưa nội dung vào meta (kể cả `## Related Sources`): phần *chắc chắn* (có trong source), phần *suy luận* (AI/người tự nghĩ ra), phần *chưa rõ* phải tách. Không merge inference vào confirmed.

  ### 4.6. Candidate-only — không tự promote canonical

  Dù bạn (hoặc AI) thấy nội dung *cực kỳ* đáng lên wiki: vẫn phải qua flow `candidate → CR → Wiki Manager`. Không tự sửa canonical wiki.

  ### 4.7. Promotion Gate — HARD STOP cho 5 thay đổi quan trọng

  Khi gặp 1 trong 5 trigger sau, AI/người **dừng lại**, tạo CR riêng:

  1. Set `knowledge_class: source_of_truth`.
  2. Đổi `source_id` của meta đã được tham chiếu.
  3. Split hoặc merge meta records.
  4. Đánh dấu artifact quan trọng là `deprecated`.
  5. Đổi traceability chain (`related_artifact_refs` / `## Related Sources`) giữa các artifact lớn.

  Lý do: 5 việc này ảnh hưởng diện rộng, không thể "lightweight update".

  ### 4.8. Resolved ≠ Reflected ≠ Superseded

  Với tài liệu supplemental (Q&A, findings, open point…):
  - **Resolved**: đã có câu trả lời/quyết định.
  - **Reflected**: đã được phản ánh vào tài liệu chính (Req Def, DD…).
  - **Superseded**: đã bị thay thế bởi version mới.

  Ba trạng thái này độc lập, không suy ra nhau.

  ### 4.9. Không edit index thủ công

  `index.jsonl` / `index.local.jsonl` chỉ được sinh bởi tool. Sửa meta → rebuild → không sửa index trực tiếp.

  ### 4.10. Binary phải convert sang MD trước

  PDF/DOCX/Excel: convert sang Markdown (router CASE 1 STAGE 1 tự xử lý) → build meta trên file MD → giữ `original_artifact_locator` trỏ về bản gốc + ghi `source_representation_status` (sufficient / partial / needs_review).

  ### 4.11. Truth > Project Wiki > Local Wiki > Common Wiki > History

  Khi có mâu thuẫn nội dung giữa các lớp: tin Truth trước (SOP_MASTER, AI_WORK_CONTRACT). Wiki không override Truth.

  ---

  ## 5. Cấu trúc Knowledge Hub trong project

  ```
  project-root/
  ├── .ai-work/
  │   ├── truth/                                    ← SOP, contract (Truth, KHÔNG phải wiki)
  │   ├── wiki/                                     ← Project-local wiki outputs
  │   │   ├── project_profile/
  │   │   ├── meta_build_outputs/                   ← Output trung gian
  │   │   ├── aip_customizations/
  │   │   └── rollout_notes/
  │   ├── wiki_sources/                             ← Runtime layer — AI thực sự tra cứu
  │   │   ├── meta/<family>/SRC-...md               ← Layer 1: artifact meta (gồm ## Related Sources)
  │   │   ├── profiles/                             
  │   │   │   ├── <type>.yml                        ← Source Interpretation Profile
  │   │   │   └── mapping_patterns/
  │   │   │       └── PMP-<id>.yml                  ← Project Mapping Pattern
  │   │   ├── index.jsonl                           ← Index (projection của Layer 1, sinh tự động)
  │   │   ├── index.local.jsonl                     ← Local knowledge index
  │   │   ├── _staging/                             ← Converted binary→MD temp
  │   │   └── HOW_TO_CREATE_LOCAL_KNOWLEDGE.md
  │   ├── procedural/skills/                        ← skills
  │   └── tooling/                                  ← Python scripts (gọi qua skill)
  │
  ├── product/                                       ← Tài liệu canonical của project
  │   ├── methodology/...
  │   └── wiki_guidelines/...
  │
  └── (source code, design docs, requirements... ở folder dự án riêng)
  ```

  **Quy ước cho member:**
  - Chỉ tạo meta trong `.ai-work/wiki_sources/meta/<family>/` (qua `/aiws-wiki register`).
  - `## Related Sources` được scaffold sẵn trong meta — chỉ điền/sửa target source_id + role, không tạo file riêng.
  - PMP không tạo tay ngay — đợi sample-first xong, AI suggest (CASE 3 reactive).
  - KHÔNG sửa tay `index.jsonl`, `index.local.jsonl`.
  - KHÔNG đọc/sửa file trong `temp/`, `.ai-work/logs/`.

  ---

  ## 6. Flow tổng quát: từ tài liệu sẵn có → Knowledge Hub

  > Áp dụng cho mọi loại tài liệu trong dự án. Chi tiết riêng cho từng loại ở mục 7.

  ```
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 0: Project profile có chưa?                                │
  │   → Nếu chưa: setup project_profile (artifact types có,         │
  │     deliverable vs working, knowledge_class mặc định)           │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 1: Inventory tài liệu                                      │
  │   → Liệt kê tài liệu hiện có, gắn artifact_type (14 loại),      │
  │     deliverable vs working, wiki-eligible vs not                │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ [Optional — Fast path] Bước 1.5: Tạo Profile / PMP trước        │
  │   → Dùng khi user chủ động yêu cầu setup trước khi add          │
  │   → /aiws-wiki register CASE 3 (proactive mode)              │
  │     → Có sample → AI analyze → HUMAN confirm → tạo profile/PMP  │
  │     → Không có sample → user mô tả format → AI draft → HUMAN    │
  │       review kỹ hơn (reuse_confidence: medium)                  │
  │   → Nếu đã làm bước này → Bước 2 và Bước 4 fast-track           │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 2: Sample-first — chọn 2-3 file đại diện                   │
  │   → /aiws-wiki register <file>                                │
  │     STAGE 1: convert binary (nếu cần)                           │
  │     STAGE 2: classify artifact_type (HUMAN confirm)             │
  │             ↳ Nếu profile/PMP đã tạo ở Bước 1.5 → skip         │
  │                  classify / load PMP tự động                    │
  │     STAGE 3: build meta (Lookup Keys + Tier) +                  │
  │              scaffold ## Related Sources                        │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 3: Verify lookup quality                                   │
  │   → /aiws-wiki test-lookup mode A (self-test)                        │
  │   → Nếu FAIL: fix Lookup Keys / Tier annotation                 │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 4: Format ổn định? → tạo PMP                                │
  │   → Nếu đã tạo PMP ở Bước 1.5 (CASE 3) → kiểm tra và xác       │
  │     nhận reuse_confidence (nâng high nếu test pass)             │
  │   → Nếu chưa có PMP → /aiws-wiki register CASE 3 (AI suggest) │
  │     → tạo PMP-<id>.yml để reuse cho batch                       │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 5: Mass build                                              │
  │   → /aiws-wiki register <folder>  (CASE 2, batch)             │
  │   → Mỗi file áp dụng PMP đã tạo                                  │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 6: Điền ## Related Sources cho meta có quan hệ             │
  │   → Trong từng meta, điền target source_id + role:              │
  │       companion_design (FE/API/BE cùng function),               │
  │       upstream_input (BD), downstream_target (testcase)…        │
  │   → Section đã được scaffold tự động ở Bước 2/5 → chỉ cần điền  │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 7: Traceability + Related Sources + supplemental status   │
  │   → related_artifact_refs (phẳng) + ## Related Sources (role): │
  │     Raw Req → Q&A → Req Def → BD → DD → Testcase                │
  │   → Q&A/findings: status, reflection_status, reflected_to,      │
  │     superseded_by                                               │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 8: Final verify                                            │
  │   → /aiws-wiki test-lookup mode C, prompt mẫu:                      │
  │     "list tài liệu cần thiết cho task [tên task],               │
  │      ghi rõ cách tìm các tài liệu đó."                         │
  │   → python .ai-work/tooling/lint_wiki.py (nếu chưa được skill   │
  │     gọi giúp)                                                   │
  └──────────────────────────────┬──────────────────────────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ Bước 9: Governance (nếu canonical update / promotion trigger)   │
  │   → candidate → CR → Wiki Manager review → AI/người apply       │
  └─────────────────────────────────────────────────────────────────┘
  ```

  ---

  ## 7. Hướng dẫn theo từng loại tài liệu

  ### 7.0. Nguyên tắc chọn lọc — loại tài liệu nào nên đưa vào wiki?

  #### Nguyên tắc cốt lõi

  > **Bất kỳ tài liệu nào mà BrSE/member cần dùng để thực hiện task trong dự án → đều nên đưa vào Knowledge Hub.**

  Lý do: Knowledge Hub tồn tại để giúp AI và member không phải tìm lại từ đầu mỗi khi cần thông tin. Nếu bạn từng tự hỏi "cái này ở đâu nhỉ?" hoặc phải đi hỏi người khác — đó là dấu hiệu nội dung đó nên có trong wiki.

  #### 7 loại tài liệu nên đưa vào wiki

  | # | Loại tài liệu | Ví dụ cụ thể | Nên đưa vào? |
  |---|---|---|---|
  | 1 | **Tài liệu giới thiệu dự án** | Project overview, kick-off deck, business context, stakeholder map, project charter | ✅ Nên — giúp AI và member mới hiểu bối cảnh |
  | 2 | **Tài liệu về các process** | Development process, release process, code review process, defect triage, escalation SOP | ✅ Nên — được tra cứu lặp lại mỗi milestone |
  | 3 | **Tài liệu guidelines sẵn có** | Coding guideline, naming convention, Git workflow, branching rule, commit message format, test guideline | ✅ Nên — BrSE và dev tra hàng ngày |
  | 4 | **Common rules / Checklists** | Definition of Done, code review checklist, release checklist, security checklist | ✅ Nên — dùng cuối mỗi sprint/release |
  | 5 | **Requirements / Input của khách hàng** | Raw Req, Q&A, Requirement Definition, BRD, change request, Meeting Minutes liên quan requirement | ✅ **Ưu tiên cao nhất** — backbone của traceability |
  | 6 | **Tài liệu design** | Basic Design, Detail Design (FE/API/BE), DB design, API spec, Architecture diagram, UI mockup spec | ✅ Nên — tra mỗi khi code, review, test |
  | 7 | **Source code** | Java class, Python module, React component, SQL migration, Terraform module | ⚠️ Hiện AIWS chưa hỗ trợ tốt cho source code |

  #### Decision table — Nên hay Không nên?

  | Tình huống | Quyết định |
  |---|---|
  | BrSE/member cần đọc tài liệu này ≥ 1 lần khi làm task | ✅ Nên đưa vào |
  | Tài liệu được hỏi lại nhiều lần trong team | ✅ Nên đưa vào |
  | Tài liệu là nguồn sự thật cho 1 decision/requirement/design | ✅ Nên đưa vào (với `knowledge_class` phù hợp) |
  | AI cần tài liệu này để hỗ trợ task review/testcase/code | ✅ Nên đưa vào |
  | Tài liệu đang là draft thay đổi hàng ngày, chưa chốt | ❌ Chưa — đợi chốt rồi build meta |
  | Email/Slack rời rạc chưa được tổng hợp | ❌ Chưa — tổng hợp thành Q&A artifact trước |
  | Personal note, scratch pad của member | ❌ Không — không phải project knowledge |
  | Code generated tự động (Lombok, protobuf…) | ❌ Không — noise thuần tuý |
  | 3 bản tài liệu cùng nội dung (trùng lặp) | ⚠️ Disambiguate trước — chọn canonical, archive còn lại |
  | Source code phổ thông (getter/setter, config boilerplate) | ❌ Không — chỉ build meta cho public API/core domain/utility reuse cao |

  #### Thứ tự ưu tiên khi bắt đầu

  Nếu Knowledge Hub mới hoàn toàn, build theo thứ tự sau để nhanh có giá trị nhất:

  ```
  1️⃣  Requirements / Input khách hàng   ← backbone traceability
  2️⃣  Design (BD, DD)                    ← AI dùng nhiều nhất
  3️⃣  Process & Guidelines               ← tra hàng tuần
  4️⃣  Tài liệu giới thiệu dự án         ← context cho AI hiểu scope
  5️⃣  Checklists / Rules                 ← cuối sprint/release
  6️⃣  Source code (chọn lọc)            ← khi cần link Code ↔ Design
  ```

  ---

  ### Với mỗi loại, member cần xác định 6 thứ:
  1. `artifact_type` trong **Artifact Type Taxonomy 14 loại**
  2. `profile_id` phù hợp (router tự suggest top-3 khi đăng ký)
  3. Canonical slot mapping điển hình
  4. Mandatory fields cho meta (có Tier annotation)
  5. `## Related Sources` — các source liên quan + role (nếu thuộc 1 entity có nhiều artifact)
  6. Link/relation thường có (`related_artifact_refs` phẳng cho traceability)

  ### 7.1. Tài liệu giới thiệu dự án

  **Ví dụ:** Project overview, project charter, kick-off slide, business context, stakeholder map.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `project_overview` *(project extension — không có trong enum canonical §2)* |
  | `source_type` (spine) | `canonical_doc` |
  | `knowledge_class` | `reference` (đa số) hoặc `curated` nếu là source xác định scope/định nghĩa stakeholder |
  | `profile_id` gợi ý | `methodology_guide` hoặc tạo `project_intro` |
  | Canonical slot | `project_purpose`, `project_scope`, `stakeholders`, `business_context`, `success_criteria`, `out_of_scope` |
  | Tier T1 ví dụ | tên project, project code |
  | Tier T2 ví dụ | tên khách hàng, domain (banking/healthcare…), tên hệ thống chính |
  | `## Related Sources` | thường ít — có thể trỏ tới `process_doc`, `req_def`, governance (role `related`/`output_template`) |
  | Link thường có | trỏ tới `process_doc`, `req_def`, `governance` doc |

  **Anti-pattern:**
  - Build meta cho mọi version kick-off deck → tạo noise.
  - Inline cả bullet list "Goals" của project vào meta → vi phạm M-3.

  **Sample prompts:**
  ```
  # Thêm vào wiki
  "Add file docs/project-overview.md vào wiki — đây là tài liệu giới thiệu dự án"
  "Đăng ký kick-off-presentation.pdf vào wiki — slide giới thiệu dự án cho khách hàng"

  # Cập nhật
  "File project-overview.md vừa update thêm scope phase 2, sync wiki meta"

  # Archive khi tài liệu cũ bị thay
  "Tài liệu project-charter-v1.md đã bị thay thế bởi v2, mark superseded"
  ```

  ### 7.2. Tài liệu process của dự án

  **Ví dụ:** Development process, release process, code review process, defect triage process, escalation process.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `process_doc` *(project extension)* |
  | `source_type` (spine) | `process_guideline` |
  | `knowledge_class` | `curated` hoặc `source_of_truth` nếu được PM/SOP_MASTER tham chiếu |
  | `profile_id` gợi ý | `process_doc` (tạo mới nếu chưa có) |
  | Canonical slot | `process_purpose`, `trigger`, `steps`, `actors_responsibilities`, `inputs`, `outputs`, `exit_criteria`, `exceptions`, `escalation` |
  | Tier T1 | tên process chính (e.g. `RELEASE_PROCESS_V2`) |
  | Tier T2 | role liên quan, tool, milestone tên |
  | `## Related Sources` | trỏ tới guideline/checklist/template liên quan (role `output_template`/`related`) |
  | Link thường có | trỏ tới `guideline`, `checklist`, `template`, `role_definition` |

  **Lưu ý:** Process có version → khi đổi version, dùng `/aiws-wiki refresh` CASE 1 thay vì tạo meta mới. Nếu là **Promotion trigger** (vd đổi knowledge_class lên source_of_truth) → STOP, qua CR.

  **Sample prompts:**
  ```
  # Thêm vào wiki
  "Add file docs/processes/release-process-v2.md vào wiki"
  "Đăng ký toàn bộ tài liệu process trong folder docs/processes/ vào wiki"

  # Cập nhật
  "Release process vừa bổ sung bước hotfix sau sprint 5, cập nhật wiki meta"
  "File deployment-process.md đã được update, sync wiki"

  # Archive / deprecate
  "Process DEPLOY-V1 đã bị thay thế hoàn toàn bởi DEPLOY-V2, deprecate meta cũ"
  ```

  ### 7.3. Tài liệu guidelines sẵn có

  **Ví dụ:** Coding guideline, Git workflow guideline, naming convention, branching rule, commit message format, test guideline.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `guideline` *(project extension)* |
  | `source_type` (spine) | `process_guideline` |
  | `knowledge_class` | `curated` |
  | `profile_id` gợi ý | `methodology_guide` (đã có) |
  | Canonical slot | `guideline_purpose`, `scope`, `rules`, `examples`, `rationale`, `exceptions`, `related_guidelines` |
  | Tier T1 | tên guideline ID (e.g. `GUIDE-CODING-JAVA-V1`) |
  | Tier T2 | ngôn ngữ/framework (Java, Spring, React…), tool, anti-pattern keyword |
  | Link thường có | trỏ tới `checklist`, `template`, source_code mẫu |

  **Sample prompts:**
  ```
  # Thêm vào wiki
  "Add file docs/guidelines/coding-guideline-java.md vào wiki"
  "Đăng ký toàn bộ guideline trong folder docs/guidelines/ vào wiki"

  # Cập nhật
  "Coding guideline Java vừa bổ sung rule về exception handling, refresh meta"
  "Git-workflow-guide.md đã được cập nhật quy trình rebase, sync wiki"

  # Archive
  "Guideline GUIDE-JAVA-V1 đã bị thay thế bởi V2, mark superseded và trỏ sang version mới"
  ```

  ### 7.4. Common rules / Checklists

  **Ví dụ:** Definition of Done, code review checklist, release checklist, security checklist, accessibility checklist.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `checklist` *(project extension)* |
  | `source_type` (spine) | `process_guideline` / `process_template` |
  | `knowledge_class` | `curated` |
  | `profile_id` gợi ý | `checklist` (tạo mới nếu chưa có) |
  | Canonical slot | `applies_to`, `entry_condition`, `items`, `evidence_required`, `owner`, `exceptions` |
  | Tier T1 | tên checklist ID |
  | Tier T2 | tên milestone (release, code review…), area (security, performance…), role |
  | Link thường có | trỏ tới `process_doc`, `guideline` |

  **Lưu ý:** Checklist dễ duplicate. Trước khi build: **disambiguate** — chọn 1 bản canonical, archive các bản trùng.

  **Sample prompts:**
  ```
  # Thêm vào wiki
  "Add file docs/checklists/release-checklist.md vào wiki — đây là release checklist"
  "Đăng ký release-checklist.xlsx vào wiki — checklist release cuối sprint"

  # Cập nhật
  "Release checklist vừa thêm 3 item security mới, cập nhật wiki meta"
  "Code-review-checklist.md đã update sau retrospective, sync wiki"

  # Archive
  "Checklist DoD-v1 đã bị thay bởi DoD-v2, deprecate meta cũ"
  ```

  ### 7.5. Requirements / Input của khách hàng

  **Ví dụ:** Raw requirement, Q&A khách hàng, Requirement Definition, BRD, change request từ khách hàng, meeting minutes liên quan requirement.

  > **Đây là family quan trọng nhất** vì requirement chain (Raw Req → Q&A → Req Def) là backbone của traceability.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `requirement_definition` (Req Def, canonical) · `meeting_note` (Q&A / meeting minutes, canonical) · `raw_req` / `customer_qa` / `change_request_input` *(project extension)* |
  | `source_type` (spine) | `requirement_definition` · `meeting_note` · `customer_requirement` (cho raw/customer/CR input) |
  | `knowledge_class` | `source_of_truth` (Req Def đã chốt) hoặc `reference` (Raw Req, Q&A, MoM) |
  | `profile_id` | `requirement` |
  | Canonical slot (Req Def) | `feature_overview`, `user_stories`, `acceptance_criteria`, `business_rules`, `data_model_outline`, `ui_outline`, `non_functional`, `out_of_scope`, `assumptions`, `open_questions` |
  | Canonical slot (Q&A) | `question`, `answer`, `decision`, `decided_by`, `decided_at`, `impacts_on` |
  | Tier T1 | feature ID, screen ID, Q&A ID |
  | Tier T2 | business term, customer name, decision keyword |
  | `## Related Sources` | link Req↔Q&A↔BD↔DD↔Testcase cùng entity (role `upstream_input`/`companion_requirement`/`downstream_target`) |
  | Link **bắt buộc** | Raw Req ↔ Q&A ↔ Req Def ↔ BD ↔ DD ↔ Testcase |

  **Quy tắc đặc thù requirement:**

  1. **Không flatten chain quá sớm.** Nếu trong Req Def có 1 quyết định gốc từ Q&A, link tới Q&A đó — đừng chỉ ghi "đã chốt".
  2. **Supplemental status** (Q&A, findings): mỗi Q&A phải có:
    - `status`: open / resolved / closed
    - `reflection_status`: not_reflected / reflected / partially_reflected
    - `reflected_to`: artifact_ref của Req Def/DD đã phản ánh
    - `superseded_by`: nếu Q&A bị Q&A sau override
  3. **Customer-facing source** ưu tiên giữ nguyên ngôn ngữ gốc (tiếng Nhật/Anh) trong source, dịch trong meta `Summary` thôi.
  4. **Change request từ khách hàng**: track riêng, không merge vào Raw Req gốc.

  **Sample prompts:**
  ```
  # Thêm vào wiki — 1 file
  "Add file requirements/Req_Def_Ordering_v2.md vào wiki — đây là Requirement Definition đã chốt"
  "Đăng ký Q&A-2026-04.xlsx vào wiki — Q&A tháng 4 với khách hàng"

  # Thêm vào wiki — cả folder
  "Đăng ký toàn bộ tài liệu requirement trong folder requirements/phase1/ vào wiki"

  # Cập nhật
  "Req_Def_F04_v2.md vừa chốt thêm 2 acceptance criteria sau meeting hôm qua, sync wiki"
  "Q&A-003 đã được reflect vào Req Def, update reflection_status thành reflected"

  # Update status supplemental
  "Q&A-2026-03-15 đã answered và đã reflected vào Req_Def_v3, set status và reflected_to"

  # Archive / supersede
  "Req_Def_F04_v1.md đã bị thay bởi v2, mark superseded — trỏ superseded_by sang v2"
  "Raw requirement R-001-OLD đã bị CR-2026-05 override, mark superseded"
  ```

  ### 7.6. Tài liệu design có sẵn

  **Ví dụ:** Basic Design (BD), Detail Design (DD), Architecture diagram, Sequence diagram, Database design, API spec, UI mockup spec.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `basic_design` / `detailed_design_fe` / `detailed_design_api` / `detailed_design_be` / `detailed_design_combined` / `db_schema` / `api_manual` / `screen_mockup` (canonical) · `architecture` *(project extension)* |
  | `source_type` (spine) | `basic_design` · `detail_design` (gộp các `detailed_design_*`) · `db_schema` · `api_manual` · `screen_mockup` |
  | `knowledge_class` | `source_of_truth` (đã chốt) hoặc `curated` (đang draft) |
  | `profile_id` | `design_doc` |
  | Canonical slot (DD) | `ui_ux_behavior`, `fe_event_logic`, `api_contract`, `be_processing_logic`, `db_data_access`, `validation`, `function_to_function_relation`, `error_handling`, `non_functional` |
  | Canonical slot (BD) | `feature_overview`, `actors`, `flow_outline`, `screen_list`, `api_list`, `data_outline`, `dependencies` |
  | Tier T1 | feature ID, screen ID, API endpoint, table name, function name (e.g. `func_F04_BOOKING_SEARCH`) |
  | Tier T2 | business term, alias, JP/EN names |
  | `## Related Sources` | **bắt buộc** với split design — link FE/API/BE cùng function (role `companion_design`) + BD/testcase |
  | Link bắt buộc | DD ↔ BD ↔ Req Def; DD ↔ Testcase; DD ↔ source code |

  **Quy tắc đặc thù design (Split Design Pattern):**

  1. **DD thường rất dài** → split theo object (FE / API / BE) — đây là Split Design Pattern chính thức của AIWS:
    - `SRC-DD-F04-BOOKING-SEARCH-FE`
    - `SRC-DD-F04-BOOKING-SEARCH-API`
    - `SRC-DD-F04-BOOKING-SEARCH-BE`
    - Cả 3 link lẫn nhau qua `## Related Sources` với role `companion_design`.
  2. **Diagram (PNG/SVG)** không build meta riêng — embed reference vào meta của design doc chính, với `source_representation_status` ghi rõ "diagram chỉ có ở source".
  3. **API spec OpenAPI/Swagger** convert sang Markdown summary → build meta trên MD, locator vẫn trỏ về YAML gốc.

  **Sample prompts:**
  ```
  # Thêm vào wiki — 1 file
  "Add file docs/design/F04_DD_FE.md vào wiki — Detail Design FE của function F04"
  "Đăng ký F04_BD.pdf vào wiki — Basic Design của function F04 booking search"

  # Thêm vào wiki — cả folder (Split Design Pattern)
  "Thêm toàn bộ tài liệu design trong folder docs/design/ordering/ vào wiki"
  "Đăng ký hết file DD trong folder docs/design/cb-purchasing/ — có FE, API, BE riêng"

  # Điền ## Related Sources sau khi có đủ meta cùng function
  "Trong meta DD-FE của F04, thêm related sources tới BD, DD-API, DD-BE (companion_design) và testcase (downstream_target)"
  "Điền ## Related Sources cho cụm CB01001: BD, DD-FE, DD-API, DD-BE liên kết companion_design"

  # Tạo PMP sau sample-first
  "Format DD Fujitsu đã ổn định qua 3 sample, tạo PMP cho format này"

  # Cập nhật
  "F04_DD_FE.md đã được update section §3.2 sau code review, refresh meta"
  "DB design thêm bảng mới t_booking_log, sync wiki meta"

  # Archive / supersede
  "DD-F04-FE-v1 đã bị thay bởi v2, mark superseded"
  ```

  ### 7.7. Source code của dự án

  **Ví dụ:** Java class, Python module, React component, SQL migration, Terraform module, shell script.

  > **Source code không đưa vào Knowledge Hub như "tài liệu"** — nó là *source of truth* tự thân. Knowledge Hub chỉ build meta cho **những đơn vị code đáng tra cứu lại**.

  | Mục | Giá trị |
  |---|---|
  | `artifact_type` | `code_module` *(project extension — AIWS chưa hỗ trợ tốt cho source code)* |
  | `source_type` (spine) | (profile-extension; không có trong base spine) |
  | `knowledge_class` | `reference` (đa số) hoặc `curated` (utility/pattern dùng chung) |
  | `profile_id` gợi ý | `java_class` (đã có), `python_module` (đã có) |
  | Canonical slot | `module_purpose`, `public_api`, `dependencies`, `key_invariants`, `usage_example`, `related_design_doc` |
  | Tier T1 | tên class/module/function (e.g. `BookingSearchService`) |
  | Tier T2 | package, domain term, design pattern name |
  | `## Related Sources` | trỏ về DD/function mà code này implement (role `companion_design`/`upstream_input`) |
  | Link thường có | Code ↔ DD; Code ↔ Testcase |

  **Quy tắc:**

  1. **Không build meta cho mọi file code.** Chỉ build cho: public API, core domain entity, utility/helper reuse, module có decision phức tạp.
  2. **Code thay đổi nhanh** → meta phải có `updated_at` đúng commit version. Code rename/move → `/aiws-wiki refresh` CASE 1 update `artifact_locator`.
  3. **`Summary` của meta code** nên trả lời: "Class/module này tồn tại để làm gì? Khi nào nên dùng nó?" — không liệt kê method.

  **Sample prompts:**
  ```
  # Thêm vào wiki
  "Add file src/service/BookingSearchService.java vào wiki — core service cho booking search"
  "Đăng ký src/utils/DateTimeHelper.py vào wiki — utility helper dùng chung toàn project"

  # Cập nhật
  "BookingSearchService vừa thêm method searchByCustomer sau refactor, update meta"
  "DateTimeHelper.py đã rename sang DateUtils.py, cập nhật artifact_locator trong meta"

  # Archive / deprecate
  "LegacyOrderService.java đã bị thay bởi OrderService.java, deprecate meta cũ"
  ```

  ---

  ### 7.8. Object nodes (`node_kind=object`) & bước "Suggest objects/relations"

  Ngoài artifact (1 meta / file), AIWS có **object node** — meta `node_kind=object` cho **entity tái dùng**, KHÔNG có file nền (`artifact_locator=__OBJECT__`), nằm cùng index + cùng `## Related Sources`.

  **7 object kind hiện hành** (family prefix `source_id`):
  `function` (`SRC-FUNC-`) · `screen` (`SRC-SCREEN-`) · `api` (`SRC-API-`) · `batch` (`SRC-BATCH-`) · `table` (`SRC-TABLE-`) · `module` (`SRC-MOD-`, navigation-only) · `concept` (`SRC-CPT-`). (`business_rule` hiện **deferred** — chưa dùng trong MVP.)

  **Quy tắc:**
  - **Hand-authored only:** AI chỉ *suggest candidate*, **HUMAN author** object meta. Không tool nào tự tạo.
  - **Necessity test:** ưu tiên gắn quan hệ qua `companion_design` trên 1 artifact sẵn có; chỉ tạo object node khi **không có host artifact đơn lẻ tự nhiên**.
  - **KHÔNG** field/store nào của retired record (xem `Knowledge_Object_Model_Spec_MVP` §8); object là **pointer**, không phải container.

  **Bước "Suggest objects/relations"** (bạn sẽ thấy ở cuối mỗi lần register/refresh): skill hiển thị 2 bảng — **Detected Objects** (kind | proposed source_id | name | represented_by | có meta chưa | action) + **Discovered Relations** (from | edge | to | confidence | evidence) — và **append capture** vào `08_capture_inbox.jsonl` (trigger `object_relation_capture`).
  - **Suggest vô điều kiện:** có artifact liên quan KHÔNG phải lý do bỏ qua. Câu hỏi "có host artifact đơn lẻ không" chỉ quyết định **tạo object node riêng** vs **gộp vào 1 edge `companion_design`** — KHÔNG quyết định có suggest hay không.
  - Không phát hiện gì → nói rõ "no reusable objects/relations detected" (không im lặng bỏ qua).

  ---

  ## 8. Templates

  ### 8.1. Template Wiki Source Meta (Layer 1)

  > Đặt trong `.ai-work/wiki_sources/meta/<family>/SRC-<FAMILY>-<SCOPE>.md`.
  > **KHÔNG tạo tay** — dùng `/aiws-wiki register` để AI build, sau đó review.

  ```markdown
  ---
  artifact_type: detailed_design_fe         # ← 1 trong 14 type của Artifact Type Taxonomy
  source_id: SRC-DD-F04-BOOKING-SEARCH-FE
  title: Detail Design — Màn Tìm kiếm Đặt phòng (F04) — FE layer
  source_type: detail_design                  # ← spine (lint authority); detailed_design_* map về detail_design
  knowledge_class: source_of_truth            # source_of_truth | curated | reference | history
  artifact_locator: docs/design/F04_BookingSearch_DD_v2_FE.md
  profile_id: design_doc
  status: active
  updated_at: 2026-05-26
  # Optional:
  # related_artifact_refs: [SRC-BD-F04-BOOKING-SEARCH, SRC-ITTC-F04]  # traceability phẳng (KHÔNG để điều hướng)
  # task_relevant_tags: [booking, search, ui]
  # source_representation_status: sufficient | partial | needs_review
  # original_artifact_locator: docs/design/F04_BookingSearch_DD_v2.pdf  (nếu source này là MD đã convert)
  # superseded_by: SRC-...
  ---

  # Wiki Source Meta — Detail Design F04 FE

  ## Summary
  Thiết kế chi tiết FE màn tìm kiếm đặt phòng F04: filter, sort, paging,
  xử lý khi không có kết quả.

  ## Knowledge Targets
  - domain
  - pattern
  - reference

  ## Lookup Keys
  - F04 [T1]                          ← Tier 1: ID duy nhất, ×3 score
  - func_F04_BOOKING_SEARCH [T1]       ← Tier 1
  - SRC-DD-F04-BOOKING-SEARCH-FE [T1]
  - booking search [T2]                ← Tier 2: domain term, ×1.5
  - tìm kiếm đặt phòng [T2]
  - BookingSearchService [T2]
  - BookingSearchComponent [T2]
  - /api/v1/bookings/search [T2]
  - detailed_design_fe [T3]            ← Tier 3: label, ×1
  - design [T3]

  ## Related Sources                   ← quan hệ cross-artifact (scaffold tự động khi build)
  - **SRC-BD-F04-BOOKING-SEARCH** — role: upstream_input — BD định nghĩa business intent + acceptance criteria F04; coupling = business rules; đổi BD → review lại FE design.
  - **SRC-DD-F04-BOOKING-SEARCH-API** — role: companion_design — cùng function, lớp API; coupling = request/response contract `/api/v1/bookings/search`; đổi contract → đồng bộ FE.
  - **SRC-DD-F04-BOOKING-SEARCH-BE** — role: companion_design — cùng function, lớp BE; coupling = data shape trả về; đổi logic → kiểm tra API/FE.
  - **SRC-ITTC-F04** — role: downstream_target — test case verify function; coupling = acceptance criteria; đổi DD → cập nhật test.
  # Basis note BẮT BUỘC (CR-06-002): viết khách quan, intent-agnostic — dependency nêu hướng+coupling+ảnh hưởng; skippable ghi "no data coupling". TRÁNH "MUST READ"/"mở khi...".
  # Documentary roles: upstream_input · downstream_navigation · downstream_target · triggered_flow ·
  #   system_foundation · companion_design · companion_requirement · output_template · related
  # Representation (Object↔Artifact): represents · represented_by   |   Domain (Object→Object): x:-namespaced

  ## Artifact Reference
  - **Type:** detail_design (source_type) — artifact_type: detailed_design_fe
  - **Path:** docs/design/F04_BookingSearch_DD_v2_FE.md
  - **Version:** v2
  - **Last reviewed:** 2026-05-20

  ## Source-Specific Hints
  - Section §3.2 là điểm khác biệt so với mock-up cũ (đã chốt theo Q&A-2026-04-12).

  ## Change Impact Hints
  - Khi DD này đổi: kiểm tra IT_TESTCASE_F04 và source code BookingSearchService.

  ## Cautions
  - Diagram sequence chỉ có ở file PDF gốc, file MD không capture được.
  ```

  **Lưu ý quan trọng về Tier:**
  - Mỗi meta nên có **ít nhất 2–4 từ T1** (ID/canonical name).
  - T2 mix tiếng Việt + tiếng Anh + technical + business.
  - T3 chỉ là label phụ — không phụ thuộc vào T3.

  ### 8.2. Template `## Related Sources`

  > Nằm **TRONG meta của từng artifact** (mô hình 2-layer).
  > Section được **scaffold tự động** khi build meta — bạn chỉ điền target source_id + role, hoặc nhờ AI điền rồi review.

  ```markdown
  ## Related Sources
  - **SRC-BD-F04-BOOKING-SEARCH** — role: upstream_input — BD định nghĩa business intent + acceptance criteria; coupling = business rules F04; đổi BD → review design.
  - **SRC-DD-F04-BOOKING-SEARCH-API** — role: companion_design — cùng function, lớp API; coupling = request/response contract; đổi contract → đồng bộ FE/BE.
  - **SRC-DD-F04-BOOKING-SEARCH-BE** — role: companion_design — cùng function, lớp BE; coupling = data shape + xử lý; đổi logic → kiểm tra API/FE.
  - **SRC-ITTC-F04** — role: downstream_target — test case verify function; coupling = acceptance criteria; đổi DD → cập nhật test.
  - **SRC-TBL-BOOKING** — role: upstream_input — table được search; coupling = schema cột dùng trong query; đổi schema → ảnh hưởng FE/BE/test.
  - **SRC-FUNC-F05-BOOKING-DETAIL** — role: related — màn chi tiết điều hướng từ F04; no data coupling (chỉ navigation).
  ```

  **Basis note (BẮT BUỘC, viết khách quan — CR-06-002):** mỗi entry viết **intent-agnostic** để AI đọc tự quyết đọc-hay-bỏ:
  - **Dependency edge** (có coupling data/contract): nêu **hướng + shared subject** (ai đọc/ghi data của ai) + **coupling** (schema/field/key/contract) + **đổi thì ảnh hưởng gì**.
  - **Skippable edge** (không coupling): nói rõ **"no data coupling"** (vd "dùng chung header component; no data coupling").
  - **TRÁNH:** "MUST READ"/"luôn đọc" (ép đọc mù) và trigger mơ hồ "mở **khi** đổi X".
  - Lint: data-flow edge thiếu basis note → **warn-only** `relations_thin_basis` (không phải error).

  **Role enum — 3 register:**

  | Register | Endpoint | Role |
  |---|---|---|
  | **documentary** (Artifact→Artifact) | meta thường | `upstream_input` · `downstream_navigation` · `downstream_target` · `triggered_flow` · `system_foundation` · `companion_design` · `companion_requirement` · `output_template` · `related` |
  | **representation** (Object↔Artifact) | object node ↔ file nền | `represents` · `represented_by` |
  | **domain** (Object→Object) | object ↔ object | `x:`-namespaced (vd `x:calls`, `x:part_of`, `x:reads`, `x:writes`, `x:migrates_to`) — registry open, project thêm `x:` ngay |

  Ý nghĩa 9 documentary role: `upstream_input` (cung cấp input/intent) · `companion_design` (cùng function khác lớp FE/API/BE) · `companion_requirement` (requirement cùng entity) · `downstream_target` (nơi verify, vd test case) · `downstream_navigation` (màn/flow đi tiếp) · `triggered_flow` (flow được kích hoạt) · `system_foundation` (nền tảng: architecture, common rule) · `output_template` (template/checklist/guideline) · `related` (liên quan ngang).

  ### 8.3. Template Source Interpretation Profile (`.yml`)

  > Đặt trong `.ai-work/wiki_sources/profiles/<profile_id>.yml`. Tạo khi xuất hiện artifact type chưa có profile phù hợp.

  ```yaml
  profile_id: <profile_id>
  title: <Tiêu đề mô tả>
  source_type: <detail_design | requirement_definition | process_guideline | ...>   # spine value (lint authority)
  default_impact: <low | medium | high>
  knowledge_targets:
    - domain
    - reference
    - pattern
  lookup_key_hints:
    - <keyword gợi ý xuất hiện trong loại tài liệu này>
  section_hints:
    - <section/heading thường có trong loại tài liệu này>
  impact_rules: []
  cautions:
    - <điều cần lưu ý khi build meta cho loại này>
  ```

  ### 8.4. Template Project Mapping Pattern — PMP

  > Đặt trong `.ai-work/wiki_sources/profiles/mapping_patterns/PMP-<id>.yml`.
  > Tạo qua `/aiws-wiki register` CASE 3 (build PMP — reactive, AI suggest sau sample-first).

  ```yaml
  mapping_pattern_id: PMP-DD-FUJITSU-V1
  artifact_type: detailed_design_fe
  format_signature:
    heading_pattern: "^§\\d+(\\.\\d+)* "
    section_markers:
      - "画面項目"        # JP: screen items
      - "イベント仕様"     # JP: event spec
      - "API連携"         # JP: API integration
    language: jp_canonical_with_en_terms
    table_format: pipe_markdown
  canonical_slots_used:
    - ui_ux_behavior
    - fe_event_logic
    - api_contract
    - validation
    - error_handling
  common_source_to_slot_mapping:
    - source_section: "画面項目"
      canonical_slot: ui_ux_behavior
    - source_section: "イベント仕様"
      canonical_slot: fe_event_logic
    - source_section: "API連携"
      canonical_slot: api_contract
    - source_section: "バリデーション"
      canonical_slot: validation
  reuse_confidence: high
  exceptions:
    - "Khi DD có section 'パフォーマンス要件' → map sang non_functional (không bắt buộc)"
  created_from_samples:
    - SRC-DD-F04-BOOKING-SEARCH-FE
    - SRC-DD-F05-BOOKING-DETAIL-FE
    - SRC-DD-F06-BOOKING-CREATE-FE
  verified_with: /aiws-wiki test-lookup mode A pass 95%
  updated_at: 2026-05-26
  ```

  ### 8.5. Template Change Request (CR)

  > Dùng khi muốn promote candidate thành canonical update. Đặc biệt **bắt buộc** khi gặp 1 trong 5 Promotion Gate trigger.

  ```markdown
  ---
  cr_id: CR-AIWS-2026-05-26-update-process-release-v2
  title: Update meta cho Release Process v2.0
  target_wiki_object_or_section: SRC-PROCESS-RELEASE-V1
  change_type: update_curated_knowledge    # 1 trong 10 change types (xem §12)
  request_type: wiki_update
  requester: <tên>
  reviewer_or_wiki_manager: <tên người duyệt>
  target_layer: curated_knowledge          # object | index | alias_map | linkage | curated_knowledge | status_reflection | other
  status: pending_review                   # pending_review → approved → applied | rejected
  created_at: <YYYY-MM-DD>
  needs_human_confirmation_after_draft: true
  promotion_gate_triggered: false          # ← true nếu gặp 1 trong 5 trigger (xem §11)
  ---

  ## Change Summary
  <Tóm tắt 1–3 câu>                          # mandatory

  ## Change Reason
  <Tại sao cần thay đổi>                     # mandatory

  ## Source Artifact References
  - <Path tới source artifact chứng minh thay đổi>   # mandatory (source_artifact_refs)

  ## Source Excerpt / Evidence
  <Trích đoạn ngắn>                          # mandatory (source_excerpt_or_evidence_summary)

  ## Proposed Update Direction
  <Đề xuất thay đổi cụ thể>                  # mandatory

  ## Do Not Change
  <Phần nào KHÔNG được đụng>

  ## Must Preserve
  <Phần nào bắt buộc giữ>
  ```

  ---

  ## 9. Checklist trước khi đưa artifact vào Knowledge Hub

  > Member tự kiểm tra trước khi commit meta. Wiki Manager kiểm tra lại khi duyệt CR.

  **Phần A — Eligibility**

  - [ ] Artifact đã được chốt (không phải draft nháp đang còn TBD)?
  - [ ] Có >= 1 use case cụ thể AI/người sẽ muốn tra lại sau 1 tháng?
  - [ ] Reuse value rõ ràng?
  - [ ] Grounding mạnh: nội dung đến từ source canonical, không phải suy luận?
  - [ ] Placement rõ ràng: biết `artifact_type` thuộc 14 loại taxonomy nào?
  - [ ] Tuân thủ project_profile?

  → Bất kỳ "Không" → để ở notebook/backlog.

  **Phần B — Skill flow**

  - [ ] Đã dùng `/aiws-wiki register` (không gọi trực tiếp tool CLI hay skill internal)?
  - [ ] STAGE 2 (classify artifact_type) đã có HUMAN confirm?
  - [ ] Profile được router suggest đã được review (top-3 candidates)?
  - [ ] Nếu dùng CASE 3 chế độ proactive (profile/PMP): profile/PMP đã được HUMAN review & confirm trước khi dùng cho batch?
  - [ ] Nếu PMP tạo không có sample (`reuse_confidence: medium`): đã test với file thực tế và nâng lên `high` sau khi pass?

  **Phần C — Meta file**

  - [ ] Frontmatter có đủ 9 field bắt buộc: `artifact_type`, `source_id`, `title`, `source_type`, `knowledge_class`, `artifact_locator`, `profile_id`, `status`, `updated_at`? (`related_artifact_refs` là optional)
  - [ ] `artifact_type` thuộc enum Artifact Type Taxonomy (14 canonical + project extension đánh dấu rõ); `source_type` ∈ spine (lint authority) hoặc profile-extension?
  - [ ] `source_id` UPPERCASE, hyphen-separated, unique, ổn định?
  - [ ] Path trong `artifact_locator` đúng và tồn tại?
  - [ ] `Summary` <= 2 câu, không inline source?
  - [ ] **Lookup Keys có ít nhất 2 T1** (ID/canonical name)?
  - [ ] T2 mix tiếng Việt + tiếng Anh + technical + business?
  - [ ] Có `Cautions` nếu artifact có phần outdated/uncertain?
  - [ ] 1 file source ↔ 1 meta (không gộp, không tách trừ Split Design Pattern)?

  **Phần D — `## Related Sources` (nếu artifact có quan hệ cross-artifact)**

  - [ ] Có `## Related Sources` cho artifact thuộc entity nhiều lớp (FE/API/BE, BD↔DD↔Testcase)?
  - [ ] Mỗi entry có **target source_id tồn tại** + **role hợp lệ** (trong role enum)?
  - [ ] Không còn TODO scaffold chưa điền (vd `<target_source_id>`)?
  - [ ] Không dùng `related_artifact_refs` (phẳng) để thay cho điều hướng — quan hệ có-role phải ở `## Related Sources`?

  **Phần E — Links & supplemental**

  - [ ] Đã link tới các artifact upstream/downstream tương ứng?
  - [ ] Với Q&A/findings/open point: đã set `status`, `reflection_status`, `reflected_to`, `superseded_by`?
  - [ ] Không "flatten" Raw Req → Req Def mà mất Q&A trung gian?

  **Phần F — Verification**

  - [ ] Đã chạy `/aiws-wiki test-lookup` mode A → mọi entry tìm được mình qua source_id + lookup_keys?
  - [ ] Nếu có FAIL → đã fix Lookup Keys / Tier annotation và rebuild?
  - [ ] Đã chạy `/aiws-wiki test-lookup` mode C với task thực tế → tài liệu thiết yếu xuất hiện trong top kết quả với **score-gap rõ** (tài liệu đúng tách hẳn nhóm dưới)?
    - Prompt mẫu: `"list tài liệu cần thiết cho task [tên task], ghi rõ cách tìm các tài liệu đó."`
  - [ ] Đã chạy `python .ai-work/tooling/lint_wiki.py` (nếu chưa được skill gọi giúp)?

  **Phần G — Promotion Gate**

  - [ ] Có trigger 1 trong 5 Promotion Gate?
    - Set `knowledge_class: source_of_truth`?
    - Đổi `source_id` đã được reference?
    - Split/merge meta?
    - Mark important artifact `deprecated`?
    - Đổi traceability chain (`related_artifact_refs` / `## Related Sources`) giữa artifact lớn?
  - [ ] Nếu có → đã tạo CR + Wiki Manager?

  **Phần H — Governance**

  - [ ] Không tự sửa file canonical của AIWS (Wiki Guidelines / methodology)?
  - [ ] Không edit tay `index.jsonl`?

  ---

  ## 10. Verify chất lượng bằng `/aiws-wiki test-lookup`

  Sau khi build meta, **bắt buộc** verify trước khi declare done. Skill `/aiws-wiki test-lookup` có 3 mode:

  ### Mode A — Self-test (automated)

  ```
  Bạn: "Test wiki lookup mode A cho toàn bộ index."
  ```

  AI chạy: với mỗi entry trong `index.jsonl`:
  1. Test `source_id` (id mode) — phải rank 1.
  2. Test từng `lookup_keys` (semantic mode) — phải có trong top-5.

  Output: `[PASS]` / `[FAIL]` mỗi entry + hint khi FAIL ("lookup_key quá chung chung, cân nhắc thêm T1 tag").

  ### Mode B — Structured cases

  ```
  Bạn: "Chạy aiws-wiki test-lookup mode B với file .ai-work/wiki_sources/test_cases.jsonl"
  ```

  File `.jsonl` có format: `{"query": "...", "expected_source_id": "...", "mode": "semantic"}`. Output: PASS/FAIL từng case.

  ### Mode C — Natural language task

  Dùng format prompt sau để test coverage cho một task thực tế:

  ```
  "list tài liệu cần thiết cho task [tên task], ghi rõ cách tìm các tài liệu đó."
  ```

  Ví dụ với sample task review basic design:

  ```
  "list tài liệu cần thiết cho task review tài liệu basic design, ghi rõ cách tìm các tài liệu đó."
  ```

  AI sẽ:
  1. Phân tích task → xác định loại tài liệu cần (BD, DD, Req Def…).
  2. Sinh 3–5 query → chạy `lookup_wiki_source.py` cho từng query.
  3. List tài liệu tìm được, score, cách tìm (query nào hit, lookup_key nào match).
  4. Báo gap nếu tài liệu quan trọng không xuất hiện trong kết quả.

  → Pass condition: tài liệu thiết yếu cho task xuất hiện trong top kết quả với **score-gap rõ** (gap lớn so với nhóm sau = confident hit). KHÔNG có ngưỡng score tuyệt đối — nếu phân phối phẳng (nhiều score thấp gần nhau) thì nới `--limit` (với `--slim`) hoặc sắc lại query.
  → Mode C đặc biệt hữu ích để đánh giá Wiki **realistic**, không chỉ self-consistency.

  ### Khi nào dùng mode nào?

  | Tình huống | Mode |
  |---|---|
  | Sau khi build/update index, verify nhanh | A |
  | Có danh sách query cụ thể (regression test) | B |
  | Muốn biết AI sẽ tìm ra gì khi làm task thực tế | C |

  ---

  ## 11. Promotion Gate — 5 trigger HARD STOP

  Khi gặp 1 trong 5 trigger sau, **AI/người không tự apply**, phải qua CR + Wiki Manager:

  | # | Trigger | Lý do |
  |---|---|---|
  | 1 | Set `knowledge_class: source_of_truth` | Nâng tài liệu lên Truth tier — ảnh hưởng diện rộng |
  | 2 | Đổi `source_id` của meta đã được tham chiếu | Mọi `related_artifact_refs` / `## Related Sources` trỏ về meta đó sẽ gãy |
  | 3 | Split hoặc merge meta records | Thay đổi semantic boundary của artifact |
  | 4 | Mark artifact quan trọng `deprecated` | Báo hiệu cho consumer dừng dùng |
  | 5 | Đổi traceability chain (`related_artifact_refs` / `## Related Sources`) giữa artifact lớn | Tái cấu trúc quan hệ artifact-to-artifact |

  ---

  ## 12. Governance flow — candidate → CR → Wiki Manager → apply

  ```
    AI/member phát hiện
    thông tin đáng lên wiki
              │
              ▼
    ┌──────────────────┐
    │  Candidate       │  ← append vào .ai-work/08_capture_inbox.jsonl
    │  (notebook)      │     theo wiki_candidate_capture_playbook
    └────────┬─────────┘
              │  BrSE / member triage:
              │  - đáng đưa lên wiki? (5 tiêu chí)
              │  - có Promotion Gate trigger?
              ▼
    ┌──────────────────┐
    │  CR draft         │  ← template mục 8.5
    │  (mandatory       │
    │   fields đủ)      │
    └────────┬─────────┘
              │  Wiki Manager review:
              │  - duplicate? conflict? scope?
              │  - approve / request_change / reject
              ▼
    ┌──────────────────┐
    │  CR approved      │
    └────────┬─────────┘
              │  AI/người apply qua `/aiws-wiki register` hoặc
              │  `/aiws-wiki refresh` theo allowed_ai_freedom
              ▼
    ┌──────────────────┐
    │  Canonical update │  ← meta file commit + index rebuild
    │  applied          │
    └──────────────────┘
  ```

  **5 tiêu chí eligibility:** reusability, grounding, placement, maturity, project-profile compliance.

  **10 change types** trong CR:
  `add_artifact_publication`, `add_metadata`, `update_metadata`, `add_linkage`, `update_linkage`, `add_curated_knowledge`, `update_curated_knowledge`, `mark_reflected_or_superseded`, `deprecate_or_hide`, `merge_or_consolidate`.

  ---

  ## 13. Anti-patterns thường gặp và cách tránh

  | Anti-pattern | Tại sao xấu | Cách tránh |
  |---|---|---|
  | Build meta cho mọi tài liệu trong project | Meta noise lớn, lookup ra hàng chục kết quả không liên quan | Eligibility checklist 9.A |
  | 1 meta gom nhiều file | Vi phạm M-1, AI không trace được source | 1 file ↔ 1 meta. Cần liên kết nhiều artifact → dùng `## Related Sources` (không gom) |
  | Inline cả nội dung source vào `Summary` hoặc body meta | Vi phạm M-3, meta nặng, không reuse, dễ outdated | `Summary` ≤ 2 câu, body chỉ ghi hint/caution |
  | Gọi tool CLI trực tiếp bỏ qua skill router | Mất HUMAN gate, mất Promotion Gate check | Luôn dùng `/aiws-wiki register` hoặc `/aiws-wiki refresh` |
  | Sửa tay `index.jsonl` | Tool sẽ ghi đè, mất công | Sửa meta → chạy lại router → rebuild index tự động |
  | Mass build trước khi sample-first | Build xong 80 meta mới phát hiện profile sai → làm lại từ đầu | Sample-first: 2–3 sample, `/aiws-wiki test-lookup`, fix, rồi PMP, rồi mass |
  | Bỏ qua Tier annotation trên Lookup Keys | T1 missing → search bằng ID không ra | Mỗi meta ≥ 2 T1 |
  | Nhồi mọi quan hệ vào `## Related Sources` | Noise, mất ý nghĩa điều hướng | Chỉ ghi quan hệ task-useful, có hướng + đúng role |
  | Dùng `related_artifact_refs` (phẳng) để điều hướng | Không typed, không điều hướng được (flat list) | Quan hệ có-role để ở `## Related Sources` |
  | Gộp `resolved` = `reflected` | Mất audit trail Q&A đã thực sự áp vào Req Def chưa | Tách 3 trạng thái |
  | Build meta cho draft chưa chốt | Meta sẽ outdated nhanh | Để ở staging cho đến khi chốt |
  | `knowledge_class: source_of_truth` tuỳ tiện | Over-claim, AI sẽ trust quá mức + Promotion Gate trigger | Chỉ dùng cho artifact thực sự là truth |
  | Build meta cho toàn bộ source code | 90% meta là noise | Chỉ build cho public API, core domain, utility reuse cao |
  | Quên link Q&A ↔ Req Def | Mất traceability requirement chain | Bắt buộc link upstream/downstream |
  | Tự sửa canonical wiki | Vi phạm governance | Luôn qua candidate → CR → Wiki Manager |
  | Tạo profile mới cho mỗi artifact lạ | Profile bùng nổ, không reuse được | Trước khi tạo profile mới: check 3–5 artifact cùng kiểu, để router suggest |
  | Tạo PMP từ 1 sample duy nhất | Không đủ evidence format ổn định | Cần ≥ 2-3 sample đồng format + `/aiws-wiki test-lookup` pass mới tạo PMP |

  ---

  ## 14. Phụ lục

  ### 14.1. Bảng mapping nhanh 7 loại tài liệu → AIWS

  > `*(ext)*` = project extension (không có trong enum canonical §2). `source_type` = spine lint authority (`artifact_type` → `source_type` many-to-one). Tất cả dùng `/aiws-wiki register` (Design thêm Split Design Pattern).

  | Loại tài liệu | artifact_type | source_type (spine, lint) | profile_id gợi ý | knowledge_class điển hình |
  |---|---|---|---|---|
  | Giới thiệu dự án | `project_overview` *(ext)* | `canonical_doc` | `methodology_guide` hoặc tạo mới | reference / curated |
  | Process | `process_doc` *(ext)* | `process_guideline` | `process_doc` (tạo mới) | curated |
  | Guidelines | `guideline` *(ext)* | `process_guideline` | `methodology_guide` | curated |
  | Common rules / Checklists | `checklist` *(ext)* | `process_guideline` / `process_template` | `checklist` (tạo mới) | curated |
  | Requirements — Req Def | `requirement_definition` | `requirement_definition` | `requirement` | source_of_truth |
  | Requirements — Q&A / Meeting minutes | `meeting_note` | `meeting_note` | `requirement` | reference |
  | Requirements — raw / customer req | `raw_req` / `customer_qa` *(ext)* | `customer_requirement` | `requirement` | reference |
  | Design — BD / DD | `basic_design` / `detailed_design_fe/api/be/combined` | `basic_design` / `detail_design` | `design_doc` | source_of_truth / curated |
  | Design — DB / API / Mockup | `db_schema` / `api_manual` / `screen_mockup` | (1:1, same) | `design_doc` | source_of_truth / curated |
  | Source code | `code_module` *(ext — AIWS chưa hỗ trợ tốt)* | (profile-ext) | `java_class` / `python_module` | reference / curated |

  ### 14.2. Lệnh hay dùng

  ```bash
  # Dùng skill (khuyến nghị) — nói chuyện tự nhiên với AI:
  /aiws-wiki register <file path / folder path>
  /aiws-wiki refresh <file path / PMP_id>
  /aiws-wiki lookup --query "<keyword>"
  /aiws-wiki test-lookup [mode A | B | C]

  # Tool CLI trực tiếp (chỉ dùng khi cần):
  python .ai-work/tooling/lookup_wiki_source.py --query "<keyword>"
  python .ai-work/tooling/lookup_wiki_source.py --query "<keyword>" --scope local
  python .ai-work/tooling/lookup_wiki_source.py --query "<keyword>" --mode id
  python .ai-work/tooling/build_wiki_source_index.py        # rebuild index (router gọi giúp)
  python .ai-work/tooling/lint_wiki.py                       # lint
  python .ai-work/tooling/smoke_test_wiki_lookup.py --self-test   # mode A
  ```

  ### 14.3. Khi nào KHÔNG đưa lên Knowledge Hub

  - Tài liệu nháp đang thay đổi hàng ngày → để ở local notebook.
  - Email/Slack message rời rạc → tổng hợp thành Q&A artifact trước, rồi mới build meta.
  - Code generated tự động → không build meta.
  - Personal note của member → không phải project knowledge.
  - Tài liệu duplicate (3 bản cùng nội dung) → disambiguate, chọn canonical, archive còn lại.

  ### 14.4. Khi gặp tình huống không có trong guideline này

  Theo thứ tự ưu tiên:

  1. Hỏi AI: _"AIWS có spec/guideline canonical nào về [chủ đề]?"_ — AI sẽ trỏ tới tài liệu phù hợp (nếu dự án có).
  2. Tra Knowledge Hub của dự án (`/aiws-wiki lookup`) xem đã có meta liên quan chưa.
  3. Hỏi Wiki Manager hoặc BrSE.
  4. Nếu vẫn ambiguous: KHÔNG tự suy đoán. Ghi vào notebook, raise lên team meeting gần nhất.

  ### 14.5. Spec canonical chi tiết

  Các spec/guideline canonical chi tiết (taxonomy, lookup key strategy, meta/index, relationship, promotion gate…) do **AI Work System quản lý nội bộ**, không kèm trong tài liệu này. Khi cần đào sâu, hỏi AI: _"AIWS có spec nào về [chủ đề]?"_ — AI sẽ trỏ tới tài liệu canonical phù hợp nếu dự án đã cài.

  ---

  ## 15. Đóng lại — 6 thông điệp cốt lõi member cần nhớ

  1. **Wiki là Knowledge Hub 2 lớp + index.** Đơn vị tri thức = artifact-level meta (Layer 1); index là projection; quan hệ cross-artifact qua `## Related Sources`. Mỗi meta phải reusable, grounded, mature.
  2. **Meta-first, source-verify.** Đừng inline source. AI search meta → đi tiếp theo `## Related Sources`, mở source khi cần.
  3. **5 lệnh skill là đủ.** Không gọi tool CLI hoặc skill internal trực tiếp.
  4. **Sample-first → `/aiws-wiki test-lookup` → PMP → mass build.** Đừng nhảy thẳng vào mass.
  5. **Tier T1/T2/T3 quyết định search.** Mỗi meta ≥ 2 T1.
  6. **Promotion Gate dừng AI.** 5 trigger HARD STOP — luôn qua CR + Wiki Manager.

  > **Khi nghi ngờ: HỎI**, không **SUY ĐOÁN**. Khi chưa đủ chín: **ĐỂ NOTEBOOK**, không **BUILD META VỘI**.
