# aiws-wiki — operation: build-meta

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Produce a small, memory-friendly Wiki Source Meta so Wiki authors can look
up + orient before opening the full source artifact.

## Design notes (CR-022/024/025/043)
- **Lookup-key noise control (CR-043).** Generic noise is dropped via universal built-in stopword sets (in `_common.py`) ∪ per-project config: sibling `project_stopwords.yml` (project-wide `stopwords:`) + a profile's optional `extra_stopwords:` (per source type) — single-token, case-insensitive; multi-word curated keys never filtered. HTML / `ui_mockup` sources are `strip_html`'d before tokenizing. A profile's `related_sources.emit_scaffold: false` is honored (no empty `## Related Sources` scaffold re-emitted).
- **Lean meta = AI orientation surface.** Tool emits Summary / Knowledge Targets / Lookup Keys / Source-Specific Hints
  (+ a `## Related Sources` scaffold). NO `## Profile Mapping` (mirrored frontmatter `profile_id` — dropped). Keep every
  section terse + signal-dense; AI later reads the meta via `python .ai-work/tooling/wiki_meta.py --view <id>` (not the whole file).
- **Resolve `## Related Sources`** (typed roles + optional `[confidence]`): fill real `source_id`s, delete unused role
  lines, or delete the section if none. Declare each relationship ONCE (canonical direction; reverse via query).
- **After writing/resolving metas → rebuild the relations projection:** `python .ai-work/tooling/build_relations.py`
  (relations.jsonl is rebuilt-from-metas — never hand-edit).

## Object node — hand-author only
A Knowledge Object (a logical entity: function/screen/api/batch/table/module/concept) is a `node_kind: object` meta treated like a source artifact. Tools do NOT generate it — hand-author with the **Write tool** (no BOM); `build_wiki_source_meta.py` stays artifact-only.
- **When:** for each reusable knowledge object you detect in the artifact, check whether it already has its own object meta. **Has one →** add the `represented_by` edge (this artifact) + every newly-found relation (`x:`) edge to that meta. **None →** propose a new object meta carrying those edges (you suggest; a human authors it). Skip the node only for a degenerate one-off doc↔doc link, where a single `companion_design` edge on the artifact suffices.
- **Frontmatter:** `node_kind: object` · `artifact_locator: __OBJECT__` · `source_type: <object kind>` (rides open-union per §3bis.1 — do NOT omit) · `profile_id: knowledge_object` (shared object profile, CR-AIWS-2026-06-004) · `source_id` = family prefix (`SRC-FUNC-`/`SRC-SCREEN-`/`SRC-API-`/`SRC-BATCH-`/`SRC-TABLE-`/`SRC-MOD-`/`SRC-CPT-`). Do NOT add `object_id`/`source_anchor`/`expansion_links`/`canonical_object_refs`. `updated_at`: UTC ISO 8601 write-time (sourceless — CR-AIWS-2026-06-024; source-backed metas built by the tool auto-stamp the source file mtime).
- **Body (never empty):** a real `## Summary` (a degenerate summary is an ERROR for objects) + `## Related Sources` with **≥1 out-edge** — `represented_by` the docs that describe it (RD/BD/DD/Testcase); domain edges via `x:` (`x:calls`, `x:part_of`) — navigation-only, never `contains`. Pointer-only — no aggregation heading.
- **Identity:** `source_id` frozen once referenced (rename≠re-key → old = alias); bare code (`F03`) + vi/ja/en names go in `## Lookup Keys`. "everything about X" = `wiki_relations.py --relations <source_id>`, NOT lookup.
- **After authoring:** `build_wiki_source_index.py` + `build_relations.py` + `lint_wiki.py --sources-only`.

## Object + relation capture — proactive, suggest-only
Lúc đọc artifact để derive Summary/Knowledge Targets/Lookup Keys (Step 0), AI **đồng thời**:
1. Nhận biết các **object** artifact mô tả (mọi loại; `source_id` family-prefix, reuse `key_objects_and_terms.objects[]`) → quan hệ **representation**: object `represented_by` artifact này.
2. Nhận biết quan hệ **object↔object** (domain) artifact hàm ý → `x:` type (`x:calls`/`x:part_of`/`x:reads`/…), **kể cả quan hệ suy luận** không nêu rõ, kèm confidence `asserted|inferred|candidate`.

