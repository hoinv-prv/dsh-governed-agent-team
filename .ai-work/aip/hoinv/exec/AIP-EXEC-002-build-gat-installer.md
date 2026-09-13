---
artifact_type: aip_exec
artifact_id: AIP-EXEC-002
title: "Build and verify the governed-agent-team installer"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "direct-human-request"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260913-exec-002
updated_at: 2026-09-13
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Build and verify the governed-agent-team installer

## SOP Compliance
- **Gate U1:** HUMAN confirmed the package namespace, copy-based installation mode, and complete acceptance contract in the current conversation.
- **Gate U2:** Package snapshot, golden design, DSH architecture, and installation contract are recorded below.
- **Gate U3:** Runtime open points are tracked in workspace `05_open_questions.md`.

## Objective
Create an official fail-closed installer for the five standalone Governed Agent Team packages, support only DeepSeek Harness `0.1.5-rc.2` at commit `c291e7961a515f6d7af9304e7fd1d257929aef26`, install transactionally into an isolated worktree, and execute every compatibility, rollback, idempotence, integrity, and keyless runtime check required by the HUMAN-supplied installation contract.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: the HUMAN supplied an exact compatibility target and acceptance contract; the work combines bounded package migration, installer implementation, and verification.
- Search/execution effect: use the copied golden design, source snapshot, DSH architecture, package sources, and exact target commit as direct authorities.
- Resolved references: GAT golden design, DSH architecture, AIWS execution rules, and the HUMAN installation contract.
- Deferred lookups: none.
- Expansion allowed: yes, only for target files and tests required to produce the exact versioned patchset and verification commands.

## Execution Scope
### In Scope
- Rename the five standalone packages to `@vuhoi/gat-core`, `@vuhoi/gat-tools`, `@vuhoi/gat-web`, `@vuhoi/gat-profile`, and `@vuhoi/gat-web-profile`.
- Add standalone pnpm workspace, build, typecheck, and keyless test wiring.
- Extract the exact DSH host changes between the supported base and accepted golden-reference commit into a versioned compatibility patchset.
- Add a machine-readable compatibility manifest with pristine hashes, changed-path allowlist, patchset checksum, package inventory, commands, and installation-record path.
- Add a copy-based transactional installer with dry-run, apply, status, rollback, simulated failure, and install-twice behavior.
- Install into the isolated DSH worktree requested by the prior contract and run all canonical compatibility checks.
- Document installation and usage without publishing or activating production.

### Out of Scope
- Supporting any DSH version or commit other than the pinned target.
- Modifying the main DSH checkout or golden-reference worktree.
- Writing shared pnpm store or global `node_modules` state.
- Real provider/API calls, credentials, publication, release, push, merge, tag, or production activation.
- Redesigning the accepted Governed Agent Team runtime behavior.

## Expected Outputs
- Root standalone workspace/build metadata and user-facing README.
- Renamed package manifests, imports, profile patches, tests, and package documentation.
- `compatibility/dsh-0.1.5-rc.2/` manifest, patchset, hashes, and verification scripts.
- `installer/` implementation and installer tests.
- Installer-generated installation record in the isolated target worktree.
- Fresh command evidence for dry-run, install, build/typecheck, compatibility behavior, rollback, idempotence, secret scan, and protected-repository integrity.

## Execution Input Package
### Plan Source
- Direct HUMAN request in the current conversation.
- HUMAN decisions: use the `@vuhoi/gat-*` namespace, copy packages into the target, and retain the complete prior install-and-verify contract.

### Required Truth Inputs
- `AGENTS.md`
- `.ai-work/truth/SOP_MASTER.md` (empty project placeholder)
- `.ai-work/truth/AI_WORK_CONTRACT.md` (empty project placeholder)

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Accepted GAT V1 design | (none) | `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md` | Copied project design used as implementation authority | [retrieval_gap] |
| DSH architecture | (external target authority) | `/home/hoinv/deepseek-harness/docs/architecture.md` | Required before target package changes | — |
| Source snapshot | (one-off provenance record) | `SOURCE_SNAPSHOT.json` | Exact copied-package provenance | — |

