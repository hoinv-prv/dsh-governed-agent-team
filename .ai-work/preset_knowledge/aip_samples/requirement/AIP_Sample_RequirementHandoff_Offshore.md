# AIP_Sample_RequirementHandoff_Offshore

**Version:** v2.0  
**Date:** 2026-04-15  
**Target Task:** Truyền đạt yêu cầu cho offshore — tạo ticket / task description rõ ràng  
**Priority Basis:** High frequency in BrSE daily work — every sprint / every new requirement  
**Recommended Primary AIP Type:** EXEC AIP  
**Secondary Pattern:** Handoff-preparation / Input-synthesis / Downstream-enablement  
**Audience:** AI + BrSE + Offshore team (dev / leader)

---

## 1. Vì sao task này nên có AIP

Task **"Truyền đạt yêu cầu cho offshore"** là một trong những task lặp lại nhiều nhất của BrSE. Mỗi khi có requirement mới hoặc thay đổi từ KH Nhật, BrSE phải chuyển đổi thành ticket / task description đủ rõ để offshore tự thực hiện.

Đây là task nằm giữa giai đoạn "BrSE đã hiểu yêu cầu" và "offshore bắt đầu làm", nên chất lượng của handoff package ảnh hưởng trực tiếp đến:

- số lượng câu hỏi clarification từ offshore
- số lần offshore hiểu sai rồi phải làm lại
- thời gian từ lúc nhận yêu cầu đến lúc offshore bắt đầu thực sự
- visibility của open points và pending items
- khả năng trace ngược yêu cầu khi có vấn đề

Task này rất phù hợp để có AIP vì nó thường có:

- input từ **nhiều nguồn** (spec + email + meeting notes + verbal) — dễ thiếu / mâu thuẫn
- cần **tổng hợp và cấu trúc hóa** — không chỉ copy-paste từ KH
- cần phân biệt:
  - confirmed requirement
  - pending / chưa chốt
  - assumption BrSE tự suy luận
  - open point chưa có owner
- cần chốt:
  - ngôn ngữ output (Nhật / Anh / hỗn hợp)
  - format ticket (backlog item / JIRA / Redmine / custom)
  - mức detail cần thiết cho offshore tự làm
- cần confirm:
  - AI hiểu đúng yêu cầu trước khi draft
  - BrSE review output trước khi gửi offshore

Nếu không có AIP, task này thường dễ gặp các vấn đề:

- ticket chỉ chứa mô tả chung chung, thiếu context
- không phân biệt rõ confirmed vs pending → offshore coi hết là confirmed
- open points không có owner → bị bỏ sót
- offshore không biết acceptance criteria → không biết khi nào là "xong"
- requirement summary thiếu background → offshore không hiểu "tại sao" cần làm
- ngôn ngữ output bị AI tự chọn → phải viết lại

AIP cho task này giúp BrSE và AI:

- xác định rõ input nào có, input nào thiếu
- tổng hợp understanding trước khi viết ticket
- tạo bộ output chuẩn: Backlog Item + Req Summary + Confirmation Record
- self-review trước khi handoff
- giảm số vòng Q&A sau handoff

---

## 2. AIP type đề xuất

## 2.1. Primary AIP Type
**EXEC AIP**

### Vì sao
- task này có flow rõ ràng: đọc input → confirm hiểu → tạo ticket → tạo summary → tạo confirmation record → review → handoff
- mỗi step cần verify từ BrSE trước khi tiếp
- output cuối là các file cụ thể, không phải plan / analysis

## 2.2. Secondary style
**Handoff-preparation / Input-synthesis / Downstream-enablement**

### Vì sao
Task này không chỉ là "viết ticket".
Nó phải:
- tổng hợp input từ nhiều nguồn thành một gói coherent
- tách rõ confirmed vs pending
- đảm bảo offshore có đủ context để tự thực hiện
- giữ visible các open points và follow-up

