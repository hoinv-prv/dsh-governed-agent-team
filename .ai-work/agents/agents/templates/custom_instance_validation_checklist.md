# Custom Instance Validation Checklist

> Run before activating a CUSTOM no-Blueprint instance (Mode C). Validates `agent_design_snapshot.yaml`
> against Detailed Design v0.2 §5A required-fields. All REQUIRED items must pass.

## Required (§5A)
- [ ] `creation_mode` == `custom_no_blueprint`
- [ ] `blueprint_id` == `null`
- [ ] `instance_id` present (convention `<role>__<project>`)
- [ ] `mission` present (non-empty)
- [ ] `responsibilities` present (≥1)
- [ ] `non_responsibilities` present (≥1; includes "no Official-Wiki update" + "no auto-run other agents")
- [ ] `input_contract` present (required/optional)
- [ ] `output_contract` present (required/optional)
- [ ] `policies` present (memory_policy + workspace_policy + review_policy)

## Manifest coverage (CR-AIWS-2026-08-009 — validation = manifest coverage, mọi mode A/B/C)
- [ ] MỌI field ✔ trong wizard MANIFEST có giá trị (hoặc `none` tường minh với `domain content`)
- [ ] `run_policy` đủ 4 key (aip_driven · aip_template · executor · plan_first) — executor ∈ {main_session, claude_subagent}
- [ ] tools whitelist KHÔNG chứa `Agent`
- [ ] Shim `.claude/agents/<instance_id>.md` đã generate (build_agent_shims) và khớp identity
- [ ] capture-routing ack ghi trong `instance_readme.md`
- [ ] HUMAN đã confirm preview TRƯỚC khi ghi (không ghi-trước-confirm)

## Recommended
- [ ] `known_limitations` present (notes the no-Blueprint baseline + "create Blueprint Creation Candidate if reused")
- [ ] `skills` and `tool_bindings` present (tool_bindings may be `[]`)

## Folder skeleton (FR-CMD-06)
- [ ] `desk.yaml` (`creation_mode: custom_no_blueprint`) + `agent_design_snapshot.yaml`
- [ ] `context/` (4 files) · `memory/` (EMPTY skeleton) · `workspace/` (4 dirs) · `training/` (EMPTY skeleton) · `tools/`
- [ ] `instance_readme.md` + `changelog.md`

## Guardrails
- [ ] Command did NOT auto-run the agent (FR-CMD-08)
- [ ] Instance did NOT auto-become a Blueprint (FR-AI-08)
- [ ] memory/ + training/ are EMPTY (no fabricated learning — content is Phase C)

## YAML convention (OQ-B1)
- [ ] No folded scalars (`>-`) in config YAML; plain or literal (`|`) used; machine-read state kept JSON/JSONL
