# Workspace / Queue / Capture Spec for AI Work System MVP
Version: 0.1  
Scope: MVP only

---

# 1. Mục đích

Tài liệu này detail hóa spec cho:
- Workspace
- Active Step Context
- Investigation Queue
- Findings
- Open Questions
- Draft Output
- Capture Inbox

Mục tiêu:
- chốt runtime artifact model
- chốt file set tối thiểu
- chốt lifecycle cơ bản
- chốt rule phân vai giữa các artifact
- chốt lint targets cơ bản

---

# 2. Vai trò của Workspace

Workspace là **runtime execution memory externalized** cho task hiện tại.

Workspace tồn tại để:
- giữ state của task
- cho phép AI làm việc nhiều bước
- hỗ trợ step focus
- giảm phụ thuộc vào chat context
- lưu discoveries và draft outputs

Workspace không phải:
- source of truth
- AIP
- official wiki
- general history store cho mọi thứ

---

# 3. Workspace placement and naming

## 3.1. Folder placement
```text
.ai-work/workspaces/<account_id>/TASK-<task-id>/
```
> **CR-AIWS-2026-06-015 v2:** NEW workspaces live under a per-account folder `.ai-work/workspaces/<account_id>/` (`account_id` from `.ai-work/account_info.yaml`). The `…/TASK-<task-id>/<file>` paths elsewhere in this spec are shorthand under that prefix. Legacy flat `.ai-work/workspaces/TASK-<task-id>/` is preserved (only-new).
>
> **CR-AIWS-2026-06-057 (Phase 1) — Task Workspace:** this runtime workspace is the executor-agnostic **Task Workspace**. The same Task Workspace serves an AIP run, an agent run, and an agent-via-AIP run — there is no separate "AIP workspace" vs "agent workspace". When an agent performs a task via an AIP, the agent run **reuses the driving AIP's Task Workspace** (no second runtime workspace). Mechanism unchanged: the flat numbered file set (§4), the sequential per-account `task_id` (§3.2), and the SINGLE `08_capture_inbox.jsonl` capture channel.

## 3.2. Task ID convention
Recommended:
`TASK-<YYYYMMDD>-<short-slug>`

Example:
`TASK-20260413-review-manufacturing-order-update`

---

# 4. Workspace file set

## 4.1. Required files
- `00_task_brief.md`
- `00b_active_aip.md`
- `00c_active_step_context.md`
- `02_investigation_queue.jsonl`
- `04_findings.md`
- `05_open_questions.md`
- `07_output_draft.md`
- `08_capture_inbox.jsonl`
- `11_output_final.md`

## 4.2. Optional files
- `01_hot_cache_snapshot.md`
- `03_sources_loaded.md`
- `06_scope_map.md`
- `09_history_log.md`
- `10_triage_candidates.md`

## 4.3. Why this split
- required files cover execution minimum
- optional files support deeper workflows without bloating every task

---

# 5. Task Brief spec

## 5.1. Purpose
Minimal human/AI-readable summary of the task.

## 5.2. Suggested sections
1. Task ID
2. Goal
3. Expected Output
4. Primary Mode
5. Supporting Modes
6. Scope Notes
7. Current Status

## 5.3. Usage
- first orientation inside workspace
- useful for resume/handoff

---

# 6. Active AIP reference spec

## 6.1. Purpose
Make the active controlling AIP explicit inside the workspace.

## 6.2. Recommended content
- source AIP id
- source AIP path
- AIP type
- status note

## 6.3. Why not duplicate full AIP
To avoid drift and duplication.
Workspace should point to AIP, not clone it.

---

# 7. Active Step Context spec

## 7.1. Placement
`.ai-work/workspaces/TASK-<task-id>/00c_active_step_context.md`

## 7.2. Optional pointer file
`.ai-work/workspaces/TASK-<task-id>/00c_current_step.json`

## 7.3. Purpose
Bridge between AIP and Workspace.
Give AI a focused packet for the current step.

## 7.4. Metadata
```yaml
artifact_type: active_step_context
artifact_id: ASC-<task-id>-<step-id>
task_id: TASK-<task-id>
source_aip: AIP-PLAN-001
step_id: STEP-02
status: active
updated_at: YYYY-MM-DD
```

## 7.5. Required sections
1. Step ID / Step Title
2. Source AIP
3. Objective
4. Recommended Mode
5. Applicable Guidelines
6. Recommended Skills
7. Inputs
8. Expected Outputs
9. Done Condition
10. Notes / Constraints
11. Relevant Queue Item IDs
12. Relevant Finding IDs
13. Relevant Open Question IDs
14. Active References

