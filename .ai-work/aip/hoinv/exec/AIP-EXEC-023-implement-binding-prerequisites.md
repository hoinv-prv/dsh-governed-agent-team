---
artifact_type: aip_exec
artifact_id: AIP-EXEC-023
title: "Implement DSH host and authority prerequisites for GAT binding"
status: done
project: dsh-governed-agent-team
owner: hoinv
plan_source: "Explicit HUMAN authorization on 2026-10-04 for prerequisite implementation supporting AIP-EXEC-022"
template_source: AIP_EXEC_TEMPLATE
related:
  - AIP-EXEC-022
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20261004-exec-023
updated_at: 2026-10-04
---

<!-- Stable macro-control. Runtime findings/evidence live in the workspace. Approved source work excludes deployment and canonical/Truth promotion. -->

# AIP_EXEC — Implement DSH host and authority prerequisites for GAT binding

## Governance Note

HUMAN explicitly authorized creation and execution, separate DSH worktree based on c291e7961a515f6d7af9304e7fd1d257929aef26, reserved admission/recovery, refresh before rendering, exact mission/task authority and nested capabilities, design-before-code, preservation of dirty work, and Luna for simple tasks. This accepts the preceding concrete prerequisite handoff as Gate U1 evidence; no repeated permission is required for those actions. Deployment remains separately approved.

The executor owns changes only in the new DSH worktree and affected GAT design/source integration. Read each repository's AGENTS.md before editing. Formal GAT design is project draft; freeze and Truth are unchanged. Official Wiki promotion, contract changes, merges, releases, deployment/profile activation and live reload are outside this authorization. If an implementation conflicts with the freeze or existing design, stop the conflicting part and ask HUMAN after bounded lookup.

## SOP Compliance

- Gate U1: retain the exact HUMAN authorization and approved baseline in STEP-00 workspace evidence.
- Gate U2: retain input understanding and source/design qualification evidence.
- Gate U3: track and conclude all open questions before closure.
- Local SOP/Contract placeholders provide no task-specific text; use project rules and explicit HUMAN scope, without rewriting Truth.

## Objective

Deliver qualified prerequisite source and exported APIs for AIP-EXEC-022: controlled reserved direct-continuable child staging/persistence/activation/recovery; awaited current context refresh before every request's prompt rendering; host-attested HUMAN mission/member approval and exact scoped canonical-task execution leases; immutable capability classification checked at each direct, aliased and nested tool dispatch. Keep existing unrelated DSH/GAT behavior compatible, prove denials before effects, and hand off exact design/source/build evidence for binding integration without deployment.

## Selected Task Lens / Mode

- Lens: No-Lens.
- Reason: the frozen contract and prior handoff determine this implementation's inputs.
- Resolved references: frozen contract, formal GAT design, prior AIP/qualification, DSH AGENTS/architecture/defensive patterns at the approved baseline.
- Deferred lookups: owning subsystem/SDK/session documentation and package gates referenced by inspected DSH code, resolved at STEP-01.
- Expansion allowed: yes for affected consumers and correctness; macro scope change requires Re-plan Log.

## Execution Scope

### In Scope

- docs/gat-design/ — intended prerequisite delta before source, final qualification and mappings.
- packages/core/ — exact mission/task authority, host attestation/lease ownership and required bridge to host APIs.
- packages/tools/ — immutable GAT capability policy and effect/model admission checks; preserve static labels and existing dirty patches.
- /home/hoinv/work/dsh-binding-prerequisites/ — approved isolated host source, docs, tests, generated API/SDK evidence, package consumers and necessary adjacent event adapters.
- .ai-work/workspaces/hoinv/TASK-20261004-exec-023/ — baseline, decisions, per-step ASC snapshots, traces, tests, captures and handoff.
- Supported deterministic keyless composition tests; disposable provider storage and installer verification when needed.

### Out of Scope

