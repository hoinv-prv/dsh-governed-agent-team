# ASP COBOL Source Build Guide

**Status:** active · **Introduced by:** CR-AIWS-2026-08-026 · **Class:** operating guide (source build preset)
**Scope:** **Fujitsu ASP** COBOL — *not* COBOL in general. See §1.

Read this before the first build. It is not an API reference; it is the list of things that were measured the
hard way and that decide whether the output is trustworthy.

The preset turns a tree of ASP COBOL / control-language / file-definition sources into `wiki_source_meta`
files with resolved relations. It does one job and stops: it never writes `index.jsonl`, never registers its
own route, and never overwrites a field it does not own.

---

## 1. Why this says ASP and not COBOL

The engine is dialect-neutral; **this preset is not**. What makes it ASP is data, not code:

| Convention | Where it lives |
|---|---|
| `.CB/.COB/.CBL` (COBOL) · `.CL/.PRC` (control language) · `.FDG` (file definition) · `.SMD` · `.MFG` · `.DP1` · `.FFX` · `.OVD` | `file_type.by_extension` in the config |
| `CALL PGM-X.LIB` names the **object** library (where the program runs), never the source library | `resolve.library_hint: object_library` |
| System-command catalog (`DLTFILE`, `CRTFILE`, `CHGFILE`, `OVRPRTF`, `SORTD`, …) | `system_commands.catalog` in the config |
| Statement reading | `cobol_parser`, written against **ASP COBOL G 文法書 V13～** |

A different COBOL dialect (IBM z/OS, Micro Focus, GnuCOBOL) is therefore a **new preset** — its own profile,
config and route on the **same** engine — not a widening of this one. Nothing here has been measured on a
non-ASP corpus, and naming it `cobol_source` would have advertised coverage that does not exist.

---

## 2. The pieces, and which are yours

| Piece | Path | Owner |
|---|---|---|
| Engine | `.ai-work/tooling/cobol_wiki/` (17 modules) | AIWS |
| Parser | `.ai-work/tooling/cobol_parser/` (14 modules) | AIWS |
| Entry point | `.ai-work/tooling/build_cobol_wiki_metas.py` | AIWS |
| Profile | `wiki_sources/profiles/asp_cobol_source.yml` | shipped, then project-owned |
| **Config** | `.ai-work/asp_cobol_wiki.config.yml` | **yours** — copy the template and edit |
| System-command catalog | a CSV you point at | **yours** — vendor data, none is shipped |
| id overrides / per-file type map | CSVs you point at | **yours**, optional |

The config is validated before a single file is scanned. Malformed input stops the build with a pointed
message rather than producing thousands of wrong metas.

### The system-command catalog must be a CSV, and it must carry column 5

There are two ways to give the builder its command catalog, and **they are not interchangeable**:

```yaml
system_commands:
  catalog: [DLTFILE, CRTFILE, OVRPRTF]        # inline names only — NOT sufficient
  catalog_file: .ai-work/asp_syscmd.csv       # command,reading,english,category,doc_source_id
```

A system-command node stands for a command the platform supplies, so it has no source artifact and asserts no
outbound call of its own. Its **one** out-edge is `described_by`, pointing at the manual page that documents
the command — and that target comes from **column 5 (`doc_source_id`) of the CSV**. The inline `catalog:` form
cannot carry it.

AIWS requires every `node_kind=object` meta to declare at least one out-edge (INV-4, CR-023). So with the
inline form, **every** system-command node fails lint with `meta_object_no_outedge`. Measured while adopting
the preset: 5 of 5 nodes on the shipped fixture; switching to a CSV with column 5 took that to zero.

Column 5 references a meta the **project** registers (the vendor manual page). If those pages are not in your
wiki yet, register them first — otherwise the edge resolves to nothing and you trade one error for another
(`relations_edge_unresolvable`). The manual page is an ordinary artifact meta, *not* an object node: a
`described_by` edge pointing at an object node is rejected as an inverted representation edge.

