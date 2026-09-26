---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260915-control-plane-stabilization-design-STEP-04
task_id: TASK-20260915-control-plane-stabilization-design
working_aip_ref: AIP-EXEC-009
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-009-control-plane-stabilization-design.md
active_step_id: STEP-04
active_step_title: Resolve findings and obtain reviewed design closure
source_aip: AIP-EXEC-009
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-009-control-plane-stabilization-design.md
step_id: STEP-04
step_index: 5
step_total: 6
status: active
active_task_lens: `design_review`
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-16
---

# Active Step Context — Resolve findings and obtain reviewed design closure

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Thiết kế lại control plane cho mission `multi-mission-web-ui` để loại bỏ vòng lặp reconcile → charge → phát hiện control defect → pause/re-plan; review thiết kế bằng `dsh-council-review` trên exact pinned bytes; chỉ tạo decision-ready handoff cho WBS revision kế tiếp sau khi review closure đạt, không build hoặc execute WBS trong AIP này.
- Final outcome (AIP Expected Outputs):
  - `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v1.md`
  - Một hoặc nhiều immutable council runs dưới `wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/`
  - Nếu cần correction: `control-plane-stabilization-design.v2.md` và council run mới có lineage.
  - `wbs-runs/multi-mission-web-ui/control-plane-stabilization-handoff.md`
  - Workspace findings, open-point log, review checklist và final output.
- Scope:
  - Phân loại root cause thành systemic cause, contributing conditions và symptoms dựa trên evidence hiện có.
  - Thiết kế một pre-charge admission protocol atomic, explicit state machine, artifact ownership, rollback/recovery, reviewer availability, continuation and budget-slack gates.
  - Thiết kế migration strategy cho legacy execution ledger theo backup-first/lossless/strict-validation.
  - Tạo traceability từ mỗi failure đã quan sát tới control, evidence và owner.
  - Chạy high-risk council review với design + governance modes, independent internal lanes, required outside view và separate Chairman.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Establish evidence-bound failure model  [upstream — done]
- STEP-02 — Author control-plane stabilization design v1  [upstream — done]
- STEP-03 — Run immutable high-risk council review  [upstream — done]
- STEP-04 — Resolve findings and obtain reviewed design closure  ◀ ACTIVE (step 5 of 6)
- STEP-05 — Produce decision-ready WBS-build handoff  [downstream]

## Downstream / Output Contract
- Next step (STEP-05 — Produce decision-ready WBS-build handoff) needs as Inputs:
  - Latest reviewed design and council report
  - Finding dispositions
- Shape this step's output to satisfy the above + the AIP final outcome (see AIP Goal & Outcome).

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Prior reviews passed artifacts that later failed deterministic or semantic checks; review must pin closed must-check items and exact bytes.
  - Legacy ledger strict-validation defect prevents trusting execution-backed progress projection.
  - Current attempt allocation has no contingency slack; this design must make the trade-off explicit rather than silently fit work.
  - A single reviewer/runtime failure must not be interpreted as artifact failure or acceptance.
  - Global council skill paths are read-only procedural inputs; DSH checkout remains forbidden.
- **Known Open Points:**
  - Workspace log: `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/05_open_questions.md`.
  - Whether later WBS raises the ceiling or reduces downstream maxima is intentionally a HUMAN decision after reviewed design.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md`
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `wbs-runs/multi-mission-web-ui/progress-analysis.v32.md`
- `wbs-runs/multi-mission-web-ui/wbs.v32.json`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| AIWS architecture | `SRC-METHOD-methodology-10-design-architecture-design-mvp-md-994c` | `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md` | actor/component and Working-AIP boundary | — |

## Workspace Actions
- Update findings/open questions and preserve run lineage.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Latest immutable design has council verdict `pass` or `pass_with_notes`, or the remaining blocking decision is explicitly escalated to HUMAN; no earlier run is overwritten.

## Active Task Lens
- `design_review`
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Disposition council findings; if material revision is required, author immutable design v2 and run a new full council review with lineage before handoff.

## Recommended Mode
Designing + Reviewing

## Applicable Guidelines
- `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/SKILL.md`

## Recommended Skills
- `dsh-council-review`

## Inputs
- `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md#council-review-v1`
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v1.md`
- `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md#confirmed-findings`

## Expected Outputs
- Finding disposition matrix
- `control-plane-stabilization-design.v2.md` when required
- New council run with valid lineage when bytes change

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Latest immutable design has council verdict `pass` or `pass_with_notes`, or the remaining blocking decision is explicitly escalated to HUMAN; no earlier run is overwritten.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Changed bytes always require a new council run.
- Do not optimize for a preferred verdict.

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
- OUT-009-01-01 —  (draft)
- OUT-009-02-01 —  (draft)
- OUT-009-03-01 —  (draft)

## Capture Inbox References
- CAP-009-01 — retrieval gap: docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md (captured)
- CAP-009-02 — AIWS command examples assume unavailable python alias (captured)
- CAP-009-03 — Workflow null result lacks typed council retry evidence (captured)
- CAP-009-04 — Council plain subagents repeatedly violate strict reviewer schema (captured)
