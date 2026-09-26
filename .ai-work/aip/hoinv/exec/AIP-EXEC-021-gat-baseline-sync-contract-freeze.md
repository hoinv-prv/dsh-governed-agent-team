---
artifact_type: aip_exec
artifact_id: AIP-EXEC-021
title: "Sync current DSH GAT baseline and freeze member-binding contracts"
status: active
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: AIP-PLAN-001
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-exec-021
updated_at: 2026-09-26
---

<!-- Stable control: Done Criteria declarative. Runtime state belongs in the Task Workspace. -->

# AIP_EXEC — Sync current DSH GAT baseline and freeze member-binding contracts

## SOP Compliance
- Gate U1: HUMAN confirmed the recommended baseline direction and explicitly requested continuation on 2026-09-26; persist evidence in STEP-00 workspace findings.
- Gate U2: input understanding below; executable source/tests outrank maintained references.
- Gate U3: track all runtime open points in workspace `05_open_questions.md`.

## Objective
Establish the current DSH experimental GAT implementation as the behavioral baseline, synchronize that baseline into the standalone GAT authoring/distribution repository without overwriting unrelated work, freeze the cross-repository contracts required by later member-binding execution packages, and prove compatibility with focused tests plus installer verification.

## Selected Task Lens / Mode
- Lens: design_authoring
- Reason: implementation synchronization plus an explicit design-contract freeze is required before binder and DSH lifecycle work can begin.
- Search/execution effect: prioritize current source/tests, registered GAT design and installer references, package/profile manifests, compatibility mappings, and deterministic diff evidence.
- Resolved references: `SRC-GAT-DESIGN-REFERENCE`, `SRC-GAT-INSTALLER-COMPATIBILITY`, AIP-PLAN-001 final plan/findings.
- Deferred lookups: none; exact source/test inventory is a STEP-01 bounded repository comparison.
- Expansion allowed: yes, restricted to standalone GAT and `/home/hoinv/deepseek-harness` paths needed for baseline comparison/verification.

