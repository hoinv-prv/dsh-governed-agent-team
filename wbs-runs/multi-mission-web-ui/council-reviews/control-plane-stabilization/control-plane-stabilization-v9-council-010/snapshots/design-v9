# Control-Plane Stabilization Design v9

**Mission:** `multi-mission-web-ui`  
**Status:** Advisory corrected design; inactive; not WBS or execution authority  
**Decision owner:** HUMAN  
**Working AIP:** `AIP-EXEC-009`  
**Predecessor:** v8 SHA-256 `8d783fac0e002d0bc72d75114ce04ecc07efea2c7a9ec94b538a69268002d0fa`  
**Review state:** Corrected after run-009 verified findings (Chairman schema-invalid); requires a new high-risk council run before WBS build

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

The evidence-bound failure model used for v9 is the immutable run-002 snapshot `snapshots/failure-model`, SHA-256 `434f1613751d8a2b5b8813936404e4567e698ea4ace88ed74863e2a56e4d8b86`; the mutable Workspace path is only its working source.

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
  ├─exact HUMAN migration-maintenance authorization──> MIGRATION_MAINTENANCE
  │                                                      ├─failure──> MIGRATION_RECOVERY
  │                                                      │              ├─exact restore proof──> FROZEN
  │                                                      │              └─restore mismatch──> MIGRATION_BLOCKED
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
                     │                                        (preserve charge/evidence)
                     v
                  VERIFYING ──fail──> FAILED_CHARGED
                     │
                     v
                  REVIEWING ──transport fail──> REVIEW_PENDING (same attempt)
                     │
                     ├─artifact finding──> REVISION_REQUIRED_CHARGED
                     └─valid review──> AWAITING_HUMAN_ACCEPTANCE
                                          ├─missing/stale/revoked authority──> ACCEPTANCE_PENDING
                                          ├─decision-owner HUMAN reject / delegated actor.kind=human reject──> REJECTED_CHARGED
                                          └─fresh attributable HUMAN accept decision bound to exact outputs──> ACCEPTED
