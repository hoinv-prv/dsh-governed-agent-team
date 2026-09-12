---
artifact_type: aip_exec
artifact_id: AIP-EXEC-XXX
title: "Truyền Đạt Yêu Cầu Khách Hàng Cho Offshore"
status: draft
project: "<project-name>"
owner: "<owner>"
plan_source: "<direct execution | AIP-PLAN-XXX>"
updated_at: 0000-00-00
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Truyền Đạt Yêu Cầu Khách Hàng cho Offshore

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates áp cho **mọi task substantive**:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — xem `STEP-00` bên dưới
- **Gate U2 Confirm-understanding-of-input (soft)** — xem `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — xem `## Known Open Points` + workspace `05_open_questions.md`

## Objective
Tiếp nhận yêu cầu từ khách hàng (qua file tài liệu, meeting notes, hoặc verbal), phân tích và cấu trúc lại, tạo **ticket mô tả chi tiết** và **summary message** để truyền đạt rõ ràng cho offshore team.

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: requirement_understanding
- Reason: Receiving + restructuring customer requirements into tickets/summary for offshore — the work is understanding the requirements correctly before relaying them.
- Search/execution effect: Prioritises `requirement_definition`, `meeting_note`, `basic_design` + object kinds (`function`) when assembling inputs and ordering the reading surface.
- Expansion allowed: yes — pull the specific spec/design when a requirement detail must be exact before handoff; do not decide technical approach (offshore's call).

## Execution Scope

### In Scope
- Đọc và tổng hợp input yêu cầu (bất kỳ dạng: file tài liệu / meeting notes / verbal từ BrSE)
- Phân tích, cấu trúc yêu cầu thành danh sách rõ ràng
- Xác định output format và detail level (thảo luận với BrSE tại STEP-02)
- Draft ticket(s) theo cấu trúc chuẩn 8 sections
- Draft summary message gửi offshore (email hoặc chat)
- BrSE review và finalize output

### Out of Scope
- Quyết định technical approach (offshore tự quyết)
- Tạo design doc / spec chi tiết (cần AIP riêng nếu phức tạp)
- Import ticket vào PM tool (Jira / Backlog / v.v.) — human action

## Expected Outputs

| # | Output | Mô tả |
|---|---|---|
| O-01 | Ticket file(s) | Mỗi requirement → 1 file. Cấu trúc 8 sections chuẩn (xem bên dưới) |
| O-02 | Summary message | Tóm tắt gửi offshore qua email/chat: context, danh sách tickets, Q&A nếu có |

### Cấu trúc Ticket chuẩn (8 sections — thứ tự theo luồng đọc)

| # | Section | Mục đích |
|---|---|---|
| S1 | **Title** | Tên ngắn gọn — offshore đọc là hiểu ngay việc cần làm. Format: `[Động từ] [Đối tượng]` |
| S2 | **Priority** | Độ ưu tiên ngay từ đầu để triage. Format: `High / Medium / Low` + lý do ngắn |
| S3 | **Background** | Tại sao yêu cầu này tồn tại — ngữ cảnh nghiệp vụ, nguồn yêu cầu |
| S4 | **Scope** | Làm gì / KHÔNG làm gì — In Scope + Out of Scope rõ ràng |
| S5 | **Screen / UI Reference** | Visual reference TRƯỚC khi đọc AC — link Figma, screenshot, wireframe, hoặc mô tả UI |
| S6 | **Acceptance Criteria** | Điều kiện done testable. Simple → checklist; complex/edge-case → Given/When/Then |
| S7 | **Technical Notes** | Gợi ý kỹ thuật: API, DB, business rule, edge case, performance/security constraint |
| S8 | **Open Questions / Q&A** | Câu chưa rõ cần offshore hoặc BrSE confirm. Format: ID + câu hỏi + trạng thái |

## Execution Input Package

### Plan Source
- Direct execution — không có AIP_PLAN. User request <YYYY-MM-DD>.

### Required Truth Inputs
- SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) — Universal Gates U1/U2/U3

### Required Wiki Inputs
- (không yêu cầu wiki cố định — tùy project instance)