## 7.6. Rules
- linked, not duplicated
- use IDs/pointers where possible
- do not copy long findings/history by default

## 7.7. Update triggers
Update Active Step Context when:
- step changes
- checkpoint changes step focus
- linked runtime state for current step changes materially

---

# 8. Investigation Queue spec

## 8.1. Placement
`.ai-work/workspaces/TASK-<task-id>/02_investigation_queue.jsonl`

## 8.2. Format
JSONL; one queue item per line.

## 8.3. Purpose
Task-scoped frontier for multi-step investigation/execution.

## 8.4. Required fields
- `id`
- `kind`
- `target`
- `question`
- `why`
- `priority`
- `status`

## 8.5. Optional fields
- `source_refs`
- `parent`
- `depth`
- `step_id`
- `notes`

## 8.6. Example
```json
{
  "id": "Q6",
  "kind": "read_artifact",
  "target": "wiki/function/inventory_update.md",
  "question": "How does inventory relate to manufacturing order lifecycle?",
  "why": "Likely mandatory dependency",
  "priority": "critical",
  "status": "queued",
  "source_refs": ["Q2"],
  "parent": "Q2",
  "depth": 1,
  "step_id": "STEP-02"
}
```

## 8.7. Enums
### priority
- critical
- high
- normal
- defer

### status
- queued
- in_progress
- done
- blocked
- discarded

## 8.8. Queue rules
- queue items must be small/actionable
- queue must not be used as general note bucket
- future-useful but not step-relevant discoveries go to Capture Inbox instead
- step relevance should be trackable when possible

---

# 9. Findings spec

## 9.1. Placement
`.ai-work/workspaces/TASK-<task-id>/04_findings.md`

## 9.2. Purpose
Store the evolving understanding/results discovered during execution.

## 9.3. Suggested structure
1. Findings List
2. Confirmed Findings
3. Inferred Findings
4. To-Verify Findings
5. Notes

## 9.4. Rules
- findings are runtime understanding
- not official truth
- should remain concise enough to support checkpoint compaction
- may be linked from Active Step Context via finding IDs/anchors

---

# 10. Open Questions spec

## 10.1. Placement
`.ai-work/workspaces/TASK-<task-id>/05_open_questions.md`

## 10.2. Purpose
Store unresolved but important uncertainty.

## 10.3. Suggested sections
1. Open Questions
2. Blocking Questions
3. Non-blocking Questions
4. Deferred Questions

## 10.4. Suggested per-question fields
- Question
- Why it matters
- Current status
- Related refs
- Suggested next action

## 10.5. Rules
- open questions should prevent false certainty
- unresolved questions should be classified, not left vague

---

# 11. Draft Output spec

## 11.1. Placement
`.ai-work/workspaces/TASK-<task-id>/07_output_draft.md`

## 11.2. Purpose
Store evolving deliverable draft.

## 11.3. Suggested sections
1. Draft Outline
2. Main Content Draft
3. Pending Gaps
4. Notes for Finalization

## 11.4. Rule
Draft Output is not final output.
Final output should move to `11_output_final.md`.

---

# 12. Capture Inbox spec

## 12.1. Placement
`.ai-work/workspaces/TASK-<task-id>/08_capture_inbox.jsonl`

## 12.2. Purpose
Staging area for discoveries not organized immediately.

## 12.3. Format
JSONL

## 12.4. Required fields
- `id`
- `type`
- `title`
- `content`
- `status`
- `suggested_target`

## 12.5. Optional fields
- `source_refs`
- `knowledge_class_candidate`
- `use_rule_candidate`
- `notes`

## 12.6. Example
```json
{
  "id": "C2",
  "type": "playbook_candidate",
  "title": "Review planning fallback mode when SeedPath is unavailable",
  "content": "Use target wiki + domain overview + canonical design + related function pages to reconstruct scope.",
  "status": "captured",
  "suggested_target": "playbook",
  "source_refs": ["07_output_draft.md"]
}
```

## 12.7. Enums
### type
- insight
- qa_candidate
- summary_candidate
- playbook_candidate
- relation_candidate
- deferred_note
- wiki_update_candidate

### status
- captured
- triaged
- promoted
- archived
- discarded
- deferred
- retained_local

> `deferred` and `retained_local` are **not new values** (CR-AIWS-2026-08-125 C7). Truth
> (`SOP_MASTER` §capture close classification) has always named them and `CAPTURE_STATUS_ENUM` has always
> carried them; only this list lacked them, so the spec contradicted Truth. A `deferred` row MUST also
> carry `deferred_to: <backlog_id>` — see **Capture Backlog** below; a `deferred` row with no pointer is
> a WARN (`capture_deferred_without_pointer`).

