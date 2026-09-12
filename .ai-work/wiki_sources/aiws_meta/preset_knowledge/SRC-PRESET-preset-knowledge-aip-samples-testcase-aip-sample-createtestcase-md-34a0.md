---
artifact_type: wiki_source_meta
source_id: SRC-PRESET-preset-knowledge-aip-samples-testcase-aip-sample-createtestcase-md-34a0
title: preset_knowledge / aip_samples/testcase/AIP_Sample_CreateTestCase.md
source_type: methodology_spec
artifact_locator: .ai-work/preset_knowledge/aip_samples/testcase/AIP_Sample_CreateTestCase.md
profile_id: methodology_spec
status: active
updated_at: 2026-04-25T01:17:48.991295+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — preset_knowledge / aip_samples/testcase/AIP_Sample_CreateTestCase.md

## Summary
Task **"tạo test case"** không chỉ là "liệt kê các bước test". Nếu làm không đúng, QA waste time test sai chỗ, bugs vẫn bị miss.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- AIP_Sample_CreateTestCase.md Vì sao task này phải có AIP
- AIP_Sample_CreateTestCase.md AIP type đề xuất
- AIP_Sample_CreateTestCase.md Bộ Q&A để clarify task (STEP 00)
- AIP_Sample_CreateTestCase.md Coverage levels
- AIP_Sample_CreateTestCase.md
- test
- AIP
- coverage
- password
- EXEC
- scope
- Test
- aip
- sample
- createtestcase
- sai
- requirements
- email
- AIP_EXEC_CreateTestCase
- cases
- Expected
- Normal
- Preconditions
- PLAN
- task
- scenarios
- boundary
- results
- BrSE
- Feature
- doc
- Coverage
- features
- Abnormal
- Category
- Priority
- Login
- Steps
- Task
- Linked

## Source-Specific Hints
- heading: AIP_Sample_CreateTestCase.md
- heading: 1. Vì sao task này phải có AIP
- heading: 2. AIP type đề xuất
- heading: 3. Bộ Q&A để clarify task (STEP-00)
- heading: 4. Coverage levels
- heading: 5. Ví dụ TC format (generic)
- heading: TC-001: Đăng nhập thành công với email và password hợp lệ
- heading: TC-002: Đăng nhập thất bại với password sai
- heading: TC-003: Validate field Password — boundary max length
- heading: 6. Khi nào KHÔNG cần AIP
- heading: 7. Linked EXEC Preset

## Related Sources
- **SRC-PRESET-preset-knowledge-aip-exec-testcase-aip-exec-createtestcase-md-1eef** — role: output_template — This sample routes the test-case task to the EXEC preset as the file to copy and fill (project / owner / plan_source, coverage level into Workspace Preconditions, paths into References to Read First, then STEP-00→STEP-05). Coupling = the coverage level and scope settled in this sample feed those preset fields; if the preset's fields or step range change, the fill instructions in §7 here go stale. [asserted]
- **SRC-PRESET-preset-knowledge-aip-exec-review-aip-exec-reviewtestcase-md-1103** — role: related — Scope boundary between two presets: this sample covers CREATING test cases; reviewing someone else's test cases is explicitly out of its scope and routed to the ReviewTestCase EXEC preset instead. Routing pointer only — no field or content coupling between the two presets. [asserted]
