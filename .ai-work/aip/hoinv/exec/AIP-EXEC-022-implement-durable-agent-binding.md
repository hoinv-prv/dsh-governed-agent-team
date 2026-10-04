---
artifact_type: aip_exec
artifact_id: AIP-EXEC-022
title: "Implement GAT required member binding and Durable Agent adapter"
status: active
project: dsh-governed-agent-team
owner: hoinv
plan_source: "Direct HUMAN request on 2026-10-04 to create an implementation AIP for docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md"
template_source: AIP_EXEC_TEMPLATE
related:
  - AIP-EXEC-021
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20261004-exec-022
updated_at: 2026-10-04
---

<!-- Stable control: declarative criteria only; runtime state belongs in the task workspace. Creating this draft does not authorize implementation, external repository changes, canonical promotion, publication or activation. Applicable approved CR gates remain mandatory. -->

# AIP_EXEC — Implement GAT required member binding and Durable Agent adapter

## Governance Note

This AIP plans delivery of proposal stages S0–S5. The current HUMAN request authorizes AIP creation and Luna assistance for simple preparation. Execution authorization, proposed decisions and dependency ownership are confirmed in STEP-00 before implementation.

- STEP-01 updates intended project design before dependent source changes. The formal design set is currently a project design draft, not canonical Truth. Preserve this status; any Truth/canonical change, frozen-contract revision or official wiki promotion requires its applicable approved CR/review gate.
- STEP-02–STEP-03 implement the generic GAT foundation against the frozen reserved-handle interface and deterministic fakes. Production child wiring waits for STEP-04.
- STEP-04 qualifies owner-supplied DSH/DA prerequisites. External repository implementation is not implicitly authorized by this AIP; missing capabilities are owner handoffs unless separately approved.
- STEP-05–STEP-06 implement the selected adapter and integrate only after matching design and dependency evidence. Pure adapter fixtures may proceed while host qualification is pending; production wiring may not.
- STEP-07 consumes separately approved mission/executor work and qualifies composition/distribution. Missing authorization enforcement leaves production disabled; this binding assignment does not silently become a mission-authority rewrite.
- STEP-08 reconciles design and produces review evidence. Package publication, deployment, profile activation and live-runtime reload require their applicable explicit authorization. A foundation-only handoff is not completion of this full implementation AIP.

## SOP Compliance

- Gate U1: confirm task understanding and execution scope at STEP-00; retain the HUMAN message as workspace evidence.
- Gate U2: maintain input understanding below and qualify changed inputs in workspace findings.
- Gate U3: track decisions, dependency owners and unresolved blockers in workspace `05_open_questions.md`.
- Read `.ai-work/truth/SOP_MASTER.md` and `.ai-work/truth/AI_WORK_CONTRACT.md` at execution preflight. If they provide no task-specific guidance, use the project-owned rules and confirm the execution scope at STEP-00; do not invent an approved process.

## Objective

