# Findings — GAT Rereview v3 Triage

## Gate U1 Evidence
- HUMAN supplied `/home/hoinv/work/advisor_workspace/council-runs/task-1-rereview-v3/review-advisory.md` and explicitly required critique-first selective application.
- Review authority is advisory. Proposal implementation/activation remains out of scope.

## Disposition Standard
- **ACCEPT:** correct and materially improves correctness/security/compatibility/testability.
- **ACCEPT-WITH-MODIFICATION:** underlying concern is valid, but the requested remedy or factual framing is excessive/imprecise.
- **REJECT:** incorrect, already satisfied, conflicts with authority, or would worsen the design.
- **DEFER:** valid but non-MVP and not required for proposal coherence.

## Comment Disposition Ledger

| ID | Disposition | Critique and evidence | Proposal action |
|---|---|---|---|
| Protocol verdict | ACCEPT, no proposal edit | `insufficient_evidence` is a council-protocol fact because mandatory lane envelopes were inadmissible. It does not prove or disprove architecture claims and cannot be treated as a vote. | Record in delivery report only. |
| “Do not approve yet” | ACCEPT, no new clause | Advisory recommendation is justified by R2/R3/R4 and proposal is already inactive. Council cannot decide approval. | Keep inactive; no redundant wording. |
| R1 native mission/plan gate | ACCEPT-WITH-MODIFICATION | Exact Team-plan approval gate is proven in DSH: `TeamView.planRevision/planPhase/planApproval` and `gat-tools.approvalFailure/readiness` fail closed for missing/stale plan approval. `TeamMissionApprovalSnapshot` exists, but current `gat-tools` evidence does **not** show native mission approval gating spawn/execution. The rereview overstates that part. | Map current native Team-plan approval as authoritative and bind exact revision/phase/approval to run/PDP/audit. If GAT elects to bind a native TeamMission, its exact approved revision is authoritative for that mapping, but do not claim current execution enforcement. |
| R2 workspace replacement | ACCEPT | Proposal §3.3/GAT-EXEC-002 permits replacing Task Workspace for same task, contradicting canonical one executor-agnostic `{account}/{task_id}` workspace and write-once pointer. | Keep Task Workspace fixed for task lifetime. A new workspace requires a new canonical `task_id`; GAT cannot alias it as a generation replacement. |
| R3 physical selector feasibility | ACCEPT-WITH-MODIFICATION | DSH ships a default-off generic MCP bridge and examples; the upstream reference server owns one JSONL graph and has no tenant selector. Rereview correctly identifies missing topology, but does not prove impossibility because an adapter-owned partitioned MCP server is viable. | Pin MVP to an adapter-owned GAT partitioned memory MCP server with native partition selection. Treat upstream MCP Reference Memory as non-MVP interoperability reference, not the backing store. Capability remains unavailable until PoC passes. |
| R4 audit/mutation atomicity | ACCEPT-WITH-MODIFICATION | Existing proposal guarantees zero mutation without a cross-store protocol. Literal zero physical write is unnecessary; the security invariant is zero **committed/visible domain mutation** without durable audit disposition. | Pin single transactional adapter-owned store for record revision, idempotency, audit intent/local chain, and commit marker; use fenced prepare/audit-anchor/publish recovery; add crash vectors at every boundary. |
| R5 Working AIP readiness | ACCEPT-WITH-MODIFICATION | Canonical spec defines `not_ready`, `lite_ready`, `execution_ready`; existence/status alone is insufficient. GAT must not duplicate/freeze package readiness semantics. | Bind package-owned readiness decision/evidence and applicability; fail when package says non-executable. Add absent/not-ready/inapplicable-Lite/high-risk vectors. |
| R6 execution identity/cache | ACCEPT | PDP/output/selector/audit omit Working AIP, Task Workspace, execution identity; cache binding is incomplete. | Remove decision/result caching from Conservative MVP and bind full execution/native-plan identity into PDP, selector, audit, and record history. Cache is future work. |
| R7 mission-shared membership | ACCEPT-WITH-MODIFICATION | No authoritative MissionMembership/revision exists; Team membership cannot be silently treated as Mission membership. Adding a new membership subsystem would inflate MVP. | Remove `mission-shared` from MVP and defer it with its membership/authorization requirements. |
| R8a lifecycle actions | ACCEPT | Legal-hold apply/release and purge are privileged but missing from PDP action/reason/vector contracts. | Add explicit lifecycle actions, HUMAN-bound authority, reason codes, and negative vectors. |
| R8b audit reconstruction | ACCEPT-WITH-MODIFICATION | Audit must bind Working AIP/Workspace/execution/native approval/selector. Full duplicated decision snapshot is unnecessary if immutable policy artifacts are content-addressed and rule IDs/hashes retained. | Add execution and native approval fields, selector/capability hash, matched rule IDs, and immutable policy/membership hashes. |
| R8c activation checklist | ACCEPT-WITH-MODIFICATION | Existing clauses individually block activation, so this is not a missing security control; it is an operational closure/traceability weakness. | Replace §0.2 with one content-addressed activation manifest that enumerates all blockers and decisions. |
| Prior-finding table | ACCEPT WITH QUALIFICATIONS | Fair summary except R1 native mission enforcement is overstated and F11 operational closure belongs to activation manifest. | No direct copy; reflect corrected contracts. |
| Rereview lint failure | REJECT as proposal evidence | `BlockingIOError` on output transport is inconclusive, neither PASS nor proposal failure. | Report separately; use current task lint evidence. |
| Missing live PoC/threat model | ACCEPT as activation evidence gap | Proposal correctly treats these as future activation gates, not completed facts. | Activation manifest must carry their hashes. |

