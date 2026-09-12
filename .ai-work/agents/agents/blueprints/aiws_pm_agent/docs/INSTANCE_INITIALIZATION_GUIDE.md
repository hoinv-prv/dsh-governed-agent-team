# PM Agent Task Desk Initialization Guide

> Mapped from PM_Agent_Blueprint/templates/INSTANCE_INITIALIZATION_GUIDE.md (template_version v0.1).
> Use when creating a PM Agent Task Desk from this blueprint (`blueprint_id: aiws_pm_agent`).
> For the precedent desk shape see the `aiws_wiki_meta_strategy_coordinator` blueprint's own `docs/`.
> **No desk is shipped in the package**, and the old pointer here named the PRE-P2 root
> (`instances/`) — both corrected by CR-AIWS-2026-08-074 C4. PM = PLANNING / ADVISORY only.

> ## ⛔ BEFORE YOU CREATE A DESK — check which desk root your tree is on
>
> `run_agent.py` resolves **one** desk root: `agents/task_desks/` **if that directory exists**,
> otherwise legacy `agents/instances/`. There is no union, and the switch is on the directory
> **existing**, not on it holding desks.
>
> ⇒ If your tree still has `agents/instances/` with desks in it and **no** `agents/task_desks/`,
> then creating your new desk at `agents/task_desks/` makes **every existing desk vanish** from
> `list` / `run` / `status` / `upgrade`, silently. Nothing is deleted; it simply stops being
> reachable.
>
> **Do this first:** `ls .ai-work/agents/agents/` — if you see `instances/`, run the desk-dir
> migration (`aiws-pkg upgrade` step **7c-bis**) BEFORE creating anything. If you see
> `task_desks/`, you are already migrated. — CR-AIWS-2026-08-074 C13


## 1. Purpose
Create a project-specific, trainable copy of the PM Agent blueprint. The instance is INSTANCE-OWNED
and is not overwritten by blueprint updates (FR-AI-05).

## 2. Required instance information
```yaml
instance_id: pm_agent__<project_name>
instance_name: PM Agent for <Project Name>
creation_mode: blueprint_based
blueprint_id: aiws_pm_agent
blueprint_version: "0.1"
project_id: <project_id>
owner: <HUMAN/PM/Team>
status: active
created_at: "YYYY-MM-DDThh:mm:ss+09:00"
last_reviewed_at: null
```

## 3. Project context setup (ask HUMAN)
- What project does this PM Agent support?
- Is it sprint-based, milestone-based, or ad-hoc?
- What are the main deliverables and the main deadlines/milestones?
- Where is the task list? the project Wiki? the meeting notes? the risk/issue/action logs?
- Who reviews PM reports? Who is the official decision owner (always HUMAN)?

## 4. Context files (instance `context/`, mirroring the precedent instance)
- `source_priority.yaml` — source_priority ordering (Detailed Design §7.4): **Wiki-first NOT
  Wiki-only** — Wiki/metadata first, then AIP / task list / schedule / status / meeting notes;
  conflicts reported, never silently resolved.
- `source_references.yaml` — task sources, report sources, AIP/working-AIP paths.
- `wiki_references.yaml` — project Wiki entries the agent consults first.
- `ignored_paths.yaml` — e.g. `tmp/`, `archive/`.
- (working_inventory per §7.5 may be added as the instance is used.)

## 5. Memory initialization (CONFIRMED default = 8 files, created EMPTY)
Create, EMPTY (no unapproved seed):
```text
memory/confirmed_memory.jsonl
memory/lessons_learned.md
memory/planning_patterns.md
memory/reporting_preferences.md
memory/recurring_risks.md
memory/stakeholder_preferences.md
memory/false_alarm_notes.md
memory/retrieval_hints.jsonl
```
Memory grows only through HUMAN-confirmed learning candidates (see MEMORY_AND_LEARNING_RULES.md).

## 6. Workspace initialization
```text
workspace/
  active_runs/
  completed_runs/
  step_outputs/
  handoff_artifacts/
training/
  feedback_log.jsonl
  candidate_queue.jsonl
  periodic_review_log.md
```

## 7. Tool bindings
This blueprint ships NO default tools. The instance `tools/tool_bindings.yaml` starts empty; tool
activation is HUMAN-gated and is not required for PM (planning/advisory) operation.

## 8. First run recommendation
Recommended first run — create a project status baseline: known tasks, milestones, current risks,
current blockers, open questions, reporting-format preference. Output: `project_pm_baseline.md`
(a proposal/baseline draft; HUMAN reviews).

## Wiki first-read + GENERATED guardrail (CR-AIWS-2026-07-015)
- `context/wiki_references.yaml` recommended_entries: include the per-system
  `SRC-OVERVIEW-WIKI_CONTENTS_OVERVIEW_<system>` + `SRC-OVERVIEW-WIKI_SEARCH_GUIDE_<system>` pages.
- GENERATED overview pages are projections — the agent NEVER hand-edits them
  (`overview_hand_edit` lint = ERROR); to change content, fix source metas/index or raise a capture.
