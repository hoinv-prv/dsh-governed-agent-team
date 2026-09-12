# Workspace Boundary Samples Appendix

Status: Canonical appendix  
Version: v0.9.10  
Date: 2026-04-26  
Source: Workspace Boundary Minimal Spec Sprint — WSB-08

---

## Purpose

This appendix provides sample Workspace structures and flows.

These examples demonstrate how Workspace should support active task continuity without replacing Working AIP, Knowledge Hub, Notebook, source artifacts, or canonical docs.

---

# AIWS_WSB-08_SAMPLE_WORKSPACE_STRUCTURE_AND_FLOWS_v1

Status: Draft  
Sprint: Workspace Boundary Minimal Spec Sprint  
Baseline: AI Work System MVP v0.9.9

---

## 1. Purpose

WSB-08 provides sample Workspace structures and flows.

The goal is to demonstrate how Workspace should be used without confusing it with Working AIP, Knowledge Hub, Notebook, or canonical docs.

---

## 2. Sample Workspace structure

```markdown
# Workspace — <task/session name>

## 1. Workspace Identity
- workspace_id:
- task/session name:
- status: active / paused / closing / closed / archived
- created_at:
- updated_at:
- related sprint/component:
- active Working AIP:

## 2. Task Summary
- HUMAN request:
- interpreted intent:
- expected output:
- scope note:

## 3. Current State
- current step:
- completed:
- next action:
- blockers:

## 4. Selected Sources / Context
| Ref | Type | Role | Status | Usage / Limitation |
|---|---|---|---|---|

## 5. Task Lens / Mode
- selected lens/mode:
- reason:
- expansion note:

## 6. Runtime Queue
- Queue file: `02_runtime_queue.jsonl`
- Compatibility alias: `02_investigation_queue.jsonl`
- Purpose: follow-up work items for current task

## 7. Open Questions / Blockers
- ...

## 7. Intermediate Findings
- ...

## 8. Draft Outputs / Working Files
- ...

## 9. Feedback / Fix Notes
- ...

## 10. Capture Inbox / Candidates for Lookback / Promotion
- Capture Inbox file: `08_capture_inbox.jsonl`

| Candidate | Type | `candidate_kind` | `improvement_scope` | Status | Suggested target |
|---|---|---|---|---|---|

## 11. Next Actions
- ...

## 12. Close / Archive Notes
- final output:
- accepted by HUMAN:
- candidates created:
- notes moved/discarded:
- archive location:
```

This is a recommended structure. Small tasks may use a lighter structure.

---

# 3. Sample Flow 1 — Sprint design task

## 3.1. Context

HUMAN says:

```text
Ok, hãy bắt đầu sprint.
```

Task:
- new sprint
- multi-step design
- Workspace useful
- Working AIP may be needed before execution/package

## 3.2. Workspace

```markdown
# Workspace — Workspace Boundary Minimal Spec Sprint

## Workspace Identity
- workspace_id: WS-WORKSPACE-BOUNDARY-2026-04-26
- status: active
- related sprint/component: Workspace Boundary Minimal Spec
- active Working AIP: not created yet / to be created if execution becomes non-trivial

## Task Summary
- HUMAN request: Start Workspace Boundary Minimal Spec Sprint.
- interpreted intent: define minimal Workspace boundary for AIWS MVP.
- expected output: WSB docs, close review, package after HUMAN confirmation.

## Current State
- completed: WSB-01~WSB-03 drafted
- current step: WSB-04 runtime flow
- next action: WSB-05 handoff rule
- blockers: none

## Selected Sources / Context
| Ref | Type | Role | Status | Usage / Limitation |
|---|---|---|---|---|
| AIWS v0.9.9 | baseline package | current canonical baseline | active | use as design baseline |
| Working AIP Connection sprint | previous sprint | boundary dependency | closed | Workspace feeds Working AIP |

## Candidates for Lookback / Promotion
- none yet
```

## 3.3. Correct behavior

Workspace tracks sprint progress.  
It does not replace WSB docs or Working AIP.

---

# 4. Sample Flow 2 — Continuation task

## 4.1. HUMAN request

```text
Hãy tiếp tục nhé.
```

## 4.2. Runtime flow

```text
HUMAN continuation request
  ↓
identify current Workspace
  ↓
read Current State / Next Actions
  ↓
continue next WSB item
  ↓
update Workspace
```

## 4.3. Workspace update

```markdown
## Current State
- completed: WSB-01~WSB-04
- current step: WSB-05 Workspace to Working AIP Handoff Rule
- next action: WSB-06 Workspace to Knowledge Promotion Candidate Rule
- blockers: none
```

## 4.4. Guardrail

Do not infer a new task from “continue” if current Workspace context is clear.

If multiple active workspaces exist, ask/confirm.

---

# 5. Sample Flow 3 — Source-heavy review task

## 5.1. Task

Review Detail Design against Requirement and Basic Design.

## 5.2. Workspace

Workspace stores:
- selected RD/BD/DD sources
- current review status
- open findings
- draft review report pointer
- source representation issues
- follow-up candidates

## 5.3. Working AIP handoff

Workspace selected sources become Working AIP Context / Source References.

Workspace findings do not become final review findings until source-checked and represented in output.

---

# 6. Sample Flow 4 — Package creation task

## 6.1. Task

Create canonical package after sprint close.

## 6.2. Workspace role

