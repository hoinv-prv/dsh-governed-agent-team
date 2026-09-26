---
artifact_type: aip_exec
artifact_id: AIP-EXEC-006
title: "Update GAT architecture proposal from council review"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
plan_source: "Direct HUMAN task task-1"
template_source: AIP_EXEC_TEMPLATE
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal
updated_at: 2026-09-13
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_EXEC — Update GAT architecture proposal from council review

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — Universal Gates áp cho mọi task substantive:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — HUMAN supplied task-1 and explicitly instructed execution; evidence to be recorded in workspace.
- **Gate U2 Confirm-understanding-of-input (soft)** — proposal and council report are summarized below.
- **Gate U3 Open Points tracking (soft)** — product-policy choices remain tracked in workspace `05_open_questions.md`.

## Objective
Revise `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md` so it responds traceably to council findings F1–F11, preserves the proposal's validated strengths, makes unresolved product decisions explicit, and is suitable for a newly pinned independent review.

## Selected Task Lens / Mode
- Lens: design_review
- Reason: The task converts a substantive architecture review into a revised design proposal.
- Search/execution effect: Prioritize canonical architecture/workspace boundaries, the reviewed proposal, and the council finding ledger.
- Resolved references: Canonical Architecture Design MVP, proposal, and council report are resolved below.
- Deferred lookups: Canonical Workspace Boundary Spec path is supplied by the council report and must be verified through lookup before use.
- Expansion allowed: yes — only when correctness requires it and all wiki-first gates are followed.

## Execution Scope
### In Scope
- Address F1–F11 in the proposal with normative boundaries, schemas, mappings, lifecycle rules, authority, and executable acceptance vectors.
- Distinguish present DSH capabilities from proposed compatibility-layer or future capabilities.
- Add revision traceability and keep the revised proposal inactive pending re-review and HUMAN activation.

### Out of Scope
- Implementing the proposal in DSH or this plugin.
- Modifying `.ai-work/truth/` or official Wiki/canonical content.
- Approving, activating, merging, or deploying the proposal.
- Silently deciding product-policy choices that require HUMAN authority.

## Expected Outputs
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/11_output_final.md`
- Workspace findings, open-point, and capture evidence under `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/`

## Execution Input Package
### Plan Source
- Shared task `task-1`, plus direct HUMAN instruction to execute it.

### Required Truth Inputs
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Workspace_Boundary_Spec_MVP.md`

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| I-01 Existing GAT proposal | (none) | `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md` | Reusable implementation proposal is not registered in lookup results | [retrieval_gap] |
| I-02 Council review report | (none) | `/home/hoinv/work/advisor_workspace/TASK-1_COUNCIL_REVIEW_REPORT.md` | One-off advisory review supplied by HUMAN task | — |
| I-03 Architecture Design MVP routing result | `SRC-METHOD-methodology-10-design-architecture-design-mvp-md-994c` | `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md` | Canonical Truth artifact; declared above for authority | — |

### Reference lookup
- Query performed: `Governed Agent Team proposal architecture`; no project-specific proposal source matched, and the top score was explicitly fragile.
- Index miss for the reusable proposal is recorded as a pending retrieval-gap capture below.

### Required Workspace Preconditions
- [ ] Workspace created by `run_aip.py start`
- [ ] Active Step Context available
- [ ] `05_open_questions.md` initialized

## Input Understanding

| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| Existing GAT proposal | Separates SoT from reference memory; proposes persistent agents, reusable teams, Desks, missions/tasks/runs, scoped MCP memory | Validated strengths should remain | Several terms and capabilities conflict with canonical/current DSH behavior | HUMAN requested revision |
| Council report | Verdict BLOCKED; requires closing F1–F11 and a new hash/review | Findings are advisory but are the revision requirements for task-1 | Product/authority/provider/retention choices are intentionally left to HUMAN | HUMAN supplied as task input |

## References to Read First
- `AGENTS.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Workspace_Boundary_Spec_MVP.md`
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `/home/hoinv/work/advisor_workspace/TASK-1_COUNCIL_REVIEW_REPORT.md`

## Current Risks / Constraints
- Council findings contain policy choices without an authoritative selected option; safe defaults may be drafted only if HUMAN approves them.
- The report is advisory and cannot activate the proposal.
- The current shell sandbox backend is unavailable; required Python tooling needs explicit wider-mode approval.
- Operating Memory was read before step design and contained no relevant entries.