### candidate_kind

The **improvement taxonomy**: what class of improvement this capture is, and therefore who triages it.
A closed vocabulary of **15** values (CR-AIWS-2026-08-126 C1), derived from the corpus rather than from
the playbook's trigger table — the table describes what capture is *prompted*, the field records what was
actually *found*, and before this CR the field was never validated at all: 66 distinct values across 709
records, every one invented at the keyboard.

`retrieval_improvement` · `process_doc_gap` · `reusable_pattern` · `tooling_opportunity` ·
`wiki_quality_issue` · `authoring_lesson` · `tool_gotcha` · `decision_or_convention` · `spec_impl_drift` ·
`review_rule` · `wiki_knowledge_gap` · `relation_or_object` · `deliverable_defect` ·
`output_quality_feedback` · `qa_candidate`

**Who triages each family and what it becomes** is the consumer map in
`procedural/capture_and_triage_rules.md` — the routing lives there, with the triage rules, not here.

**A project may declare its own kinds** under a namespace in `.ai-work/project_profile.yml`
(`capture_kinds:`); the effective set is *preset ∪ `<namespace>:<id>`*. A project may add a **kind**; it
may not add a `type` or a `suggested_target`, because those are the pipelines lint and routing
understand. Project-specific destinations are expressed through `target_artifact`.

**Legacy stays valid.** The 51 values outside this list keep working on records that already carry them
and lint as WARN, not error; `append_capture` refuses them only for **new** writes (two-beat rule,
CR-AIWS-2026-08-085). 47 records carry no `candidate_kind` at all and 4 carry a `type` value in that
field: they stay exactly as they are. Rewriting history to fit a new taxonomy is how data starts lying
about what was observed.

### improvement_scope

`aiws | project` — **required on new writes**. The routing key of the consumer map: an optional routing
key is one that half the corpus will lack. `append_capture` pre-fills it from the family default, so the
writer pays nothing in the common case and states it only where the family is genuinely ambiguous.

A third value `both` was considered and rejected: the agents-pack routing rule already resolved the same
ambiguity by requiring **two records, one per angle**, which keeps every record single-destination.

### target_artifact

Optional. A repo-relative path or a stable id, validated for **shape only and never for existence** — a
capture may legitimately name an artifact that does not exist yet. This is where a project-specific
destination goes.

### correction_class

Optional, meaningful on `output_quality_feedback`: `missing_section` · `wrong_format` ·
`wrong_approach` · `factual_error` · `scope`.

### suggested_target
- wiki_curated
- wiki_reference
- truth
- playbook
- skill
- history_only
- discard

## 12.8. Rules
- Capture Inbox is not Queue
- Capture Inbox is not official Wiki
- Capture Inbox may later feed curation or archive

## 12.9. Triage rollup (CR-AIWS-2026-06-015 F4)
The AIP registry (`.ai-work/aip/index.jsonl`, built by `build_aip_index.py`) projects a per-AIP capture-triage rollup from each workspace's `08_capture_inbox.jsonl`:
- **`needs_triage`** counts ONLY `status: captured` — aligned exactly with `lint_workspace`'s untriaged check, so registry and linter never diverge.
- **`deferred`** is a SEPARATE informational count (NOT folded into `needs_triage` — deferred is a conscious hold, not an untriaged item).
- `all_triaged` = (`needs_triage == 0`). `promoted` / `archived` / `discarded` / `retained_local` count as resolved.
- The rollup is a read-only PROJECTION (rebuildable, never writes status back). `aiws-aip run status <AIP-ID>` surfaces it per-AIP; `build_aip_index.py --list-untriaged` lists offenders repo-wide.

---

# 13. History log / task log spec

## 13.1. Placement
Optional:
`.ai-work/workspaces/TASK-<task-id>/09_history_log.md`

## 13.2. Purpose
Provide a readable timeline / trace of notable task events.

## 13.3. Typical contents
- checkpoint notes
- replan note
- major decisions
- major blockers

Not required for every task.

---

# 14. Final Output spec

## 14.1. Placement
`.ai-work/workspaces/TASK-<task-id>/11_output_final.md`

## 14.2. Purpose
Store final deliverable/result of the task.

## 14.3. Rule
A task should not be considered completed without a final output file or a clear explanation of why no final output is produced.

---

# 15. Workspace lifecycle

## 15.1. Create
Create workspace when task is complex enough by MVP rules.

## 15.2. Run
Workspace evolves during execution.

## 15.3. Checkpoint
Compact queue/findings/open questions when context becomes diffuse.

