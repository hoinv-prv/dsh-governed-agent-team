# Controlled Knowledge Promotion Templates and Checklists MVP

Version: v0.9.7  
Date: 2026-04-26  
Status: Canonical appendix/reference

---

## 1. Knowledge Hub Add/Update Checklist

```markdown
# Knowledge Hub Add/Update Checklist

## 0. Operation type
- [ ] Is this add / update / merge / replace / archive / promote_candidate?
- [ ] Is the target Knowledge Hub area clear?

## 1. Knowledge Value
- [ ] What specific value does this knowledge provide for AI runtime retrieval/reasoning/task execution?
- [ ] Which future task/use case will AI use this for?
- [ ] Does it help AI work more efficiently and/or produce higher-quality output?

## 2. Knowledge role / purpose
- [ ] Is the role clear: source_of_truth / source_derived_reference / curated_reference / best_practice / lesson_learned / usecase_specific_note / simple_reference_note?
- [ ] Is the authority level clear enough to prevent over-trust?

## 3. Source / context
- [ ] Is source/provenance available if source-backed?
- [ ] Is task/context recorded if lesson learned or best practice?
- [ ] Is freshness/currentness clear?

## 4. Target fit
- [ ] Is Knowledge Hub really the right target?
- [ ] Should this instead be Notebook / Workspace / appendix / guideline / backlog / discard?

## 5. Duplication / conflict
- [ ] Does similar knowledge already exist?
- [ ] Should this update/merge an existing entry instead of adding new content?
- [ ] Does it conflict with canonical docs or existing Knowledge Hub entries?

## 6. Risk / uncertainty
- [ ] What remains uncertain?
- [ ] Could this be over-generalized?
- [ ] Could adding/updating this reduce Knowledge Hub quality?

## 7. Review decision
- [ ] ready_to_add_update
- [ ] needs_value_clarification
- [ ] needs_source_check
- [ ] needs_owner_review
- [ ] better_as_appendix/guideline/backlog
- [ ] retain_local
- [ ] discard_recommended
```

---

## 2. Knowledge Promotion Candidate short template

```markdown
# Knowledge Promotion Candidate

- Title:
- Content:
- Source/context:
- Knowledge Value:
- AI-use case:
- Suggested target:
- Review needed:
- Status:
```

---

## 3. Knowledge Promotion Request full template

```markdown
# Knowledge Promotion Request

## 1. Request summary
- Request type:
- Candidate title:
- Short description:
- Requested by:
- Date:

## 2. Source / context
- Source/context:
- Source pointer:
- Source scope:
- Related task / AIP / Workspace / Notebook:
- Source-backed: yes/no/unknown

## 3. Knowledge Value
- AI-use case:
- How this helps AI work more efficiently:
- How this helps AI produce higher-quality output:
- What would be lost/repeated if not captured:
- Value category:

## 4. Knowledge role / authority
- Proposed role:
- Authority level:
- Freshness/currentness:
- Limitations / applicability:

## 5. Suggested target
- Primary target:
- Secondary target:
- Why this target:
- If not Knowledge Hub, where should it go:

## 6. Review checks
- Source/provenance check:
- Duplication/conflict check:
- Uncertainty/open points:
- Review/approval needed:
- Risk if promoted incorrectly:

## 6.5. Knowledge Hub Add/Update Checklist result
- Checklist required:
- Checklist status:
- Value check:
- Role/authority check:
- Source/context/freshness check:
- Target fit check:
- Duplication/conflict check:
- Risk/uncertainty check:
- Checklist decision:

## 7. Decision
- Candidate status:
- Recommended action:
- Decision reason:
- Next step:
```

---

## 4. Knowledge Hub Add/Update Request template

```markdown
# Knowledge Hub Add/Update Request

## 1. Operation
- Operation:
- Existing entry:
- Target Knowledge Hub area:

## 2. Knowledge
- Title:
- Content:
- Role:
- Scope:

## 3. Knowledge Value
- AI-use case:
- AI efficiency value:
- AI output quality value:
- Value category:

## 4. Source/context
- Source/context:
- Source pointer:
- Authority:
- Freshness:

## 5. Knowledge Hub Add/Update Checklist
- Checklist status:
- Knowledge Value:
- AI-use case:
- Role/authority:
- Source/context/freshness:
- Target fit:
- Duplication/conflict:
- Risk/uncertainty:
- Review needed:
- Checklist decision:

## 6. Draft update
...

## 7. Decision
- Recommended action:
- Status:
- Next step:
```

---

## 5. Post-feedback Knowledge Promotion Lookback template

```markdown
# Post-feedback Knowledge Promotion Lookback

## 1. Output reviewed
- Task:
- AIP Template / Working AIP:
- Output:
- Accepted by HUMAN:

## 2. HUMAN feedback summary
- ...

## 3. Fix summary
- ...

## 4. Improvement candidates

| Candidate | Type | Knowledge Value | Suggested target | Review needed | Apply-back status |
|---|---|---|---|---|---|

## 5. Knowledge Promotion candidates

| Candidate | Type | AI-use case | Suggested target | Review needed | Status |
|---|---|---|---|---|---|

## 6. Lessons learned / missed findings
- ...

## 7. Retain local / no promotion
- ...

## 8. Recommended next action
- ...
```

---

## 6. Change log template

```markdown
# AIWS Change Log Entry

- Date:
- Change type:
- Target:
- Change summary:
- Reason / Knowledge Value:
- Source/context:
- Request / Candidate:
- Reviewer / approver:
- Checklist result:
- Risk / uncertainty:
- Rollback hint:
- Status:
```

---

## 7. AIP Template snippet

```markdown
## Post-feedback Knowledge Promotion Lookback

When HUMAN accepts the fixed output, perform a short lookback.

Collect:
- improvement candidates
- missed findings
- lessons learned
- reusable HUMAN feedback patterns
- Knowledge Promotion candidates
- future backlog candidates

For each candidate, include:
- Knowledge Value
- future AI-use case
- suggested target
- review needed
- apply-back status

Guardrails:
- do not auto-promote
- do not auto-update Knowledge Hub
- do not auto-update AIP Template/guideline/prompt/playbook/process
- mark apply-back as deferred unless separately approved
- skip if HUMAN explicitly says no lookback is needed
```

---

## 8. aiws-aip run reminder text

```text
The fixed output has been accepted by HUMAN.
This AIP type includes a Post-feedback Knowledge Promotion Lookback step.
Please collect improvement candidates, missed findings, lessons learned, and Knowledge Promotion candidates.
Do not auto-promote or auto-update anything.
```
