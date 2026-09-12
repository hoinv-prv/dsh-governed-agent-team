# Runtime Sanity Checklists MVP

Status: Canonical checklist  
Version: v0.9.11  
Date: 2026-04-26  
Source: MRT-06 Package / Sprint Close Sanity Checklist

---

## Purpose

This document provides MVP-level sanity checklists for runtime, sprint close, canonical merge, and package creation.

These checklists are deterministic guardrails. They do not replace HUMAN review or semantic source verification.

---

# AIWS_MRT-06_PACKAGE_AND_SPRINT_CLOSE_SANITY_CHECKLIST_v1

Status: Draft  
Sprint: Minimal Runtime Testing Stance Sprint  
Baseline: AI Work System MVP v0.9.10

---

## 1. Purpose

MRT-06 defines minimal sanity checklists for sprint close and package/canonical update.

The goal is to prevent preventable runtime/package mistakes without creating a full testing framework.

---

## 2. Core stance

```text
Close only after minimum runtime/canonical sanity is checked.
```

And:

```text
Lint/check is guardrail, not reviewer.
```

---

# 3. Sprint close sanity checklist

Use before closing a design sprint.

```markdown
## Sprint Close Sanity Checklist

### Scope
- [ ] Sprint goal completed?
- [ ] In-scope items completed or explicitly deferred?
- [ ] Out-of-scope items not accidentally included?
- [ ] Deferred future items listed?

### Core decisions
- [ ] Closed decisions listed?
- [ ] Important HUMAN confirmations reflected?
- [ ] Risks/limitations captured?
- [ ] New concepts do not conflict with AIWS core principles?

### Runtime boundaries
- [ ] Working AIP boundary preserved?
- [ ] Workspace boundary preserved?
- [ ] Knowledge Hub / Wiki boundary preserved?
- [ ] Notebook boundary preserved?
- [ ] Candidate collection not treated as promotion?
- [ ] No auto-apply-back unless explicitly approved?

### Baseline compatibility
- [ ] v0.9.2 / latest baseline checked if relevant?
- [ ] Good baseline patterns preserved where aligned?
- [ ] Compatibility impact captured if changes are needed?

### Lookback / candidates
- [ ] Improvement candidates captured?
- [ ] Findings for future sprint captured?
- [ ] Capture Inbox items triaged or deferred?
- [ ] Runtime Queue items resolved/deferred?

### Close artifacts
- [ ] Sprint close review created?
- [ ] Closure record created after HUMAN confirmation?
- [ ] Canonical merge handoff created?
- [ ] Backlog marked closed?
```

---

# 4. Canonical merge sanity checklist

Use before merging sprint outputs into canonical docs.

```markdown
## Canonical Merge Sanity Checklist

### Merge input
- [ ] Sprint closure record exists?
- [ ] Accepted source docs identified?
- [ ] Correct versions selected?
- [ ] Canonical merge map exists?

### Merge scope
- [ ] Only approved sprint scope merged?
- [ ] Delta docs not treated as canonical body?
- [ ] Appendix/examples placed separately if needed?
- [ ] Deferred items not merged as MVP commitments?

### Canonical consistency
- [ ] Related specs updated consistently?
- [ ] Skill/runtime guidance updated if affected?
- [ ] Templates updated if affected?
- [ ] Changelog updated?
- [ ] Manifest updated?
- [ ] Baseline note updated?

### Compatibility
- [ ] Existing v0.9.2 baseline patterns not degraded unnecessarily?
- [ ] Field/name changes minimized?
- [ ] Backward-compatible alias kept when needed?
- [ ] Migration/alignment candidates listed if tooling cannot be updated now?

### Validation
- [ ] Added files exist?
- [ ] Updated files exist?
- [ ] Delta tracking copied?
- [ ] Package report created?
```

---

# 5. Package creation sanity checklist

Use before releasing a package zip.

```markdown
## Package Creation Sanity Checklist

### Baseline
- [ ] Correct baseline package selected?
- [ ] Version number correct?
- [ ] Package name correct?
- [ ] Date correct?

### Required package files
- [ ] README exists?
- [ ] CHANGELOG exists?
- [ ] MANIFEST exists?
- [ ] Baseline note exists?
- [ ] Package creation report exists?
- [ ] Delta tracking folder exists?

### Canonical docs
- [ ] New canonical specs included?
- [ ] Updated canonical specs included?
- [ ] Appendix/examples included if created?
- [ ] Templates included if created?
- [ ] Skills/guidance included if updated?

### Runtime/tooling consistency
- [ ] aiws-aip run guidance still says it does not replace semantic execution?
- [ ] lint/check guidance still says guardrail not reviewer?
- [ ] Workspace Runtime Queue/Capture Inbox docs align with templates?
- [ ] Wiki Meta / Index docs align with baseline tooling or alignment candidates listed?
- [ ] No tool/schema mismatch ignored if known?

### Output
- [ ] Full package zip created?
- [ ] Delta tracking zip created if needed?
- [ ] Report link provided?
- [ ] File names match requested version?
```