## 2.3. Khi nào có thể dùng loại khác
- **PLAN AIP**: khi chưa rõ format output, scope chưa chốt, cần lên kế hoạch trước
- **Shared AIP**: khi nhiều BrSE cùng chuẩn bị handoff cho 1 package lớn
- **PM AIP**: khi trọng tâm là tracking tình trạng handoff, không phải viết ticket
- **Member AIP**: khi cần điều tra requirement trước khi viết (ví dụ: requirement phức tạp cần research)

---

## 2A. Rule bắt buộc mới cho flow "Truyền đạt yêu cầu cho offshore"

Từ nay, flow **Truyền đạt yêu cầu cho offshore** phải có:

1. **Input understandings**
   - AI đọc toàn bộ input và output ra:
     - requirement understanding (BrSE hiểu yêu cầu gì từ KH)
     - confirmed vs pending separation (điểm nào rõ, điểm nào chưa)
     - high-risk misunderstanding areas (offshore dễ hiểu sai chỗ nào)
     - out-of-scope understanding (gì KHÔNG nằm trong yêu cầu lần này)
     - expected offshore action (offshore cần làm gì sau khi nhận ticket)
   - BrSE confirm AI hiểu đúng trước khi tạo ticket

2. **Review viewpoint + self review**
   - trước khi close/finalize handoff package:
     - ticket đủ rõ để offshore tự thực hiện không?
     - confirmed vs pending tách rõ chưa?
     - open points có owner + next action chưa?
     - ngôn ngữ output đúng chưa?
     - offshore biết acceptance criteria chưa?
     - follow-up path có rõ chưa?

### Flow chuẩn mới
```text
Collect inputs (spec + email + meeting notes)
    ↓
Confirm format / language of outputs
    ↓
Extract and structure input understandings
    ↓
BrSE confirms understandings
    ↓
Create Backlog Item (ticket)
    ↓
Create Req Summary
    ↓
Create Confirmation Record (3 parts)
    ↓
Create review viewpoint
    ↓
Self review using review viewpoint
    ↓
Finalize / handoff to offshore
```

---

## 3. Mục tiêu của AIP cho "Truyền đạt yêu cầu cho offshore"

AIP của task này nên giúp trả lời được các câu hỏi sau:

1. AI đã hiểu đúng yêu cầu từ input chưa?
2. Điểm nào đã confirmed, điểm nào đang pending?
3. Offshore dễ hiểu sai chỗ nào?
4. Ticket có đủ rõ để offshore tự thực hiện không?
5. Acceptance criteria có pass/fail rõ ràng không?
6. Open points có owner + next action không?
7. Ngôn ngữ output đã đúng chưa?
8. Confirmation Record tách rõ 3 phần: KH confirm, offshore confirm, open points?
9. Khi nào task này được coi là done?

---

## 4. Khi nào nên tạo AIP riêng cho task này

Nên tạo AIP khi có một hoặc nhiều điều kiện sau:

- requirement mới hoặc requirement thay đổi đáng kể
- input từ nhiều nguồn (spec + email + meeting notes)
- requirement phức tạp, có nhiều open points
- offshore team chưa quen context dự án
- ticket cần trace ngược được yêu cầu gốc
- cần Confirmation Record để giảm risk sau handoff

Không nhất thiết cần full AIP khi:

- chỉ update nhỏ vào ticket đã có
- yêu cầu rất đơn giản, 1 câu mô tả là đủ
- BrSE trả lời trực tiếp câu hỏi offshore, không cần viết ticket mới

---

## 5. Bộ Q&A để clarify task "Truyền đạt yêu cầu cho offshore"

AI nên hỏi theo thứ tự sau.

### Q0. Input chính là gì?
- requirement document / spec từ KH Nhật
- email / chat từ KH Nhật
- ghi chú meeting
- verbal / BrSE mô tả bằng lời
- nhiều nguồn kết hợp

### Q1. Output dạng ticket là loại nào?
- Redmine ticket
- JIRA story / task
- Backlog item (custom format)
- File Markdown / Word gửi qua email
- Format riêng của dự án

