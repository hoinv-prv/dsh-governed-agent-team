# AIP Detail Spec for AI Work System MVP
Version: 0.2  
Scope: MVP only  
Updated: 2026-05-10 (CR-AIWS-2026-05-001 applied: added §3.5 retrospective AIP authoring, §4.3 slug prefix taxonomy, §5.7 cross-AIP relationship fields + 3 optional metadata fields in §5.3/§5.4/§5.5 + §12.4 lint note)

---

# 1. Mục đích

Tài liệu này detail hóa spec cho **AIP (AI Implementation Plan)** trong MVP.

Mục tiêu:
- chốt vai trò của từng loại AIP
- chốt naming / placement
- chốt metadata tối thiểu
- chốt section structure
- chốt step structure
- chốt PLAN → EXEC handoff
- chốt rule update và lint targets

---

# 2. Vai trò của AIP trong MVP

## 2.1. AIP là gì
AIP là **execution control artifact** cho task hoặc workstream cụ thể.

AIP dùng để:
- định nghĩa objective
- định nghĩa scope / non-scope
- định nghĩa outputs
- chia step lớn
- chỉ ra references / guidelines / skills liên quan
- cung cấp done criteria và review points

## 2.2. AIP không là gì
AIP không phải:
- SOP
- AI Work Contract
- reusable playbook
- runtime notebook
- queue
- findings log
- final wiki

## 2.3. Nguyên tắc chính
- **stable by default**
- **update by exception**
- **do not store runtime state directly**

> **Provenance vs runtime state (CR-AIWS-2026-06-015).** A **write-once** pointer set once at execution start — e.g. `runtime_workspace` (§5.4) — is **provenance**, the same class as `plan_source` / `updated_at`, and does NOT violate "do not store runtime state directly." Genuine runtime state (step status, queue, findings, capture inbox) stays in the workspace. The cross-AIP **registry/index** (`.ai-work/aip/index.jsonl`) is a generated projection under `.ai-work/aip/`. The AIP-id **counter** lives in the local, gitignored `.ai-work/account_info.yaml` (per-member `next_aip_id`; the v1 `id_claims.jsonl` ledger is **retired** — CR-AIWS-2026-06-015 v2). Neither is embedded in an AIP file.

---

# 3. Các loại AIP trong MVP

## 3.1. AIP_ROOT — RETIRED (CR-AIWS-2026-07-026)

AIP_ROOT đã bị loại khỏi artifact model (2026-07-13). AIWS **không có project-level AIP**: bộ AIP chỉ gồm các task-control artifacts (AIP_PLAN / AIP_EXEC / AIP_LOCAL), và **không tồn tại quan hệ cha–con giữa AIP** (xem §5.7 — PLAN→EXEC semantics). Project context (objective / scope / priorities / constraints / prefix conventions) sống trong `SOP_MASTER` (§1–2, §Project Priorities, §AIP Conventions).

*(Số mục 3.1 giữ nguyên để bảo toàn cross-reference; §3.2 trở đi không đổi.)*

---

## 3.2. AIP_PLAN
### Purpose
Create execution handoff package.

### Typical use
- research planning
- review planning
- design planning
- scope clarification
- task breakdown

### Placement
`.ai-work/aip/<account_id>/plans/AIP-PLAN-<NNN>-<slug>.md`  (NEW, CR-015 v2; legacy flat `.ai-work/aip/plans/…` preserved)

### Lifecycle
- authored/refined during planning
- stabilizes before execution
- should not absorb runtime findings

---

## 3.3. AIP_EXEC
### Purpose
Execution control for actual work.

### Typical use
- create/update deliverable
- actual review execution
- actual wiki update
- actual organization task

### Placement
`.ai-work/aip/<account_id>/exec/AIP-EXEC-<NNN>-<slug>.md`  (NEW, CR-015 v2; legacy flat `.ai-work/aip/exec/…` preserved)

### Lifecycle
- created after plan handoff or for direct execution tasks
- may be updated only by explicit replan
- does not become runtime state container

---

## 3.4. AIP_LOCAL
### Purpose
Optional local/private execution notes.

