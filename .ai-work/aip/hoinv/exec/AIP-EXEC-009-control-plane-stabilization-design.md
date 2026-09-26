---
artifact_type: aip_exec
artifact_id: AIP-EXEC-009
title: "Redesign WBS Control-Plane Admission and Council Review"
status: active
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "direct HUMAN request: redesign first and council-review before rebuilding WBS"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design
updated_at: 2026-09-15
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Redesign WBS Control-Plane Admission and Council Review

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — Universal Gates áp dụng:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — STEP-00.
- **Gate U2 Confirm-understanding-of-input (soft)** — Input Understanding và Workspace findings.
- **Gate U3 Open Points tracking (soft)** — Workspace `05_open_questions.md`.

## Objective
Thiết kế lại control plane cho mission `multi-mission-web-ui` để loại bỏ vòng lặp reconcile → charge → phát hiện control defect → pause/re-plan; review thiết kế bằng `dsh-council-review` trên exact pinned bytes; chỉ tạo decision-ready handoff cho WBS revision kế tiếp sau khi review closure đạt, không build hoặc execute WBS trong AIP này.

## Selected Task Lens / Mode
- Lens: `design_review`
- Reason: đây là task authoring architecture/control design kèm evidence-bound design/governance review.
- Search/execution effect: ưu tiên architecture responsibility, authority, lifecycle, failure/rollback paths, traceability và reproducible review evidence.
- Resolved references: GAT proposal; v32 WBS/review/progress/ledger/decisions/evidence; canonical AIWS architecture và runtime-review methodology; council-review contracts/routing.
- Deferred lookups: không có; GAT proposal path được cung cấp bởi mission hiện hữu nhưng chưa có matching Wiki Source.
- Expansion allowed: yes — chỉ trong declared inputs/read roots khi cần xác minh finding; không mở DSH checkout.

## Execution Scope
### In Scope
- Phân loại root cause thành systemic cause, contributing conditions và symptoms dựa trên evidence hiện có.
- Thiết kế một pre-charge admission protocol atomic, explicit state machine, artifact ownership, rollback/recovery, reviewer availability, continuation and budget-slack gates.
- Thiết kế migration strategy cho legacy execution ledger theo backup-first/lossless/strict-validation.
- Tạo traceability từ mỗi failure đã quan sát tới control, evidence và owner.
- Chạy high-risk council review với design + governance modes, independent internal lanes, required outside view và separate Chairman.
- Sửa thiết kế theo confirmed findings và chạy review mới theo lineage nếu bytes thay đổi.
- Tạo handoff decision-ready làm input cho một WBS-build task tương lai.

### Out of Scope
- Không build/revise/select/execute WBS.
- Không charge attempt, accept task, thay `execution.json`, `decisions.json`, mission AIP-004 hoặc product source.
- Không chạy accepted conformance baseline.
- Không access DSH checkout, network, package managers, install, activation, merge, deploy hoặc close proposal/AIP-004.
- Council chỉ advisory; không có quyền accept design hay project artifact.

## Expected Outputs
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v1.md`
- Một hoặc nhiều immutable council runs dưới `wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/`
- Nếu cần correction: `control-plane-stabilization-design.v2.md` và council run mới có lineage.
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-handoff.md`
- Workspace findings, open-point log, review checklist và final output.

## Execution Input Package
### Plan Source
- Direct HUMAN request: “Trước mắt hãy design lại, dùng council-review để review lại trước khi build lại wbs.”

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| AIWS architecture | `SRC-METHOD-methodology-10-design-architecture-design-mvp-md-994c` | `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md` | actor/component and Working-AIP boundary | — |
| Runtime review methodology | `SRC-METHOD-methodology-20-specs-runtime-review-methodology-mvp-md-cb16` | `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md` | pinned items/checks/verdicts and ensemble discipline | — |
| GAT Conservative MVP proposal | `(none)` | `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md` | reusable project architecture proposal, exact lookup miss | `[retrieval_gap]` |
| WBS v32 | `(one-off control artifact)` | `wbs-runs/multi-mission-web-ui/wbs.v32.json` | selected plan under analysis, not authorization to run | — |
| WBS v32 review | `(one-off control artifact)` | `wbs-runs/multi-mission-web-ui/review.v32.md` | prior validation/review claim | — |
| Execution ledger | `(one-off runtime control)` | `wbs-runs/multi-mission-web-ui/execution.json` | preserve bytes; read-only for this AIP | — |
| Decision ledger | `(one-off runtime control)` | `wbs-runs/multi-mission-web-ui/decisions.json` | authority evidence; read-only | — |
| Detailed progress/root-cause analysis | `(one-off report)` | `wbs-runs/multi-mission-web-ui/progress-analysis.v32.md` | hypothesis input to independently challenge | — |
| Attempt-66 verification | `(one-off evidence)` | `wbs-runs/multi-mission-web-ui/evidence/revision-32-reconciliation/attempt-revision-32-reconciliation-001/verification.md` | current reconciliation evidence | — |

