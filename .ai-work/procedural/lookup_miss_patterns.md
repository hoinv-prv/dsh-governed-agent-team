# Lookup Miss-Pattern Taxonomy (MP1–MP7)

> Vocabulary chuẩn cho capture `retrieval_improvement` (CR-AIWS-2026-07-008 C1). Nguồn: đo thực nghiệm AIP-EXEC-902 (2026-07-04, ký hiệu gốc P1–P7 — đổi MP để khỏi trùng phase names). Dùng: khi trip-wire E4 nổ hoặc lookup miss, ghi capture content kèm mã MP tương ứng để triage gom pattern.

| # | Pattern | Nhận diện | Root cause điển hình | Hướng xử lý |
|---|---|---|---|---|
| MP1 | **Generic single-token keys** — entry không tự tìm thấy bằng first-3 keys | self-test FAIL; noise nhiều matches/query | extractor freq-rank đơn từ; thiếu compound discriminative keys | curate T1 compound keys (Lookup_Key_Strategy); CR-004 mechanism |
| MP2 | **Language-variant absence** — query VN/JA không match key EN | query thuần Việt miss trong khi query EN-mixed hit | curation chỉ EN; chưa emit alias variant | `query_aliases.yml` (CR-007 B2) + diacritic fold (B1); curate alias keys |
| MP3 | **Canonical vs derivative ranking** — spec chính bị doc phái sinh đè rank | spec đúng nằm rank sâu; sprint-summary/index đứng trên | key-flooding của derivative; scorer authority boost không đủ thắng | curate keys spec chính; cân nhắc authority weighting (eval-first) |
| MP4 | **Unregistered target** — tài liệu chưa đăng ký, lookup không thể route | 0-hit hoặc chỉ hits không liên quan; raw-fallback tìm thấy | registration hygiene / by-design boundary (runtime artifacts) | register nếu reusable (`retrieval_gap` flow); nếu by-design → ghi rõ trong search guide |
| MP5 | **Stale citations** — digest/curated doc cite source_id đã chết | mở theo citation → id không resolve | source_id đổi khi re-register; thiếu citation lint | `curated_citation_stale` lint; digest theo doctrine E2 (path+id cặp đôi) |
| MP6 | **Query-phrasing noise** — query nhiều từ generic khớp mọi nơi | hàng chục-trăm matches, score phẳng | cộng hưởng MP1; token generic không bị down-weight | sharpen query (score-gap heuristic); df-downweight (CR-007 B3) |
| MP7 | **Near-miss masking** — target chưa đăng ký nhưng registered hits "trông-có-vẻ-đúng" che mất miss | hits plausible score cao nhưng sai target; `on-empty` không fire | trigger raw = `total==0` quá thô; dirs-table coverage gap | case-A P7 escalation (`--include-raw always` cùng authorization); maintain dirs table |

**Cách ghi trong capture:** `content` bắt đầu bằng `[MPn]` + intent + chuỗi queries đã thử + call count + query trúng cuối (nếu có) + đề xuất cách tìm ít call hơn. Nhiều pattern cùng lúc → liệt kê cả hai (vd `[MP1+MP6]`).
