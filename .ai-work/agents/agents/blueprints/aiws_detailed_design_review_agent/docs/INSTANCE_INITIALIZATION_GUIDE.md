# Instance Initialization Guide — Detailed Design Review Agent

> Mapped from: Document_Review_Agent_Blueprint/templates/INSTANCE_INITIALIZATION_GUIDE.md (template_version v0.1).
> Aligned to pack instance schema: Detailed Design v0.2 §4 (instance) + §5 (blueprint_ref) + §7 (context) + §8 (workspace) + §15 (memory).
> Mirror the precedent desk shape: see the `aiws_wiki_meta_strategy_coordinator` blueprint's own
> `docs/` for the layout. **No desk is shipped in the package** (ship-set carries blueprints and
> templates only), so do not expect a `task_desks/<...>__sample_project/` folder to exist on a fresh
> install — CR-AIWS-2026-08-074 C4.

> ## ⛔ BEFORE YOU CREATE A DESK — check which desk root your tree is on
>
> `run_agent.py` resolves **one** desk root: `agents/task_desks/` **if that directory exists**,
> otherwise legacy `agents/instances/`. There is no union, and the switch is on the directory
> **existing**, not on it holding desks.
>
> ⇒ If your tree still has `agents/instances/` with desks in it and **no** `agents/task_desks/`,
> then creating your new desk at `agents/task_desks/` — as the paths below say — makes **every
> existing desk vanish** from `list` / `run` / `status` / `upgrade`, silently. Nothing is deleted;
> it simply stops being reachable.
>
> **Do this first:** `ls .ai-work/agents/agents/` — if you see `instances/`, run the desk-dir
> migration (`aiws-pkg upgrade` step **7c-bis**) BEFORE creating anything. If you see
> `task_desks/`, you are already migrated and the paths below are correct as written.


## 1. Instance identity (`desk.yaml` — §4)
```yaml
instance_id: detailed_design_review_agent__<project_or_context>
instance_name: <Readable Name>
creation_mode: blueprint_based
blueprint_id: aiws_detailed_design_review_agent
blueprint_version: "0.1"
project_id: <project_id>
owner: HUMAN
status: active
created_at: "<YYYY-MM-DDThh:mm:ss+09:00>"
last_reviewed_at: null
```
Also write `blueprint_ref.yaml` (§5) pointing at this blueprint + version.

## 2. Context (`context/` — §7, Wiki-first NOT Wiki-only)
- `wiki_references.yaml` — Wiki entries to read FIRST (project overview, business rules,
  architecture, source navigation, known cautions).
- `source_references.yaml` — source dirs that BACK findings (requirements, basic design, API/DB/
  screen specs, detailed design).
- `source_priority.yaml` (§7.4) — Wiki-first ordering; source verification required when Wiki is
  stale/unverified, a conflict is detected, or output feeds an official deliverable.
- `ignored_paths.yaml` — paths to skip.

## 3. Memory (`memory/` — §15; blueprint `memory_profile`) — EXACTLY 8 files (review-family UNION-8), created EMPTY (AP-CR-36)
```text
memory/confirmed_memory.jsonl
memory/lessons_learned.md
memory/retrieval_hints.jsonl
memory/common_issue_patterns.md
memory/false_positive_notes.md
memory/local_guidelines.md
memory/output_preferences.md
memory/tool_usage_notes.md
```
Create EMPTY. Seed ONLY HUMAN-approved initial memory — never auto-seed. `false_positive_notes.md`
is important for review agents (prevents repeated invalid findings).

## 4. Workspace + training (§8 / §14)
```text
workspace/active_runs/
workspace/completed_runs/
workspace/handoff_artifacts/
workspace/step_outputs/
training/feedback_log.jsonl
training/candidate_queue.jsonl
training/periodic_review_log.md
```

## 5. Tools (§16)
```text
tools/local_tools/
tools/tool_bindings.yaml   # default_tools is [] — bind tools only when HUMAN-activated
```

## 6. Run capture routing (§14 / AP-CR-13)
- Running UNDER an AIP: tier the capture UP to the project capture inbox
  `08_capture_inbox.jsonl` / wiki-candidate flow; the instance keeps a POINTER, not a duplicate.
- Running WITHOUT an AIP: capture stays local in `training/candidate_queue.jsonl`.
Promotion to confirmed memory / Official Wiki is HUMAN-gated in both branches.

## 7. Done criteria
Identity clear; blueprint_ref set; Wiki/source references configured (Wiki-first ordering); shared
checklist/process/output bound via the blueprint; memory/training/workspace/tools folders exist
(memory empty); HUMAN understands the agent reviews + advises only (no approve, no edit, no
auto-update).

## Wiki first-read + GENERATED guardrail (CR-AIWS-2026-07-015)
- `context/wiki_references.yaml` recommended_entries: include the per-system
  `SRC-OVERVIEW-WIKI_CONTENTS_OVERVIEW_<system>` + `SRC-OVERVIEW-WIKI_SEARCH_GUIDE_<system>` pages.
- GENERATED overview pages are projections — the agent NEVER hand-edits them
  (`overview_hand_edit` lint = ERROR); to change content, fix source metas/index or raise a capture.
