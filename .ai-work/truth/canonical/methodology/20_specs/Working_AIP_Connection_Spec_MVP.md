# Working AIP Connection Spec MVP

Status: Canonical MVP spec  
Version: v0.9.9  
Date: 2026-04-26  
Source sprint: Working AIP Connection Minimal Spec Sprint

---

## 1. Purpose

This spec defines the minimal connection rules from discovery/reuse/runtime context into Working AIP.

The purpose is to let AI move safely from:

```text
finding the right knowledge/context
```

to:

```text
executing the task
```

without bypassing Working AIP.

---

## 2. Core definition

Working AIP Connection means:

> the minimal handoff from discovered/reused/runtime context into an execution-ready Working AIP.

Short form:

```text
Working AIP Connection = context-to-execution handoff through Working AIP.
```

---

## 3. Core stance

```text
Discovery/reuse/context can inform execution.
Working AIP controls execution.
```

Supporting artifacts can feed Working AIP, but they do not replace it.

---

## 4. Mandatory Working AIP rule

Before non-trivial execution, AI must have or create a Working AIP.

Non-trivial execution includes:
- canonical doc update
- package creation
- design/review/testcase work
- multi-source task
- task affecting reusable process/future behavior
- task requiring traceability/review/rollback
- output-producing task with HUMAN acceptance

A full Working AIP is not required for trivial low-risk tasks such as simple wording correction, simple translation, or one-off explanation.

---

## 5. Lightweight Working AIP option

For medium/low-risk tasks, a Working AIP Lite may be sufficient.

Minimum structure:

```markdown
# Working AIP Lite

## Task
...

## Output
...

## Context / Sources
...

## Steps
...

## Guardrails
...

## Done Criteria
...
```

Do not use Lite for canonical updates, high-impact design/review tasks, package creation, source_of_truth changes, or broad reusable process changes.

---

## 6. Minimum Working AIP fields

Recommended minimum fields:

```markdown
# Working AIP

## 1. Task Intent
...

## 2. Scope
### In-scope
...
### Out-of-scope
...

## 3. Expected Output
...

## 4. Context / Source References
...

## 5. Selected Task Lens / Mode
...

## 6. Execution Steps
...

## 7. Guardrails / Constraints
...

## 8. Open Questions / Blockers
...

## 9. Done Criteria
...
```

---

## 7. Readiness levels

MVP uses three readiness levels:

```text
not_ready
lite_ready
execution_ready
```

### not_ready
Missing task intent, scope, output, or essential source/context.

### lite_ready
Enough for low/medium-risk task.

### execution_ready
Enough for non-trivial execution with clear scope, output, steps, guardrails, context references, and done criteria.

---

## 8. Readiness checklist

```markdown
## Working AIP Readiness Checklist

- [ ] Task intent is clear
- [ ] In-scope is clear
- [ ] Out-of-scope is clear when needed
- [ ] Expected output is clear
- [ ] Source/context references are identified
- [ ] Task Lens/mode is recorded if used
- [ ] Execution steps are defined
- [ ] Guardrails/constraints are defined
- [ ] Open questions/blockers are listed
- [ ] Done criteria are clear
```

If required items are missing, update Working AIP or ask HUMAN before execution.

---

## 9. Handoff sources and roles

Working AIP may receive input from:
- HUMAN instruction
- AIP Template
- Task Lens
- Wiki Meta / Index lookup result
- Knowledge Hub entry
- AIWS-readable source artifact
- Source Understanding Artifact
- Workspace current context
- Notebook note
- previous task output
- Controlled Knowledge Promotion candidate / lookback finding
- external/common knowledge if allowed

Rule:

```text
Many sources can feed Working AIP.
Only Working AIP controls execution.
```

---

## 10. Handoff representation

Recommended block:

```markdown
## Context / Source References

### HUMAN instruction
- ...

### AIP Template basis
- ...

### Selected Task Lens / Mode
- ...

### Wiki / Knowledge / Source references
| Ref | Type | Role in task | Status | Usage / Limitation |
|---|---|---|---|---|
| SRC-... | requirement_doc | source for ... | active | open meta first, artifact if exact wording needed |

### Workspace / Previous outputs
- ...

### Open questions from handoff
- ...
```

---

## 11. Anti-confusion boundary

Core rule:

```text
A retrieved source, note, lens, template, candidate, or workspace context is not a Working AIP.
```

They may feed Working AIP, but do not replace it.

| Artifact / layer | Can feed Working AIP? | Can replace Working AIP? |
|---|---:|---:|
| HUMAN instruction | yes | no |
| AIP Template | yes | no |
| Task Lens | yes | no |
| Wiki lookup result | yes | no |
| Knowledge Hub entry | yes | no |
| Source artifact | yes | no |
| Source Understanding Artifact | yes | no |
| Workspace | yes | no |
| Notebook | yes, with limitation | no |
| Promotion Candidate | yes, as candidate | no |
| Previous output | yes, after status check | no |
| Chat context | yes | no |
| aiws-aip run | executes Working AIP | no |

---

## 12. Runtime connection flow

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

Short form:

```text
intent → lens/context/search → selected inputs → Working AIP → readiness → execution
```

---

## 13. Task Lens relation

Task Lens can shape:
- search/retrieval focus
- review viewpoint
- reasoning focus
- source selection priority
- output framing

Working AIP should record:

