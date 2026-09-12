# aiws-pkg — operation: install

> Operation of the `aiws-pkg` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Set up a new project with AI Work System MVP: create `.ai-work/` structure,
copy skills/tooling from install package, create truth stubs, and wire `CLAUDE.local.md`.

## Inputs
- `project_root` (required) — absolute path to the target project
- `project_name` (required) — project name (used in CLAUDE.local.md)
- `package_path` (required) — path to the install package folder (contains `payload/`)
- `rule_targets` (optional) — which AI tools this team uses: multi-select `claude` | `agents` | `copilot`
  (default: `claude`). **Ask the HUMAN which Copilot *surface* they use** — do not infer from the IDE
  (see the coverage table in Flow step 6).
- `claude_rule_file` (optional) — `CLAUDE.local.md` (default) or `CLAUDE.md`; validate against exactly
  these two. *Alias, one release:* `claude_target=X` means `rule_targets=claude` + `claude_rule_file=X`.

## Flow
1. Clarify inputs; confirm with HUMAN before any file changes
2. Pre-flight — check Python >= 3.8, detect conflicts, verify package structure
3. Create `.ai-work/` directory structure (incl. `.ai-work/wiki/reference/`) + `.claude/skills/` + `.claude/commands/`
4. Copy payload sections to destinations (skills → `.claude/skills/`, commands → `.claude/commands/`, tooling → `.ai-work/tooling/`, etc.) — the **authoritative** payload→target list is the package's generated `install_guide.md` (§2 Payload mapping + §3); when a payload Section is added, this list + the install_guide update together (single source — CR-037 C4). **Exception — `wiki_source_profiles`:** project-owned → **MERGE** (never `cp -r`-overwrite) via `py .ai-work/tooling/merge_wiki_source_profiles.py --from <pkg>/payload/wiki_source_profiles --into .ai-work/wiki_sources/profiles --apply`; preserves a project's customized profiles + `extra_stopwords`, never writes `project_stopwords.yml` (CR-AIWS-2026-06-047). (Fresh init = the merge simply adds both canonical profiles.)
4b. Scaffold project-local reference doc — copy `wiki_guidelines/install/document_search_guidelines.template.md` → `.ai-work/wiki/reference/document_search_guidelines.md` (a fill-in starting point; keep the `## Raw search fallback — project artifact directories` heading verbatim; replace `<...>` placeholders with the project's task types / source-ids / artifact dirs, or leave to fill on first use). Required by `INSTALL_CHECKLIST.md`.
4c. Set account_id (CR-AIWS-2026-06-016) — ASK the HUMAN for their `account_id`, then run `py .ai-work/tooling/account_id.py set --account-id <id>` (validates dir-safe + lowercases; writes the gitignored `.ai-work/account_info.yaml` with a seeded `next_aip_id` counter; ensures `.gitignore` ignores it). Required before any AIP id allocation (CR-015 v2 precondition). NEVER invent the id — it is HUMAN-set.
4d. Place the AIWS preset wiki (CR-040 + CR-AIWS-2026-08-064) — after `payload/aiws_wiki/` is copied to `.ai-work/wiki_sources/aiws_meta/`, copy the PRE-BUILT `payload/aiws_wiki_index/index.aiws.jsonl` + `relations.aiws.jsonl` into `.ai-work/wiki_sources/` (or, when the package has no `aiws_wiki_index/`, rebuild both: `py .ai-work/tooling/build_preset_wiki.py --target .`). Makes AIWS methodology/spec/preset lookup-able immediately via `lookup_wiki_source.py --scope aiws` (or default `--scope all`) and traversable via `wiki_relations.py --relations <id>` (reads project + aiws relations). The project's own `index.jsonl` / `relations.jsonl` stay empty until `/aiws-wiki bootstrap` — the two namespaces are disjoint (never index `aiws_meta/` into `index.jsonl`; `build_relations.py` defaults to `--namespace project` once `relations.aiws.jsonl` exists).
4e. Seed the project profile (CR-AIWS-2026-08-128) — `py .ai-work/tooling/project_profile.py init`, then `py .ai-work/tooling/project_profile.py check`. `init` copies the shipped skeleton `install_templates/project_profile.template.yml` → `.ai-work/project_profile.yml` **only when absent**; it is **project-owned** (unlike `AIWS.md`, an upgrade never overwrites it). `check` prints every missing required key and every violated invariant, then exits non-zero — it **never guesses**, and it never calls `input()`, so it behaves identically in CI, in an agent run and in a terminal. If it reports a **missing key**, `project_profile.py refresh --apply` adds it inside the `AIWS:BEGIN` block without touching a single line the project wrote. If it reports a **broken invariant** (e.g. `multi_system: true` with an empty `systems:`), **ASK THE HUMAN** — that is a decision about their project, not a default to fill in. Before this CR the file was seeded by nothing and was measurably absent from real installs, so every project ran on absent-file defaults.
5. Init truth stubs — copy SOP templates; create empty `AI_WORK_CONTRACT.md`; seed `.gitattributes` carrying `* -text` (CR-AIWS-2026-08-005) — **seed-if-absent at the project ROOT**, never overwritten. v1.2.0 shipped `check_eol_alignment.py`, whose docstring asserts this convention, without ever handing the convention to the target (IR-2026-08-15 F6). If a project declines it (has its own `.gitattributes`, or removes the seeded one), `check_eol_alignment.py` will report cross-source EOL noise — that is expected, not a bug.
6. Wire rule files (CR-AIWS-2026-08-066) — rule content is RENDERED from one source, never hand-copied:
   (i) copy `payload/install_templates/` (incl. the build-stamped `VERSION`) → `.ai-work/install_templates/`;
   (ii) copy `aiws_core_rules.md` → **`.ai-work/AIWS.md`** (core rules, package-owned);
   (iii) `py .ai-work/tooling/compose_aiws_rules.py --init --tools <rule_targets> --claude-file <claude_rule_file> --project-name "<name>"` — **dry-run first**, show the diff to the HUMAN, then re-run with `--apply`;
   (iv) a pre-existing file makes the tool STOP with the verb to use — hand-written AIWS rules → `--migrate-legacy`; unrelated file → `--append-existing` (**ask the HUMAN first**); already-wired → `--refresh` (that is upgrade's path, not install's);
   (v) verify: `compose_aiws_rules.py --check` → rc=0, every block on the manifest version.

   | target | file | git | serves |
   |---|---|---|---|
   | `claude` | `<claude_rule_file>` | `CLAUDE.local.md` gitignored · `CLAUDE.md` committed | Claude Code — core via `@.ai-work/AIWS.md` |
   | `agents` | `AGENTS.md` (repo root) | committed | Codex · Copilot coding agent/CLI/Chat-in-VS-Code/code-review-GitHub.com · Cursor/Zed… |
   | `copilot` | `.github/copilot-instructions.md` | committed | Copilot surfaces that do NOT read AGENTS.md — e.g. **code review in VS Code**, Chat outside VS Code |

   **Onboarding note for the Report (when `claude_rule_file=CLAUDE.local.md`):** that file is gitignored, so a
   teammate who clones the repo gets **zero** AIWS rules until they run
   `py .ai-work/tooling/compose_aiws_rules.py --init --tools claude --apply`. Put that one-liner in the report;
   for a team of more than one, suggest `CLAUDE.md` instead.
7. Create `.claude/settings.local.json` only if not already present
8. Smoke test — run `lint_all.py --help`, `lookup_wiki_source.py --query methodology`, and `lookup_wiki_source.py --query AIP --scope aiws` (the last MUST return ≥1 AIWS hit — confirms the `aiws` namespace built)
9. Report results; suggest `/aiws-lint` next

## Rules
- `wiki_source_profiles` is project-owned — **merge, never overwrite** (use `merge_wiki_source_profiles.py`); never create/overwrite `project_stopwords.yml` (CR-AIWS-2026-06-047)
- never overwrite existing files without asking HUMAN first
- never invent Truth content — only create empty stubs or copy templates
- stop and report clearly if pre-flight fails; do not proceed
- `settings.local.json` — create only if absent; do not auto-merge
- scaffold `.ai-work/wiki/reference/document_search_guidelines.md` from `wiki_guidelines/install/document_search_guidelines.template.md` — a fill-in starting point (INSTALL_CHECKLIST requires it); the project fills its task-type sources + artifact dirs
- AIWS wiki (CR-040 / CR-064): the `aiws` namespace = `aiws_meta/` + `index.aiws.jsonl` + `relations.aiws.jsonl` (step 4d — copy pre-built or `build_preset_wiki.py --target .`); keep it disjoint from the project's own `index.jsonl`/`relations.jsonl`/`meta/` — never index `aiws_meta/` into the project index
- **Agents package (CR-AIWS-2026-06-055), single-track:** if the package ships `payload/agents/`, copy it to **`.ai-work/agents/`** (install_guide §2 row 14 is authoritative); the `aiws-agent` router skill arrives via the standard `payload/skills`→`.claude/skills` copy, and the verb entry points arrive as **generated pointer-stubs** via `payload/commands`→`.claude/commands` (CR-AIWS-2026-08-019 — spec content stays pack-internal in `.ai-work/agents/commands/`, per CR-AIWS-2026-07-031 T3). Single target `.ai-work/` — there is **no `.aiws-staging`**; maturity is managed by branch in the AIWS source repo, not by a target dotfolder.
- **Rule-file ownership (CR-AIWS-2026-08-066):** `.ai-work/AIWS.md` + `.ai-work/install_templates/` are
  package-owned (upgrade overwrites them) · everything INSIDE the `AIWS:BEGIN rules` block is tool-managed
  (hand edits there are lost on refresh) · everything OUTSIDE the block is project-owned and never touched.
  A rule file is **not Truth** — Truth is `SOP_MASTER` + `AI_WORK_CONTRACT` only.
- skip the rule-file step entirely when `rule_targets` does not include a target (e.g. no `claude` → no CLAUDE file)
- suggest `/aiws-lint` after install to verify
