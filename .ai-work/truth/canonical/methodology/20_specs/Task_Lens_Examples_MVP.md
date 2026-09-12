# Task Lens Examples and Runtime Guidance MVP

Version: v0.9.6  
Date: 2026-04-25  
Status: Canonical appendix/reference  
Source:
- TL-04 Starter Lens Examples / Minimal Presets v2
- TL-05 Selection / Confirmation / Expansion Rule v4

---

## 1. Purpose

This appendix provides practical Task Lens examples and runtime guidance for MVP.

This is appendix/reference content, not a full lens catalog.

---

## 2. Starter lens examples

# AIWS_TL-04_TASK_LENS_STARTER_EXAMPLES_MINIMAL_PRESETS_v1

Status: Draft  
Sprint: Task Lens Minimal Spec Sprint  
Baseline:
- AI Work System MVP v0.9.5
- Task Lens sprint backlog v3
- TL-01 Task Lens Concept & Purpose
- TL-02 Task Lens Ownership & Boundary
- TL-03 Task Lens Minimal Runtime Flow
- Core Principles / Sprint Alignment Checklist v3


Change from v1:
- Added Intent-first rule: Task Lens selection requires task intent to be clear enough.
- Clarified that AI must clarify / infer / confirm task intent before selecting or proposing Task Lens when intent is unclear.
- Clarified that Task Lens should not be selected from keyword alone.

---

## 1. Purpose of TL-04

TL-04 định nghĩa **starter lens examples / minimal presets** cho Task Lens trong MVP.

Mục tiêu:
- cung cấp một số lens mẫu đủ cụ thể để AI/HUMAN dùng trong runtime
- tránh Task Lens chỉ là concept trừu tượng
- giúp AI infer lens nhanh hơn khi làm task phổ biến
- giữ scope minimal, không tạo full lens catalog/orchestration
- bảo đảm Task Lens không bó hẹp năng lực tìm kiếm/suy luận của AI

TL-04 không nhằm:
- tạo full preset catalog
- tạo lens registry
- tạo scoring/ranking mechanism
- tạo lens orchestration/composition engine
- tạo UI selector
- quyết định toàn bộ lens cho mọi loại task

---

## 2. Principle for starter lenses

Starter lenses trong MVP là **examples / minimal presets**, không phải catalog đầy đủ.

Chúng dùng để:
- giúp AI có default viewpoint ban đầu
- giúp HUMAN hiểu task đang được nhìn theo hướng nào
- giúp knowledge routing có hướng rõ hơn
- làm base cho future expansion nếu cần

Starter lens không được dùng để:
- chặn AI tìm ngoài lens
- buộc mọi task phải fit vào một preset
- thay AIP Template
- thay Working AIP
- thay Wiki Meta / Index
- thay raw/source verification

---

## 3. Starter lens list for MVP

TL-04 đề xuất 7 starter lenses:

1. Requirement Understanding Lens
2. Design Review Lens
3. Test Design Lens
4. Code Investigation Lens
5. Knowledge Capture Lens
6. Source Verification Lens
7. Planning / WBS Lens

Đây là starter examples đủ dùng cho MVP, không phải full catalog.

---

# 4. Requirement Understanding Lens

## 4.1. Purpose

Dùng khi task cần hiểu requirement, customer intent, Q&A, scope, business rule hoặc expected behavior.

## 4.2. Typical tasks

- Làm rõ yêu cầu
- Tạo requirement definition
- Review requirement against Q&A
- Tìm customer decision
- Tóm tắt requirement cho design
- Kiểm tra open points trong requirement

## 4.3. Preferred knowledge targets

Ưu tiên tìm:
- requirement documents
- raw customer request
- Q&A / meeting notes
- decision logs
- Source Understanding Artifact for requirement
- related business rules
- open points / unresolved questions

## 4.4. Suggested search/routing direction

```text
Requirement Understanding Lens
  → requirement source
  → Q&A / customer confirmation
  → decision/open point notes
  → Source Understanding Artifact if available
  → raw/source when exact wording or final decision is needed
```

## 4.5. Verification triggers

Open raw/source when:
- exact customer wording is needed
- final requirement decision is unclear
- Q&A may have changed
- design/test output depends on requirement branch
- there is conflict between requirement and design

## 4.6. Expansion candidates

May expand to:
- Design Review Lens if checking design reflection
- Test Design Lens if deriving test viewpoints
- Source Verification Lens if exact source evidence is needed

---

# 5. Design Review Lens

## 5.1. Purpose

Dùng khi task cần review design, check consistency, detect missing logic, compare design against requirements, hoặc tạo review viewpoints.

## 5.2. Typical tasks

- Review Basic Design
- Review Detail Design
- Check whether Q&A has been reflected
- Compare requirement vs design
- Generate design review viewpoints
- Identify missing branches / edge cases

## 5.3. Preferred knowledge targets

Ưu tiên tìm:
- Basic Design
- Detail Design
- requirement source / Source Understanding Artifact
- Q&A reflected status
- design review guidelines
- related function design
- known risks / issue lists
- DB/interface/flow diagrams if relevant

