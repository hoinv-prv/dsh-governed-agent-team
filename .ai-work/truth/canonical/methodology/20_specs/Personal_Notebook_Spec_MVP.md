# Personal Notebook Spec MVP

Version: v0.9.4  
Date: 2026-04-25  
Status: Canonical MVP spec  
Scope: Personal Notebook only

---

## 1. Purpose

This spec defines **Personal Notebook** for the AI Work System MVP.

Personal Notebook is a **file-based personal working reference area** for BrSE/HUMAN, configured outside task Workspace and Working AIP, used to preserve selected personal ideas, observations, weak findings, cross-task notes, future sprint ideas, and capture candidates for later reference.

Personal Notebook is designed to be usable in MVP without requiring a dedicated UI, database, search framework, or governance system.

---

## 2. Core definition

Personal Notebook is:

- personal / BrSE-HUMAN owned
- file/folder-based in MVP
- configured by local setup path
- separate from Workspace findings
- separate from Working AIP
- separate from Knowledge Hub
- not source of truth by default
- not auto-promoted into Knowledge Hub

Its effective scope follows the configured notebook path.

---

## 3. Scope rule

Personal Notebook is not inherently global and not inherently project-bound.

The effective scope is defined by the configured notebook path in one of the following:

- `AGENTS.md`
- `claude.local.md`
- equivalent AIWS local setup/config file

Examples:

```markdown
Personal Notebook path: `./.aiws/personal_notebook/`
```

or:

```markdown
Personal Notebook path: `~/aiws/personal_notebook/`
```

---

## 4. Boundary rules

Personal Notebook is not:

- Workspace findings
- Working AIP
- Knowledge Hub
- Wiki Meta / Index
- Task Lens
- AIP Template
- source of truth by default
- task execution artifact
- automatic capture/promote pipeline
- dumping ground for unrelated content

---

## 5. Relationship to Workspace findings

Workspace findings cover task-bound notes and active task/session state.

Personal Notebook covers personal/cross-task notes not tied to a specific Workspace or Working AIP.

Decision rule:

- If a finding supports the current task directly, store it in Workspace findings.
- If it affects the current execution basis, reflect it into Working AIP or a task artifact.
- If it is personal/cross-task/future reference, store it in Personal Notebook.

---

## 6. Relationship to Knowledge Hub

Personal Notebook is not Knowledge Hub.

A Personal Notebook item may become a **capture candidate** if it has reusable value. It must go through controlled capture before it can become Knowledge Hub content.

Rules:

- `capture_candidate` is not promotion.
- AI must not auto-promote Personal Notebook content to Knowledge Hub.
- Source/status/authority must be clarified before promotion.
- HUMAN or an appropriate role decides whether to promote.

---

## 7. Authority and source-of-truth stance

Personal Notebook content must not be treated as source of truth by default.

Recommended status values:

- `idea`
- `observation`
- `weak_finding`
- `cross_task_note`
- `future_sprint_idea`
- `capture_candidate`
- `source_backed_note`
- `reference_only`
- `open_question`
- `archived`

Recommended authority values:

- `personal`
- `personal_observation`
- `unverified`
- `source_backed`
- `candidate`
- `reference`

If a note is used for decision or reuse, it should include enough:

- status
- authority
- source
- intended use
- review needed flag

---

## 8. File-based MVP representation

Recommended MVP structure:

```text
personal_notebook/
  README.md
  inbox.md
  notes/
  archive/
```

### README.md
Defines purpose, scope, authority stance, AI read/write rules, and no-auto-promotion rule.

### inbox.md
Quick capture area for ideas, weak findings, observations, future sprint ideas, and capture candidates.

### notes/
Topic/date-specific notes.

### archive/
Inactive but retained reference notes.

Markdown is the default practical format. YAML frontmatter is optional.

---

## 9. Minimal lifecycle

Personal Notebook lifecycle in MVP:

1. Create
2. Update
3. Review
4. Compact / reorganize
5. Archive
6. Discard
7. Mark as capture candidate when reusable value exists

AI should not delete, promote, or rewrite aggressively without explicit HUMAN instruction or local rule.

---

## 10. AI behavior

AI may read Personal Notebook when:

- HUMAN asks
- task explicitly requires personal/cross-task notes
- local setup allows it and the task context justifies it

AI may write/update Personal Notebook only when:

- HUMAN explicitly asks
- HUMAN confirms AI's suggestion
- local workflow clearly allows it

AI must not:

- silently save arbitrary content
- treat notebook notes as authoritative by default
- auto-promote to Knowledge Hub
- overwrite uncertainty/status/source hints
- store sensitive/confidential content without appropriate scope and explicit instruction

---

## 11. Capture candidate handling

A note may be marked as capture candidate when it contains:

- reusable rule
- reusable pattern
- project/common guideline candidate
- useful terminology clarification
- future sprint backlog candidate

Before promotion:

1. identify candidate
2. check source/status/authority
3. decide target scope
4. prepare capture request
5. review by HUMAN / appropriate role
6. update Knowledge Hub through controlled process
7. update notebook status

---

## 12. Write Skill Lite

The MVP allows an optional **Personal Notebook Write Skill Lite**.

The skill may help:

- initialize notebook folder
- append to `inbox.md`
- create note file
- update note
- mark capture candidate
- archive note

The skill must not:

- become decision authority
- become orchestrator
- auto-promote content
- treat notes as source of truth
- rewrite or delete without appropriate instruction

---

## 13. Deferred items

The following are outside this MVP sprint:

- Task Notebook / Workspace Notebook
- notebook search/index framework
- database/UI implementation
- multi-user notebook
- auto-promotion pipeline
- full governance workflow
- scoring/telemetry
- full access control framework

---

# Controlled Knowledge Promotion notebook addendum

Personal Notebook can store any.

It may contain raw ideas, personal notes, incomplete findings, task-local notes, unverified observations, and notes without reusable value yet.

Notebook does not require Knowledge Value.

If a Notebook note later appears useful beyond personal/local context, it may become a Knowledge Promotion Candidate.

Wiki / Knowledge Hub requires clear Knowledge Value before add/update.

---

# v0.9.9 Working AIP Connection notebook addendum

Notebook can store any personal/local note.

Notebook note may feed Working AIP only with role/status/limitation.

Rules:
- Notebook note is not Working AIP.
- Notebook note is not authoritative by default.
- If used in Working AIP, record relevance, authority/status, and limitation.

---

# v0.9.10 Workspace Boundary addendum

Workspace is task/session-bound.

Notebook is personal/local note space that may outlive one task.

At Workspace close, move/copy to Notebook when:
- note is personal/local
- note may be useful later
- note is not suitable for Knowledge Hub
- HUMAN wants to keep it

Workspace should not become long-term personal notebook.
