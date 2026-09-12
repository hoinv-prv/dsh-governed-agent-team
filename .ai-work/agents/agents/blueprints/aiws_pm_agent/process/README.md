# PM Agent — process skeleton (ATDB portable layer)

> Skeleton per content contract (CR-AIWS-2026-08-008; `agent_runtime_design.md` §10). Domain-detail
> process của PM (pm_process / prioritization / schedule replan / issue resolution) là **reference
> seed** tại `../docs/reference_content/` — project chọn nhận lúc tạo desk (wizard `domain content`).

## Governance (portable — copied to every desk)

> ⚖ **governance_invariant** `pm_advisory_boundary` — propose only; never make a final decision, treat a proposal as official before HUMAN confirms, auto-run/self-trigger, or orchestrate/dispatch other agents. (An instance owns a copy of this process per FR-AI-13 / Detailed Design §6D; this step must not be dropped/weakened.)

## Portable process references
| Ref | Path |
|---|---|
| Lesson capture (pack-level) | `../../_shared/common/lesson_capture_rule.md` |
| Capture routing (Desk vs TW) | `../../_shared/common/capture_routing_rule.md` |
| Stop-on-self-deviation | `../../_shared/common/stop_on_deviation_rule.md` |
| 5-why analysis | `../../_shared/common/problem_analysis_5why.md` |
| Domain-detail seeds (optional) | `../docs/reference_content/` |
