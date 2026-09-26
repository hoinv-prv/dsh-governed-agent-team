---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-016-STEP-03
task_id: TASK-20260926-exec-016
working_aip_ref: AIP-EXEC-016
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-016-recheck-gat-sections.md
active_step_id: STEP-03
active_step_title: Finalize Review
source_aip: AIP-EXEC-016
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-016-recheck-gat-sections.md
step_id: STEP-03
step_index: 4
step_total: 4
status: active
active_task_lens: design_review
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Finalize Review

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Recheck only §§6.6, 6.9, and 7 of the GAT design/feature reference against the durable-agents MiniMVP and current GAT team-config/tool sources, and report only remaining material discrepancies concerning the nine named prior concerns.
- Final outcome (AIP Expected Outputs):
  - Advisory review evidence in the task workspace.
  - Final response listing remaining material discrepancies only, or `None.`
- Scope:
  - Target document §§6.6, 6.9, and 7 only.
  - Durable-agent MiniMVP clauses relevant to fallback scope, byte limit, route authority, SOUL ordering, per-task loading, manifest snapshots, restart admission, conditional sharing, and filesystem ownership.
  - Current GAT team-config and tool sources that implement or constrain those points.
  **Out of Scope:**
  - Other target-document sections except cross-references necessary to interpret the scoped text.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Materialize Cross-document Review Scaffold  [upstream — done]
- STEP-02 — Verify Corrections Against Specification and Sources  [upstream — done]
- STEP-03 — Finalize Review  ◀ ACTIVE (step 4 of 4)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Advisory review evidence in the task workspace.
  - Final response listing remaining material discrepancies only, or `None.`
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Only material semantic/behavioral mismatches are reportable.
  - Do not broaden the target-document review beyond §§6.6, 6.9, and 7.
- **Known Open Points:**
  - None at creation.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md
- /home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md
- Current GAT team-config and tool sources discovered from explicit references in the scoped sections and bounded source search.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT design/feature reference | (none) | docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md | Direct HUMAN path; wiki lookup and semantic retry did not resolve it | [retrieval_gap] |

## Workspace Actions
- Complete final capture sweep and final output.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Scoped lint has zero errors and final output contains only remaining material discrepancies or `None.`

## Active Task Lens
- design_review
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Run capture sweep and scoped lint, then produce the discrepancies-only answer.

## Recommended Mode
Reviewing

## Applicable Guidelines
- .ai-work/procedural/skills/aiws-aip/operations/run.md

## Recommended Skills
- aiws-lint

## Inputs
- Review workspace artifacts

## Expected Outputs
- Clean scoped lint result
- Final concise response

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Scoped lint has zero errors and final output contains only remaining material discrepancies or `None.`

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Do not include a concern-by-concern success recap when no discrepancies remain.

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
- OUT-016-01-01 —  (draft)
- OUT-016-02-01 —  (draft)

## Capture Inbox References
- CAP-016-01 — retrieval gap: GAT_DESIGN_AND_FEATURE_REFERENCE.md (captured)
- CAP-016-02 — retrieval gap: DURABLE_AGENTS_MINIMVP.md (captured)