### Q2. Ngoài ticket, còn output nào khác?
- Req Summary (tóm tắt requirement đi kèm)
- Confirmation Record (ghi nhận điểm đã confirm)
- Open Points Log (danh sách điểm chưa rõ)
- không cần output phụ

### Q3. Ngôn ngữ output là gì?
- tiếng Nhật
- tiếng Anh
- hỗn hợp (tùy loại output)
- BrSE quyết định từng lần

### Q4. Task này do ai thực hiện?
- chỉ một BrSE
- BrSE + member khác cùng contribute
- nhiều BrSE cùng chuẩn bị
- chưa rõ

### Q5. Offshore nhận handoff qua kênh nào?
- email
- shared folder / drive
- tool (Redmine / JIRA / Backlog...)
- trực tiếp trong meeting
- hỗn hợp

### Q6. Confirmation Record gồm những phần nào?
- confirm với KH Nhật (trước khi handoff)
- confirm với offshore (sau khi gửi ticket)
- open points log (có owner + next action)
- chỉ cần 1–2 phần

### Q7. Có open points nào đã biết trước không?
- có — danh sách sẵn
- có — nhưng chưa tổng hợp
- không có
- chưa rõ

### Q8. Mức độ hoàn thiện mong muốn?
- draft để BrSE review trước
- ready-to-send cho offshore
- ready-to-upload lên tool

### Q9. Khi nào task này được coi là done?
- ticket đã gửi cho offshore
- offshore confirm đã nhận và hiểu
- offshore bắt đầu thực hiện
- Confirmation Record đã lưu

---

## 6. Section trọng tâm của AIP cho task này

Các section nên được nhấn mạnh:

1. **Input Understanding / BrSE Confirmation** — AI phải tóm tắt hiểu biết trước khi draft
2. **Backlog Item** — ticket description đủ rõ cho offshore
3. **Req Summary** — tóm tắt background + requirement kèm ticket
4. **Confirmation Record (3 parts)** — trace điểm đã confirm với KH và offshore
5. **Open Points Log** — mỗi open point có owner + next action
6. **Acceptance Criteria** — offshore biết khi nào là "xong"
7. **Review Viewpoint / Self-review** — kiểm tra package trước khi handoff
8. **Out of Scope** — tránh offshore hiểu nhầm scope
9. **Language Decision** — ngôn ngữ từng output đã chốt

---

## 7. Template đề xuất

# Template — EXEC AIP for "Truyền đạt yêu cầu cho offshore"

## A. Metadata
- AIP ID:
- Title:
- Status: Draft
- Owner:
- Related Project / Phase:
- Handoff Target: offshore team
- Input Understanding Status:
- Review Viewpoint Status:
- Output Language:
- Related Documents:
- Related AIPs:

## B. Objective
- Mục tiêu là tạo bộ handoff package cho yêu cầu nào?
- Offshore sẽ dùng package này để làm gì tiếp?
- Gói understandings nào phải được BrSE confirm trước khi draft?

## C. Context Summary
- Background ngắn của yêu cầu
- Yêu cầu này đến từ đâu (KH / CR / internal)
- Tại sao cần handoff lúc này
- Impact nếu handoff chậm hoặc sai

## D. Scope of This Handoff
### In Scope
- yêu cầu / chức năng nào được handoff
- output cụ thể: Backlog Item + Req Summary + Confirmation Record

### Out of Scope
- phân tích kỹ thuật chi tiết (→ BD/DD)
- estimate effort
- viết test case
- gửi/upload ticket lên tool

## E. Inputs / Required References
| Input | Description | Required/Optional | Source |
|---|---|---|---|
| Spec / requirement doc | nguồn chính | Required | BrSE cung cấp file path hoặc paste |
| Email / chat từ KH | bổ sung context | Required (nếu có) | BrSE paste |
| Meeting notes | ghi chú cuộc họp | Required (nếu có) | BrSE paste |
| Format mẫu ticket | nếu dự án có template | Optional | BrSE cung cấp |
| Open points đã biết | điểm chưa rõ | Optional | BrSE paste / describe |

