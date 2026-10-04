# Kế hoạch Sprint Agile cho Durable Agent MVP v10

## 1. Câu chuyện đúng của sản phẩm

```text
Agent Team giao một contracted task
→ Durable Agent validate contract
→ nhận host-supplied plan artifact qua bounded seam
→ chạy internal steps tuần tự, không delegation
→ persist/recover không replay
→ mọi terminal outcome đều đi qua handoff_pending
→ atomic-persist provisional TaskHandoff
→ chỉ sau khi handoff settle mới nhận task tiếp theo
→ Agent Team reviewer quyết định acceptance
```

Durable Agent không chạy toàn bộ WBS. WBS scheduling, cross-task dependency và task acceptance thuộc Agent Team/coordinator. Task source có thể `standalone` hoặc `wbs`, nhưng core chỉ nhận normalized source-agnostic TaskContract và opaque origin metadata.

## 2. Standard feature-sprint package

Mỗi FS1–FS6 hoàn thành đúng một DF trong một sprint:

1. detailed-design candidate;
2. independent design review với batched findings;
3. finalize design + independent oracle, tối đa hai correction attempts;
4. implementation candidate, không sửa oracle;
5. independent verification/review, ordinary correction trong approved attempt envelope.

Downstream chỉ consume final accepted contract, manifest và evidence.

## 3. PoC sprints

### P0 — Task contract → internal step plan

**Unknown:** contract fields, retry/attempt normalization và host/plugin artifact seam nào đủ để Agent tự phân rã task mà không tự thay scope/authority; internal replan được phép tới đâu.

**Hypothesis:** deterministic host adapter có thể cung cấp concise `PlanProposal` để plugin validate/persist thành private ordered plan trong finite `max_steps`; host được sửa chưa-chạy steps trong contract nhưng material deviation luôn block; plugin không cần live LLM integration.

**Seam được exercise:**

```text
validateAndNormalize(TaskContract, PlanProposal)
→ AcceptedPlan | TypedBlock
```

P0 dùng explicit deterministic adapter/test double, không dùng real host hoặc model provider. `PlanProposal` bind producer metadata, contract/execution identity, parent revision/hash khi replan, concise reason và ordered step proposals. Missing, malformed, stale hoặc identity-mismatched proposal phải fail trước effect. BS1 mới freeze production DTO sau accepted P0 evidence.

**Oracle corpus:**

| Claim | Positive observation | Known-bad/mutation phải reject |
|---|---|---|
| Origin equivalence | cùng contract payload với `standalone`/`wbs` cho cùng normalized core plan; chỉ provenance khác | origin metadata mở rộng path/command/budget hoặc yêu cầu load WBS graph |
| Material completeness | valid contract tạo bounded normalized plan | thiếu identity, output, non-goal, allowed effect, verification, `max_steps` hoặc retry/attempt field material |
| Determinism/identity | cùng input bytes + proposal bytes tạo cùng stable IDs/order/plan hash | duplicate/unstable ID, changed completed ID, wrong contract/run identity, stale parent revision |
| Bounded policy | positive bounded integers; deterministic precedence; total-attempt hard cap; replan giữ counters/ceilings | missing/unbounded/overflow/contradictory limit hoặc replan reset budget |
| Contract-preserving replan | chỉ unexecuted steps đổi; goal/input/output/effect/verification giữ nguyên | attempted goal/output/path/command/effect/verification expansion |
| Supported plan | chỉ `reason/file/command/verify/handoff`, within `max_steps`, required terminal handoff | malformed/unsupported step, excess steps, handoff/ordering invariant sai |
| No plugin LLM | dependency/import/spy trace có zero outbound model invocation | plugin cần model port/call để normalize/validate |

Fixture corpus, expected canonical JSON/hash, mutation results và decision record là authoritative P0 evidence; prose assertion hoặc implementation-owned tests một mình không đủ.

**Retry/attempt questions P0 phải freeze:** canonical integer domain/engine ceiling; `step > type > default` precedence; attempt debit point; total hard cap; `UNKNOWN_OUTCOME` accounting/no-auto-retry; replan invariants; finite handoff-commit retry; contradiction/overflow behavior. P2 phải consume manifest này, không tái quyết định semantics.

**Decision:**

- `accept`: toàn bộ mandatory positive và known-bad fixtures pass, evidence đóng, independent reviewer không còn blocker;
- `defer`: hypothesis chưa bị falsify nhưng còn mandatory observation/normalization question chưa có evidence; không mở downstream readiness;
- `reject`: cần plugin-owned LLM, WBS graph/authority expansion, unbounded policy hoặc không thể tạo deterministic bounded plan.

PM/coordinator đóng gói evidence, independent reviewer đưa recommendation; HUMAN là P0 acceptance owner và chọn `accept | defer | reject`.

**Output:** task-contract/plan mapping; seam record; retry/attempt normalization manifest; replan/blocker rules; fixture/oracle evidence; P0 decision record.

**Dependency contribution:** accepted P0 là một trong ba conjunctive prerequisites của BS1 và là direct prerequisite của FS1. Nó không trực tiếp unlock FS2.

