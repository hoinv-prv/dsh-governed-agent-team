---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260926-exec-020-STEP-11
task_id: TASK-20260926-exec-020
working_aip_ref: AIP-EXEC-020
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-020-bootstrap-gat-design-wiki.md
active_step_id: STEP-11
active_step_title: Produce the project's wiki build-up guideline
source_aip: AIP-EXEC-020
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-020-bootstrap-gat-design-wiki.md
step_id: STEP-11
step_index: 12
step_total: 12
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-26
---

# Active Step Context — Produce the project's wiki build-up guideline

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Build the first project wiki for the approved GAT design-document corpus, supporting Q&A plus design, implementation, and review tasks.
- Final outcome (AIP Expected Outputs):
  - Registered metadata and index entries for the six scoped design documents.
  - Document-to-document relations only, with no object nodes.
  - Build log, lesson log, lookup tests, and project wiki overview pages.
  - A project wiki build-up guideline derived from the completed build.
- Scope:
  - `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
  - `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
  - `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`
  - `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
  - `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md`
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm Task Understanding (HARD GATE)  [upstream — done]
- STEP-01 — Define the GOAL of the wiki  [upstream — done]
- STEP-02 — Decide WHAT goes in (inventory)  [upstream — done]
- STEP-03 — Confirm authority / value / use  [upstream — done]
- STEP-04 — Predict the relationships  [upstream — done]
- STEP-05 — Plan the meta build  [upstream — done]
- STEP-06 — Identify the tools to build  [upstream — done]
- STEP-07 — Trial-run build-meta on samples  [upstream — done]
- STEP-08 — Build/confirm the refresh tool  [upstream — done]
- STEP-09 — Mass-run + spot-checks + wire relations  [upstream — done]
- STEP-10 — Test the wiki; tune the profile  [upstream — done]
- STEP-11 — Produce the project's wiki build-up guideline  ◀ ACTIVE (step 12 of 12)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Registered metadata and index entries for the six scoped design documents.
  - Document-to-document relations only, with no object nodes.
  - Build log, lesson log, lookup tests, and project wiki overview pages.
  - A project wiki build-up guideline derived from the completed build.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - This is a first-build operation; no project wiki metadata or index entries currently exist.
  - The selected WBS document must remain v39 only; historical revisions and evidence are excluded.
  - Candidate metadata and relations require Human review gates before application.
- **Known Open Points:**
  - Open Points log: workspace `05_open_questions.md`.
  - No object-node enumeration source exists; identity nodes are intentionally skipped.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md`
- `.ai-work/procedural/skills/aiws-wiki/operations/bootstrap.md`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Project wiki buildup guideline | SRC-WIKIGUIDE-wiki-guidelines-core-guidelines-project-wiki-buildup-guideline-md-1d04 | `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` | Fixed bootstrap method | — |

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
- Human accepts the guideline and lesson triage; overview build completes.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Produce and accept the project wiki buildup guideline, incorporating BUILD LOG and triaged lessons; generate overview pages.

## Recommended Mode
Executing

## Applicable Guidelines
- `.ai-work/truth/canonical/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md` §How an AI should use this guideline; §Step 11

## Recommended Skills
- ...

## Inputs
- `build-log.md`
- Lesson log and accepted build results

## Expected Outputs
- Project wiki buildup guideline and generated contents/search/health overview pages

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
- Human accepts the guideline and lesson triage; overview build completes.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Run `python3 .ai-work/tooling/build_wiki_overview.py --all-systems` at wrap-up.

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
- OUT-020-01-01 —  (draft)
- OUT-020-02-01 —  (draft)
- OUT-020-03-01 —  (draft)
- OUT-020-04-01 —  (draft)
- OUT-020-09-01 —  (draft)
- OUT-020-10-01 —  (draft)