## F. Input Understanding and BrSE Confirmation
### F.1 Understanding Outputs
Trước khi tạo ticket, AI phải output tối thiểu:
- confirmed requirements (đã rõ từ input)
- pending requirements (chưa chốt)
- high-risk misunderstanding areas (offshore dễ hiểu sai)
- out-of-scope items (không nằm trong lần này)
- expected offshore action (offshore cần làm gì)

### F.2 BrSE Confirmation Rule
- BrSE phải confirm understandings trước khi AI tạo Backlog Item
- Nếu có phần chưa chắc, giữ visible như pending trong Confirmation Record
- AI không được coi assumption là confirmed fact

### F.3 Review Viewpoint
Review viewpoint cho handoff package:
- ticket đủ rõ để offshore tự thực hiện?
- confirmed vs pending tách rõ?
- open points có owner + next action?
- ngôn ngữ output đúng?
- acceptance criteria pass/fail rõ?
- follow-up path rõ?

## G. Step-by-Step Execution Flow
| Step | Action | Main input | Main output | Gate / note |
|---|---|---|---|---|
| 1 | Confirm format, ngôn ngữ, danh sách input | BrSE cung cấp | Bảng xác nhận | → Member verify |
| 2 | Tổng hợp Input Understanding | I-1, I-2, I-3 | Understanding summary | → Member verify: BrSE confirm AI hiểu đúng |
| 3 | Tạo Backlog Item | Understanding confirmed | Draft ticket | → Member verify: đủ rõ cho offshore? |
| 4 | Tạo Req Summary | Understanding + Ticket | Draft summary | → Member verify: đúng và đủ? |
| 5 | Tạo Confirmation Record (3 parts) | Steps 2-4 outputs | Draft record | → Member verify: open points có owner? |
| 6 | Self-review theo viewpoint | Steps 3-5 outputs | Review table | → Member verify: sẵn sàng handoff? |

## H. Open Points / Assumptions / Risks
### H.1 Open Points
| ID | Open Point | Why Important | Owner | Next Action |
|---|---|---|---|---|

### H.2 Assumptions
| ID | Assumption | Why Used | Acceptable Until When |
|---|---|---|---|

### H.3 Risks
| ID | Risk | Impact | Handling |
|---|---|---|---|

## I. Review Viewpoint / Self Review
Review viewpoint cho package:
- ticket đủ rõ để offshore tự làm?
- confirmed/pending tách rõ?
- open points có owner + action?
- high-risk areas visible?
- ngôn ngữ đúng?
- scope rõ?

## J. Done Criteria
Task is done when:
- input understandings confirmed by BrSE
- Backlog Item draft reviewed and accepted
- Req Summary draft reviewed and accepted
- Confirmation Record completed (3 parts)
- self-review performed using review viewpoint
- handoff package ready for offshore

---

## 8. Sample AIP

# Sample — AIP for "Truyền đạt yêu cầu màn hình Order Entry cho offshore"

## A. Metadata
- AIP ID: AIP-EXEC-020-truyen-dat-yeu-cau-order-entry
- Title: Truyền đạt yêu cầu màn hình Order Entry cho offshore
- Status: Draft
- Owner: BrSE
- Related Project / Phase: Requirement Handoff
- Handoff Target: offshore dev team
- Input Understanding Status: pending BrSE confirmation
- Review Viewpoint Status: to be created at Step 6
- Output Language: Ticket = tiếng Anh, Req Summary = tiếng Anh, Confirmation Record = tiếng Việt
- Related Documents:
  - Requirement spec v1.2 — Order Entry
  - Email thread: KH confirm validation rule (2026-04-10)
  - Meeting notes: kickoff meeting Order Entry (2026-04-08)
  - Open issue list
- Related AIPs:
  - AIP-PLAN-005-create-basic-design-order-entry

