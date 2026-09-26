# Integration verification

## attempt-integration-001 — failed

- WBS revision: 7
- Plan SHA-256: `80e69bac7c66e1bce2833aacae13f5f8417e6e5b4ce35a31d052b9de39ffc04f`
- Dedicated target: `/home/hoinv/deepseek-harness/.worktrees/verify-gat-install-0.1.5-rc.2`

Command 1 (required first command):

```text
node installer/index.mjs rollback --target /home/hoinv/deepseek-harness/.worktrees/verify-gat-install-0.1.5-rc.2
```

Observed result: exit code 1.

```text
gat-installer: payload hash mismatch for packages/core/src/index.ts
```

No later integration command was run. Inspection of `installer/index.mjs` shows `rollback` first calls source-manifest validation; the approved compatibility manifest describes the prior installed payload, while current mission source bytes have changed. Therefore rollback cannot reach target cleanup from the modified source tree. The dedicated target's `.gat/installation.json` still identifies the prior installation at DSH commit `c291e7961a515f6d7af9304e7fd1d257929aef26`.

Required recovery: a reviewed WBS revision must authorize deterministic reset/clean of only the dedicated verification worktree, then regeneration, installation, and canonical verification. No target cleanup, compatibility regeneration, install, or verifier run occurred in this attempt.

## attempt-integration-002 — failed

- WBS revision: 8
- Plan SHA-256: `f6267a214279d655284268d7a8cc6f571a8ac52cc53062097e63a11e7f6b9955`

All five approved commands ran once in order. Reset, clean, compatibility generation, and installation exited 0. Generation reported `host_files=9`, `payload_files=73`, patchset SHA-256 `e3bf5ab3fa6c6117e5e5ab080c0ff5b93caf1750f1b5027be3a5303c4ae4ab38`, and payload SHA-256 `4da561173080149f6c8e9737d050f35e0c27bae98be2464b4fdfeddd0a04bd90`. Installation reported 82 files.

Canonical verifier reached focused Vitest and exited 1: **151 passed, 4 failed** across 9 files. It did not proceed to later build/smoke stages.

Observed failures:
1. `projection-events.spec.ts`: noncontiguous-revision fixture also had invalid approval metadata, so schema validation preceded the expected continuity assertion.
2. `team.spec.ts`: synchronous `remoteGetMission` throw was evaluated before `expect(...).toThrow` could receive a function.
3. `team-action.client.spec.tsx`: pending approval text is rendered with adjacent content, while `getAllByText` expected an exact isolated node.
4. `team-action.client.spec.tsx`: approved status/revision text is split across DOM nodes, while `findByText` expected one exact node.

The output demonstrates test defects missed by static review; no production failure is yet established. A new reviewed revision is required for bounded test repairs, fresh review, and one final canonical verifier attempt. No verifier rerun occurred.

## attempt-integration-003 — failed

- WBS revision: 9
- Plan SHA-256: `382df5570471f84d28e95b0df66ac13102e4db00d6004552c1cdfe6988c66fff`

All five commands ran once and the first four exited 0. Final regenerated payload SHA-256: `0ca267afc393d58c167dd0d2c3c53ca03afbb17f4cf4269de5ccaa3cb0a5159f`; installation reported 82 files. Canonical focused Vitest improved to **154 passed, 1 failed** across 9 files, then verifier exited 1 before later build/smoke stages.

Remaining failure: `projection-events.spec.ts` still builds the noncontiguous revision case as a new projection containing only the revision-4 event. The projector correctly rejects that event at the initial-mission invariant before it can reach continuity. The fixture must replay a valid revision-1 create and revision-2 approval before revision 4. Production code is not implicated. No rerun occurred.

## attempt-integration-004 — failed

- WBS revision: 10
- Plan SHA-256: `e3c58c2ee53b3ed8bc26401f95a9fbb1047f036abaff7c15c00beb4d78c700b6`

All five commands ran once. Reset, clean, regeneration, and installation exited 0. Payload SHA-256: `b2c37709d45372d095ba1b4ffe0bff1d674cd71739428490748affcb0a52389e`; installation reported 82 files. Canonical focused Vitest passed **155/155 tests across 9 files**.

The verifier then reached the full DSH build and exited 1 on two TypeScript no-unused diagnostics:
- `packages/core/src/mission-board.ts(60,17)`: `caller` is declared but never read.
- `packages/core/src/projection.ts(11,3)`: imported type `TeamMissionId` is never used.

Later built-library and dashboard smoke stages did not run. Both defects are bounded compile hygiene in production source: rename the intentionally retained API parameter to `_caller` (or remove it with its call-site adjustment) and remove the unused type import. A reviewed plan revision is required before production edits or another verifier attempt.
