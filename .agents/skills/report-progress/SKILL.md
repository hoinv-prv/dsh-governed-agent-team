---
name: report-progress
description: Generate a standalone HTML WBS progress dashboard for daily or on-demand status reporting. Trigger when the HUMAN asks for a daily report, progress report, WBS status, Gantt chart, HTML dashboard, what happens next, or what the HUMAN must do. Reporting is read-only for mission controls and never starts/resumes/verifies/accepts work.
user-invocable: true
---

# Report WBS progress as standalone HTML

Use this skill for daily or on-demand WBS progress reporting.

## Contract

- This is a **status/report operation**, never execution permission.
- Read WBS plan(s), `execution.json`, `decisions.json`, and referenced evidence only as needed.
- Write only the requested/default HTML report; never edit WBS, execution, decisions, evidence, AIP, or source code.
- Distinguish the selected execution revision from a newer HUMAN-approved-but-unselected revision.
- Derive the task denominator from the approved WBS task list, not legacy tasks retained in the execution ledger.
- Do not rerun task verification, start/resume work, dispatch agents, or change acceptance.
- HTML must be standalone: no Mermaid, external URLs, scripts, fonts, npm/pnpm, or network.

## Mission resolution

1. If the HUMAN names a mission id/root, use it.
2. Otherwise select only when exactly one `wbs-runs/*/execution.json` has `run_state: active`.
3. Zero or multiple active missions is ambiguous: stop and ask the HUMAN which mission to report.

## Generate

From project root:

```bash
node .agents/skills/report-progress/scripts/render-progress.mjs \
  --mission-root wbs-runs/<mission-id>
```

Optional deterministic date/output:

```bash
node .agents/skills/report-progress/scripts/render-progress.mjs \
  --mission-root wbs-runs/<mission-id> \
  --date YYYY-MM-DD \
  --output wbs-runs/<mission-id>/WBS_PROGRESS.html
```

Default output is `<mission-root>/WBS_PROGRESS.html`. Output must remain inside the mission root and end in `.html`.

## Required report sections

- selected revision vs latest HUMAN-approved revision and exact approved hash;
- accepted/touched task progress;
- attempts charged/cap/remaining;
- WBS dependency view;
- logical Gantt (explicitly non-calendar);
- task state/attempt/deliverable table;
- next coordinator actions;
- what the HUMAN must do now and at later gates;
- explicit read-only reporting disclaimer.

## Verification before reporting

- Renderer exits 0 and returns JSON summary.
- Summary matches authoritative selected/approved revisions and attempt totals.
- Inspect the generated HTML for the mission id and required sections.
- Confirm no mission-control hash changed; the renderer enforces this around generation.
- Present the HTML file to the HUMAN.

## Daily usage

When asked “report daily”, “daily progress”, “báo cáo tiến độ hôm nay”, or equivalent, regenerate the same mission HTML with the current date and summarize only material changes since the authoritative records. Do not invent calendar ETA from the logical Gantt.
