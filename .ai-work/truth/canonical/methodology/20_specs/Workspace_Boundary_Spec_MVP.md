# Workspace Boundary Spec MVP

Status: Canonical MVP spec  
Version: v0.9.10  
Date: 2026-04-26  
Source sprint: Workspace Boundary Minimal Spec Sprint

---

## 1. Purpose

This spec defines the minimal Workspace boundary for AI Work System MVP.

The goal is to help AI manage active task/session context without confusing Workspace with Working AIP, Knowledge Hub, Notebook, source artifacts, or canonical docs.

---

## 2. Core definition

Workspace means:

> the active task/session working area that holds current context, intermediate state, selected sources, temporary notes, and task-local artifacts needed while AI/HUMAN work on a task.

Short definition:

```text
Workspace = active task/session working context.
```

### 2.1. Task Workspace (the on-disk runtime workspace) — CR-AIWS-2026-06-057 Phase 1

The concrete on-disk realization of a Workspace for one task/run is the **Task Workspace** at `.ai-work/workspaces/{account}/{task_id}/`. It is **executor-agnostic**: the same Task Workspace serves an AIP run, an agent run, and an agent-via-AIP run — there is no separate "AIP workspace" vs "agent workspace". When an agent performs a task **via an AIP**, the agent run **reuses the driving AIP's Task Workspace** and does not create a second runtime workspace to track. Mechanism is unchanged: the flat numbered file set, the sequential per-account `task_id`, the single `08_capture_inbox.jsonl` capture channel, and the write-once `runtime_workspace` pointer.

---

## 3. Core boundary

```text
Workspace holds working context.
Working AIP controls execution.
Knowledge Hub stores reusable knowledge.
Notebook stores personal/local notes.
Canonical docs/source artifacts hold official content.
```

Workspace can feed other layers, but it does not replace them.

---

## 4. What Workspace does

Workspace helps AI/HUMAN:

- keep active task context visible
- collect selected source references
- record current open points
- keep intermediate findings
- hold draft outputs before acceptance
- track temporary decisions
- prepare handoff into Working AIP
- preserve runtime-discovered follow-up work
- capture findings/ideas/candidates before triage
- support continuation after interruption
- support task close/cleanup

---

## 5. What Workspace does not do

Workspace is not:

- Working AIP
- Knowledge Hub
- Personal Notebook
- source of truth by default
- canonical design set
- official deliverable folder by default
- approval system
- automation engine
- long-term knowledge registry
- replacement for source verification
- replacement for aiws-aip run

---

## 6. Recommended runtime artifact split

For non-trivial tasks, Workspace may use separated runtime artifacts.

Recommended set:

```text
00_task_brief.md
00b_active_aip.md
00c_active_step_context.md
02_runtime_queue.jsonl
02_investigation_queue.jsonl   # backward-compatible alias
04_findings.md
05_open_questions.md
07_output_draft.md
08_capture_inbox.jsonl
11_output_final.md
```

Optional/supporting files:

```text
01_hot_cache_snapshot.md
03_sources_loaded.md
06_scope_map.md
09_history_log.md
10_triage_candidates.md
```

This split is recommended because Workspace should not become one undifferentiated dumping file.

Small tasks do not need every file.

---

## 7. Workspace contents

Workspace may contain:

- task summary
- current task state
- selected sources
- active Working AIP pointer
- Task Lens / mode
- open questions
- blockers
- assumptions
- intermediate findings
- temporary reasoning notes
- draft outputs
- review notes
- feedback notes
- current todo/next steps
- runtime queue items
- execution log/checklist
- Capture Inbox items
- candidate findings
- candidate improvements
- source representation issues
- local decisions pending confirmation
- cleanup/close notes

---

## 8. Workspace non-contents

Workspace should not be used as:

- final canonical design set
- durable Knowledge Hub entry
- official source of truth
- long-term personal notebook
- approved AIP Template
- official package archive
- source artifact repository
- project-wide registry
- uncontrolled knowledge dump

