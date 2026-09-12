# Instance Creation Wizard — HUMAN question flow

> Used by `/aiws-agent-create` (commands/aiws-agent-create.md). 8-step flow; 11 init categories.
> Keep it sufficient but not heavy — skip questions whose answer is already given on the command line.

## Required-field MANIFEST (CR-AIWS-2026-08-009) — interview chạy trên bảng này

Protocol: field HUMAN đã cung cấp (message/command line) → KHÔNG hỏi lại; field **✔ bắt buộc** còn trống →
hỏi ĐÚNG field đó (một câu, kèm default đề xuất); đủ manifest → present toàn bộ set dự kiến (identity +
cây thư mục + shim preview) → HUMAN confirm → MỚI ghi. Thêm/bớt field = sửa qua CR, không tuỳ biến ngầm.

| Field | Bắt buộc | Wizard step | Ghi chú |
|---|---|---|---|
| `archetype` (ATDB) | ✔ | 2 | menu ATDB hiện có; không khớp → Mode C + universal skeleton |
| `desk_id` (`instance_id`) + `display_name` | ✔ | 3 | validate `_ID_RE` + collision (instances/ · `previous_ids` · `.claude/agents/`) |
| `role scope` + `non_responsibilities` | ✔ | 4 | scope 1 đoạn; non_responsibilities list |
| `tools whitelist` | ✔ | 6 | default từ ATDB; **luôn loại `Agent`** (no chaining) |
| `run_policy` (aip_driven · aip_template · executor · plan_first) | ✔ | 7 | defaults từ ATDB; executor per CR-2026-08-007 |
| `desk load policy` | ✔ | 7 | default digest+hints (AP-CR-26/CR-017) |
| `output contract` | ✔ | 7 | shape từ ATDB; format cụ thể có thể project-local |
| `domain content` | ✔ (`none` tường minh được phép) | 5 | HUMAN đưa nội dung / trỏ file / chọn `reference_content` seed của ATDB (CR-2026-08-008) |
| `capture routing ack` | ✔ | 8 | xác nhận đã đọc `_shared/common/capture_routing_rule.md` (ghi vào instance_readme) |
| `language / spec refs` | ○ | 5 | optional |

## Step 1 — Purpose
- What should this agent support? (build wiki meta / refresh wiki / create extraction tool /
  consume wiki for AIP planning / task context prep / output review / other)

## Step 2 — Blueprint selection or Custom mode
- Mode A: confirm the named Blueprint.
- Mode B: AI recommends Blueprint(s) + reason → HUMAN accepts / picks another / switches to custom.
- Mode C: custom no-Blueprint → collect the `agent_design_snapshot.yaml` minimum fields.

## Step 3 — Identity  *(category: identity, project/context scope)*  *(AP-CR-23)*
- **`display_name`?** *(ask FIRST)* — a friendly person-name HUMAN label (e.g. `Henry`). Renamable.
- project / context name?
- suggested `instance_id`? — auto-suggest from the blueprint, then confirm. Convention:
  - `<blueprint_short>` — single-project default (one instance of the blueprint).
  - `<blueprint_short>_<NN>` — multiple instances of the SAME blueprint (e.g. `_01`, `_02`).
  - append `__<project>` ONLY for multi-project / shared-pool setups.
  - `instance_id` = stable machine key — **never renamed** once set (rename `display_name` instead).
- owner / reviewer?

## Step 4 — Mission customization  *(category: mission)*
- What is the instance's specific mission emphasis for this project?

## Step 5 — Context references  *(categories: wiki refs, source doc refs, source code paths, ignored paths)*
- wiki index / path? relevant existing wiki entries?
- source document folders?
- source code folders?
- ignored paths (generated/vendor/cache)?
- priority modules / domains?

## Step 6 — Tool bindings  *(category: tool bindings)*
- bind existing tools? (list tool ids) — or declare tooling needs (candidate tools stay agent-local, no auto-activate)

## Step 7 — Policies  *(categories: memory, workspace, review/HUMAN-gate)*
- memory policy (default: capture after run, no auto-confirm, HUMAN review required)
- workspace policy (default: save run history + handoff artifacts)
- review / HUMAN-gate policy (default: HUMAN review for memory_update / tool_activation / wiki_candidate / blueprint_improvement)
- **run_policy (CR-2026-08-007/009):** `aip_driven`? `aip_template`? `plan_first`? **`executor`** (`main_session` default | `claude_subagent`) — defaults từ ATDB
- desk load policy (default: digest + hints scoped-load — AP-CR-26/CR-017; KHÔNG "đọc hết bàn")

## Step 8 — Generate + Summary
- Generate the instance folder skeleton from templates.
- **Process (AP-CR-31 / §6D):** A/B (blueprint-based) → copy the blueprint's effective process (`process_docs`-resolved set, flattened/self-contained) into `process/` + capture `.atdb_snapshot/process/`; C (custom) → author a minimal own `process/` + snapshot universal skeleton (để upgrade/reconcile hoạt động). The instance owns its process thereafter (`governance_invariant` steps must not be silently dropped).
- **Shim (CR-2026-08-007 T5):** `py tooling/build_agent_shims.py --desk <instance_id>` → `.claude/agents/<instance_id>.md` (generated — sửa tay sẽ bị ghi đè).
- Write `instance_readme.md` (kèm capture-routing ack); produce `instance_setup_summary` (instance_setup_summary.md) for HUMAN review — **preview đủ set trước khi ghi** (manifest protocol).
- **STOP** — do not run the agent (FR-CMD-08).
