> **REFERENCE SEED (CR-AIWS-2026-08-008 T2)** — domain content, lớp project-local. KHÔNG auto-copy
> khi tạo desk; wizard offer như một nguồn `domain content` (manifest CR-AIWS-2026-08-009).
> Skeleton portable của ATDB không còn chứa file này (content contract: agent_runtime_design §10).

# Schedule Re-plan Process — PM Agent

> Mapped from PM_Agent_Blueprint/templates/SCHEDULE_REPLAN_PROCESS.md (template_version v0.1).
> ADVISORY ONLY: the agent proposes re-plan OPTIONS and a recommendation; it never makes the
> schedule official. HUMAN decides.

## 1. Trigger
Run this process when: a task is delayed; scope changes; a blocker appears; a key member is
unavailable; a review found major rework; the customer changes priority; or the deadline changes.

## 2. Required inputs
Current schedule; delayed / changed tasks; dependencies; milestone / deadline; available capacity;
risks / issues; HUMAN constraints. Read Wiki / metadata first for context (Wiki-first NOT Wiki-only)
and verify against the live schedule and task data; report conflicts.

## 3. Analysis steps
1. Identify the changed tasks.
2. Identify affected dependencies.
3. Estimate schedule impact.
4. Identify tasks that can be parallelized.
5. Identify tasks that can be split / deferred.
6. Identify risks and trade-offs.
7. Create 2-3 re-plan options.
8. Recommend one option (recommendation only).
9. Surface the decision for HUMAN — do NOT apply any option.

## 4. Re-plan options table

| Option | Description | Pros | Cons | Impact | Risk | Recommendation |
|---|---|---|---|---|---|---|

## 5. Decision request
State, for the HUMAN decision:
- Decision needed
- Recommended option
- Reason
- Deadline impact
- Scope impact
- Risk
- HUMAN confirmation (left blank — HUMAN fills)

## 6. Guardrail
The PM Agent may propose schedule changes but must NOT treat them as official until HUMAN confirms,
and must NOT auto-apply, dispatch, or orchestrate any execution of the chosen option.
