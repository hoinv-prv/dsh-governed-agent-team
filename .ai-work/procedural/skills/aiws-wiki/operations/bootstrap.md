# aiws-wiki — operation: bootstrap

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.

You are running **`/aiws-wiki bootstrap`** — the one-time bootstrap that builds this project's Knowledge Hub / wiki.

**Authority = the method:** `product/wiki_guidelines/core/guidelines/PROJECT_WIKI_BUILDUP_GUIDELINE.md`. You do **NOT**
re-author or re-derive that method. Your job is to **instantiate a FIXED 12-step skeleton** (the manifest below), tailor it
to this project via exploration + Q&A, and **delegate the actual AIP authoring to `/aiws-aip create` + `/aiws-aip run`**. You never
write the AIP file yourself, never add/remove/reorder steps, and never author step content free-form.

`$1` = optional corpus root (the directory the wiki should cover). If omitted, ask the HUMAN in Step B.

## Pre-flight (HARD)
1. **Multi-system (CLAUDE.md §12 / CR-AIWS-2026-06-017):** read `.ai-work/project_profile.yml`. If `multi_system: true`,
   establish the **active system** by asking the HUMAN and pass `--system <id>` on every `lookup_wiki_source.py` call;
   never auto-set. If a lookup errors for a missing system → **STOP and ask**, never guess.
2. **First-build only:** this command is for the FIRST build. Maintenance of an already-built wiki uses the **sync loop**
   (`aiws-wiki refresh`), NOT this command. If a wiki already exists, confirm with the HUMAN before proceeding.

## Step A — Explore SHAPE + inventory (only)
- Quick `Glob` skim of `$1` (or the root the HUMAN names). Classify project **SHAPE**: `docs-only` / `code-heavy` / `mixed`
  (heuristic in guideline §Step 1). Note the natural groups (path + extension + format) for a rough inventory.
- **Scope discipline:** explore ONLY to classify shape + inventory. Do **NOT** resolve canonical input *paths* by
  exploration — that is the wiki-lookup HARD GATE's job at execution time (the generated AIP lists inputs as `(lookup)`
  rows). Do not `Glob`/`Grep` to pin RD/BD/DD/spec paths here.

## Step B — Q&A with the HUMAN (gate; never guess)
Confirm, and record for the AIP brief:
- **Scope** — the in/out boundary (force one; reject "cover everything").
- **Purpose** — Q&A-only vs supporting which **task kinds** → these become the EXEC **Step-10 acceptance simulation cases** (HUMAN-set).
- **Project shape** — confirm A's classification.
- **Object-node gate** — is there a stable enumeration source (feature/requirement/function list)? Is the object-node
  tooling gate satisfiable? If not → identity nodes are SKIPPED (doc↔doc / companion-design edges only). Never synthesize identity nodes to fill a slot.

