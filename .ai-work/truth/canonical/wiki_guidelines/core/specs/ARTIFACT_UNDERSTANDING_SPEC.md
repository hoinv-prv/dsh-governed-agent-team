# ARTIFACT_UNDERSTANDING_SPEC_v0_1

## 1. Purpose
Artifact Understanding là lớp đầu vào của sprint Wiki, dùng để giúp AI hiểu các artifacts hiện có của dự án theo cách có thể:
- được BrSE review/chỉnh sửa
- được tái dùng để sinh Wiki profiles
- được tái dùng để build Wiki meta/index
- được tái dùng để customize AIP templates về sau

Artifact Understanding không nhằm thay thế source artifact, mà nhằm tạo một lớp hiểu biết có cấu trúc về artifact.

## 2. Scope in this sprint
Trong sprint này, Artifact Understanding được define ở mức minimal nhưng usable:
- có output structure rõ
- có separation giữa confirmed / inferred / unresolved
- có BrSE review/revise loop
- support các artifact families chính cho BrSE tasks
- support cả supplemental artifacts như Q&A, findings, open points

Không đi sâu trong sprint này vào:
- confidence scoring engine phức tạp
- automation nặng để tự chuẩn hóa toàn bộ artifact
- advanced semantic inference pipeline

## 3. Artifact families in scope

### 3.1. Requirement-side artifacts
- Raw Requirement List
- Q&A List
- Requirement Definition Document

### 3.2. Main project artifacts
- Basic Design
- Detail Design
- IT Testcase
- Meeting Minutes
- Weekly Report

### 3.3. Supplemental artifacts
- findings
- open points
- clarification notes
- review comments summary
- pending decisions
- similar supplemental artifacts

## 4. Foundational principle
Artifact Understanding must separate:
- what is directly grounded in the artifact
- what is inferred by AI
- what remains unresolved or needs BrSE/HUMAN confirmation

The understanding output should be reviewable and revisable by BrSE before it is reused downstream.

## 5. What Artifact Understanding should produce

### 5.1. Minimal goals
For each artifact, the understanding output should help answer:
- What artifact is this?
- What role does it play in the project flow?
- What structure/template does it seem to follow?
- What key objects/concepts/functions does it mention?
- What related artifacts does it point to or imply?
- What is confirmed from the artifact itself?
- What is inferred by AI?
- What remains unclear?

### 5.2. Requirement-side special goal
For requirement-side artifacts, the understanding must distinguish:
- raw customer input not yet refined
- clarification/Q&A layer
- refined requirement definition layer

These should not be collapsed too early into a single requirement object.

### 5.3. Supplemental artifact special goal
For supplemental artifacts such as Q&A/findings/open points, the understanding should also identify:
- current status
- reflection status
- whether the content has already been reflected into main project artifacts

## 6. Output model

### 6.1. Core sections
Each artifact understanding output should minimally contain:
- artifact_identity
- artifact_role_understanding
- structure_template_understanding
- key_objects_and_terms
- related_artifacts_and_links
- confirmed_from_artifact
- ai_inference
- unresolved_or_needs_confirmation
- suggested_followup_actions

### 6.2. Optional but recommended sections
- alias_candidates
- section_mapping
- traceability_hints
- reuse_value_notes

### 6.3. Supplemental extension
For Q&A and similar supplemental artifacts, the understanding should additionally contain:
- supplemental_status_understanding
- reflection_status_understanding
- reflected_target_docs_understanding
- whether direct future consultation is still likely needed

## 7. Confirmed / Inferred / Unresolved separation

### 7.1. Confirmed from artifact
Information that can be directly grounded in the artifact text/structure/reference.

### 7.2. AI inference
Information suggested by AI based on pattern, structure, wording, or cross-artifact reasoning, but not directly confirmed in the artifact itself.

### 7.3. Unresolved / needs confirmation
Information that remains ambiguous, incomplete, conflicting, or insufficiently grounded.

### 7.4. Rule
AI must not silently merge inferred content into confirmed content.

## 8. BrSE review / revise loop

### 8.1. First pass
AI generates artifact understanding output.

### 8.2. BrSE review
BrSE may:
- confirm sections as-is
- correct incorrect interpretations
- add project-specific clarification
- request restructuring of understanding
- explicitly mark some AI inference as accepted or rejected

### 8.3. AI revise
AI updates the understanding output accordingly.

### 8.4. Result
Only after this loop should the understanding be reused as a strong basis for:
- Wiki profile generation
- Wiki meta/index build
- AIP template customization
- task execution support

## 9. Requirement-side artifact rules

### 9.1. Raw Requirement List
Should be understood as:
- customer-origin input
- not yet fully refined
- possibly inconsistent / incomplete / vague
- not necessarily sufficient as the final source used in downstream design work

### 9.2. Q&A List
Should be understood as:
- clarification layer between raw customer input and refined requirement understanding
- may contain active unresolved items
- may also contain resolved items already reflected into later artifacts

### 9.3. Requirement Definition Document
Should be understood as:
- refined requirement artifact
- likely the stabilized downstream-facing requirement layer
- usually influenced by prior Q&A and clarification

### 9.4. Rule
AI should preserve the distinction between these three layers in understanding output.

## 10. Supplemental artifact rules

### 10.1. Examples
- Q&A
- findings
- open points
- clarification notes
- review comments summary
- pending decisions

### 10.2. Why they are special
These artifacts often carry temporary, transitional, or refinement-state information.
Their usefulness depends not only on content, but also on whether the content has already been reflected into main artifacts.

### 10.3. Reflection-aware understanding
For supplemental artifacts, understanding should try to capture:
- Is the item still active?
- Has it been answered/resolved?
- Has it been reflected into another artifact?
- If reflected, where?
- If reflected, is direct future reading still required by default?

## 11. Reuse rule
Artifact Understanding outputs are intended to be reusable by downstream flows, but:
- they do not replace source artifacts
- they should be treated as structured project understanding
- their maturity depends on whether BrSE has reviewed them

## 12. Out of scope for this sprint
- automatic artifact canonicalization
- deep conflict resolution across many artifacts
- advanced scoring for understanding confidence
- automated approval workflows for understanding acceptance

## 13. Completion criteria for BL-01
BL-01 is considered done when:
- artifact families in scope are clearly defined
- output structure is clearly defined
- confirmed / inferred / unresolved separation is clearly defined
- BrSE review / revise loop is clearly defined
- requirement-side and supplemental artifact special rules are explicitly captured
