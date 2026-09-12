# aiws-wiki — operation: add-local-knowledge

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Register an external local knowledge source so AI can discover it exists,
evaluate relevance before asking HUMAN, and search it via wiki after confirmation.

## Inputs
- `meta_dir` — absolute path to the external wiki source meta directory
- `label` — short name for this knowledge base
- `description` — domain / product / topics it covers
- `search_triggers` — keywords that should make AI consider this source

## Flow
1. Update `index.local.sources.json` — add `meta_dir` if not already present
2. Rebuild local index via `build_wiki_source_index.py --scope local`
3. Create or update `LOCAL_KNOWLEDGE_OVERVIEW.md` with a new source section
4. Verify `CLAUDE.local.md` Rule 11 references `LOCAL_KNOWLEDGE_OVERVIEW.md`

## Rules
- never remove entries from `index.local.sources.json`
- always rebuild index after updating sources
- always update `LOCAL_KNOWLEDGE_OVERVIEW.md` — it is AI's primary relevance filter
- do not embed full artifact content into the overview

---

## CR-S9: Auto-suggest Profile + Tier Hints (2026-05-25)

Source: AIP-EXEC-015 STEP-03, CR-S9.

### Enhanced flow

When registering a local knowledge source, after collecting `meta_dir` + `label` + `description`, prompt the user with:

**Step A — Profile suggestion:**
Suggest top-3 profile candidates based on:
- File extension heuristic (`.md` → design_doc, `.xlsx` → check convert first, etc.)
- Content signature from `description` + `search_triggers` text
- Match against available profiles in `.ai-work/wiki_sources/profiles/`

Format suggestion as:
```
Based on description, suggested profiles:
1. design_doc (confidence: high) — typical for design specs
2. methodology_spec (confidence: medium) — if source is process/guideline heavy
3. [custom] — describe your custom profile type
Which profile best fits this source?
```

**Step B — Tier hints:**
If user provides lookup key examples, ask them to classify:
```
For lookup keys you plan to use for this source, indicate tier:
- T1 (unique IDs, canonical names): [examples?]
- T2 (domain terms, aliases): [examples?]
- T3 (category labels): [examples?]
```

Record tier hints in `LOCAL_KNOWLEDGE_OVERVIEW.md` source section for future build guidance.
