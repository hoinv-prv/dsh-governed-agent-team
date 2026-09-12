# Methodology Design for AI Work System MVP
Version: 1.0  
Status: Draft for use as official Methodology Design baseline  
Phase: Methodology Design  
Scope: MVP (Wiki-first, no SeedPath)

---

# 1. Mục đích tài liệu

Tài liệu này định nghĩa **phương pháp luận thiết kế và vận hành tài liệu/process** cho **AI Work System MVP**.

Tài liệu **không** đi sâu vào kiến trúc kỹ thuật chi tiết của hệ thống.  
Thay vào đó, tài liệu này trả lời các câu hỏi:

- MVP sẽ được thiết kế qua những phase nào
- boundary của từng phase là gì
- những loại artifact nào tồn tại trong hệ thống
- vai trò và thứ tự ưu tiên của các artifact đó là gì
- AI sẽ được dùng như thế nào trong từng phase
- một task sẽ được AI xử lý theo phương pháp nào
- SOP, AI Work Contract, AIP, Playbook, Skill, Wiki, Workspace liên hệ ra sao
- rule review / approval / traceability như thế nào
- khi nào phase Methodology Design được coi là hoàn thành

Tài liệu này là **input chính thức** cho các phase:
- Conceptual Design
- Architecture Design
- Basic Design
- Detail Design

---

# 2. Bối cảnh và phạm vi MVP

## 2.1. Bối cảnh

AI Work System là hệ thống giúp AI hỗ trợ công việc theo cách có tổ chức, có tri thức, có quy trình, và có khả năng tích lũy dần.

Tuy nhiên, ở giai đoạn MVP, mục tiêu không phải xây toàn bộ hệ thống hoàn chỉnh, mà là xây một mô hình đủ thực dụng để AI có thể bắt đầu làm việc hiệu quả với người dùng trong khuôn khổ SOP và tài liệu chuẩn.

## 2.2. Định hướng của MVP

MVP được chốt theo hướng:

**Contract-driven, SOP-guided, AIP-directed, Wiki-first, Workspace-based AI collaboration model**

Điều này có nghĩa là:

- AI làm việc trong khuôn khổ SOP chung của tổ chức / BrSE
- AI cộng tác với người dùng theo AI Work Contract
- task cụ thể được định hướng bằng AIP
- tri thức ưu tiên lấy từ Wiki
- task phức tạp được externalize ra Workspace
- Queue và Capture Inbox được dùng để hỗ trợ working memory và curation
- long-term knowledge không được update trực tiếp trong khi task đang chạy

## 2.3. In-scope của MVP

MVP bao gồm:

- SOP
- AI Work Contract
- AIP_PLAN
- AIP_EXEC
- optional AIP_LOCAL
- core Modes
- core Playbooks / Guidelines
- Skills
- Wiki
- Workspace
- Investigation Queue
- Capture Inbox
- manual / semi-manual curation flow

## 2.4. Out-of-scope của MVP

MVP chưa bao gồm:

- SeedPath
- structural graph engine
- auto fill-back trực tiếp
- advanced orchestration
- advanced prioritization/scoring
- multi-agent coordination nặng
- structural auto-discovery mạnh
- advanced memory eviction / ranking logic

---

# 3. Nguyên tắc phương pháp luận

## 3.1. SOP-first

SOP là **quy trình chuẩn của BrSE / con người / tổ chức**.  
AI phải làm việc phù hợp với SOP đó, không được xem như một actor có quy trình riêng tách rời tổ chức.

## 3.2. Contract-driven collaboration

AI Work Contract định nghĩa **cách AI cộng tác với người dùng trong khuôn khổ SOP**.

## 3.3. AIP-directed execution

Task cụ thể phải được định hướng bằng AIP, không chỉ bằng chat.

## 3.4. Wiki-first knowledge usage

Khi cần tri thức, AI ưu tiên đọc Wiki trước khi đọc raw/canonical docs khi phù hợp.

## 3.5. Workspace for complex tasks

