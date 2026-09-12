# object_relation_capture — Nhận biết object + quan hệ của nó (representation + domain) lúc build/refresh meta
- **type:** wiki_update_candidate · **suggested_target:** wiki_meta · **timing:** ⚡immediate (lúc build/refresh meta)

## When (CHỈ lúc build/refresh meta)
Khi AI **build hoặc refresh Wiki Source Meta cho một source artifact** (`aiws-wiki build-meta` / `aiws-wiki refresh-meta`,
qua router `aiws-wiki register` / `aiws-wiki refresh` / batch `aiws-wiki register-batch`) — đang đọc artifact + trích
`key_objects_and_terms`. KHÔNG fire khi chỉ đọc raw source ngẫu nhiên (object chỉ trích đáng tin từ chính artifact mô tả nó).

Capture này **VÔ ĐIỀU KIỆN** — chạy cho mọi reusable object artifact mô tả, **bất kể** object/artifact đã có meta hay chưa.
Artifact meta liên quan là **trigger** (nó thành cạnh `represented_by`), KHÔNG bao giờ là lý do skip. Việc "single-artifact
host / `companion_design`" chỉ chi phối việc author một object **node** riêng hay gộp vào một cạnh `companion_design` —
KHÔNG chi phối việc có capture hay không.

## 2 mục tiêu
- **Mục tiêu 1 — phát hiện OBJECT → quan hệ object↔artifact (representation).** Object (function/screen/table/api/batch/
  module/concept) mà artifact mô tả → object được `represented_by` chính artifact đang build meta.
- **Mục tiêu 2 — phát hiện quan hệ object↔object (domain).** Quan hệ giữa object này và các object khác (`x:calls`,
  `x:part_of`, `x:reads`, `x:migrates_to`…), **kể cả quan hệ suy luận / cross-cutting không tài liệu nào nêu rõ**.

## 5-step mechanism (DETECT + SUGGEST-only)
1. **Recognize object** — nhận biết các object artifact mô tả (mọi loại: function/screen/table/…); identity = `source_id`
   family-prefix (`SRC-FUNC-`/`SRC-SCREEN-`/`SRC-TABLE-`/`SRC-API-`/`SRC-BATCH-`/`SRC-MOD-`/`SRC-CPT-`),
   KHÔNG field định danh riêng (INV-2 — xem `Knowledge_Object_Model_Spec_MVP` §8). Tái dùng `key_objects_and_terms.objects[]` (discovery scratch) — KHÔNG tạo record riêng cho object.
2. **Representation edge (mục tiêu 1)** — object `represented_by` artifact đang build/refresh meta (artifact `represents` object).
3. **Domain edges (mục tiêu 2)** — từ nội dung artifact, nhận biết quan hệ object↔object → map sang `x:` type
   (`x:calls`/`x:part_of`/`x:reads`/`x:migrates_to`…; namespace `x:` mở, type mới thêm ngay). **Bao gồm quan hệ suy luận/ngầm**
   không tài liệu nào nêu → gắn confidence `asserted | inferred | candidate` (`asserted` cần evidence; thiếu evidence →
   `inferred`/`candidate`). **Ghi đủ MỌI cạnh** artifact làm lộ — đừng dừng ở cạnh hiển nhiên đầu tiên.
4. **De-dup guard (KHÔNG phải coverage test)** — steps 1–3 đã sinh tập quan hệ candidate **vô điều kiện**; bước này CHỈ
   chống trùng: nếu một quan hệ đã được khai MỘT lần (chiều canonical) trên object node → không re-emit. **Capture KỂ CẢ
   khi object CHƯA có meta** (trường hợp bình thường) — granularity là *tập quan hệ*, KHÔNG phải "meta tồn tại hay chưa".
   Chiều ngược = query (`wiki_relations.py --relations <source_id>`), KHÔNG chép edge thứ hai, KHÔNG chép vào từng tài liệu.
   *Chuẩn hoá:* `build_relations.py` chỉ auto-normalize 6 bare inverse pair (vd `represented_by→represents`,
   `part_of→contains`); type `x:`-prefix KHÔNG auto-collapse → declare-once cho `x:` là convention tác giả, reverse vẫn
   recover qua `--relations`.
5. **Capture + suggest HUMAN author** — append candidate `object_relation_capture` vào `08_capture_inbox.jsonl`, `content`
   gồm: object identity (kind + ID + tên vi/ja/en + `source_id` đề xuất) · `represented_by` → source_id của artifact này ·
   các `x:` domain edges (kèm evidence locator/quote + confidence). Đề xuất HUMAN author/cập nhật **MỘT** object-node meta
   với `## Related Sources` = representation + domain out-edges, khai một lần. (Necessity test: chỉ dùng 1 cạnh
   `companion_design` trên artifact meta khi object chỉ có 1 quan hệ companion với một tài liệu; tạo object node khi quan hệ
   trải nhiều tài liệu hoặc không tài liệu nào là host tự nhiên.) AI **KHÔNG** tự author; tool **KHÔNG** instantiate object meta.

## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `relation_or_object` — tên trigger `object_relation_capture` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `relation_or_object`. `improvement_scope` mặc định: `project`.

candidate_kind = `object_relation_capture` · type = `wiki_update_candidate` · suggested_target = `wiki_meta`.

## Suggested action
Tại Final Capture Sweep (close): AI **đề xuất** HUMAN author/cập nhật object-node meta (hoặc `/aiws-wiki register` object
path) cho từng object + edges của nó; **chờ HUMAN confirm**. KHÔNG auto-author. HUMAN defer → status `deferred`.

## Hai lớp quan hệ — giữ CẢ HAI (đừng nhầm trục)
- **Lớp A documentary** (tài liệu↔tài liệu): `## Related Sources` 9-role trên **artifact** meta (doc nào input của doc nào).
  **GIỮ NGUYÊN** — build/refresh meta vẫn scaffold/resolve như cũ. #19 KHÔNG thay thế lớp này.
- **Lớp B domain** (object↔object): `x:` edges trên **object-node** meta + cầu `represented_by`. **#19 làm lớp này.**
- **Mục đích = tìm tài liệu liên quan (cần CẢ HAI):** từ một chức năng → `represented_by` các doc mô tả nó → (documentary)
  doc input/companion; đồng thời → (domain `x:`) chức năng liên quan → `represented_by` doc của chúng. Lớp A một mình chỉ
  ra doc↔doc; lớp B + representation mở thêm đường function↔function↔doc. Đừng bỏ lớp nào.

## Boundary (tránh double-capture)
- **vs #1 missing_wiki_knowledge:** #1 = reactive, thiếu một mẩu *thông tin* documentary cần bổ sung vào meta đã có.
  #19 = proactive lúc build/refresh meta, capture *object + quan hệ object↔object* (lớp domain). Khác trục.
- **vs #18 wiki_source_refresh_needed:** #18 = source/canonical doc bị sửa → refresh *meta/index của artifact đó*.
  #19 (refresh side) = artifact đổi làm lộ object MỚI hoặc quan hệ object↔object MỚI/đổi chưa khai trên object node →
  capture để cập nhật *object node*. #18 lo artifact meta; #19 lo object node + edges. Không chồng.

## Eligibility / noise-guard
CHỈ capture object/quan hệ **reusable / high-value** (core domain entity, quan hệ tái xuất ở task khác). Đừng capture
object task-local tạm hoặc quan hệ tầm thường. Quan hệ suy luận confidence thấp → vẫn capture nhưng đánh dấu `candidate`,
để HUMAN gate. Đã có candidate/edge trùng → bỏ qua.
- **business_rule (MVP deferred):** KHÔNG tạo object node cho business rule (`SRC-BIZ-` deferred — Knowledge_Object_Model_Spec §3bis.1). Tri thức business rule được capture như nội dung / knowledge target trên meta của **parent design doc**, không phải object node riêng.

## Notes (operational)
- **Confidence của quan hệ suy luận — nơi sống:** ở candidate (capture inbox) là `content`; khi HUMAN author edge lên object
  node, confidence là *annotation `[conf]` trong dòng `## Related Sources`* (vd `— x:calls — [inferred]`), `build_relations.py`
  mang sang `relationship_confidence_note` (không bắt buộc, không lint). HUMAN quyết có author quan hệ `inferred`/`candidate`
  hay không; edge bền annotate confidence hoặc bỏ qua nếu quá yếu.
- **TIMING ⚡:** capture ngay lúc build/refresh meta, context còn tươi.
- **"Everything about object X"** = `wiki_relations.py --relations <source_id>` (out+in), KHÔNG phải lookup.

## Traceability
- KHÔNG hồi sinh retired KO record (xem `Knowledge_Object_Model_Spec_MVP` §8) → CR-005 / CR-023 INV-1/2/8.
- Object = `node_kind=object` meta thường (Layer-1), HUMAN author; pointer-only, không aggregate → DP5 / INV-3 (SHAPE 1).
- AI suggest-only, HUMAN author; tool KHÔNG instantiate object meta → DP6 / INV-8 / safety rule #7.
- Identity = `source_id` family-prefix, recognition contract → CR-023 §3bis.
- Declare-once (khai một lần chiều canonical, reverse = query) → CR-024.
- "Everything about X" = relations query, KHÔNG phải lookup → DP7.
- Trigger số #19 trong bảng → `wiki_candidate_capture_playbook.md` (Triggers table).
