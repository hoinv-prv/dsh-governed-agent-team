# Goal và Scope Baseline — Durable Agent MVP v2

## 1. Product outcome

Một Durable Agent là một member của Agent Team. Agent nhận đúng một contracted task từ PM, tự chia thành internal steps, chạy tuần tự mà không delegation, persist/resume không replay effect, ghi một deterministic provisional TaskHandoff artifact và sau đó mới sẵn sàng nhận task tiếp theo.

Task có thể standalone hoặc được PM trích từ WBS. WBS orchestration nằm ngoài scope; core Durable Agent không cần biết WBS graph.

## 2. Product business goals

### PBG1 — Tự hoàn thành một contracted task

Agent validate TaskContract, tạo và điều chỉnh private internal step plan trong contract, chạy tuần tự đến completion hoặc một typed terminal outcome.

### PBG2 — Thực hiện local effects an toàn

File/command steps chỉ chạy trong approved paths/exact commands; rejected cases tạo zero outside effect.

### PBG3 — Resume không replay completed effects

Committed step progress sống qua restart; completed step không chạy lại; interrupted current effect trở thành `UNKNOWN_OUTCOME` và không được tự replay.

### PBG4 — Handoff provisional result dễ review

Agent ghi deterministic TaskHandoff artifact đủ để PM/reviewer quyết định, nhưng không tự accept task.

## 3. Product functions

| ID | Function | Primary goal | Feature sprint |
|---|---|---|---|
| DF1 | Nhận source-agnostic TaskContract và tạo internal step plan | PBG1 | FS1 |
| DF2 | Điều khiển một active task và internal steps tuần tự | PBG1 | FS2 |
| DF3 | Thực hiện contained file steps `read/write/append` | PBG2 | FS3 |
| DF4 | Thực hiện exact-command steps | PBG2 | FS4 |
| DF5 | Persist/recover task và step execution | PBG3 | FS5 |
| DF6 | Ghi deterministic provisional TaskHandoff và trở lại idle sau settlement | PBG4 | FS6 |

Mỗi function được detail-design, test và implement trong đúng một feature sprint sau khi prerequisite PoC/basic design đã accepted.

## 4. Task source và execution identity

PM gửi một normalized TaskContract. Optional origin metadata:

- `origin.kind = standalone | wbs`;
- opaque `source_ref`;
- optional parent revision/hash.

Origin chỉ dùng cho identity/provenance. Nó không mở rộng authority và không làm core đọc/validate WBS graph, chọn WBS task hoặc coordinate members.

Mỗi execution bind bất biến ít nhất `task_id`, `contract_id`/contract hash và `task_run_id`. Một task mới hoặc retry ở cấp PM phải có `task_run_id` riêng; internal step retry/replan không được đổi execution identity.

## 5. TaskContract tối thiểu

TaskContract phải có:

- task/contract identity, execution identity và origin provenance;
- goal;
- accepted input refs/hashes;
- expected outputs;
- non-goals;
- allowed paths;
- exact allowed commands;
- verification/evidence requirements;
- finite `max_steps`;
- normalized finite retry/attempt policy;
- finite effect ceilings liên quan tới step được phép, như timeout và byte/output limits;
- stop/block conditions;
- PM/reviewer handoff destination metadata.

Nếu thiếu minimum identity cần để bind execution/handoff (`task_id`, `contract_id`/contract hash hoặc `task_run_id`), Agent trả typed assignment rejection trước activation và không tạo handoff không định danh. Sau khi identity đã bind, thiếu material field khác tạo `blocked` outcome và handoff trước effect.

### 5.1 Retry và attempt invariants

MVP không dùng một task retry ceiling chung thay cho TaskContract, nhưng contract-specific policy luôn bị chặn bởi finite engine ceilings. P0 phải chọn và chứng minh một normalized representation thỏa mọi invariant sau:

1. mọi limit là positive safe integer trong canonical unit và không vượt engine ceiling;
2. precedence cho per-step limit là `step override > step-type override > default`, sau đó vẫn bị chặn bởi remaining `max_total_attempts`;
3. một attempt được debit và persist trước khi plugin thực thi hoặc yêu cầu thực thi step; attempt có success, failure hoặc `UNKNOWN_OUTCOME` đều đã bị debit;
4. replan không reset `max_steps`, attempt đã dùng, total budget hoặc effect ceilings;
5. `UNKNOWN_OUTCOME` không được tự retry;
6. missing, unbounded, overflow hoặc contradictory policy bị từ chối trước effect;
7. exhaustion tạo typed terminal outcome, không tự retry toàn task ngoài contract;
8. `handoff` commit chỉ được retry bằng cùng canonical bytes, theo finite bounded policy; exhaustion giữ Agent ở `handoff_pending` và cần operator/PM resolution.

