# Architecture Design for AI Work System MVP
Version: 0.5  
Status: Canonical merged baseline through current point  
Phase: Architecture Design  
Scope: MVP current canonical baseline

---

# 1. Purpose

Tài liệu này mô tả phần **canonical Architecture Design** cho AI Work System v1.0+ current canonical baseline.

Mục tiêu của tài liệu là:
- cập nhật kiến trúc theo mô hình mới đã được chốt
- làm rõ:
  - **AI / HUMAN là actors**
  - **component set chính thức ở current level**
  - **trách nhiệm của từng component**
  - **artifact ownership**
  - **interaction giữa actors và components**
- loại bỏ cách hiểu dễ gây nhầm rằng:
  - AIP là process component
  - có một Orchestrator như process component riêng của hệ thống

Lưu ý:
- tài liệu này mô tả **logical architecture**
- không đi sâu vào exact schema, exact UI, hay implementation details
# 3. Actor model

## 3.1. AI as primary execution actor
AI là actor chính chịu trách nhiệm:
- hiểu task
- tham khảo tri thức
- chọn và tạo AIP phù hợp
- dùng AIP để thực thi công việc
- gọi Skills khi cần capability
- tương tác với Workspace trong task hiện tại

AI không phải component.
AI là actor sử dụng các component của hệ thống để làm việc.

## 3.2. HUMAN as supervisory / decision actor
HUMAN là actor:
- kiểm tra
- confirm
- giới hạn scope
- ra quyết định ở các gate quan trọng

HUMAN không làm thay AI mọi bước.
Vai trò của HUMAN là:
- kiểm soát điểm quan trọng
- tránh lệch hướng
- đảm bảo kết quả nằm trong phạm vi mong muốn

## 3.3. Actor-governance relationship
AI Work System được thiết kế theo tinh thần:
- phát huy tối đa năng lực của AI
- nhưng các quyết định quan trọng là do HUMAN

Khi AI cần HUMAN confirm, AI phải nêu:
- lý do
- rủi ro

---

# 4. Official components at current level

Current official components of AI Work System at this level are:

1. **Workspace**
2. **Knowledge Hub**
3. **AIP**
4. **SeedPath**
5. **Skills**

In addition:
- **SOP** thuộc **governance layer**
- SOP không phải component vận hành chính

## 4.1. Minimal Task Lens concept for the current sprint

In the current sprint, **Task Lens** is introduced as a minimal official concept.

`Task Lens` is the runtime viewpoint that AI uses to access, filter, and expand knowledge according to:
- task family / intent
- target object
- current goal / stage

At the architecture level, this means:

- **Knowledge Hub** should support lens-based access
- AI should be able to use Task Lens to:
  - prioritize retrieval
  - formulate knowledge queries
  - choose expansion paths
  - filter context

Task Lens is intentionally kept light in the current sprint:
- it is **not** a heavy artifact
- it is **not** a mandatory persisted object
- it may come from:
  - preset lenses
  - BrSE-chosen lenses
  - runtime-defined lenses confirmed by BrSE

---

# 5. Architecture principles

## 5.1. Component model
Mỗi component là một khối chức năng ổn định của hệ thống, có boundary và responsibility riêng.

## 5.2. Artifact-centric AIP model
`AIP` là **artifact-centric component**.
Điều này tương tự cách một hệ thống có thể coi `Database` là một component trong thiết kế:
- nó là một khối chính thức của hệ thống
- nhưng bản thân nó không “thực thi nghiệp vụ” theo nghĩa actor/process

## 5.3. AI-led orchestration, not orchestrator component
Không có `Orchestrator` như một process component riêng.
Phần orchestration được hiểu là:
- hành vi vận hành của AI
- khi AI sử dụng Knowledge Hub, AIP, Skills, Workspace
- dưới governance của HUMAN

## 5.4. Default behavior, not rigid path
Kiến trúc mô tả **recommended default behavior**, không phải con đường duy nhất cứng nhắc.
AI có thể đề xuất reduction / bypass trong case phù hợp, nhưng:
- phải confirm với HUMAN trước
- phải giữ minimum guardrails

## 5.5. Working AIP as minimum execution guardrail
Không đi vào execution nếu chưa có **Working AIP**.
Working AIP là mandatory pre-execution artifact.

---

# 6. Component responsibilities

## 6.1. Workspace

### Purpose
Là không gian làm việc theo task/session.