### Placement
`.ai-work/aip/<account_id>/local/AIP-LOCAL-<NNN>-<slug>.md`  (NEW, CR-015 v2; legacy flat `.ai-work/aip/local/…` preserved)

### Rule
- not a required shared control artifact
- can be ignored by shared workflows unless explicitly referenced

---

## 3.5. Retrospective AIP authoring (ship-first emergencies)

In normal flow, an AIP is authored BEFORE substantive work begins (see §General Principle 5 in SOP_MASTER). Exception: prod-impact emergencies where patch must land before any planning artifact exists.

In such cases, the codifying AIP is authored RETROSPECTIVELY after the fix has shipped. The retrospective AIP retroactively documents:
- (a) what was patched (file/area/scope)
- (b) what tests are still missing or incomplete
- (c) which design / spec / wiki docs need updating to reflect the change
- (d) audit scope for sibling features potentially affected

Retrospective AIPs MUST set frontmatter field `authored_retroactively: true` and reference the patch commit(s) in the `## Background / Context` section. Status flow: `draft` → `done` (no `active` since execution already happened).

Retrospective AIPs are an exception, not a routine path. Use only when ship-first was unavoidable. Repeated retrospective authoring on planned work indicates discipline drift, not flexibility.

---

# 4. Naming convention

## 4.1. File naming
### AIP_PLAN
`AIP-PLAN-<NNN>-<slug>.md`

### AIP_EXEC
`AIP-EXEC-<NNN>-<slug>.md`

### AIP_LOCAL
`AIP-LOCAL-<NNN>-<slug>.md`

## 4.2. Slug guideline
- lowercase
- hyphen-separated
- short but meaningful
- reflect deliverable/workstream, not every micro-step

### Good examples
- `review-manufacturing-order-update`
- `design-wiki-entry-model`
- `update-shared-processing-wiki`

### Avoid
- too generic: `task-1`
- too long / sentence-like
- encoding too many unrelated outputs in one slug

## 4.3. Slug prefix taxonomy (recommended)

When the project has many AIPs, recommended prefix patterns make `ls .ai-work/aip/<account_id>/exec/` (new AIPs; or legacy flat `ls .ai-work/aip/exec/`) self-categorizing:

| Prefix | Use for | Example |
|---|---|---|
| `t<NNN>-<feat>` | Planned implementation tasks mapped to project task tracker | `t042-user-export` |
| `bugfix-<scope>` | Retrospective bugfix AIP (see §3.5) | `bugfix-auth-session-leak` |
| `uiux-<scope>` | UI/UX redesign or polish work | `uiux-dashboard-empty-state` |
| `<feat>-design` | Design phase of a feature split into design + implementation | `payment-gateway-design` |
| `<feat>-implementation` | Implementation phase | `payment-gateway-implementation` |
| `test-infra-<scope>` | Testing infrastructure / harness changes | `test-infra-cleanup` |

These prefixes are **recommended, not enforced**. Projects MAY define additional domain-specific prefixes in their `SOP_MASTER.md` (§AIP Conventions). Lint does not validate prefix membership.

Convention adoption typically happens at project setup — projects choose which prefixes to use and document in `SOP_MASTER.md` (§AIP Conventions). *(Registry re-homed từ AIP_ROOT — CR-AIWS-2026-07-026.)*

---

# 5. Metadata spec

## 5.1. YAML frontmatter required
All AIP files should use YAML frontmatter.

## 5.2. AIP_ROOT metadata — RETIRED (CR-AIWS-2026-07-026)

`aip_root` không còn là `artifact_type` hợp lệ (xem §3.1). *(Số mục giữ nguyên để bảo toàn cross-reference.)*

## 5.3. AIP_PLAN metadata
```yaml
artifact_type: aip_plan
artifact_id: AIP-PLAN-001
title: <title>
status: draft|active|done|archived
project: <project-name>
owner: <optional>
authored_retroactively: <optional, true if retrospective per §3.5>
depends_on: <optional, free-form: AIP IDs whose outputs this AIP needs>
related: <optional, free-form: sibling AIPs / capabilities touched, no hard dependency>
updated_at: YYYY-MM-DD
```

