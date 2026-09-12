# Working AIP Connection Runtime Guidance

Status: Canonical runtime guidance  
Version: v0.9.9  
Date: 2026-04-26

---

## 1. Purpose

This document provides runtime guidance for using Working AIP Connection.

It explains how AI should move from task/context/source discovery into execution through Working AIP.

---

## 2. Default runtime flow

```text
HUMAN task request
  ↓
Clarify task intent if needed
  ↓
Select / confirm Task Lens or No-Lens
  ↓
Inspect Workspace current context if relevant
  ↓
Use Wiki Meta / Index / Knowledge Hub to find candidate sources
  ↓
Read meta and source references as needed
  ↓
Select relevant inputs and classify their roles
  ↓
Create/update Working AIP
  ↓
Check Working AIP readiness
  ↓
aiws-aip run / execution
```

---

## 3. When Working AIP is required

Working AIP is required before non-trivial execution.

Examples:
- canonical package update
- canonical doc update
- design/review/testcase work
- multi-source task
- reusable process/template update
- task requiring traceability/review/rollback

---

## 4. When Working AIP Lite is enough

Working AIP Lite may be used for medium/low-risk tasks.

```markdown
# Working AIP Lite

## Task
## Output
## Context / Sources
## Steps
## Guardrails
## Done Criteria
```

Do not use Lite for high-impact/canonical/package tasks.

---

## 5. Readiness check

```markdown
- [ ] Task intent is clear
- [ ] Scope is clear
- [ ] Expected output is clear
- [ ] Source/context references are identified
- [ ] Task Lens/mode is recorded if used
- [ ] Execution steps are defined
- [ ] Guardrails/constraints are defined
- [ ] Open questions/blockers are listed
- [ ] Done criteria are clear
```

If missing, update Working AIP or ask HUMAN before execution.

---

## 6. Handoff rule

```text
Inputs can inform Working AIP.
Working AIP selects, scopes, and controls execution.
```

Do not dump all context into Working AIP.

Select relevant context and classify its role/status/limitation.

---

## 7. Anti-confusion rule

```text
A retrieved source, note, lens, template, candidate, or workspace context is not a Working AIP.
```

These can feed Working AIP but cannot replace it.

---

## 8. aiws-aip run rule

```text
aiws-aip run executes against Working AIP.
```

If Working AIP is missing or not ready for non-trivial execution, prepare/update it first.

---

## 9. Source representation issue

When a source is needed, respect AIWS-readable source representation rules.

If source representation is insufficient:

```text
source_representation_quality_issue
```

Record as blocker/limitation in Working AIP.

---

## 10. Lookback rule

For output-producing tasks with HUMAN feedback:

```text
output → HUMAN feedback → fix → HUMAN accepts → lookback candidate collection
```

Candidate collection is not promotion or apply-back.

---

## 11. Runtime failure modes

| Failure | Action |
|---|---|
| no Working AIP for non-trivial task | create/update Working AIP first |
| Working AIP not ready | resolve readiness gap |
| source representation insufficient | mark source_representation_quality_issue |
| candidate approval unknown | do not apply; ask/review |
| Task Lens too narrow | record reason and expand/confirm if needed |
| scope conflict | ask HUMAN before execution |

---

# v0.9.10 Workspace Boundary runtime addendum

When using Workspace during execution:

- use Workspace to keep active task context
- use Runtime Queue for unplanned subtasks/actions/follow-ups
- use Capture Inbox for possible future-value findings
- reflect execution-impacting Workspace context into Working AIP
- classify Workspace content at close

Do not execute directly from Workspace notes.

---

# v0.9.11 Minimal Runtime Testing runtime checks

When executing through Working AIP / aiws-aip run:

```text
aiws-aip run prepares runtime, not semantic execution.
```

Check:
- Working AIP readiness
- current Workspace state
- Runtime Queue blockers
- Capture Inbox close/triage status
- source verification need
- source_representation_quality_issue
- output/done criteria

Lint/check is a guardrail, not reviewer.

---

# v0.9.12 Runtime Tooling Alignment addendum

`run_aip.py status` should be used as runtime readiness visibility.

It can show:
- current AIP / Workspace
- Active Step Context
- Runtime Queue file and counts
- Capture Inbox counts
- final output warning
- legacy queue warning

It does not replace task reasoning, source verification, semantic review, or HUMAN confirmation.

---

# v0.9.15 Source Representation addendum

When Working AIP execution needs source evidence, the Active Step Context / runtime status should not imply source verification unless:
- AIWS-readable representation was read
- representation status/scope supports the claim
- limitations are handled or HUMAN verified original

If representation blocks current step, route to Runtime Queue.

---

# v0.9.16 Active Step Context addendum

Working AIP remains the task/step authority.

```text
ASC is derived from Working AIP current step.
It may expose execution context, but Working AIP remains the task/step authority.
```

Important step outputs, decisions, conclusions, and key HUMAN–AI discussion process used by later steps/final output must be persisted in Workspace with trace metadata.
