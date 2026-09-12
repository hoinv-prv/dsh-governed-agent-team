# Runtime Tooling Alignment Patch Guide MVP

Status: Canonical implementation guide  
Version: v0.9.12  
Date: 2026-04-26  
Source: RTA-09 Minimal Implementation Plan / Patch Map

---

## Purpose

This guide records the minimal patch map for Runtime Tooling Alignment.

The package v0.9.12 applies P0 and part of P1:
- workspace template queue rename
- init_workspace.py new queue file alignment
- lint_workspace.py new/legacy queue compatibility and Capture Inbox enum extension
- lint_all.py workspace aggregation alignment
- run_aip.py status visibility for queue/capture

---

# AIWS_RTA-09_MINIMAL_IMPLEMENTATION_PLAN_AND_PATCH_MAP_v1

Status: Draft  
Sprint: Runtime Tooling Alignment Sprint  
Baseline: AI Work System MVP v0.9.11

---

## 1. Purpose

RTA-09 defines a minimal implementation plan and patch map for Runtime Tooling Alignment.

This is not actual implementation yet.  
It is a clear patch plan for later package/tool updates.

---

## 2. Implementation stance

```text
Patch minimally.
Preserve compatibility.
Avoid broad rewrite.
```

This sprint should produce enough detail that implementation can be done safely in a later execution/package update step.

---

## 3. Patch priority

Recommended patch priority:

```text
P0 — must align before next package rollout if possible
P1 — should align soon
P2 — future alignment candidate
```

---

## 4. P0 patches

### P0-01. Workspace template rename

Target:

```text
payload/workspace_templates/task_workspace_template/
```

Patch:

```text
rename 02_investigation_queue.jsonl → 02_runtime_queue.jsonl
```

Rules:
- new template should not create `02_investigation_queue.jsonl`
- old file remains readable by tools as legacy alias
- update template task brief if it mentions queue file
- keep `08_capture_inbox.jsonl`

Related docs:
- RTA-06
- RTA-07

---

### P0-02. init_workspace.py uses new queue file

Target:

```text
payload/tooling/init_workspace.py
```

Patch:
- create `02_runtime_queue.jsonl` for new workspace
- do not create `02_investigation_queue.jsonl` for new workspace
- preserve existing old workspace files
- avoid silent deletion
- if old file exists during init/resume, show migration info if tool supports

---

### P0-03. lint_workspace.py accepts new + legacy queue file

Target:

```text
payload/tooling/lint_workspace.py
```

Patch:
- primary: `02_runtime_queue.jsonl`
- legacy alias: `02_investigation_queue.jsonl`
- if both exist, prefer new and warn when old has active/non-empty data
- if only old exists, Info/Warning, not Error
- if neither exists in non-trivial workspace, Warning/Error in strict

---

### P0-04. lint_workspace.py supports dual queue schema

Target:

```text
payload/tooling/lint_workspace.py
```

Patch:
- detect old investigation schema
- detect new runtime queue schema
- validate common required fields
- do not fail old schema only because it is old
- warn/info for legacy schema
- Error on invalid JSONL / duplicate IDs / missing ID / missing status

---

### P0-05. Capture Inbox enum extension

Target:

```text
payload/tooling/lint_workspace.py
```

Patch:
- preserve old types
- add new candidate types:
  - finding_candidate
  - wiki_meta_update_candidate
  - aip_template_improvement_candidate
  - run_aip_improvement_candidate
  - guideline_improvement_candidate
  - source_representation_issue
  - future_backlog_candidate
  - notebook_note_candidate
- preserve old status values
- add suggested_target values from canonical spec
- unknown type: Warning normal / Error or Warning in strict

---

## 5. P1 patches

### P1-01. run_aip.py status queue/capture visibility

Target:

```text
payload/tooling/run_aip.py
```

Patch:
- detect active queue file
- show legacy queue usage
- count pending/blocking/blocked/deferred items
- show Capture Inbox captured/untriaged/deferred counts
- show final output exists/missing if done
- warn if both queue files exist with active content

Do not:
- execute semantic task
- auto-resolve queue
- auto-promote capture items

---

### P1-02. lint_all.py aggregation labels

Target:

```text
payload/tooling/lint_all.py
```

