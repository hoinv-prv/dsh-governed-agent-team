# Tools shipped in this package

> Sinh tự động lúc build (CR-AIWS-2026-08-115 C2) — **đừng sửa tay**, mọi sửa đổi sẽ mất ở
> lần build sau. Mô tả lấy từ dòng đầu docstring của chính tool. Xem `README.md` cùng thư
> mục để biết *dùng tool nào khi nào* — file này chỉ trả lời *package có tool gì*.

| Tool | Purpose (dòng đầu docstring) |
|---|---|
| `_common.py` | Shared helpers for AI Work System MVP tooling. |
| `account_id.py` | Provision the local AIWS account_id + account_info.yaml — CR-AIWS-2026-06-016. |
| `allocate_aip_id.py` | Per-account AIP-id allocator — CR-AIWS-2026-06-015 v2. |
| `allocate_cr_id.py` | Cross-branch-aware CR-id allocator (month-scoped). Companion to allocate_aip_id.py. |
| `append_capture.py` | Append ONE capture record to a Task Workspace's `08_capture_inbox.jsonl` — safely. |
| `build_active_step_context.py` | Materialize Active Step Context from an AIP step + workspace state. |
| `build_aip_index.py` | Build the AIP Registry/Index — CR-AIWS-2026-06-015 v2 (per-account folders). |
| `build_aiws_install_package.py` | Build an installable package for AI Work System MVP. |
| `build_asp_manual_metas.py` | One-shot driver: build Wiki Source Metas for the ASP vendor manual set. |
| `build_canonical_package_metas.py` | One-shot driver: build Wiki Source Metas for any adopted canonical package. |
| `build_cobol_wiki_metas.py` | Build wiki source metas from a COBOL/CL/ASP source tree. |
| `build_java_wiki_metas.py` | Batch-build Wiki Source Metas for Java source files (LEAN + typed edges + endpoints). |
| `build_preset_wiki.py` | Build the PRESET AIWS wiki — the shipped `aiws` namespace a downstream project can query |
| `build_python_wiki_metas.py` | Batch-build Wiki Source Metas for Python source files (LEAN + typed import edges). |
| `build_reading_kit.py` | Reading-kit / digest generator (CR-AIWS-2026-07-003 E2). |
| `build_relations.py` | Build the Wiki Relations projection (relations.jsonl) from source metas. |
| `build_wiki_overview.py` | Wiki overview synthesis pages (CR-AIWS-2026-07-010). |
| `build_wiki_page_base.py` | deterministic base for /aiws-wiki build-pages (CR-AIWS-2026-07-023). |
| `build_wiki_source_index.py` | Build the Wiki Source Index as a projection of all source metas. |
| `build_wiki_source_meta.py` | Create or refresh a Wiki Source Meta artifact from a source + profile. |
| `check_aiws_upgrade.py` | AIWS upgrade safety check — snapshot protected zones before upgrade, |
| `check_dual_tree.py` | Dual-tree drift check (CR-AIWS-2026-07-030 change B). |
| `check_eol_alignment.py` | Report (and optionally repair) tracked files whose WORKTREE bytes differ from their BLOB. |
| `compose_aiws_rules.py` | render AIWS rules into per-tool rule files (CR-AIWS-2026-08-066 C3). |
| `convert_md_to_excel.py` | Markdown-to-Excel Converter — Local CLI Tool. |
| `detect_changed_wiki_sources.py` | Detect which wiki source artifacts may have changed. |
| `diff_payload_tree.py` | Per-file ADD / UPDATE / UNCHANGED / REMOVED between a package payload and an installed tree. |
| `evaluate_wiki_source_impact.py` | Evaluate whether a source change likely impacts the wiki. |
| `init_workspace.py` | Initialize a task workspace from the workspace template. |
| `lint_aip.py` | Lint AIP files (PLAN / EXEC / LOCAL). |
| `lint_all.py` | Run all MVP lints (AIP, workspaces, wiki) and aggregate results. |
| `lint_wiki.py` | Lint wiki knowledge artifacts and wiki source-side artifacts. |
| `lint_workspace.py` | Lint a runtime workspace directory. |
| `lookup_wiki_source.py` | Lookup sources via the Wiki Source Index. |
| `mask_sensitive.py` | Scan markdown files for sensitive information and replace with placeholders. |
| `merge_wiki_source_profiles.py` | Merge canonical wiki_source_profiles into a project's profiles dir WITHOUT overwriting. |
| `normalize_wiki_meta.py` | Batch-normalize legacy Wiki Source Meta fields to current lint-conformant form. |
| `personal_notebook_write.py` | aiws-util-personal-notebook helper. |
| `project_profile.py` | create, check and complete `.ai-work/project_profile.yml`. |
| `read_operating_memory.py` | Print the Operating Memory L2 digest on stdout (CR-AIWS-2026-08-029). |
| `refresh_wiki_source_meta.py` | Refresh a Wiki Source Meta against the current source artifact. |
| `route_build_tool.py` | Source Build Routing registry CLI — CR-AIWS-2026-05-019 Stage 2. |
| `run_aip.py` | Orchestrate AIP execution: start, resume, jump-to-step, status, list-steps. |
| `scan_sensitive.py` | Scan markdown files for sensitive information and report findings. |
| `set_current_step.py` | Set the current-step pointer for a workspace. |
| `smoke_test_wiki_lookup.py` | Smoke-test wiki lookup quality: self-findability + custom test cases. |
| `test_e2e_handoff_workflow.py` | End-to-end test: Complete handoff workflow |
| `test_handoff_stub_creation.py` | Unit tests for handoff stub writer (Wave 2 Item 1). |
| `test_lint_handoff_missing.py` | Unit tests for step_handoff_missing lint rule (Wave 2 Item 2). |
| `triage_capture.py` | Capture triage: the close sweep, `defer`, and the one-time `migrate` (CR-AIWS-2026-08-125 C3). |
| `wiki_meta.py` | Meta value-add reader — output a Wiki Source Meta's ORIENTATION info for AI WITHOUT |
| `wiki_relations.py` | Query the Wiki Relations edge layer (opt-in, one-hop). |

**Tổng: 52 tool.**