## 5.4. Suggested search/routing direction

```text
Design Review Lens
  → current design artifact
  → requirement understanding
  → related Q&A / open points
  → design guidelines / review viewpoints
  → raw/source if exact design/requirement text is needed
```

## 5.5. Verification triggers

Open raw/source when:
- design behavior conflicts with requirement
- exact branch condition is needed
- customer decision is required
- DB/interface detail must be verified
- design review finding will be formalized

## 5.6. Expansion candidates

May expand to:
- Requirement Understanding Lens for upstream requirement
- Test Design Lens for testcase impact
- Code Investigation Lens if reviewing implementation/design alignment
- Source Verification Lens for exact evidence

---

# 6. Test Design Lens

## 6.1. Purpose

Dùng khi task cần tạo hoặc review testcases, test viewpoints, branch coverage, expected result, boundary condition, hoặc regression impact.

## 6.2. Typical tasks

- Create testcase viewpoints
- Review testcase
- Derive test branches from requirement/design
- Check expected results
- Identify abnormal/error cases
- Create integration test scenarios

## 6.3. Preferred knowledge targets

Ưu tiên tìm:
- requirement branch conditions
- design branch conditions
- expected result definitions
- screen/report behavior
- business flow
- prior testcase guideline
- defect/risk history if available
- Source Understanding Artifact for requirement/design

## 6.4. Suggested search/routing direction

```text
Test Design Lens
  → requirement/design branch conditions
  → expected results
  → error/edge cases
  → test guideline/checklist
  → raw/source if exact expected value/message is needed
```

## 6.5. Verification triggers

Open raw/source when:
- exact expected result is needed
- exact message/code/value is needed
- test condition depends on customer decision
- branch logic is unclear
- design and requirement conflict

## 6.6. Expansion candidates

May expand to:
- Requirement Understanding Lens for requirement branches
- Design Review Lens for design consistency
- Code Investigation Lens if testcase must reflect implemented behavior
- Source Verification Lens for exact evidence

---

# 7. Code Investigation Lens

## 7.1. Purpose

Dùng khi task cần tìm code, hiểu module behavior, debug, identify call path, map function to implementation, hoặc sửa lỗi.

## 7.2. Typical tasks

- Find where logic is implemented
- Understand code/module responsibility
- Debug runtime behavior
- Check call path
- Modify code
- Compare code with design
- Build code index/source understanding

## 7.3. Preferred knowledge targets

Ưu tiên tìm:
- codebase index
- source files
- module/class/function responsibility
- call graph / call tree if available
- Source Understanding Artifact for code module
- design/spec source for expected behavior
- tests / logs / error messages

## 7.4. Suggested search/routing direction

```text
Code Investigation Lens
  → code index / file inventory
  → candidate modules/classes/functions
  → Source Understanding Artifact for code if available
  → raw/source code
  → design/requirement if expected behavior is unclear
```

## 7.5. Verification triggers

Open raw/source code when:
- changing code
- checking exact function signature
- confirming actual behavior
- debugging error
- code artifact may be stale
- design/code mismatch is suspected

## 7.6. Expansion candidates

May expand to:
- Design Review Lens if expected behavior comes from design
- Requirement Understanding Lens if design is unclear
- Test Design Lens for regression/test impact
- Source Verification Lens for exact source evidence

---

# 8. Knowledge Capture Lens

## 8.1. Purpose

Dùng khi task cần chuyển finding/output/idea thành capture candidate hoặc reusable knowledge thông qua controlled capture.

## 8.2. Typical tasks

- Create Knowledge Hub update candidate
- Promote reusable finding
- Convert task output into guideline
- Review capture candidate
- Decide whether something belongs in Knowledge Hub
- Capture Source Understanding Artifact candidate
- Capture useful custom/runtime lens candidate

## 8.3. Preferred knowledge targets

Ưu tiên tìm:
- current finding/output
- source pointer / evidence
- status/authority/freshness
- controlled capture guideline
- Knowledge Hub target area
- existing similar entries
- canonical docs / guidelines

## 8.4. Suggested search/routing direction

```text
Knowledge Capture Lens
  → identify candidate
  → verify source/status/authority
  → check existing Knowledge Hub entries
  → decide target scope
  → prepare capture request
  → do not auto-promote
```

## 8.5. Verification triggers

Open raw/source when:
- source evidence is required
- finding may be overgeneralized
- candidate conflicts with existing knowledge
- authority/freshness is unclear
- promotion target is canonical/curated

## 8.6. Expansion candidates

May expand to:
- Source Verification Lens for evidence
- Requirement Understanding Lens if candidate is requirement-related
- Design Review Lens if candidate is design-related
- Planning / WBS Lens if candidate should become future sprint backlog

---

# 9. Source Verification Lens

## 9.1. Purpose

Dùng khi task cần kiểm tra evidence, exact wording, final decision, source conflict, freshness, hoặc source-of-truth.

## 9.2. Typical tasks

- Verify exact requirement wording
- Confirm customer decision
- Check source conflict
- Validate Source Understanding Artifact
- Confirm code/design exact behavior
- Check whether artifact is stale

