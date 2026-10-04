# Mission: durable-agent-wbs-runner-mvp-sprint1

## Objective

Implement the smallest useful durable-agent vertical slice: after explicit approval of one product `RuntimePlanV1`, a single local coordinator runs a small dependency graph sequentially, persists committed state, resumes without replaying completed effects, and emits deterministic final reports.

## Planning profile

Agile delta / Sprint-1 implementation slice. Earlier adapter/N03 missions remain frozen research evidence and are not prerequisites.

## Workspace and accepted design baseline

- Workspace: `/home/hoinv/work/dsh-durable-agent`
- Package: `durable-agent-plugin`
- Mission root: `wbs-runs/durable-agent-wbs-runner-mvp-sprint1`
- Candidate WBS: `wbs.v6.json`
- Candidate SHA-256: `f14e13ac26a32139f36eac8562e4d11e1338e9ac32841cd4bd98d81c602622e0`
- Accepted checkpoint Contract Baseline: `store-contract-baseline.v5.md`
- Baseline SHA-256: `7ba671865eaa830386fffb6d79b8443e37e1358951a6da882ced4a13d5b1b94f`

`dsh-wbs/1` is the implementation mission contract. The product consumes the distinct closed `RuntimePlanV1` and `RuntimeApprovalV1` formats defined by baseline v5.

## Revision-4 tasks

1. Implement the RuntimePlanV1/RuntimeApprovalV1 contract and sequential execution compatibility.
2. Implement the schema-v2 private checkpoint exactly against accepted baseline v5.
3. Freeze an independently reviewed JSON/Markdown rendering contract.
4. Integrate renderer, API/exports and a three-to-five-task restart E2E; run the full bounded suite.
5. Produce independently reviewed outcome reports for HUMAN acceptance and Sprint-2 choice.

## Scope and limits

- One process, coordinator, store owner and worker lane; `max_parallel = 1`.
- Up to 20 acyclic local runtime tasks, with at most two attempts each.
- Local bounded file actions and full exact allowlisted command records; no shell inference.
- No network, external effects, databases, distributed/multi-owner guarantees, arbitrary history store, parallel execution, fleet UI, N03/PC or adapter work.
- Atomic local replacement only; no power-loss durability claim.

## Validation and status

Native validation/workspace inspection, dependency ordering and exact-byte hashing passed. Five current tasks allocate ten attempts and 1,920 effort minutes; mission-wide ceilings are 16 attempts and 2,520 effort minutes so the six immutable pre-revision-5 charges and 600 historical effort minutes remain counted. Runtime-contract attempts 1–2 under revision 5 are preserved failed; no dependent task has run. Execution remains paused until exact HUMAN approval binds revision 6 and its SHA-256.
