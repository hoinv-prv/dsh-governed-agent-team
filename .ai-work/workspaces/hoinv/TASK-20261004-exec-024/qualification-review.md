# Independent qualification review — 2026-10-04

Reviewer: /root/qualification_review. Read-only; no files changed and no tests rerun. This report persists the reviewer’s actual returned assessment. Candidate: task-memory-checkpoint-manifest.json / attempt-09.

Verdict: demonstrated task-memory feasibility; changes required before full STEP-03 clearance. All candidate source, receipt/log hashes were independently verified. The 18 passing cases are credible narrow evidence using real Loader/current GAT/public WK with mocked transport; source aliases/helper mirrors/checkpoint limits are disclosed. Existing direct design is retained.

## Findings and required corrections

1. High — Tool publication authority/bounds stop at executor return. Prototype 104–118 has no finalizeContent; Host tools/index.ts:1649 awaits post-execute and :1781–1818 allows value/content/context replacements. Add total synchronous last-mile content authority/bounds checks preserving policy denials; explicitly settle nested/PTC value and additional-context channels. Reproduce delayed post-execute withdrawal and oversized replacement.
2. High — request guard precedes awaited llm.prepareCall (agent-loop/agent.ts:559/570); prototype close():138 never cancels Agent. Withdrawal during preparation could reach transport. This is a source-derived race, not reviewer-reproduced failure. Reproduce then qualify public Agent.cancel synchronous cutoff, retaining the deny guard and avoiding self-drain. No core prerequisite inferred.
3. Medium — prototype selected read :105/109–114 does not require returned item.id equal requested selected ID. Shared tools validates shape/syntax; pinned LocalProvider correctly returns requested item. Add equality and controlled malformed-result negative.
4. High for full STEP-03 — reviewer prototype only omits memory tool/denies three names; no required packet before admission or ambient-tool isolation. Settle a creation-time trusted resolver (registration after assignTask returns is too late), exact config/replacement/current checks, authenticated callbacks/audit/bounds, and narrow existing team_execution_submit exception without placing submission in a drain it triggers. Reviewer is explicit original proposal behavior 5/qualification bullet 4 and AIP requirement; second runner/final acceptance exceeds scope.
5. Medium — present Object.values(limits) checks do not enforce required fields/unknown fields/envelope caps. Settle closed required Loader config, ceilings/aggregate policy/topology and negative fixtures.
6. Material remaining gaps — submission publication/self-drain, late provisioning, same-ID Agent/generation/provider loss, distinct members, coexistence with direct entry, production build/types/public imports/old-entry regression. Bound retained Map growth; Cordis 4.0.2 versus 4.0.4 remains fixture-only evidence.

## Disposition

Design is compatible with HUMAN plugin-only/no-system-memory and DA family contracts; no WK→DSH lease translation or memory authority. Proceed autonomously with prospective design corrections before experimental code, race reproduction/fixes, item/config checks and a trusted reviewer seam qualified with fixture-owned approved records, actual executed receipts and authorized bytes. Live deployment credentials are not needed to build that API. Reviewer activation still requires the actual trusted caller/approved policy/ACL/receipt provenance; generic brief strings cannot supply it.

Reviewer availability is resolved. STEP-03 remains uncleared pending corrections, settled Basic/Detail/Integration/Source Map/public contracts and independent follow-up.
