# WIKI_MINIMAL_GOVERNANCE_RULE_v0_1

## 1. Purpose
Tài liệu này định nghĩa **minimal governance rule** cho Wiki trong sprint hiện tại.

Mục tiêu:
- giữ canonical Wiki nhất quán
- tránh conflict khi nhiều người cùng tạo/use project knowledge
- cho phép Wiki lớn dần có kiểm soát
- không thiết kế governance nặng quá sớm

Governance trong sprint này là **minimal but usable**, không phải full workflow system.

---

## 2. Why governance is needed
Trong dự án thật:
- artifacts do nhiều người cùng tạo
- nhiều người có thể phát hiện information hữu ích cho Wiki
- AI cũng có thể gợi ý nhiều candidate khác nhau

Nếu không có governance tối thiểu, dễ gặp:
- duplicate updates
- inconsistent wording
- link/meta conflict
- immature knowledge đi thẳng vào canonical layer
- người sau không biết đâu là update chính thức

---

## 3. Governance scope in this sprint
In-scope:
- candidate → CR → canonical update flow
- wiki manager role
- AI update boundary
- AIP-driven flow treatment
- non-AIP interaction treatment ở mức tối thiểu
- publication/update boundary for canonical Wiki

Out-of-scope:
- complex approval workflow engine
- permission matrix chi tiết
- UI workflow
- automatic conflict resolution engine
- branch/merge model cho Wiki
- audit system chi tiết

---

## 4. Foundational principles

### 4.1. Canonical Wiki is a controlled layer
Canonical Wiki không phải nơi mọi finding/update được ghi trực tiếp ngay.

### 4.2. Candidate is not yet canonical
Một candidate hữu ích chưa đồng nghĩa với canonical update.

### 4.3. CR is the formal handoff to canonical update
Wiki Change Request là cấu trúc tối thiểu để chuyển từ candidate sang canonical update.

### 4.4. Wiki manager controls canonical update requests
Member quản lý Wiki là người request AI thực hiện canonical update theo change request.

### 4.5. AI does not self-promote everything
AI có thể gợi ý candidate, nhưng không tự đẩy mọi thứ vào canonical Wiki.

### 4.6. Minimal governance should reduce conflict, not block progress
Governance phải đủ để giữ consistency, nhưng không nên nặng đến mức làm flow không dùng được.

---

## 5. Minimal governance objects

### 5.1. Candidate
Một phát hiện hoặc đề xuất có ích cho Wiki, ví dụ:
- artifact publication candidate
- metadata candidate
- linkage candidate
- curated project knowledge candidate

Candidate có thể phát sinh từ:
- AIP-driven task outputs
- ad hoc interactions
- artifact understanding outputs
- review/research/brainstorming outputs
- notebook discoveries

Candidate chưa phải canonical update.

### 5.2. Change Request (CR)
Cấu trúc chính thức để yêu cầu update canonical Wiki.

### 5.3. Canonical update
Update đã được request đúng cách và được AI áp dụng vào canonical Wiki.

---

## 6. Roles in this sprint

### 6.1. BrSE / HUMAN
Có thể:
- review outputs
- confirm/refine understanding
- create or request candidates
- request or discuss CR drafting
- approve project-specific direction

### 6.2. Wiki manager
Là role tối thiểu chịu trách nhiệm:
- review candidate / CR
- decide whether canonical update should happen
- request AI to execute update
- reduce duplicate/conflicting updates

### 6.3. AI
Có thể:
- surface candidate
- draft CR
- package existing outputs into CR structure
- apply canonical update only after proper request
- avoid extra reasoning by default for CR generation

---

## 7. Minimal flow

### 7.1. AIP-driven flow
1. Task runs under AIP
2. outputs are produced
3. AI may suggest Wiki candidate if relevant
4. candidate is reviewed/converted into CR
5. wiki manager requests AI canonical update
6. AI applies update
7. optional change summary is recorded

### 7.2. Non-AIP interactions
Outside AIP:
- AI may still suggest useful candidate
- but process is not formalized in equal detail in this sprint
- canonical update still requires CR + wiki manager control

### 7.3. Rule
Only canonical update is governance-controlled here.
Candidate surfacing is intentionally lighter.

---

## 8. Governance boundary for AIP vs non-AIP

