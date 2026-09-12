---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-create-testcase
title: Create Test Case Document (Markdown)
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when test scope is already confirmed>"
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Create Test Case Document

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Tạo tài liệu test case có cấu trúc (Markdown format) từ design documents hoặc requirements, bao gồm:
- Phân tích test targets từ inputs
- Thiết kế test scenarios: normal, abnormal, boundary, error cases
- Viết test case chi tiết với đầy đủ fields
- Review coverage: mỗi requirement / acceptance criterion có ít nhất 1 TC

Output là tài liệu Markdown sẵn sàng cho QA execution hoặc offshore team.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: test_design
- Reason: Deriving test cases from design/requirements — read inputs for testable items, scenarios (normal/abnormal/boundary/error), and requirement→TC coverage.
- Search/execution effect: Prioritises `requirement_definition`, `basic_design`, `detailed_design_combined`, `test_case`, `unit_test_spec` + object kinds (`function`/`screen`) when assembling inputs and ordering the reading surface.
- Expansion allowed: yes — pull the specific design/requirement when an expected result is unclear; do not guess expected results (log Open Points).

## Execution Scope

### In Scope
- Phân tích inputs để xác định testable items
- Thiết kế test scenarios (positive, negative, boundary, error)
- Viết test case chi tiết theo Markdown format
- Coverage review: traceability từ requirements → test cases
- BrSE review checkpoint trước finalize

### Out of Scope
- Không execute test — chỉ tạo tài liệu
- Không tự quyết định expected result khi business rule chưa rõ — log Open Points
- Không tạo test automation scripts
- Không review test case của người khác — dùng `AIP_EXEC_ReviewTestCase.md`

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Test Case Document (MD) | Tài liệu test case hoàn chỉnh, Markdown format | AI → BrSE review |
| O-02 | Coverage Matrix | Mapping requirement / acceptance criterion → TC list | AI → BrSE review |
| O-03 | Open Points Log | Business rules hoặc expected results chưa rõ | AI → BrSE action |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu đến từ PLAN phase.
Hoặc `direct` — khi test scope đã confirmed, không cần PLAN phase riêng.

### Required Inputs

| Input | Description | Required / Optional |
|---|---|---|
| I-01 Design Document | BD / DD / Screen Design đã confirm | Required (preferred) |
| I-02 Requirements / Spec | Yêu cầu gốc nếu không có design doc | Required (nếu không có I-01) |
| I-03 Acceptance Criteria | Acceptance criteria đã confirm (nếu có) | Optional |
| I-04 Test Case Template | Template riêng của dự án nếu có | Optional |
| I-05 Existing Test Cases | Test cases hiện có nếu đây là update / extension | Optional |

