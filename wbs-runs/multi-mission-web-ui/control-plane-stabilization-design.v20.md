# Control-Plane Stabilization Design v20

**Mission:** `multi-mission-web-ui`  
**Status:** Advisory corrected design; inactive; not WBS or execution authority  
**Decision owner:** HUMAN  
**Working AIP:** `AIP-EXEC-009`  
**Predecessor:** v19 SHA-256 `1f6a6f81ddbe6e263b277483a5457f4009d1cef96d7cfcad4888aaff6ec092a6`  
**Review state:** Corrected after formal run-020 `needs_revision`; requires a new high-risk council run before WBS build

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

The evidence-bound failure model used for v20 is the immutable run-002 snapshot `snapshots/failure-model`, SHA-256 `434f1613751d8a2b5b8813936404e4567e698ea4ace88ed74863e2a56e4d8b86`; the mutable Workspace path is only its working source.

### 2.1 Systemic root cause

**RC-SYSTEM-01 (best-supported common control deficiency):** admission is fragmented. WBS validation, execution-ledger validity, AIP/ASC transition, goal/Team authority, command capability, reviewer availability, ownership/quiescence and budget slack are checked by different mechanisms at different times. The observed failures map to one or more missing pre-charge predicates, so a charge can be committed while another mandatory surface is already known invalid. This is not claimed as the sole causal explanation of every historical defect.

### 2.2 Counterfactual coverage of observed failures

| Observed control failure | Pre-charge predicate that would have failed |
|---|---|
| invalid/semantically incomplete WBS revision | P1/P2 plan identity and semantic closure |
| strict execution-ledger rejection | P3 ledger strict validity |
| missing generated ASC transition command or stale ASC | P6 AIP/ASC closure |
| unavailable sandbox/effect backend or undeclared command | P7 command authorization/capability |
| stale/contradictory coordinator, Goal, Team, active work or execution-ledger run state | P8–P10 same-epoch snapshot and ledger↔goal equality |
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
  ├─exact HUMAN bootstrap authorization──> BOOTSTRAP_MAINTENANCE ──verified/reviewed + HUMAN accepted──> FROZEN
  │                                      └─failure/ceiling/scope breach──> BOOTSTRAP_BLOCKED
  │                                                                         ├─fresh HUMAN recovery authorization──> BOOTSTRAP_MAINTENANCE
  │                                                                         └─exact no-effect/restore proof + HUMAN close──> FROZEN
  ├─exact HUMAN migration-maintenance authorization──> MIGRATION_MAINTENANCE
  │                                                      ├─failure──> MIGRATION_RECOVERY
  │                                                      │              ├─exact restore proof──> FROZEN
  │                                                      │              └─restore mismatch──> MIGRATION_BLOCKED
  │                                                      │                                           ├─fresh HUMAN recovery authorization──> MIGRATION_RECOVERY
  │                                                      │                                           └─HUMAN abandon decision──> MIGRATION_BLOCKED (terminal frozen)
  │                                                      └─candidate verified/reviewed + HUMAN accepted──> FROZEN(new base)
  └─prepare()──────────────────────────────────────────────┐
                                                           v
PREPARING ──any failed check──> NOT_READY (uncharged) ──re-prepare
  │
  └─all checks pinned + bundle sealed──> READY (uncharged)
                                          │
                                          ├─input/hash/state drift──> EXPIRED + AdmissionInvalidation (uncharged)
                                          │
                                          └─HUMAN exact WBS approval valid
                                                │
                                                v
                                           COMMITTING
                                                │
                           first durable write = charge + attempt allocation + bundle/boundary binding
                                                │
                     ┌──────────────────────────┴─────────────────────────┐
                     v                                                    v
              ACTIVE/DISPATCHED                              INTERRUPTED_CHARGED
                                                               ├─HUMAN resume_same_attempt + revalidation──> ACTIVE/DISPATCHED
                                                               ├─HUMAN close_failed──> FAILED_CHARGED
                                                               └─missing/invalid authority──> INTERRUPTED_CHARGED
                     │                                        (preserve charge/evidence)
                     v
                  VERIFYING ──fail──> FAILED_CHARGED
                     │
                     v
                  REVIEWING ──transport fail──> REVIEW_PENDING (same attempt)
                                                               ├─bound route restored/authorized──> REVIEWING (identical packet)
                                                               └─HUMAN terminal decision──> REVIEW_UNAVAILABLE_CHARGED (unaccepted)
                     │
                     ├─artifact finding──> REVISION_REQUIRED_CHARGED
                     └─ReviewClosureReceipt PASS(pass/pass_with_notes)──> AWAITING_HUMAN_ACCEPTANCE
                                          ├─missing/stale/revoked authority──> ACCEPTANCE_PENDING ──fresh HUMAN chain/decision──> AWAITING_HUMAN_ACCEPTANCE
                                          └─exact HUMAN accept/reject decision──> ACCEPTANCE_VERIFYING
                                                                 ├─independent confirmed──> exact ACCEPTED/REJECTED_CHARGED
                                                                 ├─refuted──> ACCEPTANCE_VERIFICATION_FAILED
                                                                 └─unavailable/inconclusive──> ACCEPTANCE_VERIFICATION_PENDING
                                          ├─first/final projection mismatch──> ACCEPTANCE_PROJECTION_REPAIR_REQUIRED
                                           └─repair outcome remains bound to failed edge
                                                                         ├─bound repair succeeds──> original ACCEPTED/REJECTED_CHARGED target
                                                                         └─failure/drift──> ACCEPTANCE_PROJECTION_REPAIR_BLOCKED
