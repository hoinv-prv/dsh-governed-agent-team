# Verification — attempt-gat-govreplan-001

## Result

FAILED. The AIP re-plan content and runtime status were present, but the declared lint command exited 2.

## Exact commands

1. `python3 .ai-work/tooling/lint_aip.py --path .ai-work/aip/hoinv/exec/AIP-EXEC-004-multi-mission-web-ui.md`
   - expected: 0
   - actual: 2
   - summary: 49 errors, 1 warning.
   - cause: newly appended STEP-05 through STEP-11 used compact prose instead of all mandatory AIP step fields (`Objective`, `Recommended Mode`, `Applicable Guidelines`, `Inputs`, `Expected Outputs`, `Done Condition`, `Notes / Constraints`). Existing historical STEP-04 also retained one vague-input warning.
2. `python3 .ai-work/tooling/run_aip.py status AIP-EXEC-004`
   - expected/actual: 0
   - observed fixed Workspace exists, 12 steps, pointer STEP-03, required runtime files present, captures 0, queue 0, backlog 6 open.

## Disposition

No product work was dispatched. WBS revision 15 gives `governance-replan` only one attempt, so this failed verification cannot be retried under revision 15. A new exact reviewed WBS revision is required to authorize one formatting-repair/reverification attempt; all 18 charges remain preserved.