### Main responsibilities
- giữ current working session
- giữ current task state ở mức làm việc
- là nơi Working AIP được dùng trong công việc hiện tại
- hỗ trợ continuity / resume của task đang xử lý
- phản ánh current active context của công việc

### Non-responsibilities
- không sở hữu reusable knowledge lõi
- không là nơi lưu Use Case / Template library chuẩn
- không là governance layer chính

---

## 6.2. Knowledge Hub

### Purpose
Là trung tâm tri thức tái sử dụng và lớp truy cập tri thức chuẩn của hệ thống.

### Main responsibilities
- common / project / local knowledge
- source artifacts / meta / index
- curated knowledge assets
- canonical object / concept organization
- alias / natural-language based recognition support
- Use Case library
- AIP Template library
- preset common knowledge appendices
- lens-based retrieval support
- scope-aware routing support
- expansion-link support
- evidence-depth-aware bridge from wiki layer to source layer
- capability-based access contract for adapters/tools
- enrichment destination
- audit / maintenance destination
- approved capture destination

### Architectural notes
At the architecture level, Knowledge Hub is expected to support:
- object / concept resolution before deep expansion
- wiki-first access by default
- controlled expansion via reusable links
- scoped deep research beyond wiki when needed
- tool-agnostic access through logical capabilities rather than backend-specific assumptions

### Non-responsibilities
- không điều phối task hiện tại
- không tạo Working AIP
- không thực thi task thay AI
- không tự quyết định mở deep research quá rộng mà không có AI/HUMAN control

---

## 6.3. AIP

### Purpose
Là artifact-centric component cho **AI Implementation Plan**.

### Main responsibilities
- AIP family / AIP structures
- AIP template instances / AIP artifacts if needed
- Working AIP artifacts
- AIP section structure / validation logic ở mức artifact
- execution-support plan artifacts for task-specific work

### Architectural clarification
AIP:
- không phải process component
- không tự thực thi nhiệm vụ
- không phải actor
- không thay AI ra quyết định

AIP là artifact để:
- AI làm việc hiệu quả hơn
- AI phát huy năng lực suy luận tốt hơn
- AI làm đúng scope mà HUMAN mong muốn
- AI làm việc dưới các gate quan trọng do HUMAN kiểm soát

### Non-responsibilities
- không sở hữu reusable knowledge chuẩn như Use Case / Template libraries
- không là governance layer
- không là capability execution layer

---

## 6.4. SeedPath

### Purpose
Là component cho path / seed-driven navigation của hệ thống.

### Current level
- official component
- current sprint chỉ ở mức declared + light detail

### Current responsibilities
- giữ vai trò future path / navigation layer
- tạo nền cho việc nối knowledge, planning, and execution paths ở phase sau

### Current detail rule
Không ép current sprint phải detail sâu SeedPath.

---

## 6.5. Skills

### Purpose
Là capability component của hệ thống.

### Main responsibilities
- cung cấp reusable execution capabilities
- xử lý các task không cần suy luận mở
- cung cấp callable routines / scripts / tool-like capabilities
- hỗ trợ task execution theo Working AIP

### Important clarification
Skills:
- không phải “skill của AI”
- là capability component của hệ thống
- chủ yếu phục vụ các task không cần suy luận mở hoặc có quy trình rõ

### Two-way interaction principle
- AI có thể gọi Skills để thực hiện các task không cần suy luận
- Skills cũng có thể gọi LLM API khi cần một subtask reasoning hẹp

### Non-responsibilities
- không quyết định direction quan trọng
- không sở hữu governance
- không sở hữu reusable knowledge chuẩn

---

# 7. Artifact ownership

## 7.1. Knowledge Hub owns
Knowledge Hub sở hữu và quản lý:
- Use Case
- AIP Template
- preset common knowledge appendices
- source artifacts / meta / index
- curated knowledge assets
- approved captured knowledge

## 7.2. AIP owns
AIP component sở hữu:
- AIP artifacts
- Working AIP artifacts
- AIP structural contracts at artifact level

## 7.3. Workspace holds active working state
Workspace giữ:
- active task/session state
- current working context at task level
- active use of Working AIP during task execution

## 7.4. Skills own capability artifacts
Skills sở hữu:
- reusable execution capabilities
- capability definitions / callable routines

## 7.5. Governance does not own runtime components
SOP/governance layer không phải component owner của các runtime artifacts.
Nó cung cấp:
- rules
- policies
- guardrails
- checkpoint expectations

