---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-create-chat-confirm-requirement
title: Create Chat to Confirm Requirement with Customer
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when grouped open points + understandings are already confirmed by PLAN/brief>"
mapped_skill: /aiws-util-mail-confirm
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Create Chat to Confirm Requirement with Customer

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Soạn chat confirm với KH Nhật — ngắn gọn, tự nhiên, đúng trọng tâm — bằng cách tách rõ bước làm rõ tiếng Việt (BrSE xác nhận) và bước soạn tiếng Nhật (dễ chỉnh từng phần độc lập). Cụ thể: trước hết AI trình bày lại Input Understandings bằng **tiếng Việt** để BrSE review/chỉnh; chỉ khi BrSE xác nhận rõ ràng (gõ "OK") AI mới soạn draft **tiếng Nhật** — để KH có thể reply nhanh và development có thể tiếp tục ngay sau khi nhận reply.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — No-Lens is a valid choice (Task_Lens_Spec §3.2/§9). -->
- Lens: No-Lens
- Reason: Drafting a short, block-first chat to confirm a few already-confirmed open points and unblock dev quickly. The inputs (grouped open points + confirmed understandings) are pre-assembled by the PLAN/brief; forcing a doc-type lens adds overhead without improving a 3–5 point confirmation message.
- Search/execution effect: Read from intent + the grouped open points; no preset doc-type prioritisation forced (zero overhead).
- Expansion allowed: yes — open the specific source doc only if a point needs evidence before sending.

---

## Execution Scope

### In Scope
- ISMS Check: AI kiểm tra input có PII không, tự ẩn danh nếu cần
- Output Input Understandings (tiếng Việt) với type header + 5 thành phần để BrSE review
- Gate bắt buộc: BrSE confirm Input Understandings (gõ "OK") trước khi AI soạn tiếng Nhật
- Confirm scope các điểm sẽ hỏi trong chat lần này (block-first, tối đa 3–5 điểm)
- Soạn draft chat **tiếng Nhật** — ngắn gọn, grouped, mỗi điểm có expected answer type rõ, dùng placeholder `[お客様名]` / `[会社名]`
- Self-review draft bằng Review Viewpoint 9 tiêu chí (mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, gồm check tự nhiên-vs-"AI copy template")
- BrSE finalization: ① review toàn bộ → ② điền placeholder `[お客様名]` / `[会社名]` ngoài AI → ③ gửi
- Gửi chat và log (ngày gửi, channel, điểm đã hỏi)
- Track reply và phân loại response (confirmed / pending / need-more-info)
- Update downstream artifacts theo reply; ghi nhận ISMS

### Out of Scope
- Không dùng khi danh sách điểm cần confirm vẫn unstable hoặc đang thay đổi nhiều
- Không dùng khi BrSE chưa confirm input understandings
- Không dùng khi chưa rõ chat channel / receiver chính thức
- Không dùng khi nội dung cần xác nhận mang tính formal / contractual → dùng Mail EXEC thay thế
- Không soạn tiếng Nhật trước khi BrSE xác nhận Input Understandings
- Không điền tên thật KH / công ty NDA vào draft — dùng placeholder, BrSE điền ngoài AI
- Không tự interpret reply mơ hồ của KH — follow-up ngay trong thread, không tự kết luận
- Không tự expand scope khi phát sinh open point mới — capture vào open points

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Input Understandings (tiếng Việt) | Type header `📂 Loại output` + 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions) cho BrSE review | AI → BrSE |
| O-02 | Draft chat tiếng Nhật | Block-first 🔴, tối đa 3–5 điểm, dùng placeholder `[お客様名]` / `[会社名]` | AI → BrSE |
| O-03 | Chat log | Date, channel, receiver, nội dung đã gửi | AI → BrSE |
| O-04 | KH reply log | Date, classified response (confirmed / pending / need-more-info) | AI → BrSE |
| O-05 | Updated open point list | Confirmed / pending / need-more-info | AI → BrSE |
| O-06 | Updated downstream artifact | Issue / spec / design note (nếu có thay đổi) — ghi rõ "KH confirmed via chat on [date]" | AI → BrSE |
| O-07 | Tracker update | Tracker update nếu cần | AI |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu đến từ PLAN phase (đã làm rõ các điểm cần confirm và input understandings được BrSE confirm ở mức working level).
Hoặc `direct` — khi grouped open points + understandings đã confirmed trước qua BrSE brief.