Task phức tạp không nên chỉ sống trong chat/context.  
Phải có Workspace để externalize working memory.

## 3.6. Queue for multi-step reasoning

Task nhiều bước phải chia nhỏ qua Investigation Queue.

## 3.7. Capture first, curate later

Discovery mới không được auto-fill-back ngay vào long-term knowledge.  
Phải đi qua:
**Capture → Triage → Organize → Promote / Archive / Discard**

## 3.8. Human-approved curation

Trong MVP, AI có thể đề xuất triage nhưng con người là người chốt việc promote chính thức.

## 3.9. Minimal active context

Hot context của AI phải nhỏ.  
Chỉ giữ phần thật sự cần cho reasoning hiện tại.

## 3.10. Traceability by default

Các quyết định, plan, discoveries, updates quan trọng phải có khả năng trace ngược về task/source/AIP khi cần.
# 6. Artifact hierarchy

## 6.1. Thứ tự ưu tiên artifact

Thứ tự ưu tiên artifact trong MVP được chốt như sau:

**SOP → AI Work Contract → AIP_PLAN / AIP_EXEC → Applicable Guidelines / Playbooks → Skills → Wiki → Workspace**

## 6.2. Ý nghĩa của từng artifact

### SOP
Quy trình chuẩn của BrSE / con người / tổ chức.

### AI Work Contract
Quy định cách AI cộng tác trong SOP đó.

### AIP_PLAN
Plan để điều tra, phân tích, design, scope, review planning, task breakdown.

### AIP_EXEC
Plan để thực thi, review thật, update artifact thật, organize thật.

### Applicable Guidelines / Playbooks
Phương pháp reusable cho từng loại step/case.

### Skills
Gói hướng dẫn tác vụ nhỏ giúp AI thực hiện một step cụ thể ổn định hơn.

### Wiki
Curated knowledge mà AI nên ưu tiên đọc trước.

### Workspace
Working memory externalized cho task hiện tại.

## 6.3. Nguyên tắc dùng artifact

- Artifact cấp trên không bị artifact cấp dưới ghi đè
- Task phải bám SOP / Contract / AIP trước khi mở rộng sang execution details
- Workspace chỉ là nơi thực thi, không phải nơi đặt luật chơi

---

# 7. Document taxonomy cho MVP

## 7.1. Governance / Operating docs
- SOP
- AI Work Contract

## 7.2. Execution control docs
- AIP_PLAN
- AIP_EXEC
- optional AIP_LOCAL

## 7.3. Procedural docs
- mode specs
- playbooks
- workspace model
- queue rules
- capture & triage rules
- wiki authoring guideline

## 7.4. Skill docs
- skills for reading wiki
- skills for queue handling
- skills for synthesis
- skills for writing outputs
- skills for capture/triage support

## 7.5. Knowledge docs
- wiki glossary
- domain wiki
- function wiki
- reusable Q&A / pattern docs

## 7.6. Runtime docs
- task workspace files
- queue
- findings
- open questions
- draft output
- inbox
- history

## 7.7. Design docs
- conceptual design
- architecture design
- basic design
- detail design

---

# 8. AI usage rules by phase

## 8.1. BrainStorming
AI có thể:
- mở ý tưởng
- so sánh option
- thử simulation
- gợi ý concept

AI không được:
- tự chốt long-term knowledge chính thức
- tự override SOP/process

## 8.2. Methodology Design
AI có thể:
- structure phases
- đề xuất artifact hierarchy
- gợi ý rules / boundaries / flow
- draft methodology docs

AI không được:
- tự thay SOP của tổ chức
- tự chốt rule trái với governance thực tế của công ty

## 8.3. Conceptual / Architecture / Basic / Detail Design
AI có thể:
- draft documents
- review consistency
- detect missing points
- suggest refinements

AI không được:
- tự thay approval của con người
- tự promote design decisions thành official truth mà không review

---

# 9. AIP methodology

## 9.1. Định nghĩa
**AIP = AI Implementation Plan**

AIP là execution control artifact mô tả cách thực hiện một task hoặc một nhóm task với AI.

