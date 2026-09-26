# Review candidate multi-mission-web-ui, revision 5

- Plan: `wbs.v5.json`
- Exact SHA-256: `00c5a7c85d9fab819a0de790b93c759a6545ed3e3cac35ddbc2e51259289c30c`
- Validation: WBS helper structural validation and workspace inspection passed.
- Order: discover → accepted core → AIWS governance recovery → final Web attempt → canonical integration → final review/human acceptance.

## Why revision 5 is required

Project `AGENTS.md` requires a Working AIP and task workspace for every non-trivial execution. The earlier WBS did not declare `.ai-work` write scope, so remaining review/integration work cannot proceed without an explicit revision. Separately, Terra child `ff029151-c067-449f-bc7a-b2d32ad6ff8b` failed before completing Web attempt 1 and left partial `packages/web` changes.

## Exact delta from revision 4

- Adds requirement/task `aiws-governance-recovery`.
- Authorizes only these AIWS writes:
  - `.ai-work/account_info.yaml` for allocator counter,
  - `.ai-work/aip/hoinv/exec/AIP-EXEC-004-multi-mission-web-ui.md`,
  - `.ai-work/workspaces/hoinv/TASK-20260913-multi-mission-web-ui`.
- Authorizes exact AIWS lookup, operating-memory, allocation, lint, start/status, final scoped lint, and close commands.
- Explicitly forbids changes to AIWS Truth, Wiki, procedural guidance, and tooling.
- Adds AIWS recovery as a hard dependency of the final Web attempt; records earlier core and partial Web work as pre-applied rather than rewriting history.
- Preserves accepted core evidence because its task contract and source hashes are unchanged.
- Charges failed Web attempt 1; Web attempt 2 is the final available Web attempt.
- Total task attempts: 9 → 10. Effort ceiling: 620 → 650 minutes.
- Existing external installer/verifier commands and live-profile non-goals are unchanged.

Approval authorizes AIP recovery, one final bounded Web completion/review attempt, then the already-declared canonical integration/final gates. It does not activate GAT in the live Web profile.