P0 freeze retry/attempt normalization và manifest cho P2 consume. P1/BS1 freeze exact units và engine ceilings cho file/command effects; không được nới các invariant trên.

`max_steps` cũng phải finite positive integer dưới engine ceiling. Initial plan và mọi replan không được vượt limit. E2E fixture dùng 3–5 steps nhưng capability không hard-code con số đó.

## 6. Internal step plan

Supported step types:

1. `reason` — host Agent runtime tạo concise decision/plan artifact; plugin chỉ validate/persist, không tự gọi LLM và không lưu private chain-of-thought.
2. `file` — contained `read/write/append`.
3. `command` — exact local command với `shell:false`.
4. `verify` — tạo deterministic evidence bằng declared assertions hoặc exact commands theo rule ở mục 6.1; model judgment không phải verification evidence.
5. `handoff` — required terminalization step ghi provisional TaskHandoff artifact cho mọi terminal status.

Mỗi step có stable ID/order, goal, type, inputs, expected output/evidence, allowed effect, verification và retry/stop rule. `handoff` đứng cuối normal success path, nhưng terminal controller được phép bypass các normal step chưa chạy để vào `handoff_pending` khi có terminal outcome.

### 6.1 Verify không phải effect bypass

- File/hash/content/schema assertions do plugin thực hiện chỉ được observational/read-only.
- Một verify check dùng process phải đi qua cùng DF4 exact-command executor, allowlist, contained cwd, `shell:false`, timeout/output bounds, persist-before-effect, result ledger và recovery semantics như ordinary command step.
- Mọi mutation có thể xảy ra từ command-based verify phải được khai báo trong allowed effects/paths. Không khai báo được thì check bị reject trước khi chạy.
- Verify không có command path, filesystem path hoặc retry channel riêng để vượt TaskContract.

### 6.2 Host runtime boundary và seam dùng cho P0

Durable Agent plugin không tích hợp hoặc invoke live LLM trong MVP. Host Agent runtime tạo plan/reason artifacts bên ngoài plugin và chuyển qua bounded data/function seam.

P0 dùng deterministic adapter/test double, không dùng real host hoặc model provider. Input tối thiểu của seam là immutable TaskContract bytes/hash; output là `PlanProposal` gồm producer metadata, contract/execution identity, parent plan revision/hash khi replan, concise reason và ordered proposed steps. Plugin chỉ validate, normalize, persist hoặc trả typed rejection/blocker.

Vì plugin không sở hữu invocation, host timeout/provider recovery nằm ngoài seam MVP. Missing, malformed, stale hoặc identity-mismatched proposal bị reject trước effect. P0 phải có dependency/import/spy evidence rằng plugin không gọi model; BS1 chỉ freeze production DTO sau accepted P0 evidence.

### 6.3 Autonomous planning/replanning

Agent không cần PM approval riêng cho initial step plan hoặc thay đổi chưa-chạy steps nếu vẫn giữ nguyên:

- task goal/outputs/non-goals;
- input và execution identity;
- allowed paths/commands/effects;
- verification/acceptance evidence;
- retry/attempt/effect budgets.

Mỗi replan phải persist new plan revision/hash và concise reason trước next effect. Completed step history/identity không được sửa. Material deviation tạo typed `blocked` outcome và TaskHandoff về PM.

## 7. Single-member lifecycle và terminal transitions

Normal success path:

```text
idle
→ assigned
→ planning
→ executing
→ handoff_pending
→ handoff_artifact_committed
→ idle
```

Terminal outcome matrix:

| Trigger | TaskHandoff status | Remaining normal steps | Next state |
|---|---|---|---|
| Tất cả required work/verification thành công | `completed_provisional` | none | `handoff_pending` |
| Sau khi execution identity đã bind: invalid/missing material contract or plan, unsupported step, attempted material deviation, declared stop/block condition | `blocked` | mark `not_executed` | `handoff_pending` |
| Deterministic non-retryable execution failure hoặc attempt exhaustion | `failed` | mark `not_executed` | `handoff_pending` |
| Restart thấy external effect đã bắt đầu nhưng chưa settle | `unknown_outcome` | mark `not_executed`; không replay | `handoff_pending` |
| Atomic handoff commit lỗi nhưng còn budget | status giữ nguyên | không chạy lại task step | ở `handoff_pending`, retry cùng bytes |
| Handoff commit exhaustion hoặc local store unavailable | chưa settled | không chạy lại task step | ở `handoff_pending`; cần operator/PM resolution |
| Atomic handoff commit thành công | status giữ nguyên | none | `handoff_artifact_committed → idle` |

Rules:

