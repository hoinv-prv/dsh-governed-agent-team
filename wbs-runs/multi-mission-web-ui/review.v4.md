# Review candidate multi-mission-web-ui, revision 4

- Plan: `wbs.v4.json`
- Exact SHA-256: `3bfee29f8e6ecc673813f1922ea9857e66cf716979e36f220027c4dd6e6ffd3b`
- Objective, effects, commands, dependencies, and acceptance gates are unchanged from revision 3.
- Delta: core attempt 3 repaired mission-plan validation, but independent review found one API-compatibility mismatch introduced during that attempt: `TeamView.missions` was made required and `remoteView()` always emits `missions: []`, while an existing exact-equality compatibility test expects the legacy empty Team view to omit that property.
- Revision 4 adds one final 15-minute core attempt to restore backward-compatible omission when empty while making the public type optional, retain populated mission lists, update focused tests, and obtain fresh independent review.
- Core max attempts: 3 → 4. Total mission attempts: 8 → 9. Effort ceiling: 530 → 620 minutes (covers all declared task allocations). Four attempts are already charged; no fifth core attempt is available.
- Validation: WBS helper API and workspace inspection passed. Order remains discover → core → Web → integration → final.

Approval authorizes only this compatibility repair/review and the already-declared downstream work. It does not activate GAT in the live Web profile.
