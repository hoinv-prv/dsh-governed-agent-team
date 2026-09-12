---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-create-mail-confirm-requirement
title: Create Mail to Confirm Requirements with Customer
status: draft
project: <project-name>
owner: <owner>
plan_source: "<AIP-PLAN-NNN or direct — when grouped open points and input understandings are already confirmed>"
mapped_skill: /aiws-util-mail-confirm
updated_at: 2026-06-20
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Create Mail to Confirm Requirements with Customer

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Soạn mail confirm với KH Nhật — có cấu trúc, tự nhiên, không nghe như AI viết — bằng cách tách rõ bước làm rõ tiếng Việt (BrSE xác nhận) và bước soạn tiếng Nhật (dễ chỉnh từng phần độc lập). Mail confirm yêu cầu với KH chính thức, đầy đủ — để KH có thể reply rõ ràng theo từng điểm và downstream artifacts có thể được update ngay sau khi nhận reply.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: requirement_understanding
- Reason: Drafting a FORMAL mail to confirm requirements — each grouped open point references its source spec/design so the question is evidence-grounded and answerable per point.
- Search/execution effect: Prioritises `requirement_definition`, `meeting_note`, `basic_design` (the source docs behind each open point) when ordering the reading surface.
- Expansion allowed: yes — open the specific source doc when a point needs an exact quote/reference before sending.

## Execution Scope

### In Scope

Dùng file này khi:
- PLAN AIP (hoặc tương đương) đã làm rõ các điểm cần confirm và input understandings đã được BrSE confirm ở mức working level
- grouped open points đã visible, receiver / KH contact đã xác định
- cần xác nhận chính thức qua mail (formal, contractual, hoặc cần có evidence bằng văn bản)
- nội dung phức tạp, nhiều điểm cần giải thích — mail phù hợp hơn chat
- task chuyển từ giai đoạn **"làm rõ / chuẩn bị"** sang giai đoạn **"soạn và gửi mail"**

Trong scope thực thi:
- Confirm scope điểm sẽ cover trong mail lần này
- Xác định subject line và cấu trúc mail
- Soạn draft mail grouped, có cấu trúc, mỗi điểm có expected answer type
- Tạo review viewpoint và self-review draft
- BrSE review và approve trước khi gửi
- Gửi mail và log evidence
- Track reply và phân loại response
- Update downstream artifacts theo reply

### Out of Scope

Không dùng file này khi:
- danh sách điểm cần confirm vẫn unstable hoặc đang thay đổi nhiều
- BrSE chưa confirm input understandings
- chưa rõ receiver / KH contact chính thức
- chưa chốt được tone / language policy / subject format
- nội dung chỉ cần unblock nhanh (1–3 điểm đơn giản) → dùng Chat EXEC thay thế

Ngoài scope thực thi:
- Không tự interpret những điểm KH trả lời mơ hồ — ghi là "need clarification"
- Không tự điều chỉnh spec / design khi KH reject một yêu cầu → escalate lên BrSE / PM trước
- Không tự expand scope khi open point mới phát sinh trong lúc soạn → capture vào open points

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Sent mail log | date, receiver, subject, expected reply date | AI → BrSE |
| O-02 | KH reply log | date, classified response | AI → BrSE |
| O-03 | Updated open point list | confirmed / rejected / pending / need-more-info | AI → BrSE action |
| O-04 | Updated downstream artifact | spec / design / issue (nếu có thay đổi) | AI → BrSE review |
| O-05 | Action item list | nếu có follow-up cần làm | AI → BrSE |
| O-06 | Tracker / project report update | nếu cần | AI → BrSE |

---

## Execution Input Package

### Plan Source
Điền `<AIP-PLAN-NNN>` nếu đến từ PLAN phase.
Hoặc `direct` — khi grouped open points và input understandings đã confirmed trước, không cần PLAN phase.

### Required Inputs

