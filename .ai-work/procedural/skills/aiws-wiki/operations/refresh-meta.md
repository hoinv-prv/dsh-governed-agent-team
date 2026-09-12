# aiws-wiki — operation: refresh-meta

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Re-project a Wiki Source Meta when the underlying source artifact may have
changed. Reports whether material change was detected (lookup keys, summary,
knowledge targets) so you can decide whether the wiki needs an update.

## Design notes (CR-022/024/025)
- **Preserve the RESOLVED `## Related Sources`** on refresh — never clobber human/AI-resolved edges (only re-emit the
  scaffold if it was never resolved). Legacy `## Profile Mapping` is dropped (mirrored frontmatter). Keep/resolve basis
  notes per the objective-stakes, intent-blind convention (build-meta SKILL / `Knowledge_Expansion_Link_Spec_MVP.md` §4.4).
- **Merge curated `## Lookup Keys` (union)** on refresh (CR-AIWS-2026-06-012 Fix 6) — the builder re-derives lookup keys mechanically, so refresh UNIONs curated+new (curated first, case-insensitive de-dup) and **never drops a curated key**; pass `--regenerate-lookup-keys` to re-derive from scratch instead.
- **After a refresh that changes `## Related Sources` → rebuild** `python .ai-work/tooling/build_relations.py`.
- Read a meta via `python .ai-work/tooling/wiki_meta.py --view <id>` (value-add reader), not the whole file.
- **Chunked SEC meta → re-chunk PARENT (CR-AIWS-2026-08-033 C3).** `refresh_wiki_source_meta.py` trên một
  SEC meta chỉ preserve `section_lines` verbatim — sau khi source đổi số dòng, span đã lệch. Muốn re-chunk đúng:
  chạy `build_wiki_source_meta.py --mode refresh` trên PARENT (hash carry-over cho section set). Từ CR-033 C1,
  mode refresh không `--out` tự resolve ĐÚNG namespace mà meta đang sống (`meta_roots()`); `--out` tường minh vẫn thắng.
- **Detector là repo-wide signal (CR-AIWS-2026-08-033 C2).** `detect_changed_wiki_sources.py` so với baseline
  snapshot toàn repo — sau một apply nhỏ nó có thể flag hàng trăm source không liên quan nếu baseline stale. Khoanh
  vùng theo footprint: `--paths <prefix[,prefix]>` (chỉ lọc REPORT + exit code; inventory và `--refresh-snapshot`
  vẫn full-repo nên scoped run không bao giờ cắt cụt baseline).
- **Sourceless refresh (node_kind=object):** an object meta has `artifact_locator: __OBJECT__` (no backing file) → `refresh_wiki_source_meta.py` source re-read does NOT apply (the tool no-ops with rc=0 on such metas — CR-AIWS-2026-07-038 T2). `detect_changed_wiki_sources.py` DOES flag hand-edits of object metas as `object_meta_changed` (meta-fingerprint — CR-032 T3/CR-038 T1); that signal routes HERE (hand refresh), never to the refresh tool. Refresh BY HAND: re-validate identity (`source_id` frozen), `## Summary`, and `## Related Sources`; set `updated_at` = `now_utc_iso()` (write time); then `build_relations.py`. (Source-backed refresh auto-stamps `updated_at` = source file mtime via re-projection — CR-AIWS-2026-06-024.)

## Tools
- `.ai-work/tooling/detect_changed_wiki_sources.py` (optional)
- `.ai-work/tooling/refresh_wiki_source_meta.py`
- `.ai-work/tooling/evaluate_wiki_source_impact.py` (optional)