### P1 — File/cwd containment

**Unknown:** safe classification cho `read/write/append` trên existing/absent target, symlink ancestor, existing/dangling final symlink và outside target; command cwd dùng cùng containment boundary.

**Output:** executable topology matrix, zero-outside-effect evidence, pinned threat boundary, chosen algorithm và proposed effect ceilings/units.

**Dependency contribution:** accepted P1 là một trong ba conjunctive prerequisites của BS1 và direct prerequisite của FS3/FS4 theo accepted interfaces.

### P2 — Internal-step checkpoint và terminal model

**Unknown:** private state nhỏ nhất để persist task/contract/execution identity, plan revision, completed steps, current effect, attempts, terminal status và immutable handoff key.

**Required vectors:** plan persist; persist/debit-before-effect; success/failure; safe replan; normalized finite retry; restart-current→`UNKNOWN_OUTCOME`; completed non-replay; `blocked | failed | unknown_outcome` bypass remaining normal steps; four TaskHandoff statuses; task-terminal-before-handoff-commit; handoff commit failure/retry/exhaustion; restart before/after commit; byte-identical idempotent recommit; same-key/different-bytes collision; illegal transition rejection.

**Output:** state/terminal transition model, attempt accounting bound to P0 manifest, logical artifact key, state vectors, illegal-state/collision evidence và decision.

**Dependency contribution:** accepted P2 là một trong ba conjunctive prerequisites của BS1 và direct prerequisite của FS5.

Nếu PoC trả `defer/reject`, function phụ thuộc không được lập feature WBS.

## 4. BS1 — Basic design

**Goal:** freeze interfaces DF1–DF6 và chứng minh mỗi function có thể hoàn thành trong một feature sprint.

**Hard readiness:** accepted P0 **và** P1 **và** P2, `goal-scope-baseline-v2.md`, `memo-agent-team-pm-goals-v1.md` và `memo-durable-agent-team-member-compatibility-v3.md`.

**Output:** production TaskContract/PlanProposal DTO boundary, internal plan/step DTOs, result interfaces, component ownership, data flow, terminal/recovery flow, exact artifact key/path layout, create-once/idempotency rules và test layers.

**Không làm:** detailed function contract, production code hoặc WBS coordination.

**Stop:** nếu design cần cross-task scheduler, subagent delegation, generic history store hoặc một DF phải trải nhiều feature sprints, giảm/split scope trước implementation.

## 5. Feature sprints

### FS1 — DF1: nhận task contract và tạo internal step plan

**Primary goal:** PBG1.

**Hard inputs:** accepted P0 + BS1.

**Outcome:** validate/bind one normalized source-agnostic task contract; require finite `max_steps`/retry/attempt/effect ceilings; preserve opaque origin provenance; validate/persist host-supplied concise `PlanProposal` thành deterministic private plan với stable step IDs/order, declared effects/verification và replan reason. Không tích hợp live LLM.

**Non-goals:** thực thi step, file/command effect, checkpoint, WBS parsing/scheduling, cross-task readiness hoặc delegation.

**Downstream artifact:** accepted task/plan DTO manifest cho FS2 và FS5.

### FS2 — DF2: điều khiển internal steps tuần tự

**Primary goal:** PBG1.

**Hard inputs:** accepted DF1 manifest + BS1.

**Outcome:** one-active-task guard, internal step states/order, first-pending selection, normalized finite attempt/stop enforcement, persist-before-effect request, terminal aggregation; `blocked | failed | unknown_outcome` bypass remaining normal steps tới `handoff_pending`. Assignment mới bị typed rejection khi task còn active hoặc `handoff_pending`.

**Non-goals:** cross-WBS readiness, task queue, chọn task tiếp theo, parallelism, actual file/command execution hoặc checkpoint bytes.

**Downstream artifact:** accepted step-control/terminal-result interface cho FS3–FS6.

### FS3 — DF3: file step an toàn

**Primary goal:** PBG2.

**Hard inputs:** accepted P1 + accepted DF2 step interface.

**Outcome:** contained `read/write/append` executor và bounded deterministic result.

**Non-goals:** delete, commands, checkpoint hoặc reporting.

**Downstream artifact:** accepted file-result manifest cho FS5/FS6/IS1.

### FS4 — DF4: exact-command step an toàn

**Primary goal:** PBG2.

**Hard inputs:** accepted P1 + accepted DF2 step interface; accepted containment helper nếu BS1 xác định dùng chung DF3 component.

**Outcome:** exact command executor với contained cwd, exact allowlist, `shell:false`, timeout/signal/output bounds và deterministic result. Command-based verify bắt buộc dùng chính executor/checkpoint/result path này; không có verify-only escape hatch.

**Non-goals:** arbitrary shell/network, file actions, checkpoint store hoặc reporting.

**Downstream artifact:** accepted command-result manifest cho FS5/FS6/IS1.

### FS5 — DF5: persist và resume internal step execution

**Primary goal:** PBG3.

**Hard inputs:** accepted P2 + accepted DF1–DF4 manifests.

