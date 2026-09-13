---
artifact_type: aip_exec
artifact_id: AIP-EXEC-001
title: "Copy Governed Agent Team source from the accepted DSH golden reference"
status: active
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "direct-human-request"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260913-exec-001
updated_at: 2026-09-13
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Copy Governed Agent Team source from the accepted DSH golden reference

## SOP Compliance
- **Gate U1:** HUMAN explicitly requested `copy source sang /home/hoinv/work/dsh-governed-agent-team` and selected AIWS account namespace `hoinv`.
- **Gate U2:** Source, destination mapping, exclusions, and provenance are recorded below.
- **Gate U3:** Runtime open points are tracked in workspace `05_open_questions.md`.

## Objective
Create a provenance-preserving source snapshot of the five accepted Governed Agent Team packages in the standalone repository, copied only from the immutable golden-reference worktree at exact HEAD `12fef7a7e01f6c3ba7ecab0929355659b3370435`.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: bounded, deterministic tracked-file migration with an exact source commit and destination mapping.
- Search/execution effect: use the registered source-representation migration reference plus direct Git inventory/hash evidence.
- Resolved references: source representation migration report template.
- Deferred lookups: none.
- Expansion allowed: no, except prerequisite repository rules and verification tooling.

## Execution Scope
### In Scope
- Copy tracked files from these golden-reference packages:
  - `packages/experimental/agent-team` → `packages/core`
  - `packages/experimental/tool-agent-team` → `packages/tools`
  - `packages/experimental/client-ui-agent-team` → `packages/web`
  - `packages/experimental/agent-team-profile` → `packages/profile`
  - `packages/experimental/agent-team-web-profile` → `packages/web-profile`
- Preserve file bytes and executable bits.
- Copy the accepted GAT design document into `docs/golden-reference/` when tracked at the declared source path.
- Write a machine-readable source snapshot inventory with source commit, mapping, per-file SHA-256, and package-level aggregate SHA-256.
- Write a concise extraction/provenance note that explicitly says this step does not create an installer, compatibility patchset, standalone build wiring, release, or compatibility claim.

### Out of Scope
- Modifying the main DSH checkout or golden-reference worktree.
- Renaming package identities/imports to `@vuhoi/gat-*`.
- Creating or claiming an official compatibility manifest, host patchset, installer, standalone build, or successful installation.
- Copying `.hermes/`, `.superpowers/`, `node_modules/`, build output, coverage, caches, or untracked files.
- Commit, push, merge, tag, publish, release, provider/API access, or production activation.

## Expected Outputs
- `packages/core/`
- `packages/tools/`
- `packages/web/`
- `packages/profile/`
- `packages/web-profile/`
- `docs/golden-reference/2026-09-12-governed-agent-team-v1-design.md`
- `docs/source-extraction.md`
- `SOURCE_SNAPSHOT.json`

## Execution Input Package
### Plan Source
- Direct HUMAN request in the current chat, following the previously approved separate-repository architecture.

### Required Truth Inputs
- `AGENTS.md`
- `.ai-work/truth/SOP_MASTER.md` (empty project placeholder)
- `.ai-work/truth/AI_WORK_CONTRACT.md` (empty project placeholder)

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| Source Representation Migration Report Template | SRC-METHOD-methodology-30-templates-source-representation-migration-report-template-md-1501 | `.ai-work/truth/canonical/methodology/30_templates/Source_Representation_Migration_Report_Template.md` | Used only to structure provenance and caution notes | — |

### Reference lookup
- Executed: `python .ai-work/tooling/lookup_wiki_source.py --query "copy migrate DeepSeek Harness governed agent team plugin source"`.
- The returned migration-template source was opened through `wiki_meta.py` and its canonical artifact path.

### Required Workspace Preconditions
- Workspace created by `run_aip.py start`.
- Active Step Context read before source mutation.
- Open-points log available.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| HUMAN request | Copy GAT source to the standalone repo now | “source” means exact tracked package snapshot, not a finished port/install | None blocking; destination mapping was previously approved | ✅ direct request |
| Golden-reference worktree | Accepted implementation source at exact immutable HEAD | Only tracked files are authoritative for copy | None | ✅ established context |
| Migration template | Requires scope, locator interpretation, status, deferred items, and rollback caution | A concise project note is sufficient | None | not required |

## References to Read First
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/create.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `.ai-work/truth/canonical/methodology/30_templates/Source_Representation_Migration_Report_Template.md`

## Current Risks / Constraints
- The copied package manifests and imports remain DSH-native; this snapshot is not yet an independently buildable `@vuhoi/gat-*` workspace.
- Cross-cutting DSH host changes are intentionally not copied into package directories; a later compatibility extraction must classify and create the exact versioned patchset.
- Byte-for-byte verification must use tracked source inventory at the exact golden HEAD.
- No credentials, API keys, tokens, passwords, or connection strings may be retained; any encountered value must be represented as `[REDACTED]`.

## Known Open Points
- Open Points log: `.ai-work/workspaces/hoinv/{TASK-ID}/05_open_questions.md`
- No blocking open points at creation time.

