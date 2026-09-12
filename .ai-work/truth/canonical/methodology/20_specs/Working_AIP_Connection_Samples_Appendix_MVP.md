# Working AIP Connection Samples Appendix

Status: Canonical appendix  
Version: v0.9.9  
Date: 2026-04-26  
Source: Working AIP Connection Minimal Spec Sprint — WAC-08

---

## Purpose

This appendix provides sample Working AIP Connection flows.

These examples are not a separate execution framework. They demonstrate how to connect selected context into Working AIP before execution.

---

# AIWS_WAC-08_SAMPLE_WORKING_AIP_CONNECTION_FLOWS_v1

Status: Draft  
Sprint: Working AIP Connection Minimal Spec Sprint  
Baseline: AI Work System MVP v0.9.8

---

## 1. Purpose

WAC-08 provides sample Working AIP Connection flows.

The goal is to show how different runtime contexts are connected into Working AIP before execution.

These samples demonstrate:
- Task Lens handoff
- Wiki Meta / Index handoff
- Workspace context handoff
- Source artifact handoff
- aiws-aip run readiness
- anti-confusion boundaries
- lightweight vs execution-ready Working AIP

---

## 2. Common flow pattern

All samples follow this pattern:

```text
HUMAN task request
  ↓
clarify task intent if needed
  ↓
select Task Lens / No-Lens if relevant
  ↓
use Workspace / Wiki / source / Knowledge Hub if relevant
  ↓
select and classify inputs
  ↓
create/update Working AIP
  ↓
check readiness
  ↓
aiws-aip run / execution
```

Core rule:

```text
Inputs can inform Working AIP.
Working AIP controls execution.
```

---

# 3. Sample Flow 1 — Wiki/source-heavy design review task

## 3.1. HUMAN request

```text
Review Detail Design F02 SearchRoom against Requirement Definition and Basic Design.
```

## 3.2. Runtime interpretation

Task type:
- design review
- source-heavy
- non-trivial execution

Working AIP required: **yes**

Task Lens:
```text
Design Review Lens
```

## 3.3. Discovery

AI uses Wiki Meta / Index:

```bash
python .ai-work/tooling/lookup_wiki_source.py --query "F02 SearchRoom requirement"
python .ai-work/tooling/lookup_wiki_source.py --query "F02 SearchRoom basic design"
python .ai-work/tooling/lookup_wiki_source.py --query "F02 SearchRoom detail design"
```

Candidate sources:
- `SRC-RD-F02-SEARCHROOM`
- `SRC-BD-F02-SEARCHROOM`
- `SRC-DD-F02-SEARCHROOM`

AI opens `meta_locator` first for each candidate.

AI opens `artifact_locator` if exact wording/design evidence is needed.

## 3.4. Working AIP connection

```markdown
# Working AIP — Review DD F02 SearchRoom

## 1. Task Intent
Review Detail Design F02 SearchRoom against Requirement Definition and Basic Design.

## 2. Scope
### In-scope
- Consistency between RD, BD, and DD for F02 SearchRoom
- Missing design branches
- Input/output and validation consistency
- Source-backed review findings

### Out-of-scope
- Review unrelated functions
- Rewrite the design document
- Update canonical docs

## 3. Expected Output
Markdown review report with findings, source references, severity, and recommended actions.

## 4. Context / Source References
| Ref | Type | Role in task | Status | Usage / Limitation |
|---|---|---|---|---|
| SRC-RD-F02-SEARCHROOM | requirement_doc | requirement source | active | verify requirement behavior |
| SRC-BD-F02-SEARCHROOM | basic_design | design baseline | active | compare DD against BD |
| SRC-DD-F02-SEARCHROOM | detail_design | review target | active | target artifact |

## 5. Selected Task Lens / Mode
- Lens: Design Review Lens
- Effect: prioritize requirement/design consistency and missing branches
- Expansion allowed: yes, if related Q&A/source is needed

## 6. Execution Steps
1. Read Wiki Source Meta for each source.
2. Open artifact_locator for RD/BD/DD as needed.
3. Compare DD behavior against RD/BD.
4. Identify inconsistencies/missing branches.
5. Create review report.

## 7. Guardrails / Constraints
- Do not use lookup results as findings without source verification.
- Cite source references for high-impact findings.
- If representation is insufficient, mark source_representation_quality_issue.

## 8. Open Questions / Blockers
- None currently blocking execution.

## 9. Done Criteria
- Review report created.
- Findings include source basis.
- Unverified assumptions clearly marked.
```

