# AIWS_SU-07_SOURCE_UNDERSTANDING_ARTIFACT_USAGE_EXAMPLES_v1

Status: Draft  
Sprint: Source Understanding Artifact Minimal Spec Sprint  
Baseline:
- AI Work System MVP v0.9.4
- Source Understanding Artifact sprint backlog v2
- SU-01 Source Understanding Artifact Concept & Purpose
- SU-02 Source Understanding Artifact Ownership & Boundary
- SU-03 Source Understanding Artifact Granularity & Source Scope Rule
- SU-04 Source Understanding Artifact Minimal Content Model
- SU-05 Source Understanding Artifact Provenance / Authority / Freshness Rule
- SU-06 Source Understanding Artifact Relation to Wiki Meta / Index and Knowledge Hub
- Source Understanding Artifact Samples v1

---

## 1. Purpose of SU-07

SU-07 cung cấp usage examples cho **Source Understanding Artifact**.

Mục tiêu:
- minh họa artifact này dùng như thế nào với nhiều loại source khác nhau
- giúp BrSE/HUMAN/AI phân biệt Source Understanding Artifact với raw/source, retrieval summary, Workspace findings, Personal Notebook và Knowledge Hub synthesis
- làm rõ khi nào artifact đủ dùng và khi nào phải quay lại raw/source
- cung cấp base examples để đưa vào appendix/reference khi merge canonical docs

SU-07 không nhằm:
- định nghĩa final schema mới
- thay thế SU-04 content model
- tạo full example library
- tạo automation pipeline
- tạo testing dataset

---

## 2. Example coverage

SU-07 gồm 5 loại example chính:

1. Requirement source
2. Basic Design section
3. Meeting / Q&A source
4. Code module source
5. External reference source

Các example đều giữ guardrail:
- raw/source remains source of truth
- artifact is reusable understanding, not source itself
- artifact includes source pointer / source scope / understanding date
- artifact includes status / authority / freshness hints
- artifact includes verification triggers

---

## 3. Usage examples

# AIWS_SOURCE_UNDERSTANDING_ARTIFACT_SAMPLES_v1

Status: Draft samples  
Sprint: Source Understanding Artifact Minimal Spec Sprint  
Related:
- SU-01 Source Understanding Artifact Concept & Purpose
- Backlog v2

---

## 1. Purpose

Tài liệu này cung cấp một vài sample để minh họa **Source Understanding Artifact**.

Các sample này **không phải schema chính thức cuối cùng**.  
Mục đích là giúp hình dung artifact này sẽ trông như thế nào trong thực tế.

Guardrails:
- raw/source vẫn là source of truth
- artifact chỉ là reusable understanding
- phải có source pointer / source scope / understanding date
- cần status / authority / freshness hint nhẹ
- nếu cần exact wording/value thì phải quay lại source

---

# Sample 1 — Requirement Source Understanding Artifact

```markdown
# Source Understanding Artifact: Login Requirement Overview

## Artifact metadata
- Artifact ID: SUA-REQ-LOGIN-001
- Artifact type: Source Understanding Artifact
- Status: draft_understanding
- Authority: source_backed_summary
- Freshness: current_as_of_extraction
- Understanding date: 2026-04-25
- Last reviewed: 2026-04-25
- Created by: AI + BrSE review pending

## Source reference
- Source pointer: `requirements/login/REQ_LOGIN_v1.md`
- Source scope: Section 2.1 "Login behavior" ~ Section 2.4 "Redirect rule"
- Source type: Requirement definition document
- Line-level provenance: not recorded
- Source of truth: raw requirement document

## Purpose
Giữ lại understanding ngắn gọn về requirement login để dùng lại trong các task:
- review basic design
- create detail design
- create test viewpoints
- clarify Q&A with customer

## Compact understanding
Login function requires the system to validate user input, handle empty/wrong credentials, and redirect the user based on the original screen/source route after successful login. Error handling must distinguish between missing input and invalid authentication.

## Key reusable points
1. Empty user ID/password must be handled before authentication.
2. Wrong credentials must return authentication error, not system error.
3. Successful login should redirect according to the original requested screen if available.
4. If no original screen exists, redirect to the default top menu.
5. Error messages may require customer confirmation if wording is not finalized.

## Important conditions / branches
- IF user ID or password is empty:
  - show input validation error
  - do not call authentication service
- ELSE IF credentials are invalid:
  - show authentication error
  - remain on login screen
- ELSE IF credentials are valid and source screen exists:
  - redirect to source screen
- ELSE:
  - redirect to default top menu

## Known uncertainties
- Exact Japanese error message wording is not finalized.
- Session timeout behavior is mentioned elsewhere and should not be inferred from this section.
- Password lockout policy is not included in this source scope.

## Reuse guidance
Use this artifact for:
- high-level design understanding
- review viewpoint generation
- testcase idea generation

Do not use this artifact for:
- exact wording
- final message text
- security policy decision
- implementation detail without checking detailed design/source

## Verification trigger
Open raw/source if:
- exact error message wording is needed
- branch condition is disputed
- customer asks for source evidence
- design differs from this understanding
```

