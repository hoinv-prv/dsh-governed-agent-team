---
artifact_type: aip_exec
artifact_id: AIP-EXEC-024
title: "Implement opt-in Durable Agent binding for isolated GAT executions"
status: active
project: dsh-governed-agent-team
owner: hoinv
plan_source: "Direct HUMAN request on 2026-10-04 to create an implementation AIP from the reviewed durable-binding-reuse proposal"
template_source: AIP_EXEC_TEMPLATE
related:
  - AIP-EXEC-022
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20261004-exec-024
updated_at: 2026-10-04
---

<!-- Stable control only. Design precedes source; runtime evidence belongs in the execution workspace. Creating this AIP does not start implementation, deploy a profile or promote canonical knowledge. -->

# AIP_EXEC — Implement opt-in Durable Agent binding for isolated GAT executions

## Governance Note

The HUMAN selected an additive isolated-execution adapter, required reference to Durable Agent design, and requested an AIP for implementation planning. This draft replaces the proposed WBS execution approach; the earlier planning documents remain reference inputs. No new WBS, Goal, worker dispatch or execution approval is created.

- STEP-00 consumes explicit execution authorization and the decisions already made in this conversation. Do not request those planning decisions again. Confirm only material new scope, effect or design conflicts.
- STEP-01 writes the intended qualification design under `docs/gat-design/` before any GAT experimental source/test changes. STEP-03 settles the production design before STEP-04 implementation. Project design amendments retain their existing authority classification; Truth/canonical, frozen-contract revisions and official Wiki changes require their applicable approved CR/review gate.
- Qualification uses the current DSH Host and WK public provider in disposable storage. Existing DSH APIs are reused; DSH core/loop/Team persistence and Durable Agent provider/source changes are excluded. A demonstrated missing capability requires a bounded owner handoff and explicit scope decision.
- Source/design changes in this repository and GAT-owned package mirrors in an explicitly selected isolated qualification Host are the intended implementation effects. Record exact destination paths, launchers and emitted build/test effects before using them; preserve unrelated dirty files. This is not a blanket write grant to a sibling checkout.
- Deployment, live Web profile activation/reload, persistent production storage initialization/migration, publication and Mission Board task10 dispatch remain separate decisions. A technical handoff can complete this AIP while deployment remains excluded.

## SOP Compliance

- Gate U1: explicit authorization to run this AIP and confirmation of its bounded implementation scope are recorded at STEP-00. The existing additive-adapter planning decision is retained as input.
- Gate U2: input understanding is declared below; actual version, package and configuration evidence is recorded in the workspace at preflight.
- Gate U3: each blocker receives a disposition in workspace `05_open_questions.md`; no blocking issue may be deferred while its dependent implementation proceeds.
- `.ai-work/truth/SOP_MASTER.md` and `.ai-work/truth/AI_WORK_CONTRACT.md` are currently empty. Preserve them; project-owned `AGENTS.md` and `.ai-work/AIWS.local.md` govern this plan, rather than inventing a task-specific SOP or approved deviation.

## Objective

Deliver `@vuhoi/gat-durable-agent/execution-composition` as an additive opt-in binding for fresh isolated current GAT task executions. Reuse the public WK Durable Agent service/Consumer and current GAT assignment/admission/settlement lifecycle. Demonstrate binding before first request, fresh Durable context at each admitted step assembly with the same prompt retained across retries within that step, exact identity and authority/service checks before every actual request including retries, assignment-selected memory reads, evidence-only reviewer context, joined cleanup and authorized live recovery. Keep the existing direct-continuable composition supported and synchronize official GAT design with the final source.

## Selected Task Lens / Mode

