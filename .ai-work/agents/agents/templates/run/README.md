# Run folder templates (Detailed Design v0.2 §8)

A run is recorded inside an Agent Task Desk Workspace:
```
agents/task_desks/<instance_id>/workspace/
  active_runs/<RUN-id>/        # while in progress
  completed_runs/<RUN-id>/     # after completion
  handoff_artifacts/           # artifacts passed to other agents (manual handoff)
  step_outputs/
```

## Run-folder naming
```
RUN-YYYYMMDD-HHMM-<short_task_name>/
# e.g. RUN-20260618-1015-sample-strategy/
```

## Run-folder contents (copy these templates)
```
run_request.yaml          # who/why/expected outputs (§8.3)
run_context.md            # the working context for the run
input_manifest.md         # what inputs were loaded
used_references.md        # wiki/source references actually used
used_tools.md             # tools actually used
output/                   # the run's output artifacts
run_log.jsonl             # event log (§8.4) — JSONL
human_feedback.md         # HUMAN feedback on the run
learning_candidates.jsonl # candidates proposed from the run (§14) — JSONL; ships EMPTY (see learning_candidates.example.jsonl for the row shape)
```

## Conventions
- Machine-read state = **JSONL** (`run_log.jsonl`, `learning_candidates.jsonl`). Config = YAML, plain/literal scalars only (OQ-B1).
- A fresh run starts with an **EMPTY** `learning_candidates.jsonl` (no placeholder); the record shape lives in `learning_candidates.example.jsonl` (AP-CR-39). The `.example.jsonl` is NOT copied into run folders.
- A run does NOT auto-confirm anything. Learning candidates require HUMAN review via `/aiws-agent-review-learning`.

> `run_plan.md` (CR-AIWS-2026-07-016) is copied ONLY for plan_first runs (two-phase); other runs never carry it.
