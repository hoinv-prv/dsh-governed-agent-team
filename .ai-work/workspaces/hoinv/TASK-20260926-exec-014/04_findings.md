# Findings

## STEP-00 — Scope confirmation

The HUMAN confirmed creation of one reference under `docs/` covering GAT architecture, implemented functions, session Enable lifecycle, exact `team_members.yaml` member resolution, governance, current implementation status, and limitations. The reference must distinguish implemented behavior from proposals and deferred work.

Evidence: current-session HUMAN confirmation on 2026-09-26.

## STEP-01 — Verified source and feature map

### Current runtime authority

The latest implemented session-enable and workspace roster behavior is present in the installed DSH checkout under `/home/hoinv/deepseek-harness/packages/experimental/gat-*`. The standalone workspace packages remain the installer source/distribution and contain other ongoing changes, but their documentation is not yet fully synchronized with the installed runtime. The consolidated reference must state this explicitly.

### Architecture evidence

- `packages/core/README.md` and installed `gat-core/src/types.ts` define one implicit Team per top-level Session, durable roster/messages/tasks/missions/work state, and `TeamView.enabled`.
- Installed `gat-core/src/index.ts` exposes `agentTeams/view` and idempotent, Lead-only `agentTeams/enable` backed by a registered initializer.
- Installed `gat-tools/src/index.ts` owns simple-mode activation, member route preflight, provisioning, scoped tool installation, and execution readiness.
- Installed `gat-web/README.md`, `TeamAction.tsx`, and `mount.ts` own the conversation-header panel, enable action, snapshot refresh, current mission/member presentation, and teammate navigation.
- `packages/profile/README.md` and `packages/web-profile/README.md` describe opt-in ordered composition.
- Root `README.md` describes installer, verification, activation, profile links, and rollback.

### `team_members.yaml` contract

Evidence: installed `gat-tools/src/team-config.ts`, `gat-tools/src/index.ts`, its tests, and workspace `team_members.yaml`.

- Resolution path is `join(lead.session.header.cwd, "team_members.yaml")`: the file comes from the current Lead Session workspace, not a hard-coded repository path.
- Loader accepts a regular non-symlink file only, bounded by `teamMembersMaxBytes` before and after UTF-8 read (default 65,536 bytes).
- Document keys are exactly `version` and `members`; `version` must equal `1`; members must be a non-empty array and cannot exceed `maxExecutionMembers` (default 4).
- Member keys are exactly `name`, `description`, `prompt`, `context`, `provider`, `model`, and optional `reasoning_effort`; unknown keys reject the workspace config.
- `name` is unique lower-kebab-case, max 64 chars. `description` max 200; `prompt` max 16,384; provider/model max 200; reasoning effort max 80. All required text is trimmed and non-empty. `context` defaults to `fresh` and accepts only `fresh|fork`.
- Missing workspace, missing file, invalid YAML/schema, symlink, oversize file, or other load error produces diagnostics and falls back to the bounded built-in roster rather than failing activation.
- Built-in roster: advisor and senior-dev on `gpt-5.6-sol`, dev on `gpt-5.6-terra`, junior-dev on `gpt-5.6-luna`; all use the Lead provider and are truncated to the configured maximum.
- All member provider/model/reasoning routes are preflighted before provisioning begins. Provisioning then occurs sequentially and is best-effort after that preflight; a later runtime/provider failure can leave a durable partial roster.
- Enable requests are deduplicated per Session. A Session with existing teammates returns source `existing` and does not reread or replace `team_members.yaml`; a new Session is required to load edits.
- Fresh members use the configured `freshProvider` continuation provider; fork members use `forkProvider`. The YAML `provider` and `model` select the child LLM route, not the continuation provider.

### Feature classification

Implemented: session opt-in, roster/provisioning/recovery, durable mailbox, Team tools, shared task board with CAS/dependencies/write-scope warnings, durable work status, missions, Web inspection/navigation, profile composition, installer/rollback.

Implemented with current simple-mode semantics: one-way Enable, HUMAN-authored mission authorization, no separate Team-plan approval in the panel, minimum-member and capability-envelope execution checks.

Proposal/deferred: MCP reference memory architecture, semantic/vector retrieval, cross-process teams, worktree isolation/locks, automatic retries/watchdogs, destructive Disable/roster replacement, mailbox timeline UI, production/stability guarantees.

## STEP-02 — Document authored and independently reviewed

Created `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` with architecture, package map, durable model, Enable lifecycle, exact YAML contract, capabilities, Web behavior, governance, installation, limitations, evidence map, and maintenance checklist.

Independent source review found and the document now records two important corrections:

1. Simple mode skips legacy Team-plan approval validation, but current code does not verify mission authorship or require a mission for readiness. “HUMAN-authored mission is authorization” is intended package policy, not an enforced invariant.
2. Current installed Web source has type/injection drift: `TeamAction.tsx` retains retired approval/import types/actions while `mount.ts` does not inject those actions. The simplified render path does not use them, but the source snapshot is not type-consistent.

## STEP-03 — Verification

- Independent source review completed; both material findings were incorporated into the reference.
- Primary workspace and installed-runtime source paths referenced by the document exist.
- `git diff --check` passed for the document and task artifacts.
- AIWS scoped task lint passed with 0 errors and 0 warnings.
- Wiki-registration candidate CAP-001 was deferred to backlog BL-014-CAP-001 for separate HUMAN curation review; no Wiki or Truth was modified.
- No unresolved open point remains.
