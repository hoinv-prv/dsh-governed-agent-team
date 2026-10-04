---
artifact_type: active_step_context
artifact_id: ASC-TASK-20261004-exec-024-STEP-07
task_id: TASK-20261004-exec-024
working_aip_ref: AIP-EXEC-024
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-024-implement-durable-binding-reuse.md
active_step_id: STEP-07
active_step_title: Finalize technical handoff and deployment proposal
source_aip: AIP-EXEC-024
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-024-implement-durable-binding-reuse.md
step_id: STEP-07
step_index: 8
step_total: 8
status: active
active_task_lens: No-Lens.
staleness_status: fresh
staleness_reason: 
updated_at: 2026-10-04
---

# Active Step Context — Finalize technical handoff and deployment proposal

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Deliver `@vuhoi/gat-durable-agent/execution-composition` as an additive opt-in binding for fresh isolated current GAT task executions. Reuse public WK service/Consumer and current GAT assignment/admission/settlement. Bind before first request, enforce exact asynchronous execution authority, and expose task/intent-authorized selective memory reads through tool results only. Never insert memory body, catalog, provider guidance or provenance into system prompt; ordinary binding/model requests do not retrieve memory context. Retain explicit evidence-only reviewer task inputs, joined cleanup and authorized live recovery. Preserve the existing direct-continuable entry and synchronize official GAT design/source.
- Final outcome (AIP Expected Outputs):
  - `docs/gat-design/DETAIL_DESIGN.md`, `BASIC_DESIGN.md`, `DURABLE_AGENT_INTEGRATION.md` and `SOURCE_CODE_MAP.md`: attributed prospective and finalized design/source amendments.
  - `packages/durable-agent/src/execution-composition.ts` and bounded implementation helpers where necessary; additive package export/build metadata and package documentation.
  - `packages/durable-agent/tests/`: focused execution-composition, selected-read/reviewer and lifecycle/recovery tests; existing entry regression evidence.
  - GAT-owned package/snapshot/distribution amendments at the exact qualification Host destinations settled during preflight; no broad Host patchset.
  - Workspace `qualification-design.md`, `qualification-environment.json`, `qualification-matrix.md`, `qualification-review.md`, `design-review.md`, `source-review.md`, `test-matrix.md`, `source-design-consistency.md`, `implementation-handoff.md` and `verification/` receipts.
  - Workspace `deployment-proposal.md`: exact proposed provider/profile/configuration, storage effects, topology evidence and rollback; no activation performed.
- Scope:
  - Qualification of current GAT isolated execution identity, first-request ordering, task-selected retrieval/no-system-memory/logging, reviewer packet input, selected reads, cleanup and cold recovery with the real WK service/provider.
  - A proposed qualification amendment followed by the reviewed production amendment in `docs/gat-design/` before dependent code changes.
  - Additive source, Config, tests, public export and build entry in `packages/durable-agent/`; reuse ownership/tool components where compatible and actually shared.
  - Necessary GAT-owned package mapping, dependency/export/build and package documentation changes for the new entry in an isolated selected qualification Host.
  - Focused UT/IT, keyless Session-driven snapshot, existing composition regressions and built public-import/Loader evidence; exact design/source and qualification manifests.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm execution scope and recover planning decisions  [upstream — done]
- STEP-01 — Define qualification design and exact environment  [upstream — done]
- STEP-02 — Qualify the real isolated-execution path  [upstream — done]
- STEP-03 — Review qualification and settle production design  [upstream — done]
- STEP-04 — Implement the additive execution composition  [upstream — done]
- STEP-05 — Run focused behavior and artifact verification  [upstream — done]
- STEP-06 — Obtain independent implementation review and synchronize design  [upstream — done]
- STEP-07 — Finalize technical handoff and deployment proposal  ◀ ACTIVE (step 8 of 8)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - `docs/gat-design/DETAIL_DESIGN.md`, `BASIC_DESIGN.md`, `DURABLE_AGENT_INTEGRATION.md` and `SOURCE_CODE_MAP.md`: attributed prospective and finalized design/source amendments.
  - `packages/durable-agent/src/execution-composition.ts` and bounded implementation helpers where necessary; additive package export/build metadata and package documentation.
  - `packages/durable-agent/tests/`: focused execution-composition, selected-read/reviewer and lifecycle/recovery tests; existing entry regression evidence.
  - GAT-owned package/snapshot/distribution amendments at the exact qualification Host destinations settled during preflight; no broad Host patchset.
  - Workspace `qualification-design.md`, `qualification-environment.json`, `qualification-matrix.md`, `qualification-review.md`, `design-review.md`, `source-review.md`, `test-matrix.md`, `source-design-consistency.md`, `implementation-handoff.md` and `verification/` receipts.
  - Workspace `deployment-proposal.md`: exact proposed provider/profile/configuration, storage effects, topology evidence and rollback; no activation performed.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - No missing public operation, new persistence field or weaker reviewer isolation may be hidden as an implementation detail; stop the affected branch and present the smallest demonstrated extension.
  - Existing adapter helpers may depend on the reserved-member Host or candidate feature; reuse only compatible ownership/validation, not the whole binder lifecycle.
  - Complete serialized and rendered task tool results need explicit UTF-8 byte bounds; retrieved content cannot grant task authority. Path-free structural DTOs do not guarantee arbitrary strings contain no private information.
  - Same-member overlapping owners fail closed despite provider ref deduplication. Compare underlying registered provider identity, reserve canonical workspace/name and keep ownership quarantined until physical cleanup settles.
  - `reviewContribution` performs an authorization snapshot read but must not render its member guidance/catalog/body. Freshness and other prompt/tool owners are Host responsibilities.
