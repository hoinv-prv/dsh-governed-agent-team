# GAT mission design deltas — cross-repository reference

**Collected:** 2026-10-04  
**Status:** Draft evidence-based reference for review; no execution or canonical-promotion grant.


For implemented behavior, use the source-aligned [formal detail design](DETAIL_DESIGN.md) and [code map](SOURCE_CODE_MAP.md). Source code is the source of truth; this page records collected design/mission evidence.

## Purpose and authority

Tập hợp design impact từ hai mission GAT tại `wbs-runs` và mười mission tại `/home/hoinv/work/dsh-durable-agent/wbs-runs`. Chọn các baseline/report/memo liên quan Agent Team; không coi mọi revision hoặc attempt artifact là một design được chấp nhận. [Manifest](collection-manifest.json) chứa bytes/hash/source locator và ledger state tại thời điểm collect.

Snapshot của report giữ wording trước acceptance. Trạng thái dưới đây lấy từ execution/decisions khi có ledger; các mission chỉ có planning document được ghi planning-only. Các kết quả test là evidence đã ghi ở nguồn, không phải kiểm thử lại hôm nay.

## Local GAT missions

| Mission | Recorded state | Design/behavior delta | Evidence |
|---|---|---|---|
| `legacy-agent-team-hotfix` | r9 `completed`; HUMAN final `decision-final-002 = accept` | Lead-only execution defaults minimum durable teammates to 0 while exact current approved Team plan remains required. One Web Approve action imports latest matching approved chat plan, deduplicates task subjects, preserves active tasks, and atomically imports/approves the resulting revision. | [Final report](sources/gat-missions/legacy-agent-team-hotfix/final-report.md), [decisions](sources/gat-missions/legacy-agent-team-hotfix/decisions.json) |
| `multi-mission-web-ui` | r32 `active`; no final acceptance recorded | Later mission objective is an inactive dependency-free Conservative MVP standalone package, despite the older Web-UI name. Governance, partitioned memory, policy and wrapper pieces have recorded accepted work; full accepted-vector dispatch and DSH/Web activation remain unclaimed. | [Mission](sources/gat-missions/multi-mission-web-ui/mission.md), [standalone integration](sources/gat-missions/multi-mission-web-ui/integration-standalone.md), [runner gap](sources/gat-missions/multi-mission-web-ui/runner-architecture-gap.md) |

### Lead-only and approved plan import

The hotfix report records installed compatibility verification, 164 focused passing tests across nine files, full host/client build, built-library smoke and three assembled dashboard tests. No live GUI/profile activation or server restart was performed. Failed attempts remain evidence.

Import uses the latest `exit_plan_mode` call and its matching later successful canonical result, never older approval fallback. It accepts bounded checklist/bullet/numbered items only in explicit `## Tasks`; malformed content rejects. NFKC/whitespace/case normalization deduplicates subjects. Exact plan revision, task cap, authorization and post-import preflight occur before one serialized flush.

### Conservative MVP control/conformance boundaries

Standalone integration recorded 32 passing source tests, deterministic ESM builds and a built-package smoke, but exercised synthetic fixtures only. The accepted full vector baseline remained unexecuted. DSH runtime/MCP integration and Web activation are explicitly excluded in that report.

The [runner gap](sources/gat-missions/multi-mission-web-ui/runner-architecture-gap.md) separates real implementation transitions from runner simulation: preserve accepted governance bytes, define package-owned control-state operations, keep fixtures setup-only, give handlers closed id/operation inputs, reduce append-only observations, require exact handler/probe/evidence coverage, and bind complete source closure.

[Control-plane v39](sources/gat-control-plane/control-plane-stabilization-design.v39.md) is advisory/inactive procedural design for content-addressed pre-charge admission. It requires fresh review before WBS build and does not activate product behavior. Keep this design distinct from the root-Session Team journal and from the Durable Agent member-memory provider.

## Durable Agent mission coverage

