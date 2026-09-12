# PM Agent Memory and Learning Rules

> Mapped from PM_Agent_Blueprint/templates/MEMORY_AND_LEARNING_RULES_TEMPLATE.md (template_version
> v0.1). NO AUTO-PROMOTION: instance memory starts empty; learning candidates are emitted with
> `status: candidate` and only HUMAN-confirmed candidates update memory.

## 1. Principle
```
Run evidence -> learning candidate (status: candidate) -> HUMAN review
  -> confirmed memory / lesson / process update / blueprint candidate
```
The agent must NOT auto-learn directly from a run.

## 2. Memory types (CONFIRMED default = 8 files; created EMPTY at instance creation)
```text
memory/
  confirmed_memory.jsonl
  lessons_learned.md
  planning_patterns.md
  reporting_preferences.md
  recurring_risks.md
  stakeholder_preferences.md
  false_alarm_notes.md
  retrieval_hints.jsonl
```

## 3. Learning candidate types
```text
planning_rule_candidate
priority_rule_candidate
schedule_buffer_candidate
reporting_preference_candidate
recurring_risk_candidate
false_alarm_note_candidate
process_improvement_candidate
wiki_candidate
blueprint_improvement_candidate
```

## 4. Candidate schema (status always starts at `candidate`)
```json
{
  "candidate_id": "PM-LC-001",
  "source_run": "RUN-YYYYMMDD-001",
  "type": "reporting_preference_candidate",
  "scope": "weekly_report",
  "content": "Weekly report should always include delayed tasks, impact, and recovery action.",
  "evidence": "HUMAN requested this format in two consecutive reports.",
  "recommended_destination": "memory/reporting_preferences.md",
  "status": "candidate"
}
```

## 5. HUMAN review rule
Only HUMAN-confirmed candidates may update: confirmed memory, planning patterns, reporting
preferences, recurring-risk notes, stakeholder preferences, process templates, and blueprint
improvement candidates. The agent never promotes a candidate itself.

## 6. False alarm rule
If HUMAN says a PM warning / risk / delay was not valid, capture it as a
`false_alarm_note_candidate` when it may recur (e.g. "do not mark a task delayed if waiting for a
customer response already recorded as an external dependency with next action on the customer side").

## 7. Periodic PM agent improvement review
Triggers: after 5 PM runs; after sprint end; after a major milestone; every 2 weeks.
Steps: collect recent runs -> summarize repeated planning problems -> summarize reporting feedback
-> identify recurring risks -> identify false alarms -> propose memory/process/checklist updates
-> HUMAN approve/reject/defer -> update memory + changelog.

## 8. Wiki candidates (Wiki-first NOT Wiki-only)
When a PM run surfaces reusable project knowledge, emit a `wiki_candidate` (status `candidate`) — the
agent never promotes to Official Wiki itself. Wiki is consulted first for context but verified
against source/AIP/task data; conflicts are reported, not silently resolved.

## 9. Confirmed-memory loading — relevance-scoped (AP-CR-26; parity per CR-AIWS-2026-07-017)
Loading is relevance-scoped for EVERY instance (runtime loader is blueprint-agnostic): always-on +
task-relevant entries load in full (ARC §5.1); ALL entries are indexed (ARC §5.2). Entry schema +
tagging convention: `../../aiws_detailed_design_review_agent/docs/MEMORY_AND_LEARNING_RULES.md` §8 and
`../../../templates/confirmed_memory_schema.md`. `load_cap`/`load_order` in blueprint.yaml are
declared fallback bounds, currently NOT enforced (CR-017 Apply Outcome).

## 10. Knowledge digests (CR-AIWS-2026-07-017)
Synthesis documents with reuse value (e.g. a project schedule-risk digest) -> `digest_synthesis_candidate`
(aligns playbook trigger #20); on HUMAN confirm via /aiws-agent-review-learning the digest moves to
`memory/knowledge_digests/` + ONE retrieval_hints.jsonl entry (discovery; ARC §5.3). Two-tier
promotion to project wiki via the capture inbox + E2 --materialize. Schema:
`../../../templates/confirmed_memory_schema.md` §Knowledge digests.
