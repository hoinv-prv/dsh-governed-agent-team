# Kế hoạch chỉnh sửa GAT để tích hợp DSH Durable Agent Team

**Status:** Planning recommendation — chưa authorize implementation  
**Date:** 2026-09-26  
**Driving AIP:** `AIP-PLAN-001`  
**Primary input:** DSH proposal `2026-09-26-gat-member-binding-extension.md`

## 1. Executive recommendation

Có thể phát triển GAT hiện tại thành nền tảng durable agent team thực hiện mission mà không tạo orchestrator thứ hai. Kiến trúc hiện tại đã có phần nền quan trọng: durable roster, Session-log projection, mailbox, task DAG, work reports, mission record, approval preflight, recovery/disposal, scoped tools và Web Remote.

Nên triển khai theo ba boundary độc lập:

1. **GAT core** giữ authority cho Team, member lifecycle, mission/task/work và lưu attachment opaque.
2. **DSH host/subagent runtime** cung cấp lifecycle hai pha để materialize child trước, chỉ admit initial inbox sau khi binding hoàn tất.
3. **DSH integration + Durable Agent service** parse declaration một lần, provision durable identity/context, đăng ký binder và scoped contributions qua public ports.

Không nên import Durable Agent trực tiếp vào GAT core, không để hai package cùng parse `team_members.yaml`, và không dùng `agent/created` như điểm bind vì sự kiện này không chứng minh initial request chưa bắt đầu.

## 2. Baseline gate trước implementation

### 2.1 Chốt source authority

Hiện có drift thực tế:

- DSH checkout `/home/hoinv/deepseek-harness/packages/experimental/gat-*` đã có `simpleMode`, loader `team_members.yaml`, route preflight và Agent route.
- Standalone repository này vẫn có initializer built-in-only ở `packages/tools/src/index.ts`.

**Gate B0:** trước khi feature branch bắt đầu, HUMAN chọn một authoring baseline và ghi exact commit/revision:

- **Khuyến nghị:** đồng bộ standalone package source/tests với exact current DSH experimental GAT, rồi phát triển trong standalone và áp dụng vào DSH bằng installer/compatibility workflow.
- Không implement member binding trên cây standalone cũ; nếu không, migration sẽ trộn “sync baseline” với “new feature”, khó review và rollback.

**Exit evidence:** package-tree diff có chủ đích, current DSH GAT tests pass trong standalone, compatibility manifest được cập nhật riêng.

## 3. Target architecture

### 3.1 Ownership

| Concern | Authority |
|---|---|
| Team identity, enabled roster, member phase, child Session, mission/task/work, mailbox | GAT |
| Child materialization, first-inbox admission, prompt assembly, tool execution, Session logging | DSH host/subagent runtime |
| Durable profile, SOUL, memory catalog/items, working artifacts, storage migration | Durable Agent service |
| Declaration normalization, GAT/Durable projections, binder implementation, compatibility diagnostics | DSH integration package |
| Workspace file | Declaration input only; không tự grant membership/storage/tool authority |

### 3.2 Public GAT values

Đề xuất các public semantic types, không expose private classes:

```ts
interface TeamMemberSpec {
  name: string
  description: string
  initialTask: ContentBlock[]
  context: 'fresh' | 'fork'
  continuationProvider: string
  agentOptions?: AgentOptions
  attachments?: TeamMemberAttachmentRequest[]
}

interface TeamMemberAttachmentRequest {
  binderId: string
  protocolVersion: number
  required: boolean
  payload: JsonValue
}

interface TeamMemberAttachmentRecord {
  binderId: string
  protocolVersion: number
  required: boolean
  payload: JsonValue
}
```

`TeamMemberSnapshot` lưu attachment records từ lúc `provisioning`. Generic GAT validation phải giới hạn binder count, bytes mỗi record/tổng mỗi member, JSON depth/nodes/string bytes, unique binder id, positive safe protocol version, và chỉ nhận plain JSON. Payload semantics chỉ binder được diễn giải.

### 3.3 Initializer contract

Thay initializer hiện tại “parse rồi tự spawn” bằng adapter trả normalized plan:

```ts
interface TeamInitialization {
  source: string
  diagnostics: string[]
  members: TeamMemberSpec[]
}

type TeamInitializer = (
  lead: Agent,
  signal: AbortSignal,
) => Promise<TeamInitialization>
```

