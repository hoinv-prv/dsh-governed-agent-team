# Governed Agent Team V1

English | [中文](2026-09-12-governed-agent-team-v1-design.zh.md)

## Status

Proposed design for HUMAN review. This document authorizes no runtime activation or external effect by itself.

## Objective

Build an opt-in coding team on DeepSeek Harness that keeps the existing implicit-root Agent Teams runtime and adds a small governed execution layer. One Lead creates a dependency-aware WBS, the HUMAN approves its exact revision before write-capable tools can run, two to four teammates execute disjoint work, and the Web UI shows durable progress, explicit blockers, inferred stalls, and reviewable files.

The V1 target is one Team Session, one DeepSeek Harness process, and one shared repository checkout.

## Evidence and lessons applied

This proposal incorporates the findings in these local review artifacts:

- `/home/hoinv/work/agent_team_hub/inbox/vuhoi_team_leader/C356-c349-delay-root-cause-advisor-R1__done_codex_advisor.md`
- `/home/hoinv/work/agent_team_hub/teams/vuhoi-team/proposals/continuous-initiative-controller/implementation/cards/C356-c349-delay-root-cause-advisor-R1/leader-terminal-review-R1.md`

The accepted analysis separates a small technical trigger from the dominant process failure: serial recovery envelopes, brittle evidence packaging, capability mismatches discovered after dispatch, and repeated loss of usable substantive work. V1 therefore follows these rules:

1. Preflight the complete Team envelope before execution: provider availability, tool availability, WBS validity, write-scope overlap, task limits, and approval revision.
2. Keep one canonical durable Team projection. UI, model tools, recovery, and review read the same Session events instead of independently composed status documents.
3. Separate work facts from inferences. `blocked` is an explicit member report with a reason; `suspected_stall` is a derived warning and never changes durable work state.
4. Preserve useful work when packaging or reporting fails. A report defect keeps the task in `review_required` or `blocked`; it does not create a new teammate or discard the prior attempt automatically.
5. Bound recovery. V1 does not implement autonomous retries, recurring watchdog agents, cross-process recovery, or one-new-agent-per-defect behavior.
6. Keep safety controls on the critical path: exact approval revision, dependency readiness, disjoint write scopes, fail-closed pre-execution checks, durable evidence, and HUMAN acceptance. Do not add standalone-read choreography, duplicate handoffs, arbitrary prose byte ceilings, or mandatory unverified skills.

## Existing foundation

V1 reuses these existing packages:

- `@deepseek-ai/dsh-experimental-agent-team` for the Lead identity, durable roster, mailbox, task DAG, Session replay, and Remote service.
- `@deepseek-ai/dsh-experimental-tool-agent-team` for scoped model tools.
- `@deepseek-ai/dsh-experimental-client-ui-agent-team` for roster, task board, and teammate navigation.
- `@deepseek-ai/dsh-api-workspace-files`, document preview, sidebar files, and `present` for reviewable workspace output.
- `tools/pre-execute` for the approval-dependent write barrier.

V1 extends the current experimental packages rather than creating a second orchestrator or external database.

## Public behavior

### Team lifecycle

A Team starts in `draft`. The Lead may inspect the repository, create and edit tasks, add dependencies and advisory write scopes, and run preflight. The Lead may not spawn teammates or invoke write-capable tools.

The HUMAN reviews the complete WBS in the Web panel and approves its current `planRevision`. The Lead may then spawn two to four teammates. Write-capable tools open only when the approved revision remains current and at least two teammates have reached durable `active` phase.

A structural WBS mutation after approval makes the approval stale and closes the write barrier. Structural mutations are task creation, deletion, text edits, dependency changes, and write-scope changes. Claim, release, assignment, reopen, progress reports, review requests, and completion do not invalidate approval.

Approval is a Web-only Remote operation. No model-facing tool can approve a plan.

### Canonical plan state

The Team projection derives `planRevision` by counting committed structural task mutations, starting at zero. Approval adds one root-Session event:

```ts
interface TeamPlanApprovalSnapshot {
  readonly approvedRevision: number
}
```

Approval rejects an empty WBS and succeeds only when `approvedRevision` equals the derived current revision. The projected phase is `approved` only while the latest approved revision equals the current revision; otherwise it is `draft`. This avoids a second plan write after each task mutation, so a committed task event and the visible plan phase cannot diverge. The Team projection is the sole authority for model tools and Web UI.

