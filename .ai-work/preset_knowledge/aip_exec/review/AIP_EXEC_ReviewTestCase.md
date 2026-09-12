---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-review-testcase
title: Review Test Case (Coverage / Regression / Quality Gap Report)
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when review scope and build context are already confirmed>"
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Review Test Case

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

AI review bộ testcase theo 5 dimensions (build coverage, regression risk, testcase quality, execution priority, known blockers), output gap report theo save path được chỉ định, áp dụng fix mode nếu BrSE yêu cầu.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: test_design
- Reason: Reviewing a testcase set across 5 dimensions (build coverage, regression risk, quality, priority, blockers) — read in test-coverage terms against viewpoint/spec/design.
- Search/execution effect: Prioritises `test_case`, `unit_test_spec`, `requirement_definition`, `basic_design`, `detailed_design_combined` + object kinds (`function`/`screen`) when ordering the reading surface.
- Expansion allowed: yes — pull the finalized test viewpoint / spec / build change log to ground a gap finding.

## Execution Scope

### In Scope

**Dùng AIP này khi:**
- Task review testcase đã có scope rõ ràng
- BrSE muốn AI execute review và output gap report
- Review gắn với build cụ thể hoặc viewpoint đã finalize

**Review bao gồm:**
- Input understanding + reviewer confirmation (Gate U2)
- Coverage mode selection (Viewpoint / Spec-derive / SRS-wiki / Heuristics / No-baseline)
- 5 review dimensions: D1 Build Coverage, D2 Regression Risk, D3 Testcase Quality, D4 Execution Priority, D5 Known Blockers
- Self-review gate, severity classification, go/no-go decision
- Gap report generation theo save path được chỉ định
- Optional fix mode (auto-fix Minor/Note hoặc Major clarity) khi BrSE yêu cầu

### Out of Scope

**KHÔNG dùng AIP này khi:**
- Scope còn thay đổi lớn
- Chỉ cần quick personal checklist (dùng Member AIP)
- Focus là PM-level tracking (dùng PM AIP)

**Review KHÔNG được:**
- Fix coverage gap (missing testcase) — never auto-fixed, kể cả Mode C
- Fix logic issue (wrong expected result) — never auto-fixed, kể cả Mode C
- Overwrite file testcase gốc — fixes luôn save vào file `_fixed_<date>` riêng

### Workspace Preconditions

Trước khi execute, tối thiểu phải có:
- [ ] Testcase document (Excel hoặc Markdown)
- [ ] Scope review rõ ràng (in-scope / out-of-scope)
- [ ] Ít nhất một trong: viewpoint, spec, hoặc AI heuristic mode được chấp nhận

---

## Expected Outputs

| # | Output | File name | Format | Save path |
|---|---|---|---|---|
| O-01 | Input understanding confirmation | (inline — Input Understanding section) | Markdown section | AIP / workspace findings |
| O-02 | Viewpoint alignment check | (inline) | Markdown table | workspace findings / draft |
| O-03 | Review findings (coverage / logic / clarity) | (inline) | Markdown tables | workspace draft |
| O-04 | Issue list with severity / owner / action | (inline) | Markdown table | workspace draft |
| O-05 | Re-review / handoff plan | (inline) | Markdown table | workspace draft |
| O-06 | Gap report (AI-generated per execution flow) | `REVIEW_TC_GAP_REPORT_<build>_<YYYY-MM-DD>.md` | Markdown | `04_generated_outputs/` trong task workspace |
| O-07 | SRS Wiki (chỉ khi field 7a = A) | `SRS_WIKI_<build>_<YYYY-MM-DD>.md` | Markdown | save path / task workspace |
| O-08 | Proposed viewpoint file (chỉ Mode B) | per save path | Markdown | task workspace |
| O-09 | Fixed testcase (chỉ Fix mode B/C) | `<testcase>_fixed_<YYYY-MM-DD>.md` | Markdown | task workspace (NEVER overwrite original) |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu đến từ PLAN phase.
Hoặc `direct` — khi review scope và build context đã confirmed trước, không cần PLAN phase.

### Required Inputs

