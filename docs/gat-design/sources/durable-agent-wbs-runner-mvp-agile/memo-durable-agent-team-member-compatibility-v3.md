# Memo — Durable Agent tương thích vai trò Agent Team member v3

## 1. Background

Durable Agent là một Agent Team member:

```text
PM giao một standalone hoặc WBS-derived TaskContract
→ Agent nhận host-supplied plan artifact và chạy internal steps, không delegation
→ mọi terminal outcome hội tụ tại handoff_pending
→ Agent atomic-persist provisional TaskHandoff
→ handoff được coi settled
→ Agent trở lại idle và có thể nhận task tiếp theo
```

WBS orchestration, cross-task readiness và acceptance thuộc PM/Agent Team, nằm ngoài Durable Agent MVP.

## 2. Compatibility constraints

### TC1 — Source-agnostic contract

Core chỉ nhận normalized TaskContract. `standalone | wbs` origin là opaque provenance, không làm thay execution semantics hoặc mở rộng authority.

### TC2 — Một task tại một thời điểm

Trong `assigned/planning/executing/handoff_pending`, assignment mới bị typed `BUSY` rejection. MVP không queue nhiều tasks và không chọn task tiếp theo.

Assignment thiếu minimum execution identity bị typed rejection trước activation; sau khi identity đã bind, thiếu material field khác tạo `blocked` handoff trước effect.

### TC3 — Autonomous internal steps qua bounded host seam

Host Agent runtime được tự tạo/replan chưa-chạy steps trong immutable task contract; plugin nhận bounded `PlanProposal`, validate/persist artifacts nhưng không tự gọi LLM. Material deviation phải tạo `blocked` terminal outcome. Supported types: `reason/file/command/verify/handoff`; plan/replan không vượt finite `max_steps` và không reset identity/budget.

P0 dùng deterministic adapter/test double. Real host transport, provider authentication/routing/recovery nằm ngoài plugin MVP; BS1 freeze production DTO sau accepted P0 evidence.

### TC4 — Verify không bypass effect control

Pure file/hash/content/schema assertions là observational. Exact-command verify dùng cùng DF4 allowlist/executor, containment, timeout, checkpoint, attempt ledger và `UNKNOWN_OUTCOME` semantics; không có verify-only effect channel.

### TC5 — Mọi terminal outcome đều handoff

`completed_provisional | blocked | failed | unknown_outcome` đều dừng remaining normal effects, chuyển `handoff_pending` và commit TaskHandoff mang đúng status. Chỉ successful atomic commit mới cho phép về idle.

Handoff commit chưa thành công giữ Agent `handoff_pending`; retry chỉ dùng cùng canonical bytes và finite budget, không replay task effects. Exhaustion cần operator/PM resolution.

### TC6 — Artifact-based settlement, không PM ack

MVP coi handoff hoàn tất khi deterministic TaskHandoff artifact được atomic-persist. Không cần PM acknowledgement, kể cả handoff status là `blocked | failed | unknown_outcome`. Sau commit, Agent trở lại idle.

Future transport/ack adapters có thể consume artifact nhưng không được làm core replay task effects hoặc phụ thuộc WBS semantics.

### TC7 — Provisional only

TaskHandoff chỉ có `completed_provisional | blocked | failed | unknown_outcome`. PM/reviewer sở hữu acceptance.

### TC8 — Restart safety

- Completed effects không replay.
- Unsettled current effect sau restart thành `UNKNOWN_OUTCOME` và không tự retry.
- Task terminal nhưng chưa commit handoff → reconstruct exact handoff từ committed state.
- Handoff đã commit → task đã handed off; Agent có thể idle.
- Illegal/identity-conflicting state fail closed.

### TC9 — Immutable execution/handoff identity

Execution bind `task_id`, `contract_id`/contract hash và `task_run_id`. Committed handoff của execution khác không được overwrite. Cùng key + cùng canonical bytes là idempotent success; cùng key + khác bytes, stale revision hoặc identity mismatch bị reject và giữ `handoff_pending`.

P2/BS1 freeze exact logical key/path và collision vectors. Long-term retention/GC, migration và distributed collision nằm ngoài MVP.

## 3. Required tests

1. Standalone và WBS-derived origins có cùng normalized core behavior.
2. Core chạy WBS-derived task không cần toàn bộ WBS.
3. WBS metadata không mở rộng paths/commands/retry/budget.
4. Missing/malformed/stale/mismatched PlanProposal reject trước effect; plugin model invocation count bằng 0.
5. Second assignment bị reject khi executing.
6. Second assignment bị reject khi handoff pending.
7. `completed_provisional | blocked | failed | unknown_outcome` đều bypass remaining normal steps và commit đúng handoff.
8. Sau atomic TaskHandoff commit, Agent nhận task tiếp theo mà không cần PM ack.
9. Handoff commit failure giữ busy và không replay task effects.
10. Restart trước handoff commit tạo đúng handoff mà không replay effects.
11. Restart sau handoff commit trở lại idle.
12. Command-based verify dùng cùng tracked DF4 path; undeclared case reject trước effect.
13. Same-byte recommit idempotent; conflicting/stale/cross-execution commit reject, không overwrite.
14. TaskHandoff deterministic và luôn provisional.
15. Future adapter compatibility không thay DF1–DF5 contracts.

## 4. WBS requirements

Future WBSs cho P0, BS1, FS1, FS2, FS5, FS6 và IS1 phải reference/hash-bind memo này và map relevant tests vào acceptance. P0 chỉ map các tests thuộc contract/plan/seam; terminal checkpoint/collision vectors thuộc P2/BS1/FS5/FS6/IS1, không bị kéo vào P0.

## 5. Provenance và revision

HUMAN đã quyết định:

- handoff settled khi TaskHandoff artifact đã persist, không cần PM acknowledgement;
- Agent tự chủ initial plan/replan trong immutable TaskContract;
- retry policy finite nhưng do từng TaskContract quy định trong engine hard bounds;
- file scope là `read/write/append`, defer `delete`;
- step types là `reason/file/command/verify/handoff`;
- host runtime reasons; plugin không gọi live LLM;
- verify chỉ dùng deterministic declared checks.

v3 supersedes `memo-durable-agent-team-member-compatibility-v2.md` cho candidate planning hiện tại. Revision chỉ đóng terminal convergence, verify effect routing, host seam evidence và handoff identity/idempotency; không mở rộng product scope.
