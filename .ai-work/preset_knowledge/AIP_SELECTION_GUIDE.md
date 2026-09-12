---
artifact_type: guide
title: AIP Selection Guide — AI Work System Design Project
status: active
updated_at: 2026-04-22
---

# AIP Selection Guide — AI Work System Design Project

## Purpose
Help BrSE and AI choose the correct AIP type for the current task. Task ngoài danh sách → follow Universal Gates (SOP_MASTER) + hỏi BrSE.

> **Note — Task Lens:** Các `Task Lens` values trong guide này (e.g. `design_methodology_artifact`, `review_canonical_artifact`) là **routing identifiers** — chỉ mang tính tham chiếu phân loại task. Task Lens feature chưa được implement thành definition files; không cần tìm file lens ở đâu cả. Sẽ cập nhật khi feature hoàn thiện.

## Rule 0: Clarify before selecting
Trước khi chọn AIP type, xác định:
- Task là gì (mục tiêu cụ thể)?
- Output kỳ vọng là gì (loại artifact gì)?
- Scope có rõ không (clear enough for EXEC, hay cần plan trước)?
- Có input artifact đã có chưa?

**If uncertain between PLAN and EXEC → choose PLAN.**

## AIP Type Guide

### Type ROOT — RETIRED (CR-AIWS-2026-07-026)
- Project scope/objective/priority changes → update `SOP_MASTER` (Truth, CR-gated). Không còn AIP_ROOT / project-level AIP.

### Type PLAN
Use PLAN when:
- Task scope needs clarification before execution
- Research / investigation phase needed before deciding approach
- Multiple execution paths possible — need to decide which
- Task is large enough to need an explicit handoff to EXEC

**AIWS examples:**
- Planning a new canonical package versioning process
- Investigating what methodology gaps exist before designing a new spec
- Researching how to structure a new wiki guideline package

### Type EXEC
Use EXEC when:
- Scope is clear, deliverable is defined, ready to act
- Well-understood task with predictable output
- Following an existing PLAN handoff

**AIWS examples:**
- Drafting a new spec document (once scope is clear)
- Rebuilding wiki source meta for a canonical package
- Applying a Cross Request to update canonical content
- Creating a new AIP template or task lens

### Type LOCAL
Use LOCAL when:
- Private notes, personal reminders, scratch thoughts
- Optional — not part of shared workflow
- Not tracked as official project artifact

---

## Case-by-case Selection

### Case A: Design a new methodology spec or guideline
**AIP type:** EXEC (if scope/structure is clear) or PLAN → EXEC (if needs research first)
**Task Lens:** `design_methodology_artifact`
**Inputs needed:** SOP_MASTER §2 Scope (verify in scope), parent spec (if extending one), existing canonical artifacts in same package

### Case B: Revise an existing canonical artifact significantly
**AIP type:** EXEC
**Task Lens:** `design_methodology_artifact`
**Inputs needed:** Current artifact, parent spec, prior version if exists

### Case C: Review a canonical artifact before publishing
**AIP type:** EXEC
**Task Lens:** `review_canonical_artifact`
**Inputs needed:** Artifact under review, governing spec, AIP_REVIEW_GUIDELINE_v0_3.md, AIP_REVIEW_CHECKLIST_v0_3.md

### Case D: Build or rebuild wiki source meta + index
**AIP type:** EXEC
**Task Lens:** `build_wiki_meta`
**Inputs needed:** Canonical package to build from, relevant WKP profile, CLAUDE.local.md §1 (versions)

### Case E: Investigate a spec gap or inconsistency
**AIP type:** PLAN (research first) or direct execution if scope is small
**Task Lens:** `investigate_spec_gap`
**Inputs needed:** Artifact(s) in question, precedence rules (CLAUDE.local.md §2), SOP_MASTER

### Case F: Create a new AIP template or preset document
**AIP type:** EXEC
**Task Lens:** `design_methodology_artifact`
**Inputs needed:** Existing template structure, AIP_Detail_Spec_MVP.md (for AIP templates), example file

### Case G: Version bump a canonical package
**AIP type:** EXEC
**Task Lens:** `design_methodology_artifact`
**Inputs needed:** Current package, list of changes, CLAUDE.local.md §1, archive path convention

### Case H: Apply an approved Change Request to canonical wiki
**AIP type:** EXEC
**Task Lens:** (none specific — follow CR instructions)
**Inputs needed:** Approved CR document, wiki index/meta files to update, SOP_MASTER §4.1

## Escalation Rule
If the AI cannot proceed because a prerequisite artifact is missing:
- Do NOT invent content silently
- Identify the missing prerequisite clearly
- Propose: either create prerequisite first, or confirm with BrSE
- Record the open point in `05_open_questions.md` (Gate U3)