Patch:
- include updated workspace lint results
- include Wiki lint results
- show Runtime Queue / Capture Inbox summary if available
- preserve text/json output
- preserve strict mode

---

### P1-03. Skill docs alignment

Targets:

```text
payload/skills/aiws-aip/SKILL.md
payload/skills/aiws-lint/SKILL.md
payload/skills/aiws-aip/SKILL.md
payload/skills/aiws-aip/SKILL.md
payload/skills/aiws-aip/SKILL.md
```

Patch:
- mention `02_runtime_queue.jsonl` as official new file
- mention old alias read/migrate behavior
- clarify aiws-aip run not semantic executor
- clarify lint not reviewer
- clarify queue/capture boundary

---

### P1-04. Workspace template README/task brief update

Target:

```text
payload/workspace_templates/task_workspace_template/00_task_brief.md
```

Patch:
- add note:
  - Runtime Queue: `02_runtime_queue.jsonl`
  - Legacy queue alias: `02_investigation_queue.jsonl`
  - Capture Inbox: `08_capture_inbox.jsonl`
- keep brief short

---

## 6. P2 patches / future candidates

### P2-01. lint_wiki alignment

Target:

```text
payload/tooling/lint_wiki.py
```

Future patch:
- recognize new source representation caution/status fields if adopted
- strengthen meta/index structural checks
- keep lint_wiki as guardrail, not reviewer

May belong to future Wiki Tooling Alignment Sprint.

---

### P2-02. Wiki change/impact tools candidate flow

Targets:

```text
detect_changed_wiki_sources.py
evaluate_wiki_source_impact.py
refresh_wiki_source_meta.py
```

Future patch:
- convert change/impact into candidate signal
- connect to Controlled Knowledge Promotion
- draft/review/apply/log flow

Defer to future Wiki Source Maintenance / Impact Detection sprint.

---

### P2-03. Active Step Context minimal spec/tooling alignment

Targets:

```text
build_active_step_context.py
set_current_step.py
run_aip.py
```

Future patch:
- define ASC content boundary
- avoid overloading ASC
- include only relevant queue/capture pointers
- rebuild/staleness rules

Defer to future Active Step Context Minimal Spec Sprint.

---

## 7. Migration patch plan

When applying version-up:

1. Update template folder:
   - rename queue file to `02_runtime_queue.jsonl`
2. Update init tool:
   - create new queue file
3. Update lint:
   - read both old/new queue names
4. Update aiws-aip run status:
   - show active queue file and legacy warning
5. Update skill docs:
   - mention new official file + old alias
6. Update package metadata:
   - README / CHANGELOG / MANIFEST / baseline note / report
7. Preserve delta tracking:
   - old-to-new rename record

---

## 8. Compatibility test checklist

After patching, test with:

### New workspace

```markdown
- [ ] init creates `02_runtime_queue.jsonl`
- [ ] init creates `08_capture_inbox.jsonl`
- [ ] no `02_investigation_queue.jsonl` created by default
- [ ] lint passes empty queue/capture
- [ ] aiws-aip run status shows new queue
```

### Old workspace

```markdown
- [ ] old workspace with only `02_investigation_queue.jsonl` is readable
- [ ] lint warns/info but does not fail only because old name exists
- [ ] aiws-aip run status shows legacy alias
- [ ] no silent deletion/migration
```

### Mixed workspace

```markdown
- [ ] both old/new files detected
- [ ] new file preferred
- [ ] warning if old file has active/non-empty items
```

### Capture Inbox

```markdown
- [ ] old types accepted
- [ ] new types accepted
- [ ] invalid JSONL errors
- [ ] duplicate ID errors
```

---

## 9. Implementation non-goals

Do not implement:
- full CI
- semantic lint
- telemetry
- automatic migration without confirmation
- automatic Knowledge Hub promotion
- full Wiki source maintenance
- full Active Step Context redesign
- package governance overhaul

---

## 10. Conclusion

RTA-09 provides a minimal patch map.

Recommended first implementation target:

```text
workspace template + init_workspace.py + lint_workspace.py
```

Then:

```text
run_aip.py status + lint_all aggregation + skill docs
```

Deep Wiki tooling and ASC redesign should be split to future sprints.