Capture này **VÔ ĐIỀU KIỆN** — chạy cho mọi reusable object artifact mô tả, **bất kể** object/artifact đã có meta hay chưa. Artifact meta liên quan là **trigger** (nó thành cạnh `represented_by`), KHÔNG bao giờ là lý do skip. Quyết định "single-artifact host / `companion_design`" chỉ chi phối việc author một object **node** riêng hay gộp vào một cạnh `companion_design` — KHÔNG chi phối việc có capture hay không.

De-dup guard (KHÔNG phải coverage test): lookup xem quan hệ đã khai MỘT lần (chiều canonical) trên object node chưa (reverse = `wiki_relations.py --relations`, không chép) — **capture kể cả khi object chưa có meta**. Ghi nhận **HẾT** mọi cạnh artifact làm lộ (cạnh `represented_by` + **MỌI** cạnh `x:` domain, kể cả quan hệ suy luận kèm confidence) — đừng dừng ở cạnh hiển nhiên đầu tiên. Chưa khai → append candidate `object_relation_capture` (identity + `represented_by` + `x:` edges + evidence + confidence) + **đề xuất HUMAN** author/cập nhật MỘT object-node meta với các edges đó. AI **KHÔNG** tự tạo object meta; `build_wiki_source_meta.py` artifact-only. Lớp documentary `## Related Sources` 9-role của artifact GIỮ NGUYÊN. Noise-guard: chỉ object/quan hệ reusable. Chi tiết: `capture_triggers/object_relation_capture.md`.

## Traceability (object node + capture)
- Object node = hand-author-only + necessity test → CR-AIWS-2026-05-023 DP6; restated Knowledge_Object_Model_Spec §3bis.5.
  **Ngoại lệ hẹp (KOM Spec v0.4 §3bis.5(7), CR-AIWS-2026-08-030):** một build route deterministic **đã được PO duyệt bằng CR** MAY instantiate object meta (2 điều kiện bắt buộc). AI tự tạo theo phán đoán vẫn CẤM.
- Capture trigger = #19 `object_relation_capture` → `wiki_candidate_capture_playbook.md` (Triggers table) + `capture_triggers/object_relation_capture.md`.
- Forbidden frontmatter keys (danh sách ở mục Frontmatter trên) → CR-023 INV-2; retired shapes — xem `Knowledge_Object_Model_Spec_MVP` §8.
- Never-empty body / ≥1 out-edge → INV-4. · Pointer-only, no aggregation → DP5 / INV-3 (SHAPE 1).
- Tools never instantiate object metas; AI suggests, HUMAN authors → DP6 / INV-8 / safety rule #7.

## Tool
`.ai-work/tooling/build_wiki_source_meta.py`

### Example (auto-extract from profile)
```
py .ai-work/tooling/build_wiki_source_meta.py \
  --artifact path/to/BD_F02_SearchRoom.md \
  --source-id SRC-BD-F02-SEARCH-ROOM \
  --source-type basic_design \
  --profile .ai-work/wiki_sources/profiles/basic_design.yml \
  --title "Basic Design — F02 Search Room"
```

### Example (AI-read override — full semantic derivation)
Use when the tool cannot auto-extract a quality summary/targets (e.g., novel
format, mismatched profile), or after reading the full artifact:
```
py .ai-work/tooling/build_wiki_source_meta.py \
  --artifact path/to/artifact.md \
  --source-id SRC-... \
  --source-type basic_design \
  --profile .ai-work/wiki_sources/profiles/basic_design.yml \
  --title "..." \
  --summary "version: v1.1. <§1 Purpose content, enriched with function ID/name if not already present>." \
  --knowledge-targets "screen_spec,validation_rule,data_crud_spec"
```

## Flow

### Step 0 — Semantic derivation (when reading the full artifact)
Before running the tool, derive the following from the artifact content:

