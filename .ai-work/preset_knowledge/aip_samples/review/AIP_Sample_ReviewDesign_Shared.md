# AIP_Sample_ReviewDesign_Shared.md

**Version:** v1.0
**Date:** 2026-04-16
**Target Task:** Review design (BD / DD / Screen Design)
**Priority Basis:** High practical reuse in BrSE design review and quality control tasks
**Recommended Primary AIP Type:** Shared AIP
**Secondary Pattern:** Review-oriented / QA-coordination / Downstream-quality-control
**Audience:** AI + BrSE + Reviewer + SE/QA/PM + Design Owner + Offshore

---

## 1. Vì sao task này nên có AIP

Task **"Review design"** là điểm kiểm soát chất lượng quan trọng trước khi tài liệu thiết kế được dùng cho các bước tiếp theo (DD, development, test, offshore handoff).

Đây không chỉ là việc "đọc tài liệu và comment".
Trong thực tế, review design thường bao gồm:

- xác định đúng scope review và mục tiêu review
- nhìn tài liệu từ nhiều góc độ:
  - requirement consistency (thiết kế có đúng với yêu cầu đã confirm không?)
  - business logic (flow/rule có đúng và đủ không?)
  - scope / boundary (in-scope/out-of-scope có rõ không?)
  - implementability (có khả thi ở mức thiết kế hiện tại không?)
  - downstream usability (DD/dev/QA/offshore có dùng được không?)
  - completeness / consistency (có thiếu section, mâu thuẫn nội bộ không?)
- tách rõ:
  - issue logic (thiết kế sai hoặc thiếu)
  - issue consistency (mâu thuẫn với requirement/spec)
  - issue clarity (mô tả không rõ, downstream phải đoán)
  - issue scope (boundary không rõ, dễ hiểu sai scope)
  - pending point (spec/requirement chưa rõ ảnh hưởng thiết kế)
  - recommendation (cải thiện nhưng không blocking)
- phối hợp nhiều bên:
  - design owner (SE / architect)
  - BrSE / reviewer
  - QA (testability viewpoint)
  - offshore team (executability)
  - PM nếu có blocker ảnh hưởng schedule

Task này rất phù hợp với **Shared AIP** vì:
- review findings không chỉ dành cho một người
- kết quả review ảnh hưởng downstream quality
- cần rule rõ về:
  - ai review
  - ai update design
  - ai xác nhận closure
  - khi nào re-review
- output chính là **Review Comment** + **Checklist** — dùng chung cho nhiều bên

AIP cho task này giúp:
- chốt review objective và scope
- structure findings / severity / owner / next action
- tạo checklist có cấu trúc để đánh giá quality
- làm rõ coordination rule sau review
- tăng chất lượng downstream handoff

---

## 2. AIP type đề xuất

### 2.1. Primary AIP Type
**Shared AIP**

#### Vì sao
- review findings ảnh hưởng đến nhiều bên: design owner, QA, offshore, BrSE, PM
- có coordination / rework / re-review
- output (Review Comment + Checklist) được nhiều bên cùng tham chiếu

### 2.2. Secondary style
**Review-oriented / QA-coordination / Downstream-quality-control**

#### Vì sao
- không phải tạo artifact mới
- trọng tâm là đánh giá chất lượng thiết kế hiện có
- cần structure findings rõ để design owner update và reviewer confirm

### 2.3. Khi nào có thể dùng loại khác
- **PLAN AIP**: nếu review nhỏ, thiên về personal checklist nhanh
- **PM AIP**: nếu focus là tracking review status / blockers cho toàn project
- **Member AIP**: nếu chỉ là self-check / pre-review investigation cá nhân
- **EXEC AIP**: khi review flow đã rất chuẩn hóa và chỉ cần đi từng bước theo checklist cố định

---

## 3. Rule bắt buộc mới cho flow "Review design"

Từ nay, flow cho task **Review design** phải có các step bắt buộc sau:

