# Wiki Source Maintenance / Impact Detection Spec MVP

Status: Canonical MVP spec  
Version: v0.9.14  
Date: 2026-04-26  
Source sprint: Wiki Source Maintenance / Impact Detection Sprint

---

## 1. Purpose

This spec defines the minimal source maintenance flow for Wiki / Knowledge Hub.

The goal is to keep Wiki Meta / Index aligned with source artifacts when source changes, while preserving AIWS guardrails.

---

## 2. Central stance

```text
AIWS can detect source changes, evaluate impact, route maintenance candidates,
create refresh drafts, review/apply safely, and log rollback trace — without auto-promotion.
```

---

## 3. Core flow

```text
source artifact changes
  ↓
detect changed source
  ↓
evaluate impact
  ↓
route result:
    - Runtime Queue if current task action
    - Capture Inbox if future-value candidate
    - refresh draft if update likely needed
  ↓
review
  ↓
apply if approved
  ↓
update log / rollback trace
  ↓
rebuild index if needed
```

---

## 4. Boundary rules

### 4.1. Source maintenance signal is not approval

```text
Source change detection is signal.
Impact evaluation is recommendation.
Refresh is draft by default.
Apply is explicit and logged.
Promotion is controlled separately.
```

### 4.2. Candidate routing depends on current-task blocking

```text
If source maintenance affects the current task, use Runtime Queue.
If it has future value but does not block now, use Capture Inbox.
Neither route means approval or promotion.
```

### 4.3. Refresh is draft/review/apply

```text
Refresh draft may prepare an update,
but only explicit reviewed apply changes canonical Wiki Meta.
```

### 4.4. Applied updates must be traceable

```text
Applied Wiki maintenance updates must be traceable and reasonably reversible.
```

### 4.5. Source representation issue must be routed visibly

```text
Source representation issues can block source verification and must be routed visibly.
```

---

## 5. Changed Source Detection

Detection answers:

```text
What changed?
Which source_id is affected?
Do we need impact evaluation?
```

Recommended change types:

```text
added
modified
deleted
moved
missing
unchanged
unknown
```

Detection output should include:

```yaml
source_id:
change_type:
change_signal:
artifact_locator:
previous_artifact_locator:
fingerprint_old:
fingerprint_new:
requires_impact_evaluation:
reason:
recommended_next_action:
candidate_type:
maintenance_model_version: wsm_v1
```

Detection does not update Wiki Meta / Index directly.

---

## 6. Impact Evaluation Result Model

Recommended impact levels:

```text
none
low
medium
high
unknown
```

Recommended recommendations:

```text
no_action
review_optional
review_required
refresh_meta_draft
create_update_candidate
create_source_representation_issue
human_check_required
blocked_missing_source
blocked_source_representation_issue
defer_to_future_backlog
```

Forbidden recommendation terms:

```text
approve_update
auto_promote
auto_apply
```

Recommended result model:

```yaml
source_id:
title:
source_type:
change_type:
impact_level:
recommendation:
candidate_type:
suggested_target:
reason:
next_action:
review_required:
blocking_current_task:
source_representation_status:
source_representation_caution:
affected_meta_locator:
affected_index_locator:
affected_artifact_locator:
related_sources:
created_at:
evaluated_by:
maintenance_model_version: wsm_v1
```

---

## 7. Candidate Routing

Runtime Queue is for current-task action.

Capture Inbox is for future-value candidate.

Use Runtime Queue when:
- current task output depends on changed source
- source verification cannot continue
- source representation issue blocks evidence
- source artifact is missing and current task depends on it

Use Capture Inbox when:
- update has future value but does not block current task
- source routing/search trigger should be improved later
- representation issue should be fixed later
- source maintenance can be deferred

---

## 8. Refresh / Review / Apply

Default refresh behavior:

```text
write refresh draft
do not overwrite existing meta
```

Apply only when:
- HUMAN or approved process confirms
- change summary exists
- backup/rollback hint exists
- representation limitation remains visible
- update log is written

Apply is not promotion unless Controlled Knowledge Promotion approves.

---

## 9. Update Log / Rollback Trace

Minimum log fields:

```yaml
log_id:
timestamp:
action:
source_id:
target_artifact:
old_locator:
new_locator:
change_summary:
reason:
impact_level:
review_decision:
applied_by:
rollback_hint:
maintenance_model_version:
```

Recommended log file:

```text
.ai-work/wiki_sources/maintenance_log.jsonl
```

For MVP this can be JSONL, package report, changelog, or delta tracking.

---

## 10. Source Representation Issue Handling

If source representation quality can affect source verification, the issue must be visible and routed.

Possible statuses:

```text
complete
partial
needs_review
failed
unknown
not_applicable
```

If representation issue blocks evidence:

```yaml
impact_level: high
recommendation: blocked_source_representation_issue
candidate_type: source_representation_issue
review_required: true
blocking_current_task: true
```

AI must not claim full source verification when representation is partial/unknown/failed.

---

## 11. Migration Compatibility

New maintenance outputs should follow WSM model.

Old artifacts remain readable/warning-compatible.

```text
Add WSM maintenance model forward,
keep old artifacts readable,
and never treat migration as approval.
```

---

## 12. Tool alignment summary

| Tool | WSM alignment |
|---|---|
| detect_changed_wiki_sources.py | changed source signal + WSM fields |
| evaluate_wiki_source_impact.py | impact/recommendation/candidate result |
| refresh_wiki_source_meta.py | draft by default, apply explicit, log/rollback |
| build_wiki_source_index.py | index projection rebuild trace |
| lint_wiki.py | maintenance log / representation / promotion checks |
| Runtime Queue | current-task maintenance blockers |
| Capture Inbox | future-value maintenance candidates |

---

## 13. Non-goals

This spec does not define:
- full metadata registry
- semantic impact scoring
- auto-promotion
- auto-update Knowledge Hub
- full CI/testing harness
- full source conversion framework
- Graphify/call graph integration
- production observability

---

## 14. Conclusion

Wiki Source Maintenance / Impact Detection closes the minimal loop between source changes and Wiki maintenance while preserving review, traceability, and no-auto-promotion boundaries.

---

# v0.9.15 Source Representation addendum

Source representation issues are first-class maintenance signals.

If source representation is partial/needs_review/failed/unknown and evidence depends on it:
- impact may be high/unknown
- review_required should be true
- current-task blocker routes to Runtime Queue
- non-blocking improvement routes to Capture Inbox
