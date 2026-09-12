# aiws-wiki — operation: register

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Routing — Detect Case First

Before doing anything, detect which CASE applies from user context:

```
User says / provides           → CASE
─────────────────────────────────────────────────────────────────
File path (single file)        → CASE 1  (single-file flow below)
"thêm vào wiki"  + file path   → CASE 1
Folder path                    → CASE 2  (batch → /aiws-wiki register-batch)
"toàn bộ" / "all files"        → CASE 2
Multiple file paths            → CASE 2
"tạo PMP" / "save pattern"     → CASE 3  (Mapping Pattern)
After sample-first confirms    → CASE 3  (AI-triggered, not user prompt)
```

**CASE 2 — Batch registration:** Delegate entirely to `/aiws-wiki register-batch`.
Say: "This looks like a batch registration. Invoking /aiws-wiki register-batch for folder: [path]."

**CASE 3 — Build Mapping Pattern:** Delegate entirely to `/aiws-wiki build-pattern`.
Note: CASE 3 is triggered by the build flow (format signature confirmed during STAGE 2/3 of CASE 1),
not by standalone user prompt. AI suggests PMP creation after sample-first confirms a stable format.

**Ambiguous input** (cannot determine CASE): Ask 1 clarifying question:
"Are you adding (a) a single file, or (b) a folder of files?"

---

## CASE 1 — Single File Flow

Single entry point for "add this file to wiki" use case. Handles the full pipeline:
1. Convert binary formats (Excel, PDF, Word) to AIWS-readable markdown
2. Classify artifact type using taxonomy + HUMAN confirmation  
3. Derive all build parameters automatically
4. Build meta + lint + verify

Design principle: user provides a file + a hint; the skill handles the rest.

## 3-Stage Flow

```
User: "add this file to wiki, đây là layout design của F04"
      + file: docs/design/F04-screen-layout.xlsx

STAGE 1 ──────────────────────────────────────────────────────
Pre-process (deterministic)
  1.1 Detect file type
      - .md / .txt → use as-is
      - .xlsx / .xls → invoke /aiws-doc-convert-skill
        output: .ai-work/wiki_sources/_staging/<file>.md
      - .pdf → invoke PDF conversion if available
      - Other binary → warn + ask user to pre-convert
  1.2 Quick scan converted file:
      - Extract path tokens, heading patterns, content markers
      - Build signature fingerprint for classifier

STAGE 2 ──────────────────────────────────────────────────────
Classify + Confirm (HUMAN gate)
  2.1 Run Artifact_Type_Taxonomy classifier:
      - Compute scores for all 14 artifact types
      - Return top-3 candidates with confidence scores
  2.2 Confidence check:
      - IF top-1 confidence ≥ 0.75 AND gap(top-1, top-2) ≥ 0.15:
          → Present top-1 with confidence to user
          → User confirms or corrects
      - ELSE (AMBIGUOUS):
          → Present top-3 with confidence scores + evidence
          → AI hint: "Based on [path pattern / heading / content], I think this is [type]"
          → User selects correct type
  2.3 Derive parameters from confirmed artifact_type:
      - profile (from Artifact_Type_Taxonomy_Spec_MVP default_profile)
      - task_relevant_tags (from default_task_relevant_tags)
      - source_id (from naming convention: SRC-<TYPE_PREFIX>-<hint_id>[-<LAYER>])
      - title (from user hint or filename-derived)
  2.4 Summary params → user confirm:
      "I will build meta with:
        - source_id: SRC-DD-F04-FE
        - artifact_type: detailed_design_fe
        - profile: design_doc
        - title: Screen Layout Design — F04 FE
      Confirm? (yes / modify)"

STAGE 3 ──────────────────────────────────────────────────────
Build + Register
  3.1 Set representation_status:
      - Binary converted → source_representation_status: partial (conversion may be incomplete)
      - Markdown original → source_representation_status: complete
  3.2 Invoke /aiws-wiki build-meta with derived params
  3.3 Rebuild index (build_wiki_source_index.py)
  3.4 Lint (lint_wiki.py --sources-only)
  3.5 Smoke test: lookup by source_id + 1 T1 keyword
  3.6 Move converted file from _staging/ to wiki_sources/converted/ (if applicable)
  3.7 Report:
      - Source registered: SRC-DD-F04-FE
      - Representation: partial (Excel → markdown conversion)
      - Lookup test: PASS

```