1. **Làm rõ input understandings**
   - AI đọc input và output ra:
     - design objective understanding (tài liệu này viết để làm gì?)
     - design scope / boundary understanding (cover gì, không cover gì?)
     - requirement alignment understanding (thiết kế bám requirement nào?)
     - likely risk / ambiguity areas (chỗ nào dễ hiểu sai / thiếu?)
     - intended downstream usage understanding (ai dùng tiếp? để làm gì?)
   - BrSE / reviewer confirm AI đã hiểu đúng input ở mức working level

2. **Thực hiện review / tạo findings draft**
   - chỉ thực hiện sau khi understandings đã được confirm đủ để làm việc
   - review theo 6 dimensions đã xác định

3. **Tạo review viewpoint để self-review trước khi close**
   - review viewpoint dùng để tự kiểm:
     - scope review đã đúng chưa
     - findings có đúng và đủ chưa
     - severity / impact có hợp lý chưa
     - checklist items có justified chưa
     - coordination / re-review rule có rõ chưa

### Ý nghĩa của rule này
Rule này giúp:
- AI không review sai scope do hiểu sai tài liệu
- findings không bị rời rạc
- Review Comment + Checklist usable hơn cho design owner và downstream team
- BrSE có điểm kiểm soát sớm để confirm AI đã hiểu đúng thiết kế trước khi review sâu

### Flow chuẩn mới
```text
Collect review inputs (design doc + requirement + clarification + prior design)
    ↓
Extract and structure understandings
    ↓
BrSE / reviewer confirms understandings
    ↓
Review design: 6 dimensions
    ↓
Create Review Comment (severity-classified findings)
    ↓
Create Checklist (pass/fail per criteria)
    ↓
Create review viewpoint
    ↓
Self review using review viewpoint
    ↓
Finalize outputs / handoff / re-review rule
```

---

## 4. Mục tiêu của AIP cho "Review design"

AIP của task này nên giúp trả lời được các câu hỏi sau:

1. Review tài liệu thiết kế nào, cho scope nào?
2. AI/reviewer đã hiểu đúng tài liệu input đến mức nào?
3. Review từ góc nhìn nào (6 dimensions)?
4. Kết quả review được ai dùng tiếp?
5. Findings nào là critical / major / minor / note?
6. Checklist items nào pass/fail?
7. Issue nào ảnh hưởng downstream work?
8. Sau review thì ai làm gì tiếp theo?
9. Khi nào review được coi là done?

---

## 5. Khi nào nên tạo AIP riêng cho "Review design"

Nên tạo AIP khi có một hoặc nhiều điều kiện sau:

- tài liệu thiết kế có độ phức tạp vừa hoặc lớn
- có nhiều reviewer hoặc nhiều viewpoint cần check
- output review ảnh hưởng tới DD/dev/QA/customer communication
- cần re-review hoặc issue tracking
- cần structure severity / owner / next action
- downstream team cần biết có thể tiếp tục hay chưa
- cần tránh comment rời rạc, thiếu follow-up

Không nhất thiết cần full AIP khi:

- chỉ review một thay đổi rất nhỏ, isolated
- chỉ self-check nhanh, không có downstream dependency đáng kể
- không cần issue structure rõ

---

## 6. Bộ Q&A để clarify task "Review design"

AI nên hỏi theo thứ tự sau.

### Q1. Review tài liệu thiết kế nào?
- Basic Design (BD)
- Detail Design (DD)
- Screen Design (UI)
- nhiều loại kết hợp

### Q2. Scope review là gì?
- toàn bộ tài liệu
- chỉ phần thay đổi / mới thêm
- chỉ section cụ thể
- issue-focused review

### Q3. Mục tiêu review là gì?
- check consistency với requirement
- check business logic
- check scope / boundary
- check implementability
- check downstream usability
- check completeness / internal consistency
- prepare for customer/internal review

### Q4. Input chính để review là gì?
- tài liệu thiết kế (target review)
- requirement / spec
- clarification results
- prior design (BD cho DD review)
- open issue / assumption list
- prior review comments
- review checklist (project-specific)

### Q5. Review từ góc nhìn nào?
- requirement consistency
- business logic
- scope / boundary
- implementability
- downstream usability
- completeness / consistency
- multiple viewpoints