```

### 5.1 Critical rule

No mutable mission ledger, selected-plan state, task/product state, acceptance state or attempt charge is procedurally allowed in `FROZEN`, `PREPARING`, `NOT_READY`, `READY`, or `EXPIRED`. Within the normal admission lifecycle, the only pre-charge writes are six coordinator-owned, uncharged control/evidence effects separately approved under P15: (a) on the `FROZEN → PREPARING` edge, the exact AIP-declared `python3 .ai-work/tooling/run_aip.py start|resume|step ...` transition may update only the AIP pointer/ASC and canonical Workspace control evidence, with argv/tool hash, before/after hashes, native sequence and observation epoch recorded in the P6 receipt; (b) create-once persistence of exact sealed `AdmissionBundle` bytes at the content-addressed canonical bundle path; (c) append of one immutable `AdmissionInvalidation` through the approved append operation; and (d) ordered create-once content-addressed persistence of the exact pre-write execution-source bytes, strictly validated candidate bytes and inline fresh P14/boundary receipt plus recomputable raw observation bytes immediately before charge, followed by a separate version-guarded `TransitionIntentIndex` OPEN append, through exact P15-approved seal/index argv and receipts; and (e) ordered create-once persistence of a `NOT_APPLIED` `ExecutionTransitionCompletion` for an abandoned pre-charge intent followed by a separate version-guarded matching index CLOSE append, through exact P15-bound completion/index argv, content-addressed paths, receipts and validators. Effect (e) is coordinator-owned, may reference only its existing intent, must strict-validate and is charged to the common administrative ledger's pre-charge-admission allocation; it cannot write `execution.json`, allocate/consume an attempt, change charge count, create APPLIED, or mutate task/product/acceptance state, and differing existing bytes or persistence failure leaves `NOT_READY` pending HUMAN-authorized recovery; and (f) guarded append(s) to the canonical `AdministrativeResourceLedger` plus the append primitive's exempt operation receipt, only through the exact P15-bound argv/path/effect and reservation described in Section 6.3. Effect (f) runs first to reserve the admission envelope and then only to record operations against that reservation; append/receipt mismatch or failure enters `ADMISSION_ACCOUNTING_BLOCKED`, permits no mission-ledger/task write, and exits only through fresh HUMAN-authorized administrative-ledger recovery under the same reservation/ceiling. None may allocate/consume an attempt or mutate mission-ledger/product/acceptance bytes; the AIP transition is limited to declared pointer/ASC/Workspace-control paths, bundle sealing cannot overwrite, and the invalidation operation may change only its canonical append-only index. `READY` is not authority to execute; it only attests that the exact admission bundle was complete at its recorded hashes/epochs. Every live predicate must be re-observed immediately at the charge boundary; any drift expires the bundle. Two administrative states remain outside normal admission: Section 6.3 `BOOTSTRAP_MAINTENANCE` may write only its HUMAN-bounded schema/tool/evidence paths and Section 9 `MIGRATION_MAINTENANCE` is the sole ledger-write exception before valid P3. Neither is READY/COMMITTING or may allocate a mission attempt; bootstrap must return exact HUMAN-accepted capability hashes, and migration must return an accepted migrated-base hash or exact restore proof, to `FROZEN` before admission begins.

### 5.2 Commit semantics

Cross-file atomicity is not claimed. The commit protocol is a logical write-ahead transaction:

1. Execute P14 in full immediately before commit: re-hash every bundle input and every P13/P15/P16 authority/delegation record; on first post-migration charge re-hash every `migration_authority` lineage link; re-check current scope, actor/owner chain and revocation for each; and re-read the canonical invalidation index under its sealed prefix-extension rule, predicate scope and comparison basis of native sequence plus recorded epoch.
2. Under that identical rule/scope/basis, confirm exact HUMAN WBS and active goal/Team authority still match and re-observe every live P7–P11 predicate. Any missing/unavailable/drifted/revoked authority, scope or migration-lineage link takes the uncharged abort branch; a timestamp window never overrides changed native state.
3. **Abort branch:** if steps 1–2 do not return fresh PASS, the live check uses a different/missing rule, epoch, sequence or scope, observation is unavailable, or any value drifts, perform no durable mission mutation, consume no attempt ID, use only the approved invalidation-append operation to append one immutable uncharged `AdmissionInvalidation`, and transition the candidate to `EXPIRED`/`NOT_READY` before re-prepare. If that append fails, remain `NOT_READY`, perform no ledger/task write, record the unavailable evidence outside mission controls, and require HUMAN/runtime repair before another prepare.
4. Before this mechanism may exist, a separate HUMAN-authorized execution-contract decision must choose exactly one proven representation: **(a)** exact existing `dsh-wbs-execution/1` JSON pointers for attempt allocation, cumulative charge, bundle hash, seal hash, boundary-receipt hash, lineage and attempt ID, accompanied by a strict-validator-passing fixture/hash; or **(b)** exact bytes/hash of a versioned execution-contract extension plus validator and migration accepted under Section 9. If neither is proven, P15 is `NOT_READY`; no field is invented. Using only the selected representation, construct an in-memory candidate template without claiming a final boundary receipt; do not seal or write it yet.
5. **Fresh boundary construction:** perform the full step-1 P14/live-authority/invalidation and P7–P12 re-observation, emit one deterministic boundary receipt with inline raw observation bytes/native sequences/epochs, and require PASS. Any failure takes the abort branch.
6. Deterministically construct the final candidate from the template plus that exact boundary-receipt hash; strict-validate it, then create-once persist/re-read/hash-validate one charge `ExecutionTransitionIntent` containing exact source, candidate, boundary receipt and raw evidence. The boundary receipt carries one canonical aggregate identity over every exact P1–P16/P14 input byte/hash plus all native sequences/epochs. Immediately before the guarded write, the exact P15-bound writer re-reads and re-hashes **every** member (WBS, dependencies/acceptance refs, design/source inputs, AIP/pointer/ASC/Workspace, execution source, invalidation index, authority/delegation/revocation records, Goal/Team/worker/capability/reviewer state, immutable `AdmissionResourceReservation` identity/ceiling deduction (not mutable post-reservation usage), planned `TransitionIntentIndex` prior hash plus exact new intent identity, and all remaining bundle inputs), recomputes that aggregate and requires exact equality to the receipt; omission, unavailable read or mismatch aborts with no ledger write. The writer also performs the Section 6.3 reservation-prefix/current-usage reconciliation and exact `P3_IN_FLIGHT` index validation; both results/current hashes are bound into the `GuardedWriteReceipt`. This final check creates no replacement boundary receipt. Any mismatch closes the intent `NOT_APPLIED`, invalidates when authorized and re-prepares. Complete equality permits exactly one version-guarded `execution.json` update as the first durable mission mutation; re-hash equal and strict-validate before dispatch. The disclosed irreducible race after the last equality read remains; no atomicity claim is added.
7. After persisted-byte equality and strict PASS, enter `CHARGED_ACCOUNTING_PENDING` and execute the Section 6.3 charged accounting/completion/index-close order. Only after validated exact-writer `GuardedWriteReceipt`, its exact usage entry/append receipt, the pre-appended completion-attempt usage entry, create-once APPLIED `ExecutionTransitionCompletion`, the pre-appended index-close-attempt usage entry, matching CLOSE/receipt, final reservation reconciliation, and ordinary P3 with zero open intents may the coordinator apply declared task mutations and dispatch. If persisted equality/validation fails, dispatch nothing and enter `POST_CHARGE_REPAIR_REQUIRED`: preserve exact sealed pre-write/candidate bytes, invalid persisted bytes/hash/version, validator output, attempt ID and cumulative charge. A fresh HUMAN repair decision must bind those hashes, the same attempt/charge, exact failed-state target bytes/hash, one coordinator-owned version-guarded repair operation/effect, administrative-ledger remaining ceiling, independent verifier/reviewer and no-new-attempt rule. `POST_CHARGE_REPAIRING` permits exactly one write from the bound invalid source version to the prevalidated repair candidate; persisted bytes must hash-equal and strict-validate, then independent verification/review plus HUMAN repair-byte acceptance closes as `FAILED_CHARGED`. The immutable repair receipt links sealed pre-write → charged candidate → invalid persisted → repaired strict-valid bytes and becomes an exceptional P3 lineage link for that same attempt/charge. Any mismatch/failure/ceiling breach enters `POST_CHARGE_REPAIR_BLOCKED`; only a fresh equally bound HUMAN decision may retry, never a new attempt or silent restore.
8. If any later post-charge mutation or dispatch fails, use a Section 9.1 transition receipt to mark the same attempt `INTERRUPTED_CHARGED` or `FAILED_CHARGED`; preserve its charge and evidence. Never return to `READY` using that attempt ID.

`INTERRUPTED_CHARGED` is procedurally owned by the coordinator but authorizes no dispatch by itself. A fresh attributable HUMAN interruption-disposition record must bind the same attempt/charge, bundle/seal/boundary hashes, interruption evidence, exact remaining commands/effects/resources, resume-count ceiling, designated-owner/delegation chain and either `resume_same_attempt` or `close_failed`. For resume, the coordinator revalidates current dependencies/source hashes, P7–P11 capabilities/state and P13/P15 scope/revocation; any drift beyond the original bound effects forbids resume. A valid decision plus PASS uses a named `interrupted_to_dispatched` `ExecutionTransitionIntent`/`ExecutionTransitionCompletion` pair and dispatches the same attempt without a charge/allocation change. `close_failed` uses `interrupted_to_failed`; unavailable/invalid authority or failed revalidation remains `INTERRUPTED_CHARGED`. Exhausted resume count requires HUMAN closure as failed; no implicit retry/new attempt.

The design detects known unreadiness before charge; it does not pretend failures after a legitimate charge can be undone.

### 5.3 Enforcement boundary and residual race

No existing pinned Source of Truth identifies a non-bypassable native charge entry point that consumes an AdmissionBundle. Therefore v20 claims **procedural fail-closed governance**, not hard runtime enforcement. The coordinator must bind the bundle hash to the immediately following charge record and re-observe live goal, Team, worker/job, sandbox and reviewer-availability predicates at that boundary. An irreducible check-to-charge race remains when external state can change between observation and mutation. A delegated or otherwise capable writer may also bypass the procedural single-coordinator path because no native capability denial is established; P8 observes topology/quiescence but does not prove such a writer is technically unable to charge.

Hard prevention of bypass or a true compare-and-swap charge requires a separately approved DSH/runtime change and is outside this design. Until such a capability exists, any path that cannot demonstrate coordinator compliance and boundary re-observation is `NOT_READY`; the residual enforcement/race risk must be visible to the HUMAN in the WBS approval packet.

### 5.4 Acceptance boundary

A validator-backed `ReviewClosureReceipt` PASS with verdict `pass` or `pass_with_notes` never implies acceptance; it only moves the charged attempt to `AWAITING_HUMAN_ACCEPTANCE`. The acceptance owner must be `actor.kind = human`—either the designated mission decision owner or a HUMAN actor reached through a complete hash-pinned, non-revoked HUMAN delegation chain from that owner with exact task/scope at every link—and must provide a fresh attributable decision whose raw record binds the exact mission/WBS/task/attempt, output and verifier hashes, review/report hashes, accept-or-reject action, scope and current P16 owner/delegation record plus revocation state. A non-HUMAN delegate is invalid even if some HUMAN record names it. Missing, stale, ambiguous, non-HUMAN or revoked authority enters coordinator-owned `ACCEPTANCE_PENDING`, which authorizes no acceptance write. A fresh/superseding HUMAN owner/delegation and accept-or-reject decision revalidated under P16 returns to `AWAITING_HUMAN_ACCEPTANCE` for projection; without it the state remains pending. Timeout/silence cannot exit.

The coordinator may only project that exact decision through the HUMAN-approved acceptance operation declared in the WBS closure matrix and Section 9.1 transition protocol. The first prevalidated, guarded receipt-linked write may produce only unaccepted `ACCEPTANCE_VERIFYING`, binding the decision/action, current ledger, exact deterministic final candidate bytes/hash and all output/verifier/review-closure hashes; dependencies still treat it as unaccepted. An independent verifier checks the persisted pending record, live P16 authority and exact proposed final bytes/hash. `confirmed` produces a bound verification receipt but does not itself authorize a stale later write. Immediately at every final accept/reject write boundary—including a source-equal intent restart—the coordinator re-hashes the decision-bound output, verifier, `ReviewClosureReceipt`, HUMAN decision, complete owner-rooted delegation/revocation records and current ledger source/version, and revalidates P16 plus exact equality to the verified pending/candidate hashes. Only PASS permits the second pre-intended guarded transition to exactly `ACCEPTED` or `REJECTED_CHARGED`; persisted bytes are re-hashed and strict-validated. Drift, revocation or unavailable observation writes no final bytes and transitions only through a separately pre-intended unaccepted edge to `ACCEPTANCE_PENDING` for authority/decision drift or `ACCEPTANCE_VERIFICATION_PENDING` for evidence/verification drift. `refuted` enters `ACCEPTANCE_VERIFICATION_FAILED`; unavailable/inconclusive enters `ACCEPTANCE_VERIFICATION_PENDING`. Those states authorize no final projection; a new independent verification over identical inputs may return to `ACCEPTANCE_VERIFYING`, while changed bytes/authority require `ACCEPTANCE_PENDING` and a fresh HUMAN decision. No HUMAN/coordinator/reviewer waiver can replace confirmation. Exact reject preserves the attempt/evidence.

A persisted write/hash/validation mismatch enters `ACCEPTANCE_PROJECTION_REPAIR_REQUIRED`, not ACCEPTED/REJECTED. Preserve exact source, candidate and invalid persisted bytes/hashes/versions, validator output, original HUMAN semantic decision and its live P16 chain. A separate HUMAN repair-authority record binds those bytes, unchanged accept/reject action, same attempt/charge, exact target bytes/hash/state, one coordinator-owned version-guarded repair argv/effect, administrative-ledger remaining ceiling, verifier/reviewer and no-new-decision/no-new-attempt rule. `ACCEPTANCE_PROJECTION_REPAIRING` permits one prevalidated write from the bound invalid version; re-hash/strict validation, independent verification/review and HUMAN repair-byte acceptance then use the Section 9.1 protocol to reach only the failed edge's exact target: repair of the first edge returns to unaccepted `ACCEPTANCE_VERIFYING` and still requires independent confirmation; repair of the final edge may reach the original decision's `ACCEPTED` or `REJECTED_CHARGED` only with the already bound confirmed verification receipt. Failure, stale/revoked original decision, scope drift or ceiling breach enters `ACCEPTANCE_PROJECTION_REPAIR_BLOCKED`; a fresh HUMAN semantic decision returns to `ACCEPTANCE_PENDING`, while a fresh equally bound repair authorization may retry the same action. No repair authority may change the original accept/reject action.

## 6. Immutable AdmissionBundle

A later WBS must require one immutable `AdmissionBundle` per charged attempt. It is an evidence artifact, not a new runtime service. Every fresh P1–P13/P15/P16 canonical receipt and the raw observation bytes needed to recompute it are embedded inline in the read-only prepared bundle bytes and persisted only by the approved create-once bundle seal; a path/hash pointer is allowed only for a pre-existing immutable source whose bytes are also hash-pinned and available to the validator. Prepare performs reads and returns canonical bytes but writes nothing. Thus bundle sealing is the sole persistence effect for preparation evidence and cannot replay a mutable or unsealed receipt path. The later fresh P14/boundary observations and raw evidence are embedded in the charge-preimage/`ExecutionTransitionIntent` bytes persisted by that already-declared create-once effect.

```yaml
record_type: AdmissionBundle
contract_status: proposed-design-contract-not-yet-activated
contract_ref: <HUMAN-approved persisted schema path+sha256; absent means NOT_READY>
validator_ref: <approved deterministic validator path+sha256 and exact argv; absent means NOT_READY>
storage_ref: <HUMAN-approved content-addressed canonical bundle root and create-once policy>
seal_ref: <approved bundle-seal operation path+sha256 and exact argv/effect; absent means NOT_READY>
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
  invalidation_index_sha256: <canonical append-only index raw-byte sha256>