| Input | Loại | Source |
|---|---|---|
| I-01 Grouped open points (phân loại theo topic) | Required | PLAN AIP hoặc BrSE brief |
| I-02 Input understandings đã confirmed | Required | PLAN AIP hoặc BrSE confirm |
| I-03 Receiver / KH contact | Required | BrSE / PM |
| I-04 Loại yêu cầu (bug / spec / question / deadline) | Required | BrSE xác định |
| I-05 Language policy | Required | BrSE (default: Japanese) |
| I-06 Subject line format | Required | BrSE / project convention |
| I-07 Source documents (spec / design / prior mail thread) | Required | Project artifact |
| I-08 Expected reply deadline | Required | BrSE / PM |
| I-09 Tên BrSE/Comtor ký cuối mail | Optional | BrSE cung cấp |
| I-10 Current assumptions nếu chưa có reply | Optional | PLAN AIP |

> Input understandings (I-02) bao gồm: current understanding, grouped open points, expected answer types, downstream impact, current assumptions.

### Workspace Preconditions
- [ ] grouped open points đã stable
- [ ] receiver / KH contact đã xác định
- [ ] loại yêu cầu (bug / spec / question / deadline) đã xác định
- [ ] language policy đã rõ (hỏi BrSE nếu chưa có)
- [ ] subject line format đã rõ (hỏi BrSE về convention)
- [ ] BrSE đã confirm input understandings
- [ ] confirmed yêu cầu / change request cần confirm chính thức từ PLAN AIP hoặc BrSE brief

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. -->

| Input | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Grouped open points | `<số điểm, phân loại theo topic>` | `<assumptions>` | `<điểm chưa rõ>` | ⬜ pending |
| I-02 Input understandings | `<current understanding, expected answer types>` | `<assumptions>` | `<gaps>` | ⬜ pending |
| I-03 Receiver / KH contact | `<receiver xác định>` | — | — | ⬜ pending |
| I-04 Loại yêu cầu | `<bug / spec / question / deadline>` | — | — | ⬜ pending |

---

## References to Read First

**Required:**
- `<path to grouped open points (I-01)>`
- `<path to source documents — spec / design / prior mail thread (I-07)>`

**Optional:**
- `<path to language policy / subject convention (I-05, I-06)>`
- `<path to current assumptions (I-10)>`

---

## Current Risks / Constraints

- **PII / ISMS:** Input có thể chứa tên thật KH / công ty NDA → AI tự ẩn danh ngay, thông báo BrSE những gì đã thay; không để tên thật lọt vào Input Understandings hay draft
- **Unstable open points:** danh sách điểm cần confirm còn thay đổi → quay lại PLAN / clarify trước, không gửi mail
- **Receiver chưa rõ:** chưa xác định receiver / KH contact chính thức → block, hỏi BrSE / PM
- **Tone / language policy:** chưa chốt language policy / subject format → hỏi BrSE về convention trước khi soạn
- **No reply risk:** Nếu KH không reply trong thời gian mong đợi → ghi vào risk/pending list, báo BrSE, cân nhắc remind qua chat
- **Customization note:** Template này là generic baseline — dự án customize subject convention, tone, và downstream artifact list theo nhu cầu

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ open point nào (điểm KH trả lời mơ hồ, point mới phát sinh khi soạn, KH reject / pending) vào file trên. Open point blocking → confirm với BrSE trước khi tiếp.

---

## Workspace Execution Rule

All runtime state (drafts, mail logs, reply classification, findings, open points) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)

Objective:
Xác nhận: scope điểm cần confirm, receiver / KH contact, loại yêu cầu (bug / spec / question / deadline), language policy, subject convention, expected reply deadline, người ký cuối mail, và rằng input understandings đã được BrSE confirm. Dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1

Inputs:
- I-01 Grouped open points (overview)
- I-02 Input understandings đã confirmed
- I-03 Receiver / KH contact
- I-04 Loại yêu cầu (bug / spec / question / deadline)

Expected Outputs:
- Xác nhận scope, receiver, loại yêu cầu, language policy, subject convention, deadline, người ký
- BrSE confirmation

Done Condition:
BrSE explicit confirm AI hiểu đúng scope và inputs (hoặc explicit ủy quyền skip gate). Entry conditions verified: grouped open points stable, receiver xác định, loại yêu cầu xác định, language policy rõ, subject format rõ, BrSE đã confirm input understandings.

Notes / Constraints:
- Nếu PLAN AIP chưa có hoặc understandings chưa confirmed → quay lại PLAN / clarify trước
- Nếu chưa rõ language policy / subject convention → hỏi BrSE trước khi tiếp
- Không làm gì khác ngoài clarify/confirm ở step này