- Changes to the original dirty DSH checkout, resetting existing GAT edits or storage deletion as compensation.
- Isolated-execution migration, official Durable Consumer substitution, model-visible confirmed-memory commit authority.
- New WBS mission execution, user credential setup, live deployment/activation, publication, merging, live reload or incident Session reuse.
- Silent canonical/Truth/wiki/freeze rewrites; compatibility bypass or weakening required attachment/authority enforcement.

## Expected Outputs

- docs/gat-design/DETAIL_DESIGN.md — intended/current prerequisite design with exact ownership, admission, persistence and failure semantics; affected architecture/basic/integration/maps updated.
- /home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md — extension point and loop ordering documentation plus owning subsystem/package docs, bilingual pairs and Agent Note.
- /home/hoinv/work/dsh-binding-prerequisites/packages/ — host implementations and focused regression/conformance tests, exported built-path evidence and affected consumers.
- packages/core/ — exact mission/task lease source/tests and host integration fixtures.
- packages/tools/ — capability policy integration/tests and safe summaries as affected.
- .ai-work/workspaces/hoinv/TASK-20261004-exec-023/ — baseline.md/json, authorization.md, design-delta.md, source-design-test-matrix.md, conformance.md, verification/, independent-review.md and prerequisite-handoff.md.

## Execution Input Package

### Plan Source

- HUMAN request on 2026-10-04, Asia/Tokyo, expressly authorizing the prerequisite handoff proposed for AIP-EXEC-022.

### Required Truth Inputs

- .ai-work/truth/SOP_MASTER.md and .ai-work/truth/AI_WORK_CONTRACT.md (no task-specific content at preflight; never fill silently).
- .ai-work/truth/canonical/methodology/20_specs/AIP_Detail_Spec_MVP.md.

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Use | Capture flag |
|---|---|---|---|---|
| Frozen contract | SRC-GAT-MEMBER-BINDING-FREEZE | docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md | §§7–14 ordering, authority, capabilities, conformance | — |
| Detail design | SRC-GAT-DETAIL-DESIGN | docs/gat-design/DETAIL_DESIGN.md | DD-01–03/06–11/16–17, §§5–6 | — |
| Architecture | SRC-GAT-ARCHITECTURE-DESIGN | docs/gat-design/ARCHITECTURE_DESIGN.md | Current ownership and intended extensions | — |
| Basic design | SRC-GAT-BASIC-DESIGN | docs/gat-design/BASIC_DESIGN.md | Mission/task and required binding behaviors | — |
| Durable integration | SRC-GAT-DURABLE-INTEGRATION-DESIGN | docs/gat-design/DURABLE_AGENT_INTEGRATION.md | Approved WK/direct target and host prerequisites | — |
| Proposal | (unregistered) | docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md | Selected baseline and acceptance map | [retrieval_gap] |
| DSH architecture | (unregistered) | /home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md | Host loop, extension points and model-visible logging | [retrieval_gap] |
| DSH defensive patterns | (unregistered) | /home/hoinv/work/dsh-binding-prerequisites/docs/defensive-patterns.md | Lifecycle and teardown invariants | [retrieval_gap] |
| AIP template | (unregistered) | .ai-work/aip/templates/AIP_EXEC_TEMPLATE.md | Stable control structure | [retrieval_gap] |

### Reference lookup

- Lexical then semantic lookup for new specification inputs; existing AIP-resolved paths may open directly while running.
- Proposal/template and DSH architecture/defensive docs did not resolve in registered lookup; use the named/AGENTS-linked paths after documented escalation. Scoped raw source/design search in the approved worktree is authorized by this implementation and STEP-01.
- Primary GAT metas were read; freshness is checked against actual source rather than trusted stale navigation summaries.

### Required Workspace Preconditions

- [ ] AIP strict validation passes; workspace/ASC pointer established and read.
- [ ] Original dirty trees and selected clean worktree baseline recorded before source changes.
- [ ] Intended design and file ownership are established before source delegation.

## Input Understanding

