# Conceptual Design for AI Work System MVP
Version: 0.2  
Status: Refined Draft  
Phase: Conceptual Design  
Scope: MVP only

---

# 1. Mục đích tài liệu

Tài liệu này mô tả **Conceptual Design** cho **AI Work System MVP**.

Mục tiêu của tài liệu là chốt:

- AI Work System MVP là gì
- hệ thống giải quyết vấn đề gì
- các khái niệm trung tâm là gì
- các artifact chính và vai trò của chúng là gì
- AI sẽ làm việc theo flow khái niệm nào
- memory / knowledge / execution được tổ chức như thế nào ở mức khái niệm
- giới hạn của MVP nằm ở đâu

Tài liệu này **không** đi vào:
- schema chi tiết
- file format chi tiết
- API / script / implementation detail
- folder/file naming rule chi tiết
- state transition chi tiết

Các phần đó sẽ được xử lý ở các phase sau.

---

# 2. Bối cảnh và vấn đề cần giải quyết

Trong các dự án phát triển phần mềm, đặc biệt là dự án có:

- nhiều tài liệu thiết kế
- nhiều tài liệu cũ/trùng lặp
- hệ thống legacy source code lớn
- nhiều use case lặp lại
- nhiều task cần AI hỗ trợ theo quy trình công ty

AI nếu chỉ làm việc bằng hội thoại sẽ gặp các vấn đề:

- dễ mất ngữ cảnh
- khó giữ consistency giữa các task
- khó biết nên đọc tài liệu nào trước
- khó chia task phức tạp thành các bước ổn định
- khó tích lũy tri thức một cách an toàn
- dễ sinh ra **思い込み** nếu reuse answer cũ không đúng cách

AI Work System được thiết kế để giải quyết các vấn đề trên bằng một mô hình làm việc có tổ chức, có tri thức, có execution control, và có working memory externalized.

---

# 3. Mục tiêu của MVP

MVP tập trung vào một mô hình làm việc với AI theo hướng:

**Contract-driven, SOP-guided, AIP-directed, Wiki-first, Workspace-based AI collaboration model**

## Mục tiêu cụ thể của MVP

MVP cần cho phép AI:

- làm việc trong khuôn khổ SOP của BrSE / tổ chức
- cộng tác với người dùng theo AI Work Contract
- thực hiện task cụ thể theo AIP
- ưu tiên đọc Wiki trước khi đọc raw/canonical source khi phù hợp
- dùng Workspace để externalize working memory cho task phức tạp
- dùng Queue để chia nhỏ task nhiều bước
- dùng Capture Inbox để giữ discoveries chưa organize ngay được
- tích lũy tri thức có kiểm soát theo nguyên tắc capture first, curate later

## Non-goals của MVP

MVP **không** nhằm:
- xây full autonomous agent platform
- có structural graph engine như SeedPath
- tự động fill back trực tiếp vào long-term knowledge
- tự động thay con người trong việc approval hoặc canonicalization
- giải quyết toàn bộ bài toán orchestration nâng cao

---

# 4. Định nghĩa hệ thống ở mức khái niệm

## 4.1. AI Work System là gì

AI Work System là một hệ thống hỗ trợ AI và con người cùng làm việc trên cùng một task trong khuôn khổ:

- SOP chung của tổ chức
- working agreement rõ ràng
- execution plan rõ ràng
- curated knowledge có tổ chức
- runtime workspace rõ ràng

AI Work System không chỉ là knowledge base.  
Nó cũng không chỉ là một bộ prompt.

Nó là một mô hình phối hợp giữa:

- process
- execution control
- knowledge
- runtime memory
- curation

## 4.2. MVP của AI Work System là gì

Trong MVP, AI Work System được hiện thực chủ yếu bằng:

- tài liệu chuẩn
- artifact chuẩn
- workspace chuẩn
- procedural rules
- wiki-first knowledge model

MVP chưa dựa vào graph navigation engine.  
Khả năng dẫn đường của MVP chủ yếu đến từ:

- SOP
- Contract
- AIP
- Guidelines / Playbooks
- Skills
- Wiki
- Workspace

---

# 5. Các khái niệm trung tâm

## 5.1. SOP

SOP là quy trình chuẩn của BrSE / con người / tổ chức.

SOP là lớp quy định:
- cách công việc được thực hiện trong tổ chức
- phase/checkpoint/review/approval chuẩn là gì

AI không đứng ngoài SOP.  
AI phải làm việc trong khuôn khổ SOP đó.

## 5.2. AI Work Contract

AI Work Contract là working agreement giữa người dùng và AI trong khuôn khổ SOP.

