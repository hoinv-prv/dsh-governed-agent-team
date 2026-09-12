---
description: Duyệt learning candidate của một desk (từ run + feedback) — HUMAN confirm / defer / reject từng mục. Chỉ mục được confirm mới thành confirmed memory; mục tái dùng rộng hơn desk đi route blueprint improvement.
argument-hint: <desk>
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, TodoWrite
---

# Command Spec — `/aiws-agent-review-learning`

> **Status:** prompt/spec (file-first). NOT an executable CLI — Post-MVP.
> **Built by:** AIP-EXEC-109 (Phase C of program AIP-PLAN-002).
> **Source:** Requirements v0.4 §6 (FR-MEM-01..05); Detailed Design v0.2 §13/§14/§15; Implementation Plan v0.2 Sprint 10.
> **Reuses** the AIWS capture → triage → HUMAN-gate mechanics (D2) at desk scope.

## Purpose
Review an Agent Task Desk's learning candidates (from runs + feedback) and let HUMAN **confirm / defer / reject**
each. Confirmed candidates become **confirmed memory**; reusable-beyond-desk items become a **blueprint
improvement candidate** (separate route). Records a periodic improvement review.

## Guardrails (always)
- **No auto-confirm / no auto-learning** (FR-MEM-04) — every promotion is an explicit HUMAN decision.
- Confirmed memory entries trace to a `source_candidate` and carry `confirmed_by: HUMAN`.
- **Blueprint improvement is separate** from desk memory (FR-AI-05) — never auto-updates a Blueprint.
- Writes only under `agents/task_desks/<instance_id>/` (staging).

## Inputs
```
/aiws-agent-review-learning instance=<instance_id> [run=<RUN-id>]
```
- Reads `training/candidate_queue.jsonl` (and/or a run's `learning_candidates.jsonl`).

## Flow
1. **Collect** — gather candidates (status `candidate` or `deferred`) from the desk queue (and the named run).
2. **Present** — show each candidate (id, type, content, source_run) to HUMAN.
3. **Decide (per candidate)** — HUMAN chooses:
   - **confirm** → append a `confirmed_memory.jsonl` entry (`status: confirmed`, `source_candidate`, `confirmed_by: HUMAN`, `confirmed_at`); set the candidate's `status: confirmed`. For lesson/guideline/hint types, also append to `memory/lessons_learned.md` / `local_guidelines.md` / `retrieval_hints.jsonl` as appropriate.
     - **Also populate relevance scope (AP-CR-26):** on the new entry, the AI **proposes** an optional `applies_when` (1-line trigger) + `scope_tags` (array) and the **HUMAN approves** (keep the HUMAN gate — no auto-tagging). Use `always` for cross-cutting methodology/process memory (loads on every run); use function/topic tags for specifics (e.g. `function:f02`, `topic:search`). An entry with neither field stays **always-load** (backward-compat). This feeds the relevance-scoped confirmed-memory loading in the ARC (`§5.1 Loaded` / `§5.2 Index`).
     - **Process improvement (AP-CR-31):** for a `process_improvement_candidate`, on confirm apply the change to the desk's OWN `agents/task_desks/<id>/process/<file>` and append a desk `changelog.md` entry (`layer: override`, `source: learning-candidate`, WHAT+WHY — §4A). It must NOT drop/weaken a `governance_invariant` step (staging `lint_agents.py` warns); it never edits the blueprint. (Detailed Design §6D / FR-AI-13.)
     - **Knowledge digest (CR-AIWS-2026-07-017):** for a `digest_synthesis_candidate`, on confirm MOVE the draft digest file into `agents/task_desks/<id>/memory/knowledge_digests/` (frontmatter per `confirmed_memory_schema.md` §Knowledge digests, `status: confirmed`, `confirmed_by: HUMAN`) AND append ONE `retrieval_hints.jsonl` entry (`digest_id` + path + `reuse_when`) — the hint is the discovery channel (ARC §5 loads hints); no separate digest index.
   - **defer** → set candidate `status: deferred` (revisit next review).
   - **reject** → set candidate `status: rejected`.
4. **Blueprint improvement** — if a candidate is reusable beyond this desk, create/append a
   `training/blueprint_creation_candidate.md` (or blueprint_improvement entry) — separate from desk memory; HUMAN review later.
5. **Record review** — append a `periodic_improvement_review.md` entry summarizing decisions + outputs.

## Outputs
- updated `memory/confirmed_memory.jsonl` (+ lessons/guidelines/hints as applicable; confirmed entries may carry HUMAN-approved `applies_when` + `scope_tags` — AP-CR-26)
- updated desk `process/` + a desk `changelog.md` entry when a `process_improvement_candidate` is confirmed (AP-CR-31; never the blueprint)
- updated `training/candidate_queue.jsonl` (status transitions)
- `training/periodic_review_log.md` entry
- optional `training/blueprint_creation_candidate.md`

## Status enum (candidates)
`candidate` → `confirmed` / `deferred` / `rejected` / `deprecated`

> Reminder: this command never promotes anything into Official Wiki or a Blueprint automatically — those remain
> HUMAN-controlled (and, for canonical promotion, CR-gated).
