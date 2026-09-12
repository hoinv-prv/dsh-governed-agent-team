# Basic Design for AI Work System MVP
Version: 0.4  
Status: Canonical merged baseline through current point  
Phase: Basic Design  
Scope: MVP current canonical baseline

---

# 1. Purpose

Tài liệu này mô tả phần **canonical Basic Design** cho AI Work System v1.0+ current canonical baseline.

Mục tiêu của tài liệu là:
- refactor Basic Design theo **actor-component model** đã được chốt
- mô tả Basic Design theo trục:
  - **component**
  - **feature**
  - **feature behavior**
- làm rõ trong từng component:
  - feature nào tồn tại
  - feature đó xử lý ra sao
  - AI dùng feature đó như thế nào
  - khi nào cần HUMAN checkpoint
  - guardrails nào cần giữ

Lưu ý:
- tài liệu này không đi sâu vào exact schema field-by-field
- cũng không đi vào exact algorithm / ranking / storage model
- các phần đó sẽ được tiếp tục chi tiết hóa trong Specs / Guidelines Delta
# 3. Actor model in Basic Design

## 3.1. AI
AI là actor chính chịu trách nhiệm:
- hiểu task
- tham khảo tri thức
- chọn / tạo AIP
- dùng Working AIP để thực thi công việc
- gọi Skills khi cần capability
- xin HUMAN confirm ở các gate quan trọng

## 3.2. HUMAN
HUMAN là actor:
- kiểm tra
- confirm
- ra quyết định ở các gate quan trọng
- giữ scope và governance expectation

## 3.3. Basic design implication
Trong Basic Design, behavior nên được viết theo kiểu:
- AI dùng feature nào của component nào
- feature đó trả ra artifact/state gì
- khi nào HUMAN cần được kéo vào

---

# 4. Official components and detail level in the current sprint

Current official components at this level are:

1. **Workspace**
2. **Knowledge Hub**
3. **AIP**
4. **SeedPath**
5. **Skills**

Current sprint detail levels:
- **Knowledge Hub**: deep
- **AIP**: deep
- **Workspace**: medium
- **Skills**: light-medium
- **SeedPath**: declared-light

---

# 5. Cross-component operating rules

## 5.1. Recommended default behavior
AI Work System có một **recommended default behavior**.
Default behavior giúp:
- giữ consistency
- giảm lệch hướng
- tăng khả năng tái sử dụng tri thức

## 5.2. Allowed shortcuts / deviations
AI có thể đề xuất:
- reduction
- bypass
- shortcut

nếu:
- task đã đủ rõ
- HUMAN đã chỉ rõ direction
- project path đã quá rõ
- additional discovery không còn information gain đáng kể

Nhưng:
- reduction / bypass quan trọng phải confirm với HUMAN
- AI phải luôn nêu:
  - lý do
  - rủi ro

## 5.3. Working AIP as minimum execution guardrail
Không đi vào execution nếu chưa có **Working AIP**.

Working AIP là:
- mandatory pre-execution artifact
- execution-support artifact cho task hiện tại

## 5.4. Working AIP minimum mandatory content
Working AIP phải có tối thiểu:
1. Task objective
2. Current scope
3. Working direction
4. Key context / inputs
5. Expected output
6. Checkpoint / approval note

## 5.5. Scope and AIP are for effectiveness, not mechanical restriction
Scope và AIP tồn tại để:
- giúp AI làm việc hiệu quả
- giữ rõ mục tiêu
- giảm lệch hướng
- phát huy suy luận tốt hơn

Không phải để kìm kẹp AI một cách máy móc.

## 5.6. Important decisions remain HUMAN-governed
Khi decision có ảnh hưởng quan trọng tới:
- direction
- shortcut
- template application
- capture / refinement

AI phải xin HUMAN confirm.

---

# 6. Component 1 — Workspace

## 6.1. Component purpose
Workspace là không gian làm việc theo task/session, nơi công việc hiện tại được giữ ở mức active.

