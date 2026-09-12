# Wiki / Truth / History Spec for AI Work System MVP
Version: 0.1  
Scope: MVP only

---

# 1. Mục đích

Tài liệu này detail hóa spec cho:
- Truth zone
- Wiki zone
- History zone
- knowledge classes
- wiki entry structure
- staleness/update metadata
- promotion/backfill destination rules

---

# 2. Physical knowledge packaging

MVP uses **wiki-centered but not wiki-only** packaging:

```text
.ai-work/
  truth/
  wiki/
  history/
```

## Mapping
- `truth/` → Source of Truth
- `wiki/` → Curated Knowledge + Reference / Guidance
- `history/` → History / Evidence Trail

This separation is intentional.

---

# 3. Truth zone spec

## 3.1. Role
Authoritative zone.

## 3.2. Typical contents
- SOP_MASTER.md
- AI_WORK_CONTRACT.md
- canonical docs
- approved canonical summaries if any

## 3.3. Use rule
`authoritative`

## 3.4. Update rule
- not default destination for backfill
- requires canonical basis
- requires human approval

## 3.5. Metadata expectation
Truth docs should carry at least:
- artifact_type
- title
- status
- updated_at

Where needed, can also include:
- owner
- approval_basis
- canonical_source

---

# 4. Wiki zone spec

## 4.1. Role
Fast reading layer for AI:
- curated understanding
- reference/guidance
- reading hints
- review hints

## 4.2. Physical structure
```text
.ai-work/wiki/
  glossary.md
  domain/
  function/
  module/
  data/
  pattern/
  reference/
```

## 4.3. Entry taxonomy
- domain
- function
- module
- data
- pattern
- reference

## 4.4. Hybrid entry model
All entries share a core structure, plus type-specific sections.

---

# 5. History zone spec

## 5.1. Role
Trail / archive / evidence / later curation source.

## 5.2. Typical contents
- task archives
- archived QA
- evidence trail
- archived candidates
- backfill candidate archive

## 5.3. Use rule
`historical_only`

## 5.4. Rule
History is not a primary truth source.
Use for audit, resume, comparison, or later curation.

---

# 6. Knowledge classes

## 6.1. Classes
- `source_of_truth`
- `curated`
- `reference`
- `history`

## 6.2. Use rules
- `source_of_truth` → `authoritative`
- `curated` → `verify_when_decision_matters`
- `reference` → `verify_before_use`
- `history` → `historical_only`

## 6.3. Interpretation
### source_of_truth
- highest trust
- canonical/approved
- should override lower classes in conflicts

### curated
- reusable explanation/synthesis
- generally useful
- verify when decisions matter

### reference
- guidance, hints, likely approach, reading hints
- useful but should not be trusted as final truth

### history
- past trail
- evidence
- not current truth

---

# 7. Wiki entry placement and naming

## 7.1. Placement
`.ai-work/wiki/<entry_type>/<slug>.md`

## 7.2. Entry type folders
- domain/
- function/
- module/
- data/
- pattern/
- reference/

## 7.3. Slug rule
- lowercase
- hyphen-separated
- concise
- represent the entity clearly

---

# 8. Wiki entry metadata spec

## 8.1. Required metadata for important entries
```yaml
artifact_type: wiki_entry
entry_type: function
artifact_id: WIKI-FUNC-001
title: Manufacturing Order Update
knowledge_class: curated
use_rule: verify_when_decision_matters
status: active
canonical_references:
  - truth/canonical/shared_processing_design.md
last_verified_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
```

## 8.2. Required enums
### entry_type
- domain
- function
- module
- data
- pattern
- reference

### knowledge_class
- source_of_truth
- curated
- reference
- history

### use_rule
- authoritative
- verify_when_decision_matters
- verify_before_use
- historical_only

### status
- active
- needs_review

---

# 9. Core wiki entry structure

## 9.1. Required sections for all wiki entries
1. Purpose
2. Scope
3. Canonical References
4. Recommended Next Reads

## 9.2. Recommended common sections
5. Notes
6. Review Hints

## 9.3. Why these are required
- Purpose = fast orientation
- Scope = boundary control
- Canonical References = verification anchor
- Recommended Next Reads = navigation support without SeedPath

---

# 10. Type-specific section recommendations

## 10.1. Domain entry
Recommended sections:
- Key Concepts
- Main Areas
- Common Questions

## 10.2. Function entry
Recommended sections:
- Key Situations / Events
- Related Functions
- Upstream / Downstream Hints
- Review Hints