### Member work state

Each member may report one durable work state:

```ts
import type { SessionId } from '@deepseek-ai/dsh-session'
import type { TeamTaskId } from '@deepseek-ai/dsh-experimental-agent-team'

type TeamWorkState = 'working' | 'blocked' | 'review_required' | 'done'

interface TeamWorkSnapshot {
  readonly memberId: SessionId
  readonly state: TeamWorkState
  readonly summary: string
  readonly reason?: string
  readonly taskId?: TeamTaskId
  readonly files: string[]
}
```

The event envelope time becomes the derived `updatedAt` in the view; the snapshot does not duplicate it. `blocked` requires a non-empty reason. `review_required` requires at least one workspace-relative file. `working` and `done` reject a blocker reason. A referenced task must exist and be owned by the reporting member.

The model tool is `report_team_status`. Its output is the complete committed member-work view, not a prose acknowledgement.

### Runtime and stall display

The roster retains its current runtime status: `running`, `idle`, `inactive`, `provisioning`, or `failed`. Work state is displayed separately.

The Web client derives `suspected_stall` when all conditions hold:

- runtime status is `running`;
- durable work state is `working`;
- elapsed time since `updatedAt` exceeds configurable `stallWarningMs`.

The default is 180,000 milliseconds. The warning is presentation-only. It never emits a durable block, interrupts an agent, retries work, changes a task, or claims root cause.

### Write barrier

A scoped `tools/pre-execute` listener denies every tool not explicitly allowed while the Team is not execution-ready. Execution readiness requires a current approval and at least two active teammates. The restricted-mode allowlist is deployment configuration and defaults to the exact read/coordination set used by the Agent Teams Web profile:

- repository read/search tools;
- `list_agents`, `wait_agent`, `send_message`;
- `team_task_create`, `team_task_list`, `team_task_get`, and WBS-only `team_task_update` actions;
- `report_team_status` only for `blocked` or `review_required` reporting;
- HUMAN interaction tools that do not mutate the workspace.

`spawn_teammate` is denied before approval, allowed after approval until four teammates exist, and denied at that limit. Shell, file edit/write, patch, code generation, formatting, and composite execution are denied unless explicitly allowlisted. The listener runs at dispatch, including nested composite-tool dispatches, so hiding tools from the prompt is not the enforcement mechanism.

When a structural mutation invalidates approval during execution, subsequent write-capable calls fail closed. V1 does not terminate a tool body that already passed the check.

## Components and changes

### Agent Teams domain

Extend `packages/experimental/agent-team` with:

- durable plan and member-work event declarations;
- projection folding and replay;
- compare-and-set approval and structural invalidation;
- validated member status reporting;
- Team views that expose plan and work state;
- `Remote('approvePlan')` and a Remote view that includes the current plan;
- activity notifications after successful durable commits only.

Task-board mutation remains the owner of structural change classification. The Team projection increments its derived plan revision while folding each committed structural task event, preventing a second-write consistency gap.

### Model tools and enforcement

Extend `packages/experimental/tool-agent-team` with:

- `report_team_status`;
- plan phase and approval guidance in the Team system-prompt section;
- a scoped `tools/pre-execute` write barrier;
- `spawn_teammate` rejection before approval;
- preflight diagnostics returned by an existing list/read path rather than a second status store.

All tool results keep explicit fixed JSON schemas. Output schemas include every stable field returned by execution, avoiding the exact-dictionary mismatch identified in the reviewed incident.

### Web UI

Extend `packages/experimental/client-ui-agent-team` with:

- plan revision, approval phase, and an approve action;
- separate runtime and work-state columns;
- blocker reason and last durable activity;
- presentation-only stall warning;
- file links for `review_required`, opened through the existing file resource/sidebar integration;
- bounded refresh while the panel is open, plus immediate refresh after mutations.

V1 uses bounded polling at a configurable interval instead of adding a new streaming Remote protocol. The default is five seconds. Polling stops when the panel closes or the component unmounts. This is deliberately smaller than a new cross-layer event stream and is adequate for one local process.

### Profile composition

The existing Agent Teams profile remains opt-in. Its patch gains explicit defaults for:

