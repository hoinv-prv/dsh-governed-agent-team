# Promotion-Readiness Note — AI Agents Pack (current agents) (Phase J-1)

> **Status: HISTORICAL — point-in-time record, kept for provenance (formalized by CR-AIWS-2026-08-036).** Không phản ánh trạng thái hiện tại — xem `PACK_VERSION.md` + `docs/rollout/known_limitations_and_backlog.md`. Built by AIP-EXEC-141 (Phase J-1) STEP-07. Checklist §3 của note này đã được thực thi bởi CR-AIWS-2026-06-055 (promotion) + CR-AIWS-2026-08-036 (formalize).
>
> **PROMOTION-READINESS ≠ PROMOTION.** This note only **PREPARES** a future Change Request to promote the
> currently-built agents from staging `development/ai_agents/` into canonical `product/` and/or `.ai-work/`
> runtime. **Promotion itself is OUT of scope** (AP-CR-10 / EXEC-141 R-5). This document:
> - does **NOT** write anything to `product/` or `.ai-work/`;
> - does **NOT** create a CR file (no `product/change_requests/` entry);
> - does **NOT** apply any path rebase, lint, or approval.
>
> It is a checklist of what a **FUTURE CR** must cover so that, when a HUMAN decides to promote, the work
> is mechanical and governed.

---

## 1. Why a CR is required (no silent promotion)

