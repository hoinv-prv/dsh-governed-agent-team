# Control-Plane Stabilization Design v4

**Mission:** `multi-mission-web-ui`  
**Status:** Advisory corrected design; inactive; not WBS or execution authority  
**Decision owner:** HUMAN  
**Working AIP:** `AIP-EXEC-009`  
**Predecessor:** v3 SHA-256 `8fc33a7d5a09ed5eb53d90d4b34ccfee0b58d061342bd561c5d986f793824bf2`  
**Review state:** Corrected after run-004 `needs_revision`; requires a new high-risk council run before WBS build

## 1. Problem statement

The mission repeatedly entered a control loop:

```text
partial readiness check
  → charge attempt
  → mutate one or more control artifacts
  → discover a missing validator, unavailable capability, authority mismatch, or stale state
  → fail review/acceptance
  → pause and re-plan
```

Product-level causes existed, especially the late split of matrix, control state, handlers/reducers and runner assembly. They do not explain why governance failures continued after that split. The best-supported common control deficiency is the absence of one fail-closed pre-charge admission protocol that jointly attests time-bounded known readiness across every authoritative control surface. The evidence shows that such a gate would have detected each observed control failure before charge; it does not prove that fragmented admission was the sole cause of every historical failure.

This design stabilizes the procedural control plane before another WBS is built. It does not modify GAT product behavior, create a scheduler, replace native DSH/AIWS mechanisms, or authorize execution.

## 2. Evidence basis and root-cause classification

The evidence-bound failure model used for v4 is the immutable run-002 snapshot `snapshots/failure-model`, SHA-256 `434f1613751d8a2b5b8813936404e4567e698ea4ace88ed74863e2a56e4d8b86`; the mutable Workspace path is only its working source.

### 2.1 Systemic root cause

**RC-SYSTEM-01 (best-supported common control deficiency):** admission is fragmented. WBS validation, execution-ledger validity, AIP/ASC transition, goal/Team authority, command capability, reviewer availability, ownership/quiescence and budget slack are checked by different mechanisms at different times. The observed failures map to one or more missing pre-charge predicates, so a charge can be committed while another mandatory surface is already known invalid. This is not claimed as the sole causal explanation of every historical defect.

### 2.2 Counterfactual coverage of observed failures

| Observed control failure | Pre-charge predicate that would have failed |
|---|---|
| invalid/semantically incomplete WBS revision | P1/P2 plan identity and semantic closure |
| strict execution-ledger rejection | P3 ledger strict validity |
| missing generated ASC transition command or stale ASC | P6 AIP/ASC closure |
| unavailable sandbox/effect backend or undeclared command | P7 command authorization/capability |
| stale/contradictory coordinator, Goal, Team or active work | P8–P10 snapshot agreement |
| unavailable reviewer route or malformed review transport | P11 availability/fallback |
| no attempt slack for mandatory recovery | P12 budget safety |
| absent or misbound HUMAN authority | P13 authority |

This establishes control coverage, not exclusive historical causation and not non-bypassable runtime enforcement.

### 2.3 Contributing conditions

- product architecture was reviewed after implementation rather than before it;
- plan schema validation did not prove semantic command-to-deliverable closure;
- the mutable ledger accumulated incompatible historical representations;
- generated ASC state could be manually edited without a declared owning transition command;
- reviewer-route and sandbox capability were not observed and bound before charge;
- execution ledger and runtime goal could disagree on active/paused state;
- attempt allocation left no recovery reserve.

### 2.4 Symptoms, not root causes

- failed runner attempts;
- sandbox refusal on attempt 65;
- reviewer failure on attempt 66;
- stale or manually reconciled ASC;
- strict progress-render rejection;
- repeated selection/reconciliation attempts.

## 3. Design goals and non-goals

### 3.1 Goals