---

# Sample 2 — Basic Design Section Understanding Artifact

```markdown
# Source Understanding Artifact: Manufacturing Order Allocation Flow

## Artifact metadata
- Artifact ID: SUA-BD-MFG-ALLOC-001
- Artifact type: Source Understanding Artifact
- Status: reviewed_understanding
- Authority: source_backed_summary
- Freshness: current_as_of_extraction
- Understanding date: 2026-04-25
- Last reviewed: 2026-04-25
- Created by: AI
- Reviewed by: BrSE pending

## Source reference
- Source pointer: `basic_design/manufacturing_order/BD_MFG_ORDER.md`
- Source scope: Section 4.3 "Inventory allocation on release"
- Source type: Basic design document
- Line-level provenance: optional / not recorded
- Source of truth: basic design source document

## Purpose
Giữ reusable understanding về flow 引当 khi 製造指図 được release, để dùng lại trong:
- detail design review
- database sequence review
- inventory common component discussion
- testcase viewpoint creation

## Compact understanding
When a manufacturing order is released, the system checks required materials and requests inventory allocation. Allocation may be full, partial, or unavailable. The result affects manufacturing order status and material usage plan. Inventory update must avoid double allocation and preserve transaction consistency.

## Key reusable points
1. Allocation is triggered by manufacturing order release.
2. Required materials come from manufacturing order detail / BOM-derived usage plan.
3. Allocation result patterns:
   - full allocation
   - partial allocation
   - unavailable / shortage
4. Inventory allocation should update allocation records and available stock consistently.
5. Manufacturing order status may depend on allocation result.
6. Transaction boundary and locking are important to avoid double allocation.

## Related concepts
- Manufacturing Order
- Material Usage Plan
- Inventory Allocation
- Inventory Common Component
- Allocation Detail
- Equipment Load is not directly updated in this section

## Known uncertainties
- Exact DB table names should be verified against DB design.
- Error handling for partial allocation may differ by customer operation rule.
- FIFO/location/lot allocation priority may be defined in another source.

## Reuse guidance
Use this artifact for:
- understanding the allocation flow
- identifying related design sections
- preparing review viewpoints

Do not use this artifact as:
- final DB design source
- exact table/column mapping
- implementation pseudo-code without checking detailed design

## Verification trigger
Open raw/source if:
- exact status transition is required
- DB table/column names are needed
- allocation priority rules are disputed
- transaction/locking design must be confirmed
```

---

# Sample 3 — Meeting / Q&A Source Understanding Artifact

