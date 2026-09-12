# Memory and Learning Rules — Detailed Design Review Agent

> Mapped from: REVIEW_AGENT_BLUEPRINT_TEMPLATE.md §13-§16 + MEMORY_AND_LEARNING_RULES_TEMPLATE.md (template_version v0.1).
> The operative lifecycle rule lives ONCE in the shared lesson-capture rule
> (`../../_shared/common/lesson_capture_rule.md`); this file is the blueprint-local summary +
> detailed-design specifics. Do not fork the shared rule.

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
`confirmed_memory.jsonl`, `lessons_learned.md`, `retrieval_hints.jsonl`,
`common_issue_patterns.md`, `false_positive_notes.md`, `local_guidelines.md`,
`output_preferences.md`, `tool_usage_notes.md`. Seed ONLY HUMAN-approved content.
<!-- CR-AIWS-2026-07-012: count/list corrected to match blueprint.yaml memory_profile (UNION-8). -->

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
Instance memory:        project/module-specific review behavior, retrieval hints, false positives.
Checklist update:       recurring detailed-design review point (-> detailed_design_review_checklist.md).
Wiki candidate:         official project knowledge found during review (HUMAN-gated, source-verified).
Blueprint improvement:  reusable rule for ALL detailed-design review agents.
```
Detailed-design example of a blueprint-level lesson: "Detailed design review should always check
retry/cancel/rollback behavior" -> blueprint_improvement_candidate (not instance memory).

## 5. HUMAN feedback handling
Categorize feedback: valid finding / false positive / severity adjustment / wording preference /
missing review point / wrong source usage / useful lesson. A rejected finding likely to recur ->
`false_positive_note_candidate`. A missing review point -> `checklist_update_candidate` /
`review_rule_candidate` / `blueprint_improvement_candidate`.

## 6. Periodic improvement (HUMAN-driven)
Suggested triggers: after ~5 runs, after a major review phase, every ~2 weeks of active use, on
repeated false positives, or on HUMAN request. Periodic output (candidates only): agent improvement
review, confirmed-memory update candidates, checklist update candidates, blueprint improvement
candidates. All HUMAN-gated.

## 7. Capture routing by run context (AP-CR-13)
Under an AIP -> tier capture up to `08_capture_inbox.jsonl`; instance keeps a pointer. Without an AIP
-> capture stays in `training/candidate_queue.jsonl`. Promotion is HUMAN-gated either way.

## 8. Confirmed-memory loading — relevance-scoped (AP-CR-26)
A run does NOT dump the whole `confirmed_memory.jsonl`. It loads **always-on + task-relevant** entries
in full (ARC §5.1) and **indexes ALL** entries (id + tags + 1-line `applies_when`) so nothing is
hidden (ARC §5.2). Matching is deterministic stdlib (token overlap + separator-stripped substring,
so `function:f02` matches "F-02") — no embeddings, no-pip. The index + AI judgment are the safety net.

### 8.1 Entry schema (`memory/confirmed_memory.jsonl`)
Required: `id`, `type`, `confirmed_by` (= HUMAN), `content`. Optional loading hints (AP-CR-26):
- `scope_tags` — array of tags; the special tag `always` = load every run.
- `applies_when` — 1-line condition describing when the entry is relevant.

```json
{"id":"CM-004","type":"domain","confirmed_by":"HUMAN","applies_when":"Reviewing the F-02 Search Room design.","scope_tags":["function:f02","topic:search"],"content":"F-02 capacity rule: room capacity validated against booking count; check the seat-vs-room count table gotcha."}
```

### 8.2 Always-on vs task-scoped convention
- **Always-on** = cross-cutting methodology / process / Wiki-first guidelines that apply to every
  review. Tag `["always"]`. Keep this set **small** — it is paid on every run.
- **Task-scoped** = function/topic specifics. Tag by `function:<id>` / `topic:<name>` and add a
  1-line `applies_when`. The growing tail of project knowledge lives here and loads **selectively**
  when the task overlaps its tags/condition.

### 8.3 Backward-compat
An entry with **neither** `scope_tags` nor `applies_when` = **always-load** (never hidden).
Legacy untagged memory keeps working unchanged.

### 8.4 Who populates these
The review-learning loop populates `scope_tags` / `applies_when` **at confirm time**: the agent
**proposes** them on a learning candidate (always-on vs task-scoped, with tags + condition), the
**HUMAN approves** on promotion (no auto-confirm — §1). Mis-scoped entries are corrected the same
HUMAN-gated way.

## 9. Knowledge digests (CR-AIWS-2026-07-017)
Synthesis documents with reuse value -> `digest_synthesis_candidate` (aligns playbook trigger #20);
on HUMAN confirm via /aiws-agent-review-learning the digest moves to `memory/knowledge_digests/`
+ ONE retrieval_hints.jsonl entry (discovery; ARC §5.3). Two-tier promotion to project wiki via the
capture inbox + E2 --materialize. Schema: `../../../templates/confirmed_memory_schema.md` §Knowledge digests.