`TeamService.enable()` phải sở hữu flow:

1. gọi đúng một initializer;
2. validate toàn roster;
3. resolve routes và mọi binder registration/version;
4. chạy tất cả `prepare()` trước first child;
5. provision tuần tự dưới roster transaction semantics;
6. trả member outcomes + bounded diagnostics.

Default GAT-only adapter giữ loader/built-in roster hiện tại. DSH integration adapter parse declaration tích hợp và trả GAT projection + attachment requests. Duplicate initializer tiếp tục fail loud.

### 3.4 Binder port

```ts
interface TeamMemberBinder<P = unknown> {
  readonly id: string
  readonly protocolVersion: number
  prepare(input: BinderPrepareInput, signal: AbortSignal): Promise<{
    attachment: JsonValue
    prepared: P
  }>
  bind(input: BinderBindInput, attachment: JsonValue, prepared: P, signal: AbortSignal): Promise<DisposableBinding>
  recover(input: BinderRecoverInput, attachment: JsonValue, signal: AbortSignal): Promise<DisposableBinding>
}
```

`DisposableBinding` đóng admission riêng của binder, settle admitted work và release contribution/resources. GAT gọi release theo reverse install order. Registry rules:

- một `(binderId, protocolVersion)` chỉ có một registration;
- không replace/remove registration khi có live affected members;
- callback không nhận journal/task/mailbox mutators;
- callbacks chỉ thao tác exact member scope do GAT cung cấp;
- timeout/cancellation dùng GAT lifecycle owner;
- error được sanitize thành safe diagnostic.

### 3.5 DSH two-phase continuable lifecycle

Đây là dependency bắt buộc, không phải optional refactor. Tạo DSH API semantic kiểu:

```ts
const reserved = await ctx.subagents.materializeContinuable(specWithoutPrompt)
// child Agent/Session tồn tại, nhưng chưa có initial user inbox và chưa chạy model
await binder.bind(reserved.agentScope, ...)
const messageId = await reserved.admitInitialPrompt(prompt, signal)
await reserved.commitCatalogOwnership()
```

Exact naming có thể khác, nhưng invariants phải giữ:

- reserved child id được GAT ghi durable trước materialization;
- materialization không tạo model request;
- abort trước admission dispose child, activation và prior bindings;
- admission tạo đúng một durable initial inbox item;
- compatibility wrapper `startContinuable()` giữ behavior cũ cho consumers khác;
- recovery có API materialize/cold-resume mà chưa admit work cho tới khi `recover()` xong.

Không đưa callback tùy ý của GAT vào subagent internals; DSH nên expose một opaque prepared activation/handle với operations bị giới hạn.

### 3.6 Provisioning state machine

Target commit order:

```text
validate roster + prepare all binders
  -> append/flush provisioning(member + immutable attachments)
  -> materialize reserved child, no initial inbox
  -> bind all required attachments in deterministic order
  -> append/flush initial inbox exactly once
  -> append/flush active
  -> publish runtime readiness
```

Failure before inbox admission:

```text
close binder admission
  -> release successful bindings in reverse order
  -> dispose reserved child
  -> append/flush failed with safe diagnostic
  -> keep name reservation and member count
```

`active` phải imply mọi required live bindings đã install. **Khuyến nghị v1: attachment được khai thì required, chưa hỗ trợ optional degradation** để giảm state combinations.

### 3.7 Recovery and disposal

Recovery order:

1. project member snapshot và attachment records;
2. verify every required binder/version exists;
3. verify persisted child descriptor/parent/provider;
4. materialize/cold-resume without admitting pending work;
5. `recover()` all binders;
6. only then admit existing pending inbox/turn;
7. mailbox recovery runs after member binding readiness.

Missing/incompatible binder leaves member `unavailable` in runtime readiness; không rewrite durable attachment và không fallback non-durable execution.

Disposal order:

1. close Team and binder admission;
2. settle Team mutations/dispatches + binder-owned work with bounded timeout;
3. release bindings reverse order;
4. drain Team children;
5. dispose registry/effects.

Persistent Durable Agent data survives Team/Session disposal.

### 3.8 Prompt/tool composition

Refactor monolithic `POLICY` thành contributions có provenance:

