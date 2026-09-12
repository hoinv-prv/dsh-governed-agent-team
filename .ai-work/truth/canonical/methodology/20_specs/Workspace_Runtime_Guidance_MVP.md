# Workspace Runtime Guidance MVP

Status: Canonical runtime guidance  
Version: v0.9.10  
Date: 2026-04-26

---

## 1. Purpose

This document provides runtime guidance for using Workspace in AIWS.

Workspace is active task/session working context.

---

## 2. Default runtime flow

```text
request → workspace → working aip → execution → workspace update → classify/close
```

Detailed:

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

---

## 3. When Workspace is needed

Use Workspace for:
- multi-step task
- source-heavy task
- interrupted/continued task
- design/review/package task
- sprint-based task
- task with multiple outputs
- task likely to create findings/candidates
- task requiring state tracking

Workspace may be skipped for trivial one-off tasks.

---

## 4. Runtime Queue rule

Use:

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

## 5. Capture Inbox rule

Use:

```text
08_capture_inbox.jsonl
```

Rule:

```text
Capture first, curate later.
```

Capture Inbox stores future-value findings/ideas/candidates before triage.

Capture Inbox item is not yet a reviewed Knowledge Promotion Candidate.

---

## 6. Queue vs Capture Inbox

```text
Runtime Queue = do/check/update later for current task.
Capture Inbox = capture possible future value for later triage.
```

Examples:
- update manifest after package files are created → Runtime Queue
- check BD F02 before finalizing review → Runtime Queue
- add Japanese alias rule to Wiki Meta guideline → Capture Inbox
- repeated HUMAN feedback may improve AIP Template → Capture Inbox

---

## 7. Workspace to Working AIP

Workspace can feed Working AIP.

Workspace cannot replace Working AIP.

Reflect execution-relevant Workspace context into Working AIP:
- task intent
- scope
- source references
- Task Lens/mode
- execution steps
- guardrails
- blockers
- done criteria

---

## 8. Close checklist

```markdown
## Workspace Close Checklist

- [ ] final output linked?
- [ ] HUMAN acceptance/cancel status recorded?
- [ ] blocking Runtime Queue items resolved or deferred?
- [ ] Capture Inbox items triaged?
- [ ] candidates classified?
- [ ] notes moved/archived/discarded?
- [ ] unresolved open points recorded?
- [ ] archive location recorded?
```

---

## 9. Anti-confusion rule

Workspace is not:
- Working AIP
- Knowledge Hub
- Notebook
- source of truth
- canonical output folder
- automatic promotion queue
- raw chat transcript
- source artifact storage

Workspace is active task/session working context.

---

# v0.9.11 Minimal Runtime Testing addendum

Before closing Workspace:

```markdown
- [ ] final output linked?
- [ ] HUMAN acceptance/cancel status recorded?
- [ ] blocking Runtime Queue items resolved or deferred?
- [ ] Capture Inbox items triaged?
- [ ] candidates classified?
- [ ] notes moved/archived/discarded?
- [ ] unresolved open points recorded?
- [ ] archive location recorded?
```

Runtime testing stance:

```text
Sanity check before close.
Deterministic guardrail before package.
HUMAN review before important decisions.
```

---

# v0.9.12 Runtime Tooling Alignment addendum

Runtime Queue file:

```text
02_runtime_queue.jsonl
```

Legacy alias:

```text
02_investigation_queue.jsonl
```

Runtime guidance:
- new workspaces should use `02_runtime_queue.jsonl`
- tools should still read legacy alias for old workspaces
- if both files exist, tools should prefer `02_runtime_queue.jsonl`
- old file should not be silently deleted in existing workspaces

---

# v0.9.14 Wiki Source Maintenance addendum

Candidate routing rule:

```text
If source maintenance affects the current task, use Runtime Queue.
If it has future value but does not block now, use Capture Inbox.
Neither route means approval or promotion.
```

Runtime Queue item type examples:
- `wiki_meta_check`
- `source_representation_check`

Capture Inbox item type examples:
- `wiki_meta_update_candidate`
- `source_representation_issue`

---

# v0.9.15 Source Representation addendum

Representation issue routing:

```text
Representation issues that block current source verification go to Runtime Queue.
Non-blocking reusable improvement candidates go to Capture Inbox.
```

Runtime Queue type example:
- `source_representation_check`

Capture Inbox type example:
- `source_representation_issue`

---

# v0.9.16 Active Step Context / Traceability addendum

Workspace is the persistence layer for:
- Step Output Artifacts
- Step Decision / Conclusion Artifacts
- Decision Discussion Trace
- Runtime Queue
- Capture Inbox
- task-local notes/logs

ASC displays the current-step slice of Workspace context. ASC does not store or replace persisted step outputs/traces.