### Two COBOL handlers — pick deliberately

`handlers.cobol` reads a **parse** and needs `cobol_parser` on the import path (it ships with the preset, so
this is the normal case). `handlers.cobol_regex` is the dependency-free fallback, selected in config:

```yaml
handlers:
  cobol: cobol_wiki.handlers.cobol_regex     # only where the parser cannot be installed
```

Measured on the originating corpus (Otsuka, 5467 COBOL files): the two disagree on 61 files and the **parse is
right on all 61**. The regex handler invents 64 references whose "name" is a keyword or a word inside a string
literal, loses the library on 7, misses 6 copybooks, and misses one program's `PROGRAM-ID` together with all
three of its file assignments. Those failures are **silent and plausible** — an invented reference looks
exactly like a real one downstream. Use the fallback only when you must, and record that you did.

---

## 3. Eleven findings, as operating rules

> **Attribution.** Every number in this section was measured on the **originating corpus** (the Otsuka COBOL
> Migration project), not on AIWS and not on yours. They are evidence that the preset was built against
> reality; they are **not** AIWS thresholds and must not be quoted as such.

**F1 — Resolution, not extraction, is where edges are lost.** Of 37 missing call edges measured there, 37 were
resolution failures and 0 were extraction failures. When recall is low, read `## Cautions` and the resolution
counters BEFORE touching a pattern.

**F2 — The library suffix names the OBJECT library.** `CALL PGM-X.LIB` says where the program RUNS from.
Trying it as a source library and then falling back to a name-only lookup moved recall from 99.3% to 100.0%.

**F3 — Two systems are independent corpora that look alike.** Resolution is system-scoped and not
configurable. A cross-system edge is meaningless even where it would "fix" a miss.

**F4 — Identity is the FILE name, not `PROGRAM-ID`.** Legacy sources disagree with themselves: a file declares
a neighbour's `PROGRAM-ID`. Preferring the declaration collides two real files onto one id.

**F5 — Object nodes carry a sentinel locator, not a path.** Anything deriving a name from `artifact_locator`
must special-case it; `Path(locator).stem` on the sentinel indexes every stub under the same wrong name.
Deriving a name by cutting an id at a fixed position has been wrong three separate times — prefer the meta's
own `system` / `library` / `program_id` fields.

**F6 — The encoding try-order decides the LABEL, not just the decode.** List the narrowest encoding first.
Renaming one tier dropped agreement with the reference from 99.4% to 49.6% without changing a byte of output.

**F7 — A file accessed but never defined still needs a node.** Work files, print devices, tape units. There
these synthetic nodes carried 7104 of 9379 access edges — the majority, not an edge case. Create them ONLY for
names that resolve to nothing: minting one for an AMBIGUOUS name adds a third candidate and makes the
ambiguity permanent.

**F8 — Some commands are invoked by nearly every program.** Four had 1920 / 1793 / 1755 / 1133 callers against
1934 programs. An edge present almost everywhere distinguishes nothing while dominating the graph, so those
get a node carrying the caller COUNT and no enumerated edges. The cut is a ratio, so it travels.

**F9 — A catalogue is not evidence of use.** The platform documented 953 commands; 112 were actually invoked.
Emit a node only for what the tree invokes.

**F10 — Never overwrite a node a human wrote.** Five of those 112 were hand-authored. The builder's own nodes
carry the `__OBJECT__` sentinel, so a node with a genuine `artifact_locator` was not written by the builder.

**F11 — Reference coverage is never uniform. This is the one that will mislead you.** There the reference
recorded program calls for 956 of 956 control-language files in one system and 197 of 801 in the other — and
on those 197 it listed 2.27 targets per file where the source contained 5.10. Measured per cell, the same
extractor scored 100% in one system and 58% in the other, with no difference in capability.

