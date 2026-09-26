# Findings

## STEP-00 — Corrected scope confirmation

The HUMAN explicitly confirmed that AIP-EXEC-012 was wrong to remove the Agent Team Enable/Disable button. Required behavior: restore an Enable/Disable control in the Agent Team UI, scoped to the current session only; profile-level activation must remain unchanged.

Evidence: current-session HUMAN confirmation on 2026-09-26.

STEP-00 done; proceed to STEP-01.

## STEP-01 — Activation seam trace

- Current `packages/web/src/client/TeamAction.tsx` has no Enable control or injected activation action.
- Current `packages/web/src/client/mount.ts` exposes only view/mission/task/navigation actions; no `remote.agentTeams.enable` wiring.
- Current `packages/core/src/types.ts` has no `TeamView.enabled` or `TeamEnableResult`; current `TeamService` has no `remoteEnable`.
- The supplied DSH checkout contains a reference Enable-only flow: `TeamService.enable`/`remoteEnable`, `TeamView.enabled`, and a tools initializer that provisions teammates. It does not define teardown/Disable.
- HUMAN resolved OP-...-01 as Enable-only opt-in; therefore implementation must port/restore that session activation contract, not invent teardown.

## STEP-02 — Implementation

Implemented the Enable-only session flow across core, tools, and Web UI:
- `TeamView.enabled` and `TeamEnableResult` added to the public model.
- `TeamService.registerInitializer`, `enable`, and Remote `enable` added; existing durable teammates are idempotent.
- Team tools register a concurrency-deduplicated built-in initializer that provisions advisor/dev teammates.
- Web mount injects `remote.agentTeams.enable`; UI shows an accessible Enable button while off and hides mission/member dashboard until enabled.
- Focused UI test added for the off-session Enable path.

Verification:
- `git diff --check` passed.
- Direct ad-hoc TypeScript invocation was not a valid repository build: the source snapshot lacks installed workspace module resolution and tsconfig references, producing pre-existing dependency/configuration errors.
- Canonical installer verification reached the DSH build/test phase but failed in the supplied checkout with a large generated-file/output mismatch; full stderr is recorded by the command harness.
- Final `lint_aip.py` and scoped `lint_all.py` both pass with 0 errors and 0 warnings.