---

# 8. Interaction architecture

## 8.1. AI ↔ Workspace
AI dùng Workspace để:
- tiếp cận task hiện tại
- giữ current working context
- làm việc với Working AIP trong active task/session
- resume / continue task hiện tại

## 8.2. AI ↔ Knowledge Hub
AI dùng Knowledge Hub để:
- tìm context liên quan
- tìm Use Case
- tìm AIP Template
- truy common/project/local knowledge
- dùng source/meta/index để discovery
- tham khảo preset common knowledge khi cần bootstrap

## 8.3. AI ↔ AIP
AI dùng AIP component để:
- chọn AIP artifact phù hợp
- tạo Working AIP
- đọc / cập nhật Working AIP khi làm việc
- dùng Working AIP như execution-support artifact

## 8.4. AI ↔ Skills
AI có thể gọi Skills để:
- thực hiện các task không cần suy luận mở
- chạy capability có quy trình rõ
- hỗ trợ thực thi theo Working AIP

## 8.5. Skills ↔ LLM API
Skills có thể gọi LLM API khi cần:
- một subtask reasoning giới hạn
- semantic interpretation hẹp
- bounded reasoning subflow

Điều này không làm Skills trở thành decision authority.

## 8.6. AI ↔ HUMAN
AI tương tác với HUMAN tại:
- clarification gates
- reduction / bypass confirmation
- template application confirmation
- high-risk direction confirmation
- controlled capture approval

Khi xin confirm, AI phải luôn nêu:
- lý do
- rủi ro

## 8.7. Knowledge Hub ↔ AIP
Knowledge Hub cung cấp:
- Use Case
- AIP Template
cho AI lựa chọn trước khi tạo Working AIP trong AIP component.

## 8.8. Workspace ↔ AIP
Workspace không “sở hữu” Working AIP như reusable artifact,
nhưng là nơi:
- Working AIP được dùng
- Working AIP được vận hành trong task hiện tại

## 8.9. AIP ↔ Skills
AIP không trực tiếp “gọi” Skills như actor,
nhưng Working AIP có thể là artifact mà AI dùng để quyết định:
- Skill nào cần gọi
- capability nào cần áp dụng

## 8.10. SeedPath ↔ other components
Ở current level, SeedPath được giữ ở mức nhẹ.
Về dài hạn, SeedPath sẽ tương tác với:
- Knowledge Hub
- AIP
- Workspace

để hỗ trợ:
- path discovery
- seeded navigation
- future work guidance

---

# 9. Default flow under the actor-component model

## 9.1. Recommended default flow
Ở mức architecture, default flow có thể được hiểu như sau:

1. HUMAN đưa task / objective / scope expectation
2. AI tiếp cận task trong Workspace
3. AI tham khảo Knowledge Hub để discovery và tìm reusable knowledge
4. AI chọn hoặc tạo AIP phù hợp
5. AI tạo Working AIP trong AIP component
6. AI dùng Working AIP để thực thi task
7. AI gọi Skills khi cần capability không cần suy luận mở
8. HUMAN kiểm tra và quyết định ở các gate quan trọng
9. Kết quả/capture được quay về Knowledge Hub khi được approve

## 9.2. Important note
Đây là **default behavior**, không phải rigid single path.
AI có thể đề xuất reduction / bypass,
nhưng reduction / bypass quan trọng phải được HUMAN confirm trước.

---

# 10. Gate and governance architecture

## 10.1. Governance source
Governance đến từ:
- SOP
- project rules
- gate rules
- approval expectations

## 10.2. Governance application
Governance không được mô hình hóa như component runtime riêng.
Thay vào đó:
- AI áp dụng governance trong hành vi vận hành
- HUMAN thực thi decision authority tại các gate

## 10.3. Typical gate points
Các gate điển hình gồm:
- scope chưa đủ rõ
- reduction / bypass được đề xuất
- selected direction có ambiguity hoặc risk cao
- template application confirmation
- controlled capture approval

---

# 11. Detail level by component in the current sprint

The current sprint should treat component detail levels as follows:

- **Knowledge Hub**: deep
- **AIP**: deep
- **Workspace**: medium
- **Skills**: light-medium
- **SeedPath**: declared-light

This helps keep the current sprint in scope.

---

# 12. Architecture boundary decisions

## 12.1. AI and HUMAN are actors, not components
AI và HUMAN phải được mô hình hóa là actors.