## B. Objective
- Tạo bộ handoff package (Backlog Item + Req Summary + Confirmation Record) cho yêu cầu màn hình Order Entry
- Offshore dev team dùng package này để bắt đầu implementation
- AI phải output input understandings để BrSE confirm trước khi tạo ticket

## C. Context Summary
KH Nhật đã provide requirement spec cho màn hình Order Entry cùng một số clarification qua email. Sau kickoff meeting, BrSE đã nắm đủ context. Cần tạo ticket rõ ràng cho offshore để bắt đầu sprint tiếp theo.

Nếu handoff chậm:
- offshore idle trong sprint mới
- risk hiểu sai requirement vì thiếu context

## D. Scope of This Handoff
### In Scope
- requirement Order Entry screen: CRUD operations, validation, search
- Backlog Item, Req Summary, Confirmation Record

### Out of Scope
- Detail Design / DB Design (→ task riêng)
- Test case creation (→ task riêng)
- Performance requirement (chưa discuss)
- Estimate effort cho offshore

## E. Inputs / Required References
| Input | Description | Required/Optional | Source |
|---|---|---|---|
| Requirement spec v1.2 | requirement chính | Required | BrSE cung cấp file path |
| Email thread 2026-04-10 | validation rule confirm | Required | BrSE paste |
| Meeting notes 2026-04-08 | kickoff context | Required | BrSE paste |
| Open issue list | pending items | Optional | BrSE paste |

## F. Input Understanding and BrSE Confirmation

### F.1 Understanding Outputs
- **Confirmed requirements:** Order Entry screen support Create/Read/Update/Delete, duplicate check on Order Code, mandatory fields validated on Save
- **Pending requirements:** permission model for override duplicate, exact error message wording
- **High-risk misunderstanding areas:** duplicate handling logic (offshore có thể hiểu "warning" là "block"), validation timing (on blur vs on save)
- **Out of scope:** auto-save, batch import, report export
- **Expected offshore action:** implement CRUD + validation theo spec, flag câu hỏi về duplicate override

### F.2 BrSE Confirmation
BrSE confirmed: understanding phản ánh đúng input → tiếp tục tạo ticket.

## G. Step-by-Step Execution Flow
| Step | Action | Main input | Main output | Gate |
|---|---|---|---|---|
| 1 | Confirm format: Backlog item format, ngôn ngữ EN/EN/VI | BrSE | Format confirmed | → Member verify |
| 2 | Input Understanding summary | spec + email + notes | Understanding (confirmed/pending/risk) | → Member verify: BrSE confirm |
| 3 | Tạo Backlog Item | Understanding confirmed | Ticket draft | → Member verify: đủ rõ? |
| 4 | Tạo Req Summary | Understanding + Ticket | Summary draft | → Member verify: đúng? |
| 5 | Tạo Confirmation Record | Steps 2-4 | Record (3 parts) | → Member verify: owner rõ? |
| 6 | Self-review | Steps 3-5 | Review table | → Member verify: ready? |

## H. Open Points / Assumptions / Risks

### H.1 Open Points
| ID | Open Point | Why Important | Owner | Next Action |
|---|---|---|---|---|
| OP-01 | Override permission for duplicate | affects flow logic | BrSE → KH | ask KH in next meeting |
| OP-02 | Exact error message wording | UI detail | BrSE | defer to DD phase |

### H.2 Assumptions
| ID | Assumption | Why Used | Acceptable Until When |
|---|---|---|---|
| AS-01 | Duplicate = block save (not just warning) | to draft ticket AC | until KH overrides |
| AS-02 | Validation on Save, not on blur | simpler to implement first | until DD phase confirm |

### H.3 Risks
| ID | Risk | Impact | Handling |
|---|---|---|---|
| R-01 | Offshore interprets "warning" as "block" | rework | explicit note in ticket |
| R-02 | Open points forgotten after handoff | scope gap | Confirmation Record Part 3 |

