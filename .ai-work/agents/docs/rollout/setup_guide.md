# Setup Guide — AI Agents Pack (current agents)  (Phase J-1)

> **Status: CANONICAL (beta) — AI Agents Pack, version: see `PACK_VERSION.md` (pack root).** Promoted by CR-AIWS-2026-06-055 (2026-06-24); status formalized by CR-AIWS-2026-08-036. Built by AIP-EXEC-141 (Phase J-1) STEP-02.
>
> **SCOPE = current agents only.** This guide installs/enables the **3 priority agents**
> (`aiws_detailed_design_review_agent`, `aiws_testcase_review_agent`, `aiws_pm_agent`) + the A/B/C foundation
> (Blueprint/Task-Desk model, `/aiws-agent-create`, desk workspace + run/learning loop) and the
> Runtime Command Set — Core runtime (`/aiws-agent-run` + `/aiws-agent-feedback`), Desk lifecycle (`/aiws-agent-upgrade`/`clone`/`rename`), and the `/aiws-agent` router. The remaining agent types
> (program phases **D**/**E**/**F**/**G**/**H** — coordinators, metadata, tooling, wiki lifecycle,
> wiki-consumer) are **deferred — see `known_limitations_and_backlog.md`**.
>
> The pack is **file-first**: there is no executable `aiws` CLI. "Install" means copying files and
> wiring a task desk's context — nothing more. All paths below are relative to the **pack root** (`product/agents/` canonical · `.ai-work/agents/` when installed — byte-identical mirror).

## 1. Prerequisites

- **Python 3.8+, stdlib only** — no `pip install`. The only tool, `tooling/run_agent.py`, imports
  stdlib modules only (`argparse`, `datetime`, `re`, `shutil`, `pathlib`).
- **Run Python with `py`** — on this machine bare `python` is a broken WindowsApps stub; use
  `py tooling/run_agent.py ...`.
- **UTF-8** — the tool reconfigures stdout/stderr to UTF-8 (cp932-safe on Windows); no extra setup
  needed, but write/read the agent files as UTF-8.
- A target project with a **Knowledge Hub** (Wiki Source Index) so task desks can ground Wiki-first.
  The current default sample wiring points at `.ai-work/wiki_sources/index.jsonl` (see §4).

## 2. Install ≠ auto-run (read first)

Installing the pack **never runs an agent**. Copying the files only makes the blueprints and
commands available. Creating a task desk (`/aiws-agent-create`) does **not** run it either —
`create ≠ run`. An agent only acts when a HUMAN explicitly starts a run (`/aiws-agent-run start`)
and then the AI reads the materialized Active Run Context and acts as the agent. Nothing auto-runs,
auto-chains, or auto-promotes at any point.

## 2b. Đề xuất thay đổi pack — id namespace (CR-AIWS-2026-08-001)

Dự án cài pack muốn đề xuất thay đổi pack/AIWS → viết IR vào `.ai-work/upstream_requests/` của **chính dự án**
(template ship sẵn, CR-AIWS-2026-08-018) rồi raise upstream.
Ghi chú anchor: bản cài dùng `.ai-work/upstream_requests/`; phía repo nguồn AIWS nó được stage vào `product/change_requests/intake/`.
**KHÔNG mint id trong namespace upstream** (`AP-CR-*`,
`CR-AIWS-*`); dùng namespace local riêng (vd `CR-<PROJECT>-*`). Registry AP-CR hiện hành:
`docs/ap_cr_ledger.md` (check collision TRƯỚC khi tham chiếu). Trước khi đề xuất, nên upgrade/diff
vs bản AIWS mới nhất — tránh đề xuất lại thứ đã ship.

## 3. What to copy / wire

There are **two distinct modes** — do not conflate them. The difference is **task desks**: dev/dogfood
keeps the sample task desks; install/promote **never** ships task desks (they are created on the target).
Because every cross-reference inside the pack is **relative**, the tree resolves identically wherever it
lands (this is what makes a future promotion to `.ai-work/` a mechanical path rebase — see
`promotion_readiness_note.md`).

### (a) Try in place — inside the installed pack `.ai-work/agents/` (dogfood)

For iterating on or dogfooding the pack in this staging repo, nothing is copied out: you run against
the tree as-is, **including the 5 sample task desks** (`*__sample_project`) that ship here as dev/test
fixtures. Point a run at an existing sample task desk (e.g.
`detailed_design_review_agent__sample_project`) or `/aiws-agent-create` a new one in
`agents/task_desks/`. This mode is the only one that uses the `agents/task_desks/` content directly.

### (b) Install / promote into a real project (ships **NO** task desks)

When installing the pack into a real target project (the future promotion CR, AP-CR-10), the ship-set
is **only** the reusable definitions + commands + tooling — **never any task desk**:

