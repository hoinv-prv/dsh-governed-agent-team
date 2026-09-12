# aiws-aip — operation: create

> Operation of the `aiws-aip` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Create an AIP aligned with:
- SOP-first
- AI Work Contract
- AIP PLAN / EXEC / LOCAL
- Active Step Context
- Workspace-based execution
- Wiki-first knowledge usage

## Inputs
- task/request
- truth/SOP_MASTER.md
- truth/AI_WORK_CONTRACT.md
- relevant truth/wiki refs if available

## PRE-FLIGHT GATE — Artifact Lookup (HARD GATE)

⛔ **HARD GATE — phải thực hiện trước khi mở bất kỳ canonical artifact nào làm input.**

Với MỌI RD/BD/DD/spec dùng làm input, bắt buộc theo đúng trình tự sau:

1. **Lookup trước** — chạy `py .ai-work/tooling/lookup_wiki_source.py --query "<keyword>"` cho từng artifact
2. **Lấy path từ meta** — đọc kết quả, lấy `artifact:` path → mở file
3. **Index miss → escalate** — retry `--mode semantic`; chỉ fallback Glob/Grep sau khi cả 2 miss, và ghi rõ đã escalate

❌ **FORBIDDEN patterns — không có ngoại lệ:**
- Glob/Grep trực tiếp cho artifact file mà không qua wiki lookup trước
- Suy luận path từ artifact khác user đã cung cấp (vd: user cho path DD → tự Glob BD/RD cùng thư mục)
- Bỏ qua lookup với lý do "đã biết chỗ rồi" hoặc "user đã cho path rồi"

✅ **Kể cả khi** user cung cấp path một artifact trực tiếp → tất cả artifact input khác (BD/RD/IT/spec...) vẫn phải qua wiki lookup riêng.

## Outputs
- chosen AIP type
- clarified understanding draft
- drafted AIP content
- unresolved questions if any

## Flow

**[STEP 0a — ALLOCATE AIP ID — MANDATORY, làm TRƯỚC khi draft]** (CR-015 **v2**)
1. Precheck `.ai-work/account_info.yaml` tồn tại (`account_id` + counter). Thiếu → DỪNG, hỏi HUMAN rồi `py .ai-work/tooling/account_id.py set --account-id <id>` (CR-AIWS-2026-06-016); KHÔNG tự bịa `account_id`. (Nghi ngờ file lỗi → `account_id.py validate --repair`.)
   - **Môi trường phi-tương tác** (CI, clone sạch, worktree, subagent không có HUMAN ngồi cạnh): chạy `py .ai-work/tooling/account_id.py resolve`. Thứ tự cố định **file → env `AIWS_ACCOUNT_ID` → namespace AIP duy nhất → DỪNG**, theo Approved Deviation `AI_WORK_CONTRACT` §6 (2026-08-17, CR-AIWS-2026-08-076).
   - **Cấm tự bịa khi mơ hồ vẫn nguyên vẹn:** `resolve` **rc≠0** khi có **0** hoặc **≥2** namespace và không có env — khi đó **DỪNG, hỏi HUMAN**, không được tự chọn một cái. `account_id` là namespace của id AIP và của thư mục workspace: chọn sai là gán AIP cho nhầm người, im lặng.
   - Giá trị không đọc từ file được ghi kèm `provisional: true`. AIP tạo dưới id provisional phải theo mục **AIP provisional** dưới đây.
2. Lấy id: `py .ai-work/tooling/allocate_aip_id.py --kind exec` (hoặc `plan`/`local`) → ghi vào `artifact_id`.
3. Ghi file AIP mới vào thư mục theo account: `.ai-work/aip/<account_id>/<kind>/AIP-<KIND>-NNN-<slug>.md` (KHÔNG để flat; legacy flat AIPs giữ nguyên).
**KHÔNG tự chọn số bằng glob max+1.** Allocator đọc/ghi per-account counter trong `account_info.yaml`; id format `AIP-<KIND>-NNN` (folder là namespace), gaps khi cancel chấp nhận được.

