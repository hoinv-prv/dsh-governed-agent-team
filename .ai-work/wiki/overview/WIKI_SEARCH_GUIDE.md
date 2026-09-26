# Wiki Search Guide — all systems

## Cách tìm (escalation chain)
1. `lookup_wiki_source.py --query <kw>  --limit 5` (lexical mặc định)
2. Miss/yếu → `--mode tokens` (per-token, fold dấu VI, aliases tự expand)
3. Concept khác từ vựng / top score <15 → `--mode catalog` (đọc-chọn slim catalog)
4. Vẫn miss → raw search (CR-052 gated — cần authorization; xem document_search_guidelines)

Budget (E4): plan 3–5 queries, ~1 call/input; vượt ~2× inputs → BẮT BUỘC capture `retrieval_improvement` (MP1–MP7). Doc-set theo task: `build_reading_kit.py --query "<task>" `.

## By task type (từ Task Lens presets × types hiện có)
| Lens | Intent | Source types có trong wiki này |
|---|---|---|
| knowledge_capture | Capture or curate reusable knowledge — synthesize patterns, conventions, and decisions for | methodology_spec (104) |
| planning_wbs | Plan work or build a WBS — decompose scope into steps/tasks, sequence them, and identify i | methodology_spec (104) |

## Types & counts
| source_type | entries |
|---|---|
| gat_design_document | 6 |
| methodology_spec | 104 |
| wiki_guideline | 50 |


<!-- GENERATED page — do not hand-edit; regenerate via `py .ai-work/tooling/build_wiki_overview.py` (/aiws-wiki build-overview). CR-AIWS-2026-07-010; hand-edit = lint ERROR overview_hand_edit. -->
<!-- GENERATED-FINGERPRINT: 974061d988b0 -->
<!-- GENERATED-BODY-HASH: 7bbe88733c83 -->
<!-- GENERATED-AT: 2026-09-26T19:05:34 -->
