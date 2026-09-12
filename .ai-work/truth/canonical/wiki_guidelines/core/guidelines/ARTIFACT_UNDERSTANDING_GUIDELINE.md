# ARTIFACT_UNDERSTANDING_GUIDELINE_v0_1

## 1. Purpose
Guideline này hướng dẫn cách AI và BrSE thực hiện flow **Artifact Understanding** trong sprint Wiki.

Nó giúp:
- hiểu artifacts hiện có của dự án theo cấu trúc rõ ràng
- tách rõ confirmed / inferred / unresolved
- cho BrSE review và chỉnh sửa
- tạo understanding có thể tái dùng cho các bước sau như:
  - build Wiki Meta / Index
  - build/update Wiki Knowledge Profile
  - customize AIP templates
  - dùng làm grounding cho task execution

## 2. When to use
Dùng guideline này khi:
- dự án đã có artifact hiện có và cần AI hiểu chúng
- cần tạo initial knowledge foundation cho Wiki
- cần hiểu lại một artifact trước khi build/update Wiki
- AI/BrSE thấy artifact hiện tại chưa rõ structure / scope / relation

Không dùng guideline này khi:
- chỉ cần trả lời một câu hỏi rất nhỏ, không cần formal understanding
- đã có understanding đủ tốt và chỉ cần update một field nhỏ

## 3. Inputs
Một hoặc nhiều trong các input sau:
- source artifact
- project overview
- artifact relation model nếu có
- alias/object mapping nếu có
- prior related Wiki Meta / Index nếu có
- prior notebook findings nếu có

### Important rule
Artifact Understanding không được thay thế source artifact.
Source artifact vẫn là grounding layer chính.

## 4. Artifact families to handle
Flow này nên support tối thiểu:

### Requirement-side
- Raw Requirement List
- Q&A List
- Requirement Definition Document

### Main project artifacts
- Basic Design
- Detail Design
- IT Testcase
- Meeting Minutes
- Weekly Report

### Supplemental artifacts
- findings
- open points
- clarification notes
- review comments summary
- pending decisions
- similar supplemental artifacts

## 5. Output expectations
A usable artifact understanding output should minimally contain:
- artifact identity
- artifact role understanding
- structure/template understanding
- key objects and terms
- related artifacts and links
- confirmed_from_artifact
- ai_inference
- unresolved_or_needs_confirmation
- suggested_followup_actions

If the artifact is supplemental, also include:
- current status understanding
- reflection status understanding
- reflected target docs understanding
- whether direct future consultation is still needed by default

## 6. Core execution flow

### Step 1 — Identify artifact type candidate
AI should first identify:
- artifact family
- artifact type candidate
- whether this is a requirement-side, main, or supplemental artifact

### Step 2 — Understand artifact role
AI should describe:
- what role this artifact likely plays
- where it sits in the project flow
- likely upstream/downstream relation

### Step 3 — Understand structure/template
AI should identify:
- section structure
- template shape
- document organization hints
- signs of project-specific formatting

### Step 4 — Extract key objects and terms
AI should surface:
- functions
- screens
- batches
- APIs
- tables
- business rules
- aliases or naming variations

### Step 5 — Identify related artifacts and links
AI should surface:
- explicit references
- inferred likely relations
- traceability hints

### Step 6 — Separate confirmed / inferred / unresolved
AI must clearly separate:
- directly grounded findings
- AI inference
- unclear or conflicting points

### Step 7 — Suggest follow-up if needed
If artifact is weak/incomplete/unclear, AI may suggest:
- additional artifact to open
- unresolved note
- alias candidate
- later Wiki candidate / meta update candidate

## 7. Special handling rules

### 7.1. Requirement-side rule
Do not collapse too early:
- Raw Requirement
- Q&A clarification
- Requirement Definition

These represent different refinement layers.

### 7.2. Q&A rule
Q&A is not just a log.
AI should understand:
- clarification topic
- answer state
- whether content seems reflected into later artifacts

### 7.3. Supplemental artifact rule
For findings/open points/clarification notes and similar artifacts,
AI should identify:
- current status
- reflection status
- whether direct future reading is still needed

### 7.4. Resolved vs reflected rule
Do not assume:
- resolved = reflected

These must stay distinct when possible.

## 8. BrSE review / revise loop

### First pass
AI produces the initial understanding draft.

### BrSE review
BrSE may:
- confirm understanding
- correct wrong interpretation
- add project-specific clarification
- reject an inference
- request restructure

### AI revise
AI updates the understanding draft accordingly.

### Rule
Only after this review/revise loop should the understanding be treated as a strong reusable basis.

## 9. Grounding rules

### 9.1. Confirmed from artifact
Only put something in this section when directly grounded in the artifact.

### 9.2. AI inference
Keep AI inference separate.
Do not silently merge it into confirmed findings.

### 9.3. Unresolved
If the artifact is unclear, incomplete, or conflicting,
preserve that uncertainty explicitly.

### 9.4. Conservative behavior
When in doubt:
- be explicit
- keep uncertainty visible
- avoid over-collapsing layers or objects

## 10. Reuse rules
Artifact Understanding outputs may later be reused for:
- Wiki Meta / Index build
- Wiki Knowledge Profile build/update
- AIP customization
- task preparation

But:
- they do not replace source artifacts
- they are stronger after BrSE review
- they should remain traceable to source basis

## 11. Common pitfalls
- treating requirement layers as one flat artifact
- ignoring reflection status for Q&A / supplemental artifacts
- mixing inference into confirmed findings
- assuming one artifact is self-sufficient when link chain is incomplete
- over-summarizing away useful traceability clues

## 12. If missing then do
If understanding is weak because artifact is insufficient:
- mark unresolved
- suggest related artifact lookup
- preserve missing linkage explicitly
- create alias candidate if naming is unclear
- do not force certainty

## 13. Relationship with other sprint artifacts
This guideline is intended to work with:
- `ARTIFACT_UNDERSTANDING_SPEC_v0_1`
- `ARTIFACT_UNDERSTANDING_OUTPUT_SCHEMA_v0_1`
- `SUPPLEMENTAL_ARTIFACT_STATUS_REFLECTION_MODEL_v0_1`
- `WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1`
- `WIKI_META_INDEX_SPEC_v0_2`

## 14. Completion criteria for BL-10
BL-10 guideline part is considered done when:
- execution flow is clear
- requirement-side handling is clear
- supplemental handling is clear
- BrSE review/revise loop is clear
- grounding rules are clear
