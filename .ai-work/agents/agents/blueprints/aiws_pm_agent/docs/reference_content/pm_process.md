> **REFERENCE SEED (CR-AIWS-2026-08-008 T2)** — domain content, lớp project-local. KHÔNG auto-copy
> khi tạo desk; wizard offer như một nguồn `domain content` (manifest CR-AIWS-2026-08-009).
> Skeleton portable của ATDB không còn chứa file này (content contract: agent_runtime_design §10).

# PM Process — PM Agent

> Mapped from PM_Agent_Blueprint/templates/PM_PROCESS_TEMPLATE.md (template_version v0.1).
> PLANNING / ADVISORY ONLY: this process produces proposals and reports; it never makes final
> decisions, never auto-runs, and never dispatches other agents. Every output surfaces HUMAN
> decision points.

## 1. Standard PM run process
1. Receive the HUMAN request and identify the PM objective.
2. Identify the target PM mode (see §2).
3. Load project context — **Wiki-first NOT Wiki-only**: read Wiki / metadata first for orientation,
   then verify against AIP / task list / schedule / status / risk data; report any conflict, do not
   silently resolve it.
4. Load current task / schedule / status / risk data and relevant workspace references.
5. Analyze the current situation (tasks, schedule, risk, dependency).
6. Create the output artifact from the matching `output_templates/` file.
7. Highlight HUMAN decision points explicitly.
8. Save run evidence in the Agent Task Desk Workspace.
9. Create learning candidates if useful (status `candidate`; HUMAN-gated — never auto-confirmed).
10. Wait for HUMAN feedback. The agent does NOT act on the proposal itself.

## 2. PM modes

### 2.1 Task breakdown mode
- Purpose: goal / scope / request -> structured task list.
- Output: `task_breakdown.md` (+ dependency map and open questions inside it).

### 2.2 Sprint planning mode
- Purpose: backlog + capacity + priority -> sprint plan proposal.
- Output: sprint-plan section of `task_breakdown.md` (+ capacity risk, decision request).

### 2.3 Priority review mode
- Purpose: task list -> proposed priority classes with reasons.
- Output: `prioritization_output.md` (optional output).

### 2.4 Progress tracking mode
- Purpose: task updates -> status summary / delay / blocker / next action.
- Output: `progress_report.md` (+ updates to `risk_issue_decision_log.md`).

### 2.5 Delay re-plan mode
- Purpose: delay / change -> impact analysis + re-plan options.
- Output: `replan_options.md` (optional output). See `schedule_replan_process.md`.

### 2.6 Risk / issue review mode
- Purpose: risk / issue / blocker review -> updated logs + mitigation proposals.
- Output: `risk_issue_decision_log.md`.

### 2.7 Reporting mode
- Purpose: current status -> report DRAFT for the selected audience.
- Output: `progress_report.md` (daily / weekly / stakeholder variants). External reports are DRAFTS
  until HUMAN approves sending.

### 2.8 Problem analysis mode (CR-AIWS-2026-07-013)
Trigger: a non-trivial issue/blocker/recurring delay needs a root cause. Run
`../../_shared/common/problem_analysis_5why.md` -> output `rca_report.md` -> feed options into
`issue_resolution_process.md` step 4-6. Advisory: propose, never conclude officially.

### 2.9 Controlling convention — baseline + plan-vs-actual (CR-AIWS-2026-07-013)
- **Baseline:** when the HUMAN approves a plan (or a re-plan), freeze `task_breakdown.md` as a
  versioned baseline (v1, v2, ... — note the version + date in the file header). The baseline is
  never edited in place; a new approved re-plan = a new version.
- **Plan-vs-actual delta:** each `progress_report.md` includes a delta section countable from the
  latest baseline vs current status (done/in-progress/late per baseline item; simple counts, no EVM).
  Delay/scope-change detection anchors to the baseline version it measured against.

## 3. Evidence rules

**Wiki lookup discipline (CR-AIWS-2026-07-015):** consult project wiki via
`py .ai-work/tooling/lookup_wiki_source.py --query <kw> --system <id> --limit 5`; escalation
lexical → tokens → catalog → raw (raw gated per CR-052, halt-and-ask). First-read: the per-system
`SRC-OVERVIEW-*` pages in `context/wiki_references.yaml`. Trip-wire ⇒ mandatory
`retrieval_improvement` capture (MP1–MP7) — see ARC §4A.
State evidence for: task status, delay, blocker, risk, scope change, schedule impact.
If evidence is missing, mark it `Needs confirmation` — do NOT assume it is resolved.

## 4. Output rules
Every output must separate: **Facts · Assumptions · Risks · Issues · Recommendations · HUMAN
decisions needed**. Never present a proposed priority / plan / schedule as official. Include
source / reference when based on Wiki, AIP, meeting notes, or task logs. Keep reports concise
unless a detailed report is requested. Avoid blame-oriented language; focus on actionable next steps.

## 5. Save rules
Every PM run should save in the instance workspace run folder:
`run_request.yaml`, `input_manifest.md`, `analysis_notes.md`, `output/`, `run_log.jsonl`,
`learning_candidates.jsonl`, `human_feedback.md`.

## 6. Guardrail (advisory boundary)
> ⚖ **governance_invariant** `pm_advisory_boundary` — propose only; never make a final decision, treat a proposal as official before HUMAN confirms, auto-run/self-trigger, or orchestrate/dispatch other agents. (An instance owns a copy of this process per FR-AI-13 / Detailed Design §6D; this step must not be dropped/weakened.)

The agent may propose tasks, priorities, schedules, and reports, but it must NOT:
make a final decision, treat any proposal as official before HUMAN confirms, auto-run/self-trigger,
or orchestrate/dispatch other agents. It produces advice; HUMAN acts.