### Q6. Ai sẽ dùng kết quả review?
- design owner
- BrSE
- SE/dev
- QA
- PM
- offshore team
- customer-facing team

### Q7. Output review cần ở dạng nào?
- Review Comment (severity-classified findings)
- Checklist (pass/fail per criteria)
- cả hai (mặc định)
- severity summary
- go/no-go recommendation

### Q8. Có cần classify issue theo severity không?
- có: critical / major / minor / note (mặc định)
- có: blocker / major / minor / note
- không cần

### Q9. Sau review, flow xử lý issue là gì?
- design owner sửa rồi re-review
- discuss trong meeting
- log vào issue tracker
- accept as pending / defer
- escalate to BrSE / PM / customer

### Q10. Khi nào task này được coi là done?
- Review Comment đã output rõ ràng
- Checklist đã output pass/fail
- findings đã handoff đúng owner
- re-review rule rõ
- downstream biết có thể tiếp tục hay chưa

---

## 7. Section trọng tâm của AIP cho task này

Các section nên được nhấn mạnh:

1. **Review Objective**
2. **Review Scope**
3. **Input Understandings / Reviewer Confirmation**
4. **Review Dimensions (6 dimensions)**
5. **Review Comment (structured findings)**
6. **Checklist (pass/fail per criteria)**
7. **Review Viewpoint / Self Review**
8. **Coordination / Re-review Plan**
9. **Done Criteria**

---

## 8. Template đề xuất

# Template — Shared AIP for "Review design"

## A. Metadata
- AIP ID:
- Title:
- Status: Draft
- Owner:
- Related Project / Phase:
- Review Target: (design document name / version)
- Design Type: BD / DD / Screen Design
- Input Understanding Status:
- Review Viewpoint Status:
- Related Documents:
- Related AIPs:
- Reviewers:
- Design Owner:

## B. Objective
- Mục tiêu của review này là gì?
- Review này nhằm phục vụ bước tiếp theo nào (DD / dev / test / offshore handoff)?
- Sau review, điều gì phải trở nên rõ hơn hoặc an toàn hơn?
- Output chính: Review Comment + Checklist

## C. Context Summary
- Background ngắn của tài liệu thiết kế
- Vì sao cần review lúc này
- Downstream impact nếu thiết kế có issue mà không phát hiện sớm
- Review round hiện tại là round mấy nếu có

## D. Input Sources / Required References
| Input | Description | Required/Optional | Source |
|---|---|---|---|
| Design document | target review | Required | Internal |
| Requirement / spec | consistency baseline | Required | Internal/Customer |
| Clarification results | confirmed business rules | Optional | Internal/Customer |
| Prior design (BD for DD review) | cross-level alignment | Optional | Internal |
| Open issue / assumption list | uncertainty visibility | Optional | Internal |
| Prior review comments | continuity | Optional | Internal |
| Review checklist (project-specific) | custom criteria | Optional | Internal |

## E. Input Understanding and Reviewer Confirmation
### E.1 Understanding outputs
Trước khi review sâu, AI/reviewer phải output tối thiểu:
- design objective understanding (tài liệu này viết để làm gì?)
- scope / boundary understanding (cover gì, không cover gì?)
- requirement alignment understanding (bám requirement nào?)
- likely risk / ambiguity areas (chỗ nào dễ hiểu sai?)
- intended downstream usage understanding (ai dùng tiếp? để làm gì?)

### E.2 Reviewer / BrSE Confirmation Rule
- BrSE hoặc reviewer phải confirm working-level understanding trước khi review findings được coi là hợp lệ
- nếu có phần input chưa đủ chắc, phải giữ visible như uncertainty note

## F. Review Scope
### In Scope
- phần nào của thiết kế được review
- viewpoint nào sẽ cover
- changed scope nếu có

### Out of Scope
- phần không review trong round này
- issue defer sang phase khác
- detail quá sâu thuộc phase khác

