# Review candidate multi-mission-web-ui, revision 7

- Plan: `wbs.v7.json`
- Exact SHA-256: `80e69bac7c66e1bce2833aacae13f5f8417e6e5b4ce35a31d052b9de39ffc04f`
- Validation: WBS helper structural validation and workspace inspection passed.
- Dependency order, requirements, product writes, external effects, attempts, and effort limits are unchanged from revision 6.

## Why revision 7 is required

Revision-6 AIWS recovery succeeded: AIP-EXEC-004 linted with zero errors, became active, and created the declared workspace at STEP-00. The approved command grants omitted the mandatory `run_aip.py step` transitions needed to execute the remaining AIP steps.

## Exact delta from revision 6

Adds only four exact `python3 .ai-work/tooling/run_aip.py step` commands:
- STEP-01 and STEP-02 under `web-mission-management`.
- STEP-03 under `integration-verification`.
- STEP-04 under `final-review`.

No new attempt, budget, product scope, installer effect, or acceptance criterion is added. Approval permits AIP pointer/context transitions only; it does not activate GAT in the live Web profile.
