# Personal Notebook Write Skill Lite Spec MVP

Version: v0.9.4  
Date: 2026-04-25  
Status: Canonical skill support spec

---

## 1. Purpose

Personal Notebook Write Skill Lite is a small reusable execution capability that helps AI/HUMAN create, append, and lightly update Personal Notebook notes according to MVP notebook rules.

It exists to make the file-based Personal Notebook usable without requiring a full notebook application.

---

## 2. Scope

Supported MVP operations:

- `init_notebook`
- `append_inbox_note`
- `create_note_file`
- `update_note`
- `mark_capture_candidate`
- `archive_note`

---

## 3. Guardrails

The skill must not:

- become decision authority
- become orchestrator
- update Knowledge Hub
- update canonical docs
- auto-promote notes
- mark content as approved
- treat notes as source of truth
- silently write without HUMAN request/confirmation by default

---

## 4. Customization points

The skill is intentionally customizable:

- folder layout
- filename rule
- required metadata fields
- status vocabulary
- authority vocabulary
- confirmation policy
- sensitivity policy

Local customization is allowed as long as the core guardrails remain intact.

---

## 5. Default input model

```yaml
operation: append_inbox_note
notebook_path: "./.aiws/personal_notebook"
title: "Future sprint idea: Notebook search"
status: "future_sprint_idea"
authority: "personal"
source: "self"
intended_use: "sprint planning"
review_needed: true
tags:
  - aiws
  - notebook
body: |
  Consider a later sprint for notebook search/index support.
```

---

## 6. Default output model

```yaml
status: success
operation: append_inbox_note
written_to: "./.aiws/personal_notebook/inbox.md"
note_title: "Future sprint idea: Notebook search"
warnings:
  - "This note is not source of truth by default."
  - "No promotion to Knowledge Hub was performed."
```

---

## 7. Package location

The MVP package includes a lightweight skill folder:

`payload/skills/aiws-util-personal-notebook/`

This folder contains:

- `SKILL.md`
- templates
- `config.example.yaml`
- optional helper script
