# Memory and Learning Rules — Test Case Review Agent

> Mapped from: REVIEW_AGENT_BLUEPRINT_TEMPLATE.md §13-§16 + MEMORY_AND_LEARNING_RULES_TEMPLATE.md (template_version v0.1).
> The operative lifecycle rule lives ONCE in the shared lesson-capture rule
> (`../../_shared/common/lesson_capture_rule.md`); this file is the blueprint-local summary +
> test-case specifics. Do not fork the shared rule.

## 1. Core rule (no auto-promotion)
```text
Run output is evidence.
Learning candidate is a proposal.
Confirmed memory requires HUMAN approval.
```
The agent never auto-confirms a candidate, never overwrites Official Wiki, never updates a checklist
or this blueprint on its own. Agent memory must not override Official Wiki silently — if memory
conflicts with Wiki/source, report the conflict.

## 2. Instance memory files (8) — created EMPTY
<!-- CR-AIWS-2026-07-012 sweep: count/list corrected to UNION-8 (same defect as DDR). -->
`confirmed_memory.jsonl`, `lessons_learned.md`, `retrieval_hints.jsonl`,
`common_issue_patterns.md`, `false_positive_notes.md`, `local_guidelines.md`, `output_preferences.md`,
`tool_usage_notes.md`. Seed ONLY HUMAN-approved content.

## 3. Learning candidate types (status: candidate)
```text
review_rule_candidate
checklist_update_candidate
retrieval_hint_candidate
false_positive_note_candidate
project_issue_pattern_candidate
output_preference_candidate
wiki_candidate
blueprint_improvement_candidate
```
Lifecycle statuses: candidate / confirmed / rejected / deferred / deprecated (Detailed Design v0.2 §14).
Candidate schema + JSONL format: `../../_shared/common/lesson_capture_rule.md`.

## 4. Destination routing
```text
Instance memory:        project/module-specific coverage behavior, retrieval hints, false positives.
Checklist update:       recurring test-case coverage point (-> testcase_review_checklist.md).
Wiki candidate:         official project knowledge found during review (HUMAN-gated, source-verified).
Blueprint improvement:  reusable rule for ALL test-case review agents.
```
Test-case example of a blueprint-level lesson: "Test-case review should always check invalid
status-transition coverage" -> blueprint_improvement_candidate (not instance memory).

## 5. HUMAN feedback handling
Categorize feedback: valid finding / false positive / severity adjustment / wording preference /
missing coverage axis / wrong source usage / useful lesson. A rejected finding likely to recur ->
`false_positive_note_candidate`. A missing coverage axis -> `checklist_update_candidate` /
`review_rule_candidate` / `blueprint_improvement_candidate`.

## 6. Periodic improvement (HUMAN-driven)
Suggested triggers: after ~5 runs, after a major review phase, every ~2 weeks of active use, on
repeated false positives, or on HUMAN request. Periodic output (candidates only): agent improvement
review, confirmed-memory update candidates, checklist update candidates, blueprint improvement
candidates. All HUMAN-gated.

## 7. Capture routing by run context (AP-CR-13)
Under an AIP -> tier capture up to `08_capture_inbox.jsonl`; instance keeps a pointer. Without an AIP
-> capture stays in `training/candidate_queue.jsonl`. Promotion is HUMAN-gated either way.

## 8. Confirmed-memory loading — relevance-scoped (AP-CR-26; parity per CR-AIWS-2026-07-017)
Loading is relevance-scoped for EVERY instance (runtime loader is blueprint-agnostic): always-on +
task-relevant entries load in full (ARC §5.1); ALL entries are indexed (ARC §5.2). Entry schema +
always/task-scoped tagging convention: see `../../aiws_detailed_design_review_agent/docs/MEMORY_AND_LEARNING_RULES.md`
§8 (canonical wording) and `../../../templates/confirmed_memory_schema.md`. `load_cap`/`load_order`
in blueprint.yaml are declared fallback bounds, currently NOT enforced (CR-017 Apply Outcome).

## 9. Knowledge digests (CR-AIWS-2026-07-017)
Synthesis documents with reuse value → `digest_synthesis_candidate` (aligns playbook trigger #20);
on HUMAN confirm via /aiws-agent-review-learning the digest moves to `memory/knowledge_digests/`
+ ONE retrieval_hints.jsonl entry (discovery; ARC §5.3). Two-tier promotion to project wiki via the
capture inbox + E2 --materialize. Schema: `../../../templates/confirmed_memory_schema.md` §Knowledge digests.