| Input | Understanding | Assumption / decision |
|---|---|---|
| HUMAN authorization | External implementation is expressly approved; deployment separate | Approved revision and direct-continuable/WK target remain fixed |
| Freeze §§7–9 | Durable quarantined initial item and explicit release/recovery; legacy wrapper compatible | Provider/journal failures and races must be independently observed |
| Freeze §10 | HUMAN provenance cannot come from model args; exact mission/task revision checked at each effect and wake | Lead can create drafts but not self-authorize; canonical task carries immutable missionId |
| Freeze §11 | Reserved external-delegation capability is immutable and nested union checks deny before effects | Keep name fallback during metadata rollout; disabled Team behavior preserved |
| DSH rules | Plugins/effects own behavior; loop changes update architecture; model-visible content logged | Document new events and affected SDK views; no released data rewrite |

## References to Read First

- AGENTS.md and .ai-work/AIWS.local.md.
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md and docs/gat-design/DETAIL_DESIGN.md.
- .ai-work/aip/hoinv/exec/AIP-EXEC-022-implement-durable-agent-binding.md.
- .ai-work/workspaces/hoinv/TASK-20261004-exec-022/dependency-qualification.md and implementation-handoff.md.
- /home/hoinv/work/dsh-binding-prerequisites/AGENTS.md, packages/AGENTS.md and docs/AGENTS.md.
- /home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md and docs/defensive-patterns.md.

## Current Risks / Constraints

- Baseline DSH APIs merge materialization and initial submission; recovery must not accidentally release work through legacy consumers.
- Authority is owned in GAT and attested by trusted host APIs; a string/token supplied by a model cannot become HUMAN provenance.
- Registrations and nested dispatch must retain immutable owner classification through wrappers and asynchronous context; check at the operation that makes the effect.
- Reserved-child and prompt refresh share agent-loop code; assign disjoint file regions or serialize edits.
- Existing GAT dirty source/design/tests belong to prior work; only additive scoped changes with preserved baseline hashes.
- Required callback cancellation/cleanup is bounded and observes late settlement; no duplicate install/release or fabricated success.

## Known Open Points

- Live log: .ai-work/workspaces/hoinv/TASK-20261004-exec-023/05_open_questions.md.
- OP-01: inspect exact persistence/agent generation operations and declare new event/version semantics before source.
- OP-02: qualify actual trusted HUMAN ingress and canonical task/plan revision inputs; no implicit list-order selection.
- OP-03: supported packaging of the new DSH revision is a later qualification, not current baseline eligibility.

## Workspace Execution Rule

Read ASC before step work; keep runtime progress in workspace, snapshot each step context, capture reusable findings immediately, and rebuild ASC on pointer moves. Never tick AIP Done Criteria or embed test counts here.

## Execution Steps

### Step: STEP-00 — Record approved scope and protected baselines (HARD GATE)
Objective:
Record the exact HUMAN authorization and protected source/worktree identity.
Recommended Mode:
Clarifying
Applicable Guidelines:
- .ai-work/procedural/skills/aiws-aip/operations/run.md
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
Inputs:
- Explicit HUMAN request and input package above
Expected Outputs:
- authorization.md and baseline.md/json in workspace
Done Condition:
Approved scope and revision, dirty-file hashes and no-deployment constraint are recorded; no new confirmation is needed for this already-approved handoff.
Notes / Constraints:
- Do not infer changes to frozen decisions; deployment remains separate.
Workspace Actions:
- Retain exact HUMAN text and baseline receipts.

### Step: STEP-01 — Resolve host contracts and write intended design
Objective:
Inspect affected host/core/tools consumers and update formal intended design and owning DSH design before any source change.
Recommended Mode:
Design-authoring
Applicable Guidelines:
- AGENTS.md
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
- /home/hoinv/work/dsh-binding-prerequisites/docs/AGENTS.md
Inputs:
- baseline.md, authorization.md and resolved specification inputs
Expected Outputs:
- design-delta.md and source-design-test-matrix.md in workspace; intended formal GAT/DSH design
Done Condition:
Exact APIs, admission/recovery events, refresh ordering, authority and capability semantics are consistent with freeze; source file ownership declared.
Notes / Constraints:
- Conflicting decisions stop only affected work. No source-before-design; no canonical promotion.
allow_raw_search: true
Workspace Actions:
- Record design locators and delegation ownership before coding.

