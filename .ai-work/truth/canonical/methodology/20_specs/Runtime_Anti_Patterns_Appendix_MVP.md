# Runtime Anti-Patterns and Failure Modes Appendix MVP

Status: Canonical appendix  
Version: v0.9.11  
Date: 2026-04-26  
Source: MRT-07 Anti-Patterns and Failure Modes

---

## Purpose

This appendix lists runtime anti-patterns and failure modes that Minimal Runtime Testing should catch.

---

# AIWS_MRT-07_ANTI_PATTERNS_AND_FAILURE_MODES_v1

Status: Draft  
Sprint: Minimal Runtime Testing Stance Sprint  
Baseline: AI Work System MVP v0.9.10

---

## 1. Purpose

MRT-07 lists runtime anti-patterns and failure modes that Minimal Runtime Testing Stance should detect.

The goal is to prevent common runtime degradations as AIWS grows through sprints.

---

## 2. Anti-pattern categories

Runtime anti-patterns are grouped into:

- task intent / Task Lens
- Wiki Meta / source verification
- Workspace / Working AIP
- Runtime Queue / Capture Inbox
- aiws-aip run / lint
- Knowledge Promotion / lookback
- baseline compatibility
- package/canonical update

---

# 3. Task intent / Task Lens anti-patterns

## AP-01. Lens before intent

Bad:

```text
AI selects Task Lens before understanding task intent.
```

Risk:
- wrong search direction
- missed sources
- incorrect output framing

Correct:
```text
Clarify/infer task intent first, then select Task Lens or No-Lens.
```

Severity:
```text
Warning / Error if correctness affected
```

---

## AP-02. Lens as blindfold

Bad:

```text
AI refuses to search outside the selected lens.
```

Correct:
```text
Task Lens shapes, but does not blind.
Expand when relevant sources/context may affect correctness.
```

Severity:
```text
Warning / Error
```

---

# 4. Wiki Meta / source verification anti-patterns

## AP-03. Meta as evidence

Bad:

```text
AI treats Wiki Meta summary as final evidence for a high-impact finding.
```

Correct:
```text
Use Wiki Meta for routing. Open source artifact when evidence/detail is needed.
```

Severity:
```text
Error
```

---

## AP-04. Source representation overclaim

Bad:

```text
AI claims full verification when converted markdown representation is incomplete.
```

Correct:
```text
Record source_representation_quality_issue and state limitation.
```

Severity:
```text
Error
```

---

## AP-05. Index bypass by default

Bad:

```text
AI greps/reads broad source folders before checking Wiki Source Index.
```

Correct:
```text
Use index/meta first where available; then open source artifact.
```

Severity:
```text
Info / Warning
```

---

# 5. Workspace / Working AIP anti-patterns

## AP-06. Workspace as Working AIP

Bad:

```text
AI executes directly from Workspace next action.
```

Correct:
```text
Workspace feeds Working AIP. Working AIP controls non-trivial execution.
```

Severity:
```text
Error
```

---

## AP-07. Working AIP skipped

Bad:

```text
AI performs package/design/review task without Working AIP readiness.
```

Correct:
```text
Create/update Working AIP before non-trivial execution.
```

Severity:
```text
Error
```

---

## AP-08. Working AIP becomes runtime tracker

Bad:

```text
AI keeps progress logs, findings, and draft output inside AIP.
```

Correct:
```text
Keep runtime state in Workspace. Keep AIP as execution guardrail.
```

Severity:
```text
Warning
```

---

# 6. Runtime Queue / Capture Inbox anti-patterns

## AP-09. Follow-up kept only in context

Bad:

```text
AI notices follow-up work but keeps it only in chat/context.
```

Correct:
```text
Add unplanned non-blocking follow-up work to Runtime Queue.
```

Severity:
```text
Warning / Error if forgotten item affects output
```

---

## AP-10. Queue as dumping ground

Bad:

```text
AI puts ideas, future improvements, findings, and personal notes into Runtime Queue.
```

Correct:
```text
Runtime Queue = do/check/update later for current task.
Capture Inbox = possible future-value findings before triage.
```

Severity:
```text
Warning
```

---

## AP-11. Capture Inbox auto-promotes

Bad:

```text
AI promotes Capture Inbox item directly into Knowledge Hub.
```

