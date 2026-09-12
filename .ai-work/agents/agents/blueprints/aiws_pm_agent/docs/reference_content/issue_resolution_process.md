> **REFERENCE SEED (CR-AIWS-2026-08-008 T2)** — domain content, lớp project-local. KHÔNG auto-copy
> khi tạo desk; wizard offer như một nguồn `domain content` (manifest CR-AIWS-2026-08-009).
> Skeleton portable của ATDB không còn chứa file này (content contract: agent_runtime_design §10).

# Issue Resolution Process — PM Agent

> Added by CR-AIWS-2026-07-013. Connects existing PM pieces into ONE resolution loop. Advisory
> throughout (`pm_advisory_boundary` — pm_process.md §6): the agent detects/analyzes/proposes/tracks;
> the HUMAN decides and acts.

## Loop

1. **Detect** — progress_management skills (collect_status, compare_plan_vs_actual, detect_delay /
   detect_blockers / detect_scope_change) surface a candidate issue.
2. **Classify** — risk / issue / blocker / decision-needed (risk_issue_decision skills); log a row in
   `risk_issue_decision_log.md` immediately (id, severity, owner=TBD).
3. **Analyze** — non-trivial issue → run `../../_shared/common/problem_analysis_5why.md`
   (analyze_problem_5why / identify_root_cause_candidates) → `rca_report.md`.
4. **Options** — propose_countermeasures / propose_mitigation: ≥2 options + trade-offs
   (+ replan options via schedule_replan_process.md when schedule-impacting).
5. **HUMAN decision** — present options; record the decision in the decision log (decided_by HUMAN).
6. **Track** — follow-up actions land in the action-item log with owner/due; each subsequent
   progress report checks open follow-ups until closed/verified.

## Guardrails
- No step in this loop executes a fix or changes the official plan — proposals only.
- A recurring issue (≥2 occurrences) → `project_issue_pattern` learning candidate + consider
  countermeasure at the pattern level, not per-instance.