## 15.4. Finalize
Write final output and classify remaining open items.

## 15.5. Archive
Later policy may move completed workspace trail into history; exact archive policy can be refined later.

---

# 16. Lint targets

## 16.1. Workspace lint
Check:
- required files exist
- active AIP reference exists
- active step context exists for active multi-step task
- final output exists before task marked done

## 16.2. Active Step Context lint
Check:
- source AIP exists
- step id present
- required sections present
- linked ids well-formed

## 16.3. Queue lint
Check:
- required fields exist
- enums valid
- duplicate ids not allowed
- question/why not empty

## 16.4. Capture lint
Check:
- required fields exist
- enums valid
- if promote-intended item lacks source_refs, warn

---

# 17. Boundary rules summary

## Queue vs Capture
- Queue = what to do next for this task
- Capture = what may matter later but not now

## Findings vs Wiki
- Findings = runtime understanding
- Wiki = curated long-term knowledge

## Open Questions vs Findings
- Findings = what we think we know
- Open Questions = what we know we do not yet know

## AIP vs Active Step Context
- AIP = macro control
- Active Step Context = current step packet

---

# 18. Kết luận

Spec này chốt Workspace và runtime artifacts theo hướng:
- focused
- step-driven
- queue-enabled
- curation-aware

Nó tạo nền để build:
- workspace templates
- queue/capture scripts
- step context generators
- runtime lint

---

# Knowledge-runtime sprint addendum — Workspace, notebook, and knowledge-runtime boundary

## Workspace and notebook-like working context

Workspace may hold current context, notebook-like working notes, selected references, temporary findings, and intermediate state for the active task.

This working context may be consulted before Wiki Meta / Index when resuming or continuing a task.

## Boundary rules

- Workspace is not Knowledge Hub.
- Notebook-like working context is not reusable canonical knowledge.
- Working notes do not automatically become Knowledge Hub objects.
- Workspace state does not replace Working AIP.
- If a working finding should become reusable knowledge, it must go through controlled capture.
- If a working finding changes execution basis, it should be reflected into Working AIP when appropriate.

## Deferred notebook work

A full Notebook spec, including lifecycle, allowed content, discard/promotion rules, and relation to Working AIP / Knowledge Hub, is deferred to a later sprint.

---

# Personal Notebook boundary addendum

## Purpose

Personal Notebook is added as a file/folder-based personal working reference area for BrSE/HUMAN.

## Boundary

- Personal Notebook is separate from Workspace findings.
- Workspace findings cover task-bound notes and active task/session state.
- Personal Notebook covers personal/cross-task notes.
- Personal Notebook is not Working AIP.
- Personal Notebook is not Knowledge Hub.
- Personal Notebook is not source of truth by default.
- Personal Notebook does not auto-promote into Knowledge Hub.

## Capture relation

Personal Notebook may produce capture candidates.

A capture candidate is not promotion. Promotion to Knowledge Hub must go through controlled capture.

## Task-bound note rule

If a finding supports the current task directly, store it in Workspace findings.

If it changes execution basis, reflect it into Working AIP or task artifact.

If it is personal/cross-task/future reference, store it in Personal Notebook.

---

# Source Understanding Artifact capture boundary addendum

## Boundary

Workspace findings, retrieval summaries, and Personal Notebook notes may suggest creating a Source Understanding Artifact, but they do not auto-convert into one.

A Source Understanding Artifact must be deliberately created with:
- source pointer
- source scope
- understanding date
- status/authority/freshness hints

## Capture path

A draft Source Understanding Artifact may become:
- capture_candidate
- reviewed_understanding
- curated Knowledge Hub artifact

through controlled capture/review.

## Guardrail

A Source Understanding Artifact does not replace Working AIP, Workspace findings, Personal Notebook, or raw/source.

---

# Task Lens trace and capture canonical addendum

Selected Task Lens should be recorded only when it affects task direction or traceability.

Record lens in Workspace / Working AIP when:
- HUMAN confirmed or adjusted lens
- lens expansion changed direction/scope
- custom/runtime lens was used
- lens affects execution basis

Custom/runtime lens may become capture candidate if reusable, but it must not auto-promote into Knowledge Hub or full lens catalog.

---

# Controlled Knowledge Promotion capture addendum

Workspace findings may become Knowledge Promotion candidates when they have potential reusable value.

Candidate does not mean approved/promoted knowledge.

Candidate statuses:
- draft_candidate
- needs_source_check
- ready_for_review
- approved_for_promotion
- promoted
- rejected
- deferred
- retained_local