```markdown
# Source Understanding Artifact: Q&A on Inventory Planned Date Update

## Artifact metadata
- Artifact ID: SUA-QA-INVENTORY-DATE-001
- Artifact type: Source Understanding Artifact
- Status: partial_understanding
- Authority: discussion_backed
- Freshness: may_need_confirmation
- Understanding date: 2026-04-25
- Last reviewed: 2026-04-25
- Created by: AI
- Reviewed by: not reviewed

## Source reference
- Source pointer: `meetings/2026-04-20_inventory_qa.md`
- Source scope: Q&A block "予定日付・実績日付・指図残 update"
- Source type: Meeting Q&A / customer discussion note
- Line-level provenance: not recorded
- Source of truth: original meeting note / customer confirmation

## Purpose
Giữ understanding về Q&A liên quan đến việc update planned date, actual date và remaining instruction quantity, để dùng lại khi:
- viết mail confirm
- update requirement definition
- review design impact
- tạo testcase impact points

## Compact understanding
The discussion indicates that unchanged dates are planned dates only. Actual dates and remaining instruction quantity are updated upon completion. There is an open confirmation point about whether planned date reflection is also mandatory.

## Key reusable points
1. Planned date may remain unchanged depending on operation.
2. Actual date is updated when completion occurs.
3. Remaining instruction quantity is updated when completion occurs.
4. Planned date reflection is a confirmation point, not yet fully decided.
5. Customer confirmation may be required before finalizing design.

## Open points
- Is planned date reflection mandatory?
- If planned date is not reflected, which downstream reports/screens are affected?
- Does this differ between partial completion and full completion?

## Known uncertainties
- This understanding is based on Q&A discussion, not final requirement definition.
- Exact customer answer may be in later email/thread.
- The related design artifact may not yet reflect this Q&A.

## Reuse guidance
Use this artifact for:
- preparing follow-up confirmation
- checking whether requirement/design has reflected Q&A
- identifying test viewpoints

Do not use this artifact as:
- finalized customer requirement
- implementation rule
- source of truth without checking final confirmation

## Verification trigger
Open raw/source if:
- final customer decision is needed
- writing official requirement/design update
- planned date behavior affects release decision
```

---

# Sample 4 — Code Module Source Understanding Artifact

```markdown
# Source Understanding Artifact: Feature Stability Filter Step

## Artifact metadata
- Artifact ID: SUA-CODE-FEATURE-STABILITY-001
- Artifact type: Source Understanding Artifact
- Status: draft_understanding
- Authority: code_backed_summary
- Freshness: needs_update_if_code_changes
- Understanding date: 2026-04-25
- Last reviewed: 2026-04-25
- Created by: AI

## Source reference
- Source pointer: `src/pipeline_steps/feature_stability_filter.py`
- Source scope: `FeatureStabilityFilterStep` class
- Source type: Python source code
- Line-level provenance: optional / not recorded
- Source of truth: source code repository

## Purpose
Giữ reusable understanding về `FeatureStabilityFilterStep` để dùng lại khi:
- sửa pipeline
- viết config YAML
- debug feature selection
- tạo docs cho ML pipeline

## Compact understanding
`FeatureStabilityFilterStep` performs walk-forward time-series cross-validation to evaluate feature stability across folds. It trains a conservative XGBoost model per fold, calculates importance metrics, and selects features based on presence ratio and importance thresholds. It outputs selected features and artifacts such as CSV/JSON reports.

## Key reusable points
1. Uses time-series / walk-forward folds, not random CV.
2. Includes gap to reduce leakage risk.
3. Trains XGBoost with conservative parameters and early stopping.
4. Tracks feature importance by gain/weight/cover.
5. Selects features by stability across folds, not one-off high importance.
6. Outputs selected feature list to pipeline context.
7. Writes report artifacts for review.

## Key inputs
- X_train
- y_train
- feature list
- date/symbol index or columns for fold generation
- config thresholds:
  - presence_ratio
  - min_mean_importance
  - top_k
  - keep/drop lists

## Key outputs
- selected_features
- X_train_filtered
- CSV report
- JSON artifact
- fold-level importance summary

## Known uncertainties
- Exact parameter names must be verified in code.
- Fold generation utility may be external.
- Behavior may differ if MultiIndex is not present.
- Compatibility with latest XGBoost version should be checked.

## Reuse guidance
Use this artifact for:
- understanding purpose and main behavior
- identifying config options to inspect
- onboarding to this pipeline step

Do not use this artifact for:
- exact function signature
- exact parameter name
- exact import path
- bug fixing without reading source code

## Verification trigger
Open raw/source if:
- changing code
- writing exact YAML config
- debugging runtime error
- checking function/class signature
- confirming output artifact names
```

---

# Sample 5 — External Reference Source Understanding Artifact