- Chỉ một task active hoặc handoff-pending tại một thời điểm.
- Task mới trong `assigned/planning/executing/handoff_pending` bị typed `BUSY` rejection.
- Mọi terminal status đều phải đi qua `handoff_pending`; không terminal outcome nào tự trở về idle hoặc tiếp tục normal effects.
- Handoff được settled khi exact TaskHandoff artifact đã atomic-persist; không cần PM acknowledgement, kể cả status `blocked | failed | unknown_outcome`.
- Chỉ handoff commit thành công mới cho phép Agent trở lại idle và nhận task tiếp theo.

## 8. Durability semantics

- Persist task/contract/origin/execution identity và internal plan trước effect đầu tiên.
- Persist current step/attempt và debit budget trước mỗi external effect.
- Persist every committed step result và terminal transition.
- Restart với settled state là no-op rồi có thể normalize về idle.
- Restart với current effect chưa settle → `UNKNOWN_OUTCOME`; không tự replay.
- Task execution terminal nhưng handoff artifact chưa commit → reconstruct exact deterministic handoff from committed state, không replay task effects.
- Handoff artifact đã commit → task được coi handed off; restart có thể trở lại idle.
- Illegal hoặc identity-conflicting checkpoint state fail closed, không phát sinh effect.

MVP chỉ claim atomic local replacement trên pinned environment, không claim power-loss/distributed durability.

## 9. Effect scope

### Included

- Local `read/write/append` within workspace containment.
- Exact local commands with contained cwd, exact argv/timeout/expected exit, `shell:false`, bounded stdout/stderr/result.
- Command-based verify chỉ qua cùng exact-command effect path.

### Deferred

- `delete` file action;
- arbitrary shell;
- network/external effects;
- parallel steps;
- subagent/member delegation;
- full WBS parsing/scheduling;
- multiple queued/active tasks;
- real PM/network transport;
- plugin-owned live LLM invocation/model routing/context admission;
- generic history/concurrent checkpoint API;
- migration and distributed/power-loss guarantees.

## 10. TaskHandoff settlement và identity

TaskHandoff contains:

- task/contract/origin/execution identity;
- internal plan revision/hash;
- status `completed_provisional | blocked | failed | unknown_outcome`;
- ordered step states/results/attempts, kể cả `not_executed` remainder;
- outputs and hashes;
- verification/evidence refs;
- blocker/failure/unknown-outcome details;
- limitations;
- requested PM decision.

TaskHandoff never sets `accepted` and never selects the next task.

Artifact settlement invariants:

1. artifact key bind immutable `contract_id`/contract hash và `task_run_id`;
2. commit là create-once; retry cùng key + cùng canonical bytes là idempotent success;
3. cùng key nhưng khác bytes, stale plan revision hoặc identity mismatch bị reject, không overwrite;
4. task mới không được che khuất hoặc replace artifact cũ;
5. P2/BS1 phải freeze exact key/path layout và collision/restart vectors trước FS5/FS6;
6. retention/archival duration là deployment policy ngoài MVP, nhưng implementation không được dựa vào overwrite để tái sử dụng key.

## 11. Required integration acceptance

IS1 must prove:

1. standalone and WBS-derived origins normalize to the same core behavior without loading a WBS graph;
2. host adapter supplies one concise reason/plan artifact and task becomes 3–5 `reason/file/command/verify/handoff` steps within finite `max_steps`;
3. plugin makes no live LLM call; missing/malformed/stale proposal fails before effect;
4. execution is sequential and non-delegating;
5. `read/write/append`, exact-command effects và command-based verify đều dùng contained tracked effect paths;
6. restart after committed step does not replay it;
7. restart with current effect yields `UNKNOWN_OUTCOME`, bypasses remaining normal steps và commits corresponding handoff;
8. `blocked` và `failed` cũng bypass remaining normal steps, commit đúng status rồi mới idle;
9. second assignment during execution or handoff pending is rejected;
10. TaskHandoff commit is sufficient to return idle and accept the next task; commit failure remains busy;
11. deterministic handoff remains provisional, create-once/idempotent và cannot self-accept;
12. internal replan within contract succeeds without resetting identity/budget; attempted material deviation blocks before effect.

## 12. Agent Team/PM governance inputs

Planning/execution must also obey:

- `memo-agent-team-pm-goals-v1.md`;
- `memo-durable-agent-team-member-compatibility-v3.md`;
- `quy-trinh-capture-kinh-nghiem-v1.md`.

DG1–DG4/PM lookback are delivery governance, not Durable Agent product functions.

## 13. Revision note

v2 supersedes `goal-scope-baseline-v1.md` cho candidate planning hiện tại. Revision này đóng terminal lifecycle, verify-effect routing, retry/attempt invariants, P0 host/plugin seam và handoff identity invariants; không mở rộng product sang WBS orchestration, multi-task queue, delegation, network, delete hoặc plugin-owned LLM.