**[AIP provisional — khi `account_id` chưa được HUMAN khai]** (CR-AIWS-2026-08-076 C4, DP-076-B = a+b)
Nếu `account_info.yaml` mang `provisional: true`, AIP vừa tạo **phải**:
1. giữ `status: draft` — **không** được để `aiws-aip run start` flip sang `active` cho tới khi ratify;
2. mang một dòng trong `Known Open Points`: `account_id là PROVISIONAL (nguồn: <env|namespace>) — cần HUMAN ratify bằng py .ai-work/tooling/account_id.py set --account-id <id>`.

Lý do cổng nằm ở đây chứ không chỉ là một cảnh báo: một AIP đã `active` là một AIP **đang được thi hành dưới tên một người**. Nếu tên đó do máy suy ra, thì thứ hỏng không phải một trường metadata mà là **quy trách nhiệm** — và nó hỏng im lặng. Ratify là thao tác một dòng; chạy dưới id sai thì phải truy lại toàn bộ.

0. **[WIKI LOOKUP]** Với mỗi input artifact cần đọc (RD/BD/DD/spec):
   - `py .ai-work/tooling/lookup_wiki_source.py --query "<keyword>"`
   - Đọc meta → lấy path artifact → mở file
   - Index miss → escalate (retry `--mode semantic` → raw search theo `document_search_guidelines.md`)
   - **Search-plan budget (CR-AIWS-2026-07-003 E4):** plan 3–5 query TRƯỚC (1/input-group), pre-flight dùng
     `--limit 5`; ~1 call/input (+1 `wiki_relations --relations` khi cần related docs). Vượt ~2× số input →
     dùng reading-kit digest hoặc hỏi HUMAN (query quá loãng). Chi tiết: `aiws-wiki lookup` SKILL §Search-plan discipline.
1. Infer task understanding draft
1a. **[OPERATING MEMORY — đọc TRƯỚC khi chia step]** (CR-AIWS-2026-08-029, DP-029-A = a)
   - `py .ai-work/tooling/read_operating_memory.py` — in bốn nhóm lập kế hoạch (`cost_sizing` ·
     `required_order` · `where_to_look` · `rejected_option`). `--all-groups` khi task chạm tooling/môi
     trường; `--groups <a,b>` khi muốn hẹp hơn.
   - Đọc rồi **cân nhắc** khi quyết: chia bao nhiêu step · thứ tự nào · đọc gì trước · phương án nào
     đã từng bị bác. Fail-soft: kho thiếu/rỗng/hỏng vẫn exit 0 — **không** chặn việc tạo AIP.
   - **KHÔNG dán digest vào file AIP.** AIP là stable control; một hint runtime nằm trong đó sẽ mục và
     sẽ bị đọc như thẩm quyền. Chỉ **kết luận của bạn** mới vào AIP — một câu trong `Notes / Constraints`
     của step tương ứng, dạng *"vì <mục L2> nên tách STEP-03"*.
   - Đây là **gợi ý tham khảo, KHÔNG phải rule**. Một mục L2 không bao giờ là lý do duy nhất để quyết;
     thứ cần *tuân thủ* thì thuộc canonical, không thuộc kho này.