* Score per `(system × file_type × role)`, never as one aggregate.
* Print COVERAGE next to precision. Below ~90%, the numbers describe a recording gap, not a capability gap.
* A cell the reference left empty is reported, not scored, and never gated.

---

## 4. What the preset does NOT derive

Stated plainly so an absent field reads as a decision rather than an oversight:

* `disp_print`, `cobol_variant`, `med_type` — these come from classifiers the preset does not carry. A
  plausible-looking guess is worse than an absent field: a wrong value is indistinguishable from a right one
  downstream, whereas a missing one is visibly missing.
* Summaries for artifacts with no extractable text (screen/report definitions, binaries). That is what
  `--emit-partial` is for: it marks the meta `needs_completion` so a later pass fills the semantic fields and
  lint blocks the partial from being treated as finished.
* Anything from commented-out code. A disabled statement is not a relation.

---

## 5. First build

```bash
# 1. edit the config, then check it parses and classifies as you expect
py .ai-work/tooling/build_cobol_wiki_metas.py --root <small-subtree> \
   --config .ai-work/asp_cobol_wiki.config.yml --updated-at today --dry-run

# 2. emit to a TEMPORARY directory and read some of it
py .ai-work/tooling/build_cobol_wiki_metas.py --root <subtree> \
   --config .ai-work/asp_cobol_wiki.config.yml --updated-at today --out-root /tmp/metas

# 3. lint the whole emitted tree
py .ai-work/tooling/lint_wiki.py --sources-only --path /tmp/metas

# 4. only then, and as a deliberate decision:
py .ai-work/tooling/build_cobol_wiki_metas.py --root <subtree> \
   --config .ai-work/asp_cobol_wiki.config.yml --updated-at today --write-live
py .ai-work/tooling/build_wiki_source_index.py
py .ai-work/tooling/build_relations.py
```

`--write-live` is required to touch the live meta tree and is never the default (without it, output goes to
`--out-root` or a fresh temp directory). The builder never writes the index — that is a separate, owned step.

**Registering the route** is done in the project that has the sources, not in AIWS:

```bash
py .ai-work/tooling/route_build_tool.py set asp_cobol_source \
   --tool .ai-work/tooling/build_cobol_wiki_metas.py \
   --args "--root {root} --source-prefix {prefix} --meta-subdir {subdir} --config .ai-work/asp_cobol_wiki.config.yml" \
   --profile-id asp_cobol_source
```

One engine, N dialect configs, N routes.

---

## 6. Rebuilding is not safe by default — check the positive signal

A source meta carries fields the builder **preserves but never produces** (`vld_usage`, `cobol_variant`,
`disp_print`, `med_type`, `cl_callers`, `copybooks_used`, curated `business_name` / `program_id`). They come
from separate enrichment tools.

Measured on the originating corpus: deleting **1141** metas and rebuilding them from source alone lost
**6857 fields and 49 sections** across 1140 of 1140 metas — **with zero lint errors**, because an absent
optional field is not a schema violation. At least one of those fields had no identified writer at all, so
what is lost may not be regenerable.

Two rules follow:

1. **Treat "delete and rebuild" as unsafe.** Rebuild in place so the merge has something to preserve from, and
   keep a copy regardless.
2. **Verify with the positive signal, never with "no errors".** The builder prints
   `preserved from existing metas: N field(s) + M section(s)`, and that line **disappears** when there was
   nothing to preserve from. Over an existing tree, no such line means the enrichment is being dropped.

### Migrating a corpus that predates this preset

A corpus built before the preset carries the builder's un-namespaced defaults (`cobol_source`, `prj_file`,
`module`, `concept`). Moving it to the preset names is a config edit plus one flag:

```bash
# keep the DIRECTORY name, change only the frontmatter field
py .ai-work/tooling/build_cobol_wiki_metas.py --root <subtree> \
   --meta-subdir cobol_source \
   --config .ai-work/asp_cobol_wiki.config.yml --updated-at today --write-live
py .ai-work/tooling/build_wiki_source_index.py && py .ai-work/tooling/build_relations.py
```

