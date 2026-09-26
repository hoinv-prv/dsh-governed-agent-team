---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-015-STEP-03
task_id: TASK-20260926-exec-015
working_aip_ref: AIP-EXEC-015
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-015-integrate-durable-agent-design.md
active_step_id: STEP-03
active_step_title: Review and finalize
source_aip: AIP-EXEC-015
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-015-integrate-durable-agent-design.md
step_id: STEP-03
step_index: 4
step_total: 4
status: active
active_task_lens: design_authoring
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Review and finalize

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Use the Durable Agents MiniMVP design as an external reference to extend the GAT design reference with the architectural relationship, shared manifest, responsibility boundary, persistence/context mapping, integration assumptions, gaps, and roadmap—without mislabeling Durable Agent behavior as already implemented in GAT.
- Final outcome (AIP Expected Outputs):
  - `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — updated with Durable Agent relationship and design mapping.
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md` — comparison and verification evidence.
- Scope:
  - Define how GAT orchestration relates to Durable Agent identity, SOUL, memory, and working storage.
  - Map the shared `team_members.yaml` fields and the additional `storage_scope` field.
  - Define separation of lifecycle/orchestration from durable definition/storage.
  - Document integration sequence, fail-closed rules, mismatches, and future work.
  - Update source/evidence and maintenance sections.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Durable Agent integration scope (HARD GATE)  [upstream — done]
- STEP-01 — Compare Durable Agent and GAT contracts  [upstream — done]
- STEP-02 — Update GAT design reference  [upstream — done]
- STEP-03 — Review and finalize  ◀ ACTIVE (step 4 of 4)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — updated with Durable Agent relationship and design mapping.
  - `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md` — comparison and verification evidence.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Both systems use `team_members.yaml`, but their accepted schema currently differs because Durable Agent adds `storage_scope` while the latest GAT loader rejects unknown keys.
  - Durable Agent explicitly does not spawn agents or manage runtime lifecycle; GAT must remain the orchestration owner.
  - A future integration must avoid two independent manifest parsers drifting silently.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/05_open_questions.md`
  - No blocker identified.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `team_members.yaml`
- Latest GAT core/tools sources identified by AIP-EXEC-014.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Durable Agent MiniMVP | (none) | `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md` | Wiki lookup and semantic escalation found no project source | [retrieval_gap] |

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Review is complete and task lint has zero errors, or residual issues are reported with evidence.

## Active Task Lens
- design_authoring
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Review the update against both documents, verify the schema incompatibility and boundary claims, and run AIWS lint.

## Recommended Mode
Reviewing

## Applicable Guidelines
- `.ai-work/procedural/skills/aiws-lint/SKILL.md`
- wiki:none

## Recommended Skills
- ...

## Inputs
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-015/04_findings.md`

## Expected Outputs
- Verification evidence and final output summary.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Review is complete and task lint has zero errors, or residual issues are reported with evidence.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
Perform final capture sweep before close.

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
- OUT-015-01-01 —  (draft)
- OUT-015-02-01 —  (draft)

## Capture Inbox References
- CAP-001 — Register Durable Agent design relationship (captured)
