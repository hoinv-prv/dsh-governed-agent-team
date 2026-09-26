---
name: aiws-lint
description: >
  Deterministic lint domain for AIWS: run AIP (ROOT/PLAN/EXEC/LOCAL), workspace, wiki entry, Wiki
  Source Meta and Wiki Source Index lints and aggregate one report (tool:
  .ai-work/tooling/lint_all.py). VERBS: all — whole-tree, the canonical / CR-apply finalize lint
  (a CR flips applied only when clean, 0 errors); task — scoped finalize lint (--scope task
  --workspace <ws> --aip <aip>, used by aiws-aip run step 7), auto-escalates to whole-tree when
  the git footprint touches product/ or the task applies a CR. TRIGGER when: user says "lint",
  "run lint", "kiểm tra lỗi", "validate", "check AIP", "check wiki", "lint toàn bộ", "lint task
  này"; before finalizing any AIP; before committing wiki changes; after creating/updating a Wiki
  Source Meta or Active Step Context; in CI on .ai-work/ changes. --strict treats warnings as
  errors. Lint is a guardrail, not a reviewer — never auto-fix wiki or Truth. covers former
  aiws-lint all skills
user-invocable: true
---

# SKILL: aiws-lint

> **Full definition (common):** [.ai-work/procedural/skills/aiws-lint/SKILL.md](../../../.ai-work/procedural/skills/aiws-lint/SKILL.md)
> Read that router first, then read `operations/<verb>.md` for the chosen verb BEFORE executing.
