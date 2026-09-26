# Review candidate multi-mission-web-ui, revision 2

- **Plan and exact hash:** `wbs.v2.json` — `55955a3b3964413d151a13e2790e9464677fa0adc08c867fb4194f3166010959`.
- **Objective:** multi-mission core and Web UI with independent mission plans/revisions/approvals and lifecycle.
- **Scope:** product writes under `packages/core` and `packages/web`; compatibility regeneration under `compatibility/dsh-0.1.5-rc.2`; coordinator evidence under this mission root.
- **Coverage:** core model/API → independent static review; Web add/list/detail/approve → independent static review; all functional claims → canonical installed-worktree verifier; final requirement conclusion → independent review plus human acceptance.
- **Integration/final tasks:** `integration-verification` and `final-review`.
- **External effects:** rollback and reinstall only the dedicated `/home/hoinv/deepseek-harness/.worktrees/verify-gat-install-0.1.5-rc.2`; canonical verifier may create/remove scratch Git worktrees. It must not modify unrelated dirty files or activate the live Web profile.
- **Exact integration commands:** rollback prior install; regenerate compatibility from `/home/hoinv/deepseek-harness`; install current payload; run `installer/verify.mjs` against the dedicated verification worktree.
- **Limits:** 7 cumulative attempts, 2 already charged; maximum parallelism 2; effort ceiling 440 minutes.
- **Validation:** helper API validation and workspace inspection passed; order is discover → core → Web → integration → final.
- **Revision delta:** preserves revision-1 bytes, attempts, failed verification, and implementation. Replaces invalid standalone source-tree tests with independent static review gates plus the repository's canonical installed-worktree verification. Adds compatibility writes and bounded external verification-worktree effects. Core revision-1 acceptance remains invalid; discover-validation evidence is eligible for reuse after hash reconciliation.
- **Risk:** rollback will refuse if installed verification files drifted; any refusal or canonical verifier failure stops the branch without bypass.

Choose request changes, or approve this exact revision/hash and its bounded execution. Approval does not activate GAT in the live profile or override DSH tool policy.