### Reference lookup
- Exact wiki lookup was performed for GAT architecture, execution control, runtime review methodology and WBS validation.
- GAT proposal lookup was escalated to semantic mode but no matching project Wiki Source was returned; path comes from the existing mission input package.

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context points at STEP-00 before any design authoring.
- Current mission execution remains untouched and no active worker/job owns it.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Redesign first; council-review before any WBS rebuild | Current execution stays frozen | Exact stabilization budget belongs to later WBS decision | ⬜ pending STEP-00 |
| GAT proposal | HUMAN owns material decisions; AIP/Workspace are canonical task guardrails; proposal remains inactive | Design must not grant activation | None for current design scope | ⬜ pending STEP-00 |
| WBS/runtime records | Repeated control-plane drift, reviewer/capability failures and strict-ledger incompatibility are evidence inputs | Historical bytes stay immutable | Exact migration target schema must be council-checked | ⬜ pending STEP-00 |

## References to Read First
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md`
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `wbs-runs/multi-mission-web-ui/progress-analysis.v32.md`
- `wbs-runs/multi-mission-web-ui/wbs.v32.json`
- `wbs-runs/multi-mission-web-ui/execution.json`
- `/home/hoinv/.dsh/skills/dsh-council-review/SKILL.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/references/contracts.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/references/risk-and-routing.md`

## Current Risks / Constraints
- Prior reviews passed artifacts that later failed deterministic or semantic checks; review must pin closed must-check items and exact bytes.
- Legacy ledger strict-validation defect prevents trusting execution-backed progress projection.
- Current attempt allocation has no contingency slack; this design must make the trade-off explicit rather than silently fit work.
- A single reviewer/runtime failure must not be interpreted as artifact failure or acceptance.
- Global council skill paths are read-only procedural inputs; DSH checkout remains forbidden.

## Known Open Points
- Workspace log: `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/05_open_questions.md`.
- Whether later WBS raises the ceiling or reduces downstream maxima is intentionally a HUMAN decision after reviewed design.

## Workspace Execution Rule
All runtime understanding, findings, council telemetry, open points and draft state live in the Task Workspace. This AIP remains stable macro-control.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record and confirm that the deliverable is a systemic control-plane stabilization design, independently council-reviewed before any new WBS is built, with current mission execution frozen.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

Recommended Skills:
- `aiws-aip`

Inputs:
- Direct HUMAN request
- Objective, scope, outputs and constraints in this AIP

Expected Outputs:
- Workspace task-understanding note
- Explicit BrSE/HUMAN confirmation evidence

Done Condition:
HUMAN confirms design-before-WBS scope, current-execution freeze and council-review requirement.

Notes / Constraints:
- No design authoring or council model call before confirmation.

Workspace Actions:
- Record understanding and confirmation reference.

### Step: STEP-01 — Establish evidence-bound failure model
Objective:
Read declared evidence, separate root cause, contributing conditions and symptoms, and create closed traceability of every repeated failure to missing control and owner.

Recommended Mode:
Analyzing

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`

Recommended Skills:
- `aiws-aip`

Inputs:
- Required input package
- Prior progress/root-cause report

Expected Outputs:
- Workspace failure taxonomy and traceability matrix
- Explicit facts versus hypotheses

Done Condition:
Every material observed failure has evidence, effect, systemic/control classification and named owner; unsupported causal claims are marked hypothesis.

Notes / Constraints:
- Do not edit current mission controls.

Workspace Actions:
- Update `04_findings.md` and `05_open_questions.md`.

### Step: STEP-02 — Author control-plane stabilization design v1
Objective:
Define the smallest credible admission architecture that prevents charge-before-readiness and state drift across WBS, execution ledger, AIP/ASC, runtime goal, Team authority, command capability, reviewer availability and budget.

Recommended Mode:
Designing

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`

Recommended Skills:
- `aiws-aip`

Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md#failure-model`
- Required Truth and Wiki inputs declared in this AIP

Expected Outputs:
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v1.md`

Done Condition:
Design includes responsibility boundaries, admission state machine, ordered checks, invariant/evidence table, failure/rollback/recovery paths, ledger migration, reviewer fallback, goal/Team synchronization, budget policy and WBS-build handoff criteria.

Notes / Constraints:
- Design is advisory and inactive.
- No custom execution runner, DSH change or product implementation.

Workspace Actions:
- Keep intermediate design notes in `07_output_draft.md`.

### Step: STEP-03 — Run immutable high-risk council review
Objective:
Review exact design-v1 bytes using the canonical council process with design and governance rubrics and an outside-view challenge.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/SKILL.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/references/contracts.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/references/risk-and-routing.md`