1. host/system safety;
2. GAT Team identity/authority/shared-checkout/task/mailbox/wait/completion duties;
3. binder capability summary;
4. Durable Agent behavioral guidance và bounded memory catalog;
5. mission/task-specific context.

Rules: duplicate section key fail loud; binder text không grant tool/filesystem permission; scoped tools vẫn qua executor guard; model-visible wording/schema/order có keyless snapshot; non-Team agents và failed/unbound members không thấy Durable Agent tools/context.

## 4. Mission model delta

Current mission implementation mới có create + approve. Để đạt “durable team thực hiện mission”, cần một workstream riêng sau binder foundation.

### 4.1 Eliminate duplicate task truth

Current mission embeds task snapshots trong khi global Team task board sở hữu executable tasks.

- **Khuyến nghị:** task board remains executable authority; mỗi task mang `missionId`; mission plan lưu task ids/revision metadata, không copy mutable task values.
- Migrate current v2 embedded mission tasks bằng explicit replay adapter sang v3; không silently reinterpret old events.

### 4.2 Mission record and commands

Extend mission với objective, constraints, expected outputs, completion evidence contract, revisioned task-plan reference, admission provenance, readiness diagnostics, reviewer responsibilities và lifecycle `draft -> approved -> active -> closed`.

Close outcome:

```ts
type MissionOutcome =
  | { kind: 'completed'; evidence: EvidenceRef[] }
  | { kind: 'blocked'; reason: string; evidence: EvidenceRef[] }
```

Add Lead-authorized CAS commands để create/admit, revise, approve exact revision, activate khi Team/bindings/capability envelope ready, record review/integration evidence, và close completed/blocked. Learning chỉ tạo candidate, không trở thành mission completion truth.

## 5. Implementation roadmap

### Phase 0 — Baseline alignment and contract freeze
**Repositories:** standalone GAT + DSH checkout.  
**Work:** select authoring source, sync current DSH GAT delta, pin exact commits, document package/port compatibility.  
**Exit:** equivalent existing behavior/tests; chưa có binding behavior.

### Phase 1 — Contract-first binder API
**Packages:** GAT core.  
**Work:** normalized initializer/spec types, attachment bounds, binder registry, prepared-state ownership, conformance tests.  
**Dependency:** Phase 0.  
**Exit:** APIs compile; default adapter produces same roster; no model-visible change.

### Phase 2 — Durable attachment event/schema migration
**Packages:** GAT core, SDK/Remote outputs.  
**Work:** attachments in provisioning snapshots, strict replay, adjacent migration, safe readiness view.  
**Dependency:** Phase 1.  
**Exit:** old fixtures replay unchanged; malformed/oversized records reject before execution.

### Phase 3 — DSH pre-inbox child lifecycle
**Packages:** DSH subagent/agent/session runtime.  
**Work:** materialize-without-admit handle, explicit first-inbox admission, abort/cleanup/cold-recovery semantics, legacy wrapper.  
**Dependency:** parallel with Phase 2 after contracts freeze.  
**Exit:** zero model requests before explicit admission; existing subagent tests green.

### Phase 4 — GAT binding orchestration
**Packages:** GAT core.  
**Work:** prepare-all, bind, rollback, recover, release, timeout and live-registration guards; recovery before mailbox/work resume.  
**Dependencies:** Phases 2 + 3.  
**Exit:** lifecycle unit/persistence/disposal suite passes with fake binders.

### Phase 5 — Initializer and policy/tool adapter split
**Packages:** GAT tools/profile.  
**Work:** loader behind default adapter, normalized specs into core, contribution registry, preserve GAT-only snapshots.  
**Dependency:** Phase 4.  
**Exit:** GAT-only composition keeps existing model-visible behavior except approved restructuring.

### Phase 6 — Durable Agent integration composition
**Packages:** DSH integration + Durable Agent service/provider/consumer.  
**Work:** single declaration loader, version negotiation, projections, binder, task-context prompt section, catalog/memory tools, opt-in profile.  
**Dependency:** stable GAT and Durable Agent ports.  
**Exit:** real Loader enable→prepare→bind→first request→restart→recover→release.

### Phase 7 — Mission lifecycle completion
**Packages:** GAT core/tools/web.  
**Work:** mission/task authority normalization, revision commands, readiness, activation, review evidence, complete/blocked close, candidate-only learning hook.  
**Dependency:** binding readiness stable.  
**Exit:** seven-stage mission scenario không tạo parallel mission/task state.