### Required Inputs

| Input | Loại | Source |
|---|---|---|
| I-01 Nội dung yêu cầu / tình huống cần confirm (tiếng Việt) | Required | BrSE mô tả |
| I-02 Grouped open points (block-first) | Required | PLAN AIP hoặc BrSE brief |
| I-03 Input understandings đã confirmed (current understanding, grouped open points, expected answer types) | Required | PLAN AIP hoặc BrSE confirm |
| I-04 Chat channel / receiver | Required | BrSE / PM |
| I-05 Loại yêu cầu (bug / spec / question / deadline) | Required | BrSE xác định |
| I-06 Source documents liên quan | Required | spec / design / issue / mail thread |
| I-07 Expected answer types | Required | PLAN AIP hoặc chuẩn bị trực tiếp |
| I-08 Deadline reply từ KH | Optional | BrSE / PM |
| I-09 Tên BrSE ký cuối | Optional | BrSE cung cấp |
| I-10 Prior chat thread liên quan | Optional | Chat system |

### Workspace Preconditions
- [ ] Confirmed nội dung yêu cầu / tình huống cần confirm (tiếng Việt)
- [ ] Confirmed điểm cần confirm qua chat (từ PLAN AIP hoặc BrSE brief)
- [ ] Confirmed input understandings (current understanding, grouped open points, expected answer types)
- [ ] Chat channel / receiver đã xác định
- [ ] BrSE sẵn sàng confirm Input Understandings trước khi AI soạn tiếng Nhật
- [ ] Grouped open points đã stable, block-first đã visible
- [ ] Receiver / chat channel đã xác định chính thức

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. BrSE có quyền reject. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Nội dung yêu cầu / tình huống | `<tóm tắt tình huống cần confirm>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Grouped open points | `<tóm tắt số điểm, điểm nào block-first>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-03 Input understandings | `<current understanding + expected answer types>` | `<assumptions>` | `<gaps>` | ⬜ pending |
| I-04 Chat channel / receiver | `<channel + receiver>` | — | — | ⬜ pending |

---

## References to Read First

**Required:**
- `<path to grouped open points (I-02)>`
- `<path to confirmed input understandings (I-03)>`
- `<path to source documents liên quan (I-06)>`

**Optional:**
- `<path to prior chat thread liên quan (I-10)>`

---

## Current Risks / Constraints

- **Input có PII:** AI tự ẩn danh ngay, thông báo BrSE những gì đã thay
- **Open points quá nhiều:** Chỉ hỏi block-first trong lần này, defer phần còn lại sang lần sau hoặc sang mail
- **Nội dung formal / contractual:** Nếu điểm cần confirm mang tính formal / contractual → chuyển sang Mail EXEC, không dùng chat
- **BrSE chỉnh Input Understandings:** Cập nhật trước khi soạn tiếng Nhật, không giữ bản cũ
- **Reply mơ hồ:** Nếu KH reply mơ hồ → ghi là "need clarification", không tự interpret, follow-up ngay trong thread
- **KH không reply:** Nếu KH không reply trong ngày → log vào pending, báo BrSE cân nhắc escalate qua mail
- **Confirm một phần:** Nếu KH confirm một phần → ghi rõ confirmed phần nào, pending phần nào, không gộp chung
- **Open point mới phát sinh qua chat:** Capture vào open points, không tự expand scope

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ open point nào (điểm KH chưa confirm, reply mơ hồ, defer sang mail) vào file trên. Open point blocking → confirm với BrSE trước khi tiếp.

