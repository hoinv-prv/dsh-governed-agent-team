---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260913-exec-003-STEP-02
task_id: TASK-20260913-exec-003
working_aip_ref: AIP-EXEC-003
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-003-update-agents-project-context.md
active_step_id: STEP-02
active_step_title: Verify and Finalize
source_aip: AIP-EXEC-003
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-003-update-agents-project-context.md
step_id: STEP-02
step_index: 3
step_total: 3
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-13
---

# Active Step Context — Verify and Finalize

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Cập nhật phần project context trong `AGENTS.md` để mô tả đúng rằng repository này xây dựng Governed Agent Team dưới dạng DSH plugin, đồng thời ghi nhận ngôn ngữ làm việc Vietnamese + English mixed.
- Final outcome (AIP Expected Outputs):
  - `AGENTS.md` có project description và user language đã được cập nhật.
  - Bằng chứng lint/kiểm tra cuối task.
- Scope:
  - Thay placeholder mô tả project trong `AGENTS.md` bằng mô tả ngắn, chính xác.
  - Thay placeholder user language bằng `Vietnamese + English mixed`.
  - Giữ nguyên toàn bộ khối AIWS generated rules.
  **Out of Scope:**
  - Không sửa `.ai-work/truth/` hoặc khối `AIWS:BEGIN rules`.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Update Project Context  [upstream — done]
- STEP-02 — Verify and Finalize  ◀ ACTIVE (step 3 of 3)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - `AGENTS.md` có project description và user language đã được cập nhật.
  - Bằng chứng lint/kiểm tra cuối task.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Do not edit the generated AIWS rules block.
  - Avoid inventing technical capabilities not supplied by the human.
- **Known Open Points:**
  - No blocking open points.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Project context guidance | (none) | (no applicable project source found; lookup performed) | One-off context update | wiki:none |

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Targeted content is correct, generated rules remain intact, and lint has been run.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Verify the targeted update and run the required lint checks.

## Recommended Mode
Verifying

## Applicable Guidelines
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

## Recommended Skills
- ...

## Inputs
- Updated `AGENTS.md`
- AIP and workspace artifacts

## Expected Outputs
- Verification evidence in workspace.
- Lint result reported honestly.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Targeted content is correct, generated rules remain intact, and lint has been run.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Do not auto-fix Truth or canonical Wiki content.

## Operating Memory (L2 — bài học vận hành)
- Lát cắt: mọi nhóm (step không khai Kind)
- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical (`.ai-work/procedural/operating_memory.md`).
- (Operating Memory trống — chưa có mục nào)

## Coverage
**Coverage Gaps:**
- Step Output / Decision Persistence Requirements (trimmed → spec §7.2)
- Source Verification Requirements (trimmed → spec §5)
- No expected outputs declared (inherited from AIP)

## Previous Step Results / Handoff Inputs
- OUT-003-01-01 —  (draft)
