# aiws-wiki — operation: lookup

Find the right registered source before opening raw artifacts. Every gate below is binding.

## Tools
Run as `python .ai-work/tooling/<tool> …` (on Windows use `py`).
- `lookup_wiki_source.py --query Q --system S [--mode lexical|id|path|tokens|catalog] [--limit N] [--full] [--excludes IDS] [--source-type T]` — find. Slim output by default (1 line/result). `--mode tokens` is diacritic-insensitive.
- `wiki_meta.py --view ID` — read a meta; never open the meta file. Header has the `artifact:` path; its Related Sources line is out-only.
- `wiki_relations.py --relations ID` — out + IN edges: impact, "who calls X", everything about an object. Needs a source_id (find it first, or `--mode id`).
- `build_reading_kit.py --query "<task>" --system S` (or `--function F02`) — whole RD↔BD↔DD set in one call; prefer it for review/authoring of a known function/object.

## Hard rules
1. **Multi-system:** if `multi_system: true`, every call needs `--system S` or `--all-systems`. Missing → tool errors → STOP, ask HUMAN which system. Never guess; never merge specs across systems.
2. **Index-first:** never grep/Glob the repo before a lookup. Never `Read` whole `index.jsonl` / `relations.jsonl`.
3. **Raw is authorization-gated.** Default scope `project,aiws`. `--include-raw off|on-empty|always`, `--scope project,local`, `--scope all` need `--authorized human|aip|agent-rule`, else the tool refuses → STOP, ask HUMAN. `local` needs HUMAN approval first (`--scope project,local --authorized human`). `on-empty` fires only for `--lookup-mode object` with 0 registered hits. Raw hits are marked `unregistered`, ranked below. Multi-system is never waived.
4. **A result is a route, not evidence.** Confirm via meta before opening an artifact.
5. **Never conclude "not found" after one miss** — run the no-match flow.

## Flow
1. Query a short concept / id / path fragment. `--limit` by intent: known doc 3–5 (or `--mode id`) · known topic 8–10 · exploratory 15–20. Don't shrink `--limit` to save tokens. `--full` only for content checks.
2. Score-gap: clear gap (27/23→12) → stop. Flat/low → widen or sharpen. Near-duplicate hits → refine, don't page. "N more not shown" → may page with `--excludes`; never crawl the whole index or page just to find rank 1.
3. Rerank yourself: pick 2–4 candidates, `wiki_meta.py --view` each. Score-floor candidates → meta only, log "low-confidence skip".
4. Open an artifact only if the meta is not enough:
   - All candidates in ONE turn; sequential only if one depends on another.
   - Sections, not files: `grep -n` → `sed -n 'a,bp'` (±20 lines), guided by Source-Specific Hints. Whole file only if < 3000 chars.
5. All nodes of a kind → `--query <broad> --source-type function|table`. Object nodes share the index; no `--kind`.
6. Mapping/coverage/impact only: include every declared `x:` edge, justify any exclusion; for each undeclared reference in an artifact body, run `lookup --query <ref> --limit 5`.
7. Authoring/reviewing: full-read the Tier-1 docs; check cited files/§ resolve · no internal or RD↔BD contradiction (e.g. VAL IDs) · every VAL traces to a BR/FR · API↔DB names match · no TBD / version-skew.

Edges: `x:reads`/`x:writes` function↔table · `x:calls` function→function · `x:part_of` table FK · `represents`/`companion_requirement` one function's RD/BD/FUNC set · `system_foundation` OVERALL/CRUD base.

## Nav page — fallback (opt-in)
Only if `.ai-work/wiki/overview/WIKI_NAV*` exists. Lookup always runs first. Use nav only when:
- lookup gives 0 hits, or the hits don't match once opened, or top score < 15 again after retrying other vocabulary; or
- the question asks to list all docs ("which documents…") — lookup truncates, nav doesn't; grep nav even after a lookup hit.

`grep -l "<kw>" .ai-work/wiki/overview/WIKI_NAV*` finds the branch; `grep -h` returns the `source_id` + path lines. Don't `cat` it. Don't `ls` to check it exists — a missing-file error means no nav page.
- Trust the page's coverage count.
- No grep hit = not in the registered wiki → record it and STOP. Don't go raw (rule 3).
- Don't re-lookup (`lookup`/`--view`) a source_id the page already gave with a path.
- Don't chase an artifact's self-citations with escalating lookups when nav doesn't list them.
- This governs tool order only: still open artifacts and read their §Related documents.

## No-match flow
1. Retry `--mode tokens`.
2. `--mode catalog --system S [--source-type T]`: pick candidates from the catalog yourself. Also when top score < 15 or the query's vocabulary differs from the doc's. Mandatory before any raw step.
3. Nav page, if present (above). No hit there = conclusive "not in the registered wiki".
4. Raw only with `--authorized` (rule 3). Dirs: `.ai-work/wiki/reference/document_search_guidelines.md` (see its case matrix). None listed → ask HUMAN, then record them there. Registered hits exist but none match → `--include-raw always` (on-empty won't fire). Found raw → use it; register later via `/aiws-wiki build-meta`.
5. No authorization → stop after step 3: report "not in the registered wiki" and offer a raw search.

## Multi-input tasks (pre-flight, review, authoring)
- Plan 3–5 queries up front, `--limit 5` each.
- Budget ≈1 call per input (+1 `--relations`). Past ≈2× → stop; use the reading kit or ask HUMAN.
- Trip-wire (over budget, or escalating tokens/catalog → raw): immediately append a `retrieval_improvement` capture to `08_capture_inbox.jsonl` — intent, queries tried, call count, winning query, how to need fewer calls; tag MP1–MP7 from `.ai-work/procedural/lookup_miss_patterns.md`. "assessed-no-reuse because X" is allowed.

## Report
`source_id` + path + one line on why it matters. Don't copy document content; quote one sentence only if the wording itself was asked.

An AIP step or HUMAN may override `--limit` / `--mode` / `--full`.
