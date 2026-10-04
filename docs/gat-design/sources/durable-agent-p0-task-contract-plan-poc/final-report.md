# Final corrected P0 decision report

## Binding and decision status

- Mission: `durable-agent-p0-task-contract-plan-poc`
- Approved WBS: revision 6
- Exact WBS SHA-256: `1fce7d02edf2916b52463516e87e2c10a91fc9ad44eacd7f3e014315db49a6c2`
- Task/attempt: `p0_final` / `p0_final-a01-r6`
- Independent integration review: `meets_criteria`, advisory `accept`
- Final artifact status: **candidate for independent final review and HUMAN decision; not self-accepted**

## Advisory recommendation

**ACCEPT**, but only for the bounded P0 conclusion that the frozen, host-supplied `TaskContract` and `PlanProposal` inputs can be validated and normalized through the tested deterministic contract-to-plan seam without expanding declared authority.

This recommendation is limited to the exact frozen candidate bytes and the evidence below. It is **not** production acceptance and does not authorize P2 persistence/checkpoint work, BS1 or later sprints, real file or command effects, host integration, live model/provider/network use, WBS execution, queue/delegation behavior, a production sandbox, or any downstream WBS execution.

The HUMAN alone must review the independently reviewed report and explicitly choose **accept**, **defer**, or **reject**. Until that explicit choice, P0 remains unaccepted. An accept choice approves only this bounded P0 conclusion and its frozen artifacts as possible inputs to later planning; it grants no downstream execution authority.

## Exact frozen candidate and command evidence

| Candidate artifact | SHA-256 |
|---|---|
| `oracle/fixture-manifest.json` | `a1e413b70a9d3cc9eb66b0f005f97e90c2c9a18db0283c6051572a9dbc253acf` |
| `oracle/p0-oracle.test.mjs` | `29aec0edbd6e75057636efc06ba7da25608a81b5f9deb0ecb286cfcbfdd3ec3f` |
| `prototype/contract-plan.mjs` | `36da5767a171232154dcbe993b05695e8621a8a9920f2b428b7752b0ce6f9105` |

Coordinator-native execution of the exact authorized integration commands on those bytes established:

- `node --test wbs-runs/durable-agent-p0-task-contract-plan-poc/oracle/p0-oracle.test.mjs`: exit 0; **135 passed, 0 failed, 0 skipped/cancelled/todo**.
- Exact three-file `sha256sum`: exit 0; all three values matched the table above in declared argument order.

The integration worker's executor had refused before process start because its workspace-write sandbox backend was unavailable. This infrastructure limitation is preserved in the record; the coordinator did not broaden the command and subsequently produced the exact native evidence above. Command success is necessary evidence, not acceptance authority.

## Requirement disposition

| Requirement | Final evidence-bound disposition |
|---|---|
| `p0-origin-equivalence` | Supported: standalone and WBS origins preserve the same normalized core; named origin authority-expansion mutations are rejected. |
| `p0-contract-completeness` | Supported: the full contract and both `contract_id`-only / `contract_hash`-only alternatives pass; named omission/invalidity cases cover every mandatory field group. |
| `p0-deterministic-plan` | Supported: repeated inputs produce identical canonical bytes/hash; all five step types, stable order, exact `max_steps`, and one final handoff are covered; malformed, unstable, excess, stale, and mismatched plans are rejected. |
| `p0-replan-boundary` | Supported: the safe replan preserves the complete canonical state, policy, parent/history/counters, authority, verification, ceilings, and changes only unexecuted steps; expansion and reset cases are rejected. |
| `p0-completed-step-binding` | Supported after revision 6: snapshot and parent history use closed `{id, order, result_hash, step_body}` entries; every completed proposal/output step deep-equals its bound body; the completed-body-only mutation returns `COMPLETED_HISTORY_MUTATION`. |
| `p0-retry-normalization` | Supported only for deterministic P0 declarations/normalization: finite domains, ceilings, precedence, total cap, debit declaration, UNKNOWN rule, no-reset, and handoff retry are frozen and negatively tested. Durable runtime persistence and transitions remain P2. |
| `p0-host-plugin-seam` | Supported as a bounded PoC: deterministic data seam, exact `node:crypto` dependency, structural module-load classification, intent counting, and bounded network guards. This is not a production sandbox or complete JavaScript security proof. |
| `p0-decision` | Supported: exact hashes, commands, reviews, limitations, lineage, and accept/defer/reject rules are bound without claiming self-acceptance. |
| `p0-carry-forward-accounting` | Supported: all failed, retired, corrected, and accepted attempts remain charged; final dispatch reaches exactly 11 attempts / 430 minutes with zero capacity. |
| `p0-governance` | Supported through final-artifact production: bounded attempts, independent review, retained dissent/adjudication, governed learning disposition, and HUMAN-only final authority. Independent final review and the HUMAN choice remain outstanding gates. |

## Complete failure, dissent, and adjudication record