Workspace Actions:
- Log confirmed scope, receiver, loại yêu cầu, language policy, subject convention, người ký → `00_task_brief.md`
- Log BrSE confirmation

---

### Step: STEP-01 — ISMS Check + Thu thập thông tin

Objective:
AI kiểm tra input có PII không, tự ẩn danh nếu cần, và hỏi thông tin còn thiếu (loại yêu cầu, deadline, người ký) gộp trong 1 tin duy nhất.

Recommended Mode:
Clarifying

Applicable Guidelines:
- VJP-ISMS-AI-FO001 Điều 3.3

Inputs:
- I-04 Loại yêu cầu (bug / spec / question / deadline)
- I-08 Expected reply deadline
- I-09 Tên BrSE/Comtor ký cuối mail

Expected Outputs:
- Input đã được kiểm PII và ẩn danh nếu cần (thông báo BrSE những gì đã thay)
- Thông tin còn thiếu (loại yêu cầu, deadline, người ký) đã thu thập trong 1 tin duy nhất

Done Condition:
Input đã được kiểm PII; nếu có PII → AI tự ẩn danh ngay và thông báo BrSE; loại yêu cầu, deadline, người ký đã đủ.

Notes / Constraints:
- Input có PII → AI tự ẩn danh ngay, thông báo BrSE những gì đã thay
- Thiếu thông tin (receiver / loại / deadline) → hỏi tất cả trong 1 tin, không hỏi lần lượt

Workspace Actions:
- Log kết quả ISMS check + những gì đã ẩn danh → `04_findings.md`
- Log thông tin thu thập (loại yêu cầu, deadline, người ký) → `00_task_brief.md`

---

### Step: STEP-02 — Output Input Understandings (tiếng Việt)

Objective:
AI trình bày lại những gì đã hiểu: header loại + 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions) bằng tiếng Việt để BrSE dễ review và chỉnh. Đây là bước làm rõ tiếng Việt — tách biệt với bước soạn tiếng Nhật để dễ chỉnh từng phần.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- I-01 Grouped open points
- I-02 Input understandings đã confirmed
- I-04 Loại yêu cầu (bug / spec / question / deadline)

Expected Outputs:
- Block Input Understandings (tiếng Việt) với header loại + 5 thành phần

Self-check (khi output Input Understandings):
- [ ] Hiển thị `📂 Loại output: [bug / spec / question / deadline]` ở đầu block
- [ ] Có đủ 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions)
- [ ] Open points đã phân loại block-first chưa
- [ ] Không có tên thật KH / công ty NDA trong phần này

Done Condition:
Input Understandings đã output bằng tiếng Việt với header loại + đủ 5 thành phần, open points phân loại block-first, không có tên thật KH / công ty NDA. BrSE confirm ở STEP-03 trước khi soạn tiếng Nhật.

Notes / Constraints:
- BrSE có thể sửa Input Understandings ở bước này mà không ảnh hưởng gì đến bước sau
- BrSE chỉnh Input Understandings ở bước này → cập nhật trước khi soạn tiếng Nhật, không giữ bản cũ

Workspace Actions:
- Write Input Understandings block (tiếng Việt) → `07_output_draft.md`

---

### Step: STEP-03 — Gate: BrSE confirm "OK"

Objective:
Gate bắt buộc: AI không soạn tiếng Nhật cho đến khi BrSE xác nhận rõ ràng (gõ "OK" hoặc tương đương). BrSE có thể sửa Input Understandings ở bước trước mà không ảnh hưởng gì đến bước sau.

Recommended Mode:
Clarifying

Applicable Guidelines:
_(none)_

Inputs:
- Input Understandings block (STEP-02)

Expected Outputs:
- BrSE explicit "OK" (hoặc tương đương) trên Input Understandings

Done Condition:
BrSE gõ "OK" (hoặc tương đương) xác nhận rõ ràng Input Understandings. AI KHÔNG được soạn tiếng Nhật trước khi có confirm này.

Notes / Constraints:
- Nếu BrSE sửa Input Understandings → cập nhật bản mới trước khi soạn tiếng Nhật, không giữ bản cũ
- Gate này tách bước làm rõ tiếng Việt khỏi bước soạn tiếng Nhật

Workspace Actions:
- Log BrSE "OK" confirmation → `04_findings.md`