---

## Workspace Execution Rule

All runtime state (drafts, chat log, reply classification, open points) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
<!-- Gate U1 — Universal. Bắt buộc cho MỌI task substantive. Skip chỉ khi BrSE explicit ủy quyền (ghi ủy quyền vào workspace findings). -->

Objective:
Xác nhận: điểm nào sẽ hỏi trong chat lần này, chat channel / receiver, expected answer types, mức impact (có cần BrSE approve trước khi gửi không), Done definition. Dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1

Inputs:
- I-01 Nội dung yêu cầu / tình huống cần confirm (tiếng Việt)
- I-02 Grouped open points (overview)
- I-03 Input understandings đã confirmed (overview)
- I-04 Chat channel / receiver

Expected Outputs:
- Xác nhận scope điểm sẽ hỏi, channel/receiver, expected answer types, mức impact
- BrSE confirmation

Done Condition:
BrSE explicit confirm ý hiểu (hoặc explicit ủy quyền skip gate). Inputs đủ để proceed.

Notes / Constraints:
- Không làm gì khác ngoài clarify/confirm ở step này.
- Nếu danh sách điểm cần confirm vẫn unstable / BrSE chưa confirm understandings / chưa rõ channel-receiver → STOP, yêu cầu BrSE làm rõ trước.
- Nếu nội dung mang tính formal / contractual → STOP, chuyển sang Mail EXEC thay vì chat.
- Nếu BrSE chỉnh hiểu biết → update note rồi re-confirm trước khi sang STEP-01.

Workspace Actions:
- Write task understanding → `00_task_brief.md`
- Log BrSE confirmation

---

### Step: STEP-01 — ISMS Check + Thu thập thông tin
<!-- OLD Bước 1 — ISMS Check + PII auto-anonymize + gather missing info trong 1 tin. -->

Objective:
AI kiểm tra input có PII không, tự ẩn danh nếu cần, và hỏi thông tin còn thiếu (loại yêu cầu, deadline, người ký) gộp trong 1 tin duy nhất.

Recommended Mode:
Clarifying

Applicable Guidelines:
- VJP-ISMS-AI-FO001 Điều 3.3 (chat soạn với hỗ trợ AI)

Inputs:
- I-01 Nội dung yêu cầu / tình huống cần confirm (tiếng Việt)
- I-05 Loại yêu cầu (bug / spec / question / deadline)
- I-08 Deadline reply từ KH (nếu có)
- I-09 Tên BrSE ký cuối (nếu có)

Expected Outputs:
- Input đã qua ISMS check (PII đã ẩn danh nếu cần) + thông tin còn thiếu đã thu thập

Done Condition:
ISMS check xong; input không còn PII chưa ẩn danh; loại yêu cầu / deadline / người ký đã rõ.

Notes / Constraints:
- Input có PII → AI tự ẩn danh ngay, thông báo BrSE những gì đã thay.
- Thiếu thông tin (kênh / loại / deadline) → hỏi tất cả trong 1 tin, không hỏi lần lượt.

Workspace Actions:
- Write ISMS check result + thông tin đã thu thập → `04_findings.md`
- Log những gì đã ẩn danh → `04_findings.md`

---

### Step: STEP-02 — Output Input Understandings (tiếng Việt)
<!-- OLD Bước 2 — IU tiếng Việt: type header 📂 + 5 thành phần để BrSE review. -->

Objective:
AI trình bày lại những gì đã hiểu: header loại + 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions) bằng tiếng Việt để BrSE dễ review và chỉnh.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- I-02 Grouped open points
- I-03 Input understandings đã confirmed
- I-07 Expected answer types

Expected Outputs:
- O-01 Input Understandings (tiếng Việt) với type header + 5 thành phần