### Reference lookup
- Ran `python3 .ai-work/tooling/lookup_wiki_source.py --query "governed agent team design" --limit 5`.
- Retried with `--mode semantic`; no registered project source resolved to the copied GAT design.
- Ran `python3 .ai-work/tooling/lookup_wiki_source.py --query "governed agent team installer compatibility patchset" --limit 5`; results were unrelated generic AIWS patch guides.

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before implementation writes.
- Open-points log available.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request and prior installer contract | Build the missing official installer, then perform the original exact install-and-verify mission | The prior 18-point verification list remains mandatory | None after three explicit selections | ✅ direct confirmation |
| Package snapshot | Five byte-copied DSH-native packages exist but retain old identities and lack standalone wiring | Runtime behavior must stay aligned with the accepted golden implementation | Cross-package rename and build fixes are expected migration work | ✅ package location supplied |
| Golden design | Durable governance, exact approval revision, preflight, nested dispatch denial, Web-only HUMAN approval, and replay are required | Golden implementation is the behavioral oracle | None | ✅ previously accepted reference |
| DSH target | Only version `0.1.5-rc.2` at the exact pinned commit is supported | Host changes are the base-to-golden diff, filtered to required compatibility paths | Exact hashes must be generated from pristine base files | ✅ prior contract |

## References to Read First
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `docs/source-extraction.md`
- `SOURCE_SNAPSHOT.json`
- `/home/hoinv/work/dsh-governed-agent-team-install-prompt.md`
- `/home/hoinv/deepseek-harness/docs/architecture.md`

## Current Risks / Constraints
- The source tree is currently untracked and DSH-native; package identity changes affect source imports, tests, profile rows, generated Remote identity, and documentation.
- The main DSH checkout contains unrelated user changes and must remain untouched.
- The golden-reference worktree contains untracked `.hermes/` and `.superpowers/` evidence that must remain untouched.
- Installer operations must be transactional and must not modify the source repo, shared pnpm store, or global modules.
- Vanilla DSH cannot replay required GAT events unless the exact host event registration patch is installed.
- No PASS claim is allowed unless every mandatory compatibility check executes freshly and succeeds.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/{TASK-ID}/05_open_questions.md`
- No blocking open points after HUMAN confirmed namespace, copy mode, and full acceptance scope.

## Workspace Execution Rule
Runtime findings, metrics, progress, open questions, and final output live in the task workspace, not in this AIP.

## Execution Steps

### Step: STEP-00 — Confirm installer contract (HARD GATE)
Objective:
Record package naming, copy semantics, supported DSH identity, protected paths, canonical operations, and PASS conditions.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `AGENTS.md`
- wiki:none — project lookup found no registered GAT installer guidance; the direct HUMAN contract governs this task.

Recommended Skills:
- direct confirmation

Inputs:
- Current HUMAN request and answers
- Prior install-and-verify contract

Expected Outputs:
- Confirmed task-understanding evidence in workspace findings

Done Condition:
The HUMAN has explicitly confirmed namespace, installation mode, and full contract scope.

Notes / Constraints:
- Do not implement a reduced installer or broaden version support.

Workspace Actions:
- Record the three HUMAN selections and exact pinned target.

### Step: STEP-01 — Migrate packages into a standalone workspace
Objective:
Rename package identities and internal references, add workspace build wiring, and preserve accepted runtime behavior.

Recommended Mode:
Executing

Applicable Guidelines:
- `AGENTS.md`
- `/home/hoinv/deepseek-harness/AGENTS.md`
- `/home/hoinv/deepseek-harness/packages/AGENTS.md`
- `/home/hoinv/deepseek-harness/packages/experimental/AGENTS.md`

Recommended Skills:
- direct TypeScript package migration

Inputs:
- `packages/`
- `SOURCE_SNAPSHOT.json`
- Accepted golden design

Expected Outputs:
- Five `@vuhoi/gat-*` packages
- Root workspace/build/test metadata
- Updated package documentation

Done Condition:
Standalone install, build, typecheck, and focused package tests pass without changing runtime behavior.

Notes / Constraints:
- Keep DSH workspace dependencies exact and private-local; do not publish.

Workspace Actions:
- Record rename inventory, commands, and test evidence.

### Step: STEP-02 — Extract exact DSH compatibility patchset
Objective:
Create the minimal deterministic host patch required to mount and replay GAT at the exact supported DSH commit.

Recommended Mode:
Executing

Applicable Guidelines:
- `AGENTS.md`
- `/home/hoinv/deepseek-harness/AGENTS.md`
- `/home/hoinv/deepseek-harness/docs/architecture.md`

Recommended Skills:
- deterministic Git diff extraction and review

Inputs:
- Supported DSH base commit
- Accepted golden-reference commit
- Renamed standalone packages

Expected Outputs:
- Versioned compatibility patch
- Pristine source hashes and changed-path allowlist
- Patchset checksum

Done Condition:
The patch applies cleanly to a pristine target, changes only declared host paths, and includes every required host compatibility component.

Notes / Constraints:
- Package copies are installer payload, not duplicated as patch hunks.

Workspace Actions:
- Record path classification and hash evidence.

### Step: STEP-03 — Implement transactional installer and manifest
Objective:
Implement canonical dry-run, apply, status, rollback, simulated-failure, and repeated-install behavior from one validated manifest.

Recommended Mode:
Executing

Applicable Guidelines:
- `AGENTS.md`
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`