---

### Step: STEP-04 — Soạn draft tiếng Nhật

Objective:
Dựa hoàn toàn vào Input Understandings đã confirmed — không tự thêm điểm mới. Subject line + cấu trúc đầy đủ; áp dụng điều chỉnh theo loại yêu cầu; dùng placeholder `[お客様名]` / `[会社名]`.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Input Understandings đã confirmed (STEP-03)
- I-04 Loại yêu cầu (bug / spec / question / deadline)
- I-07 Source documents (spec / design / prior mail thread)
- I-09 Tên BrSE/Comtor ký cuối mail

Expected Outputs:
- Draft mail tiếng Nhật: subject line + cấu trúc đầy đủ, dùng placeholder

Self-check (khi soạn draft tiếng Nhật):
- [ ] Soạn dựa trên Input Understandings đã confirmed — không tự thêm điểm mới
- [ ] Áp dụng điều chỉnh theo loại yêu cầu (mở đầu, cấu trúc) — xem skill `/aiws-util-mail-confirm` phần "Điều chỉnh theo loại"
- [ ] Subject line có rõ mục đích (【ご確認】/ 【確認依頼】/ 【ご報告】)
- [ ] Greeting / opening phù hợp KH Nhật
- [ ] Các điểm confirm đã grouped theo logic (feature / screen / flow)
- [ ] Mỗi điểm có expected answer type rõ (confirm / clarify / decide)
- [ ] Deadline reply ghi rõ nếu có
- [ ] Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật

Done Condition:
Draft tiếng Nhật soạn xong: dựa hoàn toàn vào Input Understandings đã confirmed, subject line rõ mục đích, grouped theo logic, mỗi điểm có expected answer type, dùng placeholder `[お客様名]` / `[会社名]`, áp dụng điều chỉnh theo loại yêu cầu.

Notes / Constraints:
- Không tự thêm điểm mới ngoài Input Understandings đã confirmed
- Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật (BrSE điền ngoài AI)
- Nếu open point mới phát sinh trong lúc soạn → capture vào open points, không tự expand scope

Workspace Actions:
- Write draft tiếng Nhật → `07_output_draft.md`
- Log open points → `05_open_questions.md`

---

### Step: STEP-05 — Review Viewpoint (9 tiêu chí)

Objective:
Kiểm từng tiêu chí, ghi nhận xét ngắn `→ [...]` cho mỗi cái — không chỉ tick ✅/❌. Đặc biệt chú ý: câu văn có tự nhiên không, nghe như người viết hay như AI copy template?

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Draft tiếng Nhật (STEP-04)

Expected Outputs:
- Review Viewpoint với 9 tiêu chí, mỗi tiêu chí kèm nhận xét ngắn `→ [...]`

Review Viewpoint (9 tiêu chí — mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, không chỉ tick ✅/❌):
- [ ] subject line có rõ mục đích không (【ご確認】/ 【確認依頼】/ 【ご報告】) `→ [...]`
- [ ] greeting / opening có phù hợp KH Nhật không `→ [...]`
- [ ] nội dung có đúng những gì cần confirm không `→ [...]`
- [ ] các điểm confirm có grouped theo logic (feature / screen / flow) không `→ [...]`
- [ ] mỗi điểm có expected answer type rõ ràng không (confirm / clarify / decide) `→ [...]`
- [ ] câu văn có tự nhiên không — nghe như người viết, không phải AI copy template `→ [...]`
- [ ] keigo vừa phải — không quá formal / không quá casual `→ [...]`
- [ ] không lặp lại cụm mở đầu sáo rỗng nhiều lần trong cùng 1 mail `→ [...]`
- [ ] deadline reply có ghi rõ không (nếu có) `→ [...]`

Done Condition:
Review Viewpoint đã kiểm đủ 9 tiêu chí, mỗi tiêu chí kèm nhận xét ngắn `→ [...]` (không chỉ tick ✅/❌); đặc biệt đã đánh giá câu văn có tự nhiên không, nghe như người viết hay AI copy template.

Notes / Constraints:
- Mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, không chỉ tick ✅/❌
- Câu văn có tự nhiên không — nghe như người viết, không phải AI copy template
- Không có câu quá dài, không liệt kê bullet quá nhiều khi không cần thiết
- Keigo vừa phải — không quá formal / không quá casual
- Không lặp lại cụm mở đầu sáo rỗng nhiều lần trong cùng 1 mail