Implement required GAT member attachments and a scoped Durable Agent context/memory adapter from `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, after approval of its implementation baseline. Bind before initial model admission, recover from immutable persisted attachment records before later work, keep Team authority in GAT, and keep persistent capability data in Durable Agent. Deliver traceable design, source, lifecycle/conformance evidence and supported package composition without claiming production eligibility before every prerequisite is qualified.

## Selected Task Lens / Mode

- Lens: No-Lens.
- Reason: the proposal supplies concrete stages, source/design mapping and acceptance requirements; use these and the frozen contract directly.
- Search/execution effect: wiki-first for all design/spec inputs; source inspection checks actual APIs and current callers.
- Resolved references: proposal; formal AD/BD/DD and source map; member-binding freeze; Durable integration reference; public sibling DA service/Consumer/provider; AIP spec/template.
- Deferred lookups: selected DSH lifecycle/export/executor specifications and source; selected DA package metadata/bounds/tests; conditional official Consumer and Durable DD-08/09; closing owner handoffs; design/SDK/baseline generation tooling. Resolve during STEP-01/STEP-04, with explicit applicability and owner.
- Expansion allowed: yes, when necessary to prove a contract or affected dependency; scope changes require a Re-plan Log entry.

## Execution Scope

### In Scope

- S0: baseline and dirty-file evidence across GAT, DA and selected DSH; approval of P-01–P-08, API family, execution model and intended design deltas.
- S1: normalized initializer migration; bounded opaque attachments/JCS digests; binder registry; member-only event v3/v2 replay; lifecycle, recovery, deadlines and safe views against deterministic host fakes.
- S2: qualify the DSH reserved handle, persist-only initial inbox, activation/recovery gate, legacy wrapper, per-request refresh and owner-scoped assembly shutdown surfaces.
- S3: the selected Durable integration package, strict explicit declaration, exclusive ownership, executable read/candidate handlers, bounded refresh and cleanup; real public-provider integration in temporary storage.
- S4: consume approved exact mission leases, canonical task association and nested capability enforcement; deliver opt-in profile/package mappings, SDK safe summaries, build/export/installer compatibility and supported workflow evidence.
- S5: independent review, final source/design synchronization, test traceability, deployment constraints and downgrade refusal.

### Out of Scope

- Durable task runner/WBS execution, standalone `packages/gat` reference-memory or MCP backend changes, global sharing, optional/degraded attachments, live identity edits and new filesystem authority.
- Confirmed-memory model tools, automatic memory promotion, a new memory approval UI, provider-private storage coupling, storage deletion as compensation and undocumented migration.
- Implicit WK-to-official-DSH API translation, unapproved isolated-execution migration, both API families in one initial delivery, or reactivation of incident Sessions.
- External DSH/DA implementation, mission-authority redesign, contract revisions, canonical/wiki promotion, merge, publication, deployment or live-runtime reload without the corresponding approved scope.

## Expected Outputs

- Intended and final design coverage in `docs/gat-design/ARCHITECTURE_DESIGN.md`, `BASIC_DESIGN.md`, `DETAIL_DESIGN.md`, `DURABLE_AGENT_INTEGRATION.md` and source maps/baselines; update AD-04/06/08/09/12, BD-01/02/09/10/12–14 and DD-01–03/07–11/15–17 as affected. Preserve Target status for undelivered work.
- Generic GAT implementation and tests in `packages/core/`, default initializer/callers and scoped policy regression coverage in `packages/tools/`, safe view consumers in `packages/web/` as needed.
- Proposed `packages/durable-agent/` integration package and its tests, subject to P-01 approval; opt-in integration profile and package manifests/mappings in the locations approved at STEP-01.
- Supported distribution updates under `installer/`, `scripts/` and compatibility artifacts, generated using repository tooling.
- Runtime evidence under the workspace linked by `aiws-aip run start`: `baseline.md`, `approved-decisions.md`, `design-source-test-matrix.md`, `dependency-qualification.md`, `acceptance-matrix.md`, `verification/`, `independent-review.md` and `implementation-handoff.md`, plus normal findings/open-questions/capture files.
- Evidence distinguishes source bytes, exported built artifacts and any separately authorized loaded runtime; no historical test result is presented as a new test run.

## Execution Input Package

### Plan Source

- Direct HUMAN request dated 2026-10-04, Asia/Tokyo: create an AIP to implement the named proposal; spawn Terra/Luna for simple tasks.
- Proposal is the candidate implementation handoff, not approval of P-01–P-08 or runtime activation.

### Required Truth Inputs

- `.ai-work/truth/SOP_MASTER.md` and `.ai-work/truth/AI_WORK_CONTRACT.md`; these files currently contain no task-specific text. Recheck at execution start, never fill them silently.
- `.ai-work/truth/canonical/methodology/20_specs/AIP_Detail_Spec_MVP.md`, §§2.3, 5.4, 6.3, 7, 10–11.

### Required Wiki Inputs

| Input | Wiki Source ID | Artifact Path | Use | Capture flag |
|---|---|---|---|---|
| Proposal | (unregistered) | `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md` | Full §§1–13; S0–S5 and T01–T23 | [retrieval_gap] |
| Architecture | SRC-GAT-ARCHITECTURE-DESIGN | `docs/gat-design/ARCHITECTURE_DESIGN.md` | §§4–8, AD-04/06/08/09/12 | — |
| Basic design | SRC-GAT-BASIC-DESIGN | `docs/gat-design/BASIC_DESIGN.md` | BD-12–14 and §§3/5–9 | — |
| Detail design | SRC-GAT-DETAIL-DESIGN | `docs/gat-design/DETAIL_DESIGN.md` | DD-01–03/07–11/15–17 and discrepancy table | — |
| Source map | SRC-GAT-DESIGN-SOURCE-MAP | `docs/gat-design/SOURCE_CODE_MAP.md` | Existing symbols/tests and target gaps | — |
| Frozen binding contract | SRC-GAT-MEMBER-BINDING-FREEZE | `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` | Normative §§3–14; no silent revision | — |
| Durable integration | SRC-GAT-DURABLE-INTEGRATION-DESIGN | `docs/gat-design/DURABLE_AGENT_INTEGRATION.md` | Public API, ownership, accepted-evidence limits | — |
| Public DA service | SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-SERVICE-TS | `../dsh-durable-agent/durable-agent-plugin/src/service.ts` | API version, features and public contracts | — |
| Public DA Consumer | SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-CONSUMER-TS | `../dsh-durable-agent/durable-agent-plugin/src/consumer.ts` | Metadata contribution versus executable handlers | — |
| Public DA provider | SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-LOCAL-PROVIDER-TS | `../dsh-durable-agent/durable-agent-plugin/src/local-provider.ts` | Same-identity deduplication and non-cancellable lifecycle | — |

### Reference lookup

- Use `python3 .ai-work/tooling/lookup_wiki_source.py --query '<artifact or concept>' --limit 5`, then `wiki_meta.py --view <source_id>`; obtain paths from meta before opening registered inputs.
- If a needed input misses, retry semantic/tokens and filtered catalog before authorized raw fallback. The named proposal was absent from lexical/semantic matches and the GAT design catalog; its user-supplied path is the bounded fallback input, not wiki promotion.
- Use `wiki_relations.py --relations <resolved_id>` for dependency traversal. Registered Durable integration edges include public service/provider/Consumer and their five relevant suites; resolve the suites before execution. Historical reports remain reference evidence.
- The project-local document search guidance path is currently absent. Follow the skill lookup procedure and the project rule; do not invent a raw directory policy. This AIP grants no local-wiki search.

### Required Workspace Preconditions

- [ ] Execution authorized and AIP pre-start lint passes; `aiws-aip run start` creates a per-account task workspace and writes its provenance pointer.
- [ ] Current step pointer and Active Step Context exist and are read before step work.
- [ ] Findings, queue, `05_open_questions.md` and `08_capture_inbox.jsonl` initialized; pending captures imported and checked.
- [ ] Source/design ownership and pre-existing dirty changes recorded before edits.

## Input Understanding

| Input | Key understanding | Assumption / ambiguity | Confirmation |
|---|---|---|---|
| Proposal §§1–3/10–12 | Concrete candidate baseline; foundation can be tested before production wiring | P-01–P-08, API/lifecycle and execution scope require approval | Pending at STEP-00 |
| Freeze §§4–9/14 | Core owns normalized roster, prepare-all, v3 records, required bind/recover and reverse cleanup; DSH owns reserved admission | Method names are semantic; actual exports must be qualified | Confirm against selected host |
| Freeze §§10–11 | Exact HUMAN mission leases and nested delegation enforcement are production dependencies | Current auto-approved missions/simpleMode do not satisfy the target | Owner evidence required |
| Formal AD/BD/DD | Current source-aligned design distinguishes Current/External/Target; DD-16/17 are not delivered | Apply intended design delta before source; preserve existing discrepancy records | Review at STEP-01 |
| Public DA package | WK-style API v1; Consumer returns descriptors; provider deduplicates refs and release is not an idempotent cancellable host primitive | Dedicated provider and one-host workspace ownership must be established in composition | Confirm P-03 and version pin |
| Closing supplement §§2.1–2.2/7.5 | Exact owner-proven closing may abstain from assembly; lost membership alone is insufficient | Isolated and direct-continuable paths have different authority proofs | Selection gate; no automatic migration |

## References to Read First

1. `AGENTS.md`, GAT design-first rule, and `.ai-work/AIWS.local.md`, Execution policy.
2. Required Truth inputs and the AIP template `.ai-work/aip/templates/AIP_EXEC_TEMPLATE.md`.
3. Formal architecture §§4–7, basic design BD-12–14/§§5–8, detail design DD-01–03/07–11/15–17 and source map.
4. Frozen contract §§3–14 and Durable integration public contract/verification limits.
5. Proposal §§2.2–12 and selected original public DA interfaces; use proposal §1 links only after lookup and applicability checks.
6. Conditional closing proposals and official Consumer/Durable DD-08/09 only when the selected API/lifecycle requires them; they are owner handoffs, not accepted amendments.

## Current Risks / Constraints

- Implementation approval is not recorded by creating this draft. Proposed API and lifecycle selections cannot be silently inferred from similarly named services.
- Foundation work is permitted only after execution/design approval; production wiring requires qualified S1+S2, and production dispatch requires S4.
- Preserve existing modified `packages/core/src/{projection,roster,types}.ts`, `packages/core/tests/{persistence,team}.spec.ts` and `packages/web/tests/team-action.client.spec.tsx`; recheck actual dirty bytes. Do not reset, duplicate or claim ownership of earlier patches.
- Existing static `team:policy` label capture must survive; qualify it through regression checks instead of introducing a second fix or weakening live guards.
- Ownership is one live GAT owner per canonical workspace/name, with a dedicated provider and one host process per storage workspace. A process map is not a cross-host lock proof. Slow cleanup retains identity quarantine.
- All freeze §5 limits apply to request and prepared/replayed records: 8 records/member, 65,536 canonical bytes/record, 262,144 bytes/record array, depth 16, 4,096 nodes, key/value string limit 16,384 UTF-8 bytes, binder ID up to 64 ASCII characters. Include envelope bytes and JCS conventions.
- Scope/host workspace, service key, runtime ref and raw payload are host-only; model tools, diagnostics and Web/SDK views expose only safe allow-listed information.
- An uncertain flush is not proof of no commit; an active committed snapshot may remain runtime-unavailable. Live retry and reconstructed recovery must not double-install.
- Provider timeouts do not cancel storage operations. One lifecycle deadline cuts off authority; late operations stay observed and are cleaned once without releasing a replacement owner's identity.
- Member v3 requires format registration plus projection; unrelated families retain version rules. A v2-only rollback cannot resume v3 logs; refuse downgrade rather than dropping attachments.
- Root TypeScript suites run through the DSH verifier environment; do not invent root `npm test`, bypass compatibility, or turn historical DA counts into new PASS evidence.
- The current SOP/Contract files are empty and local search guidance is absent. Record these input limits; they do not authorize canonical repairs.

## Known Open Points

- OP-01: HUMAN execution scope and approval/revision of P-01–P-08. Candidate default is the proposal's WK-style separate adapter; it remains unselected until confirmed.
- OP-02: exact DSH checkout/API family and direct-continuable versus isolated execution target. Official Consumer requires reviewed API mapping; isolated execution requires approved stable-member/execution/resource ownership mapping.
- OP-03: DSH reserved-handle, request-refresh and assembly-removal capability owner, implementation revision and qualification evidence.
- OP-04: dedicated DA provider registration key, pinned package/API/features, one-host workspace exclusivity and deployment owner.
- OP-05: approved mission/task authority and executor/nested capability workstream with concrete evidence; consuming that work does not approve rewriting it here.
- OP-06: supported verification environment, generated SDK/design-check entrypoints and external checkout edit authority, if any.
- OP-07: applicable design/contract/wiki review or CR gates and release/runtime activation scope. Missing production gates remain blockers, not waived completion criteria.
- Detailed state/history belongs in the execution workspace `05_open_questions.md` created by `run start`.

## Workspace Execution Rule

Keep findings, approvals, test output, metrics, queue and captures in the task workspace. Never tick this AIP's declarative Done Criteria or add runtime findings to its body. Update the current-step pointer, rebuild/read Active Step Context, and capture reusable decisions or retrieval friction when discovered.

Use Luna (`gpt-6-luna`) for simple bounded tasks: fixture inventory, link/ID checks, known-command verification summaries and mapping completeness. Terra may be used only if the execution environment exposes it; Luna is the available requested option. Delegate with exact scope and design paths from this AIP, require wiki-first and design-before-code, and reserve source ownership. Do not use `Assigned Agent` to fabricate an AIWS Task Desk for a native sub-agent. Main session owns contracts, API/lifecycle decisions, concurrency and authorization design. Delegate source work only after its reviewed design delta exists; independently review its result.

## Execution Steps

### Step: STEP-00 — Confirm implementation scope and prerequisite decisions (HARD GATE)
Objective:
Record task understanding, deliverables, Done definition and authorization. Confirm or revise P-01–P-08, choose one API family and execution model, and identify external dependency owners and approved workstream scope.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `AGENTS.md`, GAT design-first rule
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§1–3/8/10/12

Recommended Skills:
- aiws-aip run

Inputs:
- HUMAN request, this AIP and declared Truth/design inputs

Expected Outputs:
- Workspace task-understanding note, `approved-decisions.md`, approval references and dependency owners

Done Condition:
HUMAN confirms execution scope and baseline decisions, or explicitly delegates specific choices with recorded authority. No dependent implementation starts under unresolved conflicting choices.

Notes / Constraints:
- A request to create this AIP is not a request to start it. Approval must identify permitted GAT work and any external edits. An isolated target needs mapping approval before source; production authorization is separate.

Workspace Actions:
- Record Gate U1 evidence and OP-01–OP-07 disposition; import/check pending captures when run starts.

### Step: STEP-01 — Record current baselines and update intended official design (S0)
Objective:
Reinspect GAT/DA/selected DSH HEADs, dirty paths, exact input hashes, source callers/tests and approved API/lifecycle. Apply reviewed intended design deltas to affected formal design before code, with requirement-to-source/test mapping.

Recommended Mode:
Planning

Applicable Guidelines:
- `AGENTS.md`, GAT design-first rule
- `docs/gat-design/ARCHITECTURE_DESIGN.md`, §§4–8
- `docs/gat-design/DETAIL_DESIGN.md`, DD-01–03/07–11/15–17
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`, §§3–14