evidence_representation: <inline canonical receipt+raw observation bytes for every fresh P1-P13/P15/P16 item; external pointer only for pre-existing immutable hash-pinned bytes>
receipts:
  plan_format: <inline canonical bytes+raw evidence; optional immutable path+sha256>
  plan_semantics: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  execution_strict: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  dependency_acceptance: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  source_integrity: <inline canonical bytes+raw evidence; immutable path+sha256 for every pre-existing task input>
  design_basis: <v20 design path+sha256 plus immutable run-002 failure-model snapshot path+sha256>
  aip_asc_transition: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  command_capability: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  coordinator_quiescence: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  team_authority: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  goal_activation: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  execution_goal_state: <execution ledger hash/version + recorded run_state/pause-resume marker + runtime goal identity/state/sequence + equality result + observed_epoch>
  reviewer_availability: <pre-charge policy/template hashes + primary/fallback provider/model/family/role matrix + retry policy + call budget; no premature final-packet hash>
  budget_reserve: <inline canonical bytes+raw evidence; optional pre-existing immutable path+sha256>
  wbs_authority: <designated mission decision-owner ID/source + decision record ID/raw hash + HUMAN actor.kind/id + exact scope + bound WBS revision/hash/effects + revocation state + direct-owner equality or complete hash-pinned owner-to-actor delegation chain>
  bootstrap_authority: <ordered authority lineage: initial decision plus every recovery decision/receipt and final HUMAN maintenance-byte acceptance; each link has raw hash, designated HUMAN owner/actor/delegation, scope/effects, admin-ledger ceiling binding and revocation state; also bound bundle/invalidation/admin-ledger schemas, ledger ID/path, exact `run_aip.py start|resume|step` tool/argv/effect hashes and all other capability argv/effect hashes>
  migration_authority: <ordered authority lineage: initial migration decision plus every recovery decision/receipt and final HUMAN migrated-base acceptance; each link has raw hash, designated HUMAN owner/actor/delegation, pre/current/final ledger hashes/versions, exact migration/restore scope/effects, admin-ledger ceiling binding and revocation state>
  acceptance_authority: <designated mission decision-owner ID/source + per-task owner map + required actor.kind=human + complete owner-rooted delegation-chain decision IDs/raw hashes/scopes/revocation state; direct owner equality when no delegation; non-HUMAN or owner-unrooted delegate invalid>
  ledger_lineage: <accepted migration base hash/version + current source hash/version + ordered authorized predecessor/charge receipt hashes + append-only proof>
  invalidation_index: <canonical path + raw sha256 + item_count + last_sequence + owner + observed_epoch + freshness_rule>
