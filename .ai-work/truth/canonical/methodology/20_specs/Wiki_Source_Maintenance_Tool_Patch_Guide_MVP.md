# Wiki Source Maintenance Tool Patch Guide MVP

Status: Canonical implementation guide  
Version: v0.9.14  
Date: 2026-04-26  
Source: WSM-08 Minimal Tool Patch Map

---

## Purpose

This guide records the minimal patch map for Wiki Source Maintenance / Impact Detection.

The package v0.9.14 applies P0 and part of P1:
- detect_changed_wiki_sources.py result model alignment
- evaluate_wiki_source_impact.py WSM result model
- refresh_wiki_source_meta.py draft/review/apply trace
- build_wiki_source_index.py rebuild trace
- lint_wiki.py maintenance checks
- skill guidance updates

---

# AIWS_WSM-08_MINIMAL_TOOL_PATCH_MAP_v1

Status: Draft  
Sprint: Wiki Source Maintenance / Impact Detection Sprint  
Baseline: AI Work System MVP v0.9.13

---

## 1. Purpose

WSM-08 defines a minimal tool patch map for Wiki Source Maintenance / Impact Detection.

This is a planning document for implementation/package update. It does not require all patches to be implemented in the design sprint.

---

## 2. Implementation stance

```text
Patch minimally.
Reuse v0.9.13 tools.
Do not create auto-promotion or auto-update behavior.
```

---

## 3. Target tools

Primary tools:

```text
detect_changed_wiki_sources.py
evaluate_wiki_source_impact.py
refresh_wiki_source_meta.py
build_wiki_source_index.py
lint_wiki.py
```

Secondary tools/skills:

```text
lookup_wiki_source.py
build_wiki_source_meta.py
aiws-wiki lookup skill
aiws-wiki refresh-meta skill
aiws-wiki build-meta skill
aiws-lint skill
```

---

## 4. P0 patches

### P0-01. detect_changed_wiki_sources.py result model alignment

Patch:
- output change_type
- output requires_impact_evaluation
- output reason
- output source_representation_status/caution if available
- output runtime_boundary
- output recommended_next_action

Do not:
- refresh meta automatically
- apply update automatically
- approve anything

---

### P0-02. evaluate_wiki_source_impact.py WSM result model

Patch:
- output WSM impact model fields:
  - source_id
  - change_type
  - impact_level
  - recommendation
  - candidate_type
  - suggested_target
  - reason
  - next_action
  - review_required
  - blocking_current_task
  - affected_meta_locator
  - affected_index_locator
  - affected_artifact_locator
- avoid forbidden recommendation terms:
  - approve_update
  - auto_promote
  - auto_apply

---

### P0-03. refresh_wiki_source_meta.py draft/review/apply trace

Patch:
- default output is draft
- draft includes review_status
- preserve representation/value/authority fields
- apply requires explicit flag
- apply creates backup/old locator
- apply emits change summary / rollback hint where possible

---

### P0-04. lint_wiki.py maintenance checks

Patch:
- warn if approved/applied meta lacks review/update trace
- warn if representation issue lacks caution/review_required
- warn if candidate/draft appears as approved
- warn if index appears stale or bloated
- recognize WSM maintenance log fields if present

---

## 5. P1 patches

### P1-01. build_wiki_source_index.py rebuild trace

Patch:
- when index rebuilt in maintenance context, output changed count / source ids
- preserve index as projection
- optionally create index rebuild log entry

---

### P1-02. Maintenance log helper

Potential new helper:

```text
wiki_maintenance_log.py
```

or shared function in existing tools.

Minimum:
- append JSONL log
- create log id
- record action / source_id / target / summary / rollback hint

Can be deferred if package report/delta tracking is sufficient.

---

### P1-03. Candidate snippet output

Tools may output candidate JSON snippet for:
- Runtime Queue
- Capture Inbox

But should not write automatically unless explicitly requested.

---

### P1-04. Skills alignment

Update skills:
- detect/change flow explanation
- impact result interpretation
- refresh/apply/log rule
- no-auto-promotion
- source representation issue routing

---

## 6. P2 / future patches

### P2-01. Full maintenance command

Possible future tool:

```text
maintain_wiki_sources.py
```

Could orchestrate:
- detect
- evaluate
- draft
- candidate
- report

Deferred to avoid automation scope creep.

### P2-02. Full metadata registry

Deferred.

### P2-03. Full semantic diff scoring

Deferred.

### P2-04. Full CI watcher

Deferred.

### P2-05. Source conversion integration

Deferred to Source Representation / Conversion Integration Sprint.

---

## 7. Minimal package update candidate

If implementing package update after sprint close, recommended package scope:

```text
v0.9.14
```

Apply:
- canonical WSM docs
- skill guidance updates
- detect/evaluate result model patch
- refresh/apply trace patch if small
- lint_wiki maintenance checks if small
- migration guide update

Do not implement:
- full orchestrator command
- auto-update
- auto-promotion
- semantic scoring

---

## 8. Compatibility test checklist

After patching, test:

### Changed source detection

```markdown
- [ ] unchanged source returns no_action / no impact required
- [ ] modified source returns requires_impact_evaluation
- [ ] missing source returns missing/deleted with review_required
```

### Impact evaluation

```markdown
- [ ] medium/high/unknown impact has review_required
- [ ] source representation issue maps to candidate
- [ ] no forbidden approval terms appear
```

### Refresh/apply

```markdown
- [ ] refresh creates draft by default
- [ ] apply requires explicit flag
- [ ] backup or rollback hint exists after apply
```

### Routing

```markdown
- [ ] blocking result routes to Runtime Queue
- [ ] non-blocking future value routes to Capture Inbox
```

### lint

```markdown
- [ ] candidate/promotion confusion is warned
- [ ] representation issue hidden state is warned
- [ ] old artifacts remain warning-compatible
```

---

## 9. Conclusion

WSM-08 defines the minimal implementation patch map.

Central decision:

```text
Enhance existing Wiki tools to support maintenance signals, candidates, drafts, and logs,
without creating an auto-update or auto-promotion engine.
```

Next: WSM-09 Migration / Backward Compatibility.
