---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-plan-001-STEP-04
task_id: TASK-20260926-plan-001
working_aip_ref: AIP-PLAN-001
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/plan/AIP-PLAN-001-gat-dsh-durable-agent-team-plan.md
active_step_id: STEP-04
active_step_title: Define verification, review gates, and final recommendation
source_aip: AIP-PLAN-001
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/plan/AIP-PLAN-001-gat-dsh-durable-agent-team-plan.md
step_id: STEP-04
step_index: 5
step_total: 5
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Define verification, review gates, and final recommendation

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Tạo một kế hoạch evidence-backed để chỉnh sửa design và implementation của GAT, nhằm tích hợp vào DSH thành một durable agent team có thể thực hiện mission, trong khi giữ GAT là lifecycle/mission authority và dùng member-binding extension làm boundary cho Durable Agent cùng các capability tương lai.
- Final outcome (AIP Expected Outputs):
  - Workspace findings về current-state GAT và proposal-to-code gap matrix.
  - Target design delta có ownership/API/state/persistence/lifecycle boundaries.
  - Implementation roadmap theo phases/work packages, dependencies và migration order.
  - Verification matrix liên kết acceptance criteria với unit/integration/recovery/disposal/UI/SDK tests.
  - Decision log/open questions và handoff skeleton đủ để tạo một hoặc nhiều AIP_EXEC.
- Scope:
  - Map proposal requirements và acceptance criteria sang current GAT design/code/tests.
  - Xác định design changes: ownership boundaries, APIs/contracts, state machine, persistence/replay, initializer adapter, binding registry, prompt/tool contribution, mission lifecycle và diagnostics.
  - Xác định implementation work packages, dependencies, migration/compatibility strategy, test strategy và review gates.
  - Chỉ rõ integration contract giữa GAT plugin và DSH core/Durable Agent mà GAT cần tiêu thụ hoặc yêu cầu.
  - Đề xuất thứ tự delivery an toàn, ưu tiên backward compatibility của GAT-only mode.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Inventory current GAT architecture and implementation  [upstream — done]
- STEP-02 — Define target design delta and integration boundary  [upstream — done]
- STEP-03 — Build implementation and migration roadmap  [upstream — done]
- STEP-04 — Define verification, review gates, and final recommendation  ◀ ACTIVE (step 5 of 5)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Workspace findings về current-state GAT và proposal-to-code gap matrix.
  - Target design delta có ownership/API/state/persistence/lifecycle boundaries.
  - Implementation roadmap theo phases/work packages, dependencies và migration order.
  - Verification matrix liên kết acceptance criteria với unit/integration/recovery/disposal/UI/SDK tests.
  - Decision log/open questions và handoff skeleton đủ để tạo một hoặc nhiều AIP_EXEC.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
- (see AIP §References to Read First)

## Workspace Actions
- Hoàn thiện final plan trong workspace và chạy task lint.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Plan có traceability từ proposal → current evidence → design delta → implementation package → verification evidence.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Liên kết acceptance criteria với tests/evidence, review risks và đưa ra recommended delivery sequence.

## Recommended Mode
Review planning

## Applicable Guidelines
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

## Recommended Skills
- `dsh-council-review`

## Inputs
- Target design delta.
- Implementation roadmap.
- Proposal acceptance criteria and risks.

## Expected Outputs
- Acceptance-to-verification matrix.
- Risk register and HUMAN decision points.
- Final design/implementation plan and EXEC handoff recommendation.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Plan có traceability từ proposal → current evidence → design delta → implementation package → verification evidence.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Advisory review không tự phê duyệt canonical/DSH upstream changes.

## Operating Memory (L2 — bài học vận hành)
- Lát cắt: mọi nhóm (step không khai Kind)
- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical (`.ai-work/procedural/operating_memory.md`).
- (Operating Memory trống — chưa có mục nào)

## Coverage
**Coverage Gaps:**
- Step Output / Decision Persistence Requirements (trimmed → spec §7.2)
- Source Verification Requirements (trimmed → spec §5)
- Unresolved AIP references (guidance pointers only)
- No expected outputs declared (inherited from AIP)

## Previous Step Results / Handoff Inputs
- OUT-001-01-01 —  (draft)
- OUT-001-02-01 —  (draft)
- OUT-001-03-01 —  (draft)

## Capture Inbox References
- CAP-001-01 — retrieval gap: DSH GAT member-binding extension proposal (captured)
- CAP-001-02 — retrieval gap: GAT–Durable Agent integration boundary (captured)
- CAP-001-03 — retrieval gap: maintained GAT design reference (captured)