Workspace Actions:
- Write Review Viewpoint (9 tiêu chí + nhận xét `→ [...]`) → `04_findings.md`

---

### Step: STEP-06 — Tự chỉnh nếu cần

Objective:
Nếu Review Viewpoint có ❌ → tự chỉnh trước khi output, giải thích ngắn điểm đã sửa.

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Review Viewpoint (STEP-05)
- Draft tiếng Nhật (STEP-04)

Expected Outputs:
- Draft đã tự chỉnh các điểm ❌ + giải thích ngắn điểm đã sửa

Done Condition:
Nếu Review Viewpoint có ❌ → đã tự chỉnh trước khi output bản cuối, có giải thích ngắn điểm đã sửa. Nếu tất cả ✅ → giữ nguyên.

Notes / Constraints:
- Review Viewpoint có ❌ → bắt buộc tự chỉnh trước khi output bản cuối

Workspace Actions:
- Update draft → `07_output_draft.md`
- Log điểm đã sửa → `04_findings.md`

---

### Step: STEP-07 — BrSE review và approve

Objective:
BrSE review nội dung draft và approve trước khi gửi KH.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Draft đã tự chỉnh (STEP-06)

Expected Outputs:
- BrSE-approved draft

Done Condition:
BrSE approve nội dung draft. Bắt buộc trước khi gửi KH.

Notes / Constraints:
- Bắt buộc trước khi gửi KH

Workspace Actions:
- Apply BrSE comments → update draft → `07_output_draft.md`

---

### Step: STEP-08 — Output draft cuối + Finalization

Objective:
Output bản mail hoàn chỉnh có placeholder. BrSE làm theo thứ tự: ① review toàn bộ nội dung → ② điền placeholder ngoài AI → ③ gửi.

Recommended Mode:
Executing

Applicable Guidelines:
_(none)_

Inputs:
- BrSE-approved draft (STEP-07)

Expected Outputs:
- Bản mail hoàn chỉnh có placeholder `[お客様名]` / `[会社名]`
- Sent mail log: date, receiver, subject, expected reply date

Done Condition:
Bản mail cuối có placeholder đã output; BrSE đã thực hiện theo thứ tự ① review → ② điền placeholder ngoài AI → ③ gửi; mail đã gửi và có log: ngày gửi, receiver, subject, expected reply date.

Notes / Constraints:
- 🔴 **Thứ tự finalization (BrSE — bắt buộc):**
  1. **Review toàn bộ nội dung:** keigo đúng mức, ngày tháng, hướng xử lý chính xác, AI không thêm thông tin không có trong input
  2. **Điền placeholder ngoài AI:** copy ra email client, thay `[お客様名]` / `[会社名]` bằng tên thật
  3. **Gửi** sau khi đã review và điền đầy đủ

Workspace Actions:
- Write bản mail cuối (có placeholder) → `07_output_draft.md`
- Write sent mail log (date, receiver, subject, expected reply date) → `04_findings.md`

---

### Step: STEP-09 — Track reply và phân loại response

Objective:
Track KH reply và phân loại response theo từng điểm: confirmed / rejected / pending / need-more-info.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- KH reply

Expected Outputs:
- Classified: confirmed / rejected / pending / need-more-info

Self-check (khi nhận reply):
- [ ] đang phân loại đúng từng điểm KH trả lời (confirmed / rejected / pending)
- [ ] không tự interpret những điểm KH trả lời mơ hồ — ghi là "need clarification"
- [ ] downstream impact của reply đã được capture chưa

Done Condition:
KH reply đã được phân loại rõ từng điểm: confirmed / rejected / pending / need-more-info. BrSE verify sau step này trước khi update artifacts.

Notes / Constraints:
- Không tự interpret — ghi rõ từng điểm KH trả lời gì
- Nếu KH reply "cần thêm thông tin" → tạo follow-up mail, ghi rõ blocker và owner
- Nếu KH reject một yêu cầu → không tự điều chỉnh spec / design, escalate lên BrSE / PM trước
- Nếu KH confirm một phần → ghi rõ confirmed phần nào, pending phần nào, không gộp chung
- Nếu KH không reply trong thời gian mong đợi → ghi vào risk/pending list, báo BrSE, cân nhắc remind qua chat
- **→ BrSE verify:** Sau step này (reply đã phân loại), BrSE xác nhận trước khi tiếp

