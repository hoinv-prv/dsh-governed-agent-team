# Mission: legacy-agent-team-hotfix

## Objective
Hotfix the legacy Agent Team plugin (`packages/core`, `packages/tools`, `packages/web`) without touching the separately owned Conservative MVP mission under `packages/gat`.

HUMAN-confirmed behavior:
- Lead-only Team is valid: zero durable teammates required.
- Current Team plan approval remains mandatory.
- One Approve Plan action imports tasks first, then approves the exact resulting revision.
- Source is the latest successfully HUMAN-approved DSH Chat Plan.
- Deterministic extraction reads checklist/bullet/numbered items only within `## Tasks`.
- Existing Team tasks are preserved; only normalized missing tasks are added.
- Invalid/missing/rejected/incomplete plan input fails closed.

## Approved baseline
- Plan: `wbs.v9.json`
- Exact SHA-256: `79ea97523df2124db54b05eb82bdf6ef2de0244543fe71fb121d53dc87848b71`
- AIP: `.ai-work/aip/hoinv/exec/AIP-EXEC-011-legacy-agent-team-hotfix.md`
- AIP lint: 0 errors, 0 warnings.

## Order
1. `governance-bootstrap`
2. `lead-only-readiness` and `approved-plan-import` (parallel only when file/resource conflicts are absent)
3. `integration-verification`
4. `final-review`

## Boundaries
- Do not modify `packages/gat`.
- Do not modify `wbs-runs/multi-mission-web-ui` or its AIP/workspace controls.
- Do not parse arbitrary chat or use AI-based extraction.
- Do not remove the maximum teammate cap.
- Do not activate the live GUI/profile or restart its server.

## Limits
Maximum parallelism 2; 19 total attempts; 1170 effort minutes. Canonical external effects are confined to the dedicated legacy verification worktree and verifier scratch worktrees.

## Status
Revision 9 implementation, canonical integration, and independent final review meet criteria. HUMAN explicitly accepted final report and requested mission closure.