## 5.4. AIP_EXEC metadata
```yaml
artifact_type: aip_exec
artifact_id: AIP-EXEC-001
title: <title>
status: draft|active|done|archived
project: <project-name>
owner: <optional>
plan_source: AIP-PLAN-001
authored_retroactively: <optional, true if retrospective per §3.5>
depends_on: <optional, free-form: AIP IDs whose outputs this AIP needs>
related: <optional, free-form: sibling AIPs / capabilities touched, no hard dependency>
runtime_workspace: <optional, write-once provenance pointer to the runtime workspace; set by aiws-aip run start (CR-AIWS-2026-06-015 F5); NOT runtime state — see §2.3>
lint_accept: <optional, list of HUMAN-accepted lint findings; mutes named codes on THIS AIP — see Lint_and_Tooling_Spec_MVP §16 (CR-AIWS-2026-06-065)>
updated_at: YYYY-MM-DD
```

## 5.5. AIP_LOCAL metadata
```yaml
artifact_type: aip_local
artifact_id: AIP-LOCAL-001
title: <title>
status: draft|active|done|archived
project: <project-name>
owner: <optional>
authored_retroactively: <optional, true if retrospective per §3.5>
depends_on: <optional, free-form: AIP IDs whose outputs this AIP needs>
related: <optional, free-form: sibling AIPs / capabilities touched, no hard dependency>
updated_at: YYYY-MM-DD
```

## 5.6. Enum rules
### status
- `draft`
- `active`
- `done`
- `archived`

Lifecycle-edge actors (CR-AIWS-2026-07-040): `draft → active` is stamped by `aiws-aip run start` (surgical frontmatter write, draft-only — any other status is left untouched); `active → done` (or `draft → done` for legacy/retrospective AIPs) is set at close per aiws-aip run §"When closing an AIP"; `archived` is manual.

## 5.7. Cross-AIP relationship fields (optional)

`depends_on` and `related` are optional free-form fields for tracking AIP lineage:
- `depends_on` — list of AIP IDs whose outputs this AIP requires. Use when the work cannot start (or makes no sense) without those prior AIPs' deliverables.
- `related` — list of AIP IDs / capability IDs this AIP touches without hard dependency. Use to flag sibling work for reviewers and audit.

Format is free-form: comma-separated, plus-separated, or YAML list — readable by humans and grep-able. No typed schema; lint does not validate values.

`depends_on` semantically differs from `plan_source`: `plan_source` is the canonical PLAN→EXEC handoff (typed, well-known), while `depends_on` is for arbitrary AIP-to-AIP dependencies beyond the plan handoff.

**PLAN→EXEC semantics (CR-AIWS-2026-07-026):** PLAN→EXEC là **phase-handoff** của một khối công việc, **không phải quan hệ cha–con**. Một PLAN dạng program ĐƯỢC PHÉP fan-out nhiều EXEC — mỗi EXEC nhận handoff qua `plan_source` riêng (một-PLAN-nhiều-EXEC = *handoff fan-out* hợp lệ; tiền lệ: AIP-PLAN-002 → 17 EXECs). KHÔNG suy diễn hierarchy từ fan-out này; không tồn tại root/anchor AIP nào phía trên PLAN/EXEC (AIP_ROOT retired — §3.1).

Lineage trace example:
```
grep -l "AIP-EXEC-038" .ai-work/aip/exec/*.md
```

---

# 6. Required sections

## 6.1. AIP_ROOT required sections — RETIRED (CR-AIWS-2026-07-026)

(aip_root retired — xem §3.1. Project Priorities / Scope / Constraints sống trong `SOP_MASTER`. Số mục giữ nguyên để bảo toàn cross-reference.)

---

## 6.2. AIP_PLAN required sections
1. Objective
2. Background / Context
3. Scope
4. Non-scope — được phép fold thành `### Out of Scope` bên trong `## Scope` (chuẩn `AIP_PLAN_TEMPLATE` hiện hành; blessed per CR-AIWS-2026-08-055 / DP-1025-B)
5. Expected Outputs
6. References to Read First
7. Assumptions / Constraints
8. Open Questions / Risks
9. Execution Steps
10. Done Criteria
11. Review Points

