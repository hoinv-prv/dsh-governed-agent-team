---
name: aiws-aip
description: >
  AIP lifecycle domain — plan and execute tasks under AI Work System governance (workspace-based
  execution, HARD-GATE wiki-first lookup, HUMAN-controlled promotion). VERBS: create (draft AIP
  PLAN/EXEC/LOCAL/review/apply-CR, allocate id, resolve inputs via wiki lookup); run (start /
  resume / step / status / list — orchestrate execution, workspace + Active Step Context, capture
  inbox sweeps, finalize lint); init-workspace (scaffold task workspace); point-step (set
  current-step pointer); build-step-context (materialize 00c_active_step_context.md). TRIGGER VN:
  "tạo AIP", "cần AIP", "lập kế hoạch", "tạo plan", "chạy AIP", "bắt đầu task", "tiếp tục task",
  "nhảy step", "xem status AIP", "tạo/khởi tạo workspace", "chuyển sang step", "tạo/cập nhật
  active step context". EN: "plan this task", "start task", "create AIP", "run/start/resume AIP",
  "resume task", "jump to step", "AIP status", "init workspace", "point to step", "set current
  step", "move to STEP-NN", "build ASC", "rebuild context". Covers former aiws-aip-* skills.
user-invocable: true
---

# SKILL: aiws-aip

> **Full definition (common):** [.ai-work/procedural/skills/aiws-aip/SKILL.md](../../../.ai-work/procedural/skills/aiws-aip/SKILL.md)
> Read that router first, then read `operations/<verb>.md` for the chosen verb BEFORE executing.

## Reminder — capture wiki candidates IMMEDIATELY (applies to verb `run`)


Every time you invoke this skill (`start` / `resume` / `step`), re-read this rule:

- The moment you notice a wiki-promotable item — reusable pattern, spec/impl drift,
  non-obvious convention, HUMAN-confirmed decision, missing wiki knowledge,
  retrieval friction, tooling opportunity — append it to
  `.ai-work/workspaces/<task-id>/08_capture_inbox.jsonl` **right then**.
- Do **not** batch captures to step end or AIP close. Inline-as-you-discover is the default;
  end-of-step is only a final sweep for items missed mid-stream.
- Filter for Knowledge Value (non-obvious + reusable). Don't capture noise.
- Never promote into Wiki / Knowledge Hub directly — promotion is HUMAN-controlled.

Refer to [`.ai-work/procedural/wiki_candidate_capture_playbook.md`](../../../.ai-work/procedural/wiki_candidate_capture_playbook.md) for triggers, kinds, and JSON record format.

## New rules — see canonical for full text

The canonical aiws-aip run SKILL.md gained these sections at 2026-05-12 (ported from an AIWS deployment):

- **Wiki-first preflight at HARD GATE** → [canonical §Wiki-first preflight at HARD GATE](../../../.ai-work/procedural/skills/aiws-aip/operations/run.md#wiki-first-preflight-at-hard-gate) — 3-step preflight before posing HARD GATE clarifying questions; cite wiki path in `Applicable Guidelines` or use `wiki:none` opt-out. Enforced by `lint_aip.py` rule `wiki_first_preflight_at_hard_gate`.
- **When closing an AIP — Target-spec attribution check** → [canonical §When closing an AIP](../../../.ai-work/procedural/skills/aiws-aip/operations/run.md#when-closing-an-aip) — before flipping status `active → done`, grep target specs for AIP-ID and verify Re-plan Log reflects landed changes.
- **Section-number conflict heuristic** → [canonical §Step execution heuristics](../../../.ai-work/procedural/skills/aiws-aip/operations/run.md#step-execution-heuristics) — when an OP-decision pins an occupied section number, append as `§N+1` (next-available adjacent); document in Re-plan Log + target-doc Revision History; do not re-clarify unless intent is ambiguous.

Read the canonical SKILL.md before applying these rules — pointer-only summaries here are a reminder, not a substitute.
