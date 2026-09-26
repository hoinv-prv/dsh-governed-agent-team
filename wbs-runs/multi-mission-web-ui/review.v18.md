# Review candidate multi-mission-web-ui, revision 18

- Exact plan SHA-256: `728c1910d910ad8ffc94e38352c437513e987d69e95f77449dbc4cce82cc0b88`
- Base: approved revision 17, SHA-256 `c7a802e9ba92c1220d378605ed301ffd553f9b48f196d2f63656f9bb2c2ec96b`
- Canonical validate/order/hash: PASS.

## Trigger

Revision-17 successfully reconciled AIP control and produced a fresh STEP-06 ASC. Threat attempt 2 then received a valid durable Security review and four material REVISE findings: one remaining invented `ALLOW_EXPLICIT`, ambiguous expiry transition state, combined classification allow/deny semantics, and combined degradation/unavailability reason semantics. Both threat attempts are exhausted. No package or DSH work started.

The reviewer also could not execute hash/parse verification because revision 17 granted neither command. It relied on immutable source hashes and preserved earlier parse evidence.

## Exact delta

- Increase `governance-replan.max_attempts` 3→4 for one revision-18 selection/lint/status reconciliation attempt.
- Increase `threat-model-gate.max_attempts` 2→3 for one bounded correction/review/HUMAN-gate attempt.
- Add exact threat verification commands:
  - `sha256sum docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md docs/conformance/gat-conservative-mvp-v1.json`;
  - `node wbs-runs/multi-mission-web-ui/tooling/verify-gat-vector-shape.mjs`.
- Pin the zero-dependency Node verifier (SHA-256 `35c05e89d008dcf3845bd1c2cf136aa2d9b7c2eda10248abefdec317fa854f8a`) as a plan source; it fails nonzero unless the exact 43 pinned IDs, exact eight marked extensions, 51 total/unique IDs, required null-reason rows, and zero `ALLOW_EXPLICIT` all hold.
- Encode the exact four permitted candidate corrections in the threat deliverable, acceptance, and stop conditions; any unrelated candidate edit stops execution.
- Preserve all revision-17 step transitions, serialization, product commands, dependencies, acceptance gates, and prohibitions unchanged.

## Cumulative state

- Current charged attempts: 22.
- Remaining maximum: 18 (one revision reconciliation + one threat retry + 16 product/final allocations).
- Cumulative caps: 40 attempts and 4,670 minutes (1,775 charged/planned effort + at most 2,895 remaining).

Exact HUMAN approval is required before selecting revision 18 or correcting the candidates. The bounded correction must resolve only the four review findings, execute the declared hash/shape checks, receive independent exact-byte Security PASS, and obtain separate HUMAN artifact-hash acceptance before any package write.
