---
doc_id: cr_ir_review_checklist
title: "CR/IR Review Checklist — gate review trước khi PO approve một CR, một IR, hoặc cả một wave"
status: canonical
knowledge_class: curated
owner: AIWS-Product-Owner (HUMAN) — AI chạy checklist, HUMAN quyết định
version: 1.0
updated_at: 2026-08-19
promoted_by: CR-AIWS-2026-08-106
---

# CR/IR Review Checklist

Checklist **nội dung** dùng khi review một CR/IR trước lúc quyết định approve. Nó bổ sung cho
`AIWS_Change_Request_Spec_MVP.md`: spec nói **CR phải hợp lệ thế nào**, checklist này nói **kiểm
gì, theo thứ tự nào, và lấy bằng chứng ở đâu** trong một lượt review thật.

> **Provenance.** Nội dung dưới đây grounded từ: `AIWS_Change_Request_Spec_MVP.md`
> (§7/§9/§10/§11/§13/§17), `product/change_requests/README.md` + `intake/README.md`, intake rule
> adversarial-verify (CR-AIWS-2026-06-033 → `capture_and_triage_rules.md`), batch-apply discipline
> (CR-AIWS-2026-06-034, spec §13), và format checklist của agents pack
> (`common_document_review_checklist.md`). Thiết kế ban đầu được đối chiếu thử với batch pending
> 2026-07-14 (CR-031/032/033 + IR-14/14b). Bản draft sống trong `change_requests/intake/` từ
> 2026-07-14 tới 2026-08-19; **promote lên canonical bởi CR-AIWS-2026-08-106** vì thư mục `intake/`
> không đi vào bản cài, nên adopter không nhận được checklist nội dung nào cho họ CR/IR.

```yaml
checklist_id: cr_ir_review_checklist
version: 1.0
owner: AIWS-Product-Owner (HUMAN) — AI chạy checklist, HUMAN quyết định
status: canonical
```

## 0. Khi nào dùng — chọn mode

| Tình huống | Chạy phần |
|---|---|
| IR/candidate mới trong `intake/`, đang cân nhắc promote | §1 → §4 |
| 1 CR `proposed`, PO cân nhắc approve | §2 → §4 |
| Nhiều CR/IR cùng chờ (wave) | §2 từng CR → §3 → §4 |

Nguyên tắc chung: **review = verify against repo, không tin claim trên giấy** — mỗi check phải có evidence (file/line hoặc lệnh đã chạy). Approve ≠ apply (SOP §5 Rule C: apply cần explicit request riêng).