| Input | Description | Required / Optional |
|---|---|---|
| I-01 Testcase document | target review (field 5 trong intake form) | Required |
| I-02 Finalized test viewpoint | coverage baseline (field 6) | Recommended |
| I-03 Requirement / spec / design | logic baseline (field 7) | Recommended (nếu không có viewpoint) |
| I-04 Build release notes / change log | list of changes in this build (field 2) | Optional* |
| I-05 Targeted bug fix list | what exactly is fixed | Optional* |
| I-06 Known build issues list | defects already known in this build | Optional* |
| I-07 Clarification results | confirmed business rules | Optional |
| I-08 Open issue / assumption list | uncertainty visibility | Optional |
| I-09 Common review checklist | standard criteria | Optional |
| I-10 Prior review comments | continuity | Optional |

*Strongly recommended khi review gắn với build cụ thể. Không có build context → D1, D2, D5 sẽ bị skip.

**Build Context (điền khi có build):**

| Field | Value |
| ----- | ----- |
| Build ID / version | |
| Build type | feature release / bug-fix / CR / mixed |
| Key changes in build | |
| Known issues in build | |
| Downstream executor | offshore / QA internal / BrSE / UAT |
| Execution deadline | |

**Review Metadata (điền khi nhận task):**

<!-- Discrete recordable slots migrated from legacy "A. Metadata" (BrSE scaffold). Fill before STEP-00. -->

| Field | Value |
| ----- | ----- |
| Review Target | *(testcase document name / version)* |
| Test Viewpoint Reference | |
| Reviewers | |
| Testcase Author | |
| Related Documents | |
| Related AIPs | |
| Input Understanding Status | |
| Review Viewpoint Status | |

---

## Context Summary

<!-- Recorded section migrated from legacy "C. Context Summary" (BrSE scaffold). Records WHY this review is happening now and WHICH review round it is. AI confirms/records these at STEP-00. -->