Recommended Skills:
- fail-closed filesystem transaction design

Inputs:
- Standalone package payload
- Exact compatibility patchset
- Prior installer contract

Expected Outputs:
- Installer CLI
- Compatibility manifest
- Installation-record schema/output
- Installer behavior tests

Done Condition:
Dry-run performs no writes; apply is transactional; failure rollback is clean; repeated install is idempotent or safely refused; all paths and hashes are manifest-controlled.

Notes / Constraints:
- Never invoke package-manager postinstall or write shared package stores.

Workspace Actions:
- Record installer scenarios and failure evidence.

### Step: STEP-04 — Install and run complete compatibility verification
Objective:
Create the isolated target worktree, execute canonical dry-run/apply, and run every required keyless compatibility check.

Recommended Mode:
Verifying

Applicable Guidelines:
- `AGENTS.md`
- `/home/hoinv/deepseek-harness/AGENTS.md`

Recommended Skills:
- focused integration verification

Inputs:
- Completed installer and manifest
- Exact supported DSH commit
- Prior 18-point verification contract

Expected Outputs:
- Isolated installed worktree
- Installation record
- Fresh build, typecheck, profile, replay, authorization, rollback, idempotence, and Web-smoke evidence

Done Condition:
Every mandatory command exists, runs without real providers, and exits zero with no skipped required coverage.

Notes / Constraints:
- Do not substitute weaker smoke tests for a failed canonical command.

Workspace Actions:
- Record exact commands, exit codes, test counts, and changed paths.

### Step: STEP-05 — Final integrity review and close
Objective:
Verify allowlisted scope, secret absence, protected repository integrity, process cleanup, documentation accuracy, and final evidence.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

Recommended Skills:
- independent diff and evidence review

Inputs:
- Installer outputs and all verification transcripts
- Git status for source, target, main, and golden repositories

Expected Outputs:
- Final contract-format report
- Completed AIWS workspace output and scoped lint evidence

Done Condition:
All PASS conditions are evidenced, no secret or out-of-scope path exists, no task process remains, and unresolved limitations are explicit.

Notes / Constraints:
- Do not commit, push, publish, release, or clean the installed worktree.

Workspace Actions:
- Perform final capture sweep and write final report.

## Done Criteria
- [ ] Gate U1 confirmation evidence is recorded.
- [ ] All five packages use the confirmed `@vuhoi/gat-*` identities and pass standalone build/typecheck/tests.
- [ ] Compatibility manifest pins exact DSH version and commit with pristine hashes, path allowlist, and patchset checksum.
- [ ] Canonical dry-run exits zero and leaves the isolated target pristine.
- [ ] Canonical apply exits zero, writes the complete installation record, and changes no path outside the manifest allowlist.
- [ ] Rollback and repeated-install behavior are executed and pass.
- [ ] All 18 mandatory compatibility areas run through canonical keyless commands and pass.
- [ ] Secret scan and `git diff --check` pass.
- [ ] Main DSH checkout, golden reference, and GAT source protected inputs are not modified by installer execution.
- [ ] No process or service remains and no commit/push/merge/tag/release occurs.
- [ ] Gate U3 has no unresolved blocker at close.
- [ ] Scoped AIWS lint exits with zero errors.

## Self-check / Review Points
- Confirm source package behavior remains aligned with the accepted golden reference after identity migration.
- Review the host patch independently against base-to-golden path inventory.
- Treat installer path parsing, traversal prevention, symlink handling, rollback, and interruption as untrusted-boundary code.
- Verify every PASS statement against fresh command output rather than prior reports.

## Finalization Notes
- Completion means the installer and exact compatibility contract are implemented and freshly verified in the isolated target; it does not authorize release or production use.

## Pre-flight Pending Captures
- [IMPORTED 2026-09-13] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="Governed Agent Team V1 design" lookup_query="governed agent team design" reason="The reusable project design exists under docs/golden-reference but has no registered project Wiki Source route."

## Re-plan Rule
Any change to supported DSH identity, package namespace, installation mode, required compatibility coverage, or expected outputs requires a dated Re-plan Log entry before execution continues.

## Re-plan Log
- (no re-plan yet)