## G. Review Dimensions
| Dimension | What to check | Why it matters | Priority |
|---|---|---|---|
| Requirement Consistency | align with source requirement/clarification | prevent downstream mismatch | High |
| Business Logic | flow/rule/behavior correct and complete | prevent wrong downstream design | High |
| Scope & Boundary | in-scope/out-of-scope clarity | avoid over/under design | High |
| Implementability | feasible at current design level | reduce ambiguity later | High |
| Downstream Usability | usable for next phase team | improve handoff quality | High |
| Completeness & Consistency | no missing sections, no contradictions | prevent hidden gaps | Medium |

## H. Review Comment (Findings)

### H.1 Requirement Consistency
| ID | Requirement Area | Alignment | Gap Description | Severity | Suggested Action | Owner |
|---|---|---|---|---|---|---|

### H.2 Business Logic
| ID | Flow / Rule | Issue | Severity | Impact | Suggested Action | Owner |
|---|---|---|---|---|---|---|

### H.3 Scope & Boundary
| ID | Issue | Severity | Impact | Suggested Action | Owner |
|---|---|---|---|---|---|

### H.4 Implementability
| ID | Design Element | Issue | Severity | Impact | Suggested Action | Owner |
|---|---|---|---|---|---|---|

### H.5 Downstream Usability
| ID | Issue | Downstream Impact | Severity | Suggested Action | Owner |
|---|---|---|---|---|---|

### H.6 Completeness & Consistency
| ID | Issue | Severity | Suggested Action | Owner |
|---|---|---|---|---|

### H.7 Positive Confirmations
| Item | What is already good / clear | Why it matters |
|---|---|---|

## I. Checklist

### I.1 Standard Checklist
| No | Check Item | Result | Finding Ref | Notes |
|---|---|---|---|---|
| 1 | Scope aligns with requirement | Pass/Fail/Skip | | |
| 2 | Main business flow is visible and correct | Pass/Fail/Skip | | |
| 3 | In-scope / out-of-scope boundary is explicit | Pass/Fail/Skip | | |
| 4 | Pending/open points are visible | Pass/Fail/Skip | | |
| 5 | Design level is appropriate | Pass/Fail/Skip | | |
| 6 | Usable for downstream | Pass/Fail/Skip | | |
| 7 | Terminology consistent | Pass/Fail/Skip | | |
| 8 | No internal contradictions | Pass/Fail/Skip | | |
| 9 | All expected sections present | Pass/Fail/Skip | | |
| 10 | Assumptions explicitly marked | Pass/Fail/Skip | | |

### I.2 Design-Type-Specific Checklist
*(Chọn checklist phù hợp: BD / DD / Screen Design — xem Section 9 bên dưới)*

### I.3 Project-Specific Checklist
*(Nếu BrSE cung cấp checklist riêng của dự án)*

## J. Review Viewpoint / Self Review
Review viewpoint cho review package nên tự kiểm:
- review scope có đúng không
- findings có cover đủ 6 dimensions không
- severity / impact có logic không
- checklist items có justified không (Fail phải link finding ID)
- recommendation có actionable không
- re-review / handoff rule có rõ không
- downstream team có hiểu được Review Comment + Checklist không

## K. Coordination / Re-review Plan
| Step | Action | Owner | Output |
|---|---|---|---|
| 1 | Confirm input understandings | BrSE / Reviewer | confirmed understanding |
| 2 | Draft Review Comment + Checklist | Reviewer / AI | draft outputs |
| 3 | Create review viewpoint and self review | Reviewer / AI | reviewed outputs |
| 4 | Send consolidated result to design owner | BrSE / Reviewer | handoff review package |
| 5 | Design owner updates document | Design owner | revised design |
| 6 | Re-review Major/Critical issues | Reviewer | confirmed closure |
| 7 | Confirm proceed readiness | BrSE | go/no-go for next phase |

## L. Downstream Impact / Proceed Rule
| Downstream Task | How review result affects it | Blocked by which severity |
|---|---|---|
| Detail Design | unsafe if scope/logic unclear | Critical/Major |
| Dev / Offshore handoff | weak if design ambiguity remains | Major |
| QA / test design | difficult if business flow unclear | Major/Medium |
| Customer/internal review | weak if wording/pending points unclear | Medium |