Done Condition:
Hiển thị `📂 Loại output: [bug / spec / question / deadline]` ở đầu block; có đủ 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions); open points đã phân loại block-first; không có tên thật KH / công ty NDA trong phần này.

Notes / Constraints:
- Hiển thị `📂 Loại output: [bug / spec / question / deadline]` ở đầu block.
- Có đủ 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions).
- Open points đã phân loại block-first chưa.
- Không có tên thật KH / công ty NDA trong phần này.

Workspace Actions:
- Write Input Understandings (tiếng Việt) → `07_output_draft.md`

---

### Step: STEP-03 — Gate: BrSE confirm Input Understandings ("OK")
<!-- OLD Gate bắt buộc — HARD gate giữa bước làm rõ tiếng Việt và bước soạn tiếng Nhật. -->

Objective:
Gate bắt buộc: AI không soạn tiếng Nhật cho đến khi BrSE xác nhận rõ ràng (gõ "OK" hoặc tương đương). BrSE có thể sửa Input Understandings ở bước này mà không ảnh hưởng gì đến bước sau.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- O-01 Input Understandings (tiếng Việt) (STEP-02)

Expected Outputs:
- BrSE-confirmed Input Understandings (gõ "OK") — gate mở để sang STEP-04

Done Condition:
BrSE xác nhận Input Understandings bằng cách gõ "OK" (hoặc tương đương). Trước khi có "OK" → KHÔNG soạn tiếng Nhật.

Notes / Constraints:
- HARD gate: AI không soạn tiếng Nhật cho đến khi BrSE confirm rõ ràng (gõ "OK").
- BrSE chỉnh Input Understandings ở bước này → cập nhật trước khi soạn tiếng Nhật, không giữ bản cũ.

Workspace Actions:
- Log BrSE "OK" (hoặc bản Input Understandings đã chỉnh) → `04_findings.md`

---

### Step: STEP-04 — Soạn draft tiếng Nhật
<!-- OLD Bước 3 — JP draft, block-first 🔴, tối đa 3–5 điểm, placeholder. -->

Objective:
Dựa hoàn toàn vào Input Understandings đã confirmed — không tự thêm điểm mới. Ưu tiên điểm 🔴 BLOCK trước, tối đa 3–5 điểm, dùng placeholder `[お客様名]` / `[会社名]`.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- BrSE-confirmed Input Understandings (STEP-03)
- I-06 Source documents liên quan
- I-07 Expected answer types

Expected Outputs:
- O-02 Draft chat tiếng Nhật (block-first, placeholder)

Done Condition:
Draft tiếng Nhật soạn dựa trên Input Understandings đã confirmed (không tự thêm điểm mới); ưu tiên điểm 🔴 BLOCK trước; tối đa 3–5 điểm; dùng placeholder `[お客様名]` / `[会社名]` (không điền tên thật).

Notes / Constraints:
- Soạn dựa trên Input Understandings đã confirmed — không tự thêm điểm mới.
- Áp dụng điều chỉnh theo loại yêu cầu (mở đầu, cấu trúc) — xem skill `/aiws-util-mail-confirm` phần "Điều chỉnh theo loại".
- Ưu tiên điểm 🔴 BLOCK trước.
- Tối đa 3–5 điểm — defer phần còn lại vào Downstream note.
- Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật.
- Mở source doc cụ thể chỉ khi một điểm cần evidence trước khi gửi (Expansion allowed: yes).

Workspace Actions:
- Write draft tiếng Nhật → `07_output_draft.md`
- Log deferred điểm → `05_open_questions.md`

---

### Step: STEP-05 — Review Viewpoint (9 tiêu chí)
<!-- OLD Bước 4 — Review Viewpoint 9 criteria, mỗi cái kèm nhận xét → [...]. -->

Objective:
Kiểm từng tiêu chí, ghi nhận xét ngắn `→ [...]` cho mỗi cái — không chỉ tick ✅/❌. Đặc biệt chú ý: câu văn có tự nhiên không, nghe như người viết hay như AI copy template?

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- O-02 Draft chat tiếng Nhật (STEP-04)

