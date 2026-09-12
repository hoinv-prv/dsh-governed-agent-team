# Personal Notebook Local Setup Guide MVP

Version: v0.9.4  
Date: 2026-04-25  
Status: Canonical setup appendix / guideline

---

## 1. Purpose

This guide explains how to set up Personal Notebook for MVP usage.

Personal Notebook is file-based in MVP and must be configured explicitly by path.

---

## 2. Recommended folder structure

```text
personal_notebook/
  README.md
  inbox.md
  notes/
  archive/
```

---

## 3. AGENTS.md / claude.local.md snippet

```markdown
## Personal Notebook Configuration

Personal Notebook path:
`./.aiws/personal_notebook/`

Scope:
- This notebook is a personal reference area following this configured path.
- It is not inherently global or project-bound.

Purpose:
- Store selected personal ideas, observations, weak findings, cross-task notes, future sprint ideas, and capture candidates.

Authority:
- This notebook is not source of truth by default.
- Notes must include status / authority / source hints when they may affect reuse or decisions.

AI usage rules:
- AI may read this notebook only when HUMAN asks or when the current task clearly requires personal/cross-task notes.
- AI may write/update this notebook only when HUMAN explicitly asks or confirms.
- AI must not auto-promote notebook content to Knowledge Hub.
- AI must suggest controlled capture when a note appears reusable.
- AI must not treat notebook content as authoritative without checking status/source.
```

---

## 4. README.md template

```markdown
# Personal Notebook

## Purpose
This Personal Notebook stores selected personal ideas, observations, weak findings, cross-task notes, future sprint ideas, and capture candidates for later reference.

## Scope
The scope of this notebook follows this configured folder path.

Configured path:
`<replace-with-path>`

## Authority
This notebook is not source of truth by default.

## Relation to AI Work System
- This notebook is not Workspace findings.
- This notebook is not Working AIP.
- This notebook is not Knowledge Hub.
- This notebook is not Wiki Meta / Index.
- This notebook is not Task Lens.
- This notebook does not auto-promote content into reusable knowledge.

## AI usage rules
- AI may read this notebook when HUMAN asks or when the task explicitly needs personal/cross-task notes.
- AI may write/update only when HUMAN explicitly asks or confirms.
- AI should preserve status / authority / source hints.
- AI must not treat notes as source of truth by default.
- AI may suggest controlled capture if a note appears reusable.
- AI must not auto-promote notes to Knowledge Hub.
```

---

## 5. inbox.md template

```markdown
# Personal Notebook Inbox

Use this file for quick capture.

## Inbox rules
- Keep notes short.
- Add status / authority / source when useful.
- Move mature notes to `notes/`.
- Archive or discard stale notes during review.
- Do not treat inbox notes as source of truth by default.

---

## Notes

### YYYY-MM-DD — Note title

- Status:
- Authority:
- Source:
- Intended use:
- Review needed:

#### Note
...
```

---

## 6. Individual note template

```markdown
---
status: idea
authority: personal
source: self
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
tags: []
review_needed: false
---

# Note title

## Summary
Short summary.

## Note
Main content.

## Intended use
How this note may be used later.

## Source / context
Where this came from.

## Next action
Optional.
```

---

## 7. Minimal setup checklist

- [ ] Personal Notebook path is declared.
- [ ] `README.md` exists.
- [ ] `inbox.md` exists.
- [ ] `notes/` folder exists.
- [ ] `archive/` folder exists.
- [ ] AI read/write rules are documented.
- [ ] authority/source-of-truth warning is documented.
- [ ] no auto-promotion rule is documented.
- [ ] scope of notebook is clear enough.