1b. **[REVIEW-TASK BRANCH — CR-AIWS-2026-07-044]** Task = **review** một artifact đã tồn tại (CR/IR, spec/guideline, design doc, batch CR wave — dấu hiệu: deliverable là **báo cáo review advisory**, KHÔNG mutate artifact gốc)?
   - **Quyết định review-branch (self-contained, KHÔNG phụ thuộc doc ngoài):** deliverable là **báo cáo advisory** + KHÔNG mutate artifact gốc → đây là review task. Nguồn phân lớp: Truth → Project Wiki → Local → Common → History (precedence CLAUDE.md §2). Doc-type gate: dense single doc → hybrid free-read + checklist tối thiểu; cross-doc / CR wave → M2→M1 đầy đủ.
   - **Cơ chế review = canonical đã ship (neo vào đây, KHÔNG hardcode path):** verdict/reproducibility theo `Runtime_Review_Methodology_MVP` (leg-rubric, ensemble, headline, finding-trace — resolve vị trí qua `lookup_wiki_source.py --query "runtime review methodology" --source-type methodology_spec` nếu cần), thực thi qua skill `aiws-review-plan` (→ `review_plan.md`) rồi `aiws-runtime-review-checklist` (→ `06_runtime_review_checklist.md`). **Phần BẮT BUỘC — luôn có ở mọi bản cài** (bắt buộc là việc **KHAI** step scaffold trong AIP — xem bullet dưới; không phải việc gọi skill lúc create).
   - **Helper phương pháp (OPTIONAL — resolve-by-role qua wiki, KHÔNG hardcode `docs/`):** `lookup_wiki_source.py --query "review method guidelines M2 M1 doc-type gate" --source-type process_guideline` → nếu dự án có doc phương pháp review (mỗi dự án register **bản của mình**), đọc mục tương đương "khi nào là review" / "mô hình nguồn phân lớp" / "doc-type gate". **Lookup miss → BỎ QUA, không chặn flow** (2 bullet trên đã đủ để quyết định + scaffold); doc reusable mà chưa register → append `retrieval_gap` capture (Flow step 4b.3).
   - Substantive / cần tái lập / có ensemble / CR wave → **create KHAI, run THỰC THI** (CR-AIWS-2026-08-094, DP-094-A = c′): `create` ghi vào AIP một step **review-scaffold ngay sau STEP-00** (thường là STEP-01) với `Recommended Skills: aiws-review-plan · aiws-runtime-review-checklist` và `Expected Outputs: review_plan.md · 06_runtime_review_checklist.md (workspace)`; **KHÔNG gọi hai skill lúc create** — đích ghi của chúng là task workspace, thứ chỉ tồn tại sau `aiws-aip run start`. Khi `run` trỏ ASC tới step đó thì gọi `aiws-review-plan` (→ `review_plan.md`) rồi `aiws-runtime-review-checklist` (→ `06_runtime_review_checklist.md`, leg-rubric, verdict khởi tạo `NOT_CHECKED`). Cả hai `user-invocable: false` — caller là **step review-scaffold của AIP** (được create khai, run thực thi), hoặc một review agent.
   - Task nhỏ, scope hẹp → ad-hoc N-step vẫn hợp lệ (§5.6) nhưng **phải ghi lý do** trong AIP.
   - Review **template** (BD/DD…) là **project-local** — AIWS KHÔNG ship (CR-033 DP-033-2=b): dùng `--template <path>` tới template của project, hoặc EXEC template + checklist nội dung.
2. Decide if AIP is needed
3. Choose AIP type
4. Ask minimal clarification if needed
4b. **[TASK LENS — front-load inputs]** aiws-aip create resolves inputs up front. Once intent is clear (Intent-first):
   1. **Infer first (primary):** from intent, decide which **subject** docs (RD/BD/DD/spec) and **reference standards** (guideline/checklist/template/SOP) you need — no lens required.
   2. **Lens = additive checklist:** pick a Task Lens or **No-Lens**. If a lens, look it up in `.ai-work/wiki/task_lens_presets/` and use its `relevant_source_types` + `relevant_reference_types` to catch artifacts you missed. It only adds — never bounds/filters.
   3. **Inputs = inference ∪ lens** (never lens-only). Resolve via Flow step 0, fill into `## Required Wiki Inputs` + `## References to Read First`.
      - **Resolving reference standards** (guideline/checklist/template/SOP): query the index by the standard's NAME keywords ("requirement template", "design review checklist"), not the reference_type label; they usually live in `product/wiki_guidelines/`, the AIP templates dir (`TEMPLATE_DIR` — see Step 5), `.ai-work/procedural/`, or carry `source_type` `process_guideline`/`process_template`/`sop` (use `lookup_wiki_source.py --source-type`). Bridge: `*_template→process_template`, `*_guideline/*_checklist/naming_convention/*_playbook→process_guideline`, `sop→sop` (`Task_Lens_Spec` §B). Not findable → Deferred lookup + append a `retrieval_gap` capture.
   4. **Deferred lookups:** for anything unresolved, record `doc + lens` under `## Selected Task Lens / Mode` for aiws-aip run to resolve. No-Lens ⇒ infer fully, skip presets, leave empty. Ref: `Task_Lens_Spec_MVP` §C/§F.
