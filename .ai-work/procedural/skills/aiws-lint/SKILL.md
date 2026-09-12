---
name: aiws-lint
description: >
  Deterministic lint domain — chạy lint AIP / workspace / wiki entry / Wiki Source Meta + Index rồi
  gộp một báo cáo (`lint_all.py`). VERBS: all (whole-tree, dùng khi finalize canonical / apply CR —
  CR chỉ được flip `applied` khi 0 error) · task (scoped theo workspace + AIP, tự escalate lên
  whole-tree khi footprint chạm `product/`). Dùng khi: "lint", "kiểm tra lỗi", "validate", "check
  AIP/wiki", trước khi finalize bất kỳ AIP nào · "run lint", "lint this task".
user-invocable: true
---

# SKILL: aiws-lint (domain router)

> Consolidated by CR-AIWS-2026-07-025 — the former per-action skills of this domain are now VERBS of this ONE skill.
> **Old-name translation:** `aiws-lint-<X>` → verb `X` (authority: `product/rename_map.json`).

## Router protocol (MANDATORY)
1. Parse the request → pick ONE verb from the table below (NL triggers).
2. **Read `operations/<verb>.md` (this folder) BEFORE executing** — it is the full, authoritative operation definition; every gate in it stays binding.
3. Verb mơ hồ → HỎI HUMAN (safety rule #6). Router adds NO gates, removes NONE.

## Verb routing table
| Verb | Operation | NL triggers | Params | Key gates (full text in operation file) |
|---|---|---|---|---|
| all | operations/all.md | VN: 'kiểm tra lỗi', 'lint toàn bộ' / EN: 'lint', 'run lint', 'validate', 'check AIP', 'check wiki', 'aiws-lint all'; before canonical/CR-apply finalize; before committing wiki changes; in CI on .ai-work/ changes | python .ai-work/tooling/lint_all.py [--strict] [--format text] (default --scope all = whole-tree); exit 0 clean / 1 warnings+--strict / 2 errors | whole-tree = canonical/CR-apply finalize lint (CR-067) — a CR flips `applied` only after 0 errors; lint is a guardrail not a reviewer; do not ask the tool to auto-fix wiki or truth; --strict = warnings treated as errors; treat warnings as 'please look before m |
| task | operations/task.md | VN: 'lint task này', 'lint scoped' / EN: 'scoped lint', 'lint this task/workspace'; finalize of a task execution — invoked by aiws-aip run step 7 | python .ai-work/tooling/lint_all.py --scope task --workspace <ws> --aip <aip> [--strict] [--format text] (workspace + aip mandatory); exit 0/1/2 as above | mandatory AIP + Task-Workspace targets; conditional wiki/index targets when git footprint touched .ai-work/wiki/ or .ai-work/wiki_sources/; MUST auto-escalate to whole-tree when footprint touches product/ or the task applies a CR (CR-067, deterministic git-cha |