## Workspace Execution Rule
Runtime findings, metrics, progress, open questions, and final output live in the task workspace, not in this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record the exact source, destination, five-package mapping, exclusions, and success definition.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `AGENTS.md`
- wiki:none — the HUMAN request and repository rules fully define this bounded execution gate.

Recommended Skills:
- `superpowers:brainstorming` (prior design approval already exists; no new design decision in this copy step)

Inputs:
- Current HUMAN request
- Established golden-reference and standalone-repo architecture

Expected Outputs:
- Task-understanding note and HUMAN confirmation evidence in workspace

Done Condition:
The direct request and account-id reply provide explicit execution confirmation, with no unresolved scope blocker.

Notes / Constraints:
- Do not broaden “copy source” into package renaming, installer creation, DSH patching, or release.

Workspace Actions:
- Record confirmation evidence in workspace findings.

### Step: STEP-01 — Inventory and copy tracked GAT files
Objective:
Copy only Git-tracked files from the five exact source package directories into the approved destination mapping, preserving bytes and executable bits.

Recommended Mode:
Executing

Applicable Guidelines:
- `AGENTS.md`
- `.ai-work/truth/canonical/methodology/30_templates/Source_Representation_Migration_Report_Template.md`

Recommended Skills:
- direct deterministic file migration

Inputs:
- Golden worktree at `12fef7a7e01f6c3ba7ecab0929355659b3370435`
- Five-package source/destination mapping

Expected Outputs:
- Five populated package directories
- Copied golden-reference design document

Done Condition:
Every tracked source file in scope exists at its mapped destination and no excluded/untracked path is copied.

Notes / Constraints:
- Refuse if golden HEAD differs.
- Refuse if a destination package directory already contains files.
- Do not mutate either DSH checkout.

Workspace Actions:
- Record source and destination inventory counts in findings.

### Step: STEP-02 — Materialize provenance records
Objective:
Create machine-readable checksums and a human-readable extraction note without implying standalone compatibility.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/30_templates/Source_Representation_Migration_Report_Template.md`

Recommended Skills:
- direct documentation and checksum generation

Inputs:
- Copied package tree
- Exact Git-tracked source inventory

Expected Outputs:
- `SOURCE_SNAPSHOT.json`
- `docs/source-extraction.md`

Done Condition:
Records identify exact source commit, package mappings, per-file SHA-256, aggregate hashes, limitations, and rollback scope.

Notes / Constraints:
- Do not create `compatibility/**/manifest.yml`; that filename is reserved for a later verified installer contract.

Workspace Actions:
- Record generated artifact paths in findings.

### Step: STEP-03 — Verify copy integrity and repository scope
Objective:
Prove byte identity, expected counts, absence of excluded paths, unchanged source worktree, and bounded destination changes.

Recommended Mode:
Verifying

Applicable Guidelines:
- `AGENTS.md`

Recommended Skills:
- `superpowers:verification-before-completion`

Inputs:
- Source inventory and `SOURCE_SNAPSHOT.json`
- Git status from source and destination repositories

Expected Outputs:
- Fresh verification transcript and final status in workspace

Done Condition:
All source/destination SHA-256 pairs match; aggregate hashes match; no forbidden path exists; golden-reference HEAD/status are unchanged; target changes are limited to declared outputs plus AIWS task artifacts.

Notes / Constraints:
- Do not claim standalone build, installability, safety, or DSH compatibility from copy integrity alone.

Workspace Actions:
- Record exact commands, exit codes, file counts, and limitations.

## Done Criteria
- [ ] Gate U1 evidence is recorded in workspace.
- [ ] The five destination package trees contain exactly the scoped tracked source files.
- [ ] Source and destination SHA-256 values match for every copied package file.
- [ ] Golden-reference design document is copied byte-for-byte.
- [ ] `SOURCE_SNAPSHOT.json` and `docs/source-extraction.md` accurately record provenance and limitations.
- [ ] `.hermes/`, `.superpowers/`, `node_modules/`, build output, coverage, caches, and untracked files are absent from copied outputs.
- [ ] Main DSH checkout and golden-reference worktree were not modified.
- [ ] No installer, compatibility manifest, patchset, commit, push, merge, tag, publish, release, provider/API call, or production activation occurred.
- [ ] Gate U3 has no unresolved blocker at close.
- [ ] Scoped AIWS lint exits with zero errors.

## Self-check / Review Points
- Confirm exact source HEAD before the first write.
- Compare inventories by relative path, byte size, executable mode, and SHA-256.
- Treat source snapshot as `partial` migration: package source copied, standalone wiring and host compatibility extraction deferred.
- Report modified paths and all limitations explicitly.

## Finalization Notes
- Completion means “source snapshot copied and integrity-verified,” not “plugin ported/installed/compatible.”

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Any change to macro scope, package mapping, expected outputs, or host patch ownership requires a dated Re-plan Log entry before execution continues.

## Re-plan Log
- (no re-plan yet)
