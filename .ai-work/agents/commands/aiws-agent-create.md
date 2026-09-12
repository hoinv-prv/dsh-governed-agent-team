---
description: Tạo Agent Task Desk mới từ Blueprint có sẵn, Blueprint do AI gợi ý, hoặc định nghĩa custom do HUMAN đưa ra — dựng identity, context refs, tool binding, policy + setup summary để HUMAN duyệt.
argument-hint: [<blueprint-id>] [--name "<display name>"]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, TodoWrite
---

# Command Spec — `/aiws-agent-create`

> **Status:** prompt/spec (file-first). NOT an executable CLI — a real `aiws agent create` CLI is Post-MVP.
> **Built by:** AIP-EXEC-108 (Phase B of program AIP-PLAN-002).
> **Source:** Requirements v0.4 §4 (FR-CMD-01..08) + §3 (FR-AI-06/07/08); Detailed Design v0.2 §6.
> **Scope:** creates a named Agent Task Desk under `agents/task_desks/<instance_id>/`. It does **not** run the agent.

## Purpose
Create a named, trackable **Agent Task Desk** from (A) an existing Blueprint, (B) an AI-recommended
Blueprint, or (C) a HUMAN-defined custom definition when no suitable Blueprint exists. The command
initializes identity, context references, tool bindings, and policies, generates the desk folder
skeleton, and produces a setup summary for HUMAN review.

## Guardrails (always)
- **Create ≠ run.** The command MUST NOT auto-run the created agent (FR-CMD-08).
- **No Shared Task Workspace** is created (Post-MVP).
- **No auto-promotion** of tools / knowledge / memory / blueprint. A custom desk does NOT
  auto-become a Blueprint (FR-AI-08) — it may later produce a Blueprint Creation Candidate for HUMAN review.
- **HUMAN gate** on desk-creation confirmation before the desk is considered active.
- Writes only under `agents/task_desks/<instance_id>/` (relative to the pack root; staging).

## Modes

### Mode A — Explicit Blueprint (FR-CMD-02)
HUMAN names the Blueprint.
```
/aiws-agent-create blueprint=<blueprint_id> [project=<project_id>]
```
- Look up `<blueprint_id>` in `agents/blueprint_registry.yaml`. If absent → tell HUMAN, offer Mode B or C.
- Generate `blueprint_ref.yaml` (blueprint id/version/relative path/customization summary).

### Mode B — AI-assisted Blueprint selection (FR-CMD-03)
No blueprint specified.
```
/aiws-agent-create
```
- Ask the purpose question (wizard Step 1), then **recommend** one or more registry Blueprints with a reason.
- HUMAN may: accept a recommendation · pick another Blueprint · switch to Mode C (custom).
- On accept → behaves like Mode A from that point.

### Mode C — Custom no-Blueprint (FR-CMD-04, FR-AI-06/07)
HUMAN intentionally creates a task desk with no existing Blueprint.
```
/aiws-agent-create mode=custom
# or
/aiws-agent-create no_blueprint=true
```
- Ask the minimum fields to populate `agent_design_snapshot.yaml` (see `agents/templates/agent_design_snapshot_template.yaml`).
- Generate `agent_design_snapshot.yaml` (`creation_mode: custom_no_blueprint`, `blueprint_id: null`)
  instead of `blueprint_ref.yaml` (a `blueprint_ref.yaml` with `blueprint_id: null` is also acceptable).
- Run the custom-instance validation checklist (`agents/templates/custom_instance_validation_checklist.md`)
  before showing the setup summary.
- **Process bootstrap (CR-AIWS-AGENT-FRAMEWORK-002 D8 / AP-CR-31):** no Blueprint process to copy → AI **bootstraps a draft** `process/agent_process.md` from the agent's mission + pre-trained knowledge, using markdown markers (`Reference intents:`, `Wiki lookup intents:`, `Expected output:`, `HUMAN gate:`, `Constraints:`). **HUMAN reviews/edits** before the desk is active. `governance_invariant`-tagged steps (wiki_first / evidence / conflict_report / no_auto_promote / human_gate) must be present (staging `lint_agents.py`).

## Wizard flow (8 steps — Detailed Design §6.2)
1. **Purpose** — what should this agent support? (build wiki meta / refresh wiki / create extraction tool /
   consume wiki for AIP planning / task context prep / output review)
