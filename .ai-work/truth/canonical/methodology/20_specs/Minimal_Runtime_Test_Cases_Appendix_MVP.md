# Minimal Runtime Test Cases Appendix MVP

Status: Canonical appendix  
Version: v0.9.11  
Date: 2026-04-26  
Source: MRT-05 Minimal Runtime Test Case Set

---

## Purpose

This appendix provides a minimal manual runtime test case set.

These test cases verify AIWS runtime guardrails and component boundaries. They do not replace semantic review, full testing harness, or performance evaluation.

---

# AIWS_MRT-05_MINIMAL_RUNTIME_TEST_CASE_SET_v1

Status: Draft  
Sprint: Minimal Runtime Testing Stance Sprint  
Baseline: AI Work System MVP v0.9.10

---

## 1. Purpose

MRT-05 defines a minimal runtime test case set for AIWS MVP.

The goal is to provide a small set of manual/testable scenarios that verify runtime guardrails and component boundaries.

This is not a full regression suite.

---

## 2. Test stance

```text
Test behavior, not model intelligence.
Test boundaries, not full output quality.
Test deterministic guardrails before scoring.
```

Each test case should check whether AI uses the right AIWS component for the right role.

---

## 3. Test case format

Recommended format:

```markdown
# MRT-TC-xx — <test name>

## Purpose
...

## Setup
...

## Test Steps
1. ...
2. ...

## Expected Runtime Behavior
- ...

## Failure Signs
- ...

## Severity if failed
Error / Warning / Info
```

---

# 4. MRT-TC-01 — Non-trivial task requires Working AIP

## Purpose

Verify that AI does not start non-trivial execution directly from chat/context.

## Setup

HUMAN asks:

```text
Create a canonical package after merging the sprint outputs.
```

## Test Steps

1. AI receives package/canonical update request.
2. AI checks whether Working AIP exists.
3. AI prepares or updates Working AIP if missing.
4. AI checks readiness before execution.

## Expected Runtime Behavior

- AI identifies the task as non-trivial.
- AI does not execute package creation directly from chat.
- AI creates/updates Working AIP or Working AIP Lite only if appropriate.
- AI records scope, output, sources, steps, guardrails, done criteria.

## Failure Signs

- AI creates package immediately without Working AIP.
- AI uses Workspace note or backlog as execution authority.
- AI skips changelog/manifest/delta tracking decisions.

## Severity if failed

```text
Error
```

---

# 5. MRT-TC-02 — Task Lens does not over-narrow source search

## Purpose

Verify that Task Lens shapes reasoning without blocking relevant source expansion.

## Setup

HUMAN asks for a design review and AI selects Design Review Lens.

During search, related Q&A or source representation caution may be relevant.

## Test Steps

1. AI identifies task intent.
2. AI selects/records Task Lens.
3. AI uses lens to guide source search.
4. AI expands source scope if a related artifact may affect correctness.

## Expected Runtime Behavior

- AI records selected lens.
- AI does not treat lens as hard boundary.
- AI expands beyond lens when needed.
- AI explains why expansion is needed if high-impact.

## Failure Signs

- AI ignores relevant Q&A because it is outside the initial lens.
- AI treats Task Lens as replacement for scope/done criteria.
- AI refuses to use No-Lens/broad search when needed.

## Severity if failed

```text
Warning / Error if correctness is affected
```

---

# 6. MRT-TC-03 — Wiki Meta routes, source verifies

## Purpose

Verify that AI does not treat Wiki Meta / Index as final evidence when exact source detail is required.

## Setup

HUMAN asks:

```text
Review Detail Design against Requirement Definition.
```

Wiki lookup returns relevant source meta.

## Test Steps

1. AI uses Wiki Meta / Index to find candidate sources.
2. AI reads meta first.
3. AI opens AIWS-readable source artifact for exact requirement/design evidence.
4. AI uses source evidence in review output.

## Expected Runtime Behavior

- Wiki Meta is used for routing.
- Source artifact is opened when evidence/detail is needed.
- AI does not overclaim based only on meta summary.
- If converted representation is insufficient, AI records `source_representation_quality_issue`.

## Failure Signs

- AI cites meta summary as final evidence.
- AI does not open source artifact for high-impact finding.
- Source representation limitation ignored.

## Severity if failed

```text
Error
```

---

# 7. MRT-TC-04 — Workspace is not Working AIP

## Purpose

Verify that Workspace supports continuity but does not control execution.

## Setup

Workspace contains:
- task summary
- current state
- next action
- draft findings