Expected Outputs:
- Reviewed draft — 9 tiêu chí, mỗi tiêu chí kèm nhận xét ngắn `→ [...]`

Review Viewpoint checklist (mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, không chỉ tick ✅/❌):
- [ ] 1. Soạn dựa trên Input Understandings đã confirmed — không tự thêm điểm mới
- [ ] 2. Ưu tiên điểm 🔴 BLOCK trước
- [ ] 3. Tối đa 3–5 điểm — phần còn lại đã defer vào Downstream note
- [ ] 4. Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật
- [ ] 5. Mỗi điểm có expected answer type rõ
- [ ] 6. Câu văn có tự nhiên không — nghe như người viết, không phải AI copy template
- [ ] 7. Không có câu quá dài, quá nhiều bullet không cần thiết
- [ ] 8. Tone chat phù hợp (tự nhiên, lịch sự vừa phải) — không quá formal như mail
- [ ] 9. Keigo đúng mức, ngày tháng / hướng xử lý chính xác

Done Condition:
Mỗi tiêu chí trong 9 tiêu chí đã có nhận xét ngắn `→ [...]` (không chỉ tick ✅/❌); đã đánh giá câu văn tự nhiên-vs-"AI copy template".

Notes / Constraints:
- Mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, không chỉ tick ✅/❌.
- Câu văn có tự nhiên không — nghe như người viết, không phải AI copy template.
- Không có câu quá dài, quá nhiều bullet không cần thiết.
- Tone chat phù hợp (tự nhiên, lịch sự vừa phải) — không quá formal như mail.
- Nếu có ❌ → phải tự chỉnh trước khi output (xử lý ở STEP-06).

Workspace Actions:
- Write Review Viewpoint notes (9 tiêu chí + nhận xét) → `04_findings.md`

---

### Step: STEP-06 — Tự chỉnh nếu cần
<!-- OLD Bước 5 — self-fix nếu Review Viewpoint có ❌. -->

Objective:
Nếu Review Viewpoint có ❌ → tự chỉnh trước khi output, giải thích ngắn điểm đã sửa.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Reviewed draft + Review Viewpoint notes (STEP-05)

Expected Outputs:
- Draft tiếng Nhật đã tự chỉnh (nếu cần) + giải thích ngắn điểm đã sửa

Done Condition:
Review Viewpoint không còn ❌ (đã chỉnh những điểm ❌); mỗi điểm đã sửa có giải thích ngắn.

Notes / Constraints:
- Nếu Review Viewpoint có ❌ → bắt buộc tự chỉnh trước khi output bản cuối.
- Giải thích ngắn điểm đã sửa.

Workspace Actions:
- Update draft → `07_output_draft.md`
- Write giải thích điểm đã sửa → `04_findings.md`

---

### Step: STEP-07 — Output draft cuối + BrSE finalization
<!-- OLD Bước 6 — output final có placeholder; BrSE finalization order ①②③. -->

Objective:
Bản chat hoàn chỉnh có placeholder. BrSE làm theo thứ tự: ① review toàn bộ nội dung → ② điền placeholder ngoài AI → ③ gửi.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Draft tiếng Nhật đã tự chỉnh (STEP-06)
- I-04 Chat channel / receiver

Expected Outputs:
- O-03 Chat log (sau khi BrSE gửi)

Done Condition:
Bản chat cuối có placeholder đã output. BrSE đã thực hiện: ① review toàn bộ nội dung → ② điền placeholder `[お客様名]` / `[会社名]` ngoài AI → ③ gửi. Chat đã gửi; log ngày gửi, channel, điểm đã hỏi.

