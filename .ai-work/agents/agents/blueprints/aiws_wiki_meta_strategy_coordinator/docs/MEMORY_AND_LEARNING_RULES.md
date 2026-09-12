# Memory and Learning Rules — Wiki Meta Strategy Coordinator

> Docs-parity set added by CR-AIWS-2026-07-017 (blueprint predates the docs convention).
> The operative lifecycle rule lives ONCE in `../../_shared/common/lesson_capture_rule.md`
> (pack-level); this file is the blueprint-local summary + coordinator specifics. Do not fork it.

## 1. Core rule (no auto-promotion)
Run output is evidence. Learning candidate is a proposal. Confirmed memory requires HUMAN approval
(/aiws-agent-review-learning). Never auto-update Official Wiki / blueprint / own process silently.

## 2. Instance memory files (5) — created EMPTY
`confirmed_memory.jsonl`, `lessons_learned.md`, `local_guidelines.md`, `retrieval_hints.jsonl`,
`tool_usage_notes.md` (coordinator memory_profile). Seed ONLY HUMAN-approved content.

## 3. Learning candidate types
Per `../../../templates/learning_candidate_schema.md` (11 kinds incl. `digest_synthesis_candidate`).
Coordinator-typical: lesson_candidate (strategy pattern), retrieval_hint, wiki_candidate,
digest_synthesis_candidate (e.g. a source-area orientation digest), blueprint_improvement_candidate.

## 4. Capture routing (AP-CR-13)
Under an AIP -> tier capture up to the Task Workspace `08_capture_inbox.jsonl`; instance keeps a
pointer. Without an AIP -> `training/candidate_queue.jsonl`. Promotion HUMAN-gated either way.

## 5. Confirmed-memory loading — relevance-scoped (AP-CR-26; CR-AIWS-2026-07-017 parity)
Loader is blueprint-agnostic: always-on + task-relevant entries load in full (ARC §5.1); ALL indexed
(ARC §5.2); retrieval hints + digests surface in ARC §5.3. Schema/tagging:
`../../../templates/confirmed_memory_schema.md`. `load_cap`/`load_order` = declared fallback, not enforced.

## 6. Periodic improvement (HUMAN-driven)
After ~5 runs / phase end / every ~2 weeks: review candidate queue -> HUMAN confirm/defer/reject ->
`training/periodic_review_log.md`.
