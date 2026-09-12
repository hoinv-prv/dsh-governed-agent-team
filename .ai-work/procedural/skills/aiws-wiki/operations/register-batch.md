# aiws-wiki — operation: register-batch

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose

Batch orchestrator for bulk folder/list ingestion into the wiki. Covers 3 stages:
Layer 1 build (artifact metas) + PMP management.

For single-file registration: use `/aiws-wiki register` (Wave 2, lighter flow).

## 3-Stage Flow (A / B / D)

```
Input: /aiws-wiki register-batch docs/design/c-purchasing/cb-ordering/
       (or --files SRC1.md SRC2.md SRC3.md)

STAGE A ─── Scan + Plan (deterministic + AI assist) ───────────────
  A1. Glob folder → list candidate files
  A2. Filter: skip binaries not yet converted, skip legacy if flagged
  A3. Detect artifact_type per file (Artifact_Type_Taxonomy_Spec_MVP classifier)
      Map to canonical source_type for --source-type arg in Stage B:

      | Artifact category                          | Canonical source_type value |
      |--------------------------------------------|------------------------------|
      | Requirement definition / functional spec   | requirement_definition       |
      | Basic design / screen design               | basic_design                 |
      | Detail design / API spec                   | detail_design                |
      | Customer requirements / business req.      | customer_requirement         |
      | Process guideline / workflow doc            | process_guideline            |
      | Process / workflow template                | process_template             |
      | SOP / standard operating procedure         | sop                          |
      | Canonical reference doc / glossary         | canonical_doc                |
      | Test spec / test case                      | test_spec                    |

      If ambiguous or new: use closest canonical value + note in plan file.
      Migration: existing metas with non-standard values → flag for refresh next pass.
  A3b. Build Routing check (Stage 2 — DATA-DRIVEN registry; see SOURCE_BUILD_ROUTING_SPEC):
      Some source_types use a dedicated builder instead of the per-file engine. Before the per-file loop,
      QUERY the registry: `py .ai-work/tooling/route_build_tool.py get <source_type>`.
      - Route found → `route_build_tool.py render <source_type> --root .. --prefix .. --subdir ..` → preview
        (`--dry-run`) → run it (the builder emits the FULL meta) → go to B3 (index) + B4 (lint) and SKIP the
        per-file B2 loop for those files.
      - No route (default_route = generic) → generic per-file `/aiws-wiki build-meta` (unchanged). Default = generic; dedicated = opt-in.
      - **W2 — author-on-the-fly + register (ONLY under an explicit HUMAN directive "build a tool for X and register it"):**
        no route + such a directive → AI authors a builder per the build-tool contract (reference
        `build_java_wiki_metas.py`; stdlib, `--dry-run`, emits a FULL valid meta — frontmatter + Summary /
        Knowledge Targets / Lookup Keys), runs it, **format-checks** the output with `lint_wiki` (if a section/
        schema is wrong → fix the tool, re-run), then registers it:
        `route_build_tool.py set <source_type> --tool <path> --args "<argv template>" --profile-id <id>`.
        The upfront directive IS the authorization — **no second confirm**. AI NEVER authors+registers on its
        own initiative (Rule 8).
      - **Refresh = rerun the tool** (`refresh_mode: rerun_tool`); do NOT regenerate a whole directory on a one-file change.
      - **Index always standard** (`build_wiki_source_index.py`); a custom builder NEVER writes `index.jsonl` (SOURCE_BUILD_ROUTING_SPEC §3).
  A4. Group by inferred object identity (function/screen/table ID from path/filename) —
      grouping = batching discovery scratch, NOT a persistent field:
      - extract function/object ID from path/filename (project naming convention)
      - files sharing same ID → same group (e.g. func_cb01001)
      - ungrouped files → standalone
  A5. Detect new format / unknown profile:
      - new format → trigger Sample-First gate (CR-S1)
  A6. Emit plan file:
      .ai-work/wiki_sources/_register_plan_<batch-id>.json
      {
        "batch_id": "INGEST-<YYYYMMDD>-NNN",
        "files_total": N,
        "groups": {"func_cb01001": ["CB01001-*.md", ...]},
        "profile_per_file": {"pattern": "profile_id"},
        "artifact_type_per_file": {"filename": "artifact_type"},
        "new_format_detected": false,
        "sample_first_required": false,
        "pmp_hit": "PMP-<id>" | null
      }
  ── HUMAN review plan (GATE 1 — MANDATORY) ──
  User checks: grouping correct? profiles correct? proceed?

STAGE B ─── Layer 1 Build (parallel-friendly) ────────────────────
  B1. If sample_first_required: build 2-3 samples → review (GATE 2) → fix → confirm
  B2. For each GENERIC-route file in plan (source_types with NO dedicated bulk builder per A3b):
      /aiws-wiki build-meta ...
      (Files whose source_type matched a bulk builder in A3b were already built there — skip them here.)
      After each meta: confirm 3 required sections present (Summary, Knowledge Targets,
      Lookup Keys). Do NOT batch-generate all metas before checking.
  ⚠ [Windows] Write tool only — always use Write tool (not Edit) when creating or
      modifying meta files. Edit tool adds UTF-8 BOM → breaks frontmatter parsing silently.
      See aiws-wiki build-meta SKILL Rules for details.
  B2b. Resolve Related Sources scaffold (tool emits it — CR-017):
       The builder emits a ## Related Sources scaffold (role TODO lines from the profile's
       related_sources.expected_roles + a TODO marker). For each built meta: fill real SRC-ids into
       <SRC-id: TODO> slots where relationships are clear, delete unused role lines, or delete the
       section if none. Declare each relationship ONCE in its canonical direction (query the reverse via wiki_relations; §6A) — NOT both ends. Do not invent links —
       delete rather than guess. Section is NOT projected into index.jsonl.
       Basis note objective + intent-blind (CR-06-002): dependency → who reads/writes whose data + coupling + impact;
       skippable → "no data coupling". Convention: build-meta SKILL / Knowledge_Expansion_Link_Spec_MVP.md §4.4.
  B3. Rebuild index: python .ai-work/tooling/build_wiki_source_index.py
  B4. Lint: python .ai-work/tooling/lint_wiki.py --sources-only
  B5. Spot-check lookup: random 3 keys per group
  B6. Q2 (CR-AIWS-2026-07-001) build-time self-test gate — targeted over the new/changed metas only:
        python .ai-work/tooling/smoke_test_wiki_lookup.py --self-test --only <new/changed source_ids>
      FAIL → WARN + suggest a more discriminative lookup_key (front-load an H1/id compound key — the
      builder now emits one for auto builds, Q1); do NOT block the batch. Makes key quality visible at build.
  B7. H1 (CR-AIWS-2026-07-002) completion pass: if a builder emitted PARTIAL metas (frontmatter
      `needs_completion: [...]`, from `--emit-partial`), run the LLM completion — improve Summary /
      Lookup Keys / Related Sources basis-notes for each, then CLEAR `needs_completion`. `lint_wiki`
      ERRORs (`meta_needs_completion`) on any meta still flagged → a partial is never treated as finished.
  B8. H5 (CR-AIWS-2026-07-002) diagram handling: a meta whose `conversion_limitations` records
      `diagrams_present:N` is auto-marked `source_representation_status: partial` (never silent-drop). Per
      source choose: (a) AI re-represents the diagram(s) as **mermaid** + prose (mark `needs_review`) and
      rebuild with `--diagrams-rerepresented`; (b) HUMAN supplies a description; (c) accept `partial`.

STAGE D ─── Wrap-up ───────────────────────────────────────────────
  D1. Update Wiki Source Index: python .ai-work/tooling/build_wiki_source_index.py
  D1b. Rebuild Relations projection (CR-022): python .ai-work/tooling/build_relations.py
       (relations.jsonl = projection of metas' ## Related Sources; never hand-edit; resolves targets + flags [BROKEN REF])
  D2. Emit batch report:
      - files processed, groups built, unresolved warnings, suggested next batch
  D2b. #19 object_relation_capture wrap-up: gom toàn bộ candidate `object_relation_capture`
       các per-file /aiws-wiki build-meta (B2) đã append (object + quan hệ object↔object/representation)
       → PRESENT một cặp bảng HỢP NHẤT (de-dup) cho cả batch — Detected Objects + Discovered Relations gom across folder — CHO HUMAN review/confirm một lượt (đề xuất author object-node meta + edges, khai một lần).
       Suggest-only (rule #7/DP6/INV-8); KHÔNG auto-build object meta. Chi tiết: capture_triggers/object_relation_capture.md
       Lưu ý: wrap-up chỉ GOM — mỗi per-file build (B2) PHẢI tự fire object_relation_capture TRƯỚC; wrap-up KHÔNG thay thế capture per-file.
  D3. If new_format_detected: true AND format confirmed stable → BLOCKING GATE 4:
      Present prompt to operator — do NOT allow batch wrap-up without a logged decision:
        "Stable new format detected: [format-name]. Create PMP now?
         (yes → /aiws-wiki build-pattern | skip → note reason | defer → set reminder)"
      Record decision in plan file:
        pmp_gate_decision: yes | skip | defer
        pmp_gate_reason: "<operator note — required for skip/defer>"
  D3b. H4 (CR-AIWS-2026-07-002) route-suggestion — SAME GATE 4, SECOND question. If the stable new
       format's source_type has NO dedicated route (`route_build_tool.py get <source_type>` → returns
       the `generic` default) AND ≥3 files share that format, ALSO ask the operator:
         "Create a route/builder for source_type '[type]' so future batches build it deterministically?
          (yes → W2 flow: author a builder per SOURCE_BUILD_ROUTING_SPEC §5, format-check with lint_wiki,
           then route_build_tool.py set — no second confirm | skip → note reason | defer)"
       AI NEVER authors+registers a route on its own initiative (Rule 8) — a HUMAN 'yes' is required.
       Record: route_gate_decision: yes | skip | defer  ·  route_gate_reason: "<note for skip/defer>"
      One decision required per detected new format. Batch is NOT complete until all
      pmp_gate_decisions are recorded.
```

