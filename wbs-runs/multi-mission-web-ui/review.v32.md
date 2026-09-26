# WBS revision 32 review

Status: independent PASS and official helper validation PASS; **execution-ready candidate, not yet approved**.

Plan SHA-256: `e035073bfb1c103602c9cfc350dbc7e087d3e4c2a4856cb968abaea5686f6fb0`  
Reviewer evidence: `team-message-5efe3265-df4b-45c4-b055-12c048c34ab3`.

## Why revision 32 replaces revision 31

Revision 31 was not valid/execution-safe as written. Independent audit found forbidden requirement fields, an invalid task kind, invalid narrative `effects`, an undefined requirement, effort overflow, mutable runtime controls pinned as sources, a contradictory matrix write prohibition, and an evidence-mismatched integration build path. Revision 32 corrects those defects and carries accepted history forward instead of reauthorizing completed tasks.

## Preserved state

- All 65 charged attempts remain charged.
- Revision-31 attempt 64 remains accepted with exact HUMAN acceptance.
- Attempt 65 remains interrupted and unverified; its provisional matrix JSON/Markdown/test/Workspace outputs and exact hashes are preserved without review or acceptance.
- Accepted threat/vector, governance, memory, policy and wrapper bytes remain hash-pinned and read-only.
- The mission remains paused with no active work.

## Candidate recovery plan

Seven serialized tasks remain:

1. revision-32 reconciliation — attempt 66;
2. contract-matrix recovery/test/review — attempt 67;
3. internal-only control-state implementation/review — attempts 68–70;
4. handlers/probes/reducers implementation/review — attempts 71–74;
5. runner assembly/review — attempts 75–76;
6. standalone integration/build/smoke/determinism review — attempts 77–78;
7. implementation freeze/handoff/lint/final HUMAN acceptance — attempts 79–80.

Arithmetic is exact: `65 + 15 = 80`. Declared remaining worst-case effort is `7,425` minutes within the unchanged `8,705`-minute ceiling. `max_parallel` is 1.

## Independent checks

The independent reviewer verified by inspection:

- exact `dsh-wbs/1` field-shape intent, exact `{id, acceptance}` requirements, valid task kinds and enum-only effects;
- complete requirement mapping with no undefined requirement;
- closed chain `revision32 → matrix recovery → control → handlers → runner → integration → freeze`;
- root/task input/read/write/command containment and the exact 13-command union;
- consistent literal build path `packages/gat/build.mjs` and freeze path `packages/gat/scripts/freeze.mjs`;
- stable source pins and runtime-only treatment of mutable ledger/AIP/Workspace files;
- explicit matrix-vs-control trust boundary and fresh verification/review for attempt65 outputs;
- exact HUMAN approval before attempt66 charge, then charge-before-reconciliation, plus final HUMAN acceptance;
- persistent prohibitions on DSH, network/package managers, accepted-baseline execution, activation and AIP closure.

Coordinator-local non-DSH checks additionally observed:

- JSON parse and constrained schema-shape checks pass;
- 7 tasks, 15 attempts and 7,425-minute task-attempt effort;
- input/root containment, requirement mapping, DAG and 13-command union pass;
- all 27 pinned source hashes match current bytes.

## Official helper validation and gate

The HUMAN granted one narrow read-only exception to the no-DSH boundary solely for the symlink-resolved official helper. The official helper then returned `valid: true`, revision 32 and SHA-256 `e035073bfb1c103602c9cfc350dbc7e087d3e4c2a4856cb968abaea5686f6fb0`; its derived order exactly matches the seven-task serialized chain. No other DSH file was inspected or modified.

Exact HUMAN approval of revision 32, SHA-256 `e035073bfb1c103602c9cfc350dbc7e087d3e4c2a4856cb968abaea5686f6fb0`, and its declared effects is required before attempt 66 may be charged. That approval does not accept attempt 65, final phase output, conformance, DSH access/integration, installation or activation.
