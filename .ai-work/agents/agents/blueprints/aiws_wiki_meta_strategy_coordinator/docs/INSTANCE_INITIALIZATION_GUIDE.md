# Instance Initialization Guide — Wiki Meta Strategy Coordinator

> Docs-parity set added by CR-AIWS-2026-07-017. Create via `/aiws-agent-create` (wizard).

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


1. **Identity:** `wiki_meta_strategy_coordinator__<project>`; display_name first, id auto-suggested.
2. **Context Q&A:** which source areas / systems the wiki strategy must cover; multi-system ->
   record the `system` ids; existing wiki state (index counts, overview pages).
3. **Context files:** `wiki_references.yaml` (recommended_entries incl. `SRC-OVERVIEW-WIKI_CONTENTS_OVERVIEW_<system>`
   + `SRC-OVERVIEW-WIKI_SEARCH_GUIDE_<system>`; lookup_intents optional), `source_references.yaml`
   (+ optional `sot_layer`), `source_priority.yaml`, `ignored_paths.yaml`.
4. **Memory:** 5 files created EMPTY (see MEMORY_AND_LEARNING_RULES §2). Warm start = clone from the
   nearest same-role instance + prune via /aiws-agent-review-learning (AP-CR-28) — no fabricated seed.
5. **Workspace/training dirs** per pack skeleton; tools `[]` (HUMAN-activated).
6. **First run suggestion:** a strategy baseline over the current wiki state (planning-only output).
7. Done criteria: instance lints clean (`lint_agents.py`); setup summary HUMAN-approved; NOT run yet.