⚠️ **`--meta-subdir` is not optional here.** With it empty the meta directory is named after `source_type`
(`emit.py`, `objects.py`), so renaming the type **relocates the entire meta tree** and every `meta_locator` in
the index with it. Confirm the `preserved from existing metas: N` line shows N > 0 before accepting the run.

`file_node_dir` is a separate config key and is not derived from `source_type`, so file-node directories are
unaffected.

---

## 7. Verifying the output when you have no reference corpus

This is the normal case, and it is weaker than what the preset was developed against.

**Classify each error class before concluding anything.** Adopting this preset took five lint rounds to reach
zero, and the first four looked identical at the `errors=N` line while having completely different causes:
a missing `doc_source_id` column, then targets not yet registered, then a stub authored as the wrong node
kind, then an absolute `artifact_locator`. Only the first was about the builder at all. Read the rule names,
not the count.

1. **Run the shipped tests first, always.** `.ai-work/tests/cobol_wiki_tests/test_units.py --tooling
   .ai-work/tooling` (125 checks) and `.ai-work/tests/cobol_parser_tests/` (421 tests) both run on shipped
   fixtures and need no corpus.
2. **Structural invariants.** Every `part_of` target exists; every emitted edge resolves; no meta points at
   the `__OBJECT__` sentinel as if it were a path. `lint_wiki.py --sources-only` checks these. Emit the WHOLE
   tree before linting: a partial emit reports every out-of-scope target as a dead edge.
3. **Self-consistency counts.** Files scanned per type, per library. A type appearing once is usually a config
   gap; a library appearing with one file is usually a path rule that did not fire.
4. **Hand-verify twenty files** spread across types and libraries. Twenty catches a systematically wrong rule;
   it will not catch a rare one.

What you **cannot** conclude without a reference: recall. You can see that what was emitted is right; you
cannot see what was not emitted.

---

## 8. Config gotchas that cost real time

The config is read by the AIWS YAML-subset parser, which does not raise on malformed input:

| you wrote | what you got | fix |
|---|---|---|
| a flow list spanning several lines | the first line only, with `[` stuck to item 0 | one line, or a block list |
| a comment at ITEM indent above the first `- ` | the whole list folded into a mapping | put the comment at KEY indent |
| a collection inside a list item | empty `{}` items in the OUTER list | comma-separated string |
| a flow mapping `{k: v}` anywhere | the literal string `"{k: v}"` | block mapping |
| `- value  # comment` in a **profile** list | the value **including** the comment text — so the entry silently never registers | comment on its own line |

A role name containing a colon (`x:uses`) can never be a config KEY — the parser splits on the first colon and
quoting does not help. Write `x_uses`; the preset canonicalizes. Regex patterns use SINGLE backslashes.

**Declare all four `source_type` values explicitly.** The engine's built-in defaults are the un-namespaced
`cobol_source` / `prj_file` / `module` / `concept`; the last two collide with AIWS's generic object kinds. The
shipped config template declares `asp_cobol_source` / `asp_file` / `asp_module` / `asp_system` — leave them in.

### Upgrade note: a new object kind does not reach an existing installation

`merge_wiki_source_profiles.py` appends only **missing top-level keys**; it never inserts items into a list
that already exists. So a new object kind added to the canonical `knowledge_object.yml` reaches fresh installs
but **not** an existing one. On upgrade, add the missing values to
`.ai-work/wiki_sources/profiles/knowledge_object.yml` by hand — otherwise metas carrying them draw
`meta_source_type_unknown`.

---

## 9. See Also

- `SOURCE_BUILD_ROUTING_SPEC` §5 — the routing registry this preset registers into (in the consuming project).
- `product/wiki_source_profiles/README.md` — shipped-profile contract, merge-not-overwrite, Step-2 enrich.
- `CR-AIWS-2026-08-026` — the change that adopted this preset, including the nine decisions behind its naming.