```

### 5.1 Critical rule

No mutable mission ledger, selected-plan state, task/product state, acceptance state or attempt charge is procedurally allowed in `FROZEN`, `PREPARING`, `NOT_READY`, `READY`, or `EXPIRED`. Within the normal admission lifecycle, the only pre-charge writes are two coordinator-owned, uncharged evidence effects separately approved under P15: (a) create-once persistence of exact sealed `AdmissionBundle` bytes at the content-addressed canonical bundle path, and (b) append of one immutable `AdmissionInvalidation` through the approved append operation. Neither may allocate/consume an attempt, mutate the mission ledger/product/acceptance bytes, or overwrite an existing bundle; the invalidation operation may change only its canonical append-only index. `READY` is not authority to execute; it only attests that the exact admission bundle was complete at its recorded hashes/epochs. Every live predicate must be re-observed immediately at the charge boundary; any drift expires the bundle. Two administrative states remain outside normal admission: Section 6.3 `BOOTSTRAP_MAINTENANCE` may write only its HUMAN-bounded schema/tool/evidence paths and Section 9 `MIGRATION_MAINTENANCE` is the sole ledger-write exception before valid P3. Neither is READY/COMMITTING or may allocate a mission attempt; bootstrap must return exact HUMAN-accepted capability hashes, and migration must return an accepted migrated-base hash or exact restore proof, to `FROZEN` before admission begins.

### 5.2 Commit semantics

Cross-file atomicity is not claimed. The commit protocol is a logical write-ahead transaction:

1. Re-hash every bundle input and re-read the canonical invalidation index immediately before commit, applying exactly the bundle's sealed `freshness_rule`, predicate scope and comparison basis of native sequence plus recorded epoch.
2. Under that identical rule/scope/basis, confirm the exact HUMAN WBS decision and active goal/Team authority still match and re-observe every live P7–P11 predicate; a timestamp window never overrides a changed native-state predicate.
3. **Abort branch:** if steps 1–2 do not return fresh PASS, the live check uses a different/missing rule, epoch, sequence or scope, observation is unavailable, or any value drifts, perform no durable mission mutation, consume no attempt ID, use only the approved invalidation-append operation to append one immutable uncharged `AdmissionInvalidation`, and transition the candidate to `EXPIRED`/`NOT_READY` before re-prepare. If that append fails, remain `NOT_READY`, perform no ledger/task write, record the unavailable evidence outside mission controls, and require HUMAN/runtime repair before another prepare.
4. Deterministically construct the exact candidate `execution.json` bytes containing one attempt allocation, boundary receipt and cumulative charge. Record source-ledger hash/version and candidate hash; run the pinned official strict validator against those candidate bytes before any durable write.
5. **Charge branch:** the guarded ledger write may run only when steps 1–2 produced fresh PASS, no current invalidation exists, candidate strict validation passed, and the current source hash/version still equals the validated source. Any mismatch returns to the uncharged abort branch.
6. Persist exactly the validated candidate bytes in one version-guarded `execution.json` update as the first durable mission mutation; re-hash the persisted bytes, require equality with the candidate hash, and run the same strict validator over the persisted path before dispatch.
7. Only after persisted-byte equality and strict PASS, apply the already-declared task mutations and dispatch. If persisted validation fails, dispatch nothing, freeze the ledger, preserve the charged attempt plus invalid bytes/validation evidence, and require separately HUMAN-authorized repair to project that same attempt as `failed`; never allocate a replacement attempt implicitly.
8. If any later post-charge mutation or dispatch fails, mark the same attempt `interrupted` or `failed`; preserve its charge and evidence. Never return to `READY` using that attempt ID.

The design detects known unreadiness before charge; it does not pretend failures after a legitimate charge can be undone.

### 5.3 Enforcement boundary and residual race

No existing pinned Source of Truth identifies a non-bypassable native charge entry point that consumes an AdmissionBundle. Therefore v9 claims **procedural fail-closed governance**, not hard runtime enforcement. The coordinator must bind the bundle hash to the immediately following charge record and re-observe live goal, Team, worker/job, sandbox and reviewer-availability predicates at that boundary. An irreducible check-to-charge race remains when external state can change between observation and mutation. A delegated or otherwise capable writer may also bypass the procedural single-coordinator path because no native capability denial is established; P8 observes topology/quiescence but does not prove such a writer is technically unable to charge.

Hard prevention of bypass or a true compare-and-swap charge requires a separately approved DSH/runtime change and is outside this design. Until such a capability exists, any path that cannot demonstrate coordinator compliance and boundary re-observation is `NOT_READY`; the residual enforcement/race risk must be visible to the HUMAN in the WBS approval packet.

### 5.4 Acceptance boundary

A valid review never implies acceptance. It moves the charged attempt only to `AWAITING_HUMAN_ACCEPTANCE`. The acceptance owner must be `actor.kind = human`—either the decision owner or a HUMAN actor named by a non-revoked HUMAN delegation—and must provide a fresh attributable decision whose raw record binds the exact mission/WBS/task/attempt, output and verifier hashes, review/report hashes, accept-or-reject action, scope and current P16 owner/delegation record plus revocation state. A non-HUMAN delegate is invalid even if some HUMAN record names it. Missing, stale, ambiguous, non-HUMAN or revoked authority leaves `ACCEPTANCE_PENDING`; an explicit rejection produces `REJECTED_CHARGED` and preserves the same attempt/evidence for revision or closure.

The coordinator may only project that exact decision through the HUMAN-approved acceptance operation or permitted version-guarded file edit declared in the WBS closure matrix. Before writing, it deterministically constructs and strictly validates the candidate acceptance projection against the current ledger hash/version; after writing, it re-hashes and strictly validates persisted bytes. An independent verifier confirms decision/hash projection. Only an exact accept record can produce `ACCEPTED`; reviewer, coordinator, task declaration, timeout or silence can never do so. A write/validation mismatch freezes acceptance state and requires separately authorized repair without changing the original HUMAN decision.

## 6. Immutable AdmissionBundle

A later WBS must require one immutable `AdmissionBundle` per charged attempt. It is an evidence artifact, not a new runtime service.

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
receipts:
  plan_format: <path+sha256>
  plan_semantics: <path+sha256>
  execution_strict: <path+sha256>
  dependency_acceptance: <path+sha256>
  source_integrity: <path+sha256; includes every task input>
  design_basis: <v9 design path+sha256 plus immutable run-002 failure-model snapshot path+sha256>
  aip_asc_transition: <path+sha256>
  command_capability: <path+sha256>
  coordinator_quiescence: <path+sha256>
  team_authority: <path+sha256>
  goal_activation: <path+sha256>
  execution_goal_state: <execution ledger hash/version + recorded run_state/pause-resume marker + runtime goal identity/state/sequence + equality result + observed_epoch>
  reviewer_availability: <pre-charge policy/template hashes + primary/fallback provider/model/family/role matrix + retry policy + call budget; no premature final-packet hash>
  budget_reserve: <path+sha256>
  wbs_authority: <decision record id + raw-record sha256 + HUMAN actor + scope + bound WBS revision/sha256 + allowed effects + revocation state>
  bootstrap_authority: <decision record id + raw-record sha256 + HUMAN actor + scope + bound bundle/invalidation schema hashes + validator/prepare/seal/append argv hashes + guarded-write effect + revocation state>
  acceptance_authority: <per-task acceptance owner map + HUMAN decision record IDs/raw hashes + required owner actor.kind=human + scopes + revocation state; exact decision-owner HUMAN when no delegation; non-HUMAN delegate invalid>
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

`AdmissionBundle` above is a **proposed design contract**, not an existing authoritative schema. Before any successor WBS is built, a separately HUMAN-authorized control-plane stabilization action must persist and approve: (a) the exact schema bytes and SHA-256; (b) a deterministic validator and its exact `python3 <approved-validator-path> validate <bundle-path>` argv; and (c) the coordinator-owned read-only prepare operation and exact `python3 <approved-prepare-path> prepare ...` argv, which computes canonical bytes without changing mission/control state; (d) the coordinator-owned create-once bundle-seal operation, content-addressed storage root, exact `python3 <approved-bundle-path> seal ...` argv, allowed-effect contract, post-write hash/schema validation and crash recovery; and (e) the coordinator-owned uncharged invalidation append operation, canonical index path, exact `python3 <approved-invalidation-path> append ...` argv, allowed-effect contract, deterministic validator and recovery behavior. Until those real paths/hashes/commands exist and pass, admission is `NOT_READY`; v9 does not invent them or claim P1/P2 mechanical validation.

After bootstrap, the coordinator owns read-only bundle computation through the approved prepare command and exact durable sealing through the separate create-once seal command. `READY` is legal only after the complete canonical bundle bytes and validator receipt are durably stored at a path derived from `bundle_sha256`, re-read equal to the computed bytes, and independently retrievable; collision, overwrite request, missing bytes, hash/schema mismatch or seal crash leaves `NOT_READY`. A crash after seal but before charge leaves an uncharged retrievable bundle that must pass P14 or expire; a crash after charge can reconstruct proof from the charge-bound bundle hash and canonical bytes. The coordinator also owns the first durable charge/boundary mutation through one version-guarded `execution.json` update using the runtime's native guarded file write/edit operation, bounded by the HUMAN-approved WBS hash and declared write effect. A stale-version conflict, failed predicate, unavailable guard or missing authority aborts with no charge and no attempt allocation. The operation must re-observe live predicates and bind the immutable bundle full-file hash, `AdmissionBundleSeal` sidecar hash, boundary receipt and allocated attempt ID in the one ledger update. This is attributable procedural ownership, not a non-bypassable native DSH hook.

### 6.2 Immutable invalidation representation

A sealed bundle never changes. At seal time it pins the invalidation index's canonical path, raw-byte SHA-256, item count, last sequence, owner identity, observation epoch and the same freshness rule used by the bundle. An unavailable index or any mismatch makes the candidate `NOT_READY`, never `READY`.

When drift, withdrawal or failed re-observation is detected, the coordinator invokes only the HUMAN-approved invalidation append argv/effect and appends an immutable uncharged `AdmissionInvalidation` evidence record containing `bundle_sha256`, reason code, observed prior/current values or unavailable predicate, actor identity and observation sequence. The append receipt records operation path/hash/argv, canonical index before/after hashes and sequences, actor, zero charge/attempt effect and validation result; failure leaves `NOT_READY` with no mission-ledger write. The charge-boundary check re-reads the same canonical index, requires an append-only extension of the sealed prefix, rejects truncation/replacement/path/owner/sequence mismatch, and blocks if any extension names the bundle hash. Because an invalidation can still race the ledger write, that window remains part of the disclosed TOCTOU residual risk. The sealed `READY` bundle proves only a past observation and is never current-validity evidence by itself.

### 6.3 Bootstrap governance and accounting

Bootstrap implementation is not free or implicit work. It enters `BOOTSTRAP_MAINTENANCE` only through a separately HUMAN-authorized administrative task under its own Working AIP and Task Workspace, outside the frozen mission-attempt ledger until a valid migrated ledger exists. Before work, the HUMAN decision binds the objective, exact allowed write paths/effects, prohibited product/network/install/activation effects, administrative-resource accounting method, model-call ceiling, stop conditions, verifier, independent reviewer and HUMAN acceptance owner. If the HUMAN chooses uncharged administrative accounting rather than mission-attempt charging, that exception and its bounded ceiling must be explicit; the coordinator cannot choose or hide it.

Every bootstrap model/tool call, file effect, retry and review is recorded in that Workspace against the selected ceiling. Any ceiling exhaustion, scope drift or missing accounting stops the task without making P15 pass. Only exact HUMAN-accepted schema/tool/operation bytes and hashes, with AIP/Workspace evidence, verification and independent review, may populate `bootstrap_authority`; bootstrap work cannot be hidden inside a successor WBS or silently consume its contingency reserve. Verified/reviewed exact bytes plus an attributable HUMAN acceptance return their hashes to `FROZEN`; failure, ceiling exhaustion or scope drift enters `BOOTSTRAP_BLOCKED` until a new HUMAN decision. This design/review task specifies the requirement but does not authorize or implement the bootstrap.

## 7. Admission invariants and evidence

| Invariant | Mandatory evidence before charge | Failure disposition |
|---|---|---|
| P1 Plan identity | Official WBS validate/order/hash receipt; exact plan bytes unchanged | `NOT_READY` |
| P2 Plan semantic closure | Closed matrix mapping each deliverable/output to declared write path, owning command or permitted file operation, verifier, reviewer and acceptance owner | `NOT_READY`; revise plan |
| P3 Ledger strict validity/lineage | Official strict execution/progress validator PASS over exact `execution.json`; bundle lineage receipt proves the current source is either the exact HUMAN-accepted migrated base before first charge or an ordered chain of persisted, strictly valid, HUMAN-authorized append-only charge successors from that base | `NOT_READY`; divergence, missing predecessor/receipt or non-append mutation requires separate HUMAN-authorized repair/migration |
| P4 Dependency acceptance | Every hard dependency has valid verification, required review and acceptance refs whose output hashes still match | `NOT_READY` |
| P5 Source/design-basis integrity | All pinned immutable task-input hashes match current bytes; stabilization/WBS-build admission also re-hashes the current design and run-002 failure-model snapshot `434f1613…d8b86` through the declared read-only hashing command | `NOT_READY`; invalidate carry-forward |
| P6 AIP/ASC closure | AIP lint PASS; declared `run_aip` transition produces fresh ASC; pointer/AIP/Workspace/task all agree | `NOT_READY` |
| P7 Command authorization/capability | Exact argv appears in the pinned root/task allowed-command union whose hash is recorded; argv/cwd paths resolve; required effect backend is observed available; prohibited effects remain denied | `NOT_READY` |
| P8 Coordinator identity/quiescence snapshot | At the receipt epoch, native Team/goal listings show one Team Lead coordinator, no delegated-coordinator topology, every enumerated mission-capable writer stopped/settled, and `active_work` equal to that snapshot; this is observation plus a procedural role restriction, not proof that a delegated writer lacks native charge capability | `NOT_READY` on identity/topology mismatch, unavailable enumeration or unsettled writer; HUMAN reassigns/ends the conflict before re-prepare; disclose delegated-writer bypass residual risk |
| P9 Team authority | Native Team plan revision is current and HUMAN-approved when Team execution is required; required members available | `NOT_READY` |
| P10 Goal/execution-state synchronization | Goal identity/objective/hash agree; at one observation epoch the ledger's recorded run state and pause/resume marker equal the runtime goal state/activation, and runtime reports active/armed when autonomous continuation is promised | `NOT_READY` on any ledger↔goal mismatch or unavailable marker; no promise of continuation |
| P11 Reviewer availability/fallback | Pre-charge live discovery records provider, model, route family, eligible role, immutable review policy/template identity and typed retry policy for each primary/fallback; final packet identity is deferred until output/verifier bytes exist and is then required before review dispatch; a pinned substitution matrix proves every allowed single-primary replacement still supplies the mandatory lane and two distinct internal model families; no capacity reservation is claimed without a real provider primitive | `NOT_READY` when a primary/fallback is unavailable or any allowed substitution loses lane coverage/diversity; otherwise record double-booking/provider-loss residual risk |
| P12 Budget safety | Charge ceiling covers selected attempt plus all mandatory downstream minima and mission-specific contingency reserve | `NOT_READY`; HUMAN decides ceiling/reallocation |
| P13 Authority | Bundle `wbs_authority` receipt names exact HUMAN decision record ID/raw hash, actor, non-revoked scope, current WBS revision/hash and allowed effects; boundary re-verification re-hashes that record and checks scope/revocation | `NOT_READY` on absence, ambiguity, revocation or drift; no review/report is approval |
| P14 Bundle freshness/invalidation | All current hashes/native states, including atomic P13/P15/P16 decision receipts, ledger↔goal equality, ledger lineage and revocation/scope state, still equal the sealed bundle immediately before commit and no current `AdmissionInvalidation` exists for its hash | `EXPIRED`; abort with no mission write or attempt consumption; append uncharged invalidation evidence; re-prepare |
| P15 Admission mechanism bootstrap/authority | Bundle `bootstrap_authority` receipt names exact HUMAN decision record ID/raw hash, actor, non-revoked scope and bound bundle/invalidation schema hashes, validator/prepare/bundle-seal/invalidation-append argv hashes, guarded-write effect and migration boundary; a separately authorized bootstrap AIP/Workspace proves bounded administrative or attempt/resource accounting, model-call ceiling, allowed effects, verification/review and HUMAN acceptance; every capability exists and passes; P14 re-hashes record/artifacts and checks scope/revocation | `NOT_READY`; absence, ambiguity, revocation, drift or capability failure aborts uncharged; complete/re-authorize bootstrap before WBS admission |
| P16 Acceptance authority | Bundle `acceptance_authority` receipt maps every task acceptance owner to the HUMAN decision owner or to an alternate with `actor.kind = human` explicitly named by a separate non-revoked HUMAN authority decision ID/raw hash and exact task/scope; any non-HUMAN alternate is invalid; P14 re-verifies every delegation record before charge; at the later Section 5.4 acceptance boundary the current decision additionally binds exact task/attempt/output/verifier/review hashes and accept/reject action | `NOT_READY` before charge or `ACCEPTANCE_PENDING` afterward; a task declaration, reviewer report or coordinator cannot originate/transfer acceptance authority |

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

The HUMAN authorization must bind the Working AIP ID/hash, canonical Workspace path, current step/ASC, exact pre-migration ledger SHA-256/version, target contract hash, exact migration/restore argv or permitted version-guarded file operation, allowed write path, no-product-effect boundary, uncharged administrative-resource accounting method, model/tool-call ceiling, stop conditions, verifier, reviewer and HUMAN acceptance owner; any source hash/version change before write invalidates the authorization and requires a new HUMAN decision. The migration operation and receipt must assert and mechanically verify: no attempt ID allocated or consumed, `attempts_charged` unchanged, attempt set unchanged, no AdmissionBundle sealed/consumed, no task/product mutation, and no acceptance transition. This authority cannot be reused for a charge write. For the first post-migration charge, P3/P15 require the pre-charge source to equal the exact HUMAN-accepted migrated base bytes/hash/version. For every later charge, they require an ordered append-only lineage from that base through each prior validated candidate/persisted hash and bound charge receipt; expected authorized attempt/charge appends are accepted only through that chain, while any unlinked or non-append change is `NOT_READY`. The coordinator is the migration-operation owner, a separate verifier and reviewer validate the candidate, and only the HUMAN accepts/selects migrated bytes. The state exits only to `FROZEN(new base)` after exact HUMAN acceptance of the candidate hash plus governed scoped AIP/Workspace lint and closure evidence, or through `MIGRATION_RECOVERY` to `FROZEN` after exact backup-equality proof; restore mismatch enters `MIGRATION_BLOCKED`. Every administrative resource/tool/model call and retry is recorded against the authorized ceiling, never against a mission attempt.

### 9.2 Migration protocol

0. Start/resume the separately approved Working AIP, verify one canonical Workspace/current-step/ASC binding, and stop on lint/control mismatch.
1. Copy exact pre-migration bytes to a new immutable evidence directory and record SHA-256.
2. Pin the authoritative target `dsh-wbs-execution/1` contract/tool version.
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
- Every generated or mutable mission-control artifact has exactly one declared owner and write mechanism in the approved closure matrix: AIP pointer/ASC → exact `run_aip.py start|resume|step` argv; execution ledger/current projection → coordinator through the declared migration operation or one version-guarded native file write/edit; progress/report rendering → the official read-only renderer; AdmissionBundle computation → coordinator through the read-only prepare command; durable AdmissionBundle bytes → coordinator through the separate create-once content-addressed seal command; AdmissionInvalidation → coordinator through the bootstrap-pinned canonical index and exact uncharged append argv/effect (the invalidation-specific Section 5.1 exception); charge/boundary record → coordinator through the single version-guarded `execution.json` write bounded by HUMAN-approved WBS/effects; acceptance decision → exact decision-owner HUMAN or currently delegated acceptor whose actor.kind is HUMAN; non-HUMAN delegates prohibited; acceptance projection → coordinator through the closure-matrix-declared guarded operation/edit after candidate strict validation, with independent verification.
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
8. The coordinator may record/project an exact HUMAN decision but can never originate required acceptance. Any alternate acceptor must have actor.kind HUMAN and requires a separately recorded HUMAN authority decision before admission; a task-declared rule cannot transfer that authority.

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
| Source/dependency hash drifts | before | expire bundle; invalidate affected acceptance |
| AIP/ASC transition missing | before | revise WBS to declare owning command |
| Sandbox/effect unavailable | before | `NOT_READY`; do not dispatch through workaround |
| Reviewer unavailable | before | use a previously discovered fallback after a fresh probe, or remain `NOT_READY`; no capacity reservation is implied |
| Goal/Team authority or coordinator/native-Lead mismatch, including delegated coordinator topology | before | uncharged abort; remain frozen; HUMAN/runtime ends, reassigns or explicitly restores one native Team Lead coordinator, then re-prepare |
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
12. a report/helper claims PASS without execution-state closure;
13. invalidation append operation/index validation fails;
14. constructed or persisted charge-candidate ledger fails strict validation;
15. a reviewer substitution loses required lane/model-family diversity;
16. a delegated or other capable writer bypasses the procedural coordinator path;
17. an alternate acceptance owner lacks exact HUMAN delegation;
18. bundle sealing/persistence or post-seal retrieval fails;
19. migration restore bytes differ from the immutable backup;
20. ledger↔goal state or migrated-base/charge-lineage proof diverges.

A finding is material when it permits charge despite known unreadiness, loses/reuses a charge, changes acceptance, permits undeclared effects, or allows a non-HUMAN artifact to grant authority.

## 16. WBS-build entry criteria

An uncharged, inactive WBS candidate may be drafted and hashed only after:

- latest stabilization design bytes receive council `pass` or `pass_with_notes`;
- every material council finding is confirmed/refuted/dispositioned;
- HUMAN explicitly authorizes WBS drafting and selects the provisional attempt-ceiling/reallocation and contingency constraints the draft must satisfy;
- an attributable HUMAN migration decision record ID/raw SHA-256 binds a separate Working AIP/canonical Task Workspace/current-step/ASC, the explicit MIGRATION_MAINTENANCE state, exact pre-migration ledger hash/version, target contract, migration/restore operation, administrative-resource/model-call ceiling and no-attempt/no-bundle/no-charge effects; migration completes with scoped AIP/Workspace lint/closure and returns an accepted base to FROZEN; exact selected bytes pass strict validation and independent review without changing charges/acceptance;
- an attributable HUMAN bootstrap decision record ID/raw SHA-256 binds a separate Working AIP/Workspace, administrative or attempt/resource accounting method, model-call ceiling, allowed writes/stop conditions/reviewer/acceptance owner, plus the AdmissionBundle/Invalidation schema hashes, deterministic validator argv, read-only prepare argv, create-once bundle-seal argv/storage effect, invalidation-append argv/effect and version-guarded coordinator ledger-write effect; all work/effects are accounted, persisted, independently reviewed, HUMAN-accepted and re-hash to the approved bytes;
- every planned acceptance owner is the HUMAN decision owner or is bound by an exact non-revoked HUMAN delegation decision record/scope; the bundle contract carries and P14 re-verifies that map;
- the migrated-base/current-ledger lineage contract and same-epoch ledger↔goal state predicate are present and pass;
- exact no-DSH/no-network/no-install/product boundaries remain explicit;
- the HUMAN-facing approval packet explicitly discloses that the admission gate is procedural only, may be bypassed by another natively capable writer, and retains an external-state TOCTOU residual risk;
- WBS-build handoff lists every required task, effect, command, source, verifier, reviewer, acceptance owner, stop condition, bundle/invalidation contract reference and residual-risk disclosure.

Drafting/hashing alone grants no selection, approval, admission or attempt authority. After exact candidate bytes exist, the HUMAN must bind the final ceiling/reallocation, contingency, WBS approval and allowed effects to that exact revision and SHA-256 before selection or admission; any later byte change requires a new binding.

The subsequent WBS must start with an uncharged admission proof followed by the first bound charge operation; product matrix/control/runner tasks remain blocked until that proof is accepted. Ledger migration and admission-mechanism bootstrap are pre-WBS control-plane prerequisites, not tasks hidden inside a WBS whose own P3/P15 could not yet pass.

## 17. Design acceptance boundary

Council review is advisory. A council `pass` does not approve this design, build a WBS, resume the mission, charge an attempt, accept attempt 66, or activate GAT. Those remain separate HUMAN decisions.