1. Make all execution readiness checks one closed, content-addressed admission decision.
2. Block charge with `EXPIRED` when drift is observed before commit; separately disclose bypass and the state-change window after the final observation as irreducible residual risks, never as permission to ignore observed drift.
3. Preserve uncertain/interrupted charges after commit; never roll them back or reuse them.
4. Prevent manual or undeclared transitions of generated control artifacts.
5. Separate immutable history from the small current execution projection.
6. Reserve review/recovery call budget and prove route availability before work begins without claiming provider capacity is held.
7. Produce deterministic evidence that a later WBS can cite literally.

### 3.2 Non-goals

- No new runtime service, daemon, scheduler, custom WBS runner, or automatic approval mechanism.
- No bypass of HUMAN decisions, native Team approval, Working AIP, Workspace, or DSH tools.
- No GAT product implementation or accepted-baseline execution.
- No rewrite of historical evidence without exact backup and a reviewed migration rule.
- No DSH checkout access, package install, network, activation, merge or deployment.

## 4. Responsibility boundaries

| Actor/component | Owns | Must not own |
|---|---|---|
| HUMAN decision owner | WBS approval, attempt-ceiling/reallocation, material deviation, required task acceptance, final design/WBS direction | Mechanical validation results or model-authored evidence |
| Coordinator | Read-only prepare phase, immutable admission bundle, charge-first commit, dispatch, verification collection, ledger projection | Self-review, HUMAN acceptance, silent migration or permission widening |
| WBS builder/helper | Plan format/hash/order and declared task/effect/command model | Runtime capability, ledger migration, task acceptance |
| WBS semantic review | Requirement/owner/control/failure/command-to-deliverable closure | Execution authority |
| Execution ledger | Current selected plan, attempts, active work, outcomes, acceptance refs | AIP macro content, Workspace narrative, reusable knowledge |
| Immutable history/evidence | Raw prior bytes, attempts, receipts, reviews and decisions | Mutable current readiness projection |
| AIP | Stable macro task scope/steps/gates | Runtime metrics or attempt ledger |
| Workspace/ASC | Runtime findings and generated active-step projection | Mission authority or durable history replacement |
| Goal runtime | Observable continuation arming | WBS approval or task acceptance |
| Team runtime | Current coordinator/member/work status and approved Team-plan revision | WBS plan authority |
| Reviewer pool | Independent candidate findings/verdicts | Mutation, dispatch, acceptance or preferred-outcome retries |
| Deterministic validators | Schema/hash/closure receipts | Semantic or HUMAN judgment beyond encoded rules |

Authority follows the pinned repository rule without abbreviation. Content precedence is **Truth → Project Wiki → Local Wiki → Common Wiki → History**. Artifact/rule precedence is **SOP → Contract → AIP PLAN/EXEC → Guidelines → Skills → Wiki → Workspace**. Knowledge-class precedence is **source_of_truth → curated → reference → history**. The GAT proposal is inactive, non-authoritative design intent; only separately recorded HUMAN decisions derived from it bind execution. This design is subordinate and inactive.

## 5. Admission state machine

```text
FROZEN
  └─prepare()──────────────────────────────────────────────┐
                                                           v
PREPARING ──any failed check──> NOT_READY (uncharged) ──re-prepare
  │
  └─all checks pinned + bundle sealed──> READY (uncharged)
                                          │
                                          ├─input/hash/state drift──> EXPIRED + AdmissionInvalidation (uncharged)
                                          │
                                          └─HUMAN exact approval valid
                                                │
                                                v
                                           COMMITTING
                                                │
                           first durable write = charge + attempt allocation + bundle/boundary binding
                                                │
                     ┌──────────────────────────┴─────────────────────────┐
                     v                                                    v
              ACTIVE/DISPATCHED                              INTERRUPTED_CHARGED
                     │                                        (preserve charge/evidence)
                     v
                  VERIFYING ──fail──> FAILED_CHARGED
                     │
                     v
                  REVIEWING ──reviewer transport fail──> REVIEW_PENDING
                     │                                      (same attempt)
                     ├─artifact finding──> REVISION_REQUIRED_CHARGED
                     v
                  ACCEPTED
```

### 5.1 Critical rule