5. **Read template and draft**
   **`TEMPLATE_DIR` (install-portable, CR-AIWS-2026-06-050):** for each template file, read `.ai-work/aip/templates/<file>` if it exists, else `product/aip_templates/<file>` (downstream installs ship only `.ai-work/`; the source repo has both). Template reads below are `TEMPLATE_DIR`-relative.
   **`--template <id|path>` (optional; agent-agnostic):** if the args carry `--template`, instantiate THAT template instead of the default menu. **ID** = case-insensitive basename via alias table (under `TEMPLATE_DIR`): `EXEC→AIP_EXEC_TEMPLATE.md` · `PLAN→AIP_PLAN_TEMPLATE.md` · `LOCAL→AIP_LOCAL_TEMPLATE.md` · `APPLY_CR→AIP_EXEC_APPLY_CR_TEMPLATE.md`. **Review templates (DD/BD…) là PROJECT-LOCAL — AIWS KHÔNG ship** (CR-AIWS-2026-07-033 T5, DP-033-2=b): project tự tạo template review của mình trong `TEMPLATE_DIR` và gọi bằng **PATH** (hoặc basename file thật) — alias cho template không ship đã bị gỡ để hết quảng-cáo-file-không-tồn-tại. **PATH** = a value containing `/` or ending `.md`, resolved from project root. **If the resolved template does not exist → STOP and ASK the HUMAN; NEVER silently fall back to EXEC.** Derive `allocate_aip_id --kind` from it: PLAN→`plan`, LOCAL→`local`, all EXEC variants (incl. APPLY_CR và mọi review template project-local)→`exec`. (aiws-aip create does NOT read `instance.yaml` / agent state — whoever calls supplies `--template`.)
   Before writing a single line of the AIP body:
   - a. Read `<TEMPLATE_DIR>/AIP_EXEC_TEMPLATE.md` (or `AIP_PLAN_TEMPLATE.md` / `AIP_LOCAL_TEMPLATE.md` as appropriate) — also see `<TEMPLATE_DIR>/AIP_EXEC_QUICK_REF.md` for a concise reference
   - a1. **Apply-CR tasks** (applying an already-approved CR): instantiate `<TEMPLATE_DIR>/AIP_EXEC_APPLY_CR_TEMPLATE.md` (lint-conformant condensed EXEC; CR-AIWS-2026-05-037 Option C), not the full EXEC template.
   - b. Note required sections from §6.3 of AIP_Detail_Spec_MVP.md (for EXEC AIPs):
     `## Objective`, `## Execution Scope`, `## Expected Outputs`, `## References to Read First`,
     **`## Execution Steps`** (exact name — NOT `## Steps`), `## Current Risks / Constraints`,
     `## Done Criteria`, `## Self-check / Review Points`, `## Re-plan Rule`, `## Re-plan Log`
   - c. Draft using the template structure directly — do NOT rely on memory of prior AIPs
   - d. Confirm all required sections present before moving to Step 6
6. Draft AIP — **stamp front-matter `template_source: <template-id>`** (write-once provenance = basename of the instantiated template, e.g. `AIP_EXEC_TEMPLATE` / `AIP_EXEC_APPLY_CR_TEMPLATE`; default menu → `AIP_EXEC_TEMPLATE`). Front-matter ONLY (never a section body), modeled on `runtime_workspace` — do NOT hand-edit. (Consumed by the Agent-Pack run-gate conformance check.)
7. Self-check — **run the checklist below before reporting AIP done**