Valid outcomes:
- Knowledge Hub
- canonical docs
- appendix/examples
- guideline/playbook
- AIP Template improvement candidate
- future sprint backlog
- Workspace-only retention
- Personal Notebook retention
- discard / no promotion

Lookback reports can create candidates, but they do not auto-promote or auto-apply changes.

---

# v0.9.8 Wiki Meta / Index candidate capture addendum

If AI discovers during task execution that Wiki Source Meta is missing useful lookup keys, source-specific hints, cautions, or representation quality notes, it may create a candidate or lightweight maintenance suggestion.

Examples:
- missing alias in Lookup Keys
- broken artifact_locator
- insufficient converted markdown representation
- missing caution for deprecated/partial source
- source_representation_quality_issue

Small fixes may be lightweight maintenance. Important changes should follow Controlled Knowledge Promotion.

---

# v0.9.9 Working AIP Connection workspace addendum

Workspace holds current task/session working state.

Working AIP selects and structures execution context.

Rules:
- Workspace note is not Working AIP.
- Workspace context can feed Working AIP.
- Do not copy entire Workspace blindly.
- Continuation tasks should inspect Workspace/current sprint context, identify next step, and update/create Working AIP before non-trivial execution.

---

# v0.9.10 Workspace Boundary addendum

Workspace is active task/session working context.

Core boundary:

```text
Workspace holds working context.
Working AIP controls execution.
Knowledge Hub stores reusable knowledge.
Notebook stores personal/local notes.
Canonical docs/source artifacts hold official content.
```

Workspace can feed other layers, but it does not replace them.

---

## Runtime Queue

Preferred file:

```text
02_runtime_queue.jsonl
```

Backward-compatible alias:

```text
02_investigation_queue.jsonl
```

Rule:

```text
If any task produces an unplanned subtask/action/follow-up during execution,
AI should add it to Workspace Runtime Queue unless it blocks the current step.
```

Exception:

```text
Queue non-blocking follow-up work.
Handle or escalate blocking work immediately.
```

---

## Capture Inbox

Recommended file:

```text
08_capture_inbox.jsonl
```

Rule:

```text
Capture first, curate later.
```

Boundary:

```text
Capture Inbox item is not yet a reviewed Knowledge Promotion Candidate.
```

---

## Queue vs Capture Inbox

```text
Runtime Queue = do/check/update later for current task.
Capture Inbox = capture possible future value for later triage.
```

---

## Capture Backlog

A capture deferred at AIP close leaves the Task Workspace — which is gitignored and gets archived — and
is written to a **git-tracked, per-account** store:

```text
.ai-work/capture_backlog/<account_id>.jsonl
```

Created on demand by `triage_capture.py`, which seeds a `README.md` beside it on first use. Never
hand-edited.

**The record is self-contained.** It copies the capture's content rather than pointing at it, because a
row pointing into an archived, gitignored workspace would rot into an unresolvable reference. Key fields:

| field | meaning |
|---|---|
| `backlog_id` | `BL-<aip-number>-<cap_id>` — **derived**, never allocated, so `defer` is idempotent and two sessions cannot mint the same id |
| `origin` | `{aip_id, task_id, workspace, cap_id}`; `workspace` uses the `__PROJECT_ROOT__` portable locator |
| `defer_reason` | **required** — a deferral with no reason is the state this store replaces |
| `status` | `open` · `triaged` · `promoted` · `discarded` — a **backlog vocabulary in a separate file**, deliberately NOT part of `CAPTURE_STATUS_ENUM` |
| `resolution` | `{resolved_at, resolved_by, disposition_ref}`; `disposition_ref` names what the row *became* — a CR id, a checklist item, a wiki `source_id`, a lint code |

**Pointer semantics.** On defer the workspace inbox row is rewritten **once** to `status: deferred` plus
`deferred_to: <backlog_id>` and is frozen thereafter. The backlog row is the live one. Two live copies
would let the two records disagree about the same item.

`improvement_scope` and `target_artifact` are defined above (CR-AIWS-2026-08-126 C2) and carried on
backlog rows as well, so a deferred capture keeps its routing.

The AIP-index rollup counts backlog rows alongside open captures, so deferring keeps the debt visible
instead of hiding it.

## Close classification

At task close, classify Workspace content:

```text
discard
archive task-local
move/copy to Notebook
create Knowledge Promotion Candidate
merge into Working AIP/output
merge into canonical docs/deliverable
record in changelog/log
```

See:
- `Workspace_Boundary_Spec_MVP.md`
- `Workspace_Runtime_Guidance_MVP.md`
- `Workspace_Boundary_Samples_Appendix_MVP.md`
