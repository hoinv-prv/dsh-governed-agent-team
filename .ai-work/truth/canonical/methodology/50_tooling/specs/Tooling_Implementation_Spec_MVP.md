# Tooling Implementation Spec for AI Work System MVP
Version: 0.2  
Status: Draft  
Phase: Detail Design / Tooling Spec  
Scope: MVP only

---

# 1. Purpose

This spec details the **tooling layer** of AI Work System MVP.

This version updates tooling expectations to align with **Wiki v1.0 freeze**, especially the source-side model:
- `Wiki Source Artifact`
- `Wiki Source Meta`
- `Wiki Source Index`
- `Source Interpretation Profile`

Tooling exists to support deterministic-first operations around:
- AIP + Workspace
- Wiki source discovery
- source meta refresh
- wiki candidate generation
- lint and structural quality

---

# 2. Tooling principles

## 2.1. Deterministic first
Prefer deterministic parsing / checking / rendering / projection over LLM reasoning whenever possible.

## 2.2. No silent truth rewrite
Tools must not silently rewrite:
- Truth
- official Wiki
- canonical docs

## 2.3. Support the workflow, do not redefine it
Tools support:
- controlled wiki update
- source meta refresh
- workspace execution
- lint / validation

They do not redefine governance.

## 2.4. Index/meta-first support
Tools for wiki must assume the standard reading/build flow:

**Wiki Source Index / Meta → confirm relevance → Wiki Source Artifact → Source Interpretation Profile → Wiki Draft/Candidate/Update**

---

# 3. Minimal tooling sets in MVP

## 3.1. Runtime / AIP tooling
1. `build_active_step_context.py`
2. `set_current_step.py`
3. `init_workspace.py`
4. `lint_aip.py`
5. `lint_workspace.py`

## 3.2. Wiki / source-side tooling
6. `build_wiki_source_meta.py`
7. `build_wiki_source_index.py`
8. `lookup_wiki_source.py`
9. `refresh_wiki_source_meta.py`
10. `lint_wiki.py`

## 3.3. Optional future-friendly tools
11. `detect_changed_wiki_sources.py`
12. `evaluate_wiki_source_impact.py`
13. `build_wiki_candidate.py`
14. optional `lint_all.py`

These are optional for MVP baseline, but the model should leave room for them.

---

# 4. Existing runtime tools

## 4.1. build_active_step_context.py
Purpose:
- materialize Active Step Context from AIP + linked runtime state

## 4.2. set_current_step.py
Purpose:
- update current step pointer

## 4.3. init_workspace.py
Purpose:
- create minimal runtime workspace scaffold

## 4.4. lint_aip.py
Purpose:
- lint AIP structure/metadata/step quality

## 4.5. lint_workspace.py
Purpose:
- lint runtime workspace integrity

---

# 5. New wiki/source-side tool expectations

# 5.1. build_wiki_source_meta.py
## Purpose
Create or refresh a `Wiki Source Meta` from a `Wiki Source Artifact` using a `Source Interpretation Profile`.

## Input
Required:
- artifact locator / source file
- source type or profile id
- output path or source id

Optional:
- existing meta path
- existing index path
- mode: create | refresh

## Output
- `Wiki Source Meta` artifact
- optionally updated projection data for index refresh

## Responsibilities
- generate small, memory-friendly source meta
- include richer `lookup_keys` than index
- attach profile mapping
- include source-specific hints
- include change impact hints when relevant

## Must not do
- rewrite official wiki entry
- treat meta as source-of-truth
- inline full source content into meta

# 5.2. build_wiki_source_index.py
## Purpose
Build or refresh `Wiki Source Index` from source metas.

## Input
- folder of source metas
- output index path

## Output
- `Wiki Source Index`

## Responsibilities
- generate lightweight index entries as projections of source metas
- preserve grep-friendly lexical lookup surface
- include pointer to meta and artifact
- keep entries small

## Must not do
- embed full meta into index
- become a second full meta store

# 5.3. lookup_wiki_source.py
## Purpose
Lookup source candidates through the `Wiki Source Index`.

## Lookup modes
- lexical / exact lookup
- identifier lookup
- path token lookup
- optional semantic-like matching later if supported

## Input
- query string
- index path

## Output
- matched `Wiki Source Index Entry` records
- pointers to meta / artifact

## Responsibilities
- support grep-friendly exact matching use cases
- support "confirm before opening source artifact"

# 5.4. refresh_wiki_source_meta.py
## Purpose
Refresh source meta when source artifact changed or when meta is marked stale.

## Input
- source id or artifact locator
- index path
- source meta path
- profile id or derived profile mapping

## Output
- refreshed meta draft or updated meta artifact
- comparison result with previous meta if available

## Responsibilities
- use source artifact + profile
- compare old vs new meta where possible
- indicate whether material change occurred
- optionally produce meta refresh candidate result

## Must not do
- rewrite official wiki directly

# 5.5. lint_wiki.py
## Purpose
Lint wiki knowledge artifacts plus source-side wiki artifacts.

## Now includes checks for:
- wiki entries
- wiki source metas
- wiki source index

---

# 6. Optional change-detection tools

## detect_changed_wiki_sources.py
Purpose:
- determine whether source artifacts may have changed

Notes:
- may use manual signals
- may use lightweight file snapshot/signature checks
- may use Git as optional change signal
- Git is not part of meta; Git is just optional detection input

## evaluate_wiki_source_impact.py
Purpose:
- interpret source changes through Source Interpretation Profile
- estimate whether wiki candidate update is needed