- `minExecutionMembers: 2`;
- `maxExecutionMembers: 4`;
- `stallWarningMs: 180000`;
- `refreshIntervalMs: 5000`;
- the exact pre-approval tool allowlist.

The domain's existing hard `maxMembers` remains eight for compatibility; the governed execution layer restricts ordinary V1 spawning to four after approval.

## Data flow

1. The Lead creates or edits a task.
2. The task board validates limits, CAS revision, ownership, DAG acyclicity, and write-scope metadata.
3. The task event commits to the root Session.
4. Projection folding increments `planRevision` for a structural task event and derives whether any prior approval is stale.
5. The Team activity notifier wakes waiters only after the durable commit succeeds.
6. The Web panel reads one Team projection and displays plan, roster, work, and tasks.
7. The HUMAN approves the displayed revision; stale approval returns a typed conflict and refreshes the panel.
8. The Lead spawns teammates. Every tool dispatch rechecks approval revision and active teammate count before the body runs.
9. Members report durable status. Review files use existing workspace resource addresses and document preview.

## Failure handling

- Stale plan approval returns `team-plan-conflict`; the UI reloads authoritative state.
- Invalid work reports return typed Team errors and do not append events.
- A missing/foreign/unowned task reference is rejected.
- Write-scope overlap remains an explicit preflight failure for approval in governed V1, even though the underlying Agent Teams task board continues to expose advisory warnings.
- Provider or required-tool absence fails preflight before approval.
- A blocked member remains the same durable teammate. HUMAN or Lead may send a correction through the mailbox; V1 performs no automatic replacement or retry.
- Polling errors remain visible while retaining the last successful view; the next interval retries.
- Disposal cancels polling and preserves the existing Team runtime disposal behavior.

## Verification

Implementation uses behavior-first tests and the narrow repository check ladder.

### Domain tests

- new Team begins at plan revision zero in `draft` and rejects empty-plan approval;
- structural mutations increment revision and invalidate approval;
- execution-only task transitions do not invalidate approval;
- exact-revision HUMAN approval succeeds; stale approval fails;
- replay reconstructs plan and member work state;
- blocked/review-required validation fails closed;
- activity notifications occur only after durable commit;
- HMR disposal removes new registrations.

### Tool tests

- write-capable and composite nested calls are denied before execution readiness;
- WBS/read tools remain available before approval;
- teammate spawn is denied before approval, allowed after approval, and capped at four;
- write-capable calls remain denied until two teammates are active;
- `report_team_status` returns exactly its declared schema;
- tool/provider preflight reports missing capabilities before execution;
- no model-facing approval tool exists.

### Client tests

- plan phase and revision render;
- approval sends the displayed revision and handles stale conflict;
- runtime state, explicit blocker, and inferred stall are visually distinct;
- stall warning never changes durable state;
- review files open the existing workspace file resource;
- polling starts only while open and stops on close/disposal;
- all visible copy is locale-owned.

### Integration checks

Run focused package tests, then the checks required by the touched UI and public type surfaces:

```sh
pnpm exec vitest run packages/experimental/agent-team packages/experimental/tool-agent-team packages/experimental/client-ui-agent-team
pnpm run test:gui
pnpm run typecheck
pnpm run verify-client-ui-i18n
pnpm run verify-client-packages
DSH_SNAPSHOT=replay pnpm run test:web
```

A local opt-in profile smoke must prove: draft WBS creation, denied pre-approval write, stale-approval rejection, successful approval, two teammate spawns, one explicit blocker, one review-file link, task completion, Session restart, and identical replayed plan/work state. A smoke result is local integration evidence, not production or cross-process readiness.

## Non-goals

V1 does not provide cross-process teams, worktree isolation, filesystem locks, automatic retries, automatic blocked classification, recurring watchdog agents, direct HUMAN-to-teammate routing, mailbox timeline UI, autonomous approval, production deployment, or compatibility across unpinned Agent Teams versions.

## Delivery sequence

1. Domain plan/work state and replay.
2. Model tool plus pre-execution write barrier.
3. Web approval/status/file-review UI with bounded polling.
4. Profile defaults, documentation, Agent Note, and local composition smoke.

Each slice must pass its focused tests before the next begins. A failed reporting or UI package does not erase accepted domain behavior; correction remains on the same implementation branch and preserves the prior evidence.
