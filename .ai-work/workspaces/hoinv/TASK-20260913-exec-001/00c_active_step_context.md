---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260913-exec-001-STEP-03
task_id: TASK-20260913-exec-001
working_aip_ref: AIP-EXEC-001
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-001-copy-gat-source.md
active_step_id: STEP-03
active_step_title: Verify copy integrity and repository scope
source_aip: AIP-EXEC-001
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-001-copy-gat-source.md
step_id: STEP-03
step_index: 4
step_total: 4
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-13
---

# Active Step Context — Verify copy integrity and repository scope

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Create a provenance-preserving source snapshot of the five accepted Governed Agent Team packages in the standalone repository, copied only from the immutable golden-reference worktree at exact HEAD `12fef7a7e01f6c3ba7ecab0929355659b3370435`.
- Final outcome (AIP Expected Outputs):
  - `packages/core/`
  - `packages/tools/`
  - `packages/web/`
  - `packages/profile/`
  - `packages/web-profile/`
  - `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
  - `docs/source-extraction.md`
  - `SOURCE_SNAPSHOT.json`
- Scope:
  - Copy tracked files from these golden-reference packages:
    - `packages/experimental/agent-team` → `packages/core`
    - `packages/experimental/tool-agent-team` → `packages/tools`
    - `packages/experimental/client-ui-agent-team` → `packages/web`
    - `packages/experimental/agent-team-profile` → `packages/profile`
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Inventory and copy tracked GAT files  [upstream — done]
- STEP-02 — Materialize provenance records  [upstream — done]
- STEP-03 — Verify copy integrity and repository scope  ◀ ACTIVE (step 4 of 4)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - `packages/core/`
  - `packages/tools/`
  - `packages/web/`
  - `packages/profile/`
  - `packages/web-profile/`
  - `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
  - `docs/source-extraction.md`
  - `SOURCE_SNAPSHOT.json`
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - The copied package manifests and imports remain DSH-native; this snapshot is not yet an independently buildable `@vuhoi/gat-*` workspace.
  - Cross-cutting DSH host changes are intentionally not copied into package directories; a later compatibility extraction must classify and create the exact versioned patchset.
  - Byte-for-byte verification must use tracked source inventory at the exact golden HEAD.
  - No credentials, API keys, tokens, passwords, or connection strings may be retained; any encountered value must be represented as `[REDACTED]`.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/{TASK-ID}/05_open_questions.md`
  - No blocking open points at creation time.

## Read First
**References to Read First:**
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `.ai-work/truth/canonical/methodology/30_templates/Source_Representation_Migration_Report_Template.md`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Source Representation Migration Report Template | SRC-METHOD-methodology-30-templates-source-representation-migration-report-template-md-1501 | `.ai-work/truth/canonical/methodology/30_templates/Source_Representation_Migration_Report_Template.md` | Used only to structure provenance and caution notes | — |

## Workspace Actions
- Record exact commands, exit codes, file counts, and limitations.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
All source/destination SHA-256 pairs match; aggregate hashes match; no forbidden path exists; golden-reference HEAD/status are unchanged; target changes are limited to declared outputs plus AIWS task artifacts.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Prove byte identity, expected counts, absence of excluded paths, unchanged source worktree, and bounded destination changes.

## Recommended Mode
Verifying

## Applicable Guidelines
- `AGENTS.md`

## Recommended Skills
- `superpowers:verification-before-completion`

## Inputs
- Source inventory and `SOURCE_SNAPSHOT.json`
- Git status from source and destination repositories

## Expected Outputs
- Fresh verification transcript and final status in workspace

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
All source/destination SHA-256 pairs match; aggregate hashes match; no forbidden path exists; golden-reference HEAD/status are unchanged; target changes are limited to declared outputs plus AIWS task artifacts.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Do not claim standalone build, installability, safety, or DSH compatibility from copy integrity alone.

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
- OUT-001-01-01 —  (draft)
- OUT-001-02-01 —  (draft)