Workspace tracks:
- baseline package
- target version
- canonical merge map
- changed files
- delta tracking folder
- output zip/report paths
- validation steps
- package creation issues

## 6.3. Boundary

Package output is not Workspace.

Workspace records package output pointer after creation.

---

# 7. Sample Flow 5 — Candidate collection after feedback

## 7.1. Task

AI creates document, HUMAN gives feedback, AI fixes, HUMAN accepts.

## 7.2. Workspace records

```markdown
## Feedback / Fix Notes
- HUMAN feedback: add source representation caution.
- Fix applied: WMI spec updated with caution.

## Candidates for Lookback / Promotion
| Candidate | Type | `candidate_kind` | `improvement_scope` | Status | Suggested target |
|---|---|---|---|---|---|
| Add source representation caution to template | AIP Template improvement | draft_candidate | future apply-back task |
```

## 7.3. Boundary

Candidate is not promoted automatically.

---

# 8. Sample Flow 6 — Personal idea during task

## 8.1. Situation

During task, HUMAN has idea unrelated to current sprint but useful later.

## 8.2. Workspace handling

Workspace can temporarily record:

```markdown
## Intermediate Findings
- Personal idea: consider a future UI dashboard for workspace states.
```

At close:
- move/copy to Notebook if HUMAN wants
- or future backlog candidate
- not Knowledge Hub by default

---

# 9. Sample Flow 7 — Source representation issue

## 9.1. Situation

Converted Excel markdown misses formulas.

## 9.2. Workspace records

```markdown
## Open Questions / Blockers
- source_representation_quality_issue: converted testcase markdown may omit formulas.

## Candidates for Lookback / Promotion
| Candidate | Type | `candidate_kind` | `improvement_scope` | Status | Suggested target |
|---|---|---|---|---|---|
| Improve Excel conversion guideline | source representation improvement | draft_candidate | conversion skill/guideline |
```

## 9.3. Boundary

If it blocks current task, reflect into Working AIP blocker.  
If reusable, create candidate.  
Do not treat Workspace note as verified source.

---

# 10. Cross-sample checklist

```markdown
- [ ] Workspace is task/session-bound
- [ ] Workspace records current state
- [ ] active Working AIP pointer is recorded if applicable
- [ ] selected sources/context are role-defined
- [ ] open questions/blockers are visible
- [ ] candidates are marked as candidates
- [ ] final outputs are linked, not stored only in Workspace
- [ ] task close classification is done
- [ ] Workspace is closed/archived when task completes
```

---

## 11. Conclusion

WSB-08 provides practical examples of Workspace usage.

Core lesson:

```text
Workspace is the working area for task continuity.
It supports but does not replace execution, knowledge, notebook, or canonical layers.
```

Next: WSB-09 Anti-Confusion Boundaries.


---

# 11. Sample Flow 8 — Capture Inbox triage

## 11.1. Situation

During a task, AI finds several potentially reusable observations:
- a missing Wiki Meta lookup key
- a repeated HUMAN feedback pattern
- a source representation issue
- a personal idea that may be useful later

## 11.2. Runtime capture

AI records them in:

```text
08_capture_inbox.jsonl
```

Example:

```json
{
  "id": "C-001",
  "type": "wiki_meta_update_candidate",
  "title": "Add Japanese alias lookup key for F02 SearchRoom",
  "content": "During review, source lookup failed until Japanese alias 会議室検索 was used.",
  "status": "captured",
  "suggested_target": "wiki_meta",
  "source_refs": ["SRC-RD-F02-SEARCHROOM"],
  "notes": "Triage at workspace close."
}
```

## 11.3. Close triage

At Workspace close:

| Capture item | Classification |
|---|---|
| missing lookup key | lightweight maintenance / Wiki Meta candidate |
| repeated HUMAN feedback | AIP Template improvement candidate |
| source representation issue | source representation improvement candidate |
| personal idea | Notebook note or future backlog |
| low-value note | discard |

## 11.4. Guardrail

Capture Inbox item is not promoted automatically.



---

# 12. Sample Flow 9 — Workspace Runtime Queue for emergent follow-up work

## 12.1. Situation

During a package creation task, AI is updating files and discovers follow-up work items:

- update MANIFEST after files are generated
- update CHANGELOG after canonical docs are changed
- verify delta tracking folder before zip
- check package report includes all added files

These were not all listed explicitly in the initial chat request.

## 12.2. Queue capture

AI writes follow-up work items into:

```text
02_runtime_queue.jsonl
```

Example item:

```json
{
  "id": "Q-002",
  "title": "Update CHANGELOG after canonical docs are changed",
  "status": "pending",
  "priority": "high",
  "type": "changelog_manifest_step",
  "reason": "CHANGELOG must reflect canonical package changes before close.",
  "origin": "package creation execution",
  "next_action": "After docs are updated, append v0.9.x changelog entry.",
  "blocking": true,
  "result": ""
}
```

## 12.3. Processing loop

AI continues the current file update step.

At checkpoint:
1. Review pending high-priority queue items.
2. Process CHANGELOG and MANIFEST updates.
3. Mark queue items resolved.
4. Reflect completion in Workspace close notes.

## 12.4. Guardrail

Runtime Queue item is not a Knowledge Promotion Candidate by default.

If queue processing reveals reusable value, create or copy a separate Capture Inbox item.
