# Control-Plane Stabilization Design v1

**Mission:** `multi-mission-web-ui`  
**Status:** Advisory design draft; inactive; not WBS or execution authority  
**Decision owner:** HUMAN  
**Working AIP:** `AIP-EXEC-009`  
**Review state:** Unreviewed candidate; must pass high-risk council review before WBS build

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

Product-level causes existed, especially the late split of matrix, control state, handlers/reducers and runner assembly. They do not explain why governance failures continued after that split. The systemic cause is the absence of one fail-closed pre-charge admission protocol that jointly proves readiness across every authoritative control surface.

This design stabilizes that control plane before another WBS is built. It does not modify GAT product behavior, create a scheduler, replace native DSH/AIWS mechanisms, or authorize execution.

## 2. Evidence basis and root-cause classification

The evidence-bound failure model is recorded at `.ai-work/workspaces/hoinv/TASK-20260915-control-plane-stabilization-design/04_findings.md#failure-model`.

### 2.1 Systemic root cause

**RC-SYSTEM-01:** admission is fragmented. WBS validation, execution-ledger validity, AIP/ASC transition, goal/Team authority, command capability, reviewer availability, ownership/quiescence and budget slack are checked by different mechanisms at different times. A charge can therefore be committed while another mandatory surface is invalid.

### 2.2 Contributing conditions

- product architecture was reviewed after implementation rather than before it;
- plan schema validation did not prove semantic command-to-deliverable closure;
- the mutable ledger accumulated incompatible historical representations;
- generated ASC state could be manually edited without a declared owning transition command;
- reviewer and sandbox capability were not reserved/proved before charge;
- execution ledger and runtime goal could disagree on active/paused state;
- attempt allocation left no recovery reserve.

### 2.3 Symptoms, not root causes

- failed runner attempts;
- sandbox refusal on attempt 65;
- reviewer failure on attempt 66;
- stale or manually reconciled ASC;
- strict progress-render rejection;
- repeated selection/reconciliation attempts.

## 3. Design goals and non-goals

### 3.1 Goals

1. Make all execution readiness checks one closed, content-addressed admission decision.
2. Ensure every admission failure occurs before attempt charge.
3. Preserve uncertain/interrupted charges after commit; never roll them back or reuse them.
4. Prevent manual or undeclared transitions of generated control artifacts.
5. Separate immutable history from the small current execution projection.
6. Reserve review and recovery capacity before work begins.
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

The GAT proposal remains higher authority for HUMAN decisions and Working-AIP/Workspace boundaries. This design is subordinate and inactive.

## 5. Admission state machine

```text
FROZEN
  └─prepare()──────────────────────────────────────────────┐
                                                           v
PREPARING ──any failed check──> NOT_READY (uncharged) ──re-prepare
  │
  └─all checks pinned + bundle sealed──> READY (uncharged)
                                          │
                                          ├─input/hash/state drift──> EXPIRED (uncharged)
                                          │
                                          └─HUMAN exact approval valid
                                                │
                                                v
                                           COMMITTING
                                                │
                           first durable write = charge + attempt allocation
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

No mutable mission control and no attempt charge is allowed in `FROZEN`, `PREPARING`, `NOT_READY`, `READY`, or `EXPIRED`. `READY` is not authority to execute; it only states that the exact admission bundle is mechanically complete.

### 5.2 Commit semantics

Cross-file atomicity is not claimed. The commit protocol is a logical write-ahead transaction:

1. Re-hash every bundle input immediately before commit.
2. Confirm the exact HUMAN WBS decision and active goal/Team authority still match.
3. Append one attempt allocation and increment the cumulative charge as the first durable mission mutation.
4. Apply only the already-declared task mutations.
5. If any post-charge mutation or dispatch fails, mark the same attempt `interrupted` or `failed`; preserve its charge and evidence. Never return to `READY` using that attempt ID.

The design prevents known unreadiness before charge; it does not pretend failures after a legitimate charge can be undone.

## 6. Immutable AdmissionBundle

A later WBS must require one immutable `AdmissionBundle` per charged attempt. It is an evidence artifact, not a new runtime service.

```yaml
schema: gat-admission-bundle/1
mission_id: multi-mission-web-ui
wbs_revision: <n>
wbs_sha256: <sha256>
task_id: <task>
proposed_attempt_id: <id>
prepared_by: <coordinator identity>
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
  source_integrity: <path+sha256>
  aip_asc_transition: <path+sha256>
  command_capability: <path+sha256>
  coordinator_quiescence: <path+sha256>
  team_authority: <path+sha256>
  goal_activation: <path+sha256>
  reviewer_reservation: <path+sha256>
  budget_reserve: <path+sha256>