## 9.3. Preferred knowledge targets

Ưu tiên tìm:
- raw/source
- source pointer
- source version/date
- Source Understanding Artifact verification trigger
- Q&A / mail / decision logs
- code source
- canonical docs

## 9.4. Suggested search/routing direction

```text
Source Verification Lens
  → identify source of truth
  → open raw/source
  → compare against derived artifact/summary
  → update status/freshness if needed
```

## 9.5. Verification triggers

This lens is itself used when verification is needed.

Use it when:
- exact evidence matters
- derived artifacts conflict
- freshness is uncertain
- output will be official
- decision depends on source truth

## 9.6. Expansion candidates

May expand to:
- Requirement Understanding Lens
- Design Review Lens
- Code Investigation Lens
depending on source type.

---

# 10. Planning / WBS Lens

## 10.1. Purpose

Dùng khi task cần plan work, decompose tasks, create WBS, define sprint scope, estimate steps, or organize execution.

## 10.2. Typical tasks

- Create sprint backlog
- Create WBS
- Plan design/review/test work
- Identify dependencies
- Organize project artifacts
- Define work phases
- Prepare execution plan before Working AIP

## 10.3. Preferred knowledge targets

Ưu tiên tìm:
- project goal/scope
- current canonical baseline
- open points / deferred items
- prior sprint outputs
- dependency map
- required deliverables
- existing AIP / Working AIP
- methodology guideline

## 10.4. Suggested search/routing direction

```text
Planning / WBS Lens
  → current goal/scope
  → existing backlog/open points
  → dependencies
  → deliverables/artifacts
  → execution constraints
  → Working AIP if execution will begin
```

## 10.5. Verification triggers

Open raw/source when:
- plan depends on exact requirement/scope
- dependency is unclear
- prior decision must be confirmed
- canonical baseline may have changed

## 10.6. Expansion candidates

May expand to:
- Requirement Understanding Lens if scope comes from requirement
- Design Review Lens if planning review work
- Knowledge Capture Lens if planning includes wiki/capture update
- Source Verification Lens if baseline/source must be confirmed

---

## 11. Lens selection quick guide

| User/task intent | Likely starter lens |
|---|---|
| Làm rõ yêu cầu | Requirement Understanding Lens |
| Review basic/detail design | Design Review Lens |
| Tạo/review testcase | Test Design Lens |
| Tìm/sửa/hiểu code | Code Investigation Lens |
| Lưu finding vào Knowledge Hub | Knowledge Capture Lens |
| Kiểm tra exact source/evidence | Source Verification Lens |
| Lập kế hoạch/WBS/sprint scope | Planning / WBS Lens |

This table is a guide, not a hard rule.

---

## 12. Combining lenses

MVP không thiết kế lens composition engine, nhưng cho phép dùng primary + secondary lens một cách lightweight.

Example:

```markdown
Primary lens: Design Review Lens
Secondary lens: Requirement Understanding Lens
Reason: Review must verify design against upstream requirement.
```

Common combinations:

| Primary lens | Common secondary lens | Why |
|---|---|---|
| Design Review | Requirement Understanding | verify design against requirement |
| Test Design | Requirement Understanding | derive branches/expected results |
| Code Investigation | Design Review | compare implementation with design |
| Knowledge Capture | Source Verification | verify evidence before capture |
| Planning/WBS | Knowledge Capture | plan wiki/capture work |

---

## 13. When to create a custom/runtime lens

A custom/runtime lens may be useful when:
- task does not fit starter lenses
- domain-specific viewpoint is needed
- project-specific review viewpoint is needed
- repeated task pattern appears
- HUMAN defines special task direction

Examples:
- COBOL Migration Compatibility Lens
- Manufacturing Allocation Review Lens
- AIWS Sprint Closure Lens
- Security Impact Review Lens

If custom lens affects task direction:
- ask HUMAN confirm

If custom lens seems reusable:
- mark as capture candidate
- do not auto-add to full catalog

---

## 14. Anti-patterns

## 14.1. Treating starter lenses as full catalog
Bad:
- “If no preset lens matches, AI cannot proceed.”

Correct:
- AI may create runtime/custom lens or expand existing lens.

## 14.2. Treating lens as hard scope
Bad:
- “Design Review Lens means AI must not check requirement.”

Correct:
- AI may expand to Requirement Understanding Lens if needed.

## 14.3. Treating lens as AIP Template
Bad:
- “Test Design Lens defines all testcase creation steps.”

Correct:
- Lens guides knowledge routing. AIP Template/Working AIP define execution.

## 14.4. Treating lens as Wiki Meta / Index
Bad:
- “Lens stores source pointers.”

Correct:
- Wiki Meta / Index stores routing metadata. Lens uses it.

## 14.5. Over-confirming lens
Bad:
- asking HUMAN to confirm every obvious lens.

Correct:
- confirm when ambiguous/high-impact/custom/expansion affects scope.

---

## 15. AI behavior rules