- Background ngắn của bộ testcase
- Vì sao cần review lúc này
- Downstream impact nếu testcase có issue mà không phát hiện sớm
- Review round hiện tại là round mấy nếu có

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. BrSE confirm trước khi findings được finalize. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Testcase | `<test objective, số TC entries, scope/boundary>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Viewpoint | `<test viewpoint coverage understanding>` | `<assumptions>` | `<gaps>` | ⬜ pending |
| I-03 Spec / design | `<logic baseline understanding, intended downstream usage>` | `<assumptions>` | `<known pending/open-point>` | ⬜ pending |

**Reviewer / BrSE Confirmation Rule:**
- BrSE hoặc reviewer phải confirm working-level understanding trước khi findings được coi là hợp lệ
- Nếu có phần input chưa đủ chắc → giữ visible như uncertainty note

---

## References to Read First

**Required:**
- `<path to testcase document (I-01)>`

**Recommended:**
- `<path to finalized test viewpoint (I-02)>`
- `<path to requirement / spec / design (I-03)>`
- `<path to build release notes / change log (I-04)>`

**Optional:**
- `<path to known build issues list (I-06)>`
- `<path to clarification results (I-07)>`
- `<path to common review checklist (I-09)>`
- `<path to prior review comments (I-10)>`
- **Runtime Review Checklist (optional):** materialize a per-run `06_runtime_review_checklist.md` via the `aiws-runtime-review-checklist` skill — concrete, deterministic per-item checks selected from the common review checklist; verdicts filled during execution. Method templates: `procedural/skills/aiws-runtime-review-checklist/runtime_review_breakdown_strategies.md` (co-located with the skill).

---

## Current Risks / Constraints

| # | Risk | Likelihood | Impact | Mitigation |
| - | ---- | ---------- | ------ | ---------- |
| R-01 | AI hiểu sai scope review → findings sai hướng | Medium | Review không valuable; phải redo | BrSE confirm Input Understanding trước khi finalize |
| R-02 | Viewpoint chưa finalize được dùng làm baseline → coverage assessment sai | Medium | Coverage gap missed hoặc false gap | Verify viewpoint status trước khi bắt đầu (STEP-03) |
| R-03 | Severity over-classified → testcase author ưu tiên sai | Medium | Effort bị lãng phí vào minor issue | BrSE spot-check Major/Critical findings trước khi handoff |
| R-04 | Build change log không đầy đủ → D1/D2 assessment thiếu | Medium | Coverage gap bị bỏ sót | Note "change log incomplete" trong D1 output; verify với Dev team |

**Downstream Impact / Proceed Rule:**

| Downstream Task | How review result affects it | Blocked by which severity |
| --------------- | ---------------------------- | ------------------------- |
| Test execution (offshore) | unsafe if steps/expected result unclear | Critical/Major |
| QA execution | weak if coverage gap exists | Major |
| UAT preparation | risky if business logic wrong | Major |
| Regression suite | inconsistent if cases not structured | Medium |

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ open point review nào (input chưa chắc, viewpoint chưa finalize, change log incomplete) vào file trên. Open point blocking → confirm với BrSE trước khi tiếp.

---

## Workspace Execution Rule

All runtime state (findings, drafts, gap report, open points) → workspace files. AIP này read-only trong execution.
- Active Step Context
- Queue
- Findings
- Open Questions (`05_open_questions.md`) — Gate U3
- Draft Output / generated gap report
- Capture Inbox

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
<!-- Gate U1 — Universal. Bắt buộc cho MỌI task substantive. Skip chỉ khi BrSE explicit ủy quyền (ghi ủy quyền vào workspace findings). -->

Objective:
Viết ra ý hiểu về task review (scope review in/out, testcase target, expected output = gap report, Done definition, assumptions) và dừng chờ BrSE confirm trước khi sang STEP-01. Đọc context cụ thể của task trước. Nếu BrSE đã điền intake form trong AIP, dùng giá trị đó thay vì hỏi lại.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1

Inputs:
- AIP PLAN handoff / user request
- I-01 Testcase (overview), scope review declaration
- Build Context (nếu có)
- Review Metadata slots (Review Target, Test Viewpoint Reference, Reviewers, Testcase Author, Related Documents, Related AIPs, Input Understanding Status, Review Viewpoint Status)
- Context Summary (background ngắn của bộ testcase, vì sao cần review lúc này, downstream impact, review round hiện tại là round mấy nếu có)

Expected Outputs:
- Task understanding note trong workspace (findings/ hoặc dedicated file)
- Review Metadata table điền (Review Target, Test Viewpoint Reference, Reviewers, Testcase Author, Related Documents, Related AIPs, Input Understanding Status, Review Viewpoint Status)
- Context Summary điền — đặc biệt review round hiện tại là round mấy
- BrSE confirmation evidence (user message hoặc ghi chú)

Done Condition:
BrSE explicit confirm ý hiểu (hoặc explicit ủy quyền skip gate); Review Metadata + Context Summary (incl. review round) đã ghi.

Notes / Constraints:
- Không làm gì khác ngoài clarify/confirm ở step này.
- Nếu BrSE chỉnh hiểu biết → update note rồi re-confirm trước khi sang STEP-01.
- Không tự suy luận ngoài protocol — nếu thiếu input, dùng intake form ở STEP-01 để hỏi BrSE.
- Ghi Context Summary: background ngắn của bộ testcase, vì sao cần review lúc này, downstream impact nếu testcase có issue mà không phát hiện sớm, review round hiện tại là round mấy nếu có.
- Điền Review Metadata slots: Review Target (testcase document name / version), Test Viewpoint Reference, Reviewers, Testcase Author, Related Documents, Related AIPs, Input Understanding Status, Review Viewpoint Status.

Workspace Actions:
- Write task understanding → workspace
- Fill Review Metadata table + Context Summary (incl. review round)
- Log BrSE confirmation

### Step: STEP-01 — Intake — gather review inputs (one-shot form)

Objective:
Thu thập đủ input để review. Nếu BrSE chưa điền đủ thông tin trong AIP, AI present intake form này ngay (one-shot), không hỏi từng câu trước.

Recommended Mode:
Clarifying

Applicable Guidelines:
_(none)_

Inputs:
- I-01 Testcase, I-02 Viewpoint, I-03 Spec/design, I-04 Change log, I-06 Known build issues (bất kỳ cái nào BrSE có)

Expected Outputs:
- Intake form đã điền đủ (11 fields) — đủ để chọn coverage mode và chạy dimensions

Done Condition:
Đủ tối thiểu: testcase (field 5) + downstream (field 4) + fix mode (field 9) + output format (field 8) + language (field 11). Field còn thiếu → ghi rõ và infer default.

Notes / Constraints:
- Intake form (present nguyên văn nếu thiếu input):
  - 1. Build: [name/version]
  - 2. Change log: A Có (paste) | B Không có
  - 3. Known build issues: A Có (paste) | B Không có
  - 4. Downstream: A Offshore | B QA internal | C BrSE | D UAT | E Khác → specify
  - 5. Testcase: A Paste nội dung | B File path (.md hoặc .xlsx)
  - 6. Viewpoint (finalized): A Có (paste hoặc file path) | B Không có
  - 7. Spec / design: A Có (paste hoặc file path) | B Không có
  - 7a. Build SRS wiki từ spec trên? *(chỉ trả lời nếu câu 7 = A)* — A Có (AI đọc spec, tạo SRS wiki cấu trúc hoá, save file, dùng wiki cho review) | B Không (dùng spec trực tiếp). *(Chọn A nếu spec lớn hoặc sẽ review nhiều TC file — tiết kiệm quota từ lần review thứ 2)*
  - 8. Output format: A Markdown | B Excel (.xlsx) | C Cả hai
  - 9. Fix mode: A Review only | B Review + auto-fix Minor/Note (clarity, consistency, assumption visibility) | C Review + auto-fix tất cả có thể (bao gồm Major clarity)
  - 10. Save path: [để trống = default: 04_generated_outputs/]
  - 11. Language (gap report): A Tiếng Việt | B Tiếng Anh | C Tiếng Nhật
- Field 7a chỉ trả lời khi câu 7 = A; bỏ qua nếu câu 7 = B.
- Excel input (.xlsx/.xls) → AI convert sang markdown trước khi xử lý.
- Build type và Function type được auto-detect — không cần BrSE khai báo.

Workspace Actions:
- Log intake form values → workspace findings / brief

### Step: STEP-02 — Coverage mode selection + pre-processing + micro-checkpoint

Objective:
Chọn coverage mode cao nhất có thể từ input; thực hiện pre-processing (Excel convert, SRS wiki build nếu cần, auto-detect function/build type); output micro-checkpoint rồi proceed ngay (không chờ BrSE reply).

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- Intake form (STEP-01)
- I-01 Testcase content, I-02 Viewpoint, I-03 Spec/design, I-04 Change log

Expected Outputs:
- Coverage mode đã chọn (A / B / B-wiki / C / D)
- SRS Wiki file đã save (nếu field 7a = A): `SRS_WIKI_<build>_<YYYY-MM-DD>.md`
- Function type + build type đã auto-detect
- Micro-checkpoint line đã output

Done Condition:
Coverage baseline xác định, pre-processing xong, micro-checkpoint đã output. AI proceed ngay sang STEP-03.

Notes / Constraints:
- **Coverage Mode Selection — chọn mode cao nhất có thể:**
  - Mode A — Viewpoint: Finalized viewpoint (field 6 = A) → ✅ Full → "Coverage assessed via viewpoint"
  - Mode B — Derive from spec: Spec (field 7 = A, 7a = B) → 🟡 Good → AI generates Proposed Viewpoint file; "see proposed viewpoint file"
  - Mode B-wiki: Spec + field 7a = A → ✅ Full → AI builds SRS wiki first → uses as Mode A baseline; saves wiki file
  - Mode C — Heuristics: Chỉ có testcase (không có viewpoint/spec) → 🟠 Partial → AI auto-detects function type; generates heuristic viewpoint
  - Mode D — No baseline: Không có gì → 🔴 Logic/clarity only → "Coverage not assessed"
- **Function type auto-detection (Mode C):** AI đọc testcase content và infer:
  - UI screen: button / field / screen / validation / error message / navigation
  - API: request / response / endpoint / status code / auth / header / payload
  - Batch / report: schedule / trigger / data volume / output file / filter / date range
  - Business flow: status transition / approval / rollback / end-to-end / workflow
- **Build type auto-inference:** AI đọc change log và infer:
  - Bug-fix: "fix / bug / defect / patch / hotfix"
  - Feature: "new / add / feature / implement / release"
  - CR: "CR / change request / client request / modification"
  - Mixed: nhiều loại rõ ràng cùng tồn tại
- **SRS Wiki Build (field 7 = A AND 7a = A)** — thực hiện trước micro-checkpoint, silent:
  1. Đọc spec content
  2. Identify distinct areas (screens / features / APIs / flows)
  3. Per area, extract: business rules, testable conditions (normal/boundary/exception), data constraints, permissions
  4. Viết wiki theo format: `# SRS Wiki — [System/Feature]`, Source/Build/Built header, Quality note (AI-generated — BrSE validate trước khi reuse), rồi mỗi Area có `### Business Rules` (BR-NN), `### Testable Conditions` ([Normal]/[Boundary]/[Exception] condition → expected), `### Data Constraints`, `### Permissions / Roles`
  5. Save `SRS_WIKI_<build>_<YYYY-MM-DD>.md` tại save path → use as Mode A baseline. BrSE có thể reuse wiki ở lần review sau bằng cách paste wiki path vào field 6.