## M. Expected Outputs
- confirmed input understandings
- **Review Comment** (severity-classified findings)
- **Checklist** (pass/fail per criteria)
- action items with severity / owner / deadline
- re-review / handoff rule
- downstream proceed recommendation

## N. Done Criteria
Task is done when:
- input understandings are confirmed
- Review Comment is structured clearly with severity classification
- Checklist is completed with pass/fail and finding references
- review viewpoint exists and self-review has been performed
- action items are handed over to the correct owner
- major/critical issues have re-review plan
- downstream team knows whether they can proceed safely

---

## 9. Design-Type-Specific Checklists

### 9.1 Basic Design Checklist
| No | Check Item | Result | Finding Ref | Notes |
|---|---|---|---|---|
| BD-1 | Business flow covers normal + abnormal paths | Pass/Fail/Skip | | |
| BD-2 | Scope boundary between BD and DD is clear | Pass/Fail/Skip | | |
| BD-3 | Sufficient for DD author to start detail design | Pass/Fail/Skip | | |
| BD-4 | Key validation rules / business rules described | Pass/Fail/Skip | | |
| BD-5 | External dependencies / IF identified | Pass/Fail/Skip | | |

### 9.2 Detail Design Checklist
| No | Check Item | Result | Finding Ref | Notes |
|---|---|---|---|---|
| DD-1 | DB schema / table design covers all data requirements | Pass/Fail/Skip | | |
| DD-2 | API / IF spec is complete (input/output/error) | Pass/Fail/Skip | | |
| DD-3 | Error handling / exception flow described | Pass/Fail/Skip | | |
| DD-4 | Aligns with BD — no contradiction or scope drift | Pass/Fail/Skip | | |
| DD-5 | Sufficient for developer to implement without major clarification | Pass/Fail/Skip | | |

### 9.3 Screen Design Checklist
| No | Check Item | Result | Finding Ref | Notes |
|---|---|---|---|---|
| SD-1 | All fields have type / required / validation defined | Pass/Fail/Skip | | |
| SD-2 | Button behavior and navigation flow are clear | Pass/Fail/Skip | | |
| SD-3 | Error message / validation message specified | Pass/Fail/Skip | | |
| SD-4 | Permission / role-based display rules defined | Pass/Fail/Skip | | |
| SD-5 | UI state transitions covered (initial/edit/readonly/error) | Pass/Fail/Skip | | |

---

## 10. Sample AIP

# Sample — AIP for "Review Basic Design của Order Entry"

## A. Metadata
- AIP ID: AIP-SHARED-010-review-design-order-entry-bd
- Title: Review Basic Design — Order Entry
- Status: Draft
- Owner: BrSE
- Related Project / Phase: Basic Design review
- Review Target: Order Entry Basic Design v1.0
- Design Type: Basic Design (BD)
- Input Understanding Status: pending reviewer confirmation
- Review Viewpoint Status: to be created before finalize
- Related Documents:
  - Order Entry Basic Design v1.0
  - Requirement summary v0.2
  - Clarification results on duplicate handling and scope boundary
  - Open issue / assumption list
- Related AIPs:
  - AIP-PLAN-003-requirement-analysis-order-entry
  - AIP-PLAN-005-create-basic-design-order-entry
- Reviewers:
  - BrSE
  - SE reviewer
  - QA representative (optional for downstream testability viewpoint)
- Design Owner:
  - SE

## B. Objective
- Review Order Entry BD để phát hiện các vấn đề về requirement consistency, business logic, scope boundary và downstream usability
- Output: Review Comment + Checklist có cấu trúc
- Giảm risk ambiguity bị đẩy sang DD/dev/test

## C. Context Summary
BD của Order Entry đã được draft dựa trên requirement summary và các clarification chính.
Trước khi dùng làm baseline cho DD/dev/QA, cần review để đảm bảo:
- logic có bám requirement/clarification không
- scope/out-of-scope có rõ không
- pending/open points có visible không
- downstream team có dùng được không

Nếu không review tốt:
- DD có thể đi sai hướng
- dev/offshore có thể hiểu khác nhau về scope
- QA khó xác định test viewpoint đúng
- pending ambiguity có thể bị ẩn trong tài liệu