## 1. IR intake checks (trước khi promote IR → CR)

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| INTAKE-01 | Frontmatter intake đủ schema (`intake_id`=filename, `origin`, `intake_status`, `disposition`, `triage_note`) | Pipeline traceability | `intake/README.md` schema |
| INTAKE-02 | **Từng claim** được adversarial-verify vs repo NÀY, verdict per claim: CONFIRMED / PARTIAL(-reframed) / REFUTED / NOT-REPRO-UPSTREAM | External IR mô tả state của project KHÁC; tiền lệ 3/5 claim false (AIP-082) | Spec §17 + `capture_and_triage_rules.md` intake rule |
| INTAKE-03 | Path/line refs đã re-anchor đúng chiều (bản cài/`payload/…` → `product/…`); không truy cập evidence ngoài repo (rule #9) · **Phép kiểm rẻ nhất cho lớp finding "nội dung ship ra không khớp tài liệu": đếm CÙNG một pattern trên cả 3 cây** (`payload/` · `product/` · `.ai-work/`) — bằng nhau ⇒ bác ngay giả thuyết "bản build lấy bản stale" trong một lệnh (ca thật: 13/13/13, IR-2026-08-15 F2 bị bác; CAP-1063-008). | Demo→upstream đảo chiều path; line drift | IR-14b discipline note |
| INTAKE-04 | NOT-a-bug / intentional-by-design được GHI LẠI kèm ref quyết định gốc (tránh re-report vòng sau) | Demo re-report cùng finding qua nhiều release | CR-031 "Verified-NOT-a-bug" pattern |
| INTAKE-05 | Grouping rationale rõ (per surface / per theme); không re-intake findings vòng trước đã xử lý | 1 IR → 1..n CR phải có lý do tách/gộp | IR-14b (vòng 1 loại khỏi vòng 2) |
| INTAKE-06 | Findings không đủ chín → backlog capture / parked, KHÔNG nhét vào CR cho đủ | CR giữ AI-executable (§3.4) | IR-14b §6 → backlog |
| INTAKE-07 | Khi promote: `mapped_to_cr` + link 2 chiều + status banner trên file nguồn + `intake_status: processed` | Source-mapping convention | `intake/README.md` + feedback 2026-06-24 |
| INTAKE-08 | Screening sớm: proposal có đụng/mâu thuẫn Truth, core design, hay safety rule nào không? Có → flag ngay trong `triage_note` (candidate vẫn có thể promote, nhưng CR phải qua nhóm §2-H với evidence đầy đủ) | Chặn hướng sai từ cửa, đỡ tốn công draft CR | §2-H bên dưới |
| INTAKE-09 | **Verdict đổi SAU khi promote ⇒ truyền đạt lại.** Khi một CR revise làm đổi verdict của finding IR (rút change, ruling *not-a-bug*, reframe) sau khi back-mark/banner đã ghi → cập nhật back-mark hoặc gửi phản hồi mới cho nguồn, nêu rõ finding nào và vì sao. Verdict là thứ được **TRUYỀN ĐẠT**, không chỉ ghi vào file của mình | Ca thật: F3 rút ở CR-071 r3 ("not-a-bug", trong fence) nhưng banner 2026-08-16 vẫn liệt kê F3 dưới CR-071 → demo tái báo F3 ở IR-2026-08-17 (AIP-1074). Cùng họ bài học AIP-1065 "ghi file ≠ truyền đạt" | INTAKE-04 (ghi lại NOT-a-bug) + INTAKE-07 (banner); CAP-1074-06 |
| INTAKE-10 | **Fix ở upstream phải có ĐƯỜNG GIAO XUỐNG downstream.** Khi một CR sinh ra từ báo cáo của dự án dùng package, hỏi thẳng: bản sửa này tới được họ bằng đường nào (payload section nào? upgrade step nào? UPGRADE_NOTES?). Không có đường → **CR chưa đóng** | Ca thật: CR-AIWS-2026-08-005 thêm `.gitattributes` cho REPO NGUỒN từ incident IR-2026-08-05 G8 của demo, nhưng package không ship file đó (`find $PKG -name .gitattributes` = 0) ⇒ demo gặp lại cùng lớp vấn đề và tự thêm lần hai | CAP-1063-007; Spec §14 (auto-ship payload) |
| INTAKE-11 | **Subject doc EXTERNAL có thể SỐNG — pin mốc và re-check khi đóng.** Ở bước đầu ghi `sha256` + byte + mtime của subject vào workspace; khi stage vào `intake/` phải **byte-compare** với bản đã review; trước khi đóng **re-check mốc** — lệch thì hoặc review phần lệch, hoặc ghi rõ trên banner phạm vi chưa phủ | Ca thật: IR-2026-08-15 đổi **3 lần trong 2 ngày** (11→12→18→19 finding); round 1 stage bản 12 finding với banner chỉ phủ 11 (F12 sót), round 2 lặp lại đúng bẫy đó với F19. Lượt IR-2026-08-17 làm đúng: pin `9e276d13…` ở STEP-01, byte-compare khi stage | CAP-1065-R2-001 · CAP-1065-R2-004; AIP-1074 |

## 2. Single-CR checks (trước khi PO approve)

### A — Conformance & completeness

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-A1 | Mandatory fields đủ: `cr_id`, `title`, `request_type`/`change_type`, `requester`, `reviewer_or_product_owner`, `status`, Target, Requested change (summary+reason+expected outcome), Source basis | Thiếu → **not ready for review** (dừng sớm) | Spec §7 |
| CR-A2 | §2 Target **enumerate đủ mọi path** (không "etc."); tooling/SKILL-body → đủ **cả 2 cây** dual-tree | Under-scope = apply sót | Spec §9 |
| CR-A3 | Before/after đủ cụ thể để apply-AIP thực thi deterministic; `allowed_ai_freedom` phân mức (exact_apply / light_cleanup…) | CR phải AI-executable | Spec §3.4, §6 |
| CR-A4 | §15 propagation: resolved từng surface hoặc N/A-with-reason (node-model/vocab touch?) | Vocab đổi mà không sweep = drift | Spec §12 |
| CR-A5 | Governance class đúng: `cr_required` / `no_cr` / `mixed` khai đúng từng surface (lint RULE = cr_required dù là code) | Sai class = lách gate hoặc gate thừa | Spec §2 |
| CR-A6 | Đọc `status:` FIELD, không suy từ folder (applied có thể chưa move) | Folder-move lag đã xảy ra | README + memory 2026-06-24 |
| CR-A7 | **Mọi path trong §2 Target phải được verify TỒN TẠI trên đĩa** (hoặc khai rõ `CREATE` / `DELETE`) — chạy `ls`/`test -f` từng path, không tin trí nhớ | Ca thật: một row §2 trỏ `product/UPGRADE_IMPACT_NOTE_next_release.md` sau khi file đã bị fold+xoá (`d4ff628`) mà **mọi item nhóm A/B vẫn PASS** — không item nào đòi kiểm sự tồn tại | CAP-1059-005 (dogfood AIP-1059, FND-02) |
| CR-A8 | §11.x phải chạy LẠI sau MỖI revision — revision đổi **loại** của CR (thêm một khối tooling biến CR doc-only thành CR đổi hành vi). Bốn câu dưới một phút: `change_type` có trong từ vựng §4? · đọc title + §3 Summary như người chưa đọc thân CR, còn khớp các khối hiện tại? · khối `Cn` THÊM Ở REVISION có đổi hành vi tool ⇒ cần grep §11.8 riêng? · mọi tên `test_*.py` có tồn tại thật? | §11.x là checklist chạy MỘT LẦN lúc soạn xong ⇒ revision lọt lưới | Spec §11.8/§11.10/§11.10b; ca CR-106 r1→r3 |

### B — Identity & registry

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-B1 | `cr_id` đúng format month-scoped, allocate **cross-branch** (disk ∪ `git log --all` ∪ counter), không trùng | CAP-001: CR-025 collision 2 branch | Spec §10 |
| CR-B2 | Không pin id sibling (CR/AIP/test-label) chưa tồn tại — ref bằng mô tả ổn định + id đã có | Id chưa tồn tại sẽ trôi | Spec §11.2–11.4 |
| CR-B3 | `driving_source` truy vết được (IR/capture/triage/AIP cụ thể) | Grounding chain đứt = không audit được | Spec §6, §17 |

### C — Source basis & claim quality

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-C1 | Mọi claim then chốt có ref file/line trong repo; spot-check ít nhất các claim Critical/High **tự mở file xác nhận** | Reviewer không tin transcript | Spec §17 |
| CR-C2 | Inference/proposal của AI tách bạch khỏi grounded fact (§5/§7 của CR); `confidence_level` khai thật | Che inference = false confidence | Spec §17, §7 CR body |
| CR-C3 | CR từ external IR: verdict matrix intake (INTAKE-02) được CR trích dẫn đúng, không "nâng cấp" PARTIAL thành CONFIRMED | Verdict drift khi copy | CR-031 §Context pattern |
| CR-C4 | CR có `driving_source` là **IR/intake**: phần Context **tự đứng được** — nêu lại quan sát được gì, ở đâu, vì sao quan trọng, đo được gì lúc soạn; IR chỉ là **provenance**, không phải authority cho lý do | IR là vật tư **tiêu hao**: dựng xong CR thì xoá được. CR trỏ ngược IR để giải thích lý do sẽ mất nghĩa đúng lúc IR bị xoá, mà không có dấu hiệu nào báo | Spec §11.14 (và §11.13 — cùng hình dạng lỗi, một tầng trên) |

### D — Scope & duplication

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-D1 | Requested change khớp Target list — không scope-creep (fix "tiện tay" không khai) | Footprint thật > footprint khai | Spec §9 |
| CR-D2 | Không re-propose cái đã applied/rejected — search applied CRs + memory trước; proposal mới phải **EXTEND** cái có | Tiền lệ: re-propose bị chặn 2026-07-07 | `applied/` + `rejected/` scan |
| CR-D3 | Mọi design-decision mở được surface thành **DP đánh số cho PO** (kèm option + khuyến nghị), AI không tự chọn ngầm | PO controls the update | Spec §3.2; CR-031 DP-1..3 pattern |
| CR-D4 | YAGNI: từng sub-change có lý do riêng; sub-change "nice to have" → tách/park | Wave phình = review loãng | — |

### E — Conflict & coordination

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-E1 | Grep các CR open/draft khác cùng target file → có overlap thì `related_cr` **2 chiều** + note apply phải sequence | Hai CR im lặng cùng sửa 1 file | Spec §11.1 |
| CR-E2 | `related_cr` khai đủ lineage (CR gốc của cơ chế bị sửa, CR cùng family) | Reviewer cần biết đang đảo quyết định nào | CR-031 related_cr pattern |

### F — Guardrails & apply-readiness

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-F1 | `must_preserve` khai những gì KHÔNG được đổi; `apply_gates` bắt buộc: whole-tree lint 0 errors + dual-tree byte-identity + fixtures **in-repo** (không bao giờ dùng artifact downstream) | Gate lỏng = applied bẩn | Spec §13 |
| CR-F2 | Tooling change: có TDD case / fixture / repro kèm theo kế hoạch | "Fix" không test = defect wave sau | Spec §13; CR-031 T1/T2/T4 |
| CR-F3 | Retire/rename concept: plan sweep **mọi token variant** (snake/UPPER/prose) + surfaces dễ sót (presets, workspace templates, prose) | CR-026 sweep bắt 4 nhóm intake sót | Spec §9 (CR-030 rule) |
| CR-F4 | Back-compat/migration khai rõ (format version bump, tolerant-read, upgrade path cho bản đã cài) | Package/upgrade là surface hay vỡ nhất | CR-031 T1 SNAPSHOT_VERSION pattern |
| CR-F5 | **CR chạm cơ chế đóng gói / `PAYLOAD_MAP` / thêm section ship ⇒ phải khai LOẠI PAIR cho `check_dual_tree`** (mirror pair · source↔template · generated/skip) và enumerate test khoá bất biến đó | Ca thật: thêm section `aiws_wiki` mà không phân loại ⇒ **188 phantom `dual_tree_only_in_one`** (AIP-945); dogfood AIP-1059 cho thấy không item nào của checklist v0.1 phủ nghĩa vụ này (FND-04) | CAP-1059-004; CR-AIWS-2026-07-034 T3 · Spec §9 (pair classes) |
| CR-F6 | Ca dạng *"file không được chứa chuỗi S"*: hỏi **"S có thể là NỘI DUNG hợp lệ của file này không?"** — nếu có, ca **phải nêu PHẠM VI** (frontmatter / một section / toàn file). Rủi ro cao nhất ở tài liệu **meta** (spec/checklist/guideline nói về chính hệ thống): chúng dùng **cùng từ vựng** với thứ chúng mô tả | Nhầm 'tài liệu MANG khung X' với 'tài liệu NÓI VỀ khung X' ⇒ ca bắt oan chính nội dung | Spec §11.16; ca CR-106 D2 (checklist dạy kiểm `intake_id` nên tất nhiên chứa chữ đó) |

### G — Impact & risk

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-G1 | Package impact khai đúng: `product/**` auto-ship wholesale; content-only KHÔNG bump version per-addition | Đánh giá sai = rebadge cascade | Spec §14 |
| CR-G2 | Chạm Truth / spec authority → scrutiny cao nhất, đối chiếu precedence (spec wins trừ Approved Deviation) | Truth là highest precedence | CLAUDE §2, Spec §2 |
| CR-G3 | Blast radius: nếu CR SAI thì hỏng gì, phát hiện bằng gì? Có kill-switch/rollback không? | Risk-first như CR-019 (gated kill-or-confirm) | Known-Issues Register pattern |
| CR-G4 | Repeat-defect signal: finding lặp ≥2 release → ưu tiên apply + cân thêm guard chống tái phát (lint rule / test) | BUG-02/03 lặp 2–3 lần = cost thật | IR-14 note |
| CR-G5 | CR loại bỏ một phương án bằng lý do *"sẽ gãy / không thể / phải giữ vì có N chỗ trỏ"* ⇒ **lý do đó ĐÃ ĐƯỢC ĐO chưa, bằng lệnh nào?** Mệnh đề "sẽ hỏng nếu…" là một **claim về cây mã**, không phải nguyên tắc | Giả định chưa đo định hình phương án; CR mạch lạc quanh nó thì KHÓ phát hiện hơn CR viết tệ | Spec §11.17; ca CR-106 r1 (9/10 ca trong nỗi sợ không tồn tại) |

### H — Design & rule conformance (AIWS core) ⚠ gate cứng

> Khác G2: G2 áp khi CR **sửa file** Truth/spec; H hỏi change có **mâu thuẫn nội dung** với Truth/design/rule không — kể cả khi không sửa file nào của Truth. FAIL bất kỳ H-check nào → verdict tối đa là `REVISE` (hoặc `REJECT`), không `APPROVE-WITH-CONDITIONS`.

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| CR-H1 | Đối chiếu change với **Truth** (`SOP_MASTER`, `AI_WORK_CONTRACT`): không vi phạm / silently-bypass rule nào. Nếu cần deviate → đã có Approved Deviation (`AI_WORK_CONTRACT` §6) hoặc CR đề xuất deviation **tường minh** (nêu rule bị deviate + lý do + scope) — không bao giờ deviate ngầm | Truth là precedence cao nhất; "spec wins trừ Approved Deviation" | CLAUDE §2/§3 rule #3/#4/#8; Contract §6 |
| CR-H2 | Đối chiếu với **core design đã chốt**: methodology specs (`source_of_truth`) + applied CRs + HUMAN rulings. Change contradict/đảo ngược quyết định cũ → phải khai tường minh là **REVERSAL** (nêu CR/ruling gốc trong `related_cr` + lý do đảo) — reversal hợp lệ khi HUMAN quyết, nhưng không bao giờ âm thầm | Tiền lệ: HUMAN reversed two-track install 2026-06-23 — hợp lệ vì explicit; âm thầm đảo = design drift | Spec §17; `applied/` scan + rulings |
| CR-H3 | Không vi phạm **invariant vận hành cốt lõi**: HUMAN-gated promotion (AI không self-approve/self-apply/tự promote wiki candidate) · dual-tree byte-identity · Python stdlib-only (deviation phải sanctioned + có stdlib fallback) · portability (`__PROJECT_ROOT__`, không absolute path trong artifact) · search-scope governance (narrow-by-default, multi-system `--system`) · human-managed areas (`temp/`, `logs/`) không bị tool đụng | Đây là các rule "important" hay bị CR tooling vô tình xói mòn | CLAUDE §3 rules #1–#13, §6 env; CR-022/052/017 |
| CR-H4 | **Precedence chain giữ nguyên**: content Truth→Wiki→History; artifact SOP→Contract→AIP→Guidelines→Skills→Wiki→Workspace; knowledge class đúng chỗ. Change không tạo "authority mới" cạnh tranh mơ hồ với doc hiện có (2 nguồn cùng claim source_of_truth cho 1 chủ đề) | Authority mơ hồ = ambiguity lâu dài, reviewer sau không biết tin đâu | CLAUDE §2; Spec §18 pattern (general vs profile khai quan hệ rõ) |

| ID | Check | Vì sao | Evidence / Ref |
|---|---|---|---|
| BATCH-1 | Từng CR pass §2 trước — batch review KHÔNG thay per-item review | Batch che khuyết item | — |
| BATCH-2 | Lập **shared-target matrix** (CR × file): ≥2 CR approved co-edit cùng file → plan **MỘT batch apply-AIP theo file-pass** (mỗi file sửa 1 lần) | Apply tuần tự từng CR trên cùng file = conflict/rework | Spec §13 (CR-034); AIP-939 tiền lệ |
| BATCH-3 | Dependency giữa CRs: CR nào giả định outcome CR khác → chốt **apply order** + điều kiện (approve lẻ có ổn không?) | Approve một nửa cặp phụ thuộc = trạng thái gãy | — |
| BATCH-4 | Id-collision scan cả batch (các CR cùng tháng, cross-branch) | Nhiều CR draft song song dễ đụng NNN | Spec §10 |
| BATCH-5 | Overlap intent: 2 CR giải cùng root cause? → gộp hoặc ghi rõ ranh giới per-surface | Double-fix / fix nửa vời | IR-14b tách 032/033 per theme |
| BATCH-6 | **Bảng DP tổng hợp**: gom mọi DP-* của các CR thành một bảng quyết định duy nhất cho PO (option, khuyến nghị, CR nào chờ DP nào) | PO quyết 1 lượt, không rải rác | CR-031 DP pattern |
| BATCH-7 | Aggregate blast radius: tổng footprint Truth/product/tooling của cả wave → quyết định apply 1 wave hay staged (nhóm rủi ro cao apply riêng, có gate giữa chừng) | Wave to fail giữa chừng khó lần | — |

## 4. Verdict & report format

- **RISK headline** (dòng đầu report): rủi ro lớn nhất nếu apply + rủi ro lớn nhất nếu KHÔNG apply.
- **Findings table**: `check_id | verdict PASS/FAIL/N-A | evidence (file:line / lệnh đã chạy) | note`.
- **Per-CR verdict** (một trong):
  - `APPROVE` — sẵn sàng approve as-is;
  - `APPROVE-WITH-CONDITIONS` — liệt kê DP cần PO chốt / sửa nhỏ trước apply;
  - `REVISE` — thiếu gì, trả về draft;
  - `REJECT` — lý do (ghi vào CR, move `rejected/`);
  - `PARK` — chưa đủ chín, để intake/backlog.
- **Batch report** thêm: bảng per-CR verdict + **apply order đề xuất** + shared-file matrix + bảng DP tổng hợp (BATCH-6).
- Reminder cuối report: *approved ≠ applied* — apply cần explicit request (SOP §5 Rule C) + apply-CR AIP + gates §13.

## 5. Ghi chú vận hành

- Check nào bị MISS lặp lại qua nhiều review → `checklist_update_candidate` (capture, HUMAN-gated) — checklist tự tiến hoá qua CR.
- Review chính thức một batch = deliverable task → chạy trong AIP workspace (per project rule), report lưu workspace, capture inbox bật.
- Checklist này KHÔNG thay lint: lint là gate máy (deterministic); checklist là gate người/AI (judgment).