### Required Workspace Preconditions
- [ ] Workspace created if needed
- [ ] Active Step Context available
- [ ] `05_open_questions.md` initialized (nếu dự kiến có open points)

## Input Understanding
<!-- Gate U2 — soft gate. Input Understanding được ghi vào workspace (04_findings.md), không trực tiếp trong AIP — stability rule: runtime state không thuộc AIP. -->
→ Xem `04_findings.md` trong workspace của task instance.

## References to Read First
- SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) — Gates U1/U2/U3
- Input artifacts cụ thể sẽ được xác định tại STEP-00/STEP-01

## Current Risks / Constraints
- Input đa dạng (file / meeting notes / verbal) → mức độ đầy đủ thông tin khác nhau mỗi lần chạy
- Detail level của ticket tùy từng task — cần confirm với BrSE tại STEP-02 trước khi draft
- Ngôn ngữ output (Việt / Nhật / song ngữ) cần xác nhận tại STEP-00

## Known Open Points
<!-- Gate U3. Summary here; detail + history trong `05_open_questions.md` của workspace. -->
- Open Points log: `.ai-work/workspaces/{TASK-ID}/05_open_questions.md`
- (no open points yet)

## Workspace Execution Rule
All execution steps should update workspace artifacts when applicable:
- Active Step Context
- Queue
- Findings (`04_findings.md`)
- Open Questions (`05_open_questions.md`) — Gate U3
- Ticket drafts (`07_output_drafts/TICKET-*.md`)
- Summary message draft (`07_output_drafts/SUMMARY_MESSAGE.md`)
- Final output (`11_output_final/`)

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding + Ngôn Ngữ Output (HARD GATE)
<!-- Gate U1 — Universal. Bắt buộc. Toàn bộ step này chạy ở chế độ Planning — không thực thi gì cho đến khi BrSE approve. -->

Objective:
Viết ra ý hiểu về task instance cụ thể (scope, loại input, số requirement dự kiến, Done definition). Xác nhận ngôn ngữ output. Dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Planning

Applicable Guidelines:
- SOP_MASTER Gate U1

Recommended Skills:
- **AskUserQuestion** — bắt buộc dùng popup cho lựa chọn ngôn ngữ output (xem bên dưới)

Inputs:
- User request / yêu cầu từ BrSE
- Tên project (nếu có)
- Thông tin sơ bộ về requirement (nếu BrSE đã cung cấp)

Expected Outputs:
- Task understanding note trong workspace (`04_findings.md` hoặc file riêng)
- Xác nhận ngôn ngữ output từ BrSE — **phải hiện popup AskUserQuestion**, không để nhập tay:
  ```
  AskUserQuestion(
    question: "Ngôn ngữ output cho ticket và summary message?",
    type: "single_choice",
    options: [
      "Tiếng Việt",
      "Tiếng Nhật (日本語)",
      "Song ngữ Việt–Nhật",
      "Tuỳ nội dung (BrSE chỉ định từng phần)"
    ]
  )
  ```
- BrSE confirmation evidence (user message hoặc ghi chú)

Done Condition:
BrSE explicit confirm ý hiểu task VÀ đã chọn ngôn ngữ output (hoặc explicit ủy quyền skip gate).

Notes / Constraints:
- Không bắt đầu đọc input hoặc draft gì ở step này.
- Nếu BrSE chỉnh hiểu biết → update note rồi re-confirm trước khi sang STEP-01.

Workspace Actions:
- Write task understanding → `04_findings.md`
- Ghi ngôn ngữ output đã confirm → `04_findings.md`
- Log BrSE confirmation

---

### Step: STEP-01 — Thu Thập và Đọc Input Yêu Cầu

Objective:
Đọc và tổng hợp toàn bộ input yêu cầu từ BrSE. Ghi Input Understanding (Gate U2).

Recommended Mode:
Research

Applicable Guidelines:
- SOP_MASTER Gate U2

Recommended Skills:
- (none)

Inputs:
- File tài liệu yêu cầu (nếu có)
- Meeting notes (nếu có)
- Thông tin verbal từ BrSE (nếu không có file)

