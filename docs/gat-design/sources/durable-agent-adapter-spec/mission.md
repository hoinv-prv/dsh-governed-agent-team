# Mission: durable-agent-adapter-spec

## Objective and scope

Produce an independently reviewed, implementation-facing specification for the N03 PC evidence adapter, exact future command/path contracts, closed record schema designs, and bidirectional traceability. Workspace: `/home/hoinv/work/dsh-durable-agent`. Mission root: `wbs-runs/durable-agent-adapter-spec`. Planning profile: generic bounded specification mission.

The mission includes problem framing, alternatives, adapter state/authority/evidence contracts, future command/path discovery, schema and negative-case design, integration traceability, and a final HUMAN decision package.

It excludes implementation, test execution, adapter or WBS validator execution, N03 root creation, PC invocation, readiness migration, product/recovery work, publication, network/external effects, automatic retry, and self-acceptance.

## Inputs and assumptions

All operational inputs are beneath the closed `inputs` root and are individually hash-pinned in `wbs.v6.json` (SHA-256 `3b052ba31384d308fcf62ff64c1b565f22a6aa0f3db0de7212e24609e93063b2`):

- PM Agent guideline snapshot;
- Designer Agent guideline snapshot;
- native-v3 plan and bindings;
- evidence-first-v4 plan and final review;
- rejected adapter-v1 code, schemas and RCAs;
- controller/normalization/validator RCA records;
- non-authoritative governance identity roles;
- immutable process-evidence snapshots for F-001 through F-016 traceability.

The architecture source remains separately pinned. Direct reads from the mutable product analysis tree are not granted. Before dispatch, input file-set closure and every source hash must match. Prior failed designs are evidence, not accepted authority.

`governance-identities.json` names stable roles only. Runtime records must authenticate the actual direct HUMAN decision and independently identifiable producer/reviewer principals; the file grants no authority.

## Candidate baseline

Candidate: `wbs.v6.json`  
Exact-byte SHA-256: `3b052ba31384d308fcf62ff64c1b565f22a6aa0f3db0de7212e24609e93063b2`

Integration task: `integrate-spec`. Final-report task: `report-spec`.

Verification is manual and evidence-bound because this is an analytical/design mission with no executable commands. Every task requires independent review; coordinator acceptance applies to intermediate tasks, and HUMAN acceptance applies only to the final reviewed specification package.

Official compile, workspace validation, deterministic order and exact-byte hashing passed for build request v8 after the preserved v7 compile failure. Revisions 1–5 and their review records remain immutable and unapproved. Revision 6 is the exceptional manual successor explicitly authorized by the HUMAN to close terminal findings T-001 through T-003.

## Gates and limits

- Seven tasks; 14 attempts maximum.
- Two attempts are reserved for every task, including final-report production and its independent review.
- Any verification failure, `changes_required`, or `insufficient_evidence` pauses new dispatch. A reserved second attempt can be used only after explicit HUMAN resume and an evidence-based repair hypothesis.
- Maximum parallelism: 2.
- Planned effort ceiling: 1,170 minutes after the batched crosswalk, command-inventory, provenance, overlay and decision-mapping DoD expansion.
- Effects: workspace reads and writes only inside declared mission scopes.
- Commands: none.
- Network/external effects: none.
- Runtime producer/reviewer identities must be authenticated and unequal; neither may record HUMAN acceptance.
- Stop on unresolved authority, source drift, controlling-source conflict, mandatory gate failure, unavailable exact command/path, unclosed schema boundary, or critical/high finding.
- Final domain choice maps deterministically: implement → final_acceptance approve of the specification package only; revise/defer → hold; reject → reject. No choice authorizes implementation or N03 execution under this WBS.

These limits are plan contracts and estimates, not a sandbox or proof that undeclared effects are impossible.

## Status

Plan-only revision 6 awaiting one final bounded whole-candidate review. If that review returns `changes_required`, `insufficient_evidence`, or a native validation failure, terminate the specification planning loop with revision 6 as the strongest artifact; no revision 7 is permitted. Planning has not started WBS execution and created no execution authority.