## 9.2. AIP types cho MVP
- `AIP_PLAN`
- `AIP_EXEC`
- optional `AIP_LOCAL`

*(AIP_ROOT retired 2026-07-13 — CR-AIWS-2026-07-026; project context sống trong SOP_MASTER. Xem AIP_Detail_Spec §3.1.)*

## 9.3. AIP vs Mode
- **AIP type** = phase / control intent
- **Mode** = reasoning posture

## 9.4. Vai trò của từng AIP type

### AIP_PLAN
Dùng cho:
- investigation
- planning
- design
- scope clarification
- review planning
- task breakdown

### AIP_EXEC
Dùng cho:
- execution
- actual review
- actual update
- actual organize / finalize output

### AIP_LOCAL
- optional
- local/private execution notes

## 9.5. AIP step structure

Mỗi step trong AIP nên có tối thiểu:

- Objective
- Recommended Mode
- Applicable Guidelines
- optional Recommended Skills
- Inputs
- Expected Outputs
- Done Condition
- Notes / Constraints
- optional Workspace Actions

## 9.6. AIP_PLAN → AIP_EXEC handoff
AIP_PLAN phải tạo ra output đủ để AIP_EXEC dùng được, ví dụ:
- scope
- assumptions
- references
- task steps
- check items
- open questions
- done criteria

AIP_EXEC phải trace được ngược về AIP_PLAN khi cần.

---

# 10. Mode and Guideline methodology

## 10.1. Core modes cho MVP
- BrainStorming
- Research
- Planning
- Executing
- Reviewing
- Organizing

## 10.2. Mode purpose
Mode chỉ định AI nên suy nghĩ/làm việc theo kiểu nào trong bước hiện tại.

## 10.3. Applicable Guidelines
Mỗi step có thể tham chiếu:
- playbooks
- queue rules
- workspace rules
- triage rules
- wiki guidelines

## 10.4. Skills
Skills là execution support artifacts.  
Chúng không thay Playbooks, mà giúp AI thực hiện step cụ thể ổn định hơn.

---

# 11. Workspace methodology

## 11.1. Khi nào phải có workspace
Một task phải có workspace nếu có ít nhất một trong các điều kiện sau:

- cần nhiều hơn 1 source chính
- có nhiều bước reasoning
- có dependency / scope decision
- cần output có cấu trúc
- có khả năng resume / handoff
- cần queue hoặc capture inbox

## 11.2. Vai trò của workspace
Workspace là nơi:
- giữ working memory
- giữ queue
- giữ findings
- giữ open questions
- giữ draft
- giữ capture inbox
- giúp AI không phụ thuộc hoàn toàn vào chat

## 11.3. Kỷ luật dùng workspace
- file phải có mục đích rõ
- discoveries phải ghi đúng vùng
- findings cần compact định kỳ
- workspace không phải long-term knowledge chính thức

---

# 12. Queue methodology

## 12.1. Định nghĩa
Investigation Queue là task-scoped frontier để chia nhỏ investigation/execution nhiều bước.

## 12.2. Quy tắc dùng queue
- item phải nhỏ và rõ
- item phải có priority/status
- queue chỉ giữ việc còn cần cho task hiện tại
- discovery cho tương lai mà chưa cần ngay → vào capture inbox, không vào queue

## 12.3. Queue lifecycle
- queued
- in_progress
- done
- blocked
- discarded

## 12.4. Synthesis checkpoint
Phải có checkpoint khi:
- queue phình lớn
- findings quá dài
- đã xong một subtopic
- context bắt đầu loãng

Tại checkpoint:
- merge findings
- remove obsolete items
- reprioritize queue
- compact current understanding

---

# 13. Capture / Curation methodology

## 13.1. Vai trò của Capture Inbox
Dùng để giữ các discovery:
- có thể hữu ích
- chưa cần ngay trong bước hiện tại
- chưa đủ rõ để promote ngay
- chưa có thời gian organize ngay

## 13.2. Flow chuẩn
**Capture → Triage → Organize → Promote / Archive / Discard**