| Mission | Recorded state | Design contribution and GAT boundary | Starting source |
|---|---|---|---|
| `gat-durable-agent-integration` | r2 `complete`; final acceptance `decision-human-accept-mission-017` | Versioned service, explicit scope, opaque refs, selective context/memory, authorized immutable-generation commits, release drain and Consumer composition. GAT binder/lifecycle adoption excluded. | [Integration design](DURABLE_AGENT_INTEGRATION.md) |
| `durable-agent-p0-task-contract-plan-poc` | r6 `complete`; `decision-final-r6-005 = accept` | Bounded deterministic TaskContract → PlanProposal validation/normalization without authority widening. Accepted PoC evidence, no live host/model or product adoption. | [Final report](sources/durable-agent-p0-task-contract-plan-poc/final-report.md), [design notes](sources/durable-agent-p0-task-contract-plan-poc/prototype/design-notes.md) |
| `durable-agent-p1-file-cwd-containment-poc` | r1 `complete`; `decision-final-r1-002 = approve` | Component-aware strict no-symlink file/cwd containment in cooperative Linux/POSIX. No hostile TOCTOU, hard-link/mount, remote filesystem or production sandbox claim. | [Final report](sources/durable-agent-p1-file-cwd-containment-poc/final-report.md), [algorithm](sources/durable-agent-p1-file-cwd-containment-poc/prototype/algorithm.md) |
| `durable-agent-p2-checkpoint-terminal-model-poc` | r36 `complete`; `decision-final-p2-r36-009 = approve` | Accepted bounded checkpoint/terminal/handoff PoC package, exact immutable receipts and unknown-outcome semantics. No downstream execution/product grant. | [Final handoff](sources/durable-agent-p2-checkpoint-terminal-model-poc/HANDOFF-FINAL.md), [report](sources/durable-agent-p2-checkpoint-terminal-model-poc/final-report-r31.md) |
| `durable-agent-bs1-basic-design` | r60 `waiting_for_human`; no final acceptance | Design line separates DTO/plan, effects, state/handoff, component dataflow, flow closure and sizing/test gates. Collected a03-r53 projection is a prior design package, not a final r60 acceptance. | [Projection baseline](sources/durable-agent-bs1-basic-design/integration-stages/projection-package/attempts/bs1_integration_projection_package-a03-r53/design-baseline.md), [rationale](sources/durable-agent-bs1-basic-design/integration-stages/projection-package/attempts/bs1_integration_projection_package-a03-r53/design-rationale.md) |
| `durable-agent-plugin-mvp` | r20 `paused`; no final acceptance | Earlier broad mission-controller design with database, wake/delegation and host/API/dashboard contracts. Historical architecture research, not current GAT implementation or the later narrowed member MVP. | [Design v3](sources/durable-agent-plugin-mvp/design-baseline-v3.md), [execution protocol](sources/durable-agent-plugin-mvp/execution-protocol-v1.md) |
| `durable-agent-wbs-runner-mvp-sprint1` | r5 `cancelled` | Earlier single-coordinator sequential RuntimePlanV1/checkpoint slice; cancelled for linked Agile reset. Retain baseline for lineage, not resumed execution authority. | [Mission](sources/durable-agent-wbs-runner-mvp-sprint1/mission.md), [store baseline v5](sources/durable-agent-wbs-runner-mvp-sprint1/store-contract-baseline.v5.md) |
| `durable-agent-wbs-runner-mvp-agile` | Planning package; no execution ledger | Current collected planning navigator selects goal/scope v2, member compatibility v3 and sprint plan v10. Separates one contracted-task member execution from PM/WBS orchestration. | [Navigator](sources/durable-agent-wbs-runner-mvp-agile/README.vi.md), [goal baseline](sources/durable-agent-wbs-runner-mvp-agile/goal-scope-baseline-v2.md), [compatibility memo](sources/durable-agent-wbs-runner-mvp-agile/memo-durable-agent-team-member-compatibility-v3.md) |
| `durable-agent-adapter-spec` | Planning-only r6 candidate narrative; no execution ledger | N03 PC evidence adapter specification, schemas and traceability. Implementation, validator/PC execution and product/recovery effects excluded. | [Mission](sources/durable-agent-adapter-spec/mission.md) |
| `durable-agent-adapter-spec-lite` | Planning-only r1 candidate narrative; no execution ledger | Smaller self-contained adapter specification/disposition planning successor. No implementation or N03 authority. | [Mission](sources/durable-agent-adapter-spec-lite/mission.md) |

## Member task execution design — synthesis for GAT

The Agile compatibility memo narrows a Durable Agent to one Team member receiving one normalized contracted task. PM/Agent Team owns WBS orchestration, cross-task readiness, delegation and acceptance.

- Standalone/WBS origin is opaque provenance; it cannot widen paths, commands, retry limits or budget.
- One task is active across assigned/planning/executing/handoff-pending; a second assignment receives typed BUSY rejection. No internal queue/delegation in the member MVP.
- A bounded host seam supplies PlanProposal. The plugin validates/persists it and does not itself invoke a model. Replanning cannot reset contract identity or budget; material deviation blocks.
- Pure verify assertions are observational. Command-based verify uses the same guarded effect execution/checkpoint/attempt path as other commands.
- Every terminal outcome (`completed_provisional`, `blocked`, `failed`, `unknown_outcome`) converges on handoff-pending. Only successful atomic TaskHandoff persistence returns the member to idle.
- Settlement is artifact-based, without requiring PM acknowledgement. Task acceptance remains with PM/reviewer/HUMAN.
- Completed effects do not replay after restart. Interrupted unsettled effects become UNKNOWN_OUTCOME without automatic retry. Failed handoff persistence retains busy state and retries only exact canonical bytes within budget.
- Immutable task/contract/task-run identity binds execution and handoff; same-key/same-bytes recommit is idempotent, conflicting bytes reject.

These are planning/PoC/unfinished BS1 design inputs. Do not advertise the entire member runner as shipped by the separate completed profile/memory service mission.

## Conflicts and unresolved adoption

1. BS1 navigation snapshot says selected v58 and awaiting v59 approval; current ledger is r60 with approved r60 revision/execution records. Use ledger/source hashes for follow-up and review current task packets before taking work.
2. Sprint-1 narrative mentions a candidate v6 and a pause, while selected execution r5 is cancelled. The candidate does not reactivate the mission.
3. Final reports may request acceptance already recorded later in decisions. Never edit accepted report snapshots to make them look current.
4. MCP partitioned reference memory, Durable Agent member memory, runner checkpoint and GAT Team journal are separate authority/storage domains.
5. Live GAT binder adoption, complete BS1 design acceptance, accepted-baseline conformance and deployment are not established by this collection.

## Provenance and review

Use [manifest](collection-manifest.json) for exact source bytes, then the linked mission ledger for acceptance scope. Source snapshots are selected reference extracts, not a complete backup of historical revisions, dependency trees or attempt evidence. Their relative internal links are resolved from the original source locator.

Register the authored hub, integration design and this delta reference with the existing GAT design profile as draft/reference sources. Do not automatically promote PoC lessons, create object authority, or register copied ledgers as canonical designs.