### Example
```
# Detect first
python .ai-work/tooling/detect_changed_wiki_sources.py

# Refresh one meta (writes a draft by default)
python .ai-work/tooling/refresh_wiki_source_meta.py \
  --meta .ai-work/wiki_sources/meta/SRC-DESIGN-001.md \
  --profile .ai-work/wiki_sources/profiles/design_doc.yml

# Apply in-place (with backup)
python .ai-work/tooling/refresh_wiki_source_meta.py \
  --meta .ai-work/wiki_sources/meta/SRC-DESIGN-001.md \
  --profile .ai-work/wiki_sources/profiles/design_doc.yml \
  --apply

# Then rebuild the index
python .ai-work/tooling/build_wiki_source_index.py
```

### Flags
- `--apply` — overwrite in place (default writes a `.refresh.md` draft).
- `--regenerate-summary` — re-derive Summary instead of preserving the curated one (default preserves; Fix 1).
- **Lookup-keys modes (CR-AIWS-2026-07-038 T6, DP-038-2=C):** DEFAULT **preserves** curated `## Lookup Keys` byte-identical and only PRINTS newly derived keys as suggestions (union was monotonic junk-accumulation — R3-07). `--union-lookup-keys` — legacy union merge (curated + new, CR-012 Fix 6 + CR-044 re-filter). `--regenerate-lookup-keys` — re-derive from scratch (DROPS curated). `--preserve-lookup-keys` — explicit form of the default.
- `--review-decision <d>` — traceability of the review outcome; use `approved_to_apply` when applying after review (drives `maintenance_status`/`review_status`).
- `--impact-level <l>` / `--change-summary <s>` — recorded in the maintenance log.

## Flow
1. Detect candidates (`detect_changed_wiki_sources.py`).
2. For each candidate, refresh without `--apply` and diff the draft.
3. If material change: optionally `evaluate_wiki_source_impact.py` to see
   which wiki entries may need review; open a wiki candidate update task
   (`AIP_EXEC`) to drive the actual wiki changes — tooling must not
   rewrite wiki entries silently.
4. Apply refresh and rebuild the index.
5. **Object/relation re-check:** nếu refresh cho thấy artifact nay mô tả object MỚI, hoặc lộ quan hệ object↔object (domain) / object↔artifact (representation) MỚI/đổi chưa khai trên object node → append candidate `object_relation_capture` + đề xuất HUMAN cập nhật object node (`x:`/`represented_by` edges, khai một lần — ghi đủ MỌI edge mới, đừng dừng ở cạnh đầu). Suggest-only (rule #7/DP6/INV-8); domain edges đã resolved trên object node được PRESERVE (refresh không tự derive/ghi đè). **Khi re-check lộ object MỚI hoặc edge MỚI/đổi → PRESENT hai bảng (Detected Objects / Discovered Relations, chỉ các dòng mới/đổi) cho HUMAN confirm, đồng thời append candidate** (suggest-only; edge đã resolved giữ nguyên). Chi tiết: `capture_triggers/object_relation_capture.md`.

## Rules
- never let tooling rewrite official wiki entries
- material change is a signal, not an approval
- always go through a wiki candidate / review before applying wiki updates

---

## CR-S6: Promotion Gate (2026-05-25)

Source: AIP-EXEC-015 STEP-04, CR-S6.

**MANDATORY / HARD STOP** — trước MỌI meta refresh, classify change type theo **bản canonical duy nhất** của Promotion Gate: [`operations/refresh.md`](refresh.md) §"Promotion Gate (HARD STOP check first)" (5 promotion trigger + HARD STOP behavior + promotion-log schema + relations-impact-check). Promotion trigger → DỪNG, không apply, ghi log vào `.ai-work/wiki_sources/_promotion_log.jsonl`; Lightweight → tiếp tục flow draft → review → apply. *(Khối chi tiết — trigger list + gate behavior + log schema — dedup về refresh.md; nội dung gate không đổi một chữ. CR-AIWS-2026-07-029 C1.)*

## Traceability
- Step 5 (Object/relation re-check) ↔ governance rule #19. (Code moved out of action text per SKILL_AUTHORING_CONVENTIONS §1 / CR-032.)