AI should:
- use starter lenses as default examples
- infer lens when task intent is obvious
- combine primary/secondary lens when needed
- propose custom/runtime lens when task does not fit presets
- explain lens only when useful
- confirm high-impact/custom lens
- expand lens when initial lens is too narrow

AI should not:
- limit search only to the starter lens
- require preset match before working
- treat starter lens examples as complete catalog
- treat lens as execution plan
- auto-capture custom lens into Knowledge Hub

---

## 16. Non-goals and limits

TL-04 does not define:
- full lens catalog
- lens registry
- lens ID schema
- lens scoring/ranking
- lens orchestration/composition engine
- telemetry
- UI selector
- automated lens expansion algorithm

These may be addressed in later sprint/version if needed.

---

---

## Intent-first use of starter lenses

Starter lenses are examples selected based on intent, not keyword.

The starter lens quick guide should be applied only after AI has identified the user's task intent.

Example:

```text
Keyword: login
```

Do not immediately choose a lens.

First identify intent:

| Intent | Suitable starter lens |
|---|---|
| Understand customer requirement | Requirement Understanding Lens |
| Review Basic/Detail Design | Design Review Lens |
| Create testcase viewpoints | Test Design Lens |
| Find implementation logic | Code Investigation Lens |
| Verify exact source wording | Source Verification Lens |

Therefore, starter lenses are not keyword mappings. They are intent-based routing viewpoints.

Principle:

> Starter lenses help after intent is clear; they do not replace intent clarification.

## 17. Open points

TL-04 hiện không có open point nền mới.

Potential future decisions:
- whether to promote starter lenses into formal catalog
- custom lens capture template
- lens registry metadata
- lens scoring/readiness
- lens usage telemetry

These are deferred.

---

## Intent-first impact on starter lens examples

This update prevents misuse of starter lenses as a rigid lookup table.

- Same topic/keyword can map to different lenses.
- AI should identify task intent first.
- Starter lens examples are used after intent is clear.
- If no starter lens fits the confirmed intent, AI may propose custom/runtime lens.

## 18. Conclusion

TL-04 provides starter lens examples sufficient for MVP:

1. Requirement Understanding Lens
2. Design Review Lens
3. Test Design Lens
4. Code Investigation Lens
5. Knowledge Capture Lens
6. Source Verification Lens
7. Planning / WBS Lens

These lenses are examples/minimal presets, not a full catalog.

They guide AI knowledge routing while preserving the guardrail that AI may look broader or expand lens when needed.

This is sufficient to proceed to TL-05: Lens Selection / Confirmation / Expansion Rule.


---

## 3. Selection / confirmation / adjustment / no-lens guidance

# AIWS_TL-05_TASK_LENS_SELECTION_CONFIRMATION_EXPANSION_RULE_v2

Status: Draft  
Sprint: Task Lens Minimal Spec Sprint  
Baseline:
- AI Work System MVP v0.9.5
- Task Lens sprint backlog v4
- TL-01 Task Lens Concept & Purpose
- TL-02 Task Lens Ownership & Boundary
- TL-03 Task Lens Minimal Runtime Flow
- TL-04 Task Lens Starter Examples / Minimal Presets
- Core Principles / Sprint Alignment Checklist v3

Change from v3:
- Added No-Lens / AI-decides-search-scope option.
- Clarified explicit Task Lens is optional in MVP.
- Clarified AI may avoid explicit lens if it may narrow search incorrectly or reduce output quality.

Change from v2:
- Added HUMAN runtime lens adjustment rule.
- Clarified flow: HUMAN inputs task → AI confirms intent → AI proposes Task Lens → HUMAN may adjust Task Lens → AI uses adjusted lens.
- Clarified this is allowed when HUMAN wants it, but not mandatory default behavior for every task.

Change from v1:
- Added Intent-first rule.
- Clarified that Task Lens must be selected only after task intent is clear enough.
- Added rule that if intent is unclear, AI must clarify / infer / confirm intent before choosing lens.
- Clarified that lens must not be selected from keyword alone.

---

## 1. Purpose of TL-05

TL-05 chốt rule tối thiểu về:

- intent-first rule before Task Lens selection
- Task Lens selection
- HUMAN confirmation
- selected lens recording
- HUMAN runtime lens adjustment
- No-Lens / AI-decides-search-scope option
- lens expansion / adjustment
- custom/runtime lens handling

Mục tiêu:
- giúp AI chọn lens đủ chủ động
- đảm bảo lens selection dựa trên task intent, không chỉ keyword
- không bắt HUMAN confirm quá nhiều việc nhỏ
- vẫn giữ HUMAN gate ở các điểm ảnh hưởng direction/scope
- đảm bảo Task Lens không trở thành hard scope limiter
- cho phép AI mở rộng lens khi lens hiện tại quá hẹp
- giữ selected lens trace khi có ảnh hưởng task direction

TL-05 không nhằm:
- tạo automatic lens selection algorithm
- tạo lens scoring/ranking
- tạo lens orchestration engine
- tạo full lens registry
- tạo UI lens selector
- tạo telemetry framework

---

## 2. Core rule

Task Lens selection trong MVP dùng nguyên tắc:

> Intent first. Lens is optional support.

Nghĩa là:

> AI may select or propose a Task Lens only after the task intent is clear enough to choose a suitable viewpoint. However, AI may also choose not to use an explicit lens if doing so is safer for search/reasoning quality.

Nếu task intent chưa rõ:
- AI không được vội chọn Task Lens chỉ dựa trên keyword
- AI phải clarify / infer / confirm intent trước
- sau đó mới chọn hoặc đề xuất Task Lens phù hợp

Sau khi intent đã rõ:

> AI may infer the Task Lens when the task intent is clear. HUMAN confirmation is required only when the lens choice is ambiguous, high-impact, custom, or when lens expansion changes task direction/scope.

Đồng thời:

> Task Lens guides attention and knowledge routing, but must not mechanically restrict AI's search/reasoning scope.

---

## 3. Intent-first rule

## 3.1. Task intent must be clear before selecting Task Lens

Task Lens là viewpoint để route task → knowledge.

Vì vậy, Task Lens selection phải dựa trên task intent.

AI cần xác định trước:
- user muốn làm loại task gì
- expected output là gì
- task đang ở mode/phase nào nếu có liên quan
- target artifact/source là gì nếu đã rõ
- task cần knowledge routing hay không
- rủi ro nếu hiểu sai intent là gì

Nếu các điểm này chưa đủ rõ, AI nên clarify intent trước thay vì chọn lens vội.

## 3.2. Do not select lens from keyword alone

Cùng một keyword có thể map tới nhiều intent.

Ví dụ keyword `login` có thể là:
- hiểu requirement login
- review design login
- tạo testcase login
- điều tra code login
- verify source về login

Do đó AI không nên chọn Task Lens chỉ vì keyword xuất hiện.

## 3.3. Intent clarification comes before lens confirmation

Nếu user request ambiguous, câu hỏi đầu tiên nên là xác nhận intent, không phải xác nhận lens kỹ thuật.

Ví dụ:

```text
User: Check login.

AI: Bạn muốn check login theo hướng nào: requirement, design review, testcase, hay code investigation?
Nếu mục tiêu là review tài liệu design, tôi sẽ dùng Design Review Lens.
```

## 3.4. If AI can safely infer intent, it can select lens

Nếu intent đủ rõ từ câu yêu cầu, AI có thể chọn lens tương ứng mà không cần hỏi.

Ví dụ:

```text
User: Hãy review Basic Design cho chức năng login.
Intent: design review
Task Lens: Design Review Lens
```

---

## 4. Selection rule

## 4.1. AI can infer lens when intent is clear

AI có thể tự infer lens nếu:
- task intent đã rõ
- user request rõ task type
- expected output rõ
- source/knowledge target tương đối rõ
- risk của việc chọn sai lens thấp
- lens chỉ dùng để guide knowledge routing, không đổi task scope

Ví dụ:

```text
User: Hãy review Basic Design cho chức năng login.
Inferred lens: Design Review Lens
```

```text
User: Tạo testcase viewpoints cho chức năng login.
Inferred lens: Test Design Lens
```

```text
User: Tìm logic allocation nằm ở source nào.
Inferred lens: Code Investigation Lens
```

Trong các case này, AI không cần hỏi HUMAN confirm lens trước nếu intent/direction đã rõ.

## 4.2. AI should infer primary lens first

AI nên chọn primary lens dựa trên main task intent.

Ví dụ:
- review design → Design Review Lens
- clarify requirement → Requirement Understanding Lens
- create testcases → Test Design Lens
- investigate code → Code Investigation Lens
- capture knowledge → Knowledge Capture Lens
- verify source → Source Verification Lens
- plan work → Planning / WBS Lens

## 4.3. Secondary lens can be used when naturally needed

AI có thể dùng secondary lens nếu task cần nhiều viewpoint.

Ví dụ:
```markdown
Primary lens: Design Review Lens
Secondary lens: Requirement Understanding Lens
Reason: Review must verify Basic Design against requirement.
```

Không cần HUMAN confirm nếu secondary lens chỉ là verification/support nhỏ và không đổi task scope đáng kể.

---

## 5. Confirmation rule

## 5.1. When HUMAN confirmation is required

AI nên hỏi HUMAN confirm khi:

### 1. Task intent is ambiguous
User request có thể hiểu theo nhiều intent/lens khác nhau.

Ví dụ:
```text
User: Check login.
```

Possible intents:
- requirement clarification
- design review
- testcase review
- code investigation

AI nên clarify intent trước, rồi mới chọn lens.

### 2. Lens choice affects task direction
Lens làm thay đổi:
- loại output
- source area chính
- cách review
- deliverable
- AIP Template candidate
- Working AIP basis

### 3. Custom/runtime lens is introduced
Nếu AI đề xuất lens không thuộc starter examples và lens ảnh hưởng direction, nên confirm.

### 4. Lens expansion significantly broadens scope
Nếu AI muốn mở rộng từ lens ban đầu sang source/knowledge area lớn hơn, cần confirm.