prepared_epoch: <native state sequence/timestamp set>
freshness_rule: <explicit expiry/drift predicate>
charge_boundary_policy: coordinator version-guarded execution-ledger update authorized by exact HUMAN-approved WBS/effects
state: READY
```

The seal operation creates a separate immutable `AdmissionBundleSeal` sidecar containing the canonical bundle path, full raw-file SHA-256/size, validator/contract hashes and result, create-once operation hash/argv, actor, timestamp/sequence and recovery status. The full-file hash is intentionally outside the hashed bundle bytes; no self-referential hash field is allowed. `READY`, invalidation records and the charge boundary identify the bundle by the seal sidecar's full-file SHA-256 and bind the sidecar hash as well.

Every in-bundle receipt records exact argv/tool identity where applicable, exit/result, canonical paths, raw-byte hashes, captured native identities, observation epoch/sequence and an explicit freshness rule. Missing, stale, replayed, ambiguous or degraded bundle or seal material makes the bundle `NOT_READY`; silence is failure.

### 6.1 Contract and operation ownership bootstrap

`AdmissionBundle` above is a **proposed design contract**, not an existing authoritative schema. Before any successor WBS is built, a separately HUMAN-authorized control-plane stabilization action must persist and approve: (a) the exact schema bytes and SHA-256; (b) a deterministic validator and its exact `python3 <approved-validator-path> validate <bundle-path>` argv; and (c) the coordinator-owned read-only prepare operation and exact `python3 <approved-prepare-path> prepare ...` argv, which computes canonical bytes without changing mission/control state; (d) the coordinator-owned create-once bundle-seal operation, content-addressed storage root, exact `python3 <approved-bundle-path> seal ...` argv, allowed-effect contract, post-write hash/schema validation and crash recovery; (e) the coordinator-owned uncharged invalidation append operation, canonical index path, exact `python3 <approved-invalidation-path> append ...` argv, allowed-effect contract, deterministic validator and recovery behavior; (f) the Section 6.3 exact AdministrativeResourceLedger contract/path/validator/coordinator-only guarded append and cumulative ceiling; (g) either exact existing `dsh-wbs-execution/1` JSON-pointer mappings plus a strict-valid charge fixture, or a HUMAN-authorized versioned execution-contract extension/validator/migration; and (h) the coordinator-owned create-once charge-preimage seal plus version-guarded post-charge ledger repair, acceptance-projection repair and interrupted-disposition transition operations, exact argv/effects, immutable transition-intent/completion/guarded-write-receipt/repair schemas, review-closure receipt schema/validator, create-once/idempotent-finalize operations and P3 lineage/recovery rules. Until those real paths/hashes/commands exist and pass, admission is `NOT_READY`; v20 does not invent them or claim P1/P2 mechanical validation.

After bootstrap, the coordinator owns read-only bundle computation through the approved prepare command and exact durable sealing through the separate create-once seal command. `READY` is legal only after the complete canonical bundle bytes and validator receipt are durably stored at a path derived from `bundle_sha256`, re-read equal to the computed bytes, and independently retrievable; collision, overwrite request, missing bytes, hash/schema mismatch or seal crash leaves `NOT_READY`. A crash after seal but before charge leaves an uncharged retrievable bundle that must pass P14 or expire; a crash after charge can reconstruct proof from the charge-bound bundle hash and canonical bytes. The coordinator also owns the first durable charge/boundary mutation through one version-guarded `execution.json` update using the runtime's native guarded file write/edit operation, bounded by the HUMAN-approved WBS hash and declared write effect. A stale-version conflict, failed predicate, unavailable guard or missing authority aborts with no charge and no attempt allocation. The operation must re-observe live predicates and bind the immutable bundle full-file hash, `AdmissionBundleSeal` sidecar hash, boundary receipt and allocated attempt ID in the one ledger update. This is attributable procedural ownership, not a non-bypassable native DSH hook.

### 6.2 Immutable invalidation representation

A sealed bundle never changes. At seal time it pins the invalidation index's canonical path, raw-byte SHA-256, item count, last sequence, owner identity, observation epoch and the same freshness rule used by the bundle. An unavailable index or any mismatch makes the candidate `NOT_READY`, never `READY`.

When drift, withdrawal or failed re-observation is detected, the coordinator invokes only the HUMAN-approved invalidation append argv/effect and appends an immutable uncharged `AdmissionInvalidation` evidence record containing `bundle_sha256`, reason code, observed prior/current values or unavailable predicate, actor identity and observation sequence. The append receipt records operation path/hash/argv, canonical index before/after hashes and sequences, actor, zero charge/attempt effect and validation result; failure leaves `NOT_READY` with no mission-ledger write. The charge-boundary check re-reads the same canonical index, requires an append-only extension of the sealed prefix, rejects truncation/replacement/path/owner/sequence mismatch, and blocks if any extension names the bundle hash. Because an invalidation can still race the ledger write, that window remains part of the disclosed TOCTOU residual risk. The sealed `READY` bundle proves only a past observation and is never current-validity evidence by itself.

### 6.3 Bootstrap governance and accounting

Bootstrap implementation is not free or implicit work. It enters `BOOTSTRAP_MAINTENANCE` only through a separately HUMAN-authorized administrative task under its own Working AIP and Task Workspace, outside the frozen mission-attempt ledger until a valid migrated ledger exists. Before work, the HUMAN decision binds the objective, exact allowed write paths/effects, prohibited product/network/install/activation effects, one canonical **uncharged administrative resource ledger**, its resource/model-call ceiling, stop conditions, verifier, independent reviewer and HUMAN acceptance owner. Mission-attempt charging is prohibited because P15 and a valid mission ledger do not yet exist; there is no alternative accounting mode. Bootstrap entry and exit receipts re-hash the mission ledger and mechanically attest unchanged attempt set, unchanged `attempts_charged`, zero mission-attempt allocation/consumption and every administrative call/effect charged only to the HUMAN-bound administrative ledger. Any mismatch enters `BOOTSTRAP_BLOCKED`.

Before `BOOTSTRAP_MAINTENANCE`, `MIGRATION_MAINTENANCE` or any post-charge repair/review/transition-recovery state starts, the HUMAN must supply/accept as an outer trust anchor exact immutable `AdministrativeResourceLedgerContract` bytes/hash, canonical path/ledger ID, one **cumulative** ceiling with explicit state-specific allocations for bootstrap, migration, ordinary uncharged pre-charge admission/proof/evidence work (including prepare, capability/reviewer probes, bundle/intent sealing, invalidation and NOT_APPLIED completion), post-charge ledger repair, acceptance-projection repair, review recovery and transition-intent finalization/recovery, deterministic validator, and coordinator-only version-guarded append operation. A post-charge state without its fresh HUMAN-bound allocation and sufficient remaining common ceiling remains blocked; it never consumes or creates a mission attempt. The same ledger ID/path/contract hash and cumulative ceiling must appear in both maintenance decisions, P15 and WBS-build entry evidence; a second ledger, divergent ceiling or unreconciled allocation is `BOOTSTRAP_BLOCKED`/`MIGRATION_BLOCKED` and later `NOT_READY`. Minimum contract fields are: ledger/contract/mission IDs; sequence and previous-entry hash; attributable decision/invocation/actor IDs; operation/tool/model identity; resource units; exact allowed effect plus before/after artifact hashes; state; result; cumulative usage; remaining ceiling; and entry hash. The validator recomputes canonical bytes, sequence/hash continuity, allowed-effect scope, cumulative arithmetic and ceiling. Reconciliation enumerates every authorized non-metering model/tool invocation and Workspace file effect against exactly one ledger entry; missing, duplicate or unattributable activity fails closed. The ledger append primitive itself is the sole narrow outer-meter exemption: the HUMAN-bound contract pins its exact implementation/hash/argv/effect, an independently verified worst-case `append_overhead_reserve`, and a maximum append-invocation count. One atomic invocation may append exactly one activity record whose resource amount includes that fixed reserve; its operation receipt binds the activity invocation, before/after ledger hashes and actual success/failure without recursively generating another ledger entry. Every attempted append consumes one reserved overhead unit in reconciliation whether it succeeds or fails; failed append enters the blocked state, and operation receipts plus ledger entries must account for all invocations within the bound. The contract, initial zero-use record, append capability and passing boundary fixtures must already validate before maintenance; they cannot be self-created or retroactively backfilled inside the state.

Before any ordinary admission-cycle call/effect, effect 5.1(f) appends one immutable `AdmissionResourceReservation` as the first operation. It binds admission-cycle/mission/WBS/task/source IDs, exact permitted effect classes/argv hashes, deterministic usage-entry IDs, worst-case units covering prepare/probes/review discovery, bundle/invalidation/intent/index OPEN/NOT_APPLIED or APPLIED completion/index CLOSE, guarded writer/receipt, every required accounting append/overhead and bounded recovery, maximum append count, expiry, prior ledger hash/sequence, and reserved units. The append deducts the full reservation from globally available cumulative ceiling under its single version guard; there is no refund, so later ledger growth cannot exhaust that already-deducted envelope. Each non-charge operation appends its actual-usage entry immediately after the operation; append overhead is included as Section 6.3 already requires. The boundary aggregate binds immutable reservation ID/bytes/hash—not the mutable current ledger hash. The final guarded writer validates the current ledger is an append-only extension of the reservation prefix, every intervening entry has that reservation ID and an allowed effect, actual plus remaining bounded recovery units do not exceed reserved units, maximum append count is not exceeded, no competing/duplicate reservation exists for the cycle, and binds that pre-write reconciliation plus its deterministic pending usage-entry IDs in `GuardedWriteReceipt`.

The charge edge then follows a stricter crash-safe order. After `execution.json` is hash-equal and strict-valid, state is `CHARGED_ACCOUNTING_PENDING`; no APPLIED completion, index CLOSE, dispatch, dependency use or further ordinary transition is allowed. The coordinator appends and validates the deterministic guarded-writer/receipt usage entry and append receipt. Before each later deterministic file effect, it pre-appends a fixed contract-priced attempt entry: first for APPLIED-completion persistence, then—after that completion validates—for index CLOSE persistence. A failed attempted effect remains legitimately charged; an idempotent retry must pre-append its own distinct bounded retry entry and may only reproduce the exact pre-bound bytes. APPLIED completion is forbidden until the writer entry validates; dispatch is forbidden until the completion-attempt entry, exact APPLIED completion, index-close-attempt entry, exact CLOSE, and every append receipt all validate, the current ledger reconciles within the reservation, and ordinary P3 proves zero open intents. A crash/failure stays `CHARGED_ACCOUNTING_PENDING` or `COMPLETION_INDEX_CLOSE_PENDING` as applicable, preserves the mission attempt/charge, and permits only exact HUMAN-bounded recovery using remaining reserved recovery units. Expected accounting appends after the boundary receipt do not invalidate it, but any unrelated entry, gap, duplicate ID, failure or excess enters `ADMISSION_ACCOUNTING_BLOCKED`/`CHARGED_ACCOUNTING_BLOCKED`; exhaustion requires a fresh HUMAN ceiling/recovery decision and never permits a new admission cycle to reuse the charged attempt.

Every bootstrap model/tool call, file effect, retry and review is recorded in that Workspace against the single cumulative ceiling. Any ceiling exhaustion, scope drift or missing accounting stops the task without making P15 pass. Only exact HUMAN-accepted schema/tool/operation bytes and hashes, with AIP/Workspace evidence, verification and independent review, may populate `bootstrap_authority`; bootstrap work cannot be hidden inside a successor WBS or silently consume its contingency reserve. Verified/reviewed exact bytes plus an attributable HUMAN acceptance return their hashes to `FROZEN`; failure, ceiling exhaustion or scope drift enters HUMAN-owned `BOOTSTRAP_BLOCKED`. A fresh HUMAN recovery decision must bind failure receipts, exact current/restore hashes, allowed effects and remaining/replaced cumulative ceiling before returning to `BOOTSTRAP_MAINTENANCE`; that decision, its receipt and final HUMAN byte acceptance append to the ordered `bootstrap_authority` lineage. Alternatively exact no-effect/restore proof plus HUMAN closure returns to `FROZEN` and is also appended. Otherwise it remains blocked and no improvised work is allowed. This design/review task specifies the requirement but does not authorize or implement the bootstrap.

## 7. Admission invariants and evidence

| Invariant | Mandatory evidence before charge | Failure disposition |
|---|---|---|
| P1 Plan identity | Official WBS validate/order/hash receipt; exact plan bytes unchanged | `NOT_READY` |
| P2 Plan semantic closure | Closed matrix mapping each deliverable/output to declared write path, owning command or permitted file operation, verifier, reviewer and acceptance owner | `NOT_READY`; revise plan |
| P3 Ledger strict validity/lineage | Official strict execution/progress validator PASS over exact `execution.json`; bundle lineage receipt proves the current source is either the exact HUMAN-accepted migrated base before first charge or the complete gap-free Section 9.1 `ExecutionTransitionIntent`/`ExecutionTransitionCompletion` pair hash/sequence chain covering every charge and ordinary status/outcome/review/acceptance write from that base, reconciles the canonical intent-root scan one-to-one with the append-only `TransitionIntentIndex`, requires zero open intents for ordinary readiness/dispatch/dependency use, validates every APPLIED edge's pre-bound administrative usage entries/append receipts, and allows only the Section 5.2 hash-complete `POST_CHARGE_REPAIR` exceptional link preserving the same attempt/charge | `NOT_READY`; divergence, missing predecessor/receipt, unlinked mutation or invalid attempt/charge change requires separate HUMAN-authorized repair/migration |
| P4 Dependency acceptance | Every hard dependency has valid verification, a validator-backed policy-complete `ReviewClosureReceipt` PASS, and acceptance refs whose output hashes still match | `NOT_READY` |
| P5 Source/design-basis integrity | All pinned immutable task-input hashes match current bytes; stabilization/WBS-build admission also re-hashes the current design and run-002 failure-model snapshot `434f1613…d8b86` through the declared read-only hashing command | `NOT_READY`; invalidate carry-forward |
| P6 AIP/ASC closure | AIP lint PASS; declared `run_aip` transition produces fresh ASC; pointer/AIP/Workspace/task all agree | `NOT_READY` |
| P7 Command authorization/capability | Exact argv appears in the pinned root/task allowed-command union whose hash is recorded; argv/cwd paths resolve; required effect backend is observed available; prohibited effects remain denied | `NOT_READY` |
| P8 Coordinator identity/quiescence snapshot | At the receipt epoch, native Team/goal listings show one Team Lead coordinator, no delegated-coordinator topology, every enumerated mission-capable writer stopped/settled, and `active_work` equal to that snapshot; this is observation plus a procedural role restriction, not proof that a delegated writer lacks native charge capability | `NOT_READY` on identity/topology mismatch, unavailable enumeration or unsettled writer; HUMAN reassigns/ends the conflict before re-prepare; disclose delegated-writer bypass residual risk |
| P9 Team authority | Native Team plan revision is current and HUMAN-approved when Team execution is required; required members available | `NOT_READY` |
| P10 Goal/execution-state synchronization | Goal identity/objective/hash agree; at one observation epoch the ledger's recorded run state and pause/resume marker equal the runtime goal state/activation, and runtime reports active/armed when autonomous continuation is promised | `NOT_READY` on any ledger↔goal mismatch or unavailable marker; no promise of continuation |
| P11 Reviewer availability/fallback | Pre-charge live discovery records provider, model, route family, eligible role, immutable review policy/template identity and typed retry policy for each primary/fallback; final packet identity is deferred until output/verifier bytes exist and is then required before review dispatch; a pinned substitution matrix proves every allowed single-primary replacement still supplies the mandatory lane and two distinct internal model families; no capacity reservation is claimed without a real provider primitive | `NOT_READY` when a primary/fallback is unavailable or any allowed substitution loses lane coverage/diversity; otherwise record double-booking/provider-loss residual risk |
| P12 Budget safety | Charge ceiling covers selected attempt plus all mandatory downstream minima and mission-specific contingency reserve | `NOT_READY`; HUMAN decides ceiling/reallocation |
| P13 Authority | Bundle `wbs_authority` receipt names the designated mission decision-owner identity/source plus exact HUMAN decision record ID/raw hash, actor, non-revoked scope, current WBS revision/hash and allowed effects; actor ID must equal that owner or resolve through a complete hash-pinned non-revoked HUMAN delegation chain from that owner with exact mission/WBS/effect scope; boundary re-verification re-hashes the record/chain and checks identity/scope/revocation | `NOT_READY` on absence, ambiguity, revocation or drift; no review/report is approval |
| P14 Bundle freshness/invalidation | All current hashes/native states, including atomic P13/P15/P16 and migration-authority decision receipts, ledger↔goal equality, ledger lineage and revocation/scope state, still equal the sealed bundle immediately before commit **except** the invalidation index, which uses its sealed freshness rule: current bytes preserve the sealed raw-byte prefix/path/owner; count and last sequence advance only by valid contiguous appends; truncation/replacement/path/owner/sequence mismatch expires; any appended item naming the bundle hash blocks charge | `EXPIRED`; abort with no mission write or attempt consumption; append uncharged invalidation evidence; re-prepare |
| P15 Admission mechanism bootstrap/authority | Bundle `bootstrap_authority` receipt names exact HUMAN decision record ID/raw hash, actor, non-revoked scope and bound bundle/invalidation and AdministrativeResourceLedger contract hashes, their validator/prepare/bundle-seal/invalidation/admin-ledger-reserve+append/charge-preimage-seal/transition-intent-index+P3_IN_FLIGHT/guarded-writer/guarded-write-receipt/completion/restart/review-closure-validator argv hashes plus exact `run_aip.py start|resume|step` tool/argv hashes and bounded pointer/ASC/Workspace-control effect, guarded-write, post-charge-ledger-repair, acceptance-projection-repair and interrupted-disposition effects, exact execution-contract representation decision plus passing fixture/validator hashes, and migration boundary; a separately authorized bootstrap AIP/Workspace proves the single canonical uncharged administrative resource ledger ID/path/contract and cumulative ceiling, zero mission-attempt/charge effect, allowed effects, verification/review and HUMAN acceptance; every capability exists and passes; P14 re-hashes record/artifacts and checks scope/revocation, revalidates every link of the complete `bootstrap_authority` lineage, and on the first post-migration charge every link of the complete `migration_authority` lineage | `NOT_READY`; absence, ambiguity, revocation, drift or capability failure aborts uncharged; complete/re-authorize bootstrap before WBS admission |
| P16 Acceptance authority | Bundle `acceptance_authority` receipt maps every task acceptance owner to the HUMAN decision owner or to an alternate with `actor.kind = human` connected to that designated owner through a complete hash-pinned non-revoked HUMAN delegation chain whose every link binds exact task/scope; any non-HUMAN or owner-unrooted alternate is invalid; P14 re-verifies every chain link before charge; at the later Section 5.4 acceptance boundary the current decision additionally binds exact task/attempt/output/verifier/review hashes and accept/reject action | `NOT_READY` before charge or `ACCEPTANCE_PENDING` afterward; a task declaration, reviewer report or coordinator cannot originate/transfer acceptance authority |

### 7.1 Mission-specific contingency rule

The next WBS must reserve at least:

- one attempt for future plan-selection/reconciliation after a material reviewed correction; and
- one attempt for a runtime/tooling recovery that cannot reuse an implementation attempt.

The design recommends **two attempts** as the mission-specific contingency reserve. Only the HUMAN decision owner may select or change the operative amount; council output is advisory and cannot set it. The reserve cannot be silently borrowed by product tasks. Because the currently selected **WBS revision 32** (not this design's revision) has no slack, the later workflow is ordered: after reviewed design closure and an explicit HUMAN request to begin WBS work, an uncharged, inactive WBS candidate may be drafted and hashed; the HUMAN then records ceiling/reallocation, contingency and approval decisions bound to that exact candidate revision/SHA-256; only afterward may it be selected or admitted. Drafting is not selection, admission or execution. This current design task still does not authorize any WBS draft.

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

The current `execution.json` remains frozen until a separate Working AIP and one canonical Task Workspace exist and an exact HUMAN administrative decision enters `MIGRATION_MAINTENANCE`. The AIP is stable macro-control; every migration runtime fact, mapping, call/effect, candidate, verifier/reviewer result and decision reference lives in that Workspace. Reporting or design work must not normalize the ledger in place, and ordinary admission cannot start while migration/recovery is active. Because P3 deliberately blocks charging any WBS attempt against the known strict-invalid ledger, this one-time migration is **uncharged control-plane maintenance performed before successor-WBS build**, not a product or WBS execution attempt and not acceptance evidence.

The HUMAN authorization must bind the Working AIP ID/hash, canonical Workspace path, current step/ASC, exact pre-migration ledger SHA-256/version, target contract hash, exact migration/restore argv or permitted version-guarded file operation, allowed write path, no-product-effect boundary, the exact Section 6.3 canonical administrative-ledger ID/path/contract hash and its single cumulative ceiling/allocation, stop conditions, verifier, reviewer and HUMAN acceptance owner; any source hash/version change before write invalidates the authorization and requires a new HUMAN decision. The migration operation and receipt must assert and mechanically verify: no attempt ID allocated or consumed, `attempts_charged` unchanged, attempt set unchanged, no AdmissionBundle sealed/consumed, no task/product mutation, and no acceptance transition. This authority cannot be reused for a charge write. For the first post-migration charge, P3/P14/P15 require the pre-charge source to equal the exact HUMAN-accepted migrated base bytes/hash/version and require the bundle `migration_authority` receipt to re-hash an ordered lineage of the initial decision, every recovery decision/receipt and final HUMAN base acceptance; every link must prove designated-owner/delegation identity, exact before/current/final ledger bindings, scope/effects, common administrative-ledger ceiling and non-revocation. For every later charge, P3 requires the complete ordered Section 9.1 `ExecutionTransitionIntent`/`ExecutionTransitionCompletion` pair chain from that base through each charge and ordinary status/outcome/review/acceptance candidate/persisted hash; only linked authorized state edges are accepted, while any missing/unlinked change or improper attempt/count mutation is `NOT_READY`. The coordinator is the migration-operation owner, a separate verifier and reviewer validate the candidate, and only the HUMAN accepts/selects migrated bytes. The state exits only to `FROZEN(new base)` after exact HUMAN acceptance of the candidate hash plus governed scoped AIP/Workspace lint and closure evidence, or through `MIGRATION_RECOVERY` to `FROZEN` after exact backup-equality proof; restore mismatch enters `MIGRATION_BLOCKED`. Every administrative resource/tool/model call and retry is recorded against the same Section 6.3 cumulative ledger/ceiling, never against a mission attempt.

A canonical append-only `TransitionIntentIndex` serializes the protocol without claiming cross-file atomicity. Before intent creation, ordinary P3 requires a closed chain and zero open intents; the boundary receipt binds the prior index hash/sequence, deterministic planned intent ID/path/sequence and source/version. Ordered OPEN is: (1) create-once persist and validate the intent record, then (2) version-guard append its exact OPEN entry. A crash after (1) is `INTENT_INDEX_OPEN_PENDING`: P3 scans the canonical intent root as well as the index, blocks all charge/dispatch/dependency use, and permits only the exact idempotent index-open recovery or, while ledger bytes still equal source, the pre-bound NOT_APPLIED close path; index OPEN without its valid intent is `TRANSITION_RECOVERY_BLOCKED`. A valid OPEN enters `TRANSITION_IN_FLIGHT`. Only a transaction-local `P3_IN_FLIGHT` validator—and only for the exact P15-bound guarded writer or exact restart/finalize command—may accept it; it requires the index to equal the prior prefix plus exactly one unexpired source/version/candidate/reservation/boundary-bound intent whose previous-completion hash is the closed-chain head. It cannot report READY, authorize another prepare/intent/charge, satisfy a dependency or be consumed by any other writer.

Ordered CLOSE is: (3) create-once persist and validate the exact APPLIED/NOT_APPLIED completion, then (4) version-guard append the matching CLOSE entry. A crash after (3) is `COMPLETION_INDEX_CLOSE_PENDING`: P3 remains non-ordinary/in-flight and only the exact idempotent close recovery may append the already-bound CLOSE; index CLOSE without its valid matching completion, or any record/index disagreement, is `TRANSITION_RECOVERY_BLOCKED`. The record scan and index must reconcile one-to-one by path/hash/sequence at every validator entry. Only a validated CLOSE yields zero open intents and returns to ordinary P3. Multiple, stale, wrong-source, skipped-sequence or unmatched open intents block. These index writes and receipts are explicit parts of Section 5.1(d)/(e) and P15; no step infers or repairs them silently. Restart follows the deterministic source/candidate/divergent branches below and never ignores an intent record or OPEN entry.

Every permitted post-migration `execution.json` mutation—charge/allocation, active/dispatched, interrupted/failed, verification outcome, review pending/result, revision-required, acceptance-pending/verifying/reject/accept, and repair—uses one uniform two-record protocol. **Before any ledger write**, the coordinator create-once persists an immutable content-addressed `ExecutionTransitionIntent` that pins source bytes/hash/version, previous completion hash/sequence, deterministic intent/receipt IDs and idempotency key, exact state edge, attempt ID/count invariants, actor/authority, selected execution-contract mapping, argv/effect and strict-valid candidate bytes/hash; only a charge intent may increment the attempt set/count. The charge-preimage seal is the charge edge's intent under this same schema. The ledger then persists through one version-guarded write from the pinned source, re-hashes equal and strict-validates. For **every** edge, only the exact P15-bound guarded writer may produce one immutable hash-bound `GuardedWriteReceipt`; every `APPLIED` create-once `ExecutionTransitionCompletion` must bind and validate that receipt plus the intent, exact writer/tool/argv, edge-specific boundary/authority check set and result, source/candidate/persisted hashes and strict-validator results. Missing, mismatched or non-P15 writer receipt forbids APPLIED and enters `TRANSITION_RECOVERY_BLOCKED`. The next intent links this completion hash/sequence. The intent pre-binds deterministic administrative usage-entry IDs for guarded writer/receipt, completion attempt and index-close attempt. On a charge edge, the Section 6.3 ordering makes the writer entry a prerequisite to APPLIED completion and makes all three entries plus validated CLOSE and zero-open ordinary P3 prerequisites to dispatch/dependency use; every recovery preserves the charge. The canonical candidate is never dispatchable, dependency-satisfying or the source of another ordinary transition merely because its APPLIED completion exists.

The only action after an incomplete intent is the exact idempotent restart/finalize command named by that intent. If ledger bytes still equal the pinned source, a non-charge edge may perform its edge-specific fresh checks and then either perform the one guarded write or create-once close `NOT_APPLIED`. A **charge-edge** source-equal restart never writes the old candidate: it create-once closes the old intent `NOT_APPLIED`, appends an invalidation when authorized, and runs fresh Section 5.2 preparation/boundary construction to create a new bundle as needed, new boundary receipt, new candidate hash and new charge intent before any guarded write. Reusing or modifying the old intent/candidate is invalid; unavailable observation or any drift writes no ledger bytes and requires re-prepare; if bytes equal the candidate, APPLIED finalization is permitted only when a pre-existing immutable `GuardedWriteReceipt` from the exact P15-bound writer validates and binds the intent ID, writer/tool/argv hash, edge-specific boundary checks and authority/revocation state, source version/hash, candidate hash, write result and persisted hash; the coordinator re-runs strict validation, validates or appends the exact pre-bound writer usage entry/receipt, and pre-appends the exact completion-attempt usage entry before create-once finalizing the identical APPLIED completion; it then pre-appends the index-close-attempt entry and idempotently closes the index before ordinary P3 or dispatch. Candidate equality without that receipt—including crash before receipt persistence—or any receipt mismatch enters `TRANSITION_RECOVERY_BLOCKED` and must not create APPLIED; if the completion write itself failed, the same command retries the same content-addressed completion bytes. If ledger bytes equal neither source nor candidate, validation differs, or an existing record at either path has different bytes, enter `TRANSITION_RECOVERY_BLOCKED`; preserve attempt/charge/decision semantics and require a fresh HUMAN recovery/migration decision—never synthesize a receipt. APPLIED and NOT_APPLIED completions form one gap-free hash/sequence chain from the HUMAN-accepted migrated base; every non-charge edge preserves attempt set/count, and acceptance edges bind the P16 decision plus verification receipt. P3 accepts only this complete intent/completion chain with a validated exact guarded-writer receipt on every APPLIED link, plus explicitly bound recovery links; missing/duplicate/out-of-order records, an incomplete intent outside the exact transaction-local `P3_IN_FLIGHT` exception, unlinked ledger mutation or unauthorized count change is `NOT_READY`.

`MIGRATION_BLOCKED` is owned by the HUMAN decision owner and is frozen against all ledger/product writes. Its only executable exit is a fresh attributable HUMAN recovery decision binding the failed migration/restore receipts, immutable backup, candidate/current hashes, same AIP/Workspace, exact permitted recovery/restore effects, same administrative ledger/remaining ceiling, verifier, reviewer and HUMAN acceptance owner; the coordinator then returns to `MIGRATION_RECOVERY`; the decision/receipt and eventual HUMAN recovery result append to the ordered `migration_authority` lineage. Only independent verification plus exact backup equality, or a newly verified/reviewed candidate explicitly accepted by the HUMAN, may return to `FROZEN`. A HUMAN abandon decision records terminal frozen status and authorizes no mutation. Missing/stale/revoked authority, ceiling breach or failed evidence remains `MIGRATION_BLOCKED`; improvised repair is prohibited.

### 9.2 Migration protocol

0. Start/resume the separately approved Working AIP, verify one canonical Workspace/current-step/ASC binding, and stop on lint/control mismatch.
1. Copy exact pre-migration bytes to a new immutable evidence directory and record SHA-256.
2. Consume the exact HUMAN-approved P15 execution-representation decision and pin its single target: either proven existing `dsh-wbs-execution/1` JSON pointers plus strict-valid fixture, or the exact versioned extension contract/validator/migration bytes. No transformation starts before this choice; no double migration or invented v1 fields.
3. Inventory every incompatible field and classify it as lossless-known, conflicting or unrelated damage.
4. Transform only lossless-known fields using a reviewed deterministic mapping.
5. On duplicate/conflicting paths, missing provenance or ambiguous acceptance, stop; do not choose a value.
6. Preserve historical attempts, charges, output hashes, reviews and HUMAN decisions byte-for-byte or by reversible reference.
7. Write a small current projection separately from immutable historical evidence when the contract permits it; otherwise keep the single-file contract and record the constraint.
8. Run strict validator and execution-backed progress rendering on the exact candidate bytes.
9. Independently review the before/after mapping and no-loss proof.
10. Run scoped governed lint over the migration AIP/Workspace, preserve actual results, then HUMAN accepts the exact migration bytes and closure evidence before return to FROZEN or selection of a product WBS.
11. If strict validation/report rendering or independent review fails, the migration owner stops, retains exact original/candidate bytes and hashes, and performs a version-guarded restore through the declared restore operation. The restore receipt re-reads the persisted path and proves raw-byte hash/size/version equality to the immutable backup plus equality of attempt IDs, charge count and acceptance references. The known source may remain strict-invalid; that expected validator result is recorded separately and is not restore proof. Any restore mismatch freezes the ledger and escalates to the HUMAN; only exact equality permits no-selection return to step 3 with a new candidate identity.

### 9.3 Migration acceptance

Migration passes only when:

- original bytes and hash remain available;
- every field has a deterministic before→after trace;
- charges and attempt identities are identical;
- accepted/interrupted/failed distinctions are unchanged;
- strict validation and execution-backed report both pass;
- no task becomes accepted or ready solely because of migration.

## 10. Generated and mutable control-artifact ownership policy

- AIP remains stable macro-control; runtime facts remain in Workspace.
- Every generated or mutable mission-control artifact has exactly one declared owner and write mechanism in the approved closure matrix: AIP pointer/ASC → exact `run_aip.py start|resume|step` argv; execution ledger/current projection → coordinator through the declared migration operation or the Section 9.1 uniform prevalidated, version-guarded `ExecutionTransitionIntent`/`ExecutionTransitionCompletion` pair protocol for every charge/status/outcome/review/acceptance edge; progress/report rendering → the official read-only renderer; AdmissionBundle computation → coordinator through the read-only prepare command; durable AdmissionBundle bytes → coordinator through the separate create-once content-addressed seal command; AdmissionInvalidation → coordinator through the bootstrap-pinned canonical index and exact uncharged append argv/effect (the invalidation-specific Section 5.1 exception); charge/boundary record → coordinator through the single version-guarded `execution.json` write bounded by HUMAN-approved WBS/effects; acceptance decision → exact decision-owner HUMAN or currently delegated acceptor whose actor.kind is HUMAN; non-HUMAN delegates prohibited; acceptance projection → coordinator through the closure-matrix-declared guarded operation/edit after candidate strict validation, with independent verification.
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

1. Bind the immutable review policy/rubric and packet-template identity, required lanes, independence/model-family rules, HUMAN gate, evidence-path convention, typed retry policy and worst-case call budget. Do **not** require a final packet hash before output/verifier bytes exist.
2. Inspect live routes and record provider, model, route family and eligible replacement role for every primary/fallback; record availability as a snapshot, not a provider-capacity reservation.
3. Persist reviewer restrictions and a substitution matrix proving every allowed single-primary replacement preserves lane coverage, separate invocation identity and two-family internal diversity; otherwise admission is `NOT_READY`.

After implementation output and verifier evidence exist, but before review dispatch:

4. Construct the final immutable packet/manifest from exact output, verifier and policy/template bytes; persist and hash-pin those final bytes, re-check route/substitution eligibility, and bind their hashes to the charged attempt's review evidence.
5. A provider/transport/schema failure before valid verdict permits one typed retry or eligible fallback on **byte-identical final packet bytes** without a new implementation attempt. If no eligible route remains, enter `REVIEW_PENDING`; never substitute an unbound placeholder packet.
6. A valid adverse verdict is never retried to seek PASS; it requires disposition/revision.
7. Reviewer output remains advisory until the attributable HUMAN acceptance owner acts.
8. The coordinator may record/project an exact HUMAN decision but can never originate required acceptance. Any alternate acceptor must have actor.kind HUMAN and a complete hash-pinned, non-revoked, exact-scope delegation chain from the designated mission decision owner before admission; a task-declared rule cannot transfer that authority.

A review is complete only when a deterministic validator emits an immutable `ReviewClosureReceipt` PASS bound to the exact final review packet/hash, artifact manifest, HUMAN-approved review-policy bytes/hash, expected and actual lane/invocation/result hashes, schema-validation results, required distinct route families, typed-retry usage/dispositions, outside-view advisory separation, adjudication trigger/record or explicit not-triggered proof, separate Chairman identity/nonparticipation/result hash, final verdict and remaining budget. The validator proves every policy-required lane and gate is complete; one schema-valid lane or an unclosed Chairman response is never sufficient. Only `pass`/`pass_with_notes` receipt PASS may transition to `AWAITING_HUMAN_ACCEPTANCE`; `needs_revision` transitions to `REVISION_REQUIRED_CHARGED`, and blocked/insufficient/unavailable closure stays unaccepted in its declared state.

`REVIEW_PENDING` is a charged, unaccepted state owned procedurally by the coordinator. The exact final packet/hash, attempt/charge, output/verifier hashes, used retry count, eligible route matrix and remaining review-call budget are immutable. The coordinator may perform only the already authorized bounded re-probe and single typed retry/fallback; a freshly eligible bound route returns to `REVIEWING` on the identical packet. When no bound route/budget remains, the coordinator stops and escalates to the HUMAN. A fresh HUMAN decision may add exact route roles/families and review-only call budget without changing packet/output/attempt, after which independent route validation returns to `REVIEWING`; or may declare terminal `REVIEW_UNAVAILABLE_CHARGED`, which preserves the charge, leaves the task unaccepted and blocks dependents. HUMAN waiver cannot substitute for a mandatory review or produce acceptance. Every review-state ledger write follows the complete Section 9.1 transition-lineage rule.

For high-risk design/governance reviews, use two independent internal lanes from distinct model families, a sanitized outside-view lane, conditional adjudication and a separate Chairman. Reserve worst-case **call budget** before dispatch; do not claim provider capacity is held unless a named provider primitive proves it. Record route loss and double-booking as residual risks.

## 13. Goal, Team and ownership synchronization

Admission requires a single snapshot proving:

```text
execution.coordinator == native Team Lead/coordinator
execution.active_work == native active workers/jobs for the mission
execution.run_state/pause-resume marker == runtime goal state/activation at the same observation epoch
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
| Migration restore mismatch / `MIGRATION_BLOCKED` | before | HUMAN-owned terminal freeze; only a fresh hash/scope/ceiling-bound HUMAN recovery decision may return the coordinator to `MIGRATION_RECOVERY`; exact restore proof or HUMAN-accepted reviewed candidate required for `FROZEN` |
| Bootstrap failure / `BOOTSTRAP_BLOCKED` | before | HUMAN-owned freeze; fresh bounded HUMAN recovery authorization returns to maintenance, or exact no-effect/restore proof plus HUMAN close returns to `FROZEN`; otherwise remain blocked |
| Source/dependency hash drifts | before | expire bundle; invalidate affected acceptance |
| AIP/ASC transition missing | before | revise WBS to declare owning command |
| Sandbox/effect unavailable | before | `NOT_READY`; do not dispatch through workaround |
| Reviewer unavailable | before | use a previously discovered fallback after a fresh probe, or remain `NOT_READY`; no capacity reservation is implied |
| Goal/Team authority or coordinator/native-Lead mismatch, including delegated coordinator topology | before | uncharged abort; remain frozen; HUMAN/runtime ends, reassigns or explicitly restores one native Team Lead coordinator, then re-prepare |
| State changes after bundle sealed or at charge-boundary re-observation | before | `EXPIRED`; rebuild bundle without charge |
| Crash after charge but before dispatch / `INTERRUPTED_CHARGED` | after | coordinator waits for a fresh HUMAN same-attempt disposition; after bounded revalidation, named `interrupted_to_dispatched` resumes within exact remaining effects/resources or `interrupted_to_failed` closes while preserving charge/evidence; missing/invalid authority remains interrupted, never recharges |
| Persisted charge bytes fail equality/strict validation | after | enter `POST_CHARGE_REPAIR_REQUIRED`; use only fresh HUMAN-bound same-attempt/charge version-guarded repair with sealed source/candidate/invalid bytes, strict validation, independent verification/review, HUMAN repair-byte acceptance and exceptional P3 lineage; otherwise remain `POST_CHARGE_REPAIR_BLOCKED` |
| Worker/result uncertain | after | preserve charge and uncertainty; no acceptance |
| Verification fails | after | failed charged attempt; use remaining declared retry only |
| Reviewer transport fails / `REVIEW_PENDING` | after | coordinator preserves exact packet/attempt/charge and uses only bounded authorized re-probe/retry/fallback; restored or freshly HUMAN-authorized eligible route returns to `REVIEWING` on identical bytes; otherwise HUMAN may terminate as `REVIEW_UNAVAILABLE_CHARGED`, unaccepted with dependents blocked; no review waiver |
| Reviewer finds material defect | after | task remains unaccepted; correction follows WBS budget |
| Acceptance authority missing/stale/revoked / `ACCEPTANCE_PENDING` | after | coordinator writes no acceptance; fresh owner-rooted HUMAN chain/decision returns to projection, otherwise remain pending; timeout/silence has no effect |
| Acceptance projection persistence/validation fails | after | enter repair-required; repair the exact failed edge through its pre-write intent: first-edge repair reaches only unaccepted ACCEPTANCE_VERIFYING and still needs independent confirmation; confirmed final-edge repair may reach only the preverified action target; failure enters repair-blocked |
| HUMAN rejects | after | record reject through validated transition receipt; dependents remain blocked |

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
12. a report/helper claims PASS without execution-state closure;
13. invalidation append operation/index validation fails;
14. constructed or persisted charge-candidate ledger fails strict validation;
15. a reviewer substitution loses required lane/model-family diversity;
16. a delegated or other capable writer bypasses the procedural coordinator path;
17. an alternate acceptance owner lacks exact HUMAN delegation;
18. acceptance projection persists invalid bytes or its authority is revoked while pending;
19. a crash after charge leaves an interrupted attempt whose resume scope has drifted;
20. bundle sealing/persistence or post-seal retrieval fails;
21. migration restore bytes differ from the immutable backup;
22. ledger↔goal state or migrated-base/charge-lineage proof diverges;
23. one valid review lane exists but required lanes/diversity/Chairman closure do not;
24. acceptance verification is unavailable, inconclusive or refuted;
25. ledger write succeeds but transition-completion persistence crashes or fails.