- **Pre-processing (silent):** Excel input → convert sang markdown trước; SRS Wiki Build nếu field 7a = A; auto-detect function type + build type.
- **Quick Mode trigger:** testcase ≤ 10 TC entries AND không có change log AND không có spec/viewpoint → Quick Mode: D1/D2/D5 skip, compact output.
- **Micro-checkpoint (output trước khi chạy dimensions):** `▶ Proceeding: Build [name] | Type: [inferred] | Testcase: N entries | Mode: [Full/Quick] | Coverage baseline: [A/B-wiki/B/C/D] | SRS Wiki: [saved at <path> / not built] | Downstream: [who] | Fix mode: [A/B/C]` + "If incorrect → reply to correct before gap report is generated." AI proceed ngay — không chờ BrSE reply.

Workspace Actions:
- Write coverage mode + detected types → `04_findings.md`
- Save SRS wiki / proposed viewpoint file (nếu áp dụng)
- Output micro-checkpoint

### Step: STEP-03 — Run review dimensions D1–D5

Objective:
Thực hiện 5 review dimensions tuần tự, output findings có structure. Skip dimension có điều kiện ghi rõ.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Coverage baseline + detected types (STEP-02)
- I-01 Testcase, I-02/I-03 baseline, I-04 Change log, I-06 Known build issues

