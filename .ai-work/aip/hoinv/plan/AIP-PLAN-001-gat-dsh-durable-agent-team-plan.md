---
artifact_type: aip_plan
artifact_id: AIP-PLAN-001
title: "Plan GAT design and implementation for DSH durable agent teams"
status: done
project: "dsh-governed-agent-team"
owner: "hoinv"
runtime_workspace: __PROJECT_ROOT__/.ai-work/workspaces/hoinv/TASK-20260926-plan-001
updated_at: 2026-09-26
template_source: AIP_PLAN_TEMPLATE
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. Scope change → Re-plan Log. -->

# AIP_PLAN — Plan GAT design and implementation for DSH durable agent teams

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — file hiện rỗng; sử dụng Universal Gates từ template PLAN hiện hành:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — xem `STEP-00`.
- **Gate U2 Confirm-understanding-of-input (soft)** — xem `## Input Understanding`.
- **Gate U3 Open Points tracking (soft)** — xem `## Open Questions` và workspace `05_open_questions.md`.

## Task Classification
- Why PLAN is used: Yêu cầu cần đối chiếu một proposal DSH với design/implementation hiện tại của GAT, xác định gaps, target architecture, migration sequence và verification trước khi thay đổi code.
- Expected next artifact:
  - [ ] AIP_EXEC
  - [ ] direct execution without separate EXEC
  - [ ] not decided yet

## Objective
Tạo một kế hoạch evidence-backed để chỉnh sửa design và implementation của GAT, nhằm tích hợp vào DSH thành một durable agent team có thể thực hiện mission, trong khi giữ GAT là lifecycle/mission authority và dùng member-binding extension làm boundary cho Durable Agent cùng các capability tương lai.

## Selected Task Lens / Mode
- Lens: No-Lens
- Reason: Đây là planning task kết hợp architecture, implementation impact và migration; không có preset project-specific đã được xác nhận bao phủ đầy đủ.
- Search/execution effect: Ưu tiên proposal DSH, design/implementation hiện tại của GAT, test surfaces, lifecycle/persistence boundaries và AIWS architecture planning guidance.
- Resolved references: DSH member-binding proposal; AIWS Architecture Design; Truth/Contract; AIP PLAN template.
- Deferred lookups: GAT project design docs, runtime modules, persistence schemas, tests và DSH integration seams sẽ được resolve sau Gate U1 bằng bounded repository discovery.
- Expansion allowed: yes

## Background / Context
- DSH proposal yêu cầu versioned member-admission/binding extension, normalized Team initialization, pre-inbox bind/recover/release lifecycle, durable opaque attachments, scoped policy/tool contributions và một authoritative mission lifecycle.
- Proposal là `Status: proposed`, vì vậy kế hoạch phải phân biệt rõ phần đã có trong GAT, phần cần refactor, phần phụ thuộc thay đổi DSH, và các điểm cần HUMAN quyết định.
- GAT repository hiện dùng AIWS; mọi phân tích và plan runtime sẽ nằm trong task workspace, không ghi findings vào AIP.

## Scope
### In Scope
- Map proposal requirements và acceptance criteria sang current GAT design/code/tests.
- Xác định design changes: ownership boundaries, APIs/contracts, state machine, persistence/replay, initializer adapter, binding registry, prompt/tool contribution, mission lifecycle và diagnostics.
- Xác định implementation work packages, dependencies, migration/compatibility strategy, test strategy và review gates.
- Chỉ rõ integration contract giữa GAT plugin và DSH core/Durable Agent mà GAT cần tiêu thụ hoặc yêu cầu.
- Đề xuất thứ tự delivery an toàn, ưu tiên backward compatibility của GAT-only mode.

### Out of Scope
- Sửa code hoặc canonical/Truth artifacts trong task PLAN này.
- Tự quyết định hoặc áp dụng DSH upstream changes.
- Mặc định hóa Durable Agent cho mọi GAT profile.
- Promote findings vào Wiki/Truth khi chưa có HUMAN-controlled review.

## Expected Outputs
- Workspace findings về current-state GAT và proposal-to-code gap matrix.
- Target design delta có ownership/API/state/persistence/lifecycle boundaries.
- Implementation roadmap theo phases/work packages, dependencies và migration order.
- Verification matrix liên kết acceptance criteria với unit/integration/recovery/disposal/UI/SDK tests.
- Decision log/open questions và handoff skeleton đủ để tạo một hoặc nhiều AIP_EXEC.

## References to Read First
### Truth First
- `.ai-work/truth/SOP_MASTER.md`
- `.ai-work/truth/AI_WORK_CONTRACT.md`
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

### Wiki First
- `SRC-METHOD-methodology-10-design-architecture-design-mvp-md-994c` → `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`
- `wiki:none` — lookup cho GAT/member-binding/durable mission không tìm thấy registered project source phù hợp; proposal path do HUMAN cung cấp được dùng như raw external design input.

