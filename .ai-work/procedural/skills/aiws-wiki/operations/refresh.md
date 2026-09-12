# aiws-wiki — operation: refresh

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Routing — Detect Case First

Before doing anything, detect which CASE applies from user context:

```
User says / provides                           → CASE
──────────────────────────────────────────────────────────────────────
File path + "changed/updated/stale"            → CASE 1  (meta refresh)
"source đã thay đổi" / "tài liệu gốc update"  → CASE 1
"cập nhật wiki meta" / "refresh meta"          → CASE 1
"format đã đổi" / "PMP stale" / "drift"        → CASE 2  (Mapping Pattern)
"cập nhật mapping pattern" / "refresh PMP"     → CASE 2
```

**Ambiguous input** (cannot determine CASE): Ask 1 clarifying question:
"Are you updating (a) a source artifact meta (file changed), or (b) a Mapping Pattern (format drift)?"

---

## CASE 1 — Meta Refresh (Source Artifact Changed)

Applies when a source artifact file has been updated and its wiki meta may be stale.

### Promotion Gate (HARD STOP check first)

Before applying any meta refresh, classify the change type:

**Lightweight change (proceed normally):**
- Fix typo in lookup key, summary, or caution
- Add new lookup key (without removing existing T1 key)
- Update `task_relevant_tags`
- Fix `representation_locator` or `updated_at`
- Minor Summary rewrite (scope unchanged)

**Promotion trigger (HARD STOP):**
Per `Controlled_Knowledge_Promotion_Spec_MVP.md §CR-D8 Addendum`:
1. Set `knowledge_class: source_of_truth`
2. Change `source_id` of a referenced meta
3. Split or merge meta records
4. Mark important artifact `deprecated`
5. Re-type/remove a `## Related Sources` edge that other metas depend on (run `wiki_relations.py --relations <source_id>` for IN-edges first)

```
IF change_type = Promotion trigger:
  → HARD STOP
  → Inform user: "This change requires Controlled Promotion (CR + wiki manager)"
  → Write log entry to .ai-work/wiki_sources/_promotion_log.jsonl
  → DO NOT apply refresh
  → Suggest: "Create a CR and submit to wiki manager for approval"

IF change_type = Lightweight:
  → Continue with detect → diff → apply flow below
```

#### Merging two metas that share one artifact (lint WARN `meta_duplicate_artifact`)

Trigger #3 above, seen from the side you'll actually meet it. Merge/delete = **Promotion trigger** → Wiki-Manager approve first.

1. **Giữ id mà package builder TÁI TẠO ĐƯỢC — kể cả khi id kia có nội dung tốt hơn.** Id không tái tạo được sẽ **mồ côi ở lần rebuild kế** bất kể nội dung; content mang đi được, id thì không. Kiểm tra: chạy builder trên artifact đó, xem nó sinh ra id nào.
2. **Carry nội dung curated sang id được giữ:** `title` · `## Summary` · **union** `## Lookup Keys` (curated trước) · `## Source-Specific Hints` bản đầy đủ hơn.
3. Xoá meta còn lại → rebuild index + relations → ghi `maintenance_log.jsonl` (`action: meta_merged`, kèm approver + rollback hint).
4. **Chunk children H6** (parent + `-SEC-*`) **cùng chia `artifact_locator` một cách hợp lệ** — không phải duplicate, **không merge**. Lint đã loại trừ sẵn.

*Tiền lệ: CR-AIWS-2026-07-050 (DP-050-1=A) — `index.aiws.jsonl` 188 → 187.*

### Relations impact check (CR-AIWS-2026-05-022)

IF the refresh touches the meta's `## Related Sources` (adds / removes / retypes an edge), FIRST run the reverse
query so you see WHO DEPENDS on this source before changing its edges (the named consumer of `relations.jsonl`):

```bash
python .ai-work/tooling/wiki_relations.py --relations <source_id>   # IN-edges = sources pointing AT this one (impact)
```

Review the IN-edges (impact set). After applying any `## Related Sources` change, REBUILD the projection:

```bash
python .ai-work/tooling/build_relations.py        # rebuild relations.jsonl from metas (never hand-edit it)
```

One-hop, opt-in; `relations.jsonl` is a projection. Spec: Knowledge_Relationship Spec v0.4 §6A.

**Promotion log entry schema:**
```json
{
  "log_id": "PROM-YYYYMMDD-NNN",
  "artifact_id": "SRC-<id>",
  "trigger_type": "<one of 5 triggers from CR-D8>",
  "change_description": "<what was attempted>",
  "operator": "AI|human",
  "status": "blocked_pending_cr",
  "detected_at": "YYYY-MM-DDTHH:MM:SS"
}
```

### Flow (Lightweight changes only)

```bash
# 1. Detect candidates
python .ai-work/tooling/detect_changed_wiki_sources.py
#    NOTE (CR-AIWS-2026-07-038): records with change_type `object_meta_changed` are OBJECT
#    nodes (hand-authored, no artifact) — hand-refresh per refresh-meta.md "Sourceless
#    refresh"; only artifact-backed records go through step 2 below.

# 2. Refresh without --apply (draft + diff)
python .ai-work/tooling/refresh_wiki_source_meta.py \
  --meta .ai-work/wiki_sources/meta/SRC-<id>.md \
  --profile .ai-work/wiki_sources/profiles/<profile>.yml

# 3. Review diff — if material change: evaluate impact
python .ai-work/tooling/evaluate_wiki_source_impact.py  # optional

# 4. Apply
python .ai-work/tooling/refresh_wiki_source_meta.py \
  --meta .ai-work/wiki_sources/meta/SRC-<id>.md \
  --profile .ai-work/wiki_sources/profiles/<profile>.yml \
  --apply

# 5. Rebuild index
python .ai-work/tooling/build_wiki_source_index.py
```

### Rules
- Never let tooling rewrite official wiki entries
- Material change is a signal, not an approval
- Always go through wiki candidate / review before applying wiki updates
- **#19 object_relation_capture (router pointer):** CASE 1 delegate `/aiws-wiki refresh-meta` đã bao gồm re-check object + quan hệ object↔object (domain x:) + representation (#19); router KHÔNG lặp lại — xem `capture_triggers/object_relation_capture.md`
- **Closing check:** trước khi báo done, xác nhận delegate đã emit candidate `object_relation_capture` (hoặc ghi rõ N/A cho artifact này). Delegate skip → KHÔNG coi router là done.

---

## CASE 2 — Mapping Pattern Update (Format Drift)

Applies when an existing Project Mapping Pattern (PMP) is stale because the artifact format changed.

Delegate entirely to the internal `/aiws-wiki refresh-pattern` skill:

**Trigger signals:**
- Format drift detected during meta build (sections changed, new slots appeared)
- `reuse_confidence` dropped due to observed mapping failures
- User says "format đã đổi", "PMP stale", "drift detected"

**Invocation:** Read `.ai-work/procedural/skills/aiws-wiki/operations/refresh-pattern.md` for full flow.

Key operations:
- Identify drift signals from new artifact samples
- Update `format_signature` and `canonical_slot_mapping` in PMP
- Adjust `reuse_confidence` based on observed failures

---

## Rules (all cases)

- Promotion Gate (CASE 1) is MANDATORY — always classify change type before applying
- Never apply Promotion-trigger changes without CR + wiki manager approval
- After any meta refresh: rebuild index (`build_wiki_source_index.py`)
- Do not promote candidates into Wiki / Knowledge Hub without HUMAN review

## Overview pages hook (CR-AIWS-2026-07-010)

Sau khi refresh làm index/relations rebuild: **regenerate overview pages** —
`py .ai-work/tooling/build_wiki_overview.py --all-systems` (hoặc `--system <id>`).
Bỏ qua → lint WARN `overview_fingerprint_stale`. KHÔNG sửa tay trang generated
(`overview_hand_edit` ERROR) — sửa metas/index nguồn rồi regenerate.