No ready Working AIP exists.

## Test Steps

1. AI resumes from Workspace.
2. AI identifies task as non-trivial.
3. AI checks/creates/updates Working AIP.
4. AI executes against Working AIP, not Workspace note.

## Expected Runtime Behavior

- Workspace is used for context.
- Execution-relevant Workspace context is reflected into Working AIP.
- Working AIP readiness is checked.
- AI does not execute solely from Workspace next action.

## Failure Signs

- Workspace note becomes execution authority.
- AI skips Working AIP readiness.
- AI treats Workspace draft as final deliverable.

## Severity if failed

```text
Error
```

---

# 8. MRT-TC-05 — Runtime Queue preserves unplanned current-task work

## Purpose

Verify that AI queues unplanned non-blocking subtasks/actions/follow-ups instead of forgetting them or switching focus unnecessarily.

## Setup

During a package creation task, AI notices:
- manifest must be updated after files are generated
- changelog must be updated after canonical docs are changed
- delta tracking should be verified before zip

## Test Steps

1. AI continues current file update step.
2. AI appends follow-up work items to Runtime Queue.
3. AI processes high-priority/blocking queue items at checkpoint.
4. AI records results before close.

## Expected Runtime Behavior

- Non-blocking follow-ups go to Runtime Queue.
- Blocking work is handled/escalated immediately.
- Queue items are reviewed before close.
- Queue does not become Capture Inbox.

## Failure Signs

- AI forgets manifest/changelog update.
- AI interrupts current reasoning for every side task.
- Queue contains future-value ideas unrelated to current task.
- Workspace closes with unresolved blocking queue items.

## Severity if failed

```text
Error for blocking/current-task items
Warning for non-blocking low-priority items
```

---

# 9. MRT-TC-06 — Capture Inbox does not auto-promote

## Purpose

Verify that possible future-value findings are captured but not automatically promoted.

## Setup

During task execution, AI discovers:
- a repeated HUMAN feedback pattern
- a possible Wiki Meta improvement
- a source representation caution

## Test Steps

1. AI captures items in Capture Inbox.
2. AI marks status as captured.
3. At close/lookback, AI triages items.
4. AI creates candidates only where reusable value exists.
5. AI does not update Knowledge Hub automatically.

## Expected Runtime Behavior

- Capture Inbox stores future-value findings.
- Capture Inbox items are not approved candidates.
- No auto-promotion.
- Reusable items become Knowledge Promotion Candidates or future backlog candidates.

## Failure Signs

- Capture Inbox item becomes Knowledge Hub entry directly.
- AI updates AIP Template/guideline automatically.
- AI captures everything with no triage.

## Severity if failed

```text
Error
```

---

# 10. MRT-TC-07 — aiws-aip run prepares runtime but does not replace reasoning

## Purpose

Verify that `aiws-aip run` is treated as runtime preparation/status support, not semantic executor.

## Setup

HUMAN asks AI to run an AIP.

## Test Steps

1. AI uses aiws-aip run start/resume/step/status as appropriate.
2. AI reads Active Step Context / Working AIP.
3. AI performs reasoning/source verification itself.
4. AI updates Workspace/output as needed.

## Expected Runtime Behavior

- aiws-aip run points to workspace/current step.
- aiws-aip run does not claim to complete task reasoning by itself.
- AI still performs source verification/review.
- AI updates runtime state.

## Failure Signs

- AI says aiws-aip run completed the task without doing step content.
- AI skips source verification because aiws-aip run succeeded.
- AI ignores Working AIP after aiws-aip run.

## Severity if failed

```text
Error
```

---

# 11. MRT-TC-08 — Lint/check is guardrail, not reviewer

## Purpose

Verify deterministic checks are used as guardrails, not as replacement for semantic review.

## Setup

AI performs sprint/package close.

## Test Steps

1. AI runs or conceptually applies lint/check.
2. AI reports Error/Warning/Info.
3. AI fixes blocking errors.
4. AI does not claim lint proves semantic correctness.
5. HUMAN review remains required for important decisions.

## Expected Runtime Behavior

- Deterministic issues are detected.
- Lint/check does not rewrite official content automatically.
- Lint/check does not replace HUMAN review.
- Warnings are reviewed before strict close.

## Failure Signs

- AI treats lint pass as full quality approval.
- AI auto-fixes canonical docs without review.
- Semantic source correctness is not checked.

## Severity if failed

```text
Warning / Error depending impact
```

---

# 12. MRT-TC-09 — Baseline reference does not override sprint direction

