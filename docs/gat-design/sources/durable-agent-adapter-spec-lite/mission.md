# Mission: durable-agent-adapter-spec-lite

## Objective and scope

Produce one self-contained, independently reviewed adapter specification package and one HUMAN disposition package. Workspace: `/home/hoinv/work/dsh-durable-agent`. Mission root: `wbs-runs/durable-agent-adapter-spec-lite`. Planning profile: generic minimal specification mission.

The mission has three tasks: author the package, conduct one whole-package integration review, and present the final disposition report. It excludes implementation, validator/test execution, N03/PC work, product/recovery work, network/external effects, automatic retry and self-acceptance.

## Inputs and assumptions

All operational inputs are immutable snapshots beneath `inputs` and individually pinned in `wbs.v1.json`, including PM/Designer guidance, architecture-related project evidence, applicable DSH contracts, the strongest predecessor WBS and terminal ledgers. Predecessor revision history is advisory evidence; the lite mission does not reproduce that revision chain during execution.

Before dispatch, the coordinator must recheck the exact input file set and source hashes. Installed DSH contract drift relative to pinned bytes blocks acceptance.

## Candidate baseline

Candidate: `wbs.v1.json`  
Exact-byte SHA-256: `1433ab79c18e9ee212fd4ccb892e84ae984d4fcf5c97edd86f0955ac92c8d4c4`

Integration task: `integrate-package`. Final task: `report-package`. Native compile, validation, source inspection, dependency ordering and exact-byte hashing passed.

## Gates and limits

- Three sequential tasks; maximum parallelism 1.
- Two attempts per task, six total attempts, 750 effort minutes.
- Every failure or reviewer rejection pauses; repair requires explicit HUMAN resume and one batched hypothesis.
- Every task can read its own outputs for verification.
- Effects are read/write only; commands, network and external effects are absent.
- Every analytical output requires an authenticated independent reviewer.
- Final HUMAN acceptance maps to a coordinator-owned native decision record and grants no implementation or N03 authority.

## Status

Plan-only candidate awaiting one independent whole-candidate review and exact HUMAN approval. No execution authority or runtime artifact exists.