## 12.2. SOP is governance, not a component
SOP thuộc governance layer, không phải official component.

## 12.3. AIP is artifact-centric, not process-centric
AIP là component xoay quanh artifact, không phải process engine.

## 12.4. There is no Orchestrator component
System không có Orchestrator như process component riêng.
Orchestration là hành vi của AI khi dùng các components dưới governance của HUMAN.

## 12.5. Skills are system capabilities, not AI’s innate skills
Skills là capability component của hệ thống, không phải “skill của AI”.

## 12.6. Working AIP is mandatory before execution
Không đi vào execution nếu chưa có Working AIP.

## 12.7. Scope and AIP are for effectiveness, not mechanical restriction
Scope và AIP tồn tại để:
- giúp AI làm việc hiệu quả
- giữ rõ mục tiêu
- giảm lệch hướng
- phát huy suy luận tốt hơn

Chúng không tồn tại để kìm kẹp AI một cách máy móc.
# Knowledge-runtime sprint canonical addendum

## Purpose of this addendum

This addendum reflects the knowledge-runtime sprint decisions into the architecture baseline.

## Runtime component boundary confirmed

The following boundary is confirmed:

- **Knowledge Hub** owns reusable knowledge and standard knowledge access.
- **Task Lens** is the runtime concept that routes task intent toward relevant knowledge.
- **Wiki Meta / Index** is the runtime-facing structured layer of Knowledge Hub.
- **AIP Template** provides reusable execution frames.
- **Working AIP** is the task-specific execution-support artifact and minimum execution guardrail.
- **Workspace** holds active task/session state and notebook-like current working context.
- **Skills** are reusable execution capabilities, not decision authority or orchestrator.

## Architecture guardrails

- Knowledge Hub must not become the execution center.
- Task Lens must not be confused with AIP Template or Wiki Meta / Index.
- Wiki Meta / Index must not be treated as the whole Knowledge Hub or as source of truth.
- Workspace must not become the reusable knowledge store.
- Skills must not become an orchestrator.
- Working AIP remains mandatory before meaningful execution.

---

# Personal Notebook architecture addendum

## Architectural position

Personal Notebook is a personal working reference area outside task Workspace by default.

It is configured by local path and used for personal/cross-task continuity.

## Component boundary

- Workspace findings: task-bound findings and active task state.
- Personal Notebook: personal/cross-task reference notes.
- Knowledge Hub: reusable knowledge center.
- Working AIP: execution guardrail.
- Skills: reusable capabilities, including optional Personal Notebook Write Skill Lite.

## Guardrails

Personal Notebook must not become:
- Knowledge Hub
- Workspace findings
- Working AIP
- source of truth by default
- auto-promotion pipeline

---

# Source Understanding Artifact architecture addendum

## Architectural position

Source Understanding Artifact sits between raw/source and runtime knowledge use:

```text
raw/source
  ↓
Source Understanding Artifact
  ↓
Wiki Meta / Index / Knowledge Hub access
  ↓
AI runtime use
```

## Component boundary

- Raw/source: source of truth.
- Source Understanding Artifact: reusable source-derived understanding.
- Wiki Meta / Index: runtime route/access layer.
- Knowledge Hub: reusable knowledge center; may contain curated Source Understanding Artifacts.
- Working AIP: execution guardrail.
- Workspace/Personal Notebook: working or personal notes, not source understanding artifacts by default.

## Guardrails

Source Understanding Artifact must preserve provenance and verification path.

---

# Task Lens architecture addendum

Architectural position:

```text
Task intent
  ↓
Task Lens OR No-Lens
  ↓
Knowledge Routing
  ↓
Wiki Meta / Index / Knowledge Hub / Source Understanding Artifact
  ↓
raw/source when needed
  ↓
Working AIP / execution support
```

Task Lens belongs to runtime reasoning / task alignment.

It is not a storage component and does not own knowledge or metadata.

---

# Controlled Knowledge Promotion architecture addendum

Controlled Knowledge Promotion is a transition/review flow between working layers and durable knowledge layers.

```text
Notebook / Workspace / Task Output / Source Understanding Artifact / Task Lens / HUMAN feedback
  ↓
Knowledge Promotion Candidate
  ↓
Knowledge Value + Source/Authority/Target checks
  ↓
Promotion decision
  ↓
Knowledge Hub / canonical docs / appendix / guideline / AIP improvement / backlog / local retention / discard
```

It is not a storage component and not an approval authority.