### Workspace Preconditions
- [ ] Test scope đã xác nhận (module / feature / screen nào)
- [ ] Coverage level đã thống nhất: basic (normal only) / standard (+ abnormal) / comprehensive (+ boundary + error)
- [ ] I-01 hoặc I-02 có sẵn và đủ để suy ra expected results

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Design doc | `<tóm tắt scope, screens/modules, business rules key>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Requirements | `<tóm tắt requirements liên quan>` | — | — | ⬜ pending |
| I-03 Acceptance Criteria | `<danh sách criteria (nếu có)>` | — | `<ambiguities>` | ⬜ pending |

---

## References to Read First

**Required (ít nhất một trong hai):**
- `<path to design document (I-01)>`
- `<path to requirements / spec (I-02)>`

**Optional:**
- `<path to acceptance criteria (I-03)>`
- `<path to test case template (I-04)>`
- `<path to existing test cases (I-05)>`

---

## Current Risks / Constraints

- **Unclear business rules:** Expected result chưa rõ → log Open Points, không tự assume
- **Missing design:** Thiếu I-01 và I-02 → không thể tạo test case chính xác
- **Coverage ambiguity:** Nếu coverage level không confirm → hỏi BrSE tại STEP-00
- **Customization note:** Template này là generic baseline — dự án customize TC format và coverage standards theo nhu cầu

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ business rule hoặc expected result chưa rõ vào file trên. Blocking → confirm BrSE trước khi tiếp.

---

## Workspace Execution Rule

All runtime state (drafts, findings, open points) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)

Objective:
Xác nhận: module/feature cần test, inputs có sẵn, coverage level, TC format, review expectation.

Recommended Mode:
Clarifying

Applicable Guidelines:
SOP_MASTER Gate U1

Inputs:
- I-01 Design doc (overview) hoặc I-02 Requirements (overview)

Expected Outputs:
- Xác nhận: test scope, coverage level, inputs có đủ không
- Sơ bộ danh sách test areas (groups of scenarios)
- BrSE confirmation

Done Condition:
BrSE confirm AI hiểu đúng scope và coverage level. Inputs đủ để proceed.

Notes / Constraints:
- Nếu thiếu cả I-01 lẫn I-02 → STOP, yêu cầu BrSE cung cấp trước
- Xác nhận TC format — dùng I-04 template nếu có, không thì dùng generic format bên dưới

Generic TC format (nếu không có template riêng):
```markdown
## TC-[NNN]: [Test Scenario Title]
**Category:** Normal / Abnormal / Boundary / Error
**Priority:** High / Medium / Low
**Preconditions:** [Trạng thái hệ thống trước khi test]
**Test Steps:**
1. [Bước 1]
2. [Bước 2]
**Expected Result:** [Kết quả mong đợi — cụ thể, verifiable]
**Test Data:** [Dữ liệu test cụ thể nếu cần]
```

Workspace Actions:
- Log confirmed scope + coverage level → `00_task_brief.md`

---

### Step: STEP-01 — Phân tích test targets

Objective:
Từ inputs, xác định toàn bộ testable items: functions, screens, flows, business rules, edge cases.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- I-01 Design doc (full) hoặc I-02 Requirements (full)
- I-03 Acceptance Criteria (nếu có)

Expected Outputs:
- Test target list: nhóm theo feature/screen/function
- Danh sách business rules cần verify
- Danh sách boundary conditions đáng test (nếu coverage level = standard/comprehensive)

Done Condition:
AI có danh sách testable items đầy đủ. BrSE quick-review để confirm không bỏ sót.

Notes / Constraints:
- Phân loại theo: happy path, alternative flows, error conditions, boundary cases
- Log business rules chưa rõ vào `05_open_questions.md`

Workspace Actions:
- Write test target list → `04_findings.md`

---

### Step: STEP-02 — Thiết kế test scenarios

Objective:
Từ test targets, thiết kế test scenarios theo coverage level đã confirm.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Test target list (STEP-01)
- Coverage level confirmed (STEP-00)

Expected Outputs:
- Test scenario list: TC ID placeholder + scenario title + category
- Ước tính số TC theo category

Coverage guide:
| Level | Includes |
|---|---|
| Basic | Normal cases only (happy path per feature) |
| Standard | Normal + Abnormal (invalid inputs, error conditions) |
| Comprehensive | Normal + Abnormal + Boundary + Error handling |

Done Condition:
BrSE confirm scenario list trước khi viết chi tiết. Tránh viết nhiều rồi cắt bỏ.

Notes / Constraints:
- Confirm scenario list trước khi viết chi tiết — tránh viết nhiều rồi cắt bỏ.

Workspace Actions:
- Write scenario list → `07_output_draft.md`

---

### Step: STEP-03 — Viết test case chi tiết

Objective:
Viết đầy đủ nội dung mỗi test case theo format đã confirm.

Recommended Mode:
Generating

Applicable Guidelines:
_(project-specific test standards nếu có)_

Inputs:
- Scenario list confirmed (STEP-02)
- I-01 Design doc / I-02 Requirements (reference for expected results)
- I-04 TC template (nếu có)

Expected Outputs:
- Draft TC document — đầy đủ tất cả TCs

Done Condition:
Tất cả TCs có đầy đủ fields. Open points logged cho business rules chưa rõ.

Notes / Constraints:
- Expected Result phải **cụ thể và verifiable** — không viết "system works correctly"
- Test Steps phải **reproducible** — ai cũng làm được theo đúng step
- Với boundary cases: điền cụ thể test data (e.g., max = 100, test với 99, 100, 101)
- Điền `[OPEN POINT: OP-NNN — expected result chưa rõ]` thay vì assume

Workspace Actions:
- Write draft TC document → `07_output_draft.md`
- Log open points → `05_open_questions.md`

---

### Step: STEP-04 — Coverage Review

Objective:
Kiểm tra coverage — mỗi requirement / acceptance criterion có ít nhất 1 TC.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Draft TC document (STEP-03)
- I-02 Requirements / I-03 Acceptance Criteria

Expected Outputs:
- Coverage matrix: Requirement/AC ID → TC IDs
- Danh sách gaps (requirement chưa có TC)

Done Condition:
Mọi in-scope requirement/AC có ít nhất 1 TC. Gaps documented rõ lý do nếu intentionally skip.

Notes / Constraints:
- Gaps phải documented rõ lý do nếu intentionally skip.

Workspace Actions:
- Write coverage matrix → `04_findings.md`

---

### Step: STEP-05 — BrSE Review Checkpoint + Finalize

Objective:
BrSE review và approve. Address comments, finalize document.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Draft TC document + coverage matrix (STEP-03 + STEP-04)

Expected Outputs:
- BrSE review comments
- Final TC document (sau khi address comments)

Done Condition:
BrSE approve. Blocking open points resolved hoặc logged với action owner.

Notes / Constraints:
- Blocking open points phải resolved hoặc logged với action owner trước khi finalize.

Workspace Actions:
- Apply BrSE comments → update draft
- Move final → `11_output_final/`

---

## Done Criteria

- Test cases cover toàn bộ scope đã confirm tại STEP-00
- Mọi in-scope requirement / acceptance criterion có ít nhất 1 TC
- Mọi TC có đầy đủ fields (TC ID, category, priority, preconditions, steps, expected result)
- Expected results cụ thể và verifiable
- Coverage matrix đầy đủ
- Không có unresolved blocking open points
- BrSE review và approve
- Output lưu đúng path và naming convention

## Self-check / Review Points

Trước finalize:
- TC IDs unique, không trùng
- Expected results verifiable (không mơ hồ)
- Test steps reproducible (ai cũng làm được)
- Coverage không có gap với in-scope requirements

## Finalization Notes

- Naming convention: `TC_<Module>_v<N.N>_<YYYY-MM-DD>.md`
  Ví dụ: `TC_OrderModule_v1.0_2026-04-24.md`
- Version up thay vì overwrite khi requirements thay đổi

## Re-plan Rule

Append Re-plan Log entry khi:
- Design document thay đổi sau STEP-00 (scope/logic change)
- Coverage level thay đổi
- BrSE yêu cầu thêm TC categories không có trong scope ban đầu

## Re-plan Log

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- Tạo mới test case document cho feature/module có AI involvement
- Có design doc hoặc requirements đã confirm làm input

**Khi KHÔNG dùng file này:**
- BrSE tự viết không có AI involvement → không cần AIP
- Chỉ thêm 1-2 test cases vào doc có sẵn → không cần AIP full flow
- Review test case của người khác → dùng `AIP_EXEC_ReviewTestCase.md`

**Customization (dự án tự thêm sau install):**
- Thêm TC fields: Test Environment, Test Type (manual/auto), Related Test Suite
- Thêm TC categories theo testing methodology của dự án
- Adjust coverage standards (e.g., critical features = comprehensive, UI = basic)
- Thêm link sang test management tool nếu dự án dùng (TestRail, Jira Xray, etc.)
