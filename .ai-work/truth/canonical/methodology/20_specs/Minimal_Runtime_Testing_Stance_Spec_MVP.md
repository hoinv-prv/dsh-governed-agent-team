# Minimal Runtime Testing Stance Spec MVP

Status: Canonical MVP spec  
Version: v0.9.11  
Date: 2026-04-26  
Source sprint: Minimal Runtime Testing Stance Sprint

---

## 1. Purpose

This spec defines the Minimal Runtime Testing Stance for AI Work System MVP.

The purpose is to verify that AIWS follows runtime guardrails and component boundaries without introducing a full automated testing/scoring/telemetry framework.

---

## 2. Definition

Minimal Runtime Testing Stance means:

> the minimum set of principles, checkpoints, and manual test viewpoints used to confirm that AIWS runtime behavior follows its core guardrails and boundaries.

Short definition:

```text
Minimal Runtime Testing Stance = MVP-level runtime correctness check stance.
```

---

## 3. Central stance

```text
Minimal runtime testing = deterministic guardrails + runtime boundary checks,
not full semantic review / scoring / telemetry.
```

And:

```text
Correctness before optimization.
Runtime guardrails before scoring.
Manual/minimal checks before full automation.
```

---

## 4. What this stance checks

Minimal runtime testing checks:

```text
Did AIWS use the right component for the right role?
Did AI avoid unsafe shortcuts?
Did AI preserve source/canonical correctness?
Did AI close/classify runtime artifacts properly?
```

It focuses on:
- runtime behavior
- boundary correctness
- deterministic sanity checks
- close/package hygiene
- baseline preservation awareness

---

## 5. What this stance does not check

This spec does not define:
- full automated testing harness
- scoring/telemetry framework
- production observability
- full regression suite
- performance benchmark
- model quality benchmark
- prompt evaluation dataset
- CI integration
- automatic remediation engine

---

## 6. Runtime correctness principles

### 6.1. Correctness before optimization

```text
Do not reduce token/cost/steps in a way that weakens task correctness or output quality.
```

### 6.2. Intent before lens

```text
Clarify or infer task intent before selecting Task Lens.
```

### 6.3. Lens shapes, but does not blind

```text
Task Lens may shape search/reasoning, but must not over-narrow scope.
```

### 6.4. Wiki-first, not Wiki-only

```text
Use Wiki Meta / Index first for routing.
Use source artifact when evidence/details are needed.
```

### 6.5. Meta is not evidence

```text
Wiki Meta / Index is a routing/access layer.
It does not replace source verification when exact evidence is needed.
```

### 6.6. Workspace is not execution authority

```text
Workspace holds active task context.
Working AIP controls execution.
```

### 6.7. Working AIP before non-trivial execution

```text
Before non-trivial execution, AI must have or create a Working AIP.
```

### 6.8. aiws-aip run executes/prepares against Working AIP

```text
aiws-aip run should prepare/point runtime context and check status/readiness.
It should not replace task reasoning, review, or source verification.
```

### 6.9. Queue unplanned current-task work

```text
If any task produces an unplanned subtask/action/follow-up during execution,
AI should add it to Workspace Runtime Queue unless it blocks the current step.
```

### 6.10. Capture first, curate later

```text
Capture Inbox stores possible future-value findings before triage.
```

### 6.11. Candidate collection is not promotion

```text
Candidate collection is not promotion or apply-back.
```

### 6.12. Close/classify runtime artifacts

```text
At task close, Workspace content, Runtime Queue, Capture Inbox, open points, and candidates should be classified.
```

### 6.13. HUMAN controls important decisions

```text
AI may recommend; HUMAN confirms important scope/authority/promotion decisions.
```

### 6.14. State limitations explicitly

```text
If source/context/conversion is insufficient, AI should state limitation instead of guessing.
```

### 6.15. lint/check is guardrail, not reviewer

```text
Deterministic checks can detect structural/runtime issues,
but they do not replace HUMAN review or semantic correctness judgment.
```

### 6.16. Deterministic-first checks

```text
Prefer deterministic checks before semantic scoring.
```

### 6.17. Runtime status must be visible

```text
AI should be able to see current AIP/Working AIP, Workspace, active step/context,
queue/capture status, and draft/final output state before continuing.
```

---

## 7. Severity model

Reuse the MVP severity model:

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

## 8. Minimal runtime checkpoints

Runtime flow to check:

```text
Task request
  ↓
Intent clarification
  ↓
Task Lens / No-Lens decision
  ↓
Wiki Meta / Index / Knowledge routing
  ↓
Workspace state management
  ↓
Working AIP connection
  ↓
aiws-aip run / execution
  ↓
Output / feedback / fix
  ↓
Workspace Queue / Capture Inbox / lookback
  ↓
Close / classify / package/update
```

