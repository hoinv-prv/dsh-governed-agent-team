# Review candidate multi-mission-web-ui, revision 17

- Exact plan SHA-256: `c7a802e9ba92c1220d378605ed301ffd553f9b48f196d2f63656f9bb2c2ec96b`
- Base: approved revision 16, SHA-256 `a9a8a95d9ccc22662b33d331edf7da37175cd49f18a9eeda2fe96675f7ba1247`
- Canonical validate/order/hash: PASS.

## Trigger

Revision-16 threat attempt 1 authored candidate files while the fixed Workspace ASC still pointed to historical STEP-03. A durable independent reviewer correctly stopped `BLOCKED_BY_CONTROL` before opening them. The candidate bytes and a separate pre-ASC advisory PASS are preserved but cannot satisfy task acceptance. Attempt charge 20 remains consumed; no package work started.

## Exact delta

- Add exact AIWS transition commands using `python3 .ai-work/tooling/run_aip.py step AIP-EXEC-004 --step STEP-NN` at the start of the responsible task:
  - threat model → STEP-06;
  - package scaffold → STEP-07;
  - governance contracts → STEP-08;
  - policy selector → STEP-09;
  - conformance runner → STEP-10;
  - standalone integration/freeze → STEP-11.
- Declare AIP/tooling/Workspace reads, Workspace ASC/pointer writes, `aiws-aip-runtime` resource, and execute effects for those tasks.
- Require independent reviewers, including same-step `partitioned-memory`, `wrapper-admission`, and `implementation-freeze`, to confirm the exact ASC before opening step inputs.
- Serialize `partitioned-memory` after `governance-contracts`, and `policy-selector` after `partitioned-memory`, so STEP-09 cannot replace ASC while STEP-08 implementation/review remains active; later dependencies serialize STEP-10–11.
- Pin the retained corrected threat/vector drafts as revision-17 sources. Their pre-ASC advisory hashes are not acceptance.
- Increase `governance-replan.max_attempts` 2→3 for one exact revision-17 selection/lint/status reconciliation attempt because both prior governance attempts are already charged; no product behavior, test/build command, conformance boundary, DSH/network/external effect, HUMAN gate, or final acceptance changes.

## Cumulative state

- Current charged attempts: 20 (17 legacy + governance attempts 1/2 + invalid-ASC threat attempt 1).
- Remaining maximum: 18 (one revision reconciliation retry + threat retry 1 + remaining product/final allocations).
- Cumulative caps: 38 attempts and 4,445 minutes (1,550 charged/planned effort + at most 2,895 remaining).

Exact HUMAN approval is required before selecting revision 17 or moving the pointer. The first permitted action is the STEP-06 transition, then a fresh independent Security review and HUMAN acceptance of the exact candidate hashes. Coding remains blocked.
