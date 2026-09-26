# Governance contracts review — changes required

Fresh STEP-08 and 4/4 command evidence were valid, but independent review found material contract gaps:

1. AgentDesk key omitted ProjectScope.
2. execution identity omitted principal and did not deeply own returned data.
3. readiness reclassified caller task state and used invented readiness vocabulary instead of consuming package-owned oracle evidence.
4. Team plan approval omitted approved phase, numeric revision rules, and snapshot hash validation.
5. mapped Mission did not validate native Mission identity/revision or normalize missing/stale approval to pinned Mission denial semantics.
6. binding evidence hashes/deep mutation resistance were incomplete; tests omitted the corresponding negative cases.

Attempt 1 fails review. A final task attempt is available with a revised hypothesis; the 4/4 result is preserved but not acceptance.
