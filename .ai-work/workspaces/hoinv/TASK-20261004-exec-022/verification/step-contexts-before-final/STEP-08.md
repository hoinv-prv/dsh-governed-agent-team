---
artifact_type: active_step_context
artifact_id: ASC-TASK-20261004-exec-022-STEP-08
task_id: TASK-20261004-exec-022
working_aip_ref: AIP-EXEC-022
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-022-implement-durable-agent-binding.md
active_step_id: STEP-08
active_step_title: Independent review, official design reconciliation and handoff (S5)
source_aip: AIP-EXEC-022
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-022-implement-durable-agent-binding.md
step_id: STEP-08
step_index: 9
step_total: 9
status: active
active_task_lens: No-Lens.
staleness_status: fresh
staleness_reason:
updated_at: 2026-10-04
---

# Active Step Context — Independent review, official design reconciliation and handoff (S5)

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Implement required GAT member attachments and a scoped Durable Agent context/memory adapter from `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, after approval of its implementation baseline. Bind before initial model admission, recover from immutable persisted attachment records before later work, keep Team authority in GAT, and keep persistent capability data in Durable Agent. Deliver traceable design, source, lifecycle/conformance evidence and supported package composition without claiming production eligibility before every prerequisite is qualified.
- Final outcome (AIP Expected Outputs):
  - Intended and final design coverage in `docs/gat-design/ARCHITECTURE_DESIGN.md`, `BASIC_DESIGN.md`, `DETAIL_DESIGN.md`, `DURABLE_AGENT_INTEGRATION.md` and source maps/baselines; update AD-04/06/08/09/12, BD-01/02/09/10/12–14 and DD-01–03/07–11/15–17 as affected. Preserve Target status for undelivered work.
  - Generic GAT implementation and tests in `packages/core/`, default initializer/callers and scoped policy regression coverage in `packages/tools/`, safe view consumers in `packages/web/` as needed.
  - Proposed `packages/durable-agent/` integration package and its tests, subject to P-01 approval; opt-in integration profile and package manifests/mappings in the locations approved at STEP-01.
  - Supported distribution updates under `installer/`, `scripts/` and compatibility artifacts, generated using repository tooling.
  - Runtime evidence under the workspace linked by `aiws-aip run start`: `baseline.md`, `approved-decisions.md`, `design-source-test-matrix.md`, `dependency-qualification.md`, `acceptance-matrix.md`, `verification/`, `independent-review.md` and `implementation-handoff.md`, plus normal findings/open-questions/capture files.
  - Evidence distinguishes source bytes, exported built artifacts and any separately authorized loaded runtime; no historical test result is presented as a new test run.
- Scope:
  - S0: baseline and dirty-file evidence across GAT, DA and selected DSH; approval of P-01–P-08, API family, execution model and intended design deltas.
  - S1: normalized initializer migration; bounded opaque attachments/JCS digests; binder registry; member-only event v3/v2 replay; lifecycle, recovery, deadlines and safe views against deterministic host fakes.
  - S2: qualify the DSH reserved handle, persist-only initial inbox, activation/recovery gate, legacy wrapper, per-request refresh and owner-scoped assembly shutdown surfaces.
  - S3: the selected Durable integration package, strict explicit declaration, exclusive ownership, executable read/candidate handlers, bounded refresh and cleanup; real public-provider integration in temporary storage.
  - S4: consume approved exact mission leases, canonical task association and nested capability enforcement; deliver opt-in profile/package mappings, SDK safe summaries, build/export/installer compatibility and supported workflow evidence.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm implementation scope and prerequisite decisions (HARD GATE)  [upstream — done]
- STEP-01 — Record current baselines and update intended official design (S0)  [upstream — done]
- STEP-02 — Implement normalized initialization, attachments and member v3 (S1)  [upstream — done]
- STEP-03 — Implement core binding, recovery and bounded teardown against fakes (S1)  [upstream — done]
- STEP-04 — Qualify selected host and Durable package dependencies (S2, HARD GATE)  [upstream — done]
- STEP-05 — Implement strict Durable declaration, binder and ownership (S3)  [upstream — done]
- STEP-06 — Implement scoped tools, request refresh and qualified closing behavior (S3)  [upstream — done]
- STEP-07 — Integrate approved authorization, opt-in composition and distribution (S4, HARD GATE)  [upstream — done]
- STEP-08 — Independent review, official design reconciliation and handoff (S5)  ◀ ACTIVE (step 9 of 9)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Intended and final design coverage in `docs/gat-design/ARCHITECTURE_DESIGN.md`, `BASIC_DESIGN.md`, `DETAIL_DESIGN.md`, `DURABLE_AGENT_INTEGRATION.md` and source maps/baselines; update AD-04/06/08/09/12, BD-01/02/09/10/12–14 and DD-01–03/07–11/15–17 as affected. Preserve Target status for undelivered work.
  - Generic GAT implementation and tests in `packages/core/`, default initializer/callers and scoped policy regression coverage in `packages/tools/`, safe view consumers in `packages/web/` as needed.
  - Proposed `packages/durable-agent/` integration package and its tests, subject to P-01 approval; opt-in integration profile and package manifests/mappings in the locations approved at STEP-01.
  - Supported distribution updates under `installer/`, `scripts/` and compatibility artifacts, generated using repository tooling.
  - Runtime evidence under the workspace linked by `aiws-aip run start`: `baseline.md`, `approved-decisions.md`, `design-source-test-matrix.md`, `dependency-qualification.md`, `acceptance-matrix.md`, `verification/`, `independent-review.md` and `implementation-handoff.md`, plus normal findings/open-questions/capture files.
  - Evidence distinguishes source bytes, exported built artifacts and any separately authorized loaded runtime; no historical test result is presented as a new test run.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Implementation approval is not recorded by creating this draft. Proposed API and lifecycle selections cannot be silently inferred from similarly named services.
  - Foundation work is permitted only after execution/design approval; production wiring requires qualified S1+S2, and production dispatch requires S4.
  - Preserve existing modified `packages/core/src/{projection,roster,types}.ts`, `packages/core/tests/{persistence,team}.spec.ts` and `packages/web/tests/team-action.client.spec.tsx`; recheck actual dirty bytes. Do not reset, duplicate or claim ownership of earlier patches.
  - Existing static `team:policy` label capture must survive; qualify it through regression checks instead of introducing a second fix or weakening live guards.
  - Ownership is one live GAT owner per canonical workspace/name, with a dedicated provider and one host process per storage workspace. A process map is not a cross-host lock proof. Slow cleanup retains identity quarantine.
- **Known Open Points:**
  - OP-01: HUMAN execution scope and approval/revision of P-01–P-08. Candidate default is the proposal's WK-style separate adapter; it remains unselected until confirmed.
  - OP-02: exact DSH checkout/API family and direct-continuable versus isolated execution target. Official Consumer requires reviewed API mapping; isolated execution requires approved stable-member/execution/resource ownership mapping.
  - OP-03: DSH reserved-handle, request-refresh and assembly-removal capability owner, implementation revision and qualification evidence.
  - OP-04: dedicated DA provider registration key, pinned package/API/features, one-host workspace exclusivity and deployment owner.
  - OP-05: approved mission/task authority and executor/nested capability workstream with concrete evidence; consuming that work does not approve rewriting it here.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
1. `AGENTS.md`, GAT design-first rule, and `.ai-work/AIWS.local.md`, Execution policy.
2. Required Truth inputs and the AIP template `.ai-work/aip/templates/AIP_EXEC_TEMPLATE.md`.
3. Formal architecture §§4–7, basic design BD-12–14/§§5–8, detail design DD-01–03/07–11/15–17 and source map.
4. Frozen contract §§3–14 and Durable integration public contract/verification limits.
5. Proposal §§2.2–12 and selected original public DA interfaces; use proposal §1 links only after lookup and applicability checks.
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Use | Capture flag |
|---|---|---|---|---|
| Proposal | (unregistered) | `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md` | Full §§1–13; S0–S5 and T01–T23 | [retrieval_gap] |

## Workspace Actions
- Resolve/defer captures through the HUMAN-controlled workflow, retain test exits/warnings, record approval and deployment status; only close after Done Criteria are satisfied.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
Independent substantive review has no unresolved implementation blocker, all applicable acceptance checks and production prerequisites pass, and official design reflects delivered source. Conditional exclusions carry approved target/evidence; pending dependencies are reported without closing this full-delivery AIP.

## Active Task Lens
- No-Lens.
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Review final implementation against existing/approved design, freeze and all applicable T01–T23. Reconcile official design/source maps and exact source/build evidence, fix in-scope findings with design before code, and produce final supported-deployment handoff.

## Recommended Mode
Reviewing

## Applicable Guidelines
- `AGENTS.md`, Evidence before finalize
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`, closing and capture sweep
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§10–12