## I. Review Viewpoint / Self Review
- [x] Ticket đủ rõ để offshore tự implement?
- [x] Confirmed vs pending tách rõ?
- [x] Open points có owner (OP-01: BrSE→KH, OP-02: BrSE)?
- [x] High-risk area (duplicate handling) được note rõ?
- [x] Ngôn ngữ: Ticket EN, Summary EN, Record VI — đúng?
- [x] Scope rõ: CRUD + validation, không có auto-save/batch/report?

## J. Done Criteria
Task is done when:
- BrSE confirmed input understandings
- Backlog Item reviewed and accepted
- Req Summary reviewed and accepted
- Confirmation Record completed (KH confirm, offshore confirm, open points log)
- self-review passed
- package sent to offshore

---

## 9. Variant nên có cho task này

### Variant 1 — Truyền đạt yêu cầu màn hình / UI
Dùng cho requirement liên quan đến screen-based function.

### Variant 2 — Truyền đạt yêu cầu batch / report
Dùng khi yêu cầu là batch processing hoặc report, section ticket khác screen.

### Variant 3 — Truyền đạt Change Request cho offshore
Dùng khi handoff là CR / scope change, cần nêu rõ delta so với hiện tại.

### Variant 4 — Truyền đạt yêu cầu có nhiều open points
Dùng khi chưa clear hết nhưng vẫn cần handoff để offshore chuẩn bị.

### Variant 5 — Truyền đạt yêu cầu khẩn (urgent handoff)
Dùng khi cần handoff nhanh, giảm step review nhưng vẫn giữ minimum quality.

---

## 10. Gợi ý sample tiếp theo liên quan chặt tới task này

Sau sample này, các sample tiếp theo nên làm là:

1. **Shared AIP — Clarification round after offshore questions** *(đã có)*
2. **PLAN AIP — Create basic design**  *(đã có)*
3. **PLAN AIP — Review detail design before handoff**
4. **PM AIP — Track handoff progress across multiple tickets**
5. **META AIP — Handoff quality checklist template**

---

## 11. Final note

Task "Truyền đạt yêu cầu cho offshore" không chỉ là "viết ticket và gửi".

AIP cho task này nên tập trung vào:

> **input understanding + confirmed/pending separation + ticket clarity + open points visibility + self-review before handoff**

để offshore nhận package và bắt đầu làm việc ngay, thay vì phải hỏi lại nhiều vòng.

## PLAN-to-EXEC linkage

### Linked / Recommended EXEC AIP
AIP_EXEC_TruyenDatYeuCau_Offshore.md

### Why EXEC should follow this PLAN
Execute actual handoff: create ticket + req summary + confirmation record

### Outputs from this PLAN that EXEC should inherit
- BrSE-confirmed input understandings
- confirmed format / language of outputs
- open points list with owners
- review viewpoint for self-review
- out-of-scope items

### EXEC entry conditions
- input understandings confirmed by BrSE
- format / language of outputs confirmed
- all required inputs available
- major open points have owners

### When NOT to create EXEC yet
- do not create EXEC if input sources are still incomplete
- do not create EXEC if BrSE has not confirmed input understandings
- do not create EXEC if output format / language is still undecided
- do not create EXEC if scope of handoff is still changing

### Handoff checklist from PLAN to EXEC
- [ ] input understandings confirmed
- [ ] output format and language confirmed
- [ ] required inputs are available
- [ ] open points have owners
- [ ] review viewpoint source is identified
- [ ] BrSE agrees that execution can start

### Rule if no PLAN exists
- If no PLAN AIP exists **but inputs are already clear and format is confirmed**, EXEC may be created directly.
- If no PLAN AIP exists **and inputs are unclear or format is undecided**, create PLAN first, then derive EXEC from PLAN outputs.

### Trace note for AI / BrSE
When creating EXEC from this PLAN, AI should first read/ask:
1. Which input understandings are already confirmed?
2. Which open points must be carried into EXEC?
3. What format / language decisions have been made?
4. What review viewpoint or checklist should EXEC reuse?
5. What completion condition from this PLAN becomes the entry condition of EXEC?
