---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260913-multi-mission-web-ui-STEP-10
task_id: TASK-20260913-multi-mission-web-ui
working_aip_ref: AIP-EXEC-004
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-004-multi-mission-web-ui.md
active_step_id: STEP-10
active_step_title: Recover the matrix and complete serialized conformance architecture
source_aip: AIP-EXEC-004
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-004-multi-mission-web-ui.md
step_id: STEP-10
step_index: 11
step_total: 12
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-15
---

# Active Step Context — Split conformance architecture and runner recovery

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Complete the approved revision-32 controlled standalone coding/test phase of the inactive Governed Agent Team Conservative MVP: preserve accepted governance, memory, policy, and wrapper bytes; freeze an independently reviewed static conformance contract matrix; implement and review the missing package-owned control state machines, closed handlers/probes/reducers, and executable runner assembly; run the exact Node-only integration/build/smoke gates; and freeze the implementation hash for a separately reviewed literal-path conformance WBS. Do not access or install into DSH, execute the accepted conformance baseline, or close this AIP in this phase.
- Final outcome (AIP Expected Outputs):
  - `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md` and `docs/conformance/gat-conservative-mvp-v1.json` with independent review and HUMAN acceptance evidence.
  - Independently accepted `conformance-contract-matrix.json`/`.md` plus its focused static test.
  - Zero-dependency `packages/gat` control source/declarations/tests, closed handlers/probes/reducers, executable runner assembly, exact Node test/build output, and built-package smoke.
  - `wbs-runs/multi-mission-web-ui/integration-standalone.md`, `implementation-freeze.json`, `conformance-handoff.md`, and `final-report-standalone-phase.md`.
  - Runtime evidence in the existing `.ai-work/workspaces/hoinv/TASK-20260913-multi-mission-web-ui`.
  - AIP status remains active at the conformance re-plan boundary.
- Scope:
  - Preserve prior mission history and settle the stale revision-11 work marker without regaining its charge.
  - Author the proposal-required threat model and every unique §18.1 vector; obtain independent Security review and exact HUMAN acceptance before code.
  - Preserve independently accepted governance, policy/selector, partitioned memory/audit/lifecycle/privacy, and wrapper-admission bytes.
  - Recover, verify, and independently review the interrupted 51-vector static contract matrix before new package-source work.
  - Implement and independently review internal-only package control state machines, closed conformance handlers/probes/reducers, and the executable runner assembly without executing the accepted baseline.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Recover Governance and Inspect Pre-applied Work  [upstream — done]
- STEP-02 — Complete and Review Web Mission Management  [upstream — done]
- STEP-03 — Run Canonical Installed-worktree Verification  [upstream — done]
- STEP-04 — Review, Accept, and Close  [upstream — done]
- STEP-05 — Reconcile revision 16 governance  [upstream — done]
- STEP-06 — Threat model and vector HUMAN gate  [upstream — done]
- STEP-07 — Zero-dependency package scaffold  [upstream — done]
- STEP-08 — Implement governance and partitioned memory  [upstream — done]
- STEP-09 — Implement policy and wrapper admission  [upstream — done]
- STEP-10 — Recover the matrix and complete serialized conformance architecture  ◀ ACTIVE (step 11 of 12)
- STEP-11 — Integrate, freeze, review, and hand off  [downstream]

## Downstream / Output Contract
- Next step (STEP-11 — Integrate, freeze, review, and hand off) needs as Inputs:
  - `packages/gat`
  - `wbs-runs/multi-mission-web-ui/integration-standalone.md`
  - `.ai-work/workspaces/hoinv/TASK-20260913-multi-mission-web-ui/08_capture_inbox.jsonl`
  - `.ai-work/workspaces/hoinv/TASK-20260913-multi-mission-web-ui/05_open_questions.md`
- Shape this step's output to satisfy the above + the AIP final outcome (see AIP Goal & Outcome).

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Threat/vector acceptance is a real HUMAN gate; WBS approval does not pre-accept those future artifacts.
  - Focused Node tests/build do not establish full §18 conformance or DSH compatibility.
  - The static matrix and each split implementation gate require independent acceptance before dependents become ready.
  - The complete runner must be frozen before the later WBS can name its literal implementation-hash evidence directory.
  - No external dependency, DSH access, network, accepted-baseline conformance execution, or AIP close is allowed.
- **Known Open Points:**
  - The literal conformance evidence path remains unknown until `implementation-freeze`; the accepted handoff must preserve it for the next reviewed WBS. Runtime discoveries belong in workspace `05_open_questions.md`.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `AGENTS.md`
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `wbs-runs/multi-mission-web-ui/wbs.v32.json`
- `wbs-runs/multi-mission-web-ui/execution.json`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Project multi-mission guidance | (none) | (no applicable source found) | Preflight returned only a weak unrelated sample candidate. | wiki:none |

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Execute the revision-32 serialized recovery gates: first recover, verify, and independently accept the interrupted static 51-vector contract matrix; then implement and accept missing internal-only package control state; then implement and accept closed handlers/probes/reducers; finally assemble and accept the executable runner using synthetic fixtures only.

## Recommended Mode
Executing

## Applicable Guidelines
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `wbs-runs/multi-mission-web-ui/wbs.v32.json`

## Recommended Skills
- ...

## Inputs
- `docs/conformance/gat-conservative-mvp-v1.json`
- `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md`
- `packages/gat/src/governance`
- `packages/gat/src/policy`
- `packages/gat/src/memory`
- `packages/gat/src/adapter`
- `wbs-runs/multi-mission-web-ui/runner-architecture-gap.md`

## Expected Outputs
- `wbs-runs/multi-mission-web-ui/conformance-contract-matrix.json`
- `wbs-runs/multi-mission-web-ui/conformance-contract-matrix.md`
- `packages/gat/tests/conformance-contract-matrix.test.mjs`
- `packages/gat/src/control`, aligned declarations, and `packages/gat/tests/control-state.test.mjs`
- Closed conformance handlers/probes/reducers/fixtures, aligned declarations, focused tests, and independent reviews.
- Final runner assembly source/declarations/tests and independent review.

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
`conformance-contract-matrix-recovery`, `control-state-reconciliation`, `conformance-handlers-reducers`, and `conformance-runner-assembly` are accepted in dependency order without executing or claiming the accepted full vector baseline.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Preserve accepted governance/policy/memory/wrapper bytes.
- Handlers never receive expected, required-absence, or required-evidence declarations; only the terminal comparator does.
- Preserve the caller-supplied literal evidence path; no accepted-baseline invocation.

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
- OUT-004-01-01 —  (draft)
- OUT-004-02-01 —  (draft)
- OUT-004-05-01 —  (draft)
- OUT-004-06-01 —  (draft)
- OUT-004-07-01 —  (draft)
- OUT-004-08-01 —  (draft)
- OUT-004-09-01 —  (draft)
- OUT-004-10-01 —  (draft)
