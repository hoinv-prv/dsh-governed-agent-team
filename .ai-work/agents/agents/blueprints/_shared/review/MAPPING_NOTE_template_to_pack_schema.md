# Mapping Note — Agent Templates to Pack Schema

> Scope: applies to ALL blueprints built in AIP-EXEC-139 (the two Document Review blueprints
> AND the PM blueprint, where relevant). This note records how the READ-ONLY provenance
> templates under `docs/agent_pack_impl_package/agent_templates/` are mapped into the on-disk
> pack schema defined by Detailed Design v0.2 (`docs/agent_pack_impl_package/docs/04_Detailed_Design.md`).
> Provenance templates are template_version v0.1 and are NEVER edited — they are read and mapped.

---

## 1. Why this note exists

The agent-template packages (Document Review, PM) use their own key names and document layout.
The pack schema (Detailed Design v0.2 §3 Blueprint, §4 Instance, §5 blueprint_ref) uses a
different, canonical set of key names and an on-disk folder shape (§1) already realized by the
precedent blueprint `aiws_wiki_meta_strategy_coordinator/`.

To keep all blueprints consistent we MAP (rename / fold / add), we do NOT fork. The three
mapping operations below are the contract every downstream blueprint step must follow.

---

## 2. The three mapping operations

### 2.1. RENAME (template key -> pack-schema key)

The template `AGENT_BLUEPRINT_SCHEMA.yaml` keys are renamed to the Detailed Design v0.2 §3 keys.

| Template key (provenance)        | Pack-schema key (Detailed Design v0.2 §3) | Note |
|---|---|---|
| `blueprint_name`                 | `name`                                    | value unchanged |
| `agent_type`                     | `type`                                    | value unchanged (e.g. `review`, `pm`) |
| `version`                        | `blueprint_version`                       | quoted string, e.g. `"0.1"` |
| `inputs`                         | `input_contract`                          | keep `required` / `recommended` / `optional` tiers |
| `outputs`                        | `output_contract`                         | keep `required` / `optional` tiers |

Values such as `blueprint_id`, `status`, `mission`, `responsibilities`, `non_responsibilities`
already match the pack-schema key names and carry over unchanged.

### 2.2. FOLD (template detail -> pack-schema shape)

Some template content is collapsed into the pack-schema structure rather than renamed 1:1:

- `target_document` (template block: type / examples / expected_format) folds into the blueprint
  as an ADDITIVE block (see 2.3) AND informs the blueprint `mission` prose.
- `checklists.common` + `checklists.document_specific` (template) fold to relative paths under the
  blueprint folder. The COMMON checklist is NOT copied per-blueprint — it is referenced from the
  shared location (see §4); only the document-specific checklist lives under each blueprint.
- `process_docs.*` (template: review_process / severity_definition / finding_format /
  source_trace_rule / lesson_capture_rule) fold to relative paths pointing at the SHARED process
  files (see §4) — they are document-type-agnostic and reused by both review blueprints.
- Template doc bodies (`REVIEW_PROCESS_TEMPLATE.md`, `REVIEW_OUTPUT_TEMPLATE.md`,
  `MEMORY_AND_LEARNING_RULES_TEMPLATE.md`, `REVIEW_CHECKLIST_TEMPLATE.md`) are mapped into the
  concrete shared process / checklist / output_template files — placeholder `<...>` slots are
  resolved to plain text; example blocks are kept where they aid the agent.

### 2.3. ADD (creation-mode + template-unique blocks, ADDITIVE)

Two additions are required on every blueprint built here:

- `creation_mode: blueprint_based` — required by Detailed Design v0.2 §3 (the precedent
  `aiws_wiki_meta_strategy_coordinator/blueprint.yaml` carries it; the templates do not).
- `blueprint_id` — kept from the template; if absent, derive a stable id.

Template-unique fields that have NO pack-schema home are carried as ADDITIVE blocks (NOT dropped,
NOT silently merged). For the review blueprints these are:

- `target_document:` (type / examples / expected_format)
- `review_principles:` (wiki_grounded_not_wiki_only, evidence_required_for_important_findings,
  separate_issue_question_suggestion, report_conflict_not_silent_resolve, avoid_generic_findings)
- `learning_candidate_types:` (the 8 review candidate types)
- `human_gate_policy.required_for:` review-specific gates (final_review_acceptance,
  memory_confirmation, checklist_update, wiki_candidate_promotion, blueprint_improvement,
  conflict_resolution)