Recommended Skills:
- aiws-wiki lookup

Inputs:
- STEP-00 approvals; current formal AD/BD/DD/source map; proposal §§2/4–10; selected original APIs

Expected Outputs:
- `baseline.md`, `design-source-test-matrix.md`, intended AD/BD/DD/integration design deltas and dependency record

Done Condition:
Every planned source region has prior approved design coverage and an owner; conflicts are resolved or the affected region is held. Current, proposed and conditionally applicable behavior remain explicit.

Notes / Constraints:
- Read operating memory before step planning; its hints are advisory. Preserve dirty work and source/build/runtime distinctions. Any change to frozen semantics requires its reviewed revision/CR before dependent work. Luna may check mapping/links after the main design is ready.

Workspace Actions:
- Store input hashes/commands, decision-to-design locators and source ownership; open exact dependency questions.

### Step: STEP-02 — Implement normalized initialization, attachments and member v3 (S1)
Objective:
Migrate the single initializer to normalized specs with core-owned prepare-all. Implement generic bounded plain JSON/JCS validation and digest, registry reference lifetime and prepared ownership, and member-only v3 persistence/replay with safe views.

Recommended Mode:
Executing

Applicable Guidelines:
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`, §§4–6/9/12–14
- `docs/gat-design/DETAIL_DESIGN.md`, DD-01/03/10/16
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§4–5/9

Recommended Skills:
- aiws-wiki lookup

Inputs:
- STEP-01 design; core types/index/projection/journal; tools initializer/config callers; existing replay/view tests

Expected Outputs:
- Generic attachment/registry modules and tests; migrated initializer/default adapter; member format v3 and strict v2 adapter; safe binding summaries
- T01/T02/T09 results and applicable default-roster, SDK/view and unrelated-event-family regressions

Done Condition:
Prepare/schema/route failures create zero member rows/children; detached prepared bytes cannot mutate; full bounds/digests pass independent fixtures; inactive references prevent registry replacement; valid v2 supplies empty attachments and unknown versions reject.

Notes / Constraints:
- Core never interprets DA payload semantics. Record/array bounds include canonical envelopes; successful prepared ownership transfers or aborts once. Default GAT fallback behavior remains available through its default adapter; requested Durable configuration must not fall back.

Workspace Actions:
- Bind symbols/tests to design coverage; store raw journal/JCS oracles and focused regression reports.

### Step: STEP-03 — Implement core binding, recovery and bounded teardown against fakes (S1)
Objective:
Implement frozen prepare/provision/materialize/bind/quarantined-persist/active/publish/guarded-activate ordering, live-retry versus reconstruction, recovery-gated mailbox release and one total lifecycle deadline using the frozen host port and deterministic fakes.

Recommended Mode:
Executing

Applicable Guidelines:
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`, §§7–8/13–14
- `docs/gat-design/DETAIL_DESIGN.md`, DD-02/07/08/16
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §7

