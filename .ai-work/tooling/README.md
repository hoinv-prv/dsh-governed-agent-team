# tooling/
## Terminology note

> **Danh sách ĐẦY ĐỦ mọi tool trong package: [`TOOLS_INDEX.md`](TOOLS_INDEX.md)** (sinh tự động lúc build).
> Bảng dưới đây là bản *curate* theo nhóm việc — nó không hứa liệt kê hết.

Trong AI Work System:
- **Knowledge Hub** là tên chính thức của component
- **Wiki** là tên vắn tắt vẫn được dùng bên trong hệ thống để chỉ Knowledge Hub


Deterministic-first scripts for AI Work System MVP. **Stdlib-only by default**
— see "Document conversion" section below for the single documented exception
(`convert_md_to_excel.py` requires `openpyxl`). Each script supports `--help`.

## Runtime
| Tool | Purpose |
| --- | --- |
| `init_workspace.py` | Scaffold `.ai-work/workspaces/<task-id>/` from template |
| `set_current_step.py` | Move current-step pointer for a workspace |
| `build_active_step_context.py` | Materialize `00c_active_step_context.md` from an AIP step |
| `read_operating_memory.py` | Print the Operating Memory L2 digest (second read path — `aiws-aip create`) |
| `diff_payload_tree.py` | Per-file ADD/UPDATE/UNCHANGED/REMOVED between a package payload and an installed tree (`upgrade` step 4) |

## Lint
| Tool | Purpose |
| --- | --- |
| `lint_aip.py` | Check AIP metadata, sections, steps, references |
| `lint_workspace.py` | Check workspace files, queue + capture JSONL parse |
| `lint_wiki.py` | Check Knowledge Hub / wiki entries + source meta + source index |
| `lint_all.py` | Aggregate run over AIPs, wiki, wiki sources, workspaces |

## Wiki source side
| Tool | Purpose |
| --- | --- |
| `build_wiki_source_meta.py` | Create/refresh a Wiki Source Meta (Knowledge Hub source meta) from an artifact + profile |
| `build_wiki_source_index.py` | Build `wiki_sources/index.jsonl` from all metas |
| `lookup_wiki_source.py` | Lookup entries via the index (lexical / id / path) |
| `wiki_relations.py` | Query a source's declared relations (one-hop, out + IN edges) — find related docs without repo-wide grep |
| `refresh_wiki_source_meta.py` | Re-project meta vs artifact; detect material change |
| `detect_changed_wiki_sources.py` | Snapshot-based change detection for source artifacts |
| `evaluate_wiki_source_impact.py` | Heuristic impact recommendation for changed sources |

## Self-test / acceptance tools (shipped — run against live state)
| Tool | Purpose |
| --- | --- |
| `smoke_test_wiki_lookup.py` | Lookup self-test / structured cases against the LIVE index (current-state health) |
| `test_object_named_consumer.py` | INV-5 acceptance: an object source_id resolves as BOTH relation endpoints |

> **Dev-only regression tests** — the wiki regression suite (`test_wiki_regression.py`), the
> build/install/manifest self-checks, the `allocate_aip_id` unit test, … — live in
> `.ai-work/tests/` (**not shipped**; that dir is not a build payload source). Run them after
> editing any tool/script/guideline/rule. See `.ai-work/tests/README.md`.
>
> Golden fixtures must stay lint-clean (guarded by `lint_wiki._lint_object_golden_fixtures`, so
> `lint_all` also catches a regression): the object-node golden in `fixtures/object_nodes/` (here)
> and the wiki-regression corpus `metas_good/` in `.ai-work/tests/fixtures/wiki_corpus/`. The
> `metas_broken/` counterparts must keep FAILING lint. Change either only on purpose.

## Document conversion
| Tool | Purpose |
| --- | --- |
| `convert_md_to_excel.py` | Convert Markdown tables → `.xlsx` (one sheet per table; supports `--section`, `--from-row`, `--to-row`, `--list-sections`) |

> **Dependency exception:** this script requires `openpyxl`. Install once:
> `pip install openpyxl` (fallback: `--user` or `--break-system-packages`).
> All other tooling in this directory remains stdlib-only.

## Shared module
- `_common.py` — frontmatter parser, section extractor, JSONL helpers, lint model

## Exit code conventions
- `0` — OK (or only info findings)
- `1` — warnings with `--strict`, or "no match" for lookup
- `2` — errors (missing files, invalid metadata, parse failures)

## CLI flag conventions
`--path`, `--workspace`, `--aip`, `--index`, `--meta`, `--artifact`, `--profile`,
`--strict`, `--format text|json`.

## Known Footguns

### Bulk script + Write tool state mismatch (BUG-06)
When a Python script (`py <script>.py`) modifies files externally and then the **Write** tool
is used on those same files, Claude Code will error: "File has been modified since read —
Read it again before writing."

**Root cause:** the Claude Code file-state tracker is not updated by external script execution.

**Fix pattern:** after running any bulk-modification script, **Read** the affected files before
issuing Write operations on them. Bulk scripts should print a summary of all modified file
paths so operators know which files need re-reading.

### BOM corruption from Edit tool on Windows (BUG-01/DX-02)
The **Edit** tool (VS Code extension) adds a UTF-8 BOM when saving on Windows. For meta files,
this silently breaks `parse_frontmatter` → empty index entries. Always use the **Write** tool
when creating or modifying wiki source meta files.