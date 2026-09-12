# Wiki Source Profiles (canonical-tooling package templates)


> **File này PACKAGE-OWNED (CR-AIWS-2026-08-114).** Mỗi lần nâng cấp AIWS nó sẽ được **ghi đè** về bản canonical — ghi chú riêng của dự án đừng để ở đây. Các file `*.yml` trong cùng thư mục thì **ngược lại**: chúng là cấu hình của dự án và không bao giờ bị ghi đè (`CR-AIWS-2026-06-047`).

A Source Interpretation Profile tells the meta builders how to interpret a source type (a small
YAML file: `profile_id`, `description`/`source_type`, `knowledge_targets`, optional hints +
`related_sources` scaffold config).

This package ships **only the canonical-tooling profiles the builders depend on** (CR-AIWS-2026-06-047):

- **`java_class.yml`** — required by `build_java_wiki_metas.py` (it emits `profile_id: java_class`).
- **`asp_cobol_source.yml`** — required by `build_cobol_wiki_metas.py` for the **ASP COBOL** preset
  (CR-AIWS-2026-08-026). Scoped to Fujitsu ASP, not COBOL in general: the dialect lives in the config the
  builder reads, so another dialect is a new preset (profile + config + route) on the same engine.
- **`knowledge_object.yml`** — required for `node_kind=object` metas (`profile_id: knowledge_object`,
  CR-AIWS-2026-06-004 C1; consumed by `lint_wiki.py`). It is also the registry of **active object kinds**:
  `lint_wiki._allowed_source_types()` unions `source_type`/`source_types` across every shipped profile, so an
  object kind is added by listing it here — a data edit, no builder change. The ASP preset's three object
  kinds (`asp_file`, `asp_module`, `asp_system`) live there for that reason.

A project materializes/extends its own runtime profiles under `.ai-work/wiki_sources/profiles/`.

## Install behavior — content-level MERGE, never overwrite (CR-AIWS-2026-06-047)

`wiki_source_profiles` are **project-owned**. On install/update the canonical profiles are **merged**
into `.ai-work/wiki_sources/profiles/`, never `cp -r`-overwritten:

- Project lacks a profile → the canonical profile is added verbatim.
- Project already has it → only the canonical **top-level keys it is missing** are appended; the
  project's existing keys/values/comments (incl. `extra_stopwords`) are left untouched.

The merge is performed by `merge_wiki_source_profiles.py` (shipped in tooling).

**Open-union lists merge by ITEM, not just by key (CR-AIWS-2026-08-028).** A key that already
exists in the project copy used to be left entirely alone, so a value newly shipped in a canonical
open-union list reached fresh installs only. `source_types` is now merged item-by-item: canonical
values the project lacks are appended, and every value the project added itself is preserved. The
set of item-merged keys is declared explicitly in the tool (`ITEM_MERGE_KEYS`) — a second
open-union key is the trigger to revisit that list, not a reason to merge every list blindly.

**Put comments on their OWN line.** `- value  # note` used to register the value *including* the
comment text, so the entry silently never took effect and the symptom surfaced far away as
`meta_source_type_unknown`. Inline comments are now stripped, but a comment on its own line is
still the clearer form — and a value containing a hash with no space before it (`asp#weird`) is
left untouched.

AIWS's own *content* profiles (methodology / wiki_guidelines / preset_knowledge) are AIWS-internal and are **not** shipped.

## Step-2 enrich — project-owned, never overwritten (CR-AIWS-2026-06-048)

A language meta builder runs a canonical **Step 1** (facts → lean meta, AIWS-owned) then a
project **Step 2 enrich** (project-owned). The enrich layer consumes Step 1's *facts dict*
(engine-agnostic — same under regex or tree-sitter) and contributes augmentations the builder
folds in: extra lookup keys, concept keys, edges, sections. Two mechanisms (HYBRID):