No failed result or dissent is erased:

1. **`p0_oracle-a01-r3` failed independent review.** Executable replan preservation was under-specified, dependency control was a bypassable blacklist, and identity was incorrectly conjunctive. The RCA required full preservation checks, exact allowlisting, and `contract_id | contract_hash` alternatives.
2. **`p0_oracle-a02-r3` failed independent review.** Identity was corrected, but `max_steps` and complete normalized-policy replan equality remained incomplete, and `export * as name from` could bypass enumeration. The revision-3 task stopped; no third attempt was allowed.
3. **`p0_oracle_invariant_checklist-a01-r5` passed.** The successor approach first froze a closed state/policy checklist and adversarial import grammar rather than merely adding capacity.
4. **`p0_oracle_finalize-a01-r5` failed independent review.** Executable template interpolation and optional/bracket process loader access could bypass the example-driven classifier. RCA changed the correction to structural recursive executable-region and forbidden-access closure.
5. **`p0_oracle_finalize-a02-r5` passed independent review.** Recursive interpolation, forbidden access forms, no-load bypass guards, original fixtures, policy closure, and the P0/P2 boundary were retained.
6. **`p0_prototype-a01-r5` failed command verification: 129/134.** The prototype demanded an extra allowed-path read grant for a target already authorized by an exact verification declaration. RCA corrected verification authority while preserving file and command authority.
7. **`p0_prototype-a02-r5` passed syntax and 134/134 tests, but was not accepted.** The primary reviewer reported that criteria were met; a supplemental reviewer produced a concrete completed-step rewrite counterexample. The coordinator adjudicated the conflict in favor of the falsifying evidence because public inputs carried result metadata but not an immutable prior step body. Revision 5 stopped after both attempts.
8. **`p0_replan_binding_oracle-a01-r6` passed independent review.** Revision 6 added the implementable exact `step_body` binding, positive equality assertions, and a completed-body mutation negative while preserving all seven prior charged attempts and the bounded P0 scope.
9. **`p0_prototype_rebind-a01-r6` passed exact commands and independent review.** Syntax and 135/135 tests passed; closed completed entries, parent equality, exactly one matching proposal step, and body equality are checked before plan construction without fixture-ID special casing.
10. **`p0_integration-a01-r6` passed independent review.** The reviewer returned `meets_criteria` and advisory `accept`, confirming exact hashes, 135/135, all requirement mappings, disclosed failure/dissent/adjudication history, bounded recommendation scope, and 10/410 accounting before final.
11. **`p0_final-a01-r6` is this charged conclusion attempt.** It consumes the last 1 attempt / 20 minutes and leaves no remaining capacity. Its output still requires independent final review and an explicit HUMAN decision.

The two stop/lookbacks remain authoritative history: the oracle lookback required closed state/grammar delivery after revision 3, and the prototype lookback required an implementable completed-body binding after the sustained revision-5 dissent. Their lessons remain mission-local.

## Final cumulative accounting

| Attempt | Allowance minutes | Preserved outcome |
|---|---:|---|
| `p0_oracle-a01-r3` | 45 | failed review |
| `p0_oracle-a02-r3` | 45 | failed review; revision-3 stop |
| `p0_oracle_invariant_checklist-a01-r5` | 25 | accepted |
| `p0_oracle_finalize-a01-r5` | 45 | failed review |
| `p0_oracle_finalize-a02-r5` | 45 | accepted |
| `p0_prototype-a01-r5` | 60 | failed command verification |
| `p0_prototype-a02-r5` | 60 | command pass but sustained review blocker; revision-5 stop |
| `p0_replan_binding_oracle-a01-r6` | 25 | accepted |
| `p0_prototype_rebind-a01-r6` | 35 | accepted |
| `p0_integration-a01-r6` | 25 | accepted |
| `p0_final-a01-r6` | 20 | charged; final independent review pending |
| **Total** | **430** | **11 charged attempts** |

Cumulative ceiling: **11 attempts / 430 effort-minutes**. Charged after final dispatch: **11 / 430**. Remaining capacity: **0 attempts / 0 effort-minutes**. No failed or retired charge was reset or reused, and no retry is available.

## Decision rules for the HUMAN

- **Accept** only if the independent final reviewer finds no unresolved in-scope blocker and you approve the bounded P0 deterministic contract-to-plan feasibility conclusion for the exact frozen hashes above.
- **Defer** if you want to withhold the conclusion without finding the frozen P0 evidence false, or if the independent final review is unavailable or held.
- **Reject** if a bound hash/command/review/accounting claim is contradicted or an unresolved semantic or scope blocker is established.

### Required explicit choice

**HUMAN: choose exactly one — `accept`, `defer`, or `reject`.**

No choice, an ambiguous response, a hold, or a rejection leaves P0 unaccepted. None of the three choices authorizes production work, P2, BS1, real effects, or downstream execution; those require separate planning, review, and explicit authorization.