No mutable mission control and no attempt charge is procedurally allowed in `FROZEN`, `PREPARING`, `NOT_READY`, `READY`, or `EXPIRED`. `READY` is not authority to execute; it only attests that the exact admission bundle was complete at its recorded hashes/epochs. Every live predicate must be re-observed immediately at the charge boundary; any drift expires the bundle.

### 5.2 Commit semantics

Cross-file atomicity is not claimed. The commit protocol is a logical write-ahead transaction:

1. Re-hash every bundle input and check current invalidation records immediately before commit.
2. Confirm the exact HUMAN WBS decision and active goal/Team authority still match; re-observe all live P7–P11 predicates.
3. **Abort branch:** if steps 1–2 do not return fresh PASS, if observation is unavailable, or if any value drifts, perform no durable mission mutation, consume no attempt ID, append only an immutable uncharged `AdmissionInvalidation` evidence record for the bundle hash, and transition the candidate to `EXPIRED`/`NOT_READY` before re-prepare.
4. **Charge branch:** steps 5–6 may run only when steps 1–2 produced fresh PASS receipts and no current invalidation exists.
5. Append one attempt allocation, boundary receipt and cumulative charge in a single version-guarded `execution.json` update as the first durable mission mutation.
6. Apply only the already-declared task mutations.
7. If any post-charge mutation or dispatch fails, mark the same attempt `interrupted` or `failed`; preserve its charge and evidence. Never return to `READY` using that attempt ID.

The design detects known unreadiness before charge; it does not pretend failures after a legitimate charge can be undone.

### 5.3 Enforcement boundary and residual race

No existing pinned Source of Truth identifies a non-bypassable native charge entry point that consumes an AdmissionBundle. Therefore v4 claims **procedural fail-closed governance**, not hard runtime enforcement. The coordinator must bind the bundle hash to the immediately following charge record and re-observe live goal, Team, worker/job, sandbox and reviewer-availability predicates at that boundary. An irreducible check-to-charge race remains when external state can change between observation and mutation.

Hard prevention of bypass or a true compare-and-swap charge requires a separately approved DSH/runtime change and is outside this design. Until such a capability exists, any path that cannot demonstrate coordinator compliance and boundary re-observation is `NOT_READY`; the residual enforcement/race risk must be visible to the HUMAN in the WBS approval packet.

## 6. Immutable AdmissionBundle

A later WBS must require one immutable `AdmissionBundle` per charged attempt. It is an evidence artifact, not a new runtime service.

```yaml
record_type: AdmissionBundle
contract_status: proposed-design-contract-not-yet-activated
contract_ref: <HUMAN-approved persisted schema path+sha256; absent means NOT_READY>
validator_ref: <approved deterministic validator path+sha256 and exact argv; absent means NOT_READY>
mission_id: multi-mission-web-ui
wbs_revision: <n>
wbs_sha256: <sha256>
task_id: <task>
proposed_attempt_id: <id>
prepared_by: <coordinator identity>
enforcement_mode: procedural-coordinator-gate
prepared_from:
  execution_sha256: <sha256>
  decisions_sha256: <sha256>
  aip_sha256: <sha256>
  current_step_sha256: <sha256>
  asc_sha256: <sha256>
receipts:
  plan_format: <path+sha256>
  plan_semantics: <path+sha256>
  execution_strict: <path+sha256>
  dependency_acceptance: <path+sha256>
  source_integrity: <path+sha256; includes every task input>
  design_basis: <v4 design path+sha256 plus immutable run-002 failure-model snapshot path+sha256>
  aip_asc_transition: <path+sha256>
  command_capability: <path+sha256>
  coordinator_quiescence: <path+sha256>
  team_authority: <path+sha256>
  goal_activation: <path+sha256>
  reviewer_availability: <path+sha256>
  budget_reserve: <path+sha256>
prepared_epoch: <native state sequence/timestamp set>
freshness_rule: <explicit expiry/drift predicate>
charge_boundary_policy: coordinator version-guarded execution-ledger update authorized by exact HUMAN-approved WBS/effects
state: READY
```