## Recommended Skills
- aiws-aip run
- aiws-lint task

## Inputs
- Official design, final source, decision/dependency records, acceptance matrix and raw test/build reports

## Expected Outputs
- `independent-review.md`, complete `acceptance-matrix.md`, synchronized official design/mappings/baselines and `implementation-handoff.md`
- Scoped strict lint, applicable whole-tree lint and design-verification reports

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
Independent substantive review has no unresolved implementation blocker, all applicable acceptance checks and production prerequisites pass, and official design reflects delivered source. Conditional exclusions carry approved target/evidence; pending dependencies are reported without closing this full-delivery AIP.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Luna can check ID/link/mapping completeness and summarize recorded checks; substantive lifecycle/authority review requires an appropriately capable independent reviewer. If WBS was separately adopted, apply approved run deltas to official design and report the mapping before close. No silent wiki/canonical promotion or lint suppression.

## Operating Memory (L2 — bài học vận hành)
- Lát cắt: mọi nhóm (step không khai Kind)
- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical (`.ai-work/procedural/operating_memory.md`).
- (Operating Memory trống — chưa có mục nào)

## Coverage
**Coverage Gaps:**
- Step Output / Decision Persistence Requirements (trimmed → spec §7.2)
- Source Verification Requirements (trimmed → spec §5)
- No expected outputs declared (inherited from AIP)