## Self-check before reporting AIP done (mandatory)

Run through ALL items. Do NOT report "AIP created" until every item passes.

**Format checks:**
- [ ] AIP id obtained via `allocate_aip_id.py` (NOT hand-picked / glob max+1) — see Flow STEP 0a
- [ ] Section `## Execution Steps` present (NOT `## Steps` or any other name)
- [ ] All step headings use exactly: `### Step: STEP-nn — <title>` format
- [ ] Each step has ALL required fields on their own lines (not bold inline):
  `Objective:` / `Recommended Mode:` / `Applicable Guidelines:` /
  `Inputs:` / `Expected Outputs:` / `Done Condition:` / `Notes / Constraints:`
- [ ] **`Applicable Guidelines` = path tính từ PROJECT ROOT** (CR-AIWS-2026-08-097 C3) — trỏ file bên trong một skill package thì ghi full path `.ai-work/procedural/skills/<skill>/…`, đừng ghi `references/x.md` kiểu tương đối như SKILL.md dạy; `lint_aip` resolve từ project root nên path tương đối trần ra `ref_missing`
- [ ] STEP numbering is sequential — no gaps (STEP-01, STEP-02, STEP-03…)
- [ ] All required sections per §6.3 present (see Step 5b list above)
- [ ] Front-matter carries `template_source: <template-id>` (write-once basename; default → `AIP_EXEC_TEMPLATE`) — stamped every run; front-matter only (CR-AIWS-2026-06-050)

**Content checks:**
- [ ] **Đã chạy `read_operating_memory.py` trước khi chia step** (Flow 1a) — mục nào ảnh hưởng tới kế hoạch thì nêu trong AIP dưới dạng câu của người viết (`Notes / Constraints` của step tương ứng), KHÔNG dán digest. Kho trống ⇒ tick "đã đọc, không có mục nào liên quan" là hợp lệ (CR-AIWS-2026-08-029, DP-029-B = a)
- [ ] Governance Note accurately reflects scope — especially for mixed-governance AIPs (see Rules below)
- [ ] Done Criteria reference Gate compliance when applicable
- [ ] When encoding canonical wording into a SKILL.md (AI-only surface), it is written TERSELY — state trigger/steps/done just clearly enough to act; do NOT transcribe a CR's `change_summary` prose. Specs/templates (HUMAN-facing) keep full wording.

**CR-draft checks (khi task = draft CR — lessons wave 2026-07-14; canonical CR-AIWS-2026-07-035):**
- [ ] **CR id mint bằng `allocate_cr_id.py`** (spec §10 — CR-AIWS-2026-08-020): mint tại thời điểm draft + re-verify ngay trước khi ghi file CR; KHÔNG manual scan/max+1 khi tool hiện diện (manual union scan = fallback-only). Lesson: same-day race 013→019 (CR-2026-08-019 r3).
- [ ] **Concurrent-CR §11.1 kể cả cùng-session:** grep mọi CR open/draft — GỒM CẢ CR draft trong cùng session/wave — cho shared target files; overlap → reciprocal `related_cr` + region-ownership + batch-apply note (§13). (AIP-942 M-01: 2 CR cùng session cùng sửa `lint_wiki.py`, 5/6 reviewer độc lập bắt.)
- [ ] **CR đổi tool behavior → enumerate test files:** grep `.ai-work/tests/` theo tên tool bị sửa; test đang assert behavior CŨ phải vào §2 Target — không enumerate thì gate của chính CR tự gãy tại apply (lesson lặp ×3: test_wiki_regression / test_quick_install / test_build T6).
- [ ] **Expected Output của CR chưa mint id → khai bằng THƯ MỤC** (`product/change_requests/`), KHÔNG khai `CR-…-NNN-<slug>.md` (CR-AIWS-2026-08-065): placeholder không khớp file thật ⇒ `lint_all --scope task` tính footprint = git dirt ∩ declared → `product/` rơi ra ngoài → không escalate whole-tree và in "OK — no findings" trên một CR chưa hề được lint (CAP-1054-02). Đã lỡ khai theo file → finalize bằng `--footprint-paths product/change_requests,<ws>`; tool nay cảnh báo `scope_task_footprint_unmatched` khi rơi vào ca này.
- [ ] **Sweep guardrail trong CR phải khai carve-out mặc định:** quote-context (`change_requests/` + `intake/` — CR/IR tự trích pattern làm evidence) + immutable zones (`history/`, `workspaces/`, `releases/`) không tính hit mới (AIP-944 verify).