Notes:
- should operate after source change detection and preferably after meta refresh

---

# 7. Updated lint scope expectations

`lint_wiki.py` should now support three target groups:
1. official wiki entries
2. wiki source metas
3. wiki source index

More detailed lint rules are specified in `Lint_and_Tooling_Spec_MVP_v0_2.md`.

---

# 8. Tool input/output philosophy

## 8.1. Read-only by default
Lint and lookup tools should be read-only.

## 8.2. Controlled writes
Write tools may create/update:
- Active Step Context
- step pointers
- workspace scaffolds
- source meta
- index projection

But must not silently modify:
- official Truth
- official Wiki entries

## 8.3. Projection rule
Any tool that touches index must respect:
- index = projection
- meta = richer context
- artifact = full source

---

# 9. CLI behavior recommendations

Each tool should prefer:
- explicit required args
- `--help`
- predictable exit code
- readable text output
- optional JSON output

Recommended conventions:
- `--path`
- `--workspace`
- `--aip`
- `--index`
- `--meta`
- `--artifact`
- `--profile`
- `--strict`
- `--format text|json`

---

# 10. Priority order for implementation

## Priority 1
1. `build_active_step_context.py`
2. `set_current_step.py`
3. `lint_aip.py`

## Priority 2
4. `init_workspace.py`
5. `lint_workspace.py`
6. `build_wiki_source_meta.py`

## Priority 3
7. `build_wiki_source_index.py`
8. `lookup_wiki_source.py`
9. `lint_wiki.py`

## Priority 4
10. `refresh_wiki_source_meta.py`
11. optional `detect_changed_wiki_sources.py`
12. optional `evaluate_wiki_source_impact.py`

---

# 11. Acceptance criteria

Tooling is minimally acceptable when:

## Runtime side
- current step can be pointed and materialized deterministically
- invalid AIP structure can be detected
- workspace scaffold can be created consistently

## Wiki side
- source meta can be built from a source artifact
- index can be built as a projection of metas
- exact/lexical source lookup is possible from index
- wiki/source lint can detect structural errors
- no tool silently rewrites official wiki/truth

---

# 12. Non-goals

Tooling MVP does not aim to:
- deeply infer business truth automatically
- replace human review
- implement full graph navigation
- implement automatic wiki apply/update without review

---

# 13. Conclusion

This tooling spec now treats Wiki as a source-aware, index/meta-driven system.

The tooling layer must therefore support:
- source-side indexing
- source meta generation/refresh
- exact + semantic-friendly lookup surfaces
- controlled progression from source to wiki candidate

without collapsing:
- index into full meta
- meta into source
- tooling into governance.

---

# 7. Wiki Tooling Improvements — 2026-05-27 Addendum

**Source:** Applied from wiki_improvement_request.md (validated in vti-ai-work-system-demo, 2026-05-26).

## 7.1 build_wiki_source_meta.py — Extended Responsibilities (supplements §5.1)

**New semantic override args** (priority 1 over profile extraction):
- `--summary` — AI-derived semantic summary (overrides auto-extraction)
- `--knowledge-targets` — comma-separated list (overrides profile `knowledge_targets`)
- `--lookup-keys` — comma-separated T1/T2/T3 keys, pinned to top of lookup key list
- `--hints-depth N` — max heading depth for Source-Specific Hints (default: 2)
- `--skip-format-check` — bypass format validation (requires all 4 semantic args)

**PMP loader:** Loads `pmp_<profile_id>.yml` alongside profile when it exists.
PMP takes precedence for extraction logic (`summary_extraction`, `t1_key_extraction`,
`hints_extraction`, `format_signature`).
Falls back gracefully when PMP not found.

**BOM fix:** Files beginning with UTF-8 BOM (`U+FEFF`) handled correctly — BOM stripped before heading detection.

**Slim meta output:** Removed body sections: Runtime Use, Source Representation, Cautions,
Change Impact Hints, Profile Mapping, Artifact Reference.
Blank frontmatter fields omitted. Retained: Summary, Knowledge Targets, Lookup Keys, Source-Specific Hints.

## 7.2 build_wiki_source_index.py — Extended Responsibilities (supplements §5.2)

**Slim projection:**
- Fields permanently removed from index entries: `meta_id`, `updated_at`, `knowledge_value`, `intended_ai_use`
- Conditional fields: `original_source_locator`, `representation_locator` — omitted when identical to `artifact_locator`
- `_omit_blank()` applied: fields with value `""`, `None`, or `[]` are omitted

Token impact: ~420 → ~90–130 tokens/entry.

## 7.3 lookup_wiki_source.py — Extended Responsibilities (supplements §5.3)

**Raw fallback hint:** When 0 matches, prints a structured hint guiding AI to retry semantic mode,
then raw search in artifact dirs, then ask HUMAN.
JSON mode (0 matches): returns `{"matches": [], "raw_fallback_hint": "..."}` instead of empty array.

**Default limit:** `--limit` changed 10 → 5; `--top N` alias added.

## 7.4 Profile vs PMP Architecture (supplements §2.4)

- **Profile** = AIWS canonical, generic-only: `profile_id`, `description`, `knowledge_targets`
- **PMP** = project-specific extraction spec: `format_signature`, `summary_extraction`,
  `t1_key_extraction`, `hints_extraction`, `canonical_slot_mapping`
- Tool (`build_wiki_source_meta.py`) loads both; PMP takes precedence for extraction;
  profile provides `knowledge_targets`

This ensures profiles remain reusable across projects while project-specific format knowledge lives in PMPs.