Workspace Actions:
- Write KH reply log (date, classified response) → `04_findings.md`
- Update open point list → `05_open_questions.md`

---

### Step: STEP-10 — Update downstream artifacts + Ghi chú downstream / ISMS

Objective:
Update downstream artifacts theo classified response của KH. Ghi rõ source: "KH confirmed via mail on [date]". Gợi ý bước tiếp theo, ghi nhận ISMS, track reply. Nếu KH không reply → follow-up qua chat.

Recommended Mode:
Executing

Applicable Guidelines:
- VJP-ISMS-AI-FO001 Điều 3.3

Inputs:
- Classified response (STEP-09)

Expected Outputs:
- Updated spec / design / issue / tracker
- Updated open point list (confirmed / rejected / pending / need-more-info)
- Action item list nếu có follow-up
- Downstream note (gợi ý bước tiếp theo) + ISMS ghi nhận

Self-check (trước khi update artifacts):
- [ ] source của mỗi update có ghi rõ "KH confirmed via mail on [date]" không
- [ ] pending / open items còn lại có visible không

Done Condition:
Downstream artifacts đã update theo reply (hoặc pending list đã rõ nếu chưa có reply); mỗi update ghi rõ "KH confirmed via mail on [date]"; downstream note đã ghi gợi ý bước tiếp theo; ISMS đã ghi nhận.

Notes / Constraints:
- Ghi rõ "KH confirmed via mail on [date]"
- Pending items phải visible trong open point list
- 📋 **ISMS ghi nhận (VJP-ISMS-AI-FO001 Điều 3.3):** Mail này được soạn với hỗ trợ AI. Nếu forward hoặc trích dẫn trong tài liệu chính thức gửi ra ngoài → ghi chú theo quy định VTI.
- Nếu KH không reply → follow-up qua chat

Workspace Actions:
- Update downstream artifact (spec / design / issue / tracker)
- Update open point list → `05_open_questions.md`
- Write action item list nếu có follow-up → `04_findings.md`
- Write downstream note + ISMS ghi nhận → `04_findings.md`

---

## Step-to-Skill Mapping

**Mapped Skill:** `/aiws-util-mail-confirm` — xử lý cả chat và email trong cùng một flow.

| Step trong file này | Bước trong skill |
|---|---|
| STEP-01 — ISMS Check + Thu thập | Bước 1 — Kiểm tra ISMS & Thu thập |
| STEP-02 — Input Understandings (VN) | Bước 2 — Output Input Understandings |
| STEP-03 — Gate: BrSE "OK" | Bước 3 — BrSE confirms |
| STEP-04 — Draft tiếng Nhật | Bước 4 — Draft email/chat |
| STEP-05 — Review Viewpoint | Bước 5 — Create Review Viewpoint |
| STEP-06 — Tự chỉnh | Bước 6 — Self Review |
| STEP-08 — Output draft cuối | Bước 7 — Finalize output |
| STEP-09 / STEP-10 — Track reply & downstream note | Bước 8 — Track reply & downstream note |

---

## Done Criteria

- [ ] Input có PII đã được kiểm và tự ẩn danh; không có tên thật KH / công ty NDA trong Input Understandings hay draft
- [ ] Input Understandings (tiếng Việt) đã được BrSE confirm ("OK") trước khi soạn tiếng Nhật
- [ ] draft tiếng Nhật đã qua Review Viewpoint 9 tiêu chí (tất cả ✅ hoặc đã chỉnh những điểm ❌, mỗi tiêu chí có nhận xét `→ [...]`)
- [ ] draft đã được BrSE approve trước khi gửi
- [ ] bản mail cuối có placeholder `[お客様名]` / `[会社名]`; BrSE đã ① review → ② điền placeholder ngoài AI → ③ gửi
- [ ] mail đã gửi và có log ngày gửi + receiver + expected reply date
- [ ] KH reply đã được phân loại rõ: confirmed / rejected / pending / need-more-info
- [ ] downstream artifacts đã update theo reply (hoặc pending list đã rõ nếu chưa có reply); ISMS đã ghi nhận
- [ ] downstream note đã ghi gợi ý bước tiếp theo

