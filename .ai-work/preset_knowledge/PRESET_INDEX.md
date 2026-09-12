---
artifact_type: index
title: Preset Knowledge Index — AIP Templates & Skills
status: active
source_project: VJP-AI-COMMITTEE / vti-sop-aip
imported_at: 2026-04-24
---

# Preset Knowledge Index

Reusable AIP templates and skill definitions for common BrSE tasks. Each task has a paired **Sample (PLAN)** and **EXEC** template.

> **Profile note:** Templates trong index này được thiết kế cho **BrSE dự án Nhật** (VJP profile — offshore handoff, Japanese customer communication, VTI ISMS compliance). Hầu hết templates (Design, TestCase, Review, Requirement) là generic và dùng được cho mọi project. Riêng mục **Skills** (`AIP_MailConfirm.md`) là Japan-specific — project không làm việc với KH Nhật có thể bỏ qua.

## How to use

1. **Starting a new task** → pick Sample (PLAN) to define flow + rules
2. **Executing a confirmed task** → pick EXEC template, fill in context, hand off to AI
3. **Skill** → standalone skill definition (trigger-based, no PLAN phase needed)

---

## Design & Testcase — Document Creation (Mandatory)

> Tasks dưới đây **BẮT BUỘC** có AIP trước khi thực hiện với AI involvement.

### Tạo Tài Liệu Design
- Sample (PLAN): [aip_samples/design/AIP_Sample_CreateDesignDoc.md](aip_samples/design/AIP_Sample_CreateDesignDoc.md)
- EXEC: [aip_exec/design/AIP_EXEC_CreateDesignDoc.md](aip_exec/design/AIP_EXEC_CreateDesignDoc.md)
- Purpose: Tạo BD / DD / Screen Design document từ requirements đã confirm — có AI involvement

### Tạo Tài Liệu Test Case
- Sample (PLAN): [aip_samples/testcase/AIP_Sample_CreateTestCase.md](aip_samples/testcase/AIP_Sample_CreateTestCase.md)
- EXEC: [aip_exec/testcase/AIP_EXEC_CreateTestCase.md](aip_exec/testcase/AIP_EXEC_CreateTestCase.md)
- Purpose: Tạo test case document (Markdown) từ design doc / requirements — có AI involvement

---

## Communication — Chat / Mail Confirm

### Chat Confirm Requirement
- Sample (PLAN): [aip_samples/communication/AIP_Sample_CreateChatConfirmRequirement.md](aip_samples/communication/AIP_Sample_CreateChatConfirmRequirement.md)
- EXEC: [aip_exec/communication/AIP_EXEC_CreateChatConfirmRequirement.md](aip_exec/communication/AIP_EXEC_CreateChatConfirmRequirement.md)
- Purpose: Soạn chat confirm yêu cầu với KH — ngắn gọn, unblock dev nhanh

### Mail Confirm Requirement
- Sample (PLAN): [aip_samples/communication/AIP_Sample_CreateMailConfirmRequirement.md](aip_samples/communication/AIP_Sample_CreateMailConfirmRequirement.md)
- EXEC: [aip_exec/communication/AIP_EXEC_CreateMailConfirmRequirement.md](aip_exec/communication/AIP_EXEC_CreateMailConfirmRequirement.md)
- Purpose: Soạn mail confirm yêu cầu với KH — formal / contractual context

---

## Review — Design & Test Case (Mandatory)

> Tasks dưới đây **BẮT BUỘC** có AIP trước khi thực hiện với AI involvement.

### Review Design Document
- Sample (PLAN): [aip_samples/review/AIP_Sample_ReviewDesign_Shared.md](aip_samples/review/AIP_Sample_ReviewDesign_Shared.md)
- EXEC: [aip_exec/review/AIP_EXEC_ReviewDesign.md](aip_exec/review/AIP_EXEC_ReviewDesign.md)
- Purpose: Review BD / DD / Screen Design — output Review Comment + Checklist

### Review Test Case
- Sample (PLAN): [aip_samples/review/AIP_Sample_ReviewTestCase_Shared.md](aip_samples/review/AIP_Sample_ReviewTestCase_Shared.md)
- EXEC: [aip_exec/review/AIP_EXEC_ReviewTestCase.md](aip_exec/review/AIP_EXEC_ReviewTestCase.md)
- Purpose: Review test case — output findings + coverage quality check

---

## Requirement — Offshore Handoff & Clarification

### Requirement Handoff Offshore
- Sample (PLAN): [aip_samples/requirement/AIP_Sample_RequirementHandoff_Offshore.md](aip_samples/requirement/AIP_Sample_RequirementHandoff_Offshore.md)
- EXEC: [aip_exec/requirement/AIP_EXEC_RequirementHandoff_Offshore.md](aip_exec/requirement/AIP_EXEC_RequirementHandoff_Offshore.md)
- Purpose: Tạo Backlog Item + Req Summary + Confirmation Record cho offshore handoff

### Clarify Requirements — Meeting to RD
- Sample (PLAN): *(none — EXEC standalone, fixed flow)*
- EXEC: [aip_exec/requirement/AIP_EXEC_ClarifyReq_MeetingToRD.md](aip_exec/requirement/AIP_EXEC_ClarifyReq_MeetingToRD.md)
- Purpose: Từ meeting transcript → RD / clarification document

---

## Skills

| Skill | File | Trigger context |
|---|---|---|
| aiws-util-mail-confirm | [skills/AIP_MailConfirm.md](skills/AIP_MailConfirm.md) | Viết confirm tiếng Nhật cho KH Nhật — mail / chat |