---

# 6. Runtime sanity checklist

Use during long or non-trivial runtime execution.

```markdown
## Runtime Sanity Checklist

### Intent/lens
- [ ] Task intent clear?
- [ ] Task Lens / No-Lens appropriate?
- [ ] Lens does not over-narrow?

### Source
- [ ] Wiki Meta / Index used for routing?
- [ ] Source artifact verified when needed?
- [ ] Source representation issue recorded if needed?

### Workspace
- [ ] Workspace exists when needed?
- [ ] Current state visible?
- [ ] Runtime Queue updated for unplanned work?
- [ ] Capture Inbox used for future-value findings?

### Working AIP
- [ ] Working AIP exists before non-trivial execution?
- [ ] Working AIP readiness checked?
- [ ] Execution-impacting Workspace items reflected?

### Execution
- [ ] aiws-aip run prepares runtime, not semantic execution?
- [ ] AI performs reasoning/source verification?
- [ ] Output matches expected deliverable?

### Close
- [ ] Queue blockers resolved/deferred?
- [ ] Capture items triaged/deferred?
- [ ] Final output exists if done?
- [ ] Close notes recorded?
```

---

# 7. Lint/check severity handling

Reuse the severity model:

```text
Error = must fix before execution/close/package.
Warning = should review before merge/finalize.
Info = helpful observation, not blocking.
```

Strict close option:

```text
In strict close, unresolved warnings may block close/package.
```

---

# 8. Known alignment warnings to check

Because v0.9.10 specs advanced beyond v0.9.2 tooling, future package close should check:

```markdown
- [ ] Runtime Queue tooling supports or acknowledges `02_runtime_queue.jsonl`?
- [ ] `02_investigation_queue.jsonl` backward-compatible alias preserved?
- [ ] Capture Inbox enum/schema drift captured?
- [ ] Wiki tooling alignment candidates preserved?
- [ ] lint_workspace/lint_wiki mismatch risks listed?
```

If not fixed in current package, record as future alignment candidate.

---

## 9. Conclusion

MRT-06 defines minimum sanity checks for sprint close and package update.

Core stance:

```text
Sanity check before close.
Deterministic guardrail before package.
HUMAN review before important decisions.
```

Next: MRT-07 Anti-Patterns and Failure Modes.

---

# v0.9.12 Runtime Tooling Alignment checklist addendum

Before package close:

```markdown
- [ ] Workspace template uses `02_runtime_queue.jsonl`
- [ ] New template does not create `02_investigation_queue.jsonl`
- [ ] `init_workspace.py` creates `02_runtime_queue.jsonl`
- [ ] `lint_workspace.py` accepts `02_runtime_queue.jsonl`
- [ ] `lint_workspace.py` still reads legacy `02_investigation_queue.jsonl`
- [ ] `run_aip.py status` shows Runtime Queue and Capture Inbox visibility
- [ ] CHANGELOG/MANIFEST/baseline note record the rename
```

---

# v0.9.14 Wiki Source Maintenance checklist addendum

Before package close / source maintenance apply:

```markdown
- [ ] changed source detection result is treated as signal, not approval
- [ ] impact evaluation result has impact_level / recommendation / next_action
- [ ] Runtime Queue is used for current-task blocking maintenance
- [ ] Capture Inbox is used for future-value maintenance candidates
- [ ] refresh draft is reviewed before apply
- [ ] applied update has maintenance log / rollback hint
- [ ] source representation issue is visible when relevant
```

---

# v0.9.15 Source Representation checklist addendum

```markdown
- [ ] artifact_locator points to AIWS-readable representation
- [ ] original_source_locator is tracked when raw source exists
- [ ] representation_locator is tracked when conversion exists
- [ ] source_representation_status is present or safely unknown
- [ ] limitations are visible when representation is partial/unknown/failed
- [ ] high-impact source verification does not rely on incomplete representation without caveat/HUMAN check
```

---

# v0.9.16 Active Step Context checklist addendum

```markdown
- [ ] ASC has active_step_id / working_aip_ref
- [ ] ASC staleness_status is visible
- [ ] important step outputs have Step Output Meta
- [ ] important HUMAN–AI decisions/conclusions have Decision Discussion Trace
- [ ] previous step outputs used by current step have review_status
- [ ] source_refs include verification_level when source evidence is used
- [ ] Runtime Queue blockers are not ignored
- [ ] Capture Inbox candidates are not treated as approved knowledge
```