## Runtime Queue Blockers
- RQ-022-03 — Supported-profile browser golden mismatch needs owner alignment (blocked)
- RQ-022-04 — Production binder composition and changed-host compatibility/profile/package qualification remain pending (pending)
- RQ-022-05 — Broader type-aware lint findings need disposition before final production qualification (pending)

## Relevant Queue Item IDs
- RQ-022-01 — STEP-04: DSH reserved-child and request-refresh qualification missing; upstream pointer labels do not mean this gate passed (resolved)
- RQ-022-02 — STEP-07: Exact mission/task leases and nested capability enforcement are unqualified (resolved)
- RQ-022-03 — Supported-profile browser golden mismatch needs owner alignment (blocked)
- RQ-022-04 — Production binder composition and changed-host compatibility/profile/package qualification remain pending (pending)
- RQ-022-05 — Broader type-aware lint findings need disposition before final production qualification (pending)

## Previous Step Results / Handoff Inputs
- OUT-022-00-01 — HUMAN approved P01–08 and WK/direct-continuable target. Exact replies recorded; no external source edit or live activation grant. (approved_for_next_step)
- OUT-022-01-01 — Formal intended delta preceded source; prior dirty edits preserved. (reviewed)
- OUT-022-02-01 — Bounded attachments, strict v2/v3 replay, core initializer and safe summaries; source tests pass. (reviewed)
- OUT-022-03-01 — Deterministic lifecycle ports reviewed and tested; actual host integration not qualified. (reviewed)
- OUT-022-04-01 — Host lifecycle/refresh and exact authority/nested capability prerequisites qualified in AIP-EXEC-023. Parent production binder, changed-host compatibility/profile/package checks and browser finding remain open. (needs_revision)
- OUT-022-05-01 — WK adapter tested over public service ports and temporary real provider; production integration gate remains open. (reviewed)
- OUT-022-06-01 — Executable handlers/refresh and strict direct-path revocation pass ports tests. Isolated-only cases not applicable; actual host dispatch qualification pending. (reviewed)
- OUT-022-07-01 — Host lifecycle/refresh and exact authority/nested capability prerequisites qualified in AIP-EXEC-023. Parent production binder, changed-host compatibility/profile/package checks and browser finding remain open. (needs_revision)
- OUT-022-08-01 — Independent source review pass and design reconciliation available; full delivery acceptance and finalize blocked by production prerequisites. (draft)
- OUT-022-04-02 — Qualified prerequisite handoff: reserved recovery, pre-render refresh, exact authority and nested capabilities PASS (reviewed)

## Capture Inbox References
- CAP-022-01 — retrieval gap: docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md (captured)
- CAP-022-02 — retrieval gap: .ai-work/aip/templates/AIP_EXEC_TEMPLATE.md (captured)
- CAP-022-03 — AIP start builds stale Active Step Context before metadata and capture import settle (captured)
- CAP-022-04 — ASC ordinal upstream labels do not reflect blocked prerequisite gates (captured)
- CAP-022-05 — Review wiki refresh for implemented member-binding foundation and WK adapter (captured)
- CAP-022-06 — GAT panel replay golden expects obsolete default model labels (captured)
- CAP-022-07 — Type-aware lint must preserve optional JSON serialization outcomes (captured)
- CAP-022-08 — Prerequisite worktrees require additive compatibility selection (captured)
- CAP-022-09 — Authorization must be rechecked inside serialized acknowledgement transactions (captured)