## 13.3. Rule cho MVP
- AI có thể capture và đề xuất triage
- con người quyết định promote chính thức
- không auto-update long-term knowledge

## 13.4. Triage outcomes
- promote to wiki
- promote to procedural docs / playbooks
- archive as history
- discard

---

# 14. Wiki methodology

## 14.1. Wiki-first
AI ưu tiên đọc Wiki trước khi đọc raw/canonical docs khi phù hợp.

## 14.2. Khi nào đọc canonical docs
- khi Wiki chưa đủ
- khi cần verify
- khi cần source-of-truth

## 14.3. Rule khi Wiki và source khác nhau
- note uncertainty
- hoặc tạo candidate update
- không tự ý sửa long-term knowledge ngay trong task

## 14.4. Minimum structure cho wiki entry quan trọng
- purpose
- scope
- key situations/events
- related functions
- upstream/downstream hints
- canonical references
- recommended next reads
- review hints nếu có

---

# 15. Review / Approval methodology

## 15.1. AI can draft
AI có thể draft:
- design docs
- AIP
- wiki candidates
- review plans
- structured notes

## 15.2. Human approves official updates
Con người review/approve:
- official long-term knowledge updates
- official methodology/docs updates
- official design decisions

## 15.3. Review checkpoints
Review tối thiểu tại:
- cuối mỗi design phase
- trước khi promote long-term knowledge
- trước khi coi AIP_EXEC là done nếu task quan trọng

---

# 16. Traceability methodology

## 16.1. Trace between phases
- outputs của phase trước phải trace được sang inputs của phase sau

## 16.2. Trace between AIP and execution
- workspace trace về active AIP
- AIP_PLAN outputs trace sang AIP_EXEC inputs

## 16.3. Trace for knowledge updates
- capture candidates trace về task/source gốc
- proposed wiki/procedural update trace về evidence

## 16.4. Trace for conclusions
- review plans, findings, decisions nên trace được về references đã dùng khi cần
# 19. Kết luận

Methodology Design cho MVP chốt rằng AI Work System MVP sẽ vận hành theo cách:

- bám SOP của tổ chức
- dùng AI Work Contract như working agreement
- dùng AIP làm execution control artifact
- dùng Guidelines / Playbooks / Skills để hỗ trợ step-level execution
- dùng Wiki làm curated knowledge chính
- dùng Workspace / Queue / Capture Inbox cho working memory và curation
- dùng con người làm approval point cho long-term updates

Tài liệu này là baseline methodology chính thức để bước sang:
- Conceptual Design
- Architecture Design
- Basic Design
- Detail Design

---

# 20. Frozen additions — Stable AIP and Active Step Context

Phần này bổ sung và freeze các quyết định đã chốt sau BrainStorming, và được xem là một phần chính thức của Methodology Design cho MVP.

## 20.1. Stable AIP rule

AIP là **stable execution control artifact**.

Điều này có nghĩa là:

- AIP không phải working notebook
- AIP không phải nơi cập nhật findings liên tục
- AIP không phải nơi giữ queue/runtime state
- AIP không nên bị sửa ở mỗi bước thực thi

### Mặc định
AIP được xem là **ổn định** trong suốt quá trình làm task.

### Chỉ update AIP khi có thay đổi thật sự ở mức macro, ví dụ:
- objective thay đổi
- scope / non-scope thay đổi
- expected outputs thay đổi
- step lớn cần re-plan
- assumption nền bị thay đổi

### Không update AIP chỉ vì:
- có findings mới
- queue item mới xuất hiện
- open questions phát sinh
- draft output thay đổi
- step state thay đổi

**Freeze conclusion:**  
AIP update by exception, not by default.

---

## 20.2. Do not read full AIP at every step

AI **không cần** đọc lại toàn bộ AIP ở mỗi step.

### Rule
- lúc bắt đầu task hoặc cần re-orient: đọc AIP overview / relevant step
- trong lúc thực thi từng step: ưu tiên đọc **Active Step Context**
- chỉ quay lại full AIP khi:
  - chuyển step lớn
  - checkpoint quan trọng
  - scope thay đổi
  - cần re-orient toàn cục