### 5. Lens may increase effort/token significantly
Nếu mở rộng lens làm task lớn hơn đáng kể, cần confirm.

### 6. Lens may affect a decision gate
Nếu lens selection ảnh hưởng decision quan trọng, HUMAN cần confirm.

---

## 6. Confirmation phrasing

Confirmation nên ngắn gọn, đủ lý do và rủi ro.

## 6.1. Intent clarification before lens

```text
Tôi chưa rõ bạn muốn “check login” theo hướng nào: requirement, design review, testcase hay code investigation.
Nếu mục tiêu là review tài liệu design, tôi sẽ dùng Design Review Lens. Bạn muốn đi theo hướng nào?
```

## 6.2. Lens expansion confirmation

```text
Tôi đang dùng Design Review Lens, nhưng để tránh review lệch requirement, tôi muốn mở rộng thêm Requirement Understanding Lens để verify requirement source.
Bạn OK không?
```

## 6.3. Custom lens confirmation

```text
Task này có vẻ cần một custom lens: COBOL Migration Compatibility Lens.
Lý do là cần kiểm tra compatibility giữa FACOM/NetCOBOL, không chỉ code investigation thông thường.
Bạn OK dùng lens này cho task hiện tại không?
```

## 6.4. High-impact confirmation

```text
Nếu mở rộng sang Code Investigation Lens, scope sẽ chuyển từ review design sang kiểm tra implementation.
Điều này có thể làm task lớn hơn. Bạn muốn mở rộng luôn hay giữ trong phạm vi design review?
```

---

## 7. Recording rule

## 7.1. When to record selected lens

Không cần record mọi lens.

Nên record khi:
- HUMAN đã confirm lens
- lens ảnh hưởng task direction
- lens expansion/adjustment đã xảy ra
- custom/runtime lens được dùng
- lens ảnh hưởng AIP Template selection
- lens ảnh hưởng Working AIP basis
- trace cần cho review/replay

## 7.2. Where to record

Có thể record vào:
- Workspace
- Working AIP
- task execution notes
- sprint delta docs nếu liên quan design discussion

Không nên record vào Knowledge Hub nếu lens chỉ là runtime decision tạm thời.

## 7.3. Minimal record format

```markdown
## Task Lens
- Task intent: Design review
- Primary lens: Design Review Lens
- Secondary/expanded lens: Requirement Understanding Lens
- Reason: Need to verify Basic Design against upstream requirement.
- Confirmed by HUMAN: yes
- Impact: affects review source scope
- Date: 2026-04-25
```

---

## 8. HUMAN runtime lens adjustment rule

## 8.1. HUMAN may adjust Task Lens after AI proposal

Allowed flow:

```text
HUMAN inputs task
  ↓
AI clarifies / infers / confirms task intent
  ↓
AI proposes suitable Task Lens
  ↓
HUMAN adjusts Task Lens if desired
  ↓
AI uses the HUMAN-adjusted Task Lens during task execution/support
```

This is not the default mandatory behavior for every task.  
It is an allowed adjustment path when HUMAN wants to control the task viewpoint/direction.

## 8.2. Adjustment examples

### Example A — replace lens
```text
AI proposal: Design Review Lens
HUMAN adjustment: Requirement Understanding Lens
Reason: The real intent is to clarify requirement, not review design.
```

### Example B — add secondary lens
```text
AI proposal: Test Design Lens
HUMAN adjustment: Add Source Verification Lens
Reason: Exact expected result must be verified from source.
```

### Example C — custom runtime lens
```text
AI proposal: Code Investigation Lens
HUMAN adjustment: COBOL Migration Compatibility Lens
Reason: Need compatibility viewpoint specific to FACOM → NetCOBOL migration.
```

## 8.3. AI behavior after HUMAN adjustment

AI should:
- follow the HUMAN-adjusted lens
- use it for knowledge routing and task support
- record it if it affects task direction or Working AIP basis
- warn if the adjusted lens seems inconsistent with confirmed intent
- propose expansion if the adjusted lens is too narrow
- preserve raw/source verification when exactness/evidence matters

AI should not:
- ignore HUMAN-adjusted lens silently
- treat HUMAN adjustment as permanent catalog update
- auto-promote custom adjusted lens
- use adjusted lens as hard scope limiter

## 8.4. Relationship with intent-first rule

HUMAN adjustment happens after intent is clear enough.

If HUMAN changes the lens in a way that implies a different task intent, AI should confirm whether intent has also changed.

Example:

```text
AI: Intent is design review, proposed Design Review Lens.
HUMAN: Use Code Investigation Lens instead.
AI: Understood. Does this mean you want to shift from design review to code investigation?
```

---

## 9. No-Lens / AI-decides-search-scope option

## 9.1. Explicit Task Lens is optional in MVP

Task Lens is useful routing support, but it is not mandatory for every task.

Because Task Lens is not fully designed/tested in MVP, AI may choose the **No-Lens / AI-decides-search-scope option** when an explicit lens could reduce output quality.

## 9.2. When to use No-Lens option

