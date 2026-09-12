# aiws-aip — operation: build-step-context

> Operation of the `aiws-aip` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Turn an AIP step into a workspace-local Active Step Context so the runtime
has a short, focused reading surface for the current unit of work — including a
compact orientation header (AIP goal/outcome, step position, downstream contract)
so the step is oriented within the whole AIP without reading it all.

## Tool
`.ai-work/tooling/build_active_step_context.py`

### Example — use pointer
```
python .ai-work/tooling/build_active_step_context.py \
  --workspace .ai-work/workspaces/TASK-20260414-review-mo-update
```

### Example — explicit step
```
python .ai-work/tooling/build_active_step_context.py \
  --workspace .ai-work/workspaces/TASK-20260414-review-mo-update \
  --aip AIP-PLAN-001 --step-id STEP-02
```

## Flow
1. Ensure the workspace exists (skill `aiws-aip init-workspace`).
2. Set the pointer if not yet done (skill `aiws-aip point-step`).
3. Run the tool. It reads the AIP, finds the step, and writes
   `00c_active_step_context.md` with an orientation header (AIP Goal & Outcome /
   Step Map — You Are Here / Downstream-Output Contract; capped via
   `--digest-lines`/`--scope-lines`) + the step fields (Step Objective/Mode/
   Guidelines/Skills/Inputs/Expected Outputs/Done Condition). Lean (CR-036):
   runtime-pointer sections (queue/handoff/capture) render only when populated;
   redundant restatements and never-filled id slots are omitted.
4. Findings and open questions live in `04_findings.md` / `05_open_questions.md`
   (not hand-linked into the ASC); the builder auto-surfaces queue/handoff/capture
   pointers when present.

## Rules
- do not copy runtime state into the AIP
- re-run the tool any time the pointer moves
- the ASC is a projection; the AIP and workspace remain the sources