## 6.2. Boundary
Workspace chịu trách nhiệm:
- current working session
- current task state
- active working context ở mức vận hành
- continuity / resume support
- active use of Working AIP

Workspace không chịu trách nhiệm:
- sở hữu reusable knowledge chuẩn
- quyết định use case/template như knowledge owner
- giữ SOP/governance rules như component nội tại

## 6.3. Main features

### Feature 1 — Task/session holding
**Purpose**  
Giữ task hiện tại trong một working session rõ ràng.

**Input**  
- task context from AI/HUMAN
- current task state

**Behavior**  
- gắn task vào working session
- giữ current active state của task

**Output**  
- active task/session state

---

### Feature 2 — Active working context support
**Purpose**  
Giữ current active context ở mức làm việc.

**Input**  
- Working AIP
- current task state
- current decisions

**Behavior**  
- reflect active task context
- giữ những decision đang active cho task

**Output**  
- active working context snapshot

---

### Feature 3 — Continuity / resume support
**Purpose**  
Cho phép AI/HUMAN quay lại task đang làm mà không mất mạch.

**Input**  
- prior working state
- current task session

**Behavior**  
- giữ continuity
- hỗ trợ resume state

**Output**  
- resumable task/session state

**Open note**  
Resume/re-entry behavior vẫn có thể cần detail hơn ở vòng sau.

## 6.4. Interaction summary
Workspace chủ yếu được:
- AI sử dụng như nơi current work diễn ra
- Working AIP được dùng tại đây
- HUMAN theo dõi và kiểm tra task tại đây

---

# 7. Component 2 — Knowledge Hub

## 7.1. Component purpose
Knowledge Hub là trung tâm tri thức tái sử dụng của hệ thống.

## 7.2. Boundary
Knowledge Hub chịu trách nhiệm:
- common / project / local knowledge
- source/meta/index
- curated knowledge assets
- Use Case library
- AIP Template library
- preset common knowledge appendices
- retrieval / enrichment destination
- audit / maintenance destination
- approved capture destination

Knowledge Hub không chịu trách nhiệm:
- trực tiếp tạo Working AIP
- trực tiếp điều phối task
- trực tiếp thực thi task

## 7.3. Main feature groups

### Feature group 0 — Task Lens-driven knowledge access
Các feature này phản ánh cách AI dùng **Task Lens** khi truy cập Knowledge Hub.

#### Feature 0.1 — Task Lens determination
**Behavior**
- AI xác định `Task Lens` từ:
  - task family / intent
  - target object
  - current goal / stage
- Lens có thể đến từ:
  - preset lens
  - BrSE-selected lens
  - runtime-defined lens confirmed by BrSE

#### Feature 0.2 — Lens-based retrieval priority
**Behavior**
- AI ưu tiên loại knowledge cần tìm theo Task Lens hiện tại
- không truy raw knowledge một cách dàn trải không có mục đích

#### Feature 0.3 — Lens-based expansion path
**Behavior**
- sau khi thấy mảnh ghép đầu tiên từ Knowledge Hub, AI dùng Task Lens để quyết định:
  - cần tìm tiếp gì
  - liên kết nào nên mở tiếp
  - đâu là blocker/open point

#### Feature 0.4 — Lens-based context filtering
**Behavior**
- AI dùng Task Lens để phân loại context:
  - core
  - supporting
  - reserve
- tránh kéo quá nhiều context không phục vụ task hiện tại

---

### Feature group A — Knowledge object model and layering
Các feature gồm:
- canonical object/concept organization
- alias / natural-language recognition support
- common/project/local layering
- source/meta/index organization

> **2-layer note (CR-AIWS-2026-05-020):** Canonical identity/resolution below now lives in the **artifact-level
> meta** (lookup_keys + aliases) — retired KO record: xem `Knowledge_Object_Model_Spec_MVP` §8 (CR-005).
> "Layering" here = the common/project/local knowledge zones (A2). Cross-artifact
> relationships → `## Related Sources`.