Recommended Skills:
- `dsh-council-review`

Inputs:
- Exact design-v1 bytes
- Pinned architecture, governance and runtime-control Sources of Truth

Expected Outputs:
- New immutable council run under `wbs-runs/multi-mission-web-ui/council-reviews/control-plane-stabilization/`
- Valid request/manifests/dispatch/ledger/verifier/Chairman/report records

Done Condition:
Council closure verifies participant separation, exact hashes, required lanes, deterministic verification, conflicts and advisory verdict; reviewed design bytes remain unchanged.

Notes / Constraints:
- Risk and downstream impact are high.
- Minimum two distinct internal model families, required sanitized outside-view lane, reserved adjudicator/retries and separate Chairman.
- Council cannot accept the design.

Workspace Actions:
- Record review ID, report hash, verdict and findings in Workspace.

### Step: STEP-04 — Resolve findings and obtain reviewed design closure
Objective:
Disposition council findings; if material revision is required, author immutable design v2 and run a new full council review with lineage before handoff.

Recommended Mode:
Designing + Reviewing

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/20_specs/Runtime_Review_Methodology_MVP.md`
- `/home/hoinv/.dsh/skills/dsh-council-review/SKILL.md`

Recommended Skills:
- `dsh-council-review`

Inputs:
- `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md#council-review-v1`
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v1.md`
- `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md#confirmed-findings`

Expected Outputs:
- Finding disposition matrix
- `control-plane-stabilization-design.v2.md` when required
- New council run with valid lineage when bytes change

Done Condition:
Latest immutable design has council verdict `pass` or `pass_with_notes`, or the remaining blocking decision is explicitly escalated to HUMAN; no earlier run is overwritten.

Notes / Constraints:
- Changed bytes always require a new council run.
- Do not optimize for a preferred verdict.

Workspace Actions:
- Update findings/open questions and preserve run lineage.

### Step: STEP-05 — Produce decision-ready WBS-build handoff
Objective:
Translate the reviewed design into exact constraints and gates for a future `dsh-wbs-build` request without drafting the WBS.

Recommended Mode:
Synthesizing

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- Latest council report

Recommended Skills:
- `aiws-aip`

Inputs:
- Latest reviewed design and council report
- Finding dispositions

Expected Outputs:
- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-handoff.md`
- Workspace final output

Done Condition:
Handoff defines required WBS tasks/effects/commands/sources/reviews, pre-charge invariant, migration evidence, budget alternatives and exact HUMAN decisions still required; it contains no execution authority.

Notes / Constraints:
- WBS build is a separate subsequent task and HUMAN gate.

Workspace Actions:
- Write `11_output_final.md` and final capture-sweep result.

## Done Criteria
- [ ] Gate U1 confirmation evidence exists.
- [ ] Failure model separates facts, contributing conditions, symptoms and hypotheses.
- [ ] Stabilization design covers all identified control surfaces and negative paths.
- [ ] Council review is immutable, evidence-bound, high-risk routed and closed.
- [ ] Latest design has `pass`/`pass_with_notes` or an explicit HUMAN blocker decision.
- [ ] WBS-build handoff is decision-ready but no WBS was built or executed.
- [ ] Current mission controls and product bytes remain unchanged.
- [ ] Gate U3 open points are resolved/deferred/rejected.
- [ ] Final scoped lint reports zero errors.

## Self-check / Review Points
- Confirm council artifact hash before and after review is identical.
- Confirm reviewers, outside-view, adjudicator when triggered and Chairman have separated invocations.
- Confirm every admission check has an owner, exact evidence, failure state and retry/rollback rule.
- Confirm no attempt charge or task acceptance occurred.
- Confirm ledger migration never rewrites history without exact backup and strict closure.
- Confirm no single reviewer success/failure is treated as project acceptance.

## Finalization Notes
- Do not close AIP until council closure, handoff, capture sweep, attribution check and scoped lint pass.

## Pre-flight Pending Captures
- [IMPORTED 2026-09-15] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md" lookup_query="GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL" reason="Reusable project architecture proposal is a structural input but exact and semantic wiki lookup returned no matching source."

## Re-plan Rule
Nếu macro scope hoặc expected output thay đổi, append dated Re-plan Log entry trước khi edit; sweep toàn bộ AIP cho marker cũ và phân loại mọi residual.

## Re-plan Log
- (no re-plan yet)