## D. Input Sources / Required References
| Input | Description | Required/Optional | Source |
|---|---|---|---|
| Order Entry Basic Design v1.0 | target review | Required | Internal |
| Requirement summary v0.2 | consistency baseline | Required | Internal |
| Clarification results | confirmed business/scope points | Required | Internal/Customer |
| Open issue / assumption list | uncertainty visibility | Optional | Internal |

## E. Input Understanding and Reviewer Confirmation
### E.1 Understanding outputs
- Order Entry là màn hình/business flow quan trọng của current release
- duplicate handling và scope boundary là 2 khu vực risk cao cần review kỹ
- BD này intended to support downstream DD/test/offshore understanding
- một số pending points vẫn còn và phải visible
- BD phải giữ mức abstraction phù hợp, không đi quá sâu như DD

### E.2 Reviewer / BrSE Confirmation Rule
- BrSE/reviewer phải confirm các understandings trên ở mức working level trước khi findings được finalize

## F. Review Scope
### In Scope
- business flow chính của Order Entry (CRUD + duplicate handling + validation)
- scope / out-of-scope clarity
- consistency với requirement và clarification
- pending/open-point visibility
- usability cho DD/dev/QA downstream

### Out of Scope
- UI wording quá chi tiết
- code-level implementation
- technical architecture / DB detail (thuộc DD)
- performance concerns
- future enhancements ngoài current release scope

## G. Review Dimensions
| Dimension | What to check | Why it matters | Priority |
|---|---|---|---|
| Requirement Consistency | BD aligns with clarified requirement | prevent mismatch → DD sai | High |
| Business Logic | order flow, duplicate logic, validation rules | prevent wrong design direction | High |
| Scope & Boundary | auto-save boundary, release scope | avoid scope misunderstanding | High |
| Implementability | feasible at BD level | avoid vague handoff to DD | Medium/High |
| Downstream Usability | DD/dev/QA can proceed with clarity | improve handoff quality | High |
| Completeness & Consistency | all sections present, no contradictions | prevent hidden gaps | Medium |

## H. Review Comment (Findings)

### H.1 Requirement Consistency
| ID | Requirement Area | Alignment | Gap Description | Severity | Suggested Action | Owner |
|---|---|---|---|---|---|---|
| RC-01 | Duplicate handling rule | Partial | BD mô tả "warning" nhưng requirement confirmed là "block save" | Major | Update BD theo confirmed clarification: block save khi duplicate | Design owner |

### H.2 Business Logic
| ID | Flow / Rule | Issue | Severity | Impact | Suggested Action | Owner |
|---|---|---|---|---|---|---|
| BL-01 | Validation order | Minor | BD nêu validation nhưng không rõ validation on blur hay on save | Minor | DD sẽ phải clarify hoặc BD nên ghi rõ hơn | Design owner |
| BL-02 | Delete behavior | Major | BD không nêu soft delete hay hard delete | Major | DD không biết implement theo hướng nào | Design owner |

### H.3 Scope & Boundary
| ID | Issue | Severity | Impact | Suggested Action | Owner |
|---|---|---|---|---|---|
| SB-01 | Auto-save not declared as out-of-scope | Major | DD/dev có thể hiểu nhầm scope | Add explicit out-of-scope note | Design owner |

### H.4 Implementability
| ID | Design Element | Issue | Severity | Impact | Suggested Action | Owner |
|---|---|---|---|---|---|---|
| IM-01 | Permission model for override duplicate | Minor | Chưa rõ ai có quyền override | Minor — defer to DD nếu BD level chưa cần | Design owner |

### H.5 Downstream Usability
| ID | Issue | Downstream Impact | Severity | Suggested Action | Owner |
|---|---|---|---|---|---|
| DU-01 | Flow summary khó follow | Offshore/QA mất thời gian đọc lại | Minor | Add concise flow summary trước detail | Design owner |

### H.6 Completeness & Consistency
*(Không có finding — section omitted)*