## 3.5. Readiness

Readiness: `execution_ready`

## 3.6. aiws-aip run behavior

`aiws-aip run` executes against Working AIP, not directly from Wiki lookup results.

---

# 4. Sample Flow 2 — Continuation task from current Workspace

## 4.1. HUMAN request

```text
Tiếp tục nhé.
```

## 4.2. Runtime interpretation

Task type:
- continuation
- context-dependent
- may be non-trivial

Working AIP required: depends on current step.

If continuing sprint design/update, Working AIP should be created/updated.

## 4.3. Discovery

AI checks:
- current Workspace
- last accepted WAC item
- current sprint backlog
- next planned work item

Example current state:
```text
WAC-07 completed.
Next item: WAC-08 Sample Working AIP Connection Flows.
```

## 4.4. Working AIP connection

```markdown
# Working AIP Lite — Continue WAC Sprint

## Task
Continue Working AIP Connection Minimal Spec Sprint by drafting WAC-08.

## Output
Create WAC-08 markdown and update sprint backlog.

## Context / Sources
- Current sprint backlog: AIWS_SPRINT_BACKLOG_WORKING_AIP_CONNECTION_MINIMAL_SPEC_v5.md
- Previous output: WAC-07 aiws-aip run Relation
- HUMAN instruction: "Tiếp tục nhé"

## Steps
1. Identify next WAC item from backlog.
2. Draft WAC-08.
3. Update backlog status and closed decision if needed.
4. Provide file links.

## Guardrails
- Do not open full lifecycle/versioning scope.
- Keep sprint focused on Working AIP Connection.
- Preserve previous WAC decisions.

## Done Criteria
- WAC-08 file created.
- Backlog updated.
```

## 4.5. Readiness

Readiness: `lite_ready`

## 4.6. Guardrail

Continuation request does not mean AI should guess outside current sprint scope.

---

# 5. Sample Flow 3 — Canonical package update task

## 5.1. HUMAN request

```text
Hãy package nhé.
```

## 5.2. Runtime interpretation

Task type:
- package creation
- canonical update
- high-impact
- non-trivial execution

Working AIP required: **yes**

## 5.3. Discovery

AI should check:
- accepted sprint closure record
- canonical merge handoff
- baseline package
- target version
- delta tracking files
- changelog/manifest requirements

## 5.4. Working AIP connection

```markdown
# Working AIP — Canonical Package Update v0.9.x

## 1. Task Intent
Create new AIWS canonical package by merging closed sprint outputs into canonical docs.

## 2. Scope
### In-scope
- Use accepted sprint closure record and canonical merge map
- Update canonical docs
- Add appendix/examples if needed
- Preserve delta tracking
- Update changelog, manifest, baseline note
- Generate zip package and report

### Out-of-scope
- Redesign unrelated AIWS components
- Modify tooling unless explicitly requested
- Open deferred future items

## 3. Expected Output
- Full canonical package zip
- Delta tracking zip
- Package creation report

## 4. Context / Source References
| Ref | Type | Role in task | Status | Usage / Limitation |
|---|---|---|---|---|
| Sprint Closure Record | closure | accepted sprint output | closed | canonical merge basis |
| Canonical Merge Handoff | merge map | update guide | accepted | merge target list |
| Baseline package | package | source package | current baseline | copy and update |

## 5. Selected Task Lens / Mode
- Lens: Canonical Merge / Package Update
- Effect: prioritize source-of-truth package consistency, changelog, manifest, delta tracking

## 6. Execution Steps
1. Unpack baseline package.
2. Add/update canonical docs according to merge map.
3. Preserve sprint delta docs in delta tracking.
4. Update changelog/manifest/baseline note.
5. Create package creation report.
6. Zip full package and delta package.
7. Verify files exist.

## 7. Guardrails / Constraints
- Do not change unrelated docs.
- Do not omit changelog/manifest.
- Preserve current field/tooling compatibility.
- Keep delta docs separate from canonical docs.

## 8. Open Questions / Blockers
- None if closure record and baseline package exist.

## 9. Done Criteria
- Package zip created.
- Delta zip created.
- Report created.
- Links provided.
```

