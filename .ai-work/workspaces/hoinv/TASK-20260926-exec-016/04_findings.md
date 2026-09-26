# Findings

## Findings List
- No remaining material discrepancies.

## Confirmed Findings
- HC-01 PASS — §6.6 matches the loader-wide catch in `team-config.ts:124-147`, while correctly excluding later route preflight from fallback.
- HC-02 PASS — §§6.5/6.9 match the configurable 65,536-byte default and both entry-size/UTF-8-byte checks in `team-config.ts:124-139` and `index.ts:34-47,657-680`; Durable MiniMVP states no manifest byte constant.
- HC-03 PASS — §§6.7/7.2 separate manifest authorization, GAT/DSH effective route instantiation, continuation provider, and Durable immutable profile verification consistently with Durable MiniMVP and `index.ts:83-116,704-733`.
- HC-04 PASS — §7.4 distinguishes authority precedence from literal prompt order and preserves Durable's SOUL-after-host-system-commands/before-member-task-context rule (`DURABLE_AGENTS_MINIMVP.md:62,88-90`).
- HC-05 PASS — §§7.4/7.5 require SOUL plus bounded index before every task and selective item loading, matching `DURABLE_AGENTS_MINIMVP.md:62-65,88-104`.
- HC-06 PASS — §§7.5/7.6 accurately mark canonical snapshots as proposed and explain why current per-operation manifest reload (`DURABLE_AGENTS_MINIMVP.md:33,107`) makes an unverified digest insufficient.
- HC-07 PASS — §7.5 requires profile revalidation before resumed-task or durable-context admission and §7.8 correctly marks this unimplemented in current GAT; current cold resume only reinstalls GAT scope (`tool-team.spec.ts:1075-1094`).
- HC-08 PASS — §7.3 matches Durable's explicit-every-workspace, same-immutable-profile condition for global sharing and denies implicit copy or Team/runtime sharing (`DURABLE_AGENTS_MINIMVP.md:35-57,67`).
- HC-09 PASS — §§7.2/7.3/7.6 distinguish logical member ownership from shared-filesystem isolation/locking, matching Durable `working/` semantics and GAT's shared-checkout policy (`index.ts:49-56`).

## Inferred Findings
- None.

## To-Verify Findings
- None. Independent bounded verification also found no remaining material discrepancies across all nine concerns.

## Final Capture Sweep
- Reviewed target/spec/source comparisons, checklist, findings, and final output.
- New candidates added during sweep: 0.
- Capture inbox total: 2 retrieval-gap candidates; relation candidates pending: 0.
- Existing retrieval-gap candidates will be deferred to the governed capture backlog at close.

## Notes
- STEP-00 task understanding: recheck only target §§6.6, 6.9, and 7 against the durable-agent MiniMVP and current GAT team-config/tool sources. Check exactly these prior concerns: fallback scope, byte limit, route authority, SOUL ordering, per-task loading, manifest snapshots, restart admission, conditional sharing, and filesystem ownership. Final response must contain remaining material discrepancies only, otherwise `None.`
- Confirmation evidence: the HUMAN's direct request explicitly fixes scope, authorities, concerns, and output contract; no clarification is needed.