## 3 HUMAN Gates

| Gate          | Stage | Reason                                              |
| ------------- | ----- | --------------------------------------------------- |
| Plan review   | A6    | Grouping/profile assignment may be wrong            |
| Sample review | B1    | Quality gate before mass build (only if new format) |
| PMP creation  | D3    | Pattern reuse commitment needs confirmation         |

## State file

`.ai-work/wiki_sources/_register_plan_<batch-id>.json` — created at STAGE A, referenced throughout.

## Incremental mode

```bash
/aiws-wiki register-batch <path> --incremental
```

Diff against previous batch plan:

- Added files → run full STAGE A-D pipeline
- Modified files → STAGE B refresh (CR-S6 Promotion gate applies)
- Removed files → mark `source_representation_status: superseded` in meta

## When to use vs /aiws-wiki register

| Scenario                    | Skill                                         |
| --------------------------- | --------------------------------------------- |
| 1 file, ad-hoc              | `/aiws-wiki register` (Wave 2) — preferred |
| Multiple files, same format | `/aiws-wiki register-batch` batch           |
| Full folder ingestion       | `/aiws-wiki register-batch` batch           |
| Update 1 existing meta      | `/aiws-wiki refresh-meta`                   |

**Single-file fast-path** (when `/aiws-wiki register` is unavailable and `files_total == 1`
after Stage A scan):