state: READY
```

Every receipt records exact argv/tool identity where applicable, exit/result, canonical paths, raw-byte hashes and captured native identities. Missing, stale, ambiguous or degraded material makes the bundle `NOT_READY`; silence is failure.

## 7. Admission invariants and evidence

| Invariant | Mandatory evidence before charge | Failure disposition |
|---|---|---|
| P1 Plan identity | Official WBS validate/order/hash receipt; exact plan bytes unchanged | `NOT_READY` |
| P2 Plan semantic closure | Closed matrix mapping each deliverable/output to declared write path, owning command or permitted file operation, verifier, reviewer and acceptance owner | `NOT_READY`; revise plan |
| P3 Ledger strict validity | Official strict execution/progress validator PASS over exact `execution.json` | `NOT_READY`; migrate/repair separately |
| P4 Dependency acceptance | Every hard dependency has valid verification, required review and acceptance refs whose output hashes still match | `NOT_READY` |
| P5 Source integrity | All pinned immutable input hashes match current bytes | `NOT_READY`; invalidate carry-forward |
| P6 AIP/ASC closure | AIP lint PASS; declared `run_aip` transition produces fresh ASC; pointer/AIP/Workspace/task all agree | `NOT_READY` |
| P7 Command capability | Exact argv/cwd paths resolve; required effect backend is currently available; prohibited effects remain denied | `NOT_READY` |
| P8 Coordinator/quiescence | One coordinator identity; no predecessor, agent or job can still write; `active_work` reconciled | `NOT_READY` |
| P9 Team authority | Native Team plan revision is current and HUMAN-approved when Team execution is required; required members available | `NOT_READY` |
| P10 Goal activation | Goal identity/objective/hash agree and runtime reports active/armed when autonomous continuation is promised | `NOT_READY`; no promise of continuation |
| P11 Reviewer reservation | Required independent routes/capabilities and one typed fallback are reserved; Chairman separation where council applies | `NOT_READY` |
| P12 Budget safety | Charge ceiling covers selected attempt plus all mandatory downstream minima and mission-specific contingency reserve | `NOT_READY`; HUMAN decides ceiling/reallocation |
| P13 Authority | Exact HUMAN decision binds current WBS hash/effects; no review/report is treated as approval | `NOT_READY` |
| P14 Bundle freshness | All current hashes/native states still equal the sealed bundle immediately before commit | `EXPIRED`; re-prepare uncharged |

### 7.1 Mission-specific contingency rule

The next WBS must reserve at least:

- one attempt for future plan-selection/reconciliation after a material reviewed correction; and
- one attempt for a runtime/tooling recovery that cannot reuse an implementation attempt.

Therefore the mission-specific contingency reserve is **two attempts** until council or HUMAN selects another explicit amount. It cannot be silently borrowed by product tasks. Because v32 currently has no slack, the later WBS must either raise the cumulative ceiling or reduce downstream maxima with technical evidence; the design does not choose for the HUMAN.

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

The current `execution.json` remains frozen until a separately authorized migration task. Reporting or design work must not normalize it in place.

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

### 9.3 Migration acceptance

Migration passes only when:

- original bytes and hash remain available;
- every field has a deterministic before→after trace;
- charges and attempt identities are identical;
- accepted/interrupted/failed distinctions are unchanged;
- strict validation and execution-backed report both pass;
- no task becomes accepted or ready solely because of migration.

## 10. AIP/ASC generated-artifact policy

- AIP remains stable macro-control; runtime facts remain in Workspace.
- `.current_step.json` and ASC are generated projections owned by declared AIWS commands.
- Every WBS task requiring a pointer/ASC change must declare the exact `run_aip.py start|resume|step` argv that produces it.
- Manual ASC body edits are forbidden as acceptance evidence.
- `status` can inspect but cannot satisfy a transition requirement.
- Freshness must be observed after the final AIP mutation; a known pre-write mtime check cannot be treated as proof until a subsequent rebuild produces `fresh`.

## 11. Command and sandbox capability preflight

Capability preflight does not execute product behavior. It proves only that:

- executable names and referenced files exist at canonical paths;
- cwd is readable and declared;
- required sandbox/effect mode is available;
- timeout and output evidence can be collected;
- no command resolves through a forbidden symlink or external package store;
- exact command is included in root/task unions.

A capability receipt must distinguish `available`, `denied`, `unavailable`, and `not_probed`. `not_probed` is not PASS. A later task-command failure remains a charged attempt outcome, but an already-known unavailable backend must never be discovered after charging.

## 12. Reviewer reservation and fallback

Before charge:

1. Determine required rubric, independence, model diversity and HUMAN gate.
2. Inspect live routes and reserve the primary reviewer plus one fallback with distinct invocation identity.
3. Persist reviewer restrictions and evidence paths in the admission bundle.
4. A provider/transport/schema failure before valid verdict permits one typed retry or fallback on identical packet bytes without a new implementation attempt.
5. A valid adverse verdict is never retried to seek PASS; it requires disposition/revision.
6. Reviewer output remains advisory until the declared acceptance owner acts.
7. A task cannot name HUMAN as reviewer while naming coordinator as acceptance owner without an explicit authority rule explaining the two decisions.

For high-risk design/governance reviews, use two independent internal lanes from distinct model families, a sanitized outside-view lane, conditional adjudication and a separate Chairman, with all mandatory calls reserved before dispatch.

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
| Reviewer unavailable | before | use reserved fallback or remain `NOT_READY` |
| Goal/Team authority mismatch | before | remain frozen; HUMAN/runtime resolves |
| State changes after bundle sealed | before | `EXPIRED`; rebuild bundle without charge |
| Crash after charge but before dispatch | after | preserve charged attempt as interrupted; reconcile from write-ahead record |
| Worker/result uncertain | after | preserve charge and uncertainty; no acceptance |
| Verification fails | after | failed charged attempt; use remaining declared retry only |
| Reviewer transport fails | after | retry identical review packet via reserved fallback; same implementation attempt |
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
- ledger migration boundary and authority are decided;
- exact no-DSH/no-network/no-install/product boundaries remain explicit;
- WBS-build handoff lists every required task, effect, command, source, verifier, reviewer, acceptance owner and stop condition.

The subsequent WBS must start with stabilization/migration and admission proof. Product matrix/control/runner tasks remain blocked until that proof is accepted.

## 17. Design acceptance boundary

Council review is advisory. A council `pass` does not approve this design, build a WBS, resume the mission, charge an attempt, accept attempt 66, or activate GAT. Those remain separate HUMAN decisions.
