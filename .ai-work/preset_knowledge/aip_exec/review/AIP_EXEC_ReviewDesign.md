---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-review-design
title: Review Design Document (BD / DD / Screen Design)
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when review scope and input understandings are already confirmed>"
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Review Design Document

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Review tài liệu thiết kế hiện có theo 6 dimensions, tạo bộ output gồm:
1. **Review Comment** — severity-classified findings với suggested actions và owners
2. **Checklist** — pass/fail assessment per review criteria item

để downstream team (DD/dev/QA/offshore) có thể tiếp tục an toàn hoặc biết rõ điều kiện cần fix trước khi proceed.

> Loại tài liệu (BD / DD / Screen Design) và review mode (A / B / C) được xác nhận tại STEP-00. Một AIP instance = một review task.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: design_review
- Reason: Reviewing a design doc (BD/DD/Screen) against the requirement/spec baseline across 6 dimensions — read in design-correctness terms.
- Search/execution effect: Prioritises `basic_design`, `detailed_design_*`, `screen_mockup`, `db_schema`, `api_manual`, `requirement_definition` + object kinds (`function`/`screen`/`table`/`api`) when ordering the reading surface.
- Expansion allowed: yes — pull the requirement/spec baseline (Mode A/B) or prior design to ground a finding; verify raw source when exactness matters.

## Execution Scope

### In Scope
- Review tài liệu thiết kế (BD / DD / Screen Design) theo 6 dimensions: D1 Requirement Consistency, D2 Business Logic, D3 Scope & Boundary, D4 Implementability, D5 Downstream Usability, D6 Completeness & Consistency
- Tạo Review Comment với severity-classified findings, suggested actions, owners
- Tạo Checklist (pass/fail) với finding references
- Self-review theo review viewpoint trước handoff
- BrSE verify checkpoint sau understandings confirmed (STEP-02) và sau self-review (STEP-11)

### Out of Scope
- **Không dùng file này khi:**
  - chưa rõ scope review hoặc review objective
  - BrSE chưa confirm input understandings
  - tài liệu thiết kế đang thay đổi lớn (unstable)
  - chưa rõ downstream team sẽ dùng kết quả review
  - cần phân tích requirement sâu trước (dùng PLAN AIP hoặc Requirement Analysis AIP)
- Không tạo mới design document — dùng `AIP_EXEC_CreateDesignDoc.md`
- Không tự sửa tài liệu thiết kế đang review — chỉ output findings + recommendations

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Review Comment document (markdown / excel) | Severity-classified findings (D1–D6) với suggested actions và owners; Executive Summary + proceed recommendation | AI → design owner / stakeholders |
| O-02 | Checklist document (markdown / excel) | Pass/fail assessment per review criteria item; mỗi Fail link finding ID | AI → design owner |
| O-03 | Action items list | Embedded trong Review Comment | AI → design owner action |
| O-04 | AIP Progress file | Cập nhật status từng step | AI |
| O-05 | Tracker / review log | Ghi nhận đã review, findings count, proceed recommendation | AI → BrSE |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu PLAN AIP (hoặc tương đương) đã làm rõ scope review và input understandings đã được BrSE confirm.
Hoặc `direct` — khi review scope và input understandings đã confirmed trước, không cần PLAN phase.

Outputs inherited from PLAN (nếu có): confirmed input understandings (design objective, scope, requirement alignment, risk areas, downstream usage); review scope (in/out); review dimensions và priority; downstream context; project-specific checklist nếu có.

### Required Inputs

| Input | Loại | Source |
|---|---|---|
| I-01 Tài liệu thiết kế (BD / DD / Screen Design) | Required | Design owner / Internal |
| I-02 Requirement / spec | Required (Mode A/B) | Internal / Customer |
| I-03 Clarification results | Optional | Internal / Customer |
| I-04 Prior design (BD cho DD review) | Optional | Internal |
| I-05 Open issue / assumption list | Optional | Internal |
| I-06 Prior review comments | Optional | Internal |
| I-07 Review checklist (project-specific) | Optional | BrSE / Internal |

