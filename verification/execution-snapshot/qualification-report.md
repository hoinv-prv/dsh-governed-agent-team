# Owning Session snapshot qualification — candidate report

Reviewer/implementer: `/root/qualification_review` (Codex delegated snapshot owner).

Status: final owning snapshot qualification PASS. Final source replay (attempt 13) and built plain-Node replay (attempt 14) use the frozen gat-durable-agent-final-01 public assembly, with zero source/dependency drift and unchanged authored inputs. AIP acceptance remains parent-owned. Built attempts 11 and 12 remain superseded diagnostic runs.

## Design and scope

Implemented the prospective owning-snapshot contract in official `docs/gat-design/DETAIL_DESIGN.md` §10, after wiki-first resolution of `SRC-GAT-DETAIL-DESIGN` and reading the Host snapshot ownership rules. The changes are bounded to `snapshots/session/gat-durable-execution/**` and the scenario-specific raw verifier hook in the existing `snapshots/session/headless.snapshot.ts`. Root copies and receipts reside here. No framework source, normalization policy, new runner, executable, live keys or WK implementation changes were made by this agent.

## Demonstrated behavior

The shipped headless CLI and existing keyless replay transport execute actual public GAT/WK tools. Passive fixture setup seeds two memories via public WK APIs, then recorded model calls create and assign a task with one selected durable-memory reference. The exact fresh task execution reads selected memory successfully, receives a bounded error for the unselected memory, and submits provisionally. Actual Team events close and complete that execution while the task remains in progress until the Lead explicitly accepts it.

An independent verifier checks raw persisted parent/bootstrap/execution logs before normalization or refresh. A passive actual-request observer additionally checks that memory never enters system messages, no body/catalog/intent is loaded in the initial task model request, and the selected body reaches a subsequent model request only as a tool result. The fixture uses the same WK public module constructor as the registered service and guards that underlying service identity. The fresh bootstrap never calls memory tools; neither parent nor bootstrap exposes the task read tool. Candidate/commit/write tools are absent.

The three canonical V4 Session logs contain 58/17/29 rows, respectively. Six owned prompt/schema sidecars were reviewed. There is no unselected memory body in any Session or actual model input. Native tool-result and lifecycle assertions are not derived from normalized expected output.

## Evidence

- `attempt-08.json`: source refresh PASS, no source drift; authored Session outputs and sidecars captured.
- `attempt-09.json`: source replay PASS, no source drift, replay inputs unchanged.
- `attempt-11-built-plumbing.json`: built plain-Node replay PASS, no source drift, superseded diagnostic bundle.
- `attempt-12-wk402-built-diagnostic.json`: built plain-Node replay PASS, no source drift or dependency drift, replay inputs unchanged. Actual Host Cordis is 4.0.4; actual WK package-local declared Cordis is 4.0.2. No compatibility exemption or checker override is involved.

Each receipt records exact command, environment, input/output hashes, source/bundle hashes and full log hash. Attempt 12 additionally records actual dependency realpaths, manifest hashes and runtime hashes before/after. Earlier failed attempts remain preserved with their actual outcomes and any observed source drift.

## Final qualification and limits

- `attempt-13-final-source.json`: final source replay PASS.
- `attempt-14-final-built.json`: final built plain-Node replay PASS.

Both final receipts have zero source/dependency drift and unchanged authored replay inputs; six sidecars remain unchanged. The actual mirrored public library/manifest/README hashes match the assembly receipt. `candidate-copy-manifest.json` binds the exact source, bundle, dependency graph, receipt hashes and byte-identical 17-file distribution copy. This completes the delegated owning-snapshot gate; the parent retains AIP acceptance and remaining mission checks.

This is keyless authored replay evidence over the real shipped CLI, Loader, Session persistence and public Team/WK APIs. It does not demonstrate live model quality, deployed Host ACL/receipt workflow, OS-crash recovery or full unrelated Host suite compatibility. Those claims are not made.