These may be referenced from Workspace, but they should live in their proper layer.

---

## 9. Workspace Runtime Queue

Workspace Runtime Queue is:

> task-local action frontier for runtime-discovered work.

Preferred file:

```text
02_runtime_queue.jsonl
```

Backward-compatible alias:

```text
02_investigation_queue.jsonl
```

General rule:

```text
If any task produces an unplanned subtask/action/follow-up during execution,
AI should add it to Workspace Runtime Queue unless it blocks the current step.
```

Purpose:

```text
Stay focused on the current task.
Avoid distraction/context switching.
Avoid forgetting runtime-discovered work.
Process queued subtasks sequentially at a later loop/checkpoint.
```

Exception:

```text
Queue non-blocking follow-up work.
Handle or escalate blocking work immediately.
```

Queue vs Capture Inbox:

```text
Runtime Queue = do/check/update later for current task.
Capture Inbox = capture possible future value for later triage.
```

---

## 10. Runtime Queue format

Recommended JSONL item:

```json
{
  "id": "Q-001",
  "title": "Update manifest after package files are generated",
  "status": "pending",
  "priority": "high",
  "type": "package_update_step",
  "reason": "Manifest must reflect added/updated files before package close.",
  "source_refs": [],
  "origin": "canonical package creation step",
  "next_action": "After file generation, update MANIFEST.md and verify package contents.",
  "blocking": true,
  "created_at": "2026-04-26",
  "updated_at": "2026-04-26",
  "result": ""
}
```

Recommended status:

```text
pending / in_progress / resolved / blocked / deferred / cancelled / moved_to_capture_inbox / moved_to_open_questions / moved_to_backlog
```

Recommended priority:

```text
high / medium / low
```

---

## 11. Capture Inbox

Capture Inbox is:

> Workspace-local staging area for findings, ideas, source issues, and improvement candidates that may have future value but are not ready to be promoted or organized immediately.

Recommended file:

```text
08_capture_inbox.jsonl
```

Short rule:

```text
Capture first, curate later.
```

Boundary:

```text
Capture Inbox item is not yet a reviewed Knowledge Promotion Candidate.
```

Capture Inbox may later feed:
- Knowledge Promotion Candidate
- Wiki Meta / Index maintenance candidate
- AIP Template improvement candidate
- aiws-aip run improvement candidate
- Notebook note
- future backlog item
- task-local archive
- discard

It does not directly update Knowledge Hub.

---

## 12. Capture Inbox format

Recommended JSONL item:

```json
{
  "id": "C-001",
  "type": "wiki_update_candidate",
  "title": "Add missing lookup key rule for Japanese aliases",
  "content": "During review, AI repeatedly needed Japanese alias to find F02 source.",
  "status": "captured",
  "suggested_target": "wiki_meta",
  "source_refs": ["SRC-RD-F02-SEARCHROOM"],
  "task_refs": ["TASK-20260426-workspace-boundary"],
  "notes": "Triaged at close."
}
```

Recommended status:

```text
captured / triaged / promoted / archived / discarded / deferred / retained_local
```

---

## 13. Runtime flow

```text
HUMAN task request
  ↓
Create or identify Workspace if task is non-trivial / multi-step
  ↓
Record task summary and current state
  ↓
Collect selected context / sources / notes
  ↓
Create or update Working AIP if execution is non-trivial
  ↓
Execute task via Working AIP / aiws-aip run
  ↓
Update Workspace with progress, findings, drafts, feedback, blockers
  ↓
Queue unplanned follow-up subtasks/actions when needed
  ↓
Classify findings/notes/Capture Inbox/Queue at task close
  ↓
Promote / move / archive / discard
```

Short form:

```text
request → workspace → working aip → execution → workspace update → classify/close
```

---

## 14. Workspace to Working AIP handoff

Core rule:

```text
Workspace can feed Working AIP.
Workspace cannot replace Working AIP.
```

