# Verification — attempt-gat-govreplan-003

Plan: revision 17, SHA-256 `c7a802e9ba92c1220d378605ed301ffd553f9b48f196d2f63656f9bb2c2ec96b`.

- HUMAN exact-plan approval: `decisions.json#decision-revision-017`, verbatim `Approve v17 và tiếp tục (Recommended)`.
- Preserved prior charges: 20; this reconciliation is charge 21.
- AIP Re-plan Log records the invalid-ASC threat attempt and explicit STEP-06..11 transitions.
- `plan_source` and every active (non-historical) control reference select immutable `wbs.v17.json`; historical STEP-05/re-plan-log references remain bound to revision 16.
- Durable review first found stale active revision-16 wording; the wording was corrected within this attempt before acceptance.
- `python3 .ai-work/tooling/lint_aip.py --path .ai-work/aip/hoinv/exec/AIP-EXEC-004-multi-mission-web-ui.md`: exit 0, errors=0, warnings=0, info=0.
- `python3 .ai-work/tooling/run_aip.py status AIP-EXEC-004`: exit 0; fixed Workspace exists; pointer intentionally remains STEP-03 until threat task executes its separately granted STEP-06 transition; captures 0; queue 0; six historical backlog rows open.
- No package work, DSH access, baseline conformance execution, dependency/network activity, Web change, AIP close, or activation occurred.