## 5.5. Readiness

Readiness: `execution_ready`

## 5.6. Guardrail

Do not run package creation from the short chat request alone.  
Connect closure/merge sources into Working AIP first.

---

# 6. Sample Flow 4 — Knowledge Hub / Wiki Meta update task

## 6.1. HUMAN request

```text
Add this new requirement document into Wiki Meta / Index.
```

## 6.2. Runtime interpretation

Task type:
- Wiki Source Meta update
- may be lightweight maintenance or controlled update

Working AIP required:
- yes if adding important source
- Working AIP Lite may be enough for simple meta creation

## 6.3. Discovery

AI checks:
- artifact path
- artifact is AIWS-readable markdown representation
- source_id
- source_type
- knowledge_class
- status
- current index/build tools

## 6.4. Working AIP connection

```markdown
# Working AIP Lite — Add Wiki Source Meta

## Task
Create Wiki Source Meta for new requirement document and rebuild/verify index.

## Output
- New meta file
- Rebuilt index.jsonl
- Lookup verification result

## Context / Sources
- Artifact: docs/requirements/F05_UpdateBooking_Requirement.md
- source_id: SRC-RD-F05-UPDATEBOOKING
- source_type: requirement_doc
- knowledge_class: curated unless HUMAN says source_of_truth

## Steps
1. Create Wiki Source Meta using current field names.
2. Fill Summary, Knowledge Targets, Lookup Keys, Artifact Reference, Hints, Cautions.
3. Rebuild index.
4. Verify lookup with source_id, function ID, Japanese/English terms.

## Guardrails
- Do not set source_of_truth unless HUMAN explicitly instructs.
- artifact_locator must point to AIWS-readable markdown/source representation.
- Do not edit index.jsonl manually.

## Done Criteria
- Meta created.
- Index rebuilt.
- Lookup verified.
```

## 6.5. Readiness

Readiness: `lite_ready` or `execution_ready` depending impact.

## 6.6. Relation to Controlled Knowledge Promotion

If adding high-authority source or source_of_truth, use Controlled Knowledge Promotion/review/log.

---

# 7. Sample Flow 5 — Small wording fix

## 7.1. HUMAN request

```text
Sửa câu tiếng Nhật này cho tự nhiên hơn.
```

## 7.2. Runtime interpretation

Task type:
- trivial
- low risk
- no project source
- no canonical update

Working AIP required: **no**

## 7.3. Minimal handling

AI can answer directly.

Optional mental/light structure:
```text
Task: revise sentence
Output: corrected Japanese
Guardrail: preserve meaning
```

## 7.4. Guardrail

Do not over-create Working AIP for trivial tasks.

Working AIP is mandatory for non-trivial execution, not every chat response.

---

# 8. Sample Flow 6 — Applying a Knowledge Promotion Candidate

## 8.1. HUMAN request

```text
Apply this improvement candidate to the AIP Template.
```

## 8.2. Runtime interpretation

Task type:
- applies candidate to reusable artifact
- high-impact if template changes future behavior
- non-trivial

Working AIP required: **yes**

## 8.3. Discovery

AI checks:
- candidate content
- source/context
- approval/review status
- target AIP Template
- impact on future tasks
- rollback/log need

## 8.4. Working AIP connection

