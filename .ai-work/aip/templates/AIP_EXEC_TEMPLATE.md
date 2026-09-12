---
artifact_type: aip_exec
artifact_id: AIP-EXEC-001
title: "`<title>`"
status: draft
# status: (auto) — `aiws-aip run start` flips draft → active (CR-AIWS-2026-07-040); close sets done by hand (draft|active → done).
project: "`<project-name>`"
owner: "`<optional>`"
plan_source: AIP-PLAN-001
# runtime_workspace: (auto) — written by `aiws-aip run start`; write-once provenance pointer to the runtime workspace (CR-AIWS-2026-06-015 F5). Do NOT hand-edit; NOT runtime state (AIP_Detail_Spec §2.3).
# template_source: (auto) — written by `aiws-aip create`; write-once provenance = basename of the template this AIP was instantiated from (default `AIP_EXEC_TEMPLATE`). Do NOT hand-edit; NOT runtime state (AIP_Detail_Spec §2.3). Consumed by the Agent-Pack run-gate conformance check (CR-AIWS-2026-06-050).
updated_at: YYYY-MM-DD
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. Refs: AIP_Detail_Spec §2.3/§10/§11. -->

# AIP_EXEC — `<title>`

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — Universal Gates áp cho **mọi task substantive**:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — xem `STEP-00` bên dưới
- **Gate U2 Confirm-understanding-of-input (soft)** — xem `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — xem `## Known Open Points` + workspace `05_open_questions.md`

## Objective
...

## Selected Task Lens / Mode
<!-- OPTIONAL (CR-AIWS-2026-05-030 / -032; Task_Lens_Spec_MVP v0.9.9 + presets addendum v0.9.13). The Task Lens is an
ADDITIVE, non-exhaustive HINT that shapes which source_types/reference_types to reference (Required Wiki Inputs +
References) and the ASC reading-surface order. Consult presets in `.ai-work/wiki/task_lens_presets/` (default
`starter_lenses.yml`). aiws-aip create front-loads (Resolved references); aiws-aip run resolves only Deferred lookups. No-Lens is
valid — set Lens to No-Lens with a reason, or leave this section empty. lint_aip does NOT require this section. -->
- Lens: `<preset lens_id (e.g. design_review / design_authoring), a custom/runtime lens, or No-Lens>`
- Reason: `<why this lens fits the task intent (or why No-Lens)>`
- Search/execution effect: `<which source_types/reference_types it prioritises for inputs + reading surface>`
- Resolved references: `<subject docs + reference standards (guideline/checklist/template/SOP) already filled into Required Wiki Inputs + References at create time — AI inference ∪ lens; NOT copied verbatim from the lens list>`
- Deferred lookups: `<doc still to find + which lens — aiws-aip run resolves these at execution; empty if all resolved>`
- Expansion allowed: `<yes/no — may AI read broader than the lens when correctness needs it>`
> Note: the lens is an **ADDITIVE** hint (also-consider), not the input spec — AI inference is **primary**; inputs = inference ∪ lens, never lens-only/filter (`Task_Lens_Spec_MVP` §F).

## Execution Scope
### In Scope
- ...

### Out of Scope
- ...

## Expected Outputs
- ...

## Execution Input Package
### Plan Source
- ...

### Required Truth Inputs
- ...

### Required Wiki Inputs
<!-- Capture flag convention:
  —              = artifact đã có wiki source hoặc one-off không cần register
  [retrieval_gap] = reusable artifact chưa có wiki source → add entry vào ## Pre-flight Pending Captures ngay
  wiki:none      = pre-flight lookup confirmed không có wiki coverage (expected, not a gap)
  KHÔNG áp cho Truth: artifact dưới `.ai-work/truth/**` khai ở ## Required Truth Inputs (section riêng,
  không có cột Wiki Source ID) và KHÔNG BAO GIỜ mang [retrieval_gap] — CR-AIWS-2026-08-130.
-->

| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| I-01 ... | SRC-... | path/to/artifact.md | ... | — |
| I-02 ... | (none) | path/to/artifact.md | reusable, chưa đăng ký | [retrieval_gap] |