## 10.3. Module / Component entry
Recommended sections:
- Main Responsibilities
- Key Source Areas
- Dependency Hints

## 10.4. Data / Table entry
Recommended sections:
- Business Meaning
- Main Writers / Readers
- Data Risks

## 10.5. Pattern / Guidance entry
Recommended sections:
- When to Use
- How to Apply
- Pitfalls / Cautions

## 10.6. Reference entry
Recommended sections:
- What this helps with
- When to verify
- Suggested reading/use order

---

# 11. Reading behavior spec

## 11.1. Default reading order
1. Truth relevant to the task
2. Curated Wiki
3. Reference / Guidance
4. History when necessary

## 11.2. Truth usage
Use when:
- making important decisions
- verifying current behavior/rules
- task touches SOP/Contract/canonical design

## 11.3. Curated usage
Use when:
- fast understanding is needed
- summary/pattern/viewpoint is helpful

## 11.4. Reference usage
Use when:
- need hint / likely approach / reading order
- must still verify before relying on it

## 11.5. History usage
Use when:
- tracing
- resume
- audit
- later curation sourcing

---

# 12. Staleness spec

## 12.1. Problem
Wiki entries may become stale as sources change.

## 12.2. Minimal metadata for staleness
- canonical_references
- last_verified_at
- status

## 12.3. Status values
- active
- needs_review

## 12.4. Mark `needs_review` when
- canonical source changed
- mismatch found with source
- summary/hint appears outdated from new task evidence
- canonical refs are broken/unclear

## 12.5. Behavior of `needs_review`
- still usable for orientation
- must be verified more strongly for important tasks
- should trigger candidate/update workflow, not silent trust

---

# 13. Wiki update flow spec

## 13.1. Principle
Wiki update is a controlled execution task.

## 13.2. Flow
1. Detect need for update
2. Create update candidate
3. Triage
4. Create/use AIP_EXEC if needed
5. Build Active Step Context for update
6. Draft update
7. Human review/approval
8. Apply update
9. Record provenance

## 13.3. Update sources
Candidates may arise from:
- findings
- capture inbox
- mismatch with source
- lint warning
- human request

---

# 14. Backfill and promotion spec

## 14.1. Default rule
New items do not go directly to Truth.

## 14.2. Common destinations
- Curated Knowledge
- Reference / Guidance
- History / Evidence Trail

## 14.3. Destination rules

### Promote to Curated if
- reusable beyond current task
- not too tied to old context
- enough evidence/source basis
- not just a hint
- stable enough

### Promote to Reference if
- useful hint
- useful framing
- likely approach
- reading hint
- still needs verification before use

### Keep in History if
- task-specific
- too raw
- trail only
- not reusable enough

### Promote to Truth only if
- canonical basis clear
- human approval clear
- must be authoritative

## 14.4. Safety rules
- if unsure between Curated and Reference → choose Reference
- if unsure between Curated and Truth → choose Curated

---

# 15. Promotion checklist

## 15.1. Curated checklist
A candidate is suitable for Curated if most are true:
1. reusable beyond one task
2. not too context-bound
3. evidence/source basis is sufficient
4. not merely a hint
5. not likely to change too quickly
6. improves future understanding/work
7. minimally reviewed

## 15.2. Truth checklist
A candidate is suitable for Truth only if almost all are true:
1. official rule or approved official interpretation
2. canonical source exists
3. must be highest-priority reference
4. error impact is high
5. human approval exists
6. owner/authority exists or equivalent review basis
7. appropriate for authoritative use

---

# 16. Provenance expectations

Important wiki updates should be traceable to:
- source task
- source refs
- approval point
- update date

Provenance format can be refined later, but the concept is mandatory.

---

# 17. Wiki lint targets

## 17.1. Default MVP lint
- required metadata present
- enums valid
- required core sections present
- canonical refs exist
- recommended next reads exist

## 17.2. Additional behavior
- report `needs_review`
- warn if source_of_truth has weak canonical basis
- do not auto rewrite content

## 17.3. Optional light semantic lint
Allowed only when user explicitly requests it for a specific case.

---

# 18. Kết luận

Spec này chốt knowledge side của MVP như:
- a 3-zone physical model
- a 4-class knowledge model
- hybrid wiki entry structure
- lightweight staleness model
- controlled update/backfill flow
- safe distinction between truth, curated knowledge, guidance, and history