Workspace context should be reflected into Working AIP when it affects:
- task intent
- scope
- expected output
- selected source/context references
- Task Lens / mode
- execution steps
- guardrails / constraints
- open questions / blockers
- done criteria
- source representation limitations
- candidate/feedback constraints relevant to execution

The handoff is selective, not a full dump.

---

## 15. Workspace to Knowledge Promotion Candidate

Core rule:

```text
Workspace can collect candidates.
Controlled Knowledge Promotion decides whether/how candidates are promoted.
```

Candidate collection is not promotion.

At task close, classify Workspace items as:
- lightweight maintenance
- controlled_promotion_candidate
- future_backlog_candidate
- notebook_note
- task_local_archive
- discard

---

## 16. Workspace vs Notebook

Workspace is task/session-bound.

Notebook is personal/local note space that may outlive one task.

Move/copy to Notebook when:
- note is personal/local
- not suitable for Knowledge Hub
- may be useful later
- not tied only to current task
- HUMAN wants to keep it

---

## 17. Minimal lifecycle

MVP state model:

```text
not_created → active → paused → closing → closed → archived
```

This is not a full lifecycle/versioning framework.

---

## 18. Close classification

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

Before close, check:
- all blocking Runtime Queue items resolved or deferred
- Capture Inbox items triaged — or explicitly **deferred to the Capture Backlog with a reason** (CR-AIWS-2026-08-125); `aiws-aip run close` refuses to flip an AIP to `done` while any row is still `captured`
- final outputs linked
- HUMAN acceptance/cancel status recorded
- unresolved open points recorded
- archive location recorded

---

## 19. Anti-confusion boundaries

Workspace is not:
- Working AIP
- Knowledge Hub
- Notebook
- source of truth
- canonical output folder
- full archive/registry
- automatic promotion queue
- raw chat transcript
- source artifact storage

Core rule:

```text
Workspace is useful because it is active and flexible.
It must stay bounded so it does not become a dumping ground or substitute for other AIWS layers.
```

---

## 20. Deferred items

Deferred:
- full Workspace lifecycle/versioning
- Workspace file naming/version rules
- UI/form for Workspace
- multi-user workspace governance
- real-time collaboration model
- full archive/retention policy
- permission/security model
- integration with execution telemetry
- full Notebook promotion model
- Workspace automation support
- full queue scheduler/automation
- Capture Inbox triage UI/tooling

---

## 21. Conclusion

Central stance:

```text
Workspace is active task/session working context.
Workspace supports continuity and current-state management.
Workspace can feed Working AIP, Knowledge Promotion, Notebook, and canonical outputs.
Workspace does not replace Working AIP, Knowledge Hub, Notebook, source artifacts, or canonical docs.
Workspace Runtime Queue stores current-task follow-up work so AI can stay focused and process emergent subtasks sequentially.
Capture Inbox stores possible future-value findings before triage.
At task close, Workspace content should be classified.
```

---

# v0.9.11 Minimal Runtime Testing addendum

Workspace runtime sanity checks:

- Workspace exists when task is non-trivial/multi-step.
- Workspace holds context, not execution authority.
- Runtime Queue captures unplanned current-task follow-up work.
- Blocking queue items are resolved/deferred before close.
- Capture Inbox stores future-value items before triage.
- Capture Inbox items are not auto-promoted.
- Final output exists if task is marked done.
- Close/archive notes classify Workspace content.

Anti-pattern:

```text
Workspace should not become Working AIP, Knowledge Hub, Notebook, source of truth, or dumping ground.
```

---

# v0.9.12 Runtime Tooling Alignment addendum

Version-up rename:

```text
02_investigation_queue.jsonl
  ↓
02_runtime_queue.jsonl
```

New Workspace templates/workspaces use:

```text
02_runtime_queue.jsonl
```

Existing old workspaces with:

```text
02_investigation_queue.jsonl
```

remain readable as legacy alias / migration source.

Rule:

```text
Runtime Queue = do/check/update later for current task.
Capture Inbox = capture possible future value for later triage.
```
