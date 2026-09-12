# aiws-wiki — operation: build-overview

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Trang overview = PROJECTION của `index.jsonl`(+`index.aiws.jsonl`) + `relations.jsonl` → AI/HUMAN biết wiki chứa gì + tìm thế nào, không drift tay.

## Tool
`py .ai-work/tooling/build_wiki_overview.py --system <id> | --all-systems [--pages contents,search,health] [--no-register]`

## Khi nào chạy
- Sau mỗi index/relations rebuild (maintenance chain: rebuild relations → **regenerate overview** → final index rebuild — tool tự làm bước cuối). Bỏ qua → lint WARN `overview_fingerprint_stale`.
- Bootstrap project mới: sau STEP-11 của /aiws-wiki bootstrap.
- Lint báo `overview_hand_edit` (ERROR): KHÔNG sửa tay trang generated — sửa metas/index nguồn (hoặc generator qua CR) rồi regenerate.

## Rules
- Multi-system: BẮT BUỘC `--system <id>` hoặc `--all-systems` (per-system pages — rule #12; không aggregate cross-system).
- **Page catalog CR-ratified (DP-912-6a two-clause):** default-on = contents/search/health. Thêm/bớt trang default-on = CR mới. Trang narrative (business flow...) = LLM content → HUMAN gate từng lần, KHÔNG thuộc tool này.
- Trang generated đăng ký `source_type: overview_page`, `knowledge_targets: navigation` — routing surface, không phải curated evidence.
- **Family `wiki_page` (CR-AIWS-2026-07-023) — KHÁC:** trang synthesis curated do LLM viết, HUMAN-gated 2 lần → đăng ký `curated_reference` SAU Gate 2 (clause C của two-clause rule; use_rule verify_when_decision_matters, citations bắt buộc). Guardrail này CHỈ áp cho `overview_page` (vẫn navigation-only). Boundary (DP-2): pages ≠ `wiki_entry`; dự án có entry layer → survey coi entries là PAGE_EXISTS/PARTIAL, không tạo trùng. Xem `/aiws-wiki build-pages`.
- Output: `.ai-work/wiki/overview/<PAGE>_<system>.md`; metas: `.ai-work/wiki_sources/meta/overview/SRC-OVERVIEW-<PAGE>-<SYSTEM>.md`.

## Capture
Thấy category/trang mới đáng có (vd object catalog khi có object metas) → capture `wiki_update_candidate` (đề xuất mở page catalog qua CR) — không tự thêm trang.