### 8.1. AIP-driven flows
These are the main formally described flows in this sprint.

In these flows:
- wiki suggestion rule is clearer
- CR handling is clearer
- add-to-wiki steps for deliverable artifacts can become explicit

### 8.2. Non-AIP flows
For ad hoc Q&A / brainstorming / research / short interactions:
- AI is encouraged to suggest Wiki candidate when useful
- but sprint does not formalize a full process/rule set here
- governance still applies at the point of canonical update

### 8.3. Anti-confusion note
This sprint formalizes canonical update governance more than candidate discovery governance.

---

## 9. Canonical update boundary

### 9.1. What requires canonical governance
Examples:
- adding artifact publication into canonical Wiki
- updating canonical metadata
- updating canonical links
- marking reflected/superseded state
- adding curated reusable project knowledge
- merging/consolidating canonical objects

### 9.2. What does not automatically require immediate canonical update
Examples:
- raw notebook discovery
- early brainstorming insight
- unreviewed hypothesis
- immature inferred relation
- unconfirmed runtime suggestion

These may remain:
- candidate
- notebook item
- backlog item
until promoted properly

---

## 10. Output-driven governance rule

### 10.1. Default rule
CR should be based primarily on:
- existing task outputs
- structured outputs already produced
- artifact understanding outputs
- existing surfaced candidates

### 10.2. No-extra-reasoning by default
AI should not create additional reasoning work just to produce a richer CR.

### 10.3. Reason
This reduces:
- cost
- unnecessary synthesis
- risk of overextending beyond grounded project outputs

---

## 11. Project profile interaction
The project may define:
- deliverable vs working artifact
- wiki-eligible vs not
- what kinds of artifacts should normally be added to Wiki
- what should remain working-only

Governance should respect this project profile.

### Example
- deliverable + wiki-eligible:
  AI should suggest add-to-wiki in AIP-driven flow
- working-only artifact:
  AI should skip the add-to-wiki suggestion

---

## 12. Minimal decision rules

### Rule A
A candidate may be useful without being canonical-ready.

### Rule B
Canonical update should not happen without CR.

### Rule C
Canonical update should not happen without wiki manager request.

### Rule D
AIP-driven flows may specify clearer update obligations than non-AIP flows.

### Rule E
Outside AIP, AI may suggest candidate, but sprint does not formalize the full upstream process.

### Rule F
If source basis is insufficient, AI should draft conservatively or request more information instead of applying risky canonical change.

---

## 13. Lightweight governance states
Minimal states useful in this sprint:

### Candidate states
- `surfaced`
- `parked`
- `promoted_to_cr`
- `dropped`

### CR states
- `draft`
- `proposed`
- `approved_for_ai_update`
- `applied`
- `rejected`
- `superseded`

These are enough for this sprint without adding workflow complexity.

---

## 14. Minimal examples

### 14.1. Example — candidate only
A review task surfaces a useful linkage between BD and DD.
AI suggests it as a linkage candidate.
It is not yet canonical.

### 14.2. Example — candidate promoted to CR
Wiki manager decides the linkage is reusable enough.
A CR is created.
AI later updates canonical Wiki based on the approved CR.

### 14.3. Example — not canonical-ready
A brainstorming session discovers a possibly useful insight.
AI suggests it as a candidate.
It stays as notebook/backlog material until someone decides it is mature enough for CR.

---

## 15. Relationship with other sprint artifacts
This rule is intended to work with:
- `WIKI_CHANGE_REQUEST_SPEC`
- `AIP_WIKI_INTEGRATION_SPEC`
- `WIKI_META_INDEX_SPEC`
- `TASK_LENS_AND_WIKI_KNOWLEDGE_PROFILE_BOUNDARY_NOTE`
- future maintenance/update guidelines

---

## 16. Out of scope for this sprint
- multi-role approval chain
- vote-based approval
- automated state transition engine
- UI-based governance tooling
- access control matrix
- policy engine for dynamic permissions

---

## 17. Completion criteria for BL-07
BL-07 is considered done when:
- minimal governance scope is clearly defined
- roles are clearly defined
- candidate → CR → canonical update flow is clearly defined
- AIP vs non-AIP treatment is clearly distinguished
- output-driven/no-extra-reasoning governance principle is clearly captured