Checkpoint categories:
- task intent
- Task Lens / No-Lens
- Wiki Meta / Index
- source verification
- Workspace
- Workspace Runtime Queue
- Capture Inbox
- Working AIP
- aiws-aip run / execution
- output / feedback / fix
- close / classify
- lint / deterministic sanity
- runtime status visibility
- project boundary / identity sanity

---

## 9. Component boundary test viewpoints

Minimal runtime testing should verify that each AIWS component is used for its intended role.

Key boundaries:

| Component | Boundary to check |
|---|---|
| Task Lens | shapes search/reasoning; does not blind |
| Wiki Meta / Index | routes sources; does not replace evidence |
| Source artifact | evidence/detail source when needed |
| Workspace | active task context; not execution authority |
| Runtime Queue | current-task follow-up work |
| Capture Inbox | future-value capture before triage |
| Working AIP | non-trivial execution guardrail |
| aiws-aip run | runtime preparation/status, not semantic executor |
| lint/check | deterministic guardrail, not reviewer |
| Candidate | not approved knowledge |
| Knowledge Hub | controlled reusable knowledge |
| v0.9.2 baseline | compatibility reference, not design direction |

---

## 10. Baseline reference rule

```text
v0.9.2 is baseline/reference, not design direction.
```

Use v0.9.2 to:
- preserve good implementation patterns
- reduce migration cost
- maintain compatibility where aligned
- identify future alignment candidates

Do not use v0.9.2 to:
- override agreed sprint roadmap
- reverse accepted design decisions
- block necessary improvements
- become design authority

---

## 11. Future alignment candidates

Captured future candidates:
- Runtime Tooling Alignment Sprint
- Wiki Tooling Alignment Sprint
- Active Step Context Minimal Spec Sprint
- Controlled Update Pattern Sprint
- Wiki Source Maintenance / Impact Detection Sprint
- Source Representation / Conversion Integration Sprint
- Tooling Safety Policy Sprint
- Local/Common Knowledge Integration Sprint
- Code Source Profile Sprint
- Manual Runtime Regression Pack Sprint
- Automated Test Harness Sprint
- Runtime Telemetry / Scoring Sprint

These are not current MVP commitments unless explicitly selected later.

---

## 12. Evolution path

Recommended future evolution:

```text
MVP Minimal Runtime Testing Stance
  ↓
Runtime Tooling Alignment
  ↓
Manual Regression Pack
  ↓
Automated Tooling Test Harness
  ↓
Runtime Telemetry
  ↓
Quality Scoring
  ↓
Performance Optimization
```

Do not jump directly to scoring before runtime boundaries are stable.

---

## 13. Anti-confusion statement

```text
Minimal runtime testing checks whether AIWS follows runtime guardrails and component boundaries.
It uses deterministic checks and manual checkpoints as guardrails.
It does not replace HUMAN review, semantic source verification, future scoring, or telemetry.
```

---

# v0.9.12 Runtime Tooling Alignment addendum

Runtime testing now includes concrete tooling alignment checks:

- new Workspace template uses `02_runtime_queue.jsonl`
- legacy `02_investigation_queue.jsonl` remains readable as alias
- `lint_workspace.py` supports new + legacy queue schemas
- `run_aip.py status` exposes Runtime Queue / Capture Inbox visibility
- `lint/check` remains deterministic guardrail, not reviewer
- `aiws-aip run` remains runtime preparation/status, not semantic executor

---

# v0.9.13 Wiki Tooling Alignment addendum

Minimal runtime testing should check Wiki tool boundaries:

- lookup result is candidate route/context, not evidence verification
- refresh draft is not promotion
- detect/evaluate impact is signal, not approval
- source representation quality/caution is visible
- lint_wiki is deterministic guardrail, not semantic reviewer

---

# v0.9.14 Wiki Source Maintenance addendum

Minimal runtime testing should check Wiki source maintenance boundaries:

- source change detection is signal
- impact evaluation is recommendation
- refresh is draft by default
- apply is explicit and logged
- promotion is controlled separately
- applied maintenance has rollback hint

---

# v0.9.15 Source Representation addendum

Minimal runtime testing should check:

- AI does not claim raw non-text original was read unless HUMAN verified it
- AI verifies only what is present in AIWS-readable representation
- partial/unknown/failed representation triggers caveat, HUMAN check, re-conversion request, or blocking route
- representation issue routing uses Runtime Queue / Capture Inbox correctly

---

# v0.9.16 Active Step Context addendum

Minimal runtime testing should check:
- ASC is derived from current Working AIP step
- ASC does not replace Working AIP
- Workspace persists important step outputs/decisions/discussion traces
- ASC source pointers are not treated as source verification
- legacy missing trace is not treated as approval/verification