### H.7 Positive Confirmations
| Item | What is already good / clear | Why it matters |
|---|---|---|
| PC-01 | Main scope of Order Entry visible rõ | Baseline tốt cho DD |
| PC-02 | Key fields và primary actions đã structured | DD/test có thể bắt đầu |
| PC-03 | Assumption về auto-save out-of-scope đã partially visible | Tránh confuse offshore |

## I. Checklist

### I.1 Standard Checklist
| No | Check Item | Result | Finding Ref | Notes |
|---|---|---|---|---|
| 1 | Scope aligns with requirement | Fail | RC-01 | Duplicate handling mismatch |
| 2 | Main business flow is visible and correct | Pass | | Core flow rõ |
| 3 | In-scope / out-of-scope boundary is explicit | Fail | SB-01 | Auto-save chưa declared |
| 4 | Pending/open points are visible | Pass | | Visible trong assumptions list |
| 5 | Design level is appropriate | Pass | | Đúng mức BD |
| 6 | Usable for downstream | Fail | DU-01 | Flow summary khó follow |
| 7 | Terminology consistent | Pass | | |
| 8 | No internal contradictions | Pass | | |
| 9 | All expected sections present | Pass | | |
| 10 | Assumptions explicitly marked | Pass | | |

### I.2 Basic Design Checklist
| No | Check Item | Result | Finding Ref | Notes |
|---|---|---|---|---|
| BD-1 | Business flow covers normal + abnormal paths | Pass | | |
| BD-2 | Scope boundary between BD and DD is clear | Fail | SB-01 | |
| BD-3 | Sufficient for DD author to start detail design | Fail | BL-02 | Delete behavior unclear |
| BD-4 | Key validation rules / business rules described | Pass | | |
| BD-5 | External dependencies / IF identified | Pass | | Customer code master noted |

**Summary:** 10 / 15 passed | 4 failed | 0 skipped
**Verdict:** Has failed critical items — review required before proceeding to DD

## J. Review Viewpoint / Self Review
- review scope có đúng những risk area chính không: Yes — duplicate handling + scope boundary
- findings có cover đủ 6 dimensions không: Yes — 5 dimensions có findings
- severity classification có hợp lý không: Yes — Major cho blocking items, Minor cho improvement
- checklist Fail items có link finding ID không: Yes — tất cả Fail đều reference finding
- suggestion có actionable không: Yes — mỗi finding có specific action
- downstream team có hiểu được output không: Yes — structured theo dimension

## K. Coordination / Re-review Plan
| Step | Action | Owner | Output |
|---|---|---|---|
| 1 | Confirm input understandings | BrSE / Reviewer | confirmed understanding |
| 2 | Draft Review Comment + Checklist | Reviewer / AI | draft outputs |
| 3 | Create review viewpoint and self review | Reviewer / AI | reviewed outputs |
| 4 | Send consolidated result to design owner | BrSE / Reviewer | handoff review package |
| 5 | Design owner updates BD (RC-01, BL-02, SB-01) | Design owner | revised BD v1.1 |
| 6 | Re-review Major issues (RC-01, BL-02, SB-01) | Reviewer | confirmed closure |
| 7 | Confirm proceed readiness | BrSE | go/no-go for DD |

## L. Downstream Impact / Proceed Rule
| Downstream Task | How review result affects it | Blocked by which severity |
|---|---|---|
| Detail Design | unsafe if scope/logic unclear (RC-01, BL-02) | Major |
| Offshore handoff | weak if BD ambiguity remains | Major |
| QA / test design | difficult if validation flow unclear | Major/Medium |
| Customer/internal review | weaker if pending points are hidden | Medium |

## M. Expected Outputs
- confirmed review input understandings
- **Review Comment** with 6 findings (1 Critical-adjacent, 3 Major, 2 Minor)
- **Checklist** with 15 items (10 passed, 4 failed, 0 skipped)
- action items with severity / owner
- re-review plan for Major issues
- proceed recommendation: **Proceed with conditions** (fix RC-01, BL-02, SB-01 first)

## N. Done Criteria
Task is done when:
- input understandings are confirmed
- Review Comment is structured with severity classification
- Checklist is completed with finding references
- review viewpoint exists and self-review performed
- Major issues (RC-01, BL-02, SB-01) are re-reviewed after update
- downstream team knows: proceed to DD after 3 Major items are resolved