**Freeze conclusion:**  
AIP là master plan, không phải file phải nạp lại đầy đủ ở mọi bước.

---

## 20.3. Active Step Context

Để AI không phải đọc full AIP mỗi lần, mỗi step nên có một artifact runtime gọi là:

**Active Step Context**

Có thể xem đây là:
- runtime slice của AIP cho step hiện tại
- step packet nhỏ, đủ để AI tập trung
- bridge giữa AIP và Workspace

### Vai trò
Active Step Context giúp AI biết:
- step hiện tại là gì
- objective của step
- recommended mode
- applicable guidelines
- recommended skills
- relevant inputs
- relevant findings / queue items / open questions
- done condition của step

### Kết luận
- AIP = macro execution plan
- Active Step Context = runtime step packet
- Workspace = nơi lưu execution state

---

## 20.4. Materialize Active Step Context with skill + script

Việc tạo Active Step Context **không nên phụ thuộc hoàn toàn vào reasoning của LLM**.

Ưu tiên cách làm:

**AIP → deterministic skill/script → Active Step Context**

### Skill
Skill định nghĩa:
- Active Step Context cần có những phần nào
- lấy từ AIP / Workspace như thế nào
- cách map fields ổn định

### Script
Script thực hiện phần máy móc:
- đọc AIP
- xác định current step
- lấy metadata của step
- gom references, queue items, findings, open questions liên quan
- tạo file Active Step Context

### Lợi ích
- giảm token
- giảm nhiễu
- giảm sai lệch do mỗi lần LLM tự hiểu khác nhau
- giữ AIP sạch và ổn định
- giúp resume/handoff tốt hơn

**Freeze conclusion:**  
Việc materialize step context nên ưu tiên làm bằng skill + script deterministic.

---

## 20.5. Current step pointer

Để materialize Active Step Context mà không cần suy luận lại step hiện tại, nên có một cơ chế pointer đơn giản, ví dụ:

- current step metadata
- active step id
- current AIP reference

Methodology Design chưa chốt schema chi tiết, nhưng chốt rằng:

- hệ thống runtime/workspace nên biết step nào đang active
- Active Step Context được sinh từ step active đó
- việc xác định active step không nên phụ thuộc vào việc LLM đọc toàn bộ AIP mỗi lần

---

## 20.6. Active Step Context belongs to Workspace

Active Step Context là artifact runtime, vì vậy nó thuộc **Workspace**, không thuộc AIP gốc.

### Ý nghĩa
- AIP giữ tính ổn định
- Workspace giữ execution state
- Active Step Context nằm ở phía Workspace như một artifact active

Ví dụ ở mức methodology, Workspace có thể có:
- task brief
- active AIP reference
- active step context
- queue
- findings
- open questions
- draft output
- capture inbox

Methodology Design **không** chốt file name cụ thể ở đây, nhưng chốt vai trò logic này.

---

## 20.7. AIP step fields should be machine-friendly enough

Để skill/script có thể materialize Active Step Context, mỗi step trong AIP phải có cấu trúc đủ ổn định.

Ngoài các field đã chốt trước đó, step nên đủ machine-friendly để parse và map ra runtime packet.

### Step fields đã freeze
- Objective
- Recommended Mode
- Applicable Guidelines
- optional Recommended Skills
- Inputs
- Expected Outputs
- Done Condition
- Notes / Constraints
- optional Workspace Actions

**Freeze conclusion:**  
AIP có thể ở dạng markdown, nhưng phải đủ structured để được machine-assisted materialization.

---

## 20.8. Update to workspace methodology

Bổ sung cho mục Workspace methodology:

### Workspace should support active step execution
Workspace không chỉ giữ working memory tổng quát, mà còn phải hỗ trợ:
- active step execution
- step-local focus
- step-local queue/findings/questions

### Step execution should be small and focused
AI nên làm việc theo:
- active step context
- current queue items
- relevant findings only