**Outcome:** atomic private checkpoint, task/origin/execution/plan binding, every committed transition, settled restart no-op, current→`UNKNOWN_OUTCOME`, bounded attempt accounting, completed non-replay, durable terminal→`handoff_pending` recovery và artifact-key collision handling không re-execute task.

**Non-goals:** WBS history, concurrent API, migration, distributed/power-loss guarantee.

**Downstream artifact:** accepted checkpoint/recovery manifest cho FS6/IS1.

### FS6 — DF6: provisional task result/evidence

**Primary goal:** PBG4.

**Hard inputs:** accepted DF1–DF5 manifests.

**Outcome:** deterministic TaskHandoff JSON/Markdown cho `completed_provisional | blocked | failed | unknown_outcome`; create-once atomic commit, byte-identical recommit idempotent, conflict/stale commit reject và giữ `handoff_pending`. Sau successful commit Agent trở lại idle không cần PM acknowledgement.

**Non-goals:** task acceptance, real network/Team transport, WBS update, sprint/mission reporting, dashboard, long-term GC/retention hoặc product repair.

**Downstream artifact:** accepted result manifest cho IS1.

## 6. IS1 — Vertical integration

**Hard readiness:** accepted BS1 và accepted DF1–DF6 manifests.

**Goal:** chứng minh một Durable Agent xử lý một contracted task bằng 3–5 internal steps và settle mọi representative terminal path.

**Fixture:**

- cùng normalized contract chạy với standalone/WBS-derived origin mà không cần WBS graph;
- deterministic host adapter cung cấp concise `reason`/plan artifact; plugin không gọi live LLM;
- plan trong finite `max_steps` có `reason`, `file`, `command`, deterministic `verify`, terminal `handoff`;
- sequential execution, không delegation;
- command-based verify dùng cùng tracked DF4 effect path; undeclared case reject trước effect;
- second assignment reject khi active hoặc `handoff_pending`;
- restart sau committed step, trong current effect và trong `handoff_pending`;
- completed effect không replay; current effect tạo `UNKNOWN_OUTCOME`;
- representative `blocked`, `failed` và `unknown_outcome` bypass remaining normal steps, commit correct provisional handoff;
- commit failure giữ busy; same-byte recommit idempotent; conflicting bytes reject;
- successful artifact commit là settlement cho mọi status; sau commit mới nhận task tiếp theo, không cần PM acknowledgement;
- handoff không tự accept task.

**Non-goals:** chọn/chạy task khác trong WBS, đọc WBS graph, coordinate members, real Team transport hoặc tự accept task.

Nếu integration yêu cầu đổi DF contract, stop/lookback/RCA và material rebaseline; không patch ngầm.

## 7. QS1 — Qualification

Tổng hợp PBG1–PBG4 coverage, DF1–DF6 acceptance, E2E evidence, rework/stop metrics, limitations và learning candidates; yêu cầu HUMAN `accept | defer | reject`.

## 8. Agent Team delivery governance

- **DG1:** mọi task có goal/input/output/risk/unlock rõ.
- **DG2:** review/update/re-review nằm trong bounded WBS envelope.
- **DG3:** task/sprint/program stop trigger dẫn tới lookback/RCA trước resume/rebaseline.
- **DG4:** learning check/candidate routing tại mọi closure.

PM Agent Lookback/Improvement Skill hỗ trợ DG3/DG4 nhưng không nằm trong Durable Agent product scope.

Mọi sprint WBS phải reference/hash-bind `goal-scope-baseline-v2.md` và `memo-agent-team-pm-goals-v1.md`. WBS của P0, BS1, FS1, FS2, FS5, FS6 và IS1 còn phải bind `memo-durable-agent-team-member-compatibility-v3.md` và map relevant tests vào acceptance.

## 9. Metrics

- DF1–DF6: mỗi function hoàn thành trong một feature sprint.
- First-pass feature acceptance: ít nhất 5/6.
- Không feature sprint nào phát hiện unplanned mechanism discovery sau implementation start.
- Không task vượt hai correction attempts của delivery WBS; runtime attempt policy là khái niệm riêng và phải finite theo TaskContract/engine ceilings.
- Command-pass/review-HIGH reject: tối đa 1/6.
- Coordinator packaging/hash/budget defects: 0.
- Capacity-only WBS revisions: 0.
- Learning check coverage: 100% closure events.
- 100% accepted TaskContracts có finite normalized `max_steps`, per-step/effective attempts, total attempts và applicable effect ceilings; missing/unbounded/overflow/contradictory policy reject trước effect.
- Zero `delete`, network, delegation, WBS orchestration hoặc plugin-owned live LLM invocation trong MVP.
- 100% `verify` evidence đến từ declared deterministic checks; command checks dùng DF4 path.
- Handoff tests không phụ thuộc PM acknowledgement; commit failure không được về idle.

## 10. Revision note

v10 supersedes `ke-hoach-sprint-agile-v9.md` cho candidate planning hiện tại. Revision này đóng P0 oracle/seam/decision owner, dependency semantics, terminal vectors và time-bound artifact identity mà không mở rộng product scope.