## Self-check / Review Points

Checklist tự kiểm trong lúc thực thi:

**Khi output Input Understandings (STEP-02):**
- Hiển thị `📂 Loại output: [bug / spec / question / deadline]` ở đầu block
- Có đủ 5 thành phần (Summary / Open Points / Expected Answer Types / Downstream Impact / Assumptions)
- Open points đã phân loại block-first chưa
- Không có tên thật KH / công ty NDA trong phần này

**Khi soạn draft tiếng Nhật (STEP-04):**
- Soạn dựa trên Input Understandings đã confirmed — không tự thêm điểm mới
- Áp dụng điều chỉnh theo loại yêu cầu (mở đầu, cấu trúc) — xem skill `/aiws-util-mail-confirm` phần "Điều chỉnh theo loại"
- Subject line có rõ mục đích (【ご確認】/ 【確認依頼】/ 【ご報告】)
- Greeting / opening phù hợp KH Nhật
- Các điểm confirm đã grouped theo logic (feature / screen / flow)
- Mỗi điểm có expected answer type rõ (confirm / clarify / decide)
- Deadline reply ghi rõ nếu có
- Dùng placeholder `[お客様名]` / `[会社名]` — không điền tên thật

**Khi Review Viewpoint (STEP-05):**
- Mỗi tiêu chí kèm nhận xét ngắn `→ [...]`, không chỉ tick ✅/❌
- Câu văn có tự nhiên không — nghe như người viết, không phải AI copy template
- Không có câu quá dài, không liệt kê bullet quá nhiều khi không cần thiết
- Keigo vừa phải — không quá formal / không quá casual
- Không lặp lại cụm mở đầu sáo rỗng nhiều lần trong cùng 1 mail
- Nếu có ❌ → phải tự chỉnh trước khi output

**Khi nhận reply (STEP-09):**
- đang phân loại đúng từng điểm KH trả lời (confirmed / rejected / pending)
- không tự interpret những điểm KH trả lời mơ hồ — ghi là "need clarification"
- downstream impact của reply đã được capture chưa

**Trước khi update artifacts (STEP-10):**
- source của mỗi update có ghi rõ "KH confirmed via mail on [date]" không
- pending / open items còn lại có visible không

## Finalization Notes

> 📋 **ISMS ghi nhận (VJP-ISMS-AI-FO001 Điều 3.3):**
> Mail này được soạn với hỗ trợ AI. Nếu forward hoặc trích dẫn trong tài liệu chính thức gửi ra ngoài → ghi chú theo quy định VTI.

> 🔴 **Thứ tự finalization (BrSE — bắt buộc):**
> 1. **Review toàn bộ nội dung:** keigo đúng mức, ngày tháng, hướng xử lý chính xác, AI không thêm thông tin không có trong input
> 2. **Điền placeholder ngoài AI:** copy ra email client, thay `[お客様名]` / `[会社名]` bằng tên thật
> 3. **Gửi** sau khi đã review và điền đầy đủ

Ví dụ thực tế (sample execution note): confirm chính thức 3 điểm mơ hồ về tính năng export báo cáo.

- **STEP-01**: ISMS OK (không có PII). Kênh: Email, Loại: question, Deadline: cuối tuần, Người ký: Nguyễn (BrSE).
- **STEP-02 (tiếng Việt — chờ BrSE OK):**
  ```
  【INPUT UNDERSTANDINGS】
  📂 Loại output: [question]
  📋 Summary: Tính năng export báo cáo có 3 điểm chưa rõ cần confirm trước khi implement.
  ❓ Open Points:
     · 🔴 [BLOCK] Format export: PDF hay CSV?
     · 🔴 [BLOCK] Quyền truy cập: theo role hay tất cả user?
     · 🟡 Filter range: tối đa bao nhiêu ngày? (không block ngay)
  🎯 Expected Answer Types: lựa chọn cụ thể cho cả 3 điểm
  ⚠️  Downstream: 2 điểm BLOCK → không thể code; điểm 3 → ảnh hưởng UI
  💡 Assumptions: không có
  ```