- **Known Open Points:**
  - OP-024-01: reviewer mode and exact ReviewPacket derivation from approved assignment/candidate inputs; no invented receipts, criterion IDs or generic fallback.
  - OP-024-02: selected Host/package/public export compatibility, test Loader/snapshot launcher and actual command/build write scope.
  - OP-024-03: task/intent retrieval, no memory contribution to system prompt, per-attempt authority checks and logged tool results.
  - OP-024-04: cleanup participation in terminal settlement, delayed calls/release failures/deadlines and submission self-drain avoidance.
  - OP-024-05: live cold recovery identity/config/profile validation before model/inbox release; terminal denial.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `wbs-runs/durable-binding-reuse/proposal-review.md`; `implementation-plan.md`; `source-baseline.json`.
- `docs/gat-design/BASIC_DESIGN.md` §7 and production binding sections; `DETAIL_DESIGN.md` DD-09/DD-15/DD-16 and §§5/7/8/9; `DURABLE_AGENT_INTEGRATION.md`; `SOURCE_CODE_MAP.md`.
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§2–4/8/12.
- `/home/hoinv/work/dsh-durable-agent/docs/DURABLE_AGENT_DESIGN_INDEX.md` §§1–3 and `DURABLE_AGENT_DESIGN_MISSION_DELTAS.md` §§3–5.
- `/home/hoinv/work/dsh-durable-agent/docs/DURABLE_AGENT_ARCHITECTURE_DESIGN.md` AD-02–05; `DURABLE_AGENT_BASIC_DESIGN.md` BD-01–05; `DURABLE_AGENT_DETAIL_DESIGN.md` DD-01–04/DD-06–09/DD-11–12.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
| --- | --- | --- | --- | --- |
| GAT Basic Design | SRC-GAT-BASIC-DESIGN | `docs/gat-design/BASIC_DESIGN.md` | External capability flow and existing production delivery | — |

## Workspace Actions
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Technical deliverables, independent review and required checks are complete; all required official design changes are applied; capture disposition is HUMAN-controlled; actual lint results and limitations are reported; deployment proposal remains unactivated.

## Active Task Lens
- No-Lens.
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Complete evidence-bound implementation handoff, scoped lint and final capture disposition; prepare exact deployment configuration/storage/rollback proposal without activation.

## Recommended Mode
Executing

## Difficulty / Kind
Difficulty: medium   Kind: organize

## Applicable Guidelines
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

## Recommended Skills
- aiws-aip
- aiws-lint

## Inputs
Workspace qualification-review.md, design-review.md, source-review.md, test-matrix.md, source-design-consistency.md, qualification-environment.json and verification receipts; docs/gat-design official amended set; packages/durable-agent final package artifacts; this AIP Done Criteria

## Expected Outputs
Workspace implementation-handoff.md, deployment-proposal.md and 11_output_final.md; final lint/consistency/package manifest receipts; capture disposition and governed AIP closure

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Technical deliverables, independent review and required checks are complete; all required official design changes are applied; capture disposition is HUMAN-controlled; actual lint results and limitations are reported; deployment proposal remains unactivated.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| lint/consistency/package | no | ? | create |

## Notes / Constraints
Use aiws-lint task scoped to the runtime workspace and AIP; report whole-tree results when escalation applies. Never auto-fix Wiki/Truth or tick AIP Done Criteria. Do not claim live GUI/deployment acceptance, assign Mission Board task10, or hide a qualification blocker as a partial completion.

## Operating Memory (L2 — bài học vận hành)
- Lát cắt: Kind=organize → nhóm required_order, tool_gotcha, verification_trap (mục ngoài lát cắt được đánh dấu *bù* — DP-127-C)
- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical (`.ai-work/procedural/operating_memory.md`).
- (Operating Memory trống — chưa có mục nào)

## Coverage
**Coverage Gaps:**
- Step Output / Decision Persistence Requirements (trimmed → spec §7.2)
- Source Verification Requirements (trimmed → spec §5)

## Previous Step Results / Handoff Inputs
- OUT-024-00-01 —  (approved_for_next_step)
- OUT-024-01-01 —  (approved_for_next_step)
- OUT-024-02-01 —  (approved_for_next_step)
- OUT-024-03-01 —  (approved_for_next_step)
- OUT-024-04-01 —  (approved_for_next_step)
- OUT-024-05-01 —  (approved_for_next_step)
- OUT-024-06-01 —  (approved_for_next_step)

## Capture Inbox References
- CAP-024-01 — retrieval gap: .ai-work/aip/templates/AIP_EXEC_TEMPLATE.md (captured)
- CAP-024-02 — retrieval gap: /home/hoinv/work/dsh-durable-agent/docs/ (captured)
- CAP-024-03 — Attribute isolated-execution qualification independently of prior Host (captured)
- CAP-024-04 — pnpm exec attempts dependency auto-install in linked qualification trees (captured)
- CAP-024-05 — Current isolated Host retries retain prior WK prompt revision (captured)
- CAP-024-06 — Task intent selects memory tools; no memory system prompt in isolated adapter (captured)
- CAP-024-07 — Generic GAT brief cannot authenticate a DA reviewer packet (captured)
- CAP-024-08 — Provider-return guards do not cover later tool/model publication awaits (captured)
- CAP-024-09 — Await Loader fibers and provide optional services before set (captured)
- CAP-024-10 — Schemastery is a callable schema with its own API (captured)
