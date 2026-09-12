---
artifact_type: template_set_manifest
name: aip_template_base
project: AI Work System
class: source_of_truth
methodology_version: ai_work_system_v0_4
authoritative_spec: ../methodology/ai_work_system/20_specs/AIP_Detail_Spec_MVP.md
updated_at: 2026-04-24
---

# AIP Template Base — AI Work System Product

Bộ AIP template base là một phần của **AI Work System (AIWS) product**. Align với **AI Work System MVP** (`AIP_Detail_Spec_MVP`).

## Templates

| File | AIP Type | Required sections (spec §6) | Step fields per step (spec §7.1) |
|---|---|---|---|
| [AIP_PLAN_TEMPLATE.md](AIP_PLAN_TEMPLATE.md) | PLAN | 11 (§6.2) | 9 required |
| [AIP_EXEC_TEMPLATE.md](AIP_EXEC_TEMPLATE.md) | EXEC | 8 (§6.3) | 9 required |
| [AIP_LOCAL_TEMPLATE.md](AIP_LOCAL_TEMPLATE.md) | LOCAL | 4 (§6.4) | N/A |

Conformance can be verified via `lint_aip.py` — see tooling in `.ai-work/tooling/`.

## File placement after creation

Khi tạo AIP mới từ template, đặt file theo convention (spec §4):

| AIP Type | Target path |
|---|---|
| PLAN | `.ai-work/aip/plans/AIP-PLAN-<NNN>-<slug>.md` |
| EXEC | `.ai-work/aip/exec/AIP-EXEC-<NNN>-<slug>.md` |
| LOCAL | `.ai-work/aip/local/AIP-LOCAL-<NNN>-<slug>.md` |

## Review artifacts (companion set)

> **Moved:** Review companion artifacts đã được chuyển sang `preset_knowledge/review_support/` để collocate với review task presets.

Human-facing review tools complementing automated lint — use during peer review / BrSE sign-off:

| File | Purpose | When to use |
|---|---|---|
| preset_knowledge/review_support/AIP_REVIEW_CHECKLIST_v0_3.md (`.ai-work/preset_knowledge/review_support/AIP_REVIEW_CHECKLIST_v0_3.md`) | 2-tier conformance checklist (26 structural + 21 semantic criteria) | Fill one instance per AIP under review; Minimum tier = mandatory gate, Recommended tier = aspirational |
| preset_knowledge/review_support/AIP_REVIEW_GUIDELINE_v0_3.md (`.ai-work/preset_knowledge/review_support/AIP_REVIEW_GUIDELINE_v0_3.md`) | Companion guideline — per-criterion Purpose / Anti-pattern / Spec ref | Reference lookup when a checklist criterion is unclear |

**Coverage model:**
- **Structural tier** (Minimum, 26 criteria) — mostly auto-enforced by `lint_aip.py`. Reviewer skips lint-covered rows unless lint flagged a failure.
- **Semantic tier** (Recommended, 21 criteria) — judgment required, automation cannot cover. This is where manual review adds value beyond lint.

**In target project:** `.ai-work/preset_knowledge/review_support/`

## Tracking templates

| File | Purpose |
|---|---|
| `product/aip_templates/tracking/TEMPLATE_OPEN_POINTS_v1.md` **(repo nguồn — KHÔNG ship, CR-AIWS-2026-08-078 C3)** | Per-task open points tracker — SOP Universal Gate U3 compliance |
| `product/aip_templates/tracking/EVALUATION_CHECKLIST_AIP_Template_v1.0.md` **(repo nguồn — KHÔNG ship)** | Evaluation checklist for AIP template conformance |

## Core principles (spec §2.3)

- AIP là **stable control artifact** — không lưu runtime state. Runtime state → workspace.
- **Update by exception**: Scope change → Re-plan Log entry in AIP, không silent drift.
- AIP directs execution; workspace stores execution state.
- AIP không được contradact AI_WORK_CONTRACT.

## DO NOT edit templates in place

**Methodology changes require version bump side-by-side**, không edit in-place templates hiện tại.

Workflow khi cần thay đổi:
1. Design changes trong `product/methodology/ai_work_system/` — cập nhật spec, design docs.
2. Tạo template mới side-by-side (e.g., `AIP_EXEC_TEMPLATE_v2.md`) — không ghi đè bản cũ.
3. Bump `methodology_version` trong manifest này khi aligned với spec mới.
4. Record migration decision trong workspace liên quan.

## References

- AIP_Detail_Spec_MVP.md (`.ai-work/truth/canonical/methodology/20_specs/AIP_Detail_Spec_MVP.md`) — authoritative spec (§1–§14)
- AI_Work_System_MVP_Specs_Guidelines_Index.md (`.ai-work/truth/canonical/methodology/20_specs/AI_Work_System_MVP_Specs_Guidelines_Index.md`) — full specs index
- SOP_MASTER / AI_WORK_CONTRACT — in target project's `.ai-work/truth/`