Notes / Constraints:
- 🔴 Thứ tự finalization (BrSE — bắt buộc):
  1. Review toàn bộ nội dung: keigo đúng mức, ngày tháng, hướng xử lý chính xác, AI không thêm thông tin không có trong input
  2. Điền placeholder ngoài AI: copy ra chat tool, thay `[お客様名]` / `[会社名]` bằng tên thật
  3. Gửi sau khi đã review và điền đầy đủ
- AI không điền tên thật — placeholder do BrSE điền ngoài AI.

Workspace Actions:
- Write bản chat cuối (có placeholder) → `07_output_draft.md`
- Write chat log (date, channel, receiver, nội dung đã gửi) → `04_findings.md`

---

### Step: STEP-08 — Track reply và phân loại response
<!-- OLD Bước 7 (track reply phần) — phân loại confirmed / pending / need-more-info. -->

Objective:
Theo dõi reply của KH và phân loại từng điểm: confirmed / pending / need-more-info.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- KH reply

Expected Outputs:
- O-04 KH reply log — Classified: confirmed / pending / need-more-info
- O-05 Updated open point list

Done Condition:
Mỗi điểm KH trả lời đã được phân loại rõ; không tự interpret — ghi rõ KH trả lời gì.

Notes / Constraints:
- Không tự interpret — ghi rõ KH trả lời gì.
- Nếu KH reply mơ hồ → ghi là "need clarification", không tự interpret, follow-up ngay trong thread.
- Nếu KH không reply trong ngày → log vào pending, báo BrSE cân nhắc escalate qua mail.
- Nếu KH confirm một phần → ghi rõ confirmed phần nào, pending phần nào, không gộp chung.
- Nếu có open point mới phát sinh qua chat → capture vào open points, không tự expand scope.

Workspace Actions:
- Write KH reply log (date, classified response) → `04_findings.md`
- Update open point list (confirmed / pending / need-more-info) → `05_open_questions.md`

---

### Step: STEP-09 — Update downstream artifacts + ghi nhận ISMS
<!-- OLD Bước 7 (downstream + ISMS recording phần). -->

Objective:
Cập nhật downstream artifacts (issue / spec / design note) theo classified response; gợi ý bước tiếp theo; ghi nhận ISMS. Nếu KH không reply → cân nhắc escalate qua mail.

Recommended Mode:
Executing

Applicable Guidelines:
- VJP-ISMS-AI-FO001 Điều 3.3 (chat soạn với hỗ trợ AI)

Inputs:
- Classified response (STEP-08)

Expected Outputs:
- O-06 Updated issue / spec / design note
- O-07 Tracker update (nếu cần)

Done Condition:
Downstream artifacts đã update theo reply; mỗi update ghi rõ "KH confirmed via chat on [date]". Tracker update nếu cần. ISMS đã ghi nhận.

Notes / Constraints:
- Ghi rõ "KH confirmed via chat on [date]" cho mỗi update.
- Source của mỗi update phải ghi rõ; pending / open items còn lại phải visible.
- 📋 ISMS ghi nhận (VJP-ISMS-AI-FO001 Điều 3.3): Chat này được soạn với hỗ trợ AI. Nếu trích dẫn trong tài liệu chính thức gửi ra ngoài → ghi chú theo quy định VTI.
- Nếu KH không reply → cân nhắc escalate qua mail.

Workspace Actions:
- Update downstream artifact (issue / spec / design note)
- Tracker update nếu cần
- Move final → `11_output_final/`

---

## Done Criteria

- [ ] Input Understandings đã được BrSE confirm trước khi soạn tiếng Nhật
- [ ] Draft tiếng Nhật đã qua Review Viewpoint (tất cả ✅ hoặc đã chỉnh những điểm ❌)
- [ ] Chat đã gửi và có log ngày gửi + channel
- [ ] KH reply đã được phân loại rõ: confirmed / pending / need-more-info
- [ ] Downstream artifacts đã update theo reply (hoặc pending list đã rõ nếu chưa có reply); downstream note đã ghi gợi ý bước tiếp theo
- [ ] Open points còn lại đã được defer sang lần chat tiếp hoặc chuyển sang mail nếu cần formal confirm
- [ ] **Gate U1** confirmed — evidence trong workspace
- [ ] **Gate U2** Input Understanding đã ghi (hoặc task không có input)
- [ ] **Gate U3** Mọi open point trong `05_open_questions.md` đã resolved / deferred / rejected với conclusion rõ ràng

