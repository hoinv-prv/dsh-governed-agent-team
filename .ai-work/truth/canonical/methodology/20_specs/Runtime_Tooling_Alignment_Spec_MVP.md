# Runtime Tooling Alignment Spec MVP

Status: Canonical MVP spec  
Version: v0.9.12  
Date: 2026-04-26  
Source sprint: Runtime Tooling Alignment Sprint

---

## 1. Purpose

This spec defines Runtime Tooling Alignment for AI Work System MVP.

The goal is to align existing runtime tools/templates with latest canonical specs while preserving baseline compatibility and avoiding unnecessary redesign.

---

## 2. Definition

Runtime Tooling Alignment is:

```text
the process of aligning existing runtime tools/templates with latest canonical AIWS specs
while preserving compatibility with baseline package behavior where reasonable.
```

---

## 3. Central stance

```text
Make tools/templates align with latest canonical specs.
Preserve baseline compatibility.
Avoid unnecessary redesign.
```

---

## 4. Baseline rule

```text
v0.9.2 is baseline/reference, not design direction.
```

Use baseline to:
- preserve good patterns
- reduce migration cost
- keep compatibility where aligned
- avoid unnecessary field/file changes

Do not use baseline to:
- override accepted canonical specs
- block necessary improvements
- keep misleading names forever

---

## 5. General version-up rename rule

If a baseline file and latest canonical file have the same purpose but different names, and the latest canonical name is more accurate, then version-up should rename to the latest canonical name.

Rule:

```text
same purpose + better latest canonical name
  → version-up rename to latest name
  → old name becomes legacy alias / migration source
```

The old name is not the official file for new templates/workspaces.

---

## 6. Runtime Queue rename

Old file:

```text
02_investigation_queue.jsonl
```

New official file:

```text
02_runtime_queue.jsonl
```

Decision:

```text
02_investigation_queue.jsonl
  ↓ version-up rename
02_runtime_queue.jsonl
```

Reason:
- the queue is not only for investigation
- it is current-task runtime follow-up work for any task
- `runtime_queue` better reflects canonical meaning

---

## 7. Runtime Queue file behavior

| Situation | Tool behavior |
|---|---|
| new workspace/template generation | create `02_runtime_queue.jsonl` |
| only `02_runtime_queue.jsonl` exists | use it |
| only `02_investigation_queue.jsonl` exists | use it as legacy alias; warn/info and suggest migration |
| both exist | prefer `02_runtime_queue.jsonl`; warn if old file has active/non-empty data |
| neither exists | create `02_runtime_queue.jsonl` for new workspace; lint warning/error depending strictness |

Do not silently delete old files in existing workspaces.

---

## 8. Runtime Queue schema compatibility

Tools should support:
- legacy investigation queue schema
- new runtime queue schema

Legacy fields may include:

```text
id, kind, target, question, why, priority, status
```

New fields may include:

```text
id, title, status, priority, type, reason, source_refs, origin,
next_action, blocking, created_at, updated_at, result
```

Validation stance:
- invalid JSONL = Error
- duplicate ID = Error
- missing id/status = Error
- old schema = Info/Warning, not Error
- unknown extension fields = allowed

---

## 9. Capture Inbox alignment

File remains:

```text
08_capture_inbox.jsonl
```

Tools should support old and new candidate types.

Additional canonical types include:
- finding_candidate
- wiki_meta_update_candidate
- aip_template_improvement_candidate
- run_aip_improvement_candidate
- guideline_improvement_candidate
- source_representation_issue
- future_backlog_candidate
- notebook_note_candidate

Capture Inbox rule:

```text
Capture first, curate later.
Capture Inbox item is not yet a reviewed Knowledge Promotion Candidate.
```

---

## 10. aiws-aip run alignment

Core rule:

```text
aiws-aip run should prepare/point runtime context and expose status/readiness.
It should not replace task reasoning, source verification, semantic review, or HUMAN confirmation.
```

Runtime status should show:
- AIP / Working AIP
- Workspace
- Active Step Context
- Runtime Queue file and counts
- Capture Inbox counts
- draft/final output state
- close/lookback warnings where possible

---

## 11. lint/check alignment

Core rule:

```text
Lint detects deterministic structural/runtime issues.
Lint does not replace HUMAN review, semantic correctness judgment, or source verification.
```

Severity:

```text
Error = must fix before execution/close/package.
Warning = should review before merge/finalize.
Info = helpful observation, not blocking.
```

---

## 12. Workspace template alignment

New workspace template uses:

```text
02_runtime_queue.jsonl
08_capture_inbox.jsonl
```

New template does not create:

```text
02_investigation_queue.jsonl
```

Old workspace with `02_investigation_queue.jsonl` remains readable as legacy alias.

---

## 13. Wiki tooling boundary

Current Runtime Tooling Alignment includes only minimal Wiki runtime guardrail alignment.

Deep Wiki Tooling Alignment is future sprint scope.

Preserve:
- index-first lookup
- meta is routing, not final evidence
- lint_wiki is guardrail, not reviewer
- refresh is draft/review/apply
- change/impact tools are signal, not approval

---

## 14. Implementation stance

```text
Patch minimally.
Preserve compatibility.
Avoid broad rewrite.
```

Recommended first implementation target:

```text
workspace template + init_workspace.py + lint_workspace.py
```

---

## 15. Future candidates

- Wiki Tooling Alignment Sprint
- Wiki Source Maintenance / Impact Detection Sprint
- Active Step Context Minimal Spec Sprint
- Controlled Update Pattern Sprint
- Source Representation / Conversion Integration Sprint
- Tooling Safety Policy Sprint
- Manual Runtime Regression Pack Sprint
- Automated Test Harness Sprint

---

## 16. Conclusion

Runtime Tooling Alignment closes the gap between canonical specs and actual runtime tools/templates.

Central rule:

```text
Latest canonical specs define the direction.
Baseline tools/templates provide compatibility and good implementation patterns.
Version-up aligns names/schemas carefully without unnecessary breakage.
```

---

# v0.9.13 Wiki Tooling Alignment addendum

Runtime Tooling Alignment now includes Wiki tooling alignment at MVP level.

Applied boundaries:
- lookup routes, source verifies
- refresh drafts, apply explicit
- detect/evaluate signals, not approval
- lint_wiki checks deterministic structure/boundary risks
- migration aligns structure/metadata, not approval