```markdown
# Source Understanding Artifact: External Article on LLM Wiki Pattern

## Artifact metadata
- Artifact ID: SUA-EXT-LLM-WIKI-001
- Artifact type: Source Understanding Artifact
- Status: reference_understanding
- Authority: external_reference_summary
- Freshness: external_source_may_change
- Understanding date: 2026-04-25
- Last reviewed: 2026-04-25
- Created by: AI

## Source reference
- Source pointer: `references/llm-wiki.md`
- Source scope: full article summary / selected relevant sections
- Source type: external article / reference note
- Line-level provenance: not recorded
- Source of truth: original article or saved reference source

## Purpose
Giữ understanding về LLM Wiki pattern để tham khảo khi thiết kế Knowledge Hub / Wiki-first runtime / controlled capture.

## Compact understanding
The LLM Wiki pattern emphasizes maintaining a knowledge base that LLMs can read and update, allowing useful findings to be captured back into a structured knowledge layer. The concept is useful for AIWS, but AIWS should avoid blind filling-back and should require controlled capture when promoting knowledge.

## Key reusable points
1. LLMs benefit from external knowledge stores beyond pre-trained knowledge.
2. Knowledge should be structured enough for retrieval and reuse.
3. Filling-back can improve future performance but carries risk of incorrect or low-value knowledge accumulation.
4. AIWS should use controlled capture rather than blind auto-update.
5. Wiki/Knowledge Hub should support both retrieval and curated update flow.

## AIWS interpretation
For AIWS, this source supports:
- Knowledge Hub as external memory
- Wiki-first but not Wiki-only runtime
- controlled capture
- source-grounded reusable artifacts
- need for quality/readiness guardrails

## Known uncertainties
- External article may not match AIWS design exactly.
- The article may include assumptions not suitable for enterprise/project use.
- Need to distinguish inspiration from official AIWS design decision.

## Reuse guidance
Use this artifact for:
- explaining why Knowledge Hub matters
- brainstorming filling-back / controlled capture
- supporting design rationale

Do not use this artifact as:
- official AIWS requirement
- implementation spec
- proof that auto-update is safe

## Verification trigger
Open raw/source if:
- quoting the article
- comparing exact claims
- using it as external reference in presentation
- checking whether article has been updated
```

---

## Notes for future SU specs

These samples suggest that the minimal content model probably needs at least:

- Artifact metadata
- Source reference
- Purpose
- Compact understanding
- Key reusable points
- Known uncertainties / limitations
- Reuse guidance
- Verification trigger

This should be validated in SU-04 rather than treated as final schema now.


---

## 4. Example comparison table

| Example | Source unit type | Good for | Must verify raw/source when |
|---|---|---|---|
| Requirement login | Requirement section/file | design/test viewpoint | exact wording/security/final requirement |
| Manufacturing allocation | Basic design section | review/detail design planning | DB/status/transaction exact detail |
| Inventory Q&A | Meeting/Q&A block | follow-up/customer confirmation | final decision/official requirement |
| Feature stability code | Code class/module | onboarding/debug planning | code change/exact signature/config |
| LLM Wiki external | External reference section | design rationale/brainstorming | quoting/currentness/external claim |

---

## 5. How to use these examples in AIWS

### 5.1. For creating a new artifact
Use the examples as pattern references:
- choose the source unit
- fill metadata/source reference
- write compact understanding
- list reusable points
- record limitations
- define verification triggers

### 5.2. For reviewing artifact quality
Check whether the artifact:
- has clear source pointer
- has clear source scope
- does not overclaim
- has limitations
- has verification triggers
- is not replacing raw/source

### 5.3. For training AI/HUMAN
These examples can be used in:
- Knowledge Hub guideline
- Wiki artifact creation guide
- AIWS onboarding
- review checklist
- future tool/skill prompt examples

---

## 6. Anti-example summary

A bad Source Understanding Artifact usually has one of these problems:

1. No source pointer
2. Vague source scope
3. Too broad source scope
4. Mixed unrelated sources
5. No limitations/uncertainties
6. No verification triggers
7. Over-authoritative wording
8. Copy-paste raw source without understanding
9. Treated as Knowledge Hub content without curation
10. Used as Working AIP/execution guardrail

---

## 7. Conclusion

SU-07 provides practical examples for the MVP.

These examples confirm that a useful Source Understanding Artifact should include:
- metadata
- source reference
- purpose
- compact understanding
- key reusable points
- limitations/uncertainties
- reuse guidance
- verification triggers

The examples are sufficient to proceed to SU-08: Canonical Merge Map.
