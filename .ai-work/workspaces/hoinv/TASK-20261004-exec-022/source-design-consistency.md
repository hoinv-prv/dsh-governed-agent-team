# Source/design consistency — AIP-EXEC-022

Inspected 2026-10-04 against approved [Detail Design §5](../../../../docs/gat-design/DETAIL_DESIGN.md#5-approved-implementation-delta--aip-exec-022) and implementation qualification [§6](../../../../docs/gat-design/DETAIL_DESIGN.md#6-implementation-qualification--aip-exec-022), plus the member-binding freeze §§5 and 9. The required wiki-first lookup was used before opening these design inputs. This report records source mapping only; it does not promote or register wiki/canonical material.

## Mapping and status

| Design | Current mapped evidence | Qualification |
|---|---|---|
| DD-15 / BD-12 | Existing sibling Durable service/provider/Consumer evidence plus GAT `packages/durable-agent/src/{initializer,binder,ownership,tools,index}.ts` and adapter tests. | Explicit WK-style adapter library; production host admission and supported profile/installer activation remain gated. |
| DD-16 / BD-13 | GAT core attachment, binder registry, deadline, lifecycle modules; fail-closed gates in core index/roster/mailbox/projection/types and safe tool views; corresponding core/tool/adapter tests. | Foundation + Adapter; production gated. Nonempty attachments fail before child rows, and attached recovery/dispatch paths remain denied pending qualified host integration. |
| DD-17 / BD-14 | No production implementation mapped. | Remains Target: exact authenticated mission/task lease and nested capability enforcement are unqualified. |
| DD-18 / BD-15 | No production implementation mapped. | Remains Target: complete contracted member task runner is unimplemented. |

The adapter persists only the approved binding descriptor and uses trusted WK public service/Consumer interfaces. Source map statuses are explicit and no new `wiki_source_id` values were assigned. Existing wiki registration and collection snapshots remain historical; the new source files are not registered by this mapping task.

## Verification boundary and provenance

This mapping work did not run product tests and does not claim a PASS. Test locations are candidate evidence; suite results and remaining prerequisite ownership are recorded by the root execution in the AIP workspace. Production remains gated by the §6 qualifications: DSH initial materialization/dispatch and cold-resume release are not separable through qualified APIs, the inspected request hook cannot replace rendered prompt content, and exact authenticated mission/task leases plus immutable nested capability ownership are not qualified. No automatic Durable profile or installer activation is claimed.

`docs/gat-design/SOURCE_CODE_MAP.md` is the human-readable locator; `source-code-map.json` carries machine-readable statuses and symbols; `source-baseline.json` refreshes file hashes against actual current worktree bytes and HEADs. The preserved initial baseline remains `.ai-work/workspaces/hoinv/TASK-20261004-exec-022/baseline.json`. Current repository HEADs: GAT `8121d8c13640afa234496af34fdeac727312c5b1`; sibling Durable Agent `a8e215433ae050e36e0ba27205701be1a5f114a1` (clean at inspection).

## Final evidence refresh (STEP-07 active context)

Read the current fresh STEP-07 ASC before checking files. Baseline SHA-256/byte validation found one mismatch: the existing mapped `installer/verify.mjs` entry. Refreshed only that entry to the current file bytes (added verifier-suite coverage); DD-11 already documents the intended design-before-code change. All other baseline entries matched.

`source-code-map.json` validation: every mapped source/test file exists and every declared source symbol is locatable at its recorded line or elsewhere in that file; no unresolved symbols or missing paths. The workspace contains all nine `step_contexts/STEP-00.md` through `STEP-08.md`; no context file is missing. These checks do not assert that each step output exists, that execution gates are closed, or that AIP acceptance is complete. STEP-04 and STEP-07 production prerequisite gates remain open; no full AIP acceptance is claimed.