**Tooling gate (mandatory):**
- [ ] `py .ai-work/tooling/lint_aip.py --path <aip-file>` → **0 errors**

## Capture during AIP creation

### AIWS system issue capture

If AI discovers and fixes a problem during `aiws-aip create` — a lint failure, a
missing required section, incorrect template guidance, a schema mismatch, or
any other AIWS system issue — **capture it as a candidate**.

- **If workspace already exists:** append to `08_capture_inbox.jsonl` immediately after the fix.
- **If no workspace yet** (AIP still being drafted): note the problem inline,
  then create the capture entry as the first action after `aiws-aip run start`.

Use `type`: `aip_template_improvement_candidate` |
`run_aip_improvement_candidate` | `guideline_improvement_candidate` |
`tooling_opportunity_candidate`.

Set `candidate_kind: aiws_system_improvement`.

See: `.ai-work/procedural/wiki_candidate_capture_playbook.md` §15.

### Reusable artifact lookup miss → Pre-flight Pending Capture (MANDATORY)

Khi wiki lookup miss cho một artifact và artifact đó thuộc loại **reusable**
(template, process doc, checklist, shared spec, guideline — bất kỳ artifact nào
dùng làm "structural reference" hoặc "format template"), bắt buộc thực hiện ngay:

1. Trong AIP input table: đặt `Capture flag = [retrieval_gap]`
2. Append entry vào section `## Pre-flight Pending Captures` trong AIP file **NGAY LẬP TỨC**:
   ```
   - [PENDING] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="<tên artifact>" lookup_query="<query đã dùng>" reason="<tại sao artifact này reusable>"
   
   `suggested_target` **bắt buộc** thuộc `CAPTURE_TARGET_ENUM` (`lint_workspace.py`). Thiếu nó thì sweep để trống và cảnh báo stderr — **không tự điền mặc định** (CR-AIWS-2026-08-025).
   ```
3. `aiws-aip run start` sweep section này và import entry vào `08_capture_inbox.jsonl` **tự động** (CR-056: `run_aip.py start` thực hiện sweep + mark `[IMPORTED YYYY-MM-DD]`; fail-soft từng dòng, idempotent). AI chỉ cần verify log của tool ở Flow 1b, không phải import tay.

**LOẠI TRỪ THEO ZONE — Truth không sinh `[retrieval_gap]` (CR-AIWS-2026-08-130).**
Artifact nằm dưới `.ai-work/truth/**` (Truth zone, gồm cả `truth/canonical/**`) **KHÔNG** đánh
`[retrieval_gap]` và **KHÔNG** vào `## Pre-flight Pending Captures` — kể cả khi nó khớp mọi dấu
hiệu "reusable" bên dưới. Truth input được khai trực tiếp bằng path ở `### Required Truth Inputs`,
một section **riêng không có cột `Wiki Source ID`**; nó không đi qua wiki lookup vì nó **đứng trên**
tầng routing đó trong precedence (`Wiki_Truth_History_Spec_MVP` §2 tách zone có chủ đích; §11.1/§11.2
đặt Truth đọc TRƯỚC và đọc vì task chạm SOP/Contract, không vì một lookup route tới nó).
Đo 2026-08-29: **0/346** node trong index trỏ vào `.ai-work/truth/` — đó là ranh giới, không phải sót.
Truth vẫn tra được qua object node `SRC-CPT-truth`.