Expected Outputs:
- D1 Build Coverage findings (table: Change / Build Type / Testcase Exists / Coverage Level / Gap / Severity) + coverage summary
- D2 Regression Risk findings (table: Area / Impacted by / Risk Level / Existing TC / Recommendation)
- D3 Testcase Quality findings (coverage / logic vs spec / clarity / assumption visibility / consistency)
- D4 Execution Priority (🔴 Must-run / 🟡 Should-run / 🟢 Can-defer)
- D5 Known Blockers (TC bị ảnh hưởng → "Expected to fail — [issue]")

Done Condition:
Mọi dimension áp dụng đã chạy; dimension skip có ghi lý do (vd "Not assessed: build change log unavailable"). Findings structured theo I.1–I.5 categories (Coverage Gap, Logic/Spec, Clarity/Executability, Notes, Positive Confirmations).

Notes / Constraints:
- **D1 — Build Coverage** *(skip nếu không có change log hoặc Quick Mode)*: Với mỗi change trong build: ✅ Full coverage → không gap; ⚠️ Partial → Major nếu critical path, Minor nếu không; ❌ Not covered → Critical nếu business-critical, Major nếu không.
- **D2 — Regression Risk** *(skip nếu không có change log hoặc Quick Mode)*: Với mỗi change, identify impacted areas ngoài direct scope: 🔴 High = change ảnh hưởng shared module / core logic / data layer; 🟡 Medium = adjacent UI / secondary flow bị ảnh hưởng; 🟢 Low = change isolated, không có shared dependency.
- **D3 — Testcase Quality** *(always)*: Check tất cả sub-dimensions áp dụng: Coverage *(skip nếu Mode D)* = testcase có cover đủ viewpoint areas không; Logic vs spec = expected result có match confirmed spec không; Clarity/executability = steps + precondition + expected result có đủ rõ cho downstream; Assumption visibility = assumption/pending mark có explicit không; Consistency = cùng nhóm có nhất quán về format, ID, expected result pattern không.
- **Downstream-aware severity cho clarity issues:** Offshore (A) → Major (nếu step/expected result cần interpretation) / Minor (minor ambiguity, executable); QA internal / BrSE / UAT (B/C/D) → Minor / Note.
- **Heuristics table (Mode C):** UI screen → Normal flow, field validation, boundary, mandatory/optional, permission/role, error messages, navigation. API → Happy path, error codes (4xx/5xx), missing/invalid params, auth, response format, idempotency. Batch / report → Normal data, empty data, large volume, filter, date range, output format, trigger/schedule. Business flow → End-to-end happy path, branch conditions, rollback/cancel, status transitions, external dependency, re-entry.
- **D4 — Execution Priority** *(always)*: 🔴 Must-run = covers critical build change OR critical business path OR 🔴 regression area; 🟡 Should-run = regression of impacted area / quality gate / high-risk module; 🟢 Can-defer = low-risk / không bị ảnh hưởng bởi build này / stable regression suite.
- **D5 — Known Blockers** *(skip nếu không có known issues list hoặc Quick Mode)*: Với mỗi known issue → identify testcases bị ảnh hưởng → mark "Expected to fail — [issue]".
- **Test Viewpoint Alignment Check:** Mọi viewpoint area (từ approved viewpoint) phải có status: covered / partial / no + Gap/Note.