### Step: STEP-02 — Implement reserved admission and cold recovery
Objective:
Provide durable materialize/persist-only/activate/abort/dispose and recover-before-release with stable states/errors and legacy wrapper compatibility.
Recommended Mode:
Executing
Applicable Guidelines:
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
- /home/hoinv/work/dsh-binding-prerequisites/AGENTS.md
Inputs:
- design-delta.md and source-design-test-matrix.md
Expected Outputs:
- Reserved lifecycle source/tests and success/failure/concurrency/restart traces in conformance.md
Done Condition:
No initial inbox/model work on materialize; one durable quarantined item; tombstone before abort; exact idempotency conflicts; cold resume cannot bypass recovery or duplicate initial item.
Notes / Constraints:
- Stable direct child/provider ownership and one-generation installation. Existing unrelated consumers retain wrapper behavior.
Workspace Actions:
- Save commands/traces and per-step output metadata.

### Step: STEP-03 — Implement refresh before request rendering
Objective:
Provide awaited owner-scoped refresh before each actual prompt rendering with explicit logged contributions, bounded replacement and failure/cutoff semantics.
Recommended Mode:
Executing
Applicable Guidelines:
- /home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
Inputs:
- design-delta.md and STEP-02 conformance.md
Expected Outputs:
- Prompt/request source/tests and coherent logged refresh fixtures in conformance.md
Done Condition:
Refresh precedes rendered/provider-visible requests, replacement remains bounded, errors deny dispatch, disposed owners cannot publish late context, unrelated assembly remains intact.
Notes / Constraints:
- No post-render request hook substitution. Update public events/docs/SDK expected views when affected.
Workspace Actions:
- Retain refresh ordering and async cutoff evidence.

### Step: STEP-04 — Implement exact HUMAN mission/task execution authority
Objective:
Provide host-attested approval, canonical task mission association and opaque exact scoped leases revalidated before effects and model wake.
Recommended Mode:
Executing
Applicable Guidelines:
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
- docs/gat-design/DETAIL_DESIGN.md
Inputs:
- design-delta.md and conformance.md from STEP-02/03
Expected Outputs:
- GAT authority source/tests and exhaustive lease/exemption denial matrix in conformance.md
Done Condition:
Model-created mission remains draft; missing/ambiguous/wrong/stale/revoked/closed approvals deny effects; structural changes invalidate lease; both simpleMode modes enforce their required HUMAN approval; queued/bootstrap operations never imply model wake.
Notes / Constraints:
- Lease stored in exact scope, not model JSON. Read-only/control exemptions never widen descendant effects.
Workspace Actions:
- Save independent durable approval/task/dispatch observations.

### Step: STEP-05 — Implement immutable nested capability enforcement
Objective:
Propagate captured capability metadata and descendant union through all current tool/delegation dispatch paths with executor enforcement.
Recommended Mode:
Executing
Applicable Guidelines:
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
- /home/hoinv/work/dsh-binding-prerequisites/packages/AGENTS.md
Inputs:
- design-delta.md and source-design-test-matrix.md
Expected Outputs:
- Tool registry/delegator source/tests and named/aliased/nested denial fixtures in conformance.md
Done Condition:
Enabled Team denies external delegation before provider/child/events; aliases/wrappers cannot remove reserved classification; each nested boundary checks metadata; disabled Team behavior and name fallback remain compatible.
Notes / Constraints:
- Test actual executor routes, not schema omission. Capability registration and disposal use Cordis effects.
Workspace Actions:
- Bind fixture outcomes to exact registrations and side-effect counters.