### Phase 8 — Web/SDK/docs/release
**Packages:** GAT Web, SDK, profiles, installer/compatibility, docs.  
**Work:** safe readiness diagnostics, mission UI/actions, generated outputs, keyless snapshots, installer verification, current-state docs.  
**Dependency:** Phases 6–7.  
**Exit:** opt-in profile only; default DSH profiles unchanged nếu chưa được duyệt riêng.

## 6. Verification matrix

| Acceptance area | Required evidence |
|---|---|
| GAT has no Durable Agent dependency | dependency/import deny test; package graph assertion |
| One initializer only | duplicate Loader composition fails deterministically |
| Prepare all before first child | fake provider/binder asserts zero child Sessions on prepare failure |
| Bind before first request | model adapter request counter remains zero until binder success |
| Durable attachments | event/schema bounds, replay, checkpoint, migration fixtures |
| Failure rollback | reverse release, durable failed edge, child disposal, name reservation |
| Recovery fail-closed | missing/incompatible binder prevents work and emits safe diagnostic |
| Exactly-once binding | generation/restart/HMR tests; duplicate callback rejected |
| Disposal | admission cutoff, admitted-work settlement, reverse release, timeout |
| Scoped prompt/tools | member-only discovery, duplicate section failure, executor permission tests |
| GAT-only compatibility | existing tool/profile/browser tests + keyless snapshots unchanged |
| Mission lifecycle | admit, revise, approve, ready, execute, review, completed and blocked close |
| No parallel task truth | invariant/replay test ties mission to canonical task board |
| Full integration | real Loader, JSONL restart, UI diagnostics, SDK expected outputs |
| Release | installer dry-run/status/verify/rollback on pinned DSH |

Test ladder: focused unit → affected package test/typecheck/build → JSONL restart → real Loader composition → keyless snapshot → browser tests → installer compatibility verification.

## 7. Review gates and rollback

- **G1 Contract review:** ownership, port versions, JSON bounds, callback authority.
- **G2 DSH lifecycle review:** no-request-before-admission và cleanup races.
- **G3 Persistence review:** event migration, replay strictness, unknown-version behavior.
- **G4 Composition review:** default/GAT-only/integration profiles, duplicate initializer.
- **G5 Mission review:** one task authority, completion evidence, blocked semantics.
- **G6 Release review:** pinned DSH compatibility, installer verify/rollback, current-state docs.

Mỗi phase phải deployable hoặc hidden sau experimental profile. Không publish prompt/tool text cho capability chưa mounted. Rollback không xóa attachment payload hay Durable Agent data; unsupported runtime fail closed và giữ evidence.

## 8. Recommended execution packaging

1. **EXEC-A — Baseline sync + contract freeze** (standalone GAT).
2. **EXEC-B — GAT binder/attachment core** (Phases 1–2).
3. **EXEC-C — DSH two-phase continuable lifecycle** (Phase 3, upstream DSH).
4. **EXEC-D — GAT orchestration + adapter/policy split** (Phases 4–5).
5. **EXEC-E — Durable Agent service + integration package** (Phase 6).
6. **EXEC-F — Mission lifecycle completion** (Phase 7).
7. **EXEC-G — Web/SDK/profile/installer/docs release** (Phase 8).

EXEC-B và EXEC-C có thể chạy song song sau contract freeze; EXEC-D chờ cả hai. EXEC-F có thể design song song nhưng chỉ execute khi attachment readiness ổn định.

## 9. HUMAN decisions required before EXEC

1. Chọn authoring baseline/sync direction giữa standalone GAT và DSH experimental packages.
2. Chốt v1 attachment policy: required-only (khuyến nghị) hay optional degraded bindings.
3. Chốt event migration: member event v3 với adjacent adapter (khuyến nghị) hay event phụ.
4. Chốt mission/task normalization: `missionId` trên canonical tasks + mission references (khuyến nghị).
5. Chốt opt-in package/profile names và supported exact port versions.

## 10. Definition of ready

Implementation chỉ bắt đầu khi baseline drift đã đóng; GAT binder port và DSH two-phase lifecycle được review cùng nhau; event migration/limits được chốt; Durable Agent service port có conformance fixture; các EXEC packages có owner/repository/dependency/exit evidence; và default DSH/GAT-only behavior đã được snapshot làm compatibility baseline.
