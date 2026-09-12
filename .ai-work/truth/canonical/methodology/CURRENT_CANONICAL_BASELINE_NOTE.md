# CURRENT_CANONICAL_BASELINE_NOTE_v0_1

## Purpose
Tài liệu này chỉ ra các file methodology/spec đang được coi là baseline canonical chính trong package v0.4.

## Canonical design backbone
- `10_design/Architecture_Design_MVP_v0_5.md`
- `10_design/Basic_Design_MVP_v0_4.md`

## Canonical specs backbone
- `20_specs/AI_Work_System_MVP_Specs_Guidelines_Index_v0_4.md`
- `20_specs/Knowledge_Object_Model_Spec_MVP_v0_1.md`
- `20_specs/Knowledge_Routing_Spec_MVP_v0_1.md`
- `20_specs/Knowledge_Expansion_Link_Spec_MVP_v0_1.md`
- `20_specs/Knowledge_Access_Interface_Spec_MVP_v0_1.md`

## Terminology
- official: Knowledge Hub
- shorthand: Wiki

---

# v0.9.3 baseline note — knowledge-runtime sprint merge

The v0.9.3 baseline is based on v0.9.2 plus the knowledge-runtime sprint merge.

It confirms:
- official term: Knowledge Hub
- official execution artifact: Working AIP
- minimal runtime concept: Task Lens
- runtime-facing structured access layer: Wiki Meta / Index
- runtime direction: Wiki-first, not Wiki-only
- Workspace as active task/session state, not reusable knowledge store
- Skills as reusable capabilities, not orchestrator
- correctness before runtime optimization

Delta tracking is preserved under:
`payload/methodology/90_delta_tracking/knowledge_runtime_sprint_2026-04-25/`

---

# v0.9.4 baseline note — Personal Notebook sprint merge

The v0.9.4 baseline is based on v0.9.3 plus the Personal Notebook Minimal Spec Sprint merge.

It confirms:

- Personal Notebook is a file/folder-based personal working reference area.
- Personal Notebook is configured via local setup path.
- Personal Notebook is separate from Workspace findings and Working AIP.
- Personal Notebook is not Knowledge Hub.
- Personal Notebook is not source of truth by default.
- Personal Notebook does not auto-promote.
- Personal Notebook can create capture candidates through controlled capture.
- Personal Notebook Write Skill Lite is an optional lightweight support skill.

Delta tracking is preserved under:
`payload/methodology/90_delta_tracking/personal_notebook_sprint_2026-04-25/`

---

# v0.9.5 baseline note — Source Understanding Artifact sprint merge

The v0.9.5 baseline is based on v0.9.4 plus the Source Understanding Artifact Minimal Spec Sprint merge.

It confirms:

- Source Understanding Artifact is the practical MVP term.
- Source-derived Reusable Understanding Artifact is the full descriptive name.
- Source Understanding Artifact is source-derived reusable understanding of one clear source unit.
- Raw/source remains source of truth.
- Minimum provenance includes source pointer, source scope, and understanding date.
- Lightweight status/authority/freshness hints are required.
- Wiki Meta / Index may route to Source Understanding Artifacts.
- Source Understanding Artifact may be working/reference, capture candidate, or curated Knowledge Hub artifact.
- Controlled capture/review is required before curated Knowledge Hub status.

Delta tracking is preserved under:
`payload/methodology/90_delta_tracking/source_understanding_artifact_sprint_2026-04-25/`

---

# v0.9.6 baseline note — Task Lens sprint merge

The v0.9.6 baseline is based on v0.9.5 plus the Task Lens Minimal Spec Sprint merge.

It confirms:

- Task Lens is optional runtime viewpoint for task → knowledge routing.
- Intent-first rule is required.
- Explicit Task Lens is not mandatory for every task.
- No-Lens / AI-decides-search-scope is a valid MVP option.
- HUMAN may adjust runtime lens.
- AI may expand/adjust lens when current lens is too narrow.
- Task Lens is not a hard scope limiter.
- Task Lens does not replace AIP Template or Working AIP.
- Task Lens guides Wiki Meta / Index / Knowledge Hub access but does not store knowledge or metadata.
- Raw/source verification remains required when exactness/evidence/freshness matters.

Delta tracking is preserved under:
`payload/methodology/90_delta_tracking/task_lens_sprint_2026-04-25/`

---

# v0.9.7 baseline note — Controlled Knowledge Promotion sprint merge

The v0.9.7 baseline is based on v0.9.6 plus Controlled Knowledge Promotion Minimal Spec.

It adds:
- Controlled Knowledge Promotion
- Knowledge Value
- AI-first Knowledge Hub purpose
- Notebook / Candidate / Wiki boundary
- Knowledge Hub Add/Update Checklist
- `knowledge-hub-add-update` skill concept
- `knowledge-promotion-lookback` command concept
- post-feedback improvement candidate collection
- default AIP lookback step
- aiws-aip run lookback support
- log/rollback trace for important promotion/improvement

