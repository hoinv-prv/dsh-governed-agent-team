---
artifact_type: guide
title: Task to AIP Mapping — AI Work System Design Project
status: active
updated_at: 2026-04-24
---

# Task to AIP Mapping — AI Work System Design Project

## Quick reference table

| Task Type | AIP Type | Task Lens | Main Output |
|---|---|---|---|
| Design new methodology spec or guideline | EXEC (or PLAN if scope unclear) | `design_methodology_artifact` | New canonical artifact in `canonical/methodology/` |
| Revise existing canonical artifact significantly | EXEC | `design_methodology_artifact` | Updated canonical artifact |
| Review canonical artifact before publishing | EXEC | `review_canonical_artifact` | Review findings in workspace; reviewed artifact |
| Build / rebuild wiki source meta + index | EXEC | `build_wiki_meta` | Updated `wiki_sources/meta/` + `index.jsonl` |
| Investigate spec gap or inconsistency | PLAN → EXEC | `investigate_spec_gap` | Gap analysis in workspace; resolution proposal |
| Create new AIP template or preset | EXEC | `design_methodology_artifact` | New template file in `.ai-work/aip/templates/` |
| Version bump canonical package | EXEC | `design_methodology_artifact` | New versioned folder; updated CLAUDE.local.md; archive |
| Apply approved Change Request to canonical wiki | EXEC | (follow CR instructions) | Updated wiki meta/index; CR status → `applied` |
| Update SOP / Contract (major change) | EXEC | `design_methodology_artifact` | Updated Truth file |
| Create / update task lens | EXEC | `design_methodology_artifact` | TBD — task lens feature not yet implemented; placement pending |
| Ad hoc Q&A / small research | Direct (no AIP needed) | `investigate_spec_gap` or none | Notes in workspace or direct chat answer |

## BrSE Preset Tasks (from preset_knowledge/)

> Use templates in `preset_knowledge/` — see [PRESET_INDEX.md](PRESET_INDEX.md) for full list.

### Mandatory AIP Policy

> **Các task sau BẮT BUỘC phải có AIP trước khi thực hiện với AI involvement:**
> - Tạo tài liệu design (BD / DD / Screen Design)
> - Tạo tài liệu test case
> - Review tài liệu thiết kế
> - Review test case
>
> Không được để AI thực hiện các task này mà không có AIP. Mục đích: đảm bảo scope confirmation, open points tracking, và BrSE checkpoint trước khi output đến downstream.

| Task | AIP Type | Mandatory | Preset Template | Main Output |
|---|---|---|---|---|
| **Tạo tài liệu design** (BD / DD / Screen Design) | PLAN → EXEC | **YES** | `aip_samples/design/` + `aip_exec/design/` | Design Document (Markdown) |
| **Tạo tài liệu test case** | PLAN → EXEC | **YES** | `aip_samples/testcase/` + `aip_exec/testcase/` | Test Case Document (Markdown) |
| **Review tài liệu thiết kế** (BD/DD/Screen) | PLAN → EXEC | **YES** | `aip_samples/review/` + `aip_exec/review/` | Review Comment + Checklist |
| **Review test case** | PLAN → EXEC | **YES** | `aip_samples/review/` + `aip_exec/review/` | Review findings + coverage notes |
| Soạn chat confirm yêu cầu với KH | PLAN → EXEC | recommended | `aip_samples/communication/` + `aip_exec/communication/` | Chat message (Japanese / Vietnamese) |
| Soạn mail confirm yêu cầu với KH | PLAN → EXEC | recommended | `aip_samples/communication/` + `aip_exec/communication/` | Email (formal confirm) |
| Truyền đạt yêu cầu cho offshore | PLAN → EXEC | recommended | `aip_samples/requirement/` + `aip_exec/requirement/` | Backlog Item + Req Summary + Confirmation Record |
| Clarify requirements từ meeting transcript | EXEC (standalone) | recommended | `aip_exec/requirement/AIP_EXEC_ClarifyReq_MeetingToRD.md` | RD / clarification document |

## Dependency Reminders

### Design new spec
Usually depends on:
- SOP_MASTER.md §2 Scope (verify in scope)
- Parent spec or governing document
- AIP_Detail_Spec_MVP.md (for structure compliance)

### Revise existing artifact
Usually depends on:
- Current artifact (current version)
- Parent/governing spec
- Reason for change (approved deviation, gap finding, or explicit instruction)

### Review canonical artifact
Usually depends on:
- Artifact under review
- Governing spec (conformance check)
- `.ai-work/preset_knowledge/review_support/AIP_REVIEW_GUIDELINE_v0_3.md`
- `.ai-work/preset_knowledge/review_support/AIP_REVIEW_CHECKLIST_v0_3.md`

### Build wiki meta
Usually depends on:
- CLAUDE.local.md §1 (current versions)
- Relevant WKP profile (WKP-AIWS-METHODOLOGY-001.yml or WKP-AIWS-WIKI-GUIDELINES-001.yml)
- Canonical package folder (source of meta generation)

### Investigate spec gap
Usually depends on:
- Artifact(s) in question
- Precedence rules (CLAUDE.local.md §2, SOP_MASTER §General Principles)
- Canonical structure map (WKP-AIWS-CANONICAL-STRUCTURE-001.yml)

### Version bump
Usually depends on:
- All artifacts in current package version
- Change log / rationale for the bump
- New folder naming convention (ai_work_system_vX_Y/ or aiws_wiki_vX_Y_Z/)
- CLAUDE.local.md §1 (to update version reference)

### Apply CR
Usually depends on:
- Approved CR document (status = `approved_for_ai_update`)
- Wiki Manager request (explicit, not inferred)
- Target wiki meta/index files