**(1) Declarative `enrich:` block (PRIMARY)** — added to the PROJECT's profile (e.g. its own
`java_class.yml` under `.ai-work/wiki_sources/profiles/`; merge-preserved on update, never shipped):

```yaml
enrich:
  lookup_key_patterns:        # each is a Python regex applied VERBATIM to the raw source; every
    - '\b[MA]-\d{2}\b'        #   match becomes an extra lookup key. Use SINGLE backslashes and a
                              #   single-quoted scalar (this minimal YAML reader does NOT unescape).
  concept_keywords:           # signal token (annotation / type-name / package) -> concept keys
    Scheduled: ["batch job", "scheduled task"]
```

Single-token added keys still pass the CR-043 code-key stopword filter; multi-word keys are kept.
With no `enrich:` block and no hook, Step-2 contributes nothing → output is byte-identical to Step-1.

**(2) Optional code-hook (ESCAPE)** — for logic beyond declarative rules, the project may add
`.ai-work/wiki_sources/enrich/<source_type>.py` (e.g. `java_source.py`) exposing:

```python
def enrich(facts: dict, src: str, ctx: dict) -> dict:
    """Pure, deterministic. Return any of:
    {extra_lookup_keys: [...], extra_concepts: [...], extra_edges: [...], extra_sections: [...]}."""
    return {}
```

`apply_enrich` imports the hook **if present** (absent → declarative-only; import/run error → logged
and skipped, never breaks Step 1). The hook is **project-owned and never shipped**. `extra_edges`
items may be `{"target","role","basis"}` dicts (or strings); `extra_sections` items are full
markdown blocks appended before `## Cautions`.

## Lookup-key stopwords (CR-AIWS-2026-06-043 Change A)

Lookup-key extraction drops generic noise words so keys stay discriminating. Universal built-in
stopword sets (English function words, common-English filler, web/CSS/JS, Vietnamese/UI-CRUD) live
in `_common.py` and are **never** project config. Two **project-tunable** knobs let a project add
its own generic terms **without editing any builder**:

- **`project_stopwords.yml`** (sibling of the profiles): a project-wide `stopwords:` list applied to
  **all** source types. It is **project-authored** — **not shipped** and **never written** by the
  install (CR-047 Change C). `configured_stopwords()` reads `<profiles dir>/project_stopwords.yml`
  if the project created one.
- **`extra_stopwords:`** (optional field on a profile, e.g. `knowledge_object.yml`): a list scoped
  to **one** source type only. Empty / absent = no effect (parser-tolerant); merge-preserved.

Matching is **case-insensitive, single tokens only** — multi-word curated keys (e.g.
`member management`) are never filtered. **Never ship populated project term-lists upstream** — these
templates stay empty; each project fills its own.

## `emit_scaffold` (CR-AIWS-2026-06-043 Change B)

A profile's `related_sources.emit_scaffold: false` (e.g. `knowledge_object.yml`) is honored as a
real boolean — the builder no longer re-emits an empty `## Related Sources` TODO scaffold for
profiles that opt out. Defaults to `true` when omitted. Shipped profiles that opt out because their
pages are **generated projections**: `overview_pages.yml`, `wiki_pages.yml` (CR-AIWS-2026-08-092 C2).

### Per-meta: `related_sources: none_by_design` (CR-AIWS-2026-08-092 C3)

Profile-level opt-out is coarse. When ONE meta of a scaffolding profile genuinely has no
relationships, the curator records that decision in the meta's **frontmatter**:

```yaml
related_sources: none_by_design
```

and drops the `## Related Sources` section. The marker is a curation-state field
(`CURATION_PRESERVE_FIELDS`, same mechanism as CR-058): **refresh** carries it and does not
re-scaffold the section, **lint** stops asking (`meta_related_sources_todo`) and instead warns
`meta_related_sources_marker_conflict` if the marker and a `## Related Sources` section coexist.
Deleting the section WITHOUT the marker is not a durable decision — the next refresh scaffolds it
back (Lớp 3 always-on TODO, CR-017), and the TODO text now says so.
