# aiws-aip — operation: init-workspace

> Operation of the `aiws-aip` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Create a runtime workspace so the task has an externalized execution memory (brief, active AIP,
active step context, queue, findings, capture inbox, draft, final output). **CR-015 v2:** NEW
workspaces land under a per-account folder `.ai-work/workspaces/<account_id>/<task-id>/`
(`account_id` read from `.ai-work/account_info.yaml`; pass `--account` to override). Falls back to
legacy flat `.ai-work/workspaces/<task-id>/` only when no `account_id` is set. Existing flat
workspaces are left untouched (only-new).

## Inputs
- task id in the form `TASK-YYYYMMDD-<slug>`
- (optional) source AIP id/path
- (optional) short goal/title

## Tool
`.ai-work/tooling/init_workspace.py`

### Example
```
python .ai-work/tooling/init_workspace.py \
  --task-id TASK-20260414-review-mo-update \
  --title "Review manufacturing order update dependencies" \
  --aip AIP-PLAN-001 \
  --aip-path .ai-work/aip/plans/AIP-PLAN-001-review-mo-update.md \
  --aip-type plan
```

## Flow
1. Decide the task slug. Keep it short and deliverable-oriented.
2. If a planning/execution AIP exists, pass `--aip` + `--aip-path`.
3. Run the tool. It scaffolds the workspace and fills the brief / active AIP /
   active step context frontmatter.
4. Point the current step with the `aiws-aip point-step` skill.
5. Materialize step context with `aiws-aip build-step-context`.

## Rules
- do not reuse an existing workspace without `--force`; create a new task id.
- do not edit the AIP to absorb runtime state; runtime lives in workspace.
- capture first, curate later: new discoveries go to 08_capture_inbox.jsonl.
