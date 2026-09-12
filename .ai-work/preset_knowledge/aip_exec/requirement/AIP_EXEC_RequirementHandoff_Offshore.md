---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-requirement-handoff-offshore
title: Requirement Handoff to Offshore (Backlog Item + Req Summary + Confirmation Record)
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when scope and output format are already confirmed>"
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Requirement Handoff to Offshore

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Chuyển đổi input đầu vào hỗn hợp (spec, email, meeting notes từ KH Nhật) thành bộ handoff package gồm 3 output: **Backlog Item** (ticket description), **Req Summary** (tóm tắt requirement), và **Confirmation Record** (3 phần: confirm KH, confirm offshore, open points log) — đảm bảo offshore tự thực hiện được mà không cần hỏi lại nhiều vòng.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: requirement_understanding
- Reason: Converting mixed customer inputs (spec/email/meeting) into a handoff package (Backlog Item + Req Summary + Confirmation Record) — understanding the requirements correctly is the core before writing tickets.
- Search/execution effect: Prioritises `requirement_definition`, `meeting_note`, `basic_design` + object kinds (`function`) when ordering the reading surface.
- Expansion allowed: yes — pull the specific spec when a ticket field must be exact; record unknowns in the Confirmation Record open-points log (don't guess).

## Execution Scope

### In Scope
Dùng AIP này khi:
- BrSE đã nắm đủ yêu cầu từ KH Nhật (qua spec / email / meeting)
- format output đã chốt (ngôn ngữ, loại ticket, kênh gửi)
- input sources đã đủ hoặc BrSE biết rõ phần nào thiếu
- task chuyển từ giai đoạn **"hiểu yêu cầu"** sang giai đoạn **"viết ticket và handoff"**

### Out of Scope
Không dùng AIP này khi:
- requirement còn quá mơ hồ, chưa biết scope
- format output chưa chốt (ngôn ngữ, cấu trúc ticket)
- BrSE chưa đọc / chưa hiểu input từ KH
- cần phân tích requirement sâu trước (→ dùng PLAN AIP hoặc Clarify AIP)
- handoff là package lớn cần nhiều BrSE phối hợp (→ dùng Shared AIP)

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Backlog Item (ticket description) | Output chính — ticket với AC, scope, notes; ngôn ngữ theo Step 1 | AI → BrSE review → offshore |
| O-02 | Req Summary | Tóm tắt requirement đi kèm ticket (background, confirmed/pending, điểm offshore chú ý) | AI → BrSE review → offshore |
| O-03 | Confirmation Record (3 parts) | Part 1 KH confirm, Part 2 Offshore confirm, Part 3 Open Points log — trace confirm | AI → BrSE action |
| O-04 | Open Points Log (Part 3 của Confirmation Record) | Cập nhật nếu có điểm mới phát sinh; mỗi open point có owner + next action | AI → BrSE action |
| O-05 | AIP Progress file | Cập nhật status từng step | AI |
| O-06 | Tracker / handoff log | Ghi nhận đã gửi offshore | BrSE |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu đến từ PLAN phase.
Hoặc `direct` — khi scope và format output đã confirmed trước, không cần PLAN phase.

### Required Inputs

| Input | Description | Required / Optional |
|---|---|---|
| I-01 Spec / requirement document | Spec / requirement document từ KH Nhật | Required |
| I-02 Email / chat từ KH | Email / chat từ KH Nhật liên quan yêu cầu | Optional |
| I-03 Meeting notes | Ghi chú / meeting notes từ cuộc họp với KH | Optional |
| I-04 Format mẫu ticket | Format mẫu ticket của dự án | Optional |
| I-05 Open points list | Danh sách open points / câu hỏi chưa giải đáp | Optional |

### Workspace Preconditions
- [ ] PLAN AIP tương ứng đã thực hiện, hoặc input đủ rõ để EXEC trực tiếp
- [ ] BrSE đã có toàn bộ input cần thiết (spec / email / meeting notes)
- [ ] format / ngôn ngữ output đã confirm hoặc sẵn sàng confirm ở Step 1 (STEP-01)
- [ ] danh sách open points đã biết (nếu có) đã visible
- [ ] review viewpoint source đã sẵn (từ PLAN hoặc tạo mới ở Step 6 / STEP-06)

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. BrSE có quyền reject. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Spec / requirement | `<tóm tắt scope yêu cầu>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Email / chat (nếu có) | `<điểm bổ sung / mâu thuẫn so với spec>` | `<assumptions>` | `<gaps>` | ⬜ pending |
| I-03 Meeting notes (nếu có) | `<quyết định / context từ họp>` | — | — | ⬜ pending |

---

## References to Read First

**Required:**
- `<path to spec / requirement document từ KH Nhật (I-01)>`

**Optional:**
- `<path to email / chat từ KH (I-02)>`
- `<path to meeting notes (I-03)>`
- `<path to format mẫu ticket của dự án (I-04)>`
- `<path to danh sách open points (I-05)>`

---

## Current Risks / Constraints

- **Input mâu thuẫn giữa các nguồn:** spec nói khác email → ghi rõ trong Understanding (STEP-02), hỏi BrSE chốt trước khi draft ticket. Không coi spec text là confirmed fact khi có known system conflict.
- **Quá nhiều open point:** nếu open point quá nhiều (>5 blocking items) → cân nhắc tạo PLAN AIP trước để clarify, chưa handoff.
- **Handoff khi chưa confirm hết:** nếu BrSE muốn gửi ticket trước khi confirm hết → ghi rõ pending items trong Confirmation Record Part 3, note "handoff with known gaps".
- **Format ticket thay đổi giữa chừng:** quay lại Step 1 (STEP-01) confirm, chỉ cần redo từ Step 3 (STEP-03) trở đi.
- **Assumption vs confirmed fact:** không có assumption nào được coi là confirmed fact — unknown phải thành OP trong Confirmation Record Part 3.

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Mỗi open point phải có owner + next action. Open point blocking → confirm với BrSE/KH trước khi handoff. Khi open point quá nhiều (>5 blocking) → cân nhắc PLAN AIP để clarify trước.

---

## Workspace Execution Rule

All runtime state (drafts, findings, open points) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)

Objective:
Viết ra ý hiểu về task (scope yêu cầu, expected output: Backlog Item + Req Summary + Confirmation Record, Done definition, assumptions) và dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1

Inputs:
- AIP PLAN handoff / user request
- I-01 Spec / requirement (overview)
- I-02 Email / I-03 Meeting notes (overview, nếu có)

Expected Outputs:
- Task understanding note trong workspace
- BrSE confirmation evidence (user message hoặc ghi chú)

Done Condition:
BrSE explicit confirm ý hiểu (hoặc explicit ủy quyền skip gate).

Notes / Constraints:
- Không làm gì khác ngoài clarify/confirm ở step này.
- Nếu BrSE chỉnh hiểu biết → update note rồi re-confirm trước khi sang STEP-01.

Workspace Actions:
- Write task understanding → `00_task_brief.md`
- Log BrSE confirmation → workspace findings

---

### Step: STEP-01 — Confirm format output + thu thập input

Objective:
Xác nhận format output (ngôn ngữ, loại ticket, kênh gửi) và thu thập đầy đủ input đã nhận.

Recommended Mode:
Clarifying

Applicable Guidelines:
_(none)_

Inputs:
- BrSE cung cấp (format, ngôn ngữ, kênh gửi)
- I-01 Spec / I-02 Email / I-03 Meeting notes / I-04 Format mẫu ticket

Expected Outputs:
- Bảng xác nhận format (ngôn ngữ, format ticket, kênh gửi, priority level)
- Danh sách input đã nhận

Done Condition:
Ngôn ngữ, format ticket, kênh gửi đã confirm; danh sách input đã nhận đầy đủ.

Notes / Constraints:
- **Dual-version ticket:** Nếu KH yêu cầu ticket bằng ngôn ngữ mà offshore không đọc được → tạo dual-version ticket: (1) Bản master (ngôn ngữ KH): KH dùng để review và approve; (2) Bản working copy (EN): offshore dùng để implement — ghi rõ "This is a working copy. Master: [ticket ID ngôn ngữ KH]"; (3) Tuyên bố rõ trong cả 2 bản: bản nào là master; (4) Confirmation Record Part 2 ghi: "If conflict exists between JP and EN ticket, JP master takes precedence — offshore must escalate to BrSE"; (5) BrSE chịu trách nhiệm sync EN working copy sau mỗi lần JP master được update.
- **Dự án chưa có convention ticket:** Nếu dự án chưa có convention ticket → BrSE đề xuất format, confirm với PM/lead trước khi tạo ticket đầu tiên. Ghi nhận convention đã confirm vào Step 1 output (bảng xác nhận format). Sau Step 7, tạo convention document (1 page hoặc Wiki entry) để team reference — không chỉ ghi trong ticket. Step 1 có thể kéo dài hơn bình thường trong trường hợp này.
- **Priority level:** Ghi vào bảng xác nhận format: "Priority level: [Critical / High / Normal / Low] — BrSE confirm theo context yêu cầu". Điền vào Backlog Item Notes và ghi vào tracker ở Step 7.
- **Format thay đổi giữa chừng:** Nếu format ticket thay đổi giữa chừng → quay lại Step 1 (STEP-01) confirm, chỉ cần redo từ Step 3 (STEP-03) trở đi.

Workspace Actions:
- Write bảng xác nhận format + danh sách input → `04_findings.md`

---

### Step: STEP-02 — Tổng hợp Input Understanding

Objective:
Tổng hợp toàn bộ input thành Input Understanding (confirmed / pending / high-risk / out-of-scope / expected action).

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- Toàn bộ input từ Step 1 (STEP-01)

Expected Outputs:
- Understanding: confirmed / pending / high-risk / out-of-scope / expected action

Done Condition:
BrSE confirm Input Understanding trước khi draft ticket.

Notes / Constraints:
- BrSE phải confirm trước khi draft.
- **Input mâu thuẫn:** Nếu input mâu thuẫn giữa các nguồn (spec nói khác email) → ghi rõ trong Understanding, hỏi BrSE chốt trước khi draft ticket.
- **Brand new feature:** Nếu đây là brand new feature (current state = none): khai báo rõ confirmed item: "Feature này là hoàn toàn mới — build from scratch, không có current behavior". Với new feature có component kỹ thuật phức tạp (real-time, permissions, scaling), nhóm OP kỹ thuật vào sub-category riêng trong Part 3 (ví dụ: Architecture OPs) và note "offshore phải confirm với BrSE về các architecture decisions này trước khi commit implementation approach".
- **CRUD screen unknowns:** Với loại chức năng CRUD screen, trước khi draft ticket, kiểm tra tối thiểu 3 standard unknowns sau — nếu KH không specify, tạo OP tương ứng với default assumption: (1) Validation rules cho từng trường (required/optional, unique, format, min/max); (2) Permission model: ai có thể Create/Update/Delete, ai chỉ được Read/Search; (3) Delete behavior: soft delete (ẩn record, data giữ lại) hay hard delete (xóa vĩnh viễn).
- **Cross-module scope:** Nếu requirement ảnh hưởng 3+ màn hình/module: trước khi bắt đầu Step 2, liệt kê đầy đủ tất cả modules/screens bị ảnh hưởng. Thiếu module → AC và out-of-scope không chính xác. Nếu danh sách module chưa rõ → tạo OP blocking, không draft ticket cho đến khi BrSE/KH xác nhận phạm vi.

Workspace Actions:
- Write Input Understanding → `04_findings.md`
- Log open points / mâu thuẫn → `05_open_questions.md`

---

### Step: STEP-03 — Tạo Backlog Item (ticket)

Objective:
Tạo draft Backlog Item (ticket) với AC, scope, notes từ Understanding đã confirm.

Recommended Mode:
Generating

Applicable Guidelines:
_(I-04 format mẫu ticket của dự án nếu có)_

Inputs:
- Understanding đã confirm (STEP-02)

Expected Outputs:
- Draft ticket với AC, scope, notes

Done Condition:
AC phải testable (pass/fail rõ); ticket có scope và notes đầy đủ.

Notes / Constraints:
- **Multi-layer ticket:** Nếu 1 yêu cầu ngầm chứa thay đổi ≥2 layer (UI/BE/DB/external): xác nhận với BrSE — 1 ticket AC chia layer hay tách ticket. Nếu giữ 1 ticket: cấu trúc AC theo section per layer; ghi rõ trong ticket note rằng cần hoàn tất tất cả layer trước khi đóng.
- **Branched AC by role/condition:** Nếu AC phân nhánh theo role hoặc condition: cấu trúc AC thành Branch A / B / C riêng biệt. Mỗi nhánh cần tối thiểu: (1) điều kiện trigger rõ, (2) AC pass/fail testable riêng, (3) negative test (user không đúng role bị block). Cấu trúc này hợp lệ với tiêu chí "AC testable" trong self-review — ghi "PASS (branched)".
- **Khi dự án không có template ticket riêng:** Backlog Item tối thiểu cần bao gồm: (1) Title ngắn gọn có [Screen Name] + action mô tả, (2) Description: hiện trạng và yêu cầu thay đổi, (3) Acceptance Criteria testable (pass/fail rõ), (4) Out of scope (nếu boundary mơ hồ), (5) Notes dành cho offshore (nếu có OP hoặc điểm kỹ thuật đặc biệt).
- **Out-of-scope ngầm:** Khai báo rõ out-of-scope ngầm trong ticket khi chức năng có boundary mơ hồ — ví dụ: "Out of scope: download/save PDF to local disk (not requested)".
- **Feature removal:** Nếu yêu cầu là xóa hoặc disable chức năng hiện có: Step 3 phải include danh sách dependency đã biết và AC yêu cầu offshore tạo dependency map trước khi implement. (Xem thêm Req Summary note ở STEP-04 và blocking OP ở STEP-06.)
- **Rollback scenario:** Nếu yêu cầu là rollback → cấu trúc AC theo rollback scope đã confirm; 2 điểm rollback (scope + dữ liệu sau mốc) phải confirmed hoặc ghi blocking OP trong Part 3 trước khi draft (xem STEP-06).

Workspace Actions:
- Write draft ticket → `07_output_draft.md`

---

### Step: STEP-04 — Tạo Req Summary

Objective:
Tạo draft Req Summary đi kèm ticket — background, confirmed/pending, điểm offshore chú ý.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Understanding (STEP-02) + Ticket (STEP-03)

Expected Outputs:
- Draft summary với background, confirmed/pending, điểm offshore chú ý

Done Condition:
Tách rõ confirmed vs pending; background phù hợp offshore context.

Notes / Constraints:
- **Brand new feature:** Phần Background ghi: "Current state: No [feature name] exists. This is a new feature." thay vì mô tả current behavior.
- **Độ chi tiết Background:** Phụ thuộc vào offshore context (xác nhận tại Step 1 hoặc từ BrSE): (1) Team quen dự án (>3 tháng hoặc đã làm feature liên quan): background tối thiểu — chỉ tên màn hình/feature, link ticket liên quan nếu có; không cần mô tả flow hiện tại. (2) Member mới, team lần đầu nhận feature này, hoặc feature có dependency phức tạp: background đầy đủ — mô tả flow hiện tại, mục đích chức năng, ảnh hưởng tới module khác.
- **Feature removal:** Req Summary phải note "Offshore phải tạo impact assessment document trước — không implement trực tiếp".

Workspace Actions:
- Write draft Req Summary → `07_output_draft.md`

---

### Step: STEP-05 — Tạo Confirmation Record (3 phần)

Objective:
Tạo Confirmation Record 3 phần: Part 1 KH confirm, Part 2 Offshore confirm, Part 3 Open points log.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Outputs của Steps 2–4 (STEP-02 → STEP-04)

Expected Outputs:
- Part 1: KH confirm
- Part 2: Offshore confirm
- Part 3: Open points log

Done Condition:
Mỗi open point phải có owner + action; đầy đủ 3 phần.

Notes / Constraints:
- **Superseded confirm event (Part 1):** Khi KH thay đổi ý sau khi đã confirm: (1) Ghi event mới vào Part 1 với timestamp — không xóa record cũ; (2) Đánh dấu record cũ là "SUPERSEDED by [date/event]"; (3) Ghi rõ version mới nhất là gì và ngày KH confirm lại; (4) Thêm note "Offshore: chỉ implement theo version mới nhất — xem record [date]."
- **External system gate OP (Part 3):** Nếu OP có external dependency (bên ngoài dự án — hệ thống bên thứ ba, đối tác tích hợp): label "HIGH RISK OP — EXTERNAL DEPENDENCY" và ghi rõ: (a) tại sao không thể proceed unilaterally (impact mô tả cụ thể), (b) external contact là ai, (c) escalation path nếu bên ngoài không phản hồi trong X ngày, (d) scope cần bị block cho đến khi external confirmation. Ticket phải có scope isolation: phần nào offshore làm ngay, phần nào BLOCKED pending external confirm.

Workspace Actions:
- Write Confirmation Record (3 parts) → `07_output_draft.md`
- Sync open points (Part 3) → `05_open_questions.md`

---

### Step: STEP-06 — Self-review theo review viewpoint

Objective:
Self-review bộ output (Steps 3–5) theo review viewpoint (6 tiêu chí pass/fail) và fix trước khi handoff.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(review viewpoint source — từ PLAN hoặc tạo mới ở step này)_

Inputs:
- Outputs của Steps 3–5 (STEP-03 → STEP-05)

Expected Outputs:
- Review table (6 tiêu chí pass/fail)

Done Condition:
Tất cả tiêu chí pass; fix trước khi handoff.

Notes / Constraints:
- **Spec mâu thuẫn với hành vi hệ thống hiện tại:** Nếu spec KH rõ về text nhưng mâu thuẫn với behavior hiện tại của hệ thống → ghi vào Understanding là high-risk pending, hỏi BrSE/KH về intent thực trước khi implement. Không coi spec text là confirmed fact khi có known system conflict.
- **Feature removal:** Nếu yêu cầu là xóa hoặc disable chức năng hiện có: (1) Step 3 phải include danh sách dependency đã biết và AC yêu cầu offshore tạo dependency map trước khi implement; (2) Req Summary phải note "Offshore phải tạo impact assessment document trước — không implement trực tiếp"; (3) Nếu dependent feature ảnh hưởng critical (ví dụ: reset password) → ghi rõ là blocking OP, không handoff cho đến khi có giải pháp xử lý.
- **Cross-module scope:** Nếu requirement ảnh hưởng 3+ màn hình/module: trước khi bắt đầu Step 2, liệt kê đầy đủ tất cả modules/screens bị ảnh hưởng. Thiếu module → AC và out-of-scope không chính xác. Nếu danh sách module chưa rõ → tạo OP blocking, không draft ticket cho đến khi BrSE/KH xác nhận phạm vi.
- **Rollback scenario:** Nếu yêu cầu là rollback về phiên bản/mốc thời gian trước → bắt buộc xác nhận 2 điểm sau trước khi draft ticket: (1) rollback scope: code-only, DB schema-only, hay cả hai? (2) dữ liệu mới tạo sau mốc rollback — có tồn tại không? Nếu có → xử lý thế nào (migrate, archive, xóa)? Ghi cả 2 điểm này là OP blocking trong Confirmation Record Part 3. Không handoff cho đến khi ít nhất OP về rollback scope được confirm.
- **Brand new feature:** Nếu đây là brand new feature (current state = none) → xem ghi chú Step 2 (STEP-02) và Step 4 (STEP-04). Đặc biệt chú ý: Architecture OPs cần được nhóm riêng trong Part 3 và offshore phải confirm approach với BrSE trước khi commit.
- **Lưu ý tiêu chí "Ticket có AC testable":** PASS nếu (a) AC testable hoàn toàn (pass/fail rõ), HOẶC (b) AC có placeholder rõ ràng tham chiếu OP cụ thể `[pending OP-X]` kèm OP tương ứng trong Part 3. Với branched AC (phân nhánh theo role/condition): mỗi nhánh testable riêng là đủ — ghi "PASS (branched)" trong self-review.

Workspace Actions:
- Write review table + fixes → `04_findings.md`

---

### Step: STEP-07 — Finalize / update tracker / handoff

Objective:
Finalize reviewed package, update tracker, và handoff cho offshore.

Recommended Mode:
Executing

Applicable Guidelines:
_(none)_

Inputs:
- Reviewed package (STEP-06)

Expected Outputs:
- Final handoff package gửi offshore

Done Condition:
Update progress, lưu file nếu cần; handoff package đã gửi cho offshore, tracker cập nhật.

Notes / Constraints:
- **Convention Note** (chỉ khi Step 1 / STEP-01 tạo convention mới lần đầu cho dự án) — tạo `ticket_convention.md` hoặc Wiki page ghi format đã chọn, lý do, ngày confirm, người duyệt. Lưu vào project reference folder hoặc announce qua team channel.
- **Handoff với known gaps:** Nếu BrSE muốn gửi ticket trước khi confirm hết → ghi rõ pending items trong Confirmation Record Part 3, note "handoff with known gaps".

Workspace Actions:
- Move final package → `11_output_final/`
- Update AIP progress + tracker / handoff log

---

## Done Criteria

- [ ] input understandings đã được BrSE confirm (Step 2 / STEP-02)
- [ ] Backlog Item draft đã reviewed và accepted (Step 3 / STEP-03)
- [ ] Req Summary draft đã reviewed và accepted (Step 4 / STEP-04)
- [ ] Confirmation Record đầy đủ 3 phần, open points có owner (Step 5 / STEP-05)
- [ ] self-review đã thực hiện, tất cả tiêu chí pass (Step 6 / STEP-06)
- [ ] handoff package đã gửi cho offshore, tracker cập nhật (Step 7 / STEP-07)
- [ ] **Gate U1** confirmed — evidence trong workspace
- [ ] **Gate U2** Input Understanding đã ghi và BrSE confirm
- [ ] **Gate U3** Mọi open point trong `05_open_questions.md` đã resolved / deferred / rejected với conclusion rõ ràng (hoặc không phát sinh open point)

## Self-check / Review Points

Checklist tự kiểm trong lúc thực thi:

- [ ] Step 2 đã được BrSE confirm trước khi tạo ticket?
- [ ] Ticket có AC testable (pass/fail rõ)?
- [ ] Confirmed vs pending không bị lẫn lộn?
- [ ] Mỗi open point trong Part 3 có owner + next action?
- [ ] Ngôn ngữ output đúng theo Step 1?
- [ ] Không có assumption nào bị coi là confirmed fact?
- [ ] Out of scope đã khai báo rõ trong ticket?

**Lưu ý tiêu chí "Ticket có AC testable":** PASS nếu (a) AC testable hoàn toàn (pass/fail rõ), HOẶC (b) AC có placeholder rõ ràng tham chiếu OP cụ thể `[pending OP-X]` kèm OP tương ứng trong Part 3. Với branched AC (phân nhánh theo role/condition): mỗi nhánh testable riêng là đủ — ghi "PASS (branched)" trong self-review.

## Finalization Notes

**Ví dụ 1 — Normal case (flow thẳng):**
BrSE nhận email KH yêu cầu thêm nút "In PDF" vào màn hình chi tiết đơn hàng. Step 1: confirm format (Backlog EN, Req Summary EN, Confirmation Record VI), priority Normal. Step 2: Understanding — 4 confirmed items, 1 OP nhỏ (font tiếng Nhật). Step 3: ticket với 4 AC testable + AC-5 `[pending OP-1]`. Step 4: Req Summary — confirmed/pending tách rõ. Step 5: Confirmation Record 3 phần, OP-1 có owner + next action. Step 6: self-review pass 7 tiêu chí. Step 7: handoff, tracker cập nhật Done.

**Ví dụ 2 — Abnormal case (input mâu thuẫn):**
BrSE nhận 3 nguồn input mâu thuẫn về số dòng hiển thị trong kết quả tìm kiếm (spec: 50, email KH: không giới hạn, meeting notes: 100/page). Step 2: ghi cả 3 nguồn vào Understanding dạng conditional AC — `[pending OP-1: option A/B/C]`. Decision/branch handling: không phải >5 blocking OPs nên không trigger PLAN AIP. Step 3: ticket với AC conditional rõ ràng. Handoff với note "Start development after OP-1 confirmed".

**Ví dụ 3 — Edge case (rollback + HIGH RISK):**
KH yêu cầu rollback về trước ngày 1/4. Decision/branch handling trigger rollback branch: BrSE xác nhận rollback scope (code + DB schema) và dữ liệu sau 1/4 trước khi draft ticket. Step 5: 2 OP blocking được ghi HIGH RISK trong Part 3. Handoff bị hold cho đến khi OP về rollback scope được KH confirm bằng văn bản.

**Ví dụ 4 — Feature removal với dependency:**
KH yêu cầu bỏ chức năng gửi email thông báo. Decision/branch handling trigger feature removal branch: Step 3 ticket phải include dependency map (đặt hàng, reset password, báo cáo tuần đều gọi email). Req Summary note "offshore tạo impact assessment trước". Chức năng reset password là critical → blocking OP, không handoff cho đến khi có giải pháp thay thế.

## Re-plan Rule

Append Re-plan Log entry khi cần thay đổi macro scope hoặc expected output:
- không silently drift
- tạo explicit re-plan entry trong "Re-plan Log" section bên dưới
- ghi evidence ref vào workspace findings/capture trước khi chỉnh AIP
- ví dụ trigger: open point quá nhiều (>5 blocking) cần chuyển sang PLAN AIP để clarify; format ticket thay đổi giữa chừng cần redo từ Step 3.

## Re-plan Log

<!-- Append entry on scope/objective/output change. Format: ### YYYY-MM-DD — title / Trigger / Change / Evidence ref / Approved by. -->

- (no re-plan yet)

---

## Guidance Notes

**Decision / branch handling (tổng hợp):**
- Nếu input mâu thuẫn giữa các nguồn (spec nói khác email) → ghi rõ trong Understanding Step 2 (STEP-02), hỏi BrSE chốt trước khi draft ticket.
- Nếu open point quá nhiều (>5 blocking items) → cân nhắc tạo PLAN AIP trước để clarify, chưa handoff.
- Nếu BrSE muốn gửi ticket trước khi confirm hết → ghi rõ pending items trong Confirmation Record Part 3, note "handoff with known gaps".
- Nếu format ticket thay đổi giữa chừng → quay lại Step 1 (STEP-01) confirm, chỉ cần redo từ Step 3 (STEP-03) trở đi.

**Khi nào dùng file này:**
- BrSE đã nắm đủ yêu cầu từ KH Nhật, format output đã chốt, task chuyển từ "hiểu yêu cầu" sang "viết ticket và handoff".

**Khi KHÔNG dùng file này:**
- requirement còn quá mơ hồ, chưa biết scope; format output chưa chốt; BrSE chưa đọc/hiểu input từ KH; cần phân tích requirement sâu trước (→ PLAN AIP hoặc Clarify AIP); handoff là package lớn cần nhiều BrSE phối hợp (→ Shared AIP).

## Changelog

- Re-authored from legacy preset `AIP_EXEC_RequirementHandoff_Offshore.md` (v1.1, 2026-04-15) into the current AIP_EXEC structure on 2026-06-20. Mapped PLAN sample: `AIP_Sample_RequirementHandoff_Offshore.md`. Original purpose preserved: hướng dẫn thực thi từng bước khi scope/format đã rõ — tạo Backlog Item + Req Summary + Confirmation Record để handoff cho offshore. All documented steps, branch-handling notes, self-check items, completion criteria, and sample execution notes carried over verbatim.
