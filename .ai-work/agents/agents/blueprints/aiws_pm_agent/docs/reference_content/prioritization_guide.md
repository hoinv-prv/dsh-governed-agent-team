> **REFERENCE SEED (CR-AIWS-2026-08-008 T2)** — domain content, lớp project-local. KHÔNG auto-copy
> khi tạo desk; wizard offer như một nguồn `domain content` (manifest CR-AIWS-2026-08-009).
> Skeleton portable của ATDB không còn chứa file này (content contract: agent_runtime_design §10).

# Prioritization Guide — PM Agent

> Mapped from PM_Agent_Blueprint/templates/PRIORITIZATION_GUIDE.md (template_version v0.1).
> ADVISORY ONLY: the agent PROPOSES priority; the final priority is a HUMAN decision (the
> "HUMAN Decision" column is always present and always left for HUMAN to fill).

## 1. Default priority factors

| Factor | Meaning |
|---|---|
| Value | How important the output is to the project goal |
| Urgency | How close the deadline is |
| Dependency | Whether other tasks are blocked by this one |
| Risk | Whether late discovery may cause rework |
| Effort | Whether it fits current capacity |
| Confidence | How clear the task is |
| HUMAN Priority | Explicit HUMAN direction (overrides the proposal) |

## 2. Recommended priority classes
- **P0** — must do now / blocking / critical risk.
- **P1** — important and should be done soon.
- **P2** — useful but can wait.
- **P3** — candidate / optional / backlog.

## 3. Priority output format

| Task ID | Current Priority | Proposed Priority | Reason | Risk if Deferred | HUMAN Decision |
|---|---|---|---|---|---|

The "Proposed Priority" is a recommendation only. "HUMAN Decision" stays blank until HUMAN confirms.

## 4. Anti-patterns to avoid
- Prioritizing all tasks as high.
- Ignoring dependency.
- Ignoring review / gate tasks.
- Over-prioritizing easy tasks (quick-win bias).
- Hiding unclear ownership.
- Presenting a proposed priority as if it were the official, decided priority.
