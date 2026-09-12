# wiki_source_refresh_needed — Tài liệu wiki đã đăng ký/canonical bị sửa/đổi
- **type:** wiki_meta_update_candidate · **suggested_target:** wiki_meta · **timing:** ⚡immediate

## When
Trong khi chạy AIP, AI **sửa** hoặc **phát hiện thay đổi** ở một registered wiki source (artifact có meta tại `.ai-work/wiki_sources/meta/<id>.md` + entry trong `index.jsonl`) HOẶC một canonical wiki doc (dưới `product/wiki_guidelines/`). Khi content gốc đổi, các dependent artifacts (meta, index, knowledge object, lookup keys, summary, related sources) trở nên stale.

## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `wiki_quality_issue` — tên trigger `wiki_source_refresh_needed` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `wiki_quality_issue`. `improvement_scope` mặc định: `project`.

candidate_kind = `wiki_source_refresh_needed`. Chọn nhánh `type` theo ngữ cảnh:
- `wiki_meta_update_candidate` → khi thay đổi nằm ở **source meta** đã đăng ký (target `wiki_meta`).
- `wiki_update_candidate` → khi thay đổi nằm trong **canonical wiki doc** (target `knowledge_hub_curated`).

Trong content record ghi: changed file path, related `source_id` (artifact hay object node — nếu biết), nature of change, dependent artifacts cần refresh (meta/index/object node/related sources).

## Suggested action
Tại Final Capture Sweep (close), AI **đề xuất** chạy `/aiws-wiki refresh` (UPDATE router) cho từng item và **đợi HUMAN confirm** trước khi thực thi — KHÔNG auto-refresh (safety rule #7). HUMAN defer → set status `deferred`.

## Example
AIP-EXEC sửa `product/wiki_guidelines/core/specs/WIKI_CANDIDATE_SUGGESTION_RULE.md` → capture `wiki_update_candidate`, đề xuất refresh meta/index của source liên quan.

## Notes
TIMING: capture **ngay lập tức** khi đang edit file hoặc khi phát hiện thay đổi — không đợi cuối step; nếu bỏ qua, drift chỉ lộ ở maintenance pass sau hoặc bị miss.