Workspace Actions:
- Write dimension findings → `04_findings.md` / draft
- Log coverage gaps + viewpoint alignment

### Step: STEP-04 — Self-review gate, severity classification, go/no-go

Objective:
Trước khi viết gap report, verify findings qua self-review gate (internal — không output), classify severity, quyết định go/no-go.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Dimension findings (STEP-03)

Expected Outputs:
- Findings đã pass self-review gate (6 checks)
- Severity gán cho mỗi finding (Critical / Major / Minor / Note)
- Go/No-go recommendation (⛔ / ⚠️ / ✅)

Done Condition:
Tất cả 6 self-review checks PASS (hoặc findings đã revise); severity calibrated; go/no-go quyết định.

Notes / Constraints:
- **Self-Review Gate (internal — không output ra ngoài) — verify cả 6 điểm:**
  1. Severity consistent? Critical chỉ khi zero coverage trên critical path hoặc expected result sai trên critical flow. Major chỉ khi execution area unreliable without fix.
  2. No over-classification? Minor/Note cho issues fixable mà không block execution.
  3. Each finding actionable? Mọi gap có "Suggested Action" cụ thể — không phải "add testcase" chung chung.
  4. Viewpoint coverage complete? Mọi viewpoint area có explicit status: covered / partial / not covered.
  5. Clarity severities calibrated to downstream? Offshore = stricter; QA internal/BrSE = lenient.
  6. Execution-ready after fixes? Nếu tất cả Critical/Major resolved → testcase có execution-ready không? Nếu không → có gì đó vẫn missing, revise.
  - Nếu bất kỳ check nào fail → revise findings trước khi output.
- **Severity Classification:** Critical = Build change không có testcase, hoặc testcase sẽ cho kết quả sai trên critical path → must resolve trước khi bất kỳ execution nào bắt đầu. Major = Gap đáng kể; execution của area bị ảnh hưởng unreliable without fix → must resolve trước khi execute area đó. Minor = Testcase executable nhưng kết quả có thể inaccurate/incomplete → fix trước final execution report. Note = Improvement point; execution không bị block → optional.
- **Go/No-go Decision Logic:** ⛔ Not ready = bất kỳ Critical gap nào tồn tại; ⚠️ Ready with conditions = Major gaps tồn tại nhưng scoped vào non-critical areas, conditions nêu rõ; ✅ Ready = chỉ có Minor/Note gaps, tất cả critical path testcases confirmed executable.

Workspace Actions:
- Record self-review gate result → `04_findings.md`
- Finalize severity + go/no-go in draft

### Step: STEP-05 — Apply fix mode (optional, field 9 = B/C)

Objective:
Nếu BrSE chọn fix mode B/C, áp dụng auto-fix cho các gap được phép, sau confirm gate, và save vào file riêng (không overwrite gốc).

Recommended Mode:
Executing

Applicable Guidelines:
_(none)_

Inputs:
- Findings + severity (STEP-04)
- Fix mode (field 9)
- I-01 Testcase content

Expected Outputs:
- Fix preview + BrSE confirmation (Y/N)
- Fixed testcase file: `<testcase>_fixed_<YYYY-MM-DD>.md` (nếu BrSE approve)
- Fix Log (đưa vào gap report section 7)

Done Condition:
Fix mode A (review only) → skip step, không sửa gì. Fix mode B/C → confirm gate shown, BrSE reply Y, fixes applied vào file `_fixed_` riêng; hoặc BrSE reply N → không fix.

