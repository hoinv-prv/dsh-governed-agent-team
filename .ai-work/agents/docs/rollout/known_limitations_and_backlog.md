# Known Limitations + Post-MVP Backlog — AI Agents Pack (Phase J-1)

> **Status: CANONICAL (beta) — AI Agents Pack, version: see `PACK_VERSION.md` (pack root).** Promoted by CR-AIWS-2026-06-055 (2026-06-24); status formalized by CR-AIWS-2026-08-036. Built by AIP-EXEC-141 (Phase J-1) STEP-06.
>
> **READ THIS FIRST — the pack is NOT complete.** Phase J-1 packaged only the **currently-built
> agents**: the 3 priority agents (`aiws_detailed_design_review_agent`, `aiws_testcase_review_agent`, `aiws_pm_agent`)
> plus the A/B/C foundation (Blueprint/Task-Desk model, `/aiws-agent-create`, desk workspace +
> run/learning loop) and the runtime command set (EXEC-142). The validation done in J-1 is a **scoped
> E2E (review + PM only) over MOCK fixtures** — see `e2e_simulation_result.md`. The full cross-pack
> pipeline (build / refresh / consume) and program phases **D, E, F, G, H** are **NOT built** and are
> **DEFERRED to round J-2** (see §3). Do not read this pack as a finished product.

---

## 1. Scope of this document

This doc states (1) the **current limitations** of the built pack as it stands at the end of J-1, and
(2) the **explicit deferred backlog** — what is *not* built, mapped to its program phase and the reason
it is deferred. It is the primary anchor for **R-3 (deferred scope must be explicit)** of EXEC-141: a
reader must not be able to mistake the pack as complete.

Status legend (mirrors AIP-PLAN-005 — backlog carrier nội bộ AIWS (tracking dashboard cũ đã retired vào git history; deferred scope authoritative = §3 doc này + AIP-PLAN-005)): ✅ built · ⬜ pending/deferred · ⚠️ caveat.

---

## 2. Current limitations of the built pack

These are properties of what **is** built (A/B/C + 3 priority agents + runtime command set). They are
mostly **by-design MVP guardrails**, not defects — but a reader must know them before relying on the pack.