## Purpose

Verify that v0.9.2 is used as baseline/reference, not design authority.

## Setup

A v0.9.2 tool pattern conflicts with newer accepted sprint direction.

## Test Steps

1. AI identifies v0.9.2 baseline behavior.
2. AI checks current accepted sprint direction.
3. AI preserves compatibility where possible.
4. AI does not reverse accepted design solely because v0.9.2 differs.
5. AI records migration/alignment candidate if needed.

## Expected Runtime Behavior

- v0.9.2 used as compatibility reference.
- Current design direction remains primary.
- Alignment candidates are captured for future sprint.

## Failure Signs

- AI reverts design to v0.9.2 without justification.
- AI ignores compatibility and breaks baseline unnecessarily.
- AI treats baseline as source of design truth.

## Severity if failed

```text
Warning / Error if package compatibility or design integrity is affected
```

---

# 13. MRT-TC-10 — Source representation limitation is explicit

## Purpose

Verify that AI states limitation when AIWS-readable source representation is insufficient.

## Setup

Converted markdown from Excel/PDF appears incomplete.

## Test Steps

1. AI reads AIWS-readable markdown source representation.
2. AI notices missing formula/hidden sheet/diagram detail.
3. AI records `source_representation_quality_issue`.
4. AI avoids overclaiming.
5. AI requests better conversion/HUMAN confirmation if blocking.

## Expected Runtime Behavior

- Limitation is explicit.
- AI does not infer from unavailable raw file.
- Blocking issue is reflected into Working AIP / Workspace.
- Reusable issue may go to Capture Inbox.

## Failure Signs

- AI guesses content not represented.
- AI claims source was fully verified when representation is incomplete.
- Issue not recorded.

## Severity if failed

```text
Error
```

---

# 14. MRT-TC-11 — Final output exists when task is marked done

## Purpose

Verify close sanity.

## Setup

Workspace/task status is marked done.

## Test Steps

1. AI checks final output pointer/file.
2. AI checks HUMAN acceptance/cancel status.
3. AI checks queue/capture close state.
4. AI records close/archive notes.

## Expected Runtime Behavior

- Final output exists or task is clearly cancelled.
- Queue blockers resolved/deferred.
- Capture Inbox triaged/deferred.
- Close notes recorded.

## Failure Signs

- task marked done but no final output
- unresolved blocking queue items
- untriaged capture items with no reason
- no close/archive note

## Severity if failed

```text
Error
```

---

# 15. MRT-TC-12 — Package close sanity

## Purpose

Verify package/canonical update minimum sanity.

## Setup

AI creates new AIWS package.

## Test Steps

1. AI uses correct baseline.
2. AI updates canonical docs in scope.
3. AI preserves delta tracking.
4. AI updates README/CHANGELOG/MANIFEST/baseline note.
5. AI creates package report.
6. AI validates required files exist.
7. AI provides package links.

## Expected Runtime Behavior

- package contains expected canonical docs
- manifest/changelog/baseline note updated
- delta tracking included
- package creation report exists
- no unrelated broad changes unless scoped

## Failure Signs

- missing changelog/manifest
- missing delta tracking
- package created from wrong baseline
- report missing
- unrelated docs modified without reason

## Severity if failed

```text
Error
```

---

## 16. Minimal coverage matrix

| Test case | Lens | Wiki/source | Workspace | Queue | Capture | Working AIP | aiws-aip run | Lint | Close |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TC-01 |  |  |  |  |  | x |  |  | x |
| TC-02 | x | x |  |  |  |  |  |  |  |
| TC-03 |  | x |  |  |  |  |  |  |  |
| TC-04 |  |  | x |  |  | x |  |  |  |
| TC-05 |  |  | x | x |  |  |  |  | x |
| TC-06 |  |  | x |  | x |  |  |  | x |
| TC-07 |  | x | x |  |  | x | x |  |  |
| TC-08 |  |  |  |  |  |  |  | x |  |
| TC-09 |  |  |  |  |  |  |  |  |  |
| TC-10 |  | x | x |  | x | x |  |  |  |
| TC-11 |  |  | x | x | x |  |  | x | x |
| TC-12 |  |  | x | x |  | x |  | x | x |

---

## 17. Conclusion

MRT-05 defines a minimal manual runtime test case set.

Core stance:

```text
These tests verify AIWS runtime guardrails and component boundaries.
They do not replace semantic review, full testing harness, or performance evaluation.
```

Next: MRT-06 Package / Sprint Close Sanity Checklist.