Nó quy định:
- AI nên cộng tác như thế nào
- artifact precedence
- nguyên tắc dùng wiki/workspace/queue/capture
- nguyên tắc không đi lệch scope

## 5.3. AIP

AIP là **AI Implementation Plan**.

AIP là execution control artifact cho task cụ thể.

AIP định nghĩa:
- objective
- scope / non-scope
- outputs
- steps
- references
- done condition

MVP dùng:
- AIP_PLAN
- AIP_EXEC
- optional AIP_LOCAL

## 5.4. Mode

Mode là reasoning posture của AI trong bước hiện tại.

MVP dùng core modes:
- BrainStorming
- Research
- Planning
- Executing
- Reviewing
- Organizing

## 5.5. Applicable Guidelines / Playbooks

Guidelines / Playbooks là reusable methods cho từng loại step/case.

Chúng giúp AI biết:
- trong case này nên làm theo cách nào
- cần viewpoint nào
- cần output shape nào
- cần dừng khi nào

## 5.6. Skills

Skills là execution support artifacts cho tác vụ nhỏ.

Skill không thay Playbook.  
Skill giúp AI thực hiện từng step ổn định hơn.

## 5.7. Wiki

Wiki là lớp curated knowledge mà AI ưu tiên đọc trước.

Wiki không thay source code hay raw docs.  
Wiki là lớp:
- AI-friendly
- curated
- có knowledge classes
- có reading hints / canonical refs / review hints

## 5.8. Workspace

Workspace là runtime execution memory externalized cho task hiện tại.

Workspace giữ:
- active execution state
- findings
- open questions
- queue
- drafts
- capture inbox

## 5.9. Investigation Queue

Queue là task-scoped frontier giúp AI chia nhỏ task nhiều bước.

## 5.10. Capture Inbox

Capture Inbox là vùng staging cho discoveries chưa organize ngay được.

## 5.11. Active Step Context

AIP là stable macro plan.  
AI không cần đọc full AIP ở mỗi step.

Vì vậy, mỗi step có một **Active Step Context** để:
- đưa ra objective nhỏ hơn
- giữ mode/guidelines/skills cần cho step đó
- tập trung context cho AI

---

# 6. System context view

AI Work System MVP tồn tại trong bối cảnh có 3 nhóm actor / nguồn lực chính:

## 6.1. Con người / tổ chức
- định nghĩa SOP
- giao task
- review / approve
- quyết định canonicalization / promotion

## 6.2. AI
- làm việc theo Contract
- thực hiện task theo AIP
- đọc Wiki
- dùng Workspace
- tạo discoveries / candidates / draft outputs

## 6.3. Project assets
- source code
- design docs
- canonical documents
- wiki entries
- workspace artifacts
- history/evidence trail

### Conceptual relationship
- Con người và tổ chức định nghĩa **luật chơi**
- AI hoạt động **trong luật chơi đó**
- project assets là **nguồn để AI đọc, reason, và tạo output**
- AI Work System là lớp giúp kết nối ba thứ này một cách có tổ chức

---

# 7. Conceptual layers of the system

## 7.1. Tầng quy tắc và điều hành

Tầng này trả lời:
- tổ chức làm việc thế nào
- AI tham gia thế nào
- task cụ thể được chỉ đạo thế nào

Artifacts chính:
- SOP
- AI Work Contract
- AIP_PLAN
- AIP_EXEC

### Nature
- tương đối ổn định
- điều khiển execution
- không nên thay đổi liên tục trong runtime

---

## 7.2. Tầng phương pháp và hỗ trợ thực thi

Tầng này trả lời:
- AI nên suy nghĩ theo posture nào
- trong step này nên dùng phương pháp nào
- skill nào nên dùng để thực thi ổn định

Artifacts chính:
- Modes
- Guidelines / Playbooks
- Skills

### Nature
- reusable
- method-oriented
- hỗ trợ execution, không thay execution control

---

## 7.3. Tầng tri thức

Tầng này trả lời:
- AI đã biết gì
- cái gì là authoritative
- cái gì là curated
- cái gì chỉ là guidance
- cái gì chỉ là history

Artifacts chính:
- Wiki-centered knowledge
- canonical references
- history / evidence trail

### Nature
- cung cấp understanding
- không trực tiếp giữ runtime state
- được cập nhật có kiểm soát

---

## 7.4. Tầng runtime execution

Tầng này trả lời:
- task đang chạy ra sao
- AI đang làm step nào
- findings / queue / open questions hiện tại là gì

Artifacts chính:
- Workspace
- Active Step Context
- Investigation Queue
- Findings
- Open Questions
- Draft Output
- Capture Inbox

