# Document Search Guidelines

> **TEMPLATE — copy to `.ai-work/wiki/reference/document_search_guidelines.md` and fill in per project.**
> This is a per-project **curated reading guide**, NOT a searchable index (the index is `.ai-work/wiki_sources/index.jsonl` — do not duplicate it here). It lists the foundational, cross-cutting sources that lexical lookup alone does not surface reliably, grouped by task type, plus a raw-search fallback directory map. The no-match **escalation methodology** lives in `WIKI_FIRST_RUNTIME_GUIDANCE.md` and the `aiws-wiki lookup` SKILL — **do not restate the protocol here**; this file holds only the project-specific DATA those point at.
>
> Replace every `<...>` placeholder; remove unused rows/sections; keep the `## Raw search fallback — project artifact directories` heading **verbatim** (tooling + skills open it by name).

Curated reading guide for foundational, cross-cutting sources that lexical
lookup alone does not surface reliably. Each entry lists when to open it, what
you get, and how to navigate to it. Use this guide **before** writing,
reviewing, or implementing — especially when the task crosses multiple
functions or touches shared concepts.

---

## How to use

1. Find the task type that matches your work below.
2. Open the listed sources (use `lookup_wiki_source.py --query <source-id>` to
   get the artifact path).
3. After opening, navigate to the specific chapter named in the hints.

---

## By task type

<!-- GENERATED:BEGIN — sau khi project chạy /aiws-wiki build-overview, vùng này trỏ tới các trang generated
WIKI_SEARCH_GUIDE_<system>.md (bản enumerable maintained — CR-AIWS-2026-07-010 E5); khung tay ngoài vùng CR-gated -->
<!-- GENERATED:END -->


<!-- Fill per project. One sub-section per recurring task type; each lists the
     foundational sources (by source-id) + what to take from each. Add a
     "Why these aren't found by lexical search" note where it helps. Common task
     types: writing/reviewing a design · review gate · implementing a function ·
     onboarding/orientation · working with the AI Work System tooling/wiki. -->

### A. <task type — e.g. writing or reviewing a function-level design>

| Source | What you need from it |
|---|---|
| `<SRC-...>` | `<sections / shared concepts to read>` |

**Why these aren't found by lexical search**: `<short note — e.g. the OVERALL
doc holds shared validation / data model that function files reference but
don't repeat>`

### B. <task type — e.g. reviewing an artifact (review gate)>

| Source | What you need from it |
|---|---|
| `<SRC-...>` | `<checklist / criteria / dimensions>` |

### C. <task type — e.g. implementing a function>

| Source | What you need from it |
|---|---|
| `<SRC-...>` | `<data model / cross-function dependencies / system-level rules>` |

<!-- Add D, E, ... as the project needs; remove sections you don't use. -->

---

## Raw search fallback — project artifact directories

When `lookup_wiki_source.py` returns `(no matches)`, the source may exist as a
raw artifact not yet registered in the index. Search these directories directly:

> **Authorization-gated (the CLAUDE.md wiki-source-search-scope rule, CR-AIWS-2026-06-052):** raw search
> is **never silent** — it needs an explicit authorization source (HUMAN / the active AIP's `allow_raw_search` /
> a standing agent rule). `lookup_wiki_source.py --include-raw on-empty --authorized <src> --lookup-mode object`
> Globs/greps exactly the dirs in this table after a registered-index miss; absent authorization → halt and ask.

| Directory | Contents |
|---|---|
| `.ai-work/truth/canonical/methodology/` | AIWS methodology canonical (shipped on every install; the `index.aiws.jsonl` sources resolve here) |
| `<path/to/dir>/` | `<file glob — e.g. RD_*.md>` |

**Raw search procedure** (brief — the canonical protocol is in
`WIKI_FIRST_RUNTIME_GUIDANCE.md` / the `aiws-wiki lookup` SKILL):

1. Retry lookup with `--mode semantic` first.
2. If still no match: Glob `**/*.md` in the directories above, filter by filename.
3. Grep for the keyword inside artifact files if filename search is insufficient.
4. If found raw: read the artifact directly for this task; register it later via
   `/aiws-wiki build-meta`.
5. If no artifact dirs are listed here or the project structure differs:
   **ask HUMAN** for the correct locations, then update this table.

---

## Grep-fallback case matrix (CR-AIWS-2026-07-001 Q4 — inside the CR-052 authorization frame)

When to leave the registered lookup and grep directly. **This does NOT loosen CR-AIWS-2026-06-052** —
every raw case still needs an authorization source (HUMAN / the active AIP's `allow_raw_search` / a
standing agent rule). It only names *which case uses which mechanism*, and clarifies that cases C/D are
outside the wiki HARD GATE entirely (they are not canonical-artifact lookups).

| Case | Trigger | Mechanism | Authorization | Scope | Audit |
|---|---|---|---|---|---|
| **A. Object miss** (know the artifact, suspect unregistered) | 0 registered hits with `--lookup-mode object`, **or (P7) hits exist but none match the target name/id** | `lookup_wiki_source.py --include-raw on-empty`\|`always --authorized aip` — escalate to `always` on the P7 near-miss (`on-empty` won't fire when plausible-but-wrong hits exist) | AIP step `allow_raw_search: true` OR HUMAN | dirs table above — **must cover the project's corpus roots** (a missing dir stays invisible even under `always`) | tool labels `unregistered:`; reusable → capture `retrieval_gap` + register |
| **B. Concept research** (unsure it exists) | semantic retry still poor/0 | `--include-raw always --authorized human`, or manual Grep over the dirs table | HUMAN per-request (not AIP-pre-authorized) | dirs table | findings note; capture if a reusable source is found |
| **C. Runtime/task artifacts** (AIP records, workspace findings — **by design NOT wiki sources**) | always | Glob/Grep directly | no wiki-gate (outside the HARD GATE) — but never `temp/`, `.ai-work/logs/`, `index.local.jsonl` | `.ai-work/aip/`, own `.ai-work/workspaces/` | — |
| **D. Code surfaces** (tooling/skills) | always | Glob/Grep/Read directly | no wiki-gate (code is not a canonical artifact) | project | — |
| **E. Local knowledge** (outside repo) | need an external source | `--scope project,local --authorized human` via index; raw-local ONLY per HUMAN-named file | HUMAN explicit | index.local route | findings note |

> Cases C/D are a **clarification** (avoid a needless halt-and-ask for non-wiki lookups), not a new grant.

---

## Maintenance note

- When registering a new source whose `intended_ai_use` contains
  `design_context` or `review_reference`, consider adding it above under the relevant task type.
- When the project adds new artifact directories, update the table in
  **Raw search fallback** above.
