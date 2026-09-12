# aiws-wiki — operation: build-pages

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Trang wiki tổng hợp cho dự án (KHÁC overview navigation pages): dual-audience — HUMAN đọc onboarding + AI tra cứu như curated meta. Nội dung narrative do LLM viết TRÊN nền deterministic (survey/skeleton/digest), mọi lần sinh/tái sinh qua 2 HUMAN gate. Đăng ký `source_type: wiki_page`, `authority_level: curated_reference` (verify_when_decision_matters) SAU khi HUMAN duyệt — không bao giờ regenerate CR-free.

## Tool (deterministic base)
`py .ai-work/tooling/build_wiki_page_base.py {indices|survey|skeleton|check-grounding} --system <id>|--all-systems --scope <list> ...`

**Hai trục ĐỘC LẬP (CR-AIWS-2026-07-024):** `--system` lọc record theo system id (trục ngang, rule #12) ≠ `--scope` chọn FILE index nào để đọc — project / aiws / local (trục dọc, rule #13). `survey`/`skeleton`/`check-grounding` **hard-require `--scope`, KHÔNG có default** (DP-024-A) — thiếu → tool rc≠0. `local` trong scope đòi `--authorized` (rule #11).

## Modes
- **survey** → **Gate 0 — Index Confirm (BẮT BUỘC, trước mọi survey):** chạy `indices` → trình inventory deterministic (mỗi index: entries + đếm theo system; local ẨN hoàn toàn nếu chưa authorized — DP-024-B) cho HUMAN và **HỎI index nào cần tham khảo**. ⛔ HARD STOP — KHÔNG tự chọn, không union ngầm. HUMAN chọn → mới có `--scope` để chạy tiếp. → Gate 1: preflight (resolve `--system`; thiếu thì HỎI HUMAN, index/relations fresh — stale thì đề nghị rebuild) → chạy tool `survey --system <id> --scope <chosen>` → đọc `survey_<sys>.json` (đã ghi `scope` + `indices_read` — provenance audit) → trình **PAGE PLAN** (bảng: kind | verdict | grounding sạch | reading depth | outline 3-5 bullet + đề xuất `CUSTOM_<NAME>` nếu hữu ích; **ghi rõ scope + indices đã đọc**) → **DỪNG chờ HUMAN chọn subset**. Data-quality report → append meta-refresh candidate vào `08_capture_inbox.jsonl` NGAY (rule #7).
- **build** (sau Gate 1): mỗi trang được chọn: tool `skeleton --page <KIND>` → LLM viết narrative vào vùng `<!-- NARRATIVE:BEGIN/END -->` theo **Page contract** dưới. Reading depth: list-kind = meta-only; narrative/data-kind = mở artifact theo heading-hints của meta, đọc section đích (không cả file). Drafts + `PAGE_PLAN.md` nằm trong Task Workspace, `status: draft`. → **DỪNG chờ Gate 2**.
- **register** (sau Gate 2, chỉ trang HUMAN approve): set `status: active` + `last_verified_at: <today>` → move vào `.ai-work/wiki/pages/<KIND>_<system>.md` → `build_wiki_source_meta.py --artifact <page> --source-id SRC-PAGE-<KIND>-<SYSTEM> --source-type wiki_page --profile wiki_pages.yml --authority-level curated_reference --system <id> --lookup-keys "<3 compound keys>"` → điền `## Related Sources` của meta = mỗi grounding source 1 edge `role: x:synthesized_from — <basis> [asserted]` (DP-1) → `build_relations.py` → `build_wiki_source_index.py` → `lint_wiki.py --sources-only` (0 err) → self-test 3 keys (`aiws-wiki test-lookup`) → maintenance chain (regen overview → final index rebuild). Trang rejected → giữ draft trong workspace, KHÔNG register.
- **refresh**: tool `check-grounding` → trang stale: `status: needs_review` (+ capture) → HUMAN chọn per trang: re-build (Gate 2 diff) / verify-only (bump `last_verified_at`, về active) / retire (`aiws-wiki deregister` + archive).
- **status**: đếm trang theo status/system + stale list + trang chưa register.

## Page contract v0.1
- Frontmatter: `artifact_type: wiki_page`, `page_kind`, `system`, `title`, `status`, `audience`, `generated_by`, `generated_at`, `last_verified_at`. KHÔNG `grounding:` (grounding = `## Sources` + meta edges).
- Sections cuối trang, đúng thứ tự khi có: `## Consistency Findings` (mâu thuẫn giữa nguồn, cite 2 phía) → `## Coverage & Limits` (grounding không phủ gì; coverage số liệu TÍNH từ grounding) → `## Sources` (bảng `Alias | source_id | Artifact path | Đã lấy gì`).
- Rules: mọi claim có citation `[S#]` trace về Sources; conflict → source_type authoritative + mới hơn thắng, ghi discrepancy; grounding-beats-prompt (mâu thuẫn chỉ thị orchestrator → theo grounding, report mismatch); absence wording "chưa có trong grounding" (≠ "không tồn tại"); propagate `[asserted]/[verified]` khi dựa relation edge; negative evidence được phép có citation; không bịa.

## Rules / guardrails
- **Two-clause (DP-912-6a):** mọi trang = clause-b/(C) CONTENT — HUMAN gate mỗi lần sinh; KHÔNG auto-regen; lint chỉ báo stale.
- **KHÔNG re-propose O5-B:** LLM luôn trên deterministic base (survey/skeleton/digest), không đọc raw viết trang làm đường chính.
- **`overview_page` không đổi** (navigation-only); family này là curated-after-gate.
- **Candidate-only (#7):** AI không tự promote; `curated_reference` chỉ sau Gate 2; cao hơn = Controlled Promotion → STOP + CR.
- **Per-system (#12):** tool hard-require `--system`/`--all-systems`; trang emit per-system.
- **Index scope (CR-024):** Gate 0 bắt buộc mỗi run survey; `--scope` hard-require không default (DP-024-A); rule #11/#12/#13 giữ nguyên hiệu lực — scope grant không waive gì; `skeleton`/`check-grounding` dùng CÙNG scope đã HUMAN chọn (ghi trong survey json).
- **Grounding rank + limit (CR-067):** grounding của mỗi kind được **rank theo độ liên quan** (khớp keyword của kind vào lookup_keys/summary/title, deterministic, tiebreak index-order) **trước khi cắt**; giới hạn mặc định **100**, chỉnh bằng `--grounding-limit` khi survey. Skeleton in `hiển thị N/M nguồn` khi bị cắt → LLM **bắt buộc** phản ánh giới hạn đó vào `## Coverage & Limits`. Rank/cut chạy SAU KIND_RULES filter — KHÔNG đổi filter/flavor.
- **Directory map = registered-dirs-only** (R5): suy từ index locators, KHÔNG raw scan.
- **page_kind (DP-4):** enum trong `wiki_pages.yml` + `CUSTOM_<NAME>`; kind lạ = lint WARN.
- **wiki_entry boundary (DP-2):** pages ≠ wiki_entry; dự án có entry layer → survey coi entries là PAGE_EXISTS/PARTIAL evidence, KHÔNG tạo trùng, không migration bắt buộc.
- **Citation chưa-register (DP-3):** register-first khi artifact thuộc corpus dự án; label tạm chỉ trong draft (Gate 2 resolve hết trước register).
- **Ngôn ngữ (DP-5):** default VN (giữ thuật ngữ gốc EN/JP); override qua project_profile `wiki_pages_language`.
- stdlib-only; `py` launcher; dual-tree.

## Lint
- `page_sources_missing` (ERROR): trang registered thiếu `## Sources` / bảng rỗng / meta thiếu edge `x:synthesized_from`.
- `page_grounding_stale` (WARN): trang active có grounding `updated_at` > `last_verified_at`, hoặc grounding deregistered.

## Capture
Thấy kind mới đáng có / meta hỏng / mâu thuẫn nguồn → capture (`wiki_update_candidate` / meta-refresh) vào `08_capture_inbox.jsonl` NGAY — không tự promote.

## Flavors (KIND_RULES — CR-AIWS-2026-07-046)

`build_wiki_page_base` chọn bộ grounding rule theo **flavor** của corpus:

| Flavor | Nhận diện | Ghi chú |
|---|---|---|
| `cobol` | có source_type chứa `cobol` | như cũ |
| `methodology` | **đa số** source_type ∈ {`methodology_spec`, `wiki_guideline`, `process_guideline`, `sop`, `process_template`} | **MỚI** — corpus AIWS (110 spec + 84 guideline) trước đây rơi vào `docs` và ăn 7/10 `NO_GROUNDING` |
| `docs` | fallback | corpus RD/BD/DD thường |

- **`SCREEN_LIST` / `TABLE_LIST` trong flavor `methodology` = `N_A`** (không áp dụng — methodology không có màn hình/bảng). `N_A` **khác** `NO_GROUNDING`: không phải thiếu nguồn, mà là kind không tồn tại cho corpus này.
- Ép flavor thủ công: `--flavor {docs|cobol|methodology|auto}` (default `auto`).
