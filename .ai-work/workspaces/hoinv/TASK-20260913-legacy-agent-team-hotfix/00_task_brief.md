# Task Brief

## Task ID
TASK-20260913-legacy-agent-team-hotfix

## Plan Source
→ See `01_plan_source.md` (AIP reference + version)

## Goal
Legacy Agent Team hotfix

## Expected Output
Lead-only readiness, one-action approved `## Tasks` import, canonical installed verification, durable review evidence, and exact HUMAN acceptance.

## Primary Mode
Executing and verifying.

## Supporting Modes
Independent code review, integration review, AIWS governance.

## Scope Notes
Isolated legacy packages only: `packages/core`, `packages/tools`, `packages/web`, compatibility/verification artifacts, and this mission/workspace. Excludes `packages/gat`, the separately owned multi-mission controls, and live GUI activation.

## Step Outputs
→ See `step_outputs/README.md` (handoff registry)

## Current Status
<!-- The AIP's own frontmatter `status:` is authoritative; the close gate reads THAT, not this
     section (CR-AIWS-2026-08-125 C1). This is a human note, not machine state — do not keep a
     second copy of the status here and expect anything to honour it. Close with
     `py .ai-work/tooling/run_aip.py close <AIP-ID>`. -->
Implementation and canonical verification complete; final independent review and HUMAN acceptance pending.

## Runtime Artifacts
- Runtime Queue: `02_runtime_queue.jsonl`
- Legacy Queue Alias: `02_investigation_queue.jsonl` (old workspaces only)
- Capture Inbox: `08_capture_inbox.jsonl`
