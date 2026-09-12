# Learning Loop Lifecycle (Detailed Design v0.2 §13)

Reuses the AIWS capture → triage → HUMAN-gate mechanics (D2 — thin instance-scoped wrapper, NOT a parallel subsystem).

## Flow
```
Agent Run evidence (workspace/completed_runs/<RUN>/)
  -> learning_candidates.jsonl            (per-run proposals)
  -> training/candidate_queue.jsonl       (instance queue)
  -> HUMAN review (/aiws-agent-review-learning)
       -> confirm  -> memory/confirmed_memory.jsonl  (+ lessons_learned / local_guidelines / retrieval_hints)
       -> defer    -> stays candidate (status: deferred)
       -> reject   -> status: rejected
```

## Blueprint improvement (separate route — FR-AI-05)
```
Instance learning with reusable value
  -> blueprint_improvement_candidate (training/)
  -> HUMAN review
  -> future Blueprint version    (NEVER automatic; instance memory does not update the Blueprint)
```

## Invariants
- **No auto-learning** — candidates never auto-promote to confirmed memory (FR-MEM-04).
- Confirmed memory traces to a `source_candidate` + `confirmed_by: HUMAN`.
- Blueprint improvement is separate from instance memory.
- Machine-read state = JSONL; config = plain/literal YAML (OQ-B1).
