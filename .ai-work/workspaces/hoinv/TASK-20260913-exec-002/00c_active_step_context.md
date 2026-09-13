---
artifact_type: active_step_context
artifact_id: ASC-TASK-20260913-exec-002-STEP-05
task_id: TASK-20260913-exec-002
working_aip_ref: AIP-EXEC-002
working_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-002-build-gat-installer.md
active_step_id: STEP-05
active_step_title: Final integrity review and close
source_aip: AIP-EXEC-002
source_aip_path: __PROJECT_ROOT__/.ai-work/aip/hoinv/exec/AIP-EXEC-002-build-gat-installer.md
step_id: STEP-05
step_index: 6
step_total: 6
status: active
active_task_lens: 
staleness_status: fresh
staleness_reason: 
updated_at: 2026-09-13
---

# Active Step Context — Final integrity review and close

## AIP Goal & Outcome
- Goal (AIP-level objective):
  Create an official fail-closed installer for the five standalone Governed Agent Team packages, support only DeepSeek Harness `0.1.5-rc.2` at commit `c291e7961a515f6d7af9304e7fd1d257929aef26`, install transactionally into an isolated worktree, and execute every compatibility, rollback, idempotence, integrity, and keyless runtime check required by the HUMAN-supplied installation contract.
- Final outcome (AIP Expected Outputs):
  - Root standalone workspace/build metadata and user-facing README.
  - Renamed package manifests, imports, profile patches, tests, and package documentation.
  - `compatibility/dsh-0.1.5-rc.2/` manifest, patchset, hashes, and verification scripts.
  - `installer/` implementation and installer tests.
  - Installer-generated installation record in the isolated target worktree.
  - Fresh command evidence for dry-run, install, build/typecheck, compatibility behavior, rollback, idempotence, secret scan, and protected-repository integrity.
- Scope:
  - Rename the five standalone packages to `@vuhoi/gat-core`, `@vuhoi/gat-tools`, `@vuhoi/gat-web`, `@vuhoi/gat-profile`, and `@vuhoi/gat-web-profile`.
  - Add standalone pnpm workspace, build, typecheck, and keyless test wiring.
  - Extract the exact DSH host changes between the supported base and accepted golden-reference commit into a versioned compatibility patchset.
  - Add a machine-readable compatibility manifest with pristine hashes, changed-path allowlist, patchset checksum, package inventory, commands, and installation-record path.
  - Add a copy-based transactional installer with dry-run, apply, status, rollback, simulated failure, and install-twice behavior.
  - … (digest trimmed — open the AIP for the full text)

## Step Map — You Are Here
- STEP-00 — Confirm installer contract (HARD GATE)  [upstream — done]
- STEP-01 — Migrate packages into a standalone workspace  [upstream — done]
- STEP-02 — Extract exact DSH compatibility patchset  [upstream — done]
- STEP-03 — Implement transactional installer and manifest  [upstream — done]
- STEP-04 — Install and run complete compatibility verification  [upstream — done]
- STEP-05 — Final integrity review and close  ◀ ACTIVE (step 6 of 6)

## Downstream / Output Contract
- Final step. This AIP's `## Expected Outputs`:
  - Root standalone workspace/build metadata and user-facing README.
  - Renamed package manifests, imports, profile patches, tests, and package documentation.
  - `compatibility/dsh-0.1.5-rc.2/` manifest, patchset, hashes, and verification scripts.
  - `installer/` implementation and installer tests.
  - Installer-generated installation record in the isolated target worktree.
  - Fresh command evidence for dry-run, install, build/typecheck, compatibility behavior, rollback, idempotence, secret scan, and protected-repository integrity.
- Shape this step's output to satisfy the above.

## Guardrails (from AIP)
- **Current Risks / Constraints:**
  - The source tree is currently untracked and DSH-native; package identity changes affect source imports, tests, profile rows, generated Remote identity, and documentation.
  - The main DSH checkout contains unrelated user changes and must remain untouched.
  - The golden-reference worktree contains untracked `.hermes/` and `.superpowers/` evidence that must remain untouched.
  - Installer operations must be transactional and must not modify the source repo, shared pnpm store, or global modules.
  - Vanilla DSH cannot replay required GAT events unless the exact host event registration patch is installed.
- **Known Open Points:**
  - Open Points log: `.ai-work/workspaces/hoinv/{TASK-ID}/05_open_questions.md`
  - No blocking open points after HUMAN confirmed namespace, copy mode, and full acceptance scope.
- **Live open points recorded in workspace** `05_open_questions.md`

## Read First
**References to Read First:**
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `docs/source-extraction.md`
**Required Wiki Inputs:** (see AIP for full table)
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Accepted GAT V1 design | (none) | `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md` | Copied project design used as implementation authority | [retrieval_gap] |

## Workspace Actions
- Perform final capture sweep and write final report.

## Acceptance Criteria
**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)

**Done Criteria (for this step):**
All PASS conditions are evidenced, no secret or out-of-scope path exists, no task process remains, and unresolved limitations are explicit.

## Active Task Lens
- No explicit lens (No-Lens) — read from intent (zero forced overhead)
- Reading-surface hint (CR-030): when a lens is set, prioritise its preset `relevant_source_types` + `register_priority`/`expansion_priority` (`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard filter; expand or verify raw/source when correctness needs it.

## Step Objective
Verify allowlisted scope, secret absence, protected repository integrity, process cleanup, documentation accuracy, and final evidence.

## Recommended Mode
Reviewing

## Applicable Guidelines
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

## Recommended Skills
- independent diff and evidence review

## Inputs
- Installer outputs and all verification transcripts
- Git status for source, target, main, and golden repositories

## Expected Outputs
- Final contract-format report
- Completed AIWS workspace output and scoped lint evidence

## Step Output / Decision Persistence Requirements
→ See `AIP_Detail_Spec_MVP.md` §7.2

## Source Verification Requirements
→ See `Active_Step_Context_Spec_MVP.md` §5

## Done Condition
All PASS conditions are evidenced, no secret or out-of-scope path exists, no task process remains, and unresolved limitations are explicit.

## Output State
| Path | Exists | VCS Status | Suggested Mode |
|---|---|---|---|
| (no expected outputs declared) | — | — | — |

## Notes / Constraints
- Do not commit, push, publish, release, or clean the installed worktree.

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
- OUT-002-01-01 —  (draft)
- OUT-002-02-01 —  (draft)
- OUT-002-03-01 —  (draft)
- OUT-002-04-01 —  (draft)

## Capture Inbox References
- CAP-002-01 — retrieval gap: Governed Agent Team V1 design (captured)
