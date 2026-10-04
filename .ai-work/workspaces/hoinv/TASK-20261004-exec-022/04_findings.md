# Findings

## Findings List
- STEP-00 execution and P-01–P-08/API/lifecycle decisions confirmed; see `task-understanding.md` and `approved-decisions.md`.
- Start imported two pending captures with zero malformed entries. Initial ASC was stale due to start's sanctioned AIP writes; resume restored fresh ASC. Captured as CAP-022-03.
- DA sibling is clean at `a8e215433ae050e36e0ba27205701be1a5f114a1`. Candidate DSH checkout `/home/hoinv/deepseek-harness` is dirty at `c1157f7ed448b40c463c1a43fa595b12294fd50d`; it is an observation, not a qualified compatibility target.

## Confirmed Findings
- ...

## Inferred Findings
- ...

## To-Verify Findings
- ...

## Notes
- ...

## STEP-01 — Intended design coverage

Baseline hashes/dirty regions preserved; approved formal delta applied to AD §9, BD §10, DD §5 and Durable integration baseline before code. Matrix in design-source-test-matrix.md. Independent reviewer identified legacy queued wake, cutoff exception and lifetime races; intended DD §5 clarified before corrections. Disposable verification target /tmp/gat-exec022-verify uses manifest-compatible DSH c291e7961a515f6d7af9304e7fd1d257929aef26. Source main remains untouched. Harness required native-system build; first actual source regression 115 passed/1 fixture failure, migrated by Luna.

## STEP-02 — Attachments and normalized initialization

Member-only event v3 writes and strict v2 replay, bounded detached JCS envelopes/digests, transient registry pins and full-roster preflight implemented. Invalid later specs produce zero rows/children. Safe summaries exclude payload/ref/workspace; unqualified bindings are excluded from readiness and all legacy wake paths. Tests included in final source report.

## STEP-03 — Generic lifecycle

Prepared ownership, reserved-port success/failure traces, active-commit uncertainty, same-generation retry, serial reconstruction, shared bounded cleanup and observed late acquisitions implemented. Review identified and corrected microtask handoff race and early recovery reservation leak. Actual host qualification is not inferred from fake ports.

## STEP-05 — WK adapter

Separate packages/durable-agent strict loader, immutable payload checks, trusted workspace/service/route checks and shared exclusive coordinator implemented. Real public provider in disposable temporary storage preserves approved memory across release/recovery; candidate stays unconfirmed.

## STEP-06 — Scoped contributions

Executable closed-schema read/candidate handlers and bounded coherent refresh use exact scope checks before/after async calls. Cutoff removes contributions immediately and withholds late bodies; cleanup is memoized with pending ownership quarantine. Direct-continuable strict denial is qualified; isolated known-closing T17–21 not applicable.

## ASC refresh requested by HUMAN

Rebuild per-step contexts via run_aip/build_active_step_context, archive snapshots in step_contexts and keep current pointer at STEP07 prerequisite gate. step-status.md distinguishes source-port evidence from open production gates. Generated upstream ordinal labels are a captured tooling issue (CAP02204), not an acceptance judgment.

## STEP-07 — Final independent verification evidence

Current source run: 235 PASS / 19 files. Installer CLI tests: 11 PASS. Host/client aggregate types and bundles, Web build, core built smoke and plain Node adapter export smoke pass in disposable compatible checkout. Default dry-run/install/status (94 files structural PASS)/rollback pass in separate disposable checkout. Real registered attached child/profile and production dispatch remain unqualified. Browser replay: 2 PASS / 1 FAIL; golden model names differ from unchanged HEAD team-config defaults. Failure retained in verification/browser.log, CAP-022-06 and RQ-022-03.

Capture closing sweep reviewed design/source/test/build/installer evidence: six candidates retained for HUMAN review, no relation-update candidates, no wiki promotion. Full AIP is not closed. Strict scoped lint and whole-tree baseline warning status are recorded in verification/README.md.

## Commit follow-up and final qualification boundary

Both ASCs were refreshed before staging on HUMAN request. Closed AIP-023 supplies source/artifact prerequisites; RQ-022-01/02 are resolved from its exact receipt. Production binder/package/profile/compatibility work and browser finding remain open. The staged commit gate found mechanical format/completion-type issues in imported files; forward formal DD §7 intent preceded corrections, and all eleven corrected files have exact normalized JavaScript equality. Affected checks pass (GAT 271; Connection/Gateway 451). Broader normal-config typed lint reports 172 existing-origin findings and remains explicitly RED; RQ-022-05 tracks its final qualification disposition. Commit authorization does not close AIP-022 or approve deployment.

### Local commit receipt — 2026-10-04

DSH commit `5c02ce9f3e44dfce3f87498f65cf684194ad4572` contains exactly the 244 approved paths; commit hooks changed no checked source bytes. Current commit qualification is in ../TASK-20261004-exec-023/commit-receipt.json. Prior qualification/patch receipts remain historical. AIP-022 remains active at STEP-07 with RQ-022-03/04/05 open. Its six captures still require triage before closure; final production acceptance and STEP-08 review remain pending.