**Dấu hiệu artifact reusable** *(áp dụng SAU khi đã loại trừ Truth zone ở trên)***:**
- Tên có pattern: `TEMPLATE_*`, `*_TEMPLATE*`, `*_GUIDELINES*`, `*_CHECKLIST*`, `*_SPEC*`
- Nằm trong thư mục: `templates/`, `guidelines/`, `procedural/`, `09_processes/`
- Được dùng làm "structural reference" hoặc "format template" trong AIP input

**KHÔNG defer sang sau `aiws-aip run start`.** Entry trong `## Pre-flight Pending Captures`
là evidence vật lý — tồn tại ngay trong AIP body dù workspace chưa được tạo.

## Rules
- **Multi-system (CR-AIWS-2026-06-017):** in a `multi_system: true` project, establish the task's **active system** up front (ask the HUMAN if unstated); pass `--system <id>` on every input lookup and carry it in the brief. If a lookup errors for a missing system, STOP and ASK — never auto-set/guess. Single-system → no effect.
- If uncertain between PLAN and EXEC → choose PLAN
- Do not create overly large AIPs
- AIP is stable control, not runtime notebook
- Each step should be materializable into Active Step Context
- Follow template section names exactly — do not rename required sections

### Mixed Governance Pattern

Khi AIP chứa cả no-CR steps (tooling/skills) lẫn CR-required steps (canonical docs):

1. **Governance Note** phải liệt kê RÕ cả 2 loại, ví dụ:
   - STEP-01 đến STEP-04: tooling/skill changes — không cần CR
   - STEP-05 đến STEP-06: canonical doc changes — HARD GATE (AIWS-Product-Owner approve; wiki-meta → Wiki-Manager)
2. **CR-required steps** dùng `Recommended Mode: Canonical-edit`
3. **HTML comment** phản ánh governance NGHIÊM NGẶT NHẤT trong AIP — không copy-paste từ AIP khác
4. **Governance Note** đặt ở đầu body, trước `## Objective`

## Assigned Agent step field (CR-AIWS-2026-07-018; activation CR-AIWS-2026-08-044 C0)
Optional step field `Assigned Agent: <desk_id | auto>` — step dự kiến do agent execute qua
`run_agent.py start <instance> --aip <AIP này>` (TW-reuse; per-run namespacing `runs/<run_id>/`);
`auto` = capability routing resolve desk (CR-AIWS-2026-08-045). **ABSENT = DEFAULT = KHÔNG dispatch —
main session thực thi như AIWS thuần.** Chỉ định agent/desk là OPTIONAL feature; dự án có thể tắt cả
cơ chế qua pack `pack_config.yaml dispatch_enabled: false`.
create: điền khi plan giao việc cho agents (collaboration = 1 driving AIP, các step gán agent);
kèm optional `Executor:` (main_session | claude_subagent — CR-AIWS-2026-08-044 C4, absent = desk
default; lựa chọn plan-time của HUMAN/AIP).
run / ASC: field được surface; dispatch mỗi run qua router confirm TRỪ khi DP-913-D pre-auth
(AIP active + run nằm trong assigned set — tool cưỡng chế stage-3; ngoài list vẫn confirm per-run).

## Difficulty / Kind step fields (CR-AIWS-2026-07-059)
Optional `Difficulty:` (low|medium|high) + `Kind:` (task-kind tags: triage, plan, code, patch_proposal,
sql, test_design, review, research, organize, canonical_edit) — capability-routing inputs. create: điền để
route step theo độ khó/kỹ năng (khớp `capability.complexity_ceiling` + `task_kinds` của agent). Surface vào ASC.
Routing chỉ chạy khi step opt-in qua `Assigned Agent:` (C0); Difficulty cũng chọn execution tier trong desk
đã chọn (`tiers_supported`, cheapest-capable — CR-AIWS-2026-08-045).