## Execution Scope
### In Scope
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/` — runtime evidence, diffs, decisions, verification logs and final handoff.
- `packages/core/**`, `packages/tools/**`, `packages/profile/**`, `packages/web/**`, `packages/web-profile/**` — synchronize only demonstrated DSH experimental GAT baseline deltas.
- `compatibility/**`, `installer/**`, root package/version manifests and relevant verification fixtures — update only when the synchronized package surface requires it.
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` — correct current-source mapping if synchronization changes its caveat.
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` — create the approved EXEC-B/EXEC-C boundary contract.
- Preserve unrelated local modifications through file-by-file three-way reasoning and exact pre/post evidence.

### Out of Scope
- Implement binder registry, durable member attachments, two-phase subagent lifecycle, Durable Agent service integration, or mission lifecycle changes.
- Modify `/home/hoinv/deepseek-harness` source; it is read-only baseline/reference for this EXEC.
- Rewrite project Truth/canonical Wiki or auto-promote captures.
- Clean, reset, stash, or overwrite unrelated existing working-tree changes.
- Activate a live profile or mutate the running DSH Web GUI.

## Expected Outputs
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/04_findings.md` — source-authority map, exact delta inventory, preservation decisions and evidence.
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/07_output_draft.md` — synchronization and contract-freeze draft.
- `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/11_output_final.md` — compatibility results and EXEC-B/EXEC-C readiness handoff.
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` — versioned semantic contracts and unresolved HUMAN decisions.
- Bounded standalone package/test/profile/compatibility updates required to match the selected DSH behavioral baseline.

## Execution Input Package
### Plan Source
- `.ai-work/aip/hoinv/plan/AIP-PLAN-001-gat-dsh-durable-agent-team-plan.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-plan-001/11_output_final.md`
- HUMAN confirmation: use current DSH experimental GAT as behavioral baseline and continue with EXEC-A.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT design reference | SRC-GAT-DESIGN-REFERENCE | `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` | Maintained reference; executable source/tests override | — |
| Installer compatibility specification | SRC-GAT-INSTALLER-COMPATIBILITY | `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md` | Reviewed installer safety constraints | — |

### Reference lookup
- `python3 .ai-work/tooling/lookup_wiki_source.py --query "GAT baseline sync DSH experimental packages compatibility contract freeze" --limit 5 --format json --slim`
- Result: registered GAT design and installer compatibility references resolved.

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before every step.
- Existing dirty working tree recorded before modification.
- No target file changed without first reading standalone and DSH baseline variants.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN confirmation | DSH experimental GAT is the current behavioral baseline; standalone becomes authoring/distribution source after sync | Baseline sync is authorized, but destructive overwrite is not | None for execution start | ✅ |
| AIP-PLAN-001 final plan | Phase 0 precedes binder/attachment and DSH lifecycle work; baseline sync and contract freeze are separate from feature implementation | EXEC-A may update source/tests/docs only for proven current-baseline deltas | Exact file set must be discovered and justified | ✅ |
| DSH experimental GAT source | Contains newer simple-mode initializer, bounded manifest loading, route preflight and Agent route support | Current checkout is reference-only and must be pinned by commit/status evidence | It may include unrelated or incomplete work; diff/test evidence decides adoption | ✅ direction only |
| Standalone working tree | Contains substantial pre-existing changes and untracked files | Preserve them and avoid blanket directory copies | Attribution of overlapping edits must be resolved file by file | ✅ constraint |

## References to Read First
- `.ai-work/workspaces/hoinv/TASK-20260926-plan-001/04_findings.md`
- `.ai-work/workspaces/hoinv/TASK-20260926-plan-001/11_output_final.md`
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-core/`
- `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/`
- Standalone counterpart packages and tests.

## Current Risks / Constraints
- The standalone working tree already has overlapping modifications; direct copy/rsync is prohibited.
- DSH and standalone package names/imports/profile wiring may intentionally differ.
- Generated artifacts and source artifacts must not be confused; source-of-truth file direction must be documented.
- Installer compatibility remains strict for host preimages, installed bytes and post-build verification even when development source drift is allowed.
- Contract freeze must not silently implement EXEC-B/EXEC-C behavior.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/05_open_questions.md`
- Whether every DSH-side delta belongs in standalone, or some are host-only integration differences; resolve by evidence in STEP-01.
- Exact event migration strategy and attachment size limits remain decision placeholders for later HUMAN review unless existing DSH conventions determine them.

## Workspace Execution Rule
Runtime state, diffs, counts, decisions and verification results belong in the Task Workspace, not this AIP.

## Execution Steps

### Step: STEP-00 — Persist confirmed task understanding
Objective:
Record that HUMAN selected the recommended behavioral-baseline direction and authorized EXEC-A continuation.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`

Recommended Skills:
- `aiws-aip`

Inputs:
- HUMAN confirmation in the current session.
- AIP-PLAN-001 handoff.

Expected Outputs:
- Confirmation evidence and non-destructive execution constraints in workspace findings.

Done Condition:
Workspace records the confirmed direction, output boundary and preservation constraints.

Notes / Constraints:
- The HUMAN confirmation already satisfies the gate; do not ask again unless new ambiguity changes objective or scope.

Workspace Actions:
- Update `00_task_brief.md`, `04_findings.md` and `05_open_questions.md`.

### Step: STEP-01 — Pin baselines and build exact delta inventory
Objective:
Record exact standalone/DSH revisions and dirty state, then compare relevant package/source/test/profile/compatibility files to classify each delta as adopt, preserve standalone, merge, generated, or out of scope.

Recommended Mode:
Investigating

Applicable Guidelines:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`

Recommended Skills:
- `context-delegation`

Inputs:
- Standalone repository current files and git state.
- DSH experimental GAT package files and git state.

Expected Outputs:
- Exact baseline identifiers.
- File-level delta matrix with authority and intended action.
- Explicit overlap/risk list before edits.

Done Condition:
Every candidate target file has a classified action and no file with unexplained local changes is approved for modification.

Notes / Constraints:
- Read both variants before any edit.
- Ignore build outputs unless installer/runtime contract requires them.

allow_raw_search: true

Workspace Actions:
- Write inventory to `04_findings.md` and supporting diff summaries under the workspace.

### Step: STEP-02 — Synchronize approved baseline deltas
Objective:
Apply the minimal file-by-file changes needed for standalone source/tests/profiles to represent the selected current DSH GAT behavior while preserving project-specific distribution semantics and unrelated work.

Recommended Mode:
Executing

Applicable Guidelines:
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`

Recommended Skills:
- (none — controlled read/edit/write and deterministic diff verification)

Inputs:
- STEP-01 classified delta matrix.
- Exact standalone and DSH file variants.

Expected Outputs:
- Reviewed source/test/profile/compatibility changes.
- Pre/post preservation evidence for overlapping dirty files.

Done Condition:
All adopted deltas are traceable to the matrix; excluded differences remain untouched and documented.

Notes / Constraints:
- No blanket directory replacement.
- Do not modify DSH checkout.
- Stop if a target edit cannot preserve existing intent confidently.

Workspace Actions:
- Record each applied file and rationale immediately in `04_findings.md`.

### Step: STEP-03 — Freeze member-binding integration contracts
Objective:
Create a stable contract document for EXEC-B and EXEC-C without implementing the contracts.

Recommended Mode:
Design authoring

Applicable Guidelines:
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

Recommended Skills:
- `dsh-council-review`

Inputs:
- AIP-PLAN-001 target architecture.
- Synchronized baseline APIs and lifecycle seams.
- DSH subagent continuation contracts.

Expected Outputs:
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` covering ownership, normalized initializer/member spec, attachments/bounds, binder lifecycle, DSH two-phase lifecycle invariants, event migration decision points, version negotiation, conformance fixtures and compatibility matrix.

Done Condition:
EXEC-B and EXEC-C can proceed independently without inventing shared semantics; unresolved HUMAN decisions are explicit and non-defaulted.

Notes / Constraints:
- Status must remain proposed/contract freeze for implementation planning, not runtime activation authority.

Workspace Actions:
- Record design evidence and review notes in workspace.

### Step: STEP-04 — Verify compatibility and prepare handoff
Objective:
Run focused package tests/build/type checks, persistence/profile integration tests, installer structural checks and final AIWS lint; report real results and residual risks.

Recommended Mode:
Verification

Applicable Guidelines:
- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`

Recommended Skills:
- `aiws-lint`

Inputs:
- STEP-02 changes.
- STEP-03 contract freeze.

Expected Outputs:
- Verification matrix with exact commands/results.
- Final handoff determining readiness for EXEC-B and EXEC-C.
- Deferred capture disposition.

Done Condition:
No unexplained regression remains; failures are fixed or explicitly block readiness; task lint is reported truthfully.

Notes / Constraints:
- Do not activate a live profile.
- Separate structural install verification from post-build runtime/profile verification.

Workspace Actions:
- Finalize `11_output_final.md`, close open points, triage captures and run scoped lint.

## Done Criteria
- [ ] Behavioral baseline and exact source revisions are pinned.
- [ ] File-level delta inventory distinguishes adopted, merged, preserved and excluded differences.
- [ ] Existing unrelated working-tree changes are preserved.
- [ ] Standalone packages/tests/profile wiring reflect approved current DSH GAT behavior.
- [ ] Contract-freeze document defines EXEC-B/EXEC-C shared semantics and explicit decision points.
- [ ] Focused package, persistence, profile and installer verification results are recorded.
- [ ] No binder, durable attachment or two-phase lifecycle feature is implemented prematurely.
- [ ] Gate U1/U2/U3 evidence is complete.
- [ ] Final scoped AIWS lint has zero errors and warnings.

## Self-check / Review Points
- Did any adopted DSH delta depend on host-only private behavior?
- Was any existing standalone edit overwritten rather than merged?
- Are package naming, imports and profile composition correct for standalone distribution?
- Does the contract freeze clearly separate GAT authority, DSH host authority and Durable Agent ownership?
- Are compatibility gates and rollback evidence preserved?
- Can EXEC-B and EXEC-C start from the document without hidden shared assumptions?

## Finalization Notes
- Attribution check applies only if a touched target document explicitly names AIP-EXEC-021.
- Capture candidates are triaged, never promoted automatically.
- This EXEC does not authorize live profile activation or upstream DSH modification.

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Any objective, scope or expected-output change requires a dated Re-plan Log entry before editing earlier sections.

## Re-plan Log
- (no re-plan yet)
