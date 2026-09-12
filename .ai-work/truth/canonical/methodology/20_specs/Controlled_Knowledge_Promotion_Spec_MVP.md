# Controlled Knowledge Promotion Spec MVP

Version: v0.9.7  
Date: 2026-04-26  
Status: Canonical MVP spec  
Source sprint: Controlled Knowledge Promotion Minimal Spec Sprint

---

## 1. Purpose

Controlled Knowledge Promotion defines how AIWS safely turns useful findings, notes, source-derived understanding, lessons learned, best practices, task outputs, and improvement ideas into reusable knowledge or other controlled targets.

It is a controlled review/transition flow, not a storage component.

It prevents two opposite failures:

1. Losing useful knowledge because it was never captured.
2. Polluting Knowledge Hub/canonical docs/templates with unreviewed noise.

---

## 2. Official term

Official term:

```text
Controlled Knowledge Promotion
```

Practical short name:

```text
Knowledge Promotion
```

---

## 3. Core stance

```text
Knowledge Hub is for AI runtime value.
Notebook can store any.
Candidate can be broad.
Wiki / Knowledge Hub requires Knowledge Value.
AI can collect/prepare candidates.
Important promotion/add/update is controlled.
Skill must use checklist before Wiki add/update.
Post-feedback lookback captures improvement value.
No auto-promotion or auto-apply-back.
Important changes are logged for review/revision/rollback.
```

---

## 4. Knowledge Hub purpose

Knowledge Hub / Wiki in AIWS is primarily for AI runtime use.

It exists to help AI:
- search/retrieve knowledge efficiently
- route task intent to relevant source/knowledge
- reason with project/company-specific context
- verify source/evidence/authority
- reduce repeated reasoning/search cost
- produce higher-quality future outputs

HUMAN guides, reviews, and controls what is added or updated.  
AI is the primary runtime consumer.

Human readability is useful, but AI usability is the priority.

---

## 5. Knowledge Value

Definition:

> Knowledge Value = value that helps AI work more efficiently and/or produce higher-quality outputs in AIWS.

A knowledge item has value when it helps AI:
- search/retrieve better
- route task intent to the right source/knowledge
- reason with project/company-specific context
- verify source/evidence/authority
- reduce repeated reasoning/search cost
- avoid repeated mistakes
- improve correctness/consistency
- produce higher-quality future outputs

Minimum test:

```text
1. Which future task/use case will AI use this knowledge for?
2. How does it help AI work more efficiently or produce better output?
3. What would AI/HUMAN lose, repeat, or do incorrectly if this is not in Wiki?
```

If these cannot be answered, the item should not be added to Wiki / Knowledge Hub yet.

---

## 6. Notebook / Candidate / Wiki boundary

```text
Notebook can store any.
Candidate can be broad and intermediate.
Wiki / Knowledge Hub requires clear Knowledge Value.
```

### Notebook

Notebook may store any raw/personal/local note:
- ideas
- raw thoughts
- incomplete findings
- task-local notes
- unverified observations
- future exploration seeds
- notes without reusable value yet

Notebook does not require Knowledge Value.

### Knowledge Promotion Candidate

A candidate means:

```text
potentially reusable value pending review
```

Candidate does not mean approved, curated, canonical, promoted, or source of truth.

### Wiki / Knowledge Hub

Wiki / Knowledge Hub requires clear Knowledge Value and proper add/update control.

---

## 7. Candidate definition

A Knowledge Promotion Candidate may come from:
- Workspace finding
- Personal Notebook note
- Source Understanding Artifact
- custom/runtime Task Lens
- task output
- HUMAN feedback pattern
- lesson learned / best practice / aha finding
- recurring issue / vướng mắc
- future sprint backlog idea
- improvement candidate after feedback/fix

Candidate statuses:
- draft_candidate
- needs_source_check
- ready_for_review
- approved_for_promotion
- promoted
- rejected
- deferred
- retained_local

---

## 8. Promotion targets

Valid targets:
- Knowledge Hub
- canonical docs
- appendix/examples
- guideline/playbook
- AIP Template improvement candidate
- skill/prompt/process improvement candidate
- future sprint backlog
- Workspace-only retention
- Personal Notebook retention
- discard / no promotion

Not every candidate goes to Knowledge Hub.  
Discard/no promotion is a valid decision to prevent noise.

---

## 9. Review and checklist gate

Before important promotion/add/update, check:
- Knowledge Value
- AI-use case
- source/context/provenance
- authority/status/freshness
- target fit
- duplication/conflict
- uncertainty/open points
- scope/visibility
- risk
- review/approval need

For every meaningful Knowledge Hub add/update, the **Knowledge Hub Add/Update Checklist** is required.

Applies to:
- add new entry
- update existing entry
- merge duplicate/related entries
- replace stale knowledge
- archive outdated/noisy knowledge
- promote candidate into Knowledge Hub