- Present GATE 1 inline — no separate plan JSON file required
- An object discovered during batch → SUGGEST a candidate (§3bis, rule #7) — suggest is **unconditional**; the single-artifact-host question only governs node-vs-`companion_design` authoring, NOT whether to suggest. NEVER auto-build an object meta (DP6/INV-8) — HUMAN hand-authors via /aiws-wiki build-meta object path
- Skip GATE 4 (PMP suggestion) if `new_format_detected: false`
- Sample-first (GATE 2) still applies if new format is detected
- Still record a minimal plan summary in conversation for traceability

## Rules

- GATE 1 (Plan review) is ALWAYS mandatory — even if plan looks correct
- **Artifact path đăng ký = CANONICAL HOME của doc (CR-AIWS-2026-08-052 C9).** Ở dự án AIWS (source
  repo): canonical home là `product/**` — KHÔNG đăng ký bản working copy `.ai-work/**` khi doc có home
  ở product; doc mà canonical home thật là `.ai-work` (Truth SOP/Contract, procedural, generated pages)
  giữ `.ai-work`. Ở dự án downstream (consuming): bản ship `.ai-work/truth/canonical/**` LÀ canonical
  home → đăng ký path đó (index.aiws) là đúng. Registration wave nào lệch quy tắc này phải có
  PO/Wiki-Manager ruling ghi trong plan file.