### Optional Supporting Refs
- `/home/hoinv/deepseek-harness/.agents/notes/proposed/feature/2026-09-26-gat-member-binding-extension.md`
- GAT source/design/test files được xác định trong bounded discovery sau Gate U1.

## Input Understanding
| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| DSH GAT member-binding extension proposal | GAT giữ Team lifecycle + mission authority; binder chỉ validate/install/recover/release bounded attachment trước first request; initializer cung cấp normalized specs; attachments phải durable và recoverable | Proposal là target direction để tham khảo, chưa phải canonical mandate | Mức nào cần mirror chính xác trong GAT repo; DSH upstream APIs nào đã tồn tại; deliverable mong muốn là roadmap hay ready-to-execute task split | ⬜ pending |
| Current GAT repository | Cần evidence từ design, code, persistence schema và tests để phân loại reuse/refactor/new work | Repository hiện tại là implementation authority cho GAT | Chưa inventory vì Gate U1 chưa pass | ⬜ pending |

## Assumptions / Constraints
- Giữ một authoritative mission/task/member model trong GAT; không tạo parallel Durable Agent mission state.
- Binders không được nắm Team authority hoặc mở rộng filesystem/tool permissions bằng prompt text.
- Lifecycle split trước initial inbox là vùng rủi ro cao, cần explicit state/rollback/recovery invariants và test-first migration.
- Operating Memory đã đọc ngày 2026-09-26 và hiện không có mục liên quan.

## Open Questions
- Open Points log: `.ai-work/workspaces/hoinv/TASK-20260926-gat-dsh-durable-team-plan/05_open_questions.md`
- HUMAN có muốn output cuối là design/implementation roadmap ở mức actionable hay một WBS/AIP_EXEC decomposition có owner/estimate?
- Phạm vi có bao gồm đề xuất thay đổi cụ thể ở DSH upstream hay chỉ nêu required integration contracts từ phía GAT?

## Risks / Constraints
- Proposal có sibling notes chưa được cung cấp; đọc rộng ngoài artifact đã nêu có thể làm tăng scope và đòi hỏi lookup/authorization riêng.
- Hiện trạng GAT có thể đã triển khai một phần tương đương dưới tên khác; phải tránh thiết kế trùng state hoặc API.
- Thay đổi member provisioning/inbox admission có thể gây regression về cancellation, deduplication, replay và disposal.
- Attachment protocol dễ trở thành escape hatch nếu không giới hạn JSON shape/count/size/version và callback authority.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Xác nhận với HUMAN rằng task sẽ tạo kế hoạch design/implementation evidence-backed cho GAT theo proposal DSH, không sửa code trong giai đoạn PLAN.

Recommended Mode:
Clarifying

Applicable Guidelines:
- `.ai-work/truth/SOP_MASTER.md`
- `wiki:none` — preflight không tìm thấy project wiki source trực tiếp cho GAT/member-binding.

Recommended Skills:
- `aiws-aip`

Inputs:
- Yêu cầu của HUMAN.
- DSH member-binding extension proposal.

Expected Outputs:
- Task understanding note trong workspace.
- HUMAN confirmation evidence.

Done Condition:
HUMAN explicit confirm scope/output hoặc explicit ủy quyền bỏ gate.

Notes / Constraints:
- Không bắt đầu inventory/repository analysis trước khi Gate U1 pass.

Workspace Actions:
- Khởi tạo workspace sau khi AIP lint sạch và run start.
- Ghi task understanding và confirmation evidence.

### Step: STEP-01 — Inventory current GAT architecture and implementation
Objective:
Xác định authoritative current state của GAT về team enablement, member lifecycle, initial inbox, persistence/replay, mission/task/work state, policy/tools và disposal.

Recommended Mode:
Research

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

Recommended Skills:
- `context-delegation`

Inputs:
- Current GAT design, source, schemas và tests.
- Proposal requirements/acceptance criteria.

Expected Outputs:
- Source map và current-state architecture summary trong workspace.
- Requirement-to-current-state evidence matrix.

Done Condition:
Mỗi proposal area có evidence path/symbol hoặc explicit evidence gap; conflicts được giữ riêng.

Notes / Constraints:
- Bounded discovery; source code/tests có authority cao hơn stale design notes về implemented behavior.

Workspace Actions:
- Ghi findings vào `04_findings.md` và supporting artifacts trong workspace.
- Capture reusable retrieval gaps ngay khi phát hiện.

### Step: STEP-02 — Define target design delta and integration boundary
Objective:
Thiết kế delta tối thiểu cho GAT: normalized initializer, binder registry/protocol, provisioning state/commit order, durable attachments, recovery/release, scoped contributions, mission readiness và diagnostics.

Recommended Mode:
Architecture planning

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

Recommended Skills:
- `context-delegation`

Inputs:
- STEP-01 evidence matrix.
- DSH proposal and acceptance criteria.