| Field | How to derive |
|---|---|
| `--summary` | Content from the PMP `summary_extraction.target_sections` (typically Purpose / Overview / Summary section), enriched with doc metadata from the artifact header (version, function name/ID). **Do NOT pull from other sections** — screen items, validations, CRUD spec, and screen transitions belong in Knowledge Targets and Lookup Keys, not here. **When auto-extracted summary is thin:** read the FULL content of the target section (prose + bullet list) — bullet lists within Purpose/Overview/Summary are valid sources. Write `--summary` from that content only. Never expand beyond `summary_extraction.target_sections`. **When target section is not found in the document:** read the full artifact, then derive a concise summary from the overall content — this is the only case where full-document reading is permitted for summary derivation. |
| `--knowledge-targets` | Pick from the profile's `knowledge_targets` list. Add artifact-specific targets not in the profile if needed. |
| `--lookup-keys` | T1: IDs extracted from text (VAL-F02-01, FR-F02-01, etc.). T2: domain terms (screen names, entity names, business terms). |

Skip Step 0 and use profile auto-extraction when:
- The artifact matches the profile's `format_signature` (the tool will not show a mismatch WARNING)
- Auto-extracted summary (from `target_sections`) is acceptable — even a short Purpose-only sentence is acceptable; enrich only with version/ID prefix if missing

If the tool shows a **format mismatch WARNING** (option a/b/c/d prompt):
- **Option (a)** — Create a new profile for this format variant. Best when multiple files share this format.
- **Option (b)** — Use a different existing profile. Best when another profile already matches.
- **Option (c)** — Proceed relaxed (requires `--summary`, `--knowledge-targets`). Best one-off case.
- **Option (d)** — Abort and investigate.

### Step 1 — Pick or author a profile
Select from `.ai-work/wiki_sources/profiles/`. If no profile matches the
artifact format, create one (see option (a) above).

### Step 2 — Run the tool
The tool writes `.ai-work/wiki_sources/meta/<source-id>.md` with YAML
frontmatter + sections. Review the output — enrich manually if auto-extracted content is thin.

**Required sections — lint ERRORs on any missing section:**

| Section | Required | Expected content |
|---|---|---|
| `## Summary` | ✓ | 1–3 sentences; sourced from `summary_extraction.target_sections` in PMP |
| `## Knowledge Targets` | ✓ | Bullet list of knowledge types (e.g., `- screen_spec`) |
| `## Lookup Keys` | ✓ | Bullet list of IDs + domain terms; index uses up to 30 |
| `## Source-Specific Hints` | optional | Auto-generated headings — remove if noise |

After reviewing the generated meta, confirm all 3 required sections exist before moving to Step 3.

### Step 3 — Rebuild the index
```
py .ai-work/tooling/build_wiki_source_index.py
```

### Step 4 — Lint
```
py .ai-work/tooling/lint_wiki.py --sources-only
```

### Step 5 — Present detected objects + relations for confirm (suggest-only)
Surface what §"Object + relation capture" found — do not leave it implicit. Present TWO inline tables to HUMAN **and**
ensure the `object_relation_capture` candidate is appended to `08_capture_inbox.jsonl` (both, not either/or):
- **Detected Objects** — kind · proposed `source_id` · name (vi/ja/en) · `represented_by` (this artifact) · existing object meta? · suggested action (author new / augment existing).
- **Discovered Relations** — from · edge (`represented_by`/`x:…`) · to · confidence (asserted/inferred/candidate) · evidence.
Then ask HUMAN to confirm authoring/updating the object node(s). You present + append the candidate; a HUMAN authors —
never auto-author an object meta (DP6/INV-8). If none detected, state "no reusable objects/relations detected" explicitly.
Detail: `capture_triggers/object_relation_capture.md`.

## Rules
- **Multi-system (CR-AIWS-2026-06-017 / -058):** in a `multi_system: true` project (`.ai-work/project_profile.yml`), set the meta's `system:` non-interactively via `build_wiki_source_meta.py --system <id>` (validated against `project_profile.systems`) **or** `--common` (system-agnostic → emit NO `system:` key, the "common = absent" convention); the tool **ERRORS if neither is given** (mirror the lookup gate, no silent default). When working interactively, PROMPT the HUMAN for the same choice; never guess/auto-set. `--mode refresh` **preserves** an existing `system:` when no flag is passed (never silently drops it). Single-system project → flags ignored, no prompt.
- do NOT inline the full source content into the meta
- do NOT rewrite the official wiki entry
- meta remains lighter than artifact, richer than index
- always confirm with HUMAN if format mismatch cannot be resolved by profile;
  never silently create a low-quality meta