Correct:
```text
Capture Inbox item must be triaged and reviewed before promotion.
```

Severity:
```text
Error
```

---

## AP-12. Queue blockers ignored at close

Bad:

```text
Workspace closes while blocking queue items remain pending.
```

Correct:
```text
Resolve, defer with reason, or escalate blocker before close.
```

Severity:
```text
Error
```

---

# 7. aiws-aip run / lint anti-patterns

## AP-13. aiws-aip run as semantic executor

Bad:

```text
AI assumes aiws-aip run completed task reasoning.
```

Correct:
```text
aiws-aip run prepares runtime context; AI still executes reasoning/source verification.
```

Severity:
```text
Error
```

---

## AP-14. Lint pass as quality approval

Bad:

```text
AI claims output is semantically correct because lint passed.
```

Correct:
```text
Lint is guardrail, not reviewer.
```

Severity:
```text
Warning / Error if high-impact
```

---

## AP-15. Deterministic errors ignored

Bad:

```text
Package is released despite missing required files/invalid JSONL/duplicate IDs.
```

Correct:
```text
Errors must be fixed before close/package.
```

Severity:
```text
Error
```

---

# 8. Knowledge Promotion / lookback anti-patterns

## AP-16. Candidate as approved knowledge

Bad:

```text
AI uses an unreviewed candidate as official rule.
```

Correct:
```text
Candidate remains candidate until reviewed/promoted.
```

Severity:
```text
Error
```

---

## AP-17. Feedback auto-applies to templates

Bad:

```text
AI updates AIP Template automatically after HUMAN feedback.
```

Correct:
```text
Collect improvement candidate. Apply-back requires separate approval/task.
```

Severity:
```text
Error
```

---

## AP-18. Lookback skipped after accepted fix

Bad:

```text
AI fixes HUMAN feedback and ends task without collecting reusable learnings.
```

Correct:
```text
If AIP/output type requires lookback, collect improvement candidates before close.
```

Severity:
```text
Warning
```

---

# 9. Baseline compatibility anti-patterns

## AP-19. Baseline as design authority

Bad:

```text
AI reverts design to v0.9.2 because v0.9.2 had that implementation.
```

Correct:
```text
v0.9.2 is baseline/reference, not direction.
```

Severity:
```text
Warning / Error
```

---

## AP-20. Breaking baseline without need

Bad:

```text
AI renames fields/tools/files without clear need and breaks compatibility.
```

Correct:
```text
Preserve compatibility unless deliberate migration is approved.
```

Severity:
```text
Warning / Error if package users affected
```

---

# 10. Package/canonical anti-patterns

## AP-21. Delta docs become canonical body

Bad:

```text
AI copies all sprint delta docs into canonical body without consolidation.
```

Correct:
```text
Merge accepted decisions/specs into canonical docs; keep delta tracking separately.
```

Severity:
```text
Warning / Error
```

---

## AP-22. Changelog/manifest missing

Bad:

```text
Package created without updating CHANGELOG/MANIFEST/baseline note.
```

Correct:
```text
Package close requires changelog/manifest/baseline note/report.
```

Severity:
```text
Error
```

---

## AP-23. Future candidate becomes MVP commitment

Bad:

```text
AI lists deferred future tooling as current MVP commitment.
```

Correct:
```text
Clearly mark deferred items and future candidates.
```

Severity:
```text
Warning / Error
```

---

## 11. Failure mode table

| Failure mode | Likely cause | Checkpoint |
|---|---|---|
| wrong lens | intent unclear | intent/lens checkpoint |
| missed source | lens too narrow / index skipped | source checkpoint |
| false citation | meta used as evidence | Wiki/source checkpoint |
| execution drift | Working AIP skipped | Working AIP checkpoint |
| lost follow-up | Runtime Queue not used | Queue checkpoint |
| knowledge dumping | Capture Inbox auto-promoted | Capture/Promotion checkpoint |
| package inconsistency | sanity checks skipped | package close checklist |
| tooling mismatch | baseline specs drift | baseline compatibility checkpoint |

---

## 12. Conclusion

MRT-07 defines anti-patterns and failure modes.

Core stance:

```text
Minimal runtime testing should catch role confusion, unsafe shortcuts, and close/package hygiene failures before they degrade AIWS.
```

Next: MRT-08 Relation to Future Testing / Scoring / Telemetry.