## Known Open Points
- Exact durable scope term and AgentDesk continuity key.
- Working AIP cardinality and whether any bypass exists.
- Authorization decision owner, precedence, and revocation semantics.
- Whether cross-scope promotion exists in MVP.
- Retrieval baseline/provider and third-party handling.
- Tenant namespace, retention/deletion, audit integrity/readers, DSH compatibility target, gate ownership, and HUMAN authority matrix.
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/05_open_questions.md`

## Workspace Execution Rule
All runtime findings, metrics, decisions, progress, drafts, and capture candidates live in the Task Workspace, not in this AIP.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Record that task-1 requires revising the named proposal against the supplied council report without implementation or activation.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `AGENTS.md`
- wiki:none — project-specific GAT proposal lookup returned no match.

Recommended Skills:
- (none — direct confirmation evidence)

Inputs:
- Direct HUMAN instruction to execute task-1
- Shared task `task-1`

Expected Outputs:
- Task-understanding and confirmation evidence in workspace findings

Done Condition:
HUMAN intent is explicit enough to begin analysis; unresolved product-policy choices remain open rather than silently inferred.

Notes / Constraints:
- Confirmation of the task does not imply approval of unspecified architecture policy choices.

Workspace Actions:
- Record request and confirmation evidence.

### Step: STEP-01 — Resolve Canonical Boundaries and Product Decisions
Objective:
Verify canonical architecture/workspace requirements, map F1–F11 to concrete changes, and obtain HUMAN decisions for blocking product-policy choices.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `AGENTS.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Workspace_Boundary_Spec_MVP.md`

Recommended Skills:
- (none — governed analysis and HUMAN decision gate)

Inputs:
- Existing proposal
- Council report F1–F11
- Canonical architecture and workspace boundary

Expected Outputs:
- Finding-to-change matrix in workspace
- Open-point decisions or explicit conservative assumptions approved by HUMAN

Done Condition:
Every F1–F11 item has an intended disposition and all activation-blocking choices are resolved by HUMAN.

Notes / Constraints:
- No proposal mutation before blocker decisions are resolved.

Workspace Actions:
- Update `04_findings.md` and `05_open_questions.md`.

### Step: STEP-02 — Revise Proposal
Objective:
Apply the approved dispositions to the proposal with normative schemas, lifecycle rules, DSH mapping, and revision traceability.

Recommended Mode:
Executing

Applicable Guidelines:
- `AGENTS.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `.ai-work/truth/canonical/methodology/20_specs/Workspace_Boundary_Spec_MVP.md`

Recommended Skills:
- (none — direct document authoring)

Inputs:
- Approved finding-to-change matrix
- Existing proposal

Expected Outputs:
- Revised `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- Draft output copy/summary in workspace

Done Condition:
Proposal text closes F1–F11 traceably, introduces no silent activation, and clearly labels current, MVP, and future capabilities.

Notes / Constraints:
- Do not modify Truth or Wiki artifacts.

Workspace Actions:
- Record change trace and validation observations in workspace.

### Step: STEP-03 — Verify and Independently Review
Objective:
Run proposal-specific checks and task-scoped lint, then obtain a fresh read-only review against F1–F11.

Recommended Mode:
Review

Applicable Guidelines:
- `AGENTS.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

Recommended Skills:
- (none — document verification and independent reviewer)

Inputs:
- Revised proposal
- Council report
- Workspace evidence

Expected Outputs:
- New SHA-256
- F1–F11 closure matrix
- Exact lint outcome
- Independent review verdict

Done Condition:
All declared checks have evidence; remaining warnings/risks are reported honestly; proposal remains pending HUMAN acceptance and new council review.

Notes / Constraints:
- Independent review does not equal HUMAN approval or activation.

Workspace Actions:
- Write verification and review evidence to workspace.

### Step: STEP-04 — Final Capture Sweep and Delivery
Objective:
Complete the mandatory capture sweep and prepare the final deliverable report.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/procedural/wiki_candidate_capture_playbook.md`
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`

Recommended Skills:
- (none)

Inputs:
- `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/04_findings.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/05_open_questions.md`
- `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/08_capture_inbox.jsonl`

Expected Outputs:
- Updated capture inbox and closing summary
- Final output report

Done Condition:
Capture sweep, status check, scoped lint, and deliverable presentation are complete.

Notes / Constraints:
- Captures are candidates only; no direct Wiki promotion.

Workspace Actions:
- Update `08_capture_inbox.jsonl`, `04_findings.md`, and `11_output_final.md`.

## Done Criteria
- [ ] Proposal addresses F1–F11 with traceable dispositions.
- [ ] Working AIP and canonical Task Workspace are normative execution prerequisites.
- [ ] Authorization, promotion, memory lifecycle, audit, and retrieval capability contracts are implementable and deny-safe.
- [ ] DSH current/future capability mapping is explicit.
- [ ] Acceptance vectors are executable and have exact expected outcomes.
- [ ] Proposal has a new hash and remains inactive pending fresh review and HUMAN activation.
- [ ] Gate U1 evidence, Input Understanding, and all open-point dispositions exist in workspace.
- [ ] Task-scoped lint completes and its exact result is reported.

## Self-check / Review Points
- Preserve validated SoT/reference separation and concurrency guardrails.
- Check terminology against canonical Workspace meaning.
- Check every normative `MUST` has an owner, input, outcome, and evidence path where applicable.
- Search for stale claims that semantic retrieval or per-member runtime routing is already shipped.
- Obtain independent read-only review after editing.

## Finalization Notes
- Do not claim council PASS; request a new review against the new pinned hash.

## Pre-flight Pending Captures
- [IMPORTED 2026-09-13] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md" lookup_query="Governed Agent Team proposal architecture" reason="Reusable implementation proposal is a structural architecture reference but was not registered in wiki lookup results"

## Re-plan Rule
If macro scope, objective, or expected outputs change, append a dated Re-plan Log entry before editing earlier sections; runtime state remains in the workspace.

## Re-plan Log
### 2026-09-13 — Target-spec attribution reconciliation
- Trigger: Final attribution check found `AIP-EXEC-006` named in the revised proposal.
- Change: Recorded that this AIP landed the HUMAN-approved Conservative MVP rewrite addressing F1–F11; no macro scope/objective/output change occurred during execution.
- Evidence ref: `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md` SHA-256 `c682b65579ea9962ff8bfd819255c31c180bf3ac52df3ddcf7ae690ebf999652`; workspace `04_findings.md`.
- Approved by: HUMAN selected Conservative MVP; independent review PASS is advisory only.
