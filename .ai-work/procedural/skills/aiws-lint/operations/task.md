# aiws-lint — operation: task (scoped finalize lint)

> Scoped mode of the SAME tool — full doctrine, flags and exit-code contract live in [operations/all.md](all.md) (đọc trước khi chạy). CR-AIWS-2026-07-025 §3.5.

Command: `py .ai-work/tooling/lint_all.py --scope task --workspace <task-ws> --aip <active-aip>`

- Lints the task's AIP + Task Workspace (mandatory 0 errors); adds wiki/index lint iff the task footprint touched `.ai-work/wiki/` or `.ai-work/wiki_sources/`.
- **Auto-escalates to whole-tree** (verb `all`) when the footprint touches `product/` or the task applies a CR.