### Nature
- dynamic
- step-local
- task-local
- có thể thay đổi liên tục trong runtime

---

# 8. Artifact precedence ở mức khái niệm

MVP dùng thứ tự ưu tiên artifact như sau:

**SOP → AI Work Contract → AIP_PLAN / AIP_EXEC → Applicable Guidelines / Playbooks → Skills → Wiki → Workspace**

## Ý nghĩa của precedence này

### SOP
là chuẩn gốc của tổ chức

### AI Work Contract
định nghĩa AI làm việc thế nào trong chuẩn đó

### AIP
định nghĩa task cụ thể sẽ được triển khai ra sao

### Guidelines / Playbooks
định nghĩa phương pháp reusable cho step/case

### Skills
giúp execution ổn định ở mức vi mô

### Wiki
cung cấp tri thức curated để đọc nhanh

### Workspace
là nơi task đang thực sự được thực hiện

Conceptual meaning:
- Workspace không được override SOP/Contract/AIP
- Wiki không thay Contract/AIP
- Skills không thay Playbook
- Playbook không thay AIP

---

# 9. Core task flow view

## 9.1. Happy path for a complex task

Flow khái niệm chuẩn của một task phức tạp trong MVP là:

1. **Task enters SOP context**  
   Công việc được hiểu trong khuôn khổ SOP của tổ chức

2. **AI follows AI Work Contract**  
   AI biết cách cộng tác với người dùng trong SOP đó

3. **AI loads task execution control**  
   AIP_PLAN hoặc AIP_EXEC cung cấp control cho task hiện tại (bối cảnh project: SOP_MASTER §1–2 — đã đọc ở bước 1)

4. **Current step is materialized**  
   Step hiện tại được tạo thành Active Step Context

5. **AI selects posture and method**  
   AI dùng Recommended Mode  
   AI tham chiếu Applicable Guidelines / Skills cần thiết

6. **AI reads knowledge**  
   AI ưu tiên đọc Wiki  
   Khi cần thì quay lại canonical refs / source

7. **AI executes in Workspace**  
   AI cập nhật:
   - Queue
   - Findings
   - Open Questions
   - Draft Output
   - Capture Inbox

8. **AI performs synthesis when needed**  
   Nếu task dài / queue lớn / context loãng, AI chạy synthesis checkpoint

9. **Task produces output and curation candidates**  
   Task kết thúc với:
   - output cuối
   - discoveries / candidates cho curation/backfill

## 9.2. Smaller task path

Task nhỏ có thể đi theo flow ngắn hơn:

1. chọn mode  
2. đọc wiki tối thiểu  
3. trả lời trực tiếp  

Không nhất thiết cần full workspace.

---

# 10. Conceptual memory model

## 10.1. Hot Context Cache

Phần nhỏ nhất, active nhất, nằm trong context reasoning hiện tại của AI.

### Nature
- rất nhỏ
- chỉ phục vụ step hiện tại
- thường là distilled understanding

## 10.2. Working Memory

Trong MVP, Working Memory được externalize ra Workspace.

Chứa:
- Active Step Context
- Queue
- Findings
- Open Questions
- Draft Output
- Capture Inbox
- History

### Nature
- dynamic
- task-local
- execution-local

## 10.3. Knowledge Store

Trong MVP, Knowledge Store là mô hình **wiki-centered**:
- Wiki là trung tâm curated knowledge
- Source of Truth và History / Evidence Trail liên kết chặt với Wiki, nhưng không đồng nhất với Curated Wiki entries

### Nature
- tương đối ổn định
- không phải runtime notebook
- được curate có kiểm soát

---

# 11. Conceptual Wiki model

## 11.1. Wiki entry model

MVP dùng **hybrid wiki entry model**:
- một core template chung
- sections mở rộng theo loại entry

Taxonomy tối thiểu:
- Domain
- Function
- Module / Component
- Data / Table
- Pattern / Guidance

## 11.2. Knowledge classes

MVP dùng 4 knowledge classes:

- Source of Truth
- Curated Knowledge
- Reference / Guidance
- History / Evidence Trail

## 11.3. Use rules

- Source of Truth → authoritative
- Curated Knowledge → verify_when_decision_matters
- Reference / Guidance → verify_before_use
- History / Evidence Trail → historical_only

## 11.4. Truth / Wiki / History conceptual roles

### Truth
- authoritative
- canonical
- highest-priority reference for decisions

### Wiki
- curated + guidance-centric
- fastest reading layer for AI
- optimized for understanding and navigation hints