Delta tracking is preserved under:
`payload/methodology/90_delta_tracking/controlled_knowledge_promotion_sprint_2026-04-26/`

---

# v0.9.8 baseline note — Wiki Meta / Index Minimal Spec sprint merge

The v0.9.8 baseline is based on v0.9.7 plus Wiki Meta / Index Minimal Spec.

It preserves the v0.9.2 Wiki Source Meta / Index mechanism and adds runtime/compatibility guardrails:
- preserve current field names/tooling
- meta first, artifact when needed
- artifact_locator points to AIWS-readable markdown/source representation
- source_representation_quality_issue when representation is insufficient
- source_id / Knowledge Targets / Lookup Keys rules
- build/update/rebuild/verify flow
- optional enrichment boundary
- relation to Controlled Knowledge Promotion

---

# v0.9.9 baseline note — Working AIP Connection Minimal Spec sprint merge

The v0.9.9 baseline is based on v0.9.8 plus Working AIP Connection Minimal Spec.

It adds:
- Working AIP Connection canonical spec
- runtime guidance
- sample appendix
- mandatory Working AIP rule
- readiness criteria
- anti-confusion boundaries
- aiws-aip run relation
- Controlled Knowledge Promotion / lookback relation

---

# v0.9.10 baseline note — Workspace Boundary Minimal Spec sprint merge

The v0.9.10 baseline is based on v0.9.9 plus Workspace Boundary Minimal Spec.

It adds:
- Workspace Boundary canonical spec
- Workspace runtime guidance
- Workspace sample appendix
- Workspace templates
- Capture Inbox rule
- Workspace Runtime Queue rule
- Workspace close classification
- Workspace boundary with Working AIP / Knowledge Hub / Notebook / source artifacts / canonical docs

---

# v0.9.11 baseline note — Minimal Runtime Testing Stance sprint merge

The v0.9.11 baseline is based on v0.9.10 plus Minimal Runtime Testing Stance.

It adds:
- Minimal Runtime Testing Stance canonical spec
- Runtime Sanity Checklists
- Minimal Runtime Test Cases Appendix
- Runtime Anti-Patterns Appendix
- Sprint merge summary
- addenda to Working AIP, Workspace, Wiki/Knowledge, Controlled Promotion, aiws-aip run/lint guidance

Central stance:

```text
Minimal runtime testing checks whether AIWS follows runtime guardrails and component boundaries.
It uses deterministic checks and manual checkpoints as guardrails.
It does not replace HUMAN review, semantic source verification, future scoring, or telemetry.
```

---

# v0.9.12 baseline note — Runtime Tooling Alignment sprint merge

The v0.9.12 baseline is based on v0.9.11 plus Runtime Tooling Alignment.

It adds:
- Runtime Tooling Alignment canonical spec
- Runtime Tooling Alignment patch guide
- Runtime Tooling Alignment sprint merge summary
- P0/P1 minimal tooling/template patches

Main rename:

```text
02_investigation_queue.jsonl
  ↓
02_runtime_queue.jsonl
```

The old file remains a legacy/backward-compatible alias for old workspaces.

---

# v0.9.13 baseline note — Wiki Tooling Alignment sprint merge

The v0.9.13 baseline is based on v0.9.12 plus Wiki Tooling Alignment.

It adds:
- Wiki Tooling Alignment canonical spec
- Wiki Tooling Alignment patch guide
- Wiki Migration Guide for HUMAN and AI
- Wiki Tooling Alignment sprint merge summary
- P0/P1 minimal Wiki tooling patches

Central boundary:

```text
Wiki tools support AI runtime routing and maintenance,
but they do not replace source verification, approval, or Controlled Knowledge Promotion.
```

---

# v0.9.14 baseline note — Wiki Source Maintenance / Impact Detection sprint merge

The v0.9.14 baseline is based on v0.9.13 plus Wiki Source Maintenance / Impact Detection.

It adds:
- Wiki Source Maintenance / Impact Detection canonical spec
- Wiki Source Maintenance tool patch guide
- Wiki Maintenance Log template
- Wiki Source Maintenance sprint merge summary
- P0/P1 minimal maintenance tool patches

Central boundary:

```text
AIWS can detect source changes, evaluate impact, route maintenance candidates,
create refresh drafts, review/apply safely, and log rollback trace — without auto-promotion.
```

---

# v0.9.15 baseline note — Source Representation / Conversion Integration sprint merge

The v0.9.15 baseline is based on v0.9.14 plus Source Representation / Conversion Integration.

It adds:
- Source Representation / Conversion Integration canonical spec
- Source Representation tool/skill patch guide
- HUMAN check and re-conversion request templates
- Source Representation sprint merge summary
- P0/P1 minimal tool/skill patches