## Rules

- **Multi-system (CR-AIWS-2026-06-017):** in a `multi_system: true` project (`.ai-work/project_profile.yml`), PROMPT the HUMAN to name the source's `system:` (or explicitly "common" = leave absent); never guess/auto-set. Must be a declared project system. Single-system → no prompt.
- **Artifact path đăng ký = CANONICAL HOME của doc (CR-AIWS-2026-08-052 C9).** Ở dự án AIWS (source repo): canonical home là `product/**` — KHÔNG đăng ký bản working copy `.ai-work/**` khi doc có home ở product; doc mà canonical home thật là `.ai-work` (Truth SOP/Contract, procedural, generated pages) giữ `.ai-work`. Ở dự án downstream (consuming): bản ship `.ai-work/truth/canonical/**` LÀ canonical home → đăng ký path đó (index.aiws) là đúng. Lệch quy tắc → cần PO/Wiki-Manager ruling ghi lại.
- HUMAN disambiguation gate is MANDATORY when classifier confidence < 0.75
- STAGE 2.4 summary confirmation is MANDATORY (user must confirm params before build)
- Binary conversion: ALWAYS set `source_representation_status: partial` after conversion
- Do NOT build meta with `_unknown` artifact_type — keep asking until type is confirmed
- source_id follows convention: `SRC-<ARTIFACT_TYPE_PREFIX>-<ID>[-<LAYER>]`
- **Object discovery (symmetry with batch A4):** if the file describes a reusable object (function/screen/table/…) → SUGGEST an object candidate (§3bis, rule #7) — suggest/capture is **unconditional** (an existing related artifact is NOT a reason to skip); the "single-artifact host" question only decides whether to author a separate object node vs. fold into one `companion_design` edge, NOT whether to suggest. NEVER auto-build an object meta (DP6/INV-8) — HUMAN hand-authors via /aiws-wiki build-meta object path
- **#19 object_relation_capture (router pointer):** STAGE 3.2 delegate `/aiws-wiki build-meta` đã bao gồm capture object + quan hệ object↔object (domain x:) + representation (#19); router KHÔNG lặp lại — xem `capture_triggers/object_relation_capture.md`
- **Related Sources basis notes (CR-06-002):** delegate resolve `## Related Sources` viết note objective + intent-blind (dependency → who reads/writes whose data + coupling + what a change affects; skippable → "no data coupling") — no "MUST READ" / vague "open when". Convention: build-meta SKILL / `Knowledge_Expansion_Link_Spec_MVP.md` §4.4.
- **Closing check:** trước khi báo done, xác nhận delegate đã emit candidate `object_relation_capture` (hoặc ghi rõ N/A cho artifact này). Delegate skip → KHÔNG coi router là done.
- **Present (CR-06-005):** sau closing check, surface hai bảng Detected Objects / Discovered Relations của delegate cho HUMAN confirm (hoặc ghi rõ N/A). KHÔNG lặp lại closing check / router pointer.

## Artifact Type Prefix Convention (for source_id generation)

| artifact_type | Prefix |
|---|---|
| requirement_definition | REQ |
| basic_design | BD |
| detailed_design_fe | DD-FE |
| detailed_design_api | DD-API |
| detailed_design_be | DD-BE |
| detailed_design_combined | DD |
| test_case | TC |
| unit_test_spec | UT |
| screen_mockup | SCR |
| db_schema | DB |
| api_manual | API |
| methodology_spec | SPEC |
| meeting_note | MTG |
| legacy_design | LGC |
