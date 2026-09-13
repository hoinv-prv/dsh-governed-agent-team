---
artifact_type: aip_exec
artifact_id: AIP-EXEC-003
title: "Update AGENTS.md project context"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260913-exec-003
updated_at: 2026-09-13
---

<!-- Stable control: runtime state belongs in the workspace, not this AIP. -->

# AIP_EXEC — Update AGENTS.md project context

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — áp dụng Universal Gates cho task substantive.

## Objective
Cập nhật phần project context trong `AGENTS.md` để mô tả đúng rằng repository này xây dựng Governed Agent Team dưới dạng DSH plugin, đồng thời ghi nhận ngôn ngữ làm việc Vietnamese + English mixed.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: Task hẹp, chỉ cập nhật metadata/context của project; không cần suy rộng sang design hoặc wiki authoring.
- Search/execution effect: Chỉ đọc input trực tiếp và kiểm tra cấu trúc AGENTS.md.
- Resolved references: `.ai-work/truth/SOP_MASTER.md`, `.ai-work/truth/AI_WORK_CONTRACT.md`
- Deferred lookups: none
- Expansion allowed: no, trừ khi cần kiểm tra lint.

## Execution Scope
### In Scope
- Thay placeholder mô tả project trong `AGENTS.md` bằng mô tả ngắn, chính xác.
- Thay placeholder user language bằng `Vietnamese + English mixed`.
- Giữ nguyên toàn bộ khối AIWS generated rules.

### Out of Scope
- Không sửa `.ai-work/truth/` hoặc khối `AIWS:BEGIN rules`.
- Không thiết kế hay triển khai plugin code.
- Không thay đổi canonical/wiki content.

## Expected Outputs
- `AGENTS.md` có project description và user language đã được cập nhật.
- Bằng chứng lint/kiểm tra cuối task.

## Execution Input Package
### Plan Source
- Direct human request: dự án build “Governed Agent Team” dsh plugin.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Project context guidance | (none) | (no applicable project source found; lookup performed) | One-off context update | wiki:none |

### Reference lookup
- Wiki preflight query: `Governed Agent Team dsh plugin project context`.
- Lookup returned only generic AIWS methodology/guideline candidates; no project-specific description source was applicable.

### Required Workspace Preconditions
- [ ] Workspace created if needed
- [ ] Active Step Context available
- [ ] `05_open_questions.md` initialized if open points arise

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| Human request | Project is a DSH plugin for building a Governed Agent Team. | Exact product tagline is intentionally kept concise. | None blocking. | ✅ direct request |
| `AGENTS.md` | Only lines 5–9 are project-owned placeholders; generated AIWS block must remain unchanged. | User language preference is Vietnamese + English mixed, consistent with request. | None. | ✅ inspected |

## References to Read First
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

## Current Risks / Constraints
- Do not edit the generated AIWS rules block.
- Avoid inventing technical capabilities not supplied by the human.

## Known Open Points
- No blocking open points.

## Workspace Execution Rule
Runtime notes, findings, and verification evidence belong in the task workspace. This AIP remains stable control.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record the inferred scope and deliverable before editing.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- wiki:none — project-specific context source was not found in lookup.

Inputs:
- Direct human request
- Current `AGENTS.md`

Expected Outputs:
- Workspace task-understanding note.

Done Condition:
Scope is clear: update only project-owned placeholders in `AGENTS.md`.

Notes / Constraints:
- No edit to the generated AIWS block.

### Step: STEP-01 — Update Project Context
Objective:
Replace the project and language placeholders in `AGENTS.md` with concise project-owned text.

Recommended Mode:
Executing

Applicable Guidelines:
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

Inputs:
- Confirmed task understanding
- Existing `AGENTS.md`

Expected Outputs:
- Updated `AGENTS.md`.

Done Condition:
The placeholders are replaced and the AIWS generated block is byte-for-byte unchanged.

Notes / Constraints:
- Use only facts supplied by the human: this is a DSH plugin project building a Governed Agent Team.

### Step: STEP-02 — Verify and Finalize
Objective:
Verify the targeted update and run the required lint checks.

Recommended Mode:
Verifying

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

Inputs:
- Updated `AGENTS.md`
- AIP and workspace artifacts

Expected Outputs:
- Verification evidence in workspace.
- Lint result reported honestly.

Done Condition:
Targeted content is correct, generated rules remain intact, and lint has been run.

Notes / Constraints:
- Do not auto-fix Truth or canonical Wiki content.

## Done Criteria
- [ ] `AGENTS.md` accurately identifies the project as a DSH plugin for building a Governed Agent Team.
- [ ] User language is recorded as Vietnamese + English mixed.
- [ ] AIWS generated rules block is unchanged.
- [ ] AIP and task lint checks have been run and results recorded.

## Self-check / Review Points
- Confirm only lines outside `AIWS:BEGIN rules` / `AIWS:END rules` changed.
- Confirm no unsupported product claims were added.

## Finalization Notes
- Final status is reported after verification; runtime evidence remains in the workspace.

## Pre-flight Pending Captures
<!-- No reusable artifact lookup gap identified. -->

## Re-plan Rule
Any change to scope, target files, or project description detail requires a dated Re-plan Log entry before editing.

## Re-plan Log
- 2026-09-13 — Initial plan created from direct human request; no scope change.