### Reference lookup
- Default: `py .ai-work/tooling/lookup_wiki_source.py --query <kw> --limit 20`  (output is **slim** by default — 1 line/result)
- Scope (CR-AIWS-2026-06-052): default scope = `project,aiws` (registered project + AIWS indices). `local` is opt-in and authorization-gated — pass `--scope project,local --authorized human` only when a HUMAN authorizes local-wiki search (rule #11). Raw (un-registered) search needs `--include-raw {on-empty|always}` + `--authorized {human|aip|agent-rule}`; absent → the tool halts and asks (never silent raw / silent miss).
- Override (per use-case): AIP step / HUMAN may set `--limit` / `--mode` differently, or add `--full`
  for verbose multi-line records (targeted, 1 known doc → `--limit 5`; content-verification read → `--full`).
- Scope-then-verify (authoring / review tasks):
  - **PHASE 1 — scope** (read 0 full docs): slim lookup → fix the reference set + record each candidate's score.
  - **PHASE 2 — verify Tier-1 only** (full read): read the top Tier-1 docs the work traces to and run the
    content-verification checklist (see `aiws-wiki lookup` SKILL → "Routing, not verification").
    Tier-2/3 stay meta-only; score-floor candidates → low-confidence skip.

### Required Workspace Preconditions
- [ ] Workspace created if needed
- [ ] Active Step Context available
- [ ] `05_open_questions.md` initialized (if open points are expected)

## Input Understanding
<!-- Gate U2 — soft gate. AI viết ý hiểu về từng input artifact sau khi đọc. BrSE có quyền reject. Bỏ trống nếu task không có input. -->

| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
|  |  |  |  | ⬜ pending / ✅ / ❌ |

## References to Read First
- ...

## Current Risks / Constraints
- ...

## Known Open Points
<!-- Gate U3. Summary here; detail + history trong `05_open_questions.md` của workspace. -->
- Open Points log: `.ai-work/workspaces/<account_id>/{TASK-ID}/05_open_questions.md`  (CR-015 v2 per-account; `<account_id>` from account_info.yaml)
- (no open points yet)

## Workspace Execution Rule
All execution steps should update workspace artifacts when applicable:
- Active Step Context
- Queue
- Findings
- Open Questions (`05_open_questions.md`) — Gate U3
- Draft Output
- Capture Inbox

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
<!-- Gate U1 — Universal. Bắt buộc cho MỌI task substantive. Skip chỉ khi BrSE explicit ủy quyền (ghi ủy quyền vào workspace findings). -->

Objective:
Viết ra ý hiểu về task (scope, expected output/deliverable, Done definition, assumptions) và dừng chờ BrSE confirm trước khi sang STEP-01.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1
- wiki:none — HARD GATE preflight default. Replace with the relevant `product/wiki_guidelines/...` path after running `lookup_wiki_source.py`; keep `wiki:none` only when pre-flight confirms no wiki coverage.

Recommended Skills:
- (none — direct reasoning + confirm)

Inputs:
- AIP PLAN handoff / user request
- Truth inputs declared above

Expected Outputs:
- Task understanding note trong workspace (findings/ hoặc dedicated file)
- BrSE confirmation evidence (user message hoặc ghi chú)

Done Condition:
BrSE explicit confirm ý hiểu (hoặc explicit ủy quyền skip gate).

Notes / Constraints:
- Không làm gì khác ngoài clarify/confirm ở step này.
- Nếu BrSE chỉnh hiểu biết → update note rồi re-confirm trước khi sang STEP-01.

Workspace Actions:
- Write task understanding → workspace
- Log BrSE confirmation

### Step: STEP-01 — `<step title>`
Objective:
...

Recommended Mode:
Executing

Applicable Guidelines:
- ...

Recommended Skills:
- ...

Inputs:
- ...

Expected Outputs:
- ...

Done Condition:
...

Notes / Constraints:
...

<!-- OPTIONAL step field (CR-AIWS-2026-07-018; activation CR-AIWS-2026-08-044 C0): `Assigned Agent:`
     — agent handle (== desk_id) expected to execute this step via the agents pack
     (`run_agent.py start <instance> --aip <this AIP>`), or `auto` (capability routing resolves the
     desk — CR-AIWS-2026-08-045). ABSENT = DEFAULT = KHÔNG dispatch — main session executes như AIWS
     thuần (không run/desk). ASC surfaces it; the runtime refuses a run on this AIP from an instance
     NOT in the AIP's assigned set (stage-3) and requires AIP `status: active`. -->

<!-- OPTIONAL step field (CR-AIWS-2026-08-044 C4): `Executor:` (main_session | claude_subagent) —
     plan-time executor cho step ĐÃ chỉ định; absent = desk default (`run_policy.executor`). Runtime
     validate ∈ desk `executors_allowed`. Surfaced into the ASC. Chỉ có nghĩa khi step có
     `Assigned Agent:`. -->

<!-- OPTIONAL step fields (CR-AIWS-2026-07-059): `Difficulty:` (low|medium|high) + `Kind:` (task-kind
     tags — triage, plan, code, patch_proposal, sql, test_design, review, research, organize,
     canonical_edit) — capability-routing inputs. Absent = unspecified. Surfaced into the ASC.
     Routing chỉ chạy khi step opt-in qua `Assigned Agent:` (CR-AIWS-2026-08-044 C0); Difficulty cũng
     chọn execution tier (cheapest-capable — CR-AIWS-2026-08-045). -->

<!-- OPTIONAL step field (CR-AIWS-2026-06-052): to pre-authorize raw (un-registered) search for THIS
     step, add a line `allow_raw_search: true` anywhere in the step block. It lets the agent run
     `lookup_wiki_source.py --authorized aip --include-raw on-empty --lookup-mode object` when a
     registered lookup misses. Omit (or `false`) = no grant — raw / local / beyond-default search stays
     HUMAN-authorization-gated (halt-and-ask). build_active_step_context surfaces an explicit grant into
     the ASC as "## Raw Search Authorization". -->

Workspace Actions:
- add only step-specific actions here

## Done Criteria
- [ ] Output đúng loại, đúng scope
- [ ] Output bám PLAN handoff hoặc direct execution justification
- [ ] **Gate U1** confirmed — evidence trong workspace
- [ ] **Gate U2** Input Understanding đã ghi (hoặc task không có input)
- [ ] **Gate U3** Mọi open point trong `05_open_questions.md` đã resolved / deferred / rejected với conclusion rõ ràng (hoặc không phát sinh open point)

## Self-check / Review Points
- ...

## Finalization Notes
- ...

## Pre-flight Pending Captures
<!-- Populated by aiws-aip create when wiki lookup miss for reusable artifact (see aiws-aip create SKILL.md §"Reusable artifact lookup miss"). -->
<!-- Swept by aiws-aip run start (step 1b) → imported to 08_capture_inbox.jsonl → entries marked [IMPORTED YYYY-MM-DD]. -->
<!-- Format: - [PENDING] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="..." lookup_query="..." reason="..." -->
<!-- `suggested_target` BẮT BUỘC thuộc `CAPTURE_TARGET_ENUM` (lint_workspace.py). Thiếu nó thì sweep để trống và cảnh báo stderr — không tự điền mặc định (CR-AIWS-2026-08-025). -->
<!-- Do NOT delete entries after import — AIP is stable control. Mark [IMPORTED] instead. -->

- (none)

## Re-plan Rule
Nếu cần thay đổi macro scope hoặc expected output:
- không silently drift
- tạo explicit re-plan entry trong "Re-plan Log" section bên dưới
- ghi evidence ref vào workspace findings/capture trước khi chỉnh AIP
- **sweep wording cũ trên TOÀN BỘ AIP này, và xác nhận `residual = 0`** — không dựa vào liệt kê tay
  (CR-AIWS-2026-08-077 C1)

**Sweep phải quét hết, không quét chỗ mình nhớ.** Một scope đổi để lại dấu ở nhiều mục hơn ta tưởng:
`Objective` · `Execution Scope` · `Expected Outputs` · `Input Understanding` · `Known Open Points` ·
`Done Criteria` · **mọi step** · và cả **front-matter `title`**. Liệt kê tay bỏ sót — đó là failure mode
đã quan sát được 4 lần, **2 trong đó xảy ra với người đang chủ động phòng nó**. Nên tiêu chí là bằng
chứng (`grep` ra 0), không phải trí nhớ.

**`residual` đo trên MARKER NỘI DUNG, không phải trên tên finding hay id.** Marker = đường dẫn cũ, số
cũ, tên mục/target cũ, id DP đã gỡ. Tên finding (`F18`) và id CR thì **phải** còn lại trong
`driving_source` và Revision History — đó là **provenance, không phải sót**. Đo nhầm lên tên finding thì
tiêu chí không bao giờ đạt: khi gỡ F18 khỏi CR-075, `grep F18` cho **7 hit trước và 7 hit sau** khi đã
gỡ sạch nội dung. Vì vậy: mỗi hit còn lại phải được **phân loại** — *provenance cố ý* hay *sót thật* —
và chỉ nhóm thứ hai mới tính vào `residual`.

## Re-plan Log
<!-- Append entry on scope/objective/output change. Format: ### YYYY-MM-DD — title / Trigger / Change / Evidence ref / Approved by. -->

- (no re-plan yet)

---

## v0.9.9 Working AIP Connection note

For non-trivial execution, instantiate/adapt this template into a task-specific Working AIP before execution.

Template alone is not Working AIP.

Working AIP should include task intent, scope, expected output, selected context/source references, execution steps, guardrails, open questions/blockers, and done criteria.