Every receipt records exact argv/tool identity where applicable, exit/result, canonical paths, raw-byte hashes, captured native identities, observation epoch/sequence and an explicit freshness rule. Missing, stale, replayed, ambiguous or degraded material makes the bundle `NOT_READY`; silence is failure.

### 6.1 Contract and operation ownership bootstrap

`AdmissionBundle` above is a **proposed design contract**, not an existing authoritative schema. Before any successor WBS is built, a separately HUMAN-authorized control-plane stabilization action must persist and approve: (a) the exact schema bytes and SHA-256; (b) a deterministic validator and its exact `python3 <approved-validator-path> validate <bundle-path>` argv; and (c) the coordinator-owned read-only prepare operation and exact `python3 <approved-prepare-path> prepare ...` argv. Until those real paths/hashes/commands exist and pass, admission is `NOT_READY`; v4 does not invent them or claim P1/P2 mechanical validation.

After bootstrap, the coordinator owns bundle production through that approved read-only prepare command. The coordinator also owns the first durable charge/boundary mutation through one version-guarded `execution.json` update using the runtime's native guarded file write/edit operation, bounded by the HUMAN-approved WBS hash and declared write effect. A stale-version conflict, failed predicate, unavailable guard or missing authority aborts with no charge and no attempt allocation. The operation must re-observe live predicates and bind the immutable bundle hash, boundary receipt and allocated attempt ID in the one ledger update. This is attributable procedural ownership, not a non-bypassable native DSH hook.

### 6.2 Immutable invalidation representation

A sealed bundle never changes. When drift, withdrawal or failed re-observation is detected, the coordinator appends an immutable uncharged `AdmissionInvalidation` evidence record containing `bundle_sha256`, reason code, observed prior/current values or unavailable predicate, actor identity and observation sequence. The approved charge operation must check the append-only invalidation index immediately before its ledger write; any record for the bundle hash blocks charge. The sealed `READY` bundle proves only a past observation and is never current-validity evidence by itself.

## 7. Admission invariants and evidence

| Invariant | Mandatory evidence before charge | Failure disposition |
|---|---|---|
| P1 Plan identity | Official WBS validate/order/hash receipt; exact plan bytes unchanged | `NOT_READY` |
| P2 Plan semantic closure | Closed matrix mapping each deliverable/output to declared write path, owning command or permitted file operation, verifier, reviewer and acceptance owner | `NOT_READY`; revise plan |
| P3 Ledger strict validity | Official strict execution/progress validator PASS over exact `execution.json` | `NOT_READY`; migrate/repair separately |
| P4 Dependency acceptance | Every hard dependency has valid verification, required review and acceptance refs whose output hashes still match | `NOT_READY` |
| P5 Source/design-basis integrity | All pinned immutable task-input hashes match current bytes; stabilization/WBS-build admission also re-hashes the current design and run-002 failure-model snapshot `434f1613…d8b86` through the declared read-only hashing command | `NOT_READY`; invalidate carry-forward |
| P6 AIP/ASC closure | AIP lint PASS; declared `run_aip` transition produces fresh ASC; pointer/AIP/Workspace/task all agree | `NOT_READY` |
| P7 Command authorization/capability | Exact argv appears in the pinned root/task allowed-command union whose hash is recorded; argv/cwd paths resolve; required effect backend is observed available; prohibited effects remain denied | `NOT_READY` |
| P8 Coordinator/quiescence snapshot | One coordinator identity; enumerate every observable mission-bound agent/job and record stopped/settled evidence; `active_work` equals the same snapshot | `NOT_READY` when enumeration or settlement is unavailable; snapshot expires on native-state change |
| P9 Team authority | Native Team plan revision is current and HUMAN-approved when Team execution is required; required members available | `NOT_READY` |
| P10 Goal activation | Goal identity/objective/hash agree and runtime reports active/armed when autonomous continuation is promised | `NOT_READY`; no promise of continuation |
| P11 Reviewer availability/fallback | Live route discovery shows required independent routes and one fallback; packet identity and typed retry policy are pinned; no capacity reservation is claimed unless a real provider primitive is named | `NOT_READY` when routes are unavailable; otherwise record double-booking/provider-loss residual risk |
| P12 Budget safety | Charge ceiling covers selected attempt plus all mandatory downstream minima and mission-specific contingency reserve | `NOT_READY`; HUMAN decides ceiling/reallocation |
| P13 Authority | Exact HUMAN decision binds current WBS hash/effects; no review/report is treated as approval | `NOT_READY` |
| P14 Bundle freshness/invalidation | All current hashes/native states still equal the sealed bundle immediately before commit and no current `AdmissionInvalidation` exists for its hash | `EXPIRED`; abort with no mission write or attempt consumption; append uncharged invalidation evidence; re-prepare |
| P15 Admission mechanism bootstrap | HUMAN-approved bundle/invalidation contract hashes, deterministic validator argv, prepare argv and version-guarded ledger write capability all exist and pass | `NOT_READY`; complete separately authorized control-plane bootstrap before WBS build |

