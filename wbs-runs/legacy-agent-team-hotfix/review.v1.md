# WBS review — legacy-agent-team-hotfix revision 1

- Exact plan: `wbs-runs/legacy-agent-team-hotfix/wbs.v1.json`
- SHA-256: `95abfac1e7d78df05daee7bd5cb825d679579fd160416cbdea23fe607c3a2f93`
- WBS validation/order: PASS.
- AIP-EXEC-011 lint: 0 errors, 0 warnings.

## Scope and acceptance

### Lead-only readiness
Current legacy config defaults to two durable teammates, which produces Lead + 2 = 3 people. The hotfix defaults the minimum to zero, allowing Lead-only execution. Exact current plan approval, other readiness/authorization checks, and the configurable maximum teammate cap remain enforced. Focused tools tests and fresh independent review are mandatory.

### Approved Chat Plan import
DSH plan-mode stores the complete plan as markdown in the `exit_plan_mode` call; its projection exposes no structured tasks. The HUMAN selected a deterministic contract:
- latest successful HUMAN-approved call/result pair only;
- items only within `## Tasks`;
- checklist, bullet, or numbered items;
- preserve existing Team tasks and add normalized missing tasks only;
- approve the exact post-import revision in the same action;
- fail closed on missing, malformed, rejected, incomplete, empty, or stale input;
- never parse arbitrary chat.

Core/Web types, service, Remote wiring, localization, component/browser tests, and fresh independent review are required.

## Verification and effects
Canonical reset/clean/regenerate/install/verify is confined to `/home/hoinv/deepseek-harness/.worktrees/verify-gat-install-0.1.5-rc.2` and verifier scratch worktrees. It must pass focused core/tools/Web tests, full build, built-library smoke, and dashboard smoke. No live-profile activation or server restart is authorized.

## Ownership isolation
A different coordinator owns approved `multi-mission-web-ui` revision 32 and writes `packages/gat` plus its own controls. This new mission uses a distinct mission root, AIP, task workspace, resource keys, and legacy package paths. Any observed writer overlap stops dispatch.

During conflict discovery, the current session found that the historical untracked `multi-mission-web-ui/wbs.v12.json` bytes no longer matched their recorded hash; this mission does not attempt to reconstruct or mutate that other coordinator's history. The other coordinator/HUMAN must reconcile it separately.

## Limits and decision
Five tasks, 8 maximum attempts, 600 effort minutes, max parallelism 2. Approval authorizes only these exact bytes/effects; it does not pre-accept implementation, runtime verification, or final outcome.