## Accepted Change Plan
1. Add native Team-plan approval mapping and conditional native TeamMission mapping without claiming enforcement.
2. Remove same-task Task Workspace replacement/generation semantics.
3. Replace the ambiguous upstream Reference Memory backend with an adapter-owned partitioned GAT MCP topology.
4. Define atomic record/audit commit and crash recovery.
5. Bind package-owned AIP readiness evidence.
6. Remove caching from MVP; bind full execution context everywhere.
7. Remove `mission-shared` from MVP.
8. Add lifecycle PDP actions, reconstructable audit evidence, and one activation manifest.

## Rejected / Deferred Scope
- No generic MissionMembership subsystem in MVP.
- No distributed 2PC framework; use one transactional adapter-owned store plus fenced anchor/publish recovery.
- No claim that current DSH enforces native TeamMission approval during spawn/execution.
- No use of the council formal verdict as architecture authority.
- Cache, mission-shared memory, and upstream reference-server compatibility are future work.

## Change Trace
- R1 → AgentRun/TeamRuntimeBinding/PDP/audit/DSH mapping/runtime flow/GAT-PLAN and conditional MISSION vectors.
- R2 → execution identity/cardinality and GAT-EXEC vectors; Workspace fixed for Task lifetime.
- R3 → §10.1 and §14 pin `gat-partitioned-memory-mcp`; upstream reference server rejected as MVP backend.
- R4 → §12.3 transactional protocol and GAT-TXN crash vectors.
- R5 → AgentRun/PDP/§14 readiness-oracle mapping and GAT-AIP readiness vectors.
- R6 → PDP/selector/audit/history binding; decision/result cache removed from MVP.
- R7 → MVP scopes and physical selector remove `mission-shared`; future-work requirement retained.
- R8 → lifecycle actions/reason codes/authority/vectors, expanded audit evidence, Activation Manifest.
- Proposal header/history → revision 3, `AIP-EXEC-007`, selective rereview provenance.

## Verification Evidence
- Initial revision-3 hash `1ad4f58d...` received independent `REVISE` solely for a valid raw-MCP-tool bypass gap.
- Applied minimal correction: raw `mcp__gat-partitioned-memory-mcp__*` tools are hidden and denied at package admission, connection is package-private, negative vector `GAT-MCP-RAW-001` proves zero backend access, and §0.1 avoids implying prior HUMAN topology approval.
- Current stable proposal SHA-256: `dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee`.
- `git diff --check`: exit `0`, no output.
- Task-scoped AIWS lint after correction: `errors=0 warnings=0 info=0`.
- Conflict sweep: same-task Workspace replacement appears only in negative vector; `mission-shared` appears only as explicitly deferred; decision/result cache appears only as explicitly disabled/deferred; upstream MCP Reference Memory appears only as rejected/future interoperability reference.
- Final exact-hash independent read-only delta/regression review returned **PASS** for `dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee`.
- Reviewer confirmed R1–R8 PASS, F1–F11 remain closed, raw-MCP bypass is closed, and no rejected/low-value item was silently applied.
- Verdict is advisory only and does not approve or activate Revision 3.

## Final Capture Sweep
- Reviewed proposal diff, critique ledger, review feedback, verification artifacts, and final output scope.
- Added `CAP-007-02` for the reusable raw-MCP-tool admission/bypass pattern.
- Total inbox rows: `2`; still `captured`: `0`; deferred to HUMAN-visible backlog: `2`; relation candidates pending: `0`.
- `CAP-007-01` → `BL-007-CAP-007-01` (proposal wiki routing gap).
- `CAP-007-02` → `BL-007-CAP-007-02` (raw MCP bypass security lesson).
- No direct Wiki/Truth promotion performed.

## Target-spec Attribution Check
- Target proposal contains one `AIP-EXEC-007` attribution in its Working AIP header.
- AIP objective, expected outputs, STEP-02 edit scope, and STEP-03 exact-hash verification already reflect the attributed revision; no Re-plan Log amendment is required.

## Notes
- Working AIP readiness source resolved as `SRC-METHOD-methodology-20-specs-working-aip-connection-spec-mvp-md-e993`.
- DSH MCP guide confirms DSH only bridges default-off third-party servers; MCP Reference Memory stores one JSONL graph and performs case-insensitive substring matching.
- `CAP-007-01` records the proposal wiki-routing gap.