## Self-check / Review Points

**Khi output Input Understandings (STEP-02):**
- Hiển thị `📂 Loại output: [bug / spec / question / deadline]` ở đầu block
- Có đủ 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions)
- Open points đã phân loại block-first chưa
- Không có tên thật KH / công ty NDA trong phần này

**Khi soạn draft tiếng Nhật (STEP-04):**
- Soạn dựa trên Input Understandings đã confirmed — không tự thêm điểm mới
- Áp dụng điều chỉnh theo loại yêu cầu (mở đầu, cấu trúc) — xem skill `/aiws-util-mail-confirm` phần "Điều chỉnh theo loại"
- Ưu tiên điểm 🔴 BLOCK trước
- Tối đa 3–5 điểm — defer phần còn lại vào Downstream note
- Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật

**Khi Review Viewpoint (STEP-05):**
- Mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, không chỉ tick ✅/❌
- Câu văn có tự nhiên không — nghe như người viết, không phải AI copy template
- Không có câu quá dài, quá nhiều bullet không cần thiết
- Tone chat phù hợp (tự nhiên, lịch sự vừa phải) — không quá formal như mail
- Nếu có ❌ → phải tự chỉnh trước khi output

**Khi nhận reply:**
- Đang phân loại đúng từng điểm KH trả lời (confirmed / pending)
- Không tự interpret những điểm KH trả lời mơ hồ — follow-up ngay trong thread
- Downstream impact của reply đã được capture chưa

**Trước khi update artifacts:**
- Source của mỗi update có ghi rõ "KH confirmed via chat on [date]" không
- Pending / open items còn lại có visible không

## Finalization Notes

**Sample execution note** — ví dụ: unblock 2 điểm về tính năng export báo cáo.

- STEP-01: ISMS OK (không có PII). Kênh: Chat, Loại: question, Deadline: hôm nay, Người ký: không cần.
- STEP-02 (tiếng Việt — chờ BrSE OK):
  ```
  【INPUT UNDERSTANDINGS】
  📋 Summary: Export báo cáo đang bị block do chưa rõ format file và phân quyền theo role.
  ❓ Open Points:
     · 🔴 [BLOCK] Format export: PDF hay CSV?
     · 🔴 [BLOCK] Quyền truy cập: theo role hay tất cả user?
  🎯 Expected Answer Types: lựa chọn cụ thể (PDF/CSV; role/all)
  ⚠️  Downstream: chưa rõ 2 điểm → không thể implement
  💡 Assumptions: không có
  ```
  → **BrSE gõ "OK"** → sang STEP-04
- STEP-04 (tiếng Nhật — sau khi đã có OK):
  ```
  お世話になっております。レポートエクスポート機能の開発を進めるにあたり、
  2点確認させてください。

  ①エクスポート形式はPDFとCSV、どちらをご希望でしょうか。
  ②アクセス権限はロール別での制御を想定しておりますが、ご認識と相違ございませんでしょうか。

  ご回答いただき次第、実装を進めてまいります。よろしくお願いいたします。
  ```
- STEP-05: Review Viewpoint — ✅ tự nhiên / ✅ 2 điểm rõ / ✅ tone OK / ✅ không AI-like
- STEP-07: Gửi chat, log 2026-05-27, channel Chatwork
- STEP-08: KH reply — (1) PDF; (2) theo role. Update issue: "confirmed via Chatwork 2026-05-27: format=PDF, access=by-role"

## Re-plan Rule