Central boundary:

```text
AIWS uses explicit AI-readable source representations for runtime verification,
and representation limitations are handled visibly instead of hidden.
```

---

# v0.9.16 baseline note — Active Step Context Minimal Spec sprint merge

The v0.9.16 baseline is based on v0.9.15 plus Active Step Context Minimal Spec.

It adds:
- Active Step Context canonical spec
- Step Output / Decision / Discussion Traceability spec
- ASC tool/skill patch guide
- ASC/traceability templates
- P0/P1 minimal tool/skill patches

Central boundary:

```text
ASC gives AI the current-step runtime view,
while Workspace persists outputs/decisions/discussion traces
and Working AIP remains task authority.
```

---

# v0.9.17 baseline note

v0.9.17 is based on v0.9.16 plus deployment hardening.

Main patch:
- `run_aip.py` child command runner now has timeout and stdout/stderr diagnostics.

This patch supports ready-for-deployment packaging and does not expand MVP feature scope.

---

# v0.9.18 baseline note — AIP Convention Canonical Promotion

v0.9.18 is based on v0.9.17 plus AIP convention canonical promotion (CR-AIWS-2026-05-001 applied 2026-05-10).

Trigger: cross-project improvements observation snapshot from `vti-ai-portal` consumer project (2026-05-10) surfaced 3 AIP usage conventions worth promoting from project-level practice to canonical spec. Wiki manager (hoinv-dev) approved 3 sub-proposals via AIP-EXEC-011.

Spec changes (additive only, no breaking changes):
- `AIP_Detail_Spec_MVP.md` §3.5 NEW — Retrospective AIP authoring (ship-first emergencies). Codifies retrospective AIP convention with 4 documentation requirements (a/b/c/d) + special status flow `draft → done` (skip `active`). Adds optional metadata field `authored_retroactively`.
- `AIP_Detail_Spec_MVP.md` §4.3 NEW — Slug prefix taxonomy (recommended). Defines 6 generic prefix patterns (`t<NNN>-`, `bugfix-`, `uiux-`, `<feat>-design`, `<feat>-implementation`, `test-infra-`) for AIP slug categorization. Recommended-not-enforced; lint does not validate prefix membership.
- `AIP_Detail_Spec_MVP.md` §5.3/§5.4/§5.5 PATCH — Each metadata block adds 3 optional fields: `authored_retroactively`, `depends_on`, `related`.
- `AIP_Detail_Spec_MVP.md` §5.7 NEW — Cross-AIP relationship fields explanation. Distinguishes `depends_on` (hard dependency) from `related` (sibling, no dep) and from existing `plan_source` (typed PLAN→EXEC handoff). Format free-form.
- `AIP_Detail_Spec_MVP.md` §12.4 PATCH — Lint reference note: `depends_on`/`related` not structurally validated.
- Spec internal Version: 0.1 → 0.2.

Source basis: 1 consumer project (vti-ai-portal). Reflexive R-meta concern (single-project evidence) was surfaced in CR closing notes; wiki manager approved with awareness. Future consumer project adoptions may corroborate or surface adaptation needs.

Source artifacts:
- `C:\Dev\gitlab\vti-ai-portal\.ai-work\aiws_improvements.md` — playbook source, snapshot 2026-05-10
- `.ai-work/aip/exec/AIP-EXEC-009-aiws-improvements-batch-2026-05.md` — drafted CR
- `.ai-work/aip/exec/AIP-EXEC-011-apply-cr-aiws-2026-05-001.md` — applied CR
- `.ai-work/workspaces/TASK-20260510-aiws-improvements-batch/07_output_draft.md` D4 — full CR text

Out of scope (future sprints if needed):
- Lint enhancement to detect dangling `depends_on`/`related` references (FU-5 from AIP-EXEC-009)
- Backfill existing AIPs with new optional fields
- Renaming existing AIPs to follow §4.3 prefix taxonomy
- SKILL.md body audit beyond description audit (FU-4)

---

# v0.9.19 baseline note — Drift Sync + New Skill Promotion (2026-05-11)

v0.9.19 is based on v0.9.18 plus drift sync from `.ai-work/` (deployed area) back to canonical `product/` (build source), plus promotion of `aiws-util-personal-notebook` skill and 2 general-purpose sensitive-data tooling files.

Trigger: drift audit 2026-05-11 (this AIP) surfaced that 11 tooling files in `.ai-work/tooling/` had accumulated improvements (+1002 net lines) not yet present in canonical `product/tooling/`, plus 1 skill (`aiws-util-personal-notebook`) and 3 tooling files (`personal_notebook_write.py`, `mask_sensitive.py`, `scan_sensitive.py`) existed only in `.ai-work/` or `.claude/` but not in `product/`. Because `build_aiws_install_package.py` ships exclusively from `product/`, these improvements were at risk of NOT reaching consumer projects in the next package build. AIP-EXEC-012 promotes them to canonical.

