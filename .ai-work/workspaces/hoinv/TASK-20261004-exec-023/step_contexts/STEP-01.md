---
artifact_type: active_step_context
artifact_id: ASC-TASK-20261004-exec-023-STEP-01
task_id: TASK-20261004-exec-023
working_aip_ref: AIP-EXEC-023
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-023-implement-binding-prerequisites.md
active_step_id: STEP-01
active_step_title: Resolve host contracts and write intended design
source_aip: AIP-EXEC-023
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-023-implement-binding-prerequisites.md
step_id: STEP-01
step_index: 2
step_total: 8
status: active
active_task_lens: No-Lens.
staleness_status: fresh
staleness_reason: 
updated_at: 2026-10-04
---

# Active Step Context — Resolve host contracts and write intended design

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Deliver qualified prerequisite source and exported APIs for AIP-EXEC-022: controlled reserved direct-continuable child staging/persistence/activation/recovery; awaited current context refresh before every request's prompt rendering; host-attested HUMAN mission/member approval and exact scoped canonical-task execution leases; immutable capability classification checked at each direct, aliased and nested tool dispatch. Keep existing unrelated DSH/GAT behavior compatible, prove denials before effects, and hand off exact design/source/build evidence for binding integration without deployment.
- Final outcome (AIP Expected Outputs):
  - docs/gat-design/DETAIL_DESIGN.md — intended/current prerequisite design with exact ownership, admission, persistence and failure semantics; affected architecture/basic/integration/maps updated.
  - /home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md — extension point and loop ordering documentation plus owning subsystem/package docs, bilingual pairs and Agent Note.
  - /home/hoinv/work/dsh-binding-prerequisites/packages/ — host implementations and focused regression/conformance tests, exported built-path evidence and affected consumers.
  - packages/core/ — exact mission/task lease source/tests and host integration fixtures.
  - packages/tools/ — capability policy integration/tests and safe summaries as affected.
  - .ai-work/workspaces/hoinv/TASK-20261004-exec-023/ — baseline.md/json, authorization.md, design-delta.md, source-design-test-matrix.md, conformance.md, verification/, independent-review.md and prerequisite-handoff.md.
- Scope:
  - docs/gat-design/ — intended prerequisite delta before source, final qualification and mappings.
  - packages/core/ — exact mission/task authority, host attestation/lease ownership and required bridge to host APIs.
  - packages/tools/ — immutable GAT capability policy and effect/model admission checks; preserve static labels and existing dirty patches.
  - /home/hoinv/work/dsh-binding-prerequisites/ — approved isolated host source, docs, tests, generated API/SDK evidence, package consumers and necessary adjacent event adapters.
  - .ai-work/workspaces/hoinv/TASK-20261004-exec-023/ — baseline, decisions, per-step ASC snapshots, traces, tests, captures and handoff.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Record approved scope and protected baselines (HARD GATE)  [upstream — done]
- STEP-01 — Resolve host contracts and write intended design  ◀ ACTIVE (step 2 of 8)
- STEP-02 — Implement reserved admission and cold recovery  [downstream]
- STEP-03 — Implement refresh before request rendering  [downstream]
- STEP-04 — Implement exact HUMAN mission/task execution authority  [downstream]
- STEP-05 — Implement immutable nested capability enforcement  [downstream]
- STEP-06 — Qualify exported integration and independent review  [downstream]
- STEP-07 — Finalize prerequisite handoff and parent qualification inputs  [downstream]

## Downstream / Output Contract
- Next step (STEP-02 — Implement reserved admission and cold recovery) needs as Inputs:
  - design-delta.md and source-design-test-matrix.md
- Shape this step's output to satisfy the above + the AIP final outcome (see AIP Goal & Outcome).

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Baseline DSH APIs merge materialization and initial submission; recovery must not accidentally release work through legacy consumers.
  - Authority is owned in GAT and attested by trusted host APIs; a string/token supplied by a model cannot become HUMAN provenance.
  - Registrations and nested dispatch must retain immutable owner classification through wrappers and asynchronous context; check at the operation that makes the effect.
  - Reserved-child and prompt refresh share agent-loop code; assign disjoint file regions or serialize edits.
  - Existing GAT dirty source/design/tests belong to prior work; only additive scoped changes with preserved baseline hashes.
- **Known Open Points:**
  - Live log: .ai-work/workspaces/hoinv/TASK-20261004-exec-023/05_open_questions.md.
  - OP-01: inspect exact persistence/agent generation operations and declare new event/version semantics before source.
  - OP-02: qualify actual trusted HUMAN ingress and canonical task/plan revision inputs; no implicit list-order selection.
  - OP-03: supported packaging of the new DSH revision is a later qualification, not current baseline eligibility.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- AGENTS.md and .ai-work/AIWS.local.md.
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md and docs/gat-design/DETAIL_DESIGN.md.
- .ai-work/aip/hoinv/exec/AIP-EXEC-022-implement-durable-agent-binding.md.
- .ai-work/workspaces/hoinv/TASK-20261004-exec-022/dependency-qualification.md and implementation-handoff.md.
- /home/hoinv/work/dsh-binding-prerequisites/AGENTS.md, packages/AGENTS.md and docs/AGENTS.md.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Use | Capture flag |
|---|---|---|---|---|
| Frozen contract | SRC-GAT-MEMBER-BINDING-FREEZE | docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md | §§7–14 ordering, authority, capabilities, conformance | — |

## Workspace Actions
- Record design locators and delegation ownership before coding.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

## Active Task Lens
- No-Lens.
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Inspect affected host/core/tools consumers and update formal intended design and owning DSH design before any source change.

## Recommended Mode
Design-authoring

## Applicable Guidelines
- AGENTS.md
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
- /home/hoinv/work/dsh-binding-prerequisites/docs/AGENTS.md

## Recommended Skills
- ...

## Inputs
- baseline.md, authorization.md and resolved specification inputs

## Expected Outputs
- design-delta.md and source-design-test-matrix.md in workspace; intended formal GAT/DSH design

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Exact APIs, admission/recovery events, refresh ordering, authority and capability semantics are consistent with freeze; source file ownership declared.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Conflicting decisions stop only affected work. No source-before-design; no canonical promotion.
allow_raw_search: true

## Operating Memory (L2 — bài học vận hành)
- Lát cắt: mọi nhóm (step không khai Kind)
- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical (`.ai-work/procedural/operating_memory.md`).
- (Operating Memory trống — chưa có mục nào)

## Coverage
**Coverage Gaps:**
- Step Output / Decision Persistence Requirements (trimmed → spec §7.2)
- Source Verification Requirements (trimmed → spec §5)
- No expected outputs declared (inherited from AIP)

## Raw Search Authorization
- This step GRANTS raw (un-registered) search (`allow_raw_search: true`). When a registered lookup misses, you MAY run `lookup_wiki_source.py --authorized aip --include-raw on-empty --lookup-mode object`. Raw hits are un-registered — open directly and register via /aiws-wiki build-meta if reused. (CR-AIWS-2026-06-052)

## Capture Inbox References
- CAP-023-01 — retrieval gap: docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md (captured)
- CAP-023-02 — retrieval gap: /home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md (captured)
- CAP-023-03 — retrieval gap: .ai-work/aip/templates/AIP_EXEC_TEMPLATE.md (captured)
