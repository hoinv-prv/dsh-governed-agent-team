# aiws-lint — operation: all

> Operation of the `aiws-lint` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Single-command deterministic lint across all MVP targets:
- AIP (ROOT / PLAN / EXEC / LOCAL)
- Wiki entries
- Wiki Source Meta
- Wiki Source Index
- Every workspace under `.ai-work/workspaces/`

Bare `aiws-lint` (no `--scope`) is the **whole-tree** lint — the **canonical / CR-apply** finalize lint (CR-067); a CR flips `applied` only after it is clean (0 errors). For a normal **task-execution** finalize, `aiws-aip run` step 7 uses the **scoped finalize lint** (`--scope task`, see Scopes) which lints only the task's AIP + Task Workspace and auto-escalates back to whole-tree on a `product/` or CR-apply footprint.

## Tool
`.ai-work/tooling/lint_all.py`

### Example
```
python .ai-work/tooling/lint_all.py --strict --format text
```

### Scopes
- **(default) `--scope all`** — whole-tree; every target above. The canonical / CR-apply finalize lint.
- **`--scope task --workspace <ws> --aip <aip>`** — scoped finalize lint (CR-067): mandatory AIP + Task-Workspace, conditional wiki/index when the git footprint touched `.ai-work/wiki/` or `.ai-work/wiki_sources/`, and auto-escalate to whole-tree when the footprint touches `product/` or the task applies a CR. Deterministic (git-changed footprint) — used by `aiws-aip run` step 7.

### Exit codes
- `0` — clean (or only info)
- `1` — warnings present AND `--strict`
- `2` — at least one error

## When to run
- after creating/updating any AIP
- after generating an Active Step Context
- after building/refreshing a Wiki Source Meta or Index
- before finalizing a wiki update
- before finalizing a **task execution** → scoped finalize lint (`--scope task`, via `aiws-aip run` step 7); a **canonical / CR-apply** finalize uses bare whole-tree `aiws-lint`
- in CI on every push touching `.ai-work/`

## Rules
- lint is a guardrail, not a reviewer
- do not ask the tool to auto-fix wiki or truth
- treat warnings as "please look before merging"
- **one-driver rule list (lesson AIP-945; canonical CR-AIWS-2026-07-035):** wiki-lint rule mới → thêm vào **MỘT chỗ duy nhất**: driver `lint_wiki.run_wiki_source_lints(...)`. Cả `lint_wiki.py main()` lẫn `lint_all._lint_wiki_all` đều gọi driver này, nên rule tự động có mặt ở CẢ HAI surface (**từ CR-AIWS-2026-07-034 T2 cơ chế đã đảm bảo điều đó** — trước đó leg tự liệt kê tay và rule chỉ ở `main()` thì VÔ HÌNH trong gate whole-tree: `skill_link_broken` mù suốt CR-029→AIP-945, cùng 5 rule khác). Đừng thêm rule thẳng vào `main()` hay vào leg.
- **Parity check khi đụng lint surface:** chạy cả `lint_wiki.py` standalone lẫn `lint_all.py` → cùng finding-code set cho nhóm wiki-source rules (regression guard: `.ai-work/tests/test_lint_surface_unification.py`).
- **Noise của rule = BUG của rule, không phải chuyện UX (lesson AIP-947; canonical CR-AIWS-2026-07-036):** một rule sinh false positive **có hệ thống** phải được **refine qua CR** — KHÔNG "sống chung với noise". Lý do là correctness, không phải thẩm mỹ: `old_skill_name_reappeared` có 16 false positive (verb-token sau CR-025) và chính noise đó **che 2 hit THẬT** (`aiws-wiki/SKILL.md` ×2 cây vẫn còn tên tiền-rename của `aiws-doc-convert-skill`) từ CR-025 tới 2026-07-14 — refine rule (CR-034 T1) là hit thật lộ ra ngay. Rule mà người ta quen bỏ qua đã **ngừng là guardrail**. *(Ghi chú dogfood: bản nháp bullet này từng trích **literal** tên cũ làm bằng chứng và bị chính rule đó bắt — đúng như thiết kế: skill surface không mang tên tiền-rename, kể cả trong prose. Đã diễn đạt lại thay vì mute — chính là chính sách bên dưới.)*
- **Rule dual-tree KHÔNG quét vùng project-local nằm trong section đã ship (CR-AIWS-2026-08-091):** desk state của Agents Pack (`agents/task_desks/**`, legacy `agents/instances/**`) không phải pair — `dualtree_link_broken` và `dual_tree_only_in_one` bỏ qua nó. Danh sách vùng = `check_dual_tree.PROJECT_LOCAL_PREFIXES` (một chỗ; lint import, không chép). Một finding code bị đổi tên (`skill_link_broken` → `dualtree_link_broken`) được resolve ở tầng `lint_accept` (`_common.LINT_ACCEPT_CODE_ALIASES`, một release) — không phát lại dưới tên cũ.
- **Mute chỉ per-instance:** khi một finding cụ thể là chấp nhận được, dùng `lint_accept` trong frontmatter của CHÍNH file đó (bắt buộc `code` + `reason` + `accepted_by`; self-guard code không mute được — CR-AIWS-2026-06-065). **Không bao giờ** mute ở cấp rule/class (bỏ rule khỏi driver, nới severity để "cho đỡ ồn", hay coi một code là "cứ kệ nó"). Cùng một code phải mute ở nhiều file → đó là tín hiệu **rule cần refine**, không phải mute thêm — guard `lint_accept_class_noise` (WARN, ngưỡng ≥3 file; CR-AIWS-2026-07-036 T2) sẽ nói thẳng điều đó.