Append Re-plan Log entry khi:
- Danh sách điểm cần confirm thay đổi macro scope sau STEP-00
- Nội dung chuyển từ chat sang formal / mail (đổi kênh, đổi expected output)
- Open points phát sinh làm thay đổi expected output

Không silently drift — tạo explicit re-plan entry và ghi evidence ref vào workspace findings/capture trước khi chỉnh AIP.

## Re-plan Log

<!-- Append entry on scope/objective/output change. Format: ### YYYY-MM-DD — title / Trigger / Change / Evidence ref / Approved by. -->

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- PLAN AIP (hoặc tương đương) đã làm rõ các điểm cần confirm và input understandings đã được BrSE confirm ở mức working level
- Grouped open points đã visible, receiver / chat channel đã xác định
- Cần reply nhanh hoặc unblock development ngay — chat phù hợp hơn mail
- Nội dung không cần formal / contractual
- Task chuyển từ giai đoạn **"làm rõ"** sang giai đoạn **"soạn và gửi chat"**

**Khi KHÔNG dùng file này:**
- Danh sách điểm cần confirm vẫn unstable hoặc đang thay đổi nhiều
- BrSE chưa confirm input understandings
- Chưa rõ chat channel / receiver chính thức
- Nội dung cần xác nhận mang tính formal / contractual → dùng Mail EXEC thay thế

---

## Skill Mapping

**Mapped Skill:** `/aiws-util-mail-confirm` — xử lý cả chat và email trong cùng một flow.

| Bước trong file này | Bước trong skill |
|---|---|
| STEP-01 — ISMS Check + thu thập | Bước 1 — Kiểm tra ISMS & Thu thập |
| STEP-02 — Input Understandings (VN) | Bước 2 — Output Input Understandings |
| STEP-03 — Gate: BrSE "OK" | Bước 3 — BrSE confirms |
| STEP-04 — Draft tiếng Nhật | Bước 4 — Draft email/chat |
| STEP-05 — Review Viewpoint | Bước 5 — Create Review Viewpoint |
| STEP-06 — Tự chỉnh | Bước 6 — Self Review |
| STEP-07 — Output draft cuối | Bước 7 — Finalize output |
| STEP-08 / STEP-09 — Track reply & downstream note | Bước 8 — Track reply & downstream note |

---

## Changelog

<!-- Provenance carried over from the legacy numbered-prose preset (migrated to current AIP_EXEC structure 2026-06-20). -->

- **migrated_from:** legacy preset `AIP_EXEC_CreateChatConfirmRequirement.md` v2.0 (2026-05-27), AIP Type: EXEC AIP, Mapped Skill: `/aiws-util-mail-confirm`, Mapped PLAN Sample: `AIP_Sample_CreateChatConfirmRequirement.md`. Original purpose: "Hướng dẫn thực thi từng bước cho task **Soạn chat confirm yêu cầu với KH** — tách biệt bước làm rõ tiếng Việt và bước soạn tiếng Nhật để dễ chỉnh sửa từng phần".
- **PLAN-to-EXEC trace (legacy §11):**
  - Linked PLAN AIP: `AIP_Sample_CreateChatConfirmRequirement.md`
  - Outputs inherited from PLAN: grouped open points (block-first) đã confirmed; expected answer types cho từng điểm; chat channel / receiver đã xác định; approved tone direction
  - Entry conditions verified: grouped open points đã stable, block-first đã xác định; chat channel / receiver đã rõ; BrSE đã confirm input understandings
- **2026-06-20** — Re-authored legacy numbered-prose format (§1–§11) into the current AIP_EXEC structure (frontmatter + `## Execution Steps` with STEP-00 HARD GATE). Reinstated the two-language design (VN clarify → BrSE "OK" gate → JP draft), ISMS PII auto-anonymize, 5-component Vietnamese Input Understandings, 9-criterion Review Viewpoint, BrSE finalization order ①②③, ISMS recording note, and `/aiws-util-mail-confirm` 8-row step mapping. All documented intent preserved; no procedure redesign.