## Step C — Instantiate the FIXED 12-step skeleton
Build the AIP step list from the manifest below — **exactly these 12 steps, in order, none added/removed**. For each step:
- pin its guideline section in the AIP step's `Applicable Guidelines` as `PROJECT_WIKI_BUILDUP_GUIDELINE.md §<ref>` **plus**
  the always-read core `§How an AI should use this guideline` (the cross-cutting "important points": candidate→review→apply,
  capture-first, never hand-edit projections, never invent object nodes/edges, lint-is-a-guardrail, the running BUILD LOG +
  LESSON LOG rules). Instruct reading **{core + the step's §}**, not the whole guideline.
- apply project **shape** as a per-step **ANNOTATION** in the step body (see the Shape column) — **never** by deleting a step
  (deletion would orphan a HARD GATE and leave a numbering gap).

### Fixed manifest (do not edit at runtime)
| Step | Title | Guideline §-ref | Mandatory skills | HUMAN gate | Shape annotation |
|---|---|---|---|---|---|
| STEP-00 | Confirm Task Understanding (HARD GATE) | §How an AI should use this guideline | — | HUMAN confirms understanding | — |
| STEP-01 | Define the GOAL of the wiki | §Step 1 | aiws-wiki lookup | scope + purpose + shape + task-kinds (HUMAN-set) | shape fixed here |
| STEP-02 | Decide WHAT goes in (inventory) | §Step 2 | aiws-wiki lookup | in/out + source_type per group | docs-by-role vs language/layer groups |
| STEP-03 | Confirm authority / value / use | §Step 3 | — | matrix (esp. SoT boundary) | mark mockups "NOT source of truth" |
| STEP-04 | Predict the relationships | §Step 4 | wiki-relations | relation map (types + directions) | docs-only → doc↔doc; code → design→source + cross-layer |
| STEP-05 | Plan the meta build | §Step 5 | aiws-wiki register-batch, aiws-wiki build-pattern | plan + per-group method | docs-only → skip source-code layer |
| STEP-06 | Identify the tools to build | §Step 6 | aiws-wiki register-batch | directive per NEW bulk builder | docs-only → usually no bulk builder / no cross-layer matcher |
| STEP-07 | Trial-run build-meta on samples | §Step 7 | aiws-wiki build-meta, aiws-wiki test-lookup, aiws-lint | approve sample format + 3-keyword smoke | docs-only → trial the PROFILE, not a tool |
| STEP-08 | Build/confirm the refresh tool | §Step 8 | aiws-wiki refresh | refresh preserves curated content | docs-only → single-artifact refresh, no matcher caveat |
| STEP-09 | Mass-run + spot-checks + wire relations | §Step 9 | aiws-wiki register-batch, aiws-lint, wiki-relations | fix-and-rerun loop | docs-only no-seed → wire doc↔doc only, skip object nodes + matcher |
| STEP-10 | Test the wiki; tune the profile | §Step 10 | aiws-wiki test-lookup, aiws-lint | cap curation + task-sim gaps (DoD) | docs-only → test doc↔doc bidirectional |
| STEP-11 | Produce the project's wiki build-up guideline | §Step 11 | — | accept guideline + triage lessons | — |

Also instruct the AIP to: set up the running **BUILD LOG** + cross-project **LESSON LOG** in Step 01, name `build-log.md`
as an explicit **input** to Step 11 (so a broken thread surfaces), and resolve canonical inputs as `(lookup)` rows.

## Step D — Delegate AIP authoring (MANDATORY — do not write the AIP yourself)
Hand the assembled brief (shape · scoped corpus root(s) · the 12-step skeleton with per-step §-pins + shape annotations ·
acceptance task-kinds · object-node gate decision · BUILD/LESSON-LOG setup) to **`/aiws-aip create`**. It owns the gates:
ID-allocation (`allocate_aip_id.py`), template read, the `lint_aip` 0-error gate, the Mixed-Governance Note, and the
wiki-lookup HARD GATE. Choose:
- **large / unclear corpus / object nodes likely → a PLAN** (it brainstorms scope/shape, then derives the EXEC);
- **small & clear (e.g. a docs-only handful, no enumeration) → EXEC-direct.**

## Step E — Self-check + HUMAN review (candidate → review → run)
Before any execution:
1. confirm `py .ai-work/tooling/lint_aip.py --path <aip>` → **0 errors**;
2. confirm the AIP has **STEP-00..STEP-11 sequential** (none deleted) and each step's `§`-pin resolves to a real section in the guideline;
3. **present the generated AIP to the HUMAN for review** — do NOT auto-start `/aiws-aip run`. (Lint is a guardrail, not a reviewer.)
Only after HUMAN approval: `/aiws-aip run start <aip>`.

## When NOT to use this command
- Maintaining an already-built wiki → the project's **whole-repo refresh/sync command** (`/refresh-project-wiki-all`, built per **PROJECT_WIKI_BUILDUP_GUIDELINE Appendix G**), not this.
- Registering a single new document → `/aiws-wiki register` directly.

> Reference: the full method + per-step detail live in `PROJECT_WIKI_BUILDUP_GUIDELINE.md` — each manifest row's `§`-ref points to its section there.

## Overview pages (CR-AIWS-2026-07-010 — wiring)

- STEP-02 INVENTORY: persist quyết định in/out làm seed đối chiếu cho trang `WIKI_CONTENTS_OVERVIEW` (trang generated sẽ là bản maintained).
- STEP-11 (cuối bootstrap): chạy `py .ai-work/tooling/build_wiki_overview.py --all-systems` (hoặc `--system <id>`) để project mới có contents/search/health pages từ ngày 0; maintenance sau đó theo Appendix G step 7.
- **Wrap-up (optional handoff, opt-in — CR-AIWS-2026-07-023):** sau khi wiki build xong, ĐỀ NGHỊ HUMAN chạy `/aiws-wiki build-pages survey` để build bộ trang onboarding curated (system overview, function list, business flow...). HUMAN từ chối → ghi deferred vào rollout notes, chạy sau bất kỳ lúc nào. KHÔNG thêm step mới (giữ khung 12-step).