2. **Blueprint selection or Custom mode** — Mode A confirm · Mode B recommend+confirm · Mode C custom.
3. **Identity** (AP-CR-23) — ask the friendly **`display_name` FIRST** (a person-name, e.g. `Henry`) — the renamable HUMAN-facing label. Then **auto-suggest `instance_id`** from the blueprint = `<blueprint_short>` — **strip the `aiws_` namespace prefix first** (ATDB `aiws_pm_agent` suggests desk id `pm_agent`, NOT `aiws_pm_agent`: the prefix marks who SHIPS the archetype, and a desk belongs to the project, not to AIWS — CR-AIWS-2026-08-017) (or `<blueprint_short>_<NN>` when a task desk of that blueprint already exists). For a **single-project** install **drop** the old mandatory `__<project>` suffix; keep an optional `__<project>` suffix only for **multi-project / shared-pool** use. Validate the `instance_id` against `_ID_RE` (`^[A-Za-z0-9][A-Za-z0-9_\-]{0,79}$`) **and** a folder-collision check under `agents/task_desks/`. Record `display_name` in `desk.yaml`. **`instance_id` is the stable machine key (never renamed); `display_name` is the renamable HUMAN-facing label.** Also capture project/context name + owner/reviewer.
4. **Context references** — wiki index/path, relevant wiki entries, source doc folders, source code folders,
   ignored paths, priority modules/domains.
   - **AI reference suggestion (CR-AIWS-AGENT-FRAMEWORK-002 D8):** AI proactively SUGGESTS candidate references by querying the project Wiki Source Index (`py .ai-work/tooling/lookup_wiki_source.py --query <mission keywords> [--system <id>]`) and scanning the project structure. Present candidates as `source_id / path / reason`; **HUMAN accepts / rejects / defers** — no auto-register, no auto-promote.
   - **Populate existing context refs** from accepted candidates: `wiki_references.yaml` (`recommended_entries` + `lookup_intents` = process intent → search_targets), `source_references.yaml`, `source_priority.yaml`, `working_inventory.yaml` (non-wiki / not-yet-indexed). Project-shared assets → register into the Wiki Source Index with `status: draft` (NOT a new root); not-shareable → keep in `working_inventory.yaml`.
   - **Degrade gracefully:** if the project Wiki/index is not ready or returns nothing, say so and let HUMAN populate manually — suggestion is an assist, not a hard gate.
5. **Tool bindings** — bind existing tools or declare tooling needs (candidate tools stay agent-local; no auto-activate).
6. **Policies** — memory policy, workspace policy, HUMAN review policy (offer defaults). **Includes `run_policy` (CR-AIWS-2026-08-007/009):** `aip_driven` · `aip_template` · `plan_first` · **`executor: main_session | claude_subagent`** (default `main_session`) — defaults from the ATDB.
7. **Generate files** — create the desk folder skeleton from templates (see "Generated files"). **Copy the blueprint's effective process into `process/` (flattened, self-contained) + capture `.atdb_snapshot/process/`** for A/B; custom (C) → **AI bootstraps a draft `process/agent_process.md`** for HUMAN review (CR-AIWS-AGENT-FRAMEWORK-002 D8; AP-CR-31 / Detailed Design §6D). **Then generate the Claude sub-agent shim (CR-AIWS-2026-08-007 T5):** `py tooling/build_agent_shims.py --desk <instance_id>` → `.claude/agents/<instance_id>.md` (generated artifact — clone/rename/upgrade also regenerate).
8. **Setup summary** — write `instance_readme.md` + show `instance_setup_summary` to HUMAN for confirm (preview: desk.yaml/desk.yaml + folder tree + shim). STOP (no run).

## Init question categories (FR-CMD-05 — 11 categories)
identity (`display_name` first, then auto-suggested `instance_id` — AP-CR-23) · project/context scope · mission customization · wiki references · source document references ·
source code paths · ignored paths · tool bindings · memory policy · workspace policy · review/HUMAN-gate policy.
(Keep the wizard sufficient but not heavy — see `agents/templates/instance_creation_wizard.md`.)

## Interview theo required-field manifest (CR-AIWS-2026-08-009)