```markdown
# Working AIP — Apply Improvement Candidate to AIP Template

## 1. Task Intent
Review and apply approved improvement candidate to target AIP Template.

## 2. Scope
### In-scope
- Review candidate source/context
- Check Knowledge Value / improvement value
- Update target AIP Template if approved
- Record change summary and rollback hint

### Out-of-scope
- Apply unrelated candidate items
- Redesign entire AIP Template system

## 3. Expected Output
- Updated AIP Template
- Change log entry
- Summary of applied change

## 4. Context / Source References
| Ref | Type | Role in task | Status | Usage / Limitation |
|---|---|---|---|---|
| Candidate ID | improvement_candidate | change input | pending/approved | must not be treated as applied until reviewed |
| Target Template | AIP Template | update target | active | update only scoped section |

## 5. Selected Task Lens / Mode
- Lens: Improvement Apply-back / Controlled Update

## 6. Execution Steps
1. Review candidate and source/context.
2. Confirm target and scope.
3. Apply minimal template update.
4. Update changelog/log.
5. Check no unrelated template change.

## 7. Guardrails / Constraints
- Candidate is not approved knowledge unless reviewed/confirmed.
- Important template change requires log/rollback trace.
- Do not update unrelated templates.

## 8. Open Questions / Blockers
- Is candidate approved for apply-back? If unknown, ask HUMAN.

## 9. Done Criteria
- Template updated or blocked with reason.
- Change log entry created.
- Output summary provided.
```

## 8.5. Readiness

Readiness: `not_ready` if candidate approval is unknown.  
Readiness: `execution_ready` if candidate is approved and target/scope are clear.

---

# 9. Sample Flow 7 — Source representation issue

## 9.1. HUMAN request

```text
Review this converted Excel testcase.
```

## 9.2. Runtime interpretation

Task type:
- testcase review
- source-dependent
- may be high-impact

Working AIP required: **yes**

## 9.3. Discovery

Wiki meta says:

```markdown
## Cautions
- representation_quality: partial
- Original file was Excel; formulas/hidden sheets may not be fully represented.
```

## 9.4. Working AIP connection

```markdown
# Working AIP — Review Converted Excel Testcase

## 1. Task Intent
Review converted Excel testcase.

## 2. Scope
### In-scope
- Review visible markdown testcase rows
- Identify unclear/missing conversion details
- Report source representation limitations

### Out-of-scope
- Infer hidden Excel formulas or sheets
- Directly inspect original Excel raw file

## 3. Expected Output
Review report with findings and source representation limitations.

## 4. Context / Source References
| Ref | Type | Role in task | Status | Usage / Limitation |
|---|---|---|---|---|
| SRC-IT-F04-MYBOOKINGS | testcase | review target | needs_review | representation_quality: partial |

## 5. Selected Task Lens / Mode
- Lens: Testcase Review

## 6. Execution Steps
1. Read Wiki Source Meta.
2. Open artifact_locator markdown.
3. Review visible testcase rows.
4. Mark missing/unclear conversion areas.
5. Produce review report.

## 7. Guardrails / Constraints
- Do not infer content from original Excel if not represented.
- If key info is missing, mark source_representation_quality_issue.
- Ask for better conversion/HUMAN confirmation if needed.

## 8. Open Questions / Blockers
- Hidden sheets/formulas may not be represented. This may block final review.

## 9. Done Criteria
- Review report created with limitations clearly stated.
```

## 9.5. Readiness

If final review depends on hidden/missing data: `not_ready` until conversion/HUMAN confirmation.

If only visible rows are in scope: `lite_ready` or `execution_ready` with limitation.

---

# 10. Cross-sample checklist

Across samples, check:

```markdown
- [ ] HUMAN task request reflected
- [ ] Task Lens/mode recorded if used
- [ ] Wiki/source references selected and role-defined
- [ ] Workspace context selected, not dumped
- [ ] Working AIP exists for non-trivial task
- [ ] Readiness checked
- [ ] aiws-aip run points to Working AIP
- [ ] source_representation_quality_issue handled if relevant
- [ ] promotion candidates not treated as approved
- [ ] Done criteria clear
```

---

# 11. Conclusion

WAC-08 provides sample flows showing how Working AIP Connection works across common task types.

Core lesson:

```text
Do not jump from context discovery to execution.
Connect selected context into Working AIP, check readiness, then execute.
```

Next: WAC-09 Relation to Controlled Knowledge Promotion / Lookback.