---

## 10. No Auto-Promotion

AI may:
- identify candidates
- prepare candidate records
- run lookback
- draft add/update request
- suggest targets
- suggest review/source checks

AI must not automatically:
- promote into Knowledge Hub
- update canonical docs
- update AIP Templates
- update guidelines/playbooks/prompts/skills/process
- mark candidate as approved/promoted
- bypass checklist
- apply-back improvements

Important promotion/add/update requires HUMAN/owner review as appropriate.

---

## 11. Knowledge Hub Add/Update Skill

Suggested skill:

```text
knowledge-hub-add-update
```

The skill supports controlled add/update assessment.

It must:
- run the Knowledge Hub Add/Update Checklist
- check Knowledge Value
- classify knowledge role
- check source/context/authority/freshness
- check target fit
- check duplication/conflict
- output review/approval need
- draft add/update if appropriate

The skill is not approval authority.

Even if HUMAN says “add this to Wiki”, the skill still runs the checklist before recommending `ready_to_add_update`.

---

## 12. Knowledge roles

Recommended roles:
- source_of_truth
- source_derived_reference
- curated_reference
- best_practice
- lesson_learned
- aha_finding
- usecase_specific_note
- simple_reference_note
- candidate_only

Role must be explicit to prevent AI from over-trusting simple notes as source of truth.

---

## 13. HUMAN-triggered lookback

Command concept:

```text
knowledge-promotion-lookback
```

HUMAN may ask AI to look back over:
- chat context
- Workspace
- Working AIP trace
- task notes
- generated artifacts
- HUMAN feedback
- selected references
- open points

Output:
- missed findings
- lessons learned
- aha findings
- improvement candidates
- Knowledge Promotion candidates
- future backlog candidates
- retain-local / no-promotion notes

Lookback produces candidates only.

---

## 14. Post-feedback improvement candidate collection

Default pattern:

```text
AI creates output based on AIP
  ↓
HUMAN gives feedback
  ↓
AI fixes feedback
  ↓
HUMAN accepts fixed output
  ↓
AI collects improvement candidates
```

This captures reusable feedback value without automatically changing templates/guidelines/prompts/skills/process.

Apply-back is deferred to a later sprint/phase.

---

## 15. Default lookback for relevant AIP Templates

Relevant output-producing AIP Templates with HUMAN feedback/fix/acceptance loop should include:

```text
Post-feedback Knowledge Promotion Lookback
```

The step runs after HUMAN accepts the fixed output.

It collects:
- improvement candidates
- missed findings
- lessons learned
- reusable HUMAN feedback patterns
- Knowledge Promotion candidates
- future backlog candidates

It does not auto-promote or auto-apply changes.

---

## 16. aiws-aip run support

`aiws-aip run` should remind/check the lookback step for relevant AIPs.

When HUMAN accepts a fixed output, `aiws-aip run` should prompt AI to collect candidates unless skipped.

`aiws-aip run` must not:
- auto-promote candidates
- auto-update Knowledge Hub
- auto-update canonical docs
- auto-update AIP Templates
- auto-update guidelines/prompts/playbooks/skills/process

---

## 17. Log and rollback trace

Core rule:

```text
No important promotion/improvement without trace.
```

Important changes must be logged to support:
- tracking
- review
- revision
- rollback
- future AI reasoning

Minimum log fields:
- Date
- Change type
- Target
- Change summary
- Reason / Knowledge Value
- Source/context
- Request / Candidate
- Reviewer / approver
- Checklist result
- Risk / uncertainty
- Rollback hint
- Status

HUMAN approval can also be wrong, so important changes should be revisable/rollbackable.

---

## 18. Deferred items

Not included in MVP spec:
- full metadata/registry framework
- full approval workflow / role matrix
- apply-back workflow
- automated promotion pipeline
- scoring/telemetry
- UI/database implementation
- exact storage/folder paths
- full version-control/rollback automation
- automated duplicate detection
- Knowledge Hub lint automation

---

## 19. Anti-patterns

Avoid:
- treating every finding as Wiki value
- promoting candidate directly to Knowledge Hub
- bypassing Knowledge Hub Add/Update Checklist
- treating Notebook as Knowledge Hub
- treating Knowledge Hub as raw/source replacement
- applying feedback directly to AIP Templates
- ending AIP task immediately after HUMAN OK when lookback is required
- making important changes without trace
- letting appendix examples become hidden official rules

---

## 20. Minimal runtime flow

```text
Task work / source review / feedback / lookback
  ↓
Candidate or local retention decision
  ↓
Knowledge Value check
  ↓
Target decision
  ↓
Checklist / source / authority review
  ↓
Promote / add-update / defer / retain / discard
  ↓
Log important change if applied
```

---

# v0.9.8 Wiki Meta / Index maintenance addendum