Wizard chạy trên **required-field manifest** (bảng đầy đủ trong `agents/templates/instance_creation_wizard.md`):
field nào HUMAN đã cung cấp trong yêu cầu ban đầu → không hỏi lại; field **bắt buộc** còn trống → hỏi ĐÚNG
field đó (một câu, kèm default đề xuất); đủ manifest → present **toàn bộ set dự kiến** (identity preview +
cây thư mục + shim preview) → HUMAN confirm → mới ghi. Emit **full set một lần**: desk scaffold + process
(skeleton ∪ domain content) + `.atdb_snapshot` (kể cả path C: snapshot universal skeleton — để
upgrade/reconcile hoạt động) + shim `.claude/agents/<instance_id>.md` + `instance_readme.md` (identity +
capture-routing ack). **Một đường tạo duy nhất** — mọi NL trigger "tạo agent" route vào verb này; không có
creation path thứ hai.

## Generated files (FR-CMD-06)
Common to all modes, under `agents/task_desks/<instance_id>/`:
```
desk.yaml
instance_readme.md
context/{wiki_references,source_references,ignored_paths,source_priority}.yaml
memory/<files per the blueprint's memory_profile.required_files>                                                      # EMPTY skeleton — see "Memory set" note below (loop = Phase C)
workspace/{active_runs,completed_runs,handoff_artifacts,step_outputs}/                                                # EMPTY
training/{feedback_log.jsonl, candidate_queue.jsonl, periodic_review_log.md}                                          # EMPTY skeleton
tools/{local_tools/, tool_bindings.yaml}
changelog.md
```
**Memory — file SET per blueprint `memory_profile` (AP-CR-36 / FR-AI-05; Detailed Design §13):**
- **A / B (blueprint-based)** → scaffold EXACTLY the files in the selected blueprint's `memory_profile.required_files` (`initial_state: empty_skeleton` → all created EMPTY, no fabricated seed). The set is blueprint-specific (review-family = UNION-8; PM = its 8; coordinator = its 5) — do NOT hardcode a fixed 5-file list.
- **C (custom no-Blueprint)** → fall back to the common-minimal set `confirmed_memory.jsonl, lessons_learned.md, retrieval_hints.jsonl, local_guidelines.md, tool_usage_notes.md` (EMPTY).
- **Warm start (DP-913-C, CR-AIWS-2026-07-017):** when a same-role desk already exists and the HUMAN wants its learning, the DEFAULT path is `/aiws-agent-clone` from the nearest same-role desk + per-entry prune via `/aiws-agent-review-learning` (AP-CR-28 `clone_review: pending`) — NOT a wizard seed step. Create-from-blueprint stays cold-start (empty skeleton, no fabricated seed); a per-entry wizard seed picker is a gated follow-up only if clone proves too coarse.

**Process — desk-OWNED, copied on create (AP-CR-31 / FR-AI-13; Detailed Design §6D):**
- **A / B (blueprint-based)** → copy the blueprint's **effective process** (the `process_docs`-resolved file set in `blueprint.yaml` — e.g. the shared `_shared/review/process/*.md` — plus any blueprint-local process files) into `process/`, **flattened / self-contained** (rewrite any `../_shared/` relative refs to local). Also capture `.atdb_snapshot/process/` as the reconcile baseline. The desk follows ITS OWN `process/` from here on; it self-improves only via `process_improvement_candidate` (HUMAN-gated).
- **C (custom no-Blueprint)** → no base to copy (reconcile N/A): **AI bootstraps a draft `process/agent_process.md`** from mission + pre-trained knowledge (markers: Reference intents / Wiki lookup intents / Expected output / HUMAN gate / Constraints), then **HUMAN reviews/edits** before active (CR-AIWS-AGENT-FRAMEWORK-002 D8).
- `governance_invariant`-tagged steps copied from the base must NOT be silently dropped/weakened later (staging `lint_agents.py` warns).

Mode-specific:
- **A / B** → `blueprint_ref.yaml`
- **C** → `agent_design_snapshot.yaml` (and optionally `blueprint_ref.yaml` with `blueprint_id: null`)

## Setup summary (FR-CMD-07)
Produced from `agents/templates/instance_setup_summary.md`: selected Blueprint or custom mode, identity,
selected references, tool bindings, policies, open questions, setup warnings → for HUMAN review.

## After creation
- Desk is `status: active` only after HUMAN confirms the setup summary.
- The agent is **not** run by this command — HUMAN invokes it explicitly (Phase B+ run flow).
- If a custom desk proves reusable across runs, HUMAN may create a Blueprint Creation Candidate
  (`agents/templates/blueprint_creation_candidate_template.md`) — never automatic.
