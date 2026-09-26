# Council verifier plan — run 002

Parent-orchestrator verification is read-only; request authorizes no commands.

For each admitted finding:

1. Re-hash `design-v1` and its snapshot; mismatch stops closure.
2. Confirm the cited locator and exact evidence excerpt in the pinned snapshot.
3. For authority claims, compare against pinned repo rules, AIWS architecture and GAT proposal locators.
4. For repeat-failure claims, compare against the pinned failure-model artifact and classify unsupported historical claims `not_verifiable` rather than infer.
5. Mark each finding `confirmed`, `refuted`, `inconclusive` or `not_verifiable` in a separate verifier record with unchanged raw read evidence.
6. Do not run commands, mutate reviewed artifacts or broaden read roots.
7. Evaluate conflict gates before releasing/using the adjudicator reservation.
8. Re-hash all canonical artifacts before Chairman synthesis and closure.
