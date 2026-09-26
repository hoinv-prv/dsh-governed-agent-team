# Review candidate multi-mission-web-ui, revision 19

- Exact SHA-256: `95d9cfac0c4b08539490769af7c8d7653d3e2855f38a40d7069feda9824aac0b`
- Base: approved revision 18, SHA-256 `728c1910d910ad8ffc94e38352c437513e987d69e95f77449dbc4cce82cc0b88`
- Canonical validate/order/hash: PASS.

## Trigger and bounded delta

Governance attempt 2 closed five of six review findings but incorrectly invented native Mission plan/hash fields. Both task attempts are charged. Revision 19:

- preserves all 28 attempts and accepted threat/scaffold evidence;
- permits one governance-replan selection attempt and one final governance-contract attempt;
- changes only conditional Mission normalization: native Mission id/current numeric revision/status plus adapter-computed snapshot hash; native approval approvedRevision plus adapter-computed approval snapshot hash; exact revision equality and acceptable status; mapped identities/revision retained; absent/stale/mismatch → `NATIVE_MISSION_APPROVAL_STALE`; no DSH admission claim;
- increases governance-replan max 4→5 and governance-contracts max 2→3;
- changes cumulative caps to 42 attempts and 4,895 minutes (2,540 charged/planned + at most 2,355 remaining);
- preserves every command, STEP transition, dependency, other product contract, HUMAN gate, and no-DSH/network/dependency/accepted-conformance boundary.

Exact HUMAN approval is required before selection or code correction.
