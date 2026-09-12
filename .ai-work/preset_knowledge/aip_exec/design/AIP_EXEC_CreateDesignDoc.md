---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-create-design-doc
title: Create Design Document (BD / DD / Screen Design)
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when design type and scope are already confirmed>"
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Create Design Document

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Tạo tài liệu thiết kế phần mềm có cấu trúc từ yêu cầu đã xác nhận. Loại tài liệu:
- **BD (Basic Design)** — thiết kế tổng thể: module decomposition, system flow, component interaction
- **DD (Detail Design)** — thiết kế chi tiết: class/function/API/logic xử lý, data flow
- **Screen Design** — thiết kế màn hình: layout, UI components, screen flow, field specs

> Loại tài liệu cụ thể xác nhận tại STEP-00. Một AIP instance = một loại document.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: design_review
- Reason: Authoring a design doc (BD/DD/Screen) from confirmed requirements — read requirements + existing design in design terms (correctness, completeness, traceability).
- Search/execution effect: Prioritises `requirement_definition`, `basic_design`, `detailed_design_*`, `screen_mockup`, `db_schema`, `api_manual` + object kinds (`function`/`screen`/`table`/`api`) when assembling inputs and ordering the reading surface.
- Expansion allowed: yes — read upstream requirements / raw source when a design point needs evidence; do not invent unconfirmed requirements (log Open Points).

## Execution Scope

### In Scope
- Phân tích inputs (requirements, architecture, existing design)
- Draft và refine tài liệu design theo loại đã xác nhận
- Self-review: consistency với requirements, completeness, traceability
- BrSE review checkpoint trước finalize

### Out of Scope
- Không tự quyết định yêu cầu chưa confirm — log vào Open Points
- Không tạo code, prototype, hoặc implementation artifacts
- Không resolve architecture decisions chưa được approve
- Không review design của người khác — dùng AIP_EXEC_ReviewDesign.md

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Design Document (MD) | Tài liệu thiết kế hoàn chỉnh theo loại (BD / DD / Screen Design) | AI → BrSE review |
| O-02 | Open Points Log | Các điểm thiết kế còn pending, cần confirm | AI → BrSE action |
| O-03 | Traceability Note | Mapping requirement ID → design section (nếu requirements có ID) | AI → BrSE review |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu đến từ PLAN phase.
Hoặc `direct` — khi design type và scope đã confirmed trước, không cần PLAN phase.

### Required Inputs

| Input | Description | Required / Optional |
|---|---|---|
| I-01 Requirements / Spec | Yêu cầu đã confirm (RD, user story, spec doc, requirement list) | Required |
| I-02 Architecture / System Context | Tổng quan hệ thống, module boundaries, tech stack | Required (BD / DD) |
| I-03 Design Template | Template riêng của dự án nếu có | Optional |
| I-04 Existing Design Doc | Phiên bản hiện tại nếu đây là update | Optional |
| I-05 UI Mockup / Wireframe | Sketch hoặc wireframe — cho Screen Design | Optional (Screen Design) |

