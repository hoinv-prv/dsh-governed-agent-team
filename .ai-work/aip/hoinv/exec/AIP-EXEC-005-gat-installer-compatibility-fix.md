---
artifact_type: aip_exec
artifact_id: AIP-EXEC-005
title: "Investigate and fix GAT installer version compatibility"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct user request on 2026-09-13"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260913-gat-installer-compatibility-fix
updated_at: 2026-09-13
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state belongs in the workspace. -->

# AIP_EXEC — Investigate and fix GAT installer version compatibility

## SOP Compliance

- Gate U1 Confirm-understanding-of-task: STEP-00
- Gate U2 Confirm-understanding-of-input: `## Input Understanding`
- Gate U3 Open Points tracking: workspace `05_open_questions.md`

## Objective

Determine why `dsh web` cannot load the installed GAT packages, assess the proposed installer version/compatibility refactor against the actual installer architecture, implement the smallest correct fix, and verify installer and runtime behavior without disturbing unrelated in-progress core/UI work.

## Selected Task Lens / Mode

- Lens: No-Lens
- Reason: The task has one explicit local specification and concrete runtime/installer evidence; repository source and tests are the authoritative implementation evidence.
- Search/execution effect: Resolve the supplied specification, installer, compatibility manifest, package metadata, and installed profile links directly.
- Resolved references: User error log; `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`; installer source and tests.
- Deferred lookups: None.
- Expansion allowed: yes, within installer/package/profile/runtime integration paths.

## Execution Scope

### In Scope

- Root-cause analysis of missing `lib/index.js` for `@vuhoi/gat-core`, `@vuhoi/gat-tools`, and `@vuhoi/gat-web`.
- Review and correction of the proposed compatibility refactor specification.
- Installer/version descriptor/compatibility implementation and focused tests.
- Verification against `/home/hoinv/deepseek-harness` using non-destructive checks first.

### Out of Scope

- Unrelated multi-mission UI/core changes already present in the worktree.
- Publishing packages or releases.
- Destructive reset of the target DSH worktree or user profile.

## Expected Outputs

- Root-cause evidence in the task workspace.
- A reviewed and, where necessary, corrected refactor specification.
- Installer implementation and regression tests that separate source integrity, compatibility, and post-install correctness.
- Reproducible verification results and user-facing recovery/start instructions.

## Execution Input Package

### Plan Source

- User request and pasted `dsh web` failure log.

### Required Truth Inputs

- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| GAT installer compatibility refactor spec | (none) | docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md | Reusable project specification supplied by user; project Wiki lookup returned no reliable match | [retrieval_gap] |

### Reference lookup

- `python3 .ai-work/tooling/lookup_wiki_source.py --query "installer version compatibility refactor"`
- Lookup returned only fragile AIWS-generic matches, so the user-supplied path is used directly.

### Required Workspace Preconditions

- [ ] Workspace created.
- [ ] Active Step Context available.
- [ ] Open-points log initialized.

## Input Understanding

| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| Pasted runtime log | Profile packages resolve to `lib/index.js`, but those entrypoint files are absent. Root cause may involve build/install mode, stale symlinks, or incomplete payload installation. | The pasted log is from the current local GAT/DSH setup. | Exact current symlink targets and build outputs require inspection. | pending |
| Refactor specification | Proposes replacing source-hash authorization with explicit GAT/DSH compatibility metadata while retaining post-install verification. | It is advisory and may be edited as part of the requested fix. | Some proposed behavior may conflate source-copy installs with profile symlink/build behavior. | pending |

## References to Read First

- `docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md`
- `installer/index.mjs`
- `installer/verify.mjs`
- `installer/tests/cli.test.mjs`
- `compatibility/dsh-0.1.5-rc.2/manifest.json`
- Root and package-level `package.json` files.

## Current Risks / Constraints

- The repository already contains unrelated modified and untracked files; preserve them.
- The compatibility manifest is already modified, so distinguish pre-existing edits from this task before changing it.
- Target DSH and `~/.dsh` are outside the writable project scope; mutation there requires explicit authorization if needed.
- Operating Memory was read and contained no relevant entries.

## Known Open Points

- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260913-gat-installer-compatibility-fix/05_open_questions.md`
- No blocker identified before inspection.

## Workspace Execution Rule

Runtime findings, decisions, test results, and captures are written to the task workspace rather than this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)

Objective:
Confirm that the task is to diagnose the current `dsh web` failure, evaluate and amend the supplied refactor spec, implement the appropriate repository fix, and verify a safe recovery path.

Recommended Mode:
Clarifying

Applicable Guidelines:
- wiki:none

Recommended Skills:
- aiws-aip

Inputs:
- User request
- Pasted runtime error
- Declared task scope above

Expected Outputs:
- Explicit user confirmation or explicit authorization to proceed without another confirmation gate

Done Condition:
The user confirms the stated understanding or delegates the gate.

Notes / Constraints:
- Do not mutate installer or target DSH state before confirmation.

Workspace Actions:
- Record task understanding and confirmation evidence.

### Step: STEP-01 — Establish Root Cause

Objective:
Inspect installer authorization, package exports/build outputs, compatibility mappings, target DSH commit/state, and profile package links to isolate the complete causal chain.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- Installer and verification source
- Package manifests and build configuration
- Read-only target DSH/profile state

Expected Outputs:
- Reproducible root-cause report with primary and contributing causes

Done Condition:
The missing entrypoints and the installer behavior that allowed or caused them are explained with file/system evidence.

Notes / Constraints:
- Keep target inspection read-only.

Workspace Actions:
- Record commands and findings in `04_findings.md`.

### Step: STEP-02 — Review and Reconcile the Specification

Objective:
Compare every material proposal with current architecture and revise unsupported or incomplete requirements.

Recommended Mode:
Reviewing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- Root-cause evidence
- Refactor specification
- Installer tests and manifest schema

Expected Outputs:
- Clear verdict and corrected specification where required

Done Condition:
The design covers authorization, target compatibility, installed-state validation, build/entrypoint readiness, rollback, and legacy manifest behavior without weakening safety unintentionally.

Notes / Constraints:
- Treat source hashes and installed-file hashes as separate concerns.

Workspace Actions:
- Record review findings and decisions.

### Step: STEP-03 — Implement the Fix

Objective:
Implement the accepted design in installer/version metadata/tests and adjust the specification to match the landed behavior.

Recommended Mode:
Executing

Applicable Guidelines:
- wiki:none

Recommended Skills:
- (none)

Inputs:
- STEP-01 root-cause evidence in workspace `04_findings.md`
- STEP-02 design verdict in workspace `04_findings.md`

Expected Outputs:
- Focused source changes and regression tests

Done Condition:
Focused tests pass and existing unrelated changes remain untouched.

Notes / Constraints:
- Use advisory checks only for GAT source payload drift; retain strict checks for target patch preconditions and installed state.

Workspace Actions:
- Record implementation summary and test results.

### Step: STEP-04 — Verify, Capture, and Hand Off

Objective:
Run focused and proportionate broader checks, perform the final capture sweep, and provide safe recovery commands for the current local installation.

Recommended Mode:
Reviewing

Applicable Guidelines:
- .ai-work/procedural/wiki_candidate_capture_playbook.md

Recommended Skills:
- aiws-aip

Inputs:
- Implemented changes
- Installer test suite
- Current target/profile state

Expected Outputs:
- Verification evidence, capture sweep summary, and final handoff

Done Condition:
Task-scoped lint has zero errors, focused tests pass, unresolved blockers are reported, and the user has an actionable path to start `dsh web`.

Notes / Constraints:
- Do not mutate `/home/hoinv/deepseek-harness` or `~/.dsh` without required authorization.

Workspace Actions:
- Finalize findings, output, and capture inbox.

## Done Criteria

- [ ] Root cause is demonstrated from current source and filesystem state.
- [ ] The proposed spec has an explicit accept/revise/reject verdict with reasons.
- [ ] The implemented fix preserves compatibility and post-install safety gates.
- [ ] Installer regression tests cover modified source, supported/unverified targets, and installed entrypoint readiness.
- [ ] Gate U1 confirmation evidence is recorded.
- [ ] Gate U2 input understanding is recorded.
- [ ] Gate U3 open points are resolved, deferred, or rejected.

## Self-check / Review Points

- Run installer tests and package-focused tests/build checks.
- Run `git diff --check` on touched files.
- Run `python3 .ai-work/tooling/lint_all.py --scope task` with this AIP and workspace.
- Reinspect all symlink destinations and package entrypoints before proposing target repair.

## Finalization Notes

- Preserve pre-existing worktree changes and clearly separate them in the final report.

## Pre-flight Pending Captures

- [IMPORTED 2026-09-13] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md" lookup_query="installer version compatibility refactor" reason="Reusable installer compatibility specification is not registered in the project Wiki index"

## Re-plan Rule

If scope, objective, or expected outputs change, append a dated Re-plan Log entry before editing earlier sections and verify no stale wording remains.

## Re-plan Log

- (no re-plan yet)