Notes / Constraints:
- **Fix Mode (field 9) — gap nào fix được:**
  - Clarity — ambiguous step/expected result (Minor/Note) → Mode B ✅ Fix, Mode C ✅ Fix
  - Clarity — requires interpretation (Major) → Mode B ❌ Skip, Mode C ✅ Fix
  - Consistency — format, ID, naming (Minor/Note) → Mode B ✅ Fix, Mode C ✅ Fix
  - Assumption visibility — missing mark (Minor) → Mode B ✅ Fix, Mode C ✅ Fix
  - Coverage gap — missing testcase (Any) → ❌ Never (cả B và C)
  - Logic — wrong expected result (Any) → ❌ Never (cả B và C)
- Fix mode B/C: sau khi output gap report, AI show confirm gate trước khi sửa: `🔧 Fix preview (Mode [B/C]): Sẽ fix [N] gaps: [Gap ID list]; Không fix (cần human review): [Gap ID list]; Proceed with fixes? [Y / N]`.
- Chờ BrSE reply Y. Fixes được save vào `<testcase>_fixed_<YYYY-MM-DD>.md` — **không bao giờ overwrite file gốc**.

Workspace Actions:
- Show fix preview + capture BrSE Y/N
- Save fixed testcase → task workspace (`_fixed_` file)
- Record fix log

### Step: STEP-06 — Generate gap report + handoff plan

Objective:
Viết gap report theo format chuẩn (skip-if-empty), save theo save path, và lập re-review / handoff plan.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Findings + severity + go/no-go (STEP-04)
- Fix log (STEP-05, nếu có)
- Coverage baseline + detected types (STEP-02)

Expected Outputs:
- Gap report: `04_generated_outputs/REVIEW_TC_GAP_REPORT_<build>_<YYYY-MM-DD>.md`
- Re-review / handoff plan (Coordination steps 1–7)
- Issue list handed over to correct owner

Done Condition:
Gap report saved đúng save path với header + executive summary + sections (omit if empty); handoff plan tồn tại; tracker update flagged (AIP status = Closed sau closure).

Notes / Constraints:
- **Skip-if-empty rule:** Section/sub-section không có finding → omit hoàn toàn, không print empty header.
- **Header block:** `# Gap Report — Test Case Review`, Build/Build type/Review date, Testcase target, Coverage baseline + Proposed viewpoint/SRS wiki path, Downstream + Severity threshold + Mode; `> AI Understanding:` (1–2 câu scope và focus — BrSE reply nếu sai để AI re-review).
- **Executive Summary table:** Build type | Overall risk level (🔴/🟡/🟢) | Go/No-go recommendation (⛔/⚠️/✅) | Total gaps N (Critical: X, Major: Y, Minor: Z, Note: W) | Execution-blocked testcases N | Must-run testcase groups N.
- **Sections (omit if empty):** 1 Build Coverage Gaps (ID/Change/Coverage/Gap/Severity/Action/Owner); 2 Regression Risk Areas (Area/Impacted by/Risk Level/Existing TC/Recommendation); 3 Testcase Quality Gaps (ID/Type/Issue/TC Ref/Severity/Suggested Action/Owner); 4 Execution Priority (🔴/🟡/🟢); 5 Execution Blockers (TC/Known Issue/Action); 6 Action Items (ID/Action/Severity/Owner/By When); 7 Fix Log *(Fix mode B/C only)*.
- **Quick Mode format (compact):** Header + Summary + Quality Gaps table + Priority line + Action Items only.
- **Save path:** `04_generated_outputs/REVIEW_TC_GAP_REPORT_<build>_<YYYY-MM-DD>.md` trong task workspace.
- **Re-review / handoff plan (Coordination):** 1 Confirm input understandings → 2 Draft review findings → 3 Create review viewpoint + self review → 4 Send consolidated result to testcase author → 5 Testcase author updates document → 6 Re-review Major issues → 7 Update AIP status (Closed) and tracker.

Workspace Actions:
- Write gap report → `04_generated_outputs/`
- Write handoff plan → draft
- Move final → output location; flag tracker update

## Done Criteria