- `agents/blueprint_registry.yaml`
- `agents/blueprints/**`
- `agents/templates/**`
- `agents/execution_tiers.yaml` — execution-tier registry (CR-AIWS-2026-08-045): 2 lớp — tier trừu tượng
  + provider profile map tier→{model, effort}; **SHIPPED** (MVP profile `claude`); đổi mapping = sửa file
  này trên target (single point of update).
- `commands/*.md`
- `tooling/run_agent.py`

> **`pack_config.yaml` KHÔNG ship** (CR-AIWS-2026-08-044 C0): file optional, chỉ tạo trên target khi dự
> án muốn TẮT dispatch (`dispatch_enabled: false`). Vắng file = dispatch ON — cài pack đã là opt-in.

Task Desks are **NOT shipped**. On the target, `task_desks/` starts **empty** (a write location only —
the ship-set contains no desk; CR-AIWS-2026-08-060), and a **real task desk is created on the
target via `/aiws-agent-create`** — never by copying a `*__sample_project` desk across. The 5
sample task desks stay behind in staging as fixtures (the naming law `*__sample_project` = never-ship;
see `agent_authoring_guide.md`). The PROMOTION-EXCLUDES invariant for this ship-set is recorded in
`promotion_readiness_note.md` §3(1).

Minimum set to enable the current agents (the **ship-set** of mode (b); mode (a) additionally has the
sample `instances/` already present):

```
<pack_root>/
  agents/
    blueprint_registry.yaml        # index of available blueprints (3 priority + coordinator)
    blueprints/
      _shared/review/              # shared review process/checklists/output_templates (referenced, not copied per-agent)
      aiws_detailed_design_review_agent/
      aiws_testcase_review_agent/
      aiws_pm_agent/
      aiws_wiki_meta_strategy_coordinator/   # foundation sample (planning-only); not in J-1 run scope
    task_desks/                    # NOT in the install ship-set — created on target via /aiws-agent-create
                                   #   (mode (a) only: the 5 *__sample_project fixtures live here in staging)
    templates/                     # desk / run / learning / memory templates used by the commands
  commands/                        # the 8 command specs (prompt/spec, file-first): Core runtime + Desk lifecycle + router
    aiws-agent-create.md           #  Core runtime
    aiws-agent-run.md
    aiws-agent-feedback.md
    aiws-agent-review-learning.md
    aiws-agent-upgrade.md          #  Desk lifecycle (AP-CR-27)
    aiws-agent-clone.md            #  Desk lifecycle (AP-CR-28)
    aiws-agent-rename.md           #  Desk lifecycle (AP-CR-30)
    aiws-agent.md                  #  Convenience router (AP-CR-22)
  tooling/
    run_agent.py                   # thin runtime orchestrator (stdlib; run with py)
```

Notes:
- `_shared/review/` is **document-type-agnostic** review assets (process, severity, finding format,
  source-trace + lesson-capture rules, the common checklist, the output templates). Both review
  blueprints reference it by relative path (`../_shared/review/...`) — do not copy it per agent or
  the trees will drift.
- `agents/templates/` holds the desk skeleton (`context/`, `run/`, `tools/`),
  `learning_candidate_schema.md`, `confirmed_memory_schema.md`, `learning_loop_lifecycle.md`,
  `instance_creation_wizard.md`, `instance_setup_summary.md`, etc. The commands read these.
- The command specs are **prompt/specs**, not executable binaries. The tooling-backed verbs
  (`/aiws-agent-run` + the Desk-lifecycle `upgrade`/`clone`/`rename`) run via `run_agent.py`;
  `create`/`feedback`/`review-learning` are followed by the AI directly.

## 4. How the 3 blueprints are registered

The blueprints are already registered — no extra registration step. `agents/blueprint_registry.yaml`
lists each blueprint with `blueprint_id`, `name`, `type`, `status: active`, a **relative** `path:`
under `agents/blueprints/…/`, and a `description`. The current registry (`version: 1`) contains:

| `blueprint_id` | `type` | `path` |
|---|---|---|
| `aiws_wiki_meta_strategy_coordinator` | `coordinator` | `agents/blueprints/aiws_wiki_meta_strategy_coordinator/` |
| `aiws_pm_agent` | `project_management` | `agents/blueprints/aiws_pm_agent/` |
| `aiws_detailed_design_review_agent` | `review` | `agents/blueprints/aiws_detailed_design_review_agent/` |
| `aiws_testcase_review_agent` | `review` | `agents/blueprints/aiws_testcase_review_agent/` |