- **STEP-03**: → **BrSE gõ "OK"** → sang STEP-04
- **STEP-04 (tiếng Nhật — sau khi đã có OK):**
  ```
  件名: 【ご確認】レポートエクスポート機能の要件について

  [会社名] [お客様名]様

  お世話になっております。Nguyễnでございます。
  レポートエクスポート機能の実装に向け、以下の点をご確認いただけますでしょうか。

  ①エクスポート形式はPDFとCSV、どちらをご希望でしょうか。
  ②アクセス権限はロール別での制御を想定しておりますが、ご認識と相違ございませんでしょうか。
  ③日付フィルターで選択できる最大期間のご指定はございますでしょうか（例：30日・90日・制限なし）。

  お手数ですが、今週金曜日までにご回答いただけますと幸いです。
  （リリース日程への影響を避けるため）

  ご回答いただき次第、実装を進めてまいります。引き続きよろしくお願いいたします。

  Nguyễn
  ```
- **STEP-05**: Review Viewpoint — ✅ tự nhiên / ✅ 3 điểm grouped rõ / ✅ deadline có lý do / ✅ không AI-like
- **STEP-08**: Gửi mail 2026-05-27, expected reply 2026-05-29
- **STEP-09 / STEP-10**: KH reply — (1) PDF; (2) theo role; (3) 90 ngày. Update spec với cả 3 điểm. Ghi "KH confirmed via mail 2026-05-28".

## Re-plan Rule

Append Re-plan Log entry khi:
- danh sách điểm cần confirm thay đổi macro scope sau STEP-00
- receiver / KH contact thay đổi
- loại yêu cầu thay đổi
- language policy / subject convention thay đổi đáng kể
- KH reject yêu cầu dẫn tới thay đổi scope spec / design (escalate BrSE / PM trước)

## Re-plan Log

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- PLAN AIP (hoặc tương đương) đã làm rõ các điểm cần confirm và input understandings đã được BrSE confirm ở mức working level
- grouped open points đã visible, receiver / KH contact đã xác định
- cần xác nhận chính thức qua mail (formal, contractual, hoặc cần có evidence bằng văn bản)
- nội dung phức tạp, nhiều điểm cần giải thích — mail phù hợp hơn chat
- task chuyển từ giai đoạn **"làm rõ / chuẩn bị"** sang giai đoạn **"soạn và gửi mail"**

**Khi KHÔNG dùng file này:**
- danh sách điểm cần confirm vẫn unstable hoặc đang thay đổi nhiều
- BrSE chưa confirm input understandings
- chưa rõ receiver / KH contact chính thức
- chưa chốt được tone / language policy / subject format
- nội dung chỉ cần unblock nhanh (1–3 điểm đơn giản) → dùng Chat EXEC thay thế

## Changelog

- Migrated from legacy preset `AIP_EXEC_CreateMailConfirmRequirement.md` v1.0 (2026-04-16). Mapped PLAN sample: `AIP_Sample_CreateMailConfirmRequirement.md`.
  - Legacy PLAN-to-EXEC trace (outputs inherited from PLAN): grouped open points đã confirmed (phân loại theo topic); expected answer types cho từng điểm; current assumptions nếu chưa có reply; downstream impact understanding; approved wording direction và tone; expected reply deadline.
- 2026-06-20: Re-authored into current AIP_EXEC structure (frontmatter + `## Execution Steps` with STEP-NN em-dash headers; STEP-00 HARD GATE added). All documented intent preserved; no scope redesign.
- 2026-06-20: Repaired INTENT-LOSSY re-author — reinstated dropped legacy domain content verbatim from `.ai-work/preset_knowledge/` v2.0 source: ISMS/PII handling + VJP-ISMS-AI-FO001 Điều 3.3; required input "Loại yêu cầu (bug / spec / question / deadline)" + 📂 header + per-type adjustment; natural non-AI-sounding objective + self-checks; placeholders `[お客様名]`/`[会社名]`; BrSE finalization order ①review→②fill-placeholder-outside-AI→③send; 9-criterion Review Viewpoint with per-criterion `→ [...]` comments; keigo-level guidance; signer input "Tên BrSE/Comtor ký cuối mail"; mapped skill `/aiws-util-mail-confirm` + step-to-skill mapping table; two-language workflow (VN Input Understandings → Gate BrSE "OK" → JP draft). Steps renumbered STEP-00..STEP-10 sequential, no gaps, 7 required fields preserved.