Recommended Skills:
- aiws-wiki lookup

Inputs:
- STEP-02 contracts; prior STEP-01 lifecycle design; roster/lifecycle/mailbox/index and persistence fixtures

Expected Outputs:
- Generic lifecycle orchestration and deterministic reserved-handle fixtures
- T01/T03–T05/T07–T08 core assertions with independent durable-order traces

Done Condition:
Zero model work before committed active plus authorization/activation; one initial durable item; exact failure/uncertain-commit handling; no double installation; absent/corrupt required binding prevents release; timeout detaches authority and preserves external data.

Notes / Constraints:
- No production child wiring before qualified S2. Do not use `startContinuable` or `agent/created` as a substitute for pre-admission binding. After active commit, live valid bindings are retained for retry; reconstruction advances generation and recovers once.

Workspace Actions:
- Store success/failure/concurrency/recovery/deadline traces and unresolved host assumptions.

### Step: STEP-04 — Qualify selected host and Durable package dependencies (S2, HARD GATE)
Objective:
Verify exact DSH reserved-handle exports/state/errors, persist-only inbox, cold recovery, compatibility wrapper, per-request refresh and scoped assembly removal. Pin public DA API/features/exports and establish ownership assumptions for the selected composition.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`, §§7/10–11/14
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§2.2/5–7/10–11

Recommended Skills:
- aiws-wiki lookup

Inputs:
- Owner-supplied exact DSH/DA revision/package; STEP-00 API/lifecycle selection; selected public API and host tests

Expected Outputs:
- `dependency-qualification.md` with actual exports, commands, artifact hashes, identity mapping, required hook proofs and named blockers
- T03/T05 host conformance; relevant DA public API/export/build qualification

Done Condition:
Actual host state machine/admission/recovery and refresh/assembly facilities meet the freeze and selected design. Missing features produce an owner handoff and block dependent wiring rather than a compatibility bypass.

Notes / Constraints:
- External edits require separate approval and that repository's design-first rules. S1 and pure adapter units may be completed while S2 is blocked. Official Consumer selection requires reviewed replacement API mapping; never combine its leases/principals with the WK API. Legacy/direct paths without exact closing proof retain strict denial.

Workspace Actions:
- Record host/package/evidence locators and production gate states; capture reusable qualification gaps.

### Step: STEP-05 — Implement strict Durable declaration, binder and ownership (S3)
Objective:
Implement the approved integration package and explicit Durable initializer, payload validation, trusted registration/workspace recovery checks and host-wide exclusive identity coordinator. Map prepare/bind/recover/cleanup through the selected public API.

Recommended Mode:
Executing

Applicable Guidelines:
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§3–5/7.4/9
- `docs/gat-design/DURABLE_AGENT_INTEGRATION.md`, Public integration contract
- `docs/gat-design/DETAIL_DESIGN.md`, DD-15/16

Recommended Skills:
- aiws-wiki lookup

Inputs:
- Approved adapter design and P-01–P-04; generic core port; pinned public DA service/Consumer/provider

Expected Outputs:
- Adapter initializer/binder/ownership implementation and tests; payload persist/recovery mapping
- T07/T08/T10 evidence with a real public provider in temporary storage and deterministic lifecycle barriers

Done Condition:
Strict declaration intent fails closed; persisted payload matches immutable member/profile identity; no YAML reload or saved runtime-ref replay; second ownership rejects before provision; late work is observed and resources released once with quarantine retained until settlement.

Notes / Constraints:
- For approved P-02 use workspace/fresh only; distinguish continuation route, LLM route and storage registration. Prepare validates and reserves without storage provisioning. Partial bind cleanup and prepared abort cooperate through one owner. No storage deletion or private-directory inspection.

Workspace Actions:
- Store payload/API mapping, ownership traces and real-provider result evidence. Fake scope units may proceed before STEP-04; host wiring remains gated.

### Step: STEP-06 — Implement scoped tools, request refresh and qualified closing behavior (S3)
Objective:
Register closed-schema executable read/candidate tools before initial prompt persistence, refresh one coherent bounded Consumer contribution before each request, and implement exact generation/authority checks and one-shot non-deadlocking shutdown.

Recommended Mode:
Executing

Applicable Guidelines:
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§2.2/6/7.5/11
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`, §§10–12
- `docs/gat-design/DETAIL_DESIGN.md`, DD-09/15/16