#### Feature A1 — Canonical object / concept organization
**Behavior**
- giữ canonical identity bằng lookup keys (ID / tên chính thức) trong artifact meta
- giữ primary names theo ngôn ngữ
- giữ aliases, natural-language expressions, related keywords
- giúp AI resolve object/concept trước khi retrieval sâu hơn

#### Feature A2 — Layered knowledge organization
**Behavior**
- tổ chức knowledge theo:
  - common
  - project
  - local
- giữ boundary rõ giữa layers

#### Feature A3 — Source/meta/index handling
**Behavior**
- giữ source artifacts
- giữ source meta
- giữ source index
- hỗ trợ discovery mà không đồng nhất source-side với curated operational knowledge

---

### Feature group B — Reusable knowledge asset management
Các feature gồm:
- Use Case management
- AIP Template management
- preset knowledge management

#### Feature B1 — Use Case library management
**Behavior**
- lưu / quản lý Use Case
- hỗ trợ AI query Use Case candidates
- nhận refined/approved Use Case updates về sau

#### Feature B2 — AIP Template library management
**Behavior**
- lưu / quản lý AIP Templates
- hỗ trợ AI query template candidates
- giữ project/common/local template reuse paths

#### Feature B3 — Preset common knowledge management
**Behavior**
- giữ preset common use cases
- giữ preset common AIP templates
- giữ task lens / questioning / capture presets khi có

---

### Feature group C — Routing and retrieval support

#### Feature C1 — Object / concept resolution support
**Purpose**
Hỗ trợ AI map input runtime sang canonical object/concept.

**Behavior**
- resolve từ canonical names / aliases / natural-language expressions / keywords
- nếu input ban đầu là non-canonical thì support confirm canonical target trước khi đi sâu

#### Feature C2 — Scope-aware and lens-aware retrieval support
**Purpose**
Hỗ trợ AI lấy context đúng theo task hiện tại.

**Behavior**
- route theo:
  - task lens
  - domain
  - scope precedence
  - target object/concept
- trả về relevant knowledge / context candidates cho next decision

#### Feature C3 — Evidence-depth signaling
**Behavior**
- phân biệt nhẹ giữa:
  - wiki_only
  - source_checked
- nếu current result mới ở wiki layer thì support warning rõ cho AI/HUMAN

---

### Feature group D — Expansion support

#### Feature D1 — Common expansion link support
**Behavior**
- giữ các expansion links dạng common như:
  - parent
  - input
  - related
  - reference
- mỗi link có summary ngắn để AI biết link đó thêm thông tin gì

#### Feature D2 — Link lifecycle support
**Behavior**
- cho phép link mới được hình thành dần theo flow:
  - Working AIP
  - local wiki
  - project wiki
  - source meta / source artifact / wiki meta nếu phù hợp
- AI có thể gợi ý promote link khi thấy reuse value rõ

---

### Feature group E — Access interface support

#### Feature E1 — Capability-based access contract
**Behavior**
- hỗ trợ lớp capability logic cho AI như:
  - resolve
  - search
  - retrieve
  - expand
  - inspect source
  - report evidence depth
- không khóa vào backend/tool cụ thể

#### Feature E2 — Scoped deep research support
**Behavior**
- giữ nguyên tắc wiki first
- nếu cần đi sâu hơn ngoài wiki:
  - không grep full mặc định
  - support source inspection theo scope rõ
  - AI nên đề xuất folder/group-folder/source-zone để BrSE chọn trước

---

### Feature group F — Enrichment / maintenance destination

#### Feature F1 — Approved capture intake
**Behavior**
- nhận approved capture từ flow làm việc
- route về đúng knowledge destination

#### Feature F2 — Audit / maintenance support
**Behavior**
- hỗ trợ review / cleanup / maintenance cho knowledge assets theo lifecycle về sau

## 7.4. Interaction summary
Knowledge Hub chủ yếu được AI sử dụng để:
- resolve object/concept
- discovery
- routing and retrieval support
- expansion from first useful object
- matching support
- template lookup
- evidence-depth signaling
- bootstrap from common knowledge
- capture / enrichment destination after approval