### Step: STEP-06 — Qualify exported integration and independent review
Objective:
Exercise real host plus GAT lifecycle/authority/capability composition, affected builds/docs/SDK gates, and independent substantive review.
Recommended Mode:
Reviewing
Applicable Guidelines:
- docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md
- /home/hoinv/work/dsh-binding-prerequisites/AGENTS.md
Inputs:
- conformance.md, final source and affected documentation
Expected Outputs:
- verification/ reports, independent-review.md and reconciled source/design mappings
Done Condition:
Exported host APIs and actual GAT composition satisfy prerequisite matrix; focused behavior and required docs/build checks pass; substantive review has no unresolved blocker.
Notes / Constraints:
- Luna handles simple mappings/inventory; lifecycle/security review requires capable reviewer. Fix intended design before source correction.
Workspace Actions:
- Record source/build hashes, exact test commands and reviewer findings.

### Step: STEP-07 — Finalize prerequisite handoff and parent qualification inputs
Objective:
Deliver exact prerequisite revision/artifacts/evidence to AIP-EXEC-022, conclude runtime questions and lint without deploying.
Recommended Mode:
Executing
Applicable Guidelines:
- .ai-work/procedural/skills/aiws-aip/operations/run.md
- .ai-work/procedural/skills/aiws-lint/SKILL.md
Inputs:
- independent-review.md and verification/ from STEP-06
Expected Outputs:
- prerequisite-handoff.md, 11_output_final.md and parent dependency input locators
Done Condition:
Prerequisites are actually qualified, source/design synchronized, captures triaged/deferred with destinations, lint reports recorded and parent may consume exact evidence; no live activation is claimed.
Notes / Constraints:
- Parent production composition/packaging acceptance remains its own STEP-04/07/08; do not close parent from prerequisite status.
Workspace Actions:
- Final capture sweep; final lint; status check; close only after full prerequisite Done Criteria pass.

## Done Criteria

- [ ] Approved scope/baseline and protected dirty bytes recorded (Gate U1/U2).
- [ ] Reserved admission/recovery, refresh, exact authority and nested executor conformance pass with actual host observations.
- [ ] Required focused behavior, built exports, documentation, SDK/session checks pass and independent review has no unresolved implementation blocker.
- [ ] GAT and DSH design/notes/source are synchronized; no released session generation rewritten.
- [ ] Open questions concluded (Gate U3); captures have recorded HUMAN-controlled disposition and lint results are reported accurately.
- [ ] Exact prerequisite handoff provided to AIP-EXEC-022; deployment remains unperformed.

## Self-check / Review Points

- Check child generation, initial item count and durable flush ordering independently from callback traces.
- Check HUMAN provenance cannot be fabricated by model arguments; stale/revoked task/mission scopes deny immediately before actual effects.
- Check nested capability denial via current provider/dispatcher paths and union metadata; keep strict name fallback.
- Check final source hashes, exported artifacts and actual loaded test modules separately; no live reload evidence inferred.
- Preserve original dirty trees and prior AIP findings; no misleading upstream ordinal acceptance labels.

## Finalization Notes

Finalize only after full prerequisite conformance and independent review, with exact design/source/test evidence. Package publication/deployment/activation is separately authorized. Close uses run_aip ceremony and capture disposition, never a hand-edited status.

## Pre-flight Pending Captures

- [IMPORTED 2026-10-04] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md" lookup_query="DURABLE_AGENT_BINDING_PROPOSAL" reason="Proposal remains unregistered after lexical/semantic escalation; use explicit reviewed source path."
- [IMPORTED 2026-10-04] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="/home/hoinv/work/dsh-binding-prerequisites/docs/architecture.md" lookup_query="DSH architecture defensive patterns" reason="External host architecture/defensive documents absent from registered lookup; AGENTS explicit pointers used after escalation."
- [IMPORTED 2026-10-04] type="aip_template_improvement_candidate" candidate_kind="retrieval_improvement" suggested_target="aip_template" artifact=".ai-work/aip/templates/AIP_EXEC_TEMPLATE.md" lookup_query="AIP_EXEC_TEMPLATE" reason="Installed template path used after lexical/semantic lookup did not locate that artifact."

## Re-plan Rule

Append dated Re-plan Log entry before macro scope/output changes; retain approval and workspace evidence; sweep superseded wording across all control sections. Runtime state stays outside this AIP.

## Re-plan Log

- (no re-plan yet)
