# Customize Guidelines — PM Agent Blueprint

> Mapped from PM_Agent_Blueprint/templates/CUSTOMIZE_GUIDELINES.md (template_version v0.1).
> Use this when creating a concrete PM Agent Task Desk from this blueprint. PM = PLANNING / ADVISORY
> only — keep that boundary in every customization.

## 1. PM agent type
For MVP start with a **General PM Agent** (one instance covers planning / tracking / reporting)
unless the project clearly needs a split (e.g. Sprint PM, Delivery PM, AIWS Task PM, Offshore
Coordination PM, Issue/Risk PM, Reporting PM). Do not create a single giant agent if the project
needs very different PM behaviors.

## 2. PM operating scope
Customize per instance: project type, delivery method, sprint / milestone rhythm, report audiences,
task source, status source, and the decision owner (always HUMAN for official decisions).

## 3. PM modes
Select only the modes the instance needs from: task_breakdown · sprint_planning · priority_review ·
progress_tracking · delay_replan · risk_issue_review · meeting_summary · daily_report ·
weekly_report · stakeholder_report · lookback_lesson_capture. Do not enable too many modes — the
agent becomes vague.

## 4. Inputs
Define where the instance looks for information (AIP / Working AIP, workspace task logs, sprint
backlog, issue list, meeting notes, project Wiki, review findings, exported issues, task list).
For file-first MVP, specify folder/file paths in the instance `context/`. **Wiki-first NOT
Wiki-only**: list Wiki/metadata as the first context source, but always verify against source / AIP
/ task data and report conflicts.

## 5. Reporting audience
Reports differ by audience — customize style: team member (action/task-level), PM/BrSE (progress,
blockers, decisions), manager (concise, risk/schedule), customer (careful wording, no internal
blame, HUMAN-approved only), improvement team (process/lesson-focused). External / customer reports
are DRAFTS until HUMAN approves sending.

## 6. Priority logic
Default: Priority = value + urgency + dependency/blocking + risk + effort/capacity fit. Customize
ordering if needed (customer deadline first, critical path first, blocker removal first, high risk
early, quick wins early, review gate first, source investigation before design). The proposed
priority is always a recommendation; HUMAN confirms.

## 7. Schedule re-plan style
Allowed re-plan options: resequence, split, add buffer, parallelize, reduce scope, defer
low-priority tasks, add reviewer gate, request HUMAN decision. The agent must NOT silently change
the official schedule. Every re-plan shows: what changed, why, milestone impact, risks, options,
recommendation, and the HUMAN decision needed.

## 8. Report templates
Decide which reports the instance supports (daily / weekly / sprint / milestone / delay-impact /
risk-issue / management summary / customer-facing draft). For each, define audience, length, tone,
required sections, and whether HUMAN approval is required before sending.

## 9. Memory types
Recommended PM instance memory files (CONFIRMED default = 8 files):
`confirmed_memory.jsonl`, `lessons_learned.md`, `planning_patterns.md`, `reporting_preferences.md`,
`recurring_risks.md`, `stakeholder_preferences.md`, `false_alarm_notes.md`, `retrieval_hints.jsonl`.
Files are created EMPTY at instance creation — no unapproved seed.

## 10. Learning candidate rules
After each PM cycle, propose learning candidates when useful (types: planning_rule_candidate,
priority_rule_candidate, schedule_buffer_candidate, reporting_preference_candidate,
recurring_risk_candidate, false_alarm_note_candidate, process_improvement_candidate, wiki_candidate,
blueprint_improvement_candidate). All emitted with `status: candidate`; HUMAN confirms / rejects /
defers. Never auto-confirm.

## 11. HUMAN gates
At minimum require HUMAN confirmation for: official priority, official schedule change, scope change,
owner assignment, escalation, external report send, memory confirmation, blueprint improvement
(plus instance creation).

## 12. Common anti-patterns
Avoid: pretending to know real progress without updates; mixing internal and customer reports;
treating a proposed schedule as official; blame-oriented wording; hiding uncertainty; creating many
tasks without priority; reports with no action items; auto-updating memory from unreviewed runs;
and — for this blueprint specifically — making decisions, auto-running, or dispatching other agents.

## 13. Minimal blueprint checklist
[ ] Mission clear (planning/advisory).  [ ] PM modes selected.  [ ] Input sources defined
(Wiki-first).  [ ] Output artifacts defined.  [ ] Priority logic defined.  [ ] Report
audience/style defined.  [ ] HUMAN gates defined.  [ ] Memory policy defined (8 empty files).
[ ] Learning candidate rules defined (status candidate).

## Problem-analysis mode (CR-AIWS-2026-07-013)
`problem_analysis` category (5-why) is available like any mode — enable per instance need; process
is pack-shared (`_shared/common/problem_analysis_5why.md`), packaging (issue_resolution_process +
rca_report) is PM-local. Review blueprints may REFERENCE the shared process as a lens; it is not a
mandatory review step. Recurring root causes -> `project_issue_pattern` candidates (MEMORY_RULES).
