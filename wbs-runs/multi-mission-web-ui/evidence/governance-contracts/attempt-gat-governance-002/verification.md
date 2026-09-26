# Governance contracts verification — attempt-gat-governance-002

Plan revision 18; cumulative charge 28; STEP-08 ASC fresh.

`node --test packages/gat/tests/governance.test.mjs`: exit 0; 5 tests, 5 pass, 0 fail.

Corrected coverage:

- immutable hash-bound ProjectScope and `(tenant, principal, project_scope, agent)` Desk key;
- deep-owned hash-bound execution identity containing tenant, principal, ProjectScope, Task, AIP, Workspace; stale every-field and malformed denial;
- consumption of package-owned `not_ready|lite_ready|execution_ready` oracle evidence/hash/revision/applicability without GAT classification;
- Team plan numeric exact revision, approved phase, plan hash and approval snapshot hash;
- conditional native Mission identity/revision/plan/approval binding and pinned missing/stale denial;
- mutation-resistance tests for caller inputs and nested returned evidence.

Hashes: source `805b393e0bc0262c98a11bc9fe4f258f7ef70cb198e55e5e6e943c82ef1b3bc2`; declarations `dad968839e5e864e6d2921aa0bd0ba75090aa805b3894bf8a8823459faec83ed`; tests `0eaf3df5121c8fc440139f5fb536e167e7d45172aa69255de56ca38c3962b12c`.

No DSH/dependency/network/conformance/activation effect.
