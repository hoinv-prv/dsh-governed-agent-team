# Issue / Warning List — J-1 Scoped E2E  (MOCK)

> **Status: HISTORICAL — point-in-time record, kept for provenance (formalized by CR-AIWS-2026-08-036).** Không phản ánh trạng thái hiện tại — xem `PACK_VERSION.md` + `docs/rollout/known_limitations_and_backlog.md`. Built by AIP-EXEC-141 (Phase J-1) STEP-01 from the scoped E2E run
> (review + PM only; MOCK). Records any defect/observation seen while dogfooding the runtime commands.
> **Policy:** small staging issues may be fixed in place; agents are **NOT** re-scoped here (that would
> be a separate AIP). Severity: Blocker / Major / Minor / Note.

## Summary

The chained E2E (DDR → testcase → PM, 3 runs via `/aiws-agent-run start`) ran **clean** — no blocking
defect. All runs scaffolded, materialized a correct ARC, accepted hand-written `output/`, reconciled
`active → completed`, and `/aiws-agent-feedback` emitted a candidate without touching confirmed memory.
The items below are minor ergonomics / consistency observations.

## Items

| ID | Severity | Area | Observation | Disposition |
|---|---|---|---|---|
| W-01 | Note | `run_agent.py` template copy | A freshly scaffolded run's `learning_candidates.jsonl` is seeded from `agents/templates/run/learning_candidates.jsonl`, which ships **one placeholder row** (`agent_instance_id:"<instance_id>"`, `content:"<learning content…>"`). The AI must **overwrite** it with real candidates (as done this run), else a placeholder leaks into evidence. | **Keep as-is (by design fill-in example), documented.** Authoring/user guides note "overwrite the placeholder candidate row". No code change — changing the template default is out of J-1 scope. |
| W-02 | Note | `run_agent.py` `run_state.yaml` notes | The `notes:` field is truncated to 120 chars from `--task` on `start` (`run_state` writer). For long task prompts the note is cut mid-word until the AI rewrites it. The AI rewrites `notes` on completion (done this run), so final state is fine. | **Keep as-is**, documented. The 120-char cap is intentional (one-liner). No change. |
| W-03 | Note | Handoff ergonomics | Handoff between legs is a **manual file copy** by the operator (by design — HUMAN-controlled, no auto-chain). There is no helper to copy an upstream `output/` into a downstream `input/`; the operator does it directly. | **Intended guardrail, not a defect.** A future (post-MVP) convenience helper could be considered in J-2, but auto-chaining must remain prohibited. Logged to backlog, not fixed. |
| W-04 | Note | Two-feature fixtures | The reused EXEC-139 fixtures cover two different mock features (order-cancel for DDR; login for testcase). The E2E narrative treats them as one "Sample Project release candidate" so the PM leg can plan a combined backlog. This is a narrative convenience, not a fixture defect. | **Documented in the plan + sample package README.** No change. |

## Defects requiring an agent re-scope

None. No item above touches an agent's blueprint scope or `non_responsibilities`. No agent logic was
changed by this E2E.

## Cross-check against guardrails

- No auto-run / no auto-chain observed — confirmed (coordinator untouched; manual handoff).
- No auto-promotion — confirmed (all `confirmed_memory.jsonl` = 0 bytes post-run).
- Scoped review + PM only — confirmed (build/refresh/consume + wiki-meta + consumer agents NOT run; J-2).
- All fixtures/evidence MOCK — confirmed.