---

## 6.3. AIP_EXEC required sections
1. Objective
2. Execution Scope
3. Expected Outputs
4. References to Read First
5. Execution Steps
6. Current Risks / Constraints
7. Done Criteria
8. Review / Finalization Notes
9. Re-plan Rule
10. Re-plan Log

(8→10 per CR-AIWS-2026-08-055 / DP-1025-B — spec đuổi theo `AIP_EXEC_TEMPLATE` thực tế: mọi AIP active đều đã mang `## Re-plan Rule` + `## Re-plan Log`; AIP trong `done/` giữ nguyên, không hồi tố.)

---

## 6.4. AIP_LOCAL required sections
1. Objective
2. Notes
3. Personal Constraints / Reminders
4. Local Execution Notes

---

# 7. Step structure spec

## 7.1. Required fields per step
Each step in AIP_PLAN / AIP_EXEC must define:

- Step ID
- Step Title
- Objective
- Recommended Mode
- Applicable Guidelines
- Inputs
- Expected Outputs
- Done Condition
- Notes / Constraints

## 7.2. Optional fields per step
- Recommended Skills
- Workspace Actions
- Step Dependencies
- Review Note
- Assigned Agent — optional (CR-AIWS-2026-07-018; activation semantics CR-AIWS-2026-08-044 C0): agent handle (== desk_id) expected to execute this step via `/aiws-agent-run --aip <this AIP>`, or `auto` (capability routing resolves the desk — CR-AIWS-2026-08-045). **Absent = KHÔNG dispatch — main session executes như AIWS thuần (default; không run/desk nào tham gia).** Surfaced into the ASC; the agent runtime enforces membership (a run on this AIP is refused if its instance is not in the AIP's assigned set — stage-3 gate) and requires the AIP `status: active`.
- Executor — optional (CR-AIWS-2026-08-044 C4): plan-time executor cho step ĐÃ chỉ định (`main_session` | `claude_subagent`); absent = desk default (`run_policy.executor`). Chỉ có nghĩa khi step có `Assigned Agent:`; runtime validate ∈ desk `executors_allowed`. Surfaced into the ASC; lựa chọn executor là của HUMAN/AIP — model không tự quyết tại dispatch.
- Difficulty — optional (CR-AIWS-2026-07-059): the step's difficulty for capability routing — `low` / `medium` / `high`. Absent = unspecified. A routing input only; no behaviour on its own — **routing chỉ chạy khi step opt-in qua `Assigned Agent:`** (CR-AIWS-2026-08-044 C0); Difficulty cũng chọn execution tier trong desk đã chọn (cheapest-capable — CR-AIWS-2026-08-045).
- Kind — optional (CR-AIWS-2026-07-059): one or more task-kind tags (comma-separated) from the controlled set `triage, plan, code, patch_proposal, sql, test_design, review, research, organize, canonical_edit`, matched against an agent's `capability.task_kinds` during routing (routing mechanics: the agents-pack runtime).
- Procedure — optional (CR-AIWS-2026-08-25 Item 4): One of:
  - Ordered list of actions (1. … 2. …)
  - Reference to playbook: `.ai-work/procedural/path/to/playbook.md`
  - Skill invocation: `/skill <name>`
- Acceptance — optional (CR-AIWS-2026-08-25 Item 4): Spec section or checklist that judges this step's output:
  - `Done Criteria` of this step (if final step or reviewing mode)
  - `04_findings.md#STEP-NN` (if Gate U1 record exists)
  - Reference to external spec / checklist

## 7.3. Recommended step format
```md
## Step: STEP-02 — Identify mandatory review dependencies

Objective:
Identify mandatory downstream functions for first-pass review scope.

Recommended Mode:
Research

Applicable Guidelines:
- playbooks/investigate_specific_function.md
- queue_rules.md

Recommended Skills:
- skills/generate_active_step_context.md
- skills/extract_dependency_candidates.md

Inputs:
- wiki/function/manufacturing_order_update.md
- wiki/function/inventory_update.md
- truth/canonical/shared_processing_design.md

Expected Outputs:
- mandatory dependency list
- optional dependency list
- supporting findings

Done Condition:
Mandatory dependencies are identified with reasonable confidence.

Procedure:
- Research each candidate in context of the codebase design
- Cross-check against wiki/function entries for scope alignment

Acceptance:
- Done Criteria (confidence in dependency scope)

Notes / Constraints:
Do not over-expand into secondary downstream topics unless needed.

Workspace Actions:
- create/update queue items
- update findings
- update open questions
```

## 7.4. Step ID convention
Suggested:
- `STEP-01`
- `STEP-02`
- `STEP-03`

Must be unique inside one AIP.

---

# 8. Granularity rules

## 8.1. Default granularity
AIP should map to a **medium-sized deliverable or workstream**.

## 8.2. Split triggers
Create separate AIPs when:
- multiple major outputs of different kinds appear
- multiple independent scopes appear
- clear PLAN → EXEC handoff exists
- AIP becomes too large to re-orient even with Active Step Context

## 8.3. Avoid
- one AIP for every tiny micro-task
- one AIP for an entire broad phase with many unrelated outputs

---

# 9. PLAN → EXEC handoff spec

## 9.1. Handoff package minimum
AIP_PLAN must hand off at least:
- Objective
- Background / Context
- Scope
- Non-scope
- Expected Outputs
- References to Read First
- Task step skeleton
- Open Questions
- Risks / Constraints
- Done Criteria
- Review Points

## 9.2. Consumption rule
AIP_EXEC should consume this handoff by default.

## 9.3. Drift rule
If execution requires changing macro scope or outputs:
- do not silently drift
- update AIP explicitly or create re-plan action

---

# 10. Update rules

## 10.1. AIP update allowed when
- objective changes
- scope / non-scope changes
- expected outputs change
- major assumptions change
- explicit re-plan required

## 10.2. AIP update not required for
- new findings
- queue changes
- runtime open questions
- minor execution notes
- evolving draft output

These belong to Workspace.

---

# 11. Relationship to other artifacts

## 11.1. With Contract
AIP must not contradict AI Work Contract.

## 11.2. With Workspace
AIP directs execution; Workspace stores execution state. The runtime workspace is the executor-agnostic **Task Workspace** (`.ai-work/workspaces/{account}/{task_id}/`) — the same Task Workspace serves an AIP run, an agent run, and an agent-via-AIP run. When an agent performs a task via this AIP, the agent run **reuses this AIP's Task Workspace** (resolved via the `runtime_workspace` pointer, §5.4) rather than creating a second runtime workspace. (CR-AIWS-2026-06-057 Phase 1.)

## 11.3. With Active Step Context
Active Step Context is materialized from AIP + linked runtime state.

## 11.4. With Playbooks/Skills
AIP step references them; they do not replace AIP.

---

# 12. AIP lint targets

## 12.1. Metadata lint
- artifact_type valid
- artifact_id present
- status valid
- plan_source present for AIP_EXEC

## 12.2. Section lint
- required sections present
- missing required section = error

## 12.3. Step lint
- Step ID present
- Recommended Mode present
- Applicable Guidelines present
- Objective present
- Expected Outputs present
- Done Condition present
- INFO: If `Recommended Mode: Executing` and neither `Procedure:` nor a non-generic skill (`Recommended Skills:` value not `aiws-aip` or `none`) is given, lint reports INFO-level guidance to clarify execution approach

## 12.4. Reference lint
- guideline paths exist if declared
- skills paths exist if declared
- plan_source exists if declared
- `depends_on` / `related` fields: NOT structurally validated by lint (free-form by design — see §5.7)

---

# 13. Minimal examples

## 13.1. Good AIP_PLAN
- one clear deliverable
- execution skeleton present
- references curated
- review points present
- handoff ready

## 13.2. Bad AIP_PLAN
- too many unrelated outputs
- vague steps
- no done criteria
- no review points
- execution would have to re-plan everything

---

# 14. Kết luận

Spec này chốt AIP như:
- stable execution control artifact
- medium-granularity deliverable/workstream plan
- bridge giữa governance và runtime
- source of Active Step Context
- foundation for execution without silent drift

---

# Knowledge-runtime sprint addendum — Working AIP connection

## Working AIP remains the execution guardrail

Runtime knowledge access may clarify the task, select relevant knowledge, and provide inputs to execution.

However, the following artifacts do not replace Working AIP:

- Wiki Meta / Index entries
- curated knowledge objects
- retrieval summaries
- working notes / notebook fragments
- Workspace state
- AIP Templates
- raw/source references

## What may feed Working AIP

The following may feed Working AIP when sufficiently mature and relevant:

- clarified task intent
- scope and constraints
- selected knowledge entries
- key findings from Knowledge Hub
- disambiguation results
- Task Lens-influenced context
- selected AIP Template
- HUMAN clarifications / approvals

## Execution rule

When meaningful execution continues, it should continue under Working AIP guardrail.

Ongoing knowledge access can continue during execution, but it remains support for the Working AIP-led task flow.

---

# Personal Notebook and Working AIP addendum

Personal Notebook does not replace Working AIP.

If a Personal Notebook note affects the current execution basis, it should be reflected into Working AIP or an appropriate task artifact.

Working AIP remains the minimum execution guardrail for meaningful execution.

Personal Notebook may provide personal/cross-task reference, but it is not an execution artifact.

---

# Source Understanding Artifact and Working AIP addendum

A Source Understanding Artifact may feed a Working AIP as source-derived context.

It does not replace Working AIP.

If using a Source Understanding Artifact changes execution basis, the Working AIP or task artifact should reflect the relevant decision/constraint.

Working AIP remains the execution guardrail.

---

# Task Lens, AIP Template, and Working AIP canonical addendum

Task Lens may influence or suggest an AIP Template, but it does not replace AIP Template.

Task Lens may feed Working AIP context, but it does not replace Working AIP.

Working AIP remains the task-specific execution guardrail.

If selected, adjusted, or expanded lens affects execution basis, it should be reflected in Working AIP or Workspace trace when appropriate.

No-Lens mode can still lead to AIP Template suggestion or Working AIP creation based on confirmed task intent.

---

# Controlled Knowledge Promotion AIP addendum

Relevant output-producing AIP Templates with HUMAN feedback/fix/acceptance loop should include a default step:

```text
Post-feedback Knowledge Promotion Lookback
```

Default flow:
```text
AI creates output
  ↓
HUMAN feedback
  ↓
AI fix/revision
  ↓
HUMAN OK / acceptance
  ↓
AI collects improvement candidates and Knowledge Promotion candidates
```

This step:
- collects candidates only
- does not auto-promote
- does not auto-update AIP Template/guideline/prompt/playbook/process
- marks apply-back as deferred unless separately approved

AIP Template improvement candidate is not an applied template update.

---

# v0.9.8 Wiki Meta / Index AIP runtime addendum

When AIP execution requires project source lookup, AI should use Wiki Source Meta / Index flow:

```text
lookup → meta_locator → artifact_locator when needed
```

AIP/Working AIP should treat `artifact_locator` as AIWS-readable source representation.

If source representation quality is insufficient, mark `source_representation_quality_issue` and ask for conversion/HUMAN confirmation rather than inferring from original non-text raw file.

---

# v0.9.9 Working AIP Connection addendum

Working AIP Connection is the minimal handoff from discovered/reused/runtime context into an execution-ready Working AIP.

Core rules:
- Discovery/reuse/context can inform execution.
- Working AIP controls execution.
- Before non-trivial execution, AI must have or create a Working AIP.
- Support artifacts can feed Working AIP but cannot replace it.
- aiws-aip run executes against Working AIP.
- If Working AIP is missing or not ready, prepare/update it first.

Minimum Working AIP sections:
```markdown
## Task Intent
## Scope
## Expected Output
## Context / Source References
## Selected Task Lens / Mode
## Execution Steps
## Guardrails / Constraints
## Open Questions / Blockers
## Done Criteria
```

Relevant specs:
- `Working_AIP_Connection_Spec_MVP.md`
- `Working_AIP_Connection_Runtime_Guidance_MVP.md`
- `Working_AIP_Connection_Samples_Appendix_MVP.md`