- **[Windows] Always use Write tool, never Edit tool** — The Edit tool (VS Code / IDE extension) adds
  a UTF-8 BOM when saving files on Windows. A BOM causes `parse_frontmatter` to return `{}`,
  silently producing a malformed index entry (empty `artifact_locator`, wrong `title`).
  Always create and modify meta files using the **Write tool** only.
- **No trailing tool-call/markup junk (CR-AIWS-2026-06-020)** — write metas clean; never leave stray
  `</invoke>`/`</content>`/scaffold artifacts after the last section. They parse-harmlessly into the index;
  `lint_wiki` now WARNs (`meta_trailing_junk`) on them.
- **Resolve the Related Sources scaffold (CR-017)** — The tool now EMITS a `## Related Sources`
  section after `## Profile Mapping`: an enum comment + one `- **<SRC-id: TODO>** — role: <role>`
  line per role declared in the profile/PMP `related_sources.expected_roles` (flat list) + a TODO
  marker. After the tool run, RESOLVE it: fill a real `SRC-<id>` into each `<SRC-id: TODO>` slot you
  use (+ why/when to open), delete role lines you don't need, or delete the whole section if the
  artifact has no relationships. Pass `--no-related-sources` to skip emission entirely.
  ```
  ## Related Sources
  - **SRC-<id>** — role: upstream_input — <why/when to open>
  ```
  Valid roles: `upstream_input` · `downstream_navigation` · `downstream_target` · `triggered_flow` ·
  `system_foundation` · `companion_design` · `companion_requirement` · `output_template` · `related`.
  Declare a source_type's typical roles in its profile: `related_sources.expected_roles:` (flat list).
  Section is NOT projected into `index.jsonl`. Declare each relationship ONCE in its canonical direction (query the reverse via `wiki_relations`) — do NOT declare both ends (superseded by canonical-direction-once, `Knowledge_Expansion_Link_Spec_MVP.md` §6A).
  On `--mode refresh` the tool PRESERVES an already-resolved section (re-emits only the unresolved scaffold).
  For a **chunked** source (H6 parent), refresh regenerates the ordered `contains` list from the current
  sections AND preserves the parent's hand-resolved non-`contains` edges (CR-AIWS-2026-07-021 IR-B —
  previously these were silently dropped on a chunked refresh; you no longer need to re-resolve parent
  edges after the last refresh). Section children still carry only the `part_of` back-edge.
  `lint_wiki` WARNs if a `<SRC-id: TODO>` scaffold is left unresolved.
  **Basis note — objective + intent-blind (CR-06-002):** write each note so it serves review / authoring /
  understanding / impact alike — no "MUST READ", no "read when reviewing/designing", no vague "open when X changes":
  - dependency edge → `<who reads/writes whose data + direction>; coupling = <schema/fields/keys>; <what a change affects>`
  - skippable edge → `<what it is>; no data coupling`
  Keep `role:` accurate (priority signal). Full convention + worked example: `Knowledge_Expansion_Link_Spec_MVP.md` §4.4.
  `lint_wiki` WARNs (never errors) a data-flow edge left with a blank basis note (`relations_thin_basis`).

## Language source-code metas — Step-2 enrich (CR-AIWS-2026-06-048)

Language metas (Java now; TS/Python/COBOL later) come from dedicated **builders** (e.g.
`build_java_wiki_metas.py`), NOT this PMP/doc flow. Each = a canonical **Step 1** (facts → lean meta)
⊕ a project **Step 2 enrich** (project-owned, never shipped): a declarative `enrich:` block in the
project's profile (`lookup_key_patterns` = verbatim regex → extra lookup keys; `concept_keywords` =
signal → concept keys) + an optional code-hook `.ai-work/wiki_sources/enrich/<source_type>.py`
(`def enrich(facts, src, ctx) -> dict`). No `enrich:` + no hook → byte-identical Step-1 output; a hook
error degrades to declarative-only (never breaks the build). Schema + hook contract:
`wiki_source_profiles/README.md`.
