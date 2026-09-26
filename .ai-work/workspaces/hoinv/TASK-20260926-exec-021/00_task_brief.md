# Task Brief

## Task ID
TASK-20260926-exec-021

## Plan Source
→ See `01_plan_source.md` (AIP reference + version)

## Goal
GAT baseline sync contract freeze

## Expected Output
- Standalone GAT synchronized to the approved current DSH behavioral baseline.
- Versioned member-binding contract freeze for EXEC-B/EXEC-C.
- Compatibility and preservation evidence with explicit residual risks.

## Primary Mode
Controlled baseline synchronization and contract authoring.

## Supporting Modes
Repository comparison, test verification, installer compatibility analysis, and risk review.

## Scope Notes
- HUMAN confirmed the recommended source direction on 2026-09-26 and requested continuation.
- DSH checkout is read-only behavioral baseline; standalone is the authoring/distribution target.
- Preserve all unrelated existing working-tree changes; no blanket copy/reset/stash.
- Do not implement binder, attachment, two-phase lifecycle, Durable Agent integration, or mission extensions in this EXEC.

## Step Outputs
→ See `step_outputs/README.md` (handoff registry)

## Current Status
<!-- The AIP's own frontmatter `status:` is authoritative; the close gate reads THAT, not this
     section (CR-AIWS-2026-08-125 C1). This is a human note, not machine state — do not keep a
     second copy of the status here and expect anything to honour it. Close with
     `py .ai-work/tooling/run_aip.py close <AIP-ID>`. -->
...

## Runtime Artifacts
- Runtime Queue: `02_runtime_queue.jsonl`
- Legacy Queue Alias: `02_investigation_queue.jsonl` (old workspaces only)
- Capture Inbox: `08_capture_inbox.jsonl`
