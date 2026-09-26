# Control-Plane Stabilization Consistency Audit — Design v32

**Audited artifact:** `control-plane-stabilization-design.v32.md`  
**Audited SHA-256:** `96a038597a655ce6b20fc73994128436d1043d4a97e697e4b7bc7175f70a1790`  
**Mode:** read-only pre-council consistency audit  
**Scope:** state machine, P3/P15 lineage, failure matrix, hash construction, bundle identity, administrative accounting, recovery allocation, and handoff closure  
**Result:** **revision required before another council run**

## Executive result

The v32 corrections address the four run-032 findings locally, but the composed contract is not yet closed. The audit confirmed **17 findings**: 1 critical, 12 high, and 4 medium. No finding requires a new runtime service or a claim of native non-bypassability; all corrections are contract, state, serialization, accounting, validator, fixture, or handoff clarifications.

## Findings

| ID | Severity | Area | Finding | Required correction |
|---|---|---|---|---|
| CS-01 | Critical | State/write order | §5 calls charge/allocation the first durable write although source/candidate/intent evidence and index OPEN are durable pre-charge writes. | Rename it first **mission-ledger** write and place intent publication/OPEN substates before charge. |
| CS-02 | High | State closure | §5 omits operative §9.1 states (`INTENT_INDEX_OPEN_PENDING`, `INTENT_CORRUPT_BLOCKED`, `TRANSITION_IN_FLIGHT`, generic recovery blocked, and charged/uncharged completion corruption). | Add a normative composed transition table covering every state and edge. |
| CS-03 | High | Candidate-equal recovery | Candidate-equal bytes without a valid writer receipt have §9.1 recovery but no matching main-machine/failure-matrix branch; decision and exceptional-record names differ. | Add the branch and normalize `UNKNOWN_WRITE_PROVENANCE` decision versus `UNKNOWN_APPLIED_NO_RECEIPT` lineage record. |
| CS-04 | High | Accounting states | `ADMISSION_ACCOUNTING_BLOCKED` is absent and `CHARGED_ACCOUNTING_BLOCKED` is a sink despite defined recovery/allocation behavior. | Model preserved intent/charge, allowed reconciliation, exhaustion and terminal outcomes. |
| CS-05 | High | Acceptance states | Acceptance verification failed/pending/conflict are diagram sinks while prose permits guarded reverification/new HUMAN decision. | Add exact return edges and matrix dispositions. |
| CS-06 | High | Corruption dispatch | Generic “any record/index disagreement” recovery conflicts with charge-sensitive completion-corruption states. | Dispatch absent/unmatched, uncharged-corrupt, and charged-corrupt cases explicitly. |
| CS-07 | High | P15/handoff | P15 and handoff do not form a closed capability manifest for every exceptional record/state/edge required by P3. | Require state/edge/record/path/schema/hash/validator/argv/effect/authority/accounting/fixture/P3 rule for every transition. |
| CS-08 | Medium | Missing-intent matrix | `INTENT_INDEX_OPEN_PENDING` absent/exact-valid cases are tested but absent from the failure matrix. | Add deterministic idempotent publication/OPEN/NOT_APPLIED/CLOSE response. |
| CS-09 | Medium | Stale terminology | “post-charge ledger repair” survives despite prohibition of alternate repair paths. | Replace with accounting finalization/reconciliation, interrupted disposition, or provenance-terminal recovery. |
| CH-01 | High | Hash cycle | Generic §9.1 says the boundary receipt binds planned intent path, conflicting with the charge-edge rule that derives content-addressed path only after final intent bytes. | Carve out charge intent: preflight binds logical ID/body commitment/prior index/expected sequence; final path is bound later. |
| CH-02 | Medium | Hash projection | `logical_intent_id`, candidate-template hash, and excluded-field projection are under-defined and “four” is numerically wrong. | Specify closed input projections and named exclusions byte-for-byte. |
| CH-03 | Medium | Serialization | Canonical JSON, UTF-8 framing, normalization, hash encoding/case and concatenation domains are not pinned. | Pin one serialization profile and exact raw-byte hash domains. |
| CA-01 | Medium | Bundle identity | Bundle hash/path and seal hash/path are ambiguous and can be conflated. | Define out-of-band `bundle_sha256` and independent `seal_sha256` derivations and paths. |
| BA-01 | High | Double debit | Root append overhead can be charged both to RootControlJournal recovery and reservation/admin usage. | Split root and admin overhead/ceilings and charge each unit exactly once. |
| BA-02 | High | Recovery arithmetic | `PostChargeRecoveryAllocation` lacks named debit/usage/remaining fields and recurrence. | Define `D`, `B`, `D_remaining`, global recurrence, UNKNOWN=max, overhead, no-refund and fixtures. |
| BA-03 | High | Prefix exception | Sealed-prefix validation allows only original pre-bound IDs, while recovery allocation introduces fresh IDs. | Define a narrow post-charge P3/P15 exception tied to original reservation/attempt/open intent, never pre-charge readiness. |
| BA-04 | High | Dual-ceiling exhaustion | Recovery checks global ceiling but also requires root-journal capacity; root exhaustion is otherwise fail-stop. | Require both capacities; either exhaustion preserves charged blocked state and is terminal fail-stop. |

## Cross-cutting correction plan

1. Replace the illustrative §5 diagram with a normative composed state/transition table and retain the diagram only as a summary.
2. Establish a closed transition-capability manifest used identically by P3, P15, failure matrix, fixtures and handoff.
3. Publish one serialization/hash-domain profile shared by bundle, seal, intent, index, administrative ledger and root journal.
4. Separate pre-hash logical IDs from content-addressed paths in every create-once object.
5. Split root-recovery accounting from administrative/reservation accounting and specify a validator recurrence for post-charge recovery allocations.
6. Make recovery allocation a post-charge-only exceptional extension; it cannot satisfy readiness, create/reuse an attempt, or authorize success dispatch unless the explicitly bound recovery target permits it.
7. Run deterministic cross-reference checks before the next council: state coverage, record coverage, stale term scan, hash-domain dependency DAG, arithmetic fixtures, and exact design-basis hash verification.

## Gate

No new council run should start until all findings above are either corrected in a new immutable design revision or explicitly dispositioned with evidence. WBS build, selection and product execution remain out of scope and frozen.

## Remediation verification

A separate read-only verification of design v33 initially classified 16 findings corrected, CH-02 partial, and found two new high cross-section defects: stale v32 design-basis binding and an alternate nonterminal charged-corruption outcome. Before freezing v33, all three were corrected by: (1) defining the candidate-template projection as the complete strict-schema candidate tree minus exactly one selected preflight pointer and replacing aggregate commitment placeholders with closed named objects; (2) making the bundle bind the latest council-passed HUMAN-accepted design through an out-of-band raw-byte hash; and (3) making index supersession an intermediate effect on the sole terminal `FAILED_CHARGED_COMPLETION_CORRUPT` path. Deterministic checks must be rerun against final v33 bytes.