Sync scope (additive only, no breaking changes):

**Tooling sync** — 11 files updated `.ai-work/tooling/ → product/tooling/`:
- `build_active_step_context.py` (+73 lines: `_load_jsonl_safe`, `_first_existing`, `_bullet_refs` helpers + blocking_queue logic)
- `build_wiki_source_index.py` (+47)
- `build_wiki_source_meta.py` (+82)
- `detect_changed_wiki_sources.py` (+57)
- `evaluate_wiki_source_impact.py` (+60)
- `lint_aip.py` (in-place fix: candidate parsing strips backticks)
- `lint_all.py` (-6 refactor)
- `lint_wiki.py` (+206)
- `lint_workspace.py` (+317)
- `lookup_wiki_source.py` (+57)
- `refresh_wiki_source_meta.py` (+109)

**Skill promotion** — `aiws-util-personal-notebook` to canonical layout (8 new files):
- `product/skills/aiws-util-personal-notebook/SKILL.md` (thin pointer)
- `product/procedural/skills/aiws-util-personal-notebook/` (SKILL.md + config.example.yaml + scripts/notebook_write.py + templates/×3)
- `product/tooling/personal_notebook_write.py` (companion script)

**General-purpose tooling promotion** — 2 sensitive-data tools added to `product/tooling/`:
- `mask_sensitive.py` — markdown sensitive-info masking with placeholder mapping
- `scan_sensitive.py` — read-only sensitive-info scanner with multi-format report

**Intentionally NOT promoted** — kept as project-local helpers in `.ai-work/tooling/`:
- `build_asp_manual_metas.py` — specific to ASP manuals knowledge source in this project
- `build_canonical_package_metas.py` — specific to AIWS canonical package metas in this project

R-meta concern (process): the drift cycle occurred because improvements were authored directly in `.ai-work/` (deployed area) instead of `product/` (canonical). Memory rule `feedback_tooling_edit_flow.md` already documents the expected flow (edit only in `product/`, deploy via install/update). This v0.9.19 sprint is a one-time remediation. Future improvements MUST flow `product/ → install → .ai-work/`. No recurring drift cycle should be tolerated.

Source artifacts:
- `.ai-work/aip/exec/AIP-EXEC-012-aiws-canonical-sync-and-package-v0_9_19.md` — this AIP
- `.ai-work/workspaces/TASK-20260511-exec-012/04_findings.md` — full drift inventory + per-step evidence
- `.ai-work/workspaces/TASK-20260511-exec-012/11_output_final.md` — final report (after STEP-06)

Out of scope (future sprints if needed):
- FU-4 (SKILL.md body audit) — deferred from AIP-EXEC-009/011
- FU-5 (lint dangling refs detection) — deferred from AIP-EXEC-009/011
- Git release tag `v0.9.19` on `mvp_final` branch — user-decided
- Consumer project propagation (FE, CEC, BSN-WithAI, vti-ai-portal) — handled by their `/aiws-pkg upgrade` cycles


# 2026-06-19 baseline note — AIWS Change Request Spec (CR-AIWS-2026-06-030)

Adds `20_specs/AIWS_Change_Request_Spec_MVP.md` as the general AIWS-wide CR authority (`WIKI_CHANGE_REQUEST_SPEC` = wiki-meta profile). Codifies month-scoped + cross-branch CR-id allocation discipline (CAP-001) and the 3 CR-authoring conventions absorbed from AIP-093. Applied via AIP-EXEC-086 (governing CR-AIWS-2026-06-030).


# 2026-08-15 baseline note — Staleness-audit scope + registration policy (CR-AIWS-2026-08-057, DP-1025-G/H)

**DP-G — History-class exclusion RATIFIED.** Docs thuộc history-class (`00_brainstorming/`, `90_delta_tracking/` — 403 docs @2026-08-13) nằm **NGOÀI scope** canonical staleness audit (per OP-1025-05, PO ratify 2026-08-15). Các cây này là quá trình đã đóng băng, không phải canonical hiện hành; audit staleness không quét và không tính chúng vào DOC-STALE. Muốn rà chúng → history-scan pass riêng (mandate riêng), không gộp vào audit canonical.

**DP-H — `aip_templates/tracking/` + generated pages = INTERNAL.** `product/aip_templates/tracking/` (evaluation checklist, open-points templates) và các trang generated (vd `.ai-work/wiki/overview/`) **không thuộc canonical-doc-set và KHÔNG register wiki** (PO ruling 2026-08-15). Lint `canonical_doc_unregistered` hiện chỉ quét `.ai-work/guidelines` + `.ai-work/procedural` — vùng này vốn ngoài scan (zero-touch, verify tại apply CR-057).