### History
- trail of past work / evidence / candidates
- useful for audit, resume, later curation
- not a primary truth layer

## 11.5. Wiki-first meaning in MVP

AI nên:
1. đọc Source of Truth / Contract / AIP nếu liên quan  
2. đọc Curated Knowledge để hiểu nhanh  
3. đọc Reference / Guidance để có hint / next reads  
4. chỉ tra History / Evidence Trail khi cần tra cứu hoặc curate

---

# 12. Conceptual backfill / curation flow view

## 12.1. Backfill in MVP

Backfill có trong MVP, nhưng chỉ theo hướng:
**controlled / semi-manual backfill**

## 12.2. Flow

**Task execution → discoveries / candidate signals → Capture Inbox / History → Triage → Organize → Promote / Archive / Discard**

## 12.3. Promotion direction

### Not default
- không đi thẳng vào Source of Truth

### Common destinations
- Curated Knowledge
- Reference / Guidance
- History / Evidence Trail

### Safety rules
- nếu còn phân vân giữa Curated và Reference → ưu tiên Reference
- nếu còn phân vân giữa Curated và Source of Truth → ưu tiên Curated

## 12.4. Conceptual role of Capture Inbox

Capture Inbox là lớp đệm giúp:
- không mất discoveries
- không làm bẩn long-term knowledge ngay
- hỗ trợ curation có kiểm soát

---

# 13. Conceptual Wiki update model

## 13.1. Wiki update is controlled execution

Trong MVP, cập nhật Wiki được xem là một task thực thi có kiểm soát.

## 13.2. High-level flow

1. Detect mismatch / improvement opportunity  
2. Create update candidate  
3. Triage  
4. If needed, create/update AIP-EXEC  
5. Build Active Step Context for wiki update  
6. Draft update  
7. Human review / approval  
8. Apply official update  
9. Record provenance

## 13.3. Why this matters conceptually

Điều này đảm bảo:
- AI có thể tích lũy tri thức
- nhưng không silently rewrite truth
- giảm rủi ro stale summary hoặc 思い込み

---

# 14. Conceptual staleness model

## 14.1. Wiki entries may become stale

Vì source/canonical docs có thể thay đổi, wiki entry không được giả định là luôn mới.

## 14.2. Minimal status model for MVP

- active
- needs_review

## 14.3. Conceptual meaning

- active: hiện có thể dùng theo use_rule của knowledge class
- needs_review: vẫn có thể đọc để định hướng, nhưng phải verify mạnh hơn nếu task quan trọng

---

# 15. Conceptual lint model

## 15.1. Role of lint in MVP

Lint trong MVP là guardrail cho:
- structure
- references
- metadata
- light consistency

Lint không thay review nội dung.

## 15.2. Default lint posture

MVP mặc định dùng:
- structural lint
- reference lint
- metadata lint

Option semantic nhẹ chỉ bật khi user yêu cầu rõ ràng cho case cụ thể.

---

# 16. Deploy concept for software projects

Khi dùng trong dự án phần mềm, toàn bộ artifact của AI Work System MVP phải nằm trong một thư mục riêng ở project root.

Thư mục gốc khuyến nghị:
- `.ai-work/`

Bên trong, knowledge packaging theo hướng:
- `/truth/`
- `/wiki/`
- `/history/`

Ý nghĩa:
- không làm bẩn source/business folders
- AI artifacts được quản lý tập trung
- knowledge zones rõ ràng hơn

---

# 17. Conceptual boundaries of MVP

## MVP intentionally does not include
- SeedPath
- structural graph navigation
- automated truth update
- strong autonomous orchestration
- heavy multi-agent logic

## MVP intentionally focuses on
- process clarity
- execution control
- wiki-first knowledge use
- workspace-based execution
- safe curation

---

# 18. Kết luận

AI Work System MVP là một mô hình cộng tác với AI trong đó:

- SOP cung cấp quy trình chuẩn của tổ chức
- AI Work Contract định nghĩa cách AI tham gia vào quy trình đó
- AIP điều hướng task cụ thể
- Modes / Guidelines / Skills hỗ trợ execution từng bước
- Wiki cung cấp curated knowledge để AI đọc trước
- Truth cung cấp lớp authoritative
- History giữ trail và candidate
- Workspace externalize working memory cho task phức tạp
- Queue và Active Step Context giúp AI làm việc từng bước nhỏ, tập trung
- Capture Inbox và curation flow cho phép tích lũy tri thức có kiểm soát

Conceptual Design này xác định **AI Work System MVP là gì** và **các khối khái niệm chính liên hệ với nhau ra sao**, làm nền cho Architecture Design và các phase tiếp theo.