Use No-Lens option when:
- lens choice is uncertain
- available starter lenses do not fit
- explicit lens may narrow search scope incorrectly
- task requires broad exploration
- task is simple and lens adds overhead
- HUMAN did not request lens control
- AI can better preserve quality by deciding search scope directly from intent

## 9.3. How AI should behave in No-Lens mode

AI should:
- confirm/clarify intent if needed
- decide search/reasoning scope directly from intent
- search broadly enough to avoid missing important context
- verify raw/source when exactness/evidence matters
- use Working AIP when execution guardrail is needed
- explain No-Lens choice if it affects traceability or direction

AI should not:
- use No-Lens as excuse for unstructured reasoning
- skip source verification
- ignore Knowledge Hub/Wiki Meta when relevant
- avoid HUMAN confirmation for high-impact scope decisions

## 9.4. Relationship with HUMAN adjustment

If HUMAN wants to adjust lens, AI should follow the HUMAN-adjusted lens.

If AI believes the HUMAN-adjusted lens may be too narrow, AI should explain the risk and suggest:
- add secondary lens
- expand scope
- or use No-Lens / broad intent-based search for part of the task

---

## 10. Expansion rule

## 8.1. Task Lens is not a hard scope limiter

Task Lens không được ngăn AI:
- kiểm tra source liên quan
- mở rộng reasoning khi cần
- phát hiện dependency ngoài lens
- verify raw/source
- xem broader context để tránh sai hướng

## 8.2. When AI may expand lens

AI có thể đề xuất mở rộng/điều chỉnh lens khi:
- current lens không đủ để đạt task goal
- source/knowledge route bị dead-end
- phát hiện missing upstream/downstream dependency
- có conflict giữa artifacts
- cần raw/source verification
- task output có rủi ro nếu chỉ nhìn theo lens hiện tại
- HUMAN goal implies broader context

## 8.3. Expansion types

- Add secondary lens
- Switch primary lens
- Temporary verification lens
- Custom/runtime lens
- Broaden source/knowledge area

---

## 11. Expansion confirmation rule

## 9.1. No confirmation needed for small support expansion

AI không cần confirm nếu:
- expansion nhỏ
- chỉ để verify một source obvious
- không đổi deliverable
- không đổi task direction
- effort/token tăng không đáng kể

Ví dụ:
- Design Review Lens mở requirement source để confirm one branch condition.

## 9.2. Confirmation needed for direction-affecting expansion

AI cần confirm nếu:
- mở rộng sang một workstream khác
- task output sẽ thay đổi
- effort/token tăng đáng kể
- deliverable scope thay đổi
- Working AIP cần update
- custom/runtime lens được tạo

## 9.3. AI should explain expansion reason

AI nên nêu:
- current intent/lens
- proposed expansion
- reason
- risk if not expanded
- impact on scope/effort/output

---

## 12. Custom/runtime lens rule

## 10.1. When to create custom/runtime lens

Custom/runtime lens có thể tạo khi:
- starter lenses không đủ
- task có domain-specific viewpoint
- HUMAN yêu cầu một hướng review đặc biệt
- repeated task pattern xuất hiện
- cần phối hợp nhiều lens thành một viewpoint tạm

Examples:
- COBOL Migration Compatibility Lens
- Manufacturing Allocation Review Lens
- Security Impact Review Lens
- AIWS Sprint Closure Lens

## 10.2. Custom lens should be lightweight

MVP chưa cần full schema.

Custom/runtime lens có thể mô tả bằng:

```markdown
## Runtime Task Lens
- Name:
- Purpose:
- When to use:
- Preferred knowledge targets:
- Verification triggers:
- Boundary:
```

## 10.3. Capture candidate rule

Nếu custom lens có khả năng reuse:
- mark as capture candidate
- không auto-promote vào full catalog
- controlled capture nếu muốn đưa vào Knowledge Hub / methodology guide

---

## 13. AIP Template influence rule

Task Lens có thể influence/suggest AIP Template.

Ví dụ:
```text
Task Lens: Test Design Lens
Suggested AIP Template: Testcase Creation / Test Design AIP
```

Nhưng:
- Task Lens không thay AIP Template
- AIP Template không bị chọn hoàn toàn tự động nếu task high-impact
- nếu template choice quan trọng, HUMAN confirm theo existing AIP rule

---

## 14. Working AIP reflection rule

Nếu intent/lens selection/expansion ảnh hưởng execution basis:
- reflect vào Working AIP hoặc Workspace
- ghi reason nếu cần
- không chỉ giữ trong AI reasoning

Examples:
- mở rộng từ design review sang requirement verification
- dùng custom lens cho COBOL migration compatibility
- thay đổi primary lens từ planning sang execution

---

## 15. Stop / continue rule

## 13.1. AI may stop with current lens when sufficient

Có thể không expand nếu:
- task answer đủ
- source confidence đủ
- no conflict
- no high-impact decision
- no exactness requirement
- lens covers task goal

## 13.2. AI should continue/expand when needed

Nên expand hoặc verify khi:
- answer sẽ thiếu nếu chỉ giữ lens hiện tại
- source evidence cần thiết
- task has downstream impact
- current lens leads to uncertainty
- artifact is stale/needs_review
- user asked for correctness/high confidence