---

## 11. Variant nên có cho task này

### Variant 1 — Review BD for requirement consistency
Dùng khi trọng tâm là consistency với requirement / clarification.

### Variant 2 — Review DD for implementability
Dùng khi trọng tâm là DD đủ chi tiết để dev/offshore implement.

### Variant 3 — Review Screen Design for UI completeness
Dùng khi trọng tâm là field/validation/navigation coverage.

### Variant 4 — Review changed sections after CR / feedback
Dùng khi chỉ review phần thay đổi do CR hoặc review feedback.

### Variant 5 — Multi-reviewer consolidated design review
Dùng khi BrSE + SE + QA cùng review và cần merge kết quả.

### Variant 6 — Customer-facing design review readiness
Dùng khi chuẩn bị thiết kế cho customer review — focus vào wording, completeness, formal tone.

### Variant 7 — Cross-level review (BD vs DD alignment)
Dùng khi review DD mà cần đối chiếu với BD đã approve để kiểm tra consistency.

---

## 12. Gợi ý sample tiếp theo liên quan chặt tới task này

Sau sample này, các sample tiếp theo nên làm là:

1. **PM AIP — Risk / issue tracking** (nếu review findings ảnh hưởng schedule)
2. **PLAN AIP — Change request analysis** (nếu review phát hiện scope change)
3. **Shared AIP — Clarification round after offshore questions** (nếu offshore cần clarify sau handoff)
4. **PLAN AIP — Create test viewpoint** (nếu review findings ảnh hưởng test approach)
5. **PLAN AIP — Customer status report** (nếu design quality impact cần báo cáo KH)

---

## 13. Final note

Task "Review design" không chỉ là đọc tài liệu và comment.

AIP cho task này nên tập trung vào:

> **input understandings + 6 review dimensions + structured Review Comment + Checklist (pass/fail) + coordination / re-review rule + downstream safety**

để kết quả review giúp nâng chất lượng thiết kế và downstream work an toàn hơn.

## PLAN-to-EXEC linkage

### Linked / Recommended EXEC AIP

AIP_EXEC_ReviewDesign.md

### Why EXEC should follow this PLAN

Thực thi review design từng bước — sau khi PLAN đã xác nhận scope, understandings, và review dimensions.

### Outputs from this PLAN that EXEC should inherit

- confirmed input understandings
- review scope (in/out)
- review dimensions và priority
- downstream context
- project-specific checklist nếu có

### EXEC entry conditions

- tài liệu thiết kế đã available
- requirement / spec baseline đã available (hoặc xác nhận Mode C)
- review scope đã chốt
- BrSE đã confirm key understandings

### When NOT to create EXEC yet

- không tạo EXEC nếu input understandings chưa confirmed
- không tạo EXEC nếu chưa rõ review scope
- không tạo EXEC nếu tài liệu thiết kế đang thay đổi lớn
- không tạo EXEC nếu chưa rõ downstream team

### Handoff checklist from PLAN to EXEC

- [ ] PLAN objective và scope đã stable
- [ ] input understandings đã visible và confirmed
- [ ] open points / assumptions carried forward đã explicit
- [ ] review dimensions và priority đã xác định
- [ ] BrSE đồng ý execution có thể bắt đầu an toàn

### Rule if no PLAN exists

- Nếu không có PLAN AIP **nhưng inputs đã đủ rõ**, có thể tạo EXEC trực tiếp.
- Nếu không có PLAN AIP **và inputs chưa rõ**, tạo PLAN trước, sau đó derive EXEC từ PLAN outputs.

### Trace note for AI / BrSE

Khi tạo EXEC từ PLAN này, AI nên đọc / hỏi:
1. Outputs nào của PLAN này đã được confirmed?
2. Open points nào vẫn còn live và phải carry vào EXEC?
3. Review dimensions nào EXEC nên focus?
4. Checklist nào EXEC nên reuse?
5. Completion condition nào của PLAN này trở thành entry condition của EXEC?
