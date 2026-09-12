---
artifact_type: aip_plan
artifact_id: AIP-PLAN-001
title: "`<title>`"
status: draft
# status: (auto) — `aiws-aip run start` flips draft → active (CR-AIWS-2026-07-040); close sets done by hand (draft|active → done).
project: "`<project-name>`"
owner: "`<optional>`"
updated_at: YYYY-MM-DD
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. Refs: AIP_Detail_Spec §2.3/§10/§11. -->

# AIP_PLAN — `<title>`

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — Universal Gates áp cho **mọi AIP** (bao gồm cả giai đoạn lập plan):
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — xem `STEP-00` bên dưới
- **Gate U2 Confirm-understanding-of-input (soft)** — xem `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — xem `## Open Questions` + workspace `05_open_questions.md`

## Task Classification
- Why PLAN is used:
- Expected next artifact:
  - [ ] AIP_EXEC
  - [ ] direct execution without separate EXEC
  - [ ] not decided yet

## Objective
...

## Selected Task Lens / Mode
<!-- OPTIONAL (CR-AIWS-2026-05-030 / -032; Task_Lens_Spec_MVP v0.9.9 + presets addendum v0.9.13). The Task Lens is an
ADDITIVE, non-exhaustive HINT that shapes which source_types/reference_types to reference (Wiki First refs) and the ASC
reading-surface order. Consult presets in `.ai-work/wiki/task_lens_presets/`. aiws-aip create front-loads (Resolved
references); aiws-aip run resolves only Deferred lookups. No-Lens is valid — set Lens to No-Lens with a reason, or leave
empty. lint_aip does NOT require this section. -->
- Lens: `<preset lens_id (e.g. planning_wbs / requirement_authoring), a custom/runtime lens, or No-Lens>`
- Reason: `<why this lens fits the task intent (or why No-Lens)>`
- Search/execution effect: `<which source_types/reference_types it prioritises for inputs + reading surface>`
- Resolved references: `<subject docs + reference standards (guideline/checklist/template/SOP) already filled into the Wiki First refs at create time — AI inference ∪ lens; NOT copied verbatim from the lens list>`
- Deferred lookups: `<doc still to find + which lens — aiws-aip run resolves these at execution; empty if all resolved>`
- Expansion allowed: `<yes/no — may AI read broader than the lens when correctness needs it>`
> Note: the lens is an **ADDITIVE** hint (also-consider), not the input spec — AI inference is **primary**; inputs = inference ∪ lens, never lens-only/filter (`Task_Lens_Spec_MVP` §F).

## Background / Context
- ...

## Scope
### In Scope
- ...

### Out of Scope
- ...

## Expected Outputs
- ...

## References to Read First
### Truth First
- ...

### Wiki First
- ...

### Optional Supporting Refs
- ...

## Input Understanding
<!-- Gate U2 — soft gate. AI viết ý hiểu về từng input artifact chính dùng cho planning. Bỏ trống nếu không có input. -->

| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
|  |  |  |  | ⬜ pending / ✅ / ❌ |

## Assumptions / Constraints
- ...

## Open Questions
<!-- Gate U3. Summary; detail + history trong `05_open_questions.md` của workspace. -->
- Open Points log: `.ai-work/workspaces/<account_id>/{TASK-ID}/05_open_questions.md`  (CR-015 v2 per-account; `<account_id>` from account_info.yaml)
- (no open questions yet)

## Risks / Constraints
- ...

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
<!-- Gate U1 — Universal. Bắt buộc cho mọi task substantive. Skip chỉ khi BrSE explicit ủy quyền. -->

Objective:
Viết ra ý hiểu về task-to-be-planned (scope, expected plan output, Done definition) và dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1
- wiki:none — HARD GATE preflight default. Replace with the relevant `product/wiki_guidelines/...` path after running `lookup_wiki_source.py`; keep `wiki:none` only when pre-flight confirms no wiki coverage.

Recommended Skills:
- (none — direct reasoning + confirm)

Inputs:
- User request / upstream ROOT AIP reference

Expected Outputs:
- Task understanding note trong workspace
- BrSE confirmation evidence

Done Condition:
BrSE explicit confirm ý hiểu (hoặc explicit ủy quyền skip gate).

Notes / Constraints:
- Không bắt đầu draft plan cho tới khi gate pass.

Workspace Actions:
- Write task understanding → workspace
- Log BrSE confirmation

### Step: STEP-01 — `<step title>`
Objective:
...

Recommended Mode:
Planning

Applicable Guidelines:
- ...

Recommended Skills:
- ...

Inputs:
- ...

Expected Outputs:
- ...

Step Output / Execution Artifact:
- ...

Done Condition:
...

Notes / Constraints:
...

Workspace Actions:
- ...

## Done Criteria
- [ ] Scope đủ rõ
- [ ] Output đủ rõ
- [ ] Execution skeleton đủ để chuyển sang EXEC
- [ ] **Gate U1** confirmed — evidence trong workspace
- [ ] **Gate U2** Input Understanding đã ghi (hoặc task không có input)
- [ ] **Gate U3** Mọi open point trong `05_open_questions.md` có conclusion hoặc status pending+ETA

## Review Points
- ...

## Handoff to EXEC
- objective
- scope / non-scope
- expected outputs
- refs
- step skeleton
- open questions (link tới `05_open_questions.md`)
- risks / constraints
- done criteria
- review points
- Gate U1/U2/U3 status (để EXEC không phải redo từ đầu)

## Re-plan Log
<!-- Append entry on scope/objective/output change. Format: ### YYYY-MM-DD — title / Trigger / Change / Evidence ref / Approved by. -->

- (no re-plan yet)

---

## v0.9.9 Working AIP Connection note

For non-trivial execution, instantiate/adapt this template into a task-specific Working AIP before execution.

Template alone is not Working AIP.

Working AIP should include task intent, scope, expected output, selected context/source references, execution steps, guardrails, open questions/blockers, and done criteria.