Expected Outputs:
- Input Understanding table điền đầy đủ (từng artifact → key points, assumptions, ambiguities)
- Danh sách sơ bộ các requirement phát hiện được (để chuẩn bị cho STEP-02)

Done Condition:
Tất cả input đã đọc. Input Understanding table đã ghi đầy đủ. Nếu input chưa có → ghi nhận trạng thái "chờ BrSE cung cấp" và dừng tại đây.

Notes / Constraints:
- Nếu input là verbal/chat → ghi lại dưới dạng structured note trong workspace trước khi phân tích.
- Nếu input không đầy đủ → raise Open Point (Gate U3) ngay tại bước này.

Workspace Actions:
- Write Input Understanding → `04_findings.md` (không update bảng trong AIP — stability rule)
- Write findings summary → `04_findings.md`
- Log open points phát sinh → `05_open_questions.md`

---

### Step: STEP-02 — Phân Tích Yêu Cầu + Xác Định Output Format

Objective:
Phân tích input, liệt kê danh sách requirements. Đề xuất số lượng ticket, cấu trúc và level of detail. Dừng chờ BrSE confirm format trước khi draft.

Recommended Mode:
Planning

Applicable Guidelines:
- (none cụ thể — judgment call dựa trên độ phức tạp của requirement)

Recommended Skills:
- **AskUserQuestion** — bắt buộc dùng popup cho lựa chọn detail level và Q&A list (xem bên dưới)

Inputs:
- Input Understanding từ STEP-01
- Findings summary trong workspace

Expected Outputs:
- Danh sách requirements có cấu trúc (ID + tên ngắn + loại: feature / fix / change)
- Đề xuất output format — **phải hiện popup AskUserQuestion**, không để nhập tay:
  ```
  AskUserQuestion(
    question: "Level of detail cho ticket?",
    type: "single_choice",
    options: [
      "Brief (S1–S4 only)",
      "Full spec (S1–S8)"
    ]
  )

  AskUserQuestion(
    question: "Có cần Q&A list riêng (ngoài S8 trong ticket) không?",
    type: "single_choice",
    options: [
      "Có — tổng hợp Q&A list riêng trong summary message",
      "Không — chỉ ghi trong S8 của từng ticket"
    ]
  )
  ```
- BrSE confirmation về format

Done Condition:
BrSE đã confirm danh sách requirements và output format (ticket count + detail level) trước khi sang STEP-03.

Notes / Constraints:
- Không draft ticket trước khi BrSE confirm format ở step này.
- Nếu requirements quá phức tạp → đề xuất tách thành nhiều AIP_EXEC riêng.

Workspace Actions:
- Write requirements list → `04_findings.md`
- Write output format proposal → `04_findings.md`
- Log BrSE confirmation về format

---

### Step: STEP-03 — Draft Tickets

Objective:
Draft ticket cho từng requirement theo format đã confirm ở STEP-02, sử dụng cấu trúc 8 sections chuẩn và ngôn ngữ đã xác nhận ở STEP-00.

Recommended Mode:
Executing

Applicable Guidelines:
- Cấu trúc Ticket 8 sections trong section ## Expected Outputs

Recommended Skills:
- (none)

Inputs:
- Requirements list từ STEP-02
- Output format đã confirm (detail level, ngôn ngữ)
- Input Understanding từ STEP-01

Expected Outputs:
- N file ticket drafts: `07_output_drafts/TICKET-{ID}-{slug}.md`
- Mỗi file gồm 8 sections theo cấu trúc chuẩn (bỏ qua section không áp dụng với note "N/A — [lý do]")

Done Condition:
Tất cả requirements đã có ticket draft. Mỗi ticket có đủ các sections bắt buộc (S1–S6 tối thiểu). Open questions phát sinh đã được log.

Notes / Constraints:
- Nếu brief mode (S1–S4 only) → ghi rõ "Brief ticket — S5–S8 skipped per BrSE instruction."
- Mỗi AC là 1 điều kiện độc lập, không gộp.
- Không tự quyết định technical approach.

Workspace Actions:
- Write `07_output_drafts/TICKET-{ID}-{slug}.md` cho mỗi requirement
- Log open points phát sinh → `05_open_questions.md`