Promotion of staging content into canonical (`product/` and/or `.ai-work/` runtime) is **CR-gated** by
project rule (CLAUDE.md rule #8 / `../../../../.ai-work/truth/SOP_MASTER.md` §4.1) and by
`Controlled_Knowledge_Promotion_Spec_MVP` (`../../../../product/methodology/ai_work_system/20_specs/Controlled_Knowledge_Promotion_Spec_MVP.md`)
— candidate → review → apply, **No Auto-Promotion** (spec §10). AIWS may prepare candidates and draft the
request; it may **not** apply. Building inside `development/ai_agents/` needs no CR (it is non-canonical
staging), but **moving it to canonical does**. This note is the candidate/preparation artifact, not the
approval.

---

## 2. Scope a future promotion CR MUST declare

The CR's scope is **current agents only** — exactly what J-1 packaged and validated:

**IN scope for the promotion CR:**
- Foundation A/B/C: Blueprint/Instance model, `/aiws-agent-create`, instance workspace + run/learning loop.
- The 3 priority agents: `aiws_detailed_design_review_agent`, `aiws_testcase_review_agent`, `aiws_pm_agent` (+ the
  `_shared/review/` assets they reuse).
- Runtime command set (EXEC-142): `/aiws-agent-run` (start/resume/status/stop), `/aiws-agent-feedback`,
  `tooling/run_agent.py`, the Active Run Context, and the additive `run_state.yaml`.
- Phase I result: the `aiws_detailed_design_review_agent` absorbed DDR graft (EXEC-140).
- The rollout/packaging docs under `docs/rollout/` (setup / user / command / authoring / smoke + sample
  package / this note / known-limitations), rebased as appropriate.

**OUT of scope for the promotion CR (DEFER — `known_limitations_and_backlog.md`):**
- Program phases **D / E / F / G / H** (coordinator, metadata sub-agents, tooling, wiki-lifecycle,
  wiki-consumer agents) — not built.
- The **full cross-pack E2E** (build / refresh / consume on generated metadata).
- Any remaining agents and real-document validation.

> Rationale: only promote what is built **and** validated. The deferred items get their own build round
> (J-2) and, later, their own promotion CR(s).

---

## 3. What the future CR MUST cover (readiness checklist)

A promotion CR for the current agents must address each of the following. Each is **prepared** here, not done.

### (1) Path rebase `development/ai_agents/` → `.ai-work/agents/` (and `product/` for canonical docs)
- **Single-track install (CR-AIWS-2026-06-055/049; supersedes two-track AP-CR-29 / AP-DDR-17).** The pack has
  **one** install target: it installs to a target project's **`.ai-work/agents/`** whether incubating (trial)
  or matured. Maturity is managed by **git branch** in the AIWS source repo; CR-gated promotion
  `development/`→`product/` graduates it into the canonical `product/`→`.ai-work/agents/` build (the rebase
  below) — it does not change the target dir. There is no `.aiws-staging/`. The install-model + tooling are
  canonical → **`CR-AIWS-2026-06-055`** (+ CR-049/051; AIWS-Product-Owner approved 2026-06-23). The
  PROMOTION-EXCLUDES invariant (below) still applies.
- The staging tree maps to runtime per `../../README.md` ("Install/promotion mapping"): `development/ai_agents/` →
  `.ai-work/` (`…/agents/` → `.ai-work/agents/`, `…/wiki_meta/` → `.ai-work/wiki_meta/`, …). Design-doc /
  spec material (if any is promoted) targets `product/` per DD/Impl-Plan path convention (AP-CR-12).
- **All internal cross-references in the pack are relative**, so the rebase is **mechanical** (move tree +
  adjust the wrapper prefix; relative links between pack files survive). The CR must (a) confirm no absolute
  staging paths leaked into the promoted set, and (b) re-point any references that pointed *up* out of the
  pack (e.g. `../../../product/...`, `../../../.ai-work/truth/...`) to their post-promotion locations.
- Decide the **target split**: agent definitions/commands/tooling → `.ai-work/agents/` (runtime);
  any methodology/spec text intended as canonical → `product/`. (Per AP-CR-12, runtime tree creation at
  `.ai-work/agents/` is itself a canonical touch — drafted as CR-AIWS-2026-06-042 C2 — and must be
  reconciled with this promotion CR.)

- **PROMOTION-EXCLUDES invariant (acceptance criterion, AP-CR-24).** The promotion mapping rebases
  **only** `agents/{blueprint_registry.yaml, blueprints/, templates/}` + `commands/` + `tooling/run_agent.py`
  into `.ai-work/agents/`, and **EXCLUDES** (glob):
  - `agents/task_desks/**` — instances are **created on the target** via `/aiws-agent-create`, never shipped;
  - `**/__sample_project/**` — the dev/test fixtures;
  - `**/workspace/**` — per-run workspaces (active/completed runs, step outputs, handoff artifacts);
  - runtime `*.jsonl` — memory / run / candidate files (e.g. `confirmed_memory.jsonl`,
    `learning_candidates.jsonl`, `run_log.jsonl`, `candidate_queue.jsonl`, `feedback_log.jsonl`).

  Promotion creates an **empty** `.ai-work/agents/task_desks/.gitkeep` on the target (a write location only).
  This is a **checkable one-line rule, not a hand-maintained list**: any path component with the suffix
  `__sample_project` is **never-ship**, and the only `instances/` artifact that crosses is the empty
  `.gitkeep`. The promotion CR's acceptance check is: confirm the promoted set contains **no** instance
  directory, **no** `*__sample_project` path, **no** `workspace/`, and **no** runtime `*.jsonl`.

  - **Instance lifecycle artifacts (AP-CR-27/28, AIP-EXEC-146) are already covered.** The new per-instance
    artifacts — `.atdb_snapshot/`, `blueprint_ref.yaml` `reconcile_log`, and the clone lineage
    (`cloned_from`/`cloned_at`/`clone_why`) + `clone_review` memory markers — all live **under
    `agents/task_desks/<id>/`**, so the existing `agents/task_desks/**` exclusion keeps them never-ship; no
    new glob is needed. What **does** ship (correctly): the new command specs
    `commands/aiws-agent-upgrade.md` + `commands/aiws-agent-clone.md`, the new `agents/templates/`
    (`upgrade_reconcile_template.md`, `clone_review_checklist.md`), and the `run_agent.py` `upgrade`/`clone`
    subcommands — the tooling surface, not instance state.
  - **Instance rename artifacts (AP-CR-30, AIP-EXEC-147) are already covered.** The rename alias
    `previous_ids` lives in `instances/<id>/desk.yaml`, so the existing `agents/task_desks/**` exclusion
    keeps it never-ship; no new glob is needed. What **does** ship (correctly): the new command spec
    `commands/aiws-agent-rename.md` and the `run_agent.py` `rename` subcommand (+ alias-aware resolver) —
    the tooling surface, not instance state.
  - **Ownership invariant + reconcile prompts (AP-CR-27).** The future promotion CR (and the
    `aiws-pkg upgrade` flow) MUST honor the **3-layer ownership invariant (FR-AI-09)**: a Blueprint
    update propagated by an AIWS package upgrade must **never** overwrite an instance's override/learned
    layers. After a package upgrade, list instances behind the new Blueprint version and prompt the HUMAN to
    run `/aiws-agent-upgrade` per instance (HUMAN-gated, present-don't-auto-apply). This `aiws-pkg upgrade`
    integration is ⚠ **canonical-touch DEFERRED** to that CR.

### (2) Dual-tree apply discipline (if applicable)
- Project rule: imported/runtime improvements that exist both in `.ai-work/` (live) and `product/`
  (canonical source) must be applied to **both trees** (memory: tooling/skill edit flow). The CR must state
  whether the promoted agents have a `product/` canonical home in addition to the `.ai-work/agents/` runtime
  home, and if so, apply to both and keep them in sync. If the pack lives **only** in `.ai-work/agents/`
  runtime (no `product/` mirror), the CR must say so explicitly so the dual-tree rule is consciously
  N/A rather than silently skipped.

### (3) Lint clean before apply
- The CR must run and pass: `lint_aip` (the promotion AIP itself) + **workspace** lint + **wiki** lint
  (via `/aiws-lint`). Promotion that touches runtime knowledge surfaces must lint clean (0 errors) before
  apply, consistent with how every AIP is finalized.

### (4) AIWS-Product-Owner approval
- Canonical change requires **AIWS-Product-Owner** approval (CLAUDE.md rule #8 / SOP_MASTER §4.1):
  draft CR → `product/change_requests/` → AIWS-Product-Owner approves → only then apply. (Wiki-meta changes,
  if any are bundled, additionally route to Wiki-Manager.) AI does **not** self-approve, even with complete
  information. The CR must carry the mandatory CR fields and a logged decision/rollback trace
  (Controlled-Knowledge-Promotion spec §17).

### (5) CR scope = current agents only (defer D/E/F/G/H + full E2E)
- Restate §2: the CR promotes **only** the built + validated current agents; it explicitly **does not**
  promote the deferred phases or the full E2E. This keeps the canonical surface honest — it must not imply
  the pack is complete (the promoted `known_limitations_and_backlog.md` carries the deferred list forward).

---

## 4. Readiness signals already in place (from J-1)

These reduce the future CR's effort — they are facts about the current staging build, not approvals:

- **Relative cross-refs everywhere** → path rebase is mechanical (OQ-1 resolved at Phase A; `../../README.md`).
- **Scoped + MOCK markers** on every E2E/packaging artifact → the canonical surface inherits an honest
  "not complete" framing (R-1/R-3).
- **No-auto-promotion / no-auto-run guardrails** validated in the scoped E2E
  (`e2e_simulation_result.md` §4) → the promoted behavior is already governance-aligned.
- **Deferred scope is explicit** (`known_limitations_and_backlog.md`) → the CR can copy the defer list
  verbatim as its out-of-scope section.
- **Clean E2E, no blocking defect** (`issue_warning_list.md`) → no known blocker gates promotion of the
  current agents (only minor documented ergonomics).

---

## 5. What this note explicitly does NOT do (R-5 guard)

- No write to `product/` or `.ai-work/`.
- No CR file created (no `product/change_requests/` entry).
- No path rebase applied; no lint run as part of promotion; no approval obtained.
- No promotion of any kind performed.

**This is preparation only. The actual promotion is a separate, future, HUMAN-approved CR (AP-CR-10),
out of scope of J-1 and J-2.** This note is its intended input.
