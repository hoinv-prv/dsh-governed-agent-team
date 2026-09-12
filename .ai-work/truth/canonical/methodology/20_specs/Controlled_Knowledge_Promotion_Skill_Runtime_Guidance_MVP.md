# Controlled Knowledge Promotion Skill Runtime Guidance MVP

Version: v0.9.7  
Date: 2026-04-26  
Status: Canonical runtime/skill guidance

---

## 1. Purpose

This document defines MVP runtime guidance for skills related to Controlled Knowledge Promotion.

It covers:
- `knowledge-promotion-lookback`
- `knowledge-hub-add-update`
- `aiws-aip run` lookback support

---

## 2. knowledge-promotion-lookback

Purpose:

> HUMAN-triggered lookback command to extract missed findings, lessons learned, improvement candidates, Knowledge Promotion candidates, and future backlog candidates.

Natural language triggers:
- “Hãy lookback task này và rút ra các điểm cần cải thiện / findings đáng chú ý.”
- “Hãy rà lại chat + Workspace để xem có lessons learned hoặc aha findings nào nên đưa vào Knowledge Hub không.”
- “Hãy xem lại quá trình làm task này và list Knowledge Promotion candidates.”

Guardrails:
- collect candidates only
- no auto-promotion
- no auto-update Knowledge Hub/canonical/AIP/guideline/process
- use Knowledge Value filtering
- distinguish Notebook / Candidate / Wiki

---

## 3. knowledge-hub-add-update

Purpose:

> Controlled skill for assessing and preparing Knowledge Hub add/update operations.

Supported operations:
- add_new_entry
- update_entry
- merge_entries
- replace_entry
- archive_entry
- promote_candidate
- assess_only
- draft_entry

Mandatory behavior:
- run Knowledge Hub Add/Update Checklist
- check Knowledge Value
- classify knowledge role
- check source/context/authority/freshness
- check target fit
- check duplication/conflict
- identify review/approval need
- output decision

Decision values:
- ready_to_add_update
- needs_value_clarification
- needs_source_check
- needs_owner_review
- better_as_appendix
- better_as_guideline
- better_as_backlog
- retain_in_notebook
- retain_in_workspace
- discard_recommended

Important:

> The skill is not approval authority.

Even when HUMAN directly requests adding to Wiki, the checklist still runs before `ready_to_add_update`.

---

## 4. aiws-aip run lookback support

For relevant AIPs with this flow:

```text
AI creates output
  ↓
HUMAN feedback
  ↓
AI fix/revision
  ↓
HUMAN OK / acceptance
```

`aiws-aip run` should remind/check:

```text
Post-feedback Knowledge Promotion Lookback
```

Expected behavior:
- detect feedback/fix/acceptance flow
- remind AI after HUMAN OK
- collect candidates only
- allow HUMAN skip
- record skip reason if useful
- never auto-promote
- never auto-update templates/guidelines/prompts/skills/process

---

## 5. Skip conditions

Lookback may be skipped when:
- HUMAN explicitly skips
- task is trivial
- feedback was only typo/formatting
- no reusable learning exists
- task is pure tool execution
- time/scope constraints require skipping
- AIP marks lookback as not applicable

---

## 6. Deferred

Not defined in MVP:
- exact skill implementation
- exact command file/prompt format
- storage path
- candidate registry
- aiws-aip run state machine implementation
- automated apply-back
- rollback automation