Recommended Skills:
- aiws-wiki lookup

Inputs:
- STEP-05 binder identified in workspace `design-source-test-matrix.md`; qualified STEP-04 host surfaces and approved execution mapping in workspace `dependency-qualification.md`; relevant existing static policy regression

Expected Outputs:
- Executable scoped handlers/contributions and real composition fixtures; T06/T08/T11/T12
- T16–T21 as applicable, or documented unsupported-path strict-denial evidence

Done Condition:
Caller cannot select ref/workspace/identity/approval; candidate remains unconfirmed; stale closures deny; refresh errors prevent dispatch; late context/memory is withheld after authority loss. Applicable closing removes all owner material including pre-collected schemas without weakening effect admission or self-awaiting cleanup.

Notes / Constraints:
- Preserve static Team labels and real active-provider/unknown-identity errors. No confirmed commit model tool. General post-await/cleanup safeguards apply to the adapter; isolated closing fixtures require approved exact owner proof. Do not implement the official Consumer unless its scope was separately approved.

Workspace Actions:
- Record scope negatives, context size/refresh traces, no-Consumer controls and async barrier cleanup evidence; flag conditional tests accurately.

### Step: STEP-07 — Integrate approved authorization, opt-in composition and distribution (S4, HARD GATE)
Objective:
Consume the approved mission/task/executor workstream, wire production child binding only with qualified dependencies, and deliver supported profile/package/build/SDK/installer verification. Prove runtime wakes and effects enforce exact current authority.