---

# 8. Component 3 — AIP

## 8.1. Component purpose
AIP là artifact-centric component cho **AI Implementation Plan**.

## 8.2. Boundary
AIP chịu trách nhiệm:
- AIP artifact structures
- Working AIP artifacts
- AIP artifact-level validation
- AIP as execution-support artifact family

AIP không chịu trách nhiệm:
- điều phối flow như process component
- sở hữu reusable knowledge chuẩn
- tự thực thi nhiệm vụ

## 8.3. Core clarification
AIP là artifact để:
- giúp AI thực thi nhiệm vụ hiệu quả
- giúp AI phát huy tối đa năng lực suy luận
- giúp AI làm đúng scope mà HUMAN mong muốn
- giúp AI làm việc dưới HUMAN-controlled gates

AIP không sinh ra để:
- trói AI một cách máy móc
- thay thế actor thực thi
- tự quyết định process

## 8.4. Main feature groups

### Feature group A — AIP structure handling
#### Feature A1 — Artifact structure handling
**Behavior**
- giữ cấu trúc AIP family
- hỗ trợ artifact sections / organization ở mức component

#### Feature A2 — Mandatory content validation
**Behavior**
- kiểm tra Working AIP có đủ content tối thiểu chưa
- nếu thiếu, trả ra missing mandatory items

**Mandatory minimum content**
1. Task objective
2. Current scope
3. Working direction
4. Key context / inputs
5. Expected output
6. Checkpoint / approval note

---

### Feature group B — Working AIP generation support
#### Feature B1 — Working AIP drafting support
**Purpose**
Hỗ trợ AI tạo Working AIP cho task hiện tại.

**Input**
- selected direction
- selected template
- relevant context
- confirmed human instructions / decisions

**Behavior**
- hỗ trợ instantiate Working AIP
- carry forward selected decisions
- auto-fill khi có đủ context

**Output**
- Working AIP draft

#### Feature B2 — Sufficient-to-start validation
**Behavior**
Kiểm tra Working AIP đã đủ để bắt đầu execution chưa:
- mandatory content đủ chưa
- direction đủ rõ chưa
- scope đủ rõ chưa
- checkpoint cần thiết đã ghi chưa
- HUMAN confirmations cần thiết đã xong chưa

**Output**
- ready to execute
- or need minimal clarification

---

### Feature group C — Working AIP active use support
#### Feature C1 — Active Working AIP handling
**Behavior**
- cho phép AI đọc/ghi/update Working AIP trong lúc làm task
- giữ Working AIP như execution-support artifact của task cụ thể

## 8.5. Interaction summary
AIP được AI dùng để:
- tạo Working AIP
- validate Working AIP
- giữ execution-support artifact cho task hiện tại

Workspace dùng Working AIP như active work artifact,
nhưng ownership của artifact nằm ở AIP component.

---

# 9. Component 4 — SeedPath

## 9.1. Component purpose
SeedPath là component cho path / seed-driven navigation của hệ thống.

## 9.2. Current level boundary
Ở sprint hiện tại, SeedPath:
- đã là official component
- nhưng mới ở mức declared + light detail

## 9.3. Current feature placeholders

### Feature placeholder 1 — Path semantics
SeedPath sẽ về sau hỗ trợ:
- path definition
- seeded guidance
- navigation semantics between work/knowledge paths

### Feature placeholder 2 — Future integration points
SeedPath dự kiến sẽ nối với:
- Knowledge Hub
- AIP
- Workspace

để hỗ trợ:
- path discovery
- seeded navigation
- future work guidance

## 9.4. Current design rule
Không ép current sprint phải detail sâu SeedPath beyond declared role.

---

# 10. Component 5 — Skills

## 10.1. Component purpose
Skills là capability component của hệ thống.

