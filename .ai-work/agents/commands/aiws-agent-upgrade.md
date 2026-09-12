---
description: Phát hiện drift giữa desk và Blueprint rồi TRÌNH BÀY từng thay đổi kèm WHY, cạnh customization của desk, để HUMAN quyết từng mục. Không bao giờ tự áp dụng, không đụng lớp desk-learned.
argument-hint: <desk> [--reconcile --to-version <v> --decisions "..."]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, TodoWrite
---

# Command Spec — `/aiws-agent-upgrade`

> **Status:** prompt/spec (file-first), backed by thin tooling `tooling/run_agent.py` (stdlib, `py`). NOT a full CLI. Post-MVP lifecycle verb.
> **Built by:** AIP-EXEC-146 (Desk lifecycle; AP-CR-27, AP-DDR-15).
> **Source:** Detailed Design §6A + §4A + §5; requirements FR-AI-09/FR-AI-10; 09 AP-CR-27 (impl package, repo nguồn AIWS — không ship trong bản cài).
> **Scope:** reconcile an existing blueprint-based Agent Task Desk against a **newer Blueprint version**, HUMAN-gated, without overwriting the desk's own work. Does **not** create task desks (`/aiws-agent-create`), does **not** run them (`/aiws-agent-run`), does **not** confirm memory (`/aiws-agent-review-learning`).

## Purpose
When AIWS ships a newer version of a Blueprint, a Task Desk created from it may **drift** behind. `/aiws-agent-upgrade` detects that drift and **presents** the Blueprint's changes (with their WHY) next to the desk's customizations (with their WHY) so the **HUMAN decides, per change**, what to adopt — without ever silently overwriting what the desk has learned or been customized to do.

## HARD RULE — present, never auto-apply; never touch the desk-learned layer
The tool **PRESENTS** the diff and **RECORDS a HUMAN decision**. It does **not** merge Blueprint content into the desk automatically, and it **NEVER writes the desk-learned layer** (`memory/`, `training/`, `local_guidelines`, `context/`) — the **Three-Layer Ownership Invariant (FR-AI-09)**. Adopting a Blueprint change into the desk-override layer is a HUMAN edit; the tool only re-pins the version, refreshes the snapshot, and logs the decision.

## Guardrails (always)
- **Upgrade ≠ auto-apply.** No LLM, no auto-merge, no chaining. Drift is *shown*; the HUMAN decides.
- **Ownership invariant (FR-AI-09):** Blueprint (AIWS-owned, upgradeable) / Desk-override (HUMAN-confirm per change) / Desk-learned (**never** auto-overwritten — advisory only).
- **No auto-promotion:** reconcile decisions are HUMAN-gated; learned memory is advisory-never-delete.
- Writes only under `agents/task_desks/<instance>/` (relative to the pack root; staging; boundary-guarded) — and only the blueprint-derived metadata (`blueprint_ref.yaml` version pin + `reconcile_log`, `.atdb_snapshot/`, the desk `changelog.md`), never the learned layer.

## Subcommands

### present drift (default)
```
/aiws-agent-upgrade <instance>
```
Tool: `py tooling/run_agent.py upgrade <instance>`
- Shows pinned vs current `blueprint_version` and a `.atdb_snapshot/` vs current `blueprint.yaml` diff signal (`[outdated]` = version pin behind; `[drift]` = content differs). The first run on a task desk with no snapshot **captures the baseline** (setup, not a reconcile).
- When drift exists, **presents** the Blueprint `changelog.md` (WHY of each blueprint change — §4A), the desk `changelog.md` + `customization_summary` (WHY of each desk customization), then prints the `--reconcile` command to record a decision. It applies nothing.

### record a HUMAN-confirmed reconcile
```
/aiws-agent-upgrade <instance> --reconcile --to-version "<v>" --decisions "adopted X, skipped Y"
```
- Re-pins `blueprint_ref.blueprint_version`, refreshes `.atdb_snapshot/`, appends a `reconcile_log` entry (§5) and a desk `changelog.md` entry (`layer: override`, `source: HUMAN-feedback`). The desk-learned layer is **not** touched; apply any adopted blueprint changes to the desk-override layer yourself.

## Drift in `list`
`py tooling/run_agent.py list` flags genuinely-diverged task desks `[outdated]`/`[drift]` beside `[aip_driven]`. A not-yet-baselined desk shows **no** marker (benign).

## Outputs
`blueprint_ref.yaml` (re-pinned `blueprint_version` + appended `reconcile_log`) · `.atdb_snapshot/` (refreshed baseline) · desk `changelog.md` (reconcile entry). Never: `memory/`, `training/`, `context/`, `local_guidelines`.

## Related
`/aiws-agent-create` (make the desk — writes the initial snapshot) · `/aiws-agent-clone` (clone a task desk — clones inherit the pinned version + snapshot and still reconcile) · `/aiws-agent-rename` (change a task desk's id + folder, with a `previous_ids` alias) · `/aiws-agent-run` (run a task) · `/aiws-agent-review-learning` (confirm candidates → memory).