A finding is material when it permits charge despite known unreadiness, loses/reuses a charge, changes acceptance, permits undeclared effects, or allows a non-HUMAN artifact to grant authority.

## 16. WBS-build entry criteria

An uncharged, inactive WBS candidate may be drafted and hashed only after:

- latest stabilization design bytes receive council `pass` or `pass_with_notes`;
- every material council finding is confirmed/refuted/dispositioned;
- HUMAN explicitly authorizes WBS drafting and selects the provisional attempt-ceiling/reallocation and contingency constraints the draft must satisfy;
- an attributable HUMAN migration decision record ID/raw SHA-256 binds a separate Working AIP/canonical Task Workspace/current-step/ASC, the explicit MIGRATION_MAINTENANCE state, exact pre-migration ledger hash/version, target contract, migration/restore operation, exact common AdministrativeResourceLedger ID/path/contract hash plus cumulative ceiling/allocation and no-attempt/no-bundle/no-charge effects; migration completes with an ordered initial/recovery/receipt/final-acceptance authority lineage, scoped AIP/Workspace lint/closure and an accepted base returned to FROZEN; exact selected bytes pass strict validation and independent review without changing charges/acceptance;
- an attributable HUMAN bootstrap decision record ID/raw SHA-256 binds a separate Working AIP/Workspace, the identical canonical uncharged AdministrativeResourceLedger ID/path/contract and cumulative ceiling, schema/validator/coordinator-only guarded-append operation, fixed append-overhead reserve/bounded outer-meter exemption and complete invocation/effect/append-receipt reconciliation, mechanical zero mission-attempt/charge attestations, allowed writes/stop conditions/reviewer/acceptance owner, AdmissionBundle/Invalidation schema hashes, deterministic validator argv, read-only prepare argv, create-once bundle-seal argv/storage effect, invalidation-append argv/effect and version-guarded coordinator ledger-write effect, charge-preimage/transition-intent, exact guarded writer plus immutable write-result receipt, AdmissionResourceReservation/accounting-append operation, canonical TransitionIntentIndex/P3_IN_FLIGHT validator, and create-once completion/finalize/restart operations, validator-backed policy-complete ReviewClosureReceipt, two-phase acceptance verification/projection, bounded post-charge ledger/acceptance-projection repair contracts, interrupted same-attempt disposition edges and their lineage/recovery contracts; the execution contract also supplies either exact existing boundary/bundle/seal/lineage JSON pointers with a strict-valid fixture or a HUMAN-authorized versioned extension/migration; all work/effects and initial/recovery/receipt/final-acceptance authority links are accounted, persisted, independently reviewed, HUMAN-accepted and re-hash to approved bytes;
- every WBS approver and planned acceptance owner has `actor.kind = human` and either equals the designated mission decision owner or is bound through a complete hash-pinned non-revoked HUMAN delegation chain with exact scope; the bundle contract carries and P13/P14/P16 re-verify those identities/maps;
- the migrated-base/current-ledger lineage contract includes the gap-free `ExecutionTransitionIntent`/`ExecutionTransitionCompletion` pair schema/validator/selected representation for every charge and ordinary status/outcome/review/acceptance write, and the same-epoch ledger↔goal predicate is present and passes;
- exact no-DSH/no-network/no-install/product boundaries remain explicit;
- the HUMAN-facing approval packet explicitly discloses that the admission gate is procedural only, may be bypassed by another natively capable writer, and retains an external-state TOCTOU residual risk;
- WBS-build handoff lists every required task, effect, command, source, verifier, reviewer, acceptance owner, stop condition, bundle/invalidation contract reference and residual-risk disclosure.

Drafting/hashing alone grants no selection, approval, admission or attempt authority. After exact candidate bytes exist, the HUMAN must bind the final ceiling/reallocation, contingency, WBS approval and allowed effects to that exact revision and SHA-256 before selection or admission; any later byte change requires a new binding.

The subsequent WBS must start with an uncharged admission proof followed by the first bound charge operation; product matrix/control/runner tasks remain blocked until that proof is accepted. Ledger migration and admission-mechanism bootstrap are pre-WBS control-plane prerequisites, not tasks hidden inside a WBS whose own P3/P15 could not yet pass.

## 17. Design acceptance boundary

Council review is advisory. A council `pass` does not approve this design, build a WBS, resume the mission, charge an attempt, accept attempt 66, or activate GAT. Those remain separate HUMAN decisions.