Wiki Source Meta / Index updates can be:

```text
lightweight maintenance
```

or:

```text
Controlled Knowledge Promotion
```

Lightweight maintenance:
- add Lookup Key
- fix typo
- improve Summary
- correct artifact_locator
- add simple caution
- rebuild index and verify lookup

Controlled Knowledge Promotion is needed for:
- source_of_truth / authority changes
- source_id changes
- merge/split meta records
- major deprecation/replacement
- broad optional enrichment
- changes affecting future AI behavior broadly

Important changes should be logged for review/revision/rollback.

---

# v0.9.9 Working AIP Connection / lookback addendum

Knowledge Promotion candidates may feed Working AIP with status/limitations.

Rules:
- Candidate is not approved knowledge.
- If candidate approval is unknown, do not apply; ask/review.
- If task is candidate promotion/apply-back, Working AIP is required.
- Output-producing Working AIPs may include Post-Execution / Lookback.
- Lookback may collect improvement candidates and Knowledge Promotion candidates.
- Candidate collection is not promotion or apply-back.

Working AIP snippet:

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

# v0.9.10 Workspace Boundary / Capture Inbox addendum

Workspace can collect potential candidates.

Capture Inbox is Workspace-local staging:

```text
Capture Inbox = capture first, curate later.
```

A Capture Inbox item is not yet a reviewed Knowledge Promotion Candidate.

At Workspace close or lookback:
- triage Capture Inbox items
- convert reusable value into Knowledge Promotion Candidate if appropriate
- archive/discard low-value or task-local items
- do not auto-promote

Workspace findings require Controlled Knowledge Promotion before becoming Knowledge Hub updates.

---

# v0.9.11 Minimal Runtime Testing addendum

Runtime testing checks for Controlled Knowledge Promotion:

```text
Candidate collection is not promotion.
Capture Inbox item is not yet a reviewed Knowledge Promotion Candidate.
```

Check:
- Capture Inbox items are triaged before promotion
- Knowledge Hub updates pass add/update checklist
- feedback lookback collects candidates only
- no auto-apply-back to AIP Template/guideline/process without separate approval
- important improvements/promotions are logged for review/rollback where applicable

---

# v0.9.13 Wiki Tooling Alignment addendum

Wiki tooling outputs are not promotion.

```text
Refresh draft is not Knowledge Hub update.
Detect/evaluate impact is signal, not approval.
Migration aligns structure, not approval.
```

Approved Knowledge Hub update still requires:
- Knowledge Value check
- source/authority check
- review/control
- update log / rollback trace where applicable

---

# v0.9.14 Wiki Source Maintenance addendum

Wiki source maintenance can produce:
- update candidate
- refresh draft
- maintenance log
- Runtime Queue item
- Capture Inbox item

It cannot by itself produce:
- approved Knowledge Hub update
- promoted knowledge
- source_of_truth status change

Promotion remains controlled separately.

---

# v0.9.16 Step Output / Decision Trace addendum

Step Output / Decision / Discussion Trace may generate Knowledge Promotion candidates.

But:
- Step Output Artifact is not automatically Knowledge Hub content
- Decision Discussion Trace is not promotion
- Capture Inbox candidate is not approval
- Controlled Knowledge Promotion still decides if reusable knowledge enters Knowledge Hub

---

# CR-D8 Addendum — Promotion Trigger List (2026-05-25)

Source: AIP-EXEC-014 STEP-04, CR-D8 from AIWS-Wiki-CR-Proposal-2026-05-25.md §3.

## Enumerated Promotion Triggers

Các operations sau **MUST go through Controlled Promotion** (không phải lightweight update):

1. **Set `knowledge_class: source_of_truth`** — Nâng status artifact/object lên source_of_truth level. Irreversible without another Promotion.

2. **Change `source_id` của meta đang được referenced** — Meta ID là identity của routing record. Changing it breaks existing references.

3. **Split hoặc merge meta records** — Thay đổi 1:1 mapping giữa source artifact và meta. Affects all downstream metas / `## Related Sources` referencing these metas.

4. **Mark important artifact `deprecated`** — Deprecate artifact đang là input/parent cho các metas/quan hệ khác. Affects downstream routing.

5. **Change traceability chain (`related_artifact_refs`, `## Related Sources`) giữa major artifacts** — Thay đổi quan hệ artifact-to-artifact ở level major (không phải typo fix).

**Lightweight updates** (không cần Promotion — standard draft/review/apply):
- Fix typo trong lookup key
- Add/fix caution note
- Update `lookup_keys` (add new key, không remove T1)
- Update `task_relevant_tags`
- Fix `representation_locator` path
- Bump `updated_at` timestamp

**Note:** Skill `/aiws-wiki refresh-meta` (Wave 2) sẽ auto-detect và hard-stop khi gặp trigger list trên. Ref: CR-S6.
