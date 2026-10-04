# Memo — Agent Team và PM goals cho mission Durable Agent MVP v1

## 1. Trạng thái và phạm vi

Đây là project-level planning/execution memo theo chỉ dẫn trực tiếp của HUMAN.

**Áp dụng cho:** coordinator và Agent Team khi lên plan, review WBS và thực hiện mission implement Durable Agent MVP.

**Không phải:** Durable Agent product goal, product function, task acceptance, WBS execution approval hoặc quyền tự thay đổi scope.

Mọi sprint WBS của mission mới phải khai báo memo này như một planning/governance source và chứng minh cách áp dụng các goal dưới đây.

## 2. Agent Team delivery goals

### DG1 — Clear work contract

Mỗi sprint/task trước dispatch phải có:

- một goal quan sát được;
- Durable Agent function/business goal liên quan;
- lý do task đã ready;
- exact accepted inputs/design/PoC/evidence;
- technical issues đã clear;
- remaining/deferred risks;
- output cụ thể;
- named downstream consumer/unlock;
- non-goals;
- verification/review contract;
- rework envelope;
- stop triggers.

Nếu là design, phải biết design làm gì và technical mechanism đã được PoC clear chưa. Nếu là implementation, phải bind exact accepted design/oracle. Nếu là test/oracle, phải nêu claim, source contract và known-bad/mutation cần reject.

### DG2 — Bounded rework trong cùng WBS

Ordinary review/update/re-review được plan và budget trước:

```text
candidate
→ independent review + batched finding ledger
→ update/finalize
→ independent re-review
```

Giữ cùng WBS revision khi goal, deliverable, dependencies, scope/effects, commands, acceptance và ceilings không thay đổi. Tối đa hai correction attempts; exhaustion chuyển `BLOCKED`.

Successor WBS chỉ dùng cho material contract change, không dùng chỉ để cấp thêm attempts.

### DG3 — Stop, lookback/RCA và controlled rebaseline

Phải dừng dispatch và phân tích khi xảy ra một trong các pattern:

- một task exhaust attempt 2;
- review/update loop vượt correction envelope;
- hai task liên tiếp cần rework;
- từ hai task trong cùng sprint dùng attempt 2;
- two command-pass attempts bị independent review reject với in-scope HIGH finding;
- cùng missing assumption làm nhiều task fail;
- accepted PoC assumption bị falsify;
- cần tăng attempt ceiling hoặc capacity-only revision;
- coordinator có packaging/hash/budget/settlement defect.

Tại stop point phải preserve actuals/evidence, phân loại root cause và chọn `continue | retry | add_poc | reduce_scope | rebaseline | stop`. Material change cần successor WBS và HUMAN approval.

### DG4 — Capture kinh nghiệm có governance

Learning check bắt buộc tại task/attempt/review/PoC/sprint close.

Reusable lesson được capture thành evidence-backed candidate có provenance, statement type, confidence, limitations, sensitivity, status `candidate` và named destination.

Candidate có thể làm input cho current design review, later sprint hoặc post-MVP backlog nhưng không tự trở thành requirement, accepted design, canonical knowledge hoặc execution instruction.

Không capture raw conversation, chain-of-thought, credentials/secrets hoặc unbounded logs.

## 3. PM Agent goal/capability

### PG1 — Lookback/Improvement

PM Agent phải hỗ trợ DG3/DG4 bằng cách:

1. đọc WBS, execution ledger, review findings, metrics và learning candidates;
2. phân biệt normal rework với failure system;
3. xác định task/sprint/program stop trigger;
4. thực hiện evidence-backed lookback/RCA;
5. đánh giá blast radius;
6. đề xuất `continue | retry | add_poc | reduce_scope | rebaseline | stop`;
7. phát sinh learning candidates khi có reusable lesson;
8. trình HUMAN decision khi authority/scope/budget thay đổi.

PM Agent không được tự approve task, revise approved WBS, tăng budget, promote memory candidate hoặc resume blocked mission nếu chưa có authority.

Design/implementation của một automated PM Lookback/Improvement Skill là mission riêng; trong Durable Agent MVP, coordinator phải áp dụng workflow này bằng governed planning/execution artifacts.

## 4. Cách dùng memo khi planning

Trước khi trình một sprint WBS:

- map từng task tới DG1 work-contract fields;
- budget DG2 review/update envelope;
- khai báo DG3 stop thresholds và stop actions;
- khai báo DG4 learning-check output/path;
- chỉ ra PoC nào đã clear technical uncertainty;
- không đưa DG/PG goals vào Durable Agent product function list;
- independent reviewer phải kiểm tra memo compliance trước approval request.

## 5. Cách dùng memo khi execution

Trong execution:

- không dispatch task thiếu DG1 readiness;
- ordinary correction dùng DG2 envelope, không tạo revision;
- khi DG3 trigger xảy ra, stop trước khi tiêu thêm attempt;
- chạy DG4 learning check tại mọi closure;
- mọi worker completion vẫn provisional cho tới independent acceptance;
- preserve attempts, evidence, decisions và budget actuals qua mọi rebaseline.

## 6. Provenance và authority

**HUMAN directive:** “Các goal trong scope B (Agent Team) và scope C (PM Agent) thì hãy memo lại vì đó chính là goal dành cho bạn khi lên plan (wbs) và thực hiện theo plan để hoàn thành mission là implement Durable Agent MVP.”

Memo này là authoritative project planning input cho mission hiện tại. Nó không thay thế exact WBS approval hoặc product acceptance.

Không có authorized memory backend trong session hiện tại; vì vậy không tuyên bố nội dung đã được persist thành personal/shared Agent memory. Project memo này là durable repository artifact và phải được referenced/hash-bound bởi future sprint WBSs.