Expected Outputs:
- Target component/responsibility map.
- API and data-contract sketch.
- Lifecycle/state transition and failure/rollback invariants.
- GAT-versus-DSH ownership matrix.

Done Condition:
Target design covers every accepted proposal requirement or records a justified deviation/open decision.

Notes / Constraints:
- Không biến binder thành parallel lifecycle authority.
- Phân biệt stable GAT contract với DSH-specific adapter implementation.

Workspace Actions:
- Ghi design delta và decision candidates trong workspace.

### Step: STEP-03 — Build implementation and migration roadmap
Objective:
Chuyển target design thành work packages có dependency, compatibility strategy, rollout order và rollback boundaries.

Recommended Mode:
Planning

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/50_tooling/specs/Tooling_Implementation_Spec_MVP.md`

Recommended Skills:
- `dsh-wbs-build`

Inputs:
- STEP-02 target design.
- Current repository module/test map.

Expected Outputs:
- Phased implementation roadmap.
- Work-package dependency graph và suggested AIP_EXEC split.
- Migration/backward-compatibility plan.

Done Condition:
Roadmap có thể được giao thực thi mà không cần đoán ownership, dependency hoặc exit criteria chính.

Notes / Constraints:
- Không coi work estimate là fact nếu chưa có evidence; ghi sizing tương đối và uncertainty.

Workspace Actions:
- Soạn roadmap và handoff skeleton trong workspace.

### Step: STEP-04 — Define verification, review gates, and final recommendation
Objective:
Liên kết acceptance criteria với tests/evidence, review risks và đưa ra recommended delivery sequence.

Recommended Mode:
Review planning

Applicable Guidelines:
- `.ai-work/truth/canonical/methodology/10_design/Architecture_Design_MVP.md`

Recommended Skills:
- `dsh-council-review`

Inputs:
- Target design delta.
- Implementation roadmap.
- Proposal acceptance criteria and risks.

Expected Outputs:
- Acceptance-to-verification matrix.
- Risk register and HUMAN decision points.
- Final design/implementation plan and EXEC handoff recommendation.

Done Condition:
Plan có traceability từ proposal → current evidence → design delta → implementation package → verification evidence.

Notes / Constraints:
- Advisory review không tự phê duyệt canonical/DSH upstream changes.

Workspace Actions:
- Hoàn thiện final plan trong workspace và chạy task lint.

## Done Criteria
- [ ] Scope đủ rõ và được HUMAN confirm tại Gate U1.
- [ ] Current-state GAT được inventory bằng evidence paths/symbols/tests.
- [ ] Mỗi requirement và acceptance criterion của proposal có disposition.
- [ ] Target design giữ rõ authority boundaries của GAT, binder và DSH/Durable Agent.
- [ ] Implementation roadmap có phases, dependencies, migration strategy và rollback boundaries.
- [ ] Verification matrix bao phủ unit, integration, persistence/recovery, disposal, SDK/snapshot và diagnostics.
- [ ] Open points có owner/status và không bị biến thành assumption im lặng.
- [ ] Handoff đủ để tạo AIP_EXEC/WBS tiếp theo.
- [ ] Gate U2 Input Understanding và Gate U3 Open Points được xử lý.

## Review Points
- Có lifecycle window nào cho phép first model request trước bind/recover không?
- Có duplicate source of truth nào cho mission/task/member/readiness không?
- Attachment versioning/limits/replay có deterministic và fail-closed không?
- GAT-only behavior và snapshots có giữ backward compatibility không?
- Tool/prompt contributions có đúng scope và không biến text thành permission không?
- Implementation order có giữ repository testable ở từng phase không?

## Handoff to EXEC
- Objective: Implement approved GAT design delta for DSH durable agent-team integration.
- Scope / non-scope: Sẽ lấy từ final PLAN; upstream DSH changes tách riêng nếu cần.
- Expected outputs: code, schema/events/SDK updates, tests, docs và migration evidence.
- Refs: final workspace plan + proposal + exact source map.
- Step skeleton: protocol/contracts → persistence → pre-inbox lifecycle → orchestration → initializer/policy → diagnostics/docs.
- Open questions: link tới workspace `05_open_questions.md`.
- Risks / constraints: lifecycle regression, recovery incompatibility, authority leakage.
- Done criteria: acceptance-to-verification matrix trong final plan.
- Review points: independent design/code review và real Loader composition.
- Gate status: U1/U2/U3 evidence từ PLAN workspace.

## Pre-flight Pending Captures
- [IMPORTED 2026-09-26] type="wiki_meta_update_candidate" candidate_kind="retrieval_improvement" suggested_target="wiki_meta" artifact="DSH GAT member-binding extension proposal" lookup_query="GAT governed agent team durable mission member binding; member binding extension DSH agent team" reason="Reusable cross-repository architecture proposal used as a structural planning input was not registered in the project Wiki Source Index"

## Re-plan Log
- (no re-plan yet)
