# aiws-wiki — operation: lookup

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Fast, grep-friendly lookup of source artifacts via the Wiki Source Index.
Use this before opening raw artifacts so you pick the right source first.

## Tool
`.ai-work/tooling/lookup_wiki_source.py`

### Examples
```
# lexical search (default)
python .ai-work/tooling/lookup_wiki_source.py --query "manufacturing order"

# exact id
python .ai-work/tooling/lookup_wiki_source.py --query SRC-FUNC-MO-UPDATE --mode id

# path-token match
python .ai-work/tooling/lookup_wiki_source.py --query "inventory/update" --mode path

# default output is slim (1 line/result, routing fields only) — keep recall high, low cost
python .ai-work/tooling/lookup_wiki_source.py --query "booking" --limit 20

# verbose: full multi-line records (summary / authority / representation inline) — for content verification
python .ai-work/tooling/lookup_wiki_source.py --query "booking" --limit 5 --full

# continue past a truncated result set (skip already-checked ids)
python .ai-work/tooling/lookup_wiki_source.py --query "booking" --excludes "SRC-A,SRC-B"
```

## Scope & raw search (CR-AIWS-2026-06-052)

- **Default scope = `project,aiws`** (registered project + AIWS indices). A bare `--query` searches exactly those. `local` is rule-#11-gated — opt-in only via `--scope project,local --authorized human` (after a HUMAN authorizes local-wiki search). `--scope all` = `project,local,aiws` (also needs `--authorized`).
- **Raw (un-registered) search is authorization-gated + never silent.** `--include-raw {off|on-empty|always}` (default `off`) Globs/greps the project dirs listed in `document_search_guidelines.md`; it **REQUIRES** `--authorized {human|aip|agent-rule}`. The `on-empty` fallback fires only for an **object** lookup (`--lookup-mode object`) that returns 0 registered hits. Absent `--authorized` (any raw, or scope beyond `project,aiws`) → the tool **refuses (rc≠0)**: STOP and ask HUMAN. Raw hits are labelled `unregistered:` and ranked below registered results.
- Multi-system (rule #12) is orthogonal and not waived by a raw/AIP grant — `multi_system:true` still hard-requires `--system`/`--all-systems`.

## Search orchestration — match need → tool

| Need | Shape | Tool |
|---|---|---|
| A doc/concept (no id yet) | FIND | `lookup --query X` |
| All nodes of a kind (every function / table) | ENUMERATE | `lookup --query <broad> --source-type function\|table` |
| What a node relates to / who depends on it | TRAVERSE | `wiki_relations --relations <id>` |

**Chain rule:** `wiki_relations` needs a `source_id` (an output of `lookup`) — FIND/ENUMERATE first, or `lookup --mode id` (`SRC-FUNC-Fxx`, `SRC-TABLE-<NAME>`). **Pick edges by need:** `x:reads`/`x:writes` = function↔table; `x:calls` = function→function; `x:part_of` = table FK; `represents`/`companion_requirement` = the RD/BD/FUNC set of one function; `system_foundation` = OVERALL/CRUD baseline.
❌ Don't `Read` the whole `index.jsonl`/`relations.jsonl` to enumerate — use `--source-type` / `wiki_relations` / grep (≈2× cheaper).

## Flow
1. Form a short query using a concept / identifier / path fragment.
2. Run the tool. It returns ranked entries with pointers to meta + artifact.
3. **Read the meta via the value-add reader** — `python .ai-work/tooling/wiki_meta.py --view <source_id>` — NOT by
   opening the whole meta file. It prints the orientation value-add (Summary / Source-Specific Hints / Cautions /
   a Related Sources **signal** — out-edge count+types, NOT the full edges) and SKIPS what you already saw at lookup
   (Lookup Keys / Knowledge Targets). The Related Sources signal is **out-only** — for the full out+in (reverse /
   impact) picture run `wiki_relations.py --relations` (step 4); don't treat the signal as "all relations". Don't
   re-read discovery fields.
4. **Impact / reverse (opt-in, one-hop):** if the task needs "who points AT / who calls X / what feeds this", run
   `python .ai-work/tooling/wiki_relations.py --relations <source_id>` (out-edges + IN-edges).
   - **Mapping relationships/coverage (not finding one route):** the edge set IS the deliverable — put EVERY
     declared `x:`-edge into the answer and *justify* any exclusion inline; don't silently drop a seen edge as
     "out of scope". A seen-then-dropped edge is a recurring under-recall — distinct from a missing-edge coverage
     gap (fix the latter in the meta's Related Sources, not here).
5. Open the `artifact_locator` only if the meta is not enough — and use the meta's **Source-Specific Hints** to open
   the RIGHT section, not the whole file.
   - **Mapping/coverage/impact tasks — recover undeclared references:** after reading the artifact, for each
     reference it names in its **body** that is NOT a declared `## Related Sources` edge (a doc it cites but doesn't
     link — e.g. message-list / code-master-definition docs), run a separate `lookup --query <ref> --limit 5`.
     `wiki_relations` only returns declared edges, so these never surface via TRAVERSE — skipping them silently
     drops needed docs. (Mapping/coverage/impact only — not single-route FIND.)

## Choosing `--limit` / `--slim` (intent-aware)

Slim output is the **default** (1 line/result: score, source_id, title, source_type, meta_locator)
— it keeps recall high at low cost (~−81% text / −93% json vs verbose). The cost driver is
**fields-per-result**, not result count: don't shrink `--limit` to save tokens (you drop
foundational / downstream docs). Pass **`--full`** only when you need the inline summary /
authority / representation fields (e.g. a content-verification read).

| Intent | `--limit` | How to query |
|---|---|---|
| Targeted (you know the doc) | 3–5 | Lead with a distinctive token (F-code, doc id) or `--mode id` |
| Intermediate (know topic, not boundary) | 8–10 | Tier-2 / downstream docs rank ~9–15, so 5 is too narrow |
| Exploratory (unsure what you need) | 15–20 | Slim default keeps recall high; widen the limit, don't add fields |

**Score-gap heuristic:** a clear gap (e.g. 27 / 23 → 12) = confident hit, stop. A flat / floor
distribution (many low scores) = widen the limit or sharpen the query.
If the tool prints "… N more match(es) not shown", `--limit` clipped the set (`has_more`) — recall
isn't exhausted. When current hits look insufficient, you **may** re-run with
`--excludes <ids already checked>` to page the next batch (or raise `--limit`). Continuing is your
reasoning call — don't crawl the whole index by default.
An AIP step or HUMAN may override `--limit` / `--mode` / `--full` per use-case.

## Routing, not verification

A lookup result is a **candidate route**, not evidence. The index/meta is an identification
layer, not a content copy — errors that live in the document body (broken cross-refs, internal
contradictions, traceability gaps, version-skew) are invisible to lookup alone. When **authoring
or reviewing** (not merely locating), full-read the Tier-1 docs the work traces to and run:

```
□ Every cited filename/§ resolves to a real file/section?
□ Any internal or RD↔BD contradiction (e.g. VAL IDs misnumbered)?
□ Every VAL traces to a BR/FR? Tables referenced in §9 exist in the data model?
□ Field names consistent API↔DB? Any leftover TBD / version-skew?
```

Confidence gate: candidates at the score floor (low overlap) → meta-only, log a
"low-confidence skip"; do not full-read them.

## No-match escalation (MANDATORY)

When the tool returns `(no matches)` (exit code 1), **do not stop**. The index
may be incomplete — the source may exist as a raw artifact not yet registered.

```
Step 1 — Retry token mode (if first attempt was lexical):
  py .ai-work/tooling/lookup_wiki_source.py --query <keyword> --mode tokens
  (mode name per CR-2026-07-007 B4 — 'semantic' is a deprecated alias of the same matching;
   queries VN có dấu/không dấu đều match — two-way diacritic fold B1; aliases
   profiles/query_aliases.yml tự expand B2)

Step 1b — Catalog-scan (CR-2026-07-007 B6 — concept recall, ZERO-dep, registered-only):
  py .ai-work/tooling/lookup_wiki_source.py --mode catalog --system <sys> [--source-type ...]
  → đọc slim catalog đã filter (vài nghìn tokens) → TỰ CHỌN candidates khớp intent
  → mở meta qua --mode id <source_id>. Dùng khi: 0-hit sau Step 1, HOẶC top score <15
  (tool tự in note "fragile"), HOẶC query là concept khác từ vựng với keys.
  Đây là bước BẮT BUỘC trước khi cân nhắc raw (Step 2) — raw vẫn CR-052-gated.

Step 2 — Raw search:
  a. Open .ai-work/wiki/reference/document_search_guidelines.md
     → section "Raw search fallback — project artifact directories"
     → lists artifact dirs for this project
  b. Glob **/*.md in those dirs, filter by filename
  c. Grep <keyword> in artifact dirs if filename search is insufficient

Step 3 — If no artifact dirs documented in guidelines:
  → Ask HUMAN: "Index miss for '<keyword>'. Which directories hold raw artifacts?"
  → After answer: update document_search_guidelines.md with the info

Step 4 — If found in raw:
  a. Read the artifact directly for this task
  b. Register it later: /aiws-wiki build-meta

Step 5 — Only report "no relevant documents" if steps 1–4 all miss.
```

**2-stage retrieve → rerank (CR-2026-07-007 B5 — codify hành vi chuẩn):** với query rộng/concept,
stage 1 = 1 call slim (`--limit 15-20`, hoặc `--mode catalog` khi lexical yếu) lấy candidate set;
stage 2 = AI đọc slim lines và RERANK theo intent (chọn 2-4 candidates mở meta) — KHÔNG page thêm
call để "tìm đúng rank 1". Precision đến từ rerank của AI, recall đến từ stage-1 đủ rộng.
Trip-wire capture (mục 2b §Search-plan) vẫn áp khi escalate.

❌ **Never silently conclude "not found" after a single index miss.**

**Grep-fallback case matrix (CR-AIWS-2026-07-001 Q4):** which case uses which mechanism (A object-miss ·
B concept-research · C runtime artifacts · D code surfaces · E local knowledge) is tabulated in
`.ai-work/wiki/reference/document_search_guidelines.md` → "Grep-fallback case matrix". It stays inside the
CR-052 authorization frame (no new grant). Note **case-A P7 escalation**: when registered hits exist but
none matches the target name/id, `--include-raw on-empty` will NOT fire — escalate to `--include-raw always`
under the same authorization.

## Search-plan discipline (CR-AIWS-2026-07-003 E4)

For a multi-input task (aiws-aip create pre-flight, a review/authoring AIP), plan before firing calls:

1. **Plan 3–5 queries first** (one per input/keyword-group) — the mode-C pattern of `aiws-wiki test-lookup`.
   Prefer `--limit 5` per query for pre-flight scoping (raise only when a query is genuinely broad).
2. **Budget** ~1 call per input (+1 `wiki_relations --relations` when related docs are needed — it returns
   many neighbours in one call, replacing N per-doc lookups). If a task's routing exceeds ~2× its input
   count, stop and either use a reading-kit digest or ask HUMAN — the queries are too diffuse.
2b. **Trip-wire ⇒ capture BẮT BUỘC (CR-AIWS-2026-07-008 C1):** khi budget trip-wire nổ (calls > ~2× inputs)
   hoặc phải escalate mode (semantic/tokens → raw): PHẢI append 1 capture `retrieval_improvement` vào
   `08_capture_inbox.jsonl` NGAY — content: intent, chuỗi queries đã thử, call count, query trúng cuối
   (nếu có), đề xuất cách tìm ít call hơn (key/alias/digest); vocabulary = mã MP1–MP7
   (`.ai-work/procedural/lookup_miss_patterns.md`). Record được phép kết luận "assessed-no-reuse vì X"
   → discard-triage ngay (giữ noise filter). KHÔNG skip vì "task vẫn xong" — sự kiện trip-wire chính là data.
3. **Stop rules:** an id/exact top hit with a clear score gap ⇒ stop (don't widen); repeated near-duplicate
   hits ⇒ the query is generic, refine it rather than paging.

**Reading-kit / digest (CR-AIWS-2026-07-003 E2):** for a review/authoring task on a function or object,
one call assembles the whole doc set (RD↔BD↔DD chain, →OVERALL, chunked-section ranges) instead of N
per-doc lookups — `py .ai-work/tooling/build_reading_kit.py --query "<task>" --system <sys>` (or
`--function F02`). It seeds via the shared scorer and expands one hop over relations edges, with a
naming-convention (F-code) fallback when the corpus has no edges. Prefer it over firing N lookups when the
task is a known shape.

## Rules
- **Multi-system (CR-AIWS-2026-06-017):** in a `multi_system: true` project, `lookup_wiki_source.py` ERRORS (rc≠0) if `--system <id>`/`--all-systems` is missing. On that error, **STOP and ASK the HUMAN** for the active system — never ignore it, never auto-set/guess a system; carry the chosen `--system` through the task. Never merge specs across systems.
- do not bypass the index by grepping the whole repo first (index-first)
- confirm relevance via meta before opening the artifact
- index miss → escalate per no-match protocol above; never silently give up
- **Object nodes** (`node_kind=object`, `__OBJECT__`) live in the SAME index and are found by the SAME lookup — no `--kind` flag (DP7). "Everything about X / who calls X" = `wiki_relations.py --relations <source_id>` (out+IN edges), NOT lookup.
