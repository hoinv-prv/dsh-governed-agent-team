# AI Agents Pack

> **Status:** CANONICAL (promoted to `product/agents/` via CR-AIWS-2026-06-055, applied 2026-06-24 by AIP-EXEC-165; banner corrected by CR-AIWS-2026-07-012). File-first, client-side, HUMAN-gated. Installs to a target project's `.ai-work/agents/` (single-track). `development/` tree đã RETIRED + DELETED (CR-AIWS-2026-08-039, PO ruling 2026-08-14; git history = provenance); literal `development/ai_agents/` mentions below là provenance lịch sử.
> **Built by:** AIP-EXEC-107 (Phase A of program AIP-PLAN-002).
> **Source baseline:** `docs/agent_pack_impl_package/`.
> **Pack version:** see `PACK_VERSION.md` — 0.9 (beta), pack-level single bump point.

This folder is the **canonical build** of the **AIWS Wiki Meta Build & Consume Agent Pack** — the
**Agent Blueprint → Agent Task Desk** model. It is built here (not in `product/` or `.ai-work/`)
exactly like the earlier `development/ai_assisstant/` feature: iterate + dogfood first, then
promote to canonical via a Change Request (đã xảy ra — CR-AIWS-2026-06-055; `development/` đã retired + deleted — CR-AIWS-2026-08-039; mọi cập nhật trực tiếp trong `product/agents/`, CR-gated).

## Governance

- `development/` đã RETIRED + DELETED (CR-AIWS-2026-08-039) — mọi thay đổi pack thực hiện trực tiếp trong `product/agents/` và đều **CR-gated** (không còn chế độ dev-no-CR).
- **Promotion into `product/` HAS HAPPENED** (CR-AIWS-2026-06-055, 2026-06-24): this copy IS the
  canonical build. Every change to `product/agents/**` is now **CR-gated** (CLAUDE.md rule #8 /
  SOP_MASTER §4.1); changes apply 2-tree (product ↔ `.ai-work/agents/` byte-identical). *(3-tree → 2-tree sau
  retire dev — CR-AIWS-2026-08-039; wording trước đó CR-AIWS-2026-07-012.)*
- **Single-track install (CR-AIWS-2026-06-055/049; supersedes the two-track AP-CR-29 / AP-DDR-17):** the pack
  installs to a target project's **`.ai-work/agents/`** whether trialed or matured — there is no `.aiws-staging/`.
  Maturity is managed by **git branch** in the AIWS source repo; promotion `development/`→`product/` (CR-gated)
  graduates the pack into the canonical build, not a change of target dir.
- **No silent promotion** at any layer: generated metadata → Wiki, Wiki candidate → Official Wiki,
  learning candidate → confirmed memory, candidate tool → active tool, desk lesson → Blueprint —
  every step requires HUMAN approval.
- Coordinator agents are **planning-only** (plan / task-card / integration-summary). They do **not**
  auto-run other agents. HUMAN invokes each agent explicitly; collaboration is via manual handoff
  artifacts (Shared Task Workspace is Post-MVP, not built).

## Dispatch model (wave 2026-08-14 — CR-AIWS-2026-08-043..046)

**Activation default-off:** giao việc cho agent/desk là OPTIONAL — AIP step không khai `Assigned Agent:`
→ main session thực thi AIWS thuần (không run/desk). Khi chỉ định: **agent handle == desk_id** (desk =
toolkit + state anchor, không phải bên nhận việc); **executor** chọn per-assignment plan-time
(`Executor:` step field / `--executor`, validate `executors_allowed`); **execution tier** resolve
{model, effort} qua `agents/execution_tiers.yaml` (`--tier`, cheapest-capable); **multi-step span**
(`extend` + named continuation — KHÔNG fork) cho chuỗi step liên tiếp cùng desk; **project toggle**
`pack_config.yaml dispatch_enabled` (vắng = ON). Authority đầy đủ: `docs/agent_runtime_design.md`
§8E–§8F; hướng dẫn dùng: `product/guidelines/AGENT_USAGE_GUIDE.md` + `docs/rollout/user_guide.md`.

## Layout (OQ-1 resolved — AIP-EXEC-107 STEP-00, 2026-06-18)

```
<pack root>/                      <- product/agents/ (canonical) · .ai-work/agents/ (installed)
  README.md                       <- this file
  agents/
    blueprint_registry.yaml       <- index of available Blueprints
    blueprints/<blueprint_id>/    <- reusable agent definitions (no project-specific memory)
    execution_tiers.yaml          <- execution-tier registry (CR-AIWS-2026-08-045): tier trừu tượng + provider profile {model, effort}; MVP: claude
    task_desks/<desk_id>/         <- named, tracked agent task desks (P2 rename 2026-08-05; tools dual-read instances/)
  wiki_meta/                      <- GENERATED metadata (inventories/relations/meta_reviews/tool_outputs)
  wiki_candidates/                <- candidate_packs / patch_proposals / review_packs (pre-approval)
  tools/                          <- project/ + common/ tools (candidate tools live agent-local first)
```