thay vì giữ toàn bộ AIP và toàn bộ workspace trong context.

---

## 20.9. Update to skills methodology

Bổ sung cho Skills:

Trong MVP, nên cân nhắc có các skill thuộc nhóm:
- generate active step context
- execute current step from step context
- run synthesis checkpoint
- advance step / switch step
- capture step-level discoveries

Các skill này được xem là **execution support skills**, không thay thế AIP hay Playbook.

---

## 20.10. Methodology freeze

Các điểm sau được freeze chính thức:

1. AIP là stable execution control artifact  
2. AIP không cần được đọc full ở mỗi step  
3. Mỗi step nên có Active Step Context trong Workspace  
4. Active Step Context nên được materialize bằng skill + script deterministic  
5. Runtime state sống trong Workspace, không sống trong AIP  
6. AIP step structure phải đủ machine-friendly để hỗ trợ materialization  
7. Chỉ update AIP khi có thay đổi macro, không update mặc định trong runtime

---

# Sprint methodology addendum — one concept or feature per sprint

For future AI Work System refinement, each sprint should focus on **one concept or one feature**.

The sprint should first define:
- why the concept/feature matters
- what scope is needed to make it sufficiently mature
- what is in scope
- what is out of scope
- what is deferred

Only after the concept/feature is sufficiently mature should the project move to the next sprint.

When the major MVP concepts/features are sufficiently mature, a later balancing sprint may review the full system and add small adjustments for overall consistency.

This rule is intended to prevent scope drift and reduce the risk of mixing partially mature concepts into the canonical design.

---

# Personal Notebook methodology addendum

## Runtime use

Personal Notebook may support continuity across tasks/sprints by storing selected personal notes and cross-task findings.

AI should read it only when HUMAN asks or when the task clearly requires personal/cross-task notes and local setup permits it.

AI should write/update it only when HUMAN asks or confirms.

## Note handling

Notebook notes should preserve:
- status
- authority
- source
- intended use
- review needed flag when useful

Personal Notebook should not become a dumping ground. It should be reviewed, compacted, archived, or discarded lightly as needed.

## Controlled capture

Reusable-looking notes should be marked as capture candidates first.

Promotion into Knowledge Hub requires controlled capture.

---

# Source Understanding Artifact methodology addendum

## When to create

Create a Source Understanding Artifact when:
- a source is reused often
- a source is long or complex
- source understanding should be preserved
- repeated raw/source reopening is costly
- provenance and verification path can be recorded

Do not create it when:
- source is small and easy to read
- source is used only once
- source unit is unclear
- note is merely personal or task-bound

## Safe usage

Use Source Understanding Artifact for high-level understanding, source triage, review viewpoint brainstorming, and testcase idea generation.

Use raw/source for exact wording, final decisions, source evidence, implementation detail, and freshness verification.

---

# Task Lens runtime methodology addendum

Task Lens is optional routing support.

Use Task Lens when it improves knowledge routing and HUMAN-AI alignment.

Use No-Lens / AI-decides-search-scope when explicit lens may reduce output quality or narrow search incorrectly.

Runtime stance:
- clarify intent first
- use or skip explicit lens depending on quality impact
- allow HUMAN runtime lens adjustment
- allow AI lens expansion
- preserve raw/source verification
- preserve Working AIP guardrail

---

# Controlled Knowledge Promotion methodology addendum

Controlled Knowledge Promotion is added as an MVP runtime/methodology flow.

Core stance:
```text
Knowledge Hub is for AI runtime value.
Notebook can store any.
Candidate can be broad.
Wiki requires Knowledge Value.
AI can collect/prepare candidates.
Important promotion/add/update is controlled.
Skill must use checklist before Wiki add/update.
Post-feedback lookback captures improvement value.
No auto-promotion or auto-apply-back.
Important changes are logged for review/revision/rollback.
```

Controlled Knowledge Promotion helps AIWS accumulate reusable value without turning Knowledge Hub/canonical docs/templates into noisy or unsafe stores.