---

### Step: STEP-04 — Draft Summary Message

Objective:
Draft summary message ngắn gọn để BrSE gửi cho offshore qua email hoặc chat. Ngôn ngữ theo xác nhận ở STEP-00.

Recommended Mode:
Executing

Applicable Guidelines:
- (none)

Recommended Skills:
- (none)

Inputs:
- Ticket drafts từ STEP-03
- Kênh giao tiếp (email / Slack / Chatwork / Teams — BrSE chỉ định)

Expected Outputs:
- `07_output_drafts/SUMMARY_MESSAGE.md` gồm:
  - Context ngắn (1–2 câu lý do gửi)
  - Danh sách tickets kèm title và priority
  - Q&A list tổng hợp từ Open Questions (nếu có)
  - Yêu cầu offshore confirm trước khi bắt đầu (nếu có open points)

Done Condition:
Summary message draft hoàn thành, ngắn gọn, phù hợp kênh giao tiếp.

Notes / Constraints:
- Không gửi trực tiếp — BrSE review và tự gửi.
- Nếu có nhiều open points nghiêm trọng → đề xuất BrSE gặp offline trước khi gửi ticket cho offshore.

Workspace Actions:
- Write `07_output_drafts/SUMMARY_MESSAGE.md`

---

### Step: STEP-05 — BrSE Review + Finalize

Objective:
BrSE review toàn bộ tickets và summary message. AI chỉnh sửa theo feedback. Finalize output khi BrSE approve.

Recommended Mode:
Reviewing

Applicable Guidelines:
- (none)

Recommended Skills:
- (none)

Inputs:
- Ticket drafts từ STEP-03
- Summary message draft từ STEP-04
- Feedback từ BrSE

Expected Outputs:
- Final ticket files trong `11_output_final/`
- Final summary message trong `11_output_final/`

Done Condition:
BrSE explicit approve output. Files final đã được copy vào `11_output_final/`.

Notes / Constraints:
- Nếu BrSE yêu cầu thay đổi lớn về scope → append Re-plan Log entry, không silently drift.
- Nếu open points chưa resolved → deferred với ETA hoặc reject với rationale rõ.

Workspace Actions:
- Update tickets theo feedback → re-write trong `07_output_drafts/`
- Copy final output → `11_output_final/`
- Update `05_open_questions.md` — resolved / deferred / rejected với conclusion
- Log BrSE approval

---

## Done Criteria
- [ ] Ticket file(s) đúng loại, đúng scope đã confirm ở STEP-00
- [ ] Summary message phù hợp kênh giao tiếp, ngôn ngữ đúng như đã xác nhận
- [ ] **Gate U1** confirmed — BrSE confirm task understanding + ngôn ngữ trước STEP-01
- [ ] **Gate U2** Input Understanding đã ghi (hoặc task không có file input)
- [ ] **Gate U3** Mọi open point trong `05_open_questions.md` đã resolved / deferred / rejected với conclusion rõ ràng

## Self-check / Review Points
- Mỗi ticket: có đủ S1–S6 tối thiểu; S7/S8 để "N/A" nếu không áp dụng (có lý do)
- AC: mỗi dòng là 1 điều kiện độc lập, testable
- Summary message: ngắn gọn, không lặp lại toàn bộ nội dung ticket
- Ngôn ngữ output nhất quán với lựa chọn tại STEP-00
- Không có technical decision nào do AI tự đưa ra mà chưa qua BrSE confirm

## Finalization Notes
- Output cuối nằm trong `11_output_final/` của workspace
- BrSE tự gửi summary message và ticket files cho offshore
- Nếu cần import vào PM tool → human action sau khi finalize

## Re-plan Rule
Nếu cần thay đổi macro scope hoặc expected output:
- không silently drift
- tạo explicit re-plan entry trong "Re-plan Log" section bên dưới
- ghi evidence ref vào workspace findings/capture trước khi chỉnh AIP

## Re-plan Log
<!-- Append entry on scope/objective/output change. Format: ### YYYY-MM-DD — title / Trigger / Change / Evidence ref / Approved by. -->

- (no re-plan yet)