**Install/promotion mapping — single-track by maturity (CR-AIWS-2026-06-055/049; supersedes two-track AP-CR-29 / AP-DDR-17):**
- **One target** — the pack installs to the project's **`.ai-work/agents/`** whether incubating (trial) or matured (`.../agents/` → `.ai-work/agents/`, `.../wiki_meta/` → `.ai-work/agents/wiki_meta/`, …). There is no `.aiws-staging/`.
- **Maturity = git branch** in the AIWS source repo (HUMAN-managed). Promotion `development/`→`product/` (CR-gated, CLAUDE.md #8 / SOP_MASTER §4.1) graduates the pack into the canonical `product/`→`.ai-work/agents/` build; it does **not** change the target dir.

All internal cross-references are **relative**, so the install rebase is mechanical. The pack is promoted into `product/agents/` and ships via a dedicated builder PAYLOAD_SECTION → **`CR-AIWS-2026-06-055`** (with CR-049 install-model + CR-051 `.claude` wiring; AIWS-Product-Owner approved 2026-06-23).

> **`instances/` are EXCLUDED from the install** (AP-CR-24). Task Desks are **created on the target**
> via `/aiws-agent-create`, **not shipped** — the ship-set is blueprints + registry + templates + commands +
> tooling only. The install target gets task desks created at runtime under `.ai-work/agents/agents/task_desks/`
> (a write location only); the `*__sample_project` task desks stay here as dev/test fixtures. See the
> PROMOTION-EXCLUDES invariant in `docs/rollout/promotion_readiness_note.md` §3(1).

**Folder separation is a guardrail** — `wiki_meta/` (generated, not Wiki) ≠ `wiki_candidates/`
(reviewable candidates/patches) ≠ Official Wiki (only after HUMAN approval).

## Phase status (program AIP-PLAN-002)

| Phase | Scope | This folder |
|---|---|---|
| **A** (AIP-EXEC-107) | Foundation: skeleton + schemas + 1 sample blueprint + 1 sample task desk | ✅ built |
| **B** (AIP-EXEC-108) | Create-Agent-Task-Desk command (3 modes incl. custom no-blueprint + `agent_design_snapshot.yaml`) | ✅ built |
| **C** (AIP-EXEC-109) | Desk Workspace + run/learning/confirmed-memory loop | ✅ built |
| **Priority workstream** (AIP-EXEC-139) | 3 priority agents mapped from v0.1 templates: `detailed_design_review_agent`, `testcase_review_agent`, `pm_agent` — incl. `_shared/review/` assets, registry +3, 3 sample task desks, 3 MOCK sample runs | ✅ built (2026-06-21) |
| **Runtime Command Set** (AIP-EXEC-142) | `/aiws-agent-run` (start/resume/status/stop) + `/aiws-agent-feedback` + tooling `run_agent.py` (stdlib, thin) + Active Run Context (`00_active_run_context.md`) + additive `run_state.yaml`; dogfood MOCK on `detailed_design_review_agent` | ✅ built (2026-06-21) |
| D · E · F · G | Coordinators → metadata sub-agents → tooling → wiki lifecycle | pending |
| **H** Wiki Consumer agents | **re-scoped OUT of EXEC-139 (2026-06-21)** → separate AIP, not yet created | pending |
| **I** (AIP-EXEC-140) | Assistant (DDR) **absorbed** into `detailed_design_review_agent` (additive `memory_load_policy` graft) + `development/ai_assisstant/` **retired** (archived to `.ai-work/history/archive/`) | ✅ done (2026-06-21) |
| **J-1** (AIP-EXEC-141) | Scoped E2E (review+PM) + FULL packaging for current agents: `docs/rollout/` (setup/user/command/authoring guides + smoke + known-limitations + promotion-readiness) + `sample_project_package/` | ✅ done (2026-06-21) |
| J-2 | Full cross-pack E2E (build/refresh/consume) + remaining agents (D/E/F/G/H) | pending (deferred — needs create-wiki pipeline) |

> The `memory/` and `training/` files inside the sample task desks are intentionally **empty skeletons**
> (header + `_(none yet)_`) — confirmed learning is created only via the Phase-C run/learning loop with
> HUMAN approval (no fabricated/seeded learning). The Phase-C demo populated the coordinator sample only;
> the 3 priority-agent task desks ship with empty memory by design.