Recommended Mode:
Executing

Applicable Guidelines:
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`
- `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`, §§10–14
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§8–11
- `docs/gat-design/DETAIL_DESIGN.md`, DD-09–11/16/17

Recommended Skills:
- aiws-wiki lookup
- aiws-lint

Inputs:
- STEP-02–STEP-06 results; independently approved host mission leases/task authority/nested capability evidence; selected package/environment pins

Expected Outputs:
- Opt-in dedicated-provider/single-initializer composition; new package build/exports/mappings and safe generated SDK/Web summaries
- T13–T15; applicable T16/T22/T23; full supported build/profile/installer and GAT-only regression evidence

Done Condition:
All proposal §10 production prerequisites have evidence locators. Wrong/stale/ambiguous/revoked leases and named/aliased/nested delegation deny before effects; queue/bootstrap without a lease cannot wake work. Real registered service→binder→child→restart→release and exported built-path workflow pass.

Notes / Constraints:
- Missing separate authority work blocks production, not a reason to silently rewrite it. Build profile composition in isolated verification checkout; deployment/activation remains separately authorized. Regenerate artifacts; extend verifier suites/mappings first. Preserve v2-only downgrade refusal.

Workspace Actions:
- Record actual tested bytes, build paths, package pins, every prerequisite locator and source/build/profile workflow logs. Live check only under explicit runtime-owner authorization.

### Step: STEP-08 — Independent review, official design reconciliation and handoff (S5)
Objective:
Review final implementation against existing/approved design, freeze and all applicable T01–T23. Reconcile official design/source maps and exact source/build evidence, fix in-scope findings with design before code, and produce final supported-deployment handoff.

Recommended Mode:
Reviewing

Applicable Guidelines:
- `AGENTS.md`, Evidence before finalize
- `.ai-work/procedural/skills/aiws-aip/operations/run.md`, closing and capture sweep
- `docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md`, §§10–12

Recommended Skills:
- aiws-aip run
- aiws-lint task

Inputs:
- Official design, final source, decision/dependency records, acceptance matrix and raw test/build reports

Expected Outputs:
- `independent-review.md`, complete `acceptance-matrix.md`, synchronized official design/mappings/baselines and `implementation-handoff.md`
- Scoped strict lint, applicable whole-tree lint and design-verification reports

Done Condition:
Independent substantive review has no unresolved implementation blocker, all applicable acceptance checks and production prerequisites pass, and official design reflects delivered source. Conditional exclusions carry approved target/evidence; pending dependencies are reported without closing this full-delivery AIP.

Notes / Constraints:
- Luna can check ID/link/mapping completeness and summarize recorded checks; substantive lifecycle/authority review requires an appropriately capable independent reviewer. If WBS was separately adopted, apply approved run deltas to official design and report the mapping before close. No silent wiki/canonical promotion or lint suppression.

Workspace Actions:
- Resolve/defer captures through the HUMAN-controlled workflow, retain test exits/warnings, record approval and deployment status; only close after Done Criteria are satisfied.

## Acceptance and Verification Map

| Proposal requirements | Planned step / evidence |
|---|---|
| T01/T02/T09 — prepare-all, JCS/bounds/registry, migration | STEP-02; independent canonical vectors and raw replay fixtures |
| T03/T04/T05 — ordering, failure injection, concurrency/idempotency | STEP-03 fakes + STEP-04 real host + STEP-07 composition |
| T06 — scope/arguments/private-data isolation | STEP-06 + STEP-07 safe SDK/Web serialization |
| T07/T08 — recovery, mailbox admission, deadline/late cleanup | STEP-03 + STEP-05/06 real provider and barriers |
| T10 — exclusive ownership across Teams | STEP-05; reject second provision and preserve owner through physical cleanup |
| T11/T12 — coherent refresh, selective reads, unconfirmed candidate | STEP-06; public DA memory/composition checks |
| T13/T14 — authorization and nested delegation | STEP-07; full freeze §13 matrix from approved executor/mission owner |
| T15 — real service/binder/child and package compatibility | STEP-07; registered composition, restart/release, packed import/profile/installer |
| T16/T17/T18/T19/T20/T21 — closing/async/identity negatives | STEP-06/07; applicability follows proposal §11 and the approved execution model |
| T22 — result/turn/cleanup/task/acceptance separation | STEP-07; isolated outcome owner evidence when that target is approved |
| T23 — source/built entry/workflow and loaded-runtime distinction | STEP-07/08; actual built exports; live module evidence only if authorized |

The full freeze §13 fixture set also applies; the proposal matrix augments it. For a direct-continuable target, prove static labels, strict denial and actual supported lifecycle; mark isolated-only fixtures not applicable with approved selection evidence. Do not add isolated execution to satisfy a fixture. Blocked prerequisites are not test exclusions.

Verification commands are resolved on the selected supported environment. Existing entrypoints are `node --test installer/tests/*.test.mjs`, `node installer/verify.mjs --target "$GAT_BINDING_DSH_TARGET"` on an explicitly reviewed checkout, and DA pinned `build`/`check:named-exports` plus service/provider/Consumer/memory/composition suites. Extend verifier package/suite coverage before using it for the new adapter. Store exact commands, revisions/hashes, exit codes and raw reports; no API keys or incident Session reuse is needed for deterministic fixtures.

## Done Criteria

- [ ] Gate U1 approval and P-01–P-08/API/lifecycle/owner choices have evidence; U2 input understanding and U3 open-point dispositions are recorded.
- [ ] Each source change had prior reviewed intended design coverage; final official `docs/gat-design/` AD/BD/DD/integration/mappings reflect the delivered implementation.
- [ ] Generic binding, strict adapter, ownership, model tools/refresh and replay/recovery/deadline behavior conform to the freeze and approved proposal.
- [ ] T01–T23 and freeze §13 requirements have executed PASS evidence or approved conditional non-applicability; no required dependency remains blocked or is mislabeled as skipped.
- [ ] DSH/DA API/lifecycle, exact mission/task leases and nested executor capability prerequisites are qualified on pinned bytes; production integration is evidenced independently of fakes.
- [ ] Supported default GAT and Durable profiles, safe SDK/Web, build/exports/installer, v2/v3 replay and downgrade policy are verified on final bytes.
- [ ] Independent review findings resolved; task/design verification and strict scoped lint pass. Whole-tree issues, if any, are accurately reported and applicable canonical gates are satisfied.
- [ ] Captures receive explicit disposition; handoff names design sections, changed source, checks, deployment constraints and separate publication/activation authorization status.

## Self-check / Review Points

- Cross-check normalization ownership, exact prepared payload/digest and full record limits; test getters/cycles/non-JSON and late mutation independently.
- Check active-flush uncertainty, stable admission idempotency, retry versus new generation, quarantined mailbox recovery and incomplete cleanup ownership.
- Check raw attachment redaction across view/SDK serialization and model errors, and every asynchronous scope/authority boundary.
- Check strict declaration selection and unsupported API/lifecycle paths; current shortcuts cannot masquerade as authenticated authorization.
- Verify precise closing applicability, pre-collected owner-material removal, unrelated assembly preservation, late-body withholding and one cleanup owner without self-drain deadlock.
- Review actual exported/built paths and independent journal/provider observations; a mapped test or historical acceptance is not a fresh run.

## Finalization Notes

AIP creation finishes with this draft validated. Implementation completion is a later operation: run scoped lint through `aiws-lint task`, whole-tree lint when required, and approved design/build checks; report actual results without muting unrelated warnings. Reconcile target-spec attribution and accepted changes before setting `done`. Evidence bundles live in workspace, not this stable control file. Wiki/source registration changes are reviewed candidates and require their own promotion authorization.

## Pre-flight Pending Captures

- [IMPORTED 2026-10-04] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="docs/gat-design/DURABLE_AGENT_BINDING_PROPOSAL.md" lookup_query="DURABLE_AGENT_BINDING_PROPOSAL" reason="Reusable implementation handoff referenced as a shared structural input; lexical and semantic lookup and the GAT design catalog did not resolve this proposal; user-supplied path used after escalation. Review registration without promoting draft decisions to authority."
- [IMPORTED 2026-10-04] type="aip_template_improvement_candidate" candidate_kind="process_doc_gap" suggested_target="aip_template" artifact=".ai-work/aip/templates/AIP_EXEC_TEMPLATE.md" lookup_query="step input dependency locators" reason="Creation self-check corrected step_inputs_unresolvable by binding predecessor outputs to named workspace artifacts. Consider an Inputs example with concrete predecessor output locators in the template. Independent review also corrected the create skill's superseded capture kind to the current process_doc_gap family (default improvement_scope aiws); review that procedural example. Retain stable macro-control and keep runtime results in workspace."

## Re-plan Rule

Append a dated Re-plan Log entry before changing objective, scope, expected outputs, major API/lifecycle assumptions or execution ownership. Include trigger, change, evidence locator and approval. Keep runtime questions/results in workspace. Sweep the whole AIP, including frontmatter and every step, for obsolete content markers; classify intentional provenance and verify residual obsolete content is zero. Missing host/authorization dependencies do not justify fallback wiring, unbound execution or declaring foundation-only delivery complete.

## Re-plan Log

- No re-plan entries at creation.