- Lens: No-Lens.
- Reason: the reviewed proposal and both formal design sets provide the concrete subject and acceptance set.
- Resolved references: GAT Basic/Detail/Integration/source map and member-binding freeze; DA Architecture/Basic/Detail/source map/conflicts/mission deltas; public WK service/Consumer/provider; proposal and planning review.
- Deferred lookups: exact selected Host package destinations, supported snapshot/Loader launcher and qualified public review-packet inputs; resolve at STEP-01/STEP-02.
- Expansion allowed: dependency/source inspection necessary for correctness; implementation scope changes require a dated Re-plan Log entry and the applicable HUMAN decision.

## Execution Scope

### In Scope

- Qualification of current GAT isolated execution identity, first-request ordering, step refresh/retry snapshot/logging, reviewer packet input, selected reads, cleanup and cold recovery with the real WK service/provider.
- A proposed qualification amendment followed by the reviewed production amendment in `docs/gat-design/` before dependent code changes.
- Additive source, Config, tests, public export and build entry in `packages/durable-agent/`; reuse ownership/tool components where compatible and actually shared.
- Necessary GAT-owned package mapping, dependency/export/build and package documentation changes for the new entry in an isolated selected qualification Host.
- Focused UT/IT, keyless Session-driven snapshot, existing composition regressions and built public-import/Loader evidence; exact design/source and qualification manifests.
- Independent assessment of qualification/design and final implementation; final handoff and a deployment proposal containing exact configuration, storage effects and rollback.

### Out of Scope

- DSH core/agent-loop/subagent/Team execution schema changes, a new dispatcher or second Team lifecycle, importing the older compatibility patchset wholesale, or replacing the existing initializer/roster.
- Durable Agent service/Consumer/provider/storage modifications, DSH lease API translation, provider-private path inspection, global/fork scope, new universal identity or a full Durable task runner.
- Candidate-submission and confirmed-memory model tools for this read-only integration; automatic learning promotion or memory migration.
- Live profile/GUI activation, production storage writes, deployment/publication, historical execution/evidence rewrite, WBS revision/charges/reset and Mission Board task10 assignment.
- Truth, frozen normative contracts, canonical methodology or official Wiki promotion without their applicable approved change authority.

## Expected Outputs

- `docs/gat-design/DETAIL_DESIGN.md`, `BASIC_DESIGN.md`, `DURABLE_AGENT_INTEGRATION.md` and `SOURCE_CODE_MAP.md`: attributed prospective and finalized design/source amendments.
- `packages/durable-agent/src/execution-composition.ts` and bounded implementation helpers where necessary; additive package export/build metadata and package documentation.
- `packages/durable-agent/tests/`: focused execution-composition, selected-read/reviewer and lifecycle/recovery tests; existing entry regression evidence.
- GAT-owned package/snapshot/distribution amendments at the exact qualification Host destinations settled during preflight; no broad Host patchset.
- Workspace `qualification-design.md`, `qualification-environment.json`, `qualification-matrix.md`, `qualification-review.md`, `design-review.md`, `source-review.md`, `test-matrix.md`, `source-design-consistency.md`, `implementation-handoff.md` and `verification/` receipts.
- Workspace `deployment-proposal.md`: exact proposed provider/profile/configuration, storage effects, topology evidence and rollback; no activation performed.

## Execution Input Package

### Plan Source

- Direct HUMAN instructions in this conversation: additive adapter planning direction; Durable Agent design reference requirement; use an AIP instead of a WBS.
- `wbs-runs/durable-binding-reuse/proposal-review.md` and `implementation-plan.md`: technical planning inputs; AIP step governance supersedes their proposed WBS execution approach.
- `/home/hoinv/deepseek-harness/wbs-runs/mission-board-regression-execution-02/durable-binding-reuse-proposal.md`: requested integration outcome and qualification cases; no prior mission authority transfer.

### Required Truth Inputs

- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- `AGENTS.md` and `.ai-work/AIWS.local.md`: project-owned design-first and optional-AIP policy.

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
| --- | --- | --- | --- | --- |
| GAT Basic Design | SRC-GAT-BASIC-DESIGN | `docs/gat-design/BASIC_DESIGN.md` | External capability flow and existing production delivery | — |
| GAT Detail Design | SRC-GAT-DETAIL-DESIGN | `docs/gat-design/DETAIL_DESIGN.md` | DD-09/DD-15/DD-16, §§5/7/8; existing direct-continuable scope | — |
| GAT integration | SRC-GAT-DURABLE-INTEGRATION-DESIGN | `docs/gat-design/DURABLE_AGENT_INTEGRATION.md` | WK public service ownership and opt-in boundary | — |
| GAT source map | SRC-GAT-DESIGN-SOURCE-MAP | `docs/gat-design/SOURCE_CODE_MAP.md` | Final source/design traceability | — |
| Member-binding freeze | SRC-GAT-MEMBER-BINDING-FREEZE | `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` | §§2–4/8/12; no silent contract revision | — |
| WK service | SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-SERVICE-TS | `/home/hoinv/work/dsh-durable-agent/durable-agent-plugin/src/service.ts` | API/version/features and non-cancellable public calls | — |
| WK Consumer | SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-CONSUMER-TS | `/home/hoinv/work/dsh-durable-agent/durable-agent-plugin/src/consumer.ts` | Ordinary versus explicit evidence-only review | — |
| WK provider | SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-LOCAL-PROVIDER-TS | `/home/hoinv/work/dsh-durable-agent/durable-agent-plugin/src/local-provider.ts` | Profile conflicts, ref reuse and release | — |
| DA formal design collection | none | `/home/hoinv/work/dsh-durable-agent/docs/` | Exact source set/sections listed in References; no exact collection registration found through lexical/path and semantic lookup | [retrieval_gap] |
| EXEC template | none | `.ai-work/aip/templates/AIP_EXEC_TEMPLATE.md` | Required local authoring template; exact registration not returned by path/semantic lookup | [retrieval_gap] |

### Reference lookup

- Use `python3 .ai-work/tooling/lookup_wiki_source.py --query '<subject>' --limit 5` before opening new design/spec inputs, then `wiki_meta.py --view` for registered routes. Retry semantic/tokens and bounded path search on misses.
- The DA formal documents were explicitly supplied by the HUMAN, inspected in the preceding review after wiki-first escalation, and remain external authoritative design inputs for their implementation family. No local-wiki search or official Wiki registration is implied.
- Source/API inspection verifies current package bytes rather than trusting stale metadata or historical acceptance. The create-time `source-baseline.json` is a reference manifest; recapture current exact inputs at execution preflight.

### Required Workspace Preconditions

- [ ] `aiws-aip run start` creates the per-account execution workspace and writes its provenance pointer; do not hand-stamp `runtime_workspace`.
- [ ] Read the generated Active Step Context before working on each step.
- [ ] Initialize `05_open_questions.md` and preserve immediate capture entries in `08_capture_inbox.jsonl`.
- [ ] Import and verify pending retrieval captures at start; do not promote them into Wiki automatically.

## Input Understanding

| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
| --- | --- | --- | --- | --- |
| HUMAN request and proposal | Plan an additive isolated-execution adapter; keep GAT assignment ownership | Planning is authorized; execution starts only on a run instruction | Deployment and new dependency changes need their own decisions | Planning direction confirmed |
| GAT formal design and freeze | Existing implementation selects direct-continuable binding; the new entry requires an attributed compatible delta | Existing entry remains supported | Conflicting normative semantics cannot be silently overridden | Planning direction confirmed |
| DA formal design | WK/DSH/LEG are distinct; provider owns persistence; refs are process-local; reads are consistent per call | Public WK artifacts can be qualified at their actual exports | ReviewPacket derivation, input ACLs and artifact resolution require qualification | Required as input by HUMAN |
| DSH execution/extension source | Fresh task Session, awaited creation, GAT authority and joined child closing are the intended reuse path | Current APIs support the selected step snapshot policy; no core edits are authorized | Step refresh, unchanged retry prompt with per-attempt authority checks, cleanup failure and cold recovery need real evidence | Qualification pending |

