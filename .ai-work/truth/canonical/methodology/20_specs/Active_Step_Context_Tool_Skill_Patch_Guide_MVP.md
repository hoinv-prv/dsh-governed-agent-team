# Active Step Context Tool / Skill Patch Guide MVP

Status: Canonical implementation guide  
Version: v0.9.16  
Date: 2026-04-26  
Source: ASC-08 Tool / Skill Patch Map

---

## Purpose

This guide records the minimal patch map for Active Step Context and Step Output / Decision Discussion Trace.

The package v0.9.16 applies P0 and part of P1:
- `build_active_step_context.py` includes traceability/source verification sections
- `run_aip.py status` exposes ASC/traceability summary
- `lint_workspace.py` checks Step Output Meta and Decision Discussion Trace
- `lint_all.py` aggregates workspace trace checks through workspace lint
- templates added for ASC, step output meta, decision trace, output index, and migration report
- skills updated with ASC/traceability guidance

---

# AIWS_ASC-08_TOOL_SKILL_PATCH_MAP_v1

Status: Draft  
Sprint: Active Step Context Minimal Spec Sprint  
Baseline: AI Work System MVP v0.9.15

---

## 1. Purpose

ASC-08 defines the minimal tool/skill patch map for Active Step Context and Step Output / Decision Trace.

This is a planning document for canonical merge / optional implementation package update.

---

## 2. Implementation stance

```text
Patch minimally.
Expose current-step context safely.
Do not build full orchestration engine.
Do not create hidden memory/cache layer.
```

---

## 3. Target tools

Primary target tools:

```text
run_aip.py
lint_workspace.py
lint_all.py
```

Related tools:

```text
lookup_wiki_source.py
lint_wiki.py
refresh_wiki_source_meta.py
build_wiki_source_index.py
```

Target skills:

```text
aiws-aip run
aiws-lint
aiws-wiki lookup
aiws-wiki refresh-meta
aiws-wiki build-meta
```

---

## 4. P0 patch candidates

### P0-01. run_aip.py active-step-context status

Patch:
- show active step id/title
- show expected output(s)
- show required previous step output refs if available
- show Runtime Queue blockers
- show source verification requirements/cautions
- show ASC staleness status if available

Do not:
- auto-select/advance step
- rewrite Working AIP
- claim source verification
- resolve queue items

---

### P0-02. Step Output / Decision Trace template

Add templates:
- Step_Output_Meta_Template.yml
- Step_Decision_Discussion_Trace_Template.yml
- Active_Step_Context_Template.yml

These should support:
- output_id
- result_type
- working_aip_ref
- step_id
- output_locator
- discussion_trace_locator
- source_refs
- used_by_steps
- used_by_final_output
- review_status
- limitations
- promotion/improvement candidate flags

---

### P0-03. lint_workspace.py step output trace checks

Patch:
- warn if persisted step output lacks meta
- warn if output used_by_steps exists but review_status missing
- warn if discussion_trace required but missing
- warn if source_refs claim verification but verification_level missing
- warn if Runtime Queue blocker linked but output marked complete/approved

---

### P0-04. lint_all.py include ASC/step output checks

Patch:
- include workspace step output trace lint
- surface blocking issues in aggregated output
- do not treat lint as semantic reviewer

---

## 5. P1 patch candidates

### P1-01. run_aip.py generate ASC draft

Optional minimal command:

```text
aiws-aip run status --active-step-context
```

or:

```text
aiws-aip run prepare-context --step STEP-001
```

Outputs Active Step Context draft.

Do not execute full step or auto-advance.

---

### P1-02. Workspace template update

Add folders:

```text
workspace/
  active_step_context/
  step_outputs/
  decision_traces/
```

Or keep simple file-based MVP layout if package already has a workspace template.

---

### P1-03. Skill guidance updates

Update skills with:
- ASC is temporary runtime view
- Working AIP remains authority
- Workspace persists outputs/traces
- source verification still requires representation
- discussion process trace required for important HUMAN–AI decisions

---

### P1-04. Minimal output handoff index

Optional file:

```text
workspace/step_outputs/index.jsonl
```

or:

```text
workspace/step_output_index.yml
```

Used to find:
- output_id
- step_id
- output_locator
- used_by_steps
- review_status

---

## 6. P2 / future

Defer:
- full execution engine
- automatic context optimizer
- semantic chunk ranking
- token scoring
- UI/form
- automatic AIP rewriting
- automatic output review scoring
- full artifact registry

---

## 7. Compatibility test checklist

After implementation, test:

```markdown
- [ ] old workspaces without ASC remain usable
- [ ] ASC template exists
- [ ] Step Output Meta template exists
- [ ] Decision Discussion Trace template exists
- [ ] lint warns if important output lacks meta
- [ ] lint warns if decision trace is missing where referenced
- [ ] aiws-aip run status can show current step context without changing task state
- [ ] source verification requirement remains pointer/status, not fake evidence
```

---

## 8. Conclusion

ASC-08 defines minimal tool/skill patch map.

Central decision:

```text
Tools should expose and check Active Step Context and step output traces,
without becoming a full task orchestration engine.
```

Next: ASC-09 Migration / Compatibility.