---

## 16. Minimal decision matrix

| Situation | AI action |
|---|---|
| Task intent unclear | clarify / infer / confirm intent first |
| Task intent clear | infer lens |
| Task ambiguous | ask HUMAN to clarify intent and then choose/confirm lens |
| HUMAN adjusts proposed lens | use adjusted lens, and confirm intent if adjustment implies intent change |
| Lens obvious and low-risk | proceed without confirmation |
| Lens affects deliverable/scope | confirm |
| Need small verification | expand lightly without confirmation |
| Need large expansion | confirm |
| Custom lens for one task | confirm if direction-affecting |
| Custom lens reusable | mark capture candidate |
| Lens affects Working AIP | record/reflect |
| Lens trivial | no need to record |
| Explicit lens may reduce quality | use No-Lens / AI-decides-search-scope option |

---

## 17. Examples

## Example A — no confirmation needed

```text
User: Hãy tạo testcase viewpoints cho login requirement.
Intent: testcase viewpoint creation
Lens: Test Design Lens
Action: proceed.
Reason: intent is clear and lens is low-risk.
```

## Example B — intent clarification needed

```text
User: Check login.
AI: Bạn muốn check login theo hướng requirement, design review, testcase, hay code investigation?
Nếu mục tiêu là review tài liệu design, tôi sẽ dùng Design Review Lens.
```

## Example C — small expansion without confirmation

```text
Task: Review Basic Design login.
Intent: design review
Primary lens: Design Review Lens
AI opens requirement Source Understanding Artifact to verify branch condition.
No confirmation needed if scope/output unchanged.
```

## Example D — expansion with confirmation

```text
Task: Review Basic Design login.
AI detects possible code/design mismatch and wants to inspect implementation.
Confirm because this shifts from design review to code investigation.
```

## Example E — custom lens

```text
Task: Check FACOM to NetCOBOL compatibility.
Intent: compatibility investigation
Custom lens: COBOL Migration Compatibility Lens
AI asks HUMAN confirm because this domain-specific lens affects review direction.
```

---

## Example F — No-Lens option

```text
User: Analyze this area and find related issues.
Intent: broad investigation
AI: I will not lock this to a specific Task Lens because the search scope may need to remain broad. I will decide the search scope from the confirmed intent and verify raw/source where needed.
```

---

## Example G — HUMAN adjusts lens

```text
User: Review login.
AI: I understand the intent as design review. Suggested lens: Design Review Lens.
HUMAN: Add Requirement Understanding Lens too.
AI: Understood. I will use Design Review Lens as primary and Requirement Understanding Lens as secondary to verify upstream requirement.
```

---

## 18. AI behavior rules

AI should:
- clarify / infer / confirm task intent before selecting lens when intent is unclear
- infer lens when intent is obvious
- avoid over-confirming trivial choices
- confirm ambiguous/high-impact/custom/large expansion
- record lens only when useful
- use HUMAN-adjusted lens when HUMAN adjusts it
- use No-Lens option when explicit lens may reduce quality
- propose expansion when lens is too narrow
- explain reason/risk when asking confirmation
- preserve raw/source verification
- preserve Working AIP boundary

AI should not:
- choose lens from keyword alone when intent is unclear
- ignore HUMAN-adjusted lens silently
- silently use high-impact custom lens
- force an explicit lens when No-Lens would better preserve search/reasoning quality
- treat lens as hard scope limiter
- block necessary exploration
- expand scope significantly without confirmation
- record every trivial lens
- treat lens as AIP Template
- treat custom lens as reusable catalog entry without capture

---

## 19. Non-goals and limits

TL-05 does not define:
- full lens selection algorithm
- scoring/ranking
- orchestration engine
- UI selector
- lens registry
- telemetry
- full reusable lens lifecycle

These are deferred.

---

## 20. Open points

TL-05 hiện không có open point nền mới.

Potential future decisions:
- exact custom lens capture template
- lens registry format
- scoring and telemetry
- standard lens record format
- relation with future testing framework

These are deferred.

---

## 21. Conclusion

TL-05 chốt Task Lens operation rules:

- Intent first, lens second.
- AI must clarify / infer / confirm task intent before selecting Task Lens when intent is unclear.
- AI can infer obvious lens when intent is clear.
- HUMAN confirms ambiguous/high-impact/custom lens.
- Selected lens is recorded only when it affects direction or traceability.
- HUMAN may adjust the proposed runtime lens when desired.
- AI uses the HUMAN-adjusted lens while still warning/expanding if needed.
- AI may choose No-Lens / AI-decides-search-scope option when explicit lens may reduce quality.
- AI may expand/adjust lens when current lens is too narrow.
- Expansion that affects scope/direction requires confirmation.
- Custom/runtime lens is allowed but not auto-promoted.
- Task Lens can influence AIP Template but never replaces it.
- Working AIP must reflect intent/lens decisions that affect execution basis.

This is sufficient to proceed to TL-06: Relation to Wiki Meta / Index and Knowledge Hub.
