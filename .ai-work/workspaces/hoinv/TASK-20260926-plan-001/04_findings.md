# Findings — GAT design/implementation planning for DSH durable agent teams

## Scope and authority
- HUMAN confirmed the recommended planning scope on 2026-09-26.
- Runtime/code authority order used here: current DSH checkout source and tests > standalone GAT source/tests > maintained project reference > proposed DSH Agent Notes > inference.
- No product code was modified. The working tree already contained substantial unrelated changes before this PLAN.

## Current baseline

### Current DSH GAT is ahead of the standalone source
- The DSH checkout already has `simpleMode`, bounded `team_members.yaml` loading, per-member route preflight, optional Agent route, and source=`workspace|built-in-default|existing`: `/home/hoinv/deepseek-harness/packages/experimental/gat-tools/src/index.ts:20-47,83-116,657-766`, `.../gat-tools/src/team-config.ts:1-149`, `.../gat-core/src/types.ts:272-292`.
- The standalone workspace currently contains an older built-in-only initializer and a narrower public type: `packages/tools/src/index.ts:620-698`, `packages/core/src/types.ts:282-304`.
- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md:20-29` already warns about this synchronization gap. Implementation must establish one authoring baseline before feature work.

### Existing capabilities that should be preserved
- One initializer registration already exists and duplicate registration fails: DSH `gat-core/src/index.ts:303-325`.
- GAT already owns Team identity, durable roster phases, mailbox, task DAG, work state, missions, approval preflights, wait/interrupt, recovery, and disposal: DSH `gat-core/src/index.ts:149-550`.
- Member creation already reserves a child id, flushes `provisioning`, starts a continuable child, verifies initial prompt durability, then commits `active`; failure is durable and cleanup is bounded: DSH `gat-core/src/roster.ts:245-337`.
- Projection/event parsing is strict and currently version 2; member identity fields are immutable: standalone `packages/core/src/projection.ts:77-85,125-141,322-376` and `packages/core/src/types.ts:51-63,366-387`.
- Recovery and mailbox de-duplication already have restart coverage: `packages/core/tests/persistence.spec.ts:166-514`.
- Policy and Team tools are member-scoped and executor-enforced: DSH `gat-tools/src/index.ts:363-655`.

## Material gaps versus the proposal

| Proposal area | Current state | Gap / implication |
|---|---|---|
| Normalized Team initialization | Singleton initializer exists, but it owns parsing, route preflight, and provisioning | Change initializer contract so adapters return normalized specs; core performs prepare/provision/commit |
| Binder registry/protocol | Absent | Add versioned registry, protocol negotiation, duplicate/live replacement rules, and callback contracts |
| Durable attachments | `TeamMemberSnapshot` has no attachments | Add bounded, versioned opaque records and strict replay/migration |
| Pre-first-request bind point | `startContinuable()` both materializes child and queues prompt before returning | Requires a DSH subagent lifecycle API split before GAT can guarantee binding |
| Recovery | Roster reconciliation only checks child descriptor + accepted prompt | Recover required binders before cold resume; fail closed on missing/incompatible binder |
| Release | Team drains children and scoped tools dispose | Add reverse-order binder release and admitted-work settlement before child drain |
| Prompt/tool contributions | One monolithic `team:policy`; install via lifecycle listeners | Add named/provenanced scoped contributions with duplicate-key rejection and pre-admission ordering |
| Attachment readiness view | Only member diagnostics array | Add safe per-binder readiness without exposing payloads |
| Mission lifecycle | Mission create/approve only; embedded initial task snapshots | Add revise/readiness/activate/review/close/blocker evidence; remove or control duplicate task authority |
| Mission tests | Create/approve/replay only | Add seven-stage lifecycle, blocker, review, completion-evidence, candidate-only learning tests |

## Highest-risk seam
- `SubagentContinuationManager.startContinuable()` prepares/materializes the child and calls `submitMaterialized()` to queue the initial prompt before returning: `/home/hoinv/deepseek-harness/packages/subagent/subagent/src/continuation.ts:95-190`.
- Therefore a GAT-only callback added after `startContinuable()` is too late. The required change is a DSH-owned two-phase continuable lifecycle: materialize/reserve without model admission, then explicitly admit the first inbox item after GAT bind succeeds.
- This DSH host change must preserve ownership holds, provider preparation, persistence duplicate checks, activation cleanup, cancellation, descriptor/catalog publication, and existing public behavior through a compatibility wrapper.

## Mission authority conflict to resolve
- Current `TeamMissionSnapshot.plan.tasks` embeds task snapshots (`packages/core/src/types.ts:107-129`), while the global task board separately owns mutable executable tasks. The proposal says the mission owns objective/completion and tasks own executable work/dependencies.
- Recommended direction: a mission references Team task identities (or tasks carry `missionId`) rather than owning an independently mutable copy. Existing v2 mission events need an explicit adapter/migration path; do not silently reinterpret embedded snapshots.

## Design conclusion
- The proposal is directionally compatible with current GAT ownership, persistence, scoped tooling, and recovery architecture.
- Implementation should extend the current architecture rather than add a second orchestrator or persistence store.
- Required cross-repository work is unavoidable at the pre-inbox child lifecycle seam; GAT member binding cannot be made correct by only changing this standalone repository.
- DSH integration and Durable Agent service work should be separate execution packages linked by versioned conformance contracts.

## Open decision disposition
- OP-02 is resolved: DSH upstream lifecycle and integration-package changes must be separate execution workstreams from GAT core/tool changes, with an integration gate that tests the exact supported combination.

## Capture closing note
- Three retrieval-gap candidates were captured for the member-binding proposal, integration-boundary note, and maintained GAT reference. No knowledge was promoted automatically.