### Workspace Preconditions
- [ ] Tài liệu thiết kế available và stable
- [ ] Review scope đã chốt (toàn bộ / changed sections / specific sections)
- [ ] Requirement / spec baseline available (hoặc xác nhận Mode C — document-only)
- [ ] Input understandings confirmed hoặc sẵn sàng confirm ở STEP-02
- [ ] Downstream context đã rõ (ai dùng kết quả review)
- [ ] BrSE approve review có thể bắt đầu

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC khi review sâu (STEP-03). BrSE phải confirm tại STEP-02. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Design doc | `<design objective, scope/boundary>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Requirement / spec | `<requirement alignment, coverage>` | `<assumptions>` | `<gaps>` | ⬜ pending |
| Downstream context | `<ai dùng kết quả review, risk areas>` | — | — | ⬜ pending |

---

## References to Read First

**Required:**
- `<path to tài liệu thiết kế (I-01)>`
- `<path to requirement / spec (I-02)>` — Mode A/B

**Optional:**
- `<path to clarification results (I-03)>`
- `<path to prior design / BD (I-04)>`
- `<path to open issue / assumption list (I-05)>`
- `<path to prior review comments (I-06)>`
- `<path to project-specific review checklist (I-07)>`
- **Runtime Review Checklist (optional, recommended for STEP-10):** materialize a per-run `06_runtime_review_checklist.md` via the `aiws-runtime-review-checklist` skill — concrete, deterministic per-item checks (Assert / Method-with-loci / objective PASS·FAIL·N/A) selected from the project review checklist; the STEP-03→STEP-08 dimension findings then fill its verdicts. Method templates: `procedural/skills/aiws-runtime-review-checklist/runtime_review_breakdown_strategies.md` (co-located with the skill).

---

## Current Risks / Constraints

- **Large design document:** Nếu tài liệu thiết kế quá lớn (>50 trang / >20 sections) → chia review thành multiple rounds theo section group; mỗi round output Review Comment + Checklist riêng; tổng hợp cuối cùng.
- **No requirement baseline:** Nếu requirement / spec không available → switch sang Mode C (document-only review); ghi rõ trong header "Requirement consistency not assessed — Mode C."
- **Unclear design type:** Nếu design type không rõ → AI auto-detect từ nội dung; nếu ambiguous thì hỏi BrSE.
- **No prior design for DD review:** Nếu prior design (BD) không available khi review DD → skip cross-level consistency check; ghi rõ trong findings "BD alignment not assessed — BD not provided."
- **Requirement vs clarification conflict:** Nếu có mâu thuẫn giữa requirement và clarification → ghi rõ trong findings, hỏi BrSE chốt trước khi classify severity.
- **Too many findings:** Nếu findings quá nhiều (>20 items) → nhóm theo dimension, highlight top 5 Critical/Major; phần còn lại trong appendix.
- **Duplicate checklist items:** Nếu project-specific checklist có items trùng standard checklist → merge, không duplicate; note source trong Checklist.
- **Time-constrained review:** Nếu BrSE muốn review nhanh (time-constrained) → focus D1 + D2 + D3 (3 dimensions quan trọng nhất); skip D4/D5/D6; ghi rõ "Partial review — 3/6 dimensions assessed."

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ open point review nào (mâu thuẫn requirement, severity ambiguity, missing baseline) vào file trên. Open point blocking → confirm với BrSE trước khi tiếp.

---

## Workspace Execution Rule

All runtime state (findings tables D1–D6, draft Review Comment, Checklist, open points) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
<!-- Gate U1 — Universal. Bắt buộc cho MỌI task substantive. Skip chỉ khi BrSE explicit ủy quyền (ghi ủy quyền vào workspace findings). -->

Objective:
Xác nhận review scope, design type (BD/DD/Screen), review mode (A/B/C), downstream context, language; thu thập input. Viết ra ý hiểu về task (scope, expected output/deliverable, Done definition, assumptions) và dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1
- wiki:none — HARD GATE preflight default. Replace with the relevant `product/wiki_guidelines/...` path after running `lookup_wiki_source.py`; keep `wiki:none` only when pre-flight confirms no wiki coverage.

Inputs:
- I-01 Tài liệu thiết kế (overview)
- I-02 Requirement / spec (overview, nếu Mode A/B)
- AIP PLAN handoff / BrSE request

Expected Outputs:
- Bảng xác nhận: design type, scope, baseline mode, downstream, language
- Task understanding note trong workspace
- BrSE confirmation evidence

Done Condition:
BrSE explicit confirm ý hiểu task — design type (BD/DD/Screen) và review mode (A/B/C) đã xác nhận (hoặc explicit ủy quyền skip gate).

Notes / Constraints:
- Không làm gì khác ngoài clarify/confirm ở step này.
- Nếu design type không rõ → AI auto-detect từ nội dung; nếu ambiguous thì hỏi BrSE.
- Nếu requirement / spec không available → switch sang Mode C (document-only); ghi rõ trong header.
- Nếu BrSE chỉnh hiểu biết → update note rồi re-confirm trước khi sang STEP-01.

Workspace Actions:
- Write confirmed design type, scope, baseline mode, downstream → `00_task_brief.md`
- Log BrSE confirmation

---

### Step: STEP-01 — Tổng hợp Input Understanding

Objective:
Tổng hợp Input Understanding từ toàn bộ input thu thập tại STEP-00: design objective, scope/boundary, requirement alignment, risk areas, downstream usage.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- Toàn bộ input từ STEP-00 (I-01 design doc, I-02 requirement, I-03 clarification nếu có)

Expected Outputs:
- Understanding note: design objective, scope/boundary, requirement alignment, risk areas, downstream usage
- Input Understanding table điền

Done Condition:
Understanding đã ghi đầy đủ; sẵn sàng cho BrSE confirm tại STEP-02. Điểm chưa rõ → log `05_open_questions.md`.

Notes / Constraints:
- BrSE phải confirm understanding trước khi review sâu (gate tại STEP-02).
- Assumption không được coi là confirmed fact.

Workspace Actions:
- Write Input Understanding → `04_findings.md`
- Log open points → `05_open_questions.md`

---

### Step: STEP-02 — BrSE confirm Input Understanding (verify checkpoint)

Objective:
BrSE xác nhận Input Understanding đúng trước khi bắt đầu review sâu D1–D6.

Recommended Mode:
Clarifying

Applicable Guidelines:
_(none)_

Inputs:
- Input Understanding note (STEP-01)

Expected Outputs:
- BrSE confirmation evidence (Input Understanding table cập nhật ✅)

Done Condition:
BrSE confirm understandings. Nếu reject → quay lại STEP-01 chỉnh understanding rồi re-confirm.

Notes / Constraints:
- **BrSE verify:** đây là verify checkpoint đầu tiên (understandings confirmed) — không proceed review nếu chưa confirm.

Workspace Actions:
- Update Input Understanding table (BrSE confirmed) → `04_findings.md`

---

### Step: STEP-03 — Review D1 — Requirement Consistency

Objective:
Review dimension D1 — kiểm tra tài liệu thiết kế nhất quán với requirement / spec baseline.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- Understanding (STEP-01/02)
- I-02 Requirement / spec

Expected Outputs:
- Findings table D1

Done Condition:
D1 findings đã ghi với severity classification, hoặc D1 skipped (Mode C).

Notes / Constraints:
- **Skip nếu Mode C** (không có requirement baseline) — ghi rõ "Requirement consistency not assessed — Mode C."
- Nếu có mâu thuẫn giữa requirement và clarification → ghi rõ trong findings, hỏi BrSE chốt trước khi classify severity.

Workspace Actions:
- Write D1 findings → `04_findings.md`

---

### Step: STEP-04 — Review D2 — Business Logic

Objective:
Review dimension D2 — kiểm tra business logic trong design đúng và đầy đủ.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- Understanding (STEP-01/02)
- I-01 Design document

Expected Outputs:
- Findings table D2

Done Condition:
D2 findings đã ghi với severity classification.

Notes / Constraints:
- Luôn thực hiện.
- Critical chỉ dùng cho wrong logic on critical path.

Workspace Actions:
- Write D2 findings → `04_findings.md`

---

### Step: STEP-05 — Review D3 — Scope & Boundary

Objective:
Review dimension D3 — kiểm tra scope và boundary của design rõ ràng, không gap/overlap.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- Understanding (STEP-01/02)
- I-01 Design document

Expected Outputs:
- Findings table D3

Done Condition:
D3 findings đã ghi với severity classification.

Notes / Constraints:
- Luôn thực hiện.

Workspace Actions:
- Write D3 findings → `04_findings.md`

---

### Step: STEP-06 — Review D4 — Implementability

Objective:
Review dimension D4 — kiểm tra design có thể implement được (đủ chi tiết, không mâu thuẫn kỹ thuật).

Recommended Mode:
Reviewing

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- Understanding (STEP-01/02)
- I-01 Design document

Expected Outputs:
- Findings table D4

Done Condition:
D4 findings đã ghi với severity classification.

Notes / Constraints:
- Luôn thực hiện.
- Skip D4 nếu BrSE chọn partial review (time-constrained, 3/6 dimensions).

Workspace Actions:
- Write D4 findings → `04_findings.md`

---

### Step: STEP-07 — Review D5 — Downstream Usability

Objective:
Review dimension D5 — kiểm tra design usable cho downstream team (DD/dev/QA/offshore).

Recommended Mode:
Reviewing

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- Understanding (STEP-01/02)
- Downstream context

Expected Outputs:
- Findings table D5

Done Condition:
D5 findings đã ghi với severity classification, calibrated theo downstream.

Notes / Constraints:
- Calibrate severity theo downstream (offshore/customer = stricter).
- Skip D5 nếu BrSE chọn partial review (time-constrained, 3/6 dimensions).

Workspace Actions:
- Write D5 findings → `04_findings.md`

---

### Step: STEP-08 — Review D6 — Completeness & Consistency

Objective:
Review dimension D6 — kiểm tra design đầy đủ và nội bộ nhất quán.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- I-01 Design document

Expected Outputs:
- Findings table D6

Done Condition:
D6 findings đã ghi với severity classification.

Notes / Constraints:
- Luôn thực hiện.
- Nếu prior design (BD) không available khi review DD → skip cross-level consistency check; ghi rõ "BD alignment not assessed — BD not provided."
- Skip D6 nếu BrSE chọn partial review (time-constrained, 3/6 dimensions).

Workspace Actions:
- Write D6 findings → `04_findings.md`

---

### Step: STEP-09 — Tổng hợp Review Comment

Objective:
Tổng hợp findings từ D1–D6 thành Review Comment document với severity classification, suggested actions, owners, Executive Summary và proceed recommendation.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Findings D1–D6 (STEP-03 → STEP-08)

Expected Outputs:
- Review Comment document

Done Condition:
Review Comment có Executive Summary với proceed recommendation; mọi finding có severity và suggested action cụ thể. Self-review gate trước khi output.

Notes / Constraints:
- Critical chỉ dùng cho business-critical requirement miss hoặc wrong logic on critical path; Major chỉ dùng cho significant gap blocking downstream.
- Suggested action phải cụ thể (không phải generic "fix this").
- Sections không có findings đã omit; include Positive Confirmations (không chỉ toàn findings negative).
- Nếu findings quá nhiều (>20 items) → nhóm theo dimension, highlight top 5 Critical/Major; phần còn lại trong appendix.
- Mode C: header ghi "Requirement consistency not assessed — Mode C." Partial review: header ghi "Partial review — 3/6 dimensions assessed."

Workspace Actions:
- Write Review Comment draft → `07_output_draft.md`

---

### Step: STEP-10 — Tạo Checklist

Objective:
Tạo Checklist document (pass/fail) per review criteria item, mỗi Fail link finding ID.

Recommended Mode:
Generating

Applicable Guidelines:
_(I-07 project-specific review checklist nếu có)_

Inputs:
- Findings D1–D6
- Review criteria (standard + I-07 project-specific)

Expected Outputs:
- Checklist document (pass/fail)

Done Condition:
Checklist hoàn chỉnh; mỗi Fail link đúng finding ID.

Notes / Constraints:
- Nếu project-specific checklist có items trùng standard checklist → merge, không duplicate; note source trong Checklist.
- Partial review: Checklist chỉ include items liên quan dimensions đã review; các items khác = Skip.

Workspace Actions:
- Write Checklist → `07_output_draft.md`

---

### Step: STEP-11 — Self-review theo review viewpoint

Objective:
Self-review Review Comment + Checklist theo review viewpoint trước khi handoff; fix issues trước handoff.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Review Comment (STEP-09)
- Checklist (STEP-10)

Self-review checklist:
- [ ] Review Comment có Executive Summary với proceed recommendation?
- [ ] Mỗi Checklist Fail link đúng finding ID?
- [ ] Sections không có findings đã omit?
- [ ] Positive Confirmations có include (không chỉ toàn findings negative)?
- [ ] Mỗi finding có severity classification hợp lý?
- [ ] Downstream severity calibration đã áp dụng?

Expected Outputs:
- Reviewed outputs (Review Comment + Checklist), issues fixed

Done Condition:
Self-review pass; mọi issue đã fix trước handoff. Sau bước này BrSE verify (verify checkpoint thứ hai).

Notes / Constraints:
- **BrSE verify:** Sau STEP-02 (understandings confirmed) và STEP-11 (self-review done), BrSE xác nhận trước khi tiếp.
- Fix trước khi handoff — không handoff outputs chưa self-review.

Workspace Actions:
- Write self-review notes → `04_findings.md`

---

### Step: STEP-12 — Finalize / handoff

Objective:
Finalize Review Comment + Checklist và handoff cho design owner và relevant stakeholders; update tracker, lưu file.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Reviewed outputs (STEP-11)

Expected Outputs:
- Final Review Comment + Checklist
- Tracker / review log cập nhật (findings count, proceed recommendation)

Done Condition:
Outputs handoff cho design owner và stakeholders; proceed recommendation rõ (Proceed / Proceed with conditions / Stop); re-review plan cho Critical/Major issues đã xác định.

Notes / Constraints:
- Nếu có Critical → Hold handoff, fix Critical first → re-review → then proceed.
- Update tracker, lưu file đúng path và naming convention.

Workspace Actions:
- Apply final fixes → update draft
- Move final → `11_output_final/`
- Update tracker / review log

---

## Done Criteria

- [ ] Input understandings đã được BrSE confirm (STEP-02)
- [ ] Review Comment đã output với severity classification rõ ràng (STEP-09)
- [ ] Checklist đã output với pass/fail và finding references (STEP-10)
- [ ] Self-review đã thực hiện (STEP-11)
- [ ] Outputs đã handoff cho design owner và relevant stakeholders (STEP-12)
- [ ] Proceed recommendation đã rõ (Proceed / Proceed with conditions / Stop)
- [ ] Re-review plan cho Critical/Major issues đã xác định
- [ ] **Gate U1** confirmed — evidence trong workspace
- [ ] **Gate U2** Input Understanding đã ghi và BrSE confirmed
- [ ] **Gate U3** Mọi open point trong `05_open_questions.md` đã resolved / deferred / rejected (hoặc không phát sinh)

## Self-check / Review Points

**Trước khi review (STEP-00 → STEP-02):**
- [ ] Design type đã xác định (BD / DD / Screen)?
- [ ] Review scope đã chốt (toàn bộ / changed / specific)?
- [ ] Baseline mode đã xác định (A / B / C)?
- [ ] Downstream context đã rõ?
- [ ] Input understandings đã được BrSE confirm?

**Khi review (STEP-03 → STEP-08):**
- [ ] Mỗi finding có severity classification hợp lý?
- [ ] Critical chỉ dùng cho business-critical requirement miss hoặc wrong logic on critical path?
- [ ] Major chỉ dùng cho significant gap blocking downstream?
- [ ] Mỗi finding có suggested action cụ thể (không phải generic "fix this")?
- [ ] Downstream severity calibration đã áp dụng (offshore/customer = stricter)?
- [ ] Assumption không bị coi là confirmed fact?

**Khi tạo output (STEP-09 → STEP-11):**
- [ ] Review Comment có Executive Summary với proceed recommendation?
- [ ] Mỗi Checklist Fail link đúng finding ID?
- [ ] Sections không có findings đã omit?
- [ ] Positive Confirmations có include (không chỉ toàn findings negative)?
- [ ] Self-review viewpoint đã thực hiện trước khi output?

## Finalization Notes

**Ví dụ 1 — Normal case: Review BD cho Order Entry**
- STEP-00: Design type = BD, scope = full, Mode A (có requirement + clarification), downstream = DD team
- STEP-01/02: Understanding — Order Entry CRUD + duplicate handling + validation. BrSE confirm.
- STEP-03 → STEP-08: Review 6 dimensions → 6 findings (1 RC, 2 BL, 1 SB, 1 IM, 1 DU)
- STEP-09: Review Comment — 6 findings: 0 Critical, 3 Major, 2 Minor, 1 Note
- STEP-10: Checklist — 15 items: 10 Pass, 4 Fail, 1 Skip. Verdict: "Proceed with conditions"
- STEP-11: Self-review pass
- STEP-12: Handoff → design owner fix 3 Major items → re-review → proceed to DD

**Ví dụ 2 — Review DD cho Payment module (Mode B — no clarification)**
- STEP-00: Design type = DD, scope = full, Mode B (có requirement, không có clarification), downstream = offshore
- STEP-01/02: Understanding — Payment flow, DB schema, API spec. BrSE confirm.
- STEP-03: D1 — 2 findings (requirement coverage partial)
- STEP-04: D2 — 1 Critical finding (refund logic contradicts requirement)
- STEP-05 → STEP-08: D3–D6 — 3 Minor findings
- STEP-09: Review Comment — 6 findings: 1 Critical, 2 Major, 3 Minor → **Stop** (Critical exists)
- STEP-10: Checklist — 15 items: 9 Pass, 5 Fail, 1 Skip
- STEP-12: Hold handoff → fix Critical first → re-review → then proceed

**Ví dụ 3 — Review Screen Design (Mode C — document only)**
- STEP-00: Design type = Screen Design, scope = changed sections only (after CR), Mode C (no requirement provided)
- STEP-01/02: Understanding — 3 screens changed: Order List, Order Detail, Order Search. BrSE confirm.
- STEP-03: D1 skipped (Mode C)
- STEP-04 → STEP-08: Review D2–D6 → 4 findings (field validation missing, navigation unclear, role-based display not defined)
- STEP-09: Review Comment — Note in header: "Requirement consistency not assessed — Mode C"
- STEP-10: Checklist — SD-specific items: 2 Pass, 3 Fail, 0 Skip
- STEP-12: Handoff → design owner update 3 items → re-review

**Ví dụ 4 — Partial review (time-constrained)**
- BrSE yêu cầu review nhanh, chỉ có 2 giờ
- STEP-00: Focus D1 + D2 + D3 only; skip D4/D5/D6
- STEP-09: Review Comment header ghi "Partial review — 3/6 dimensions assessed"
- STEP-10: Checklist chỉ include items liên quan 3 dimensions đã review; các items khác = Skip
- STEP-12: Handoff kèm note "Full review recommended before final approval"

**Naming / handoff:**
- Lưu file đúng path và naming convention của dự án; version up thay vì overwrite khi có thay đổi sau re-review.

## Re-plan Rule

Append Re-plan Log entry khi:
- Review scope thay đổi sau STEP-00 (toàn bộ ↔ partial ↔ specific sections)
- Baseline mode thay đổi (A/B ↔ C)
- Tài liệu thiết kế thay đổi lớn (unstable) trong lúc review
- BrSE yêu cầu chia review thành multiple rounds (large document)

## Re-plan Log

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- PLAN AIP (hoặc tương đương) đã làm rõ scope review và input understandings đã được BrSE confirm
- tài liệu thiết kế đã available (BD / DD / Screen Design)
- requirement / spec baseline đã available (hoặc xác nhận review ở Mode C — document-only)
- task chuyển từ giai đoạn **"chuẩn bị review"** sang giai đoạn **"thực hiện review và output findings"**

**Khi KHÔNG dùng file này:** (xem `## Execution Scope → Out of Scope`)
- chưa rõ scope review hoặc review objective; BrSE chưa confirm input understandings; tài liệu thiết kế đang thay đổi lớn; chưa rõ downstream; cần phân tích requirement sâu trước
- Cần tạo mới design (không review) → dùng `AIP_EXEC_CreateDesignDoc.md`

**Review modes:**
- **Mode A** — requirement + clarification available (full baseline)
- **Mode B** — requirement available, no clarification
- **Mode C** — document-only (no requirement baseline); D1 skipped, header ghi "Requirement consistency not assessed — Mode C"

---

## Changelog

- **Migrated from:** `AIP_EXEC_ReviewDesign.md` legacy numbered-prose format v1.0 (2026-04-16). Re-authored into current AIP_EXEC structure 2026-06-20. Mapped PLAN Sample (legacy): `AIP_Sample_ReviewDesign_Shared.md`. All documented intent (6-dimension review, Mode A/B/C, branch handling, self-check, completion criteria, 4 sample execution notes, PLAN-to-EXEC trace) preserved; relocated into template sections, not dropped.