```markdown
## Selected Task Lens / Mode
- Lens: ...
- Reason:
- Search/execution effect:
- Expansion allowed:
```

Task Lens does not replace Working AIP, scope, output, or done criteria.

No-Lens / AI-decides-search-scope is also valid and should be recorded when relevant.

---

## 14. Wiki Meta / Index relation

Wiki lookup results are candidate source references.

They should be selected and role-defined before entering Working AIP.

Working AIP should record:
- source_id / path
- source type
- role in task
- status
- usage
- limitation
- whether source verification is needed

A lookup hit is not automatically relevant or authoritative.

---

## 15. Workspace relation

Workspace holds current task/session working state.

Working AIP selects and structures relevant Workspace context.

Do not copy entire Workspace blindly into Working AIP.

Continuation tasks should inspect Workspace/current sprint context, identify next step, and update or create Working AIP as needed.

---

## 16. Notebook relation

Notebook may contain personal/local/raw ideas.

Notebook note may feed Working AIP only with role/status/limitation.

Notebook can store any, but Working AIP should not treat Notebook notes as authoritative unless reviewed/confirmed.

---

## 17. Source artifact relation

Source artifacts provide evidence/detail.

Working AIP defines how evidence is used.

In AIWS runtime, source artifact means AIWS-readable source representation, normally markdown.

If source representation is insufficient, record:

```text
source_representation_quality_issue
```

---

## 18. aiws-aip run relation

Core rule:

```text
aiws-aip run executes against Working AIP.
```

If Working AIP is missing or not ready for non-trivial execution, prepare/update it first.

aiws-aip run must not execute directly from:
- AIP Template alone
- Task Lens alone
- Wiki lookup result
- Knowledge Hub entry
- Workspace note
- Notebook note
- Promotion Candidate alone
- long chat context without consolidation

---

## 19. aiws-aip run pre-execution checklist

```markdown
## aiws-aip run Pre-Execution Checklist

- [ ] Working AIP exists
- [ ] Task intent clear
- [ ] Scope clear
- [ ] Expected output clear
- [ ] Source/context references selected
- [ ] Task Lens/mode recorded if used
- [ ] Steps defined
- [ ] Guardrails defined
- [ ] Blockers checked
- [ ] Done criteria clear
- [ ] Source representation quality issue checked if source is needed
- [ ] Post-feedback lookback requirement known if output-producing AIP
```

---

## 20. Controlled Knowledge Promotion / lookback relation

Candidates may feed Working AIP with status/limitations.

Working AIP execution may produce new candidates through lookback.

Candidate collection is not promotion or apply-back.

Relevant Working AIPs may include:

```markdown
## Post-Execution / Lookback
- Lookback required: yes/no
- Trigger: after HUMAN accepts fixed output
- Candidate types to collect:
  - improvement candidates
  - Knowledge Promotion candidates
  - Wiki Meta update candidates
  - AIP Template improvement candidates
  - source representation issues
- Auto-promotion: no
- Apply-back: deferred unless separately approved
```

---

## 21. Anti-patterns

### 21.1. Search-to-execution jump

Bad:

```text
Lookup found relevant source. Start execution.
```

Correct:

```text
Add selected source reference into Working AIP, check readiness, then execute.
```

### 21.2. Template-only execution

Bad:

```text
Run AIP Template directly.
```

Correct:

```text
Instantiate/adapt template into Working AIP first.
```

### 21.3. Candidate as approved knowledge

Bad:

```text
Candidate says X, so apply X as standard rule.
```

Correct:

```text
Record candidate status; review/approve before applying.
```

---

## 22. Deferred items

Deferred:
- full Working AIP lifecycle/versioning
- full AIP Template redesign
- automation engine
- UI/form
- scoring/telemetry
- full task execution framework
- full aiws-aip run implementation
- full approval workflow
- full Workspace lifecycle
- full Notebook promotion model
- apply-back automation

---

## 23. Conclusion

Working AIP Connection MVP defines the minimal context-to-execution handoff.

Central stance:

```text
Discovery/reuse/context can inform execution.
Working AIP controls execution.
Before non-trivial execution, AI must have or create a Working AIP.
Support artifacts can feed Working AIP but cannot replace it.
aiws-aip run executes against Working AIP.
If Working AIP is missing or not ready, prepare/update it first.
Candidate collection is not promotion or apply-back.
```

---

# v0.9.10 Workspace Boundary addendum

Workspace can feed Working AIP, but cannot replace it.

When Workspace context affects execution, reflect it into Working AIP:
- task intent
- scope
- source references
- Task Lens/mode
- execution steps
- guardrails
- blockers/open questions
- done criteria

Runtime Queue items that affect execution should also be reflected into Working AIP when needed.

Workspace itself is not execution authority.

---

# v0.9.11 Minimal Runtime Testing addendum

Runtime sanity rule:

```text
Before non-trivial execution, check Working AIP readiness.
```

Minimal runtime testing verifies:
- Working AIP exists before non-trivial execution
- task intent/scope/output are clear
- selected source/context references are present when needed
- execution steps and guardrails are defined
- blockers/open questions are visible
- done criteria are clear

Anti-pattern:

```text
Workspace, Wiki lookup result, Notebook note, or long chat context must not replace Working AIP.
```

See:
- `Minimal_Runtime_Testing_Stance_Spec_MVP.md`
- `Runtime_Sanity_Checklists_MVP.md`