| # | Limitation | Detail | By design? |
|---|---|---|---|
| L-1 | **MOCK-only validation** | The scoped E2E and the sample-project package exercise the agents over **reused MOCK fixtures** (EXEC-139 mock detailed-design / test-case / requirements), not real project documents. The pack proves the *mechanism*, not review quality on real artifacts. Every produced artifact is marked MOCK. | Yes (MVP scope) |
| L-2 | **No real CLI / engine** | `tooling/run_agent.py` is a **thin orchestrator** (stdlib): it scaffolds a run-folder, materializes the Active Run Context (ARC), and reconciles `run_state.yaml` status. It does **not** call an LLM or "execute" the agent. The AI (operator session) reads the ARC and **acts as the agent** by hand. There is no autonomous **external** engine. (CR-AIWS-2026-07-062 ruling: an **in-session** sub-agent dispatched by the operator session per an `active` AIP is NOT this engine and IS in scope — see `agent_runtime_design.md §8D`; a real external CLI/executor stays Post-MVP + CR-019 default-REJECT.) | Yes (command-spec-first, external CLI/engine = Post-MVP) |
| L-3 | **No Shared Task Workspace** | Cross-agent collaboration uses **manual handoff artifacts** (operator copies an upstream `output/` into a downstream `input/`). There is no shared workspace where agents co-write. Shared Task Workspace is **Post-MVP** (scope-locked out at Phase A). | Yes (Post-MVP) |
| L-4 | **Manual HUMAN handoff (no auto-chain)** | The coordinator does **not** auto-run other agents; each leg of a chain is HUMAN/operator-invoked and handoff is a manual file copy (see `e2e_simulation_result.md` §3, and `issue_warning_list.md` W-03). There is no helper to copy artifacts between legs. | Yes (guardrail — no auto-dispatch) |
| L-5 | **Review = mechanism-demo, not graded review** | The review agents demonstrate the *review flow* (Wiki-first-not-Wiki-only + source verification + findings + learning candidate) on MOCK input. Findings counts are illustrative of the mechanism; this is **not** a quality benchmark of review accuracy on real docs. | Yes (MVP) |
| L-6 | **Single-shot run model; resume is HUMAN-driven** | `/aiws-agent-run` uses a single-shot happy path. `resume` / `stop` exist and were dogfooded (EXEC-142), but resumption is **HUMAN-driven** off the run-record `status` + progress markers — there is no automatic retry/continuation. | Yes (DDR-10 run model) |
| L-7 | **Empty-skeleton memory** | The 3 priority-agent task desks ship with **empty** `memory/`+`training/` (`confirmed_memory.jsonl` = 0 bytes). Confirmed memory is created **only** via the run → learning-candidate → HUMAN-confirm loop. No seeded/fabricated learning. Agents start "cold". | Yes (no-fabricated-seed rule) |
| L-8 | **RESOLVED — canonical + installed** | Pack canonical tại `product/agents/` (CR-AIWS-2026-06-055, 2026-06-24) và install vào `.ai-work/agents/` (single-track). Dev tree `development/ai_agents/` đã retired + deleted (CR-AIWS-2026-08-039; git history = provenance). Mọi thay đổi pack = CR-gated (rule #8). | Resolved 2026-06-24; banner formalized CR-AIWS-2026-08-036 |
| L-9 | **Minor ergonomics observations** | Template placeholder rows must be overwritten (`issue_warning_list.md` W-01); `run_state.yaml notes` capped at 120 chars (W-02). Documented, not fixed (out of J-1 scope). | Yes (logged) |
| L-10 | **Harness shim-registration lag** | Sinh `.claude/agents/<desk_id>.md` (build_agent_shims) **không** làm agent type dispatch được ngay: harness đăng ký agent type theo lịch riêng (thường là ranh giới session), AIWS không kiểm soát. Đo 2026-08-06: shim sinh giữa phiên không được nhận trong phiên đó (AIP-EXEC-1002 BLOCKED); shim sinh phiên trước dispatch bình thường. Quy tắc vận hành: dogfood/enablement gate phải chạy ở phiên mà agent type ĐÃ xuất hiện; không dispatch được vì thiếu registration ⇒ verdict **BLOCKED** (không phải FAIL), KHÔNG cấp capability, revert enablement chờ phiên sau. | **No — environment** (không phải defect của pack; pack chỉ có thể tài liệu hoá + thiết kế gate chịu được lag) |
| L-11 | **Tier áp spawn chỉ đường `claude_subagent`** | Execution tier (CR-AIWS-2026-08-045) resolve {model, effort} cho spawn sub-agent; đường `main_session` chỉ stamp tier vào ledger (model/effort của phiên chính không đổi được giữa task — cache key, AGENT_USAGE_GUIDE §5.3.6). | Yes (giới hạn harness, tài liệu hoá tại `agent_runtime_design.md` §8E) |
| L-12 | **Kinh tế span CHƯA đo** | Multi-step span (CR-AIWS-2026-08-046) dogfood PASS về CƠ CHẾ (continuation giữ context — mock-scale 2 leg, AIP-EXEC-1044); số đo token savings thật (sàn ~16k + desk digest amortized qua các step) chưa có — xem backlog §3.3. | Yes (đo là backlog, cơ chế đã ship) |

> **None of these were blocking defects in the scoped E2E** — the chain ran clean (`issue_warning_list.md`).
> They bound *what the pack can be trusted to do today*.

---

## 3. DEFERRED backlog — round J-2 (EXPLICIT)

The following are **NOT built** and are **deferred to round J-2**. Each item is mapped to its **program
phase** (AIP-PLAN-005 — backlog carrier nội bộ AIWS (tracking dashboard cũ đã retired vào git history; deferred scope authoritative = §3 doc này + AIP-PLAN-005) §2) and the **reason** it is deferred. The dominant reason
across D/E/F/G + the full E2E is the same: they need the **create-wiki pipeline** (generated wiki-meta +
the wiki-consumer agents), which is not built, so they cannot run on real generated metadata yet.

### 3.1 Remaining program phases (all ⬜ pending — no AIP created yet)

| Phase | Name | What it adds | Deferred because | AIP |
|---|---|---|---|---|
| **D** | **Coordinator Agents** (planning-only) | Strategy + planning coordinators that produce a meta-build plan / task-cards / `human_decision_points` / `integration_summary` (no auto-run). Groups into the "create-wiki" cluster (it plans/orchestrates meta-build). | The coordinator plans the **create-wiki** meta-build flow; without the metadata sub-agents (E) and wiki-lifecycle agents (G) there is nothing for it to coordinate end-to-end. | ⬜ not created |
| **E** | **Metadata Sub-agents** (structure / document / source-code → DB / API / relation → meta-quality) | The agents that **generate wiki-meta** (inventories + relations + meta-quality review) from project sources. | **This is the create-wiki pipeline itself.** It does not exist yet, so no real generated metadata exists to build a wiki from or to consume. This is the root dependency that blocks the full E2E. | ⬜ not created |
| **F** | **Metadata Tooling Agent + tool lifecycle** | Helper scripts (`extract_folder_tree.py`, `extract_markdown_sections.py`, …) + the agent-local → project-candidate → HUMAN-tested-active → common tool lifecycle (no auto-activate). | Tooling exists to **support** metadata generation (E). Without E it has no consumer; tool promotion is also HUMAN-gated and out of build scope. Can run in parallel with G once E core lands. | ⬜ not created |
| **G** | **Wiki Lifecycle Agents** (candidate / refresh / review / apply) | Build wiki **candidate packs**, refresh **patch proposals**, review packs, and apply-support (all HUMAN-approved before apply). | Turns **generated metadata (E)** into wiki candidates. With no generated metadata there is nothing to package into a candidate, refresh, or review. | ⬜ not created |
| **H** | **Wiki Consumer Agents** (AIP-plan / task-context / output-review) | `aip_planning_agent` / `task_context_preparation_agent` / `wiki_grounded_output_review_agent` — consume the Knowledge Hub for planning / context / output review. (Re-scoped OUT of EXEC-139 on 2026-06-21 → separate AIP.) | These can run on the **existing** Knowledge Hub + mock today, but the **full** consume scenario (consuming *generated* wiki-meta) needs E/G first. The agents themselves are still unbuilt and need their own AIP. | ⬜ not created (own AIP) |

> Phases A, B, C are ✅ built; the **priority workstream** (EXEC-139), **runtime command set** (EXEC-142),
> and **Phase I** (assistant merge/retire, EXEC-140) are ✅ done. Phase J is **in progress at J-1** (this
> round). See AIP-PLAN-005 — backlog carrier nội bộ AIWS (tracking dashboard cũ đã retired vào git history; deferred scope authoritative = §3 doc này + AIP-PLAN-005) §2 dashboard for the authoritative status.

### 3.2 Full cross-pack E2E (the 3 real scenarios) — DEFERRED to J-2

The J-1 scoped E2E exercised **review + PM only** over the existing Knowledge Hub + MOCK fixtures. The
**full** cross-pack E2E (the 3 scenarios from Impl-Plan Sprint 11) is **NOT** done:

| Scenario | What it would prove | Deferred because |
|---|---|---|
| **1 — Build** | Generate wiki-meta from project sources → candidate pack → review pack (coordinator no auto-run; explicit HUMAN handoff). | Needs the **metadata sub-agents (E)** + **wiki-lifecycle agents (G)** + **coordinator (D)** — none built. No generated wiki-meta exists. |
| **2 — Refresh** | Source change → patch proposal → refresh-impact / stale report → review pack (no auto-promote). | Needs **G** (refresh analysis) operating on **E**'s generated metadata — neither built. |
| **3 — Consume (FULL)** | Consume the **generated** wiki-meta for AIP-plan / task-context / output-review (run evidence stored; learning not auto-confirmed). | J-1 covered only the **review + PM slice over the *existing* Hub + mock**. The full consume of *generated* metadata needs **E/G** output + the **wiki-consumer agents (H)** — none built. |

> **Marker (R-1):** the J-1 E2E is a **subset** of Scenario 3 (review + PM over the existing Hub + MOCK).
> Scenarios 1, 2, and the generated-metadata part of 3 are **J-2**.

### 3.3 Remaining agents + other deferred items

- **Remaining agents** beyond the 3 priority agents + the 1 sample coordinator: the full coordinator set
  (D), all metadata sub-agents (E), the tooling agent (F), all wiki-lifecycle agents (G), and all
  wiki-consumer agents (H). → **J-2** (each needs its own AIP).
- **Real-document validation** (replace MOCK fixtures with real project docs once a pilot project + real
  generated metadata exist). → **J-2 / Post-MVP** (depends on E).
- **Đo kinh tế span + tier trên task thật** (nguồn: Apply Outcome CR-AIWS-2026-08-046 + L-12): đo token
  savings của multi-step span (sàn ~16k + desk digest amortized, TTL gap thực) và hiệu quả chi phí của
  tier routing (cheapest-capable) trên một AIP thật — kỷ luật đo theo AGENT_USAGE_GUIDE §5.5
  (pre-registration, đơn vị khai trước). → **J-2**.
- **Promotion to canonical** (`product/` / `.ai-work/`) is **out of scope of both J-1 and J-2** — it is a
  separate **future CR** (AP-CR-10). J-1 only prepares the `promotion_readiness_note.md`.
- **Post-MVP (scope-locked, not J-2):** real CLI / autonomous EXTERNAL engine (L-2; in-session sub-agent dispatch is in scope per CR-AIWS-2026-07-062), Shared Task Workspace (L-3),
  an auto-handoff convenience helper (`issue_warning_list.md` W-03) — these stay prohibited/Post-MVP, **not**
  pulled into J-2 unless re-scoped.

---

## 4. Bottom line

- **Built + validated (mechanism, MOCK):** Blueprint/Task-Desk foundation (A/B/C), 3 priority agents
  (review + PM), runtime command set (`/aiws-agent-create`, `/aiws-agent-run`, `/aiws-agent-feedback`,
  `/aiws-agent-review-learning`), assistant merge (I).
- **NOT built (J-2):** create-wiki pipeline (D coordinator, E metadata, F tooling, G wiki-lifecycle),
  wiki-consumer agents (H), full cross-pack E2E (build / refresh / consume on generated metadata),
  remaining agents, real-document validation.
- **Out of scope of J-1 and J-2:** promotion to `product/`/`.ai-work/` — future CR
  (`promotion_readiness_note.md`).

**The pack is a validated foundation + a review/PM slice — it is not the full AIWS Wiki Meta Build &
Consume Agent Pack yet.**

> **Wave CR-AIWS-2026-07-012..018 update (2026-07-07):** L-6 amended — the run model gains an OPTIONAL
> two-phase form (`plan_first`: plan → HUMAN confirm-plan → execute, CR-016) while staying single-shot
> per phase with HUMAN-driven resume; L-3/L-4 amended — AIP-driven multi-agent collaboration is now
> formalized via shared Task Workspace + `assigned_agent` + per-run namespacing (CR-018); manual
> handoff remains for standalone chains. L-5 answered by the review mechanism upgrade (CR-012).