`/aiws-agent-create blueprint=<id>` (Mode A) looks an id up here; if absent it offers AI-assisted
selection (Mode B) or custom no-blueprint (Mode C). To add your own blueprint later, see
`agent_authoring_guide.md`. **Verify** each `path:` directory exists and holds a `blueprint.yaml`
after copying (this is also smoke-test step A in `smoke_test_checklist.md`).

### 4a. Namespace `aiws_` — ATDB do AIWS ship vs blueprint của dự án (CR-AIWS-2026-08-017)

Mọi ATDB **do AIWS ship** mang tiền tố `aiws_` trong `blueprint_id` **và** tên thư mục, kèm hai trường
trong `blueprint.yaml`:

```yaml
blueprint_id: aiws_pm_agent
previous_ids: [pm_agent]   # alias — desk pin id trước rename vẫn resolve
origin: aiws               # marker máy-đọc: ai ship ATDB này
```

Luật vận hành:
- **`aiws_*` / `origin: aiws`** = tài sản của pack ⇒ upgrade pack được phép reconcile/ghi đè.
- **Không tiền tố** = blueprint của dự án ⇒ upgrade **KHÔNG đụng**. Đặt tên blueprint riêng, đừng mượn
  tiền tố `aiws_` (mất đúng lớp bảo vệ này).
- **Desk (task desk) KHÔNG mang tiền tố** — desk thuộc về dự án. `/aiws-agent create` tự **strip** tiền tố
  khi gợi ý `instance_id`: ATDB `aiws_pm_agent` ⇒ desk `pm_agent`.
- Desk cũ pin id trước rename **vẫn chạy** nhờ `previous_ids` (resolver dual-read trong `run_agent.py` +
  `lint_agents.py`) — không cần sửa gấp, nhưng nên cập nhật pin khi tiện.

## 5. Point a task desk's `context/` at your project Knowledge Hub

A **task desk** (formerly *agent instance*) is the real tracked runtime unit — it binds a blueprint to one project's context,
memory, and workspace. Create one with `/aiws-agent-create` (see `command_usage_guide.md`), which
generates the desk folder skeleton, or wire an existing sample task desk. The Knowledge Hub wiring
lives in the desk's `context/` directory (Detailed Design v0.2 §7), **not** in the blueprint:

- `context/wiki_references.yaml` — set `wiki_index:` to your project's Wiki Source Index path (the
  sample uses `.ai-work/wiki_sources/index.jsonl`) and list `recommended_entries:` to read first.
  Carries `usage_rule: wiki_first_not_wiki_only` and the `source_verification_required_when:` triggers.
- `context/source_references.yaml` — source dirs that back findings (requirements, basic design,
  API/DB/screen specs, detailed design, `src/`).
- `context/source_priority.yaml` — Wiki-first ordering + when source verification is required.
- `context/working_inventory.yaml` — specific **non-wiki / not-yet-indexed** files this desk
  needs. **Desk-owned**: a blueprint update must never overwrite it (FR-AI-05). Ships empty `[]`.
- `context/ignored_paths.yaml` — paths to skip.

The desk also carries `scope:` in `desk.yaml` (`target_document_areas`, `target_source_areas`,
`ignored_paths`). When a run starts, `run_agent.py` reads these `context/` files (plus the blueprint
and confirmed memory) to materialize the Active Run Context — so wiring `context/` correctly is what
"points the agent at your project".

> **Wiki-first, NOT Wiki-only.** Task Desks ground in the Wiki/index first, then **verify important
> findings against source** and report conflicts rather than treat the Wiki as the sole authority.

## 6. Verify the install (smoke)

Run the smoke checklist (`smoke_test_checklist.md`): registry resolves the 3 blueprints (A); create
a task desk from a blueprint (B, `create ≠ run`, empty-skeleton memory); start a review run on MOCK
input (C); start a PM run (D); feedback emits a candidate not auto-confirmed (E); review-learning
surfaces it without auto-confirm (F); guardrail checks (G). A green smoke run confirms the install.
Thêm (dispatch wave 2026-08-14): `py tooling/lint_agents.py` chạy sạch — gồm 4 rule mới
`shim_desk_binding_drift` / `executors_allowed_offvocab` / `tiers_supported_invalid` /
`provider_profile_invalid` (CR-AIWS-2026-08-044/045) không nổ trên tree hợp lệ.

## 7. Related guides

- `user_guide.md` — run the agents day to day.
- `command_usage_guide.md` — the command groups (Core runtime · Desk lifecycle · Convenience router) in detail.
- `agent_authoring_guide.md` — author a new blueprint/desk.
- `known_limitations_and_backlog.md` — what's deferred (D/E/F/G/H + full cross-pack E2E → J-2).
- `promotion_readiness_note.md` — what a future CR must cover to promote staging → canonical.