## 10.2. Boundary
Skills chịu trách nhiệm:
- reusable execution capabilities
- callable routines/scripts/tools
- tasks không cần suy luận mở
- bounded execution support

Skills không chịu trách nhiệm:
- quyết định working direction quan trọng
- sở hữu governance
- sở hữu reusable knowledge chuẩn

## 10.3. Main feature groups

### Feature group A — Capability invocation
#### Feature A1 — Callable execution capability
**Behavior**
- nhận execution request từ AI
- thực hiện task capability có quy trình rõ
- trả kết quả / output / evidence

### Feature group B — Bounded reasoning subflow
#### Feature B1 — LLM-assisted bounded reasoning inside Skills
**Behavior**
- khi cần một subtask reasoning hẹp, Skill có thể gọi LLM API
- rồi tiếp tục flow capability của Skill

**Important boundary**
- việc Skills gọi LLM API không biến Skills thành decision authority
- Skills vẫn không quyết định direction quan trọng của task

## 10.4. Interaction summary
AI có thể gọi Skills để:
- thực hiện tác vụ không cần suy luận mở
- chạy bounded capability flows

Skills có thể call LLM API khi cần reasoning hẹp,
nhưng quyết định direction vẫn nằm ở AI under HUMAN governance.

---

# 11. Cross-component interaction summary

## 11.1. AI ↔ Workspace
AI dùng Workspace để:
- tiếp cận task hiện tại
- giữ current active work
- resume task continuity

## 11.2. AI ↔ Knowledge Hub
AI dùng Knowledge Hub để:
- discovery
- use case lookup
- template lookup
- context retrieval
- bootstrap common knowledge

## 11.3. AI ↔ AIP
AI dùng AIP để:
- tạo / cập nhật Working AIP
- validate readiness
- dùng Working AIP như execution-support artifact

## 11.4. AI ↔ Skills
AI dùng Skills để:
- thực hiện execution capabilities

## 11.5. AI ↔ HUMAN
AI xin HUMAN confirm tại:
- shortcut / bypass
- template application
- high-risk direction
- controlled capture approval
- các gate quan trọng khác

Khi xin confirm, AI phải nêu:
- reason
- risk

## 11.6. Approved capture → Knowledge Hub
Capture suggestion được AI đề xuất,
HUMAN approve,
sau đó quay về Knowledge Hub như reusable knowledge destination.

---

# 12. Carry-forward and continuity rules

## 12.1. Carry-forward objects
System nên carry forward:
- relevant task understanding
- current active context
- selected direction
- selected template
- confirmed decisions
- Working AIP state when applicable

## 12.2. No unnecessary re-asking
Các point đã được close đủ rõ không nên bị hỏi lặp ở bước sau.

## 12.3. Working AIP continuity
Working AIP phải phản ánh:
- selected direction
- selected template
- key context đã chốt
- approval/checkpoint notes

---

# 13. Basic boundary decisions

## 13.1. Basic Design is component-based
Basic Design phải được tổ chức theo:
- component
- feature
- feature behavior

không phải chủ yếu theo runtime phase.

## 13.2. Runtime flow remains as a short summary only
Flow tổng thể vẫn có thể được giữ ở mức summary ngắn,
nhưng không phải trục chính của Basic Design.

## 13.3. AI/HUMAN are actors, not components
Các behavior trong Basic Design phải phản ánh actor usage,
không mô hình hóa AI/HUMAN như components.

## 13.4. SOP is governance, not a component
SOP không phải component được detail như các component khác.

## 13.5. AIP is artifact-centric
AIP không được mô tả như process engine.

## 13.6. Skills are capabilities, not decision authority
Skills không quyết direction quan trọng.

## 13.7. Default behavior is not a rigid single path
Reduction / bypass là allowed,
nhưng:
- phải confirm với HUMAN trong case quan trọng
- phải giữ minimum guardrails

## 13.8. Working AIP is mandatory before execution
Không bắt đầu execution nếu chưa có Working AIP đủ điều kiện.
# Knowledge-runtime sprint canonical addendum