### Workspace Preconditions
- [ ] Design type đã xác nhận: BD / DD / Screen Design
- [ ] Scope / module đã chốt
- [ ] Requirements (I-01) đã được confirm — không còn blocking ambiguities

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Requirements | `<tóm tắt scope, số requirements, confirmed/ambiguous ratio>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Architecture | `<tóm tắt system context, modules liên quan>` | `<assumptions>` | `<gaps>` | ⬜ pending |
| I-04 Existing doc (nếu có) | `<version hiện tại, phạm vi cần update>` | — | — | ⬜ pending |

---

## References to Read First

**Required:**
- `<path to requirements / spec (I-01)>`
- `<path to architecture / system context (I-02)>`

**Optional:**
- `<path to existing design doc (I-04)>`
- `<path to design template (I-03)>`
- `<path to UI mockup / wireframe (I-05)>`

---

## Current Risks / Constraints

- **Ambiguous requirements:** Requirement chưa confirm → log Open Points, không tự assume
- **Missing architecture context:** Thiếu I-02 cho BD/DD → design có thể không nhất quán với system
- **Scope creep:** Tránh thiết kế tính năng ngoài scope đã confirm tại STEP-00
- **Customization note:** Template này là generic baseline — dự án customize sections và format theo nhu cầu

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ open point thiết kế nào vào file trên. Open point blocking → confirm với BrSE trước khi tiếp.

---

## Workspace Execution Rule

All runtime state (drafts, findings, open points) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)

Objective:
Xác nhận: loại document (BD/DD/Screen), scope/module cụ thể, inputs có đủ không, format output, review expectation.

Recommended Mode:
Clarifying

Applicable Guidelines:
SOP_MASTER Gate U1

Inputs:
- I-01 Requirements (overview)
- I-02 Architecture context (overview)

Expected Outputs:
- Xác nhận loại document, scope, inputs
- Sơ bộ outline các sections dự kiến
- BrSE confirmation

Done Condition:
BrSE confirm AI hiểu đúng scope và loại document. Inputs đủ để proceed.

Notes / Constraints:
- Nếu thiếu I-01 (requirements chưa confirm) → STOP, yêu cầu BrSE cung cấp trước khi tiếp tục
- Xác nhận có design template riêng (I-03) không — nếu có thì dùng

Workspace Actions:
- Log confirmed scope → `00_task_brief.md`

---

### Step: STEP-01 — Phân tích inputs, xây dựng design understanding

Objective:
Đọc kỹ toàn bộ inputs. Nắm rõ domain, flow, constraints, design decisions cần make trước khi draft.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- I-01 Requirements (full)
- I-02 Architecture context
- I-04 Existing design doc (nếu có)

Expected Outputs:
- Design understanding note: key entities, flows, business rules, constraints
- Danh sách design decisions cần make

Done Condition:
AI có đủ understanding để draft. Điểm chưa rõ → log Input Understanding table và `05_open_questions.md`.

Notes / Constraints:
- Không assume để fill gap — log vào open points
- Với Screen Design: xác định screens, navigation flow, shared components trước

Workspace Actions:
- Write design understanding → `04_findings.md`

---

### Step: STEP-02 — Draft document structure

Objective:
Tạo outline chi tiết, confirm với BrSE trước khi viết nội dung đầy đủ.

Recommended Mode:
Generating

Applicable Guidelines:
_(sử dụng I-03 design template nếu có)_

Inputs:
- Design understanding (STEP-01)
- I-03 Design template (nếu có)

Expected Outputs:
- Document outline: danh sách sections + brief description mỗi section

Done Condition:
BrSE confirm structure trước khi viết nội dung. Tránh viết nhiều rồi restructure lại.

Notes / Constraints:
- Confirm structure với BrSE trước khi viết nội dung — tránh viết nhiều rồi restructure lại.

Workspace Actions:
- Write outline → `07_output_draft.md`

---

### Step: STEP-03 — Viết nội dung design

Objective:
Viết nội dung đầy đủ từng section theo outline đã confirm.

Recommended Mode:
Generating

Applicable Guidelines:
_(project-specific design guidelines nếu có)_

Inputs:
- Outline confirmed (STEP-02)
- I-01 Requirements + I-02 Architecture (reference)
- I-05 UI mockup (nếu có, cho Screen Design)

Expected Outputs:
- Draft design document — đầy đủ nội dung tất cả sections

Done Condition:
Tất cả sections có nội dung. Open points logged, không để trống không giải thích.

Notes / Constraints:
- Điền `[OPEN POINT: OP-NNN]` tại chỗ chưa có thông tin — không assume
- Screen Design: mỗi màn hình phải có layout description, field list, screen flow
- DD: mỗi function/API phải có inputs, outputs, logic, error handling

Workspace Actions:
- Write draft → `07_output_draft.md`
- Log open points → `05_open_questions.md`

---

### Step: STEP-04 — Self-review

Objective:
Kiểm tra chất lượng draft trước khi gửi BrSE review.

Recommended Mode:
Reviewing

Applicable Guidelines:
`AIP_REVIEW_CHECKLIST_v0_3.md` (nếu applicable)

Inputs:
- Draft design document (STEP-03)

Expected Outputs:
- Self-review checklist result + fixes

Self-review checklist:
- [ ] Mọi requirement trong I-01 được address (traceability rõ)
- [ ] Không có assumption ẩn — assumptions phải explicit
- [ ] Không có internal contradiction (section A mâu thuẫn section B)
- [ ] Open points có ID, không để "TBD" vô danh
- [ ] Format nhất quán (heading levels, table format, naming)
- [ ] Usable cho downstream (team có thể implement/test từ document này)

Done Condition:
Tất cả items PASS hoặc issues đã fix.

Notes / Constraints:
- Self-review là gate trước BrSE review — mọi item phải PASS hoặc issue đã fix trước khi chuyển STEP-05.

Workspace Actions:
- Write self-review notes → `04_findings.md`

---

### Step: STEP-05 — BrSE Review Checkpoint + Finalize

Objective:
BrSE review và approve document. Address comments, finalize.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Draft document (STEP-03 + STEP-04 fixes)

Expected Outputs:
- BrSE review comments
- Final design document (sau khi address comments)
- Final open points list (các items deferred sang next iteration)

Done Condition:
BrSE approve. Blocking open points resolved hoặc logged với action owner và timeline.

Notes / Constraints:
- Blocking open points phải resolved hoặc logged với action owner và timeline trước khi finalize.

Workspace Actions:
- Apply BrSE comments → update draft
- Move final → `11_output_final/`

---

## Done Criteria

- Design document cover đủ scope đã confirm tại STEP-00
- Mọi requirement trong I-01 được address
- Không có unresolved blocking open points
- Self-review STEP-04 PASS
- BrSE review và approve
- Output lưu đúng path và naming convention

## Self-check / Review Points

Trước finalize:
- Requirements traceable → design sections
- Assumptions explicit (không ẩn trong content)
- Open points có ID và action owner
- Document usable cho downstream (dev / QA / offshore)

## Finalization Notes

- Naming convention: `<DocType>_<Module>_v<N.N>_<YYYY-MM-DD>.md`
  Ví dụ: `BD_OrderModule_v1.0_2026-04-24.md`
- Version up thay vì overwrite khi có thay đổi sau review

## Re-plan Rule

Append Re-plan Log entry khi:
- Requirements thay đổi sau STEP-00 (scope change)
- Architecture context thay đổi đáng kể
- BrSE yêu cầu restructure document (không chỉ content fix)

## Re-plan Log

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- Tạo BD / DD / Screen Design document có AI involvement
- Có requirements đã confirm làm input

**Khi KHÔNG dùng file này:**
- BrSE tự viết không có AI involvement → không cần AIP
- Chỉ sửa nhỏ 1 field hoặc thêm 1 note vào doc có sẵn → không cần AIP full flow
- Cần review design (không tạo mới) → dùng `AIP_EXEC_ReviewDesign.md`

**Customization (dự án tự thêm sau install):**
- Thêm sections đặc thù: security requirements, performance specs, API spec format
- Điều chỉnh self-review checklist theo coding/design standards của dự án
- Thêm mandatory fields cho từng loại document theo convention nội bộ