## References to Read First

- `wbs-runs/durable-binding-reuse/proposal-review.md`; `implementation-plan.md`; `source-baseline.json`.
- `docs/gat-design/BASIC_DESIGN.md` §7 and production binding sections; `DETAIL_DESIGN.md` DD-09/DD-15/DD-16 and §§5/7/8; `DURABLE_AGENT_INTEGRATION.md`; `SOURCE_CODE_MAP.md`.
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` §§2–4/8/12.
- `/home/hoinv/work/dsh-durable-agent/docs/DURABLE_AGENT_DESIGN_INDEX.md` §§1–3 and `DURABLE_AGENT_DESIGN_MISSION_DELTAS.md` §§3–5.
- `/home/hoinv/work/dsh-durable-agent/docs/DURABLE_AGENT_ARCHITECTURE_DESIGN.md` AD-02–05; `DURABLE_AGENT_BASIC_DESIGN.md` BD-01–05; `DURABLE_AGENT_DETAIL_DESIGN.md` DD-01–04/DD-06–09/DD-11–12.
- `/home/hoinv/work/dsh-durable-agent/docs/DURABLE_AGENT_DETAIL_SOURCE_MAP.md` WK-PORT/PROFILE/CONTEXT/CONSUMER/MUTATE/TASK/PACKET/REVIEW and DSH-BIND/GAT-MEMBER; `DURABLE_AGENT_DESIGN_CONFLICTS.md` C-01/02/03/05/06/07/10/11/17. Resolve each basename within the same explicitly named DA docs directory.
- `packages/durable-agent/src/binder.ts`, `ownership.ts`, `tools.ts`, `composition.ts`, `package.json` and `tsdown.config.ts`.
- `/home/hoinv/deepseek-harness/AGENTS.md`, affected package instructions, execution manager/GAT attribution and public child/prompt/tool lifecycle definitions before Host qualification work.
- `.ai-work/procedural/skills/aiws-aip/operations/run.md` and `.ai-work/procedural/skills/aiws-lint/operations/task.md` for execution/finalization. Operating memory was read before step decomposition; it contains no applicable entries.

## Current Risks / Constraints

- No missing public operation, new persistence field or weaker reviewer isolation may be hidden as an implementation detail; stop the affected branch and present the smallest demonstrated extension.
- Existing adapter helpers may depend on the reserved-member Host or candidate feature; reuse only compatible ownership/validation, not the whole binder lifecycle.
- Whole model prompt and serialized tool results need explicit UTF-8 byte bounds; guidance is advisory and cannot grant task authority. Path-free structural DTOs do not guarantee arbitrary strings contain no private information.
- Same-member overlapping owners fail closed despite provider ref deduplication. Compare underlying registered provider identity, reserve canonical workspace/name and keep ownership quarantined until physical cleanup settles.
- `reviewContribution` performs an authorization snapshot read but must not render its member guidance/catalog/body. Freshness and other prompt/tool owners are Host responsibilities.
- Closing admission removes context/tools synchronously; non-cancellable calls remain observed/drained and late results are withheld. Never await a cleanup drain from an operation included in that drain.
- Recovery cannot redefine the roster from changed configuration, reopen a terminal execution, inject prior history or create retroactive receipts. Profile conflict/absent mapping denies admission.
- Preserve unrelated existing changes in `SOURCE_SNAPSHOT.json`, `compatibility/dsh-0.1.5-rc.2/manifest.json` and `installer/verify.mjs`; if a required distribution change overlaps them, reconcile ownership before editing.
- Estimated effort is 11–17 hours plus 3–5 hours correction/recheck reserve; no dollar cap or charged execution budget is implied. Focused checks only; no online provider call or full repository suite by default.

## Known Open Points

- OP-024-01: reviewer mode and exact ReviewPacket derivation from approved assignment/candidate inputs; no invented receipts, criterion IDs or generic fallback.
- OP-024-02: selected Host/package/public export compatibility, test Loader/snapshot launcher and actual command/build write scope.
- OP-024-03: prompt assembly timing, refresh at each admitted step assembly, unchanged snapshot across retries with per-attempt authority checks, logged reconstruction and no recursive/duplicate assembly.
- OP-024-04: cleanup participation in terminal settlement, delayed calls/release failures/deadlines and submission self-drain avoidance.
- OP-024-05: live cold recovery identity/config/profile validation before model/inbox release; terminal denial.
- OP-024-06: qualification/design and implementation reviewer identity/capability. Independent verdicts cannot be written by their producer.
- Runtime questions and evidence belong in workspace `05_open_questions.md`; this list is the initial planned uncertainty set, not a live progress table.

## Workspace Execution Rule

Runtime findings, confirmation evidence, decisions, check logs, drafts, review verdicts, metrics and capture disposition live in the per-account workspace created by `run start`. Update Active Step Context on transitions. Keep the AIP stable and Done Criteria declarative; append a dated Re-plan Log entry before changing objective, scope, expected outputs or major assumptions.

## Execution Steps

### Step: STEP-00 — Confirm execution scope and recover planning decisions

Objective:
Record the exact run instruction and bounded implementation understanding; carry forward the already confirmed additive adapter and DA-design requirements.

Recommended Mode:
Clarifying

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
plan

Inputs:
Direct HUMAN run instruction; this AIP Execution Scope/Governance Note; wbs-runs/durable-binding-reuse/proposal-review.md; AGENTS.md; .ai-work/AIWS.local.md

Expected Outputs:
Workspace task-understanding.md, authorization evidence and 05_open_questions.md

Done Condition:
The HUMAN has authorized running this exact bounded AIP; known planning decisions are retained, and any material new conflict is resolved before affected work.

Notes / Constraints:
Creating the AIP is authorized now; it is not a run instruction. No duplicate confirmation of prior planning choices. No deployment or protected canonical authority is inferred.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-01 — Define qualification design and exact environment

Objective:
Resolve selected Host/WK package bytes, mappings, public packet inputs and supported test launchers. Write prospective qualification design before any experimental GAT test/source changes.

Recommended Mode:
Executing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
test_design

Inputs:
wbs-runs/durable-binding-reuse/implementation-plan.md; wbs-runs/durable-binding-reuse/source-baseline.json; docs/gat-design/DETAIL_DESIGN.md; docs/gat-design/DURABLE_AGENT_INTEGRATION.md; DA formal documents in References; selected Host AGENTS.md and package exports

Expected Outputs:
docs/gat-design/DETAIL_DESIGN.md prospective qualification amendment; workspace qualification-design.md and qualification-environment.json with exact paths/commands/effects

Done Condition:
Qualification scope, source/design compatibility, real consumer path, provider identity/public exports, reviewer-input method and bounded launcher/write effects are concrete and reviewable; missing prerequisites are explicitly blocked.

Notes / Constraints:
Use disposable provider storage and an explicitly selected isolated Host. No core/loop/provider changes or live profile activation. Validate current WK versus DSH API family. Any experimental code must follow its recorded official design amendment.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-02 — Qualify the real isolated-execution path

Objective:
Exercise actual GAT execution manager and WK service/Consumer/provider through test-only Loader composition with mocked model transport. Resolve first-request, reviewer packet, selected-read, closing and recovery feasibility.

Recommended Mode:
Executing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
research

Inputs:
Workspace qualification-design.md and qualification-environment.json from STEP-01; docs/gat-design/DETAIL_DESIGN.md prospective amendment; original durable-binding-reuse-proposal.md; DA Detail DD-02–04/DD-06–09; selected public Host/WK artifacts

Expected Outputs:
Workspace qualification-matrix.md and verification/qualification logs/receipts; bounded test-only adapter prototype following the qualification amendment if required

Done Condition:
Each blocking feasibility question has actual positive/negative evidence or a precise reproduced scope blocker; successful cases use real GAT/WK owners and exact artifacts rather than a mocked Team service.

Notes / Constraints:
Test binding failure with zero model requests; packet mismatch/memory isolation; asynchronous authority loss; ref overlap; cleanup error/hang and no self-drain; cold/terminal recovery; exact step refresh/retry snapshot/logging. A missing public operation stops its branch. No acceptance from file existence or exit code alone.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-03 — Review qualification and settle production design

Objective:
Obtain independent qualification assessment and produce/review the additive production design delta under the official GAT design set before implementation.

Recommended Mode:
Reviewing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
review

Inputs:
Workspace qualification-matrix.md, qualification-design.md and qualification-environment.json; docs/gat-design/BASIC_DESIGN.md, DETAIL_DESIGN.md, DURABLE_AGENT_INTEGRATION.md, SOURCE_CODE_MAP.md; docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md; DA formal specification sections in References

Expected Outputs:
Workspace qualification-review.md and design-review.md; approved attributed amendments in docs/gat-design/BASIC_DESIGN.md, DETAIL_DESIGN.md, DURABLE_AGENT_INTEGRATION.md and SOURCE_CODE_MAP.md

Done Condition:
An independent reviewer has assessed the full implementation/test/final chain; blockers are resolved with evidence, the approved delta matches both existing design sets, and the intended source/authority/config contracts are settled before STEP-04.

Notes / Constraints:
Specify exact Session/execution/member/generation checks, ordinary selection, explicit reviewer packet/ACL, step-assembly refresh and per-request authority integration, bounds, provider-identity exclusion and cleanup/recovery. Preserve direct composition. Applicable approved CR/HUMAN design decisions remain mandatory. Reviewer availability is a real dependency; do not invent a verdict or silently overwrite frozen semantics.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-04 — Implement the additive execution composition

Objective:
Implement the new opt-in entry and its narrowly scoped configuration, ownership, executable selected-read tools, prompt integration, reviewer mode and joined lifecycle according to STEP-03 design.

Recommended Mode:
Executing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
code

Inputs:
docs/gat-design/DETAIL_DESIGN.md accepted execution delta; docs/gat-design/DURABLE_AGENT_INTEGRATION.md; workspace qualification-review.md and design-review.md; packages/durable-agent/src/ownership.ts, tools.ts, binder.ts, composition.ts; public WK service/Consumer and selected Host interfaces

Expected Outputs:
packages/durable-agent/src/execution-composition.ts and required shared helpers; package.json/tsdown/build/export metadata; package README/JSDoc; bounded GAT-owned qualification Host mirrors

Done Condition:
New public entry implements the accepted design without altering existing composition behavior; reused helpers serve actual callers; API consumers and package metadata remain consistent; exact changed source inventory is recorded.

Notes / Constraints:
Register contributions/tools through owned effects. Skip bootstrap/nonexecution Sessions; reject missing selected-execution mappings. Check current identity/selection around every await. No candidate/confirmed-write tools, provider paths, second dispatcher, released persistence rewrite or broader Host patchset.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-05 — Run focused behavior and artifact verification

Objective:
Verify current implementation against detailed-design UT, interface/basic-design IT and proposal scenarios using actual GAT/WK owners; update the owning keyless Session snapshot and qualify built public imports.

Recommended Mode:
Executing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
test_design

Inputs:
docs/gat-design/DETAIL_DESIGN.md accepted delta; BASIC_DESIGN.md and DURABLE_AGENT_INTEGRATION.md; original proposal qualification cases; workspace qualification-environment.json; packages/durable-agent/src and tests; selected Host public artifacts and Session snapshot composition

Expected Outputs:
Focused tests under packages/durable-agent/tests; GAT-owned Host keyless gat-durable-execution snapshot; workspace test-matrix.md and verification/typecheck, behavior, snapshot, public-import and Loader receipts

Done Condition:
Full required positive/negative matrix passes on the exact current candidate; existing direct-composition regressions pass; typecheck/build/public imports and logged snapshot qualification are tied to source/package hashes; any NG prevents dependent technical acceptance.

Notes / Constraints:
No online model/provider test or full repository suite by default. Include build dependency lib/tsbuildinfo and snapshot effects in preflight scope. After a repair rerun all required checks affected by that repair; do not reuse stale PASS evidence. No expectation normalization that hides changed admission or memory behavior.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-06 — Obtain independent implementation review and synchronize design

Objective:
Obtain independent source/design review of the exact tested candidate and reconcile any corrections before final handoff. Confirm final official design/source mapping and artifacts.

Recommended Mode:
Reviewing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- (none; main session coordination and independent review where specified)

Difficulty:
high

Kind:
review

Inputs:
docs/gat-design/BASIC_DESIGN.md, DETAIL_DESIGN.md, DURABLE_AGENT_INTEGRATION.md and SOURCE_CODE_MAP.md; docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md; DA formal sections in References; workspace design-review.md, test-matrix.md and verification receipts; packages/durable-agent implementation

Expected Outputs:
Workspace source-review.md and source-design-consistency.md; reconciled official GAT design/source mappings; fresh test/review receipts for corrected candidates

Done Condition:
Independent review clears identity/authority ordering, selected reads, reviewer isolation, logged step refresh/retry snapshot, cleanup/recovery and additive compatibility on the exact final bytes; official GAT design fully reflects those bytes.

Notes / Constraints:
Review uses the same external specifications as author/tester, not author assertions as proof. Corrections follow design-before-code and preserve prior evidence. Missing public operations or new semantic conflicts stop the affected branch for scope/approval decision.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

### Step: STEP-07 — Finalize technical handoff and deployment proposal

Objective:
Complete evidence-bound implementation handoff, scoped lint and final capture disposition; prepare exact deployment configuration/storage/rollback proposal without activation.

Recommended Mode:
Executing

Applicable Guidelines:
- AGENTS.md — GAT design-first and project authority rules.
- .ai-work/AIWS.local.md
- .ai-work/procedural/skills/aiws-aip/operations/run.md

Recommended Skills:
- aiws-aip
- aiws-lint

Difficulty:
medium

Kind:
organize

Inputs:
Workspace qualification-review.md, design-review.md, source-review.md, test-matrix.md, source-design-consistency.md, qualification-environment.json and verification receipts; docs/gat-design official amended set; packages/durable-agent final package artifacts; this AIP Done Criteria

Expected Outputs:
Workspace implementation-handoff.md, deployment-proposal.md and 11_output_final.md; final lint/consistency/package manifest receipts; capture disposition and governed AIP closure

Done Condition:
Technical deliverables, independent review and required checks are complete; all required official design changes are applied; capture disposition is HUMAN-controlled; actual lint results and limitations are reported; deployment proposal remains unactivated.

Notes / Constraints:
Use aiws-lint task scoped to the runtime workspace and AIP; report whole-tree results when escalation applies. Never auto-fix Wiki/Truth or tick AIP Done Criteria. Do not claim live GUI/deployment acceptance, assign Mission Board task10, or hide a qualification blocker as a partial completion.

Workspace Actions:
- Record step evidence, current open-point dispositions and immediate capture candidates in the runtime workspace; refresh/read Active Step Context on transition.

## Done Criteria

- [ ] Gate U1 execution scope confirmed with actual HUMAN authorization; U2 input understanding and U3 open-point dispositions are recorded in the runtime workspace.
- [ ] Real Host/WK qualification resolves first-request/step refresh/retry snapshot/logging, reviewer packet/ACL/isolation, selected reads, joined cleanup and live/terminal recovery before production implementation.
- [ ] Approved GAT design deltas precede source changes and final official `docs/gat-design/` documents map to the implemented additive entry; normative conflicts follow applicable approval/CR gates.
- [ ] `@vuhoi/gat-durable-agent/execution-composition` has explicit validated configuration and actual guarded executable tools/contributions; existing direct composition remains supported.
- [ ] Required focused UT/IT, typecheck, built public-export/Loader and keyless Session snapshot cases pass on exact final candidate bytes, including negative authority and cleanup cases.
- [ ] Independent qualification/design and implementation reviews have actual verdicts; no author self-acceptance substitutes for them.
- [ ] Technical handoff, source/design consistency, exact package manifests and proposed deployment/storage/rollback configuration are complete; deployment is excluded and not claimed.
- [ ] Required scoped/escalated lint results and HUMAN-controlled capture dispositions are recorded before governed close; prior mission history and unrelated changes remain preserved.

## Self-check / Review Points

- Match the intervention to current GAT isolated-execution attribution and WK public APIs; do not import reserved-member prerequisites merely because older code uses them.
- Review provider ref deduplication versus adapter ownership, exact identity before/after await, stable tool schema timing and complete prompt/result bounds.
- Reviewer context is the explicit memory-free route with authenticated current packet inputs, genuinely fresh transport and evidence ACLs; a generic reviewer role is insufficient.
- Verify cleanup is part of terminal settlement and cannot self-await; authority cutoff does not falsely cancel non-cancellable provider work.
- Keep configuration/profile reconciliation and terminal denial explicit; no bootstrap rebinding or historical receipts.
- No execution state, runtime counters or completed-checkbox tracking belongs in this AIP.

## Finalization Notes

Creating this draft completes the requested planning action. `aiws-aip run start` is a later execution action. No workspace is initialized or active step is set merely to create the plan. Technical completion requires the entire intended implementation and evidence set; an unresolved scope blocker is a blocked handoff, not completion. Live deployment remains separately authorized.

## Pre-flight Pending Captures

- [IMPORTED 2026-10-04] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact=".ai-work/aip/templates/AIP_EXEC_TEMPLATE.md" lookup_query="AIP_EXEC_TEMPLATE path and semantic" reason="Required local EXEC authoring template was read after bounded lookup escalation; no exact registered route returned."
- [IMPORTED 2026-10-04] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="/home/hoinv/work/dsh-durable-agent/docs/" lookup_query="DURABLE_AGENT_DETAIL_DESIGN.md path and semantic" reason="HUMAN-supplied formal DA design collection supplies reusable implementation/review references; current GAT lookup returned related GAT/code routes rather than these exact documents."

## Re-plan Rule

Append a dated entry before any change to objective, scope, expected outputs, major assumptions or execution strategy. Include the trigger, concrete change, evidence reference and applicable HUMAN approval. Record runtime detail in workspace findings/open points, not the AIP. Sweep superseded wording across the entire AIP, classify intentional history references, and verify no stale active-scope wording remains. Do not silently expand into DSH core, DA provider or deployment work.

## Re-plan Log

- 2026-10-04 — HUMAN chose “theo huong chi sua plugin” after OP-024-03 retry qualification. Retain adapter-only scope and unchanged DSH/WK APIs; refresh Durable context at each admitted step assembly and retain that exact prompt snapshot for all retries within the step. Continue exact authority/service checks before every actual request, including retry. Amend active qualification/design/test wording before dependent source changes; preserve prior failing retry-freshness receipts as historical evidence. Scope decision and evidence: runtime workspace `plugin-only-decision.md`, `qualification-matrix.md`, `verification/qualification-attempt-08.log`. Independent qualification/design/implementation review and deployment exclusions remain applicable.
