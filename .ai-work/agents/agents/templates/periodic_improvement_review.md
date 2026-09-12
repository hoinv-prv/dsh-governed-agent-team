# Periodic Improvement Review (template)

> Periodic review of an instance's run history + candidate queue. Output is HUMAN-gated.
> Lives at `agents/task_desks/<instance_id>/training/periodic_review_log.md` (append each review).

## Review metadata
- instance_id:
- reviewed_at:
- reviewer: HUMAN
- runs covered:

## Candidate queue review
| candidate_id | type | decision | rationale |
|---|---|---|---|
| LC-… | … | confirm / defer / reject | … |

## Outputs of this review
- confirmed memory updates: <MEM-ids created>
- rejected / deferred candidates: <LC-ids>
- **blueprint_improvement_candidate(s)**: <routed separately — instance does NOT auto-update Blueprint>
- tool_improvement_candidate(s): <…>

## Notes
- No auto-learning: every promotion above is an explicit HUMAN decision.