Task is done when:
- [ ] input understandings are confirmed (Gate U2)
- [ ] viewpoint alignment has been checked
- [ ] review findings are structured clearly
- [ ] review viewpoint exists and self-review (STEP-04) has been performed
- [ ] issue list is handed over to the correct owner
- [ ] gap report saved đúng save path và naming convention
- [ ] tracker has been updated (AIP status = Closed)
- [ ] downstream team knows whether testcase is execution-ready or needs update
- [ ] **Gate U1** confirmed — evidence trong workspace
- [ ] **Gate U3** mọi open point trong `05_open_questions.md` đã resolved / deferred / rejected (hoặc không phát sinh)

## Self-check / Review Points

Trước handoff (Self Review — pass condition: tất cả checks PASS):
- Review scope có đúng không — Scope khớp với Execution Scope; không review ngoài scope khai báo
- Tất cả viewpoint area đã được check chưa — Mọi area trong Viewpoint Alignment đều có status (covered / partial / no)
- Coverage gap có đầy đủ và actionable không — Mỗi gap có Suggested Action cụ thể (không phải "add testcase" chung chung)
- Logic issue có đúng spec không — Issue logic có reference confirmed spec / clarification result
- Severity / impact có hợp lý không — Major chỉ khi execution bị ảnh hưởng; Critical chỉ khi không thể execute
- Downstream có execute được sau khi update không — Nếu Critical/Major resolved → testcase execution-ready

## Finalization Notes

**Sample execution note:**
- Khi BrSE giao AIP này và yêu cầu execute: AI đọc context cụ thể trước, present intake form (STEP-01) nếu thiếu input, không hỏi từng câu trước.
- AI proceed ngay sau micro-checkpoint (STEP-02) — không chờ BrSE reply trừ confirm gate của fix mode.
- Gap report naming: `REVIEW_TC_GAP_REPORT_<build>_<YYYY-MM-DD>.md` tại `04_generated_outputs/`.
- Fixes (mode B/C) luôn save vào file `<testcase>_fixed_<YYYY-MM-DD>.md` — không bao giờ overwrite file gốc.

## Re-plan Rule

Append Re-plan Log entry khi:
- Review scope thay đổi sau STEP-00 (scope change)
- Coverage baseline thay đổi đáng kể (vd viewpoint finalize muộn, build change log bổ sung)
- BrSE yêu cầu đổi fix mode hoặc output format ảnh hưởng macro scope

## Re-plan Log
<!-- Append entry on scope/objective/output change. Format: ### YYYY-MM-DD — title / Trigger / Change / Evidence ref / Approved by. -->

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- Task review testcase đã có scope rõ ràng
- BrSE muốn AI execute review và output gap report
- Review gắn với build cụ thể hoặc viewpoint đã finalize

**Khi KHÔNG dùng file này:**
- Scope còn thay đổi lớn
- Chỉ cần quick personal checklist (dùng Member AIP)
- Focus là PM-level tracking (dùng PM AIP)

**AI execution principles:**
- Đọc context cụ thể trước khi execute; follow execution flow STEP-00 → STEP-06.
- Không tự suy luận ngoài flow. Nếu BrSE đã điền intake form trong AIP, dùng giá trị đó thay vì hỏi lại.
- Nếu thiếu input → dùng intake form (STEP-01) để hỏi BrSE.

---

## Changelog

- Migrated from legacy preset `AIP_EXEC_ReviewTestCase.md` (v1.0, 2026-04-21; Mapped Sample: `AIP_Sample_ReviewTestCase_Shared.md`). Re-authored into current AIP_EXEC structure (frontmatter + `## Execution Steps` STEP-NN) on 2026-06-20. All documented intent preserved: legacy sections A–O (BrSE scaffold) + AI Execution Protocol P1–P10 relocated into top-level sections and 7 sequential steps (STEP-00 HARD GATE → STEP-06 gap report); no scope redesign.
- Fidelity repair 2026-06-20: reinstated dropped legacy content — (1) legacy `C. Context Summary` as a recorded `## Context Summary` section (background ngắn của bộ testcase, vì sao cần review lúc này, downstream impact, review round hiện tại là round mấy nếu có) + recorded at STEP-00; (2) legacy `A. Metadata` discrete recordable slots (Review Target, Test Viewpoint Reference, Reviewers, Testcase Author, Related Documents, Related AIPs, Input Understanding Status, Review Viewpoint Status) as a `Review Metadata` table filled at STEP-00.