Additive blocks are placed AFTER the pack-schema core keys in `blueprint.yaml`, so a reader sees
the canonical contract first and the review-specific extension second.

---

## 3. Conventions every blueprint step must hold

- `creation_mode: blueprint_based` is always present, plus `blueprint_id`.
- The pack-schema core key ORDER mirrors the precedent: `creation_mode`, `blueprint_id`,
  `blueprint_version`, `name`, `type`, `status`, `mission`, `responsibilities`,
  `non_responsibilities`, `input_contract`, `output_contract`, `skills`, `default_tools`,
  `memory_policy`, `workspace_policy`, `human_gate_policy`. Additive blocks follow.
- YAML uses plain or literal scalars only — NO folded `>-`. Multi-line prose uses literal `|`.
- All cross-references between files are RELATIVE paths (never absolute, never `.ai-work/` rooted)
  so the canonical tree under `product/agents/` and the installed tree under `.ai-work/agents/`
  resolve identically.
- Wiki-first NOT Wiki-only: every process/checklist/output asset states that the agent reads Wiki
  first for grounding but must verify against source/reference docs and report conflicts rather
  than treat Wiki as the only authority.
- No auto-promotion: instance memory files are created EMPTY; learning candidates are emitted with
  `status: candidate` and never auto-confirmed. Promotion to confirmed memory / Official Wiki /
  checklist / blueprint is HUMAN-gated.
- PM agent caveat: the PM blueprint reuses the RENAME and ADD rules (creation_mode, name/type/
  blueprint_version) but does NOT use the shared review process/checklist/output assets — those
  are review-specific. PM = planning/advisory only.

---

## 4. Shared-asset location convention

Assets reused by BOTH review blueprints live under this shared folder, NOT duplicated per
blueprint:

```
<pack root>/agents/blueprints/_shared/review/
  MAPPING_NOTE_template_to_pack_schema.md   (this file)
  process/
    document_review_process.md
    severity_definition.md
    finding_format.md
    source_trace_rule.md
    (lesson_capture_rule.md nằm ở ../common/ — relocate bởi CR-AIWS-2026-07-017; xem snippet YAML dưới)
  checklists/
    common_document_review_checklist.md
  output_templates/
    review_report.md
    findings_table.md
    open_questions.md
    references_used.md
    review_limitations.md
```

How a review blueprint references these (relative paths from the blueprint folder
`<pack root>/agents/blueprints/<doc_type>_review_agent/`):

```yaml
process_docs:
  review_process:      ../_shared/review/process/document_review_process.md
  severity_definition: ../_shared/review/process/severity_definition.md
  finding_format:      ../_shared/review/process/finding_format.md
  source_trace_rule:   ../_shared/review/process/source_trace_rule.md
  lesson_capture_rule: ../_shared/common/lesson_capture_rule.md

checklists:
  common:            ../_shared/review/checklists/common_document_review_checklist.md
  document_specific: checklists/<doc_type>_review_checklist.md   # blueprint-local

output_templates:
  shared_dir: ../_shared/review/output_templates/
```

Rule of thumb:
- DOCUMENT-TYPE-AGNOSTIC content (the review process, severity tiers, finding format, source-trace
  rule, lesson-capture rule, the common checklist, the report shape) -> SHARED here.
- DOCUMENT-TYPE-SPECIFIC content (the per-type checklist, type-specific skills, mission wording,
  severity examples for the type) -> lives under the individual blueprint folder.

This avoids drift: a change to the common review behavior is made once in `_shared/review/` and is
picked up by every review blueprint that references it.

---

## 5. Provenance

- Source templates (READ-ONLY, template_version v0.1):
  - `docs/agent_pack_impl_package/agent_templates/Document_Review_Agent_Blueprint/`
  - `docs/agent_pack_impl_package/agent_templates/PM_Agent_Blueprint/`
- Target schema: `docs/agent_pack_impl_package/docs/04_Detailed_Design.md` (§1 folder, §2
  registry, §3 blueprint, §4 instance, §5 blueprint_ref, §7 context, §8 run/workspace, §14
  learning, §15 memory, §16 tool-binding).
- On-disk precedent mirrored (HISTORICAL — cây dev đã xóa, CR-AIWS-2026-08-039; live pack root nay là `product/agents/` canonical · `.ai-work/agents/` installed): `development/ai_agents/agents/blueprints/aiws_wiki_meta_strategy_coordinator/`.
- Authored by: AIP-EXEC-139 / STEP-01.