### 7.1 Mission-specific contingency rule

The next WBS must reserve at least:

- one attempt for future plan-selection/reconciliation after a material reviewed correction; and
- one attempt for a runtime/tooling recovery that cannot reuse an implementation attempt.

The design recommends **two attempts** as the mission-specific contingency reserve. Only the HUMAN decision owner may select or change the operative amount; council output is advisory and cannot set it. The reserve cannot be silently borrowed by product tasks. Because the currently selected **WBS revision 32** (not this design's revision) has no slack, no successor WBS may be built or admitted until the HUMAN records a ceiling/reallocation and contingency decision bound to that successor's exact WBS revision and SHA-256; Section 16 repeats the same gate.

## 8. Semantic plan-closure review

Official schema validation remains mandatory but is insufficient. Before presenting a WBS for approval, a semantic closure matrix must answer for every task:

1. What exact state transition/deliverable is required?
2. Which actor/component owns it?
3. Is it produced by a declared command or permitted file operation?
4. For generated artifacts, is the canonical owning command declared?
5. Can every command run under the current backend without widening effects?
6. What negative path proves the control fails closed?
7. Who verifies, who reviews, who accepts, and are those roles non-conflicting?
8. What dependency evidence makes the task ready?
9. What happens on command denial, reviewer transport failure, crash after charge or hash drift?
10. Does the attempt and contingency arithmetic close?

A WBS cannot be labelled execution-ready while any row is incomplete, even if its format helper passes.

## 9. Ledger stabilization and migration

### 9.1 Freeze rule

The current `execution.json` remains frozen until a separately HUMAN-authorized migration action. Reporting or design work must not normalize it in place. Because P3 deliberately blocks charging any WBS attempt against the known strict-invalid ledger, this one-time migration is **uncharged control-plane maintenance performed before successor-WBS build**, not a product or WBS execution attempt and not acceptance evidence. The HUMAN authorization must bind exact source hash, target contract, allowed write path and no-product-effect boundary. The coordinator is the migration-operation owner, a separate verifier and reviewer validate the candidate, and only the HUMAN accepts/selects migrated bytes.

### 9.2 Migration protocol

1. Copy exact pre-migration bytes to a new immutable evidence directory and record SHA-256.
2. Pin the authoritative target `dsh-wbs-execution/1` contract/tool version.
3. Inventory every incompatible field and classify it as lossless-known, conflicting or unrelated damage.
4. Transform only lossless-known fields using a reviewed deterministic mapping.
5. On duplicate/conflicting paths, missing provenance or ambiguous acceptance, stop; do not choose a value.
6. Preserve historical attempts, charges, output hashes, reviews and HUMAN decisions byte-for-byte or by reversible reference.
7. Write a small current projection separately from immutable historical evidence when the contract permits it; otherwise keep the single-file contract and record the constraint.
8. Run strict validator and execution-backed progress rendering on the exact candidate bytes.
9. Independently review the before/after mapping and no-loss proof.
10. HUMAN accepts the migration bytes before selection of a product WBS.
11. If strict validation/report rendering or independent review fails, the migration owner stops, retains the exact original/candidate bytes and hashes, restores the recorded pre-migration current bytes through the declared owning file operation, reruns the same strict validator, records no selection, and returns to step 3 with a new candidate identity.

### 9.3 Migration acceptance

Migration passes only when:

- original bytes and hash remain available;
- every field has a deterministic before→after trace;
- charges and attempt identities are identical;
- accepted/interrupted/failed distinctions are unchanged;
- strict validation and execution-backed report both pass;
- no task becomes accepted or ready solely because of migration.

## 10. Generated and mutable mission-control ownership policy

- AIP remains stable macro-control; runtime facts remain in Workspace.
- Every generated or mutable mission-control artifact has exactly one declared owner and write mechanism in the approved closure matrix: AIP pointer/ASC → exact `run_aip.py start|resume|step` argv; execution ledger/current projection → coordinator through the declared migration operation or one version-guarded native file write/edit; progress/report rendering → the official read-only renderer; AdmissionBundle → coordinator through the separately approved prepare command; AdmissionInvalidation → coordinator through the same approved evidence append operation; charge/boundary record → coordinator through the single version-guarded `execution.json` write bounded by HUMAN-approved WBS/effects.
- Every WBS task requiring one of these transitions must declare the exact argv or permitted file operation, canonical path, effect scope and verifier. A migration projection may be written only by the migration operation named in the approved closure matrix.
- Manual or undeclared edits to ASC, execution/current projection, AdmissionBundle, charge record or report are invalid as acceptance/admission evidence and force `NOT_READY` until restored and re-verified.
- `status` can inspect but cannot satisfy a transition requirement.
- Freshness and raw-byte hash must be observed after the final authorized mutation for every control artifact; a pre-write observation cannot satisfy the post-write receipt.

## 11. Command and sandbox capability preflight

Capability preflight does not execute product behavior. It records only that, at the stated observation epoch:

- executable names and referenced files exist at canonical paths;
- cwd is readable and declared;
- required sandbox/effect mode is available;
- timeout and output evidence can be collected;
- no command resolves through a forbidden symlink or external package store;
- exact command is included in root/task unions.

A capability receipt must distinguish `available`, `denied`, `unavailable`, and `not_probed`. `not_probed` is not PASS. A later task-command failure remains a charged attempt outcome, but an already-known unavailable backend must never be discovered after charging.

## 12. Reviewer availability and fallback

Before charge:

1. Determine required rubric, independence, model diversity and HUMAN gate.
2. Inspect live routes for the primary reviewer and one fallback with distinct invocation identity; record availability as a snapshot, not a provider-capacity reservation.
3. Persist reviewer restrictions, packet hashes, retry policy and evidence paths in the admission bundle.
4. A provider/transport/schema failure before valid verdict permits one typed retry or fallback on identical packet bytes without a new implementation attempt.
5. A valid adverse verdict is never retried to seek PASS; it requires disposition/revision.
6. Reviewer output remains advisory until the attributable HUMAN acceptance owner acts.
7. The coordinator may record/project an exact HUMAN decision but can never originate required acceptance. Any alternate acceptor requires a separately recorded HUMAN authority decision before admission; a task-declared rule cannot transfer that authority.

For high-risk design/governance reviews, use two independent internal lanes from distinct model families, a sanitized outside-view lane, conditional adjudication and a separate Chairman. Reserve worst-case **call budget** before dispatch; do not claim provider capacity is held unless a named provider primitive proves it. Record route loss and double-booking as residual risks.

## 13. Goal, Team and ownership synchronization

Admission requires a single snapshot proving:

```text
execution.coordinator == native Team Lead/coordinator
execution.active_work == native active workers/jobs for the mission
goal.objective binds mission + WBS hash
goal.phase == active and activation == armed when autonomous continuation is claimed
Team plan revision == current HUMAN-approved revision when Team execution is used
```

Any mismatch blocks charge. A user message requesting continuation is authority evidence but does not substitute for the runtime goal reporting armed. If the runtime rejects resume, report the blocker and do not promise autonomous completion.

## 14. Failure, rollback and recovery matrix

| Failure point | Before/after charge | Required response |
|---|---|---|
| Plan/helper/semantic closure fails | before | `NOT_READY`; correct and re-review without charge |
| Strict ledger validation fails | before | freeze; perform separate reviewed migration |
| Source/dependency hash drifts | before | expire bundle; invalidate affected acceptance |
| AIP/ASC transition missing | before | revise WBS to declare owning command |
| Sandbox/effect unavailable | before | `NOT_READY`; do not dispatch through workaround |
| Reviewer unavailable | before | use a previously discovered fallback after a fresh probe, or remain `NOT_READY`; no capacity reservation is implied |
| Goal/Team authority mismatch | before | remain frozen; HUMAN/runtime resolves |
| State changes after bundle sealed or at charge-boundary re-observation | before | `EXPIRED`; rebuild bundle without charge |
| Crash after charge but before dispatch | after | preserve charged attempt as interrupted; reconcile from write-ahead record |
| Worker/result uncertain | after | preserve charge and uncertainty; no acceptance |
| Verification fails | after | failed charged attempt; use remaining declared retry only |
| Reviewer transport fails | after | retry identical review packet via a freshly probed fallback; same implementation attempt |
| Reviewer finds material defect | after | task remains unaccepted; correction follows WBS budget |
| HUMAN rejects | after | record reject; dependents remain blocked |

## 15. Verification strategy for this design

Council must challenge at least these scenarios:

1. valid WBS but invalid legacy ledger;
2. valid schema but missing ASC transition command;
3. reviewer disappears before verdict;
4. goal paused while execution ledger says active;
5. Team-plan revision changes after bundle creation;
6. sandbox disappears after capability receipt;
7. source hash changes between prepare and commit;
8. crash immediately after charge;
9. conflicting legacy hash entries during migration;
10. zero attempt slack;
11. coordinator is also acceptance owner while HUMAN review is required;
12. a report/helper claims PASS without execution-state closure.

A finding is material when it permits charge despite known unreadiness, loses/reuses a charge, changes acceptance, permits undeclared effects, or allows a non-HUMAN artifact to grant authority.

## 16. WBS-build entry criteria

A new WBS may be built only after:

- latest stabilization design bytes receive council `pass` or `pass_with_notes`;
- every material council finding is confirmed/refuted/dispositioned;
- HUMAN selects the attempt-ceiling/reallocation and contingency policy;
- HUMAN authorizes the one-time uncharged ledger-maintenance boundary; migration completes; exact selected bytes pass strict validation and independent review without changing charges/acceptance;
- the AdmissionBundle/Invalidation schema, deterministic validator, prepare command and version-guarded coordinator ledger-write path are persisted, hash-pinned, independently reviewed and HUMAN-approved as control-plane bootstrap;
- exact no-DSH/no-network/no-install/product boundaries remain explicit;
- the HUMAN-facing approval packet explicitly discloses that the admission gate is procedural/non-bypassable only by coordinator compliance and retains an external-state TOCTOU residual risk;
- WBS-build handoff lists every required task, effect, command, source, verifier, reviewer, acceptance owner, stop condition, bundle/invalidation contract reference and residual-risk disclosure.

The subsequent WBS must start with an uncharged admission proof followed by the first bound charge operation; product matrix/control/runner tasks remain blocked until that proof is accepted. Ledger migration and admission-mechanism bootstrap are pre-WBS control-plane prerequisites, not tasks hidden inside a WBS whose own P3/P15 could not yet pass.

## 17. Design acceptance boundary

Council review is advisory. A council `pass` does not approve this design, build a WBS, resume the mission, charge an attempt, accept attempt 66, or activate GAT. Those remain separate HUMAN decisions.