## Feature group — Runtime knowledge foundation

The MVP baseline now explicitly includes the following minimal runtime knowledge foundation:

1. **Runtime terminology baseline**
   - Knowledge Hub
   - Task Lens
   - Wiki Meta / Index
   - Working AIP
   - Workspace
   - Skills

2. **Runtime knowledge access flow**
   - current context / notebook / workspace state
   - Task Lens
   - Wiki Meta / Index
   - curated artifact meta (+ `## Related Sources`)
   - raw/source fallback when required

3. **Working AIP connection**
   - discovery/reuse/runtime knowledge access may feed Working AIP
   - retrieval summaries, working notes, selected entries, and raw/source references do not replace Working AIP
   - Working AIP remains the minimum execution guardrail

4. **Minimal testing stance**
   - correctness before optimization
   - runtime support must not degrade task quality
   - readiness/equivalence mindset is required when changing knowledge-runtime behavior

## Deferred feature areas

The following are intentionally deferred from MVP detailed design in this sprint:

- full notebook spec
- full metadata/registry framework
- full testing/scoring/telemetry
- lens preset catalog/orchestration
- source-derived reusable understanding artifact canonicalization

---

# Personal Notebook MVP addendum

## Feature summary

Personal Notebook is added as a minimal MVP feature.

It is a file/folder-based personal working reference area for BrSE/HUMAN, configured outside task Workspace and Working AIP.

It is used to preserve selected personal ideas, observations, weak findings, cross-task notes, future sprint ideas, and capture candidates for later reference.

## Core boundaries

- Personal Notebook is not Workspace findings.
- Personal Notebook is not Working AIP.
- Personal Notebook is not Knowledge Hub.
- Personal Notebook is not source of truth by default.
- Personal Notebook does not auto-promote into Knowledge Hub.
- Personal Notebook effective scope follows the configured notebook path.

## Skill support

A lightweight Personal Notebook Write Skill Lite may support creating, appending, updating, marking capture candidates, and archiving notes.

The skill is not decision authority or orchestrator.

---

# Source Understanding Artifact MVP addendum

## Feature summary

Source Understanding Artifact is added as a minimal MVP artifact pattern.

It stores reusable source-derived understanding of one clear source unit, with minimal provenance, authority, and freshness hints.

## Core boundaries

- Raw/source remains source of truth.
- Source Understanding Artifact is not Wiki Meta / Index.
- Source Understanding Artifact is not Working AIP.
- Source Understanding Artifact is not Workspace findings.
- Source Understanding Artifact is not Personal Notebook.
- Source Understanding Artifact is not Knowledge Hub content by default.

## MVP value

It reduces repeated raw/source reading while preserving a verification path back to source.

---

# Task Lens MVP addendum

Task Lens is added as a minimal MVP runtime concept.

It is an optional viewpoint for task → knowledge routing after task intent is clear.

It does not replace:
- AIP Template
- Working AIP
- Wiki Meta / Index
- Knowledge Hub
- raw/source verification

Because Task Lens is not fully designed/tested in MVP, No-Lens / AI-decides-search-scope remains a valid option.

---

# Controlled Knowledge Promotion MVP addendum

Controlled Knowledge Promotion is part of MVP as a minimal controlled flow for reusable value capture and promotion.

MVP includes:
- Knowledge Value definition
- candidate definition
- Knowledge Hub Add/Update Checklist
- no auto-promotion
- HUMAN-triggered lookback
- post-feedback improvement candidate collection
- default lookback for relevant AIP Templates
- run-aip lookback support
  > **PLANNED / NOT BUILT (CR-AIWS-2026-08-057):** đoạn trên mô tả tooling chưa tồn tại (`run_aip.py` không có lookback support — 0 hit code, residual R5-01) — design intent, không phải hành vi. Build → CR riêng gỡ banner.
- log/rollback trace requirement

MVP defers full apply-back workflow, full governance/role matrix, metadata registry, automation, scoring, and rollback implementation.
