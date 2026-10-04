# Prerequisite conformance — AIP-EXEC-023

Qualified source/artifact scope: isolated DSH baseline `c291e7961a515f6d7af9304e7fd1d257929aef26`, worktree `/home/hoinv/work/dsh-binding-prerequisites`. Independent substantive review: PASS. Parent production binder composition, changed-host release compatibility and deployment remain separate.

| Contract | Actual observation | Evidence | Result |
|---|---|---|---|
| Reserved admission/recovery | Quarantine, exact generation, durable activation/tombstone, idempotency conflict, malformed recovery, shared disposal and retained legacy behavior | host-prerequisites.md; host review qualification/cold-resume logs; final 270-test suite | PASS |
| Refresh before rendering | Awaited owner-scoped refresh before render/retry, bounded replacement and logged history; synchronous final guard denies late revocation | host-prerequisites.md; sdk-qualification.md; composition fixture | PASS |
| HUMAN provenance | Signed authenticated HTTP, one-use exact action/request/Agent receipts; model/public RPC cannot mint approval | authority-ingress-final.log; authority-prerequisites.md | PASS |
| Exact mission/task scope | Draft creation, canonical mission association, current owner/status, exact revision/current plan; reassignment/close/revoke and legacy provenance deny | authority/projection suites; authorization-matrix.md | PASS |
| Model/activation races | Actual HTTP revocation after async listeners or during held activation flush; zero provider requests | prerequisite-composition.spec.ts; gat-behavior-final.log | PASS |
| Publication/withdrawal/recovery | Pending/false authority flush denies; unrelated mailbox publication preserves valid lease; withdrawal closes gates and retains guards through physical drainage | authority/team suites; authority-prerequisites.md | PASS |
| Immutable nested capabilities | Detached aliases, descendant union, live exact parent, current policy rechecks, PTC and configured delegator names | capability-prerequisites.md; independent registry/PTC checks | PASS |
| Actual GAT policy matrix | Real nested delegation denied before effects; HTTP current-plan approval admits exact scope; all mode/enablement/mission/plan tuples reached | authorization-matrix.md: 60 cases, 19 allowed bodies, 41 denied, zero provider requests | PASS |
| Supported builds/public exports | Host/client compiler and bundle; plain Node public imports with actual reserved/refresh/draft denial observations | host-qualified-*.log; client-qualified-*.log; public-built-qualified.log | PASS |
| SDK/session checks | Built CLI TypeScript replay: 10 checks; four Python comparisons; existing v2/Python predecessor bytes retained; current-v3 refresh reviewed separately | sdk-qualification.md; sdk-qualified-hash-comparison.json | PASS within stated artifact scope |
| Documentation | All 34 documentation gates pass, including comments, freshness, pairing, site and type checks | doc-sync-accepted.log | PASS |
| Source/design/review | Formal DD §7 and owning DSH references match final behavior; 57 GAT source/test pairs match; R1–R8 resolved; independently repeated 270-test run passes | source-design-consistency.md; independent-review.md; final-mapping.md | PASS with retained process limitations |
| Governance | Scoped strict lint: zero errors/warnings; whole-tree: 37 baseline warnings, zero errors | governance-qualified.log; governance-whole-tree-accepted.log | Task PASS; whole-tree strict exit 1 reported |

Log filenames resolve under verification/ unless explicitly named as workspace reports. Earlier failed logs remain investigation history. Counts overlap and are not additive. This evidence does not qualify parent production attachment/binder/profile/browser integration or deployment.

Two earlier corrective design-before-code chronology gaps, corrected API annotation accidents, and the outside-workstream original AGENTS.md difference remain disclosed. Final mapping/patch receipts package the qualified source without changing its behavior.
