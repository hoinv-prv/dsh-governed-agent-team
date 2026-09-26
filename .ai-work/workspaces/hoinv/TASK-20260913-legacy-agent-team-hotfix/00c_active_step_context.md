---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260913-legacy-agent-team-hotfix-STEP-04
task_id: TASK-20260913-legacy-agent-team-hotfix
working_aip_ref: AIP-EXEC-011
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-011-legacy-agent-team-hotfix.md
active_step_id: STEP-04
active_step_title: Final Review, Acceptance, and Close
source_aip: AIP-EXEC-011
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-011-legacy-agent-team-hotfix.md
step_id: STEP-04
step_index: 5
step_total: 5
status: active
active_task_lens: 
staleness_status: stale
staleness_reason: AIP modified after ASC was built
updated_at: 2026-09-17
---

# Active Step Context — Final Review, Acceptance, and Close

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Hotfix the legacy `packages/core`, `packages/tools`, and `packages/web` plugin so a Lead-only Team can execute after plan approval and one Approve Plan action imports missing tasks from the latest HUMAN-approved DSH Chat Plan `## Tasks` section before approving the exact resulting Team plan revision.
- Final outcome (AIP Expected Outputs):
  - Hotfixed legacy source and focused tests in `packages/tools`, `packages/core`, and `packages/web`.
  - New mission evidence under `wbs-runs/legacy-agent-team-hotfix`.
  - Canonical installed-worktree verification report.
  - Independent task/final reviews and explicit HUMAN acceptance.
- Scope:
  - Default minimum durable teammates becomes zero; Lead-only operation is allowed.
  - Configurable maximum teammate cap and Team plan approval gate remain enforced.
  - Latest successful HUMAN-approved `exit_plan_mode` call/result pairing is read deterministically from the Lead Session log.
  - Only checklist/bullet/numbered items in a `## Tasks` section are imported.
  - Existing Team tasks are preserved; only normalized missing tasks are added.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Hotfix Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Allow Lead-only Team Execution  [upstream — done]
- STEP-02 — Import Chat Plan Tasks and Approve  [upstream — done]
- STEP-03 — Canonical Installed-worktree Verification  [upstream — done]
- STEP-04 — Final Review, Acceptance, and Close  ◀ ACTIVE (step 5 of 5)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Hotfixed legacy source and focused tests in `packages/tools`, `packages/core`, and `packages/web`.
  - New mission evidence under `wbs-runs/legacy-agent-team-hotfix`.
  - Canonical installed-worktree verification report.
  - Independent task/final reviews and explicit HUMAN acceptance.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - Another coordinator owns the distinct revision-32 `multi-mission-web-ui` mission and `packages/gat`; this AIP must never mutate its controls or package scope.
  - Session-event parsing must distinguish successful approval from rejection/incomplete calls.
  - Merge/dedupe and approval revision must be atomic or fail closed with preserved existing tasks.
  - Runtime/build proof is deferred to the canonical verifier.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/05_open_questions.md`
  - No unresolved product decision; exact source design remains subject to independent review.

## Read First
**References to Read First:**
- `AGENTS.md`
- `wbs-runs/legacy-agent-team-hotfix/wbs.v7.json`
- `packages/tools/src/index.ts`
- `packages/core/src/index.ts`
- `packages/core/src/task-board.ts`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Legacy GAT plan integration | (none) | `packages/core`, `packages/tools`, `packages/web` | Project wiki lookup and semantic retry found no relevant DSH plan/task contract. | wiki:none |

## Workspace Actions
- Final capture/open-point sweep and closure evidence.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
All requirements map to evidence, scoped lint is clean, HUMAN accepts exact final report, captures are explicitly triaged, and AIP is done.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Produce the final evidence report, run scoped AIWS lint, obtain independent review and explicit HUMAN acceptance, disposition capture candidates, and close the AIP.

## Recommended Mode
Reviewing

## Applicable Guidelines
- wiki:none
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

## Recommended Skills
- aiws-lint

## Inputs
- `wbs-runs/legacy-agent-team-hotfix/integration.md`
- `wbs-runs/legacy-agent-team-hotfix/execution.json`
- `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/04_findings.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/05_open_questions.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-legacy-agent-team-hotfix/08_capture_inbox.jsonl`
- `wbs-runs/legacy-agent-team-hotfix/evidence`

## Expected Outputs
- `wbs-runs/legacy-agent-team-hotfix/final-report.md`
- Independent final verdict
- HUMAN acceptance and closed AIP

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
All requirements map to evidence, scoped lint is clean, HUMAN accepts exact final report, captures are explicitly triaged, and AIP is done.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Waiting for HUMAN is not completion.

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
- OUT-011-01-01 —  (draft)
- OUT-011-02-01 —  (draft)
- OUT-011-03-01 —  (draft)

## Capture Inbox References
- CAP-TASK-20260913-legacy-agent-team-hotfix-001 — Approved DSH Chat Plan is markdown, not structured tasks (captured)
- CAP-TASK-20260913-legacy-agent-team-hotfix-002 — Fresh ASC may report stale immediately after run start (captured)
